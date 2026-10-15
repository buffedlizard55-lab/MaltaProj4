"""Synthetic mutation tests, never production match data."""
import copy
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('audit', Path(__file__).with_name('audit_snapshot.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def example():
    raw = {'id': 'test', 'participants0_name': 'Alpha', 'participants1_name': 'Beta',
        'participants0_id': 'a', 'participants1_id': 'b', 'competition_name': 'Synthetic test',
        'sport_alias': 'cs2', 'status': 'scheduled', 'scheduled_start_time': '2026-10-15T12:00:00Z',
        'lock_time': '2026-10-15T11:54:00Z'}
    quote = {'provider': 'Polymarket', 'source_teams': ['Beta', 'Alpha'], 'start': raw['scheduled_start_time'],
        'observed_at': '2026-10-14T08:00:00Z', 'url': 'https://polymarket.com/', 'api_url': 'https://gamma-api.polymarket.com/',
        'raw': {'sportsMarketType': 'moneyline', 'outcomes': ['Beta', 'Alpha'], 'active': True,
            'closed': False, 'acceptingOrders': True, 'outcomePrices': ['.4', '.6'],
            'updatedAt': '2026-10-14T08:00:00Z', 'bestBid': .39, 'bestAsk': .41, 'liquidity': 500}}
    match = {'id': 'test', 'teams': ['Alpha', 'Beta'], 'team_ids': ['a', 'b'],
        'competition': 'Synthetic test', 'tier': None, 'best_of': None, 'source_status': 'scheduled',
        'start': raw['scheduled_start_time'], 'lock': raw['lock_time'], 'state': 'open',
        'source_url': 'https://play.hotspawn.com/cs2-pickems', 'probabilities': [.6, .4],
        'fair_odds': [1/.6, 1/.4], 'pick': 'Alpha', 'method': 'exchange', 'evidence': [quote]}
    return {'generated_at': '2026-10-14T08:00:00Z', 'fixture_evidence': [raw], 'matches': [match]}


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.s = example()
        self.m = self.s['matches'][0]

    def errors(self):
        return audit.inspect(self.s)[1]

    def test_reversed_outcomes_calculated_independently(self):
        self.assertEqual(self.errors(), [])

    def test_dropped_fixture(self):
        self.s['matches'] = []
        self.assertTrue(self.errors())

    def test_duplicate(self):
        self.s['matches'].append(copy.deepcopy(self.m))
        self.assertTrue(self.errors())

    def test_probability_mutation(self):
        self.m['probabilities'] = [.61, .39]
        self.assertTrue(self.errors())

    def test_unverified_format_filled(self):
        self.m['best_of'] = 3
        self.assertTrue(self.errors())

    def test_hotspawn_popularity_rejected(self):
        self.s['fixture_evidence'][0]['participants0_picked_percent'] = 99
        self.assertTrue(self.errors())

    def test_stale_quote(self):
        self.m['evidence'][0]['observed_at'] = '2026-10-13T08:00:00Z'
        self.assertTrue(self.errors())

    def test_unverified_alias(self):
        self.m['evidence'][0]['source_teams'][1] = 'Alpha Academy'
        self.assertTrue(self.errors())

    def test_locked_pick(self):
        self.s['generated_at'] = '2026-10-15T11:55:00Z'
        self.assertTrue(self.errors())

    def test_unresolved_remains_blank(self):
        self.m.update(probabilities=None, fair_odds=None, pick=None, method=None, evidence=[], reason='No independently verified price')
        self.assertEqual(self.errors(), [])
        self.m['pick'] = 'Alpha'
        self.assertTrue(self.errors())

    def test_wide_exchange_spread(self):
        self.m['evidence'][0]['raw'].update(bestBid=.07, bestAsk=.94)
        self.assertTrue(self.errors())

    def test_timezone_missing(self):
        self.m['start'] = '2026-10-15T12:00:00'
        self.assertTrue(self.errors())


if __name__ == '__main__':
    unittest.main()
