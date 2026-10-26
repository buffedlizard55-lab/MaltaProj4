"""Session 28e4f2a1: where every pick is, counted and linked, and the lines re-derived.

What this suite proves, and why
-------------------------------
1. **The executive summary answers "where are the picks?" with a table, not a
   sentence.** ``#picks-directory`` — rendered inside the executive summary's
   unresolved-and-limitations section (``#unresolved-limits``) and again at the
   top of ``unresolved.html`` — lists every source that produced a pick on this
   snapshot, how many open matches it answered for, whether those rows carry a
   percentage, the official source of that kind of line and the page on this
   site that lists them. Every count is recomputed here from the snapshot with
   ``scripts.summary.METHOD_STEP``, so no number is typed by hand, and the
   categories must sum to the open board exactly.

2. **A zero is measured, not hidden.** A tier that answered for nothing on this
   snapshot still renders, with 0, because a vanishing row is how coverage
   silently drifts. An unclassified method must not be folded into a known
   tier: it is counted under "no pick" and named on the page.

3. **The mobile contract is a stylesheet fact, not a claim.** Both stylesheet
   copies stay byte-identical and brace-balanced, the directory's phone rules
   exist, and no phone rule hides or clips a directory cell — the same rule the
   earlier phone suites enforce for percentages, fair lines and source links.

4. **HLTV is documented as an identity input, never a price.** The directory
   states, with links, that HLTV confirms the pair, the start, the five and the
   ranking, that this project measured no numeric two-way line on it, and that
   its community vote is never used — next to the esportsbook listing the
   ladder falls back to.

5. **Every published line re-derives from its own raw bytes.** The two
   verification runners in ``research/session-28e4f2a1`` re-implement the
   arithmetic and the gates without importing ``scripts``; their receipts are
   committed. The invariants that must hold for *any* snapshot (pick is the
   higher side, fair odds are reciprocals, probabilities sum to 1) are asserted
   directly here, and a receipt is only held to its own snapshot when the two
   timestamps agree — a newer snapshot never fails this suite for the wrong
   reason (see the 2026-10-23/24 outage in ``tests/test_session_019a253a.py``).
"""
import copy
import json
import re
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import build, summary

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())
# Rendered from scripts.build rather than read from the committed root: the
# publisher stages the root fallback from this same code *after* the unit gate,
# so a test that read the committed page would fail for a stale file, not a bug
# (session 6d111263's measured lesson). The browser suites measure the real
# artifact under public/ at publish time.
INDEX = build.overview(copy.deepcopy(SNAPSHOT))
UNRESOLVED = build.unresolved_page(copy.deepcopy(SNAPSHOT))
CSS_ROOT = (ROOT / 'assets' / 'style.css').read_text()
CSS_SITE = (ROOT / 'site' / 'assets' / 'style.css').read_text()
RECEIPTS = ROOT / 'research' / 'session-28e4f2a1'
IN_SITE = {'picks.html', 'unresolved.html', 'matches.html', 'review.html',
           'sources.html', 'evidence.html', 'data/latest.json', 'data/matches.csv'}


def open_rows(doc=None):
    return [m for m in (doc or SNAPSHOT)['matches'] if m.get('state') == 'open']


def directory_rows(html):
    soup = BeautifulSoup(html, 'html.parser')
    directory = soup.select_one('#picks-directory')
    assert directory is not None
    table = directory.select_one('table.directory-table')
    assert table is not None
    return directory, [tr for tr in table.select('tbody tr')]


class DirectoryInTheExecutiveSummary(unittest.TestCase):
    def setUp(self):
        self.soup = BeautifulSoup(INDEX, 'html.parser')

    def test_the_directory_is_inside_the_executive_summary(self):
        section = self.soup.select_one('#unresolved-limits')
        self.assertIsNotNone(section)
        self.assertIsNotNone(section.select_one('#picks-directory'),
                             'the executive summary must carry the pick directory')
        self.assertEqual(len(self.soup.select('#picks-directory')), 1,
                         'exactly one directory on the home page')

    def test_it_links_the_pick_board_and_the_unresolved_page(self):
        directory, _ = directory_rows(INDEX)
        hrefs = {a['href'] for a in directory.select('a[href]')}
        self.assertIn('picks.html', hrefs)
        self.assertIn('unresolved.html', hrefs)
        # The last paragraph is the site map a phone reader needs in one place.
        note = directory.select_one('#where-picks-are')
        self.assertIsNotNone(note)
        for route in ('picks.html', 'unresolved.html', 'matches.html', 'review.html',
                      'sources.html#method', 'evidence.html', 'data/latest.json'):
            self.assertIn(route, {a['href'] for a in note.select('a')}, route)

    def test_every_category_appears_even_at_zero(self):
        _, rows = directory_rows(INDEX)
        steps = [row.get('data-directory-step') for row in rows]
        self.assertEqual(steps, [key for key, *_ in build.DIRECTORY_STEPS] + ['none', 'total'])
        for row in rows:
            cells = row.select('td')
            self.assertEqual(len(cells), 5, 'label, count, priced count, source, destination')
            if row.get('data-directory-step') not in ('total',):
                self.assertRegex(cells[1].get_text(strip=True), r'^\d+$')

    def test_counts_sum_to_the_open_board(self):
        _, rows = directory_rows(INDEX)
        counts = {row['data-directory-step']: int(row.select('td')[1].get_text(strip=True))
                  for row in rows}
        self.assertEqual(counts['total'], len(open_rows()))
        self.assertEqual(sum(v for k, v in counts.items() if k != 'total'), len(open_rows()))
        priced = sum(1 for m in open_rows() if m['probabilities'] is not None)
        self.assertEqual(int(rows[-1].select('td')[2].get_text(strip=True)), priced)

    def test_counts_equal_the_snapshot_methods(self):
        _, rows = directory_rows(INDEX)
        expected = {}
        for m in open_rows():
            if m.get('probabilities') is None and not m.get('pick'):
                step = 'none'
            else:
                step = summary.METHOD_STEP.get(m.get('method'), 'none')
            expected[step] = expected.get(step, 0) + 1
        for row in rows:
            key = row['data-directory-step']
            if key == 'total':
                continue
            self.assertEqual(int(row.select('td')[1].get_text(strip=True)),
                             expected.get(key, 0), key)

    def test_every_row_carries_an_official_source_or_says_why_not(self):
        _, rows = directory_rows(INDEX)
        external = {key: url for key, _label, _what, _href, _dest in build.DIRECTORY_STEPS
                    for url in [next((s['url'] for s in summary.ladder_rows() if s['key'] == key), None)]}
        for row in rows:
            key = row['data-directory-step']
            links = [a['href'] for a in row.select('a[href]')]
            in_site = [href for href in links if href in IN_SITE or href.startswith('unresolved.html')]
            self.assertTrue(in_site, '%s has no in-site destination' % key)
            if key in external and external[key]:
                self.assertIn(external[key], links, '%s must cite its official source' % key)
            if key in ('none', 'total'):
                self.assertIn('https://play.hotspawn.com/cs2-pickems', links)
        self.assertEqual(len(self.soup.select('a[href="picks.html"]')) > 0, True)

    def test_hltv_is_described_as_an_identity_input_with_a_link(self):
        directory, _ = directory_rows(INDEX)
        text = directory.get_text(' ', strip=True)
        self.assertIn('HLTV is an identity and ranking input, not a price', text)
        self.assertIn('community vote is never used', text)
        hrefs = {a['href'] for a in directory.select('a[href]')}
        self.assertIn('https://www.hltv.org/matches', hrefs)
        self.assertIn('https://egamersworld.com/counterstrike/matches', hrefs)

    def test_the_unresolved_page_carries_the_same_directory_with_a_jump(self):
        directory, rows = directory_rows(UNRESOLVED)
        self.assertEqual([r['data-directory-step'] for r in rows],
                         [key for key, *_ in build.DIRECTORY_STEPS] + ['none', 'total'])
        jump = directory.select_one('a.directory-jump')
        self.assertIsNotNone(jump)
        self.assertEqual(jump['href'], '#unresolved-rows')
        self.assertIn('id="unresolved-rows"', UNRESOLVED)
        self.assertLess(UNRESOLVED.index('id="picks-directory"'), UNRESOLVED.index('id="unresolved-rows"'))

    def test_the_full_summary_bar_links_the_directory(self):
        bar = self.soup.select_one('#exec-summary')
        self.assertIn('#picks-directory', {a['href'] for a in bar.select('a[href]')})


class UnclassifiedMethodsAreNamed(unittest.TestCase):
    def test_an_unknown_method_is_counted_as_no_pick_and_reported(self):
        doc = json.loads(json.dumps(SNAPSHOT))
        row = open_rows(doc)[0]
        row['method'] = 'made_up_tier'
        html = build.pick_directory(doc)
        soup = BeautifulSoup(html, 'html.parser')
        counts = {tr['data-directory-step']: int(tr.select('td')[1].get_text(strip=True))
                  for tr in soup.select('tbody tr')}
        self.assertEqual(counts['none'], 1)
        self.assertIn('Unclassified method on this snapshot', soup.get_text(' ', strip=True))
        self.assertIn(row['id'], soup.get_text(' ', strip=True))

    def test_an_unresolved_row_is_counted_and_named_on_the_summary(self):
        doc = json.loads(json.dumps(SNAPSHOT))
        row = open_rows(doc)[0]
        row['probabilities'] = row['fair_odds'] = row['pick'] = row['method'] = None
        card = BeautifulSoup(build.unresolved_limits_card(doc), 'html.parser')
        section = card.select_one('#unresolved-limits')
        self.assertIsNotNone(section.select_one('#picks-directory'))
        counts = {tr['data-directory-step']: int(tr.select('td')[1].get_text(strip=True))
                  for tr in section.select('#picks-directory tbody tr')}
        self.assertEqual(counts['none'], 1)
        self.assertIn(counts['total'], (len(open_rows(doc)), len(open_rows(doc))))


class PhoneStylesheetContract(unittest.TestCase):
    def test_both_copies_stay_identical_and_balanced(self):
        self.assertEqual(CSS_ROOT, CSS_SITE)
        depth = 0
        for char in CSS_SITE:
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
            self.assertGreaterEqual(depth, 0)
        self.assertEqual(depth, 0)

    def test_the_directory_has_its_own_phone_rules(self):
        block = CSS_SITE[CSS_SITE.index('.directory-table'):]
        self.assertIn('@media(max-width:650px)', block)
        phone = block[block.index('@media(max-width:650px)'):]
        for selector in ('.directory-table tbody tr{display:grid', '.directory-table td:first-child',
                         '.directory-table td:nth-child(4)', '.directory-table td:nth-child(5)'):
            self.assertIn(selector, phone)

    def test_no_phone_rule_hides_a_directory_cell_or_its_count(self):
        phone_blocks = re.findall(r'@media\(max-width:650px\)\{(?:[^{}]|\{[^{}]*\})*\}', CSS_SITE)
        self.assertTrue(phone_blocks)
        for block in phone_blocks:
            for rule in re.finditer(r'([^{}]+)\{([^{}]*)\}', block):
                selector, body = rule.group(1), rule.group(2)
                if 'directory' in selector:
                    self.assertNotIn('display:none', body.replace(' ', ''), selector)
                    self.assertNotIn('visibility:hidden', body.replace(' ', ''), selector)

    def test_the_directory_cells_are_present_on_every_rendered_page(self):
        for name, html in (('index', INDEX), ('unresolved', UNRESOLVED)):
            directory, rows = directory_rows(html)
            for row in rows:
                for cell in row.select('td'):
                    self.assertTrue(cell.get_text(strip=True), '%s: an empty directory cell' % name)


class PublishedLinesReDerive(unittest.TestCase):
    def test_every_open_row_satisfies_the_published_arithmetic(self):
        checked = 0
        for m in open_rows():
            p = m.get('probabilities')
            if p is None:
                self.assertFalse(m.get('fair_odds'), '%s: fair odds without a probability' % m['id'])
                if m.get('pick'):
                    self.assertTrue(m.get('method'), '%s: priced pick without a method' % m['id'])
                continue
            checked += 1
            self.assertEqual(len(p), 2)
            self.assertTrue(all(0 < x < 1 for x in p), m['id'])
            self.assertAlmostEqual(sum(p), 1, places=12)
            for x, f in zip(p, m['fair_odds']):
                self.assertAlmostEqual(f, 1 / x, places=12)
            if p[0] != p[1]:
                self.assertEqual(m['pick'], m['teams'][0] if p[0] > p[1] else m['teams'][1])
            self.assertTrue(str(m.get('method') or '').startswith(('exchange', 'bookmaker', 'model_')))
        self.assertGreater(checked, 0, 'the committed snapshot prices no open row')

    def test_no_probability_originates_on_hotspawn(self):
        for m in open_rows():
            for quote in m.get('evidence') or []:
                for key in ('url', 'api_url'):
                    value = quote.get(key) or ''
                    self.assertNotIn('play.hotspawn.com', value,
                                     '%s prices a row from Hotspawn' % m['id'])
                    self.assertNotIn('hotspawn.com/matches', value)

    def test_the_model_receipt_reproduces_every_model_row(self):
        receipt = json.loads((RECEIPTS / 'model-receipt.json').read_text())
        self.assertEqual(receipt['summary']['problems'], 0, receipt['problems'])
        self.assertEqual(receipt['summary']['reproduced'], receipt['summary']['model_rows'])
        model_ids = {r['fixture'] for r in receipt['rows'] if r['kind'] == 'published_line'}
        # Session b964dffd repair (2026-10-26): bind this receipt to its own
        # snapshot exactly like the line-receipt test below — this suite's own
        # stated rule (docstring point 5). Unbound, the assertion held every
        # future board's model rows to the 2026-10-26T00:10:49Z receipt and
        # failed on the first rotated snapshot (2026-10-26T01:00:10Z, new
        # model row 1079202), which is the pinned-live-value failure class
        # that froze publication on 2026-10-23/24. The receipt-internal
        # checks above and below stay unconditional.
        self.assertIn('snapshot_generated_at', receipt)
        if receipt['snapshot_generated_at'] == SNAPSHOT['generated_at']:
            for m in open_rows():
                if m.get('method') in ('model_vrs', 'model_vrs_mirror'):
                    self.assertIn(m['id'], model_ids)
        for row in receipt['rows']:
            for duplicate in row.get('duplicate_labels', []):
                self.assertTrue(duplicate['roster_rule_verified'], (row['fixture'], duplicate))

    def test_the_line_receipt_is_bound_to_the_snapshot_it_audited(self):
        receipt = json.loads((RECEIPTS / 'line-receipt.json').read_text())
        self.assertEqual(receipt['summary']['failed'], 0, receipt['problems'])
        self.assertGreater(receipt['summary']['checks'], 0)
        if receipt['snapshot_generated_at'] == SNAPSHOT['generated_at']:
            self.assertEqual({r['fixture'] for r in receipt['rows']},
                             {m['id'] for m in open_rows()})
        # A newer snapshot must never fail this suite: the receipts are dated
        # observations, and the publisher regenerates them on the next refresh.
        self.assertIn('snapshot_generated_at', receipt)

    def test_the_committed_valve_copy_is_the_official_bytes(self):
        copy = RECEIPTS / 'valve-live-2026-10-05.md'
        vendored = ROOT / 'data' / 'vrs' / 'standings_global_2026_10_05.md'
        self.assertTrue(copy.exists())
        self.assertEqual(copy.read_bytes(), vendored.read_bytes(),
                         'the retained official copy and the vendored input must be identical')
        import hashlib
        meta = json.loads((ROOT / 'data' / 'vrs' / 'meta.json').read_text())
        self.assertEqual(hashlib.sha256(copy.read_bytes()).hexdigest(), meta['sha256'])


class DirectoryIsNotAFakeTable(unittest.TestCase):
    def test_it_adds_no_match_row_to_the_validated_tables(self):
        # scripts.validate counts tr[data-match]; the directory must never
        # masquerade as a fixture row or the row counts would stop agreeing.
        directory, rows = directory_rows(INDEX)
        self.assertEqual(directory.select('tr[data-match]'), [])
        for row in rows:
            self.assertIsNone(row.get('data-match'))

    def test_it_publishes_no_probability_of_its_own(self):
        directory, _ = directory_rows(INDEX)
        text = directory.get_text(' ', strip=True)
        self.assertNotIn('% of', text)
        self.assertEqual(text.count('50/50'), 1, 'only the sentence refusing a default 50/50')
        self.assertIn('never a default 50/50', text)


if __name__ == '__main__':
    unittest.main()
