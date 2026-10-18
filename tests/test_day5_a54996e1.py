"""Session a54996e1: Day-5 final-day re-read (2026-10-18) — deterministic, no network."""
import json, unittest
from pathlib import Path
from scripts.day5_a54996e1 import dec, devig
ROOT = Path(__file__).resolve().parents[1]

class Day5RereadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((ROOT/'research/session-a54996e1/day5-lines.json').read_text())
        cls.notes = json.loads((ROOT/'data/analysis.json').read_text())
        cls.guide = cls.notes['day_five_guidance']

    def test_devig_arithmetic(self):
        probs, total = devig({'Aurora': 140, 'Falcons': -200})
        self.assertAlmostEqual(probs['Falcons'], 0.6153846, places=6)
        self.assertAlmostEqual(probs['Aurora'], 0.3846154, places=6)
        self.assertAlmostEqual(total, 1.0833333, places=6)
        probs2, total2 = devig({'FURIA': -286, 'BETBOOM': 190})
        self.assertAlmostEqual(probs2['FURIA'], 0.682409, places=6)
        self.assertAlmostEqual(total2, 1.085760, places=6)
        self.assertAlmostEqual(dec(140), 2.4); self.assertAlmostEqual(dec(-200), 1.5)

    def test_cards_match_receipt_and_pick_is_favourite(self):
        cards = {tuple(c['teams']): c for c in self.guide['not_listed']}
        third, final = cards[('Aurora','Falcons')], cards[('FURIA','BETBOOM')]
        self.assertEqual(third['pick'], 'Falcons')
        self.assertIn('60.5%', third['pick_detail'])
        self.assertEqual(final['pick'], 'FURIA')
        self.assertIn('70.5%', final['pick_detail'])
        # 18 Oct: the board exchange row is primary; Thunderpick stays a cross-check.
        for c, pct in ((third, '61.54%'), (final, '68.24%')):
            self.assertTrue(c['market']['url'].startswith('https://gamma-api.polymarket.com/'))
            self.assertIn(c['market']['observed_at'], ('2026-10-18T00:45:16Z', '2026-10-18T00:49:15Z'))
            self.assertIn(c['market']['expires_at'], ('2026-10-18T08:45:16Z', '2026-10-18T08:49:15Z'))
            self.assertTrue(c['market']['receipt_url'].endswith('receipt-2026-10-18.json'))
            self.assertIn('thunderpick.io', c['book_line']['url'])
            self.assertEqual(c['book_line']['expires_at'], '2026-10-18T08:55:00Z')
            self.assertIn(pct, c['book_line']['detail'])
            self.assertIn('cross-check', c['book_line']['label'])
            self.assertIn('line_move', c)

    def test_line_move_is_recorded_not_hidden(self):
        text = json.dumps(self.guide)
        self.assertIn('line_move', text); self.assertIn('+170', text)

    def test_hotspawn_listing_corrected_by_harvest(self):
        # 00:48Z lobby read had no Sunday rows; 00:52Z verified harvest listed both.
        self.assertIn('00:48', json.dumps(self.guide))
        self.assertTrue(all(c['now_listed'] is True for c in self.guide['not_listed']))
        self.assertEqual({c['hotspawn_id'] for c in self.guide['not_listed']}, {'1080209','1080210'})

    def test_every_open_row_has_pick_or_flagged_reason(self):
        latest = json.loads((ROOT/'data/latest.json').read_text())
        for r in latest['matches']:
            if r['state'] == 'open':
                self.assertTrue(r.get('pick') or r.get('reason'), r['id'])

    def test_day1_to_day4_results_still_replay(self):
        n = self.notes
        self.assertEqual((n['day_one']['matches'][0]['winner'], n['day_one']['matches'][0]['score']), ('9z','2-0'))
        self.assertEqual({(m['winner'],m['loser']):m['score'] for m in n['day_four_results']['matches']},
                         {('FURIA','Aurora'):'2-0', ('BETBOOM','Falcons'):'2-1'})

if __name__ == '__main__':
    unittest.main()
