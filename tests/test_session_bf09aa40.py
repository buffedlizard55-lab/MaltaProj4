"""Session bf09aa40 regressions: a pick for every open fixture and a probability
wherever research supports one.

Two sourced changes are pinned here, both from the 2026-10-21T20:10:54Z refresh
committed at ``research/harvest-bf09aa40/``:

1. ``data/identities.json`` registers the Off Chops / THUNDER dOWNUNDER rename
   (Liquipedia's dated note, HLTV's team page and Valve's own three-player
   roster-continuity rule). That turns fixture 1082858 Ground Zero vs Off Chops
   from a research-only pick into an originated Valve VRS model line. Every
   probability below is recomputed from Valve's published formula and then
   replayed by ``scripts.validate.validate_model_row``, which re-reads the
   official standings file itself.

2. ``scripts.hltv.research`` also reads HLTV's dated match views for fixtures
   the front list does not contain, so a fixture that starts on a later day
   still collects its HLTV identity (fixture 1081597 benched gods vs TitanFlow
   had no HLTV context at all and ended the run with no pick).

Nothing here invents a price: where the opponent is genuinely absent from
Valve's standings and no market line exists, the tests assert that the
probabilities stay blank.
"""
import json
import math
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts import hltv, vrs
from scripts.core import ALIAS_MAP, norm, plain_name, research_rank_pick
from scripts.validate import validate_model_row

ROOT = Path(__file__).resolve().parents[1]
IDENTITIES = json.loads((ROOT / 'data/identities.json').read_text())
SNAPSHOT = json.loads((ROOT / 'research/harvest-bf09aa40/snapshot.json').read_text())
STANDINGS, META = vrs.vendored(datetime.now(timezone.utc))

# Independent de-vig of Valve's own formula for the two official standings rows
# (Ground Zero 878, THUNDER dOWNUNDER 971 in standings_global_2026_10_05.md).
RAW = 1 / (1 + 10 ** (-vrs.G * (878 - 971) / 400))
P_GZ = 0.5 + vrs.SLOPE * (RAW - 0.5)

LINEUPS = {'Ground Zero': ['apocdud', 'Omichella', 'vision', 'tucks', 'sliimey'],
           'Off Chops': ['viridian', 'dexter', 'Liazz', 'Gratisfaction', 'damyo']}


def fixture_for(fixture_id, teams, lineups=None):
    row = next((m for m in SNAPSHOT['matches'] if m['id'] == fixture_id), None)
    return {'id': fixture_id, 'teams': list(teams), 'state': 'open',
            'start': (row or {}).get('start') or '2026-10-26T03:00:00Z',
            'lock': None, 'best_of': None, 'probabilities': None, 'fair_odds': None,
            'pick': None, 'method': None, 'evidence': [], 'attempts': [],
            'flags': [], 'reason': None,
            'hltv_context': dict((row or {}).get('hltv_context') or {}),
            '_lineups': lineups}


def off_chops_entry():
    return next(e for e in IDENTITIES['aliases'] if e['canonical'] == 'Off Chops')


class TestOffChopsRename(unittest.TestCase):
    def test_rename_is_registered_with_primary_sources(self):
        entry = off_chops_entry()
        self.assertEqual(sorted(plain_name(n) for n in entry['names']),
                         sorted({plain_name('Off Chops'), plain_name('THUNDER dOWNUNDER')}))
        self.assertEqual(entry['source'], 'https://liquipedia.net/counterstrike/Logitech_G_Pro_Series/2026')
        self.assertEqual(entry['additional_source'], 'https://www.hltv.org/team/14095/off-chops')
        for needle in ('THUNDERdOWNUNDER rename to Off Chops',
                       'counter-strike_regional_standings',
                       'TEAM_OVERLAP_TO_SHARE_ROSTER'):
            self.assertIn(needle, entry['basis'])

    def test_alias_maps_both_labels_to_one_key(self):
        self.assertEqual(norm('THUNDER dOWNUNDER'), norm('Off Chops'))
        self.assertEqual(ALIAS_MAP[plain_name('THUNDER dOWNUNDER')], plain_name('Off Chops'))

    def test_alias_resolves_the_official_standings_row_by_roster(self):
        entry, note = vrs.identify('Off Chops', STANDINGS, LINEUPS['Off Chops'])
        self.assertIsNotNone(entry, 'the renamed label must resolve to Valve\'s row')
        self.assertEqual(entry['name'], 'THUNDER dOWNUNDER')
        self.assertEqual((entry['standing'], entry['points']), (119, 971))
        self.assertGreaterEqual(entry['roster_overlap'], vrs.ROSTER_OVERLAP)
        self.assertEqual(entry['roster_overlap'], 4,
                         'dexter, Liazz, Gratisfaction and viridian are shared with the listed roster')
        self.assertIn('roster verified', note)

    def test_rename_does_not_absorb_unrelated_labels(self):
        for label in ('TitanFlow', 'Staqued', 'LOS NINOS', 'benched gods'):
            self.assertNotEqual(norm(label), norm('Off Chops'), label)
        for label in ('TitanFlow', 'Staqued', 'LOS NINOS'):
            entry, note = vrs.identify(label, STANDINGS, None)
            self.assertIsNone(entry, label)
            self.assertIn('not listed in the Valve global standings', note)


class TestOriginatedLineForFixture1082858(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture_for('1082858', ['Ground Zero', 'Off Chops'])
        vrs.apply(self.fixture, STANDINGS, META, LINEUPS)

    def test_line_matches_an_independent_recomputation(self):
        self.assertEqual(self.fixture['method'], 'model_vrs')
        self.assertAlmostEqual(self.fixture['probabilities'][0], P_GZ, places=10)
        self.assertAlmostEqual(self.fixture['probabilities'][1], 1 - P_GZ, places=10)
        self.assertAlmostEqual(sum(self.fixture['probabilities']), 1.0, places=12)
        self.assertEqual(self.fixture['pick'], 'Off Chops')
        self.assertIn(vrs.MODEL_FLAG, self.fixture['flags'])

    def test_quote_records_the_previous_label_and_the_rename_evidence(self):
        quote = self.fixture['evidence'][0]
        self.assertEqual(quote['vrs_teams'], ['Ground Zero', 'THUNDER dOWNUNDER'])
        self.assertEqual(quote['points'], [878, 971])
        self.assertEqual(quote['fixture_teams'], ['Ground Zero', 'Off Chops'])
        identities = {i['canonical'] for i in quote['identity_sources']}
        self.assertIn('Off Chops', identities)

    def test_independent_validator_replays_the_row(self):
        # scripts.validate re-reads Valve's official file and re-derives every
        # number, the identity mapping and the pick.
        validate_model_row(self.fixture, self.fixture['evidence'][0], datetime.now(timezone.utc))

    def test_probabilities_are_reproducible_from_the_points_alone(self):
        raw = vrs.expected(878, 971)
        self.assertTrue(math.isclose(raw, RAW, rel_tol=0, abs_tol=1e-12))
        self.assertTrue(math.isclose(vrs.calibrated(raw), P_GZ, rel_tol=0, abs_tol=1e-12))


class TestHltvDatedViews(unittest.TestCase):
    FRONT = """<html><body>
      <div class="matches"><div>
        <a class="match-teams" href="/matches/2399999/other-vs-match-x">
          <div class="match-teamname">Other</div><div class="match-teamname">Match</div></a>
        <div class="match-time" data-unix="1792587600000"></div>
      </div></div></body></html>"""

    DATED = """<html><body>
      <div class="matches"><div>
        <a class="match-teams" href="/matches/2399900/benched-gods-vs-titanflow-cct-2026-challengers-europe-series-8">
          <div class="match-teamname">benched gods</div><div class="match-teamname">TitanFlow</div></a>
        <div class="match-time" data-unix="1792666800000"></div>
      </div></div></body></html>"""

    MATCH = """<html><body>
      <div class="timeAndEvent"><div class="time" data-unix="1792666800000"></div></div>
      <div class="team1-gradient"><div class="teamName">benched gods</div></div>
      <div class="team2-gradient"><div class="teamName">TitanFlow</div></div>
      <div class="teamRanking"><a href="/team/13599/benched-gods">benched gods</a>
        <a class="hltv-ranking" href="/ranking/teams/2026/october/19/13599">#175</a></div>
      <div class="lineups"><div class="lineup">
        <div class="box-headline"><a href="/team/13599/benched-gods">benched gods</a></div>
        <table><tbody>
          <tr><td class="player"><span class="player-compare"><span class="text-ellipsis">Wign</span></span></td></tr>
          <tr><td class="player"><span class="player-compare"><span class="text-ellipsis">K014NZ</span></span></td></tr>
          <tr><td class="player"><span class="player-compare"><span class="text-ellipsis">facer</span></span></td></tr>
          <tr><td class="player"><span class="player-compare"><span class="text-ellipsis">norescue</span></span></td></tr>
          <tr><td class="player"><span class="player-compare"><span class="text-ellipsis">yoyoS2</span></span></td></tr>
        </tbody></table></div></div></body></html>"""

    class Src:
        """Minimal read-only source stub that records every URL it was asked for."""

        def __init__(self, pages):
            self.pages = pages
            self.read = []

        def get(self, name, url, as_json=True, headers=None):
            self.read.append(url)
            if url not in self.pages:
                raise ValueError('Unexpected URL requested: ' + url)
            return self.pages[url], {'url': url, 'observed_at': '2026-10-21T20:10:54Z',
                                     'status': 'ok', 'http_status': 200, 'bytes': len(self.pages[url])}

    def test_a_fixture_missing_from_the_front_list_is_found_on_its_dated_view(self):
        fixture = {'id': '1081597', 'teams': ['benched gods', 'TitanFlow'],
                   'start': '2026-10-22T11:00:00Z', 'attempts': [], 'flags': []}
        src = self.Src({'https://www.hltv.org/matches': self.FRONT,
                        'https://www.hltv.org/matches?selectedDate=2026-10-22': self.DATED,
                        'https://www.hltv.org/matches/2399900/benched-gods-vs-titanflow-cct-2026-challengers-europe-series-8': self.MATCH})
        hltv.research([fixture], src)
        self.assertIn('https://www.hltv.org/matches?selectedDate=2026-10-22', src.read,
                      'the dated view for the fixture\'s UTC date must be read')
        context = fixture.get('hltv_context')
        self.assertTrue(context, 'HLTV identity must be collected from the dated view')
        self.assertEqual(context['teams'], ['benched gods', 'TitanFlow'])
        self.assertEqual(context['start'], '2026-10-22T11:00:00Z')
        lineups = {x['team']: x['players'] for x in context['lineups']}
        self.assertEqual(sorted(lineups['benched gods']),
                         sorted(['Wign', 'K014NZ', 'facer', 'norescue', 'yoyoS2']))
        attempt = next(a for a in fixture['attempts'] if a['provider'] == 'HLTV')
        self.assertEqual(attempt['status'], 'unresolved')  # context only; never a price
        self.assertEqual(attempt['date_views'][0]['url'],
                         'https://www.hltv.org/matches?selectedDate=2026-10-22')
        self.assertEqual(attempt['date_views'][0]['status'], 'ok')

    def test_the_neighbouring_hltv_day_can_supply_the_identity(self):
        # HLTV groups its list by its own local day, so the pair can be published
        # on the page after the fixture's UTC date while carrying the same start.
        dated = self.DATED.replace('/matches/2399900/benched-gods-vs-titanflow-cct-2026-challengers-europe-series-8',
                                   '/matches/2399901/benched-gods-vs-titanflow-cct')
        src = self.Src({'https://www.hltv.org/matches': self.FRONT,
                        'https://www.hltv.org/matches?selectedDate=2026-10-22':
                            '<html><body><div class="matches"></div></body></html>',
                        'https://www.hltv.org/matches?selectedDate=2026-10-23': dated,
                        'https://www.hltv.org/matches?selectedDate=2026-10-21':
                            '<html><body><div class="matches"></div></body></html>',
                        'https://www.hltv.org/matches/2399901/benched-gods-vs-titanflow-cct':
                            self.MATCH})
        fixture = {'id': '1081597', 'teams': ['benched gods', 'TitanFlow'],
                   'start': '2026-10-22T11:00:00Z', 'attempts': [], 'flags': []}
        hltv.research([fixture], src)
        self.assertEqual(fixture['hltv_context']['source'],
                         'https://www.hltv.org/matches/2399901/benched-gods-vs-titanflow-cct')
        self.assertEqual(fixture['hltv_context']['start'], '2026-10-22T11:00:00Z',
                         'the start stays the one the official feed published')
        attempt = next(a for a in fixture['attempts'] if a['provider'] == 'HLTV')
        self.assertEqual([d['url'].split('selectedDate=')[1] for d in attempt['date_views']],
                         ['2026-10-22', '2026-10-23', '2026-10-21'],
                         "own UTC date first, then the neighbouring HLTV days")

    def test_a_neighbouring_day_never_supplies_a_different_start(self):
        earlier = self.DATED.replace('1792666800000', '1792663200000')
        empty = '<html><body><div class="matches"></div></body></html>'
        src = self.Src({'https://www.hltv.org/matches': self.FRONT,
                        'https://www.hltv.org/matches?selectedDate=2026-10-22': empty,
                        'https://www.hltv.org/matches?selectedDate=2026-10-23': earlier,
                        'https://www.hltv.org/matches?selectedDate=2026-10-21': empty})
        fixture = {'id': '1081597', 'teams': ['benched gods', 'TitanFlow'],
                   'start': '2026-10-22T11:00:00Z', 'attempts': [], 'flags': []}
        hltv.research([fixture], src)
        self.assertIsNone(fixture.get('hltv_context'))
        attempt = next(a for a in fixture['attempts'] if a['provider'] == 'HLTV')
        self.assertEqual([c['start'] for c in attempt['same_pair_other_start']],
                         ['2026-10-22T10:00:00Z'])

    def test_the_dated_lineup_resolves_a_duplicated_valve_label(self):
        # The reason this fixture had no pick: 'benched gods' appears twice in
        # Valve's standings and without a lineup the label cannot be resolved.
        entry, note = vrs.identify('benched gods', STANDINGS, None)
        self.assertIsNone(entry)
        self.assertIn('appears 2 times', note)
        lineup = ['Wign', 'K014NZ', 'facer', 'norescue', 'yoyoS2']
        entry, note = vrs.identify('benched gods', STANDINGS, lineup)
        self.assertIsNotNone(entry, 'the HLTV lineup must disambiguate the repeated label')
        self.assertEqual(entry['roster'], ['facer', 'K014NZ', 'norescue', 'Wign', 'yoyoS2'])
        self.assertEqual(entry['points'], 811)

    def test_dated_views_are_bounded_and_a_refusal_is_recorded(self):
        fixtures = [{'id': 'x%d' % i, 'teams': ['A%d' % i, 'B%d' % i],
                     'start': '2026-11-%02dT10:00:00Z' % (i + 1), 'attempts': [], 'flags': []}
                    for i in range(hltv.DATE_PAGE_LIMIT + 3)]
        src = self.Src({'https://www.hltv.org/matches': self.FRONT})
        hltv.research(fixtures, src)
        dated_reads = [u for u in src.read if 'selectedDate=' in u]
        self.assertEqual(len(dated_reads), hltv.DATE_PAGE_LIMIT,
                         'HLTV must not be hammered with one request per fixture')
        attempt = next(a for a in fixtures[0]['attempts'] if a['provider'] == 'HLTV')
        self.assertIn('No unique exact team-pair and UTC-start match', attempt['reason'])
        self.assertIn('Dated HLTV views also read', attempt['reason'])
        self.assertEqual({d['status'] for d in attempt['date_views']}, {'error'})

    def test_a_start_mismatch_is_recorded_and_never_corrected(self):
        # HLTV lists the same opponent pair one hour earlier than Hotspawn: the
        # fixture must stay unmatched, with the near miss published as evidence.
        front = """<html><body><div class="matches"><div>
          <a class="match-teams" href="/matches/7/benched-gods-vs-titanflow-x">
            <div class="match-teamname">benched gods</div>
            <div class="match-teamname">TitanFlow</div></a>
          <div class="match-time" data-unix="1792663200000"></div></div></div></body></html>"""
        fixture = {'id': '1081597', 'teams': ['benched gods', 'TitanFlow'],
                   'start': '2026-10-22T11:00:00Z', 'attempts': [], 'flags': []}
        src = self.Src({'https://www.hltv.org/matches': front,
                        'https://www.hltv.org/matches?selectedDate=2026-10-22': front})
        hltv.research([fixture], src)
        self.assertIsNone(fixture.get('hltv_context'),
                          'a different UTC start may never be corrected into a match')
        attempt = next(a for a in fixture['attempts'] if a['provider'] == 'HLTV')
        self.assertEqual(attempt['candidates'], [])
        self.assertEqual([c['start'] for c in attempt['same_pair_other_start']],
                         ['2026-10-22T10:00:00Z'])

    def test_no_dated_read_when_the_front_list_already_covers_every_fixture(self):
        front = """<html><body><div class="matches"><div>
          <a class="match-teams" href="/matches/1/a-vs-b"><div class="match-teamname">A</div>
          <div class="match-teamname">B</div></a>
          <div class="match-time" data-unix="1792587600000"></div></div></div></body></html>"""
        match = """<html><body>
          <div class="timeAndEvent"><div class="time" data-unix="1792587600000"></div></div>
          <div class="team1-gradient"><div class="teamName">A</div></div>
          <div class="team2-gradient"><div class="teamName">B</div></div></body></html>"""
        src = self.Src({'https://www.hltv.org/matches': front, 'https://www.hltv.org/matches/1/a-vs-b': match})
        hltv.research([{'id': '1', 'teams': ['A', 'B'], 'start': '2026-10-21T13:00:00Z',
                        'attempts': [], 'flags': []}], src)
        self.assertEqual([u for u in src.read if 'selectedDate=' in u], [])


class TestNoInventedProbabilities(unittest.TestCase):
    def test_a_fixture_whose_opponent_is_absent_stays_unpriced(self):
        lineups = {'1081597': {'benched gods': ['Wign', 'K014NZ', 'facer', 'norescue', 'yoyoS2']}}
        for fixture_id, teams in (('1082860', ['FlyQuest', 'Staqued']),
                                  ('1082837', ['Zetta', 'LOS NINOS']),
                                  ('1081597', ['benched gods', 'TitanFlow'])):
            fixture = fixture_for(fixture_id, teams)
            vrs.apply(fixture, STANDINGS, META, lineups.get(fixture_id))
            self.assertIsNone(fixture['probabilities'], fixture_id)
            reason = next(a for a in fixture['attempts']
                          if a['provider'] == 'Valve VRS model')['reason']
            self.assertIn(teams[1] + ': not listed in the Valve global standings', reason)

    def test_the_research_pick_survives_without_a_number(self):
        fixture = fixture_for('1082860', ['FlyQuest', 'Staqued'])
        research_rank_pick(fixture)
        self.assertEqual(fixture['pick'], 'FlyQuest')
        self.assertEqual(fixture['method'], 'research_rank_single')
        self.assertIsNone(fixture['probabilities'])
        self.assertIsNone(fixture['fair_odds'])


class TestHarvestGapEvidence(unittest.TestCase):
    def test_the_committed_snapshot_names_every_gap_row(self):
        # Post-fix harvest (run 39670144626, snapshot 2026-10-21T20:30:11Z):
        # 1082858 is no longer a gap because the registered rename lets the
        # originated model price it; the remaining three are the honest ceiling.
        gaps = json.loads((ROOT / 'research/harvest-bf09aa40/gaps.json').read_text())
        self.assertEqual(gaps['snapshot_generated_at'], SNAPSHOT['generated_at'])
        self.assertEqual(sorted(g['id'] for g in gaps['gaps']),
                         ['1081597', '1082837', '1082860'])
        self.assertEqual(gaps['no_pick'], ['1081597'])

    def test_the_live_refresh_now_prices_the_off_chops_fixture(self):
        row = next(m for m in SNAPSHOT['matches'] if m['id'] == '1082858')
        self.assertEqual(row['state'], 'open')
        self.assertEqual(row['method'], 'model_vrs')
        self.assertEqual(row['pick'], 'Off Chops')
        raw = vrs.expected(878, 971)
        expected = [vrs.calibrated(raw), 1 - vrs.calibrated(raw)]
        for got, want in zip(row['probabilities'], expected):
            self.assertAlmostEqual(got, want, places=12)
        quote = row['evidence'][0]
        self.assertEqual(quote['vrs_teams'], ['Ground Zero', 'THUNDER dOWNUNDER'])
        # This is a retained historical capture, so replay freshness at the
        # capture's own timestamp. Using wall-clock time made the test fail
        # permanently once the snapshot aged past the eight-hour input TTL.
        snapshot_time = datetime.fromisoformat(SNAPSHOT['generated_at'].replace('Z', '+00:00'))
        validate_model_row(row, quote, snapshot_time)

    def test_the_probe_recorded_refusals_instead_of_prices(self):
        report = json.loads((ROOT / 'research/harvest-bf09aa40/probe/probe-report.json').read_text())
        self.assertEqual(report['matches_found'], [],
                         'no exact book listing was found, so no receipt may be written')
        self.assertEqual(report['markets']['polymarket']['gap_hits'], [])
        self.assertEqual(report['markets']['pinnacle']['gap_hits'], [])
        self.assertTrue(any(p['status'] == 'error' for p in report['pages']),
                        'refused sources must stay visible in the evidence')


if __name__ == '__main__':
    unittest.main()
