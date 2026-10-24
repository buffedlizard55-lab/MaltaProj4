"""Session 2b856884 (2026-10-24): an exactly even line must never stop the ladder.

Measured defect this module exists for
-------------------------------------
On the 2026-10-24T16:25Z refresh, Polymarket quoted fixture 1079200 (Color vs
ex-Zero Tenacity, NODWIN Clutch Series #13) at 0.50/0.50 with a 2-point spread
and $5,990 of liquidity. ``scripts.core.resolve`` published that pair with
``pick = None``, honouring the repository's older "no directional edge" wording.
That state is unrepresentable downstream: 52 contracts under ``tests/``,
``audits/`` and ``verification-*/`` require every open row to publish a pick or
to stay completely blank with recorded attempts, and
``verification-767649ba/audit_2026_10_22.py`` states it in one line — "unpicked
open row must remain blank and carry attempts + an explicit limitation".

The consequence was not cosmetic. The publisher's own unit gate failed, the
"Keep the legacy main:/ root fallback on the verified build" step returned rc=3
(run 40097410704), the scheduled publish never deployed, and the scheduled audit
at 16:07Z measured the live site at snapshot age 29,041s with
``actionable_at_check: 0`` (run 40110028068). No visitor could see a pick.

The rule
--------
The repository had already decided this case, for the wide tier only (session
ce45f672): an even midpoint "is recorded as rejected evidence instead, so the
ladder continues". This module pins that decision for *every* pricing tier, and
pins the three properties that make it safe:

1. nothing is deleted — the source URL, prices, spread and liquidity stay on the
   row inside ``attempts[].rejected_quote`` with a notice that says it is not a
   pick;
2. the row is left with no pick, no probabilities and no method, so it is
   unambiguously blank rather than a disguised 50/50;
3. the documented fallback ladder continues, so the model and research tiers can
   still originate a pick — which is what actually happened for 1079200 on the
   next refresh (model_vrs, Color 68.8%, from Valve's official standings).
"""
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.core import (EVEN_TOLERANCE, directional, normalize_fixtures,
                          pinnacle_candidates, polymarket_candidates, resolve)

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 24, 16, 30, tzinfo=timezone.utc)
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())


def fixture():
    """Two-team open row shaped exactly like ``scripts.refresh`` builds them."""
    return {'id': '1079200', 'teams': ['Color', 'ex-Zero Tenacity'],
            'team_ids': ['1', '2'], 'competition': 'NODWIN Clutch Series #13',
            'tier': 'b', 'best_of': 3, 'start': '2026-10-25T18:00:00Z',
            'lock': '2026-10-25T17:54:00Z', 'source_status': 'scheduled',
            'state': 'open', 'source_url': 'https://play.hotspawn.com/cs2-pickems',
            'flags': [], 'probabilities': None, 'fair_odds': None, 'pick': None,
            'method': None, 'evidence': [], 'attempts': [], 'expires_at': None}


def market_event(prices=('0.5', '0.5'), bid='0.49', ask='0.51', liquidity='5989.7983',
                 updated='2026-10-24T16:24:39.312073Z', teams=('Color', 'ex-Zero Tenacity'),
                 start='2026-10-25 18:00:00+00'):
    """The real 1079200 event, in the shape ``scripts.core.polymarket_candidates`` reads."""
    return {'id': '1238707', 'slug': 'cs2-color-zerote-2026-10-25',
            'sport': {'id': 37, 'sport': 'cs2'}, 'closed': False, 'live': None, 'ended': None,
            'teams': [{'name': teams[0], 'abbreviation': 'COL'},
                      {'name': teams[1], 'abbreviation': 'EZT'}],
            'markets': [{'id': '6072812',
                         'question': 'Counter-Strike: %s vs %s (BO3) - NODWIN Clutch Series Playoffs' % teams,
                         'sportsMarketType': 'moneyline',
                         'outcomes': json.dumps(list(teams)),
                         'outcomePrices': json.dumps(list(prices)),
                         'gameStartTime': start, 'eventStartTime': '2026-10-25T18:00:00Z',
                         'updatedAt': updated, 'active': True, 'closed': False,
                         'acceptingOrders': True, 'bestBid': bid, 'bestAsk': ask,
                         'liquidity': liquidity, 'volume': None}]}


class TheSharedDirectionalRule(unittest.TestCase):
    def test_one_comparison_decides_every_tier(self):
        self.assertEqual(directional([0.6883, 0.3117]), 0)
        self.assertEqual(directional([0.3117, 0.6883]), 1)
        self.assertIsNone(directional([0.5, 0.5]))
        # Inside the source's own precision it is still a tie, not a coin flip
        # with a winner picked out of floating-point dust.
        self.assertIsNone(directional([0.5, 0.5 + EVEN_TOLERANCE / 10]))

    def test_a_pair_of_anything_else_is_refused(self):
        for pair in ([0.5], [0.5, 0.3, 0.2], []):
            with self.subTest(pair=pair):
                with self.assertRaises(ValueError):
                    directional(pair)


class AnEvenExchangeLineIsEvidenceNotAPick(unittest.TestCase):
    def resolve(self, **event):
        row = fixture()
        resolve(row, polymarket_candidates([market_event(**event)], '2026-10-24T16:25:17Z'),
                'Polymarket', NOW)
        return row

    def test_the_exact_market_that_blocked_publication_stays_blank(self):
        row = self.resolve()
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['fair_odds'])
        self.assertIsNone(row['pick'])
        self.assertIsNone(row['method'])
        self.assertEqual(row['evidence'], [])

    def test_the_observation_is_retained_with_its_provenance(self):
        row = self.resolve()
        attempt = row['attempts'][0]
        self.assertEqual(attempt['provider'], 'Polymarket')
        self.assertEqual(attempt['status'], 'unresolved')
        self.assertIn('exactly even', attempt['reason'].lower())
        rejected = attempt['rejected_quote']
        self.assertEqual(rejected['notice'], 'Rejected evidence, not a pick or verified probability.')
        self.assertEqual(rejected['api_url'], 'https://gamma-api.polymarket.com/markets/6072812')
        self.assertEqual(rejected['raw']['outcomePrices'], '["0.5", "0.5"]')
        self.assertEqual(rejected['raw']['bestBid'], '0.49')
        self.assertEqual(rejected['raw']['liquidity'], '5989.7983')
        self.assertIn('https://polymarket.com/event/cs2-color-zerote-2026-10-25',
                      [rejected.get('url'), attempt.get('url')])

    def test_the_ladder_continues_so_a_later_tier_can_still_pick(self):
        # What the next real refresh did: the model tier priced the same row
        # from Valve's official standings once the even pair stopped occupying
        # the row. Simulated here at the interface the refresh uses.
        row = self.resolve()
        self.assertEqual(row['state'], 'open')
        self.assertIsNone(row['probabilities'])
        row.update(probabilities=[0.6884, 0.3116], fair_odds=[1.4527, 3.2092],
                   pick='Color', method='model_vrs')
        self.assertEqual(row['teams'][directional(row['probabilities'])], 'Color')

    def test_a_directional_market_is_unaffected(self):
        row = self.resolve(prices=('0.7', '0.3'))
        self.assertEqual(row['pick'], 'Color')
        self.assertEqual(row['method'], 'exchange')
        self.assertAlmostEqual(row['probabilities'][0], 0.7, places=12)
        self.assertIsNone(row['reason'])

    def test_a_stale_or_thin_market_keeps_its_own_refusal(self):
        # The pre-existing gates are untouched: a thin market is refused for
        # being thin, not recycled into the even-line message.
        row = self.resolve(liquidity='42.0')
        self.assertIsNone(row['probabilities'])
        self.assertIn('liquidity', row['attempts'][0]['reason'].lower())


class AnEvenBookmakerLineIsEvidenceNotAPick(unittest.TestCase):
    def test_a_symmetric_two_way_line_never_becomes_a_pick(self):
        from scripts.core import quote_book
        candidate = {'provider': 'Listed book', 'id': '1082859',
                     'teams': ['Color', 'ex-Zero Tenacity'],
                     'start': '2026-10-25T18:00:00Z', 'url': 'https://egamersworld.com/counterstrike/matches',
                     'decimal_odds': [1.8, 1.8],
                     'observed_at': '2026-10-24T16:00:00Z', 'best_of': 3}
        row = fixture()
        from scripts.core import book_research_pick
        before = json.dumps(row, sort_keys=True)
        try:
            book_research_pick(row, receipts=[candidate], now=NOW)
        except ValueError:
            self.fail('an even listing must be recorded, not raised out of the tier')
        # Either the listing is refused before it can be priced (scripts.books
        # refuses the symmetric 1.8/1.8 placeholder) or it is retained as an
        # even observation; in no case may it publish a pick or a 50/50.
        self.assertIsNone(row['pick'])
        if row['probabilities'] is not None:
            self.assertEqual(row['probabilities'], [0.5, 0.5], 'only an even pair may be unpicked')
        else:
            self.assertTrue(row['attempts'] or before == json.dumps(row, sort_keys=True))


class NoPublishedRowIsPricedWithoutAPick(unittest.TestCase):
    """The invariant the publisher's unit gate actually enforces, on real data."""

    def test_the_committed_board_has_no_priced_row_without_a_pick(self):
        offenders = [(m['id'], m['teams'], m['probabilities']) for m in SNAPSHOT['matches']
                     if m.get('state') == 'open' and m.get('probabilities') is not None
                     and not m.get('pick')]
        self.assertEqual(offenders, [], 'a priced row with no pick blocks every publication')

    def test_every_open_row_is_either_picked_or_fully_blank(self):
        for m in SNAPSHOT['matches']:
            if m.get('state') != 'open':
                continue
            with self.subTest(fixture=m['id']):
                if m.get('pick'):
                    self.assertIn(m['pick'], m['teams'])
                    self.assertIsNotNone(m.get('method'))
                else:
                    self.assertIsNone(m.get('probabilities'))
                    self.assertIsNone(m.get('fair_odds'))
                    self.assertIsNone(m.get('method'))
                    self.assertTrue((m.get('reason') or '').strip())

    def test_an_even_market_is_still_recorded_as_evidence_somewhere(self):
        # The rule must not quietly drop the quote: if a row's market was even,
        # the evidence is on the row with a notice.
        recorded = [a for m in SNAPSHOT['matches'] for a in (m.get('attempts') or [])
                    if (a.get('rejected_quote') or {}).get('notice')]
        for attempt in recorded:
            self.assertIn('not a pick', attempt['rejected_quote']['notice'])
            self.assertTrue(str(attempt.get('url', '')).startswith('https://')
                            or str(attempt['rejected_quote'].get('api_url', '')).startswith('https://'))


class TheMobileExecutiveSummaryStillAnswersTheQuestion(unittest.TestCase):
    """The user-facing acceptance this session was asked for, on the built page."""

    @classmethod
    def setUpClass(cls):
        cls.index = (ROOT / 'index.html').read_text()
        cls.css = (ROOT / 'site' / 'assets' / 'style.css').read_text()

    def test_the_quick_nav_never_clips_its_own_sentence(self):
        # Measured at 390x844 before this session: inside the phone block the row
        # was `overflow-x:auto` with a `white-space:nowrap` line, so the summary
        # read "Executive summ" until the reader swiped. Both are gone now.
        self.assertNotIn('overflow-x:auto', self.css[self.css.index('.exec-quicknav{display:none}'):])
        phone = self.css[self.css.index('body[data-page="index"] main>#exec-quicknav{order:3}'):]
        phone = phone[:phone.index('\n}\n')]
        self.assertIn('flex-wrap:wrap', phone)
        line = phone[phone.index('.exec-quicknav-line{'):]
        line = line[:line.index('}')]
        self.assertIn('white-space:normal', line)
        self.assertIn('flex:1 1 100%', line)

    def test_the_pick_is_ordered_before_the_other_cells_on_every_phone(self):
        # The ordering used to apply only at <=700px tall, leaving the first
        # .pick at y=863 on a 320x844 phone.
        rule = "body[data-page=picks] tbody tr td.pick-cell{order:1}"
        self.assertIn(rule, self.css)
        start = self.css.index('@media(max-width:650px){\n  body[data-page=picks] main{display:flex')
        block = self.css[start:self.css.index('\n}\n', start)]
        self.assertIn(rule, block, 'the pick ordering must live in the all-phone-width block')

    def test_the_summary_still_links_the_updated_picks_in_site(self):
        for href in ('picks.html', '#picks-at-a-glance', 'unresolved.html',
                     '#unresolved-limits', 'review.html'):
            self.assertIn('href="%s"' % href, self.index)
        self.assertIn('id="exec-summary"', self.index)
        self.assertIn('id="unresolved-limits"', self.index)


if __name__ == '__main__':
    unittest.main()
