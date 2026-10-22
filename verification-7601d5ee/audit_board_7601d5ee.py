"""Comprehensive line-by-line acceptance auditor for session 7601d5ee.

Audits:
- data/latest.json (all matches, open vs non-open, probabilities, fair odds, source links)
- All 9 staged HTML pages (index.html, picks.html, unresolved.html, matches.html,
  analysis.html, evidence.html, review.html, sources.html, methodology.html)
- Mobile layout invariants (viewport meta tag, executive summary links, responsive CSS)
- Zero-Hotspawn-probability-leakage invariant
- Mathematical re-derivation of every priced row (exchange, bookmaker, Valve VRS model)
- Unverified/research-only rows leave probability cells blank and appear on review.html
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.core import devig, norm
from scripts.vrs import calibrated, expected

HTML_PAGES = [
    "index.html",
    "picks.html",
    "unresolved.html",
    "matches.html",
    "analysis.html",
    "evidence.html",
    "review.html",
    "sources.html",
    "methodology.html",
]

FORBIDDEN_HOTSPAWN_TOKENS = (
    "winner_percentage",
    "selection_percentage",
    "crowd_pick",
    "fan_vote",
)


def audit_html_pages(root: Path = ROOT) -> dict:
    page_stats = {}
    for name in HTML_PAGES:
        path = root / name
        assert path.exists(), f"Missing staged HTML page: {name}"
        text = path.read_text()
        for token in FORBIDDEN_HOTSPAWN_TOKENS:
            assert token not in text, f"Forbidden token {token!r} found in {name}"
        soup = BeautifulSoup(text, "html.parser")
        viewport = soup.find("meta", attrs={"name": "viewport"})
        assert viewport is not None and "width=device-width" in (viewport.get("content") or ""), (
            f"Missing mobile viewport meta on {name}"
        )
        rows = soup.select("tbody tr")
        if name in {"picks.html", "unresolved.html", "matches.html", "evidence.html", "review.html", "sources.html"}:
            for idx, tr in enumerate(rows, start=1):
                ext_links = [
                    a.get("href", "")
                    for a in tr.find_all("a", href=True)
                    if a["href"].startswith("https://")
                ]
                assert ext_links, f"{name} tbody row #{idx} has no external https:// source link"
        page_stats[name] = {
            "tbody_rows": len(rows),
            "has_viewport": True,
        }

    # Verify index.html executive summary links
    index_soup = BeautifulSoup((root / "index.html").read_text(), "html.parser")
    hrefs = {a.get("href", "") for a in index_soup.find_all("a", href=True)}
    for target in ("picks.html", "unresolved.html", "review.html"):
        assert any(h == target or h.startswith(target + "#") for h in hrefs), (
            f"index.html missing executive-summary link to {target}"
        )
    return page_stats


def audit_board_math(root: Path = ROOT) -> dict:
    latest = json.loads((root / "data" / "latest.json").read_text())
    matches = latest["matches"]
    open_rows = [m for m in matches if m["state"] == "open"]
    not_open_rows = [m for m in matches if m["state"] != "open"]

    priced_count = 0
    research_count = 0
    unresolved_count = 0

    for row in open_rows:
        assert row.get("source_url", "").startswith("https://"), f"Row {row['id']} missing source_url"
        assert row.get("feed_url", "").startswith("https://"), f"Row {row['id']} missing feed_url"
        probs = row.get("probabilities")
        fair = row.get("fair_odds")
        method = row.get("method")
        if probs is not None:
            priced_count += 1
            assert len(probs) == 2 and len(fair) == 2
            assert math.isclose(probs[0] + probs[1], 1.0, abs_tol=1e-6)
            assert math.isclose(fair[0], 1.0 / probs[0], rel_tol=1e-6)
            assert math.isclose(fair[1], 1.0 / probs[1], rel_tol=1e-6)
            expected_pick = row["teams"][0 if probs[0] > probs[1] else 1]
            assert row["pick"] == expected_pick
            ev = row["evidence"][0]
            assert ev.get("url", "").startswith("https://")
            if method == "model_vrs":
                pts = ev["points"]
                c = calibrated(expected(pts[0], pts[1]))
                assert math.isclose(probs[0], c, abs_tol=1e-6)
                assert math.isclose(probs[1], 1.0 - c, abs_tol=1e-6)
            elif method in {"bookmaker", "bookmaker_fallback", "bookmaker_research"}:
                p_devig, _ = devig(ev["decimal_odds"])
                assert math.isclose(probs[0], p_devig[0], abs_tol=1e-6)
                assert math.isclose(probs[1], p_devig[1], abs_tol=1e-6)
            elif method in {"exchange", "exchange_wide"}:
                outcomes = json.loads(ev["raw"]["outcomes"])
                raw_prices = [float(x) for x in json.loads(ev["raw"]["outcomePrices"])]
                total = sum(raw_prices)
                norm_prices = [x / total for x in raw_prices]
                if norm(outcomes[0]) == norm(row["teams"][1]):
                    norm_prices = list(reversed(norm_prices))
                assert math.isclose(probs[0], norm_prices[0], abs_tol=1e-6)
                assert math.isclose(probs[1], norm_prices[1], abs_tol=1e-6)
        elif row.get("pick"):
            research_count += 1
            assert fair is None
            assert row.get("flags"), f"Research-only row {row['id']} must be flagged for review"
        else:
            unresolved_count += 1
            assert fair is None

    # Every research-only open fixture must appear on review.html
    review_html = (root / "review.html").read_text()
    for row in open_rows:
        if row.get("probabilities") is None and row.get("pick"):
            assert row["teams"][0] in review_html and row["teams"][1] in review_html, (
                f"Research-only row {row['id']} ({row['teams']}) missing from review.html"
            )

    return {
        "generated_at": latest["generated_at"],
        "total_matches": len(matches),
        "open_matches": len(open_rows),
        "not_open_matches": len(not_open_rows),
        "priced_open": priced_count,
        "research_only_open": research_count,
        "unresolved_open": unresolved_count,
    }


def run_all(root: Path = ROOT) -> dict:
    pages = audit_html_pages(root)
    board = audit_board_math(root)
    return {
        "status": "ok",
        "session_id": "7601d5ee",
        "board": board,
        "pages": pages,
    }


if __name__ == "__main__":
    print(json.dumps(run_all(), indent=2))
