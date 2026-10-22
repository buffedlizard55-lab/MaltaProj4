"""Regression and receipt checks for the 22 October full-board audit."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup

from scripts import build
from scripts.probe_77667efa import audit
from scripts.refresh import cache_bust

ROOT = Path(__file__).resolve().parents[1]
HARVEST = ROOT / "research/harvest-77667efa"
SNAPSHOT = json.loads((HARVEST / "snapshot.json").read_text())
TARGETED = json.loads((HARVEST / "targeted/probe-report.json").read_text())
COVERAGE = json.loads((HARVEST / "coverage-audit.json").read_text())


class CacheBustRegressionTests(unittest.TestCase):
    """A future Hotspawn lobby URL may legitimately gain query arguments."""

    def test_url_without_query_gets_one_labelled_argument(self):
        self.assertEqual(
            cache_bust("https://play.hotspawn.com/lobby", "T1"),
            "https://play.hotspawn.com/lobby?_cb=T1",
        )

    def test_existing_query_is_preserved_byte_for_byte(self):
        url = "https://play.hotspawn.com/lobby?tenantId=1&encoded=a%2Fb&flag&blank="
        busted = cache_bust(url, "T 2")
        self.assertEqual(
            busted,
            url + "&_cb=T+2",
            "cache busting must not crash, decode, reorder, or double-encode canonical arguments",
        )

    def test_duplicate_arguments_and_fragment_survive(self):
        url = "https://play.hotspawn.com/lobby?a=1&a=2#open"
        busted = cache_bust(url, "T3")
        parts = urlsplit(busted)
        self.assertEqual(parts.query, "a=1&a=2&_cb=T3")
        self.assertEqual(parts.fragment, "open")
        self.assertEqual(parse_qs(parts.query)["a"], ["1", "2"])


class FreshHarvestCoverageTests(unittest.TestCase):
    def setUp(self):
        self.open_rows = [row for row in SNAPSHOT["matches"] if row["state"] == "open"]
        self.gaps = [row for row in self.open_rows if row.get("probabilities") is None]

    def test_inventory_is_verified_and_materially_newer_than_the_bootstrap(self):
        bootstrap = json.loads((ROOT / "data/latest.json").read_text())
        self.assertEqual(SNAPSHOT["coverage"], "verified")
        self.assertGreater(SNAPSHOT["generated_at"], bootstrap["generated_at"])
        self.assertEqual(len(SNAPSHOT["matches"]), 97)
        self.assertEqual(len(self.open_rows), 35)

    def test_every_open_fixture_has_a_pick(self):
        self.assertEqual([row["id"] for row in self.open_rows if not row.get("pick")], [])
        for row in self.open_rows:
            self.assertIn(row["pick"], row["teams"], row["id"])

    def test_every_open_fixture_links_the_official_inventory_row(self):
        for row in self.open_rows:
            source = urlsplit(row["source_url"])
            self.assertEqual(source.scheme, "https", row["id"])
            self.assertIn(source.netloc, {"www.hotspawn.com", "play.hotspawn.com"}, row["id"])

    def test_every_probability_replays_from_non_hotspawn_evidence(self):
        priced = [row for row in self.open_rows if row.get("probabilities") is not None]
        self.assertEqual(len(priced), 28)
        for row in priced:
            self.assertEqual(len(row["probabilities"]), 2, row["id"])
            self.assertAlmostEqual(sum(row["probabilities"]), 1.0, places=9, msg=row["id"])
            self.assertTrue(row.get("evidence"), row["id"])
            evidence = row["evidence"][0]
            source = evidence.get("api_url") or evidence.get("url")
            self.assertTrue(source.startswith("https://"), row["id"])
            self.assertNotIn("hotspawn", source.lower(), row["id"])

    def test_every_unpriced_row_was_researched_hltv_then_pinnacle(self):
        self.assertEqual(len(self.gaps), 7)
        self.assertEqual({row["id"] for row in self.gaps}, {
            "1081869", "1081597", "1082769", "1079654", "1081149", "1081150", "1082860"
        })
        for row in self.gaps:
            providers = [attempt.get("provider") for attempt in row.get("attempts", [])]
            self.assertIn("HLTV", providers, row["id"])
            self.assertIn("Pinnacle", providers, row["id"])
            self.assertLess(providers.index("HLTV"), providers.index("Pinnacle"), row["id"])
            self.assertTrue(row.get("reason"), row["id"])
            self.assertTrue(str(row.get("method")).startswith("research_"), row["id"])

    def test_exact_target_set_was_probed_and_no_book_hit_was_silently_ignored(self):
        probed = {str(row["id"]) for row in TARGETED["gap_rows"]}
        self.assertEqual(probed, {row["id"] for row in self.gaps})
        self.assertEqual(TARGETED["matches_found"], [])
        self.assertEqual(TARGETED["markets"]["pinnacle"]["gap_hits"], [])
        # Do not assert that the convenience Polymarket tag query proves there
        # are no CS2 markets. The production refresh uses the official sports
        # registry and did accept seven exact lines in this same snapshot.
        self.assertEqual(
            sum(row.get("method") == "exchange" for row in self.open_rows), 7
        )

    def test_joined_audit_and_independent_row_audit_are_green(self):
        self.assertEqual(COVERAGE["verdict"], "pass")
        self.assertEqual(COVERAGE["violations"], [])
        self.assertEqual(COVERAGE["counts"], {
            "rows_total": 97,
            "open": 35,
            "with_pick": 35,
            "with_probability": 28,
            "research_only": 7,
            "without_pick": 0,
        })
        row_audit = (HARVEST / "row-audit.md").read_text()
        self.assertIn("Rows checked: **97**", row_audit)
        self.assertNotIn("Inconsistent with stored evidence", row_audit)


class ProbeFailureModeTests(unittest.TestCase):
    def test_missing_pick_fails_closed(self):
        snapshot = copy.deepcopy(SNAPSHOT)
        target = next(row for row in snapshot["matches"] if row["state"] == "open")
        target["pick"] = None
        result = audit(snapshot, TARGETED)
        self.assertEqual(result["verdict"], "fail")
        self.assertTrue(any(
            item.get("fixture_id") == target["id"] and "pick is missing" in item.get("problem", "")
            for item in result["violations"]
        ))

    def test_hotspawn_cannot_be_probability_evidence(self):
        snapshot = copy.deepcopy(SNAPSHOT)
        target = next(row for row in snapshot["matches"] if row["state"] == "open" and row.get("probabilities"))
        target["evidence"][0]["api_url"] = target["source_url"]
        result = audit(snapshot, TARGETED)
        self.assertTrue(any(
            item.get("fixture_id") == target["id"] and "never be a probability source" in item.get("problem", "")
            for item in result["violations"]
        ))

    def test_missing_targeted_gap_fails_closed(self):
        targeted = copy.deepcopy(TARGETED)
        removed = targeted["gap_rows"].pop()
        result = audit(SNAPSHOT, targeted)
        self.assertEqual(result["verdict"], "fail")
        self.assertTrue(any(
            item.get("fixture_id") == str(removed["id"]) and "targeted research" in item.get("problem", "")
            for item in result["violations"]
        ))


class PhoneExecutiveSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.soup = BeautifulSoup(build.overview(copy.deepcopy(SNAPSHOT)), "html.parser")
        cls.open_rows = [row for row in SNAPSHOT["matches"] if row["state"] == "open"]

    def test_first_summary_strip_has_direct_internal_pick_links(self):
        strip = self.soup.select_one("#freshness-strip")
        self.assertIsNotNone(strip)
        hrefs = {a.get("href") for a in strip.select("a")}
        self.assertTrue({"picks.html", "#picks-at-a-glance", "unresolved.html"} <= hrefs)
        text = strip.get_text(" ", strip=True)
        self.assertIn("35 open CS2 match(es)", text)
        self.assertIn("35 with a pick", text)
        self.assertIn("28 with a win probability", text)
        self.assertIn("0 unresolved", text)

    def test_every_open_match_has_both_desktop_and_phone_glance_cards(self):
        section = self.soup.select_one("#picks-at-a-glance")
        self.assertEqual(len(section.select("a.glance-row")), len(self.open_rows))
        self.assertEqual(len(section.select("a.glance-card-mobile")), len(self.open_rows))
        hrefs = [a.get("href") for a in section.select("a.glance-card-mobile")]
        for row in self.open_rows:
            self.assertIn("evidence.html#match-" + row["id"], hrefs)

    def test_phone_cards_never_show_a_fake_fifty_fifty(self):
        section = self.soup.select_one("#picks-at-a-glance")
        cards = section.select("a.glance-card-mobile")
        research_cards = [card for card in cards if card.get("data-glance-priced") == "0"]
        self.assertEqual(len(research_cards), 7)
        for card in research_cards:
            self.assertIn("No percentage", card.get_text(" ", strip=True))
        self.assertNotIn("50/50", section.get_text(" ", strip=True))

    def test_exec_summary_has_separate_unresolved_and_limitations_section(self):
        section = self.soup.select_one("#unresolved-summary")
        self.assertIsNotNone(section)
        self.assertIsNotNone(section.select_one("#pick-limitations"))
        text = section.get_text(" ", strip=True)
        for row in self.open_rows:
            if row.get("probabilities") is None:
                self.assertIn(row["teams"][0], text)
                self.assertIn(row["teams"][1], text)
        self.assertIn("Every open match currently carries a pick", text)


if __name__ == "__main__":
    unittest.main()
