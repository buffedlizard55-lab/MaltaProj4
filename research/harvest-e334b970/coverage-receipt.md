# Live coverage receipt — session e334b970

**Capture clock (fixtures observed at):** `2026-10-24T10:41:46.991787Z`  
**Board built at:** `2026-10-24T10:45:25.990333Z`  
**Accounting evaluated at:** `2026-10-24T10:41:46.991787Z` (the capture's own clock, never the reader's)

| Measure | Value |
| --- | --- |
| Hotspawn CS2 feed rows | 90 |
| Board rows | 90 |
| Inventory coverage | `verified` |
| Open matches | 29 |
| Open with a pick | 29 |
| Open with a win probability | 29 |
| Open without a pick | 0 |

## Evidence tier behind each pick

| Method | Rows | Tier |
| --- | --- | --- |
| `bookmaker_fallback` | 3 | Bookmaker listing (dated, identity-verified two-way line) |
| `exchange` | 15 | Exchange line (Polymarket mid, two-sided, within gate) |
| `exchange_wide` | 5 | Wide exchange line (published spread, low precision) |
| `model_vrs` | 5 | Originated line (Valve's official standings + published expectation formula) |
| `model_vrs_mirror` | 1 | Originated line (HLTV's dated mirror of Valve's ranking) |

## Unresolved open rows and why

None: every open match carried a sourced pick and a win probability at this capture.
## Source read results

| Source | HTTP | Status | Observed | Bytes |
| --- | --- | --- | --- | --- |
| Hotspawn CS2 fixtures | 200 | ok | 2026-10-24T10:41:46.991787Z | 70256 |
| Hotspawn CS2 lobby | 200 | ok | 2026-10-24T10:41:48.235202Z | 411378 |
| Hotspawn general lobby | 200 | ok | 2026-10-24T10:41:49.011003Z | 412562 |
| HLTV Valve ranking mirror (dated view) | 200 | ok | 2026-10-24T10:41:49.617813Z | 1666138 |
| Polymarket sports registry | 200 | ok | 2026-10-24T10:39:55.920381Z | 155942 |
| Polymarket events page 1 | 200 | ok | 2026-10-24T10:41:51.236380Z | 3379665 |
| HLTV fallback discovery | 200 | ok | 2026-10-24T10:41:51.766172Z | 666985 |
| HLTV match 1081152 | 200 | ok | 2026-10-24T10:41:52.332593Z | 392639 |
| HLTV match 1081154 | 200 | ok | 2026-10-24T10:41:53.096526Z | 422546 |
| HLTV match 1083122 | 200 | ok | 2026-10-24T10:41:53.687858Z | 335758 |
| HLTV match 1083123 | 200 | ok | 2026-10-24T10:41:54.221747Z | 382566 |
| HLTV match 1082996 | 200 | ok | 2026-10-24T10:41:54.797564Z | 396555 |
| HLTV match 1079198 | 200 | ok | 2026-10-24T10:41:55.914115Z | 406764 |
| HLTV match 1081156 | 200 | ok | 2026-10-24T10:41:56.949957Z | 386424 |
| HLTV match 1081158 | 200 | ok | 2026-10-24T10:41:57.625813Z | 473464 |
| HLTV match 1082858 | 200 | ok | 2026-10-24T10:41:58.274549Z | 365444 |
| HLTV match 1082859 | 200 | ok | 2026-10-24T10:41:58.827778Z | 391274 |
| HLTV match 1082860 | 200 | ok | 2026-10-24T10:41:59.418574Z | 331627 |
| HLTV match 1082861 | 200 | ok | 2026-10-24T10:42:00.663169Z | 371408 |
| HLTV match 1082792 | 200 | ok | 2026-10-24T10:42:01.195338Z | 423760 |
| HLTV match 1082793 | 200 | ok | 2026-10-24T10:42:02.365681Z | 421741 |
| Pinnacle esports fixtures | 200 | ok | 2026-10-24T10:36:22.739392Z | 120157 |
| Pinnacle esports moneylines | 200 | ok | 2026-10-24T10:37:28.790919Z | 580074 |
| Thunderpick fallback access | 200 | ok | 2026-10-24T10:42:03.061992Z | 14610 |
| GG.BET fallback access | 403 | error | None | None |
| BO3.gg CS2 upcoming feed page 1 | 200 | ok | 2026-10-24T10:43:44.248139Z | 227051 |
| BO3.gg CS2 upcoming feed page 2 | 200 | ok | 2026-10-24T10:43:44.495851Z | 199520 |
| BO3.gg CS2 upcoming feed page 3 | 200 | ok | 2026-10-24T10:43:44.744097Z | 172011 |
| Book listing gap recheck 1082861 | 403 | error | None | None |
| Book listing gap recheck 1082996 | None | error | None | None |
| Book listing gap recheck 1082792 | None | error | None | None |
| Book listing gap recheck 1082793 | None | error | None | None |
| Valve VRS standings index 2026 | 200 | ok | 2026-10-24T10:45:25.460893Z | 46751 |
| Valve VRS standings commit | 200 | ok | 2026-10-24T10:45:25.700491Z | 3621 |
| Valve VRS global standings | 200 | ok | 2026-10-24T10:45:25.887511Z | 77872 |

Accounting and provenance shape only. Source truth and the arithmetic behind every percentage are replayed independently by verification-c6/audit_snapshot.py.

