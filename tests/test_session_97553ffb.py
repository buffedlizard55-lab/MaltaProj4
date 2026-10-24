"""Release-recovery and fresh-harvest contracts for session 97553ffb."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / '.github' / 'workflows' / 'harvest-97553ffb.yml').read_text()
RECOVERY = (ROOT / 'tests' / 'test_session_0cc1138a.py').read_text()


class PublishRecoveryTests(unittest.TestCase):
    def test_current_parity_uses_current_raw_evidence_not_the_historical_open_set(self):
        start = RECOVERY.index('def test_snapshot_covers_the_current_official_fixture_evidence')
        end = RECOVERY.index('def test_each_current_open_fixture_', start)
        body = RECOVERY[start:end]
        self.assertIn("SNAPSHOT.get('fixture_evidence'", body)
        self.assertNotIn('OBSERVED_OPEN -', body)
        self.assertNotIn('removed_ids', body)

    def test_current_open_contract_does_not_index_a_missing_historical_row(self):
        start = RECOVERY.index('def test_each_current_open_fixture_')
        body = RECOVERY[start:]
        self.assertIn("for row in SNAPSHOT['matches']", body)
        self.assertNotIn('rows[fixture]', body)
        self.assertIn("row.get('attempts'", body)

    def test_harvest_is_branch_bound_and_cannot_deploy(self):
        self.assertIn('branches: [arena/97553ffb-maltaproj4]', WORKFLOW)
        self.assertNotIn('actions/deploy-pages', WORKFLOW)
        self.assertNotIn('pages: write', WORKFLOW)
        self.assertNotIn('git push origin main', WORKFLOW)
        self.assertIn('git push origin arena/97553ffb-maltaproj4', WORKFLOW)

    def test_harvest_replays_sources_and_every_release_gate(self):
        for command in (
            'python -m scripts.refresh --output runtime/latest.json',
            'python -m scripts.quarantine runtime/latest.json',
            'verification-c6/audit_snapshot.py public/data/latest.json',
            'python -m scripts.audit_9b97d585',
            'python -m scripts.coverage_contract',
            'python -m scripts.validate --data data/latest.json --site .',
            'npm run test:browser',
            'python -m unittest discover -s tests',
        ):
            self.assertIn(command, WORKFLOW)

    def test_harvest_requires_fresh_evidence_but_permits_a_flagged_official_union(self):
        self.assertIn("assert report['inventory_fresh']", WORKFLOW)
        self.assertIn("assert not report['problems']", WORKFLOW)
        self.assertNotIn('coverage-contract.json --require-fresh', WORKFLOW)

    def test_failed_harvest_can_commit_only_research_not_a_board(self):
        failure = WORKFLOW.split('name: Retain failed-candidate research without publishing its data', 1)[1]
        failure = failure.split('- name: Retain candidate and audit artifacts', 1)[0]
        self.assertIn('git add -- research/harvest-97553ffb', failure)
        self.assertNotIn('data/latest.json', failure)
        self.assertNotIn('index.html', failure)


class CurrentSnapshotShapeTests(unittest.TestCase):
    def test_committed_snapshot_has_exact_raw_fixture_id_parity(self):
        snapshot = json.loads((ROOT / 'data' / 'latest.json').read_text())
        published = {str(row['id']) for row in snapshot['matches']}
        raw = {str(row['id']) for row in snapshot['fixture_evidence']
               if row.get('sport_alias') == 'cs2'}
        self.assertEqual(published, raw)


if __name__ == '__main__':
    unittest.main()
