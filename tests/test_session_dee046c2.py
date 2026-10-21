"""Offline tests for scripts.probe_dee046c2 (session dee046c2).

No network: every source read is stubbed. The tests pin the probe's contracts:
an inventory row must be exact (teams, start, status, no end time) to count as
still listed; an exchange replay compares the market's current normalised price
with the published value without changing anything; a refusal is recorded as a
refusal, never as a number; and the model replay uses the repo's vendored
official standings copy when the live GitHub read is unavailable.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import core  # noqa: E402
from scripts import probe_dee046c2 as probe  # noqa: E402

NOW = '2026-10-21T20:30:00Z'


def snapshot():
    return {'generated_at': NOW, 'fixtures_observed_at': NOW, 'coverage': 'verified',
            'matches': [
                {'id': '1', 'teams': ['Alpha', 'Beta'], 'start': '2026-10-22T14:00:00Z',
                 'lock': '2026-10-22T13:54:00Z', 'state': 'open', 'method': 'exchange',
                 'probabilities': [0.775, 0.225],
                 'evidence': [{'provider': 'Polymarket', 'id': '999',
                               'url': 'https://polymarket.com/event/cs2-a-b-2026-10-22',
                               'api_url': 'https://gamma-api.polymarket.com/markets/999',
                               'observed_at': '2026-10-21T19:30:00Z',
                               'updated_at': '2026-10-21T19:29:00Z',
                               'source_teams': ['Alpha', 'Beta'],
                               'start': '2026-10-22T14:00:00Z'}],
                 'attempts': []},
                {'id': '2', 'teams': ['Gamma', 'Delta'], 'start': '2026-10-22T11:00:00Z',
                 'lock': '2026-10-22T10:54:00Z', 'state': 'open', 'method': None,
                 'probabilities': None, 'evidence': [],
                 'attempts': [{'provider': 'Polymarket', 'status': 'unresolved',
                               'reason': 'no candidate', 'url': core.GAMMA + '/sports'}]},
                {'id': '3', 'teams': ['Eps', 'Zed'], 'start': '2026-10-23T03:00:00Z',
                 'lock': '2026-10-23T02:54:00Z', 'state': 'open', 'method': 'model_vrs',
                 'probabilities': [0.6, 0.4], 'evidence': [], 'attempts': []}]}


API_ROWS = [
    {'id': 1, 'sport_alias': 'cs2', 'participants0_name': 'Alpha', 'participants1_name': 'Beta',
     'scheduled_start_time': '2026-10-22T14:00:00Z', 'status': 'scheduled',
     'competition_name': 'Cup', 'tier': 'c'},
    # id 2 is gone from the feed and id 3 moved to a later start: one proves
    # "still listed = False", the other proves a start change is not ignored.
    {'id': 3, 'sport_alias': 'cs2', 'participants0_name': 'Eps', 'participants1_name': 'Zed',
     'scheduled_start_time': '2026-10-23T04:00:00Z', 'status': 'scheduled',
     'competition_name': 'Cup', 'tier': 'c'},
    {'id': 4, 'sport_alias': 'dota2', 'participants0_name': 'X', 'participants1_name': 'Y',
     'scheduled_start_time': '2026-10-22T14:00:00Z', 'status': 'scheduled'},
]

GAMMA_MARKET = {'question': 'Counter-Strike: Alpha vs Beta (BO3) - Tournament',
                'outcomes': '["Alpha", "Beta"]', 'outcomePrices': '["0.78", "0.22"]',
                'bestBid': 0.77, 'bestAsk': 0.79, 'active': True, 'closed': False,
                'acceptingOrders': True, 'liquidity': '12345.0', 'volume': '98765.0',
                'startDate': '2026-10-22T14:00:00Z', 'endDate': '2026-10-22T18:00:00Z'}


class StubSources:
    def __init__(self, now=None):
        self.log = []
        self.blocked_hosts = {}

    def get(self, name, url, as_json=True, headers=None):
        rec = {'name': name, 'url': url, 'observed_at': NOW, 'checked_at': NOW}
        if url.startswith(core.FIXTURES):
            return {'data': API_ROWS}, rec
        if url.endswith('polymarket.com/markets/999') or url.endswith('/markets/999'):
            return GAMMA_MARKET, rec
        if 'arcadia.pinnacle.com' in url:
            return [], rec
        if url.endswith('hltv.org/matches'):
            return '<html>nothing usable</html>', rec
        if url.startswith('https://api.github.com'):
            raise ValueError('simulated GitHub refusal (vendored copy expected)')
        if any(h in url for h in ('play.hotspawn.com', 'egamersworld.com', 'bo3.gg',
                                  'thunderpick.io', 'gg.bet')):
            return '<html>stub</html>', rec
        raise ValueError('unexpected url ' + url)


class ProbeOfflineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raw = probe.Raw(Path(self.tmp.name))
        self.snap = snapshot()

    def test_inventory_exactness(self):
        out = probe.probe_inventory(StubSources(), self.snap, self.raw)
        rows = out['open_rows']
        self.assertTrue(rows['1']['exact_match_start_status'])
        self.assertFalse(rows['2']['still_listed'])
        self.assertFalse(rows['3']['exact_match_start_status'], 'a moved start must not be treated as identical')
        self.assertEqual(out['api']['count_cs2'], 2, 'the dota2 row must be excluded, both cs2 rows counted')

    def test_exchange_replay_dated_delta(self):
        findings = []
        out = probe.probe_exchange(StubSources(), self.snap, self.raw, findings)
        self.assertEqual(len(out), 1)
        entry = out[0]
        self.assertAlmostEqual(entry['first_team_prob_replay'], 0.78)
        self.assertAlmostEqual(entry['delta_first_team_vs_published'], 0.005, places=6)
        self.assertEqual(entry['spread_points'], 2.0)
        self.assertEqual(findings, [], 'a 0.5-point move is a dated quote, not an error')

    def test_pinnacle_and_hltv_refusals_recorded_not_zeroed(self):
        findings = []
        pin = probe.probe_pinnacle(StubSources(), self.snap, self.raw, findings)
        self.assertEqual(pin['status'], 'ok')
        self.assertEqual(pin['per_open_fixture']['2']['exact_candidates'], 0)
        hltv_out = probe.probe_hltv(StubSources(), self.snap, self.raw, findings)
        self.assertEqual(hltv_out['listing']['status'], 'refused')
        self.assertNotIn('1', hltv_out)

    def test_gap_books_access_checks_and_no_invented_lines(self):
        findings = []
        out = probe.probe_gap_books(StubSources(), self.snap, self.raw, findings)
        self.assertIn('2', out)
        self.assertNotIn('egw', out['2'], 'no listing URL is invented for a fixture without one')
        self.assertEqual(out['access_checks']['GG.BET']['status'], 'reachable')
        self.assertEqual(out['access_checks']['Thunderpick']['status'], 'reachable')

    def test_vrs_replay_uses_vendored_when_live_refused(self):
        findings = []
        out = probe.probe_vrs(StubSources(), self.snap, self.raw, None, findings)
        self.assertTrue(out['fetch']['problem'] and 'vendored' in out['fetch']['problem'])
        self.assertEqual(out['fetch']['as_of'], '2026-10-05')
        for mid in ('1', '2', '3'):
            self.assertTrue(out[mid]['model_refuses'], 'unknown teams must refuse, never default')

    def test_main_writes_serialisable_probe_json(self):
        snap_path = Path(self.tmp.name) / 'latest.json'
        snap_path.write_text(json.dumps(self.snap))
        argv = ['probe', '--snapshot', str(snap_path), '--out', self.tmp.name + '/out']
        with mock.patch.object(probe, 'Sources', StubSources), \
                mock.patch.object(sys, 'argv', argv), \
                contextlib_stdout() as sink:
            probe.main()
        doc = json.loads((Path(self.tmp.name) / 'out' / 'probe.json').read_text())
        self.assertEqual(doc['session'], 'dee046c2')
        self.assertIn('inventory', doc)
        self.assertIsInstance(doc['findings'], list)
        self.assertIn('"findings"', sink[0].getvalue())


def contextlib_stdout():
    import contextlib, io
    class _Ctx:
        def __init__(self):
            self.buf = io.StringIO()
        def __enter__(self):
            self.redir = contextlib.redirect_stdout(self.buf)
            self.redir.__enter__()
            return [self.buf]
        def __exit__(self, *a):
            self.redir.__exit__(*a)
            return False
    return _Ctx()


if __name__ == '__main__':
    unittest.main()
