"""Session bd650209: the line-by-line verifier is falsifiable, and the
committed board passes it.

The verifier (``research/session-bd650209/verify_board.py``) is the artefact this
session publishes for manual review: for every open priced match it re-derives
the percentages, the pick, the fair odds and the presence of a source link from
the row's own stored evidence. These tests exist so that a verifier which always
prints PASS is caught:

* the committed snapshot must pass every check;
* a flipped pick, a broken sum, a dropped source link, an impossible percentage
  and an already-locked row must each fail the specific check that covers them;
* a row with no pick must be reported as unresolved with its reason and must
  never acquire a number.

No fixture id, team name, date or count in this file is pinned to today's
rotating board.
"""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / 'research' / 'session-bd650209' / 'verify_board.py'
SNAPSHOT = ROOT / 'data' / 'latest.json'


def load_verifier():
    spec = importlib.util.spec_from_file_location('verify_board_bd650209', VERIFIER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifierModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_verifier()
        cls.data = json.loads(SNAPSHOT.read_text())

    def test_verifier_declares_the_published_ladder_labels(self):
        for label in ('exchange', 'exchange_wide', 'bookmaker_fallback', 'model_vrs',
                      'model_vrs_mirror', 'research_vrs_single', 'research_rank',
                      'research_rank_single', 'research_form'):
            self.assertIn(label, self.module.METHODS)

    def test_the_committed_board_passes_every_check(self):
        rows = [m for m in self.data['matches']
                if m.get('state') == 'open' and m.get('probabilities') is not None]
        self.assertTrue(rows, 'the committed snapshot must contain at least one priced open match')
        captured = self.module.parse(self.data['generated_at'])
        for row in rows:
            with self.subTest(fixture=row['id']):
                failed = [k for k, ok in self.module.row_checks(row, captured).items() if not ok]
                self.assertEqual(failed, [])

    def test_a_flipped_pick_fails(self):
        row = next(m for m in self.data['matches']
                   if m.get('state') == 'open' and m.get('probabilities') and m.get('pick'))
        mutated = json.loads(json.dumps(row))
        mutated['pick'] = next(t for t in mutated['teams'] if t != mutated['pick'])
        self.assertFalse(self.module.row_checks(mutated, self.module.parse(self.data['generated_at']))['P4'])

    def test_a_broken_sum_fails(self):
        row = next(m for m in self.data['matches'] if m.get('probabilities'))
        mutated = json.loads(json.dumps(row))
        mutated['probabilities'][0] += 0.01
        self.assertFalse(self.module.row_checks(mutated, self.module.parse(self.data['generated_at']))['P2'])

    def test_wrong_fair_odds_fail(self):
        row = next(m for m in self.data['matches'] if m.get('fair_odds'))
        mutated = json.loads(json.dumps(row))
        mutated['fair_odds'][0] += 0.01
        self.assertFalse(self.module.row_checks(mutated, self.module.parse(self.data['generated_at']))['P3'])

    def test_a_missing_source_link_fails(self):
        row = next(m for m in self.data['matches'] if m.get('evidence'))
        mutated = json.loads(json.dumps(row))
        for quote in mutated['evidence']:
            quote.pop('api_url', None)
            quote.pop('url', None)
        self.assertFalse(self.module.row_checks(mutated, self.module.parse(self.data['generated_at']))['P5'])

    def test_an_impossible_percentage_fails(self):
        row = next(m for m in self.data['matches'] if m.get('probabilities'))
        mutated = json.loads(json.dumps(row))
        mutated['probabilities'] = [1.4, -0.4]
        self.assertFalse(self.module.row_checks(mutated, self.module.parse(self.data['generated_at']))['P1'])

    def test_a_locked_row_fails(self):
        row = next(m for m in self.data['matches'] if m.get('probabilities'))
        mutated = json.loads(json.dumps(row))
        mutated['lock'] = '2000-01-01T00:00:00Z'
        self.assertFalse(self.module.row_checks(mutated, self.module.parse(self.data['generated_at']))['P8'])


class ReportingTests(unittest.TestCase):
    def test_report_separates_unresolved_rows_and_gives_them_no_number(self):
        module = load_verifier()
        import tempfile
        data = {"generated_at": "2026-10-25T00:00:00Z", "fixtures_observed_at": "2026-10-25T00:00:00Z",
                "coverage": "verified", "matches": [
                    {"id": "1", "state": "open", "teams": ["A", "B"], "start": "2026-10-25T09:00:00Z",
                     "lock": "2026-10-25T08:54:00Z", "probabilities": [0.7, 0.3], "fair_odds": [1.4285714285714286, 3.3333333333333335],
                     "pick": "A", "method": "exchange", "source_url": "https://www.hotspawn.com/matches/a-vs-b-1",
                     "evidence": [{"provider": "Polymarket", "api_url": "https://gamma-api.polymarket.com/markets/1",
                                   "url": "https://polymarket.com/event/a"}]},
                    {"id": "2", "state": "open", "teams": ["C", "D"], "start": "2026-10-25T10:00:00Z",
                     "lock": "2026-10-25T09:54:00Z", "probabilities": None, "fair_odds": None, "pick": None,
                     "method": None, "source_url": "https://www.hotspawn.com/matches/c-vs-d-2",
                     "attempts": [{"provider": "Polymarket", "status": "unresolved"}],
                     "reason": "No exact pair", "evidence": []}]}
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = Path(tmp) / 'snap.json'
            snapshot.write_text(json.dumps(data))
            out = Path(tmp) / 'report.md'
            module.main.__globals__  # module imported by path; main reads sys.argv
            import sys
            argv = sys.argv
            sys.argv = ['verify_board.py', str(snapshot), '--output', str(out)]
            try:
                rc = module.main()
            finally:
                sys.argv = argv
            text = out.read_text()
        self.assertEqual(rc, 0)
        self.assertIn('Open matches with no pick (unresolved)', text)
        self.assertIn('| [2](https://www.hotspawn.com/matches/c-vs-d-2) | C vs D |', text)
        self.assertIn('No exact pair', text)
        self.assertIn('1 of 1 priced rows pass every re-derived check', text)


if __name__ == '__main__':
    unittest.main()
