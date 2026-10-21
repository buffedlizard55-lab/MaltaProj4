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


class CybershokeIdentity(unittest.TestCase):
    """The one gap in the 2026-10-21 fresh snapshot: fixture 1082762."""

    def test_alias_folds_three_labels_but_not_prospects(self):
        from scripts.core import norm

        self.assertEqual(norm("ex-CYBERSHOKE"), norm("CYBERSHOKE Esports"))
        self.assertEqual(norm("CYBERSHOKE"), norm("CYBERSHOKE Esports"))
        self.assertNotEqual(norm("CYBERSHOKE Prospects"), norm("CYBERSHOKE"))

    def test_alias_entry_is_sourced_and_bounded(self):
        register = json.loads((ROOT / "data/identities.json").read_text())["aliases"]
        entries = [a for a in register if a["canonical"] == "CYBERSHOKE"]
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual({"CYBERSHOKE", "CYBERSHOKE Esports", "ex-CYBERSHOKE"}, set(entry["names"]))
        self.assertTrue(entry["source"].startswith("https://www.hltv.org/matches/2399839/"))
        self.assertTrue(entry["additional_source"].startswith("https://gamma-api.polymarket.com/markets/5971981"))
        basis = entry["basis"].lower()
        for needle in ("exact opponent", "utc start", "roster", "prospects"):
            self.assertIn(needle, basis)

    def test_vrs_roster_rule_selects_standing_61(self):
        from scripts import vrs

        standings, _meta = vrs.vendored(__import__("datetime").datetime.now(__import__("datetime").timezone.utc))
        entry, note = vrs.identify(
            "ex-CYBERSHOKE", standings, ["bl1x1", "Mokuj1n", "nota", "yiksrezo", "shoke"]
        )
        self.assertIsNotNone(entry, note)
        self.assertEqual(entry["standing"], 61)
        self.assertEqual(entry["roster_overlap"], 3)


if __name__ == "__main__":
    unittest.main()
