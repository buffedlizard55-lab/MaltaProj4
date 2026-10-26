"""Session b964dffd — every open match picked, and the mirror tier auditable.

Everything here pins the *archived* harvest capture
(``research/harvest-b964dffd/snapshot.json``, non-publishing runner run
40251666216, snapshot 2026-10-26T01:00:10Z), never the live
``data/latest.json`` — a rotating board must not break these tests and
freeze publication the way pinned live values did on 2026-10-23/24
(see tests/test_session_e334b970.py).

Groups:

* ``HarvestCaptureCoverage`` — the capture that answered this session's
  brief: 81 = 81 = 81 surface parity, the 8 fixtures Hotspawn added after
  the 00:10Z board, and 19/19 open rows with a pick, both probabilities,
  a non-Hotspawn source and a recorded HLTV-first-then-books ladder trail.
* ``HarvestCaptureArithmetic`` — every published percentage re-derived here
  from the retained evidence (exchange normalisation, bookmaker de-vig,
  Valve's published Glicko fit + calibration slope) with no pipeline code.
* ``MirrorTierAuditorRegression`` — the defect this session fixed in
  ``scripts/audit_5717f7d9``: mirror rows used to fail that independent
  auditor ("Model row has no VRS evidence") so any board containing one
  could not pass the publisher's staged-root gate. The auditor must now
  pass genuine mirror evidence and still fail swapped, undated or
  numerically tampered mirror evidence.
"""
import copy
import json
import math
import unittest
from pathlib import Path

from scripts import audit_5717f7d9 as auditor

ROOT = Path(__file__).resolve().parents[1]
HARVEST = ROOT / "research" / "harvest-b964dffd"
SNAPSHOT = json.loads((HARVEST / "snapshot.json").read_text(encoding="utf-8"))
RUN = json.loads((HARVEST / "run.json").read_text(encoding="utf-8"))
OPENS = [m for m in SNAPSHOT["matches"] if m["state"] == "open"]
BY_ID = {m["id"]: m for m in SNAPSHOT["matches"]}
NEW_IDS = {"1079201", "1079202", "1079203", "1081159",
           "1081160", "1081162", "1081163", "1081164"}

# Valve's published fit: Glicko expected score, RD 75, then calibration
# slope 0.7986 applied symmetrically around 50% (model/fit.js, modelfit.png).
_Q = math.log(10) / 400
_G = 1 / math.sqrt(1 + 3 * _Q * _Q * 75.0 * 75.0 / math.pi ** 2)


def vrs_probability(points_a, points_b):
    expected = 1 / (1 + 10 ** (-_G * (points_a - points_b) / 400))
    return 0.5 + 0.7986 * (expected - 0.5)


class HarvestCaptureCoverage(unittest.TestCase):
    def test_receipt_names_the_nonpublishing_runner(self):
        self.assertEqual(RUN["workflow_run_id"], "40251666216")
        self.assertFalse(RUN["publishes_pages"])
        self.assertEqual(SNAPSHOT["generated_at"], "2026-10-26T01:00:10.246310Z")

    def test_all_three_hotspawn_surfaces_agree(self):
        self.assertEqual(SNAPSHOT["coverage"], "verified")
        self.assertEqual(SNAPSHOT["coverage_counts"],
                         {"api": 81, "page": 81, "lobby": 81, "retained": 81})
        self.assertEqual(len(SNAPSHOT["matches"]), 81)

    def test_the_eight_added_fixtures_are_the_inventory_delta(self):
        changes = SNAPSHOT["inventory_changes"]
        self.assertEqual(set(changes["added_ids"]), NEW_IDS)
        self.assertEqual(changes["removed_ids"], [])

    def test_every_open_row_has_pick_probabilities_and_external_source(self):
        self.assertEqual(len(OPENS), 19)
        for m in OPENS:
            self.assertTrue(m["pick"], m["id"])
            self.assertIsNotNone(m["probabilities"], m["id"])
            self.assertAlmostEqual(sum(m["probabilities"]), 1.0, places=12, msg=m["id"])
            self.assertTrue(m["evidence"], m["id"])
            url = m["evidence"][0].get("url") or ""
            self.assertTrue(url.startswith("https://"), (m["id"], url))
            self.assertNotIn("hotspawn.com", url, m["id"])
            self.assertNotIn("cloudwaysapps.com", url, m["id"])
            self.assertTrue(m["expires_at"], m["id"])

    def test_no_open_row_is_unresolved_or_research_only_on_this_capture(self):
        for m in OPENS:
            self.assertNotIn(m["method"], (None, "research_rank",
                                           "research_rank_single",
                                           "research_vrs_single",
                                           "research_form"), m["id"])

    def test_new_low_tier_rows_record_the_ladder_they_actually_climbed(self):
        # The brief: featured markets first, then HLTV, then esportsbooks,
        # then originate. Every non-exchange newcomer must show the attempts.
        for fid in sorted(NEW_IDS):
            m = BY_ID[fid]
            providers = [a["provider"] for a in m["attempts"]]
            if m["method"] == "exchange":
                self.assertEqual(providers[0], "Polymarket", fid)
                continue
            for expected in ("HLTV", "Pinnacle", "Thunderpick (via BO3.gg API)"):
                self.assertIn(expected, providers, (fid, providers))
        # The two rows no monthly-file or market route could resolve went to
        # HLTV's dated mirror of Valve's ranking, and say so.
        for fid in ("1081159", "1081162"):
            m = BY_ID[fid]
            self.assertEqual(m["method"], "model_vrs_mirror", fid)
            self.assertTrue(any("dated Valve ranking" in f for f in m["flags"]), fid)


class HarvestCaptureArithmetic(unittest.TestCase):
    def test_every_percentage_rederives_from_retained_evidence(self):
        for m in OPENS:
            e = m["evidence"][0]
            if m["method"] == "exchange":
                raw = e["raw"]
                prices = [float(x) for x in json.loads(raw["outcomePrices"])]
                normalised = sorted(p / sum(prices) for p in prices)
                calc = sorted(m["probabilities"])
                # 1082861's retained spread is 0.55 - 0.30, which is
                # 0.25000000000000006 in binary floating point.
                self.assertLessEqual(e["spread"], 0.25 + 1e-9, m["id"])
                self.assertGreaterEqual(e["liquidity"], 100.0, m["id"])
            elif m["method"] == "bookmaker_fallback":
                odds = e["raw"]["odds"]
                inv = [1 / o for o in odds]
                calc = [x / sum(inv) for x in inv]
                normalised = calc
                calc = m["probabilities"]
                for got, want in zip(calc, normalised):
                    self.assertAlmostEqual(got, want, places=12, msg=m["id"])
                continue
            elif m["method"] in ("model_vrs", "model_vrs_mirror"):
                pts = e["points"]
                normalised = [vrs_probability(pts[0], pts[1]),
                              vrs_probability(pts[1], pts[0])]
                calc = m["probabilities"]
                for got, want in zip(calc, normalised):
                    self.assertAlmostEqual(got, want, places=12, msg=m["id"])
                continue
            else:  # pragma: no cover - a new tier must extend this test
                self.fail("unhandled method %r on %s" % (m["method"], m["id"]))
            for got, want in zip(calc, normalised):
                self.assertAlmostEqual(got, want, places=9, msg=m["id"])
            favourite = m["teams"][0] if m["probabilities"][0] > m["probabilities"][1] \
                else m["teams"][1]
            self.assertEqual(m["pick"], favourite, m["id"])

    def test_mirror_points_match_the_standings_they_claim(self):
        expected = {"1081159": ([803, 968], [157, 118]),
                    "1081162": ([1059, 1038], [94, 101])}
        for fid, (points, standings) in expected.items():
            e = BY_ID[fid]["evidence"][0]
            self.assertEqual(e["provider"], "HLTV Valve ranking (Valve points)", fid)
            self.assertEqual(e["points"], points, fid)
            self.assertEqual(e["standings"], standings, fid)
            self.assertEqual(e["ranking_as_of"], "2026-10-26", fid)
            self.assertTrue(e["ranking_page_sha256"], fid)


class MirrorTierAuditorRegression(unittest.TestCase):
    """audit_5717f7d9 must pass genuine mirror rows and still fail bad ones."""

    @classmethod
    def setUpClass(cls):
        cls.amap = auditor.load_alias_map()
        cls.standings = auditor.load_vendored_standings()

    def findings_for(self, snapshot, fid):
        findings, _ledger, _expected = auditor.audit(snapshot, self.amap, self.standings)
        return [f for f in findings
                if f["severity"] in ("fail", "flag") and f["fixture"] == fid]

    def tampered(self, fid, mutate):
        snapshot = copy.deepcopy(SNAPSHOT)
        row = next(m for m in snapshot["matches"] if m["id"] == fid)
        mutate(row)
        return snapshot

    def test_genuine_mirror_rows_pass_the_auditor(self):
        for fid in ("1081159", "1081162"):
            self.assertEqual(self.findings_for(SNAPSHOT, fid), [], fid)

    def test_provider_swapped_mirror_evidence_fails(self):
        def swap(row):
            row["evidence"][0]["provider"] = "Valve VRS model"
        bad = self.findings_for(self.tampered("1081159", swap), "1081159")
        self.assertTrue(any(f["area"] == "vrs_evidence" for f in bad), bad)

    def test_undated_mirror_evidence_fails(self):
        def strip(row):
            row["evidence"][0].pop("ranking_as_of", None)
            row["evidence"][0].pop("ranking_page_sha256", None)
        bad = self.findings_for(self.tampered("1081162", strip), "1081162")
        self.assertTrue(any(f["area"] == "vrs_mirror_source" for f in bad), bad)

    def test_tampered_mirror_points_fail_the_rederivation(self):
        def bump(row):
            row["evidence"][0]["points"] = [row["evidence"][0]["points"][0] + 250,
                                            row["evidence"][0]["points"][1]]
        bad = self.findings_for(self.tampered("1081159", bump), "1081159")
        self.assertTrue(any(f["area"] in ("vrs_rederive", "vrs_raw") for f in bad), bad)

    def test_monthly_file_rows_still_require_the_valve_provider(self):
        row_id = next(m["id"] for m in OPENS if m["method"] == "model_vrs")

        def swap(row):
            row["evidence"][0]["provider"] = "HLTV Valve ranking (Valve points)"
        bad = self.findings_for(self.tampered(row_id, swap), row_id)
        self.assertTrue(any(f["area"] == "vrs_evidence" for f in bad), bad)


if __name__ == "__main__":
    unittest.main()
