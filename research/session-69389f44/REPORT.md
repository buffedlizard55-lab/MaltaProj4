# Session 69389f44 — independent live-site and source audit

**Audit date:** 18 October 2026 (UTC)
**Branch:** `arena/69389f44-maltaproj4`
**Current status:** independent audit and PR #80 integration verification are complete. PR #80 is merged and the 98-row Pages deployment is byte-verified; PR #81 remains open with a merge conflict. This session is preparing a report/test/coordination-only PR on the fixed Arena branch.

## Executive findings

1. After PR #80 merged, main run [39085430548](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39085430548) refreshed and deployed the dashboard from `4f5d44b1…`; both its build/deploy and exact-live-byte check passed. A cache-busting public read at ~01:14Z reports build/snapshot time `2026-10-18T01:11:44.010765Z` / `01:11:43.690752Z`, 98 rows and revision `4f5d44b1…`. An initial unparameterized read still returned the preceding 00:52 snapshot (`b182d428…`); this stale CDN response is preserved separately and is not treated as the newest publication. The earlier 00:28 build (`3027f782…`) was the baseline for identifying the inventory mistake. The current summary reports 34 open rows: 17 market probabilities, 12 Valve VRS estimates, 5 research-only picks without percentages, and 0 open rows without a supported pick.
2. **Correction to an initial inference:** Hotspawn's rendered CS2 current-week filter showed 81 entries, but the 00:28 live dashboard snapshot already contains the exact final-day feed rows **1080209 Falcons–Aurora** and **1080210 FURIA–BetBoom**. The live analysis page dynamically recognizes both as current board rows and links to the current picks/evidence pages. Therefore the earlier inference “neither final was on the board” from the 81-entry UI count was wrong. The 81 UI count and 98 retained-feed count are not interchangeable; this audit did not reconcile every ID across both representations and does not assign a cause to the 17-row difference.
3. The initial 00:28 pick board listed **Falcons 60.5% / Aurora 39.5%** and **FURIA 70.5% / BetBoom 29.5%** from Polymarket, with separate VRS cross-checks of 63.6/36.4 and 72.9/27.1. A direct Gamma reread returned FURIA **71.5/28.5** (`updatedAt` 00:59:15Z); the 01:11 refreshed board then published the same 71.5/28.5, observed at 01:09Z. Aurora remained 60.5/39.5 on both the updated board and provider read. The one-point mismatch was present during the first audit, then resolved by the scheduled refresh.
4. The two official Thunderpick Match Winner pages were independently reread within **00:54:12–00:54:17Z**. They displayed Aurora **+140** / Falcons **−200** and FURIA **−286** / BB Team **+190**. Normalizing each two-way book line gives Falcons **61.54%**, Aurora **38.46%** (8.33% overround), and FURIA **68.24%**, BETBOOM **31.76%** (8.58% overround). These are one-book market estimates, not a true-win model or multi-book consensus. The new price receipt preserves the older 17 October quote; it does not assert why the displayed price differed.
5. The live executive summary has direct links to updated picks, the Day-5 guide, Day-4 results, unresolved limitations and all matches, and its extracted text describes a phone bottom bar. A stale-warning sentence is also extracted from the page text; **whether that warning is visibly rendered is unverified** because this read did not inspect rendered pixels.

## Live Pages and Hotspawn inventory

| Observation | Value | Source |
|---|---:|---|
| Current post-merge live build | Build-info revision `4f5d44b1…`; built 01:11:44Z; snapshot generated 01:11:43Z; 98 rows | [Cache-busted current build receipt](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json?cb=20261018T011400Z); prior baseline was `3027f782…` at 00:28:29Z |
| Snapshot/feed rows | 98 | [Build receipt](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json), [public snapshot](https://buffedlizard55-lab.github.io/MaltaProj4/data/latest.json) |
| Open coverage | 34 open: 17 market, 12 VRS, 5 research-only/no %, 0 without a supported pick | [Live executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/) |
| Hotspawn rendered CS2 filter | 81 in “All tiers / All tournaments / All teams”; “This week” heading shows 213 | [Official Hotspawn CS2 Pick’ems page](https://play.hotspawn.com/cs2-pickems) |
| Day-5 row 1080209 | Falcons–Aurora, 11:30Z, lock 11:24Z; 60.5/39.5 observed 01:09Z, expires 09:09Z | [Hotspawn match page](https://www.hotspawn.com/matches/aurora-vs-falcons-thunderpick-world-championship-2026-1080209), [live pick board](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html?cb=20261018T011400Z), [Gamma market 5837604](https://gamma-api.polymarket.com/markets/5837604) |
| Day-5 row 1080210 | FURIA–BetBoom, 15:00Z, lock 14:54Z; 71.5/28.5 observed 01:09Z, expires 09:09Z | [Hotspawn match page](https://www.hotspawn.com/matches/furia-vs-betboom-thunderpick-world-championship-2026-1080210), [live pick board](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html?cb=20261018T011400Z), [Gamma market 5837622](https://gamma-api.polymarket.com/markets/5837622) |

The public fixture API is [Hotspawn's scheduled-CS2 endpoint](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1). The live 98-row snapshot contains both IDs and the public match pages identify the exact Thunderpick World Championship matchups and starts. The UI-filter count of 81 does not disprove those source-feed rows. No claim is made here that every one of the 98 feed IDs has been row-by-row matched to a card in the rendered 81-entry filter.

The 00:52:19Z runner harvest attached to [PR #80](https://github.com/buffedlizard55-lab/MaltaProj4/pull/80) reported 98 rows, three-way inventory parity and an independent row audit with 0 failures. It was merged at `2026-10-18T01:03:15Z` as commit `25bcef3eca79c490c28c6097adc547cd94aa19e1`. Main run [39085054628](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39085054628) completed successfully at 01:07:10Z; its verify-build and deploy jobs passed, including “Verify live Pages bytes match this exact build.” Pages deployment [39085054721](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39085054721) also succeeded. A follow-on main run [39085430548](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39085430548) on commit `4f5d44b…` completed at 01:13:19Z, refreshed the inventory to a 01:11:43Z 98-row snapshot, deployed, and passed the same exact-byte check. The first unparameterized fetch still returned the prior build; a cache-busting query retrieved the current manifest and pick board. Publication is confirmed; the initial skipped PR deployment was not mistaken for a live release.

### Live-page copy and cadence notes

- At the pre-merge 00:28 baseline, `analysis.html` had a mixed-time state: dynamic cards said “Now on the Hotspawn board” and linked IDs 1080209/1080210, while static summary/limitations described them as absent from an earlier lobby observation. That absence inference from the 81-entry filter was false and is withdrawn. The post-merge live summary and Day-5 guide now identify both board IDs, the board line and separate book cross-check; dated research cards continue to state their specific limitations without claiming the live fixtures are absent.
- `index.html` extraction includes “Snapshot expired or timestamp unverified. Current picks are withheld.” The snapshot itself is under an hour old at the cache-busted read and the app may hide fallback text in a browser; visibility was not checked from pixels.
- After main run [39085430548](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39085430548) completed, an unparameterized build-info request still returned the prior 00:52 manifest (`b182d428…`). A cache-busted request returned the current 01:11 build (`4f5d44b…`); the workflow's exact-byte verification passed. This appears to be a stale cached response, not a stale deployment; both responses and URLs are kept in `post-merge-reread.json`.
- Scheduled Pages run [39084533776](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39084533776) completed successfully at 00:55Z, but its freshness gate skipped refresh/build/deploy because the 00:28 snapshot was still recent. This is a successful skip, not a failed build or a new deployment. The later main runs performed successful verified refreshes.
- The 00:28 board quotes for both Day-5 rows initially expired at 08:23Z / 08:25Z. The next verified refresh at 01:11Z renewed both quotes to an expiry of 09:09Z, still before their Hotspawn locks (11:24Z and 14:54Z). The configured scheduled refresh must renew them again before expiry or the freshness gate will withhold them. This audit does not promise an at-lock price.

## Direct market rereads

### Polymarket Gamma API

Direct source pages: [Aurora–Falcons, market 5837604](https://gamma-api.polymarket.com/markets/5837604) and [FURIA–BetBoom, market 5837622](https://gamma-api.polymarket.com/markets/5837622). The direct reread returned 71.5/28.5 for FURIA–BetBoom (`updatedAt` 00:59:15Z), versus 70.5/29.5 in the 00:28 site snapshot. The 01:11 site refresh then published 71.5/28.5, observed on the board at 01:09Z; Aurora–Falcons remained 60.5/39.5. Provider `updatedAt`, local API retrieval window and dashboard `observed_at` are separate timestamps. Outcome prices are not calibrated true-win probabilities or a cross-book consensus.

### Thunderpick

| Match | Displayed American price | De-vig estimate | Overround | Observation / policy expiry | Source |
|---|---|---|---:|---|---|
| Aurora–Falcons (BO3; 11:30Z) | Aurora +140 / Falcons −200 | Aurora 38.46% / Falcons 61.54% | 8.33% | Retrieved during 00:54:12–00:54:17Z; local eight-hour cutoff 08:54:12Z | [Thunderpick Match Winner](https://thunderpick.io/esports/cs2-betting/thunderpick-world-championship-2026/11024/aurora-vs-falcons/2843582) |
| FURIA–BETBOOM (BO5; 15:00Z) | FURIA −286 / BB Team +190 | FURIA 68.24% / BETBOOM 31.76% | 8.58% | Same retrieval window; same local cutoff 08:54:12Z | [Thunderpick Match Winner](https://thunderpick.io/esports/cs2-betting/thunderpick-world-championship-2026/11024/furia-vs-bb-team/2843592) |

The market pages did not expose a server-side quote timestamp. The recorded `observed_at` is a conservative local retrieval time, and the eight-hour expiry is a freshness policy—not a bookmaker-guaranteed quote lifetime. The cutoff is before both match starts and before the first row's 11:24Z pick lock. The older [17 October receipt](https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/research/session-e0fd5a32/day5-lines.json) remains historical: Aurora +170 / Falcons −238; FURIA −286 / BETBOOM +190. The same-minute tournament-card vs match-page discrepancy (+150/−208 vs +170/−238) is preserved as historical; the card itself was not reread in this capture. The page-price difference is observed, but its cause is not established.

The operator labels the grand-final participant “BB Team”; [the organization's official site](https://betboom.team/) uses BB TEAM and lists its CS2 roster. This supports the narrow label mapping to the project's canonical BETBOOM identity, not a claim about roster continuity.

**Do not average these sources.** The 00:28 board shows the Polymarket line; the later Thunderpick observation is a separate one-book cross-check. Direct Gamma and the board snapshot differ by 1 point for the final at the later read, while the book differs more. No consensus or independent true probability is asserted, and no Hotspawn crowd percentage was used.

## Day 1–4 results checked against HLTV

The 12 series listed below match the event result listing and match-specific pages. HLTV is a specialist secondary source; no tournament-organizer result confirmation was collected in this audit. Map details are included for the pivotal upset/rematch and Day-4 semifinals; each result row links to its match-specific page.

| Day | Result | Source |
|---|---|---|
| 14 Oct | **9z 2–0 Aurora** — Inferno 13–11, Nuke 13–1 | [HLTV match 2399384](https://www.hltv.org/matches/2399384/9z-vs-aurora-thunderpick-world-championship-2026) |
| 14 Oct | Falcons 2–0 Ninjas in Pyjamas | [HLTV match 2399385](https://www.hltv.org/matches/2399385/falcons-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026) |
| 14 Oct | Legacy 2–0 PARIVISION | [HLTV match 2399386](https://www.hltv.org/matches/2399386/legacy-vs-parivision-thunderpick-world-championship-2026) |
| 14 Oct | FURIA 2–0 BETBOOM | [HLTV match 2399387](https://www.hltv.org/matches/2399387/furia-vs-betboom-thunderpick-world-championship-2026) |
| 15 Oct | Falcons 2–1 9z | [HLTV match 2399409](https://www.hltv.org/matches/2399409/9z-vs-falcons-thunderpick-world-championship-2026) |
| 15 Oct | Aurora 2–0 Ninjas in Pyjamas | [HLTV match 2399408](https://www.hltv.org/matches/2399408/aurora-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026) |
| 15 Oct | FURIA 2–1 Legacy | [HLTV match 2399411](https://www.hltv.org/matches/2399411/legacy-vs-furia-thunderpick-world-championship-2026) |
| 15 Oct | BETBOOM 2–1 PARIVISION | [HLTV match 2399410](https://www.hltv.org/matches/2399410/parivision-vs-betboom-thunderpick-world-championship-2026) |
| 16 Oct | Aurora 2–0 9z (the Day-1 upset was reversed) | [HLTV match 2399412](https://www.hltv.org/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026) |
| 16 Oct | BETBOOM 2–1 Legacy | [HLTV match 2399413](https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026) |
| 17 Oct | FURIA 2–0 Aurora — Dust2 13–8, Inferno 13–10 | [HLTV match 2399414](https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026) |
| 17 Oct | BETBOOM 2–1 Falcons — Anubis 5–13, Dust2 16–14, Mirage 13–7 | [HLTV match 2399415](https://www.hltv.org/matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026) |

Aurora's rebuild was announced on **8 July 2026**, roughly **98 days before Day 1**, per [HLTV News 45082](https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan). It is not supported to call this a last-minute October roster change. The Day-1 9z result is important context, but the Day-3 2–0 Aurora rematch demonstrates why one upset should not be treated as a deterministic forecast.

## Day-5 pick framing and limits

- **Baseline picks:** Falcons for third place and FURIA in the final, supported by the current board's external Polymarket line and the separate Thunderpick page reads. On the 00:28 snapshot the Polymarket lines were 60.5% Falcons and 70.5% FURIA; later Gamma was 71.5% FURIA. VRS is a separate originated model line, not another market.
- **Aurora:** about 38.5–39.5% across the two current source reads. It is the closer underdog and a plausible variance selection only for someone deliberately chasing; no positive expected value or optimal leaderboard recommendation is established.
- **BETBOOM:** about 28.5–31.8% across the sources read. Its three consecutive 2–1 wins over PARIVISION, Legacy and Falcons are a concrete form case ([Day 2](https://www.hltv.org/matches/2399410/parivision-vs-betboom-thunderpick-world-championship-2026), [Day 3](https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026), [Day 4](https://www.hltv.org/matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026)); FURIA beat it 2–0 on Day 1 ([HLTV](https://www.hltv.org/matches/2399387/furia-vs-betboom-thunderpick-world-championship-2026)). The 11-vs-7 tournament-map count follows from these linked series and [FURIA's Day-2 match](https://www.hltv.org/matches/2399411/legacy-vs-furia-thunderpick-world-championship-2026) and [Day-4 semi-final](https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026); it is descriptive context, not a fatigue probability adjustment or proof of a mispriced line.
- Hotspawn's [rules page](https://play.hotspawn.com/how-it-works) describes pre-start locks, tier points, streak bonuses and weekly reset. No exact bonus formula, current user pick-share distribution or user's leaderboard position was verified. Hotspawn crowd percentages were not used as win probabilities. Therefore the site does not claim an optimal rank-climbing strategy.

## Existing PRs, ownership and integration

Before any merge, I inspected existing open PRs:

- [PR #80](https://github.com/buffedlizard55-lab/MaltaProj4/pull/80), head `9df14434…` (session a54996e1), covers the final-day verified harvest, updated Day-5 prices, current Hotspawn rows, mobile summary and publication. Its `verify-build` passed (98-row row audit, 371 unit tests, 9 audit, 5 integrity, 12 c6, browser/accessibility/expiry gates); it had not yet been merged/deployed at the time of initial inspection. This session does not edit its branch.
- [PR #81](https://github.com/buffedlizard55-lab/MaltaProj4/pull/81), latest head `b35ad584…` (session 23b7f5d9), is a no-percentage/research-queue UX follow-up. Its updated PR body records a fresh 98-row snapshot identical to main's 00:52:19Z snapshot and its verification passed (376 unit tests, independent row audit 0 failures, responsive/accessibility/expiry gates); its deploy job was skipped as a PR. GitHub currently reports `mergeable=CONFLICTING` / `mergeStateStatus=DIRTY`, so it remains open and unmerged. This session did not modify its branch or attempt to bypass the conflict.
- [PR #64](https://github.com/buffedlizard55-lab/MaltaProj4/pull/64) is a Day-1 source/strategy audit with passing checks but an older snapshot. [PR #23](https://github.com/buffedlizard55-lab/MaltaProj4/pull/23) contains October 15 Day-2/market references and a much older snapshot. They were inspected, not merged as current Day-5 evidence.

The Session 69389f44 claim was pushed at 00:50Z and its integration scope was expanded at 00:55Z. The later discovery that PR #80 was already actively claimed at 00:48Z changed the correct approach: preserve the independent source audit and do not overwrite its shared data/code scope. The only new additions in this session are session-unique receipts, tests and this report; no current live snapshot was hand-assembled or copied over `data/latest.json`.

## Verification record

- Session-specific receipt tests: `tests/test_session_69389f44.py` (reproduces both Thunderpick de-vig calculations, checks quote freshness limits, validates Gamma outcomes and preserves the 98-vs-81 distinction).
- **Local full verification completed 01:20:18Z:** 371 main/session Python tests passed; 9 independent audit tests, 5 independent integrity tests and 12 verification-c6 tests passed. The committed bootstrap and generated local `public/` snapshot each passed the independent row audit (81 rows, 0 failures). Public and tracked-root validators passed (81 source rows, 13 probability calculations, 15 pages, 570 links/assets, 20 checksums, 192 rendered rows). Browser checks passed 32 page/viewport accessibility/overflow scans at 320/390/768/1440px plus seven board-expiry and four research-quote boundary/future-clock scenarios. `git diff --check` passed; staged/untracked audit files will be checked again before the PR.
- Local build/validator data came from the committed bootstrap, **not** from the live 98-row site. It was intentionally not promoted into tracked root outputs and is not a deployment claim.
- PR #80 merge and its exact-byte-verified Pages deployment are confirmed above. PR #81 remains open with passing checks but a GitHub merge conflict; no merge was attempted.
- This session's report/test/coordination PR and any later merge/deployment remain pending; record their explicit status and checks after GitHub verification.

## Receipts in this session folder

- `day5-live-markets.json` — bounded official Thunderpick reread and reproducible American-odds arithmetic.
- `polymarket-reread.json` — later direct Gamma reread, including market update timestamps and the one-point FURIA display difference from the 00:28 site snapshot.
- `live-site-observation.json` — pre-merge deployed build, open-pick counts, current-week UI count, Day-5 row IDs, dynamic page state and freshness-gate result.
- `post-merge-reread.json` — cache-busted 01:11 live build and refreshed Day-5 rows after merge; records the separate provider and board timestamps.
- `verification.log` — final local test, audit, validator, browser and whitespace-check output.
- `tests/test_session_69389f44.py` — deterministic local checks for receipt arithmetic, post-merge rows, counts and linked report table rows.
