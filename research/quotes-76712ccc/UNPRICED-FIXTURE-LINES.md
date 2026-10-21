# Quote availability for every pick without a published probability

Built by `research/quotes-76712ccc/build_dossier.py` from the committed snapshot of 2026-10-18T00:52:19.597023Z. Every row below
is recomputed, not typed: the market column quotes the pipeline's own attempt records, the model column is
the output of `scripts.vrs.line` over the vendored Valve standings of 2026-10-05 plus the HLTV lineup, and a
blank model cell means that function returned no line (the reason is printed verbatim).

| Fixture | Start (UTC) | Competition | Pick | Market probes | Model line |
| --- | --- | --- | --- | --- | --- |
| NEXVOID vs Off Chops (`1081519`) | 2026-10-18T03:00:00Z | Logitech G Pro Series 2026 | NEXVOID | Polymarket: unresolved; HLTV: unresolved; Pinnacle: unresolved; Polymarket: unresolved; Thunderpick: unresolved; GG.BET: error; Valve VRS model: unresolved; Rank research: resolved | **52.68% / 47.32%** (VRS model, NEXVOID #113 995 pts, THUNDER dOWNUNDER #119 971 pts) |
| Privateer vs antidaun (`1081129`) | 2026-10-18T11:00:00Z | CCT Europe 2026 Series #12 Play-In | Privateer | Polymarket: unresolved; HLTV: unresolved; Pinnacle: unresolved; Polymarket: unresolved; Thunderpick: unresolved; GG.BET: error; Valve VRS model: unresolved; Rank research: resolved | blank — antidaun: not listed in the Valve global standings. |
| Damajuana vs A NATA (`1082206`) | 2026-10-18T16:00:00Z | CCT South America 2026 Series #7 | Damajuana | Polymarket: unresolved; HLTV: unresolved; Pinnacle: unresolved; Polymarket: unresolved; Thunderpick: unresolved; GG.BET: error; Valve VRS model: unresolved; Rank research: resolved | blank — A NATA: not listed in the Valve global standings. |
| Lynn Vision vs Morningstar (`1081861`) | 2026-10-20T03:00:00Z | VOID Autumn Cup 2026 | Lynn Vision | Polymarket: unresolved; HLTV: unresolved; Pinnacle: unresolved; Polymarket: unresolved; Thunderpick: unresolved; GG.BET: error; Valve VRS model: unresolved; Rank research: resolved | blank — Morningstar: not listed in the Valve global standings. |
| Chinggis Warriors vs WXM (`1081863`) | 2026-10-20T07:00:00Z | VOID Autumn Cup 2026 | Chinggis Warriors | Polymarket: unresolved; HLTV: unresolved; Pinnacle: unresolved; Polymarket: unresolved; Thunderpick: unresolved; GG.BET: error; Valve VRS model: unresolved; Rank research: resolved | blank — WXM: not listed in the Valve global standings. |

## Per-fixture detail

### NEXVOID vs Off Chops — Hotspawn fixture 1081519

- Competition / start: Logitech G Pro Series 2026, 2026-10-18T03:00:00Z.
- Pick published by the pipeline: **NEXVOID** (research_rank_single).
- Fixture identity: [HLTV match page](https://www.hltv.org/matches/2399547/nexvoid-vs-off-chops-dfrag-logitech-g-pro-series-2026), captured 2026-10-18T00:50:28.057797Z.
- Valve standings: `NEXVOID` → **NEXVOID** #113, 995 points, 5 of 5 lineup players matched (`AccuracyTG, erkaSt, MiQ, xerolte, Zesta`).
- Valve standings: `Off Chops` → **THUNDER dOWNUNDER** #119, 971 points, 4 of 5 lineup players matched (`dexter, Gratisfaction, Liazz, TjP, viridian`).
- Polymarket probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://gamma-api.polymarket.com/sports)).
- HLTV probe: *unresolved* — HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. ([source](https://www.hltv.org/matches/2399547/nexvoid-vs-off-chops-dfrag-logitech-g-pro-series-2026)).
- Pinnacle probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)).
- Polymarket probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://gamma-api.polymarket.com/sports)).
- Thunderpick probe: *unresolved* — Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. ([source](https://thunderpick.io/esports/cs2-betting)).
- GG.BET probe: *error* — HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. ([source](https://gg.bet/en/esports/counter-strike)).
- Valve VRS model probe: *unresolved* — No originated line: Off Chops: not listed in the Valve global standings. ([source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)).
- Rank research probe: *resolved* — Exact HLTV fixture identity; one team world-ranked in the ranking page, the other absent from it. No probability derived. ([source](https://www.hltv.org/matches/2399547/nexvoid-vs-off-chops-dfrag-logitech-g-pro-series-2026)).
- **Published probability: NEXVOID 52.68% and Off Chops 47.32%** from the labelled VRS model (Originated by scripts.vrs from the Valve standings plus the HLTV lineup. Not a market price.).
- Roster continuity checks: `NEXVOID` lineup (AccuracyTG, xerolte, erkaSt, Zesta, MiQ) shares 5 of 5 players with the standings roster; `THUNDER dOWNUNDER` lineup (viridian, dexter, Liazz, Gratisfaction, damyo) shares 4 of 5 players with the standings roster.
- Reproducible: the pipeline applies this same line automatically on its next run (`scripts.vrs.apply`), so the unresolved `Valve VRS model` probe above is superseded here.

### Privateer vs antidaun — Hotspawn fixture 1081129

- Competition / start: CCT Europe 2026 Series #12 Play-In, 2026-10-18T11:00:00Z.
- Pick published by the pipeline: **Privateer** (research_rank_single).
- Fixture identity: [HLTV match page](https://www.hltv.org/matches/2399480/antidaun-vs-privateer-cct-2026-europe-series-12-closed-qualifier), captured 2026-10-18T00:50:29.064791Z.
- Valve standings: `Privateer` → **Privateer** #271, 608 points, 3 of 5 lineup players matched (`Ariant0, Frazehh, JAUSTERE, M1n1maL, Prime`).
- Valve standings: `antidaun` — not listed in the Valve global standings (no list carries the label).
- Polymarket probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://gamma-api.polymarket.com/sports)).
- HLTV probe: *unresolved* — HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. ([source](https://www.hltv.org/matches/2399480/antidaun-vs-privateer-cct-2026-europe-series-12-closed-qualifier)).
- Pinnacle probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)).
- Polymarket probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://gamma-api.polymarket.com/sports)).
- Thunderpick probe: *unresolved* — Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. ([source](https://thunderpick.io/esports/cs2-betting)).
- GG.BET probe: *error* — HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. ([source](https://gg.bet/en/esports/counter-strike)).
- Valve VRS model probe: *unresolved* — No originated line: antidaun: not listed in the Valve global standings. ([source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)).
- Rank research probe: *resolved* — Exact HLTV fixture identity; one team world-ranked in the ranking page, the other absent from it. No probability derived. ([source](https://www.hltv.org/matches/2399480/antidaun-vs-privateer-cct-2026-europe-series-12-closed-qualifier)).
- **Published probability: blank.** Blocker: antidaun: not listed in the Valve global standings.

### Damajuana vs A NATA — Hotspawn fixture 1082206

- Competition / start: CCT South America 2026 Series #7, 2026-10-18T16:00:00Z.
- Pick published by the pipeline: **Damajuana** (research_rank_single).
- Fixture identity: [HLTV match page](https://www.hltv.org/matches/2399791/damajuana-vs-a-nata-cct-2026-south-america-series-7), captured 2026-10-18T00:50:30.562399Z.
- Valve standings: `Damajuana` → **DAMAJUANA** #356, 476 points, 3 of 5 lineup players matched (`Dunn, Kiritox, leo, maik, R4N`).
- Valve standings: `A NATA` — not listed in the Valve global standings (no list carries the label).
- Polymarket probe: *unresolved* — Exchange spread exceeds 25 points or liquidity is below $100. ([source](https://gamma-api.polymarket.com/markets/5819204)).
- HLTV probe: *unresolved* — HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. ([source](https://www.hltv.org/matches/2399791/damajuana-vs-a-nata-cct-2026-south-america-series-7)).
- Pinnacle probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)).
- Polymarket probe: *unresolved* — Exchange spread exceeds the 60-point ceiling for the low-confidence tier. ([source](https://gamma-api.polymarket.com/markets/5819204)).
- Thunderpick probe: *unresolved* — Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. ([source](https://thunderpick.io/esports/cs2-betting)).
- GG.BET probe: *error* — HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. ([source](https://gg.bet/en/esports/counter-strike)).
- Valve VRS model probe: *unresolved* — No originated line: A NATA: not listed in the Valve global standings. ([source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)).
- Rank research probe: *resolved* — Exact HLTV fixture identity; one team world-ranked in the ranking page, the other absent from it. No probability derived. ([source](https://www.hltv.org/matches/2399791/damajuana-vs-a-nata-cct-2026-south-america-series-7)).
- **Published probability: blank.** Blocker: A NATA: not listed in the Valve global standings.

### Lynn Vision vs Morningstar — Hotspawn fixture 1081861

- Competition / start: VOID Autumn Cup 2026, 2026-10-20T03:00:00Z.
- Pick published by the pipeline: **Lynn Vision** (research_rank_single).
- Fixture identity: [HLTV match page](https://www.hltv.org/matches/2399576/lynn-vision-vs-morningstar-macemedia-void-autumn-cup-2026), captured 2026-10-18T00:50:35.392693Z.
- Valve standings: `Lynn Vision` → **Lynn Vision** #64, 1190 points, 5 of 5 lineup players matched (`C4LLM3SU3, EmiliaQAQ, Starry, Westmelon, z4KR`).
- Valve standings: `Morningstar` — not listed in the Valve global standings (no list carries the label).
- Polymarket probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://gamma-api.polymarket.com/sports)).
- HLTV probe: *unresolved* — HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. ([source](https://www.hltv.org/matches/2399576/lynn-vision-vs-morningstar-macemedia-void-autumn-cup-2026)).
- Pinnacle probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)).
- Polymarket probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://gamma-api.polymarket.com/sports)).
- Thunderpick probe: *unresolved* — Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. ([source](https://thunderpick.io/esports/cs2-betting)).
- GG.BET probe: *error* — HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. ([source](https://gg.bet/en/esports/counter-strike)).
- Valve VRS model probe: *unresolved* — No originated line: Morningstar: not listed in the Valve global standings. ([source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)).
- Rank research probe: *resolved* — Exact HLTV fixture identity; one team world-ranked in the ranking page, the other absent from it. No probability derived. ([source](https://www.hltv.org/matches/2399576/lynn-vision-vs-morningstar-macemedia-void-autumn-cup-2026)).
- **Published probability: blank.** Blocker: Morningstar: not listed in the Valve global standings.

### Chinggis Warriors vs WXM — Hotspawn fixture 1081863

- Competition / start: VOID Autumn Cup 2026, 2026-10-20T07:00:00Z.
- Pick published by the pipeline: **Chinggis Warriors** (research_rank_single).
- Fixture identity: [HLTV match page](https://www.hltv.org/matches/2399578/chinggis-warriors-vs-wxm-macemedia-void-autumn-cup-2026), captured 2026-10-18T00:50:37.348825Z.
- Valve standings: `Chinggis Warriors` → **Chinggis Warriors** #87, 1084 points, 4 of 5 lineup players matched (`cool4st, fury5k, ROUX, sk0R, yAmi`).
- Valve standings: `WXM` — not listed in the Valve global standings (no list carries the label).
- Polymarket probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://gamma-api.polymarket.com/sports)).
- HLTV probe: *unresolved* — HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. ([source](https://www.hltv.org/matches/2399578/chinggis-warriors-vs-wxm-macemedia-void-autumn-cup-2026)).
- Pinnacle probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)).
- Polymarket probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://gamma-api.polymarket.com/sports)).
- Thunderpick probe: *unresolved* — Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. ([source](https://thunderpick.io/esports/cs2-betting)).
- GG.BET probe: *error* — HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. ([source](https://gg.bet/en/esports/counter-strike)).
- Valve VRS model probe: *unresolved* — No originated line: WXM: not listed in the Valve global standings. ([source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)).
- Rank research probe: *resolved* — Exact HLTV fixture identity; one team world-ranked in the ranking page, the other absent from it. No probability derived. ([source](https://www.hltv.org/matches/2399578/chinggis-warriors-vs-wxm-macemedia-void-autumn-cup-2026)).
- **Published probability: blank.** Blocker: WXM: not listed in the Valve global standings.

## Retained receipts

| File | SHA-256 | Source |
| --- | --- | --- |
| `research/quotes-76712ccc/valve-standings_global_2026_10_05.md` | `df96e7fc3cd91a26` | https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/live/2026/standings_global_2026_10_05.md |
| `research/quotes-76712ccc/valve-standings_europe_2026_10_05.md` | `058fb338b8710b3e` | https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/live/2026/standings_europe_2026_10_05.md |
| `research/quotes-76712ccc/valve-standings_asia_2026_10_05.md` | `b26930613dec57b4` | https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/live/2026/standings_asia_2026_10_05.md |
| `research/quotes-76712ccc/valve-standings_americas_2026_10_05.md` | `82b2519b9ba3d581` | https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/live/2026/standings_americas_2026_10_05.md |
| `research/harvest-76712ccc/polymarket-cs2-scan.json` | `4a08d45b0cc61aae` | https://gamma-api.polymarket.com/events?closed=false&limit=100&offset=0 |
| `research/harvest-76712ccc/pinnacle-sweep.json` | `9c46330a0a961903` | https://guest.api.arcana.pinnacle.com/0.1/leagues |
| `research/harvest-76712ccc/pinnacle-league-moneylines.json` | `cb06b13f25e75e82` | https://guest.api.arcana.pinnacle.com/0.1/leagues/230242/markets/straight |
| `research/harvest-76712ccc/book-probes.json` | `fd99aef9103e055e` | https://thunderpick.io/esports/cs2-betting |
| `research/harvest-76712ccc/hotspawn-fixtures.json` | `95ca43f75ea6032d` | https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1 |

## Policy

- Hotspawn pick percentages are never used as a probability.
- A probability exists only when a retained market receipt validates, or when scripts.vrs originates a labelled model line from both teams' Valve standings points plus the HLTV lineup.
- A team that appears in no Valve list stays blank and is flagged, never estimated.
