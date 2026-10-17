"""Guardrails for the independent Day-4 contrarian-logic review.

The tests use retained result/line evidence and the rendered analysis page; they do
not fetch external sources or turn a schedule/ranking observation into a probability.
"""
import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import build

ROOT = Path(__file__).resolve().parents[1]
NOTES = json.loads((ROOT / 'data/analysis.json').read_text())
SNAPSHOT = json.loads((ROOT / 'data/latest.json').read_text())


class DayFourContrarianLogicTests(unittest.TestCase):
    def setUp(self):
        self.guidance = NOTES['day_four_guidance']
        self.cards = {row['label']: row for row in self.guidance['not_listed']}

    def test_summary_does_not_call_shorter_underdog_rest_an_upset_edge(self):
        summary = self.guidance['summary'].lower()
        self.assertIn("neither is on hotspawn's cs2 feed", summary)
        self.assertIn('aurora is the more measured contrarian option', summary)
        self.assertIn('aurora also played later and more maps than furia, a counterweight', summary)
        self.assertIn('roughly 22-hour turnaround', summary)
        self.assertIn('short turnaround weighs against it, not for it', summary)
        self.assertIn('no verified user pick-share data', summary)
        self.assertIn('00:00', summary)
        self.assertNotIn('only real underdog argument is betboom', summary)

    def test_betboom_upset_case_and_schedule_counterweight_are_separated(self):
        card = self.cards['Falcons vs BETBOOM']
        self.assertEqual('Falcons', card['pick'])
        self.assertIn('20–24%', card['pick_detail'])
        why = card['why'].lower()
        self.assertIn('2-0 head-to-head win over falcons', why)
        self.assertIn('schedule is a counterweight, not an edge for betboom', why)
        self.assertIn('do not cite rest as support for the underdog', why)
        self.assertNotIn('only sourced argument for the underdog is the schedule', why)

    def test_both_semifinals_are_marked_as_not_on_the_hotspawn_board(self):
        self.assertEqual({'FURIA vs Aurora', 'Falcons vs BETBOOM'}, set(self.cards))
        for card in self.cards.values():
            self.assertFalse(card['now_listed'])
            self.assertIn(card['pick'], card['teams'])

    def test_last_played_dates_and_map_loads_reproduce_from_result_cards(self):
        days = [NOTES['day_one'], NOTES['day_two'], NOTES['day_three_results']]
        expected = {
            'FURIA': ('2026-10-15', 5),
            'Falcons': ('2026-10-15', 5),
            'Aurora': ('2026-10-16', 6),
            'BETBOOM': ('2026-10-16', 8),
        }
        actual = {}
        for team in expected:
            appearances = []
            for day in days:
                for match in day['matches']:
                    if team in (match['winner'], match['loser']):
                        score = [int(value) for value in match['score'].split('-')]
                        appearances.append((day['date'], sum(score)))
            self.assertTrue(appearances, team)
            actual[team] = (appearances[-1][0], sum(maps for _, maps in appearances))
        self.assertEqual(expected, actual)
        rest_point = next(point for point in self.guidance['points']
                          if point['claim'].startswith('Rest is a counterweight'))
        detail = rest_point['detail'].lower()
        self.assertIn('furia and falcons each logged five event maps', detail)
        self.assertIn('aurora logged six', detail)
        self.assertIn('betboom eight', detail)
        for team in expected:
            self.assertIn(team.lower(), detail)
        self.assertIn('not a measured fatigue effect', detail)
        self.assertTrue(rest_point['source'].startswith('https://www.hltv.org/'))

    def test_july_roster_change_is_not_misreported_as_day_four_onboarding(self):
        roster_rule = NOTES['strategy']['rules'][0]
        self.assertIn('recent and structural', roster_rule['rule'])
        self.assertIn('July 2026', roster_rule['why'])
        self.assertIn('not a fresh day-four onboarding explanation', roster_rule['why'])
        self.assertTrue(any('45082' in source['url'] for source in roster_rule['sources']))

    def test_each_strategy_table_row_has_absolute_source_links_in_rendered_html(self):
        rules = NOTES['strategy']['rules']
        self.assertEqual(6, len(rules))
        for rule in rules:
            self.assertTrue(rule.get('sources'), rule['rule'])
            for source in rule['sources']:
                self.assertTrue(source['url'].startswith('https://'), source)
                self.assertTrue(source.get('label'), source)

        soup = BeautifulSoup(build.analysis_page(SNAPSHOT), 'html.parser')
        section = soup.find('section', id='strategy')
        self.assertIsNotNone(section)
        table = section.find('table')
        self.assertEqual('Sources', table.select_one('thead th:last-child').get_text(strip=True))
        rows = table.select('tbody tr')
        self.assertEqual(len(rules), len(rows))
        for rule, row in zip(rules, rows):
            links = row.select('td:last-child a[href]')
            self.assertTrue(links, rule['rule'])
            self.assertEqual({source['url'] for source in rule['sources']},
                             {link['href'] for link in links}, rule['rule'])

    def test_no_crowd_share_or_calibrated_leaderboard_advantage_is_claimed(self):
        strategy = NOTES['strategy']
        self.assertIn('no verified Hotspawn user pick-share data', strategy['summary'])
        self.assertTrue(any('no leaderboard advantage is claimed' in item.lower()
                            for item in strategy['unverified']))
        self.assertTrue(any('points come from tier' in point['claim'].lower()
                            and 'participants0_picked_percent' in point['detail']
                            for point in self.guidance['points']))


class DayOneHltvSourceCoverageTests(unittest.TestCase):
    """Ensure all four Day-1 rows use the retained HLTV match-page evidence."""

    def test_day_one_maps_match_retained_hltv_captures(self):
        receipts = json.loads((ROOT / 'verification-76712ccc/TWC-RESULTS.json').read_text())
        expected_maps = {
            '2399384': 'Inferno 13-11, Nuke 13-1',
            '2399385': 'Ancient 16-13 (overtime), Dust2 13-6',
            '2399386': 'Dust2 13-11, Mirage 16-14 (overtime)',
            '2399387': 'Ancient 13-10, Mirage 13-9',
        }
        rows = NOTES['day_one']['matches']
        self.assertEqual(set(expected_maps), {
            row['match_url'].split('/matches/')[1].split('/')[0] for row in rows
        })
        for row in rows:
            match_id = row['match_url'].split('/matches/')[1].split('/')[0]
            capture = receipts['results'][match_id]
            self.assertEqual(capture['url'], row['match_url'])
            self.assertEqual(expected_maps[match_id], row['maps'])
            self.assertEqual(len(capture['sha256']), 64)
            self.assertTrue(row['report_url'].startswith('https://www.hltv.org/'))

        falcons_nip = next(row for row in rows if '/2399385/' in row['match_url'])
        self.assertNotIn('esportbet.com', falcons_nip['report_url'])
        self.assertIn('not the previously cited betting preview', falcons_nip['flag'])


if __name__ == '__main__':
    unittest.main()
