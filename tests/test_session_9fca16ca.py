"""Falsifiable delivery/source regressions for session 9fca16ca.

These tests use committed bytes only. They pin the contract that made the live
site confusing: a fresh board must publish a coherent receipt, visible mobile
navigation, an executive summary with in-site pick links, source links on every
published row, and a hidden stale banner that JavaScript may reveal only under
the eight-hour evidence rule.
"""
import html
import importlib.util
import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'research/session-9fca16ca'
SPEC = importlib.util.spec_from_file_location('session_9fca16ca_report', HERE / 'build_report.py')
report = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(report)


def load(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


class Session9fca16ca(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load('data/latest.json')
        cls.official = json.loads((HERE / 'official-checks.json').read_text(encoding='utf-8'))
        cls.open_rows = [m for m in cls.data['matches'] if m.get('state') == 'open']

    def test_every_open_row_reproduces_from_its_own_evidence(self):
        self.assertTrue(self.open_rows, 'a board with no open rows cannot verify coverage')
        for m in self.open_rows:
            with self.subTest(fixture=m['id']):
                checks = report.row_checks(m)
                self.assertTrue(all(checks.values()), checks)
                self.assertNotEqual(m['probabilities'][0], m['probabilities'][1],
                                    'a current pick must never be a 50/50 default')

    def test_every_published_pick_row_has_an_external_price_source(self):
        picks = (ROOT / 'picks.html').read_text(encoding='utf-8')
        blocks = re.findall(r'<tr[^>]+data-match="[^"]+"[^>]*>.*?</tr>', picks, re.S)
        self.assertEqual(len(blocks), len(self.open_rows))
        for block in blocks:
            fixture = re.search(r'data-match="([^"]+)"', block).group(1)
            with self.subTest(fixture=fixture):
                urls = [html.unescape(url) for url in re.findall(r'href="(https://[^"]+)"', block)]
                external = [u for u in urls if urlsplit(u).hostname not in report.HOTSPAWN_HOSTS]
                self.assertTrue(external, 'row has no external official price link')
                self.assertTrue(all(urlsplit(u).scheme == 'https' for u in external))

    def test_generated_site_and_receipt_checks_all_pass(self):
        site, site_failures = report.html_checks()
        receipt, receipt_failures = report.receipt_checks(self.data)
        self.assertEqual(site_failures, [])
        self.assertEqual(receipt_failures, [])
        self.assertTrue(all(site['checks'].values()))
        self.assertTrue(all(receipt['checks'].values()))
        self.assertEqual(site['picks_rows'], len(self.open_rows))
        self.assertEqual(receipt['files_checked'], 20)

    def test_report_generator_is_reproducible_and_verified(self):
        before = [(HERE / name).read_bytes() for name in ('ROW-LEDGER.md', 'SUMMARY.json')]
        self.assertEqual(report.main(), 0)
        after = [(HERE / name).read_bytes() for name in ('ROW-LEDGER.md', 'SUMMARY.json')]
        self.assertEqual(before, after, 'the committed ledger was not reproducible')
        summary = json.loads((HERE / 'SUMMARY.json').read_text(encoding='utf-8'))
        self.assertTrue(summary['verified'])
        self.assertEqual(summary['row_failures'], [])
        self.assertEqual(summary['html_failures'], [])
        self.assertEqual(summary['receipt_failures'], [])

    def test_direct_official_checks_are_linked_and_well_formed(self):
        for entry in self.official['current_market_checks']:
            with self.subTest(market=entry['market_id']):
                self.assertTrue(entry['source_url'].startswith('https://gamma-api.polymarket.com/markets/'))
                self.assertEqual(len(entry['outcomePrices']), 2)
                self.assertEqual(len(entry['stored_order_prices']), 2)
                self.assertTrue(all(0 <= p <= 1 for p in entry['outcomePrices'] + entry['stored_order_prices']))
                self.assertAlmostEqual(sum(entry['outcomePrices']), 1.0)
        open_ids = {m['id'] for m in self.open_rows}
        for entry in self.official['current_market_checks']:
            self.assertIn(entry['fixture_id'], open_ids)
        for source in self.official['official_sources']:
            self.assertTrue(source['url'].startswith('https://'), source['name'])
        self.assertIn('&', report.md_url('https://example.test/?a=1&b=2'))
        self.assertNotIn('&amp;', report.md_url('https://example.test/?a=1&b=2'))

    def test_fallback_rows_record_hltv_then_esportsbook_attempts(self):
        for m in self.open_rows:
            if m.get('method') == 'exchange':
                continue
            providers = [a.get('provider') for a in m.get('attempts', [])]
            with self.subTest(fixture=m['id']):
                self.assertIn('HLTV', providers)
                self.assertIn('Pinnacle', providers)
                if m.get('method') in ('model_vrs', 'model_vrs_mirror'):
                    self.assertIn('Valve VRS model', providers)
                    self.assertTrue(any('Thunderpick' in str(p) for p in providers))
                    self.assertIn('GG.BET', providers)
                    hltv = providers.index('HLTV')
                    pinnacle = providers.index('Pinnacle')
                    self.assertLess(hltv, pinnacle)

    def test_executive_summary_link_label_is_escaped_once(self):
        index = (ROOT / 'index.html').read_text(encoding='utf-8')
        for page in sorted((ROOT).glob('*.html')):
            with self.subTest(page=page.name):
                text = page.read_text(encoding='utf-8')
                self.assertNotIn('&amp;amp;', text)
                self.assertNotIn('&amp;lt;', text)
                self.assertNotIn('&amp;quot;', text)
        self.assertIn('odds &amp; prediction overview', index)
        self.assertIn('https://www.hltv.org/betting/analytics/2399918/tropa-do-kingui-vs-yawara-cct-2026-south-america-series-7', index)

    def test_refresh_cadence_and_eight_hour_window_are_published(self):
        self.assertEqual(self.data['stale_after_hours'], 8)
        pages = (ROOT / '.github/workflows/pages.yml').read_text(encoding='utf-8')
        watchdog = (ROOT / '.github/workflows/refresh-watchdog.yml').read_text(encoding='utf-8')
        app = (ROOT / 'assets/app.js').read_text(encoding='utf-8')
        self.assertIn("cron: '4,19,34,49 * * * *'", pages)
        self.assertIn("cron: '*/10 * * * *'", watchdog)
        self.assertIn('const ttl = 8 * 3600000;', app)

    def test_review_flags_from_this_session_are_present(self):
        notes = load('data/review-notes.json')
        ids = {note['id'] for note in notes}
        self.assertIn('session-9fca16ca-dated-market-drift-2026-10-25', ids)
        self.assertIn('session-9fca16ca-fallback-access-limitations-2026-10-25', ids)
        self.assertIn('session-9fca16ca-double-escaped-summary-link-2026-10-25', ids)
        for note in notes:
            self.assertTrue(note['sources'])
            for source in note['sources']:
                self.assertTrue(source['url'].startswith('https://'))


if __name__ == '__main__':
    unittest.main()
