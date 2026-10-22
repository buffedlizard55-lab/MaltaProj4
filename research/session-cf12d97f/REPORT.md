# Session cf12d97f — dated evidence for the rows that publish no win probability, and the read that can close them

**Date:** 2026-10-22 (UTC)
**Branch:** `arena/cf12d97f-maltaproj4`
**Snapshot researched:** `data/latest.json`, generated `2026-10-22T07:42:29.738379Z` — 107 rows, 46 open, 45 picks, **39 with a win probability**, 6 picks without a percentage, 1 row with no pick at all.

Every fact below was read on 2026-10-22 and is linked to the page it came from. Where a value could not be confirmed, it is written as *not confirmed* rather than filled in. No probability was invented and no market was loosened to make a row publishable.

---

## 1. Scope: the seven rows the site could not price

| Row | Fixture | Start (UTC) | State on the site | Why it has no percentage |
| --- | --- | --- | --- | --- |
| 1079654 | ex-Zero Tenacity vs ex-RUSTEC | 2026-10-23 08:00 | pick, blank % | Valve's file lists **two ex-RUSTEC rosters** with the same overlap against the row's HLTV lineup → tie, no model line |
| 1081149 | FORZE Reload vs LFO 10 | 2026-10-23 14:00 | pick, blank % | **LFO 10 is absent from Valve's monthly file** → the model tier cannot resolve both clubs |
| 1081150 | ex-RUSTEC vs Saint Sinners | 2026-10-23 17:00 | pick, blank % | same ex-RUSTEC ambiguity |
| 1082925 | BESTIA Academy vs RED Canids Academy | 2026-10-23 19:00 | pick, blank % | **RED Canids Academy is absent from Valve's monthly file** |
| 1082926 | Isurus vs Hacha | 2026-10-23 22:00 | pick, blank % | **Hacha is absent from Valve's monthly file** |
| 1082860 | FlyQuest vs Staqued | 2026-10-27 03:00 | pick, blank % | **Staqued is absent from Valve's monthly file** |
| 1082919 | Projeto do KinGui vs Martians | 2026-10-22 13:00 | **no pick on the 07:42Z capture** | no HLTV team page carries the label "Projeto do KinGui"; no market pair; no rank → nothing invented. *Resolved on `main` after this report was written: session 9f3e77d2 (PR #176) mapped the club to Tropa do KinGui / ex-Keyd Stars and priced it from Polymarket market 6033256 (0.75/0.25, spread 0.42, liquidity $156.04).* |

All six "blank percentage" rows carry the same recorded blocker in the snapshot's own attempt log:

> `HLTV Valve ranking mirror unavailable: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run.`

and, immediately before it, the model tier's own verdict:

> `No originated line: <club>: not listed in the Valve global standings.` (LFO 10, RED Canids Academy, Hacha, Staqued)
> `No originated line: ex-RUSTEC: more than one listed roster shares the same number of players with the current HLTV lineup.` (1079654, 1081150)

So there are exactly two causes: **(a)** the club is not in Valve's monthly file, and **(b)** the club appears twice in Valve's file and the row's lineup cannot separate the two entries. Both are *file* problems, not *market* problems: no bookmaker would quote these fixtures anyway (see §3).

---

## 2. What Valve's own monthly file does and does not contain

Read on 2026-10-22 from ValveSoftware/counter-strike_regional_standings, `live/2026/` — the newest official set is dated **2026-10-05** (`standings_{global,europe,asia,americas}_2026_10_05.md`; the global file is the one the pipeline consumes, `data/vrs/standings_global_2026_10_05.md`).

* Present: Saint Sinners (global #158, 810 points), benched gods (#157, 811 and #329, 516 — **two rows**), ex-RUSTEC (#92, 1066 and #152, 824 — **two rows**), ex-Zero Tenacity (#93, 1066), FORZE Reload (#84, 1100), FlyQuest (#86, 1093).
* **Absent from all four regional files and the global file:** LFO 10, TitanFlow, Staqued, Morningstar, RED Canids Academy, Hacha.

Source: <https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/2026> and the four raw `standings_*_2026_10_05.md` files.

This is why the official-file model tier cannot price the "absent" rows: it has no points for them.

---

## 3. What the books actually say today (read 2026-10-22)

### 3.1 EGamersWorld — every one of these fixtures is listed, every one is a **1.8 / 1.8 placeholder**

The site renders a fixed "1.8" on both sides when no real price exists, so these listings carry **no information** and were rejected by the pipeline's placeholder rule (`scripts/books.py`):

| Fixture | Listing | Rendered | Extra facts the page does show |
| --- | --- | --- | --- |
| benched gods vs TitanFlow | <https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn> | 1.8 / 1.8 | EGW rating 694 vs 1408 |
| ex-Zero Tenacity vs ex-RUSTEC | <https://egamersworld.com/counterstrike/match/_rW8GEyWK/ex-zero-tenacity-vs-ex-rustec-YieSsHTBr> | 1.8 / 1.8 | CCT Europe 2026 Series #11, 23.10.2026 08:00; ratings 170 vs 259; ex-RUSTEC lineup with **relaxxie** |
| ex-RUSTEC vs Saint Sinners | <https://egamersworld.com/counterstrike/match/HiXMAaC8L/ex-rustec-vs-saint-sinners-uI7ncz4GF7> | 1.8 / 1.8 | CCT Europe 2026 Series #12, display 23.10 13:00 (= 17:00Z) |
| FlyQuest vs Staqued | <https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3> | 1.8 / 1.8 | DFRAG Invitational 2026, 27.10.2026 03:00 |
| BESTIA Academy vs RED Canids Academy | <https://egamersworld.com/counterstrike/match/0U32SId-H/bestia-academy-vs-red-canids-academy-3nbNt3Gf1p> | 1.8 | EGW rating 408 vs 608; H2H 1–1; last meeting 27.08.26 |
| Isurus vs Hacha | <https://egamersworld.com/counterstrike/match/0U32SId-H/isurus-vs-hacha-esports-qgq9dKgkRU> | 1.8 / 1.8 | EGW rating 395 vs 1139; EGW's full label is **"Hacha Esports"** while Hotspawn says "Hacha" |

EGW's own tips page carries real two-way prices only for the large events (Vitality 1.12, MOUZ 1.22, Aurora 1.25, TYLOO 1.17 …); none of the seven fixtures is listed.

### 3.2 Polymarket — two markets exist, and **both books are empty**

| Market | Prices | Best bid / ask | Spread | Liquidity |
| --- | --- | --- | --- | --- |
| <https://gamma-api.polymarket.com/markets?slug=cs2-zerote-rustec-2026-10-23> (market 6034112, event 1232992, start 08:00Z) | 0.565 / 0.435 | 0.20 / 0.93 | **0.73** | $662.14 |
| <https://gamma-api.polymarket.com/markets?slug=cs2-rustec-ssins-2026-10-23> (market 6036913, event 1233765, start 17:00Z) | 0.495 / 0.505 | 0.04 / 0.95 | **0.91** | $505.68 |

Both markets are `funded: false`, `ready: false`, $0 volume, with the map markets at 0.5/0.5 and a 0.92 spread. The project's policy publishes a two-sided quote only when the spread is at most 0.25 (strict tier) or 0.60 (wide tier) — **0.73 and 0.91 are both outside it**, so the visible midpoint is not a price anyone could trade at. Rejected, and the rejection is recorded in `data/book-receipts.json`.

Polymarket's own search confirms there is **no market at all** for the remaining fixtures: `public-search?q=RED Canids Academy` returns only the closed July 2026 ALKA events, and `public-search?q=Hacha` returns only the resolved 21 Oct Damajuana event; the team pages for benched gods, FlyQuest and Staqued show **0 active markets**.

### 3.3 bo3.gg — "All odds are on"

<https://bo3.gg/matches/benched-gods-vs-titanflow-22-10-2026>, <https://bo3.gg/matches/ex-zero-tenacity-vs-ex-rustec-23-10-2026> and <https://bo3.gg/matches/flyquest-vs-staqued-27-10-2026> all show the message **"All odds are on"** — no two-way price. The `forze-reload-vs-lfo-10-23-10-2026` slug 404s. bo3.gg does carry real two-way odds for other CS2 matches on the same day, so the absence is specific to these fixtures, not a site-wide failure.

### 3.4 HLTV's own betting table

The pipeline's read of the HLTV match pages reports *"HLTV betting table does not expose a numeric two-way line in this response"*. Confirmed by hand on the fixture pages themselves, which carry the fixture identity, the UTC start, both lineups and both world ranks but no two-way price:

| Fixture | HLTV page (read by the refresh at 07:39Z) | World rank / VRS rank on HLTV |
| --- | --- | --- |
| ex-Zero Tenacity vs ex-RUSTEC | <https://www.hltv.org/matches/2399331/ex-zero-tenacity-vs-ex-rustec-cct-2026-europe-series-11> | 67 / 95 and 70 / 91 |
| FORZE Reload vs LFO 10 | <https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12> | 80 / 84 and — / 157 |
| ex-RUSTEC vs Saint Sinners | <https://www.hltv.org/matches/2399500/ex-rustec-vs-saint-sinners-cct-2026-europe-series-12> | 70 / 91 and 123 / 133 |
| FlyQuest vs Staqued | <https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026> | 61 / 54 and — / — |
| BESTIA Academy vs RED Canids Academy | <https://www.hltv.org/matches/2399910/bestia-academy-vs-red-canids-academy-cct-2026-south-america-series-7> | 184 / 243 and 170 / — |
| Isurus vs Hacha | <https://www.hltv.org/matches/2399911/isurus-vs-hacha-cct-2026-south-america-series-7> | 215 / 200 and 229 / 378 |

**Conclusion of §3:** there is no publishable market line for any of the seven rows today. Every "line" that exists is either a 1.8/1.8 placeholder or a book with a 73–91 point spread. Inventing a price from them would be exactly the hallucination the project forbids.

---

## 4. The read that *can* close four of the six gaps — and why it was blocked

Valve publishes its ranking monthly as a file; HLTV republishes the **same ranking, dated, continuously**, including the clubs that are too small for Valve's monthly file (LFO 10, TitanFlow, Staqued, Hacha). The pipeline already has a tier for exactly this ("the mirror tier", added by session 6dd6f287) — but it could only read the canonical path:

```
https://www.hltv.org/valve-ranking/teams      →  HTTP 403 from the runner (measured, 3 waits: 10s, 30s, 60s)
```

### 4.1 The dated view exists, is the same view, and carries the same numbers

Read by hand on 2026-10-22 at ≈08:05Z: <https://www.hltv.org/valve-ranking/teams/2026/october/22>

* Title: "Counter-Strike Ranking | Valve Global Ranking | HLTV.org"
* Heading: **"Valve global ranking on October 22nd, 2026"**
* Row shape: `#1 Vitality(1993 Valve points)EU apEX ropz ZywOo flameZ mezii` — the same `ranked-team` block markup the parser already reads, and the same "Valve points" wording (the undated world-ranking page reads "HLTV points" and is deliberately refused by the parser).
* Regional views exist at the same dated path: `…/2026/october/22/region/Europe`, `…/region/Americas`, `…/region/Asia`.
* The page's own date is in the heading, so the parser's existing "dated heading required" rule still applies to this form.

The entries for the clubs in scope, read through the search index of that same dated page (page dated 22 Oct 2026):

| Club | Standing | Valve points | Roster shown on the page |
| --- | --- | --- | --- |
| FORZE Reload | #61 | 1103 | (Europe) |
| LFO 10 | **#111** | **806** | dottie, flaw, Sapec, Mann3n, L00m1 |
| LFO 10 | **#205** | **565** | (second entry) |
| benched gods | #160 | 792 | Wign, K014NZ, facer, norescue, yoyoS2 |
| benched gods | #349 | 496 | (second entry) |
| TitanFlow | #235 | 664 | (Europe) |
| ex-RUSTEC | #91 | 1073 | shalfey, Brilliance, bl1x1, youka, yiksrezo |

### 4.2 What the change does (and what it deliberately does not do)

`scripts/vrs_mirror.py` now reads the canonical URL first and, when HLTV refuses it, the dated URLs for the last three days, newest first
(`/valve-ranking/teams/2026/october/22`, `…/21`, `…/20`). Every refusal and every parse miss is recorded in the row's attempt log. Nothing else changes:

* the parser still refuses a page without a dated heading, a page that says "HLTV points", and any table that is not a complete, ordered list of ≥100 clubs;
* the roster-continuity rule still has to pick the right row when a club appears twice (LFO 10 at 806 and 565 points, benched gods at 792 and 496, ex-RUSTEC twice in Valve's file) — the row's own HLTV lineup must overlap ≥3 of the listed roster, and the lineup must itself come from an HLTV page;
* the eight-hour evidence window, the calibration constants and the published "this is a model estimate, not a market price" label are unchanged;
* the validator now accepts the dated URL form and still refuses any other host.

**Rows this can close if the runner can read the dated page:** 1081149 (LFO 10 — the 806-point entry matches the fixture's lineup Sapec/L00m1/dottie/Mann3n on four of five names, the 565-point entry on fewer), 1082926 (Hacha appears in HLTV's South America Valve ranking at #378), 1079654 and 1081150 (ex-RUSTEC's single HLTV entry at 1073 points separates the tie that Valve's monthly file cannot separate).
**Rows it cannot close:** 1082860 (FlyQuest vs Staqued — Staqued is in neither Valve's file nor HLTV's ranking) and 1082925 (RED Canids Academy carries no Valve rank on HLTV either: `vrs_rank_on_hltv` is empty in the refresh's own read).

---

## 5. The count drift on the executive summary (found while checking the above)

On the live site the freshness strip read **"34 open CS2 match(es) · 34 with a pick · 29 with a win probability"** while the coverage card directly underneath read **"33 open CS2 matches. 33 picks. 28 with a win probability."** Cause: `scripts/build.py::fresh_strip` printed build-time totals as static text, while the card, the buttons and the notices use live `data-count` counters that `assets/app.js` rewrites from the same expiry rules. One row that locked or started therefore moved the card and left the strip stale — the exact "the numbers on the page disagree" complaint. Fixed by giving the strip and the three coverage notices the same live counters; the build-time numbers stay in the markup as the no-JavaScript fallback.

---

## 6. Sources read (all 2026-10-22)

* Valve official standings: <https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/2026> — `standings_global_2026_10_05.md`, `standings_europe_2026_10_05.md`, `standings_asia_2026_10_05.md`, `standings_americas_2026_10_05.md`.
* HLTV Valve ranking (dated): <https://www.hltv.org/valve-ranking/teams/2026/october/22> and its regional forms.
* HLTV fixture pages: 2399331, 2399499, 2399500, 2399890, 2399910, 2399911 (see the table in §3.4).
* EGamersWorld listings: `benched-gods-vs-titanflow-EcLgERbZn`, `ex-zero-tenacity-vs-ex-rustec-YieSsHTBr`, `ex-rustec-vs-saint-sinners-uI7ncz4GF7`, `flyquest-vs-staqued-zawJ-Q52S3`, `bestia-academy-vs-red-canids-academy-3nbNt3Gf1p`, `isurus-vs-hacha-esports-qgq9dKgkRU`, plus <https://egamersworld.com/counterstrike/tips>.
* Polymarket Gamma API: markets `cs2-zerote-rustec-2026-10-23` (6034112), `cs2-rustec-ssins-2026-10-23` (6036913), events 1232992 / 1233765, `public-search` for "RED Canids Academy" and "Hacha", team pages for benched gods / FlyQuest / Staqued.
* bo3.gg match centre: `benched-gods-vs-titanflow-22-10-2026`, `ex-zero-tenacity-vs-ex-rustec-23-10-2026`, `flyquest-vs-staqued-27-10-2026`.
* The project's own machine reads of the same pages are stored with timestamps in `data/latest.json` (`hltv_context`, `attempts`) and in `data/book-receipts.json`.

## 6a. Change of state on `main` after this report was written

While this session was researching, session 9f3e77d2 merged PR #176 and resolved the one row that had no pick: `Projeto do KinGui vs Martians` (1082919) is now priced from Polymarket moneyline market 6033256 (0.75/0.25, liquidity $156.04, spread 0.42) with the identity mapping to *Tropa do KinGui* / *ex-Keyd Stars* verified against HLTV match 2399904 and Valve's `2026-10-05` global standings row #144 (854 points). This session does not claim that row; the observation recorded above is the state of the 07:42Z capture that this research read against, and the other session's receipt is the current one. The six rows without a percentage are unchanged by that merge.

## 7. What is deliberately *not* claimed

* No market line was published for any of the seven rows; the 1.8/1.8 placeholders and the 0.73/0.91-spread books stay rejected.
* No percentage was derived from HLTV world ranks or EGW ratings: ranks are context, not a calibrated model, and the project's policy says so.
* The two Polymarket midpoints are recorded as **rejected observations**, not as prices.
* The mirror tier publishes a labelled **estimate**, not a market quote, and only for a club that Valve's own monthly file cannot resolve uniquely.
