"""Session 53284c80: harvest contract, executive-summary links, honest unresolved rows.

These tests pin what this session owns and what it must not change:

* the harvest workflow is non-publishing and branch-gated
* the committed dashboard already names where the picks are, including the
  separate unresolved/limitations surface
* an open row is either a sourced pick with a two-way line, or fully blank
  with a reason — never a priced row with no pick
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.diag_53284c80 import ledger, unresolved

ROOT = Path(__file__).resolve().parents[1]
HARVEST = (ROOT / ".github/workflows/harvest-53284c80.yml").read_text()
PAGES = (ROOT / ".github/workflows/pages.yml").read_text()
INDEX = (ROOT / "index.html").read_text()
UNRESOLVED_PAGE = (ROOT / "unresolved.html").read_text()
SNAPSHOT = json.loads((ROOT / "data/latest.json").read_text())


class HarvestWorkflowTests(unittest.TestCase):
    def test_the_harvest_never_deploys_pages_or_pushes_main(self):
        self.assertNotIn("actions/deploy-pages", HARVEST)
        self.assertNotIn("actions/upload-pages-artifact", HARVEST)
        self.assertNotIn("git push origin main", HARVEST)
        self.assertNotIn("git push origin HEAD:main", HARVEST)
        self.assertIn("'publishes_pages': False", HARVEST)
        self.assertIn("'pushes_main': False", HARVEST)

    def test_the_harvest_is_gated_to_this_branch_and_a_capture_marker(self):
        self.assertIn("branches: [arena/53284c80-maltaproj4]", HARVEST)
        self.assertIn("contains(github.event.head_commit.message, '[capture]')", HARVEST)
        self.assertIn("github.event_name == 'workflow_dispatch'", HARVEST)
        self.assertIn("python -m scripts.refresh --output runtime/latest.json", HARVEST)
        self.assertIn("python -m scripts.diag_53284c80", HARVEST)

    def test_pages_yml_still_uploads_the_artifact_before_the_legacy_root_step(self):
        upload = PAGES.index("actions/upload-pages-artifact@")
        fallback = PAGES.index("- name: Keep the legacy main:/ root fallback on the verified build")
        self.assertLess(upload, fallback)


class ExecutiveSummaryTests(unittest.TestCase):
    def test_the_home_page_names_where_the_picks_are(self):
        for needle in (
            'id="exec-summary"',
            'id="exec-quicknav"',
            'href="picks.html"',
            'href="unresolved.html"',
            'href="#unresolved-limits"',
            'href="matches.html"',
            "Updated picks",
        ):
            self.assertIn(needle, INDEX)

    def test_the_unresolved_page_states_the_limitation_surface(self):
        self.assertIn("unresolved", UNRESOLVED_PAGE.lower())
        self.assertTrue(
            "limitation" in UNRESOLVED_PAGE.lower() or "limitations" in UNRESOLVED_PAGE.lower()
        )


class SnapshotContractTests(unittest.TestCase):
    def test_every_open_row_is_either_a_full_pick_or_a_blank_unresolved_row(self):
        opened = [m for m in SNAPSHOT["matches"] if m.get("state") == "open"]
        self.assertGreater(len(opened), 0)
        for row in opened:
            if unresolved(row):
                self.assertIsNone(row.get("pick"), f"{row['id']} unresolved but has a pick")
                self.assertIsNone(row.get("probabilities"), f"{row['id']} unresolved but priced")
                self.assertIsNone(row.get("fair_odds"), f"{row['id']} unresolved but has fair odds")
                self.assertTrue(row.get("reason"), f"{row['id']} unresolved without a reason")
            else:
                self.assertIn(row["pick"], row["teams"])
                self.assertEqual(len(row["probabilities"]), 2)
                self.assertAlmostEqual(sum(row["probabilities"]), 1.0, places=9)
                self.assertTrue(str(row.get("source_url") or "").startswith("https://"))

    def test_the_reporter_matches_the_committed_snapshot_counts(self):
        report = ledger(SNAPSHOT)
        opened = [m for m in SNAPSHOT["matches"] if m.get("state") == "open"]
        self.assertEqual(report["rows"], len(SNAPSHOT["matches"]))
        self.assertEqual(report["open"], len(opened))
        self.assertEqual(report["picked"], sum(1 for m in opened if m.get("pick")))
        self.assertEqual(report["priced"], sum(1 for m in opened if m.get("probabilities")))
        self.assertEqual(report["unresolved"], sum(1 for m in opened if unresolved(m)))
        self.assertEqual(report["unresolved"], 0, "committed snapshot should have no unresolved open rows")


if __name__ == "__main__":
    unittest.main()
