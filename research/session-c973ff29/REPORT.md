# Independent coverage contract — session c973ff29

## Scope and coordination

This session owns the new coverage-accounting script, its tests and its non-publishing workflow. It does **not** overwrite the featured-pick resolver, research receipts, shared table data or the executive-summary/mobile changes owned by active parallel sessions. [PR #139](https://github.com/buffedlizard55-lab/MaltaProj4/pull/139) owns the summary-discoverability work. [PR #144](https://github.com/buffedlizard55-lab/MaltaProj4/pull/144) contains this verification work.

The coverage contract is read-only: it never invents a pick, replaces an external price, changes a source timestamp, treats fan votes as probabilities, or removes an unresolved fixture. It does not certify the true chance of winning. The existing independent row auditor remains responsible for replaying identity and probability arithmetic from source evidence.

## Changes

- One row per input fixture, preserving an official Hotspawn link and a site evidence anchor.
- Separate counts for market, originated model, research-only, unresolved, expired and not-open rows.
- Current-time checks rather than assuming every row called `open` in an older snapshot is still actionable.
- Earliest expiry accounting: fixture observation + eight hours, accepted quote observation/update + eight hours, explicit expiry, start, lock and Pinnacle cutoff. A fresh snapshot cannot renew an old quote. Research-context observations are dated and expire too.
- Unsupported numeric methods, malformed probabilities, unknown-team picks, picks against the published favorite, blocked fixture identities, missing source links and unexplained unpriced rows fail the contract.
- Equal **sourced** probabilities are allowed only with no directional pick and an explicit limitation. This does not permit an invented 50/50 default; evidence replay remains required.
- Unresolved rows with linked research attempts and explicit limitations are a valid result, not a reason to synthesize a forecast.
- Twenty-eight synthetic fixed-clock tests; no assertions pinned to the changing committed fixture list.
- A runner workflow refreshes the existing official-source collector, quarantines failed rows, runs independent evidence replay, checks the contract, builds and validates. It never deploys or changes shared table data. Compact dated receipts are retained only under this session's research directory and only on its fixed branch; full raw-source artifacts expire after seven days.

## Verification performed locally

- `python -m unittest discover -s tests`: **630 passed** at the session's original integration baseline, including 28 new tests.
- Independent audit tests: **9 passed**; integrity acceptance: **5 passed**; verification-c6 tests: **12 passed**.
- Build/validator: **75 sourced rows**, **11 reproduced probability calculations**, **15 pages**, **649 internal links/assets**, **20 artifact checksums**, **174 displayed rows**. Counts are from the committed baseline, not a claim about today's complete live lobby.
- Browser checks: **32 page/viewport accessibility and no-overflow scans**, widths **320/390/768/1440**, filters, subpath links, six redirects, evidence anchors, expiry; seven board-expiry and four research-quote boundary/future-clock scenarios passed.
- Historical contract at `2026-10-21T21:27:36.742398Z`: 75 total, 13 then-open, 5 market, 6 model, 2 research-only, 0 unresolved; no contract problems. Explicitly historical: these are not current coverage counts.

## Live/source checks, 22 October 2026, approximately 01:17–01:22 UTC

These were actual retrieval-tool reads except the Valve file, which was read from GitHub's official contents API. A successful read is not a guarantee of future access or complete operator coverage. No new odds receipt or team alias was registered from this investigation.

| Source | Confirmed observation | Limitation / treatment |
| --- | --- | --- |
| [Live build receipt](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) | revision `40e1fab4313fc25f320d0cf08bffe9e5ee4f5443`, build `2026-10-22T00:55:06.084617Z`, snapshot `00:55:05.742549Z`, 97 rows | Distinguishes the actual published artifact from the older committed root fallback. |
| [Executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/) | At that build: 35 open, 35 picks, 28 probabilities (8 market + 20 model), 7 research-only, 0 unresolved. Direct updated-picks/unresolved links and per-match evidence links present. | Counts are dated to the build; they are not a future coverage guarantee. |
| [Canonical Hotspawn lobby](https://play.hotspawn.com/lobby) | Retrieval displayed a 74-entry filter and 12 open cards, including the four DFRAG fixtures and two Moscow fixtures. | This differed from the published artifact's larger inventory. The retrieval exposes no cache-age receipt, so it cannot establish a current inventory conflict or prove omissions. Keep the collector's cache-aware, three-source parity gate; do not overwrite the larger inventory from this read. |
| [HLTV FlyQuest–Staqued fixture](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026) | Exact teams; BO3; FlyQuest HLTV #61 displayed. The betting table in the retrieved chunk exposes advertising text, not a numeric two-way line. | HLTV is specialist identity/ranking context, not an official bookmaker. The separate 90/10 fan vote is **not used**. Localized displayed time is not treated as UTC. |
| [HLTV bracket slot 2399696](https://www.hltv.org/matches/2399696/cct-2026-challengers-europe-series-8-lower-bracket-round-3-2-cct-2026-challengers-europe-series-8) | “Match postponed”; both team slots are placeholders. | This page does **not** confirm a named benched gods–TitanFlow match. Existing schedule warning belongs on Flagged for Review; it cannot produce odds. |
| [HLTV benched gods team page](https://www.hltv.org/team/13599/benched-gods) | Wign, K014NZ, facer, norescue, yoyoS2; world #204 and HLTV's VRS mirror #160 displayed. | These are different ranking systems/dates, not direct win probabilities or replacements for Valve's pinned file. |
| [HLTV TitanFlow team page](https://www.hltv.org/team/14021/titanflow) | No active roster, no world rank, VRS dash and no upcoming match shown. | Missing display data is not proof that TitanFlow cannot win or lacks players elsewhere. No probability inferred. |
| [Valve's official pinned standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | Official contents API bytes match vendored SHA-256 `df96e7fc3cd91a2687ec08cac0128e50cc4e4e55346581679572e881d79ae61b`. FlyQuest #86/1093; benched gods has two rows (#157/811 and #329/516); no exact TitanFlow or Staqued label. | File is dated 5 October, not a newly measured rating. Duplicate labels require roster disambiguation. An absent second team cannot support a two-team numeric model. |
| [Pinnacle public esports matchups](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/matchups) | The retrieved first chunk is usable JSON, containing parent fixtures and special markets across multiple esports. | Response has 106 chunks. This session did not manually inspect every chunk and therefore makes **no exhaustive absence claim**. The automated exact-pair, period-0 resolver remains required. |
| [Thunderpick CS2 page](https://thunderpick.io/esports/cs2-betting) | All four retrieval chunks read. Four featured cards rendered, followed by generic guide text; no FlyQuest–Staqued or benched gods–TitanFlow price in that rendering. | The UI also advertises 62 events, so four rendered cards cannot establish whole-book absence. No new probability accepted. Marketing examples and stale 2023 guide text are not current match odds. |
| [GG.BET CS2 page](https://gg.bet/en/esports/counter-strike) | Explicit “not accepting visitors from your region” response. | Regional access limitation; not bypassed, not counted as an empty sportsbook. |

The hidden runtime-expiry warning is included in plain-text page extraction even when hidden in HTML. The successful live receipt and dated freshness strip, not that extracted warning alone, establish the observed snapshot age. The local browser suite tests the actual visible warning state.

## Source-backed limits available to visitors

The site already exposes [Unresolved & limitations](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html), the executive summary's [limitations section](https://buffedlizard55-lab.github.io/MaltaProj4/#unresolved-summary), [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html), and [Sources & methodology](https://buffedlizard55-lab.github.io/MaltaProj4/sources.html). No source-access limitation is turned into invented values. The schedule has frequent attempts and a watchdog, but GitHub may delay jobs: 4–8 hours is an operational target, not a guaranteed service level. Pages still reported `build_type: legacy` through GitHub's Pages API during this session; the existing verified root-fallback publisher is retained, not reconfigured by this audit.

## Runner and publication receipts

Fresh-source run: [39704552672](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39704552672). Final results and deployment receipt are appended after completion.
