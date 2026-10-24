"""Session 35c6e1e9: the publication-continuity audit, and the rule that keeps
it advisory.

What had to be provable, and how it is proven here
--------------------------------------------------
1. The auditor's verdict comes from the sources it read, never from a value the
   pipeline asserted about itself. Each rule is exercised on a good input and on
   a deliberately corrupted one, because a check that cannot fail is decoration.
2. An *undecidable* state is reported as undecidable. Offline, the run history
   is not read and the published receipt is not read; claiming "frozen" there
   would make this auditor red for a reason nobody can act on, and claiming
   "current" would be the silence that let the 2026-10-24 outage run 17.7 h.
3. This auditor is never wired into the merge gate. It reads wall-clock
   staleness, so a committed baseline older than its own evidence window is
   normal between refreshes. On 2026-10-23/24 two snapshot-coupled assertions
   in ``tests/test_session_0cc1138a.py`` did exactly that and held every
   scheduled publication for 17.7 h; the pin below is the guard against this
   module becoming the next one.
4. The measured outage is recorded as a dated receipt, so the report cites
   official run and step identifiers rather than prose.
"""
import datetime
import json
import pathlib
import unittest

from scripts import verify_35c6e1e9 as A

ROOT = pathlib.Path(__file__).resolve().parents[1]
NOW = datetime.datetime(2026, 10, 24, 5, 33, tzinfo=datetime.timezone.utc)
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())


def stamp(minutes_ago):
    return (NOW - datetime.timedelta(minutes=minutes_ago)).strftime('%Y-%m-%dT%H:%M:%SZ')


def live_receipt(minutes_ago=30, revision='deadbeef'):
    return {'revision': revision, 'built_at': stamp(minutes_ago),
            'snapshot_generated_at': stamp(minutes_ago), 'rows': 90}


def run(conclusion='success', created=60, sha='5d56f35e' + '0' * 32, event='schedule',
        status='completed', run_id=1):
    return {'id': run_id, 'event': event, 'status': status, 'conclusion': conclusion,
            'created_at': stamp(created), 'updated_at': stamp(created + 2),
            'head_sha': sha, 'html_url': 'https://github.com/o/r/actions/runs/%d' % run_id}


def codes(findings):
    return [f['code'] for f in findings]


class SnapshotWindow(unittest.TestCase):
    def test_a_live_snapshot_inside_its_window_passes(self):
        found = A.check_snapshot_age(live_receipt(30), 8, NOW)
        self.assertEqual(codes(found), ['snapshot_inside_evidence_window'])
        self.assertEqual(found[0]['severity'], 'ok')

    def test_a_live_snapshot_outside_its_window_is_proof_of_a_frozen_board(self):
        # The measured 2026-10-24 state: 1066 min against a stated 8 h TTL.
        found = A.check_snapshot_age(live_receipt(1066), 8, NOW)
        self.assertEqual(codes(found), ['snapshot_outside_evidence_window'])
        self.assertEqual(found[0]['severity'], 'frozen')
        self.assertIn('every open pick is withheld', found[0]['detail'])
        self.assertAlmostEqual(found[0]['age_minutes'], 1066, delta=1)
        self.assertEqual(found[0]['window_minutes'], 480)

    def test_a_stale_committed_baseline_is_a_flag_not_a_proof(self):
        # Offline the published receipt was never read, so an old committed
        # baseline cannot prove the public site is frozen. Reporting it as frozen
        # is how an advisory auditor becomes a deadlocking merge gate.
        found = A.check_snapshot_age(live_receipt(1066), 8, NOW, receipt_is_live=False)
        self.assertEqual(codes(found), ['committed_baseline_outside_evidence_window'])
        self.assertEqual(found[0]['severity'], 'flag')
        self.assertIn('not proof the live site is frozen', found[0]['detail'])

    def test_an_unreadable_timestamp_is_never_a_guess(self):
        self.assertEqual(A.check_snapshot_age({}, 8, NOW)[0]['code'], 'receipt_unreadable')
        self.assertEqual(A.check_snapshot_age({'snapshot_generated_at': 'not a time'}, 8, NOW)[0]['code'],
                         'receipt_unreadable')
        self.assertEqual(A.check_snapshot_age(None, 8, NOW)[0]['severity'], 'frozen')
        # Offline the same unreadable state is undecidable, not proof.
        self.assertEqual(A.check_snapshot_age(None, 8, NOW, receipt_is_live=False)[0]['severity'], 'flag')

    def test_the_window_comes_from_the_snapshots_own_ttl(self):
        self.assertEqual(SNAPSHOT['stale_after_hours'], 8)
        found = A.check_snapshot_age(live_receipt(481), SNAPSHOT['stale_after_hours'], NOW)
        self.assertEqual(found[0]['code'], 'snapshot_outside_evidence_window')
        self.assertEqual(A.check_snapshot_age(live_receipt(479), SNAPSHOT['stale_after_hours'], NOW)[0]['code'],
                         'snapshot_inside_evidence_window')


class PublishChain(unittest.TestCase):
    def test_a_green_chain_passes(self):
        found = A.check_publish_chain([run('success', 20)], NOW)
        self.assertEqual(codes(found), ['publish_chain_green'])

    def test_an_in_flight_run_is_not_a_red_chain(self):
        found = A.check_publish_chain([run(created=20, status='in_progress', conclusion=None),
                                       run('success', 200)], NOW)
        self.assertIn('publish_chain_in_flight', codes(found))
        self.assertNotIn('publish_chain_red', codes(found))

    def test_consecutive_failures_on_one_commit_are_frozen_and_name_the_commit(self):
        runs = [run('failure', 60 + 150 * i, run_id=40062143026 + i) for i in range(5)]
        found = A.check_publish_chain(runs, NOW)
        red = next(f for f in found if f['code'] == 'publish_chain_red')
        self.assertEqual(red['severity'], 'frozen')
        self.assertEqual(red['streak'], 5)
        self.assertTrue(red['head_sha'].startswith('5d56f35e'))
        self.assertIn('one unmoved commit 5d56f35e', red['detail'])
        self.assertEqual(len(red['failed_run_urls']), 5)
        self.assertEqual(red['failed_run_ids'][0], 40062143026)

    def test_a_streak_across_different_commits_is_a_flag_not_a_deadlock(self):
        runs = [run('failure', 60, sha='a' * 40), run('failure', 200, sha='b' * 40),
                run('success', 400)]
        red = next(f for f in A.check_publish_chain(runs, NOW) if f['code'] == 'publish_chain_red')
        self.assertEqual(red['severity'], 'flag', 'a moving main is retrying, not deadlocked')

    def test_an_unread_history_is_undecidable_offline(self):
        self.assertEqual(A.check_publish_chain([], NOW)[0]['code'], 'no_run_history')
        self.assertEqual(A.check_publish_chain([], NOW)[0]['severity'], 'frozen')
        found = A.check_publish_chain([], NOW, history_read=False)
        self.assertEqual(codes(found), ['run_history_not_read'])
        self.assertEqual(found[0]['severity'], 'flag')
        self.assertIn('undecidable', found[0]['detail'])

    def test_a_run_older_than_a_day_is_flagged_as_starved_delivery(self):
        found = A.check_publish_chain([run('success', 60 * 30)], NOW)
        self.assertIn('no_recent_run', codes(found))
        self.assertIn('scheduled delivery, not the cron expression', next(
            f for f in found if f['code'] == 'no_recent_run')['detail'])


class RowSources(unittest.TestCase):
    def open_only(self, **overrides):
        doc = {'matches': [dict(m, **overrides) for m in SNAPSHOT['matches'] if m['state'] == 'open']}
        return doc

    def test_the_committed_board_passes(self):
        found = A.check_row_sources(SNAPSHOT)
        self.assertEqual(codes(found), ['rows_sourced'])
        self.assertEqual(found[0]['open_rows'], 27)
        self.assertEqual(found[0]['with_pick'], 27)
        self.assertEqual(found[0]['with_probability'], 27)

    def test_a_row_losing_its_official_fixture_link_is_frozen(self):
        doc = self.open_only()
        doc['matches'][0]['source_url'] = 'http://insecure.example/match'
        found = A.check_row_sources(doc)
        self.assertIn('row_without_official_fixture_link', codes(found))
        self.assertIn(doc['matches'][0]['id'], next(
            f for f in found if f['code'] == 'row_without_official_fixture_link')['detail'])

    def test_evidence_outside_the_official_allowlist_is_flagged(self):
        doc = self.open_only()
        doc['matches'][0]['evidence'] = [{'url': 'https://random-blog.example/odds'}]
        found = A.check_row_sources(doc)
        self.assertIn('evidence_host_outside_allowlist', codes(found))
        self.assertIn('random-blog.example', next(
            f for f in found if f['code'] == 'evidence_host_outside_allowlist')['detail'])

    def test_a_subdomain_of_an_official_host_is_accepted(self):
        doc = self.open_only()
        doc['matches'][0]['evidence'] = [{'url': 'https://www.hltv.org/matches/2399086/x'}]
        self.assertNotIn('evidence_host_outside_allowlist', codes(A.check_row_sources(doc)))

    def test_a_row_with_neither_pick_nor_reason_is_the_reported_symptom(self):
        # "We don't have picks" is exactly this state, and it is the only one the
        # auditor treats as frozen rather than flaggable.
        doc = self.open_only()
        row = doc['matches'][0]
        row['pick'] = None
        row['reason'] = None
        row['attempts'] = []
        found = A.check_row_sources(doc)
        self.assertIn('row_with_neither_pick_nor_limitation', codes(found))

    def test_a_row_with_a_recorded_limitation_is_not_a_failure(self):
        doc = self.open_only()
        row = doc['matches'][0]
        row['pick'] = None
        row['probabilities'] = None
        row['attempts'] = [{'provider': 'Polymarket', 'status': 'unresolved',
                            'reason': 'No exact team-pair and UTC-start match'}]
        self.assertNotIn('row_with_neither_pick_nor_limitation', codes(A.check_row_sources(doc)))

    def test_an_empty_board_is_never_reported_as_fully_sourced(self):
        # "All zero open rows carry an official link" is a vacuous truth. A
        # vacuous pass is worse than no check, so an empty board reports itself.
        for doc in ({'matches': []}, {'matches': [{'id': '1', 'state': 'not_open'}]}, None, {}):
            found = A.check_row_sources(doc)
            self.assertNotIn('rows_sourced', codes(found), doc)
        found = A.check_row_sources({'matches': [{'id': '1', 'state': 'not_open'}]})
        self.assertEqual(codes(found), ['no_open_rows'])
        self.assertEqual(found[0]['severity'], 'flag')
        self.assertIn('This is not coverage', found[0]['detail'])


class PickReproduction(unittest.TestCase):
    def test_every_committed_pick_reproduces(self):
        self.assertEqual(codes(A.check_pick_is_the_larger_probability(SNAPSHOT)), ['picks_reproducible'])

    def test_a_flipped_pick_is_caught(self):
        doc = {'matches': [dict(m) for m in SNAPSHOT['matches'] if m['state'] == 'open']}
        row = doc['matches'][0]
        row['pick'] = row['teams'][1 - row['teams'].index(row['pick'])]
        found = A.check_pick_is_the_larger_probability(doc)
        self.assertEqual(found[0]['code'], 'pick_not_reproducible')
        self.assertIn('the larger probability is', found[0]['detail'])

    def test_probabilities_that_do_not_sum_to_one_are_caught(self):
        doc = {'matches': [dict(m) for m in SNAPSHOT['matches'] if m['state'] == 'open']}
        doc['matches'][0]['probabilities'] = [0.6, 0.6]
        self.assertIn('sum to', A.check_pick_is_the_larger_probability(doc)[0]['detail'])

    def test_unpriced_rows_are_skipped_not_invented(self):
        doc = {'matches': [{'id': 'x', 'state': 'open', 'teams': ['A', 'B'],
                            'probabilities': None, 'pick': 'A'}]}
        self.assertEqual(codes(A.check_pick_is_the_larger_probability(doc)), ['picks_reproducible'])


class VerdictAndExitCodes(unittest.TestCase):
    def test_a_current_board_is_current(self):
        result = A.audit(live_receipt(30), [run('success', 20)], SNAPSHOT, NOW)
        self.assertEqual(result['verdict'], 'current')
        self.assertTrue(result['current'])
        self.assertEqual(result['counts']['frozen'], 0)

    def test_a_frozen_board_is_frozen_and_carries_the_step_names(self):
        runs = [run('failure', 60 + 150 * i, run_id=40062143026 + i) for i in range(5)]
        steps = {str(40062143026 + i): ['Unit and independent failure-mode tests (verify-build)']
                 for i in range(5)}
        result = A.audit(live_receipt(1066), runs, SNAPSHOT, NOW, steps_by_run=steps)
        self.assertEqual(result['verdict'], 'frozen')
        self.assertFalse(result['current'])
        red = next(f for f in result['findings'] if f['code'] == 'publish_chain_red')
        self.assertIn('Unit and independent failure-mode tests', red['detail'])
        self.assertEqual(len(red['failed_steps']), 5)
        # Both independent proofs of the outage are present, not just one.
        self.assertIn('snapshot_outside_evidence_window', codes(result['findings']))

    def test_offline_is_honest_about_what_it_could_not_read(self):
        result = A.audit({'snapshot_generated_at': stamp(1066)}, [], SNAPSHOT, NOW,
                         receipt_is_live=False, history_read=False)
        self.assertFalse(any(f['severity'] == 'frozen' for f in result['findings']),
                         'offline must not claim proof it does not have')
        self.assertIn('run_history_not_read', codes(result['findings']))
        self.assertIn('committed_baseline_outside_evidence_window', codes(result['findings']))

    def test_the_ledger_links_every_run_it_cites(self):
        runs = [run('failure', 60 + 150 * i, run_id=40062143026 + i) for i in range(5)]
        steps = {'40062143026': ['Unit and independent failure-mode tests (verify-build)']}
        text = A.markdown(A.audit(live_receipt(1066), runs, SNAPSHOT, NOW, steps_by_run=steps))
        self.assertIn('https://github.com/o/r/actions/runs/40062143026', text)
        self.assertIn('Unit and independent failure-mode tests', text)
        self.assertIn('build-info.json', text)
        self.assertIn('data/latest.json', text)
        self.assertIn('FROZEN', text)

    def test_timestamps_are_parsed_or_none_never_guessed(self):
        self.assertIsNone(A.utc(None))
        self.assertIsNone(A.utc('yesterday'))
        self.assertIsNone(A.age_minutes('yesterday', NOW))
        self.assertAlmostEqual(A.age_minutes(stamp(90), NOW), 90, delta=0.01)


class NeverAMergeGate(unittest.TestCase):
    def test_pages_yml_does_not_invoke_this_auditor(self):
        # The 2026-10-23/24 outage was caused by snapshot-coupled assertions
        # running as a blocking publication gate. This module reads wall-clock
        # staleness and is advisory by design; if it ever appears in the
        # publication workflow the same deadlock returns.
        pages = (ROOT / '.github/workflows/pages.yml').read_text()
        self.assertNotIn('verify_35c6e1e9', pages)

    def test_the_auditor_documents_the_rule(self):
        self.assertIn('never be wired into the merge gate', A.__doc__)
        self.assertIn('17.7 h', A.__doc__)

    def test_the_module_never_writes_data_or_publishes(self):
        source = (ROOT / 'scripts/verify_35c6e1e9.py').read_text()
        for forbidden in ('scripts.build', 'scripts.refresh', 'publish_root_fallback',
                          'upload-pages-artifact', "method='PUT'", "method='DELETE'"):
            self.assertNotIn(forbidden, source, forbidden)


class MeasuredOutageReceipt(unittest.TestCase):
    """The committed receipt cites official identifiers, so the report is checkable."""

    # Dated on purpose. This is frozen evidence of a specific outage, not a
    # mutable file: once the board recovers the streak resets, and a test pinned
    # to a regenerated receipt would start asserting a history that no longer
    # happened. Reproduce with:
    #   python -m scripts.verify_35c6e1e9 --live --token $TOKEN \
    #     --output research/session-35c6e1e9/continuity-receipt-<NEW>.json
    RECEIPT = ROOT / 'research/session-35c6e1e9/continuity-receipt-OUTAGE-2026-10-24T0602Z.json'

    def test_the_receipt_records_the_five_failed_runs_and_their_step(self):
        self.assertTrue(self.RECEIPT.exists(), 'the dated outage receipt is committed evidence')
        data = json.loads(self.RECEIPT.read_text())
        self.assertEqual(data['mode'], 'live')
        red = next(f for f in data['findings'] if f['code'] == 'publish_chain_red')
        self.assertEqual(red['streak'], 5)
        self.assertTrue(red['head_sha'].startswith('5d56f35e'))
        self.assertEqual(set(red['failed_run_ids']),
                         {39956197341, 39998307424, 40025828846, 40042111432, 40062143026})
        for run_id, steps in red['failed_steps'].items():
            self.assertIn('Unit and independent failure-mode tests (verify-build)', steps, run_id)

    def test_the_receipt_records_what_the_sandbox_could_not_read(self):
        # The authoring sandbox cannot reach the Pages host, and that is recorded
        # rather than papered over: an unread source is a stated limitation.
        data = json.loads(self.RECEIPT.read_text())
        self.assertTrue(any('live build receipt unreadable' in p for p in data['source_problems']),
                        data['source_problems'])


if __name__ == '__main__':
    unittest.main()
