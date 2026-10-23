"""Read-only, line-by-line acceptance audit for a fresh Hotspawn CS2 snapshot.

This probe does not create or change a pick.  It records exactly what the fresh
collector resolved, which open rows still need the HLTV-first/book fallback
ladder, and every fixture's official review links.  It is deliberately stdlib
only so its accounting is independent of the site builder and collector.

Usage (normally on a GitHub runner with normal source access)::

    python -m scripts.refresh --output runtime/latest.json
    python -m scripts.probe_e141a921 --snapshot runtime/latest.json \
        --previous data/latest.json --output research/harvest-e141a921

The fresh snapshot is copied byte-for-byte into the output directory.  The
JSON and Markdown reports name gaps rather than filling them with guesses.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

HOTSPAWN_HOSTS = {"play.hotspawn.com", "hotspawn.com", "www.hotspawn.com"}
FEED_HOST = "phpstack-1372681-6459848.cloudwaysapps.com"


def https_url(url: str, hosts: set[str] | None = None) -> bool:
    parts = urlsplit(str(url or ""))
    return parts.scheme == "https" and bool(parts.hostname) and (
        hosts is None or parts.hostname in hosts
    )


def external_evidence_urls(row: dict) -> list[str]:
    """Return non-Hotspawn evidence/research URLs in stable order."""
    found: list[str] = []

    def add(value) -> None:
        if isinstance(value, str) and https_url(value):
            host = urlsplit(value).hostname
            if host not in HOTSPAWN_HOSTS and value not in found:
                found.append(value)

    def walk(value) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"url", "api_url", "source", "rank_source", "formula_source",
                           "calibration_source", "alias_source"}:
                    add(item)
                elif key not in {"raw", "raw_text", "html"}:
                    walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    for key in ("evidence", "hltv_context", "hltv_team_pages", "vrs_research",
                "model_check", "attempts"):
        walk(row.get(key))
    return found


def inspect_row(row: dict) -> list[str]:
    """Check source identity and internal pick arithmetic without inferring data."""
    errors: list[str] = []
    fixture_id = str(row.get("id") or "")
    teams = row.get("teams")
    if not fixture_id:
        errors.append("missing fixture id")
    if not isinstance(teams, list) or len(teams) != 2 or not all(
            isinstance(team, str) and team.strip() for team in teams):
        errors.append("fixture does not have two named teams")
        teams = []
    if not https_url(row.get("source_url", ""), HOTSPAWN_HOSTS):
        errors.append("missing official Hotspawn fixture source")
    if not https_url(row.get("feed_url", ""), {FEED_HOST}):
        errors.append("missing official Hotspawn fixture API source")
    if not row.get("fixture_sources"):
        errors.append("no dated fixture-source receipt")

    if row.get("state") != "open":
        return errors

    pick = row.get("pick")
    probabilities = row.get("probabilities")
    if pick is not None and pick not in teams:
        errors.append("pick is not one of the fixture's two teams")
    if probabilities is None:
        if row.get("fair_odds") is not None:
            errors.append("blank probabilities with non-blank fair odds")
        if not row.get("reason"):
            errors.append("open row without a percentage lacks its limitation")
        if pick and not str(row.get("method") or "").startswith("research_"):
            errors.append("unpriced pick is not labelled as research")
        return errors

    if not isinstance(probabilities, list) or len(probabilities) != 2:
        errors.append("priced row does not have two probabilities")
        return errors
    if not all(isinstance(value, (int, float)) and math.isfinite(value) and 0 < value < 1
               for value in probabilities):
        errors.append("probabilities are not finite values strictly between zero and one")
        return errors
    if abs(sum(probabilities) - 1.0) > 1e-9:
        errors.append("probabilities do not sum to one")
    fair_odds = row.get("fair_odds")
    if not isinstance(fair_odds, list) or len(fair_odds) != 2 or any(
            abs(fair - 1 / probability) > 1e-9
            for fair, probability in zip(fair_odds, probabilities)):
        errors.append("fair odds are not reciprocals of the probabilities")
    if pick not in teams:
        errors.append("priced row has no valid pick")
    elif abs(probabilities[0] - probabilities[1]) > 1e-9:
        expected = teams[probabilities[1] > probabilities[0]]
        if pick != expected:
            errors.append("pick does not follow the larger probability")
    evidence = row.get("evidence") or []
    if not evidence:
        errors.append("priced row has no selected evidence")
    external = external_evidence_urls(row)
    if not external:
        errors.append("priced row has no external evidence link")
    if any(urlsplit(url).hostname in HOTSPAWN_HOSTS for url in external):
        errors.append("Hotspawn was retained as probability evidence")
    return errors


def changed_fixtures(snapshot: dict, previous: dict) -> dict:
    old = {str(row.get("id")): row for row in previous.get("matches", [])}
    new = {str(row.get("id")): row for row in snapshot.get("matches", [])}
    changed = []
    for fixture_id in sorted(old.keys() & new.keys()):
        fields = {}
        for field in ("start", "lock", "state", "source_status"):
            if old[fixture_id].get(field) != new[fixture_id].get(field):
                fields[field] = {"previous": old[fixture_id].get(field),
                                 "fresh": new[fixture_id].get(field)}
        if fields:
            changed.append({"id": fixture_id, "teams": new[fixture_id].get("teams"),
                            "changes": fields})
    return {
        "added": sorted(new.keys() - old.keys()),
        "removed": sorted(old.keys() - new.keys()),
        "changed_start_lock_or_state": changed,
    }


def audit(snapshot: dict, previous: dict, snapshot_sha256: str) -> dict:
    rows = snapshot.get("matches") or []
    ids = [str(row.get("id")) for row in rows]
    global_errors = []
    if len(ids) != len(set(ids)):
        global_errors.append("duplicate fixture ids")
    row_results = []
    for row in rows:
        errors = inspect_row(row)
        row_results.append({
            "id": str(row.get("id")),
            "teams": row.get("teams"),
            "competition": row.get("competition"),
            "start": row.get("start"),
            "lock": row.get("lock"),
            "state": row.get("state"),
            "pick": row.get("pick"),
            "method": row.get("method"),
            "probabilities": row.get("probabilities"),
            "reason": row.get("reason"),
            "hotspawn_url": row.get("source_url"),
            "feed_url": row.get("feed_url"),
            "external_evidence_urls": external_evidence_urls(row),
            "errors": errors,
        })
    open_rows = [row for row in rows if row.get("state") == "open"]
    gaps = [row for row in open_rows if not row.get("pick") or row.get("probabilities") is None]
    counts = snapshot.get("coverage_counts") or {}
    inventory_counts = {key: counts.get(key) for key in ("api", "page", "lobby", "retained")}
    parity = len(set(inventory_counts.values())) == 1 and None not in inventory_counts.values()
    if snapshot.get("coverage") != "verified" or not parity:
        global_errors.append("three-view Hotspawn inventory coverage is not verified at parity")
    source_errors = [check for check in snapshot.get("source_checks") or []
                     if check.get("status") not in (None, "ok", 200, "200")]
    return {
        "schema_version": 1,
        "session": "e141a921",
        "snapshot_generated_at": snapshot.get("generated_at"),
        "fixtures_observed_at": snapshot.get("fixtures_observed_at"),
        "previous_generated_at": previous.get("generated_at"),
        "snapshot_sha256": snapshot_sha256,
        "coverage": snapshot.get("coverage"),
        "coverage_counts": inventory_counts,
        "three_view_parity": parity,
        "counts": {
            "total": len(rows),
            "open": len(open_rows),
            "open_with_pick": sum(bool(row.get("pick")) for row in open_rows),
            "open_with_probability": sum(row.get("probabilities") is not None for row in open_rows),
            "open_without_pick": [str(row.get("id")) for row in open_rows if not row.get("pick")],
            "open_without_probability": [str(row.get("id")) for row in open_rows
                                          if row.get("probabilities") is None],
            "methods": dict(sorted(Counter(str(row.get("method")) for row in open_rows).items())),
        },
        "fallback_research_required": [
            {"id": str(row.get("id")), "teams": row.get("teams"), "start": row.get("start"),
             "pick": row.get("pick"), "method": row.get("method"), "reason": row.get("reason"),
             "hltv_source": (row.get("hltv_context") or {}).get("source"),
             "attempts": row.get("attempts") or []}
            for row in gaps
        ],
        "inventory_diff_vs_previous": changed_fixtures(snapshot, previous),
        "inventory_changes_reported_by_refresh": snapshot.get("inventory_changes"),
        "fixture_conflicts": snapshot.get("fixture_conflicts"),
        "issues": snapshot.get("issues"),
        "source_checks_total": len(snapshot.get("source_checks") or []),
        "source_checks_not_ok": source_errors,
        "global_errors": global_errors,
        "rows": row_results,
        "status": "pass" if not global_errors and not any(r["errors"] for r in row_results) else "fail",
    }


def markdown(report: dict) -> str:
    counts = report["counts"]
    lines = [
        "# Fresh Hotspawn CS2 line-by-line audit — session e141a921",
        "",
        f"- Snapshot: `{report['snapshot_generated_at']}`",
        f"- Snapshot SHA-256: `{report['snapshot_sha256']}`",
        f"- Inventory parity: `{report['coverage_counts']}`; coverage `{report['coverage']}`",
        f"- Open coverage: **{counts['open_with_pick']}/{counts['open']} picks**, "
        f"**{counts['open_with_probability']}/{counts['open']} probability pairs**",
        f"- Methods: `{json.dumps(counts['methods'], sort_keys=True)}`",
        f"- Audit status: **{report['status']}**",
        "",
        "Hotspawn is used for fixture membership and lock/start times only. It is not a probability source.",
        "Rows without a pick or percentage remain explicit fallback-research/limitation items; none is filled by inference.",
        "",
        "## Fallback research required",
        "",
    ]
    gaps = report["fallback_research_required"]
    if not gaps:
        lines.append("None in this fresh capture. No supplemental gap-only source probe was needed.")
    for gap in gaps:
        lines.append(f"- `{gap['id']}` {' vs '.join(gap['teams'] or [])}: pick `{gap['pick']}`, "
                     f"method `{gap['method']}`; limitation: {gap['reason']}")
    diff = report["inventory_diff_vs_previous"]
    lines += ["", "## Inventory changes against the committed board", "",
              f"- Added IDs: {diff['added'] or 'none'}",
              f"- Removed IDs: {diff['removed'] or 'none'}",
              f"- Shared rows with start/lock/state changes: {len(diff['changed_start_lock_or_state'])}"]
    for change in diff["changed_start_lock_or_state"]:
        lines.append(f"  - `{change['id']}`: `{json.dumps(change['changes'], sort_keys=True)}`")
    lines += ["", "## Every fixture", "",
              "| Fixture | Match | State | Pick / method | Team-win probabilities | Official review links | Audit |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for row in report["rows"]:
        teams = " vs ".join(row["teams"] or [])
        probs = row["probabilities"]
        probability_text = "blank (unverified)" if probs is None else " / ".join(f"{p * 100:.1f}%" for p in probs)
        links = [f"[Hotspawn]({row['hotspawn_url']})"]
        links += [f"[External {index}]({url})" for index, url in enumerate(row["external_evidence_urls"][:4], 1)]
        result = "OK" if not row["errors"] else "; ".join(row["errors"])
        pick = f"{row['pick'] or 'blank'} / {row['method'] or 'blank'}"
        lines.append(f"| `{row['id']}` | {teams} | {row['state']} | {pick} | {probability_text} | "
                     f"{' · '.join(links)} | {result} |")
    lines += ["", "## Snapshot issues and source failures", "",
              f"- Issues: `{json.dumps(report['issues'], ensure_ascii=False)}`",
              f"- Fixture conflicts: `{json.dumps(report['fixture_conflicts'], ensure_ascii=False)}`",
              f"- Non-OK source checks: `{json.dumps(report['source_checks_not_ok'], ensure_ascii=False)}`",
              f"- Global errors: `{json.dumps(report['global_errors'], ensure_ascii=False)}`", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", default="runtime/latest.json")
    parser.add_argument("--previous", default="data/latest.json")
    parser.add_argument("--output", default="research/harvest-e141a921")
    args = parser.parse_args(argv)
    snapshot_path = Path(args.snapshot)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    snapshot_bytes = snapshot_path.read_bytes()
    snapshot = json.loads(snapshot_bytes)
    previous = json.loads(Path(args.previous).read_text())
    digest = hashlib.sha256(snapshot_bytes).hexdigest()
    report = audit(snapshot, previous, digest)
    shutil.copyfile(snapshot_path, output / "snapshot.json")
    (output / "audit.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    (output / "ROW-AUDIT.md").write_text(markdown(report))
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=1))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
