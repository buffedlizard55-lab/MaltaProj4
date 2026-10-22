"""Regression suite for Session 80504414 (2026-10-22).

Calendar-pinned at ``PINNED_NOW`` so scheduled CI never fails on wall-clock drift.

Covers:
1. ``#exec-banner`` live ``data-count`` counters (``open``, ``priced``, ``researched``,
   ``picked``, ``missing``) and direct internal links to ``picks.html``,
   ``unresolved.html``, ``review.html``, ``matches.html``, and ``sources.html#method``.
2. Direct ``https://`` official-source links on every HTML table data row across all
   rendered pages, specifically pinning ``results_section`` ``pick_outcomes`` rows
   and ``contrarian_screen`` 15–40% underdog & research rows.
3. Primary-source register hygiene across ``data/lineup-receipts.json`` (including
   ``1082922``, ``1082925``, ``1082926``, and finalized 5-man ``Staqued`` on
   ``1082860``), ``data/book-receipts.json`` (canonical EGW ``0U32SId-H/...3nbNt3Gf1p``
   placeholder refusal and rejected cross-operator Stavka ``1082922`` listing),
   and ``data/review-notes.json`` (4 dated ``80504414-*`` flags, ``indent=1``).
4. Independent Session ``80504414`` auditor (``verification-80504414/audit_80504414.py``)
   passes with zero failures on a freshly built site.
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from bs4 import BeautifulSoup

from scripts import build, validate
from scripts.core import dt, iso

ROOT = Path(__file__).resolve().parents[1]
PINNED_NOW = dt('2026-10-22T09:05:00Z')
PINNED_ISO = iso(PINNED_NOW)


def _load_auditor():
    spec = importlib.util.spec_from_file_location(
        'audit_80504414', ROOT / 'verification-80504414/audit_80504414.py'
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _synthetic_snapshot() -> dict:
    return {
        'schema_version': 2,
        'generated_at': PINNED_ISO,
        'last_attempt_at': PINNED_ISO,
        'refresh_started_at': PINNED_ISO,
        'fixtures_observed_at': PINNED_ISO,
        'coverage': 'verified',
        'refresh_hours': 1,
        'stale_after_hours': 8,
        'coverage_counts': {'feed': 2, 'cs2_page': 2, 'lobby': 2},
        'fixture_conflicts': [],
        'inventory_changes': {'added': [], 'removed': []},
        'source_checks': [],
        'issues': [],
        'matches': [
            {
                'id': '1082926',
                'teams': ['Isurus', 'Hacha'],
                'competition': 'CCT South America 2026 Series #7',
                'tier': 'c',
                'status': 'scheduled',
                'state': 'open',
                'start': '2026-10-23T22:00:00Z',
                'lock': '2026-10-23T21:54:00Z',
                'end': None,
                'best_of': 3,
                'source_url': 'https://play.hotspawn.com/cs2/match/1082926',
                'feed_url': 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1',
                'probabilities': [0.6751022253514088, 0.32489777464859115],
                'fair_odds': [1.0 / 0.6751022253514088, 1.0 / 0.32489777464859115],
                'pick': 'Isurus',
                'method': 'model_vrs_mirror',
                'expires_at': '2026-10-22T15:56:52Z',
                'reason': None,
                'flags': ['Originated line from HLTV Valve ranking mirror.'],
                'evidence': [
                    {
                        'provider': 'HLTV Valve ranking (Valve points)',
                        'url': 'https://www.hltv.org/valve-ranking/teams/2026/october/21',
                        'api_url': 'https://www.hltv.org/valve-ranking/teams/2026/october/21',
                        'observed_at': '2026-10-22T07:56:52Z',
                        'ranking_as_of': '2026-10-21',
                        'fixture_teams': ['Isurus', 'Hacha'],
                        'vrs_teams': ['Isurus', 'Hacha'],
                        'standings': [200, 378],
                        'points': [667, 499],
                        'roster_checks': [
                            {'note': '4/5 overlap', 'overlap': 4},
                            {'note': '4/5 overlap', 'overlap': 4},
                        ],
                        'official_file': {
                            'as_of': '2026-10-05',
                            'url': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/live/2026/standings_global_2026_10_05.md',
                        },
                        'limitation': 'Secondary mirror of Valve points.',
                        'formula_source': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/model/fit.js',
                        'calibration_source': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/model/modelfit.png',
                    }
                ],
                'attempts': [],
            },
            {
                'id': '1082925',
                'teams': ['BESTIA Academy', 'RED Canids Academy'],
                'competition': 'CCT South America 2026 Series #7',
                'tier': 'c',
                'status': 'scheduled',
                'state': 'open',
                'start': '2026-10-23T19:00:00Z',
                'lock': '2026-10-23T18:54:00Z',
                'end': None,
                'best_of': 3,
                'source_url': 'https://play.hotspawn.com/cs2/match/1082925',
                'feed_url': 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1',
                'probabilities': None,
                'fair_odds': None,
                'pick': 'RED Canids Academy',
                'method': 'research_rank',
                'expires_at': '2026-10-22T15:56:52Z',
                'reason': 'Polymarket 0.90 spread ($0.00 Vol); EGW 1.8/1.8 placeholder; RED Canids Academy VRS Unranked.',
                'flags': ['Research pick only; win probability blank.'],
                'hltv_context': {
                    'source': 'https://www.hltv.org/matches/2399910/bestia-academy-vs-red-canids-academy-cct-2026-south-america-series-7',
                    'observed_at': '2026-10-22T08:49:00Z',
                    'limitation': 'World ranking is a directional tiebreaker only, not a win probability.',
                    'ranks': {'BESTIA Academy': 184, 'RED Canids Academy': 170},
                },
                'evidence': [],
                'attempts': [
                    {
                        'provider': 'Polymarket',
                        'status': 'unresolved',
                        'reason': 'Spread 0.90 exceeds 0.60 ceiling.',
                        'url': 'https://gamma-api.polymarket.com/markets/6036921',
                    }
                ],
            },
        ],
        'fixture_evidence': [
            {
                'id': '1082926',
                'sport_alias': 'cs2',
                'participants0_name': 'Isurus',
                'participants1_name': 'Hacha',
                'competition_name': 'CCT South America 2026 Series #7',
                'status': 'scheduled',
                'tier': 'c',
            },
            {
                'id': '1082925',
                'sport_alias': 'cs2',
                'participants0_name': 'BESTIA Academy',
                'participants1_name': 'RED Canids Academy',
                'competition_name': 'CCT South America 2026 Series #7',
                'status': 'scheduled',
                'tier': 'c',
            },
        ],
    }


class TestSession80504414(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.auditor = _load_auditor()
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.site_dir = Path(cls.tmpdir.name) / 'public'
        snap = _synthetic_snapshot()
        build.build(snap, cls.site_dir, PINNED_NOW)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmpdir.cleanup()

    def test_exec_banner_has_live_data_counts_and_review_cta(self) -> None:
        soup = BeautifulSoup((self.site_dir / 'index.html').read_text(encoding='utf-8'), 'html.parser')
        banner = soup.find(id='exec-banner')
        self.assertIsNotNone(banner)
        data_counts = {el.get('data-count'): el.get_text(strip=True) for el in banner.select('[data-count]')}
        self.assertEqual(
            data_counts,
            {'open': '2', 'picked': '2', 'unresolved': '0', 'priced': '1', 'researched': '1', 'missing': '1'},
        )
        hrefs = {a.get('href') for a in banner.find_all('a', href=True)}
        self.assertTrue(
            {'picks.html', 'unresolved.html', 'review.html', 'matches.html', 'sources.html#method'} <= hrefs,
            hrefs,
        )

    def test_every_rendered_table_row_carries_direct_https_source_link(self) -> None:
        report = self.auditor.audit_snapshot_and_site(
            self.site_dir / 'data/latest.json', self.site_dir, ROOT
        )
        self.assertEqual(report['failures'], [])
        for page_name, stats in report['table_link_audit'].items():
            self.assertEqual(stats['zero_link_rows'], 0, page_name)
            self.assertEqual(stats['internal_only_link_rows'], 0, page_name)

        # Explicitly check Day 5 pick_outcomes and contrarian_screen on analysis.html
        analysis_soup = BeautifulSoup((self.site_dir / 'analysis.html').read_text(encoding='utf-8'), 'html.parser')
        contrarian = analysis_soup.find(id='contrarian')
        self.assertIsNotNone(contrarian)
        rows = contrarian.select('tbody tr')
        self.assertEqual(len(rows), 2)
        for tr in rows:
            ext = [a['href'] for a in tr.find_all('a', href=True) if a['href'].startswith('https://')]
            self.assertGreaterEqual(len(ext), 2, tr.get_text(' ', strip=True))

    def test_committed_registers_include_80504414_receipts_and_flags(self) -> None:
        lineup_raw = (ROOT / 'data/lineup-receipts.json').read_text(encoding='utf-8')
        lineup_doc = json.loads(lineup_raw)
        self.assertEqual(lineup_raw, json.dumps(lineup_doc, indent=2, ensure_ascii=False) + '\n')
        by_fid = {r['fixture_id']: r for r in lineup_doc['receipts']}
        for fid in ('1082860', '1082922', '1082925', '1082926'):
            self.assertIn(fid, by_fid)
            entry = by_fid[fid]
            for lu in entry['lineups']:
                self.assertTrue(lu['source'].startswith('https://www.hltv.org/matches/'))
                self.assertEqual(len(lu['players']), 5, (fid, lu['team']))
                self.assertTrue(validate.lineup_source_ok({'id': fid, 'teams': entry['teams']}, lu['team'], lu['players']))
        self.assertEqual(
            by_fid['1082860']['lineups'][1]['players'],
            ['w0mbat', 'xelja', 'Hazel', 'lzj', 'kasze'],
        )

        books_raw = (ROOT / 'data/book-receipts.json').read_text(encoding='utf-8')
        books_doc = json.loads(books_raw)
        self.assertEqual(books_raw, json.dumps(books_doc, indent=1, ensure_ascii=False) + '\n')
        rej_urls = {r['url'] for r in books_doc['rejected_listings']}
        self.assertIn(
            'https://egamersworld.com/counterstrike/match/0U32SId-H/bestia-academy-vs-red-canids-academy-3nbNt3Gf1p',
            rej_urls,
        )
        self.assertIn(
            'https://stavka.tv/matches/csgo/22-10-2026-low-cortisol-gremio-esports',
            rej_urls,
        )

        notes_raw = (ROOT / 'data/review-notes.json').read_text(encoding='utf-8')
        notes = json.loads(notes_raw)
        self.assertEqual(notes_raw, json.dumps(notes, indent=1, ensure_ascii=False) + '\n')
        by_id = {n['id']: n for n in notes}
        expected_ids = {
            '80504414-bestia-ac-red-canids-ac-egw-and-standin-2026-10-22',
            '80504414-low-cortisol-gremio-standin-and-crossbook-2026-10-22',
            '80504414-isurus-hacha-kvns-substitute-2026-10-22',
            '80504414-flyquest-staqued-lineup-update-2026-10-22',
        }
        self.assertTrue(expected_ids <= set(by_id))
        for nid in expected_ids:
            note = by_id[nid]
            self.assertGreaterEqual(len(note['sources']), 3, nid)
            for s in note['sources']:
                self.assertTrue(s['url'].startswith('https://'), (nid, s))


if __name__ == '__main__':
    unittest.main()
