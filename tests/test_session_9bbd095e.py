"""Regression tests for session 9bbd095e (2026-10-26).

Covers:
1. ``scripts/audit_5717f7d9.py`` root-staging gate support for valid
   ``model_vrs_mirror`` rows (such as 1081159 LFO 10 vs ex-6666 and 1081162
   ex-RUSTEC vs Spirit Academy) without importing ``scripts.*`` production code.
2. Fail-closed synthetic mutations on ``model_vrs_mirror`` rows (wrong provider,
   tampered Valve points, non-HLTV URL, stale observation >8h, stale ranking
   date >45d, incomplete ranking <100 teams, duplicate label without >=3 HLTV
   roster overlap, and missing prior unresolved ``Valve VRS model`` attempt).
3. Full line-by-line invariants on ``research/harvest-9bbd095e/refresh-snapshot.json``
   (81 rows, 19 open, 19/19 picks and probabilities, 0 Hotspawn crowd leakage,
   HLTV-first fallback order on non-exchange rows, and refusal of unverified
   Polymarket 6231429 ``Sökerorg`` opponent label on 1081159).
4. ``data/review-notes.json`` canonical ``indent=1`` formatting and presence of
   session 9bbd095e's three primary-sourced Flagged-for-Review disclosures, plus
   paired stylesheet and executive-summary / refresh-cadence invariants.
"""
from __future__ import annotations

import ast
import copy
import json
import unittest
from pathlib import Path

from scripts import audit_5717f7d9 as auditor

ROOT = Path(__file__).resolve().parents[1]
HARVEST_SNAPSHOT = ROOT / "research" / "harvest-9bbd095e" / "refresh-snapshot.json"
REVIEW_NOTES = ROOT / "data" / "review-notes.json"
SESSION_NOTE_IDS = (
    "session-9bbd095e-polymarket-sokerorg-lfo10-1081159-2026-10-26",
    "session-9bbd095e-bo3-nodwin13-slot-rotation-2026-10-26",
    "session-9bbd095e-audit-5717f7d9-mirror-gate-2026-10-26",
)


class Audit5717MirrorGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snap = json.loads(HARVEST_SNAPSHOT.read_text(encoding="utf-8"))
        cls.amap = auditor.load_alias_map()
        cls.standings = auditor.load_vendored_standings()

    def _audit(self, snap: dict):
        findings, ledger, expected = auditor.audit(snap, self.amap, self.standings)
        return findings, ledger, expected

    def test_auditor_remains_self_contained_with_zero_scripts_imports(self):
        tree = ast.parse((ROOT / "scripts" / "audit_5717f7d9.py").read_text(encoding="utf-8"))
        forbidden = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "scripts" or alias.name.startswith("scripts."):
                        forbidden.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if mod == "scripts" or mod.startswith("scripts."):
                    forbidden.append(mod)
        self.assertEqual(forbidden, [])

    def test_harvest_snapshot_with_two_mirror_rows_passes_with_zero_fails_or_flags(self):
        findings, ledger, expected = self._audit(self.snap)
        bad = [f for f in findings if f["severity"] in ("fail", "flag")]
        self.assertEqual(bad, [], f"Unexpected findings: {bad}")
        self.assertEqual(
            expected,
            {"open": 19, "with_pick": 19, "with_prob": 19, "unresolved": 0, "not_open_feed_rows": 62},
        )
        by_id = {r["id"]: r for r in ledger}
        for fid in ("1081159", "1081162"):
            self.assertEqual(by_id[fid]["method"], "model_vrs_mirror")
            self.assertIn(
                "Glicko + Valve calibration re-derived from retained points",
                by_id[fid]["checks"],
            )
            self.assertIn(
                "HLTV dated Valve ranking provenance, freshness and completeness verified",
                by_id[fid]["checks"],
            )

    def _mutated_mirror(self, mutator):
        snap = copy.deepcopy(self.snap)
        row = next(m for m in snap["matches"] if m["id"] == "1081159")
        mutator(snap, row, row["evidence"][0])
        findings, _, _ = self._audit(snap)
        return [f for f in findings if f["fixture"] == "1081159"]

    def test_mirror_row_rejects_wrong_provider(self):
        hits = self._mutated_mirror(lambda _s, _r, ev: ev.update(provider="Valve VRS model"))
        self.assertTrue(any(f["severity"] == "fail" and f["area"] == "vrs_evidence" for f in hits), hits)

    def test_official_vrs_row_rejects_mirror_provider(self):
        snap = copy.deepcopy(self.snap)
        row = next(m for m in snap["matches"] if m["id"] == "1079202")
        row["evidence"][0]["provider"] = "HLTV Valve ranking (Valve points)"
        findings, _, _ = self._audit(snap)
        hits = [f for f in findings if f["fixture"] == "1079202"]
        self.assertTrue(any(f["severity"] == "fail" and f["area"] == "vrs_evidence" for f in hits), hits)

    def test_mirror_row_rejects_tampered_points(self):
        hits = self._mutated_mirror(lambda _s, _r, ev: ev.update(points=[850, 968]))
        self.assertTrue(any(f["severity"] == "fail" and f["area"] == "vrs_rederive" for f in hits), hits)

    def test_mirror_row_rejects_non_hltv_valve_ranking_url(self):
        hits = self._mutated_mirror(
            lambda _s, _r, ev: ev.update(
                url="https://www.hltv.org/ranking/teams/2026/october/26",
                api_url="https://www.hltv.org/ranking/teams/2026/october/26",
            )
        )
        self.assertTrue(any(f["severity"] == "fail" and f["area"] == "vrs_mirror_source" for f in hits), hits)

    def test_mirror_row_rejects_stale_observation_over_8_hours(self):
        hits = self._mutated_mirror(lambda _s, _r, ev: ev.update(observed_at="2026-10-25T15:00:00Z"))
        self.assertTrue(any(f["severity"] == "fail" and f["area"] == "freshness" for f in hits), hits)

    def test_mirror_row_rejects_stale_ranking_as_of_over_45_days(self):
        hits = self._mutated_mirror(lambda _s, _r, ev: ev.update(ranking_as_of="2026-08-01"))
        self.assertTrue(any(f["severity"] == "fail" and f["area"] == "vrs_mirror_age" for f in hits), hits)

    def test_mirror_row_rejects_incomplete_ranking_table(self):
        hits = self._mutated_mirror(lambda _s, _r, ev: ev.update(ranking_teams_count=42))
        self.assertTrue(
            any(f["severity"] == "fail" and f["area"] == "vrs_mirror_completeness" for f in hits), hits
        )

    def test_mirror_row_rejects_duplicate_label_without_roster_overlap(self):
        def mutate(_s, _r, ev):
            ev["label_counts"] = [1, 2]
            ev["roster_checks"][1]["overlap"] = 2

        hits = self._mutated_mirror(mutate)
        self.assertTrue(
            any(f["severity"] == "fail" and f["area"] == "vrs_duplicate_label" for f in hits), hits
        )

    def test_mirror_row_rejects_missing_prior_official_vrs_attempt(self):
        def mutate(_s, row, _ev):
            row["attempts"] = [a for a in row["attempts"] if a.get("provider") != "Valve VRS model"]

        hits = self._mutated_mirror(mutate)
        self.assertTrue(
            any(f["severity"] == "fail" and f["area"] == "vrs_mirror_precedence" for f in hits), hits
        )


class HarvestCoverageAndFallbackInvariantsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snap = json.loads(HARVEST_SNAPSHOT.read_text(encoding="utf-8"))

    def test_every_non_exchange_open_row_attempts_hltv_before_books_and_models(self):
        opens = [m for m in self.snap["matches"] if m["state"] == "open"]
        self.assertEqual(len(opens), 19)
        non_exchange = [m for m in opens if m["method"] not in ("exchange", "exchange_wide")]
        self.assertEqual(len(non_exchange), 11)
        for m in non_exchange:
            providers = [a["provider"] for a in m["attempts"]]
            self.assertIn("HLTV", providers, m["id"])
            hltv_idx = providers.index("HLTV")
            for later in ("Pinnacle", "Thunderpick", "Valve VRS model", "HLTV Valve ranking (Valve points)"):
                if later in providers:
                    self.assertLess(hltv_idx, providers.index(later), f"{m['id']}: HLTV must precede {later}")

    def test_1081159_refuses_unverified_sokerorg_alias_and_preserves_non_inference(self):
        identities = json.loads((ROOT / "data" / "identities.json").read_text(encoding="utf-8"))
        flat_names = {
            auditor.plain_name(n)
            for item in identities.get("aliases", [])
            for n in item.get("names", [])
        }
        self.assertNotIn(auditor.plain_name("Sökerorg"), flat_names)
        row = next(m for m in self.snap["matches"] if m["id"] == "1081159")
        self.assertEqual(row["teams"], ["LFO 10", "ex-6666"])
        self.assertEqual(row["method"], "model_vrs_mirror")
        self.assertEqual(row["pick"], "ex-6666")
        pm_attempts = [a for a in row["attempts"] if a["provider"] == "Polymarket"]
        self.assertTrue(pm_attempts and all(a["status"] == "unresolved" for a in pm_attempts))


class ReviewNotesAndSiteStructureTest(unittest.TestCase):
    def test_review_notes_preserve_canonical_indent1_and_include_9bbd095e_findings(self):
        raw = REVIEW_NOTES.read_text(encoding="utf-8")
        notes = json.loads(raw)
        self.assertEqual(raw, json.dumps(notes, indent=1, ensure_ascii=False) + "\n")
        ids = [n["id"] for n in notes]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate review-note IDs found")
        by_id = {n["id"]: n for n in notes}
        for nid in SESSION_NOTE_IDS:
            self.assertIn(nid, by_id)
            self.assertTrue(by_id[nid].get("sources"))

    def test_paired_stylesheets_remain_byte_identical(self):
        root_css = (ROOT / "assets" / "style.css").read_bytes()
        site_css = (ROOT / "site" / "assets" / "style.css").read_bytes()
        self.assertEqual(root_css, site_css)

    def test_committed_snapshot_never_uses_hotspawn_for_probabilities(self):
        latest = json.loads((ROOT / "data" / "latest.json").read_text(encoding="utf-8"))
        for m in latest["matches"]:
            for ev in m.get("evidence") or []:
                for key in ("url", "api_url"):
                    val = (ev.get(key) or "").lower()
                    self.assertNotIn("hotspawn.com", val)
                    self.assertNotIn("cloudwaysapps.com", val)


if __name__ == "__main__":
    unittest.main()
