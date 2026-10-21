"""Session 5ed35e72 regressions.

Two things are pinned here.

1. **Publication can no longer break on the calendar.** The scheduled
   ``pages.yml`` runs on ``main`` failed from 2026-10-20T13:02Z until
   2026-10-21T10:00Z inside *Unit and independent failure-mode tests*, because
   three tests in ``tests/test_session_133fe7ca.py`` built a fixture starting at
   ``2026-10-20T12:00Z`` and then read the wall clock. Once that start passed,
   ``normalize_fixtures`` correctly marked the row ``not_open`` and every pick
   tier declined to act, so the assertions failed and nothing was published for
   29 hours. Those tests are pinned to their own observation instant now, and
   the regression below proves the scenario still exercises an *open* row.
2. **The two label mappings researched on 2026-10-21** turn two open Hotspawn
   fixtures into ordinary market-priced rows. They must fold only the exact
   labels, only at the exact opponent pair and UTC start, and must never pull in
   an academy or a bare organisation label.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.core import (iso, norm, normalize_fixtures, polymarket_candidates,
                          resolve)
from scripts.gap_probe_5ed35e72 import classify

ROOT = Path(__file__).resolve().parents[1]
NOW = iso('2026-10-21T12:38:00Z')
START = '2026-10-21T15:00:00Z'


def fixture(team_a: str, team_b: str, start: str = START, ident: str = '1082762'):
    raw = {'id': ident, 'sport_alias': 'cs2', 'participants0_name': team_a,
           'participants1_name': team_b, 'participants0_id': 'a', 'participants1_id': 'b',
           'status': 'scheduled', 'scheduled_start_time': start,
           'lock_time': '2026-10-21T14:54:00Z',
           'competition_name': 'CIS LAN Championship #9', 'tier': 'c', 'best_of': 3}
    return normalize_fixtures([raw], {}, __import__('scripts.core', fromlist=['dt']).dt(NOW))[0]


def event(teams, start=START, prices=('0.82', '0.18'), ident='5971981', slug='cs2-cs1-bli4-2026-10-21'):
    market = {'id': ident, 'question': 'Counter-Strike: %s vs %s (BO3)' % tuple(teams),
              'sportsMarketType': 'moneyline', 'active': True, 'closed': False,
              'acceptingOrders': True, 'outcomes': json.dumps(list(teams)),
              'outcomePrices': json.dumps(list(prices)), 'gameStartTime': start,
              'updatedAt': NOW, 'bestBid': 0.80, 'bestAsk': 0.84, 'liquidity': '1975.4496'}
    return {'slug': slug, 'sport': {'sport': 'cs2'}, 'markets': [market]}


class LabelMappingTests(unittest.TestCase):
    def test_the_two_exact_labels_fold(self):
        self.assertEqual(norm('ex-CYBERSHOKE'), norm('CYBERSHOKE Esports'))
        self.assertEqual(norm('flacons'), norm('Team flacons'))

    def test_academy_and_bare_labels_are_not_folded(self):
        self.assertNotEqual(norm('CYBERSHOKE Prospects'), norm('CYBERSHOKE Esports'))
        self.assertNotEqual(norm('CYBERSHOKE'), norm('ex-CYBERSHOKE'))
        self.assertNotEqual(norm('flacons'), norm('Falcons'))

    def test_entries_carry_primary_sources_and_a_bounded_basis(self):
        register = json.loads((ROOT / 'data/identities.json').read_text())['aliases']
        for canonical in ('ex-CYBERSHOKE', 'flacons'):
            entry = next(a for a in register if a['canonical'] == canonical)
            self.assertTrue(entry['source'].startswith('https://www.hltv.org/matches/'), canonical)
            self.assertTrue(entry['additional_source'].startswith('https://gamma-api.polymarket.com/'), canonical)
            basis = entry['basis'].lower()
            self.assertIn('utc start', basis, canonical)
            self.assertIn('exact opponent', basis, canonical)
            self.assertGreaterEqual(len(entry['names']), 2, canonical)


class ExchangePricingAfterMappingTests(unittest.TestCase):
    def test_cybershoke_is_priced_at_the_exact_start(self):
        row = fixture('ex-CYBERSHOKE', 'BlinkDagger')
        self.assertEqual(row['state'], 'open')
        resolve(row, polymarket_candidates([event(('CYBERSHOKE Esports', 'BlinkDagger'))], NOW),
                'Polymarket', __import__('scripts.core', fromlist=['dt']).dt(NOW))
        self.assertIsNotNone(row['probabilities'], row['attempts'])
        self.assertEqual(row['method'], 'exchange')
        self.assertEqual(row['pick'], 'ex-CYBERSHOKE')
        self.assertAlmostEqual(row['probabilities'][0], 0.82, places=6)

    def test_flacons_is_priced_at_the_exact_start(self):
        row = fixture('UPGRADE', 'flacons', ident='1082763')
        resolve(row, polymarket_candidates([event(('UPGRADE', 'Team flacons'),
                                                   prices=('0.545', '0.455'), ident='5971985',
                                                   slug='cs2-upgrad-tf4-2026-10-21')], NOW),
                'Polymarket', __import__('scripts.core', fromlist=['dt']).dt(NOW))
        self.assertIsNotNone(row['probabilities'], row['attempts'])
        self.assertEqual(row['pick'], 'UPGRADE')

    def test_reversed_label_order_still_points_at_the_right_team(self):
        row = fixture('ex-CYBERSHOKE', 'BlinkDagger')
        resolve(row, polymarket_candidates([event(('BlinkDagger', 'CYBERSHOKE Esports'),
                                                   prices=('0.18', '0.82'))], NOW),
                'Polymarket', __import__('scripts.core', fromlist=['dt']).dt(NOW))
        self.assertEqual(row['pick'], 'ex-CYBERSHOKE')
        # Orientation follows the fixture's own team order, so the 0.82 side is
        # ex-CYBERSHOKE even though the event lists it second.
        self.assertAlmostEqual(row['probabilities'][0], 0.82, places=6)
        self.assertAlmostEqual(row['probabilities'][1], 0.18, places=6)

    def test_a_different_utc_start_is_not_priced(self):
        row = fixture('ex-CYBERSHOKE', 'BlinkDagger', start='2026-10-21T16:00:00Z')
        resolve(row, polymarket_candidates([event(('CYBERSHOKE Esports', 'BlinkDagger'))], NOW),
                'Polymarket', __import__('scripts.core', fromlist=['dt']).dt(NOW))
        self.assertIsNone(row['probabilities'])

    def test_a_different_opponent_is_not_priced(self):
        row = fixture('ex-CYBERSHOKE', 'BlinkDagger')
        resolve(row, polymarket_candidates([event(('CYBERSHOKE Esports', 'flacons'))], NOW),
                'Polymarket', __import__('scripts.core', fromlist=['dt']).dt(NOW))
        self.assertIsNone(row['probabilities'])

    def test_the_bare_organisation_label_is_not_priced(self):
        row = fixture('CYBERSHOKE', 'BlinkDagger')
        resolve(row, polymarket_candidates([event(('CYBERSHOKE Esports', 'BlinkDagger'))], NOW),
                'Polymarket', __import__('scripts.core', fromlist=['dt']).dt(NOW))
        self.assertIsNone(row['probabilities'])


class CalendarDeterminismTests(unittest.TestCase):
    """The publication outage of 2026-10-20 must not be able to come back."""

    def test_the_pinned_scenario_is_still_open(self):
        from tests.test_session_133fe7ca import PINNED_NOW, fixture_for
        row = fixture_for('Sangal', 'Aurora YB')
        self.assertEqual(row['state'], 'open')
        self.assertLess(PINNED_NOW, __import__('scripts.core', fromlist=['dt']).dt(row['start']))

    def test_fixture_helper_does_not_read_the_wall_clock(self):
        source = (ROOT / 'tests/test_session_133fe7ca.py').read_text()
        helper = source.split('def fixture_for', 1)[1].split('def ', 1)[0]
        self.assertNotIn('datetime.now', helper)


class GapProbeTests(unittest.TestCase):
    def test_classification_names_the_three_gap_kinds(self):
        self.assertEqual(classify({'pick': None, 'probabilities': None}), 'no_pick')
        self.assertEqual(classify({'pick': 'Zetta', 'probabilities': None}), 'pick_without_price')
        self.assertEqual(classify({'pick': 'Zetta', 'probabilities': [0.6, 0.4]}), 'price_without_pick')

    def test_live_gap_report_matches_its_own_snapshot(self):
        gaps = json.loads((ROOT / 'research/harvest-5ed35e72/gaps.json').read_text())
        snapshot = json.loads((ROOT / 'research/harvest-5ed35e72/snapshot.json').read_text())
        open_rows = [r for r in snapshot['matches'] if r['state'] == 'open']
        self.assertEqual(gaps['open_total'], len(open_rows))
        self.assertEqual(gaps['open_priced'],
                         sum(1 for r in open_rows if r['probabilities'] is not None))
        missing = [r['id'] for r in open_rows if not r['pick'] or r['probabilities'] is None]
        self.assertEqual({g['id'] for g in gaps['gaps']}, set(missing))


if __name__ == '__main__':
    unittest.main()
