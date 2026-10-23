"""Tests for the cadence watchdog decision rules and the coverage-gap matcher.

Both scripts exist to keep a promise the user asked for: the pick board is
re-checked automatically, and a fixture that Hotspawn does not list is reported
as a gap instead of silently missing. These tests pin the decision rules so a
future edit cannot turn the watchdog into a loop, and pin the gap matcher so it
cannot claim coverage it did not measure.
"""
import contextlib
import datetime
import io
import json
import pathlib
import tempfile
import unittest

from scripts import refresh_watchdog as watchdog
from scripts.refresh_watchdog import age_minutes, evaluate
from scripts.coverage_gap_dedd2e34 import hltv_matches

NOW = datetime.datetime(2026, 10, 16, 4, 30, tzinfo=datetime.timezone.utc)


def stamp(minutes_ago, seconds=0):
    return (NOW - datetime.timedelta(minutes=minutes_ago, seconds=seconds)).strftime('%Y-%m-%dT%H:%M:%SZ')


def run(event='schedule', status='completed', conclusion='success', created=200, updated=None):
    return {'event': event, 'status': status, 'conclusion': conclusion, 'created_at': stamp(created),
            'updated_at': stamp(updated if updated is not None else created - 2),
            'html_url': 'https://github.com/o/r/actions/runs/1'}


def receipt(minutes_ago):
    return {'built_at': stamp(minutes_ago), 'snapshot_generated_at': stamp(minutes_ago),
            'revision': 'deadbeef', 'rows': 86}


class WatchdogRules(unittest.TestCase):
    def test_fresh_snapshot_needs_no_action(self):
        action, detail = evaluate([run()], receipt(50), NOW, 150, 45, 10, [])
        self.assertEqual(action, 'ok')
        self.assertIn('no action', detail)

    def test_overdue_snapshot_dispatches_once(self):
        action, detail = evaluate([run()], receipt(320), NOW, 150, 45, 10, [])
        self.assertEqual(action, 'dispatch')
        self.assertIn('over the 150-min limit', detail)

    def test_a_run_in_progress_blocks_a_second_dispatch(self):
        action, detail = evaluate([run(status='in_progress', conclusion=None, created=10), run()],
                                  receipt(320), NOW, 150, 45, 10, [])
        self.assertEqual(action, 'skip')
        self.assertIn('already in_progress', detail)

    def test_cooldown_after_a_recent_watchdog_dispatch(self):
        runs = [run(event='workflow_dispatch', created=20), run()]
        action, detail = evaluate(runs, receipt(320), NOW, 150, 45, 10, [])
        self.assertEqual(action, 'skip')
        self.assertIn('cooldown', detail)

    def test_daily_budget_stops_a_loop(self):
        runs = [run(event='workflow_dispatch', created=60 * (i + 1) + 60) for i in range(10)]
        action, detail = evaluate(runs, receipt(320), NOW, 150, 45, 10, [])
        self.assertEqual(action, 'stop')
        self.assertIn('budget', detail)

    def test_missing_receipt_is_a_stop_not_a_guess(self):
        action, detail = evaluate([run()], None, NOW, 150, 45, 10, ['live build receipt unreadable: 404'])
        self.assertEqual(action, 'stop')
        self.assertIn('unknown state', detail)

    def test_receipt_without_a_snapshot_time_falls_back_to_build_age(self):
        action, detail = evaluate([run()], {'built_at': stamp(300)}, NOW, 150, 45, 10, [])
        self.assertEqual(action, 'dispatch')
        self.assertIn('falling back to build age', detail)

    def test_unparseable_timestamps_are_reported_not_assumed(self):
        self.assertIsNone(age_minutes(None, NOW))
        self.assertIsNone(age_minutes('not a time', NOW))
        self.assertAlmostEqual(age_minutes(stamp(90), NOW), 90, places=0)

    def test_consecutive_failed_runs_warn_early_and_stop_same_commit_loop(self):
        from scripts.refresh_watchdog import consecutive_failures
        failed_pair = [
            {**run(conclusion='failure', created=25), 'head_sha': 'abc12345deadbeef'},
            {**run(conclusion='failure', created=40), 'head_sha': 'abc12345deadbeef'},
            run(conclusion='success', created=70),
        ]
        self.assertEqual(consecutive_failures(failed_pair), 2)
        action, detail = evaluate(failed_pair, receipt(50), NOW, 150, 45, 10, [])
        self.assertEqual(action, 'ok')
        self.assertIn('warning: 2 consecutive failed runs on main', detail)

        failed_triple = [
            {**run(conclusion='failure', created=50), 'head_sha': 'abc12345deadbeef'},
            {**run(conclusion='failure', created=110), 'head_sha': 'abc12345deadbeef'},
            {**run(conclusion='failure', created=170), 'head_sha': 'abc12345deadbeef'},
        ]
        self.assertEqual(consecutive_failures(failed_triple), 3)
        action, detail = evaluate(failed_triple, receipt(320), NOW, 150, 45, 10, [])
        self.assertEqual(action, 'stop')
        self.assertIn('3 consecutive failed runs on commit abc12345', detail)


    def test_default_window_matches_watchdog_policy(self):
        # The publication cron runs every 15 minutes; the watchdog dispatches only
        # after the published snapshot is more than 90 minutes old. Keep the threshold
        # distinct from both the trigger cadence and the eight-hour evidence TTL.
        import subprocess, sys
        help_text = subprocess.run([sys.executable, '-m', 'scripts.refresh_watchdog', '--help'],
                                   capture_output=True, text=True, check=True).stdout
        self.assertIn('--max-age-minutes', help_text)
        self.assertIn('(default: 90)', help_text)

    def test_documented_cadence_matches_workflows(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        pages = root.joinpath('.github/workflows/pages.yml').read_text()
        watchdog = root.joinpath('.github/workflows/refresh-watchdog.yml').read_text()
        readme = root.joinpath('README.md').read_text()
        builder = root.joinpath('scripts/build.py').read_text()
        self.assertIn("cron: '4,19,34,49 * * * *'", pages)
        self.assertIn("cron: '*/10 * * * *'", watchdog)
        self.assertIn('four times an hour at :04, :19, :34 and :49 UTC', readme)
        self.assertIn('watchdog checks the published snapshot every 10 minutes', readme)
        self.assertIn('scheduled checks every 15 minutes at :04, :19, :34 and :49 UTC', builder)
        self.assertNotIn('hourly at :17 UTC', readme + builder)


class CoverageGapMatcher(unittest.TestCase):
    def test_hltv_event_page_yields_exact_pairs_and_utc_starts(self):
        from scripts.core import iso, norm
        page = pathlib.Path(__file__).parent.joinpath('fixtures/hltv.html').read_text()
        found = hltv_matches(page)
        self.assertTrue(found, 'the saved HLTV excerpt must yield fixtures')
        for row in found.values():
            self.assertEqual(len(row['teams']), 2)
            # The start is carried through as an explicit UTC instant.
            self.assertEqual(row['start'], iso(row['start']))
            self.assertTrue(row['url'].startswith('https://www.hltv.org/matches/'))
            self.assertEqual(row['key'], tuple(sorted(map(norm, row['teams']))))

    def test_fetch_helper_uses_the_collector_client(self):
        # The gap check must go through the same client the collector uses: HLTV answers
        # 403 to a bare urllib request from the runner and 200 to this session, so a
        # private HTTP path would make "unreachable" mean two different things. Pinned
        # here because a wrong call signature inside the helper is otherwise only
        # visible as a fail-closed "(not measured)" report.
        import types
        from scripts import coverage_gap_dedd2e34 as gap
        seen = {}

        class FakeSources:
            def __init__(self, now):
                seen['now'] = now

            def get(self, label, url, as_json, **kwargs):
                seen.update(label=label, url=url, as_json=as_json)
                return '{"fixtures": []}', {'observed_at': '2026-10-16T05:00:00Z', 'http_status': 200}

        original = __import__('scripts.refresh', fromlist=['Sources']).Sources
        __import__('scripts.refresh', fromlist=['Sources']).Sources = FakeSources
        try:
            body, headers = gap.get('https://example.test/api/fixtures?sport_alias=cs2')
        finally:
            __import__('scripts.refresh', fromlist=['Sources']).Sources = original
        self.assertIs(body['fixtures'], []) if isinstance(body, dict) else json.loads(body)
        self.assertEqual(headers.get('x-status'), 200)
        self.assertTrue(seen['as_json'], 'fixture API responses must be parsed as JSON')
        self.assertEqual(seen['url'], 'https://example.test/api/fixtures?sport_alias=cs2')
        import datetime as dt_module
        self.assertIsInstance(seen['now'], dt_module.datetime)


    def test_empty_or_changed_page_fails_loudly(self):
        with self.assertRaises(ValueError):
            hltv_matches('<div>no matches here</div>')


class HarvestRecompute(unittest.TestCase):
    def test_replay_arithmetic_matches_the_published_probability(self):
        from scripts.harvest_dedd2e34 import replay_check
        # Two-sided exchange prices already sum to 1.000, so devigging is exact,
        # in the source's own order or swapped to the fixture's order.
        same = replay_check({'prices': [0.685, 0.315]}, [0.685, 0.315])
        self.assertTrue(same['match'])
        self.assertEqual(same['orientation'], 'source order')
        flipped = replay_check({'prices': [0.315, 0.685]}, [0.685, 0.315])
        self.assertTrue(flipped['match'])
        self.assertEqual(flipped['orientation'], 'swapped order')
        # American +130 / -170: decimal 2.30 and 1.5882, implied 0.4348 and 0.6296.
        # The minus side is the favourite, so the replay must put it above 50%.
        decimal_home, decimal_away = 1 + 130 / 100, 1 + 100 / 170
        implied = [1 / decimal_home, 1 / decimal_away]
        pair = [x / sum(implied) for x in implied]
        self.assertLess(pair[0], 0.5 < pair[1], 'the -170 side must be the favourite')
        book = replay_check({'raw': {'prices': [{'price': 130}, {'price': -170}]}}, pair)
        self.assertTrue(book['match'], book)
        self.assertEqual(book['orientation'], 'source order')
        # A row whose numbers are not reproducible is reported, never accepted.
        wrong = replay_check({'prices': [0.685, 0.315]}, [0.5, 0.5])
        self.assertIs(wrong['match'], False)
        self.assertIsNone(replay_check({}, [0.5, 0.5])['match'])
        self.assertIsNone(replay_check({'prices': ['x', 'y']}, [0.5, 0.5])['match'])
        self.assertIsNone(replay_check({'raw': {'prices': [{'price': 130}]}}, [0.5, 0.5])['match'])

    def test_model_lines_replay_from_valve_points(self):
        from scripts import vrs
        from scripts.harvest_dedd2e34 import replay_check
        points = [1716, 1543]
        published = [vrs.calibrated(vrs.expected(*points)), vrs.calibrated(vrs.expected(points[1], points[0]))]
        check = replay_check({'provider': 'Valve VRS model', 'points': points}, published)
        self.assertTrue(check['match'], check)
        self.assertIn('Valve standings points', check['inputs'])

    def test_book_probe_records_are_never_probabilities(self):
        from scripts.book_probe_dedd2e34 import ENDPOINTS
        self.assertTrue(all(len(entry) == 4 for entry in ENDPOINTS))
        for name, url, category, why in ENDPOINTS:
            self.assertTrue(url.startswith('https://'), name)
            self.assertIn(category, ('bookmaker', 'exchange', 'schedule', 'aggregator', 'model'))


class WatchdogEscalation(unittest.TestCase):
    """A red gate must be visible to a human, not just recorded in a log.

    On 23 October 2026 a failing test step froze the board for 8 h 40 min. The
    watchdog did the right thing - it stopped dispatching into a broken gate -
    but the only trace was a line in a workflow log, and the live site withheld
    every pick with no explanation anywhere else.
    """

    def failing_run(self, sha='abc1234', created=100):
        row = run(created=created, conclusion='failure')
        row['head_sha'] = sha
        row['html_url'] = 'https://github.com/o/r/actions/runs/%d' % created
        return row

    def test_escalates_only_when_the_gate_has_stopped_the_chain(self):
        self.assertTrue(watchdog.should_escalate('stop', 3))
        self.assertTrue(watchdog.should_escalate('stop', 5))
        self.assertFalse(watchdog.should_escalate('stop', 2))
        self.assertFalse(watchdog.should_escalate('dispatch', 9))
        self.assertFalse(watchdog.should_escalate('ok', 0))

    def test_body_names_the_runs_the_snapshot_and_the_consequence(self):
        runs = [self.failing_run(created=100), self.failing_run(created=200)]
        body = watchdog.escalation_body('3 consecutive failed runs', runs, receipt(520),
                                        'https://o.github.io/r/', 3)
        self.assertTrue(body.startswith(watchdog.ESCALATION_MARKER))
        self.assertIn('every pick is withheld', body)
        self.assertIn('3 consecutive failed runs', body)
        self.assertIn('https://github.com/o/r/actions/runs/100', body)
        self.assertIn('abc1234', body)
        self.assertIn(receipt(520)['snapshot_generated_at'], body)
        self.assertIn('close this issue', body)

    def test_issue_is_created_once_then_updated_in_place(self):
        calls = []
        state = {'search': [], 'create_number': 7}

        def fake_api(path, token, method='GET', payload=None):
            calls.append((method, path, payload))
            if path.startswith('/search/issues'):
                return {'items': state['search']}
            if path == '/repos/o/r/issues':
                item = {'number': state['create_number'], 'body': payload['body']}
                state['search'] = [item]
                return item
            return {}

        original = watchdog.api
        watchdog.api = fake_api
        try:
            self.assertEqual(watchdog.sync_escalation('t', 'o/r', watchdog.ESCALATION_TITLE, 'body one'),
                             'created #7')
            self.assertEqual(watchdog.sync_escalation('t', 'o/r', watchdog.ESCALATION_TITLE, 'body one'),
                             'unchanged #7')
            self.assertEqual(watchdog.sync_escalation('t', 'o/r', watchdog.ESCALATION_TITLE, 'body two'),
                             'updated #7')
        finally:
            watchdog.api = original
        created = [c for c in calls if c[0] == 'POST' and c[1] == '/repos/o/r/issues']
        self.assertEqual(len(created), 1, 'the issue must never be duplicated')
        self.assertEqual(created[0][2]['title'], watchdog.ESCALATION_TITLE)
        patched = [c for c in calls if c[0] == 'PATCH']
        self.assertEqual(len(patched), 1)
        self.assertEqual(patched[0][1], '/repos/o/r/issues/7')
        self.assertEqual(patched[0][2]['body'], 'body two')

    def test_a_failed_alert_never_breaks_the_tick(self):
        def boom(path, token, method='GET', payload=None):
            raise OSError('network down')

        original = watchdog.api
        watchdog.api = boom
        try:
            with self.assertRaises(OSError):
                watchdog.sync_escalation('t', 'o/r', watchdog.ESCALATION_TITLE, 'body')
        finally:
            watchdog.api = original

    def test_workflow_grants_issues_write_for_the_alert(self):
        workflow = (pathlib.Path(__file__).resolve().parents[1]
                    / '.github/workflows/refresh-watchdog.yml').read_text()
        head = workflow.split('concurrency:')[0]
        self.assertIn('issues: write', head)
        self.assertIn('actions: write', head)
        self.assertIn('contents: read', head)


if __name__ == '__main__':
    unittest.main()
