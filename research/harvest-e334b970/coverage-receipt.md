# Live coverage receipt — session e334b970

**Capture clock (fixtures observed at):** `2026-10-24T05:33:45.062897Z`  
**Board built at:** `2026-10-24T05:37:20.660266Z`  
**Accounting evaluated at:** `2026-10-24T05:33:45.062897Z` (the capture's own clock, never the reader's)

| Measure | Value |
| --- | --- |
| Hotspawn CS2 feed rows | 88 |
| Board rows | 88 |
| Inventory coverage | `verified` |
| Open matches | 25 |
| Open with a pick | 25 |
| Open with a win probability | 25 |
| Open without a pick | 0 |

## Evidence tier behind each pick

| Method | Rows | Tier |
| --- | --- | --- |
| `bookmaker_fallback` | 2 | Bookmaker listing (dated, identity-verified two-way line) |
| `exchange` | 12 | Exchange line (Polymarket mid, two-sided, within gate) |
| `exchange_wide` | 2 | Wide exchange line (published spread, low precision) |
| `model_vrs` | 7 | Originated line (Valve's official standings + published expectation formula) |
| `model_vrs_mirror` | 2 | Originated line (HLTV's dated mirror of Valve's ranking) |

## Unresolved open rows and why

None: every open match carried a sourced pick and a win probability at this capture.
## Source read results

| Source | HTTP | Status | Observed | Bytes |
| --- | --- | --- | --- | --- |
| Hotspawn CS2 fixtures | 200 | ok | 2026-10-24T05:33:45.062897Z | 68712 |
| Hotspawn CS2 lobby | 200 | ok | 2026-10-24T05:33:46.614901Z | 376929 |
| Hotspawn general lobby | 200 | ok | 2026-10-24T05:33:47.429121Z | 378000 |
| HLTV Valve ranking mirror (dated view) | 200 | ok | 2026-10-24T05:33:48.054050Z | 1591256 |
| Polymarket sports registry | 200 | ok | 2026-10-24T05:19:52.374877Z | 155942 |
| Polymarket events page 1 | 200 | ok | 2026-10-24T05:29:50.431722Z | 3176649 |
| HLTV fallback discovery | 200 | ok | 2026-10-24T05:33:49.752058Z | 623224 |
| HLTV match 1081152 | 200 | ok | 2026-10-24T05:33:50.436442Z | 313982 |
| HLTV match 1081153 | 200 | ok | 2026-10-24T05:33:51.037168Z | 280169 |
| HLTV match 1081154 | 200 | ok | 2026-10-24T05:33:51.671948Z | 343733 |
| HLTV match 1082996 | 200 | ok | 2026-10-24T05:33:52.309164Z | 318112 |
| HLTV match 1079198 | 200 | ok | 2026-10-24T05:33:52.855320Z | 329117 |
| HLTV match 1081156 | 200 | ok | 2026-10-24T05:33:53.414322Z | 308805 |
| HLTV match 1081158 | 200 | ok | 2026-10-24T05:33:53.985143Z | 393352 |
| HLTV match 1082858 | 200 | ok | 2026-10-24T05:33:54.611040Z | 286861 |
| HLTV match 1082859 | 200 | ok | 2026-10-24T05:33:55.103287Z | 315137 |
| HLTV match 1082860 | 200 | ok | 2026-10-24T05:33:55.777678Z | 251833 |
| HLTV match 1082861 | 200 | ok | 2026-10-24T05:33:56.283879Z | 293792 |
| HLTV match 1082792 | 200 | ok | 2026-10-24T05:33:56.793742Z | 342904 |
| HLTV match 1082793 | 200 | ok | 2026-10-24T05:33:57.360863Z | 341017 |
| Pinnacle esports fixtures | 200 | ok | 2026-10-24T05:19:24.668086Z | 125271 |
| Pinnacle esports moneylines | 200 | ok | 2026-10-24T05:20:27.693376Z | 698265 |
| Thunderpick fallback access | 200 | ok | 2026-10-24T05:33:57.968043Z | 14610 |
| GG.BET fallback access | 403 | error | None | None |
| BO3.gg CS2 upcoming feed page 1 | 200 | ok | 2026-10-24T05:35:38.825104Z | 229970 |
| BO3.gg CS2 upcoming feed page 2 | 200 | ok | 2026-10-24T05:35:39.070080Z | 203204 |
| BO3.gg CS2 upcoming feed page 3 | 200 | ok | 2026-10-24T05:35:39.314122Z | 183934 |
| Book listing gap recheck 1082861 | 403 | error | None | None |
| Book listing gap recheck 1082996 | None | error | None | None |
| Book listing gap recheck 1082792 | None | error | None | None |
| Book listing gap recheck 1082793 | None | error | None | None |
| Valve VRS standings index 2026 | 200 | ok | 2026-10-24T05:37:20.150370Z | 46751 |
| Valve VRS standings commit | 200 | ok | 2026-10-24T05:37:20.406712Z | 3621 |
| Valve VRS global standings | 200 | ok | 2026-10-24T05:37:20.564188Z | 77872 |

Accounting and provenance shape only. Source truth and the arithmetic behind every percentage are replayed independently by verification-c6/audit_snapshot.py.

