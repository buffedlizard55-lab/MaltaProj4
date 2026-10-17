"""Regressions for empty-board navigation and evidence-led contrarian wording."""
import copy
import json
import unittest
from pathlib import Path
from bs4 import BeautifulSoup
from scripts import build

ROOT = Path(__file__).resolve().parents[1]

class DashboardAuditTests(unittest.TestCase):
    def test_jump_targets_exist_with_no_priced_rows(self):
        data = json.loads((ROOT / 'data/latest.json').read_text())
        for row in data['matches']:
            row.update(probabilities=None, pick=None, method=None)
        html = build.overview(data)
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.select('.jump-nav a'):
            self.assertIsNotNone(soup.find(id=a['href'][1:]), a['href'])
        self.assertNotIn('Every other open fixture on the board carries a pick', html)

    def test_every_strategy_rule_links_its_evidence(self):
        data = json.loads((ROOT / 'data/latest.json').read_text())
        soup = BeautifulSoup(build.analysis_page(data), 'html.parser')
        for row in soup.select('#strategy tbody tr'):
            self.assertTrue(row.select('a[href^="https://"]'))

    def test_day_three_map_totals_support_rest_counterweight(self):
        notes = json.loads((ROOT / 'data/analysis.json').read_text())
        actual = {}
        for team in ('FURIA', 'Falcons', 'Aurora', 'BETBOOM'):
            matches = [(day['date'], sum(map(int, m['score'].split('-'))))
                       for day in (notes['day_one'], notes['day_two'], notes['day_three_results'])
                       for m in day['matches'] if team in (m['winner'], m['loser'])]
            actual[team] = (matches[-1][0], sum(x[1] for x in matches))
        self.assertEqual({'FURIA': ('2026-10-15', 5), 'Falcons': ('2026-10-15', 5),
                          'Aurora': ('2026-10-16', 6), 'BETBOOM': ('2026-10-16', 8)}, actual)
        summary = notes['day_four_guidance']['summary']
        self.assertIn('not an upset advantage', summary)
        self.assertIn('No verified user pick-share', summary)
        self.assertNotIn('three three-map', json.dumps(notes['day_four_guidance']['fixtures']))
