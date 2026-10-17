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
<div class="bodyshot-team">
  <div class="player-holder"><div class="text-ellipsis">XANTARES</div></div>
  <div class="player-holder"><div class="text-ellipsis">kyxsan</div><div class="player-role">IGL</div></div>
</div>
<table class="transfer-table">
  <tr><td>08-07-2026</td><td>kyxsan</td><td>Falcons</td><td>Aurora</td></tr>
</table>
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

    def test_team_page_roster_and_transfers(self):
        page = hv.parse_team_page(TEAM_HTML)
        self.assertEqual([r['player'] for r in page['roster']], ['XANTARES', 'kyxsan'])
        self.assertEqual(page['roster'][1]['role'], 'IGL')
        self.assertIn(['08-07-2026', 'kyxsan', 'Falcons', 'Aurora'], page['transfers'])

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
