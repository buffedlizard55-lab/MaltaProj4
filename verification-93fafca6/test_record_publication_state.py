"""Tests for the publication-state recorder: which publisher is serving the site.

Offline and deterministic. The API records are passed in as plain dicts shaped
exactly like ``request()`` returns them, so no network call is made except in the
one test that proves ``request()`` never raises on an unreachable host.

Run: ``python -m unittest discover -s verification-93fafca6 -p 'test_*.py' -v``
"""
import datetime
import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    'record_publication_state', Path(__file__).with_name('record_publication_state.py'))
rps = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rps)

NOW = datetime.datetime(2026, 10, 21, 20, 42, 15, tzinfo=datetime.timezone.utc)
MAIN = '884f36eb27b11865d2f36577f9e1ea8ec55bf67e'
FALLBACK = '88b1b2c3b96954e64f614ad08342cc74aeb289fe'

PAGES_LEGACY = {'url': 'https://api.github.com/repos/o/r/pages', 'method': 'GET', 'status': 200,
                'error': None, 'body': {'build_type': 'legacy', 'status': 'built',
                                       'source': {'branch': 'main', 'path': '/'},
                                       'html_url': 'https://o.github.io/r/'}}
PAGES_WORKFLOW = {'status': 200, 'error': None,
                  'body': {'build_type': 'workflow', 'status': 'built',
                           'source': None, 'html_url': 'https://o.github.io/r/'}}
BUILDS = {'status': 200, 'error': None, 'body': [
    {'created_at': '2026-10-21T20:35:17Z', 'status': 'building', 'commit': MAIN},
    {'created_at': '2026-10-21T20:12:40Z', 'status': 'built', 'commit': '63f4172cb50aff8b'},
]}
RUNS = {'status': 200, 'error': None, 'body': {'workflow_runs': [
    {'id': 1, 'event': 'push', 'status': 'completed', 'conclusion': 'success',
     'run_started_at': '2026-10-21T20:12:41Z', 'html_url': 'https://x/1'},
    {'id': 2, 'event': 'schedule', 'status': 'completed', 'conclusion': 'failure',
     'run_started_at': '2026-10-21T19:16:10Z', 'html_url': 'https://x/2'},
]}}
COMMITTED = {'revision': FALLBACK, 'built_at': '2026-10-18T00:52:19Z',
             'snapshot_generated_at': '2026-10-18T00:52:19.597023Z', 'rows': 98}


def live_receipt(revision, snapshot_at, built_at='2026-10-21T19:57:45Z', rows=76, status=200):
    return {'status': status, 'error': None if status == 200 else 'HTTP %s' % status,
            'body': {'revision': revision, 'built_at': built_at,
                     'snapshot_generated_at': snapshot_at, 'rows': rows} if status == 200 else None}


def table_blocks(text):
    """Group consecutive markdown table lines into (header, rows) blocks."""
    blocks, current = [], []
    for line in text.splitlines():
        if line.startswith('|'):
            current.append(line)
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return blocks


def assert_tables_well_formed(testcase, text):
    """Every table keeps one column count, and its second line is a separator."""
    blocks = table_blocks(text)
    testcase.assertTrue(blocks, 'the report renders no markdown table at all')
    for block in blocks:
        testcase.assertGreaterEqual(len(block), 2, block)
        testcase.assertIn('---', block[1])
        columns = block[0].count('|')
        for line in block:
            testcase.assertEqual(line.count('|'), columns,
                                 'ragged table row: %r (expected %d pipes)' % (line, columns))


class TestClassify(unittest.TestCase):
    def test_artifact_for_current_main(self):
        self.assertEqual(rps.classify(MAIN, FALLBACK, MAIN), 'artifact-current-main')

    def test_committed_root_fallback_being_served(self):
        self.assertEqual(rps.classify(FALLBACK, FALLBACK, MAIN), 'committed-root-fallback')

    def test_artifact_for_an_older_commit(self):
        self.assertEqual(rps.classify('47f230bd83c2', FALLBACK, MAIN), 'artifact-older-commit')

    def test_unreadable_receipt_is_unknown_not_guessed(self):
        self.assertEqual(rps.classify(None, FALLBACK, MAIN), 'unknown')
        self.assertEqual(rps.classify(None, None, None), 'unknown')

    def test_a_fallback_revision_that_is_also_head_is_not_an_overwrite(self):
        # If the root fallback were re-staged from the current build, the served
        # revision would equal HEAD and the artifact is what is being served.
        self.assertEqual(rps.classify(MAIN, MAIN, MAIN), 'artifact-current-main')


class TestSummarize(unittest.TestCase):
    def test_the_observed_legacy_overwrite(self):
        state = rps.summarize(PAGES_LEGACY, BUILDS, RUNS,
                              live_receipt(FALLBACK, '2026-10-18T00:52:19.597023Z',
                                           built_at='2026-10-18T00:52:19Z', rows=98),
                              COMMITTED, MAIN, NOW)
        self.assertEqual(state['serving'], 'committed-root-fallback')
        self.assertTrue(state['legacy_overwrite_detected'])
        self.assertTrue(state['outside_evidence_window'])
        self.assertGreater(state['live_receipt']['snapshot_age_hours'], 91)
        self.assertTrue(state['dual_publisher_race_possible'])
        self.assertEqual(state['pages_configuration']['build_type'], 'legacy')
        self.assertEqual(state['pages_configuration']['source_branch'], 'main')
        self.assertEqual(state['last_successful_publication'], 'https://x/1')
        self.assertEqual(len(state['pages_builds']), 2)
        self.assertEqual(state['newest_pages_build']['commit'], MAIN)

    def test_a_fresh_root_fallback_is_not_called_a_stale_overwrite(self):
        """pages.yml now re-stages the committed root from the verified build.

        Observed at 2026-10-21T21:52:09Z: the legacy publisher was serving the
        committed root, and that root carried a 0.06 h old verified snapshot, so
        both publication paths served fresh bytes. Naming the publisher is a
        classification; calling it a stale-board event would be a claim the
        timestamps do not support.
        """
        state = rps.summarize(PAGES_LEGACY, BUILDS, RUNS,
                              live_receipt(FALLBACK, '2026-10-21T21:22:00.000000Z',
                                           built_at='2026-10-21T21:22:01Z', rows=75),
                              COMMITTED, MAIN, NOW)
        self.assertEqual(state['serving'], 'committed-root-fallback')
        self.assertTrue(state['legacy_overwrite_detected'])
        self.assertFalse(state['outside_evidence_window'])
        self.assertFalse(state['legacy_overwrote_with_a_stale_board'])
        md = rps.to_markdown(state)
        self.assertIn('inside its evidence window', md)
        self.assertNotIn('outside its 8-hour evidence window**', md)

    def test_a_stale_root_fallback_is_called_what_the_timestamps_show(self):
        state = rps.summarize(PAGES_LEGACY, BUILDS, RUNS,
                              live_receipt(FALLBACK, '2026-10-18T00:52:19.597023Z',
                                           built_at='2026-10-18T00:52:19Z', rows=98),
                              COMMITTED, MAIN, NOW)
        self.assertTrue(state['legacy_overwrote_with_a_stale_board'])
        self.assertIn('outside its 8-hour evidence window**', rps.to_markdown(state))

    def test_an_unreadable_age_is_never_assumed_fresh(self):
        state = rps.summarize(PAGES_LEGACY, BUILDS, RUNS,
                              live_receipt(FALLBACK, 'not-a-timestamp', rows=98),
                              COMMITTED, MAIN, NOW)
        self.assertIsNone(state['outside_evidence_window'])
        self.assertFalse(state['legacy_overwrote_with_a_stale_board'])
        md = rps.to_markdown(state)
        self.assertIn('could not be read', md)
        self.assertNotIn('inside its evidence window', md)

    def test_a_fresh_artifact_is_not_an_overwrite(self):
        state = rps.summarize(PAGES_LEGACY, BUILDS, RUNS,
                              live_receipt(MAIN, '2026-10-21T19:57:45.210692Z'),
                              COMMITTED, MAIN, NOW)
        self.assertEqual(state['serving'], 'artifact-current-main')
        self.assertFalse(state['legacy_overwrite_detected'])
        self.assertFalse(state['outside_evidence_window'])
        # legacy mode still means the race can happen again on the next push
        self.assertTrue(state['dual_publisher_race_possible'])

    def test_switching_pages_to_workflow_removes_the_race(self):
        state = rps.summarize(PAGES_WORKFLOW, BUILDS, RUNS,
                              live_receipt(MAIN, '2026-10-21T19:57:45.210692Z'),
                              COMMITTED, MAIN, NOW)
        self.assertFalse(state['dual_publisher_race_possible'])
        self.assertEqual(state['pages_configuration']['build_type'], 'workflow')

    def test_an_unreadable_live_receipt_is_recorded_not_inferred(self):
        state = rps.summarize(PAGES_LEGACY, BUILDS, RUNS, live_receipt(None, None, status=None),
                              COMMITTED, MAIN, NOW)
        self.assertEqual(state['serving'], 'unknown')
        self.assertIsNone(state['live_receipt']['snapshot_age_hours'])
        self.assertIsNone(state['outside_evidence_window'])
        self.assertFalse(state['legacy_overwrite_detected'])

    def test_missing_inputs_do_not_raise(self):
        state = rps.summarize(None, None, None, None, None, None, NOW)
        self.assertEqual(state['serving'], 'unknown')
        self.assertEqual(state['pages_builds'], [])
        self.assertEqual(state['publication_runs'], [])
        self.assertIsNone(state['newest_pages_build'])
        self.assertIsNone(state['last_successful_publication'])

    def test_the_fix_attempt_is_carried_through_verbatim(self):
        attempt = {'method': 'PUT', 'url': 'https://api.github.com/repos/o/r/pages',
                   'status': 403, 'error': 'HTTP 403', 'body': 'Resource not accessible by integration',
                   'accepted_permissions': 'pages=write,administration=write',
                   'request_id': '806E:285EA4:6F3A8:B63A5:6AD923A9',
                   'payload': {'build_type': 'workflow'}}
        state = rps.summarize(PAGES_LEGACY, BUILDS, RUNS,
                              live_receipt(FALLBACK, '2026-10-18T00:52:19.597023Z'),
                              COMMITTED, MAIN, NOW, fix_attempt=attempt)
        self.assertEqual(state['owner_fix_attempt']['status'], 403)
        self.assertEqual(state['owner_fix_attempt']['accepted_permissions'],
                         'pages=write,administration=write')


class TestMarkdown(unittest.TestCase):
    def test_the_overwrite_report_names_both_publishers_and_links_the_api(self):
        state = rps.summarize(PAGES_LEGACY, BUILDS, RUNS,
                              live_receipt(FALLBACK, '2026-10-18T00:52:19.597023Z', rows=98),
                              COMMITTED, MAIN, NOW)
        text = rps.to_markdown(state)
        self.assertIn('`build_type: legacy`, source `main:/`', text)
        self.assertIn('**the legacy root fallback is serving and the board it carries is outside '
                      'its 8-hour evidence window**', text)
        self.assertIn('https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages', text)
        self.assertIn('| 2026-10-21T20:35:17Z | building |', text)
        self.assertIn('https://x/1', text)
        assert_tables_well_formed(self, text)

    def test_an_unreadable_receipt_still_renders_a_complete_table(self):
        state = rps.summarize(PAGES_LEGACY, BUILDS, RUNS, live_receipt(None, None, status=None),
                              COMMITTED, MAIN, NOW)
        text = rps.to_markdown(state)
        self.assertIn('unreadable (HTTP `None`)', text)
        assert_tables_well_formed(self, text)

    def test_the_fix_attempt_section_only_appears_when_attempted(self):
        base = rps.summarize(PAGES_LEGACY, BUILDS, RUNS,
                             live_receipt(MAIN, '2026-10-21T19:57:45.210692Z'), COMMITTED, MAIN, NOW)
        self.assertNotIn('Owner-level fix attempt', rps.to_markdown(base))
        attempted = rps.summarize(PAGES_LEGACY, BUILDS, RUNS,
                                  live_receipt(MAIN, '2026-10-21T19:57:45.210692Z'), COMMITTED, MAIN,
                                  NOW, fix_attempt={'method': 'PUT', 'url': 'u', 'status': 403,
                                                    'error': 'HTTP 403', 'body': 'denied',
                                                    'accepted_permissions': 'pages=write',
                                                    'request_id': 'R1',
                                                    'payload': {'build_type': 'workflow'}})
        text = rps.to_markdown(attempted)
        self.assertIn('Owner-level fix attempt', text)
        self.assertIn('**403**', text)
        self.assertIn('pages=write', text)
        self.assertIn('Settings → Pages', text)


class TestOwnerFixOutcome(unittest.TestCase):
    """The fix attempt must be proven by a re-read, never by the status code alone."""

    ATTEMPT_OK = {'method': 'PUT', 'url': 'u', 'status': 200, 'error': None, 'body': {},
                  'accepted_permissions': 'pages=write', 'request_id': 'R2',
                  'payload': {'build_type': 'workflow'}}
    AFTER = {'status': 200, 'error': None,
             'body': {'build_type': 'workflow', 'status': 'built', 'source': None}}

    def test_a_successful_switch_removes_the_race_forward_looking(self):
        state = rps.summarize(PAGES_LEGACY, BUILDS, RUNS,
                              live_receipt(MAIN, '2026-10-21T19:57:45.210692Z'),
                              COMMITTED, MAIN, NOW, fix_attempt=self.ATTEMPT_OK,
                              pages_after=self.AFTER)
        self.assertFalse(state['dual_publisher_race_possible'])
        self.assertEqual(state['pages_configuration']['build_type'], 'legacy',
                         'what was serving must stay on the record')
        self.assertEqual(state['pages_configuration_after_fix']['build_type'], 'workflow')
        self.assertIsNone(state['pages_configuration_after_fix']['source_branch'])
        self.assertIn('Configuration after the fix attempt', rps.to_markdown(state))

    def test_a_denied_switch_leaves_the_race_in_place(self):
        denied = dict(self.ATTEMPT_OK, status=403, error='HTTP 403',
                      body='Resource not accessible by integration',
                      accepted_permissions='pages=write,administration=write')
        state = rps.summarize(PAGES_LEGACY, BUILDS, RUNS,
                              live_receipt(MAIN, '2026-10-21T19:57:45.210692Z'),
                              COMMITTED, MAIN, NOW, fix_attempt=denied)
        self.assertTrue(state['dual_publisher_race_possible'])
        self.assertIsNone(state['pages_configuration_after_fix'])
        self.assertNotIn('Configuration after the fix attempt', rps.to_markdown(state))


class TestPrimitives(unittest.TestCase):
    def test_utc_and_age(self):
        self.assertIsNone(rps.utc(None))
        self.assertIsNone(rps.utc('nonsense'))
        self.assertEqual(rps.age_hours('2026-10-21T19:57:45Z', NOW), 0.74)
        self.assertIsNone(rps.age_hours(None, NOW))
        self.assertIsNone(rps.age_hours('2026-10-21T19:57:45Z', None))

    def test_request_records_a_failure_instead_of_raising(self):
        record = rps.request('https://invalid.invalid./nope', timeout=2)
        self.assertIsNone(record['status'])
        self.assertTrue(record['error'])
        self.assertEqual(record['method'], 'GET')

    def test_a_real_api_read_returns_a_complete_record(self):
        # One live read against the public repository: GitHub's own verdict is not
        # asserted (it depends on the token this runs with), only that the record
        # carries every field the report renders.
        record = rps.request('https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages',
                             timeout=20)
        for key in ('url', 'method', 'status', 'error', 'accepted_permissions', 'request_id'):
            self.assertIn(key, record)
        if record['status'] == 200:
            self.assertEqual(record['body']['source'], {'branch': 'main', 'path': '/'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
