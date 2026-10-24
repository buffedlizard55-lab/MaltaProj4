"""The legacy root fallback must never be able to withhold a verified fresh board.

Measured failure this pins (2026-10-24). Every ``pages.yml`` run on ``main`` from
09:03Z to 16:07Z failed at step 15, *Keep the legacy main:/ root fallback on the
verified build*: 40080448344, 40082763751, 40084520702 and 40097410704. The
refresh, quarantine, build, independent row audit and all Chromium gates in those
runs succeeded; only the legacy-root staging step failed (its own annotation:
*"The staged root failed its own validator or unit gate"*, i.e. ``publish()``
returned 3). Because a failed step fails the job, ``upload-pages-artifact`` and
the whole ``deploy`` job were *skipped* as well, so the freshly verified snapshot
was never published. The public board kept serving the 2026-10-24T08:06:51Z
snapshot until its eight-hour window closed, and then withheld all 29 picks --
the live site read "22 open CS2 match(es) - 0 with a pick" at 16:2xZ (measured in
run 40110028068's independent audit, ``actionable: 0``).

The fix kept every existing safety rule and changed only the blast radius:

* the root is still staged only when ``scripts.validate --site .`` and the
  committed unit suite pass on the staged tree (``rc 3`` still refuses to commit,
  which is what keeps ``main`` green after ``dce494b``);
* the step is ``continue-on-error`` so the verified artifact still deploys;
* a follow-up step publishes the exact gate and the failing test names, plus
  ``runtime/root-fallback.json``, instead of leaving an unread annotation.

These tests read the workflow text rather than a parsed document, so they keep
working without a YAML dependency, and they fail if anyone removes the guard,
removes the non-blocking behaviour, or lets the artifact upload depend on the
fallback again.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / '.github/workflows/pages.yml').read_text()

STAGING_NAME = 'Keep the legacy main:/ root fallback on the verified build'
EXPLAIN_NAME = 'Explain a legacy-root failure without withholding the verified board'


def job(name='verify-build'):
    match = re.search(r'^  %s:\n(.*?)(?=^  \w|\Z)' % re.escape(name), WORKFLOW, re.S | re.M)
    assert match, 'no %s job in .github/workflows/pages.yml' % name
    return match.group(1)


def step(name, text=None):
    """The YAML block for one step, from its ``- name:`` line to the next one."""
    text = job() if text is None else text
    start = text.index('- name: ' + name)
    following = text.find('\n      - ', start + 1)
    return text[start:] if following == -1 else text[start:following]


class RootFallbackCannotWithholdTheBoard(unittest.TestCase):
    def setUp(self):
        self.job = job()
        self.staging = step(STAGING_NAME, self.job)

    def test_the_staging_step_is_non_blocking(self):
        self.assertIn('continue-on-error: true', self.staging,
                      'a legacy-root failure must not fail the job that uploads the artifact')

    def test_the_staging_step_keeps_its_own_safety_gates(self):
        # rc 3 must still refuse to commit: the whole point of the 2026-10-24
        # freeze was that a broken root was *not* published after dce494b.
        # Both gates now run through scripts.staged_gate, which is the module that
        # tells a rotation-coupled unit failure apart from a real one.
        self.assertIn('python -m scripts.staged_gate --check data', self.staging)
        self.assertIn('python -m scripts.staged_gate --check units', self.staging)
        self.assertIn('return 3', self.staging)
        self.assertIn('report 3 pinned-gate', self.staging)
        self.assertEqual(self.staging.count('[ "$rc" = "3" ]'), 2,
                         'both the first pass and the replay must refuse to commit')

    def test_the_gates_are_checked_before_anything_is_committed(self):
        commit = self.staging.index('git commit -m "Publish the verified build')
        for gate in ('scripts.staged_gate --check data',
                     'scripts.staged_gate --check units'):
            self.assertLess(self.staging.index(gate), commit,
                            '%s must run before the root is committed' % gate)

    def test_the_pre_staging_snapshot_is_captured_before_the_root_is_staged(self):
        # The control the units gate compares against has to be the board the root
        # carried *before* this run, so it is copied before the stager runs.
        capture = self.staging.index('runtime/pre-staging-latest.json')
        stage = self.staging.index('scripts.publish_root_fallback --public public')
        self.assertLess(capture, stage)

    def test_a_failure_writes_a_machine_readable_report(self):
        self.assertIn("runtime/root-fallback.json", self.staging)
        self.assertIn("'artifact_still_deploys'", self.staging)

    def test_the_failure_is_explained_with_the_failing_gate(self):
        explain = step(EXPLAIN_NAME, self.job)
        self.assertIn("steps.rootfallback.outcome == 'failure'", explain)
        self.assertIn('runtime/root-gate-validate.log', explain)
        self.assertIn('runtime/root-gate-unit.log', explain)
        self.assertIn('grep -E', explain)
        self.assertIn('FAIL|ERROR', explain)
        self.assertIn('GITHUB_STEP_SUMMARY', explain)

    def test_the_artifact_and_the_deploy_do_not_depend_on_the_fallback(self):
        # The upload must run whenever the refresh/build gates passed, and the
        # deploy job must be reachable even when the root step broke.
        upload = self.job[self.job.index('- uses: actions/upload-pages-artifact@'):]
        self.assertIn("steps.gate.outputs.publish == 'true'", upload)
        self.assertNotIn('rootfallback', upload)
        deploy = job('deploy')
        self.assertNotIn('rootfallback', deploy)
        self.assertIn("needs.verify-build.outputs.publish == 'true'", deploy)

    def test_no_other_step_reads_the_root_outcome_as_a_gate(self):
        # Guards against a future edit that re-couples publication to the root.
        for match in re.finditer(r'rootfallback', self.job):
            line = self.job[:match.start()].rsplit('\n', 1)[-1] + self.job[match.start():].split('\n', 1)[0]
            self.assertNotIn("if: steps.rootfallback.outputs", line)


class TheReportHelperIsWellFormed(unittest.TestCase):
    """The report helper must emit JSON the explanation step can echo verbatim."""

    def test_the_report_helper_writes_valid_json(self):
        source = step(STAGING_NAME, job())
        start = source.index('report() {')
        end = source.index('publish() {')
        body = source[start:end]
        self.assertIn("json.dumps({", body)
        self.assertIn('rc ==', body)
        self.assertNotIn('>>', body.replace("'@@'", ''))


if __name__ == '__main__':
    unittest.main()


class NoEdgeIsAFirstClassState(unittest.TestCase):
    """The documented even-line state must be classified, counted and rendered.

    Measured problem: the 2026-10-24T16:24Z capture contained one open row that
    published a probability and no pick (Color vs ex-Zero Tenacity, 0.500/0.500).
    ``scripts.summary.counts`` derived ``with_pick`` and ``priced`` separately, so
    the executive summary advertised 22 picks for 21 picks and the committed
    contract suite failed. These tests pin one canonical classification.
    """

    ROW = {'id': '1079200', 'state': 'open', 'pick': None, 'probabilities': [0.5, 0.5],
           'fair_odds': [2.0, 2.0], 'method': 'exchange',
           'reason': 'Equal verified prices; no directional edge.'}

    def test_a_documented_even_line_is_no_edge(self):
        from scripts import summary
        self.assertTrue(summary.is_no_edge(self.ROW))

    def test_a_picked_row_is_never_no_edge(self):
        from scripts import summary
        self.assertFalse(summary.is_no_edge(dict(self.ROW, pick='Color')))

    def test_an_even_row_without_the_limitation_is_not_no_edge(self):
        from scripts import summary
        self.assertFalse(summary.is_no_edge(dict(self.ROW, reason=None)))

    def test_an_unpriced_row_is_not_no_edge(self):
        from scripts import summary
        self.assertFalse(summary.is_no_edge(dict(self.ROW, probabilities=None)))

    def test_counts_partition_the_open_board(self):
        from scripts import summary
        picked = {'id': '1', 'state': 'open', 'pick': 'A', 'probabilities': [0.6, 0.4], 'method': 'exchange'}
        unpicked = {'id': '2', 'state': 'open', 'pick': None, 'probabilities': None, 'reason': 'no line'}
        closed = {'id': '3', 'state': 'not_open', 'pick': None, 'probabilities': None}
        c = summary.counts([picked, self.ROW, unpicked, closed])
        self.assertEqual(summary.partition(c), (1, 1, 1))
        self.assertEqual(c['open'], 3)
        self.assertEqual((c['priced'], c['with_pick'], c['no_edge'], c['unresolved']), (2, 1, 1, 1))
        self.assertEqual(c['market'] + c['model'] + c['research'] + c['no_edge'] + c['none'], c['open'])

    def test_partition_refuses_a_board_that_does_not_add_up(self):
        from scripts import summary
        with self.assertRaises(AssertionError):
            summary.partition({'with_pick': 1, 'no_edge': 1, 'unresolved': 1, 'open': 4})

    def test_the_method_page_documents_the_even_line_rule(self):
        # The method page is generated, so its source of truth is build.py.
        source = (ROOT / 'scripts' / 'build.py').read_text()
        self.assertIn('An exactly even two-way price supports no directional pick', source)
        self.assertIn('never a coin flip', source)
        self.assertIn('the ladder continues to our model line or a research tier', source)


class EvenLinesNeverFreezeTheLadder(unittest.TestCase):
    """An exactly even accepted line must not become the published probability."""

    def test_the_rule_is_implemented_after_the_wide_tier_check(self):
        source = (ROOT / 'scripts' / 'core.py').read_text()
        wide = source.index('Wide exchange quote is exactly even')
        tight = source.index('Accepted line is exactly even')
        update = source.index("fixture.update(probabilities=p", tight)
        self.assertLess(wide, tight, 'the wide-tier rule stays first')
        self.assertLess(tight, update, 'the even check must run before the row is priced')
        self.assertIn('ladder continues', source[wide:update],
                      'the rejected even line must be explained, not silently dropped')


class RotationOnlyFailuresCannotFreezeTheBoard(unittest.TestCase):
    """A unit failure that only exists because the board advanced must not refuse.

    Measured on 2026-10-24: the staged gate returned 3 for seven hours because the
    freshly refreshed snapshot no longer contained fixtures 1083121 and 1081152,
    which two modules index in ``data/latest.json``. The tree, the build and the
    fresh data were all sound. ``scripts.staged_gate`` re-runs each failing module
    against the pre-staging snapshot and only then decides.
    """

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'tests').mkdir()
        (self.root / 'data').mkdir()
        (self.root / 'runtime').mkdir()
        (self.root / 'data' / 'latest.json').write_text('{"matches": [{"id": "2222222"}]}\n')
        self.previous = self.root / 'previous.json'
        self.previous.write_text('{"matches": [{"id": "1111111"}, {"id": "2222222"}]}\n')

    def tearDown(self):
        self.tmp.cleanup()

    def write_module(self, name, body):
        (self.root / 'tests' / (name + '.py')).write_text(body)

    def run_gate(self, *extra):
        import contextlib
        import io
        from scripts import staged_gate
        # The gate prints the captured suite output on refusal; keep the test log clean.
        with contextlib.redirect_stdout(io.StringIO()):
            return staged_gate.main(['--check', 'units', '--root', str(self.root),
                                     '--previous', str(self.previous),
                                     '--report', str(self.root / 'runtime' / 'gate.json')]
                                    + list(extra))

    def test_the_parser_reads_unittest_lines_and_ignores_auditor_lines(self):
        from scripts import staged_gate
        log = (
            'FAIL: 1082769 K27 vs NEXORA: unresolved method must be None\n'
            'ERROR: setUpClass (test_session_35c6e1e9.VerifierConsultsTheSourcedAliasRegister)\n'
            'ERROR: test_known (test_session_e9be3e6b.SourceLadderVerification.test_known)\n'
            'FAIL: same_module_again (test_session_e9be3e6b.Other.test_x)\n'
        )
        self.assertEqual(staged_gate.failing_modules(log),
                         ['test_session_35c6e1e9', 'test_session_e9be3e6b'])
        self.assertEqual(staged_gate.failing_targets(log),
                         ['test_session_35c6e1e9.VerifierConsultsTheSourcedAliasRegister',
                          'test_session_e9be3e6b.SourceLadderVerification.test_known',
                          'test_session_e9be3e6b.Other.test_x'])

    def test_a_failure_that_disappears_on_the_older_board_is_published(self):
        self.write_module('test_pinned', (
            'import json, pathlib, unittest\n'
            'DATA = json.loads((pathlib.Path(__file__).resolve().parents[1] / "data" / "latest.json").read_text())\n'
            'class Pinned(unittest.TestCase):\n'
            '    def test_fixture_is_live(self):\n'
            '        self.assertIn("1111111", [m["id"] for m in DATA["matches"]])\n'))
        self.assertEqual(self.run_gate(), 0)
        # The staged snapshot must be back on disk, not the control copy.
        self.assertIn('2222222', (self.root / 'data' / 'latest.json').read_text())
        report = (self.root / 'runtime' / 'gate.json').read_text()
        self.assertIn('test_pinned', report)
        self.assertIn('rotation_coupled', report)

    def test_a_failure_that_reproduces_on_the_older_board_still_refuses(self):
        self.write_module('test_broken', (
            'import unittest\n'
            'class Broken(unittest.TestCase):\n'
            '    def test_always_fails(self):\n'
            '        self.assertEqual(1, 2)\n'))
        self.assertEqual(self.run_gate(), 3)
        report = (self.root / 'runtime' / 'gate.json').read_text()
        self.assertIn('not caused by the snapshot advancing', report)

    def test_no_previous_snapshot_means_refuse_rather_than_guess(self):
        # Fail closed: without the control the failure is unexplained, and an
        # unexplained failure must never be published green.
        self.write_module('test_pinned', (
            'import json, pathlib, unittest\n'
            'DATA = json.loads((pathlib.Path(__file__).resolve().parents[1] / "data" / "latest.json").read_text())\n'
            'class Pinned(unittest.TestCase):\n'
            '    def test_fixture_is_live(self):\n'
            '        self.assertIn("1111111", [m["id"] for m in DATA["matches"]])\n'))
        self.previous.unlink()
        self.assertEqual(self.run_gate(), 3)
        self.assertIn('no pre-staging snapshot', (self.root / 'runtime' / 'gate.json').read_text())


class StagedGateIsWiredIntoTheWorkflow(unittest.TestCase):
    def setUp(self):
        self.staging = step(STAGING_NAME, job())

    def test_the_explanation_step_reports_the_gate_result(self):
        explain = step(EXPLAIN_NAME, job())
        self.assertIn('runtime/staged-gate.json', explain)
        self.assertIn('GITHUB_STEP_SUMMARY', explain)

    def test_the_classifier_is_documented_where_the_decision_is_made(self):
        source = (ROOT / 'scripts' / 'staged_gate.py').read_text()
        self.assertIn('rotation', source)
        self.assertIn('fail-closed', source)
        self.assertIn('pre-staging snapshot', source)
