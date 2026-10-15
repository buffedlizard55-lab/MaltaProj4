"""Regression tests for this session's non-publishing research harvester.

The harvester only re-derives counts from a snapshot it never modifies, so these
tests assert exactly that: no value is invented, and a row that carries no method
at all (``None``) cannot break the JSON summary that the coordination log quotes.
"""
import importlib
import json
import pathlib
import tempfile
import unittest
import unittest.mock

harvest = importlib.import_module('scripts.harvest_0e407ec7')


def snapshot(rows):
    return {
        'generated_at': '2026-10-15T22:37:11Z',
        'last_attempt_at': '2026-10-15T22:37:11Z',
        'refresh_started_at': '2026-10-15T22:37:02Z',
        'fixtures_observed_at': '2026-10-15T21:33:48Z',
        'coverage': 'verified',
        'issues': [],
        'coverage_counts': {'open': len(rows)},
        'inventory_changes': [],
        'matches': rows,
    }


class SummariserTest(unittest.TestCase):
    def test_none_method_survives_sorted_json(self):
        rows = [
            {'id': '1', 'state': 'open', 'start': '2026-10-16T08:00:00Z', 'teams': ['A', 'B'],
             'probabilities': [0.6, 0.4], 'pick': 'A', 'method': 'exchange'},
            {'id': '2', 'state': 'open', 'start': '2026-10-16T09:00:00Z', 'teams': ['C', 'D'],
             'probabilities': None, 'pick': 'C', 'method': None},
            {'id': '3', 'state': 'open', 'start': '2026-10-16T10:00:00Z', 'teams': ['E', 'F'],
             'probabilities': None, 'pick': None, 'method': None},
        ]
        summary = harvest.summarise(snapshot(rows), 12345, 'arena/x')
        text = json.dumps(summary, indent=1, sort_keys=True)  # the call that used to raise
        self.assertIn('"None": 2', text)
        self.assertEqual(summary['snapshot']['rows_total'], 3)
        self.assertEqual(summary['snapshot']['rows_open'], 3)
        self.assertEqual(summary['snapshot']['rows_open_with_prices'], 1)
        self.assertEqual(summary['snapshot']['rows_open_with_pick_no_price'], 1)
        self.assertEqual(summary['snapshot']['rows_open_without_pick'], 1)
        self.assertEqual(summary['snapshot']['unresolved_open_ids'], ['3'])

    def test_counts_are_rederived_not_authored(self):
        rows = [{'id': str(i), 'state': 'closed' if i % 3 else 'open', 'start': None,
                 'teams': ['A', 'B'], 'probabilities': [0.5, 0.5] if i % 3 == 0 else None,
                 'pick': 'A', 'method': 'exchange'} for i in range(9)]
        summary = harvest.summarise(snapshot(rows), None, None)
        self.assertEqual(summary['snapshot']['rows_open'], 3)
        self.assertEqual(summary['snapshot']['rows_open_with_prices'], 3)
        self.assertEqual(summary['snapshot']['rows_open_with_pick_no_price'], 0)
        self.assertEqual(summary['snapshot']['rows_open_without_pick'], 0)

    def test_main_writes_summary_and_reports_digests(self):
        rows = [{'id': '1', 'state': 'open', 'start': '2026-10-16T08:00:00Z', 'teams': ['A', 'B'],
                 'probabilities': None, 'pick': None, 'method': None}]
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            runtime = root / 'runtime'
            runtime.mkdir()
            (runtime / 'latest.json').write_text(json.dumps(snapshot(rows)))
            out = root / 'harvest'
            argv = ['harvest', '--runtime', str(runtime / 'latest.json'), '--output', str(out)]
            with unittest.mock.patch('sys.argv', argv):
                self.assertEqual(harvest.main(), 0)
            summary = json.loads((out / 'harvest-summary.json').read_text())
            self.assertEqual(sorted(summary['files']), ['latest.json'])
            self.assertEqual(summary['files']['latest.json'],
                             harvest.digest(out / 'latest.json'))
            self.assertEqual(json.loads((out / 'latest.json').read_text()), snapshot(rows))

    def test_missing_runtime_exits_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            out = root / 'harvest'
            argv = ['harvest', '--runtime', str(root / 'nope.json'), '--output', str(out)]
            with unittest.mock.patch('sys.argv', argv):
                self.assertEqual(harvest.main(), 2)
            self.assertFalse((out / 'harvest-summary.json').exists())
            self.assertFalse((out / 'latest.json').exists())


if __name__ == '__main__':
    unittest.main()
