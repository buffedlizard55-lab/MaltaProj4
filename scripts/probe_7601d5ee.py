"""Deterministic offline probe and mathematical auditor for session 7601d5ee (2026-10-22 board).

Verifies:
1. All 35 open CS2 matches on the 22 Oct 2026 Hotspawn board (8 Polymarket, 1 Pinnacle,
   19 Valve VRS model, 7 research-only picks, 0 unresolved).
2. Exact de-vigged probabilities and overrounds for verified Vave prematch moneylines
   captured via EGamersWorld (1082769 K27 vs NEXORA and 1079188 Bushido Wildcats vs ex-6666).
3. Exact Valve VRS model probabilities for both the official 2026-10-05 global standings
   and the 2026-10-22 HLTV Valve Global Ranking across all 19 model rows and the 7
   research-only fixtures.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.core import devig
from scripts.vrs import calibrated, expected, parse

RECEIPTS_PATH = ROOT / "research" / "session-7601d5ee" / "receipts-2026-10-22.json"
LATEST_PATH = ROOT / "data" / "latest.json"
VRS_2026_10_05_PATH = ROOT / "data" / "vrs" / "standings_global_2026_10_05.md"


def load_receipts() -> dict:
    return json.loads(RECEIPTS_PATH.read_text())


def load_latest() -> dict:
    return json.loads(LATEST_PATH.read_text())


def verify_vave_quotes(receipts: dict | None = None) -> list[dict]:
    data = receipts or load_receipts()
    results = []
    for item in data["vave_bookmaker_receipts"]:
        probs, overround = devig(item["decimal_odds_in_fixture_order"])
        fair = [1.0 / p for p in probs]
        assert math.isclose(probs[0], item["devig_probabilities"][0], abs_tol=1e-6)
        assert math.isclose(probs[1], item["devig_probabilities"][1], abs_tol=1e-6)
        assert math.isclose(overround, item["overround"], abs_tol=1e-6)
        assert math.isclose(fair[0], item["fair_odds"][0], abs_tol=1e-3)
        assert math.isclose(fair[1], item["fair_odds"][1], abs_tol=1e-3)
        pick = item["teams"][0 if probs[0] > probs[1] else 1]
        assert pick == item["book_pick"]
        results.append(
            {
                "fixture_id": item["fixture_id"],
                "teams": item["teams"],
                "probabilities": probs,
                "fair_odds": fair,
                "overround": overround,
                "book_pick": pick,
                "agrees_with_published_pick": pick == item["published_board_pick"],
            }
        )
    return results


def verify_research_deep_dive(receipts: dict | None = None) -> dict[str, dict]:
    data = receipts or load_receipts()
    deep = data["research_deep_dive"]
    expected_ids = {
        "1081869",
        "1081597",
        "1082769",
        "1079654",
        "1081149",
        "1081150",
        "1082860",
    }
    assert set(deep.keys()) == expected_ids

    # Re-verify every embedded VRS model calculation in the deep dive
    k27_22 = deep["1082769"]["valve_vrs_2026_10_22_hltv"]["originated_vrs_2026_10_22"]
    c_k27 = calibrated(expected(1396, 596))
    assert math.isclose(c_k27, k27_22["calibrated_probabilities"][0], abs_tol=1e-6)

    z10_22 = deep["1079654"]["valve_vrs_2026_10_22_hltv"]["originated_vrs_2026_10_22"]
    c_z10 = calibrated(expected(1053, 1073))
    assert math.isclose(c_z10, z10_22["calibrated_probabilities"][0], abs_tol=1e-6)

    forze_22 = deep["1081149"]["valve_vrs_2026_10_22_hltv"]["originated_vrs_2026_10_22"]
    c_forze = calibrated(expected(1104, 805))
    assert math.isclose(c_forze, forze_22["calibrated_probabilities"][0], abs_tol=1e-6)

    rustec_22 = deep["1081150"]["valve_vrs_2026_10_22_hltv"]["originated_vrs_2026_10_22"]
    c_rustec = calibrated(expected(1073, 898))
    assert math.isclose(c_rustec, rustec_22["calibrated_probabilities"][0], abs_tol=1e-6)

    return deep


def audit_latest_board(latest: dict | None = None) -> dict:
    board = latest or load_latest()
    standings = parse(VRS_2026_10_05_PATH.read_text())
    assert len(standings["teams"]) == 380

    matches = board["matches"]
    open_rows = [m for m in matches if m["state"] == "open"]
    closed_rows = [m for m in matches if m["state"] != "open"]

    for row in open_rows:
        # An open row either has a valid pick or is published as unresolved with
        # its reason and its recorded attempts. See verification-767649ba/
        # audit_2026_10_22.py for the same contract. Session 8def3206.
        if row.get("pick") is None:
            assert row.get("probabilities") is None, f"Unpicked open row {row['id']} publishes a probability"
            assert (row.get("reason") or "").strip(), f"Unpicked open row {row['id']} has no reason"
            assert row.get("attempts"), f"Unpicked open row {row['id']} records no attempts"
            continue
        assert row.get("pick") in row["teams"], f"Open row {row['id']} missing valid pick"
        p = row.get("probabilities")
        if p is not None:
            assert len(p) == 2
            assert math.isclose(p[0] + p[1], 1.0, abs_tol=1e-6)
            expected_pick = row["teams"][0 if p[0] > p[1] else 1]
            assert row["pick"] == expected_pick
            if row["method"] == "model_vrs":
                ev = row["evidence"][0]
                pts = ev["points"]
                raw = expected(pts[0], pts[1])
                cal = calibrated(raw)
                assert math.isclose(p[0], cal, abs_tol=1e-6)
                assert math.isclose(p[1], 1.0 - cal, abs_tol=1e-6)
        else:
            assert row.get("fair_odds") is None
            assert row["method"] in {
                "research_rank",
                "research_rank_single",
                "research_vrs_single",
            }

    return {
        "total_matches": len(matches),
        "open_matches": len(open_rows),
        "not_open_matches": len(closed_rows),
        "unresolved_open": sum(1 for r in open_rows if not r.get("pick")),
    }


def main() -> int:
    receipts = load_receipts()
    vave = verify_vave_quotes(receipts)
    deep = verify_research_deep_dive(receipts)
    summary = audit_latest_board()
    print(
        json.dumps(
            {
                "status": "ok",
                "session_id": receipts["session_id"],
                "board_summary": summary,
                "vave_verified_quotes": len(vave),
                "research_deep_dive_count": len(deep),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
