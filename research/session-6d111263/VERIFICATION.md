# Session 6d111263 — line-by-line verification receipt

Date: 2026-10-25 (UTC). Branch `arena/6d111263-maltaproj4`. All numbers below are read from
committed artifacts or run outputs, never assumed. Blank means unverified; nothing is inferred.

## 1. Starting state (measured before any edit)

| Fact | Value | Source |
| --- | --- | --- |
| `main` at claim | `6ade440` | `git rev-parse origin/main` |
| Committed snapshot | `2026-10-25T01:47:42.430039Z`, 79 rows, 18 open / 18 picks / 18 probabilities / 0 unresolved | `data/latest.json` |
| Snapshot age at claim | 11.6 h — outside the 8-hour evidence window | computed from `generated_at` |
| Public site at 13:26Z | `build-info.json` revision `cbe9dce`, built `01:47:42Z`, 79 rows; summary read `14 open · 0 with a pick · 14 unresolved` with the expiry banner | `https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json`, `.../index.html` (fetched live) |
| Publisher runs red | 40143667147 (23:40Z), 40170923727 (06:56Z), 40193317196 (12:29Z) — all failed at *Build and independently verify every row, calculation and internal link*; 40151731896 (01:43Z) was the last success | GitHub Actions run pages (links in `data/review-notes.json` note `session-6d111263-publisher-alias-freeze-2026-10-25`) |

## 2. Diagnosis (reproduced, not inferred)

The authoring sandbox has no egress to Hotspawn/HLTV/Polymarket and no access to the Actions
log hosts, so the exact failing step was replayed on GitHub egress by the session harvest
(workflow `.github/workflows/harvest-6d111263.yml`, run
[40197851926](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40197851926)):

| Step (identical to `pages.yml`) | Outcome |
| --- | --- |
| refresh official sources | success |
| quarantine | success |
| independent row audit (`verification-c6/audit_snapshot.py`) | success |
| `scripts.build` | success |
| `scripts.validate` | **failure** — `AssertionError: Model roster has no HLTV source on this row` |
| independent row audit of built artifact | success |
| coverage census | 78 rows, 17 open, 17 picks, 17 probabilities, 0 unresolved, 0 expired |

Receipts committed under `research/harvest-6d111263/` (logs `01`–`11`, `rcs.json`, `snapshot.json`).

Failing row (probe: `validate_model_row` per open model row):

| Field | Value | Source |
| --- | --- | --- |
| Fixture | `1086697` — Projeto do KinGui vs Yawara, CCT 2026 South America Series 7 | Hotspawn fixtures API + `play.hotspawn.com/cs2-pickems` (`fixture_sources` in the receipt snapshot) |
| Method | `model_vrs` (originated line: Valve standings 854 vs 845 points → 51.0% / 49.0%, pick Projeto do KinGui) | `evidence[0]` in the receipt snapshot; Valve file `standings_global_2026_10_05.md` @ `eec4853` |
| HLTV page | `https://www.hltv.org/matches/2399918/tropa-do-kingui-vs-yawara-cct-2026-south-america-series-7` labels the club **Tropa do KinGui** | `hltv_context.source` in the receipt snapshot |
| Identity register | `data/identities.json` already pairs `Tropa do KinGui` / `Projeto do KinGui` / `ex-Keyd Stars` with source `.../matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7` | the identity entry itself |
| Defect | `lineup_source_ok` compared HLTV headings to fixture labels with `plain_name` equality only, so the registered alias was refused; the assertion killed `scripts.validate` and with it every scheduled publish | `research/harvest-6d111263/logs/05-validate.log` |

## 3. Resolution

While this session's diagnosis was in flight, session b85ad9b4 landed the equivalent repair on
`main` (PR [#316](https://github.com/buffedlizard55-lab/MaltaProj4/pull/316),
`scripts/validate.py same_club()`). Per the coordination protocol this session **adopted that
implementation instead of layering a second one** (merge of `origin/main` into this branch,
conflicts resolved in favour of upstream for `scripts/validate.py`; both sessions' review notes
and both coordination claims retained). This session's independent contribution kept:

- the reproduction receipts above (independent of the other session's replay),
- `tests/test_session_6d111263.py` — 13 tests: exact/alias/source-less/unregistered label
  handling, the self-colliding-fixture guard, all three lineup-source branches, and an incident
  replay that validates the exact rejected snapshot **and** proves the same row fails when the
  identity register is removed.

## 4. Gates re-run on the merged tree (this session, 2026-10-25)

| Gate | Result |
| --- | --- |
| `python -m unittest discover -s tests` | OK — 1,632 tests, 7 skipped (includes the 13 above) |
| `python -m unittest discover -s audits -p 'test_*.py'` | OK — 9 |
| `python verification-95b588c2/test_integrity.py` | OK — 5 |
| `python -m unittest discover -s verification-c6 -p 'test_*.py'` | OK — 12 |
| `python -m scripts.validate --data data/latest.json --site .` | 79 rows / 18 calculations / 15 pages / 751 links / 20 checksums / 186 displayed rows |
| `python -m scripts.validate --data research/harvest-6d111263/snapshot.json` | 78 rows / 17 calculations / 15 pages / 802 links / 20 checksums / 198 displayed rows (the exact data the publisher rejected) |
| `node tests/browser.cjs` (first Chromium suite, local) | 32 accessibility/overflow scans pass at 320/390/768/1440 |

The full 13-suite `npm run test:browser` and the fresh runner capture/staging receipts are
recorded in the completion section of `COORDINATION.md`.

## 5. Line-by-line row verification rules applied

Every published row must satisfy (checked by three independent layers: `scripts.validate`,
`verification-c6/audit_snapshot.py`, and the row audits in `audits/`): a row's probabilities are
recomputed from its stored receipt, the pick equals the larger probability, every evidence URL is
an https URL on the official source it claims, observations are inside the 8-hour window at
publication time, and rendered counts equal the data. A value that cannot be confirmed from an
official source stays blank and the row is withheld or moved to the unresolved section with its
limitation — nothing is inferred. Hotspawn supplies fixture inventory and locks only, never a
probability.

## Completion — 2026-10-25 16:34–17:05 UTC

**Delivery:** PR [#335](https://github.com/buffedlizard55-lab/MaltaProj4/pull/335) **merged to `main` at
2026-10-25T16:34:10Z**, merge commit `7e48c86be28cf35721c7892109c8b22b88963d63`, without waiting for approval.
Head at merge: `b2945d94`. PR checks on that head: `verify-build` **pass 3m59s** (run 40211524304),
`audit` **pass 31s** (run 40211524287), `deploy`/`capture` skipped by design for PRs.

**Post-merge gates, run locally on `main`'s exact tree (`36fa6d17`):**

| Gate | Result |
| --- | --- |
| `unittest discover -s tests` | **1,778 OK** (14 skipped) |
| `unittest discover -s audits` / `verification-95b588c2` / `verification-c6` | OK / OK / OK |
| `scripts.validate --data data/latest.json --site .` | 75 rows · 14 calculations · 15 pages · 711 links · 20 checksums · 172 displayed rows |
| `npm run test:browser` (all 13 Chromium suites) | **rc=0** (11 suites print `Passed:` receipts; board totals 14 open rows) |

**Publisher runs after the merge (all green):**
- `40212306911` — push run of my merge `7e48c86b`: **success 21m18s**, including the staging step, which
  committed root `36fa6d17` "Publish the verified build to the legacy main:/ root fallback" (root data
  `2026-10-25T16:50:26Z`, 14 open / 14 with a pick / 14 with a probability / 0 unresolved).
- `40213100898` — next scheduled slot: **success 11m55s**.
- The three failures immediately before the merge (`40208959787`, `40210487483`, `40210749388`, all at the
  staging step "The staged root failed its own validator or unit gate") ran trees that predate session
  85087497's `b1465df6` re-anchoring of `tests/test_session_9fca16ca.py` to its retained ledger; the fix is on
  `main`, and the two runs after it are green.

**Live-site verification (`fetch_page`, ~16:52 UTC):** `build-info.json` revision `a6d7bb4a`, built
`2026-10-25T16:39:32Z` from snapshot `16:39:31Z`, 75 rows; index shows "Last checked 25 Oct 2026 · 16:39 UTC ·
13m ago", "Snapshot inside its 8-hour evidence window", **14 open · 14 with a pick · 14 with a win
probability · 0 unresolved**, all executive-summary in-site links (`picks.html`, `#picks-at-a-glance`,
`unresolved.html`, `review.html`, `matches.html`, `sources.html#method`, per-pick `evidence.html#match-…`
anchors), the method split "10 from betting markets · 4 from our own VRS model line", and the standing
"Hotspawn's crowd percentages are never used". The committed root (what the legacy Pages source serves)
advanced again at 16:53Z to `36fa6d17`.

**Adopted (never layered):** upstream `same_club()` (PR #316) for the publisher freeze; session 9fca16ca's
short-phone compaction (PR #337) for the 320x568 tab-bar overlap — this session's measured equivalent was
deleted after main merged first, and both stylesheet copies are byte-identical to `main` again (residue-free).
The flagged notes `session-6d111263-publisher-alias-freeze-2026-10-25` and
`session-6d111263-phone-tabbar-overlap-2026-10-25` carry the full disclosures on the Flagged for Review page.

**Irregularities carried forward (non-blocking):** PR `pull_request` check runs silently stopped being
created while the PR was `dirty` (close/reopen re-fired them); `gh run cancel` 403s for this token and gh
REST rate limits fluctuate; harvest captures never landed (40199443431 failed with unreachable logs; queued
runs 40200829452/40202743862 were uncancellable and may still fire); hand-staging must never copy
`scripts.build`'s clock-withheld `public/data/latest.json` over the committed snapshot on a branch (build
deep-copies and withholds per reader clock at `build.py:1733` — the pipeline stages it deliberately, a
diagnostic session must not); the adopted phone fix leaves a measured 2px margin at 320x568 for the current
long-named first card (a three-line heading would need a content-independent fix); GitHub Pages legacy
`main:/` builds are soft-limited to 10/hour, so the served site can lag a green run by several minutes.
