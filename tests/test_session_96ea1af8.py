"""Session 96ea1af8: the executive summary names the open fixtures with no pick.

The request for this session was a pick for every Hotspawn CS2 match, with a
separate unresolved-and-limitations section inside the executive summary. The
section already existed; what it lacked was the *names* of the rows that still
have nothing, so a phone reader had to open another page to learn which match
was missing. ``#pick-limitations`` now states them, built only from the
snapshot rows, and states the opposite when the set is empty.
"""
import copy
import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import build

ROOT = Path(__file__).resolve().parents[1]


class LimitationsPanelNamesTheGaps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "data/latest.json").read_text())

    def _panel(self, data):
        soup = BeautifulSoup(build.overview(data), "html.parser")
        panel = soup.select_one("#pick-limitations")
        self.assertIsNotNone(panel)
        return panel

    def test_every_unresolved_open_row_is_named_with_a_working_link(self):
        data = copy.deepcopy(self.data)
        # Deterministic regardless of today's frozen snapshot: clear the pick and
        # the numbers on every open row, so the panel must name all of them.
        unresolved = []
        for m in data["matches"]:
            if m["state"] != "open":
                continue
            m["pick"] = None
            m["probabilities"] = None
            m["fair_odds"] = None
            m["method"] = None
            unresolved.append(m)
        self.assertTrue(unresolved, "frozen snapshot has no open rows to render")
        panel = self._panel(data)
        now = panel.select_one(".lim-now")
        self.assertIsNotNone(now)
        text = now.get_text(" ", strip=True)
        self.assertIn("Open now with no pick at all", text)
        hrefs = [a.get("href") or "" for a in now.select("a")]
        for m in unresolved:
            self.assertTrue(any("match-" + m["id"] in h for h in hrefs),
                            f"unresolved row {m['id']} is not linked from #pick-limitations")
            self.assertIn(m["teams"][0], text)
            self.assertIn(m["teams"][1], text)
        self.assertEqual(text.count("Open now with no pick at all"), 1)

    def test_states_the_opposite_when_nothing_is_unresolved(self):
        data = copy.deepcopy(self.data)
        # Give every open row a pick so the empty-state sentence must render.
        for m in data["matches"]:
            if m["state"] == "open":
                m.setdefault("pick", m["teams"][0])
                if not m.get("pick"):
                    m["pick"] = m["teams"][0]
        panel = self._panel(data)
        now = panel.select_one(".lim-now")
        self.assertIn("Every open match currently carries a pick", now.get_text(" ", strip=True))
        self.assertEqual(now.select("a"), [])

    def test_panel_stays_inside_the_executive_summary_section(self):
        soup = BeautifulSoup(build.overview(self.data), "html.parser")
        section = soup.select_one("#unresolved-summary")
        self.assertIsNotNone(section)
        self.assertIsNotNone(section.select_one("#pick-limitations .lim-now"))


class PublishedLimitationNote(unittest.TestCase):
    """The Flagged-for-Review note for the one unpicked fixture must be sourced."""

    def test_note_exists_and_cites_the_sources_that_were_actually_read(self):
        notes = json.loads((ROOT / "data/review-notes.json").read_text())
        note = next((n for n in notes if n["id"] == "1081597-no-pick-2026-10-21"), None)
        self.assertIsNotNone(note, "the unpicked-fixture review note is missing")
        urls = " ".join(s["url"] for s in note["sources"])
        for required in (
            "hotspawn.com/matches/benched-gods-vs-titanflow",
            "hltv.org/team/13599/benched-gods",
            "standings_global_2026_10_05.md",
            "egamersworld.com/counterstrike/match/",
            "bo3.gg/matches/benched-gods-vs-titanflow",
        ):
            self.assertIn(required, urls)
        # It must not claim a probability exists for a row that has none.
        self.assertIn("no percentage", note["finding"])


if __name__ == "__main__":
    unittest.main()
