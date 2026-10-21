"""Session a980a709 regression: the last unresolved open fixture gets a sourced line.

The 2026-10-21T12:43Z published snapshot left exactly one open fixture without
a pick (1082762 ex-CYBERSHOKE vs BlinkDagger). These tests pin the retained
capture to the row it was read for, replay the de-vig arithmetic and prove the
receipt cannot price a different fixture.
"""
from __future__ import annotations

import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.core import (book_candidate, book_receipts, book_research_pick, iso, quote_book,
                          normalize_fixtures)

ROOT = Path(__file__).resolve().parents[1]
NOTES = json.loads((ROOT / 'data/review-notes.json').read_text())
RECEIPT_ID = 'stavka-cybershoke-blinkdagger-1082762'
NOW = datetime(2026, 10, 21, 12, 50, tzinfo=timezone.utc)


def fixture_for(team_a: str, team_b: str, fixture_id: str = '1082762') -> dict:
    start = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    raw = {'id': fixture_id, 'sport_alias': 'cs2', 'participants0_name': team_a,
           'participants1_name': team_b, 'participants0_id': 'a', 'participants1_id': 'b',
           'status': 'scheduled', 'scheduled_start_time': iso(start),
           'lock_time': iso(start - timedelta(minutes=6)),
           'competition_name': 'CIS LAN Championship #9', 'tier': 'c', 'best_of': 3}
    row = normalize_fixtures([raw], {}, NOW)[0]
    row.update(probabilities=None, fair_odds=None, pick=None, method=None, evidence=[],
               flags=[], attempts=[], reason=None)
    return row


class LastUnresolvedFixtureTests(unittest.TestCase):
    def test_receipt_is_callable_and_asymmetric(self):
        receipt = next(r for r in book_receipts() if r['id'] == RECEIPT_ID)
        self.assertEqual(receipt['fixture_id'], '1082762')
        self.assertEqual(receipt['source_teams'], ['ex-CYBERSHOKE', 'BlinkDagger'])
        self.assertEqual(receipt['start'], '2026-10-21T15:00:00Z')
        self.assertNotEqual(receipt['odds'][0], receipt['odds'][1])
        self.assertEqual(receipt['odds'], [1.14, 7.5])
        self.assertIn('Winline', receipt['provider'])
        self.assertIn('BetBoom', receipt['provider'])
        # Every claim in the published limitation is stated, not implied.
        self.assertIn('Cross-operator price panel', receipt['limitation'])
        self.assertTrue(all(item['url'].startswith('https://') for item in receipt['identity_evidence']))

    def test_de_vig_matches_the_project_formula(self):
        receipt = next(r for r in book_receipts() if r['id'] == RECEIPT_ID)
        quote = quote_book(book_candidate(receipt), [0, 1], NOW)
        self.assertAlmostEqual(quote['probabilities'][0], 0.868056, places=6)
        self.assertAlmostEqual(quote['probabilities'][1], 0.131944, places=6)
        self.assertAlmostEqual(quote['overround'], 0.010526, places=6)

    def test_row_now_gets_a_priced_pick(self):
        row = fixture_for('ex-CYBERSHOKE', 'BlinkDagger')
        book_research_pick(row, [next(r for r in book_receipts() if r['id'] == RECEIPT_ID)], now=NOW)
        self.assertEqual(row['pick'], 'ex-CYBERSHOKE')
        self.assertEqual(row['method'], 'bookmaker_fallback')
        self.assertAlmostEqual(row['probabilities'][0], 0.868056, places=6)
        self.assertAlmostEqual(row['fair_odds'][0], 1 / 0.868056, places=5)

    def test_receipt_cannot_price_a_different_pair_or_id(self):
        other = fixture_for('BlinkDagger', 'UPGRADE', fixture_id='1082763')
        book_research_pick(other, [next(r for r in book_receipts() if r['id'] == RECEIPT_ID)], now=NOW)
        self.assertIsNone(other['pick'])
        self.assertIsNone(other['probabilities'])

    def test_observation_expires_after_eight_hours(self):
        receipt = next(r for r in book_receipts() if r['id'] == RECEIPT_ID)
        with self.assertRaises(ValueError):
            quote_book(book_candidate(receipt), [0, 1], NOW + timedelta(hours=9))


class FlaggedForReviewTests(unittest.TestCase):
    def test_composite_basis_is_published(self):
        note = next(n for n in NOTES if n['id'] == 'a980a709-cybershoke-blinkdagger-composite')
        self.assertIn('1.8/1.8 placeholder', note['finding'])
        self.assertIn('$100', note['finding'])
        self.assertIn('ex-CYBERSHOKE', note['finding'])
        urls = {s['url'] for s in note['sources']}
        self.assertIn('https://stavka.tv/matches/csgo/21-10-2026-cybershoke-esports-blinkdagger', urls)
        self.assertIn('https://www.hltv.org/matches/2399839/match', urls)
        self.assertTrue(all(u.startswith('https://') for u in urls))

    def test_rejections_are_recorded_with_reasons(self):
        doc = json.loads((ROOT / 'data/book-receipts.json').read_text())
        rejected = [r for r in doc['rejected_listings'] if str(r.get('fixture_id')) == '1082762']
        urls = {r['url'] for r in rejected}
        self.assertIn('https://egamersworld.com/counterstrike/match/4yp_dlKtNl/ex-cybershoke-vs-blinkdagger-5sOoK5oHU4', urls)
        self.assertIn('https://polymarket.com/esports/cs2', urls)
        for row in rejected:
            self.assertTrue(row['reason'])
            self.assertTrue(row['observed_at'].endswith('Z'))


if __name__ == '__main__':
    unittest.main()
