"""Exact-tie fallback contract for the 2026-10-24 fresh harvest.

A balanced quote is retained as evidence, but it cannot answer the requested
directional pick. Every numeric rung must therefore leave the row unpriced and
allow the next independent rung to run; no favourite is invented from a tie.
"""
import unittest

from scripts import vrs, vrs_mirror
from scripts.core import (book_research_pick, dt, iso, normalize_fixtures,
                          polymarket_candidates, resolve)

NOW = dt('2026-10-24T16:00:00Z')
START = '2026-10-25T18:00:00Z'


def fixture():
    raw = {
        'id': 'tie-fixture', 'sport_alias': 'cs2',
        'participants0_name': 'Alpha', 'participants1_name': 'Bravo',
        'status': 'scheduled', 'scheduled_start_time': START,
        'lock_time': '2026-10-25T17:54:00Z',
    }
    return normalize_fixtures([raw], {}, NOW)[0]


def event(prices=('0.5', '0.5'), bid=0.49, ask=0.51):
    return {
        'slug': 'cs2-alpha-bravo', 'sport': {'sport': 'cs2'},
        'markets': [{
            'id': 'tie-market', 'question': 'Counter-Strike: Alpha vs Bravo (BO3)',
            'sportsMarketType': 'moneyline', 'active': True, 'closed': False,
            'acceptingOrders': True, 'outcomes': '["Alpha","Bravo"]',
            'outcomePrices': '["%s","%s"]' % prices,
            'gameStartTime': START, 'updatedAt': iso(NOW),
            'bestBid': bid, 'bestAsk': ask, 'liquidity': '1000',
        }],
    }


def standings(bravo_points=1000):
    return {
        'as_of': '2026-10-05',
        'teams': [
            {'standing': 1, 'points': 1000, 'name': 'Alpha',
             'roster': ['a1', 'a2', 'a3', 'a4', 'a5'], 'details': 'alpha.md'},
            {'standing': 2, 'points': bravo_points, 'name': 'Bravo',
             'roster': ['b1', 'b2', 'b3', 'b4', 'b5'], 'details': 'bravo.md'},
        ],
    }


VRS_META = {
    'file': 'standings_global_2026_10_05.md', 'commit': 'c' * 40,
    'raw_url': vrs.RAW + '/' + 'c' * 40 + '/live/2026/standings_global_2026_10_05.md',
    'blob_url': vrs.BLOB + '/' + 'c' * 40 + '/live/2026/standings_global_2026_10_05.md',
    'details_base': vrs.BLOB + '/' + 'c' * 40 + '/live/2026/',
    'observed_at': iso(NOW), 'origin': 'test',
}
MIRROR_META = {
    'url': vrs_mirror.RANKING, 'observed_at': iso(NOW), 'sha256': 'd' * 64,
    'as_of': '2026-10-24', 'heading': 'Valve global ranking on October 24th, 2026',
    'teams_count': 2, 'parsed_by': 'test',
}
OFFICIAL = {'file': VRS_META['file'], 'commit': 'c' * 40, 'as_of': '2026-10-05'}


class ExactTieFallbackTests(unittest.TestCase):
    def assert_rejected_tie(self, row):
        self.assertIsNone(row['pick'])
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['fair_odds'])
        self.assertIsNone(row['method'])
        self.assertEqual(row['evidence'], [])
        attempt = row['attempts'][-1]
        self.assertEqual(attempt['status'], 'unresolved')
        self.assertIn('exactly even', attempt['reason'])
        self.assertIn('no directional edge', attempt['reason'])
        self.assertEqual(attempt['rejected_quote']['probabilities'], [0.5, 0.5])
        self.assertEqual(attempt['rejected_quote']['notice'],
                         'Rejected evidence, not a pick or verified probability.')

    def resolve_market(self, row, relax=False, **kwargs):
        candidates = polymarket_candidates([event(**kwargs)], iso(NOW))
        resolve(row, candidates, 'Polymarket', NOW, relax=relax)

    def test_strict_exchange_tie_is_rejected_then_vrs_can_resolve(self):
        row = fixture()
        self.resolve_market(row)
        self.assert_rejected_tie(row)
        vrs.apply(row, standings(bravo_points=700), VRS_META)
        self.assertEqual(row['method'], 'model_vrs')
        self.assertEqual(row['pick'], 'Alpha')
        self.assertGreater(row['probabilities'][0], row['probabilities'][1])
        self.assertEqual(len(row['attempts']), 2)

    def test_wide_exchange_tie_is_also_rejected(self):
        row = fixture()
        self.resolve_market(row, relax=True, bid=0.24, ask=0.76)
        self.assert_rejected_tie(row)

    def test_directional_exchange_still_publishes_normally(self):
        row = fixture()
        self.resolve_market(row, prices=('0.6', '0.4'), bid=0.59, ask=0.61)
        self.assertEqual(row['method'], 'exchange')
        self.assertEqual(row['pick'], 'Alpha')
        self.assertEqual(row['probabilities'], [0.6, 0.4])

    def test_book_tie_is_rejected_then_vrs_can_resolve(self):
        row = fixture()
        receipt = {
            'provider': 'Synthetic book test', 'id': 'tie-book',
            'fixture_id': row['id'], 'source_teams': ['Alpha', 'Bravo'],
            'team_aliases': [['Alpha'], ['Bravo']], 'start': START,
            'odds': [2.0, 2.0], 'observed_at': iso(NOW),
            'url': 'https://example.com/official-book-tie',
        }
        book_research_pick(row, [receipt], NOW)
        self.assert_rejected_tie(row)
        vrs.apply(row, standings(bravo_points=700), VRS_META)
        self.assertEqual(row['pick'], 'Alpha')
        self.assertEqual(row['method'], 'model_vrs')

    def test_official_vrs_tie_is_rejected_and_can_be_retried(self):
        row = fixture()
        vrs.apply(row, standings(), VRS_META)
        self.assert_rejected_tie(row)
        vrs.apply(row, standings(bravo_points=700), VRS_META)
        self.assertEqual(row['pick'], 'Alpha')
        self.assertEqual(row['method'], 'model_vrs')

    def test_hltv_valve_mirror_tie_is_rejected(self):
        row = fixture()
        vrs_mirror.apply(row, standings(), MIRROR_META, {}, OFFICIAL)
        self.assert_rejected_tie(row)


if __name__ == '__main__':
    unittest.main()
