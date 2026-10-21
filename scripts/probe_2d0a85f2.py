"""Independent open-board audit for session 2d0a85f2.

Reads a snapshot produced by the *unmodified* ``scripts.refresh`` (no network
calls of its own) and writes two artifacts:

* ``board.json`` -- one entry per Hotspawn CS2 record in start order with every
  field a reviewer needs to check the row line by line against an official
  source: the fixture identity, its state, the pick, both probabilities, our
  fair decimal prices, the method tier, every evidence URL with its observation
  and update timestamps, the expiry, the published limitation text and the
  rejected-attempt ledger.
* ``board.md`` -- the same rows as a readable table plus the explicit gap lists
  (open rows with no pick, open rows with a pick but no percentage) and the
  snapshot-level coverage / source-check summary.

Nothing is inferred here. A field that the snapshot does not carry is written as
``null`` / blank, so an unverified value can never be confused with a verified
one. This probe deliberately does not reuse the pick tiers: it only reports what
the collector already stored, so it can contradict the collector.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _evidence_urls(ev: Any) -> list[dict[str, Any]]:
    """Compact, replayable view of every evidence entry stored on a row."""
    out: list[dict[str, Any]] = []
    for item in ev or []:
        if not isinstance(item, dict):
            continue
        raw = item.get("raw") if isinstance(item.get("raw"), dict) else {}
        out.append({
            "provider": item.get("provider"),
            "tier": item.get("tier"),
            "id": item.get("id"),
            "url": item.get("url"),
            "api_url": item.get("api_url"),
            "observed_at": item.get("observed_at"),
            "updated_at": item.get("updated_at"),
            "probabilities": item.get("probabilities"),
            "spread": item.get("spread"),
            "liquidity": item.get("liquidity"),
            "warning": item.get("warning"),
            "source_teams": item.get("source_teams"),
            "start": item.get("start"),
            "raw_question": raw.get("question"),
            "raw_outcomes": raw.get("outcomes"),
            "raw_outcome_prices": raw.get("outcomePrices"),
            "raw_game_start": raw.get("gameStartTime") or raw.get("eventStartTime"),
            "raw_active": raw.get("active"),
            "raw_closed": raw.get("closed"),
            "raw_accepting": raw.get("acceptingOrders"),
            "identity_sources": [
                (s.get("url") if isinstance(s, dict) else s)
                for s in (item.get("identity_sources") or [])
            ],
            "receipt_urls": [
                (r.get("url") if isinstance(r, dict) else r)
                for r in (item.get("source_receipts") or [])
            ],
        })
    return out


def _attempts(att: Any) -> list[dict[str, Any]]:
    """The rejected-tier ledger, compacted to what a reviewer must check."""
    out: list[dict[str, Any]] = []
    for item in att or []:
        if not isinstance(item, dict):
            continue
        out.append({
            "tier": item.get("tier"),
            "provider": item.get("provider"),
            "status": item.get("status"),
            "reason": item.get("reason"),
            "url": item.get("url"),
            "checked_at": item.get("checked_at"),
        })
    return out


def _start_key(row: dict[str, Any]) -> str:
    return row.get("start") or ""


def build(snapshot: dict[str, Any]) -> dict[str, Any]:
    matches = snapshot.get("matches") or []
    rows: list[dict[str, Any]] = []
    for row in sorted(matches, key=_start_key):
        ctx = row.get("hltv_context") or {}
        rows.append({
            "id": row.get("id"),
            "teams": row.get("teams"),
            "team_ids": row.get("team_ids"),
            "competition": row.get("competition"),
            "tier": row.get("tier"),
            "best_of": row.get("best_of"),
            "start": row.get("start"),
            "lock": row.get("lock"),
            "source_status": row.get("source_status"),
            "state": row.get("state"),
            "pick": row.get("pick"),
            "probabilities": row.get("probabilities"),
            "fair_odds": row.get("fair_odds"),
            "method": row.get("method"),
            "expires_at": row.get("expires_at"),
            "reason": row.get("reason"),
            "flags": row.get("flags"),
            "fixture_source_url": row.get("source_url"),
            "feed_url": row.get("feed_url"),
            "hltv_source": ctx.get("source"),
            "hltv_match_id": ctx.get("match_id"),
            "hltv_ranks": ctx.get("ranks"),
            "model_check": row.get("model_check"),
            "evidence": _evidence_urls(row.get("evidence")),
            "attempts": _attempts(row.get("attempts")),
        })

    open_rows = [r for r in rows if r["state"] == "open"]
    no_pick = [r for r in open_rows if not r["pick"]]
    no_probability = [r for r in open_rows if r["pick"] and r["probabilities"] is None]
    expired_open = [
        r for r in open_rows
        if r["expires_at"] and r["expires_at"] <= snapshot.get("generated_at")
    ]
    missing_source_link = [
        r for r in rows
        if r["state"] == "open" and not any(e.get("url") or e.get("api_url") for e in r["evidence"])
        and r["method"] not in (None, "")
    ]

    return {
        "generated_now_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "snapshot_generated_at": snapshot.get("generated_at"),
        "fixtures_observed_at": snapshot.get("fixtures_observed_at"),
        "refresh_started_at": snapshot.get("refresh_started_at"),
        "coverage": snapshot.get("coverage"),
        "coverage_counts": snapshot.get("coverage_counts"),
        "stale_after_hours": snapshot.get("stale_after_hours"),
        "totals": {
            "records": len(rows),
            "open": len(open_rows),
            "not_open": sum(1 for r in rows if r["state"] != "open"),
            "open_with_pick": sum(1 for r in open_rows if r["pick"]),
            "open_with_percentage": sum(1 for r in open_rows if r["probabilities"] is not None),
            "open_no_pick": len(no_pick),
            "open_pick_no_percentage": len(no_probability),
            "open_expired": len(expired_open),
            "open_priced_without_source_link": len(missing_source_link),
        },
        "method_counts": dict(Counter(str(r["method"]) for r in open_rows)),
        "gap_ids": {
            "no_pick": [r["id"] for r in no_pick],
            "pick_without_percentage": [r["id"] for r in no_probability],
            "expired_while_open": [r["id"] for r in expired_open],
            "priced_without_source_link": [r["id"] for r in missing_source_link],
        },
        "gaps": no_pick + no_probability,
        "issues": snapshot.get("issues"),
        "fixture_conflicts": snapshot.get("fixture_conflicts"),
        "inventory_changes": snapshot.get("inventory_changes"),
        "source_checks": [
            {k: c.get(k) for k in ("name", "url", "status", "http_status", "observed_at", "cache_status", "bytes", "sha256")}
            for c in (snapshot.get("source_checks") or [])
        ],
        "rows": rows,
    }


def _md(audit: dict[str, Any]) -> str:
    t = audit["totals"]
    lines = [
        "# Independent open-board audit (session 2d0a85f2)",
        "",
        f"- Snapshot generated: `{audit['snapshot_generated_at']}`",
        f"- Fixtures observed: `{audit['fixtures_observed_at']}`",
        f"- Probe run: `{audit['generated_now_utc']}`",
        f"- Coverage: `{audit['coverage']}` counts `{json.dumps(audit['coverage_counts'], sort_keys=True)}`",
        "",
        "## Totals",
        "",
        "| Measure | Count |",
        "| --- | --- |",
        f"| Hotspawn CS2 records | {t['records']} |",
        f"| Open | {t['open']} |",
        f"| Not open | {t['not_open']} |",
        f"| Open with a pick | {t['open_with_pick']} |",
        f"| Open with a published percentage | {t['open_with_percentage']} |",
        f"| **Open with NO pick** | **{t['open_no_pick']}** |",
        f"| **Open with a pick but NO percentage** | **{t['open_pick_no_percentage']}** |",
        f"| Open whose evidence already expired | {t['open_expired']} |",
        f"| Open priced rows with no evidence link | {t['open_priced_without_source_link']} |",
        "",
        f"Method mix on open rows: `{json.dumps(audit['method_counts'], sort_keys=True)}`",
        "",
        "## Every open fixture, in start order",
        "",
        "| Start (UTC) | ID | Match | Competition | Pick | P(team1) | P(team2) | Method | Evidence | Expires (UTC) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in audit["rows"]:
        if r["state"] != "open":
            continue
        probs = r["probabilities"] or [None, None]
        p1 = "" if probs[0] is None else f"{probs[0] * 100:.1f}%"
        p2 = "" if (len(probs) < 2 or probs[1] is None) else f"{probs[1] * 100:.1f}%"
        teams = r["teams"] or []
        match = f"{teams[0] if teams else '?'} vs {teams[1] if len(teams) > 1 else '?'}"
        ev = r["evidence"][0] if r["evidence"] else {}
        ev_txt = ev.get("url") or ev.get("api_url") or "(none)"
        lines.append(
            "| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
                r["start"], r["id"], match, r["competition"] or "",
                r["pick"] or "**NONE**", p1 or "**blank**", p2 or "**blank**",
                r["method"] or "-", ev_txt, r["expires_at"] or "-",
            )
        )

    if audit["gaps"]:
        lines += ["", "## Gap detail (rows with no pick, or a pick with no percentage)", ""]
        for r in audit["gaps"]:
            teams = r["teams"] or []
            lines += [
                f"### {r['id']} — {teams[0] if teams else '?'} vs {teams[1] if len(teams) > 1 else '?'}",
                "",
                f"- Competition: {r['competition']} (tier `{r['tier']}`)",
                f"- Start: `{r['start']}`  Lock: `{r['lock']}`  State: `{r['state']}`",
                f"- Pick: `{r['pick']}`  Probabilities: `{json.dumps(r['probabilities'])}`  Method: `{r['method']}`",
                f"- Hotspawn fixture page: {r['fixture_source_url']}",
                f"- HLTV context source: {r['hltv_source']}",
                f"- Published limitation/reason: {r['reason']}",
                f"- Flags: {json.dumps(r['flags'], ensure_ascii=False)}",
                "- Attempt ledger:",
            ]
            for a in r["attempts"] or [{"tier": "(none recorded)"}]:
                lines.append(
                    f"  - tier `{a.get('tier')}` status `{a.get('status')}` — {a.get('reason')} ({a.get('url')})"
                )
            if r["evidence"]:
                lines.append("- Evidence:")
                for e in r["evidence"]:
                    lines.append(
                        f"  - {e.get('provider')} tier `{e.get('tier')}` {e.get('url') or e.get('api_url')}"
                        f" observed `{e.get('observed_at')}` updated `{e.get('updated_at')}`"
                    )
            lines.append("")
    else:
        lines += ["", "## Gap detail", "", "No open fixture is missing a pick or a percentage in this snapshot.", ""]

    lines += ["", "## Snapshot-level source checks", "", "| Source | Status | HTTP | Observed (UTC) | Bytes |", "| --- | --- | --- | --- | --- |"]
    for c in audit["source_checks"]:
        lines.append(
            f"| {c.get('name')} | {c.get('status')} | {c.get('http_status')} | {c.get('observed_at')} | {c.get('bytes')} |"
        )
    lines += ["", "## Snapshot issues", ""]
    for i in audit["issues"] or []:
        lines.append(f"- `{i.get('code')}` {i.get('message')} ({i.get('source')})")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--output", required=True, help="board.json path")
    parser.add_argument("--markdown", help="board.md path (default: alongside --output)")
    args = parser.parse_args()

    snapshot = json.loads(Path(args.snapshot).read_text())
    audit = build(snapshot)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n")
    md_path = Path(args.markdown) if args.markdown else out.with_suffix(".md")
    md_path.write_text(_md(audit))
    t = audit["totals"]
    print(
        "records=%d open=%d with_pick=%d with_pct=%d NO_PICK=%s PICK_NO_PCT=%s expired_open=%d no_link=%d"
        % (
            t["records"], t["open"], t["open_with_pick"], t["open_with_percentage"],
            ",".join(audit["gap_ids"]["no_pick"]) or "-",
            ",".join(audit["gap_ids"]["pick_without_percentage"]) or "-",
            t["open_expired"], t["open_priced_without_source_link"],
        )
    )


if __name__ == "__main__":
    main()
