"""Regression guards for ece64b74's publication diagnostics.

The successful-upload deployment gate was adopted from PR #311. This session's
remaining change keeps complete build-gate logs in the run artifacts/summary and
emits the tail of a failure as one check annotation, so GitHub's annotation cap
cannot hide the terminal assertion.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/pages.yml").read_text()


def job(name: str) -> str:
    match = re.search(r"^  %s:\n(.*?)(?=^  \w|\Z)" % re.escape(name), WORKFLOW, re.S | re.M)
    if not match:
        raise AssertionError("no %s job in .github/workflows/pages.yml" % name)
    return match.group(1)


def step(text: str, header: str) -> str:
    start = text.index(header)
    end = text.find("\n      - ", start + len(header))
    return text[start:] if end == -1 else text[start:end]


class BuildFailureDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.verify = job("verify-build")

    def test_fixed_session_branch_runs_verification_without_qualifying_for_upload(self):
        push = WORKFLOW.split("  pull_request:", 1)[0]
        self.assertIn("arena/ece64b74-maltaproj4", push)
        upload = step(self.verify, "- uses: actions/upload-pages-artifact@")
        self.assertIn("github.ref == 'refs/heads/main'", upload)

    def test_each_build_gate_retains_its_own_log_and_summary(self):
        build = step(self.verify, "- name: Build and independently verify every row")
        for expected in (
            "runtime/row-audit.log",
            "runtime/build.log",
            "runtime/validate.log",
            "runtime/published-row-audit.log",
            "tail -n 80 \"$logfile\"",
            "GITHUB_STEP_SUMMARY",
            'cat "$logfile"',
            'return "$rc"',
        ):
            self.assertIn(expected, build)

    def test_failure_tail_is_one_annotation_so_terminal_assertion_is_visible(self):
        build = step(self.verify, "- name: Build and independently verify every row")
        self.assertIn("splitlines()[-20:]", build)
        self.assertIn("detail = ' | '.join(lines)", build)
        self.assertIn("GitHub truncates check annotations at ten", build)
        self.assertIn("::error title={label}::{detail[:6000]}", build)
        self.assertNotIn("for line in lines:", build)

    def test_receipt_is_recorded_only_after_pages_artifact_upload_succeeds(self):
        receipt = step(self.verify, "- name: Record the exact artifact expected at the public site")
        self.assertIn("steps.pages_artifact.outcome == 'success'", receipt)
        self.assertIn("manifest_sha", receipt)


if __name__ == "__main__":
    unittest.main()
