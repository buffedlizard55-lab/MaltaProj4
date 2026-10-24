"""Session d15e84e5: a verified build must reach Pages even when the legacy root fallback fails.

Regression being pinned (2026-10-24): on ``main`` the runs at 09:38Z, 10:05Z and 16:06Z all
passed steps 8-14, then died in step 15 (``Keep the legacy main:/ root fallback on the
verified build``). Because ``actions/upload-pages-artifact`` used to run *after* that step,
the artifact never existed, GitHub skipped ``deploy``, and the public board froze at the
08:06Z snapshot until every pick was withheld. The step-15 push itself is the flaky part:
it rebases onto ``origin/main`` and pushes a commit, which competed with other sessions'
pushes and with Pages' own ``main:/`` republish.

The fix, pinned here, keeps the fault visible *and* unblocks publication:

* the verified artifact is uploaded **before** step 15 runs;
* step 15 keeps its fatal ``|| return 3`` gates (a staged root that cannot validate or
  pass unit tests is still an error) but an exhausted push retry exits 0 with a warning,
  because a push conflict says nothing about the board that was just verified;
* the artifact receipt is recorded under ``if: always()`` so a red step 15 still yields a
  manifest for the deploy job;
* ``deploy`` is ``always()``-guarded but still requires ``publish == 'true'``, ``main`` and
  a non-PR event, so nothing is published that the gate withheld.

The assertions read the workflow text (like ``test_deploy_job_checkout_621776e4``) so they
run without a YAML dependency.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/pages.yml").read_text()
UPLOAD = "actions/upload-pages-artifact@"
FALLBACK = "- name: Keep the legacy main:/ root fallback on the verified build"
RECEIPT = "- name: Record the exact artifact expected at the public site"


def job(name: str) -> str:
    match = re.search(r"^  %s:\n(.*?)(?=^  \w|\Z)" % re.escape(name), WORKFLOW, re.S | re.M)
    assert match, "no %s job in .github/workflows/pages.yml" % name
    return match.group(1)


def step(text: str, header: str) -> str:
    start = text.index(header)
    end = text.find("\n      - ", start + len(header))
    return text[start:] if end == -1 else text[start:end]


class VerifiedBuildStillDeploysTests(unittest.TestCase):
    def setUp(self):
        self.verify = job("verify-build")
        self.deploy = job("deploy")

    def test_the_artifact_is_uploaded_before_the_legacy_root_fallback_runs(self):
        upload = self.verify.index(UPLOAD)
        fallback = self.verify.index(FALLBACK)
        self.assertLess(
            upload,
            fallback,
            "upload-pages-artifact must run before step 15: a failing main:/ push then "
            "cannot cost the verified build its deploy (the 2026-10-24 freeze)",
        )

    def test_the_upload_only_publishes_a_verified_main_board(self):
        block = step(self.verify, UPLOAD)
        self.assertIn("path: public", block)
        self.assertIn("github.ref == 'refs/heads/main'", block)
        self.assertIn("github.event_name != 'pull_request'", block)
        self.assertIn("steps.gate.outputs.publish == 'true'", block)

    def test_the_root_fallback_keeps_its_fatal_gates(self):
        block = step(self.verify, FALLBACK)
        self.assertIn("python -m scripts.validate --data data/latest.json --site . || return 3", block)
        # Session aeafcbe6 kept the gate fatal and made it legible: the suite is teed to a
        # log, a non-zero exit still returns 3, and the failing test names now reach
        # the run summary. Assert the gate, not one spelling of it.
        self.assertIn("python -m unittest discover -s tests 2>&1 | tee runtime/staged-root-unit.log", block)
        self.assertIn("return 3", block)
        self.assertNotIn("continue-on-error", block)
        self.assertNotIn("|| true\n          done", block)

    def test_an_exhausted_push_retry_warns_instead_of_blocking_publication(self):
        block = step(self.verify, FALLBACK)
        self.assertIn("::warning::", block)
        tail = block.rstrip().splitlines()[-1].strip()
        self.assertEqual(
            tail,
            "exit 0",
            "the exhausted main:/ push must bail out successfully so the run's verified "
            "artifact still deploys; the red step is reported through the warning",
        )

    def test_the_receipt_survives_a_red_fallback_step(self):
        self.assertIn(RECEIPT, self.verify)
        block = step(self.verify, RECEIPT)
        self.assertIn("if: always()", block)
        self.assertIn("steps.gate.outputs.publish == 'true'", block)
        self.assertIn("manifest_sha", block)
        self.assertLess(self.verify.index(FALLBACK), self.verify.index(RECEIPT))

    def test_deploy_is_always_guarded_and_never_publishes_a_withheld_board(self):
        guard = re.search(r"^    if: (.+)$", self.deploy, re.M)
        self.assertIsNotNone(guard, "the deploy job lost its guard")
        condition = guard.group(1)
        self.assertTrue(condition.startswith("always() &&"), condition)
        self.assertIn("github.ref == 'refs/heads/main'", condition)
        self.assertIn("github.event_name != 'pull_request'", condition)
        self.assertIn("needs.verify-build.outputs.publish == 'true'", condition)

    def test_the_deploy_job_consumes_the_artifact_the_verify_job_uploaded(self):
        self.assertIn("actions/deploy-pages@", self.deploy)
        self.assertIn("needs: verify-build", self.deploy)


if __name__ == "__main__":
    unittest.main()
