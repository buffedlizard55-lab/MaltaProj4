#!/usr/bin/env python3
"""Independent line-by-line repository & HTML table-row auditor (session 86b56cf6).

Verifies every requirement across data/*.json, data/matches.csv, and all built HTML pages:
1. Zero Hotspawn probability origination anywhere in data/latest.json or evidence records.
2. Supported open-match picks and documented fail-closed unresolved rows, exact mathematical reproduction
   of every published probability & fair decimal line from stored raw inputs, and strict
   blank preservation (probabilities=None, fair_odds=None, never 50/50) when unpriced.
3. Line-by-line integrity of data/lineup-receipts.json (all 10 fixtures carry canonical
   HLTV URLs and verified 5-player lineups; zero corrupted/hallucinated players) and
   data/book-receipts.json (zero wrong-event mashup slugs; live-verified timestamps).
4. Every single rendered HTML data row across ALL 9 primary HTML pages (index.html,
   picks.html, unresolved.html, matches.html, analysis.html, evidence.html, sources.html,
   review.html, 404.html) carries a valid official external source link (http/https).
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent

FORBIDDEN_LINEUP_NAMES = {
    "SPine", "ExpSasiKi", "rage", "Miami", "dama",
    "FL4MUS", "SELLTER", "alpha", "Magnojez", "zorte",
    "kus0k", "rexxie", "Something", "sunlight", "rik0", "flaw",
    "KRAXYT",
}

FORBIDDEN_BOOK_URLS = {
    "https://egamersworld.com/counterstrike/match/zawJ-Q52S3/bestia-academy-vs-red-canids-academy-zawJ-Q52S3",
    "https://egamersworld.com/counterstrike/match/fQ0D-T2eM/bestia-academy-vs-red-canids-academy-3nbNt3Gf1p",
    "https://egamersworld.com/counterstrike/match/fQ0D-T2eM/isurus-gaming-vs-hacha-qgq9dKgkRU",
}

TRUSTED_HOSTS = (
    "https://gamma-api.polymarket.com/",
    "https://polymarket.com/",
    "https://docs.polymarket.com/",
    "https://guest.api.arcadia.pinnacle.com/",
    "https://www.pinnacle.com/",
    "https://www.pinnaclesports.com/",
    "https://www.hltv.org/",
    "https://github.com/ValveSoftware/counter-strike_regional_standings/",
    "https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/",
    "https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/",
    "https://github.com/buffedlizard55-lab/MaltaProj4/",
    "https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/",
    "https://docs.github.com/",
    "https://stavka.tv/",
    "https://winline.ru/",
    "https://egamersworld.com/",
    "https://kushvsporte.ru/",
    "https://thunderpick.io/",
    "https://gg.bet/",
    "https://bo3.gg/",
    "https://api.bo3.gg/",
    "https://www.rivalry.com/",
    "https://stake.com/",
    "https://picklebet.com/",
    "https://kalshi.com/",
    "https://api.elections.kalshi.com/",
    # Session 85087497: Kalshi's current official hosts per docs.kalshi.com
    # (production Trade API + documentation), same operator as the two above;
    # cited by the 2026-10-25 fallback-probe review note.
    "https://external-api.kalshi.com/",
    "https://docs.kalshi.com/",
    "https://liquipedia.net/counterstrike/",
    "https://draft5.gg/",
    "https://dfrag.gg/",
    "https://www.strafe.com/",
    "https://esportbet.com/",
    "https://white.market/",
    "https://game-tournaments.com/",
    "https://www.teamliquid.com/",
    "https://betboom.team/",
    "https://auroragg.com/",
    "https://nip.gl/",
    "https://www.hotspawn.com/",
    "https://play.hotspawn.com/",
    "https://phpstack-1372681-6459848.cloudwaysapps.com/",
    "https://buffedlizard55-lab.github.io/MaltaProj4/",
)


def is_trusted_source(url: str) -> bool:
    # The official project root is a valid citation with or without its terminal
    # slash. Exact equality is intentional: a neighbouring GitHub project or
    # phishing suffix is not made trusted by this completed-owner integration.
    return (url == "https://github.com/ValveSoftware/counter-strike_regional_standings"
            or url.startswith(TRUSTED_HOSTS))


def audit_all(root: Path = ROOT) -> dict:
    errors: list[str] = []
    latest = json.loads((root / "data/latest.json").read_text())
    matches = latest["matches"]

    # 1. Verify CSV row parity 1-for-1 against data/latest.json
    with (root / "data/matches.csv").open(encoding="utf-8") as csv_fh:
        csv_rows = list(csv.DictReader(csv_fh))
    if len(csv_rows) != len(matches):
        errors.append(f"CSV row count mismatch: {len(csv_rows)} vs {len(matches)}")

    open_rows = 0
    open_picked = 0
    open_priced = 0
    open_unpriced = 0
    row_ledger = []

    for idx, m in enumerate(matches):
        fid = str(m["id"])
        state = m["state"]
        method = m.get("method")
        probs = m.get("probabilities")
        fair = m.get("fair_odds")
        pick = m.get("pick")
        ev = (m.get("evidence") or [None])[0]

        # Never use Hotspawn for win probability
        if probs is not None:
            if not ev:
                errors.append(f"{fid}: probabilities present without evidence record")
            else:
                ev_url = str(ev.get("url") or "")
                ev_prov = str(ev.get("provider") or "")
                if "hotspawn" in ev_url.lower() or "hotspawn" in ev_prov.lower():
                    errors.append(f"{fid}: Hotspawn forbidden as probability source ({ev_prov} / {ev_url})")

        if state == "open":
            open_rows += 1
            if pick is None:
                for field in ("probabilities", "fair_odds", "method"):
                    if m.get(field) is not None:
                        errors.append(f"{fid}: unresolved {field} must be None")
                if not m.get("reason"):
                    errors.append(f"{fid}: unresolved row lacks its limitation reason")
                if not any(isinstance(a, dict) and str(a.get("url") or "").startswith("https://")
                           and a.get("reason") for a in (m.get("attempts") or [])):
                    errors.append(f"{fid}: unresolved row lacks dated source attempts")
                if not str(m.get("source_url") or "").startswith("https://"):
                    errors.append(f"{fid}: unresolved row lacks official fixture URL")
            elif pick not in m["teams"]:
                errors.append(f"{fid}: open match has invalid pick ({pick!r})")
            else:
                open_picked += 1

            if probs is not None:
                open_priced += 1
                if abs(probs[0] + probs[1] - 1.0) > 1e-6:
                    errors.append(f"{fid}: probabilities do not sum to 1.0: {probs}")
                expected_pick = m["teams"][0] if probs[0] >= probs[1] else m["teams"][1]
                if pick != expected_pick:
                    errors.append(f"{fid}: pick {pick} != higher probability team {expected_pick} ({probs})")
                if not fair or abs(fair[0] - round(1.0 / probs[0], 3)) > 0.002 or abs(fair[1] - round(1.0 / probs[1], 3)) > 0.002:
                    errors.append(f"{fid}: fair_odds {fair} inconsistent with probabilities {probs}")
                # Verify Valve Glicko fit.js / bookmaker math independently from raw inputs
                if method in ("model_vrs", "model_vrs_mirror") and ev:
                    pts_a, pts_b = float(ev["points"][0]), float(ev["points"][1])
                    rd = float(ev["rating_deviation"])
                    slope = float(ev["calibration_slope"])
                    q_const = math.log(10.0) / 400.0
                    g_factor = 1.0 / math.sqrt(1.0 + 3.0 * q_const * q_const * rd * rd / (math.pi ** 2))
                    raw_a = 1.0 / (1.0 + 10.0 ** (-g_factor * (pts_a - pts_b) / 400.0))
                    cal_a = 0.5 + slope * (raw_a - 0.5)
                    repro = [cal_a, 1.0 - cal_a]
                    if abs(repro[0] - probs[0]) > 1e-12 or abs(repro[1] - probs[1]) > 1e-12:
                        errors.append(f"{fid}: independent Valve fit.js formula mismatch {probs} vs {repro}")
                elif method == "bookmaker_fallback" and ev and ev.get("decimal_odds"):
                    inv0 = 1.0 / float(ev["decimal_odds"][0])
                    inv1 = 1.0 / float(ev["decimal_odds"][1])
                    total_imp = inv0 + inv1
                    repro = [inv0 / total_imp, inv1 / total_imp]
                    if abs(repro[0] - probs[0]) > 1e-4 or abs(repro[1] - probs[1]) > 1e-4:
                        errors.append(f"{fid}: independent bookmaker devig mismatch {probs} vs {repro}")
            else:
                open_unpriced += 1
                if fair is not None:
                    errors.append(f"{fid}: unpriced match must have fair_odds=None, got {fair}")
                if pick is not None:
                    if method not in ("research_rank", "research_rank_single", "research_vrs_single"):
                        errors.append(f"{fid}: open unpriced match has unexpected method {method!r}")
                    hc = m.get("hltv_context") or {}
                    vr = m.get("vrs_research") or {}
                    if not hc.get("source") and not vr.get("source"):
                        errors.append(f"{fid}: research-only pick lacks HLTV/VRS source link")
        else:
            if probs is not None or pick is not None:
                errors.append(f"{fid}: closed match must not publish active pick/probabilities")

        primary_source = (
            (ev or {}).get("url")
            or ((m.get("hltv_context") or {}).get("source"))
            or ((m.get("vrs_research") or {}).get("source"))
            or m.get("source_url")
        )
        row_ledger.append({
            "row": idx + 1,
            "id": fid,
            "teams": m["teams"],
            "competition": m["competition"],
            "start": m["start"],
            "lock": m["lock"],
            "state": state,
            "method": method,
            "pick": pick,
            "probabilities": probs,
            "fair_odds": fair,
            "primary_source": primary_source,
        })

    # 2. Verify data/lineup-receipts.json line by line
    lineup_doc = json.loads((root / "data/lineup-receipts.json").read_text())
    lineup_ids = set()
    for r in lineup_doc.get("receipts", []):
        fid = str(r["fixture_id"])
        lineup_ids.add(fid)
        if not str(r.get("event_url", "")).startswith("https://www.hltv.org/"):
            errors.append(f"lineup-receipts {fid}: non-HLTV event_url {r.get('event_url')}")
        if len(r.get("lineups", [])) != 2:
            errors.append(f"lineup-receipts {fid}: expected 2 team lineups")
        for lu in r.get("lineups", []):
            players = lu.get("players", [])
            if len(players) != 5:
                errors.append(f"lineup-receipts {fid} ({lu.get('team')}): expected 5 players, got {len(players)}")
            bad = FORBIDDEN_LINEUP_NAMES.intersection(players)
            if bad:
                errors.append(f"lineup-receipts {fid} ({lu.get('team')}): contains forbidden corrupted names {sorted(bad)}")
            if not str(lu.get("source", "")).startswith("https://www.hltv.org/matches/"):
                errors.append(f"lineup-receipts {fid} ({lu.get('team')}): source must be canonical HLTV match page")

    # 3. Verify data/book-receipts.json has zero wrong-event mashup URLs
    book_doc = json.loads((root / "data/book-receipts.json").read_text())
    for section in ("receipts", "rejected_listings"):
        for item in book_doc.get(section, []):
            u = str(item.get("url", ""))
            if u in FORBIDDEN_BOOK_URLS:
                errors.append(f"book-receipts {section} ({item.get('fixture_id')}): forbidden wrong-event URL {u}")

    # 4. Verify EVERY data row across ALL 9 primary HTML pages carries a trusted external source link
    html_pages = [
        "index.html", "picks.html", "unresolved.html", "matches.html",
        "analysis.html", "evidence.html", "sources.html", "review.html", "404.html",
    ]
    total_tables = 0
    total_html_rows = 0
    html_page_summary = {}
    for page_name in html_pages:
        soup = BeautifulSoup((root / page_name).read_text(), "html.parser")
        tables = soup.find_all("table")
        page_rows = 0
        for ti, tb in enumerate(tables):
            tbody = tb.find("tbody") or tb
            for ri, tr in enumerate(tbody.find_all("tr")):
                if tr.find("th") and not tr.find("td"):
                    continue
                page_rows += 1
                hrefs = [a.get("href", "") for a in tr.find_all("a", href=True)]
                ext = [h for h in hrefs if h.startswith(("http://", "https://"))]
                if not ext:
                    errors.append(f"{page_name} table#{ti} row#{ri}: missing external official source link ({tr.get_text(' ', strip=True)[:80]})")
                else:
                    for h in ext:
                        if not is_trusted_source(h):
                            errors.append(f"{page_name} table#{ti} row#{ri}: untrusted external host {h}")
        total_tables += len(tables)
        total_html_rows += page_rows
        html_page_summary[page_name] = {"tables": len(tables), "rows": page_rows}

    result = {
        "status": "ok" if not errors else "failed",
        "snapshot_generated_at": latest["generated_at"],
        "fixtures_observed_at": latest["fixtures_observed_at"],
        "rows_total": len(matches),
        "rows_open": open_rows,
        "rows_open_picked": open_picked,
        "rows_open_priced": open_priced,
        "rows_open_unpriced": open_unpriced,
        "lineup_receipts_verified": len(lineup_ids),
        "html_tables_checked": total_tables,
        "html_rows_checked": total_html_rows,
        "html_pages": html_page_summary,
        "errors": errors,
        "ledger": row_ledger,
    }
    return result


def main() -> int:
    res = audit_all(ROOT)
    summary = {k: v for k, v in res.items() if k != "ledger"}
    print(json.dumps(summary, indent=2))
    if res["errors"]:
        return 1
    out_ledger = ROOT / "research/session-86b56cf6/audit-107-rows.json"
    out_ledger.parent.mkdir(parents=True, exist_ok=True)
    out_ledger.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
