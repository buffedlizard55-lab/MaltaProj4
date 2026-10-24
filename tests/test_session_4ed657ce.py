"""Session 4ed657ce: phone-summary discoverability and dated source verification.

These tests are offline: they read the committed snapshot, this session's dated
external receipts, and the generated pages from scripts.build. They do not
refresh a source or require the browser; the Chromium measurements are stored as
a separate receipt in research/session-4ed657ce/mobile-measurements.json.
"""
import copy
import importlib.util
import json
import re
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import summary
from scripts.build import exec_summary_bar, exec_summary_quicknav, overview
from scripts.verify_4ed657ce import audit, same_team

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())
EXTERNAL = json.loads((ROOT / 'research' / 'session-4ed657ce' / 'external-observations.json').read_text())
OVERVIEW = overview(copy.deepcopy(SNAPSHOT))
CSS_ROOT = (ROOT / 'assets' / 'style.css').read_text()
CSS_SITE = (ROOT / 'site' / 'assets' / 'style.css').read_text()


def load_alias_verifier():
    spec = importlib.util.spec_from_file_location(
        'verify_0cc1138a_alias', ROOT / 'research' / 'session-0cc1138a' / 'verify_0cc1138a.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PhoneExecutiveSummaryTests(unittest.TestCase):
    def setUp(self):
        self.soup = BeautifulSoup(OVERVIEW, 'html.parser')
        self.quick = self.soup.select_one('#exec-quicknav')
        self.bar = self.soup.select_one('#exec-summary')

    def test_quick_nav_exists_once_and_is_not_folded(self):
        self.assertIsNotNone(self.quick)
        self.assertEqual(len(self.soup.select('#exec-quicknav')), 1)
        self.assertIsNone(self.quick.find_parent('details'))

    def test_quick_nav_is_dom_ordered_between_full_bar_and_pick_list(self):
        self.assertLess(OVERVIEW.index('id="exec-summary"'), OVERVIEW.index('id="exec-quicknav"'))
        self.assertLess(OVERVIEW.index('id="exec-quicknav"'), OVERVIEW.index('id="picks-at-a-glance"'))

    def test_quick_nav_links_to_picks_and_visible_limitations(self):
        hrefs = {a['href'] for a in self.quick.select('a')}
        self.assertEqual(hrefs, {'picks.html', '#unresolved-limits'})
        self.assertTrue(self.soup.select_one('#unresolved-limits'))

    def test_quick_nav_counts_come_from_the_snapshot(self):
        c = summary.counts(SNAPSHOT['matches'])
        text = re.sub(r'\s*/\s*', '/', self.quick.get_text(' ', strip=True))
        self.assertIn('%d/%d picks' % (c['with_pick'], c['open']), text)
        self.assertIn('%d unresolved' % c['without_percentage'], text)
        self.assertIn('past feed rows', self.quick.get_text(' ', strip=True))

    def test_full_bar_keeps_its_contract_and_adds_visible_limitations(self):
        hrefs = {a['href'] for a in self.bar.select('a')}
        self.assertTrue({'picks.html', '#picks-at-a-glance', 'unresolved.html',
                         '#unresolved-summary', '#unresolved-limits', 'matches.html',
                         'review.html'} <= hrefs)
        self.assertIn('past their lock or start', self.bar.get_text(' ', strip=True))

    def test_stylesheets_are_identical_balanced_and_keep_pinned_orders(self):
        self.assertEqual(CSS_ROOT, CSS_SITE)
        depth = 0
        for char in CSS_SITE:
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
            self.assertGreaterEqual(depth, 0)
        self.assertEqual(depth, 0)
        for needle in (
            'body[data-page="index"] main>#exec-quicknav{order:3}',
            'body[data-page="index"] main>#picks-at-a-glance{order:4}',
            'body[data-page="index"] main>#exec-summary{order:5}',
            'body[data-page="index"] main>details.briefing-more{order:6}',
            '.exec-quicknav-actions a',
        ):
            self.assertIn(needle, CSS_SITE)

    def test_mobile_measurement_receipt_records_the_fixed_geometry(self):
        path = ROOT / 'research' / 'session-4ed657ce' / 'mobile-measurements.json'
        measurements = json.loads(path.read_text())
        by_width = {m['width']: m for m in measurements}
        self.assertEqual(set((320, 390, 768, 1440)) & set(by_width), {320, 390, 768, 1440})
        for width in (320, 390):
            self.assertFalse(by_width[width]['overflow'])
            self.assertFalse(by_width[width]['staleVisible'])
            self.assertTrue(by_width[width]['firstCardAboveTab'])
            self.assertTrue(by_width[width]['answerAboveTab'])


class DatedVerificationTests(unittest.TestCase):
    def test_official_observation_receipt_is_complete(self):
        self.assertEqual(EXTERNAL['session'], '4ed657ce')
        self.assertEqual(len(EXTERNAL['polymarket']), 19)
        self.assertEqual(len(EXTERNAL['bookmaker_pages']), 3)
        self.assertEqual(EXTERNAL['inventory']['lobby_cache_busted']['tier_count'], 92)
        self.assertEqual(EXTERNAL['inventory']['lobby_uncached']['tier_count'], 88)
        self.assertEqual(EXTERNAL['hltv_dated_valve_ranking']['points']['LOS NINOS'], 573)
        self.assertEqual(len(EXTERNAL['valve_monthly_file']['sha256']), 64)

    def test_every_open_row_reproduces_and_keeps_official_links(self):
        report, _ = audit(copy.deepcopy(SNAPSHOT), EXTERNAL)
        self.assertEqual(report['open_rows'], 31)
        self.assertEqual(report['reproduced_rows'], 31)
        self.assertEqual(report['rows_failing'], 0)
        for row in report['rows']:
            self.assertTrue(row['fixture_source'].startswith('https://'))
            self.assertIn('hotspawn.com', row['fixture_source'])
            self.assertTrue(row['price_source'].startswith('https://'))
            self.assertIsNotNone(row['re_derived_probabilities'])
            self.assertFalse(row['problems'])

    def test_cache_irregularity_is_flagged_not_silently_dropped(self):
        report, _ = audit(copy.deepcopy(SNAPSHOT), EXTERNAL)
        self.assertTrue(any('uncached lobby' in issue for issue in report['issues']))

    def test_a_tampered_probability_is_rejected(self):
        doc = copy.deepcopy(SNAPSHOT)
        row = next(m for m in doc['matches'] if m['state'] == 'open' and m['probabilities'])
        row['probabilities'] = [row['probabilities'][1], row['probabilities'][0]]
        report, _ = audit(doc, EXTERNAL)
        self.assertGreater(report['rows_failing'], 0)
        self.assertTrue(any('re-derived' in issue for issue in report['issues']))

    def test_the_verification_markdown_has_one_sourced_row_per_open_match(self):
        text = (ROOT / 'research' / 'session-4ed657ce' / 'VERIFICATION.md').read_text()
        rows = [line for line in text.splitlines() if line.startswith('| ') and 'Hotspawn](http' in line]
        self.assertEqual(len(rows), 31)
        for line in rows:
            self.assertIn('[source](https://', line)


class AliasVerifierRepairTests(unittest.TestCase):
    def test_a_sourced_alias_maps_and_an_unsourced_alias_fails(self):
        v = load_alias_verifier()
        sourced = {'identity_sources': [{
            'names': ['Tropa do KinGui', 'Projeto do KinGui'],
            'source': 'https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7',
            'basis': 'Same CCT South America Round-of-16 slot and lineup; also registered in data/identities.json.'}]}
        self.assertEqual(
            v.order_prices(['Tropa do KinGui', 'MEIA NOITE'], [0.615, 0.385],
                           ['Projeto do KinGui', 'MEIA NOITE'], sourced),
            [0.615, 0.385])
        with self.assertRaises(ValueError):
            v.order_prices(['Tropa do KinGui', 'MEIA NOITE'], [0.615, 0.385],
                           ['Projeto do KinGui', 'MEIA NOITE'])
        self.assertTrue(same_team('BakS eSports', 'BakS'))
        self.assertFalse(same_team('Alpha', 'Beta'))


class ReviewFlagTests(unittest.TestCase):
    def test_session_flags_are_published_with_official_links(self):
        notes = json.loads((ROOT / 'data' / 'review-notes.json').read_text())
        by_id = {n['id']: n for n in notes}
        expected = {
            'session-4ed657ce-hotspawn-lobby-cache-2026-10-24',
            'session-4ed657ce-kingui-label-alias-2026-10-24',
            'session-4ed657ce-duplicate-valve-label-2026-10-05',
            'session-4ed657ce-market-drift-2026-10-24',
            'session-4ed657ce-root-css-copy-sync-2026-10-24',
            'session-4ed657ce-phone-summary-discoverability-2026-10-24',
            'session-4ed657ce-pages-deployment-lag-2026-10-24',
        }
        self.assertTrue(expected <= set(by_id))
        for key in expected:
            self.assertTrue(by_id[key]['sources'])
            for source in by_id[key]['sources']:
                self.assertTrue(source['url'].startswith('https://'))


if __name__ == '__main__':
    unittest.main()
