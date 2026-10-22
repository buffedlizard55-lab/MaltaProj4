"""Replay every acceptance gate against retained PRIMARY raw fields."""
import copy
import json
import math
import unittest
from pathlib import Path
from scripts.core import dt, pick_deadline, quote_polymarket, devig, american, iso, PIN
from scripts.validate import validate_data


def pinnacle_shaped(m):
    """A bookmaker row whose retained raw evidence is a Pinnacle matchup/line.

    Researched book listings (for example EGamersWorld receipts) are also
    published as bookmaker_fallback rows, but their raw evidence is the dated
    receipt, not a Pinnacle line with cutoffAt. The cutoff-deadline tests below
    exercise the Pinnacle raw gates specifically, so they need this shape.
    """
    return (m.get('method') == 'bookmaker_fallback'
            and 'line' in ((m.get('evidence') or [{}])[0].get('raw') or {}))


def synthetic_bookmaker_row(data):
    """Clone one open, priced row with a replayed Pinnacle quote.

    The snapshot may legitimately contain no Pinnacle-shaped bookmaker row (for
    example after every covered fixture locks, or when the only book line is a
    researched EGamersWorld receipt whose raw evidence carries no Pinnacle
    'line'). These integrity tests must still exercise the raw bookmaker gates,
    so the row is rebuilt from a documented synthetic matchup/line and the
    production quote function — never hand-written numbers.
    """
    source = next((m for m in data['matches'] if m['state'] == 'open' and m['method'] == 'exchange'), None)
    if source is None:
        raise unittest.SkipTest('No open priced row available to derive a bookmaker row from')
    row = copy.deepcopy(source)
    odds = [american(-200), american(170)]
    probabilities, margin = devig(odds)
    matchup = {'id': 999001, 'league': {'name': 'CS2 - Synthetic integrity fixture'},
               'participants': [{'alignment': 'home', 'name': row['teams'][0]}, {'alignment': 'away', 'name': row['teams'][1]}],
               'startTime': row['start'], 'status': 'pending', 'isLive': False, 'bestOfX': row['best_of'],
               'type': 'matchup', 'parentId': None}
    line = {'matchupId': 999001, 'type': 'moneyline', 'period': 0, 'status': 'open', 'cutoffAt': row['lock'],
            'prices': [{'designation': 'home', 'price': -200}, {'designation': 'away', 'price': 170}]}
    row['method'] = 'bookmaker_fallback'
    row['probabilities'] = probabilities
    row['fair_odds'] = [1 / p for p in probabilities]
    row['pick'] = row['teams'][0] if probabilities[0] > probabilities[1] else row['teams'][1]
    row['evidence'] = [{'provider': 'Pinnacle', 'id': '999001', 'url': 'https://www.pinnacle.com/en/esports',
        'api_url': PIN + '/sports/12/markets/straight', 'observed_at': data['generated_at'], 'updated_at': None,
        'raw': {'matchup': matchup, 'line': line}, 'probabilities': probabilities,
        'decimal_odds': odds, 'overround': margin, 'source_teams': row['teams'], 'start': row['start'],
        'warning': 'Single bookmaker; price update timestamp not supplied. Observation time shown.'}]
    return row


class EvidenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(Path('data/latest.json').read_text())
        if not any(pinnacle_shaped(m) for m in self.data['matches']):
            row = synthetic_bookmaker_row(self.data)
            self.data['matches'] = [row if m['id'] == row['id'] else m for m in self.data['matches']]
            validate_data(self.data)  # the synthetic baseline itself must replay
        self.exchange = next(m for m in self.data['matches'] if m['method'] == 'exchange')
        self.book = next(m for m in self.data['matches'] if pinnacle_shaped(m))

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
            q = next(m for m in data['matches'] if pinnacle_shaped(m))['evidence'][0]
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
