"""Replay final-day facts and links against retained source receipts, no network."""
import copy
import json
import unittest
from pathlib import Path
from scripts import build

ROOT=Path(__file__).resolve().parents[1]
NOTES=json.loads((ROOT/'data/analysis.json').read_text())
SNAP=json.loads((ROOT/'research/session-f4e34907/snapshot.json').read_text())
RESULTS=json.loads((ROOT/'research/session-f4e34907/probe/hltv-twc-results.json').read_text())

class FinalDayTests(unittest.TestCase):
    def test_every_published_series_replays_against_fresh_results(self):
        rows={r['url'].split('/')[4]: r for d in RESULTS['days'] for r in d['results']}
        for key in ('day_one','day_two','day_three_results','day_four_results'):
            for match in NOTES[key]['matches']:
                row=rows[match['match_url'].split('/')[4]]
                a,b=map(int,row['score'].split('-'))
                self.assertEqual(match['winner'],row['teams'][0 if a>b else 1])
                self.assertEqual(match['loser'],row['teams'][1 if a>b else 0])
                self.assertEqual(match['score'],f'{max(a,b)}-{min(a,b)}')

    def test_final_pair_and_utc_clock_replay(self):
        receipt=json.loads((ROOT/'research/session-f4e34907/probe/hltv-twc-2399417.json').read_text())
        card=NOTES['day_five_guidance']['not_listed'][1]
        self.assertEqual(receipt['teams'],card['teams'])
        self.assertEqual(receipt['start_utc'],card['start_utc'])
        self.assertEqual(['FURIA','BETBOOM'],card['teams'])
        self.assertEqual('FURIA',card['pick'])
        self.assertNotIn('probabilities',card)

    def test_front_page_targets_final_day_and_limitations(self):
        html=build.overview(SNAP)
        self.assertEqual('day-five-guidance',build.guidance_anchor(NOTES))
        self.assertIn('analysis.html#day-five-guidance',html)
        self.assertIn('analysis.html#day-five-guidance-unpriced',html)
        self.assertNotIn('have no participants yet',html)
        self.assertIn('picks.html',html)

    def test_known_pairs_do_not_render_unknown_pair_model_excuse(self):
        html=build.guidance_section(SNAP,NOTES,'day_five_guidance','day-five-guidance')
        self.assertNotIn('opponent pair is not known',html)
        self.assertIn('Research-only ranking baseline',html)
        self.assertIn('No independently replayed',html)

    def test_future_board_discovery_uses_exact_pair_and_start(self):
        data=copy.deepcopy(SNAP)
        template=copy.deepcopy(next(m for m in SNAP['matches'] if m['state']=='open' and m['probabilities']))
        template.update(id='future-final',teams=['FURIA','BETBOOM'],start='2026-10-18T15:00:00Z',probabilities=[.6,.4],pick='FURIA',method='exchange')
        data['matches'].append(template)
        html=build.guidance_section(data,NOTES,'day_five_guidance','day-five-guidance')
        self.assertIn('Current board line:',html)
        self.assertIn('expiry-checked pick board',html)
        self.assertNotIn('FURIA 60.0%',html)
        self.assertIn('evidence.html#match-future-final',html)
        template['start']='2026-10-19T15:00:00Z'
        html=build.guidance_section(data,NOTES,'day_five_guidance','day-five-guidance')
        self.assertNotIn('Current board line:',html)

if __name__=='__main__': unittest.main()
