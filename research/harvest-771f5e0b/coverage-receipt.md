# Live coverage receipt — session e334b970

**Capture clock (fixtures observed at):** `2026-10-24T16:55:27.448416Z`  
**Board built at:** `2026-10-24T16:58:58.772454Z`  
**Accounting evaluated at:** `2026-10-24T16:55:27.448416Z` (the capture's own clock, never the reader's)

| Measure | Value |
| --- | --- |
| Hotspawn CS2 feed rows | 83 |
| Board rows | 83 |
| Inventory coverage | `verified` |
| Open matches | 20 |
| Open with a pick | 19 |
| Open with a win probability | 20 |
| Open without a pick | 1 |

## Evidence tier behind each pick

| Method | Rows | Tier |
| --- | --- | --- |
| `bookmaker_fallback` | 2 | Bookmaker listing (dated, identity-verified two-way line) |
| `exchange` | 12 | Exchange line (Polymarket mid, two-sided, within gate) |
| `exchange_wide` | 2 | Wide exchange line (published spread, low precision) |
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
| Hotspawn CS2 fixtures | 200 | ok | 2026-10-24T16:55:27.448416Z | 64837 |
| Hotspawn CS2 lobby | 200 | ok | 2026-10-24T16:55:28.652184Z | 347956 |
| Hotspawn general lobby | 200 | ok | 2026-10-24T16:55:29.361960Z | 348979 |
| HLTV Valve ranking mirror (dated view) | 200 | ok | 2026-10-24T16:55:29.798535Z | 1667359 |
| Polymarket sports registry | 200 | ok | 2026-10-24T16:40:35.730615Z | 155942 |
| Polymarket events page 1 | 200 | ok | 2026-10-24T16:55:31.135498Z | 3264455 |
| HLTV fallback discovery | 200 | ok | 2026-10-24T16:55:31.527455Z | 614787 |
| HLTV match 1083123 | 200 | ok | 2026-10-24T16:55:31.994473Z | 387050 |
| HLTV match 1081156 | 200 | ok | 2026-10-24T16:55:32.789652Z | 391717 |
| HLTV match 1082858 | 200 | ok | 2026-10-24T16:55:33.266493Z | 369896 |
| HLTV match 1082859 | 200 | ok | 2026-10-24T16:55:33.730433Z | 395667 |
| HLTV match 1082860 | 200 | ok | 2026-10-24T16:55:34.421477Z | 334851 |
| HLTV match 1082792 | 200 | ok | 2026-10-24T16:55:34.865244Z | 426956 |
| HLTV match 1082793 | 200 | ok | 2026-10-24T16:55:35.423863Z | 427409 |
| Pinnacle esports fixtures | 200 | ok | 2026-10-24T16:53:45.671327Z | 94290 |
| Pinnacle esports moneylines | 200 | ok | 2026-10-24T16:54:54.737504Z | 480329 |
| Thunderpick fallback access | 200 | ok | 2026-10-24T16:55:36.002132Z | 14610 |
| GG.BET fallback access | 403 | error | None | None |
| BO3.gg CS2 upcoming feed page 1 | 200 | ok | 2026-10-24T16:57:17.160287Z | 223176 |
| BO3.gg CS2 upcoming feed page 2 | 200 | ok | 2026-10-24T16:57:17.482991Z | 206465 |
| BO3.gg CS2 upcoming feed page 3 | 200 | ok | 2026-10-24T16:57:17.696582Z | 104656 |
| Book listing gap recheck 1082792 | 403 | error | None | None |
| Book listing gap recheck 1082793 | None | error | None | None |
| Valve VRS standings index 2026 | 200 | ok | 2026-10-24T16:58:58.413960Z | 46751 |
| Valve VRS standings commit | 200 | ok | 2026-10-24T16:58:58.638843Z | 3621 |
| Valve VRS global standings | 200 | ok | 2026-10-24T16:58:58.723637Z | 77872 |

Accounting and provenance shape only. Source truth and the arithmetic behind every percentage are replayed independently by verification-c6/audit_snapshot.py.

