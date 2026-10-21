"""Session afce4281: executive summary must route a phone user to every pick."""
import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import build

ROOT = Path(__file__).resolve().parents[1]


class ExecutiveSummaryRouting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = json.loads((ROOT / "data/latest.json").read_text())
        cls.data = data
        cls.opens = [m for m in data["matches"] if m["state"] == "open"]
        # overview() is the executive-summary renderer used by build().
        cls.soup = BeautifulSoup(build.overview(data), "html.parser")

    def test_glance_covers_every_open_match(self):
        glance = self.soup.select_one("#picks-at-a-glance")
        self.assertIsNotNone(glance)
        hrefs = [a.get("href", "") for a in glance.select("a.glance-row")]
        for m in self.opens:
            self.assertTrue(
                any(f"match-{m['id']}" in h for h in hrefs),
                f"open match {m['id']} missing from picks-at-a-glance",
            )

    def test_glance_has_large_tap_targets_to_updated_picks_and_unresolved(self):
        actions = self.soup.select_one("#picks-at-a-glance .glance-actions")
        self.assertIsNotNone(actions)
        hrefs = [a.get("href") for a in actions.select("a")]
        self.assertIn("picks.html", hrefs)
        self.assertIn("#unresolved-summary", hrefs)

    def test_unresolved_section_and_limitations_inside_summary(self):
        section = self.soup.select_one("#unresolved-summary")
        self.assertIsNotNone(section)
        self.assertIsNotNone(section.select_one("#pick-limitations"))

    def test_every_open_match_has_a_pick_or_is_named_unresolved(self):
        # Either a pick is published, or the row must carry an explicit reason
        # (research/unresolved rows are never silently blank).
        for m in self.opens:
            if not m.get("pick"):
                self.assertTrue(m.get("reason"), f"{m['id']} has neither pick nor reason")


if __name__ == "__main__":
    unittest.main()
