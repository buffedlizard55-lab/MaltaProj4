"""Replay every acceptance gate against retained PRIMARY raw fields."""
import copy
import json
import math
import unittest
from pathlib import Path
from scripts.core import dt, pick_deadline, quote_polymarket
from scripts.validate import validate_data


class EvidenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(Path('data/latest.json').read_text())
        self.exchange = next(m for m in self.data['matches'] if m['method'] == 'exchange')
        self.book = next(m for m in self.data['matches'] if m['method'] == 'bookmaker_fallback')

    def test_raw_identity_cannot_be_replaced_by_derived_labels(self):
        self.exchange['evidence'][0]['raw']['outcomes'] = '["TEST_ONLY_A", "TEST_ONLY_B"]'
        with self.assertRaises((AssertionError, ValueError)):
            validate_data(self.data)

    def test_nonfinite_liquidity_never_valid(self):
        for value in ['NaN', 'Infinity', '-Infinity']:
            data = copy.deepcopy(self.data)
            quote = next(m for m in data['matches'] if m['method'] == 'exchange')['evidence'][0]
            quote['raw']['liquidity'] = value
            with self.subTest(value=value), self.assertRaises((AssertionError, ValueError)):
                validate_data(data)

    def test_raw_quality_gates_replayed(self):
        for change in [{'bestBid': .01, 'bestAsk': .99}, {'liquidity': '1'}, {'acceptingOrders': False},
                       {'sportsMarketType': 'child_moneyline'}, {'updatedAt': '2000-01-01T00:00:00Z'},
                       {'outcomePrices': '["NaN", "0.5"]'}]:
            data = copy.deepcopy(self.data)
            q = next(m for m in data['matches'] if m['method'] == 'exchange')['evidence'][0]
            q['raw'].update(change)
            with self.subTest(change=change), self.assertRaises((AssertionError, ValueError)):
                validate_data(data)

    def test_bookmaker_scope_cutoff_and_identity_replayed(self):
        for target, change in [('line', {'period': 1}), ('line', {'isAlternate': True}),
                               ('line', {'cutoffAt': '2000-01-01T00:00:00Z'}),
                               ('matchup', {'parentId': 999}), ('matchup', {'type': 'special'}),
                               ('matchup', {'isLive': True})]:
            data = copy.deepcopy(self.data)
            q = next(m for m in data['matches'] if m['method'] == 'bookmaker_fallback')['evidence'][0]
            q['raw'][target].update(change)
            with self.subTest(change=change), self.assertRaises((AssertionError, ValueError)):
                validate_data(data)

    def test_start_bound_to_raw_quote(self):
        self.exchange['evidence'][0]['start'] = '2099-01-01T00:00:00Z'
        with self.assertRaises((AssertionError, ValueError)):
            validate_data(self.data)

    def test_known_series_format_must_match(self):
        m = self.exchange
        m['best_of'] = 99
        next(r for r in self.data['fixture_evidence'] if str(r['id']) == m['id'])['best_of'] = 99
        with self.assertRaises((AssertionError, ValueError)):
            validate_data(self.data)

    def test_source_deadline_includes_update_time(self):
        m = copy.deepcopy(self.exchange)
        q = m['evidence'][0]
        q['updated_at'] = '2026-10-15T01:00:00Z'
        q['observed_at'] = '2026-10-15T02:00:00Z'
        m['start'] = '2026-10-15T12:00:00Z'
        m['lock'] = '2026-10-15T11:54:00Z'
        self.assertEqual(pick_deadline(m, '2026-10-15T02:00:00Z'), '2026-10-15T09:00:00Z')

    def test_source_deadline_includes_book_cutoff(self):
        m = copy.deepcopy(self.book)
        m['start'] = '2026-10-15T12:00:00Z'
        m['lock'] = '2026-10-15T11:54:00Z'
        m['evidence'][0]['observed_at'] = '2026-10-15T08:00:00Z'
        m['evidence'][0]['raw']['line']['cutoffAt'] = '2026-10-15T09:00:00Z'
        self.assertEqual(pick_deadline(m, '2026-10-15T08:00:00Z'), '2026-10-15T09:00:00Z')

    def test_missing_required_expiry_fact_fails_closed(self):
        self.book['evidence'][0]['raw']['line']['cutoffAt'] = None
        self.assertIsNone(pick_deadline(self.book, self.data['fixtures_observed_at']))


if __name__ == '__main__':
    unittest.main()
