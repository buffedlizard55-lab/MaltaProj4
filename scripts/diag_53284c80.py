"""Session 53284c80: coverage ledger and unresolved-row reporter.

Reads one snapshot JSON (the collector output, never Hotspawn crowd fields) and
writes a dated coverage ledger. Used by the non-publishing harvest so the
authoring sandbox, which cannot download Actions logs, can still see:

* how many open Hotspawn CS2 rows the snapshot holds
* which of those have a pick and a two-way win probability
* which remain unresolved, with the attempts and limitation recorded on the row
* the method mix (exchange / books / originated model / research)

No probability is invented here. The reporter never talks to Hotspawn, HLTV,
Polymarket or any book.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def iso(value) -> str:
    if not value:
        return ""
    text = str(value)
    if text.endswith("Z"):
        return text
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text
    return parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def open_rows(snapshot: dict) -> list:
    return [m for m in snapshot.get("matches") or [] if m.get("state") == "open"]


def priced(row: dict) -> bool:
    probs = row.get("probabilities")
    return isinstance(probs, list) and len(probs) == 2 and all(isinstance(x, (int, float)) for x in probs)


def picked(row: dict) -> bool:
    pick = row.get("pick")
    return bool(pick) and pick in (row.get("teams") or [])


def unresolved(row: dict) -> bool:
    """An open row is unresolved when it has no directional pick or no two-way line."""
    return not picked(row) or not priced(row)


def attempts(row: dict) -> list:
    raw = row.get("attempts") or []
    if isinstance(raw, list):
        return raw
    return []


def ledger(snapshot: dict) -> dict:
    rows = snapshot.get("matches") or []
    opened = open_rows(snapshot)
    picked_rows = [m for m in opened if picked(m)]
    priced_rows = [m for m in opened if priced(m)]
    missing = [m for m in opened if unresolved(m)]
    methods = Counter(str(m.get("method") or "none") for m in opened)
    return {
        "generated_at": snapshot.get("generated_at"),
        "fixtures_observed_at": snapshot.get("fixtures_observed_at"),
        "stale_after_hours": snapshot.get("stale_after_hours"),
        "coverage": snapshot.get("coverage"),
        "coverage_counts": snapshot.get("coverage_counts"),
        "rows": len(rows),
        "open": len(opened),
        "picked": len(picked_rows),
        "priced": len(priced_rows),
        "unresolved": len(missing),
        "methods": dict(methods),
        "open_ids": [m.get("id") for m in opened],
        "unresolved_ids": [m.get("id") for m in missing],
        "unresolved_rows": [
            {
                "id": m.get("id"),
                "teams": m.get("teams"),
                "competition": m.get("competition"),
                "tier": m.get("tier"),
                "start": m.get("start"),
                "lock": m.get("lock"),
                "method": m.get("method"),
                "pick": m.get("pick"),
                "probabilities": m.get("probabilities"),
                "reason": m.get("reason"),
                "source_url": m.get("source_url"),
                "attempts": attempts(m),
                "flags": m.get("flags") or [],
            }
            for m in missing
        ],
        "open_rows": [
            {
                "id": m.get("id"),
                "teams": m.get("teams"),
                "competition": m.get("competition"),
                "tier": m.get("tier"),
                "start": m.get("start"),
                "method": m.get("method"),
                "pick": m.get("pick"),
                "probabilities": m.get("probabilities"),
                "source_url": m.get("source_url"),
                "reason": m.get("reason"),
            }
            for m in opened
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# Session 53284c80 coverage ledger",
        "",
        f"- snapshot generated: `{report.get('generated_at')}`",
        f"- fixtures observed: `{report.get('fixtures_observed_at')}`",
        f"- coverage: `{report.get('coverage')}` {report.get('coverage_counts')}",
        f"- rows: **{report['rows']}** · open: **{report['open']}** · "
        f"picks: **{report['picked']}** · win probabilities: **{report['priced']}** · "
        f"unresolved: **{report['unresolved']}**",
        f"- methods: `{report.get('methods')}`",
        "",
        "## Open matches",
        "",
        "| id | teams | pick | probabilities | method | source |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.get("open_rows") or []:
        teams = " vs ".join(row.get("teams") or [])
        probs = row.get("probabilities")
        probs_s = ""
        if isinstance(probs, list) and len(probs) == 2:
            probs_s = f"{100 * float(probs[0]):.1f}% / {100 * float(probs[1]):.1f}%"
        source = row.get("source_url") or ""
        src = f"[link]({source})" if str(source).startswith("https://") else ""
        lines.append(
            f"| {row.get('id')} | {teams} | {row.get('pick') or ''} | {probs_s} | "
            f"{row.get('method') or ''} | {src} |"
        )
    lines.extend(["", "## Unresolved picks and limitations", ""])
    missing = report.get("unresolved_rows") or []
    if not missing:
        lines.append(
            "Every open match in this snapshot has a directional pick and a two-way "
            "win probability. There is nothing to list in this section."
        )
    else:
        lines.append(
            "These open fixtures could not be resolved from the sourced ladder "
            "(exchange → HLTV → Pinnacle → wide exchange → researched books → "
            "Valve VRS model → HLTV VRS mirror → HLTV rank/form). No number was invented."
        )
        lines.append("")
        for row in missing:
            teams = " vs ".join(row.get("teams") or [])
            lines.append(f"### {row.get('id')} — {teams}")
            lines.append("")
            lines.append(f"- competition: {row.get('competition')} (tier {row.get('tier')})")
            lines.append(f"- start: `{row.get('start')}` · lock: `{row.get('lock')}`")
            lines.append(f"- reason: {row.get('reason') or '(none recorded)'}")
            source = row.get("source_url") or ""
            if str(source).startswith("https://"):
                lines.append(f"- Hotspawn fixture (inventory only): {source}")
            tried = row.get("attempts") or []
            if tried:
                lines.append("- attempted sources:")
                for item in tried:
                    if isinstance(item, dict):
                        lines.append(
                            f"  - {item.get('provider') or item.get('method') or item}: "
                            f"{item.get('url') or item.get('source') or ''} "
                            f"{item.get('detail') or item.get('reason') or ''}".rstrip()
                        )
                    else:
                        lines.append(f"  - {item}")
            else:
                lines.append("- attempted sources: none recorded on the row")
            lines.append("")
    lines.append("")
    return "\n".join(lines)


def annotate(report: dict) -> None:
    """Emit GitHub Actions annotations that GraphQL can read when logs cannot."""
    msg = (
        f"open={report['open']} picked={report['picked']} priced={report['priced']} "
        f"unresolved={report['unresolved']} methods={report.get('methods')}"
    )
    print(f"::notice title=53284c80-coverage::{msg}")
    for row in report.get("unresolved_rows") or []:
        teams = " vs ".join(row.get("teams") or [])
        print(
            f"::warning title=53284c80-unresolved-{row.get('id')}::"
            f"{row.get('id')} {teams} — {row.get('reason') or 'no reason recorded'}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--output", required=True, help="Directory for coverage.json and coverage.md")
    args = parser.parse_args(argv)
    path = Path(args.snapshot)
    if not path.is_file():
        print(f"::error title=53284c80-missing-snapshot::no snapshot at {path}")
        return 2
    snapshot = load(path)
    report = ledger(snapshot)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "coverage.json").write_text(json.dumps(report, indent=1) + "\n")
    (out / "coverage.md").write_text(markdown(report))
    annotate(report)
    print(json.dumps({k: report[k] for k in ("rows", "open", "picked", "priced", "unresolved", "methods")}, sort_keys=True))
    # Non-zero only when the snapshot file itself is unreadable. An unresolved
    # row is a published limitation, not a reporter failure.
    return 0


if __name__ == "__main__":
    sys.exit(main())
