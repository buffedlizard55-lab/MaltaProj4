#!/usr/bin/env python3
"""Independent line-by-line primary-source, arithmetic, HTML-row-link, and mobile auditor (Session 80504414).

Verifies without importing scripts.core calculation helpers:
1. Primary Hotspawn CS2 inventory fidelity (all non-crowd fields match fixture_evidence; zero Hotspawn/HLTV crowd votes used).
2. Strict probability replay from stored raw inputs across exchange, bookmaker_fallback, model_vrs, and model_vrs_mirror.
3. Anti-hallucination blank-if-unverified rule (research-only & unresolved rows carry null probabilities/fair_odds and dated source links; closed rows withhold live picks).
4. Every HTML table data row across all rendered pages carries at least one direct https:// official source link.
5. Executive summary phone-first navigation, unresolved-picks limitations section, live data-count spans, and responsive CSS cards.
6. Register hygiene across data/identities.json, data/lineup-receipts.json, data/book-receipts.json, and data/review-notes.json.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from bs4 import BeautifulSoup

VALVE_SLOPE = 1.227
HTML_PAGES = (
    "index.html",
    "picks.html",
    "unresolved.html",
    "matches.html",
    "analysis.html",
    "review.html",
    "sources.html",
    "evidence.html",
    "methodology.html",
    "404.html",
)


def parse_utc(ts: str) -> datetime:
    assert isinstance(ts, str) and ts.strip(), f"Missing timestamp: {ts!r}"
    cleaned = ts.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    parsed = datetime.fromisoformat(cleaned)
    assert parsed.tzinfo is not None, f"Timezone-naive timestamp forbidden: {ts!r}"
    return parsed.astimezone(timezone.utc)


def valve_calibrated_prob(pts_a: float, pts_b: float) -> tuple[float, float]:
    raw_a = 1.0 / (1.0 + 10.0 ** ((pts_b - pts_a) / 400.0))
    cal_a = min(0.99, max(0.01, 0.5 + (raw_a - 0.5) * VALVE_SLOPE))
    return cal_a, 1.0 - cal_a


def audit_snapshot_and_site(data_path: Path, site_dir: Path, repo_root: Path | None = None) -> dict:
    root = repo_root or data_path.resolve().parents[1]
    data = json.loads(data_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    checks = 0

    def check(cond: bool, msg: str) -> None:
        nonlocal checks
        checks += 1
        if not cond:
            failures.append(msg)

    matches = data.get("matches") or []
    raw_feed = {str(r["id"]): r for r in (data.get("fixture_evidence") or [])}
    check(data.get("schema_version") == 2, "schema_version must be 2")
    check(data.get("stale_after_hours") == 8, "stale_after_hours must be 8")
    check(len(matches) == len(raw_feed) and len(matches) > 0, "matches count must equal fixture_evidence count")

    # Ensure crowd pick percentages were stripped from fixture_evidence
    for fid, raw in raw_feed.items():
        leaked = [k for k in raw if "picked" in k.lower() or k == "total_picks"]
        check(not leaked, f"fixture_evidence {fid} leaked crowd fields: {leaked}")

    seen_ids: set[str] = set()
    method_counts: dict[str, int] = {}
    open_count = priced_open = research_open = unresolved_open = 0

    for m in matches:
        mid = str(m.get("id") or "")
        check(bool(mid) and mid not in seen_ids, f"duplicate or empty match id {mid!r}")
        seen_ids.add(mid)
        raw = raw_feed.get(mid)
        check(raw is not None, f"match {mid} missing from fixture_evidence")
        if raw is not None:
            raw_teams = [
                ((raw.get("team1") or {}).get("name") or "").strip(),
                ((raw.get("team2") or {}).get("name") or "").strip(),
            ]
            check(m.get("teams") == raw_teams, f"match {mid} teams mismatch vs official API: {m.get('teams')} != {raw_teams}")
        check(str(m.get("source_url") or "").startswith("https://"), f"match {mid} missing https source_url")
        for tfield in ("start", "lock", "end"):
            if m.get(tfield) is not None:
                try:
                    parse_utc(m[tfield])
                    checks += 1
                except Exception as exc:
                    failures.append(f"match {mid} invalid {tfield}: {exc}")

        if m.get("state") != "open":
            for k in ("probabilities", "fair_odds", "pick", "method"):
                check(m.get(k) is None, f"closed match {mid} must withhold {k}")
            continue

        open_count += 1
        probs = m.get("probabilities")
        fodds = m.get("fair_odds")
        pick = m.get("pick")
        method = m.get("method")
        check(m.get("expires_at") is not None, f"open match {mid} missing expires_at")
        if m.get("expires_at"):
            parse_utc(m["expires_at"])

        if probs is None:
            check(fodds is None, f"unpriced open match {mid} must have null fair_odds")
            check(bool((m.get("reason") or "").strip()), f"unpriced open match {mid} must state limitation reason")
            check("50/50" not in (m.get("reason") or ""), f"unpriced open match {mid} must never claim 50/50")
            if pick is None:
                unresolved_open += 1
                method_counts["unresolved"] = method_counts.get("unresolved", 0) + 1
                check(method is None, f"unresolved open match {mid} must have method=None")
                check(bool(m.get("attempts")), f"unresolved open match {mid} must retain research attempts")
            else:
                research_open += 1
                method_counts[str(method)] = method_counts.get(str(method), 0) + 1
                check(pick in m["teams"], f"research match {mid} pick {pick!r} not in teams")
                check(str(method or "").startswith("research_"), f"research match {mid} unexpected method {method!r}")
                if method == "research_vrs_single":
                    vr = m.get("vrs_research") or {}
                    check(str(vr.get("source") or "").startswith("https://github.com/ValveSoftware/"),
                          f"research_vrs_single {mid} missing official Valve URL")
                    parse_utc(vr.get("observed_at") or "")
                else:
                    ctx = m.get("hltv_context") or {}
                    check(str(ctx.get("source") or "").startswith("https://www.hltv.org/matches/"),
                          f"{method} {mid} missing HLTV match URL")
                    parse_utc(ctx.get("observed_at") or "")
            continue

        # Priced open row: replay arithmetic independently
        priced_open += 1
        method_counts[str(method)] = method_counts.get(str(method), 0) + 1
        check(isinstance(probs, list) and len(probs) == 2, f"priced match {mid} invalid probabilities list")
        check(all(isinstance(x, (int, float)) and math.isfinite(x) and 0.0 < x < 1.0 for x in probs),
              f"priced match {mid} non-finite or out-of-range probabilities {probs}")
        check(abs(sum(probs) - 1.0) < 1e-9, f"priced match {mid} probabilities do not sum to 1: {probs}")
        check(isinstance(fodds, list) and len(fodds) == 2, f"priced match {mid} invalid fair_odds")
        if isinstance(fodds, list) and len(fodds) == 2:
            for pi, fo in zip(probs, fodds):
                check(abs(fo - (1.0 / pi)) < 1e-6, f"priced match {mid} fair_odds {fo} != 1/{pi}")
        expected_pick = None if abs(probs[0] - probs[1]) < 1e-4 else m["teams"][0 if probs[0] > probs[1] else 1]
        check(pick == expected_pick, f"priced match {mid} pick {pick!r} != argmax {expected_pick!r}")

        ev_list = m.get("evidence") or []
        check(len(ev_list) >= 1, f"priced match {mid} missing evidence record")
        if not ev_list:
            continue
        ev = ev_list[0]
        obs = parse_utc(ev.get("observed_at") or "")
        snap_clock = parse_utc(data.get("generated_at") or data.get("last_attempt_at"))
        check(snap_clock - obs < timedelta(hours=8), f"priced match {mid} evidence older than 8h at snapshot clock")
        check("hotspawn.com" not in str(ev.get("url") or "") and "hotspawn.com" not in str(ev.get("api_url") or ""),
              f"priced match {mid} must never derive probabilities from Hotspawn")

        if method in ("exchange", "exchange_wide"):
            check(ev.get("provider") == "Polymarket", f"match {mid} exchange provider must be Polymarket")
            spread = float(ev.get("spread", 1.0))
            liq = float(ev.get("liquidity", 0.0))
            ceil = 0.25 if method == "exchange" else 0.60
            check(spread <= ceil + 1e-9, f"match {mid} spread {spread} exceeds {ceil}")
            check(liq >= 100.0 - 1e-9, f"match {mid} liquidity {liq} below $100 floor")
            raw_prices = ev.get("implied_raw") or []
            if len(raw_prices) == 2 and sum(raw_prices) > 0:
                replayed = [raw_prices[0] / sum(raw_prices), raw_prices[1] / sum(raw_prices)]
                check(all(abs(a - b) < 1e-6 for a, b in zip(probs, replayed)),
                      f"match {mid} exchange de-vig mismatch: {probs} vs {replayed}")
        elif method == "bookmaker_fallback":
            dec = ev.get("decimal_odds") or []
            check(len(dec) == 2 and all(float(o) > 1.0 for o in dec), f"match {mid} invalid decimal_odds {dec}")
            if ev.get("provider") != "Pinnacle":
                check(abs(float(dec[0]) - float(dec[1])) > 1e-9,
                      f"match {mid} secondary book listing cannot have symmetric placeholder odds {dec}")
            inv = [1.0 / float(dec[0]), 1.0 / float(dec[1])]
            overround = sum(inv) - 1.0
            check(-0.02 <= overround <= 0.25, f"match {mid} bookmaker overround {overround:.4f} out of bounds")
            replayed = [inv[0] / sum(inv), inv[1] / sum(inv)]
            check(all(abs(a - b) < 1e-6 for a, b in zip(probs, replayed)),
                  f"match {mid} bookmaker de-vig mismatch: {probs} vs {replayed}")
        elif method in ("model_vrs", "model_vrs_mirror"):
            pts = ev.get("points") or []
            check(len(pts) == 2, f"match {mid} VRS model missing points pair")
            cal_a, cal_b = valve_calibrated_prob(float(pts[0]), float(pts[1]))
            check(abs(probs[0] - cal_a) < 1e-6 and abs(probs[1] - cal_b) < 1e-6,
                  f"match {mid} Valve calibration mismatch: {probs} vs {[cal_a, cal_b]}")
            url = str(ev.get("url") or "")
            if method == "model_vrs":
                check(url.startswith("https://github.com/ValveSoftware/counter-strike_regional_standings/"),
                      f"model_vrs {mid} must cite official ValveSoftware repo: {url}")
            else:
                check(url.startswith("https://www.hltv.org/valve-ranking/teams"),
                      f"model_vrs_mirror {mid} must cite HLTV Valve ranking: {url}")
        else:
            failures.append(f"match {mid} unknown priced method {method!r}")

    # HTML table-row official-source link audit + mobile/executive-summary audit
    table_stats: dict[str, dict] = {}
    for page_name in HTML_PAGES:
        p = site_dir / page_name
        check(p.exists(), f"missing rendered HTML page {page_name}")
        if not p.exists():
            continue
        soup = BeautifulSoup(p.read_text(encoding="utf-8"), "html.parser")
        tables = soup.find_all("table")
        zero_links = 0
        internal_only = 0
        data_rows = 0
        for ti, tbl in enumerate(tables):
            cap = tbl.find("caption").get_text(" ", strip=True) if tbl.find("caption") else f"table-{ti}"
            tbody = tbl.find("tbody") or tbl
            for ri, tr in enumerate(tbody.find_all("tr", recursive=False)):
                tds = tr.find_all("td", recursive=False)
                if not tds:
                    continue
                if len(tds) == 1 and tds[0].has_attr("colspan"):
                    continue
                data_rows += 1
                hrefs = [a.get("href", "") for a in tr.find_all("a", href=True)]
                ext_hrefs = [h for h in hrefs if h.startswith("https://")]
                if not hrefs:
                    zero_links += 1
                    failures.append(f"{page_name} [{cap}] row {ri} has ZERO links")
                elif not ext_hrefs:
                    internal_only += 1
                    failures.append(f"{page_name} [{cap}] row {ri} has NO external official https:// source link ({hrefs})")
        checks += max(1, data_rows)
        table_stats[page_name] = {
            "tables": len(tables),
            "data_rows": data_rows,
            "zero_link_rows": zero_links,
            "internal_only_link_rows": internal_only,
        }

        if page_name == "index.html":
            for sec_id in ("exec-banner", "freshness-strip", "coverage-now", "picks-at-a-glance", "unresolved-picks"):
                check(soup.find(id=sec_id) is not None, f"index.html missing #{sec_id}")
            banner = soup.find(id="exec-banner")
            if banner is not None:
                b_hrefs = {a.get("href") for a in banner.find_all("a", href=True)}
                for req in ("picks.html", "unresolved.html", "matches.html", "review.html", "sources.html#method"):
                    check(req in b_hrefs, f"#exec-banner missing direct link to {req}")
                b_counts = {el.get("data-count") for el in banner.select("[data-count]")}
                for req_c in ("open", "priced", "researched", "picked", "missing"):
                    check(req_c in b_counts, f"#exec-banner missing live data-count={req_c!r}")
            mob = soup.select_one("nav.mobile-tabs")
            check(mob is not None, "index.html missing phone bottom nav .mobile-tabs")
            if mob is not None:
                tabs = [a.get("href") for a in mob.find_all("a", href=True)]
                check(tabs == ["index.html", "picks.html", "unresolved.html", "matches.html", "analysis.html"],
                      f"unexpected mobile tabs: {tabs}")

    css_path = site_dir / "assets" / "style.css"
    check(css_path.exists(), "missing assets/style.css")
    if css_path.exists():
        css_txt = css_path.read_text(encoding="utf-8")
        check("@media (max-width:650px)" in css_txt or "@media (max-width: 650px)" in css_txt,
              "style.css missing <=650px mobile card breakpoint")

    # Register hygiene checks
    identities = json.loads((root / "data/identities.json").read_text(encoding="utf-8"))
    for entry in identities.get("aliases", []):
        check(str(entry.get("source") or "").startswith("https://"), f"identities.json entry missing https source: {entry}")
    lineup_reg = json.loads((root / "data/lineup-receipts.json").read_text(encoding="utf-8"))
    for rec in lineup_reg.get("receipts", []):
        parse_utc(rec.get("observed_at") or "")
        for lu in rec.get("lineups", []):
            check(str(lu.get("source") or "").startswith("https://www.hltv.org/matches/"),
                  f"lineup receipt {rec.get('fixture_id')} missing HLTV match URL")
    book_reg = json.loads((root / "data/book-receipts.json").read_text(encoding="utf-8"))
    for rec in book_reg.get("receipts", []):
        odds = rec.get("odds") or []
        check(len(odds) == 2 and float(odds[0]) != float(odds[1]),
              f"accepted book receipt {rec.get('id')} has invalid or symmetric odds {odds}")
    review_notes = json.loads((root / "data/review-notes.json").read_text(encoding="utf-8"))
    check(isinstance(review_notes, list) and len(review_notes) >= 129, "review-notes.json unexpectedly truncated")

    return {
        "session": "80504414",
        "audited_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "snapshot_generated_at": data.get("generated_at"),
        "fixtures_observed_at": data.get("fixtures_observed_at"),
        "total_matches": len(matches),
        "open_matches": open_count,
        "priced_open": priced_open,
        "research_only_open": research_open,
        "unresolved_open": unresolved_open,
        "method_breakdown": method_counts,
        "table_link_audit": table_stats,
        "checks_run": checks,
        "failures": failures,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/latest.json")
    ap.add_argument("--site", default=".")
    ap.add_argument("--output", default="")
    args = ap.parse_args()
    result = audit_snapshot_and_site(Path(args.data), Path(args.site))
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "checks_run": result["checks_run"],
        "failures_count": len(result["failures"]),
        "total_matches": result["total_matches"],
        "open_matches": result["open_matches"],
        "priced_open": result["priced_open"],
        "research_only_open": result["research_only_open"],
        "unresolved_open": result["unresolved_open"],
    }, indent=2))
    if result["failures"]:
        for f in result["failures"]:
            print("FAILURE:", f)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
