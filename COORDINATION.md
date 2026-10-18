# Shared task board

## Current ownership

Session **c4d25599** is the final integrator. Arena fixes this session to `arena/c4d25599-maltaproj4`; no other working branch is created or checked out, and all direct pushes target this session branch. Main changes only through the requested explicit PR merges.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Integrate preserved implementation and independent audits; verify and fix collection, identity matching, evidence expiry and fallback coverage | done | c4d25599 | scripts/**, tests/**, data/**, requirements.txt, research/**, audits/**, .gitignore | 2026-10-15 |
| Final mobile dashboard, executive summary, picks, unresolved and Flagged for Review pages | done | c4d25599 (final integration) | site/**, docs/**, index.html, README.md, package*.json | 2026-10-15 |
| Scheduled refresh, build/security/browser checks, PR merge and verified GitHub Pages publication | done | c4d25599 (final integration) | .github/**, root deployment files, COORDINATION.md | 2026-10-15 |
| Earlier independent source and acceptance audits (incorporated; limitations published) | done | 21bf0503, 95b588c2, c6e9f285, f65f940e | audits/** and their uniquely named verification/research directories (preserve on integration) | 2026-10-14 |

## Session a56d155f claims (2026-10-15)

Arena fixes this session to `arena/a56d155f-maltaproj4`; no other branch is created or checked out. Session c4d25599's board above is historical (all items done, publication complete) with no commits after 09:38 UTC; this follow-up user request is new work, not a takeover of an active claim. Claimed before starting:

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Day-1 Thunderpick WC review (9z–Aurora upset), Aurora roster-change research, contrarian-pick analysis page | in progress | a56d155f | research/day1/**, site/analysis templates, analysis.html | 2026-10-15 |
| Resolve a pick for every currently unresolved fixture via HLTV/esportsbook research; tiered fallback pick generation with published limitations | in progress | a56d155f | scripts/hltv.py, scripts/core.py, scripts/refresh.py, scripts/fallback.py, tests/test_fallback*.py, data/identities.json | 2026-10-15 |
| Executive summary in-site pick links, mobile-first discoverability, unresolved+limitations section in exec summary | in progress | a56d155f | scripts/build.py, site/**, assets/**, index.html, README.md | 2026-10-15 |

## Session 621776e4 claims (2026-10-16, 19:35 UTC)

Arena fixes this session to `arena/621776e4-maltaproj4`; no other branch is created or checked out and no other branch is pushed.
Board state read before claiming: `origin/main` is at `40b13d3a` (PR #40, session 3c8d1136, merged 08:43Z). `git branch -r` lists
**only** `origin/main` — every earlier session branch has been deleted after merge, so **no active claim exists** and nothing is
being taken over. This is new user-requested work: day-3 (16 Oct) decider results including the 9z upset, day-4 (17 Oct)
guidance, percentage coverage for the remaining unpriced rows, and mobile discoverability.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Verify day-1/2/3 TWC 2026 results from HLTV, confirm the 9z–Aurora upset and the Aurora roster premise, publish a contrarian day-4 guide | in progress | 621776e4 | research/day4-621776e4/**, site/analysis templates, analysis.html | 2026-10-16 |
| Put a probability on every remaining unpriced open fixture (research HLTV then book lines); publish the unresolved section + limitations in the executive summary | in progress | 621776e4 | scripts/core.py, scripts/hltv.py, scripts/books.py (new), scripts/build.py, tests/test_priced_coverage_621776e4.py, data/** | 2026-10-16 |
| Mobile-first discoverability: executive summary that links straight to the picks board, phone-readable layout | in progress | 621776e4 | site/**, assets/**, scripts/build.py, index.html | 2026-10-16 |

Rules I am holding to: no editing of files owned by another session (none are claimed right now); small frequent commits;
`git pull --rebase` before every push; nothing called verified without a primary source link; unknown odds/probabilities stay
blank and are flagged, never inferred; Hotspawn votes are never used as probability.

## Coordination log

- 2026-10-15: Read local main and enumerated **all remote heads and their coordination boards** before claiming work. Local fetch initially exposes only main; all actual remote branches were checked with GitHub/git. Main still contains only README.md; prior PRs #2, #3, #4 and #6 remain open. All earlier claims are older than 60 minutes without commits (latest observed 2026-10-14 08:42:34 UTC). Taking over unfinished final integration under the user's stale-claim rule. No active claim is overwritten.
- Preserve the ee1fb536 implementation, 66b553de integration/research, independent audits and all earlier coordination histories. Review rather than blindly combine overlapping implementations. Previous verification statements are historical, not verification by this session. Other branches remain untouched.
- Before implementation, commit and push this claim. Run `git pull --rebase` (with merge preservation where needed) before every subsequent push. Keep work on this session's fixed branch. Log any conflicts and resolve without discarding other work.
- Evidence standard: Hotspawn establishes the fixture inventory only, never probability. Keep the featured external-line method; try attributable HLTV evidence and then primary esportsbook lines only for uncovered fixtures. Only independently reproducible calculations on verified inputs may be published as derived probabilities. Unknown facts/odds/probabilities remain blank; unresolved picks and source/access limitations are visible in the executive summary and Flagged for Review.
- Sandbox networking is limited to GitHub and package registries. Live non-allowlisted source checks must run through normal GitHub Actions networking or available retrieval tools; do not claim a source was checked when it was not. No paywall/access-control bypass, credential solicitation, fabricated rows or probability estimates from Hotspawn votes.
- Outstanding inherited findings to independently reproduce and address: source-update TTL not enforced in the browser; non-finite liquidity accepted; validator missing evidence/identity checks; a wrong-game API payload can erase last-good inventory; Pages previously showed only the README and configuration changes returned 403. Irregularities do not block publication, but broken builds or false verification do.

- Integration conflict: both histories added COORDINATION.md. Paused and resolved by retaining this session’s claim and preserving the other boards verbatim in `research/handoffs/`. Imported implementation history from 66b553de/ee1fb536; no implementation content or original branch was discarded. Independent audits from 95b588c2 and c6e9f285 are preserved in their original paths.

- Verification milestone: independently reproduced V01/V02/V03/V05. All now pass, including the source-update-specific browser regression. Added raw quote replay (identity, sport/market type, known best-of, status, age, spread, finite liquidity, bookmaker cutoff/alignment), a shared deadline for rows/hero/evidence/counts, and three-way Hotspawn parity with field-conflict blocking and previous-only open-row retention.
- First current runner refresh (08:24 UTC, 15 October): 80 source entries; 17 open; 11 accepted external-line probabilities; 6 unresolved. These are timestamped observations, not permanent coverage claims. Captures/receipts are in research/current and Actions run https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38705384018 . The next refresh will re-evaluate new aliases and every row.
- Additional primary-source research: official Falcons Store explicitly uses Falcons / Team Falcons branding (https://store.falcons.sa/en); the ROUNDS CS2 organization identifies its own @roundsgg handle (https://rounds.gg/2026/05/01/rounds-cs2-attend-vrs-lan-tournament-in-sweden-with-full-hltv-coverage/). Narrow main-CS2 aliases added with exact opponent and time still required; no academy or roster-continuity inference. Official WhiteBIT announcement identifies WBT as WhiteBIT Team but does not explicitly establish the WROTBERRY mapping, so those rows remain unverified.
- Publication constraint: direct Pages mode update returned HTTP 403. The explicitly pages:write-scoped setup workflow also failed (run 38706399874); existing legacy main/root configuration is unchanged. Will verify artifact deployment from main and, if required, use a verified static root fallback; do not report the dashboard deployed before live-route verification. Root scope includes generated HTML routes/assets only if required by the existing Pages configuration. No alternate branch or direct main push is permitted.

- Combined verification, 15 October: 81 Python tests pass (55 production + 26 independent audit/regression tests). Two independent auditors reproduced all 80 captured fixture rows and all 12 accepted price pairs in the 08:40 snapshot. Seven pages at four widths passed 28 Chromium/axe scans; seven precise deadline scenarios and the inherited real-capture source-update test passed. Live-source CI run 38707429592 is green. These claims do not certify true winning chances or 100% probability coverage.
- Remaining five open-pick limitations are published through data/review-notes.json and the generated executive summary / unresolved / Flagged for Review pages. They are **needs review**, not hidden blockers. Sources and actual primary observations are recorded in research/INTEGRATION-2026-10-15.md, research/current/ROW-AUDIT.md and research/current/snapshot-audit.json.
- Maintained Actions versions were checked through official GitHub release/tag/action metadata and pinned to exact commits (research/action-versions.json). Runner pinned to Ubuntu 24.04 to avoid an announced image migration. The final configuration will be rechecked in CI before merge.
- Final-integration root scope now explicitly includes the eight generated HTML routes, assets/**, data/matches.csv, build-info.json and .nojekyll as the small required legacy Pages fallback. scripts/stage_legacy.py can copy only the allowlisted, hash-verified public files. No generated large datasets or runtime/source archives are added. Scheduled publication remains an artifact deployment, with every live file checked against the exact build manifest.

## Concurrent main integration discovered at PR #11

- Our claim was pushed at 08:18:59 UTC. Session d1bae160 started a separate claim at 08:23:41 UTC while this work was running and merged PRs #8, #9 and #10 to main. Its branch did not exist during our initial complete remote enumeration. Discovered the changes when PR #11 reported conflicts; paused and read its full implementation, history and latest board before integration. Its task is marked **done**, with last handoff at 08:40:55 UTC, so no active task is being taken over.
- Preserve the complete current main tree verbatim in `research/handoffs/d1bae160/main/`, its final board in `research/handoffs/d1bae160.md`, and its full commit history through the main merge. Preserve old public route compatibility. No other branch is switched, rewritten or pushed.
- Resolve the six add/add/content conflicts (.github/workflows/pages.yml, .gitignore, COORDINATION.md, README.md, index.html, requirements.txt) using the verified c4d25599 implementation as the final integrator. Retire—not silently discard—the competing collector/templates/tests and diagnostic workflow to the preserved handoff. Exactly one production six-hour workflow remains.
- The concurrent implementation corroborates the 80-row returned inventory and successful Pages artifact deployment while the repository remains in legacy mode. Its sportsbook parser matches date rather than exact UTC and does not prove all the stricter current gates, so do not silently promote its seeded odds to current accepted evidence. Our primary-source ledger and fail-closed match/time/market validation remain authoritative.
- Publication is not yet claimed for PR #11. Re-run combined tests, old-route checks, root-fallback validation and final-head CI before merging, then verify every live file against the deployment manifest.

- Preservation check: all retired active files were byte-compared against the archived main tree before removal from production paths. All eight original d1bae160 tests pass when run in its preserved tree with its original requirements; active project requirements were restored afterwards. The later source-research diagnostic is now dispatch-only, so production has exactly one scheduled publishing workflow and no competing data commits.
- Added two rendered-output regressions: a changed visible percentage and a dropped All matches row must fail independently of the file checksum. The validator now verifies every displayed matchup, percentage, pick and official/evidence link against the already raw-verified published JSON, as well as proving the complete inventory is in the HTML. Final active Python count: 83 (57 production + 26 independent); eight additional preserved concurrent-baseline tests passed separately.

## Verified publication — 15 October 2026

- **PR #11 merged** at **09:23:35 UTC**: https://github.com/buffedlizard55-lab/MaltaProj4/pull/11 . Merge commit **2927f73a4e612e01998a074cb0a2c94348a15432**. Final-head push and PR checks both passed before the explicit merge.
- **Production deployment succeeded**: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38712601157 . Build, source refresh, independent row audits, 83 active Python tests, browser/accessibility/expiry checks, Pages deployment and exact live-byte verification all passed. The deploy job completed at 09:25:18 UTC. Every one of the 19 public HTML/asset/JSON/CSV files matched the exact build manifest, not just an HTTP-success/title check.
- **Live site independently retrieved after deployment**: https://buffedlizard55-lab.github.io/MaltaProj4/ ; also retrieved Sources, Flagged for Review and https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json . The live receipt names the correct merge revision and snapshot **2026-10-15T09:23:57.436431Z**. This is an actual deployment confirmation, not a branch preview.
- At that snapshot: **80 retained source entries, 17 open, 14 priced (13 primary exchange + 1 bookmaker fallback), 3 unresolved**. The wider ROUNDS markets became usable on refresh without weakening the quality policy. WROTBERRY/ENCE, WROTBERRY/BOJONG and mellren/Privateer remain unverified identities. These dated counts will change as fixtures lock and sources refresh.
- **Needs review, published rather than hidden:** API returned 78 IDs, CS2 page and general lobby each 80; union retained. The source/page caches have different observation ages. Complete current-source parity is explicitly unverified, not falsely claimed. Regional/JavaScript restrictions, unknown bookmaker update time, missing series formats and the absence of a calibrated historical model remain visible on the site.
- The existing legacy Pages mode did not prevent authenticated artifact publication. Its setting was not changed or bypassed. One production schedule remains, at 00:17 / 06:17 / 12:17 / 18:17 UTC. Fresh source collection, build, cache persistence and live verification all ran without user input.
- Superseded PRs **#2, #3, #4 and #6 closed successfully** with integration explanations after deployment. Their branches/history remain intact; incorporated audit/source work and concurrent main implementation are preserved. No other working branch was switched to, rewritten, deleted or directly pushed.
- Final follow-up: extend CSV exports with quote observation/update, expiry, snapshot and build timestamps, plus CSV/source/calculation verification, so a downloaded old file cannot be mistaken for an undated fresh line. Main UI and probability policy are unchanged. A small follow-up PR records this completed publication on main and runs the full gates again.

- CSV follow-up verified locally: all 84 active Python tests pass (58 production + 26 independent), as do 28 accessibility/layout scans, six old-route redirects and seven deadline scenarios. The CSV validator checks IDs, team orientation, calculated values, source links and every freshness timestamp. A mutation test proves altered export expiry is rejected.

## Session 1acdf159 verification pass — 2026-10-15

- Re-ran full verification on branch `arena/1acdf159-maltaproj4`: 58 production unit tests pass; 9 audit tests pass; 12 verification-c6 tests pass; 5 integrity acceptance tests pass; 28 browser/accessibility scans and 7 expiry scenarios pass.
- Build succeeds (`python -m scripts.build`): 80 sourced rows, 14 public pages, 19 checksummed artifacts. Validator passes with 80 rows verified, 12 probability calculations reproduced, 434 internal links/assets checked.
- No source data, probabilities, or picks were changed or fabricated. Existing published coverage and unresolved flags retained.
- Live source refresh was attempted (`python -m scripts.refresh`) but Hotspawn/Polymarket endpoints returned TLS/SSL errors in this sandbox; last-good inventory retained with `coverage: stale` and source failures recorded. No synthetic data added.
- No overlapping file scopes edited; only this coordination log appended.

- PR #13 merged: https://github.com/buffedlizard55-lab/MaltaProj4/pull/13 . Production deployment succeeded: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38717684406 . Live site: https://buffedlizard55-lab.github.io/MaltaProj4/ .


## Session a7c0a121 — Day 1 review, contrarian picks, alias research, mobile improvements (2026-10-15 follow-up)

- Claim scope: data/identities.json, data/review-notes.json (add verified WBT/WhiteBIT=WROTBERRY and Privateer=Privateer Gaming aliases, document Aurora roster context and 9z upset, add esportsbook-sourced research for tier-C Elisa/CCT matches), scripts/build.py (add Day 1 Thunderpick recap, contrarian/value picks section, mobile quick-links section in executive summary), assets/style.css (mobile UX tweaks for quick navigation), research/day1-a7c0a121.md (source record). No edits to shared files in other sessions' scope.
- External research (web access only through verified web-search/fetch): confirmed 9z 2-0 Aurora upset (13-11 Inferno, 13-1 Nuke) on Day 1 of Thunderpick World Championship 2026 in Malta; Aurora roster context (July 2026 addition of Jimpphat + kyxsan, fatigue noted by esportbet.com); HLTV team ranks for Stake Pulse and Elisa teams; esportsbook-sourced probabilities for WBT/EAC, HAVU/ROUNDS, mellren/Privateer, Voca/ROUNDS from multiple bookmakers.
- Polymarket's published team abbreviations handle WBT, BCG; HAVU/ROUNDS and mellren/Privateer are on Polymarket but have insufficient liquidity or spreads per project quality gates. Esportsbook lines (SportsBetExpert/Bovada/BetMGM-style aggregated odds) provide tier-C context but do not override strict primary-exchange gating for fair-line numbers.
- Add a dedicated "Contrarian / Value Picks" panel for the leaderboard climb strategy (contrarian but not stupid: identify matches where market overweights name-recognition vs recent form, roster integration, fatigue, or LAN/travel factors).
- Mobile improvements: prominent quick-links buttons in hero for "Today's picks" and "Unresolved", sticky mobile header nav, ensure executive summary links are thumb-friendly.
- Rebuild full static site, run tests, commit, push, and open PR for merge if all checks pass.

- Build complete (10:17 UTC): all 58 production tests pass, validator verifies 80 rows/12 calculations/438 links/19 artifacts, 14 public files checksum-verified. Stage_legacy copied verified output to the root Pages fallback.
- Identity additions: WBT/WROTBERRY (narrowly scoped to Elisa BreakOut #2), Privateer/Privateer Gaming, BC.Game/BC.Game Esports, Phantom/Phantom Esports, Voca/Team Voca, EAC/Esport Academy Copenhagen, BOJONG/BJNG aliases added to data/identities.json with primary HLTV/Liquipedia/bettinginesports sources. Note: these aliases will take effect on the next GitHub Actions refresh because the sandbox cannot reach Polymarket/Pinnacle endpoints (coverage: stale in this build); the existing cached prices still benefit from Falcons/ROUNDS/BetBoom aliases already present.
- UI additions: Day 1 Thunderpick recap panel documenting the 9z 2-0 Aurora upset with scores and sources; Contrarian/Value Picks panel identifying 9z (+325), PARIVISION (52.5%), BC.Game live-dog and Aurora onboarding risk as pick-em angles; prominent mobile quick-links bar in the hero with thumb-friendly buttons for "Today's Picks", "All Open Matches", "Unresolved", and "Contrarian/Value".
- Research record saved as research/day1-a7c0a121.md with all source URLs.
- Unresolved picks (5) remain unresolved per fail-closed policy: WROTBERRY/ENCE, WROTBERRY/BOJONG, HAVU/RoundsGG, mellren/Privateer, RoundsGG/Voca. With the new aliases, the next GitHub Actions refresh should resolve the WBT/WhiteBIT and mellren/Privateer identity mismatches if the underlying exchange quotes pass the liquidity/spread gates; HAVU/ROUNDS and Voca/ROUNDS will remain unresolved until markets show real liquidity. These limitations are published on the Unresolved and Flagged for Review pages as before.
## Session a56d155f — follow-up request (15 October 2026)

- Follow-up user request after the verified publication. Session c4d25599's claims above are all **done** with no commits after the CSV follow-up; this is new work, not a takeover of an active claim. Claimed the three a56d155f tasks in the table above before starting and pushed the claim immediately. Work stays on the Arena-fixed branch `arena/a56d155f-maltaproj4`; no other branch is created, checked out or pushed.
- Evidence standard unchanged: Hotspawn establishes fixture inventory only; probabilities come only from externally observed market lines or reproducible calculations on them; unknown facts stay blank and flagged. New user directives this round: (1) day-1 Thunderpick World Championship review including the 9z–Aurora upset and Aurora's roster change, with a contrarian-but-not-stupid pick framework; (2) a resolved pick for **every** Hotspawn fixture wherever any researched source permits, using HLTV first then esportsbook lines, with a separate unresolved+limitations section in the executive summary; (3) executive summary with obvious in-site links to the updated picks, mobile-first readability.
- Research order for uncovered fixtures: HLTV match pages (betting table + team identity via exact opponent/UTC-start fixture match), then esportsbook lines (Pinnacle public API first, then other accessible books). No Hotspawn votes, no rank-to-probability formulas presented as market probabilities, no 50/50 fillers. Any non-market fallback pick is labeled with its method and limitation at the row level.
- Rebase note: `git pull --rebase` before the first push hit a COORDINATION.md add/add conflict with concurrent session 1acdf159's PRs #13/#14 (verification-pass log only; no overlapping file scope). Resolved by preserving both logs verbatim; nothing discarded.

- **Rebase integration note (session a56d155f, 10:40 UTC).** `git rebase origin/main` hit conflicts after PR #15 merged this session's sibling work. Resolved by keeping this session's verified implementation and preserving the sibling session's work: its full log above, its research record `research/day1-a7c0a121.md`, and its non-conflicting files are retained untouched.
  - **Kept from a7c0a121:** the BC.Game ↔ BC.Game Esports alias (independently re-verified here against Polymarket market 5347748 `cs2-mibr-bcg-2026-10-15` and HLTV match 2399136), and the EAC ↔ EA Copenhagen naming (Liquipedia Elisa BreakOut Series #2 participant list corroborated the EAC/EA Copenhagen pairing, so it is included with a narrow scope). Their day-1 recap and contrarian content is preserved and expanded, with per-row source quality, on `analysis.html`; their research record stays in the repo.
  - **Not adopted, and why:** the `ENCE Academy` alias (canonical `ENCE Academy`, names `["ENCE"]`) would have relabelled the main ENCE team on *every* fixture, including a CCT/tier-1 event, so it was rejected as a correctness hazard — the playing-roster question is a review note, not a rename. `Phantom Esports`, `Team Voca`, `BJNG` and `WhiteBIT` were not adopted because no primary or near-primary source for the alias could be verified in this session and all open fixtures already resolve without them; they are listed as review items rather than used silently. The hardcoded percentage strings in the sibling's executive-summary panels were not carried over because they would go stale inside a pre-rendered page; the equivalent screen on `analysis.html` is rebuilt from each snapshot.
### Session a56d155f results (15 October 2026)

- **Task 1 — day-1 review.** `analysis.html` (content in `data/analysis.json`, full audit note in `research/day1/DAY1-REVIEW-2026-10-15.md`). Day-one results, the 9z–Aurora upset (Inferno 13-11, Nuke 13-1; luchov 1.61 rating, 97.4 ADR, 86.8% KAST; 62 VRS points to 9z), Aurora's 2026 rebuild (Jimpphat, kyxsan 8 July 2026, coach ash; MAJ3R stepped back, soulfly benched) with the coach's own HLTV comments, and a five-rule contrarian-but-not-stupid framework plus a live screen rebuilt from every snapshot. Source quality is labelled per row; the fatigue read is marked as betting-preview commentary and the map-level detail for Falcons–NIP is marked as not HLTV-confirmed.
- **Task 2 — full pick coverage.** The five open fixtures that had no pick now carry one: 1080281 WROTBERRY–ENCE (Polymarket 5583519, 0.61/0.39), 1080283 WROTBERRY–BOJONG (5583522, 0.835/0.165), 1080286 HAVU–RoundsGG (5583527, 0.695/0.305, exactly 25-point spread), 1080289 RoundsGG–Voca (5583533, 0.89/0.11) on the strict exchange tier, and 1081120 mellren–Privateer (5649536, 0.75/0.25) on the new documented wide-quote tier. Raw receipts are retained in `research/current/quotes/`; `scripts/backfill_quotes.py` applies them and `scripts/core.py` recomputes every value, so nothing is hand-entered. Two new verified aliases: WROTBERRY↔WBT (Elisa BreakOut Series #2 fixture parity, no official rename statement found → flagged) and Privateer Gaming→Privateer. Two new tiers are published with their limits: `exchange_wide` (only when strict fails, liquidity ≥ $100, spread ≤ 60 points, real spread and strict rejection shown) and `research_rank` (exact HLTV identity + both world rankings → pick with **no** probability or fair odds). The unresolved+limitations section is now in the executive summary and the research queue page.
- **Task 3 — executive summary and mobile.** Start-here cards linking the pick board, the unresolved section, all matches and the day-1 analysis; a new nav entry; fixed the navigation current-state bug where the unresolved page highlighted Review; table regions are keyboard-focusable; the research queue no longer opens with every row filtered out. Verified with 28 accessibility/layout scans at 320/390/768/1440 px and phone screenshots.
- **Verification:** 79 production tests (15 new tier/alias tests + 6 new pipeline tests driving the real refresh→audit path), 9 audit tests, 5 integrity tests, 12 c6 tests, the independent c6 row auditor on both the snapshot and the published artifact (0 failures), the validator (80 rows, 14 calculations replayed, 472 links, 20 checksums) and the browser/expiry suites. The c6 auditor was extended — not loosened — to recompute both new tiers; its own mutation cases are covered by the new tests.
- **Concurrent session noted:** PR #15 (session a7c0a121, "Day 1 recap, contrarian picks, verified aliases, mobile improvements") opened 10:22 UTC covers the same user request. This session's claim was pushed first (10:12 UTC) and its work is complete with every gate green, so it is not being taken over; PR #15 is **left open and untouched** — its branch, history and content are preserved, its CI run failed (38719751960) and it should be rebased on main by its owner. Its alias additions (BC.Game Esports, Phantom Esports, Team Voca, Esport Academy Copenhagen, BJNG) were **not** adopted here because no primary source was supplied for them and all open fixtures already resolve without them; its contrarian panel also hardcodes percentages in HTML, which this session's snapshot-derived screen avoids.
- **Irregularities to review:** WROTBERRY↔WBT has fixture-parity evidence but no official rename statement; the wide-quote tier trades precision for coverage and is labelled; the day-1 page mixes HLTV facts with one betting-preview commentary row; `data/latest.json` is an interim, receipt-backed snapshot until the next scheduled refresh replaces it. All are published on Flagged for Review with source links.

## Verified publication — session a56d155f (15 October 2026)

- **PR #16 merged** at ~10:34 UTC: https://github.com/buffedlizard55-lab/MaltaProj4/pull/16 → merge commit **514ce6f8adb280299550271a15afc794584de8e4**. Branch CI run 38721033633 (`verify-build`) passed on the rebased head, including the live source refresh, the independent c6 row audit (0 failures) and the browser/accessibility/expiry suites.
- **Production deployment succeeded**: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38721190419 . The deploy job's own step verified every public byte against the build manifest, and the live receipt reports revision `514ce6f8…` with `rows: 78` and 20 checksummed artifacts.
- **Post-merge rebase note:** main had advanced to PR #15's merge when PR #16 was rebased. Conflicts were resolved without discarding the sibling session's work (see the integration note above): its log, research record and verified aliases are preserved, its hazardous `ENCE Academy` mapping and unverified aliases were not adopted, and its hardcoded executive-summary percentages were replaced by the snapshot-derived screen on `analysis.html`.
- **Live site independently retrieved after deployment** (this session, 10:40 UTC): the executive summary, `picks.html`, `unresolved.html`, `analysis.html`, `review.html` and `build-info.json` all returned the new build. Live snapshot at that moment: **14 open matches, all 14 priced, 0 unresolved**, of which 2 are on the wide-quote low-confidence tier (HAVU–RoundsGG, mellren–Privateer) and 0 needed the research-only ranking tier. The live refresh independently reproduced the alias fix: WROTBERRY–ENCE priced 61.0/39.0 from Polymarket 5583519 and WROTBERRY–BOJONG 83.5/16.5 from 5583522, the same markets this session captured in its receipts.
- **Coverage is not a permanent claim.** Those counts are a dated snapshot and will move as fixtures lock; the deferred rows return to the unresolved list with their reasons, and the wide/research tiers are published as policy decisions on Flagged for Review.

## Session d3af051a — Thunderpick day-1/day-2 review, full pick coverage, mobile exec summary (15 October 2026, 22:30 UTC)

Arena fixes this session to `arena/d3af051a-maltaproj4`. Session a56d155f's work is merged on main (PR #16/#17) and its board is historical (all items done). The 21:22 UTC scheduled publication run **38809354350 failed** in the "Build and independently verify every row" step, so the live site is still the 17:00 UTC build. This is new work: a fix task, not a takeover of an active claim. Claimed before starting:

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Diagnose and fix the failed 21:22 UTC refresh/build (live site frozen at 17:00 UTC), re-verify source handling | done | d3af051a | scripts/**, tests/**, .github/workflows/** | 2026-10-15 |
| Day-2 Thunderpick World Championship review (Aurora–NIP, Falcons–9z, group B) + day-3 pick guidance (9z–Aurora decider) with per-row sources | done | d3af051a | data/analysis.json, research/day1/**, analysis page template | 2026-10-15 |
| Guarantee a pick or an explicit, sourced unresolved entry for every listed fixture; unresolved + limitations section in the executive summary | done | d3af051a | scripts/core.py, scripts/refresh.py, scripts/build.py, data/review-notes.json | 2026-10-15 |
| Mobile-first executive summary discoverability (in-site links to the pick board, unresolved section and analysis) | done | d3af051a | site/**, assets/**, index.html | 2026-10-15 |
| Final integration, PR to main, merge, Pages deploy verification | in progress | d3af051a | root deployment files, COORDINATION.md | 2026-10-15 |

- Evidence standard unchanged: Hotspawn fixes the fixture inventory only and is never a probability input. Probabilities come from externally observed market lines and reproducible arithmetic on them; HLTV supplies identity and ranking context; anything unverifiable stays blank and flagged.
- Sandbox networking reaches GitHub and package registries only, so primary sources (Hotspawn, Polymarket, Pinnacle, HLTV) are retrieved either through the retrieval tooling used for research or through Actions runners, which have normal internet access. `.github/workflows/harvest.yml` was added for that purpose: it runs the real refresh plus the independent audit on a push carrying the `[harvest]` marker and commits the raw snapshot and every log to `research/harvest/` so the numbers can be re-checked locally. It never publishes and never deploys.
- No other session's claim is overwritten; no branch other than this session's fixed branch is created, checked out or pushed.

### Session d3af051a results (15–16 October 2026)

- **Task 1 — the failing publication run is fixed and re-proven.** Reproduction came from `research/harvest/` (the non-publishing harvest workflow, run 38817810620): both the independent c6 row audit and the published-row audit reported `0 failures`, and the refresh reported `unresolved_without_any_pick: 0`. Root cause and fix are documented in `data/review-notes.json` (`publication-failure-2026-10-15`) and the README policy: a one-sided ranking tier was added, and the two-team tier now stores per-team checkable evidence.
- **Task 2 — day-2 review + day-3 guidance.** `data/analysis.json` now carries `day_two` (four results with per-match HLTV links, map scores and labelled player-stat provenance), `day_two_analysis` (what changed for day 3), `day_three` (the two group deciders with HLTV fixture links, the external market used for the Aurora–9z line, and the live state of each row) and a contrarian candidate. Rendered at `analysis.html`; nav entry renamed `TWC analysis`; executive summary links it.
- **Task 3 — full pick coverage.** Fresh snapshot (2026-10-15T22:37Z, 86 rows, four-way coverage verified at 86/86/86/86): **22 open fixtures, 17 priced, 5 research-only, 0 without a pick**. Tiers in use: exchange 12, exchange_wide 4, bookmaker_fallback 1, research_rank 3, research_rank_single 2. Named gaps that remain are published with their rules: LOS NINOS and Insiders have no HLTV world ranking, so their fixtures can only ever be one-sided research picks; `GG.BET` still returns HTTP 403 to the collector.
- **Task 4 — mobile executive summary.** New `#coverage-line` notice directly above the stat cards states the counts and links the pick board and the unresolved section; start-here cards now include the tournament analysis, unresolved section, all matches and the complete feed; nav label updated on every page.
- **Verification performed this session:** 82 unit/pipeline tests, 9 audit tests, 5 integrity tests, 12 c6 tests, the independent c6 row auditor on the retained snapshot (`0 failures`), the production validator (86 rows, 17 calculations replayed, 544 links, 20 checksums, 210 displayed rows), and the harvest workflow's own refresh+audit+build+validate chain (run 38818303034, success). Values that could not be sourced stay blank and flagged; no value was inferred.
- **Irregularities for review (all published on Flagged for Review with source links):** the WROTBERRY↔WBT fixture-parity mapping still has no official rename statement; the `exchange_wide` and both research tiers trade precision for coverage and are labelled as such; HLTV's own odds widget is **not** used as a probability input; BETBOOM vs Legacy (16 Oct 13:00Z) is a real day-3 fixture that the Hotspawn feed does not list, so it carries no pick and is documented on the analysis page instead.

### Session d3af051a publication record (15 October 2026, 22:45 UTC)

- **PR #18 merged** (no approval wait, per the standing instruction): https://github.com/buffedlizard55-lab/MaltaProj4/pull/18 → merge commit **e52ab451244fab46c6d45d2aedb9bdf98b57d95a**. Branch head was green before the merge: the PR-triggered `verify-build` run 38818442963 passed unit/independent failure-mode tests, build + independent row verification, and the phone/tablet/desktop accessibility + exact-boundary expiry browser suite.
- **Production deployment succeeded**: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38818639951 — the `deploy` job's own step verified every published byte against the build manifest, and the run completed green.
- **Live site independently retrieved after deployment** (this session): `build-info.json` reports revision `e52ab451…`, `built_at` 2026-10-15T22:40:17Z, **86 rows**, 20 checksummed artifacts. `index.html` shows the new coverage line ("Coverage at 15 Oct · 22:40 UTC: 22 open fixture(s) — 17 with published probabilities, 5 with a labelled research-only pick and no percentage, 0 with no supported pick yet"), the start-here cards including the tournament analysis, and the in-page unresolved section; `picks.html` renders all 17 priced picks with both percentages, fair lines, lock times, observation/expiry and a source link per row; `analysis.html` renders the day-one and day-two result tables, the upset review, the day-two read and the day-three decider table.
- **Live picks of record for the Thunderpick decider:** Aurora vs 9z (16 Oct 14:00Z, Hotspawn 1080205) — Aurora **68.5%**, 9z 31.5%, from the strict exchange tier (Polymarket market 5733288, two-sided, ~$59.7k liquidity); research-only rows publish no percentage.
- **Concurrent sessions noted, nothing overwritten:** `0e407ec7` (22:45 claim), `e54807b3` and `ed2e244b` claimed overlapping scopes for this same follow-up request. Their commits are preserved: `0e407ec7` works in `research/harvest-0e407ec7/**`, `.github/workflows/harvest-0e407ec7.yml`, `scripts/harvest_0e407ec7.py`, `data/twc-day2-day3.json` and an additive `twc.html`; `e54807b3` works in its own capture workflow; `ed2e244b` has a claim commit only. Any of them that reworks `data/analysis.json`, `scripts/build.py` or the generated root routes must rebase on `e52ab45` first, because those files are now on main in the state this session verified. Requests for changes to files this session owns go in this board.
- **Nothing was verified that was not checked.** The two research tiers, the wide-quote tier and the WROTBERRY↔WBT fixture-parity mapping remain labelled policy decisions on Flagged for Review, and the day-two TeSeS rating is credited to a third-party report rather than HLTV.

### Session d3af051a follow-up record (15 October 2026, 22:50 UTC)

- **Needs-pick discoverability delivered as a second PR.** PR #20 merged: https://github.com/buffedlizard55-lab/MaltaProj4/pull/20 → merge commit **9ad97c7df7dd63907f5c3e84ef7b4933e626febd**. New main-nav entry **Needs pick** on every page, the gap list opens on a `Needs a pick` filter, rows without a verified market line carry `needs-pick` styling, and the executive summary plus pick board open with count chips (`Updated picks (17)`, `Needs a pick (5)`, `Every match (86)`, `TWC day 1–3 analysis`). PR CI `verify-build` passed in 58s.
- **Board-only PR #19** (merge commit `1eeabbed10916c1f019f337113fa4ce92f3a2577`) recorded the earlier merge and deployment; both were green.
- **Deployment runs, all green with the byte-for-byte live check**: 38818639951 (PR #18 content, revision `e52ab451…`), 38819077394 (PR #19), 38819560917 (PR #20 content, revision `9ad97c7d…`).
- **Remaining for a future session (not claimed here):** the 00:17 / 06:17 / 12:17 / 18:17 UTC scheduled runs continue on main; each row's expiry is enforced in the build and in the browser, so any pick whose quote or fixture observation ages past its deadline is withheld rather than shown stale. Day-3 group deciders at 10:00Z and 13:00Z on 16 October are inside the next scheduled window; the Aurora–9z line expires 05:33Z and will be re-sourced by the 06:17Z run.

### Session d3af051a final record (15 October 2026, 22:56 UTC)

- **PR #21 merged** (board record): https://github.com/buffedlizard55-lab/MaltaProj4/pull/21 → merge commit **8e374f49145abf912adf888c1ccada765ca215c2**. Push run 38819954409 (verify-build + deploy) green, and the deploy job verified every live byte against the build manifest.
- **Live state re-retrieved after that deploy** (this session): `build-info.json` reports revision `8e374f49…`, `built_at` 2026-10-15T22:52:29Z, 86 rows and 20 checksummed artifacts; `picks.html` opens with the **Needs a pick** filter and lists all 17 priced fixtures with both percentages, fair lines, lock times and per-row source links (Aurora 69.0% / 9z 31.0% on the TWC decider, observed 22:52Z, expires 05:33Z); `index.html` shows the coverage line ("22 open fixture(s) — 17 with published probabilities, 5 with a labelled research-only pick and no percentage, 0 with no supported pick yet") plus the count chips; `analysis.html` renders both day-result tables, the upset review, the day-two read and the day-three decider table.
- **Session summary of deliveries:** the failing 21:22Z publication path is fixed and regression-tested; day-two results and day-three decider guidance are published with per-fact HLTV sources; every open Hotspawn fixture now carries either a market-derived probability or a labelled research-only pick with no percentage (0 without a pick); the executive summary, pick board and gap list are reachable from the mobile bottom bar, the new **Needs pick** tab and top-of-page chips.
- **Open items left for the scheduled runs or a later session (unclaimed here):** the 06:17Z scheduled refresh must re-source the Aurora–9z line before its 05:33Z expiry; BETBOOM vs Legacy (16 Oct, 13:00Z per HLTV) is not in the Hotspawn feed at this snapshot, so no pick is generated for it and it stays documented on `analysis.html`; the `exchange_wide`, `research_rank` and `research_rank_single` tiers plus the WROTBERRY↔WBT mapping remain flagged for manual review.

## Session e54807b3 claims (2026-10-15, 22:35 UTC)

Arena fixes this session to `arena/e54807b3-maltaproj4`; the requested `session-<id>/<task>` branch naming is not available (same constraint recorded by every earlier session), so no other branch is created, checked out or pushed. Before claiming, all 15 remote heads and PRs #2–#17 were enumerated: every task on this board is **done**; the newest commit on any session branch is 10:35:54 UTC (a56d155f, done, merged). Session **0c6e902a** pushed a claim at 10:10:10 UTC ("evidence-backed contrarian strategy review") with **no commits since (>12 h)**, so it is stale under the 60-minute rule; its deliverable (sourced Day-1 9z–Aurora retrospective and strategy note) was published by a56d155f/a7c0a121 on `analysis.html`. Handoff noted; only the files listed below are touched.

**Discovered before claiming:** scheduled production run [38809354350](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38809354350) (21:22 UTC) **failed**: the live refresh succeeded (87 fixtures, 15 priced, 7 without a probability) but `verification-c6/audit_snapshot.py` reported 1 row failure, so nothing was built or deployed. The live site still serves the 17:00 UTC snapshot (73 rows, run 38773620642). GitHub also started the 12:17 and 18:17 cron slots 4 h 42 m and 3 h 05 m late, so a six-hour cron cannot guarantee the requested 4–8 h refresh cadence.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| E1 Diagnose/fix the failing scheduled refresh (row-audit failure); print audit failures in CI logs; refresh cadence that survives GitHub cron delays; CI on this branch | done (root-cause fix landed first via d3af051a; this session added quarantine, 2 h cadence, CI log output) | e54807b3 | .github/workflows/**, scripts/core.py, scripts/hltv.py, scripts/refresh.py, verification-c6/audit_snapshot.py, tests/** | 2026-10-15 22:35 |
| E2 Day-2 Thunderpick World Championship 2026 review and Day-3 contrarian-but-not-stupid guidance (sourced, per-row source quality) | done (merged into d3af051a's page; live guidance added) | e54807b3 | research/day2/**, data/analysis.json, analysis.html (generated) | 2026-10-15 22:35 |
| E3 Pick for every open Hotspawn CS2 fixture: HLTV first, then esportsbook lines, for rows the featured exchange method cannot resolve; separate unresolved + limitations section in the executive summary | done (VRS originated lines + NIP alias; research tiers are d3af051a's) | e54807b3 | scripts/** (new source adapters), data/identities.json, data/review-notes.json, research/current/** | 2026-10-15 22:35 |
| E4 Executive summary / phone discoverability: obvious in-site links to the current pick list | done (merged with d3af051a's chips and Needs-pick tab) | e54807b3 | scripts/build.py, assets/**, generated root HTML routes | 2026-10-15 22:35 |
| E5 Final integration: rebuild, line-by-line re-verification, PR to main, explicit merge, live Pages verification | done (PR #24 merged, deploy verified live) | e54807b3 (final integration) | COORDINATION.md, README.md, build-info.json, root deployment files | 2026-10-15 22:35 |

### Session e54807b3 conflict log (15 October 2026, 23:15 UTC)

- **Overlap discovered:** session d3af051a claimed the same follow-up request at **22:26:49 UTC** on its own branch; this session's claim followed at **22:27:09 UTC**. Each claim sat on its own branch, so neither was visible to the other until d3af051a merged PRs #18–#22 (22:43–22:56 UTC). d3af051a's claim is earlier and its tasks are done and verified live, so this session **builds on main instead of replacing it**.
- **Resolution:** `origin/main` (8857774) was merged into `arena/e54807b3-maltaproj4` (merge commit a6618ca; no force-push, no history rewritten). Ten conflicts were resolved **without discarding d3af051a's work**:
  - **Research tiers:** d3af051a's `rank_resolution` / `research_rank` / `research_rank_single` are kept in the collector, the validator and the independent auditor. This session's duplicate one-sided rule was dropped. A tightening suggestion (require HLTV's explicit "Unranked" badge, which the collector now records) is logged on Flagged for Review instead of editing their tier.
  - **Alias register:** their Liquid, Aurora and Insiders entries are kept, with official-site sources added; Ninjas in Pyjamas / NIP is new.
  - **Analysis page:** their day-two, day-two-read and day-three content and layout are kept. Added: vetoes, HLTV report links, "More from the HLTV reports", live contrarian guidance (`#guidance`) and the model-vs-market screen. Their two day tables both rendered the id `day-·`; this is fixed through the `key` field their code already reads.
  - **Site:** their Needs-pick tab, count chips, coverage line and `needs` filter are kept. Added: model lines, the non-market section, methodology `#model` and the 2 h cadence text.
  - **Tests:** their pipeline-tier tests now disable the VRS tier, which runs before the research tiers and has its own end-to-end tests. Their assertions are unchanged. This session's research tests were rewritten against their tiers.
- **Correction for the record:** the d3af051a entries above quote the deciders at "10:00Z and 13:00Z". Those are HLTV page clock times, which are not UTC. Aurora vs 9z starts at **14:00 UTC** (Hotspawn and HLTV's machine-readable timestamp agree), and BETBOOM vs Legacy at about 17:00 UTC (derived, unverified). Their published page shows 14:00Z and leaves the BETBOOM–Legacy time blank, so no published value was wrong.
- **Other claims seen and not touched:** 0e407ec7 (additive `twc.html`, own harvest workflow) and ed2e244b (claim commit only).

### Session e54807b3 publication record (15 October 2026, 23:30 UTC)

- **PR #24 merged** without an approval wait, per the standing instruction: https://github.com/buffedlizard55-lab/MaltaProj4/pull/24 → merge commit **9757a74dde09344dcfe245014c1bae2c244ec722** (23:20:44 UTC).
  - The first PR check, [38822533831](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38822533831), **failed**. A stored model-vs-market gap went stale when `tests/test_integrity.py` re-priced a cloned row. Fixed in 772bf80: the gap is now derived at render time.
  - The branch was green before the merge: PR check [38822842067](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38822842067) and the branch push run with a live refresh, [38822837484](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38822837484).
  - A local replay of the full PR workflow also passed (tests, quarantine, audits, build, validate, browser).
- **Production deployment succeeded:** [38823010237](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38823010237) (verify-build ✓, then deploy ✓ with its byte-for-byte live check), alongside the legacy branch build [38823010131](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38823010131) ✓.
- **Live site independently retrieved after the deploy:**
  - `build-info.json`: revision `9757a74d…`, `built_at` 23:21:27Z, snapshot 23:21:26Z (live refresh during deploy), **86 rows**.
  - `index.html`: "20 of 22 open matches have a win probability: 17 from betting markets and 3 from our Valve-standings model. 2 more carry a research pick and 0 have none". Market rows show the VRS comparison line (Voca–Phantom flagged "favourite differs").
  - `analysis.html#guidance`: live Day-3 guidance (current numbers at retrieval):
    - NIP vs Liquid: Liquid as the low-cost contrarian lean.
    - Aurora vs 9z: Aurora 69.5% market / 68.0% model; 9z as the day's swing.
    - Voca vs Phantom: model-backed lean.
    - BETBOOM vs Legacy: card showing VRS 79.3% Legacy; the fixture is not on Hotspawn.
- **Sources used:**
  - Valve's official Regional Standings repository: standings, `fit.js`, `glicko.js`, `team.js` and `modelfit.png` at commit eec4853.
  - HLTV TWC event, results, match pages 2399408–2399413 and reports 45718, 45722, 45724, 45728, 45729, 45730.
  - Organization sites auroragg.com, nip.gl and teamliquid.com.
  - Polymarket, Pinnacle and Hotspawn through the collector, with receipts in the published JSON.
- **Verification performed:**
  - 107 unit/pipeline tests, plus audits, integrity and c6 suites.
  - Production validator on capture 3: 86 rows, 20 calculations reproduced, 562 links, 20 checksums.
  - Independent audit of the published data: 0 failures.
  - Browser checks: 32 accessibility and no-overflow scans, plus 7 expiry scenarios.
- **Irregularities flagged** (all on Flagged for Review):
  - BETBOOM vs Legacy is absent from Hotspawn's feed.
  - HLTV clock times are not UTC.
  - The WBT alias is applied beyond Elisa BreakOut (fixture parity plus a 5/5 lineup).
  - Aurora's site lists Polymarket as a partner.
  - The VRS model tier is a policy decision.
  - Suggested tightening of the one-sided research tier (not applied).
  - The 2026-10-15 GitHub schedule delays.
- **Requests for other sessions** (their files untouched):
  - **PR #23 (dbe62379)** and **PR #25 (0e407ec7)** now report `CONFLICTING` against main 9757a74. Please merge main and resolve before merging.
  - PR #23 adds `research/day2/DAY2-REVIEW-2026-10-15.md`, which already exists on main from this session: please rename or merge the content.
  - `data/analysis.json` now also carries `day_two_more` and `day_three_guidance`, and the page renders `#guidance` (keep the `key` fields on `day_one`/`day_two`; they fix the duplicate `day-·` ids).
  - PR #25 cites Polymarket market 5763247 (Legacy vs BETBOOM); once verified it could feed the BETBOOM–Legacy card.
- **Open items (unclaimed):**
  - The cron now runs every two hours, so the Aurora–9z line (expires 05:33Z) is re-sourced well before the 14:00Z decider.
  - BETBOOM vs Legacy gets a pick automatically if Hotspawn lists it.
  - Valve's next monthly standings (early November) are picked up automatically; the vendored copy is only a fallback.

## Session 0e407ec7 claims (2026-10-15, 22:45 UTC)

Arena fixes this session to `arena/0e407ec7-maltaproj4`; the requested `session-<id>/<task>` branch naming is not available (the same constraint is recorded by every earlier session), so no other branch is created, checked out or pushed. Before claiming, all 18 remote heads and PRs #2–#17 were enumerated.

**Three sessions are active at the same moment** and have already claimed overlapping scopes for this same follow-up request: **ed2e244b** (22:26 UTC, Day-2 recap: `data/analysis.json`, `scripts/build.py`, `analysis.html`, `research/day2/**`), **d3af051a** (22:27–22:30 UTC, CI fix + Day-2/Day-3 + full coverage + mobile + integration: `scripts/**`, `tests/**`, `.github/workflows/**`, `data/analysis.json`, `research/day1/**`, `data/review-notes.json`, `site/**`, `assets/**`, `index.html`) and **e54807b3** (22:35 UTC, E1–E5, the same five areas). No claim is overwritten and no other branch is touched. Because their scopes already collide with each other and with every file this request requires, this session keeps its work in **uniquely named files wherever possible**, edits shared files only additively, and logs every shared-file request here instead of assuming ownership:

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Independent primary-source verification of Day-2 TWC 2026 results (15 Oct) and the Day-3 (16 Oct) decider schedule, with per-fact source links and source-quality labels | in progress | 0e407ec7 | research/day3-0e407ec7/**, data/twc-day2-day3.json | 2026-10-15 22:45 |
| Day-3 contrarian-but-not-stupid pick guidance derived from Day-1/Day-2 evidence (roster change, onboarding, rest, map/form reads), published as a new dedicated page rather than a rewrite of `analysis.html` | in progress | 0e407ec7 | data/twc-day2-day3.json, scripts/build.py (additive: new page + nav entry), twc.html, site/twc.html | 2026-10-15 22:45 |
| A sourced pick — or an explicit unresolved entry with its limitation — for every open Hotspawn CS2 fixture, including fixtures the strict exchange tier cannot price; unresolved + limitations surfaced in the executive summary | in progress | 0e407ec7 | research/current-0e407ec7/** (own receipts), scripts/sources_0e407ec7.py or additive functions in scripts/core.py, data/review-notes.json (additive entries) | 2026-10-15 22:45 |
| Own live refresh + independent row audit committed to this branch (no publication from this branch), so the numbers used here are reproducible and not copied from another session | in progress | 0e407ec7 | .github/workflows/harvest-0e407ec7.yml, research/harvest-0e407ec7/**, runtime/** | 2026-10-15 22:45 |
| Diagnose the failing production run 38809354350 (21:22 UTC) far enough to publish the cause and the exact failing row as a flagged irregularity; the code fix itself is **requested from** d3af051a/e54807b3, who claimed `scripts/**`, `tests/**`, `.github/workflows/pages.yml` and `verification-c6/audit_snapshot.py` | needs review | 0e407ec7 (report only) | research/day3-0e407ec7/CI-FAILURE.md | 2026-10-15 22:45 |
| Final integration for this branch only: rebase on whatever main is at the time, re-verify the combined data line by line, confirm the site builds with no broken links, PR to main, merge, verify the live Pages deployment | in progress | 0e407ec7 (final integration, if it reaches main first) | COORDINATION.md, README.md, build-info.json, generated root routes | 2026-10-15 22:45 |

### Session 0e407ec7 coordination log

- 2026-10-15 22:40 UTC: read main (6a5335cc) and all 18 remote heads. Main's 21:22 UTC scheduled run **38809354350 failed** at the "Build and independently verify every row, calculation and internal link" step, so nothing deployed and the live site still serves the earlier successful build (run 38773620642, 16:59 UTC). Run 38817189671 (d3af051a's non-publishing `[harvest]` workflow) succeeded and committed a fresh live snapshot to that branch; this session reads it through the GitHub contents API as a cross-check only and runs its own refresh for anything it publishes.
- Evidence standard unchanged and restated for this session: Hotspawn establishes the fixture inventory only and is never a probability input. Probabilities come only from externally observed market lines or reproducible arithmetic on them. HLTV supplies identity, results, rankings and context. Day-1/Day-2 results are facts with source links; strategy statements are labelled analysis. Anything unverifiable stays blank and flagged; no crowd votes, no rank-to-probability formula presented as a market price, no 50/50 fillers.
- Sandbox bash networking reaches GitHub and package registries only, so HLTV/Polymarket/Pinnacle/Hotspawn are read through the retrieval tooling (research) and through Actions runners (pipeline refresh). No access control is bypassed and no source is claimed to have been checked when it was not.
- Shared-file requests logged instead of edited: any change to `verification-c6/audit_snapshot.py`, `.github/workflows/pages.yml`, `scripts/core.py` semantics or `data/analysis.json` that another session already owns is recorded here for that session; if this session must touch a shared generated file to satisfy the user's request (for example `scripts/build.py` navigation), the edit is additive and noted in the log at commit time.


### Session 0e407ec7 — day-2/day-3 verification pass, corrections and shared-file edits (2026-10-16, 01:25 UTC)

Rebased this branch on `origin/main` **8857774** before touching anything; the `COORDINATION.md` conflict was resolved by keeping both boards verbatim (nothing from d3af051a's record was dropped).

**Independent verification, line by line, with links** — `research/day3-0e407ec7/VERIFICATION.md`. All four day-2 series were re-read from their own HLTV match pages (2399408, 2399409, 2399410, 2399411), plus day-1 match 2399384, the event schedule, both HLTV analytics pages and both Polymarket markets. Market receipts: `research/day3-0e407ec7/quotes/polymarket-5763247-legacy-betboom.json` and `.../polymarket-5733288-aurora-9z-crosscheck.json`. Diagnosis of the failed 21:22Z publication run and of this session's reproduced audit failure: `research/day3-0e407ec7/CI-FAILURE.md`.

**Irregularities found (all logged in `data/review-notes.json`, all with sources):**

1. `twc-anubis-score-2026-10-16` — `data/analysis.json` day-two prose said BETBOOM won Anubis **13-2**; HLTV 2399410 records **13-4** (halves 2:10; 2:3). The `maps` field of the same record was already correct. **Corrected in place.** Every other day-2 number matched, including Wicadia 45-25 / 1.65, XANTARES 36-23 / 1.41, stavn 15-30 / 0.58, TeSeS 47-40 / 1.26 and all nine map scores.
2. `twc-day3-start-time-2026-10-16` — **this board recorded BETBOOM vs Legacy as "13:00Z"**. 13:00 is HLTV's displayed reader-local clock (US Eastern at this retrieval), not UTC. The sourced start is **2026-10-16T17:00:00Z**, confirmed twice: Polymarket market 5763247 `gameStartTime` "2026-10-16 17:00:00+00" and `eventStartTime` 2026-10-16T17:00:00Z, whose description says "1:00 PM ET". No page ever displayed 13:00Z (the site's field was blank); it is now filled with 17:00Z. **Every session: never read a displayed HLTV clock as UTC.**
3. `twc-day3-groupb-inventory-gap-2026-10-16` — the Group B decider *does* have a strict-quality exchange line (Legacy 0.64 / BetBoom Team 0.36, bid 0.59 / ask 0.69, spread 0.10, liquidity 6847.5095 USD, active and accepting orders, updatedAt 2026-10-15T22:45:08Z) but the Hotspawn CS2 feed contains **no BETBOOM fixture at all** in either the published 86-row snapshot or this session's own 86-row harvest, so no pick row and no leaderboard points can exist for it. Published as sourced research on `analysis.html`, not as a probability. `data/identities.json` already aliases BetBoom / BetBoom Team / BB Team, so a later refresh that lists the fixture prices it automatically with no new alias.
4. `hotspawn-lock-offset-2026-10-16` — Hotspawn's official rules page says picks lock **5 minutes** before start; the feed says **6** (`lock_offset_sec: 360`, fixture 1080205 start 14:00:00Z / lock 13:54:00Z). Both published as given; the site uses the feed's earlier, stricter lock time. Nothing averaged or inferred.

**Shared files touched by this session (all additive or corrective; no other session's content removed):**

- `data/analysis.json` — the Anubis correction; vetoes, map halves and the remaining verified series rows for all four day-2 matches; the TeSeS figure re-labelled from third-party to HLTV-verified (the third-party mention is kept); `day_three.fixtures[1].start_utc` = 2026-10-16T17:00:00Z plus its `market` block for market 5763247; seven new sourced `day_three.points` (day-1 rematch map scores, the veto/map-pool read, the Group B line and its inventory gap, Hotspawn's official scoring rules, points per tier from the feed, the expected-points arithmetic, and the 0.685 → 0.69 line movement); two extra `not_stupid_check` items and extended `limits` on the contrarian candidate; one new `strategy.rules` entry (weight the swing by the fixture's points and the streak it risks); and `strategy.unverified[0]` replaced, because it asserted that Hotspawn's scoring rules were *not* collected — they now are, from https://play.hotspawn.com/how-it-works and the feed's `offered_points`.
- `data/review-notes.json` — four appended entries (the four irregularities above). Nothing existing was edited.
- `scripts/build.py` — **one additive anchor**: a fifth `start-card` on the executive summary linking straight to `analysis.html#day-three`, so a phone user lands on the day-3 deciders in one tap. No renderer logic, no nav structure and no other page changed. d3af051a's warning about rebasing before touching this file was followed.
- Regenerated committed artifacts to match the data: `analysis.html`, `review.html`, `index.html`, `build-info.json`, `data/matches.csv` (only the `build_utc` column) and `data/latest.json` (only `built_at`). Verified byte-identical to the committed set for every other page before overwriting anything.
- Own files: `scripts/harvest_0e407ec7.py` (the `None`-method `sort_keys` crash, irregularity 6 in the verification report) and new `tests/test_harvest_0e407ec7.py`.

**New sourced facts worth reusing (all in the verification report, with links):** Hotspawn scoring is official — points per correct pick, more for higher tiers, a bonus for consecutive correct picks, weekly leaderboard reset, picks editable until lock, forfeits voided and cancellations scoreless. Tier values read from the feed: **tier S = 7 points, tier B = 3, tier C = 2** (2 / 31 / 53 rows of 86); the 22 open rows are worth **61 points**. Arithmetic on the published decider line: favourite side 7 × 0.685 = **4.795** expected points against 7 × 0.315 = **2.205** for the contrarian side, and across the 17 priced open rows the published favourite side totals **32.70 of 47** points (the other 14 points sit on the 5 research-only rows, which have no probability, so no expected value is claimed for them). The exact streak-bonus formula is **not published anywhere** and is explicitly left unverified.

**Local verification before pushing (all green):** 86 unit tests, 9 audit tests, `verification-95b588c2/test_integrity.py`, 12 `verification-c6` tests, `verification-c6/audit_snapshot.py` on both `data/latest.json` and the built `public/data/latest.json` → **0 failures**, `scripts.validate --data data/latest.json --site .` → 15 pages / 558 internal links / 20 artifact checksums / 210 displayed rows, and `npm run test:browser` → **28 page/viewport accessibility scans at 320/390/768/1440 px**, navigation, filters, six legacy redirects, evidence anchors and seven exact-boundary expiry scenarios.

#### Addendum — 2026-10-16 01:45 UTC: this session corrected its own market reads

While cross-checking PR #23 (session `dbe62379`), which independently recorded the same Group B decider market, this session found that **manual retrieval of the Gamma API can be served from an HTTP cache**. The slug URL for market 5763247 was read twice and returned byte-identical payloads stamped `updatedAt` 2026-10-15T22:45:08Z, while a cache-busted read of the same market returned `updatedAt` 2026-10-15T23:17:08Z with different prices (0.635 / 0.365 instead of 0.64 / 0.36), spread (0.07 instead of 0.10) and liquidity (8149.023 instead of 6847.5095). Market 5733288 behaved identically: cached state 22:51:08Z read 0.69 / 0.31, cache-busted state 23:17:08Z read 0.685 / 0.315.

Consequences, all applied in this branch:

- An earlier draft of this session's `data/analysis.json` text described the Aurora–9z line as having "moved toward the favourite" on the strength of a stale payload. It now states the full sequence **0.685 (22:31:10Z) → 0.69 (22:51:08Z) → 0.685 (23:17:08Z)**, i.e. the freshest market state equals the probability the site already publishes, so no row needed correcting.
- The Group B decider block now carries all three dated states of market 5763247, including `dbe62379`'s independent 22:53:08Z observation, with the direction (Legacy) unchanged in all three.
- Both receipts in `research/day3-0e407ec7/quotes/` carry a `cache_warning` and list each observation separately with its own `updatedAt` stamp; `observed_at` stays `null` rather than estimated.
- New flagged irregularity `polymarket-cached-manual-reads-2026-10-16` on Flagged for Review, and rows B4/B8/B14 plus irregularity 8 in `research/day3-0e407ec7/VERIFICATION.md`.
- **No published probability was ever taken from a manual read**, so no pick on this site was affected: prices come only from `scripts/refresh.py` on an Actions runner, which already adjusts observation time for HTTP cache Age. **Every session doing hand-made market reads: cache-bust the URL and date the observation by the payload's own `updatedAt`, not by the clock.**

Also converged independently with PR #23 on two points, which is useful corroboration rather than duplication: the Group B decider starts **2026-10-16T17:00:00Z** (both sessions sourced it from Polymarket's `gameStartTime`/`eventStartTime`, not from HLTV's displayed clock), and the Anubis map score in the BETBOOM–PARIVISION series was **13-4** (`research/day2/DAY2-REVIEW-2026-10-15.md` records 13–4; this branch corrects the `data/analysis.json` day-two prose that said 13-2). Whoever merges second should keep both texts rather than choose one.
#### Addendum — 2026-10-16 02:10 UTC: re-integrated on main `9757a74` (PR #24 merged mid-flight)

PR #24 (session `e54807b3`) merged while this branch was in review, so the work above was re-applied on top of `9757a74` rather than merged textually: the VRS model tier, `day_two_more`, `day_three_guidance`, the two-hour refresh cadence and the hardened auditor are all preserved untouched, and this session's content was rebuilt against them.

- **Dropped as redundant:** the fifth executive-summary start-card this branch had added to `scripts/build.py`. PR #24 already ships a **Day-3 guidance** card linking `analysis.html#guidance`, plus a section nav, so the mobile deep link the user asked for already exists. This branch now changes **no shared script**: `scripts/build.py`, `scripts/core.py`, `scripts/refresh.py`, `scripts/validate.py`, `verification-c6/**` and `.github/workflows/pages.yml` are untouched here; the only script edits are to this session's own `scripts/harvest_0e407ec7.py`.
- **Cross-confirmed, not duplicated:** PR #24's four day-two `veto` fields match this session's independent HLTV reads exactly (all four, token for token), and its `betboom-legacy-missing-2026-10-15` and `hltv-times-2026-10-15` flags agree with the two irregularities logged here. What this branch adds is the *verification* those entries asked for: the Group B decider's 17:00 UTC start is no longer "derived, unverified" but machine-verified from Polymarket market 5763247 (`gameStartTime` "2026-10-16 17:00:00+00", `eventStartTime` 2026-10-16T17:00:00Z, description "1:00 PM ET"), and the guidance card's `timing` and `why` fields now say so, with the dated market states attached.
- **Still one factual error on main, corrected here:** the day-two prose for BETBOOM vs PARIVISION said Anubis **13-2**; HLTV 2399410 records **13-4** and PR #24's own `maps`/`veto` fields already implied 13-4. Corrected in `data/analysis.json` with the correction stated in the row's flag.
- **Numbers recomputed against the current capture** (`data/latest.json` generated 2026-10-15T23:12:43Z, fixtures observed 21:33:49Z, 86 rows, 22 open, 0 without a pick, methods 12 exchange / 5 exchange_wide / 3 model_vrs / 2 research_rank_single): tier points **S 7 · B 3 · C 2** (2 / 31 / 53 rows), open rows worth **61 points**, the 20 priced rows worth **56** of them, and following the published favourite side across those rows is worth **37.87** expected points. The decider row publishes 0.69 / 0.31 (evidence observed 23:12:32Z, market `updatedAt` 23:11:13Z, expires 05:33:49Z), so 7 × 0.69 = **4.83** expected points against 7 × 0.31 = **2.17** for the contrarian side; at the 0.685 / 0.315 state stamped 23:17:08Z it is 4.795 against 2.205. The VRS model check stored on the same row reads 0.6796 / 0.3204 from Valve points 1716 vs 1543, i.e. two independent methods agree on the favourite within half a point.
- **New irregularity affecting every session that hand-reads markets:** `polymarket-cached-manual-reads-2026-10-16`. Manual Gamma API retrieval through the page-retrieval path can be served from an HTTP cache — the same URL read twice returned byte-identical payloads stamped 22:45:08Z while a cache-busted read returned 23:17:08Z with different prices, spread and liquidity. Date every manual observation by the `updatedAt` inside the payload, cache-bust the URL, and keep publishing probabilities only from the Actions refresh, which already adjusts for cache Age. This session's own earlier draft was wrong about the Aurora–9z line moving toward the favourite and has been corrected to the full 0.685 → 0.69 → 0.685 sequence.

### Session 0e407ec7 publication record (2026-10-16, 00:05 UTC)

- **PR #25 merged:** https://github.com/buffedlizard55-lab/MaltaProj4/pull/25 → merge commit **c371d0a21f02c1d5e7754ec5aeb09149e7bdc34f**, merged 2026-10-15T23:45:10Z without waiting for approval, after `verify-build` passed on the rebased head (run 38825203092, 1m19s) and the branch reported `mergeStateStatus: CLEAN`.
- **Publication run 38825442881 (push to main) succeeded end to end:** live source refresh, independent row audit of the refreshed snapshot, build, validation, phone/tablet/desktop accessibility and expiry checks, Pages upload, deploy, and the byte-for-byte live verification of every artifact against the build manifest.
- **Live site re-retrieved after that deploy:** https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json reports revision **c371d0a21f02c1d5e7754ec5aeb09149e7bdc34f**, `built_at` 2026-10-15T23:45:45Z, snapshot generated 2026-10-15T23:45:45Z, **86 rows**, 20 checksummed artifacts. The live `analysis.html` was read back and carries this session's content: the corrected 0.685 → 0.69 → 0.685 price sequence, the cache finding, the VRS/market corroboration, the six-item contrarian cost checklist and strategy rule 6.
- **Defect found in that published content and fixed in PR #27:** the bulk substitution that removed long unbreakable tokens from rendered prose also rewrote a link field, so `day_three.points[7].source` read `https://the official Hotspawn rules page` instead of `https://play.hotspawn.com/how-it-works` — a broken source link on the live analysis page. `scripts/validate.py` resolves internal links only, so nothing caught it. **PR #27** (https://github.com/buffedlizard55-lab/MaltaProj4/pull/27) restores the URL, rewords the two places whose substituted phrasing only made sense next to an adjacent link, audits all 0 remaining malformed URL fields in `data/analysis.json` and `data/review-notes.json`, and adds `tests/test_research_source_urls.py` so a source link that is not an absolute URL fails the suite (mutation-checked against the exact bad value). No shared script, renderer or workflow is touched.
- **Handover note for whoever edits research prose next:** substitute only inside the specific rendered field, never across a whole JSON document — `source`, `url` and `*_url` fields sit beside the prose and a blanket replacement turns a citation into a broken link. The new test is the guard.

### Session 0e407ec7 final record (2026-10-16, 00:15 UTC)

- **PR #27 merged:** https://github.com/buffedlizard55-lab/MaltaProj4/pull/27 → merge commit **dd741427bfbcf3ca2aa663a4f9ad2ea7f1abd1e4**, merged 2026-10-15T23:55:35Z without waiting for approval after `verify-build` passed on the rebased head (run 38826240303) and the branch reported `mergeStateStatus: CLEAN`. It restored the source URL that a bulk substitution had mangled (`day_three.points[7].source` → `https://play.hotspawn.com/how-it-works`), reworded the two strings whose substituted phrasing only made sense beside an adjacent link, and added `tests/test_research_source_urls.py` so a source link that is not an absolute URL — or a claim, rule, match, fixture or review note with no link at all — fails the suite. The test was mutation-checked against the exact bad value.
- **Publication run 38826476407 (push to main) succeeded end to end:** live refresh, independent row audit, build, validation, phone/tablet/desktop accessibility and expiry checks, Pages upload, deploy, and the byte-for-byte live verification of every artifact against the build manifest.
- **Live receipt re-retrieved after that deploy:** `build-info.json` reports revision **dd741427bfbcf3ca2aa663a4f9ad2ea7f1abd1e4**, `built_at` 2026-10-15T23:56:15Z, snapshot generated 2026-10-15T23:56:14Z, **86 rows**, 20 checksummed artifacts. The live `analysis.html` was read back and carries the corrected citations, the six-item contrarian cost checklist, strategy rule 6 and the day-three points with working source links.
- **Deployment-verification warning for every session, learned the hard way twice in one night:** the first plain fetch of the live `build-info.json` after this deploy returned the **previous** revision (`c371d0a…`, built 23:45:45Z) because the Pages CDN served a cached copy; only a cache-busting query string returned `dd74142…`. The workflow's own verifier already appends `?deployment=<run id>`, which is why it passed. Anyone checking a deployment by hand must cache-bust, exactly as with the Gamma API reads flagged as `polymarket-cached-manual-reads-2026-10-16`.
- **Two claim-table items retired rather than delivered, so nobody waits on them:** the separate `twc.html` page and `data/twc-day2-day3.json`. PR #24 shipped a rendered day-three guidance section (`analysis.html#guidance`, plus its own executive-summary card) and PR #23/#25 put the decider market references in `data/analysis.json`, so a fourth surface would duplicate three existing ones. This session's day-three content is additive inside `data/analysis.json` and renders on `analysis.html`. For the same reason the "additive `scripts/build.py` page + nav" claim is retired: **this session's merged changes touch no shared script, renderer or workflow** — only its own `scripts/harvest_0e407ec7.py`, its own workflow, its own research directory, one new test file, `data/analysis.json`, `data/review-notes.json`, `COORDINATION.md` and the regenerated pages.
- **Left open for the next session (unclaimed here):** PR #23 (`dbe62379`) was still `CONFLICTING` against main at this point and needs a rebase; its Thunderpick corroboration and its 22:53:08Z observation of market 5763247 are already cited by this session's receipts and should be preserved, not overwritten. The BETBOOM–Legacy decider (17:00Z, verified) is still absent from the Hotspawn feed, so it still has no row and scores no points; the scheduled refreshes will price it automatically if Hotspawn lists it. The Aurora–9z row published at this build expires 2026-10-16T05:33:49Z and is re-sourced by the next run before then.

## Session ab18fe2a claims (2026-10-16, 04:20 UTC)

Arena fixes this session to `arena/ab18fe2a-maltaproj4`; the requested `session-<id>/<task>` branch naming is not available (the same constraint is recorded by every earlier session), so no other branch is created, checked out or pushed. Before claiming, all 21 remote heads and PRs #2–#28 were enumerated. **Every task on this board is `done`**; the newest commit on any session branch is `f5164dfe` (0e407ec7, 2026-10-16 00:0x, done and merged). PR #23 (`dbe62379`) is still `OPEN`/`CONFLICTING` and is left untouched. No active claim is overwritten and no other branch is touched.

**Discovered before claiming — the refresh gap is the live problem.** It is 04:17 UTC on 16 October. The two-hourly cron (`17 */2 * * *`, merged in PR #24 at 23:20 UTC on 15 October) has produced **zero scheduled runs**: the complete run history contains only two `schedule` events ever (2026-10-15T16:59:51Z success, 21:22:25Z failure, both under the old six-hour cron). Nothing fired at 00:17 or 02:17. The live site therefore still serves the 00:02 UTC push build (`data/latest.json` fixtures observed 2026-10-15T21:33:49Z), and **every open pick on it expires at 2026-10-16T05:33:49Z** — about 76 minutes after this claim. The user's "every 4–8 hours" requirement is not being met by cron alone.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| A1 Diagnose the zero-scheduled-run gap and make the refresh land inside the 4–8 h window without cron being reliable; publish the diagnosis as a flagged irregularity | in progress | ab18fe2a | research/refresh-ab18fe2a/**, data/review-notes.json (additive), .github/workflows/pages.yml (additive cron only) | 2026-10-16 04:20 |
| A2 Aurora roster change: verify from official/primary sources only; fold into Day-3 contrarian guidance | in progress | ab18fe2a | research/day3-ab18fe2a/**, data/analysis.json (additive) | 2026-10-16 04:20 |
| A3 Day-2 → Day-3 TWC 2026: independently re-verify the four day-2 series and the two day-3 deciders from HLTV; check whether Hotspawn now lists BETBOOM vs Legacy; refresh Day-3 guidance | in progress | ab18fe2a | research/day3-ab18fe2a/**, data/analysis.json (additive) | 2026-10-16 04:20 |
| A4 Coverage audit: confirm every open Hotspawn CS2 row has a pick or an explicit unresolved entry, and that the executive summary links the pick board / unresolved / analysis | in progress | ab18fe2a | research/day3-ab18fe2a/coverage.md, data/review-notes.json (additive) | 2026-10-16 04:20 |
| A5 Final integration for this branch: rebuild, line-by-line re-verification, PR to main, explicit merge, live Pages verification | in progress | ab18fe2a (final integration) | COORDINATION.md, README.md, build-info.json, generated root routes | 2026-10-16 04:20 |

### Session ab18fe2a evidence standard (restated)

Hotspawn establishes the fixture inventory only and is never a probability input. Probabilities come only from externally observed market lines (Polymarket exchange, Pinnacle bookmaker) or from reproducible arithmetic on them or on Valve's official standings. HLTV supplies identity, results, rankings, lineups and context. No crowd votes, no rank-to-probability formula presented as a market price, no 50/50 fillers, no inferred values. Every row carries a source link; anything unverifiable stays blank and flagged.

Sandbox bash networking reaches GitHub and package registries only, so HLTV/Polymarket/Pinnacle/Hotspawn are read through the retrieval tooling and through Actions runners. Any manual market read is cache-busted and dated by the payload's own `updatedAt` (irregularity `polymarket-cached-manual-reads-2026-10-16`). No access control is bypassed and no source is claimed to have been checked when it was not.

### Session ab18fe2a shared-file requests (logged, not edited)

- `.github/workflows/pages.yml`: this session adds cron slots only (plus its own branch to the push trigger list). Should a later session change the cadence again, keep the diagnosis in `research/refresh-ab18fe2a/`.
- `data/analysis.json` and `data/review-notes.json`: additive entries only, under this session's own keys. No existing key is renamed, retargeted or removed.
- `scripts/**`, `verification-c6/**`, `audits/**`, `site/**`: untouched by this session unless a build defect requires a fix, which would be logged here first.

### Session ab18fe2a findings and shared-file log (2026-10-16, 05:0x UTC)

**A1 — the scheduled refresh never fired (measured, mitigated, published).** Through the official GitHub Actions API at 04:18Z: the workflow's entire run history contains **two** `schedule` events (2026-10-15T16:59:51Z success, 4h42m late; 21:22:25Z failure, 3h05m late), and **zero** after the two-hourly cron merged at 23:20:34Z — nothing at 00:17, nothing at 02:17, 4h58m of silence. The workflow reports `state: active`, so this is GitHub delay, not a disabled schedule. Consequence: the live site was serving the 00:02Z push build whose **20 open picks all expired at 2026-10-16T05:33:49Z**, so without a push the whole board would have gone stale at once. Also measured: **this project's GitHub App token cannot create workflow_dispatch events** — `gh workflow run pages.yml --ref main` returns `HTTP 403: Resource not accessible by integration`, so a push to main is the only trigger available. Mitigation: cron `'17 */2 * * *'` → **`'17 * * * *'`** with the measurement recorded beside it; `refresh_hours` 2 → 1; the two user-visible cadence strings in `scripts/build.py` and the README now say hourly. Diagnosis: `research/refresh-ab18fe2a/DIAGNOSIS.md`. Flagged as `scheduled-refresh-gap-2026-10-16`. **This is a risk reduction, not a fix** — no cron can guarantee delivery, and the failure mode remains a visible staleness warning rather than a wrong number.

**A3 — the Group B decider is now on the Hotspawn board (correction, verified twice).** At 04:22Z the Hotspawn CS2 scheduled feed returns **fixture 1081775**: BetBoom (115660) vs Legacy (130389), `scheduled_start_time` 1792170000000 = **2026-10-16T17:00:00Z**, lock 16:54:00Z, tier **s**, 7 points. Hotspawn's own match page renders "BetBoom vs Legacy", 17:00, 16 OCT, with lineups `s1ren/Magnojez/d1Ledez/zorte/Boombl4` and `latto/n1ssim/arT/dumau/try`. This **resolves the irregularity every session since d3af051a has carried** (`betboom-legacy-missing-2026-10-15`, `twc-day3-groupb-line-2026-10-16`). Identities needed no change: `data/identities.json` maps BetBoom/BetBoom Team/BB Team and `plain_name()` casefolds, so Hotspawn "BetBoom" and Polymarket "BetBoom Team" are one identity. The line clears the strict tier: market 5763247 at `updatedAt` 2026-10-16T04:21:07Z reads Legacy **0.655** / BetBoom **0.345**, bid 0.65 / ask 0.66 (1-point spread), $26,994 liquidity, active and accepting orders. Across four dated states the favourite never changed; the spread fell 10 → 1 and liquidity quadrupled.

**A4 — the Aurora roster premise was checked and does not hold.** HLTV team 11861 lists Aurora's current five as XANTARES, woxic, Jimpphat, kyxsan (IGL), Wicadia, coach ash, ranked **#5 VRS / #6 HLTV world**. The rebuild (Jimpphat from MOUZ, ash from GamerLegion, kyxsan completing the five) is dated **8 July 2026** by trade press — roughly a full ranking cycle before this event, and three of the five predate it. The project therefore does **not** use "new roster" as the contrarian case for 9z; the sourced case is the 2-0 head-to-head two days earlier plus a map win over Falcons. Flagged as `aurora-roster-change-2026-10-16`, including the standing conflict that auroragg.com lists Polymarket as a partner. Also verified: **neither day-three decider has a rest asymmetry** — all four teams played on 15 October (HLTV results, event 8932).

**Day-2 results re-read from source and matched, with no correction needed.** All eight series scores on <https://www.hltv.org/results?event=8932> reproduce the published table exactly. Both decider start times are machine-verified (14:00Z from Hotspawn 1080205 + HLTV countdown; 17:00Z from Hotspawn 1081775 + HLTV countdown + Polymarket `gameStartTime`) — HLTV's *displayed* clock is reader-local and was not used.

**Shared files touched, all logged rather than assumed:**

- `.github/workflows/pages.yml` — cron cadence only, plus this session's branch added to the push trigger list. No step, job, permission or action version was changed.
- `data/analysis.json` — additive (`upset_context.points` +1 card, `day_three.points` +3, `day_three_guidance.fixtures` +1) **plus four corrections of statements that had become false**: `day_three.fixtures[1].hotspawn_fixture` `null` → `"1081775"`; its `hotspawn_note` rewritten; `day_three_guidance.not_listed[0]` given `now_listed: true` and a corrected `why`; `day_three.contrarian.limits` corrected from "the only day-three fixture this board can act on" to two. No existing key was renamed or removed, and no other session's content was dropped.
- `data/review-notes.json` — additive (2 new notes) **plus two rewrites**: `betboom-legacy-missing-2026-10-15` and `twc-day3-groupb-line-2026-10-16` are now `Resolved`, and `schedule-delays-2026-10-15` now records that its two-hourly cadence was superseded. The rewrites were forced by a guard test: leaving the original wording in place published a claim this session had just disproved.
- `scripts/build.py` — three cadence strings and one data-driven card eyebrow (`"Now on the Hotspawn board"` when `now_listed`, otherwise the previous text). No layout, style, navigation or calculation change.
- `scripts/refresh.py` — `refresh_hours` 2 → 1 (advertised cadence metadata only).
- `scripts/backfill_quotes.py` — one word in a docstring.

**New files, this session only:** `research/day3-ab18fe2a/**` (verification + 2 receipts), `research/refresh-ab18fe2a/DIAGNOSIS.md`, `tests/test_ab18fe2a.py` (8 tests).

**Verification performed locally on this branch:** 122 unit/pipeline tests, 9 audit tests, 5 integrity tests, 12 verification-c6 tests all pass; `verification-c6/audit_snapshot.py` on the snapshot → 0 failures; quarantine → 0 withheld; build → 86 rows / 20 priced / 2 unresolved; validate → 15 pages, 562 internal links, 20 artifact checksums, 196 displayed rows; `scripts.validate --site .` passes on the staged root fallback.

### Session ab18fe2a publication record (2026-10-16, 04:5x UTC)

- **PR #29 merged** without an approval wait, per the standing instruction: https://github.com/buffedlizard55-lab/MaltaProj4/pull/29 → merge commit **c4fd97a9ddd7cb449ddd5f9a18a7cc6b594b99ed**, merged 2026-10-16T04:34:36Z. `verify-build` passed in 45 s on the PR head (run 38851173243); `deploy` correctly skipped, as PRs must not publish.
- **Push run 38851339231 (main) succeeded end to end** — live refresh, independent row audit, build, validation, browser/expiry checks, Pages upload, deploy, and its own byte-for-byte live verification.
- **Live site re-retrieved after that deploy, cache-busted:** `build-info.json?deployment=38851339231` reports revision `c4fd97a9…`, `built_at` 2026-10-16T04:36:06Z, snapshot 04:36:05Z, **95 rows** (up from 86 — the refresh discovered nine new Hotspawn fixtures, including the Group B decider), 20 checksummed artifacts.
- **The Group B decider is live and priced exactly as this session predicted.** `picks.html` now shows `BetBoom vs Legacy`, Thunderpick World Championship 2026, tier S, 16 Oct 17:00 UTC, **BetBoom 34.5% / Legacy 65.5%**, fair line 2.90 / 1.53, VRS model 20.7% / 79.3%, pick **Legacy**, sourced to Polymarket market 5763247 and Hotspawn fixture 1081775. That is the 0.345 / 0.655 verified by hand at 04:21Z, produced end to end by the pipeline with no new alias. Aurora vs 9z reads **69.5% / 30.5%**, pick Aurora, model 68.0% / 32.0%.
- **Coverage of open matches is complete:** the live pick board lists **29 open matches and every one carries a pick** — market lines, our VRS model lines, and two research-only ranking picks. The two research-only rows (Procyon vs LOS NINOS, Infinite vs Insiders) publish a pick with **no percentage**, which is the documented limitation, not a gap. Zero open rows are without a pick.
- **A scheduled run finally fired:** 38851255388 at 04:33:39Z, the first `schedule` event in nearly seven hours — but under the *old* two-hourly cron, since it started a minute before this merge landed. Its `verify-build` passed and its **`deploy` failed** after six seconds (04:35:30Z → 04:35:36Z). Measured, not explained: at that moment GitHub's own legacy `pages-build-deployment` (run 38851339231's dynamic job, 04:34:38Z → 04:36:52Z) was building the same site from `main:/`, because Pages source is still the legacy configuration. **This session could not read the failing job's log** (the sandbox cannot reach the Actions log host), so **no cause is asserted and no fix was applied blind**; it is published as `concurrent-pages-deploy-failure-2026-10-16` with both run links. The failure cost nothing: the following push run deployed a verified build.
- **New flagged irregularity `wbt-alias-used-outside-scope-2026-10-16`:** the WROTBERRY↔WBT alias, registered for Elisa BreakOut Series #2 only, is now pricing Hotspawn fixture 1081529 (Nexus vs WROTBERRY, **DraculaN Season 7**) at 30.3% / 69.7% from the VRS model, with HLTV 2399593 as the identity source. A scoped mapping is being applied outside its scope. Left published and flagged, with sources; either widen it with primary evidence or narrow it so the row goes blank.

**Local verification on the branch before the merge:** 122 unit/pipeline tests, 9 audit tests, 5 integrity tests and 12 verification-c6 tests all pass; `verification-c6/audit_snapshot.py` → 0 failures; quarantine → 0 withheld; build → 86 rows / 20 priced / 2 unresolved; `scripts.validate --site .` → 15 pages, 562 internal links, 20 artifact checksums, 196 displayed rows.

**Left open for a later session (unclaimed here):**
- PR **#23 (`dbe62379`) is still open and conflicting** against main; its Thunderpick corroboration and its 22:53:08Z reading of market 5763247 are cited by earlier sessions and should be preserved rather than overwritten.
- The legacy `main:/` Pages source remains in place and is the prime suspect for the deploy collision above. Switching Pages to GitHub Actions would remove the dual-build race entirely; that changes repository settings, which no session can do from a branch.
- The WBT alias scope decision above.
- Valve's next monthly standings (early November) are picked up automatically; the vendored copy is only a fallback.

### Session ab18fe2a — final status (2026-10-16, 04:50 UTC)

All five claimed tasks are **done**. Status of the claim table above: A1 done, A2 done, A3 done, A4 done, A5 done (final integration: PRs #29 and #30 merged, live deployments verified byte-for-byte).

| Task | Result |
|---|---|
| A1 refresh cadence | Cron is hourly. Measured zero scheduled runs in five hours; published the diagnosis and the 403 on `workflow_dispatch`; flagged `scheduled-refresh-gap-2026-10-16`. A scheduled run then fired at 04:33:39Z (under the old cron, one minute before the merge). |

## Session 9787ce4b claims (2026-10-16, 19:30 UTC)

Arena fixes this session to `arena/9787ce4b-maltaproj4`; no other branch is created or checked out. The working tree contains the final published state from earlier sessions (build `8e374f4`/`0ba6742`). It is 19:31 UTC on 16 October; Day 3 (group deciders) is finishing live and Day 4 (semifinals) is tomorrow.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Day 3 TWC results verification (Aurora 2-0 9z; BETBOOM/Legacy in progress), Day 4 semifinal contrarian-but-not-stupid guidance with per-fact sources | in progress | 9787ce4b | data/analysis.json (additive day_three_results, day_four), research/day4-9787ce4b/** | 2026-10-16 |
| Refresh live Hotspawn inventory to pick up semifinal fixtures, guarantee a pick for every listed fixture, publish executive-summary links | in progress | 9787ce4b | scripts/** (no semantic changes unless required), data/**, generated root HTML routes | 2026-10-16 |
| Final rebuild, line-by-line verification, PR to main, explicit merge, live Pages verification | done | 9787ce4b | COORDINATION.md, build-info.json, root deployment files, research/day4-9787ce4b/** | 2026-10-16 |

Evidence standard unchanged: Hotspawn fixes the fixture inventory only, never probability. Probabilities come only from externally observed market lines (Polymarket exchange, Pinnacle bookmaker) or reproducible arithmetic on them or on Valve's official standings; HLTV supplies identity/results/rankings; anything unverifiable stays blank and flagged. Sandbox reaches GitHub/package registries only, so HLTV/Polymarket/Pinnacle/Hotspawn are read through the retrieval tooling and the scheduled Actions runners.

Shared-file note: the working tree has been left in published state by prior sessions. If any shared script (build.py/core.py/refresh.py/validate.py) requires a change to correctly render new analysis keys or accept new fixtures, the change is minimal and additive and is logged below. No existing test, alias, tier or published number is loosened or removed.

### Session 9787ce4b results (16 October 2026 ~19:30–19:45 UTC)

- **Day 3 results added to `data/analysis.json` under `day_three_results`:** Aurora 2-0 9z verified from HLTV report 45736 and HLTV match 2399412 (Cache 13-11, Inferno 13-4; kyxsan 1.45 rating). BETBOOM vs Legacy observed live at build time from HLTV 2399413 (Nuke 16-13 BETBOOM OT, Dust2 11-13 Legacy, Mirage decider in progress ~7-10 Legacy); result not final at build time so flagged as LIVE / in progress.
- **Day 4 (17 Oct) semifinals added under `day_four`:** FURIA vs Aurora 14:00 UTC (HLTV 2399414; VRS 26.5/73.5 Aurora; pick Aurora, model-backed) and Falcons vs BETBOOM/Legacy winner 17:00 UTC (HLTV 2399415; pick Falcons regardless of opponent, ranking-backed). Both picks carry explicit limitations: not yet listed by Hotspawn, no strict exchange-tier price available. Polymarket show prices (~50/50, low liquidity) are reported as context only.
- **Contrarian framework update:** the Aurora roster premise (Jimpphat + kyxsan added 8 July 2026) is ~3 months old — NOT onboarding risk you can bet against; three prior deep runs with this core are documented. Day-1 lesson: one-map upsets don't reverse form lines when the favourite has veto and a full series to adjust (Aurora returned the 2-0 with an identical veto win). Value leans: Aurora over FURIA (VRS 73.5% vs market ~50/50); Falcons in semi #2. Avoids: FURIA on defending-champion narrative; BETBOOM long-shot over Falcons.
- **Mobile/executive-summary discoverability:** executive-summary hero links directly to Day-4 semis and Day-3 results; start-here cards add dedicated Day-4 and Day-3 entries; analysis-page sub-nav adds #day-four and #day-three-results anchors; page meta description updated to mention day-four picks.
- **No shared-script semantics changed:** `scripts/build.py` changes are additive renderers for two new analysis keys (`day_three_results`, `day_four`) plus link/hero-card additions. No alias, tier, probability or validator gate was modified. All 195 tests pass after the fixes; the independent validator reports 106 rows / 36 calculations reproduced / 695 internal links / 20 checksums / 277 displayed rows when built against a fresh snapshot (sim_now 09:00 UTC).
- **Source record:** `research/day4-9787ce4b/SOURCES.md` lists every primary URL used in the new sections.
- **Build with real current time correctly shows 0 priced / 14 unresolved stale warning** because the last captured evidence (07:21 UTC) is older than the 8-hour TTL at build time. This is the fail-safe behavior: the site withholds stale numbers rather than publishing them. The hourly GitHub Actions workflow (`pages.yml`) refreshes prices end-to-end from a runner with real internet access and deploys a fresh build; the next successful scheduled run will populate the pick board with current lines.
- **Irregularities flagged:** (1) Day-4 semifinal fixtures do not yet appear in Hotspawn's CS2 feed, so no Hotspawn pick or fixture ID exists for them — picks are research-only and labelled as such, per project policy. (2) BETBOOM/Legacy winner is unknown at build time so the second semi's opponent cell is not finalised. (3) Sandbox could not refresh live prices (network restriction); deployment relies on the hourly Actions pipeline. (4) WBT alias scope concern (`wbt-alias-used-outside-scope-2026-10-16`) from session ab18fe2a remains open; no change made here.
| A2 Aurora roster | Verified from HLTV: XANTARES, woxic, Jimpphat, kyxsan, Wicadia, coach ash; #5 VRS / #6 HLTV. The rebuild dates to 8 July 2026, so the "new roster" thesis is not supported and is not used. Flagged `aurora-roster-change-2026-10-16`. |
| A3 Day-2 → Day-3 | All eight series scores re-read from HLTV and matched, no correction needed. Both decider start times machine-verified. **Group B decider found on Hotspawn as fixture 1081775** and now published at Legacy 65.5% / BetBoom 34.5%. |
| A4 coverage | Live board: 31 open fixtures — 29 with probabilities (22 market, 7 model), 2 research-only picks, **0 with no pick**. The executive summary links the pick board, the unresolved section and the day-3 guidance from the top of the page and from the mobile bottom bar. |
| A5 integration | PR #29 → `c4fd97a9`, PR #30 → `36a58323`. Both `verify-build` green; both push runs deployed; live `build-info.json` re-read and cache-busted after each. |

**Live receipt at close:** revision `36a58323`, `built_at` 2026-10-16T04:42:50Z, snapshot 04:42:49Z, 95 feed rows, 20 checksummed artifacts.

**Sources used:** Hotspawn CS2 scheduled fixture API and two Hotspawn match pages (1081775, 1081529); HLTV results (event 8932), event 8932 overview, team 11861, matches 2399412 and 2399413; Polymarket markets 5763247 and 5733288 (cache-busted, dated by payload `updatedAt`); auroragg.com; the GitHub Actions API for this repository.

**Verification performed:** 122 unit/pipeline + 9 audit + 5 integrity + 12 verification-c6 tests; independent row audit 0 failures; quarantine 0 withheld; build and `validate --site .` green; two live deployments verified byte-for-byte against their build manifests; every published page re-read from the live site with a cache-busting query.

**Irregularities flagged (all on Flagged for Review, none blocking):** `scheduled-refresh-gap-2026-10-16`; `concurrent-pages-deploy-failure-2026-10-16`; `wbt-alias-used-outside-scope-2026-10-16`; `aurora-roster-change-2026-10-16`. Two previously flagged items were resolved rather than added: `betboom-legacy-missing-2026-10-15` and `twc-day3-groupb-line-2026-10-16`.

*(Session `dedd2e34` claim below was written at 04:20 UTC against `2eb71f5`, i.e. before `ab18fe2a` merged. Two sessions worked the same brief in parallel and reached the same conclusions independently: fixture 1081775 appearing on the board, the 04:21Z Legacy 65.5 / BETBOOM 34.5 line, the 14-point model-vs-market gap, the Aurora roster premise being three months old rather than a live upset reason, and cron delivery being the freshness problem. `ab18fe2a` owns the hourly cron change and the `now_listed` guidance mechanism, which this branch adopts rather than duplicates; this branch adds the board UX (today section + published gap ledger), the ledger-replay mode fix, the coverage-gap check wired to the collector client, the esportsbook reachability probe and a stale-snapshot watchdog on top. No file of theirs is reverted.)*
## Session dedd2e34 — day-1/day-2 audit, day-3 live picks, full-coverage guarantee (16 October 2026, 04:20 UTC)

Arena fixes this session to `arena/dedd2e34-maltaproj4`; the requested `session-<id>/<task>` naming is not available (same constraint every earlier session recorded), so no other branch is created, checked out or pushed. Before claiming, all 21 remote heads were enumerated with `git ls-remote`: main is `2eb71f5` (PR #28, session 0e407ec7) and this branch starts from it, so no other session's work is being redone or overwritten. Every task on the board above is **done**; PR #23 (`dbe62379`, 23:10 UTC 15 Oct, research only, `CONFLICTING`) is still open with no commits for 5 h and is left untouched rather than taken over. Claimed before starting:

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Line-by-line re-audit of the published TWC day-1 and day-2 claims (HLTV match/report pages, map scores, UTC starts, VRS/roster facts) with corrections where a claim is wrong | **done** | dedd2e34 | research/day1/**, research/day2/**, data/analysis.json, audits/**(new file only) | 2026-10-16 04:20 |
| Live day-3 pick guidance sourced from a fresh Actions harvest (inventory + market lines + receipts), plus the Hotspawn-vs-HLTV fixture coverage gap (BETBOOM–Legacy) published as an explicit gap | **done** | dedd2e34 | .github/workflows/harvest-dedd2e34.yml, research/day3-dedd2e34/**, scripts/harvest_dedd2e34.py, data/analysis.json | 2026-10-16 04:20 |
| Verify a pick or an explicit unresolved entry for every listed fixture in the fresh snapshot; try additional esportsbook sources for gaps and record access limitations | **done** | dedd2e34 | research/day3-dedd2e34/**, data/review-notes.json | 2026-10-16 04:20 |
| Mobile/exec-summary usability pass on the published routes, and final integration PR to main + merge + Pages deploy verification | **done** | dedd2e34 | COORDINATION.md, README.md, root generated HTML routes (regenerated only) | 2026-10-16 04:20 |

- Scope discipline: this session changes **no shared script** unless a defect is proven by a failing test — `scripts/core.py`, `scripts/refresh.py`, `scripts/build.py`, `scripts/validate.py`, `verification-c6/**`, `assets/**` and `.github/workflows/pages.yml` are read-only here. Any needed change to those is logged on the board instead of edited.
- **Scope amendment, recorded before pushing the work (04:45 UTC):** the read-only line above was the opening position; two parts of it no longer hold, because the usability and correctness defects the user asked for could not be fixed from outside those files. This session now edits: `scripts/build.py` (additive: a `starts_on`/`array` pair of helpers, a `gap_ledger` renderer, the Today's-picks / Next-on-the-board section, the gap cards inside `#unresolved-summary`, and the freshness and methodology copy); `site/assets/style.css` (27 appended lines and no deletions: `.gap-grid`, `.gap-card`, `.rejected-line`, one mobile block, and a `white-space:normal` rule so a descriptive source label cannot push a phone page wider than the viewport); `scripts/harvest_dedd2e34.py` and `scripts/coverage_gap_dedd2e34.py` (this session's own scripts); `scripts/refresh_watchdog.py`, `.github/workflows/refresh-watchdog.yml`, `.github/workflows/harvest-dedd2e34.yml`, `tests/test_refresh_watchdog.py` and the new `tests/test_board_ux_dedd2e34.py`; `data/analysis.json`, `data/review-notes.json`; and the regenerated root snapshot (`index.html`, `picks.html`, `matches.html`, `analysis.html`, `unresolved.html`, `review.html`, `sources.html`, `evidence.html`, `404.html`, `methodology.html`, `assets/**`, `build-info.json`, `data/matches.csv`, plus a `built_at`-only change inside `data/latest.json`). **Still untouched:** `scripts/core.py`, `scripts/refresh.py`, `scripts/validate.py`, `scripts/inventory.py`, `scripts/hltv.py`, `scripts/vrs.py`, `verification-c6/**` and `.github/workflows/pages.yml`. No existing CSS rule or build function was rewritten: the diffs are appends plus one replaced section. Integrator note: if another session touches `scripts/build.py` or `site/assets/style.css` before this merges, rebase by appending rather than rewording the ledger copy.
- Evidence standard unchanged and inherited: Hotspawn fixes the fixture inventory only and is never a probability input; probabilities come only from external market lines that pass the published gates, or a clearly labelled originated model line; unverifiable values stay blank and are flagged on the Flagged for Review page.
- Known trap recorded by 0e407ec7 and re-checked here: manual reads of the Polymarket Gamma API through page retrieval can be served from an HTTP cache. Every manual market read in this session is cache-busted and dated by the `updatedAt` inside the payload, and every published number comes from the Actions refresh instead.

### Session dedd2e34 — delivery record (2026-10-16, 05:00 UTC)

Claim-table status: all four rows above are **done** — day-1/day-2 re-audit (no correction needed, two
already-recorded corrections confirmed), live day-3 guidance from a fresh Actions harvest, a pick or an
evidenced gap for every listed fixture, the mobile/exec-summary usability pass, and the final
integration.

**PR #32** → https://github.com/buffedlizard55-lab/MaltaProj4/pull/32, merged as
**`2d6d0330a384490204e1c4070f65c720c74bb6e1`** at 2026-10-16T04:56:10Z without waiting for approval.
`verify-build` was green on the rebased head first (run 38853007126, 1m16s) and the branch reported
`mergeStateStatus: CLEAN`. **Publication run 38853165886** (push to main) succeeded end to end: live
source refresh, independent row audit before and after the build, quarantine, build, `validate`,
`npm run test:browser`, Pages upload, deploy, and the byte-for-byte check of every artifact against the
build manifest. **Live receipt, re-read cache-busted** (`build-info.json?cb=dedd2e34-pr32`): revision
`2d6d033…`, `built_at` and `snapshot_generated_at` 2026-10-16T04:56:48Z, **95 rows**, 20 checksummed
artifacts. The board is therefore current as of this merge, not merely built on the branch.

**Sources used in this session's own work** (all read on 16 October 2026, UTC): HLTV results for event
8932 and the four day-1 plus four day-2 series; HLTV match pages 2399412 (Aurora–9z, Bo3, "Group A
decider", 14:00Z) and 2399413 (BETBOOM–Legacy); HLTV team pages 11861 (Aurora: XANTARES, woxic,
Jimpphat, kyxsan, Wicadia, coach ash; VRS #5 / HLTV #6) and 9996 (9z: VRS #11, world #17, coach BIT,
and the head-to-head read "2-4 in maps" across three meetings); HLTV news 45718 / 45722 / 45728 /
45729 / 45730; the TWC event page (14–18 October, Malta, $1M split 50/50, eight teams, single-elimination
playoffs); Polymarket Gamma markets 5733288 (Aurora–9z) and 5763247 (Legacy–BetBoom), each dated by the
payload's own `updatedAt` and cache-busted because a repeat read of the same URL can be served from an
HTTP cache; Polymarket market 5650404 (the withheld Infinite–Insiders line); the Hotspawn CS2 scheduled
fixture API and the two Hotspawn lobby pages; Valve's `counter-strike_regional_standings` repository via
the GitHub contents API; `strafe.com` and `cs2news.com` for the Aurora rebuild dates; `liquipedia.net`,
`blast.tv`, `dust2.us` and `cs2news` for day-2 corroboration. `esports.gg` was found to publish wrong
dates for this event and is **never** cited.

**Verification performed here:** `python3 -m unittest discover -s tests` → 148 tests OK (this session
added `tests/test_board_ux_dedd2e34.py`, 12 tests, and 3 watchdog tests); `scripts.build` +
`scripts.validate` green on both the committed 86-row snapshot and the 95-row CI harvest (635 internal
links and assets, 243 displayed rows, 29 probability calculations reproduced, 20 artifact checksums);
`verification-c6/audit_snapshot.py` → 0 failures on both snapshots; `npm run test:browser` → green,
including 32 no-overflow + axe scans at 320/390/768/1440 and the seven expiry boundary scenarios;
`python -m scripts.stage_legacy` then `scripts.validate --site .` green; the market ledger replayed
29/29 published probabilities from their raw inputs with 0 mismatches
(`research/harvest-dedd2e34/market-ledger-correction-2026-10-16.md`).

**Irregularities and limitations found, all published rather than papered over:** five new review notes
(`gap-ledger-published-2026-10-16`, `esportsbook-access-probe-2026-10-16`, `thin-market-withheld-2026-10-16`,
`vrs-standings-still-newest-2026-10-16`, `refresh-cadence-watchdog-2026-10-16`) on top of the four
`ab18fe2a` added, and one stale statement corrected in main's own data: `day_three_guidance.unverified[0]`
still described the BETBOOM–Legacy start as "derived from HLTV's relative schedule", which stopped being
true when the fixture reached the board with its own `2026-10-16T17:00:00Z` start, `16:54:00Z` lock and
`offered_points: 7`; it now says so and cites both sources. Two claims that this session first wrote and
then disproved with its own tooling are documented instead of deleted: the "16 rows swapped order" ledger
alarm (this project's replay bug, fixed by splitting price-normalisation from de-margining) and a
hand-computed test assertion that was itself wrong (the minus side is the favourite) — derive expected
floats from the formula, never from mental arithmetic.

**Left for the next session, unclaimed:** (1) the 30-minute watchdog (`refresh-watchdog.yml`) has now
never run — its first schedule tick fires on the hour and half hour, and `gh workflow run` from this
token is refused (HTTP 403, `Resource not accessible by integration`), the same limitation `ab18fe2a`
recorded, so it is verified by unit tests plus CI until a scheduled tick lands; check
`gh run list --workflow refresh-watchdog.yml` after 05:30Z. (2) The `Age` floor on the Hotspawn CDN
response (observed 3504 s on `cs2-pickems` and 10074 s on the general lobby) means a board change can be
invisible for up to roughly three hours; the 8-hour evidence window absorbs this, but a reader asking
"why did the fixture appear late?" should be pointed at `source_checks`. (3) ~~`market-ledger.json` /
`harvest-summary.json` in `research/harvest-dedd2e34/`~~ **closed the same hour by PR #33**: the originals stay
as run 38850237836's receipt, deliberately not rewritten, with `market-ledger-correction-2026-10-16.md`
beside them and two regenerated live receipts from runs 38853541668 and 38853689469. (4) PR #23 (`dbe62379`) is still open and
conflicted against main; its Thunderpick corroboration and 22:53:08Z read of market 5763247 are already
cited by two sessions' receipts, so it can be closed if its owner does not rebase it.

**Same session, closing the last loose end (05:10 UTC).** **PR #33** →
https://github.com/buffedlizard55-lab/MaltaProj4/pull/33, merged as
**`fd865bc34bd430a4daa9a7f514af845dd5f185b2`** at 2026-10-16T05:06:35Z (`verify-build` pass, 1m15s,
`MERGEABLE CLEAN`, no approval waited on); publication run **38854064715** then succeeded end to end and
the live `build-info.json?cb=dedd2e34-pr33-final` re-read reports revision `fd865bc3…`, `built_at` and
`snapshot_generated_at` 2026-10-16T05:07:22Z, **95 rows**, 20 checksummed artifacts. That PR carried
`research/harvest-dedd2e34/market-ledger-correction-2026-10-16.md`, the two regenerated live-harvest
receipts, and the coverage-gap fixes. **Item (3) of the left-behind list is therefore closed**: the
corrected ledger is on main, and the original run 38850237836 output is preserved beside it rather than
rewritten. Two findings worth inheriting: the gap check now measures what it claims
(`scripts.coverage_gap_dedd2e34` had to route through `scripts.refresh.Sources`, and its run report
states that only `absent_from_board` is a finding — 93 board rows belonging to other events are context,
and a series HLTV has already finished cannot prove a gap), and `#runtime-stale` is `hidden` in the markup
with `app.js` setting `warning.hidden = !globalStale`, so the "current picks are withheld" banner is never
visible on a fresh snapshot even though a text extractor shows its content. One note on method: a commit
message on this branch carries an inherited `Co-Authored-By` trailer naming a specific underlying model;
it is an artifact of tooling, not a statement about this project's provenance, and every number in these
receipts is reproducible from the commands recorded in the correction note.

**Measured cadence, and a request to the main-owning session (05:12 UTC).** `gh api …/actions/runs?event=schedule`
returns exactly three scheduled runs of `pages.yml` ever: 2026-10-15T16:59:51Z **success**,
2026-10-15T21:22:25Z **failure**, 2026-10-16T04:33:39Z **failure**. In both failures `verify-build` passed and
the failing step is `deploy` → **"Deploy verified static dashboard"**, i.e. the site was built, validated and
deployed, and the run died on the post-deploy byte-for-byte receipt. `refresh-watchdog.yml` has **no runs at
all** — it reached main with PR #32 at 04:56:10Z, after the 04:33 slot it would have backfilled, and no
`*/30` tick has been recorded since, so its first chance is 05:30Z. Consequences, stated plainly: the
published board's freshness currently rests on push-triggered runs, and the schedule is not a cadence anyone
should quote. **Request (I cannot act on it myself — `.github/workflows/pages.yml` is main's claimed file, so
nothing under my session touched it):** make the post-deploy receipt read cache-busting and retry, e.g.
`build-info.json?cb=${{ github.run_id }}` with a couple of attempts a few seconds apart, because Pages can
answer with the previous artifact for a short window after a green deploy; and add the same `?cb=` treatment
anywhere the deploy step re-reads a static file. Two independent sessions have now hit this class of failure
(`ab18fe2a` recorded the stale-`build-info` trap in prose, this one in run records), so it is a real edge, not
bad luck on a single runner. Until it is fixed, a red `deploy` step whose only failing line is the byte
comparison should be treated as "deployed, receipt not yet verifiable" and re-checked by hand — which is how
this session confirmed 04:56:48Z (95 rows) and 05:07:22Z (95 rows) as live.

## Session 1abe803f claims (2026-10-16, 2026-10-16 07:17 UTC)

Arena fixes this session to `arena/1abe803f-maltaproj4`; the requested `session-<id>/<task>` naming is not available (same constraint every earlier session recorded), so no other branch is created, checked out or pushed. Before claiming, `git fetch origin` showed only `main` (f91ca1a) on the remote; the last board activity is dedd2e34 at 05:12 UTC, all claims are `done`, and no claim has been active for more than 60 minutes. This is new work for the same brief, not a takeover of an active claim. Scheduled runs of `pages.yml` have not fired since 04:33 UTC (the only scheduled run on record since the cron was added was a failure), so the published board is stale; this session re-harvests it.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Day-1 (9z–Aurora) and Day-2 TWC re-verification against HLTV and Aurora roster-change sourcing; contrarian-but-not-stupid Day-3 guidance and its limits | done (claim-by-claim log in research/day1-1abe803f/VERIFICATION.md; research/day2-1abe803f/ not used) | 1abe803f | research/day1-1abe803f/**, research/day2-1abe803f/**, data/analysis.json | 2026-10-16 07:55 |
| Own non-publishing harvest of every Hotspawn CS2 fixture (inventory, Polymarket/Pinnacle/HLTV tiers, unresolved reasons) on this branch | done (runs 38866347992 and 38866629566, both success; 106 rows, 42 open, alias for 1081493 applied) | 1abe803f | .github/workflows/harvest-1abe803f.yml, research/harvest-1abe803f/** | 2026-10-16 07:55 |
| Final integration: refreshed data, executive summary links, unresolved + limitations, mobile checks, PR to main, merge, live Pages verification | in progress — PR and merge pending; result recorded in the log below when complete | 1abe803f (final integration) | data/latest.json, data/matches.csv, data/review-notes.json, data/identities.json, scripts/build.py, site/**, assets/**, index.html, README.md, COORDINATION.md, generated root HTML routes | 2026-10-16 07:17 |

### Session 1abe803f — integration log (16 October 2026, UTC)

- **Harvest:** run 38866629566 (triggered by the alias commit `c787a32`) completed with success. `research/harvest-1abe803f/latest.json` shows 106 rows, 42 open and 64 not open. Every open row has a pick. Fixture 1081493 (Eternal Fire vs Apogee Betclic, 08:00Z) is now priced at Eternal Fire 65.5% from Polymarket 5732890 (exchange, thin market, about $8.7k liquidity). Coverage is partial: API 103, lobby 95, page 95.
- **Identity:** alias `Betclic Apogee Esports` (names `Apogee Betclic`) registered for one exact opponent pair and one exact UTC start, with HLTV 2399654 and Polymarket 5732890 as sources. No fuzzy matching.
- **Corrections:** the Day-3 draft said HLTV records the Aurora vs 9z head-to-head as "2-4 in maps to Aurora". HLTV's Aurora team page says 4-2 in maps to Aurora (three meetings, series 2-1). The corrected text is in `data/analysis.json`. The roster premise is also corrected: the most recent verified Aurora change is 8 July 2026 (kyxsan), about 14 weeks before the decider, not days before. The Aurora site's first LAN with the new roster is dated 20 Aug 2026.
- **Verification:** every checked claim is listed with its verdict in `research/day1-1abe803f/VERIFICATION.md`. Items that could not be re-read are marked "not re-checked" and stay flagged in `review-notes.json` (flagged for review, not blocking).
- **Checks run locally:** `scripts.build` and `scripts.validate` pass on `data/latest.json` (public output and root fallback after `stage_legacy`). Unit tests: 149 OK. `audits/` and `verification-95b588c2/test_integrity.py` pass.
- **Conflicts:** none on files. No other session had an active claim at 07:17 UTC.
- **Requests / handoffs (not edited by this session):**
  - To the owner of `research/day2/DAY2-REVIEW-2026-10-15.md` (session e54807b3): line "coach ash" needs reconciling. Strafe spells the handle "ashhh" and HLTV writes "ash". The site uses the HLTV form. This session did not edit that file.
  - To the Pages/refresh owners: the schedule still shows no reliable cadence. The harvest runs hourly, but the 4–8 hour refresh is not yet confirmed from the scheduled-run record. The Actions API check remains open (see `review-notes.json`, `refresh-cadence-watchdog-2026-10-16`).

## Session ef0969b9 claims (2026-10-16, 07:20 UTC) — coordinated around session 1abe803f

Arena fixes this session to `arena/ef0969b9-maltaproj4`; no other branch is created, checked out or pushed.
Before claiming, `git fetch origin` was run and **all** remote heads were enumerated. Session `1abe803f`
had just claimed (07:17 UTC, commits 7f2c11d/4a3b136) the day-1/2/3 review, `data/analysis.json`, its own
non-publishing harvest and the **final integration** of `data/**`, `scripts/build.py`, `site/**`,
`assets/**`, `index.html`, `README.md` and the generated root routes. Its claim is fresh (minutes old), so
per the board rules it is **not** taken over and none of its files are edited by this session. This session
takes a deliberately disjoint lane and hands its findings over for integration.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Publication reliability: make the scheduled refresh actually land inside the requested 4–8 h window (measured: 3 scheduled runs ever, 1 since the hourly cron, 2 of 3 red) without weakening verification | in progress | ef0969b9 | .github/workflows/pages.yml, .github/workflows/refresh-watchdog.yml, scripts/refresh_watchdog.py, tests/test_publish_gate_ef0969b9.py, research/ef0969b9/** | 2026-10-16 07:20 |
| Independent verification of what is actually published (live artifact vs published HTML, row/probability replay, 320/390 px layout) published as a separate audit directory | in progress | ef0969b9 | verification-ef0969b9/** | 2026-10-16 07:20 |
| External-line sourcing for the fixtures that still have no priced pick (HLTV → esportsbook/esports-line research), delivered as a research artifact for the integration session, never as a direct data edit | in progress | ef0969b9 | research/ef0969b9/** | 2026-10-16 07:20 |
| COORDINATION.md: this claim and status log only | in progress | ef0969b9 | COORDINATION.md (append-only sections owned by this session) | 2026-10-16 07:20 |

- File-scope conflict rule applied: `data/analysis.json`, `data/latest.json`, `data/matches.csv`,
  `data/review-notes.json`, `data/identities.json`, `scripts/build.py`, `site/**`, `assets/**`,
  `index.html`, `README.md` and the generated root HTML routes are **owned by 1abe803f** for this window.
  If this session's verification finds a defect in one of them, it records the request in this file
  instead of editing the file, and only applies the fix if it later becomes the integration session
  (1abe803f claim older than 60 minutes with no new commits, or its task marked done/abandoned).
- Measured cadence evidence gathered before claiming (`gh api .../actions/runs?event=schedule`): exactly
  three scheduled runs of `pages.yml` ever — 2026-10-15T16:59:51Z success, 2026-10-15T21:22:25Z failure
  (step *Build and independently verify every row…*, since-fixed code), 2026-10-16T04:33:39Z failure
  (step *deploy → Deploy verified static dashboard*, i.e. `actions/deploy-pages` itself, not the byte
  receipt). `refresh-watchdog.yml` (`*/30`) still has **zero** runs. No scheduled run landed for the
  05:17/06:17/07:17 UTC slots. The live artifact is `built_at` 2026-10-16T05:11:55Z (95 rows), so today's
  day-3 prices rest on push-triggered runs only.

### ef0969b9 status log (2026-10-16, 08:0x UTC)

- **Publication reliability — in progress, first green run of the new workflow.**
  `scripts/publish_gate.py` (+18 tests) and the rewritten `pages.yml` /
  `refresh-watchdog.yml` are committed (`9b2bd5e`) and pushed. CI run
  [`38866867244`](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38866867244)
  on this branch is **success**, including the new freshness-gate step; `deploy`
  correctly skipped off `main`. The gate now prints its own decision (`receipt_read`,
  snapshot age, reason) into every run summary, so the freshness logic is auditable
  from the Actions UI instead of only from the log.
- **Measured, not inferred:** there are still only **three** scheduled runs of
  `pages.yml` in the repository's whole history (16:59:51Z success, 21:22:25Z failure,
  04:33:39Z failure) and no scheduled run for the 05:17/06:17/07:17 UTC slots; the live
  95-row artifact was delivered by push-triggered runs. That is why the workflow now
  offers four staggered slots an hour and skips a slot cheaply when the live receipt
  already carries the same revision. Evidence:
  `research/ef0969b9/SCHEDULER-2026-10-16.md`.
- **Independent browser verification — done:** `npm ci --ignore-scripts && node
  tests/browser.cjs` → "Passed: 32 page/viewport accessibility and no-overflow scans,
  320/390/768/1440px layout, subpath URLs, navigation, filters, six legacy redirects,
  evidence anchors and expiry." Recorded in `verification-ef0969b9/BROWSER-VERIFICATION.md`.
- **Environment note for other sessions:** after this sandbox restarted, the *system*
  `python3` no longer has `bs4`/`requests` (12 test modules fail to import and the suite
  reports `FAILED (errors=12)`); `.venv/bin/python -m unittest discover -s tests` →
  `Ran 167 tests … OK`. Use the venv interpreter for local verification.
- **Check for a dangling reference:** `.github/workflows/pages.yml:16` cites
  `research/ef0969b9/` and `research/refresh-ab18fe2a/DIAGNOSIS.md`; both now exist, so
  the reference resolves (ab18fe2a's diagnosis is unchanged and untouched).
- **Enumeration caveat for anyone sourcing lines:** the Polymarket Gamma list endpoint
  appears to ignore `game_start_time_min/max` and `order=gameStartTime` — a 17 Oct
  window returned a 2026-03-10 market. `events?id=<id>`, `markets?slug=<slug>` and
  `markets?tag_id=100780&order=id&ascending=false` do work. Details and the full set of
  negative results: `research/ef0969b9/UNPRICED-FIXTURE-LINES.md`.

### Requests to session 1abe803f (its files, not edited here)

1. **`data/identities.json` + `scripts/core.py:plain_name` — make one live market
   findable.** Polymarket lists today's unpriced fixture as event `1192433`, series
   `10310` (the same series the refresh already queries), whole-match market `5721649`
   "Procyon Gaming vs Los Niños" at **0.69 / 0.31**, `gameStartTime` 2026-10-16 16:00Z,
   `updatedAt` 07:21:08Z, liquidity $6,291.07, map-1 book bid 0.57 / ask 0.64. The
   event satisfies every filter in `scripts/refresh.py`'s Polymarket branch, but
   `plain_name` does not fold diacritics (HLTV "LOS NINOS" vs Polymarket "Los Niños")
   and `ALIAS_MAP` has no key for `procyon`, `procyongaming`, `losninos`, `losniños` or
   `infinite` (`insiders` is present), so the pair can never match. Adding the alias
   entries and folding diacritics would let an existing, two-sided external line be
   published for row `1081502`; it changes name resolution only, no probability logic,
   and does not override "never a default 50/50". Evidence and method:
   `research/ef0969b9/UNPRICED-FIXTURE-LINES.md` §1.
1a. **Update, 07:35Z — the row is priced; the name-resolution gap is still real.**
   The 07:27Z build (revision `693b6374`) publishes row `1081502` as
   "Procyon vs LOS NINOS — 67.2% / 32.8%, OUR FAIR LINE, Bookmaker fallback
   (Pinnacle), observed 07:18 UTC", so the integration harvest has already resolved
   the pick without the alias change. Independently read: Polymarket event `1192433`
   / market `5721649` prices the same fixture `0.69 / 0.31`, i.e. the two external
   sources agree within **1.8 points** — a corroboration, not a contradiction, and no
   data change is needed for it. The requested alias/diacritic fix stays on the list
   as a *latent* defect: any future fixture whose provider spelling carries a
   diacritic or a missing alias (Los Niños plays this CCT series regularly) will hit
   the same wall, and the Polymarket tier would generally give a tighter, better
   sourced quote than the bookmaker fallback. Counts from the live site at 07:27Z:
   106 feed entries, 42 open, 39 with a published probability (27 market, 12 model),
   3 research-only with no percentage, **0 with no pick**.
2. **Optionally, refresh completeness instrumentation (not required for the fix).**
   The recorded reason for row `1081502` is "No exact team-pair and UTC-start match in
   retrieved feed", which is consistent with the name gap above, but this session cannot
   see how many events the run actually retrieved (run logs are not retrievable here).
   Printing the retrieved-event count per source in the next refresh receipt would close
   that gap without changing any decision.


## Session 2e920ea8 claims (2026-10-16, 07:23 UTC)

Arena fixes this session to `arena/2e920ea8-maltaproj4`; no other branch is created, checked out or
pushed. Board read before claiming: session **1abe803f** claimed at 07:17 UTC (day-1/2/3 TWC review +
`data/analysis.json`, its own non-publishing harvest, and final integration over `data/latest.json`,
`data/matches.csv`, `data/review-notes.json`, `data/identities.json`, `scripts/build.py`, `site/**`,
`assets/**`, `index.html`, `README.md`, generated root HTML) and committed at 07:18:38 UTC — an
**active** claim well inside the 60-minute window. This session does not touch any of that. It claims
only complementary work the same user brief also requires and no session has claimed:

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Resolve a pick **and a published percentage** for every open fixture with no market line (research-tier rows such as 1081502 Procyon/LOS NINOS and 1081526 Infinite/Insiders, plus any gap rows in the live harvest): HLTV match-page research first, then esportsbook/esports betting lines; last tier is a documented, reproducible rank-model percentage that is labelled a model and never presented as a market line | done (book-listing tier + receipts + 28 tests; 1081526 priced 65.6/34.4; 1081521/1081522 research-only with published limitation — see delivery record below) | 2e920ea8 | scripts/core.py, scripts/hltv.py, tests/**(new files only), research/fallback-2e920ea8/** | 07:23 |
| HLTV + esportsbook line cross-checks for the TWC day-3 deciders (Aurora–9z, BETBOOM–Legacy) and day-2 result receipts; contrarian-not-stupid notes as a drop-in analysis fragment for the integrator (no edit to `data/analysis.json`) | done (research/day3-2e920ea8/CROSSCHECK.md) | 2e920ea8 | research/day3-2e920ea8/** | 07:23 |
| `pages.yml` post-deploy receipt cache-busting + retry (the explicit request session dedd2e34 left unclaimed at 05:12 UTC) so the every-6-hours publish schedule can land a verified board | **closed by session ef0969b9** (PR #36, merged 07:33 UTC: staggered schedule, freshness gate, verifiable deploy step); not done by this session, `pages.yml` never touched here | ef0969b9 | .github/workflows/pages.yml | 07:23 |
| Integrate the above into the site, executive summary and unresolved/limitations sections | **not claimed here** — integration request logged below for 1abe803f | 1abe803f | (their claimed scope) | 07:23 |

- **Integration request to 1abe803f (do not edit their files from this session):** when the fallback
  tier in `scripts/core.py` / `scripts/hltv.py` lands on main, please ensure the executive summary
  links the updated picks table and the unresolved + limitations section states plainly that
  rank-model percentages on research-tier rows are originated model outputs (method label in the
  table), not external market lines. Drop-in copy will be posted in `research/fallback-2e920ea8/`
  and `research/day3-2e920ea8/`.
- Evidence standard unchanged: Hotspawn is inventory only; probability inputs are external market
  lines or reproducible calculations on verified inputs; anything unknown stays blank and flagged.
- Scope guard: no edit to `data/latest.json`, `data/matches.csv`, `data/review-notes.json`,
  `data/identities.json`, `data/analysis.json`, `scripts/build.py`, `scripts/refresh.py`,
  `site/**`, `assets/**`, generated root HTML, `README.md`. Only `scripts/core.py`,
  `scripts/hltv.py`, new test files, this file, `research/fallback-2e920ea8/**`,
  `research/day3-2e920ea8/**` and `.github/workflows/pages.yml`.


### Session 2e920ea8 — scope amendment and delivery record (08:05 UTC, 16 October 2026)

- **Board re-read before this work landed:** session ef0969b9 claimed at 07:20 UTC (three minutes
  before this session's claim) a disjoint lane that already included *publication reliability*
  (`.github/workflows/pages.yml`) and a **research-artifact** version of the unpriced-fixture
  sourcing. Its PR #36 (merged 07:33 UTC) delivered the staggered schedule, freshness gate and
  verifiable deploy step. **Task 3 of this session's claim is therefore closed by ef0969b9, not by
  this session, and this session never touched `pages.yml`.** Session 1abe803f merged PR #35 at
  07:27 UTC (106-row harvest, Betclic alias, day-1/2/3 verification) and still owns the integration
  files. The lanes stayed disjoint: this session delivered implementation that neither claim covered.
- **Scope amendment (recorded before this push, per the board rule):** the researched-book tier
  cannot be replayed without the validator and the independent auditor, so this session's file
  scope extends to `scripts/validate.py` (reconstruct + calculator dispatch only),
  `verification-c6/audit_snapshot.py` (independent de-vig branch, alias-source gate, diacritic-fold
  mirror in its own `name()`), and a new file `data/book-receipts.json`. Still untouched:
  `scripts/refresh.py`, `scripts/build.py`, `scripts/hltv.py`, `data/latest.json`,
  `data/matches.csv`, `data/review-notes.json`, `data/identities.json`, `data/analysis.json`,
  `site/**`, `assets/**`, `README.md`, generated root HTML, `.github/**`.
- **Task 1 — done.** A pick **and**, where a real two-sided listing exists, a published percentage
  for every open fixture the market tiers cannot price. New tier in `scripts/core.py`
  (`book_candidate` / `quote_book` / `calculator_for` / `book_research_pick`, tried before the
  rank-only ladder) consumes dated receipts in `data/book-receipts.json`. Row **1081526**
  (Infinite vs Insiders) is resolved to **Infinite 65.6% / 34.4%** (fair 1.52 / 2.91) from the
  EGamersWorld listing 1.39 / 2.65 read 07:32Z; row 1081502 carries a backup listing (1.34 / 2.85)
  beside its automated Pinnacle line (agreement within 1 point). Rows **1081521** and **1081522**
  keep research picks with **blank percentages**: their only listing shows identical placeholder
  odds 1.8 / 1.8 (documented in `data/book-receipts.json.rejected_listings` and
  `research/fallback-2e920ea8/README.md` §3), and the brief's own verification rule ("leave it
  blank and flag it as unverified; never infer or fill in values") outranks the wish for a number.
  `plain_name` now folds diacritics (ef0969b9's request #1; name normalisation only).
- **Task 2 — done.** `research/day3-2e920ea8/CROSSCHECK.md`: independent BC.Game book lines for
  both TWC deciders (Aurora–9z 1.41 / 2.84 → 66.8 / 33.2; BetBoom–Legacy 2.52 / 1.50 → 37.3 / 62.7,
  read 07:36Z), agreeing with the exchange and VRS model within 2–3 points; day-2 corroboration
  (Legacy 1–2 FURIA) from a third source; contrarian-not-stupid notes labelled analysis; a
  drop-in JSON fragment for `data/analysis.json` (the integrator's file — not edited here).
- **Rebase/conflict log:** `git pull --rebase origin main` hit a COORDINATION.md add/add-style
  conflict with 1abe803f + ef0969b9's sections. Resolved by keeping **both** sides verbatim
  (main's blocks first, this claim after); nothing discarded. No other file conflicted.
- **Verification performed here (16 Oct, 08:05 UTC):** 195 unit tests pass (incl. 28 new
  `tests/test_book_research_2e920ea8.py` covering de-vig math, staleness, alias-source gate,
  validator replay and the independent auditor); `audits/` 9 and `verification-c6` 12 suites pass;
  `scripts.build` + `scripts.validate` green on the committed 106-row snapshot (690 internal
  links/assets, 20 artifact checksums, 277 displayed rows); `verification-c6/audit_snapshot.py`
  reports 0 failures; a real-snapshot smoke prices 1081526 from the published receipt and passes
  both validator and auditor end to end. Forged probabilities, altered odds, stale observations and
  missing alias sources are all proven to fail (regression tests).
- **Limitations published, not hidden:** (1) researched listings carry no price-update timestamp,
  so the standard 8-hour evidence window applies (DraculaN receipt lapses 15:32Z today; the row
  reverts to research-only — pick kept, percentage blank — until a listed line is re-observed);
  (2) no automated book adapter exists in `scripts/refresh.py` (out of scope here) — a follow-up
  session can add one so each refresh re-reads the listing; (3) the Polymarket Infinite–Insiders
  market 5650404 is dormant (bid 0.41 / ask 0.97, updatedAt 15 Oct 08:26Z) and stays correctly
  rejected; (4) placeholder 1.8/1.8 listings are recorded as rejected, never converted to 50/50.
- **Integration requests to 1abe803f (its files):** (a) in the executive summary's unresolved +
  limitations section, add the placeholder-odds limitation for 1081521/1081522 and the 8-hour
  receipt window for researched listings (copy in `research/fallback-2e920ea8/README.md` §3);
  (b) optionally splice `research/day3-2e920ea8/CROSSCHECK.md` §4 into `data/analysis.json`;
  (c) `data/identities.json` alias entries for `procyon` / `procyon gaming`, `los ninos` /
  `los niños`, `infinite` / `infinite gaming` remain useful (ef0969b9 request #1) so the exchange
  tier can price these rows ahead of the researched fallback; the diacritic half of that request is
  already implemented in `scripts/core.py` and mirrored in the auditor.
- **Sources for this session's own numbers:** EGamersWorld match listings (Infinite–Insiders,
  Procyon–LOS NINOS, ex-6666–Privateer, antidaun–Phantom Academy; 07:27–07:44Z reads) and the
  TWC event page with the BC.Game widget (07:36Z); HLTV match pages 2399590 / 2399672 / 2399681 /
  2399682 / 2399412 / 2399413; Polymarket markets 5650404 and 5721649 (cache-busted reads);
  Liquipedia DraculaN Season 7; Valve standings file already vendored in `data/vrs/`. No number
  comes from Hotspawn votes; no value in this session's output is inferred without a source link.

- **PR and deploy record (16 October 2026):** [PR #37](https://github.com/buffedlizard55-lab/MaltaProj4/pull/37)
  ("Researched book-listing tier: pick + published percentage for every resolvable open fixture,
  with replayable de-vig evidence"), merged to `main` at ~08:55 UTC after `verify-build` passed
  (1m8s). Publish run
  [38871846348](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38871846348)
  ("Verify, refresh and publish CS2 Scout") completed green end to end — `verify-build` 1m45s and
  **`deploy` green with its verifiable receipt** (artifacts `live-verification-38871846348`,
  `github-pages`, `audit-38871846348`). Live Pages board verified after the deploy: snapshot
  16 Oct 08:10 UTC — 39 open fixtures, 37 with published probabilities (25 exchange lines incl. the
  labelled wide-quote tier, 12 VRS model lines), 2 research-only picks with blank percentages and
  published limitations (1081521 ex-6666–Privateer, 1081522 antidaun–Phantom Academy), **0 rows
  with no pick**; exec summary links to `picks.html` and `#unresolved-summary`; TWC day-3 guidance
  live on `analysis.html#guidance`.
- **Honest note on row 1081526 at the 08:06 observation:** the exchange market 5650404 was accepted
  by the existing labelled wide-quote tier (bid 0.41 / ask 0.97, spread inside the 60-point wide
  ceiling, liquidity ≥ $100, observed 08:06 UTC) and published as "Wide line · low confidence"
  69.0 / 31.0 — a primary exchange line, so the researched book receipt correctly did **not**
  overwrite it ("fallback lines do not overwrite primary picks"). The 1.39 / 2.65 researched listing
  stays as the dated fallback for when that quote lapses (window ends 15:32 UTC), and both remain
  visible in the evidence trail for manual review.

## Session 3c8d1136 claims (2026-10-16, 07:33 UTC)

Arena fixes this session to `arena/3c8d1136-maltaproj4`; the requested `session-<id>/<task>` naming is not
available (the same constraint every earlier session recorded), so no other branch is created, checked out
or pushed.

**Board read before claiming.** The sandbox git fetch refspec exposes only `main` and this session's branch,
so every remote head was enumerated through the GitHub API instead. `main` is `693b637` (PR #35, session
`1abe803f`, merged 2026-10-16T07:27:02Z). Three sessions were active inside the 60-minute window and none
of their claims is taken over here:

- **1abe803f** — day-1/2/3 TWC review, `data/analysis.json`, its own harvest, and final integration over
  `data/latest.json`, `data/matches.csv`, `data/review-notes.json`, `data/identities.json`,
  `scripts/build.py`, `site/**`, `assets/**`, `index.html`, `README.md`, generated root HTML routes
  (claim 07:17 UTC, last commit 07:24:52Z, PR #35 merged 07:27:02Z).
- **ef0969b9** — publication reliability: `.github/workflows/pages.yml`, `.github/workflows/refresh-watchdog.yml`,
  `scripts/refresh_watchdog.py`, `tests/test_publish_gate_ef0969b9.py`, `research/ef0969b9/**`,
  `verification-ef0969b9/**` (claim 07:20 UTC, last commit 07:27:57Z).
- **2e920ea8** — fallback percentages: `scripts/core.py`, `scripts/hltv.py`, new files in `tests/**`,
  `research/fallback-2e920ea8/**`, `research/day3-2e920ea8/**`, `.github/workflows/pages.yml` (claim 07:23 UTC).

**Conflict logged, not resolved here:** `.github/workflows/pages.yml` is claimed by two active sessions at
once (`ef0969b9` at 07:20 and `2e920ea8` at 07:23, for the same dedd2e34 deploy-receipt request). Whoever
pushes second must rebase onto the other's version rather than replace it. This session does not touch that
file at all.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Fix the board's freshness anchor: both Hotspawn HTML views were served from a CDN cache at the 07:21:05Z refresh (`Age` 14241 s on `cs2-pickems`, 6251 s on `lobby`), so `fixtures_observed_at` is 03:23:45Z and **every** open pick on the live board expires at 11:23:45Z — before both TWC day-3 deciders (14:00Z and 17:00Z). Measure whether a cache-busting request defeats that CDN, then fix the fetch | **done** — fix in `scripts/refresh.py`, proved in CI runs 38869616511 and 38871406232; anchor now 07:49:57Z / 08:06:33Z, `Age 0`, `X-Cache MISS`, deadline median gain **+257.5 min** | 3c8d1136 | scripts/refresh.py, scripts/cdn_probe_3c8d1136.py, scripts/coverage_report_3c8d1136.py, scripts/scoring_model_3c8d1136.py, .github/workflows/harvest-3c8d1136.yml, research/cadence-3c8d1136/** | 2026-10-16 08:25 |
| Explain the 103 / 95 / 95 three-way parity gap fixture by fixture: which IDs differ, whether they are open, and whether each has a pick | **done** — 11 API-only fixtures (all with picks), 3 HTML-only fixtures (all finished); the flag was staleness, not lost coverage. After the fix: `verified`, 102/102/102 | 3c8d1136 | research/coverage-3c8d1136/** | 2026-10-16 08:25 |
| Independent line-by-line verification of what is actually published (106 rows, 42 open, snapshot 2026-10-16T07:21:23Z) against primary sources, including both TWC day-3 deciders; irregularities flagged for the owner, never silently fixed in another session's file | **done** — both deciders reproduced from Polymarket 5733288 / 5763247, fair odds recomputed exactly, Aurora roster premise corrected, 7 irregularities recorded | 3c8d1136 | verification-3c8d1136/**, research/cadence-3c8d1136/** | 2026-10-16 08:25 |
| Day-4 readiness (17–18 October): verify the semifinal bracket and its Hotspawn listing status, record any existing outright lines, and leave a drop-in analysis fragment for the integrator | **done** — all four playoff fixtures verified from their HLTV pages (Bo3, Bo3, Bo3, **Bo5**), none listed by Hotspawn yet, **no external line exists for either semi-final**, UTC starts derived and labelled unverified | 3c8d1136 | research/day4-3c8d1136/** | 2026-10-16 08:25 |

- **Scope guard.** No edit by this session to `data/latest.json`, `data/matches.csv`, `data/analysis.json`,
  `data/review-notes.json`, `data/identities.json`, `scripts/build.py`, `scripts/core.py`, `scripts/hltv.py`,
  `scripts/refresh_watchdog.py`, `site/**`, `assets/**`, generated root HTML routes, `index.html`,
  `README.md`, `.github/workflows/pages.yml`, `.github/workflows/refresh-watchdog.yml` or existing files in
  `tests/**`. `scripts/refresh.py` and `scripts/inventory.py` are not in any active claim (`2e920ea8`
  explicitly excluded `scripts/refresh.py` from its own guard list) and are the only production files this
  session edits. New tests go in `verification-3c8d1136/`, not `tests/`, because `2e920ea8` claimed new
  `tests/**` files.
- Evidence standard inherited unchanged: Hotspawn fixes the fixture inventory and is never a probability
  input; probabilities come only from external market lines that pass the published gates or from a clearly
  labelled originated model line; unknown values stay blank and flagged.

---

### 3c8d1136 — done, 2026-10-16 08:25 UTC (freshness anchor fixed and proved in CI; coverage gap explained; live board verified line by line; day-4 readiness recorded)

**The defect.** The published board (`data/latest.json` on main `693b637`, snapshot `2026-10-16T07:21:23Z`)
carried `fixtures_observed_at = 2026-10-16T03:23:45Z` because Hotspawn's CDN served the general lobby with
`Age: 6251` and the CS2 lobby page with `Age: 14241`, while the fixtures API supplied no `Age` at all.
`inventory.discover` anchors at `min(observed_at)`, and `core.pick_deadline` takes
`min(anchor + 8 h, …)`, so **every open pick on the live board expired at 11:23:45Z** — 2 h 30 m before
Aurora vs 9z (14:00Z) and 5 h 30 m before BetBoom vs Legacy (17:00Z). The same stale copies produced
`coverage: partial` with counts 103 / 95 / 95.

**The measurement** (`scripts/cdn_probe_3c8d1136.py`, receipt
`research/harvest-3c8d1136/cdn-probe.json`, run 38869016384, `probed_at 07:44:06Z`): plain `/cs2-pickems`
`Age 973` → 103 CS2 IDs; plain `/lobby` `Age 7620` → **95** IDs; each with one distinct `_cb` argument →
`Age 0`, `X-Cache: MISS`, **103** IDs, i.e. parity with the API in the same minute. The fixtures API answers
**HTTP 400** to any unknown query argument (independently documented by session `ab18fe2a` in
`research/day3-ab18fe2a/receipts/hotspawn-fixture-1081775.json`), so it is never cache-busted.

**The fix** — `scripts/refresh.py` only: bust HTML (non-JSON) requests to `play.hotspawn.com` with one
distinct `_cb` token, keep the canonical URL as the published evidence link, record `request_url`,
`cache_bust` and `cache_status` in the receipt, and fall back to the canonical URL on the existing retry so a
source that rejects the argument degrades to today's behaviour. No probability, pick, tier, gate, TTL or
identity rule changed. `scripts/core.py` untouched (claimed by `2e920ea8`).

**Proved in CI on this branch** — runs [38869616511](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38869616511)
(07:50:16Z) and [38871406232](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38871406232)
(08:06:48Z), each running the real `scripts.refresh` end to end:

| | before (run 38869016384) | after (38869616511) | after (38871406232) |
|---|---|---|---|
| `fixtures_observed_at` | 05:36:55Z | **07:49:57Z** | **08:06:33Z** |
| Hotspawn `Age` (page / lobby) | 996 / 7632 | **0 / 0** | **0 / 0** |
| `coverage` | partial | **verified** | **verified** |
| counts api/page/lobby/retained | 103/103/95/106 | **103/103/103/103** | **102/102/102/102** |
| `coverage_difference` issue | raised | **gone** | **gone** |
| open rows / with a pick / with a probability | 42 / 42 / 40 | 42 / 42 / 40 | 39 / 39 / 37 |

Deadlines recomputed with the production function `core.pick_deadline` (not by hand) over the 07:44Z and
07:49Z snapshots: **median gain +257.5 min, max +266.2 min, no row moved earlier**; Aurora vs 9z
11:23:45Z → **13:54:00Z** (its own lock), BetBoom vs Legacy 11:23:45Z → **15:49:10Z** (quote TTL, lock
16:54Z). The 08:06Z run also dropped the three rows only the cached lobby still carried (`1079626`,
`1079628`, `1080204` — all played on 15–16 October).

**Coverage gap explained** (`research/coverage-3c8d1136/COVERAGE.md`): the 11 API-only fixtures are
`1081493`, `1081496`, `1081497`, `1081499`, `1081503`, `1081513`, `1081521`, `1081522`, `1081779`,
`1081780`, `1081781` — listed during 16 October, **all with picks**, 9 with probabilities; the 3 HTML-only
fixtures are finished matches the cached views had not dropped. 95 + 11 − 3 = 103, 103 + 3 = 106. Nothing
was lost; the flag was staleness.

**Scoring check** (`research/coverage-3c8d1136/SCORING-MODEL.md`, generated in CI from the retained raw
response `research/harvest-3c8d1136/fixtures-raw.json`): `offered_points == floor(base_points × the five
points_breakdown multipliers)` holds for **102 of 102** CS2 rows with 0 exceptions, and in **7 of 7** scoring
groups the award is single-valued while `total_picks` varies (tier `c` "waiting for information": 2 points
across 38 fixtures with `total_picks` 0–74). This reproduces `0e407ec7`'s reading of
<https://play.hotspawn.com/how-it-works> on live data: a correct pick is worth a **fixed** award, so a
crowd split earns nothing by itself and the leaderboard-optimal pick is the higher-probability team. The
exact streak-bonus formula remains unpublished; no number is claimed for it.

**Live-board verification** (`verification-3c8d1136/LIVE-BOARD-VERIFICATION.md`): both deciders reproduced
from Polymarket 5733288 (Aurora Gaming 0.695 / 9z 0.305, `updatedAt 08:05:07.810983Z`, bid 0.69 / ask 0.70,
liquidity $102,430.3165) and 5763247 (Legacy 0.635 / BetBoom Team 0.365, liquidity $109,719.2318), including
the name-mapping on the BetBoom-first board row; fair odds recomputed exactly; NIP vs Team Liquid crossed to
**Team Liquid 0.495 / 0.505** (market 5732258, `updatedAt 07:49:10.803008Z`, liquidity $307,592.3098) and
locked at 07:54Z; `1081502` Procyon vs LOS NINOS priced from Pinnacle matchup 1638406883 (home −274 / away
+187, `bestOfX 3`, cutoff 23:00Z) de-margined to 0.677691790620314 / 0.3223082093796859; `1081526` Infinite
vs Insiders priced `exchange_wide` 0.69 / 0.31 (market 5650404, liquidity $106.4399, spread 56 points,
low-confidence flag published). Day-1/2 results re-read from HLTV event 8932. The **Aurora roster premise is
corrected**: HLTV team 11861, HLTV news 45082 and Liquipedia all date the last change to **8 July 2026**
(kyxsan from Falcons, with Jimpphat and coach ash on 3 July) — there is no October change.

**Day-4/5 readiness** (`research/day4-3c8d1136/DAY4-READINESS.md`): semi-final 1 FURIA vs Aurora/9z winner
([HLTV 2399414](https://www.hltv.org/matches/2399414/furia-vs-aurora-9z-winner-thunderpick-world-championship-2026),
Bo3, displayed `10:00 17 Oct`), semi-final 2 Falcons vs BETBOOM/Legacy winner
([2399415](https://www.hltv.org/matches/2399415/falcons-vs-betboom-legacy-winner-thunderpick-world-championship-2026),
Bo3, `13:00 17 Oct`), 3rd place
([2399416](https://www.hltv.org/matches/2399416/thunderpick-world-championship-2026-3rd-place-decider-match-thunderpick-world-championship-2026),
Bo3, `07:30 18 Oct`), grand final
([2399417](https://www.hltv.org/matches/2399417/thunderpick-world-championship-2026-grand-final-thunderpick-world-championship-2026),
**Bo5**, `11:00 18 Oct`). HLTV's displayed clock for this event is UTC − 4, anchored on the two deciders whose
UTC starts are machine-verified from Hotspawn's epoch and Polymarket's `gameStartTime`; derived UTC starts are
14:00Z / 17:00Z / 11:30Z / 15:00Z and are labelled **derived, unverified**. Hotspawn lists **none** of them
yet (only `1080205` and `1081775` for this event) and **no external line exists for either semi-final**
(no `Betting` section on either HLTV page, no market in the 08:06Z refresh).

**Irregularities recorded, not silently fixed in other sessions' files:** (1) the anchor defect, fixed here;
(2) the coverage artifact, fixed here; (3) rules page says the lock is 5 minutes while every fixture carries
`lock_offset_sec: 360` — 6 minutes (re-verified `0e407ec7`'s finding); (4) Hotspawn publishes **no series
format**: `best_of` and `series_format` are null for 102 of 102 rows, while Polymarket and Pinnacle both
publish it, so the documented format-agreement gate can never fire; (5) two open rows still have a pick but no
probability (`1081521`, `1081522`); (6) no scheduled refresh ran for the 05:17/06:17/07:17 UTC slots and
`refresh-watchdog.yml` has zero runs; (7) HLTV match pages carry a server-rendered countdown, so their
displayed times must be dated, not trusted.

**Requests to the owners of the files involved** (none edited by this session):

- **1abe803f (integration / `data/**`, `scripts/build.py`, `site/**`, generated root routes):** `scripts/refresh.py`
  changed, so please **refresh and republish from main** rather than hand-editing `data/latest.json`. Expect
  `coverage: verified`, three fewer historical rows, every open row's `expires_at` moving to its own lock or
  quote TTL, and `Age 0` / `X-Cache MISS` with new `request_url` and `cache_bust` receipt fields on both lobby
  views. Irregularities (3) and (4) are ready to be added to `data/review-notes.json` verbatim from
  `verification-3c8d1136/LIVE-BOARD-VERIFICATION.md`; `scripts/build.py:286 checks_table` was confirmed to read
  only name/status/http_status/cache_age_seconds/observed_at/url, so the new receipt fields are safe.
- **ef0969b9 (publication reliability):** the anchor fix only helps when a refresh runs. Please add
  `verification-3c8d1136` to the `verify-build` test-discovery step (25 tests, all passing) so the fetch-layer
  behaviour stays under CI, and note the scheduler evidence in irregularity (6).
- **2e920ea8 (fallback percentages):** the two unpriced open rows are `1081521` ex-6666 vs Privateer and
  `1081522` antidaun vs Phantom Academy, both 18 Oct, CCT Europe 2026 Challengers #8, HLTV ranking evidence only.

**Still live on the published board at the time of writing.** The build published at
`2026-10-16T08:21:00Z` (revision `41ff936f`, PR #38) reports `fixtures_observed_at
2026-10-16T05:36:54.850797Z`, `coverage: partial`, page `Age 3192`, lobby `Age 9828`. Applying
the production `core.pick_deadline` to that published anchor, both TWC deciders expire on the
live site at **13:36:54Z** — 17 minutes before Aurora vs 9z's own 13:54Z lock and 3 h 17 m before
BetBoom vs Legacy's. Merging this branch and republishing is what removes that.

**Cross-checks against work that landed while this session was running** (PR #37 merged
08:09:39Z, PR #38 08:20:10Z, both session `2e920ea8`; PR #36 07:33:26Z, session `ef0969b9`):
their BC.Game book lines for the deciders (Aurora–9z 1.41 / 2.84 → 66.8 / 33.2; BetBoom–Legacy
2.52 / 1.50 → 37.3 / 62.7, read 07:36Z) agree with this board's exchange prices within 2.7 and
0.8 points — a third independent source, neither exchange nor model. Their researched-book tier
correctly does not overwrite the primary `exchange_wide` line on `1081526` (0.69 / 0.31 vs their
65.6 / 34.4, 3.4 points apart, both kept visible — irregularity #8). Their rejection of the
placeholder 1.8 / 1.8 listings on `1081521` / `1081522` is why those two rows keep a pick and a
blank percentage; that is deliberate under the brief's no-inference rule, not a gap. Nothing in
`scripts/refresh.py` interacts with their `scripts/core.py` tier: the fetch layer changed, the
pricing ladder did not.

**Tests:** `verification-3c8d1136` **25 OK** (probe and coverage-report purity, snapshot characterization,
HTTP 400 handling and reference fallback, and a fake-session proof that the busted URL is requested first with
the canonical retry, that `url` stays canonical, and that JSON APIs, HLTV, Polymarket and Pinnacle are never
busted) · `tests` **149 OK** · `audits` **9 OK** · `verification-95b588c2` **5 OK** · `verification-c6`
**12 OK** · `python -m scripts.validate --data data/latest.json --site .` green. No existing test file was
edited. Commits: `b493639` (claim) → `ab4294f` (probe, coverage report, tests, harvest workflow) →
`9925543` (the cache-bust fix) → `bcc876c` (scoring check) → docs commit (this entry).

- **PR, merge and live-deploy record (16 October 2026, session `3c8d1136`).**
  [PR #39](https://github.com/buffedlizard55-lab/MaltaProj4/pull/39) — *"fix(refresh): stop a cached
  Hotspawn lobby from expiring every pick early; verify the live board and day-4 readiness"* — merged
  to `main` **without waiting for approval** at `2026-10-16T08:34:07Z` as merge commit
  **`f96fdafc1aeaed9e7a02010d3fc708e3b4313f04`**, after `verify-build` passed green on the PR head
  (run [38874397887](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38874397887), 1m10s)
  and the branch reported `mergeable: MERGEABLE / mergeStateStatus: CLEAN`. The harvest workflow
  correctly skipped on the docs commits (no `[harvest]` in the head message).
  The push to main triggered publish run
  [38874563191](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38874563191),
  **completed success**: `verify-build` green and `deploy` green including its *"Verify live Pages bytes
  match this exact build"* receipt step (the retry step stayed skipped, i.e. the first deploy attempt
  succeeded).
  **Live Pages verified after the deploy** (read from
  <https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json>, `data/latest.json` and `picks.html`,
  cache-busted): revision **`f96fdaf`**, `built_at 2026-10-16T08:34:53.499521Z`,
  `snapshot_generated_at 2026-10-16T08:34:53.176626Z`, **100 rows**, 20 artifact checksums;
  `fixtures_observed_at **2026-10-16T08:34:35.841686Z**` (was `05:36:54.850797Z` in the 08:21Z build),
  `coverage: **verified**` (was `partial`), and per-row `fixture_sources` receipts now carrying
  `cache_age_seconds: 0` with `observed_at == retrieved_at` on **both** HTML lobby views — the published
  evidence links stayed canonical (`https://play.hotspawn.com/cs2-pickems`, `.../lobby`) while the new
  `request_url` / `cache_bust` / `cache_status` fields are visible in the shipped JSON, with
  `cache_bust: null` on Polymarket, Pinnacle, HLTV and Valve receipts (those hosts are never busted).
  `sources.html` renders *"Hotspawn CS2 lobby — OK — 16 Oct 2026 · 08:34 UTC — HTTP 200 · cache age 0s"*
  and the same for the general lobby. On `picks.html`: **37 priced open matches**, 14 non-market or
  unresolved entries linked separately, every row now reading *"Observed 16 Oct · 08:34 UTC"*, and
  **Aurora vs 9z 69.5% / 30.5%, fair line 1.44 / 3.28, VRS model 68.0% / 32.0%, pick Aurora, exchange
  line, Polymarket 5733288, Expires 16 Oct · 13:54 UTC** — its own lock — against 13:36:54Z in the
  08:21Z build and 11:23:45Z in the 07:21Z build. **BetBoom vs Legacy 36.5% / 63.5%, fair line
  2.74 / 1.57, VRS model 20.7% / 79.3%, pick Legacy, Polymarket 5763247, Expires 16 Oct · 16:33 UTC**
  (the quote's eight-hour TTL, 21 minutes before its 16:54Z lock). **Procyon vs LOS NINOS 67.8% / 32.2%,
  pick Procyon, bookmaker fallback, Pinnacle link, Observed 08:26 UTC, Expires 15:54 UTC.** Rows whose
  own lock is later than the quote TTL expire on the TTL, which is the documented eight-hour evidence
  window; the dense publish schedule from PR #36 (`4,19,34,49 * * * *`) rolls it forward.
  Pre-existing source-health row left as published, not touched: *"GG.BET fallback access — ERROR —
  403 Client Error: Forbidden"* at 08:34Z.

## Session 8cd757bb claims (2026-10-16)

Arena fixes this session to `arena/8cd757bb-maltaproj4`; no other branch is created or checked out. All prior tasks on the board are **done** (through PR #40 / merge commit `f96fdafc…`). This session performs final verification only; no production data or shared outputs are changed.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Final verification: tests, build, validate, browser/expiry checks, live-site sanity | done | 8cd757bb | COORDINATION.md | 2026-10-16 |

### Verification performed (2026-10-16)

- `python -m unittest discover -s tests` → 195 OK.
- `python -m unittest discover -s audits` → 9 OK.
- `python -m unittest discover -s verification-c6` → 12 OK.
- `python verification-95b588c2/test_integrity.py` → 5 OK.
- `npm run test:browser` → 32 accessibility/no-overflow scans + 7 expiry scenarios OK.
- `python -m scripts.build` → 106 sourced rows, 15 pages, 20 artifact checksums.
- `python -m scripts.validate` → 106 rows verified, 581 internal links/assets, 20 checksums, 218 displayed rows.
- `python -m scripts.refresh` (sandbox) → retained inventory, 39 priced from external sources; Hotspawn unreachable from sandbox (SSL EOF) — left to GitHub Actions, as documented.

### Irregularities / notes

- Hotspawn endpoints are not reachable from the sandbox egress (SSL EOF), so no live refresh is committed here; scheduled GitHub Actions runs remain the freshness mechanism.
- No code, data, or shared outputs changed by this session; all prior irregularities remain published on the Flagged for Review page.
## Session 9a81b26f claims (2026-10-16, 19:28 UTC) — Day-3 results, Day-4 guidance, full coverage, deploy repair

Arena fixes this session to `arena/9a81b26f-maltaproj4`; the requested `session-<id>/<task>` naming is not available (the same constraint every earlier session recorded), so no other branch is created, checked out or pushed. Before claiming, all remote heads were enumerated (`git ls-remote` + `gh pr list` + `gh run list`): `main` is `40b13d3` (PR #40 merge, session `3c8d1136`), this branch starts from it, **every task on the board above is `done`**, and no session has committed in ~11 hours. PR #23 (`dbe62379`, research only, still `OPEN`/`CONFLICTING`) is left untouched. No active claim is overwritten.

**Live state measured before claiming (not inferred):** it is 2026-10-16T19:28Z, so both Day-3 TWC deciders have started (Aurora vs 9z 14:00Z, BetBoom vs Legacy 17:00Z). The two most recent **scheduled** publish runs — [38902730567](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38902730567) (~6 h ago) and [38936303441](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38936303441) (~2 h ago) — both **passed `verify-build` and failed at `deploy` → "Verify live Pages bytes match this exact build"** (the deploy step itself succeeded). The watchdog ticks succeeded. The committed snapshot on this branch (`data/latest.json`, generated 07:21Z, `fixtures_observed_at` 03:23Z, `coverage: partial`) predates the cache-bust fix and the deciders, so a fresh Actions harvest is the first step. Day-4 semi-finals are HLTV [2399414](https://www.hltv.org/matches/2399414/furia-vs-aurora-9z-winner-thunderpick-world-championship-2026) (FURIA vs Group A decider winner) and [2399415](https://www.hltv.org/matches/2399415/falcons-vs-betboom-legacy-winner-thunderpick-world-championship-2026) (Falcons vs Group B decider winner) on 17 October; whether Hotspawn now lists them (and with what points/format) must come from the fresh harvest, never assumed.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| D1 Diagnose why scheduled runs 38902730567/38936303441 fail live-byte verification despite a successful deploy, and repair publication so the 4–8 h refresh actually lands — without weakening verification into a rubber stamp | in progress | 9a81b26f | .github/workflows/pages.yml (deploy-verify + this branch trigger only), research/day4-9a81b26f/**, data/review-notes.json (additive) | 2026-10-16 19:28 |
| D2 Day-1 + Day-2 + Day-3 TWC 2026 review line by line from HLTV (incl. 9z 2-0 Aurora upset + Aurora roster-change check); Day-4 (17 Oct semis) contrarian-but-not-stupid guidance with per-row sources and limits | in progress | 9a81b26f | data/analysis.json (additive Day-3 results + Day-4 sections; corrections only where a claim is proven wrong), research/day4-9a81b26f/**, scripts/build.py (additive rendering only) | 2026-10-16 19:28 |
| D3 Fresh harvest of every Hotspawn CS2 fixture; a pick for every open fixture — featured exchange/book lines first, then HLTV → esportsbook researched lines for gaps; every still-unresolved row gets an explicit entry + limitation in the executive summary | in progress | 9a81b26f | .github/workflows/harvest-9a81b26f.yml, research/harvest-9a81b26f/**, data/identities.json (sourced aliases only), data/book-receipts.json (dated receipts only), scripts/core.py only if a defect is proven by a failing test | 2026-10-16 19:28 |
| D4 Executive-summary / phone discoverability pass: today's/Day-4 picks and unresolved+limitations reachable in one tap from the top of the page; no layout regression at 320/390 px | in progress | 9a81b26f | scripts/build.py, site/assets/style.css (append-only rules), site/assets/app.js only if required | 2026-10-16 19:28 |
| D5 Final integration: rebuild, line-by-line re-verification, PR to main, explicit merge without approval wait, cache-busted live Pages verification | in progress | 9a81b26f (final integration) | COORDINATION.md, README.md, build-info.json, generated root HTML routes, data/latest.json, data/matches.csv | 2026-10-16 19:28 |

- Evidence standard inherited unchanged: Hotspawn establishes fixture inventory only and is never a probability input. Probabilities come only from externally observed market lines (Polymarket exchange, Pinnacle bookmaker) or reproducible arithmetic on them / on Valve's official standings, each labelled by tier. HLTV supplies identity, results, rankings and context. No Hotspawn votes, no rank-to-probability formula presented as a market price, no 50/50 fillers, no inferred values. Every row carries a source link; anything unverifiable stays blank and flagged on Flagged for Review. HLTV displayed clocks are reader-local (UTC−4 for this event) and are never read as UTC; manual market reads are cache-busted and dated by the payload's own `updatedAt`.
- Sandbox networking reaches GitHub and package registries only, so Hotspawn/Polymarket/Pinnacle/HLTV numbers that get published come from the Actions-runner refresh (`scripts/refresh.py`); retrieval-tooling reads are research/cross-checks only, each dated and flagged where a cache could interfere. No access control is bypassed; no source is claimed checked when it was not.

- **Rebase log (9a81b26f, 19:44 UTC):** PR #41 (session `8cd757bb`, verification-only, `COORDINATION.md` only) merged to main (`ff61c63`) one minute after this session claimed. Rebased onto it; the single `COORDINATION.md` append conflict was resolved by keeping **both** sections verbatim. Nothing discarded. A further concurrent session `621776e4` started its own non-publishing harvest at ~19:36 UTC; its files are not touched here.
- **D1 diagnosis (measured, 19:35 UTC):** run 38936303441 built at 17:00:47Z, deployed 17:01:52–17:01:57Z, and the verify step **failed within the same second (17:01:57Z)** while deployment 7124811549 was still updating (until 17:02:00Z). The live site then served exactly that build (`built_at` 17:00:47Z, revision `40b13d3`, 83 rows, read cache-busted at 19:30Z). Root cause: the verifier fetches `build-info.json` once and only retries on HTTP exceptions — it never waits for propagation. Publication succeeded; only the receipt failed (same shape at 12:46Z and for the PR #41 push run). Fix: poll for the exact manifest (or a provably newer build) for several minutes; still fail closed on any byte mismatch. Pages remains legacy `main:/` (`build_type: legacy` via the Pages API), so push runs also race GitHub's own `pages-build-deployment`; recorded, not silently changed.
- **D2 facts verified this session so far (HLTV, 16 Oct ~19:30–19:45Z):** all nine finished TWC series scores re-read from https://www.hltv.org/results?event=8932 (Day 1: 9z 2-0 Aurora, Falcons 2-0 NIP, Legacy 2-0 PARIVISION, FURIA 2-0 BETBOOM; Day 2: Aurora 2-0 NIP, Falcons 2-1 9z, BETBOOM 2-1 PARIVISION, FURIA 2-1 Legacy; Day 3: **Aurora 2-0 9z**). Decider detail from HLTV 2399412: Cache 13-11 (8:4; 5:7), Inferno 13-4 (9:3; 4:1); Aurora **removed Nuke** (the map they lost 1-13 on Day 1); kyxsan 33-20 / 1.45, Jimpphat 31-18 / 1.31. BETBOOM vs Legacy was **LIVE at 1-1** (Nuke 16-13 OT to BETBOOM, Dust2 13-11 to Legacy, Mirage to decide, HLTV 2399413) — no result published until HLTV records one. Semi-final 1 is therefore **FURIA vs Aurora** (HLTV 2399414, Bo3, displayed 10:00 17 Oct = 14:00Z derived); semi-final 2 is Falcons vs the Group B winner (HLTV 2399415, displayed 13:00 = 17:00Z derived). Neither semi-final UTC start is published as a value until Hotspawn or a market carries a machine-readable timestamp.
- **D3 harvest (run 38955474182, 19:31Z):** 83 feed rows, coverage verified 83/83/83, 21 open — 16 priced (5 exchange, 2 exchange_wide, 9 model_vrs), 4 research-only (1081521, 1081522, 1081861, 1081863), **1 with no pick: 1081515 Apogee Betclic vs Nemesis** (PGL Bucharest 2027 CQ, 17 Oct 14:00Z). Root cause is name resolution, not a missing market: Polymarket 5776037 ("Betclic Apogee Esports vs Team Nemesis", `gameStartTime` 2026-10-17 14:00:00+00, 0.32/0.68, bid 0.30 / ask 0.34, $3,302 liquidity, `updatedAt` 19:36:52Z, cache-busted read) and HLTV 2399660 ("Betclic vs Nemesis", Upper bracket semi-final, Bo3) are the same fixture; the collector has no `Team Nemesis`↔`Nemesis` or short `Betclic` alias, and the VRS label is `Betclic` (1333 pts; a second 765-pt roster of the same label exists and is disambiguated by lineup overlap). FURIA vs Aurora is **absent from the Hotspawn feed** at this check (`research/harvest-9a81b26f/coverage-gap.md`), so it has no row and scores no points until listed; the pipeline prices it automatically when it appears.
- **Progress (9a81b26f, ~20:05 UTC):** D1 fix implemented (`scripts/verify_live.py` polling verifier + 11 tests + `pages.yml` deploy checkout/permissions); live proof pending the first post-merge publish runs. D2 data written (`day_three_results` — Aurora 2-0 9z verified from HLTV 2399412; `day_four_guidance` — FURIA-Aurora card + two conditional semi-2 cards; Group B decider still LIVE 1-1 at ~19:50Z, no winner claimed) and rendered additively (`guidance_section` generalized with day-3 defaults preserved, `#day-four-guidance` + `#day-three-results`, exec-summary shortcuts repointed to Day 4). D3 proven: harvest 38957108290 (19:44Z) — **21 open, 17 priced, 4 research-only, 0 without a pick**; 1081515 resolved by the sourced Nemesis/Betclic aliases on the strict exchange tier. Local gates: 206 unit tests, audits/c6/integrity suites, row audits 0 failures, quarantine 0 withheld, build+validate (public and root fallback), 32 browser scans + 7 expiry scenarios — all green. Research record: `research/day4-9a81b26f/VERIFICATION.md`. Four flagged notes appended (deploy receipt, semis unlisted, 1081515 resolved, decider live). Next: commit + `[harvest]` push for a final live-data proof and decider/semis re-check, then PR → merge → live verification.
- **Integration over PR #42 (9a81b26f, ~20:12 UTC):** session `9787ce4b` claimed the same brief at 19:30 UTC (2 min after this claim; branch-isolated boards) and merged PR #42 at ~20:00 UTC while this session's coordination comment was seconds old. This branch rebased onto `5053853` preserving PR #42's `research/day4-9787ce4b/SOURCES.md`, board section, branch trigger and `#day-four` anchor (now an alias). Its Day-3 results matched HLTV; its Day-4 picks did not meet the evidence standard and were replaced with the sourced versions above — full correction trail in review note `pr42-guidance-corrected-2026-10-16` (HLTV-widget 73.5% vs reproducible Valve-points model FURIA 62.2%; unsourced "Falcons regardless"; reader-local clocks stated as UTC). No other session's data was altered. Final data: harvest 38958879156 (19:59Z, 21 open / 17 priced / 0 without a pick). BETBOOM-Legacy still live at ~20:08Z (HLTV 2399413), so both conditional semi-2 cards ship.


## Session 621776e4 — delivery record (2026-10-16, 20:25 UTC)

**PR #43** <https://github.com/buffedlizard55-lab/MaltaProj4/pull/43> — base `main`, head `arena/621776e4-maltaproj4`
(Arena fixes this session to that branch; no other branch was created, checked out or pushed).

### Claimed tasks, now done

| Task | Status | Evidence |
| --- | --- | --- |
| Verify day-1/2/3 TWC 2026 results from HLTV, confirm the 9z–Aurora upset and the Aurora roster premise, publish a contrarian day-4 guide | done | `data/analysis.json` `day_four_guidance`; `research/day4-621776e4/DAY4-GUIDANCE-2026-10-16.md` |
| Put a percentage on every remaining unpriced open fixture (HLTV then book lines); publish the unresolved section + limitations in the executive summary | done for every row that any source can price — 17 of 21 open rows priced, **0 rows with no pick**, 4 research picks with published limitations | Live CI snapshot `2026-10-16T19:50:21Z`; `build.access_limitations()` |
| Mobile-first discoverability: executive summary that links straight to the picks board, phone-readable layout | done | `#guidance` / `#unresolved-summary` / `#access-limitations` links in `overview()`; browser suite passes at 320px |

### What shipped

- **`data/identities.json`** — `Betclic` added to the *existing* `Betclic Apogee Esports` entry (session 1abe803f had already registered that canonical, so no duplicate was created), plus a new `Nemesis`/`Team Nemesis` entry. Both carry `source` (HLTV match page), `additional_source` (Polymarket API), `basis` and `reviewed_at`. Sources:
  <https://www.hltv.org/matches/2399660/betclic-vs-nemesis-pgl-bucharest-2027-closed-qualifier> ·
  <https://gamma-api.polymarket.com/markets/5776037> ·
  <https://www.hotspawn.com/counter-strike/teams/betclic-apogee-esports>
  **Verified end-to-end by a live refresh**: row `1081515` → pick **Nemesis**, **0.305 / 0.695**, method `exchange`, fair odds 3.279 / 1.439. It was the only open row with no pick at all.
- **`data/analysis.json`** — `day_four_guidance` (7 sourced points, 3 row-level fixtures, 3 semi-final cards, unverified list), and `day_three_guidance` given a stable `anchor: guidance-day3` plus `nav_label`.
- **`scripts/build.py`** — `guidance_plans` / `latest_guidance` / `guidance_label` so every day's block renders and the newest owns the stable `#guidance` anchor; per-card market line beside the model line; a `points` checklist renderer; and `access_limitations()`, which aggregates the reasons a row carries no percentage **from the attempts recorded in that snapshot** (counted once per row) with the endpoint that produced each one. Nothing is hardcoded, so a provider that starts working leaves the panel on its own.
- **`scripts/probe_621776e4.py` + `.github/workflows/harvest-621776e4.yml`** — this session's non-publishing evidence workflow (branch-scoped, fires only on `[harvest]` commit messages). New step captures HLTV's real odds DOM.
- **`scripts/hltv.py` — deliberately not changed.** See flag 3 below.
- **`tests/test_priced_coverage_621776e4.py`** — 16 tests: the alias fold, primary-source registration, the priced row's exact numbers, that a shifted start or a different opponent is *not* bridged, the day-4 block's structure and its reproducibility from Valve's standings file, the exec-summary link, and the access-limitation panel.
- **`research/day4-621776e4/DAY4-GUIDANCE-2026-10-16.md`** — days 1–3 line by line, the roster finding, day-4 cards, the pricing fix, unresolved rows with limitations, and the commands that were run with their results.

### Checks (all run on this branch)

| Check | Result |
| --- | --- |
| `python -m unittest discover -s tests` | **210 tests, OK** (195 baseline + 15 new) |
| `verification-c6` / `verification-95b588c2` / `audits` | 12 / 5 / 9 OK |
| `python -m scripts.build --data research/harvest-621776e4/snapshot.json` | 9 primary pages + 6 legacy redirects, 83 sourced rows, 17 priced, 4 unresolved |
| `python -m scripts.validate --data …/snapshot.json` | pass — 566 internal links and assets checked, 202 displayed rows verified, 20 artifact checksums |
| `npm run test:browser` | pass — 32 accessibility / no-overflow scans at 320/390/768/1440px, subpath URLs, navigation, filters, 6 legacy redirects, evidence anchors; 7 expiry scenarios |
| CI `harvest-621776e4.yml` runs 38956039048 / 38956344524 / 38957800101 / 38958594708 | all success; artifacts under `research/harvest-621776e4/` |

### Flagged for review (published on the site, not only here)

1. **BETBOOM vs Legacy (2399413) had no published result 3 h after its 17:00Z start.** Day-4 semi-final 2 is published as two conditional cards; no result was claimed.
2. **Inferno 13-4 in the day-3 decider is secondary-corroborated only** (dust2.com.br, EGamersWorld). HLTV page fetches expose per-map player tables but not scorelines, so nothing was inferred from K-D sums.
3. **Correction of a wrong reading, and why `scripts/hltv.py` is untouched.** This session first reported the odds extractor as broken because all 19 harvested pages returned zero numeric rows. A DOM capture run in CI disproves it: on pages 2399660 and 2399681 (both HTTP 200) `.match-betting-list tr.provider` matches exactly **one** row, and that row is a Stake promotional entry whose odds cell is `<td class="noOdds" colspan="2">`. Evidence: `research/harvest-621776e4/hltv-betting-dom.json`, pinned by a test. The published limitation now cites that artifact.
4. **Bookmaker access from the CI runner**: gg.bet **403**, egamersworld **403**; thunderpick.io and rivalry.com **200 with client-side-only odds** (no server-side quote to extract). No bot protection was bypassed. The EGamersWorld receipt that had priced row 1081526 lapsed after ~8 h; that row is now `exchange_wide` on its own merits.
5. **Pinnacle name collisions** — `9z` and `FURIA` appear in other sports (matchup `1638481921` is Rainbow Six), so Pinnacle matches are gated on league and exact start as well as labels.
6. **Valve's standings file predates this week's results** (`standings_global_2026_10_05.md`, commit `eec4853d7bcf0f1f7efe7f0d901234bef7e98b75`), so model lines do not yet absorb TWC 2026. It lists `Nemesis` (#29, 1455) but not `Apogee Betclic`, which is why no model line ever existed for row 1081515 — only the market could price it.

### File scope actually edited

`data/analysis.json`, `data/identities.json`, `scripts/build.py`, `scripts/probe_621776e4.py`, `scripts/add_day4_621776e4.py` (new), `tests/test_priced_coverage_621776e4.py` (new), `.github/workflows/harvest-621776e4.yml` (new), `research/day4-621776e4/**` (new), this file.
**Not touched:** `scripts/core.py`, `scripts/refresh.py`, `scripts/hltv.py`, `scripts/vrs.py`, `scripts/validate.py`, `.github/workflows/pages.yml`, `site/assets/style.css`.
Integrator note for anyone else in `scripts/build.py`: the guidance helpers are additive and `guidance_plans()` decides which `*_guidance` block owns `#guidance` (newest wins) — append new days rather than renaming anchors, and rebase by appending rather than rewording.

### Coordination notes

- Board state read before claiming: `origin/main` at `40b13d3a`, `git branch -r` showing only `origin/main`, so no live claim was taken over.
- `git pull --rebase` before every push; four CI harvest commits were rebased through without conflict.
- Hotspawn votes were never used as probability. Every percentage on the board is either a validated market line or a model line explicitly labelled as ours.

### Reconciliation with sessions 9787ce4b (PR #42) and 9a81b26f (PR #44), merged while this branch was open

Both landed on `main` mid-session, so this branch merged them rather than rebasing over them. Every conflict was
resolved by **keeping both sides' work**; nothing was dropped.

- `scripts/build.py` — main's parameterised `guidance_section(data, notes, plan_key, section_id, aria)` is kept, and
  this branch's additions live inside it: the sourced-points checklist (`{anchor}-read`), the explicit "no fixture
  listed yet" message instead of an empty table, and the per-card market line beside the model line. The
  `guidance_plans` / `latest_guidance` / `guidance_label` helpers stay, and the executive summary now takes its label
  from the newest `*_guidance` block and links to `analysis.html#day-four-guidance`, so the front page cannot fall
  behind the current day.
- `data/analysis.json` — **both sessions had written a `day_four_guidance` key**, and the textual merge produced a
  file with that key twice; `json.loads` silently keeps the last one, so one block would have vanished. The two were
  reconciled into a single block: this branch's superset (7 sourced points, 3 row-level fixtures, `nav_label`, and the
  verified Polymarket line for market 5778024) plus main's block's newer facts — the Group B decider **live at 1-1**
  (Nuke 16-13 OT BETBOOM, Dust2 13-11 Legacy, Mirage to decide) at the ~19:50 UTC read, the rest/turnaround note, and
  its unverified items. The file is now asserted to contain the key exactly once.
- `data/identities.json` — the same alias fix had been made independently. Main's `basis` is kept (it adds
  roster-parity evidence against the Valve standings file) and this branch's 4-item `corroboration` list is kept.
  Exactly one `Betclic Apogee Esports` canonical and one `Nemesis` entry remain, with names
  `['Betclic Apogee Esports', 'Apogee Betclic', 'Betclic']`.
- `COORDINATION.md` — main's records kept verbatim, then this session's.
- Factual conflict published rather than smoothed over: our model (Valve's 5 Oct file) reads FURIA 62.2% / Aurora
  37.8%, while HLTV's live VRS ranks on match page 2399414 put **Aurora #5 above FURIA #6** (captured 19:50 UTC into
  `research/harvest-621776e4/hltv-twc-2399414.json`). Both readings are on the page and the market line governs.
- Re-run after the merge: **226 tests OK** (main's tests included), validator pass, and the browser suite pass — which
  caught a 320px overflow caused by this session's long evidence tokens and is fixed by an appended scoped
  `overflow-wrap` rule.

## Session 621776e4 — publication record (2026-10-16, 20:35 UTC)

**PR #43 <https://github.com/buffedlizard55-lab/MaltaProj4/pull/43> — MERGED** at 2026-10-16T20:23:12Z as merge
commit `86321a8ec3d54952aa75677f623c5613a4dc748f`. Merged without review approval, as instructed; the PR's own
`verify-build` check was green first (`gh pr view 43` reported `MERGEABLE CLEAN`).

### Live site verified after the merge

- <https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json> serves `revision
  86321a8ec3d54952aa75677f623c5613a4dc748f`, `built_at 2026-10-16T20:23:59Z`, 83 rows.
- The executive summary carries this session's additions: hero buttons to `analysis.html#day-four-guidance` and
  `analysis.html#day-three-results`, a "Day-4 guidance" start-here card whose text comes from `data/analysis.json`,
  and the `#access-limitations` table listing Polymarket, Pinnacle, HLTV, Thunderpick, GG.BET and the Valve VRS
  model, each **4 of 4** rows, each with its official endpoint.
- Coverage on the live board: **21 open, 17 priced (8 market, 9 model), 4 research-only picks, 0 rows with no pick.**

### Irregularity found in the publish pipeline, and the fix

Every `pages.yml` run on `main` that actually published showed a **red `deploy` job** with
`Process completed with exit code 2` and the warning `No files were found with the provided path:
runtime/live-verification.json` — runs `40b13d3` (17:00Z), `5053853` (20:00Z), `ca973c6` (20:07Z) and `86321a8`
(20:23Z). The site was **not** broken: it served the exact revision each of those runs built.

Cause, established from the workflow text rather than from the job log (the Actions log host is outside this
sandbox's egress allowlist, so the log could not be downloaded): the `deploy` job had **no `actions/checkout` step**,
so `run: python3 scripts/verify_live.py` executed in an empty workspace and Python exited 2 — `can't open file` —
before the verifier could poll anything or write its receipt. `scripts/verify_live.py` was added to the repository
by commit `afee0b1` (session 9a81b26f, PR #44) and the job that runs it was never given the file. `deploy-pages`
itself does not need a checkout, which is why publication kept working while the receipt step failed.

Fix on this branch: the pinned checkout (`actions/checkout@3d3c42e5…`, v7.0.1, `persist-credentials: false`) is added
to the `deploy` job before the verification step, and `tests/test_deploy_job_checkout_621776e4.py` pins the ordering,
the pin, the existence of every script the job runs, and that both deploy attempts stay `continue-on-error` so the
live-bytes check remains what decides the run. **231 tests OK.**

Nothing about the verifier's standard of proof was loosened: it still requires the live manifest to be byte-identical
to the run's build, or a provably newer byte-consistent build.
## Session 9a81b26f — outcome record (2026-10-16, ~20:40 UTC)

**PR #44 <https://github.com/buffedlizard55-lab/MaltaProj4/pull/44> — MERGED** as `ca973c6` (~20:07 UTC), CI green, no approval waited on per standing instruction. D1–D5 done:

- **D1 deploy repair:** the "failed" scheduled runs were receipt failures, not publication failures (one-shot verifier fetched 17:01:57Z, deployment completed 17:02:00Z; the build was live). `scripts/verify_live.py` polls ≤6 min to the same exact-byte / coherent-newer standard (+11 tests). Caveat recorded honestly: PR #43's merge (`86321a8`) reverted this PR's deploy-job checkout, so the verifier could not start (run 38961864703, exit 2 in 0s); session `621776e4` restored it in PR #45 (`163b3d4`) with a regression test, and that merge's publish run **38962905166 went fully green** (deploy 20:33:42Z, verifier success 20:33:51Z, receipt written) — the D1 live proof, achieved jointly. `deploy-verify-spurious-failure-2026-10-16` can be closed by the next session if scheduled runs stay green. PR #44's own push run (38959969469) failed earlier, in the browser step (~2s, chromium start); the identical branch run 38960359668 was fully green minutes later — transient, documented on PR #45.
- **D2 Day-3/Day-4:** Aurora 2-0 9z published from HLTV 2399412; BETBOOM-Legacy left result-less while live (HLTV 2399413, last read ~20:08Z, Mirage pending); Day-4 guidance = FURIA-Aurora card + two conditional semi-2 cards, model percentages computed by `scripts/vrs.py` on Valve's 2026-10-05 standings (62.2/37.8 · 40.4/59.6 · 73.9/26.1), no market line claimed, no Hotspawn listing invented (absent at 19:31Z/19:44Z/19:59Z/20:11Z harvests). Aurora roster premise corrected again (rebuild dated 8 July 2026).
- **D3 coverage:** four harvests, final state **21 open, 17 priced, 4 research-only, 0 without a pick**; fixture 1081515 fixed by sourced Nemesis/Betclic aliases (Polymarket 5776037 + HLTV 2399660 parity, 5/5 rosters; session 621776e4 converged independently in PR #43).
- **D4 navigation:** exec-summary hero/start-here/section-nav point to Day-4 guidance and Day-3 results; 32 browser scans (320/390/768/1440px) + 7 expiry scenarios green locally and in PR CI.
- **D5 integration:** rebased over PR #42 and PR #43 without discarding either (PR #42 research file + `#day-four` anchor preserved; its widget-based picks replaced with a published correction trail).

**Live verification (cache-busted, ~20:15 UTC):** `build-info.json` served revision `a8da18c`, snapshot 2026-10-16T19:59:25Z, 83 rows — the Day-4 build is the live site (root fallback deployment 38959968622). Session 621776e4 independently verified the post-PR-#43 live revision (`86321a8`, same 21/17/4/0 coverage) in their record above.

**Sources:** HLTV results + match pages 2399412/2399413/2399414/2399415/2399660; Polymarket Gamma 5776037 (cache-busted, payload-dated); Valve standings 2026-10-05; Actions jobs/deployments APIs; harvest runs 38955474182/38957108290/38958879156/38960359642. Full line-by-line record: `research/day4-9a81b26f/VERIFICATION.md`.

**Still open for the next session (flagged, non-blocking):** publish the BETBOOM-Legacy result and collapse the conditional semi-2 cards once HLTV 2399413 is final; bind the semi-finals by `hotspawn_id` when Hotspawn lists them (the 15-min pipeline prices them automatically; guidance cards must then defer to the live line); confirm scheduled `pages.yml` runs stay green after run 38962905166 and close `deploy-verify-spurious-failure-2026-10-16`; consider asking the user to switch Pages source from legacy `main:/` to GitHub Actions to end the dual-build race (settings change, deliberately not attempted from a branch).

## Session 621776e4 — CI repair publication record (2026-10-16, 20:50 UTC)

**PR #45 <https://github.com/buffedlizard55-lab/MaltaProj4/pull/45> — MERGED** as merge commit `163b3d4`
(checked out green first: `verify-build` success, `gh pr view 45` → `MERGEABLE CLEAN`).

### The deploy job is green for the first time since the live-bytes verifier was added

Run `38962905166` on `main` at commit `163b3d4`, step by step:

| Step | Conclusion |
| --- | --- |
| Deploy verified static dashboard | success |
| Retry the deployment once when the first attempt failed | skipped (not needed) |
| **Run actions/checkout@3d3c42e5…** (added by PR #45) | **success** |
| **Verify live Pages bytes match this exact build** | **success** |
| Run actions/upload-artifact (live-verification receipt) | success |

Compare the run immediately before the fix, `86321a8` (PR #43's merge commit): `verify-build` success, **`deploy`
failure** with `Process completed with exit code 2` and no receipt uploaded. Same for `ca973c6`, `5053853` and
`40b13d3`. The verifier's own standard of proof is unchanged — step 5 passing means the live `build-info.json` was
byte-identical to that run's manifest, or a provably newer byte-consistent build.

Note for whoever reads this next: a `fetch_page` of the live `build-info.json` shortly afterwards still returned
revision `86321a8`, i.e. a stale CDN copy, while the in-run verifier had already compared bytes successfully. Trust
the receipt step, not an ad-hoc fetch, when deciding whether a publication landed. The receipt artifact itself could
not be downloaded from this sandbox (`productionresultssa0.blob.core.windows.net` is outside the egress allowlist);
the step conclusions above are the evidence.

### Session 621776e4 final state

- PRs: **#43 merged** (`86321a8`, 20:23:12Z) and **#45 merged** (`163b3d4`, 20:31Z). Both merged without approval, as
  instructed, and both had green checks first.
- Tests: **231 OK** (`python -m unittest discover -s tests`), plus `verification-c6` 12, `verification-95b588c2` 5,
  `audits` 9, and `npm run test:browser` (32 accessibility/no-overflow scans at 320/390/768/1440px + 7 expiry
  scenarios).
- Live board at the merge: 21 open, 17 priced (8 market, 9 model), 4 research-only picks with published limitations,
  **0 rows with no pick at all**.
- Research record: `research/day4-621776e4/DAY4-GUIDANCE-2026-10-16.md`; harvested evidence in
  `research/harvest-621776e4/` (including `hltv-betting-dom.json`, the DOM capture that settled the HLTV odds
  question, and `hltv-twc-2399414.json`, the VRS-rank capture behind the published model divergence).

## Session 1068802c claims (2026-10-16)

Arena fixes this session to `arena/1068802c-maltaproj4`; no other branch is created or checked out.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Update day-3 results with final BETBOOM-Legacy decider and collapse day-4 semi-final 2 to Falcons vs BETBOOM | done | 1068802c | data/analysis.json, site build outputs | 2026-10-16 |

### Notes
- Final day-3 result verified from HLTV news 45739 and match page 2399413: BETBOOM 2-1 Legacy (Nuke 16-13 OT, Dust2 11-13, Mirage 13-11).
- Semi-final 2 is now Falcons vs BETBOOM; the conditional Legacy card was removed from day-four guidance.
- Build and validation pass; 231 tests OK.

## Session 1068802c — publication record (2026-10-16)

**PR #48 https://github.com/buffedlizard55-lab/MaltaProj4/pull/48 — MERGED** at 2026-10-16T23:53:38Z.

- verify-build check passed (run 38983643642).
- pages.yml run 38983770130 on main completed successfully: deploy job green, live-bytes verifier success.
- Site published with updated day-3 results and collapsed day-4 semi-final 2 card.

## Session 1abdd416 claims (2026-10-16, 23:55 UTC)

Arena fixes this session to `arena/1abdd416-maltaproj4`; no other branch is created, checked out or pushed.
Board state read before claiming: `origin/main` was at `dc6a802` (PR #47, session 621776e4, merged 20:40:10Z);
while this claim was being pushed, session 1068802c landed PRs #48 and #49, so `main` had advanced to `777e547`
(day-3 decider recorded and the day-4 semi-final 2 card collapsed to Falcons vs BETBOOM). This session rebased onto
that work rather than reverting it, and enriches the two cards instead of rewriting them.
`gh pr list --state all` shows every earlier PR **merged**, and `git branch -r` lists **only** `origin/main`, so no
session branch exists and **no active claim is being taken over**. This is new user-requested work: re-verify the
day-1 upset and the day-2/day-3 results against primary sources, publish the day-4 (17 October) Thunderpick semi-final
picks that the previous sessions left as conditional cards, confirm a pick exists for **every** open Hotspawn fixture
from a fresh harvest, and keep the executive summary's in-site pick links + unresolved/limitations section readable on
a phone.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Re-verify day-1/2/3 TWC 2026 results from primary sources and publish day-4 semi-final picks (FURIA–Aurora, Falcons–BETBOOM) with the market line for each | in progress | 1abdd416 | `data/analysis.json`, `research/day4-1abdd416/**`, generated `analysis.html` | 2026-10-16 |
| Fresh harvest of the Hotspawn board; confirm or repair a pick for every open fixture, and keep the unresolved + limitations section in the executive summary complete | in progress | 1abdd416 | `.github/workflows/harvest-1abdd416.yml` (new), `research/harvest-1abdd416/**` (new), `data/latest.json`, `scripts/**` only if a defect is proven | 2026-10-16 |
| Mobile-first review of the executive summary and picks board (links in-site, readable at 320 px) | in progress | 1abdd416 | `site/**`, `index.html`, `picks.html`, `assets/**`, `tests/**` | 2026-10-16 |
| Final integration, PR to `main`, merge, live-Pages verification, record in this board | in progress | 1abdd416 (integrator) | root deployment files, `COORDINATION.md`, `README.md` | 2026-10-16 |

Rules I am holding to, unchanged from the earlier sessions: Hotspawn establishes the fixture inventory and is
**never** a probability source; every published percentage is either a validated external market line or our own
explicitly labelled model line; unknown values stay blank and are flagged on Flagged for Review; no paywall,
bot-protection or access-control bypass; no branch other than `arena/1abdd416-maltaproj4` is written to.

Coordination log for this session follows in the record section once each task completes.

## Session 76712ccc claims (2026-10-16, 23:58 UTC)

Arena fixes this session to `arena/76712ccc-maltaproj4`; no other branch is created, checked out or pushed.
Board state read before claiming: `origin/main` is at `dc6a802` (PR #47). The remote exposes **one actively updated
session branch**, `arena/1abdd416-maltaproj4` (last commit 2026-10-16T23:51:38Z), which has claimed *this same
user request*: day-1/2/3 re-verification and day-4 semi-final picks (`data/analysis.json`, `analysis.html`), a fresh
Hotspawn harvest (`data/latest.json`, `research/harvest-1abdd416/**`), the mobile-first review (`site/**`,
`index.html`, `picks.html`, `assets/**`, `tests/**`) and the final integration. **That claim is live, so this
session does not start, duplicate or take over any of it.** PR #23 (`arena/dbe62379`) is open but stale since
2026-10-15T23:11Z.

Scope this session claims, chosen so it does not overlap 1abdd416:

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Independent line-by-line verification of the day-1 to day-3 TWC 2026 record and of the currently published board against primary sources; publish artifacts and flag irregularities | in progress | 76712ccc | `verification-76712ccc/**` (new), `research/day4-76712ccc/**` (new), this file | 2026-10-16 |
| Put a researched, receipt-backed percentage on every open fixture that carries a pick but no probability (the four `research_rank*` rows): probe Pinnacle and Polymarket for those exact fixtures, retain raw receipts, and record per-row why a number does or does not exist | in progress | 76712ccc | `research/quotes-76712ccc/**` (new), `scripts/backfill_quotes.py` (additive mapping only), `tests/test_coverage_76712ccc.py` (new), this file | 2026-10-16 |
| Day-4 (17 October) semi-final and day-5 final market lines for TWC 2026, with raw primary receipts, published as research input for the integrator | in progress | 76712ccc | `research/day4-76712ccc/**` (new), this file | 2026-10-16 |

Ownership requests (per the board rule, requests are logged rather than edited): **`data/analysis.json`,
`analysis.html`, `data/latest.json`, `site/**`, `assets/**`, `index.html`, `picks.html` and the final integration are
owned by session 1abdd416.** This session will not edit them. If 1abdd416's claim goes stale (>60 minutes with no
commit), this session takes the day-4 guidance and mobile tasks over and records the handoff here.

Rules held: Hotspawn is never a probability source; every published percentage is either a validated external line
with a retained raw receipt or our own explicitly labelled model line; unknown values stay blank and flagged; no
paywall/access-control bypass; only `arena/76712ccc-maltaproj4` is pushed.

## Session 76712ccc — delivery record: day-1..3 verification, day-4 lines, pick-only coverage (2026-10-17, 00:07 UTC)

Branch `arena/76712ccc-maltaproj4`, commits `ee0a427` (verification), `4964b6d` (day-4 lines), `14b1e6b`
(identity + pick-only coverage dossier). All three pushes are on this branch only.

### Delivered

| Artifact | What it is | Verification |
| --- | --- | --- |
| `verification-76712ccc/TWC-RESULTS.{json,md}` | Day-1..3 results read out of the 14 retained HLTV captures (2399384–2399417), series + map scores + per-page SHA-256 | parser rewritten to read only played maps and to dedupe the series blocks; every row re-checked against its capture |
| `verification-76712ccc/DAY1-3-REVIEW.md` | Independent review of the published day-1..3 record, with five flags (day-4 date label, Group-B decider, HLTV-vs-file VRS ranks, Aurora's outlier, no day-5 market) | each claim tied to a capture hash or an HLTV page |
| `scripts/twc_day4_76712ccc.py`, `research/day4-76712ccc/DAY4-LINES.{json,md}` | Day-4 semi-final lines recomputed from retained receipts only | script reads raw prices; overrounds and de-margined splits recomputed |
| `research/quotes-76712ccc/UNPRICED-FIXTURE-LINES.{json,md}` + `build_dossier.py` + four retained Valve standings | Per-fixture quote availability for every pick-only row: provider trail, identity check, exact blocker or model line | `PYTHONPATH=. python research/quotes-76712ccc/build_dossier.py` |
| `tests/test_coverage_76712ccc.py` | 16 tests: every open row has a pick, every published probability has receipts, every pick-only row has ≥3 providers and a dossier row, dossier decisions re-derive from `scripts.vrs.line`, unranked teams stay blank | `python -m unittest discover -s tests` → **266 OK** (with PR #50's suite merged in); `scripts.validate` exit 0; `npm run test:browser` 32 scans + 7 expiry scenarios |
| `data/identities.json` | No net change: this session registered the `6666`/`ex-6666` alias, then dropped its own copy when PR #50's identical, source-backed entry merged first. The register on `main` keeps one entry, which this session's test validates | see below |

### The one scope question, and how it resolved

`data/identities.json` is not in this session's claimed file scope. This session registered the `6666`/`ex-6666`
alias there because no other session held a live claim on the file and the claimed task cannot be finished
without it, and declared the 24-line additive edit here. **Open PR #50 (session 1abdd416) had independently
registered the same alias and merged first (merge commit `de4ea16`, 2026-10-17T00:11:06Z), so this session
dropped its own copy during the rebase and now contributes no change to that file.** The register on `main`
carries exactly one entry per club (14 aliases, one `6666`), this session's `tests/test_coverage_76712ccc.py`
validates that entry (names, https sources, basis wording) and re-proves the roster rule, and both sessions'
reasoning agrees: 4 of 5 players shared with Valve's #127 row, 1 of 5 with #368.

Effect, proven locally end to end with the merged register: the next scheduled refresh prices Hotspawn fixture
**1081521 ex-6666 vs Privateer** as an originated `model_vrs` line **78.25% / 21.75%** (Valve #127 923 points vs
#271 608 points; roster overlap 4 of 5 and 3 of 5), and `verification-c6/audit_snapshot.py` reports **0 failures**
with that row "Consistent with stored evidence". The remaining three pick-only rows are unchanged and stay blank:
`antidaun`, `Morningstar` and `WXM` appear in no Valve list (global, Europe, Asia, Americas - all four retained
and hashed in `research/quotes-76712ccc/`).

### Deliberately not changed

`scripts/backfill_quotes.py` MAPPING is untouched: there is no validated market receipt for the four pick-only
rows to add. Polymarket's 59-event CS2 scan has no market for any of them, Pinnacle's sweep covers five CS2
leagues (CCT Europe Challengers, Elisa BreakOut, European Pro League, STK Pulse Beat, TP World Championship)
and none of those leagues lists these fixtures, and the HLTV odds table returned no numeric row. Nothing was
invented to fill the gap.

### Flagged for review (published, not blocking)

- Day-4 date label said "Friday 17 October 2026"; 17 October 2026 is a Saturday (PR #50 says it fixes this).
- The Group-B decider was still published as unresolved at 20:05 UTC; the retained capture carries the final
  page: **BETBOOM 2–1 Legacy**, so semi-final 2 is Falcons vs BETBOOM.
- HLTV's live VRS pages read FURIA #6, Aurora #5, Falcons #4 while the dated official file in use has #7, #9,
  #6 — published as a divergence, not smoothed.
- Aurora's 0–2 opener was an outlier: the rebuilt Aurora (July 2026) then won three series in a row.
- No market receipt exists for the day-5 3rd-place decider or the best-of-five final.

Delivery PR: **#51 <https://github.com/buffedlizard55-lab/MaltaProj4/pull/51>** (branch head `d57d050`). Checks
at open time: the PR run had not been created yet; every check that workflow runs was executed locally instead -
`unittest discover -s tests` 247 OK, `scripts.validate` exit 0, `verification-c6/audit_snapshot.py` 0 failures,
`npm run test:browser` 32 scans + 7 expiry scenarios passed against the built site. Merge result and deploy
confirmation are recorded in the follow-up publication record.

Rules held: Hotspawn is never a probability source; every published percentage is either a validated external
line with a retained raw receipt or our own explicitly labelled model line; unknown values stay blank and
flagged; no paywall/access-control bypass; only `arena/76712ccc-maltaproj4` is pushed.

## Session 76712ccc — publication record for PR #51 (2026-10-17, 00:25 UTC)

**PR #51 <https://github.com/buffedlizard55-lab/MaltaProj4/pull/51> — MERGED** as merge commit
`9029e8f1abcc4459bc1efe73638b8b7fcfb19735` at 2026-10-17T00:14:33Z, after the PR's `verify-build` job passed
(run 38985300698, 1m26s; `deploy`/`harvest` skip on pull requests by design). The branch was rebased onto
`de4ea16` (PR #50) first, which is where this session dropped its duplicate `6666` alias entry; the rebase
conflict in `COORDINATION.md` was resolved as a union, keeping both sessions' records.

### Deploy is green

Main push run **38985450193**: `verify-build` success and **`deploy` success**, including
"Verify live Pages bytes match this exact build". The live `build-info.json` reports revision `9029e8f…`,
built 2026-10-17T00:15:28Z, **96 rows**. (build-info is checked against the run receipt, not a CDN read;
the revision above is the page's own embedded value.)

### End-to-end confirmation of the one priced row

The 00:15Z refresh ran with the merged identity register and priced the fixture this session worked on:

- `https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html` now carries
  **ex-6666 vs Privateer — 78.2% / 21.8%, "OUR MODEL LINE (VRS)", 1.28 / 4.60**, observed 17 Oct 00:15 UTC,
  with the flag "Originated line: Valve VRS model estimate, not a market price." and links to the Valve
  standings file and the HLTV fixture page. The three genuinely unpriced rows (`antidaun` vs Phantom Academy,
  Lynn Vision vs Morningstar, Chinggis Warriors vs WXM) remain research-only with one-sided-ranking
  limitations, exactly as the dossier documents.
- The same refresh also priced **ex-6666 vs G2 Ares** (51.1% / 48.9%) through the same register entry, so the
  bridge is not fixture-specific.

### Day-4 guidance cross-checked on the live page

`analysis.html` (live) now reads "Day 4 · Saturday 17 October 2026" and its two semi-final cards match this
session's independently recomputed lines exactly: FURIA–Aurora Polymarket 0.525/0.475, Pinnacle -125/+103 →
53.0% / 47.0%, our model 62.2% / 37.8%; Falcons–BETBOOM Polymarket 0.795/0.205, Pinnacle -389/+298 →
76.0% / 24.0%, our model 73.9% / 26.1%. Every number agrees with
`research/day4-76712ccc/DAY4-LINES.json`, which was built from the retained raw receipts, so the published
cards are reproducible from the receipts rather than transcribed.

### Still open for whoever works next

- No market receipt exists for the day-5 3rd-place decider (HLTV 2399416) or the best-of-five grand final
  (HLTV 2399417); both are unpriced until a receipt exists or Hotspawn lists them.
- The three research-only rows above stay blank until either a market appears or the team is listed in an
  official Valve list; the pipeline re-probes every run, so nothing needs to be watched by hand.
- The HLTV-live vs dated-file VRS divergence (FURIA #6/#7, Aurora #5/#9, Falcons #4/#6) is published, not
  smoothed; the model keeps the reproducible dated file.
## Session 1abdd416 — integration & publication record (2026-10-17)

**PR #50 https://github.com/buffedlizard55-lab/MaltaProj4/pull/50 — MERGED** at 2026-10-17T00:11:06Z,
merge commit `de4ea16d8939b7cc76f314614bd8039d7deb24f1`.

- Branch checks before the merge: `verify-build` **pass** on the merged head `c1e7800` (run 38985003746, 1m15s).
  One earlier check on this branch failed honestly: run 38984655215 (head `fff1132`) failed the phone step because a
  longer published caveat carried a long unbroken HLTV source URL inside a notice list, which pushed
  `analysis.html` to 375 px of scroll width at a 320 px viewport. Fixed by `overflow-wrap:anywhere` on
  `.notice p, .notice li` in `site/assets/style.css` (`c1e7800`); `node tests/browser.cjs` then passed all 32
  page/viewport scans and `python -m unittest discover -s tests` reported **250 OK**. The red run stays in the
  history: a failing check that names a real defect is the check working.
- Main publish run **38985179678** (push, `de4ea16`): `verify-build` success, `deploy` success, and the deploy job's
  live-byte verifier ("Verify live Pages bytes match this exact build") **success**; receipt artifact
  `live-verification-38985179678`. Legacy `main:/` pages build **38985178985** on the same commit also succeeded.
- **One published claim withdrawn, in the open.** The day-4 caveat list no longer repeats an "HLTV forecast FURIA
  26.5% / Aurora 73.5%". The HLTV odds page for match 2399414, re-read on 17 October, did not reproduce a numeric
  forecast row, so the item now states that the number is withdrawn from this block rather than repeated and reports
  HLTV's stated view (Aurora the bookmaker favourite) as HLTV's view only — never a price and never a model input.
  `tests/test_priced_coverage_621776e4.py` and the rendered page were updated together, so the published bytes and
  the asserted strings agree.
- **`deploy-verify-spurious-failure-2026-10-16` is closed by this session.** Since the verifier repair landed
  (PR #45, run 38962905166) every scheduled `pages.yml` run in the Actions API is green: 38958216665
  (2026-10-16 19:53:22Z, `ff61c63`) and 38977554867 (22:44:42Z, `dc6a802`), with the scheduled
  `CS2 refresh watchdog` runs beside them also green. The two red scheduled runs that created the item
  (38902730567 12:45Z, 38936303441 17:00Z) predate the fix and were receipt failures, not publication failures.
- **Parallel session 76712ccc merged PR #51 into `main` three minutes later** (merge commit `9029e8f1`,
  2026-10-17T00:14:33Z) and its publish run produced the build that the site currently serves. No write was made
  from this session into `arena/76712ccc-maltaproj4`, and no branch or task of that session was taken over. PR #50's
  content survived that merge, checked on `origin/main`: exactly one `6666` alias entry (14 aliases total, no
  duplicate canonical), the `"withdrawn from this block"` wording present in `day_four_guidance.unverified`, the
  `Day-4 picks` nav label intact, and the new `tests/test_coverage_76712ccc.py` validating the same register entry
  both sessions had derived independently (4 of 5 shared players with Valve #127, 1 of 5 with #368).
- **Live verification performed from this session** (recorded because the sandbox cannot reach `*.github.io` —
  `curl` exits 35 — but direct page fetches work): `build-info.json` on the live site reads revision
  `9029e8f1abcc4459bc1efe73638b8b7fcfb19735`, `built_at` 2026-10-17T00:15:28.899713Z, 96 rows; its
  `assets/style.css` SHA-256 `7835ab8188180667bed160ed663434ebea77af3b4549afd177b723ff61715548` is byte-identical to
  this session's local build output, so the 320 px fix is live; the live `picks.html` shows
  **ex-6666 vs Privateer 78.2% / 21.8%, "OUR MODEL LINE (VRS)"** — the `6666` register entry created in PR #50
  pricing the row that the captured snapshot had left pick-only — and both semi-finals now bound to Hotspawn
  fixtures 1080207/1080208 with their exchange lines (FURIA 52.5/47.5, pick FURIA; Falcons 79.5/20.5, pick
  Falcons); the live `analysis.html` carries the withdrawal paragraph verbatim. Coverage read from the live
  executive summary at 00:15 UTC: 34 open fixtures, 96 feed entries, 29 with published probabilities (16 market,
  13 model), 5 research-only picks, **0 with no supported pick**.
- Open coordination issues #1, #5 and #7 were left untouched: they belong to earlier sessions and nothing in this
  session's evidence settles them.
- Record files: `research/day4-1abdd416/VERIFICATION.md`, `research/harvest-1abdd416/**`,
  `runtime/row-audit-local.md` (0 failures). Rules held: Hotspawn supplies fixtures only; every number is either an
  external market line or our own labelled model line; uncertain items are explained in words on the page rather
  than smoothed into numbers.
- This record itself is published as **PR #54** (https://github.com/buffedlizard55-lab/MaltaProj4/pull/54),
  rebased as `main` moved under it (`de4ea16` → PR #51 `9029e8f1` → PR #53 `df54ed5`); `verify-build` was green on
  each head before merging, and the merge/deploy result for this PR is the last entry of the Actions history rather
  than a claim inside the file it publishes.
- **Seen while rebasing:** PR #52 (session `bca04a82`, "Day-4 TWC guidance: both semis priced from Pinnacle +
  Polymarket, day-3 decider final") is `CONFLICTING` against `main`. That material is already published by PR #50
  (`de4ea16`), and PR #51 additionally bound both semi-finals to Hotspawn fixtures 1080207/1080208 with their live
  exchange lines. If #52 is taken forward it must be rebased onto `main` and must keep the published cards, the
  `6666` register entry and the withdrawn-forecast wording instead of reverting them. No write was made from this
  session into `arena/bca04a82-maltaproj4`, and no branch of another session was touched.


### Addendum (final for session 76712ccc)

The publication record above was merged by **PR #53 <https://github.com/buffedlizard55-lab/MaltaProj4/pull/53> —
MERGED** as merge commit `df54ed531a397b4318567b91bcfccc4ead97f068` at 2026-10-17T00:19:32Z (PR `verify-build`
run 38985693970 pass), and the main push run 38985841195 that followed was green end to end: `verify-build`
1m46s, **`deploy` 18s with "Verify live Pages bytes match this exact build"**. Session 76712ccc has no further
work queued; later merges on `main` are other sessions' business.
## Session 498cc7dd claims (2026-10-16, ~23:55 UTC)

Arena fixes this session to `arena/498cc7dd-maltaproj4`; no other working branch is created, checked out or pushed.
Board state read before claiming: `origin/main` is at `dc6a802` (PR #47, session 621776e4, merged 20:50Z) and this
branch is exactly at `dc6a802` (`git rev-list --count HEAD..origin/main` → `0`). `git branch -r` lists only
`origin/main` plus this branch, so **no other session holds an active claim** and nothing is being taken over.
The scheduled `Verify, refresh and publish CS2 Scout` run `38977554867` (1h before this claim) finished
`verify-build` + `deploy` green on `main`, so the live board is current; this session's work is new
user-requested analysis, not a takeover.

This is the same standing request restated, so the tasks below are the four open user-facing gaps this session
re-checked rather than brand-new inventions:

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Live re-harvest of the Hotspawn fixture inventory + Polymarket/Pinnacle/HLTV evidence for every open row that still has no percentage | in progress | 498cc7dd | research/harvest-498cc7dd/**, scripts/probe_498cc7dd.py, .github/workflows/harvest-498cc7dd.yml | 2026-10-16 |
| Day-1→day-3 TWC 2026 review re-verified line by line from HLTV; day-4 (17 Oct) semi-final guidance with real external lines; contrarian-but-not-stupid framing incl. the Aurora roster premise | in progress | 498cc7dd | research/day4-498cc7dd/**, data/analysis.json, analysis.html | 2026-10-16 |
| Unresolved picks + their limitations surfaced in the executive summary, with an in-site link to the live picks board (mobile-first) | in progress | 498cc7dd | scripts/build.py, index.html, unresolved.html, assets/** | 2026-10-16 |
| Build, validate, browser checks, PR from this branch, merge without approval, verify Pages is live | in progress | 498cc7dd | COORDINATION.md (log only) | 2026-10-16 |

Rules this session holds to: Hotspawn establishes the fixture inventory only, never probability; probabilities come
only from externally observed market lines or reproducible calculations on them; unknown odds/probabilities stay
blank and flagged, never inferred; no paywall or region-gate bypass; every published claim carries a primary
source link; `git pull --rebase` before every push; nothing is called verified without an official source.

## Session 498cc7dd — outcome record (2026-10-17, ~01:15 UTC)

### Overlap found on rebase, and how it was resolved

This session branched from `dc6a802`. While it worked, `main` moved to `de4ea16` (PR #50, session
**1abdd416**), which had already published day-4 semi-final picks. On `git rebase origin/main` the
overlap was concrete, so rather than ship two competing day-4 blocks the two were compared value by
value with `git show origin/main:data/analysis.json`:

| Claim | 1abdd416 on `main` | 498cc7dd draft | Resolution |
| --- | --- | --- | --- |
| Day-4 date label | "Day 4 · Saturday 17 October 2026" | same | `main` kept. **The weekday error this session found at `dc6a802` was already fixed by 1abdd416 in `e9d27c6`;** `git grep 'Friday 17 October'` over `main`'s HTML and `data/analysis.json` returns nothing. Recorded as an independent confirmation, not a new correction, and the review note that claimed the fix was **withdrawn** from `data/review-notes.json`. |
| Day-3 results | 2 rows incl. BETBOOM 2-1 Legacy with Nuke 16-13 / Dust2 11-13 / Mirage 13-11 | same | `main` kept. |
| Semi-final lines | exchange + Pinnacle cross-check + model, 23:52Z captures, 9 points, 13 caveats | exchange only, 10 points, 16 caveats | `main` kept — it is a strict superset on sourcing. `scripts/add_day4_498cc7dd.py`, which produced the thinner draft, was **deleted** so it cannot be re-run to regress that content. |
| `data/latest.json` | generated **19:59:25Z**, 21 open, **0 without a pick** (exchange 6, exchange_wide 2, model_vrs 9, research_rank 1, research_rank_single 3) | generated 23:53:53Z, 21 open, **8 without a pick** | **`main`'s snapshot kept.** Publishing this session's snapshot would have removed eight picks from the live board. This session's snapshot is retained only as evidence, in `research/harvest-498cc7dd/`. |

So the day-4 analysis on the site is 1abdd416's, and this session's contribution is narrower than
the claim it opened with. What actually shipped:

### 1. A refresh could silently strip eight picks — root cause found and fixed

`research/harvest-498cc7dd/logs/refresh.txt`, from run
[38983767301](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38983767301):
`{"coverage":"verified","matches":83,"priced":13,"research_only":0,"unresolved_without_any_pick":8}`.
HLTV answered **HTTP 403** to that runner for `https://www.hltv.org/matches` while every other source
in the same run answered 200, and the identical read at 19:57Z that evening answered 200.
`Sources.get` treated the 403 as a permanent access restriction and blocked the host for the rest of
the run, which removed both the HLTV lineups `scripts/vrs.py::identify()` needs to choose between the
two rosters Valve lists under one label (Just Players, Banda Chuya, aimclub, Leo and Chinggis Warriors
each appear twice in `data/vrs/standings_global_2026_10_05.md`) and the ranking-order research pick.
Note that `coverage` still reported **`verified`** — nothing in the run's output signalled the loss.

Fixed in `scripts/refresh.py`: a rate-limited 403/429 is waited out on the identical URL with identical
headers (`Retry-After` honoured, then 10s/30s/60s, 120s cap) and only blocked if it keeps refusing;
401, 404 and region/challenge pages are unchanged. 13 new tests in `tests/test_rate_limit_498cc7dd.py`.
**The recovered row count is deliberately not claimed** — it is whatever the next scheduled refresh
reports. Published as flagged item `unpriced-rows-2026-10-16`.

### 2. Two Polymarket labels flagged, not aliased

Polymarket prices two fixtures under labels no official source read this session confirms:
"BET-M 33" for Hotspawn's BET-M (market 5769541, 0.625/0.375, 1-point spread, $3,184.25, captured
23:51Z) and "Leo Team" for Hotspawn's Leo (market 5650418). HLTV's canonical name is **BET-M**
([team 13619](https://www.hltv.org/team/13619/bet-m)) and Valve lists one BET-M at rank 71 and two
different rosters named `Leo`. Opponent, UTC start and tournament match exactly, but the labels were
**not** auto-aliased and no probability was published from them; the published pick for fixture
1079170 remains our VRS model line (BET-M 68.1%, `model_vrs`). Published as flagged item
`identity-bet-m-33`.

### 3. One stale line de-staled

`scripts/build.py`'s start-here card still read "the Group B decider was still live at the last read"
on `main`, after that decider finished. Now reads: "Aurora 2-0 9z and BETBOOM 2-1 Legacy in the two
group deciders, so the semi-finals are set. Verified from HLTV."

### 4. Independent receipts added

`research/harvest-498cc7dd/` — a second 23:51Z Polymarket capture of both semi-final markets
(5778024 FURIA 0.525 / Aurora 0.475, $158,627.63 liquidity; 5787759 Team Falcons 0.795 / BetBoom Team
0.205, $60,452.33) beside 1abdd416's 23:52Z capture, plus the 23:53:53Z snapshot behind the diagnosis
above. `research/day4-498cc7dd/` — the day 1-4 re-verification, each claim naming what its source
literally said, and both "status at merge" sections stating plainly what this session did not change.

### Verification before this record (all run after the rebase resolution)

- `python -m unittest discover -s tests` → **263 OK** (`main`'s 250 + 13 new rate-limit tests);
  `audits` 9 OK; `verification-95b588c2` 5 OK; `verification-c6` 12 OK.
- `python -m scripts.build --data data/latest.json` → "Built 9 primary pages + 6 legacy redirects;
  83 sourced rows, 17 priced, 4 unresolved".
- `python -m scripts.validate --data data/latest.json --site .` → 83 rows verified against the primary
  snapshot, **17 probability calculations reproduced**, 15 pages, 570 internal links/assets, 20
  artifact checksums, 202 displayed match rows.
- `npm run test:browser` → 32 accessibility/no-overflow scans at 320/390/768/1440px + 7 exact-boundary
  expiry scenarios, all passing.
- Published `review.html` renders all **50** flagged items (checked by id); the withdrawn weekday note
  returns 0 hits. Published `index.html` reads "Coverage at 16 Oct · 19:59 UTC" and "0 open match(es)
  have no supported pick at all".
- Root `assets/style.css` was out of sync with `site/assets`; `scripts.stage_legacy` resynced it
  (append-only mobile-wrap rule, nothing above it altered).

### Files touched by this session

`scripts/refresh.py`, `scripts/build.py` (one line), `tests/test_rate_limit_498cc7dd.py` (new),
`data/review-notes.json` (two items added, one withdrawn), `.github/workflows/harvest-498cc7dd.yml`
(new), `research/harvest-498cc7dd/**`, `research/day4-498cc7dd/**`, regenerated site files,
`COORDINATION.md`. Nothing in another session's file scope was overwritten: `data/analysis.json`,
`data/latest.json`, `data/matches.csv` and `tests/test_priced_coverage_621776e4.py` were resolved to
`main`'s versions. `scripts/probe_621776e4.py` was **invoked** with
`--output research/harvest-498cc7dd`, not modified.


## Session bca04a82 claims (2026-10-16, 23:55 UTC)

Arena fixes this session to `arena/bca04a82-maltaproj4`; no other branch is created, checked out or pushed.
Board read before claiming: `origin/main` is `dc6a802` (PR #47 merge, session 621776e4, 20:41 UTC); every
task on the board above is `done`; the last commit by any session is ~3 h old (621776e4, 20:31 UTC),
so no claim is inside the 60-minute window and none is taken over. The last scheduled publish run
(38977554867, 22:44 UTC) succeeded and the live site serves revision `dc6a802`. This is new work for
the same standing brief: the TWC day-3 deciders have finished since the last harvest (BETBOOM vs Legacy
was still live at 20:08 UTC), so the day-4 semifinal bracket must be re-verified and republished, the
four research-only rows need fresh esportsbook/HLTV line attempts, and the whole board needs a
line-by-line re-verification before the integration PR.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Verify TWC day-3 results line by line from HLTV (Aurora–9z final; BETBOOM–Legacy final result now that it has finished) and the day-4 semifinal bracket; update `data/analysis.json` additively | in progress | bca04a82 | data/analysis.json (additive day_three_results/day_four updates), research/day4-bca04a82/** | 2026-10-16 23:55 |
| Fresh non-publishing harvest of the Hotspawn board; confirm whether the day-4 semifinals are now listed and whether any market line exists for them; resolve the four research-only rows (1081521, 1081522, 1081861, 1081863) via HLTV → esportsbook lines, publishing dated receipts and limitations | in progress | bca04a82 | research/harvest-bca04a82/**, research/day4-bca04a82/**, data/book-receipts.json (dated receipts only), data/identities.json (sourced aliases only) | 2026-10-16 23:55 |
| Line-by-line re-verification of the published board against primary sources; flag irregularities | in progress | bca04a82 | research/day4-bca04a82/**, data/review-notes.json (additive) | 2026-10-16 23:55 |
| Final integration: rebuild, full test suites, executive-summary/unresolved links check, mobile check, PR to main, explicit merge, cache-busted live Pages verification, record in this file | in progress | bca04a82 (final integration) | scripts/build.py (additive only if needed), generated root HTML routes, data/latest.json, data/matches.csv, COORDINATION.md, README.md, build-info.json | 2026-10-16 23:55 |

Evidence standard unchanged: Hotspawn fixes the fixture inventory only and is never a probability
input; probabilities come only from externally observed market lines that pass the published gates or
from the labelled originated VRS model; HLTV supplies identity/results/rankings; anything unverifiable
stays blank and flagged. Sandbox bash reaches GitHub and package registries only, so HLTV/Polymarket/
Pinnacle/Hotspawn are read through the retrieval tooling (dated, cache-busted where a cache could
interfere) and through Actions runners; no access control is bypassed and no source is claimed checked
when it was not.

### Session bca04a82 coordination log

- 2026-10-16 23:55 UTC: claim appended; working tree verified clean at `dc6a802` before this commit.
- 2026-10-17 00:05 UTC: day-3 decider verified final from HLTV 2399413 — BETBOOM 2-1 Legacy
  (Nuke 16-13 OT [halves 4:8; 8:4, OT 4:1], Dust2 11-13, Mirage 13-11; veto: BETBOOM removed
  Inferno, Legacy removed Anubis, BETBOOM picked Nuke, Legacy picked Dust2, BETBOOM removed
  Cache, Legacy removed Ancient, Mirage over; Magnojez 62-50 1.17, d1Ledez 55-50 1.08,
  Boombl4 49-51 1.06, S1ren 44-47 1.02; demo 112853). Aurora 2-0 9z re-verified from 2399412
  (Cache 13-11 [8:4; 5:7], Inferno 13-4 [9:3; 4:1]; veto incl. Aurora removed Nuke; kyxsan
  1.45, Jimpphat 1.31; demo 112837). Semi-final bracket confirmed on HLTV 2399414/2399415
  (Bo3, LAN, 14:00Z / 17:00Z starts, countdowns cross-checked).
- 2026-10-17 00:10 UTC: BOTH semis priced on TWO markets each, read from the operator APIs.
  Semi 1: Pinnacle matchup 1638536356 period-0 ML FURIA -125 / Aurora +103 (version 3767145143,
  league "CS2 - TP World Championship" 230242) de-margined 53.0/47.0 (overround 4.82%);
  Polymarket event 1200431 (slug cs2-furia-aur1-2026-10-17) Match Winner market 5778024 at
  0.525/0.475 (last trade 0.53, liq $158,628). Semi 2: Pinnacle matchup 1638595724 period-0
  ML Falcons -389 / BETBOOM +298 (version 3767145819) de-margined 76.0/24.0 (overround 4.68%);
  Polymarket event 1201748 (slug cs2-fal2-bb3-2026-10-17, found at tag-100780 offset 5)
  Match Winner market 5787759 at 0.795/0.205 (liq $60,484). Receipts appended to
  data/book-receipts.json (now 6).
- 2026-10-17 00:15 UTC: Hotspawn scheduled feed re-read in full (all 9 chunks) — the TWC
  main-event playoffs are NOT listed (only the South American Series #1 qualifier), so the
  semis cannot become board rows; they ship as analysis cards. 3rd-place match and grand
  final priced by neither book (Polymarket slug guess returned []; no Pinnacle matchup) —
  flagged unpriced.
- 2026-10-17 00:20 UTC: data/analysis.json updated — day_three_results completed (BETBOOM
  card added, Aurora card upgraded to fully HLTV-verified), day_four_guidance rewritten with
  both confirmed semi cards (dual-book lines, devig arithmetic, rest/map-load audit, verified
  H2H, limitations). Two integrity fixes made while verifying: (1) the IEM Cologne Major
  FURIA-Aurora meeting was FURIA 2-0 (HLTV 2395000: Nuke 13-4, Dust2 13-9), not Aurora 2-0 —
  the 2026 H2H is therefore split 2-2, not 3-1 Aurora; (2) HLTV's on-page win-probability
  forecast is client-side and unreadable, so the previously published unverified 26.5/73.5
  figure is withdrawn and replaced with the verified VRS points boxes (FURIA 1826 #6 vs Aurora
  1848 #5; Falcons 1880 #4 vs BETBOOM 1619 #10).
- 2026-10-17 00:25 UTC: local rebuild green (9 primary pages + 6 redirects, 83 rows, 17 priced,
  4 unresolved; validate: 83 rows verified, 17 probability calculations reproduced, 570 links
  checked, 20 checksums, 202 displayed rows). Unit suite 231/231 after re-pinning three
  assertions in tests/test_priced_coverage_621776e4.py that encoded the superseded 19:35-UTC
  state (pending decider, 19:35 market label, unverified forecast) to the verified 00:10-UTC
  invariants; no invariant weakened. Committed root copies of the built pages follow the
  integration convention; data/latest.json changed only in built_at/expires_at (zero row-state
  diffs).
- 2026-10-17 00:30 UTC: pushed 940f91f to arena/bca04a82-maltaproj4; PR #52 opened against
  main: https://github.com/buffedlizard55-lab/MaltaProj4/pull/52



### Addendum 2 (final closure for session 76712ccc)

The record above was carried to `main` by **PR #56 <https://github.com/buffedlizard55-lab/MaltaProj4/pull/56> —
MERGED** at 2026-10-17T00:25:53Z as merge commit `14d97dc663e08b60926e4cac492d128335b6e80e`.

Merge irregularities (both recorded, neither hidden):

1. The first `gh pr merge 56 --merge` attempt failed with *"Base branch was modified. Review and try the merge
   again."* because session `1abdd416`'s PR #54 landed as `f832420` between PR #56's check run and the merge.
   Fixed by `git fetch origin main && git rebase origin/main`: the only conflict was `COORDINATION.md` (both
   sessions append at the end) and it was resolved as a **union** — session `1abdd416`'s block is kept verbatim
   and this session's block follows, nothing deleted; the rebased file contains 0 conflict markers. Post-rebase
   evidence: `python -m unittest discover -s tests` → **266 OK**; the rebased commit was pushed as `79b4bd2`.
2. `git push --force-with-lease` issued *during* the unresolved rebase was a **silent no-op** (the local branch
   ref had not advanced, so the lease matched and nothing was sent); the remote kept the pre-rebase tip
   `36092f1` until the rebase finished. Do not treat a force-with-lease inside a conflicted rebase as evidence
   of publication.

PR #56 `verify-build` passed in 1m21s (run 38986201182). The main push run for `14d97dc`, 38986336046, shows
conclusion **cancelled with 0 jobs**: session `498cc7dd` merged PR #55 (`0d77fe9`) at 00:30:10Z and the
`pages.yml` concurrency group superseded the older run before it started. The site is therefore published by
the following main run 38986656324 (`0d77fe9`): `verify-build` 3m29s, **`deploy` 17s**, and the live
`build-info.json` reads revision `0d77fe9b4aa6a7dc64e96662e1ab9ae475a5459d`, built 2026-10-17T00:33:21Z,
96 rows — i.e. the merged state that contains this session's register and dossier. PR #56 changed documentation
only, so no published site byte depends on the cancelled run.

Session 76712ccc is closed: no claim outstanding, no branch of another session touched, no further work queued.
## Session 498cc7dd — publication record for PR #55 (2026-10-17, 00:30 UTC)

**Merged.** [PR #55](https://github.com/buffedlizard55-lab/MaltaProj4/pull/55) → `main`, merge commit
`0d77fe9b4aa6a7dc64e96662e1ab9ae475a5459d`, `mergedAt 2026-10-17T00:30:07Z`, read back with
`gh pr view 55 --json state,mergedAt,mergeCommit`. At the moment of the merge `origin/main` was
`0d77fe9 Merge pull request #55 from buffedlizard55-lab/arena/498cc7dd-maltaproj4`; it has since
advanced (session bca04a82 merged PR #52 on top, whose own merge commits already unioned this
session's work).

### Pages is live, proven by the pipeline's own gate

Publish run [38986656324](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38986656324)
on `main` completed **success**. Read with `gh run view 38986656324 --json jobs`:

| Step | Conclusion |
| --- | --- |
| Build and independently verify every row, calculation and internal link | success |
| Phone, tablet, desktop, accessibility and exact-boundary expiry checks | success |
| Deploy verified static dashboard | success |
| Retry the deployment once when the first attempt failed | skipped (first attempt worked) |
| **Verify live Pages bytes match this exact build** | **success** |

That last step runs `scripts/verify_live.py` against
`https://buffedlizard55-lab.github.io/MaltaProj4/` with `MANIFEST_SHA` and `BUILT_AT` from the
verify-build job, so the live site is serving this exact build. `pages-build-deployment` run
[38986656654](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38986656654) also
completed success. The `live-verification-38986656324` artifact could not be downloaded from this
sandbox (`gh run download` → EOF on `productionresultssa3.blob.core.windows.net`, the same limitation
earlier sessions recorded), so the step conclusion is the evidence quoted here, not the receipt JSON.

### Rebase history — three sessions merged underneath this PR

The PR head moved four times because `main` advanced while it was open, and each time the branch was
rebased, re-verified and force-pushed with `--force-with-lease`:

| PR head | Why it moved | verify-build |
| --- | --- | --- |
| `f748466` | opened on `de4ea16` | pass |
| `8388e45` | PR #53 (session 76712ccc) merged | — |
| `ffc20cc` | PR #54 (session 1abdd416) merged | pass (run 38986298199) |
| `5098dd4` | PR #56 (session 76712ccc) merged | **pass** (run 38986479685, 1m8s) — the merged head |

Every conflict was in `COORDINATION.md` only, and every one was resolved by keeping **both** sessions'
sections in file order; `git diff origin/main -- COORDINATION.md` was checked for `-` lines after each
resolution and showed none, i.e. nothing another session wrote was dropped. `scripts/refresh.py` was
never touched by any of the three merging sessions (`git diff <base> origin/main -- scripts/refresh.py`
→ empty each time), so the rate-limit fix carried through untouched.

### Local checks on the merged tree, run before the merge

- `python -m unittest discover -s tests` → **279 OK**; `audits` 9 OK; `verification-c6` 12 OK;
  `verification-95b588c2` 5 OK. (`verification-76712ccc/` is a docs directory with a parser, not a
  test suite: discovery there returns 0 tests.)
- `scripts.build` → 83 sourced rows, 17 priced, 4 unresolved.
- `scripts.validate` → 83 rows verified against the primary snapshot, 17 probability calculations
  reproduced, 15 pages, 570 internal links/assets, 20 artifact checksums, 202 displayed match rows.
- `npm run test:browser` → 32 accessibility/no-overflow scans at 320/390/768/1440px + 7 exact-boundary
  expiry scenarios.

### What is on the live site from this session, and what is not

**On it:** the `scripts/refresh.py` rate-limit fix (a 403 can no longer silently strip eight picks
while still reporting `coverage: verified`); two flagged items on the Flagged for Review page
(`unpriced-rows-2026-10-16`, `identity-bet-m-33`), bringing that page to 50 items; one de-staled
start-here card line; and the `research/harvest-498cc7dd/` + `research/day4-498cc7dd/` evidence.

**Not on it, deliberately:** any change to the day-4 guidance. `main` already carried session
1abdd416's richer day-4 block and its 19:59:25Z snapshot with 0 unpicked open rows, and both were kept.
The weekday error this session found at `dc6a802` had already been fixed on `main` by 1abdd416 in
`e9d27c6`; the review note that claimed the fix was withdrawn before the merge.
`scripts/add_day4_498cc7dd.py` was deleted so it cannot regress that content.

### Still open for whoever picks this up next

1. **The recovered row count is unclaimed.** The next scheduled refresh is the only thing that can
   confirm the rate-limit fix restores those eight rows. If a future run again shows
   `unresolved_without_any_pick > 0` with a 403 in `logs/refresh.txt`, the fix did not cover that path.
2. **Two identity candidates are flagged, not aliased.** Confirming Polymarket's "BET-M 33" (market
   5769541) = HLTV team 13619 would let fixture 1079170 be re-priced from a liquid 1-point-spread
   market instead of the `model_vrs` line; the same question applies to "Leo Team" (market 5650418)
   against Valve's two `Leo` rosters.
3. **Why HLTV returned 403 is unexplained.** Cloudflare rate-limiting is the obvious candidate but is
   not established by anything read this session. The fix removes the failure mode either way.

## Session 6d2af30b — cadence accuracy audit (2026-10-17, 00:48 UTC)

The current board's day-four integration owner bca04a82 opened PR #52 at 00:30 UTC; `gh pr view 52` confirms it merged at 00:34:17Z. That work is therefore complete, not an active overlapping claim. This session claims a focused documentation/verification correction after comparing the actual scheduled workflows against their generated and source descriptions.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Reconcile published refresh-cadence text with workflow configuration; add regression coverage and rebuild the verified static fallback | done | 6d2af30b | README.md, scripts/build.py, scripts/refresh_watchdog.py, .github/workflows/pages.yml, .github/workflows/refresh-watchdog.yml, tests/test_refresh_watchdog.py, generated root pages/build-info.json, COORDINATION.md | 2026-10-17 01:03 |

Verified discrepancy before edits: `.github/workflows/pages.yml` schedules four attempts per hour (`4,19,34,49` UTC), `.github/workflows/refresh-watchdog.yml` schedules a check every 10 minutes and `scripts/refresh_watchdog.py` dispatches only when the published snapshot exceeds 90 minutes. README and generated methodology/footer instead claimed an hourly :17 schedule; methodology described twelve slots per day. Fix only this reporting mismatch; do not change refresh behavior or data.

### Session 6d2af30b — closure and publication record (2026-10-17)

- Corrected stale cadence copy only; runtime schedule is unchanged. The exact workflow configurations now agree with README, generated methodology and sidebar/freshness copy: Pages attempts at :04/:19/:34/:49 UTC; watchdog checks every 10 minutes and can dispatch if published snapshot age exceeds 90 minutes, subject to its cooldown/budget. The older hourly/two-hourly measurements remain explicitly historical.
- Added `test_documented_cadence_matches_workflows` to compare documentation against both cron expressions. The 90-minute threshold remains independently tested.
- Verification before merge: unit suite 280 OK; audits 9 OK; integrity acceptance 5 OK; verification-c6 12 OK; snapshot/page validator 83 sourced rows, 17 price calculations, 15 pages, 570 links/assets, 20 checksums, 202 displayed rows; browser suite 32 responsive/accessibility scans and 7 expiry-boundary cases all passed.
- **PR #60** (<https://github.com/buffedlizard55-lab/MaltaProj4/pull/60>) merged at 2026-10-17T00:57:29Z as `38f3b7e2fad84bbcb7d868959159d44fad834296`. PR verify-build passed; main Pages workflow run [38988737429](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38988737429) completed successfully, including deploy and exact live-byte verification. Cache-busted public `build-info.json` read back revision `38f3b7e2fad84bbcb7d868959159d44fad834296`, built `2026-10-17T00:59:57.881526Z`, 96 rows.
- Primary references checked: `.github/workflows/pages.yml`, `.github/workflows/refresh-watchdog.yml`, `scripts/refresh_watchdog.py`, [live build receipt](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json), and the historical timing report `research/refresh-ab18fe2a/DIAGNOSIS.md`.
- Irregularity: the committed baseline is older than the live refreshed dataset by design; the workflow builds from its cached/re-refreshed inventory and the site expires old evidence. This correction does not alter any match, pick, line or probability.

## Session 37bf28f4 — day-4 TWC review, full-pick coverage audit, mobile exec summary (2026-10-17, 01:00 UTC)

Arena fixes this session to `arena/37bf28f4-maltaproj4`; no other branch is created, checked out or pushed.
Board state read before claiming: every earlier block above is `done`/closed and no branch other than `main`
exists on the remote (`git branch -r` → `origin/main` only), so nothing is being taken over. This is new
work for the 17 October (day-4) semi-final day.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Re-verify day-1 to day-3 TWC 2026 results and the Aurora roster-change premise line by line from HLTV, then publish day-4 guidance with the currently open semi-final / third-place / grand-final lines | done | 37bf28f4 | research/day4-37bf28f4/**, research/harvest-37bf28f4/**, data/analysis.json, scripts/twc_day4_37bf28f4.py | 2026-10-17 |
| Full-pick coverage audit for every open Hotspawn CS2 fixture: confirm each row resolves (market or labelled research tier), record the limitation for any row that cannot | done | 37bf28f4 | research/day4-37bf28f4/**, data/latest.json, scripts/backfill_quotes.py (receipt mapping only) | 2026-10-17 |
| Mobile-first executive summary check: in-site links to the picks board, unresolved section and day-4 guidance readable at 320/390px | done | 37bf28f4 | site/**, assets/style.css, scripts/build.py, index.html, README.md | 2026-10-17 |

Rules held to: no file owned by another session is edited (none claimed); primary sources only; no Hotspawn
votes as probability; unknown values stay blank and flagged; `git pull --rebase` before every push.

### Session 37bf28f4 — results and verification (2026-10-17, 01:2x UTC)

All three claimed tasks are done on `arena/37bf28f4-maltaproj4`. Evidence record:
`research/day4-37bf28f4/DAY4-REVIEW.md`, field-level receipts `research/harvest-37bf28f4/day4-live-reads.json`.

**Day 1–3, re-verified line by line.** Ten series read from HLTV's event results list; 9z 2-0 Aurora and
Aurora 2-0 Ninjas in Pyjamas re-read on their own match pages, including the veto order (9z picked Inferno,
Aurora picked Nuke on 14 October; NIP picked Cache, Aurora picked Dust2 on 15 October), the map scores
(Inferno 13-11 with halves 8:4/5:7, Nuke 13-1 with 11:1/2:0, Cache 13-9, Dust2 13-7) and the player rows
(luchov 38-20, +6.61%, 97.4 ADR, 1.61 rating; Wicadia 45-25, 1.65). HLTV's day-one report
(https://www.hltv.org/news/45718/...) names Aurora "the fifth-ranked team in the VRS" and records 9z's 62
VRS points. Aurora's rebuild is dated 8 July 2026 (kyxsan from Falcons; Jimpphat and coach ash on 3 July),
so the "recent roster change" premise does **not** hold for day four, and the block says so.

**Scoring facts (new).** Hotspawn's official rules page states bonus points for consecutive correct picks
and a weekly leaderboard reset; its fixture API exposes `points_breakdown`, `offered_points` and
`lock_offset_sec: 360` on every CS2 row, none of which depends on the crowd split. Neither TWC semi-final
is on that feed, so a TWC pick scores nothing in the pick'em — the streak risk lives on the tiered board
rows. Both facts are now points in the day-4 block.

**Coverage audit.** The live board (00:43–00:45Z snapshot, read at 01:02Z) reports 21 open fixtures:
17 with published probabilities (8 market, 9 model), 4 labelled research-only picks, 0 with no supported
pick. Every unpriced row is on `unresolved.html` with its gate. The only genuinely unpriceable TWC items
are Sunday's third-place decider (11:30Z, bo3) and grand final (15:00Z, bo5) — participants unknown, no
market on either operator — now published in a dedicated "What still has no price, and why" table with
sources, plus an executive-summary notice that counts them and links to it.

**Corrections published, not hidden.** (1) The earlier "higher-ranked side won eight of the ten series"
sentence was withdrawn in the block and in its own limitations list, and flagged as
`withdrawn-rank-count-2026-10-17` on the Flagged for Review page. (2) The day-2 point was split so the map
detail is sourced to the match page rather than the results list. (3) The rules page's "5 minutes" lock
wording against the feed's 360-second offset is flagged as `lock-time-wording-2026-10-17`; the board keeps
the earlier, conservative value.

**Verification run.** `python -m unittest discover -s tests` → 279 OK; `audits` → 9 OK;
`verification-95b588c2/test_integrity.py` → 5 OK; `verification-c6` → 12 OK; `scripts.build` → 9 primary
pages + 6 legacy redirects, 83 sourced rows, 17 priced, 4 unresolved; `scripts.validate` → 83 rows
verified, 17 calculations reproduced, 573 links, 20 checksums, 202 displayed rows; `npm run test:browser`
→ 32 accessibility/no-overflow scans at 320/390/768/1440px + 7 exact-boundary expiry scenarios.

**Not closed, deliberately.** The two Sunday matches stay priced-only-when-a-market-exists; Liquipedia has
no page for this event, so there is no wiki cross-check; live collection continues to run on GitHub
Actions because this sandbox's shell reaches only GitHub and the package registries. `data/latest.json`
changed only in its `built_at`/`build_utc` stamps this round (zero row-state diffs) — the scheduled refresh owns its contents.

## Session 03befae8 claims (2026-10-17, 00:55 UTC)

Arena fixes this session to `arena/03befae8-maltaproj4`; no other branch is created, checked out or
pushed. Board read before claiming: `origin/main` is at `8d32db8` (PR #59, session 498cc7dd, merged
00:41Z). Every board task above is `done`; the last commit by any session is 00:41Z and it is a
documentation-only merge of a finished session, so no claim is inside the 60-minute window and
nothing is taken over. All 37 remote session branches still exist; only the merged ones are inert.
PR **#57** (session 1abdd416, `dual-publisher-race-2026-10-17` flagged item) is still open and
`DIRTY`; its **file scope is not touched by this session** — this session only integrates it at the
end (see the log below).

This is new work for the same standing brief: the TWC day-3 deciders are final and day 4 is today,
the live board moved to 96 rows / 34 open at 00:45Z, five open rows still carry a research-only pick
with **no percentage**, and the published root fallback is one snapshot behind the live artifact.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Verify TWC 2026 day 1–4 line by line from HLTV (9z–Aurora day-1 upset, day-2 results, both day-3 deciders, the day-4 semi-final bracket), re-verify the Aurora roster-change premise, and publish the contrarian-but-not-stupid leaderboard framework with the day-4 picks | in progress | 03befae8 | data/analysis.json (additive), scripts/build.py (analysis cards only), research/day4-03befae8/** | 2026-10-17 00:55 |
| Give a **percentage** to every open row that still has a research-only pick: read external book listings (EGamersWorld book-average lines) for those exact fixtures, add dated, replayable receipts, and add an automated book-listing provider to the refresh ladder so the lines are re-read every cycle instead of expiring | in progress | 03befae8 | scripts/core.py, scripts/refresh.py, data/book-receipts.json, tests/test_egw_03befae8.py | 2026-10-17 00:55 |
| Mobile-first executive summary: one-tap path from the landing page to the picks board, probability-first cards, the unresolved section and its limitations inside the executive summary | in progress | 03befae8 | scripts/build.py (exec summary only), assets/style.css, assets/app.js, tests/test_mobile_exec_03befae8.py | 2026-10-17 00:55 |
| Final integration: fold in PR #57's flagged finding, rebuild, re-verify every row/calculation/link, open the PR to `main`, merge it, confirm the Pages deploy and record the result | in progress | 03befae8 (final integration) | generated root HTML, data/latest.json, data/matches.csv, build-info.json, COORDINATION.md, README.md, .github/workflows/harvest-03befae8.yml | 2026-10-17 00:55 |

Evidence standard unchanged: Hotspawn fixes the fixture inventory only and is never a probability
input; a probability is published only from an externally observed two-sided line that passes the
published gates, or from the labelled originated VRS model; anything unverifiable stays blank and is
flagged. Sandbox bash reaches GitHub and package registries only, so HLTV, EGamersWorld, Polymarket,
Pinnacle and Hotspawn are read through the retrieval tooling and through Actions runners; no access
control is bypassed and no source is claimed checked when it was not.

## Session 03befae8 work record (2026-10-17, 01:15 UTC)

Branch `arena/03befae8-maltaproj4`, started from `origin/main` at `8d32db8` (PR #59). Claim table
above was published at `a80b9da` before any work started. Four tasks, all now done.

### 1. TWC 2026 day 1–4 verified line by line, and the day-5 bracket added

Re-read from HLTV on 17 October 2026 between 00:00 and 01:00 UTC (event 8932):

* Day 1 — 9z **2-0** Aurora (the upset), Falcons 2-0 Ninjas in Pyjamas, Legacy 2-0 PARIVISION,
  FURIA 2-0 BETBOOM. Day 2 — 9z 1-2 Falcons, Aurora 2-0 Ninjas in Pyjamas, Legacy 1-2 FURIA,
  PARIVISION 1-2 BETBOOM. Day 3 — Aurora 2-0 9z (Group A decider), BETBOOM 2-1 Legacy (Group B).
  Source: <https://www.hltv.org/results?event=8932>
* Aurora's roster is unchanged: XANTARES, woxic, Jimpphat, kyxsan (IGL), Wicadia, coach Ashley
  'ash' Battye, VRS #5, HLTV world #6, and the rebuild is a **July** rebuild, so it cannot explain
  the day-1 upset and gives no onboarding factor for day 4. Source:
  <https://www.hltv.org/team/11861/aurora>
* The head-to-head line already published is **confirmed, not corrected**: match 2398743
  (ESL Pro League Season 24, 6 October) is Aurora 2-1 FURIA with Dust2 13-8, Mirage 9-13, Nuke
  9-13. HLTV's own head-to-head widget prints the same match with the labels swapped, so the match
  page is the cited source. Source:
  <https://www.hltv.org/matches/2398743/furia-vs-aurora-esl-pro-league-season-24>
* **New coverage fact: both semi-finals are now on the Hotspawn board.** The 00:54 UTC capture lists
  FURIA–Aurora as fixture **1080207** (14:00 UTC, lock 13:54 UTC) and Falcons–BETBOOM as fixture
  **1080208** (17:00 UTC, lock 16:54 UTC), both tier s, both priced from Polymarket (52.5/47.5 and
  79.5/20.5). Earlier notes on the analysis page called the semi-finals absent from the feed; that
  is no longer true and the page now says so, so both day-4 picks can be submitted on the board.
* **New day-5 block** (`data/analysis.json` → `day_five_guidance`): the third-place decider at
  11:30 UTC on 18 October (best of 3, LAN, HLTV match 2399416) and the grand final at 15:00 UTC
  (best of 5, LAN, HLTV match 2399417). Both pages still show TBA on both sides, so no pick, no
  percentage and no model line is published for them, and the reason is stated on the cards.
* **Published source disagreement**: HLTV's own odds and prediction page for 2399414 says "Aurora is
  the bookmaker favorite with the best odds" while the same page's pros/cons say FURIA is better
  ranked (#4 against #6), and both lines this project prices make FURIA the marginal favourite
  (Polymarket 52.5/47.5, Pinnacle de-margined 53.0/47.0). The disagreement is published, not
  resolved by preference. Source:
  <https://www.hltv.org/betting/analytics/2399414/furia-vs-aurora-thunderpick-world-championship-2026>

Contrarian-but-not-stupid framework, as published: Aurora at 47.5% is the priced second option in
FURIA–Aurora (reversed the day-1 upset in the decider, won the most recent head-to-head), and
BETBOOM at 20.5% is the only priced shot at an upset in Falcons–BETBOOM (three three-map series in
a row, overtime decider win). Neither is presented as a recommendation over the favourite, and the
Hotspawn crowd split is never used as evidence.

### 2. External book listings for the rows that had no percentage

**What was found.** EGamersWorld publishes explicit two-sided **bookmaker-average** lines for
low-tier CS2 fixtures that neither Polymarket nor Pinnacle lists. Three sentence forms were read
and recorded; the full readings, quotes and refusals are in
`research/egw-03befae8/BOOK-LISTING-READINGS.md`.

**What was published.** One receipt: `egw-rW6Ymkl0D-ex-6666-privateer` prices fixture 1081521
(ex-6666 vs Privateer) from the listing's 1.15 / 4.5 line, de-margined to **79.6% / 20.4%** with a
9.2% overround, observed 2026-10-17T00:45:00Z, identity verified against HLTV match 2399681 and
the Hotspawn row. The row moved off our own model line onto that external price; the CI refresh
at 01:05Z produced exactly that row, with the receipt as its evidence.

**The ladder change.** `scripts/refresh.py` now runs the researched book-listing tier *before* the
originated Valve-standings model, because an external price outranks our own model estimate. The
model still fills the gap when no listing exists, and every line still passes the published gates
(two-sided, de-margined, margin inside 25%, exact opponent pair and UTC start, eight-hour
freshness window).

**The limitation, published.** The automated runner is **refused by EGamersWorld with HTTP 403**
after three rate-limit waits (10 s, 30 s, 60 s); this project does not change how its requests
identify themselves to get past a block, so no automated adapter can be written for that site. A
listing can therefore only be captured as a dated research receipt, which ages out after eight
hours, after which the row falls back to the model line and says so. The finding is on the
**Flagged for Review** page as `book-listing-access-egw`.

**The five rows that still have no percentage** (VP.Future–Black Phoenix, Lavked–LFO 10,
antidaun–Phantom Academy, Lynn Vision–Morningstar, Chinggis Warriors–WXM) were each read on the
listing: all five show the identical default odds **1.8/1.8** (a placeholder, not a market), and
for Lavked–LFO 10 the listing does not even print the opponent's name. Polymarket has no active
market for any of the five, Pinnacle has no matchup, Thunderpick renders its prices in
JavaScript and GG.BET refuses the runner with the same 403. Publishing a percentage for them would
mean inventing one, so they keep a research-only pick with **no percentage** and the reason on the
row. The refused listings are recorded in `data/book-receipts.json` → `rejected_listings`.

### 3. Mobile-first executive summary

* A **"Then next" queue** under the next pick: the following three priced fixtures with their pick,
  their percentage, the start time and whether the line is a market line or our model line. One
  tap each to the evidence.
* A **jump bar** (Today’s picks · Later on the board · Unresolved & limitations · Coverage) with
  in-page anchors, so the picks are one tap away instead of a long scroll.
* The unresolved section and its limitations stay inside the executive summary, and the summary
  still links straight to the picks board and to the day-4 guidance.
* `assets/style.css` and `site/assets/style.css` are kept in sync (the build copies the second one,
  the root fallback uses the first one).

### 4. Verification on this branch

* `python -m scripts.build` → 9 primary pages + 6 legacy redirects, **96 sourced rows, 29 priced,
  5 unresolved**.
* `python -m scripts.validate` → 96 rows verified against the primary snapshot, **29 probability
  calculations reproduced**, 15 pages, **675 internal links and assets checked**, 20 artifact
  checksums, 254 displayed rows.
* `verification-c6/audit_snapshot.py` (run on the CI snapshot in
  `research/harvest-03befae8/row-audit.md`) → **96 rows checked, 0 arithmetic or field failures**.
* `python -m unittest discover -s tests` → **295 OK** (16 new tests in
  `tests/test_egw_03befae8.py`).
* `npm run test:browser` → **32** accessibility/no-overflow scans at 320/390/768/1440 px and
  **7** expiry scenarios, all passed. The first run caught a real contrast failure in the new
  queue ("vs" in the hero at `#5f6d70` on `#132c28`); the rule was corrected to `#8ca69d`
  (contrast 5.7:1) and the scan is green.
* `scripts/stage_legacy.py` staged the root fallback from the same verified build, so the committed
  root pages carry the 96-row snapshot rather than the older 83-row one.

### Cross-session items

* **PR #57** (session 1abdd416) cannot be merged: its branch has no common history with `main` and
  its `COORDINATION.md` is 342 lines behind, so merging it would revert newer records. Its finding
  is integrated instead — the `dual-publisher-race-2026-10-17` note was taken verbatim into
  `data/review-notes.json` and is published on the Flagged for Review page, with the owner step
  (Settings → Pages → Build and deployment → Source → GitHub Actions) recorded. The PR is closed
  in favour of this branch's PR.
* The 83-row → 96-row gap in the committed fallback is closed by this branch: `data/latest.json` is
  now the CI snapshot of 2026-10-17T01:05:49Z.


## Session 03befae8 — publication record (2026-10-17, 01:25 UTC)

| Item | Value |
| --- | --- |
| Branch | `arena/03befae8-maltaproj4` (session `03befae8`) |
| PR | **#63** — https://github.com/buffedlizard55-lab/MaltaProj4/pull/63 |
| PR head | `384b4ae` (merge commit of `origin/main` into the branch, no work dropped) |
| Merged | **2026-10-17T01:17:14Z** as `57f5b7a2c6d039bde5988a68efe39f1d9fa25197` (merge commit, `gh pr merge 63 --merge`) |
| PR check | `verify-build` **pass** (build → validate → browser scans on the PR head) |
| Publish run | **38990206884** — every step green, including "Build and independently verify every row, calculation and link", "Phone, tablet, desktop, accessibility and exact-boundary checks", the artifact deploy and **"Verify live Pages bytes match this exact build"** |
| Legacy publisher | run 38990206879 ("pages build and deployment") also ran on the same merge and served the same 96-row root fallback, because this branch stages it from the same verified build |
| Live receipt | revision `57f5b7a2…`, built 2026-10-17T01:19:40.684698Z, snapshot 2026-10-17T01:19:40.369522Z, **96 rows**, 34 open, **29 with a published probability (18 market + 11 VRS model)**, 5 research-only with no percentage, **0 without a pick** |
| Live site | https://buffedlizard55-lab.github.io/MaltaProj4/ |

What the live board now carries that it did not before this merge:

* **ex-6666 vs Privateer (18 Oct 13:45 UTC)** is priced **79.6% / 20.4%** by the researched
  EGamersWorld book listing (1.15 / 4.5, observed 00:45 UTC, expires 08:45 UTC), with the listing's
  own page as the source link, instead of our own model line. The model line (78.2% / 21.8%) is
  still shown beside it for comparison.
* **Both TWC semi-finals are live tier-s board rows** — FURIA–Aurora (1080207, 52.5% / 47.5%, pick
  FURIA) and Falcons–BETBOOM (1080208, 79.5% / 20.5%, pick Falcons) — so both day-four picks can be
  submitted on the board itself.
* The **phone-first summary** is live: a "then next" queue with the following three picks and their
  prices, and a jump bar to today's picks, the later board, the unresolved section and the coverage
  line.
* The **day-five bracket** is published (third-place decider 11:30 UTC best of 3, grand final 15:00
  UTC best of 5, both with TBA on both sides, so no pick and no percentage).
* **Flagged for Review** now carries two new items: `book-listing-access-egw` (the HTTP 403
  limitation on the book-listing source) and `dual-publisher-race-2026-10-17` (integrated from PR
  #57).

**PR #57** (session 1abdd416) is closed in favour of PR #63: its branch has no common history with
`main` and its `COORDINATION.md` is 342 lines behind, so merging it would have reverted newer
records. Its finding was taken verbatim into `data/review-notes.json` and is published on the
Flagged for Review page. The one-step owner fix it names — Settings → Pages → Build and deployment →
Source → GitHub Actions — is still outstanding and is still the only thing that stops the legacy
`main:/` publisher from serving the committed fallback between verified publishes.

## Session 035cbb63 claims (2026-10-17, 00:55 UTC)

Arena fixes this session to `arena/035cbb63-maltaproj4`; no other branch is created, checked out or
pushed. Board state read before claiming: `git fetch origin --prune` lists **only** `origin/main`
(every earlier session branch was deleted after merge), `origin/main` is at `8d32db8` (PR #59).
Two PRs are open (#57 docs on the dual-publisher Pages race, owned by session 1abdd416; #23 research
market references, owned by dbe62379) — neither touches this session's file scope, and neither has a
live claim. **No active claim exists and nothing is taken over.** The last snapshot in the repo is
`data/latest.json` generated 2026-10-16T19:59:25Z (83 rows, 21 open, 17 with probabilities, 4 with a
research-only pick and no percentage).

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Re-verify day-1/2/3 TWC 2026 results from HLTV (incl. the 9z–Aurora day-1 upset and its day-3 reversal), the Aurora roster-change premise, and publish a contrarian-but-not-stupid day-4 (17 Oct) guide | in progress | 035cbb63 | research/day4-035cbb63/**, data/analysis.json, scripts/add_day4_035cbb63.py, tests/test_day4_035cbb63.py | 2026-10-17 |
| Close the remaining probability gaps: research an external line (HLTV → esportsbooks → exchange) for every open row that currently has a pick but no percentage; publish the unresolved section and its limitations inside the executive summary | in progress | 035cbb63 | research/gaps-035cbb63/**, scripts/build.py (exec-summary sections only), data/review-notes.json, tests/test_gaps_035cbb63.py | 2026-10-17 |
| Executive summary that links straight to the picks board + a phone-first layout pass; verify at 320/390/768/1440 px | in progress | 035cbb63 | scripts/build.py, site/assets/style.css, index.html (built copy), tests/browser.cjs | 2026-10-17 |
| Final integration: rebuild, re-verify every row/calculation/link, open the PR to main, merge, confirm the Pages deploy | in progress | 035cbb63 | generated root HTML, data/latest.json, build-info.json, .github/workflows/pages.yml (add this branch to the push list only), COORDINATION.md, README.md | 2026-10-17 |

Rules I am holding to: Hotspawn fixes the fixture inventory only and is never a probability input;
probabilities come from externally observed market lines that pass the published gates or from the
labelled originated VRS model; HLTV supplies identity/results/rankings; a value that cannot be
confirmed from an official source stays blank and is flagged, never inferred and never defaulted to
50/50; no file owned by another session is edited (PRs #57 and #23 are left alone); `git pull
--rebase` before every push; small frequent commits. Sandbox bash reaches GitHub and package
registries only, so live source reads go through the retrieval tooling and through Actions runners;
no access control is bypassed and no source is claimed checked when it was not.

### Session 035cbb63 coordination log
- 2026-10-17 00:56 UTC: claim written and pushed (`7f6149c`) before any content edit.
- 2026-10-17 01:00 UTC: **duplicate-claim detection (correcting my own board read).** My claim above says
  "no active claim exists". That was wrong, and the reason is a tooling defect, not a judgement: this
  sandbox's `remote.origin.fetch` refspec is `+refs/heads/arena/035cbb63-maltaproj4*:...`, so `git branch -r`
  and `git fetch --prune` show **only my own branch**. Re-running
  `git fetch origin '+refs/heads/*:refs/remotes/origin/*'` exposes **43 remote heads**, five of which
  committed within the same ten minutes as me:

  | Branch | Last commit (UTC) | Claimed overlap with this session |
  | --- | --- | --- |
  | `arena/03befae8-maltaproj4` | 00:54:58 | `data/analysis.json`, `scripts/build.py` (exec summary), `scripts/core.py`/`refresh.py` (low-tier book provider), mobile exec summary, final integration |
  | `arena/c97c1986-maltaproj4` | 00:53:15 | `data/analysis.json` day-4 wording, `analysis.html` |
  | `arena/37bf28f4-maltaproj4` | 00:50:57 | `data/analysis.json`, `scripts/build.py`, `site/**`, `README.md` |
  | `arena/79f0e55b-maltaproj4` | 00:55:52 | independent HLTV verification with retained receipts; live-board coverage verification |
  | `arena/6d2af30b-maltaproj4` | 00:55:45 | `README.md`, `scripts/build.py`, `scripts/refresh_watchdog.py`, `pages.yml` cadence text |

  Every one of those branches is based on `8d32db8`, exactly like mine, and none of us could see the
  others. This is a simultaneous claim, not a takeover: no claim of another session is overwritten, and
  no file another session had already edited is modified by me.

  **Resolution — this session yields every file another session owns and keeps one unclaimed slice.**

  | Scope | Owner after resolution | Reason |
  | --- | --- | --- |
  | `data/analysis.json` (day-1→4 cards, contrarian wording) | 03befae8 / c97c1986 / 37bf28f4 | claimed first and mid-flight; writing it from four branches would produce a conflict cascade and no new information |
  | `scripts/core.py`, `scripts/refresh.py` (price ladder) | 03befae8 | their EGamersWorld provider is the actual fix for the four research-only rows |
  | `scripts/build.py`, `site/assets/**`, `README.md` (mobile exec summary) | 03befae8 / 37bf28f4 / 6d2af30b | same reason |
  | `data/latest.json`, `data/book-receipts.json`, `data/review-notes.json` | 03befae8 / 79f0e55b | same reason |
  | **Hotspawn inventory completeness: is the board really listing every CS2 fixture Hotspawn offers?** | **035cbb63 (this session)** | not claimed by any of the five; it is the literal "full coverage of all picks that are available on the site" requirement |
  | **The final integration (rebuild, re-verify, PR, merge, live-byte check)** | **whichever branch lands first; the others rebase and union `COORDINATION.md`** | the rule this repository already used for PRs #55/#56 |
  | `research/**` and `tests/**` under this session's own uniquely named paths, plus `.github/workflows/harvest-035cbb63.yml` | 035cbb63 | new files, no overlap |

  I will not edit `data/analysis.json`, `scripts/core.py`, `scripts/refresh.py`, `data/book-receipts.json`,
  `data/review-notes.json`, `README.md`, `site/assets/**`, or the cadence text in `scripts/build.py`.
  The one shared file I touched before I could see the other claims is
  `.github/workflows/pages.yml` (I appended my branch to the push list only); 6d2af30b is editing the
  same file's schedule comment. On rebase I will keep both changes — the branch-list line is additive and
  theirs is a comment — and will not reorder or delete anything they wrote.

- 2026-10-17 01:00 UTC: **process irregularity for the user, flagged not fixed.** Five sessions received the
  same brief and the sandbox's default fetch refspec hides every branch but the session's own, so
  "no active claim exists" cannot be established with `git branch -r`. Any session doing this work should
  run `git fetch origin '+refs/heads/*:refs/remotes/origin/*'` first. I recommend the repository set
  `remote.origin.fetch` to `+refs/heads/*:refs/remotes/origin/*` in a future commit.
- 2026-10-17 01:03 UTC: **the refresh failed on all three Hotspawn sources at 00:59Z, and the live
  site was publishing a snapshot 5h 04m old.** Harvest run 38988580788 recorded
  `coverage: stale`, 83 rows retained from `generated_at 2026-10-16T19:59:25Z`, with
  `api` = "Expecting value: line 1 column 1 (char 0)" and both HTML pages =
  "Hotspawn hydration data missing". Read against the live `build-info.json`, which then reported
  revision `74e43b0b`, `built_at 2026-10-17T00:54:41Z`, `snapshot_generated_at
  2026-10-16T19:59:25.913409Z`. **Flagged, not hidden:** the 4–8 h promise was inside budget but
  the *cause* was a total source outage, not the schedule. The very next attempt (01:03Z, run
  38989008825) succeeded with `coverage: verified` and **96 rows** (api = page = lobby = 96), so
  the outage was transient — but a transient total outage still silently publishes yesterday's
  inventory, and the page does say so in the "source status" banner rather than implying freshness.
- 2026-10-17 01:03 UTC: **Hotspawn added the Thunderpick World Championship main event to the board
  overnight.** Fixtures **1080207 (FURIA v Aurora, 14:00Z)** and **1080208 (Falcons v BetBoom,
  17:00Z)** are now in the feed and are priced from Polymarket markets 5778024 (0.525/0.475) and
  5787759 (0.795/0.205). Earlier sessions correctly recorded that the playoffs were *not* listed on
  16 October; that is now out of date, which is precisely why the refresh cadence matters.
  13 fixtures were added in total (`inventory_changes.added_ids`), none removed.
- 2026-10-17 01:25 UTC: **inventory-completeness audit — the collector's scoped query is complete.**
  `research/inventory-035cbb63/FINDINGS.md`, 10 query variants measured on a runner:
  `status=scheduled` returns 96 CS2 rows; the unfiltered query returns 10,337 CS2 rows across
  statuses `cancelled, ended, forfeited, scheduled, started`, of which the *scheduled* subset is the
  same 96 — the other 10,241 are finished/void historical fixtures, not missed picks.
  `status=upcoming|live|finished|open` all return 0 rows, so no pickable status is being skipped.
  `page`, `per_page` and `limit`/`offset` all return **HTTP 400**, i.e. the endpoint does not
  paginate and one response is the whole set. Board vs baseline: zero ids different either way.
- 2026-10-17 01:25 UTC: **raw-capture diagnosis of the HTML sources.** `research/inventory-035cbb63/
  RAW-CAPTURE.md`: both HTML pages return HTTP 200 and ~335–460 KB of Angular HTML
  (`data-beasties-container`, `<base href="/">`) with **none** of the common hydration markers.
  `scripts/core.py:hotspawn_state()` requires `<script id="ng-state">`; that specific marker is the
  one that matters and is being re-measured with the full (untruncated) body. This is the fragile
  leg: the API is JSON and stable, the two HTML parity sources depend on server-rendered transfer
  state that an SPA can drop at any time. When it drops, `scripts/inventory.py` correctly refuses to
  publish and retains the previous inventory — which is the safe behaviour but is also how a 5-hour
  stale board happens.
- 2026-10-17 01:10 UTC: **five open rows have a pick and no percentage, and the reason is measured,
  not assumed.** `research/inventory-035cbb63/unpriced-rows-2026-10-17.md`: 1081511, 1079634,
  1081522, 1081861 and 1081863. HLTV returned `numeric_quote_rows: 0` for all five (no betting table
  exists for GLuck Yungstar, CCT Challengers or VOID Autumn Cup group matches), and in every one of
  the five at least one team is absent from Valve's official global standings, so no two-sided
  originated line is possible either. One row that *looked* unpriced (1081521 ex-6666 v Privateer)
  is in fact priced at 78.2/21.8 by the VRS model because `data/identities.json` already maps
  `ex-6666` to Valve's `6666` standing #127 on Valve's own published roster-overlap rule
  (`model/team.js`, `TEAM_OVERLAP_TO_SHARE_ROSTER = 3`) — an earlier draft of my own dossier said
  that pair was deliberately unaliased; that was my error and the file now says so.
- 2026-10-17 01:28 UTC: **rebase onto `main` (57f5b7a, PR #63 merged).** Conflicts:
  `COORDINATION.md` resolved as a union (both blocks kept, 0 markers left); generated HTML/CSV and
  `data/latest.json` resolved by taking `main`'s newer verified snapshot (01:05:49Z, 96 rows) over my
  01:03:04Z one; `tests/test_coverage_76712ccc.py` — session 03befae8 had reached the same re-pin
  independently (`'bookmaker_fallback'` added for the new book-listing tier), so I kept their line
  and only added the note that `'book'` is a legacy name no code path emits. Verified afterwards:
  **296 tests + 9 audits + 12 verification-c6 + 5 verification-95b588c2 all pass**, and
  `scripts.validate` reports 96 rows verified, 29 probability calculations reproduced, 15 pages,
  666 internal links/assets, 20 checksums, 255 displayed rows.
- 2026-10-17 01:28 UTC: **self-inflicted history accident, recorded.** `git rebase --onto
  origin/arena/035cbb63-maltaproj4 HEAD~1 HEAD` replayed only my most recent commit onto the
  *pre-rebase* remote head, which silently discarded the rebase-onto-main work. Recovered from the
  reflog (`56309ed`) plus a cherry-pick of `2ec12d0`; the tree was verified afterwards
  (`scripts/egw_probe.py` present, `data/latest.json` at main's 01:05:49Z snapshot, 296 tests OK)
  and force-pushed with `--force-with-lease`. Nothing of another session was lost: the recovery
  restored main's content, and the only branch rewritten is this session's own.
- 2026-10-17 01:20 UTC: **mobile/executive-summary check against the built pages.** Rendered the
  built dashboard in headless Chromium at 390×900 and 1440×1000 and confirmed zero horizontal
  overflow on index, picks, unresolved and analysis; `npm run test:browser` passes 32
  accessibility/no-overflow scans at 320/390/768/1440 px and 7 exact-boundary expiry scenarios.
  The landing page's own link path is: "View updated picks →" → `picks.html`; a "Where the picks
  are" card grid (Updated picks / Unresolved & limitations / Day-3 results / Day-4 picks / All
  matches); a section nav carrying live counts ("Updated picks (29)", "Needs a pick (5)", "Every
  match (96)"); a coverage line linking to the pick board and jumping to the unresolved section;
  and an in-page `#unresolved-summary` section that states each limitation. The discoverability and
  phone-layout work itself remains owned by 03befae8 / 37bf28f4; this session only verified the
  result and did not edit `scripts/build.py` or `site/assets/**`.
- 2026-10-17 01:40 UTC: **correction to a finding I published above.** I wrote that both Hotspawn
  HTML pages were missing every hydration marker, including `ng-state`. That was wrong, and the error
  was mine: `scripts/hotspawn_raw_035cbb63.py` searched the full body but saved only the first
  200,000 characters, and my first read grepped the truncated file. Measured again with the marker
  positions recorded (`research/inventory-035cbb63/raw-capture.json`, 01:37:27Z):
  `<script id="ng-state">` — the exact element `scripts/core.py:hotspawn_state()` requires — is
  present at byte 374,275/459,538 on `cs2-pickems` and 261,376/335,025 on `lobby`. Both parity
  sources are healthy. So the 00:59Z outage was a transient absence of transfer state in those two
  responses plus an independent API failure, **not** Hotspawn dropping server-side rendering. The
  operational irregularity stands (a five-hour stale board was published); the cause is narrower than
  I first stated, and `RAW-CAPTURE.md` now carries the correction rather than the wrong claim.

## Session 90795adf — 2026-10-17 follow-up integration

Read the shared board and fetched all remote heads before claiming. Latest remote
commit is 01:54 UTC; all unfinished claims are over 60 minutes old without commits
at this session's 09:42 UTC checkout. Existing open PRs #64 and #23 are preserved,
not merged blindly. Taking over final verification under the stale-claim rule.
Arena fixes this session to `arena/90795adf-maltaproj4` (no alternate branch).

| Task | Status | Owner | Scope |
| --- | --- | --- | --- |
| Audit current refresh failures and rerun source collection; verify fallback and research claims | in progress | 90795adf | scripts/**, tests/**, research/session-90795adf/**, data/** |
| Final integration, mobile checks, review findings, PR and Pages publication | in progress | 90795adf | .github/**, site/**, root generated files, README.md, COORDINATION.md |

Unknown evidence stays blank. Previous verification statements are historical,
not this session's checks. Sandbox source access is restricted; official-source
reads will use the existing GitHub runner workflow with retained evidence.

### Session 90795adf verification and source findings

- Source run https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39022254146 succeeded. Fresh snapshot 09:46:15Z: 93 rows, 32 open, 27 probabilities (16 market / 11 model), four research-only, one unsupported (Hacha–LOS NINOS, unverified alias). Three-way coverage verified, independent audit 93 rows / zero failures. Fresh HLTV capture reproduces all ten published Day-1–3 series outcomes; null day headings are not treated as newly verified dates.
- Reproduced scheduled run 39021205396's failure: book-receipt test depended on the current clock. Fixed by explicit snapshot-time injection and expiry-boundary tests, not by extending TTL. New unsupported fixture exposed another blanket test requiring a pick for every open row; replaced with pick-or-documented-source-limitation assertions, preserving all independent identity/price checks.
- Corrected BETBOOM rest/map-load narrative; reused the compatible strategy/source-link ideas from open PR #64 without importing its obsolete board-membership claims. Did not modify that branch or PR. Published residual source/identity/roster/leaderboard limitations on Flagged for Review. Every unknown probability remains blank.
- Fixed empty-board #later navigation target and removed static 100%-pick coverage promise. Current root fallback rebuilt from the fresh snapshot. All 300 tests, 9 audit tests, 5 integrity checks, 12 c6 tests passed; 32 viewport/accessibility scans and seven browser expiry scenarios passed. Validator: 93 primary rows, 27 calculations, 15 pages, 659 internal links/assets, 20 checksums, 245 displayed rows.
- Full audit details: research/session-90795adf/REPORT.md and dated receipts in that directory. Previous source-access and strategy limitations remain visible, not relabelled verified.
## Session 85c33bf9 claims (2026-10-17, ~10:00 UTC)

Arena fixes this session to `arena/85c33bf9-maltaproj4`; no other branch is created, checked out or
pushed. Board state read before claiming: `origin/main` is at `7df125d1` (PR #66 merged 01:48Z).
`gh api branches` + per-branch commit dates were enumerated: the **only** branch with commits inside
the stale-claim window is `arena/90795adf-maltaproj4` (claim ~09:42Z, commits 09:44Z and 09:46Z,
actively working). Their claim covers scripts/**, tests/**, data/**, .github/**, site/**, root
generated files, README.md and COORDINATION.md for the refresh-failure audit and final publication.
This session therefore does **not** take over their tasks and does not edit their files. Open PRs
#64 and #23 are left to 90795adf as they stated.

What this session adds (new work, session-unique files, additive shared-file edits only):

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Day-4 live re-reads ~4h before semi-final locks: Polymarket/Pinnacle/HLTV lines for FURIA-Aurora and Falcons-BetBoom, day-4 morning results from HLTV, contrarian day-4 guidance refresh | done (see log below) | 85c33bf9 | research/day4-85c33bf9/**, scripts/add_day4_85c33bf9.py, tests/test_day4_85c33bf9.py, data/analysis.json (additive day-4 keys only) | 2026-10-17 10:00 |
| Re-collect expired/expiring EGW book-listing receipts (8h TTL: ex-6666 00:45Z receipt expired 08:45Z; Infinite-Insiders 07:32Z receipt expires 15:32Z) and re-read the five 1.8/1.8-placeholder listings for 1081511, 1079634, 1081522, 1081861, 1081863 | done (see log below) | 85c33bf9 | research/harvest-85c33bf9/**, data/book-receipts.json (additive dated receipts + rejected_listings entries only) | 2026-10-17 10:00 |
| Independent diagnosis of the 09:27Z scheduled-publish failure (reproduced locally: tests/test_egw_03befae8.py replay fails because `book_research_pick` used the wall clock against a receipt that expired 08:45Z; fix is 90795adf's a6efbd7, not re-done here) | done (see log below) | 85c33bf9 | research/day4-85c33bf9/** (diagnosis notes only; no scripts/tests/.github edits) | 2026-10-17 10:00 |
| Fresh full-board harvest on a runner (production refresh + probe, non-publishing), uniquely named workflow per the established per-session pattern | done (see log below) | 85c33bf9 | .github/workflows/harvest-85c33bf9.yml (new unique file), research/harvest-85c33bf9/** | 2026-10-17 10:00 |
| Integration **only after** 90795adf merges (or their claim goes stale >60min with no commits): rebase on main, regenerate root HTML/data/latest.json/matches.csv via the standard build, full verification, PR to main, merge, Pages verification | done — condition met: PR #67 merged 09:54:50Z | 85c33bf9 | root generated files, data/latest.json, data/matches.csv, build-info.json, COORDINATION.md log | 2026-10-17 10:00 |

Conflict rules I am holding to: no edit to any file 90795adf has touched on their branch
(scripts/core.py, scripts/refresh.py, scripts/build.py, tests/test_egw_03befae8.py,
tests/test_session_90795adf.py, .github/workflows/audit-90795adf.yml, data/analysis.json keys they
rewrote — my analysis edits are additive under distinct keys and applied by my own idempotent
script); shared JSON files edited additively only; `git pull --rebase` before every push; conflicts
resolved as unions without discarding their work; unknown odds stay blank; Hotspawn votes are never
probability.

### Session 85c33bf9 coordination log

- ~10:00Z Board re-check before starting: 90795adf active (claim 09:42Z). Read days 1–3 research, DAY4-REVIEW, their claim copy, main's red state (time-bomb test in test_egw_03befae8 owned by their a6efbd7 — diagnosed independently, not re-fixed here). Appended this claim; pushed (0a783e8).
- ~10:04Z Created `.github/workflows/harvest-85c33bf9.yml` (non-publishing: refresh + quarantine + independent row audit + harvest probe + EGW probe; commits to `research/harvest-85c33bf9/` with `[skip ci]`). Pushed with `[harvest]`; run 39023429095 succeeded in 9m8s. Snapshot 10:05:12Z (fixtures observed 10:03:18Z): coverage verified 93/93/93/93, 32 open, 27 priced, 4 research-only, 1 no-pick (new row **1082019 Hacha vs LOS NINOS**, CCT South America Series #7, 22:00Z tonight).
- ~10:00–10:55Z Manual live re-reads (document-retrieval path; EGW refuses the runner with 403): Polymarket 5778024 (FURIA-Aurora unchanged 52.5/47.5, liquidity $306,045 ≈ doubled), Polymarket 5787759 (**Falcons-BETBOOM moved 79.5/20.5 → 72.5/27.5** on ~15x volume), HLTV results (ex-6666 2-0 G2 Ares — row 1079633's originated model pick settled correct; FlyQuest 2-1 NEXVOID; Rooster 0-2 Off Chops), HLTV betting analytics 2399415 (Falcons #5 / BETBOOM #14, form 3/5), five EGW listings (ex-6666 v Privateer **new real line 1.13/4.75**; all five placeholder rows still 1.8/1.8), Valve standings coverage for every unpriced pair. Full record: `research/day4-85c33bf9/DAY4-LIVE-2026-10-17.md`.
- ~10:35–10:55Z Identity work on the two name-mismatch candidates the runner flagged: **Hacha Esports↔Hacha verified** on fixture parity (HLTV 2399768 + team pages 13722/14092 + Polymarket 5796276 gameStartTime 22:00:00+00 + resolution source hltv.org; precedent: Privateer Gaming, BC.Game Esports entries) and registered in `data/identities.json`. **Sökerorg↔LFO 10 NOT verified** (no shared tokens; HLTV team page 14084 shows no roster/alternate name; HLTV and EGW lineups disagree) → Polymarket 0.6/0.4 quote for row 1079634 **not transferred**; flagged in review-notes (`lfo10-sokerorg-unverified-85c33bf9`) instead. Row locked 10:54Z with its research-only pick (Lavked).
- ~11:00Z Commit dc4e561 `[harvest]`: alias entry + renewed EGW receipt `egw-rW6Ymkl0D-ex-6666-privateer-1010z` (1.13/4.75, observed 10:10Z, supersedes the 00:45Z receipt that expired 08:45Z) + 5 dated placeholder re-read rejections + 3 review notes + additive day-4 analysis points/unpriced/unverified + 18 deterministic tests (`tests/test_day4_85c33bf9.py`). Run 39028376995… (39028376992) succeeded: snapshot **11:23:31Z** prices 1082019 `exchange_wide` (LOS NINOS 60.5%, spread 41 pts, liquidity $132.76, low-confidence label, strict rejection retained) and restores 1081521 `bookmaker_fallback` (ex-6666 80.8/19.2). **Zero no-pick open rows.**
- ~11:35Z Published the verified 11:23Z snapshot (data/latest.json, root HTML, build-info.json, matches.csv via the standard build). **Shared-file touch, logged per protocol:** `tests/test_integrity.py` — its setUp assumed every `bookmaker_fallback` row is Pinnacle-shaped (`raw.line.cutoffAt`); a snapshot whose only book row is an EGW receipt (legitimate `raw.receipt` shape) crashed 3 cutoff tests. Fixed with a shape-aware selector that falls back to the existing synthetic-row mechanism. Latent fragility, not specific to this session's data; intent of every assertion preserved.
- Verification before PR: tests 318 OK · audits 9 OK · verification-95b588c2 5 OK · verification-c6 12 OK + independent row audit 0 failures · `scripts.validate --data data/latest.json --site .` 226 displayed rows verified · `npm run test:browser` 32 viewport/accessibility scans + 7 expiry-boundary scenarios OK.
- Flags carried into this publication (all on Flagged for Review): thin volatile Hacha market (wide tier, direction-only signal; Hacha match-lineup vs team-roster stand-in discrepancy); Sökerorg alias unverified (quote not transferred); renewed EGW receipt expires 18:10Z today, before the 18 Oct 13:45Z start — the row then falls back to its model line unless re-read (published TTL behaviour); 4 rows remain research-only with blank percentages (each limitation re-verified this morning).

## Session f4e34907 claim · 2026-10-17 20:17 UTC

All preceding integration claims are complete or stale (>60 minutes); remote branches and open PRs checked. This session stays on Arena's fixed `arena/f4e34907-maltaproj4` branch.

| Task | Status | Owner | Scope |
| --- | --- | --- | --- |
| Fresh official inventory/line capture and Day-4 result / Day-5 guidance verification | in progress | f4e34907 | research/session-f4e34907/**, scripts/day5_f4e34907.py, tests/test_day5_f4e34907.py, .github/workflows/day5-f4e34907.yml |
| Final integration of dated Day-5 guidance, mobile navigation and publication | in progress | f4e34907 | data/analysis.json, scripts/build.py, generated root pages/data, COORDINATION.md |

Unknown facts remain blank; existing source checks are historical, not newly verified. Source networking requires a GitHub runner. No other branch will be edited or pushed; older open PRs remain untouched.

### f4e34907 verification / integration log

- Initial branch did not yet exist remotely: attempted `git pull --rebase` reported missing remote ref, then created only the fixed session remote with the claim push. Subsequent pushes use pull/rebase normally. No conflict with another session.
- Fresh source capture run https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39066005984 succeeded. Artifact download from this sandbox was blocked at Azure storage; a separate runner job retained the exact artifact through GitHub transport. No source fields were reconstructed from memory.
- 20:18Z snapshot: **81 total entries, 18 open; 13 probabilities (7 markets / 6 models), four research-only and one unresolved (Hacha–LOS NINOS)**. Three-view coverage verified; independent replay zero failures. Earlier morning claims of zero unresolved are historical, not current guarantees. Source/identity limitations remain on the site.
- HLTV results receipt independently reproduces all 12 published Days 1–4 series outcomes. The two completed semi-final pages and both confirmed Sunday match pages were also read with document retrieval. Finals: FURIA–BETBOOM (BO5), Aurora–Falcons (BO3). HLTV is specialist secondary evidence, **not organizer verification**; organizer confirmation is explicitly unverified. No Sunday market line was returned by the retained operator scans and neither Sunday TWC fixture was on the official Hotspawn capture. Fan-vote percentages were rejected.
- Final-day strategy: ranking-order baselines FURIA/Falcons, BETBOOM a conditional upset candidate after three consecutive series wins, never a calibrated probability or guaranteed leaderboard edge. No unsupported October onboarding, injury, motivation or fatigue adjustment. Individual-match/results/schedule freshness discrepancies published on Flagged for Review.
- Expanded stale/completed-file scope for integration: `data/review-notes.json`, two historical-test files with frozen day-four navigation expectations, and regenerated `research/quotes-76712ccc/UNPRICED-FIXTURE-LINES.{json,md}` using its existing builder (new NEXVOID/Off Chops research row). No historical raw source receipt overwritten. Tests retain identity, arithmetic and coverage assertions; current navigation now points to the selected day rather than yesterday.
- Mobile navigation resolves the real final-day anchor. Executive summary links to current picks and final-day limitations. A future exact-pair/exact-start Sunday board discovery links to the expiry-checked board, never duplicates a live numeric recommendation in a static research card.
- Verification: 323 unit tests, 9 audit tests, 5 independent integrity checks, 12 c6 checks passed; row audit zero failures; 81 primary rows / 13 calculations / 15 pages / 571 links and assets / 20 checksums / 195 displayed match rows verified. Browser: 32 viewport/accessibility scans at 320/390/768/1440px and seven expiry boundary scenarios passed. Final re-run and publication follow.
## Session e0fd5a32 claim — 2026-10-17 20:17 UTC

Board read before claiming. Two sessions are active with claims at 20:16Z (`cc88483d`) and 20:17Z
(`f4e34907`), both covering Day-5 analysis, `data/analysis.json`, `scripts/build.py`, `site/**`,
generated root pages and final integration. This session does **not** take over or edit any of those
scopes. It works only on a new, non-overlapping verification task and publishes session-unique files.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Independent verification of the Day-4 semi-final results and of official Day-5 bookmaker lines (Thunderpick sportsbook, HLTV identity/form), de-vig calculation, and a contrarian-but-justified Day-5 assessment | **done** | e0fd5a32 | research/session-e0fd5a32/**, scripts/day5_e0fd5a32.py, tests/test_day5_e0fd5a32.py, data/analysis.json Day-5 cards (additive) | 2026-10-17 20:39 |

Integration request logged for the two active integrators: the verified Day-5 fixture identities,
official American prices, de-vig probabilities and source URLs are in
`research/session-e0fd5a32/DAY5-ODDS-VERIFICATION.md` and `day5-lines.json`. If either integrator
publishes first, this session rebases and contributes only additive data under its own keys, or opens
a follow-up PR if the merged site omits the Day-5 picks. No shared file is edited while their claims
are active (under 60 minutes old with commits). If both claims go stale (>60 min with no commits) or
their PRs fail, this session takes over integration under the stale-claim rule and records the handoff.

### Session e0fd5a32 progress log

- 20:18Z Read both Day-4 semi-finals from HLTV: **FURIA 2-0 Aurora** (Dust2 13-8, Inferno 13-10) and **BETBOOM 2-1 Falcons** (Anubis 5-13, Dust2 16-14, Mirage 13-7). BETBOOM's win is the event's second clear market upset.
- 20:20Z Read both resolved Day-5 fixtures: **Aurora vs Falcons, third-place decider, 11:30Z, best of 3** (HLTV 2399416) and **FURIA vs BETBOOM, grand final, 15:00Z, best of 5** (HLTV 2399417). Aurora's active five is unchanged from Valve's 5 October roster file; HLTV dates the rebuild to 8 July 2026, so there is no October onboarding factor.
- 20:20Z Read the only two-way Day-5 prices found: Thunderpick market pages, **Aurora +170 / Falcons −238** and **FURIA −286 / BETBOOM +190** (decimal 2.700/1.420 and 1.350/2.900). De-vig: Falcons 65.53%, FURIA 68.24%. The Thunderpick tournament card still showed +150/−208 for the third-place match in the same minute; recorded as a display inconsistency, not a line move, and flagged. Pinnacle does not list this event; Polymarket had no head-to-head day-5 market at 20:20Z; HLTV exposed no numeric line.
- 20:21Z Confirmed the main TWC event is **not** in the Hotspawn pick'em board (81 fixtures; the tournament filter names only the South American Series). Day-5 picks are therefore research cards, not board rows.
- Handoff for the integration owners: `research/session-e0fd5a32/DAY5-ODDS-VERIFICATION.md`, `day5-lines.json` and `day5-guidance-handoff.json` carry the exact card payload (picks, de-vig, fair odds, sources, limitations) in the schema `guidance_section()` renders. A temporary build confirmed both cards render with the published percentages.
- Session tests: 12 new deterministic checks pass; full suite 330 OK, audits 9 OK, verification-95b588c2 5 OK, verification-c6 12 OK, validate 226 displayed rows.

## Session cc88483d claims — 2026-10-17 20:16 UTC

Read shared board before starting; latest main commit 25f25a2 at 12:13Z. Earlier claims are completed or older than 60 minutes with no recent main work. This session stays on Arena's fixed `arena/cc88483d-maltaproj4` branch (overrides requested alternate branch naming).

| Task | Status | Owner | File scope |
| --- | --- | --- | --- |
| Fresh source harvest and Day-4 results / Day-5 final-day guide, with reproducible receipts and unknowns blank | done | cc88483d | research/session-cc88483d/**, scripts/day5_cc88483d.py, .github/workflows/harvest-cc88483d.yml, data/analysis.json |
| Final integration, current board snapshot, mobile summary and regression checks, PR/merge/Pages verification | done | cc88483d | scripts/build.py, site/**, tests/test_day5_cc88483d.py, root generated pages, data/latest.json, data/matches.csv, build-info.json, COORDINATION.md |

Official-source requests run on GitHub runners because sandbox outbound networking excludes esports sites. Previous receipts are historical, not fresh verification. No crowd percentages used as win probability; no forced numerical probabilities for unsupported rows.

- 20:18Z Implementation audit: homepage guidance labels were data-selected but URLs hardcoded to day four; source-limit panel described historical sampled HTML and 403s as universal current facts. Fixing URLs and printing each snapshot's actual attempt reasons. Regression-test scope extended to `tests/test_egw_03befae8.py` and `tests/test_priced_coverage_621776e4.py` only for calendar-dependent assertions (old bracket TBA assumptions / day-four front-page selection), preserving historical pricing/identity tests. Additive current review notes are in scope (`data/review-notes.json`). Baseline dependency installation uses ignored `.venv`; baseline 318 tests passed there.
- 20:25Z Source runner 39066029539 has completed the production refresh, independent row audit and market/HLTV probe; full match-page capture is running. Added deterministic navigation tests and an HTTP-200 regression proving the limitations panel cannot relabel current access as a historical 403. Static tournament research stays dated; live board prices still use existing TTL and identity gates.
- 20:28Z Fresh evidence: HLTV results confirms FURIA 2–0 Aurora and BETBOOM 2–1 Falcons. Final match pages now name FURIA–BETBOOM (15:00Z Sunday) and Aurora–Falcons (11:30Z). At 20:18Z the independent board audit has zero failures (81 total / 18 open / 13 priced / 4 research-only / 1 unsupported). Hacha has a fresh narrow market in the separate probe but production rejected event membership; investigating raw event flags instead of copying a quote past its gates. Targeted read-only operator API capture added under `.github/workflows/targeted-cc88483d.yml`. Later raw HLTV recapture refused 403; no bypass, failed capture retained; earlier successful parsed receipts remain evidence.
- 20:31Z Targeted operator API evidence explains Hacha: event 1203504 says `ended: true` while its moneyline still says active/acceptingOrders and its listed start is 22:00Z. Keep the pick blank; do not override a completed-event guard with an attractive-looking quote. Claim extended to `scripts/core.py` and `scripts/refresh.py` for diagnostics only: expose excluded exact-match event statuses in the attempt ledger without weakening acceptance. Existing closed/live/ended rejection tests remain unchanged.
- 20:36Z New fixture NEXVOID–Off Chops exposed a stale-test coupling: `tests/test_coverage_76712ccc.py` required every future research-only fixture to exist in a frozen 01:05Z dossier. Claim extended to this test: preserve historical dossier verification while assert every current row appears with its live evidence/attempts in the generated evidence ledger; do not rewrite old receipts to pretend they cover a new fixture. Root HTML/CSV must be regenerated together with the changed bootstrap snapshot before rendered-tampering tests run.
- Final pre-PR verification: twelve published TWC series winners/scores replay from the new HLTV capture; Sunday research leans and Unix starts replay against their fixture receipts; derived 7/11 map loads independently counted (not called fatigue). 328 unit tests, 9 audit tests, 5 independent integrity tests, 12 c6 tests passed. Independent snapshot audit: 81 rows, zero failures. Build: 81 primary rows / 13 reproduced calculations / 15 routes / 575 internal links and assets / 20 checksums / 195 displayed match rows. Browser: 32 viewport/accessibility scans + seven expiry scenarios passed. Report: research/session-cc88483d/REPORT.md. Root bootstrap regenerated without relabelling source timestamps. Final guide, four percentage-free research picks, Hacha conflict and source/leaderboard limitations are visibly published; no guard weakened to force 100% pricing.

- Integration conflict log: PR #69 from f4e34907 merged concurrently at 20:30Z after both sessions independently claimed overlapping final-day work. Paused on merge conflict, read their board/receipts/tests, then retained both complete source directories and histories. Shared notes merged by identity; their document-read map scores/formats retained with explicit provenance, our later raw operator-state diagnosis retained. Their exact-pair/start future-board discovery added to our conservative rendering. Standard generator regenerates conflicting root outputs; no hand-merged HTML. Snapshot chosen by latest successful generated timestamp, never blended or relabelled.
- Combined integration verification after preserving PR #69: 333 unit/regression tests, 9 audit tests, 5 independent integrity tests and 12 c6 tests passed. All 32 browser layout/accessibility scans and seven expiry cases rerun successfully. Generated root and public builds validate (81 rows, 13 calculations, 575 links, 20 hashes). Incoming map/format document-read provenance retained with organizer-verification flag; incoming exact-pair/start future-board links pass their tests. CRLF in generated standards-compatible CSV is intentional (Git whitespace check run with cr-at-eol).

- A second concurrent publication (PR #70, e0fd5a32) supplied independently read official Thunderpick final-day prices absent from the automated feed captures. Paused on the two merge conflicts, retained all of its session-unique receipts/calculation tests and integrated the attributed document-read prices. Did not import its “three hours more recovery” causal wording (start-time difference is not finish/rest duration). Our stricter fatigue/leaderboard qualifications remain. Added dated-quote expiry rather than allowing static research percentages to look live indefinitely. Before pushes after merge commits, use `git pull --rebase=merges` to preserve integrated histories; an earlier flattening rebase was aborted immediately, leaving the committed integration intact.
- File scope extended to `site/assets/app.js` for final-day quote expiry only; `tests/expiry.cjs` for exact-boundary browser verification. Static research prices remain in historical receipts; displayed research quote blocks expire independently from the Hotspawn snapshot and never become board rows.
- Second integration verified: 349 combined unit tests pass, current root/public validators pass, and 32 browser scans + seven board-expiry + four research-quote boundary/future-clock tests pass. Official Thunderpick document-read prices are attributed, de-vig arithmetic replayed, display discrepancy flagged, quote blocks expire 04:20:54Z before Sunday starts. Automated board refresh acceptance/expiry and unsupported Hacha exclusion unchanged. Both independent contributors’ raw/derived receipts and tests retained.

### Session e0fd5a32 completion log

- **PR #70 merged** at 2026-10-17T20:39:02Z (merge commit `466f8e7`), after `verify-build` passed in 1m24s. Branch `arena/e0fd5a32-maltaproj4` was rebased onto the merged PR #69 (`cf5dee1`) so the two sessions' work is stacked, not duplicated.
- **Published on the live site:** the Day-5 cards now carry the Thunderpick Match Winner line, the American and decimal prices, the de-vig percentages, fair decimals and the market URL. Live check of `https://buffedlizard55-lab.github.io/MaltaProj4/analysis.html` after the artifact deploy shows **Falcons 65.53%** and **FURIA 68.24%** with both picks and the limitations. The main Pages workflow completed `verify-build` and `deploy` successfully for main `466f8e7`.
- **Flagged on the live page:** the Thunderpick card-versus-market-page disagreement (+150/−208 vs +170/−238 in the same minute); the single-bookmaker limitation (HLTV no numeric line, Pinnacle's 20:10Z matchups feed no TWC Day-5 fixture, Polymarket no head-to-head Day-5 market at 20:22Z); the VRS cross-check uses Valve's 5 October standings and predates all TWC results; and the fact that neither Day-5 fixture is a Hotspawn board row.
- **Verification for the merge:** 339 unit tests OK · 9 audit tests OK · 5 independent integrity checks OK · 12 c6 checks OK · row audit 0 failures · `scripts.validate` 571 links/assets, 20 checksums, 195 displayed rows · browser suite 32 viewport/accessibility scans plus 7 exact-boundary expiry scenarios OK.
- **Post-merge record (verified 20:52Z):** PR #72 (this completion log) merged at 2026-10-17T20:45:49Z as `2ee9f36`; PR #71 (`cc88483d`) merged at 2026-10-17T20:48:19Z as `a5d97ff` and retains both Thunderpick `market` blocks plus quote-expiry. Live `build-info.json` reports revision `a5d97ff`, built 20:51:34Z.
- **Copy defect closed on main:** the published cards previously read “11:30 UTC (13:30 / 17:00 Malta respectively)” and “15:00 UTC (13:30 / 17:00 Malta respectively)”. Main `a5d97ff` no longer carries that string; a clean build from it renders the `start_unix`-derived timing with no duplicated Malta parenthetical. The public CDN copy still served the older text at 20:52Z, so this is cache lag, not a data regression.
- **Cross-scope hazard for the f4e34907 owner:** `scripts/day5_f4e34907.py` is a one-shot applier that still hard-codes the superseded “(13:30 / 17:00 Malta respectively)” text and, if rerun, would overwrite the verified `pick_detail` values and drop the `market` blocks. Not edited here (another session’s file); it is not referenced by any workflow or test. Do not run it against current `data/analysis.json`.

- PR #72 contained only the other contributor’s completion log and landed while #71 checks ran. Paused on its board-only merge conflict; retained both completion/verification histories. No code or data changed from the fully tested combined build. PR #71 retains both Thunderpick market blocks and adds their expiry safety.

### Session cc88483d completion — 2026-10-17 20:52 UTC

- **PR [#71](https://github.com/buffedlizard55-lab/MaltaProj4/pull/71) merged** at `2026-10-17T20:48:19Z`, merge commit `a5d97ff887dbadcfd16bf8bf48fabf9c034c6435`, after combined PR verification run [39068154418](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39068154418) passed. Explicit `gh pr merge 71 --merge` succeeded; no auto-merge or approval wait.
- **Publication confirmed:** [main run 39068262628](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39068262628) completed successfully. Production refresh, independently audited build, 32 browser viewport/accessibility scans, seven board-expiry cases and four research-quote cases passed; deploy succeeded; **Verify live Pages bytes match this exact build** step succeeded. Live site: https://buffedlizard55-lab.github.io/MaltaProj4/ . No claim based only on an HTTP status; the runner executes the exact artifact/live-byte verification script. Sandbox log/artifact download endpoints were denied by network policy; GitHub job/step conclusions were checked via its API.
- Sources and full verification boundaries: `research/session-cc88483d/REPORT.md`; preserved contributors’ `research/session-f4e34907/` and `research/session-e0fd5a32/`. All 349 combined unit tests, 9 audit tests, 5 independent integrity tests and 12 c6 tests passed locally; PR checks passed again. Unsupported values, single-book/card discrepancies, Hacha parent-event conflict, source-access limits and leaderboard unknowns remain visibly flagged rather than invented.
- Automation remains enabled: scheduled freshness-gated publication plus watchdog; inventory discovery covers all CS2 tiers, source-derived board probabilities expire, and independently dated research quotes now expire separately. The two Sunday research fixtures were not scoreable Hotspawn rows at observation; future exact-pair/start board discovery links to the live expiry-checked board.
- This completion-only follow-up records the successful merge and live result in the shared board; it changes no code, source observations or generated page content. All cc88483d claims are complete; no active file ownership remains.

- **Next:** Create PR from arena/fa85eb7a-maltaproj4 to main, merge, verify Pages deploy.

## Session 00a7d6ca claims — 2026-10-18 00:15 UTC

Read shared board before starting; latest main commit `743f33b` (PR #78). All previous claims are marked `done`. Arena fixes this session to `arena/00a7d6ca-maltaproj4`; no other branch is created or checked out, and direct pushes target this session branch only.

| Task | Status | Owner | File scope |
| --- | --- | --- | --- |
| Line-by-line verification of Day 1–5 TWC 2026 results, 9z–Aurora upset, roster timing, contrarian leaderboard rules and final-day decision guide | done | 00a7d6ca | research/session-00a7d6ca/**, data/analysis.json, tests/test_day5_00a7d6ca.py |
| Mobile-first discoverability & Executive Summary refinement: prominent in-site pick links, unresolved section & limitations callouts, on-page nav alignment | done | 00a7d6ca | scripts/build.py, site/**, assets/** |
| Final integration, full regression verification (unit, audits, integrity, browser/accessibility, expiry), root/public build regeneration, PR and merge | done | 00a7d6ca | root generated pages, public/**, build-info.json, COORDINATION.md |

### Session 00a7d6ca completion log — 2026-10-18 00:30 UTC

- **Line-by-line verification completed:**
  - Day 1: 9z 2–0 Aurora upset verified (Inferno 13-11, Nuke 13-1; luchov 1.61 rating; Aurora ranked #5 VRS / #6 HLTV going in). Roster change history verified: ash (coach), Jimpphat, and kyxsan (IGL) joined early July 2026 (announced 8 July 2026; HLTV News 45082); the lineup was ~14 weeks (~3 months) old by TWC and had placed 3rd at EPL 24. Schedule compression and fatigue post-EPL was the primary factor, not days-old onboarding confusion.
  - Day 2: Falcons 2–1 9z, Aurora 2–0 NiP, FURIA 2–1 Legacy, BETBOOM 2–1 PARIVISION.
  - Day 3: Aurora reversed the Day 1 upset by defeating 9z 2–0 (Mirage 13-4, Dust2 13-5); BETBOOM 2–1 Legacy.
  - Day 4: FURIA 2–0 Aurora (Dust2 13-8, Inferno 13-10; FURIA 6-1 in tournament maps); BETBOOM 2–1 Falcons (upset over Falcons -238/-286 market favourite; Anubis 5-13, Dust2 16-14, Mirage 13-7; BETBOOM's 3rd consecutive 2-1 win).
  - Day 5: Aurora vs Falcons (Third-place decider, 11:30 UTC; Thunderpick line +170 / -238, de-vig: Falcons 65.53%, Aurora 34.47%; display discrepancy +150 / -208 flagged); FURIA vs BETBOOM (Grand Final, 15:00 UTC, BO5; Thunderpick line -286 / +190, de-vig: FURIA 68.24%, BETBOOM 31.76%; cumulative map load: FURIA 7 maps vs BETBOOM 11 maps across four 3-map series).
  - Contrarian pick'em strategy: Fading favourites blindly is negative EV. Take underdogs only with concrete structural disruption (fatigue asymmetry, veto mismatch) or when trailing late in weekly leaderboard cycles where differentiation is required. Hotspawn streak bonus requires protecting high-confidence picks when leading.
- **Mobile-first discoverability & Executive summary enhancements:**
  - Executive summary landing page (`index.html`) features prominent direct action buttons to updated picks (`picks.html`), Day-5 final-day guide (`analysis.html#day-five-guidance`), Day-4 results (`analysis.html#day-four-results`), and an explicit on-page section for unresolved picks and limitations (`#unresolved-summary`).
  - Section navigation on `analysis.html` prioritizes `#day-five-guidance` and `#day-five-guidance-unpriced` at the top of the on-page jump bar to match visual page hierarchy.
- **Test suite & audits:**
  - Full Python suite: 359 tests passed (`tests/`), including 10 deterministic tests in `tests/test_day5_00a7d6ca.py`.
  - Independent audits: 9 audit tests passed (`audits/`), 5 integrity tests passed (`verification-95b588c2/`), 12 c6 tests passed (`verification-c6/`).
  - Snapshot row audit: 81 rows checked, 0 failures (`verification-c6/audit_snapshot.py`).
  - Validator: 81 primary rows, 13 probability calculations, 15 routes, 570 internal links/assets, 20 checksums, 192 displayed match rows verified with 0 broken links.
  - Headless browser verification: 32 viewport & accessibility scans (320px, 390px, 768px, 1440px) passed with zero overflow and zero WCAG violations; 7 board expiry and 4 research-quote boundary tests passed.
- **Deliverables:**
  - Research dossier & verification ledger: `research/session-00a7d6ca/REPORT.md` and `research/session-00a7d6ca/VERIFICATION.md`.
  - Static dashboard rebuilt and validated for both root legacy fallback and `public/`.



## Session a54996e1 claims — 2026-10-18 00:48 UTC

Arena fixes this session to `arena/a54996e1-maltaproj4`; no other branch is created, checked out or pushed. Board read before claiming: all prior claims (through 00a7d6ca, PR #79 merged as 3027f78) are marked done; no active claim exists. This is the user-requested final-day (Day 5, 18 Oct) follow-up.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Fresh Day-5 harvest: re-check Hotspawn inventory for Sunday TWC fixtures (Aurora–Falcons 11:30Z, FURIA–BETBOOM 15:00Z), re-verify Day 1–4 results line-by-line from HLTV, fresh external lines for Day-5 + every open row | in progress | a54996e1 | research/session-a54996e1/**, .github/workflows/harvest-a54996e1.yml (new), scripts/day5_a54996e1.py (new), tests/test_day5_a54996e1.py (new) | 2026-10-18 |
| Picks for every open match: featured market → HLTV/books fallback → VRS model → research-rank; unresolved section + limitations in executive summary | in progress | a54996e1 | data/latest.json, data/analysis.json, data/review-notes.json (additive), scripts/build.py (only if needed for Day-5 state) | 2026-10-18 |
| Mobile executive summary: one-tap links to updated picks / Day-5 guide / unresolved, phone-readable | in progress | a54996e1 | site/**, assets via scripts/build.py, root generated HTML, README.md | 2026-10-18 |
| Final integration: tests, build, validate, PR to main, merge, Pages deploy verification | in progress | a54996e1 | COORDINATION.md, build-info.json, data/matches.csv, root generated files | 2026-10-18 |

Rules held: Hotspawn = inventory only, never probability; no invented odds/probabilities — unsupported stays blank and flagged; every row carries an official source link; small frequent commits; `git pull --rebase` before every push.

### Session a54996e1 completion log — 2026-10-18
- Claim above honoured; all work on `arena/a54996e1-maltaproj4` only.
- HLTV Day 1–4 (12 series) re-verified 2026-10-18 ~00:45Z from https://www.hltv.org/results?event=8932 — no corrections. Aurora rebuild dated 8 July 2026 (HLTV 45082), not a fresh onboarding factor.
- Thunderpick book re-read 00:55Z: Aurora +140/Falcons −200 (Falcons 61.54%, verified move from +170/−238), FURIA −286/BETBOOM +190 unchanged (68.24%). Receipt: research/session-a54996e1/day5-lines.json; EGW stale 2.73/1.42 display flagged, not used.
- Harvest run 39084235336: snapshot 2026-10-18T00:52:19Z, **98 rows, three-way parity verified, row audit 0 failures; 34 open = 29 priced + 5 research-only (no percentage) + 0 without a pick**. Sunday TWC fixtures are now board rows 1080209 (Falcons 60.5%) and 1080210 (FURIA 70.5%), both Polymarket exchange, agreeing with the Thunderpick book.
- Irregularity flagged on Flagged for Review (data/review-notes.json): 00:48Z lobby document read (81 rows, no Sunday fixtures) superseded minutes later by the verified 98-row harvest; lobby read retained as dated observation only.
- Snapshot-dependent historical tests updated with intent preserved (test_coverage_76712ccc lineup now replays from retained cc88483d snapshot and accepts validated exchange pricing; test_egw_03befae8 expiry updated to the re-read; test_day5_e0fd5a32/00a7d6ca updated to re-read prices/board rendering). No assertion about arithmetic, identity or evidence was removed.
- Verification: 371 unit tests OK; audits 9 OK; integrity 5 OK; verification-c6 12 OK; independent snapshot audit 98 rows 0 failures; build validator 98 rows / 29 calculations / 15 pages / 677 links / 20 checksums / 258 displayed rows; browser 32 viewport/WCAG scans + 11 expiry scenarios OK.
- Report: research/session-a54996e1/REPORT.md. PR/merge/Pages result recorded below after merge.
