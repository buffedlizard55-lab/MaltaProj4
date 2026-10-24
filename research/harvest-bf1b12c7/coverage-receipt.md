# Live coverage receipt — session e334b970

**Capture clock (fixtures observed at):** `2026-10-24T16:50:50.220894Z`  
**Board built at:** `2026-10-24T16:54:24.311021Z`  
**Accounting evaluated at:** `2026-10-24T16:50:50.220894Z` (the capture's own clock, never the reader's)

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
| Hotspawn CS2 fixtures | 200 | ok | 2026-10-24T16:50:50.220894Z | 64837 |
| Hotspawn CS2 lobby | 200 | ok | 2026-10-24T16:50:51.420610Z | 346186 |
| Hotspawn general lobby | 200 | ok | 2026-10-24T16:50:52.152767Z | 347209 |
| HLTV Valve ranking mirror (dated view) | 200 | ok | 2026-10-24T16:50:52.664959Z | 1668299 |
| Polymarket sports registry | 200 | ok | 2026-10-24T16:40:35.904807Z | 155942 |
| Polymarket events page 1 | 200 | ok | 2026-10-24T16:49:07.921605Z | 3262918 |
| HLTV fallback discovery | 200 | ok | 2026-10-24T16:50:54.658913Z | 615729 |
| HLTV match 1083123 | 200 | ok | 2026-10-24T16:50:55.116406Z | 387989 |
| HLTV match 1081156 | 200 | ok | 2026-10-24T16:50:55.686414Z | 392665 |
| HLTV match 1079200 | 200 | ok | 2026-10-24T16:50:56.433698Z | 427810 |
| HLTV match 1082858 | 200 | ok | 2026-10-24T16:50:57.460065Z | 370839 |
| HLTV match 1082859 | 200 | ok | 2026-10-24T16:50:58.592115Z | 396626 |
| HLTV match 1082860 | 200 | ok | 2026-10-24T16:50:59.603200Z | 335810 |
| HLTV match 1082792 | 200 | ok | 2026-10-24T16:51:00.550008Z | 427896 |
| HLTV match 1082793 | 200 | ok | 2026-10-24T16:51:01.103489Z | 428356 |
| Pinnacle esports fixtures | 200 | ok | 2026-10-24T16:38:40.406605Z | 100575 |
| Pinnacle esports moneylines | 200 | ok | 2026-10-24T16:39:49.431289Z | 498940 |
| Thunderpick fallback access | 200 | ok | 2026-10-24T16:51:01.797041Z | 14610 |
| GG.BET fallback access | 403 | error | None | None |
| BO3.gg CS2 upcoming feed page 1 | 200 | ok | 2026-10-24T16:52:42.797579Z | 219814 |
| BO3.gg CS2 upcoming feed page 2 | 200 | ok | 2026-10-24T16:52:43.163106Z | 210773 |
| BO3.gg CS2 upcoming feed page 3 | 200 | ok | 2026-10-24T16:52:43.364023Z | 112793 |
| Book listing gap recheck 1082792 | 403 | error | None | None |
| Book listing gap recheck 1082793 | None | error | None | None |
| Valve VRS standings index 2026 | 200 | ok | 2026-10-24T16:54:23.942983Z | 46751 |
| Valve VRS standings commit | 200 | ok | 2026-10-24T16:54:24.173609Z | 3621 |
| Valve VRS global standings | 200 | ok | 2026-10-24T16:54:24.233707Z | 77872 |

Accounting and provenance shape only. Source truth and the arithmetic behind every percentage are replayed independently by verification-c6/audit_snapshot.py.

