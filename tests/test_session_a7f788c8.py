"""Deployment can survive staging failure, never a missing verified artifact."""
import unittest
from pathlib import Path


class ArtifactEligibility(unittest.TestCase):
    def test_upload_success_is_exported_not_freshness_intention(self):
        workflow = Path('.github/workflows/pages.yml').read_text()
        self.assertIn('artifact_ready: ${{ steps.pages_artifact.outcome }}', workflow)
        upload = workflow.split('- uses: actions/upload-pages-artifact@', 1)[1].split('      - ', 1)[0]
        self.assertIn('id: pages_artifact', upload)
        self.assertNotIn('always()', upload)
        self.assertNotIn('continue-on-error', upload)

    def test_deploy_requires_upload_but_can_survive_later_failure(self):
        workflow = Path('.github/workflows/pages.yml').read_text()
        condition = workflow.split('  deploy:\n', 1)[1].split('    if: ', 1)[1].splitlines()[0]
        for guard in ('always()', "github.ref == 'refs/heads/main'",
                      "github.event_name != 'pull_request'",
                      "needs.verify-build.outputs.publish == 'true'",
                      "needs.verify-build.outputs.artifact_ready == 'success'"):
            self.assertIn(guard, condition)
        self.assertNotIn('needs.verify-build.result', condition)


if __name__ == '__main__':
    unittest.main()
