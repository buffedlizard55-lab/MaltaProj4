"""Full-coverage tiers: wide exchange quote, rank research pick, verified aliases.

These tests pin the user-requested behaviour that every fixture should end with a
pick where a researched source permits it, without ever inventing a probability.
"""
import json
import unittest
from pathlib import Path
from scripts.core import (
    dt, iso, norm, orientation, normalize_fixtures, polymarket_candidates,
    quote_polymarket, research_rank_pick, resolve,
)

NOW = dt('2026-10-15T10:20:00Z')
FIX = {'id': 'test', 'sport_alias': 'cs2', 'participants0_name': 'Alpha', 'participants1_name': 'Beta',
       'status': 'scheduled', 'scheduled_start_time': '2026-10-15T12:00:00Z', 'lock_time': '2026-10-15T11:54:00Z'}


def fixture(**over):
    return normalize_fixtures([FIX | over], {}, NOW)[0]


def exchange(**over):
    market = {'id': '123', 'question': 'Counter-Strike: Alpha vs Beta (BO3)', 'sportsMarketType': 'moneyline',
              'active': True, 'closed': False, 'acceptingOrders': True, 'outcomes': '["Alpha","Beta"]',
              'outcomePrices': '["0.75","0.25"]', 'gameStartTime': '2026-10-15T12:00:00Z', 'updatedAt': iso(NOW),
              'bestBid': .55, 'bestAsk': .95, 'liquidity': '2966.0927'}
    market.update(over)
    return {'slug': 'cs2-test', 'sport': {'sport': 'cs2'}, 'markets': [market]}


class WideTierTests(unittest.TestCase):
    def test_wide_quote_rejected_without_relax(self):
        f = fixture()
        resolve(f, polymarket_candidates([exchange()], iso(NOW)), 'Polymarket', NOW)
        self.assertIsNone(f['probabilities'])
        self.assertIn('spread exceeds 25 points', f['attempts'][0]['reason'])

    def test_wide_quote_accepted_only_in_relaxed_tier(self):
        f = fixture()
        candidates = polymarket_candidates([exchange()], iso(NOW))
        resolve(f, [c for c in candidates], 'Polymarket', NOW, relax=True)
        self.assertIsNotNone(f['probabilities'])
        self.assertEqual(f['method'], 'exchange_wide')
        self.assertEqual(f['pick'], 'Alpha')
        quote = f['evidence'][0]
        self.assertEqual(quote['tier'], 'wide_exchange')
        self.assertAlmostEqual(quote['spread'], .4, places=9)
        self.assertAlmostEqual(quote['liquidity'], 2966.0927, places=4)
        self.assertIn('Low confidence', quote['warning'])
        self.assertIn('spread exceeds 25 points', quote['strict_rejection'])
        self.assertTrue(any('Low confidence' in flag for flag in f['flags']))

    def test_wide_tier_never_accepts_unfunded_market(self):
        f = fixture()
        candidates = polymarket_candidates([exchange(liquidity='99')], iso(NOW))
        resolve(f, candidates, 'Polymarket', NOW, relax=True)
        self.assertIsNone(f['probabilities'])

    def test_wide_tier_has_a_ceiling(self):
        f = fixture()
        candidates = polymarket_candidates([exchange(bestBid=.05, bestAsk=.95)], iso(NOW))
        resolve(f, candidates, 'Polymarket', NOW, relax=True)
        self.assertIsNone(f['probabilities'])
        self.assertIn('60-point ceiling', f['attempts'][0]['reason'])

    def test_exactly_25_point_spread_is_still_strict(self):
        f = fixture()
        candidates = polymarket_candidates([exchange(bestBid=.57, bestAsk=.82)], iso(NOW))
        resolve(f, candidates, 'Polymarket', NOW)
        self.assertEqual(f['method'], 'exchange')
        quote = f['evidence'][0]
        self.assertEqual(quote['tier'], 'exchange')
        self.assertIn('Wide exchange spread', quote['warning'])

    def test_relax_never_overwrites_a_strict_primary(self):
        f = fixture()
        strict = polymarket_candidates([exchange(bestBid=.59, bestAsk=.61)], iso(NOW))
        resolve(f, strict, 'Polymarket', NOW)
        before = json.dumps(f, sort_keys=True)
        resolve(f, polymarket_candidates([exchange()], iso(NOW)), 'Polymarket', NOW, relax=True)
        self.assertEqual(before, json.dumps(f, sort_keys=True))


class ResearchRankTests(unittest.TestCase):
    def context(self, ranks):
        return {'teams': ['Alpha', 'Beta'], 'start': '2026-10-15T12:00:00Z', 'ranks': ranks,
                'source': 'https://www.hltv.org/matches/1/alpha-vs-beta-test', 'observed_at': iso(NOW)}

    def test_better_rank_becomes_a_labelled_research_pick(self):
        f = fixture()
        f['hltv_context'] = self.context([
            {'team': 'Alpha', 'hltv_rank': 31, 'source': 'https://www.hltv.org/ranking/teams/1'},
            {'team': 'Beta', 'hltv_rank': 6, 'source': 'https://www.hltv.org/ranking/teams/2'}])
        research_rank_pick(f)
        self.assertEqual(f['pick'], 'Beta')
        self.assertEqual(f['method'], 'research_rank')
        self.assertIsNone(f['probabilities'])
        self.assertIsNone(f['fair_odds'])
        self.assertIn('not a market probability', f['reason'])
        self.assertTrue(any('no probability published' in flag for flag in f['flags']))

    def test_reversed_orientation_uses_the_fixture_order(self):
        f = fixture()
        f['hltv_context'] = self.context([
            {'team': 'Beta', 'hltv_rank': 3, 'source': 'https://www.hltv.org/ranking/teams/2'},
            {'team': 'Alpha', 'hltv_rank': 40, 'source': 'https://www.hltv.org/ranking/teams/1'}])
        research_rank_pick(f)
        self.assertEqual(f['pick'], 'Beta')

    def test_exactly_one_ranked_team_is_a_labelled_one_sided_research_pick(self):
        """Documented tier: one team world-ranked, the other absent from the ranking page."""
        for ranks, expected in (
                ([{'team': 'Alpha', 'hltv_rank': 119, 'source': 'https://www.hltv.org/ranking/teams/1'},
                  {'team': 'Beta', 'hltv_rank': None, 'source': None}], 'Alpha'),
                ([{'team': 'Alpha', 'hltv_rank': None, 'source': None},
                  {'team': 'Beta', 'hltv_rank': 2, 'source': 'https://www.hltv.org/ranking/teams/2'}], 'Beta')):
            f = fixture()
            f['hltv_context'] = self.context(ranks)
            research_rank_pick(f)
            self.assertEqual(f['pick'], expected)
            self.assertEqual(f['method'], 'research_rank_single')
            self.assertIsNone(f['probabilities'])
            self.assertIsNone(f['fair_odds'])
            self.assertIn('not a market probability', f['reason'])
            self.assertTrue(any('no probability published' in flag for flag in f['flags']))
            resolved = f['hltv_context']['resolved_ranks']
            self.assertEqual([r['team'] for r in resolved], ['Alpha', 'Beta'])
            self.assertEqual(sorted(r['hltv_rank'] for r in resolved if r['hltv_rank']), [2 if expected == 'Beta' else 119])
            self.assertEqual(f['attempts'][-1]['status'], 'resolved')

    def test_unusable_ranking_evidence_still_invents_nothing(self):
        for ranks in ([{'team': 'Alpha', 'hltv_rank': 7, 'source': 'https://www.hltv.org/ranking/teams/1'},
                       {'team': 'Beta', 'hltv_rank': 7, 'source': 'https://www.hltv.org/ranking/teams/2'}],
                      [{'team': 'Alpha', 'hltv_rank': 4, 'source': None},
                       {'team': 'Beta', 'hltv_rank': None, 'source': None}],
                      [{'team': 'Alpha', 'hltv_rank': None, 'source': None},
                       {'team': 'Beta', 'hltv_rank': None, 'source': None}],
                      []):
            f = fixture()
            f['hltv_context'] = self.context(ranks)
            research_rank_pick(f)
            self.assertIsNone(f['pick'], ranks)
            self.assertEqual(f['attempts'][-1]['status'], 'unresolved')

    def test_alias_labelled_rank_row_needs_a_registered_primary_source(self):
        """An HLTV label that differs from the fixture label must map through the register."""
        f = fixture()
        f['teams'] = ['WROTBERRY', 'Nexus']
        f['hltv_context'] = self.context([
            {'team': 'WBT', 'hltv_rank': 109, 'source': 'https://www.hltv.org/ranking/teams/13683'},
            {'team': 'Nexus', 'hltv_rank': 139, 'source': 'https://www.hltv.org/ranking/teams/7187'}])
        research_rank_pick(f)
        self.assertEqual(f['pick'], 'WROTBERRY')
        resolved = {r['team']: r for r in f['hltv_context']['resolved_ranks']}
        self.assertEqual(resolved['WROTBERRY']['hltv_name'], 'WBT')
        self.assertTrue(resolved['WROTBERRY']['alias_source'].startswith('https://'))
        self.assertIsNone(resolved['Nexus']['alias_source'])
        # A team whose label produced no ranking row at all is genuinely absent
        # from the ranking page; the one-sided tier may then use the other team,
        # and the row records that absence explicitly instead of guessing a name.
        f = fixture()
        f['teams'] = ['Unknown Tag', 'Nexus']
        f['hltv_context'] = self.context([
            {'team': 'Nexus', 'hltv_rank': 139, 'source': 'https://www.hltv.org/ranking/teams/2'}])
        research_rank_pick(f)
        self.assertEqual(f['pick'], 'Nexus')
        self.assertEqual(f['method'], 'research_rank_single')
        resolved = {r['team']: r for r in f['hltv_context']['resolved_ranks']}
        self.assertEqual(resolved['Unknown Tag']['status'], 'no_rank_row')
        self.assertIsNone(resolved['Unknown Tag']['alias_source'])
        # Ambiguity is never resolved by a guess: two matching rows for one label.
        f = fixture()
        f['hltv_context'] = self.context([
            {'team': 'Alpha', 'hltv_rank': 3, 'source': 'https://www.hltv.org/ranking/teams/1'},
            {'team': 'Alpha', 'hltv_rank': 9, 'source': 'https://www.hltv.org/ranking/teams/3'},
            {'team': 'Beta', 'hltv_rank': 139, 'source': 'https://www.hltv.org/ranking/teams/2'}])
        research_rank_pick(f)
        self.assertIsNone(f['pick'])
        self.assertEqual(f['attempts'][-1]['status'], 'unresolved')

    def test_market_evidence_is_never_replaced_by_a_rank_pick(self):
        f = fixture()
        resolve(f, polymarket_candidates([exchange(bestBid=.59, bestAsk=.61)], iso(NOW)), 'Polymarket', NOW)
        f['hltv_context'] = self.context([
            {'team': 'Alpha', 'hltv_rank': 99, 'source': 'https://www.hltv.org/ranking/teams/1'},
            {'team': 'Beta', 'hltv_rank': 1, 'source': 'https://www.hltv.org/ranking/teams/2'}])
        research_rank_pick(f)
        self.assertEqual(f['pick'], 'Alpha')
        self.assertEqual(f['method'], 'exchange')

    def test_no_hltv_context_means_no_pick(self):
        f = fixture()
        research_rank_pick(f)
        self.assertIsNone(f['pick'])
        self.assertIsNone(f['probabilities'])


class VerifiedAliasTests(unittest.TestCase):
    def test_registered_aliases_only(self):
        self.assertEqual(norm('WROTBERRY'), norm('WBT'))
        self.assertEqual(norm('Privateer Gaming'), norm('Privateer'))
        self.assertNotEqual(norm('WBT Academy'), norm('WBT'))
        self.assertNotEqual(norm('Privateer Academy'), norm('Privateer'))

    def test_every_alias_entry_has_primary_sources(self):
        data = json.loads(Path('data/identities.json').read_text())
        for item in data['aliases']:
            self.assertTrue(item['source'].startswith('https://'), item['canonical'])
            if item.get('additional_source'):
                self.assertTrue(item['additional_source'].startswith('https://'), item['canonical'])
            basis = item['basis'].lower()
            self.assertIn('utc start', basis)
            self.assertTrue('exact opponent' in basis or 'exact opposing team' in basis, item['canonical'])
            self.assertGreaterEqual(len(item['names']), 2, item['canonical'])

    def test_hotspawn_name_resolves_against_the_exchange_label(self):
        f = normalize_fixtures([FIX | {'participants0_name': 'WROTBERRY', 'participants1_name': 'ENCE',
                                       'scheduled_start_time': '2026-10-15T12:00:00Z',
                                       'lock_time': '2026-10-15T11:54:00Z'}], {}, NOW)[0]
        market = {'id': '9', 'question': 'Counter-Strike: WBT vs ENCE (BO1)', 'sportsMarketType': 'moneyline',
                  'active': True, 'closed': False, 'acceptingOrders': True, 'outcomes': '["WBT","ENCE"]',
                  'outcomePrices': '["0.61","0.39"]', 'gameStartTime': '2026-10-15T12:00:00Z', 'updatedAt': iso(NOW),
                  'bestBid': .6, 'bestAsk': .62, 'liquidity': '11195.9987'}
        event = {'slug': 'cs2-wbt-ence-2026-10-15', 'sport': {'sport': 'cs2'}, 'markets': [market]}
        resolve(f, polymarket_candidates([event], iso(NOW)), 'Polymarket', NOW)
        self.assertEqual(f['pick'], 'WROTBERRY')
        self.assertEqual(f['probabilities'], [.61, .39])
        self.assertTrue(f['evidence'][0]['identity_sources'])

    def test_alias_never_bypasses_the_start_time_check(self):
        f = normalize_fixtures([FIX | {'participants0_name': 'WROTBERRY', 'participants1_name': 'ENCE'}], {}, NOW)[0]
        self.assertIsNone(orientation(f, ['WBT', 'ENCE'], '2026-10-15T13:00:00Z'))
        self.assertEqual(orientation(f, ['ENCE', 'WBT'], '2026-10-15T12:00:00Z'), [1, 0])


if __name__ == '__main__':
    unittest.main()
