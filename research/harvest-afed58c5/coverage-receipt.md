# Live coverage receipt — session e334b970

**Capture clock (fixtures observed at):** `2026-10-24T16:43:03.622123Z`  
**Board built at:** `2026-10-24T16:46:36.541544Z`  
**Accounting evaluated at:** `2026-10-24T16:43:03.622123Z` (the capture's own clock, never the reader's)

| Measure | Value |
| --- | --- |
| Hotspawn CS2 feed rows | 83 |
| Board rows | 83 |
| Inventory coverage | `verified` |
| Open matches | 22 |
| Open with a pick | 21 |
| Open with a win probability | 22 |
| Open without a pick | 1 |

## Evidence tier behind each pick

| Method | Rows | Tier |
| --- | --- | --- |
| `bookmaker_fallback` | 3 | Bookmaker listing (dated, identity-verified two-way line) |
| `exchange` | 14 | Exchange line (Polymarket mid, two-sided, within gate) |
| `exchange_wide` | 1 | Wide exchange line (published spread, low precision) |
| `model_vrs` | 2 | Originated line (Valve's official standings + published expectation formula) |
| `model_vrs_mirror` | 1 | Originated line (HLTV's dated mirror of Valve's ranking) |

## Unresolved open rows and why

### 1079200 — Color vs ex-Zero Tenacity

*Competition:* NODWIN Clutch Series #13 · *start* `2026-10-25T18:00:00Z` · *lock* `2026-10-25T17:54:00Z`

*Limitation:* Equal verified prices; no directional edge.

*Official fixture link:* https://www.hotspawn.com/matches/color-vs-ex-zero-tenacity-nodwin-clutch-series-13-1079200

| Provider | Status | Reason | Source |
| --- | --- | --- | --- |
| Polymarket | resolved | Exact pair and UTC start; two-way series winner validated. | https://gamma-api.polymarket.com/markets/6072812 |

## Source read results

| Source | HTTP | Status | Observed | Bytes |
| --- | --- | --- | --- | --- |
| Hotspawn CS2 fixtures | 200 | ok | 2026-10-24T16:43:03.622123Z | 64837 |
| Hotspawn CS2 lobby | 200 | ok | 2026-10-24T16:43:04.973818Z | 346198 |
| Hotspawn general lobby | 200 | ok | 2026-10-24T16:43:05.677555Z | 347221 |
| HLTV Valve ranking mirror (dated view) | 200 | ok | 2026-10-24T16:43:06.721981Z | 1668401 |
| Polymarket sports registry | 200 | ok | 2026-10-24T16:37:50.570271Z | 155942 |
| Polymarket events page 1 | 200 | ok | 2026-10-24T16:40:56.589908Z | 3257625 |
| HLTV fallback discovery | 200 | ok | 2026-10-24T16:43:08.856760Z | 615779 |
| HLTV match 1083123 | 200 | ok | 2026-10-24T16:43:09.380665Z | 391037 |
| HLTV match 1081156 | 200 | ok | 2026-10-24T16:43:10.175015Z | 395699 |
| HLTV match 1082858 | 200 | ok | 2026-10-24T16:43:10.821597Z | 373879 |
| HLTV match 1082859 | 200 | ok | 2026-10-24T16:43:11.366006Z | 399663 |
| HLTV match 1082860 | 200 | ok | 2026-10-24T16:43:11.949148Z | 338850 |
| HLTV match 1082792 | 200 | ok | 2026-10-24T16:43:12.777714Z | 430933 |
| HLTV match 1082793 | 200 | ok | 2026-10-24T16:43:13.475331Z | 433290 |
| Pinnacle esports fixtures | 200 | ok | 2026-10-24T16:38:40.847245Z | 100575 |
| Pinnacle esports moneylines | 200 | ok | 2026-10-24T16:39:48.866946Z | 498940 |
| Thunderpick fallback access | 200 | ok | 2026-10-24T16:43:14.309771Z | 14610 |
| GG.BET fallback access | 403 | error | None | None |
| BO3.gg CS2 upcoming feed page 1 | 200 | ok | 2026-10-24T16:44:55.197395Z | 219814 |
| BO3.gg CS2 upcoming feed page 2 | 200 | ok | 2026-10-24T16:44:55.515847Z | 210773 |
| BO3.gg CS2 upcoming feed page 3 | 200 | ok | 2026-10-24T16:44:55.727647Z | 112793 |
| Book listing gap recheck 1082792 | 403 | error | None | None |
| Book listing gap recheck 1082793 | None | error | None | None |
| Valve VRS standings index 2026 | 200 | ok | 2026-10-24T16:46:36.198370Z | 46751 |
| Valve VRS standings commit | 200 | ok | 2026-10-24T16:46:36.378994Z | 3621 |
| Valve VRS global standings | 200 | ok | 2026-10-24T16:46:36.445157Z | 77872 |

Accounting and provenance shape only. Source truth and the arithmetic behind every percentage are replayed independently by verification-c6/audit_snapshot.py.

