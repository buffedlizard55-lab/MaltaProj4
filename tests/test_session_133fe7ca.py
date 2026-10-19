"""Session 133fe7ca regressions: final results and the last unpicked fixture.

Two claims are pinned here:

* The 18 October Thunderpick final day is published as a completed, sourced
  result with honest pre-lock pick outcomes, and the old guide can no longer say
  "TODAY" on 19 October.
* Hotspawn's "Aurora YB" is the same club as HLTV's "Aurora Young Blud" for an
  exact fixture, so the existing ranking tier can produce a research pick for
  the Sangal fixture without inventing a probability. The main "Aurora" register
  entry must remain separate.
"""
from __future__ import annotations

import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import build
from scripts.core import (book_candidate, book_receipts, book_research_pick, iso, norm,
                          normalize_fixtures, quote_book, research_rank_pick)

ROOT = Path(__file__).resolve().parents[1]
NOTES = json.loads((ROOT / 'data/analysis.json').read_text())
LATEST = json.loads((ROOT / 'data/latest.json').read_text())


def fixture_for(team_a: str, team_b: str) -> dict:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    start = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)
    raw = {'id': '1082157', 'sport_alias': 'cs2', 'participants0_name': team_a,
           'participants1_name': team_b, 'participants0_id': 'a', 'participants1_id': 'b',
           'status': 'scheduled', 'scheduled_start_time': iso(start),
           'lock_time': iso(start - timedelta(minutes=6)),
           'competition_name': 'Stake Ranked Episode 6: Closed Qualifier', 'tier': 'b',
           'best_of': 3}
    row = normalize_fixtures([raw], {}, now)[0]
    row.update(probabilities=None, fair_odds=None, pick=None, method=None, evidence=[],
               flags=[], attempts=[], reason=None)
    row['hltv_context'] = {
        'teams': ['Sangal', 'Aurora Young Blud'], 'start': iso(start),
        'ranks': [
            {'team': 'Sangal', 'hltv_rank': 45,
             'source': 'https://www.hltv.org/ranking/teams/2026/october/12/1',
             'hltv_unranked': False, 'vrs_rank_on_hltv': 38, 'vrs_source': None},
            {'team': 'Aurora Young Blud', 'hltv_rank': None,
             'source': None, 'hltv_unranked': True, 'vrs_rank_on_hltv': None,
             'vrs_source': None},
        ],
        'lineups': [], 'source': 'https://www.hltv.org/matches/2399777/sangal-vs-aurora-young-blud-stake-ranked-episode-6-closed-qualifier',
        'observed_at': iso(now), 'numeric_quote_rows': 0, 'limitation': 'context only',
    }
    return row


class AuroraYoungBludIdentityTests(unittest.TestCase):
    def test_alias_joins_the_two_verified_labels_only(self):
        self.assertEqual(norm('Aurora YB'), norm('Aurora Young Blud'))
        self.assertNotEqual(norm('Aurora YB'), norm('Aurora'))

    def test_unpicked_fixture_now_gets_a_sourced_research_pick(self):
        row = fixture_for('Sangal', 'Aurora YB')
        row['id'] = '9999999'  # no book receipt for this id: exercise the rank tier
        research_rank_pick(row)
        self.assertEqual((row['pick'], row['method']), ('Sangal', 'research_rank_single'))
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['fair_odds'])
        mapped = next(r for r in row['hltv_context']['resolved_ranks'] if r['team'] == 'Aurora YB')
        self.assertEqual(mapped['hltv_name'], 'Aurora Young Blud')
        self.assertEqual(mapped['status'], 'unranked')
        self.assertTrue(mapped['alias_source'].startswith('https://www.hltv.org/matches/2399777/'))
        self.assertIn('no percentage is published', row['reason'])

    def test_main_aurora_identity_is_untouched(self):
        from scripts.core import IDENTITIES
        aurora = next(item for item in IDENTITIES if item['canonical'] == 'Aurora')
        self.assertEqual(aurora['names'], ['Aurora', 'Aurora Gaming'])
        young = next(item for item in IDENTITIES if item['canonical'] == 'Aurora Young Blud')
        self.assertEqual(young['names'], ['Aurora Young Blud', 'Aurora YB'])
        self.assertNotIn('Aurora', young['names'])


class BookListingForTheLastFixtureTests(unittest.TestCase):
    receipt = next(r for r in book_receipts() if r['id'] == 'egw-41yaj8BdVx-sangal-aurora-young-blud')

    def test_receipt_order_maps_to_hotspawn_and_de_vigs(self):
        candidate = book_candidate(self.receipt)
        self.assertEqual(candidate['fixture_id'], '1082157')
        self.assertEqual(candidate['teams'], ['Sangal', 'Aurora Young Blud'])
        self.assertEqual(candidate['start'], '2026-10-20T12:00:00Z')
        quote = quote_book(candidate, [0, 1], datetime(2026, 10, 19, 4, 30, tzinfo=timezone.utc))
        self.assertAlmostEqual(quote['probabilities'][0], 0.8533, places=4)
        self.assertAlmostEqual(quote['probabilities'][1], 0.1467, places=4)
        self.assertAlmostEqual(quote['overround'], 0.0852, places=4)

    def test_receipt_prices_the_exact_fixture_only(self):
        row = fixture_for('Sangal', 'Aurora YB')
        book_research_pick(row, [self.receipt], now=datetime(2026, 10, 19, 4, 30, tzinfo=timezone.utc))
        self.assertEqual(row['pick'], 'Sangal')
        self.assertEqual(row['method'], 'bookmaker_fallback')
        self.assertAlmostEqual(row['probabilities'][0], 0.8533, places=4)
        other = fixture_for('Sangal', 'Aurora')
        book_research_pick(other, [self.receipt], now=datetime(2026, 10, 19, 4, 30, tzinfo=timezone.utc))
        self.assertIsNone(other['probabilities'])
        self.assertIsNone(other['pick'])

    def test_receipt_expires_after_eight_hours(self):
        candidate = book_candidate(self.receipt)
        with self.assertRaises(ValueError):
            quote_book(candidate, [0, 1], datetime(2026, 10, 19, 12, 13, tzinfo=timezone.utc))

    def test_rank_fallback_still_exists_after_the_line_ages_out(self):
        row = fixture_for('Sangal', 'Aurora YB')
        row['id'] = '9999999'
        research_rank_pick(row)
        self.assertEqual((row['pick'], row['method']), ('Sangal', 'research_rank_single'))
        self.assertIsNone(row['probabilities'])


class FinalDayResultsTests(unittest.TestCase):
    def test_verified_scores_and_sources(self):
        results = NOTES['day_five_results']
        by_pair = {(m['winner'], m['loser']): m for m in results['matches']}
        self.assertEqual(by_pair[('Aurora', 'Falcons')]['score'], '2-1')
        self.assertEqual(by_pair[('FURIA', 'BETBOOM')]['score'], '3-2')
        self.assertEqual(by_pair[('Aurora', 'Falcons')]['maps'],
                         'Anubis 8-13, Dust2 19-17, Nuke 13-9')
        self.assertEqual(by_pair[('FURIA', 'BETBOOM')]['maps'],
                         'Dust2 13-6, Ancient 16-19, Nuke 9-13, Mirage 13-11, Cache 13-6')
        for match in results['matches']:
            self.assertTrue(match['match_url'].startswith('https://www.hltv.org/matches/'))
            self.assertTrue(match['report_url'].startswith('https://www.hltv.org/results'))
        self.assertEqual(results['results_url'], 'https://www.hltv.org/results?event=8932')

    def test_pick_outcomes_match_the_pre_lock_board(self):
        rows = {r['board_pick']: r for r in NOTES['day_five_results']['pick_outcomes']['rows']}
        self.assertEqual(rows['Falcons']['board_probability'], 60.5)
        self.assertEqual(rows['Falcons']['result'], 'lost')
        self.assertEqual(rows['FURIA']['board_probability'], 70.5)
        self.assertEqual(rows['FURIA']['result'], 'won')
        self.assertIn('not a calibrated accuracy claim',
                      NOTES['day_five_results']['pick_outcomes']['summary'])

    def test_archived_guide_cannot_say_today(self):
        guide = NOTES['day_five_guidance']
        self.assertTrue(guide['archived'])
        self.assertNotIn('TODAY', guide['summary'])
        self.assertNotIn('TODAY', guide['card'])
        self.assertIn('event is now complete', guide['summary'])
        # Historical pre-lock prices stay visible as a dated record.
        self.assertIn('70.5%', guide['not_listed'][1]['pick_detail'])

    def test_analysis_page_renders_results_before_the_archived_guide(self):
        html = build.analysis_page(LATEST)
        soup = BeautifulSoup(html, 'html.parser')
        self.assertIsNotNone(soup.select_one('#day-five-results'))
        self.assertIsNotNone(soup.select_one('#day-five-guidance'))
        text = soup.get_text(' ', strip=True)
        self.assertIn('Aurora beat Falcons', text)
        self.assertIn('FURIA beat BETBOOM', text)
        self.assertIn('Pre-lock board picks on the final day', text)
        self.assertIn('2-1', text)
        self.assertIn('3-2', text)
        self.assertLess(html.find('id="day-five-results"'), html.find('id="day-five-guidance"'))
        self.assertIn('TWC 2026: every result, and what decided it.', text)

    def test_homepage_points_at_final_results_and_five_tabs(self):
        html = build.page('index', 'Executive summary', build.overview(LATEST), LATEST)
        self.assertIn('href="analysis.html#day-five-results"', html)
        self.assertIn('TWC final results', html)
        self.assertIn('href="picks.html"', html)
        self.assertIn('href="unresolved.html"', html)
        self.assertNotIn('Final day is TODAY', html)
        self.assertNotIn('Day-5 final-day guide ↗', html)
        soup = BeautifulSoup(html, 'html.parser')
        tabs = soup.select_one('nav.mobile-tabs')
        self.assertIsNotNone(tabs)
        labels = [''.join(a.stripped_strings) for a in tabs.select('a')]
        self.assertEqual(labels, ['Home', 'Picks', 'Unresolved', 'Matches', 'TWC'])
        # Sources and Review remain reachable in the footer on a phone.
        footer = soup.select_one('footer')
        footer_html = str(footer)
        self.assertIn('href="review.html"', footer_html)
        self.assertIn('href="sources.html"', footer_html)


if __name__ == '__main__':
    unittest.main()
