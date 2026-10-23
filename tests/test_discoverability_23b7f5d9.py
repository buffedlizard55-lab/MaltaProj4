"""Discoverability labels describe coverage state, not whether a pick exists."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from scripts.build import build, filters, overview

ROOT = Path(__file__).resolve().parents[1]


class DiscoverabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads((ROOT / "data/latest.json").read_text())
        cls.no_percentage = sum(
            row["state"] == "open" and row.get("probabilities") is None
            for row in cls.snapshot["matches"]
        )
        cls.temp = tempfile.TemporaryDirectory()
        observed = datetime.fromisoformat(cls.snapshot["generated_at"].replace("Z", "+00:00"))
        build(copy.deepcopy(cls.snapshot), cls.temp.name, now=observed)
        cls.output = Path(cls.temp.name)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def soup(self, route: str) -> BeautifulSoup:
        return BeautifulSoup((self.output / route).read_text(), "html.parser")

    @staticmethod
    def label(link) -> str:
        return "".join(link.stripped_strings)

    def test_global_navigation_names_the_research_queue_truthfully(self):
        nav = self.soup("index.html").select_one('nav[aria-label="Main navigation"]')
        labels = ["".join(a.stripped_strings) for a in nav.select("a")]
        self.assertIn("Unresolved", labels)
        self.assertNotIn("Needs pick", labels)

    def test_no_percentage_filter_is_used_for_rows_that_still_have_a_research_pick(self):
        expected = self.no_percentage
        for route in ("index.html", "picks.html", "unresolved.html"):
            soup = self.soup(route)
            link = soup.select_one('a[href="unresolved.html?status=needs"]')
            self.assertIsNotNone(link, route)
            self.assertEqual(self.label(link), f"No percentage ({expected})", route)
            option = soup.select_one('select#status option[value="needs"]')
            if option:
                self.assertEqual(option.get_text(strip=True), "No percentage", route)

    def test_count_is_derived_from_the_current_snapshot_not_a_fixed_five(self):
        row = next(
            (
                item for item in self.snapshot["matches"]
                if item["state"] == "open"
                and item.get("probabilities") is None
                and item.get("pick")
            ),
            None,
        )
        if row is None:
            row = copy.deepcopy(next(item for item in self.snapshot["matches"] if item["state"] == "open" and item.get("pick")))
            row["probabilities"] = None
            row["fair_odds"] = None
            row["method"] = "research_rank_single"
        one_row = copy.deepcopy(self.snapshot)
        one_row["matches"] = [copy.deepcopy(row)]
        html = overview(one_row)
        soup = BeautifulSoup(html, "html.parser")
        link = soup.select_one('a[href="unresolved.html?status=needs"]')
        self.assertEqual(self.label(link), "No percentage (1)")
        self.assertEqual(soup.select_one('[data-count="missing"]').get_text(strip=True), "1")
        self.assertIn("0 with no supported pick yet", soup.get_text(" ", strip=True))

    def test_phone_help_uses_dynamic_gap_count_and_measured_refresh_cadence(self):
        soup = self.soup("index.html")
        text = soup.select_one("#phone-tips").get_text(" ", strip=True)
        self.assertIn("Unresolved", text)
        self.assertIn("No percentage", text)
        self.assertIn("data-count", str(soup.select_one('#phone-tips [data-count="missing"]')))
        self.assertIn("15-minute schedule", text)
        self.assertIn("90 minutes old", text)
        self.assertNotIn("why 5 rows", text)
        self.assertNotIn("Every 4–8 hours", text)

    def test_filter_label_maps_to_the_existing_no_probability_state(self):
        html = filters(self.snapshot["matches"])
        soup = BeautifulSoup(html, "html.parser")
        option = soup.select_one('select#status option[value="needs"]')
        self.assertIsNotNone(option)
        self.assertEqual(option.get_text(strip=True), "No percentage")


if __name__ == "__main__":
    unittest.main()
