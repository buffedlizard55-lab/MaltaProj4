#!/usr/bin/env python3
"""Union-merge data/analysis.json after merging origin/main (session 76712ccc/1abdd416,
PR #51) into session bca04a82's branch.

Base = origin/main's version (it owns the pick/pick_detail/book_line card schema, the
Saturday weekday fix and two extra sourced points). Layer bca04a82's genuinely new,
independently verified content on top:
  - map-by-map re-verified FURIA-Aurora head-to-head, which CORRECTS the Cologne Major
    direction (FURIA won 2-0 on HLTV 2395000, so 2026 H2H is 2-2, not "1-1 in 30 days")
  - HLTV's server-side VRS forecast boxes captured directly (live ranks verified, not
    merely harvested): Aurora #5 1848 > FURIA #6 1826; Falcons #4 1880 > BETBOOM #10 1619
  - map-level market context (Polymarket map/totals markets, Pinnacle period-2 ML)
  - the fatigue/map-load arithmetic for both semis
  - BETBOOM's 2-0 head-to-head sweep of Falcons (Cologne Major, HLTV 2394975)
  - 00:10 UTC re-read confirmation of every market line (same prices, same versions)
  - Hotspawn full-feed re-check at 00:15 UTC (playoffs still absent)
  - day-3 results enriched with veto, halves, overtime, demo ids and series ratings
Both sessions' receipts live in data/book-receipts.json; raw reads in
research/day4-bca04a82/MARKET-READS.md and research/harvest-1abdd416/.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
theirs = json.loads(Path('/tmp/main_analysis.json').read_text())          # origin/main
# The working tree carries conflict markers, so take MY blob from git instead.
import subprocess
mine = json.loads(subprocess.check_output(
    ['git', 'show', 'HEAD:data/analysis.json'], cwd=ROOT, text=True))

d = json.loads(json.dumps(theirs))  # deep copy of theirs as the union base

# ---------------------------------------------------------------- top level
d['reviewed_at'] = mine['reviewed_at']
d['reviewed_at_utc'] = mine['reviewed_at_utc']
d['note'] = theirs['note'] + (
    " Day-4 semi-final lines re-read and re-verified on 17 October 2026 (UTC) by session "
    "bca04a82 from Pinnacle's public matchup/markets API (matchups 1638536356 and 1638595724, "
    "market versions 3767145143 and 3767145819) and Polymarket's Gamma API (markets 5778024 "
    "and 5787759): the same prices as the 23:52 UTC capture, so both captures are retained and "
    "dated. The FURIA-Aurora head-to-head was re-verified map by map against HLTV match pages "
    "2398743, 2396600, 2395000, 2391758 and 2389661, which corrected the IEM Cologne Major "
    "direction (FURIA won 2-0, not Aurora), and HLTV's server-side VRS forecast boxes on match "
    "pages 2399414 and 2399415 were captured and published as verified live ranks. Receipts: "
    "data/book-receipts.json. Raw reads: research/day4-bca04a82/MARKET-READS.md.")

# ---------------------------------------------------------------- day-3 results
r = d['day_three_results']
r['note'] = theirs['day_three_results']['note'] + (
    " Re-read on 17 October 2026 (UTC) by session bca04a82: the veto sequence, all three "
    "half-time splits, the overtime score, the series ratings and both demo ids below are "
    "verified directly on the HLTV match pages 2399412 and 2399413.")
r['matches'][0] = mine['day_three_results']['matches'][0]  # mine carries veto/demo/KAST + the
# re-verified flag; theirs' Inferno caveat is closed inside it.

bet = dict(theirs['day_three_results']['matches'][1])
bet['maps'] = mine['day_three_results']['matches'][1]['maps']
bet['detail'] = (
    "BETBOOM became the final semi-finalist with a 2-1 win: Nuke 16-13 in overtime after "
    "trailing 4-10 in the first half (4:8, then 8:4, overtime 4:1), Dust2 11-13 to Legacy "
    "(halves 7:5, 4:8) and Mirage 13-11 (halves 7:5, 6:6) behind a 25-kill, 104.5 ADR, "
    "1.58-rated map three from Magnojez. The veto ran: BETBOOM removed Inferno, Legacy "
    "removed Anubis, BETBOOM picked Nuke, Legacy picked Dust2, BETBOOM removed Cache, "
    "Legacy removed Ancient, Mirage left over. Series ratings on the HLTV match page "
    "(Rating 3.0, re-read 17 October 2026): Magnojez 62-50 K-D, 82.8 ADR, 67.5% KAST, 1.17; "
    "d1Ledez 55-50 with 1.08; Boombl4 49-51 with 1.06; S1ren 44-47 with 1.02. The match "
    "began 17:00 UTC (HLTV displays 13:00, UTC-4) and the overtime finish pushed the end to "
    "roughly 19:30 UTC. Legacy are eliminated in 5th/6th place. Demo: HLTV download 112853. "
    "The day-four semi-final 2 is therefore Falcons vs BETBOOM, not Falcons vs Legacy.")
bet['flag'] = (
    "Map scores, halves, overtime, veto, ratings and the demo id are HLTV values from the "
    "match page, not this project's calculation. The finish time is derived from the 17:00 "
    "UTC start plus the three-map runtime and is approximate. Final result published 16 "
    "October 2026; the slot was undecided (live at 1-1, Mirage to decide) at the earlier "
    "19:35 UTC read.")
bet.setdefault('report_url', 'https://www.hltv.org/results?event=8932')
r['matches'][1] = bet

# ---------------------------------------------------------------- day-4 cards
g = d['day_four_guidance']
sf1, sf2 = g['not_listed']

# --- semi-final 1: FURIA vs Aurora
sf1['timing'] = theirs['day_four_guidance']['not_listed'][0]['timing'] + (
    " The match page showed a 14h 10m countdown at the 17 October 00:10 UTC read. Maps are "
    "TBA until the veto.")
sf1['market']['label'] = ("Polymarket moneyline, market 5778024, capture 23:52 UTC 16 "
                          "October, re-read unchanged at 00:10 UTC 17 October")
sf1['market']['detail'] = theirs['day_four_guidance']['not_listed'][0]['market']['detail'] + (
    " Re-read at 00:10 UTC on 17 October: same outcome prices, last trade 0.53, best bid 0.52 "
    "/ best ask 0.53, liquidity $158,627.63.")
sf1['book_line']['label'] = ("Pinnacle moneyline, matchup 1638536356, capture 23:52 UTC 16 "
                             "October, re-read unchanged at 00:10 UTC 17 October")
sf1['book_line']['detail'] = theirs['day_four_guidance']['not_listed'][0]['book_line']['detail'] + (
    " Re-read at 00:10 UTC on 17 October: same prices, version 3767145143, status open.")
sf1['why'] = (
    "Both the exchange and the sharp bookmaker call this a near coin flip - Polymarket "
    "52.5/47.5, Pinnacle de-margined 53.0/47.0, half a point apart - while our model "
    "(Valve's 5 October standings, which predate this week) reads FURIA 62.2%. The market "
    "does not share the model's conviction, and that is published rather than smoothed over. "
    "The sourced case for the 47-48% side: Aurora beat Ninjas in Pyjamas 2-0 on day two and "
    "9z 2-0 in the Group A decider, and HLTV's live VRS now ranks Aurora #5 (1848 pts) above "
    "FURIA #6 (1826 pts) - a 22-point gap the 5 October repository file does not contain, "
    "verified from the server-side VRS forecast box on the match page. Head-to-head, "
    "re-verified map by map on 17 October: all-time FURIA lead 18-15 with 5 overtimes, but "
    "2026 is split 2-2 - Aurora won the most recent meeting (ESL Pro League Season 24, "
    "6 October, 2-1: Nuke 9-13, Mirage 9-13, Dust2 13-8) and BLAST Open Rotterdam in March "
    "2-0 (Dust2 16-14 in overtime, Inferno 13-6), while FURIA won the IEM Cologne Major in "
    "June 2-0 (Nuke 13-4, Dust2 13-9) and the Esports World Cup in August 2-1 (Mirage "
    "13-9, Nuke 14-16, Ancient 13-11). An earlier working note had the Cologne Major the "
    "other way round; match page 2395000 confirms FURIA won it 2-0. The case for FURIA: "
    "group-winner form (2-0 over BETBOOM, 2-1 over Legacy), a one-map lighter path (5 maps "
    "to Aurora's 6) and roughly one extra rest day (last played 15 October, against "
    "Aurora's 16 October 14:00 UTC decider). Map-level prices lean Aurora on map 1 "
    "(Polymarket 0.475 against 0.525) and FURIA on map 2 (0.545 against 0.455; Pinnacle's "
    "map-2 moneyline is FURIA -134 / Aurora +110), and the games total leans a 2-0 sweep "
    "(Polymarket Under 2.5 games at 0.53; the map handicap prices a FURIA 2-0 at about "
    "28%). Leaderboard default: FURIA, because Hotspawn awards a fixed number of points per "
    "correct pick and both market lines make FURIA the favourite. Contrarian side: Aurora, "
    "at about 47-48% - a coin flip, not a long shot - for anyone who weighs the live VRS "
    "rank and the most recent head-to-head above the bookmakers; the market edge is only "
    "about four points, so it is a differentiation, not a swing.")
sf1['sources'] = theirs['day_four_guidance']['not_listed'][0]['sources'] + [
    {"label": "Pinnacle CS2 straight markets (matchup 1638536356, period 0, version 3767145143)",
     "url": "https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight"},
    {"label": "Polymarket event 1200431 (Match Winner, map, handicap and totals markets)",
     "url": "https://gamma-api.polymarket.com/events?slug=cs2-furia-aur1-2026-10-17"},
    {"label": "HLTV: FURIA vs Aurora, 6 Oct 2026, EPL Season 24 (Aurora 2-1)",
     "url": "https://www.hltv.org/matches/2398743/furia-vs-aurora-esl-pro-league-season-24"},
    {"label": "HLTV: Aurora vs FURIA, 20 Jun 2026, IEM Cologne Major (FURIA 2-0)",
     "url": "https://www.hltv.org/matches/2395000/aurora-vs-furia-iem-cologne-major-2026"},
]

# --- semi-final 2: Falcons vs BETBOOM
sf2['timing'] = theirs['day_four_guidance']['not_listed'][1]['timing'] + (
    " The match page showed a 17h 11m countdown at the 00:10 UTC read. Maps are TBA until "
    "the veto.")
sf2['market']['label'] = ("Polymarket moneyline, market 5787759, capture 23:52 UTC 16 "
                          "October, re-read unchanged at 00:10 UTC 17 October")
sf2['market']['detail'] = theirs['day_four_guidance']['not_listed'][1]['market']['detail'] + (
    " Re-read at 00:10 UTC on 17 October: same outcome prices, liquidity $60,484.48, "
    "$12,271.77 traded.")
sf2['book_line']['label'] = ("Pinnacle moneyline, matchup 1638595724, capture 23:52 UTC 16 "
                             "October, re-read unchanged at 00:10 UTC 17 October")
sf2['book_line']['detail'] = theirs['day_four_guidance']['not_listed'][1]['book_line']['detail'] + (
    " Re-read at 00:10 UTC on 17 October: same prices, version 3767145819, status open.")
sf2['why'] = (
    "Every source agrees on direction here: the exchange says 79.5%, the sharp bookmaker "
    "76.0% and our model 73.9%. The only sourced argument for the underdog is the schedule, "
    "and it is real: BETBOOM have played on all three days (0-2 to FURIA on 14 October, "
    "2-1 over PARIVISION on 15 October, then the 2-1 overtime decider over Legacy on 16 "
    "October) - eight maps, including two three-map series in two days, the second decided "
    "in overtime on Nuke - while Falcons played five maps and last played on 15 October: "
    "about two days of rest against roughly 22 hours for BETBOOM, whose decider ended "
    "around 19:30 UTC on 16 October. The underdog also owns the head-to-head: BETBOOM "
    "swept Falcons 2-0 in their only meetings, at the IEM Cologne Major on 12 June "
    "(Ancient 13-10, Nuke 13-11), and enter with ESL Pro League Season 24 wins over Aurora "
    "2-1 and 9z 2-0, while Falcons lost 0-2 to Spirit at EPL S24 one week ago. HLTV's live "
    "VRS has Falcons #4 (1880 pts) against BETBOOM #10 (1619 pts) - the same direction as "
    "the market, with a wider gap. Map-level prices: Polymarket map 1 Falcons 0.68 / "
    "BETBOOM 0.32, map 2 Falcons 0.725 / 0.275. Rest is a structural observation from the "
    "fixture list, not a measured performance effect, and the market has to be wrong for "
    "the contrarian side to pay: the de-margined lines put BETBOOM between roughly 21% and "
    "24%, so taking them is a deliberate swing and should be capped if taken at all - and "
    "the dog is also the tired side, which is why this is published as the slate's "
    "contrarian candidate rather than recommended. Leaderboard default: Falcons. "
    "Contrarian side: BETBOOM, at the outside edge of the 15-40% band.")
sf2['sources'] = theirs['day_four_guidance']['not_listed'][1]['sources'] + [
    {"label": "Pinnacle CS2 straight markets (matchup 1638595724, period 0, version 3767145819)",
     "url": "https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight"},
    {"label": "Polymarket event 1201748 (Match Winner and map markets)",
     "url": "https://gamma-api.polymarket.com/events?slug=cs2-fal2-bb3-2026-10-17"},
    {"label": "HLTV: Falcons vs BETBOOM, 12 Jun 2026, IEM Cologne Major (BETBOOM 2-0)",
     "url": "https://www.hltv.org/matches/2394975/falcons-vs-betboom-iem-cologne-major-2026"},
]

# ---------------------------------------------------------------- unverified list
u = g['unverified']
u[0] = u[0] + (" At the 00:10 UTC re-read neither book had opened them: Pinnacle's CS2 "
               "matchup list contains no such fixtures and a Polymarket slug search for the "
               "third-place match returned no event.")
u[3] = u[3] + (" Session bca04a82 captured the server-side VRS forecast boxes directly on "
               "17 October: semi 1 FURIA 1826 pts (#6; +24 to #5 if they win, -24 if they "
               "lose) against Aurora 1848 pts (#5; +37 to #4 if they win, -32 to #6 if they "
               "lose), and semi 2 Falcons 1880 pts (#4) against BETBOOM 1619 pts (#10; +106 "
               "to #8 if they win). The live ranking is therefore verified rather than "
               "merely captured, and it puts Aurora 22 points above FURIA where the 5 "
               "October repository file puts FURIA 113 points above Aurora.")
u[5] = u[5] + (" Map load at the event: FURIA 5 maps (last played 15 October), Aurora 6 "
               "maps (last played 16 October 14:00 UTC), Falcons 5 maps (last played 15 "
               "October), BETBOOM 8 maps including an overtime Nuke decider that ended "
               "around 19:30 UTC on 16 October - a turnaround of about 22 hours into the "
               "17:00 UTC semi-final.")
u[8] = u[8] + (" Re-checked at 00:15 UTC on 17 October: all nine chunks of the scheduled "
               "fixture API were read in full and the main-event playoffs are still absent, "
               "so the semi-finals ship as research cards rather than board rows.")
u[10] = u[10] + (" Pinnacle's public guest API also exposes no price-change timestamp; each "
                 "line is a single version-stamped observation (versions 3767145143 and "
                 "3767145819), not a price history.")
u += [
    "Polymarket's semi-final 1 market tightened during the evening: the same moneyline "
    "market 5778024 read 0.52/0.48 with $10,151.23 liquidity at 19:35 UTC on 16 October "
    "(session 621776e4) and 0.525/0.475 with $158,627.63 liquidity at the 23:52 UTC capture "
    "(session 1abdd416) and the unchanged 00:10 UTC re-read (session bca04a82). The "
    "published price is the latest read and the earlier reads are retained in the session "
    "receipts.",
    "Map-level prices (Polymarket map-winner and totals markets, Pinnacle period moneylines) "
    "are quotes on single maps, not series probabilities, and are published only as context "
    "on the cards. Pinnacle's period-1 (map-1) moneylines were not captured for either "
    "semi-final at the final read.",
]

(ROOT / 'data/analysis.json').write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("union written")
print("unverified items:", len(g['unverified']))
print("points:", len(g['points']), "| fixtures:", len(g['fixtures']), "| not_listed:", len(g['not_listed']))
