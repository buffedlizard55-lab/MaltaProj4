# Quote availability for every pick without a published probability

Built by `research/quotes-76712ccc/build_dossier.py` from the committed snapshot of 2026-10-17T20:18:27.941952Z. Every row below
is recomputed, not typed: the market column quotes the pipeline's own attempt records, the model column is
the output of `scripts.vrs.line` over the vendored Valve standings of 2026-10-05 plus the HLTV lineup, and a
blank model cell means that function returned no line (the reason is printed verbatim).

| Fixture | Start (UTC) | Competition | Pick | Market probes | Model line |
| --- | --- | --- | --- | --- | --- |
| NEXVOID vs Off Chops (`1081519`) | 2026-10-18T03:00:00Z | Logitech G Pro Series 2026 | NEXVOID | Polymarket: unresolved; HLTV: unresolved; Pinnacle: unresolved; Polymarket: unresolved; Thunderpick: unresolved; GG.BET: error; Valve VRS model: unresolved; Rank research: resolved | blank — Off Chops: not listed in the Valve global standings. |
| antidaun vs Phantom Academy (`1081522`) | 2026-10-18T13:45:00Z | CCT Europe 2026 Challengers #8 | Phantom Academy | Polymarket: unresolved; HLTV: unresolved; Pinnacle: unresolved; Polymarket: unresolved; Thunderpick: unresolved; GG.BET: error; Valve VRS model: unresolved; Rank research: resolved | blank — antidaun: not listed in the Valve global standings. |
| Lynn Vision vs Morningstar (`1081861`) | 2026-10-20T03:00:00Z | VOID Autumn Cup 2026 | Lynn Vision | Polymarket: unresolved; HLTV: unresolved; Pinnacle: unresolved; Polymarket: unresolved; Thunderpick: unresolved; GG.BET: error; Valve VRS model: unresolved; Rank research: resolved | blank — Morningstar: not listed in the Valve global standings. |
| Chinggis Warriors vs WXM (`1081863`) | 2026-10-20T07:00:00Z | VOID Autumn Cup 2026 | Chinggis Warriors | Polymarket: unresolved; HLTV: unresolved; Pinnacle: unresolved; Polymarket: unresolved; Thunderpick: unresolved; GG.BET: error; Valve VRS model: unresolved; Rank research: resolved | blank — WXM: not listed in the Valve global standings. |

## Per-fixture detail

### NEXVOID vs Off Chops — Hotspawn fixture 1081519

- Competition / start: Logitech G Pro Series 2026, 2026-10-18T03:00:00Z.
- Pick published by the pipeline: **NEXVOID** (research_rank_single).
- Fixture identity: [HLTV match page](https://www.hltv.org/matches/2399547/nexvoid-vs-off-chops-dfrag-logitech-g-pro-series-2026), captured 2026-10-17T20:16:38.947761Z.
- Valve standings: `NEXVOID` → **NEXVOID** #113, 995 points, 5 of 5 lineup players matched (`AccuracyTG, erkaSt, MiQ, xerolte, Zesta`).
- Valve standings: `Off Chops` — not listed in the Valve global standings (no list carries the label).
- Polymarket probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://gamma-api.polymarket.com/sports)).
- HLTV probe: *unresolved* — HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. ([source](https://www.hltv.org/matches/2399547/nexvoid-vs-off-chops-dfrag-logitech-g-pro-series-2026)).
- Pinnacle probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)).
- Polymarket probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://gamma-api.polymarket.com/sports)).
- Thunderpick probe: *unresolved* — Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. ([source](https://thunderpick.io/esports/cs2-betting)).
- GG.BET probe: *error* — HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. ([source](https://gg.bet/en/esports/counter-strike)).
- Valve VRS model probe: *unresolved* — No originated line: Off Chops: not listed in the Valve global standings. ([source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)).
- Rank research probe: *resolved* — Exact HLTV fixture identity; one team world-ranked in the ranking page, the other absent from it. No probability derived. ([source](https://www.hltv.org/matches/2399547/nexvoid-vs-off-chops-dfrag-logitech-g-pro-series-2026)).
- **Published probability: blank.** Blocker: Off Chops: not listed in the Valve global standings.

### antidaun vs Phantom Academy — Hotspawn fixture 1081522

- Competition / start: CCT Europe 2026 Challengers #8, 2026-10-18T13:45:00Z.
- Pick published by the pipeline: **Phantom Academy** (research_rank_single).
- Fixture identity: [HLTV match page](https://www.hltv.org/matches/2399682/antidaun-vs-phantom-academy-cct-2026-challengers-europe-series-8), captured 2026-10-17T20:16:40.506383Z.
- Valve standings: `antidaun` — not listed in the Valve global standings (no list carries the label).
- Valve standings: `Phantom Academy` → **Phantom Academy** #172, 783 points, 4 of 5 lineup players matched (`Ayteel, Brain47, Dr3nquu, kalyambys, stefienson`).
- Polymarket probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://gamma-api.polymarket.com/sports)).
- HLTV probe: *unresolved* — HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. ([source](https://www.hltv.org/matches/2399682/antidaun-vs-phantom-academy-cct-2026-challengers-europe-series-8)).
- Pinnacle probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)).
- Polymarket probe: *unresolved* — No exact team-pair and UTC-start match in retrieved feed. ([source](https://gamma-api.polymarket.com/sports)).
- Thunderpick probe: *unresolved* — Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. ([source](https://thunderpick.io/esports/cs2-betting)).
- GG.BET probe: *error* — HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. ([source](https://gg.bet/en/esports/counter-strike)).
- Valve VRS model probe: *unresolved* — No originated line: antidaun: not listed in the Valve global standings. ([source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)).
- Rank research probe: *resolved* — Exact HLTV fixture identity; one team world-ranked in the ranking page, the other absent from it. No probability derived. ([source](https://www.hltv.org/matches/2399682/antidaun-vs-phantom-academy-cct-2026-challengers-europe-series-8)).
- **Published probability: blank.** Blocker: antidaun: not listed in the Valve global standings.

### Lynn Vision vs Morningstar — Hotspawn fixture 1081861

- Competition / start: VOID Autumn Cup 2026, 2026-10-20T03:00:00Z.
- Pick published by the pipeline: **Lynn Vision** (research_rank_single).
- Fixture identity: [HLTV match page](https://www.hltv.org/matches/2399576/lynn-vision-vs-morningstar-macemedia-void-autumn-cup-2026), captured 2026-10-17T20:16:43.775536Z.
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
- Fixture identity: [HLTV match page](https://www.hltv.org/matches/2399578/chinggis-warriors-vs-wxm-macemedia-void-autumn-cup-2026), captured 2026-10-17T20:16:45.527623Z.
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
