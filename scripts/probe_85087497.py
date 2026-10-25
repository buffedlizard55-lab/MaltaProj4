"""Session 85087497 probe: can a keyless public source price the fixtures the
existing ladder leaves without a percentage?

Candidates probed (read-only, unauthenticated, nothing bypassed):

* Kalshi's public Trade API market data (docs.kalshi.com: market-data endpoints
  need no API key). We list series, keep any whose title/ticker identifies
  Counter-Strike/CS2, list its open markets, and test each unpriced open
  Hotspawn fixture for an exact two-team match in the market title/subtitle.
  A "possible" row is a lead for a later typed adapter, never a price: this
  probe publishes nothing and writes only its dated report.
* HLTV's dated world-ranking page reachability from the runner (the ranking
  order rung already uses HLTV fixture/team pages; this records whether the
  standalone dated ranking view is readable for a future adapter).

Output: JSON with per-request receipts (url, http status, byte count, sha256,
retrieved_at) so every claim in the session report replays from the report.
Usage: python -m scripts.probe_85087497 --snapshot runtime/latest.json --output research/harvest-85087497/probe.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

UA = {"User-Agent": "Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)"}
KALSHI = "https://external-api.kalshi.com/trade-api/v2"


def market_team(market):
    """The single team a Kalshi "<Team> wins" market is about, or None."""
    for field in ("yes_sub_title", "subtitle", "title"):
        value = market.get(field)
        if isinstance(value, str) and value.strip():
            label = value.strip()
            if label.lower().endswith(" wins"):
                label = label[: -len(" wins")].strip()
            if label:
                return label
    return None


def pair_events(markets):
    """Group retained markets into two-sided events. Diagnostic only.

    An event is a lead only when it holds exactly two markets with two
    distinct team labels — the shape a future typed adapter would still have
    to re-gate (exact start, open status, spread, liquidity) before pricing.
    """
    from scripts.core import norm

    grouped = {}
    for market in markets or []:
        event = market.get("event_ticker")
        team = market_team(market)
        if not event or not team:
            continue
        grouped.setdefault(event, []).append({
            "team": team, "ticker": market.get("ticker"),
            "title": market.get("title"),
            "yes_bid_dollars": market.get("yes_bid_dollars"),
            "yes_ask_dollars": market.get("yes_ask_dollars"),
            "liquidity_dollars": market.get("liquidity_dollars"),
            "close_time": market.get("close_time"),
            "expected_expiration_time": market.get("expected_expiration_time"),
        })
    paired = []
    for event, sides in grouped.items():
        keys = [norm(s["team"]) for s in sides]
        if len(sides) == 2 and len(set(keys)) == 2:
            paired.append({"event_ticker": event, "sides": sides})
    return paired


def match_event(fixture_teams, paired_events):
    """The unique paired event naming exactly these two teams, else None."""
    from scripts.core import norm

    if len(fixture_teams or []) != 2:
        return None
    want = {norm(t) for t in fixture_teams}
    hits = [e for e in paired_events or []
            if {norm(s["team"]) for s in e["sides"]} == want]
    return hits[0] if len(hits) == 1 else None


def get(url, timeout=30):
    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    try:
        r = requests.get(url, headers=UA, timeout=timeout)
        body = r.content
        parsed = None
        try:
            parsed = r.json()
        except ValueError:
            parsed = None
        return {
            "url": url, "retrieved_at": started, "http_status": r.status_code,
            "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
            "json": parsed,
        }
    except requests.RequestException as exc:
        return {"url": url, "retrieved_at": started, "http_status": None,
                "error": "%s: %s" % (type(exc).__name__, exc), "json": None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default="data/latest.json")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    snap = json.loads(Path(args.snapshot).read_text())
    open_rows = [m for m in snap.get("matches", []) if m.get("state") == "open"]
    unpriced = [m for m in open_rows if m.get("probabilities") is None]
    report = {
        "probe": "session-85087497 keyless fallback sources",
        "snapshot_generated_at": snap.get("generated_at"),
        "open_rows": len(open_rows),
        "unpriced_open_rows": [
            {"id": m["id"], "teams": m["teams"], "start": m.get("start"),
             "pick": m.get("pick"), "method": m.get("method")}
            for m in unpriced
        ],
        "kalshi": {}, "hltv_ranking": {},
    }

    # --- Kalshi series discovery (paged, bounded) ---
    series, receipts, cursor = [], [], None
    for _ in range(10):
        url = KALSHI + "/series?limit=1000" + (("&cursor=" + cursor) if cursor else "")
        got = get(url)
        receipts.append({k: v for k, v in got.items() if k != "json"})
        payload = got.get("json") or {}
        batch = payload.get("series") if isinstance(payload, dict) else None
        if not isinstance(batch, list):
            break
        series.extend(batch)
        cursor = payload.get("cursor") or None
        if not cursor or len(batch) < 1000:
            break
    cs_series = []
    for s in series:
        hay = " ".join(str(s.get(k) or "") for k in ("ticker", "title", "category")).lower()
        if "counter" in hay or "cs2" in hay or "csgo" in hay or "esports" in hay:
            cs_series.append({k: s.get(k) for k in ("ticker", "title", "category", "frequency")})
    report["kalshi"]["series_receipts"] = receipts
    report["kalshi"]["series_total"] = len(series)
    report["kalshi"]["cs_or_esports_series"] = cs_series

    # Series order is not meaningful, and the first probe (run 40199883762)
    # only just reached the moneyline series (KXCS2GAME, 11th of 54 matches).
    # CS2-titled series go first so the bounded fetch always starts with the
    # candidates an adapter would actually use.
    cs_series.sort(key=lambda s: (0 if "cs2" in str(s.get("ticker") or "").lower()
                                  or "counter-strike" in str(s.get("title") or "").lower() else 1,
                                  str(s.get("ticker") or "")))
    report["kalshi"]["cs_or_esports_series"] = cs_series
    markets_by_series = {}
    for s in cs_series[:12]:
        ticker = s.get("ticker")
        if not ticker:
            continue
        got = get(f"{KALSHI}/markets?series_ticker={ticker}&status=open&limit=1000")
        payload = got.get("json") or {}
        markets = payload.get("markets") if isinstance(payload, dict) else None
        markets = markets if isinstance(markets, list) else []
        markets_by_series[ticker] = {
            "receipt": {k: v for k, v in got.items() if k != "json"},
            "open_markets": len(markets),
            "sample_titles": [str(m.get("title") or "")[:160] for m in markets[:5]],
            "markets": [
                {"ticker": m.get("ticker"), "event_ticker": m.get("event_ticker"),
                 "title": m.get("title"), "subtitle": m.get("subtitle"),
                 "yes_sub_title": m.get("yes_sub_title"), "no_sub_title": m.get("no_sub_title"),
                 "status": m.get("status"), "close_time": m.get("close_time"),
                 "expected_expiration_time": m.get("expected_expiration_time"),
                 "yes_bid_dollars": m.get("yes_bid_dollars"), "yes_ask_dollars": m.get("yes_ask_dollars"),
                 "liquidity_dollars": m.get("liquidity_dollars"), "volume_fp": m.get("volume_fp")}
                for m in markets
            ],
        }
    report["kalshi"]["markets_by_series"] = markets_by_series

    # Kalshi's moneyline shape (measured run 40199883762): one event holds
    # exactly two markets titled "<Team> wins", one per side — so a pair can
    # never appear inside a single market's text and the first probe's
    # both-names-in-one-market test structurally found 0 leads. Pair markets
    # by event and compare whole labels through the project's own identity
    # rule (scripts.core.norm: exact folded label or verified register alias,
    # never substring — "BESTIA Academy wins" must not match "BESTIA").
    paired = {}
    for ticker, pack in markets_by_series.items():
        if "TOTAL" in ticker or "MAPS" in ticker:
            continue  # totals are not a series-winner price
        paired[ticker] = pair_events(pack["markets"])
    report["kalshi"]["paired_events_by_series"] = {
        ticker: len(events) for ticker, events in paired.items()}
    leads = []
    for m in open_rows:
        for ticker, events in paired.items():
            hit = match_event(m["teams"], events)
            if hit:
                leads.append({"fixture_id": m["id"], "teams": m["teams"],
                              "start": m.get("start"), "series": ticker,
                              "event_ticker": hit["event_ticker"],
                              "sides": hit["sides"]})
    report["kalshi"]["exact_pair_leads"] = leads

    # --- HLTV dated world ranking reachability ---
    today = datetime.now(timezone.utc).date()
    url = "https://www.hltv.org/ranking/teams/%04d/%s/%d" % (
        today.year, today.strftime("%B").lower(), today.day)
    got = get(url)
    report["hltv_ranking"] = {k: v for k, v in got.items() if k != "json"}
    report["hltv_ranking"]["url_requested"] = url

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({
        "open": len(open_rows), "unpriced": len(unpriced),
        "kalshi_series_total": len(series), "kalshi_cs_series": len(cs_series),
        "kalshi_open_markets": sum(p["open_markets"] for p in markets_by_series.values()),
        "exact_pair_leads": len(leads),
        "hltv_ranking_status": report["hltv_ranking"].get("http_status"),
    }))


if __name__ == "__main__":
    main()
