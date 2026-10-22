"""Unit and integration tests for session 7601d5ee."""
from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path

from scripts.core import devig
from scripts.vrs import calibrated, expected
from scripts import probe_7601d5ee

ROOT = Path(__file__).resolve().parents[1]


def _load_audit_module():
    path = ROOT / "verification-7601d5ee" / "audit_board_7601d5ee.py"
    spec = importlib.util.spec_from_file_location("audit_board_7601d5ee", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class Session7601d5eeTests(unittest.TestCase):
    def test_vave_bookmaker_quotes_math(self):
        receipts = probe_7601d5ee.load_receipts()
        verified = probe_7601d5ee.verify_vave_quotes(receipts)
        self.assertEqual(len(verified), 2)

        by_id = {r["fixture_id"]: r for r in verified}
        k27 = by_id["1082769"]
        self.assertEqual(k27["book_pick"], "K27")
        self.assertTrue(k27["agrees_with_published_pick"])
        p_k27, m_k27 = devig([1.021, 8.1])
        self.assertAlmostEqual(k27["probabilities"][0], p_k27[0], places=6)
        self.assertAlmostEqual(k27["overround"], m_k27, places=6)

        bw = by_id["1079188"]
        self.assertEqual(bw["book_pick"], "ex-6666")
        self.assertFalse(bw["agrees_with_published_pick"])
        p_bw, m_bw = devig([2.26, 1.55])
        self.assertAlmostEqual(bw["probabilities"][1], p_bw[1], places=6)
        self.assertAlmostEqual(bw["overround"], m_bw, places=6)

    def test_research_deep_dive_vrs_2026_10_22_math(self):
        deep = probe_7601d5ee.verify_research_deep_dive()
        self.assertEqual(
            set(deep.keys()),
            {"1081869", "1081597", "1082769", "1079654", "1081149", "1081150", "1082860"},
        )
        # K27 (1396) vs NEXORA (596) on 22 Oct VRS agrees closely with Vave 1.021 / 8.10
        p_vrs_k27 = calibrated(expected(1396, 596))
        p_vave_k27, _ = devig([1.021, 8.1])
        self.assertLess(abs(p_vrs_k27 - p_vave_k27[0]), 0.005)

    def test_probe_and_audit_board(self):
        board_summary = probe_7601d5ee.audit_latest_board()
        self.assertGreaterEqual(board_summary["total_matches"], 35)
        self.assertGreaterEqual(board_summary["open_matches"], 1)
        self.assertGreaterEqual(board_summary["unresolved_open"], 0)
        self.assertEqual(board_summary["priced_open"] + board_summary["research_only_open"] +
                         board_summary["unresolved_open"], board_summary["open_matches"])

        audit_mod = _load_audit_module()
        report = audit_mod.run_all(ROOT)
        self.assertEqual(report["status"], "ok")
        self.assertGreaterEqual(report["board"]["unresolved_open"], 0)
        self.assertEqual(
            report["board"]["priced_open"] + report["board"]["research_only_open"] +
            report["board"]["unresolved_open"], report["board"]["open_matches"],
        )


if __name__ == "__main__":
    unittest.main()
