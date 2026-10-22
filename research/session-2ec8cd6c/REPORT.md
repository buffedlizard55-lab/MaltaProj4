# Session 2ec8cd6c — independent line-by-line verification of the published board

**Date:** 2026-10-22 (UTC)
**Branch:** `arena/2ec8cd6c-maltaproj4`
**Snapshot verified:** `data/latest.json`, generated `2026-10-22T07:58:54.670274Z` (the board published on `main` after PR #175) — 107 rows, **43 open**, 43 with a pick, **41 with a win probability**, **2 research-only picks with blank percentages**, 0 open rows without a pick.

Every value below is either re-derived from a receipt stored in this repository or read live from an official source reachable in the authoring sandbox (the GitHub API for Valve's official standings repository). Nothing was fetched from, or inferred about, Hotspawn's crowd data or any betting site; where a value could not be confirmed from an official source in this environment it is left blank and flagged, never filled in.

---

## 1. Independent re-derivation of every published row

`research/session-2ec8cd6c/audit_board.py` re-implements the project's rules without importing `scripts/` and replays the committed snapshot. Receipt: `audit-receipt.json` (same directory), re-run with:

```sh
python research/session-2ec8cd6c/audit_board.py
```

**Result on the 2026-10-22T07:58:54Z snapshot: 404 checks, 0 failures.**

| Check | Result |
| --- | --- |
| Every row (open and retained) carries at least one https source link on an official host (Hotspawn site/API, HLTV, Polymarket, Pinnacle, Valve's official GitHub repository, or a book host with a stored dated receipt) | **107 / 107** |
| Open row's pick is one of its two named teams | **43 / 43** |
| Published probability pair is in (0,1), sums to 1, the pick is the strictly higher side (no 50/50), and the fair odds are the reciprocals | **41 / 41** |
| `exchange` (22) / `exchange_wide` (3) rows reproduce from the stored raw Polymarket `outcomePrices`, with two-sided fresh accepting market, liquidity ≥ $100, spread inside the tier gate (0.25 strict / 0.60 labelled wide), and team identity mapped by plain-name folding + the explicit alias register + Polymarket's own event-team abbreviations (the same rule `scripts/core.py::resolve` applies) | **25 / 25** |
| `bookmaker_fallback` rows (3) reproduce from the stored raw line — the Pinnacle American moneyline (2 rows) through the American→decimal conversion, and the Stavka.tv Winline listing receipt (1 row) from its decimal odds — de-vigged, with each side mapped to the fixture team by name | **3 / 3** |
| `model_vrs` rows (10) reproduce from the stored official points through Valve's own published formula (Glicko expected score, RD 75) and the published calibration slope 0.7986, with each team's points **and roster** re-checked against the official standings file | **10 / 10** |
| `model_vrs_mirror` rows (3) apply the same formula to the stored Valve-points values from HLTV's dated ranking page, with the dated-page provenance recorded and verified on the row: HLTV valve-ranking URL, dated heading ("ranking on October 22nd, 2026"), 396-club table, page SHA-256, the official file the values stand in for (`standings_global_2026_10_05.md`), and ≥3-player roster-continuity checks on both sides | **3 / 3** |
| Research-only rows (2): stated limitation present, a resolved attempt with an official source link, and the row named with its limitation on both the executive summary's `#unresolved-summary` section and the standalone research-queue page | **2 / 2** |

The first run of the audit (against the 2026-10-22T08:03Z board that `main` carried before this session rebased onto f75054d) reported 19 "failures"; each was traced to the audit itself comparing market-side ordering/labels before applying the pipeline's documented identity mapping (Polymarket lists several fixtures in the reverse team order or with a decorated label, e.g. `Team Nemesis` for fixture team `Nemesis`, `Los Niños` for `LOS NINOS`). After replicating the documented mapping verbatim, every probability re-derives with zero tolerance mismatch. **No published value was changed by this session.**

## 2. Official-source re-verification of the VRS model input

`research/session-2ec8cd6c/verify_valve_file.py` live-reads Valve's official repository through the GitHub contents API (the same endpoint the refresh uses; it is the only official source reachable from the authoring sandbox). Receipt: `valve-file-receipt.json`.

* Newest official global file as of the read: `live/2026/standings_global_2026_10_05.md` (10 global files, January → 5 October 2026; <https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/2026>).
* Live official bytes: 77,872 bytes, SHA-256 `df96e7fc3cd91a2687ec08cac0128e50cc4e4e55346581679572e881d79ae61b` (<https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/2026/standings_global_2026_10_05.md>, HTTP 200).
* Vendored copy `data/vrs/standings_global_2026_10_05.md`: byte-identical to the live official file; the recorded SHA in `data/vrs/meta.json` matches.
* Every model row in the snapshot cites that same official file (`standings_global_2026_10_05.md`, commit `eec4853d`); the three mirror rows record it as the official filing date their dated HLTV values stand in for.
* 380 standings rows parsed from the official file; all 10 model-row teams' points and rosters match their official rows exactly.

**Consequence:** the two remaining research-only rows' file-level blockers are confirmed against the current official file, not a stale copy. The file is the newest Valve has published, so RED Canids Academy and Staqued are resolvable from no official two-team model input today.

## 3. The two unresolved-percentage rows — what was tried and what can close them

Every row states its blocker on the site (executive summary `#unresolved-summary` + [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html)); the per-row attempt logs in the snapshot record the full source order — HLTV first, then the books — for each:

| Fixture (UTC) | Pick (research-only, no %) | Blocker, verified 2026-10-22 |
| --- | --- | --- |
| BESTIA Academy vs RED Canids Academy, 23 Oct 19:00 (fixture 1082925) | RED Canids Academy (HLTV world #170 vs BESTIA #184, HLTV fixture 2399910) | **RED Canids Academy is absent from Valve's monthly file and from HLTV's dated 2026-10-22 Valve ranking** — neither model tier can run. Polymarket's market for the pair exceeds the 60-point wide-tier spread ceiling; Pinnacle has no exact pair+start; Thunderpick yields no validated two-way quote; GG.BET 403s; EGamersWorld serves the 1.8/1.8 placeholder (recorded rejection). Stays a research-only pick with a blank percentage; limitation published with its source links. |
| FlyQuest vs Staqued, 27 Oct 03:00 (fixture 1082860) | FlyQuest (#61 vs unranked, HLTV fixture 2399890) | **Staqued is in neither Valve's monthly file nor HLTV's dated 2026-10-22 Valve ranking**, and no exchange or book lists the pair at all (each Polymarket/Pinnacle/Thunderpick/GG.BET refusal is recorded in the row's attempt log). Stays a research-only pick with a blank percentage; limitation published with its source links. |

The other four rows that were unresolved on the 07:42Z board are now priced on `main` by concurrent session cb867c3c (PR #175, merged): ex-Zero Tenacity vs ex-RUSTEC from the Stavka.tv Winline moneyline listing (1.90/1.80 → 48.6/51.4, pick ex-RUSTEC), and FORZE Reload vs LFO 10, ex-RUSTEC vs Saint Sinners, Isurus vs Hacha from the `model_vrs_mirror` tier (HLTV's dated 2026-10-22 Valve ranking read live by the runner, page SHA recorded). This session re-derived those three mirror lines and the Winline line from their stored receipts (Section 1) but does not claim them.

## 4. Site requirements verified on the published build

* **Executive summary with in-site links to the updated pick list:** the home page opens with the freshness strip (snapshot time, re-check cadence, open/pick/probability counts from the live counters) and three direct links — *Updated picks →* (`picks.html`), *Unresolved & limits →* (`unresolved.html`), *All 107 feed entries →* (`matches.html`) — plus the in-page **Picks at a glance** list of all 43 open matches in start order with the pick highlighted and its percentage. Verified present in the committed `index.html` and pinned by `tests/test_session_2ec8cd6c.py::TestUnresolvedSectionContract`.
* **Separate section for unresolved picks and their limitations, included in the executive summary:** `index.html` carries the *Executive summary · evidence gaps* section (`#unresolved-summary`) with the **Limitations for generating these picks** block (`#pick-limitations`: no book lists the match; a market exists but fails a gate; names differ between sites; HLTV has no usable line; HLTV has a bracket slot but no team names; the model needs both teams; timing; some books post no line at all; sources can disagree) and a per-row table for the two research-only rows with their individual limitations and source links. The standalone research-queue page `unresolved.html` lists the full eight-tier source order tried before a blank and every non-market row with its limitation. Both rows are named on both surfaces (audit + test-pinned).
* **Mobile-first readability:** phone layouts use match cards with the pick on top, a persistent bottom navigation bar (Home · Picks · Unresolved · Matches · Analysis), 320/390/768/1440px scans and WCAG A/AA accessibility checks pass (`npm run test:browser`: 32 scans passed on this build).
* **Full Hotspawn coverage, checked regularly:** the snapshot's three Hotspawn views (API, CS2 page, lobby) agree at 107 records (`coverage_counts`), and the publication workflow refreshes on schedule (:04/:19/:34/:49 UTC) with a 10-minute stale watchdog — no routine input required.

## 5. Irregularities found and flagged (none block publication)

1. **Retained past rows carry the lobby URL as their Hotspawn link.** 43 rows (exactly the open ones) carry a real match-page permalink (`https://www.hotspawn.com/matches/<slug>-<id>`); the 64 retained non-open rows carry `https://play.hotspawn.com/lobby` because the lobby's permalink map covers only the scheduled window. Every one of the 64 still carries the official API feed URL and per-row attempt/evidence links, so no row is source-less; the per-match Hotspawn page is missing rather than absent-by-design. Known and already visible on Flagged for Review (documented by session c828a275).
2. **HLTV's canonical Valve-ranking path refused the authoring sandbox (HTTP 403)**; the refresh runner read it successfully on this board's refresh (07:58Z) after the TLS-transport fallback landed (PR #175), and the three mirror rows record the page SHA as proof of the read. If the refusal returns on a later run, the rows fail closed back to research-only picks with the refusal recorded — no stale value is published.
3. **Concurrent sessions own the shared UI/build/data scope** while this report was written: #172 (8def3206) and #177 (eaff7cce) are still open, and #179 (13e99ca6, executive-summary banner + HLTV→esportsbook research notes) merged mid-session (f75054d → 4f250e2). Their claims were read in `COORDINATION.md`; this session edited none of the files they own, rebased onto the new `main` (4f250e2), and re-ran every gate (Section 6 numbers reflect the final base).

## 6. Gates run locally (all green, on the rebased board)

* `python -m unittest discover -s tests` — **829 tests OK** (822 pre-existing on the rebased board + 7 new session tests).
* `python -m unittest discover -s audits -p 'test_*.py'` — **9 OK**; `verification-95b588c2/test_integrity.py` — **OK**; `verification-c6` — **12 OK**.
* `python -m scripts.validate --data data/latest.json --site .` — 41 calculations reproduced, 15 pages, 968 internal links/assets, 20 artifact checksums, 283 displayed match rows.
* `python verification-c6/audit_snapshot.py data/latest.json` — **0 failures**.
* `npm run test:browser` — **32 page/viewport/accessibility/no-overflow scans passed** (320/390/768/1440px, subpath URLs, navigation, filters, legacy redirects, evidence anchors, expiry).
* `research/session-2ec8cd6c/audit_board.py` — **404 checks, 0 failures**; `verify_valve_file.py` — **4/4 official-input checks pass**.

## 7. Sources read in this session

* Valve official standings index: <https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/2026>
* Valve official global file (live bytes, 2026-10-22 read): <https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/2026/standings_global_2026_10_05.md>
* Valve official model formula: <https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/model/fit.js>
* Snapshot's retained receipts: `data/latest.json` (source checks, `attempts`, `fixture_evidence`), `data/book-receipts.json`, `data/review-notes.json`, `data/identities.json`, `data/vrs/meta.json`
* Prior dated research re-checked line by line: `research/session-cf12d97f/REPORT.md` (book refusals, HLTV fixture pages, dated Valve-ranking read), session 9f3e77d2 notes (identity mappings)
* Published site: <https://buffedlizard55-lab.github.io/MaltaProj4/> (executive summary, `picks.html`, `unresolved.html`, `review.html`)
