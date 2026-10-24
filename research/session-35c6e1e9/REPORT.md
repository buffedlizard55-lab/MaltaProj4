# Session 35c6e1e9 — verification report

**Branch** `arena/35c6e1e9-maltaproj4` · **date** 2026-10-24 · **author** Arena session `35c6e1e9`

Scope was chosen *after* reading the board: at claim time (05:45Z) **twelve** other sessions had pushed
between 05:30Z and 05:37Z and **all twelve** were editing the same contested file,
`tests/test_session_0cc1138a.py`. Session `019a253a` landed that repair as PR
[#240](https://github.com/buffedlizard55-lab/MaltaProj4/pull/240) (`60a150b`) and session `d2a55add`
landed the executive-summary bar as PR
[#246](https://github.com/buffedlizard55-lab/MaltaProj4/pull/246) (`dd92178`). This session did not
touch either file. It took the two defects nobody had claimed, both of which are *why the board keeps
freezing*, and both verified from official sources.

Everything below was measured. Where the sandbox could not read a source, that is stated as a
limitation instead of being inferred.

---

## 1. The 17.7-hour publication freeze (verified, and now recovered)

### 1.1 What was wrong

| Fact | Value | Official source |
| --- | --- | --- |
| Consecutive failed `pages.yml` runs on `main` | **5** | [39956197341](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39956197341) 2026-10-23T12:49:03Z · [39998307424](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39998307424) 17:50:02Z · [40025828846](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40025828846) 21:18:45Z · [40042111432](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40042111432) 23:53:03Z · [40062143026](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40062143026) 2026-10-24T04:23:24Z |
| All five on one unmoved commit | `5d56f35e7fd8a4e185c7192197c3b8c2b3b4fa70` | `GET /repos/…/actions/workflows/pages.yml/runs?branch=main` |
| Failed step, read from the jobs endpoint for **each** of the five run ids | `Unit and independent failure-mode tests (verify-build)` | `GET /repos/…/actions/runs/{id}/jobs` |
| `deploy` job on each | `skipped` | same |
| Published snapshot at the time | `2026-10-23T11:47:19.504519Z` → **1066 min** old at 05:33Z | `GET /repos/…/pages/builds/latest` (`status: built`, `commit 5d56f35e`, `created_at 2026-10-23T11:48:51Z`) and the served `build-info.json` |
| The snapshot's own evidence TTL | `stale_after_hours: 8` (= 480 min) | `data/latest.json` at `5d56f35` |
| Consequence | every open pick withheld on the live board | `#runtime-stale` banner in the served `index.html` |

**Root cause, reproduced locally** on a clean `5d56f35` checkout (Python 3.11.2, pinned
`requirements.txt`): `Ran 1195 tests … FAILED (failures=1, errors=1, skipped=3)` —

- `tests/test_session_0cc1138a.py::LiveHotspawnCoverage::test_snapshot_covers_the_observed_lobby_fixtures`
  → `AssertionError: '1081148', '1079655' … lobby fixture missing from the board`
- `…::test_each_observed_fixture_is_published_with_a_pick_and_an_official_link` → `KeyError: '1081148'`

`OBSERVED_OPEN` pinned the 30 fixture IDs the lobby showed at 2026-10-23T09:44Z. The excuse added by
session `b6e37c61` (`inventory_changes.removed_ids`) only holds for the single snapshot that recorded
the removal: at 11:47Z the field reads
`{"compared_with": "2026-10-23T11:25:13.929047Z", "added_ids": [], "removed_ids": []}`, so the excuse
rolled out of the comparison window one snapshot later and the assertion became permanently false.
Hotspawn rotating its own lobby is normal, not a data error.

**Repaired by session `019a253a`, PR [#240](https://github.com/buffedlizard55-lab/MaltaProj4/pull/240).**
Not this session's file; recorded here because it is the cause of the freeze this session was asked to
end. Verified: on `60a150b` the suite passes, and run
[40067946986](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40067946986) took
`verify-build` to **success** — the first green publish run since 2026-10-23T11:37Z.

### 1.2 The board after recovery

Read from `origin/main` `data/latest.json`, snapshot `2026-10-24T05:59:34.228578Z`, fixtures observed
`2026-10-24T05:55:58.459230Z`:

| Measure | Value |
| --- | --- |
| Feed rows / three-view parity (`api`/`page`/`lobby`/`retained`) | 88 · **88 / 88 / 88 / 88** · `coverage: verified` |
| Open matches | **25** |
| Open matches with a pick | **25 / 25** |
| Open matches with a win probability | **25 / 25** |
| Unresolved (open, no pick at all) | **0** |
| Research-only (pick, no percentage) | **0** |
| Methods | `exchange` 12 · `model_vrs` 7 · `exchange_wide` 2 · `model_vrs_mirror` 2 · `bookmaker_fallback` 2 |
| `not_open` feed rows retained for visibility, never priced | 63 |

Row-by-row ledger, every row with its official fixture link **and** its official price-evidence link:
[`OPEN-ROW-LEDGER.md`](OPEN-ROW-LEDGER.md). Independent re-derivation of all 88 rows from their own
archived evidence: [`independent-row-audit.md`](independent-row-audit.md) — **0 arithmetic/field
failures**.

Price evidence hosts across the 25 open rows, counted from the snapshot: `polymarket.com`,
`github.com` (Valve's own `counter-strike_regional_standings` file, at a pinned commit), `bo3.gg`
(Thunderpick rendering). **No probability on this board comes from Hotspawn** — Hotspawn supplies
fixture identity and lock times only, which is the user's rule and the pipeline's contract.

### 1.3 The alert that never fired (this session's first repair)

The escalation issue exists precisely to make a red gate visible. It did not fire.

| Fact | Value | Official source |
| --- | --- | --- |
| Watchdog decision, replaying its own pure `evaluate()` against the real run list and the real published receipt | `action='stop'`, `consecutive_failures=5`, `should_escalate=True` — *"5 consecutive failed runs on commit 5d56f35e while snapshot is 1066 min old"* | reproduced locally; inputs from `GET /repos/…/actions/workflows/pages.yml/runs?branch=main` |
| Escalation issue titled `Publish gate is red: no CS2 picks can be published` | **does not exist** | `GET /search/issues?q=…in:title "…"` → `total_count: 0` |
| Open issues in the repository | `[239, 204, 7, 5, 1]` — none is the escalation | `GET /repos/…/issues?state=open` |
| The same search shape, as a control | finds #204 (`total_count 1`) and #239 (`total_count 1`) | same endpoint |
| Every watchdog tick in the window | `success` | [40065251776](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40065251776) 05:10:57Z, [40047031321](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40047031321) 00:51:25Z, [40033438852](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40033438852) 22:24:47Z |

A green tick means `problems` was empty and `main()` returned `0`, so both the run history and the
published receipt were read successfully. The decision was therefore `stop` with escalation required,
and no issue was filed.

**Which call raised is not provable from this sandbox and is not asserted here.** Actions log download
(`results-receiver.actions.githubusercontent.com`) is outside the authoring egress allowlist, so the
run logs could not be read; `gh run view --log-failed` returns `EOF`. What *is* provable from the code
is that the design guaranteed the silence: a required escalation that fails is caught by
`except Exception`, recorded only as `report['escalation'] = 'failed: …'` inside a log nobody reads,
and the tick still exits `0`. Its own docstring records the same failure mode on 2026-10-23 — an
8 h 40 min frozen board with "nothing anywhere said why". This one ran 17.7 h.

**Repaired** in `scripts/refresh_watchdog.py` / `.github/workflows/refresh-watchdog.yml`, with
34 tests in `tests/test_refresh_watchdog.py` (was 22):

1. **No Search-API dependency.** `find_open_issue` now reads the core REST listing
   `GET /repos/{repo}/issues?state=open&per_page=100&page=N` (bounded to three pages), skipping pull
   requests and matching the exact title. That is the same API family the run-history read already uses
   successfully in the same tick, so the alert no longer needs a second, separately limited service to
   be reachable. Verified against the live API: returns `None` for the escalation title and enumerates
   `[239, 204, 7, 5, 1]`.
2. **A silent alert is not an alert.** A required-but-undelivered escalation now emits an `::error::`
   workflow annotation and the tick exits `1`. The decision-rule tests moved to `if: always()` so a red
   tick still proves them.
3. **Escalate on the harm, not only on one cause.** `should_escalate(action, streak,
   outside_evidence_window=False)` now also fires when the watchdog has *stopped* while the published
   snapshot is outside its evidence window (`--evidence-window-minutes`, default **480** = the
   snapshot's own `stale_after_hours: 8`). The budget-exhausted and unknown-state stops carry no
   streak at all, so a streak-only rule left the first ~10 h of this outage unannounced. The
   two-argument contract is unchanged, so every existing caller and assertion keeps its meaning.
4. **The issue names the failing step.** New `failing_steps()` reads
   `GET /repos/{repo}/actions/runs/{id}/jobs`, best-effort by design — the alert must still be filed
   when that lookup fails. Verified live: returns
   `['Unit and independent failure-mode tests (verify-build)']` for all five failed run ids.
5. **Recovery closes its own alert.** `close_escalation()` comments and closes, but only an issue
   carrying both the exact title and the watchdog marker, so an open escalation always means a board
   that is frozen *right now*.

---

## 2. Main went red again 11 minutes after recovery (verified, and repaired)

PR #246 merged at `dd92178` with both CSS copies identical. Eleven minutes later the root-fallback
publisher broke them.

| Commit | `assets/style.css` | `site/assets/style.css` | `.exec-bar` rules | State |
| --- | --- | --- | --- | --- |
| `60a150b` (PR #240) | `cffb06e4…` | `cffb06e4…` | 0 / 0 | identical |
| `dd92178` (PR #246) | `ad856f14…` | `ad856f14…` | 15 / 15 | identical |
| `f54b37a` *"Publish the verified build to the legacy main:/ root fallback"*, `cs2-scout-publisher`, 2026-10-24T06:02:34Z | **`cffb06e4…`** | `ad856f14…` | **0** / 15 | **diverged** |

`git show --stat f54b37a` records `assets/style.css | 43 -`: the publisher deleted 43 lines,
reverting that one file to the PR #240 content while its twin kept the PR #246 content. Measured
consequence on a clean checkout of `f54b37a`: **five** committed tests fail —

`test_session_0cc1138a.BothTeamsOnPhoneCards.test_both_published_css_copies_carry_the_score_rows`,
`test_session_138cbedd.FreshnessStripMarkup.test_stylesheet_marks_an_overdue_snapshot`,
`test_session_5f1df842.PhoneLayoutTests.test_the_site_stylesheet_is_the_one_that_ships`,
`test_session_d2a55add.ExecutiveSummaryBarTests.test_phone_ordering_rule_and_identical_css_copies`,
`test_session_dddcb90d.StalePhoneLayoutFix.test_style_copies_stay_byte_identical`.

Because that suite runs **before** refresh, build and deploy in `pages.yml`, main was already
deadlocked again — the same shape as the freeze in §1, eleven minutes after it ended.

### 2.1 Mechanism, proven from source

- `scripts/build.py:1606` — `shutil.copytree(ROOT/'site/assets', out/'assets', dirs_exist_ok=True)`.
  So **`site/assets/style.css` is the source of truth**; `public/assets/style.css` is a copy of it.
- `scripts/stage_legacy.py` — `ALLOWED` contains `assets/style.css` and `assets/app.js`, and does
  **not** contain `site/assets/style.css` or `site/assets/app.js`. The publisher therefore moves one
  half of a pair that five tests require to be byte-identical, and never moves the other.
- Running the build on `f54b37a` proves which copy is stale: `scripts.build` regenerates
  `public/assets/style.css` as `ad856f14…` with **15** `.exec-bar` rules — identical to
  `site/assets/style.css`, and not the committed `assets/style.css`.

What is **not** provable from here: the exact step ordering that let the publisher commit a divergent
tree, since `publish()` runs `python -m unittest discover -s tests` before committing and that should
have caught it. The run logs are unreachable from this sandbox (same egress limitation as §1.3), so
this is **flagged for review rather than asserted**.

### 2.2 Repair

- **Restored, not hand-written.** `assets/style.css` was replaced with `scripts.build`'s own generated
  output, byte-identical to `site/assets/style.css` (`ad856f14…`, sha256 `c4f8aad1…`), then the whole
  hash-verified build was staged to the root through the sanctioned path
  (`python -m scripts.stage_legacy`), so `build-info.json`'s manifest agrees with the file it
  describes. No CSS was authored and no assertion was weakened.
- **Guarded, so it cannot recur.** `scripts/publish_root_fallback.py` gains `asset_divergence(public,
  root)`: a pure, byte-exact comparison of each staged copy in `public/assets/` against its committed
  source in `site/assets/`. A non-empty result means `public/` was built from a *different* source
  than the one now committed, so staging would break the required identity — the module then refuses,
  with a machine-readable reason naming commit `f54b37a`, and writes nothing. Refusal is a normal exit
  with a reason, matching every other refusal in that module, so a green build is logged rather than
  failed. 7 new tests in `tests/test_session_35c6e1e9.py` cover the safe case, the exact `f54b37a`
  shape, `app.js`, a missing copy, and the repaired committed state.

---

## 3. The publication-continuity auditor (new, advisory)

`scripts/verify_35c6e1e9.py` answers the one question this repository could not answer automatically,
because every existing auditor runs *inside* the pipeline it audits:

> Is the board the public actually sees current — and if it is not, what stopped it, at which step, on
> which commit, and for how long?

It reads three official sources and compares them with each other, never with a value the pipeline
asserted about itself: the live Pages build receipt, the `pages.yml` run history plus each failed
run's job/step conclusions, and the committed snapshot for its own stated TTL and rows. `--live`
produces a dated receipt; `--offline` audits only committed artifacts so it can run with no network.

Two dated receipts are committed as evidence:

- [`continuity-receipt-OUTAGE-2026-10-24T0602Z.json`](continuity-receipt-OUTAGE-2026-10-24T0602Z.json)
  / [`CONTINUITY-OUTAGE-2026-10-24T0602Z.md`](CONTINUITY-OUTAGE-2026-10-24T0602Z.md) — verdict
  **frozen**: streak 5 on `5d56f35e`, all five runs naming
  `Unit and independent failure-mode tests (verify-build)`.
- [`continuity-receipt-RECOVERY-2026-10-24T0620Z.json`](continuity-receipt-RECOVERY-2026-10-24T0620Z.json)
  / [`CONTINUITY-RECOVERY.md`](CONTINUITY-RECOVERY.md) — chain back in flight
  ([40069834693](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40069834693)), 25 open
  rows all sourced, all picks reproducible.

**This auditor is advisory and must never become a merge gate**, and
`tests/test_session_35c6e1e9.py::NeverAMergeGate` pins that `.github/workflows/pages.yml` does not
invoke it. It reads wall-clock staleness, so a committed baseline older than its own evidence window
is *normal* between refreshes; blocking on that would recreate exactly the deadlock in §1. For the
same reason an offline run reports a stale committed baseline as a **flag**
(`committed_baseline_outside_evidence_window`) and never as proof the live site is frozen, and an
unread run history as `run_history_not_read` — undecidable, not red. An empty board reports
`no_open_rows` rather than "all zero open rows are sourced", because a vacuous pass is worse than no
check.

---

## 4. The user's product requirements, verified against the built pages

Verified by parsing the committed `index.html` (regenerated from snapshot
`2026-10-24T05:59:34Z`) rather than by reading prose about it.

| Requirement | Verified state |
| --- | --- |
| Executive summary with in-site links to the updated picks | `index.html` `<title>` is *Executive summary · CS2 Scout*. `#coverage-now`, `#exec-banner` and `nav.exec-summary-links` carry in-site links to `picks.html`, `#picks-at-a-glance`, `unresolved.html`, `matches.html`, `matches.html#feed-scope`, `sources.html#method`, `review.html` |
| Picks easy to find on a phone | `#picks-at-a-glance` renders **25** `a.glance-card-mobile` cards, **25/25** `data-glance-priced="1"`; `<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">`; `#exec-summary` with the always-visible `.exec-bar` is present in the page and in `assets/style.css`, and the phone ordering rule `body[data-page="index"] main>#exec-summary{order:5}` keeps the pick list on the first screen |
| Probability obvious per team, pick obvious | Card 1 (`evidence.html#match-1079193`) renders `OUR PICK` + `.glance-card-pick-team` **FOKUS 78.5%** and `.glance-card-score.other` **ex-6666 21.5%**, plus a `.glance-card-prob-bar` at `width:78.5%`. Checked against the snapshot: `teams == ['FOKUS','ex-6666']`, `probabilities == [0.785, 0.215]`, `pick == 'FOKUS'` → the tagged team **is** the larger probability |
| Separate section for unresolved picks **and** the limitations, inside the executive summary | `#unresolved-limits` (heading *Unresolved picks, and why a pick can be missing*) sits in the summary next to `#picks-at-a-glance`. Its links, read from the page: `#unresolved-summary`, `unresolved.html`, `review.html`, `sources.html#method`, `sources.html#model`, **and the two research fallbacks the user asked for** — `https://www.hltv.org/matches` and `https://egamersworld.com/counterstrike/matches`. `#pick-limitations` lists **9** dated, source-linked limitations; `#unresolved-picks` and `#unresolved-summary` are separate sections; `nav.exec-summary-links` and the anchors `#coverage-now`, `#exec-banner`, `#picks-at-a-glance`, `#unresolved-picks`, `#unresolved-summary`, `#pick-limitations`, `#how-picks`, `#detailed-summary` all resolve |
| Percentages from outside betting lines, never from Hotspawn | 16 of 25 from betting markets, 9 from our own Valve-standings model; evidence hosts are `polymarket.com`, `github.com` (Valve), `bo3.gg` — see §1.2 |
| Refresh every 4–8 h | `pages.yml` cron `4,19,34,49 * * * *` (four slots an hour) plus a `*/10` watchdog. **Actual delivery is the binding constraint, not the cron** — see irregularity F3 |
| No manual input | The whole chain (refresh → quarantine → build → validate → independent audits → browser gates → publish → live-byte verification) is automated; nothing in this session was typed by hand into the data |

**Limitation on this section:** the phone/tablet/desktop and axe accessibility suites
(`npm run test:browser`, six Chromium suites) were **not** run locally. Playwright's Chromium download
host is outside this sandbox's egress allowlist, so `@sparticuz/chromium` cannot be fetched here. They
run in CI on the pull request and are reported in §6. The markup, viewport, ordering rules and card
structure above were verified directly from the committed HTML and CSS.

---

## 5. Irregularities flagged for review

Non-blocking, published with their sources, none inferred.

- **F1 — the root-fallback publisher reverted a committed asset (`f54b37a`).** Proven in §2. Repaired
  and guarded. **Still open for review:** how a divergent tree passed `publish()`'s own
  `python -m unittest discover -s tests` before committing. Unprovable from this sandbox (Actions log
  host unreachable); needs a runner-side read of run
  [40068512182](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40068512182) /
  [40067946986](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40067946986).
- **F2 — the watchdog's alert path did not deliver during a 17.7 h outage** while every tick reported
  `success`. Proven in §1.3; the raising call is not identifiable from here. Repaired so that the cause
  no longer matters.
- **F3 — scheduled delivery, not the cron expression, is the binding constraint.** `pages.yml` asks for
  four slots an hour; GitHub delivered **five** scheduled runs in the 16 h from 2026-10-23T12:49Z to
  2026-10-24T04:23Z (≈ one per 2.5–4.5 h), and the `*/10` watchdog delivered **five** ticks in 14 h.
  The auditor reports this as `no_recent_run`. Documented in the repo since 2026-10-15; unchanged and
  not fixable from inside the repository.
- **F4 — `stage_legacy.ALLOWED` omits `site/assets/*`.** This is the structural reason a staged build
  can move one half of a byte-identical pair. Guarded at the publisher (§2.2); whether `site/assets/`
  should instead be *inside* the staged set is a design question for the owning session, not something
  this session changed unilaterally.
- **F5 — 63 of 88 feed rows are `not_open`** yet still returned by the endpoint with
  `status: scheduled`. The snapshot records this itself: *"63 feed entries are not open by sourced
  timestamps/status. They remain in All matches and are not treated as future picks."* They are listed
  and never priced. Official source:
  [the fixtures endpoint](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1).
- **F6 — 12 concurrent sessions edited one file.** All twelve branches pushed 05:30–05:37Z on
  2026-10-24 touched `tests/test_session_0cc1138a.py`, and one of them
  ([PR #217](https://github.com/buffedlizard55-lab/MaltaProj4/pull/217), stale since
  2026-10-23T11:27Z) is `CONFLICTING`/`DIRTY`. Coordination, not data; recorded in
  [issue #239](https://github.com/buffedlizard55-lab/MaltaProj4/issues/239). Six open PRs
  (#233, #228, #225, #221, #220, #217) still carry stale `data/latest.json` from 2026-10-23 and must
  not be merged over the recovered board.
- **F7 — three `exchange_wide` rows are labelled low-confidence by the pipeline itself** (spread wider
  than the standard gate). They are published with the label `Wide line · low confidence` and their
  numbers, not silently. Source: the row's own badge and `#pick-limitations`.

---

## 6. Gates run for this session

Local, on the exact branch head, Python 3.11.2 with the pinned `requirements.txt`:

| Gate | Result |
| --- | --- |
| `python -m unittest discover -s tests` | **Ran 1278 tests — OK (skipped=1)** |
| `python -m unittest discover -s audits -p 'test_*.py'` | **Ran 9 — OK** |
| `python verification-95b588c2/test_integrity.py` | **Ran 5 — OK** |
| `python -m unittest discover -s verification-c6 -p 'test_*.py'` | **Ran 12 — OK** |
| `python -m scripts.validate --data data/latest.json --site .` | 88 rows verified · **25 probability calculations reproduced** · 15 pages · 822 internal links/assets · 20 artifact checksums · 216 displayed rows |
| `python verification-c6/audit_snapshot.py data/latest.json` | 88 rows · **0 failures** |
| `python -m scripts.verify_35c6e1e9 --offline` | exit 0 · verdict `current-with-flags` · 2 honest flags, 0 frozen |
| `python -m unittest tests.test_refresh_watchdog` | **Ran 34 — OK** (was 22) |
| `python -m unittest tests.test_session_35c6e1e9` | **Ran 32 — OK** |
| `npm run test:browser` | **not run locally** — Chromium download host outside the sandbox egress allowlist; runs in CI (see §4 limitation) |

Before this session's repair the same checkout of `f54b37a` produced **6 failures**; after restoring
the generated CSS and staging the hash-verified build, **0**.

---

## 7. Files changed by this session

| File | Change |
| --- | --- |
| `scripts/refresh_watchdog.py` | alert path: REST dedupe, loud failure, harm-based escalation, failing-step names, auto-close on recovery |
| `.github/workflows/refresh-watchdog.yml` | documented the exit-code contract on the alert step; decision-rule tests now `if: always()` |
| `tests/test_refresh_watchdog.py` | 22 → 34 tests, including negative cases for every new rule |
| `scripts/publish_root_fallback.py` | `asset_divergence()` guard + `PAIRED_ASSETS`; refuses to stage a build that would break a byte-identical pair |
| `scripts/verify_35c6e1e9.py` | new publication-continuity auditor (advisory; live + offline modes) |
| `tests/test_session_35c6e1e9.py` | new: 32 tests, incl. the never-a-merge-gate pin and the paired-asset guard |
| `assets/style.css` | restored from `scripts.build`'s own output to match `site/assets/style.css` |
| `build-info.json`, `index.html`, `review.html`, `data/latest.json`, `data/matches.csv` | regenerated by staging the hash-verified build through `scripts.stage_legacy` |
| `research/session-35c6e1e9/**` | this report, the open-row ledger, the independent row audit, two dated continuity receipts |
| `COORDINATION.md` | claim (additive) + receipt (additive) |

Not touched: `tests/test_session_0cc1138a.py`, `scripts/build.py`, `scripts/summary.py`,
`site/assets/**`, `data/review-notes.json`, and every other session's `research/` or
`verification-*` directory.
