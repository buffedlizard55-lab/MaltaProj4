"""Session aeafcbe6: the 8.5-hour publication freeze of 2026-10-24, and the two ways it happened.

What was measured
-----------------
`pages.yml` on `main` failed at the single step *"Keep the legacy main:/ root fallback on
the verified build"* on every push and schedule from 2026-10-24T08:12Z (runs 40077144677,
40080448344, 40082763751, 40084520702, 40097410704). Steps 8–14 — the unit gate, the live
refresh, the quarantine, the build with the independent row audit, and the phone/browser
gates — all reported success; `upload-pages-artifact` and the whole `deploy` job were
skipped, so the public board stayed at the 2026-10-24T08:06:51Z snapshot until its own
eight-hour window closed.

This sandbox has no egress to Hotspawn, HLTV or Polymarket, so the failure could not be
reproduced here. `.github/workflows/diagnose-aeafcbe6.yml` re-ran the real refresh on
GitHub's egress and replayed that step sub-command by sub-command; the receipt is
`research/diagnose-aeafcbe6/` (`00-return-codes.txt`: `staged_unit_rc=1`, everything else
0; `11-staged-unit.log`: 42 failures). The cause was data: Hotspawn fixture 1079200
(Color vs ex-Zero Tenacity) matched Polymarket market 6072812, whose `outcomePrices` were
the untouched initialisation `["0.5","0.5"]`. A tier published `probabilities: [0.5, 0.5]`
with `pick: null`, and because every later tier begins with
`if fixture['probabilities'] is not None: return`, that row could never be picked or priced
by the ladder. A second, independent freeze cause appeared on the same capture:
`test_session_35c6e1e9` and `test_session_e9be3e6b` hard-indexed the live board by fixture
ids Hotspawn had already rotated out (`1083121`, `1081152`), raising `StopIteration` /
`KeyError`.

The rule itself was implemented on `main` by sessions 6b8b4be0 and 2b856884
(`scripts.core.directional()`, `fixture['no_edge_lines']`), and those repairs were adopted at
integration rather than layered over. What this module pins is what this session added and
verified end to end:

1. the neutral-line convention is enforced in every tier and in the site's own prose —
   a pick and its probability are published together or not at all;
2. no test may index the *live* board by a bare fixture id: Hotspawn rotates fixtures out as
   they lock, so that pattern freezes publication again at the next rotation unless the
   literal is asserted against a dated receipt or the rotated row is skipped;
3. the publisher publishes the failing test names to the run summary and keeps the log as
   an artifact, so a future rejection is diagnosable from the run page rather than from an
   unreadable job log;
4. the phone board is measured on a *fresh* capture (`tests/browser_aeafcbe6.cjs`).
"""
import json
import re
import unittest
from pathlib import Path

from scripts import core

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())

# The capture whose staged-root replay produced these findings, retained immutably.
DIAGNOSIS = ROOT / 'research' / 'diagnose-aeafcbe6'


class NeutralLineForEveryTierTests(unittest.TestCase):
    """`directional()` is the single comparison; no tier may invent a side."""

    def test_directional_matches_the_documented_tolerance(self):
        self.assertEqual(core.EVEN_TOLERANCE, 1e-4)
        self.assertIsNone(core.directional([0.5, 0.5]))
        self.assertIsNone(core.directional([0.50001, 0.49999]))
        self.assertEqual(core.directional([0.6, 0.4]), 0)
        self.assertEqual(core.directional([0.4, 0.6]), 1)
        with self.assertRaises(ValueError):
            core.directional([0.5])

    def test_every_pricing_tier_uses_the_single_comparison(self):
        # scripts/core.py keeps a defensive `pick=None if ...` on its publication
        # line, but the neutral branch above it raises first, so that line is
        # unreachable for an even pair. What must not regress is that every tier
        # asks the shared comparison and retains the neutral line as context.
        for name in ('scripts/core.py', 'scripts/vrs.py', 'scripts/vrs_mirror.py'):
            source = (ROOT / name).read_text()
            self.assertIn('directional(', source, name)
            self.assertIn("no_edge_lines", source, name)

    def test_a_neutral_quote_is_retained_as_context_and_the_ladder_continues(self):
        source = (ROOT / 'scripts/core.py').read_text()
        self.assertIn("fixture.setdefault('no_edge_lines', [])", source)
        self.assertIn('Continue independent research', source)


class PublicationDiagnosticsTests(unittest.TestCase):
    """The publisher must never again hide *which* assertion froze the board."""

    @classmethod
    def setUpClass(cls):
        cls.yml = (ROOT / '.github' / 'workflows' / 'pages.yml').read_text()

    def test_the_staged_root_unit_gate_is_still_fatal(self):
        start = self.yml.index('Keep the legacy main:/ root fallback on the verified build')
        step = self.yml[start:self.yml.index('Record the exact artifact expected at the public site')]
        self.assertIn('python -m unittest discover -s tests 2>&1 | tee runtime/staged-root-unit.log', step)
        self.assertIn('return 3', step)
        self.assertIn('runtime/staged-root-unit.log', step)

    def test_the_failing_test_names_are_published_to_the_run_summary(self):
        start = self.yml.index('Keep the legacy main:/ root fallback on the verified build')
        step = self.yml[start:self.yml.index('Record the exact artifact expected at the public site')]
        self.assertIn('GITHUB_STEP_SUMMARY', step)
        self.assertIn("grep -E '^(FAIL|ERROR):' runtime/staged-root-unit.log", step)

    def test_the_log_is_kept_as_an_artifact(self):
        self.assertIn('staged-root-unit-log-${{ github.run_id }}', self.yml)
        self.assertIn('if-no-files-found: ignore', self.yml)

    def test_the_gate_still_runs_after_the_build_and_validate(self):
        start = self.yml.index('Keep the legacy main:/ root fallback on the verified build')
        step = self.yml[start:self.yml.index('Record the exact artifact expected at the public site')]
        self.assertLess(step.index('scripts.validate --data data/latest.json --site .'),
                        step.index('unittest discover -s tests'))
        self.assertLess(step.index('unittest discover -s tests'),
                        step.index('git commit -m "Publish the verified build'))


class RotationGuardTests(unittest.TestCase):
    """A pinned *live* fixture id is a time bomb: Hotspawn rotates rows out as they lock."""

    PATTERN = re.compile(
        r"\bSNAPSHOT\[['\"]matches['\"]\] if m\[['\"]id['\"]\] == ['\"]\d{6,8}['\"]")
    ARCHIVE = re.compile(r"(snapshot\.json|HARVEST_SNAPSHOT|ARCHIVE_SNAPSHOT|archived|archive)")

    def test_no_module_indexes_the_live_board_by_a_bare_fixture_id(self):
        offenders = []
        for path in sorted((ROOT / 'tests').glob('test_*.py')):
            text = path.read_text()
            if not self.PATTERN.search(text):
                continue
            if self.ARCHIVE.search(text) or 'skipTest' in text:
                continue
            offenders.append(path.name)
        self.assertEqual([], offenders,
                         'a pinned live fixture id freezes publication at the next rotation; '
                         'assert it against a dated receipt or skip the rotated row')

    def test_the_two_modules_that_froze_the_run_read_a_dated_receipt(self):
        for name in ('test_session_35c6e1e9.py', 'test_session_e9be3e6b.py'):
            text = (ROOT / 'tests' / name).read_text()
            self.assertIn('snapshot.json', text, name)
            self.assertNotRegex(text, r"next\(m for m in SNAPSHOT\[['\"]matches['\"]\]")

    def test_the_receipt_that_repairs_them_exists_and_holds_their_rows(self):
        archive = json.loads((ROOT / 'research/harvest-ce45f672/snapshot.json').read_text())
        ids = {m['id'] for m in archive['matches']}
        for fixture in ('1083121', '1081152'):
            self.assertIn(fixture, ids)


class RetentionTests(unittest.TestCase):
    """The diagnosis this session acted on must stay readable in the repository."""

    def test_the_return_codes_of_the_reproducing_run_are_retained(self):
        codes = (DIAGNOSIS / '00-return-codes.txt').read_text()
        for key in ('refresh_rc=0', 'build_rc=0', 'published_validate_rc=0',
                    'root_fallback_rc=0', 'staged_validate_rc=0'):
            self.assertIn(key, codes)
        # The reproducing run ended with the staged unit suite red; the verifying run
        # that followed the repair ended with it green. Both are on the record.
        self.assertIn('staged_unit_rc=1', codes)
        self.assertIn('staged_unit_rc=0', codes)

    def test_the_capture_counts_are_retained(self):
        coverage = (DIAGNOSIS / '12-coverage.md').read_text()
        self.assertIn('open with pick:', coverage)
        self.assertIn('open without pick: []', coverage)

    def test_the_phone_measurements_are_retained(self):
        receipt = json.loads((ROOT / 'research/session-aeafcbe6/mobile-measurements.json').read_text())
        self.assertEqual([], receipt['failures'])
        widths = sorted(v['viewport']['width'] for v in receipt['viewports'])
        self.assertEqual([320, 390, 412], widths)
        for viewport in receipt['viewports']:
            self.assertTrue(viewport['home']['picks_link_reachable'], viewport['name'])
            self.assertTrue(viewport['home']['unresolved_link'], viewport['name'])
            self.assertFalse(viewport['home']['horizontalOverflow'], viewport['name'])
            self.assertEqual(2, len(viewport['board']['percentages']), viewport['name'])
            self.assertTrue(viewport['board']['pick'], viewport['name'])


class CommittedBoardTests(unittest.TestCase):
    """The board contract the frozen run violated, checked on whatever is committed now."""

    def test_no_published_row_carries_a_probability_without_a_pick(self):
        for match in SNAPSHOT['matches']:
            if match.get('probabilities') is not None:
                self.assertIsNotNone(match.get('pick'), match['id'])
                self.assertIsNotNone(core.directional(match['probabilities']), match['id'])
            else:
                self.assertIsNone(match.get('pick'), match['id'])
                self.assertIsNone(match.get('fair_odds'), match['id'])

    def test_every_open_row_is_picked_and_priced_or_explicitly_unresolved(self):
        opens = [m for m in SNAPSHOT['matches'] if m.get('state') == 'open']
        self.assertTrue(opens, 'a snapshot with no open rows cannot prove coverage')
        for match in opens:
            if match.get('pick'):
                self.assertIsNotNone(match.get('probabilities'), match['id'])
            else:
                self.assertIsNone(match.get('probabilities'), match['id'])
                self.assertTrue(match.get('reason'), match['id'])
                self.assertTrue(match.get('attempts'), match['id'])


if __name__ == '__main__':
    unittest.main()
