# Session `86b56cf6` — Line-by-Line Forensic Audit, Hallucination Remediation & Full Site Verification

- **Date:** `2026-10-22` UTC
- **Branch:** `arena/86b56cf6-maltaproj4`
- **Live Site:** <https://buffedlizard55-lab.github.io/MaltaProj4/>
- **Machine-Readable 107-Row Audit Ledger:** `research/session-86b56cf6/audit-107-rows.json`
- **Standalone Repo & HTML Row Auditor:** `verification-86b56cf6/audit_repo_86b56cf6.py`
- **Automated Regression Suite:** `tests/test_session_86b56cf6.py`

---

## 1. Executive Summary of Board Coverage & Automation

1. **Automated Collection Cadence (`every 15 minutes` — strictly tighter than the 4–8h requirement):**
   - `.github/workflows/pages.yml` runs on cron `4,19,34,49 * * * *` (4 runs/hour = 96 runs/day) plus `.github/workflows/refresh-watchdog.yml` every 10 minutes.
   - Restored live refresh resilience in `scripts/refresh.py`: preserved the standard `requests.Response` object when `curl_cffi` fallback also receives HTTP `>=400` (e.g., persistent HTTP `403` on `gg.bet`), preventing uncaught non-`requests` `HTTPError` exceptions from halting live refreshes on `main`.
2. **Complete Open-Match Coverage (Zero Hotspawn Probability Usage):**
   - **107 total Hotspawn CS2 fixtures** (`43 open`, `64 not_open` historical/locked entries).
   - **43 / 43 open matches (`100.0%`) carry a primary-sourced pick.**
   - **41 / 43 open matches (`95.3%`) carry calibrated, mathematically reproducible win probabilities** (`22 exchange` via Polymarket Gamma API, `3 exchange_wide` via Polymarket wide-spread tier flagged low confidence, `3 bookmaker_fallback` via live Pinnacle/Winline listings, `10 model_vrs` via Valve's official `counter-strike_regional_standings` file + published `fit.js` formula and calibration slope, `3 model_vrs_mirror` via HLTV's dated `2026-10-22` Valve VRS mirror).
   - **2 / 43 open matches (`4.7%`) remain research-only (`probabilities: null`, `fair_odds: null`, never inferred or set to `50/50`)** with exact primary-source proof documented on `unresolved.html` and `review.html`:
     - **`1082925` (`BESTIA Academy vs RED Canids Academy`, `2026-10-23T19:00:00Z`)**: Pick `RED Canids Academy` (`research_rank`, HLTV `#170` vs `#184` on [HLTV 2399910](https://www.hltv.org/matches/2399910/bestia-academy-vs-red-canids-academy-cct-2026-south-america-series-7)). `BESTIA Academy` holds Valve VRS points (`#244` live / `#215` Oct 5), whereas `RED Canids Academy` has only **2 wins across 3 matches** (`1-2 Bounty Hunters`, `2-0 Sementes do Mal`, `2-0 QUINTESSÊNCIA` on `/team/13029/red-canids-academy`, fielding stand-in `FasteR` for `Nk`), below Valve's **5-win minimum** for VRS ranking (`HTTP 404` on HLTV's Valve ranking calculator). Polymarket `6036921` sits unquoted (`0.05 / 0.95`, `spread 0.90`), EGamersWorld `0U32SId-H/...-3nbNt3Gf1p` displays placeholder `1.8 / 1.8`, and Stavka.tv `23-10-2026-bestia-academy-red-canids-academy` has empty moneyline cells.
     - **`1082860` (`FlyQuest vs Staqued`, `2026-10-27T03:00:00Z`)**: Pick `FlyQuest` (`research_rank_single`, HLTV `#61` / Valve VRS `#54` vs unranked on [HLTV 2399890](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026)). `Staqued` holds a `0-4` match record (`0` wins on `/team/13997/staqued`, `HTTP 404` on HLTV's Valve calculator), and zero books or exchanges have posted odds 5 days ahead of LAN.

---

## 2. Line-by-Line Forensic Findings & Remediations

### A. `data/lineup-receipts.json` — Four Pre-Existing Corrupted Rosters Replaced from Official HLTV Match Pages
Every entry in `data/lineup-receipts.json` was verified player-for-player against live `https://www.hltv.org/matches/<id>/...` HTML fetched on `2026-10-22`:
1. **`1081869` (`Morningstar vs NEXVOID`, [HLTV 2399584](https://www.hltv.org/matches/2399584/morningstar-vs-nexvoid-macemedia-void-autumn-cup-2026))**: Replaced pre-existing unverified list `["SPine", "ExpSasiKi", "rage", "Miami", "dama"]` with official 5-man lineup `["swiftsteel", "fineshine52", "Apraki", "Freeman", "Terryyy"]` vs `["xerolte", "Zesta", "MiQ", "erkaSt", "AccuracyTG"]`.
2. **`1082769` (`K27 vs NEXORA`, [HLTV 2399846](https://www.hltv.org/matches/2399846/nexora-vs-k27-winline-mpkbk-cis-lan-season-9))**: Replaced wrong NEXORA roster `["FL4MUS", "SELLTER", "alpha", "Magnojez", "zorte"]` and stale K27 names `relaxxie, Alv` with official starters `K27: ["xeedo", "qw1nk1", "kashl1d", "X5G7V", "clax"]` vs `NEXORA: ["matusik", "torox", "hurtfrisk", "VRONSKY", "Pryan3ch"]`.
3. **`1081149` (`FORZE Reload vs LFO 10`, [HLTV 2399499](https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12))**: Replaced wrong FORZE Reload roster `["kus0k", "rexxie", "Something", "sunlight", "rik0"]` and stale `flaw` on LFO 10 with official starters `["YumsaN", "HeCkBNk", "KusMe", "Lack1", "NickelBack"]` vs `["Sapec", "L00m1", "dottie", "Mann3n", "dan1"]`.
4. **`1082860` (`FlyQuest vs Staqued`, [HLTV 2399890](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026))**: Replaced 4-player list containing wrong player `"KRAXYT"` with official 5-man lineup `["w0mbat", "xelja", "Hazel", "lzj", "kasze"]` vs `["jks", "aliStair", "INS", "nettik", "Vexite"]`.
5. **Canonical Slugs & New 5v5 Receipts (`1081597`, `1082925`, `1082926`)**: Canonicalized HLTV match slugs across all entries and added verified 5-player receipts for `1082925` ([HLTV 2399910](https://www.hltv.org/matches/2399910/bestia-academy-vs-red-canids-academy-cct-2026-south-america-series-7)) and `1082926` ([HLTV 2399911](https://www.hltv.org/matches/2399911/isurus-vs-hacha-cct-2026-south-america-series-7)).

### B. `data/book-receipts.json` — Wrong-Event / Mashup URL Fixes & Live `08:54Z` Re-Observations
1. Replaced wrong-event / mashup `rejected_listings` URLs (`zawJ-Q52S3/bestia-academy-vs-red-canids-academy-zawJ-Q52S3`, `fQ0D-T2eM/bestia-academy-vs-red-canids-academy-3nbNt3Gf1p`, `fQ0D-T2eM/isurus-gaming-vs-hacha-qgq9dKgkRU`) with the verified `CCT South America 2026 Series #7` match pages (`0U32SId-H/bestia-academy-vs-red-canids-academy-3nbNt3Gf1p` and `0U32SId-H/isurus-vs-hacha-esports-qgq9dKgkRU`) plus live `stavka.tv` and `gamma-api.polymarket.com` observations.
2. Renewed active bookmaker backup/fallback receipts from live reads at `2026-10-22T08:54:00Z`:
   - `egw-4yp_dlKtNl-nexora-k27` (`1082769`): live countdown `8:35:12` to `17:30:00Z`, odds `8.1 / 1.021`.
   - `stavka-winline-1079654-ex-zero-tenacity-ex-rustec` (`1079654`): live Winline moneyline `1.90 / 1.80` (`48.6% / 51.4%`).
   - `stavka-winline-1082919-tropa-do-kingui-martians` (`1082919`): live Winline moneyline `1.06 / 7.26`.

### C. `scripts/build.py` — 100% Official External Source Links Across All 579 Rendered Table Rows
- Added explicit per-row official source links (`HLTV result ↗` on `results_section` outcome rows and `quote_source(m['evidence'][0])` on `contrarian_screen` underdog rows in `analysis.html`), reducing rows without an external official source link across the entire 9-page site from `22` to **`0 / 579` (`100.0%` compliant across all `38` tables)**.
