# Live coverage receipt — session e334b970

**Capture clock (fixtures observed at):** `2026-10-24T17:26:24.804410Z`  
**Board built at:** `2026-10-24T17:30:00.255965Z`  
**Accounting evaluated at:** `2026-10-24T17:26:24.804410Z` (the capture's own clock, never the reader's)

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
| Hotspawn CS2 fixtures | 200 | ok | 2026-10-24T17:26:24.804410Z | 63290 |
| Hotspawn CS2 lobby | 200 | ok | 2026-10-24T17:26:26.035715Z | 328543 |
| Hotspawn general lobby | 200 | ok | 2026-10-24T17:26:26.849102Z | 329521 |
| HLTV Valve ranking mirror (dated view) | 200 | ok | 2026-10-24T17:26:27.322574Z | 1664913 |
| Polymarket sports registry | 200 | ok | 2026-10-24T17:22:04.086740Z | 155942 |
| Polymarket events page 1 | 200 | ok | 2026-10-24T17:23:31.104540Z | 3347443 |
| HLTV fallback discovery | 200 | ok | 2026-10-24T17:26:29.419769Z | 615357 |
| HLTV match 1083123 | 200 | ok | 2026-10-24T17:26:30.043191Z | 387515 |
| HLTV match 1081156 | 200 | ok | 2026-10-24T17:26:31.332477Z | 393464 |
| HLTV match 1079200 | 200 | ok | 2026-10-24T17:26:32.029845Z | 428098 |
| HLTV match 1082858 | 200 | ok | 2026-10-24T17:26:32.753064Z | 371164 |
| HLTV match 1082859 | 200 | ok | 2026-10-24T17:26:33.538919Z | 396947 |
| HLTV match 1082860 | 200 | ok | 2026-10-24T17:26:34.592410Z | 336133 |
| HLTV match 1082792 | 200 | ok | 2026-10-24T17:26:35.890892Z | 428216 |
| HLTV match 1082793 | 200 | ok | 2026-10-24T17:26:36.629441Z | 428680 |
| Pinnacle esports fixtures | 200 | ok | 2026-10-24T17:23:57.033886Z | 95484 |
| Pinnacle esports moneylines | 200 | ok | 2026-10-24T17:25:06.061645Z | 389885 |
| Thunderpick fallback access | 200 | ok | 2026-10-24T17:26:37.324553Z | 14610 |
| GG.BET fallback access | 403 | error | None | None |
| BO3.gg CS2 upcoming feed page 1 | 200 | ok | 2026-10-24T17:28:18.284954Z | 223175 |
| BO3.gg CS2 upcoming feed page 2 | 200 | ok | 2026-10-24T17:28:18.694203Z | 206465 |
| BO3.gg CS2 upcoming feed page 3 | 200 | ok | 2026-10-24T17:28:19.106079Z | 104656 |
| Book listing gap recheck 1082792 | 403 | error | None | None |
| Book listing gap recheck 1082793 | None | error | None | None |
| Valve VRS standings index 2026 | 200 | ok | 2026-10-24T17:29:59.728535Z | 46751 |
| Valve VRS standings commit | 200 | ok | 2026-10-24T17:29:59.969272Z | 3621 |
| Valve VRS global standings | 200 | ok | 2026-10-24T17:30:00.147582Z | 77872 |

Accounting and provenance shape only. Source truth and the arithmetic behind every percentage are replayed independently by verification-c6/audit_snapshot.py.

