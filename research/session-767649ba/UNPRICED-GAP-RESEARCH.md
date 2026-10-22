# Session `767649ba` — HLTV-First & Esportsbook Research Across All Seven 2026-10-22 Unpriced Fixtures

**Captured UTC Window:** `2026-10-22T01:07:00Z` – `2026-10-22T01:20:00Z`
**Strict Ordering Applied:**
1. Hotspawn (`play.hotspawn.com/lobby`, `play.hotspawn.com/cs2-pickems`, `/api/v2/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`) strictly for fixture inventory and lock times — **never** crowd votes or pick percentages.
2. Polymarket Gamma CS2 whole-match moneyline (`$100` floor, `<=0.25` spread / `<=0.60` wide, `<=8h` freshness).
3. HLTV match page first (`www.hltv.org/matches/<id>/...`) for official schedule status, format, world ranks, and 5-man lineups, paired with Valve's official `standings_global_2026_10_05.md` (`>=3/5` unique core continuity -> calibrated logistic `model_vrs`).
4. External esportsbooks & odds panels (`Pinnacle`, `EGamersWorld`, `СТАВКА ТВ`, `KushVSporte`) with strict rejection of symmetric `1.8 / 1.8` placeholders, sub-`$100` books, map totals, and exact-score props.

---

## Executive Summary of Findings

Out of **35 open CS2 fixtures** on the live `2026-10-22` board (`28` already carrying verified two-sided win probabilities and `7` lacking win probabilities):

- **`1` open fixture (`1082769` `K27 vs NEXORA`, `2026-10-22T17:30:00Z`, CIS LAN Season 9 Quarter-final)** has **live, corroborated, asymmetric two-way bookmaker odds across three independent CIS panels** and is **upgraded to a verified `bookmaker_fallback` probability (`K27 88.8% / NEXORA 11.2%`, fair odds `1.13 / 8.93`)** via primary receipt `egw-4yp_dlKtNl-nexora-k27` in `data/book-receipts.json` ( raising live priced open coverage from **`28 / 35` (`80.0%`) to `29 / 35` (`82.9%`)**).
- **`6` open fixtures (`1081869`, `1081597`, `1079654`, `1081149`, `1081150`, `1082860`)** genuinely carry **zero valid two-way moneyline odds across every checked market and esportsbook** (`1.8 / 1.8` placeholders or blank `П1/П2` cells) AND **cannot be priced honestly by `model_vrs` without guessing**. Each retains its verified directional pick with `probabilities = null` (`—`), fresh `2026-10-22T01:08Z–01:14Z` rejected-listing receipts in `data/book-receipts.json`, and full visibility on `unresolved.html` and `review.html`.
- **Three broken non-canonical placeholder URLs (`CCTEU8/...`, `DFRAG26/...`)** previously stored in `data/book-receipts.json` were discovered and repaired to their live HTTP-200 canonical `egamersworld.com` match URLs.

---

## Fixture-by-Fixture Primary Source Audit

### 1. `1082769` — **K27 vs NEXORA** (`2026-10-22T17:30:00Z`, Bo3 LAN) -> **UPGRADED TO `88.8% / 11.2%`**
- **HLTV primary page:** <https://www.hltv.org/matches/2399846/nexora-vs-k27-winline-mpkbk-cis-lan-season-9>
  - Event: *Winline MPKBK CIS LAN Season 9* Quarter-final (LAN, Best of 3), exact UTC kickoff `2026-10-22T17:30:00Z`.
  - **K27** (`team/12895`, HLTV World `#46`, live Valve `#31`, Oct 5 Valve `#32` `1435` pts): `xeedo, qw1nk1, kashl1d, X5G7V, clax`.
  - **NEXORA** (`team/14002`, HLTV Unranked, live Valve `#282`, absent from Oct 5 Valve global file): `matusik, torox, hurtfrisk, VRONSKY, Pryan3ch`.
- **Esportsbook two-way moneyline corroboration (`2026-10-22T01:12Z–01:13Z`):**
  1. **Accepted primary single-page receipt (`egw-4yp_dlKtNl-nexora-k27`):** <https://egamersworld.com/counterstrike/match/4yp_dlKtNl/nexora-vs-k27-U_TH-dVYT> — matches exact `2026-10-22T17:30:00Z` UTC kickoff to the second (`countdown 16:17:42` at `01:12:18Z`), quotes **`NEXORA 8.1` / `K27 1.021`** (confirmed verbatim in page summary text), `overround = +10.29%` -> de-margined **`K27 88.8061%` (`88.8%`) / `NEXORA 11.1939%` (`11.2%`)**, fair odds `1.126 / 8.933`.
  2. **Corroboration #1 (`СТАВКА ТВ` named operators):** <https://stavka.tv/matches/csgo/22-10-2026-nexora-k27> — `Betcity П1 (NEXORA) = 7.80`, `Melbet П2 (K27) = 1.06`, `overround = +7.16%` -> de-margined **`K27 88.04% / NEXORA 11.96%`** (**`0.77` pp difference**; kept as corroboration rather than primary receipt because the Stavka header prints stale `12:00` MSK instead of official `20:30` MSK / `17:30Z`).
  3. **Corroboration #2 (`KushVSporte`):** <https://kushvsporte.ru/event/6993380-k27-nexora> — `K27 1.04 / NEXORA 8.20`, `overround = +8.35%` -> de-margined **`K27 88.74% / NEXORA 11.26%`** (**`0.07` pp difference**).
  4. **Corroboration #3 & #4 (`Vave` named operator + `2026-10-22` Valve VRS):** Direct Vave sportsbook feed quotes identical `1.021 / 8.10` (`88.81% / 11.19%`), and 22 Oct Valve VRS ratings (`K27 1396 pts` vs `NEXORA 596 pts`, Glicko `RD=75` + `0.7986` calibration) independently yield **`K27 88.5%`** (within **`0.3` pp** across all five independent sources).

### 2. `1081869` — **Morningstar vs NEXVOID** (`2026-10-22T03:00:00Z`, Bo3) -> **Research Pick `NEXVOID` (`—`)**
- **HLTV primary page:** <https://www.hltv.org/matches/2399584/morningstar-vs-nexvoid-macemedia-void-autumn-cup-2026> — *MaceMedia Void Autumn Cup 2026* Grand Final; **NEXVOID** (`#77` HLTV, `#113` Oct 5 Valve `995` pts: `tuvshuu, tugu, MagnumZ, shinobi, Clouden`) vs **Morningstar** (HLTV Unranked, `0 / 380` rows in Oct 5 Valve standings: `suki, yuhan, rage, BZA, z8z`).
- **Esportsbooks checked (`01:14Z`):** <https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/morningstar-vs-nexvoid-e_MT2tamL> serves symmetric `1.8 / 1.8` placeholder `<2h` pre-lock; Polymarket, Pinnacle, and `stavka.tv` list no market. Honest outcome: **`NEXVOID`** (`research_rank_single`), no `%`.

### 3. `1081597` — **benched gods vs TitanFlow** (`2026-10-22T11:00:00Z`, Bo3) -> **Research Pick `benched gods` (`—`)**
- **HLTV primary page:** <https://www.hltv.org/matches/2399696/cct-2026-challengers-europe-series-8-lower-bracket-round-3-2-cct-2026-challengers-europe-series-8> — marked **`Match postponed`** with undecided `TBA` bracket slots on HLTV; **benched gods** holds Oct 5 Valve `#157` (`811` pts: `FinigaN, Magnojez, SELLTER, alpha, syph0` verified via `data/vrs-anchors.json`), whereas **TitanFlow** (`Sdaim, sh1nejezzz, Pipw, lollipop21k, ArtFr0st`, HLTV match `2399692`) is absent from Oct 5 Valve standings.
- **Esportsbooks checked (`01:08Z`):** Live canonical <https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn> serves `1.8 / 1.8` placeholder; Polymarket, Pinnacle, and `stavka.tv` list no market. Honest outcome: **`benched gods`** (`research_vrs_single`), no `%`.

### 4. `1079654` — **ex-Zero Tenacity vs ex-RUSTEC** (`2026-10-23T08:00:00Z`, Bo3) -> **Research Pick `ex-Zero Tenacity` (`—`)**
- **HLTV primary page:** <https://www.hltv.org/matches/2399331/ex-zero-tenacity-vs-ex-rustec-european-pro-league-series-8> — **ex-Zero Tenacity** (`#67` HLTV, `#93` Oct 5 Valve `1066` pts: `aVN, Cjoffo, nEMANHA, Brutmonster, maden`) vs **ex-RUSTEC** (`#70` HLTV: `youka, bl1x1, yiksrezo, Brilliance, jakekeS`).
- **Exact Valve VRS proof:** In `data/vrs/standings_global_2026_10_05.md`, `ex-RUSTEC`'s 5-man lineup shares **3 players (`bl1x1, jakekeS, youka`)** with `#92 RUSTEC` (`1066` pts) **AND 3 players (`Brilliance, jakekeS, yiksrezo`)** with `#152 ex-RUSTEC` (`824` pts). `scripts/vrs.py` strictly rejects `3 == 3` ties rather than guessing which VRS row owns the roster (and `#92` vs `#93` would be `1066 == 1066` = `50/50` coin flip!).
- **Esportsbooks checked (`01:13Z–01:14Z`):** <https://egamersworld.com/counterstrike/match/_rW8GEyWK/ex-zero-tenacity-vs-ex-rustec-YieSsHTBr> serves `1.8 / 1.8`; <https://stavka.tv/matches/csgo/23-10-2026-ex-zero-tenacity-ex-rustec> leaves `П1 / П2` blank (only Totals `Over 2.5 @ 1.88` / Exact Score `2:1 @ 3.25`). Honest outcome: **`ex-Zero Tenacity`** (`research_rank`), no `%`.

### 5. `1081149` — **FORZE Reload vs LFO 10** (`2026-10-23T14:00:00Z`, Bo3) -> **Research Pick `FORZE Reload` (`—`)**
- **HLTV primary page:** <https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12> — **FORZE Reload** (`#80` HLTV, `#84` Oct 5 Valve `1100` pts: `kus0k, shady, spirit, rikon, rexxie`) vs **LFO 10** (HLTV Unranked; fielding 3 substitutes `Sapec, L00m1, dottie, Mann3n, dan1`).
- **Exact Valve VRS proof:** Across all 380 rows of `standings_global_2026_10_05.md`, `LFO 10`'s lineup overlaps at most **`2 / 5` players** (`dottie, Sapec` on `#156 Entropy`, `813` pts), strictly below Valve's `3/5` core continuity rule (`ROSTER_OVERLAP = 3`).
- **Esportsbooks checked (`01:14Z`):** <https://egamersworld.com/counterstrike/match/HiXMAaC8L/forze-reload-vs-_04jKZ07_4> shows `1.8 / 1.8` + unnamed opponent; `stavka.tv` returns `404`. Honest outcome: **`FORZE Reload`** (`research_rank_single`), no `%`.

### 6. `1081150` — **ex-RUSTEC vs Saint Sinners** (`2026-10-23T17:00:00Z`, Bo3) -> **Research Pick `ex-RUSTEC` (`—`)**
- **HLTV primary page:** <https://www.hltv.org/matches/2399500/ex-rustec-vs-saint-sinners-cct-2026-europe-series-12> — **ex-RUSTEC** (`#70` HLTV) vs **Saint Sinners** (`#123` HLTV, `#162 RUSH B` `801` pts via `4/5` core `executor, kinqie, z1NNY, k1n`). Same `3 == 3` Valve tie blocks numeric VRS pricing on `ex-RUSTEC`.
- **Esportsbooks checked (`01:13Z–01:14Z`):** <https://egamersworld.com/counterstrike/match/HiXMAaC8L/ex-rustec-vs-saint-sinners-qRkeIZuchq> shows `1.8 / 1.8`; <https://stavka.tv/matches/csgo/23-10-2026-ex-rustec-saint-sinners> leaves `П1 / П2` blank. Honest outcome: **`ex-RUSTEC`** (`research_rank`), no `%`.

### 7. `1082860` — **FlyQuest vs Staqued** (`2026-10-27T03:00:00Z`, Bo3) -> **Research Pick `FlyQuest` (`—`)**
- **HLTV primary page:** <https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026> — **FlyQuest** (`#61` HLTV, `#86` Oct 5 Valve `1093` pts: `INS, Vexite, nettik, story, jks`) vs **Staqued** (HLTV Unranked, absent from Valve standings: `w0mbat, xelja, Hazel, lzj, kasze`). Note: HLTV's `95%` Major Regional Invite simulation figure for FlyQuest is **not** a match win probability and is strictly excluded.
- **Esportsbooks checked (`01:14Z`):** Live canonical <https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3> shows `1.8 / 1.8` five days pre-event; Polymarket, Pinnacle, and `stavka.tv` carry no line. Honest outcome: **`FlyQuest`** (`research_rank_single`), no `%`.
