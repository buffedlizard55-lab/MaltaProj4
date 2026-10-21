"""Idempotent applier for session 2d0a85f2 research output (integration phase).

Applies ONLY dated, sourced research records produced by this session:

* ``data/vrs-anchors.json``  -- roster anchors that let Valve's own
  >=3-shared-player rule resolve a duplicated Valve label when a fixture's HLTV
  page has no lineup yet. Every anchor is re-validated against the official
  standings file at apply time and the apply FAILS CLOSED if the overlap
  arithmetic, the standing/points pair or the official-lineup source check does
  not hold.
* ``data/review-notes.json`` -- sourced findings for the Flagged for Review page
  (start conflict, fixture-identity conflict, evidence-link gap, source
  availability limits, excluded fan vote).

It never writes a probability, a pick or an alias, and it never touches the pick
tiers: anchors only unblock the already-published, pick-only
``research_vrs_single`` tier. Default is a dry run; ``--apply`` writes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import vrs
from scripts.core import norm

ROOT = Path(__file__).resolve().parents[1]
ANCHOR_SRC = ROOT / "research" / "session-2d0a85f2" / "anchors.json"
ANCHOR_DST = ROOT / "data" / "vrs-anchors.json"
NOTES_DST = ROOT / "data" / "review-notes.json"

NOTES = [
    {
        "id": "2d0a85f2-start-conflict-1081597",
        "status": "Needs review — Hotspawn, EGamersWorld and bo3.gg agree on 2026-10-22T11:00:00Z for benched gods vs TitanFlow while HLTV's listings place the pair elsewhere",
        "finding": "Hotspawn fixture 1081597 (CCT Europe 2026 Challengers #8, lower bracket round 3) carries start 2026-10-22T11:00:00Z; EGamersWorld's match page states 22.10.2026 at 11:00 and bo3.gg's match page shows 'Oct 22, 07:00' in its page-local zone, the same instant. HLTV's date-filtered listings observed on 2026-10-21 show the pair at page-local 13:00 and also under the 2026-10-24 filter, i.e. a different instant, which is the mechanical reason the collector's exact pair+UTC-start HLTV gate finds no match and the row carries no HLTV evidence. The row keeps Hotspawn's sourced timestamps; nothing is averaged or adjusted. Research on 2026-10-21 (session 2d0a85f2 receipts R1, R2, R3, R8) found no two-way price for this fixture anywhere: Thunderpick's affiliate rendering shows no line for it while pricing Quintessence vs Ryvex 1.55/2.24 in the same event, EGamersWorld shows the identical 1.8/1.8 placeholder (rejected by policy), GG.BET answers HTTP 403, Pinnacle and Polymarket have no exact pair+start market, and Kalshi's CS2 series has zero open markets.",
        "sources": [
            {"url": "https://www.hotspawn.com/matches/benched-gods-vs-titanflow-cct-europe-2026-challengers-8-1081597", "label": "Hotspawn fixture page (board source of the start time)"},
            {"url": "https://www.hltv.org/matches?selectedDate=2026-10-22", "label": "HLTV listing observed 2026-10-21 (pair at page-local 13:00)"},
            {"url": "https://www.hltv.org/matches?selectedDate=2026-10-24", "label": "HLTV listing observed 2026-10-21 (pair under the 24 Oct filter)"},
            {"url": "https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn", "label": "EGamersWorld match page: 22.10.2026 11:00 and the rejected 1.8/1.8 placeholder"},
            {"url": "https://bo3.gg/matches/benched-gods-vs-titanflow-22-10-2026", "label": "bo3.gg match page: same instant, no Thunderpick line, fixture lineup listed"},
            {"url": "https://bo3.gg/tournaments/cct-europe-2026-challengers-8", "label": "bo3.gg event page: control fixture Quintessence vs Ryvex priced 1.55/2.24"},
        ],
    },
    {
        "id": "2d0a85f2-identity-conflict-1082837",
        "status": "Needs review — the 22:00Z slot of CCT South America 2026 Series #7 is Zetta vs LOS NINOS on Hotspawn and HLTV but Alianza Lima Esports vs Los Niños on bo3.gg and Polymarket",
        "finding": "Hotspawn fixture 1082837 and HLTV match 2399865 agree on Zetta vs LOS NINOS, Bo3, Swiss round 5 (2-2 records), 2026-10-21T22:00:00Z (HLTV prints 18:00 in its page-local zone with a matching countdown). The same 22:00Z slot of the same event is carried by bo3.gg as Alianza Lima Esports vs Los Niños and by Polymarket as a market of that name (1.33x/1.37x at observation). No sourced alias or bracket evidence links 'Zetta' to 'Alianza Lima Esports', so attaching that market price to row 1082837 would be a wrong-game line and is refused. HLTV's betting block for 2399865 contains no numeric two-way odds (a Stake social-casino promo only) and its 75/25 community vote is excluded by project policy; the published research-only pick (Zetta, HLTV #241, blank percentages) therefore remains the only defensible output.",
        "sources": [
            {"url": "https://www.hltv.org/matches/2399865/zetta-vs-los-ninos-cct-2026-south-america-series-7", "label": "HLTV match page: identity, Swiss round 5, no numeric odds, fan vote displayed"},
            {"url": "https://bo3.gg/tournaments/cct-south-america-2026-series-7", "label": "bo3.gg event page: 22:00Z slot listed as Alianza Lima Esports vs Los Niños, no line"},
            {"url": "https://polymarket.com/esports/cs2", "label": "Polymarket CS2 listing: the 22:00Z market of this event names Alianza Lima Esports vs Los Niños"},
        ],
    },
    {
        "id": "2d0a85f2-no-line-dfrag",
        "status": "Needs review — DFRAG Invitational 2026 carries no bookmaker line anywhere this session could read, so two rows stay pick-only with blank percentages",
        "finding": "Rows 1082858 (Ground Zero vs Off Chops, 2026-10-26T03:00:00Z) and 1082860 (FlyQuest vs Staqued, 2026-10-27T03:00:00Z) are LAN fixtures of DFRAG Invitational 2026 (Brisbane). bo3.gg's event page lists all four Hotspawn DFRAG fixtures with no two-way line at all while its own FAQ states rosters are unannounced; Polymarket and Pinnacle have no exact pair+start market (CI attempt ledger of run 39664773335); GG.BET answers HTTP 403; EGamersWorld re-observation failed; Kalshi has zero open CS2 markets. Valve's official standings resolve exactly one side of each pair (Ground Zero #136 878 pts; FlyQuest #86 1093 pts), which is why the published research-only picks exist and why no percentage can be sourced without inventing one.",
        "sources": [
            {"url": "https://bo3.gg/tournaments/dfrag-invitational-2026", "label": "bo3.gg event page: all four fixtures listed with no line"},
            {"url": "https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39664773335", "label": "CI refresh attempt ledger: Polymarket/Pinnacle absent, GG.BET 403, EGW re-observation failed"},
            {"url": "https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=kxcs2game&status=open&limit=200", "label": "Kalshi public API: zero open CS2 game markets at observation"},
        ],
    },
    {
        "id": "2d0a85f2-evidence-link-gap",
        "status": "Needs review — research-only rows carry their HLTV link in hltv_context.source but the published CSV source column is empty for them",
        "finding": "Rows 1082837, 1082858 and 1082860 store their official HLTV match URL in hltv_context.source while their evidence[] list is empty, so the CSV's source column (the column the 'every row must have a source link' requirement is checked against) is blank for exactly those rows. The links exist and are official; they are simply not surfaced where the requirement is verified. Requested fix (REQUESTS.md R-3): render hltv_context.source as the row's identity source in the CSV and tables, labelled as identity evidence, never as a price.",
        "sources": [
            {"url": "https://buffedlizard55-lab.github.io/MaltaProj4/data/matches.csv", "label": "Published CSV: blank source column on the three research-only rows"},
            {"url": "https://buffedlizard55-lab.github.io/MaltaProj4/data/latest.json", "label": "Published snapshot: hltv_context.source holds the HLTV match URLs"},
        ],
    },
    {
        "id": "2d0a85f2-source-availability",
        "status": "Needs review — three price sources are unreadable or empty right now; that is a collection limit, not proof that no line exists",
        "finding": "At 2026-10-21T19:48-19:57Z: GG.BET answers HTTP 403 to the collector after three waits; EGamersWorld listing re-observation fails (403 or no reading); Kalshi's regulated CS2 game series returns an empty open-market list although it traded CS2 games earlier in October (e.g. kxcs2game-26oct171800lnhac, Los Ninos vs Hacha Esports, 66/34 on 2026-10-17). Thunderpick's own page renders no extractable two-way quote for the gap fixtures while its affiliate rendering on bo3.gg shows lines elsewhere. None of these absences is treated as a 50/50 or as a pick; they are published as limitations.",
        "sources": [
            {"url": "https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=kxcs2game&status=open&limit=200", "label": "Kalshi public API: empty open-market list"},
            {"url": "https://kalshi.com/markets/kxcs2game/counterstrike-2-game/kxcs2game-26oct171800lnhac", "label": "Kalshi CS2 market that traded on 2026-10-17 (series is live in principle)"},
            {"url": "https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39664773335", "label": "CI source_checks: GG.BET 403, EGW re-observation errors"},
        ],
    },
]


def _overlap(lineup, roster):
    a = {norm(p) for p in lineup}
    b = {norm(p) for p in roster}
    return len(a & b)


def validate_anchors(payload, standings):
    """Fail closed. Returns (accepted, errors)."""
    accepted, errors = [], []
    for anchor in payload.get("anchors", []):
        team = anchor["team"]
        rows = [r for r in standings["teams"] if norm(r["name"]) == norm(team)]
        if len(rows) < 2:
            errors.append(f"{team}: label is not duplicated in the standings; an anchor is unnecessary")
            continue
        selected = next((r for r in rows if r["standing"] == anchor["valve_standing"]), None)
        if selected is None or selected["points"] != anchor["valve_points"]:
            errors.append(f"{team}: standing/points pair not found in the official file")
            continue
        lineup = anchor["anchor_lineup"]
        overlaps = sorted((_overlap(lineup, r["roster"]), r["standing"]) for r in rows)
        best, others = overlaps[-1], overlaps[:-1]
        if best[1] != anchor["valve_standing"] or best[0] < vrs.ROSTER_OVERLAP:
            errors.append(f"{team}: anchor lineup does not reach {vrs.ROSTER_OVERLAP} shared players with row {anchor['valve_standing']}")
            continue
        if any(o[0] >= vrs.ROSTER_OVERLAP for o in others):
            errors.append(f"{team}: another same-label row also reaches the overlap threshold; anchor ambiguous")
            continue
        if not any(s.get("kind") == "official_hltv_played_match_lineup" for s in anchor["lineup_sources"]):
            errors.append(f"{team}: no official HLTV lineup source; third-party lineup alone is not accepted")
            continue
        accepted.append({**anchor, "overlap_selected": best[0], "overlap_others": [o[0] for o in others]})
    return accepted, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the data files (default: dry run)")
    args = parser.parse_args()

    from datetime import datetime, timezone

    payload = json.loads(ANCHOR_SRC.read_text())
    standings, meta = vrs.vendored(datetime.now(timezone.utc))
    print(f"official standings in use: {meta['file']} (sha256 {meta['sha256'][:12]}…)")
    accepted, errors = validate_anchors(payload, standings)
    if errors:
        for e in errors:
            print("REJECTED:", e)
    print(f"anchors accepted: {len(accepted)} of {len(payload.get('anchors', []))}")

    existing_anchors = json.loads(ANCHOR_DST.read_text()) if ANCHOR_DST.exists() else {"schema_version": 1, "anchors": []}
    merged = {a["team"] + "@" + str(a["valve_standing"]): a for a in existing_anchors.get("anchors", [])}
    for a in accepted:
        merged[a["team"] + "@" + str(a["valve_standing"])] = a
    anchor_doc = {"schema_version": 1, "anchors": [merged[k] for k in sorted(merged)]}

    notes = json.loads(NOTES_DST.read_text())
    have = {n["id"] for n in notes}
    new_notes = [n for n in NOTES if n["id"] not in have]

    if not args.apply:
        print(f"dry run: would write {len(anchor_doc['anchors'])} anchors and append {len(new_notes)} review notes")
        for n in new_notes:
            print("  + note", n["id"])
        return
    ANCHOR_DST.write_text(json.dumps(anchor_doc, indent=2, ensure_ascii=False) + "\n")
    NOTES_DST.write_text(json.dumps(notes + new_notes, indent=2, ensure_ascii=False) + "\n")
    print(f"applied: {ANCHOR_DST.name} ({len(anchor_doc['anchors'])} anchors), {NOTES_DST.name} (+{len(new_notes)} notes)")


if __name__ == "__main__":
    main()
