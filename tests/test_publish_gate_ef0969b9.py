"""Session ef0969b9: rules for the dense-schedule freshness gate (no network).

The gate decides whether a *scheduled* publication run has anything to do. These
tests pin the fail-open behaviour: anything unknown or unreadable must publish,
and only a live receipt that matches this exact commit inside the freshness
budget may skip. A skipped run builds and deploys nothing, so it cannot weaken
verification.
"""
import datetime
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.publish_gate import decide, age_minutes  # noqa: E402

NOW = datetime.datetime(2026, 10, 16, 7, 30, tzinfo=datetime.timezone.utc)
SHA = 'a' * 40


def receipt(revision=SHA, snapshot_minutes=10, built_minutes=8, rows=95):
    def stamp(minutes):
        if minutes is None:
            return None
        return (NOW - datetime.timedelta(minutes=minutes)).isoformat().replace('+00:00', 'Z')
    return {'revision': revision, 'snapshot_generated_at': stamp(snapshot_minutes),
            'built_at': stamp(built_minutes), 'rows': rows}


class GateRules(unittest.TestCase):
    def test_pull_request_always_runs(self):
        publish, reason, _ = decide('pull_request', SHA, receipt(), None, NOW)
        self.assertTrue(publish)
        self.assertIn('always publishes', reason)

    def test_push_always_runs_even_when_live_is_fresh(self):
        publish, reason, _ = decide('push', SHA, receipt(), None, NOW)
        self.assertTrue(publish)
        self.assertIn('always publishes', reason)

    def test_manual_dispatch_always_runs(self):
        publish, _, _ = decide('workflow_dispatch', SHA, receipt(), None, NOW)
        self.assertTrue(publish)

    def test_scheduled_run_skips_only_for_same_revision_inside_budget(self):
        publish, reason, detail = decide('schedule', SHA, receipt(snapshot_minutes=30), None, NOW)
        self.assertFalse(publish)
        self.assertIn('skipping the build', reason)
        self.assertEqual(detail['snapshot_age_minutes'], 30.0)

    def test_scheduled_run_publishes_when_snapshot_is_older_than_the_budget(self):
        publish, reason, detail = decide('schedule', SHA, receipt(snapshot_minutes=61), None, NOW)
        self.assertTrue(publish)
        self.assertIn('61 min old', reason)
        self.assertEqual(detail['snapshot_age_minutes'], 61.0)

    def test_scheduled_run_publishes_when_the_live_revision_differs(self):
        publish, reason, _ = decide('schedule', SHA, receipt(revision='b' * 40), None, NOW)
        self.assertTrue(publish)
        self.assertIn('revision', reason)

    def test_missing_receipt_publishes(self):
        publish, reason, _ = decide('schedule', SHA, None, 'URLError: down', NOW)
        self.assertTrue(publish)
        self.assertIn('could not be read', reason)

    def test_non_dict_receipt_publishes(self):
        publish, reason, _ = decide('schedule', SHA, ['not', 'a', 'receipt'], None, NOW)
        self.assertTrue(publish)
        self.assertIn('no usable live build receipt', reason)

    def test_missing_timestamps_publish(self):
        publish, reason, _ = decide('schedule', SHA, {'revision': SHA, 'rows': 95}, None, NOW)
        self.assertTrue(publish)
        self.assertIn('neither a snapshot nor a build timestamp', reason)

    def test_missing_revision_publishes(self):
        publish, reason, _ = decide('schedule', SHA, {'built_at': receipt()['built_at']}, None, NOW)
        self.assertTrue(publish)
        self.assertIn('missing', reason)

    def test_missing_head_sha_publishes(self):
        publish, reason, _ = decide('schedule', '', receipt(), None, NOW)
        self.assertTrue(publish)
        self.assertIn('missing', reason)

    def test_build_age_is_the_fallback_when_snapshot_time_is_absent(self):
        payload = receipt()
        payload.pop('snapshot_generated_at')
        publish, reason, detail = decide('schedule', SHA, payload, None, NOW)
        self.assertFalse(publish)
        self.assertEqual(detail['build_age_minutes'], 8.0)

    def test_zero_budget_always_publishes_on_schedule(self):
        publish, _, _ = decide('schedule', SHA, receipt(), None, NOW, max_age_minutes=0)
        self.assertTrue(publish)

    def test_age_minutes_rejects_garbage(self):
        self.assertIsNone(age_minutes('not-a-date', NOW))
        self.assertIsNone(age_minutes(None, NOW))
        self.assertAlmostEqual(age_minutes('2026-10-16T07:00:00Z', NOW), 30.0)

    def test_future_timestamp_counts_as_fresh_not_stale(self):
        publish, _, detail = decide('schedule', SHA, receipt(snapshot_minutes=-5), None, NOW)
        self.assertFalse(publish)
        self.assertEqual(detail['snapshot_age_minutes'], -5.0)


class GateCli(unittest.TestCase):
    def run_cli(self, receipt_path, event='schedule', extra=()):
        with tempfile.TemporaryDirectory() as tmp:
            output = os.path.join(tmp, 'github_output')
            env = dict(os.environ, GITHUB_OUTPUT=output)
            command = [sys.executable, '-m', 'scripts.publish_gate', '--receipt', receipt_path,
                       '--event', event, '--sha', SHA, '--now', NOW.isoformat(), '--json', *extra]
            completed = subprocess.run(command, capture_output=True, text=True, env=env,
                                       cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            written = ''
            if os.path.exists(output):
                with open(output, encoding='utf-8') as handle:
                    written = handle.read()
            return completed, written

    def test_cli_writes_github_output_for_an_unreadable_receipt(self):
        completed, written = self.run_cli('/nonexistent/build-info.json')
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn('publish=true', written)
        self.assertIn('"publish": true', completed.stdout)

    def test_cli_skips_for_a_fresh_matching_receipt(self):
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as handle:
            json.dump(receipt(), handle)
            path = handle.name
        try:
            completed, written = self.run_cli(path)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn('publish=false', written)
        finally:
            os.unlink(path)

    def test_cli_publishes_on_a_pull_request_even_with_a_fresh_receipt(self):
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as handle:
            json.dump(receipt(), handle)
            path = handle.name
        try:
            completed, written = self.run_cli(path, event='pull_request')
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn('publish=true', written)
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
