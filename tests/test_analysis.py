"""Regression tests for dated TWC market research that remains outside the feed."""
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from scripts.build import ROOT, build


GAMMA_AURORA = 'https://gamma-api.polymarket.com/markets/5733288'
GAMMA_LEGACY = 'https://gamma-api.polymarket.com/markets/5763247'
THUNDERPICK_AURORA = 'https://thunderpick.io/esports/cs2-betting/thunderpick-world-championship-2026/11024/aurora-vs-9z-team/2830808'
THUNDERPICK_LEGACY = 'https://thunderpick.io/esports/cs2-betting/thunderpick-world-championship-2026/11024/bb-team-vs-legacy/2832532'


def no_vig_from_american(odds):
    implied = [
        100 / (price + 100) if price > 0 else -price / (-price + 100)
        for price in odds
    ]
    overround = sum(implied) - 1
    total = sum(implied)
    return [value / total for value in implied], overround


class DayThreeMarketSupplementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analysis = json.loads((ROOT / 'data/analysis.json').read_text())
        cls.notes = json.loads((ROOT / 'data/review-notes.json').read_text())

    def fixture(self, teams):
        return next(item for item in self.analysis['day_three']['fixtures'] if item['teams'] == teams)

    def test_exchange_receipts_meet_the_recorded_strict_quality_gates(self):
        for teams in (['Aurora', '9z'], ['BETBOOM', 'Legacy']):
            with self.subTest(teams=teams):
                market = self.fixture(teams)['market']
                receipt = market['receipt']
                observed = datetime.fromisoformat(receipt['observed_at'].replace('Z', '+00:00'))
                updated = datetime.fromisoformat(receipt['updated_at'].replace('Z', '+00:00'))
                self.assertTrue(receipt['active'])
                self.assertFalse(receipt['closed'])
                self.assertTrue(receipt['accepting_orders'])
                self.assertAlmostEqual(sum(receipt['outcome_prices']), 1.0, places=9)
                self.assertEqual(round((receipt['best_ask'] - receipt['best_bid']) * 100), receipt['spread_points'])
                self.assertLessEqual(receipt['spread_points'], 25)
                self.assertGreaterEqual(receipt['liquidity_usd'], 100)
                self.assertGreaterEqual(observed, updated)
                self.assertLess(observed - updated, timedelta(hours=8))
                self.assertEqual(market['url'], GAMMA_AURORA if teams[0] == 'Aurora' else GAMMA_LEGACY)

    def test_bookmaker_no_vig_receipts_recompute_and_remain_timestamp_limited(self):
        for teams in (['Aurora', '9z'], ['BETBOOM', 'Legacy']):
            with self.subTest(teams=teams):
                market = self.fixture(teams)['market']
                quote = market['bookmaker_receipts'][0]
                probabilities, overround = no_vig_from_american(quote['american_odds'])
                for actual, expected in zip(probabilities, quote['no_vig_probabilities']):
                    self.assertAlmostEqual(actual, expected, places=12)
                self.assertAlmostEqual(overround, quote['overround'], places=12)
                self.assertEqual(quote['provider'], 'Thunderpick')
                self.assertIsNone(quote['quote_updated_at'])
                self.assertEqual(quote['url'], THUNDERPICK_AURORA if teams[0] == 'Aurora' else THUNDERPICK_LEGACY)

    def test_legacy_rejected_quote_is_retained_but_not_used_as_the_current_midpoint(self):
        fixture = self.fixture(['BETBOOM', 'Legacy'])
        self.assertIsNone(fixture['hotspawn_fixture'])
        self.assertEqual(fixture['start_utc'], '2026-10-16T17:00:00Z')
        receipt = fixture['market']['receipt']
        prior = receipt['prior_rejected_snapshot']
        self.assertEqual(prior['outcome_prices'], [0.5, 0.5])
        self.assertEqual(prior['spread_points'], 94)
        self.assertEqual(prior['liquidity_usd'], 260)
        self.assertIsNone(prior['volume_usd'])
        self.assertEqual(receipt['outcome_prices'], [0.635, 0.365])
        self.assertEqual(receipt['spread_points'], 9)
        self.assertGreater(receipt['liquidity_usd'], 100)
        self.assertIn('not in the Hotspawn feed', fixture['market']['market_read'])
        self.assertIn('no automated board pick is created', fixture['market']['market_read'])

    def test_analysis_renders_market_only_scope_and_each_source_link(self):
        snapshot = json.loads((ROOT / 'data/latest.json').read_text())
        now = datetime(2026, 10, 15, 23, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            build(snapshot, directory, now=now)
            root = Path(directory)
            page = BeautifulSoup((root / 'analysis.html').read_text(), 'html.parser')
            rows = page.select('#day-three table tbody tr')
            self.assertEqual(len(rows), 2)
            legacy_row = next(row for row in rows if 'BETBOOM' in row.get_text(' ', strip=True))
            cells = legacy_row.select('td')
            self.assertIn('17:00:00Z', cells[1].get_text(' ', strip=True))
            self.assertIn('Not listed by the Hotspawn feed', cells[2].get_text(' ', strip=True))
            self.assertIn('Market-only read:', cells[3].get_text(' ', strip=True))
            self.assertIn('Legacy', cells[3].get_text(' ', strip=True))
            for url in (GAMMA_LEGACY, THUNDERPICK_LEGACY, 'https://betboom.team/', 'https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/data/identities.json'):
                with self.subTest(url=url):
                    self.assertTrue(cells[3].select_one(f'a[href="{url}"]'))
            aurora_row = next(row for row in rows if 'Aurora' in row.get_text(' ', strip=True))
            self.assertTrue(aurora_row.select_one(f'a[href="{THUNDERPICK_AURORA}"]'))
            point_links = [anchor.get('href') for anchor in page.select('#day-three .checklist a[href]')]
            self.assertIn(GAMMA_LEGACY, point_links)
            self.assertIn(THUNDERPICK_LEGACY, point_links)
            self.assertIn('absent from Hotspawn remains outside the automated board', page.select_one('#day-three table caption').get_text(' ', strip=True))
            self.assertTrue(page.select_one('a[href="review.html"]'))
            self.assertTrue(page.select_one('a[href="https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/research/day2/DAY2-REVIEW-2026-10-15.md"]'))

    def test_flagged_for_review_carries_market_and_quote_time_limitations(self):
        ids = {note['id']: note for note in self.notes}
        market_note = ids['day3-market-only-betboom-legacy-2026-10-15']
        quote_note = ids['day3-thunderpick-quote-timestamp-2026-10-15']
        self.assertIn('not present in the Hotspawn inventory', market_note['finding'])
        self.assertIn('94-point spread', market_note['finding'])
        self.assertIn('updatedAt', market_note['finding'])
        self.assertIn('no quote-update timestamp', market_note['finding'])
        self.assertIn('must not be mistaken for the bookmaker', quote_note['finding'])
        snapshot = json.loads((ROOT / 'data/latest.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            build(snapshot, directory, now=datetime(2026, 10, 15, 23, 0, tzinfo=timezone.utc))
            page = BeautifulSoup((Path(directory) / 'review.html').read_text(), 'html.parser')
            self.assertTrue(page.select_one('#day3-market-only-betboom-legacy-2026-10-15'))
            self.assertTrue(page.select_one('#day3-thunderpick-quote-timestamp-2026-10-15'))
            self.assertTrue(page.select_one(f'a[href="{GAMMA_LEGACY}"]'))
            self.assertTrue(page.select_one(f'a[href="{THUNDERPICK_LEGACY}"]'))


if __name__ == '__main__':
    unittest.main()
