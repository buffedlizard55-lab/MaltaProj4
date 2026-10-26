"""Session 32efbb66: a pick for every open match - the Kalshi exchange tier.

What this suite proves, and why
-------------------------------
The user requirement is a pick for *every* Hotspawn CS2 match, including the
low-tier fixtures Polymarket never lists. The ladder already fell through
HLTV, Pinnacle, a wide Polymarket quote, BO3.gg/Thunderpick book lines, our
own Valve-standings model and three qualitative research tiers; a row could
still end blank when no venue priced it and a club had no Valve/HLTV
footprint. This session measured Kalshi's public no-auth market-data API on
a GitHub runner (run 40251306187, 2026-10-26; payload retained at
``research/session-32efbb66/kalshi-markets.json``): the KXCS2GAME series
listed 58 match events, 15 of them exact opponent pairs for the 19 then-open
Hotspawn fixtures, 13 joining on the exact UTC start.

The dangerous part is identity. Kalshi's market record has no
machine-readable scheduled start, and ``occurrence_datetime`` is *not* one
(measured: contract-stated start + 4h on the 13 joins). The adapter derives
the start only from the contract's own ``rules_primary`` sentence with an
explicit EST/EDT offset, cross-checked against the wall-clock time encoded
in the event ticker. These tests pin that behaviour against the retained
real payload and against single-field mutations of it:

* every real event becomes exactly one candidate, with a proven start;
* the two measured same-pair/other-start fixtures (1079203 Metizport vs
  BRUTE, 1079202 FOKUS vs ex-Zero Tenacity) do NOT join - no start is ever
  "corrected";
* a real tight book de-vigs by hand-checkable arithmetic, and Kalshi's own
  0.06/0.94 placeholder books are refused by the spread and liquidity gates;
* any single mutation of the structural contract (rules/ticker disagreement,
  ambiguous timezone, missing full-match definition, closed market, a third
  market) drops the candidate instead of being interpreted;
* a stored Kalshi quote round-trips through the independent validator
  (``reconstruct_quote`` + calculator replay) and the independent c6 row
  audit, with a numeric best-of on the fixture proving the full-match
  format-evidence path - and the retained pre-adapter snapshot still
  validates unchanged.
"""
import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.core import (
    calculator_for, kalshi_candidates, normalize_fixtures, orientation,
    pick_deadline, quote_kalshi, resolve,
)
from scripts.validate import reconstruct_quote, validate_data

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / 'research' / 'session-32efbb66'
OBSERVED = '2026-10-26T00:50:00Z'
NOW = datetime(2026, 10, 26, 1, 20, tzinfo=timezone.utc)


def load(name):
    return json.loads((SESSION / name).read_text())


def event(candidates, suffix):
    hits = [c for c in candidates if c['id'].endswith(suffix)]
    assert len(hits) == 1, suffix
    return hits[0]


class KalshiCandidatesFromRealBytes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.markets = load('kalshi-markets.json')
        cls.snapshot = load('snapshot.json')
        cls.candidates = kalshi_candidates(cls.markets, OBSERVED)

    def test_every_real_event_becomes_one_candidate(self):
        events = {m['event_ticker'] for m in self.markets}
        self.assertEqual(len(events), 58)
        self.assertEqual({c['id'] for c in self.candidates}, events)
        for c in self.candidates:
            self.assertEqual(c['provider'], 'Kalshi')
            self.assertEqual(c['format_evidence'], 'kalshi_full_match_rules')
            self.assertIsNone(c['best_of'])
            self.assertEqual(len(c['teams']), 2)
            self.assertEqual(len(set(c['teams'])), 2)
            # The derived start is a whole minute in UTC, never the
            # occurrence buffer the venue also publishes.
            self.assertTrue(c['start'].endswith(':00Z'), c['start'])
            raw_occurrence = {m['occurrence_datetime'] for m in c['markets']}
            self.assertNotIn(c['start'], raw_occurrence)

    def test_thirteen_measured_fixtures_join_exactly(self):
        by_id = {m['id']: m for m in self.snapshot['matches']}
        joined = []
        for fixture_id in ('1082859', '1082858', '1079201', '1081160', '1082861',
                           '1082860', '1082897', '1082898', '1081162', '1081163',
                           '1082900', '1081164', '1082901'):
            fixture = by_id[fixture_id]
            hits = [c for c in self.candidates
                    if orientation(fixture, c['teams'], c['start']) is not None]
            self.assertEqual(len(hits), 1, fixture_id)
            joined.append(fixture_id)
        self.assertEqual(len(joined), 13)

    def test_same_pair_other_start_stays_refused(self):
        # Measured source disagreements: Kalshi states 12:00Z where Hotspawn
        # states 15:00Z (1079203) and 18:00Z where Hotspawn states 12:00Z
        # (1079202). An assumed start correction is exactly what this project
        # refuses, so neither may join.
        by_id = {m['id']: m for m in self.snapshot['matches']}
        for fixture_id in ('1079203', '1079202'):
            fixture = by_id[fixture_id]
            hits = [c for c in self.candidates
                    if orientation(fixture, c['teams'], c['start']) is not None]
            self.assertEqual(hits, [], fixture_id)


class KalshiQuoteGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidates = kalshi_candidates(load('kalshi-markets.json'), OBSERVED)

    def test_real_tight_book_devigs_from_both_mids(self):
        candidate = event(self.candidates, 'AENEX')  # NEXVOID vs Alter Ego
        order = [0, 1] if candidate['teams'][0] == 'NEXVOID' else [1, 0]
        expected = []
        for m in candidate['markets']:
            expected.append((float(m['yes_bid_dollars']) + float(m['yes_ask_dollars'])) / 2)
        quote = quote_kalshi(candidate, order, NOW)
        for got, mid in zip((quote['probabilities'][order.index(0)],
                             quote['probabilities'][order.index(1)]), expected):
            self.assertAlmostEqual(got, mid / sum(expected), places=12)
        self.assertAlmostEqual(sum(quote['probabilities']), 1.0, places=12)
        self.assertLessEqual(quote['spread'], 0.04 + 1e-9)
        self.assertGreaterEqual(quote['liquidity'], 50)
        self.assertIsNone(quote['updated_at'])
        self.assertEqual(quote['tier'], 'exchange')

    def test_placeholder_books_are_refused(self):
        # Kalshi seeds unfancied fixtures at 0.06/0.94 with no interest:
        # HAVU (0.67/0.73 spreads) and BakS (0.88/0.88) on the real capture.
        for suffix in ('ILLHAVU', 'SSINSBAKS', 'LAVINN', 'TSAEXR'):
            candidate = event(self.candidates, suffix)
            with self.assertRaises(ValueError, msg=suffix):
                quote_kalshi(candidate, [0, 1], NOW)

    def test_thin_top_of_book_is_refused(self):
        candidate = copy.deepcopy(event(self.candidates, 'AENEX'))
        for m in candidate['markets']:
            m['yes_bid_size_fp'] = '1.00'
            m['yes_ask_size_fp'] = '1.00'
            m['open_interest_fp'] = '0.00'
        with self.assertRaisesRegex(ValueError, 'liquidity'):
            quote_kalshi(candidate, [0, 1], NOW)

    def test_inconsistent_mid_sum_is_refused(self):
        candidate = copy.deepcopy(event(self.candidates, 'AENEX'))
        candidate['markets'][0]['yes_bid_dollars'] = '0.7000'
        candidate['markets'][0]['yes_ask_dollars'] = '0.7400'
        with self.assertRaisesRegex(ValueError, 'inconsistent'):
            quote_kalshi(candidate, [0, 1], NOW)

    def test_stale_observation_is_refused(self):
        candidate = event(self.candidates, 'AENEX')
        later = datetime(2026, 10, 26, 9, 0, tzinfo=timezone.utc)  # +8h10m
        with self.assertRaisesRegex(ValueError, 'eight hours'):
            quote_kalshi(candidate, [0, 1], later)


class KalshiIdentityRefusals(unittest.TestCase):
    """One mutation at a time: the candidate must disappear, not degrade."""

    @classmethod
    def setUpClass(cls):
        cls.markets = load('kalshi-markets.json')

    def one_event(self):
        return [copy.deepcopy(m) for m in self.markets
                if m['event_ticker'].endswith('AENEX')]

    def assert_dropped(self, markets):
        self.assertEqual(kalshi_candidates(markets, OBSERVED), [])

    def test_rules_time_disagreeing_with_ticker(self):
        markets = self.one_event()
        for m in markets:
            m['rules_primary'] = m['rules_primary'].replace('11:00 PM', '10:00 PM')
        self.assert_dropped(markets)

    def test_ambiguous_timezone_abbreviation(self):
        markets = self.one_event()
        for m in markets:
            m['rules_primary'] = m['rules_primary'].replace('EDT', 'ET')
        self.assert_dropped(markets)

    def test_full_match_definition_removed(self):
        markets = self.one_event()
        markets[0]['rules_secondary'] = markets[0]['rules_secondary'].replace(
            'refers to the full match', 'refers to map one')
        self.assert_dropped(markets)

    def test_closed_market(self):
        markets = self.one_event()
        markets[1]['status'] = 'closed'
        self.assert_dropped(markets)

    def test_third_market_in_event(self):
        markets = self.one_event()
        extra = copy.deepcopy(markets[0])
        extra['ticker'] += '-X'
        self.assert_dropped(markets + [extra])

    def test_title_not_a_team_wins_market(self):
        markets = self.one_event()
        markets[0]['title'] = markets[0]['yes_sub_title'] + ' wins map 1'
        self.assert_dropped(markets)

    def test_opponent_not_named_in_contract_text(self):
        markets = self.one_event()
        other = markets[1]['yes_sub_title']
        markets[0]['rules_primary'] = markets[0]['rules_primary'].replace(other, 'TBD')
        self.assert_dropped(markets)


RAW_ROW = {
    'id': '9999999', 'sport_alias': 'cs2',
    'participants0_name': 'NEXVOID', 'participants1_name': 'Alter Ego',
    'participants0_id': 101, 'participants1_id': 102,
    'competition_name': 'DFRAG Invitational 2026', 'tier': 'b', 'best_of': 3,
    'scheduled_start_time': '2026-10-26T03:00:00Z',
    'lock_time': '2026-10-26T02:55:00Z', 'status': 'scheduled',
}


class KalshiRoundTrip(unittest.TestCase):
    """A stored Kalshi quote must replay through every independent gate."""

    @classmethod
    def setUpClass(cls):
        cls.candidates = kalshi_candidates(load('kalshi-markets.json'), OBSERVED)

    def priced_fixture(self):
        fixture = normalize_fixtures([copy.deepcopy(RAW_ROW)], {}, NOW)[0]
        self.assertEqual(fixture['state'], 'open')
        resolve(fixture, self.candidates, 'Kalshi', NOW)
        return fixture

    def test_resolve_prices_and_picks_the_favourite(self):
        fixture = self.priced_fixture()
        # Real book at capture: NEXVOID 0.55/0.59, Alter Ego 0.43/0.45.
        self.assertEqual(fixture['method'], 'exchange')
        self.assertEqual(fixture['pick'], 'NEXVOID')
        self.assertIsNotNone(fixture['probabilities'])
        self.assertEqual(fixture['evidence'][0]['provider'], 'Kalshi')
        attempt = [a for a in fixture['attempts'] if a['provider'] == 'Kalshi']
        self.assertEqual(attempt[0]['status'], 'resolved')

    def test_validator_reconstructs_and_replays_the_quote(self):
        fixture = self.priced_fixture()
        quote = fixture['evidence'][0]
        candidate = reconstruct_quote(quote, schema_version=2)
        order = orientation(fixture, candidate['teams'], candidate['start'])
        self.assertIsNotNone(order)
        replay = calculator_for('Kalshi')(candidate, order, NOW)
        for stored, fresh in zip(quote['probabilities'], replay['probabilities']):
            self.assertAlmostEqual(stored, fresh, places=12)
        self.assertEqual(quote['spread'], replay['spread'])
        self.assertEqual(quote['liquidity'], replay['liquidity'])
        self.assertIsNotNone(pick_deadline(fixture, OBSERVED))

    def test_independent_c6_audit_accepts_the_row(self):
        import importlib.util
        fixture = self.priced_fixture()
        fixture['expires_at'] = pick_deadline(fixture, OBSERVED)
        snapshot = {
            'schema_version': 2, 'generated_at': '2026-10-26T01:20:00Z',
            'fixtures_observed_at': OBSERVED, 'coverage': 'verified',
            'matches': [fixture], 'fixture_evidence': [copy.deepcopy(RAW_ROW)],
        }
        spec = importlib.util.spec_from_file_location(
            'audit_snapshot', ROOT / 'verification-c6' / 'audit_snapshot.py')
        audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit)
        rows, errors = audit.inspect(snapshot)
        self.assertEqual(errors, [])
        self.assertEqual(rows[0][1], [])

    def test_retained_pre_adapter_snapshot_still_validates(self):
        result = validate_data(load('snapshot.json'))
        self.assertGreater(result['probability_calculations_reproduced'], 0)


if __name__ == '__main__':
    unittest.main()
