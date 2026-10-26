"""Session 77046e56 — the independent auditor must treat both Valve-point
providers as model evidence, and must still fail closed on tampering.

Measured defect this pins (2026-10-26): ``scripts.audit_5717f7d9`` selected
evidence with ``provider == "Valve VRS model"`` only. A row priced from HLTV's
*dated view* of Valve's ranking carries ``provider == "HLTV Valve ranking
(Valve points)"``, so the auditor reported ``Model row has no VRS evidence`` as a
hard failure for fixtures 1081159 and 1081162. That failure is part of the
publish workflow's own unit gate: the verified 81-row build was refused at
``step 17`` ("Keep the legacy main:/ root fallback on the verified build"), the
legacy ``main:/`` root kept the older 73-row snapshot, and the public board kept
serving 11 open matches after Hotspawn listed 19. The auditor was wrong, not the
rows: both providers retain the same Valve points and the same published
formula, and the arithmetic re-derives exactly.

The tests also prove the audit does not simply stop checking mirrors: a missing
ranking date/hash, a fixture-identity mismatch and a tampered probability must
each still produce a failure.
"""
import copy
import json
import unittest
from pathlib import Path

from scripts import audit_5717f7d9 as audit

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / "data" / "latest.json").read_text(encoding="utf-8"))
AMAP = audit.load_alias_map()
STANDINGS = audit.load_vendored_standings()


def mirror_row(snapshot):
    return next((m for m in snapshot["matches"]
                 if m.get("method") == "model_vrs_mirror"
                 and m.get("evidence", [{}])[0].get("provider") == audit.MIRROR_PROVIDER), None)


def hard_findings(findings):
    return [f for f in findings if f["severity"] in ("fail", "flag")]


class MirrorRowsAreAudited(unittest.TestCase):
    def setUp(self):
        self.row = mirror_row(SNAPSHOT)
        if self.row is None:
            self.skipTest("committed snapshot carries no HLTV-mirror row to audit")

    def audit_with(self, mutate):
        snapshot = copy.deepcopy(SNAPSHOT)
        row = next(m for m in snapshot["matches"] if m["id"] == self.row["id"])
        mutate(row)
        findings, _ledger, _expected = audit.audit(snapshot, AMAP, STANDINGS)
        return [f for f in findings if f["fixture"] == self.row["id"]]

    def test_the_committed_mirror_row_carries_no_hard_finding(self):
        findings = self.audit_with(lambda row: None)
        self.assertEqual(hard_findings(findings), [], json.dumps(hard_findings(findings), indent=2))

    def test_missing_ranking_provenance_is_a_failure(self):
        for key in ("ranking_as_of", "ranking_page_sha256"):
            with self.subTest(key=key):
                def drop(row, key=key):
                    row["evidence"][0].pop(key, None)
                areas = {f["area"] for f in hard_findings(self.audit_with(drop))}
                self.assertIn("vrs_mirror_source", areas)

    def test_fixture_identity_mismatch_is_a_failure(self):
        def swap(row):
            row["evidence"][0]["fixture_teams"] = ["Somebody Else", "Another Club"]
        areas = {f["area"] for f in hard_findings(self.audit_with(swap))}
        self.assertIn("vrs_mirror_identity", areas)

    def test_tampered_probability_is_caught_by_the_formula(self):
        def tamper(row):
            p = row["probabilities"]
            row["probabilities"] = [min(0.999, p[0] + 0.05), max(0.001, p[1] - 0.05)]
            row["pick"] = row["teams"][0] if row["probabilities"][0] > 0.5 else row["teams"][1]
        areas = {f["area"] for f in hard_findings(self.audit_with(tamper))}
        self.assertIn("vrs_rederive", areas)

    def test_tampered_points_are_caught_against_the_retained_expectation(self):
        def tamper(row):
            e = row["evidence"][0]
            e["points"] = [e["points"][0] + 60, e["points"][1]]
        areas = {f["area"] for f in hard_findings(self.audit_with(tamper))}
        self.assertTrue({"vrs_rederive", "vrs_raw"} & areas, areas)

    def test_the_vendored_official_file_is_not_used_to_judge_a_mirror_row(self):
        # The mirror exists precisely because the monthly file does not resolve
        # these clubs; a false "not found in the vendored file" failure would
        # push a correct row back to unresolved.
        areas = {f["area"] for f in hard_findings(self.audit_with(lambda row: None))}
        self.assertNotIn("vrs_vendored", areas)


if __name__ == "__main__":
    unittest.main()
