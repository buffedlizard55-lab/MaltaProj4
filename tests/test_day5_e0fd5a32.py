"""Deterministic checks for the session-e0fd5a32 Day-5 receipts."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.day5_e0fd5a32 import (DEFAULT_RECEIPT, decimal_from_american, devig,
                                  implied_from_american, verify)


class Day5ReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DEFAULT_RECEIPT.read_text())

    def test_american_conversions(self):
        self.assertAlmostEqual(decimal_from_american(170), 2.70, places=12)
        self.assertAlmostEqual(decimal_from_american(-238), 1.4201680672268908, places=12)
        self.assertAlmostEqual(implied_from_american(170), 0.37037037037037035, places=12)
        self.assertAlmostEqual(implied_from_american(-238), 0.7041420118343196, places=12)

    def test_third_place_published_values(self):
        calc = devig('Aurora', 'Falcons', {'Aurora': 170, 'Falcons': -238})
        self.assertAlmostEqual(calc['overround'], 1.07451238220469, places=12)
        self.assertAlmostEqual(calc['devig']['Aurora'], 0.344687, places=6)
        self.assertAlmostEqual(calc['devig']['Falcons'], 0.655313, places=6)
        self.assertAlmostEqual(calc['fair_decimal']['Aurora'], 2.901183, places=6)
        self.assertAlmostEqual(calc['fair_decimal']['Falcons'], 1.525988, places=6)

    def test_final_published_values(self):
        calc = devig('FURIA', 'BETBOOM', {'FURIA': -286, 'BETBOOM': 190})
        self.assertAlmostEqual(calc['overround'], 1.0857602286939432, places=12)
        self.assertAlmostEqual(calc['devig']['FURIA'], 0.682409, places=6)
        self.assertAlmostEqual(calc['devig']['BETBOOM'], 0.317591, places=6)
        self.assertAlmostEqual(calc['fair_decimal']['FURIA'], 1.465397, places=6)
        self.assertAlmostEqual(calc['fair_decimal']['BETBOOM'], 3.148705, places=6)

    def test_every_stored_value_reproduces(self):
        rows = verify(DEFAULT_RECEIPT)
        self.assertEqual([row['id'] for row in rows], ['2399416', '2399417'])

    def test_picks_are_the_higher_probability(self):
        picks = {fixture['id']: fixture['pick'] for fixture in self.data['fixtures']}
        self.assertEqual(picks, {'2399416': 'Falcons', '2399417': 'FURIA'})

    def test_overround_above_one_means_no_arbitrage_claim(self):
        for fixture in self.data['fixtures']:
            self.assertGreater(fixture['overround'], 1.0)

    def test_fixture_identity_and_format(self):
        third, final = self.data['fixtures']
        self.assertEqual((third['team_a'], third['team_b'], third['best_of']), ('Aurora', 'Falcons', 3))
        self.assertEqual((final['team_a'], final['team_b'], final['best_of']), ('FURIA', 'BETBOOM', 5))
        self.assertEqual(third['start_utc'], '2026-10-18T11:30:00Z')
        self.assertEqual(final['start_utc'], '2026-10-18T15:00:00Z')

    def test_bookmaker_sources_are_primary_and_https(self):
        for fixture in self.data['fixtures']:
            self.assertEqual(fixture['book'], 'Thunderpick')
            self.assertTrue(fixture['book_listing_url'].startswith('https://thunderpick.io/'))
            self.assertTrue(fixture['fixture_source_url'].startswith('https://www.hltv.org/matches/'))

    def test_hotspawn_non_listing_is_recorded(self):
        listing = self.data['hotspawn_listing']
        self.assertIn('not the main Thunderpick World Championship 2026 event', listing['finding'])
        self.assertIn('neither can be submitted', listing['finding'])

    def test_roster_premise_cites_july_dates(self):
        premise = self.data['roster_premise']
        self.assertIn('July 2026 rebuild', premise['finding'])
        self.assertIn('8 July 2026', premise['finding'])
        self.assertIn('No onboarding factor', premise['finding'])
        self.assertTrue(any('hltv.org/news/45082' in url for url in premise['sources']))

    def test_limitations_are_not_blank(self):
        self.assertGreaterEqual(len(self.data['limitations']), 4)
        self.assertTrue(all(isinstance(item, str) and item.strip() for item in self.data['limitations']))

    def test_receipt_path_exists(self):
        self.assertTrue(DEFAULT_RECEIPT.exists())
        self.assertGreater(DEFAULT_RECEIPT.stat().st_size, 1000)


if __name__ == '__main__':
    unittest.main()


class Day5PublishedTests(unittest.TestCase):
    """The final-day block must carry the verified external line, not a blank."""

    @classmethod
    def setUpClass(cls):
        from scripts import build
        cls.build = build
        cls.notes = json.loads((Path(__file__).resolve().parents[1] / 'data' / 'analysis.json').read_text())
        cls.data = json.loads((Path(__file__).resolve().parents[1] / 'data' / 'latest.json').read_text())
        cls.html = build.analysis_page(cls.data)

    def test_cards_publish_the_thunderpick_devig(self):
        cards = self.notes['day_five_guidance']['not_listed']
        self.assertEqual(len(cards), 2)
        self.assertEqual([card['pick'] for card in cards], ['Falcons', 'FURIA'])
        # 17 Oct 65.53% superseded by a54996e1 re-read 18 Oct 00:55Z (+140/-200)
        self.assertIn('61.54%', cards[0]['pick_detail'])
        self.assertIn('68.24%', cards[1]['pick_detail'])
        for card in cards:
            self.assertIn('thunderpick.io', card['market']['url'])
            self.assertNotIn('probabilities', card)

    def test_rendered_page_shows_the_prices_and_the_picks(self):
        # Cards are now board rows (1080209/1080210): build renders the live board
        # link instead of the dated Thunderpick quote; percentages stay in the summary.
        for needle in ('61.54%', '68.24%', 'Now on the Hotspawn board',
                       'evidence.html#match-1080209', 'evidence.html#match-1080210'):
            self.assertIn(needle, self.html)

    def test_the_front_page_points_at_the_final_day(self):
        self.assertEqual('day_five_guidance', self.notes.get('front_page_plan'))
        self.assertIn('analysis.html#day-five-guidance', self.build.overview(self.data))

    def test_the_card_flags_the_unverified_second_book_and_card_discrepancy(self):
        block = self.notes['day_five_guidance']
        unpriced = ' '.join(item['limitation'] for item in block['unpriced'])
        unverified = ' '.join(block['unverified'])
        self.assertIn('One bookmaker is not consensus', unpriced)
        # Historical +150 card discrepancy superseded; current unverified flags the verified move
        self.assertIn('+140', unverified)
        self.assertIn('+170', unverified)
