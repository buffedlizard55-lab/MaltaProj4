"""Rate-limit resilience for `scripts.refresh.Sources` (session 498cc7dd).

Why these tests exist
---------------------
On the 2026-10-16T23:53:53Z harvest (run 38983767301,
``research/harvest-498cc7dd/probe-report.json``) ``https://www.hltv.org/matches``
answered HTTP 403 while every other source in the same run answered 200, and the
same HLTV read at 19:57Z that evening had answered 200
(``research/harvest-621776e4/hltv-unpriced-*.json``). One 403 blocked the host for
the rest of the run, so eight open fixtures lost the HLTV lineups that
disambiguate repeated Valve standings labels *and* the ranking-order fallback:
``unresolved_without_any_pick`` went from 0 to 8.

These tests pin the corrected behaviour: a rate-limited response is waited out on
the same URL with the same headers, every wait is recorded as evidence, and a
source that keeps refusing is still blocked.
"""
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from scripts import refresh
from scripts.refresh import Sources, RATE_LIMIT_BACKOFF


class FakeResponse:
    def __init__(self, status=200, body=b'<html>ok</html>', headers=None, json_body=None):
        self.status_code = status
        self.content = body
        self.headers = dict(headers or {})
        self._json = json_body
        self.text = body.decode('utf-8', 'replace')

    def json(self):
        if self._json is None:
            raise ValueError('not json')
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            error = requests.exceptions.HTTPError('%d Client Error' % self.status_code)
            error.response = self
            raise error


class ScriptedSession:
    """Replays a fixed list of responses, recording each request URL and headers."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.request_headers = []
        self.headers = {}

    def get(self, url, timeout=None, headers=None):
        self.calls.append(url)
        self.request_headers.append(headers)
        if not self.responses:
            raise AssertionError('more requests than scripted responses')
        return self.responses.pop(0)


def make_source(responses):
    src = Sources(datetime(2026, 10, 16, 23, 53, tzinfo=timezone.utc))
    src.session = ScriptedSession(responses)
    src.rate_limit_backoff = (0.0, 0.0, 0.0)  # keep the test fast; the shape is what matters
    return src


class RateLimitRetryTests(unittest.TestCase):
    url = 'https://www.hltv.org/matches'

    def test_a_single_rate_limit_is_waited_out_and_the_read_succeeds(self):
        src = make_source([FakeResponse(403), FakeResponse(200)])
        body, record = src.get('HLTV fallback discovery', self.url, False)
        self.assertEqual(body, '<html>ok</html>')
        self.assertEqual(record['status'], 'ok')
        self.assertEqual(record['http_status'], 200)
        self.assertEqual(src.blocked_hosts, {}, 'a waited-out limit must not block the host')
        self.assertEqual(len(record['rate_limit_waits']), 1)
        self.assertEqual(record['rate_limit_waits'][0]['http_status'], 403)
        self.assertEqual(len(src.session.calls), 2)
        self.assertEqual(src.session.calls[0], src.session.calls[1],
                         'the retry must use the identical URL: nothing is rewritten to slip past')

    def test_the_request_is_re_asked_unchanged_after_a_rate_limit(self):
        src = make_source([FakeResponse(403), FakeResponse(200)])
        src.get('HLTV fallback discovery', self.url, False)
        self.assertEqual(src.session.request_headers[0], src.session.request_headers[1],
                         'the retry must send identical headers: no spoofing to evade the limit')
        real = Sources(datetime(2026, 10, 16, 23, 53, tzinfo=timezone.utc))
        self.assertEqual(real.session.headers['User-Agent'],
                         'Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)')

    def test_retry_after_header_is_honoured(self):
        src = make_source([FakeResponse(429, headers={'Retry-After': '7'}), FakeResponse(200)])
        with patch('scripts.refresh.time.sleep') as slept:
            _, record = src.get('HLTV fallback discovery', self.url, False)
        self.assertEqual(record['rate_limit_waits'][0]['retry_after_header'], 7.0)
        self.assertEqual(record['rate_limit_waits'][0]['waited_seconds'], 7.0)
        slept.assert_called_once_with(7.0)

    def test_retry_after_above_the_cap_is_clamped(self):
        src = make_source([FakeResponse(429, headers={'Retry-After': '9999'}), FakeResponse(200)])
        with patch('scripts.refresh.time.sleep') as slept:
            _, record = src.get('HLTV fallback discovery', self.url, False)
        self.assertEqual(record['rate_limit_waits'][0]['waited_seconds'], refresh.RATE_LIMIT_BACKOFF_CAP)
        slept.assert_called_once_with(refresh.RATE_LIMIT_BACKOFF_CAP)

    def test_a_non_numeric_retry_after_falls_back_to_the_published_backoff(self):
        src = make_source([FakeResponse(429, headers={'Retry-After': 'Wed, 21 Oct 2026 07:28:00 GMT'}),
                           FakeResponse(200)])
        with patch('scripts.refresh.time.sleep'):
            _, record = src.get('HLTV fallback discovery', self.url, False)
        self.assertIsNone(record['rate_limit_waits'][0]['retry_after_header'])
        self.assertEqual(record['rate_limit_waits'][0]['waited_seconds'], 0.0)

    def test_a_persistent_rate_limit_still_blocks_the_host_and_logs_every_wait(self):
        src = make_source([FakeResponse(403)] * (len(RATE_LIMIT_BACKOFF) + 1))
        with self.assertRaises(ValueError) as ctx:
            src.get('HLTV fallback discovery', self.url, False)
        self.assertIn('host blocked for this run', str(ctx.exception))
        self.assertEqual(src.blocked_hosts.get('www.hltv.org'), '403')
        record = src.log[0]
        self.assertEqual(record['status'], 'error')
        self.assertEqual(len(record['rate_limit_waits']), len(RATE_LIMIT_BACKOFF))

    def test_a_blocked_host_is_not_hammered_on_the_next_read(self):
        src = make_source([FakeResponse(403)] * (len(RATE_LIMIT_BACKOFF) + 1))
        with self.assertRaises(ValueError):
            src.get('HLTV fallback discovery', self.url, False)
        calls_after_block = len(src.session.calls)
        with self.assertRaises(ValueError) as ctx:
            src.get('HLTV match 1', self.url, False)
        self.assertIn('Skipped after earlier access/rate restriction', str(ctx.exception))
        self.assertEqual(len(src.session.calls), calls_after_block, 'a blocked host must not be re-requested')

    def test_a_401_is_not_treated_as_a_rate_limit(self):
        src = make_source([FakeResponse(401)])
        with self.assertRaises(ValueError):
            src.get('private endpoint', 'https://example.org/private', True)
        self.assertEqual(src.blocked_hosts.get('example.org'), '401')
        self.assertNotIn('rate_limit_waits', src.log[0])
        self.assertEqual(len(src.session.calls), 1, 'an auth refusal must not be retried')

    def test_a_404_is_not_treated_as_a_rate_limit(self):
        src = make_source([FakeResponse(404)])
        with self.assertRaises(ValueError):
            src.get('missing', 'https://example.org/missing', True)
        self.assertNotIn('rate_limit_waits', src.log[0])
        self.assertEqual(len(src.session.calls), 1)

    def test_a_region_or_challenge_page_is_not_retried_as_a_rate_limit(self):
        src = make_source([FakeResponse(200, body=b'<html>Just a moment...</html>'),
                           FakeResponse(200, body=b'<html>Just a moment...</html>')])
        with patch('scripts.refresh.time.sleep'):
            with self.assertRaises(ValueError) as ctx:
                src.get('HLTV fallback discovery', self.url, False)
        self.assertIn('Access restriction or challenge page', str(ctx.exception))
        self.assertNotIn('rate_limit_waits', src.log[0])

    def test_a_transient_connection_error_still_gets_one_retry(self):
        import requests

        class FlakySession(ScriptedSession):
            def get(self, url, timeout=None, headers=None):
                self.calls.append(url)
                if len(self.calls) == 1:
                    raise requests.exceptions.ConnectionError('reset by peer')
                return self.responses.pop(0)

        src = Sources(datetime(2026, 10, 16, 23, 53, tzinfo=timezone.utc))
        src.session = FlakySession([FakeResponse(200)])
        src.rate_limit_backoff = (0.0,)
        with patch('scripts.refresh.time.sleep'):
            body, record = src.get('HLTV fallback discovery', self.url, False)
        self.assertEqual(record['status'], 'ok')
        self.assertEqual(body, '<html>ok</html>')
        self.assertEqual(len(src.session.calls), 2)


class HltvResearchRecoversTests(unittest.TestCase):
    """End-to-end: the fallback that produced picks again after the fix."""

    HLTV_LIST = """
    <html><body>
      <div class="match">
        <span class="match-time" data-unix="1792331100000"></span>
        <a class="match-teams" href="/matches/2399681/ex-6666-vs-privateer-cct-2026-challengers-europe-series-8">
          <span class="match-teamname">ex-6666</span><span class="match-teamname">Privateer</span>
        </a>
      </div>
    </body></html>"""

    # The structural minimum scripts.hltv.context() reads from a match page. The
    # identities and the clock are the real values recorded for this fixture at
    # 2026-10-16T19:57:11Z in research/harvest-621776e4/hltv-unpriced-1081521.json.
    HLTV_MATCH = """
    <html><body>
      <div class="timeAndEvent"><div class="time" data-unix="1792331100000"></div></div>
      <div class="team1-gradient"><div class="teamName">ex-6666</div></div>
      <div class="team2-gradient"><div class="teamName">Privateer</div></div>
      <div class="lineups">
        <div class="lineup">
          <div class="box-headline"><a href="/team/14100/ex-6666">ex-6666</a></div>
          <table><tbody><tr><td class="player"><span class="player-compare"><span class="text-ellipsis">skcH</span></span></td></tr>
          <tr><td class="player"><span class="player-compare"><span class="text-ellipsis">kL1o</span></span></td></tr></tbody></table>
        </div>
        <div class="lineup">
          <div class="box-headline"><a href="/team/13914/privateer">Privateer</a></div>
          <table><tbody><tr><td class="player"><span class="player-compare"><span class="text-ellipsis">Frazehh</span></span></td></tr></tbody></table>
        </div>
      </div>
    </body></html>"""

    def test_a_rate_limited_discovery_read_still_yields_hltv_context(self):
        from scripts import hltv
        src = make_source([FakeResponse(403), FakeResponse(200, body=self.HLTV_LIST.encode()),
                           FakeResponse(200, body=self.HLTV_MATCH.encode())])
        fixture = {'id': '1081521', 'teams': ['ex-6666', 'Privateer'],
                   'start': '2026-10-18T13:45:00Z', 'attempts': [], 'flags': []}
        hltv.research([fixture], src)
        self.assertEqual(src.blocked_hosts, {})
        self.assertTrue(fixture.get('hltv_context'),
                        'HLTV context must survive a rate-limited first read')
        self.assertEqual(fixture['hltv_context']['teams'], ['ex-6666', 'Privateer'])
        self.assertEqual(fixture['hltv_context']['start'], '2026-10-18T13:45:00Z')
        lineups = {x['team']: x['players'] for x in fixture['hltv_context']['lineups']}
        self.assertEqual(lineups['ex-6666'], ['skcH', 'kL1o'],
                         'the lineups that disambiguate repeated Valve labels must be captured')

    def test_a_persistently_rate_limited_hltv_fails_closed_with_evidence(self):
        from scripts import hltv
        src = make_source([FakeResponse(403)] * (len(RATE_LIMIT_BACKOFF) + 1))
        fixture = {'id': '1081521', 'teams': ['ex-6666', 'Privateer'],
                   'start': '2026-10-18T13:45:00Z', 'attempts': [], 'flags': []}
        hltv.research([fixture], src)
        self.assertIsNone(fixture.get('hltv_context'), 'nothing may be invented when HLTV stays closed')
        self.assertEqual(fixture['attempts'][0]['provider'], 'HLTV')
        self.assertEqual(fixture['attempts'][0]['status'], 'error')
        self.assertIn('host blocked for this run', fixture['attempts'][0]['reason'])


if __name__ == '__main__':
    unittest.main()
