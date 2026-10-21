# Session dee046c2 — cross-session requests (logged, not applied)

This session edits only `research/session-dee046c2/**`, `verification-dee046c2/**`,
`scripts/probe_dee046c2.py`, `tests/test_session_dee046c2.py`,
`.github/workflows/harvest-dee046c2.yml` and its `COORDINATION.md` rows. Everything below is a
request to the owning session / final integration, with the dated evidence that motivated it.

## R-1 · Pages legacy race republishes the committed root fallback between publishes

- **Observed, dated:** ~20:12Z the live `build-info.json` read the fresh artifact
  (rev `47f230b`, built 19:57:45Z) while the live `index.html` served the *committed root
  fallback* (18 Oct data, red "picks are withheld" banner). Every push to `main` also fires
  `pages-build-deployment` (legacy `source: main:/`), which can land after `pages.yml`'s artifact
  deploy and briefly serve the fallback until the next slot re-publishes.
- **Asks:** (a) owner-level switch of Pages source to GitHub Actions (the API attempts return
  HTTP 403 for this integration — a repository setting only the owner can change; first noted by
  84295759 §7, still `legacy` at 20:2xZ by a980a709's GET); (b) meanwhile, re-stage the committed
  root fallback from a *fresh runner snapshot* as a guarded, main-only step in `pages.yml`
  (`scripts.build` + `scripts.validate` + `scripts.stage_legacy` + commit), so a legacy win shows
  current data rather than 18 Oct.
- **Mitigation that already works (verified by this session):** the fallback's expiry banner
  suppressed every pick with words; `verify_live` passed on 20:12Z and 20:20Z publishes
  (runs 39668307571, 39669384223), and the next slot restored the artifact.

## R-2 · Watchdog misses the gaps it exists to catch when GitHub's scheduler slips

- **Measured:** the 4,19,34,49 cron produced scheduled main runs only at 15:03:48Z and
  19:16:10Z (gap **4 h 13 m**, inside the 4–8 h promise but far outside the watchdog's 90-minute
  target), and the watchdog's own `*/10` cron delivered only two ticks in that window
  (15:28:11Z, 19:27:14Z) — so no dispatch was ever attempted during the gap.
- **Ask:** in `refresh-watchdog.yml`, also trigger the tick on `push: branches: ['**']` (or at
  least `pull_request: synchronize`) with the existing cooldown + daily budget; while the repo is
  busy with parallel sessions, every push becomes a free staleness check and the mitigation stops
  sharing a single point of failure with the scheduler it compensates for.

## R-3 · PR #119's report table disagrees with the published lines for two fixtures (prose only)

- **1082793 `5star vs 1WIN`:** the board and every pipeline replay publish `model_vrs`
  **24.30 / 75.70** from quote id `vrs-2026-10-05-80-38` (#80 vs #38 in Valve's global file);
  this session reproduced 24.2986/75.7014 at 20:30Z and 20:45Z, **delta 0.0**, from Valve's file
  at commit `eec4853`. `research/session-db1f35c5/REPORT.md` instead states "36.3% / 63.7%
  (#96 vs #59)".
- **1082858 `Ground Zero vs Off Chops`:** the board publishes **39.83 / 60.17** (rows #136,
  878 pts vs #119, 971 pts); this session's replay at 20:45Z returns 39.831/60.169, **delta
  0.0**. The report table says "40.9% / 59.1%".
- No data file carries the prose numbers; the published board is arithmetically correct from
  Valve's own inputs, and the report text is stale/wrong on these two lines.
- **Ask:** session db1f35c5 (or integration) corrects those REPORT.md table rows so the research
  prose and the published rows cannot diverge for a human reviewer.

## R-4 · PR #119's two new EGW `rejected_listings` entries cite URLs in a format EGW does not use

- **Dated evidence:** the entries (observed_at 2026-10-21T20:05Z) use
  `https://egamersworld.com/counterstrike/match/CCTEU8/...` and `/DFRAG26/...`. Every EGW match
  page seen by this repo (and by sessions 96ea1af8/b214c818) follows
  `/counterstrike/match/<opaque-id>/<slug>-<opaque-id>`; the benched-gods page actually read was
  `/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn` (403 from at least two runners). The
  *decisions* (1.8/1.8 placeholder → refuse; no pricing) are consistent with every other source
  read and change no published number; only the citation looks unverifiable.
- **Ask:** owner of `data/book-receipts.json` re-checks the two rejection citations against the
  pages actually fetched (or replaces them with the fetched opaque URLs + raw captures), so the
  rejection ledger stays replayable line by line like every other receipt.

## R-5 · Stale open PRs from earlier sessions

- #88 (2026-10-19), #64 (2026-10-17), #23 (2026-10-15) are still open with no commits since
  main absorbed the same territory several times over (precedent: session 0b26ea9a closed #93 as
  superseded after checking its one-line change was already in main).
- **Ask:** final integration diffs each; close as superseded where the content already landed,
  rebase and merge where it has not. (Flagged here, not done here: closing others' PRs is shared
  output.)
