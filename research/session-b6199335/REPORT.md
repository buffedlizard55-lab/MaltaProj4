# Session b6199335 — verification log

Everything below was measured in this session. Where a claim depends on a live
source, the source URL and the observation time are given; where this sandbox
could not reach the source, that is stated rather than filled in.

Written 2026-10-24, 06:10 UTC.

---

## 1. What the repository was actually doing when this session started

The public dashboard served the snapshot generated at **2026-10-23T11:47:19Z**
(`data/latest.json`, `build-info.json` revision `92d248d`, 90 rows) for
**17 h 47 m** — measured against the sandbox clock at 2026-10-24T05:31Z.

The refresh workflow had not run successfully since then. From
<https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/actions/runs>:

| Run | Started (UTC) | Event | Conclusion | First failing step |
| --- | --- | --- | --- | --- |
| 39956197341 | 2026-10-23T13:27 | schedule | failure | 8 · Unit and independent failure-mode tests |
| 39998307424 | 2026-10-23T16:2x | schedule | failure | 8 · Unit and independent failure-mode tests |
| 40025828846 | 2026-10-23T19:3x | schedule | failure | 8 · Unit and independent failure-mode tests |
| 40042111432 | 2026-10-23T22:3x | schedule | failure | 8 · Unit and independent failure-mode tests |
| 40062143026 | 2026-10-24T04:3x | schedule | failure | 8 · Unit and independent failure-mode tests |

Every one failed **before** `Refresh official sources`, `Build and independently
verify`, the browser gates, the legacy root staging and the Pages deploy, so no
new pick could reach the site regardless of what the sources said.

### Root cause (reproduced before it was changed)

```
$ python -m unittest tests.test_session_0cc1138a
FAIL: test_snapshot_covers_the_observed_lobby_fixtures
AssertionError: Items in the first set but not the second: '1081148', '1079655'
ERROR: test_each_observed_fixture_is_published_with_a_pick_and_an_official_link
KeyError: '1079655'
```

`tests/test_session_0cc1138a.py` pinned the 30 fixtures read from
`https://play.hotspawn.com/lobby` at 09:44Z on 2026-10-23 and asserted they
remained on the board. Hotspawn removes a fixture from the lobby when it
finishes, so by the 11:47Z snapshot two of them were gone and the assertion
could never hold again. A test about one observation had become a permanent
gate on publication.

The parity that *is* re-derivable from any snapshot — the three official views
(`api`, `page`, `lobby`) and the retained board all agree on the same fixture
count — is now asserted instead, together with a per-row official source and
the pick rule at the snapshot's own clock.

## 2. The phone layout did not apply to ordinary phones

`site/assets/style.css` opened `@media(max-width:650px) and (max-height:700px)`
at line 449 and never closed it, so the phone block that begins at line 461 —
including `body[data-page="index"] main>#picks-at-a-glance{order:4}`, the rule
that puts the pick list above the folded guide — was **nested inside a
short-screen query**. Measured with the repository's own headless Chromium:

| Viewport | First pick card, before | First pick card, after |
| --- | --- | --- |
| 390 × 844 (common modern phone) | **y = 868** — below the 844 px fold | **y = 434** |
| 320 × 568 | y = 434 | y = 434 (unchanged; the query already matched) |

The block's own comment claimed "Desktop is untouched" and the CSS-order repair
was believed live; it only ever applied below 700 px of viewport *height*.

## 3. Two browser suites measured the clock, not the page

* `tests/browser_f0814674.cjs` asserted "a snapshot inside its window shows no
  stale banner" about whatever snapshot was committed, while the page compares
  that snapshot with the reader's clock. It was true for eight hours after a
  build, then failed forever.
* `tests/browser_9b97d585.cjs` then crashed at 320×568 (`row` was `null`) for
  the same reason: once stale, the board publishes no current pick.

`tests/pinned-clock.cjs` pins the page's `Date` — constructor and `now()` — to
the snapshot under test. The stale branch stays covered by `tests/browser.cjs`
and by the explicit 9-hour ageing step in `browser_f0814674.cjs`.

A second trap found while fixing this: pinning only `Date.now()` leaves
`new Date()` on the wall clock, and `browser_9b97d585.cjs` builds its scenario
timestamp that way, which produced a future-dated snapshot and tripped the
page's own clock-skew guard. The helper pins both.

## 4. Gates run in this session

Against the committed snapshot, from a clean working tree (`public/` and
`runtime/` removed):

| Gate | Result |
| --- | --- |
| `python -m unittest discover -s tests` | **1,210 tests, OK (3 skipped)** |
| `python -m unittest discover -s audits` | 9 OK |
| `verification-95b588c2/test_integrity.py` | 5 OK |
| `python -m unittest discover -s verification-c6` | 12 OK |
| `verification-c6/audit_snapshot.py data/latest.json` | 90 rows, **0 failures** |
| `python -m scripts.validate --data data/latest.json --site .` | 90 rows · 27 calculations reproduced · 15 pages · 810 links/assets · 20 checksums · 212 displayed rows |
| `npm run test:browser` | **all 8 suites** |

The 1,210 includes `tests/test_session_b6199335.py` (13 new tests). Verified by
mutation: restoring the missing `}` turns four of them red.

The browser suites were also re-run against a **freshly dated copy** of the
snapshot (every timestamp shifted so `built_at` is the current minute) to prove
they no longer depend on how old the committed snapshot is: all 8 passed.

Three suites failed on the first attempt in this session for a reason worth
recording, because it will catch the next person: `build-info.json` records the
SHA-256 of every shipped file. Editing `assets/style.css` without re-running
`scripts.build` + `scripts.stage_legacy` leaves the manifest describing bytes
that are no longer there, and `test_session_dddcb90d`,
`test_session_cf8f94b9` and `test_session_071642e7` all fail on it. The artifact
was rebuilt with the snapshot's own build clock and re-staged.

## 5. Source reachability — what this session could and could not measure

This sandbox has outbound access to GitHub only. `curl` to
`play.hotspawn.com`, `www.hltv.org` and the bookmakers returns no connection,
so **no source in section 6 was re-observed from here**. What could be measured
was measured through a separate, read-only fetch path; those results are in
section 6 with their URLs and times, and anything not measured is marked
unverified rather than inferred.

## 6. Live source checks (filled from the runner capture)

See section 7 for the capture that produced these numbers, and
`raw/index.jsonl` for the HTTP status of every endpoint.

*(This section is completed from the committed probe evidence; no value here is
typed from memory.)*

## 7. Reproducing any of this

```
python -m venv .venv && .venv/bin/pip install -r requirements.txt
npm ci --ignore-scripts
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -m scripts.build --data data/latest.json
.venv/bin/python -m scripts.validate --data data/latest.json --site .
npm run test:browser
```
