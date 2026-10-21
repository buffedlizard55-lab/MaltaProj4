# Independent open-board audit (session 2d0a85f2)

- Snapshot generated: `2026-10-21T19:57:45.210692Z`
- Fixtures observed: `2026-10-21T19:54:09.001755Z`
- Probe run: `2026-10-21T20:11:44Z`
- Coverage: `verified` counts `{"api": 76, "lobby": 76, "page": 76, "retained": 76}`

## Totals

| Measure | Count |
| --- | --- |
| Hotspawn CS2 records | 76 |
| Open | 13 |
| Not open | 63 |
| Open with a pick | 12 |
| Open with a published percentage | 9 |
| **Open with NO pick** | **1** |
| **Open with a pick but NO percentage** | **3** |
| Open whose evidence already expired | 0 |
| Open priced rows with no evidence link | 3 |

Method mix on open rows: `{"None": 1, "exchange": 3, "exchange_wide": 1, "model_vrs": 5, "research_rank": 1, "research_rank_single": 2}`

## Every open fixture, in start order

| Start (UTC) | ID | Match | Competition | Pick | P(team1) | P(team2) | Method | Evidence | Expires (UTC) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-21T22:00:00Z | 1082837 | Zetta vs LOS NINOS | CCT South America 2026 Series #7 | Zetta | **blank** | **blank** | research_rank_single | (none) | - |
| 2026-10-22T05:00:00Z | 1081870 | Vitalem Aerem vs Rare Atom | VOID Autumn Cup 2026 | Rare Atom | 41.0% | 59.0% | exchange_wide | https://polymarket.com/event/cs2-va-ra1-2026-10-22 | 2026-10-22T03:50:57.571907Z |
| 2026-10-22T11:00:00Z | 1081597 | benched gods vs TitanFlow | CCT Europe 2026 Challengers #8 | **NONE** | **blank** | **blank** | - | (none) | - |
| 2026-10-22T13:45:00Z | 1081600 | Donstu vs Banda chuya | CCT Europe 2026 Challengers #8 | Banda chuya | 42.4% | 57.6% | model_vrs | https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md | 2026-10-22T03:54:09.001755Z |
| 2026-10-22T14:00:00Z | 1082688 | Imperial vs Turma do Pagode | Circuit X Curitiba #4 | Imperial | 77.0% | 23.0% | exchange | https://polymarket.com/event/cs2-imp11-tdp-2026-10-22 | 2026-10-22T03:50:57.571907Z |
| 2026-10-22T14:00:00Z | 1082689 | BESTIA vs ShindeN | Circuit X Curitiba #4 | BESTIA | 52.5% | 47.5% | exchange | https://polymarket.com/event/cs2-bst-shin-2026-10-22 | 2026-10-22T03:50:57.571907Z |
| 2026-10-22T14:00:00Z | 1082882 | UNiTY vs Apogee Betclic | Stake Ranked Episode 6: Closed Qualifier | Apogee Betclic | 41.5% | 58.5% | exchange | https://polymarket.com/event/cs2-unity-bca-2026-10-22 | 2026-10-22T03:50:57.571907Z |
| 2026-10-26T03:00:00Z | 1082858 | Ground Zero vs Off Chops | DFRAG Invitational 2026 | Off Chops | **blank** | **blank** | research_rank | (none) | - |
| 2026-10-26T03:00:00Z | 1082859 | NEXVOID vs Alter Ego | DFRAG Invitational 2026 | NEXVOID | 68.2% | 31.8% | model_vrs | https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md | 2026-10-22T03:54:09.001755Z |
| 2026-10-27T03:00:00Z | 1082860 | FlyQuest vs Staqued | DFRAG Invitational 2026 | FlyQuest | **blank** | **blank** | research_rank_single | (none) | - |
| 2026-10-27T03:00:00Z | 1082861 | Rooster vs Abyssal | DFRAG Invitational 2026 | Abyssal | 48.2% | 51.8% | model_vrs | https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md | 2026-10-22T03:54:09.001755Z |
| 2026-10-31T09:00:00Z | 1082792 | HOTU vs The Huns | Moscow Cyber Games 2026 | HOTU | 85.2% | 14.8% | model_vrs | https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md | 2026-10-22T03:54:09.001755Z |
| 2026-10-31T13:00:00Z | 1082793 | 5star vs 1WIN | Moscow Cyber Games 2026 | 1WIN | 24.3% | 75.7% | model_vrs | https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md | 2026-10-22T03:54:09.001755Z |

## Gap detail (rows with no pick, or a pick with no percentage)

### 1081597 — benched gods vs TitanFlow

- Competition: CCT Europe 2026 Challengers #8 (tier `c`)
- Start: `2026-10-22T11:00:00Z`  Lock: `2026-10-22T10:54:00Z`  State: `open`
- Pick: `None`  Probabilities: `null`  Method: `None`
- Hotspawn fixture page: https://www.hotspawn.com/matches/benched-gods-vs-titanflow-cct-europe-2026-challengers-8-1081597
- HLTV context source: None
- Published limitation/reason: No exact team-pair and UTC-start match in retrieved feed. HLTV / esportsbook fallbacks, the Valve VRS model and one-sided Valve standings evidence did not establish a verified line, a two-team ranking pair, or single-team ranking evidence.
- Flags: []
- Attempt ledger:
  - tier `None` status `unresolved` — No exact team-pair and UTC-start match in retrieved feed. (https://gamma-api.polymarket.com/sports)
  - tier `None` status `unresolved` — No unique exact team-pair and UTC-start match in the retrieved HLTV list; renamed teams are not inferred. (https://www.hltv.org/matches)
  - tier `None` status `unresolved` — No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - tier `None` status `unresolved` — No exact team-pair and UTC-start match in retrieved feed. (https://gamma-api.polymarket.com/sports)
  - tier `None` status `unresolved` — Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - tier `None` status `error` — HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - tier `None` status `unresolved` — No originated line: benched gods: label appears 2 times in the standings and no lineup was available to tell the rosters apart. (https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)
  - tier `None` status `unresolved` — No verified market line and no usable HLTV ranking evidence: neither team carries a world-ranking number in this fixture. No pick invented. (https://www.hltv.org/ranking/teams)
  - tier `None` status `unresolved` — No one-sided Valve standings pick: 0 of the two teams resolve in the Valve global standings, not exactly one. No pick invented, and no probability derived from a single points value. (https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)

### 1082837 — Zetta vs LOS NINOS

- Competition: CCT South America 2026 Series #7 (tier `c`)
- Start: `2026-10-21T22:00:00Z`  Lock: `2026-10-21T21:54:00Z`  State: `open`
- Pick: `Zetta`  Probabilities: `null`  Method: `research_rank_single`
- Hotspawn fixture page: https://www.hotspawn.com/matches/zetta-vs-los-ninos-cct-south-america-2026-series-7-1082837
- HLTV context source: https://www.hltv.org/matches/2399865/zetta-vs-los-ninos-cct-2026-south-america-series-7
- Published limitation/reason: No verified market line. Research pick only: Zetta is HLTV world #241 (Zetta) while LOS NINOS appears in the same HLTV fixture without a world-ranking number. One-sided ranking evidence, not a market probability, and no percentage is published.
- Flags: ["Research pick on one-sided ranking evidence (only one team is world-ranked): no probability published."]
- Attempt ledger:
  - tier `None` status `unresolved` — Unverified opponent/alias or roster-name mismatch; no fuzzy match used. (https://gamma-api.polymarket.com/sports)
  - tier `None` status `unresolved` — HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. (https://www.hltv.org/matches/2399865/zetta-vs-los-ninos-cct-2026-south-america-series-7)
  - tier `None` status `unresolved` — No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - tier `None` status `unresolved` — Unverified opponent/alias or roster-name mismatch; no fuzzy match used. (https://gamma-api.polymarket.com/sports)
  - tier `None` status `unresolved` — Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - tier `None` status `error` — HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - tier `None` status `unresolved` — No originated line: LOS NINOS: not listed in the Valve global standings. (https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)
  - tier `None` status `resolved` — Exact HLTV fixture identity; one team world-ranked in the ranking page, the other absent from it. No probability derived. (https://www.hltv.org/matches/2399865/zetta-vs-los-ninos-cct-2026-south-america-series-7)

### 1082858 — Ground Zero vs Off Chops

- Competition: DFRAG Invitational 2026 (tier `b`)
- Start: `2026-10-26T03:00:00Z`  Lock: `2026-10-26T02:54:00Z`  State: `open`
- Pick: `Off Chops`  Probabilities: `null`  Method: `research_rank`
- Hotspawn fixture page: https://play.hotspawn.com/cs2-pickems
- HLTV context source: https://www.hltv.org/matches/2399888/ground-zero-vs-off-chops-dfrag-invitational-2026
- Published limitation/reason: No verified market line. Research pick only: Off Chops is HLTV world #142 (Off Chops) against Ground Zero at #143 (Ground Zero) in the same fixture. This is a ranking-order signal, not a market probability.
- Flags: ["Research pick without a market line: qualitative evidence only, no probability published."]
- Attempt ledger:
  - tier `None` status `unresolved` — No exact team-pair and UTC-start match in retrieved feed. (https://gamma-api.polymarket.com/sports)
  - tier `None` status `unresolved` — HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. (https://www.hltv.org/matches/2399888/ground-zero-vs-off-chops-dfrag-invitational-2026)
  - tier `None` status `unresolved` — No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - tier `None` status `unresolved` — No exact team-pair and UTC-start match in retrieved feed. (https://gamma-api.polymarket.com/sports)
  - tier `None` status `unresolved` — Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - tier `None` status `error` — HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - tier `None` status `unresolved` — No originated line: Off Chops: not listed in the Valve global standings. (https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)
  - tier `None` status `resolved` — Exact HLTV fixture identity and both world rankings used; no probability derived. (https://www.hltv.org/matches/2399888/ground-zero-vs-off-chops-dfrag-invitational-2026)

### 1082860 — FlyQuest vs Staqued

- Competition: DFRAG Invitational 2026 (tier `b`)
- Start: `2026-10-27T03:00:00Z`  Lock: `2026-10-27T02:54:00Z`  State: `open`
- Pick: `FlyQuest`  Probabilities: `null`  Method: `research_rank_single`
- Hotspawn fixture page: https://play.hotspawn.com/cs2-pickems
- HLTV context source: https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026
- Published limitation/reason: No verified market line. Research pick only: FlyQuest is HLTV world #61 (FlyQuest) while Staqued appears in the same HLTV fixture without a world-ranking number. One-sided ranking evidence, not a market probability, and no percentage is published.
- Flags: ["Research pick on one-sided ranking evidence (only one team is world-ranked): no probability published."]
- Attempt ledger:
  - tier `None` status `unresolved` — No exact team-pair and UTC-start match in retrieved feed. (https://gamma-api.polymarket.com/sports)
  - tier `None` status `unresolved` — HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. (https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026)
  - tier `None` status `unresolved` — No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - tier `None` status `unresolved` — No exact team-pair and UTC-start match in retrieved feed. (https://gamma-api.polymarket.com/sports)
  - tier `None` status `unresolved` — Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - tier `None` status `error` — HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - tier `None` status `unresolved` — No originated line: Staqued: not listed in the Valve global standings. (https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)
  - tier `None` status `resolved` — Exact HLTV fixture identity; one team world-ranked in the ranking page, the other absent from it. No probability derived. (https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026)


## Snapshot-level source checks

| Source | Status | HTTP | Observed (UTC) | Bytes |
| --- | --- | --- | --- | --- |
| Hotspawn CS2 fixtures | ok | 200 | 2026-10-21T19:54:09.001755Z | 60694 |
| Hotspawn CS2 lobby | ok | 200 | 2026-10-21T19:54:13.823314Z | 266599 |
| Hotspawn general lobby | ok | 200 | 2026-10-21T19:54:14.523799Z | 267408 |
| Polymarket sports registry | ok | 200 | 2026-10-21T19:37:29.797275Z | 155628 |
| Polymarket events page 1 | ok | 200 | 2026-10-21T19:52:25.831498Z | 3388159 |
| HLTV fallback discovery | ok | 200 | 2026-10-21T19:54:15.249487Z | 838680 |
| HLTV match 1082837 | ok | 200 | 2026-10-21T19:54:16.470420Z | 316559 |
| HLTV match 1081870 | ok | 200 | 2026-10-21T19:54:16.965101Z | 433851 |
| HLTV match 1081600 | ok | 200 | 2026-10-21T19:54:17.597067Z | 388467 |
| HLTV match 1082858 | ok | 200 | 2026-10-21T19:54:18.153141Z | 369870 |
| HLTV match 1082859 | ok | 200 | 2026-10-21T19:54:18.687480Z | 398263 |
| HLTV match 1082860 | ok | 200 | 2026-10-21T19:54:19.164664Z | 337613 |
| HLTV match 1082861 | ok | 200 | 2026-10-21T19:54:20.337193Z | 379606 |
| HLTV match 1082792 | ok | 200 | 2026-10-21T19:54:21.096193Z | 427449 |
| HLTV match 1082793 | ok | 200 | 2026-10-21T19:54:21.917575Z | 429025 |
| Pinnacle esports fixtures | ok | 200 | 2026-10-21T19:42:47.338080Z | 106619 |
| Pinnacle esports moneylines | ok | 200 | 2026-10-21T19:43:15.372082Z | 593554 |
| Thunderpick fallback access | ok | 200 | 2026-10-21T19:54:22.731709Z | 14610 |
| GG.BET fallback access | error | 403 | None | None |
| Book listing re-observation egw-V1JAWhPomg-infinite-insiders | error | 403 | None | None |
| Book listing re-observation egw-0U32SId-H-procyon-los-ninos | error | None | None | None |
| Book listing re-observation pin-1638536356-period0-ml-v3767145143 | ok | 200 | 2026-10-21T19:43:15.369135Z | 593554 |
| Book listing re-observation pin-1638595724-period0-ml-v3767145819 | ok | 200 | 2026-10-21T19:43:15.412092Z | 593554 |
| Book listing re-observation poly-5778024-match-winner | ok | 200 | 2026-10-21T19:55:54.430293Z | 5204 |
| Book listing re-observation poly-5787759-match-winner | ok | 200 | 2026-10-21T19:55:54.451795Z | 5267 |
| Book listing re-observation egw-rW6Ymkl0D-ex-6666-privateer | error | None | None | None |
| Book listing re-observation egw-rW6Ymkl0D-ex-6666-privateer-1010z | error | None | None | None |
| Book listing re-observation egw-41yaj8BdVx-sangal-aurora-young-blud | error | None | None | None |
| Book listing re-observation egw-NTRtiger-l6k0vg5-nemesis-nuclear | error | None | None | None |
| Book listing re-observation egw-V1JAWhPomg-astral-leo | error | None | None | None |
| Book listing re-observation egw-Nk9F-Ov54e-fireflux-ex6666 | error | None | None | None |
| Book listing re-observation egw-rW8GEyWK-lavked-ex6666 | error | None | None | None |
| Book listing re-observation stavka-cybershoke-blinkdagger-1082762 | ok | 200 | 2026-10-21T19:57:44.625275Z | 472067 |
| Valve VRS standings index 2026 | ok | 200 | 2026-10-21T19:57:44.852011Z | 46751 |
| Valve VRS standings commit | ok | 200 | 2026-10-21T19:57:45.108631Z | 3621 |
| Valve VRS global standings | ok | 200 | 2026-10-21T19:57:45.153842Z | 77872 |

## Snapshot issues

- `feed_status` 63 feed entries are not open by sourced timestamps/status. They remain in All matches and are not treated as future picks. (https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1)
