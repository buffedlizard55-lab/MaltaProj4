"""Offline pins for the final Hotspawn coverage audit (session 9b97d585).

No assertion pins a live team, market id, price, research sub-tier or row count.
The fresh runner capture supplies those facts; these tests pin only fail-closed
behaviour and the provenance of the generated review ledger.
"""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts import audit_9b97d585 as audit

ROOT = Path(__file__).resolve().parents[1]
BRANCH = "arena/9b97d585-maltaproj4"


def snapshot():
    return json.loads((ROOT / "data/latest.json").read_text())


def minimal(**changes):
    row = {
        "id": "synthetic",
        "teams": ["Alpha", "Beta"],
        "competition": "Synthetic audit fixture",
        "start": "2026-10-24T00:00:00Z",
        "lock": "2026-10-23T23:54:00Z",
        "state": "open",
        "source_url": "https://play.hotspawn.com/cs2-pickems",
        "feed_url": audit.FIXTURE_FEED,
        "pick": "Alpha",
        "probabilities": [0.6, 0.4],
        "fair_odds": [1 / 0.6, 2.5],
        "method": "exchange",
        "evidence": [{"api_url": "https://example.com/market", "url": "https://example.com/event"}],
        "attempts": [],
        "reason": None,
        "flags": [],
    }
    row.update(changes)
    return row


class RowInvariantTests(unittest.TestCase):
    def test_valid_synthetic_row_has_no_additional_problem(self):
        self.assertEqual(audit.common_row_problems(minimal()), [])

    def test_probability_change_is_not_accepted_as_verified(self):
        row = minimal(probabilities=[0.9, 0.1])
        problems = audit.common_row_problems(row)
        self.assertTrue(any("fair odds" in problem for problem in problems))

    def test_not_open_row_cannot_carry_a_pick(self):
        row = minimal(state="not_open")
        self.assertIn("not-open row carries an actionable value", audit.common_row_problems(row))

    def test_unresolved_row_needs_limitation_and_attempts(self):
        row = minimal(pick=None, probabilities=None, fair_odds=None, method=None, evidence=[])
        problems = audit.common_row_problems(row)
        self.assertIn("unresolved open row lacks a limitation", problems)
        self.assertIn("unresolved open row lacks source attempts", problems)

    def test_research_pick_must_not_gain_an_unsupported_percentage(self):
        row = minimal(probabilities=None, fair_odds=None, method="research_rank")
        self.assertEqual(audit.common_row_problems(row), [])
        row["probabilities"] = [0.5, 0.5]
        row["fair_odds"] = [2.0, 2.0]
        self.assertIn("priced row has an undocumented method", audit.common_row_problems(row))

    def test_non_hotspawn_fixture_source_is_rejected(self):
        row = minimal(source_url="https://example.com/not-hotspawn")
        self.assertIn("row lacks an official Hotspawn HTTPS fixture link", audit.common_row_problems(row))

    def test_method_sets_follow_the_canonical_summary_registry(self):
        from scripts.summary import ORIGINS
        for method, (kind, *_rest) in ORIGINS.items():
            if kind == 'research':
                self.assertIn(method, audit.RESEARCH_METHODS)
            elif kind in ('market', 'model'):
                self.assertIn(method, audit.MARKET_METHODS | audit.MODEL_METHODS)
        self.assertIn('bookmaker', audit.MARKET_METHODS)


class GeneratedLedgerTests(unittest.TestCase):
    def test_report_has_one_ledger_entry_per_snapshot_row(self):
        data = snapshot()
        result = audit.audit(data, data, json.dumps(data).encode())
        self.assertEqual(len(result["rows"]), len(data["matches"]))
        self.assertEqual(result["counts"]["fixtures"], len(data["matches"]))
        self.assertEqual(result["counts"]["open"], sum(row["state"] == "open" for row in result["rows"]))
        self.assertIsInstance(result["integrity_failures"], list)

    def test_report_copies_source_urls_instead_of_constructing_market_ids(self):
        data = snapshot()
        result = audit.audit(data, data)
        by_id = {str(row["id"]): row for row in data["matches"]}
        for row in result["rows"]:
            original = by_id[row["id"]]
            self.assertEqual(row["fixture_source"], original["source_url"])
            expected = []
            for evidence in original.get("evidence") or []:
                for key in ("api_url", "url"):
                    if evidence.get(key) and evidence[key] not in expected:
                        expected.append(evidence[key])
            self.assertEqual(row["evidence_sources"], expected)

    def test_writer_emits_snapshot_summary_and_every_row(self):
        data = snapshot()
        raw = json.dumps(data).encode()
        result = audit.audit(data, data, raw)
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            audit.write_reports(result, out, raw)
            self.assertEqual((out / "snapshot.json").read_bytes(), raw)
            saved = json.loads((out / "audit.json").read_text())
            self.assertEqual(len(saved["rows"]), len(data["matches"]))
            ledger = (out / "row-ledger.md").read_text()
            for row in data["matches"]:
                self.assertIn(f"| {row['id']} |", ledger)


class ExecutiveSummaryCopyTests(unittest.TestCase):
    """Count-aware prose must agree between the static build and runtime JS."""

    @staticmethod
    def counts(open_rows, without_percentage, no_pick=0):
        return {'open': open_rows, 'no_pick': no_pick,
                'with_pick': open_rows - no_pick,
                'without_percentage': without_percentage}

    def test_all_priced_never_says_zero_of_them_carry_no_probability(self):
        from scripts import summary
        text = summary.completeness_sentence(self.counts(2, 0))
        self.assertEqual(text, 'Every one of the 2 open matches has a pick, and every pick carries a win probability.')
        self.assertNotIn('0 of them', text)

    def test_one_research_row_uses_singular_grammar(self):
        from scripts import summary
        text = summary.completeness_sentence(self.counts(2, 1))
        self.assertIn('One of them carries no win probability', text)
        self.assertNotIn('1 of them carry', text)

    def test_single_open_match_has_natural_grammar(self):
        from scripts import summary
        self.assertEqual(summary.completeness_sentence(self.counts(1, 0)),
                         'The only open match has a pick, and every pick carries a win probability.')
        self.assertIn('It carries no win probability',
                      summary.completeness_sentence(self.counts(1, 1)))

    def test_short_phone_media_block_closes_before_later_phone_rules(self):
        for name in ('assets/style.css', 'site/assets/style.css'):
            text = (ROOT / name).read_text()
            self.assertIn('body[data-page=picks] .prob-pair span{white-space:nowrap}\n}\n\n/* Session f89bb1f8', text,
                          f'{name}: the short-screen media block must close before the later phone rules')


class WorkflowContractTests(unittest.TestCase):
    def test_capture_is_fixed_branch_non_publishing_and_fully_gated(self):
        text = (ROOT / ".github/workflows/harvest-9b97d585.yml").read_text()
        self.assertIn(f"branches: [{BRANCH}]", text)
        self.assertIn("scripts.refresh --output runtime/latest.json", text)
        self.assertIn("scripts.quarantine runtime/latest.json", text)
        self.assertIn("scripts.audit_9b97d585", text)
        self.assertIn("verification-c6/audit_snapshot.py", text)
        self.assertIn("npm run test:browser", text)
        self.assertIn("'publishes_pages': False", text)
        self.assertNotIn("actions/deploy-pages", text)
        self.assertNotIn("git push origin main", text)


if __name__ == "__main__":
    unittest.main()
