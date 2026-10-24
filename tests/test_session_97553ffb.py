"""Release-recovery and fresh-harvest contracts for session 97553ffb."""
from pathlib import Path
import copy
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
        self.assertIn('cancel-in-progress: true', WORKFLOW)
        self.assertNotIn('actions/deploy-pages', WORKFLOW)
        self.assertNotIn('pages: write', WORKFLOW)
        self.assertNotIn('git push origin main', WORKFLOW)
        self.assertIn('git push origin arena/97553ffb-maltaproj4', WORKFLOW)

    def test_harvest_replays_sources_and_every_release_gate(self):
        for block in WORKFLOW.split('- name:')[1:]:
            if 'tee ' in block:
                self.assertIn('set -o pipefail', block,
                              'a logged test/source pipeline must not mask its exit status')
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


class ExecutiveSummaryIntegrationTests(unittest.TestCase):
    """Browser-reviewed UI integration from d2a55add / 55430b8."""

    @classmethod
    def setUpClass(cls):
        from bs4 import BeautifulSoup
        from scripts.build import overview
        snapshot = json.loads((ROOT / 'data' / 'latest.json').read_text())
        cls.html = overview(copy.deepcopy(snapshot))
        cls.soup = BeautifulSoup(cls.html, 'html.parser')

    def test_summary_is_visible_and_directly_routes_to_current_picks_and_limits(self):
        bars = self.soup.select('#exec-summary')
        self.assertEqual(len(bars), 1)
        self.assertIsNone(bars[0].find_parent('details'))
        self.assertLess(self.html.index('id="freshness-strip"'), self.html.index('id="exec-summary"'))
        self.assertLess(self.html.index('id="exec-summary"'), self.html.index('id="picks-at-a-glance"'))
        hrefs = {a.get('href') for a in bars[0].select('a[href]')}
        self.assertTrue({'picks.html', '#picks-at-a-glance', 'unresolved.html',
                         '#unresolved-summary', 'matches.html', 'review.html'} <= hrefs)

    def test_phone_summary_css_is_deterministic_and_accessibly_sized(self):
        root_css = (ROOT / 'assets' / 'style.css').read_bytes()
        self.assertEqual(root_css, (ROOT / 'site' / 'assets' / 'style.css').read_bytes())
        text = root_css.decode()
        self.assertIn('body[data-page="index"] main>#exec-summary{order:3}', text)
        self.assertIn('.exec-bar-links a{min-height:44px', text)
        # A missing brace here used to nest every later tall-phone index rule
        # inside the short-phone picks media query. Browser placement is the
        # end-to-end guard; this pins the exact repaired boundary as well.
        self.assertIn('body[data-page=picks] .prob-pair span{white-space:nowrap}\n}\n/* Session f89bb1f8', text)


class CurrentSnapshotShapeTests(unittest.TestCase):
    def test_independent_verifier_replays_hltv_mirror_valve_points(self):
        from tests.test_session_0cc1138a import V
        evidence = {
            'provider': 'HLTV Valve ranking (Valve points)',
            'points': [1030, 819], 'rating_deviation': 75.0,
            'calibration_slope': 0.7986,
            'raw_expected': [V.glicko_expect(1030, 819), V.glicko_expect(819, 1030)],
        }
        probabilities, kind = V.evidence_probabilities(evidence, ['Spirit Academy', 'LFO 10'])
        self.assertEqual(kind, 'hltv_valve_vrs_mirror')
        self.assertAlmostEqual(sum(probabilities), 1.0, places=12)
        self.assertGreater(probabilities[0], probabilities[1])

    def test_flagged_current_official_union_is_complete_and_disclosed(self):
        from scripts import audit_f89bb1f8
        snapshot = json.loads((ROOT / 'data' / 'latest.json').read_text())
        union = copy.deepcopy(snapshot)
        union['coverage'] = 'partial'
        union['coverage_counts']['lobby'] -= 1
        union['matches'][0]['fixture_sources'] = [
            r for r in union['matches'][0]['fixture_sources']
            if r.get('url') != audit_f89bb1f8.LOBBY
        ]
        union.setdefault('issues', []).append({
            'code': 'coverage_difference', 'message': 'Official lobby ID sets differ; union retained.',
            'source': audit_f89bb1f8.LOBBY,
        })
        self.assertEqual(audit_f89bb1f8.inventory_problems(union), [])
        union['issues'] = [i for i in union['issues'] if i.get('code') != 'coverage_difference']
        self.assertTrue(any('disclosure' in p for p in audit_f89bb1f8.inventory_problems(union)))

    def test_coverage_auditor_accepts_the_production_recent_form_research_rung(self):
        # Fix reviewed and integrated from 019a253a / 50c8bfea. This must stay
        # green when a fresh fixture needs the final sourced-form fallback.
        from scripts import audit_f89bb1f8, build, summary
        audited = audit_f89bb1f8.PRICED | audit_f89bb1f8.RESEARCH
        self.assertIn('research_form', audit_f89bb1f8.RESEARCH)
        self.assertLessEqual(set(build.METHOD_LABELS), audited)
        self.assertLessEqual(audited, set(summary.ORIGINS))
        self.assertFalse(audit_f89bb1f8.PRICED & audit_f89bb1f8.RESEARCH)

    def test_non_featured_rows_record_hltv_first_then_betting_lines(self):
        snapshot = json.loads((ROOT / 'data' / 'latest.json').read_text())
        gaps = [m for m in snapshot['matches'] if m.get('state') == 'open'
                and m.get('method') != 'exchange']
        self.assertTrue(gaps, 'this candidate must exercise the fallback ledger')
        for match in gaps:
            providers = [a.get('provider') for a in match.get('attempts') or []]
            self.assertIn('HLTV', providers, match['id'])
            self.assertIn('Pinnacle', providers, match['id'])
            self.assertLess(providers.index('HLTV'), providers.index('Pinnacle'), match['id'])
            if match.get('method') not in {'bookmaker', 'exchange_wide'}:
                self.assertTrue(any(p and any(label in p for label in (
                    'Thunderpick', 'GG.BET', 'Book research', 'Book listing')) for p in providers),
                    match['id'])

    def test_committed_snapshot_has_exact_raw_fixture_id_parity(self):
        snapshot = json.loads((ROOT / 'data' / 'latest.json').read_text())
        published = {str(row['id']) for row in snapshot['matches']}
        raw = {str(row['id']) for row in snapshot['fixture_evidence']
               if row.get('sport_alias') == 'cs2'}
        self.assertEqual(published, raw)


if __name__ == '__main__':
    unittest.main()
