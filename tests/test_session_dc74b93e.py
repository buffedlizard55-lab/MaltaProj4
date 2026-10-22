"""Independent policy checks for the committed dashboard snapshot.

These checks are intentionally method-agnostic: they permit a genuinely
unresolved row only when it is explicitly fail-closed, and never require a
made-up percentage merely to achieve headline coverage.
"""
import json
import math
import unittest
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/latest.json').read_text())
ROWS = DATA['matches']
OPEN = [row for row in ROWS if row.get('state') == 'open']


class TestIndependentBoardAudit(unittest.TestCase):
    def test_every_open_fixture_has_a_pick_or_explicit_fail_closed_reason(self):
        self.assertTrue(OPEN, 'the retained snapshot must contain open fixtures')
        for row in OPEN:
            with self.subTest(fixture=row['id']):
                if row.get('pick') is None:
                    self.assertEqual(row.get('method'), 'unresolved')
                    self.assertTrue(row.get('reason'))
                else:
                    self.assertIn(row['pick'], row['teams'])

    def test_every_published_probability_is_a_valid_two_team_pair(self):
        for row in OPEN:
            with self.subTest(fixture=row['id']):
                probabilities = row.get('probabilities')
                if probabilities is None:
                    self.assertTrue(str(row.get('method', '')).startswith('research_') or
                                    row.get('method') == 'unresolved')
                    self.assertIsNone(row.get('fair_odds'))
                    continue
                self.assertEqual(len(probabilities), 2)
                self.assertTrue(all(math.isfinite(float(p)) and 0 < float(p) < 1
                                    for p in probabilities))
                self.assertAlmostEqual(sum(probabilities), 1.0, places=9)
                self.assertIn(row.get('pick'), row['teams'])
                self.assertIsInstance(row.get('evidence'), list)
                self.assertTrue(row['evidence'], 'a percentage needs retained evidence')
                providers = {e.get('provider', '').casefold() for e in row['evidence']}
                self.assertFalse(any('hotspawn' in provider for provider in providers),
                                 'Hotspawn is inventory only, never a probability input')

    def test_open_fixture_sources_and_probability_inputs_are_linked(self):
        for row in OPEN:
            with self.subTest(fixture=row['id']):
                self.assertTrue(row.get('fixture_sources'))
                self.assertTrue(all(source.get('url', '').startswith('https://')
                                    for source in row['fixture_sources']))
                for evidence in row.get('evidence', []):
                    link = evidence.get('url') or evidence.get('api_url')
                    self.assertTrue(link and link.startswith('https://'), evidence)
                if row.get('method') == 'model_vrs':
                    self.assertTrue(any('ValveSoftware/counter-strike_regional_standings' in
                                        (e.get('url', '') + e.get('api_url', ''))
                                        for e in row.get('evidence', [])))

    def test_executive_summary_has_direct_pick_and_unresolved_routes(self):
        soup = BeautifulSoup((ROOT / 'index.html').read_text(), 'html.parser')
        hrefs = {a.get('href') for a in soup.find_all('a')}
        self.assertIn('picks.html', hrefs)
        self.assertIn('unresolved.html', hrefs)
        self.assertIn('matches.html', hrefs)
        self.assertIsNotNone(soup.find('meta', attrs={'name': 'viewport'}))


if __name__ == '__main__':
    unittest.main()
