"""Regression suite for session db1f35c5 (2026-10-21).

Calendar-pinned at ``PINNED_NOW`` (never reads wall clock ``datetime.now``) so
future dates never cause time-bomb failures.

Verifies:
1. ``1082837`` (Zetta vs LOS NINOS, 2026-10-21T22:00:00Z) resolves via the
   primary-sourced ``Zetta <-> Alianza Lima Esports`` alias to Polymarket
   moneyline ``cs2-ale1-ln-2026-10-21`` with ``pick == 'LOS NINOS'`` and passes
   both ``scripts.validate.validate_data`` and ``verification-c6/audit_snapshot.py``.
2. ``1082858`` (Ground Zero vs Off Chops, 2026-10-26T03:00:00Z) resolves via the
   DFRAG-verified ``Off Chops <-> THUNDER dOWNUNDER`` 4/5 core rebrand alias to
   calibrated two-sided ``model_vrs`` (``Off Chops`` ~59.1%, ``Ground Zero`` ~40.9%).
3. ``1081597`` (benched gods vs TitanFlow, 2026-10-22T11:00:00Z) uses verified
   same-day tournament HLTV match lineups when HLTV marks slot ``2399696``
   ``Match postponed`` (``TBA``), resolving cleanly to ``research_vrs_single``
   (``pick == 'benched gods'``, ``roster_overlap == 5``, ``probabilities is None``)
   with explicit postponement flag, while live HLTV lineups always take precedence.
4. Formatting & integrity invariants on ``data/identities.json``,
   ``data/lineup-receipts.json``, ``data/book-receipts.json``, and
   ``data/review-notes.json`` (including strict ``indent=1`` formatting).
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
PINNED_NOW = dt('2026-10-21T20:15:00Z')
PINNED_ISO = iso(PINNED_NOW)


def _load_independent_auditor():
    spec = importlib.util.spec_from_file_location('audit_snapshot_db1f35c5', ROOT / 'verification-c6/audit_snapshot.py')
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
    row['fixture_sources'] = [{'retrieved_at': PINNED_ISO, 'observed_at': PINNED_ISO,
                               'cache_age_seconds': None, 'sha256': '0' * 64,
                               'url': row['feed_url']}]
    return raw, row


class SessionDb1f35c5Tests(unittest.TestCase):
    def setUp(self):
        self.standings, self.vrs_meta = vrs.vendored(PINNED_NOW)
        self.auditor = _load_independent_auditor()

    def test_identities_fold_strictly_without_wrong_pair_leakage(self):
        self.assertEqual(norm('Zetta'), norm('Alianza Lima Esports'))
        self.assertEqual(norm('Off Chops'), norm('THUNDER dOWNUNDER'))
        self.assertNotEqual(norm('Zetta'), norm('LOS NINOS'))
        self.assertNotEqual(norm('Off Chops'), norm('Ground Zero'))

    def test_1082837_zetta_vs_los_ninos_prices_from_polymarket_and_flips_to_los_ninos(self):
        raw_zetta, row_zetta = _make_open_fixture(
            '1082837', 'Zetta', 'LOS NINOS',
            '2026-10-21T22:00:00Z', '2026-10-21T21:54:00Z',
            'CCT South America 2026 Series #7',
        )
        pm_event = {
            'id': '1227336',
            'slug': 'cs2-ale1-ln-2026-10-21',
            'sport': {'sport': 'cs2'},
            'markets': [{
                'id': '5998877',
                'question': 'Counter-Strike: Alianza Lima Esports vs Los Niños (BO3) - CCT South America Series 7',
                'sportsMarketType': 'moneyline',
                'active': True,
                'closed': False,
                'acceptingOrders': True,
                'outcomes': json.dumps(['Alianza Lima Esports', 'Los Niños']),
                'outcomePrices': json.dumps(['0.385', '0.615']),
                'gameStartTime': '2026-10-21 22:00:00+00',
                'eventStartTime': '2026-10-21T22:00:00Z',
                'updatedAt': '2026-10-21T20:10:00Z',
                'bestBid': 0.38,
                'bestAsk': 0.39,
                'liquidity': '3240.93',
                'volume': '451.02',
            }],
        }
        resolve(row_zetta, polymarket_candidates([pm_event], PINNED_ISO), 'Polymarket', PINNED_NOW)
        self.assertEqual(row_zetta['method'], 'exchange')
        self.assertEqual(row_zetta['pick'], 'LOS NINOS')
        self.assertAlmostEqual(row_zetta['probabilities'][0], 0.385, places=6)
        self.assertAlmostEqual(row_zetta['probabilities'][1], 0.615, places=6)

        # Wrong UTC start or wrong opponent must NEVER borrow this line.
        _, wrong_time = _make_open_fixture(
            '1082837b', 'Zetta', 'LOS NINOS',
            '2026-10-21T23:00:00Z', '2026-10-21T22:54:00Z',
            'CCT South America 2026 Series #7',
        )
        resolve(wrong_time, polymarket_candidates([pm_event], PINNED_ISO), 'Polymarket', PINNED_NOW)
        self.assertIsNone(wrong_time['probabilities'])

        # Full snapshot + rendered 8-page site + independent C6 audit all pass 0 errors.
        raw_gz, row_gz = _make_open_fixture(
            '1082858', 'Ground Zero', 'Off Chops',
            '2026-10-26T03:00:00Z', '2026-10-26T02:54:00Z',
            'DFRAG Invitational 2026', tier='b',
        )
        gz_lineups = {
            'Ground Zero': ['apocdud', 'Omichella', 'vision', 'tucks', 'sliimey'],
            'Off Chops': ['viridian', 'dexter', 'Liazz', 'Gratisfaction', 'damyo'],
        }
        vrs.apply(row_gz, self.standings, self.vrs_meta, gz_lineups)
        self.assertEqual(row_gz['method'], 'model_vrs')
        self.assertEqual(row_gz['pick'], 'Off Chops')
        self.assertEqual(row_gz['evidence'][0]['points'], [878, 971])

        raw_bg, row_bg = _make_open_fixture(
            '1081597', 'benched gods', 'TitanFlow',
            '2026-10-22T11:00:00Z', '2026-10-22T10:54:00Z',
            'CCT Europe 2026 Challengers #8',
        )
        bg_lineups, receipt = hltv.fallback_lineups(row_bg)
        self.assertIsNotNone(receipt)
        row_bg['flags'].append(receipt['flag'])
        vrs.apply(row_bg, self.standings, self.vrs_meta, bg_lineups)
        self.assertIsNone(row_bg['probabilities'])
        vrs.research_single(row_bg, self.standings, self.vrs_meta, bg_lineups)
        self.assertEqual(row_bg['method'], 'research_vrs_single')
        self.assertEqual(row_bg['pick'], 'benched gods')
        self.assertIsNone(row_bg['probabilities'])

        snapshot = {
            'schema_version': 2,
            'generated_at': PINNED_ISO,
            'last_attempt_at': PINNED_ISO,
            'refresh_started_at': PINNED_ISO,
            'fixtures_observed_at': PINNED_ISO,
            'coverage': 'verified',
            'refresh_hours': 1,
            'stale_after_hours': 8,
            'matches': [row_zetta, row_bg, row_gz],
            'source_checks': [],
            'issues': [],
            'coverage_counts': {'feed': 3, 'cs2_page': 3, 'lobby': 3},
            'fixture_conflicts': [],
            'inventory_changes': {'added': [], 'removed': []},
            'fixture_evidence': [raw_zetta, raw_bg, raw_gz],
        }
        with tempfile.TemporaryDirectory() as tmp:
            site_dir = Path(tmp) / 'public'
            build.build(snapshot, site_dir, PINNED_NOW)
            built_snapshot = json.loads((site_dir / 'data/latest.json').read_text())
            validate_data(built_snapshot)
            validate_site(site_dir)
            rows_out, errors = self.auditor.inspect(built_snapshot)
            self.assertEqual(errors, [])
            for _, row_errs in rows_out:
                self.assertEqual(row_errs, [])

    def test_live_hltv_lineups_always_override_fallback_receipt(self):
        _, row_bg = _make_open_fixture(
            '1081597', 'benched gods', 'TitanFlow',
            '2026-10-22T11:00:00Z', '2026-10-22T10:54:00Z',
            'CCT Europe 2026 Challengers #8',
        )
        row_bg['hltv_context'] = {
            'lineups': [
                {'team': 'benched gods', 'players': ['p1', 'p2', 'p3', 'p4', 'p5']},
                {'team': 'TitanFlow', 'players': ['q1', 'q2', 'q3', 'q4', 'q5']},
            ]
        }
        lineups, receipt = hltv.fallback_lineups(row_bg)
        self.assertIsNone(receipt)
        self.assertEqual(lineups['benched gods'], ['p1', 'p2', 'p3', 'p4', 'p5'])

    def test_committed_data_files_match_indentation_and_source_invariants(self):
        notes_raw = (ROOT / 'data/review-notes.json').read_text()
        notes = json.loads(notes_raw)
        self.assertEqual(notes_raw, json.dumps(notes, indent=1, ensure_ascii=False) + '\n')
        note_ids = {n['id'] for n in notes}
        self.assertTrue({
            'db1f35c5-zetta-alianza-resolved-2026-10-21',
            'db1f35c5-benched-gods-postponed-and-forfeit-2026-10-21',
            'db1f35c5-off-chops-rebrand-and-standin-2026-10-21',
        } <= note_ids)

        books_raw = (ROOT / 'data/book-receipts.json').read_text()
        books = json.loads(books_raw)
        self.assertEqual(books_raw, json.dumps(books, indent=1, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    unittest.main()
