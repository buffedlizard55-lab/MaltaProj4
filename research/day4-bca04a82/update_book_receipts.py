#!/usr/bin/env python3
"""Append day-4 semi-final market receipts (session bca04a82, 2026-10-17T00:05Z).

Four receipts, all read line-by-line from the operator APIs:
  Pinnacle matchup 1638536356 (FURIA vs Aurora, period 0 ML, version 3767145143)
  Pinnacle matchup 1638595724 (Falcons vs BB Team, period 0 ML, version 3767145819)
  Polymarket market 5778024 (event 1200431, cs2-furia-aur1-2026-10-17)
  Polymarket market 5787759 (event 1201748, cs2-fal2-bb3-2026-10-17)
Pinnacle American odds are converted to decimal for the odds field:
  -125 -> 1.800, +103 -> 2.030, -389 -> 1.257, +298 -> 3.980.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / "data" / "book-receipts.json"
r = json.loads(p.read_text())

r["collected_by"] = "sessions 2e920ea8 and bca04a82"
r["collected_at"] = "2026-10-17T00:20:00Z"
r["note"] = (
    "Researched bookmaker listing receipts for fixtures the automated ladder "
    "cannot price (session 2e920ea8, 2026-10-16) plus the two Thunderpick "
    "World Championship semi-finals (session bca04a82, 2026-10-17), which have "
    "no Hotspawn fixture at all and therefore no board row. Each receipt is a "
    "dated observation of a two-way line from the operator's own API, verified "
    "against the HLTV match page (exact opponent pair, UTC start, best-of) "
    "before publication. Probabilities are never hand-entered: bookmaker "
    "overround is removed by normalising the implied probabilities, and "
    "exchange prices are normalised by their own sum."
)

PIN_URL = "https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight"
PIN_MATCHUPS = "https://guest.api.arcadia.pinnacle.com/0.1/sports/12/matchups?withSpecials=false"

r["receipts"].append({
    "provider": "Pinnacle guest esports API (bookmaker moneyline)",
    "id": "pin-1638536356-period0-ml-v3767145143",
    "fixture_id": "hltv-2399414 (no Hotspawn fixture: TWC semi-final 1 is absent from the Hotspawn scheduled feed, verified across all 9 feed chunks 2026-10-17T00:15Z)",
    "source_teams": ["FURIA", "Aurora"],
    "team_aliases": [["FURIA"], ["Aurora Gaming"]],
    "alias_sources": ["Pinnacle home/away team labels", "HLTV match page 2399414 team names"],
    "start": "2026-10-17T14:00:00Z",
    "best_of": 3,
    "odds": [1.800, 2.030],
    "observed_at": "2026-10-17T00:05:00Z",
    "url": PIN_URL,
    "api_url": PIN_URL,
    "event": "CS2 - TP World Championship (Pinnacle league id 230242)",
    "identity_evidence": [
        {"label": "Pinnacle matchup 1638536356: home FURIA / away Aurora, rotationNumber 14046, startTime 2026-10-17T14:00:00Z, league 'CS2 - TP World Championship' id 230242",
         "url": PIN_MATCHUPS},
        {"label": "HLTV match 2399414: FURIA vs Aurora, Thunderpick World Championship 2026, semi-final, Bo3 LAN, 17 Oct 10:00 (UTC-4 display)",
         "url": "https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026"},
    ],
    "corroboration": [
        {"label": "De-margined probabilities: FURIA 53.0% / Aurora 47.0% (implied 0.5556 + 0.4926 = 1.0482 overround, 4.82%); fair decimal line 1.887 / 2.127",
         "url": PIN_URL},
        {"label": "Polymarket Match Winner market 5778024 prices the same series FURIA 0.525 / Aurora 0.475 (last trade 0.53) - agrees within 0.5 points after de-vig",
         "url": "https://gamma-api.polymarket.com/markets/5778024"},
        {"label": "Pinnacle market record: period 0, key 's;0;m', status open, cutoff 2026-10-17T14:00:00Z, maxRiskStake 5000, version 3767145143; period-2 (map-2) moneyline version 3767146007 read as FURIA -134 / Aurora +110",
         "url": PIN_URL},
    ],
    "limitation": "Pinnacle's public guest API exposes no price-change timestamp; single observation, version-stamped. One bookmaker is not consensus. Name-collision trap checked: matchup 1638484900 is 'FURIA vs Cloud9' in LoL Worlds Play-In and a '9z vs FURIA' row exists in Rainbow Six - this receipt is gated on league id 230242 plus the exact 14:00Z start.",
})

r["receipts"].append({
    "provider": "Pinnacle guest esports API (bookmaker moneyline)",
    "id": "pin-1638595724-period0-ml-v3767145819",
    "fixture_id": "hltv-2399415 (no Hotspawn fixture: TWC semi-final 2 is absent from the Hotspawn scheduled feed, verified across all 9 feed chunks 2026-10-17T00:15Z)",
    "source_teams": ["Falcons", "BetBoom Team"],
    "team_aliases": [["Falcons", "Team Falcons"], ["BetBoom Team", "BB Team", "BETBOOM"]],
    "alias_sources": ["Pinnacle home/away team labels ('BB Team')", "data/identities.json BetBoom register", "HLTV match page 2399415 team names"],
    "start": "2026-10-17T17:00:00Z",
    "best_of": 3,
    "odds": [1.257, 3.980],
    "observed_at": "2026-10-17T00:05:00Z",
    "url": PIN_URL,
    "api_url": PIN_URL,
    "event": "CS2 - TP World Championship (Pinnacle league id 230242)",
    "identity_evidence": [
        {"label": "Pinnacle matchup 1638595724: home Falcons / away BB Team, rotationNumber 14048, startTime 2026-10-17T17:00:00Z, league 'CS2 - TP World Championship' id 230242",
         "url": PIN_MATCHUPS},
        {"label": "HLTV match 2399415: Falcons vs BETBOOM, Thunderpick World Championship 2026, semi-final, Bo3 LAN, 17 Oct 13:00 (UTC-4 display)",
         "url": "https://www.hltv.org/matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026"},
    ],
    "corroboration": [
        {"label": "De-margined probabilities: Falcons 76.0% / BETBOOM 24.0% (implied 0.7955 + 0.2513 = 1.0468 overround, 4.68%); fair decimal line 1.316 / 4.166",
         "url": PIN_URL},
        {"label": "Polymarket Match Winner market 5787759 prices the same series Falcons 0.795 / BETBOOM 0.205 - agrees within 3.5 points after de-vig, same direction",
         "url": "https://gamma-api.polymarket.com/markets/5787759"},
        {"label": "Pinnacle market record: period 0, key 's;0;m', status open, cutoff 2026-10-17T17:00:00Z, maxRiskStake 5000, version 3767145819",
         "url": PIN_URL},
    ],
    "limitation": "Pinnacle lists the away team as 'BB Team', an alias mapped to BetBoom Team through the verified identity register (betboom.team is the organisation's own site; HLTV match 2399415 confirms the pairing). Pinnacle's guest API exposes no price-change timestamp; single observation, version-stamped. One bookmaker is not consensus.",
})

r["receipts"].append({
    "provider": "Polymarket exchange (event 1200431, slug cs2-furia-aur1-2026-10-17)",
    "id": "poly-5778024-match-winner",
    "fixture_id": "hltv-2399414 (no Hotspawn fixture: TWC semi-final 1 is absent from the Hotspawn scheduled feed, verified across all 9 feed chunks 2026-10-17T00:15Z)",
    "source_teams": ["FURIA", "Aurora Gaming"],
    "team_aliases": [["FURIA"], ["Aurora Gaming", "Aurora"]],
    "alias_sources": ["Polymarket market outcome titles", "HLTV match page 2399414 team names"],
    "start": "2026-10-17T14:00:00Z",
    "best_of": 3,
    "odds": [0.525, 0.475],
    "observed_at": "2026-10-17T00:00:00Z",
    "url": "https://gamma-api.polymarket.com/markets/5778024",
    "api_url": "https://gamma-api.polymarket.com/events?slug=cs2-furia-aur1-2026-10-17",
    "event": "Thunderpick World Championship 2026 Playoffs - Semifinal 1 (Polymarket event 1200431)",
    "identity_evidence": [
        {"label": "Polymarket market 5778024 'Match Winner', outcomePrices ['0.525','0.475'], lastTradePrice 0.53, bestBid 0.52 / bestAsk 0.53, liquidityNum $158,627.63, volumeNum $38,837.57, accepting orders, endDate 2026-10-17T20:00Z, updatedAt 2026-10-16T23:55:13Z",
         "url": "https://gamma-api.polymarket.com/markets/5778024"},
        {"label": "Polymarket event 1200431: gameStartTime 2026-10-17 14:00 UTC, resolutionSource twitch.tv/thunderpicktv, total liquidity $292,925 across five markets",
         "url": "https://gamma-api.polymarket.com/events?slug=cs2-furia-aur1-2026-10-17"},
        {"label": "HLTV match 2399414: FURIA vs Aurora, Thunderpick World Championship 2026, semi-final, Bo3 LAN, 17 Oct 14:00 UTC",
         "url": "https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026"},
    ],
    "corroboration": [
        {"label": "Same event's other markets: Map 1 Winner 5778022 (FURIA 0.475 / Aurora 0.525), Map 2 Winner 5778023 (0.545 / 0.455), Games O/U 2.5 market 5778025 (Over 0.47 / Under 0.53), Map Handicap FURIA -1.5 market 5778026",
         "url": "https://gamma-api.polymarket.com/events?slug=cs2-furia-aur1-2026-10-17"},
        {"label": "Pinnacle matchup 1638536356 period-0 moneyline FURIA -125 / Aurora +103 de-margined to 53.0% / 47.0% - agrees with the exchange within 0.5 points",
         "url": PIN_URL},
        {"label": "Market tightened during the evening: an earlier read at 2026-10-16T19:35Z showed 0.52 / 0.48 with $10,151.23 liquidity (session 621776e4)",
         "url": "https://gamma-api.polymarket.com/markets/5778024"},
    ],
    "limitation": "Exchange outcome prices, not a bookmaker's odds; no fee adjustment applied. Prices sum to 1.000 so no visible overround at 1-cent granularity. Exchange liquidity is not a guarantee of execution at the quoted price.",
})

r["receipts"].append({
    "provider": "Polymarket exchange (event 1201748, slug cs2-fal2-bb3-2026-10-17)",
    "id": "poly-5787759-match-winner",
    "fixture_id": "hltv-2399415 (no Hotspawn fixture: TWC semi-final 2 is absent from the Hotspawn scheduled feed, verified across all 9 feed chunks 2026-10-17T00:15Z)",
    "source_teams": ["Team Falcons", "BetBoom Team"],
    "team_aliases": [["Team Falcons", "Falcons"], ["BetBoom Team", "BETBOOM", "BB Team"]],
    "alias_sources": ["Polymarket market outcome titles", "data/identities.json register", "HLTV match page 2399415 team names"],
    "start": "2026-10-17T17:00:00Z",
    "best_of": 3,
    "odds": [0.795, 0.205],
    "observed_at": "2026-10-17T00:00:00Z",
    "url": "https://gamma-api.polymarket.com/markets/5787759",
    "api_url": "https://gamma-api.polymarket.com/events?slug=cs2-fal2-bb3-2026-10-17",
    "event": "Thunderpick World Championship 2026 Playoffs - Semifinal 2 (Polymarket event 1201748)",
    "identity_evidence": [
        {"label": "Polymarket market 5787759 'Match Winner', outcomePrices ['0.795','0.205'], liquidityNum $60,484.48, volumeNum $12,271.77, endDate 2026-10-17T23:00Z, updatedAt 2026-10-16T23:53:13Z",
         "url": "https://gamma-api.polymarket.com/markets/5787759"},
        {"label": "Polymarket event 1201748: gameStartTime 2026-10-17 17:00 UTC, event liquidity $193,499, found by paginating the CS2 tag feed (tag 100780) to offset 5",
         "url": "https://gamma-api.polymarket.com/events?tag_id=100780&order=id&ascending=false&limit=10"},
        {"label": "HLTV match 2399415: Falcons vs BETBOOM, Thunderpick World Championship 2026, semi-final, Bo3 LAN, 17 Oct 17:00 UTC",
         "url": "https://www.hltv.org/matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026"},
    ],
    "corroboration": [
        {"label": "Same event's map markets: Map 1 Winner 5787757 (Falcons 0.68 / BETBOOM 0.32), Map 2 Winner 5787758 (Falcons 0.725 / BETBOOM 0.275)",
         "url": "https://gamma-api.polymarket.com/events?slug=cs2-fal2-bb3-2026-10-17"},
        {"label": "Pinnacle matchup 1638595724 period-0 moneyline Falcons -389 / BETBOOM +298 de-margined to 76.0% / 24.0% - same direction, exchange 3.5 points stronger on Falcons",
         "url": PIN_URL},
        {"label": "HLTV live VRS forecast box on match 2399415: Falcons 1880 pts #4 vs BETBOOM 1619 pts #10 - same direction",
         "url": "https://www.hltv.org/matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026"},
    ],
    "limitation": "Exchange outcome prices, not a bookmaker's odds; no fee adjustment applied. Prices sum to 1.000 so no visible overround at 1-cent granularity. Polymarket slug abbreviation ('fal2', 'bb3') is not predictable - the event was located by paginating the tag feed, not by slug guessing.",
})

p.write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n")
print("book-receipts.json updated:", len(r["receipts"]), "receipts")
