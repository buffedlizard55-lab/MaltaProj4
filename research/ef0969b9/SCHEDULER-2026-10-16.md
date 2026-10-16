# Publication reliability: measured cadence, the failure mode, and the fix

Session `ef0969b9`, written 16 October 2026 (UTC). Scope: this session owns
`.github/workflows/pages.yml`, `.github/workflows/refresh-watchdog.yml`,
`scripts/refresh_watchdog.py`, `scripts/publish_gate.py` and
`tests/test_publish_gate_ef0969b9.py`. Session `1abe803f` owns the data and site
files; nothing here edits them.

Requirement being protected: *"So that we have a full list of updated matches and picks for
counter strike 2 from hotspawn every 4-8 hours."*

## 1. What was measured before changing anything

| Evidence | Command | Result |
| --- | --- | --- |
| Scheduled runs of `pages.yml`, all time | `gh api 'repos/buffedlizard55-lab/MaltaProj4/actions/runs?event=schedule&per_page=15'` | exactly three: 2026-10-15T16:59:51Z **success**, 2026-10-15T21:22:25Z **failure**, 2026-10-16T04:33:39Z **failure** |
| Which step failed at 04:33Z | `gh api repos/buffedlizard55-lab/MaltaProj4/actions/runs/38851255388/jobs` | `verify-build`: every step success. `deploy`: **"Deploy verified static dashboard" failure**, "Verify live Pages bytes match this exact build" skipped |
| Which step failed at 21:22Z | `gh api .../runs/38809354350/jobs` | step 11 "Build and independently verify every row…" failure, 22 s in (code since rewritten; later main runs pass this step) |
| Was the 04:33Z deploy actually a race? | `gh api repos/buffedlizard55-lab/MaltaProj4/deployments?environment=github-pages` and `.../deployments/<id>/statuses` | deployment **7110983154** (created 04:34:51Z, push-triggered) reached `success` 04:36:39Z while deployment **7110990374** (created 04:35:25Z, the scheduled run) went `queued → in_progress 04:35:30Z → failure 04:35:37Z` seven seconds later. Two deployments to the same `github-pages` environment overlapped |
| Is the live site stale? | `fetch_page https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json` | revision `f91ca1a9c96fdb94d0ef6f5b5ca5c45b31b0414e`, `snapshot_generated_at`/`built_at` 2026-10-16T05:11:55Z, **95 rows**, 20 checksummed files - fresh, but published by push-triggered runs, not by the schedule |
| Watchdog ticks | `gh api '.../actions/runs?event=schedule'`, workflow list | `refresh-watchdog.yml` (`*/30`) had **zero runs** at the time of this measurement |

Two conclusions follow, and they are the reason the workflow changed:

1. **Delivery is the binding constraint, not frequency.** After the hourly cron was
   merged (PR #32, 04:56Z) no scheduled slot fired for 05:17Z, 06:17Z or 07:17Z. A
   single hourly slot cannot be relied on, so the workflow now offers four slots an
   hour and skips cheaply when there is nothing to do.
2. **A failed `deploy` step is not proof that the dashboard is stale.** The 04:33Z
   run was superseded by an overlapping push-triggered deployment. The run now
   decides success on the published bytes, not on the action's exit code, and still
   fails when the live site is on an *older* build than the one it built.

## 2. What changed

### `scripts/publish_gate.py` (+ `tests/test_publish_gate_ef0969b9.py`, 18 tests)

Runs first, before any dependency install. Pure decision function `decide()`:

* `pull_request`, `workflow_dispatch` and `push` **always** run in full - those are the
  paths that put new code and new data on the site.
* A **scheduled** slot may skip only when all three are true: the live receipt is
  readable, its `revision` equals the commit being deployed, and its
  `snapshot_generated_at` (falling back to `built_at`) is inside a 60-minute budget.
* Everything else publishes: missing receipt, unparsable JSON, no timestamps, a
  different revision, an old snapshot, or a missing head SHA. The gate fails **open**.

When the gate skips, nothing is built, tested, uploaded or deployed, so there is no
unverified build anywhere - the site keeps serving the bytes of the last fully
verified publication. `--max-age-minutes` (default 60) is the only tunable.

### `.github/workflows/pages.yml`

* `schedule: '4,19,34,49 * * * *'` (four staggered slots an hour) replaces
  `'17 * * * *'`. The gate above is what keeps this cheap; the header comment records
  the measurement behind it.
* Every expensive step and the whole `deploy` job are gated on
  `steps.gate.outputs.publish == 'true'`; a skipped slot costs a checkout and one
  Python call and writes an explanation into the run summary
  (`### Scheduled slot skipped`).
* The gate's own decision for a hypothetical scheduled slot is printed into the run
  summary of **every** run (`### Freshness gate`, with `receipt_read`, snapshot age and
  the reason), so the freshness check is auditable from the Actions UI.
* `deploy`: attempt one is `continue-on-error`, a **retry** follows if it failed, and
  the run's outcome is then decided by the byte-for-byte live check: all files of the
  build manifest must match, except that a **strictly newer** live `built_at` is
  accepted as "superseded, not stale" and an **older** one fails the run. The live
  check keeps the `?deployment=<run_id>` cache-buster and its six attempts.

### `.github/workflows/refresh-watchdog.yml`

`*/10 * * * *` (was `*/30`) plus a `push` trigger on `main`, so a missed refresh is
noticed sooner and every merge re-arms the chain. The decision rules and budgets in
`scripts/refresh_watchdog.py` are unchanged (dispatch once, 45-minute cooldown, 10
dispatches per 24 h, never on an unreadable receipt).

## 3. Verification performed

* `python3 -m unittest tests.test_publish_gate_ef0969b9 -v` -> **18 tests OK** (rules,
  fail-open paths, CLI, `GITHUB_OUTPUT` writing).
* `.venv/bin/python -m unittest discover -s tests` -> **167 tests OK** (whole suite
  with the new tests in place).
* Local build chain on the committed snapshot: `python -m scripts.build` ->
  "Built 9 primary pages + 6 legacy redirects; 86 sourced rows, 0 priced, 22
  unresolved"; `python -m scripts.validate` -> 15 pages, 602 internal links/assets,
  20 artifact checksums, 216 displayed rows.
* Both workflows parse (`yaml.safe_load`) and the cron/gate structure was inspected
  step by step.
* **CI run [38866867244](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38866867244)** on
  `arena/ef0969b9-maltaproj4` (push, includes the new gate step): **success** -
  freshness gate step success, unit and independent failure-mode tests success,
  refresh of official sources success, build + independent row audit success,
  "Phone, tablet, desktop, accessibility and exact-boundary expiry checks" success;
  `upload-pages-artifact` and `deploy` correctly skipped off `main`.

## 4. Limitations, stated plainly

* **Scheduled delivery cannot be verified from here.** Whether GitHub actually
  delivers the new slots is only observable over the coming hours. The gate turns a
  late or dropped slot into "no harm done" rather than a claim that the schedule now
  works; the watchdog remains the backstop.
* **The gate's network path is exercised in CI, not in the authoring sandbox:** this
  sandbox cannot reach `buffedlizard55-lab.github.io` over raw HTTP (TLS EOF), so
  `fetch_receipt()` is covered by unit tests with an injected receipt plus the
  in-CI diagnostic, not by a local end-to-end run.
* **Run logs and job artifacts are not downloadable from the sandbox** (`gh run view
  --log`, `gh run download` return EOF from the results CDN), so CI evidence here is
  step-level conclusions plus the run summary the workflow itself writes.
* The 60-minute budget is a policy value, not a measured optimum: it is half the
  previous watchdog threshold (90 min) and an eighth of the eight-hour evidence
  window, so a skipped slot can never leave a pick unrefreshed beyond ~1 hour plus
  whatever the scheduler delivers late.

## 5. Post-merge delivery check — measured, and not yet what we want

Everything below was read from the official Actions API after PR #36 merged
(`fa2b4d84`, 07:33:26Z) and the main push run `38867976175` completed successfully.

| Measurement (polled 07:43Z → 08:07Z, once a minute) | Result |
| --- | --- |
| Scheduled runs of `pages.yml`, repository-wide | **still 3** — 16:59:51Z success, 21:22:25Z failure, 04:33:39Z failure |
| Scheduled runs of `refresh-watchdog.yml` | **0** (its only run so far is the push run `38867976068`, success) |
| The new `08:04Z` slot | **not delivered** by 08:07Z |
| Push-triggered delivery | works every time: `38867976175` ran verify + deploy and the live check passed |

So the honest status is:

* **Push delivery is proven; cron delivery is still unproven in this repository.** GitHub
  scheduled workflows here have a track record of arriving hours late (4h42m, 3h05m) or
  not at all (zero runs between the hourly cron merge and the next morning), and the new
  `4,19,34,49` slots have not yet produced a single run. Scheduled workflows can be
  delayed by GitHub for many minutes under load, so a slot missing at +3 minutes is not
  proof it will never arrive — but three slots an hour are the cheapest available hedge,
  and the watchdog is a second one.
* **What the change already guarantees:** whenever *any* trigger fires — a late cron
  slot, a push, a manual dispatch, the watchdog — the freshness gate lets it through
  only if the live snapshot is older than 60 minutes, so a late delivery still refreshes
  the board instead of being skipped as redundant. A skipped slot costs seconds and
  writes its reason into the run summary.
* **What no workflow change can guarantee here:** delivery itself. The mitigation for a
  missed refresh stays what the site already does — a visible staleness notice, a
  `review.html` entry and `sources.html`, and the watchdog's dispatch attempts inside its
  own budget (once per 45 minutes, at most 10 per day). The board's own wording — "the
  schedule is a target, not a guarantee" — is accurate and should stay.

A background watcher (`gh api …/runs?event=schedule` every minute) keeps a timestamped
log of every scheduled run so the next check can state exactly when, or whether, a slot
arrived.
