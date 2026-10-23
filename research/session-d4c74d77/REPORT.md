# Session d4c74d77 — why the live board stopped updating, and the repair

Worked 2026-10-23 on Arena branch `arena/d4c74d77-maltaproj4`, forked from `main` at
`7b9180d5d9d63778460cd9f1a9b146391f82695d`.

The authoring sandbox has **no network path to Hotspawn, HLTV, Polymarket, Pinnacle or any
esportsbook**: every request to a non-GitHub host fails during TLS setup
(`curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL`). Only `github.com`,
`codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org` and
`files.pythonhosted.org` resolve. So no value in this report was invented from memory: every
claim below is either a byte read from `api.github.com` / `codeload.github.com`, a value read
out of this repository's committed data, or a number produced by this repository's own code
during a run whose command is quoted.

## 1. Measured defect: the scheduled publish has been failing since 2026-10-22T23:26Z

Read from `GET /repos/buffedlizard55-lab/MaltaProj4/actions/runs`:

| Run | Started (UTC) | Event | Result | First failing step |
| --- | --- | --- | --- | --- |
| [39886171791](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39886171791) | 2026-10-23T01:49:32Z | schedule | failure | 8 · Unit and independent failure-mode tests |
| [39871808909](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39871808909) | 2026-10-22T23:26:37Z | schedule | failure | 8 · Unit and independent failure-mode tests |
| [39846639619](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39846639619) | 2026-10-22T20:11:15Z | schedule | success | — (published snapshot `2026-10-22T20:15:52Z`) |

Because step 8 failed, step 11 (`Refresh official sources`) was **skipped** in both later runs,
so no new fixture or price was read and nothing was deployed. The live board therefore still
serves the 20:15:52Z snapshot: `build-info.json` from `codeload.github.com` reports
`rows: 84`, `built_at: 2026-10-22T20:15:53.114095Z` (8h+ old when this session started).

Reproduction on the exact pushed `main` tree, with the pinned requirements installed
(`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`):

```
.venv/bin/python -m unittest discover -s tests
Ran 961 tests in 25.324s
FAILED (failures=2, skipped=3)
```

* `tests/test_session_75ebd2d6.py::ResearchRowsCarryDatedHLTVAndLimitation::test_each_research_row_has_method_pick_and_no_percentage`
  — `AssertionError: 'research_vrs_single' != 'research_rank_single' : 1081149`
* `tests/test_session_13e99ca6.py::TestExecutiveSummaryMobileClarity::test_research_only_fixtures_have_hltv_evidence_and_no_percentage`
  — its allowlist required `method.startswith('research_rank')`, which rejects
  `research_vrs_single`

### Root cause

Both are **stale pins, not bad data**. Fixture `1081149` (FORZE Reload vs LFO 10, CCT Europe
2026 Series #12, 2026-10-23T14:00:00Z) carries `method: research_vrs_single` in the signed
board, with the receipt that justifies it:

* `vrs_research.source` = `https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md`
  (`standings_as_of 2026-10-05`, `teams_count 380`, `observed_at 2026-10-22T20:15:52.764829Z`)
* `resolved_vrs`: **FORZE Reload — status `listed`, standing 84, points 1100, roster overlap 4**;
  **LFO 10 — status `absent`** ("not listed in the Valve global standings")
* `attempts`: `Valve VRS research → resolved`; `Rank research → unresolved`
  ("neither team carries a world-ranking number in this fixture")
* `flags`: "Research pick on one-sided Valve standings evidence"

That tier is published by the code base in five places — `scripts/vrs.py:271` (assignment),
`scripts/coverage_contract.py:21` (`RESEARCH`), `scripts/build.py:64-66` (labels/tags/kinds),
`scripts/summary.py:40/89`, `scripts/validate.py:231` — and documented in the methodology as
"One-sided Valve standings tier, no numbers". The pick (`FORZE Reload`) and the blank
percentage are correct; only the two test pins were out of date. The re-tiering happened in
the 20:15:52Z refresh, i.e. *after* the last test run of the day, and it locked the pipeline:
each subsequent scheduled run re-ran the stale pins against the newly committed board and
died before it was allowed to read a source.

## 2. Concurrent fix (read this before reviewing the diff)

While this session was reproducing the outage, session **f0814674** diagnosed the same two pins
and merged its fix to `main` as
`4940873 Unblock publication: stop pinning a research tier in two data-driven tests`
(PR #196, merge `a030476`), together with a fresh publish of the
**2026-10-23T04:59:16Z** board (92 fixtures, 30 open, 30 picks, 29 with a probability). That
session's repair accepts any `research_*` tier.

This branch rebases onto that merge and keeps its work unchanged, with two additions that are
strictly stronger and deadlock-safe:

* the two files now also require the *receipt* that justifies the tier (official Valve
  standings URL + the picked team `listed` with an integer standing for
  `research_vrs_single`; an official HLTV URL for the `research_rank*` tiers);
* `tests/test_session_d4c74d77.py` re-derives the tier from each open row's own receipt,
  rejects six corrupted variants, and scans the whole suite for pins that contradict the live
  board. It also keeps the full-coverage and executive-summary contracts.

A tier added after this session is *not* failed by either addition (only the documented floor is
held to proof), so a healthier refresh cannot turn the unit gate red the way the 20:15Z
re-tiering did. `tests/test_session_f0814674.py` (their meta-guard) passes unchanged.

## 3. Repair

1. `tests/test_session_75ebd2d6.py`
   * `RESEARCH_EXPECTED["1081149"]` now records `research_vrs_single` with a dated comment
     citing the Valve receipt above.
   * The strict pin `assertEqual(method, expected_method)` is replaced by an
     **evidence-derived** assertion: `research_tier_from_evidence(m)` returns the tier the
     row's own retained receipt proves (`research_vrs_single` only when the Valve receipt names
     exactly the picked team as `listed` *with* an integer standing and the opponent as
     `absent`; `research_rank` only when both HLTV ranks exist and the pick is the better-ranked
     team; `research_rank_single` only when exactly one team is ranked and it is the pick).
     The pick pins are unchanged.
2. `tests/test_session_13e99ca6.py` — the allowlist is now the three published research-only
   tiers instead of a `research_rank` prefix, and it additionally requires the matching
   receipt (`vrs_research` with an official Valve URL and a `listed` picked team, or
   `hltv_context` with an official HLTV URL) plus `probabilities is None` and
   `fair_odds is None`. Nothing was loosened for priced rows.
3. New `tests/test_session_d4c74d77.py` (15 tests) so the same class of deadlock cannot recur
   silently:
   * independent re-derivation of the research tier from each open row's receipt, compared
     with the label the board publishes;
   * a direct replay of the two assertions that failed the production runs;
   * six corruption negatives (missing receipt, unofficial host, pick is the unlisted team,
     both teams listed, listed row without a standing, `research_rank_single` whose pick is the
     unranked team) that must all be rejected;
   * `NoStaleResearchTierPins` scans every `tests/test_*.py` for
     `"<fixture id>": {"method": "research_…"}` pins and fails if one contradicts the live
     board for an open, unpriced row. Verified effective: restoring the old
     `research_rank_single` pin makes it fail with
     `test_session_75ebd2d6.py: 1081149 pinned research_rank_single, board says research_vrs_single`;
   * policy floor: the three documented tiers must still exist in `coverage_contract.RESEARCH`
     and in the `build.py` label maps.
4. `.github/workflows/harvest-d4c74d77.yml` — non-publishing pre-merge verification on a GitHub
   runner (this sandbox cannot reach the sources). It runs the production pipeline
   (refresh → quarantine → independent row audit → build → validate), stages the fresh build at
   the root exactly as production does, and then re-runs **every** suite against that freshly
   refreshed tree. That is the check that would have caught this deadlock before merge. It
   never deploys and commits only `research/harvest-d4c74d77/`.

No price, probability, pick, roster, identity, source timestamp or production gate was changed.

## 4. Verification performed locally (exact commands)

| Gate | Result |
| --- | --- |
| `python -m unittest discover -s tests` | **990 tests OK**, 1 skipped, 22.6s (re-measured after rebasing onto `a030476`; 976 before that merge brought its own tests) |
| `python -m unittest discover -s audits -p 'test_*.py'` | **9 tests OK** |
| `python verification-95b588c2/test_integrity.py` | **5 tests OK** |
| `python -m unittest discover -s verification-c6 -p 'test_*.py'` | **12 tests OK** |
| `python -m scripts.validate --data data/latest.json --site .` | 92 rows, 29 calculations reproduced, 15 pages, **839** links/assets, 20 checksums, 231 displayed rows |
| `python -m scripts.build --data data/latest.json` + `validate --site public` | 9 primary pages + 6 legacy redirects; 92 rows, 29 calculations reproduced, 839 links/assets, 20 checksums, 231 displayed rows |
| `npm run test:browser` | **all four suites pass** on the 04:59Z board: 32 accessibility/no-overflow scans (320/390/768/1440px), 7 expiry + 4 quote-boundary scenarios, 8 phone/queue/unresolved scenarios, and the first-screen 44px pick CTA at 320/390px. Before the fresh board, `browser_eaff7cce` failed only in the stale state — see §5 |

Regression control: re-inserting the old pin into `tests/test_session_75ebd2d6.py` makes the
new guard fail (2 failures), and restoring it returns 15/15 OK.

## 5. Flagged for review (published with limitations, does not block the fix)

1. **Stale-state phone discoverability.** With the board 8h+ stale, `assets/app.js` shows the
   106px `#runtime-stale` notice above the freshness strip. Measured in Chromium at 320×568
   (`playwright-core` + `@sparticuz/chromium`), `#freshness-strip .fresh-cta` bottom lands at
   **622px** against the 504px first-screen limit, so `tests/browser_eaff7cce.cjs`'s
   "Pick-board CTA must be a first-screen phone tap at 320px" fails. Re-measured with the page
   clock pinned to the snapshot's own minute (2026-10-22T20:20Z): the notice is hidden and the
   CTA bottom is **459px**, i.e. the layout passes whenever the data is fresh. So the immediate
   cause is staleness, which this session's repair removes — but the banner still costs a stale
   visitor the first screen. Fixing it means editing `scripts/build.py` / `site/assets/**`,
   which session `fe7f5de4` has claimed; logged as a request in `COORDINATION.md` rather than
   edited here. No overflow at 320px (`scrollWidth == innerWidth`), and `#picks-at-a-glance`
   sits at 1625px (fresh) / 1787px (stale), inside the suite's 1700px ceiling only when fresh.
2. **The publish pipeline has no alarm for a red test step.** Two scheduled slots and ~8 hours
   were lost while `refresh-watchdog` kept reporting success (it dispatches the same workflow,
   which then failed the identical way). Nothing in the repository turns repeated
   `verify-build` failures into a visible signal on the site. Not repaired here: the watchdog is
   another session's shared scope (`scripts/refresh_watchdog.py`, `.github/workflows/refresh-watchdog.yml`)
   and no owner is currently active, so it is flagged rather than changed.
3. **Dormant historical pins remain.** `tests/test_session_75ebd2d6.py` still pins `1079654` and
   `1081150` to `research_rank` although both rows now publish an `exchange` line. They cannot
   block publication today because the strict branch is skipped for priced rows, and the scan in
   `NoStaleResearchTierPins` reports only pins that would actually block. Recorded so the next
   integrator does not mistake them for live assertions.
4. **One open row still publishes no percentage on the 04:59Z board** (`1082860` FlyQuest,
   HLTV world #61 vs an unranked Staqued). It keeps a sourced pick, a blank percentage and a
   per-source limitation; this is the documented research tier, not an omission. `1081149`
   has since been priced as `model_vrs_mirror`, which is why the retained 20:15Z row is stored
   as a hash-checked fixture for the negative controls instead of being read live.

## 6. Sources used for verification

* GitHub Actions run list and per-job step status — `api.github.com/repos/buffedlizard55-lab/MaltaProj4/actions/runs[/{id}/jobs]`
* Live/committed build manifest — `codeload.github.com` tarball of `main`, `build-info.json`
* Pages configuration — `api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages` (`build_type: legacy`, `source: main:/`)
* Board data — `data/latest.json` (`fixture_evidence`, `vrs_research`, `attempts`, `hltv_context`)
* Valve standings receipt cited on the row — `https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md`
* HLTV fixture/ranking links carried on the rows themselves — `https://www.hltv.org/matches/...`,
  `https://www.hltv.org/ranking/teams/...`

## 7. Live-state verification of the fresh published board (read-only, 2026-10-23 05:36Z)

The outage is over on `main`: the root-fallback commit `547be25` carries
`build-info.json` `built_at 2026-10-23T05:22:51.477590Z`, `snapshot_generated_at
2026-10-23T05:22:51.144308Z`, `rows 92`, and all **20** files it lists match their recorded sha256
(checked byte-for-byte on a `git archive origin/main` checkout). `data/latest.json` on that tree:
**92 fixtures, 30 open, 30 with a pick, 29 with a win probability, 1 with a pick and no percentage.**

Verified against those exact published bytes:

| Requirement | Measured |
| --- | --- |
| Executive summary links to the updated picks | `href="picks.html"`, `href="unresolved.html"`, `href="matches.html"`, `href="analysis.html"`, `href="#picks-at-a-glance"`, `href="#unresolved-picks"`, plus the "Where the updated picks are" banner — all present in `index.html` |
| Separate unresolved section inside the summary | `id="unresolved-picks"` with "Picks without a win probability" and "What is tried, in order, before a blank"; the one blank row (`1082860`) is named there **and** on `unresolved.html` |
| Every open match has a pick | 30/30; the summary states 30 open, 30 picked, 1 without a percentage |
| Phone readability | Chromium at 320×568, 390×844 and 1440×900 on `index.html`, `picks.html`, `unresolved.html`, `matches.html`, `analysis.html`: **no horizontal overflow at any size**, phone tab bar present on every page, pick-board CTA bottom **459px / 441px** (first screen), `#picks-at-a-glance` at **1665px / 1462px**, first pick table row on `picks.html` at **868px / 754px** |
| Validator on the live bytes | 92 rows, 29 calculations reproduced, 15 pages, **841** links/assets, 20 checksums, 232 displayed rows |

Two copy/UX defects measured on those bytes, both in `scripts/build.py` / `assets/**` (claimed by
session `fe7f5de4`, so logged in `COORDINATION.md` and **not** edited here):

1. The executive summary sentence reads "**30 open matches has a pick. 1 of them carry no win
   probability**" — agreement errors on the first screen of the site.
2. Minimum tap target among header/phone-tab links is **34px**, below the 44px guidance, even though
   the pick-board CTA itself is 44px+.
