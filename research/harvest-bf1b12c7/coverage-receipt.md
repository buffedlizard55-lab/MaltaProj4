# Live coverage receipt — session e334b970

**Capture clock (fixtures observed at):** `2026-10-24T17:52:00.825406Z`  
**Board built at:** `2026-10-24T17:55:33.590989Z`  
**Accounting evaluated at:** `2026-10-24T17:52:00.825406Z` (the capture's own clock, never the reader's)

| Measure | Value |
| --- | --- |
| Hotspawn CS2 feed rows | 81 |
| Board rows | 81 |
| Inventory coverage | `verified` |
| Open matches | 19 |
| Open with a pick | 19 |
| Open with a win probability | 19 |
| Open without a pick | 0 |

## Evidence tier behind each pick

| Method | Rows | Tier |
| --- | --- | --- |
| `bookmaker_fallback` | 3 | Bookmaker listing (dated, identity-verified two-way line) |
| `exchange` | 11 | Exchange line (Polymarket mid, two-sided, within gate) |
| `exchange_wide` | 1 | Wide exchange line (published spread, low precision) |
| `model_vrs` | 3 | Originated line (Valve's official standings + published expectation formula) |
| `model_vrs_mirror` | 1 | Originated line (HLTV's dated mirror of Valve's ranking) |

## Unresolved open rows and why

None: every open match carried a sourced pick and a win probability at this capture.
## Source read results

| Source | HTTP | Status | Observed | Bytes |
| --- | --- | --- | --- | --- |
| Hotspawn CS2 fixtures | 200 | ok | 2026-10-24T17:52:00.825406Z | 63291 |
| Hotspawn CS2 lobby | 200 | ok | 2026-10-24T17:52:02.113494Z | 328533 |
| Hotspawn general lobby | 200 | ok | 2026-10-24T17:52:02.868582Z | 329511 |
| HLTV Valve ranking mirror (dated view) | 200 | ok | 2026-10-24T17:52:03.349393Z | 1666172 |
| Polymarket sports registry | 200 | ok | 2026-10-24T17:40:45.502986Z | 155942 |
| Polymarket events page 1 | 200 | ok | 2026-10-24T17:47:58.569351Z | 3078950 |
| HLTV fallback discovery | 200 | ok | 2026-10-24T17:52:04.855551Z | 616363 |
| HLTV match 1083123 | 200 | ok | 2026-10-24T17:52:05.334441Z | 388740 |
| HLTV match 1081156 | 200 | ok | 2026-10-24T17:52:05.906079Z | 393917 |
| HLTV match 1079200 | 200 | ok | 2026-10-24T17:52:06.465150Z | 428549 |
| HLTV match 1082858 | 200 | ok | 2026-10-24T17:52:07.044654Z | 371614 |
| HLTV match 1082859 | 200 | ok | 2026-10-24T17:52:07.576441Z | 397402 |
| HLTV match 1082860 | 200 | ok | 2026-10-24T17:52:08.376997Z | 336620 |
| HLTV match 1082792 | 200 | ok | 2026-10-24T17:52:08.855679Z | 428676 |
| HLTV match 1082793 | 200 | ok | 2026-10-24T17:52:09.471036Z | 427365 |
| Pinnacle esports fixtures | 200 | ok | 2026-10-24T17:39:02.798370Z | 95586 |
| Pinnacle esports moneylines | 200 | ok | 2026-10-24T17:40:10.826317Z | 393988 |
| Thunderpick fallback access | 200 | ok | 2026-10-24T17:52:10.429518Z | 14610 |
| GG.BET fallback access | 403 | error | None | None |
| BO3.gg CS2 upcoming feed page 1 | 200 | ok | 2026-10-24T17:53:51.401499Z | 220350 |
| BO3.gg CS2 upcoming feed page 2 | 200 | ok | 2026-10-24T17:53:52.106462Z | 208897 |
| BO3.gg CS2 upcoming feed page 3 | 200 | ok | 2026-10-24T17:53:52.317763Z | 104656 |
| Book listing gap recheck 1082792 | 403 | error | None | None |
| Book listing gap recheck 1082793 | None | error | None | None |
| Valve VRS standings index 2026 | 200 | ok | 2026-10-24T17:55:33.157966Z | 46751 |
| Valve VRS standings commit | 200 | ok | 2026-10-24T17:55:33.369294Z | 3621 |
| Valve VRS global standings | 200 | ok | 2026-10-24T17:55:33.530426Z | 77872 |

Accounting and provenance shape only. Source truth and the arithmetic behind every percentage are replayed independently by verification-c6/audit_snapshot.py.

