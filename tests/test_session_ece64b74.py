"""Regression guards for the ece64b74 final-integration repair.

On 2026-10-25 the main publication workflow had a `publish=true` freshness-gate
output even though its fresh-build verifier failed. Because the deploy job was
`always()`-guarded only by that freshness output, it still ran without the
current run's verified Pages artifact and failed the exact-live-byte check.
The artifact marker below is set only after upload-pages-artifact succeeds,
which preserves the intentional fallback-failure deploy path while closing the
build-failure path.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github/workflows/pages.yml"
WORKFLOW = WORKFLOW_PATH.read_text()
PHONE_TEST = (ROOT / "tests/browser_aeafcbe6.cjs").read_text()
UPLOAD = "actions/upload-pages-artifact@"
FALLBACK = "- name: Keep the legacy main:/ root fallback on the verified build"
MARKER = "- name: Record verified Pages artifact availability"
RECEIPT = "- name: Record the exact artifact expected at the public site"


def job(name: str) -> str:
    match = re.search(r"^  %s:\n(.*?)(?=^  \w|\Z)" % re.escape(name), WORKFLOW, re.S | re.M)
    if not match:
        raise AssertionError("no %s job in .github/workflows/pages.yml" % name)
    return match.group(1)


def step(text: str, header: str) -> str:
    start = text.index(header)
    end = text.find("\n      - ", start + len(header))
    return text[start:] if end == -1 else text[start:end]


class VerifiedArtifactDeployTests(unittest.TestCase):
    def setUp(self):
        self.verify = job("verify-build")
        self.deploy = job("deploy")

    def test_fixed_session_branch_runs_the_same_nonpublishing_verification(self):
        self.assertIn("arena/ece64b74-maltaproj4", WORKFLOW.split("  pull_request:", 1)[0])

    def test_only_a_successful_pages_upload_sets_the_job_output(self):
        self.assertIn("artifact_ready: ${{ steps.artifact_ready.outputs.ready }}", self.verify)
        upload = step(self.verify, UPLOAD)
        self.assertIn("id: pages_upload", upload)
        marker = step(self.verify, MARKER)
        self.assertIn("id: artifact_ready", marker)
        self.assertIn("steps.pages_upload.outcome == 'success'", marker)
        self.assertIn('echo "ready=true" >> "$GITHUB_OUTPUT"', marker)
        self.assertLess(self.verify.index(UPLOAD), self.verify.index(MARKER))
        self.assertLess(self.verify.index(MARKER), self.verify.index(FALLBACK))

    def test_later_root_fallback_failure_can_still_deploy_the_verified_artifact(self):
        # The marker is recorded before the root fallback. `always()` deliberately
        # allows the downstream deploy job to run if only that fallback step fails.
        self.assertLess(self.verify.index(MARKER), self.verify.index(FALLBACK))
        condition = re.search(r"^    if: (.+)$", self.deploy, re.M)
        self.assertIsNotNone(condition)
        self.assertIn("always()", condition.group(1))
        self.assertIn("needs.verify-build.outputs.artifact_ready == 'true'", condition.group(1))

    def test_build_failure_or_skipped_upload_cannot_reach_deploy(self):
        condition = re.search(r"^    if: (.+)$", self.deploy, re.M)
        self.assertIsNotNone(condition)
        condition = condition.group(1)
        self.assertIn("needs.verify-build.outputs.publish == 'true'", condition)
        self.assertIn("needs.verify-build.outputs.artifact_ready == 'true'", condition)
        self.assertIn("github.ref == 'refs/heads/main'", condition)
        self.assertIn("github.event_name != 'pull_request'", condition)

    def test_manifest_receipt_is_not_created_without_a_verified_artifact(self):
        receipt = step(self.verify, RECEIPT)
        self.assertIn("if: always()", receipt)
        self.assertIn("steps.artifact_ready.outputs.ready == 'true'", receipt)
        self.assertIn("manifest_sha", receipt)

    def test_failing_build_gate_retains_logs_and_emits_check_annotations(self):
        build = step(self.verify, "- name: Build and independently verify every row")
        for expected in ("run_gate()", "GITHUB_STEP_SUMMARY", "::error title=", "runtime/row-audit.log",
                         "runtime/build.log", "runtime/validate.log", "runtime/published-row-audit.log",
                         "detail = ' | '.join(lines)", "truncates check annotations at ten"):
            self.assertIn(expected, build)


class StalePhoneBoardTests(unittest.TestCase):
    def test_mobile_gate_accepts_intentional_stale_withholding_without_showing_old_prices(self):
        self.assertIn("const snapshotStale", PHONE_TEST)
        self.assertIn("home.withheld !== snapshotStale", PHONE_TEST)
        self.assertIn("stale board still exposes", PHONE_TEST)
        self.assertIn("current_priced_rows", PHONE_TEST)
        self.assertNotIn("research/session-aeafcbe6/mobile-measurements.json", PHONE_TEST)


if __name__ == "__main__":
    unittest.main()
