"""Session aeafcbe6: a pick and its probability travel together, in every tier.

Measured failure this session repaired
-------------------------------------
`pages.yml` on `main` failed at the step *"Keep the legacy main:/ root fallback on the
verified build"* on every push/schedule from 2026-10-24T08:12Z (runs 40077144677,
40080448344, 40082763751, 40084520702, 40097410704). That step installs the freshly
refreshed snapshot at the repository root and then re-runs the unit suite against it.
The refresh on the 16:33Z capture (receipt: `research/diagnose-aeafcbe6/`) matched
Hotspawn fixture 1079200 (Color vs ex-Zero Tenacity) to Polymarket market 6072812,
whose `outcomePrices` were the untouched initialisation `["0.5","0.5"]`. The strict
exchange tier published `probabilities: [0.5, 0.5]` with `pick: null`, and because every
later tier begins with `if fixture['probabilities'] is not None: return`, the row could
never be priced or picked by the model or research ladder. 42 unit tests failed on the
staged root (`staged_unit_rc=1`), step 15 exited 3, `upload-pages-artifact` and the
`deploy` job were skipped, and the public board froze at the 08:06:51Z snapshot until
the site's own eight-hour window expired.

The repository held both halves of a contradiction until then: `test_session_92e3275c`,
`test_session_ce45f672`, `test_core` and `test_vrs_mirror_6dd6f287` accepted a published
`[0.5, 0.5]` with no pick, while `test_session_fe7f5de4`, `test_session_f0814674`,
`test_session_f89bb1f8`, `test_session_75ebd2d6` and 30+ others require every open row to
be either picked *and* priced, or explicitly unresolved with blank numbers, a reason and
its attempts. Nothing collided until a genuinely even quote appeared.

The rule now: every tier that publishes numbers treats an exactly even pair as rejected
evidence and lets the ladder continue; the row ends either picked+priced or unresolved
with that limitation. These tests pin the rule in the source and in behaviour, so the
eight-hour freeze cannot come back by a one-line revert in a single tier.
"""
import json
import re
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts import core, vrs

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 24, 16, 33, tzinfo=timezone.utc)
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())


def even_fixture():
    """An open fixture with the ladder untouched, in the shape refresh.py builds."""
    return {
        'id': '1079200', 'teams': ['Color', 'ex-Zero Tenacity'], 'state': 'open',
        'start': '2026-10-25T18:00:00Z', 'best_of': None, 'probabilities': None,
        'fair_odds': None, 'pick': None, 'method': None, 'evidence': [], 'attempts': [],
        'flags': [], 'reason': None, 'reason': None, 'source_url': 'https://www.hotspawn.com/matches/x',
        'resolution_blocked': None,
    }


def even_market(prices=('0.5', '0.5'), bid='0.49', ask='0.51', liquidity='6176.0'):
    """The exact live shape of Polymarket market 6072812 on the 16:33Z capture."""
    return {
        'slug': 'cs2-color-zerote-2026-10-25', 'id': '1238707', 'closed': False,
        'sport': {'sport': 'cs2'},
        'teams': [{'name': 'Color', 'abbreviation': 'color'},
                  {'name': 'ex-Zero Tenacity', 'abbreviation': 'zerote'}],
        'markets': [{
            'id': '6072812', 'question': 'Counter-Strike: Color vs ex-Zero Tenacity (BO3)',
            'sportsMarketType': 'moneyline', 'outcomes': '["Color", "ex-Zero Tenacity"]',
            'outcomePrices': json.dumps(list(prices)), 'gameStartTime': '2026-10-25 18:00:00+00',
            'eventStartTime': '2026-10-25T18:00:00Z',
            'updatedAt': '2026-10-24T16:28:39.056759Z', 'active': True, 'closed': False,
            'acceptingOrders': True, 'bestBid': float(bid), 'bestAsk': float(ask),
            'liquidity': liquidity, 'volume': None,
        }],
    }


class EvenPairHelperTests(unittest.TestCase):
    def test_tolerance_is_the_documented_one(self):
        self.assertEqual(core.EVEN_TOLERANCE, 1e-4)
        self.assertTrue(core.is_even_pair([0.5, 0.5]))
        self.assertTrue(core.is_even_pair(['0.50001', '0.49999']))
        self.assertFalse(core.is_even_pair([0.5002, 0.4998]))
        self.assertFalse(core.is_even_pair([None, 0.5]))
        self.assertFalse(core.is_even_pair([0.6]))

    def test_reason_names_both_probabilities_and_the_ladder(self):
        reason = core.even_reason([0.5, 0.5])
        self.assertIn('0.5 / 0.5', reason)
        self.assertIn('cannot supply a directional pick', reason)
        for ladder in ('researched book line', 'VRS model', 'HLTV Valve-ranking mirror',
                       'research-only tiers'):
            self.assertIn(ladder, reason)


class StrictExchangeTierTests(unittest.TestCase):
    def test_even_live_quote_is_evidence_not_a_published_50_50(self):
        row = even_fixture()
        core.resolve(row, core.polymarket_candidates([even_market()], '2026-10-24T16:30:30Z'),
                     'Polymarket', NOW)
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['fair_odds'])
        self.assertIsNone(row['pick'])
        self.assertIsNone(row['method'])
        attempt = row['attempts'][0]
        self.assertEqual(attempt['status'], 'unresolved')
        self.assertIn('Exactly even two-way quote', attempt['reason'])
        self.assertEqual(attempt['rejected_quote']['raw']['outcomePrices'], '["0.5", "0.5"]')
        self.assertEqual(attempt['rejected_quote']['notice'],
                         'Rejected evidence, not a pick or verified probability.')

    def test_the_row_is_still_open_to_the_next_tier(self):
        # The measured deadlock was not the 50/50 itself but that it stopped the
        # ladder. After the rejection the row must still accept a real line.
        row = even_fixture()
        core.resolve(row, core.polymarket_candidates([even_market()], '2026-10-24T16:30:30Z'),
                     'Polymarket', NOW)
        self.assertIsNone(row['probabilities'])
        later = core.polymarket_candidates(
            [even_market(prices=('0.62', '0.38'), bid='0.61', ask='0.63')], '2026-10-24T16:40:00Z')
        core.resolve(row, later, 'Polymarket', datetime(2026, 10, 24, 16, 45, tzinfo=timezone.utc))
        self.assertEqual(row['method'], 'exchange')
        self.assertEqual(row['pick'], 'Color')
        self.assertGreater(row['probabilities'][0], row['probabilities'][1])

    def test_a_directional_quote_is_untouched_by_the_rule(self):
        row = even_fixture()
        core.resolve(row, core.polymarket_candidates(
            [even_market(prices=('0.71', '0.29'), bid='0.70', ask='0.72')], '2026-10-24T16:30:30Z'),
            'Polymarket', NOW)
        self.assertEqual(row['method'], 'exchange')
        self.assertEqual(row['pick'], 'Color')
        self.assertIsNone(row['reason'])


class EveryPricedTierTests(unittest.TestCase):
    """Source-level: no tier may keep the old `pick=None if even` publication path."""

    TIERS = ('scripts/core.py', 'scripts/vrs.py', 'scripts/vrs_mirror.py')

    def test_no_tier_publishes_a_probability_without_a_pick(self):
        for name in self.TIERS:
            source = (ROOT / name).read_text()
            self.assertNotIn('pick=None if', source, name)
            for retired in ('Equal verified prices; no directional edge.',
                            'Equal model estimate; no directional edge.',
                            'Equal researched book line; no directional edge.'):
                self.assertNotIn(retired, source, name)

    def test_every_tier_that_publishes_numbers_calls_the_shared_rule(self):
        for name in self.TIERS:
            source = (ROOT / name).read_text()
            if name == 'scripts/core.py':
                self.assertGreaterEqual(source.count('is_even_pair('), 3, name)
            else:
                self.assertIn('is_even_pair(', source, name)
                self.assertIn('even_reason(', source, name)

    def test_the_model_helpers_are_importable_from_the_module_refresh_uses(self):
        self.assertTrue(callable(vrs.is_even_pair))
        self.assertTrue(callable(vrs.even_reason))


class CommittedBoardTests(unittest.TestCase):
    def test_no_published_row_carries_a_probability_without_a_pick(self):
        for match in SNAPSHOT['matches']:
            if match.get('probabilities') is not None:
                self.assertIsNotNone(match.get('pick'), match['id'])
                self.assertFalse(core.is_even_pair(match['probabilities']), match['id'])
            else:
                self.assertIsNone(match.get('pick'), match['id'])
                self.assertIsNone(match.get('fair_odds'), match['id'])

    def test_every_open_row_is_picked_and_priced_or_explicitly_unresolved(self):
        opens = [m for m in SNAPSHOT['matches'] if m.get('state') == 'open']
        self.assertTrue(opens, 'a snapshot with no open rows cannot prove coverage')
        for match in opens:
            if match.get('pick'):
                self.assertIsNotNone(match.get('probabilities'), match['id'])
            else:
                self.assertIsNone(match.get('probabilities'), match['id'])
                self.assertTrue(match.get('reason'), match['id'])
                self.assertTrue(match.get('attempts'), match['id'])

    def test_the_published_methodology_states_the_rule(self):
        source = (ROOT / 'scripts/build.py').read_text()
        self.assertIn('a pick and its probability are published together or not at all', source)
        self.assertNotIn('exactly equal verified prices get', source)


if __name__ == '__main__':
    unittest.main()
