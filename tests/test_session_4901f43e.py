"""Session 4901f43e: the claims this session verified must stay replayable.

Every assertion here re-derives a number with the repository's own calculators
from values this session read off a primary source, so the tests pass offline and
stay true after other sessions merge. They pin three things:

1. the receipt file cannot be edited silently (each extract carries its sha256),
2. the two identities this session's verification rests on are roster facts, not
   name guesses, and
3. the probabilities those facts support are the ones Valve's published file and
   Polymarket's own API produce -- including the model value that a research note
   reported as 59.1% and which does not reproduce.
"""
import json
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import core, vrs  # noqa: E402

RECEIPTS = ROOT / 'research/session-4901f43e/receipts-2026-10-21.json'
STANDINGS = ROOT / 'data/vrs/standings_global_2026_10_05.md'
BASELINE = ROOT / 'data/latest.json'
AUDITOR = ROOT / 'verification-4901f43e/audit_published_claims.py'


def load_receipts():
    doc = json.loads(RECEIPTS.read_text())
    return doc, {item['id']: item for item in doc['receipts']}


def players(values):
    return {core.plain_name(v) for v in values}


class TestReceiptIntegrity(unittest.TestCase):
    def setUp(self):
        self.doc, self.by_id = load_receipts()

    def test_every_receipt_is_replayable(self):
        required = ('id', 'url', 'retrieved_at', 'extract', 'extract_sha256',
                    'evidence_level', 'read_path')
        for item in self.doc['receipts']:
            for key in required:
                self.assertTrue(item.get(key), '%s is missing %s' % (item.get('id'), key))
            self.assertTrue(item['url'].startswith('https://'), item['id'])
            digest = __import__('hashlib').sha256(item['extract'].encode()).hexdigest()
            self.assertEqual(digest, item['extract_sha256'],
                             '%s extract was edited after the read' % item['id'])

    def test_reads_are_bounded_by_evidence_inside_the_response(self):
        """A read time is only credible if something in the response bounds it."""
        bounded = [i for i in self.doc['receipts'] if i.get('read_not_before')]
        self.assertTrue(bounded, 'no receipt records a lower bound for its read time')
        for item in bounded:
            self.assertLessEqual(core.dt(item['read_not_before']), core.dt(item['retrieved_at']),
                                 item['id'])

    def test_reads_are_inside_the_evidence_window(self):
        recorded = core.dt(self.doc['recorded_at'])
        for item in self.doc['receipts']:
            self.assertTrue(core.fresh(item['retrieved_at'], recorded),
                            '%s was already stale when recorded' % item['id'])

    def test_policy_is_stated_and_crowd_votes_are_never_prices(self):
        self.assertIn('inventory only', self.doc['policy'])
        for item in self.doc['receipts']:
            verified = item.get('verified_values') or {}
            for key, value in verified.items():
                if 'crowd' in key:
                    self.assertNotIn('probabilities', verified,
                                     '%s mixes a crowd vote with a price' % item['id'])


class TestZettaIdentity(unittest.TestCase):
    """Zetta (Hotspawn/HLTV) and Alianza Lima Esports (Polymarket) are one roster."""

    def setUp(self):
        _doc, self.by_id = load_receipts()
        self.standings = vrs.parse(STANDINGS.read_text())

    def valve_row(self, standing):
        return next(r for r in self.standings['teams'] if r['standing'] == standing)

    def test_three_independent_reads_give_one_five_player_roster(self):
        valve = self.valve_row(357)
        self.assertEqual(valve['name'], 'Zetta')
        hltv = self.by_id['R5-hltv-match-2399865']['verified_values']['zetta_lineup']
        bo3gg = self.by_id['R7-bo3gg-alianza-lima-lineup']['verified_values']['alianza_lima_lineup']
        self.assertEqual(players(valve['roster']), players(hltv))
        self.assertEqual(players(valve['roster']), players(bo3gg))
        self.assertEqual(len(players(valve['roster'])), 5)

    def test_the_alias_rests_on_full_reads_not_snippets(self):
        load_bearing = ['R3-valve-vrs-357-zetta', 'R5-hltv-match-2399865',
                        'R7-bo3gg-alianza-lima-lineup', 'R8-hltv-event-9452-results',
                        'R9-maisesports-pandascore-ale']
        for rid in load_bearing:
            self.assertEqual(self.by_id[rid]['evidence_level'], 'full_read', rid)

    def test_slot_labels_cross_over_on_two_separate_match_days(self):
        """HLTV says Zetta, the aggregators say ALE, for the same real match."""
        hltv = self.by_id['R8-hltv-event-9452-results']['verified_values']
        mais = self.by_id['R9-maisesports-pandascore-ale']['verified_values']
        self.assertIn('Zetta 1-0 realgotis22', hltv['hltv_match_2399802'])
        self.assertEqual(mais['ale_vs_realgotis22'], '2026-10-19 round 4')
        self.assertIn('2026-10-15', mais['ale_vs_sukeban'])
        strafe = self.by_id['R10-strafe-event-75c83e']['verified_values']
        self.assertEqual(strafe['zetta_vs_sukeban_utc'], '2026-10-15T16:05:00Z')

    def test_hltv_match_id_serves_a_different_match_than_its_slug(self):
        """HLTV resolves by numeric id, so a wrong id behind a right slug looks valid."""
        item = self.by_id['R11-hltv-match-2399867-is-not-zetta']
        self.assertIn('/matches/2399867/zetta-vs-los-ninos', item['url'])
        self.assertIn('alliance-vs-faze', item['served_url'])
        self.assertIn('Alliance vs FaZe', item['verified_values']['actual_match'])
        self.assertIn('IRREGULARITY', item['irregularity'])

    def test_hltv_lists_exactly_one_upcoming_zetta_fixture(self):
        team = self.by_id['R6-hltv-team-13833-zetta']['verified_values']
        self.assertEqual(team['upcoming_matches'], 1)
        self.assertEqual(team['hltv_world_rank'], 241)

    def test_liquipedia_cannot_corroborate_and_is_recorded_as_negative(self):
        item = self.by_id['R15-liquipedia-zetta-absent']
        self.assertEqual(item['evidence_level'], 'full_read_negative')
        self.assertFalse(item['verified_values']['page_exists'])


class TestPolymarketLineReplay(unittest.TestCase):
    """The 1082837 price must survive the repository's own strict gate."""

    def setUp(self):
        _doc, self.by_id = load_receipts()
        self.item = self.by_id['R1-polymarket-market-6001634']

    def candidate(self):
        values = self.item['verified_values']
        return {
            'provider': 'Polymarket', 'id': '6001634',
            'url': 'https://polymarket.com/event/cs2-ale1-ln-2026-10-21',
            'api_url': self.item['url'],
            'observed_at': self.item['read_not_before'],
            'updated_at': '2026-10-21T20:20:57.736361Z',
            'prices': [0.385, 0.615],
            'raw': {'id': '6001634', 'outcomePrices': '["0.385", "0.615"]'},
            'market': {'active': True, 'closed': False, 'acceptingOrders': True,
                       'bestBid': 0.38, 'bestAsk': 0.39, 'liquidity': 3888.256,
                       'sportsMarketType': 'moneyline'},
            'teams': ['Alianza Lima Esports', 'Los Niños'],
            'start': values['start_utc'],
        }

    def test_strict_gate_accepts_and_returns_the_published_split(self):
        now = core.dt(self.item['retrieved_at'])
        quote = core.quote_polymarket(self.candidate(), [1, 0], now)
        self.assertEqual(quote['tier'], 'exchange')
        self.assertEqual([round(p, 6) for p in quote['probabilities']], [0.615, 0.385])
        self.assertAlmostEqual(quote['spread'], 0.01, places=6)
        self.assertAlmostEqual(quote['liquidity'], 3888.256, places=3)

    def test_start_matches_the_hotspawn_fixture_exactly(self):
        self.assertEqual(self.item['verified_values']['start_utc'], '2026-10-21T22:00:00Z')
        event = self.by_id['R2-polymarket-event-1227336']['verified_values']
        self.assertEqual(event['round'], 5)
        hltv = self.by_id['R5-hltv-match-2399865']['verified_values']
        self.assertEqual(hltv['round'], 'Swiss round 5')

    def test_expired_observation_is_refused(self):
        stale = self.candidate()
        stale['observed_at'] = '2026-10-20T01:00:00Z'
        with self.assertRaises(ValueError):
            core.quote_polymarket(stale, [1, 0], datetime.now(timezone.utc))

    def test_thin_liquidity_is_refused_even_with_a_tight_spread(self):
        thin = self.candidate()
        thin['market']['liquidity'] = 42.0
        with self.assertRaises(ValueError):
            core.quote_polymarket(thin, [1, 0], core.dt(self.item['retrieved_at']))


class TestValveModelArithmetic(unittest.TestCase):
    """1082858 must publish what Valve's own rows produce, not a reported figure."""

    def setUp(self):
        self.standings = vrs.parse(STANDINGS.read_text())
        self.rows = {r['standing']: r for r in self.standings['teams']}

    def split(self, first, second):
        raw = vrs.expected(self.rows[first]['points'], self.rows[second]['points'])
        return vrs.calibrated(raw)

    def test_published_rows_are_the_official_ones(self):
        for standing, name, points in ((86, 'FlyQuest', 1093), (119, 'THUNDER dOWNUNDER', 971),
                                       (136, 'Ground Zero', 878), (157, 'benched gods', 811),
                                       (329, 'benched gods', 516), (357, 'Zetta', 473)):
            self.assertEqual(self.rows[standing]['name'], name)
            self.assertEqual(self.rows[standing]['points'], points)

    def test_ground_zero_versus_off_chops_is_60_2_not_59_1(self):
        first = self.split(136, 119)  # Ground Zero then Off Chops / THUNDER dOWNUNDER
        self.assertEqual(round(first * 100, 1), 39.8)
        self.assertEqual(round((1 - first) * 100, 1), 60.2)
        self.assertNotEqual(round((1 - first) * 100, 1), 59.1)

    def test_a_59_1_claim_needs_a_points_gap_valve_does_not_publish(self):
        implied_raw = 0.5 + (0.591 - 0.5) / vrs.SLOPE
        import math
        implied_gap = -math.log10(1 / implied_raw - 1) * 400 / vrs.G
        actual_gap = self.rows[119]['points'] - self.rows[136]['points']
        self.assertEqual(actual_gap, 93)
        self.assertLess(implied_gap, 90, 'the reported split is not reproducible from Valve rows')

    def test_benched_gods_label_is_ambiguous_without_a_lineup(self):
        """Two Valve rows carry this label, so the model must refuse the label alone."""
        duplicated = [r for r in self.standings['teams'] if core.norm(r['name']) == core.norm('benched gods')]
        self.assertEqual(len(duplicated), 2)
        entry, note = vrs.identify('benched gods', self.standings)
        self.assertIsNone(entry)
        self.assertIn('2 times', note)

    def test_benched_gods_lineup_selects_exactly_one_row(self):
        lineup = ['Wign', 'facer', 'norescue', 'yoyoS2', 'K014NZ']
        entry, note = vrs.identify('benched gods', self.standings, lineup)
        self.assertIsNotNone(entry)
        self.assertEqual(entry['standing'], 157)
        self.assertEqual(entry['roster_overlap'], 5)

    def test_roster_continuity_for_both_dfrag_teams(self):
        _doc, by_id = load_receipts()
        values = by_id['R13-hltv-match-2399888-lineups']['verified_values']
        ground_zero = players(values['ground_zero_lineup'])
        off_chops = players(values['off_chops_lineup'])
        self.assertEqual(len(ground_zero & players(self.rows[136]['roster'])), 4)
        self.assertEqual(len(off_chops & players(self.rows[119]['roster'])), 4)
        self.assertGreaterEqual(len(off_chops & players(self.rows[119]['roster'])), vrs.ROSTER_OVERLAP)
        self.assertEqual(values['ground_zero_substitute'], 'tucks')

    def test_dfrag_announcement_names_the_same_five_as_hltv(self):
        _doc, by_id = load_receipts()
        announced = players(by_id['R14-dfrag-off-chops-rebrand']['verified_values']['new_five'])
        listed = players(by_id['R13-hltv-match-2399888-lineups']['verified_values']['off_chops_lineup'])
        self.assertEqual(announced, listed)

    def test_staqued_and_off_chops_have_no_valve_row(self):
        names = {core.norm(r['name']) for r in self.standings['teams']}
        self.assertNotIn(core.norm('Staqued'), names)
        self.assertNotIn(core.norm('Off Chops'), names)


class TestPostponedFixture(unittest.TestCase):
    def test_hltv_names_no_teams_for_the_postponed_slot(self):
        _doc, by_id = load_receipts()
        item = by_id['R12-hltv-match-2399696-postponed']
        self.assertEqual(item['verified_values']['status'], 'Match postponed')
        self.assertEqual(item['verified_values']['teams_named_on_page'], 0)
        self.assertIn('postponed', item['irregularity'].lower())

    def test_no_percentage_is_claimed_for_it(self):
        _doc, by_id = load_receipts()
        item = by_id['R12-hltv-match-2399696-postponed']
        self.assertNotIn('probabilities', item['verified_values'])
        self.assertIn('percentage-free', item['conclusion'])


class TestAuditorEndToEnd(unittest.TestCase):
    def test_auditor_replays_the_committed_baseline_with_no_failures(self):
        result = subprocess.run(
            [sys.executable, str(AUDITOR), '--snapshot', str(BASELINE)],
            cwd=str(ROOT), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout[-3000:] + result.stderr[-2000:])
        self.assertIn('0 failed', result.stdout)
        self.assertIn('crowd-votes-excluded', result.stdout)

    def test_auditor_detects_a_probability_that_does_not_replay(self):
        import copy
        import tempfile
        doc = json.loads(BASELINE.read_text())
        broken = copy.deepcopy(doc)
        target = next(m for m in broken['matches']
                      if m['state'] == 'open' and m.get('probabilities'))
        target['probabilities'] = [0.5, 0.5]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'broken.json'
            path.write_text(json.dumps(broken))
            result = subprocess.run(
                [sys.executable, str(AUDITOR), '--snapshot', str(path)],
                cwd=str(ROOT), capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('row-does-not-replay:%s' % target['id'], result.stdout)

    def test_auditor_detects_a_silently_edited_receipt(self):
        import tempfile
        doc, _by_id = load_receipts()
        doc['receipts'][0]['extract'] += ' (edited after the read)'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'receipts.json'
            path.write_text(json.dumps(doc))
            result = subprocess.run(
                [sys.executable, str(AUDITOR), '--receipts', str(path)],
                cwd=str(ROOT), capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('edited after the read', result.stdout)


if __name__ == '__main__':
    unittest.main()
