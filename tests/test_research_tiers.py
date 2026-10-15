"""Regression tests for the 2026-10-15 refresh failure and the research tiers.

The 21:22 UTC scheduled refresh failed its independent audit on fixture
1081529 (Nexus vs WROTBERRY): HLTV labels the team WBT, the collector matched
it through the verified alias register, but the auditor compared raw labels.
"""
import copy
import importlib.util
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.core import iso, research_rank_pick, normalize_fixtures, dt
from scripts.hltv import context
from scripts.quarantine import quarantine
from scripts.validate import validate_data

ROOT = Path(__file__).resolve().parents[1]


def load_auditor():
    spec = importlib.util.spec_from_file_location('audit_snapshot', ROOT / 'verification-c6/audit_snapshot.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NOW = datetime.now(timezone.utc).replace(microsecond=0)
START = NOW + timedelta(hours=5)


def snapshot(team_a, team_b, ranks):
    raw = {'id': 'R1', 'sport_alias': 'cs2', 'participants0_name': team_a, 'participants1_name': team_b,
           'participants0_id': 'a', 'participants1_id': 'b', 'status': 'scheduled',
           'scheduled_start_time': iso(START), 'lock_time': iso(START - timedelta(minutes=6)),
           'competition_name': 'DraculaN Season 7', 'tier': 'b'}
    row = normalize_fixtures([raw], {}, NOW)[0]
    row.update(probabilities=None, fair_odds=None, pick=None, method=None, evidence=[], flags=[], attempts=[], reason=None)
    row['hltv_context'] = {'teams': [r['team'] for r in ranks], 'start': iso(START), 'ranks': ranks, 'lineups': [],
                           'source': 'https://www.hltv.org/matches/2399593/wbt-vs-nexus-digital-crusade-draculan-season-7',
                           'observed_at': iso(NOW), 'numeric_quote_rows': 0, 'limitation': 'context only'}
    research_rank_pick(row)
    return {'schema_version': 2, 'generated_at': iso(NOW), 'last_attempt_at': iso(NOW), 'fixtures_observed_at': iso(NOW),
            'coverage': 'verified', 'matches': [row], 'fixture_evidence': [raw], 'issues': [], 'source_checks': []}


def rank(team, value, unranked=False, vrs=None):
    return {'team': team, 'hltv_rank': value, 'source': ('https://www.hltv.org/ranking/teams/2026/october/12/1' if value else None),
            'hltv_unranked': unranked, 'vrs_rank_on_hltv': vrs, 'vrs_source': None}


class AliasResearchRegression(unittest.TestCase):
    def test_wbt_alias_row_passes_both_audits(self):
        data = snapshot('Nexus', 'WROTBERRY', [rank('WBT', 109), rank('Nexus', 139)])
        row = data['matches'][0]
        self.assertEqual(row['pick'], 'WROTBERRY')
        self.assertEqual([i['canonical'] for i in row['identity_sources']], ['WBT'])
        _, errors = load_auditor().inspect(data)
        self.assertEqual(errors, [])
        validate_data(data)

    def test_auditor_still_rejects_an_unsourced_alias(self):
        data = snapshot('Nexus', 'WROTBERRY', [rank('WBT', 109), rank('Nexus', 139)])
        row = data['matches'][0]
        row['identity_sources'] = []
        _, errors = load_auditor().inspect(data)
        self.assertTrue(errors)
        data = snapshot('Nexus', 'WROTBERRY', [rank('WBT', 109), rank('Nexus', 139)])
        data['matches'][0]['identity_sources'][0]['source'] = ''
        _, errors = load_auditor().inspect(data)
        self.assertTrue(errors)


    def test_identity_records_are_copies_not_the_register(self):
        from scripts.core import IDENTITIES
        data = snapshot('Nexus', 'WROTBERRY', [rank('WBT', 109), rank('Nexus', 139)])
        data['matches'][0]['identity_sources'][0]['source'] = ''
        self.assertTrue(next(i for i in IDENTITIES if i['canonical'] == 'WBT')['source'])


class OneSidedRankingTests(unittest.TestCase):
    def test_explicit_unranked_badge_gives_a_research_pick(self):
        data = snapshot('Procyon', 'LOS NINOS', [rank('Procyon', 119, vrs=149), rank('LOS NINOS', None, unranked=True)])
        row = data['matches'][0]
        self.assertEqual(row['pick'], 'Procyon')
        self.assertIsNone(row['probabilities'])
        self.assertIn('Unranked', row['reason'])
        _, errors = load_auditor().inspect(data)
        self.assertEqual(errors, [])
        validate_data(data)

    def test_missing_badge_or_contradicting_vrs_gives_no_pick(self):
        for ranks in ([rank('Procyon', 119), rank('LOS NINOS', None, unranked=False)],
                      [rank('Procyon', 119, vrs=149), rank('LOS NINOS', None, unranked=True, vrs=60)],
                      [rank('Procyon', 119, vrs=None), rank('LOS NINOS', None, unranked=True, vrs=60)],
                      [rank('Procyon', 119)]):
            data = snapshot('Procyon', 'LOS NINOS', ranks)
            self.assertIsNone(data['matches'][0]['pick'], ranks)

    def test_auditor_rejects_a_forged_one_sided_pick(self):
        data = snapshot('Procyon', 'LOS NINOS', [rank('Procyon', 119, vrs=149), rank('LOS NINOS', None, unranked=True)])
        auditor = load_auditor()
        for mutate in (lambda m: m['hltv_context']['ranks'][1].update(hltv_unranked=False),
                       lambda m: m['hltv_context']['ranks'][1].update(vrs_rank_on_hltv=10),
                       lambda m: m.update(pick='LOS NINOS')):
            forged = copy.deepcopy(data)
            mutate(forged['matches'][0])
            _, errors = auditor.inspect(forged)
            self.assertTrue(errors)


class QuarantineTests(unittest.TestCase):
    def test_failing_row_is_withheld_and_the_audit_then_passes(self):
        data = snapshot('Nexus', 'WROTBERRY', [rank('WBT', 109), rank('Nexus', 139)])
        data['matches'][0]['identity_sources'] = []  # reproduce the 21:22 UTC failure
        failing, structural = quarantine(data)
        self.assertEqual(list(failing), ['R1'])
        self.assertEqual(structural, [])
        row = data['matches'][0]
        self.assertIsNone(row['pick'])
        self.assertIsNone(row['method'])
        self.assertIn('Withheld', row['reason'])
        self.assertEqual(row['withheld']['values']['pick'], 'WROTBERRY')
        self.assertTrue(any(i['code'] == 'audit_quarantine' for i in data['issues']))
        _, errors = load_auditor().inspect(data)
        self.assertEqual(errors, [])

    def test_snapshot_level_failures_are_not_quarantined(self):
        data = snapshot('Nexus', 'WROTBERRY', [rank('WBT', 109), rank('Nexus', 139)])
        data['matches'].append(copy.deepcopy(data['matches'][0]))
        _, structural = quarantine(data)
        self.assertTrue(structural)


class RealCaptureParseTests(unittest.TestCase):
    def test_lineups_and_unranked_badge_from_the_retained_hltv_page(self):
        html = (ROOT / 'research/probe/hltv-banda.txt').read_text()
        row = normalize_fixtures([{'id': 'X', 'sport_alias': 'cs2', 'participants0_name': 'Banda Chuya',
            'participants1_name': '6666', 'status': 'scheduled', 'scheduled_start_time': '2026-10-14T11:00:00Z',
            'lock_time': '2026-10-14T10:54:00Z'}], {}, dt('2026-10-14T09:00:00Z'))[0]
        parsed = context(html, row)
        by_team = {r['team']: r for r in parsed['ranks']}
        self.assertTrue(by_team['Banda Chuya']['hltv_unranked'])
        self.assertIsNone(by_team['Banda Chuya']['hltv_rank'])
        self.assertEqual(by_team['Banda Chuya']['vrs_rank_on_hltv'], 187)
        self.assertFalse(by_team['6666']['hltv_unranked'])
        self.assertEqual((by_team['6666']['hltv_rank'], by_team['6666']['vrs_rank_on_hltv']), (80, 119))
        lineups = {x['team']: x['players'] for x in parsed['lineups']}
        self.assertEqual(lineups['Banda Chuya'], ['tomiko', 'maaryy', 'AdrieN', 'Showk', 'ezox'])
        self.assertEqual(lineups['6666'], ['skcH', 'amster', 'rendysky', 'kL1o', 'stefienson'])


if __name__ == '__main__':
    unittest.main()
