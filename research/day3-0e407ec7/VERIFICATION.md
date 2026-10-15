# Day-2 / day-3 verification pass — session 0e407ec7

**When:** 2026-10-15 22:40 UTC → 2026-10-16 01:10 UTC (retrievals), report written 2026-10-16 (UTC).
**Who:** Arena session `0e407ec7`, branch `arena/0e407ec7-maltaproj4`. Retrievals and the first draft ran against `origin/main` `8857774`; PR #24 (session `e54807b3`) merged mid-flight, so the final work was re-applied on `origin/main` **`9757a74`** and every count below was recomputed against that state (capture generated 2026-10-15T23:12:43Z). Where a number in this report was first written against the earlier 22:37Z capture, the current value is given and the capture it belongs to is named.
**What this file is:** an independent, line-by-line check of every factual claim this site publishes about the
Thunderpick World Championship 2026 day-2 results (15 October) and the day-3 deciders (16 October), plus the
external market lines behind them. Each row states the claim as published, the primary source read, the verdict
and the exact link a human can open to repeat the check.

**Tool constraints, stated plainly:** the authoring sandbox's shell reaches `github.com`, `api.github.com` and the
package registries only. HLTV, Polymarket and Hotspawn were read through the page-retrieval tool; the Hotspawn
fixture inventory and the pipeline's own refresh ran on GitHub Actions runners (workflow
`.github/workflows/harvest-0e407ec7.yml`, run `38818433905`, artifacts retained in
`research/harvest-0e407ec7/`). Nothing below claims a source was read that was not read.

**Method rule applied throughout:** Hotspawn establishes fixture inventory only and is never a probability input.
Probabilities come only from externally observed market quotes or reproducible arithmetic on them. HLTV supplies
results, vetoes, rankings and context. Crowd `picked_percent` values present in the Hotspawn feed were ignored as
probability evidence.

---

## A. Day-2 results as published in `data/analysis.json` → `day_two`

All four day-2 series were read directly from their own HLTV match pages (not from a results list, not from a PR #24 (session `e54807b3`) had meanwhile added a `veto` field to each of the four day-two records; all four strings match this session's independent reads of the HLTV pages token for token, which is a useful cross-confirmation of both passes.
third-party report).

| # | Claim as published | Verdict | Primary source |
| --- | --- | --- | --- |
| A1 | Falcons beat 9z **2-1**, Group A winners' match | **Confirmed** | [HLTV 2399409](https://www.hltv.org/matches/2399409/9z-vs-falcons-thunderpick-world-championship-2026) |
| A2 | Maps: Nuke 13-9 (Falcons), Mirage 8-13 (9z), Dust2 13-9 (Falcons) | **Confirmed** — page shows Nuke 9-13, Mirage 13-8, Dust2 9-13 from 9z's side, i.e. the same three results written winner-first | [HLTV 2399409](https://www.hltv.org/matches/2399409/9z-vs-falcons-thunderpick-world-championship-2026) |
| A3 | Veto: 9z picked Nuke and lost it 9-13; Falcons picked Mirage and lost it 8-13; Dust2 was left over and Falcons closed 13-9 | **Confirmed** — page veto reads: 9z removed Anubis, Falcons removed Cache, 9z picked Nuke, Falcons picked Mirage, 9z removed Inferno, Falcons removed Ancient, Dust2 left over | [HLTV 2399409](https://www.hltv.org/matches/2399409/9z-vs-falcons-thunderpick-world-championship-2026) |
| A4 | TeSeS 47-40 with a 1.26 rating, previously labelled "third-party report" | **Confirmed on the HLTV page itself** — match-stats table: TeSeS 47-40, eK-eD 48-39, swing +2.35%, ADR 75.1, KAST 78.5%, Rating 3.0 **1.26**. The label in `data/analysis.json` has been upgraded to HLTV-verified by this session; the third-party report is kept as a secondary link | [HLTV 2399409 match stats](https://www.hltv.org/matches/2399409/9z-vs-falcons-thunderpick-world-championship-2026) |
| A5 | Aurora beat Ninjas in Pyjamas **2-0**, Group A elimination match; NIP eliminated after two losses | **Confirmed** | [HLTV 2399408](https://www.hltv.org/matches/2399408/aurora-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026) |
| A6 | Maps: Cache 13-9, Dust2 13-7 | **Confirmed** — page: Cache 13-9 (halves 7:5; 6:4), Dust2 13-7 (halves 9:3; 4:4); Nuke was left over and never played | [HLTV 2399408](https://www.hltv.org/matches/2399408/aurora-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026) |
| A7 | Wicadia 45-25 with a 1.65 rating | **Confirmed** — series row: 45-25, swing +6.01%, ADR 101.5, KAST 81.0%, Rating 3.0 1.65 | [HLTV 2399408 match stats](https://www.hltv.org/matches/2399408/aurora-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026) |
| A8 | XANTARES 36-23 with 1.41 | **Confirmed** — series row: 36-23, ADR 103.8, KAST 85.7%, Rating 3.0 1.41 | [HLTV 2399408 match stats](https://www.hltv.org/matches/2399408/aurora-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026) |
| A9 | stavn 15-30 (0.58) | **Confirmed** — NIP series row: 15-30, swing −5.68%, ADR 51.4, KAST 54.8%, Rating 3.0 0.58 | [HLTV 2399408 match stats](https://www.hltv.org/matches/2399408/aurora-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026) |
| A10 | FURIA beat Legacy **2-1**, Group B winners' match, and took the direct semifinal place 2-0 in the group | **Confirmed** | [HLTV 2399411](https://www.hltv.org/matches/2399411/legacy-vs-furia-thunderpick-world-championship-2026) |
| A11 | Legacy took FURIA's Cache pick 13-10; FURIA won Inferno 13-5 and Mirage 13-8 | **Confirmed** — veto: FURIA removed Ancient, Legacy removed Anubis, **FURIA picked Cache**, **Legacy picked Inferno**, FURIA removed Dust2, Legacy removed Nuke, Mirage left over. Scores: Cache Legacy 13-10 (7:5; 6:5), Inferno Legacy 5-13 (4:8; 1:5), Mirage Legacy 8-13 (3:9; 5:4) | [HLTV 2399411](https://www.hltv.org/matches/2399411/legacy-vs-furia-thunderpick-world-championship-2026) |
| A12 | BETBOOM beat PARIVISION **2-1**, Group B elimination match | **Confirmed** | [HLTV 2399410](https://www.hltv.org/matches/2399410/parivision-vs-betboom-thunderpick-world-championship-2026) |
| A13 | Maps: Ancient 13-10 (PARIVISION), Anubis 4-13, Mirage 7-13 (`maps` field) | **Confirmed** — page: Ancient PARIVISION 13-10 (4:8; 9:2), Anubis PARIVISION 4-13 (2:10; 2:3), Mirage PARIVISION 7-13 (3:9; 4:4) | [HLTV 2399410](https://www.hltv.org/matches/2399410/parivision-vs-betboom-thunderpick-world-championship-2026) |
| A14 | "PARIVISION took their own Ancient pick 13-10" (in the `detail` prose) | **Confirmed** — veto: PARIVISION removed Nuke, BETBOOM removed Inferno, **PARIVISION picked Ancient**, **BETBOOM picked Anubis**, PARIVISION removed Cache, BETBOOM removed Dust2, Mirage left over | [HLTV 2399410](https://www.hltv.org/matches/2399410/parivision-vs-betboom-thunderpick-world-championship-2026) |
| A15 | "then BETBOOM won Anubis **13-2** and Mirage 13-7" (in the `detail` prose) | **WRONG — irregularity #1.** HLTV shows Anubis **13-4** (halves 2:10; 2:3). Mirage 13-7 is correct. The same record's `maps` field ("Anubis 4-13") was already correct, so only the prose was wrong. Corrected by this session in `data/analysis.json` and logged in `data/review-notes.json` | [HLTV 2399410](https://www.hltv.org/matches/2399410/parivision-vs-betboom-thunderpick-world-championship-2026) |

**Group consequences re-derived from A1–A15 and the results list** ([HLTV results, event 8932](https://www.hltv.org/results?event=8932)):
Group A → Falcons 2-0 through as group winner, Aurora and 9z both 1-1 into the decider, NIP 0-2 eliminated.
Group B → FURIA 2-0 through as group winner, BETBOOM and Legacy both 1-1 into the decider, PARIVISION 0-2 eliminated.
Day-1 results used in that derivation (14 October, all on the same results page): FURIA 2-0 BETBOOM (2399387),
Legacy 2-0 PARIVISION (2399386), Falcons 2-0 NIP (2399385), 9z 2-0 Aurora (2399384). **Confirmed.**

## B. Day-3 fixtures, start times and external lines

| # | Claim | Verdict | Source |
| --- | --- | --- | --- |
| B1 | Group A decider Aurora vs 9z on 16 October, Bo3, HLTV match 2399412 | **Confirmed** | [HLTV event schedule](https://www.hltv.org/events/8932/matches) · [HLTV fixture](https://www.hltv.org/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026) |
| B2 | Aurora vs 9z starts **2026-10-16T14:00:00Z** | **Confirmed by three independent sources**: Hotspawn fixture `1080205` `scheduled_start_time` → `start` 14:00Z (lock 13:54Z); Polymarket market `5733288` `gameStartTime` "2026-10-16 14:00:00+00" and `eventStartTime` 2026-10-16T14:00:00Z; its description says "10:00 AM ET", and HLTV displays 10:00 for this fixture in the reader's timezone (US Eastern, UTC−4, at this retrieval) | [market 5733288](https://gamma-api.polymarket.com/markets/5733288) · [HLTV fixture](https://www.hltv.org/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026) |
| B3 | The published Aurora/9z line passes the project's exchange gates | **Confirmed** — the row published now (`data/latest.json` capture 2026-10-15T23:12:43Z) is 0.69 / 0.31 with fair odds 1.4492753623188408 and 3.2258064516129035, evidence observed 2026-10-15T23:12:32Z against market `updatedAt` 2026-10-15T23:11:13Z, expiring 2026-10-16T05:33:49Z: sum 1.000, bid 0.68 ≤ ask 0.70, spread 0.02 ≤ 0.25 → `exchange` tier, liquidity ≥ $100, `active` true, `closed` false, `acceptingOrders` true, `updatedAt` inside 8 h. The previous capture published 0.685 / 0.315 with fair odds 1.4598540145985401 and 3.1746031746031744, which also reproduce exactly as 1/p | `data/latest.json` → `matches[1080205].evidence[0].raw`; cross-check receipt [quotes/polymarket-5733288-aurora-9z-crosscheck.json](quotes/polymarket-5733288-aurora-9z-crosscheck.json) |
| B4 | Where the same line stood at this session's later reads | **Confirmed, with a correction to this session's own earlier wording.** Two states were read: `updatedAt` 2026-10-15T22:51:08Z → 0.69 / 0.31, bid 0.68 / ask 0.70, spread 0.02, last trade 0.70, liquidity 62875.9868, volume 10450.905170000002; then a cache-busted read of `updatedAt` 2026-10-15T23:17:08Z → **0.685 / 0.315**, bid 0.68 / ask 0.69, spread 0.01, liquidity 55257.8679. So the favourite's price rose half a cent after Aurora's 2-0 win over NIP and then came back; the freshest state equals the probability the site already publishes, so the row needed no correction. Recorded as research only; no published probability was edited by hand | [market 5733288](https://gamma-api.polymarket.com/markets/5733288?cb=0e407ec7-0135z) |
| B5 | Group B decider BETBOOM vs Legacy on 16 October, Bo3, HLTV match 2399413 | **Confirmed** | [HLTV event schedule](https://www.hltv.org/events/8932/matches) · [HLTV fixture](https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026) |
| B6 | BETBOOM vs Legacy starts **2026-10-16T17:00:00Z** (published as blank before this pass) | **Confirmed by two independent sources** — Polymarket market `5763247` `gameStartTime` "2026-10-16 17:00:00+00", `eventStartTime` 2026-10-16T17:00:00Z, description "initially scheduled for October 16, 2026 at 1:00 PM ET"; HLTV displays 13:00 for this fixture in the reader's timezone (US Eastern = 17:00Z). Filled into `data/analysis.json` → `day_three.fixtures[1].start_utc` | [market 5763247](https://gamma-api.polymarket.com/markets?slug=cs2-lgc-bb3-2026-10-16) · receipt [quotes/polymarket-5763247-legacy-betboom.json](quotes/polymarket-5763247-legacy-betboom.json) |
| B7 | The shared board recorded this fixture as "13:00Z" | **WRONG — irregularity #2.** 13:00 is HLTV's displayed Eastern clock, not UTC. The correct UTC start is 17:00Z (B6). Logged in `data/review-notes.json` and in `COORDINATION.md`; no published fixture time on the site carried the wrong value (the field was blank), so no page needed a correction beyond filling it in | [COORDINATION.md](../../COORDINATION.md) · [market 5763247](https://gamma-api.polymarket.com/markets?slug=cs2-lgc-bb3-2026-10-16) |
| B8 | An exchange series moneyline exists for the Group B decider | **Confirmed, and the price moved between reads.** Market `5763247` (event `1196836`, slug `cs2-lgc-bb3-2026-10-16`), `sportsMarketType` moneyline, `groupItemTitle` "Match Winner", `createdAt` 2026-10-15T22:25:13Z, `active` true, `closed` false, `acceptingOrders` true, `gameId`/`pandascoreMatchId` 1741374, `leagueTier` 2, `resolutionSource` https://hltv.org. Three dated states: `updatedAt` 22:45:08Z -> Legacy 0.64 / BetBoom Team 0.36, bid 0.59 / ask 0.69, spread 0.10, last trade 0.68, liquidity 6847.5095; `updatedAt` 22:53:08Z -> 0.635 / 0.365, bid 0.59 / ask 0.68, spread 0.09, liquidity 6891.13, volume 2270.94 (independent read by concurrent session dbe62379 in PR #23); `updatedAt` **23:17:08Z** -> **0.635 / 0.365**, bid 0.60 / ask 0.67, spread 0.07, last trade 0.65, liquidity **8149.023**, volume 2361.111557 (this session's cache-busted read, the freshest of the three). Legacy is the lean at every state | [market 5763247](https://gamma-api.polymarket.com/markets/5763247?cb=0e407ec7-0135z) · [receipt](quotes/polymarket-5763247-legacy-betboom.json) |
| B9 | That line cannot become a pick row on this site | **Confirmed** — the fixture does not exist in the Hotspawn CS2 feed. Neither the published snapshot (`data/latest.json`, 86 rows, capture generated 2026-10-15T23:12:43Z, fixtures observed 21:33:49Z) nor this session's own independent harvest (`research/harvest-0e407ec7/latest.json`, 86 rows, fixtures observed 21:33:48Z) contains **any BETBOOM row**, and each contains exactly one Legacy row: `1080204` Legacy vs FURIA, state `not_open`, scheduled 2026-10-15T16:00:00Z. This project publishes picks only for fixtures the Hotspawn feed lists, so the market is recorded as sourced research and flagged as an inventory gap (**irregularity #3**). Session `e54807b3` reached the same conclusion independently in `betboom-legacy-missing-2026-10-15` | [Hotspawn feed](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1) · `research/harvest-0e407ec7/latest.json` |
| B10 | HLTV analytics: Aurora #6 vs 9z #17; Aurora bookmaker favourite; Aurora won 3 of last 5; Aurora lost the most recent head-to-head 0-2 to 9z | **Confirmed** | [HLTV analytics 2399412](https://www.hltv.org/betting/analytics/2399412/aurora-vs-9z-thunderpick-world-championship-2026) |
| B11 | HLTV analytics: BETBOOM #14 vs Legacy #7, Legacy better form and rank | **Confirmed** | [HLTV analytics 2399413](https://www.hltv.org/betting/analytics/2399413/betboom-vs-legacy-thunderpick-world-championship-2026) |
| B12 | HLTV analytics pages carry **no decimal match-winner odds** | **Confirmed** — so HLTV is never used as a price source on this project; only rankings, form, H2H and ratings | [HLTV analytics 2399412](https://www.hltv.org/betting/analytics/2399412/aurora-vs-9z-thunderpick-world-championship-2026) |
| B13 | 17 October semifinals (2399414, 2399415), 18 October 3rd place (2399416) and Bo5 final (2399417) | **Confirmed** | [HLTV event schedule](https://www.hltv.org/events/8932/matches) |
| B14 | Manual retrieval of these markets can be served from an HTTP cache | **Confirmed — irregularity #8.** The slug URL for market 5763247 was read twice and returned byte-identical payloads stamped `updatedAt` 22:45:08Z, while a cache-busted read of the same market (`?cb=…`) returned `updatedAt` 23:17:08Z with different prices, spread, liquidity and volume. The same happened on market 5733288 (cached 22:51:08Z state 0.69/0.31 versus cache-busted 23:17:08Z state 0.685/0.315). Consequence: a manual read is dated by the `updatedAt` inside the payload, never by the moment of the read, and the pipeline's own refresh — which already adjusts observation time for HTTP cache Age — stays the only source of published probabilities | [cached read](https://gamma-api.polymarket.com/markets?slug=cs2-lgc-bb3-2026-10-16) · [cache-busted read](https://gamma-api.polymarket.com/markets/5763247?cb=0e407ec7-0135z) |

## C. Hotspawn scoring rules and what they mean for contrarian picks

Newly collected in this pass; the site previously stated that the scoring rules were **not** collected, which is no
longer true and has been corrected in `data/analysis.json` → `strategy.unverified`.

| # | Claim | Verdict | Source |
| --- | --- | --- | --- |
| C1 | Points are earned for every correct pick and higher-tier matches award more points | **Confirmed, official** | [play.hotspawn.com/how-it-works](https://play.hotspawn.com/how-it-works) |
| C2 | Bonus points are awarded for consecutive correct picks ("the longer your streak, the bigger the bonus") | **Confirmed, official** — the exact bonus formula is not published anywhere this session could read, so no number is claimed for it | [play.hotspawn.com/how-it-works](https://play.hotspawn.com/how-it-works) |
| C3 | Picks lock **5 minutes** before the scheduled start; picks can be changed any time before they lock; the leaderboard resets weekly | **Confirmed, official** — but the feed disagrees by one minute: see the lock-time note below (**irregularity #7**) | [play.hotspawn.com/how-it-works](https://play.hotspawn.com/how-it-works) · `data/latest.json` → `matches[1080205]` |
| C4 | Forfeited matches void all predictions (no points awarded or deducted); cancelled matches are cancelled and do not count | **Confirmed, official** | [play.hotspawn.com/how-it-works](https://play.hotspawn.com/how-it-works) |
| C5 | Points per tier, read from the official fixture feed: tier **s = 7**, tier **b = 3**, tier **c = 2** (`offered_points`, `base_points` 2 with `points_breakdown.tier_multiplier` 3 / 1.5 / 1) | **Confirmed from the feed, not from the rules page** — identical in both snapshots: 2 tier-s rows, 31 tier-b rows and 53 tier-c rows out of 86, and the 22 open rows are worth **61 points** in total | `data/latest.json` → `fixture_evidence[*].offered_points`; same numbers in `research/harvest-0e407ec7/latest.json` |
| C6 | Arithmetic on the published lines: the TWC decider is worth 7 points, so at the row published now (0.69 / 0.31) the favourite side is worth 7 × 0.69 = **4.83** expected points and the contrarian side 7 × 0.31 = **2.17** (4.795 / 2.205 at the 0.685 / 0.315 state); across the **20** priced open rows of the 23:12:43Z capture, following the published favourite side is worth **37.87** of the **56** points those rows carry, with the remaining 5 of the 61 open points on the 2 rows that have no probability, for which no expected value is computed or claimed | **Arithmetic performed by this session on the recorded lines** — reproducible with the command at the end of this file. Not a new probability claim; no published probability was changed. (First drafted against the 22:37Z capture, where 17 rows were priced, they carried 47 points and the favourite side totalled 32.70; PR #24's VRS model tier priced three more rows, which is why the counts moved) | `data/latest.json` |
| C7 | This project's own originated line agrees with the market on the decider | **Confirmed** — the `model_check` stored on fixture 1080205 reads Valve Regional Standings points 1716 (Aurora) vs 1543 (9z), standings as of 2026-10-05, calibrated to 0.6795895802085545 / 0.32041041979144547, i.e. half a percentage point from the exchange's 0.69 / 0.31 and the same favourite. Two independent methods agreeing is corroboration, not a consensus price: the published pick and percentage still come from the market row. The model's own limits (monthly standings, blind to Aurora's 2026 rebuild and to 9z's day-one form) are already flagged as `vrs-model-2026-10-15` | `data/latest.json` → `matches[1080205].model_check` · [Valve standings 2026-10-05](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |

**Lock-time note (C3, irregularity #7):** the official rules page says picks lock 5 minutes before start. The
Hotspawn feed disagrees with its own rules page: fixture `1080205` carries `scheduled_start_time` 1792159200000 ms
(2026-10-16T14:00:00Z) and `lock_time` 1792158840000 ms (2026-10-16T13:54:00Z), and the feed states
`lock_offset_sec: 360` — a six-minute offset. Both values are published exactly as the sources give them and the
discrepancy is recorded rather than smoothed over. This site's row-level countdown uses the feed's `lock_time`,
which is the stricter (earlier) of the two, so a reader following this site cannot submit later than the feed allows.
Logged in `data/review-notes.json` as `hotspawn-lock-offset-2026-10-16`.

## D. Claims inherited from earlier sessions that this pass did **not** re-verify

Listed so nobody mistakes silence for confirmation. Each of these is already published with its own source link on
`analysis.html` and was verified by the session that wrote it (day-1 evidence lives in
`research/day1/DAY1-REVIEW-2026-10-15.md`).

- Aurora's 2026 rebuild: Jimpphat from MOUZ, kyxsan as in-game leader, coach ash (HLTV news 45718 / 45719 / 45284).
- 9z's day-1 2-0 win over Aurora and luchov's 1.61 rating in that match (HLTV news 45718).
- Aurora's third-place finish at ESL Pro League Season 24 and the resulting schedule load.
- The identity mappings `Aurora ↔ Aurora Gaming`, `Team Liquid ↔ Liquid`, `Insiders ↔ Insiders Esport`
  (`data/identities.json`, each with its own cited source; re-checked for *presence and source URL*, not re-derived).
- The `day_two_more` claims added by PR #24 and sourced to HLTV news articles: arT returning from meningitis with "my aim is still a bit shaky" (news 45722), BETBOOM's 89.1% simulated PGL Singapore Major chance (news 45729), NIP's Stake Pulse Beat III quarter-final starting less than 24 hours after their elimination (news 45724), and Legacy losing a rivalry they had won twice in 2026 (news 45730). These are relevant to the rest/fatigue screen and are published with their own links; this session did not open those four articles.
- The VRS model tier itself (`vrs-model-2026-10-15`): Valve's standings, formula and calibration slope, and its roster-label rule. This session verified only that the model line stored on fixture 1080205 agrees with the market within half a point (C7), not the model's construction.
- `WROTBERRY ↔ WBT` remains flagged for manual review by the session that created it (no official rename statement).

## E. Irregularities found in this pass

1. **Wrong map score in prose (fixed).** `data/analysis.json` → `day_two` BETBOOM/PARIVISION `detail` said Anubis
   **13-2**; HLTV 2399410 says **13-4**. The `maps` field of the same record was already correct. Corrected in
   place, logged in `data/review-notes.json` (`twc-anubis-score-2026-10-16`).
2. **UTC start recorded as HLTV's displayed Eastern clock (fixed where it mattered).** The shared board recorded
   BETBOOM vs Legacy as "13:00Z"; the sourced UTC start is **17:00Z** (Polymarket `gameStartTime` +
   `eventStartTime`, corroborated by the market description's "1:00 PM ET"). The site's field was blank rather than
   wrong, and it is now filled with 17:00Z. Logged as `twc-day3-start-time-2026-10-16`.
3. **Inventory gap: a strict-quality market exists for a fixture the board does not list.** Polymarket `5763247`
   prices the Group B decider (Legacy 0.64 / BetBoom Team 0.36, 10-point spread, $6,847.51 liquidity) but Hotspawn's
   CS2 feed carries no BETBOOM fixture at all, so no pick row can exist and no leaderboard points can be scored on
   that series. Logged as `twc-day3-groupb-inventory-gap-2026-10-16`. `data/identities.json` already aliases
   BetBoom/BetBoom Team/BB Team, so if the feed lists it later, `scripts/refresh.py` can price it without a new alias.
4. **Under-attributed statistic (upgraded).** TeSeS 47-40 / 1.26 was published as "a third-party match report"; the
   same figures are on the HLTV match page's own stats table, which this session read. The label now says
   HLTV-verified and keeps the third-party link as secondary.
5. **Stale statement about Hotspawn scoring (corrected).** `strategy.unverified` asserted that this project does not
   collect Hotspawn's scoring rules. The official rules page and the feed's `offered_points` fields were both read in
   this pass, so the statement is replaced with what is sourced (C1–C5) and what is still unknown (the streak-bonus
   formula).
6. **This session's own harvester crashed on a `None` key (fixed).** `scripts/harvest_0e407ec7.py` built
   `open_pick_methods` with `dict(collections.Counter(...))`, and three open rows in the 22:38Z snapshot have
   `method: null`, so `json.dumps(..., sort_keys=True)` raised
   `TypeError: '<' not supported between instances of 'str' and 'NoneType'` (run 38818433905,
   `research/harvest-0e407ec7/logs/summary.exit` = `exit=1`, traceback in `logs/summary.txt`). Keys are now
   stringified; `tests/test_harvest_0e407ec7.py` reproduces the crash case and asserts the counts are re-derived,
   never authored. Re-running the summariser on the exact snapshot that crashed now exits 0 and writes
   `harvest-summary.json` with `open_pick_methods {"None": 3, "exchange": 9, "exchange_wide": 6, "research_rank": 4}`.
7. **Hotspawn's feed locks picks six minutes before start while its own rules page says five.** Fixture `1080205`:
   `lock_time` 2026-10-16T13:54:00Z against `scheduled_start_time` 2026-10-16T14:00:00Z, with `lock_offset_sec: 360`
   in the feed, versus "picks lock 5 minutes before the scheduled start time" on
   [play.hotspawn.com/how-it-works](https://play.hotspawn.com/how-it-works). This site uses the feed's earlier
   `lock_time`, so no reader is told they have longer than the feed allows. Logged as
   `hotspawn-lock-offset-2026-10-16`; no value was averaged, reconciled or inferred.
8. **This session's own manual market reads were partly served from an HTTP cache (corrected).** The slug URL
   `https://gamma-api.polymarket.com/markets?slug=cs2-lgc-bb3-2026-10-16` was read twice and returned byte-identical
   payloads stamped `updatedAt` 2026-10-15T22:45:08Z. A cache-busted read of the same market then returned
   `updatedAt` 2026-10-15T23:17:08Z with different prices (0.635 / 0.365 instead of 0.64 / 0.36), spread (0.07
   instead of 0.10), liquidity (8149.023 instead of 6847.5095) and volume. Market 5733288 behaved the same way
   (cached state 22:51:08Z at 0.69 / 0.31 versus cache-busted state 23:17:08Z at 0.685 / 0.315). An earlier draft of
   this report and of `data/analysis.json` therefore described the Aurora–9z line as having "moved toward the
   favourite" on the strength of a stale payload; both have been corrected to the full sequence
   0.685 → 0.69 → 0.685 with each state dated by its own `updatedAt`. Both quote receipts now carry a
   `cache_warning` and list every observation separately. Logged as
   `polymarket-cached-manual-reads-2026-10-16`. No published probability was ever taken from a manual read, so no
   pick on this site was affected.

## F. Not verifiable from any source this session could read (left blank / flagged, never inferred)

- The Hotspawn **streak-bonus formula** (points per consecutive correct pick) — the rules page says a bonus exists
  and does not quantify it.
- Any **decimal match-winner odds** from HLTV — the analytics pages do not expose them, and `GG.BET` returned
  HTTP 403 to earlier pipeline attempts (already flagged as `book-access`).
- A world ranking for **LOS NINOS** and **Insiders** — one-sided research only, already flagged
  (`research-rank-tier-2026-10-15`, `one-sided-rank-tier-2026-10-16`).
- The exact wall-clock time of this session's manual market reads — recorded as `observed_at: null` in both quote
  receipts with the exchange-side `updatedAt` as the bound instead of an invented timestamp.
- Whether Hotspawn will list the Group B decider before it starts — unknowable now; the 06:17Z scheduled refresh is
  the next check, and the fixture will be priced automatically if it appears.

## G. Reproduce every number above

```bash
# row-level independent audit of the published snapshot (0 failures expected)
python verification-c6/audit_snapshot.py data/latest.json --output /tmp/row-audit.md && tail -1 /tmp/row-audit.md

# site + data validation (pages, internal links, artifact checksums, displayed rows)
python -m scripts.validate --data data/latest.json --site .

# unit and failure-mode suites, including this session's harvester regression tests
python -m unittest discover -s tests
python -m unittest discover -s audits -p 'test_*.py'
python verification-95b588c2/test_integrity.py
python -m unittest discover -s verification-c6 -p 'test_*.py'

# C5/C6: tier points, open points, expected points of following the published favourite
python - <<'PY'
import json
d = json.load(open('data/latest.json'))
ev = {str(r['id']): r for r in d['fixture_evidence']}
opens = [m for m in d['matches'] if m['state'] == 'open']
pts = lambda m: ev[m['id']].get('offered_points') or 0
priced = [m for m in opens if m.get('probabilities')]
print('open rows', len(opens), 'points available', sum(pts(m) for m in opens))
print('priced', len(priced), 'EV of the published favourite %.2f of %d' % (
      sum(pts(m) * max(m['probabilities']) for m in priced), sum(pts(m) for m in priced)))
PY

# this session's harvest summariser on the snapshot that used to crash it
python -m scripts.harvest_0e407ec7 --runtime research/harvest-0e407ec7/latest.json --output /tmp/harvest-check
```

## H. Files written by this pass

- `research/day3-0e407ec7/VERIFICATION.md` (this file)
- `research/day3-0e407ec7/CI-FAILURE.md` — diagnosis of the failed publication run 38809354350 and of this
  session's own reproduced audit failure on row 1081529
- `research/day3-0e407ec7/quotes/polymarket-5763247-legacy-betboom.json` — Group B decider market receipt
- `research/day3-0e407ec7/quotes/polymarket-5733288-aurora-9z-crosscheck.json` — Group A decider cross-check receipt
- `data/analysis.json` — corrections E1, E4, E5 plus the additive day-3 content (B6, B8, C1–C6)
- `data/review-notes.json` — additive entries for irregularities 1, 2, 3 and the lock-time note (C3)
- `scripts/harvest_0e407ec7.py`, `tests/test_harvest_0e407ec7.py` — irregularity 6 fix and its regression test
