"""Name the exact check that fails a scheduled publish on freshly refreshed data.

Session 8e4ff8d2. The scheduled publisher (``.github/workflows/pages.yml``) failed inside
``Build and independently verify every row, calculation and internal link`` on
2026-10-25T06:56Z (run 40170923727) and 2026-10-25T12:29Z (run 40193317196) after
every earlier step — including the source refresh and the quarantine — had passed. The
committed tree is green locally, so the defect only exists on a fresh snapshot, and this
session's sandbox can reach ``github.com`` / ``api.github.com`` only: it cannot download
workflow logs or artifact blobs.

This module therefore does no measurement of its own. It reads the return codes and logs
that ``.github/workflows/diag-8e4ff8d2.yml`` captured from the four commands the publisher
runs in that step, and renders them as (a) ``::error title=...::`` annotation lines, which
are readable through the check-run API, and (b) a compact markdown receipt that the
workflow commits to the branch. Nothing here writes a pick, a probability or a page.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Order matters: this is the order the publisher runs them in.
STEPS: tuple[tuple[str, str, str], ...] = (
    ("row_audit", "independent-row-audit", "verification-c6/audit_snapshot.py runtime/latest.json"),
    ("build", "build", "scripts.build --data runtime/latest.json"),
    ("validate", "validate (public/)", "scripts.validate --data runtime/latest.json"),
    ("published_audit", "published-row-audit", "verification-c6/audit_snapshot.py public/data/latest.json"),
)

# Lines that identify a failing assertion rather than incidental progress output.
FAILURE_MARKERS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^(FAIL|ERROR)[: ]"),
    re.compile(r"^\s*FAIL: "),
    re.compile(r"^(Traceback \(most recent call last\))"),
    re.compile(r"^\w*(Error|Exception)\b.*"),
    re.compile(r"^(checks|failures|verdict)\b.*", re.IGNORECASE),
    re.compile(r"^AssertionError"),
    re.compile(r"^\s+\S+:\s+.*\b(failed|missing|mismatch)\b", re.IGNORECASE),
)

MAX_MARKER_LINES = 60
MAX_TAIL_LINES = 40


def _tail(path: Path, count: int) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    return lines[-count:]


def _markers(path: Path) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    found: list[str] = []
    for line in lines:
        stripped = line.rstrip()
        if not stripped:
            continue
        if any(pattern.search(stripped) for pattern in FAILURE_MARKERS):
            found.append(stripped[:400])
    return found[:MAX_MARKER_LINES]


def collect(root: Path) -> dict:
    """Read the workflow's ``diag.env`` and per-step logs into a report dictionary."""
    codes: dict[str, int] = {}
    env_path = root / "diag.env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition("=")
            value = value.strip()
            if key.endswith("_rc") and value.lstrip("-").isdigit():
                codes[key[: -len("_rc")]] = int(value)

    steps = []
    for key, label, command in STEPS:
        log = root / f"{key}.log"
        steps.append(
            {
                "key": key,
                "label": label,
                "command": command,
                "return_code": codes.get(key),
                "failed": codes.get(key) not in (0, None),
                "markers": _markers(log),
                "tail": _tail(log, MAX_TAIL_LINES) if codes.get(key) not in (0, None) else [],
            }
        )

    snapshot = {}
    snapshot_path = root / "latest.json"
    if snapshot_path.exists():
        try:
            data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        matches = data.get("matches") or []
        open_rows = [m for m in matches if m.get("state") == "open"]
        priced = [m for m in open_rows if m.get("probabilities")]
        picked = [m for m in open_rows if m.get("pick")]
        snapshot = {
            "generated_at": data.get("generated_at"),
            "fixtures_observed_at": data.get("fixtures_observed_at"),
            "coverage": data.get("coverage"),
            "rows": len(matches),
            "open": len(open_rows),
            "picks": len(picked),
            "priced": len(priced),
            "unresolved": len([m for m in open_rows if not m.get("probabilities")]),
            "unpicked_priced": [
                {"id": m.get("id"), "teams": m.get("teams"), "method": m.get("method")}
                for m in open_rows
                if m.get("probabilities") and not m.get("pick")
            ],
        }

    return {
        "generated_at": os.environ.get("DIAG_GENERATED_AT"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "branch": os.environ.get("GITHUB_REF_NAME"),
        "commit": os.environ.get("GITHUB_SHA"),
        "steps": steps,
        "snapshot": snapshot,
        "failing": [s["label"] for s in steps if s["failed"]],
        "all_green": bool(steps) and not any(s["failed"] for s in steps),
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Publisher diagnostic — session 8e4ff8d2",
        "",
        f"- Workflow run: `{report.get('run_id')}` on `{report.get('branch')}` "
        f"(`{report.get('commit')}`)",
        f"- Captured at: `{report.get('generated_at')}`",
        f"- Commands that failed: "
        f"{', '.join('`%s`' % f for f in report['failing']) if report['failing'] else 'none'}",
        "",
        "| Command the publisher runs | Return code |",
        "| --- | --- |",
    ]
    for step in report["steps"]:
        rc = step["return_code"]
        lines.append(f"| `{step['command']}` | {'—' if rc is None else rc} |")
    lines.append("")

    snap = report.get("snapshot") or {}
    if snap:
        lines += [
            "## Fresh snapshot under test",
            "",
            f"- generated_at `{snap.get('generated_at')}`, fixtures observed `{snap.get('fixtures_observed_at')}`",
            f"- {snap.get('rows')} feed rows · **{snap.get('open')} open · {snap.get('picks')} picks · "
            f"{snap.get('priced')} with a win probability · {snap.get('unresolved')} unresolved**",
            "",
        ]
        if snap.get("unpicked_priced"):
            lines.append("Priced-but-unpicked rows (a contract violation):")
            lines.append("")
            for row in snap["unpicked_priced"]:
                lines.append(f"- `{row['id']}` {' vs '.join(row.get('teams') or [])} — method `{row.get('method')}`")
            lines.append("")

    for step in report["steps"]:
        if not step["failed"]:
            continue
        lines += ["## `%s` failed" % step["label"], ""]
        if step["markers"]:
            lines += ["Matched failure lines:", "", "```"] + step["markers"] + ["```", ""]
        if step["tail"]:
            lines += ["Last 40 lines:", "", "```"] + step["tail"] + ["```", ""]
    return "\n".join(lines).rstrip() + "\n"


def annotation_lines(report: dict) -> list[str]:
    out = [
        "diag 8e4ff8d2: "
        + (", ".join(f"{s['label']}=rc{s['return_code']}" for s in report["steps"]) or "no steps captured")
    ]
    snap = report.get("snapshot") or {}
    if snap:
        out.append(
            "snapshot %s: %s rows, %s open, %s picks, %s priced, %s unresolved"
            % (
                snap.get("generated_at"),
                snap.get("rows"),
                snap.get("open"),
                snap.get("picks"),
                snap.get("priced"),
                snap.get("unresolved"),
            )
        )
    for step in report["steps"]:
        if not step["failed"]:
            continue
        for marker in step["markers"][:25]:
            out.append(f"{step['label']}: {marker}")
        if not step["markers"]:
            for line in step["tail"][-10:]:
                out.append(f"{step['label']} tail: {line}")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", default="runtime", type=Path, help="directory the workflow wrote")
    parser.add_argument("--report", type=Path, default=Path("runtime/diag-report.md"))
    parser.add_argument("--json", type=Path, default=Path("runtime/diag-report.json"))
    parser.add_argument(
        "--annotate",
        action="store_true",
        help="write ::error title=diag:: lines to stdout (readable through the check-run API)",
    )
    args = parser.parse_args(argv)

    report = collect(args.runtime)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_markdown(report), encoding="utf-8")
    args.json.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    if args.annotate:
        for line in annotation_lines(report):
            safe = line.replace("%", "%25").replace("\r", " ").replace("\n", " ")[:900]
            print(f"::error title=diag 8e4ff8d2::{safe}")

    print(render_markdown(report))
    # Never fail on a diagnostic: the workflow decides its own outcome from the codes.
    return 0


if __name__ == "__main__":
    sys.exit(main())
