"""Provenance regression checks; no fixture IDs, dates or current counts pinned."""
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest

from scripts import audit_e3fe9518 as audit

ROOT = Path(__file__).resolve().parents[1]


class SourceAuthorityTests(unittest.TestCase):
    def test_exact_https_authority_only(self):
        for url in ['http://polymarket.com/event/a',
                    'https://polymarket.com.attacker.invalid/event/a',
                    'https://polymarket.com@attacker.invalid/event/a',
                    'https://user:secret@polymarket.com/event/a',
                    'https://polymarket.com:444/event/a',
                    'https://polymarket.com/event/a#pretend-verification',
                    'https://polymarket.com:invalid/event/a', None, 7]:
            with self.subTest(url=url):
                self.assertFalse(audit.secure_url(url, {'polymarket.com'}))
        self.assertTrue(audit.secure_url('https://polymarket.com/event/a', {'polymarket.com'}))

    def test_valve_repository_owner_is_not_inferred_from_filename(self):
        self.assertFalse(audit.valve_url('https://github.com/attacker/counter-strike_regional_standings/blob/main/model/fit.js'))
        self.assertFalse(audit.valve_url('https://github.com/ValveSoftware/counter-strike_regional_standings-fake/model/fit.js'))
        self.assertTrue(audit.valve_url('https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/model/fit.js'))

    def test_timezone_required(self):
        for value in ['2026-10-24T06:00:00', None, 'not-a-date']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit.moment(value)

    def test_an_operator_name_does_not_upgrade_listing_data(self):
        quote = {'provider': 'Polymarket', 'api_url': 'https://api.bo3.gg/api/v1/matches',
                 'url': 'https://polymarket.com/event/cs2-a-b'}
        self.assertEqual(audit.source_kind(quote), 'unrecognized')

    def test_a_bookmaker_link_does_not_verify_a_quote(self):
        self.assertFalse(audit.receipt_ok({'url': 'https://thunderpick.io/match/123'}))

    def test_methodology_does_not_upgrade_listing_inputs_to_operator_evidence(self):
        source = (ROOT / 'scripts/build.py').read_text()
        self.assertNotIn('Every accepted price retains the official operator’s raw fields', source)
        self.assertIn('publisher’s captured fields, source receipts and observation time', source)
        self.assertIn('a bookmaker link in a listing is not independent confirmation', source)
        self.assertIn('our derived estimates, not official forecasts', source)


class ReceiptAndClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads((ROOT / 'data/latest.json').read_text())

    def snapshot_with(self, method):
        snapshot = copy.deepcopy(self.snapshot)
        match = next((m for m in snapshot['matches'] if m.get('method') == method), None)
        if match is None:
            self.skipTest('This rotating board has no ' + method + ' row; synthetic authority tests still run')
        return snapshot, match

    def problems_after(self, method, mutate):
        snapshot, match = self.snapshot_with(method)
        mutate(snapshot, match)
        result = audit.inspect(snapshot)
        return result, next(r for r in result['rows'] if r['id'] == match['id'])

    def test_current_snapshot_has_no_unreplayed_or_untraced_row(self):
        result = audit.inspect(self.snapshot)
        self.assertEqual(result['errors'], [])
        self.assertEqual(len(result['rows']), len(self.snapshot['matches']))
        self.assertEqual(sum(result['counts'].values()), len(result['rows']))

    def test_snapshot_clock_is_explicitly_not_a_live_claim(self):
        result = audit.inspect(self.snapshot)
        self.assertEqual(result['clock_basis'], 'snapshot_generation_time_not_live')
        self.assertEqual(audit.moment(result['audit_clock']), audit.moment(self.snapshot['generated_at']))

    def test_expired_evidence_never_becomes_actionable_on_reaudit(self):
        result = audit.inspect(self.snapshot, '2099-01-01T00:00:00Z')
        self.assertEqual(result['actionable_at_audit_clock'], 0)
        self.assertTrue(all(not row['actionable_at_audit_clock'] for row in result['rows']))
        self.assertEqual(result['clock_basis'], 'explicit')

    def test_audit_is_read_only(self):
        before = copy.deepcopy(self.snapshot)
        audit.inspect(self.snapshot)
        self.assertEqual(self.snapshot, before)

    def test_operator_input_calculation_is_not_claimed_as_a_bookmaker_forecast(self):
        snapshot, match = self.snapshot_with('exchange')
        result = audit.inspect(snapshot)
        row = next(r for r in result['rows'] if r['id'] == match['id'])
        self.assertEqual(row['source_kind'], 'operator_market')
        self.assertEqual(row['primary_only_market_estimate'], match['probabilities'])
        self.assertIn('not a guarantee', ' '.join(row['limitations']))

    def test_listing_primary_only_values_stay_blank(self):
        snapshot, match = self.snapshot_with('bookmaker_fallback')
        if audit.source_kind(match['evidence'][0]) != 'third_party_listing':
            self.skipTest('This board uses direct operator odds instead of a listing')
        row = next(r for r in audit.inspect(snapshot)['rows'] if r['id'] == match['id'])
        self.assertIsNone(row['primary_only_market_estimate'])
        self.assertEqual(row['calculated_probability'], match['probabilities'])
        self.assertIn('not directly confirmed', ' '.join(row['limitations']))

    def test_models_are_never_classified_as_primary_market_odds(self):
        for method in ['model_vrs', 'model_vrs_mirror']:
            with self.subTest(method=method):
                snapshot, match = self.snapshot_with(method)
                row = next(r for r in audit.inspect(snapshot)['rows'] if r['id'] == match['id'])
                self.assertIsNone(row['primary_only_market_estimate'])
                self.assertIn('model', row['source_kind'])

    def test_changed_quote_receipt_hash_fails_closed(self):
        result, row = self.problems_after('exchange', lambda s, m:
            m['evidence'][0]['source_receipts'][0].update(sha256='f' * 64))
        self.assertTrue(result['errors'])
        self.assertIn('Quote receipt does not match', ' '.join(row['problems']))
        self.assertIsNone(row['primary_only_market_estimate'])
        self.assertIsNone(row['calculated_probability'])

    def test_changed_receipt_byte_size_fails(self):
        result, row = self.problems_after('exchange', lambda s, m:
            m['evidence'][0]['source_receipts'][0].update(bytes=1))
        self.assertIn('hash/size/time', ' '.join(row['problems']))

    def test_unsuccessful_receipt_cannot_verify_a_quote(self):
        result, row = self.problems_after('exchange', lambda s, m:
            m['evidence'][0]['source_receipts'][0].update(status='error', http_status=403))
        self.assertIn('No successful source receipt', ' '.join(row['problems']))

    def test_forged_primary_receipt_on_aggregator_host_fails(self):
        snapshot, match = self.snapshot_with('exchange')
        receipt = match['evidence'][0]['source_receipts'][0]
        receipt['url'] = 'https://api.bo3.gg/api/v1/matches'
        snapshot['source_checks'].append(copy.deepcopy(receipt))
        row = next(r for r in audit.inspect(snapshot)['rows'] if r['id'] == match['id'])
        self.assertIn('different source authority', ' '.join(row['problems']))

    def test_changed_quote_observation_fails(self):
        result, row = self.problems_after('exchange', lambda s, m:
            m['evidence'][0].update(observed_at='2026-01-01T00:00:00Z'))
        self.assertTrue(result['errors'])
        self.assertIn('Quote observation does not match', ' '.join(row['problems']))

    def test_ranking_page_hash_bound_to_its_receipt(self):
        result, row = self.problems_after('model_vrs_mirror', lambda s, m:
            m['evidence'][0].update(ranking_page_sha256='f' * 64))
        self.assertIn('Ranking page hash', ' '.join(row['problems']))

    def test_untrusted_formula_link_fails(self):
        result, row = self.problems_after('model_vrs', lambda s, m:
            m['evidence'][0].update(formula_source='https://github.com/attacker/model/blob/main/model/fit.js'))
        self.assertIn('official Valve file', ' '.join(row['problems']))

    def test_primary_model_values_match_actual_hash_bound_valve_file(self):
        snapshot, match = self.snapshot_with('model_vrs')
        if match['evidence'][0]['api_url'] not in audit.archived_standings():
            self.skipTest('No archived copy for this newer official file; auditor reports unverified')
        row = next(r for r in audit.inspect(snapshot)['rows'] if r['id'] == match['id'])
        self.assertTrue(row['official_standings_input_crosscheck'])

    def test_self_consistent_fabricated_points_do_not_pass_source_verification(self):
        snapshot, match = self.snapshot_with('model_vrs')
        quote = match['evidence'][0]
        if quote['api_url'] not in audit.archived_standings():
            self.skipTest('No archived copy for this newer official file')
        quote['points'][0] += 100
        g = 1 / math.sqrt(1 + 3 * (math.log(10) / 400) ** 2 * 75 ** 2 / math.pi ** 2)
        raw = 1 / (1 + 10 ** (-g * (quote['points'][0] - quote['points'][1]) / 400))
        first = .5 + .7986 * (raw - .5)
        p = [first, 1 - first]
        quote.update(raw_expected=[raw, 1 - raw], probabilities=p)
        match.update(probabilities=p, fair_odds=[1 / x for x in p],
                     pick=match['teams'][0 if p[0] > p[1] else 1])
        row = next(r for r in audit.inspect(snapshot)['rows'] if r['id'] == match['id'])
        self.assertIn('differ from official standings', ' '.join(row['problems']))
        self.assertFalse(row['official_standings_input_crosscheck'])
        self.assertIsNone(row['calculated_probability'])

    def test_changed_primary_document_hash_is_rejected(self):
        snapshot, match = self.snapshot_with('model_vrs')
        quote = match['evidence'][0]
        documents = {quote['api_url']: b'Fabricated primary-source copy'}
        row = next(r for r in audit.inspect(snapshot, standings_documents=documents)['rows'] if r['id'] == match['id'])
        self.assertIn('file hash does not match', ' '.join(row['problems']))

    def test_missing_primary_document_is_unverified_not_invented(self):
        snapshot, match = self.snapshot_with('model_vrs')
        row = next(r for r in audit.inspect(snapshot, standings_documents={})['rows'] if r['id'] == match['id'])
        self.assertIsNone(row['official_standings_input_crosscheck'])
        self.assertIn('cross-check is unverified', ' '.join(row['limitations']))

    def test_missing_fixture_provenance_fails(self):
        result, row = self.problems_after('exchange', lambda s, m: m.update(fixture_sources=[]))
        self.assertIn('Fixture HTTP provenance missing', row['problems'])

    def test_forged_fixture_receipt_fails(self):
        result, row = self.problems_after('exchange', lambda s, m:
            m['fixture_sources'][0].update(sha256='0' * 64))
        self.assertIn('Fixture receipt does not match', ' '.join(row['problems']))

    def test_omitted_hltv_fallback_attempt_fails(self):
        result, row = self.problems_after('model_vrs', lambda s, m:
            m.update(attempts=[a for a in m['attempts'] if a['provider'] not in audit.HLTV_STEPS]))
        self.assertIn('HLTV-first', ' '.join(row['problems']))

    def test_reordered_book_before_hltv_fails(self):
        snapshot, match = self.snapshot_with('model_vrs')
        match['attempts'].sort(key=lambda a: a.get('provider') not in audit.BOOK_STEPS)
        row = next(r for r in audit.inspect(snapshot)['rows'] if r['id'] == match['id'])
        self.assertIn('HLTV-first', ' '.join(row['problems']))

    def test_tampered_probabilities_fail_independent_replay(self):
        result, row = self.problems_after('exchange', lambda s, m: m.update(probabilities=[.5, .5]))
        self.assertTrue(row['problems'])
        self.assertIsNone(row['calculated_probability'])

    def test_official_fixture_source_is_required_on_every_row(self):
        snapshot = copy.deepcopy(self.snapshot)
        snapshot['matches'][0]['source_url'] = 'https://example.invalid/match/1'
        result = audit.inspect(snapshot)
        self.assertIn('Official Hotspawn HTTPS fixture link missing', result['rows'][0]['problems'])

    def test_wrong_tenant_feed_fails(self):
        result, row = self.problems_after('exchange', lambda s, m:
            m.update(feed_url=audit.FEED.replace('tenantId=1', 'tenantId=2')))
        self.assertIn('Official scoped CS2 feed link changed', row['problems'])

    def test_markdown_includes_all_rows_and_never_fills_unknown_primary_values(self):
        result = audit.inspect(self.snapshot)
        text = audit.markdown(result)
        for match in self.snapshot['matches']:
            self.assertIn(f"[{match['id']}]({match['source_url']})", text)
        self.assertIn('Blank never means 50/50', text)
        self.assertIn('not the live picks page', text)

    def test_cli_writes_digest_of_exact_input(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            path = ROOT / 'data/latest.json'
            self.assertEqual(audit.main(['--data', str(path), '--out', str(out)]), 0)
            result = json.loads((out / 'source-audit.json').read_text())
            self.assertEqual(result['snapshot_sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertTrue((out / 'source-audit.md').exists())


class PublicationExpectationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('live_expectation_e3fe9518', ROOT / 'verification-e3fe9518/live_check.py')
        cls.live = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.live)

    def test_unmerged_branch_can_audit_production_but_cannot_claim_its_release_live(self):
        self.assertEqual(self.live.expectation('refs/heads/arena/e3fe9518-maltaproj4', b'branch', b'production'),
                         (b'production', 'observed_production_not_this_unmerged_branch'))
        with self.assertRaises(ValueError):
            self.live.expectation('refs/heads/arena/e3fe9518-maltaproj4', b'branch')

    def test_main_and_local_checks_require_the_merged_build_or_a_newer_release(self):
        for ref in ('refs/heads/main', None):
            self.assertEqual(self.live.expectation(ref, b'merged', b'previously-published'),
                             (b'merged', 'this_merged_main_build_or_a_coherent_newer_release'))

    def test_annotation_receipt_cannot_inject_workflow_commands(self):
        command = self.live.receipt_annotation({'untrusted': '%0A\n::error::not a command'})
        self.assertTrue(command.startswith('::notice title=e3fe9518-public-source-receipt::'))
        self.assertNotIn('\n', command)
        self.assertIn('%250A', command)
        self.assertTrue(self.live.receipt_annotation({'verified': False}, failed=True).startswith('::error '))

    def test_new_self_consistent_manifest_cannot_replace_the_one_actually_verified(self):
        old_data, new_data = b'old snapshot', b'new snapshot'
        manifest = lambda data: json.dumps({'files': {'data/latest.json': hashlib.sha256(data).hexdigest()}}).encode()
        old, new = manifest(old_data), manifest(new_data)
        same = self.live.public_read_binding(old, old, old_data)
        self.assertTrue(same['manifest_unchanged_since_byte_verification'])
        self.assertTrue(same['snapshot_matches_adjacent_manifest'])
        race = self.live.public_read_binding(old, new, new_data)
        self.assertFalse(race['manifest_unchanged_since_byte_verification'])
        self.assertTrue(race['snapshot_matches_adjacent_manifest'])
        corrupt = self.live.public_read_binding(old, old, new_data)
        self.assertFalse(corrupt['snapshot_matches_adjacent_manifest'])
        missing = self.live.public_read_binding(None, None, new_data)
        self.assertFalse(missing['manifest_unchanged_since_byte_verification'])
        self.assertFalse(missing['snapshot_matches_adjacent_manifest'])


    def target_fixture(self):
        raw = b'{"built_at":"fixture-only","files":{}}'
        target = {'repository': 'buffedlizard55-lab/MaltaProj4',
                  'application_release_commit': 'a' * 40, 'target_main_commit': 'b' * 40,
                  'target_manifest_sha256': hashlib.sha256(raw).hexdigest()}
        return target, raw

    def test_explicit_merged_target_proves_both_ancestries_and_the_git_manifest(self):
        target, raw = self.target_fixture()
        calls = []
        def git(args):
            calls.append(args)
            return raw if args[1] == 'show' else b''
        self.assertEqual(self.live.resolve_merged_release_target(target, git), raw)
        self.assertIn(['git', 'merge-base', '--is-ancestor', 'a' * 40, 'b' * 40], calls)
        self.assertIn(['git', 'merge-base', '--is-ancestor', 'b' * 40, 'origin/main'], calls)

    def test_unmerged_target_or_missing_release_ancestor_is_refused(self):
        target, raw = self.target_fixture()
        for failed_tip in ('b' * 40, 'origin/main'):
            with self.subTest(failed_tip=failed_tip):
                def git(args):
                    if args[1] == 'merge-base' and args[-1] == failed_tip:
                        raise self.live.subprocess.CalledProcessError(1, args)
                    return raw if args[1] == 'show' else b''
                with self.assertRaisesRegex(ValueError, 'already merged'):
                    self.live.resolve_merged_release_target(target, git)

    def test_branch_declared_manifest_cannot_replace_the_main_git_object(self):
        target, raw = self.target_fixture()
        def git(args):
            return raw + b' ' if args[1] == 'show' else b''
        with self.assertRaisesRegex(ValueError, 'manifest bytes'):
            self.live.resolve_merged_release_target(target, git)

    def test_invalid_target_or_repository_is_rejected_before_any_git_call(self):
        target, raw = self.target_fixture()
        for field, value in [('repository', 'elsewhere/unknown'),
                             ('target_main_commit', '--malicious-ref'),
                             ('target_manifest_sha256', 'not-a-digest')]:
            with self.subTest(field=field):
                bad = dict(target, **{field: value})
                def git(args):
                    self.fail('Malformed target reached git')
                with self.assertRaises(ValueError):
                    self.live.resolve_merged_release_target(bad, git)


class LiveComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('live_check_e3fe9518', ROOT / 'verification-e3fe9518/live_check.py')
        cls.live = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.live)
        snapshot = json.loads((ROOT / 'data/latest.json').read_text())
        match = next((m for m in snapshot['matches'] if m.get('method') == 'exchange'), None)
        if match is None:
            raise unittest.SkipTest('No exchange row on this rotating board')
        cls.quote = match['evidence'][0]

    def test_exact_current_operator_inputs_can_be_confirmed(self):
        result = self.live.compare_operator_record(self.quote, copy.deepcopy(self.quote['raw']))
        self.assertTrue(result['snapshot_inputs_confirmed_now'])

    def test_changed_live_prices_do_not_renew_archived_values(self):
        payload = copy.deepcopy(self.quote['raw'])
        payload['outcomePrices'] = ['0.501', '0.499']
        result = self.live.compare_operator_record(self.quote, payload)
        self.assertTrue(result['identity_matches'])
        self.assertFalse(result['snapshot_inputs_confirmed_now'])
        self.assertIn('not re-labelled as current', result['limitation'])

    def test_different_market_id_is_not_an_identity_match(self):
        payload = copy.deepcopy(self.quote['raw'])
        payload['id'] = 'different-market'
        self.assertFalse(self.live.compare_operator_record(self.quote, payload)['identity_matches'])

    def test_suspended_market_is_not_a_current_confirmation(self):
        payload = copy.deepcopy(self.quote['raw'])
        payload['acceptingOrders'] = False
        self.assertFalse(self.live.compare_operator_record(self.quote, payload)['snapshot_inputs_confirmed_now'])

    def test_wrong_start_or_outcome_order_is_not_inferred(self):
        for field, value in [('gameStartTime', '2099-01-01T00:00:00Z'),
                             ('outcomes', ['Unknown A', 'Unknown B']),
                             ('sportsMarketType', 'map_winner')]:
            with self.subTest(field=field):
                payload = copy.deepcopy(self.quote['raw'])
                payload[field] = value
                self.assertFalse(self.live.compare_operator_record(self.quote, payload)['identity_matches'])



class CurrentSnapshotAuthorityTests(unittest.TestCase):
    def test_every_current_row_is_source_verified_without_a_fixed_live_count(self):
        snapshot = json.loads((ROOT / 'data' / 'latest.json').read_text())
        result = audit.inspect(snapshot, snapshot.get('built_at') or snapshot['generated_at'])
        self.assertEqual(result['errors'], [])
        self.assertEqual(len(result['rows']), len(snapshot['matches']))
        self.assertEqual({row['id'] for row in result['rows']},
                         {str(row['id']) for row in snapshot['matches']})

if __name__ == '__main__':
    unittest.main()
