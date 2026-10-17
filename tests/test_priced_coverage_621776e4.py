"""Session 621776e4: priced coverage for renamed clubs, and the day-4 guidance block.

Two behaviours are pinned here:

1. A fixture whose three sources spell the same club three different ways must still
   be priced, provided the alias is registered with primary sources and the opponent
   pair and UTC start agree exactly. Fixture 1081515 (Apogee Betclic vs Nemesis) had
   no pick at all on 16 October because Polymarket's market for it is labelled
   "Betclic Apogee Esports vs Team Nemesis"; the row's own attempt record named that
   market as the near-miss. The captured market fields below are the real ones from
   research/harvest-621776e4/polymarket-active-cs2.json, read at 19:35 UTC.

2. data/analysis.json carries one guidance block per tournament day and the build
   renders every one of them, with the newest owning the stable #guidance anchor that
   the executive summary links to. Nothing here supplies a probability: the model
   percentages in the day-4 cards are recomputed by scripts.vrs from Valve's official
   standings file at build time.
"""
import json
import unittest
from pathlib import Path

from scripts import build, vrs
from scripts.core import dt, iso, norm, normalize_fixtures, polymarket_candidates, resolve

ROOT = Path(__file__).resolve().parents[1]
NOW = dt('2026-10-16T19:36:00Z')
OBSERVED = '2026-10-16T19:35:53.077051Z'

# Real captured fields for Polymarket market 5776037 (event 1200120).
MARKET = {
    'id': '5776037',
    'question': 'Counter-Strike: Betclic Apogee Esports vs Team Nemesis (BO3) - PGL Bucharest Closed Qualifier Playoffs',
    'sportsMarketType': 'moneyline',
    'active': True, 'closed': False, 'acceptingOrders': True,
    'outcomes': '["Betclic Apogee Esports","Team Nemesis"]',
    'outcomePrices': '["0.32","0.68"]',
    'gameStartTime': '2026-10-17 14:00:00+00',
    'updatedAt': '2026-10-16T19:34:52.308347Z',
    'bestBid': .3, 'bestAsk': .34,
    'liquidity': '3296.7755',
}
EVENT = {'id': '1200120', 'slug': 'cs2-bca-nem-2026-10-17', 'sport': {'sport': 'cs2'},
         'closed': False, 'live': False, 'ended': False, 'markets': [MARKET]}

FIXTURE = {'id': '1081515', 'sport_alias': 'cs2',
           'participants0_name': 'Apogee Betclic', 'participants1_name': 'Nemesis',
           'competition_name': 'PGL Bucharest 2027: Closed Qualifier',
           'status': 'scheduled', 'scheduled_start_time': '2026-10-17T14:00:00Z',
           'lock_time': '2026-10-17T13:54:00Z'}


def fixture(**over):
    return normalize_fixtures([FIXTURE | over], {}, NOW)[0]


class RenamedClubPricingTests(unittest.TestCase):
    def test_all_three_labels_fold_to_one_identity(self):
        self.assertEqual(norm('Apogee Betclic'), norm('Betclic Apogee Esports'))
        self.assertEqual(norm('Betclic Apogee Esports'), norm('Betclic'))
        self.assertEqual(norm('Nemesis'), norm('Team Nemesis'))

    def test_the_registered_alias_carries_primary_sources(self):
        register = json.loads((ROOT / 'data/identities.json').read_text())['aliases']
        club = next(a for a in register if a['canonical'] == 'Betclic Apogee Esports')
        nemesis = next(a for a in register if a['canonical'] == 'Nemesis')
        for entry, names in ((club, {'Apogee Betclic', 'Betclic Apogee Esports', 'Betclic'}),
                             (nemesis, {'Nemesis', 'Team Nemesis'})):
            self.assertEqual(names, set(entry['names']))
            self.assertTrue(entry['source'].startswith('https://www.hltv.org/matches/'))
            self.assertTrue(entry['additional_source'].startswith('https://gamma-api.polymarket.com/'))
            self.assertGreater(len(entry['basis']), 120)
        self.assertEqual(len([a for a in register if a['canonical'] == 'Betclic Apogee Esports']), 1,
                         'One club must not be registered twice under competing canonicals')

    def test_the_renamed_fixture_is_priced_from_the_exchange(self):
        f = fixture()
        resolve(f, polymarket_candidates([EVENT], OBSERVED), 'Polymarket', NOW)
        self.assertIsNotNone(f['probabilities'], f['attempts'])
        self.assertEqual(f['method'], 'exchange')
        self.assertEqual(f['pick'], 'Nemesis')
        self.assertAlmostEqual(f['probabilities'][0], .32, places=9)
        self.assertAlmostEqual(f['probabilities'][1], .68, places=9)
        self.assertAlmostEqual(f['fair_odds'][0], 1 / .32, places=9)
        quote = f['evidence'][0]
        self.assertEqual(quote['id'], '5776037')
        self.assertAlmostEqual(quote['spread'], .04, places=9)
        self.assertAlmostEqual(quote['liquidity'], 3296.7755, places=4)
        self.assertIsNone(quote['warning'])
        self.assertTrue(any(i['canonical'] == 'Nemesis' for i in quote['identity_sources']))

    def test_the_identity_is_still_exact_opponent_and_exact_start(self):
        # Same market, different fixture start: the alias must not bridge the gap.
        f = fixture(scheduled_start_time='2026-10-17T15:00:00Z', lock_time='2026-10-17T14:54:00Z')
        resolve(f, polymarket_candidates([EVENT], OBSERVED), 'Polymarket', NOW)
        self.assertIsNone(f['probabilities'])
        self.assertEqual('No exact team-pair and UTC-start match in retrieved feed.', f['attempts'][0]['reason'])

    def test_the_alias_does_not_bridge_a_different_opponent(self):
        f = fixture(participants1_name='Nemiga')
        resolve(f, polymarket_candidates([EVENT], OBSERVED), 'Polymarket', NOW)
        self.assertIsNone(f['probabilities'])


class DayFourGuidanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notes = json.loads((ROOT / 'data/analysis.json').read_text())
        cls.plans = build.guidance_plans(cls.notes)

    def test_every_day_keeps_its_own_block_and_the_last_one_is_current(self):
        self.assertEqual([key for key, _ in self.plans], ['day_three_guidance', 'day_four_guidance'])
        self.assertEqual(build.latest_guidance(self.notes), self.notes['day_four_guidance'])
        self.assertEqual(build.guidance_label(self.notes),
                         self.notes['day_four_guidance']['nav_label'])
        self.assertEqual(self.notes['day_three_guidance']['anchor'], 'guidance-day3')

    def test_day_four_block_is_complete_and_sourced(self):
        plan = self.notes['day_four_guidance']
        for key in ('date', 'headline', 'summary', 'points', 'fixtures', 'not_listed', 'unverified'):
            self.assertIn(key, plan)
        for point in plan['points']:
            self.assertTrue(point['source'].startswith('https://'), point)
            self.assertGreater(len(point['claim']), 10)
            self.assertGreater(len(point['detail']), 40)
        for f in plan['fixtures']:
            for key in ('hotspawn_id', 'label', 'event', 'contrarian', 'verdict', 'why', 'sources'):
                self.assertIn(key, f)
            self.assertTrue(f['sources'])
            for s in f['sources']:
                self.assertTrue(s['url'].startswith('https://'), s)
        for card in plan['not_listed']:
            for key in ('label', 'event', 'teams', 'points', 'timing', 'why', 'hltv_url', 'standings_url', 'sources'):
                self.assertIn(key, card)
            self.assertEqual(len(card['points']), 2)
            self.assertTrue(card['hltv_url'].startswith('https://www.hltv.org/matches/'))
            self.assertIn('ValveSoftware/counter-strike_regional_standings', card['standings_url'])
        self.assertTrue(plan['unverified'])

    def test_the_published_model_numbers_are_reproducible_from_valves_file(self):
        meta = json.loads((vrs.VENDORED / 'meta.json').read_text())
        table = vrs.parse((vrs.VENDORED / meta['file']).read_text())
        by_name = {row['name']: row for row in table['teams']}
        for card in self.notes['day_four_guidance']['not_listed']:
            a, b = card['teams']
            self.assertIn(a, by_name)
            self.assertIn(b, by_name)
            self.assertEqual([by_name[a]['points'], by_name[b]['points']], card['points'],
                             'Card points must equal the official standings file')
            p = vrs.calibrated(vrs.expected(*card['points']))
            self.assertTrue(0 < p < 1)

    def test_the_semi_final_line_cites_the_official_market_api(self):
        cards = self.notes['day_four_guidance']['not_listed']
        sf1 = next(c for c in cards if c['teams'] == ['FURIA', 'Aurora'])
        self.assertIn('gamma-api.polymarket.com/markets/', sf1['market']['url'])
        self.assertIn('5778024', sf1['market']['url'])
        self.assertIn('23:52', sf1['market']['label'])
        self.assertIn('00:10', sf1['market']['label'])
        # The earlier 19:35 read is retained in the block's limitations.
        self.assertIn('19:35', json.dumps(self.notes['day_four_guidance']['unverified']))

    def test_the_build_renders_every_block_with_the_current_day_first(self):
        snapshot = json.loads((ROOT / 'research/harvest-621776e4/snapshot.json').read_text())
        html = build.analysis_page(snapshot)
        # analysis_page gives the current day its own anchor and keeps the earlier
        # day at the stable #guidance anchor.
        self.assertIn('id="day-four-guidance"', html)
        self.assertIn('id="guidance"', html)
        self.assertIn('id="day-four-guidance-read"', html)
        self.assertIn(build.guidance_label(self.notes), html)
        self.assertIn('Semi-final day', html)
        self.assertIn('FURIA vs Aurora', html)
        self.assertLess(html.index('id="day-four-guidance"'), html.index('id="guidance"'))

    def test_the_day_four_block_keeps_the_earlier_evidence_and_drops_superseded_wording(self):
        """One merged block: the verified exchange line survives, the un-finished decider wording does not."""
        plan = self.notes['day_four_guidance']
        text = json.dumps(plan, ensure_ascii=False)
        # Retained from the sessions that wrote the earlier day-4 blocks: the
        # exchange line, the sourced points list and the board-fixture cards.
        self.assertIn('5778024', text)
        self.assertGreaterEqual(len(plan['points']), 7)
        self.assertEqual(3, len(plan['fixtures']))
        # The reconciled state of 17 October: the decider is decided and the
        # conditional "still live" wording that depended on it is gone, while the
        # turnaround observation it carried is still published.
        self.assertEqual('Day-4 picks', plan['nav_label'])
        self.assertIn('BETBOOM 2-1 Legacy', text)
        self.assertIn('BETBOOM 2-1 Legacy',
                      json.dumps(self.notes['day_three_results'], ensure_ascii=False))
        self.assertNotIn('live at 1-1', text)
        self.assertIn('three-map series', text)
        self.assertIn('turn around', plan['summary'])
        # The earlier session's 19:35 market read is retained as evidence, not deleted.
        self.assertIn('19:35', text)
        # One block only - a duplicate JSON key would silently drop one of them.
        self.assertEqual(1, (ROOT / 'data/analysis.json').read_text().count('"day_four_guidance"'))

    def test_executive_summary_points_at_the_current_guidance(self):
        snapshot = json.loads((ROOT / 'research/harvest-621776e4/snapshot.json').read_text())
        html = build.overview(snapshot)
        self.assertIn('analysis.html#day-four-guidance', html)
        self.assertIn(self.notes['day_four_guidance']['nav_label'], html)
        self.assertIn('analysis.html#day-three-results', html)
        # The label comes from the data, so it cannot fall behind the current day.
        self.assertIn(build.guidance_label(self.notes), html)


class AccessLimitationTests(unittest.TestCase):
    """The executive summary must explain why a row has no percentage, from real attempts."""

    def setUp(self):
        self.data = json.loads((ROOT / 'research/harvest-621776e4/snapshot.json').read_text())

    def test_every_source_tried_is_counted_once_per_row(self):
        html = build.access_limitations(self.data)
        self.assertIn('id="access-limitations"', html)
        unpriced = [m for m in self.data['matches'] if m['state'] == 'open' and m['probabilities'] is None]
        self.assertTrue(unpriced)
        for provider in ('Polymarket', 'Pinnacle', 'HLTV', 'Thunderpick', 'GG.BET', 'Valve VRS model'):
            wanted = len({m['id'] for m in unpriced
                          if any((a.get('provider') or '').strip() == provider for a in m['attempts'])})
            self.assertIn('%s</strong></td><td data-label="Rows">%d of %d' % (provider, wanted, len(unpriced)), html)
        # A provider that is never tried must not appear.
        self.assertNotIn('Rivalry', html)

    def test_the_gg_bet_refusal_is_reported_as_a_refusal(self):
        html = build.access_limitations(self.data)
        self.assertIn('Access refused (HTTP 403 Forbidden)', html)
        self.assertIn('No bot protection was bypassed', html)

    def test_no_probability_is_invented_for_a_gap(self):
        html = build.access_limitations(self.data)
        self.assertNotIn('50/50 means', html)
        self.assertIn('never 50/50', html)

    def test_the_hltv_gap_is_documented_from_the_dom_capture_not_blamed_on_a_selector(self):
        """A corrected claim: the selector matches, HLTV simply publishes no numbers."""
        dom = json.loads((ROOT / 'research/harvest-621776e4/hltv-betting-dom.json').read_text())
        self.assertTrue(dom)
        for page in dom:
            self.assertEqual(200, page['http_status'])
            self.assertEqual(1, page['selector_hits']['.match-betting-list tr.provider'])
            self.assertIn('noOdds', page['container_html_excerpt'])
        html = build.access_limitations(self.data)
        self.assertIn('noOdds', html)
        self.assertIn('hltv-betting-dom.json', html)
        self.assertNotIn('selector is stale', html)

    def test_a_priced_snapshot_needs_no_access_panel(self):
        data = json.loads((ROOT / 'research/harvest-621776e4/snapshot.json').read_text())
        for m in data['matches']:
            if m['state'] == 'open':
                m['probabilities'] = [.5, .5]
                m['pick'] = m['teams'][0]
        self.assertEqual(build.access_limitations(data), '')


class DivergentStandingsTests(unittest.TestCase):
    """Two Valve-standings readings disagree on FURIA-Aurora; the conflict is published."""

    def test_the_published_ranks_match_the_harvested_match_page(self):
        page = json.loads((ROOT / 'research/harvest-621776e4/hltv-twc-2399414.json').read_text())
        self.assertEqual(['FURIA', 'Aurora'], page['teams'])
        self.assertEqual({'FURIA': 6, 'Aurora': 5}, {r['team']: r['vrs_rank'] for r in page['ranks']})
        # Valve's own file, which the model reads, says the opposite order.
        meta = json.loads((vrs.VENDORED / 'meta.json').read_text())
        points = {r['name']: r['points'] for r in vrs.parse((vrs.VENDORED / meta['file']).read_text())['teams']}
        self.assertGreater(points['FURIA'], points['Aurora'])

    def test_both_readings_and_the_unverified_forecast_are_on_the_page(self):
        snapshot = json.loads((ROOT / 'research/harvest-621776e4/snapshot.json').read_text())
        html = build.analysis_page(snapshot)
        # The two standings readings still disagree, and the disagreement is published.
        self.assertIn('disagree on the FURIA-Aurora direction', html)
        self.assertIn('VRS #6 FURIA against VRS #5 Aurora', html)
        self.assertIn('hltv-twc-2399414.json', html)
        # The live VRS ranks are now verified from the server-side forecast box.
        self.assertIn('Aurora #5 (1848 pts)', html)
        self.assertIn('FURIA #6 (1826 pts)', html)
        # The previously unverified HLTV forecast figure is withdrawn in public.
        self.assertIn('forecast of FURIA 26.5% / Aurora 73.5%', html)
        self.assertIn('withdrawn from this block', html)
        # The market stays the primary line, not either model.
        self.assertIn('gamma-api.polymarket.com/markets/5778024', html)

    def test_the_executive_summary_still_points_at_the_newest_guidance_block(self):
        snapshot = json.loads((ROOT / 'research/harvest-621776e4/snapshot.json').read_text())
        notes = json.loads((ROOT / 'data/analysis.json').read_text())
        html = build.overview(snapshot)
        self.assertIn('analysis.html#day-four-guidance', html)
        self.assertIn(notes['day_four_guidance']['nav_label'], html)


if __name__ == '__main__':
    unittest.main()
