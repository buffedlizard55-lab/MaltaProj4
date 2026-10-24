"""Regression checks for the 24 October refresh and phone integration."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts.build import overview


ROOT = Path(__file__).resolve().parents[1]


class StylesheetBoundaryTests(unittest.TestCase):
    def test_canonical_css_has_balanced_blocks_and_matches_published_copy(self):
        canonical = (ROOT / "site" / "assets" / "style.css").read_text()
        self.assertEqual(canonical.count("{"), canonical.count("}"),
                         "an unclosed media block disables later phone rules")
        self.assertEqual(canonical, (ROOT / "assets" / "style.css").read_text())

    def test_summary_keeps_direct_pick_and_limit_links(self):
        data = json.loads((ROOT / "data" / "latest.json").read_text())
        soup = BeautifulSoup(overview(data), "html.parser")
        self.assertIsNotNone(soup.select_one("#freshness-strip a[href='picks.html']"))
        self.assertIsNotNone(soup.select_one("#picks-at-a-glance"))
        limitations = soup.select_one("#unresolved-limits")
        self.assertIsNotNone(limitations)
        hrefs = {a.get("href") for a in limitations.select("a[href]")}
        self.assertIn("unresolved.html", hrefs)
        self.assertIn("review.html", hrefs)


class IndependentMirrorReplayTests(unittest.TestCase):
    def test_hltv_valve_points_use_the_same_independent_model_formula(self):
        from tests.test_session_0cc1138a import V

        probabilities, kind = V.evidence_probabilities({
            "provider": "HLTV Valve ranking (Valve points)",
            "points": [1030, 819],
        })
        expected = V.calibrate(V.glicko_expect(1030, 819))
        self.assertEqual(kind, "valve_vrs_hltv_mirror")
        self.assertAlmostEqual(probabilities[0], expected, places=12)
        self.assertAlmostEqual(sum(probabilities), 1.0, places=12)


class DatedLobbyLifecycleTests(unittest.TestCase):
    """The repaired old-lobby test must still reject a premature disappearance."""

    @classmethod
    def setUpClass(cls):
        import tests.test_session_0cc1138a as lobby_test
        cls.lobby_test = lobby_test
        # Use the immutable dated lobby for both synthetic clock cases. Using
        # whatever board happens to be current would reintroduce unrelated
        # later removals into this focused regression.
        cls.original = json.loads(
            (ROOT / "research" / "harvest-9b97d585" / "snapshot.json").read_text()
        )

    def setUp(self):
        self.lobby_test.SNAPSHOT = copy.deepcopy(self.original)

    def tearDown(self):
        self.lobby_test.SNAPSHOT = self.original

    def remove_before_lock(self):
        doc = self.lobby_test.SNAPSHOT
        doc["built_at"] = "2026-10-23T09:30:00Z"
        doc["fixtures_observed_at"] = "2026-10-23T09:30:00Z"
        doc["matches"] = [row for row in doc["matches"] if row["id"] != "1081148"]
        doc["inventory_changes"] = {"removed_ids": []}
        return doc

    def test_missing_open_fixture_is_still_rejected_before_its_captured_lock(self):
        self.remove_before_lock()
        with self.assertRaisesRegex(AssertionError, "1081148"):
            self.lobby_test.LiveHotspawnCoverage(
                "test_snapshot_covers_the_observed_lobby_fixtures"
            ).test_snapshot_covers_the_observed_lobby_fixtures()

    def test_missing_locked_fixture_is_accepted_after_its_captured_lock(self):
        doc = self.lobby_test.SNAPSHOT
        doc["built_at"] = "2026-10-23T11:47:19Z"
        doc["fixtures_observed_at"] = "2026-10-23T11:43:39Z"
        doc["matches"] = [row for row in doc["matches"]
                          if row["id"] not in {"1081148", "1079655"}]
        doc["inventory_changes"] = {"removed_ids": []}
        case = self.lobby_test.LiveHotspawnCoverage(
            "test_snapshot_covers_the_observed_lobby_fixtures"
        )
        case.test_snapshot_covers_the_observed_lobby_fixtures()


if __name__ == "__main__":
    unittest.main()
