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

    # Exact-pair lead test only (both team labels present in one market's text).
    def mentions(text, team):
        return team and team.lower() in (text or "").lower()

    leads = []
    for m in unpriced + open_rows:
        for ticker, pack in markets_by_series.items():
            for mk in pack["markets"]:
                text = " | ".join(str(mk.get(k) or "") for k in ("title", "subtitle", "yes_sub_title", "no_sub_title"))
                if all(mentions(text, t) for t in m["teams"]):
                    leads.append({"fixture_id": m["id"], "teams": m["teams"], "start": m.get("start"),
                                  "series": ticker, "market_ticker": mk.get("ticker"), "title": mk.get("title")})
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
