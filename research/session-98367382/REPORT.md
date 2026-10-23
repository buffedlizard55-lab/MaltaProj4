# Independent CS2 board audit — 2026-10-23

**Session:** `98367382` · fixed branch `arena/98367382-maltaproj4`

**Audit clock:** `2026-10-23T09:57:29Z` for the retained-snapshot coverage contract. A fresh live Hotspawn page read followed that clock and completed before `09:58:59Z`; the retrieval tool does not expose upstream response timestamps.

## Executive result

The last successful published snapshot is internally complete for its recorded Hotspawn CS2 inventory: **92 fixtures, 30 open, 30 picks, 30 numerical win probabilities, 0 research-only rows, 0 unresolved rows, and 62 not open by sourced lock/start/status**. All 30 open recommendations are supported by a retained non-Hotspawn evidence source and pass the independent arithmetic/identity/deadline audit. Hotspawn crowd percentages are not used.

**Important live-source limitation:** a fresh read of Hotspawn’s generic lobby showed **94** in its count filters, while its dedicated CS2 Pick’ems page showed **92**. The generic lobby’s selected game state and the exact IDs behind the count difference were not exposed by the text retrieval. This is **not** enough evidence to call two CS2 fixtures missing or to add picks. The mismatch is now source-linked on the generated **Flagged for Review** page; the board remains at the last complete three-view capture until a fresh API/page/lobby capture compares exact IDs.

## Snapshot and methods

- Retained `data/latest.json`: generated `2026-10-23T08:32:56.593552Z`; fixture observation `2026-10-23T08:29:19.125787Z`; SHA-256 `19fcf9853cddbd12b10cdeb00e62cf7128ed3b0b48adf0c7945891735ce3a4df`.
- Last complete automated Hotspawn parity receipt: **API 92 / dedicated CS2 page 92 / general lobby 92 / retained 92**, with coverage marked `verified` and no fixture conflicts.
- Current open-row method mix in that snapshot: **20 Polymarket strict exchange lines, 1 labelled wide-spread exchange estimate, 2 bookmaker-listing estimates, and 7 originated Valve VRS model lines**. The two EGamersWorld rows are labelled as secondary/listing-derived estimates—not operator API quotes or a multi-book consensus.
- The model rows use Valve’s published global standings plus its published model-fit formula/calibration, with HLTV roster context. HLTV ranks/fan votes are not converted into percentages. When no accepted market/model number exists, the implementation supports research-only picks with no percentage or an explicit unresolved row; neither category occurs among this snapshot’s 30 open matches.
- **62 not-open records are retained in All matches.** They do not receive a current pre-match pick after the sourced lock/start/status says they are not open.

The full dated, source-linked ledger of all 30 open picks is [open-picks.md](open-picks.md). The independent auditor’s 92-row, source/evidence/arithmetic report is [row-audit.md](row-audit.md); the fresh-clock classifier output is [coverage-contract.json](coverage-contract.json).

## Current Hotspawn source comparison — flagged, not inferred

Official pages reviewed:

- [Hotspawn general Pick’ems lobby](https://play.hotspawn.com/lobby): the rendered count filters showed `All tiers (94)`, `All tournaments (94)` and `All teams (94)`, alongside `CS2` and `LoL` tabs.
- [Hotspawn dedicated CS2 Pick’ems page](https://play.hotspawn.com/cs2-pickems): the corresponding rendered filters showed `92`.
- [Hotspawn CS2 fixtures API](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1): the last committed complete source receipt is dated `08:29:19Z` and was part of the 92/92/92 parity capture.

The discrepancy repeated on a second page read. Because the text retrieval does not identify the generic lobby’s selected game state, does not provide exact row IDs for the two-count difference, and does not expose a server observation timestamp, this audit does **not** claim that the 94 count is a verified CS2 inventory. No match, team, probability or pick was invented. See the additive note `98367382-hotspawn-lobby-view-count-difference-2026-10-23` in `data/review-notes.json`; a regression test confirms it is rendered with all three official Hotspawn links on `review.html`.

## Non-Hotspawn probability sources and limitations

- **Polymarket:** 21 rows total (20 strict, 1 clearly labelled wide-spread/low-precision tier); market evidence retains exact event/market identity, two-way price, observation/update time, spread and liquidity. Example direct market/API receipts are linked per row in [open-picks.md](open-picks.md).
- **Valve VRS model:** 7 rows; independently reproduced from the official [Valve standings repository](https://github.com/ValveSoftware/counter-strike_regional_standings), with Valve’s published model formula/calibration and HLTV roster context. These are labelled as our model estimates, not bookmaker odds.
- **Book listings:** 2 rows use [EGamersWorld](https://egamersworld.com/counterstrike/matches) as a secondary listing source and are explicitly labelled as listing-derived estimates. Fixture `1082859` uses EGamersWorld’s six-operator average; `1082860` uses the displayed Thunderpick pair, with five other operators on the same listing and an independent bo3.gg corroboration. Neither is a direct operator API capture. Both observations disclose that operator price-update timestamps are unavailable and are subject to the eight-hour evidence expiry gate.
- **No Hotspawn probability input:** fixture identity and lock/start come from Hotspawn; its crowd-pick percentages are removed from the retained evidence and never enter the model or calculations.
- **Unresolved policy:** blanks remain blank; no 50/50 fallback, inferred best-of, guessed alias, or probability from HLTV ranking/fan votes. The live mismatch above is a fixture-inventory uncertainty, not an unresolved odds row, and is separately flagged.

## Freshness, automation and live deployment

- `.github/workflows/pages.yml` is configured for four scheduled publication attempts per hour at `:04`, `:19`, `:34`, and `:49` UTC. `.github/workflows/refresh-watchdog.yml` is configured for a ten-minute check and dispatches the same verified refresh only after the published snapshot exceeds 90 minutes, with cooldown and daily-budget safeguards. The repository correctly documents that GitHub schedule delivery is best-effort, not guaranteed.
- GitHub Actions run [39924864346](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39924864346) succeeded on `4716f970`; its refresh, browser gates, deploy, and “Verify live Pages bytes match this exact build” steps all succeeded. The live [build receipt](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) matches that revision and reports 92 rows built at `08:32:56Z`.
- GitHub’s Actions API showed the latest `pages.yml` schedule event at `07:20:51Z` (success); the later successful full refresh was the `08:28Z` push run above. The latest watchdog schedule event returned by the API was `05:31:38Z` and was cancelled. No later scheduled event was present in the audit read. This is a **cadence-delivery irregularity**, not evidence that the workflow definition is missing; it remains a best-effort service and is flagged in this report.
- I attempted a non-publishing manual `workflow_dispatch` on this session’s fixed branch to obtain a fresh three-view capture. GitHub returned `403 Resource not accessible by integration`; no permission bypass was attempted. A merge to `main` will instead trigger the repository’s normal verified push pipeline. If manual dispatch is needed outside that path, the GitHub integration permissions need attention.

## Executive summary and mobile verification

The live home page is the executive summary and links directly to [Updated picks](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html), [Unresolved & limitations](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html), [All matches](https://buffedlizard55-lab.github.io/MaltaProj4/matches.html), and [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html). Its picks-at-a-glance and phone bottom-tab navigation are already in the generated site. The added source-count note is included in the page build and will be published with the merged change.

The browser suite passed at `320`, `390`, `768`, and `1440` px; all open picks, both team probabilities, official fixture links, first-screen phone pick visibility, stale/expiry suppression, navigation, keyboard disclosures, accessibility checks, and no-horizontal-overflow scans passed.

## Verification performed

- Coverage contract at `09:57:29Z`, with `--require-fresh`: **30 open; 23 market; 7 model; 0 research-only; 0 unresolved; 0 expired; 62 not open; 30 actionable; 0 contract problems**.
- Independent retained-evidence auditor (`verification-c6/audit_snapshot.py`): **92 rows, 30 probability calculations, 0 failures**.
- Validator on generated build: **92 rows, 30 calculations, 15 pages, 820 internal links/assets, 20 artifact checksums, 224 displayed match rows**.
- Unit suite: **1,061 passed, 3 skipped**. Audit suite: **9 passed**. Integrity suite: **5 passed**. C6 suite: **12 passed**.
- Browser suite (`npm run test:browser`): all six suites passed, including 32 page/viewport accessibility and overflow scans and the 320/390 phone first-pick checks.
- New regression tests: **3 passed**; they ensure the live count mismatch is described conservatively, linked only to official Hotspawn sources, and rendered on `review.html`.

Detailed logs and machine reports are retained beside this report in `research/session-98367382/`. All reported percentages are dated estimates from the recorded snapshot and are not guarantees of outcome or live operator availability.
