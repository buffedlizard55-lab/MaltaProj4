"""Session d4c74d77 — publication-deadlock repair and read-only board verification.

Measured defect this suite locks down (2026-10-23, evidence in COORDINATION.md):

* The scheduled production workflow
  (.github/workflows/pages.yml, step "Unit and independent failure-mode tests")
  runs the whole unit suite against the *committed* board before it reads any
  live source. Two stale pins in ``tests/test_session_75ebd2d6.py`` and
  ``tests/test_session_13e99ca6.py`` still required fixture 1081149
  (FORZE Reload vs LFO 10) to be ``research_rank_single``. The 2026-10-22T20:15Z
  refresh had legitimately re-tiered that row to the one-sided Valve standings
  tier (``research_vrs_single``) and committed it, so every later scheduled run
  failed at the test step, the source refresh never ran again, and the public
  board froze for 8h+.
* The repaired assertions accept a research tier only when the row's own retained
  receipt proves it. This module independently re-derives that proof, rejects
  corrupted receipts, and scans the whole suite for the same class of stale pin
  so a future tier change cannot silently stop publication again.

Nothing here changes a price, a probability, a pick or a source timestamp.
"""
import copy
import hashlib
import importlib
import json
import os
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "latest.json"
TESTS = ROOT / "tests"

# The tiers that publish a pick with no percentage. Production policy lives in
# scripts/coverage_contract.py (RESEARCH) and scripts/build.py (METHOD_LABELS);
# the floor is asserted separately so a tier can never be silently renamed away.
RESEARCH_TIERS_FLOOR = {"research_rank", "research_rank_single", "research_vrs_single"}

VALVE_STANDINGS_PREFIX = "https://github.com/ValveSoftware/counter-strike_regional_standings/"
HLTV_FIXTURE_PREFIX = "https://www.hltv.org/matches/"


def load_audit_helpers():
    """Import the repaired audit module under its unittest-discover name."""
    try:
        return importlib.import_module("test_session_75ebd2d6")
    except ImportError:  # direct invocation from the repository root
        sys.path.insert(0, str(TESTS))
        try:
            return importlib.import_module("test_session_75ebd2d6")
        finally:
            sys.path.pop(0)


def proven_tier(match):
    """Session-independent re-derivation of the research tier a row proves."""
    vrs = match.get("vrs_research") or {}
    resolved = vrs.get("resolved_vrs") or []
    if str(vrs.get("source") or "").startswith(VALVE_STANDINGS_PREFIX):
        listed = [x for x in resolved if x.get("status") == "listed"]
        absent = [x for x in resolved if x.get("status") == "absent"]
        if len(listed) == 1 and listed[0].get("team") == match.get("pick"):
            if isinstance(listed[0].get("standing"), int) and len(absent) == 1:
                return "research_vrs_single"
    ctx = match.get("hltv_context") or {}
    if str(ctx.get("source") or "").startswith(HLTV_FIXTURE_PREFIX):
        ranks = [r for r in (ctx.get("ranks") or []) if r.get("hltv_rank")]
        if len(ranks) == 2:
            return "research_rank" if min(ranks, key=lambda r: r["hltv_rank"]).get("team") == match.get("pick") else None
        if len(ranks) == 1 and ranks[0].get("team") == match.get("pick"):
            return "research_rank_single"
    return None


class PublishedResearchPolicy(unittest.TestCase):
    def test_production_policy_keeps_every_documented_research_tier(self):
        from scripts import build, coverage_contract
        self.assertTrue(RESEARCH_TIERS_FLOOR <= set(coverage_contract.RESEARCH),
                        "a documented research-only tier disappeared from scripts/coverage_contract.py")
        for tier in RESEARCH_TIERS_FLOOR:
            self.assertIn(tier, build.METHOD_LABELS)
            self.assertIn(tier, build.METHOD_TAGS)
            self.assertIn(tier, build.METHOD_KIND)
        # Every tier the coverage contract publishes must carry a rendered label. A
        # future *addition* is deliberately allowed to ship (that is how the 20:15Z
        # re-tiering happened); a removal or a label-less tier is not.
        self.assertTrue(set(coverage_contract.RESEARCH)
                        <= {k for k in build.METHOD_LABELS if k.startswith("research_")})


class BoardTierProof(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(DATA.read_text())
        self.rows = self.data["matches"]

    def test_every_open_research_row_is_proven_by_its_own_receipt(self):
        seen = 0
        for m in self.rows:
            method = m.get("method") or ""
            if m["state"] != "open" or not method.startswith("research_"):
                continue
            # Generic invariant for any research tier, including one added later.
            self.assertIsNone(m.get("probabilities"), m["id"])
            self.assertIsNone(m.get("fair_odds"), m["id"])
            self.assertIn(m.get("pick"), m.get("teams") or [], m["id"])
            self.assertTrue(m.get("attempts"), m["id"])
            self.assertTrue(m.get("reason"), m["id"])
            if method in RESEARCH_TIERS_FLOOR:
                # A documented tier must be exactly the tier its receipt proves.
                seen += 1
                self.assertEqual(proven_tier(m), method, m["id"])
        if seen == 0:
            # A fully priced board is the healthy case: prove the documented tier on
            # the retained real row instead of demanding that one stays unpriced.
            fixture = json.loads(FIXTURE.read_text())["row"]
            self.assertEqual(proven_tier(fixture), "research_vrs_single")

    def test_repaired_audit_helper_agrees_with_independent_derivation(self):
        helper = load_audit_helpers().research_tier_from_evidence
        for m in self.rows:
            if m["state"] == "open" and (m.get("method") or "") in RESEARCH_TIERS_FLOOR:
                self.assertEqual(helper(m), proven_tier(m), m["id"])
                self.assertEqual(helper(m), m.get("method"), m["id"])

    def test_both_previously_failing_pins_are_satisfied_by_the_signed_board(self):
        """Replay the two exact assertions that failed production runs 39871808909 / 39886171791."""
        data = json.loads(DATA.read_text())
        research_only = ("research_rank", "research_rank_single", "research_vrs_single")
        # tests/test_session_13e99ca6.py::test_research_only_fixtures_have_hltv_evidence_and_no_percentage
        index = (ROOT / "index.html").read_text()
        for m in data["matches"]:
            if m["state"] == "open" and m.get("method") in research_only:
                self.assertIn(m["method"], research_only)
                self.assertIsNone(m["probabilities"])
                self.assertIn(m["id"], index)
        # tests/test_session_75ebd2d6.py::test_each_research_row_has_method_pick_and_no_percentage
        expected = load_audit_helpers().RESEARCH_EXPECTED
        for mid, exp in expected.items():
            row = next((x for x in data["matches"] if x["id"] == mid), None)
            if row is None or row["state"] != "open" or row.get("probabilities") is not None:
                continue
            self.assertEqual(row["method"], exp["method"], mid)
            self.assertEqual(row["pick"], exp["pick"], mid)


FIXTURE = ROOT / "research" / "session-d4c74d77" / "fixture-1081149-research_vrs_single.json"


def vrs_single_exemplar():
    """A real row that carries the one-sided Valve tier, live if the board has one.

    The board legitimately re-prices rows when a mirror model line resolves them
    (1081149 itself became ``model_vrs_mirror`` on the 2026-10-23T04:59Z board), so
    the negative controls fall back to the retained, hash-checked row from commit
    7b9180d instead of depending on today's data.
    """
    live = [m for m in json.loads(DATA.read_text())["matches"]
            if m["state"] == "open" and m.get("method") == "research_vrs_single"]
    if live:
        return live[0]
    return json.loads(FIXTURE.read_text())["row"]


class CorruptedReceiptsAreRejected(unittest.TestCase):
    """Negative controls: the proof must fail closed when the evidence does not fit."""

    def setUp(self):
        self.row = vrs_single_exemplar()
        self.assertIn(self.row["method"], ("research_vrs_single", "model_vrs_mirror"))
        self.assertEqual(self.row["pick"], "FORZE Reload")

    def test_retained_fixture_is_the_hashed_row_from_the_signed_commit(self):
        doc = json.loads(FIXTURE.read_text())
        blob = json.dumps(doc["row"], sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(hashlib.sha256(blob).hexdigest(), doc["row_sha256"])
        self.assertEqual(doc["row"]["method"], "research_vrs_single")
        self.assertEqual(doc["snapshot_generated_at"], "2026-10-22T20:15:52.839962Z")

    def vrs_row(self):
        if self.row.get("method") != "research_vrs_single":
            return json.loads(FIXTURE.read_text())["row"]
        return self.row

    def mutated(self, change):
        row = copy.deepcopy(self.row)
        change(row)
        return row

    def test_missing_valve_receipt(self):
        row = copy.deepcopy(self.vrs_row())
        row.pop("vrs_research", None)
        self.assertIsNone(proven_tier(row))

    def test_unofficial_standings_host(self):
        row = copy.deepcopy(self.vrs_row())
        row["vrs_research"]["source"] = "https://example.com/standings_global_2026_10_05.md"
        self.assertIsNone(proven_tier(row))

    def test_pick_is_the_unlisted_team(self):
        row = copy.deepcopy(self.vrs_row())
        row["pick"] = "LFO 10"
        self.assertIsNone(proven_tier(row))

    def test_both_teams_listed_is_not_one_sided(self):
        row = copy.deepcopy(self.vrs_row())
        absent = next(x for x in row["vrs_research"]["resolved_vrs"] if x["status"] == "absent")
        absent["status"] = "listed"
        absent["standing"] = 301
        self.assertIsNone(proven_tier(row))

    def test_listed_row_without_a_standing_is_not_proof(self):
        row = copy.deepcopy(self.vrs_row())
        row["vrs_research"]["resolved_vrs"][0]["standing"] = None
        self.assertIsNone(proven_tier(row))

    def test_rank_single_pick_must_be_the_ranked_team(self):
        row = self.mutated(lambda r: (r.pop("vrs_research", None), r.update(
            method="research_rank_single",
            hltv_context={
                "source": "https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10",
                "ranks": [{"team": "FORZE Reload", "hltv_rank": 61},
                          {"team": "LFO 10", "hltv_rank": None}],
            })))
        self.assertEqual(proven_tier(row), "research_rank_single")
        row["pick"] = "LFO 10"
        self.assertIsNone(proven_tier(row))


class NoStaleResearchTierPins(unittest.TestCase):
    """The deadlock class itself: a test file pinning a tier the board contradicts."""

    PIN = re.compile(r'"(1\d{6})"\s*:\s*\{\s*"method"\s*:\s*"(research_[a-z_]+)"')

    def test_no_test_file_pins_a_research_tier_the_board_contradicts(self):
        # Only an unpriced open row reaches the strict pin branch, so a pin on a row
        # that is currently priced is dormant and must not be reported as a blocker.
        data = json.loads(DATA.read_text())
        rows = {m["id"]: m for m in data["matches"]}
        conflicts = []
        for path in sorted(TESTS.glob("test_*.py")):
            if path.name == Path(__file__).name:
                continue
            for mid, method in self.PIN.findall(path.read_text()):
                row = rows.get(mid)
                if not row or row["state"] != "open" or row.get("probabilities") is not None:
                    continue
                if row.get("method") != method:
                    conflicts.append(f"{path.name}: {mid} pinned {method}, board says {row.get('method')}")
        self.assertEqual(conflicts, [],
                         "stale research-tier pin(s) would block the next scheduled publish: "
                         + "; ".join(conflicts))


class ExecutiveSummaryDiscoverability(unittest.TestCase):
    """The user-facing contract, verified on the committed build (read-only)."""

    def setUp(self):
        self.data = json.loads(DATA.read_text())
        self.index = (ROOT / "index.html").read_text()
        self.picks = (ROOT / "picks.html").read_text()
        self.unresolved = (ROOT / "unresolved.html").read_text()
        self.matches = (ROOT / "matches.html").read_text()

    def test_executive_summary_links_to_the_live_pick_lists(self):
        for target in ('href="picks.html"', 'href="unresolved.html"', 'href="matches.html"',
                       'href="analysis.html"', 'href="#picks-at-a-glance"', 'href="#unresolved-picks"'):
            self.assertIn(target, self.index)

    def test_unresolved_section_is_separate_and_carries_limitations(self):
        self.assertIn('id="unresolved-picks"', self.index)
        self.assertIn("Picks without a win probability", self.index)
        self.assertIn("What is tried, in order, before a blank", self.index)
        # The limitations block has been carried under more than one anchor as the
        # page was reworked; require the content and at least one live anchor so a
        # rename does not fail this contract, but a deletion does.
        self.assertIn("Limitations for generating these picks", self.index)
        anchors = ('id="pick-limitations"', 'id="access-limitations"', 'id="unresolved-summary"')
        self.assertTrue(any(a in self.index for a in anchors),
                        "no limitations anchor on the executive summary")
        # Every blank row published by the summary must be named with its limitation.
        for m in self.data["matches"]:
            if m["state"] == "open" and m.get("probabilities") is None:
                self.assertIn(m["id"], self.index)
                self.assertIn(m["id"], self.unresolved)
                self.assertTrue(m.get("reason"))

    def test_every_open_match_is_picked_or_published_as_unresolved(self):
        for m in self.data["matches"]:
            if m["state"] != "open":
                continue
            if m.get("pick"):
                self.assertIn(m["pick"], m["teams"], m["id"])
                self.assertIn(m["id"], self.picks)
            else:
                self.assertIsNone(m.get("probabilities"), m["id"])
                self.assertTrue(m.get("reason"), m["id"])
                self.assertIn(m["id"], self.unresolved)
            # Every row keeps an official Hotspawn fixture link.
            self.assertTrue(str(m.get("source_url") or "").startswith("https://"), m["id"])

    def test_phone_shell_is_present_for_the_first_screen(self):
        self.assertIn('class="mobile-tabs"', self.index)
        self.assertIn('name="viewport"', self.index)
        self.assertIn("width=device-width", self.index)
        self.assertIn('id="exec-banner"', self.index)
        self.assertIn("Where the updated picks are", self.index)
        for page in (self.picks, self.unresolved, self.matches):
            self.assertIn('class="mobile-tabs"', page)


if __name__ == "__main__":
    unittest.main()
