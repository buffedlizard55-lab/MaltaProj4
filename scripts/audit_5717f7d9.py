"""Independent line-by-line audit of the Hotspawn CS2 pick board (session 5717f7d9).

This auditor is deliberately self-contained: it imports **nothing** from
``scripts.*`` and re-derives every published number from the retained primary
evidence, so a shared bug in the production code cannot validate itself. It
reads only committed artifacts:

  * ``data/latest.json``                 -- the published snapshot
  * ``data/identities.json``             -- the reviewed alias register
  * ``data/vrs/standings_global_*.md``   -- Valve's official vendored standings
  * the rendered root ``*.html`` pages   -- what GitHub Pages actually serves

Findings have three severities:

  * ``fail`` -- a hard coverage/arithmetic/sourcing contract is broken; the
    board must not be published until explained. Exit code 1.
  * ``flag`` -- a real irregularity a human should review (source linked).
  * ``info`` -- a documented, already-disclosed limitation or observation.

The audit never invents a value: anything it cannot confirm from a retained
official source is reported, not filled in.
"""
from __future__ import annotations

import json
import math
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "session-5717f7d9"
MAX_AGE_HOURS = 8.0
EPS = 1e-9
ODDS_EPS = 1e-6
# Exchange gates published on the method page and enforced by the pipeline.
STRICT_SPREAD = 0.25
WIDE_SPREAD_CEILING = 0.60
MIN_LIQUIDITY = 100.0
# Valve published fit calibration (modelfit.png): observed = .7986 * expected + .126
VRS_SLOPE = 0.7986
VRS_RD = 75.0
HOTSPAWN_HOSTS = ("hotspawn.com", "cloudwaysapps.com")


# --------------------------------------------------------------------------- #
# Independent primitives (re-implemented from the documented rules, no imports)
# --------------------------------------------------------------------------- #
def plain_name(value: str) -> str:
    """NFKD diacritic fold + casefold + alphanumeric-only key."""
    if not isinstance(value, str):
        raise ValueError("team name is not text")
    folded = unicodedata.normalize("NFKD", value).casefold()
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    return "".join(c for c in unicodedata.normalize("NFKC", folded) if c.isalnum())


def load_alias_map() -> dict[str, str]:
    data = json.loads((ROOT / "data" / "identities.json").read_text(encoding="utf-8"))
    amap = {}
    for item in data.get("aliases", []):
        canonical = plain_name(item["canonical"])
        for name in item["names"]:
            amap[plain_name(name)] = canonical
    return amap


def norm(value: str, amap: dict[str, str]) -> str:
    key = plain_name(value)
    return amap.get(key, key)


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)


# Valve Glicko expected score with fixed RD 75 (model/fit.js priorWinExpectation).
_Q = math.log(10) / 400
_G = 1 / math.sqrt(1 + 3 * _Q * _Q * VRS_RD * VRS_RD / math.pi ** 2)


def vrs_expected(points_a: float, points_b: float) -> float:
    return 1 / (1 + 10 ** (-_G * (points_a - points_b) / 400))


def vrs_calibrated(raw: float) -> float:
    return 0.5 + VRS_SLOPE * (raw - 0.5)


_VRS_ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(-?\d+)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*\[details\]\(([^)]+)\)"
)


def load_vendored_standings() -> dict:
    """Parse Valve's vendored standings into by-rank and by-name indexes.

    Valve repeats some labels for distinct older rosters (e.g. two clubs both
    named "The Huns"), so names map to a *list*; the authoritative join is the
    retained standing number plus a roster overlap check.
    """
    vrs_dir = ROOT / "data" / "vrs"
    files = sorted(vrs_dir.glob("standings_global_*.md"))
    if not files:
        return {"by_standing": {}, "by_name": {}}
    by_standing: dict[int, dict] = {}
    by_name: dict[str, list[dict]] = {}
    for line in files[-1].read_text(encoding="utf-8").splitlines():
        m = _VRS_ROW.match(line)
        if not m:
            continue
        roster = [p.strip() for p in m.group(4).split(",") if p.strip()]
        row = {"standing": int(m.group(1)), "points": int(m.group(2)),
               "name": m.group(3).strip(), "roster": roster}
        by_standing[row["standing"]] = row
        by_name.setdefault(plain_name(row["name"]), []).append(row)
    return {"by_standing": by_standing, "by_name": by_name}


class Finding(dict):
    def __init__(self, severity, area, fixture, message, sources=None):
        super().__init__(severity=severity, area=area, fixture=str(fixture) if fixture is not None else None,
                         message=message, sources=sources or [])


# --------------------------------------------------------------------------- #
# Audit
# --------------------------------------------------------------------------- #
def audit(snapshot: dict, amap: dict, standings: dict) -> tuple[list[Finding], list[dict], dict]:
    findings: list[Finding] = []
    ledger: list[dict] = []
    generated = parse_ts(snapshot["generated_at"])
    matches = snapshot["matches"]
    opens = [m for m in matches if m.get("state") == "open"]
    not_open = [m for m in matches if m.get("state") != "open"]

    # --- D: not-open rows must never carry a price ------------------------- #
    for m in not_open:
        if m.get("probabilities") is not None or m.get("pick") or m.get("method"):
            findings.append(Finding("fail", "not_open_priced", m["id"],
                                    "A past/not-open feed row carries a pick, probability or method; "
                                    "past fixtures must never be priced.", [m.get("feed_url")]))
        ledger.append({"id": m["id"], "state": m.get("state"), "teams": m.get("teams"),
                       "priced": False, "result": "not-open row correctly unpriced"})

    for m in opens:
        fid = m["id"]
        rec = {"id": fid, "teams": m.get("teams"), "method": m.get("method"),
               "probabilities": m.get("probabilities"), "pick": m.get("pick"), "checks": []}

        # inventory-level source links
        if not m.get("source_url") or "hotspawn" not in m["source_url"]:
            findings.append(Finding("fail", "inventory_source", fid,
                                    "Missing an official Hotspawn source URL for the fixture.", []))
        else:
            rec["checks"].append("hotspawn source url")
            if "/matches/" not in m["source_url"]:
                # Hotspawn publishes no dedicated match page for this fixture;
                # the per-row authoritative source is the fixtures feed receipt.
                findings.append(Finding(
                    "info", "inventory_source", fid,
                    "No dedicated Hotspawn match page exists for this fixture; its official link is the "
                    "pick'em lobby. The fixtures-feed API receipt (with sha256 in fixture_sources) remains "
                    "the per-row primary source.",
                    [m["source_url"], m.get("feed_url")]))
        if not m.get("feed_url"):
            findings.append(Finding("fail", "inventory_source", fid, "Missing fixtures feed URL.", []))
        if not m.get("expires_at"):
            findings.append(Finding("flag", "expiry", fid, "No expires_at on an open row.",
                                    [m.get("source_url")]))
        if not m.get("evidence"):
            findings.append(Finding("fail", "evidence", fid, "Open row has no evidence entries.",
                                    [m.get("source_url")]))
        # C: no probability may originate from Hotspawn
        for e in m.get("evidence", []):
            for key in ("url", "api_url"):
                u = e.get(key) or ""
                if any(h in u for h in HOTSPAWN_HOSTS) and e.get("probabilities") is not None:
                    findings.append(Finding("fail", "hotspawn_leakage", fid,
                                            f"Probability evidence cites a Hotspawn host via {e.get('provider')}.",
                                            [u]))

        probs = m.get("probabilities")
        if probs is None:
            # E: unresolved / research-only contract
            if not m.get("attempts"):
                findings.append(Finding("fail", "unresolved_contract", fid,
                                        "Row has no probability and no recorded attempts ledger.", []))
            if not m.get("pick") and not m.get("reason"):
                findings.append(Finding("fail", "unresolved_contract", fid,
                                        "Unpriced row has neither a pick nor a reason; blank must be explained.",
                                        []))
            rec["result"] = "no probability (research-only or unresolved); attempts ledger present"
            ledger.append(rec)
            continue

        # B1: complement / range
        if len(probs) != 2 or not all(0.0 < p < 1.0 for p in probs):
            findings.append(Finding("fail", "probability_shape", fid,
                                    f"Probabilities are not two values in (0,1): {probs}", []))
        elif abs(sum(probs) - 1.0) > EPS:
            findings.append(Finding("fail", "complement", fid,
                                    f"Probabilities sum to {sum(probs)!r}, not 1.", []))
        else:
            rec["checks"].append("probabilities sum to 1")

        # B2: fair odds inverse
        fair = m.get("fair_odds")
        if not fair or len(fair) != 2 or any(abs(o - 1 / p) > ODDS_EPS for p, o in zip(probs, fair)):
            findings.append(Finding("fail", "fair_odds", fid,
                                    f"Fair odds {fair} are not the inverse of probabilities {probs}.", []))
        else:
            rec["checks"].append("fair odds = 1/probability")

        # B3: pick is the favourite (a true 0.5/0.5 would publish no directional pick)
        if m.get("pick") not in m["teams"]:
            findings.append(Finding("fail", "pick_identity", fid,
                                    f"Pick {m.get('pick')!r} is not one of the teams {m['teams']}.", []))
        elif abs(probs[0] - probs[1]) > EPS:
            fav = m["teams"][probs.index(max(probs))]
            if m["pick"] != fav:
                findings.append(Finding("fail", "pick_direction", fid,
                                        f"Pick {m['pick']!r} is not the favourite {fav!r} ({probs}).", []))
            else:
                rec["checks"].append("pick = favourite")

        method = m.get("method")
        if method in ("exchange", "exchange_wide"):
            _audit_exchange(m, generated, amap, findings, rec)
        elif method == "bookmaker_fallback":
            _audit_book(m, generated, amap, findings, rec)
        elif method in ("model_vrs", "model_vrs_mirror"):
            _audit_vrs(m, generated, standings, findings, rec)
        else:
            findings.append(Finding("flag", "method", fid,
                                    f"Unrecognised method {method!r}; arithmetic not independently re-derived.",
                                    [m.get("source_url")]))
        ledger.append(rec)

    # snapshot-level: aggregate the source-access limits recorded in the
    # attempts ledgers (the documented reason some rungs cannot price a row).
    blocked = {}
    for m in opens:
        for a in m.get("attempts", []):
            if a.get("status") == "error":
                blocked.setdefault(a.get("provider", "unknown"), set()).add(str(a.get("reason", ""))[:140])
    for provider, reasons in sorted(blocked.items()):
        findings.append(Finding(
            "info", "source_access_limit", None,
            f"{provider} was unreachable on the runner for this snapshot: "
            + " | ".join(sorted(reasons))[:400],
            ["https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html"]))

    # snapshot-level coverage statement
    expected = {
        "open": len(opens),
        "with_pick": sum(1 for m in opens if m.get("pick")),
        "with_prob": sum(1 for m in opens if m.get("probabilities") is not None),
        "unresolved": sum(1 for m in opens if m.get("probabilities") is None and not m.get("pick")),
        "not_open_feed_rows": len(not_open),
    }
    return findings, ledger, expected


def _fresh(e: dict, generated: datetime, findings: list[Finding], fid: str) -> bool:
    obs = e.get("observed_at")
    if not obs:
        findings.append(Finding("flag", "freshness", fid,
                                f"{e.get('provider')} evidence has no observation timestamp.",
                                [e.get("url")]))
        return False
    age_h = (generated - parse_ts(obs)).total_seconds() / 3600
    if age_h > MAX_AGE_HOURS:
        findings.append(Finding("fail", "freshness", fid,
                                f"{e.get('provider')} evidence is {age_h:.2f}h old (> {MAX_AGE_HOURS}h window).",
                                [e.get("url")]))
        return False
    return True


def _audit_exchange(m, generated, amap, findings, rec):
    ev = [e for e in m["evidence"] if e.get("provider") == "Polymarket" and "raw" in e]
    if not ev:
        findings.append(Finding("fail", "exchange_evidence", m["id"],
                                "Exchange row has no retained Polymarket raw market.", []))
        return
    e = ev[0]
    raw = e["raw"]
    _fresh(e, generated, findings, m["id"])
    # market must still be live and funded
    if not raw.get("acceptingOrders") or raw.get("closed") or not raw.get("active"):
        findings.append(Finding("fail", "market_state", m["id"],
                                "Polymarket market is closed/inactive/not accepting orders but a live "
                                "probability was published.", [e.get("api_url")]))
    # orient raw prices to the fixture's team order via the named outcomes array
    outcomes = json.loads(raw["outcomes"])
    prices = [float(x) for x in json.loads(raw["outcomePrices"])]
    by_name = {norm(name, amap): price for name, price in zip(outcomes, prices)}
    for team, published in zip(m["teams"], m["probabilities"]):
        raw_price = by_name.get(norm(team, amap))
        if raw_price is None:
            findings.append(Finding("fail", "orientation", m["id"],
                                    f"Fixture team {team!r} cannot be matched to a named Polymarket outcome "
                                    f"{outcomes}; no fuzzy guessing allowed.", [e.get("api_url")]))
        elif abs(raw_price - published) > EPS:
            findings.append(Finding("fail", "price_rederive", m["id"],
                                    f"Published {published} != raw outcome price {raw_price} for {team!r}.",
                                    [e.get("api_url")]))
    rec["checks"].append("probability re-derived from named raw outcome prices")
    # gate geometry. The documented rule is "spread <= 25 points"; use the same
    # float-safe epsilon the primary gate uses (a computed 0.25000000000000006
    # is 25 points, not a violation).
    spread = e.get("spread")
    liquidity = e.get("liquidity") or 0.0
    eps = 1e-9
    if m["method"] == "exchange":
        if spread is None or spread > STRICT_SPREAD + eps:
            findings.append(Finding("fail", "spread_gate", m["id"],
                                    f"Strict exchange spread {spread} exceeds {STRICT_SPREAD}.",
                                    [e.get("api_url")]))
    else:
        if spread is None or not (STRICT_SPREAD + eps < spread <= WIDE_SPREAD_CEILING + eps):
            findings.append(Finding("fail", "spread_gate", m["id"],
                                    f"Wide-exchange spread {spread} outside "
                                    f"({STRICT_SPREAD}, {WIDE_SPREAD_CEILING}].", [e.get("api_url")]))
        if not any("wide" in f.lower() for f in m.get("flags", [])):
            findings.append(Finding("flag", "wide_label", m["id"],
                                    "Wide low-confidence tier used without a visible warning flag.",
                                    [e.get("api_url")]))
    if liquidity < MIN_LIQUIDITY:
        findings.append(Finding("fail", "liquidity_gate", m["id"],
                                f"Liquidity {liquidity} below ${MIN_LIQUIDITY:.0f}.", [e.get("api_url")]))
    if not e.get("url"):
        findings.append(Finding("fail", "source_link", m["id"], "Exchange evidence has no source URL.", []))
    rec["checks"].append(f"spread {spread}, liquidity {liquidity}")


def _audit_book(m, generated, amap, findings, rec):
    e = m["evidence"][0]
    _fresh(e, generated, findings, m["id"])
    odds = e.get("decimal_odds")
    if not odds or len(odds) != 2:
        findings.append(Finding("fail", "book_odds", m["id"],
                                "Bookmaker row retains no two-way decimal odds.", [e.get("url")]))
        return
    inverse = [1 / float(o) for o in odds]
    overround = sum(inverse) - 1.0
    fair = [x / sum(inverse) for x in inverse]
    if any(abs(a - b) > EPS for a, b in zip(fair, m["probabilities"])):
        findings.append(Finding("fail", "devig_rederive", m["id"],
                                f"De-vig {fair} != published {m['probabilities']}.", [e.get("url")]))
    else:
        rec["checks"].append("de-vig re-derived from retained decimal odds")
    if abs(overround - e.get("overround", overround)) > 1e-9:
        findings.append(Finding("flag", "overround", m["id"],
                                f"Retained overround {e.get('overround')} != computed {overround}.",
                                [e.get("url")]))
    src_teams = e.get("source_teams") or []
    if sorted(norm(t, amap) for t in src_teams) != sorted(norm(t, amap) for t in m["teams"]):
        findings.append(Finding("fail", "book_identity", m["id"],
                                f"Book source teams {src_teams} do not match fixture {m['teams']}.",
                                [e.get("url")]))
    if not e.get("url") or not e.get("api_url"):
        findings.append(Finding("fail", "source_link", m["id"],
                                "Bookmaker evidence missing a listing or API source link.", [e.get("url")]))
    if not any("researched listing" in f.lower() for f in m.get("flags", [])):
        findings.append(Finding("flag", "book_label", m["id"],
                                "Researched book listing without the disclosed no-adapter limitation flag.",
                                [e.get("url")]))


MIRROR_PROVIDER = "HLTV Valve ranking (Valve points)"


def _audit_vrs(m, generated, standings, findings, rec):
    # Two providers carry the same Valve points and the same published formula:
    # the monthly official file, and HLTV's dated view of that ranking used when
    # the monthly file does not resolve the clubs. The arithmetic checks below
    # are identical; only the mirror needs its own provenance assertions, and
    # only the official-file row can be joined against the vendored file.
    ev = [e for e in m["evidence"] if e.get("provider") in ("Valve VRS model", MIRROR_PROVIDER)]
    if not ev:
        findings.append(Finding("fail", "vrs_evidence", m["id"], "Model row has no VRS evidence.", []))
        return
    e = ev[0]
    if e.get("provider") == MIRROR_PROVIDER:
        for key in ("ranking_as_of", "ranking_page_sha256"):
            if not e.get(key):
                findings.append(Finding("fail", "vrs_mirror_source", m["id"],
                                        f"Mirror evidence missing {key}.", [e.get("url")]))
        fixture_teams = e.get("fixture_teams") or []
        if sorted(norm(t, {}) for t in fixture_teams) != sorted(norm(t, {}) for t in m["teams"]):
            findings.append(Finding("fail", "vrs_mirror_identity", m["id"],
                                    f"Mirror fixture teams {fixture_teams} do not match {m['teams']}.",
                                    [e.get("url")]))
        if len(e.get("vrs_teams") or []) != 2:
            findings.append(Finding("fail", "vrs_mirror_identity", m["id"],
                                    "Mirror evidence does not name both ranking rows.", [e.get("url")]))
        if str(e.get("ranking_as_of")) > generated.strftime("%Y-%m-%d"):
            findings.append(Finding("fail", "vrs_mirror_source", m["id"],
                                    f"Mirror ranking dated {e.get('ranking_as_of')} is after the snapshot.",
                                    [e.get("url")]))
    points = e.get("points")
    if not points or len(points) != 2:
        findings.append(Finding("fail", "vrs_points", m["id"], "No retained Valve points.", [e.get("url")]))
        return
    raw_e = vrs_expected(points[0], points[1])
    cal = vrs_calibrated(raw_e)
    if abs(cal - m["probabilities"][0]) > EPS:
        findings.append(Finding("fail", "vrs_rederive", m["id"],
                                f"Re-derived {cal:.6f} != published {m['probabilities'][0]:.6f}.",
                                [e.get("formula_source"), e.get("url")]))
    else:
        rec["checks"].append("Glicko + Valve calibration re-derived from retained points")
    retained_raw = (e.get("raw_expected") or [None])[0]
    if retained_raw is not None and abs(retained_raw - raw_e) > EPS:
        findings.append(Finding("fail", "vrs_raw", m["id"],
                                f"Retained raw expectation {retained_raw} != re-derived {raw_e}.",
                                [e.get("formula_source")]))
    if abs(e.get("calibration_slope", VRS_SLOPE) - VRS_SLOPE) > EPS:
        findings.append(Finding("flag", "vrs_slope", m["id"],
                                f"Calibration slope {e.get('calibration_slope')} != documented {VRS_SLOPE}.",
                                [e.get("calibration_source")]))
    for key in ("formula_source", "calibration_source", "url", "api_url"):
        if not e.get(key):
            findings.append(Finding("fail", "vrs_source", m["id"],
                                    f"Model evidence missing {key}.", [e.get("url")]))
    if not any("model estimate" in f.lower() for f in m.get("flags", [])):
        findings.append(Finding("flag", "vrs_label", m["id"],
                                "Originated model line missing the 'not a market price' flag.", [e.get("url")]))
    # cross-check retained points against the vendored official Valve file.
    # Join on the retained standing number (labels can repeat for two rosters);
    # for a duplicated label require the >=3-player roster overlap that Valve
    # itself uses to treat rosters as the same club.
    if m["method"] == "model_vrs" and standings and standings.get("by_standing"):
        by_standing = standings["by_standing"]
        by_name = standings["by_name"]
        overlap_by_team = {norm(m["teams"][i], {}): c
                           for i, c in enumerate(e.get("roster_checks", []))}
        for team, pts, standing, retained_roster in zip(
                e.get("vrs_teams", m["teams"]), points, e.get("standings", [None, None]),
                e.get("rosters", [[], []])):
            key = norm(team, {})
            same_label = by_name.get(key, [])
            row = by_standing.get(standing) if standing is not None else None
            if row is None:
                findings.append(Finding("flag", "vrs_vendored", m["id"],
                                        f"Retained standing {standing} for {team!r} not found in the vendored "
                                        "Valve file.", [e.get("url")]))
                continue
            if row["points"] != pts:
                findings.append(Finding("fail", "vrs_vendored", m["id"],
                                        f"Retained points {pts} for {team!r} != vendored Valve file "
                                        f"{row['points']} at standing {standing}.", [e.get("url")]))
            # the joined row must carry the same roster the evidence retained
            if retained_roster and {plain_name(p) for p in retained_roster} != \
                    {plain_name(p) for p in row["roster"]}:
                findings.append(Finding("fail", "vrs_vendored", m["id"],
                                        f"Retained roster for {team!r} does not match vendored standing "
                                        f"{standing}.", [e.get("url")]))
            # duplicated label: prove the disambiguation, do not guess
            if len(same_label) > 1:
                chk = overlap_by_team.get(key)
                overlap = chk.get("overlap") if chk else None
                if not isinstance(overlap, int) or overlap < 3:
                    findings.append(Finding("fail", "vrs_duplicate_label", m["id"],
                                            f"Duplicated Valve label {team!r} (standings "
                                            f"{[r['standing'] for r in same_label]}) selected without the "
                                            "required >=3-player HLTV roster overlap.", [e.get("url")]))
                else:
                    rec["checks"].append(
                        f"duplicate label disambiguated by {overlap}/5 roster overlap -> standing {standing}")
        rec["checks"].append("points/standings/roster cross-checked against vendored Valve file")
    # roster overlap: Valve treats >=3 shared players as the same club. A null
    # overlap means roster continuity was not checked on this run (legal for a
    # unique Valve label); it is neither a pass nor a failure here.
    for chk in e.get("roster_checks", []):
        overlap = chk.get("overlap")
        if overlap is None:
            rec["checks"].append("roster continuity not checked this run (unique label)")
            continue
        if overlap < 3:
            findings.append(Finding("flag", "vrs_roster", m["id"],
                                    f"Roster overlap {overlap} < 3 for {chk.get('lineup')}; "
                                    "identity rests on the alias/anchor register.", [e.get("url")]))


# --------------------------------------------------------------------------- #
# Rendered-site / mobile checks
# --------------------------------------------------------------------------- #
def audit_site(snapshot: dict, findings: list[Finding]) -> dict:
    index = BeautifulSoup((ROOT / "index.html").read_text(encoding="utf-8"), "html.parser")
    picks = BeautifulSoup((ROOT / "picks.html").read_text(encoding="utf-8"), "html.parser")
    unresolved = BeautifulSoup((ROOT / "unresolved.html").read_text(encoding="utf-8"), "html.parser")
    page_names = ("index.html", "picks.html", "unresolved.html", "matches.html",
                  "analysis.html", "review.html", "sources.html", "evidence.html",
                  "methodology.html", "404.html")
    pages = {name: BeautifulSoup((ROOT / name).read_text(encoding="utf-8"), "html.parser")
             for name in page_names if (ROOT / name).exists()}
    opens = [m for m in snapshot["matches"] if m.get("state") == "open"]
    result = {}
    redirects = set()

    # viewport + phone tab bar on every real page; redirect stubs only need a
    # viewport and a target that exists.
    for name, soup in pages.items():
        if not soup.find("meta", attrs={"name": "viewport"}):
            findings.append(Finding("fail", "mobile", name, "Missing viewport meta tag.", []))
        refresh = soup.find("meta", attrs={"http-equiv": "refresh"})
        if refresh:
            redirects.add(name)
            target = re.search(r"url=([^'\"\s>]+)", refresh.get("content", ""))
            if not target or not (ROOT / target.group(1).lstrip("./")).exists():
                findings.append(Finding("fail", "redirect", name,
                                        f"Redirect target missing: {refresh.get('content')}", []))
            continue
        tabs = soup.find("nav", class_="mobile-tabs")
        if not tabs:
            findings.append(Finding("fail", "mobile", name, "Missing the phone bottom tab bar.", []))
        else:
            labels = tabs.get_text(" ", strip=True)
            for need in ("Home", "Picks", "Unresolved", "Matches", "Analysis"):
                if need not in labels:
                    findings.append(Finding("fail", "mobile", name,
                                            f"Phone tab bar missing {need!r}.", []))
    result["pages_checked"] = len(pages)
    result["redirect_stubs"] = sorted(redirects)

    # executive summary quicknav: in-site links to the pick board and unresolved
    qn = index.find(id="exec-quicknav")
    if not qn:
        findings.append(Finding("fail", "exec_summary", "index.html",
                                "Executive summary quicknav (#exec-quicknav) missing.", []))
    else:
        hrefs = [a.get("href", "") for a in qn.find_all("a", href=True)]
        if not any(h.startswith("picks.html") for h in hrefs):
            findings.append(Finding("fail", "exec_summary", "index.html",
                                    "Quicknav has no in-site link to the updated-pick board.", hrefs))
        if not any("unresolved" in h for h in hrefs):
            findings.append(Finding("fail", "exec_summary", "index.html",
                                    "Quicknav has no link to the unresolved/limitations section.", hrefs))
        result["quicknav_hrefs"] = hrefs
    for anchor in ("unresolved-limits", "unresolved-summary"):
        if not index.find(id=anchor):
            findings.append(Finding("flag", "exec_summary", "index.html",
                                    f"Expected in-page anchor #{anchor} not found.", []))

    # unresolved page renders even when the count is zero and names the limits
    uh = unresolved.get_text(" ", strip=True).lower()
    if not any(term in uh for term in ("ladder", "rung", "every source tried", "in order")):
        findings.append(Finding("flag", "unresolved", "unresolved.html",
                                "Unresolved page does not describe the resolution ladder.", []))

    # every priced open fixture is a row on picks.html with an external source
    # link and both teams' percentages
    rows = {r.get("data-match"): r for r in picks.find_all("tr", attrs={"data-match": True})}
    result["pick_rows"] = len(rows)
    missing_rows = []
    for m in opens:
        fid = m["id"]
        row = rows.get(fid)
        if row is None:
            missing_rows.append(fid)
            continue
        ext = [a["href"] for a in row.find_all("a", href=True) if a["href"].startswith("http")]
        if not ext:
            findings.append(Finding("fail", "row_source", fid,
                                    "Displayed pick row has no external official source link.", []))
        txt = row.get_text(" ", strip=True)
        pcts = re.findall(r"(\d+(?:\.\d+)?)%", txt)
        if len(pcts) < 2:
            findings.append(Finding("fail", "row_percent", fid,
                                    "Displayed pick row does not show both teams' percentages.", ext[:2]))
        if m.get("pick") and m["pick"] not in txt:
            findings.append(Finding("fail", "row_pick", fid,
                                    f"Displayed row does not name the pick {m['pick']!r}.", ext[:2]))
    if missing_rows:
        findings.append(Finding("fail", "pick_coverage", None,
                                f"{len(missing_rows)} open fixtures have no row on picks.html: "
                                f"{missing_rows}", ["picks.html"]))

    # internal links resolve to a real file/anchor; no localhost on the browser side
    for name, soup in pages.items():
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith(("http", "mailto:", "tel:")):
                if "localhost" in href or "127.0.0.1" in href:
                    findings.append(Finding("fail", "link", name,
                                            f"Browser-facing link points at localhost: {href}", []))
                continue
            no_frag = href.split("#", 1)[0]
            target = no_frag.split("?", 1)[0]          # strip filter query string
            frag = href.split("#", 1)[1] if "#" in href else ""
            path = ROOT / target if target else ROOT / name
            if target and not path.exists():
                findings.append(Finding("fail", "link", name,
                                        f"Broken internal link {href!r}.", []))
            elif frag:
                tsoup = soup if not target else BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
                if not tsoup.find(id=frag):
                    findings.append(Finding("flag", "link", name,
                                            f"Anchor #{frag} not found in {target or name}.", []))
    return result


def main() -> int:
    snapshot = json.loads((ROOT / "data" / "latest.json").read_text(encoding="utf-8"))
    amap = load_alias_map()
    standings = load_vendored_standings()
    findings, ledger, expected = audit(snapshot, amap, standings)
    site = audit_site(snapshot, findings)

    sev = {}
    for f in findings:
        sev[f["severity"]] = sev.get(f["severity"], 0) + 1
    report = {
        "auditor": "scripts/audit_5717f7d9.py",
        "snapshot_generated_at": snapshot["generated_at"],
        "independent_of_pipeline": True,
        "coverage_measured": expected,
        "method_mix": _method_mix(snapshot),
        "site_checks": site,
        "finding_counts": sev,
        "findings": findings,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "audit-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (OUT / "row-ledger.json").write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    (OUT / "row-ledger.md").write_text(_ledger_md(snapshot, ledger, expected), encoding="utf-8")

    print(json.dumps({"coverage": expected, "method_mix": report["method_mix"],
                      "site_checks": site, "finding_counts": sev}, indent=2))
    hard = [f for f in findings if f["severity"] == "fail"]
    if hard:
        print(f"\n{len(hard)} HARD FAILURE(S):", file=sys.stderr)
        for f in hard:
            print(f"  [{f['area']}] {f['fixture']}: {f['message']}", file=sys.stderr)
        return 1
    print("\nNo hard contract failures. Flags/info are documented in",
          OUT / "audit-report.json")
    return 0


def _method_mix(snapshot):
    mix = {}
    for m in snapshot["matches"]:
        if m.get("state") == "open":
            mix[m.get("method")] = mix.get(m.get("method"), 0) + 1
    return mix


def _ledger_md(snapshot, ledger, expected):
    lines = ["# Independent row ledger — session 5717f7d9", "",
             f"Snapshot `{snapshot['generated_at']}`. Every open row re-derived from retained primary "
             "evidence; this auditor imports no pipeline code.", "",
             f"Measured coverage: **{expected['open']} open · {expected['with_pick']} with a pick · "
             f"{expected['with_prob']} with a win probability · {expected['unresolved']} unresolved**.", "",
             "| Fixture | Teams | Method | Published probs | Pick | Independent checks |",
             "| --- | --- | --- | --- | --- | --- |"]
    for rec in ledger:
        if rec.get("state") and rec["state"] != "open":
            continue
        probs = rec.get("probabilities")
        prob_txt = " / ".join(f"{p:.4f}" for p in probs) if probs else "—"
        lines.append("| {id} | {teams} | {method} | {probs} | {pick} | {checks} |".format(
            id=rec["id"], teams=" vs ".join(rec.get("teams") or []), method=rec.get("method"),
            probs=prob_txt, pick=rec.get("pick") or "—",
            checks="; ".join(rec.get("checks") or [rec.get("result", "")])))
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
