# Hotspawn CS2 coverage / publication repair — 24 October 2026

## Executive summary

The existing site already implemented source-linked match tables, a mobile executive summary, an unresolved page and automated refreshes. The current outage was in publication acceptance, not a lack of source adapters. This session independently reproduced it, repaired the source-ladder stop on neutral primary lines and two historical fixture tests, and verified a replacement build.

**Dated verification, not a permanent coverage guarantee:** capture `2026-10-24T16:40:40.748952Z`, official inventory parity **83 API / 83 CS2 page / 83 lobby / 83 retained**, **22 open / 22 picks / 22 probability pairs / 0 unresolved**. Eighteen open lines are market-derived and four are explicitly labelled model-derived. Sixty-one retained rows were not open and remain unpriced. Exact source URLs, original fields, observations and failed attempts are in `live/snapshot.json` and the published evidence ledger.

## What changed

- A genuine neutral primary line retains its original values in `no_edge_lines` and continues HLTV, books and independent model/research, rather than stopping with no directional pick. No coin flip, guessed favorite or Hotspawn vote share is used. An inaccessible or unsupported fallback still leaves a blank, source-linked limitation.
- The equal Color / ex-Zero Tenacity exchange observation remains **50% / 50%** in source context. The selected **68.8395% / 31.1605%** is a separately labelled Valve-model calculation. These are different methods, not corroborating market prices or a consensus. The evidence page explicitly discloses this disagreement.
- Two historical identity/arithmetic contracts use retained dated fixtures rather than assuming those IDs remain in the rotating current feed. All current-row independent audits remain strict. Provisional relaxations of other independent verifiers were dropped.
- Phone tests count unresolved rows in the full coverage partition and inspect the exact linked fixture before demanding probabilities. Upstream PR #279's stale-banner guards were retained at integration.
- The optional picks-page filters now follow the match board at every phone height. The real fresh-board 320×844 placement failure (first pick y=863) is fixed without relaxing its browser threshold. Filters remain functional and keyboard accessible.
- A linked Flagged for Review entry records the publication failure and the practical schedule/source-access limitations.

## Official records and review links

| Finding | Primary record |
| --- | --- |
| Scheduled publisher failed after refresh, at staged-root validation/unit gate | [GitHub run 40097410704](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40097410704) |
| Independent live reproduction (historical-ID failures and neutral line demanded a favorite) | [GitHub run 40111520773](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40111520773) |
| Replacement live capture, corrected resolver; its two remaining test failures were subsequently repaired and every gate rerun locally | [GitHub run 40112370187](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40112370187) |
| Fixture membership, not probability input | [Hotspawn lobby](https://play.hotspawn.com/lobby) |
| Fallback identity, lineups and specialist match research | [HLTV matches](https://www.hltv.org/matches) |
| Model's official standings and formula inputs | [Valve regional standings](https://github.com/ValveSoftware/counter-strike_regional_standings) |
| Neutral primary exchange fixture | [Polymarket](https://polymarket.com/event/cs2-color-zerote-2026-10-25) |
| Integration pull request | [PR #281](https://github.com/buffedlizard55-lab/MaltaProj4/pull/281) |

## Verification receipts

- **1,490 unit tests**, seven explicitly non-applicable historical skips; nine audits; five integrity tests; twelve C6 tests.
- Independent retained-field/calculation audit: **83 rows / 0 failures**.
- Validator: **22 calculations reproduced, 15 pages, 787 internal links/assets, 20 checksums, 195 displayed rows**.
- Freshness/coverage contract: **22 actionable / 0 unresolved / 0 expired / 0 problems** at `16:46:32Z`.
- **All eleven Chromium suites pass**: phone/tablet/desktop accessibility and no overflow, 320/390/412px phone placement, links/navigation/filter functionality, strict expiry and stale-state withholding.
- Separate neutral-context replay test reconstructs original publisher fields and verifies the retained neutral pair; zero-liquidity observations cannot create neutral context.

Receipts are the adjacent `final-*.log`, `final-validation.json`, `coverage.json`, and `final-row-audit.md`. The older `staged-failures.json` and `live/staged-unit.log` are intentionally retained diagnostic failures, not claimed green runs.

## Limitations

The authoring sandbox cannot directly reach Hotspawn, HLTV, exchange or book hosts. Live reads were made by the unmodified collector on GitHub's runner, not fabricated locally. Replaying retained evidence verifies source-field consistency, source identity and arithmetic; it cannot prove the true winning chance or independently verify every organizational claim. Specialist HLTV and third-party book listings are labelled accordingly, not misrepresented as operator confirmations. Models are estimates, not official forecasts.

GitHub scheduling and runner queues are best-effort. The site attempts scheduled checks and has a watchdog; it cannot promise an uninterrupted 4–8-hour delivery SLA, especially if GitHub fails/delays jobs. Source timestamps and lock times remain authoritative, expired picks are withheld, and failures never relabel old evidence fresh. GitHub's shared REST quota was exhausted during this session; no authentication or access-control bypass was attempted. Merge and public deployment confirmation must be recorded separately and never inferred from a branch build.
