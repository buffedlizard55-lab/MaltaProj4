"""Audit one fresh board and its targeted HLTV/esportsbook probe.

This session-specific verifier is deliberately read-only.  ``scripts.refresh``
collects the live inventory and tries the featured market path; only rows still
without a supported percentage are then researched by
``scripts.probe_bf09aa40`` in the order requested by the project: HLTV first,
then public esportsbook/odds listings.  This module joins those two receipts and
fails closed when a row, probability, source URL, or research target is missing.

It never creates a pick or a probability.  Missing evidence is an explicit gap
in the JSON report and a non-zero exit, not a value to infer.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

MARKET_METHODS = {"exchange", "exchange_wide", "bookmaker_fallback"}
RESEARCH_PREFIX = "research_"


def https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parts = urlsplit(value)
    return parts.scheme == "https" and bool(parts.netloc)


def audit(snapshot: dict, targeted: dict) -> dict:
    rows = [row for row in snapshot.get("matches", []) if row.get("state") == "open"]
    gaps = [row for row in rows if row.get("probabilities") is None]
    targeted_by_id = {str(row.get("id")): row for row in targeted.get("gap_rows", [])}
    violations: list[dict] = []
    audited_rows: list[dict] = []

    if snapshot.get("coverage") != "verified":
        violations.append({"code": "inventory-not-verified", "value": snapshot.get("coverage")})

    for row in rows:
        fixture_id = str(row.get("id") or "")
        teams = row.get("teams") or []
        probabilities = row.get("probabilities")
        pick = row.get("pick")
        method = row.get("method")
        evidence = row.get("evidence") or []
        attempts = row.get("attempts") or []
        row_problems: list[str] = []

        if len(teams) != 2 or not all(isinstance(team, str) and team.strip() for team in teams):
            row_problems.append("two verified team labels are required")
        if not fixture_id:
            row_problems.append("fixture id is missing")
        if not https_url(row.get("source_url")):
            row_problems.append("official Hotspawn inventory link is missing")
        if pick not in teams:
            row_problems.append("pick is missing or is not one of the two teams")

        probability_source = None
        if probabilities is not None:
            try:
                numbers = [float(value) for value in probabilities]
            except (TypeError, ValueError):
                numbers = []
            if len(numbers) != 2 or any(value <= 0 or value >= 1 for value in numbers) or abs(sum(numbers) - 1) > 1e-6:
                row_problems.append("two finite probabilities summing to one are required")
            if not evidence:
                row_problems.append("priced row has no primary evidence")
            else:
                probability_source = evidence[0].get("api_url") or evidence[0].get("url")
                if not https_url(probability_source):
                    row_problems.append("priced row has no HTTPS primary-source link")
                if "hotspawn" in str(probability_source).lower():
                    row_problems.append("Hotspawn must never be a probability source")
        else:
            target = targeted_by_id.get(fixture_id)
            if target is None:
                row_problems.append("unpriced row is absent from the targeted research probe")
            providers = [attempt.get("provider") for attempt in attempts]
            # The collector must establish identity/context at HLTV before the
            # Pinnacle and other book fallbacks.  Not every host is reachable,
            # but the attempt itself and its order must be retained.
            try:
                hltv_index = providers.index("HLTV")
            except ValueError:
                hltv_index = None
                row_problems.append("unpriced row has no recorded HLTV attempt")
            try:
                pinnacle_index = providers.index("Pinnacle")
            except ValueError:
                pinnacle_index = None
                row_problems.append("unpriced row has no recorded Pinnacle attempt")
            if hltv_index is not None and pinnacle_index is not None and hltv_index > pinnacle_index:
                row_problems.append("HLTV research did not precede the esportsbook fallback")
            if not row.get("reason"):
                row_problems.append("unpriced row does not explain its limitation")
            if method and not str(method).startswith(RESEARCH_PREFIX):
                row_problems.append("unpriced pick is not labelled research-only")

        for problem in row_problems:
            violations.append({"code": "row-invalid", "fixture_id": fixture_id, "problem": problem})
        audited_rows.append({
            "id": fixture_id,
            "teams": teams,
            "start": row.get("start"),
            "pick": pick,
            "method": method,
            "probabilities": probabilities,
            "inventory_source": row.get("source_url"),
            "probability_source": probability_source,
            "targeted_research": fixture_id in targeted_by_id,
            "problems": row_problems,
        })

    snapshot_gap_ids = {str(row.get("id")) for row in gaps}
    target_gap_ids = set(targeted_by_id)
    if snapshot_gap_ids != target_gap_ids:
        violations.append({
            "code": "target-set-mismatch",
            "snapshot_only": sorted(snapshot_gap_ids - target_gap_ids),
            "probe_only": sorted(target_gap_ids - snapshot_gap_ids),
        })

    no_pick = [str(row.get("id")) for row in rows if not row.get("pick")]
    research_only = [str(row.get("id")) for row in gaps if row.get("pick")]
    return {
        "schema_version": 1,
        "snapshot_generated_at": snapshot.get("generated_at"),
        "fixtures_observed_at": snapshot.get("fixtures_observed_at"),
        "coverage": snapshot.get("coverage"),
        "counts": {
            "rows_total": len(snapshot.get("matches", [])),
            "open": len(rows),
            "with_pick": len(rows) - len(no_pick),
            "with_probability": len(rows) - len(gaps),
            "research_only": len(research_only),
            "without_pick": len(no_pick),
        },
        "research_only_ids": research_only,
        "unresolved_without_pick_ids": no_pick,
        "targeted_probe": {
            "probed_at": targeted.get("probed_at"),
            "gap_ids": sorted(target_gap_ids),
            "book_listing_hits": len(targeted.get("matches_found") or []),
            "polymarket_gap_hits": len(((targeted.get("markets") or {}).get("polymarket") or {}).get("gap_hits") or []),
            "pinnacle_gap_hits": len(((targeted.get("markets") or {}).get("pinnacle") or {}).get("gap_hits") or []),
        },
        "rows": audited_rows,
        "violations": violations,
        "verdict": "pass" if not violations else "fail",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--targeted-report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    snapshot = json.loads(Path(args.snapshot).read_text())
    targeted = json.loads(Path(args.targeted_report).read_text())
    result = audit(snapshot, targeted)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    counts = result["counts"]
    print(
        "open={open} picks={with_pick} priced={with_probability} "
        "research_only={research_only} unresolved={without_pick} violations={violations}".format(
            **counts, violations=len(result["violations"])
        )
    )
    for violation in result["violations"]:
        print("FAIL " + json.dumps(violation, ensure_ascii=False, sort_keys=True))
    raise SystemExit(0 if result["verdict"] == "pass" else 1)


if __name__ == "__main__":
    main()
