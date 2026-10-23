"""Regression tests for session e141a921's read-only acceptance audit."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts.probe_e141a921 import audit, changed_fixtures, inspect_row


def fixture_row(**changes):
    row = {
        "id": "42",
        "teams": ["Alpha", "Beta"],
        "competition": "Example CS2 event",
        "start": "2026-10-24T12:00:00Z",
        "lock": "2026-10-24T11:54:00Z",
        "state": "open",
        "source_url": "https://play.hotspawn.com/cs2-pickems/42",
        "feed_url": "https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1",
        "fixture_sources": [{"url": "https://play.hotspawn.com/lobby",
                             "observed_at": "2026-10-23T10:00:00Z"}],
        "pick": "Alpha",
        "method": "exchange",
        "probabilities": [0.6, 0.4],
        "fair_odds": [1 / 0.6, 2.5],
        "reason": "Polymarket two-way line, de-vigged.",
        "evidence": [{"provider": "Polymarket",
                      "url": "https://polymarket.com/event/alpha-beta",
                      "api_url": "https://gamma-api.polymarket.com/markets/42"}],
        "attempts": [],
    }
    row.update(changes)
    return row


def snapshot(rows):
    return {
        "generated_at": "2026-10-23T10:00:00Z",
        "fixtures_observed_at": "2026-10-23T09:59:00Z",
        "coverage": "verified",
        "coverage_counts": {"api": len(rows), "page": len(rows),
                            "lobby": len(rows), "retained": len(rows)},
        "matches": rows,
        "source_checks": [],
        "issues": [],
        "fixture_conflicts": [],
        "inventory_changes": {},
    }


class RowAuditTests(unittest.TestCase):
    def test_valid_external_line_passes(self):
        self.assertEqual(inspect_row(fixture_row()), [])

    def test_hotspawn_only_cannot_support_a_price(self):
        row = fixture_row(evidence=[{"provider": "Hotspawn",
                                     "url": "https://play.hotspawn.com/lobby"}])
        self.assertIn("priced row has no external evidence link", inspect_row(row))

    def test_arithmetic_and_pick_orientation_are_checked(self):
        row = fixture_row(probabilities=[0.4, 0.6], fair_odds=[2.5, 1 / 0.6])
        self.assertIn("pick does not follow the larger probability", inspect_row(row))
        row = fixture_row(probabilities=[0.7, 0.4])
        self.assertIn("probabilities do not sum to one", inspect_row(row))

    def test_research_gap_keeps_blank_numbers_and_limitation(self):
        row = fixture_row(pick="Beta", method="research_rank", probabilities=None,
                          fair_odds=None, evidence=[],
                          reason="HLTV ranking order only; not a market probability.")
        self.assertEqual(inspect_row(row), [])
        row["reason"] = ""
        self.assertIn("open row without a percentage lacks its limitation", inspect_row(row))

    def test_non_open_rows_are_not_forced_to_have_picks(self):
        row = fixture_row(state="not_open", pick=None, method=None,
                          probabilities=None, fair_odds=None, evidence=[], reason="Past lock.")
        self.assertEqual(inspect_row(row), [])


class SnapshotAuditTests(unittest.TestCase):
    def test_gap_accounting_does_not_invent_a_resolution(self):
        priced = fixture_row()
        research = fixture_row(id="43", pick="Beta", method="research_rank_single",
                               probabilities=None, fair_odds=None, evidence=[],
                               reason="Only Beta has an HLTV rank; no probability published.")
        unresolved = fixture_row(id="44", pick=None, method=None, probabilities=None,
                                 fair_odds=None, evidence=[],
                                 reason="No exact external line or ranking edge was verified.")
        report = audit(snapshot([priced, research, unresolved]), snapshot([]), "abc")
        self.assertEqual(report["counts"]["open"], 3)
        self.assertEqual(report["counts"]["open_with_pick"], 2)
        self.assertEqual(report["counts"]["open_with_probability"], 1)
        self.assertEqual(report["counts"]["open_without_pick"], ["44"])
        self.assertEqual(report["counts"]["open_without_probability"], ["43", "44"])
        self.assertEqual([g["id"] for g in report["fallback_research_required"]], ["43", "44"])
        self.assertEqual(report["status"], "pass")

    def test_partial_inventory_is_not_called_verified(self):
        snap = snapshot([fixture_row()])
        snap["coverage_counts"]["lobby"] = 0
        report = audit(snap, snapshot([]), "abc")
        self.assertEqual(report["status"], "fail")
        self.assertFalse(report["three_view_parity"])

    def test_source_time_changes_are_explicit(self):
        before = snapshot([fixture_row()])
        after = copy.deepcopy(before)
        after["matches"][0]["start"] = "2026-10-24T13:00:00Z"
        diff = changed_fixtures(after, before)
        self.assertEqual(diff["changed_start_lock_or_state"][0]["id"], "42")
        self.assertEqual(diff["changed_start_lock_or_state"][0]["changes"]["start"]["fresh"],
                         "2026-10-24T13:00:00Z")


class PublishedStructureTests(unittest.TestCase):
    def test_executive_summary_links_to_picks_and_limitations(self):
        soup = BeautifulSoup(Path("index.html").read_text(), "html.parser")
        self.assertIsNotNone(soup.find(id="picks-at-a-glance"))
        self.assertIsNotNone(soup.find(id="unresolved-picks"))
        self.assertIsNotNone(soup.find(id="unresolved-summary"))
        hrefs = {tag.get("href") for tag in soup.find_all("a", href=True)}
        self.assertIn("picks.html", hrefs)
        self.assertIn("unresolved.html", hrefs)
        self.assertIn("matches.html", hrefs)
        self.assertIn("review.html", hrefs)
        self.assertIn("#picks-at-a-glance", hrefs)
        self.assertIn("#unresolved-picks", hrefs)

    def test_every_committed_fixture_has_an_official_source_and_no_hotspawn_price(self):
        data = json.loads(Path("data/latest.json").read_text())
        for row in data["matches"]:
            with self.subTest(fixture=row["id"]):
                self.assertEqual(inspect_row(row), [])


if __name__ == "__main__":
    unittest.main()
