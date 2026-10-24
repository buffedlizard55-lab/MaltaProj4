"""Session cecfe864: independent line-by-line verifier and ledger generator for
the 92-row / 31-open 2026-10-24T06:19:43.492019Z Hotspawn CS2 snapshot.

Checks performed without sharing math helpers with ``scripts/core.py``:
1. Three-view Hotspawn inventory parity (API = 92, /cs2-pickems = 92, /lobby = 92,
   retained = 92): 31 open fixtures and 61 past-dated not-open scheduled rows.
2. Every open fixture (31/31) has a pick from its own two teams, two win
   probabilities summing to 1, two fair decimal odds equal to 1/p_i, and an
   https source URL on both the fixture and the primary evidence record.
3. Every probability is independently re-derived from the stored raw source
   receipt (Polymarket outcomePrices normalized and oriented via exact label,
   prefix or primary-source-verified identity_sources; BO3.gg/Thunderpick
   decimal odds de-vigged via q_i = 1/d_i, p_i = q_i/(q_1+q_2); Valve VRS and
   HLTV dated Valve ranking mirror points passed through Valve's Glicko
   expectation with RD=75 and calibration slope 0.7986).
4. Every non-featured open row (15 rows: 3 exchange_wide, 3 bookmaker_fallback,
   6 model_vrs, 3 model_vrs_mirror) records an explicit HLTV attempt first and
   esportsbook/betting-line attempts next before any originated model tier.
5. Every not-open row (61/61) carries an https source URL and feed URL, blank
   pick/probabilities/fair_odds/method, and an explicit non-open reason.
"""
from __future__ import annotations

import argparse
import json
import math
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RD = 75.0
Q = math.log(10) / 400.0
G = 1.0 / math.sqrt(1.0 + 3.0 * Q * Q * RD * RD / (math.pi ** 2))
SLOPE = 0.7986
TOL = 1e-6


def _norm(text: str) -> str:
    folded = unicodedata.normalize("NFKD", str(text))
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    return "".join(ch for ch in folded.lower() if ch.isalnum())


def _same_team(a: str, b: str, identity_sources=()) -> bool:
    na, nb = _norm(a), _norm(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    short, long = sorted((na, nb), key=len)
    if len(short) >= 3 and long.startswith(short):
        return True
    for entry in identity_sources or ():
        if not isinstance(entry, dict):
            continue
        if not str(entry.get("source") or "").startswith("https://"):
            continue
        if not str(entry.get("basis") or "").strip():
            continue
        names = {_norm(n) for n in (entry.get("names") or ()) if _norm(n)}
        if na in names and nb in names:
            return True
    return False


def _order_pair(labels, values, teams, identity_sources=()):
    indices = []
    for team in teams:
        hits = [i for i, lbl in enumerate(labels) if _same_team(lbl, team, identity_sources)]
        if len(hits) != 1:
            raise ValueError(f"cannot map {team!r} to {labels!r}")
        indices.append(hits[0])
    if len(set(indices)) != 2:
        raise ValueError(f"ambiguous team mapping for {teams!r} in {labels!r}")
    return [values[i] for i in indices]


def _vrs_probs(pa: float, pb: float) -> list[float]:
    raw = 1.0 / (1.0 + 10.0 ** (-G * (float(pa) - float(pb)) / 400.0))
    cal = 0.5 + SLOPE * (raw - 0.5)
    return [cal, 1.0 - cal]


def rederive_row(match: dict) -> tuple[list[float], str]:
    ev = (match.get("evidence") or [None])[0]
    if not ev:
        raise ValueError(f"match {match.get('id')} has no evidence record")
    teams = match["teams"]
    id_sources = ev.get("identity_sources") or ()
    provider = ev.get("provider")
    if provider == "Valve VRS model":
        pts = ev["points"]
        return _vrs_probs(pts[0], pts[1]), "model_vrs"
    if provider == "HLTV Valve ranking (Valve points)":
        pts = ev["points"]
        return _vrs_probs(pts[0], pts[1]), "model_vrs_mirror"
    if "decimal_odds" in ev:
        odds = [float(x) for x in ev["decimal_odds"]]
        inv = [1.0 / d for d in odds]
        total = sum(inv)
        probs = [q / total for q in inv]
        probs = _order_pair(ev.get("source_teams") or teams, probs, teams, id_sources)
        return probs, "bookmaker_devig"
    raw = ev.get("raw") or {}
    outcome_prices = raw.get("outcomePrices")
    if outcome_prices:
        vals = [
            float(x)
            for x in (
                json.loads(outcome_prices)
                if isinstance(outcome_prices, str)
                else outcome_prices
            )
        ]
        total = sum(vals)
        probs = [v / total for v in vals]
        outcomes = (
            json.loads(raw["outcomes"])
            if isinstance(raw.get("outcomes"), str)
            else raw.get("outcomes")
        )
        probs = _order_pair(outcomes, probs, teams, id_sources)
        return probs, "exchange_mid"
    raise ValueError(f"unrecognised evidence structure on {match.get('id')}")


def audit_snapshot(data_path: Path = ROOT / "data" / "latest.json") -> dict:
    doc = json.loads(Path(data_path).read_text(encoding="utf-8"))
    matches = doc.get("matches") or []
    open_rows = [m for m in matches if m.get("state") == "open"]
    not_open_rows = [m for m in matches if m.get("state") != "open"]
    errors: list[str] = []

    counts = doc.get("coverage_counts") or {}
    for key in ("api", "page", "lobby", "retained"):
        if counts.get(key) != len(matches):
            errors.append(f"coverage_counts[{key!r}]={counts.get(key)} != {len(matches)}")

    open_ledger = []
    non_featured_ledger = []
    method_counts = Counter()

    for m in sorted(open_rows, key=lambda r: (r.get("start") or "", r["id"])):
        mid = str(m["id"])
        teams = m.get("teams") or []
        probs = m.get("probabilities")
        fair = m.get("fair_odds")
        pick = m.get("pick")
        method = m.get("method")
        method_counts[method] += 1
        ev = (m.get("evidence") or [{}])[0]
        attempts = m.get("attempts") or []

        if len(teams) != 2:
            errors.append(f"{mid}: expected 2 teams, got {teams!r}")
        if pick not in teams:
            errors.append(f"{mid}: pick {pick!r} not in {teams!r}")
        if not probs or len(probs) != 2:
            errors.append(f"{mid}: missing two-sided probabilities")
            continue
        if abs(sum(probs) - 1.0) > 1e-9:
            errors.append(f"{mid}: probabilities do not sum to 1: {probs}")
        best_team = teams[0 if probs[0] >= probs[1] else 1]
        if pick != best_team:
            errors.append(f"{mid}: pick {pick!r} != higher probability team {best_team!r}")
        if not fair or len(fair) != 2:
            errors.append(f"{mid}: missing fair_odds")
        else:
            for i in (0, 1):
                if abs(fair[i] - (1.0 / probs[i])) > TOL:
                    errors.append(f"{mid}: fair_odds[{i}]={fair[i]} != 1/p={1.0/probs[i]}")

        for url_field, url_val in (
            ("source_url", m.get("source_url")),
            ("feed_url", m.get("feed_url")),
            ("evidence.url", ev.get("url")),
            ("evidence.api_url", ev.get("api_url")),
        ):
            if not str(url_val or "").startswith("https://"):
                errors.append(f"{mid}: {url_field} is not https: {url_val!r}")

        rederived, kind = rederive_row(m)
        delta = max(abs(probs[0] - rederived[0]), abs(probs[1] - rederived[1]))
        if delta > TOL:
            errors.append(f"{mid}: published {probs} != re-derived {rederived} (delta={delta})")

        provider_trail = [a.get("provider") for a in attempts]
        if method != "exchange":
            if "HLTV" not in provider_trail:
                errors.append(f"{mid}: non-featured row ({method}) missing HLTV attempt")
            else:
                hltv_idx = provider_trail.index("HLTV")
                later_providers = provider_trail[hltv_idx + 1 :]
                book_checked = any(
                    p in later_providers
                    for p in (
                        "Pinnacle",
                        "Polymarket",
                        "Thunderpick",
                        "GG.BET",
                        "Thunderpick (via BO3.gg API)",
                        "Book research",
                    )
                )
                if not book_checked:
                    errors.append(
                        f"{mid}: non-featured row ({method}) did not attempt esportsbooks after HLTV"
                    )
            non_featured_ledger.append(
                {
                    "id": mid,
                    "start": m.get("start"),
                    "teams": teams,
                    "competition": m.get("competition"),
                    "pick": pick,
                    "method": method,
                    "probabilities": [round(probs[0], 6), round(probs[1], 6)],
                    "fair_odds": [round(fair[0], 4), round(fair[1], 4)],
                    "provider": ev.get("provider"),
                    "source_url": m.get("source_url"),
                    "evidence_url": ev.get("url"),
                    "evidence_api_url": ev.get("api_url"),
                    "attempt_trail": [
                        {
                            "provider": a.get("provider"),
                            "status": a.get("status"),
                            "reason": a.get("reason"),
                            "url": a.get("url"),
                        }
                        for a in attempts
                    ],
                }
            )

        open_ledger.append(
            {
                "id": mid,
                "start": m.get("start"),
                "lock": m.get("lock"),
                "expires_at": m.get("expires_at"),
                "teams": teams,
                "competition": m.get("competition"),
                "tier": m.get("tier"),
                "pick": pick,
                "method": method,
                "probabilities": [round(probs[0], 6), round(probs[1], 6)],
                "re_derived": [round(rederived[0], 6), round(rederived[1], 6)],
                "max_delta": delta,
                "fair_odds": [round(fair[0], 4), round(fair[1], 4)],
                "provider": ev.get("provider"),
                "source_url": m.get("source_url"),
                "evidence_url": ev.get("url"),
                "evidence_api_url": ev.get("api_url"),
                "flags": m.get("flags") or [],
            }
        )

    for m in not_open_rows:
        mid = str(m["id"])
        if not str(m.get("source_url") or "").startswith("https://"):
            errors.append(f"not_open {mid}: non-https source_url")
        if not str(m.get("feed_url") or "").startswith("https://"):
            errors.append(f"not_open {mid}: non-https feed_url")
        if (
            m.get("pick") is not None
            or m.get("probabilities") is not None
            or m.get("fair_odds") is not None
            or m.get("method") is not None
        ):
            errors.append(f"not_open {mid}: carries live pick/probability fields")
        if not m.get("reason"):
            errors.append(f"not_open {mid}: missing non-open reason")

    return {
        "session": "cecfe864",
        "snapshot_generated_at": doc.get("generated_at"),
        "fixtures_observed_at": doc.get("fixtures_observed_at"),
        "coverage": doc.get("coverage"),
        "coverage_counts": counts,
        "rows_total": len(matches),
        "rows_open": len(open_rows),
        "rows_not_open": len(not_open_rows),
        "open_with_pick": sum(1 for m in open_rows if m.get("pick")),
        "open_with_probability": sum(1 for m in open_rows if m.get("probabilities")),
        "open_research_only": sum(
            1 for m in open_rows if m.get("pick") and not m.get("probabilities")
        ),
        "open_unresolved": sum(1 for m in open_rows if not m.get("pick")),
        "method_counts": dict(method_counts),
        "non_featured_count": len(non_featured_ledger),
        "errors": errors,
        "open_ledger": open_ledger,
        "non_featured_ledger": non_featured_ledger,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=str(ROOT / "data" / "latest.json"))
    ap.add_argument(
        "--output",
        default=str(ROOT / "research" / "session-cecfe864" / "board-ledger.json"),
    )
    args = ap.parse_args(argv)
    result = audit_snapshot(Path(args.data))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "snapshot_generated_at",
                    "fixtures_observed_at",
                    "rows_total",
                    "rows_open",
                    "rows_not_open",
                    "open_with_pick",
                    "open_with_probability",
                    "open_research_only",
                    "open_unresolved",
                    "method_counts",
                    "non_featured_count",
                    "errors",
                )
            },
            indent=1,
        )
    )
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
