"""Gap probe for session 8c8e3c5f: why does each open row lack a pick or a percentage?

Reads a refreshed snapshot (produced by the unmodified ``scripts.refresh``) and,
for every open fixture whose ``pick`` or ``probabilities`` is missing, records:

* the full attempt ledger the collector already stored on the row,
* the HLTV context the collector stored (ranks, VRS ranks shown on HLTV, lineups),
* a fresh, read-only Valve VRS identification per team (unique label, roster
  overlap against the stored HLTV lineup, or absence from the 380-team global
  standings) using this repository's own ``scripts.vrs.identify``,
* whether the fixture's HLTV page displayed a VRS rank for each team.

It never invents a price, never treats a rejected quote as a line, and makes no
network calls of its own beyond reading the snapshot and the vendored official
standings copy, so every number in the output traces to the snapshot or to
Valve's published file (live copy is fetched by the refresh that ran before it).
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts import vrs
from scripts.core import norm


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    snapshot = json.loads(Path(args.snapshot).read_text())
    standings, meta = vrs.vendored(datetime.now(timezone.utc))

    gaps = []
    for row in snapshot["matches"]:
        if row["state"] != "open":
            continue
        if row.get("pick") and row.get("probabilities") is not None:
            continue
        context = row.get("hltv_context") or {}
        lineups = {x["team"]: x["players"] for x in context.get("lineups", [])}
        per_team = []
        for team in row["teams"]:
            lineup = next((v for k, v in lineups.items() if norm(k) == norm(team)), None)
            entry, note = vrs.identify(team, standings, lineup)
            label_count = sum(norm(r["name"]) == norm(team) for r in standings["teams"])
            rank_row = next(
                (r for r in context.get("ranks", []) if norm(r.get("team") or "") == norm(team)), None
            )
            per_team.append({
                "team": team,
                "hltv_lineup": lineup,
                "hltv_rank_row": rank_row,
                "vrs_label_count": label_count,
                "vrs_entry": (
                    {k: entry[k] for k in ("standing", "points", "name", "roster", "roster_overlap")}
                    if entry else None
                ),
                "vrs_note": note,
            })
        gaps.append({
            "id": row["id"],
            "teams": row["teams"],
            "competition": row.get("competition"),
            "tier": row.get("tier"),
            "best_of": row.get("best_of"),
            "start": row.get("start"),
            "lock": row.get("lock"),
            "pick": row.get("pick"),
            "method": row.get("method"),
            "probabilities": row.get("probabilities"),
            "reason": row.get("reason"),
            "flags": row.get("flags"),
            "hltv_source": context.get("source"),
            "attempts": row.get("attempts"),
            "per_team": per_team,
        })

    out = {
        "snapshot_generated_at": snapshot.get("generated_at"),
        "fixtures_observed_at": snapshot.get("fixtures_observed_at"),
        "open_total": sum(1 for m in snapshot["matches"] if m["state"] == "open"),
        "gap_count": len(gaps),
        "no_pick": [g["id"] for g in gaps if not g["pick"]],
        "no_probability": [g["id"] for g in gaps if g["probabilities"] is None],
        "vrs_standings": {
            "as_of": standings["as_of"],
            "teams": len(standings["teams"]),
            "file": meta["file"],
            "blob_url": meta["blob_url"],
        },
        "gaps": gaps,
    }
    Path(args.output).write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print("open=%d gaps=%d no_pick=%s" % (out["open_total"], len(gaps), ",".join(out["no_pick"]) or "-"))


if __name__ == "__main__":
    main()
