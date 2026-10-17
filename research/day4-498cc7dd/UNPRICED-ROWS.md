# The eight open fixtures with no pick — root cause, evidence, fix

Session **498cc7dd**, 2026-10-16/17 (UTC). Every number here comes from a file in this
repository or from a named primary source read this session.

## What the board actually said

Live harvest run [38983767301](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38983767301),
snapshot `research/harvest-498cc7dd/snapshot.json`, generated **2026-10-16T23:53:53.342604Z**,
`coverage: verified`:

```
{"coverage": "verified", "matches": 83, "priced": 13, "research_only": 0, "unresolved_without_any_pick": 8}
```

83 CS2 fixtures, 21 open, **13 priced, 8 open rows with no pick at all**. The previous
committed snapshot (19:59:25Z, `data/latest.json`) had 21 open and 0 rows without a pick, so
this was a same-evening regression, not a permanent coverage limit.

| Hotspawn id | Fixture | Competition | Start (UTC) |
| --- | --- | --- | --- |
| 1079170 | BET-M vs Just Players | NODWIN Clutch Series #13 | 2026-10-17T08:00:00Z |
| 1081126 | Banda chuya vs Enjoy | CCT Europe 2026 Series #12 Play-In | 2026-10-18T08:00:00Z |
| 1081521 | ex-6666 vs Privateer | CCT Europe 2026 Challengers #8 | 2026-10-18T13:45:00Z |
| 1081522 | antidaun vs Phantom Academy | CCT Europe 2026 Challengers #8 | 2026-10-18T13:45:00Z |
| 1081527 | aimclub vs BASEMENT BOYS | DraculaN Season 7 | 2026-10-19T09:00:00Z |
| 1081532 | ASTRAL vs Leo | DraculaN Season 7 | 2026-10-19T10:45:00Z |
| 1081861 | Lynn Vision vs Morningstar | VOID Autumn Cup 2026 | 2026-10-20T03:00:00Z |
| 1081863 | Chinggis Warriors vs WXM | VOID Autumn Cup 2026 | 2026-10-20T07:00:00Z |

## Root cause, with the receipts

**One HTTP 403 from HLTV.** `research/harvest-498cc7dd/probe-report.json` → `source_checks`:

```json
{"checked_at": "2026-10-16T23:53:53.818600Z", "error": "403 Client Error: Forbidden for url: https://www.hltv.org/matches",
 "http_status": 403, "name": "HLTV upcoming matches", "status": "error", "url": "https://www.hltv.org/matches"}
```

Every other source in the same run answered 200 in the same seconds: Polymarket sports
registry (200, `Age: 873`), Polymarket events page 1 (200, `Age: 118`), Pinnacle fixtures
(200) and Pinnacle moneylines (200). And the **identical** HLTV read at
`2026-10-16T19:57:11Z` had answered 200 with a recorded sha256 —
`research/harvest-621776e4/hltv-unpriced-1081521.json` (`c5dbec11…`), `-1081522.json`
(`c7ef9571…`), `-1081861.json` (`74f37660…`), `-1081863.json` (`87776c84…`). So HLTV is
rate-limiting this project's User-Agent intermittently, not refusing it.

`scripts/refresh.py` → `Sources.get` treated 403 exactly like 401: it recorded
`blocked_hosts['www.hltv.org'] = '403'` and never asked again for the rest of the run. One
403 therefore removed **two** independent pick paths at once:

1. **HLTV lineups**, which `scripts/vrs.py::identify()` needs to choose between the two
   rosters Valve lists under one label. Without a lineup the model fails closed with
   *"label appears 2 times in the standings and no lineup was available to tell the rosters
   apart"* — which is exactly what it reported for Just Players, Banda chuya, aimclub, Leo and
   Chinggis Warriors.
2. **The ranking-order research pick** (`scripts/core.py::research_rank_pick`), which needs the
   HLTV fixture page. Without it every row reported *"neither team carries a world-ranking
   number in this fixture"* — which was false: it was unread, not absent.

The repeated labels are real, in Valve's own file
(`data/vrs/standings_global_2026_10_05.md`, commit `eec4853`):

| Label | Valve rows | Rosters |
| --- | --- | --- |
| Just Players | #118 (974 pts) and #347 (485 pts) | `bl1x1, h1te, sm3t, sstiNiX, Temny Prince` vs `em0k1d, rexxie, Something, spirit, sstiNiX` |
| Banda Chuya | #165 (801) and #373 (402) | `AdrieN, ezox, maaryy, Showk, tomiko` vs `ezox, manio` |
| aimclub | #77 (1113) and #336 (504) | `ERSIN, mhN1, ragga, waZz, zewts` vs `Ed1m, ERSIN, RoberttMP, XELLOW, zewts` |
| Leo | #112 (1001) and #340 (499) | `aimy, drac, leen, next1me, Tarkky` vs `amster, kL1o, leen, Malkiss, OneUn1que` |
| Chinggis Warriors | #87 (1084) and #220 (685) | `cool4st, fury5k, ROUX, sk0R, yAmi` vs `Aceari, hasteka, ROUX, sk0R, yAmi` |

And three teams are not in Valve's file at all: **ex-6666**, **antidaun**, **Morningstar**,
**WXM** (verified by search of the same file).

## The fix

`scripts/refresh.py`: a rate-limited 403/429 is now waited out on the **identical** URL with
the **identical** headers (`Retry-After` honoured when present, otherwise 10/30/60 s, capped at
120 s). Nothing is rewritten, signed, spoofed or bypassed. Every wait is recorded in the
evidence log as `rate_limit_waits`. A source that keeps refusing is still blocked for the run,
401 and 404 are unchanged, and a 200 response that is a region gate or a challenge page is
still rejected immediately rather than retried as though it were a rate limit.
`tests/test_rate_limit_498cc7dd.py` pins all of that, including the end-to-end case where a
rate-limited HLTV discovery read still yields the lineups.

Expected effect: the four rows with a published HLTV ranking pair at 19:57Z return to research
picks; Chinggis Warriors' lineup (`ROUX, sk0R, cool4st, tikuak, fury5k`) overlaps 4 of 5
players with Valve row #87 and 2 of 5 with #220, so the VRS model can also select a roster for
it. **This is an expectation, not a verified result** — it is confirmed by the next scheduled
refresh, and the count is re-published here when it is.

## What is NOT fixed by it, and stays flagged

| Row | Blocker | Evidence |
| --- | --- | --- |
| 1079170 BET-M vs Just Players | Polymarket prices it (market [5769541](https://gamma-api.polymarket.com/markets/5769541), 0.625/0.375, bid 0.62 / ask 0.63, 1-point spread, $3,184.25 liquidity, 08:00Z start) but under the label **"BET-M 33"**. HLTV's canonical name is **BET-M** ([team 13619](https://www.hltv.org/team/13619/bet-m)) and Valve lists exactly one BET-M. Opponent, UTC start and tournament all match, but no official source read this session states the two labels are the same team, so no alias was added and no probability was published. Flagged for manual review. | `research/harvest-498cc7dd/polymarket-active-cs2.json` |
| 1081527 aimclub vs BASEMENT BOYS | A Polymarket market exists ([5650407](https://gamma-api.polymarket.com/markets/5650407)) but its spread exceeded the 25-point gate and then the 60-point low-confidence ceiling, so both exchange tiers rejected it. Its midpoint is not published as a probability. | `research/harvest-498cc7dd/snapshot.json` attempts |
| 1081532 ASTRAL vs Leo | Polymarket prices "ASTRAL vs **Leo Team**" ([5650418](https://gamma-api.polymarket.com/markets/5650418)). Same identity problem as BET-M 33, plus the duplicate Leo label above. Flagged, not aliased. | `research/harvest-498cc7dd/snapshot.json` attempts |

Pinnacle was read successfully in the same run (200 on both endpoints) and returned
*"No exact team-pair and UTC-start match in retrieved feed"* for all eight — these low-tier
fixtures are simply not in that feed. GG.BET answered 403 and Thunderpick returned no
machine-readable two-sided quote; both are recorded as collection limitations, not as evidence
that no odds exist.

## Irregularity found in the published content

`data/analysis.json` labelled day four as **"Friday 17 October 2026"**. 17 October 2026 is a
**Saturday**, and HLTV's event schedule renders both semi-finals under the heading
*"Saturday - 2026-10-17"*. Corrected; the fixture start times (14:00Z and 17:00Z) were already
correct and were not changed.

## Status at merge — this is a pipeline risk, not a published coverage gap

Re-checked against `main` at the merge (`de4ea16`). The snapshot this site publishes is
`data/latest.json`, generated **2026-10-16T19:59:25.913409Z**, and it reached HLTV with a 200:
21 open rows, **0 of them without a pick**, methods `exchange` 6, `exchange_wide` 2, `model_vrs`
9, `research_rank` 1, `research_rank_single` 3. All eight fixtures in the table above carry a
pick there — for example 1079170 BET-M vs Just Players is `pick: BET-M`, `method: model_vrs`,
68.1% / 31.9%. The 23:53:53Z harvest in `research/harvest-498cc7dd/snapshot.json` was never
published to the site, so no reader ever saw a row lose its pick.

That is exactly why the finding is worth recording: a single 403 from one source was enough to
strip eight picks from an otherwise healthy refresh, and nothing in the run's output said so —
`coverage` still read `verified`. The fix in `scripts/refresh.py` makes the next refresh wait out
the rate limit instead. The recovered row count is deliberately not claimed; it is whatever the
next scheduled run reports.
