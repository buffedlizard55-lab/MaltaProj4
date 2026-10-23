"""Session 2c7b9e48 regression tests for the independent board auditor.

The auditor in ``verification-2c7b9e48/audit_board.py`` is the gate that answers
the request "every match must have a pick, and anything that cannot be resolved
must be blank and explained". A gate that only ever says OK is worthless, so
these tests drive it with six independent corruptions and require it to reject
each one, then require it to accept the real committed board and the real built
site unchanged.

The corruptions are applied to a deep copy in memory. Nothing under ``data/`` or
``public/`` is written by this module.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ``public/`` is a build output and is not committed, so these tests build the
# site from the committed snapshot themselves instead of reading a local
# artifact. ``now`` is pinned to the snapshot's own generation time, exactly as
# the refresh does, so rows that were open when it was captured stay open here.
def build_site(directory):
    from scripts import build as build_module
    snapshot = copy.deepcopy(BOARD)
    build_module.build(snapshot, directory,
                       now=datetime.fromisoformat(snapshot['generated_at'].replace('Z', '+00:00')))
    return Path(directory)


def load_auditor():
    spec = importlib.util.spec_from_file_location(
        'audit_board_2c7b9e48', ROOT / 'verification-2c7b9e48' / 'audit_board.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_valve_verifier():
    spec = importlib.util.spec_from_file_location(
        'verify_valve_2c7b9e48', ROOT / 'verification-2c7b9e48' / 'verify_valve.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUDIT = load_auditor()
VALVE = load_valve_verifier()
BOARD = json.loads((ROOT / 'data/latest.json').read_text())
IDENTITIES = json.loads((ROOT / 'data/identities.json').read_text())


def codes(result):
    return {item['code'] for item in result['errors']}


def open_priced(board):
    return [m for m in board['matches'] if m.get('state') == 'open' and m.get('probabilities')]


class RealBoard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.site = build_site(Path(cls.tmp.name) / 'public')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_committed_snapshot_passes_every_rule(self):
        result = AUDIT.audit(copy.deepcopy(BOARD), None, IDENTITIES)
        self.assertEqual(result['errors'], [], result['errors'][:3])
        self.assertGreater(result['checks'], 1000)

    def test_every_open_row_has_a_pick_and_a_source(self):
        rows = [m for m in BOARD['matches'] if m.get('state') == 'open']
        self.assertTrue(rows, 'the committed snapshot must contain open fixtures')
        for m in rows:
            self.assertTrue(m.get('pick'), f'{m["id"]} has no pick')
            self.assertIn(m['pick'], m['teams'], f'{m["id"]} picks a team outside the fixture')
            self.assertTrue(m.get('source_url', '').startswith('https://'), m['id'])
            self.assertTrue(m.get('evidence'), f'{m["id"]} has a pick without evidence')

    def test_unresolved_rows_are_explained_not_defaulted(self):
        for m in BOARD['matches']:
            if m.get('state') == 'open' and not m.get('pick'):
                self.assertTrue(m.get('reason'), f'{m["id"]} unresolved without a reason')
                self.assertTrue(m.get('attempts'), f'{m["id"]} unresolved without attempts')
                self.assertIsNone(m.get('probabilities'), f'{m["id"]} unresolved with a percentage')

    def test_no_probability_comes_from_hotspawn(self):
        for m in BOARD['matches']:
            for quote in m.get('evidence') or []:
                self.assertNotIn('hotspawn', str(quote.get('provider', '')).lower(),
                                 f'{m["id"]} uses a Hotspawn-provided probability')

    def test_built_site_matches_the_snapshot(self):
        result = AUDIT.audit(copy.deepcopy(BOARD), self.site, IDENTITIES)
        self.assertEqual(result['errors'], [], result['errors'][:3])
        self.assertGreater(result['checks'], 2000)


class Refusals(unittest.TestCase):
    """Each case corrupts exactly one fact and must be refused."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.site = build_site(Path(cls.tmp.name) / 'public')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_swapping_the_two_probabilities_is_detected(self):
        board = copy.deepcopy(BOARD)
        row = open_priced(board)[0]
        row['probabilities'] = [row['probabilities'][1], row['probabilities'][0]]
        result = AUDIT.audit(board, None, IDENTITIES)
        self.assertIn('row.replay_mismatch', codes(result))

    def test_editing_one_probability_is_detected(self):
        board = copy.deepcopy(BOARD)
        row = open_priced(board)[0]
        row['probabilities'] = [row['probabilities'][0] + 0.01, row['probabilities'][1] - 0.01]
        result = AUDIT.audit(board, None, IDENTITIES)
        self.assertIn('row.replay_mismatch', codes(result))

    def test_editing_the_underlying_price_is_detected(self):
        board = copy.deepcopy(BOARD)
        row = [m for m in open_priced(board) if m['method'] == 'exchange'][0]
        prices = json.loads(row['evidence'][0]['raw']['outcomePrices'])
        prices[0] = str(round(float(prices[0]) + 0.05, 4))
        row['evidence'][0]['raw']['outcomePrices'] = json.dumps(prices)
        result = AUDIT.audit(board, None, IDENTITIES)
        self.assertIn('row.replay_mismatch', codes(result))

    def test_editing_model_points_is_detected(self):
        board = copy.deepcopy(BOARD)
        rows = [m for m in open_priced(board) if m['method'] == 'model_vrs']
        if not rows:
            self.skipTest('no model-priced row in this snapshot')
        rows[0]['evidence'][0]['points'][0] += 40
        result = AUDIT.audit(board, None, IDENTITIES)
        self.assertIn('row.replay_mismatch', codes(result))

    def test_a_pick_outside_the_fixture_is_refused(self):
        board = copy.deepcopy(BOARD)
        row = open_priced(board)[0]
        row['pick'] = 'Some Other Team'
        result = AUDIT.audit(board, None, IDENTITIES)
        self.assertIn('row.pick_not_in_fixture', codes(result))

    def test_removing_the_official_source_link_is_refused(self):
        board = copy.deepcopy(BOARD)
        open_priced(board)[0]['source_url'] = 'https://example.com/fixture'
        result = AUDIT.audit(board, None, IDENTITIES)
        self.assertIn('row.official_source', codes(result))

    def test_a_hotspawn_derived_probability_is_refused(self):
        board = copy.deepcopy(BOARD)
        open_priced(board)[0]['evidence'][0]['provider'] = 'Hotspawn crowd vote'
        result = AUDIT.audit(board, None, IDENTITIES)
        self.assertIn('row.provider_hotspawn', codes(result))

    def test_an_open_row_without_a_pick_or_a_reason_is_refused(self):
        board = copy.deepcopy(BOARD)
        row = open_priced(board)[0]
        row.update({'pick': None, 'probabilities': None, 'fair_odds': None,
                    'method': None, 'reason': '', 'attempts': []})
        result = AUDIT.audit(board, None, IDENTITIES)
        self.assertTrue({'coverage.open_without_pick', 'coverage.unresolved_reason'} <= codes(result))

    def test_a_past_row_carrying_a_pick_is_refused(self):
        board = copy.deepcopy(BOARD)
        closed = [m for m in board['matches'] if m.get('state') != 'open']
        if not closed:
            self.skipTest('no closed row in this snapshot')
        closed[0]['pick'] = closed[0]['teams'][0]
        result = AUDIT.audit(board, None, IDENTITIES)
        self.assertIn('closed.pick', codes(result))

    def test_two_fixtures_cannot_share_one_market(self):
        board = copy.deepcopy(BOARD)
        rows = open_priced(board)
        rows[1]['evidence'][0]['id'] = rows[0]['evidence'][0]['id']
        result = AUDIT.audit(board, None, IDENTITIES)
        self.assertIn('row.quote_reused', codes(result))

    def test_a_quote_at_a_different_start_is_refused(self):
        board = copy.deepcopy(BOARD)
        row = open_priced(board)[0]
        row['evidence'][0]['start'] = '2026-10-23T23:59:00Z'
        if row['start'] == row['evidence'][0]['start']:
            row['evidence'][0]['start'] = '2026-10-24T23:59:00Z'
        result = AUDIT.audit(board, None, IDENTITIES)
        self.assertIn('row.quote_start', codes(result))

    def test_a_missing_fixture_on_the_built_page_is_refused(self):
        board = copy.deepcopy(BOARD)
        result = AUDIT.audit(board, self.site, IDENTITIES)
        self.assertEqual(result['errors'], [])
        # Point the site check at a directory whose matches page drops one row.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            for name in ('index.html', 'picks.html', 'matches.html', 'unresolved.html', 'review.html'):
                (site / name).write_text((self.site / name).read_text())
            target = str(open_priced(board)[0]['id'])
            html = (site / 'matches.html').read_text().replace(f'data-match="{target}"', 'data-match="removed"')
            (site / 'matches.html').write_text(html)
            result = AUDIT.audit(board, site, IDENTITIES)
        self.assertIn('site.row_missing', codes(result))


class Mapping(unittest.TestCase):
    def test_label_variants_are_accepted(self):
        for fixture, quote in (('LPH', 'LPH Gaming'), ('LOS NINOS', 'Los Niños'),
                               ('BakS', 'BakS eSports'), ('Nuclear TigeRES', 'Nuclear TigeRES')):
            self.assertTrue(AUDIT.label_matches(fixture, quote, []), (fixture, quote))

    def test_unrelated_labels_are_not_matched(self):
        for fixture, quote in (('paiN', 'Imperial'), ('BESTIA Academy', 'RED Canids'),
                               ('WBT', 'ENCE'), ('FlyQuest', 'Staqued')):
            self.assertFalse(AUDIT.label_matches(fixture, quote, []), (fixture, quote))

    def test_a_registered_alias_is_honoured(self):
        record = {'canonical': 'WBT', 'names': ['WBT', 'WROTBERRY']}
        self.assertTrue(AUDIT.label_matches('WROTBERRY', 'WBT', [record]))
        self.assertFalse(AUDIT.label_matches('WROTBERRY', 'WBT', []))

    def test_swapped_mapping_returns_the_permutation(self):
        self.assertEqual(AUDIT.mapping(['BakS', 'BRUTE'], ['Brute', 'BakS eSports'], []), (1, 0))
        self.assertEqual(AUDIT.mapping(['BakS', 'BRUTE'], ['BakS eSports', 'Brute'], []), (0, 1))


class Arithmetic(unittest.TestCase):
    def test_exchange_prices_de_vig_to_one(self):
        p = AUDIT.de_vig(['0.38', '0.62'])
        self.assertAlmostEqual(sum(p), 1.0, places=12)
        self.assertAlmostEqual(p[0], 0.38, places=12)

    def test_overround_is_removed_for_decimal_odds(self):
        p = AUDIT.decimal_odds([1.61, 2.14])
        self.assertAlmostEqual(sum(p), 1.0, places=12)
        self.assertAlmostEqual(p[0], 0.5706666666666667, places=12)

    def test_rounded_or_placeholder_odds_are_refused(self):
        with self.assertRaises(AUDIT.Failure):
            AUDIT.decimal_odds([1.0, 12.0])
        with self.assertRaises(AUDIT.Failure):
            AUDIT.decimal_odds([1.8])

    def test_valve_formula_is_symmetric_and_calibrated(self):
        forward = AUDIT.valve_model([1000, 900])
        backward = AUDIT.valve_model([900, 1000])
        self.assertAlmostEqual(forward[0], backward[1], places=12)
        self.assertAlmostEqual(sum(forward), 1.0, places=12)
        neutral = AUDIT.valve_model([1000, 1000])
        self.assertAlmostEqual(neutral[0], 0.5, places=12)


VALVE_SAMPLE = '''### Standings as of 2026_10_05<br />

| Standing | Points | Team Name            | Roster                                                |                                                                                                      |
| :- | -: | :- | :- | :- |
| 122      |    944 | The Huns             | Annihilation, Bart4k, bexyz, controlez, Cozen         | [details](details/2026_10_05/0122--the_huns--x.md) |
| 165      |    801 | Banda Chuya          | AdrieN, ezox, maaryy, Showk, tomiko                   | [details](details/2026_10_05/0165--banda_chuya--x.md) |
| 213      |    701 | The Huns             | Bart4k, controlez, nin9, sk0R, xerolte                | [details](details/2026_10_05/0213--the_huns--x.md) |
| 172      |    783 | Phantom Academy      | Ayteel, Brain47, Dr3nquu, kalyambys, stefienson       | [details](details/2026_10_05/0172--phantom--x.md) |
| 373      |    402 | Banda Chuya          | ezox, manio                                           | [details](details/2026_10_05/0373--banda_chuya--x.md) |
'''


class ValveVerifier(unittest.TestCase):
    """The VRS verifier must follow Valve's own duplicate-label rule."""

    def setUp(self):
        self.as_of, self.rows = VALVE.parse(VALVE_SAMPLE)

    def test_header_date_is_read_from_valves_file(self):
        self.assertEqual(self.as_of, '2026-10-05')

    def test_repeated_labels_are_all_kept(self):
        self.assertEqual(len(self.rows['The Huns']), 2)
        self.assertEqual(len(self.rows['Banda Chuya']), 2)

    def test_roster_selects_the_right_repeated_label(self):
        row, how, overlap = VALVE.choose(
            self.rows['The Huns'], 122, ['Annihilation', 'Bart4k', 'bexyz', 'controlez', 'Cozen'])
        self.assertEqual((row['standing'], row['points']), (122, 944))
        self.assertEqual(overlap, 5)
        self.assertIn('roster-selected', how)

    def test_a_unique_label_is_used_directly(self):
        row, how, overlap = VALVE.choose(
            self.rows['Phantom Academy'], 172,
            ['Brain47', 'Ayteel', 'Dr3nquu', 'kalyambys', 'La1roN'])
        self.assertEqual(row['points'], 783)
        self.assertEqual(how, 'unique label')
        self.assertEqual(overlap, 4)  # one stand-in is allowed by Valve's own rule

    def test_an_absent_label_is_not_invented(self):
        row, how, overlap = VALVE.choose([], 1, ['a', 'b', 'c', 'd', 'e'])
        self.assertIsNone(row)
        self.assertEqual(how, 'label absent from Valve file')

    def test_an_ambiguous_label_without_roster_evidence_is_refused(self):
        row, how, overlap = VALVE.choose(
            self.rows['Banda Chuya'], 165, ['someone', 'else', 'entirely'])
        self.assertIsNone(row)
        self.assertIn('ambiguous', how)

    def test_valve_model_replay_matches_the_published_number(self):
        # 1079198 Metizport vs BakS: 1290 and 1044 points in Valve's file.
        replay = VALVE.model_probability(1290, 1044)
        self.assertAlmostEqual(replay[0], 0.7385, places=4)
        self.assertAlmostEqual(sum(replay), 1.0, places=12)


if __name__ == '__main__':
    unittest.main()
