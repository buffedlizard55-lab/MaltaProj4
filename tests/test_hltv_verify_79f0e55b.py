"""Unit tests for scripts/hltv_verify_79f0e55b.py (session 79f0e55b).

These run offline against synthetic markup shaped like HLTV's own pages. They pin the
properties the verification depends on: extraction is deterministic, failures are
recorded as receipts instead of raising, and a missing selector yields ``None`` rather
than an invented value.
"""
import unittest
from unittest import mock

from scripts import hltv_verify_79f0e55b as hv

RESULTS_HTML = """
<div class="results-sublist">
  <div class="standard-headline">October 16th 2026</div>
  <div class="results-all">
    <div class="result-con">
      <a href="/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026">
        <div class="team">Aurora</div><div class="team">9z</div>
        <div class="result-score"><span class="won">2</span> - <span class="lost">0</span></div>
      </a>
    </div>
    <div class="result-con">
      <a href="/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026">
        <div class="team">BETBOOM</div><div class="team">Legacy</div>
        <div class="result-score"><span class="won">2</span> - <span class="lost">1</span></div>
      </a>
    </div>
  </div>
</div>
"""

SCHEDULE_HTML = """
<div class="match-day">
  <div class="standard-headline">Saturday - 2026-10-17</div>
  <div class="upcomingMatch">
    <a class="match" href="/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026">
      <div class="matchTime">10:00</div>
      <div class="matchMeta">bo3</div>
      <div class="matchTeamName">FURIA</div><div class="matchTeamName">Aurora</div>
      <div class="matchEventName">Thunderpick World Championship 2026</div>
    </a>
  </div>
  <div class="upcomingMatch">
    <a class="match" href="/matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026">
      <div class="matchTime">13:00</div>
      <div class="matchMeta">bo3</div>
      <div class="matchTeamName">Falcons</div><div class="matchTeamName">BETBOOM</div>
    </a>
  </div>
</div>
<div class="match-day">
  <div class="standard-headline">Sunday - 2026-10-18</div>
  <div class="upcomingMatch">
    <a class="match" href="/matches/2399416/third-place-decider">
      <div class="matchTime">07:30</div><div class="matchMeta">bo3</div>
      <div class="matchTeamName">TBD</div><div class="matchTeamName">TBD</div>
    </a>
  </div>
</div>
"""

# The flat shape: day heading followed by its own matches, with no per-day wrapper.
FLAT_SCHEDULE_HTML = """
<div>
  <div class="standard-headline">Saturday - 2026-10-17</div>
  <div class="upcomingMatch">
    <a class="match" href="/matches/2399414/x"><div class="matchTime">10:00</div>
      <div class="matchTeamName">FURIA</div><div class="matchTeamName">Aurora</div></a>
  </div>
  <div class="standard-headline">Sunday - 2026-10-18</div>
  <div class="upcomingMatch">
    <a class="match" href="/matches/2399417/x"><div class="matchTime">11:00</div>
      <div class="matchTeamName">TBD</div><div class="matchTeamName">TBD</div></a>
  </div>
</div>
"""


# The shape HLTV's event schedule actually serves (captured 2026-10-17, trimmed of images
# and tracking attributes): a day label in span.event-headline and rows in div.match whose
# .match-time carries the absolute epoch in data-unix.
REAL_SCHEDULE_HTML = """
<div class="matches-list eventpage-matches-list">
  <span class="event-headline">Saturday - 2026-10-17</span>
  <div class="match">
    <div class="match-bottom">
      <a class="match-info" href="/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026">
        <div class="match-time" data-time-format="HH:mm" data-unix="1792245600000">16:00</div>
        <div class="match-meta">bo3</div></a>
      <a class="match-teams" href="/matches/2399414/x">
        <div class="match-team team1"><div class="match-teamname text-ellipsis">FURIA</div></div>
        <div class="match-team team2"><div class="match-teamname text-ellipsis">Aurora</div></div></a>
      <div class="match-fixtures-placeholder" data-match-id="2399414"></div>
      <div class="match-btn-wrapper"><div class="match-stage match-semifinal">Semifinal</div></div>
    </div>
  </div>
  <div class="match">
    <div class="match-bottom">
      <a class="match-info" href="/matches/2399415/falcons-vs-betboom-x">
        <div class="match-time" data-unix="1792256400000">19:00</div>
        <div class="match-meta">bo3</div></a>
      <a class="match-teams" href="/matches/2399415/x">
        <div class="match-team team1"><div class="match-teamname">Falcons</div></div>
        <div class="match-team team2"><div class="match-teamname">BETBOOM</div></div></a>
      <div class="match-fixtures-placeholder" data-match-id="2399415"></div>
    </div>
  </div>
  <span class="event-headline">Sunday - 2026-10-18</span>
  <div class="match">
    <div class="match-bottom">
      <a class="match-info" href="/matches/2399417/grand-final">
        <div class="match-time" data-unix="1792335600000">17:00</div>
        <div class="match-meta">bo5</div></a>
      <div class="match-fixtures-placeholder" data-match-id="2399417"></div>
      <div class="match-btn-wrapper"><div class="match-stage">Grand Final</div></div>
    </div>
  </div>
</div>
"""

MATCH_HTML = """
<div class="timeAndEvent"><div class="time">10:00</div><div class="date">17th of October 2026</div></div>
<div class="teamName">FURIA</div><div class="teamName">Aurora</div>
<div class="veto-box"><div class="padding">
  <div>1. FURIA removed Ancient</div>
  <div>2. Aurora removed Nuke</div>
  <div>Veto</div>
</div></div>
<div class="mapholder">
  <div class="played">
    <div class="map-name-holder"><div class="mapname">Inferno</div>
      <div class="map-pick">(picked by FURIA)</div></div>
    <div class="results-left won"><div class="results-team-score">13</div></div>
    <div class="results-right lost"><div class="results-team-score">9</div></div>
  </div>
</div>
"""

ANALYTICS_HTML = """
<div class="analyticsRow">FURIA is better ranked (#4)</div>
<div class="analyticsRow">Aurora is worse ranked (#6)</div>
<div class="analyticsRow">Aurora is the bookmaker favorite with the best odds</div>
<p>The overview of odds includes odds from bookmakers</p>
"""

TEAM_HTML = """
<div class="team-country-rank">#5 ( EU #5)</div>
<div class="table-container players-table">
<table><tr><th>Player</th><th>Status</th><th>Time on team</th><th>Maps played</th><th>Rating 3.0</th></tr>
<tr><td>Wicadia</td><td>STARTER</td><td>1 year 6 months</td><td>314</td><td>1.14</td></tr>
<tr><td>Jimpphat</td><td>STARTER</td><td>3 months</td><td>65</td><td>1.13</td></tr>
<tr><td>kyxsan</td><td>STARTER</td><td>3 months</td><td>65</td><td>0.98</td></tr>
<tr><td>MAJ3R</td><td>BENCHED</td><td>1 year 6 months</td><td>249</td><td>0.89</td></tr>
</table></div>
<div class="table-container coach-table">
<table><tr><th>Coach</th><th>Time on team</th><th>Maps coached</th><th>Winrate</th></tr>
<tr><td>ash</td><td>3 months</td><td>65</td><td>63%</td></tr></table></div>
<div class="table-container match-table">
<table><tr><th>Date</th><th>Matches</th></tr>
<tr><td>16/10/2026</td><td>Aurora 2 : 0 9z</td></tr>
<tr><td>14/10/2026</td><td>Aurora 0 : 2 9z</td></tr></table></div>
"""

# The match page's start time, as HLTV really marks it up: the rendered clock is local,
# data-unix is the absolute instant.
MATCH_TIME_HTML = """
<div class="timeAndEvent"><div class="time" data-time-format="HH:mm" data-unix="1792245600000">16:00</div>
<div class="date">17th of October 2026</div></div>
"""

class HltvVerifyParsers(unittest.TestCase):
    def test_results_rows_carry_id_teams_and_score(self):
        rows = hv.parse_results(RESULTS_HTML)
        self.assertEqual([r['match_id'] for r in rows], [2399412, 2399413])
        self.assertEqual(rows[0]['teams'], ['Aurora', '9z'])
        self.assertEqual(rows[0]['score'], '2 - 0')
        self.assertEqual(rows[0]['date_heading'], 'October 16th 2026')
        self.assertTrue(rows[0]['url'].startswith('https://www.hltv.org/matches/2399412/'))

    def test_schedule_rows_keep_the_displayed_clock_verbatim(self):
        rows = hv.parse_schedule(SCHEDULE_HTML)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]['displayed_time'], '10:00')
        self.assertEqual(rows[0]['teams'], ['FURIA', 'Aurora'])
        self.assertEqual(rows[2]['day_heading'], 'Sunday - 2026-10-18')
        # The clock is never converted: HLTV does not name the timezone it renders in.
        self.assertEqual([r['displayed_time'] for r in rows], ['10:00', '13:00', '07:30'])

    def test_flat_schedule_never_attributes_matches_to_the_wrong_day(self):
        rows = hv.parse_schedule(FLAT_SCHEDULE_HTML)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['day_heading'], 'Saturday - 2026-10-17')
        self.assertEqual(rows[0]['teams'], ['FURIA', 'Aurora'])
        self.assertEqual(rows[1]['day_heading'], 'Sunday - 2026-10-18')
        self.assertEqual(rows[1]['match_id'], 2399417)


    def test_real_schedule_shape_yields_absolute_utc_starts(self):
        rows = hv.parse_schedule(REAL_SCHEDULE_HTML)
        self.assertEqual([r['match_id'] for r in rows], [2399414, 2399415, 2399417])
        # The rendered clock is local and unnamed; data-unix is the absolute truth.
        self.assertEqual(rows[0]['displayed_time'], '16:00')
        self.assertEqual(rows[0]['start_utc'], '2026-10-17T14:00:00Z')
        self.assertEqual(rows[1]['start_utc'], '2026-10-17T17:00:00Z')
        self.assertEqual(rows[2]['day_heading'], 'Sunday - 2026-10-18')
        self.assertEqual(rows[2]['start_utc'], '2026-10-18T15:00:00Z')
        self.assertEqual(rows[2]['format'], 'bo5')
        self.assertEqual(rows[0]['stage'], 'Semifinal')
        self.assertEqual(rows[0]['teams'], ['FURIA', 'Aurora'])

    def test_rows_without_an_id_are_dropped_not_guessed(self):
        html = REAL_SCHEDULE_HTML.replace('data-match-id="2399415"', '').replace(
            '/matches/2399415/falcons-vs-betboom-x', '#').replace('/matches/2399415/x', '#')
        rows = hv.parse_schedule(html)
        self.assertEqual([r['match_id'] for r in rows], [2399414, 2399417])

    def test_unix_conversion_returns_none_on_garbage(self):
        self.assertIsNone(hv.unix_to_iso(None))
        self.assertIsNone(hv.unix_to_iso('not-a-number'))
        self.assertEqual(hv.unix_to_iso('1792245600000'), '2026-10-17T14:00:00Z')

    def test_match_page_maps_veto_and_time(self):
        page = hv.parse_match_page(MATCH_HTML)
        self.assertEqual(page['displayed_time'], '10:00')
        self.assertEqual(page['displayed_date'], '17th of October 2026')
        self.assertEqual(page['team_names'], ['FURIA', 'Aurora'])
        self.assertEqual(page['maps'][0]['map'], 'Inferno')
        self.assertEqual(page['maps'][0]['left'], {'team': None, 'score': '13', 'won': True})
        self.assertEqual(page['maps'][0]['right']['score'], '9')
        self.assertFalse(page['maps'][0]['right']['won'])
        self.assertEqual(page['veto'], ['1. FURIA removed Ancient', '2. Aurora removed Nuke'])

    def test_analytics_records_hltv_wording_and_ranks(self):
        page = hv.parse_analytics(ANALYTICS_HTML)
        self.assertTrue(page['states_bookmaker_favorite'])
        self.assertTrue(page['mentions_odds_from_bookmakers'])
        self.assertEqual(page['ranking_mentions'], ['4', '6'])
        self.assertTrue(any('bookmaker favorite' in line for line in page['bookmaker_favorite_lines']))

    def test_team_page_time_on_team_is_the_roster_change_evidence(self):
        page = hv.parse_team_page(TEAM_HTML)
        rows = {r[0]: r for r in page['roster_table'][1:]}
        self.assertEqual(rows['Jimpphat'][1], 'STARTER')
        self.assertEqual(rows['Jimpphat'][2], '3 months')
        self.assertEqual(rows['kyxsan'][2], '3 months')
        self.assertEqual(rows['Wicadia'][2], '1 year 6 months')
        self.assertEqual(page['coach_table'][1], ['ash', '3 months', '65', '63%'])
        self.assertEqual(page['world_rank_text'], '#5 ( EU #5)')
        self.assertIn(['16/10/2026', 'Aurora 2 : 0 9z'], page['recent_results_table'])

    def test_match_page_start_time_comes_from_the_absolute_epoch(self):
        page = hv.parse_match_page(MATCH_TIME_HTML)
        self.assertEqual(page['displayed_time'], '16:00')
        self.assertEqual(page['start_utc'], '2026-10-17T14:00:00Z')

    def test_missing_selectors_yield_none_not_invented_values(self):
        page = hv.parse_match_page('<html><body><div>empty</div></body></html>')
        self.assertIsNone(page['displayed_time'])
        self.assertEqual(page['team_names'], [])
        self.assertEqual(page['maps'], [])
        self.assertFalse(page['mentions_odds_from_bookmakers'])


class HltvVerifyFetch(unittest.TestCase):
    def test_http_error_is_recorded_as_a_receipt_not_raised(self):
        session = mock.Mock()
        response = mock.Mock(status_code=403, content=b'forbidden', url='https://www.hltv.org/x',
                             encoding='utf-8')
        session.get.return_value = response
        with mock.patch.object(hv.time, 'sleep', lambda *_: None):
            text, receipt = hv.fetch(session, 'https://www.hltv.org/x', attempts=2, pause=0)
        self.assertIsNone(text)
        self.assertEqual(receipt['status'], 403)
        self.assertIsNotNone(receipt['error'])
        self.assertEqual(receipt['bytes'], len(b'forbidden'))
        self.assertEqual(receipt['attempts'], 2)

    def test_ok_response_is_returned_with_hash_and_size(self):
        session = mock.Mock()
        response = mock.Mock(status_code=200, content=b'<html>ok</html>', url='https://www.hltv.org/y',
                             encoding='utf-8')
        session.get.return_value = response
        text, receipt = hv.fetch(session, 'https://www.hltv.org/y', attempts=1)
        self.assertEqual(text, '<html>ok</html>')
        self.assertEqual(receipt['status'], 200)
        self.assertEqual(receipt['bytes'], len(b'<html>ok</html>'))
        self.assertEqual(len(receipt['sha256']), 64)
        self.assertIsNone(receipt['error'])


if __name__ == '__main__':
    unittest.main()
