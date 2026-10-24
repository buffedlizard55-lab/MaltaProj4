# Live coverage receipt — session e334b970

**Capture clock (fixtures observed at):** `2026-10-24T17:15:15.645274Z`  
**Board built at:** `2026-10-24T17:18:48.961351Z`  
**Accounting evaluated at:** `2026-10-24T17:15:15.645274Z` (the capture's own clock, never the reader's)

| Measure | Value |
| --- | --- |
| Hotspawn CS2 feed rows | 81 |
| Board rows | 81 |
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
| Hotspawn CS2 fixtures | 200 | ok | 2026-10-24T17:15:15.645274Z | 63290 |
| Hotspawn CS2 lobby | 200 | ok | 2026-10-24T17:15:16.628269Z | 329113 |
| Hotspawn general lobby | 200 | ok | 2026-10-24T17:15:17.312986Z | 330074 |
| HLTV Valve ranking mirror (dated view) | 200 | ok | 2026-10-24T17:15:17.784918Z | 1664472 |
| Polymarket sports registry | 200 | ok | 2026-10-24T16:57:50.602139Z | 155942 |
| Polymarket events page 1 | 200 | ok | 2026-10-24T17:13:44.622457Z | 3285699 |
| HLTV fallback discovery | 200 | ok | 2026-10-24T17:15:19.970438Z | 614652 |
| HLTV match 1083123 | 200 | ok | 2026-10-24T17:15:20.410373Z | 388176 |
| HLTV match 1081156 | 200 | ok | 2026-10-24T17:15:21.030566Z | 393311 |
| HLTV match 1079200 | 200 | ok | 2026-10-24T17:15:21.686324Z | 427946 |
| HLTV match 1082858 | 200 | ok | 2026-10-24T17:15:22.602008Z | 371016 |
| HLTV match 1082859 | 200 | ok | 2026-10-24T17:15:23.169585Z | 396803 |
| HLTV match 1082860 | 200 | ok | 2026-10-24T17:15:24.196572Z | 335987 |
| HLTV match 1082792 | 200 | ok | 2026-10-24T17:15:24.904897Z | 428076 |
| HLTV match 1082793 | 200 | ok | 2026-10-24T17:15:25.637619Z | 428528 |
| Pinnacle esports fixtures | 200 | ok | 2026-10-24T17:08:50.043815Z | 93899 |
| Pinnacle esports moneylines | 200 | ok | 2026-10-24T17:10:01.070557Z | 447393 |
| Thunderpick fallback access | 200 | ok | 2026-10-24T17:15:26.539351Z | 14610 |
| GG.BET fallback access | 403 | error | None | None |
| BO3.gg CS2 upcoming feed page 1 | 200 | ok | 2026-10-24T17:17:07.323425Z | 223175 |
| BO3.gg CS2 upcoming feed page 2 | 200 | ok | 2026-10-24T17:17:07.680890Z | 206465 |
| BO3.gg CS2 upcoming feed page 3 | 200 | ok | 2026-10-24T17:17:08.158112Z | 104656 |
| Book listing gap recheck 1082792 | 403 | error | None | None |
| Book listing gap recheck 1082793 | None | error | None | None |
| Valve VRS standings index 2026 | 200 | ok | 2026-10-24T17:18:48.665287Z | 46751 |
| Valve VRS standings commit | 200 | ok | 2026-10-24T17:18:48.832596Z | 3621 |
| Valve VRS global standings | 200 | ok | 2026-10-24T17:18:48.873020Z | 77872 |

Accounting and provenance shape only. Source truth and the arithmetic behind every percentage are replayed independently by verification-c6/audit_snapshot.py.

