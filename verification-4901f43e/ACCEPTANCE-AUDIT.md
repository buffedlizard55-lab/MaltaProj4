# Acceptance audit — session 4901f43e

Independent line-by-line verification of the published CS2 board, the repository that produces it, and
the live GitHub Pages site. Written against the requirements as stated, not against what the
repository claims about itself. Every number here was re-derived or re-read; nothing is carried over
from another session's summary.

Auditor: `verification-4901f43e/audit_published_claims.py` · Receipts:
[`../research/session-4901f43e/receipts-2026-10-21.json`](../research/session-4901f43e/receipts-2026-10-21.json)
· Findings: [`../research/session-4901f43e/REPORT.md`](../research/session-4901f43e/REPORT.md) ·
Requests: [`../research/session-4901f43e/REQUESTS.md`](../research/session-4901f43e/REQUESTS.md)

| Reference point | Value |
| --- | --- |
| `origin/main` when this audit started | `179789e` (PR #121) |
| `origin/main` when this audit finished | `c55b4b0` (PR #128 + the root-fallback publication) |
| Live build receipt read | [build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) — revision `ac5c816`, built `2026-10-21T21:27:37Z`, 75 rows |
| CI harvest this session ran | runs `39674050906` (pre-rebase pipeline) and `39676969126` (current pipeline), both `success` |

---

## 1. Verdicts against the stated requirements

| # | Requirement | Verdict | Evidence |
| --- | --- | --- | --- |
| 1 | Full list of Hotspawn CS2 matches, auto-refreshed every 4–8 h | **Met** — was broken at audit time and blocked from republishing; both cleared before merge (§3, §3.5, §5). One structural risk remains open (§3.6) | cron `4,19,34,49 * * * *` in `.github/workflows/pages.yml`; `refresh_hours: 1`, `stale_after_hours: 8` in the snapshot; watchdog workflow; 75 rows refreshed at `2026-10-21T21:27:36Z` |
| 2 | A pick for **every** match | **Met** | CI harvest `39676969126`: `open=13 gaps=2 no_pick=-`, `unresolved_without_any_pick: 0`. Live board read at 20:50Z: "13 open CS2 match(es) · **13 with a pick**" |
| 3 | Every match has a pick **or** a win percentage | **Met** | 11 of 13 open rows carry two-sided probabilities; the 2 without one carry a sourced research pick and a published reason (`research_vrs_single` for 1081597, `research_rank_single` for 1082860) |
| 4 | Where the featured-pick method can't resolve a match, research alternates — HLTV first, then esportsbooks/betting lines | **Met** | Every row stores its provider attempts in order: Polymarket → HLTV → Pinnacle → Thunderpick → GG.BET → Valve VRS model → rank research. Refusals are recorded with reasons, never bypassed |
| 5 | Probabilities originate from external betting lines and/or HLTV-derived own lines | **Met** | `probability_calculations_reproduced: 11` in the CI validator run; 5 market lines (Polymarket, tiers `exchange`/`exchange_wide`) + 6 originated `model_vrs` lines from Valve's standings with Valve's own formula |
| 6 | **Hotspawn is never a probability input** | **Met, and asserted on every run** | Auditor check `crowd-votes-excluded` passes against both the committed baseline and the fresh CI snapshot. Three crowd votes were seen and rejected this session: HLTV 75/25 (R5), Strafe 24/76 for the *same* fixture (R10), HLTV 50/50 with zero votes (R13). Hotspawn is used for inventory and lock times only |
| 7 | Separate section for unresolved picks **plus** the limitations, surfaced in the executive summary | **Met** | [unresolved.html](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html) ("Unresolved & non-market picks", columns *Win probability · Our pick · Limitation / review flag · Sources*); `#unresolved-summary` → `#pick-limitations` on the landing page; exec-summary links "[Unresolved & limits →](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html)" |
| 8 | Executive summary links **within the site** to the updated picks list | **Met** | Landing page carries `[Updated picks →](picks.html)`, `[Every pick on this page ↓](#picks-at-a-glance)`, `[Unresolved & limits →](unresolved.html)`, plus a "Where the picks are" card grid |
| 9 | Obvious pick + per-team win probability, un-confusing on a phone | **Met** | `#picks-at-a-glance` numbers every open match in start-time order with the pick in bold and its percentage; each card links to `evidence.html#match-<id>`; the page states "On a phone: the bottom bar has Home, Picks, Unresolved, Matches and TWC. Each match is a card with the pick on top, so there is no sideways scrolling" |
| 10 | Mobile/tablet/desktop verified, not assumed | **Met** | `npm run test:browser` → 32 page/viewport/accessibility/no-overflow scans at 320, 390, 768 and 1440 px, 7 board-expiry scenarios, 4 research-quote clock scenarios — all green locally on the rebased tree |
| 11 | Every table row has a source link to an official site | **Met** | CI validator: `internal_links_and_assets_checked: 650`, `displayed_match_rows_verified: 176`, `artifact_checksums_verified: 20`. Each row carries Hotspawn (inventory) plus the pricing source (Polymarket/Pinnacle/Valve standings/HLTV) |
| 12 | Line-by-line verification from official trusted sources, with links | **Met for the four gap fixtures and every open row**; **15 HLTV citations elsewhere remain unread** | 15 dated receipts with sha256'd extracts (§2 of `REPORT.md`); auditor replays all 13 open rows. The auditor reports `hltv-citations-not-read` listing 15 ids by number rather than implying they were checked |
| 13 | Never infer or fill unverified values — leave blank and flag | **Met** | Both blank rows publish a reason string (279 and 247 characters) and appear on `review.html`; `blank-probability-documented` is asserted for each. Absent teams (TitanFlow, Staqued, LOS NINOS) produce no points and no percentage |
| 14 | Flag irregularities; flagged items don't block merge but appear on "Flagged for Review" | **Met** | [review.html](https://buffedlizard55-lab.github.io/MaltaProj4/review.html) — "These limitations are visible, not silently filled in. They do not prevent publication." Six irregularities recorded this session (`REPORT.md` §6.1–§6.4, §6.6, plus §6.5 withdrawn on the evidence), the content ones as warnings and the publication blocker documented separately |
| 15 | GitHub Pages site, clean landing page + category subpages, readable tables | **Met** | 9 primary pages + 6 legacy redirects; `index`, `picks`, `matches`, `analysis`, `evidence`, `sources`, `unresolved`, `review`, `methodology`, `404` |
| 16 | Coordination protocol (claim first, non-overlapping scope, log requests, rebase before push) | **Met** | Claim committed before any work (`f9d071e` → `3dcac6f`); no file owned by another session was edited; 5 requests logged in `REQUESTS.md`, including one urgent cross-session blocker |
| 17 | PR → merge without approval → confirm Pages deploys → record in COORDINATION.md | **Met** | PR [#135](https://github.com/buffedlizard55-lab/MaltaProj4/pull/135) merged 22:04:21Z as `8e7a475`; legacy Pages build 39683759807 **success**; publication run 39683760753 **success** including its own live-byte check; live board re-read independently at 22:12–22:15 UTC and recorded in §5; board rows and completion log in `COORDINATION.md` |

---

## 2. What was re-derived rather than trusted

| Claim under audit | How it was checked | Result |
| --- | --- | --- |
| Polymarket market `6001634` prices fixture `1082837` | Read the market through the gamma API (R1), then replayed it through `scripts.core.quote_polymarket` offline | Accepted at tier `exchange`, spread 0.01, liquidity $3,888.26 → **LOS NINOS 61.5% / Zetta 38.5%** at 20:12Z |
| Zetta ≡ Alianza Lima Esports | Four independent routes (result parity, 5/5 roster identity across three sources, a second label-swap instance, exactly one upcoming Zetta fixture) | **Confirmed**; both labels resolve to Valve #357, 473 points |
| Off Chops ≡ THUNDER dOWNUNDER | Organiser's own rebrand announcement (R14) + HLTV lineup (R13) + Valve #119 roster | **Confirmed**, 4/5 roster continuity ≥ `ROSTER_OVERLAP = 3` |
| Ground Zero vs Off Chops percentage | `vrs.expected(971, 878)` then `vrs.calibrated` | **Off Chops 60.2% / Ground Zero 39.8%** — matches the live board; the merged note's 59.1% needs an 82.85-point gap, Valve publishes 93 |
| 5star vs 1WIN percentage | Same calculator on the rows the note cites, then on the rows that are actually these teams | Cited #96/#59 are **Bounty Hunters / Iberian Soul**; the real rows #80 (1110) / #38 (1383) give **24.3% / 75.7%**, which is what the board prints |
| benched gods disambiguation | `vrs.identify` with the receipt lineup against both #157 and #329 | #157 (811) at **5/5** overlap; without a lineup the label is refused as ambiguous |
| FlyQuest vs Staqued | Label lookup across all 380 Valve rows | FlyQuest #86 (1093); **Staqued absent** → blank is correct |
| HLTV citation `2399867` | Read the id directly (R11) | Serves **Alliance vs FaZe, RLG Tesla Cup 2026** — the citation is wrong; `2399865` is correct |
| "Swiss Round 3" | Read HLTV's round label (R5) and Polymarket's event description (R2) | Both say **Round 5** |
| Every open row's published probability | Re-derived from the row's own cited inputs in the snapshot | **All 13 replay**, in both the committed snapshot (75 rows, the 21 October build) and the fresh CI snapshot (75 rows) |

Auditor totals: **49 passed / 0 failed / 4 warnings** against the committed snapshot, and
**46 passed / 0 failed / 4 warnings** against the freshly refreshed CI snapshot
(`research/harvest-4901f43e/logs/claims-audit.txt`, run `39676969126`). The four warnings are the
findings in `REPORT.md` §6 — warnings by design, so `main` stays green while the discrepancies stay
visible. One of them has already cleared itself: the `36.3% / 63.7%` figure for `5star vs 1WIN` was
corrected on `main` while this audit was running, and the check that reported it now passes without
anyone editing the check. That is deliberate — a verification tool that keeps reporting a fixed
problem is worse than no tool at all.

---

## 3. Live publication: a real defect, independently reproduced

**This is the most consequential finding of the audit, and it is not about pick quality.** The
pipeline is producing a correct, fully sourced board; the live site was not serving it.

### 3.1 What was observed, with timestamps

| Time (UTC) | URL read | What it served |
| --- | --- | --- |
| 20:50 | `index.html` | **Fresh**: "Wed, 21 Oct 2026", "Last checked 21 Oct 2026 · 20:47 UTC", 13 open · 13 with a pick · 11 with a probability · 0 unresolved, next pick LOS NINOS 80.5% |
| 20:50 | `build-info.json` | revision `884f36e`, built `2026-10-21T20:47:31Z`, 75 rows |
| 21:37 | `picks.html` | **Frozen**: "Sun, 18 Oct 2026", "0 matches shown", every row "Pick closed", 18 Oct fixtures only |
| 21:37 | `unresolved.html` (also with a cache-busting query) | **Frozen**: "Sun, 18 Oct 2026", 16 matches from 18 Oct |
| 21:37 | `review.html` | **Frozen**: "Sun, 18 Oct 2026" |
| 21:37 | `index.html` | **Frozen**: "Sun, 18 Oct 2026", "Last checked 18 Oct 2026 · 00:52 UTC", 34 open matches, "Snapshot is older than 8 hours: every percentage below is expired", next pick "**Pick withheld · refresh pending**" |
| 21:37 | `data/latest.json` | **Frozen**: `generated_at 2026-10-18T00:52:19Z` |
| 21:40 | `build-info.json` | **Fresh**: revision `ac5c816`, built `2026-10-21T21:27:37Z`, 75 rows, advertising `picks.html` digest `87137fcc…` |

So the site served a fresh build receipt next to three-day-old pages: the manifest and the bytes it
checksums disagreed with each other in production. On a phone this reads as a dead board — 34 closed
matches, every pick withheld — while CI reported green.

### 3.2 Root cause

```
GET /repos/buffedlizard55-lab/MaltaProj4/pages
→ {"build_type":"legacy","source":{"branch":"main","path":"/"},"status":"built"}
```

GitHub Pages for this repository is configured as a **legacy branch build from `main:/`**, not as an
Actions artifact deployment. `.github/workflows/pages.yml` verifies, refreshes, builds and uploads
`public/` as a Pages artifact — but the site is actually served from the **committed repository
root**, where a frozen 2026-10-18 staging of the same pages lives (`build-info.json` at `88b1b2c`,
built `2026-10-18T00:52:19Z`, 98 rows; every root `*.html` date pill reads "Sun, 18 Oct 2026").

Every push to `main` therefore republishes the frozen root over whatever the verified workflow had
just deployed. Two deployment mechanisms race for one slot, and the loser's bytes are what a reader
gets. The committed root files at `edb1640` confirm it: `build-info.json` 18 Oct / 98 rows and
`index.html` "Sun, 18 Oct 2026" / 34 open.

The failure is fail-closed, which is the one thing in its favour: the stale board withholds every
percentage and says so loudly, rather than presenting three-day-old prices as current.

### 3.3 The fix, and its own failure

Session `1395f539` diagnosed the same defect independently and merged a fix while this audit was
running — commit `b68a664` "Keep the legacy main:/ root on the verified build" (PR #128), adding
`scripts/publish_root_fallback.py`, which stages the hash-verified `public/` build to the repository
root only when the snapshot is readable, inside the 8-hour window, strictly newer than the committed
one, and the committed one is older than a 4-hour cooldown. Its docstring records that the `PUT`
which would switch Pages to `build_type: workflow` answers **HTTP 403** for this integration, so
staging the root forward is the only available lever.

The fix ran on the `2026-10-21T21:27:37Z` publication and committed **`c55b4b0` "Publish the
verified build to the legacy main:/ root fallback"**. The committed root is now current:
`build-info.json` built `2026-10-21T21:27:37Z`, revision `ac5c816`, 75 rows; `index.html` date pill
"Wed, 21 Oct 2026"; 13 open matches. **The frozen-board failure mode is fixed at the source.**

But the Pages build of that commit failed:

```
run 39679099962 (pages-build-deployment, head c55b4b0) → failure
  build:              success
  report-build-status: success
  deploy:             failure — "Deployment request failed for c55b4b0… due to in progress
                        deployment. Please cancel first or wait for it to complete."
```

A deployment-slot race, not a content error: the Jekyll build of the fresh root succeeded and only
the hand-off collided with the artifact deploy from run `39678232770` two minutes earlier. This is
the same race `pages.yml` already documents from 2026-10-16 ("a red deploy step does not by itself
prove the dashboard is stale") and that session `dee046c2` recorded as "the R-1 deployment-slot race
on its delivery run".

`gh run rerun 39679099962 --failed` was attempted and refused: *"run 39679099962 cannot be rerun;
its workflow file may be broken"* — GitHub's internal `pages-build-deployment` workflow is not
re-runnable through the API. The only way to trigger another legacy build is a new push to `main`.

### 3.4 What this session did about it

- Did **not** edit `.github/workflows/pages.yml`, `scripts/publish_root_fallback.py`, the root staged
  `*.html` or `data/latest.json` — all owned by other sessions, and `1395f539` was actively fixing
  exactly this. Duplicating that work would have risked a second, conflicting staging path.
- Verified the fix at the source instead: the committed root at `c55b4b0` is byte-checked here
  against its own `build-info.json`, and reads "Wed, 21 Oct 2026" with 13 open matches.
- Planned to use this session's own merge to `main` as the retry, since merging pushes to `main` and
  that triggers a fresh legacy Pages build of the already-current root. **That retry is now known to
  be blocked** — see §3.5. Merging still lands this session's work and still pushes to `main`, but it
  will not produce a publication until the test gate is green again.

### 3.5 A second blocker, found while verifying the first: the test gate was red — RESOLVED by PR #130

`unittest discover -s tests` on `main` at `c55b4b0` reports **582 tests, 4 failures, 2 errors**. The
same six tests **pass** on the immediately preceding commit `ac5c816`. Both results were produced in
a pristine `git worktree` checked out from `origin/main`, containing none of this session's files, so
the attribution is exact and one commit wide.

The breaking commit is `c55b4b0` itself — the root-fallback publication described above. It replaced
the frozen 2026-10-18 98-row `data/latest.json` and all nine root `*.html` with the fresh 21 October
75-row build, and six tests in `test_coverage_76712ccc`, `test_day5_e0fd5a32`, `test_day5_f4e34907`
and `test_session_d6df5beb` assert against those committed artifacts as if they were frozen history.
Two of them pin board state that other sessions deliberately changed (the method for row `1081597`,
now `research_vrs_single`; the wording of the TWC review note).

That step is the **first hard gate** in `pages.yml` and carries no `continue-on-error` — the only two
in the file are in the `deploy` job. So the next scheduled slot will build nothing, upload no
artifact, and the `deploy` job (`needs.verify-build`) will not run. Combined with §3.3, the site
cannot get a correct, fully-published build until *both* problems are fixed: the legacy build has to
be re-triggered by a push to `main`, and a push to `main` currently fails its own test gate. The live
board meanwhile holds a mixed state, and `assets/app.js` starts withholding picks when the served
snapshot passes its eight-hour limit.

Full per-test diagnosis, reproduction commands and a suggested minimal fix for each:
**`verification-4901f43e/MAIN-SUITE-BLOCKER.md`**, with the request logged as
`research/session-4901f43e/REQUESTS.md` item 5. This session edited none of the six tests, none of
the data they read, and no workflow file. It also deliberately did **not** request
`continue-on-error` on the test step: that would restore publishing by removing the only check that
keeps broken data off the site.

**Resolved while this audit was being written.** `9563620` *"Restore the suite to green: unpin four
sessions' tests from a refreshed snapshot"* (session `bf09aa40`), merged as **PR #130** (`1b2d92e`),
touched exactly the four files diagnosed here and applied the first suggested fix: the historical
assertions were unpinned from the mutable snapshot instead of the published data being rolled back or
the gate being weakened. Session `93fafca6` raised the same blocker on the shared board at 21:45 UTC
and recorded the resolution at 21:55 UTC (`43ce3a2`), independently of this session's 21:40 UTC
measurement; both diagnoses name the same six tests, the same breaking commit and the same fix
direction. This session re-verified on the rebased tree: **602 tests OK** (their 573 plus this
session's 29), all other suites green, validator and browser suite green, auditor 49/0/4.

`93fafca6`'s notice also keeps three structural items open that PR #130 does **not** close, and this
audit agrees with all three: `publish_root_fallback` writes `data/latest.json` on `main`, so the next
re-stage can re-break any test that reads it as history; the publication steps run inside
`verify-build`, so a failure there skips `deploy` and the run cannot self-heal; and switching Pages
from `build_type: legacy` to GitHub Actions is still refused for both token types this project can
present. §3.6 below is direct evidence for why the third one matters.

### 3.6 Still open: two deployment paths publish the same URLs, and the pages disagree

Measured at **21:52–21:53 UTC**, both reads in the same window, against the same fixture
(`1082837`, Zetta vs LOS NINOS, Polymarket market `6001634`):

| Live page | Generation served | What it prints for `1082837` | Observation stamps |
| --- | --- | --- | --- |
| `index.html` (executive summary) | run-time artifact build, snapshot **21 Oct 21:48 UTC** | LOS NINOS **72.0%** (28.0 / 72.0, fair line 3.57 / 1.39) | "Observed 21 Oct · 21:42 UTC" |
| `picks.html` (the board the summary links to) | committed root build, snapshot **21 Oct 21:27 UTC** | LOS NINOS **84.5%** (15.5 / 84.5, fair line 6.45 / 1.18) | "Observed 21 Oct · 21:20 UTC" |
| `build-info.json` | committed root build | `built_at 2026-10-21T21:27:37Z`, `revision ac5c816`, 75 rows, `picks.html` digest `87137fcc…` | — |

Two other market rows differ the same way (`1081870` Rare Atom 59.5% vs 61.0%; `1082882` Apogee
Betclic 55.5% vs 56.5%). All six model rows are identical across both generations (Off Chops 60.2%,
1WIN 75.7%, NEXVOID 68.2%, Abyssal 51.8%, HOTU 85.2%, Banda chuya 57.6%), and **both generations
show 13 open matches, 13 with a pick, 11 with a probability, 0 unresolved**, so no requirement in §1
is unmet by this. Neither page is wrong on its own terms: both numbers are real dated observations of
one thin market that moved 61.5% → 80.5% → 84.0% → 84.5% → 72.0% across the hour.

**Why it happens, from the code rather than from inference.** `scripts/publish_root_fallback.py`
states it in its own docstring: the site is `build_type: legacy` with `source: main:/`, the `PUT`
that would switch it to GitHub Actions answers **403**, so "every push … republishes the *committed*
root pages over whatever the verified artifact deploy just published". Its `decide()` refuses to
re-stage the root while the committed root is inside a **4-hour cooldown**, and the root was staged
at 21:27:37Z — so the committed fallback is *designed* to lag the artifact build by up to four hours.
Three merges landed on `main` in five minutes (21:44, 21:47, 21:49 UTC), each re-running the legacy
build, while a publish run deployed its artifact at ~21:48 UTC. Two writers, one set of URLs.

**Honest limit on this measurement:** these reads go through a caching proxy, and raw bytes cannot be
hashed from here, so a per-path cache-generation difference cannot be fully separated from a genuinely
mixed deployment. What is not in doubt is the structural fact behind it: the committed root
(`build-info.json` at 21:27:37Z on `main` at `0131087`) lags the run-time build the artifact path
publishes (21:48Z), by design, for up to four hours.

**Fix, already requested by someone with the right scope:** session `93fafca6`'s board item (c) —
switch Pages to **GitHub Actions** at the owner level, which removes the legacy writer and leaves one
publication path. Interim options, in order of preference: skip the artifact `deploy` while the site
is `build_type: legacy` (it is overwritten by the next push anyway, so skipping removes the second
writer entirely); or stage the root on every publish run by passing `--cooldown-hours 0` (cost: one
commit per run). Neither is requested as a change to make blindly — both belong to `1395f539` and
`96ea1af8`, and this session edited neither file. Logged as `REQUESTS.md` item 6.

---

## 4. Repository verification (local, on the rebased tree)

Every suite the publishing workflow runs, plus this session's own:

| Command | Result |
| --- | --- |
| `python -m unittest discover -s tests` | **602 tests, OK** on the rebased tree (was 582 with 4 failures + 2 errors before PR #130 — §3.5) |
| `python -m unittest tests.test_session_4901f43e -v` | **29 tests, OK** |
| `python -m unittest discover -s audits -p 'test_*.py'` | 9 tests, OK |
| `python verification-95b588c2/test_integrity.py` | 5 tests, OK |
| `python -m unittest discover -s verification-c6 -p 'test_*.py'` | 12 tests, OK |
| `python -m scripts.validate --data data/latest.json --site .` | 75 rows verified against the primary snapshot, 11 probability calculations reproduced, 15 pages, 655 internal links, 20 checksums, 176 displayed rows |
| `python verification-c6/audit_snapshot.py data/latest.json` | **0 failures** |
| `python -m scripts.build --data data/latest.json` | 9 primary pages + 6 legacy redirects; 75 sourced rows, 11 with percentages, 2 without, **0 unresolved** |
| `npm run test:browser` | 32 scans (320/390/768/1440 px, axe, no-overflow) + 7 expiry + 4 quote-clock scenarios |
| `verification-4901f43e/audit_published_claims.py --snapshot data/latest.json` | **49 passed, 0 failed, 4 warnings** |

CI, on this session's branch (run `39676969126`, harvest workflow, non-publishing):

| Step | Result |
| --- | --- |
| `scripts.refresh` against live sources | `coverage: verified`, 75 matches, **11 priced, 2 research-only, 0 without any pick** |
| `scripts.build` | 75 sourced rows, 11 with percentages, 2 without, 0 unresolved |
| `scripts.gap_probe_8c8e3c5f` | `open=13 gaps=2 no_pick=-`, `no_probability: [1081597, 1082860]` |
| `verification-c6/audit_snapshot.py runtime/latest.json` | **0 failures** |
| `scripts.validate --data runtime/latest.json` | 75 rows verified, 11 calculations reproduced, 15 pages, 650 links, 20 checksums, 176 displayed rows |
| this session's auditor against the fresh snapshot | **46 passed, 0 failed, 4 warnings** |
| `scripts.probe_4901f43e` | 6 readable, 8 refused (403), 1 served-without-marker |

One regression this session introduced and then corrected is worth recording, because it is the kind
of thing that silently rots: after PR #121 merged, `core.norm` began folding the alias register, so
`THUNDER dOWNUNDER` and `Off Chops` normalize to one label. A test asserting "no Valve row
normalizes to `Off Chops`" stopped testing anything meaningful and started failing. It now checks
the **raw published row names** (Valve has no `Off Chops` row) and separately pins that the alias is
what bridges to #119 — a stronger claim than the one it replaced.

---

## 5. Merge and live verification record

| Item | Value |
| --- | --- |
| Branch | `arena/4901f43e-maltaproj4` |
| Pull request | [#135](https://github.com/buffedlizard55-lab/MaltaProj4/pull/135) — *Independent acceptance audit of the published board: replayable claim auditor, 15 primary-source receipts, two publication blockers diagnosed* |
| PR checks before merging | `verify-build` run [39683487349](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39683487349) → **success**; `harvest` skipped (gated on `[harvest]` in the commit message) |
| Merged | **2026-10-21T22:04:21Z**, without waiting for approval, via `gh pr merge 135 --merge` |
| Merge commit | `8e7a4753240ccb8f5fe63748fe149a91870d0879` — now `main`'s tip |
| Legacy Pages build on the merge commit | `pages-build-deployment` [39683759807](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39683759807) → **success** (started 22:04:23Z). This is the retry for the failed `c55b4b0` deploy in §3.3 |
| Publication run on the merge commit | [39683760753](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39683760753) → **success**: `verify-build` (real refresh, independent row audit, build, validator, browser/accessibility/expiry suites, root-fallback decision, Pages artifact) and `deploy` ✓ 19s, whose own *"Verify live Pages bytes match this exact build"* step passed |

**Live board after the merge, read independently at 22:12–22:15 UTC** — all five artifacts agree on one
build, which is the acceptance rule stated below:

| Artifact | What it serves |
| --- | --- |
| `build-info.json` | `revision 8e7a4753240ccb8f5fe63748fe149a91870d0879` (this merge), `built_at 2026-10-21T22:10:30.863837Z`, `snapshot_generated_at 22:10:30.567783Z`, `rows 75`, per-file sha256 for all 20 published files |
| `data/latest.json` | `generated_at 2026-10-21T22:10:30.567783Z`, `refresh_started_at 22:06:53Z`, `fixtures_observed_at 22:06:53Z`, `coverage: verified`, `refresh_hours 1`, `stale_after_hours 8` |
| `index.html` | "Wed, 21 Oct 2026"; "Snapshot 21 Oct 2026 · **22:10 UTC**"; "**Coverage at 21 Oct · 22:10 UTC:** 12 open fixture(s) — 10 with published probabilities (4 from markets, 6 from our VRS model), 2 with a labelled research-only pick and no percentage, **0 with no supported pick yet**"; in-site links "Full updated pick board →", "Unresolved & limitations →", "All matches →", plus the phone instructions |
| `picks.html` | "Wed, 21 Oct 2026"; 10 priced rows with the **same** observed stamps as `index.html` (22:06 / 22:10 UTC) and the same numbers — Rare Atom 40.5/59.5, Banda chuya 42.4/57.6, Imperial 77.0/23.0, ShindeN 46.5/53.5, Apogee Betclic 44.5/55.5, Off Chops 39.8/**60.2**, NEXVOID **68.2**/31.8, Abyssal 48.2/**51.8**, HOTU **85.2**/14.8, 1WIN 24.3/**75.7** |
| `unresolved.html` | "Wed, 21 Oct 2026"; **8 rows** = 6 labelled model lines + 2 research-only picks, each with its limitation and its source links; **0 unresolved**. The two blank rows state their reason in full: `1081597` (benched gods #157 / 811 points in Valve's 380-team file, TitanFlow absent, plus the HLTV `2399696` postponement flag) and `1082860` (FlyQuest HLTV world #61, Staqued unranked in the same fixture) |

Two things about this reading are worth stating rather than glossing:

1. **Fixture `1082837` (Zetta vs LOS NINOS) left the open board** between the 21:48Z and 22:10Z
   generations — open count 13 → 12, priced 11 → 10. That is correct, not data loss: the match starts
   22:00 UTC with a 21:54 UTC lock, so at 22:10Z it is no longer an open pick. It is the fixture whose
   market this session replayed four times (61.5% → 80.5% → 84.0% → 84.5% → 72.0%) and whose alias
   evidence is in `REPORT.md` §4.
2. **The §3.6 divergence is not present in this reading** — both pages serve the 22:10:30Z generation.
   That is a property of which writer landed last, not a fix: the committed root on `main` still reads
   `built_at 2026-10-21T21:27:37Z`, because `publish_root_fallback.decide()` is inside its 4-hour
   cooldown until ~01:27Z, so any push to `main` before then can republish that older root over the
   artifact build again. §3.6 stays open as a structural finding.

Acceptance rule applied, per the project's own standard: the site is not considered live until
`build-info.json`, `index.html`, `picks.html`, `unresolved.html` and `data/latest.json` all agree on
one build, and the board shows a pick for every open CS2 match. A green workflow is not accepted as
proof of publication on its own — §3 is exactly the case where that inference fails.
