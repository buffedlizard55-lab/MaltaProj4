"""Session 58354934 — the 2026-10-25 publication freeze and its two fixes.

Measured failure: publication runs 40170923727 (06:41Z) and 40193317196
(12:29Z) both died at *Build and independently verify every row, calculation
and internal link* with

    File "scripts/validate.py", line 122, in validate_model_row
        assert lineup_source_ok(m, team, check.get('lineup') or []),
               'Model roster has no HLTV source on this row'
    AssertionError: Model roster has no HLTV source on this row

on fixture 1086697. Hotspawn names the club ``Projeto do KinGui``; the HLTV
match page the row resolves to (matches/2399918) names it ``Tropa do KinGui``.
Both labels are entries in ``data/identities.json`` under one canonical club
with a primary source, and ``validate_model_row`` already accepts that alias for
the VRS label. Only the roster-source lookup compared raw labels, so a roster
that *is* sourced on the row was called unsourced and the whole board was
refused -- every pick on the live site was withheld for 11 h 40 m.

Two things are pinned here:

1. ``scripts.validate.same_club`` / ``lineup_source_ok`` accept a verified
   alias (never a fuzzy match, never a different club, never different players).
2. ``scripts.quarantine.validation_violations`` withholds only the row the
   repository data validator cannot reproduce, and only when that provably
   repairs the snapshot, so a single such row can no longer freeze the board.
"""
import copy
import importlib.util
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts import core, quarantine
from scripts.core import iso, normalize_fixtures
from scripts.validate import lineup_source_ok, same_club, validate_data

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now(timezone.utc).replace(microsecond=0)
START = NOW + timedelta(hours=6)


def load_auditor():
    spec = importlib.util.spec_from_file_location('audit_snapshot_58354934',
                                                  ROOT / 'verification-c6/audit_snapshot.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def team_pages(lineup_alpha=None):
    return {'status': 'available', 'observed_at': iso(NOW), 'teams': [
        {'team': 'Alpha', 'label': 'Alpha', 'world_rank': 12,
         'world_rank_status': 'ranked',
         'world_rank_source': 'https://www.hltv.org/ranking/teams',
         'observed_at': iso(NOW), 'url': 'https://www.hltv.org/team/111/alpha',
         'lineup': lineup_alpha or []}]}


def one_sided(match, lineup=('a', 'b', 'c', 'd', 'x'), page_lineup=('p', 'q', 'r', 's', 't')):
    """A real ``research_vrs_single`` row: one club listed by Valve, one absent.

    The stored roster window (``lineup``) overlaps the roster Valve publishes by
    four players, so the identity rule is satisfied arithmetically. Whether that
    window is *sourced* is what only ``validate_data`` checks: when the club's own
    HLTV team page is on the row, the same five must appear there.
    """
    match.update(pick='Alpha', method='research_vrs_single',
                 reason='One-sided Valve standings listing; not a market probability.',
                 evidence=[], attempts=[], flags=['Research pick, no probability published.'],
                 hltv_team_pages=team_pages(list(page_lineup)),
                 vrs_research={
                     'source': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md',
                     'standings_as_of': NOW.date().isoformat(), 'observed_at': iso(NOW),
                     'teams_count': 100, 'resolved_vrs': [
                         {'team': 'Alpha', 'status': 'listed', 'standing': 1, 'points': 1500,
                          'vrs_name': 'Alpha', 'roster': ['a', 'b', 'c', 'd', 'e'],
                          'roster_overlap': 4, 'label_count': 1, 'lineup': list(lineup)},
                         {'team': 'Bravo', 'status': 'absent', 'label_count': 0}]})
    return match


def open_snapshot(rows=1):
    raw_rows = []
    for index in range(rows):
        raw_rows.append({'id': str(9000 + index), 'sport_alias': 'cs2',
                         'participants0_name': 'Alpha', 'participants1_name': 'Bravo',
                         'participants0_id': 'a', 'participants1_id': 'b',
                         'status': 'scheduled',
                         'scheduled_start_time': iso(START),
                         'lock_time': iso(START - timedelta(minutes=6)),
                         'competition_name': 'CCT South America 2026 Series #7',
                         'tier': 'c'})
    matches = normalize_fixtures(raw_rows, {}, NOW)
    for match in matches:
        match.update(pick=None, probabilities=None, fair_odds=None, method=None,
                     reason=None, evidence=[], attempts=[], flags=[])
        one_sided(match, page_lineup=('a', 'b', 'c', 'd', 'x'))
    return {'schema_version': 2, 'generated_at': iso(NOW), 'last_attempt_at': iso(NOW),
            'fixtures_observed_at': iso(NOW), 'coverage': 'verified',
            'matches': matches, 'fixture_evidence': raw_rows, 'issues': [],
            'source_checks': [], 'fixture_conflicts': []}


class VerifiedAliasRosterTests(unittest.TestCase):
    def test_registered_alias_is_the_same_club(self):
        # The exact pair from the freeze: one canonical club, two published labels.
        self.assertTrue(same_club('Tropa do KinGui', 'Projeto do KinGui'))
        self.assertTrue(same_club('Projeto do KinGui', 'Tropa do KinGui'))
        self.assertTrue(same_club('ex-Keyd Stars', 'Projeto do KinGui'))

    def test_a_different_club_is_never_accepted(self):
        self.assertFalse(same_club('Yawara', 'Projeto do KinGui'))
        self.assertFalse(same_club('', 'Projeto do KinGui'))
        self.assertFalse(same_club(None, 'Projeto do KinGui'))

    def test_alias_mapped_hltv_lineup_sources_the_roster(self):
        lineup = ['drg', 'ALLE', 'ckzao', 'xureba', 'lash']
        row = {'id': '1086697', 'teams': ['Projeto do KinGui', 'Yawara'],
               'hltv_context': {'lineups': [{'team': 'Tropa do KinGui', 'players': lineup},
                                            {'team': 'Yawara', 'players': ['brn$', 'j0w', 'deemO', 'tele', 'mlhzin']}]}}
        self.assertTrue(lineup_source_ok(row, 'Projeto do KinGui', lineup))
        self.assertTrue(lineup_source_ok(row, 'Yawara', ['brn$', 'j0w', 'deemO', 'tele', 'mlhzin']))

    def test_alias_never_waives_the_player_check(self):
        lineup = ['drg', 'ALLE', 'ckzao', 'xureba', 'lash']
        row = {'id': '1086697', 'teams': ['Projeto do KinGui', 'Yawara'],
               'hltv_context': {'lineups': [{'team': 'Tropa do KinGui', 'players': lineup}]}}
        self.assertFalse(lineup_source_ok(row, 'Projeto do KinGui', lineup + ['invented']))
        self.assertFalse(lineup_source_ok(row, 'Projeto do KinGui', []))

    def test_team_page_lineup_matches_through_the_alias_register(self):
        lineup = ['drg', 'ALLE', 'ckzao', 'xureba', 'lash']
        row = {'id': '1086697', 'teams': ['Projeto do KinGui', 'Yawara'],
               'hltv_team_pages': {'teams': [
                   {'team': 'Tropa do KinGui', 'lineup': lineup,
                    'url': 'https://www.hltv.org/team/12674/tropa-do-kingui'}]}}
        self.assertTrue(lineup_source_ok(row, 'Projeto do KinGui', lineup))


class ValidatorBackstopTests(unittest.TestCase):
    """One unreproducible row must not withhold every other pick."""

    def with_unreproducible_lineup(self, snapshot):
        """Row 9000 fails ``validate_data`` only - the auditor cannot see this.

        The stored overlap is arithmetically correct, but the club's HLTV team
        page on the same row lists a different five. Only the repository
        validator checks that linkage, so the independent auditor passes the row
        while publication is refused: the exact shape of the 2026-10-25 freeze.
        """
        row = snapshot['matches'][0]
        row['hltv_team_pages']['teams'][0]['lineup'] = ['p', 'q', 'r', 's', 't']
        return snapshot

    def test_validator_failure_is_isolated_to_the_row(self):
        snapshot = self.with_unreproducible_lineup(open_snapshot())
        with self.assertRaises(AssertionError):
            validate_data(snapshot)
        _, auditor_errors = load_auditor().inspect(snapshot)
        self.assertEqual(auditor_errors, [], 'the auditor accepts this row; only validate rejects it')
        isolated = quarantine.validation_violations(snapshot)
        self.assertEqual(list(isolated), ['9000'])
        self.assertIn('repository data validator', isolated['9000'][0])

    def test_quarantine_keeps_the_other_rows_and_names_the_reason(self):
        data = self.with_unreproducible_lineup(open_snapshot(rows=2))
        failing, structural = quarantine.quarantine(data)
        self.assertEqual(structural, [])
        self.assertIn('9000', failing)
        self.assertIsNone(data['matches'][0]['pick'])
        self.assertIn('Withheld', data['matches'][0]['reason'])
        self.assertEqual(data['matches'][0]['withheld']['values']['method'], 'research_vrs_single')
        self.assertTrue(data['matches'][1]['pick'], 'the healthy row keeps its pick')
        self.assertTrue(any(i['code'] == 'validation_quarantine' for i in data['issues']))
        validate_data(data)  # the repaired snapshot now passes the publication gate

    def test_snapshot_level_problem_withholds_nothing(self):
        """A failure that is not confined to a row must still fail loudly."""
        data = self.with_unreproducible_lineup(open_snapshot())
        data['matches'].append(copy.deepcopy(data['matches'][0]))  # duplicate id, snapshot-level
        isolated = quarantine.validation_violations(data)
        self.assertEqual(isolated, {}, 'nothing may be blanked when withholding cannot repair the snapshot')

    def test_healthy_snapshot_is_untouched(self):
        data = open_snapshot()
        self.assertEqual(quarantine.validation_violations(data), {})
        before = copy.deepcopy(data)
        failing, structural = quarantine.quarantine(data)
        self.assertEqual((failing, structural), ({}, []))
        self.assertEqual([m['pick'] for m in data['matches']], [m['pick'] for m in before['matches']])


if __name__ == '__main__':
    unittest.main()
