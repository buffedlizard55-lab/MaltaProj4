"""Session 84295759: a priced pick for the last unpriced fixture, and a
freshness-first executive summary.

Two claims are pinned here, both read on 2026-10-21 UTC and recorded in
research/session-84295759/REPORT.md:

* Hotspawn's ``flacons`` and Polymarket's ``Team flacons`` are one club for the
  exact fixture 1082763 (UPGRADE vs flacons, WINLINE MPKBK CIS LAN Season 9
  Group C, 2026-10-21T15:00:00Z). HLTV team page 13932 carries the label
  ``flacons``; market 5971986 carries ``Team flacons`` at the same UTC start and
  names hltv.org as its resolution source. The mapping is a label alias only: the
  resolver still requires the exact opponent pair and UTC start before any price
  is read, and the register's other entries are untouched.
* The executive summary answers "is this current, and where are the picks?"
  before the hero: a freshness strip with the snapshot time, the published
  re-check cadence, the open-match coverage counts and direct links to the pick
  board. A snapshot outside its eight-hour evidence window is marked stale in
  the markup, so a delayed refresh can never look like a live board.
"""
from __future__ import annotations

import copy
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from scripts.build import fresh_strip, next_check, overview
from scripts.core import (IDENTITIES, iso, norm, normalize_fixtures,
                          polymarket_candidates, resolve)

ROOT = Path(__file__).resolve().parents[1]

# Frozen clock: the fixture start is fixed by Hotspawn's own feed, so pinning the
# observation keeps this regression deterministic after the match has passed.
OBSERVED = datetime(2026, 10, 21, 12, 47, tzinfo=timezone.utc)
START = '2026-10-21T15:00:00Z'

HLTV_MATCH = ('https://www.hltv.org/matches/2399840/'
              'upgrade-vs-flacons-winline-mpkbk-cis-lan-season-9')
POLYMARKET_MARKET = 'https://gamma-api.polymarket.com/markets/5971986'


def fixture(team_a: str, team_b: str, fixture_id: str = '1082763') -> dict:
    raw = {'id': fixture_id, 'sport_alias': 'cs2', 'participants0_name': team_a,
           'participants1_name': team_b, 'participants0_id': '13989',
           'participants1_id': '13932', 'status': 'scheduled',
           'scheduled_start_time': START, 'lock_time': '2026-10-21T14:54:00Z',
           'competition_name': 'CIS LAN Championship #9', 'tier': 'c', 'best_of': 3}
    row = normalize_fixtures([raw], {}, OBSERVED)[0]
    row.update(probabilities=None, fair_odds=None, pick=None, method=None,
               evidence=[], flags=[], attempts=[], reason=None)
    return row


def market_candidate(outcomes, prices, start='2026-10-21 15:00:00+00'):
    """The Polymarket market 5971986 record as read on 2026-10-21T12:34:58Z."""
    event = {'id': 'evt-flacons', 'slug': 'cs2-upgrad-tf4-2026-10-21',
             'sport': {'sport': 'cs2'}, 'closed': False, 'live': False, 'ended': False,
             'teams': [{'name': 'UPGRADE'}, {'name': 'Team flacons'}],
             'markets': [{'id': '5971986', 'sportsMarketType': 'moneyline',
                          'question': 'Counter-Strike: UPGRADE vs Team flacons (BO3) - CIS LAN Championship Group C',
                          'outcomes': json.dumps(outcomes),
                          'outcomePrices': json.dumps(prices),
                          'gameStartTime': start,
                          'eventStartTime': '2026-10-21T15:00:00Z',
                          'updatedAt': '2026-10-21T12:34:58Z',
                          'active': True, 'closed': False, 'acceptingOrders': True,
                          'bestBid': 0.95, 'bestAsk': 0.96,
                          'liquidity': 2954.121, 'volume': 100}]}
    return polymarket_candidates([event], iso(OBSERVED))


class FlaconsIdentityTests(unittest.TestCase):
    def setUp(self):
        self.entry = next(a for a in IDENTITIES if a['canonical'] == 'flacons')

    def test_register_entry_is_narrow_and_sourced(self):
        self.assertEqual(self.entry['names'], ['flacons', 'Team flacons'])
        self.assertEqual(self.entry['source'], HLTV_MATCH)
        self.assertEqual(self.entry['additional_source'], POLYMARKET_MARKET)
        self.assertEqual(norm('Team flacons'), norm('flacons'))
        # The mapping must not swallow other teams or invent roster continuity.
        self.assertNotEqual(norm('Team flacons'), norm('Falcons'))
        self.assertIn('exact opponent pair and UTC start', self.entry['basis'])

    def test_exact_fixture_now_prices_from_the_exchange(self):
        row = fixture('UPGRADE', 'flacons')
        resolve(row, market_candidate(['UPGRADE', 'Team flacons'], ['0.955', '0.045']),
                'Polymarket', OBSERVED)
        self.assertEqual(row['pick'], 'UPGRADE')
        self.assertEqual(row['method'], 'exchange')
        self.assertAlmostEqual(row['probabilities'][0], 0.955, places=4)
        self.assertAlmostEqual(row['probabilities'][1], 0.045, places=4)
        self.assertEqual(row['attempts'][0]['status'], 'resolved')
        self.assertIsNone(row['reason'])

    def test_alias_never_bypasses_the_exact_start(self):
        row = fixture('UPGRADE', 'flacons')
        resolve(row, market_candidate(['UPGRADE', 'Team flacons'], ['0.955', '0.045'],
                                      start='2026-10-21 16:00:00+00'),
                'Polymarket', OBSERVED)
        self.assertIsNone(row['pick'])
        self.assertIsNone(row['probabilities'])
        self.assertEqual(row['attempts'][0]['status'], 'unresolved')

    def test_alias_does_not_price_a_different_opponent(self):
        row = fixture('Zetta', 'LOS NINOS', fixture_id='1082837')
        resolve(row, market_candidate(['UPGRADE', 'Team flacons'], ['0.955', '0.045']),
                'Polymarket', OBSERVED)
        self.assertIsNone(row['pick'])
        self.assertIsNone(row['probabilities'])


class FreshnessStripTests(unittest.TestCase):
    def test_next_slot_follows_the_published_cadence(self):
        cases = {
            datetime(2026, 10, 21, 12, 41, tzinfo=timezone.utc): '12:49',
            datetime(2026, 10, 21, 12, 47, tzinfo=timezone.utc): '12:49',
            datetime(2026, 10, 21, 13, 5, tzinfo=timezone.utc): '13:19',
            datetime(2026, 10, 21, 13, 50, tzinfo=timezone.utc): '14:04',
        }
        for captured, expected in cases.items():
            self.assertEqual(next_check(iso(captured)).strftime('%H:%M'), expected)

    def test_live_snapshot_states_coverage_and_links(self):
        snapshot = datetime.now(timezone.utc).replace(microsecond=0)
        row = 'row'
        soup = BeautifulSoup(fresh_strip({'last_attempt_at': iso(snapshot), 'fixtures_observed_at': iso(snapshot)},
                                         [row, row, row], [row, row], [row], []), 'html.parser')
        strip = soup.select_one('#freshness-strip')
        self.assertIn('fresh-strip', strip['class'])
        self.assertNotIn('stale', strip['class'])
        text = strip.get_text(' ', strip=True)
        self.assertIn('Last checked', text)
        self.assertIn('3 open CS2 match(es)', text)
        self.assertIn('3 with a pick', text)
        self.assertIn('0 unresolved', text)
        self.assertIn(':04, :19, :34 and :49', text)
        hrefs = {a['href'] for a in strip.select('a[href]')}
        self.assertEqual(hrefs, {'picks.html', '#picks-at-a-glance', 'unresolved.html'})

    def test_expired_snapshot_is_marked_stale(self):
        old = datetime.now(timezone.utc) - timedelta(hours=9)
        strip = BeautifulSoup(fresh_strip({'last_attempt_at': iso(old), 'fixtures_observed_at': iso(old)}, ['x'], [], [], ['y']),
                              'html.parser').select_one('#freshness-strip')
        self.assertIn('stale', strip['class'])
        self.assertIn('older than 8 hours', strip.get_text(' ', strip=True))

    def test_strip_sits_before_the_hero_and_the_cards(self):
        data = json.loads((ROOT / 'data/latest.json').read_text())
        html = overview(copy.deepcopy(data))
        self.assertLess(html.find('id="freshness-strip"'), html.find('class="hero"'))
        # The four destination cards are reachable before the long glance list.
        self.assertLess(html.find('id="start-here"'), html.find('id="picks-at-a-glance"'))

    def test_unresolved_notice_links_once(self):
        data = json.loads((ROOT / 'data/latest.json').read_text())
        soup = BeautifulSoup(overview(copy.deepcopy(data)), 'html.parser')
        notice = soup.select_one('#twc-unpriced')
        if notice is None:
            self.skipTest('bootstrap snapshot carries no unpriced final-day research block')
        labels = [a.get_text(strip=True) for a in notice.select('a[href="unresolved.html"]')]
        self.assertEqual(labels.count('All non-market rows →'), 1)


if __name__ == '__main__':
    unittest.main()
