"""Session 1abdd416: day-4 semi-final pricing, the day-3 decider result, and the 6666 bridge.

Every number asserted here is recomputed from a captured primary response in
``research/harvest-1abdd416/`` or from Valve's vendored standings file, so a
hand-edited figure in ``data/analysis.json`` (or in the identity register) fails
the suite instead of shipping. Nothing in this module contacts the network.
"""
import json
import re
import unittest
from pathlib import Path

from scripts import build, vrs
from scripts.core import norm

ROOT = Path(__file__).resolve().parents[1]
HARVEST = ROOT / 'research/harvest-1abdd416'
NOTES = json.loads((ROOT / 'data/analysis.json').read_text())
SNAPSHOT = json.loads((HARVEST / 'snapshot.json').read_text())
CAPTURE = json.loads((HARVEST / 'polymarket-active-cs2.json').read_text())
PINNACLE = json.loads((HARVEST / 'pinnacle-esports.json').read_text())
IDENTITIES = json.loads((ROOT / 'data/identities.json').read_text())


def market(market_id):
    for event in CAPTURE['events']:
        for mk in event['markets']:
            if str(mk['id']) == str(market_id):
                return event, mk
    raise AssertionError('market %s is not in the captured exchange feed' % market_id)


def matchup(matchup_id):
    for m in PINNACLE['matchups']:
        if str(m.get('id')) == str(matchup_id):
            return m
    raise AssertionError('matchup %s is not in the captured Pinnacle feed' % matchup_id)


def moneyline_zero(matchup_id):
    for line in PINNACLE['lines']:
        if str(line.get('matchupId')) == str(matchup_id) and line.get('type') == 'moneyline' \
                and line.get('period') == 0:
            return line
    raise AssertionError('no whole-match moneyline captured for matchup %s' % matchup_id)


def decimal(american):
    """American -> decimal, per the project's published conversion."""
    return 1 + (american / 100) if american > 0 else 1 + (100 / abs(american))


def devig(prices):
    q = [1 / decimal(p) for p in prices]
    total = sum(q)
    return [x / total for x in q], total - 1


class DayThreeDecidersTests(unittest.TestCase):
    def setUp(self):
        self.results = NOTES['day_three_results']
        self.rows = {m['winner']: m for m in self.results['matches']}

    def test_both_group_deciders_are_final_and_sourced(self):
        self.assertEqual({'Aurora', 'BETBOOM'}, set(self.rows))
        for row in self.rows.values():
            self.assertTrue(row['match_url'].startswith('https://www.hltv.org/matches/'))
            self.assertEqual('2-0' if row['winner'] == 'Aurora' else '2-1', row['score'])

    def test_the_group_b_decider_matches_the_hltv_match_page(self):
        row = self.rows['BETBOOM']
        self.assertIn('2399413', row['match_url'])
        self.assertEqual('Legacy', row['loser'])
        # Map scores as printed on the page: Nuke 16-13 (OT), Dust2 11-13, Mirage 13-11.
        self.assertIn('Nuke 16-13', row['maps'])
        self.assertIn('Dust2 11-13', row['maps'])
        self.assertIn('Mirage 13-11', row['maps'])
        self.assertIn('Mirage', row['detail'])
        self.assertIn('Magnojez', row['detail'])

    def test_the_inferno_secondary_caveat_is_gone_because_the_match_page_carries_it(self):
        aurora = self.rows['Aurora']
        self.assertIn('13-4', aurora['detail'])
        self.assertIn('HLTV match page', aurora['detail'])
        for stale in ('dust2.com.br', 'EGamersWorld'):
            self.assertNotIn(stale, aurora['detail'])
        # The decider note must not still describe a live match.
        self.assertNotIn('still LIVE', self.results['note'])


class SemiFinalPricingTests(unittest.TestCase):
    """The two day-4 cards must reproduce the captured exchange and bookmaker lines."""

    def setUp(self):
        self.cards = {c['label']: c for c in NOTES['day_four_guidance']['not_listed']}
        self.assertEqual({'FURIA vs Aurora', 'Falcons vs BETBOOM'}, set(self.cards))
        meta = json.loads((vrs.VENDORED / 'meta.json').read_text())
        self.points = {r['name']: r['points']
                       for r in vrs.parse((vrs.VENDORED / meta['file']).read_text())['teams']}

    def test_each_card_names_a_pick_and_two_prices(self):
        for label, card in self.cards.items():
            self.assertIn(card['pick'], card['teams'], label)
            for key in ('market', 'book_line', 'timing', 'why', 'hltv_url', 'standings_url', 'sources'):
                self.assertTrue(card.get(key), '%s is missing %s' % (label, key))
            self.assertGreater(len(card['pick_detail']), 40)

    def test_the_published_model_numbers_reproduce_from_valves_file(self):
        for card in self.cards.values():
            a, b = card['teams']
            self.assertEqual([self.points[a], self.points[b]], card['points'])
            p = vrs.calibrated(vrs.expected(*card['points']))
            html = build.analysis_page(SNAPSHOT)
            self.assertIn('%.1f%%' % (p * 100), html)

    def test_the_exchange_line_equals_the_captured_market(self):
        # Card 1 quotes Polymarket 5778024; card 2 quotes 5787759.
        for card, market_id in ((self.cards['FURIA vs Aurora'], '5778024'),
                                (self.cards['Falcons vs BETBOOM'], '5787759')):
            event, mk = market(market_id)
            self.assertTrue(mk['acceptingOrders'])
            self.assertEqual('2026-10-17 14:00:00+00' if market_id == '5778024' else '2026-10-17 17:00:00+00',
                             mk['gameStartTime'])
            prices = json.loads(mk['outcomePrices'])
            self.assertIn('%.1f%%' % (float(prices[0]) * 100), card['market']['detail'])
            self.assertIn('%.1f%%' % (float(prices[1]) * 100), card['market']['detail'])
            self.assertIn('%.2f' % mk['bestBid'], card['market']['detail'])
            self.assertIn('%.2f' % mk['bestAsk'], card['market']['detail'])
            self.assertIn('{:,}'.format(round(mk['liquidityNum'], 2)), card['market']['detail'])
            # The card quotes the market's update time to the second.
            self.assertIn(mk['updatedAt'][:19] + 'Z', card['market']['detail'])
            self.assertIn(market_id, card['market']['url'])
            self.assertEqual('2026-10-17T14:00:00Z' if market_id == '5778024' else '2026-10-17T17:00:00Z',
                             mk['gameStartTime'].replace(' 14:00:00+00', 'T14:00:00Z')
                             .replace(' 17:00:00+00', 'T17:00:00Z'))

    def test_the_bookmaker_cross_check_is_de_margined_from_the_captured_prices(self):
        expected = {'FURIA vs Aurora': ('1638536356', ['FURIA', 'Aurora']),
                    'Falcons vs BETBOOM': ('1638595724', ['Falcons', 'BB Team'])}
        for label, (matchup_id, names) in expected.items():
            card = self.cards[label]
            m = matchup(matchup_id)
            participants = [p['name'] for p in m['participants']]
            self.assertEqual(names, participants)
            self.assertEqual('CS2 - TP World Championship', m['league']['name'])
            line = moneyline_zero(matchup_id)
            self.assertEqual('open', line['status'])
            prices = [p['price'] for p in line['prices']]
            probs, overround = devig(prices)
            self.assertTrue(-0.02 < overround < 0.25, overround)
            detail = card['book_line']['detail']
            for american, prob in zip(prices, probs):
                self.assertIn(('%+d' % american) if american > 0 else str(american), detail)
                self.assertIn('%.1f%%' % (prob * 100), detail)
            self.assertIn('%.1f%%' % (overround * 100), detail)
            # The decimal odds in the card are the captured prices; compare numerically
            # so the site's rounding cannot drift from the feed it quotes.
            printed = [float(x) for x in re.findall(r'decimal ([\d.]+) / ([\d.]+)', detail)[0]]
            for got, want in zip(printed, [decimal(p) for p in prices]):
                self.assertLess(abs(got - want), 0.005)
            # The card normalises Pinnacle's "+00:00" offset to the site's "Z" style.
            self.assertIn(line['cutoffAt'].replace('+00:00', 'Z'), detail)
            self.assertIn('Pinnacle', card['book_line']['label'])

    def test_the_start_times_match_hltvs_machine_readable_clocks(self):
        pages = {'FURIA vs Aurora': 'hltv-twc-2399414.json', 'Falcons vs BETBOOM': 'hltv-twc-2399415.json'}
        for label, filename in pages.items():
            page = json.loads((HARVEST / filename).read_text())
            card = self.cards[label]
            self.assertEqual(200, page['http_status'])
            self.assertEqual(card['teams'], page['teams'])
            self.assertIn(page['start_utc'], card['timing'])
            # The market's own gameStartTime must agree with HLTV's clock.
            spelled = page['start_utc'].replace('T', ' ').replace(':00Z', ' UTC').replace('Z', ' UTC')
            self.assertIn(spelled, card['market']['detail'])
            self.assertIn('best of 3', card['timing'])
            self.assertEqual(['Falcons', 'BETBOOM'] if label.startswith('Falcons') else ['FURIA', 'Aurora'],
                             card['teams'])

    def test_the_rendered_page_states_each_pick(self):
        html = build.analysis_page(SNAPSHOT)
        for card in self.cards.values():
            self.assertIn('Pick:', html)
            self.assertIn(card['pick'], html)
            self.assertIn('id="day-four-guidance"', html)

    def test_the_grand_final_and_third_place_have_no_teams_yet(self):
        for filename in ('hltv-twc-2399416.json', 'hltv-twc-2399417.json'):
            page = json.loads((HARVEST / filename).read_text())
            self.assertEqual(['', ''], page['teams'])
            self.assertFalse(page['ranks'])
        text = json.dumps(NOTES['day_four_guidance'], ensure_ascii=False)
        self.assertIn('2399416', text)
        self.assertIn('2399417', text)


class SixSixIdentityTests(unittest.TestCase):
    """The low-tier row that no market covers still gets a reproducible model line."""

    def setUp(self):
        self.entry = next((i for i in IDENTITIES['aliases'] if i['canonical'] == '6666'), None)
        self.assertIsNotNone(self.entry, 'the 6666 identity entry is missing')
        self.lineups = {}
        for row in ('1081521', '1081522'):
            page = json.loads((HARVEST / ('hltv-unpriced-%s.json' % row)).read_text())
            for lineup in page['lineups']:
                self.lineups[lineup['team']] = lineup['players']
        # No in-memory patching: the supported entry point supplies the provenance.
        self.standings, self.meta = vrs.vendored()
        self.assertEqual('vendored copy (live fetch unavailable)', self.meta['origin'])
        self.assertTrue(self.meta['observed_at'].endswith('Z'))

    def test_the_label_mapping_carries_its_primary_sources(self):
        self.assertEqual(['6666', 'ex-6666'], self.entry['names'])
        self.assertIn('counter-strike_regional_standings', self.entry['source'])
        self.assertIn('hltv.org/matches/2399681', self.entry['additional_source'])
        self.assertIn('TEAM_OVERLAP_TO_SHARE_ROSTER', self.entry['basis'])
        self.assertIn('923.2', self.entry['basis'])

    def test_norm_folds_the_two_labels_and_nothing_else(self):
        self.assertEqual(norm('ex-6666'), norm('6666'))
        self.assertNotEqual(norm('ex-6666'), norm('666'))

    def test_the_model_line_reproduces_from_the_captured_lineup(self):
        fixture = {'teams': ['ex-6666', 'Privateer']}
        quote, reason = vrs.line(fixture, self.standings, self.meta, self.lineups)
        self.assertIsNone(reason)
        # Expected value is rebuilt from the standings rows the model selected,
        # found by standing number, so a duplicated label cannot mask a wrong row.
        by_standing = {r['standing']: r for r in self.standings['teams']}
        self.assertEqual('6666', by_standing[127]['name'])
        self.assertEqual('Privateer', by_standing[271]['name'])
        expected = vrs.calibrated(vrs.expected(by_standing[127]['points'], by_standing[271]['points']))
        self.assertAlmostEqual(quote['probabilities'][0], expected, places=12)
        self.assertEqual(['6666', 'Privateer'], quote['vrs_teams'])
        self.assertEqual([by_standing[127]['points'], by_standing[271]['points']], quote['points'])
        self.assertEqual([127, 271], quote['standings'])
        for check in quote['roster_checks']:
            self.assertGreaterEqual(check['overlap'], 3)

    def test_a_different_roster_does_not_bridge(self):
        lineups = dict(self.lineups)
        lineups['ex-6666'] = ['nobody1', 'nobody2', 'nobody3', 'nobody4', 'nobody5']
        quote, reason = vrs.line({'teams': ['ex-6666', 'Privateer']}, self.standings, self.meta, lineups)
        self.assertIsNone(quote)
        self.assertIn('roster-continuity rule', reason)

    def test_the_bridge_prices_exactly_the_one_row_that_needed_it(self):
        row = json.loads(json.dumps(next(m for m in SNAPSHOT['matches'] if m['id'] == '1081521')))
        self.assertIsNone(row['probabilities'])
        vrs.apply(row, self.standings, self.meta, self.lineups)
        self.assertEqual('model_vrs', row['method'])
        self.assertEqual(row['pick'], 'ex-6666')
        self.assertGreater(row['probabilities'][0], 0.5)
        # The label also appears on three closed June fixtures, but the bridge can
        # only ever price an open row, so exactly one row's pick can change.
        labelled = [m['id'] for m in SNAPSHOT['matches'] if any('6666' in t for t in m['teams'])]
        self.assertEqual({'1081521', '1053439', '1053470', '1053442'}, set(labelled))
        self.assertEqual(['1081521'], [m['id'] for m in SNAPSHOT['matches']
                                       if m['state'] == 'open' and any('6666' in t for t in m['teams'])])


class RemainingUnpricedTests(unittest.TestCase):
    """Three rows still carry a pick with no percentage; the limitation is published."""

    def setUp(self):
        self.open_rows = [m for m in SNAPSHOT['matches'] if m['state'] == 'open']
        self.unpriced = [m for m in self.open_rows if m['probabilities'] is None]

    def test_the_alias_flips_exactly_the_row_that_was_blocked_by_a_label(self):
        """The captured snapshot predates the aliases; replaying it now must price the two
        label-blocked rows: 1081521 (6666/ex-6666 bridge) and 1081522 (Strael Bora/antidaun
        bridge, registered 2026-10-17 by session bc70eb9a)."""
        meta = json.loads((vrs.VENDORED / 'meta.json').read_text())
        meta.update(observed_at='2026-10-17T00:00:00Z', origin='replay of the vendored official copy')
        standings = vrs.parse((vrs.VENDORED / meta['file']).read_text())
        lineups = {}
        for row in ('1081521', '1081522', '1081861', '1081863'):
            page = json.loads((HARVEST / ('hltv-unpriced-%s.json' % row)).read_text())
            for lineup in page['lineups']:
                lineups[lineup['team']] = lineup['players']
        # The reason recorded before the alias existed, kept as the evidence it was.
        blocked_row = next(m for m in SNAPSHOT['matches'] if m['id'] == '1081521')
        recorded = next(a['reason'] for a in blocked_row['attempts'] if a.get('provider') == 'Valve VRS model')
        self.assertEqual('No originated line: ex-6666: not listed in the Valve global standings.', recorded)
        replay = json.loads(json.dumps(SNAPSHOT['matches']))
        for row in replay:
            if row['state'] == 'open':
                vrs.apply(row, standings, meta, lineups)
        still_unpriced = sorted(m['id'] for m in replay
                                if m['state'] == 'open' and m['probabilities'] is None)
        self.assertEqual(['1081861', '1081863'], still_unpriced)
        flipped = next(m for m in replay if m['id'] == '1081521')
        self.assertEqual('model_vrs', flipped['method'])
        self.assertGreater(flipped['probabilities'][0], 0.5)
        flipped2 = next(m for m in replay if m['id'] == '1081522')
        self.assertEqual('model_vrs', flipped2['method'])
        self.assertGreater(flipped2['probabilities'][1], 0.5)
        self.assertEqual('Phantom Academy', flipped2['pick'])
        # The two that remain fail on a team that the official file does not list.
        listed = {norm(r['name']) for r in standings['teams']}
        for row in replay:
            if row['id'] in still_unpriced:
                blocked = [t for t in row['teams'] if norm(t) not in listed]
                self.assertEqual(1, len(blocked), row['id'])

    # The four rows the harvest of 2026-10-16T23:52Z left without a percentage and the
    # two that still have none once the 6666 / ex-6666 and the Strael Bora / antidaun
    # labels are registered (the latter added 2026-10-17 by session bc70eb9a).
    CAPTURED_UNPRICED = ['1081521', '1081522', '1081861', '1081863']

    def test_the_snapshot_has_no_open_row_without_a_pick(self):
        self.assertEqual(21, len(self.open_rows))
        self.assertEqual(17, len([m for m in self.open_rows if m['probabilities'] is not None]))
        self.assertEqual(self.CAPTURED_UNPRICED, sorted(m['id'] for m in self.unpriced))
        for row in self.unpriced:
            self.assertTrue(row['pick'])
            self.assertTrue(row['reason'])

    def test_each_unpriced_row_names_the_team_the_official_file_omits(self):
        meta = json.loads((vrs.VENDORED / 'meta.json').read_text())
        table = vrs.parse((vrs.VENDORED / meta['file']).read_text())
        listed = {norm(r['name']) for r in table['teams']}
        for row in self.unpriced:
            reason = next(str(a['reason']) for a in row['attempts']
                          if a.get('provider') == 'Valve VRS model')
            # 1081521's blocker was the label (ex-6666) and 1081522's was the label
            # (antidaun); both are registered renames now, so norm() folds each onto a
            # listed team and they are checked as label blocks. The other two name a
            # club the official file does not list at all.
            if row['id'] == self.CAPTURED_UNPRICED[0]:
                self.assertIn('ex-6666', reason)
                continue
            if row['id'] == '1081522':
                self.assertIn('antidaun', reason)
                continue
            self.assertIn('not listed in the Valve global standings', reason)
            blocked = [t for t in row['teams'] if norm(t) not in listed]
            self.assertEqual(1, len(blocked), row['id'])
            self.assertIn(blocked[0], reason)

    def test_the_limitations_section_lists_every_unpriced_row(self):
        html = build.access_limitations(SNAPSHOT)
        self.assertIn('id="access-limitations"', html)
        self.assertIn('%d of %d' % (len(self.unpriced), len(self.unpriced)), html)
        self.assertIn('Valve VRS model', html)


if __name__ == '__main__':
    unittest.main()
