"""Deterministic verification for session 85c33bf9's additive day-4 changes.

Covers: the verified Hacha alias (and the deliberate non-mapping of
Sökerorg/LFO 10), the wide-tier resolution path for row 1082019 with the
market fields as read at 10:32 UTC on 17 October 2026, the renewed
ex-6666/Privateer book receipt replayed on an explicit clock (fresh and
expired), the dated placeholder re-reads, and the additive analysis and
review-note content. No network access and no wall-clock dependence.
"""
import json
import unittest
from datetime import timedelta
from pathlib import Path

from scripts.core import (ALIAS_MAP, book_candidate, book_research_pick, dt, norm,
                          plain_name, quote_book, resolve)

ROOT = Path(__file__).resolve().parents[1]
IDENTITIES = json.loads((ROOT / 'data/identities.json').read_text())
RECEIPTS = json.loads((ROOT / 'data/book-receipts.json').read_text())
REVIEW = json.loads((ROOT / 'data/review-notes.json').read_text())
ANALYSIS = json.loads((ROOT / 'data/analysis.json').read_text())


def fixture_1082019():
    return {
        'id': '1082019', 'teams': ['Hacha', 'LOS NINOS'],
        'competition': 'CCT South America 2026 Series #7', 'tier': 'c',
        'best_of': None, 'start': '2026-10-17T22:00:00Z', 'lock': '2026-10-17T21:54:00Z',
        'state': 'open', 'probabilities': None, 'fair_odds': None, 'pick': None,
        'method': None, 'evidence': [], 'flags': [], 'attempts': [], 'reason': None,
    }


MARKET_5796276 = {
    'id': '5796276',
    'question': 'Counter-Strike: Hacha Esports vs Los Niños (BO3) - CCT South America Series 7 Group Stage',
    'sportsMarketType': 'moneyline',
    'outcomes': '["Hacha Esports", "Los Niños"]',
    'outcomePrices': '["0.395", "0.605"]',
    'gameStartTime': '2026-10-17 22:00:00+00',
    'eventStartTime': '2026-10-17T22:00:00Z',
    'updatedAt': '2026-10-17T10:31:16.112391Z',
    'active': True, 'closed': False, 'acceptingOrders': True,
    'bestBid': 0.19, 'bestAsk': 0.6,
    'liquidity': '128.9748', 'volume': '27.177528000000002',
}


def candidate_5796276():
    return {
        'provider': 'Polymarket', 'id': '5796276',
        'teams': ['Hacha Esports', 'Los Niños'],
        'start': '2026-10-17 22:00:00+00',
        'observed_at': '2026-10-17T10:32:00Z',
        'updated_at': MARKET_5796276['updatedAt'],
        'url': 'https://polymarket.com/event/cs2-hachae-ln-2026-10-17',
        'api_url': 'https://gamma-api.polymarket.com/markets/5796276',
        'raw': dict(MARKET_5796276),
        'prices': [0.395, 0.605],
        'market': dict(MARKET_5796276),
        'best_of': 3,
        'team_aliases': [['Hacha Esports', ''], ['Los Niños', '']],
        'team_metadata': [], 'event': None,
    }


class TestHachaAlias(unittest.TestCase):
    def test_register_entry_present_and_shaped(self):
        entry = next((a for a in IDENTITIES['aliases'] if a.get('canonical') == 'Hacha'), None)
        self.assertIsNotNone(entry, 'Hacha alias entry missing from data/identities.json')
        self.assertEqual(sorted(entry['names']), sorted(['Hacha', 'Hacha Esports']))
        self.assertIn('2399768', entry['source'])
        self.assertIn('5796276', entry['additional_source'])
        self.assertTrue(entry['basis'].strip())

    def test_alias_map_maps_suffix_not_guesses(self):
        self.assertEqual(norm('Hacha Esports'), norm('Hacha'))
        self.assertEqual(norm('Hacha Esports'), plain_name('Hacha'))

    def test_los_ninos_folds_without_register_entry(self):
        self.assertEqual(plain_name('Los Niños'), plain_name('LOS NINOS'))
        self.assertNotIn('losniños', ALIAS_MAP)  # folding handles it; no entry needed

    def test_sokerorg_is_deliberately_not_mapped(self):
        self.assertNotEqual(norm('Sökerorg'), norm('LFO 10'))
        self.assertFalse(any('Sökerorg' in n or 'sokerorg' in n.lower()
                             for a in IDENTITIES['aliases'] for n in a['names']))


class TestWideTierResolution(unittest.TestCase):
    def test_strict_resolve_rejects_41_point_spread(self):
        row = fixture_1082019()
        resolve(row, [candidate_5796276()], 'Polymarket',
                dt('2026-10-17T10:35:00Z'), relax=False)
        self.assertIsNone(row['probabilities'])
        self.assertEqual(row['attempts'][-1]['status'], 'unresolved')
        self.assertIn('spread', row['attempts'][-1]['reason'])

    def test_wide_tier_prices_row_with_low_confidence_label(self):
        row = fixture_1082019()
        resolve(row, [candidate_5796276()], 'Polymarket',
                dt('2026-10-17T10:35:00Z'), relax=True)
        self.assertEqual(row['method'], 'exchange_wide')
        self.assertAlmostEqual(row['probabilities'][0], 0.395, places=9)
        self.assertAlmostEqual(row['probabilities'][1], 0.605, places=9)
        self.assertEqual(row['pick'], 'LOS NINOS')
        self.assertTrue(any('Low confidence' in f for f in row['flags']))
        quote = row['evidence'][0]
        self.assertEqual(quote['tier'], 'wide_exchange')
        self.assertAlmostEqual(quote['spread'], 0.41, places=9)
        self.assertAlmostEqual(quote['liquidity'], 128.9748, places=4)
        self.assertIn('strict_rejection', quote)
        self.assertTrue(any(i.get('canonical') == 'Hacha' for i in quote['identity_sources']))

    def test_quote_rejected_when_market_closed(self):
        row = fixture_1082019()
        cand = candidate_5796276()
        cand['market']['closed'] = True
        resolve(row, [cand], 'Polymarket', dt('2026-10-17T10:35:00Z'), relax=True)
        self.assertIsNone(row['probabilities'])

    def test_quote_rejected_below_liquidity_floor(self):
        row = fixture_1082019()
        cand = candidate_5796276()
        cand['market']['liquidity'] = '99.99'
        resolve(row, [cand], 'Polymarket', dt('2026-10-17T10:35:00Z'), relax=True)
        self.assertIsNone(row['probabilities'])


class TestEx6666Receipt(unittest.TestCase):
    def receipt(self):
        r = next((x for x in RECEIPTS['receipts']
                  if x.get('id') == 'egw-rW6Ymkl0D-ex-6666-privateer-1010z'), None)
        self.assertIsNotNone(r, 'renewed ex-6666 receipt missing')
        return r

    def test_schema_and_arithmetic(self):
        r = self.receipt()
        self.assertEqual(r['fixture_id'], '1081521')
        self.assertEqual(r['odds'], [1.13, 4.75])
        self.assertNotEqual(r['odds'][0], r['odds'][1])
        self.assertTrue(dt(r['observed_at']) < dt(r['start']))
        q = [1 / x for x in r['odds']]
        margin = sum(q) - 1
        self.assertAlmostEqual(margin, 0.0954822, places=5)
        p = [x / sum(q) for x in q]
        self.assertAlmostEqual(p[0], 0.8078, places=3)
        self.assertAlmostEqual(p[1], 0.1922, places=3)

    def row(self):
        return {'id': '1081521', 'teams': ['ex-6666', 'Privateer'],
                'start': '2026-10-18T13:45:00Z', 'state': 'open',
                'probabilities': None, 'flags': [], 'attempts': [],
                'best_of': None, 'pick': None, 'evidence': None}

    def test_book_research_pick_on_explicit_clock(self):
        row = self.row()
        book_research_pick(row, receipts=[self.receipt()], now=dt('2026-10-17T11:00:00Z'))
        self.assertEqual(row['method'], 'bookmaker_fallback')
        self.assertEqual(row['pick'], 'ex-6666')
        self.assertAlmostEqual(row['probabilities'][0], 0.8078, places=3)
        self.assertAlmostEqual(row['probabilities'][1], 0.1922, places=3)

    def test_receipt_expires_eight_hours_after_observation(self):
        row = self.row()
        book_research_pick(row, receipts=[self.receipt()],
                           now=dt('2026-10-17T10:10:00Z') + timedelta(hours=8, minutes=1))
        self.assertIsNone(row['probabilities'])
        self.assertTrue(any(a['status'] == 'unresolved' and 'stale' in a['reason']
                            for a in row['attempts']))

    def test_old_receipt_left_untouched_and_still_dated(self):
        old = next((x for x in RECEIPTS['receipts']
                    if x.get('id') == 'egw-rW6Ymkl0D-ex-6666-privateer'), None)
        self.assertIsNotNone(old)
        self.assertEqual(old['odds'], [1.15, 4.5])
        self.assertEqual(old['observed_at'], '2026-10-17T00:45:00Z')

    def test_rejected_rereads_recorded(self):
        have = {(r.get('fixture_id'), r.get('observed_at')) for r in RECEIPTS['rejected_listings']}
        for fid, obs in [('1079634', '2026-10-17T10:06:00Z'), ('1081522', '2026-10-17T10:11:00Z'),
                         ('1081861', '2026-10-17T10:11:00Z'), ('1081863', '2026-10-17T10:13:00Z'),
                         ('1081511', '2026-10-17T10:13:00Z')]:
            self.assertIn((fid, obs), have)


class TestReviewAndAnalysisContent(unittest.TestCase):
    def test_review_notes_added(self):
        ids = {n['id'] for n in REVIEW}
        for wanted in ('hacha-alias-verified-85c33bf9', 'hacha-market-thin-85c33bf9',
                       'lfo10-sokerorg-unverified-85c33bf9'):
            self.assertIn(wanted, ids)
        for n in REVIEW:
            if n['id'].endswith('85c33bf9'):
                self.assertTrue(n['finding'].strip())
                self.assertTrue(n['sources'])
                for s in n['sources']:
                    self.assertTrue(s['url'].startswith('https://'))

    def test_analysis_points_added(self):
        claims = ' '.join(p['claim'] for p in ANALYSIS['day_four_guidance']['points'])
        self.assertIn('72.5/27.5', claims)
        self.assertIn('Hacha vs LOS NINOS', claims)
        self.assertIn('settled correct', claims)
        for p in ANALYSIS['day_four_guidance']['points']:
            self.assertTrue(p['claim'] and p['detail'] and p['source'].startswith('https://'))

    def test_analysis_unpriced_reread_added(self):
        labels = [u['label'] for u in ANALYSIS['day_four_guidance']['unpriced']]
        self.assertTrue(any('10:05-10:55 UTC' in l for l in labels))
        entry = next(u for u in ANALYSIS['day_four_guidance']['unpriced'] if '10:05-10:55 UTC' in u['label'])
        self.assertTrue(entry['limitation'].strip())
        self.assertTrue(entry['sources'])

    def test_analysis_unverified_added(self):
        joined = ' '.join(ANALYSIS['day_four_guidance']['unverified'])
        self.assertIn('Sökerorg', joined)
        self.assertIn('fixture-parity identity evidence', joined)
        self.assertIn('thin and volatile', joined)

    def test_no_percentage_invented_for_research_rows(self):
        # The four research-only rows must not gain probabilities anywhere in analysis text.
        text = json.dumps(ANALYSIS['day_four_guidance'])
        self.assertNotIn('research-only pick (Lavked, HLTV world #140) with probability', text)


if __name__ == '__main__':
    unittest.main()
