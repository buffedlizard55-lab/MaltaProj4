# Independent CS2 board audit — 2026-10-23

**Session:** `98367382` · fixed branch `arena/98367382-maltaproj4`

**Audit clock:** coverage contract `2026-10-23T10:16:14Z`. Manual rendered-page reads were bracketed by local UTC readings `10:14:56Z` and `10:16:15Z`; the retrieval tool does not expose upstream response timestamps.

## Executive result

The latest retained, source-verified snapshot under audit was generated at `2026-10-23T10:05:50.376420Z` from fixture evidence observed at `10:02:13.241104Z`: **92 fixtures, 30 open, 30 picks, 30 numerical win-probability pairs, 0 research-only, 0 unresolved, and 62 not open**. The automated capture reported API / dedicated CS2 page / general lobby / retained counts **92 / 92 / 92 / 92**, `coverage: verified`, no fixture conflicts, and no added or removed IDs versus the earlier `08:32:56Z` snapshot. All 30 open recommendations have retained non-Hotspawn evidence; the independent row audit reproduces all 30 probability calculations. Hotspawn crowd percentages are not used.

**Important live-source limitation:** the rendered count discrepancy is recurring. Complete automated capture at `10:02Z` recorded 92/92/92/92, but a fresh rendered-page read after `10:14:56Z` again showed **94** in the general-lobby filters and **92** on the dedicated CS2 Pick’ems page. A separate `09:47Z` audit matched all 30 visible open lobby fixture IDs one-to-one to the 30 open board rows; it did not resolve the exact IDs behind the two-count difference. Its tournament filters differed at VOID Autumn Cup (lobby 1 / feed 0) and CCT Europe Series #12 (lobby 3 / feed 2). The current text retrieval still does not expose the generic lobby’s selected-game state or the complete fixture-ID set. This is **not** proof of two missing CS2 fixtures and is not grounds to invent rows or picks. The updated note is linked on **Flagged for Review** and the timeline is in [live-inventory-check.json](live-inventory-check.json).

## Snapshot and methods

- Retained `data/latest.json`: generated `2026-10-23T10:05:50.376420Z`; fixture observation `2026-10-23T10:02:13.241104Z`; SHA-256 `e24362fa32b96deb01a66b2ce9333fe98ef6ee96f205425f012dc2434b019952`.
- Latest complete automated Hotspawn receipt: **API 92 / dedicated CS2 page 92 / general lobby 92 / retained 92**, `coverage: verified`, `fixture_conflicts: []`; `inventory_changes` vs the 08:32 snapshot had no added or removed IDs.
- Latest open-row method mix: **20 Polymarket strict exchange lines, 3 labelled wide-spread exchange estimates, 2 bookmaker-listing estimates, and 5 originated Valve VRS model lines**. The two EGamersWorld rows are labelled as secondary/listing-derived estimates—not direct operator API quotes.
- The model rows use Valve’s published global standings plus its published model-fit formula/calibration, with HLTV roster context. HLTV ranks/fan votes are not converted into probabilities. When no accepted market/model number exists, the implementation supports research-only picks with no percentage or an explicit unresolved row; neither category occurs among this snapshot’s 30 open matches.
- **62 not-open records** remain in All matches. The site labels past-dated feed rows separately and does not turn them into pre-match recommendations.

The full dated, source-linked ledger of all 30 open picks is [open-picks.md](open-picks.md). The independent auditor’s 92-row, source/evidence/arithmetic report is [row-audit.md](row-audit.md); the fresh-clock classifier output is [coverage-contract.json](coverage-contract.json).

## Current Hotspawn source comparison — flagged, not inferred

Official pages reviewed:

- [Hotspawn general Pick’ems lobby](https://play.hotspawn.com/lobby): the re-read after `10:14:56Z` showed `All tiers (94)`, `All tournaments (94)` and `All teams (94)`, alongside `CS2` and `LoL` tabs. Its tournament filters showed VOID Autumn Cup `1` and CCT Europe 2026 Series #12 `3`.
- [Hotspawn dedicated CS2 Pick’ems page](https://play.hotspawn.com/cs2-pickems): the same audit window showed `92` in the all-tier/tournament/team filters; VOID Autumn Cup was absent and CCT Europe 2026 Series #12 showed `2`.
- [Hotspawn CS2 fixtures API](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1): the complete automated `10:02Z` receipt is in `data/latest.json` (HTTP 200, 92 rows, SHA-256 `2e872d2b32948e0ee510aa8a12ef8bec8e009b9393f1699acf6c703ce084e51e`).
- A separate [09:47Z independent audit](https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/research/session-51a9c98a/REPORT.md) recorded 30 open lobby cards and mapped their IDs one-to-one to the 30 open board rows, while also seeing the 94-vs-92 total-count delta. It located the filter-count difference at tournament level but did not verify the two exact fixture IDs.

The 94-vs-92 render was seen in repeated manual reads (including after the automated 92/92/92/92 capture), so the automated capture does not establish that the later rendered state is permanently resolved. Conversely, the later filter count alone does not establish that all 94 entries are CS2 or identify any extra fixture. Do not infer which view is authoritative, or add a match, team, pick, probability or alias from counts alone. The additive note `98367382-hotspawn-lobby-view-count-difference-2026-10-23` in `data/review-notes.json` records this timeline; its regression test checks that the uncertainty and all three official Hotspawn links appear on `review.html`.

## Non-Hotspawn probability sources and limitations

- **Polymarket:** 23 rows total (20 strict and 3 explicitly labelled wide-spread/low-precision); market evidence retains exact event/market identity, two-way price, observation/update time, spread and liquidity. Direct market/API links are included per row in [open-picks.md](open-picks.md).
- **Valve VRS model:** 5 rows; independently reproduced from the official [Valve standings repository](https://github.com/ValveSoftware/counter-strike_regional_standings), with Valve’s published model-fit formula/calibration and HLTV roster context. These are labelled as our model estimates, not bookmaker odds.
- **Book listings:** 2 rows use [EGamersWorld](https://egamersworld.com/counterstrike/matches) as a secondary listing source and are explicitly labelled as listing-derived estimates. Fixture `1082859` uses EGamersWorld’s six-operator average; `1082860` uses the displayed Thunderpick pair, with other operators on the same listing and independent bo3.gg corroboration. Neither is a direct operator API capture. Both disclose that operator price-update timestamps are unavailable and are subject to the eight-hour evidence expiry gate.
- **No Hotspawn probability input:** fixture identity and lock/start come from Hotspawn; its crowd-pick percentages are removed from the retained evidence and never enter the model or calculations.
- **Unresolved policy:** blanks remain blank; no 50/50 fallback, inferred best-of, guessed alias, or probability from HLTV ranking/fan votes. The source-count discrepancy is an inventory uncertainty, not an unresolved odds row, and is separately flagged.

## Freshness, automation and deployment status

- `.github/workflows/pages.yml` is configured for four scheduled publication attempts per hour at `:04`, `:19`, `:34`, and `:49` UTC. `.github/workflows/refresh-watchdog.yml` is configured for a ten-minute check and dispatches the same verified refresh only after the published snapshot exceeds 90 minutes, with cooldown and daily-budget safeguards. GitHub schedule delivery is best-effort, not guaranteed.
- Main run [39935797381](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39935797381) completed successfully at `10:23:31Z` on `2f22fec`. Source refresh, independent row audit, build, validator, browser gates, legacy root fallback, Pages deploy, and **Verify live Pages bytes match this exact build** all passed.
- A cache-busted live [build receipt](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json?audit=20261023T102500Z) confirmed revision `2f22fecaee1dd616288b4a6a88c6c2920ede14da`, built `10:05:50.716317Z` from snapshot `10:05:50.376420Z`, 92 rows; its `data/latest.json` SHA-256 exactly matches the retained `e24362fa…` snapshot audited here. A non-cache-busted receipt briefly returned the old `4716f970` object, while the cache-busted receipt and homepage served the new build; record this as a CDN-cache inconsistency, not a failed deploy.
- Run [39936981314](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39936981314), triggered by PR #222, was cancelled while queued; the successful 39935797381 live-byte verification is the confirmed 10:05Z deployment. This session’s new review note is not in that build yet and awaits its own merged PR.
- GitHub’s Actions API read at `09:55Z` showed the latest `pages.yml` schedule event at `07:20:51Z` (success); the watchdog had no schedule event in its listed runs that day. The refresh watchdog’s decision logic is tested, but schedule delivery remains a **cadence irregularity**. A subsequent successful main push run does not prove schedule reliability.
- A non-publishing manual `workflow_dispatch` on this session’s fixed branch returned `403 Resource not accessible by integration`; no permission bypass was attempted. The normal PR merge-to-main pipeline remains the permitted publication path.

## Executive summary and mobile verification

The site’s executive summary links directly to [Updated picks](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html), [Unresolved & limitations](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html), [All matches](https://buffedlizard55-lab.github.io/MaltaProj4/matches.html), and [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html). Picks-at-a-glance and phone bottom-tab navigation are in the generated site. The source-count note is in the build output and will be public only after the queued Pages deployment and this session’s merged change are verified.

The browser suite was rerun against the `public/` build from the `10:05Z` snapshot with this note included. At `320`, `390`, `768`, and `1440` px, open picks, both team probabilities, official fixture links, first-screen phone pick visibility, stale/expiry suppression, navigation, keyboard disclosures, accessibility checks and no-horizontal-overflow scans all passed.

## Verification performed on the current snapshot

- Coverage contract at `10:16:14Z`, with `--require-fresh`: **92 total; 30 open; 25 market; 5 model; 0 research-only; 0 unresolved; 0 expired; 62 not open; 30 actionable; 0 contract problems**.
- Independent retained-evidence auditor (`verification-c6/audit_snapshot.py`): **92 rows, 30 probability calculations, 0 failures**.
- `scripts.validate` on the rebased root fallback: **92 rows, 30 calculations, 15 pages, 816 internal links/assets, 20 artifact checksums, 221 displayed match rows**. The rebuilt local `public/` (including the additive review note) validated separately: **92 rows, 30 calculations, 15 pages, 821 links/assets, 20 checksums, 221 displayed rows**.
- Unit suite: **1,090 passed, 3 skipped**. Hotspawn audit tests: **9 passed**. Integrity tests: **5 passed**. C6 audit tests: **12 passed**. The three session-specific review-note regression tests also passed and are included in the unit suite.
- Browser suite (`npm run test:browser`): all six suites passed, including 32 page/viewport accessibility and overflow scans and the 320/390 phone first-pick checks.
- `coverage-contract.json`, `row-audit.md`, both validator logs, and all test logs were regenerated against the `10:05Z` retained snapshot.

Detailed logs and machine reports are retained beside this report in `research/session-98367382/`. All percentages are dated estimates from the recorded snapshot and are not guarantees of outcome or live operator availability.
