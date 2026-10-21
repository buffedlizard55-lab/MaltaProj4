"""Idempotent applier for session 5ed35e72's sourced research records.

Adds, only when absent:

* the two label mappings in ``data/identities.json`` whose primary sources were
  read on 2026-10-21 (kept here as well so a fresh checkout can reproduce them);
* one rejected EGamersWorld listing (the identical 1.8/1.8 placeholder pair on
  Zetta vs LOS NINOS) in ``data/book-receipts.json``;
* three findings for the Flagged for Review page in ``data/review-notes.json``.

Running it twice changes nothing. It never writes a probability, never edits an
existing record and never touches a published page.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CYBERSHOKE = {
    "canonical": "ex-CYBERSHOKE",
    "names": ["ex-CYBERSHOKE", "CYBERSHOKE Esports"],
    "source": "https://www.hltv.org/matches/2399839/ex-cybershoke-vs-blinkdagger-winline-mpkbk-cis-lan-season-9",
    "additional_source": "https://gamma-api.polymarket.com/events/1224206",
    "basis": (
        "Label mapping only, anchored on the exact opponent pair and the exact UTC start, never on the team "
        "name alone. Hotspawn fixture 1082762 lists ex-CYBERSHOKE vs BlinkDagger in CIS LAN Championship #9 at "
        "2026-10-21T15:00:00Z. HLTV match 2399839 lists ex-CYBERSHOKE vs BlinkDagger with the same exact opponent "
        "pair and the same 15:00Z start; HLTV's team page 14106 carries the label ex-CYBERSHOKE. Liquipedia's CIS "
        "LAN Championship #9 page labels that opening Group C slot CYBERSHOKE Esports vs BlinkDagger and links the "
        "team page CYBERSHOKE_Esports. Polymarket event 1224206 names the same fixture CYBERSHOKE Esports vs "
        "BlinkDagger with gameStartTime 2026-10-21T15:00:00Z, the same UTC start as the Hotspawn row. Four sources "
        "agree on the match, so only one club can occupy that slot. Main squad only: the separately listed "
        "CYBERSHOKE Prospects (academy) and a bare CYBERSHOKE label are deliberately not mapped, and no roster "
        "continuity is inferred."
    ),
}

FLACONS = {
    "canonical": "flacons",
    "names": ["flacons", "Team flacons"],
    "source": "https://www.hltv.org/matches/2399840/upgrade-vs-flacons-winline-mpkbk-cis-lan-season-9",
    "additional_source": "https://gamma-api.polymarket.com/events/1224207",
    "basis": (
        "Label mapping only, anchored on the exact opponent pair and the exact UTC start. Hotspawn fixture 1082763 "
        "lists UPGRADE vs flacons in CIS LAN Championship #9 at 2026-10-21T15:00:00Z. HLTV match 2399840 lists "
        "UPGRADE vs flacons with the same exact opponent pair and the same 15:00Z start, and HLTV's team page 13932 "
        "carries the label flacons. Liquipedia's CIS LAN Championship #9 page labels the same Group C opening slot "
        "UPGRADE vs Team flacons, and Polymarket event 1224207 names it UPGRADE vs Team flacons with gameStartTime "
        "2026-10-21T15:00:00Z. Four sources agree on the match, so the only difference is the Team prefix. No other "
        "club in that event is called flacons, and no roster continuity is inferred."
    ),
}

REJECTION = {
    "fixture_id": "1082837",
    "teams": ["Zetta", "LOS NINOS"],
    "url": "https://egamersworld.com/counterstrike/match/0U32SId-H/zetta-vs-los-ninos-Wi0PWrNpb",
    "observed_at": "2026-10-21T13:03:00Z",
    "displayed": [1.8, 1.8],
    "reason": (
        "Identical default odds (1.8/1.8) on both sides of the listing, with no book name and no price-update "
        "timestamp: a placement placeholder, not a two-sided market line. Read directly during the "
        "2026-10-21T12:55-13:10Z window (minute-precision timestamp). Publishing it would fabricate a 50/50, so the "
        "row keeps its research-only pick (Zetta, HLTV world #241) and publishes no percentage."
    ),
}

NOTES = [
    {
        "id": "publication-outage-2026-10-21",
        "status": "Fixed \u2014 scheduled publication restored",
        "finding": (
            "Every scheduled refresh on main from 2026-10-20T13:02Z to 2026-10-21T10:00Z failed in the unit-test step, "
            "so the newest published build stayed at 2026-10-20T07:44:51Z (96 rows) for 29 hours and every open pick "
            "on the site aged past its eight-hour evidence window. Reproduced locally: three tests in "
            "tests/test_session_133fe7ca.py built a fixture whose start is 2026-10-20T12:00Z and then called the pick "
            "tiers with the wall clock, so after that start the row was correctly not_open and no pick was applied. The "
            "collector was never at fault. The tests now pin their own observation instant (2026-10-19T04:30Z, when the "
            "Sangal book listing was read) and assert the row is open first; 440 tests pass on main's code plus this fix."
        ),
        "sources": [
            {"url": "https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39581284152",
             "label": "Failed scheduled run 2026-10-21T10:00Z (unit-test step)"},
            {"url": "https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39427081979",
             "label": "First failed scheduled run 2026-10-20T13:02Z"},
            {"url": "https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json",
             "label": "Live build receipt (stuck at 2026-10-20T07:44:51Z)"},
        ],
    },
    {
        "id": "identity-cis-lan-2026-10-21",
        "status": "Needs review \u2014 label mapping verified on fixture parity",
        "finding": (
            "Two open Hotspawn fixtures had no pick only because the exchange's team labels differ from the feed's. "
            "Hotspawn 'ex-CYBERSHOKE' is Polymarket/Liquipedia 'CYBERSHOKE Esports' (fixture 1082762) and Hotspawn "
            "'flacons' is Polymarket/Liquipedia 'Team flacons' (fixture 1082763). Both mappings are anchored on the "
            "exact opponent pair and the exact 2026-10-21T15:00:00Z start across HLTV's match page, HLTV's team page, "
            "Liquipedia's CIS LAN Championship #9 page and the Polymarket event. After registering them the scheduled "
            "refresh prices both rows from the exchange (82.0/18.0 and 95.5/4.5) instead of leaving them blank; a "
            "mapping only ever reuses an existing line for the same pair and start. Academy and bare labels are "
            "excluded. A manual reviewer may still want to confirm that the 'ex-' prefix reflects the same club."
        ),
        "sources": [
            {"url": "https://www.hltv.org/matches/2399839/ex-cybershoke-vs-blinkdagger-winline-mpkbk-cis-lan-season-9",
             "label": "HLTV match: ex-CYBERSHOKE vs BlinkDagger, 15:00Z"},
            {"url": "https://www.hltv.org/team/14106/ex-cybershoke",
             "label": "HLTV team 14106 (ex-CYBERSHOKE)"},
            {"url": "https://liquipedia.net/counterstrike/CIS_LAN_Championship/9",
             "label": "Liquipedia CIS LAN #9 (CYBERSHOKE Esports vs BlinkDagger; UPGRADE vs Team flacons)"},
            {"url": "https://gamma-api.polymarket.com/events/1224206",
             "label": "Polymarket event 1224206 (CYBERSHOKE Esports vs BlinkDagger, 15:00Z)"},
            {"url": "https://www.hltv.org/matches/2399840/upgrade-vs-flacons-winline-mpkbk-cis-lan-season-9",
             "label": "HLTV match: UPGRADE vs flacons, 15:00Z"},
            {"url": "https://gamma-api.polymarket.com/events/1224207",
             "label": "Polymarket event 1224207 (UPGRADE vs Team flacons, 15:00Z)"},
        ],
    },
    {
        "id": "unresolved-zetta-2026-10-21",
        "status": "Unresolved \u2014 research-only pick, no percentage",
        "finding": (
            "Fixture 1082837 (Hotspawn Zetta vs LOS NINOS, CCT South America Series 7, 2026-10-21T22:00:00Z) is the one "
            "open match on the 12:47Z board with no published percentage. HLTV lists the same pair at the same start "
            "and ranks Zetta #241 with LOS NINOS unranked, which supports a research pick only. No accessible two-way "
            "line exists: EGamersWorld serves the identical 1.8/1.8 placeholder pair, Pinnacle and the GG.BET adapter "
            "had no listing, and Valve's global standings do not list LOS NINOS, so the originated model line cannot be "
            "computed. Polymarket does carry an event at exactly 22:00Z, but it is labelled 'Alianza Lima Esports vs "
            "Los Ni\u00f1os' (event 1227336). No primary source connects Alianza Lima Esports to Zetta, and the two "
            "labels cannot both describe one side of the same match, so the market was deliberately not used. That is "
            "the whole limitation: the pick is ranked-order evidence and carries no probability."
        ),
        "sources": [
            {"url": "https://www.hotspawn.com/matches/zetta-vs-los-ninos-cct-south-america-2026-series-7-1082837",
             "label": "Hotspawn fixture 1082837"},
            {"url": "https://www.hltv.org/betting/analytics/2399865/zetta-vs-los-ninos-cct-2026-south-america-series-7",
             "label": "HLTV analytics: Zetta #241, LOS NINOS unranked"},
            {"url": "https://egamersworld.com/counterstrike/match/0U32SId-H/zetta-vs-los-ninos-Wi0PWrNpb",
             "label": "EGamersWorld listing (1.8/1.8 placeholder)"},
            {"url": "https://gamma-api.polymarket.com/events/1227336",
             "label": "Polymarket event 1227336 (Alianza Lima Esports vs Los Ni\u00f1os, 22:00Z)"},
        ],
    },
]


def _read(rel):
    return json.loads((ROOT / rel).read_text())


def _write(rel, doc):
    (ROOT / rel).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def main():
    changes = {"aliases_added": 0, "rejections_added": 0, "notes_added": 0}

    identities = _read("data/identities.json")
    have = {a["canonical"] for a in identities["aliases"]}
    for entry in (CYBERSHOKE, FLACONS):
        if entry["canonical"] not in have:
            identities["aliases"].append(entry)
            changes["aliases_added"] += 1
    if changes["aliases_added"]:
        identities["reviewed_at"] = "2026-10-21"
        _write("data/identities.json", identities)

    receipts = _read("data/book-receipts.json")
    if not any(r.get("fixture_id") == REJECTION["fixture_id"]
               and r.get("displayed") == REJECTION["displayed"]
               for r in receipts.get("rejected_listings", [])):
        receipts.setdefault("rejected_listings", []).append(REJECTION)
        changes["rejections_added"] += 1
        _write("data/book-receipts.json", receipts)

    notes = _read("data/review-notes.json")
    known = {n["id"] for n in notes}
    for note in NOTES:
        if note["id"] not in known:
            notes.append(note)
            changes["notes_added"] += 1
    if changes["notes_added"]:
        _write("data/review-notes.json", notes)

    print(json.dumps(changes, indent=1))
    return changes


if __name__ == "__main__":
    main()
