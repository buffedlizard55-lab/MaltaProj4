"""Complete pick-board inventory and finite research-pick lifetimes.

Site tests use a retained, dated official-source capture, not mutable latest.json.
Synthetic deadline inputs below are memory-only test fixtures, never published.
"""
import copy
import gzip
import hashlib
import json
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import books, build, core, validate
from scripts.probe_ac4743a3 import coverage, evidence_index, markdown, verify_primary_inventory

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / 'research/harvest-bf09aa40/snapshot.json'
NOW = core.dt('2026-10-22T01:00:00Z')


def research_row(method='research_rank'):
    return {'pick': 'Test only A', 'method': method, 'evidence': [],
            'start': '2026-10-23T10:00:00Z', 'lock': '2026-10-23T09:54:00Z',
            'hltv_context': {'observed_at': '2026-10-22T00:30:00Z'},
            'vrs_research': {'observed_at': '2026-10-22T00:45:00Z'}}


class ResearchDeadlineTests(unittest.TestCase):
    def test_each_research_method_uses_its_actual_evidence_timestamp(self):
        for method, deadline in [('research_rank', '2026-10-22T08:30:00Z'),
                                 ('research_rank_single', '2026-10-22T08:30:00Z'),
                                 ('research_vrs_single', '2026-10-22T08:45:00Z')]:
            with self.subTest(method=method):
                self.assertEqual(core.pick_deadline(research_row(method), core.iso(NOW)), deadline)

    def test_inventory_lifetime_and_lock_can_only_shorten_the_lifetime(self):
        row = research_row()
        self.assertEqual(core.pick_deadline(row, '2026-10-22T00:00:00Z'), '2026-10-22T08:00:00Z')
        row['lock'] = '2026-10-22T02:54:00Z'
        self.assertEqual(core.pick_deadline(row, core.iso(NOW)), row['lock'])
        row['start'] = '2026-10-22T02:00:00Z'
        self.assertEqual(core.pick_deadline(row, core.iso(NOW)), row['start'])

    def test_missing_or_malformed_required_times_fail_closed(self):
        for field in ('start', 'lock'):
            row = research_row(); row[field] = None
            self.assertIsNone(core.pick_deadline(row, core.iso(NOW)))
        for value in (None, '', 'unverified', '2026-10-22T00:00:00'):
            row = research_row(); row['hltv_context']['observed_at'] = value
            self.assertIsNone(core.pick_deadline(row, core.iso(NOW)))
        self.assertIsNone(core.pick_deadline(research_row(), None))

    def test_unresolved_rows_do_not_gain_a_recommendation_or_a_deadline(self):
        row = research_row(); row.update(pick=None, method=None)
        self.assertIsNone(core.pick_deadline(row, core.iso(NOW)))
        self.assertIsNone(core.research_observation(row))


class CompletePickBoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CAPTURE.read_text())
        cls.clock = core.dt(cls.data['generated_at'])
        cls.temp = tempfile.TemporaryDirectory()
        cls.site = Path(cls.temp.name)
        build.build(cls.data, cls.site, now=cls.clock)
        cls.published = json.loads((cls.site / 'data/latest.json').read_text())

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def soup(self, name='picks'):
        return BeautifulSoup((self.site / (name + '.html')).read_text(), 'html.parser')

    def test_pick_board_contains_every_open_match_not_only_priced_matches(self):
        expected = {m['id'] for m in self.published['matches'] if m['state'] == 'open'}
        rows = self.soup().select('tr[data-match]')
        self.assertEqual({row['data-match'] for row in rows}, expected)
        self.assertEqual(len(rows), len(expected))
        self.assertTrue(any(row['data-status'] == 'research' for row in rows))
        self.assertTrue(any(row['data-status'] == 'unresolved' for row in rows))
        self.assertEqual(self.soup().select_one('#status option[selected]')['value'], 'open')

    def test_every_pick_has_official_sources_and_a_finite_deadline(self):
        for row in self.soup().select('tr[data-match]'):
            self.assertTrue(row.select_one('.source-links a[href*="hotspawn.com/"]'))
            self.assertTrue(row.select_one('.source-links a[href^="evidence.html#match-"]'))
            if row.select_one('.pick-cell .pick'):
                self.assertTrue(row.get('data-expires'))
            if row['data-status'] == 'research':
                self.assertFalse(row.select('.prob-pair'))
                self.assertTrue(row.select_one('.pick-cell .research-only'))
                self.assertIn('no probability', row.select_one('.review-reason').get_text(' ', strip=True).lower())

    def test_only_the_current_navigation_item_is_marked_current(self):
        for name in ('picks', 'unresolved'):
            soup = self.soup(name)
            for nav in soup.select('nav[aria-label="Main navigation"], nav[aria-label="Mobile navigation"]'):
                links = nav.select('[aria-current="page"]')
                self.assertEqual(len(links), 1)
                self.assertEqual(links[0]['href'], name + '.html')

    def test_mobile_cards_and_queue_carry_research_and_expiry_metadata(self):
        soup = self.soup('index')
        research = soup.select('.glance-card-mobile[data-glance-research="1"]')
        self.assertTrue(research)
        self.assertTrue(all(card.get('data-glance-expires') for card in research))
        self.assertTrue(all(a.get('data-glance-expires') for a in soup.select('.queue a')))

    def test_new_summary_recommendations_have_the_same_finite_lifetime(self):
        soup = self.soup('index')
        entries = soup.select('.unresolved-row[data-glance-research="1"]')
        self.assertTrue(entries)
        self.assertTrue(all(a.get('data-glance-expires') for a in entries))
        self.assertTrue(soup.select_one('#coverage-now [data-count="picked"]'))
        lookup = {m['id']: m for m in self.published['matches']}
        validate.verify_recommendation_deadlines(soup, lookup, self.published['fixtures_observed_at'])
        entries[0].attrs.pop('data-glance-expires')
        with self.assertRaisesRegex(AssertionError, 'deadline differs'):
            validate.verify_recommendation_deadlines(soup, lookup, self.published['fixtures_observed_at'])

    def test_build_withholds_research_at_exact_eight_hour_boundary(self):
        data = copy.deepcopy(self.data)
        row = next(m for m in data['matches'] if m.get('method') == 'research_rank_single')
        # Keep the lock/start in the future to isolate evidence expiry.
        row['lock'] = core.iso(self.clock + timedelta(days=2))
        row['start'] = core.iso(self.clock + timedelta(days=3))
        row['hltv_context']['observed_at'] = core.iso(self.clock)
        data['matches'] = [row]
        data['fixtures_observed_at'] = core.iso(self.clock)
        for age, actionable in [(timedelta(hours=8, microseconds=-1), True), (timedelta(hours=8), False)]:
            with self.subTest(age=age), tempfile.TemporaryDirectory() as directory:
                build.build(data, directory, now=self.clock + age)
                saved = json.loads((Path(directory) / 'data/latest.json').read_text())['matches'][0]
                self.assertEqual(bool(saved['pick']), actionable)
                self.assertIsNone(saved['probabilities'])
                if not actionable:
                    self.assertIn('Evidence deadline passed', saved['reason'])

    def test_clock_future_research_is_withheld_even_with_a_future_deadline(self):
        data = copy.deepcopy(self.data)
        row = next(m for m in data['matches'] if m.get('method') == 'research_rank_single')
        row['hltv_context']['observed_at'] = core.iso(self.clock + timedelta(minutes=6))
        data['matches'] = [row]
        with tempfile.TemporaryDirectory() as directory:
            build.build(data, directory, now=self.clock)
            saved = json.loads((Path(directory) / 'data/latest.json').read_text())['matches'][0]
            self.assertIsNone(saved['pick'])

    def test_validator_refuses_a_missing_research_row_on_the_pick_board(self):
        with tempfile.TemporaryDirectory() as directory:
            build.build(self.data, directory, now=self.clock)
            path = Path(directory) / 'picks.html'
            soup = BeautifulSoup(path.read_text(), 'html.parser')
            soup.select_one('tr[data-status="research"]').decompose()
            path.write_text(str(soup))
            with self.assertRaisesRegex(AssertionError, 'Picks must contain every open fixture'):
                validate.validate_site(directory)


class FallbackScopeTests(unittest.TestCase):
    def setUp(self):
        self.receipts = [{'fixture_id': 'test-unpriced'}, {'fixture_id': 'test-priced'},
                         {'fixture_id': 'test-closed'}, {'fixture_id': 'test-conflict'},
                         {'fixture_id': 'test-removed'}]
        self.fixtures = [{'id': 'test-unpriced', 'state': 'open', 'probabilities': None},
                         {'id': 'test-priced', 'state': 'open', 'probabilities': [.6, .4]},
                         {'id': 'test-closed', 'state': 'not_open', 'probabilities': None},
                         {'id': 'test-conflict', 'state': 'open', 'probabilities': None, 'resolution_blocked': True}]

    def test_only_unpriced_open_unblocked_fixtures_enter_book_reobservation(self):
        self.assertEqual(books.for_unpriced(self.receipts, self.fixtures), [self.receipts[0]])

    def test_no_gap_means_no_listing_requests_even_with_historical_receipts(self):
        self.assertEqual(books.for_unpriced(self.receipts, self.fixtures[1:]), [])

    def test_filter_does_not_mutate_the_dated_research_register(self):
        original = copy.deepcopy(self.receipts)
        books.for_unpriced(self.receipts, self.fixtures)
        self.assertEqual(self.receipts, original)

    def test_unknown_market_label_is_not_guessed_from_the_opponent(self):
        self.assertNotEqual(core.norm('MORROW'), core.norm('benched gods'))


class PrimaryInventoryTests(unittest.TestCase):
    def setUp(self):
        self.row = {'id': 'TEST_ONLY', 'sport_alias': 'cs2', 'participants0_name': 'Test A'}
        self.snapshot = {'fixture_evidence': [self.row]}

    def test_exact_response_matches_all_retained_fields_but_excludes_crowd(self):
        raw = json.dumps([self.row | {'participants0_picked_percent': 99}])
        report = verify_primary_inventory(self.snapshot, raw)
        self.assertEqual(report['rows_checked'], 1)
        self.assertEqual(report['rows'][0]['fields_checked'], 3)

    def test_altered_field_or_crowd_evidence_is_rejected(self):
        raw = json.dumps([self.row])
        for change in ({'participants0_name': 'Changed'}, {'participants0_picked_percent': 99}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                verify_primary_inventory({'fixture_evidence': [self.row | change]}, raw)

    def test_a_multi_source_union_is_not_called_single_source_parity(self):
        report = verify_primary_inventory(self.snapshot, '[]')
        self.assertIn('unverified', report['status'])
        self.assertEqual(report['rows'], [])


class CorrectedSourceTests(unittest.TestCase):
    def test_zetta_register_cites_the_actual_match_and_dated_schedule(self):
        data = json.loads((ROOT / 'data/identities.json').read_text())
        entry = next(a for a in data['aliases'] if a['canonical'] == 'Zetta')
        links = [entry['source']] + [a['url'] for a in entry.get('corroboration', [])]
        self.assertTrue(any('/matches/2399865/' in u for u in links))
        self.assertFalse(any('/matches/2399867/' in u for u in links))
        self.assertIn('Swiss Round 5', entry['basis'])
        self.assertIn('dated pre-match schedule', entry['basis'])

    def test_off_chops_note_matches_the_replayed_points_without_standin_guess(self):
        notes = json.loads((ROOT / 'data/review-notes.json').read_text())
        entry = next(n for n in notes if n['id'] == 'db1f35c5-off-chops-rebrand-and-standin-2026-10-21')
        self.assertIn('60.2% / Ground Zero 39.8%', entry['finding'])
        self.assertNotIn('59.1%', entry['finding'])
        self.assertIn('no numeric adjustment', entry['finding'])
        self.assertNotIn('no sportsbook or exchange has opened', entry['finding'])


class ListingSourceTests(unittest.TestCase):
    def test_listing_html_is_not_claimed_to_be_an_official_operator_api(self):
        q = {'provider': 'EGamersWorld book listing', 'url': 'https://egamersworld.com/',
             'api_url': 'https://egamersworld.com/', 'decimal_odds': [8.1, 1.021]}
        self.assertTrue(build.listing_quote(q))
        text = BeautifulSoup(build.quote_source(q), 'html.parser').get_text()
        self.assertIn('published listing', text)
        self.assertNotIn('official API', text)
        for provider in ('Polymarket', 'Pinnacle'):
            with self.subTest(provider=provider):
                direct = {'provider': provider, 'api_url': 'https://example.invalid/'}
                self.assertFalse(build.listing_quote(direct))
                self.assertIn('official API', build.quote_source(direct))

    def test_dated_listing_limitation_is_visible_beside_derived_numbers(self):
        receipt = next(r for r in core.book_receipts() if r['id'] == 'egw-4yp_dlKtNl-nexora-k27')
        frozen = json.loads((ROOT / 'research/session-ac4743a3/k27-inventory-2026-10-22.json').read_text())
        row = core.normalize_fixtures([frozen['fixture']], {}, core.dt('2026-10-22T02:00:00Z'))[0]
        row.update(pick=None, probabilities=None, fair_odds=None, method=None, evidence=[], flags=[], attempts=[])
        core.book_research_pick(row, [receipt], core.dt('2026-10-22T02:00:00Z'))
        row['expires_at'] = core.pick_deadline(row, frozen['observed_at'])
        soup = BeautifulSoup(build.table([row], review=True), 'html.parser')
        self.assertIn('Listing estimate', soup.select_one('.pick-cell').get_text())
        self.assertIn('LISTING-DERIVED ESTIMATE', soup.select_one('.prob-label').get_text())
        self.assertIn(receipt['limitation'], soup.select_one('.review-reason').get_text())

    def test_researched_raw_pair_is_oriented_once_and_not_replaced_by_derived_odds(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('claims_auditor', ROOT / 'verification-4901f43e/audit_published_claims.py')
        auditor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auditor)
        frozen = json.loads((ROOT / 'research/session-ac4743a3/k27-inventory-2026-10-22.json').read_text())
        row = core.normalize_fixtures([frozen['fixture']], {}, core.dt('2026-10-22T02:00:00Z'))[0]
        receipt = next(r for r in core.book_receipts() if r['id'] == 'egw-4yp_dlKtNl-nexora-k27')
        core.book_research_pick(row, [receipt], core.dt('2026-10-22T02:00:00Z'))
        q = row['evidence'][0]
        self.assertEqual(q['source_teams'], list(reversed(row['teams'])))
        replay = auditor.replay_row(row, q)
        self.assertAlmostEqual(replay[0], 0.8880605196798597, places=12)
        self.assertAlmostEqual(replay[0], row['probabilities'][0], places=12)
        q['decimal_odds'] = list(reversed(q['decimal_odds']))
        self.assertIsNone(auditor.replay_row(row, q))


class CombinedMethodTests(unittest.TestCase):
    def test_known_mirror_is_model_not_an_unknown_or_market(self):
        from scripts import coverage_contract, summary
        from tests.test_coverage_contract import snapshot, NOW
        data = snapshot()  # explicitly synthetic Alpha/Beta fixture, fixed clock
        row = data['matches'][0]
        row['method'] = 'model_vrs_mirror'
        row['evidence'][0].update(provider='HLTV Valve ranking (Valve points)', url='https://www.hltv.org/valve-ranking/teams')
        counts = summary.counts(data['matches'])
        self.assertEqual((counts['model'], counts['market'], counts['no_pick']), (1, 0, 0))
        self.assertEqual((coverage(data)['model'], coverage(data)['market'], coverage(data)['hltv_mirror_models']), (1, 0, 1))
        self.assertEqual(summary.METHOD_STEP['model_vrs_mirror'], 'model_vrs_mirror')
        contract = coverage_contract.inspect(data, NOW)
        self.assertEqual(contract['problems'], [])
        self.assertEqual((contract['counts']['model'], contract['counts']['market']), (1, 0))
        row['method'] = 'unregistered_method'
        self.assertTrue(coverage_contract.inspect(data, NOW)['problems'])

    def test_equal_verified_line_is_not_claimed_as_a_directional_pick(self):
        from scripts import summary
        c = summary.counts([{'state': 'open', 'method': 'exchange', 'probabilities': [.5, .5], 'pick': None}])
        self.assertEqual((c['priced'], c['market'], c['with_pick'], c['no_pick']), (1, 1, 0, 1))
        self.assertNotIn('Every one', summary.completeness_sentence(c))

    def test_mirror_only_board_never_attributes_hltv_page_to_official_monthly_file(self):
        # Minimal synthetic render input: no claim about a real team's points.
        q = {'provider': 'HLTV Valve ranking (Valve points)', 'url': 'https://www.hltv.org/valve-ranking/teams'}
        data = {'matches': [{'method': 'model_vrs_mirror', 'state': 'open', 'evidence': [q], 'probabilities': [.6, .4]}]}
        soup = BeautifulSoup(build.model_section(data), 'html.parser')
        official = soup.find('strong', string='Inputs (official):').parent.find('a')
        self.assertTrue(official['href'].startswith('https://github.com/ValveSoftware/'))
        self.assertIn('HLTV dated Valve ranking', build.quote_source(q))
        self.assertNotIn('official API', build.quote_source(q))


class ArchiveTests(unittest.TestCase):
    def test_exact_response_bytes_are_hash_checked_and_replayable(self):
        raw = b'{"official_response": true}\n'
        digest = hashlib.sha256(raw).hexdigest()
        snapshot = {'source_checks': [{'url': 'https://github.com/ValveSoftware/counter-strike_regional_standings', 'sha256': digest}]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / (digest + '.json')).write_bytes(raw)
            index = evidence_index(snapshot, root, root / 'archive')
            archived = root / 'archive' / (digest + '.json.gz')
            self.assertEqual(gzip.decompress(archived.read_bytes()), raw)
            self.assertEqual(index[0]['archive_status'], 'exact response bytes retained')
            (root / (digest + '.json')).write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                evidence_index(snapshot, root, root / 'archive')

    def test_a_missing_body_is_flagged_not_called_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            records = evidence_index({'source_checks': [{'sha256': 'missing', 'url': 'https://www.hltv.org/matches'}]}, directory, Path(directory) / 'out')
            self.assertIn('unverified', records[0]['archive_status'])

    def test_report_does_not_fill_blank_probabilities(self):
        data = json.loads(CAPTURE.read_text())
        result = coverage(data)
        self.assertGreater(result['research_only'], 0)
        self.assertGreater(result['unresolved'], 0)
        report = markdown(data)
        self.assertIn('Blank means unverified, never 50/50', report)
        self.assertIn('[Hotspawn](https://', report)


if __name__ == '__main__':
    unittest.main()
