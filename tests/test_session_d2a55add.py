"""Session d2a55add: a fresh board, an HLTV-first/book ledger for every
non-featured row, and an executive summary a phone can read without a tap.

Three invariants, none of which may be weakened to fit a snapshot:

1. Every open row the featured strict-exchange tier did not resolve appears
   in the gap ledger with a recorded HLTV attempt and a recorded
   esportsbook/betting-line attempt. A missing attempt is an irregularity,
   never silently described as "no line exists".
2. The home page carries one always-visible executive summary (`#exec-summary`)
   outside any folded disclosure, after the freshness strip and before the
   pick list, linking inside this site to the updated picks, the picks on
   this page, the separate unresolved section and page, all matches and the
   flagged-for-review page. Its completeness sentence and its no-percentage
   counter come from `scripts.summary` on the same snapshot, and the two
   shipped CSS copies stay byte-identical with the phone ordering rule.
3. The snapshot these tests read is the committed one; when integration
   replaces it, the same assertions re-run against the fresh board.
"""
import copy
import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import summary
from scripts.build import exec_summary_bar, overview
from scripts.gap_probe_d2a55add import ledger

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data' / 'latest.json').read_text(encoding='utf-8'))


class GapLedgerTests(unittest.TestCase):
    def setUp(self):
        self.book = ledger(copy.deepcopy(DATA))
        self.by_id = {r['id']: r for r in self.book['rows']}

    def test_every_non_featured_open_row_is_ledgered(self):
        expected = {m['id'] for m in DATA['matches']
                    if m['state'] == 'open'
                    and not (m.get('method') == 'exchange' and m.get('probabilities') is not None)}
        self.assertEqual(set(self.by_id), expected)

    def test_hltv_first_and_books_next_are_recorded(self):
        for row in self.book['rows']:
            self.assertNotEqual(row['hltv_first_step'], 'not recorded', row['id'])
            self.assertNotEqual(row['book_step'], 'not recorded', row['id'])
        self.assertEqual(self.book['irregularities'], [])

    def test_counts_add_up(self):
        c = self.book['counts']
        self.assertEqual(c['non_featured_open'], len(self.book['rows']))
        self.assertEqual(c['with_probability'] + c['research_only_pick']
                         + c['unresolved_no_pick'], c['non_featured_open'])

    def test_priced_rows_have_no_fake_limitation(self):
        for row in self.book['rows']:
            if row['probabilities'] is not None:
                self.assertTrue(row['limitation'].startswith('Not applicable'), row['id'])
            else:
                self.assertTrue(row['limitation'], row['id'])

    def test_missing_attempts_are_flagged_never_hidden(self):
        snapshot = {'generated_at': DATA['generated_at'],
                    'fixtures_observed_at': DATA['fixtures_observed_at'],
                    'matches': [{'id': 'x1', 'teams': ['A', 'B'], 'competition': 'C',
                                 'start': '2999-01-01T00:00:00Z', 'lock': '2999-01-01T00:00:00Z',
                                 'state': 'open', 'pick': None, 'method': None,
                                 'probabilities': None, 'attempts': [], 'flags': [],
                                 'reason': 'Nothing verified.', 'source_url': 'https://play.hotspawn.com/lobby'}]}
        book = ledger(snapshot)
        self.assertEqual(book['counts']['unresolved_no_pick'], 1)
        self.assertEqual(len(book['irregularities']), 2)  # HLTV and book both missing

    def test_ladder_tries_hltv_before_books(self):
        keys = [step[0] for step in summary.LADDER]
        self.assertLess(keys.index('hltv'), keys.index('pinnacle'))
        self.assertLess(keys.index('pinnacle'), keys.index('book'))
        self.assertLess(keys.index('book'), keys.index('research'))


class ExecutiveSummaryBarTests(unittest.TestCase):
    def setUp(self):
        self.html = overview(copy.deepcopy(DATA))
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.bar = self.soup.select_one('#exec-summary')

    def test_bar_exists_once_and_is_never_folded(self):
        self.assertEqual(len(self.soup.select('#exec-summary')), 1)
        self.assertIsNotNone(self.bar)
        self.assertIsNone(self.bar.find_parent('details'))

    def test_bar_sits_between_freshness_strip_and_pick_list(self):
        self.assertLess(self.html.index('id="freshness-strip"'),
                        self.html.index('id="exec-summary"'))
        self.assertLess(self.html.index('id="exec-summary"'),
                        self.html.index('id="picks-at-a-glance"'))

    def test_bar_links_inside_the_site_to_the_updated_picks(self):
        hrefs = {a['href'] for a in self.bar.select('a')}
        self.assertTrue({'picks.html', '#picks-at-a-glance', 'unresolved.html',
                         '#unresolved-summary', 'matches.html', 'review.html'} <= hrefs)
        for href in hrefs:
            self.assertFalse(href.startswith('http'), href)  # in-site links only

    def test_bar_sentence_and_counter_come_from_the_snapshot(self):
        c = summary.counts(DATA['matches'])
        self.assertEqual(self.bar.select_one('[data-completeness]').get_text(),
                         summary.completeness_sentence(c))
        counter = self.bar.select_one('[data-count="missing"]')
        self.assertEqual(int(counter.get_text()), c['without_percentage'])

    def test_bar_alone_renders_from_the_same_function(self):
        soup = BeautifulSoup(exec_summary_bar(copy.deepcopy(DATA)), 'html.parser')
        self.assertIsNotNone(soup.select_one('#exec-summary'))

    def test_phone_ordering_rule_and_identical_css_copies(self):
        root_css = (ROOT / 'assets' / 'style.css').read_bytes()
        site_css = (ROOT / 'site' / 'assets' / 'style.css').read_bytes()
        self.assertEqual(root_css, site_css)
        css = site_css.decode('utf-8')
        # Phones order the bar directly after the pick list (order 5): with it
        # above the list the first picks sat at y=901 on a 390px phone, past
        # the 750px first-screen gate other suites enforce.
        self.assertIn('body[data-page="index"] main>#exec-summary{order:5}', css)
        self.assertIn('.exec-bar-link', css)
        self.assertIn('min-height:44px', css)


class FreshBoardCoverageTests(unittest.TestCase):
    """The committed board must answer every open row: a pick (priced or
    research-only) or an unresolved row the ledger can explain."""

    def test_every_open_row_has_a_pick_or_a_ledger_limitation(self):
        book = {r['id']: r for r in ledger(copy.deepcopy(DATA))['rows']}
        for m in DATA['matches']:
            if m['state'] != 'open':
                continue
            if m.get('method') == 'exchange' and m.get('probabilities') is not None:
                self.assertIn(m['pick'], m['teams'])
                continue
            self.assertIn(m['id'], book)
            if not m.get('pick'):
                self.assertTrue(book[m['id']]['limitation'])


if __name__ == '__main__':
    unittest.main()
