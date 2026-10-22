"""Session 8c8e3c5f: the Aurora YB alias, the one-sided Valve standings
research tier, and the phone-first Picks at a glance in the executive summary.

The alias rests on primary specialist sources read 2026-10-19 (HLTV match
2399777 and Liquipedia's Aurora Young Blud team page, which lists fixture
1082157 abbreviated "Aurora YB"); see research/session-8c8e3c5f/REPORT.md.
The VRS tier must publish a pick and no numbers, and must stay silent when
the "absent" side is actually present-but-unresolvable.
"""
import copy
import importlib.util
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import vrs
from scripts.build import glance, overview
from scripts.core import iso, norm, normalize_fixtures, orientation
from scripts.validate import validate_data

ROOT = Path(__file__).resolve().parents[1]
TABLE = vrs.parse((ROOT / 'data/vrs/standings_global_2026_10_05.md').read_text())

NOW = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)
START = NOW + timedelta(hours=30)


def load_auditor():
    spec = importlib.util.spec_from_file_location('audit_snapshot', ROOT / 'verification-c6/audit_snapshot.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def meta():
    doc = json.loads((ROOT / 'data/vrs/meta.json').read_text())
    return dict(doc, origin='test vendored copy', observed_at=iso(NOW))


def fixture(team_a, team_b):
    raw = {'id': 'T8157', 'sport_alias': 'cs2', 'participants0_name': team_a, 'participants1_name': team_b,
           'participants0_id': 'a', 'participants1_id': 'b', 'status': 'scheduled',
           'scheduled_start_time': iso(START), 'lock_time': iso(START - timedelta(minutes=6)),
           'competition_name': 'Stake Ranked Episode 6: Closed Qualifier', 'tier': 'b'}
    row = normalize_fixtures([raw], {}, NOW)[0]
    row.update(probabilities=None, fair_odds=None, pick=None, method=None, evidence=[], flags=[], attempts=[], reason=None)
    return raw, row


def snapshot(row, raw):
    return {'schema_version': 2, 'generated_at': iso(NOW), 'last_attempt_at': iso(NOW),
            'fixtures_observed_at': iso(NOW), 'coverage': 'verified', 'matches': [row],
            'fixture_evidence': [raw], 'issues': [], 'source_checks': []}


class AuroraAliasTests(unittest.TestCase):
    def test_three_labels_one_team(self):
        keys = {norm('Aurora YB'), norm('Aurora Young Blud'), norm('Aurora Young Blood')}
        self.assertEqual(len(keys), 1)

    def test_never_maps_to_the_main_aurora_team(self):
        self.assertNotEqual(norm('Aurora'), norm('Aurora YB'))
        self.assertNotEqual(norm('Aurora'), norm('Aurora Young Blood'))

    def test_hltv_and_polymarket_labels_now_orient_exactly(self):
        _, row = fixture('Sangal', 'Aurora YB')
        self.assertEqual(orientation(row, ['Sangal', 'Aurora Young Blud'], iso(START)), [0, 1])
        self.assertEqual(orientation(row, ['Aurora Young Blood', 'Sangal'], iso(START)), [1, 0])
        # Exact start is still required: one hour off does not match.
        self.assertIsNone(orientation(row, ['Sangal', 'Aurora Young Blud'], iso(START + timedelta(hours=1))))

    def test_valve_label_resolves_through_the_alias(self):
        entry, note = vrs.identify('Aurora YB', TABLE, None)
        self.assertIsNotNone(entry, note)
        self.assertEqual((entry['name'], entry['standing']), ('Aurora Young Blud', 326))


class VrsSingleTierTests(unittest.TestCase):
    def test_fires_with_pick_only_and_no_numbers(self):
        raw, row = fixture('Sangal', 'Team Nowhere 8143')
        vrs.research_single(row, TABLE, meta())
        self.assertEqual((row['pick'], row['method']), ('Sangal', 'research_vrs_single'))
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['fair_odds'])
        self.assertEqual(row['evidence'], [])
        self.assertIn('not a market probability', row['reason'])
        data = snapshot(row, raw)
        validate_data(data)
        _, errors = load_auditor().inspect(data)
        self.assertEqual(errors, [])

    def test_silent_when_both_teams_listed(self):
        _, row = fixture('Sangal', 'Aurora')
        vrs.research_single(row, TABLE, meta())
        self.assertIsNone(row['pick'])
        self.assertEqual(row['attempts'][-1]['status'], 'unresolved')

    def test_silent_when_neither_team_listed(self):
        _, row = fixture('Team Nowhere 8143', 'Ghost Squad 5521')
        vrs.research_single(row, TABLE, meta())
        self.assertIsNone(row['pick'])

    def test_present_but_stale_roster_is_not_absent(self):
        # Aurora Young Blud is #326 in the 2026-10-05 file, but the current
        # HLTV lineup shares only one player with that listed roster, so the
        # label is unresolvable -- not absent -- and no pick may be made.
        _, row = fixture('Sangal', 'Aurora YB')
        lineups = {'Aurora Young Blud': ['Re1GN', 'meetyoxanaji', 'fluffy', 'Sa1nTy', 'ms2180']}
        vrs.research_single(row, TABLE, meta(), lineups)
        self.assertIsNone(row['pick'])
        loser = next(r for r in row['vrs_research']['resolved_vrs'] if r['team'] == 'Aurora YB')
        self.assertEqual(loser['status'], 'unresolved_label')

    def test_hltv_displayed_vrs_rank_blocks_the_absence_claim(self):
        _, row = fixture('Sangal', 'Team Nowhere 8143')
        row['hltv_context'] = {'ranks': [{'team': 'Team Nowhere 8143', 'hltv_rank': None,
                                          'vrs_rank_on_hltv': 210, 'vrs_source': 'https://www.hltv.org/valve-ranking/teams?teamId=1'}]}
        vrs.research_single(row, TABLE, meta())
        self.assertIsNone(row['pick'])

    def test_tampered_evidence_is_rejected_by_both_audits(self):
        raw, row = fixture('Sangal', 'Team Nowhere 8143')
        vrs.research_single(row, TABLE, meta())
        row['pick'] = 'Team Nowhere 8143'
        data = snapshot(row, raw)
        with self.assertRaises(AssertionError):
            validate_data(data)
        _, errors = load_auditor().inspect(data)
        self.assertTrue(errors)


class GlanceTests(unittest.TestCase):
    def test_every_open_match_appears_once_with_pick_states(self):
        priced = {'id': 'G1', 'teams': ['Alpha', 'Beta'], 'state': 'open', 'start': iso(START),
                  'lock': iso(START - timedelta(minutes=6)), 'expires_at': iso(START - timedelta(minutes=6)),
                  'probabilities': [0.7, 0.3], 'pick': 'Alpha', 'method': 'exchange'}
        research = dict(priced, id='G2', probabilities=None, pick='Beta', method='research_vrs_single')
        missing = dict(priced, id='G3', probabilities=None, pick=None, method=None)
        data = {'last_attempt_at': iso(NOW)}
        soup = BeautifulSoup(glance(data, [missing, research, priced]), 'html.parser')
        rows = soup.select('.glance-row')
        self.assertEqual(len(rows), 3)
        text = soup.get_text(' ', strip=True)
        self.assertIn('Alpha 70.0%', text)
        self.assertIn('Research pick: Beta', text)
        self.assertIn('No pick yet', text)
        hrefs = {a['href'] for a in soup.select('a[href]')}
        self.assertIn('evidence.html#match-G1', hrefs)
        self.assertIn('#unresolved-summary', hrefs)
        self.assertIn('picks.html', hrefs)
        # The glance must not duplicate the validator's one-table-row rule.
        self.assertEqual(soup.select('tr[data-match]'), [])

    def test_executive_summary_links_and_limitations(self):
        snapshot_doc = json.loads((ROOT / 'data/latest.json').read_text())
        soup = BeautifulSoup(overview(copy.deepcopy(snapshot_doc)), 'html.parser')
        self.assertIsNotNone(soup.select_one('#picks-at-a-glance'))
        limits = soup.select_one('#pick-limitations')
        self.assertIsNotNone(limits)
        text = limits.get_text(' ', strip=True)
        for phrase in ('No book lists the match', 'Names differ between sites', 'fan votes are never used', 'model needs both teams'):
            self.assertIn(phrase, text)
        hero_links = {a['href'] for a in soup.select('.hero a[href]')}
        self.assertIn('#picks-at-a-glance', hero_links)
        self.assertIn('picks.html', hero_links)


if __name__ == '__main__':
    unittest.main()
