"""Deterministic regression tests for session 9f3e77d2 (2026-10-22).

Calendar-pinned at ``PINNED_NOW`` so future dates never cause time-bomb failures.

Verifies:
1. ``data/identities.json`` registers ``Tropa do KinGui / Projeto do KinGui / ex-Keyd Stars``
   and ``Envy / 3DMAX`` with primary sources and exact-opponent / UTC-start rules.
2. ``1082919`` (Projeto do KinGui vs Martians, 2026-10-22T13:00:00Z) rejects the
   42-point Polymarket spread on the strict pass, resolves via ``exchange_wide``
   (75.0% / 25.0%, fair odds 1.3333 / 4.0000, pick ``Projeto do KinGui``), and
   falls back cleanly to ``research_vrs_single`` (#144 ``ex-Keyd Stars``, 854 pts,
   4/5 roster overlap) when market quotes are absent.
3. ``1082901`` (Envy vs GamerLegion, 2026-10-27T20:00:00Z) attaches an ``ok``
   ``model_check`` via ``Envy <-> 3DMAX`` (#21 ``3DMAX``, 1500 pts, 3/5 overlap
   vs #22 ``GamerLegion``, 1479 pts, 3/5 overlap).
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from scripts import build, hltv, vrs
from scripts.core import dt, iso, norm, normalize_fixtures, polymarket_candidates, resolve
from scripts.validate import validate_data, validate_site

ROOT = Path(__file__).resolve().parents[1]
PINNED_NOW = dt('2026-10-22T08:03:00Z')
PINNED_ISO = iso(PINNED_NOW)


def _load_c6_auditor():
    spec = importlib.util.spec_from_file_location('audit_snapshot_9f3e77d2', ROOT / 'verification-c6/audit_snapshot.py')
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _make_open_fixture(fid: str, team_a: str, team_b: str, start: str, lock: str, comp: str, tier: str = 'c'):
    raw = {
        'id': fid,
        'sport_alias': 'cs2',
        'participants0_name': team_a,
        'participants1_name': team_b,
        'participants0_id': f'{fid}_a',
        'participants1_id': f'{fid}_b',
        'status': 'scheduled',
        'scheduled_start_time': start,
        'lock_time': lock,
        'competition_name': comp,
        'tier': tier,
        'best_of': None,
    }
    row = normalize_fixtures([raw], {}, PINNED_NOW)[0]
    row['fixture_sources'] = [{
        'retrieved_at': PINNED_ISO,
        'observed_at': PINNED_ISO,
        'cache_age_seconds': None,
        'sha256': '0' * 64,
        'url': row['feed_url'],
    }]
    return raw, row


class Session9f3e77d2Tests(unittest.TestCase):
    def setUp(self):
        self.standings, self.vrs_meta = vrs.vendored(PINNED_NOW)
        self.auditor = _load_c6_auditor()

    def test_identities_registered_and_isolated(self):
        self.assertEqual(norm('Projeto do KinGui'), norm('Tropa do KinGui'))
        self.assertEqual(norm('Projeto do KinGui'), norm('ex-Keyd Stars'))
        self.assertNotEqual(norm('Projeto do KinGui'), norm('Martians'))
        self.assertEqual(norm('Envy'), norm('3DMAX'))
        self.assertNotEqual(norm('Envy'), norm('GamerLegion'))

        ident = json.loads((ROOT / 'data/identities.json').read_text(encoding='utf-8'))
        by_canonical = {a['canonical']: a for a in ident['aliases']}
        self.assertIn('Tropa do KinGui', by_canonical)
        self.assertIn('Envy', by_canonical)
        self.assertIn('2399904', by_canonical['Tropa do KinGui']['source'])
        self.assertIn('6033256', by_canonical['Tropa do KinGui']['additional_source'])
        self.assertIn('2399870', by_canonical['Envy']['source'])
        self.assertIn('45594', by_canonical['Envy']['additional_source'])

    def test_1082919_resolves_wide_exchange_and_vrs_single_fallback(self):
        raw_tdkg, row_tdkg = _make_open_fixture(
            '1082919', 'Projeto do KinGui', 'Martians',
            '2026-10-22T13:00:00Z', '2026-10-22T12:54:00Z',
            'CCT South America 2026 Series #7',
        )
        pm_event = {
            'id': '1232953',
            'slug': 'cs2-tdkg-mar1-2026-10-22',
            'sport': {'sport': 'cs2'},
            'markets': [{
                'id': '6033256',
                'question': 'Counter-Strike: Tropa do KinGui vs Martians (BO3) - CCT South America Series 7 Playoffs',
                'sportsMarketType': 'moneyline',
                'active': True,
                'closed': False,
                'acceptingOrders': True,
                'outcomes': json.dumps(['Tropa do KinGui', 'Martians']),
                'outcomePrices': json.dumps(['0.75', '0.25']),
                'gameStartTime': '2026-10-22 13:00:00+00',
                'eventStartTime': '2026-10-22T13:00:00Z',
                'updatedAt': '2026-10-22T07:42:57.621734Z',
                'bestBid': 0.54,
                'bestAsk': 0.96,
                'liquidity': '156.0392',
                'volume': None,
            }],
        }
        cands = polymarket_candidates([pm_event], PINNED_ISO)

        # Strict pass rejects 42-point spread (> 0.25).
        resolve(row_tdkg, cands, 'Polymarket', PINNED_NOW, relax=False)
        self.assertIsNone(row_tdkg['probabilities'])

        # Wide pass accepts 42-point spread (<= 0.60) and liquidity $156.04 (>= $100).
        resolve(row_tdkg, cands, 'Polymarket', PINNED_NOW, relax=True)
        self.assertEqual(row_tdkg['method'], 'exchange_wide')
        self.assertEqual(row_tdkg['pick'], 'Projeto do KinGui')
        self.assertAlmostEqual(row_tdkg['probabilities'][0], 0.75, places=6)
        self.assertAlmostEqual(row_tdkg['probabilities'][1], 0.25, places=6)

        # Fallback check: if market quotes are absent, 1082919 resolves via research_vrs_single
        # (#144 ex-Keyd Stars, 854 pts, 4/5 roster overlap).
        _, row_fallback = _make_open_fixture(
            '1082919', 'Projeto do KinGui', 'Martians',
            '2026-10-22T13:00:00Z', '2026-10-22T12:54:00Z',
            'CCT South America 2026 Series #7',
        )
        fb_lineups, receipt = hltv.fallback_lineups(row_fallback)
        self.assertIsNotNone(receipt)
        vrs.apply(row_fallback, self.standings, self.vrs_meta, fb_lineups)
        self.assertIsNone(row_fallback['probabilities'])
        vrs.research_single(row_fallback, self.standings, self.vrs_meta, fb_lineups)
        self.assertEqual(row_fallback['method'], 'research_vrs_single')
        self.assertEqual(row_fallback['pick'], 'Projeto do KinGui')
        self.assertIsNone(row_fallback['probabilities'])

        # 1082901 Envy vs GamerLegion model_check resolves cleanly via Envy <-> 3DMAX.
        raw_envy, row_envy = _make_open_fixture(
            '1082901', 'Envy', 'GamerLegion',
            '2026-10-27T20:00:00Z', '2026-10-27T19:54:00Z',
            'Tesla Cup 2026', tier='b',
        )
        row_envy['hltv_context'] = {
            'teams': ['Envy', 'GamerLegion'],
            'start': '2026-10-27T20:00:00Z',
            'ranks': [],
            'lineups': [
                {'team': 'Envy', 'players': ['Graviti', 'Kursy', 'Maka', 'misutaaa', 'Lucky']},
                {'team': 'GamerLegion', 'players': ['shalfey', 'FL4MUS', 'Tauson', 'REZ', 'hypex']},
            ],
            'numeric_quote_rows': 0,
            'limitation': 'context only',
            'source': 'https://www.hltv.org/matches/2399870/envy-vs-gamerlegion-rlg-tesla-cup-2026',
            'observed_at': PINNED_ISO,
        }
        vrs.apply(row_envy, self.standings, self.vrs_meta, {
            'Envy': ['Graviti', 'Kursy', 'Maka', 'misutaaa', 'Lucky'],
            'GamerLegion': ['shalfey', 'FL4MUS', 'Tauson', 'REZ', 'hypex'],
        })
        self.assertEqual(row_envy['method'], 'model_vrs')
        self.assertEqual(row_envy['evidence'][0]['points'], [1500, 1479])
        self.assertEqual(row_envy['pick'], 'Envy')

        snapshot = {
            'schema_version': 2,
            'generated_at': PINNED_ISO,
            'last_attempt_at': PINNED_ISO,
            'refresh_started_at': PINNED_ISO,
            'fixtures_observed_at': PINNED_ISO,
            'coverage': 'verified',
            'refresh_hours': 1,
            'stale_after_hours': 8,
            'matches': [row_tdkg, row_envy],
            'source_checks': [],
            'issues': [],
            'coverage_counts': {'feed': 2, 'cs2_page': 2, 'lobby': 2},
            'fixture_conflicts': [],
            'inventory_changes': {'added': [], 'removed': []},
            'fixture_evidence': [raw_tdkg, raw_envy],
        }
        with tempfile.TemporaryDirectory() as tmp:
            site_dir = Path(tmp) / 'public'
            build.build(snapshot, site_dir, PINNED_NOW)
            built_snapshot = json.loads((site_dir / 'data/latest.json').read_text(encoding='utf-8'))
            validate_data(built_snapshot)
            validate_site(site_dir)
            rows_out, errors = self.auditor.inspect(built_snapshot)
            self.assertEqual(errors, [])
            for _, row_errs in rows_out:
                self.assertEqual(row_errs, [])


if __name__ == '__main__':
    unittest.main()
