import json
import unittest
from pathlib import Path

from scripts import core, vrs
from scripts.core import dt


ROOT = Path(__file__).resolve().parents[1]


class Session92b6a82dTests(unittest.TestCase):
    def test_refresh_invokes_vrs_research_single_after_research_rank_pick(self):
        source = (ROOT / 'scripts/refresh.py').read_text()
        rank_idx = source.index('research_rank_pick(m)')
        vrs_single_idx = source.index('vrs.research_single(m,standings,vrs_meta,lineups)')
        self.assertLess(
            rank_idx,
            vrs_single_idx,
            'vrs.research_single must run after research_rank_pick as the final research tier',
        )

    def test_zetta_vs_los_ninos_resolves_via_vrs_research_single_when_hltv_rank_unavailable(self):
        standings, meta = vrs._vendored(dt('2026-10-21T12:40:00Z'))
        fixture = {
            'id': '1082837',
            'teams': ['Zetta', 'LOS NINOS'],
            'competition': 'CCT South America 2026 Series #7',
            'tier': 'c',
            'best_of': None,
            'start': '2026-10-21T22:00:00Z',
            'lock': '2026-10-21T21:54:00Z',
            'state': 'open',
            'probabilities': None,
            'fair_odds': None,
            'pick': None,
            'method': None,
            'reason': None,
            'flags': [],
            'attempts': [],
            'hltv_context': {
                'id': '2399865',
                'url': 'https://www.hltv.org/matches/2399865/zetta-vs-los-ninos-cct-2026-south-america-series-7',
                'lineups': [
                    {'team': 'Zetta', 'players': ['Notjuanjo', 'zockie', 'BabyRage', 'Antuanette', 'Slayerhz']},
                    {'team': 'LOS NINOS', 'players': ['Reix', 'PremiuM', 'aNgelo', 'protado', 'Space']},
                ],
                'ranks': [],
            },
        }
        lineups = {x['team']: x['players'] for x in fixture['hltv_context']['lineups']}
        vrs.research_single(fixture, standings, meta, lineups)
        self.assertEqual(fixture['pick'], 'Zetta')
        self.assertEqual(fixture['method'], 'research_vrs_single')
        self.assertIsNone(fixture['probabilities'])
        self.assertIsNone(fixture['fair_odds'])
        self.assertEqual(fixture['vrs_research']['resolved_vrs'][0]['standing'], 357)
        self.assertEqual(fixture['vrs_research']['resolved_vrs'][0]['points'], 473)
        self.assertEqual(fixture['vrs_research']['resolved_vrs'][1]['status'], 'absent')
        # Also verify the independent auditor (verification-c6/audit_snapshot.py)
        # accepts the research_vrs_single row with 0 failures.
        import importlib.util
        spec = importlib.util.spec_from_file_location('audit_snapshot', ROOT / 'verification-c6/audit_snapshot.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        snap = json.loads((ROOT / 'research/harvest-40c14278/snapshot.json').read_text())
        for row in snap['matches']:
            if row['id'] == '1082837':
                row.pop('hltv_ranks', None)
                row.pop('hltv_source', None)
                row.update(fixture)
        _, errors = mod.inspect(snap)
        self.assertEqual(errors, [])

    def test_wide_exchange_60_point_spread_ceiling_is_float_safe(self):
        now = dt('2026-10-21T12:45:00Z')
        raw_market = {
            'id': '6001634',
            'sportsMarketType': 'moneyline',
            'outcomes': '["Alianza Lima Esports", "Los Niños"]',
            'outcomePrices': '["0.49", "0.51"]',
            'active': True,
            'closed': False,
            'acceptingOrders': True,
            'bestBid': 0.19,
            'bestAsk': 0.79,
            'liquidity': '542.6664',
            'updatedAt': '2026-10-21T12:34:41.58777Z',
            'gameStartTime': '2026-10-21 22:00:00+00',
        }
        candidate = {
            'provider': 'Polymarket',
            'id': '6001634',
            'url': 'https://polymarket.com/event/cs2-ali1-losn-2026-10-21',
            'api_url': 'https://gamma-api.polymarket.com/markets/6001634',
            'observed_at': '2026-10-21T12:45:00Z',
            'updated_at': '2026-10-21T12:34:41Z',
            'teams': ['Alianza Lima Esports', 'Los Niños'],
            'start': dt('2026-10-21T22:00:00Z'),
            'event': 'CCT South America Series 7',
            'prices': [0.49, 0.51],
            'market': raw_market,
            'raw': raw_market,
        }
        # In IEEE-754 float, 0.79 - 0.19 == 0.6000000000000001; allow_wide must accept
        # a genuine 60.0-point spread just as verification-c6 Decimal('.60') does.
        quote = core.quote_polymarket(candidate, [0, 1], now, allow_wide=True)
        self.assertEqual(quote['tier'], 'wide_exchange')
        self.assertAlmostEqual(quote['probabilities'][0], 0.49, places=6)
        self.assertAlmostEqual(quote['probabilities'][1], 0.51, places=6)
        self.assertIn('Low confidence', quote['warning'])

    def test_review_note_and_report_exist_and_have_https_sources(self):
        notes = json.loads((ROOT / 'data/review-notes.json').read_text())
        entry = next((n for n in notes if n.get('id') == '92b6a82d-zetta-los-ninos-audit'), None)
        self.assertIsNotNone(entry)
        self.assertGreaterEqual(len(entry['sources']), 5)
        for src in entry['sources']:
            self.assertTrue(src['url'].startswith('https://'), src)
        report = (ROOT / 'research/session-92b6a82d/REPORT.md').read_text()
        self.assertIn('1082837', report)
        self.assertIn('Alianza Lima Esports', report)


if __name__ == '__main__':
    unittest.main()
