# Session ec033870 — sourced values for every past (locked) fixture on the board

## Task and acceptance criteria

Hotspawn's CS2 board carries rows whose `lock_time` and `start_time` are already in the
past. The existing ladder prices a row only while it is open (`scripts/vrs.py` `apply()`
and `research_single()` both early-return when `state != 'open'`), so on the
`2026-10-24T08:06:51Z` baseline **63 of 92 rows published no pick, no percentage and no
odds at all**. The brief requires picks for every match on the board, with a separate
section for the rows that cannot be resolved, that section referenced from the executive
summary, every value traceable to an official source, and nothing inferred.

Standing source policy held: Hotspawn crowd percentages are never a probability input;
probabilities come only from external market lines or from this project's own originated
line built on Valve's official standings; a value that cannot be confirmed from an
official source is left blank and flagged.

## What was built

1. **`scripts/vrs_history.py`** — fetches, vendors and verifies Valve's official monthly
   global standings, and selects the file that was current for a given fixture start.
   `load()` raises on any SHA-256 mismatch, so a corrupted or tampered copy cannot price a
   row. Index: `data/vrs/history.json`; bytes: `data/vrs/history/`.
2. **`scripts/historical.py`** — a separate four-rung ladder that writes a `historical`
   block per locked row. It deliberately does **not** touch `pick`, `probabilities`,
   `fair_odds` or `method`, because `audits/audit_9b97d585.py:73-90` and
   `audits/audit_cecfe864.py:259-273` correctly forbid a `not_open` row from carrying a
   live pick. The historical block also carries `not_a_current_pick: true`.
   Tiers, in order: `model_vrs` → `research_vrs_single` → `research_vrs_invariant` →
   `unresolved`.
3. **`scripts/build.py`** — renders the historical block as `.hist-pick` / `.hist-prob` /
   `.hist-prob-pair` / `.hist-blank` (never `.pick-cell .pick` or `.prob-pair`, which
   `scripts/validate.py` reserves for live, expiring rows), a `Past fixtures` section
   anchored `#past-picks`, and a separate `#past-unresolved` section. The executive
   summary links to both.
4. **`scripts/validate.py`** — `validate_historical()` re-derives every historical block
   from the vendored standings bytes and the published Valve formula, independently of the
   collector, and checks it against what the site displays.

## Measured result on the `2026-10-24T08:06:51Z` baseline

92 rows · 29 open · 63 locked. All 63 locked rows now carry a sourced value.

| Tier | Rows | What is published |
| --- | --- | --- |
| `model_vrs` | 25 | pick **and** both win probabilities, from Valve points |
| `research_vrs_single` | 21 | pick only — exactly one of the two teams is in the standings |
| `research_vrs_invariant` | 8 | pick only — a repeated label, but every candidate roster gives the same favourite |
| `unresolved` | 9 | nothing; blank and flagged, never 50/50 |
| **resolved** | **54 of 63 = 85.7 %** | |

Standings file used per row (selected by the row's own sourced `start`):
`standings_global_2026_06_01.md` × 58, `standings_global_2026_07_06.md` × 1,
`standings_global_2026_10_05.md` × 4.

Pricing all 63 rows from the *current* file instead would resolve only 42, because the
October file repeats 12 labels that the June file lists once. That measurement is the
reason dated selection exists.

`scripts.validate --data data/latest.json --site .` reports
`historical_rows_present 63, historical_rows_reproduced 63,
historical_probabilities_reproduced 25, historical_unresolved 9, historical_coverage_pct
85.7`.

## Official sources

Valve's own repository is the sole price input. Ten monthly global standings files were
downloaded from the pinned commits and vendored unmodified; every one is re-fetched and
hash-checked by `vrs_history.load()`.

| As of | Teams | Commit | File |
| --- | --- | --- | --- |
| 2026-01-05 | 295 | `0b2154eacafe50abd2ec251ed78d460d8f833088` | `standings_global_2026_01_05.md` |
| 2026-02-02 | 310 | `73c71008fb39` | `standings_global_2026_02_02.md` |
| 2026-03-02 | 334 | `3404a877b6ca` | `standings_global_2026_03_02.md` |
| 2026-04-06 | 357 | `3c32325b3f52` | `standings_global_2026_04_06.md` |
| 2026-05-04 | 356 | `aac2074bc10f` | `standings_global_2026_05_04.md` |
| 2026-06-01 | 364 | `510968f54723dcb698ad3b04d396140fc263c239` | `standings_global_2026_06_01.md` |
| 2026-07-06 | 378 | `050a38d71d4f5f07d2618bb8bedd54268b93bddf` | `standings_global_2026_07_06.md` |
| 2026-08-03 | 396 | `467b9d2e0e4b` | `standings_global_2026_08_03.md` |
| 2026-09-07 | 401 | `84ccfa4d751f` | `standings_global_2026_09_07.md` |
| 2026-10-05 | 380 | `eec4853d7bcf0f1f7efe7f0d901234bef7e98b75` | `standings_global_2026_10_05.md` |

Directory listing: <https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/2026>
Human-readable mirror of the same official ranking (HLTV states "This is an official Valve
ranking"): <https://www.hltv.org/valve-ranking/teams/2026/october/05>

Per-row evidence carries the fixture's team names, the resolved Valve rows, points,
placements, both five-player rosters, the raw file URL and the per-team detail-page URLs,
e.g. `…/details/2026_06_01/0186--fortress--as_k-bqrebedre-brand-bukki-grennie.md`.

## Irregularities found

### 1. Disambiguating a repeated Valve label with today's HLTV roster picks the wrong team

This is the most consequential finding and it reversed an obvious shortcut. Valve's
`2026-10-05` file lists **Johnny Speeds twice**: #99 (bsover / draken / hampus / Rack /
Svedjehed, 1049 points) and #164 (HEAP / jocab / Lekr0 / nawwk / titulus, 802 points).
Today's HLTV team page shows the #99 five:
<https://www.hltv.org/team/12604/johnny-speeds>.

Valve's `2026-06-01` file (commit `510968f5…`) lists Johnny Speeds **once, at #75**, with
HEAP / jocab / Lekr0 / nawwk / titulus and 1138 points — i.e. the roster that actually
played the June fixtures `1053068` (2026-06-26) and `1053071` (2026-06-27).

An anchor built from today's HLTV lineup is therefore **89 places and 367 points off** the
team that played. HLTV's own roster timeline confirms the switch: draken 2026-07-10, hampus
2026-07-11, Rack and bsover 2026-08-22, Svedjehed 2026-09-01, so the current five did not
exist in June. Corroborating HLTV news:
[/news/44738/short-news-week-22](https://www.hltv.org/news/44738/short-news-week-22)
(2026-06-07, lists jocab / nawwk / Lekr0 / titulus / HEAP),
[/news/45081/johnny-speeds-bench-friberg-nawwk-and-lekr0](https://www.hltv.org/news/45081/johnny-speeds-bench-friberg-nawwk-and-lekr0)
(2026-07-07),
[/news/45116/hampus-returns-on-johnny-speeds](https://www.hltv.org/news/45116/hampus-returns-on-johnny-speeds)
(2026-07-11),
[/news/45210/johnny-speeds-and-heap-part-ways](https://www.hltv.org/news/45210/johnny-speeds-and-heap-part-ways)
(2026-07-31).

Recorded as review note
`session-ec033870-current-roster-anchor-would-pick-the-wrong-valve-row-2026-10-24`.

### 2. Nine rows genuinely cannot be priced, and two would flip

Left blank and flagged, with the reason per team:

| Fixture | Match | Start | Why |
| --- | --- | --- | --- |
| 1051339 | Acend vs Infinite | 2026-06-26 12:00Z | Infinite's label appears twice; favourite **flips** 0.424 → 0.874 across the two Infinite rosters |
| 1052700 | GameHunters vs VEXA | 2026-06-27 16:00Z | GameHunters twice; flips 0.636 → 0.460 |
| 1052599 | Mai Tai vs Megoshort | 2026-06-27 14:00Z | Mai Tai absent from the June file; Megoshort listed twice |
| 1053069 | roamsfiest vs train launcher | 2026-06-26 16:45Z | neither club in the Valve standings |
| 1053072 | train launcher vs roamsfiest | 2026-06-27 14:10Z | neither club in the Valve standings |
| 1053436 | Aimhaus vs Coalesce | 2026-06-28 13:00Z | neither club in the Valve standings |
| 1053469 | BERG vs SINQU REHTI | 2026-06-28 16:00Z | neither club in the Valve standings |
| 1053470 | 6666 vs SINQU REHTI | 2026-06-28 17:00Z | neither club in the Valve standings |
| 1053442 | 6666 vs BERG | 2026-06-28 18:00Z | neither club in the Valve standings |

The last six are Svenska CS-Ligan and Urban Riga Open #5 clubs sitting below the ranking
floor. HLTV team pages exist for some, but HLTV publishes no pre-match probability and no
bookmaker line was found for any of them, so nothing was inferred.

### 3. Eight rows are safe despite a repeated label

For these, every candidate roster for the repeated label produces the same favourite, so
the pick does not depend on which club played: 1052748 Inner Circle Academy over sAw ·
1051801 Bounty Hunters over UNO MILLE · 1052185 Entropy over sAw · 1052698 ex-KRÜ over
MAGICOS · 1052186 Lilmix over Subtop De France · 1051804 Fluxo over UNO MILLE · 1055478
Lavked over illwill · 1079193 FOKUS over ex-6666. No percentage is published for any of
them, because one input of the two-team formula is still unknown.

### 4. Duplicate labels in `2026-10-05` (380 teams)

Johnny Speeds #99/#164 · Misa #134/#290 · Just Players #118/#347 · Mai Tai #240/#296 ·
BIG Academy #280/#311 · UNO MILLE #186/#266 · Honvéd #169/#331 · Leo #112/#340 ·
Lilmix #167/#244 · 6666 / ex-6666 #127/#368 · METANOIA Wolves #235/#339.
Absent from that file: Sharks, ex-Tricked, ReThink, Wampirki, GAMEHARMONY, SINQU REHTI.
Any future row touching these labels needs the invariant test, not a blind match.

## Two pre-existing defects in the browser suite, found and fixed

Neither was caused by this change: `git diff --stat 45fc6ba HEAD -- assets/app.js
site/assets/app.js` is empty. Both reproduce byte-identically on unmodified `main`,
verified by building `45fc6ba` in a separate worktree and running the same suite against
it. They are the same class of defect — a test that assumes the committed snapshot is
fresh, while `.github/workflows/pages.yml` refreshes only on `main`, so every pull request
runs the suite against an ageing baseline.

1. **`tests/browser_9b97d585.cjs:112`** — `data.matches.find(m => m.state === 'open')`
   takes the first *open* row, but `app.js` hides rows whose lock has passed at the
   reader's clock. At 16:58Z against the 08:06:51Z baseline, `picks.html` had 29 rows but
   only 20 visible, and the chosen row `1079659` (Spirit Academy vs Lavked, locked 10:54Z)
   was already hidden, so the filter matched 0 rows. The check now derives its target and
   its expected counts from `tr[data-match]:visible` itself, and when nothing is live it
   asserts the snapshot is at least eight hours old and reports the case as not
   applicable — the escape hatch the withheld-pick branch of the same file already used.
2. **`tests/browser_ce45f672.cjs:90`** — `a win probability is hidden behind the tab bar`
   fired on **placeholder text**. `app.js` keeps the `.glance-card-score` elements when it
   withholds a card and rewrites them to "Withheld" / "Expired · pick withheld", so
   counting them cannot distinguish a live card from a withheld one, and the suite then
   asserted the geometry of two rows of text that are not win probabilities at all.
   Detection is now content-based; a withheld card is asserted to say so, and the
   snapshot-age guard proves the case only applies to an aged baseline. The board
   assertions were split into the two halves that are actually true at any clock: every
   open row is in the DOM, and no row past its lock is still visible (20 of 29 at 17:00Z).

Both files belong to other sessions' scopes, so the edits are logged in `COORDINATION.md`.

## Verification receipts (all executed on this tree)

- `.venv/bin/python -m unittest discover -s tests` → **Ran 1503 tests, OK (skipped=1)**
  (baseline before this work: 1484).
- `.venv/bin/python -m unittest discover -s audits` → **9 OK**
- `.venv/bin/python verification-95b588c2/test_integrity.py` → **5 OK**
- `.venv/bin/python -m unittest discover -s verification-c6` → **12 OK**
- `.venv/bin/python verification-c6/audit_snapshot.py data/latest.json --output
  runtime/independent-row-audit.md` → **0 failures**
- `.venv/bin/python -m scripts.coverage_contract --snapshot data/latest.json` →
  `problems: []`
- `.venv/bin/python -m scripts.build --data data/latest.json --now 2026-10-24T08:06:51Z`
  → `92 sourced rows, 29 with percentages, 0 without, 0 unresolved`;
  `.venv/bin/python -m scripts.stage_legacy` → `Staged verified static root fallback (22 files)`
- `.venv/bin/python -m scripts.validate --data data/latest.json --site .` → **PASS**,
  `rows 92, probabilities 29, pages 15, links 888, checksums 20, displayed rows 227,
  historical 63/63/25/9, coverage 85.7`
- `npm run test:browser` → **exit 0, 11 of 11 suites passed**

New regression coverage: `tests/test_session_ec033870.py` (19 tests) — dated standings
selection, the historical ladder including 8 corruption cases that must raise, and the
rendered site.

## Public review record

Three notes were **appended** to `data/review-notes.json` (229 → 232, ids verified unique;
appended rather than edited so the existing literal-date assertions stay valid):

- `session-ec033870-past-fixtures-priced-from-dated-valve-standings-2026-10-24`
- `session-ec033870-current-roster-anchor-would-pick-the-wrong-valve-row-2026-10-24`
- `session-ec033870-nine-past-rows-unresolved-2026-10-24`
