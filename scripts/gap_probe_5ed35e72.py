"""Gap probe for session 5ed35e72.

Reads the snapshot produced by the unmodified ``scripts.refresh`` and lists,
for every **open** fixture, whether the board has a pick and whether it has a
published probability pair. It never computes a price and never writes to a
published file: its only job is to name the exact fixtures that still need
research, with the collector's own reasons attached, so the research step can
be aimed at real rows instead of a guess.

Output fields per gap row: the fixture id, teams, competition, tier, series
format, start, lock, current pick/method/probabilities, the collector's reason,
its flags, the HLTV context URL it stored, and a one-line classification:

* ``no_pick``            - no pick at all (not even a research-only one)
* ``pick_without_price`` - a sourced research pick with blank probabilities
* ``price_without_pick`` - a probability pair that produced no selection
                          (should not occur; reported loudly if it does)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def classify(row: dict) -> str:
    has_pick = bool(row.get("pick"))
    has_price = row.get("probabilities") is not None
    if not has_pick:
        return "no_pick"
    if not has_price:
        return "pick_without_price"
    return "price_without_pick"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    snapshot = json.loads(Path(args.snapshot).read_text())
    rows = snapshot.get("matches") or []
    open_rows = [r for r in rows if r.get("state") == "open"]
    gaps = []
    for row in open_rows:
        has_price = row.get("probabilities") is not None
        if row.get("pick") and has_price:
            continue
        context = row.get("hltv_context") or {}
        gaps.append({
            "id": row.get("id"),
            "teams": row.get("teams"),
            "competition": row.get("competition"),
            "tier": row.get("tier"),
            "best_of": row.get("best_of"),
            "start": row.get("start"),
            "lock": row.get("lock"),
            "state": row.get("state"),
            "pick": row.get("pick"),
            "method": row.get("method"),
            "probabilities": row.get("probabilities"),
            "fair_odds": row.get("fair_odds"),
            "reason": row.get("reason"),
            "flags": row.get("flags"),
            "hltv_source": context.get("source"),
            "hltv_ranks": context.get("ranks"),
            "source_url": row.get("source_url"),
            "classification": classify(row),
            "attempts": row.get("attempts"),
        })

    methods = {}
    for row in open_rows:
        key = row.get("method") or "none"
        methods[key] = methods.get(key, 0) + 1

    out = {
        "snapshot_generated_at": snapshot.get("generated_at"),
        "fixtures_observed_at": snapshot.get("fixtures_observed_at"),
        "coverage": snapshot.get("coverage"),
        "coverage_counts": snapshot.get("coverage_counts"),
        "rows_total": len(rows),
        "open_total": len(open_rows),
        "open_priced": sum(1 for r in open_rows if r.get("probabilities") is not None),
        "open_with_pick": sum(1 for r in open_rows if r.get("pick")),
        "open_methods": methods,
        "gap_count": len(gaps),
        "no_pick": [g["id"] for g in gaps if g["classification"] == "no_pick"],
        "pick_without_price": [g["id"] for g in gaps
                               if g["classification"] == "pick_without_price"],
        "price_without_pick": [g["id"] for g in gaps
                               if g["classification"] == "price_without_pick"],
        "gaps": gaps,
    }
    Path(args.output).write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print("rows=%d open=%d priced=%d with_pick=%d gaps=%d no_pick=%s"
          % (out["rows_total"], out["open_total"], out["open_priced"],
             out["open_with_pick"], out["gap_count"], ",".join(out["no_pick"]) or "-"))


if __name__ == "__main__":
    main()
