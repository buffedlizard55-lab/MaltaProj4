"""Session d6df5beb: deterministic verification of the TWC 2026 record and the Day-5 prices.

No network access. Every assertion replays a dated receipt or checks a committed
data file, so a stale or invented number cannot pass by being re-typed.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.audit_d6df5beb import (
    Audit,
    audit_fixtures,
    audit_published_data,
    audit_receipt,
    audit_rendered,
    devig_american,
)

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = ROOT / 'research' / 'session-d6df5beb' / 'receipt-2026-10-18.json'


class ReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(RECEIPT_PATH.read_text())
        cls.analysis = json.loads((ROOT / 'data' / 'analysis.json').read_text())
        cls.latest = json.loads((ROOT / 'data' / 'latest.json').read_text())

    # -- structure ---------------------------------------------------------- #
    def test_receipt_covers_the_whole_event(self):
        series = self.receipt['series']
        self.assertEqual(len(series), 12)
        days = {}
        for s in series:
            days[s['day']] = days.get(s['day'], 0) + 1
        self.assertEqual(days, {1: 4, 2: 4, 3: 2, 4: 2})
        self.assertEqual(len(self.receipt['fixtures']), 2)
        self.assertEqual(
            sorted(f['start_utc'] for f in self.receipt['fixtures']),
            ['2026-10-18T11:30:00Z', '2026-10-18T15:00:00Z'],
        )

    def test_series_internal_consistency(self):
        audit = Audit()
        summary = audit_receipt(self.receipt, audit)
        self.assertEqual(audit.failures, [])
        self.assertEqual(summary['maps'], 29)

    def test_each_series_has_a_primary_source(self):
        for s in self.receipt['series']:
            self.assertTrue(s['match_url'].startswith('https://www.hltv.org/matches/'), s['match_url'])

    # -- arithmetic --------------------------------------------------------- #
    def test_devig_known_values(self):
        third = devig_american({'Aurora': 140, 'Falcons': -200})
        self.assertAlmostEqual(third['probabilities']['Falcons'], 0.6153846, places=6)
        self.assertAlmostEqual(third['probabilities']['Aurora'], 0.3846154, places=6)
        self.assertAlmostEqual(third['overround'], 1.0833333, places=6)
        final = devig_american({'FURIA': -286, 'BETBOOM': 190})
        self.assertAlmostEqual(final['probabilities']['FURIA'], 0.682409, places=6)
        self.assertAlmostEqual(final['overround'], 1.085760, places=6)

    def test_venue_gate_and_agreement(self):
        audit = Audit()
        out = audit_fixtures(self.receipt, audit)
        self.assertEqual(audit.failures, [])
        third = out['Aurora-Falcons']
        self.assertEqual(third['pick'], 'Falcons')
        self.assertLessEqual(max(third['gap_points'].values()), 5.0)
        self.assertAlmostEqual(third['polymarket']['Falcons'], 0.605, places=6)
        final = out['FURIA-BETBOOM']
        self.assertEqual(final['pick'], 'FURIA')
        self.assertAlmostEqual(final['polymarket']['FURIA'], 0.705, places=6)
        self.assertLessEqual(max(final['gap_points'].values()), 5.0)

    def test_polymarket_quotes_clear_the_production_gate(self):
        for fx in self.receipt['fixtures']:
            quote = next(v for v in fx['venue_quotes'] if v['venue'] == 'Polymarket')
            self.assertAlmostEqual(sum(quote['prices'].values()), 1.0, places=6)
            self.assertLessEqual(quote['spread'], 0.25)
            self.assertGreaterEqual(quote['liquidity_usd'], 100)
            self.assertFalse(quote['closed'])
            self.assertTrue(quote['accepting_orders'])
            self.assertEqual(quote['game_start_time_utc'], fx['start_utc'])

    # -- published data ----------------------------------------------------- #
    def test_every_published_result_matches_the_receipt(self):
        audit = Audit()
        summary = audit_published_data(self.receipt, audit)
        self.assertEqual(audit.failures, [])
        self.assertEqual(summary['published_series'], 12)

    def test_every_open_row_has_a_pick_and_a_reason_when_unpriced(self):
        rows = [m for m in self.latest['matches'] if m.get('state') == 'open']
        self.assertTrue(rows)
        for row in rows:
            with self.subTest(row=row['id']):
                self.assertIn(row.get('pick'), row.get('teams') or [])
                self.assertTrue(row.get('reason') or row.get('probabilities'))
                if row.get('probabilities'):
                    self.assertAlmostEqual(sum(row['probabilities']), 1.0, places=6)
                    self.assertIn(row.get('method'),
                                  {'exchange', 'exchange_wide', 'bookmaker_fallback', 'model_vrs'})
                else:
                    # All supported qualitative tiers, never a probability:
                    # two HLTV ranks, one HLTV rank, or one uniquely resolved
                    # Valve listing. A newly refreshed snapshot may use any of
                    # these; this assertion is not pinned to one day's methods.
                    self.assertIn(row.get('method'),
                                  {'research_rank', 'research_rank_single', 'research_vrs_single'})

    def test_day_five_cards_exist_for_both_fixtures(self):
        cards = {tuple(c.get('teams') or []): c
                 for c in self.analysis['day_five_guidance']['not_listed']}
        for fx in self.receipt['fixtures']:
            key = (fx['team_a'], fx['team_b'])
            card = cards.get(key) or cards.get((fx['team_b'], fx['team_a']))
            with self.subTest(fixture=key):
                self.assertIsNotNone(card)
                self.assertIn(card['pick'], key)
                self.assertEqual(card['start_utc'], fx['start_utc'])
                observed = card['market']['observed_at']
                self.assertTrue(observed.startswith('2026-10-'))
                self.assertTrue(card['market']['url'].startswith('https://gamma-api.polymarket.com/'))
                self.assertTrue(card['market']['receipt_url'].endswith('receipt-2026-10-18.json'))
                self.assertIn('cross-check', card['book_line']['label'])

    def test_main_twc_event_is_research_only_unless_priced(self):
        mains = [m for m in self.latest['matches']
                 if m.get('competition') == 'Thunderpick World Championship 2026']
        if not mains:
            verdict = self.receipt['verified_claims']['hotspawn_inventory']['verdict']
            # The claim under test is that the earlier lobby read carried no
            # main-event row; the receipt now states it as a dated sequence
            # ("... and no main-event row. By 00:52 UTC ...") instead of the
            # earlier "Not listed" phrasing.
            self.assertIn('no main-event row', verdict)
        else:
            for row in mains:
                self.assertIn(row.get('pick'), row.get('teams') or [])

    def test_rendered_pages_carry_the_day_five_anchor(self):
        audit = Audit()
        rendered = audit_rendered(audit)
        self.assertEqual(audit.failures, [])
        self.assertTrue(all(rendered.values()))


if __name__ == '__main__':
    unittest.main()
