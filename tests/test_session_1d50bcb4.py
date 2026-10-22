"""Tests for the HLTV-results form model (session 1d50bcb4).

The module estimates a team's strength in Valve's published points units from
its own dated HLTV results, so a fixture whose opponent Valve does not list can
still carry a labelled win probability. These tests pin the parser, the
estimator's arithmetic, its refusal cases and the interval propagation.
"""
import json
import math
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts import form, vrs
from scripts.core import norm

ROOT = Path(__file__).resolve().parents[1]
RESULTS_HTML = ROOT / 'research/harvest-76712ccc/HLTV_TWC_results.html'


def standings(rows):
    return {'as_of': '2026-10-05', 'teams': [
        {'standing': i + 1, 'points': points, 'name': name, 'roster': ['a', 'b', 'c', 'd', 'e'],
         'details': 'x.md'} for i, (name, points) in enumerate(rows)]}


def results_for(team, opponents, won, start='2026-10-01T12:00:00Z', step_hours=6):
    """Build synthetic HLTV results rows for one team against anchors."""
    base = datetime.fromisoformat(start.replace('Z', '+00:00'))
    out = []
    for i, (opponent, points) in enumerate(opponents):
        when = (base - timedelta(hours=step_hours * i)).isoformat().replace('+00:00', 'Z')
        out.append({'start': when, 'teams': [team, opponent],
                    'winner': team if won[i] else opponent,
                    'score': '2 - 0', 'url': 'https://www.hltv.org/matches/%d/x' % (100000 + i)})
    return out


class ParseTests(unittest.TestCase):
    def test_real_hltv_results_page_parses_to_dated_rows(self):
        rows = form.parse_results(RESULTS_HTML.read_text(encoding='utf-8', errors='replace'))
        self.assertEqual(len(rows), 10)
        first = rows[0]
        self.assertEqual(sorted(first['teams']), ['BETBOOM', 'Legacy'])
        self.assertEqual(first['winner'], 'BETBOOM')
        self.assertEqual(first['start'], '2026-10-16T20:28:36Z')
        self.assertTrue(first['url'].startswith('https://www.hltv.org/matches/'))
        for row in rows:
            self.assertIn(row['winner'], row['teams'])
            self.assertEqual(len(row['teams']), 2)

    def test_a_row_without_a_score_is_skipped_not_guessed(self):
        html = '''<div class="result-con" data-zonedgrouping-entry-unix="1792182516000">
        <a class="a-reset" href="/matches/1/a-vs-b"><div class="result"><table><tr>
        <td class="team-cell"><div class="team">A</div></td>
        <td class="team-cell"><div class="team">B</div></td></tr></table></div></a></div>'''
        self.assertEqual(form.parse_results(html), [])


class EstimateTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 22, tzinfo=timezone.utc)
        # Five anchors spread across the published range.
        self.table = standings([('Anchor 1', 1900), ('Anchor 2', 1600), ('Anchor 3', 1300),
                                ('Anchor 4', 1000), ('Anchor 5', 700), ('Anchor 6', 1500)])
        self.index = form._points_index(self.table)

    def test_recovers_a_known_rating_from_win_loss_alone(self):
        truth = 1400.0
        opponents = [('Anchor 1', 1900), ('Anchor 2', 1600), ('Anchor 3', 1300),
                     ('Anchor 4', 1000), ('Anchor 5', 700), ('Anchor 6', 1500)]
        # Deterministic outcomes at the true rating: win the ones the model says
        # are more likely than not, lose the rest. The fit must land near 1400.
        won = [vrs.expected(truth, p) > 0.5 for _, p in opponents]
        rows = results_for('Mystery', opponents, won)
        est, problem = form.estimate(rows, 'Mystery', self.index, self.now)
        self.assertIsNone(problem)
        self.assertLess(abs(est['rating'] - 1400), 120, est['rating'])
        self.assertEqual(est['matches'], 6)
        self.assertGreater(est['se'], 0)
        self.assertLess(est['interval'][0], est['rating'])
        self.assertGreater(est['interval'][1], est['rating'])

    def test_refuses_with_too_few_anchored_matches(self):
        rows = results_for('Mystery', [('Anchor 1', 1900), ('Anchor 2', 1600), ('Anchor 3', 1300)], [True, False, True])
        est, problem = form.estimate(rows, 'Mystery', self.index, self.now)
        self.assertIsNone(est)
        self.assertIn('at least 6', problem)

    def test_refuses_when_every_opponent_is_unlisted(self):
        rows = results_for('Mystery', [('Nobody A', 0), ('Nobody B', 0), ('Nobody C', 0),
                                       ('Nobody D', 0), ('Nobody E', 0)], [True] * 5)
        est, problem = form.estimate(rows, 'Mystery', self.index, self.now)
        self.assertIsNone(est)
        self.assertIn('uniquely listed', problem)

    def test_duplicate_standings_labels_are_not_used_as_anchors(self):
        table = {'as_of': '2026-10-05', 'teams': [
            {'standing': 1, 'points': 1500, 'name': 'Dup', 'roster': ['a'], 'details': 'x'},
            {'standing': 2, 'points': 900, 'name': 'Dup', 'roster': ['b'], 'details': 'y'},
            {'standing': 3, 'points': 1200, 'name': 'Solo', 'roster': ['c'], 'details': 'z'}]}
        index = form._points_index(table)
        self.assertNotIn(norm('Dup'), index)
        self.assertIn(norm('Solo'), index)


class LineTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 22, tzinfo=timezone.utc)
        self.table = standings([('Known', 1500), ('Anchor 1', 1700), ('Anchor 2', 1500),
                                ('Anchor 3', 1400), ('Anchor 4', 1300), ('Anchor 5', 1200),
                                ('Anchor 6', 1100), ('Anchor 7', 1000), ('Anchor 8', 900)])
        self.meta = {'file': 'standings_global_2026_10_05.md', 'commit': 'abc', 'origin': 'live official repository',
                     'raw_url': 'https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/abc/x',
                     'blob_url': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/abc/x'}
        opponents = [('Anchor 1', 1700), ('Anchor 2', 1500), ('Anchor 3', 1400),
                     ('Anchor 4', 1300), ('Anchor 5', 1200), ('Anchor 6', 1100),
                     ('Anchor 7', 1000), ('Anchor 8', 900)]
        self.corpus = {'captured_at': '2026-10-22T00:00:00Z', 'teams': {'Mystery': {
            'team': 'Mystery', 'role': 'unlisted', 'status': 'rescued',
            'results_url': 'https://www.hltv.org/results?team=1',
            'team_url': 'https://www.hltv.org/team/1/mystery',
            'results': results_for('Mystery', opponents, [True, True, False, True, False, True, False, True])}}}

    def fixture(self):
        return {'id': '999', 'teams': ['Known', 'Mystery'], 'state': 'open', 'probabilities': None,
                'flags': [], 'attempts': []}

    def test_one_listed_side_plus_one_estimated_side_produces_a_labelled_line(self):
        quote, problem = form.line(self.fixture(), self.table, self.meta, self.corpus, self.now)
        self.assertIsNone(problem)
        p = quote['probabilities']
        self.assertAlmostEqual(sum(p), 1.0, places=12)
        self.assertEqual(quote['bases'], ['valve_standings', 'hltv_results_estimate'])
        self.assertIn('form estimate', quote['warning'])
        self.assertIsNotNone(quote['interval'])
        self.assertLessEqual(quote['interval'][0], p[0])
        self.assertGreaterEqual(quote['interval'][1], p[0])
        self.assertEqual(quote['fixture_teams'], ['Known', 'Mystery'])

    def test_probability_matches_valve_formula_on_the_two_points(self):
        quote, _ = form.line(self.fixture(), self.table, self.meta, self.corpus, self.now)
        expected = 0.5 + vrs.SLOPE * (vrs.expected(1500, quote['points'][1]) - 0.5)
        self.assertAlmostEqual(quote['probabilities'][0], expected, places=12)

    def test_missing_corpus_is_refused_with_a_stated_reason(self):
        quote, problem = form.line(self.fixture(), self.table, self.meta, {'teams': {}}, self.now)
        self.assertIsNone(quote)
        self.assertIn('no verified HLTV results corpus', problem)

    def test_apply_writes_method_probabilities_and_a_pick(self):
        fx = self.fixture()
        form.apply(fx, self.table, self.meta, self.corpus, self.now)
        self.assertEqual(fx['method'], 'model_form')
        self.assertEqual(fx['pick'], fx['teams'][0] if fx['probabilities'][0] > fx['probabilities'][1] else fx['teams'][1])
        self.assertTrue(fx['evidence'])
        self.assertTrue(any('not a market price' in f for f in fx['flags']))

    def test_apply_never_overwrites_an_existing_market_line(self):
        fx = self.fixture()
        fx.update(probabilities=[0.6, 0.4], method='exchange', pick='Known')
        form.apply(fx, self.table, self.meta, self.corpus, self.now)
        self.assertEqual(fx['method'], 'exchange')
        self.assertEqual(fx['probabilities'], [0.6, 0.4])


class HoldoutTests(unittest.TestCase):
    def test_holdout_only_scores_teams_captured_for_validation(self):
        now = datetime(2026, 10, 22, tzinfo=timezone.utc)
        table = standings([('Known', 1500), ('Anchor 1', 1700), ('Anchor 2', 1500),
                           ('Anchor 3', 1400), ('Anchor 4', 1300), ('Anchor 5', 1200),
                           ('Anchor 6', 1100), ('Anchor 7', 1000), ('Anchor 8', 900)])
        opponents = [('Anchor 1', 1700), ('Anchor 2', 1500), ('Anchor 3', 1400),
                     ('Anchor 4', 1300), ('Anchor 5', 1200), ('Anchor 6', 1100),
                     ('Anchor 7', 1000), ('Anchor 8', 900)]
        corpus = {'teams': {
            'Known': {'team': 'Known', 'role': 'validation', 'status': 'rescued',
                      'results': results_for('Known', opponents, [True, True, True, False, True, True, True, True])},
            'Mystery': {'team': 'Mystery', 'role': 'unlisted', 'status': 'rescued',
                        'results': results_for('Mystery', opponents, [True] * 8)}}}
        report = form.holdout(table, corpus, now)
        self.assertEqual(report['summary']['n'], 1)
        self.assertEqual(report['rows'][0]['team'], 'Known')
        self.assertIn('error', report['rows'][0])
        self.assertIsInstance(report['summary']['mae'], float)


if __name__ == '__main__':
    unittest.main()

class ValidatorReplayTests(unittest.TestCase):
    """Both independent verifiers must accept a genuine row and reject a tampered one."""

    def setUp(self):
        from datetime import datetime, timezone
        self.now = datetime(2026, 10, 22, 1, 0, tzinfo=timezone.utc)
        table = standings([('Known', 1500), ('Anchor 1', 1700), ('Anchor 2', 1500),
                           ('Anchor 3', 1400), ('Anchor 4', 1300), ('Anchor 5', 1200),
                           ('Anchor 6', 1100), ('Anchor 7', 1000), ('Anchor 8', 900)])
        self.meta = {'file': 'standings_global_2026_10_05.md', 'commit': 'abc', 'origin': 'live official repository',
                     'raw_url': 'https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/abc/x',
                     'blob_url': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/abc/live/2026/x.md'}
        opponents = [('Anchor 1', 1700), ('Anchor 2', 1500), ('Anchor 3', 1400),
                     ('Anchor 4', 1300), ('Anchor 5', 1200), ('Anchor 6', 1100),
                     ('Anchor 7', 1000), ('Anchor 8', 900)]
        corpus = {'captured_at': '2026-10-22T00:30:00Z', 'teams': {'Mystery': {
            'team': 'Mystery', 'role': 'unlisted', 'status': 'rescued',
            'results_url': 'https://www.hltv.org/results?team=1',
            'team_url': 'https://www.hltv.org/team/1/mystery',
            'results': results_for('Mystery', opponents, [True, True, False, True, True, False, True, True])}}}
        self.fixture = {'id': '999', 'teams': ['Known', 'Mystery'], 'state': 'open', 'probabilities': None,
                        'flags': [], 'attempts': [], 'lock': '2026-10-23T11:54:00Z',
                        'start': '2026-10-23T12:00:00Z'}
        form.apply(self.fixture, table, self.meta, corpus, self.now)
        self.assertEqual(self.fixture['method'], 'model_form')

    def test_the_build_validator_replays_the_row(self):
        from scripts.validate import validate_form_row
        validate_form_row(self.fixture, self.fixture['evidence'][0], self.now)

    def test_the_independent_auditor_replays_the_row(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('audit', ROOT / 'verification-c6/audit_snapshot.py')
        audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit)
        problems = []

        def require(condition, message):
            if not condition:
                problems.append(message)

        audit.audit_form_row(self.fixture, self.fixture['probabilities'], self.now, require)
        self.assertEqual(problems, [])

    def test_a_tampered_rating_is_rejected_by_both(self):
        from scripts.validate import validate_form_row
        import importlib.util
        row = json.loads(json.dumps(self.fixture))
        row['evidence'][0]['parts'][1]['form']['rating'] += 40
        with self.assertRaises(AssertionError):
            validate_form_row(row, row['evidence'][0], self.now)
        spec = importlib.util.spec_from_file_location('audit', ROOT / 'verification-c6/audit_snapshot.py')
        audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit)
        problems = []

        def require(condition, message):
            if not condition:
                problems.append(message)

        audit.audit_form_row(row, row['probabilities'], self.now, require)
        self.assertTrue(any('optimum' in p or 'reproducible' in p or 'mismatch' in p for p in problems), problems)
