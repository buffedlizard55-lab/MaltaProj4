"""Historical replay must not stop refreshes; live source clocks still fail closed.

All Alpha/Bravo inputs below are synthetic memory-only test fixtures, not odds or
claims about a real match. Historical checks use the retained official capture.
"""
import copy
import importlib.util
import tempfile
import json
import unittest
from datetime import timedelta
from bs4 import BeautifulSoup
from pathlib import Path

from scripts import books, core, validate, build

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


class BriefingFreshnessTests(unittest.TestCase):
    def strip(self, **overrides):
        data = {'last_attempt_at': core.iso(NOW), 'fixtures_observed_at': core.iso(NOW), 'built_at': core.iso(NOW)}
        data.update(overrides)
        return BeautifulSoup(build.fresh_strip(data, [], [], [], []), 'html.parser').select_one('#freshness-strip')

    def test_recent_failed_attempt_cannot_renew_old_fixture_evidence(self):
        node = self.strip(fixtures_observed_at=core.iso(NOW - timedelta(hours=9)))
        self.assertIn('stale', node['class'])
        self.assertIn('older than 8 hours', node.get_text())
        self.assertIn('fixture evidence 22 Oct 2026 · 00:00 UTC', node.get_text())

    def test_missing_malformed_exact_boundary_or_future_evidence_fails_closed(self):
        for observed in (None, 'unverified', core.iso(NOW - timedelta(hours=8)), core.iso(NOW + timedelta(minutes=6))):
            with self.subTest(observed=observed):
                self.assertIn('stale', self.strip(fixtures_observed_at=observed)['class'])

    def test_freshness_uses_explicit_build_clock_not_attempt_clock(self):
        self.assertIn('live', self.strip(last_attempt_at=core.iso(NOW - timedelta(hours=10)))['class'])
        self.assertIn('stale', self.strip(built_at=core.iso(NOW + timedelta(hours=8)))['class'])

    def test_invalid_display_time_is_explicitly_unverified(self):
        node = self.strip(last_attempt_at='unverified', fixtures_observed_at='unverified')
        self.assertIn('Last checked unverified', node.get_text())
        self.assertIn('fixture evidence unverified', node.get_text())

    def test_strip_counters_share_browser_expiry_hooks(self):
        node = self.strip()
        self.assertEqual({n['data-count'] for n in node.select('[data-count]')}, {'open', 'picked', 'priced', 'unresolved'})


class BriefingDisclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads((ROOT / 'research/session-eaff7cce/capture/snapshot.json').read_text())
        cls.html = BeautifulSoup(build.overview(copy.deepcopy(cls.snapshot)), 'html.parser')

    def test_all_open_phone_and_desktop_pick_cards_remain_unfolded(self):
        expected = sum(m['state'] == 'open' for m in self.snapshot['matches'])
        glance = self.html.select_one('#picks-at-a-glance')
        self.assertIsNone(glance.find_parent('details'))
        self.assertEqual(len(glance.select('.glance-row')), expected)
        self.assertEqual(len(glance.select('.glance-card-mobile')), expected)

    def test_no_percentage_rows_remain_separate_and_unfolded(self):
        section = self.html.select_one('#unresolved-picks')
        self.assertIsNone(section.find_parent('details'))
        expected = sum(m['state'] == 'open' and m.get('probabilities') is None for m in self.snapshot['matches'])
        self.assertEqual(len(section.select('.unresolved-row')), expected)

    def test_duplicate_boards_fold_without_removing_legacy_anchors(self):
        folded = self.html.select_one('#detailed-summary')
        self.assertIsNone(folded.get('open'))
        self.assertIsNotNone(folded.select_one('#unresolved-summary'))
        self.assertIsNotNone(folded.select_one('#pick-limitations'))
        self.assertTrue(self.html.select_one('#start-here').find_parent('details'))
        self.assertEqual(self.html.select_one('#coverage-now .actions .button')['href'], 'picks.html')

    def test_each_archived_pick_outcome_row_links_its_exact_official_result(self):
        day = json.loads((ROOT / 'data/analysis.json').read_text())['day_five_results']
        page = BeautifulSoup(build.results_section(day), 'html.parser')
        table = next(t for t in page.select('table') if 'Board picks as published' in t.caption.get_text())
        expected = {f'{m["winner"]} {m["score"]} {m["loser"]}': m['match_url'] for m in day['matches']}
        for row in table.select('tbody tr'):
            label = row.select_one('td strong').get_text()
            self.assertEqual(row.select_one('.source-links a')['href'], expected[label])

    def test_concurrent_banner_reports_real_blank_counts_and_stays_inside_navigation_guide(self):
        banner = BeautifulSoup(build.executive_banner(self.snapshot), 'html.parser')
        self.assertNotIn('Every open match has a pick;', banner.get_text())
        self.assertEqual(banner.select_one('[data-count="unresolved"]').get_text(), '1')
        self.assertEqual(banner.select_one('[data-count="picked"]').get_text(), '45')
        self.assertTrue(self.html.select_one('#exec-banner').find_parent('details'))
        self.assertEqual(len(self.html.select('#exec-banner')), 1)

    def test_capture_contract_only_derives_production_deadlines(self):
        from scripts.coverage_contract import inspect
        checked = copy.deepcopy(self.snapshot)
        for match in checked['matches']:
            match['expires_at'] = core.pick_deadline(match, checked['fixtures_observed_at'])
        self.assertEqual(inspect(checked, checked['generated_at'])['problems'], [])
        self.assertTrue(all('expires_at' not in m for m in self.snapshot['matches']))

    def test_uncorroborated_name_mismatch_stays_blank_in_the_dated_capture(self):
        from unittest.mock import patch
        match = next(m for m in self.snapshot['matches'] if m['id'] == '1082919')
        self.assertIsNone(match['pick'])
        self.assertIsNone(match['probabilities'])
        # Replay the pre-corroboration condition, not an assertion that another
        # session can never register a subsequently sourced identity receipt.
        aliases = {k: v for k, v in core.ALIAS_MAP.items()
                   if v != core.plain_name('Tropa do KinGui')}
        with patch.object(core, 'ALIAS_MAP', aliases):
            self.assertNotEqual(core.norm('Projeto do KinGui'), core.norm('Tropa do KinGui'))


class HonestBlankAuditorTests(unittest.TestCase):
    """A real unresolved row is valid; a fabricated value or empty excuse is not.

    Mutations below are memory/tempfile-only negative test inputs, never changes
    to the captured official response or to published data.
    """
    @classmethod
    def setUpClass(cls):
        cls.board = json.loads((ROOT / 'research/session-eaff7cce/capture/snapshot.json').read_text())
        cls.board['matches'] = [m for m in cls.board['matches'] if m['id'] == '1082919']
        cls.board['fixture_evidence'] = [r for r in cls.board['fixture_evidence'] if str(r['id']) == '1082919']
        cls.modules = {}
        for name, file in [('board', 'verification-7601d5ee/audit_board_7601d5ee.py'),
                           ('rows', 'verification-7271c5d5/audit_board_7271c5d5.py'),
                           ('acceptance', 'verification-767649ba/audit_2026_10_22.py')]:
            spec = importlib.util.spec_from_file_location('audit_eaff7cce_' + name, ROOT / file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            cls.modules[name] = module

    def candidates(self):
        yield 'honest blank', copy.deepcopy(self.board), True
        for field, bad in [('fair_odds', [1.1, 9.0]), ('method', 'research_made_up'),
                           ('reason', ''), ('attempts', [])]:
            changed = copy.deepcopy(self.board)
            changed['matches'][0][field] = bad
            yield 'invalid ' + field, changed, False

    def test_probe_accepts_honest_blank_but_rejects_unsupported_values(self):
        from scripts.probe_7601d5ee import audit_latest_board
        for label, board, valid in self.candidates():
            with self.subTest(case=label):
                if valid:
                    self.assertEqual(audit_latest_board(board)['unresolved_open'], 1)
                else:
                    with self.assertRaises(AssertionError):
                        audit_latest_board(board)

    def test_independent_row_auditor_accepts_only_documented_blank(self):
        standings = (ROOT / 'data/vrs/standings_global_2026_10_05.md').read_text()
        for label, board, valid in self.candidates():
            with self.subTest(case=label):
                _, errors = self.modules['rows'].audit_snapshot(board, standings)
                self.assertEqual(not errors, valid, errors)

    def test_independent_board_auditor_accounts_for_unresolved_separately(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'data').mkdir()
            (root / 'review.html').write_text((ROOT / 'review.html').read_text())
            for label, board, valid in self.candidates():
                (root / 'data/latest.json').write_text(json.dumps(board))
                with self.subTest(case=label):
                    if valid:
                        result = self.modules['board'].audit_board_math(root)
                        self.assertEqual(result['unresolved_open'], 1)
                        self.assertEqual(result['research_only_open'], 0)
                    else:
                        with self.assertRaises(AssertionError):
                            self.modules['board'].audit_board_math(root)

    def test_acceptance_auditor_does_not_report_unresolved_as_research_or_100_percent(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'latest.json'
            for label, board, valid in self.candidates():
                path.write_text(json.dumps(board))
                with self.subTest(case=label):
                    report = self.modules['acceptance'].run_audit(path, ROOT)
                    self.assertEqual(not report['failures'], valid, report['failures'])
                    if valid:
                        self.assertEqual(report['open_unpicked'], 1)
                        self.assertEqual(report['open_research_no_percentage'], 0)
                        self.assertIn('0.0%', self.modules['acceptance'].format_markdown(report))

    def test_day_five_receipt_auditor_does_not_require_a_fabricated_current_pick(self):
        from scripts.audit_d6df5beb import Audit, audit_published_data
        receipt = json.loads((ROOT / 'research/session-d6df5beb/receipt-2026-10-18.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'latest.json'
            for label, board, valid in self.candidates():
                path.write_text(json.dumps(board)); audit = Audit()
                with self.subTest(case=label):
                    summary = audit_published_data(receipt, audit, path)
                    self.assertEqual(not audit.failures, valid, audit.failures)
                    if valid:
                        self.assertEqual(summary['unresolved'], 1)
                        self.assertEqual(summary['research_only'], 0)

    def test_closed_quote_history_is_retained_but_not_a_live_recommendation(self):
        # A future source refresh may legitimately have no historical quotes.
        # Test retention by closing the immutable capture at a fixed lock clock,
        # never by depending on whichever snapshot is currently published.
        captured = json.loads((ROOT / 'research/session-eaff7cce/capture/snapshot.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            build.build(captured, Path(temp), now=core.dt('2026-10-22T08:03:00Z'))
            board = json.loads((Path(temp) / 'data/latest.json').read_text())
        closed = next(m for m in board['matches'] if m['state'] != 'open' and m.get('evidence'))
        board['matches'] = [closed]
        board['fixture_evidence'] = [r for r in board['fixture_evidence'] if str(r['id']) == closed['id']]
        standings = (ROOT / 'data/vrs/standings_global_2026_10_05.md').read_text()
        _, errors = self.modules['rows'].audit_snapshot(board, standings)
        self.assertEqual(errors, [])
        self.assertTrue(closed['evidence'])
        self.assertTrue(all(closed.get(key) is None for key in ('probabilities', 'fair_odds', 'pick', 'method')))


class ActualStavkaAndConcurrentReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import gzip
        import hashlib
        base = ROOT / 'research/session-eaff7cce/targeted'
        checks = json.loads((base / 'report.json').read_text())['source_checks']
        cls.receipt = next(r for r in checks if r['url'].endswith('23-10-2026-ex-zero-tenacity-ex-rustec'))
        body = gzip.decompress((base / cls.receipt['archive']).read_bytes())
        assert hashlib.sha256(body).hexdigest() == cls.receipt['sha256']
        cls.html = body.decode()
        saint = next(r for r in checks if r['url'].endswith('23-10-2026-ex-rustec-saint-sinners'))
        cls.saint_html = gzip.decompress((base / saint['archive']).read_bytes()).decode()

    def changed(self, mutate):
        soup = BeautifulSoup(self.html, 'html.parser')
        script = soup.select_one('#__NUXT_DATA__')
        table = json.loads(script.get_text())
        index = next(i for i, v in enumerate(table) if isinstance(v, dict) and 'promoSettings' in v)
        mutate(table, table[index], index)
        script.string = json.dumps(table, ensure_ascii=False)
        return str(soup)

    def test_real_newsarticle_page_binds_utc_bo3_and_winner_panel_not_editorial_prices(self):
        self.assertNotIn('"@type":"SportsEvent"', self.html)
        readings = books.parse_listing(self.html)
        self.assertEqual(len(readings), 1)
        self.assertEqual([readings[0][k] for k in ('team1', 'team2', 'start', 'best_of', 'odds')],
                         ['ex-Zero Tenacity', 'ex-RUSTEC', '2026-10-23T08:00:00Z', 3, [1.9, 1.8]])
        self.assertTrue(readings[0]['bound_to_labels'])
        self.assertIn('not independently verified', readings[0]['source_note'])

    def test_real_empty_saint_panel_does_not_borrow_related_fixture_odds(self):
        self.assertEqual(books.parse_listing(self.saint_html), [])

    def test_nuxt_rejects_wrong_canonical_timezone_live_equal_wrong_market_and_cycles(self):
        def set_panel_field(table, match, field, value):
            promo = table[match['promoSettings']]
            maximum = table[promo['maxBookmakerOdds']]
            panel = table[maximum['one_two']]
            quote = table[panel[0]]
            table[quote[field]] = value
        mutations = [
            lambda t, m, i: t.__setitem__(m['matchDate'], '2026-10-23T08:00:00'),
            lambda t, m, i: t.__setitem__(m['isLive'], True),
            lambda t, m, i: set_panel_field(t, m, 'value', 1.8),
            lambda t, m, i: set_panel_field(t, m, 'type', 'totals'),
            lambda t, m, i: set_panel_field(t, m, 'bookmakerCode', 'unverified-other-operator'),
            lambda t, m, i: m.__setitem__('promoSettings', i),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutations.index(mutate)):
                self.assertEqual(books.parse_listing(self.changed(mutate)), [])
        wrong = self.html.replace('https://stavka.tv/matches/csgo/23-10-2026-ex-zero-tenacity-ex-rustec',
                                  'https://stavka.tv/matches/csgo/not-this-fixture')
        self.assertEqual(books.parse_listing(wrong), [])

    def test_actual_page_reobservation_preserves_cache_clock_and_rejects_missing_clock_or_format_conflict(self):
        register = json.loads((ROOT / 'data/book-receipts.json').read_text())
        original = next(r for r in register['receipts'] if r['id'] == 'stavka-winline-1079654-ex-zero-tenacity-ex-rustec')
        class Source:
            def __init__(self, html, receipt): self.html, self.receipt = html, receipt
            def get(self, *args): return self.html, dict(self.receipt)
        now = core.dt('2026-10-22T08:25:00Z')
        renewed, records = books.reobserve([original], Source(self.html, self.receipt), now)
        self.assertEqual(records[0]['status'], 'renewed')
        self.assertEqual(renewed[0]['observed_at'], self.receipt['observed_at'])
        self.assertEqual(renewed[0]['source_receipts'][0]['sha256'], self.receipt['sha256'])
        self.assertEqual(renewed[0]['odds'], [1.9, 1.8])
        cases = [(self.html, {}),
                 (self.changed(lambda t, m, i: t.__setitem__(m['bestOf'], 5)), self.receipt)]
        for html, receipt in cases:
            unchanged, records = books.reobserve([original], Source(html, receipt), now)
            self.assertNotEqual(records[0]['status'], 'renewed')
            self.assertEqual(unchanged[0]['observed_at'], original['observed_at'])

    def test_concurrent_capture_zero_assertions_do_not_force_guessed_future_picks(self):
        from unittest.mock import patch
        spec = importlib.util.spec_from_file_location('cb_dated_replay_eaff7cce', ROOT / 'tests/test_session_cb867c3c.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        board = json.loads((ROOT / 'research/session-eaff7cce/capture/snapshot.json').read_text())
        for row in board['matches']:
            row['expires_at'] = core.pick_deadline(row, board['fixtures_observed_at'])
        test = module.TestLiveBoardCompletenessAndContract()
        methods = [test.test_zero_open_rows_without_pick_and_indent1_registers_preserved,
                   test.test_coverage_contract_passes_at_snapshot_clock_with_zero_problems]
        with patch.object(module, 'SNAPSHOT', board):
            for check in methods: check()
            next(m for m in board['matches'] if m['id'] == '1082919')['reason'] = ''
            for check in methods:
                with self.assertRaises(AssertionError): check()

    def test_expired_future_quote_remains_archived_without_any_live_values(self):
        board = json.loads((ROOT / 'research/session-eaff7cce/capture/snapshot.json').read_text())
        board['matches'] = [m for m in board['matches'] if m['id'] == '1082858']
        board['fixture_evidence'] = [r for r in board['fixture_evidence'] if str(r['id']) == '1082858']
        with tempfile.TemporaryDirectory() as temp:
            build.build(board, Path(temp), now=core.dt('2026-10-22T16:00:00Z'))
            expired = json.loads((Path(temp) / 'data/latest.json').read_text())
        row = expired['matches'][0]
        self.assertEqual(row['state'], 'open')
        self.assertTrue(row['evidence'])
        self.assertTrue(row['reason'].startswith('Evidence deadline passed'))
        self.assertTrue(all(row.get(k) is None for k in ('pick', 'method', 'probabilities', 'fair_odds')))
        spec = importlib.util.spec_from_file_location('expired_history_eaff7cce', ROOT / 'verification-7271c5d5/audit_board_7271c5d5.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        _, errors = module.audit_snapshot(expired, (ROOT / 'data/vrs/standings_global_2026_10_05.md').read_text())
        self.assertEqual(errors, [])


if __name__ == '__main__':
    unittest.main()
