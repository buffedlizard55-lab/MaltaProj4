"""Session 233b8a0e: a green pre-refresh gate, no silent CSS drift, and a
first-screen map to the picks on a phone.

What this session measured on `main` `dce494b` and what each test here keeps
fixed:

1. `python -m unittest discover -s tests` was red (8 failures, 1 error) and it
   runs *before* the refresh step in `pages.yml`, so every scheduled publish run
   died before collecting a line. Two causes: the committed root
   `assets/style.css` was one `}` short of the canonical `site/assets/style.css`
   (so the whole second half of the phone layout was nested inside a
   short-phone media query), and the independent verifier could not map a
   Hotspawn label onto the exchange's label for one fixture even though
   `data/identities.json` carries that rename with primary evidence.
2. Nothing repaired the root copy after the canonical stylesheet changed; only
   a staged publish brought them together. Staging now repairs it, and
   `scripts.validate` fails a build whose served stylesheet is unbalanced or
   differs from the canonical one.
3. At 320x568 the first phone screen held only the freshness strip: the
   always-visible executive summary that names the updated pick board rendered
   after all open cards (y=8827 on this snapshot). A never-folded, number-free
   map of destinations now sits directly under the strip.

Nothing here asserts a pick, price or probability; those are re-derived by
`research/session-0cc1138a/verify_0cc1138a.py` and `scripts.validate`.
"""
import copy
import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import stage_legacy, validate
from scripts.build import exec_quick_links, overview
from scripts.coverage_233b8a0e import RUNG_LABELS, report

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data' / 'latest.json').read_text(encoding='utf-8'))
INDEX = overview(copy.deepcopy(DATA))


class ServedStylesheetTests(unittest.TestCase):
    def test_the_served_stylesheet_is_balanced_and_canonical(self):
        served = (ROOT / 'assets' / 'style.css').read_text(encoding='utf-8')
        self.assertEqual(validate.stylesheet_problems(served), [])
        self.assertEqual((ROOT / 'assets' / 'style.css').read_bytes(),
                         (ROOT / 'site' / 'assets' / 'style.css').read_bytes())

    def test_an_unclosed_block_is_reported_not_ignored(self):
        broken = 'a{color:red}\n@media(max-width:650px){\n b{color:blue}\n'
        self.assertEqual(validate.stylesheet_problems(broken), ['1 unclosed block(s) at end of file'])
        # The exact 2026-10-24 defect: a nested rule swallowed the closing brace.
        drift = ('@media(max-width:650px) and (max-height:700px){\n'
                 '  body .prob-pair{font-size:17px}\n  /* comment */\n'
                 '/* next rule */\n@media(max-width:650px){x{y:1}}\n')
        self.assertTrue(validate.stylesheet_problems(drift))

    def test_an_extra_closing_brace_is_reported(self):
        self.assertEqual(validate.stylesheet_problems('a{color:red}}\n'),
                         ['unexpected closing brace on line 1'])

    def test_staging_repairs_a_drifted_root_copy(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'site' / 'assets').mkdir(parents=True)
            (root / 'assets').mkdir()
            canonical = 'a{color:red}\n'
            (root / 'site' / 'assets' / 'style.css').write_text(canonical)
            (root / 'assets' / 'style.css').write_text('a{color:red\n')
            self.assertTrue(stage_legacy.ensure_stylesheet_parity(root))
            self.assertEqual((root / 'assets' / 'style.css').read_text(), canonical)
            # A second call must be a no-op, so staging stays idempotent.
            self.assertFalse(stage_legacy.ensure_stylesheet_parity(root))

    def test_validate_stylesheet_accepts_the_repository_and_refuses_drift(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'site' / 'assets').mkdir(parents=True)
            (root / 'assets').mkdir()
            (root / 'site' / 'assets' / 'style.css').write_text('a{color:red}\n')
            (root / 'assets' / 'style.css').write_text('a{color:red}\n')
            self.assertTrue(validate.validate_stylesheet(root))
            (root / 'assets' / 'style.css').write_text('a{color:red\n')
            with self.assertRaises(AssertionError):
                validate.validate_stylesheet(root)


class FirstScreenPickMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.soup = BeautifulSoup(INDEX, 'html.parser')
        cls.nav = cls.soup.select_one('#exec-quick')

    def test_exists_once_and_is_never_folded(self):
        self.assertEqual(len(self.soup.select('#exec-quick')), 1)
        self.assertIsNotNone(self.nav)
        self.assertIsNone(self.nav.find_parent('details'))

    def test_sits_directly_between_the_strip_and_the_pick_list(self):
        for anchor in ('id="freshness-strip"', 'id="exec-quick"', 'id="exec-summary"',
                       'id="picks-at-a-glance"'):
            self.assertIn(anchor, INDEX)
        self.assertLess(INDEX.index('id="freshness-strip"'), INDEX.index('id="exec-quick"'))
        self.assertLess(INDEX.index('id="exec-quick"'), INDEX.index('id="picks-at-a-glance"'))

    def test_links_inside_the_site_to_every_destination_the_briefing_names(self):
        hrefs = [a['href'] for a in self.nav.select('a')]
        self.assertEqual(hrefs, ['picks.html', '#picks-at-a-glance', 'unresolved.html',
                                 'matches.html', 'review.html'])
        for href in hrefs:
            self.assertFalse(href.startswith('http'), href)

    def test_it_renders_no_number_and_no_pick(self):
        text = self.nav.get_text(' ', strip=True)
        self.assertNotIn('%', text)
        self.assertEqual(self.nav.select('.prob-pair, .pick, [data-count]'), [])

    def test_phone_rules_order_it_before_the_list_with_44px_targets(self):
        css = (ROOT / 'site' / 'assets' / 'style.css').read_text(encoding='utf-8')
        self.assertIn('body[data-page="index"] main>#exec-quick{order:4}', css)
        self.assertIn('body[data-page="index"] main>#picks-at-a-glance{order:5}', css)
        self.assertIn('.exec-quick a{display:flex;align-items:center;justify-content:center;min-height:44px', css)
        # The summary stays reachable and visible, just after the list.
        self.assertIn('body[data-page="index"] main>#exec-summary{order:6}', css)

    def test_shipped_page_carries_it(self):
        page = BeautifulSoup((ROOT / 'index.html').read_text(encoding='utf-8'), 'html.parser')
        self.assertIsNotNone(page.select_one('#exec-quick a[href="picks.html"]'))


class CoverageReportTests(unittest.TestCase):
    def setUp(self):
        self.summary = report(copy.deepcopy(DATA))

    def test_counts_add_up_on_the_committed_snapshot(self):
        s = self.summary
        self.assertEqual(s['rows_open'], s['rows_total'] - s['rows_past_dated'])
        self.assertEqual(s['rows_open'],
                         s['open_with_pick'] + s['open_unresolved'])
        self.assertLessEqual(s['open_with_probability'], s['open_with_pick'])
        self.assertEqual(s['open_research_only'], s['open_with_pick'] - s['open_with_probability'])
        self.assertEqual(sum(r['rows'] for r in s['rungs']), s['rows_open'])

    def test_every_method_in_the_snapshot_has_a_documented_rung(self):
        self.assertEqual(self.summary['unknown_methods'], [])
        labels = {method for method, _ in RUNG_LABELS}
        for row in DATA['matches']:
            if row['state'] == 'open':
                self.assertIn(row['method'], labels, row['id'])

    def test_unresolved_ledger_quotes_only_snapshot_values(self):
        unresolved = [m for m in DATA['matches'] if m['state'] == 'open' and not m.get('pick')]
        self.assertEqual(len(self.summary['unresolved_ledger']), len(unresolved))
        for row in self.summary['unresolved_ledger']:
            source = next(m for m in DATA['matches'] if m['id'] == row['id'])
            self.assertEqual(row['reason'], source.get('reason'))
            self.assertEqual([a['url'] for a in row['attempts']],
                             [a.get('url') for a in source.get('attempts') or []])

    def test_report_invents_nothing_for_a_synthetic_unresolved_row(self):
        doc = {'generated_at': '2026-10-24T00:00:00Z',
               'fixtures_observed_at': '2026-10-24T00:00:00Z', 'coverage': 'verified',
               'matches': [{'id': 'x1', 'teams': ['A', 'B'], 'state': 'open', 'pick': None,
                            'method': None, 'probabilities': None, 'start': '2026-10-25T00:00:00Z',
                            'competition': 'C', 'source_url': 'https://play.hotspawn.com/lobby',
                            'reason': 'Nothing verified.', 'attempts': []}]}
        summary = report(doc)
        self.assertEqual(summary['open_unresolved'], 1)
        self.assertEqual(summary['open_with_probability'], 0)
        self.assertEqual(summary['unresolved_ledger'][0]['attempts'], [])
        self.assertEqual(summary['unresolved_ledger'][0]['reason'], 'Nothing verified.')


if __name__ == '__main__':
    unittest.main()
