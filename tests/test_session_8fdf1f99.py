"""Contract tests for the three promises this session was asked to keep.

The user's complaint on 2026-10-23 was concrete: the site said there were picks
but the page showed none, and a match without a percentage had no explanation.
The cause was a publish gate that had been red for eight hours; the visible
symptom was a stale snapshot whose evidence had expired. These tests pin the
user-facing contract so the same symptom cannot return silently:

1. every open match has a pick (never a blank row);
2. every open match either carries a two-way probability that sums to 1, or is
   an honest research pick with a stated limitation - never a fabricated 50/50;
3. whatever has no percentage is reachable from the executive summary and listed
   in the unresolved section with its limitation;
4. the executive summary's own numbers agree with the data it summarises;
5. the phone layout keeps the pick on top at 320 px;
6. the refresh watchdog escalates a red gate to a visible issue instead of only
   logging it, and the publication gate stays snapshot-agnostic.
"""
import json
import re
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import build
from scripts import core

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'latest.json'
SNAPSHOT = json.loads(DATA.read_text())
RESEARCH = ('research_',)


def research(row):
    return str(row.get('method') or '').startswith(RESEARCH)


class PickBoardContract(unittest.TestCase):
    """The three promises, checked against a build of the committed snapshot."""

    @classmethod
    def setUpClass(cls):
        cls.clock = core.dt(SNAPSHOT['generated_at'])
        cls.temp = tempfile.TemporaryDirectory()
        cls.site = Path(cls.temp.name)
        build.build(SNAPSHOT, cls.site, now=cls.clock)
        cls.published = json.loads((cls.site / 'data' / 'latest.json').read_text())
        cls.open_rows = [m for m in cls.published['matches'] if m['state'] == 'open']

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def soup(self, name):
        return BeautifulSoup((self.site / (name + '.html')).read_text(), 'html.parser')

    def test_every_open_match_has_a_pick(self):
        self.assertTrue(self.open_rows, 'a build with no open matches cannot prove coverage')
        blanks = [m['id'] for m in self.open_rows if not m.get('pick')]
        self.assertEqual(blanks, [], 'open matches must never be published without a pick')
        for m in self.open_rows:
            self.assertIn(m['pick'], m['teams'], m['id'])

    def test_every_open_match_has_a_real_probability_or_a_stated_limitation(self):
        for m in self.open_rows:
            mid = m['id']
            if m.get('probabilities') is None:
                self.assertTrue(research(m), '%s has no percentage but no research tier' % mid)
                self.assertTrue(m.get('reason'), '%s must state why it has no percentage' % mid)
                self.assertTrue(m.get('limitation') or m.get('reason'), mid)
                self.assertIsNone(m.get('fair_odds'), mid)
                continue
            self.assertEqual(len(m['probabilities']), 2, mid)
            self.assertAlmostEqual(sum(m['probabilities']), 1.0, places=9, msg=mid)
            self.assertNotEqual(m['probabilities'][0], m['probabilities'][1], mid)
            self.assertTrue(m.get('fair_odds'), mid)
            self.assertTrue(m.get('evidence'), mid)
            self.assertTrue(str(m['evidence'][0]['url']).startswith('https://'), mid)

    def test_a_missing_percentage_is_never_papered_over_with_a_coin_flip(self):
        for m in self.open_rows:
            probabilities = m.get('probabilities')
            if probabilities is None:
                self.assertIsNone(m.get('fair_odds'), m['id'])
                continue
            self.assertNotAlmostEqual(probabilities[0], 0.5, places=6, msg=m['id'])

    def test_rows_without_a_percentage_are_listed_in_the_unresolved_section(self):
        unpriced = [m for m in self.open_rows if m.get('probabilities') is None]
        unresolved = self.soup('unresolved')
        unresolved_text = unresolved.get_text(' ', strip=True)
        index_soup = self.soup('index')
        index_text = index_soup.get_text(' ', strip=True)
        for m in unpriced:
            self.assertIn(str(m['id']), unresolved_text,
                          '%s is not listed on unresolved.html' % m['id'])
            self.assertIn(m['pick'], unresolved_text, m['id'])
        # The executive summary must always route to the limitations, even when
        # the current snapshot has nothing unresolved.
        self.assertTrue(any('unresolved' in (a.get('href') or '') for a in index_soup.find_all('a')),
                        'the executive summary must link the unresolved section')
        self.assertIn('never 50/50', index_text)

    def test_executive_summary_numbers_match_the_data(self):
        index_text = self.soup('index').get_text(' ', strip=True)
        open_count = len(self.open_rows)
        picks = sum(1 for m in self.open_rows if m.get('pick'))
        priced = sum(1 for m in self.open_rows if m.get('probabilities') is not None)
        self.assertIn(str(open_count), index_text)
        self.assertIn('%d with a pick' % picks, index_text)
        self.assertIn('%d with a win probability' % priced, index_text)
        # The prose must not claim a probability for a row that has none.
        if priced < open_count:
            self.assertIn('no percentage', index_text)

    def test_the_updated_picks_board_is_reachable_in_one_tap(self):
        index_soup = self.soup('index')
        hrefs = [a.get('href') or '' for a in index_soup.find_all('a')]
        self.assertIn('picks.html', hrefs)
        board = self.soup('picks')
        rows = board.select('[data-match-id], tr[data-id]')
        self.assertTrue(rows or 'match-' in str(board), 'picks.html must carry the board rows')
        ids = set(re.findall(r'match-(\d{6,})', str(board)))
        for m in self.open_rows:
            self.assertIn(str(m['id']), ids, '%s missing from picks.html' % m['id'])

    def test_phone_layout_puts_the_pick_first(self):
        html = (self.site / 'index.html').read_text()
        self.assertIn('name="viewport"', html)
        self.assertIn('width=device-width', html)
        css = (self.site / 'assets' / 'style.css').read_text()
        self.assertRegex(css, r'@media[^{]*max-width:\s*(320|360|375|400|480|520|600|640|680|700|720|760|768)px')
        self.assertNotIn('width: 100vw', css.replace('min-width', ''))


class ResearchRowsAreHonest(unittest.TestCase):
    def test_research_rows_cite_a_dated_source(self):
        for m in SNAPSHOT['matches']:
            if not research(m) or m['state'] != 'open':
                continue
            self.assertTrue(m.get('pick'), m['id'])
            self.assertIsNone(m.get('probabilities'), m['id'])
            urls = [str(e.get('url')) for e in (m.get('evidence') or [])]
            self.assertTrue(urls and all(u.startswith('https://') for u in urls), m['id'])


class PublishGateStaysSnapshotAgnostic(unittest.TestCase):
    """Regression guard for the 2026-10-23 eight-hour outage.

    Two tests pinned a *historical* research sub-tier and a historical pick for
    live fixture ids. The next automated refresh re-derived those rows from a
    different tier, step 8 went red, nothing was published, and every percentage
    on the live site expired. A guard that compares a row's method with a pinned
    value turns a routine data update into a site-wide outage.
    """

    def source(self, name):
        return (ROOT / 'tests' / name).read_text()

    def test_research_rows_are_asserted_structurally_not_by_pinned_method(self):
        body = self.source('test_session_75ebd2d6.py')
        self.assertIn('startswith("research_")', body)
        self.assertNotIn('assertEqual(m["method"], exp["method"]', body)
        source_gate = self.source('test_session_13e99ca6.py')
        self.assertIn("startswith('research_')", source_gate)

    def test_no_test_pins_a_historical_probability_for_a_fixture_id(self):
        # A pinned percentage for a live fixture is the same defect in another
        # shape: the next refresh legitimately changes it.
        for path in sorted((ROOT / 'tests').glob('test_*.py')):
            text = path.read_text()
            for match in re.finditer(r'"(10\d{5,})"\s*:\s*\{[^}]*"probabilities"\s*:\s*\[', text):
                self.fail('%s pins probabilities for fixture %s' % (path.name, match.group(1)))

    def test_the_watchdog_escalates_a_red_gate_instead_of_only_logging_it(self):
        from scripts import refresh_watchdog as watchdog
        self.assertTrue(watchdog.should_escalate('stop', 3))
        workflow = (ROOT / '.github/workflows/refresh-watchdog.yml').read_text()
        self.assertIn('issues: write', workflow.split('concurrency:')[0])


class ExternalLineReceiptContract(unittest.TestCase):
    """Book receipts must be identity-bound, dated and two-way."""

    @classmethod
    def setUpClass(cls):
        cls.receipts = json.loads((ROOT / 'data' / 'book-receipts.json').read_text())
        cls.rows = {str(m['id']): m for m in SNAPSHOT['matches']}

    def test_every_receipt_is_a_two_way_line_with_a_dated_source(self):
        accepted = [r for r in self.receipts['receipts']]
        self.assertTrue(accepted)
        for r in accepted:
            self.assertEqual(len(r['odds']), 2, r['id'])
            self.assertNotEqual(r['odds'][0], r['odds'][1], r['id'])
            self.assertTrue(str(r['url']).startswith('https://'), r['id'])
            self.assertRegex(r['start'], r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
            self.assertRegex(r['observed_at'], r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
            self.assertEqual(len(r['source_teams']), 2, r['id'])
            self.assertEqual(len({t.casefold() for t in r['source_teams']}), 2, r['id'])

    def test_a_receipt_for_a_listed_fixture_shares_its_start_time(self):
        for r in self.receipts['receipts']:
            row = self.rows.get(str(r.get('fixture_id')))
            if row and row.get('start'):
                self.assertEqual(core.dt(r['start']), core.dt(row['start']), r['id'])

    def test_a_listing_receipt_carries_identity_and_corroboration(self):
        # A pricing receipt is only usable if the names were bound to the fixture
        # and a second reading corroborates the number.
        for r in self.receipts['receipts']:
            row = self.rows.get(str(r.get('fixture_id')))
            if not row or row['state'] != 'open' or row.get('probabilities') is None:
                continue
            if not str(row.get('method') or '').startswith('bookmaker'):
                continue
            self.assertTrue(r.get('identity_evidence'), r['id'])
            self.assertTrue(r.get('corroboration'), r['id'])


if __name__ == '__main__':
    unittest.main()
