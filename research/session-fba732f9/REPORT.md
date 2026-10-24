# Session fba732f9 — current CS2 coverage, recovery and integration report

## 1. Scope and evidence contract

This pass claimed the broken-refresh recovery, a new real-source capture, a row-by-row review of every open Hotspawn CS2 fixture, phone-first verification, and final integration. It stayed on `arena/fba732f9-maltaproj4` and did not publish from the capture workflow.

Hotspawn is used only for fixture membership, team IDs/names, competition, UTC start and pick lock. Its crowd percentages are not probability evidence. Exchange and book inputs come from their own retained API records; originated lines use Valve's published VRS points, formula and calibration, with HLTV's dated Valve ranking only where the monthly official file cannot resolve both clubs. HLTV crowd votes and ranks are not converted into probabilities. Unsupported values remain blank.

## 2. Fresh capture receipt

- Non-publishing Actions run: [40066434606](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40066434606), attempt 1, checkout `70cf6dc84fcb7b01d176cbe5bf07606eee56b190`; all steps passed in 5m12s.
- Runner evidence commit: `1362b028fc146986bf1dedd89b46ac6e7403b9ab` (`1362b02`).
- Snapshot: [`../harvest-fba732f9/snapshot.json`](../harvest-fba732f9/snapshot.json), generated `2026-10-24T05:34:01.441501Z`; official fixture response observed `2026-10-24T05:30:27.487614Z`.
- Snapshot SHA-256: `c63d16fc9b7101c44e2d9b42c1a2669164e7e0068c738d2c8acebb25d8c6f569`.
- Official discovery: [scoped fixture API](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1), [CS2 lobby](https://play.hotspawn.com/cs2-pickems), and [general lobby](https://play.hotspawn.com/lobby). All three returned HTTP 200; both HTML reads were cache-busted misses with `Age: 0`. Their ID sets and retained primary fields agree at **88 / 88 / 88 / 88** (API / CS2 page / general lobby / retained), with no fixture conflicts.
- Result: **88 sourced rows; 25 open; 25 picks; 25 two-sided probabilities; 0 research-only rows without a percentage; 0 unresolved open rows; 0 quarantined rows**.
- Open-row methods: **12 exchange, 2 labelled wide exchange, 2 bookmaker fallback, 7 official-file VRS model, 2 HLTV-published Valve-points mirror**.

The runner's [summary](../harvest-fba732f9/summary.md), [all-row source ledger](../harvest-fba732f9/row-ledger.md), [independent audit](../harvest-fba732f9/independent-row-audit.md), [structured audit](../harvest-fba732f9/audit.json), [browser log](../harvest-fba732f9/browser.log), and [run identity](../harvest-fba732f9/run.json) are committed. The fresh candidate was also rebuilt and tested locally rather than accepting the runner result on faith.

## 3. Inventory reconciliation against the previous board

The previous committed snapshot had 90 rows and 27 open picks; this capture has 88 rows and 25 open picks. The difference is accounted for, not silently ignored:

- Nine newly discovered IDs are all present and open: `1079658`, `1079659`, `1079660`, `1079661`, `1081152`, `1081153`, `1081154`, `1081156`, `1081158`.
- Eleven IDs departed all three current Hotspawn views: `1079657`, `1081150`, `1081605`, `1081606`, `1082693`, `1082923`, `1082924`, `1082925`, `1082980`, `1083014`, `1083025`. Ten were open on the previous board and had source starts/locks on 23 October; `1081605` was already not open.
- `1082926` Isurus vs Hacha remains in the feed but is now `not_open` after its sourced `2026-10-23T12:54:00Z` lock and `13:00:00Z` start. Its old pick is not carried forward as current.
- Thus all 11 previous open rows that are no longer open are explained by their prior-day source times: ten departed the current views and one remains as not-open. No still-future previous open row was dropped to make the coverage count pass.
- The other 63 retained feed rows are not open by sourced status/timestamps. They remain visible in All matches with no current pick. The official feed's continuing `scheduled` label on those records is published as a refresh/coverage finding on Flagged for Review, not rewritten into a claimed result.

## 4. Line-by-line open-row review

[`open-row-review.md`](open-row-review.md) lists all 25 rows individually with the official Hotspawn link, UTC start and lock, pick, both probabilities, method, raw derivation, quality inputs, primary review links, and every published flag. [`../harvest-fba732f9/row-ledger.md`](../harvest-fba732f9/row-ledger.md) separately covers every one of the 88 retained rows, including the 63 not-open rows and their blank-value checks.

Independent replays agree on every row:

- C6 retained-evidence replay: **88 rows, 0 arithmetic/field failures**.
- Additional coverage/integrity audit: **25/25 open picks and probabilities, 0 integrity failures**, full three-view coverage.
- The separate session-0cc1138a implementation, which shares no pipeline code, re-derived **25/25** exchange mids, book de-vigs, official VRS lines, and HLTV-published Valve-points mirror lines with **0 failures**. Its output is retained as `independent-rederivation.txt`.
- Every exchange row is an active, unclosed, order-accepting whole-series moneyline with exact team/start orientation, two outcome prices, fresh observation/update, liquidity above the project threshold, and a valid two-sided quote. Exchange probabilities are the normalized outcome prices; no Hotspawn pick rate enters the calculation.
- Both book rows have exact BO3 fixture/team IDs and UTC starts, active team-bound Thunderpick moneylines, and reciprocal de-vig calculations. NEXVOID–Alter Ego uses 1.60 / 2.17 (8.5829% overround); FlyQuest–Staqued uses 1.001 / 12.0 (8.2334%). Direct operator and BO3 links are supplied. The missing tick-level price-update timestamp is disclosed and the observation-time TTL applies.
- All nine model rows reproduce Valve's RD-75 expectation and 0.7986 calibration around 50%. Both teams' points and standings are retained, and every current HLTV lineup/standings roster overlap is at least three players. The two mirror rows explicitly say their points came from HLTV's 24 October Valve-ranking view rather than Valve's 5 October monthly file.

## 5. Irregularities and limitations kept visible

These do not block a valid build, but none is hidden or replaced with a guess:

- **Wide/low-precision exchange quotes:** INOX–BRUTE and Color–ex-Zero have 15-point spreads and carry low-precision flags inside the strict tier. Metizport–BakS (31 points) and Ground Zero–Off Chops (33 points) use the separately labelled low-confidence wide tier below the 60-point ceiling. Their real spreads and liquidity are printed in the row review and on the site.
- **Originated rather than market lines:** all nine VRS rows are labelled as model estimates, not betting-market prices. The two mirror rows have the additional source limitation.
- **Book timestamp limitation:** the two Thunderpick-via-BO3 rows disclose a single-operator line and no tick-level update timestamp.
- **Source access:** GG.BET returned HTTP 403 after the logged 10/30/60-second waits. The EGamersWorld Rooster–Abyssal recheck likewise returned 403 after those waits; the Acend–UNiTY, HOTU–The Huns and 5star–1WIN rechecks were then skipped fail-closed after the host block. These are collection limitations, not claims that odds do not exist. HLTV was checked first for rows unresolved by the featured path, and every such row ultimately resolved through a validated book or documented VRS line.
- **Schedule review:** all open-row external price/model records retain exact UTC-start identity. HLTV pages can render localized clock labels different from Hotspawn's lobby; the retained HLTV `data-unix` identity, not the visual timezone label, controls matching. No unsupported start correction or open-row schedule conflict was accepted. The 63 past/not-open records still labelled `scheduled` are the actual current feed irregularity and are flagged.
- **No unresolved current pick:** the separate Unresolved & non-market page lists the nine model rows and two book fallback limitations as applicable; zero open rows lack a pick or percentage in this dated capture. This is not a promise that a later refresh can always resolve every match.

## 6. Repairs made during integration

1. `tests/test_session_0cc1138a.py` had treated two historical lobby IDs as permanently present. My initial repair in `036b6e2` used source-proven expiry. While PR #243 was queued, PR #240 merged a more general rotation-proof repair: the historical observation is now checked against its immutable archived snapshot, while live-board coverage comes from each snapshot's own three-view counts. The rebase dropped my superseded overlapping patch and retained that implementation; missing still-future fixtures remain hard failures.
2. Fresh data exposed that `research/session-0cc1138a/verify_0cc1138a.py` replayed official-file VRS rows but not the already-supported `model_vrs_mirror` method. PR #246 independently merged equivalent support while this PR was queued; the final branch retains that implementation, which applies the same Valve formula to the HLTV-published Valve-points provider under a separate derivation label. The intermediate candidate also added a synthetic mirror regression and a clear unsupported-row assertion; the final evidence-only PR leaves the newer merged implementation and its expanded suite untouched rather than carrying duplicate test changes.
3. `tests/test_session_f89bb1f8.py` hard-coded `23 Oct` in the phone next-pick strip. The combined suite now derives the expected date from the selected fixture's actual UTC start, preserving the phone-placement requirement without freezing the test to one snapshot.
4. The branch was rebased onto merged main `60a150b159aab5480dae9a759db67f2f9136d702`. Both `COORDINATION.md` conflicts were resolved as lossless unions. PR #240's executive-summary fallback-ladder addition was preserved by rebuilding the candidate with the merged builder, and every gate was rerun.
5. PR #246 then merged its own 36-second-older capture and phone-visible executive-summary bar. A second rebase onto `dd9217806e63511a34334da7635571607d60bb5d` preserved that bar, its CSS, review notes, HLTV-first/book ledger and all prior reports while retaining this capture and audit. Duplicate mirror/date fixes were de-duplicated in favor of the merged implementations. The combined builder regenerated the site and the complete gates were rerun again.

No freshness, expiry, identity, calculation, source-link, or mobile gate was weakened. The two initial local browser failures against the day-old build were not treated as UI regressions; the unmodified freshness behavior passed against the fresh capture.

## 7. Verification on the intermediate 88-row combined candidate

The staged root and `public/` are byte-identical for the 20 manifest files. After both lossless rebases and the combined rebuild, `build-info.json` records source revision `7e14e7ceedee3d6ecca96588c8daf03a02087d6c`, build `2026-10-24T06:03:52.079849Z`, snapshot `2026-10-24T05:34:01.441501Z`, and 88 rows.

- Full final-combined Python suite: **1,229 tests OK, 1 skipped**.
- Independent audit suites: **9 audit tests OK; 5 integrity tests OK; 12 C6 tests OK**.
- C6 published-snapshot replay: **0 failures**; additional coverage/integrity audit: **0 failures**.
- Static validation on both the rebuilt candidate and staged root: **88 primary-snapshot rows; 25 calculations; 15 pages; 825 internal links/assets; 20 checksums; 217 displayed match rows**.
- Browser: all **8 chained Chromium suites** passed on the runner and locally on fresh data: 32 accessibility/no-overflow scans, 320/390/768/1440 layouts, phone first-screen pick and both probabilities, official row links, all open rows, unresolved/limitations surfaces, subpath/legacy routes, freshness clocks, and exact expiry/filter behavior.

## 8. Final integration on the current 92-row main board

Main advanced again through PR #251 while this PR was queued. That PR independently merged equivalent retained-identity replay support and a more fundamental repair for the unclosed CSS media block. The final fba732f9 PR therefore **de-duplicates those implementations and carries no production-code or generated-dashboard changes**. It retains this session's additive capture, independent evidence and reports on top of the current main board, avoiding another root-publisher race.

The integrated snapshot remains production run [40068512182](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40068512182)'s `2026-10-24T06:19:43.492019Z` read (fixture evidence `06:16:00.648005Z`): **92/92/92/92 API/page/lobby/retained rows, 31 open, 31 picks, 31 probability pairs, 0 unresolved**. Methods are 16 strict exchange, 3 labelled wide exchange, 3 book fallback, 6 official-file VRS and 3 HLTV-published Valve-points mirror. The earlier 88-row capture and its 25-row review remain unchanged as dated evidence.

Before that de-duplication, this session independently reproduced the stale-CSS/phone placement and KinGui replay failures described above. PR #251's merged implementations are retained rather than replaced. A direct manual check also confirmed the high-risk identity: [Hotspawn fixture 1083121](https://www.hotspawn.com/matches/meia-noite-vs-projeto-do-kingui-cct-south-america-2026-series-7-1083121) lists Projeto do KinGui at 16:00 UTC; [HLTV match 2399904](https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7) uses Tropa do KinGui with the matching players; [Polymarket market 6081997](https://gamma-api.polymarket.com/markets/6081997) uses the HLTV label at the same 16:00 UTC start. The quote remains a dated market observation, not a Hotspawn percentage.

The exact committed root and a freshly rebuilt `public/` are byte-identical. `build-info.json` records revision `118e3b168ceb7e9412ac3b6faa3ebc54cf5a6497`, build/snapshot `2026-10-24T06:19:43.860972Z` / `2026-10-24T06:19:43.492019Z`, 92 rows, and manifest SHA-256 `1319757f44520a97df19e0174c1c2176baccbc1550d0ec683f849e6e27227c48`. Canonical and published CSS are byte-identical at SHA-256 `e0fe006317309312197389e64e756e2e4f8b4613dd507528f55b01ba203020b8`.

- Full Python suite: **1,254 tests OK, 1 skipped**.
- Independent suites: **9 audit + 5 integrity + 12 C6 tests OK**; C6 row replay **0 failures**.
- Separate no-pipeline-import replay: **31/31 rows re-derived, 0 failures**.
- Static validation on both root and `public/`: **92 primary-snapshot rows, 31 calculations, 15 pages, 874 internal links/assets, 20 checksums, 234 displayed match rows**.
- All **9 Chromium suites** pass on that exact artifact: 32 accessibility/no-overflow scans, 320/390/768/1440 layouts, exact expiry/filter boundaries, official row links, both probabilities, and computed phone order/44px CTA/probability placement at 320x568 and 390x844.
- [Integrated 31-row line-by-line review](integrated-open-row-review.md) gives every official Hotspawn URL, UTC start/lock, pick, both probabilities, raw derivation, quality inputs, primary review links and flags. [Its independent replay](integrated-independent-rederivation.txt) is retained separately from the earlier 25-row capture replay.

Final PR, merge, production refresh, Pages deployment, and exact live-byte receipt are recorded separately in `COORDINATION.md` once measured; this report does not claim them prematurely.
