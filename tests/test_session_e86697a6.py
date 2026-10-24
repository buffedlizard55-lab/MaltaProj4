"""Session e86697a6 — the published board must answer every open match, and it
must never call a *withheld* pick an *unresolved* one.

Two live observations from 2026-10-24 drive these tests:

* Fixture 1079200 (Color vs ex-Zero Tenacity, NODWIN Clutch Series #13, BO3,
  2026-10-25T18:00Z) was priced by Polymarket at exactly 0.500 / 0.500
  (bid 0.49 / ask 0.51, liquidity $5,989.80, updated 16:24:39Z). Publishing that
  as a 50/50 probability with ``pick: null`` left the match with no answer and
  broke every downstream contract that requires a pick to be the larger number.
  The even quote must therefore be kept as rejected evidence and the ladder must
  continue to Valve's own standings, which do carry a direction
  (Color 1249 pts #57 vs ex-Zero Tenacity 1066 pts #93, standings 2026-10-05).
* While the committed snapshot sat outside its eight-hour window the site said
  "22 open CS2 match(es) · 0 with a pick · 22 unresolved" although all 22 rows
  held a sourced pick. Withheld is not unresolved and must be counted apart.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts import core, summary, vrs

ROOT = Path(__file__).resolve().parent.parent
OBSERVED = core.dt('2026-10-24T16:40:00Z')

FIXTURE = {
    'id': '1079200', 'sport_alias': 'cs2',
    'participants0_name': 'Color', 'participants1_name': 'ex-Zero Tenacity',
    'status': 'scheduled', 'best_of': 3,
    'scheduled_start_time': '2026-10-25T18:00:00Z',
    'lock_time': '2026-10-25T17:54:00Z',
}


def even_market():
    """The exact live Polymarket market, replayed through the real candidate builder."""
    market = {
        'id': '6072812',
        'question': 'Counter-Strike: Color vs ex-Zero Tenacity (BO3) - NODWIN Clutch Series Playoffs',
        'sportsMarketType': 'moneyline',
        'outcomes': '["Color", "ex-Zero Tenacity"]',
        'outcomePrices': '["0.5", "0.5"]',
        'gameStartTime': '2026-10-25 18:00:00+00',
        'updatedAt': '2026-10-24T16:24:39.312073Z',
        'active': True, 'closed': False, 'acceptingOrders': True,
        'bestBid': 0.49, 'bestAsk': 0.51, 'liquidity': '5989.7983', 'volume': None,
    }
    event = {'id': '1238707', 'slug': 'cs2-color-zerote-2026-10-25',
             'sport': {'id': 37, 'sport': 'cs2', 'name': 'CS2'},
             'closed': False, 'live': None, 'ended': None,
             'teams': [{'name': 'Color', 'abbreviation': 'color'},
                       {'name': 'ex-Zero Tenacity', 'abbreviation': 'zerote'}],
             'markets': [market]}
    candidates = core.polymarket_candidates([event], '2026-10-24T16:25:17.936350Z')
    assert len(candidates) == 1, 'the captured market must build exactly one candidate'
    return candidates[0]


class EvenLineIsEvidenceNotAPick(unittest.TestCase):
    def setUp(self):
        self.fixture = core.normalize_fixtures([FIXTURE], {}, OBSERVED)[0]

    def test_an_exactly_even_quote_publishes_no_probability_and_no_pick(self):
        core.resolve(self.fixture, [even_market()], 'Polymarket', OBSERVED)
        self.assertIsNone(self.fixture['probabilities'],
                          'an even two-way line is not a directional probability')
        self.assertIsNone(self.fixture['pick'])
        self.assertIsNone(self.fixture['method'])

    def test_the_even_quote_is_kept_as_rejected_evidence(self):
        core.resolve(self.fixture, [even_market()], 'Polymarket', OBSERVED)
        attempt = self.fixture['attempts'][-1]
        self.assertEqual(attempt['status'], 'unresolved')
        rejected = attempt['rejected_quote']
        self.assertEqual(rejected['provider'], 'Polymarket')
        self.assertEqual(rejected['raw']['bestBid'], 0.49)  # bid/ask in the capture's own raw block
        self.assertEqual(rejected['raw']['bestAsk'], 0.51)
        self.assertEqual(rejected['observed_at'], '2026-10-24T16:25:17.936350Z')
        self.assertEqual(rejected['api_url'], 'https://gamma-api.polymarket.com/markets/6072812')
        self.assertIn('Rejected evidence', rejected['notice'])
        self.assertIn('exactly even', attempt['reason'])

    def test_the_ladder_then_resolves_the_match_from_valve_standings(self):
        core.resolve(self.fixture, [even_market()], 'Polymarket', OBSERVED)
        standings, meta = vrs.vendored(OBSERVED)
        vrs.apply(self.fixture, standings, meta, None)
        probabilities = self.fixture['probabilities']
        self.assertIsNotNone(probabilities, 'the model tier must answer the row the market could not')
        self.assertAlmostEqual(probabilities[0], 0.6883951727580038, places=12)
        self.assertAlmostEqual(sum(probabilities), 1.0, places=12)
        self.assertEqual(self.fixture['pick'], 'Color')
        self.assertEqual(self.fixture['method'], 'model_vrs')
        self.assertEqual(self.fixture['evidence'][0]['provider'], 'Valve VRS model')
        self.assertEqual(self.fixture['attempts'][-1]['status'], 'resolved')

    def test_the_standings_points_behind_that_line_are_the_official_ones(self):
        standings, _ = vrs.vendored(OBSERVED)
        color, color_note = vrs.identify('Color', standings)
        zt, zt_note = vrs.identify('ex-Zero Tenacity', standings)
        self.assertIsNotNone(color, color_note)
        self.assertIsNotNone(zt, zt_note)
        self.assertEqual(color['points'], 1249)
        self.assertEqual(zt['points'], 1066)
        self.assertEqual(standings['as_of'], '2026-10-05')


class WithheldIsNotUnresolved(unittest.TestCase):
    def test_counts_separate_a_withheld_pick_from_a_missing_one(self):
        matches = [
            {'id': 'a', 'state': 'open', 'probabilities': [0.6, 0.4], 'pick': 'A', 'method': 'exchange'},
            {'id': 'b', 'state': 'open', 'probabilities': None, 'fair_odds': None, 'pick': None,
             'method': None, 'reason': 'evidence deadline passed',
             'withheld': {'kind': 'snapshot_stale', 'had': {'pick': 'B'}, 'reason': 'stale snapshot'}},
            {'id': 'c', 'state': 'open', 'probabilities': None, 'fair_odds': None, 'pick': None,
             'method': None, 'reason': 'no two-way line anywhere'},
        ]
        c = summary.counts(matches)
        self.assertEqual(c['open'], 3)
        self.assertEqual(c['withheld'], 1)
        self.assertEqual(c['no_pick'], 1, 'the withheld row must not be counted as unresolved')
        self.assertEqual([m['id'] for m in c['withheld_rows']], ['b'])
        self.assertEqual([m['id'] for m in c['blank_rows']], ['c'])
        self.assertEqual(c['without_percentage'], 2)
        sentence = summary.completeness_sentence(c)
        self.assertIn('withheld pending a refresh', sentence)
        self.assertIn('1 open match(es) genuinely have no supported pick', sentence)

    def test_a_board_of_only_withheld_rows_is_not_reported_as_unresolved(self):
        matches = [{'id': str(i), 'state': 'open', 'probabilities': None, 'fair_odds': None,
                    'pick': None, 'method': None, 'reason': 'stale',
                    'withheld': {'kind': 'snapshot_stale', 'had': {'pick': 'X'}, 'reason': 'stale'}}
                   for i in range(22)]
        c = summary.counts(matches)
        self.assertEqual((c['withheld'], c['no_pick']), (22, 0))
        self.assertIn('No open match is unresolved', summary.completeness_sentence(c))


class ReviewNotesStayIndentOne(unittest.TestCase):
    """The published Flagged-for-Review page is generated from this register."""

    def test_register_is_indent_one_and_every_entry_links_sources(self):
        path = ROOT / 'data/review-notes.json'
        raw = path.read_text()
        self.assertEqual(json.dumps(json.loads(raw), indent=1, ensure_ascii=False) + '\n', raw)
        notes = json.loads(raw)
        for note in notes:
            self.assertTrue(note['id'] and note['status'] and note['finding'])
            self.assertTrue(note['sources'], note['id'])
            for source in note['sources']:
                self.assertTrue(source['url'].startswith('https://'), note['id'])


if __name__ == '__main__':
    unittest.main()
