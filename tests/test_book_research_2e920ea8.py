"""Researched-book listing tier (session 2e920ea8, 2026-10-16).

Covers the user requirement that a pick (and, where a real two-sided listing
exists, a percentage) can be published for fixtures the automated exchange and
Pinnacle tiers cannot price. Every probability still comes from de-vigging a
dated two-way decimal book line; nothing here writes a probability by hand,
and a listing placeholder (identical default odds) is never converted into a
50/50.
"""
import copy
import importlib.util
import json
import math
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.core import (
    ALIAS_MAP, BOOK_RECEIPTS, book_candidate, book_receipts, book_research_pick,
    calculator_for, dt, iso, norm, normalize_fixtures, plain_name, quote_book,
    research_rank_pick,
)
from scripts.validate import reconstruct_quote, validate_data

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now(timezone.utc).replace(microsecond=0)
START = NOW + timedelta(hours=5)


def load_auditor():
    spec = importlib.util.spec_from_file_location('audit_snapshot', ROOT / 'verification-c6/audit_snapshot.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def receipt(**over):
    base = {
        'provider': 'EGamersWorld book listing',
        'id': 'egw-test-infinite-insiders',
        'fixture_id': 'R1',
        'source_teams': ['Infinite Gaming', 'Insiders Esport'],
        'team_aliases': [['Infinite Gaming', 'Infinite', 'INFINITE'], ['Insiders Esport', 'Insiders']],
        'alias_sources': ['https://www.hltv.org/matches/2399590/x', 'https://www.hltv.org/matches/2399590/x'],
        'start': iso(START),
        'best_of': 1,
        'odds': [1.39, 2.65],
        'observed_at': iso(NOW),
        'url': 'https://egamersworld.com/counterstrike/match/test',
        'api_url': 'https://egamersworld.com/counterstrike/match/test',
        'event': 'Digital Crusade DraculaN Season 7',
    }
    base.update(over)
    return base


def snapshot(receipts, team_a='Infinite', team_b='Insiders', start=None):
    raw = {'id': 'R1', 'sport_alias': 'cs2', 'participants0_name': team_a, 'participants1_name': team_b,
           'participants0_id': 'a', 'participants1_id': 'b', 'status': 'scheduled',
           'scheduled_start_time': iso(start or START), 'lock_time': iso((start or START) - timedelta(minutes=6)),
           'competition_name': 'DraculaN Season 7', 'tier': 'b'}
    row = normalize_fixtures([raw], {}, NOW)[0]
    row.update(probabilities=None, fair_odds=None, pick=None, method=None, evidence=[], flags=[], attempts=[], reason=None)
    row['hltv_context'] = {'teams': [team_a, team_b], 'start': iso(start or START), 'ranks': [], 'lineups': [],
                           'source': 'https://www.hltv.org/matches/2399590/infinite-vs-insiders-digital-crusade-draculan-season-7',
                           'observed_at': iso(NOW), 'numeric_quote_rows': 0, 'limitation': 'context only'}
    book_research_pick(row, receipts=receipts)
    return {'schema_version': 2, 'generated_at': iso(NOW), 'last_attempt_at': iso(NOW),
            'fixtures_observed_at': iso(NOW), 'coverage': 'verified', 'matches': [row],
            'fixture_evidence': [raw], 'issues': [], 'source_checks': []}


class DiacriticFoldingTests(unittest.TestCase):
    def test_los_ninos_spellings_share_one_key(self):
        self.assertEqual(plain_name('Los Niños'), plain_name('LOS NINOS'))
        self.assertEqual(plain_name('Los Niños'), 'losninos')

    def test_plain_names_without_accents_are_unchanged(self):
        self.assertEqual(plain_name('ZywOo'), 'zywoo')
        self.assertEqual(plain_name('ex-6666'), 'ex6666')
        self.assertEqual(norm('Los Niños'), norm('LOS NINOS'))

    def test_alias_register_keys_are_folded_consistently(self):
        for key in ALIAS_MAP:
            self.assertEqual(key, plain_name(key))


class ReceiptFileTests(unittest.TestCase):
    def test_published_receipts_all_parse_as_candidates(self):
        receipts = book_receipts()
        self.assertGreaterEqual(len(receipts), 1)
        for item in receipts:
            candidate = book_candidate(item)
            self.assertEqual(candidate['fixture_id'], str(item['fixture_id']))
            self.assertEqual(len(candidate['odds']), 2)

    def test_loader_ignores_rejected_listings(self):
        doc = json.loads(BOOK_RECEIPTS.read_text())
        self.assertTrue(doc.get('rejected_listings'))
        loaded = book_receipts()
        self.assertFalse(any(r.get('displayed') for r in loaded))
        self.assertEqual(len(loaded), len(doc['receipts']))

    def test_missing_file_means_no_receipts(self):
        self.assertEqual(book_receipts(path=ROOT / 'data/does-not-exist.json'), [])

    def test_malformed_receipt_is_rejected(self):
        broken = receipt()
        del broken['odds']
        with self.assertRaises(ValueError):
            book_candidate(broken)
        with self.assertRaises(ValueError):
            book_candidate(receipt(odds=[1.5]))
        with self.assertRaises(ValueError):
            book_candidate(receipt(team_aliases=[['x']]))


class QuoteBookMathTests(unittest.TestCase):
    def test_devig_is_exact_and_reproducible(self):
        candidate = book_candidate(receipt())
        quote = quote_book(candidate, [0, 1], NOW)
        implied = [1 / 1.39, 1 / 2.65]
        total = sum(implied)
        expected = [implied[0] / total, implied[1] / total]
        for got, want in zip(quote['probabilities'], expected):
            self.assertAlmostEqual(got, want, places=12)
        self.assertAlmostEqual(sum(quote['probabilities']), 1.0, places=12)
        self.assertAlmostEqual(quote['overround'], total - 1, places=12)
        self.assertEqual(quote['updated_at'], None)
        self.assertIn('no price-update timestamp', quote['warning'])

    def test_stale_listing_is_refused(self):
        stale = receipt(observed_at=iso(NOW - timedelta(hours=9)))
        with self.assertRaises(ValueError):
            quote_book(book_candidate(stale), [0, 1], NOW)

    def test_observation_after_start_is_refused(self):
        late = receipt(observed_at=iso(START + timedelta(minutes=1)))
        with self.assertRaises(ValueError):
            quote_book(book_candidate(late), [0, 1], NOW)

    def test_absurd_margin_is_refused(self):
        wide = receipt(odds=[1.01, 1.01])
        with self.assertRaises(ValueError):
            quote_book(book_candidate(wide), [0, 1], NOW)

    def test_equal_odds_are_a_legitimate_coin_flip_not_a_default(self):
        # 1.90/1.90 is a real two-way line with margin, not a placeholder.
        quote = quote_book(book_candidate(receipt(odds=[1.9, 1.9])), [0, 1], NOW)
        self.assertAlmostEqual(quote['probabilities'][0], 0.5, places=12)


class BookResearchPickTests(unittest.TestCase):
    def test_listed_line_prices_the_row_with_the_bookmaker_tier(self):
        data = snapshot([receipt()])
        row = data['matches'][0]
        self.assertEqual(row['method'], 'bookmaker_fallback')
        self.assertEqual(row['pick'], 'Infinite')
        self.assertEqual(len(row['evidence']), 1)
        self.assertAlmostEqual(row['probabilities'][0], (1 / 1.39) / (1 / 1.39 + 1 / 2.65), places=12)
        self.assertAlmostEqual(row['fair_odds'][0], 1 / row['probabilities'][0], places=12)
        self.assertTrue(any('researched listing' in f for f in row['flags']))
        self.assertEqual(row['reason'], None)

    def test_alias_bridge_maps_listed_labels_to_fixture_labels(self):
        data = snapshot([receipt()])
        row = data['matches'][0]
        self.assertEqual(row['evidence'][0]['source_teams'], ['Infinite Gaming', 'Insiders Esport'])
        self.assertEqual(row['evidence'][0]['team_aliases'][0][1], 'Infinite')

    def test_reversed_listing_order_stays_oriented(self):
        flipped = receipt(source_teams=['Insiders Esport', 'Infinite Gaming'],
                          team_aliases=[['Insiders Esport', 'Insiders'], ['Infinite Gaming', 'Infinite', 'INFINITE']],
                          alias_sources=[receipt()['alias_sources'][1], receipt()['alias_sources'][0]],
                          odds=[2.65, 1.39])
        data = snapshot([flipped])
        row = data['matches'][0]
        self.assertEqual(row['pick'], 'Infinite')
        self.assertAlmostEqual(row['probabilities'][0], (1 / 1.39) / (1 / 1.39 + 1 / 2.65), places=12)

    def test_receipt_for_another_fixture_id_is_ignored(self):
        data = snapshot([receipt(fixture_id='999999')])
        row = data['matches'][0]
        self.assertIsNone(row['pick'])
        self.assertIsNone(row['probabilities'])
        self.assertFalse(row['evidence'])

    def test_receipt_with_wrong_start_is_refused_with_an_attempt(self):
        data = snapshot([receipt(start=iso(START + timedelta(hours=1)))])
        row = data['matches'][0]
        self.assertIsNone(row['pick'])
        self.assertTrue(any(a['status'] == 'unresolved' and 'exact opponent pair' in a['reason'] for a in row['attempts']))

    def test_stale_receipt_falls_through_without_a_pick(self):
        data = snapshot([receipt(observed_at=iso(NOW - timedelta(hours=10)))])
        row = data['matches'][0]
        self.assertIsNone(row['pick'])
        self.assertTrue(any('stale' in a['reason'].lower() for a in row['attempts']))

    def test_research_rank_still_picks_when_no_receipt_matches(self):
        data = snapshot([], team_a='Procyon', team_b='LOS NINOS')
        row = data['matches'][0]
        row['hltv_context']['ranks'] = [
            {'team': 'Procyon', 'hltv_rank': 119, 'source': 'https://www.hltv.org/ranking/teams/2026/october/12/1'},
            {'team': 'LOS NINOS', 'hltv_rank': None, 'source': None, 'hltv_unranked': True},
        ]
        research_rank_pick(row)
        self.assertEqual((row['pick'], row['method']), ('Procyon', 'research_rank_single'))
        self.assertIsNone(row['probabilities'])


class ValidatorReplayTests(unittest.TestCase):
    def test_quote_replays_through_validate_helpers(self):
        data = snapshot([receipt()])
        row = data['matches'][0]
        q = row['evidence'][0]
        candidate = reconstruct_quote(q, data.get('schema_version', 1))
        self.assertEqual(candidate['odds'], [1.39, 2.65])
        order = [0, 1]
        replay = calculator_for(q['provider'])(candidate, order, NOW)
        for got, want in zip(replay['probabilities'], q['probabilities']):
            self.assertAlmostEqual(got, want, places=12)
        self.assertEqual(replay['decimal_odds'], q['decimal_odds'])
        self.assertEqual(replay['overround'], q['overround'])

    def test_validate_data_accepts_the_priced_row(self):
        data = snapshot([receipt()])
        validate_data(data)

    def test_validate_data_rejects_forged_probabilities(self):
        data = snapshot([receipt()])
        data['matches'][0]['probabilities'] = [0.99, 0.01]
        with self.assertRaises(AssertionError):
            validate_data(data)

    def test_validate_data_rejects_a_hand_entered_odds_change(self):
        data = snapshot([receipt()])
        data['matches'][0]['evidence'][0]['decimal_odds'] = [2.0, 2.0]
        with self.assertRaises(AssertionError):
            validate_data(data)


class IndependentAuditorTests(unittest.TestCase):
    def test_priced_row_passes_the_independent_audit(self):
        data = snapshot([receipt()])
        _, errors = load_auditor().inspect(data)
        self.assertEqual(errors, [])

    def test_auditor_rejects_aliases_without_a_primary_source(self):
        forged = receipt(alias_sources=[None, None])
        data = snapshot([forged])
        _, errors = load_auditor().inspect(data)
        self.assertTrue(errors)

    def test_auditor_rejects_forged_probabilities(self):
        data = snapshot([receipt()])
        data['matches'][0]['probabilities'] = [0.9, 0.1]
        _, errors = load_auditor().inspect(data)
        self.assertTrue(errors)

    def test_auditor_rejects_stale_observation(self):
        data = snapshot([receipt()])
        row = data['matches'][0]
        stale = iso(NOW - timedelta(hours=10))
        row['evidence'][0]['observed_at'] = stale
        row['evidence'][0]['raw']['observed_at'] = stale
        _, errors = load_auditor().inspect(data)
        self.assertTrue(errors)

    def test_diacritic_labels_resolve_in_the_independent_auditor(self):
        raw = receipt(source_teams=['LOS NINOS', 'Procyon'],
                      team_aliases=[['LOS NINOS'], ['Procyon']],
                      alias_sources=[None, None], odds=[2.85, 1.34], fixture_id='R1')
        data = snapshot([raw], team_a='Los Niños', team_b='Procyon')
        row = data['matches'][0]
        self.assertEqual(row['pick'], 'Procyon')
        _, errors = load_auditor().inspect(data)
        self.assertEqual(errors, [])


if __name__ == '__main__':
    unittest.main()
