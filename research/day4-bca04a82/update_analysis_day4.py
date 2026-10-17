#!/usr/bin/env python3
"""Session bca04a82 day-4 content update: final day-3 results + fully priced day-4 semis.

Additive/rewrite edit of data/analysis.json only. Every number below was read from the
named primary source at 2026-10-17T00:00-00:15Z:
  - HLTV match pages 2399412 (Aurora 2-0 9z), 2399413 (BETBOOM 2-1 Legacy),
    2399414 (FURIA vs Aurora semi), 2399415 (Falcons vs BETBOOM semi),
    2395000 (Cologne Major FURIA 2-0 Aurora), 2391758 (Rotterdam Aurora 2-0 FURIA),
    2394975 (Cologne Major BETBOOM 2-0 Falcons), 2398743 (EPL S24 FURIA vs Aurora)
  - Pinnacle guest API sports/12/markets/straight: matchup 1638536356 period-0 ML
    FURIA -125 / Aurora +103 (version 3767145143); matchup 1638595724 period-0 ML
    Falcons -389 / BETBOOM +298 (version 3767145819); both league "CS2 - TP World
    Championship" id 230242, status open
  - Polymarket Gamma API: event 1200431 slug cs2-furia-aur1-2026-10-17 (Match Winner
    market 5778024 outcomePrices 0.525/0.475) and event 1201748 slug
    cs2-fal2-bb3-2026-10-17 (Match Winner market 5787759 outcomePrices 0.795/0.205)
American-odds devig: neg -X -> X/(X+100); pos +Y -> 100/(Y+100); then normalise.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / "data" / "analysis.json"
d = json.loads(p.read_text())

d["reviewed_at"] = "2026-10-17"
d["reviewed_at_utc"] = "2026-10-17T00:20:00Z"

# ---------------------------------------------------------------- day-3 results
r = d["day_three_results"]
r["note"] = (
    "Both group deciders are final, read from the HLTV match pages on 17 October: "
    "Aurora 2-0 9z (match 2399412) and BETBOOM 2-1 Legacy (match 2399413). Group A is "
    "won by Falcons (2-0) with Aurora second (2-1); Group B is won by FURIA (2-0) with "
    "BETBOOM second (2-1). The semi-final pairings are therefore FURIA vs Aurora "
    "(HLTV 2399414, 14:00 UTC on 17 October) and Falcons vs BETBOOM (HLTV 2399415, "
    "17:00 UTC on 17 October)."
)
r["matches"][0]["flag"] = (
    "Map scores, halves, veto, ratings and the demo id are HLTV values from the match "
    "page, re-read 17 October 2026, not this project's calculation. The Cache and "
    "Inferno scores and both half-time splits are now verified on HLTV directly; the "
    "earlier draft attributed the Inferno 13-4 to dust2.com.br and EGamersWorld only."
)
r["matches"][0]["detail"] = (
    "The day-one upset reversed. Veto: Aurora removed Ancient, 9z removed Anubis, "
    "Aurora picked Cache, 9z picked Inferno, Aurora removed Nuke, 9z removed Dust2, "
    "Mirage left over. Aurora won their own Cache pick 13-11 (halves 8:4, 5:7) and "
    "closed 9z's Inferno pick 13-4 (halves 9:3, 4:1) - the same map they lost 1-13 on "
    "day one. Top ratings on the HLTV match page (Rating 3.0, re-read 17 October 2026): "
    "kyxsan 33-20 K-D, 92.7% KAST, 1.45 and Jimpphat 31-18 with 1.31, the two summer "
    "signings leading the server. Aurora advance to semi-final 1 against FURIA (HLTV "
    "2399414); 9z are eliminated. Demo: HLTV download 112837. This board priced the "
    "decider at roughly 69.5% Aurora from the exchange line with the VRS model at "
    "68.0%, and the day-three guidance offered 9z only as a need-ground swing: the "
    "favourite won, so the swing would have cost the fixture's 7 tier-S points - the "
    "worked example of why the strategy rules cap contrarian exposure per slate."
)
r["matches"].append({
    "winner": "BETBOOM",
    "loser": "Legacy",
    "score": "2-1",
    "maps": (
        "Nuke 16-13 in overtime (halves 4:8; 8:4, overtime 4:1), Dust2 11-13 "
        "(halves 7:5; 4:8), Mirage 13-11 (halves 7:5; 6:6)"
    ),
    "stage": "Group B decider match",
    "match_url": "https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026",
    "report_url": "https://www.hltv.org/results?event=8932",
    "detail": (
        "BETBOOM win Group B. The veto ran: BETBOOM removed Inferno, Legacy removed "
        "Anubis, BETBOOM picked Nuke, Legacy picked Dust2, BETBOOM removed Cache, "
        "Legacy removed Ancient, Mirage left over. BETBOOM lost Nuke's first half 4:8, "
        "leveled the second 8:4 and took the map 16-13 in overtime (4:1); Legacy "
        "flipping Dust2 13-11 (halves 7:5, 4:8) forced the decider, where BETBOOM led "
        "7:5 at half-time and closed Mirage 13-11. Top ratings on the HLTV match page "
        "(Rating 3.0, read 17 October 2026): Magnojez 62-50 K-D, 82.8 ADR, 1.17; "
        "d1Ledez 55-50 with 1.08; Boombl4 49-51 with 1.06; S1ren 44-47 with 1.02. The "
        "match began 17:00 UTC (HLTV displays 13:00, UTC-4) and the overtime finish "
        "pushed the end to roughly 19:30 UTC - the rest deficit BETBOOM carry into "
        "semi-final 2. Demo: HLTV download 112853. BETBOOM also beat FURIA's group "
        "conquered side note: this was BETBOOM's third three-map series of the event "
        "(they lost 0-2 to FURIA on day one, beat PARIVISION 2-1 on day two)."
    ),
    "flag": (
        "Map scores, halves, overtime, veto, ratings and the demo id are HLTV values "
        "from the match page, not this project's calculation. The finish time is "
        "derived from the 17:00 UTC start plus the three-map runtime and is approximate."
    ),
})

# ---------------------------------------------------------------- day-4 guidance
g = d["day_four_guidance"]
g["card"] = (
    "Semi-final day: both semi-finals priced by Pinnacle and Polymarket side by side, "
    "the contrarian side of each, and why the tired dog is not automatically a value buy."
)
g["summary"] = (
    "Semi-final day in Malta. Both semi-finals are now priced by two independent "
    "sources each: Pinnacle's public matchup lines and Polymarket's event markets, "
    "read around 00:10 UTC on 17 October, with the de-margining arithmetic shown on "
    "each card. Neither semi-final is on the Hotspawn CS2 feed - the full scheduled "
    "fixture feed was re-read chunk by chunk at 00:15 UTC and contains no Thunderpick "
    "World Championship main-event match, only the South American Series #1 qualifier - "
    "so the pick board carries no row for either semi-final and Hotspawn's crowd "
    "percentages play no part in this section. The third-place match and the best-of-"
    "five grand final (both 18 October) are priced by neither book yet and stay in the "
    "limitations. Scoring on Hotspawn awards a fixed number of points per correct pick, "
    "so the leaderboard-optimal choice is always the higher-probability team; the "
    "contrarian column exists for the cases where you judge the favourite to be wrong, "
    "not because going against the crowd is worth anything by itself. Rest figures are "
    "schedule observations, not measured fatigue effects: FURIA had about one more day "
    "off than Aurora and played one map fewer (5 to 6), while BETBOOM played eight maps "
    "including an overtime Nuke decider against Falcons' five maps and roughly one more "
    "day of rest."
)

semi1 = {
    "label": "FURIA vs Aurora",
    "event": "Thunderpick World Championship 2026, semi-final 1 (best of 3, Malta)",
    "teams": ["FURIA", "Aurora"],
    "points": [1829, 1716],
    "now_listed": False,
    "timing": (
        "HLTV's machine-readable start is 2026-10-17T14:00:00Z (HLTV displays 10:00 "
        "because this event's clock is UTC-4; the match page showed a 14h 10m countdown "
        "at the 17 October ~00:10 UTC read). Semi-final, best of 3, LAN; maps TBA."
    ),
    "market": {
        "label": "Pinnacle and Polymarket, read 17 Oct ~00:10 UTC",
        "detail": (
            "Pinnacle series moneyline FURIA -125 / Aurora +103 - de-margined 53.0% / "
            "47.0% (4.8% overround; fair line about -113 / +113). Polymarket Match "
            "Winner (market 5778024) FURIA 0.525 / Aurora 0.475, last trade 0.53, "
            "$158,628 liquidity. Two independent books agree within half a point: FURIA "
            "a slight favourite, effectively a coin flip."
        ),
        "url": "https://gamma-api.polymarket.com/markets/5778024",
        "link_label": "Polymarket Match Winner market ↗",
    },
    "why": (
        "Both books price this as a near coin flip with a slight FURIA edge, and our "
        "stale Valve-file model (62.2% FURIA) is the outlier - the market does not "
        "share that conviction. Three verified readings cut the other way: HLTV's live "
        "VRS now ranks Aurora #5 (1848 pts) above FURIA #6 (1826 pts), a 22-point gap "
        "the 5 October Valve repository file does not contain; Aurora won the most "
        "recent meeting (ESL Pro League Season 24, 6 October, 2-1: Nuke 9-13, Mirage "
        "9-13, Dust2 13-8); and Aurora answered their day-one upset by sweeping NIP and "
        "9z in Malta while FURIA needed three maps twice. The honest case for FURIA: "
        "group-winner form (2-0, 2-1), a one-map lighter path (5 maps to Aurora's 6) "
        "and roughly one extra rest day (last played 15 October, against Aurora's "
        "16 October 14:00 UTC decider). Head-to-head, re-verified map by map on 17 "
        "October: all-time FURIA lead 18-15 with 5 overtimes, but 2026 is split 2-2 - "
        "Aurora won the most recent meeting and BLAST Open Rotterdam in March 2-0 "
        "(Dust2 16-14 in overtime, Inferno 13-6), while FURIA won the IEM Cologne "
        "Major in June 2-0 (Nuke 13-4, Dust2 13-9) and the Esports World Cup in August "
        "2-1. An earlier working note had the Cologne Major the wrong way round; the "
        "match page (HLTV 2395000) confirms FURIA won it. Map-level prices lean Aurora "
        "on map 1 (Polymarket 0.525 against 0.475) and FURIA on map 2 (0.545 against "
        "0.455; Pinnacle's map-2 moneyline has FURIA -134 / Aurora +110), and the "
        "games total leans a 2-0 sweep (Polymarket Under 2.5 games at 0.53). Pick: "
        "FURIA, following the market line. Contrarian angle, published rather than "
        "recommended: Aurora at about 47% is the cheapest differentiation available if "
        "you weigh the live VRS rank and the most recent head-to-head above the "
        "bookmakers' 53 - but you would be fading two independent books and the "
        "group-winner form line."
    ),
    "hltv_url": "https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026",
    "standings_url": "https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md",
    "sources": [
        {"label": "Pinnacle CS2 straight markets (matchup 1638536356, period 0, version 3767145143)",
         "url": "https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight"},
        {"label": "Polymarket event 1200431 (Match Winner, map, handicap and totals markets)",
         "url": "https://gamma-api.polymarket.com/events?slug=cs2-furia-aur1-2026-10-17"},
        {"label": "HLTV: Aurora beat 9z to reach this semi-final",
         "url": "https://www.hltv.org/news/45736/aurora-beat-9z-to-secure-third-consecutive-top-four-appearance"},
        {"label": "HLTV: FURIA came back to beat Legacy 2-1",
         "url": "https://www.hltv.org/matches/2399411/legacy-vs-furia-thunderpick-world-championship-2026"},
        {"label": "HLTV: FURIA vs Aurora, 6 Oct 2026, EPL Season 24 (Aurora 2-1)",
         "url": "https://www.hltv.org/matches/2398743/furia-vs-aurora-esl-pro-league-season-24"},
        {"label": "HLTV: Aurora vs FURIA, 20 Jun 2026, IEM Cologne Major (FURIA 2-0)",
         "url": "https://www.hltv.org/matches/2395000/aurora-vs-furia-iem-cologne-major-2026"},
    ],
}

semi2 = {
    "label": "Falcons vs BETBOOM",
    "event": "Thunderpick World Championship 2026, semi-final 2 (best of 3, Malta)",
    "teams": ["Falcons", "BETBOOM"],
    "points": [1843, 1596],
    "now_listed": False,
    "timing": (
        "HLTV's machine-readable start is 2026-10-17T17:00:00Z (HLTV displays 13:00, "
        "UTC-4; the match page showed a 17h 11m countdown at the ~00:10 UTC read). "
        "Opponent confirmed: BETBOOM beat Legacy 2-1 in the Group B decider on 16 "
        "October. Semi-final, best of 3, LAN; maps TBA."
    ),
    "market": {
        "label": "Pinnacle and Polymarket, read 17 Oct ~00:10 UTC",
        "detail": (
            "Pinnacle series moneyline Falcons -389 / BETBOOM +298 - de-margined 76.0% "
            "/ 24.0% (4.7% overround; fair line about -326 / +317). Polymarket Match "
            "Winner (market 5787759) Falcons 0.795 / BETBOOM 0.205, $60,484 liquidity, "
            "$12,272 traded. Both books make Falcons a heavy favourite; the exchange is "
            "about 3.5 points stronger on Falcons than the bookmaker."
        ),
        "url": "https://gamma-api.polymarket.com/markets/5787759",
        "link_label": "Polymarket Match Winner market ↗",
    },
    "why": (
        "Every checkable input points the same way, so this is not a contrarian pick: "
        "the market (76.0% bookmaker, 79.5% exchange), our stale Valve-file model "
        "(73.9%) and the schedule audit all favour Falcons. Falcons won Group A at 2-0 "
        "(NIP, 9z) and carry five maps and about two days of rest into this match. "
        "BETBOOM played eight maps - including an overtime Nuke decider against Legacy "
        "that ended around 19:30 UTC on 16 October - and turn around in about 22 hours; "
        "the dog is also the tired side, which is exactly why buying BETBOOM here would "
        "be contrarian for the wrong reason. The real evidence for the dog, published "
        "honestly: BETBOOM own the only head-to-head, having swept Falcons 2-0 at the "
        "IEM Cologne Major on 12 June (Ancient 13-10, Nuke 13-11), and they enter with "
        "momentum from the overtime decider plus ESL Pro League Season 24 wins over "
        "Aurora 2-1 and 9z 2-0. Falcons, meanwhile, lost 0-2 to Spirit at EPL S24 one "
        "week ago. HLTV's live VRS has Falcons #4 (1880 pts) against BETBOOM #10 "
        "(1619 pts) - same direction as the market, with a wider gap. Map-level prices: "
        "Polymarket map 1 Falcons 0.68 / BETBOOM 0.32, map 2 Falcons 0.725 / 0.275 - "
        "the market expects Falcons to open up a map lead. Pick: Falcons, on the market "
        "line, with the head-to-head sweep recorded as the strongest known counter-"
        "argument rather than hidden."
    ),
    "hltv_url": "https://www.hltv.org/matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026",
    "standings_url": "https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md",
    "sources": [
        {"label": "Pinnacle CS2 straight markets (matchup 1638595724, period 0, version 3767145819)",
         "url": "https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight"},
        {"label": "Polymarket event 1201748 (Match Winner and map markets)",
         "url": "https://gamma-api.polymarket.com/events?slug=cs2-fal2-bb3-2026-10-17"},
        {"label": "HLTV: BETBOOM beat Legacy 2-1 in the Group B decider",
         "url": "https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026"},
        {"label": "HLTV: Falcons 2-1 9z to top Group A",
         "url": "https://www.hltv.org/news/45728/falcons-secure-playoff-berth-at-twc-2026"},
        {"label": "HLTV: Falcons vs BETBOOM, 12 Jun 2026, IEM Cologne Major (BETBOOM 2-0)",
         "url": "https://www.hltv.org/matches/2394975/falcons-vs-betboom-iem-cologne-major-2026"},
    ],
}

g["not_listed"] = [semi1, semi2]

g["unverified"] = [
    "Neither semi-final is on the Hotspawn CS2 scheduled feed: all nine chunks of the "
    "fixture API were re-read at 00:15 UTC on 17 October and the only Thunderpick World "
    "Championship entries are the South American Series #1 qualifiers (competition "
    "33804). The board therefore publishes no Hotspawn-tier pick for either semi-final; "
    "the prices in this section are research content, not board rows, and discovery "
    "stays automatic in case Hotspawn adds the playoff fixtures.",
    "The third-place match (9z vs Legacy, HLTV 2399416, about 11:30 UTC on 18 October) "
    "and the grand final (HLTV 2399417, best of five, about 15:00 UTC on 18 October) "
    "are priced by neither book at the final read: Pinnacle's CS2 matchup list contains "
    "no such fixtures and a Polymarket slug search for the third-place match returned no "
    "event. They stay unpriced until the books open them, which cannot happen before the "
    "semi-finals conclude.",
    "Pinnacle's public guest API does not expose a price-change timestamp; each line is "
    "a single observation at the read time, version-stamped (3767145143 and 3767145819) "
    "but not a price history. One bookmaker is not consensus, and Pinnacle's league "
    "label for this event is 'CS2 - TP World Championship' (id 230242).",
    "Polymarket's semi-final 1 market tightened during the evening: liquidity grew from "
    "$10,151 at 19:35 UTC on 16 October to $158,628 at the 00:00 UTC read, with the "
    "FURIA price moving 0.52 to 0.525. The published line is the later read; the earlier "
    "read is retained in the session receipts.",
    "HLTV's on-page win-probability forecast is rendered client-side and was not "
    "machine-readable at the final read, so no HLTV forecast percentage is published. "
    "What the match pages do expose server-side - the VRS points forecast boxes - is "
    "published instead: semi 1 FURIA 1826 (#6) vs Aurora 1848 (#5), semi 2 Falcons 1880 "
    "(#4) vs BETBOOM 1619 (#10). An earlier draft of this page carried an unverified "
    "'FURIA 26.5% / Aurora 73.5%' forecast figure; it is withdrawn and replaced with the "
    "verified points boxes.",
    "Map-level prices (Polymarket map-winner markets, Pinnacle period moneylines) are "
    "quotes on single maps, not series probabilities, and are published only as context "
    "on the cards. Pinnacle's period-1 (map-1) moneylines were not captured for either "
    "semi at the final read.",
    "Semi-final start times are HLTV's machine-readable starts (14:00 and 17:00 UTC on "
    "17 October), cross-checked against the live countdowns on the match pages at read "
    "time. Hotspawn machine-readable times govern if the fixtures are ever listed.",
    "Rest and map-load figures are schedule arithmetic from HLTV start times, not "
    "measured fatigue data. FURIA: 5 maps, last played 15 October. Aurora: 6 maps, last "
    "played 16 October 14:00 UTC. Falcons: 5 maps, last played 15 October. BETBOOM: 8 "
    "maps, last played 16 October 17:00 UTC with an overtime finish.",
    "Valve's standings file is dated 2026-10-05 (commit eec4853), which predates this "
    "week's results. Every model percentage here is a comparison beside market lines, "
    "never a market price and never an override of one.",
    "Two Valve-standings readings disagree on the FURIA-Aurora direction, and both are "
    "now verified rather than conflicting reports: the Valve repository file (5 October, "
    "pre-event) puts FURIA 1829 at #7 above Aurora 1716 at #9, which is what our "
    "reproducible model uses for its 62.2% FURIA line, while HLTV's live VRS forecast "
    "box on match 2399414 shows Aurora 1848 at #5 above FURIA 1826 at #6. The market "
    "(53.0/47.0 and 52.5/47.5) sits far closer to the live ranking than to either "
    "model-era file; the board treats the market as the primary line for this fixture "
    "and publishes both model readings as labelled context.",
    "Aurora's roster has been unchanged since 8 July 2026, so no onboarding, stand-in "
    "or rest factor is available for day four; anyone reasoning from a 'recent Aurora "
    "roster change' is reasoning from a change that happened three months ago.",
]

p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("analysis.json updated")
print("day_three_results matches:", len(r["matches"]))
print("day_four_guidance not_listed cards:", len(g["not_listed"]))
print("day_four_guidance unverified items:", len(g["unverified"]))
