"""Live multi-source audit and primary-evidence harvest for session 7271c5d5.

Executed on the GitHub Actions Ubuntu runner (.github/workflows/harvest-7271c5d5.yml)
with standard outbound HTTPS only (zero access-control bypasses, zero crowd-vote
inputs). Writes compact, SHA-256-stamped receipts and a full line-by-line audit
of every Hotspawn CS2 row to ``research/harvest-7271c5d5/``.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import books, core, hltv, vrs  # noqa: E402

OUT = ROOT / "research" / "harvest-7271c5d5"
UA = "Mozilla/5.0 (X11; Linux x86_64) CS2ScoutAudit/1.0"

DIRECT_URLS: list[tuple[str, str]] = [
    ("polymarket-market-6029909", "https://gamma-api.polymarket.com/markets/6029909"),
    ("polymarket-event-k27-nexora", "https://gamma-api.polymarket.com/events?slug=cs2-nexora-k271-2026-10-22"),
    ("polymarket-market-6028868", "https://gamma-api.polymarket.com/markets/6028868"),
    ("polymarket-event-morrow-titanflow", "https://gamma-api.polymarket.com/events?slug=cs2-morrow-titanf-2026-10-22"),
    ("stavka-csgo-schedule", "https://stavka.tv/matches/csgo"),
    ("stavka-k27-nexora", "https://stavka.tv/matches/csgo/22-10-2026-nexora-k27"),
    ("stavka-morningstar-nexvoid", "https://stavka.tv/matches/csgo/22-10-2026-morningstar-nexvoid"),
    ("stavka-z10-rustec", "https://stavka.tv/matches/csgo/23-10-2026-ex-zero-tenacity-ex-rustec"),
    ("stavka-rustec-saintsinners", "https://stavka.tv/matches/csgo/23-10-2026-ex-rustec-saint-sinners"),
    ("egw-benched-titanflow", "https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn"),
    ("egw-forze-lfo10", "https://egamersworld.com/counterstrike/match/HiXMAaC8L/forze-reload-vs-_04jKZ07_4"),
    ("egw-rustec-saintsinners", "https://egamersworld.com/counterstrike/match/HiXMAaC8L/ex-rustec-vs-saint-sinners-qRkeIZuchq"),
    ("egw-flyquest-staqued", "https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3"),
    ("hltv-match-1081869", "https://www.hltv.org/matches/2399584/morningstar-vs-nexvoid-void-autumn-cup-2026"),
    ("hltv-match-1081597-slot", "https://www.hltv.org/matches/2399696/cct-challengers-lb-r3-m1-cct-2026-challengers-europe-series-8"),
    ("hltv-match-1081597-lbr2a", "https://www.hltv.org/matches/2399691/benched-gods-vs-ex-6666-cct-2026-challengers-europe-series-8"),
    ("hltv-match-1081597-lbr2b", "https://www.hltv.org/matches/2399692/noir-verse-vs-titanflow-cct-2026-challengers-europe-series-8"),
    ("hltv-event-9453", "https://www.hltv.org/events/9453/cct-2026-challengers-europe-series-8"),
    ("hltv-match-1082769", "https://www.hltv.org/matches/2399846/k27-vs-nexora-cis-lan-championship-9"),
    ("hltv-match-1079654", "https://www.hltv.org/matches/2399331/ex-zero-tenacity-vs-ex-rustec-cct-2026-europe-series-11"),
    ("hltv-match-1081149", "https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12"),
    ("hltv-match-1081150", "https://www.hltv.org/matches/2399500/ex-rustec-vs-saint-sinners-cct-2026-europe-series-12"),
    ("hltv-match-1082860", "https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026"),
    ("hltv-valve-ranking-oct20", "https://www.hltv.org/valve-ranking/teams/2026/october/20"),
    ("hltv-valve-ranking-asia-oct20", "https://www.hltv.org/valve-ranking/teams/2026/october/20/region/Asia"),
    ("picklebet-csgo-board", "https://picklebet.com/csgo/betting/"),
    ("live-pages-build-info", "https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json"),
    ("live-pages-index", "https://buffedlizard55-lab.github.io/MaltaProj4/index.html"),
    ("live-pages-picks", "https://buffedlizard55-lab.github.io/MaltaProj4/picks.html"),
    ("live-pages-unresolved", "https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html"),
    ("live-pages-review", "https://buffedlizard55-lab.github.io/MaltaProj4/review.html"),
]


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_raw(url: str, timeout: int = 25) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json,text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    t0 = utcnow()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return {
                "ok": True,
                "status": resp.status,
                "final_url": resp.geturl(),
                "content_type": resp.headers.get("Content-Type", ""),
                "retrieved_at": t0,
                "byte_length": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
                "text": body.decode("utf-8", errors="replace"),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read() if hasattr(exc, "read") else b""
        return {
            "ok": False,
            "status": exc.code,
            "final_url": url,
            "content_type": exc.headers.get("Content-Type", "") if exc.headers else "",
            "retrieved_at": t0,
            "byte_length": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "error": f"HTTP {exc.code}: {exc.reason}",
            "text": body.decode("utf-8", errors="replace")[:4000],
        }
    except Exception as exc:
        return {
            "ok": False,
            "status": None,
            "final_url": url,
            "retrieved_at": t0,
            "byte_length": 0,
            "sha256": None,
            "error": f"{type(exc).__name__}: {exc}",
            "text": "",
        }


def parse_stavka_header(html: str) -> dict[str, Any]:
    """Extract П1 / П2 odds and operator logos from a stavka.tv match page."""
    stripped = re.sub(r"<[^>]+>", " ", html)
    stripped = re.sub(r"\s+", " ", stripped)
    p1 = re.search(r"П1\s+(\d+\.\d+|--|-+)", stripped)
    p2 = re.search(r"П2\s+(\d+\.\d+|--|-+)", stripped)
    book_logos = re.findall(r'bookmaker[^"\']*["\'][^>]*alt=["\']([^"\']+)["\']|cdn\.stavka\.tv/[^"\']*bookmakers/([^"\'./]+)', html, re.I)
    operators = [a or b for a, b in book_logos if (a or b)]
    title_m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    return {
        "title": re.sub(r"\s+", " ", title_m.group(1)).strip() if title_m else None,
        "p1": p1.group(1) if p1 else None,
        "p2": p2.group(1) if p2 else None,
        "operator_hints": operators[:12],
    }


def scan_polymarket_all_cs2() -> dict[str, Any]:
    """Fetch every active Polymarket CS2 series=10310 event and extract all moneyline markets."""
    events: list[dict[str, Any]] = []
    for offset in (0, 100, 200):
        url = f"{core.GAMMA}/events?series_id=10310&active=true&closed=false&limit=100&offset={offset}"
        r = fetch_raw(url)
        if not r["ok"]:
            break
        batch = json.loads(r["text"])
        if not batch:
            break
        events.extend(batch)
        if len(batch) < 100:
            break
    markets_out = []
    for ev in events:
        for m in ev.get("markets") or []:
            if m.get("sportsMarketType") == "moneyline":
                markets_out.append({
                    "event_id": str(ev.get("id")),
                    "slug": ev.get("slug"),
                    "title": ev.get("title"),
                    "market_id": str(m.get("id")),
                    "question": m.get("question"),
                    "outcomes": json.loads(m["outcomes"]) if isinstance(m.get("outcomes"), str) else m.get("outcomes"),
                    "outcomePrices": json.loads(m["outcomePrices"]) if isinstance(m.get("outcomePrices"), str) else m.get("outcomePrices"),
                    "bestBid": m.get("bestBid"),
                    "bestAsk": m.get("bestAsk"),
                    "spread": m.get("spread"),
                    "liquidity": m.get("liquidity"),
                    "volume": m.get("volume"),
                    "gameStartTime": m.get("gameStartTime"),
                    "eventStartTime": m.get("eventStartTime") or ev.get("startTime"),
                    "updatedAt": m.get("updatedAt"),
                    "acceptingOrders": m.get("acceptingOrders"),
                })
    return {"events_count": len(events), "moneyline_markets_count": len(markets_out), "markets": markets_out}


def scan_pinnacle_all_cs2() -> dict[str, Any]:
    mu = fetch_raw(f"{core.PIN}/sports/12/matchups")
    st = fetch_raw(f"{core.PIN}/sports/12/markets/straight")
    if not (mu["ok"] and st["ok"]):
        return {"ok": False, "matchups_status": mu["status"], "straight_status": st["status"], "rows": []}
    matchups = json.loads(mu["text"])
    lines = json.loads(st["text"])
    by_id = {
        x.get("matchupId"): x for x in lines
        if x.get("type") == "moneyline" and x.get("period") == 0 and not x.get("isAlternate")
    }
    rows = []
    for m in matchups:
        if m.get("parentId") is not None or m.get("type") != "matchup":
            continue
        league = (m.get("league") or {}).get("name") or ""
        parts = m.get("participants") or []
        if len(parts) != 2:
            continue
        line = by_id.get(m.get("id"))
        rows.append({
            "id": m.get("id"),
            "league": league,
            "teams": [p.get("name") for p in parts],
            "startTime": m.get("startTime"),
            "status": m.get("status"),
            "isLive": m.get("isLive"),
            "line_status": line.get("status") if line else None,
            "cutoffAt": line.get("cutoffAt") if line else None,
            "prices": line.get("prices") if line else None,
        })
    return {"ok": True, "matchups_sha256": mu["sha256"], "straight_sha256": st["sha256"], "rows": rows}


def probe_picklebet_api(board_html: str) -> dict[str, Any]:
    """Check whether Picklebet exposes public JSON endpoints referenced in its SSR HTML/JS."""
    found_urls = sorted(set(re.findall(r"https://[a-z0-9.-]*picklebet\.com/[^\s\"'<>]+", board_html)))
    js_urls = [u for u in found_urls if u.endswith(".js")][:5]
    api_candidates = set()
    for jurl in js_urls:
        jr = fetch_raw(jurl, timeout=15)
        if jr["ok"]:
            for m in re.findall(r"https://[a-z0-9.-]*picklebet\.com/[a-zA-Z0-9/_-]+", jr["text"]):
                api_candidates.add(m)
    probe_results = {}
    for cand in sorted(api_candidates)[:10]:
        if any(k in cand.lower() for k in ("api", "sport", "event", "fixture", "betting", "graphql")):
            cr = fetch_raw(cand, timeout=12)
            probe_results[cand] = {"status": cr["status"], "content_type": cr.get("content_type"), "bytes": cr["byte_length"]}
    # Also parse every match card already embedded in SSR HTML
    text = re.sub(r"<[^>]+>", "\n", board_html)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    match_links = sorted(set(re.findall(r"https://picklebet\.com/csgo/betting/match/[^\s\"'<>]+", board_html)))
    return {
        "ssr_asset_urls_sample": found_urls[:25],
        "api_candidates": probe_results,
        "ssr_match_links": match_links,
        "ssr_lines_sample": lines[:220],
    }


def cross_match_open_fixtures(snapshot: dict[str, Any], poly: dict[str, Any], pin: dict[str, Any]) -> list[dict[str, Any]]:
    """For every open Hotspawn fixture, check ALL Polymarket & Pinnacle items even with looser start/name matching."""
    known_aliases: dict[str, set[str]] = {}
    for entry in core.IDENTITIES:
        group = {core.norm(x) for x in entry.get("names", [])}
        for n in group:
            known_aliases.setdefault(n, set()).update(group)

    def keys(team: str) -> set[str]:
        k = core.norm(team)
        out = {k} | known_aliases.get(k, set())
        if k.startswith("ex") and len(k) > 4:
            out.add(k[2:])
        if k.startswith("team") and len(k) > 6:
            out.add(k[4:])
        return out

    open_audit = []
    for m in snapshot["matches"]:
        if m["state"] != "open":
            continue
        k0, k1 = keys(m["teams"][0]), keys(m["teams"][1])
        poly_hits = []
        for pm in poly.get("markets", []):
            outs = pm.get("outcomes") or []
            if len(outs) != 2:
                continue
            o0, o1 = keys(str(outs[0])), keys(str(outs[1]))
            both = (bool(k0 & o0) and bool(k1 & o1)) or (bool(k0 & o1) and bool(k1 & o0))
            either = bool((k0 | k1) & (o0 | o1))
            if both or (either and m["probabilities"] is None):
                poly_hits.append({"match_type": "both_teams" if both else "one_team", **pm})
        pin_hits = []
        for pr in pin.get("rows", []):
            t0, t1 = keys(str(pr["teams"][0] or "")), keys(str(pr["teams"][1] or ""))
            both = (bool(k0 & t0) and bool(k1 & t1)) or (bool(k0 & t1) and bool(k1 & t0))
            either = bool((k0 | k1) & (t0 | t1))
            if both or (either and m["probabilities"] is None):
                pin_hits.append({"match_type": "both_teams" if both else "one_team", **pr})
        open_audit.append({
            "id": m["id"],
            "teams": m["teams"],
            "competition": m["competition"],
            "start": m["start"],
            "best_of": m["best_of"],
            "pick": m["pick"],
            "method": m["method"],
            "probabilities": m["probabilities"],
            "reason": m["reason"],
            "flags": m.get("flags", []),
            "polymarket_matches": poly_hits,
            "pinnacle_matches": pin_hits,
        })
    return open_audit


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    snap_path = OUT / "snapshot.json"
    audit_md = OUT / "c6-audit.md"

    refresh_run = subprocess.run(
        [sys.executable, "-m", "scripts.refresh", "--output", str(snap_path)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if refresh_run.returncode != 0:
        (OUT / "refresh-error.txt").write_text(refresh_run.stdout + "\n" + refresh_run.stderr)
        raise SystemExit(refresh_run.returncode)

    c6_run = subprocess.run(
        [sys.executable, "verification-c6/audit_snapshot.py", str(snap_path), "--output", str(audit_md)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )

    snapshot = json.loads(snap_path.read_text())
    poly = scan_polymarket_all_cs2()
    pin = scan_pinnacle_all_cs2()

    receipts = []
    picklebet_info: dict[str, Any] = {}
    for rid, url in DIRECT_URLS:
        res = fetch_raw(url)
        entry: dict[str, Any] = {
            "id": rid,
            "url": url,
            "final_url": res.get("final_url"),
            "status": res.get("status"),
            "ok": res.get("ok"),
            "retrieved_at": res.get("retrieved_at"),
            "byte_length": res.get("byte_length"),
            "sha256": res.get("sha256"),
        }
        if res.get("error"):
            entry["error"] = res["error"]
        txt = res.get("text") or ""
        if "gamma-api.polymarket.com" in url or url.endswith(".json"):
            entry["body_excerpt"] = txt[:4000]
        elif "stavka.tv/matches/csgo/" in url:
            entry["stavka_parsed"] = parse_stavka_header(txt)
        elif "stavka.tv/matches/csgo" == url:
            clean = re.sub(r"<[^>]+>", " ", txt)
            entry["stavka_schedule_excerpt"] = re.sub(r"\s+", " ", clean)[:5000]
        elif "egamersworld.com" in url:
            entry["egw_parsed_listings"] = books.parse_listing(txt)
            names = re.findall(r'"name"\s*:\s*"([^"\\]+?\s+VS\s+[^"\\]*)"', txt)
            starts = re.findall(r'"startDate"\s*:\s*"([^"\\]+)"', txt)
            entry["egw_jsonld_names"] = names[:5]
            entry["egw_jsonld_starts"] = starts[:5]
            entry["contains_1_8_placeholder"] = bool(re.search(r"1\.8\s+Make a bet\s+1\.8", re.sub(r"<[^>]+>", " ", txt)))
        elif "picklebet.com" in url and res.get("ok"):
            picklebet_info = probe_picklebet_api(txt)
            entry["picklebet_match_links_count"] = len(picklebet_info["ssr_match_links"])
        elif "www.hltv.org/matches/" in url and res.get("ok"):
            entry["hltv_parsed"] = hltv.parse_match_page(txt)
            entry["postponed_banner"] = "Match postponed" in txt
        receipts.append(entry)

    open_cross = cross_match_open_fixtures(snapshot, poly, pin)

    summary = {
        "harvested_at": utcnow(),
        "snapshot_generated_at": snapshot["generated_at"],
        "snapshot_sha256": hashlib.sha256(snap_path.read_bytes()).hexdigest(),
        "refresh_stdout": refresh_run.stdout.strip(),
        "c6_audit_returncode": c6_run.returncode,
        "c6_audit_stdout": c6_run.stdout.strip(),
        "counts": {
            "total_rows": len(snapshot["matches"]),
            "open_rows": sum(1 for m in snapshot["matches"] if m["state"] == "open"),
            "priced_open_rows": sum(1 for m in snapshot["matches"] if m["state"] == "open" and m["probabilities"] is not None),
            "research_only_open_rows": sum(1 for m in snapshot["matches"] if m["state"] == "open" and m["probabilities"] is None and m["pick"] is not None),
            "unresolved_open_rows": sum(1 for m in snapshot["matches"] if m["state"] == "open" and m["pick"] is None),
        },
        "polymarket_scan_counts": {
            "events": poly["events_count"],
            "moneyline_markets": poly["moneyline_markets_count"],
        },
        "pinnacle_scan_counts": {
            "ok": pin.get("ok"),
            "parent_matchups": len(pin.get("rows", [])),
        },
        "open_fixtures_cross_source": open_cross,
        "picklebet_probe": picklebet_info,
    }

    (OUT / "receipts.json").write_text(json.dumps({"receipts": receipts}, indent=2, ensure_ascii=False) + "\n")
    (OUT / "probe-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(summary["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
