"""Session 2d0a85f2 regression tests.

These tests never touch the network. They prove that the session's research
records are internally consistent and that the integration applier fails closed:
an anchor that no longer satisfies Valve's own >=3-shared-player rule, or that
lacks an official HLTV lineup source, can never reach the data files.
"""
import hashlib
import json
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import vrs  # noqa: E402
from scripts.apply_2d0a85f2 import ANCHOR_SRC, NOTES, NOTES_DST, ANCHOR_DST, validate_anchors  # noqa: E402


def payload():
    return json.loads(ANCHOR_SRC.read_text())


PINNED_VRS_NOW = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)


class AnchorValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.standings, cls.meta = vrs.vendored(PINNED_VRS_NOW)

    def test_anchor_resolves_the_duplicate_label_exactly_once(self):
        accepted, errors = validate_anchors(payload(), self.standings)
        self.assertEqual(errors, [])
        self.assertEqual(len(accepted), 1)
        a = accepted[0]
        self.assertEqual(a["team"], "benched gods")
        self.assertEqual(a["valve_standing"], 157)
        self.assertEqual(a["overlap_selected"], 5)
        self.assertEqual(a["overlap_others"], [2])

    def test_weak_lineup_is_rejected(self):
        p = payload()
        p["anchors"][0]["anchor_lineup"] = ["Wign", "K014NZ", "someone", "else", "new"]
        accepted, errors = validate_anchors(p, self.standings)
        self.assertEqual(accepted, [])
        self.assertTrue(any("shared players" in e for e in errors))

    def test_wrong_points_pair_is_rejected(self):
        p = payload()
        p["anchors"][0]["valve_points"] = 999999
        accepted, errors = validate_anchors(p, self.standings)
        self.assertEqual(accepted, [])
        self.assertTrue(any("standing/points" in e for e in errors))

    def test_third_party_lineup_alone_is_rejected(self):
        p = payload()
        p["anchors"][0]["lineup_sources"] = [
            s for s in p["anchors"][0]["lineup_sources"]
            if s["kind"] != "official_hltv_played_match_lineup"
        ]
        accepted, errors = validate_anchors(p, self.standings)
        self.assertEqual(accepted, [])
        self.assertTrue(any("official HLTV lineup" in e for e in errors))

    def test_vendored_file_is_the_official_blob(self):
        out = subprocess.run(
            ["git", "hash-object", str(ROOT / "data" / "vrs" / self.meta["file"])],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        self.assertEqual(out, payload()["anchors"][0]["valve_blob_sha"])
        self.assertEqual(out, "2aa2805394fbc68f36a5752a5b16026f2ab2fed5")


class ReceiptShape(unittest.TestCase):
    def test_every_receipt_is_dated_sourced_and_purposed(self):
        doc = json.loads((ROOT / "research" / "session-2d0a85f2" / "receipts-2026-10-21.json").read_text())
        self.assertTrue(doc["receipts"])
        for r in doc["receipts"]:
            urls = [r["url"]] if "url" in r else r["urls"]
            self.assertTrue(all(u.startswith("https://") for u in urls), r["id"])
            self.assertRegex(r["observed_at"], r"^2026-10-21T\d{2}:\d{2}:\d{2}Z$")
            self.assertTrue(r["use"].strip())
            self.assertTrue(r["showed"])

    def test_rejected_prices_are_never_probabilities(self):
        doc = json.loads((ROOT / "research" / "session-2d0a85f2" / "receipts-2026-10-21.json").read_text())
        egw = next(r for r in doc["receipts"] if r["id"] == "R3")
        self.assertIn("REJECTED", egw["use"])
        hltv = next(r for r in doc["receipts"] if r["id"] == "R9")
        self.assertIn("REJECTED", hltv["use"])


class NoteShape(unittest.TestCase):
    def test_notes_carry_official_links(self):
        for n in NOTES:
            self.assertTrue(n["id"].startswith("2d0a85f2-"))
            self.assertTrue(n["status"].startswith("Needs review"))
            self.assertTrue(len(n["finding"]) > 200)
            for s in n["sources"]:
                self.assertTrue(s["url"].startswith("https://"))
                self.assertTrue(s["label"].strip())


def fixture_stub():
    return {
        "id": "1081597",
        "teams": ["benched gods", "TitanFlow"],
        "state": "open",
        "probabilities": None,
        "fair_odds": None,
        "pick": None,
        "method": None,
        "attempts": [],
        "flags": [],
        "hltv_context": {},
    }


class AnchorUnblocksThePickOnlyTier(unittest.TestCase):
    """End-to-end, offline: the anchor turns 'no pick at all' into the documented
    pick-only research tier, and changes nothing else."""

    @classmethod
    def setUpClass(cls):
        cls.standings, cls.meta = vrs.vendored(PINNED_VRS_NOW)
        accepted, errors = validate_anchors(payload(), cls.standings)
        assert not errors, errors
        cls.anchors = accepted

    def test_without_anchor_the_tier_stays_silent(self):
        f = fixture_stub()
        vrs.research_single(f, self.standings, self.meta, {})
        self.assertIsNone(f.get("pick"))
        self.assertTrue(any(a["status"] == "unresolved" for a in f["attempts"]))

    def test_with_anchor_the_pick_only_tier_fires(self):
        from scripts import vrs_anchor_2d0a85f2 as anchor_mod

        f = fixture_stub()
        lineups = anchor_mod.with_anchors(f, {}, anchors=self.anchors)
        self.assertIn("benched gods", lineups)
        vrs.research_single(f, self.standings, self.meta, lineups)
        self.assertEqual(f.get("pick"), "benched gods")
        self.assertEqual(f.get("method"), "research_vrs_single")
        self.assertIsNone(f.get("probabilities"))
        self.assertIsNone(f.get("fair_odds"))
        anchor_attempts = [a for a in f["attempts"] if a["provider"] == "Valve VRS roster anchor"]
        self.assertEqual(len(anchor_attempts), 1)
        self.assertIn("hltv.org", anchor_attempts[0]["url"])

    def test_anchor_never_overrides_a_fixture_lineup_or_other_fixtures(self):
        from scripts import vrs_anchor_2d0a85f2 as anchor_mod

        f = fixture_stub()
        f["teams"] = ["Zetta", "LOS NINOS"]
        out = anchor_mod.with_anchors(f, {"Zetta": ["a", "b", "c", "d", "e"]}, anchors=self.anchors)
        self.assertEqual(out, {"Zetta": ["a", "b", "c", "d", "e"]})
        self.assertEqual(f["attempts"], [])

    def test_missing_anchor_file_is_a_no_op(self):
        from scripts import vrs_anchor_2d0a85f2 as anchor_mod

        f = fixture_stub()
        out = anchor_mod.with_anchors(f, {}, anchors=[])
        self.assertEqual(out, {})
        self.assertEqual(f["attempts"], [])


class ApplierIsSafeByDefault(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        before = {
            p: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (NOTES_DST, ANCHOR_DST) if p.exists()
        }
        out = subprocess.run(
            [sys.executable, "-m", "scripts.apply_2d0a85f2"],
            capture_output=True, text=True, cwd=ROOT,
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("dry run", out.stdout)
        after = {
            p: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (NOTES_DST, ANCHOR_DST) if p.exists()
        }
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
