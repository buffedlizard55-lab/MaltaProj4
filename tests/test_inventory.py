"""Hypothetical inventory failures, never used as production match data."""
import copy
import json
import unittest
from scripts.core import dt, normalize_fixtures, iso, FIXTURES, HOTSPAWN
from scripts.inventory import discover, LOBBY

NOW = dt('2026-10-15T08:00:00Z')
ROW = {'id': 'TEST_ONLY_1', 'sport_alias': 'cs2', 'participants0_name': 'Alpha',
       'participants1_name': 'Beta', 'scheduled_start_time': '2026-10-16T12:00:00Z',
       'lock_time': '2026-10-16T11:54:00Z', 'status': 'scheduled'}


class Sources:
    def __init__(self, responses):
        self.responses = responses
        self.log = []

    def get(self, name, url, as_json=True):
        response = self.responses[url]
        if isinstance(response, Exception):
            raise response
        if as_json:
            payload = response
        else:
            payload = '<script id="ng-state">' + json.dumps({'test': {'u': FIXTURES.split('?')[0], 'b': response}}) + '</script>'
        return payload, {'observed_at': iso(NOW), 'url': url}


def previous():
    return {'matches': normalize_fixtures([ROW], {}, NOW), 'fixture_evidence': [ROW],
            'fixtures_observed_at': iso(NOW), 'generated_at': iso(NOW), 'issues': []}


class InventoryTests(unittest.TestCase):
    def sources(self, rows=None):
        return {FIXTURES: [ROW], HOTSPAWN: [ROW], LOBBY: [ROW]} if rows is None else rows

    def test_three_official_views_required_for_parity(self):
        result = discover(Sources(self.sources()), NOW)
        self.assertEqual(result['coverage'], 'verified')
        self.assertEqual(result['counts'], {'api': 1, 'page': 1, 'lobby': 1, 'retained': 1})

    def test_new_lobby_only_match_is_not_dropped(self):
        responses = self.sources()
        responses[LOBBY] = [ROW, ROW | {'id': 'TEST_ONLY_2'}]
        result = discover(Sources(responses), NOW)
        self.assertEqual(len(result['matches']), 2)
        self.assertEqual(result['coverage'], 'partial')

    def test_same_id_conflicting_opponent_blocks_recommendation(self):
        responses = self.sources()
        responses[HOTSPAWN] = [ROW | {'participants1_name': 'Gamma'}]
        result = discover(Sources(responses), NOW)
        self.assertTrue(result['matches'][0]['resolution_blocked'])
        self.assertTrue(result['conflicts'])
        self.assertEqual(result['matches'][0]['teams'], ['Alpha', 'Beta'])

    def test_missing_still_open_prior_row_survives_partial_fetch(self):
        responses = {FIXTURES: [ROW | {'id': 'TEST_ONLY_2'}], HOTSPAWN: ValueError('test unavailable'), LOBBY: ValueError('test unavailable')}
        result = discover(Sources(responses), NOW, previous())
        retained = next(m for m in result['matches'] if m['id'] == ROW['id'])
        self.assertTrue(retained['resolution_blocked'])
        self.assertEqual(result['counts']['retained'], 2)

    def test_complete_agreement_can_remove_previous_row(self):
        responses = {key: [ROW | {'id': 'TEST_ONLY_2'}] for key in self.sources()}
        result = discover(Sources(responses), NOW, previous())
        self.assertEqual([m['id'] for m in result['matches']], ['TEST_ONLY_2'])
        self.assertEqual(result['changes']['removed_ids'], [ROW['id']])

    def test_wrong_game_and_no_fallback_preserves_previous(self):
        responses = {FIXTURES: [ROW | {'sport_alias': 'lol'}], HOTSPAWN: ValueError('test unavailable'), LOBBY: ValueError('test unavailable')}
        before = previous()
        result = discover(Sources(responses), NOW, before)['retained']
        self.assertEqual(result['matches'], before['matches'])
        self.assertEqual(result['generated_at'], before['generated_at'])
        self.assertNotIn('coverage', before, 'Do not mutate the caller’s last-good object')

    def test_duplicates_are_not_silently_deduplicated(self):
        responses = {key: [ROW, ROW] for key in self.sources()}
        self.assertIn('retained', discover(Sources(responses), NOW, previous()))

    def test_empty_requires_all_three_sources_and_no_populated_previous(self):
        responses = {key: [] for key in self.sources()}
        self.assertEqual(discover(Sources(responses), NOW)['matches'], [])
        self.assertIn('retained', discover(Sources(responses), NOW, previous()))
        responses[LOBBY] = ValueError('test unavailable')
        with self.assertRaises(RuntimeError):
            discover(Sources(responses), NOW)


if __name__ == '__main__':
    unittest.main()
