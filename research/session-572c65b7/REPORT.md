# Session 572c65b7 — why the board had no picks, and what was repaired

All times UTC. Every number below was measured in this session; nothing is
carried over from another session's claim without saying so.

## 1. The symptom, measured on the live site

At **16:2xZ on 2026-10-24** the public board served
`https://buffedlizard55-lab.github.io/MaltaProj4/` with this text:

> **Snapshot expired or timestamp unverified.** Current picks are withheld.
> … 22 open CS2 match(es) · **0 with a pick** · 0 with a win probability ·
> 22 unresolved

The independent live audit job `120919620027` (run
[40110028068](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40110028068))
recorded the same state from its own read at `2026-10-24T16:07:12Z`:

| Field | Value |
| --- | --- |
| live `build-info.json` revision | `71eddff` (built `2026-10-24T08:26:58Z`) |
| `snapshot_generated_at` | `2026-10-24T08:06:51Z` |
| `snapshot_age_seconds` | `29041.8` (8 h 04 m) |
| `inside_eight_hour_window` | `false` |
| `actionable_at_check` | `0` |
| `live_build.verdict` | `match` (20 files, bytes identical to that build) |

So the published bytes were correct and internally consistent; the board simply
had not been refreshed for eight hours, and the site's own rule then withheld
every pick. That rule is deliberate (an expired price is not a current
recommendation) and was not changed.

## 2. Why it had not refreshed: the failed step

Every `pages.yml` run on `main` from **09:03:32Z** to **13:16:15Z** failed at the
same step:

| Run | Created | Commit | Failed step |
| --- | --- | --- | --- |
| [40080448344](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40080448344) | 09:03Z | `1ae6445` | 15 — Keep the legacy main:/ root fallback on the verified build |
| [40082763751](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40082763751) | 09:38Z | `99253f7` | same |
| [40084520702](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40084520702) | 10:05Z | `45fc6ba` | same |
| [40097410704](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40097410704) | 13:16Z | `45fc6ba` | same |

Step timings of the last one (job `120882445087`) show that everything else
worked:

```
11 Refresh official sources                         13:17:02Z -> 13:20:38Z  success
12 Withhold any row the independent audit cannot reproduce   13:20:38Z  success
13 Build and independently verify every row          13:20:38Z -> 13:20:40Z  success
14 Phone/tablet/desktop/accessibility/browser gates  13:20:40Z -> 13:21:41Z  success
15 Keep the legacy main:/ root fallback              13:21:41Z -> 13:22:10Z  FAILURE
16 Record the exact artifact expected at the site    13:22:10Z  skipped
19 actions/upload-pages-artifact                     13:22:12Z  skipped
deploy job                                           skipped
```

The step's own annotation was: *"The staged root failed its own validator or
unit gate"* — i.e. `publish()` returned **3**. The site is still served from the
committed `main:/` root (the Pages `PUT` that would switch it to the Actions
artifact answers HTTP 403), so refusing that commit is what froze the board.

## 3. Reproducing the gate

The first diagnostic (run
[40111643580](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40111643580))
captured a live snapshot. Replaying publication against it locally reproduced
the refusal; `scripts.validate` passed while the unit gate failed on one row.
That defect (an exactly even Polymarket line published as a probability with no
pick, `1079200 Color vs ex-Zero Tenacity`) was repaired in commit `1363318`,
which also made the staging step non-blocking. The suite went to **1500 tests
OK**.

The second diagnostic (run
[40112854117](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40112854117),
4 m 53 s, success) re-ran the whole publication path on that commit with real
network access. Its committed evidence is
`research/session-572c65b7/diag/`:

| Gate | Result |
| --- | --- |
| `summary.json` | 83 rows · 22 open · **22 with a pick** · **22 with a probability** · 0 without either · `coverage: verified` (83/83 api, page, lobby, retained) |
| `quarantine.log` | `{"withheld_rows": 0, "snapshot_level_failures": []}` |
| `publish.log` | `{"publish": true, …}` · `publish_rc=0` (22 files staged) |
| `staged-validate.log` | 83 rows, 22 calculations, 15 pages, 787 links, 20 checksums, 195 displayed rows · `validate_rc=0` |
| `staged-c6.log` | 12 tests OK · `c6_rc=0` |
| `staged-unit.log` | `Ran 1493 tests … FAILED (errors=2, skipped=7)` · `unit_rc=1` |

## 4. The remaining root cause: the gate was coupled to live fixtures

The two errors name fixtures, not code:

```
ERROR: setUpClass (test_session_35c6e1e9.VerifierConsultsTheSourcedAliasRegister)
  File "tests/test_session_35c6e1e9.py", line 315, in setUpClass
    cls.row = next(m for m in SNAPSHOT['matches'] if m['id'] == '1083121')
StopIteration
ERROR: test_known_listing_and_model_arithmetic (test_session_e9be3e6b.SourceLadderVerification.…)
  File "tests/test_session_e9be3e6b.py", line 106, in test_known_listing_and_model_arithmetic
    model = by_id['1081152']['evidence'][0]
KeyError: '1081152'
```

Measured against both snapshots:

| Snapshot | matches | `1083121` | `1081152` | `1082859` |
| --- | --- | --- | --- | --- |
| committed `data/latest.json` (08:06:51Z) | 92 | present | present | present |
| fresh capture (16:47:02Z) | 83 | **absent** | **absent** | present |

Both fixtures had started, and a started fixture leaves the board. Two unit
modules indexed those ids in the *live* snapshot, so advancing the board turned
a green suite red with nothing wrong in the code, the build or the fresh data.
Because the committed root is what visitors are served, every such failure
freezes publication — exactly the seven hours observed.

The count moves: 22 open rows, 22 of them priced by the ladder (exchange,
exchange-wide, bookmaker fallback, Valve VRS model, model mirror), so the
acceptance target of a pick and a probability for every open match is met by the
fresh snapshot itself. The gate, not the data, was the blocker.

## 5. Repairs in this session

1. **`scripts/core.py` — an exactly even accepted line no longer stops the
   ladder** (`1363318`). The even quote is retained as rejected evidence and the
   ladder continues to the model or a research tier.
2. **`scripts/summary.py` / `scripts/build.py`** — a no-edge row is a first-class
   state and every count on the page is derived from `partition()`, which refuses
   a board whose picks + no-edge + unresolved do not equal the open count.
3. **Fixture rotation is no longer a publication gate** (`tests/test_session_35c6e1e9.py`,
   `tests/test_session_e9be3e6b.py`). The pinned rows are read from the live
   board when present and otherwise from `research/harvest-ce45f672/snapshot.json`
   — the immutable capture they were published from — so the arithmetic
   assertions keep their subject after the fixture starts. If neither source
   carries the row, the test skips instead of failing the publish.
4. **`scripts/staged_gate.py` — the gate classifies, and fails closed.**
   `--check data` is `scripts.validate --data data/latest.json --site .` and is
   absolute. `--check units` runs the suite and, only if it fails, restores the
   pre-staging snapshot, replays **just the failing test targets** and publishes
   only when every one of them passes there. Anything else — an unparsable log,
   a target that still fails, a missing control snapshot — returns `3` and
   commits nothing.
5. **`pages.yml`** — `publish()` copies the pre-staging snapshot to
   `runtime/pre-staging-latest.json` *before* staging, runs the two
   `scripts.staged_gate` checks, and keeps `rc 3` fatal; the step stays
   `continue-on-error` so the verified artifact still deploys, and the follow-up
   step now publishes `runtime/staged-gate.json`.
6. **Contract tests re-pinned to the new gate** where they asserted the old
   literal lines (`test_session_a30d31a0`, `test_session_cecfe864`,
   `test_session_333b053a`, `test_session_071642e7`, `test_session_fe7f5de4`);
   each keeps its original intent (the gate must run before the commit and a
   failure must leave `main` untouched) and `test_session_572c65b7` adds the
   contract for the new behaviour.

## 6. Verification performed

| Gate | Result |
| --- | --- |
| `python -m unittest discover -s tests` | **1507 tests OK** (1 skipped) |
| `python -m unittest discover -s audits -p 'test_*.py'` | 9 tests OK |
| `python -m scripts.validate --data data/latest.json --site .` | 92 rows, 29 calculations, 15 pages, 858 links/assets, 20 checksums, 227 displayed rows |
| YAML parse + `bash -n` of all 25 step bodies in `pages.yml` | clean |
| Runner diagnostic `40112854117` | publish `true`, validate `rc 0`, c6 `rc 0`, 22/22 picks and probabilities |

**End-to-end replay of the real failure** (`_scratch/gate`, a copy of the tree
with the fresh 16:47Z snapshot built and staged):

| Scenario | Gate result |
| --- | --- |
| original (fixture-coupled) tests, fresh board | suite `FAILED (errors=2)` → gate **0** with 2 rotation warnings |
| fixed tests, fresh board | data **0**, units **0**, no warnings |
| add a test that fails on both boards | units **3**, naming the target |
| corrupt a staged page | data **3** |

## 7. Phone and executive-summary measurement

Measured with the repository's own headless Chromium on a build made from the
committed snapshot at its own clock (`--now 2026-10-24T08:30:00Z`, so picks are
visible rather than withheld), viewport heights 568 and 844:

| Viewport | Freshness strip | Quick-nav | **First pick card** | Bottom tab bar | Overflow |
| --- | --- | --- | --- | --- | --- |
| 320×568 | y = 113 | y = 290 | **y = 336** | y = 507 | none |
| 390×844 | y = 117 | y = 300 | **y = 360** | y = 783 | none |

The first card shows both teams' probabilities (`Spirit Academy 64.5%`,
`Lavked 35.5%`) and the pick label, above the fixed tab bar on both phones. The
index carries 19 in-site links to `picks.html`, and the executive summary
contains the dedicated section `id="unresolved-limits"` — *"Unresolved picks, and
why a pick can be missing"* — which renders even when nothing is unresolved and
lists the full fallback ladder with per-rung counts.

## 8. Sources

* Hotspawn lobby `https://play.hotspawn.com/lobby` and CS2 fixtures API — read on
  the runner; receipts in `research/session-572c65b7/diag/latest.json`
  (`fixture_sources[].url`, `sha256`, `observed_at`).
* Polymarket Gamma API — the even quote on `1079200` is retained in that
  snapshot's `attempts`.
* Valve standings / HLTV mirror use is unchanged by this session and remains
  documented on `sources.html#method`.
* GitHub Actions runs cited in §2, §3 and §4, and the archived capture
  `research/harvest-ce45f672/snapshot.json` used as the fixture control.

## 9. Flagged for review (also on the site's Flagged for Review page)

1. **The legacy-root step froze publication for seven hours** —
   `session-572c65b7-legacy-root-froze-publication-2026-10-24`.
2. **An exactly even line made the board unpublishable** —
   `session-572c65b7-even-line-blocked-the-contract-suite-2026-10-24`.
3. **The publication gate was written against the live board** — two modules
   indexed fixtures that start and leave the feed; the same class of coupling
   held publication for 17.7 h on 2026-10-23/24 per session 35c6e1e9's own
   docstring. Fixed here for these two, and no longer able to refuse a commit
   after `scripts/staged_gate` proves the coupling —
   `session-572c65b7-fixture-rotation-held-publication-2026-10-24`.
4. **Actions logs and artifacts are not readable from the authoring sandbox**
   (TLS reset on `productionresultssa*.blob.core.windows.net`; the HTML log view
   requires sign-in) — `session-572c65b7-actions-evidence-access-2026-10-24`.
5. **Fifteen or more sessions were dispatched against the same failure** —
   `session-572c65b7-parallel-sessions-duplicated-the-same-repair-2026-10-24`.
