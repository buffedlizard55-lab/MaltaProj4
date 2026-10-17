"""Final-day navigation and source-access wording regressions (no network)."""
import copy
import json
import unittest
from pathlib import Path
from scripts import build

ROOT = Path(__file__).resolve().parents[1]

class FinalDayNavigation(unittest.TestCase):
    def test_link_and_label_select_the_same_day(self):
        notes = json.loads((ROOT / 'data/analysis.json').read_text())
        for key, anchor in [('day_three_guidance', 'guidance'),
                            ('day_four_guidance', 'day-four-guidance'),
                            ('day_five_guidance', 'day-five-guidance')]:
            notes['front_page_plan'] = key
            self.assertIs(build.front_page_plan(notes), notes[key])
            self.assertEqual('analysis.html#' + anchor, build.guidance_href(notes))
            self.assertEqual('analysis.html#' + anchor + '-unpriced',
                             build.guidance_href(notes, '-unpriced'))
            self.assertEqual(notes[key]['nav_label'], build.guidance_label(notes))

    def test_missing_selection_uses_latest_block(self):
        notes = json.loads((ROOT / 'data/analysis.json').read_text())
        notes.pop('front_page_plan', None)
        self.assertEqual('analysis.html#day-five-guidance', build.guidance_href(notes))

    def test_current_attempt_reason_is_not_replaced_by_an_old_403(self):
        data = json.loads((ROOT / 'research/harvest-621776e4/snapshot.json').read_text())
        row = copy.deepcopy(next(m for m in data['matches'] if m['state']=='open' and m['probabilities'] is None))
        row['attempts'] = [{'provider': 'GG.BET', 'status': 'unresolved',
                            'reason': 'HTTP 200; no validated numeric quote extracted',
                            'url': 'https://gg.bet/en/esports/counter-strike'}]
        data['matches'] = [row]
        html = build.access_limitations(data)
        self.assertIn('HTTP 200; no validated numeric quote extracted', html)
        self.assertNotIn('403', html)
        self.assertNotIn('Access refused', html)

    def test_source_reason_is_escaped(self):
        data = json.loads((ROOT / 'research/harvest-621776e4/snapshot.json').read_text())
        row = copy.deepcopy(next(m for m in data['matches'] if m['state']=='open' and m['probabilities'] is None))
        row['attempts'] = [{'provider': 'HLTV', 'reason': '<script>test</script>', 'status': 'error'}]
        data['matches'] = [row]
        html = build.access_limitations(data)
        self.assertNotIn('<script>test</script>', html)
        self.assertIn('&lt;script&gt;test&lt;/script&gt;', html)

if __name__ == '__main__':
    unittest.main()
