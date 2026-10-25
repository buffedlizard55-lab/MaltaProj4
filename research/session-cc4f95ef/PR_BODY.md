# Final additive integration — verified CS2 pick coverage, mobile board and line-by-line audit

PR #325 from the Arena-fixed branch `arena/cc4f95ef-maltaproj4`. `main` has been
publishing fresh boards continuously through parallel sessions, so this final
PR is deliberately **additive**: it keeps main's current generated root bytes
and data snapshot untouched and adds this session's independent verification,
flagged notes, regression test and coordination receipt. The post-merge
publisher regenerates the legacy `main:/` root with the new review notes.

## Current board on main

- Official runner snapshot `2026-10-25T14:22:27Z`; root build
  `2026-10-25T14:34:24Z` (revision `fccf2ca`).
- 78 Hotspawn feed rows; **16 open, 16 picks, 16 two-way win probabilities,
  0 unresolved**. Earlier 13:30Z/13:46Z captures had 17 open; the 13:54Z pick
  lock passed, so the stale recommendation is withheld by rule.
- Method mix: 11 strict exchange, 1 researched book listing, 4 labelled Valve
  VRS model lines. Hotspawn crowd percentages are never used.
- Every displayed row carries an official Hotspawn source link; every priced
  row carries its accepted external source and every attempted source.

## Upstream fixes adopted, not duplicated

- PR #316: `same_club` identity-register bridge that fixed the frozen publisher
  when HLTV called Hotspawn's `Projeto do KinGui` side `Tropa do KinGui`.
- PR #311: deploy only after a verified Pages artifact was uploaded.
- PR #313: mobile gate tolerates an intentionally withheld stale board.
- PR #322 / #332 / #333: row-scoped quarantine backstop, successive fresh
  captures and the measured short-phone CSS compaction for the y=519 / y=507
  probability/tab-bar overlap.
- This session independently measured the same alias and phone failures on
  runner captures `40197480741` / `40197553353`, then adopted the single
  current upstream implementation of each. Its row-level regression replays
  the exact `1086697` capture and refuses altered rosters/unregistered aliases.

## This PR adds

- `research/session-cc4f95ef/LINE_BY_LINE_AUDIT.md`: all 78 rows with official
  source links, picks, probabilities, arithmetic checks and limitations.
- Four additive Flagged-for-Review notes (265 total) covering the publication
  freeze, the verified HLTV alias, the phone geometry and non-market /
  third-party line limitations, each with official links.
- `tests/test_session_cc4f95ef.py`: exact runner-row alias regression, identity
  ledger/source boundary, and byte-identical balanced stylesheet check.
- Final verification receipts under
  `research/session-cc4f95ef/verification/pr325-final3-*.log`.
- A final `COORDINATION.md` task/status table and sources. No generated root
  page or snapshot is overwritten by this PR.

## Verification (all green on the combined tree)

- 1,701 unit tests OK (12 skipped), 9 audits, 5 integrity checks, 12
  verification-c6 tests.
- `scripts.validate`: 78 rows, 16 calculations, 15 pages, 726 links/assets,
  20 checksums, 181 displayed rows — both root and rebuilt public tree.
- Independent replayers, zero failures: `verification-c6` (78 rows),
  `verification-93f6951a` (3,260 checks), `verification-e9be3e6b` (294),
  coverage contract 16 actionable / 0 problems.
- All 13 Chromium suites pass at 320×568, 390×844, 412×915 and desktop: no
  horizontal overflow, first pick and both probabilities above the fixed tab
  bar, 16 published picks and 16 priced rows.

## Official sources

- Hotspawn lobby: https://play.hotspawn.com/lobby
- Hotspawn fixtures API: https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1
- HLTV match 2399918: https://www.hltv.org/matches/2399918/tropa-do-kingui-vs-yawara-cct-2026-south-america-series-7
- HLTV matches / Valve ranking: https://www.hltv.org/matches and https://www.hltv.org/valve-ranking/teams
- Polymarket Gamma: https://gamma-api.polymarket.com/events and https://gamma-api.polymarket.com/markets/6158059
- Pinnacle esports API: https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight
- BO3.gg researched listing: https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026
- Valve Regional Standings: https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md
- Publisher evidence: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40193317196 , https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40197480741 , https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40197553353

## Flagged irregularities (non-blocking, published on the site)

- Four rows are labelled VRS model estimates, not market prices; one is a dated
  third-party Thunderpick/BO3.gg listing. GG.BET can return HTTP 403 and
  Pinnacle/HLTV do not always expose a numeric two-way quote. These limits are
  labelled on the picks, unresolved and review pages.
- `verification-4901f43e` reports two warnings about a stale figure in another
  session's archived prose and older HLTV alias citations it did not fetch;
  neither changes a current row.
- Pages remains `build_type: legacy` from `main:/`; the root fallback and the
  verified Actions artifact are kept byte-consistent by the workflow. The
  4-slots-an-hour schedule is a best-effort target with an eight-hour evidence
  gate, not a guarantee.

Live site after merge: https://buffedlizard55-lab.github.io/MaltaProj4/
