"""End-to-end refresh path: wide tier resolves, research tier labels, audits agree.

The scheduled workflow runs this exact sequence against live sources. These tests
drive it with synthetic upstream responses so the CI path is covered offline:
inventory parity -> exchange resolution (strict then wide) -> HLTV research ->
independent row audit -> full data validation.
"""
import importlib.util
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from scripts.core import FIXTURES, HOTSPAWN, GAMMA, PIN, iso, normalize_fixtures
from scripts.inventory import LOBBY
from scripts.refresh import run
from scripts.validate import validate_data

ROOT = Path(__file__).resolve().parents[1]


def load_auditor():
    spec = importlib.util.spec_from_file_location('audit_snapshot', ROOT / 'verification-c6/audit_snapshot.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NOW = datetime.now(timezone.utc).replace(microsecond=0)
WIDE_START = NOW + timedelta(hours=2)
RESEARCH_START = NOW + timedelta(hours=3)
SINGLE_START = NOW + timedelta(hours=4)
ALIAS_START = NOW + timedelta(hours=5)


def row(fixture_id, team_a, team_b, start):
    return {'id': fixture_id, 'sport_alias': 'cs2', 'participants0_name': team_a, 'participants1_name': team_b,
            'participants0_id': fixture_id + '0', 'participants1_id': fixture_id + '1', 'status': 'scheduled',
            'scheduled_start_time': iso(start), 'lock_time': iso(start - timedelta(minutes=6)),
            'competition_name': 'Synthetic Test Cup', 'tier': 'c'}


ROWS = [row('TIER_1', 'Alpha', 'Beta', WIDE_START), row('TIER_2', 'Gamma', 'Delta', RESEARCH_START),
        row('TIER_3', 'Epsilon', 'Zeta', SINGLE_START), row('TIER_4', 'WROTBERRY', 'Nexus', ALIAS_START)]

# Only one team carries a published world ranking in TIER_3's HLTV page, and
# TIER_4's HLTV page labels the first team WBT (a registered identity mapping).
RANKS = {
    'TIER_1': [('team1-gradient', 'Alpha', 44), ('team2-gradient', 'Beta', 12)],
    'TIER_2': [('team1-gradient', 'Gamma', 31), ('team2-gradient', 'Delta', 6)],
    'TIER_3': [('team1-gradient', 'Epsilon', 250), ('team2-gradient', 'Zeta', None)],
    'TIER_4': [('team1-gradient', 'WBT', 109), ('team2-gradient', 'Nexus', 139)],
}


def ng_state(rows):
    return ('<html><body><script id="ng-state">'
            + json.dumps({'test': {'u': FIXTURES.split('?')[0], 'b': rows}})
            + '</script></body></html>')


DETAIL_URLS = {fixture['id']: f'https://www.hltv.org/matches/902{index}/{fixture["id"].lower()}'
               for index, fixture in enumerate(ROWS, start=1)}


def hltv_list():
    links = []
    for fixture in ROWS:
        teams = ''.join(f'<span class="match-teamname">{t}</span>' for t in (fixture['participants0_name'], fixture['participants1_name']))
        unix = int(datetime.fromisoformat(fixture['scheduled_start_time'].replace('Z', '+00:00')).timestamp() * 1000)
        links.append(f'<div class="match"><a class="match-teams" href="{DETAIL_URLS[fixture["id"]].replace("https://www.hltv.org", "")}">' + teams
                     + f'</a><div class="match-time" data-unix="{unix}"></div></div>')
    return '<html><body>' + ''.join(links) + '</body></html>'


def hltv_detail(fixture, entries):
    """Mirror the markup shape observed in a retained HLTV capture.

    The ranking block below reproduces the real structure documented in
    tests/test_pipeline_tiers.py::test_ranking_parse_matches_the_retained_capture:
    <div class="teamRanking"><a class="ranking-badge hltv-ranking"><span>HLTV: </span>#N</a>...
    A team without a world ranking has no numeric badge (the real page simply
    omits it), which is exactly the one-sided evidence case.
    """
    unix = int(datetime.fromisoformat(fixture['scheduled_start_time'].replace('Z', '+00:00')).timestamp() * 1000)
    blocks = ''
    for side, team, rank in entries:
        badge = (f'<a href="/ranking/teams/2026/october/12/{rank}" class="ranking-badge hltv-ranking">'
                 f'<span>HLTV: </span>#{rank}</a>'
                 f'<a href="/valve-ranking/teams?teamId={rank}" class="ranking-badge vrs-ranking"><span>VRS: </span>#{rank + 5}</a>') if rank else ''
        blocks += (f'<div class="{side}"><a href="/team/{rank or 0}/{team}"><span class="teamName">{team}</span></a></div>'
                   f'<div class="team-detail"><div class="teamRanking">{badge}</div>'
                   f'<a href="/team/{rank or 0}/{team}">{team}</a></div>')
    return ('<html><body><div class="timeAndEvent"><div class="time" data-format="HH:mm" data-unix="' + str(unix) + '"></div></div>'
            + blocks + '</body></html>')


class PipelineSources:
    """Synthetic upstream responses, matching the real source contracts."""

    def __init__(self, now=None):
        self.now = now
        self.log = []
        self.blocked_hosts = {}

    def get(self, name, url, as_json=True):
        self.log.append({'name': name, 'url': url, 'status': 'ok',
                         'observed_at': iso(datetime.now(timezone.utc))})
        stamp = {'observed_at': iso(datetime.now(timezone.utc))}
        if url == FIXTURES:
            return ROWS, stamp
        if url == HOTSPAWN or url == LOBBY:
            return ng_state(ROWS), stamp
        if url == GAMMA + '/sports':
            return [{'sport': 'cs2', 'series': '10310'}], stamp
        if url.startswith(GAMMA + '/events?'):
            market = {'id': '900001', 'question': 'Counter-Strike: Alpha vs Beta (BO1)',
                      'sportsMarketType': 'moneyline', 'active': True, 'closed': False, 'acceptingOrders': True,
                      'outcomes': '["Alpha", "Beta"]', 'outcomePrices': '["0.75", "0.25"]',
                      'gameStartTime': WIDE_START.strftime('%Y-%m-%d %H:%M:%S+00'),
                      'eventStartTime': iso(WIDE_START), 'updatedAt': iso(datetime.now(timezone.utc)),
                      'bestBid': 0.55, 'bestAsk': 0.95, 'liquidity': '2966.0927'}
            return [{'id': '990001', 'slug': 'cs2-alpha-beta-test', 'sport': {'sport': 'cs2'}, 'closed': False,
                     'markets': [market]}], stamp
        if url == 'https://www.hltv.org/matches':
            return hltv_list(), stamp
        if url.startswith('https://www.hltv.org/matches/'):
            fixture_id = next(fid for fid, target in DETAIL_URLS.items() if target == url)
            fixture = next(f for f in ROWS if f['id'] == fixture_id)
            return hltv_detail(fixture, RANKS[fixture_id]), stamp
        if url.startswith(PIN):
            return ([], stamp) if url.endswith('matchups?withSpecials=false') else ([], stamp)
        raise ValueError('HTTP 403 access restricted for ' + url)


class PipelineTierTests(unittest.TestCase):
    def snapshot(self):
        # These tests exercise the market and research tiers. The Valve VRS
        # originated-line tier runs before the research tiers and would price
        # TIER_4 (WROTBERRY vs Nexus, both in Valve's standings); it has its
        # own end-to-end tests in tests/test_vrs.py, so it is disabled here.
        with patch('scripts.refresh.Sources', PipelineSources), \
             patch('scripts.vrs.fetch', return_value=(None, None, None)):
            return run(None)

    def test_wide_tier_and_research_tier_survive_the_full_path(self):
        data = self.snapshot()
        rows = {m['id']: m for m in data['matches']}
        wide = rows['TIER_1']
        self.assertEqual(wide['method'], 'exchange_wide')
        self.assertEqual(wide['pick'], 'Alpha')
        self.assertAlmostEqual(wide['probabilities'][0], .75, places=9)
        self.assertTrue(any('Low confidence' in flag for flag in wide['flags']))
        research = rows['TIER_2']
        self.assertEqual(research['method'], 'research_rank')
        self.assertEqual(research['pick'], 'Delta')
        self.assertIsNone(research['probabilities'])
        self.assertIsNone(research['fair_odds'])
        self.assertEqual(research['evidence'], [])
        single = rows['TIER_3']
        self.assertEqual(single['method'], 'research_rank_single')
        self.assertEqual(single['pick'], 'Epsilon')
        self.assertIsNone(single['probabilities'])
        self.assertIsNone(single['fair_odds'])
        aliased = rows['TIER_4']
        self.assertEqual(aliased['method'], 'research_rank')
        self.assertEqual(aliased['pick'], 'WROTBERRY')
        stored = {r['team']: r for r in aliased['hltv_context']['resolved_ranks']}
        self.assertEqual(stored['WROTBERRY']['hltv_name'], 'WBT')
        self.assertTrue(stored['WROTBERRY']['alias_source'].startswith('https://'))
        self.assertEqual(stored['WROTBERRY']['hltv_rank'], 109)
        self.assertIsNone(stored['Nexus']['alias_source'])
        self.assertEqual(stored['Nexus']['hltv_name'], 'Nexus')

    def test_ranking_evidence_is_required_for_both_research_tiers(self):
        """The validator and the independent auditor must reject stripped evidence."""
        auditor = load_auditor()
        for mutate, label in [
            (lambda row: row['hltv_context'].pop('resolved_ranks'), 'missing per-team rank evidence'),
            (lambda row: row['hltv_context']['resolved_ranks'][0].update(alias_source=None), 'mapping without a primary source'),
            (lambda row: row['hltv_context']['resolved_ranks'][0].update(rank_source=None), 'rank without a ranking link'),
            (lambda row: [r.update(hltv_rank=200) for r in row['hltv_context']['resolved_ranks']], 'rank edited away from the context'),
            (lambda row: row.update(method='research_rank'), 'one-sided row relabelled as the full tier'),
        ]:
            data = self.snapshot()
            target = next(m for m in data['matches'] if m['id'] == ('TIER_3' if 'one-sided' in label else 'TIER_4'))
            mutate(target)
            with self.assertRaises(AssertionError, msg=label):
                validate_data(data)
            _, errors = auditor.inspect(data)
            self.assertTrue(errors, label)

    def test_refresh_output_passes_the_production_validator(self):
        data = self.snapshot()
        report = validate_data(data)
        self.assertEqual(report['rows_verified_against_primary_snapshot'], len(data['matches']))
        self.assertEqual(report['probability_calculations_reproduced'], 1)

    def test_independent_auditor_accepts_the_new_tiers(self):
        auditor = load_auditor()
        data = self.snapshot()
        rows, errors = auditor.inspect(data)
        self.assertEqual(errors, [], errors)
        self.assertEqual(len(rows), len(data['matches']))

    def test_ranking_parse_matches_the_retained_capture(self):
        """The ranking parser must match the real HLTV markup, not a guess.

        This is the exact structure read from the project's retained HLTV capture
        (a WBT vs ENCE match page fetched during this session's research); if HLTV
        changes it, the research tier must fail closed instead of inventing ranks.
        """
        from scripts.core import dt, iso, normalize_fixtures
        from scripts.hltv import context
        html = ('<html><body><div class="timeAndEvent"><div class="time" data-unix="1792065600000"></div></div>'
                '<div class="team1-gradient"><span class="teamName">WBT</span></div>'
                '<div class="team2-gradient"><span class="teamName">ENCE</span></div>'
                '<div class="team-detail"><div class="teamRanking">'
                '<a href="/ranking/teams/2026/october/12/13683" class="ranking-badge hltv-ranking"><span>HLTV: </span>#109</a>'
                '<a href="/valve-ranking/teams?teamId=13683" class="ranking-badge vrs-ranking"><span>VRS: </span>#64</a>'
                '</div><a href="/team/13683/wbt">WBT</a></div>'
                '<div class="team-detail"><div class="teamRanking">'
                '<a href="/ranking/teams/2026/october/12/4869" class="ranking-badge hltv-ranking"><span>HLTV: </span>#114</a>'
                '</div><a href="/team/4869/ence">ENCE</a></div></body></html>')
        fixture = normalize_fixtures([{'id': 'X', 'sport_alias': 'cs2', 'participants0_name': 'WROTBERRY',
            'participants1_name': 'ENCE', 'status': 'scheduled', 'scheduled_start_time': '2026-10-15T12:00:00Z',
            'lock_time': '2026-10-15T11:54:00Z'}], {}, dt('2026-10-15T10:00:00Z'))[0]
        parsed = context(html, fixture)
        self.assertEqual(parsed['start'], iso('2026-10-15T12:00:00Z'))
        self.assertEqual({r['team']: r['hltv_rank'] for r in parsed['ranks']}, {'WBT': 109, 'ENCE': 114})
        for entry in parsed['ranks']:
            self.assertTrue(entry['source'].startswith('https://www.hltv.org/ranking/teams/'))
        self.assertEqual(parsed['numeric_quote_rows'], 0)
        self.assertIn('Rankings are context only', parsed['limitation'])
        self.assertIn('no calibrated rank-to-win model', parsed['limitation'])

    def test_independent_auditor_still_rejects_a_hand_edited_research_pick(self):
        auditor = load_auditor()
        for mutate, label in [
            (lambda row: row.update(pick='Gamma'), 'pick contradicts the verified ranking order'),
            (lambda row: row.update(fair_odds=[1.1, 2.2]), 'research row given fair odds'),
            (lambda row: row['hltv_context']['ranks'].pop(), 'research row without both ranks'),
            (lambda row: row['flags'].clear(), 'research row without its low-confidence flag'),
        ]:
            data = self.snapshot()
            target = next(m for m in data['matches'] if m['id'] == 'TIER_2')
            mutate(target)
            _, errors = auditor.inspect(data)
            self.assertTrue(errors, label)

    def test_independent_auditor_still_rejects_a_tampered_wide_quote(self):
        auditor = load_auditor()
        for mutate, label in [
            (lambda row: row['evidence'][0].update(tier='exchange'), 'wide quote mislabelled as strict'),
            (lambda row: row['evidence'][0].update(strict_rejection=None), 'wide quote without strict rejection'),
            (lambda row: row['evidence'][0]['raw'].update(liquidity='99'), 'wide quote below the liquidity floor'),
            (lambda row: row['evidence'][0]['raw'].update(bestBid=0.01, bestAsk=0.99), 'spread above the wide ceiling'),
        ]:
            data = self.snapshot()
            target = next(m for m in data['matches'] if m['id'] == 'TIER_1')
            mutate(target)
            _, errors = auditor.inspect(data)
            self.assertTrue(errors, label)


if __name__ == '__main__':
    unittest.main()
