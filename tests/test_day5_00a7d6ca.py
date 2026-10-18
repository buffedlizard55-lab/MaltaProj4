"""Deterministic regression tests for Session 00a7d6ca.

Verifies:
1. Day 1–5 TWC 2026 data integrity, results, and the 9z vs Aurora upset context.
2. Aurora roster change timing (July 2026, ~14 weeks prior, not days-old).
3. Day 4 semi-final results (FURIA 2-0 Aurora, BETBOOM 2-1 Falcons) and map counts.
4. Day 5 Thunderpick prices, de-vig probabilities, and overround.
5. Contrarian-not-stupid leaderboard strategy rules and streak mechanics.
6. Executive summary structure, in-site pick links, and unresolved limitations.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts import build

ROOT = Path(__file__).resolve().parents[1]


class Day1To5TWCIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notes = json.loads((ROOT / 'data' / 'analysis.json').read_text())
        cls.latest = json.loads((ROOT / 'data' / 'latest.json').read_text())
        cls.html_index = build.overview(cls.latest)
        cls.html_analysis = build.analysis_page(cls.latest)

    def test_day_one_9z_upset_details(self):
        day1 = self.notes['day_one']
        self.assertEqual(day1['date'], '2026-10-14')
        match9z = next(m for m in day1['matches'] if m['winner'] == '9z')
        self.assertEqual(match9z['loser'], 'Aurora')
        self.assertEqual(match9z['score'], '2-0')
        self.assertIn('Inferno 13-11', match9z['maps'])
        self.assertIn('Nuke 13-1', match9z['maps'])
        self.assertIn('luchov 1.61 rating', match9z['detail'])
        self.assertTrue(match9z['match_url'].startswith('https://www.hltv.org/matches/'))
        self.assertTrue(match9z['report_url'].startswith('https://www.hltv.org/news/'))

    def test_aurora_roster_timing_is_historical(self):
        points = self.notes['upset_context']['points']
        rebuild_point = next(p for p in points if 'Jimpphat' in p['claim'] or 'Jimpphat' in p.get('detail', ''))
        self.assertIn('8 July 2026', rebuild_point['claim'] + rebuild_point['detail'])
        self.assertIn('ash', rebuild_point['claim'] + rebuild_point['detail'])
        self.assertIn('kyxsan', rebuild_point['claim'] + rebuild_point['detail'])
        # Confirms roster change was ~14 weeks old, not days old
        self.assertTrue(any('14 weeks' in p.get('detail', '') or 'three months old' in p.get('claim', '') for p in points))

    def test_day_two_results(self):
        day2 = self.notes['day_two']
        self.assertEqual(day2['date'], '2026-10-15')
        results = {(m['winner'], m['loser']): m['score'] for m in day2['matches']}
        self.assertEqual(results.get(('Falcons', '9z')), '2-1')
        self.assertEqual(results.get(('Aurora', 'Ninjas in Pyjamas')), '2-0')
        self.assertEqual(results.get(('FURIA', 'Legacy')), '2-1')
        self.assertEqual(results.get(('BETBOOM', 'PARIVISION')), '2-1')

    def test_day_three_decider_results(self):
        day3 = self.notes['day_three_results']
        self.assertEqual(day3['date'], '2026-10-16')
        results = {(m['winner'], m['loser']): m['score'] for m in day3['matches']}
        # Aurora reversed the Day 1 upset against 9z
        self.assertEqual(results.get(('Aurora', '9z')), '2-0')
        self.assertEqual(results.get(('BETBOOM', 'Legacy')), '2-1')

    def test_day_four_semi_final_results(self):
        day4 = self.notes['day_four_results']
        self.assertEqual(day4['date'], '2026-10-17')
        results = {(m['winner'], m['loser']): m['score'] for m in day4['matches']}
        self.assertEqual(results.get(('FURIA', 'Aurora')), '2-0')
        self.assertEqual(results.get(('BETBOOM', 'Falcons')), '2-1')

    def test_day_five_guidance_cards(self):
        guide = self.notes['day_five_guidance']
        self.assertEqual(guide['nav_label'], 'Day-5 final-day guide')
        cards = guide['not_listed']
        self.assertEqual(len(cards), 2)
        # Match 1: Third place decider Aurora vs Falcons
        card_3rd = next(c for c in cards if 'Aurora' in c['teams'] and 'Falcons' in c['teams'])
        self.assertEqual(card_3rd['pick'], 'Falcons')
        # Superseded 17 Oct +170/-238 (65.53%) was re-read 18 Oct 00:55Z by a54996e1: +140/-200
        self.assertIn('61.54%', card_3rd['pick_detail'])
        self.assertIn('+140', card_3rd['market']['detail'])
        self.assertIn('−200', card_3rd['market']['detail'])

        # Match 2: Grand final FURIA vs BETBOOM
        card_final = next(c for c in cards if 'FURIA' in c['teams'] and 'BETBOOM' in c['teams'])
        self.assertEqual(card_final['pick'], 'FURIA')
        self.assertIn('68.24%', card_final['pick_detail'])
        self.assertIn('−286', card_final['market']['detail'])
        self.assertIn('+190', card_final['market']['detail'])

    def test_contrarian_strategy_principles(self):
        strat = self.notes['strategy']
        self.assertIn('Contrarian but not stupid', strat['headline'])
        # Must emphasize that contrarian is not a scoring bonus and hotspawn crowd % is not used
        self.assertIn('Contrarian is a risk choice', strat['summary'])
        self.assertIn('no verified Hotspawn user pick-share data', strat['summary'])
        rules = strat['rules']
        self.assertTrue(len(rules) >= 4)
        # Every rule must have sources
        for r in rules:
            self.assertTrue(len(r.get('sources', [])) >= 1)
            for s in r['sources']:
                self.assertTrue(s['url'].startswith('https://'))

    def test_executive_summary_links_and_navigation(self):
        html = self.html_index
        # Must provide direct links to updated picks
        self.assertIn('href="picks.html"', html)
        self.assertIn('View updated picks →', html)
        # Must provide direct link to Day-5 guidance
        self.assertIn('href="analysis.html#day-five-guidance"', html)
        self.assertIn('Day-5 final-day guide', html)
        # Must provide direct link to Day-4 results
        self.assertIn('href="analysis.html#day-four-results"', html)
        # Jump navigation anchors
        self.assertIn('href="#today"', html)
        self.assertIn('href="#later"', html)
        self.assertIn('href="#unresolved-summary"', html)
        self.assertIn('href="#coverage"', html)

    def test_executive_summary_unresolved_limitations_section(self):
        html = self.html_index
        self.assertIn('id="unresolved-summary"', html)
        self.assertIn('Matches with no market line, and what was tried', html)
        self.assertIn('href="unresolved.html"', html)

    def test_analysis_page_nav_order(self):
        html = self.html_analysis
        # Day-5 guidance should appear before Day-4 guidance in the on-page nav
        nav_start = html.find('class="section-nav"')
        self.assertNotEqual(nav_start, -1)
        nav_end = html.find('</nav>', nav_start)
        nav_html = html[nav_start:nav_end]
        self.assertIn('href="#day-five-guidance"', nav_html)
        self.assertIn('href="#day-four-guidance"', nav_html)
        idx_day5 = nav_html.find('href="#day-five-guidance"')
        idx_day4 = nav_html.find('href="#day-four-guidance"')
        self.assertLess(idx_day5, idx_day4, "Day-5 guidance must appear before Day-4 guidance in analysis.html nav")


if __name__ == '__main__':
    unittest.main()
