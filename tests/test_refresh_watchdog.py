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


    def test_default_window_is_one_late_hourly_slot(self):
        # pages.yml is scheduled hourly at :17 (tightened from two hours by session
        # ab18fe2a after measuring zero scheduled runs in five hours). The watchdog only
        # backfills a missed slot, so its published-freshness default must stay just
        # above one hour: wider, and the eight-hour evidence window can lapse between
        # ticks without anyone acting on it.
        import subprocess, sys
        help_text = subprocess.run([sys.executable, '-m', 'scripts.refresh_watchdog', '--help'],
                                   capture_output=True, text=True, check=True).stdout
        self.assertIn('--max-age-minutes', help_text)
        self.assertIn('(default: 90)', help_text)


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


if __name__ == '__main__':
    unittest.main()
