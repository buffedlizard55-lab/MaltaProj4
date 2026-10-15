"""Originated VRS lines: Valve's formula, identity rules, the live fetch path,
and agreement between the collector, the validator and the independent auditor."""
import copy
import importlib.util
import json
import math
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from scripts import vrs
from scripts.core import FIXTURES, HOTSPAWN, GAMMA, PIN, iso
from scripts.inventory import LOBBY
from scripts.refresh import run
from scripts.validate import validate_data

ROOT = Path(__file__).resolve().parents[1]
VENDORED_TEXT = (ROOT / 'data/vrs/standings_global_2026_10_05.md').read_text()
TABLE = vrs.parse(VENDORED_TEXT)


def load_auditor():
    spec = importlib.util.spec_from_file_location('audit_snapshot', ROOT / 'verification-c6/audit_snapshot.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valve_prior_win_expectation(rv1, rv2, rd=75.0):
    """Line-by-line port of Valve's model/fit.js priorWinExpectation using
    model/glicko.js with setFixedRD(rd). Used to prove the closed form exact."""
    q = math.log(10) / 400
    one_over_pi_sq = 1 / (math.pi * math.pi)

    def clamp(value):
        return max(rd, min(rd, value))

    def apply(rank, score):
        g = 1 / math.sqrt(1 + (3 * q * q * rd * rd * one_over_pi_sq))
        ev = 1 / (1 + math.pow(10, g * (rank - rv2) / (-400)))
        adj_rd_sq = g * g * ev * (1 - ev)
        adj_rank = g * (score - ev)
        adjusted_rd_sq = 1 / (1 / (rd * rd) + q * q * adj_rd_sq)
        clamp(math.sqrt(adjusted_rd_sq))
        return rank + q * adjusted_rd_sq * adj_rank

    win_delta = apply(rv1, 1) - rv1
    loss_delta = rv1 - apply(rv1, 0)
    return 1 - (win_delta / (win_delta + loss_delta))


class FormulaTests(unittest.TestCase):
    def test_closed_form_equals_valves_procedure(self):
        for a, b in [(1716, 1543), (1534, 1527), (2046, 400), (499, 1072), (1000, 1000), (937, 548)]:
            self.assertAlmostEqual(vrs.expected(a, b), valve_prior_win_expectation(a, b), places=12)

    def test_published_constants_and_symmetry(self):
        self.assertEqual(vrs.RD, 75.0)
        self.assertEqual(vrs.SLOPE, 0.7986)
        self.assertEqual(vrs.ROSTER_OVERLAP, 3)
        self.assertAlmostEqual(vrs.G, 0.9728209910486895, places=12)
        for a, b in [(1716, 1543), (600, 1900)]:
            raw = vrs.expected(a, b)
            self.assertAlmostEqual(raw + vrs.expected(b, a), 1, places=12)
            self.assertAlmostEqual(vrs.calibrated(raw) + vrs.calibrated(1 - raw), 1, places=12)
        self.assertEqual(vrs.calibrated(.5), .5)
        # Aurora 1716 vs 9z 1543 (Valve standings of 2026-10-05).
        self.assertAlmostEqual(vrs.expected(1716, 1543), 0.724881, places=6)
        self.assertAlmostEqual(vrs.calibrated(vrs.expected(1716, 1543)), 0.6795896, places=6)


class ParseAndIdentityTests(unittest.TestCase):
    def test_vendored_file_is_the_unmodified_official_copy(self):
        import hashlib
        meta = json.loads((ROOT / 'data/vrs/meta.json').read_text())
        self.assertEqual(hashlib.sha256(VENDORED_TEXT.encode()).hexdigest(), meta['sha256'])
        self.assertEqual(TABLE['as_of'], '2026-10-05')
        self.assertEqual(len(TABLE['teams']), 380)
        self.assertEqual((TABLE['teams'][0]['name'], TABLE['teams'][0]['points']), ('Spirit', 2046))

    def test_parse_fails_closed(self):
        with self.assertRaises(ValueError):
            vrs.parse('no header here')
        with self.assertRaises(ValueError):
            vrs.parse('### Standings as of 2026_10_05\n| 1 | 2000 | X | a, b | [details](d.md) |')

    def test_exact_and_alias_labels(self):
        self.assertEqual(vrs.identify('Aurora', TABLE)[0]['points'], 1716)
        self.assertEqual(vrs.identify('Team Liquid', TABLE)[0]['name'], 'Liquid')
        self.assertEqual(vrs.identify('WROTBERRY', TABLE)[0]['name'], 'WBT')
        self.assertIsNone(vrs.identify('LOS NINOS', TABLE)[0])
        self.assertIsNone(vrs.identify('Aurora Young', TABLE)[0])

    def test_duplicated_label_needs_the_lineup(self):
        entry, reason = vrs.identify('Leo', TABLE)
        self.assertIsNone(entry)
        self.assertIn('appears 2 times', reason)
        entry, _ = vrs.identify('Leo', TABLE, ['aimy', 'drac', 'leen', 'next1me', 'Tarkky'])
        self.assertEqual((entry['standing'], entry['roster_overlap']), (112, 5))
        entry, _ = vrs.identify('Leo', TABLE, ['amster', 'kL1o', 'leen', 'Malkiss', 'someone'])
        self.assertEqual(entry['standing'], 340)
        entry, reason = vrs.identify('Leo', TABLE, ['leen', 'a', 'b', 'c', 'd'])
        self.assertIsNone(entry)
        self.assertIn('fewer than 3', reason)

    def test_unique_label_with_a_different_roster_is_rejected(self):
        entry, reason = vrs.identify('Aurora', TABLE, ['p1', 'p2', 'p3', 'XANTARES', 'woxic'])
        self.assertIsNone(entry)
        entry, _ = vrs.identify('Aurora', TABLE, ['XANTARES', 'woxic', 'Jimpphat', 'kyxsan', 'Wicadia'])
        self.assertEqual(entry['roster_overlap'], 5)

    def test_equal_overlap_between_two_listed_rosters_is_ambiguous(self):
        # Zomblers is listed twice; both rosters share four players.
        entry, reason = vrs.identify('Zomblers', TABLE, ['CAJUN', 'CoolComs', 'FxRE', 'Pose1doNN', 'nobody'])
        self.assertIsNone(entry)
        self.assertIn('same number of players', reason)
        entry, _ = vrs.identify('Zomblers', TABLE, ['CAJUN', 'CoolComs', 'FxRE', 'Pose1doNN', 'Zoker'])
        self.assertEqual(entry['standing'], 259)


def fixture(teams, start=None, probabilities=None):
    start = start or datetime.now(timezone.utc) + timedelta(hours=3)
    return {'id': 'F1', 'teams': list(teams), 'state': 'open', 'start': iso(start), 'lock': iso(start - timedelta(minutes=6)),
            'probabilities': probabilities, 'fair_odds': None, 'pick': None, 'method': None, 'evidence': [],
            'flags': [], 'attempts': [], 'reason': None}


META = {'file': 'standings_global_2026_10_05.md', 'commit': 'c' * 40, 'raw_url': vrs.RAW + '/' + 'c' * 40 + '/live/2026/x.md',
        'blob_url': vrs.BLOB + '/' + 'c' * 40 + '/live/2026/x.md', 'details_base': vrs.BLOB + '/' + 'c' * 40 + '/live/2026/',
        'observed_at': iso(datetime.now(timezone.utc)), 'origin': 'test'}


class ApplyTests(unittest.TestCase):
    def test_apply_prices_only_rows_without_a_market(self):
        row = fixture(['Aurora', '9z'])
        vrs.apply(row, TABLE, META)
        self.assertEqual(row['method'], 'model_vrs')
        self.assertEqual(row['pick'], 'Aurora')
        self.assertAlmostEqual(row['probabilities'][0], vrs.calibrated(vrs.expected(1716, 1543)), places=12)
        self.assertIn(vrs.MODEL_FLAG, row['flags'])
        self.assertTrue(any('roster continuity not checked' in f for f in row['flags']))
        priced = fixture(['Aurora', '9z'], probabilities=[.69, .31])
        vrs.apply(priced, TABLE, META)
        self.assertEqual(priced['probabilities'], [.69, .31])
        self.assertNotIn('evidence', [k for k, v in priced.items() if v and k == 'evidence'])

    def test_alias_identity_is_recorded(self):
        row = fixture(['Ninjas in Pyjamas', 'Team Liquid'])
        vrs.apply(row, TABLE, META)
        quote = row['evidence'][0]
        self.assertEqual(quote['vrs_teams'], ['Ninjas in Pyjamas', 'Liquid'])
        self.assertEqual([i['canonical'] for i in quote['identity_sources']], ['Liquid'])

    def test_unidentifiable_rows_stay_unpriced(self):
        row = fixture(['Procyon', 'LOS NINOS'])
        vrs.apply(row, TABLE, META)
        self.assertIsNone(row['probabilities'])
        self.assertIn('LOS NINOS', row['attempts'][-1]['reason'])

    def test_compare_attaches_a_reproducible_model_check(self):
        row = fixture(['Aurora', '9z'], probabilities=[.69, .31])
        row['method'] = 'exchange'
        vrs.compare(row, TABLE, META)
        check = row['model_check']
        self.assertEqual(check['status'], 'ok')
        self.assertNotIn('difference', check)  # derived at render time, never stored
        difference, same = vrs.gap(row)
        self.assertTrue(same)
        self.assertAlmostEqual(difference, check['probabilities'][0] - .69, places=12)
        row['probabilities'] = [.3, .7]  # a later market move cannot leave a stored gap stale
        self.assertFalse(vrs.gap(row)[1])


class FailingSources:
    log = []

    def get(self, *args, **kwargs):
        raise ValueError('HTTP 403')


class FetchTests(unittest.TestCase):
    def test_vendored_copy_is_used_when_the_live_fetch_fails(self):
        standings, meta, problem = vrs.fetch(FailingSources(), datetime(2026, 10, 15, 23, tzinfo=timezone.utc))
        self.assertEqual(standings['as_of'], '2026-10-05')
        self.assertIn('vendored', meta['origin'])
        self.assertIn('Live VRS fetch failed', problem)

    def test_stale_standings_are_refused(self):
        standings, meta, problem = vrs.fetch(FailingSources(), datetime(2027, 1, 15, tzinfo=timezone.utc))
        self.assertIsNone(standings)
        self.assertIn('days old', problem)


TODAY = datetime.now(timezone.utc)
TODAY_FILE = 'standings_global_%s.md' % TODAY.strftime('%Y_%m_%d')
LIVE_TEXT = VENDORED_TEXT.replace('Standings as of 2026_10_05', 'Standings as of ' + TODAY.strftime('%Y_%m_%d'))
START = (TODAY + timedelta(hours=4)).replace(microsecond=0)
ROWS = [
    {'id': 'VRS_1', 'sport_alias': 'cs2', 'participants0_name': 'Aurora', 'participants1_name': '9z',
     'participants0_id': 'a', 'participants1_id': 'b', 'status': 'scheduled', 'scheduled_start_time': iso(START),
     'lock_time': iso(START - timedelta(minutes=6)), 'competition_name': 'Synthetic VRS Cup', 'tier': 's'},
    {'id': 'VRS_2', 'sport_alias': 'cs2', 'participants0_name': 'Ninjas in Pyjamas', 'participants1_name': 'Team Liquid',
     'participants0_id': 'c', 'participants1_id': 'd', 'status': 'scheduled', 'scheduled_start_time': iso(START),
     'lock_time': iso(START - timedelta(minutes=6)), 'competition_name': 'Synthetic VRS Cup', 'tier': 'b'},
]


def ng_state(rows):
    return '<html><body><script id="ng-state">' + json.dumps({'t': {'u': FIXTURES.split('?')[0], 'b': rows}}) + '</script></body></html>'


class LiveSources:
    """Synthetic upstreams including the official GitHub API contract."""

    def __init__(self, now=None):
        self.log = []
        self.blocked_hosts = {}
        self.headers_seen = []

    def get(self, name, url, as_json=True, headers=None):
        stamp = {'observed_at': iso(datetime.now(timezone.utc))}
        self.log.append({'name': name, 'url': url, 'status': 'ok', 'observed_at': stamp['observed_at']})
        if url == FIXTURES:
            return ROWS, stamp
        if url in (HOTSPAWN, LOBBY):
            return ng_state(ROWS), stamp
        if url == GAMMA + '/sports':
            return [{'sport': 'cs2', 'series': '10310'}], stamp
        if url.startswith(GAMMA + '/events?'):
            return [], stamp
        if url.startswith(vrs.API + '/contents/live/%d' % TODAY.year):
            return [{'name': 'standings_europe_2026_10_05.md'}, {'name': 'standings_global_2026_09_07.md'}, {'name': TODAY_FILE}], stamp
        if url.startswith(vrs.API + '/commits?path=live/%d/%s' % (TODAY.year, TODAY_FILE)):
            return [{'sha': 'f' * 40}], stamp
        if url == '%s/%s/live/%d/%s' % (vrs.RAW, 'f' * 40, TODAY.year, TODAY_FILE):
            return LIVE_TEXT, stamp
        if url.startswith(PIN):
            return [], stamp
        raise ValueError('HTTP 403 access restricted for ' + url)


class PipelineTests(unittest.TestCase):
    def snapshot(self):
        with patch('scripts.refresh.Sources', LiveSources):
            return run(None)

    def test_live_path_originates_lines_for_unpriced_rows(self):
        data = self.snapshot()
        rows = {m['id']: m for m in data['matches']}
        aurora = rows['VRS_1']
        self.assertEqual(aurora['method'], 'model_vrs')
        self.assertEqual(aurora['pick'], 'Aurora')
        quote = aurora['evidence'][0]
        self.assertEqual(quote['standings_commit'], 'f' * 40)
        self.assertEqual(quote['standings_origin'], 'live official repository')
        self.assertTrue(quote['api_url'].startswith(vrs.RAW + '/' + 'f' * 40))
        nip = rows['VRS_2']
        self.assertEqual(nip['method'], 'model_vrs')
        self.assertFalse([i for i in data['issues'] if i['code'] == 'vrs'])

    def test_validator_and_independent_auditor_accept_model_rows(self):
        data = self.snapshot()
        report = validate_data(data)
        self.assertEqual(report['probability_calculations_reproduced'], 2)
        _, errors = load_auditor().inspect(data)
        self.assertEqual(errors, [])

    def test_tampered_model_rows_are_rejected_by_both_checks(self):
        auditor = load_auditor()
        mutations = [
            (lambda m: m['evidence'][0].update(points=[1800, 1543]), 'altered points'),
            (lambda m: m['evidence'][0].update(calibration_slope=1.0), 'altered calibration'),
            (lambda m: m.update(pick='9z'), 'pick against the model'),
            (lambda m: m['evidence'][0].update(label_counts=[2, 1]), 'duplicated label without a roster check'),
            (lambda m: m['evidence'][0].update(vrs_teams=['Astralis', '9z']), 'label mapped to another team'),
            (lambda m: m['evidence'][0].update(url='https://example.com/standings.md'), 'unofficial source'),
            (lambda m: m.update(flags=[]), 'model row not labelled as non-market'),
        ]
        base = self.snapshot()
        for mutate, label in mutations:
            data = copy.deepcopy(base)
            mutate(next(m for m in data['matches'] if m['id'] == 'VRS_1'))
            _, errors = auditor.inspect(data)
            self.assertTrue(errors, 'auditor accepted: ' + label)
            with self.assertRaises(AssertionError, msg='validator accepted: ' + label):
                validate_data(data)


if __name__ == '__main__':
    unittest.main()
