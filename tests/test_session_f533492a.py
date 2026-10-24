"""Session f533492a: test the refreshed candidate, never the expired board.

The scheduled publisher used to run the complete data-dependent unit suite
before its first source refresh.  Those tests read ``data/latest.json`` and the
committed root HTML, so a legitimate inventory change could permanently prevent
the refresh that would satisfy them.  Moving only the test step would not fix
that input mismatch: ``scripts.refresh`` writes ``runtime/latest.json``.

The publication sequence now refreshes and quarantines first, independently
audits/builds/validates the candidate, stages those hash-verified bytes into the
runner workspace, and only then runs every unit, independent-audit, root-link
and browser gate.  Staging is not publication.  The root commit/push, Pages
artifact upload and deployment all remain downstream of the complete gates.
Pull requests skip the network refresh as before and test the rebuilt committed
candidate through the same path.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")


def step(name):
    marker = "      - name: " + name + "\n"
    start = WORKFLOW.index(marker)
    end = WORKFLOW.find("\n      - ", start + len(marker))
    return WORKFLOW[start:end if end >= 0 else None]


class CandidateGateOrdering(unittest.TestCase):
    def test_refresh_precedes_the_data_dependent_unit_gate(self):
        refresh = WORKFLOW.index("      - name: Refresh official sources (trusted branches only)\n")
        unit = WORKFLOW.index("      - name: Unit and independent failure-mode tests\n")
        self.assertLess(refresh, unit)
        self.assertNotIn("python -m unittest discover -s tests", WORKFLOW[:refresh])

    def test_unit_gate_reads_staged_candidate_not_stale_runtime_baseline(self):
        build = WORKFLOW.index("      - name: Build and independently verify every row, calculation and internal link\n")
        stage = WORKFLOW.index("      - name: Stage the verified candidate for data-dependent regression tests\n")
        unit = WORKFLOW.index("      - name: Unit and independent failure-mode tests\n")
        browser = WORKFLOW.index("      - name: Phone, tablet, desktop, accessibility and exact-boundary expiry checks\n")
        self.assertLess(build, stage)
        self.assertLess(stage, unit)
        self.assertLess(unit, browser)
        staged = step("Stage the verified candidate for data-dependent regression tests")
        self.assertIn("python -m scripts.stage_legacy", staged)
        self.assertNotIn("publish_root_fallback", staged)
        self.assertNotIn("git commit", staged)
        self.assertNotIn("git push", staged)
        self.assertNotIn("continue-on-error", staged)

    def test_candidate_is_quarantined_audited_built_and_validated_before_staging(self):
        names = [
            "Refresh official sources (trusted branches only)",
            "Withhold any row the independent audit cannot reproduce",
            "Build and independently verify every row, calculation and internal link",
            "Stage the verified candidate for data-dependent regression tests",
        ]
        positions = [WORKFLOW.index("      - name: " + name + "\n") for name in names]
        self.assertEqual(positions, sorted(positions))
        build = step(names[2])
        self.assertLess(build.index("audit_snapshot.py runtime/latest.json"),
                        build.index("python -m scripts.build --data runtime/latest.json"))
        self.assertIn("python -m scripts.validate --data runtime/latest.json", build)
        self.assertIn("audit_snapshot.py public/data/latest.json", build)

    def test_no_original_test_or_independent_validator_was_removed(self):
        gate = step("Unit and independent failure-mode tests")
        for command in (
            "python -m unittest discover -s tests -v",
            "python -m unittest discover -s audits -p 'test_*.py' -v",
            "python verification-95b588c2/test_integrity.py",
            "python -m unittest discover -s verification-c6 -p 'test_*.py' -v",
            "python -m scripts.validate --data data/latest.json --site .",
        ):
            self.assertIn(command, gate)
        self.assertNotIn("continue-on-error", gate)

    def test_every_publication_effect_remains_downstream_of_all_gates(self):
        unit = WORKFLOW.index("      - name: Unit and independent failure-mode tests\n")
        browser = WORKFLOW.index("      - name: Phone, tablet, desktop, accessibility and exact-boundary expiry checks\n")
        root = WORKFLOW.index("      - name: Keep the legacy main:/ root fallback on the verified build\n")
        artifact = WORKFLOW.index("      - uses: actions/upload-pages-artifact@")
        self.assertLess(unit, browser)
        self.assertLess(browser, root)
        self.assertLess(root, artifact)
        self.assertIn("run: npm run test:browser",
                      step("Phone, tablet, desktop, accessibility and exact-boundary expiry checks"))
        self.assertIn("needs: verify-build", WORKFLOW[artifact:])

    def test_pull_requests_still_rebuild_and_test_without_network_refresh(self):
        refresh = step("Refresh official sources (trusted branches only)")
        self.assertIn("github.event_name != 'pull_request'", refresh)
        for name in (
            "Build and independently verify every row, calculation and internal link",
            "Stage the verified candidate for data-dependent regression tests",
            "Unit and independent failure-mode tests",
            "Phone, tablet, desktop, accessibility and exact-boundary expiry checks",
        ):
            block = step(name)
            self.assertIn("steps.gate.outputs.publish == 'true'", block)
            self.assertNotIn("github.event_name != 'pull_request'", block)


if __name__ == "__main__":
    unittest.main()
