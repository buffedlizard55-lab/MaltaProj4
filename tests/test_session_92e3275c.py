"""Session 92e3275c regressions: a pick for every open fixture, from a sourced line.

Two changes are pinned here, and neither invents a number.

1. ``data/identities.json`` registers the Tropa do KinGui / Projeto do KinGui
   label pair for Hotspawn fixture 1082919. That fixture was the only open row
   on the 22 October board with no pick at all, because Hotspawn spells the team
   "Projeto do KinGui" while HLTV and Polymarket spell it "Tropa do KinGui".
   The mapping rests on fixture parity **and** a five-for-five lineup agreement,
   recorded in the register with both primary links; the tests below also pin
   the refusals, so the alias cannot be widened into fuzzy matching.

2. ``scripts/refresh.py`` reads HLTV's dated Valve ranking **before** the
   per-fixture HLTV sweep. The mirror tier used to be read last, by which point
   the run had already earned a rate-limit 403 that blocks the host for the rest
   of the run, so the tier never published. The read-only probe in this session
   (``scripts/probe_92e3275c.py``, run 39742112362) recorded the page answering
   200 with 1.6 MB to this project's own User-Agent, which is why this is a
   pacing fix and not an access claim.
"""
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.core import norm, plain_name, polymarket_candidates, resolve

ROOT = Path(__file__).resolve().parents[1]
IDENTITIES = json.loads((ROOT / 'data/identities.json').read_text())
SNAPSHOT = json.loads((ROOT / 'data/latest.json').read_text())
FIXTURE_ID = '1082919'

START = '2026-10-22T13:00:00Z'
NOW = datetime(2026, 10, 22, 8, 10, tzinfo=timezone.utc)


def entry():
    found = [e for e in IDENTITIES['aliases'] if e['canonical'] == 'Tropa do KinGui']
    assert len(found) == 1, 'exactly one register entry for this pair'
    return found[0]


def market_event(teams=('Tropa do KinGui', 'Martians'), start='2026-10-22 13:00:00+00',
                 prices=('0.75', '0.25'), bid='0.54', ask='0.96',
                 updated='2026-10-22T07:42:57.621734Z', liquidity='156.0392',
                 accepting=True, closed=False):
    return {'id': 'x', 'slug': 'cs2-tdkg-mar1-2026-10-22', 'sport': {'sport': 'cs2'},
            'closed': False, 'live': False, 'ended': False,
            'teams': [{'name': teams[0], 'abbreviation': 'TDK'},
                      {'name': teams[1], 'abbreviation': 'MAR'}],
            'markets': [{'id': '6033256',
                         'question': 'Counter-Strike: %s vs %s (BO3) - CCT South America Series 7 Playoffs' % teams,
                         'sportsMarketType': 'moneyline',
                         'outcomes': json.dumps(list(teams)),
                         'outcomePrices': json.dumps(list(prices)),
                         'gameStartTime': start, 'eventStartTime': '2026-10-22T13:00:00Z',
                         'updatedAt': updated, 'active': True,
                         'closed': closed, 'acceptingOrders': accepting,
                         'bestBid': bid, 'bestAsk': ask,
                         'liquidity': liquidity, 'volume': '10'}]}


def fixture(teams=('Projeto do KinGui', 'Martians'), start=START, best_of=3):
    return {'id': FIXTURE_ID, 'teams': list(teams), 'state': 'open', 'start': start,
            'lock': '2026-10-22T12:54:00Z', 'best_of': best_of, 'probabilities': None,
            'fair_odds': None, 'pick': None, 'method': None, 'evidence': [],
            'attempts': [], 'flags': [], 'reason': None}


class TestKinGuiIdentity(unittest.TestCase):
    def test_entry_lists_both_labels_with_primary_sources(self):
        item = entry()
        self.assertEqual(sorted(plain_name(n) for n in item['names']),
                         sorted({plain_name('Tropa do KinGui'), plain_name('Projeto do KinGui'),
                                 plain_name('ex-Keyd Stars')}))
        self.assertEqual(item['source'],
                         'https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7')
        # Main #176 independently verified the ex-Keyd core and retained the
        # exact market in this legacy slot; EGW is an explicit corroboration.
        # Require all three labels and both exact links, not a smaller old set.
        self.assertEqual(item['additional_source'], 'https://gamma-api.polymarket.com/markets/6033256')
        self.assertIn('https://egamersworld.com/counterstrike/match/0U32SId-H/projeto-do-kingui-vs-martians-esports-3j3hkufF0',
                      [source['url'] for source in item['corroboration']])
        for needle in ('five players', 'ALLE', 'ckzao', 'drg', 'xureba', 'lash',
                       'HLTV: Unranked', 'Polymarket market 6033256', '13:00Z'):
            self.assertIn(needle, item['basis'], needle)

    def test_basis_records_the_roster_discrepancy_instead_of_hiding_it(self):
        self.assertIn('team-overview page for id 13151 still prints an older roster', entry()['basis'])

    def test_both_labels_normalise_to_one_key(self):
        self.assertEqual(norm('Projeto do KinGui'), norm('Tropa do KinGui'))

    def test_alias_does_not_absorb_other_teams(self):
        for label in ('Martians', 'KinGui', 'Tropa do KinGui Academy', 'UNO MILLE'):
            self.assertNotEqual(norm(label), norm('Tropa do KinGui'), label)

    def test_the_committed_board_shows_why_the_row_was_blocked(self):
        """The committed snapshot predates this register change.

        It therefore still shows fixture 1082919 unpriced, and its attempts
        record exactly the gap this alias closes: Polymarket and HLTV both
        returned the fixture under the label "Tropa do KinGui" and the resolver
        refused to map it by name shape. Once a refresh runs with this register,
        the same row is priced by the exchange tier (asserted in
        ``TestWideTierThroughTheAlias``); the board itself is asserted by the
        publication gates, not by this historical snapshot.
        """
        row = next((m for m in SNAPSHOT['matches'] if m['id'] == FIXTURE_ID), None)
        if row is None:
            self.skipTest('fixture is no longer in the retained snapshot')
        self.assertEqual(row['state'], 'open')
        if row.get('probabilities') is not None:
            self.assertIn(row['method'], ('exchange', 'exchange_wide'))
            self.assertTrue(row['pick'])
            return
        labels = set()
        for attempt in row['attempts']:
            for candidate in attempt.get('candidates') or []:
                labels.update(candidate.get('teams') or [])
        self.assertIn('Tropa do KinGui', labels,
                      'the pre-alias row must record the label gap, not a silence')


class TestWideTierThroughTheAlias(unittest.TestCase):
    def test_alias_lets_the_exchange_line_price_the_fixture(self):
        f = fixture()
        resolve(f, polymarket_candidates([market_event()], '2026-10-22T08:06:00Z'),
                'Polymarket', NOW, relax=True)
        self.assertEqual(f['method'], 'exchange_wide', 'wide tier must be labelled as such')
        self.assertEqual(f['pick'], 'Projeto do KinGui')
        self.assertAlmostEqual(f['probabilities'][0], 0.75, places=9)
        self.assertAlmostEqual(f['probabilities'][1], 0.25, places=9)
        self.assertTrue(any('wide' in flag.lower() for flag in f['flags']),
                        'a 42-point spread has to be published as low confidence')

    def test_a_different_start_is_still_refused(self):
        f = fixture()
        resolve(f, polymarket_candidates([market_event(start='2026-10-22 17:00:00+00')],
                                         '2026-10-22T08:06:00Z'), 'Polymarket', NOW, relax=True)
        self.assertIsNone(f['probabilities'])
        self.assertIsNone(f['method'])

    def test_a_different_opponent_is_still_refused(self):
        f = fixture()
        resolve(f, polymarket_candidates([market_event(teams=('Tropa do KinGui', 'Isurus'))],
                                         '2026-10-22T08:06:00Z'), 'Polymarket', NOW, relax=True)
        self.assertIsNone(f['probabilities'])

    def test_thin_liquidity_is_never_accepted_even_wide(self):
        f = fixture()
        resolve(f, polymarket_candidates([market_event(liquidity='42.0')],
                                         '2026-10-22T08:06:00Z'), 'Polymarket', NOW, relax=True)
        self.assertIsNone(f['probabilities'])

    def test_stale_update_is_refused(self):
        f = fixture()
        resolve(f, polymarket_candidates([market_event(updated='2026-10-22T00:00:00Z')],
                                         '2026-10-22T08:06:00Z'), 'Polymarket', NOW, relax=True)
        self.assertIsNone(f['probabilities'])

    def test_equal_exchange_prices_have_no_directional_edge(self):
        # A genuine 50/50 exchange quote is not an error, but it must not be
        # dressed up as a pick: the documented result is "no directional edge".
        # (The book-listing placeholder pair 1.8/1.8 is refused earlier, in
        # scripts/books.py, and never reaches this path.)
        f = fixture()
        resolve(f, polymarket_candidates([market_event(prices=('0.5', '0.5'),
                                                      bid='0.49', ask='0.51')],
                                         '2026-10-22T08:06:00Z'), 'Polymarket', NOW, relax=True)
        self.assertIsNone(f['pick'])
        self.assertIn('no directional edge', (f['reason'] or '').lower())


class TestMirrorReadOrder(unittest.TestCase):
    def test_refresh_reads_the_valve_mirror_before_the_per_fixture_sweep(self):
        source = (ROOT / 'scripts/refresh.py').read_text()
        early = source.index('Read HLTV\'s dated Valve ranking FIRST')
        sweep = source.index("from scripts.hltv import research")
        late = source.index('mirror_open = [m for m in open_matches')
        self.assertLess(early, sweep, 'the mirror read must come before the HLTV sweep')
        self.assertLess(sweep, late)
        # The late block consumes the early result and never re-fetches inside a
        # host the run may already have blocked.
        tail = source[late:]
        self.assertIn('mirror_standings', tail)
        self.assertNotIn('vrs_mirror.fetch(src', tail)

    def test_a_probe_report_exists_for_the_access_claim(self):
        probe = (ROOT / 'scripts/probe_92e3275c.py').read_text()
        for url in ('https://www.hltv.org/valve-ranking/teams',
                    'https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12'):
            self.assertIn(url, probe)
        self.assertIn("'Hotspawn-CS2-Research/1.0", probe, 'the probe must send this project\'s own User-Agent')


if __name__ == '__main__':
    unittest.main()
