"""Reproduce this session's independent Day-5 quote and live-page audit receipts."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.day5_e0fd5a32 import devig

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research' / 'session-69389f44'


class Session69389f44ReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book = json.loads((RESEARCH / 'day5-live-markets.json').read_text())
        cls.gamma = json.loads((RESEARCH / 'polymarket-reread.json').read_text())
        cls.live = json.loads((RESEARCH / 'live-site-observation.json').read_text())
        cls.post_merge = json.loads((RESEARCH / 'post-merge-reread.json').read_text())
        cls.post_pr83 = json.loads((RESEARCH / 'post-pr83-reread.json').read_text())
        cls.post_pr81 = json.loads((RESEARCH / 'post-pr81-reread.json').read_text())

    def test_thunderpick_calculation_and_selected_pick_reproduce(self):
        expected = [
            ({'Aurora': 140, 'Falcons': -200}, {'Aurora': 0.38461538461538464, 'Falcons': 0.6153846153846154}, 1.0833333333333333, 'Falcons'),
            ({'FURIA': -286, 'BETBOOM': 190}, {'FURIA': 0.6824090834293237, 'BETBOOM': 0.31759091657067634}, 1.0857602286939432, 'FURIA'),
        ]
        self.assertEqual([row['hltv_match_id'] for row in self.book['fixtures']], ['2399416', '2399417'])
        for row, (prices, probabilities, margin, pick) in zip(self.book['fixtures'], expected):
            calculated = devig(*row['teams'], prices)
            self.assertEqual(row['prices_american'], prices)
            self.assertEqual(row['pick'], pick)
            self.assertAlmostEqual(calculated['overround'], margin, places=12)
            self.assertAlmostEqual(row['overround'], margin, places=12)
            for team, probability in probabilities.items():
                self.assertAlmostEqual(calculated['devig'][team], probability, places=12)
                self.assertAlmostEqual(row['devig'][team], probability, places=12)
            self.assertLess(row['expires_at_utc'], row['start_utc'])
            self.assertTrue(row['bookmaker_source_url'].startswith('https://thunderpick.io/'))

    def test_thunderpick_capture_window_is_not_claimed_as_provider_time(self):
        window = self.book['observation_window_utc']
        self.assertLess(window['started_at'], window['completed_by'])
        self.assertEqual(window['conservative_observed_at'], window['started_at'])
        self.assertIn('not a Thunderpick server timestamp', self.book['capture_method'])
        self.assertTrue(any('consensus' in item for item in self.book['limitations']))

    def test_gamma_reread_matches_ordered_outcome_prices_and_starts(self):
        self.assertEqual([market['id'] for market in self.gamma['markets']], ['5837604', '5837622'])
        for market in self.gamma['markets']:
            self.assertTrue(market['active'])
            self.assertFalse(market['closed'])
            self.assertTrue(market['accepting_orders'])
            self.assertAlmostEqual(sum(market['outcome_prices']), 1.0, places=12)
            self.assertTrue(all(0.0 <= price <= 1.0 for price in market['outcome_prices']))
            self.assertTrue(market['source_url'].startswith('https://gamma-api.polymarket.com/markets/'))
        final = self.gamma['markets'][1]
        self.assertEqual(final['displayed_market_percentages'], {'FURIA': 71.5, 'BETBOOM': 28.5})
        self.assertEqual(final['updated_at_utc'], '2026-10-18T00:59:15.015789Z')

    def test_live_snapshot_and_current_week_ui_counts_are_kept_distinct(self):
        counts = self.live['count_reconciliation']
        self.assertEqual(counts['dashboard_retained_feed_rows'], 98)
        self.assertEqual(counts['Hotspawn_current_week_filter_entries'], 81)
        self.assertEqual(counts['difference'], 17)
        rows = self.live['final_day_rows_in_live_dashboard_snapshot']
        self.assertEqual([row['hotspawn_id'] for row in rows], ['1080209', '1080210'])
        self.assertAlmostEqual(rows[0]['published_snapshot_line']['Falcons'], 0.605)
        self.assertAlmostEqual(rows[1]['published_snapshot_line']['FURIA'], 0.705)
        self.assertIn('did not fully reconcile', counts['verified_conclusion'])

    def test_post_merge_cache_busted_receipt_is_current_and_published(self):
        build = self.post_merge['build_info']
        self.assertEqual(build['revision'], '4f5d44b1f0903e013446d1fe931d4812f086e1f0')
        self.assertEqual(build['rows'], 98)
        self.assertEqual(build['snapshot_generated_at'], '2026-10-18T01:11:43.690752Z')
        self.assertEqual(self.post_merge['publication']['verify_build'], 'success')
        self.assertEqual(self.post_merge['publication']['deploy'], 'success')
        rows = self.post_merge['final_day_rows']
        self.assertEqual([row['hotspawn_id'] for row in rows], ['1080209', '1080210'])
        self.assertEqual(rows[0]['market_percentages'], {'Falcons': 60.5, 'Aurora': 39.5})
        self.assertEqual(rows[1]['market_percentages'], {'FURIA': 71.5, 'BetBoom': 28.5})
        for row in rows:
            self.assertEqual(row['dashboard_observed_at_utc'], '2026-10-18T01:09Z')
            self.assertLess(row['dashboard_expiry_utc'], row['lock_utc'])

    def test_post_pr83_reread_records_merged_build_and_current_final_rows(self):
        receipt = self.post_pr83
        build = receipt['build_info']
        self.assertEqual(build['revision'], '4a9740d976d6ff2a3aa7e3e7b9b9483aa49ff54e')
        self.assertEqual(build['snapshot_generated_at'], '2026-10-18T01:27:34.098265Z')
        self.assertEqual(build['rows'], 98)
        publication = receipt['integration']['main_run']
        self.assertEqual(publication['verify_build'], 'success')
        self.assertEqual(publication['deploy'], 'success')
        self.assertEqual(publication['live_bytes_verification'], 'success')
        self.assertEqual(receipt['refresh_receipt']['summary'], {
            'open': 34, 'probabilities': 29, 'market': 17, 'vrs': 12,
            'research_only_no_percentage': 5, 'without_supported_pick': 0,
        })
        rows = receipt['final_day_rows']
        self.assertEqual([row['hotspawn_id'] for row in rows], ['1080209', '1080210'])
        self.assertEqual(rows[0]['market_percentages'], {'Falcons': 60.5, 'Aurora': 39.5})
        self.assertEqual(rows[1]['market_percentages'], {'FURIA': 71.5, 'BetBoom': 28.5})
        self.assertEqual(rows[1]['dashboard_observed_at_utc'], '2026-10-18T01:25Z')
        self.assertEqual(rows[1]['dashboard_expiry_utc'], '2026-10-18T09:25:00Z')
        self.assertIn('70.5%', receipt['updated_analysis_cards']['residual_copy_mismatch'])
        self.assertIn('historical', receipt['updated_analysis_cards']['residual_copy_mismatch'])

    def test_post_pr81_reread_records_current_live_build_counts_and_expiry(self):
        receipt = self.post_pr81
        build = receipt['build_info']
        self.assertEqual(build['revision'], 'c97fd1827d48903f79f6fb5a2b41fe30b8c09ffe')
        self.assertEqual(build['snapshot_generated_at'], '2026-10-18T01:32:37.072848Z')
        self.assertEqual(build['rows'], 98)
        publication = receipt['publication']['main_run']
        self.assertEqual(publication['verify_build'], 'success')
        self.assertEqual(publication['deploy'], 'success')
        self.assertEqual(publication['live_bytes_verification'], 'success')
        self.assertEqual(receipt['live_summary'], {
            'url': receipt['live_summary']['url'],
            'observation_utc': '2026-10-18T01:32Z',
            'feed_rows': 98,
            'open': 34,
            'with_probabilities': 29,
            'external_market': 18,
            'vrs_model': 11,
            'research_only_without_percentage': 5,
            'open_without_supported_pick': 0,
            'mobile_nav': ['Overview', 'Picks', 'Research', 'Matches', 'TWC analysis', 'Review', 'Sources'],
            'no_percentage_filter_label': True,
            'refresh_copy': receipt['live_summary']['refresh_copy'],
        })
        rows = receipt['final_day_rows']
        self.assertEqual([row['hotspawn_id'] for row in rows], ['1080209', '1080210'])
        self.assertEqual(rows[0]['market_percentages'], {'Falcons': 60.5, 'Aurora': 39.5})
        self.assertEqual(rows[1]['market_percentages'], {'FURIA': 71.5, 'BetBoom': 28.5})
        self.assertEqual(rows[1]['dashboard_expiry_display'], '18 Oct · 09:29 UTC')
        self.assertEqual(receipt['residual_static_copy_mismatch']['current_board'],
                         'The cache-busted 01:32 build contains FURIA 71.5%, observed at 01:30. Against the 68.24% Thunderpick de-vig line the current difference is 3.26 percentage points, not 2.26.')

    def test_each_fact_table_row_links_a_source(self):
        report = (RESEARCH / 'REPORT.md').read_text().splitlines()
        in_table = False
        data_rows = 0
        for line in report:
            if not line.startswith('|'):
                in_table = False
                continue
            if not in_table:
                in_table = True
                continue  # heading row
            if line.replace('|', '').replace('-', '').replace(':', '').strip() == '':
                continue  # separator row
            data_rows += 1
            self.assertIn('](', line, f'Table row lacks a source link: {line}')
        self.assertGreaterEqual(data_rows, 20)


if __name__ == '__main__':
    unittest.main()
