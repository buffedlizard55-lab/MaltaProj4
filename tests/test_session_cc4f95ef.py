"""Regression for the 2026-10-25 publish-gate alias defect and phone geometry.

Official receipts:
  * GitHub Actions run 40193317196 (main publisher) failed in scripts.validate
    with "Model roster has no HLTV source on this row".
  * Runner captures 40197480741 and 40197553353 preserved the exact fresh row
    and the failing browser measurement.
  * HLTV match 2399918 names Tropa do KinGui; Hotspawn fixture 1086697 names
    Projeto do KinGui. data/identities.json records the verified alias with
    HLTV/Polymarket/Valve source links.

PR #316 landed the shared ``same_club`` identity-register bridge and PR #332
landed the current short-phone CSS compaction while this session was
verifying. This integration adopts both upstream implementations; these tests
replay the exact retained runner row, confirm the ledger/source boundary, and
check stylesheet parity. No roster, price, pick or freshness gate is relaxed.
"""
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import validate
from scripts.core import dt

ROOT = Path(__file__).resolve().parents[1]
ROW_FILE = ROOT / 'research' / 'session-cc4f95ef' / 'evidence' / 'fixture-1086697.json'


class VerifiedAliasLineupSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.row = json.loads(ROW_FILE.read_text())

    def test_the_official_hltv_alias_lineup_replays(self):
        row = copy.deepcopy(self.row)
        self.assertEqual(row['id'], '1086697')
        self.assertEqual(row['teams'], ['Projeto do KinGui', 'Yawara'])
        self.assertTrue(row['hltv_context']['source'].startswith(
            'https://www.hltv.org/matches/2399918/'))
        self.assertEqual(row['hltv_context']['team_map']['Tropa do KinGui'],
                         'Projeto do KinGui')
        self.assertTrue(validate.lineup_source_ok(
            row, 'Projeto do KinGui',
            ['drg', 'ALLE', 'ckzao', 'xureba', 'lash']))
        validate.validate_model_row(
            row, row['evidence'][0], dt(row['snapshot_generated_at']))

    def test_a_direct_team_label_still_matches_without_alias_context(self):
        row = {'id': '1', 'teams': ['Alpha', 'Beta'],
               'hltv_context': {'lineups': [
                   {'team': 'Alpha', 'players': ['a', 'b']}]}}
        self.assertTrue(validate.lineup_source_ok(row, 'Alpha', ['a', 'b']))

    def test_the_adopted_same_club_bridge_uses_only_sourced_ledger_aliases(self):
        row = copy.deepcopy(self.row)
        self.assertTrue(validate.same_club(
            row, 'Projeto do KinGui', 'Tropa do KinGui'))
        self.assertTrue(validate.same_club(row, 'Yawara', 'Yawara'))
        self.assertFalse(validate.same_club(
            row, 'Projeto do KinGui', 'Invented Label'))
        self.assertFalse(validate.same_club(
            row, 'Yawara', 'Tropa do KinGui'))
        # An empty identity register must fall back to exact matching only.
        with patch.object(validate, 'IDENTITIES', []):
            self.assertFalse(validate.same_club(
                row, 'Projeto do KinGui', 'Tropa do KinGui'))
            self.assertTrue(validate.same_club(row, 'Yawara', 'Yawara'))

    def test_an_ambiguous_fixture_pair_cannot_use_the_alias_bridge(self):
        row = copy.deepcopy(self.row)
        row['teams'] = ['Projeto do KinGui', 'Tropa do KinGui']
        self.assertFalse(validate.same_club(
            row, 'Projeto do KinGui', 'Tropa do KinGui'))

    def test_an_unverified_alias_label_is_refused_even_with_a_team_map(self):
        row = copy.deepcopy(self.row)
        row['hltv_context']['teams'] = ['Invented Label', 'Yawara']
        row['hltv_context']['team_map'] = {
            'Invented Label': 'Projeto do KinGui', 'Yawara': 'Yawara'}
        row['hltv_context']['lineups'][0]['team'] = 'Invented Label'
        self.assertFalse(validate.lineup_source_ok(
            row, 'Projeto do KinGui',
            ['drg', 'ALLE', 'ckzao', 'xureba', 'lash']))
        with self.assertRaises(AssertionError):
            validate.validate_model_row(
                row, row['evidence'][0], dt(row['snapshot_generated_at']))

    def test_an_altered_roster_is_refused(self):
        row = copy.deepcopy(self.row)
        row['hltv_context']['lineups'][0]['players'][0] = 'invented-player'
        self.assertFalse(validate.lineup_source_ok(
            row, 'Projeto do KinGui',
            ['drg', 'ALLE', 'ckzao', 'xureba', 'lash']))
        with self.assertRaises(AssertionError):
            validate.validate_model_row(
                row, row['evidence'][0], dt(row['snapshot_generated_at']))

    def test_the_row_keeps_its_official_source_links(self):
        row = self.row
        q = row['evidence'][0]
        self.assertTrue(q['url'].startswith(
            'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/'))
        self.assertTrue(q['formula_source'].startswith(
            'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/'))
        self.assertTrue(row['hltv_context']['source'].startswith(
            'https://www.hltv.org/matches/'))
        self.assertTrue(row['source_url'].startswith('https://play.hotspawn.com/'))


class ShortPhoneBoardGeometryCss(unittest.TestCase):
    def test_adopted_short_phone_stylesheets_are_identical_and_balanced(self):
        served = (ROOT / 'assets' / 'style.css').read_text()
        canonical = (ROOT / 'site' / 'assets' / 'style.css').read_text()
        self.assertEqual(served, canonical)
        # PR #332's measured repair for the y=519 / y=507 overlap found by
        # runner 40197553353 and independently reproduced by this session.
        self.assertIn('Session 8e4ff8d2 (2026-10-25)', served)
        self.assertIn('body[data-page=picks] tbody tr{padding:13px;gap:11px 14px}', served)
        self.assertEqual(validate.stylesheet_problems(served), [])


if __name__ == '__main__':
    unittest.main()
