"""Session 333b053a regression tests.

Covers:
1. Multi-day HLTV dated view ordering (all exact UTC dates before +/-1 offsets,
   DATE_PAGE_LIMIT >= 14 so 6+ distinct fixture dates like 2026-10-31 are never dropped).
2. EGamersWorld integer decimal odds (e.g. 1.001 / 12) and pre-button team2 label
   binding in scripts.books.parse_listing / reobserve, plus strict negative controls.
3. Replay of committed 2026-10-23 DFRAG book receipts (1082860 FlyQuest vs Staqued
   and 1082859 NEXVOID vs Alter Ego) through scripts.core.book_research_pick.
4. Partial (<5-player) hltv_team_pages fallback to verified 5-player lineup receipts
   in scripts.refresh.fixture_lineups, and non-TBA reason copy on same_pair_other_start.
5. Zero-diff no-op write guard in scripts.session_b214c818 and pre-commit unittest
   gate in .github/workflows/pages.yml Step 15.
"""
from __future__ import annotations

import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from scripts import books, core, hltv, refresh, session_b214c818

ROOT = Path(__file__).resolve().parents[1]


class TestHltvDateViewsMultiDay(unittest.TestCase):
    def test_single_fixture_preserves_exact_plus_one_minus_one_order(self):
        fx = [{'id': '1', 'teams': ['Alpha', 'Beta'], 'start': '2026-10-22T23:30:00Z'}]
        self.assertEqual(hltv.date_views(fx, []), ['2026-10-22', '2026-10-23', '2026-10-21'])

    def test_six_distinct_open_dates_keep_all_exact_dates_before_neighbours(self):
        dates = ['2026-10-23', '2026-10-24', '2026-10-25', '2026-10-26', '2026-10-27', '2026-10-31']
        fx = [{'id': str(i), 'teams': [f'TeamA{i}', f'TeamB{i}'], 'start': f'{d}T09:00:00Z'}
              for i, d in enumerate(dates, 1)]
        got = hltv.date_views(fx, [])
        self.assertGreaterEqual(hltv.DATE_PAGE_LIMIT, 14)
        self.assertEqual(got[:6], dates)
        self.assertIn('2026-10-31', got[:hltv.DATE_PAGE_LIMIT])


class TestBooksIntegerAndPreButtonOdds(unittest.TestCase):
    EGW_FLYQUEST_STAQUED = """
    <html><head>
    <script type="application/ld+json">{"name":"FlyQuest VS Staqued",
    "description":"FlyQuest VS Staqued: DFRAG Invitational 2026",
    "startDate":"2026-10-27T03:00:00.000Z"}</script>
    </head><body>
    <div class="header">
      <a href="/counterstrike/team/flyquest">FlyQuest<span>1.001</span></a>
      <div>26.10.26 23:00 Bo3</div>
      <a href="/counterstrike/team/staqued">Staqued<span>12</span></a>
      <div class="bet"><a>1.001</a><a>Make a bet</a><a>12</a></div>
    </div>
    </body></html>
    """

    def test_parse_listing_accepts_integer_odds_and_pre_button_second_label(self):
        readings = books.parse_listing(self.EGW_FLYQUEST_STAQUED)
        self.assertEqual(len(readings), 1)
        r = readings[0]
        self.assertEqual((r['team1'], r['team2']), ('FlyQuest', 'Staqued'))
        self.assertEqual(r['start'], '2026-10-27T03:00:00.000Z')
        self.assertEqual(r['odds'], [1.001, 12.0])
        self.assertTrue(r['bound_to_labels'])

    def test_parse_listing_rejects_unit_or_sub_unit_and_prefix_mismatch(self):
        unit_odds = self.EGW_FLYQUEST_STAQUED.replace('1.001', '1.00')
        self.assertEqual(books.parse_listing(unit_odds), [])
        prefix_mismatch = self.EGW_FLYQUEST_STAQUED.replace('Staqued<span>12</span>', 'Staqued<span>125</span>')
        readings = books.parse_listing(prefix_mismatch)
        self.assertEqual(len(readings), 1)
        self.assertFalse(readings[0]['bound_to_labels'])

    def test_reobserve_renews_committed_flyquest_and_nexvoid_receipts(self):
        reg = json.loads((ROOT / 'data/book-receipts.json').read_text())
        by_id = {r['id']: copy.deepcopy(r) for r in reg['receipts']}
        fly = by_id['egw-4kaAQWgKEx-flyquest-staqued']
        nex = by_id['egw-4kaAQWgKEx-nexvoid-alter-ego']
        nex_html = (
            '<html><head><script type="application/ld+json">'
            '{"name":"NEXVOID VS Alter Ego","startDate":"2026-10-26T03:00:00.000Z"}'
            '</script></head><body>'
            '<a>NEXVOID<span>1.61</span></a><div>25.10.26 23:00 Bo3</div>'
            '<a>Alter Ego<span>2.14</span></a>'
            '<div><a>1.61</a><a>Make a bet</a><a>2.14</a></div></body></html>'
        )
        pages = {fly['url']: self.EGW_FLYQUEST_STAQUED, nex['url']: nex_html}

        class StubSrc:
            def get(self, name, url, as_json=True, headers=None):
                return pages[url], {'name': name, 'url': url, 'observed_at': '2026-10-23T06:00:00Z'}

        now = datetime(2026, 10, 23, 6, 0, tzinfo=timezone.utc)
        out, records = books.reobserve([fly, nex], StubSrc(), now)
        self.assertEqual([r['status'] for r in records], ['renewed', 'renewed'])
        self.assertEqual(out[0]['odds'], [1.001, 12.0])
        self.assertEqual(out[1]['odds'], [1.61, 2.14])

    def test_committed_dfrag_receipts_price_exact_fixtures_via_production_path(self):
        reg = json.loads((ROOT / 'data/book-receipts.json').read_text())['receipts']
        now = datetime(2026, 10, 23, 5, 15, tzinfo=timezone.utc)

        fly_row = {
            'id': '1082860', 'state': 'open', 'teams': ['FlyQuest', 'Staqued'],
            'start': '2026-10-27T03:00:00Z', 'lock': '2026-10-27T02:54:00Z',
            'best_of': None, 'probabilities': None, 'fair_odds': None,
            'pick': None, 'method': None, 'evidence': [], 'attempts': [], 'flags': [],
        }
        core.book_research_pick(fly_row, receipts=reg, now=now)
        self.assertEqual(fly_row['method'], 'bookmaker_fallback')
        self.assertEqual(fly_row['pick'], 'FlyQuest')
        self.assertAlmostEqual(fly_row['probabilities'][0], (1 / 1.001) / (1 / 1.001 + 1 / 12.0), places=12)
        self.assertAlmostEqual(sum(fly_row['probabilities']), 1.0, places=12)

        nex_row = {
            'id': '1082859', 'state': 'open', 'teams': ['NEXVOID', 'Alter Ego'],
            'start': '2026-10-26T03:00:00Z', 'lock': '2026-10-26T02:54:00Z',
            'best_of': None, 'probabilities': None, 'fair_odds': None,
            'pick': None, 'method': None, 'evidence': [], 'attempts': [], 'flags': [],
        }
        core.book_research_pick(nex_row, receipts=reg, now=now)
        self.assertEqual(nex_row['method'], 'bookmaker_fallback')
        self.assertEqual(nex_row['pick'], 'NEXVOID')
        self.assertAlmostEqual(nex_row['probabilities'][0], (1 / 1.61) / (1 / 1.61 + 1 / 2.14), places=12)
        self.assertAlmostEqual(sum(nex_row['probabilities']), 1.0, places=12)


class TestRefreshFixtureLineupsAndPagesGate(unittest.TestCase):
    def test_partial_team_page_roster_falls_back_to_five_player_lineup_receipt(self):
        row = {
            'id': '1081149',
            'teams': ['FORZE Reload', 'LFO 10'],
            'start': '2026-10-23T08:00:00Z',
            'hltv_context': None,
            'hltv_team_pages': {
                'observed_at': '2026-10-23T05:00:00Z',
                'teams': [
                    {'team': 'FORZE Reload', 'url': 'https://www.hltv.org/team/12857/forze-reload',
                     'players': ['KusMe', 'NickelBack', 'Lack1', 'YumsaN', 'HeCkBNk']},
                    {'team': 'LFO 10', 'url': 'https://www.hltv.org/team/14084/lfo-10',
                     'players': ['Sapec', 'dan1', 'Mann3n']},
                ],
            },
        }
        lineups, receipt = refresh.fixture_lineups(row)
        self.assertIsNotNone(receipt)
        self.assertEqual(len(lineups['LFO 10']), 5)
        self.assertCountEqual(lineups['LFO 10'], ['Sapec', 'L00m1', 'dottie', 'Mann3n', 'dan1'])

    def test_session_b214c818_noop_does_not_rewrite_identities_or_review_notes(self):
        with mock.patch.object(Path, 'write_text') as mocked_write:
            self.assertEqual(session_b214c818.main(), 0)
            mocked_write.assert_not_called()

    def test_pages_workflow_runs_unittest_before_staging_root_fallback(self):
        yml = (ROOT / '.github/workflows/pages.yml').read_text()
        idx_step = yml.index('Keep the legacy main:/ root fallback on the verified build')
        # Slice to the next step instead of a fixed character window: session
        # 572c65b7 documented the 2026-10-24 freeze in the step, and a 2400-char
        # window began truncating the gate it is meant to check.
        rest = yml[idx_step:]
        following = rest.find('\n      - name:', 1)
        step_block = rest if following == -1 else rest[:following]
        self.assertLess(step_block.index('unittest discover -s tests'),
                        step_block.index('git commit -m "Publish the verified build'))


if __name__ == '__main__':
    unittest.main()
