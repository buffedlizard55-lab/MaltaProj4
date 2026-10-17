# Day-4 semi-final market reads — session bca04a82

All reads taken 2026-10-17T00:00–00:15 UTC via the sandbox's page-fetch tool
(bash egress reaches GitHub and package registries only; the operator APIs were
read through fetch_page, never claimed as bash checks).

## Semi-final 1 — FURIA vs Aurora (HLTV 2399414, 2026-10-17T14:00Z, Bo3 LAN)

**Pinnacle** (guest API `sports/12/markets/straight`, chunk scan):
matchupId 1638536356, home FURIA / away Aurora, league "CS2 - TP World
Championship" id 230242, startTime 2026-10-17T14:00Z, rotation 14046.
Period-0 moneyline (`s;0;m`): **home −125 / away +103**, status open, cutoff
2026-10-17T14:00Z, maxRiskStake 5000, version 3767145143.
Period-2 moneyline (`s;2;m`, map 2): home −134 / away +110 (version 3767146007).
De-margined: 125/225 = 0.55556, 100/203 = 0.49261, sum 1.04817 →
**FURIA 53.0% / Aurora 47.0%**, overround 4.82%, fair line ≈ −113/+113.

**Polymarket** (Gamma API): event 1200431, slug `cs2-furia-aur1-2026-10-17`,
gameStartTime 2026-10-17 14:00 UTC, resolutionSource twitch.tv/thunderpicktv.
Match Winner market 5778024: outcomePrices **["0.525","0.475"]** FURIA/Aurora,
lastTradePrice 0.53, bestBid 0.52 / bestAsk 0.53, liquidityNum $158,627.63,
volumeNum $38,837.57, endDate 2026-10-17T20:00Z, updatedAt 2026-10-16T23:55:13Z.
Context markets on the same event: Map 1 Winner 5778022 (0.475/0.525 — exchange
leans Aurora on map 1), Map 2 Winner 5778023 (0.545/0.455), Games O/U 2.5
market 5778025 (Over 0.47 / Under 0.53 — leans a 2-0 sweep), Map Handicap
FURIA −1.5 market 5778026. Event liquidity $292,925, volume $40,581.
Earlier read (session 621776e4, 19:35 UTC 16 Oct): 0.52/0.48 with $10,151.23
liquidity — retained as the price-movement record.

**HLTV match page 2399414** (server-side): VRS forecast box — FURIA 1826 pts
#6 current, Aurora 1848 pts #5 current; if FURIA wins +24 → #5, if Aurora wins
+37 → #4; if FURIA loses −24 → #6, if Aurora loses −32 → #6. Head-to-head:
all-time FURIA 18 wins / 5 overtimes / Aurora 15 wins; 2026 split 2-2 (EPL S24
6 Oct Aurora 2-1 [Nuke 9-13, Mirage 9-13, Dust2 13-8]; EWC 19 Aug FURIA 2-1
[Mirage 13-9, Nuke 14-16, Ancient 13-11]; IEM Cologne Major 20 Jun FURIA 2-0
[Nuke 13-4, Dust2 13-9]; BLAST Open Rotterdam 20 Mar Aurora 2-0 [Dust2 16-14
OT, Inferno 13-6]). The Cologne direction was corrected against match page
2395000 (Aurora 0-2 FURIA) — an earlier working note had it backwards.
Countdown at read time: 14h 10m → 14:00Z start confirmed.

## Semi-final 2 — Falcons vs BETBOOM (HLTV 2399415, 2026-10-17T17:00Z, Bo3 LAN)

**Pinnacle**: matchupId 1638595724, home Falcons / away "BB Team" (BetBoom
alias, mapped through data/identities.json), league id 230242, startTime
2026-10-17T17:00Z, rotation 14048. Period-0 moneyline: **home −389 / away
+298**, status open, cutoff 2026-10-17T17:00Z, maxRiskStake 5000, version
3767145819. De-margined: 389/489 = 0.79550, 100/398 = 0.25126, sum 1.04676 →
**Falcons 76.0% / BETBOOM 24.0%**, overround 4.68%, fair line ≈ −326/+317.

**Polymarket**: event 1201748, slug `cs2-fal2-bb3-2026-10-17` (located by
paginating the CS2 tag feed, tag_id 100780, to offset 5 — the slug abbreviation
is not predictable), gameStartTime 2026-10-17 17:00 UTC, event liquidity
$193,499. Match Winner market 5787759: outcomePrices **["0.795","0.205"]**
Falcons/BetBoom Team, liquidityNum $60,484.48, volumeNum $12,271.77, endDate
2026-10-17T23:00Z, updatedAt 2026-10-16T23:53:13Z. Map 1 Winner 5787757
(0.68/0.32), Map 2 Winner 5787758 (0.725/0.275).

**HLTV match page 2399415** (server-side): VRS forecast box — Falcons 1880 pts
#4 current, BETBOOM 1619 pts #10; if Falcons win +14 → #4, if BETBOOM win
+106 → #8; if Falcons lose −19 → #5, if BETBOOM lose −17 → #10. Head-to-head:
Falcons 0 wins / BETBOOM 2 wins — both at the IEM Cologne Major 2026, 12 June
(Ancient 10-13, Nuke 11-13, match 2394975). Falcons recent: EPL S24 losses
0-2 Spirit (1 week ago) and 1-2 Vitality, wins 2-0 Aurora, 2-0 TYLOO, 2-1 NAVI;
TWC 2-0 NIP, 2-1 9z. BETBOOM recent: TWC 0-2 FURIA, 2-1 PARIVISION, 2-1 Legacy
(OT decider); EPL S24 2-0 9z, 2-1 Aurora, 0-2 FURIA. Countdown at read time:
17h 11m → 17:00Z start confirmed.

## Unpriced at final read

- 3rd-place match (9z vs Legacy, HLTV 2399416, ~2026-10-18T11:30Z): no Pinnacle
  matchup, Polymarket slug guess `cs2-9z-legacy-2026-10-18` returned [].
- Grand final Bo5 (HLTV 2399417, ~2026-10-18T15:00Z): participants unknowable
  before the semis; no market on either book.

## Hotspawn feed re-check (2026-10-17T00:15Z)

All 9 chunks of the CS2 scheduled fixtures API read in full: the TWC main-event
playoffs are NOT listed (only "Thunderpick World Championship 2026: South
American Series #1", competition 33804, appears). The semis therefore cannot
become board rows; they are published as research content in
data/analysis.json → analysis.html#day-four-guidance only.
