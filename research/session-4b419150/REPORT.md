# Session `4b419150` — restore the 4–8 h refresh, re-verify every fallback source

Branch `arena/4b419150-maltaproj4` (this session) · work 2026-10-24, 05:27–06:0xZ

The board was **already complete as a product**: the committed `data/latest.json`
(2026-10-23T11:47:19Z) carried 90 feed rows, 27 open, **27 picks, 27 win
probabilities, 0 unresolved**, each sourced outside Hotspawn, and the mobile
layout/executive-summary/unresolved sections were covered by passing browser
suites. The failure this session had to close was **not** a missing pick — it was
that the published snapshot was 17+ hours old and the **refresh pipeline that
keeps it current had stopped**, together with a fresh, independent re-verification
of the sources used to price matches that the featured market cannot resolve.

---

## 1. Measured defect: every scheduled refresh was failing (line-by-line)

* Public `https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json` read
  live at 2026-10-24T05:38Z: `revision 92d248d2…`, `built_at
  2026-10-23T11:47:19Z`, 90 rows — i.e. the **same 17-hour-old snapshot** as the
  committed baseline, well past the site's own `stale_after_hours: 8`. Its picks
  are correctly withheld client-side; the *data* never advanced.
* `gh run list` showed the five most recent `Verify, refresh and publish CS2
  Scout` **schedule** runs on `main` in state `failure` (`40062143026`,
  `40042111432`, `40025828846`, `39998307424`, `39956197341`), while the paired
  `CS2 refresh watchdog` runs were green. Step-level conclusions read through
  the Actions jobs API: each failing run's `verify-build` job failed at the step
  **"Unit and independent failure-mode tests"**; `deploy` was `skipped`.
* Local reproduction (`python -m unittest discover -s tests`, 1195 tests): exactly
  **1 failure + 1 error**, both in
  `tests/test_session_0cc1138a.py::LiveHotspawnCoverage` —
  `KeyError: '1079655'` and `AssertionError … '1079655','1081148': lobby fixture
  missing from the board`. That class pinned a frozen lobby observation
  (2026-10-23 09:44Z, 30 IDs) against the ever-changing `data/latest.json`.
  Hotspawn rotated `1079655` and `1081148` out of the feed within hours; the
  11:47Z snapshot's own `inventory_changes.removed_ids` is `[]` (it compared
  against 11:25Z, by which time both were already gone), so the "removed" excuse
  no longer applied. Because that test step runs **before** `scripts.refresh` and
  gates the entire `verify-build` job, the stale-data condition was self-sustaining.

This directly explains the user's "site regularly check for updates every 4–8
hours" failure. It is fixed below, and the fix is bound so it cannot recur.

## 2. Fix: bind coverage on every build from the snapshot's own sourced record

`tests/test_session_0cc1138a.py::LiveHotspawnCoverage` was repaired **without
weakening intent**:

* `test_three_view_parity_is_recorded_on_every_build` — asserts, on **every**
  build, the snapshot's own `coverage`/`coverage_counts` three-view parity record
  produced by `scripts/inventory.py` from the official scoped API, the CS2 pick'em
  page and the general lobby. `verified` requires `api == page == lobby ==
  retained`; `partial` must carry a documented issue/fixture-conflict; every row
  must carry an official Hotspawn source. This is *stronger* than a frozen id list
  because it binds to whatever Hotspawn actually lists at build time.
* `test_every_open_row_has_a_pick_and_provenance_or_an_honest_limit` — a
  clock-aware per-row contract on every still-open row: a priced pick must name a
  fixture team and carry an `https` external price source; a research-only pick
  (HLTV form / Valve-VRS single) must carry external research context; a row with
  no pick must carry a documented limitation; a past lock correctly withholds the
  pick (the original frozen-pin bug). It was hardened to accept research tiers
  (verified against a synthetic fresh snapshot carrying a `research_form` row).
* `test_the_repaired_gate_still_rejects_a_silent_omission` — a negative test
  proving the gate still flags a priced pick with no source and a blank open row
  with no limitation. The frozen 09:44Z observation is retained and verified as a
  historical artifact against `research/session-0cc1138a/REPORT.md`.

Gates re-run locally after the fix (see §5): 1195 unit tests green, audits 9,
integrity 5, C6 12, `scripts.validate` 90 rows / 27 reproduced probabilities /
810 links / 20 checksums, and 7 of 8 browser suites pass locally — the 8th
(`browser_f0814674`) asserts the served snapshot is fresh, which is only true in
CI *after* the source refresh (§4). Its local failure on the stale snapshot is the
expected symptom, not a code defect.

## 3. "Own research" — resolving matches the featured market cannot price

The user asked to look for information sources to guide picks for matches the
featured (Polymarket exchange) tier cannot resolve — **HLTV first, then
esportsbooks / betting lines**. All reads below were taken on 2026-10-24 and are
independent of the pipeline:

| Tier the board uses | Fixture | Independent 2026-10-24 read | Result |
| --- | --- | --- | --- |
| `bookmaker_fallback` | `1082859` NEXVOID vs Alter Ego (DFRAG Invitational, starts 2026-10-26 03:00Z) | [BO3.gg match page](https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026) shows Thunderpick **1.60 / 2.17** ("view all markets"), NEXVOID 69% monthly winrate + 3-match streak, Alter Ego 0% H2H and lower rank (155 vs 113). [EGamersWorld listing](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/nexvoid-vs-alter-ego-HfdcJeXmT) corroborates the match (NEXVOID 1.8, 3-win streak vs 3-loss). | The committed evidence is `odds [1.6, 2.17]` → `57.56% / 42.44%` pick NEXVOID. The live read reproduces it **exactly** — no drift, de-vig is `1/1.6 : 1/2.17 = 0.625 : 0.4608 → 0.5756 : 0.4244`. |
| `model_vrs` | `1082996` Acend vs UNiTY (NODWIN Clutch Series 13) | [HLTV match page](https://www.hltv.org/matches/2399112/acend-vs-unity-nodwin-clutch-series-13) reachable; its *community* "pick a winner" reads Acend 16.7% / UNiTY 83.3% — a crowd vote the site **never uses as a probability**. [HLTV Valve ranking 2026-10-24](https://www.hltv.org/valve-ranking/teams/2026/october/24) live. | The board originates its own line from Valve's official standings file (see §3.1), correctly ignoring the crowd vote. |
| fixture inventory | all events | [HLTV matches](https://www.hltv.org/matches) lists the exact events the feed carries: PGL Masters Bucharest 2026 (Oct 24–31), NODWIN Clutch Series 13 (Oct 14–27), DFRAG Invitational 2026 (Oct 26–Nov 1), RLG Tesla Cup 2026 (Oct 27–29), GLuck Moscow Cyber Games 2026 (Oct 31–Nov 1). | HLTV and the Hotspawn scoped API agree the upcoming slate is real and current. |
| `bookmaker_fallback` corroboration | `1082860` FlyQuest vs Staqued | [EGamersWorld](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3) (from the 09:44Z receipt) and BO3.gg DFRAG markets. | A second non-exchange line source for a low-tier fixture. |

**Kalshi** was re-checked as an additional keyless exchange (as in earlier
sessions): the search surfaced only a *settled* Aug 2026 NEXVOID–Alter Ego market
(`kxcs2game-26aug…`, payout Aug 24, 2026), not a live line for these fixtures —
so it cannot price an upcoming match and is not used. Commercial odds APIs remain
keyed/paid and are not adoptable in the keyless Actions pipeline. Thunderpick and
GG.BET direct access stays recorded, never bypassed.

### 3.1 Dated-model limitation (flagged, non-blocking)

The `model_vrs` line for `1082996` (Acend 53.35% / UNiTY 46.65%) is derived from
Valve's official `standings_global_2026_10_05.md` (Acend rank 63, **1197 pts** vs
UNiTY rank 69, **1167 pts**), reproduced with Valve's published Glicko/calibration
(RD 75, slope 0.7986). On 2026-10-24 HLTV's live Valve ranking shows **UNiTY #61
ahead of Acend #75** — the monthly official file lags live form. I verified via
the GitHub contents API that `standings_global_2026_10_05.md` is **still the
newest** file in `ValveSoftware/counter-strike_regional_standings/live/2026`
(others: 09_07, 08_03, …), so the model is correctly using the latest *official*
file; `MAX_STANDINGS_AGE_DAYS = 62` tolerates the 19-day age. This divergence is a
genuine, disclosed source-cadence limitation and is published on the Flagged for
Review page — it is never a silent fill and no value was invented.

## 4. Restoring the live data

Local `curl` to the source hosts is blocked by the sandbox (SSL_ERROR_SYSCALL),
so a faithful `scripts.refresh` cannot run inside this workspace; the project's
own design runs refresh on the GitHub Actions runner, which has source access.
The fix in §2 makes that runner's unit gate green. This session triggers a
`workflow_dispatch` of `pages.yml` on the branch as a **pre-flight** (it performs
the real source refresh, quarantine, independent row audit, build, validation and
all browser suites with a fresh snapshot), then the verified snapshot is merged to
`main`, whose push performs the production refresh and deploy. The live Pages bytes
are verified against the exact manifest afterwards. (See COORDINATION.md receipt.)

## 5. Verification performed

* `python -m unittest discover -s tests` — **1195 run, OK** (3 skipped) after the
  fix; the pre-fix reproduction failed with the exact `KeyError`/parity error.
* `audits` (9), `verification-95b588c2` (5), `verification-c6` (12) — all OK.
* `scripts.coverage_contract.inspect(data/latest.json)` — **0 problems**.
* `scripts.validate --data data/latest.json --site .` — 90 rows, 27 calculations
  reproduced, 15 pages, 810 internal links/assets, 20 checksums, 212 displayed
  rows.
* Local `scripts.build --data data/latest.json --out public --now
  2026-10-23T11:47:19Z` reproduces the committed build; validate on `public/`
  passes. `npm run test:browser`: 7/8 suites green; the 8th
  (`browser_f0814674`, "fresh snapshot shows no stale banner") fails **only**
  because the served snapshot is 17 h stale relative to the browser's real clock —
  the exact condition the CI source refresh removes.

Every probability and pick above traces to an external official source with a link;
no Hotspawn crowd percentage is used as a probability; no value was inferred or
filled in.
