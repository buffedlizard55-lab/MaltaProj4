# Session 138cbedd — verification pass and freshness-clock repair

**Date:** 2026-10-23 · **Branch:** `arena/138cbedd-maltaproj4` · **Snapshot audited:**
`data/latest.json`, generated **2026-10-23T10:05:50Z**, fixture evidence **2026-10-23T10:02:13Z** (the
builder's refresh that landed on `main` while this branch was open; every number below is read from
that snapshot, not from the earlier 08:32Z one).

## 1. What this session was asked to confirm

The user's standing requirements for this project are: a pick for **every** match listed on Hotspawn
for CS2 (including low-tier fixtures no book prices), a clearly separate unresolved section with its
limitations carried into the executive summary, in-site links from the summary to the updated picks,
a phone-readable board, and line-by-line verification with an official source link on every row.
Hotspawn may supply the fixture list only — never a probability.

## 2. Line-by-line verification (independent of the project's own code)

`verification-138cbedd/audit_board.py` is a **zero-collector** auditor: it imports none of the
project's modules and trusts no stored number. It re-reads the published snapshot and re-derives each
figure from the raw source fields kept beside it.

**Result: 1,041 checks over 92 rows, 0 failures.** Report: [`BOARD-AUDIT.md`](BOARD-AUDIT.md),
machine receipt [`board-audit.json`](board-audit.json), and the same audit repeated against the
staged public copy in [`published-audit.json`](published-audit.json).

| Contract | Result on this snapshot |
| --- | --- |
| Fixtures retained | **92**, all three Hotspawn views agree (`api` = `page` = `lobby` = `retained` = 92) |
| Open matches | **30** (starts 2026-10-23T11:00Z → 2026-10-31T13:00Z) |
| Open matches with a pick | **30 / 30** |
| Open matches with a two-sided win probability | **30 / 30** |
| Open matches with no supported pick | **0** |
| Probabilities re-derived from their own raw fields | **30 / 30**, maximum error **0.0e+00** (model rows ≤ 1e-15) |
| Picks naming a team in the same row | 30 / 30 |
| Pick equal to the larger re-derived probability | 30 / 30 |
| Fair odds exactly `1/p` per side | 30 / 30 |
| Expiry ≤ 8 h after the row's own observation, its lock and its start | 30 / 30 |
| Rows whose evidence names Hotspawn as price provider | **0** |

Method mix on the open board: **23 Polymarket exchange quotes** (20 strict, **3** in the labelled
wide-spread tier), **5 originated Valve-VRS model lines**, **2 dated EGamersWorld bookmaker listings**.
90 source attempts are retained across the board, including the unsuccessful ones. Earliest expiry
10:54Z (this morning's first lock), latest 18:02Z.

### What "re-derived" means per tier

* **Exchange** (`exchange`, `exchange_wide`) — renormalise the market's own two outcome prices
  (`pᵢ = xᵢ / (x₁ + x₂)`). Outcome labels are mapped to the Hotspawn pair by documented identity only
  (exact label, a single trailing word such as `Hacha` / `Hacha Esports`, or the project's alias
  register). Where the mapping is not provable the auditor reports it for review instead of assuming
  an order — that is why row `1079657` (Polymarket lists `Brute, BakS eSports` while Hotspawn lists
  `BakS, BRUTE`) is verified by name and *not* by array position.
* **Bookmaker listing** (`bookmaker_fallback`) — de-vig `1/d` for both decimal odds and check the
  overround stays inside the published −2 % … 25 % gate. FlyQuest vs Staqued: `1.001 / 12.0` →
  92.30 % / 7.70 %, overround 8.23 %. NEXVOID vs Alter Ego: `1.61 / 2.14` → 57.07 % / 42.93 %,
  overround 8.84 %.
* **Model** (`model_vrs`) — Valve's own Glicko expectation at RD 75 (`g = 1/√(1+3q²RD²/π²)`),
  then Valve's published calibration slope 0.7986 about 50 %. Example: Phantom Academy 783 points
  vs Banda chuya 801 → raw 0.474821 → calibrated **0.479892 / 0.520108**, which is the stored value
  to 1e-15.

### The auditor is proven to fail

`tests/test_session_138cbedd.py` applies **19 separate corruptions** to a copy of the committed
snapshot and requires a specific failure for each: probabilities that no longer sum to 1, a swapped
pair, a pick that is not the larger side, a pick that is not one of the teams, a research tier
carrying a number, fair odds that are not `1/p`, edited model points, edited listing odds, an expiry
past the start, an expiry past the 8-hour window, a Hotspawn price, a duplicate fixture id, an open
row that already started, a closed row keeping a pick, missing evidence, and a missing expiry. A
verifier that only ever passes verifies nothing.

## 3. Defect found and repaired: a "next slot" that is already in the past

**Measured, not theoretical.** The built executive summary carried the byte string
`<span class="fresh-schedule"> · automatic re-check at :04, :19, :34 and :49 past each hour · next slot 08:34 UTC</span>`,
computed once from the snapshot clock at 08:32:56Z. The published page was still serving that sentence
when it was read at 10:20Z, so a reader was told the next check would happen 1 h 51 m earlier. Every
other clock on the page (counts, expiry, withheld picks) is evaluated in the browser; this one was
not.

**Repair** (`scripts/build.py`, `site/assets/app.js`, `site/assets/style.css` and the identical
`assets/*` copies the staged root serves):

* the build still states the first slot after its own snapshot, now inside
  `<span id="next-slot" data-slot-minutes="4,19,34,49">` (a fallback for readers without JavaScript);
* `renderClock()` recomputes that slot against the **reader's** clock on every expiry tick, so the
  advertised slot is always 0–15 minutes ahead;
* the same function fills `<span id="fresh-age">` with the snapshot's real age (` · 1h 28m ago`) and,
  once the snapshot passes the **90-minute refresh target** the watchdog uses, appends
  ` · past the 90-minute refresh target` and marks it in the stylesheet. On a phone the long schedule
  line stays folded (existing first-screen contract) but the age — the part that matters — stays
  visible.

**Proof it works:** `tests/browser_138cbedd.cjs` drives the real page at 390×844 and 1440×900 with a
faked clock at +6 min, +2 h and +6 h from the observed snapshot. It asserts the advertised slot is
always 0–15 minutes in the future, the age text is always present, the overdue marker appears exactly
when it should, and nothing scrolls sideways. All six reads pass, and the board's per-row
`Observed … UTC / Expires … UTC` times are asserted in the same run.

**Not added to `picks.html` on purpose.** At 320×568 the first pick row already sits at y=572 and the
first probability at y=696, and the existing first-screen contract requires the pick above 844 px.
Rather than break a measured phone guarantee to duplicate a message, the board keeps its per-row
observation/expiry times and the >8 h stale banner instead of a second block.

## 4. Freshness of the published board — finding, not a code claim

`gh run list` at claim time showed **six `schedule` events in the last 100 workflow runs**, the most
recent at **07:20:51Z**, and the watchdog's `*/10` cron produced **no scheduled runs at all** — every
watchdog run in the list is `push`-triggered. The committed snapshot therefore stood at 08:29Z while
being read at 10:20Z, i.e. already past the 4–8 hour promise's *fast* end on a quiet morning.
This is recorded as an operational finding: GitHub's delivery of scheduled jobs to this repository is
the binding constraint, not the pipeline. The merge of this session triggers a real refresh and the
production run is verified below. The behaviour is flagged on **Flagged for Review**, not papered
over with a static "updated just now" string.

## 5. Gates run on this tree

| Gate | Result |
| --- | --- |
| `python -m unittest discover -s tests` | **1,086 tests, OK** (3 skipped), including 28 new |
| `audits` | 9 tests OK |
| `verification-95b588c2/test_integrity.py` | 5 tests OK |
| `verification-c6` | 12 tests OK |
| `verification-c6/audit_snapshot.py public/data/latest.json` | **0 failures** |
| `verification-138cbedd/audit_board.py` (committed + published copies) | **1,041 checks, 0 failures** each |
| `scripts.validate --data data/latest.json --site .` | 92 rows, 30 calculations, 15 pages, 820 links/assets, 20 checksums, 224 displayed rows |
| `npm run test:browser` (7 suites) | all pass: 32 viewport/accessibility scans, expiry scenarios, phone first-screen, completeness prose, new freshness clock |

## 6. Sources used for manual review

* Hotspawn CS2 lobby and fixture feed — `https://play.hotspawn.com/lobby`,
  `https://play.hotspawn.com/cs2-pickems`,
  `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`
* Polymarket Gamma API market pages, e.g. `https://gamma-api.polymarket.com/markets/6036897`
  (Nuclear TigeRES vs ILLYRIANS — `0.865 / 0.135` at the 08:29Z read, `0.85 / 0.15` at the 10:02Z
  read; both renormalise exactly and the row is marked low-precision when the spread widens)
* Valve official Regional Standings 2026-10-05 —
  `https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md`
  and Valve's formula `model/fit.js` in the same repository
* EGamersWorld dated listings —
  `https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3`,
  `https://egamersworld.com/counterstrike/match/4kaAQWgKEx/nexvoid-vs-alter-ego-HfdcJeXmT`
* HLTV fixture identity — `https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026`,
  `https://www.hltv.org/matches/2399889/nexvoid-vs-alter-ego-dfrag-invitational-2026`

Outbound access from this sandbox reaches only `github.com`, `codeload.github.com`,
`api.github.com`, `registry.npmjs.org`, `pypi.org` and `files.pythonhosted.org`; Polymarket, HLTV,
EGamersWorld and Hotspawn itself are **not** reachable from here. Every price above was therefore
verified by recomputation from the raw fields captured by the production runner (each with its own
retrieval timestamp and SHA-256), not by a fresh fetch from this session. That limitation is stated
rather than glossed: the arithmetic and the internal consistency are independently verified here; the
sources' own availability is evidenced by the runner receipts in `data/latest.json`.

## 7. Flagged for review

1. **Scheduled delivery, not code** — six `schedule` runs in the last 100 workflow runs, none since
   07:20:51Z; the `*/10` watchdog has produced only push-triggered runs. The board can age past the
   4–8 hour promise even though the pipeline is green.
2. **The freshness clock is client-side** — with JavaScript disabled the page still shows the
   build-time slot, which is why the no-JavaScript warning already says live checks require
   JavaScript. That is disclosed, not hidden.
3. **Identity mapping for five exchange rows** relies on label variants (`Hacha` / `Hacha Esports`,
   `LPH` / `LPH Gaming`, `BakS` / `BakS eSports`, one swapped order). All five recompute exactly and
   the register/alias rule is documented, but a human should still eyeball the five.
