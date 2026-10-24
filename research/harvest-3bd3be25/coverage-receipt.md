# Live coverage receipt — session e334b970

**Capture clock (fixtures observed at):** `2026-10-24T17:48:54.497110Z`  
**Board built at:** `2026-10-24T17:52:26.059241Z`  
**Accounting evaluated at:** `2026-10-24T17:48:54.497110Z` (the capture's own clock, never the reader's)

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
| Hotspawn CS2 fixtures | 200 | ok | 2026-10-24T17:48:54.497110Z | 63290 |
| Hotspawn CS2 lobby | 200 | ok | 2026-10-24T17:48:55.616408Z | 328531 |
| Hotspawn general lobby | 200 | ok | 2026-10-24T17:48:56.361786Z | 329509 |
| HLTV Valve ranking mirror (dated view) | 200 | ok | 2026-10-24T17:48:56.939468Z | 1666966 |
| Polymarket sports registry | 200 | ok | 2026-10-24T17:40:45.882057Z | 155942 |
| Polymarket events page 1 | 200 | ok | 2026-10-24T17:47:58.936406Z | 3078950 |
| HLTV fallback discovery | 200 | ok | 2026-10-24T17:48:58.204539Z | 617209 |
| HLTV match 1083123 | 200 | ok | 2026-10-24T17:48:58.812856Z | 389542 |
| HLTV match 1081156 | 200 | ok | 2026-10-24T17:48:59.255242Z | 394722 |
| HLTV match 1079200 | 200 | ok | 2026-10-24T17:48:59.783059Z | 429351 |
| HLTV match 1082858 | 200 | ok | 2026-10-24T17:49:00.160863Z | 372450 |
| HLTV match 1082859 | 200 | ok | 2026-10-24T17:49:00.640980Z | 398205 |
| HLTV match 1082860 | 200 | ok | 2026-10-24T17:49:01.470793Z | 337421 |
| HLTV match 1082792 | 200 | ok | 2026-10-24T17:49:02.114987Z | 429477 |
| HLTV match 1082793 | 200 | ok | 2026-10-24T17:49:02.622754Z | 428018 |
| Pinnacle esports fixtures | 200 | ok | 2026-10-24T17:39:02.882079Z | 95586 |
| Pinnacle esports moneylines | 200 | ok | 2026-10-24T17:40:10.945446Z | 393988 |
| Thunderpick fallback access | 200 | ok | 2026-10-24T17:49:03.338636Z | 14610 |
| GG.BET fallback access | 403 | error | None | None |
| BO3.gg CS2 upcoming feed page 1 | 200 | ok | 2026-10-24T17:50:44.239632Z | 223175 |
| BO3.gg CS2 upcoming feed page 2 | 200 | ok | 2026-10-24T17:50:44.502844Z | 206465 |
| BO3.gg CS2 upcoming feed page 3 | 200 | ok | 2026-10-24T17:50:44.904900Z | 104656 |
| Book listing gap recheck 1082792 | 403 | error | None | None |
| Book listing gap recheck 1082793 | None | error | None | None |
| Valve VRS standings index 2026 | 200 | ok | 2026-10-24T17:52:25.668503Z | 46751 |
| Valve VRS standings commit | 200 | ok | 2026-10-24T17:52:25.916925Z | 3621 |
| Valve VRS global standings | 200 | ok | 2026-10-24T17:52:25.991963Z | 77872 |

Accounting and provenance shape only. Source truth and the arithmetic behind every percentage are replayed independently by verification-c6/audit_snapshot.py.

