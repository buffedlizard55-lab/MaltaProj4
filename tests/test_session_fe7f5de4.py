"""Session fe7f5de4: current coverage, honest gaps, and phone-first pick access.

These tests intentionally use source-derived counts rather than pinning a number
of matches. Hotspawn can add or close fixtures on every refresh; the contract is
that every open row remains visible and every blank remains explained.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from scripts import build

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data/latest.json").read_text())


class CurrentCoverageContract(unittest.TestCase):
    def setUp(self):
        self.data = copy.deepcopy(DATA)
        self.open = [m for m in self.data["matches"] if m.get("state") == "open"]

    def test_three_hotspawn_views_describe_the_same_retained_inventory(self):
        counts = self.data.get("coverage_counts") or {}
        self.assertEqual(self.data.get("coverage"), "verified")
        self.assertEqual(counts.get("retained"), len(self.data["matches"]))
        self.assertEqual(counts.get("api"), counts.get("page"))
        self.assertEqual(counts.get("api"), counts.get("lobby"))
        self.assertEqual(counts.get("api"), counts.get("retained"))
        ids = [str(m["id"]) for m in self.data["matches"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {str(m["id"]) for m in self.data["fixture_evidence"]})

    def test_every_open_match_has_a_pick_or_an_explicit_unverified_blank(self):
        for match in self.open:
            with self.subTest(fixture=match["id"]):
                self.assertTrue(match.get("source_url", "").startswith("https://"))
                if match.get("pick"):
                    self.assertIn(match["pick"], match["teams"])
                else:
                    self.assertIsNone(match.get("probabilities"))
                    self.assertIsNone(match.get("fair_odds"))
                    self.assertIsNone(match.get("method"))
                    self.assertTrue(match.get("reason"), "unresolved limitation missing")
                    self.assertTrue(match.get("attempts"), "unresolved source attempts missing")

    def test_only_current_no_percentage_rows_drive_the_limitations_section(self):
        expected = {m["id"] for m in self.open if m.get("probabilities") is None}
        soup = BeautifulSoup(build.overview(self.data), "html.parser")
        section = soup.select_one("#unresolved-picks")
        self.assertIsNotNone(section)
        self.assertIsNone(section.find_parent("details"))
        linked = {a["href"].split("#match-", 1)[1] for a in section.select('a[href*="#match-"]')}
        self.assertEqual(linked, expected)
        for match in self.open:
            if match["id"] in expected:
                self.assertIn(match["teams"][0], section.get_text(" ", strip=True))
                self.assertIn(match["teams"][1], section.get_text(" ", strip=True))

    def test_each_no_percentage_row_has_hltv_and_external_line_attempts(self):
        for match in self.open:
            if match.get("probabilities") is not None:
                continue
            with self.subTest(fixture=match["id"]):
                attempts = match.get("attempts") or []
                providers = {a.get("provider") for a in attempts}
                self.assertIn("HLTV", providers)
                self.assertIn("Polymarket", providers)
                self.assertIn("Pinnacle", providers)
                self.assertTrue(providers & {
                    "Thunderpick", "GG.BET", "Book listing gap recheck",
                    "Book listing re-observation", "Book research",
                })
                self.assertTrue(match.get("reason"))
                for attempt in attempts:
                    if attempt.get("url"):
                        self.assertEqual(urlparse(attempt["url"]).scheme, "https")
                # A rejected 0.50/0.50 market may remain in the audit ledger,
                # but can never become the published probability.
                self.assertIsNone(match.get("probabilities"))
                self.assertIsNone(match.get("fair_odds"))

    def test_every_priced_open_row_has_two_reproducible_probabilities(self):
        for match in self.open:
            probabilities = match.get("probabilities")
            if probabilities is None:
                continue
            with self.subTest(fixture=match["id"]):
                self.assertEqual(len(probabilities), 2)
                self.assertAlmostEqual(sum(probabilities), 1.0, places=12)
                self.assertTrue(all(0 < p < 1 for p in probabilities))
                self.assertNotEqual(probabilities, [0.5, 0.5])
                self.assertIn(match.get("method"), {
                    "exchange", "exchange_wide", "bookmaker", "bookmaker_fallback",
                    "model_vrs", "model_vrs_mirror",
                })
                self.assertTrue(match.get("evidence"))
                self.assertEqual(len(match.get("fair_odds") or []), 2)
                for probability, fair in zip(probabilities, match["fair_odds"]):
                    self.assertAlmostEqual(fair, 1 / probability, places=12)


class VerifiedArtifactPublicationContract(unittest.TestCase):
    def test_only_root_push_race_is_non_blocking(self):
        workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        step = workflow.split(
            "      - name: Keep the legacy main:/ root fallback on the verified build",
            1,
        )[1]
        # Session 572c65b7 inserted an explanation step directly after the
        # fallback step, so the block ends at whichever header comes next.
        for header in ("      - name: Explain a legacy-root failure without withholding the verified board",
                       "      - name: Record the exact artifact expected at the public site"):
            if header in step:
                step = step.split(header, 1)[0]

        # Session 572c65b7 (2026-10-24): the fallback is now explicitly
        # non-blocking, because between 09:03Z and 16:07Z a failure here skipped
        # the Pages artifact upload and the deploy as well, and the verified
        # fresh board was never published. The gates below are unchanged and
        # still run before the push loop; the step still exits 1 when they fail,
        # so the run itself stays red and the next step annotates the failing
        # gate. What changed is the blast radius, not the standard.
        self.assertIn("continue-on-error: true", step)
        self.assertIn('[ "$rc" = "3" ]', step, 'a gate failure must still fail the step')
        self.assertNotIn('|| true\n          [ "$rc" = "3" ]', step)
        for required in (
            "python -m scripts.publish_root_fallback",
            "python -m scripts.validate --data data/latest.json --site .",
            "python -m unittest discover -s tests",
            "git commit -m",
        ):
            self.assertIn(required, step)
            self.assertLess(step.index(required), step.index("for attempt in 1 2 3"))
        self.assertIn("if git pull --rebase --autostash origin main && git push origin HEAD:main", step)
        self.assertNotIn('echo "::error::Could not push the staged root fallback', step)
        self.assertIn('echo "::warning::Could not push the staged root fallback after three attempts', step)
        self.assertIn("deploying the verified Actions artifact", step)
        self.assertTrue(step.rstrip().endswith("exit 0"))


class PhoneFirstMarkupContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.soup = BeautifulSoup(build.overview(copy.deepcopy(DATA)), "html.parser")
        cls.css = (ROOT / "site/assets/style.css").read_text()

    def test_actual_pick_list_is_unfolded_and_duplicate_guides_are_folded(self):
        glance = self.soup.select_one("#picks-at-a-glance")
        self.assertIsNotNone(glance)
        self.assertIsNone(glance.find_parent("details"))
        self.assertIsNotNone(self.soup.select_one("#freshness-strip a.fresh-cta[href='picks.html']"))
        guide = self.soup.select_one("#exec-banner").find_parent("details")
        self.assertIsNotNone(guide)
        self.assertIsNone(guide.get("open"))
        self.assertIs(self.soup.select_one("#coverage-now").find_parent("details"), guide)
        self.assertIs(self.soup.select_one("#start-here").find_parent("details"), guide)
        # Exactly one duplicated guide disclosure, not a stack of introductory
        # boxes between the freshness CTA and the real picks.
        self.assertEqual(len(glance.find_all_previous("details", class_="briefing-more")), 1)

    def test_all_open_matches_have_desktop_and_phone_cards(self):
        glance = self.soup.select_one("#picks-at-a-glance")
        expected = [m for m in DATA["matches"] if m.get("state") == "open"]
        self.assertEqual(len(glance.select("a.glance-row")), len(expected))
        self.assertEqual(len(glance.select("a.glance-card-mobile")), len(expected))
        for match in expected:
            links = glance.select(f'a[href="evidence.html#match-{match["id"]}"]')
            self.assertGreaterEqual(len(links), 2, match["id"])

    def test_compact_phone_rules_do_not_remove_accessible_targets(self):
        self.assertIn(".fresh-strip .fresh-schedule{display:none}", self.css)
        self.assertIn(".glance-actions{display:none}", self.css)
        self.assertIn(".fresh-strip .fresh-links a{min-height:44px}", self.css)
        self.assertIn(".mobile-tabs a", self.css)
        self.assertIn("@media(max-width:650px)", self.css)


if __name__ == "__main__":
    unittest.main()
