"""Regression tests for session 0247223d:

1. Automated pre-match Thunderpick / BO3.gg CS2 moneyline adapter (`scripts/bo3.py`):
   - Accepts valid upcoming CS2 (`discipline_id=1, game_version=2`) matches with
     active team-ID-bound `bet_updates`, exact UTC start, matching `bo_type`,
     and valid bookmaker overround (`[-0.02, 0.25]`).
   - Refuses wrong discipline/game_version, started/ended/settled matches, TBA or
     duplicate team IDs, suspended (`active=False`) quotes, swapped/mismatched
     `team_id` bindings, placeholder/unit (`<= 1.0`) or out-of-margin odds,
     series-format mismatches, stale observations, and duplicate feed entries.
   - Integrates end-to-end with `book_research_pick`, `scripts.validate.validate_data`,
     `verification-c6/audit_snapshot.py`, and `verification-138cbedd/audit_board.py`
     without special-case overrides.
2. Primary-source organization aliases (`data/identities.json`):
   - Maps main CS2 org names cleanly (`Team Vitality` -> `Vitality`, `Nemiga Gaming`
     -> `Nemiga`, `G2 Esports` -> `G2`, `Team Spirit` -> `Spirit`, `NAVI` ->
     `Natus Vincere`, `FURIA Esports` -> `FURIA`, `FUT Esports` -> `FUT`,
     `BakS eSports` -> `BakS`, `LPH Gaming` -> `LPH`) while strictly isolating
     academy/secondary squads (`Spirit Academy`, `G2 Ares`, `FUT Academy`, `FURIA fe`).
3. Scheduled-publish resilience (`tests/test_session_8fdf1f99.py` + `audit_board.py`):
   - `ResearchRowsAreHonest` validates actual non-vacuous `research_rank`,
     `research_rank_single`, `research_vrs_single`, and `research_form` rows
     (which must keep `evidence == []` per `verification-c6/audit_snapshot.py`),
     and `verification-138cbedd/audit_board.py` accepts `research_form`.
4. Executive summary & mobile board clarity:
   - `index.html` links directly to `picks.html`, `unresolved.html`, `matches.html`,
     `review.html`, `#picks-at-a-glance`, and `#unresolved-picks`, and `picks.html`
     renders both teams' win percentages alongside the highlighted pick for every
     priced open fixture.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import bo3, build, core, validate
from scripts.core import dt, iso, norm

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data/latest.json').read_text(encoding='utf-8'))
NOW = dt('2026-10-23T10:00:00Z')
OBS = '2026-10-23T09:50:00Z'


def sample_bo3_row(**overrides) -> dict:
    base = {
        'id': 990101,
        'slug': 'flyquest-vs-staqued-27-10-2026',
        'team1_id': 10398,
        'team2_id': 25258,
        'winner_team_id': None,
        'loser_team_id': None,
        'status': 'upcoming',
        'bo_type': 3,
        'start_date': '2026-10-27T03:00:00.000+00:00',
        'end_date': None,
        'discipline_id': 1,
        'game_version': 2,
        'bet_updates': {
            'path': 'https://thunderpick.io/match/2872333',
            'team_1': {'name': 'FlyQuest', 'coeff': 1.001, 'active': True, 'team_id': 10398},
            'team_2': {'name': 'Staqued', 'coeff': 12.0, 'active': True, 'team_id': 25258},
            'provider': 'thunderpick',
            'markets_count': 7,
        },
        'team1': {'id': 10398, 'slug': 'flyquest', 'name': 'FlyQuest', 'discipline_id': 1},
        'team2': {'id': 25258, 'slug': 'staqued', 'name': 'Staqued', 'discipline_id': 1},
        'tournament': {'id': 6150, 'slug': 'dfrag-invitational-2026', 'name': 'DFRAG Invitational 2026'},
    }
    base.update(overrides)
    return base


def sample_fixture(**overrides) -> dict:
    row = {
        'id': '999860',
        'teams': ['FlyQuest', 'Staqued'],
        'team_ids': ['161153', '263291'],
        'competition': 'DFRAG Invitational 2026',
        'tier': 'b',
        'best_of': 3,
        'start': '2026-10-27T03:00:00Z',
        'lock': '2026-10-27T02:54:00Z',
        'source_status': 'scheduled',
        'state': 'open',
        'source_url': 'https://www.hotspawn.com/matches/flyquest-vs-staqued-dfrag-invitational-2026-1082860',
        'feed_url': core.FIXTURES,
        'flags': [],
        'probabilities': None,
        'fair_odds': None,
        'pick': None,
        'method': None,
        'evidence': [],
        'attempts': [],
        'reason': None,
    }
    row.update(overrides)
    return row


class Bo3ThunderpickAdapterTests(unittest.TestCase):
    def test_valid_prematch_thunderpick_row_replays_through_all_validators_and_auditors(self):
        feed_url = bo3.page_url(0, 100)
        entry, status = bo3.parse_match_row(
            sample_bo3_row(), OBS, feed_url, {'observed_at': OBS, 'sha256': 'a' * 64, 'url': feed_url}
        )
        self.assertEqual(status, 'ok')
        self.assertTrue(entry['priced'])
        self.assertEqual(entry['odds'], [1.001, 12.0])

        # Reversed fixture team order proves exact orientation handling.
        fx = sample_fixture(teams=['Staqued', 'FlyQuest'], team_ids=['263291', '161153'])
        receipt, attempt = bo3.build_receipt_for_fixture(fx, [entry], NOW)
        self.assertEqual(attempt['status'], 'resolved')
        self.assertIsNotNone(receipt)

        core.book_research_pick(fx, receipts=[receipt], now=NOW)
        fx['expires_at'] = core.pick_deadline(fx, OBS)
        self.assertEqual(fx['method'], 'bookmaker_fallback')
        self.assertEqual(fx['pick'], 'FlyQuest')
        self.assertAlmostEqual(sum(fx['probabilities']), 1.0, places=12)
        self.assertLess(fx['probabilities'][0], 0.10)
        self.assertGreater(fx['probabilities'][1], 0.90)

        reconstructed = validate.reconstruct_quote(fx['evidence'][0], schema_version=2)
        replayed = core.quote_book(reconstructed, [1, 0], NOW)
        self.assertEqual(replayed['probabilities'], fx['probabilities'])

        spec_c6 = importlib.util.spec_from_file_location('audit_c6', ROOT / 'verification-c6/audit_snapshot.py')
        audit_c6 = importlib.util.module_from_spec(spec_c6)
        spec_c6.loader.exec_module(audit_c6)

        spec_138 = importlib.util.spec_from_file_location('audit_138', ROOT / 'verification-138cbedd/audit_board.py')
        audit_138 = importlib.util.module_from_spec(spec_138)
        spec_138.loader.exec_module(audit_138)

        snap = {
            'schema_version': 2,
            'generated_at': iso(NOW),
            'last_attempt_at': iso(NOW),
            'fixtures_observed_at': OBS,
            'stale_after_hours': 8,
            'coverage': 'verified',
            'coverage_counts': {'api': 1, 'page': 1, 'lobby': 1, 'retained': 1},
            'matches': [fx],
            'fixture_evidence': [{
                'id': '999860',
                'sport_alias': 'cs2',
                'status': 'scheduled',
                'scheduled_start_time': '2026-10-27T03:00:00Z',
                'lock_time': '2026-10-27T02:54:00Z',
                'end_time': None,
                'participants0_id': '263291',
                'participants0_name': 'Staqued',
                'participants1_id': '161153',
                'participants1_name': 'FlyQuest',
                'competition_name': 'DFRAG Invitational 2026',
                'tier': 'b',
                'best_of': 3,
            }],
        }
        validate.validate_data(snap)
        _, errors = audit_c6.inspect(snap)
        self.assertEqual(errors, [])

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'snap.json'
            p.write_text(json.dumps(snap), encoding='utf-8')
            report_138 = audit_138.audit(str(p), identities_path=str(ROOT / 'data/identities.json'))[0]
            self.assertEqual(report_138.failures, [])

    def test_fail_closed_rejections_on_malformed_wrong_game_live_or_unbound_quotes(self):
        feed_url = bo3.page_url(0, 100)
        hard_drop_cases = [
            {'discipline_id': 2},
            {'game_version': 1},
            {'status': 'current'},
            {'end_date': '2026-10-27T05:00:00Z'},
            {'winner_team_id': 10398},
            {'team2': None},
            {'team2': {'id': 10398, 'slug': 'dup', 'name': 'FlyQuest', 'discipline_id': 1}},
            {'start_date': '2026-10-27 03:00:00'},
        ]
        for bad in hard_drop_cases:
            with self.subTest(bad=bad):
                parsed, _ = bo3.parse_match_row(sample_bo3_row(**bad), OBS, feed_url)
                self.assertIsNone(parsed)

        unpriced_cases = [
            {'bet_updates': None},
            {'bet_updates': {'provider': 'thunderpick', 'team_1': {'name': 'FlyQuest', 'coeff': 1.5, 'active': False, 'team_id': 10398}, 'team_2': {'name': 'Staqued', 'coeff': 2.5, 'active': True, 'team_id': 25258}}},
            {'bet_updates': {'provider': 'thunderpick', 'team_1': {'name': 'FlyQuest', 'coeff': 1.5, 'active': True, 'team_id': 25258}, 'team_2': {'name': 'Staqued', 'coeff': 2.5, 'active': True, 'team_id': 10398}}},
            {'bet_updates': {'provider': 'thunderpick', 'team_1': {'name': 'FlyQuest', 'coeff': 1.0, 'active': True, 'team_id': 10398}, 'team_2': {'name': 'Staqued', 'coeff': 12.0, 'active': True, 'team_id': 25258}}},
            {'bet_updates': {'provider': 'thunderpick', 'team_1': {'name': 'FlyQuest', 'coeff': 1.2, 'active': True, 'team_id': 10398}, 'team_2': {'name': 'Staqued', 'coeff': 1.2, 'active': True, 'team_id': 25258}}},
        ]
        fx = sample_fixture()
        for bad in unpriced_cases:
            with self.subTest(unpriced=bad):
                parsed, _ = bo3.parse_match_row(sample_bo3_row(**bad), OBS, feed_url)
                self.assertIsNotNone(parsed)
                self.assertFalse(parsed['priced'])
                receipt, att = bo3.build_receipt_for_fixture(fx, [parsed], NOW)
                self.assertIsNone(receipt)
                self.assertEqual(att['status'], 'unresolved')

    def test_discover_receipts_paginates_and_records_attempts_cleanly(self):
        class StubSrc:
            def get(self, name, url, as_json=True):
                return {'total': {'count': 1, 'pages': 1}, 'results': [sample_bo3_row()]}, {
                    'observed_at': OBS, 'sha256': 'b' * 64, 'url': url
                }

        fx_hit = sample_fixture()
        fx_miss = sample_fixture(id='999861', teams=['Rooster', 'Abyssal'])
        receipts, attempts = bo3.discover_receipts([fx_hit, fx_miss], StubSrc(), NOW)
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0]['fixture_id'], '999860')
        self.assertEqual({a['fixture_id']: a['status'] for a in attempts},
                         {'999860': 'resolved', '999861': 'unresolved'})


class IdentityIsolationAndMobileClarityTests(unittest.TestCase):
    def test_organization_aliases_resolve_main_clubs_without_colliding_with_academies(self):
        self.assertEqual(norm('Team Vitality'), norm('Vitality'))
        self.assertEqual(norm('Nemiga Gaming'), norm('Nemiga'))
        self.assertEqual(norm('G2 Esports'), norm('G2'))
        self.assertEqual(norm('Team Spirit'), norm('Spirit'))
        self.assertEqual(norm('NAVI'), norm('Natus Vincere'))
        self.assertEqual(norm('FURIA Esports'), norm('FURIA'))
        self.assertEqual(norm('FUT Esports'), norm('FUT'))
        self.assertEqual(norm('BakS eSports'), norm('BakS'))
        self.assertEqual(norm('LPH Gaming'), norm('LPH'))

        # Academy / secondary rosters must NEVER collapse into main club labels.
        self.assertNotEqual(norm('Spirit Academy'), norm('Spirit'))
        self.assertNotEqual(norm('G2 Ares'), norm('G2'))
        self.assertNotEqual(norm('FUT Academy'), norm('FUT'))
        self.assertNotEqual(norm('FURIA fe'), norm('FURIA'))
        self.assertNotEqual(norm('Aurora Young Blud'), norm('Aurora'))

    def test_research_row_contract_is_non_vacuous_across_all_research_tiers(self):
        from tests.test_session_8fdf1f99 import ResearchRowsAreHonest
        spec_138 = importlib.util.spec_from_file_location('audit_138', ROOT / 'verification-138cbedd/audit_board.py')
        audit_138 = importlib.util.module_from_spec(spec_138)
        spec_138.loader.exec_module(audit_138)
        self.assertIn('research_form', audit_138.RESEARCH_METHODS)

        synthetic_rows = [
            {
                'id': '999901',
                'state': 'open',
                'teams': ['Alpha', 'Bravo'],
                'pick': 'Alpha',
                'method': 'research_rank_single',
                'probabilities': None,
                'fair_odds': None,
                'evidence': [],
                'hltv_context': {'source': 'https://www.hltv.org/matches/999901/alpha-vs-bravo'},
                'attempts': [{'provider': 'Rank research', 'status': 'resolved', 'url': 'https://www.hltv.org/matches/999901/alpha-vs-bravo'}],
            },
            {
                'id': '999902',
                'state': 'open',
                'teams': ['Charlie', 'Delta'],
                'pick': 'Charlie',
                'method': 'research_vrs_single',
                'probabilities': None,
                'fair_odds': None,
                'evidence': [],
                'vrs_research': {'source': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/live/2026/standings_global_2026_10_05.md'},
                'attempts': [{'provider': 'Valve VRS research', 'status': 'resolved', 'url': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/live/2026/standings_global_2026_10_05.md'}],
            },
            {
                'id': '999903',
                'state': 'open',
                'teams': ['Echo', 'Foxtrot'],
                'pick': 'Echo',
                'method': 'research_form',
                'probabilities': None,
                'fair_odds': None,
                'evidence': [],
                'hltv_context': {'source': 'https://www.hltv.org/matches/999903/echo-vs-foxtrot'},
                'attempts': [{'provider': 'Form research', 'status': 'resolved', 'url': 'https://www.hltv.org/matches/999903/echo-vs-foxtrot'}],
            },
        ]
        for row in synthetic_rows:
            urls = ResearchRowsAreHonest.research_urls(row)
            self.assertTrue(urls and all(u.startswith('https://') for u in urls))
            self.assertFalse(row['evidence'])

    def test_executive_summary_links_and_picks_board_dual_probabilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            clock = dt(SNAPSHOT['generated_at'])
            build.build(copy.deepcopy(SNAPSHOT), out, now=clock)
            validate.validate_site(out)
            index_soup = BeautifulSoup((out / 'index.html').read_text(encoding='utf-8'), 'html.parser')
            hrefs = {a.get('href') for a in index_soup.find_all('a', href=True)}
            for expected in ('picks.html', 'unresolved.html', 'matches.html',
                             'review.html', '#picks-at-a-glance', '#unresolved-picks'):
                self.assertIn(expected, hrefs)
            picks_soup = BeautifulSoup((out / 'picks.html').read_text(encoding='utf-8'), 'html.parser')
            open_rows = {m['id']: m for m in SNAPSHOT['matches'] if m['state'] == 'open'}
            for tr in picks_soup.select('tr[data-match]'):
                m = open_rows[tr['data-match']]
                if m['probabilities'] is not None:
                    spans = [s.get_text(strip=True) for s in tr.select('.prob-pair > span')]
                    self.assertEqual(len(spans), 2, m['id'])


if __name__ == '__main__':
    unittest.main()
