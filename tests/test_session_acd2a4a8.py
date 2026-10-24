"""Session acd2a4a8 (2026-10-24): an exactly even line must not strand a match.

Measured cause: on the 2026-10-24T16:30Z harvest, fixture 1079200
(Color vs ex-Zero Tenacity, NODWIN Clutch Series #13) carried a newly opened
Polymarket market at outcomePrices 0.5/0.5, bestBid 0.49 / bestAsk 0.51, no
volume. The collector published probabilities [0.5, 0.5] with pick=None
("Equal verified prices; no directional edge"). The board contracts forbid
that state (a priced row must carry its larger side as the pick; a 50/50 is
never a published probability), so the publisher's root-fallback gate failed
on the whole fresh snapshot (42 unit failures in the staged-root replay) and
scheduled run 40097410704 could not publish any new board.

Policy, extending session ce45f672's wide-tier rule to every tier: an exactly
even quote -- exchange, bookmaker, researched book listing, or our own VRS
model/mirror -- is recorded as rejected evidence with the reason on the row's
attempts, and the fallback ladder continues (HLTV first, then esportsbook
lines, then the originated VRS model, then the HLTV research tiers). A row
that no tier can separate stays unresolved with its limitation published in
the executive summary's unresolved section; no 50/50 is ever printed.
"""
import unittest
from datetime import datetime, timedelta, timezone

from scripts.core import book_research_pick, iso, normalize_fixtures
from scripts import vrs

NOW = datetime.now(timezone.utc).replace(microsecond=0)
START = NOW + timedelta(hours=5)


def open_row(team_a='Alpha', team_b='Beta'):
    raw = {'id': 'R1', 'sport_alias': 'cs2', 'participants0_name': team_a,
           'participants1_name': team_b, 'participants0_id': 'a', 'participants1_id': 'b',
           'status': 'scheduled', 'scheduled_start_time': iso(START),
           'lock_time': iso(START - timedelta(minutes=6)),
           'competition_name': 'Test Cup', 'tier': 'b'}
    row = normalize_fixtures([raw], {}, NOW)[0]
    row.update(probabilities=None, fair_odds=None, pick=None, method=None,
               evidence=[], flags=[], attempts=[], reason=None)
    return row


def book_receipt(**over):
    base = {
        'provider': 'EGamersWorld book listing',
        'id': 'egw-test-alpha-beta',
        'fixture_id': 'R1',
        'source_teams': ['Alpha', 'Beta'],
        'team_aliases': [['Alpha'], ['Beta']],
        'alias_sources': ['https://www.hltv.org/matches/2399590/x',
                          'https://www.hltv.org/matches/2399590/x'],
        'start': iso(START),
        'best_of': 1,
        'odds': [1.9, 1.9],
        'observed_at': iso(NOW),
        'url': 'https://egamersworld.com/counterstrike/match/test',
        'api_url': 'https://egamersworld.com/counterstrike/match/test',
        'event': 'Test Cup',
    }
    base.update(over)
    return base


class EvenBookListingFallsThrough(unittest.TestCase):
    def test_equal_researched_line_is_rejected_evidence(self):
        row = open_row()
        book_research_pick(row, receipts=[book_receipt()], now=NOW)
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['pick'])
        self.assertIsNone(row['method'])
        self.assertTrue(any(a.get('provider') == 'Book research'
                            and a.get('status') == 'unresolved'
                            and 'exactly even' in (a.get('reason') or '')
                            for a in row['attempts']))

    def test_directional_researched_line_still_prices(self):
        row = open_row()
        book_research_pick(row, receipts=[book_receipt(odds=[1.39, 2.65])], now=NOW)
        self.assertEqual(row['method'], 'bookmaker_fallback')
        self.assertEqual(row['pick'], 'Alpha')
        self.assertGreater(row['probabilities'][0], row['probabilities'][1])


class EvenModelLineFallsThrough(unittest.TestCase):
    def test_equal_vrs_points_publish_no_model_line(self):
        row = open_row()
        standings = {'as_of': '2026-10-05', 'teams': [
            {'name': 'Alpha', 'standing': 10, 'points': 500, 'roster': [],
             'details': 'alpha'},
            {'name': 'Beta', 'standing': 20, 'points': 500, 'roster': [],
             'details': 'beta'},
        ]}
        meta = {'raw_url': 'https://raw.githubusercontent.com/ValveSoftware/counter-strike/main/standings.json',
                'blob_url': 'https://github.com/ValveSoftware/counter-strike/blob/main/standings.json',
                'observed_at': iso(NOW), 'commit': 'abc', 'file': 'standings.json',
                'origin': 'Valve', 'details_base': 'https://github.com/ValveSoftware/counter-strike/'}
        vrs.apply(row, standings, meta)
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['pick'])
        self.assertIsNone(row['method'])
        self.assertTrue(any('Equal model estimate' in (a.get('reason') or '')
                            for a in row['attempts']))


if __name__ == '__main__':
    unittest.main()
