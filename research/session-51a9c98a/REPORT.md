# Session 51a9c98a — independent read of the live board, the Hotspawn feed and one external line

**Date:** 2026-10-23, 09:45–10:20 UTC
**Branch:** `arena/51a9c98a-maltaproj4`
**Scope:** verify the published board against official sources line by line, fix the one
thing a reader actually trips over (92 feed rows reading as 92 matches), and record every
finding with its source. No probability, pick, price or start time was changed.

## 1. Environment limit (recorded first, because it shapes the method)

This sandbox has **no outbound HTTPS** from its own shell: every request through
`urllib`/`curl` returns `TLS/SSL connection has been closed (EOF)` — Polymarket, the
Hotspawn fixtures endpoint, HLTV, EGamersWorld and `play.hotspawn.com` all failed
identically, while `github.com` answered over the `gh` CLI. Live reads were therefore
made with the workspace fetch tool, one URL at a time, and every value below is quoted
from that response. Nothing here is reconstructed from memory or from the repository's
own JSON.

## 2. Coverage: the lobby's 30 cards map 1:1 onto the board's 30 open fixtures

| Check | Live value (read 2026-10-23T09:47Z) | Board (snapshot 08:32:56Z, fixture evidence 08:29:19Z) |
| --- | --- | --- |
| Open CS2 matches on the lobby | 30 cards | 30 rows with `state=open` |
| Fixtures with a pick | — | 30 |
| Fixtures with a win probability | — | 30 (`exchange` 20, `bookmaker_fallback` 2, `exchange_wide` 1, `model_vrs` 7) |
| Fixtures with no supported pick | — | 0 |

Every fixture ID on the lobby appears in the board's open set, and the board's open set
contains nothing that is not on the lobby:

```
1081605 1081148 1079655 1081606 1082926 1082980 1083014 1082924 1081150 1079657
1082693 1082925 1083025 1082923 1079193 1079195 1082996 1079198 1079199 1079200
1082858 1082859 1082860 1082861 1082897 1082898 1082900 1082901 1082792 1082793
```

One lobby card (JiJieHao vs Eternal Fire) renders without a "View Match" link; it is
feed row `1081606`, so the 1:1 mapping still holds. Source:
<https://play.hotspawn.com/lobby>.

## 3. What the feed returns beyond the lobby (now disclosed on the site)

`GET https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`

* 92 CS2 rows, all carrying `"status":"scheduled"`.
* 62 of them have scheduled starts **before the snapshot's own observation clock**
  (26 Jun · 10:30Z → 23 Oct · 08:00Z). They are old records the endpoint has not
  retired. They are listed for completeness and never priced.
* The lobby's tier/tournament filter counts sum to **94** (B 40, C 54) while the endpoint
  returned 92. The two-row difference is one *VOID Autumn Cup 2026* fixture (lobby 1,
  feed 0) and one further *CCT Europe 2026 Series #12* fixture (lobby 3, feed 2). Neither
  was invented; the next refresh re-reads both views.

**What changed:** `scripts/build.py` now computes the split from the snapshot clock
(`past_dated_rows`), prints it at the top of *All matches* (`feed_scope`, linking the lobby
and the endpoint), names the count in the executive summary, and labels those rows
*Past fixture · not in the lobby* instead of the ambiguous *Not open*. A feed with no
past-dated rows renders no panel and no sentence.

## 4. Lobby clock vs feed clock (not a conflict — a display timezone)

| Fixture | Lobby card | Lobby "Locks in" at 09:47:57Z | Feed `scheduled_start_time` |
| --- | --- | --- | --- |
| 1082925 BESTIA Academy vs RED Canids Academy | Oct 23, 15:00 | 09:12:03 → 19:00:00Z | 1793046000000 ms = 19:00:00Z |
| 1083025 paiN vs Imperial | Oct 23, 17:00 | 09:12:03 → 21:00:00Z | 1793053200000 ms = 21:00:00Z |
| 1079655 Nuclear TigeRES vs ILLYRIANS | Oct 23, 07:00 | — | 11:00:00Z |

The offset is a constant −4 h (US Eastern daylight time), not a disagreement: the lobby's
own countdowns match the feed's UTC values. The board publishes the feed's UTC values and
converts nothing. Recorded as a review note so the four-hour gap is not read as a wrong
start time.

## 5. External line spot-check (independent of Hotspawn)

| Fixture | Board pick / probability (observed 08:29Z) | External observation | Verdict |
| --- | --- | --- | --- |
| 1079655 Nuclear TigeRES vs ILLYRIANS | Nuclear TigeRES 86.5% / 13.5%, Polymarket `6036897`, spread 0.01, $6,413 liquidity | Polymarket `6036897` re-read at 09:44Z: `outcomePrices ["0.85","0.15"]`, bid 0.84 / ask 0.86, `updatedAt 2026-10-23T09:44:06Z`; EGamersWorld listing `1.12 / 5.8` (de-vigged ≈ 83.8% / 16.2%) | Same direction and same order of magnitude; the board's 86.5% is its 08:28Z observation, and the market has since moved to 85.0%. The stale-by-76-minutes price is exactly why every row publishes its observation time. |

Sources: <https://gamma-api.polymarket.com/markets/6036897> ·
<https://egamersworld.com/counterstrike/matches>.

The EGamersWorld page also carries pre-match two-way prices for today's fixtures
(``1.12 / 5.8`` on Nuclear TigeRES–ILLYRIANS, ``1.78 / 1.9`` on ex-Zero Tenacity–ex-RUSTEC),
which is the tier the ladder uses when no exchange price survives its gates.

## 6. Scheduled delivery (flagged, unchanged)

Through the Actions API at 09:55Z: between 07:20Z and 09:55Z the repository received
**one** `schedule` event (pages.yml, 07:20:51Z, success) although pages.yml's
`4,19,34,49 * * * *` cron asked for ten slots and `refresh-watchdog.yml`'s
`*/10 * * * *` cron asked for fifteen more. The watchdog has delivered **zero** scheduled
runs all day; every listed watchdog run is a `push`. In the same window: 67 `push`,
16 `pull_request`, 16 `pages-build` events.

Consequence: the board refreshes when a merge runs the pipeline, not on the advertised
15-minute beat. The evidence-window rules still stop an expired snapshot from being shown
as current. Recorded as a review note with a follow-up (external trigger or a reserved
queue slot); no workflow was changed here, because a denser cron cannot fix a dropped
event and this session did not measure a candidate fix.

## 7. Verification performed on the tree

```
python -m unittest discover -s tests          # 1058 tests before this session's additions
python -m unittest tests.test_session_51a9c98a -v   # 16 new tests, OK
python -m scripts.build                       # 92 sourced rows, 30 with percentages, 0 unresolved
python -m scripts.validate --data data/latest.json
```

`scripts.validate` on the rebuilt site: 30 probability calculations reproduced, 15 pages,
820 internal links and assets, 20 manifest checksums, 224 displayed rows — all passing.

## 8. Files touched

| File | Change |
| --- | --- |
| `scripts/build.py` | `past_dated_rows`, `feed_scope`, past-row labels, executive-summary sentence |
| `data/review-notes.json` | three dated notes (feed vs lobby counts, EDT lobby clock, schedule delivery) |
| `tests/test_session_51a9c98a.py` | 16 regression tests for the above |
| `research/session-51a9c98a/REPORT.md` | this report |
| `README.md`, `COORDINATION.md` | session record |

## 9. Open items for manual review

1. The lobby counts 94 fixtures; the endpoint returned 92 (one `VOID Autumn Cup 2026`, one
   `CCT Europe 2026 Series #12`). Not resolvable without a fresh endpoint read; the
   scheduled refresh closes it.
2. 62 feed rows are past-dated yet still `status: scheduled`. The site now labels them;
   whether Hotspawn intends to keep returning them is their side of the contract.
3. Scheduled workflow delivery is starved (section 6). Needs an external trigger to be
   robust when no session is merging.
