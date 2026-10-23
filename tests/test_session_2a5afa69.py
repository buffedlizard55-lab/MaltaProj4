"""Session 2a5afa69 — row-by-row board audit, no network, no invented values.

These tests pin the two things the auditor is allowed to say about a row:

* a published percentage must be reproducible from that row's own retained
  evidence (exchange price pair, bookmaker decimal odds, or Valve points
  through Valve's published formula), otherwise the row fails the audit;
* a row without a pick must be published by name together with every source
  that was tried, and the auditor must never fill the blank in.

They also prove the audit is read-only: the snapshot passed in is unchanged.
"""
import copy
import json
import pathlib
import unittest
from datetime import datetime, timedelta, timezone

from scripts import audit_board_2a5afa69 as audit_mod
from scripts import vrs
from scripts.audit_board_2a5afa69 import audit, markdown, reproduce

NOW = datetime(2026, 10, 23, 5, 0, tzinfo=timezone.utc)
OBSERVED = '2026-10-23T04:55:00Z'


def exchange_row(probs=(0.6, 0.4), mid='900001', pick='Alpha', **over):
    row = {
        'id': mid, 'teams': ['Alpha', 'Bravo'], 'start': '2026-10-23T12:00:00Z',
        'competition': 'CCT Europe 2026 Series #1', 'tier': 'b', 'state': 'open',
        'source_url': 'https://www.hotspawn.com/matches/alpha-vs-bravo-900001',
        'pick': pick, 'method': 'exchange', 'probabilities': list(probs),
        'evidence': [{'provider': 'Polymarket', 'url': 'https://polymarket.com/event/x',
                      'api_url': 'https://gamma-api.polymarket.com/markets/1',
                      'observed_at': OBSERVED, 'updated_at': OBSERVED,
                      'probabilities': [0.6, 0.4], 'spread': 0.02, 'liquidity': 5000.0}],
        'attempts': [{'provider': 'Polymarket', 'status': 'resolved', 'url': 'https://gamma-api.polymarket.com/markets/1',
                      'reason': 'Exact pair and UTC start; two-way series winner validated.'}],
        'reason': None, 'expires_at': '2026-10-23T11:54:00Z',
    }
    row.update(over)
    return row


def model_row(mid='900002'):
    points = [1500.0, 1200.0]
    p0 = vrs.calibrated(vrs.expected(points[0], points[1]))
    return {
        'id': mid, 'teams': ['Charlie', 'Delta'], 'start': '2026-10-24T12:00:00Z',
        'competition': 'DACH CS Masters Season 5', 'tier': 'c', 'state': 'open',
        'source_url': 'https://www.hotspawn.com/matches/charlie-vs-delta-900002',
        'pick': 'Charlie', 'method': 'model_vrs', 'probabilities': [p0, 1 - p0],
        'evidence': [{'provider': 'Valve VRS model', 'url': 'https://github.com/ValveSoftware/x',
                      'api_url': 'https://raw.githubusercontent.com/ValveSoftware/x',
                      'observed_at': OBSERVED, 'points': points, 'probabilities': [p0, 1 - p0]}],
        'attempts': [], 'reason': None, 'expires_at': '2026-10-24T11:54:00Z',
    }


def open_snapshot(rows):
    return {'generated_at': '2026-10-23T04:56:00Z', 'fixtures_observed_at': OBSERVED,
            'built_at': '2026-10-23T04:57:00Z', 'matches': rows}


class ReproductionRules(unittest.TestCase):
    def test_exchange_row_reproduces_and_tampered_pair_does_not(self):
        ok, why = reproduce(exchange_row(), NOW)
        self.assertTrue(ok, why)
        bad, why = reproduce(exchange_row(probs=(0.7, 0.3)), NOW)
        self.assertFalse(bad)
        self.assertIn('normalised exchange price', why)

    def test_exchange_row_without_spread_or_liquidity_record_fails(self):
        row = exchange_row()
        row['evidence'][0].pop('spread')
        ok, why = reproduce(row, NOW)
        self.assertFalse(ok)
        self.assertIn('spread or liquidity', why)

    def test_bookmaker_decimal_odds_are_de_vigged(self):
        row = exchange_row(probs=(0.5, 0.5), mid='900003')
        row['method'] = 'bookmaker_fallback'
        row['evidence'][0] = {'provider': 'Winline', 'url': 'https://stavka.tv/x',
                              'observed_at': OBSERVED, 'decimal_odds': [1.90, 1.90]}
        ok, why = reproduce(row, NOW)
        self.assertTrue(ok, why)
        row['probabilities'] = [0.6, 0.4]
        self.assertFalse(reproduce(row, NOW)[0])

    def test_model_row_is_recomputed_from_valve_points(self):
        row = model_row()
        ok, why = reproduce(row, NOW)
        self.assertTrue(ok, why)
        self.assertIn('Valve points', why)
        row['probabilities'] = [0.9, 0.1]
        self.assertFalse(reproduce(row, NOW)[0])

    def test_stale_evidence_and_research_percentages_fail(self):
        row = exchange_row()
        row['evidence'][0]['observed_at'] = '2026-10-23T01:00:00Z'  # 4h old at NOW? still inside 8h
        self.assertTrue(reproduce(row, NOW)[0])
        row['evidence'][0]['observed_at'] = '2026-10-22T18:00:00Z'  # 11h old
        self.assertFalse(reproduce(row, NOW)[0])
        research = exchange_row(mid='900004', method='research_rank_single')
        self.assertFalse(reproduce(research, NOW)[0])
        self.assertIn('research tier', reproduce(research, NOW)[1])

    def test_pick_must_name_a_fixture_team(self):
        report = audit(open_snapshot([exchange_row(pick='Echo')]), NOW)
        self.assertFalse(report['rows'][0]['pick_is_a_team'])


class UnpickedRowsArePublishedNotFilledIn(unittest.TestCase):
    def row_without_pick(self):
        return {
            'id': '900005', 'teams': ['Echo', 'Foxtrot'], 'start': '2026-10-25T09:00:00Z',
            'competition': 'Thunderpick World Championship 2026: South American Series #1',
            'tier': 'c', 'state': 'open', 'pick': None, 'method': None, 'probabilities': None,
            'source_url': 'https://www.hotspawn.com/matches/echo-vs-foxtrot-900005',
            'attempts': [
                {'provider': 'HLTV', 'status': 'unresolved', 'url': 'https://www.hltv.org/matches',
                 'reason': 'No unique exact team-pair and UTC-start match; renamed teams are not inferred.'},
                {'provider': 'Pinnacle', 'status': 'unresolved',
                 'url': 'https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight',
                 'reason': 'No exact team-pair and UTC-start match in retrieved feed.'},
                {'provider': 'EGamersWorld', 'status': 'error', 'url': 'https://egamersworld.com/counterstrike/match/x',
                 'reason': 'HTTP 403 persisted; host blocked for this run.'},
            ],
            'reason': 'No verified market line and no usable HLTV ranking evidence.',
            'expires_at': None,
        }

    def test_audit_keeps_the_row_blank_and_lists_every_attempt(self):
        snapshot = open_snapshot([exchange_row(), self.row_without_pick()])
        report = audit(snapshot, NOW)
        self.assertEqual(report['rows_without_pick'], ['900005'])
        self.assertEqual(report['rows_with_pick'], 1)
        out = markdown(report)
        self.assertIn('900005 — Echo vs Foxtrot', out)
        for provider in ('HLTV', 'Pinnacle', 'EGamersWorld'):
            self.assertIn(provider, out)
        self.assertIn('HTTP 403', out)
        # The blank row is not given a percentage or a pick anywhere.
        row = next(r for r in report['rows'] if r['id'] == '900005')
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['pick'])

    def test_every_open_row_appears_and_closed_rows_are_skipped(self):
        closed = exchange_row(mid='900006', state='not_open')
        report = audit(open_snapshot([exchange_row(), self.row_without_pick(), closed]), NOW)
        self.assertEqual([r['id'] for r in report['rows']], ['900001', '900005'])
        self.assertEqual(report['rows_open'], 2)

    def test_audit_is_read_only(self):
        snapshot = open_snapshot([exchange_row(), self.row_without_pick()])
        before = copy.deepcopy(snapshot)
        audit(snapshot, NOW)
        self.assertEqual(snapshot, before)


class RealCommittedBoard(unittest.TestCase):
    """The committed board must pass the same row-by-row auditor."""

    def test_committed_snapshot_reproduces_or_reports_the_gap(self):
        data = json.loads(pathlib.Path('data/latest.json').read_text())
        report = audit(data)
        opens = [m for m in data['matches'] if m['state'] == 'open']
        self.assertEqual(report['rows_open'], len(opens))
        self.assertEqual(report['rows_failing_reproduction'], [])
        # A pick, when present, always names a fixture team.
        self.assertTrue(all(r['pick_is_a_team'] for r in report['rows'] if r['pick']))
        # Every open row is either priced or explicitly research-only/unresolved.
        for r in report['rows']:
            if r['probabilities'] is not None:
                self.assertIn(r['method'], audit_mod.MARKET + audit_mod.MODEL, r['id'])
            elif r['pick']:
                self.assertTrue(str(r['method']).startswith('research_'), r['id'])
            else:
                self.assertTrue(r['attempts'], r['id'])


if __name__ == '__main__':
    unittest.main()
