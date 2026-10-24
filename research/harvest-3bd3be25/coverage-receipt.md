# Live coverage receipt — session e334b970

**Capture clock (fixtures observed at):** `2026-10-24T16:59:57.117225Z`  
**Board built at:** `2026-10-24T17:03:28.115064Z`  
**Accounting evaluated at:** `2026-10-24T16:59:57.117225Z` (the capture's own clock, never the reader's)

| Measure | Value |
| --- | --- |
| Hotspawn CS2 feed rows | 83 |
| Board rows | 83 |
| Inventory coverage | `verified` |
| Open matches | 20 |
| Open with a pick | 20 |
| Open with a win probability | 20 |
| Open without a pick | 0 |

## Evidence tier behind each pick

| Method | Rows | Tier |
| --- | --- | --- |
| `bookmaker_fallback` | 3 | Bookmaker listing (dated, identity-verified two-way line) |
| `exchange` | 12 | Exchange line (Polymarket mid, two-sided, within gate) |
| `exchange_wide` | 1 | Wide exchange line (published spread, low precision) |
| `model_vrs` | 3 | Originated line (Valve's official standings + published expectation formula) |
| `model_vrs_mirror` | 1 | Originated line (HLTV's dated mirror of Valve's ranking) |

## Unresolved open rows and why

None: every open match carried a sourced pick and a win probability at this capture.
## Source read results

| Source | HTTP | Status | Observed | Bytes |
| --- | --- | --- | --- | --- |
| Hotspawn CS2 fixtures | 200 | ok | 2026-10-24T16:59:57.117225Z | 64837 |
| Hotspawn CS2 lobby | 200 | ok | 2026-10-24T16:59:58.236664Z | 347956 |
| Hotspawn general lobby | 200 | ok | 2026-10-24T16:59:58.944278Z | 348979 |
| HLTV Valve ranking mirror (dated view) | 200 | ok | 2026-10-24T16:59:59.410314Z | 1667531 |
| Polymarket sports registry | 200 | ok | 2026-10-24T16:57:50.245380Z | 155942 |
| Polymarket events page 1 | 200 | ok | 2026-10-24T16:57:24.265332Z | 3266455 |
| HLTV fallback discovery | 200 | ok | 2026-10-24T17:00:01.543082Z | 614978 |
| HLTV match 1083123 | 200 | ok | 2026-10-24T17:00:02.037753Z | 387241 |
| HLTV match 1081156 | 200 | ok | 2026-10-24T17:00:02.525087Z | 391904 |
| HLTV match 1079200 | 200 | ok | 2026-10-24T17:00:02.971421Z | 427046 |
| HLTV match 1082858 | 200 | ok | 2026-10-24T17:00:03.438702Z | 370088 |
| HLTV match 1082859 | 200 | ok | 2026-10-24T17:00:03.806906Z | 395871 |
| HLTV match 1082860 | 200 | ok | 2026-10-24T17:00:04.285154Z | 335057 |
| HLTV match 1082792 | 200 | ok | 2026-10-24T17:00:04.651352Z | 427143 |
| HLTV match 1082793 | 200 | ok | 2026-10-24T17:00:05.383275Z | 427599 |
| Pinnacle esports fixtures | 200 | ok | 2026-10-24T16:53:45.788473Z | 94290 |
| Pinnacle esports moneylines | 200 | ok | 2026-10-24T16:54:54.826640Z | 480329 |
| Thunderpick fallback access | 200 | ok | 2026-10-24T17:00:06.134640Z | 14610 |
| GG.BET fallback access | 403 | error | None | None |
| BO3.gg CS2 upcoming feed page 1 | 200 | ok | 2026-10-24T17:01:46.791418Z | 223176 |
| BO3.gg CS2 upcoming feed page 2 | 200 | ok | 2026-10-24T17:01:47.006712Z | 206465 |
| BO3.gg CS2 upcoming feed page 3 | 200 | ok | 2026-10-24T17:01:47.188659Z | 104656 |
| Book listing gap recheck 1082792 | 403 | error | None | None |
| Book listing gap recheck 1082793 | None | error | None | None |
| Valve VRS standings index 2026 | 200 | ok | 2026-10-24T17:03:27.687341Z | 46751 |
| Valve VRS standings commit | 200 | ok | 2026-10-24T17:03:27.917826Z | 3621 |
| Valve VRS global standings | 200 | ok | 2026-10-24T17:03:27.957515Z | 77872 |

Accounting and provenance shape only. Source truth and the arithmetic behind every percentage are replayed independently by verification-c6/audit_snapshot.py.

