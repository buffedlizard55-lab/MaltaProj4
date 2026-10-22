"""Historical replay must not stop refreshes; live source clocks still fail closed.

All Alpha/Bravo inputs below are synthetic memory-only test fixtures, not odds or
claims about a real match. Historical checks use the retained official capture.
"""
import copy
import json
import unittest
from datetime import timedelta
from pathlib import Path

from scripts import books, core, validate

ROOT = Path(__file__).resolve().parents[1]
NOW = core.dt('2026-10-22T09:00:00Z')
URL = 'https://egamersworld.com/counterstrike/match/TEST_ONLY/alpha-vs-bravo-TEST_ONLY'
HTML = '''<script type="application/ld+json">{"name":"Alpha VS Bravo",
"startDate":"2026-10-22T12:00:00Z"}</script>
<div>Alpha 1.5 Make a bet 3.0 Bravo 3.0</div>'''


def fixture():
    return {'id': 'TEST_ONLY', 'teams': ['Alpha', 'Bravo'], 'state': 'open',
            'start': '2026-10-22T12:00:00Z', 'lock': '2026-10-22T11:54:00Z',
            'source_url': 'https://play.hotspawn.com/cs2-pickems', 'best_of': None,
            'probabilities': None, 'fair_odds': None, 'pick': None, 'method': None,
            'evidence': [], 'attempts': [], 'flags': []}


def rejected():
    return {'fixture_id': 'TEST_ONLY', 'teams': ['Alpha', 'Bravo'], 'url': URL,
            'displayed': [1.8, 1.8], 'observed_at': '2026-10-21T00:00:00Z'}


class Sources:
    def __init__(self, html=HTML, observed=core.iso(NOW), error=None):
        self.html, self.observed, self.error = html, observed, error
        self.seen = []

    def get(self, name, url, as_json=True):
        self.seen.append(url)
        if self.error:
            raise ValueError(self.error)
        return self.html, {'name': name, 'url': url, 'observed_at': self.observed,
                           'sha256': 'TEST_ONLY_NOT_A_REAL_BODY_HASH'}


class HistoricalReplayClockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads((ROOT / 'research/harvest-bf09aa40/snapshot.json').read_text())
        cls.row = next(m for m in cls.snapshot['matches'] if m['id'] == '1082858')
        cls.quote = cls.row['evidence'][0]

    def test_historical_arithmetic_remains_reproducible_at_its_own_clock(self):
        validate.validate_model_row(self.row, self.quote, core.dt(self.snapshot['generated_at']))

    def test_old_source_is_still_refused_for_current_recommendations(self):
        with self.assertRaisesRegex(AssertionError, 'eight hours'):
            validate.validate_model_row(self.row, self.quote, core.dt(self.quote['observed_at']) + timedelta(hours=8))

    def test_precise_ttl_boundary_is_not_extended_by_the_test_repair(self):
        deadline = core.dt(self.quote['observed_at']) + timedelta(hours=8)
        validate.validate_model_row(self.row, self.quote, deadline - timedelta(microseconds=1))
        self.assertFalse(core.fresh(self.quote['observed_at'], deadline))


class GapWatchTests(unittest.TestCase):
    def watch(self, html=HTML, observed=core.iso(NOW), row=None, prior=None, receipts=None, error=None):
        src = Sources(html, observed, error)
        result, records = books.watch_unpriced(receipts or [], [row or fixture()], src, NOW,
                                               register=[prior or rejected()])
        return result, records, src

    def test_a_placeholder_url_is_revisited_without_seeding_a_price(self):
        prior = rejected()
        before = copy.deepcopy(prior)
        found, records, src = self.watch(prior=prior)
        self.assertEqual(src.seen, [URL])
        self.assertEqual(prior, before, 'the historical rejection is immutable')
        self.assertEqual(records[0]['status'], 'resolved')
        self.assertEqual(found[0]['odds'], [1.5, 3.0], 'old rejected prices may not supply the line')
        self.assertIn('Secondary', found[0]['limitation'])
        self.assertNotIn('best_of', found[0], 'unknown format stays blank')
        row = fixture()
        core.book_research_pick(row, found, NOW)
        self.assertEqual(row['pick'], 'Alpha')
        self.assertEqual(row['method'], 'bookmaker_fallback')
        self.assertAlmostEqual(row['probabilities'][0], 2 / 3)
        self.assertEqual(row['evidence'][0]['source_receipts'][0]['url'], URL)

    def test_an_identical_default_pair_remains_blank(self):
        found, records, _ = self.watch(HTML.replace('1.5', '1.8').replace('3.0', '1.8'))
        self.assertEqual(found, [])
        self.assertEqual(records[0]['status'], 'unresolved')
        self.assertIn('placeholder', records[0]['reason'])

    def test_equal_nondefault_odds_do_not_invent_a_directional_pick(self):
        self.assertEqual(self.watch(HTML.replace('1.5', '2.0').replace('3.0', '2.0'))[0], [])

    def test_other_start_unnamed_opponent_and_unbound_prices_are_refused(self):
        for html in (HTML.replace('12:00:00Z', '13:00:00Z'),
                     HTML.replace('Alpha VS Bravo', 'Alpha VS '),
                     HTML.replace('Alpha 1.5', 'Different team 1.5'),
                     HTML.replace('3.0 Bravo 3.0', '3.0 Different team 3.0')):
            with self.subTest(html=html):
                self.assertEqual(self.watch(html)[0], [])

    def test_duplicate_exact_readings_are_ambiguous_not_a_best_price_choice(self):
        self.assertEqual(self.watch(HTML + HTML)[0], [])

    def test_missing_invalid_old_and_future_observations_are_refused(self):
        for observed in (None, '', 'unverified', '2026-10-22T01:00:00Z', '2026-10-22T09:06:00Z'):
            with self.subTest(observed=observed):
                found, records, _ = self.watch(observed=observed)
                self.assertEqual(found, [])
                self.assertIn('observation', records[0]['reason'])

    def test_cache_adjusted_source_clock_is_retained_not_reset(self):
        found, _, _ = self.watch(observed='2026-10-22T06:00:00Z')
        self.assertEqual(found[0]['observed_at'], '2026-10-22T06:00:00Z')

    def test_registered_urls_cannot_fetch_other_hosts_or_bad_schemes(self):
        for url in ('http://egamersworld.com/counterstrike/match/x',
                    'https://untrusted.example/counterstrike/match/x',
                    'https://egamersworld.com@untrusted.example/counterstrike/match/x',
                    URL + '?unverified=1'):
            prior = rejected(); prior['url'] = url
            found, records, src = self.watch(prior=prior)
            self.assertEqual((found, records, src.seen), ([], [], []))

    def test_only_current_unpriced_nonconflicting_matching_fixtures_are_fetched(self):
        for changes in ({'state': 'not_open'}, {'probabilities': [.6, .4]},
                        {'resolution_blocked': True}, {'id': 'OTHER_TEST_ONLY'}):
            row = fixture(); row.update(changes)
            self.assertEqual(self.watch(row=row)[2].seen, [])
        prior = rejected(); prior['teams'] = ['Alpha', 'Different team']
        self.assertEqual(self.watch(prior=prior)[2].seen, [])

    def test_existing_receipt_is_not_fetched_twice(self):
        receipt = {'fixture_id': 'TEST_ONLY'}
        found, records, src = self.watch(receipts=[receipt])
        self.assertEqual((found, records, src.seen), ([receipt], [], []))

    def test_known_series_format_without_listing_confirmation_is_refused(self):
        row = fixture(); row['best_of'] = 3
        found, records, _ = self.watch(row=row)
        self.assertEqual(found, [])
        self.assertIn('format', records[0]['reason'])

    def test_bad_margin_and_access_failure_stay_explicit_and_blank(self):
        found, records, _ = self.watch(HTML.replace('1.5', '1.01').replace('3.0', '1.1'))
        self.assertEqual(found, [])
        self.assertIn('margin', records[0]['reason'])
        found, records, _ = self.watch(error='HTTP 403; access refused')
        self.assertEqual(found, [])
        self.assertIn('403', records[0]['reason'])

    def test_prior_duplicate_reads_are_deduplicated(self):
        src = Sources()
        found, records = books.watch_unpriced([], [fixture()], src, NOW, register=[rejected(), rejected()])
        self.assertEqual(len(found), 1)
        self.assertEqual(len(records), 1)
        self.assertEqual(src.seen, [URL])


class ExistingListingClockTests(unittest.TestCase):
    def receipt(self):
        return {'id': 'TEST_ONLY', 'fixture_id': 'TEST_ONLY', 'url': URL,
                'source_teams': ['Alpha', 'Bravo'], 'team_aliases': [['Alpha'], ['Bravo']],
                'start': '2026-10-22T12:00:00Z', 'odds': [1.6, 2.8],
                'observed_at': '2026-10-21T00:00:00Z'}

    def test_cached_existing_receipt_renews_only_at_actual_source_time(self):
        found, records = books.reobserve([self.receipt()], Sources(observed='2026-10-22T06:00:00Z'), NOW)
        self.assertEqual(records[0]['status'], 'renewed')
        self.assertEqual(found[0]['observed_at'], '2026-10-22T06:00:00Z')
        self.assertEqual(found[0]['reobserved']['observed_at'], '2026-10-22T06:00:00Z')
        self.assertTrue(found[0]['source_receipts'])

    def test_missing_or_expired_source_time_never_renews_a_receipt(self):
        for observed in (None, 'unverified', '2026-10-22T01:00:00Z'):
            receipt = self.receipt()
            found, records = books.reobserve([receipt], Sources(observed=observed), NOW)
            self.assertEqual(records[0]['status'], 'error')
            self.assertEqual(found, [receipt])


if __name__ == '__main__':
    unittest.main()
