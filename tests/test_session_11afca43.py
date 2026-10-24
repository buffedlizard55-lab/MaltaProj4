"""Session 11afca43 (2026-10-24): an exactly even exchange quote is refused.

A genuine two-sided market can price a match exactly 50/50. The rule that
shipped in ``ce45f672`` only refused the *wide*-tier midpoint, so a tight even
market was published as ``probabilities=[0.5, 0.5]`` with ``pick=None``: a row
carrying a probability and no pick. That breaks the board contract (every open
match has a pick), the no-50/50 policy, and it made the row invisible in the
unresolved section, which keys off ``probabilities is None``.

The quote is now refused as evidence for every tier, so the ladder in
``scripts/refresh.py`` keeps falling through to the model and research tiers
instead of stopping on an uninformative 50/50.
"""
import unittest
from pathlib import Path

from scripts.core import (dt, iso, normalize_fixtures, polymarket_candidates,
                          resolve)

ROOT = Path(__file__).resolve().parents[1]
NOW = dt('2026-10-24T08:00:00Z')
FIX = {'id': '1079200', 'sport_alias': 'cs2', 'participants0_name': 'Color',
       'participants1_name': 'ex-Zero Tenacity', 'status': 'scheduled',
       'scheduled_start_time': '2026-10-25T18:00:00Z',
       'lock_time': '2026-10-25T17:54:00Z'}


def fixture():
    return normalize_fixtures([FIX], {}, NOW)[0]


def exchange(prices=('0.5', '0.5'), bid='0.49', ask='0.51'):
    return {'slug': 'cs2-color-zerote', 'sport': {'sport': 'cs2'},
            'markets': [{'id': '6072812',
                         'question': 'Counter-Strike: Color vs ex-Zero Tenacity (BO3)',
                         'sportsMarketType': 'moneyline', 'active': True, 'closed': False,
                         'acceptingOrders': True,
                         'outcomes': '["Color","ex-Zero Tenacity"]',
                         'outcomePrices': '["%s","%s"]' % prices,
                         'gameStartTime': '2026-10-25T18:00:00Z',
                         'updatedAt': iso(NOW), 'bestBid': bid, 'bestAsk': ask,
                         'spread': 0.02, 'liquidity': '6144'}]}


class EvenExchangeQuoteIsRefused(unittest.TestCase):
    def _resolve(self, relax=False):
        f = fixture()
        resolve(f, polymarket_candidates([exchange()], iso(NOW)), 'Polymarket', NOW,
                relax=relax)
        return f

    def test_a_tight_even_quote_publishes_no_probability_and_no_pick(self):
        f = self._resolve()
        self.assertIsNone(f['probabilities'])
        self.assertIsNone(f['pick'])
        self.assertIsNone(f['method'])
        self.assertIsNone(f['fair_odds'])

    def test_the_refusal_is_recorded_as_rejected_evidence(self):
        f = self._resolve()
        self.assertEqual(f['attempts'][0]['status'], 'unresolved')
        self.assertIn('exactly even', f['attempts'][0]['reason'])
        self.assertIn('rejected_quote', f['attempts'][0])
        self.assertEqual(f['attempts'][0]['rejected_quote']['notice'],
                         'Rejected evidence, not a pick or verified probability.')

    def test_the_refusal_also_holds_in_the_wide_tier(self):
        f = self._resolve(relax=True)
        self.assertIsNone(f['probabilities'])
        self.assertIsNone(f['pick'])
        self.assertIn('exactly even', f['attempts'][0]['reason'])

    def test_a_directional_quote_still_publishes_its_pick(self):
        f = fixture()
        resolve(f, polymarket_candidates([exchange(prices=('0.688', '0.312'))], iso(NOW)),
                'Polymarket', NOW)
        self.assertEqual(f['pick'], 'Color')
        self.assertEqual(f['method'], 'exchange')
        self.assertAlmostEqual(f['probabilities'][0], 0.688, places=12)


if __name__ == '__main__':
    unittest.main()
