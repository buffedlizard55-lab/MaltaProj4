"""Session f533492a: test the refreshed candidate, never the expired board.

The scheduled publisher used to run the complete data-dependent unit suite
before its first source refresh.  Those tests read ``data/latest.json`` and the
committed root HTML, so a legitimate inventory change could permanently prevent
the refresh that would satisfy them.  Moving only the test step would not fix
that input mismatch: ``scripts.refresh`` writes ``runtime/latest.json``.

The publication sequence now refreshes and quarantines first, independently
audits/builds/validates the candidate, stages those hash-verified bytes into the
runner workspace, and only then runs every unit, independent-audit, root-link
and browser gate.  Staging is not publication.  The root commit/push, Pages
artifact upload and deployment all remain downstream of the complete gates.
Pull requests skip the network refresh as before and test the rebuilt committed
candidate through the same path.
"""
import copy
import json
from pathlib import Path
import unittest

from scripts.core import FIXTURES, HOTSPAWN, dt, iso
from scripts.inventory import LOBBY, discover, validate_inventory_receipt

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
REVIEW = json.loads((ROOT / "data/inventory-receipts.json").read_text(encoding="utf-8"))["receipts"][0]


def step(name):
    marker = "      - name: " + name + "\n"
    start = WORKFLOW.index(marker)
    end = WORKFLOW.find("\n      - ", start + len(marker))
    return WORKFLOW[start:end if end >= 0 else None]


class CandidateGateOrdering(unittest.TestCase):
    def test_refresh_precedes_the_data_dependent_unit_gate(self):
        refresh = WORKFLOW.index("      - name: Refresh official sources (trusted branches only)\n")
        unit = WORKFLOW.index("      - name: Unit and independent failure-mode tests\n")
        self.assertLess(refresh, unit)
        self.assertNotIn("python -m unittest discover -s tests", WORKFLOW[:refresh])

    def test_unit_gate_reads_staged_candidate_not_stale_runtime_baseline(self):
        build = WORKFLOW.index("      - name: Build and independently verify every row, calculation and internal link\n")
        stage = WORKFLOW.index("      - name: Stage the verified candidate for data-dependent regression tests\n")
        unit = WORKFLOW.index("      - name: Unit and independent failure-mode tests\n")
        browser = WORKFLOW.index("      - name: Phone, tablet, desktop, accessibility and exact-boundary expiry checks\n")
        self.assertLess(build, stage)
        self.assertLess(stage, unit)
        self.assertLess(unit, browser)
        staged = step("Stage the verified candidate for data-dependent regression tests")
        self.assertIn("python -m scripts.stage_legacy", staged)
        self.assertNotIn("publish_root_fallback", staged)
        self.assertNotIn("git commit", staged)
        self.assertNotIn("git push", staged)
        self.assertNotIn("continue-on-error", staged)

    def test_candidate_is_quarantined_audited_built_and_validated_before_staging(self):
        names = [
            "Refresh official sources (trusted branches only)",
            "Withhold any row the independent audit cannot reproduce",
            "Build and independently verify every row, calculation and internal link",
            "Stage the verified candidate for data-dependent regression tests",
        ]
        positions = [WORKFLOW.index("      - name: " + name + "\n") for name in names]
        self.assertEqual(positions, sorted(positions))
        build = step(names[2])
        self.assertLess(build.index("audit_snapshot.py runtime/latest.json"),
                        build.index("python -m scripts.build --data runtime/latest.json"))
        self.assertIn("python -m scripts.validate --data runtime/latest.json", build)
        self.assertIn("audit_snapshot.py public/data/latest.json", build)

    def test_no_original_test_or_independent_validator_was_removed(self):
        gate = step("Unit and independent failure-mode tests")
        for command in (
            "python -m unittest discover -s tests -v",
            "python -m unittest discover -s audits -p 'test_*.py' -v",
            "python verification-95b588c2/test_integrity.py",
            "python -m unittest discover -s verification-c6 -p 'test_*.py' -v",
            "python -m scripts.validate --data data/latest.json --site .",
        ):
            self.assertIn(command, gate)
        self.assertNotIn("continue-on-error", gate)

    def test_every_publication_effect_remains_downstream_of_all_gates(self):
        unit = WORKFLOW.index("      - name: Unit and independent failure-mode tests\n")
        browser = WORKFLOW.index("      - name: Phone, tablet, desktop, accessibility and exact-boundary expiry checks\n")
        root = WORKFLOW.index("      - name: Keep the legacy main:/ root fallback on the verified build\n")
        artifact = WORKFLOW.index("      - uses: actions/upload-pages-artifact@")
        self.assertLess(unit, browser)
        self.assertLess(browser, root)
        self.assertLess(root, artifact)
        self.assertIn("run: npm run test:browser",
                      step("Phone, tablet, desktop, accessibility and exact-boundary expiry checks"))
        self.assertIn("needs: verify-build", WORKFLOW[artifact:])

    def test_pull_requests_still_rebuild_and_test_without_network_refresh(self):
        refresh = step("Refresh official sources (trusted branches only)")
        self.assertIn("github.event_name != 'pull_request'", refresh)
        for name in (
            "Build and independently verify every row, calculation and internal link",
            "Stage the verified candidate for data-dependent regression tests",
            "Unit and independent failure-mode tests",
            "Phone, tablet, desktop, accessibility and exact-boundary expiry checks",
        ):
            block = step(name)
            self.assertIn("steps.gate.outputs.publish == 'true'", block)
            self.assertNotIn("github.event_name != 'pull_request'", block)


NOW = dt("2026-10-24T06:00:00Z")
BASE_ROW = {
    "id": "TEST_ONLY_BASE", "sport_alias": "cs2",
    "participants0_name": "Alpha", "participants1_name": "Beta",
    "scheduled_start_time": "2026-10-24T07:00:00Z",
    "lock_time": "2026-10-24T06:54:00Z", "status": "scheduled",
}
SUPPLEMENT_ROW = {
    "id": "1083045", "sport_alias": "cs2", "competition_id": "36412",
    "competition_name": "VOID Autumn Cup 2026", "tier": "c", "best_of": None,
    "participants0_id": "146827", "participants0_name": "Chinggis Warriors",
    "participants1_id": "59131", "participants1_name": "Rare Atom",
    "scheduled_start_time": "2026-10-24T03:00:00Z",
    "lock_time": "2026-10-24T02:54:00Z", "status": "ended",
    "participants0_picked_percent": 88, "participants1_picked_percent": 12,
    "participants0_score": 2, "participants1_score": 0,
}
OTHER_ROW = SUPPLEMENT_ROW | {"id": "1081861"}


class DiscoverySources:
    def __init__(self, primary, supplement=None):
        self.primary = list(primary)
        self.supplement = supplement
        self.log = []
        self.calls = []

    def get(self, name, url, as_json=True):
        self.calls.append(url)
        receipt = {"observed_at": iso(NOW), "retrieved_at": iso(NOW),
                   "sha256": "a" * 64, "url": url}
        if url == REVIEW["api_url"]:
            if isinstance(self.supplement, Exception):
                raise self.supplement
            return self.supplement, receipt
        rows = self.primary
        if as_json:
            return rows, receipt
        html = '<script id="ng-state">' + json.dumps({
            "test": {"u": FIXTURES.split("?")[0], "b": rows}
        }) + "</script>"
        return html, receipt


def run_discovery(review=None, primary=None, supplement=None, now=NOW):
    review = copy.deepcopy(REVIEW) if review is None else review
    primary = [BASE_ROW] if primary is None else primary
    supplement = [SUPPLEMENT_ROW, OTHER_ROW] if supplement is None else supplement
    src = DiscoverySources(primary, supplement)
    result = discover(src, now, receipts=[review])
    return result, src


class ReviewedInventorySupplementTests(unittest.TestCase):
    def test_exact_row_is_unioned_without_the_rest_of_its_competition(self):
        result, src = run_discovery()
        self.assertEqual({row["id"] for row in result["matches"]},
                         {"TEST_ONLY_BASE", "1083045"})
        self.assertEqual(result["coverage"], "partial")
        self.assertEqual(result["counts"],
                         {"api": 1, "page": 1, "lobby": 1, "retained": 2})
        row = next(row for row in result["matches"] if row["id"] == "1083045")
        self.assertEqual(row["state"], "not_open")
        self.assertIsNone(row["pick"])
        self.assertIsNone(row["probabilities"])
        self.assertIsNone(row["fair_odds"])
        self.assertEqual(row["source_url"], REVIEW["match_url"])
        self.assertEqual(row["feed_url"], REVIEW["api_url"])
        self.assertEqual(row["fixture_sources"][0]["url"], REVIEW["api_url"])
        self.assertEqual(row["inventory_receipt"]["listed_url"], HOTSPAWN)
        self.assertIn(REVIEW["api_url"], src.calls)
        self.assertEqual({issue["code"] for issue in result["flags"]},
                         {"reviewed_inventory_supplement", "coverage_difference"})

    def test_receipt_expires_at_the_pickem_week_boundary(self):
        result, src = run_discovery(now=dt(REVIEW["valid_until"]))
        self.assertEqual([row["id"] for row in result["matches"]], ["TEST_ONLY_BASE"])
        self.assertEqual(result["coverage"], "verified")
        self.assertNotIn(REVIEW["api_url"], src.calls)

    def test_receipt_is_skipped_when_all_primary_views_have_the_row(self):
        result, src = run_discovery(primary=[BASE_ROW, SUPPLEMENT_ROW])
        self.assertEqual(result["coverage"], "verified")
        self.assertEqual(result["counts"]["retained"], 2)
        self.assertNotIn(REVIEW["api_url"], src.calls)

    def test_changed_team_identity_is_not_added_and_coverage_stays_partial(self):
        review = copy.deepcopy(REVIEW)
        review["teams"] = ["Wrong Team", "Rare Atom"]
        result, _ = run_discovery(review=review)
        self.assertEqual([row["id"] for row in result["matches"]], ["TEST_ONLY_BASE"])
        self.assertEqual(result["coverage"], "partial")
        self.assertIn("inventory_supplement", {issue["code"] for issue in result["flags"]})

    def test_missing_registered_id_is_not_invented(self):
        result, _ = run_discovery(supplement=[OTHER_ROW])
        self.assertNotIn("1083045", {row["id"] for row in result["matches"]})
        self.assertEqual(result["coverage"], "partial")
        self.assertIn("inventory_supplement", {issue["code"] for issue in result["flags"]})

    def test_unofficial_or_probability_bearing_receipts_are_rejected(self):
        for mutation in (
            {"api_url": "https://example.com/api/v1/fixtures"},
            {"probabilities": [0.88, 0.12]},
            {"pick": "Chinggis Warriors"},
        ):
            review = copy.deepcopy(REVIEW) | mutation
            with self.subTest(mutation=mutation):
                with self.assertRaises(ValueError):
                    validate_inventory_receipt(review)
                result, src = run_discovery(review=review)
                self.assertEqual(result["coverage"], "partial")
                self.assertNotIn("1083045", {row["id"] for row in result["matches"]})
                self.assertFalse(any("example.com" in call for call in src.calls))

    def test_committed_receipt_is_official_bounded_and_inventory_only(self):
        self.assertEqual(validate_inventory_receipt(REVIEW), "1083045")
        self.assertIn("competition_id=36412", REVIEW["api_url"])
        self.assertNotIn("status=scheduled", REVIEW["api_url"])
        self.assertTrue(REVIEW["match_url"].endswith("-1083045"))
        self.assertEqual(REVIEW["listed_url"], HOTSPAWN)
        self.assertEqual(REVIEW["valid_until"], "2026-10-26T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
