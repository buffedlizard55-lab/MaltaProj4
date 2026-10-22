# Session `7271c5d5` — Complete 2026-10-22 CS2 Pick'em Coverage, Primary-Source Line Research & Line-by-Line Verification Report

## 1. Executive Summary

- **Repository & Working Branch:** `buffedlizard55-lab/MaltaProj4` · branch `arena/7271c5d5-maltaproj4`
- **Live Board Audited (`data/latest.json`):** `generated_at = 2026-10-22T01:28:24.176572Z`, `fixtures_observed_at = 2026-10-22T01:24:39.442268Z` (**97 total CS2 feed rows**: **35 open scheduled matches** + **62 completed/locked matches**).
- **Zero Crowd-Percentage Policy Verified:** `0` Hotspawn fan-vote fields (`picked*`, `total_picks`) retained anywhere in `fixture_evidence`; `0` HLTV/Strafe/EGW fan vote bars used anywhere; `0` synthetic `50/50` or `1.8/1.8` placeholder odds converted into win probabilities.
- **Open Match Coverage (Before vs After Session `7271c5d5` Upgrade):**
  - **Picks published:** **35 / 35 open CS2 matches (`100.0%`)** — **0 unresolved matches lacking a pick**.
  - **Verified numerical win probabilities:** **upgraded from `28 / 35` (`80.0%`) to `29 / 35` (`82.9%`)** via verified bookmaker receipt `egw-4yp_dlKtNl-nexora-k27` for **`1082769` `K27 vs NEXORA` (`2026-10-22T17:30:00Z`, `CIS LAN Championship #9` Quarterfinal 3 Bo3 -> `K27 88.8% / NEXORA 11.2%`, fair decimal odds `1.13 / 8.93`)**, corroborated across four independent primary sources.
  - **Remaining non-numeric research-only picks:** **6 / 35 open matches (`17.1%`)** (`1081869`, `1081597`, `1079654`, `1081149`, `1081150`, `1082860`) — every single one verified across **Polymarket CLOB**, **Pinnacle Arcadia**, **Picklebet AU**, **EGamersWorld**, **Stavka TV**, **HLTV match/bracket/Valve-ranking pages**, and **Valve's official VRS repository** to have **zero open pre-match moneyline quotes** at audit time (`01:05–01:35 UTC`). Unverifiable probabilities are deliberately kept blank (`null`) rather than fabricated.
- **All 97 Rows Line-by-Line Ledger:** See [`research/session-7271c5d5/LINE-BY-LINE-AUDIT.md`](LINE-BY-LINE-AUDIT.md) (`97 / 97` rows verified, `0` errors).

---

## 2. Newly Priced Open Fixture: `1082769` `K27 vs NEXORA` (`K27 88.8% / NEXORA 11.2%`)

On the `00:55Z` and `01:28Z` boards, `1082769` (`K27 vs NEXORA`, `2026-10-22T17:30:00Z`, `CIS LAN Championship #9` Quarterfinal 3, Bo3) lacked a percentage (`research_rank_single`, `pick: K27`, `probabilities: null`). Line-by-line multi-source investigation uncovered **four independent primary sources** confirming both identity and market pricing:

| Source | Official URL | Raw Quote / Fact | Fair Implied Win Prob. (`K27` / `NEXORA`) | Role in Pipeline |
| --- | --- | --- | --- | --- |
| **EGamersWorld live match page** | `https://egamersworld.com/counterstrike/match/4yp_dlKtNl/nexora-vs-k27-U_TH-dVYT` | `NEXORA 8.1 Make a bet 1.021 K27` + `EGWxxxBOT` summary (`1.021 / 8.1`, `+10.29%` margin), `startDate: 2026-10-22T17:30:00Z`, Bo3 | **88.8% / 11.2%** (`1.13 / 8.93`) | **Primary receipt `egw-4yp_dlKtNl-nexora-k27`** in `data/book-receipts.json` (auto-reobservable every 15 min via `scripts/books.py`) |
| **Stavka TV match header (Betcity / Melbet)** | `https://stavka.tv/matches/csgo/22-10-2026-nexora-k27` | Named licensed operators: `П1 7.80` (**Betcity** on `NEXORA`) / `П2 1.06` (**Melbet** on `K27`), `+7.16%` margin; CS2 schedule row `8.10 / 1.02` | **88.0% / 12.0%** *(schedule: `88.8% / 11.2%`)* | Independent named-sportsbook corroboration within **0.77 pp** |
| **Polymarket CLOB Gamma API (`6029909`)** | `https://gamma-api.polymarket.com/markets/6029909` (`cs2-nexora-k271-2026-10-22`) | Active series moneyline: `outcomes: ["NEXORA", "K27"]`, `outcomePrices: ["0.24", "0.76"]`, `liquidity: $151.01`, `bestBid: 0.04`, `bestAsk: 0.44` (`spread: 0.40`), `updatedAt: 2026-10-22T01:04:56Z` | **76.0% / 24.0%** | Live funded exchange corroboration; automatically excluded only because PandaScore sets `gameStartTime = 16:00:00Z` vs HLTV/Hotspawn `17:30:00Z` |
| **HLTV Match `2399846` & Valve Ranking** | `https://www.hltv.org/matches/2399846/k27-vs-nexora-cis-lan-championship-9` · `https://www.hltv.org/valve-ranking/teams/2026/october/20` | Exact Quarterfinal 3 Bo3 at `2026-10-22T17:30:00Z`; lineups `xeedo, relaxxie, kashl1d, X5G7V, Alv` vs `FL4MUS, SELLTER, alpha, Magnojez, zorte`; HLTV `#37` / Valve `#32` (`1392` pts) vs Valve `#279` (`595` pts) | Directional confirmation (`+797` VRS pts) | Primary identity, lineup, and VRS corroboration |

---

## 3. Forensic Investigation of All 6 Remaining Non-Numeric Open Matches & Data Repairs

Every open fixture that remains without a percentage after `egw-4yp_dlKtNl-nexora-k27` was checked across HLTV first, then Polymarket, Pinnacle, Picklebet AU, EGamersWorld, Stavka TV, and Valve's official VRS files:

1. **`1081597` — `benched gods vs TitanFlow` (`2026-10-22T11:00:00Z`, `CCT Europe 2026 Challengers #8` LB R3) -> Pick `benched gods` (`research_vrs_single`, blank `%`)**
   - **5-Source Bracket Irregularity Solved:**
     - HLTV event page `https://www.hltv.org/events/9453/cct-2026-challengers-europe-series-8` confirms: LB Round 1 `ex-6666 1-0 MORROW` (`MORROW` eliminated) -> LB Round 2 match `2399691` `benched gods 1-0 ex-6666` (`Default 1-0` forfeit win: *"benched gods won by default"*) + match `2399692` `TitanFlow 2-0 Noir Verse` (`13-9 Dust2, 13-11 Inferno`).
     - Yet HLTV slot `2399696` (`https://www.hltv.org/matches/2399696/cct-challengers-lb-r3-m1-cct-2026-challengers-europe-series-8`) still displays `TBA vs TBA — Match postponed`, while Polymarket market `6028868` (`https://gamma-api.polymarket.com/markets/6028868`, `cs2-morrow-titanf-2026-10-22`, `11:00:00Z`) falsely seeded eliminated LB R1 loser `MORROW` opposite `TitanFlow` with an unquoted `0.87` spread (`0.08 / 0.95`), and EGW (`https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn`) displays `1.8 / 1.8`.
   - **Repository Bug Repaired (`data/lineup-receipts.json` & `data/book-receipts.json`):** Corrected an earlier session's fabricated prose claim `"benched gods 2-1 ex-6666 in match 2399691"` in `data/lineup-receipts.json` to the true official HLTV `1-0` default forfeit record, and replaced PR #119's synthetic `/match/CCTEU8/...` and `/match/DFRAG26/...` URLs in `data/book-receipts.json` with verified canonical opaque EGW URLs.

2. **`1079654` — `ex-Zero Tenacity vs ex-RUSTEC` (`2026-10-23T08:00:00Z`, `CCT Europe 2026 Series #11`) -> Pick `ex-Zero Tenacity` (`research_rank`, blank `%`)**
   - **Primary Lineups (`HLTV 2399331`):** `Dragon, Kind0, VLDN, brutmonster, Cjoffo` vs `youka, bl1x1, yiksrezo, Brilliance, jakekeS`.
   - **Exact Valve VRS Dual-Tie & Rank-Inversion Proof:** In `data/vrs/standings_global_2026_10_05.md`, `ex-RUSTEC`'s 5-man lineup shares **3/5 players** with **both** row `#92` (`1066` pts) and row `#152` (`824` pts), triggering `scripts/vrs.py`'s strict tie refusal (`3 == 3`); moreover row `#93 ex-Zero Tenacity` is also `1066` pts (`expected(1066, 1066) = 50.0% / 50.0%`), whereas HLTV World Ranking prefers `ex-Zero Tenacity` (`#67` vs `#70`) and HLTV's `2026-10-20` Valve ranking prefers `ex-RUSTEC` (`#91`, `1068` pts vs `#96`, `1051` pts). Both EGW (`_rW8GEyWK/ex-zero-tenacity-vs-ex-rustec-YieSsHTBr`, `1.8/1.8`) and Stavka (`23-10-2026-ex-zero-tenacity-ex-rustec`, `---`) have no open moneyline.

3. **`1081150` — `ex-RUSTEC vs Saint Sinners` (`2026-10-23T17:00:00Z`, `CCT Europe 2026 Series #12`) -> Pick `ex-RUSTEC` (`research_rank`, blank `%`)**
   - **Primary Lineups (`HLTV 2399500`):** `ex-RUSTEC` (`youka, bl1x1, yiksrezo, Brilliance, jakekeS`, HLTV `#70`) vs `Saint Sinners` (`deb0, Caleyy, pavlysha666, iRV1NG, halfjix`, HLTV `#143`, Valve `#158` `810` pts `4/5` core). Refused in `model_vrs` solely by `ex-RUSTEC`'s `3 == 3` overlap tie across Valve `#92` and `#152`; EGW (`1.8/1.8`) and Stavka (`---`) carry no moneyline yet.

4. **`1081869` — `Morningstar vs NEXVOID` (`2026-10-22T03:00:00Z`, `VOID Autumn Cup 2026`) -> Pick `NEXVOID` (`research_rank_single`, blank `%`)**
   - **Primary Lineups (`HLTV 2399584`):** `SPine, ExpSasiKi, rage, Miami, dama` (unranked HLTV, absent from global & Asia Valve standings) vs `erkaSt, xerolte, MiQ, AccuracyTG, Zesta` (`NEXVOID`, HLTV `#59`, Valve `#71` `1169` pts `5/5`). EGW (`1.8/1.8`) and Stavka (`---`; historical capper slips `Morningstar @ 4.80` never used as live line) publish no open moneyline.

5. **`1081149` — `FORZE Reload vs LFO 10` (`2026-10-23T14:00:00Z`, `CCT Europe 2026 Series #12`) -> Pick `FORZE Reload` (`research_rank_single`, blank `%`)**
   - **Primary Lineups (`HLTV 2399499`):** `kus0k, rexxie, Something, sunlight, rik0` (`FORZE Reload`, HLTV `#74`, Valve `#85` `1100` pts) vs `L00m1, Sapec, flaw, dottie, Mann3n` (`LFO 10`, unranked HLTV, absent from `2026-10-05` Valve file; `<= 2/5` overlap with `#156 Entropy`). EGW shows `1.8/1.8` against a blank opponent label; no book quotes posted yet.

6. **`1082860` — `FlyQuest vs Staqued` (`2026-10-27T03:00:00Z`, `DFRAG Invitational 2026`) -> Pick `FlyQuest` (`research_rank_single`, blank `%`)**
   - **Primary Lineups (`HLTV 2399890`):** `jks, aliStair, INS, nettik, Vexite` (`FlyQuest`, HLTV `#61`, Valve `#86` `1093` pts) vs `KRAXYT, w0mbat, lzj, xelja` + 1 TBA (`Staqued`, unranked HLTV & absent from global/Asia Valve standings). EGW shows `1.8/1.8`; unposted across all books 5 days before start.

---

## 4. Cross-Venue Audit Highlights Across Priced Open Matches

- **`1079650` `GenOne vs Spirit Academy` (`2026-10-22T08:00:00Z`):** Polymarket `6028795` (`exchange_wide`) prices `Spirit Academy 65.0% / GenOne 35.0%`, inverting two-team Valve VRS (`GenOne 70.6% / Spirit Academy 29.4%`, a **35.6 pp** divergence already surfaced automatically on the row card via `favourite differs`).
- **`1082689` `BESTIA vs ShindeN` (`2026-10-22T14:00:00Z`):** Near-coin-flip cross-venue split — Polymarket `5972071` slightly favors `ShindeN 52.5%`, whereas Picklebet AU (`BESTIA 1.82 vs ShindeN 1.88` -> `BESTIA 50.8%`), Stavka (`1.84 vs 1.88` -> `BESTIA 50.5%`), and Valve VRS (`BESTIA 57.5%`) lean slightly to `BESTIA`.
- **Strong Multi-Book Confirmation on Remaining Priced Rows:** `1081870` (`Rare Atom 71.5%` Polymarket vs `63.8%` Stavka vs `69.0%` VRS), `1079189` (`FORZE Reload 66.5%` Polymarket vs `65.0%` Picklebet AU), `1082688` (`Imperial 77.5%` Polymarket vs `75.7%` Picklebet AU vs `75.3%` Stavka vs `73.8%` VRS), `1082882` (`Apogee Betclic 60.0%` Polymarket vs `61.0%` Picklebet AU vs `60.5%` Stavka), and `1082770` (`Virtus.pro 60.4%` Pinnacle vs `63.3%` VRS) all agree in favorite and magnitude.

---

## 5. Verification, Mobile UX & Automation Cadence Summary

- **Automated Refresh Cadence:** `.github/workflows/pages.yml` runs every 15 minutes (`4,19,34,49 * * * *`) backed by `.github/workflows/refresh-watchdog.yml` (`*/10 * * * *`), comfortably inside the required 4–8 hour window with client-side + server-side 8-hour evidence expiry withholding.
- **Mobile & Executive Summary Audit (`verification-7271c5d5/audit_board_7271c5d5.py`):** Verified `index.html` links directly to `picks.html`, `unresolved.html`, `#unresolved-summary`, `matches.html`, and `review.html`, includes thumb-sized phone navigation (`nav.mobile-tabs`), displays all open picks with explicit model/research badges and limitations, and passes with **97/97 rows verified, 10 pages, 875 internal links/assets, 276 rendered match table rows, and 0 errors**.
