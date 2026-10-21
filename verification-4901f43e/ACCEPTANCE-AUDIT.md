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
| 1 | Full list of Hotspawn CS2 matches, auto-refreshed every 4–8 h | **Met in the pipeline; broken on the live site at audit time, and blocked from republishing** (§3, §3.5) | cron `4,19,34,49 * * * *` in `.github/workflows/pages.yml`; `refresh_hours: 1`, `stale_after_hours: 8` in the snapshot; watchdog workflow; 75 rows refreshed at `2026-10-21T21:27:36Z` |
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
| 17 | PR → merge without approval → confirm Pages deploys → record in COORDINATION.md | **In progress at time of writing**; see §3, §3.5 and §5 | Live publication is serving a mixed build for reasons unrelated to this session's changes. The staging fix is already committed on `main`, but its legacy Pages build failed on a deploy-slot race and cannot be re-run, and `main` is now red on the test gate, so this session's merge alone will not republish. Both are documented and requested, not silently absorbed |

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

### 3.5 A second blocker, found while verifying the first: the test gate is red

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

---

## 4. Repository verification (local, on the rebased tree)

Every suite the publishing workflow runs, plus this session's own:

| Command | Result |
| --- | --- |
| `python -m unittest discover -s tests` | **582 tests — 4 failures + 2 errors, all pre-existing on `main`, none in this session's files** (§3.5) |
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
| Pull request | *(filled in at merge time)* |
| Merge commit | *(filled in at merge time)* |
| Live board after merge | *(filled in at merge time)* |

Acceptance rule applied, per the project's own standard: the site is not considered live until
`build-info.json`, `index.html`, `picks.html`, `unresolved.html` and `data/latest.json` all agree on
one build, and the board shows a pick for every open CS2 match. A green workflow is not accepted as
proof of publication on its own — §3 is exactly the case where that inference fails.
