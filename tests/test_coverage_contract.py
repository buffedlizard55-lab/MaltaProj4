import copy
import unittest

from scripts.coverage_contract import inspect

NOW = '2026-10-22T01:00:00Z'


def snapshot():
    return {'fixtures_observed_at': NOW, 'generated_at': NOW, 'coverage': 'verified', 'matches': [{
        'id': '1', 'teams': ['Alpha', 'Beta'], 'state': 'open',
        'start': '2026-10-22T05:00:00Z', 'lock': '2026-10-22T04:54:00Z',
        'source_url': 'https://play.hotspawn.com/cs2-pickems',
        'feed_url': 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures',
        'pick': 'Alpha', 'probabilities': [.6, .4], 'fair_odds': [1/.6, 1/.4],
        'method': 'exchange', 'expires_at': '2026-10-22T04:54:00Z',
        'evidence': [{'url': 'https://polymarket.com/event/example', 'observed_at': NOW}],
        'attempts': [], 'reason': None}]}


class ContractTests(unittest.TestCase):
    def audit(self, mutate=None, at=NOW):
        data = snapshot()
        if mutate:
            mutate(data['matches'][0])
        return inspect(data, at)

    def test_market(self):
        result = self.audit()
        self.assertEqual(result['problems'], [])
        self.assertEqual(result['counts']['market'], 1)
        self.assertEqual(result['counts']['actionable'], 1)

    def test_model_is_not_market(self):
        result = self.audit(lambda m: m.update(method='model_vrs'))
        self.assertEqual(result['counts']['model'], 1)
        self.assertEqual(result['counts']['market'], 0)

    def test_hltv_valve_mirror_remains_model_not_market(self):
        result = self.audit(lambda m: m.update(method='model_vrs_mirror'))
        self.assertEqual(result['problems'], [])
        self.assertEqual(result['counts']['model'], 1)
        self.assertEqual(result['counts']['market'], 0)

    def research(self, m):
        m.update(method='research_rank_single', probabilities=None, fair_odds=None, evidence=[],
                 reason='One published ranking only; no verified price or percentage.',
                 hltv_context={'source': 'https://www.hltv.org/matches/1/example', 'observed_at': NOW},
                 attempts=[{'url': 'https://www.hltv.org/matches', 'reason': 'No numeric line.'}])

    def test_research_is_not_priced_or_unresolved(self):
        result = self.audit(self.research)
        self.assertEqual(result['problems'], [])
        self.assertEqual(result['counts']['research_only'], 1)
        self.assertEqual(result['counts']['market'], 0)

    def test_unresolved_is_valid_when_linked_and_explained(self):
        def mutate(m):
            self.research(m)
            m.update(pick=None, method=None)
        result = self.audit(mutate)
        self.assertEqual(result['problems'], [])
        self.assertEqual(result['counts']['unresolved'], 1)
        self.assertEqual(result['counts']['actionable'], 0)

    def test_no_silent_unresolved(self):
        result = self.audit(lambda m: m.update(probabilities=None, pick=None, method=None))
        self.assertEqual(len(result['problems']), 2)

    def test_rank_cannot_become_numeric(self):
        result = self.audit(lambda m: m.update(method='research_rank'))
        self.assertTrue(result['problems'])

    def test_pick_must_be_fixture_team(self):
        self.assertTrue(self.audit(lambda m: m.update(pick='Gamma'))['problems'])

    def test_pick_must_match_favorite(self):
        self.assertTrue(self.audit(lambda m: m.update(pick='Beta'))['problems'])

    def test_missing_or_hotspawn_price_source_rejected(self):
        for source in (None, 'https://play.hotspawn.com/lobby', 'http://polymarket.com/event/1',
                       'https://user@polymarket.com/event/1'):
            with self.subTest(source=source):
                self.assertTrue(self.audit(lambda m: m['evidence'][0].update(url=source))['problems'])

    def test_normalized_finite_probabilities(self):
        for pair in ([.6, .5], [float('nan'), .4], [True, False], [1, 0], [.5], '0.6,0.4'):
            with self.subTest(pair=pair):
                self.assertTrue(self.audit(lambda m: m.update(probabilities=pair))['problems'])

    def test_no_probability_from_no_evidence(self):
        self.assertTrue(self.audit(lambda m: m.update(evidence=[]))['problems'])

    def test_equal_line_is_not_a_directional_pick(self):
        result = self.audit(lambda m: m.update(probabilities=[.5, .5], pick=None,
                                               reason='Equal sourced line; no directional edge.'))
        self.assertEqual(result['problems'], [])
        self.assertTrue(self.audit(lambda m: m.update(probabilities=[.5, .5]))['problems'])

    def test_exact_expiry_withholds_recommendation(self):
        result = self.audit(at='2026-10-22T04:54:00Z')
        self.assertEqual(result['counts']['not_open'], 1)
        self.assertIsNone(result['rows'][0]['pick'])
        result = self.audit(lambda m: m.update(expires_at=NOW))
        self.assertEqual(result['counts']['expired'], 1)
        self.assertEqual(result['counts']['actionable'], 0)

    def test_snapshot_eight_hour_boundary(self):
        data = snapshot()
        data['fixtures_observed_at'] = '2026-10-21T17:00:00Z'
        result = inspect(data, NOW)
        self.assertFalse(result['inventory_fresh'])
        self.assertEqual(result['counts']['expired'], 1)

    def test_future_timestamp_not_fresh(self):
        data = snapshot()
        data['fixtures_observed_at'] = '2026-10-23T01:00:00Z'
        self.assertFalse(inspect(data, NOW)['inventory_fresh'])

    def test_conflicting_fixture_cannot_have_pick(self):
        self.assertTrue(self.audit(lambda m: m.update(resolution_blocked=True))['problems'])

    def test_no_research_odds(self):
        def mutate(m):
            self.research(m)
            m['fair_odds'] = [1.5, 3]
        self.assertTrue(self.audit(mutate)['problems'])

    def test_rejected_attempt_is_not_research_evidence(self):
        def mutate(m):
            self.research(m)
            del m['hltv_context']
        self.assertTrue(self.audit(mutate)['problems'])

    def test_old_quote_cannot_be_renewed_by_new_snapshot(self):
        result = self.audit(lambda m: m['evidence'][0].update(observed_at='2026-10-21T17:00:00Z'))
        self.assertEqual(result['counts']['expired'], 1)
        self.assertIsNone(result['rows'][0]['pick'])

    def test_update_timestamp_can_expire_before_observation(self):
        result = self.audit(lambda m: m['evidence'][0].update(updated_at='2026-10-21T17:00:00Z'))
        self.assertEqual(result['counts']['expired'], 1)

    def test_research_context_expires_even_if_snapshot_is_fresh(self):
        def mutate(m):
            self.research(m)
            m['hltv_context']['observed_at'] = '2026-10-21T17:00:00Z'
        self.assertEqual(self.audit(mutate)['counts']['expired'], 1)

    def test_research_needs_dated_external_context(self):
        def mutate(m):
            self.research(m)
            del m['hltv_context']['observed_at']
        self.assertTrue(self.audit(mutate)['problems'])

    def test_future_quote_is_not_actionable(self):
        result = self.audit(lambda m: m['evidence'][0].update(observed_at='2026-10-23T01:00:00Z'))
        self.assertTrue(result['problems'])
        self.assertEqual(result['counts']['actionable'], 0)

    def test_official_match_permalink_is_a_valid_fixture_source(self):
        result = self.audit(lambda m: m.update(source_url='https://www.hotspawn.com/matches/alpha-beta-1'))
        self.assertEqual(result['problems'], [])

    def test_duplicate_ids(self):
        data = snapshot()
        data['matches'].append(copy.deepcopy(data['matches'][0]))
        self.assertTrue(inspect(data, NOW)['problems'])

    def test_audit_does_not_mutate_input(self):
        data = snapshot()
        before = copy.deepcopy(data)
        inspect(data, '2026-10-23T01:00:00Z')
        self.assertEqual(data, before)

    def test_missing_array_is_not_empty_inventory(self):
        with self.assertRaises(ValueError):
            inspect({}, NOW)

    def test_malformed_open_times(self):
        self.assertTrue(self.audit(lambda m: m.update(lock='2026-10-22T04:00:00'))['problems'])


if __name__ == '__main__':
    unittest.main()
