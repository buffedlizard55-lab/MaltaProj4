# Live coverage receipt — session e334b970

**Capture clock (fixtures observed at):** `2026-10-24T16:30:38.431533Z`  
**Board built at:** `2026-10-24T16:34:10.168603Z`  
**Accounting evaluated at:** `2026-10-24T16:30:38.431533Z` (the capture's own clock, never the reader's)

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
| Hotspawn CS2 fixtures | 200 | ok | 2026-10-24T16:30:38.431533Z | 64837 |
| Hotspawn CS2 lobby | 200 | ok | 2026-10-24T16:30:39.385963Z | 346198 |
| Hotspawn general lobby | 200 | ok | 2026-10-24T16:30:40.161002Z | 347221 |
| HLTV Valve ranking mirror (dated view) | 200 | ok | 2026-10-24T16:30:40.575459Z | 1668806 |
| Polymarket sports registry | 200 | ok | 2026-10-24T16:20:34.768729Z | 155942 |
| Polymarket events page 1 | 200 | ok | 2026-10-24T16:30:42.159784Z | 3247581 |
| HLTV fallback discovery | 200 | ok | 2026-10-24T16:30:42.426115Z | 627676 |
| HLTV match 1083123 | 200 | ok | 2026-10-24T16:30:43.168661Z | 390786 |
| HLTV match 1081156 | 200 | ok | 2026-10-24T16:30:43.809605Z | 395447 |
| HLTV match 1082858 | 200 | ok | 2026-10-24T16:30:44.516234Z | 373627 |
| HLTV match 1082859 | 200 | ok | 2026-10-24T16:30:45.007196Z | 399413 |
| HLTV match 1082860 | 200 | ok | 2026-10-24T16:30:45.549154Z | 338598 |
| HLTV match 1082792 | 200 | ok | 2026-10-24T16:30:46.024340Z | 430683 |
| HLTV match 1082793 | 200 | ok | 2026-10-24T16:30:46.724657Z | 433047 |
| Pinnacle esports fixtures | 200 | ok | 2026-10-24T16:23:34.059399Z | 103575 |
| Pinnacle esports moneylines | 200 | ok | 2026-10-24T16:24:42.092224Z | 500036 |
| Thunderpick fallback access | 200 | ok | 2026-10-24T16:30:47.485926Z | 14610 |
| GG.BET fallback access | 403 | error | None | None |
| BO3.gg CS2 upcoming feed page 1 | 200 | ok | 2026-10-24T16:32:28.538072Z | 219572 |
| BO3.gg CS2 upcoming feed page 2 | 200 | ok | 2026-10-24T16:32:28.821077Z | 210773 |
| BO3.gg CS2 upcoming feed page 3 | 200 | ok | 2026-10-24T16:32:29.020903Z | 112793 |
| Book listing gap recheck 1082792 | 403 | error | None | None |
| Book listing gap recheck 1082793 | None | error | None | None |
| Valve VRS standings index 2026 | 200 | ok | 2026-10-24T16:34:09.753983Z | 46751 |
| Valve VRS standings commit | 200 | ok | 2026-10-24T16:34:09.972466Z | 3621 |
| Valve VRS global standings | 200 | ok | 2026-10-24T16:34:10.099228Z | 77872 |

Accounting and provenance shape only. Source truth and the arithmetic behind every percentage are replayed independently by verification-c6/audit_snapshot.py.

