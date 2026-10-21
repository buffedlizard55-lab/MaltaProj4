"""Session 1395f539: a pick for the last unpicked fixture, sourced honestly.

Fixture 1081597 (benched gods vs TitanFlow, CCT Europe 2026 Challengers #8,
2026-10-22T11:00:00Z) had no pick because HLTV publishes that bracket slot with
TBA teams (match 2399696, "Lower Bracket Round 3 #2"), so the collector had no
fixture lineup, Valve's published global standings repeat the label
"benched gods" twice, and no accessible book listed a two-way price.

These tests pin the new evidence path: each label is resolved to exactly one
HLTV team page by that page's own heading, the page's published starting five
supplies the roster evidence Valve's continuity rule needs, and the existing
one-sided Valve-standings tier then produces a pick with **no percentage**.
They also pin the refusals that keep it honest.
"""
import json
import unittest
from pathlib import Path

from scripts import build, hltv, refresh, validate, vrs
from scripts.core import dt, normalize_fixtures

ROOT = Path(__file__).resolve().parents[1]


BENCHED = """<html><body>
<div class="profile-team-name"><h1>benched gods</h1></div>
<div class="teamProfile">
  <a href="/ranking/teams/2026/october/19/details/13599">#204</a>
  <a href="/ranking/teams/2026/october/19/country/Russia">#31 in Russia</a>
  <a href="/valve-ranking/teams?teamId=13599">#161</a>
</div>
<h2>FAQ</h2>
<p>Who plays for benched gods?</p>
<p>The main lineup of benched gods is <a href="/player/23773/wign">Wign</a>,
<a href="/player/24840/k014nz">K014NZ</a>, <a href="/player/24885/facer">facer</a>,
<a href="/player/26059/norescue">norescue</a> &amp; <a href="/player/26646/yoyos2">yoyoS2</a></p>
<p>What is benched gods' current world rank?</p>
<p>benched gods is currently <a href="/ranking/teams/2026/october/19/details/13599">ranked #204</a> in our world ranking</p>
</body></html>"""

TITAN = """<html><body>
<div class="profile-team-name"><h1>TitanFlow</h1></div>
<div class="teamProfile"><span class="ranking">-</span><span class="valve">-</span></div>
<h2>FAQ</h2>
<p>Who plays for TitanFlow?</p>
<p>TitanFlow has no active players in their lineup at the moment</p>
<p>What is TitanFlow's current world rank?</p>
<p>TitanFlow doesn't have a world rank at the moment.</p>
<p>TitanFlow does not currently have a roster.</p>
</body></html>"""

SEARCH = """<html><body><table>
<tr><td>Team</td><td><a href="/team/13599/benched-gods"><img src="logo.png" alt="">benched gods</a></td></tr>
<tr><td>Team</td><td><a href="/team/14021/titanflow"><img src="logo.png" alt="">TitanFlow</a></td></tr>
<tr><td>Player</td><td><a href="/player/23773/wign">Wign</a></td></tr>
</table></body></html>"""

DUPLICATE_SEARCH = """<html><body><table>
<tr><td><a href="/team/14021/titanflow">TitanFlow</a></td></tr>
<tr><td><a href="/team/19999/titanflow-academy">TitanFlow</a></td></tr>
</table></body></html>"""

WRONG_PAGE = """<html><body><div class="profile-team-name"><h1>TitanFlow Academy</h1></div></body></html>"""


class FakeSources:
    """Minimal stand-in for scripts.refresh.Sources.get."""

    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def get(self, name, url, as_json=True, headers=None):
        self.calls.append((name, url))
        for prefix, body in self.pages:
            if url.startswith(prefix):
                return body, {'name': name, 'url': url, 'status': 'ok',
                              'observed_at': '2026-10-21T20:00:00Z'}
        raise ValueError('HTTP 404 for ' + url)


def fixture(method=None, **extra):
    row = {'id': '1081597', 'teams': ['benched gods', 'TitanFlow'],
           'team_ids': ['150001', '150002'], 'competition': 'CCT Europe 2026 Challengers #8',
           'tier': 'c', 'best_of': None, 'start': '2026-10-22T11:00:00Z',
           'lock': '2026-10-22T10:54:00Z', 'source_status': 'scheduled', 'state': 'open',
           'source_url': 'https://www.hotspawn.com/matches/benched-gods-vs-titanflow-cct-europe-2026-challengers-8-1081597',
           'probabilities': None, 'fair_odds': None, 'pick': None, 'method': method,
           'evidence': [], 'attempts': [], 'flags': [], 'reason': None, 'expires_at': None}
    row.update(extra)
    return row


def standings():
    text = (ROOT / 'data/vrs/standings_global_2026_10_05.md').read_text()
    return vrs.parse(text)


def meta():
    raw = json.loads((ROOT / 'data/vrs/meta.json').read_text())
    raw.update(origin='vendored', observed_at='2026-10-21T20:00:00Z')
    return raw


class TeamPageParsing(unittest.TestCase):
    def test_search_keeps_only_team_links(self):
        found = hltv.search_teams(SEARCH)
        self.assertEqual(found, {'https://www.hltv.org/team/14021/titanflow': 'TitanFlow',
                                 'https://www.hltv.org/team/13599/benched-gods': 'benched gods'})

    def test_ranked_page_yields_lineup_and_rank(self):
        profile = hltv.team_profile(BENCHED, 'benched gods')
        self.assertEqual(profile['lineup'], ['Wign', 'K014NZ', 'facer', 'norescue', 'yoyoS2'])
        self.assertEqual(profile['world_rank'], 204)
        self.assertEqual(profile['world_rank_status'], 'ranked')
        self.assertTrue(profile['world_rank_source'].startswith('https://www.hltv.org/ranking/teams/'))
        self.assertEqual(profile['vrs_rank'], 161)

    def test_page_without_rank_needs_an_explicit_absence(self):
        profile = hltv.team_profile(TITAN, 'TitanFlow')
        self.assertEqual(profile['lineup'], [])
        self.assertIsNone(profile['world_rank'])
        self.assertEqual(profile['world_rank_status'], 'unranked')
        self.assertTrue(profile['roster_absent'])
        unknown = hltv.team_profile('<html><body><h1>TitanFlow</h1><p>No ranking here.</p></body></html>', 'TitanFlow')
        self.assertEqual(unknown['world_rank_status'], 'unknown')

    def test_a_near_match_heading_is_refused(self):
        with self.assertRaises(ValueError):
            hltv.team_profile(WRONG_PAGE, 'TitanFlow')


class TeamPageResearch(unittest.TestCase):
    def test_both_pages_are_recorded_with_their_urls(self):
        src = FakeSources([('https://www.hltv.org/search', SEARCH),
                           ('https://www.hltv.org/team/13599', BENCHED),
                           ('https://www.hltv.org/team/14021', TITAN)])
        row = fixture()
        hltv.team_pages([row], src)
        pages = row['hltv_team_pages']
        self.assertEqual([p['team'] for p in pages['teams']], ['benched gods', 'TitanFlow'])
        self.assertEqual(pages['teams'][0]['url'], 'https://www.hltv.org/team/13599/benched-gods')
        self.assertEqual(pages['observed_at'], '2026-10-21T20:00:00Z')
        self.assertEqual(row['attempts'][-1]['status'], 'resolved')
        self.assertIn('no probability derived', row['attempts'][-1]['reason'])

    def test_ambiguous_search_is_refused(self):
        src = FakeSources([('https://www.hltv.org/search', DUPLICATE_SEARCH)])
        row = fixture()
        hltv.team_pages([row], src)
        self.assertNotIn('hltv_team_pages', row)
        self.assertEqual(row['attempts'][-1]['status'], 'unresolved')
        self.assertIn('unique identity is required', row['attempts'][-1]['reason'])

    def test_heading_mismatch_is_refused(self):
        src = FakeSources([('https://www.hltv.org/search', SEARCH),
                           ('https://www.hltv.org/team/13599', BENCHED),
                           ('https://www.hltv.org/team/14021', WRONG_PAGE)])
        row = fixture()
        hltv.team_pages([row], src)
        self.assertNotIn('hltv_team_pages', row)
        self.assertEqual(row['attempts'][-1]['status'], 'unresolved')

    def test_fixtures_with_an_hltv_fixture_identity_are_left_alone(self):
        row = fixture(hltv_context={'lineups': [], 'ranks': []})
        src = FakeSources([])
        hltv.team_pages([row], src)
        self.assertNotIn('hltv_team_pages', row)
        self.assertEqual(src.calls, [])

    def test_research_calls_the_team_page_step(self):
        calls = []
        original = hltv.team_pages
        try:
            hltv.team_pages = lambda matches, src: calls.append(list(matches))
            match_list = """<html><body><div class="match"><a class="match-teams" href="/matches/1/a-vs-b">
                <div class="match-teamname">A</div><div class="match-teamname">B</div></a>
                <div class="match-time" data-unix="1780000000000"></div></div></body></html>"""
            hltv.research([fixture()], FakeSources([('https://www.hltv.org/matches', match_list)]))
        finally:
            hltv.team_pages = original
        self.assertEqual(len(calls), 1)

    def test_refresh_merges_team_page_lineups(self):
        row = fixture(hltv_team_pages={'observed_at': '2026-10-21T20:00:00Z', 'teams': [
            {'team': 'benched gods', 'lineup': ['Wign', 'K014NZ', 'facer', 'norescue', 'yoyoS2'],
             'url': 'https://www.hltv.org/team/13599/benched-gods'},
            {'team': 'TitanFlow', 'lineup': [], 'url': 'https://www.hltv.org/team/14021/titanflow'}]})
        lineups, receipt = refresh.fixture_lineups(row)
        self.assertEqual(lineups['benched gods'], ['Wign', 'K014NZ', 'facer', 'norescue', 'yoyoS2'])
        # TitanFlow publishes no roster on its own page, so the retained HLTV
        # lineup receipt fills that side; the receipt is returned for the row.
        self.assertEqual(sorted(lineups['TitanFlow']), sorted(['ves111', 'ZzZoOm', 'Saiman Strit', 'keeisen', 'Henma']))
        self.assertEqual(receipt['fixture_id'], '1081597')


class OneSidedResolution(unittest.TestCase):
    def resolved(self):
        row = fixture(hltv_team_pages={'observed_at': '2026-10-21T20:00:00Z', 'teams': [
            {'team': 'benched gods', 'lineup': ['Wign', 'K014NZ', 'facer', 'norescue', 'yoyoS2'],
             'url': 'https://www.hltv.org/team/13599/benched-gods'},
            {'team': 'TitanFlow', 'lineup': [], 'url': 'https://www.hltv.org/team/14021/titanflow'}]})
        vrs.research_single(row, standings(), meta(), refresh.fixture_lineups(row)[0])
        return row

    def test_the_last_unpicked_fixture_gets_a_sourced_pick_and_no_percentage(self):
        row = self.resolved()
        self.assertEqual(row['pick'], 'benched gods')
        self.assertEqual(row['method'], 'research_vrs_single')
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['fair_odds'])
        self.assertEqual(row['evidence'], [])
        self.assertIn('not a market probability', row['reason'])
        self.assertTrue(any('no probability published' in flag.lower() for flag in row['flags']))
        research = row['vrs_research']
        self.assertEqual(research['standings_as_of'], '2026-10-05')
        listed, absent = research['resolved_vrs']
        self.assertEqual((listed['team'], listed['standing'], listed['points']), ('benched gods', 157, 811))
        self.assertEqual(listed['roster_overlap'], 5)
        self.assertEqual(absent['team'], 'TitanFlow')
        self.assertEqual(absent['status'], 'absent')
        self.assertEqual(absent['label_count'], 0)

    def test_the_roster_source_is_on_the_row(self):
        row = self.resolved()
        sources = {p['team']: p['url'] for p in row['hltv_team_pages']['teams']}
        self.assertTrue(sources['benched gods'].startswith('https://www.hltv.org/team/'))
        self.assertTrue(sources['TitanFlow'].startswith('https://www.hltv.org/team/'))

    def test_a_row_without_team_page_rosters_still_refuses(self):
        row = fixture()
        vrs.research_single(row, standings(), meta(), {})
        self.assertIsNone(row['pick'])
        self.assertIsNone(row['method'])

    def test_the_rendered_row_links_each_team_page(self):
        row = self.resolved()
        row.update(published_at='2026-10-21T20:00:00Z')
        html = build.table([row], review=True)
        self.assertIn('https://www.hltv.org/team/13599/benched-gods', html)
        self.assertIn('https://www.hltv.org/team/14021/titanflow', html)
        self.assertIn('Roster from the HLTV team pages', html)
        self.assertIn('Research only · Valve listing', html)


class ValidatorAcceptance(unittest.TestCase):
    """The row the collector will publish must pass the shipped validator."""

    RAW = {'id': '1081597', 'participants0_id': '150001', 'participants0_name': 'benched gods',
           'participants1_id': '150002', 'participants1_name': 'TitanFlow',
           'competition_name': 'CCT Europe 2026 Challengers #8', 'tier': 'c', 'best_of': None,
           'status': 'scheduled', 'scheduled_start_time': '1792666800000',
           'lock_time': '1792666440000', 'sport_alias': 'cs2'}

    def published(self):
        original = normalize_fixtures([self.RAW], {}, dt('2026-10-21T20:00:00Z'))[0]
        self.assertEqual((original['start'], original['lock']), ('2026-10-22T11:00:00Z', '2026-10-22T10:54:00Z'))
        row = dict(original, probabilities=None, fair_odds=None, pick=None, method=None,
                   evidence=[], attempts=[], flags=[], reason=None, expires_at=None,
                   hltv_team_pages={'observed_at': '2026-10-21T20:00:00Z', 'teams': [
                       {'team': 'benched gods', 'lineup': ['Wign', 'K014NZ', 'facer', 'norescue', 'yoyoS2'],
                        'url': 'https://www.hltv.org/team/13599/benched-gods'},
                       {'team': 'TitanFlow', 'lineup': [],
                        'url': 'https://www.hltv.org/team/14021/titanflow'}]})
        vrs.research_single(row, standings(), meta(), refresh.fixture_lineups(row)[0])
        return row

    def test_validator_accepts_the_one_sided_row(self):
        row = self.published()
        validate.validate_data({'schema_version': 2, 'generated_at': '2026-10-21T20:00:00Z',
                                'fixtures_observed_at': '2026-10-21T20:00:00Z',
                                'matches': [row], 'fixture_evidence': [self.RAW], 'issues': []})

    def test_lineup_must_be_reproducible_from_a_source_named_on_the_row(self):
        row = self.published()
        real = ['Wign', 'K014NZ', 'facer', 'norescue', 'yoyoS2']
        self.assertTrue(validate.lineup_source_ok(row, 'benched gods', real),
                        'the club team page on the row is the source')
        with_pages = row.pop('hltv_team_pages')
        self.assertTrue(validate.lineup_source_ok(row, 'benched gods', real),
                        'the retained HLTV lineup receipt is an equally valid source')
        self.assertFalse(validate.lineup_source_ok(row, 'benched gods', real + ['Invented Player']))
        row['hltv_team_pages'] = with_pages
        row['hltv_team_pages']['teams'] = [dict(t, url='https://example.com/fake') for t in with_pages['teams']]
        row.pop('hltv_team_pages')
        self.assertFalse(validate.lineup_source_ok(row, 'TitanFlow', ['Ghost']))


class PhoneFirstSummary(unittest.TestCase):
    """The executive summary must link to the picks, and never double-escape."""

    def test_glance_footer_escapes_the_ampersand_once(self):
        row = ValidatorAcceptance().published()
        opens = [row]
        html = build.glance({'last_attempt_at': '2026-10-21T20:00:00Z'}, opens)
        self.assertNotIn('&amp;amp;', html)
        self.assertIn('Unresolved &amp; limitations', html)
        self.assertIn('href="picks.html"', html)
        self.assertIn('href="#unresolved-summary"', html)
        self.assertIn('href="unresolved.html"', html)

    def test_every_unpicked_row_says_why_and_links_its_evidence(self):
        row = ValidatorAcceptance().published()
        html = build.glance({'last_attempt_at': '2026-10-21T20:00:00Z'}, [row])
        self.assertIn('Research pick: <strong>benched gods</strong>', html)
        self.assertIn('Research only', html)
        self.assertIn('evidence.html#match-1081597', html)
        self.assertIn('glance-card-mobile', html, 'phones need the card layout, not the wide table')


class LineupReceiptLink(unittest.TestCase):
    """A pick whose roster came from the retained receipt must link that receipt."""

    def test_receipt_url_appears_on_the_row(self):
        row = ValidatorAcceptance().published()
        row['hltv_team_pages'] = {'observed_at': '2026-10-21T20:00:00Z', 'teams': []}
        row['attempts'].append({'provider': 'HLTV lineup receipt', 'status': 'resolved',
            'url': 'https://www.hltv.org/matches/2399691/benched-gods-vs-ex-6666-cct-2026-challengers-europe-series-8',
            'reason': 'Feeder-match lineups for both clubs.'})
        html = build.table([row], review=True)
        self.assertIn('HLTV lineup receipt ↗', html)
        self.assertIn('hltv.org/matches/2399691', html)
        self.assertIn('Roster from the retained HLTV lineup receipt', html)
        self.assertNotIn('Roster from the HLTV team pages', html)


if __name__ == '__main__':
    unittest.main()
