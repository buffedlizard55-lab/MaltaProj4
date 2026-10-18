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

class ExcludedEventDiagnostics(unittest.TestCase):
    def fixture(self):
        data = json.loads((ROOT / 'research/session-cc88483d/snapshot.json').read_text())
        return copy.deepcopy(next(m for m in data['matches'] if m['id']=='1082019'))

    def event(self):
        return json.loads((ROOT / 'research/session-cc88483d/targeted/hacha-event.json').read_text())['data'][0]

    def test_contradictory_ended_event_is_reported_but_not_priced(self):
        from scripts.core import record_polymarket_exclusions, polymarket_candidates
        event = self.event()
        self.assertTrue(event['ended'])
        self.assertTrue(next(m for m in event['markets'] if m['id']=='5796276')['acceptingOrders'])
        self.assertEqual([], polymarket_candidates([event], '2026-10-17T20:28:00Z'))
        fixture = self.fixture()
        record_polymarket_exclusions([fixture], [event], '2026-10-17T20:28:00Z')
        self.assertIsNone(fixture['pick'])
        self.assertIsNone(fixture['probabilities'])
        attempt = fixture['attempts'][-1]
        self.assertEqual('rejected', attempt['status'])
        self.assertIn('ended=true', attempt['reason'])
        self.assertEqual('1203504', attempt['event_status']['id'])

    def test_diagnostic_cannot_overwrite_featured_pick(self):
        from scripts.core import record_polymarket_exclusions
        fixture = self.fixture()
        fixture.update(probabilities=[.6,.4], pick='Hacha', method='exchange')
        before = copy.deepcopy(fixture)
        record_polymarket_exclusions([fixture], [self.event()], '2026-10-17T20:28:00Z')
        self.assertEqual(before, fixture)

    def test_no_diagnostic_for_wrong_opponents_or_map_only(self):
        from scripts.core import record_polymarket_exclusions
        for variant in ('wrong_opponents', 'map_only'):
            fixture = self.fixture()
            event = self.event()
            if variant == 'wrong_opponents':
                fixture['teams'] = ['Different', 'Opponents']
            else:
                for market in event['markets']:
                    market['sportsMarketType'] = 'child_moneyline'
            before = copy.deepcopy(fixture)
            record_polymarket_exclusions([fixture], [event], '2026-10-17T20:28:00Z')
            self.assertEqual(before, fixture)

class FinalDayEvidenceReplay(unittest.TestCase):
    def setUp(self):
        self.notes = json.loads((ROOT / 'data/analysis.json').read_text())
        self.plan = self.notes['day_five_guidance']
        self.capture = ROOT / 'research/session-cc88483d/probe'

    def test_every_published_series_replays_from_hltv_results(self):
        raw = json.loads((self.capture / 'hltv-twc-results.json').read_text())
        observed = {r['url']:r for d in raw['days'] for r in d['results']}
        self.assertEqual(12, len(observed))
        for key in ('day_one','day_two','day_three_results','day_four_results'):
            for match in self.notes[key]['matches']:
                row = observed[match['match_url']]
                scores = [int(n) for n in row['score'].split('-')]
                winner = row['teams'][scores.index(max(scores))]
                self.assertEqual(match['winner'].casefold(), winner.casefold())
                self.assertEqual(match['score'], '%d-%d' % (max(scores),min(scores)))

    def test_research_leans_replay_fixture_rank_order_and_start(self):
        for card, ident in zip(self.plan['not_listed'], ['2399416','2399417']):
            raw = json.loads((self.capture / ('hltv-twc-'+ident+'.json')).read_text())
            self.assertEqual(200, raw['http_status'])
            self.assertEqual(raw['teams'], card['teams'])
            ranks = {r['team']:r['hltv_rank'] for r in raw['ranks']}
            self.assertEqual(min(ranks,key=ranks.get),card['pick'])
            self.assertIn(raw['start_utc'][11:16]+' UTC',card['timing'])
            self.assertIn('expires_at',card['market'])
            self.assertIn('polymarket', card['market']['url'])
            for key in ('probabilities','fair_odds','points'):
                self.assertNotIn(key,card)
            if 'book_line' in card:
                # any second line must be labelled a cross-check, never a second price
                self.assertIn('cross-check', card['book_line']['label'])

    def test_final_map_load_is_a_count_not_a_fatigue_estimate(self):
        raw = json.loads((self.capture / 'hltv-twc-results.json').read_text())
        counts = {'FURIA':0,'BETBOOM':0}
        for day in raw['days']:
            for row in day['results']:
                for team in counts:
                    if team in row['teams']:
                        counts[team] += sum(int(n) for n in row['score'].split('-'))
        self.assertEqual({'FURIA':7,'BETBOOM':11},counts)
        self.assertIn('7 and 11 maps',self.plan['not_listed'][1]['why'])
        self.assertIn('None of this quantifies fatigue',self.plan['not_listed'][1]['why'])
