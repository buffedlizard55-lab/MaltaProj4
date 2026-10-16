"""The deploy job must check the repository out before running the live-bytes verifier.

Regression target: the runs for 40b13d3, 5053853, ca973c6 and 86321a8 on 2026-10-16 all
showed a red ``deploy`` job with ``Process completed with exit code 2`` and the warning
``No files were found with the provided path: runtime/live-verification.json`` — while the
live site was serving exactly the revision those runs built. The cause was not publication
and not the verifier's polling logic (covered by tests/test_verify_live_9a81b26f.py): the
``deploy`` job never checked the repository out, so ``python3 scripts/verify_live.py``
could not find the script and Python exited 2 before any receipt was written.

These assertions read the workflow text rather than a parsed document so they keep working
without a YAML dependency, and they fail if the checkout is removed, moved after the
verification step, or pinned to a SHA the repository has not recorded.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / '.github/workflows/pages.yml').read_text()


def deploy_job():
    match = re.search(r'^  deploy:\n(.*?)(?=^  \w|\Z)', WORKFLOW, re.S | re.M)
    assert match, 'no deploy job in .github/workflows/pages.yml'
    return match.group(1)


class DeployJobCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.job = deploy_job()

    def test_the_job_checks_out_the_repository_before_running_the_verifier(self):
        checkout = self.job.index('uses: actions/checkout@')
        verifier = self.job.index('python3 scripts/verify_live.py')
        self.assertLess(checkout, verifier,
                        'the verifier runs from the repository, so the checkout must come first')

    def test_the_checkout_pin_is_the_one_this_repository_records(self):
        pins = json.loads((ROOT / 'research/action-versions.json').read_text())
        self.assertIn('actions/checkout@%s' % pins['checkout']['sha'], self.job)
        self.assertNotIn('actions/checkout@main', self.job)
        self.assertNotIn('actions/checkout@v', self.job)

    def test_the_verifier_it_checks_out_actually_exists(self):
        runs = [line.strip()[len('run:'):].strip() for line in self.job.splitlines()
                if line.strip().startswith('run:')]
        scripts = [part for run in runs for part in run.split() if part.endswith('.py')]
        self.assertTrue(scripts, 'the deploy job runs no python script')
        for script in scripts:
            self.assertTrue((ROOT / script).is_file(),
                            '%s is run by CI but is not in the repository' % script)

    def test_the_receipt_is_still_uploaded_after_the_verifier(self):
        verifier = self.job.index('python3 scripts/verify_live.py')
        upload = self.job.index('runtime/live-verification.json')
        self.assertLess(verifier, upload, 'the receipt must be produced before it is uploaded')
        self.assertIn('if: always()', self.job[upload - 400:upload + 200])

    def test_a_failed_deployment_still_does_not_hide_a_successful_publication(self):
        # Both deploy attempts stay continue-on-error: the live-bytes check is what
        # decides the run, exactly as the job comment documents.
        self.assertEqual(2, self.job.count('continue-on-error: true'))
        self.assertIn('steps.deployment.outcome', self.job)


if __name__ == '__main__':
    unittest.main()
