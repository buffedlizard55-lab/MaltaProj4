"""Session bf1b12c7 (2026-10-24): a root-fallback test failure may not strand a verified build.

Measured on the Actions API: main's publish runs 40080448344, 40082763751,
40084520702 and the scheduled 40097410704 all failed at "Keep the legacy main:/
root fallback on the verified build". Because the Pages artifact was uploaded
only after that step, ``deploy`` was skipped every time, so the public board
kept the 2026-10-24T08:06:51Z snapshot until its 8-hour window closed and every
pick was withheld -- while refresh, quarantine, build, validator, the
independent row audit and every browser gate had passed on the fresh build.

These tests pin the repaired order without pinning any fixture, team or date.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = (ROOT / '.github' / 'workflows' / 'pages.yml').read_text(encoding='utf-8')
HARVEST = (ROOT / '.github' / 'workflows' / 'harvest-bf1b12c7.yml').read_text(encoding='utf-8')


def job(name):
    match = re.search(r'^  %s:\n(.*?)(?=^  [\w-]+:\n|\Z)' % re.escape(name), PAGES, re.S | re.M)
    assert match, name
    return match.group(1)


class VerifiedArtifactIsDeployedIndependentlyOfTheRootCommit(unittest.TestCase):
    def setUp(self):
        self.build = job('verify-build')
        self.deploy = job('deploy')

    def test_artifact_is_uploaded_after_every_gate_and_before_the_root_step(self):
        browser = self.build.index('npm run test:browser')
        validate = self.build.index('python -m scripts.validate --data runtime/latest.json')
        upload = self.build.index('actions/upload-pages-artifact@')
        root = self.build.index('- name: Keep the legacy main:/ root fallback on the verified build')
        self.assertLess(validate, upload)
        self.assertLess(browser, upload)
        self.assertLess(upload, root)
        self.assertEqual(self.build.count('actions/upload-pages-artifact@'), 1)

    def test_upload_is_still_main_only_and_never_on_pull_requests(self):
        upload = self.build.index('actions/upload-pages-artifact@')
        block = self.build[upload:upload + 400]
        self.assertIn("github.ref == 'refs/heads/main'", block)
        self.assertIn("github.event_name != 'pull_request'", block)

    def test_ready_flag_depends_on_a_successful_upload(self):
        self.assertIn("artifact_ready: ${{ steps.artifact_ready.outputs.ready }}", PAGES)
        self.assertIn("if: steps.pages_artifact.outcome == 'success'", self.build)

    def test_fingerprint_comes_from_the_uploaded_build(self):
        self.assertIn('manifest_sha: ${{ steps.artifact.outputs.manifest_sha }}', PAGES)
        step = self.build.split('- name: Fingerprint the verified Pages artifact before the root fallback', 1)[1]
        step = step.split('- uses: actions/upload-pages-artifact@', 1)[0]
        self.assertIn('sha256sum public/build-info.json', step)

    def test_deploy_runs_after_a_failed_root_step_only_with_a_ready_artifact(self):
        condition = re.search(r'^    if: (.*)$', self.deploy, re.M).group(1)
        self.assertTrue(condition.startswith('always() &&'), condition)
        for clause in ("github.ref == 'refs/heads/main'", "github.event_name != 'pull_request'",
                       "needs.verify-build.outputs.publish == 'true'",
                       "needs.verify-build.outputs.artifact_ready == 'true'"):
            self.assertIn(clause, condition)

    def test_root_failure_still_turns_the_run_red_after_live_verification(self):
        verify = self.deploy.index('python3 scripts/verify_live.py')
        red = self.deploy.index('- name: Keep the run red when the root fallback gate failed')
        self.assertLess(verify, red)
        tail = self.deploy[red:]
        self.assertIn("if: always() && needs.verify-build.result != 'success'", tail)
        self.assertIn('exit 1', tail)

    def test_root_step_gates_are_unchanged(self):
        root = self.build.split('- name: Keep the legacy main:/ root fallback on the verified build', 1)[1]
        root = root.split('- name: Record the exact artifact expected at the public site', 1)[0]
        self.assertIn('python -m unittest discover -s tests || return 3', root)
        self.assertIn('python -m scripts.validate --data data/latest.json --site . || return 3', root)


class HarvestRehearsalIsFaithfulAndNonPublishing(unittest.TestCase):
    def test_rehearsal_uses_the_publishers_own_promotion_and_gates(self):
        self.assertIn('python -m scripts.publish_root_fallback --public public --root . --cooldown-hours 0.2', HARVEST)
        self.assertIn('python -m scripts.validate --data data/latest.json --site .', HARVEST)
        self.assertIn('python -m unittest discover -s tests -v', HARVEST)

    def test_harvest_never_deploys_or_touches_main(self):
        for forbidden in ('upload-pages-artifact', 'deploy-pages', 'HEAD:main', 'origin main'):
            self.assertNotIn(forbidden, HARVEST, forbidden)
        self.assertIn('branches: [arena/bf1b12c7-maltaproj4]', HARVEST)
        self.assertIn('git add -A -- research/harvest-bf1b12c7', HARVEST)


if __name__ == '__main__':
    unittest.main()
