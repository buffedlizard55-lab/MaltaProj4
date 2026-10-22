# Session `7601d5ee` — 2026-10-22 Hotspawn CS2 Board Audit, HLTV / 22 Oct Valve VRS Deep Dive & Bookmaker Line Verification

- **Session ID**: `7601d5ee`
- **Branch**: `arena/7601d5ee-maltaproj4`
- **Audit Window (UTC)**: `2026-10-22T01:14:11Z` – `2026-10-22T01:30:00Z`
- **Board Snapshot Audited**: `2026-10-22T01:28:24.176572Z` (`97` total CS2 fixtures, `35` open, `62` non-open historical rows)

---

## 1. Executive Summary of the 2026-10-22 Board

All **97** Counter-Strike 2 fixtures returned by Hotspawn's API (`https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`) and hydrated on `https://play.hotspawn.com/cs2-pickems` and `https://play.hotspawn.com/lobby` are accounted for on the published board:

| Category | Count | Details |
|---|---:|---|
| **Total CS2 Fixtures Retained** | **97** | `api: 97`, `page: 97`, `lobby: 97`, `retained: 97`, `fixture_conflicts: 0` |
| **Open Matches (`state: open`)** | **35** | **35 / 35 resolved with a pick (100% open-match pick coverage)** |
| **Priced Open Matches** | **28** | **8 Polymarket** (`7 exchange` + `1 exchange_wide`), **1 Pinnacle** (`bookmaker_fallback`), **19 Valve VRS model** (`model_vrs`) |
| **Research-Only Open Picks** | **7** | **4 `research_rank_single`**, **2 `research_rank`**, **1 `research_vrs_single`** — probabilities and fair odds intentionally left blank (`—`) and flagged on `review.html` |
| **Unresolved Open Matches** | **0** | Listed in `unresolved.html` alongside the 7 research-only unpriced picks and full per-provider attempt logs |
| **Non-Open Historical Rows** | **62** | Retained in `matches.html` (`All matches`) with sourced start/lock timestamps and excluded from future picks |

---

## 2. All 28 Priced Open Matches (De-Vigged Market & Calibrated Valve VRS Model Lines)

### 2A. Polymarket Exchange Lines (`8` matches: `7 exchange` + `1 exchange_wide`)

| Hotspawn ID | Match | Competition | Start (UTC) | Method | Pick | Probabilities (`T1 / T2`) | Fair Odds (`T1 / T2`) | Source |
|---|---|---|---|---|---|---|---|---|
| `1081870` | **Vitalem Aerem vs Rare Atom** | VOID Autumn Cup 2026 | `2026-10-22T05:00:00Z` | `exchange` | **Rare Atom** | `28.5% / 71.5%` | `3.51 / 1.40` | [Polymarket 6024922](https://polymarket.com/event/cs2-va-ra1-2026-10-22) |
| `1079650` | **GenOne vs Spirit Academy** | CCT Europe 2026 Series #11 | `2026-10-22T08:00:00Z` | `exchange_wide` | **Spirit Academy** | `35.0% / 65.0%` | `2.86 / 1.54` | [Polymarket 6044807](https://polymarket.com/event/cs2-gen-sa2-2026-10-22) |
| `1079189` | **FORZE Reload vs Just Players** | NODWIN Clutch Series #13 | `2026-10-22T11:00:00Z` | `exchange` | **FORZE Reload** | `66.5% / 33.5%` | `1.50 / 2.99` | [Polymarket 6044572](https://polymarket.com/event/cs2-fr-jp1-2026-10-22) |
| `1081598` | **JiJieHao vs Nexus** | DraculaN Season 7 | `2026-10-22T13:00:00Z` | `exchange` | **JiJieHao** | `61.5% / 38.5%` | `1.63 / 2.60` | [Polymarket 6002749](https://polymarket.com/event/cs2-jjh1-nex-2026-10-22) |
| `1082688` | **Imperial vs Turma do Pagode** | Circuit X Curitiba #4 | `2026-10-22T14:00:00Z` | `exchange` | **Imperial** | `77.5% / 22.5%` | `1.29 / 4.44` | [Polymarket 6019822](https://polymarket.com/event/cs2-imp-tdp-2026-10-22) |
| `1082689` | **BESTIA vs ShindeN** | Circuit X Curitiba #4 | `2026-10-22T14:00:00Z` | `exchange` | **ShindeN** | `47.5% / 52.5%` | `2.11 / 1.90` | [Polymarket 6019809](https://polymarket.com/event/cs2-bst-shn-2026-10-22) |
| `1082882` | **UNiTY vs Apogee Betclic** | Stake Ranked Ep. 6 CQ | `2026-10-22T14:00:00Z` | `exchange` | **Apogee Betclic** | `40.0% / 60.0%` | `2.50 / 1.67` | [Polymarket 6034572](https://polymarket.com/event/cs2-unt1-bae-2026-10-22) |
| `1082180` | **Sangal vs Metizport** | DraculaN Season 7 | `2026-10-22T16:30:00Z` | `exchange` | **Sangal** | `53.5% / 46.5%` | `1.87 / 2.15` | [Polymarket 6024603](https://polymarket.com/event/cs2-san-met-2026-10-22) |

### 2B. Pinnacle Bookmaker Line (`1` match: `bookmaker_fallback`)

| Hotspawn ID | Match | Competition | Start (UTC) | Method | Pick | Raw Moneyline | Probabilities (`T1 / T2`) | Fair Odds (`T1 / T2`) | Source |
|---|---|---|---|---|---|---|---|---|---|
| `1082770` | **UPGRADE vs Virtus.pro** | CIS LAN Championship #9 | `2026-10-22T20:30:00Z` | `bookmaker_fallback` | **Virtus.pro** | `+135 / -184` (`2.35 / 1.5435`, margin `7.34%`) | `39.6% / 60.4%` | `2.52 / 1.66` | [Pinnacle 1638942910](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight) |

### 2C. Originated Valve VRS Model Lines (`19` matches: `model_vrs`)

All 19 `model_vrs` rows are computed deterministically from `data/vrs/standings_global_2026_10_05.md` (`RD = 400`, `SLOPE = 0.7791`, `K = 0.004`):

| Hotspawn ID | Match | Start (UTC) | 2026-10-05 VRS Standings & Points | Probabilities (`T1 / T2`) | Fair Odds (`T1 / T2`) | Pick |
|---|---|---|---|---|---|---|
| `1079188` | **Bushido Wildcats vs ex-6666** | `2026-10-22T08:00:00Z` | `#114 Bushido Wildcats (982)` vs `#127 6666 (923)` | `56.5% / 43.5%` | `1.77 / 2.30` | **Bushido Wildcats** *(see §3B: Vave `2.26/1.55` & 22 Oct VRS `#121 vs #117` favour `ex-6666`)* |
| `1081143` | **BakS vs Azuolas** | `2026-10-22T08:00:00Z` | `#100 BAKS (1044)` vs `#140 Azuolas (863)` | `68.7% / 31.3%` | `1.46 / 3.19` | **BakS** |
| `1079651` | **Butterfly vs Lavked** | `2026-10-22T11:00:00Z` | `#88 Butterfly (1082)` vs `#143 Lavked (862)` | `71.9% / 28.1%` | `1.39 / 3.56` | **Butterfly** |
| `1081596` | **Falcons Force vs Phantom Academy** | `2026-10-22T11:00:00Z` | `#161 Falcons Force (806)` vs `#172 Phantom Academy (783)` | `52.6% / 47.4%` | `1.90 / 2.11` | **Falcons Force** |
| `1082767` | **Nemesis vs WW** | `2026-10-22T11:30:00Z` | `#29 Nemesis (1455)` vs `#108 WW (1023)` | `83.4% / 16.6%` | `1.20 / 6.02` | **Nemesis** |
| `1081600` | **Donstu vs Banda chuya** | `2026-10-22T13:45:00Z` | `#197 DONSTU (732)` vs `#165 Banda Chuya (801)` | `42.4% / 57.6%` | `2.36 / 1.74` | **Banda chuya** |
| `1079652` | **Acend vs ex-6666** | `2026-10-22T14:00:00Z` | `#63 Acend (1197)` vs `#127 6666 (923)` | `75.8% / 24.2%` | `1.32 / 4.13` | **Acend** |
| `1081145` | **Lavked vs HAVU** | `2026-10-22T14:00:00Z` | `#143 Lavked (862)` vs `#124 HAVU (937)` | `41.7% / 58.3%` | `2.40 / 1.71` | **HAVU** |
| `1079653` | **Rune Eaters vs FORZE Reload** | `2026-10-22T17:00:00Z` | `#81 Rune Eaters (1110)` vs `#84 FORZE Reload (1100)` | `51.1% / 48.9%` | `1.96 / 2.05` | **Rune Eaters** |
| `1081146` | **6yuBoJlbl vs ex-6666** | `2026-10-22T17:00:00Z` | `#110 6yuBoJlbl (1015)` vs `#127 6666 (923)` | `60.1% / 39.9%` | `1.66 / 2.51` | **6yuBoJlbl** |
| `1081871` | **Lynn Vision vs Chinggis Warriors** | `2026-10-23T03:00:00Z` | `#64 Lynn Vision (1190)` vs `#87 Chinggis Warriors (1084)` | `61.5% / 38.5%` | `1.63 / 2.60` | **Lynn Vision** |
| `1079655` | **Nuclear TigeRES vs ILLYRIANS** | `2026-10-23T11:00:00Z` | `#46 Nuclear TigeRES (1324)` vs `#141 Illyrians (862)` | `84.3% / 15.7%` | `1.19 / 6.39` | **Nuclear TigeRES** |
| `1081148` | **Inner Circle Academy vs Spirit Academy** | `2026-10-23T11:00:00Z` | `#94 Inner Circle Academy (1064)` vs `#115 Spirit Academy (981)` | `59.1% / 40.9%` | `1.69 / 2.45` | **Inner Circle Academy** |
| `1079657` | **BakS vs BRUTE** | `2026-10-23T17:00:00Z` | `#100 BAKS (1044)` vs `#75 BRUTE (1116)` | `42.1% / 57.9%` | `2.38 / 1.73` | **BRUTE** |
| `1082858` | **Ground Zero vs Off Chops** | `2026-10-26T03:00:00Z` | `#136 Ground Zero (878)` vs `#119 THUNDER dOWNUNDER (971)` | `39.8% / 60.2%` | `2.51 / 1.66` | **Off Chops** |
| `1082859` | **NEXVOID vs Alter Ego** | `2026-10-26T03:00:00Z` | `#113 NEXVOID (995)` vs `#155 Alter Ego (819)` | `68.2% / 31.8%` | `1.47 / 3.14` | **NEXVOID** |
| `1082861` | **Rooster vs Abyssal** | `2026-10-27T03:00:00Z` | `#205 Rooster (718)` vs `#195 Abyssal (734)` | `48.2% / 51.8%` | `2.07 / 1.93` | **Abyssal** |
| `1082792` | **HOTU vs The Huns** | `2026-10-31T09:00:00Z` | `#31 HOTU (1437)` vs `#122 The Huns (944)` | `85.2% / 14.8%` | `1.17 / 6.77` | **HOTU** |
| `1082793` | **5star vs 1WIN** | `2026-10-31T13:00:00Z` | `#80 5star (1110)` vs `#38 1win (1383)` | `24.3% / 75.7%` | `4.12 / 1.32` | **1WIN** |

---

## 3. Bookmaker Line Verification (EGamersWorld / Vave Prematch Moneylines)

Session `7601d5ee` audited EGamersWorld (`https://egamersworld.com/counterstrike/matches` and individual `/counterstrike/match/...` & `/counterstrike/tip/...` pages) across the open fixtures not priced by Polymarket or Pinnacle:

### 3A. Fixture `1082769` — **K27 vs NEXORA** (`2026-10-22T17:30:00Z`, CIS LAN Championship #9)

- **EGamersWorld Match Page**: `https://egamersworld.com/counterstrike/match/nexora-vs-k27-U_TH-dVYT`
- **EGamersWorld Vave Tip Receipt**: `https://egamersworld.com/counterstrike/tip/nexora-vs-k27-U_TH-dVYT/4yp_dlKtNl`
- **HLTV Match Page**: `https://www.hltv.org/matches/2399846/nexora-vs-k27-winline-mpkbk-cis-lan-season-9`
- **Vave Prematch Moneyline (in Hotspawn fixture order `[K27, NEXORA]`)**:
  - Tip receipt decimal odds: **`K27 1.021 / NEXORA 8.10`** (`overround = 10.29%`)
  - Listing index decimal odds: **`K27 1.04 / NEXORA 8.20`** (`overround = 8.35%`)
  - **De-vigged probabilities (`[1.021, 8.10]`)**: **`88.8109% K27 / 11.1891% NEXORA`** (fair odds **`1.1260 / 8.9373`**)
- **HLTV 22 Oct 2026 Valve Global Ranking Comparison (`https://www.hltv.org/valve-ranking/teams/2026/october/22`)**:
  - **K27**: `#31` (`1396 points`; roster `clax, X5G7V, xeedo, kashl1d, qw1nk1`)
  - **NEXORA**: `#282` (`596 points`; roster `matusik, VRONSKY, Pryan3ch`)
  - **22 Oct 2026 VRS Calibrated Model (`1396 vs 596`)**: `expected = 0.988794`, **`89.0358% K27 / 10.9642% NEXORA`** (fair odds **`1.1231 / 9.1206`**)
  - Both the Vave prematch moneyline (`88.8% K27`) and the 22 Oct 2026 Valve VRS model (`89.0% K27`) agree within `0.22%` and confirm the published research pick **K27**.

### 3B. Fixture `1079188` — **Bushido Wildcats vs ex-6666** (`2026-10-22T08:00:00Z`, NODWIN Clutch Series #13)

- **EGamersWorld Match Page**: `https://egamersworld.com/counterstrike/match/bushido-wildcats-vs-ex-6666-Xs452MP7y`
- **EGamersWorld Vave Tip Receipt**: `https://egamersworld.com/counterstrike/tip/bushido-wildcats-vs-ex-6666-Xs452MP7y/Nk9F-Ov54e`
- **HLTV Match Page**: `https://www.hltv.org/matches/2399105/bushido-wildcats-vs-ex-6666-nodwin-clutch-series-13`
- **Vave Prematch Moneyline (in Hotspawn fixture order `[Bushido Wildcats, ex-6666]`)**:
  - Tip receipt decimal odds: **`Bushido Wildcats 2.26 / ex-6666 1.55`** (`overround = 8.76%`)
  - Listing index decimal odds: **`Bushido Wildcats 2.35 / ex-6666 1.50`** (`overround = 9.22%`)
  - **De-vigged probabilities (`[2.26, 1.55]`)**: **`40.6819% Bushido Wildcats / 59.3181% ex-6666`** (fair odds **`2.4581 / 1.6858`**)
- **Why the 5 Oct 2026 VRS Model Disagrees with Both the Bookmaker and the 22 Oct 2026 VRS**:
  - In `standings_global_2026_10_05.md`, `Bushido Wildcats` is `#114 (982 pts)` and `6666` is `#127 (923 pts)` -> **`56.5% Bushido Wildcats / 43.5% ex-6666`**.
  - On HLTV's 19 Oct 2026 World Ranking, `ex-6666` is `#72` while `Bushido Wildcats` is `#113`.
  - On HLTV's 22 Oct 2026 Valve Global Ranking (`https://www.hltv.org/valve-ranking/teams/2026/october/22`), `ex-6666` (`6666`) has risen to **`#117 (918 pts)`** while `Bushido Wildcats` has dropped to **`#121 (898 pts)`**, which produces a 22 Oct VRS model probability of **`47.77% Bushido Wildcats / 52.23% ex-6666`**.
  - Thus, the bookmaker line (`59.3% ex-6666`), the 22 Oct 2026 Valve VRS (`52.2% ex-6666`), and the HLTV World Ranking (`#72 vs #113`) all favour **ex-6666**. We have logged a request in `research/session-7601d5ee/REQUESTS.md` and `COORDINATION.md` to add this Vave receipt to `data/book-receipts.json` and `data/review-notes.json`.

### 3C. EGamersWorld `1.80 / 1.80` Placeholder Receipts (Correctly Rejected)

The following EGamersWorld match pages display only default `1.8 / 1.8` placeholders (no bookmaker table and no Vave prematch quote) and are therefore **rejected** under the repo's fail-closed rules:
- `1081869` Morningstar vs NEXVOID (`https://egamersworld.com/counterstrike/match/morningstar-vs-nexvoid-e_MT2tamL`)
- `1081597` benched gods vs TitanFlow (`https://egamersworld.com/counterstrike/match/benched-gods-vs-titanflow-EcLgERbZn`)
- `1079654` ex-Zero Tenacity vs ex-RUSTEC (`https://egamersworld.com/counterstrike/match/ex-zero-tenacity-vs-ex-rustec-YieSsHTBr`)
- `1081149` FORZE Reload vs LFO 10 (`https://egamersworld.com/counterstrike/match/forze-reload-vs-_04jKZ07_4`)
- `1081150` ex-RUSTEC vs Saint Sinners (`https://egamersworld.com/counterstrike/match/ex-rustec-vs-saint-sinners-qRkeIZuchq`)
- `1082860` FlyQuest vs Staqued (`https://egamersworld.com/counterstrike/match/flyquest-vs-staqued-zawJ-Q52S3`)
- `1081596` Falcons Force vs Phantom Academy (`https://egamersworld.com/counterstrike/match/falcons-force-vs-phantom-academy-sC2w9SZz4`)
- `1081145` Lavked vs HAVU (`https://egamersworld.com/counterstrike/match/lavked-vs-havu-qGBNreiXP-`)
- `1081148` Inner Circle Academy vs Spirit Academy (`https://egamersworld.com/counterstrike/match/inner-circle-academy-vs-spirit-academy-qIxpg8-CUg`)

---

## 4. Deep Dive on the 7 Research-Only Open Matches (`2026-10-05` vs `2026-10-22` Valve VRS)

| Hotspawn ID | Match | Published Method | Published Pick | Why `2026-10-05` VRS Model Withheld Probability | `2026-10-22` HLTV Valve VRS Standings & Calibrated Comparison |
|---|---|---|---|---|---|
| `1081869` | **Morningstar vs NEXVOID** | `research_rank_single` | **NEXVOID** | Morningstar (`Freeman, fineshine52, swiftsteel, Terryyy, Apraki`) is absent from 5 Oct VRS (`380` teams) and unranked on HLTV. NEXVOID is HLTV `#77` and 5 Oct VRS `#113 (995 pts)`. | NEXVOID is `#72 (1168 pts)` on 22 Oct VRS; Morningstar remains unranked (`0` VRS points). |
| `1081597` | **benched gods vs TitanFlow** | `research_vrs_single` | **benched gods** | benched gods is 5 Oct VRS `#157 (811 pts)` and HLTV `#204`; TitanFlow (`team/14021`) has no active lineup and is absent from 5 Oct VRS. | benched gods is `#160 (792 pts)` on 22 Oct VRS; TitanFlow remains unranked. |
| `1082769` | **K27 vs NEXORA** | `research_rank_single` | **K27** | K27 is HLTV `#46` and 5 Oct VRS `#32 (1435 pts)`, while NEXORA was not yet listed in the 5 Oct VRS file (`380` teams), even though HLTV match `2399846` displays NEXORA's newer VRS rank `#282`. | On 22 Oct VRS, K27 is `#31 (1396 pts)` and NEXORA is `#282 (596 pts)` -> **`89.04% K27 / 10.96% NEXORA`** (fair `1.12 / 9.12`), matching Vave's `1.021 / 8.10` (`88.81% / 11.19%`). |
| `1079654` | **ex-Zero Tenacity vs ex-RUSTEC** | `research_rank` | **ex-Zero Tenacity** | Active HLTV lineup for `ex-RUSTEC` (`youka, bl1x1, yiksrezo, Brilliance, jakekeS`) ties at `3/5` overlap with two 5 Oct VRS rows: `#92 (1066 pts)` (`50.0% / 50.0%` vs `#93 ex-Zero Tenacity 1066 pts`) and `#152 (824 pts)` (`73.56% / 26.44%`). Resolved by HLTV world rank `#67 vs #70`. | On 22 Oct VRS, `ex-Zero Tenacity` is `#95 (1053 pts)` and `ex-RUSTEC` (`RUSTEC`) is `#91 (1073 pts)` -> **`47.77% ex-Zero Tenacity / 52.23% ex-RUSTEC`** (near-coinflip). |
| `1081149` | **FORZE Reload vs LFO 10** | `research_rank_single` | **FORZE Reload** | `LFO 10` (`team/14084`, formerly `#156 Entropy 813 pts` in 5 Oct VRS) fielded `Sapec, dottie, L00m1, Mann3n, dan1` in match `2399499`, sharing only `2/5` players (`Sapec, dottie`) with 5 Oct `#156 Entropy` (`chawzyyy, dottie, flaw, Noisyboy, Sapec`), below Valve's `3/5` roster-continuity rule. | On 22 Oct VRS, `FORZE Reload` is `#82 (1104 pts)` and `LFO 10` (`Entropy`) is `#157 (805 pts, dottie, flaw, Sapec, Mann3n, L00m1)` -> **`77.33% FORZE Reload / 22.67% LFO 10`** (5 Oct `1100 vs 813` is **`76.60% / 23.40%`**). |
| `1081150` | **ex-RUSTEC vs Saint Sinners** | `research_rank` | **ex-RUSTEC** | Same `3/5` tie for `ex-RUSTEC` between 5 Oct VRS `#92 (1066 pts)` and `#152 (824 pts)` against `#158 Saint Sinners (810 pts)` (`74.55% / 25.45%` under `#92`, `51.56% / 48.44%` under `#152`). Both favour `ex-RUSTEC`; resolved by HLTV world rank `#70 vs #123`. | On 22 Oct VRS, `ex-RUSTEC` is `#91 (1073 pts)` and `Saint Sinners` is `#133 (898 pts)` -> **`68.14% ex-RUSTEC / 31.86% Saint Sinners`**. |
| `1082860` | **FlyQuest vs Staqued** | `research_rank_single` | **FlyQuest** | FlyQuest is HLTV `#61` and 5 Oct VRS `#86 (1093 pts)`; Staqued (`w0mbat, xelja, Hazel, lzj, kasze`) is absent from 5 Oct VRS and unranked on HLTV. | On 22 Oct VRS, FlyQuest is `#54 (1253 pts)` while Staqued remains unranked. |
