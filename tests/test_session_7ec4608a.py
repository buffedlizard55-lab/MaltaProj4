"""Navigation regressions render current templates, never a stale build folder."""
import copy
import json
import unittest
from pathlib import Path
from bs4 import BeautifulSoup
from scripts.build import overview

ROOT = Path(__file__).resolve().parents[1]

class SummaryNavigationTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT/'data/latest.json').read_text())
        self.html = overview(copy.deepcopy(self.data))
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def test_focused_destinations(self):
        nav = self.soup.select_one('.exec-summary-links')
        self.assertIsNotNone(nav)
        self.assertEqual({a['href'] for a in nav.select('a')},
                         {'picks.html', '#picks-at-a-glance', 'unresolved.html', 'matches.html'})
        self.assertIn(f"All {len(self.data['matches'])} feed entries", nav.get_text())
        self.assertNotIn('{len(matches)}', nav.get_text())

    def test_navigation_precedes_hero(self):
        self.assertLess(self.html.index('id="freshness-strip"'), self.html.index('class="exec-summary-links"'))
        self.assertLess(self.html.index('class="exec-summary-links"'), self.html.index('class="hero"'))

    def test_glance_includes_exact_open_set(self):
        actual = {a['href'] for a in self.soup.select('a.glance-row')}
        expected = {'evidence.html#match-'+m['id'] for m in self.data['matches'] if m['state']=='open'}
        self.assertEqual(actual, expected)

    def test_summary_keeps_limitations(self):
        section = self.soup.select_one('#unresolved-summary')
        self.assertIsNotNone(section.select_one('#pick-limitations'))
        self.assertTrue(section.select('a[href="unresolved.html"]'))

    def test_mobile_rules_are_in_build_asset(self):
        css = (ROOT/'site/assets/style.css').read_text()
        self.assertIn('.exec-summary-links', css)
        self.assertIn('@media(max-width:650px)', css)
        self.assertIn('min-height:44px', css)

if __name__ == '__main__':
    unittest.main()
