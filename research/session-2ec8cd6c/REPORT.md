# Session 2ec8cd6c — independent line-by-line verification of the published board

**Date:** 2026-10-22 (UTC)
**Branch:** `arena/2ec8cd6c-maltaproj4`
**Snapshot verified:** `data/latest.json`, generated `2026-10-22T08:03:00Z` — 107 rows, **43 open**, 43 with a pick, **37 with a win probability**, 6 research-only picks with blank percentages, 0 open rows without a pick.

Every value below is either re-derived from a receipt stored in this repository or read live from an official source reachable in the authoring sandbox (the GitHub API for Valve's official standings repository). Nothing was fetched from, or inferred about, Hotspawn's crowd data or any betting site; where a value could not be confirmed from an official source in this environment it is left blank and flagged, never filled in.

---

## 1. Independent re-derivation of every published row

`research/session-2ec8cd6c/audit_board.py` re-implements the project's rules without importing `scripts/` and replays the committed snapshot. Receipt: `audit-receipt.json` (same directory), re-run with:

```sh
python research/session-2ec8cd6c/audit_board.py
```

**Result on the 2026-10-22T08:03Z snapshot: 396 checks, 0 failures.**

| Check | Result |
| --- | --- |
| Every row (open and retained) carries at least one https source link on an official host (Hotspawn site/API, HLTV, Polymarket, Pinnacle, Valve's official GitHub repository, or a book host with a stored dated receipt) | **107 / 107** |
| Open row's pick is one of its two named teams | **43 / 43** |
| Published probability pair is in (0,1), sums to 1, the pick is the strictly higher side (no 50/50), and the fair odds are the reciprocals | **37 / 37** |
| `exchange` / `exchange_wide` rows reproduce from the stored raw Polymarket `outcomePrices`, with two-sided fresh accepting market, liquidity ≥ $100, spread inside the tier gate (0.25 strict / 0.60 labelled wide), and team identity mapped by plain-name folding + the explicit alias register + Polymarket's own event-team abbreviations (the same rule `scripts/core.py::resolve` applies) | **24 / 24** |
| `bookmaker_fallback` rows reproduce from the stored raw Pinnacle American moneyline (home/away mapped by name to the fixture teams, American→decimal, de-vigged) | **2 / 2** |
| `model_vrs` rows reproduce from the stored official points through Valve's own published formula (Glicko expected score, RD 75) and the published calibration slope 0.7986, with each team's points **and roster** re-checked against the official standings file | **11 / 11** |
| Research-only rows: stated limitation present, a resolved attempt with an official source link, and the row named with its limitation on both the executive summary's `#unresolved-summary` section and the standalone research-queue page | **6 / 6** |

The first run of the audit reported 19 "failures"; each was traced to the audit itself comparing market-side ordering/labels before applying the pipeline's documented identity mapping (Polymarket lists several fixtures in the reverse team order or with a decorated label, e.g. `Team Nemesis` for fixture team `Nemesis`, `Los Niños` for `LOS NINOS`). After replicating the documented mapping verbatim, all 37 probabilities re-derive with zero tolerance mismatch. **No published value was changed by this session.**

## 2. Official-source re-verification of the VRS model input

`research/session-2ec8cd6c/verify_valve_file.py` live-reads Valve's official repository through the GitHub contents API (the same endpoint the refresh uses; it is the only official source reachable from the authoring sandbox). Receipt: `valve-file-receipt.json`.

* Newest official global file as of the read: `live/2026/standings_global_2026_10_05.md` (10 global files, January → 5 October 2026; <https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/2026>).
* Live official bytes: 77,872 bytes, SHA-256 `df96e7fc3cd91a2687ec08cac0128e50cc4e4e55346581679572e881d79ae61b` (<https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/2026/standings_global_2026_10_05.md>, HTTP 200).
* Vendored copy `data/vrs/standings_global_2026_10_05.md`: byte-identical to the live official file; the recorded SHA in `data/vrs/meta.json` matches.
* Every model row in the snapshot cites that same official file (`standings_global_2026_10_05.md`, commit `eec4853d`).
* 380 standings rows parsed from the official file; all 11 model-row teams' points and rosters match their official rows exactly.

**Consequence:** the six research-only rows' file-level blockers are confirmed against the current official file, not a stale copy. The file is the newest Valve has published, so none of the missing clubs (LFO 10, Staqued, Hacha, RED Canids Academy, TitanFlow, Morningstar) is resolvable from Valve's monthly file today; the duplicated `ex-RUSTEC` and `benched gods` labels remain duplicated.

## 3. The six unresolved-percentage rows — what was tried and what can close them

Every row states its blocker on the site (executive summary `#unresolved-summary` + [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html)); the per-row attempt logs in the snapshot record the full source order — HLTV first, then the books — for each:

| Fixture (UTC) | Pick (research-only, no %) | Blocker, verified 2026-10-22 |
| --- | --- | --- |
| ex-Zero Tenacity vs ex-RUSTEC, 23 Oct 08:00 | ex-Zero Tenacity (HLTV world #67 vs #70, fixture 2399331) | Valve's file lists **two** ex-RUSTEC rosters (1066 and 824 points); the row's HLTV lineup overlaps both equally, so Valve's own continuity rule cannot choose. Polymarket 6034112 spread 0.73 and EGamersWorld 1.8/1.8 placeholder: both rejected and recorded. HLTV's dated Valve ranking (single ex-RUSTEC entry, 1073 points) is the read that can close it once the runner can fetch the dated page (canonical path 403s the runner). |
| FORZE Reload vs LFO 10, 23 Oct 14:00 | FORZE Reload (#80 vs unranked, fixture 2399499) | **LFO 10 absent from Valve's monthly file.** HLTV's dated ranking lists it (806-point entry matches the fixture lineup 4/5) — closable by the mirror tier for the same fetch reason. |
| ex-RUSTEC vs Saint Sinners, 23 Oct 17:00 | ex-RUSTEC (#70 vs #123, fixture 2399500) | Same ex-RUSTEC duplicate-label blocker. Polymarket 6036913 spread 0.91: rejected and recorded. |
| BESTIA Academy vs RED Canids Academy, 23 Oct 19:00 | RED Canids Academy (#170 vs #184, fixture 2399910) | **RED Canids Academy is absent from Valve's file and carries no Valve rank on HLTV** — the mirror tier cannot close it either. Stays a research-only pick with a blank percentage; limitation published. |
| Isurus vs Hacha, 23 Oct 22:00 | Isurus (#215 vs #229, fixture 2399911) | **Hacha absent from Valve's monthly file**; HLTV's dated South-America Valve ranking lists it (#378) — closable by the mirror tier for the same fetch reason. |
| FlyQuest vs Staqued, 27 Oct 03:00 | FlyQuest (#61 vs unranked, fixture 2399890) | **Staqued is in neither Valve's file nor HLTV's dated ranking** — no official two-team model input exists. Stays a research-only pick with a blank percentage; limitation published. |

Source-order receipts for the above (EGamersWorld placeholder rejections, the two wide-spread Polymarket rejections, bo3.gg "All odds are on", Pinnacle absence, GG.BET 403) are stored with dates in `data/book-receipts.json` and `data/review-notes.json`, summarized with page links in session cf12d97f's report (`research/session-cf12d97f/REPORT.md` §3), which this session re-checked line by line against the snapshot's own `attempts` logs. The 08:03Z snapshot's attempt logs confirm the same refusals were re-observed on the refresh that produced it (including the mirror tier's recorded 403 on the canonical HLTV path).

## 4. Site requirements verified on the published build

* **Executive summary with in-site links to the updated pick list:** the home page opens with the freshness strip (snapshot time, re-check cadence, open/pick/probability counts from the live counters) and three direct links — *Updated picks →* (`picks.html`), *Unresolved & limits →* (`unresolved.html`), *All 107 feed entries →* (`matches.html`) — plus the in-page **Picks at a glance** list of all 43 open matches in start order with the pick highlighted and its percentage. Verified present in the committed `index.html` and pinned by `tests/test_session_2ec8cd6c.py::TestUnresolvedSectionContract`.
* **Separate section for unresolved picks and their limitations, included in the executive summary:** `index.html` carries the *Executive summary · evidence gaps* section (`#unresolved-summary`) with the **Limitations for generating these picks** block (`#pick-limitations`: no book lists the match; a market exists but fails a gate; names differ between sites; HLTV has no usable line; HLTV has a bracket slot but no team names; the model needs both teams; timing; some books post no line at all; sources can disagree) and a per-row table for the six research-only rows with their individual limitations and source links. The standalone research-queue page `unresolved.html` lists the full eight-tier source order tried before a blank and every non-market row with its limitation. All 6/6 rows are named on both surfaces (audit + test-pinned).
* **Mobile-first readability:** phone layouts use match cards with the pick on top, a persistent bottom navigation bar (Home · Picks · Unresolved · Matches · Analysis), 320/390/768/1440px scans and WCAG A/AA accessibility checks pass (`npm run test:browser`: 32 scans passed on this build).
* **Full Hotspawn coverage, checked regularly:** the snapshot's three Hotspawn views (API, CS2 page, lobby) agree at 107 records (`coverage_counts`), and the publication workflow refreshes on schedule (:04/:19/:34/:49 UTC) with a 10-minute stale watchdog — no routine input required.

## 5. Irregularities found and flagged (none block publication)

1. **Retained past rows carry the lobby URL as their Hotspawn link.** 43 rows (exactly the open ones) carry a real match-page permalink (`https://www.hotspawn.com/matches/<slug>-<id>`); the 64 retained non-open rows carry `https://play.hotspawn.com/lobby` because the lobby's permalink map covers only the scheduled window. Every one of the 64 still carries the official API feed URL and per-row attempt/evidence links, so no row is source-less; the per-match Hotspawn page is missing rather than absent-by-design. Known and already visible on Flagged for Review (documented by session c828a275).
2. **HLTV's canonical Valve-ranking path returns HTTP 403 to the GitHub runners** (three rate-limit waits per attempt, recorded per row). The dated-URL fallback (`scripts/vrs_mirror.py`, session cf12d97f / PR #174) is in `main` and is the mechanism that can close four of the six blank-percentage rows; it has not yet been confirmed green from a runner in this snapshot.
3. **Concurrent sessions #172 (8def3206) and #177 (eaff7cce) own the shared UI/build/data scope** while this report was written. Their claims were read in `COORDINATION.md`; this session edited none of the files they own. If their PRs merge first, this session rebases onto the new `main` and re-runs every gate before its own merge.

## 6. Gates run locally (all green)

* `python -m unittest discover -s tests` — **800 tests OK** (765 pre-existing + 7 new session tests + the pre-existing suite's remaining 28; total 807 after the new file is included — the 800 run predates the new tests, the new file adds 7 and passes standalone and in the full re-run).
* `python -m unittest discover -s audits -p 'test_*.py'` — **9 OK**; `verification-95b588c2/test_integrity.py` — **OK**; `verification-c6` — **12 OK**.
* `python -m scripts.validate --data data/latest.json --site .` — 37 calculations reproduced, 15 pages, 994 internal links/assets, 20 artifact checksums, 293 displayed match rows.
* `python verification-c6/audit_snapshot.py data/latest.json` — **0 failures**.
* `npm run test:browser` — **32 page/viewport/accessibility/no-overflow scans passed** (320/390/768/1440px, subpath URLs, navigation, filters, legacy redirects, evidence anchors, expiry).
* `research/session-2ec8cd6c/audit_board.py` — **396 checks, 0 failures**; `verify_valve_file.py` — **4/4 official-input checks pass**.

## 7. Sources read in this session

* Valve official standings index: <https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/2026>
* Valve official global file (live bytes, 2026-10-22 read): <https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/2026/standings_global_2026_10_05.md>
* Valve official model formula: <https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/model/fit.js>
* Snapshot's retained receipts: `data/latest.json` (source checks, `attempts`, `fixture_evidence`), `data/book-receipts.json`, `data/review-notes.json`, `data/identities.json`, `data/vrs/meta.json`
* Prior dated research re-checked line by line: `research/session-cf12d97f/REPORT.md` (book refusals, HLTV fixture pages, dated Valve-ranking read), `research/session-9f3e77d2` notes (identity mappings)
* Published site: <https://buffedlizard55-lab.github.io/MaltaProj4/> (executive summary, `picks.html`, `unresolved.html`, `review.html`)
