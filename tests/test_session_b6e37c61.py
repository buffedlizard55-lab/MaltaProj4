"""Session b6e37c61: the final sourced pick tier, HLTV recent form.

Every test here is offline and deterministic. The HLTV parser tests run
against real match-page HTML retained in the repository
(``research/harvest-76712ccc/hltv-2399386.html``, Legacy vs PARIVISION,
Thunderpick World Championship 2026), so the selectors are proven against
HLTV's own markup, not a hand-written imitation. The validator and
independent-audit tests convert one real open row of the committed snapshot
into a ``research_form`` row and require both gates to reproduce the pick
from the stored raw evidence -- and to reject the same row once its stored
win totals are corrupted.
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import hltv
from scripts.core import iso, research_form_pick, research_observation

ROOT = Path(__file__).resolve().parents[1]
MATCH_HTML = ROOT / 'research' / 'harvest-76712ccc' / 'hltv-2399386.html'
SNAPSHOT = ROOT / 'data' / 'latest.json'


def result(opponent, won, when='1 week ago', fmt='bo3'):
    return {'opponent': opponent, 'when': when, 'format': fmt,
            'score': '2 - 1' if won else '1 - 2', 'won': won}


def fixture(form, h2h=None, teams=('Alpha', 'Bravo')):
    return {'id': '9999999', 'teams': list(teams), 'state': 'open',
            'probabilities': None, 'fair_odds': None, 'pick': None, 'method': None,
            'evidence': [], 'attempts': [], 'flags': [], 'reason': None,
            'hltv_context': {'source': 'https://www.hltv.org/matches/2400000/alpha-vs-bravo',
                             'observed_at': '2026-10-23T08:00:00Z',
                             'team_map': {teams[0]: teams[0], teams[1]: teams[1]},
                             'form': form, 'head_to_head': h2h}}


class PastResultsParserTest(unittest.TestCase):
    """scripts.hltv.past_results/head_to_head on real retained HLTV HTML."""

    @classmethod
    def setUpClass(cls):
        cls.soup = BeautifulSoup(MATCH_HTML.read_text(encoding='utf-8', errors='ignore'),
                                 'html.parser')

    def test_form_boxes_for_both_teams(self):
        form = hltv.past_results(self.soup)
        self.assertIn('Legacy', form)
        self.assertIn('PARIVISION', form)
        self.assertGreaterEqual(len(form['Legacy']), 10)
        self.assertGreaterEqual(len(form['PARIVISION']), 10)

    def test_results_are_score_consistent_and_deduped(self):
        form = hltv.past_results(self.soup)
        for team, rows in form.items():
            keys = [(r['opponent'], r['when'], r['format'], r['score']) for r in rows]
            self.assertEqual(len(keys), len(set(keys)), 'Team/Core double rendering counted twice')
            for row in rows:
                first, second = (int(x) for x in row['score'].split(' - '))
                self.assertNotEqual(first, second)
                self.assertEqual(row['won'], first > second, row)

    def test_first_rows_match_the_page(self):
        form = hltv.past_results(self.soup)
        first = form['Legacy'][0]
        self.assertEqual(first['opponent'], 'M80')
        self.assertEqual(first['score'], '1 - 2')
        self.assertFalse(first['won'])

    def test_head_to_head_summary(self):
        h2h = hltv.head_to_head(self.soup)
        self.assertEqual(h2h, {'teams': ['Legacy', 'PARIVISION'], 'wins': [6, 4], 'overtimes': 3})

    def test_context_carries_form_and_exact_team_map(self):
        fix = {'teams': ['PARIVISION', 'Legacy'], 'start': iso('1791992400000')}
        ctx = hltv.context(MATCH_HTML.read_text(encoding='utf-8', errors='ignore'), fix)
        self.assertEqual(ctx['team_map'], {'Legacy': 'Legacy', 'PARIVISION': 'PARIVISION'})
        self.assertIn('Legacy', ctx['form'])
        self.assertEqual(ctx['head_to_head']['wins'], [6, 4])


class ResearchFormPickTest(unittest.TestCase):
    """scripts.core.research_form_pick decision rules."""

    def test_recent_form_edge_picks_the_better_record(self):
        form = {'Alpha': [result('X', True), result('Y', True), result('Z', False), result('W', True)],
                'Bravo': [result('X', False), result('Y', True), result('Z', False), result('W', False)]}
        fix = fixture(form)
        research_form_pick(fix)
        self.assertEqual(fix['pick'], 'Alpha')
        self.assertEqual(fix['method'], 'research_form')
        self.assertIsNone(fix['probabilities'])
        self.assertIsNone(fix['fair_odds'])
        self.assertIn('not a market probability', fix['reason'])
        detail = fix['hltv_context']['form_detail']
        self.assertEqual(detail['basis'], 'recent_form')
        self.assertEqual(detail['window'], 4)
        self.assertEqual(research_observation(fix), '2026-10-23T08:00:00Z')

    def test_equal_window_even_when_histories_differ(self):
        form = {'Alpha': [result('T%d' % i, True) for i in range(9)],
                'Bravo': [result('T%d' % i, False) for i in range(3)]}
        fix = fixture(form)
        research_form_pick(fix)
        self.assertEqual(fix['pick'], 'Alpha')
        self.assertEqual(fix['hltv_context']['form_detail']['window'], 3)
        self.assertEqual(fix['hltv_context']['resolved_form'][0]['wins'], 3)

    def test_level_form_falls_to_head_to_head(self):
        rows = [result('X', True), result('Y', False), result('Z', True), result('W', False)]
        form = {'Alpha': list(rows), 'Bravo': list(rows)}
        h2h = {'teams': ['Alpha', 'Bravo'], 'wins': [2, 5], 'overtimes': 1}
        fix = fixture(form, h2h)
        research_form_pick(fix)
        self.assertEqual(fix['pick'], 'Bravo')
        self.assertEqual(fix['hltv_context']['form_detail']['basis'], 'head_to_head')

    def test_level_form_and_level_h2h_stays_unresolved(self):
        rows = [result('X', True), result('Y', False), result('Z', True)]
        form = {'Alpha': list(rows), 'Bravo': list(rows)}
        fix = fixture(form, {'teams': ['Alpha', 'Bravo'], 'wins': [3, 3], 'overtimes': 0})
        research_form_pick(fix)
        self.assertIsNone(fix['pick'])
        self.assertIsNone(fix['method'])
        self.assertEqual(fix['attempts'][-1]['provider'], 'Form research')
        self.assertEqual(fix['attempts'][-1]['status'], 'unresolved')

    def test_insufficient_results_stays_unresolved(self):
        form = {'Alpha': [result('X', True), result('Y', True)],
                'Bravo': [result('X', False), result('Y', False), result('Z', False)]}
        fix = fixture(form)
        research_form_pick(fix)
        self.assertIsNone(fix['pick'])
        self.assertIn('insufficient', fix['attempts'][-1]['reason'].replace('fewer than 3 completed results', 'insufficient'))

    def test_missing_hltv_context_stays_unresolved(self):
        fix = fixture({})
        fix['hltv_context'] = {}
        research_form_pick(fix)
        self.assertIsNone(fix['pick'])

    def test_priced_or_picked_fixtures_are_untouched(self):
        form = {'Alpha': [result('X', True), result('Y', True), result('Z', True)],
                'Bravo': [result('X', False), result('Y', False), result('Z', False)]}
        priced = fixture(form)
        priced['probabilities'] = [0.6, 0.4]
        research_form_pick(priced)
        self.assertIsNone(priced['pick'])
        self.assertEqual(priced['attempts'], [])
        picked = fixture(form)
        picked['pick'] = 'Bravo'
        picked['method'] = 'research_rank'
        research_form_pick(picked)
        self.assertEqual(picked['pick'], 'Bravo')
        self.assertEqual(picked['attempts'], [])


def converted_snapshot():
    """One real open row of the committed snapshot, re-tiered to research_form."""
    data = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    row = next(m for m in data['matches'] if m['state'] == 'open' and m.get('pick'))
    a, b = row['teams']
    form = {a: [result('Rival %d' % i, i % 3 != 2, fmt='bo3') for i in range(6)],
            b: [result('Rival %d' % i, i % 3 == 2, fmt='bo3') for i in range(6)]}
    row.update(pick=None, method=None, probabilities=None, fair_odds=None, evidence=[],
               attempts=[], flags=[], reason=None)
    row['hltv_context'] = {'source': 'https://www.hltv.org/matches/2400000/example',
                           'observed_at': data['generated_at'],
                           'teams': [b, a], 'start': row['start'], 'team_map': {b: b, a: a},
                           'form': form, 'head_to_head': None,
                           'ranks': [], 'lineups': [],
                           'limitation': 'Synthetic context for gate tests; the live collector writes this field in scripts.hltv.context.'}
    research_form_pick(row)
    return data


class GatesTest(unittest.TestCase):
    """validate.py and the independent c6 audit reproduce (and police) the tier."""

    def test_converted_row_carries_the_form_pick(self):
        data = converted_snapshot()
        row = next(m for m in data['matches'] if m.get('method') == 'research_form')
        self.assertEqual(row['pick'], row['teams'][0])

    def test_validator_accepts_the_converted_row(self):
        from scripts.validate import validate_data
        validate_data(converted_snapshot())

    def test_validator_rejects_corrupted_win_totals(self):
        from scripts.validate import validate_data
        data = converted_snapshot()
        row = next(m for m in data['matches'] if m.get('method') == 'research_form')
        row['hltv_context']['resolved_form'][1]['wins'] += 3
        with self.assertRaises(AssertionError):
            validate_data(data)

    def test_independent_audit_reproduces_and_polices(self):
        good = converted_snapshot()
        bad = copy.deepcopy(good)
        row = next(m for m in bad['matches'] if m.get('method') == 'research_form')
        row['hltv_context']['resolved_form'][1]['wins'] += 3
        with tempfile.TemporaryDirectory() as tmp:
            for name, payload in (('good', good), ('bad', bad)):
                path = Path(tmp) / (name + '.json')
                path.write_text(json.dumps(payload), encoding='utf-8')
                out = Path(tmp) / (name + '.md')
                proc = subprocess.run([sys.executable, str(ROOT / 'verification-c6' / 'audit_snapshot.py'),
                                       str(path), '--output', str(out)],
                                      capture_output=True, text=True)
                if name == 'good':
                    self.assertEqual(proc.returncode, 0, out.read_text() if out.exists() else proc.stdout + proc.stderr)
                else:
                    self.assertNotEqual(proc.returncode, 0, 'audit accepted corrupted form totals')


class DisplayTest(unittest.TestCase):
    """The new method is labelled everywhere the board explains a pick."""

    def test_method_registered_in_every_display_map(self):
        from scripts import build, summary
        from scripts.coverage_contract import RESEARCH
        self.assertIn('research_form', build.METHOD_LABELS)
        self.assertIn('research_form', build.METHOD_TAGS)
        self.assertIn('research_form', build.METHOD_KIND)
        self.assertIn('research_form', summary.ORIGINS)
        self.assertEqual(summary.METHOD_STEP['research_form'], 'research')
        self.assertIn('research_form', RESEARCH)
        kind, label, _basis = summary.origin({'probabilities': None, 'pick': 'Alpha', 'method': 'research_form'})
        self.assertEqual(kind, 'research')
        self.assertIn('recent form', label)


if __name__ == '__main__':
    unittest.main()
