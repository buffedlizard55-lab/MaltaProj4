"""Session a30d31a0 (2026-10-24): the root fallback may never roll newer source back.

``main`` (``dce494b``) failed the unit suite that every scheduled refresh runs
*before* it refreshes, so the board would have frozen again. Run ``40068512182``
built from ``dd92178``; PR #245 merged as ``4a50ea4`` while it ran; the step's
replay path re-staged the older build over the newer ``origin/main`` and
committed ``dce494b`` with the pre-#245 root stylesheet. The step's own
validate/unit lines did not stop the commit because ``set +e`` is active around
``publish()``. (The second defect on ``dce494b`` -- the independent verifier
refusing a sourced identity alias -- was fixed by PR #251 and is tested there.)

The workflow tests execute the real step script from ``pages.yml`` against a
throwaway origin and clone; nothing here pins a fixture ID, team or date.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts import publish_root_fallback as prf
from scripts import stage_legacy

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / '.github' / 'workflows' / 'pages.yml').read_text(encoding='utf-8')
STEP_NAME = '      - name: Keep the legacy main:/ root fallback on the verified build'
NEXT_STEP = '      - name: Record the exact artifact expected at the public site'
HAS_GIT = shutil.which('git') is not None


def step_script():
    """The exact bash body of the root-fallback step, de-indented from the YAML."""
    block = WORKFLOW.split(STEP_NAME, 1)[1].split(NEXT_STEP, 1)[0]
    body = block.split('        run: |\n', 1)[1]
    return '\n'.join(line[10:] if line.startswith(' ' * 10) else line.strip() for line in body.splitlines()) + '\n'


# ---------------------------------------------------------------------------
# 1a. The publisher's source-revision rule, in isolation.
# ---------------------------------------------------------------------------
class SourcePathClassification(unittest.TestCase):
    def test_generated_outputs_documents_and_research_are_not_build_inputs(self):
        for path in sorted(stage_legacy.ALLOWED | stage_legacy.EXTRA) + [
                'COORDINATION.md', 'README.md', 'research/session-x/REPORT.md']:
            self.assertFalse(prf.is_source_path(path), path)

    def test_everything_the_build_or_gates_read_is_a_build_input(self):
        for path in ('site/assets/style.css', 'site/assets/app.js', 'scripts/build.py',
                     'data/identities.json', 'data/review-notes.json', 'data/book-receipts.json',
                     'data/analysis.json', 'data/vrs/meta.json', 'tests/test_x.py',
                     '.github/workflows/pages.yml', 'verification-c6/audit_snapshot.py',
                     'package.json', 'requirements.txt'):
            self.assertTrue(prf.is_source_path(path), path)

    def test_the_stylesheet_pair_that_dce494b_split_is_classified_correctly(self):
        # The canonical copy is an input; the root copy is the staged output.
        self.assertTrue(prf.is_source_path('site/assets/style.css'))
        self.assertFalse(prf.is_source_path('assets/style.css'))


def git(cwd, *args, check=True):
    return subprocess.run(['git', *args], cwd=str(cwd), check=check, capture_output=True, text=True)


def init_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    git(path, 'init', '-q', '-b', 'main')
    git(path, 'config', 'user.name', 'test')
    git(path, 'config', 'user.email', 'test@example.invalid')
    git(path, 'config', 'commit.gpgsign', 'false')


def commit_all(path, message):
    git(path, 'add', '-A')
    git(path, 'commit', '-q', '-m', message)
    return git(path, 'rev-parse', 'HEAD').stdout.strip()


@unittest.skipUnless(HAS_GIT, 'git is required')
class SourceDriftDetection(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / 'repo'
        init_repo(self.repo)
        (self.repo / 'site/assets').mkdir(parents=True)
        (self.repo / 'site/assets/style.css').write_text('a{}\n')
        (self.repo / 'index.html').write_text('<p>old</p>\n')
        self.base = commit_all(self.repo, 'base')

    def tearDown(self):
        self.tmp.cleanup()

    def test_same_revision_has_no_drift(self):
        self.assertEqual(prf.source_drift(self.base, 'HEAD', self.repo), [])

    def test_output_and_research_only_commits_are_not_drift(self):
        (self.repo / 'index.html').write_text('<p>new</p>\n')
        (self.repo / 'research').mkdir()
        (self.repo / 'research/r.md').write_text('note\n')
        (self.repo / 'COORDINATION.md').write_text('board\n')
        commit_all(self.repo, 'outputs and receipts only')
        self.assertEqual(prf.source_drift(self.base, 'HEAD', self.repo), [])

    def test_a_newer_canonical_stylesheet_is_drift(self):
        (self.repo / 'site/assets/style.css').write_text('a{}\n}\n')
        commit_all(self.repo, 'close the media block')
        self.assertEqual(prf.source_drift(self.base, 'HEAD', self.repo), ['site/assets/style.css'])

    def test_unknown_or_missing_revisions_fail_closed(self):
        self.assertTrue(prf.source_drift('', 'HEAD', self.repo))
        self.assertTrue(prf.source_drift('0' * 40, 'HEAD', self.repo))
        self.assertTrue(prf.source_drift(self.base, '0' * 40, self.repo))

    def test_a_root_outside_any_repository_has_no_source_to_roll_back(self):
        plain = Path(self.tmp.name) / 'plain'
        plain.mkdir()
        self.assertEqual(prf.source_drift('deadbeef', 'HEAD', plain), [])
        self.assertEqual(prf.source_drift('deadbeef', 'HEAD', Path(self.tmp.name) / 'missing'), [])

    def test_check_drift_cli_exit_codes(self):
        cwd = os.getcwd()
        try:
            os.chdir(self.repo)
            with open(os.devnull, 'w') as sink:
                stdout = sys.stdout
                sys.stdout = sink
                try:
                    clean = prf.main(['--check-drift', '--revision', self.base, '--against', 'HEAD'])
                    (self.repo / 'site/assets/style.css').write_text('b{}\n')
                    commit_all(self.repo, 'source change')
                    drifted = prf.main(['--check-drift', '--revision', self.base, '--against', 'HEAD'])
                finally:
                    sys.stdout = stdout
        finally:
            os.chdir(cwd)
        self.assertEqual((clean, drifted), (0, 3))


# ---------------------------------------------------------------------------
# 1b. The real workflow step, executed against a throwaway origin and clone.
# ---------------------------------------------------------------------------
FAKE_VALIDATE = '''import os, sys
sys.exit(1 if os.environ.get("A30D31A0_FAIL_VALIDATE") else 0)
'''
TRIVIAL_TEST = '''import unittest
class Ok(unittest.TestCase):
    def test_ok(self):
        self.assertTrue(True)
'''


def stamp(hours_ago):
    return (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat().replace('+00:00', 'Z')


@unittest.skipUnless(HAS_GIT, 'git is required')
class RootFallbackStepExecution(unittest.TestCase):
    """Runs the committed step body; ``python -m scripts.validate`` is faked, the
    publisher and stager are the real modules."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.origin = base / 'origin.git'
        git(base, 'init', '-q', '--bare', '-b', 'main', str(self.origin))
        self.seed = base / 'seed'
        init_repo(self.seed)
        scripts = self.seed / 'scripts'
        scripts.mkdir()
        (scripts / '__init__.py').write_text('')
        shutil.copyfile(ROOT / 'scripts/publish_root_fallback.py', scripts / 'publish_root_fallback.py')
        shutil.copyfile(ROOT / 'scripts/stage_legacy.py', scripts / 'stage_legacy.py')
        (scripts / 'validate.py').write_text(FAKE_VALIDATE)
        (self.seed / 'tests').mkdir()
        (self.seed / 'tests/test_ok.py').write_text(TRIVIAL_TEST)
        (self.seed / 'site/assets').mkdir(parents=True)
        (self.seed / 'site/assets/style.css').write_text('/* old */\n')
        (self.seed / 'data').mkdir()
        (self.seed / 'data/book-receipts.json').write_text('{"receipts": []}\n')
        self.write_outputs(self.seed, css='/* old */\n', snapshot=stamp(1.0), tag='committed')
        self.build_revision = commit_all(self.seed, 'base build')
        git(self.seed, 'remote', 'add', 'origin', str(self.origin))
        git(self.seed, 'push', '-q', 'origin', 'main')
        # The runner: checked out at the build revision, built from it.
        self.runner = base / 'runner'
        git(base, 'clone', '-q', str(self.origin), str(self.runner))
        git(self.runner, 'config', 'user.name', 'runner')
        git(self.runner, 'config', 'user.email', 'runner@example.invalid')
        self.write_public(self.runner / 'public', css='/* old */\n', snapshot=stamp(0.5),
                          revision=self.build_revision)
        self.bin = base / 'bin'
        self.bin.mkdir()
        os.symlink(sys.executable, self.bin / 'python')
        self.script = base / 'step.sh'
        self.script.write_text(step_script())

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def write_outputs(repo, css, snapshot, tag):
        for relative in sorted(stage_legacy.ALLOWED):
            path = repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(css if relative == 'assets/style.css' else '%s %s\n' % (tag, relative))
        (repo / 'build-info.json').write_text(json.dumps({'snapshot_generated_at': snapshot}))
        (repo / '.nojekyll').write_text('')

    @staticmethod
    def write_public(public, css, snapshot, revision):
        manifest = {}
        for relative in sorted(stage_legacy.ALLOWED):
            path = public / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            body = (css if relative == 'assets/style.css' else 'built %s\n' % relative).encode()
            path.write_bytes(body)
            manifest[relative] = hashlib.sha256(body).hexdigest()
        (public / 'build-info.json').write_text(json.dumps({
            'schema_version': 1, 'revision': revision, 'built_at': snapshot,
            'snapshot_generated_at': snapshot, 'rows': 1, 'files': manifest}))
        (public / '.nojekyll').write_text('')

    def advance_main(self, files, message):
        git(self.seed, 'pull', '-q', 'origin', 'main')
        for relative, text in files.items():
            path = self.seed / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        sha = commit_all(self.seed, message)
        git(self.seed, 'push', '-q', 'origin', 'main')
        return sha

    def run_step(self, **extra_env):
        env = dict(os.environ, GITHUB_SHA=self.build_revision,
                   PATH=str(self.bin) + os.pathsep + os.environ.get('PATH', ''),
                   GIT_TERMINAL_PROMPT='0', **extra_env)
        return subprocess.run(['bash', '-e', str(self.script)], cwd=str(self.runner), env=env,
                              capture_output=True, text=True, timeout=120)

    def origin_file(self, relative):
        return git(self.origin, 'show', 'main:' + relative).stdout

    def origin_head(self):
        return git(self.origin, 'rev-parse', 'main').stdout.strip()

    def test_the_dce494b_replay_can_no_longer_roll_the_stylesheet_back(self):
        # Exactly the 2026-10-24 race: a newer main fixed both stylesheet copies
        # and regenerated the pages, so the first rebase conflicts and the step
        # falls through to its replay path with an older build.
        fixed = '/* old */\n}\n'
        newer = self.advance_main({'site/assets/style.css': fixed, 'assets/style.css': fixed,
                                   'index.html': 'regenerated by the newer merge\n'}, 'PR #245 analogue')
        result = self.run_step()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.origin_head(), newer, 'nothing may be pushed over the newer source')
        self.assertEqual(self.origin_file('assets/style.css'), fixed)
        self.assertIn('source_drift', result.stdout)

    def test_a_clean_rebase_over_newer_source_is_refused_at_push_time(self):
        # No textual conflict, so `git pull --rebase` succeeds: only the pre-push
        # hook stands between the older build and the newer source.
        newer = self.advance_main({'scripts/new_rule.py': 'RULE = 1\n'}, 'source-only change')
        result = self.run_step()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.origin_head(), newer)
        self.assertEqual(self.origin_file('index.html'), 'committed index.html\n')

    def test_research_and_board_commits_do_not_block_a_current_build(self):
        self.advance_main({'research/session-x/REPORT.md': 'receipt\n', 'COORDINATION.md': 'board\n'},
                          'receipts only')
        result = self.run_step()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.origin_file('index.html'), 'built index.html\n')
        self.assertIn('Publish the verified build to the legacy main:/ root fallback',
                      git(self.origin, 'log', '-1', '--format=%s', 'main').stdout)

    def test_a_staged_root_that_fails_its_own_gate_is_never_committed(self):
        before = self.origin_head()
        result = self.run_step(A30D31A0_FAIL_VALIDATE='1')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('failed its own validator or unit gate', result.stdout + result.stderr)
        self.assertEqual(self.origin_head(), before)


class WorkflowStepContract(unittest.TestCase):
    def setUp(self):
        self.step = step_script()

    def test_in_step_gates_are_fatal(self):
        self.assertIn('python -m scripts.validate --data data/latest.json --site . || return 3', self.step)
        self.assertIn('python -m unittest discover -s tests || return 3', self.step)
        self.assertEqual(self.step.count('[ "$rc" = "3" ] && {'), 2)

    def test_pre_push_hook_is_installed_before_the_first_push(self):
        hook = self.step.index('.git/hooks/pre-push')
        self.assertLess(hook, self.step.index('git push origin HEAD:main'))
        self.assertIn('--check-drift --revision %s --against "$rsha"', self.step)


if __name__ == '__main__':
    unittest.main()
