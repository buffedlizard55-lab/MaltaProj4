# Session 333b053a — Live Hotspawn CS2 Refresh, 100% Open Win-Probability Coverage, & Line-by-Line Audit

**Date:** `2026-10-23` (UTC)  
**Branch:** `arena/333b053a-maltaproj4`  
**Live GitHub Pages:** <https://buffedlizard55-lab.github.io/MaltaProj4/>  

## 1. Root Cause of the Frozen Board (`2026-10-22T20:15Z` → `2026-10-23T05:00Z`)

1. Scheduled runs [39871808909](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39871808909) (`2026-10-22T23:26Z`) and [39886171791](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39886171791) (`2026-10-23T01:49Z`) failed at Step 8 (*Unit and independent failure-mode tests*) before *Refresh official sources* could run.
2. Commit `7b9180d` (`Publish the verified build to the legacy main:/ root fallback`) had staged the `2026-10-22T20:15:52Z` snapshot (`84` rows) to `main` after running `scripts.validate` and Playwright browser gates, **without re-running `python -m unittest discover -s tests -q`** against the refreshed `data/latest.json`. When fixture `1081149` (`FORZE Reload vs LFO 10`) legitimately moved from `research_rank_single` to `research_vrs_single`, two historical snapshot tests failed on subsequent runs.
3. **Permanent prevention:** In addition to replacing the pinned-tier assertions (`tests/test_session_13e99ca6.py`, `tests/test_session_75ebd2d6.py`), `.github/workflows/pages.yml` Step 15 now executes `python -m unittest discover -s tests -q` **before** `python -m scripts.publish_root_fallback` commits refreshed artifacts to `main`.

## 2. Collector & Parser Defects Uncovered and Repaired

1. **Multi-day HLTV dated discovery (`scripts/hltv.py`):** `date_views` previously interleaved `(0, +1, -1)` day offsets per fixture with `DATE_PAGE_LIMIT = 6`. With 30 open Hotspawn fixtures spanning six distinct UTC dates (`Oct 23, 24, 25, 26, 27, 31`), the first two dates consumed all 6 slots and silently dropped `selectedDate=2026-10-31` (`1082792 HOTU vs The Huns`, [HLTV 2399437](https://www.hltv.org/matches/2399437/hotu-vs-the-huns-gluck-moscow-cyber-games-2026); `1082793 5star vs 1WIN`, [HLTV 2399438](https://www.hltv.org/matches/2399438/1win-vs-5star-gluck-moscow-cyber-games-2026)). `date_views` now emits all exact `offset == 0` dates before `(1, -1)` neighbours with `DATE_PAGE_LIMIT = 14`.
2. **Integer decimal odds & pre-button `team2` binding (`scripts/books.py`):** EGamersWorld renders whole-number decimal odds without `.0` (e.g. Staqued `12` in `1.001 Make a bet 12`) and places `team2` before `Make a bet` in its current header DOM. `scripts/books.py::parse_listing` now binds integer or decimal odds (`> 1.0`) across both post-button and pre-button team labels while still rejecting `1.8/1.8` placeholders, `<= 1.0` odds, and prefix mismatches.
3. **Partial `<5`-player `hltv_team_pages` roster fallback (`scripts/refresh.py`):** `fixture_lineups` now consults verified 5-player `data/lineup-receipts.json` entries whenever an `hltv_team_pages` club page exposes fewer than 5 players (such as `LFO 10`'s 3-player club page), and `same_pair_other_start` schedule mismatches no longer emit misleading "TBA bracket slot" prose.
4. **Clean `unittest` working tree (`scripts/session_b214c818.py`):** Guarded `apply_alias()`, `apply_receipts()`, and `apply_review_notes()` against rewriting `data/identities.json` / `data/book-receipts.json` / `data/review-notes.json` when zero changes are needed.

## 3. Primary-Source Research for Non-Featured Matches (`2026-10-23T05:06–05:13Z`)

Hotspawn (`https://play.hotspawn.com/lobby`, `https://play.hotspawn.com/cs2-pickems`, and `fixtures?sport_alias=cs2&status=scheduled&tenantId=1`) lists **92 retained CS2 fixtures, 30 open for picks**. Hotspawn/HLTV crowd votes are never used.

- **19 open matches** resolve directly from **Polymarket Gamma official API** (`18` strict `exchange` + `1` labelled `exchange_wide` on `1082858 Ground Zero vs Off Chops`).
- **2 open DFRAG Invitational 2026 matches** resolve from **newly opened external bookmaker moneyline odds** verified across multiple independent sources on `2026-10-23T05:06–05:07Z`:
  - **`1082860` (`FlyQuest vs Staqued`, `2026-10-27T03:00:00Z`, Bo3):**
    - [HLTV 2399890](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026): exact pair & `03:00Z` Bo3 (`FlyQuest` `#61` / VRS `#54`, `jks, INS, Vexite, nettik, aliStair` vs `Staqued` unranked, `w0mbat, xelja, Hazel, lzj, kasze`).
    - [EGamersWorld 4kaAQWgKEx](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3): header Thunderpick **`1.001 / 12`**, plus Rainbet `1.01/11.76`, Underdog `1.01/12.01`, CocoBet `1.02/11.91`, FanDuel `1.01/12.02`, Fanatics `1.02/11.97` (book-average `1.012 / 11.945`).
    - [bo3.gg](https://bo3.gg/matches/flyquest-vs-staqued-27-10-2026): Thunderpick `1.00 / 12.00` & Prediction panel `1.001 / 12`.
    - [Polymarket 6066520](https://gamma-api.polymarket.com/markets/6066520): unquoted (`bestBid 0.07`, `bestAsk 0.95`, spread `0.88 > 0.60`), refused.
    - De-vigged `1.001 / 12`: **FlyQuest `92.3%` (`1.08`) / Staqued `7.7%` (`12.99`)** (`overround +8.23%`).
  - **`1082859` (`NEXVOID vs Alter Ego`, `2026-10-26T03:00:00Z`, Bo3):**
    - [HLTV 2399889](https://www.hltv.org/matches/2399889/nexvoid-vs-alter-ego-dfrag-invitational-2026): exact pair & `03:00Z` Bo3 (`NEXVOID` `#77` / VRS `#71` vs `Alter Ego` `#132`; `54.5%/45.5%` fan vote refused).
    - [EGamersWorld HfdcJeXmT](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/nexvoid-vs-alter-ego-HfdcJeXmT) & [bo3.gg](https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026): Thunderpick **`1.61 / 2.14`**, plus Rainbet `1.59/2.19`, Underdog `1.63/2.14`, CocoBet `1.65/2.11`, FanDuel `1.57/2.16`, Fanatics `1.6/2.12`.
    - De-vigged `1.61 / 2.14`: **NEXVOID `57.1%` (`1.75`) / Alter Ego `42.9%` (`2.33`)** (`overround +8.84%`), with Valve VRS cross-check (`68.2% / 31.8%`) shown alongside.
- **8 open matches** (`1081605`, `1082996`, `1079198`, `1079199`, `1079200`, `1082861`, `1082792`, `1082793`) have no active pre-match market line inside gates (all EGW `1.8/1.8` placeholders recorded as dated refusals in `data/book-receipts.json`) and originate probabilities from **Valve official VRS standings (`2026-10-05`)** with live HLTV match-page 5/5 lineup verification.
- **1 open match** (`1081149 FORZE Reload vs LFO 10`, `2026-10-23T08:00:00Z`) originates **`78.1% / 21.9%`** via **`model_vrs_mirror`** from [HLTV dated Valve ranking `2026-10-23`](https://www.hltv.org/valve-ranking/teams/2026/october/23) (`#79` `1133 pts` vs `#151` `820 pts`) and [HLTV 2399499](https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12), while EGW's unnamed-opponent `1.8/1.8` page and Stavka's `14:00Z Sökerorg` conflict are refused and flagged on `review.html`.
