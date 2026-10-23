"""Session 9b97d585: dated, row-by-row coverage and evidence ledger.

Run after the real refresh and quarantine steps.  This module does not collect
odds and never changes a pick.  It combines the existing independent C6 audit
with additional coverage/source checks and writes only derived review reports:

    python -m scripts.audit_9b97d585 \
        --snapshot runtime/latest.json --previous data/latest.json \
        --output research/harvest-9b97d585

The JSON and Markdown outputs distinguish an integrity failure (which exits
nonzero) from a coverage gap (an honestly unresolved open row, which remains
visible with its limitation and source attempts).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_FEED = (
    "https://phpstack-1372681-6459848.cloudwaysapps.com/"
    "api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1"
)
MARKET_METHODS = {"exchange", "exchange_wide", "bookmaker_fallback"}
MODEL_METHODS = {"model_vrs", "model_vrs_mirror"}
RESEARCH_METHODS = {"research_rank", "research_rank_single", "research_vrs_single"}


def independent_auditor():
    path = ROOT / "verification-c6" / "audit_snapshot.py"
    spec = importlib.util.spec_from_file_location("audit_snapshot_9b97d585", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def https(value):
    try:
        return urlsplit(str(value or "")).scheme == "https" and bool(urlsplit(str(value)).netloc)
    except ValueError:
        return False


def common_row_problems(match):
    """Additional invariants not used to manufacture a coverage success."""
    problems = []
    source = match.get("source_url")
    if not https(source) or urlsplit(source).hostname not in {
        "play.hotspawn.com", "www.hotspawn.com", "hotspawn.com"
    }:
        problems.append("row lacks an official Hotspawn HTTPS fixture link")
    if match.get("feed_url") != FIXTURE_FEED:
        problems.append("row lacks the exact scoped Hotspawn fixture-feed link")

    state = match.get("state")
    teams = match.get("teams") or []
    pick = match.get("pick")
    probabilities = match.get("probabilities")
    fair_odds = match.get("fair_odds")
    method = match.get("method")
    if state not in {"open", "not_open"}:
        problems.append("unknown fixture state")
    if state == "not_open" and any(value is not None for value in (pick, probabilities, fair_odds, method)):
        problems.append("not-open row carries an actionable value")
    if pick is not None and pick not in teams:
        problems.append("pick is not one of the two fixture teams")

    if probabilities is None:
        if fair_odds is not None:
            problems.append("blank probability has fair odds")
        if state == "open" and pick and method not in RESEARCH_METHODS:
            problems.append("open pick without a probability lacks a documented research method")
        if state == "open" and not pick:
            if method is not None:
                problems.append("unresolved open row has a method")
            if not match.get("reason"):
                problems.append("unresolved open row lacks a limitation")
            if not match.get("attempts"):
                problems.append("unresolved open row lacks source attempts")
        return problems

    if state != "open":
        problems.append("probability appears outside an open row")
    if not isinstance(probabilities, list) or len(probabilities) != 2:
        return problems + ["probability is not a two-way pair"]
    if any(not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 < value < 1
           for value in probabilities):
        problems.append("probability is not finite and strictly between zero and one")
    elif abs(sum(probabilities) - 1) > 1e-9:
        problems.append("probabilities do not sum to one")
    if not isinstance(fair_odds, list) or len(fair_odds) != 2:
        problems.append("fair odds are not a two-way pair")
    else:
        for probability, odds in zip(probabilities, fair_odds):
            if not isinstance(odds, (int, float)) or not math.isfinite(odds) or abs(odds - 1 / probability) > 1e-8:
                problems.append("fair odds do not equal 1 / probability")
                break
    if method not in MARKET_METHODS | MODEL_METHODS:
        problems.append("priced row has an undocumented method")
    if not match.get("evidence"):
        problems.append("priced row has no selected evidence")
    else:
        evidence = match["evidence"][0]
        if not https(evidence.get("api_url")) or not https(evidence.get("url")):
            problems.append("priced row lacks HTTPS evidence links")
    if probabilities[0] != probabilities[1]:
        expected = teams[0 if probabilities[0] > probabilities[1] else 1]
        if pick != expected:
            problems.append("pick does not follow the larger probability")
    return problems


def evidence_links(match):
    links = []
    for evidence in match.get("evidence") or []:
        for key in ("api_url", "url"):
            value = evidence.get(key)
            if value and value not in links:
                links.append(value)
    return links


def ledger_row(match, independent_problems, additional_problems):
    probabilities = match.get("probabilities")
    return {
        "id": str(match.get("id")),
        "teams": match.get("teams"),
        "competition": match.get("competition"),
        "start": match.get("start"),
        "lock": match.get("lock"),
        "state": match.get("state"),
        "pick": match.get("pick"),
        "probabilities": probabilities,
        "fair_odds": match.get("fair_odds"),
        "method": match.get("method"),
        "fixture_source": match.get("source_url"),
        "feed_source": match.get("feed_url"),
        "evidence_sources": evidence_links(match),
        "expires_at": match.get("expires_at"),
        "limitation": match.get("reason"),
        "flags": match.get("flags") or [],
        "independent_audit_problems": independent_problems,
        "additional_audit_problems": additional_problems,
        "source_attempts": (match.get("attempts") or []) if match.get("state") == "open" and (
            match.get("pick") is None or probabilities is None or match.get("method") not in MARKET_METHODS
        ) else [],
    }


def pct(values):
    if not values:
        return "blank"
    return " / ".join(f"{100 * value:.1f}%" for value in values)


def markdown_link(url, label):
    if not url:
        return "—"
    return f"[{label}]({url})"


def audit(snapshot, previous, snapshot_bytes=None):
    auditor = independent_auditor()
    independent_rows, independent_errors = auditor.inspect(snapshot)
    independent_by_id = {str(match["id"]): problems for match, problems in independent_rows}

    rows = []
    additional_errors = []
    for match in snapshot.get("matches") or []:
        problems = common_row_problems(match)
        additional_errors.extend(f"{match.get('id')}: {problem}" for problem in problems)
        rows.append(ledger_row(match, independent_by_id.get(str(match.get("id")), ["row missing from independent audit"]), problems))

    previous_by_id = {str(match.get("id")): match for match in (previous or {}).get("matches") or []}
    current_by_id = {str(match.get("id")): match for match in snapshot.get("matches") or []}
    changes = []
    for ident, match in current_by_id.items():
        old = previous_by_id.get(ident)
        if not old:
            continue
        changed = {
            field: {"previous": old.get(field), "current": match.get(field)}
            for field in ("teams", "competition", "start", "lock", "state")
            if old.get(field) != match.get(field)
        }
        if changed:
            changes.append({"id": ident, "teams": match.get("teams"), "changed": changed})

    open_rows = [row for row in rows if row["state"] == "open"]
    gaps = [row for row in open_rows if not row["pick"] or row["probabilities"] is None]
    result = {
        "schema_version": 1,
        "snapshot_sha256": hashlib.sha256(snapshot_bytes).hexdigest() if snapshot_bytes is not None else None,
        "snapshot_generated_at": snapshot.get("generated_at"),
        "fixtures_observed_at": snapshot.get("fixtures_observed_at"),
        "previous_generated_at": (previous or {}).get("generated_at"),
        "coverage": snapshot.get("coverage"),
        "coverage_counts": snapshot.get("coverage_counts"),
        "fixture_conflicts": snapshot.get("fixture_conflicts") or [],
        "inventory_changes_reported_by_refresh": snapshot.get("inventory_changes"),
        "added_vs_previous": sorted(set(current_by_id) - set(previous_by_id)),
        "removed_vs_previous": sorted(set(previous_by_id) - set(current_by_id)),
        "changed_fixture_facts_vs_previous": changes,
        "counts": {
            "fixtures": len(rows),
            "open": len(open_rows),
            "open_with_pick": sum(bool(row["pick"]) for row in open_rows),
            "open_with_probability": sum(row["probabilities"] is not None for row in open_rows),
            "open_fully_resolved": sum(bool(row["pick"]) and row["probabilities"] is not None for row in open_rows),
            "open_with_pick_but_no_probability": sum(bool(row["pick"]) and row["probabilities"] is None for row in open_rows),
            "open_without_pick": sum(not row["pick"] for row in open_rows),
            "not_open": sum(row["state"] == "not_open" for row in rows),
            "methods": dict(sorted(Counter(row["method"] or "none" for row in open_rows).items())),
        },
        "coverage_complete": not gaps,
        "coverage_gaps": gaps,
        "integrity_failures": independent_errors + additional_errors,
        "source_checks": snapshot.get("source_checks") or [],
        "issues": snapshot.get("issues") or [],
        "rows": rows,
    }
    return result


def write_reports(result, output, snapshot_bytes):
    output.mkdir(parents=True, exist_ok=True)
    (output / "snapshot.json").write_bytes(snapshot_bytes)
    (output / "audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n")

    counts = result["counts"]
    lines = [
        "# Hotspawn coverage and verification summary",
        "",
        f"- Snapshot generated: `{result['snapshot_generated_at']}`",
        f"- Fixture evidence observed: `{result['fixtures_observed_at']}`",
        f"- Snapshot SHA-256: `{result['snapshot_sha256']}`",
        f"- Three-view coverage flag: **{result['coverage']}**; counts: `{json.dumps(result['coverage_counts'])}`",
        f"- Fixtures: **{counts['fixtures']}**; open: **{counts['open']}**; with a pick: **{counts['open_with_pick']}**; with a probability: **{counts['open_with_probability']}**; fully resolved: **{counts['open_fully_resolved']}**",
        f"- Research-only picks without a percentage: **{counts['open_with_pick_but_no_probability']}**; open rows without a pick: **{counts['open_without_pick']}**",
        f"- Open-row methods: `{json.dumps(counts['methods'])}`",
        f"- Added vs previous: `{result['added_vs_previous'] or 'none'}`; removed: `{result['removed_vs_previous'] or 'none'}`",
        f"- Independent + additional integrity failures: **{len(result['integrity_failures'])}**",
        "",
        "Hotspawn is used only for fixture identity, schedule and lock state. It is not a probability source. Blank values are not replaced with guesses.",
        "",
        "## Changed fixture facts vs the previous committed snapshot",
        "",
    ]
    if result["changed_fixture_facts_vs_previous"]:
        for change in result["changed_fixture_facts_vs_previous"]:
            lines.append(f"- `{change['id']}` {' vs '.join(change['teams'] or [])}: `{json.dumps(change['changed'], ensure_ascii=False)}`")
    else:
        lines.append("- None.")
    lines += ["", "## Open-row gaps and limitations", ""]
    if not result["coverage_gaps"]:
        lines.append("No open-row coverage gaps in this dated snapshot. Later refreshes may produce gaps; those remain visible rather than being filled with invented values.")
    for row in result["coverage_gaps"]:
        lines += [
            f"### {row['id']} — {' vs '.join(row['teams'] or [])}",
            "",
            f"- Start: `{row['start']}`; pick: `{row['pick']}`; probability: `{pct(row['probabilities'])}`; method: `{row['method']}`",
            f"- Limitation: {row['limitation'] or 'See source attempts and flags.'}",
            f"- Fixture: {markdown_link(row['fixture_source'], 'Hotspawn')}; evidence: {', '.join(markdown_link(url, 'source') for url in row['evidence_sources']) or 'none accepted'}",
            "- Source attempts:",
        ]
        for attempt in row["source_attempts"]:
            lines.append(f"  - {attempt.get('provider')}: {attempt.get('status')} — {attempt.get('reason')} ({attempt.get('url')})")
        if not row["source_attempts"]:
            lines.append("  - No attempts retained; this is an integrity failure, not a resolved row.")
    if result["integrity_failures"]:
        lines += ["", "## Integrity failures", ""] + [f"- {error}" for error in result["integrity_failures"]]
    (output / "summary.md").write_text("\n".join(lines) + "\n")

    ledger = [
        "# Row-by-row source ledger",
        "",
        "Every row below is copied from the dated snapshot. Probabilities are team 1 / team 2 in the displayed team order. The independent C6 evidence replay and the additional checks must both pass; source links are supplied for manual review.",
        "",
        "| ID | State | Match / event | Start (UTC) | Pick | Probability (team 1 / team 2) | Method | Fixture source | Price/model source | Audit |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in result["rows"]:
        teams = " vs ".join(row["teams"] or [])
        match = f"{teams}<br>{row['competition'] or ''}"
        sources = "<br>".join(markdown_link(url, "evidence") for url in row["evidence_sources"]) or "—"
        problems = row["independent_audit_problems"] + row["additional_audit_problems"]
        verdict = "PASS" if not problems else "FAIL: " + "; ".join(problems)
        ledger.append(
            f"| {row['id']} | {row['state']} | {match} | {row['start']} | {row['pick'] or '—'} | {pct(row['probabilities'])} | "
            f"{row['method'] or '—'} | {markdown_link(row['fixture_source'], 'Hotspawn')}<br>{markdown_link(row['feed_source'], 'feed')} | {sources} | {verdict} |"
        )
    (output / "row-ledger.md").write_text("\n".join(ledger) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    snapshot_bytes = args.snapshot.read_bytes()
    snapshot = json.loads(snapshot_bytes)
    previous = json.loads(args.previous.read_bytes()) if args.previous and args.previous.exists() else {}
    result = audit(snapshot, previous, snapshot_bytes)
    write_reports(result, args.output, snapshot_bytes)
    print(json.dumps({"counts": result["counts"], "coverage_complete": result["coverage_complete"],
                      "integrity_failures": len(result["integrity_failures"])}, indent=1))
    return bool(result["integrity_failures"])


if __name__ == "__main__":
    raise SystemExit(main())
