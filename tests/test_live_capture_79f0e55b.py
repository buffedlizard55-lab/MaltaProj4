"""Offline tests for scripts/live_capture_79f0e55b.py (session 79f0e55b).

The live audit is only useful if its counting rules are pinned: a row counts as priced
only when it carries probabilities, the board totals must not silently include closed
fixtures, and a page percentage is only ever compared against the published set (never
asserted to be an error, because pages legitimately show VRS points and rating numbers).
"""
import unittest
from unittest import mock

from scripts import live_capture_79f0e55b as lc

SNAPSHOT = {
    'coverage': 'verified',
    'generated_at': '2026-10-17T00:45:31.347884Z',
    'matches': [
        {'id': '1', 'state': 'open', 'teams': ['A', 'B'], 'pick': 'A', 'method': 'exchange',
         'probabilities': [0.55, 0.45], 'reason': None},
        {'id': '2', 'state': 'open', 'teams': ['C', 'D'], 'pick': 'C', 'method': 'research_rank',
         'probabilities': None, 'reason': 'No verified market line.'},
        {'id': '3', 'state': 'open', 'teams': ['E', 'F'], 'pick': None, 'method': None,
         'probabilities': None, 'reason': 'Source start or pick lock has passed.'},
        {'id': '4', 'state': 'not_open', 'teams': ['G', 'H'], 'pick': None, 'method': None,
         'probabilities': None, 'reason': 'closed'},
    ],
}

PAGE = """
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body>
<nav class="bottom-nav"><a href="picks.html">Picks</a><a href="matches.html">Matches</a>
<a href="analysis.html">Analysis</a><a href="unresolved.html">Gaps</a></nav>
<h1>Executive summary</h1>
<div id="unresolved-summary">1 fixture has no usable market line.</div>
<table><tbody>
<tr><td>A</td><td>B</td><td>55.0%</td></tr>
<tr><td>C</td><td>D</td><td>no line</td></tr>
<tr><td>E</td><td>F</td><td>no line</td></tr>
</tbody></table>
</body></html>
"""


class Summarise(unittest.TestCase):
    def test_counts_only_open_rows_and_separates_unpriced(self):
        summary = lc.summarise(SNAPSHOT)
        self.assertEqual(summary['rows_total'], 4)
        self.assertEqual(summary['open_total'], 3)
        self.assertEqual(summary['open_priced'], 1)
        self.assertEqual(summary['open_unpriced'], 2)
        self.assertEqual(summary['open_without_pick'], 1)
        self.assertEqual(summary['unpriced_ids'], ['2', '3'])
        self.assertEqual(summary['methods'], {'exchange': 1, 'None': 1, 'research_rank': 1})
        self.assertEqual(summary['coverage'], 'verified')

    def test_unpriced_rows_keep_their_reason_for_the_reader(self):
        summary = lc.summarise(SNAPSHOT)
        reasons = {row[0]: row[4] for row in summary['unpriced_teams']}
        self.assertEqual(reasons['2'], 'No verified market line.')


class PageChecks(unittest.TestCase):
    def test_viewport_nav_anchor_and_links(self):
        checks = lc.page_checks('index.html', PAGE, SNAPSHOT)
        self.assertTrue(checks['mobile_viewport_ok'])
        self.assertTrue(checks['has_unresolved_anchor'])
        self.assertTrue(checks['links_to']['picks.html'])
        self.assertTrue(checks['links_to']['unresolved.html'])
        self.assertFalse(checks['links_to']['sources.html'])
        self.assertIn('bottom-nav', ' '.join(checks['nav_candidates']))
        self.assertEqual(checks['h1'], 'Executive summary')

    def test_missing_open_row_is_reported_on_the_picks_page(self):
        html = PAGE.replace('<tr><td>C</td><td>D</td><td>no line</td></tr>', '')  # C/D row dropped
        checks = lc.page_checks('picks.html', html, SNAPSHOT)
        self.assertEqual(checks['open_rows_expected'], 3)
        self.assertIn(['2', ['C', 'D']], checks['open_rows_missing_from_page'])
        self.assertNotIn(['1', ['A', 'B']], checks['open_rows_missing_from_page'])

    def test_percentage_comparison_is_a_set_difference_not_an_error(self):
        # 55.0% is published (0.55) and rendered, so it is not reported as unexplained.
        self.assertNotIn('55.0', lc.displayed_odds_mismatches(PAGE, SNAPSHOT))
        page = PAGE.replace('55.0%', '55.0% <span>78.5%</span>')
        extra = lc.displayed_odds_mismatches(page, SNAPSHOT)
        # A percentage the board does not publish is surfaced for review, never asserted wrong.
        self.assertIn('78.5', extra)
        self.assertIsInstance(extra, list)


class FetchReceipts(unittest.TestCase):
    def test_pages_host_failure_is_a_receipt(self):
        session = mock.Mock()
        response = mock.Mock(status_code=404, content=b'nope', headers={})
        session.get.return_value = response
        with mock.patch.object(lc.time, 'sleep', lambda *_: None):
            body, receipt = lc.fetch(session, 'https://example.invalid/index.html', attempts=2, pause=0)
        self.assertIsNone(body)
        self.assertEqual(receipt['status'], 404)
        self.assertEqual(receipt['bytes'], 4)
        self.assertIn('HTTP 404', receipt['error'])

    def test_success_receipt_records_hash(self):
        session = mock.Mock()
        response = mock.Mock(status_code=200, content=b'<html></html>', headers={'Cache-Control': 'max-age=600'})
        session.get.return_value = response
        body, receipt = lc.fetch(session, 'https://example.invalid/index.html', attempts=1)
        self.assertEqual(body, b'<html></html>')
        self.assertEqual(len(receipt['sha256']), 64)
        self.assertEqual(receipt['cache_control'], 'max-age=600')


if __name__ == '__main__':
    unittest.main()
