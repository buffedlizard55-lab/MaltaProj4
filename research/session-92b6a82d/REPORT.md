# Session 92b6a82d Research & Pipeline Audit Report (2026-10-21)

## 1. Live Hotspawn CS2 Inventory & Gap Audit (2026-10-21)

Observed from the official Hotspawn CS2 fixture feed (`https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`) and verified against the live GitHub Pages deployment (`https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json`):

- **Total CS2 scheduled records:** `81` (`62` past lock/start retained as `not_open` in `matches.html`, `19` open upcoming matches).
- **Scheduled publication recovery:** `main` run [`39601307680`](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39601307680) (`e9abc8a`) restored live publication after the historical wall-clock test in `tests/test_session_133fe7ca.py` was pinned to its fixture date.
- **Four gap fixtures audited on 2026-10-21:**
  1. **`1079648` — `G2 Ares` vs `ILLYRIANS`** (`CCT Europe 2026 Series #11`, `2026-10-21T14:00:00Z`):
     - At `12:41 UTC`, Polymarket market [`5994489`](https://gamma-api.polymarket.com/markets/5994489) sat at `0.50 / 0.50` (`No directional edge`).
     - By `12:42:59 UTC` (`main` run `39601307680`), market `5994489` updated to `outcomePrices: ["0.505", "0.495"]` (`bestBid: 0.50`, `bestAsk: 0.51`, `liquidity: $5,219.72`), resolving `1079648` to **`G2 Ares` (`50.5% / 49.5%`)** under strict `exchange` gates.
  2. **`1082762` — `ex-CYBERSHOKE` vs `BlinkDagger`** (`CIS LAN Championship #9`, `2026-10-21T15:00:00Z`):
     - HLTV fixture [`2399839`](https://www.hltv.org/matches/2399839/ex-cybershoke-vs-blinkdagger-winline-mpkbk-cis-lan-season-9) lists `ex-CYBERSHOKE` (`bl1x1, fen2k, glowiing, levantino, alpha`) vs `BlinkDagger` (`hoody,uga, Me1o, k1ssly, R3LiFw0w, spirit`), both unranked on HLTV.
     - Polymarket market [`5971981`](https://gamma-api.polymarket.com/markets/5971981) (`CYBERSHOKE Esports vs BlinkDagger`, `2026-10-21 15:00:00+00`) quotes `outcomePrices: ["0.82", "0.18"]` (`bestBid: 0.81`, `bestAsk: 0.83`, `liquidity: $1,981.53`).
     - Valve's `2026-10-05` global standings list two separate `CYBERSHOKE` rows (`#61` and `#171`), neither matching `3/5` of the `ex-CYBERSHOKE` lineup (`bl1x1, fen2k, glowiing, levantino, alpha`), and `BlinkDagger` is absent.
  3. **`1082763` — `UPGRADE` vs `flacons`** (`CIS LAN Championship #9`, `2026-10-21T15:00:00Z`):
     - HLTV fixture [`2399840`](https://www.hltv.org/matches/2399840/upgrade-vs-flacons-winline-mpkbk-cis-lan-season-9) lists `UPGRADE` (`HLTV #187`) vs unranked `flacons` (`research_rank_single` pick: `UPGRADE`).
     - Polymarket market [`5971986`](https://gamma-api.polymarket.com/markets/5971986) (`UPGRADE vs Team flacons`, `2026-10-21 15:00:00+00`) quotes `outcomePrices: ["0.955", "0.045"]` (`bestBid: 0.95`, `bestAsk: 0.96`, `liquidity: $2,954.12`).
  4. **`1082837` — `Zetta` vs `LOS NINOS`** (`CCT South America 2026 Series #7`, `2026-10-21T22:00:00Z`):
     - Detailed cross-source verification below.

## 2. Deep-Dive Verification of `1082837` (`Zetta` vs `LOS NINOS`)

| Source | URL | Observation (2026-10-21) |
| --- | --- | --- |
| Hotspawn | `https://www.hotspawn.com/matches/zetta-vs-los-ninos-cct-south-america-2026-series-7-1082837` | Scheduled `2026-10-21T22:00:00Z` (lock `21:54:00Z`), `CCT South America 2026 Series #7`. |
| HLTV fixture | `https://www.hltv.org/matches/2399865/zetta-vs-los-ninos-cct-2026-south-america-series-7` | `Zetta` (`Notjuanjo, zockie, BabyRage, Antuanette, Slayerhz`, World `#241`) vs `LOS NINOS` (`Reix, PremiuM, aNgelo, protado, Space`, unranked). Resolves to **`Zetta`** via `research_rank_single` (no numeric probability). |
| HLTV team | `https://www.hltv.org/team/13833/zetta` | Lists `Zetta` at Valve ranking `#269` and World ranking `#241` with roster `zockie, BabyRage, Slayerhz, Antuanette, Notjuanjo`. |
| Valve VRS Global (`2026-10-05`) | `https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md` | `Zetta` is `#357` globally (`473` VRS points, roster `Antuanette, BabyRage, Notjuanjo, Slayerhz, zockie`). `LOS NINOS` is absent from the 380-team global file. |
| Valve VRS Americas (`2026-10-05`) | `https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_americas_2026_10_05.md` | `Zetta` is `#80` Americas (`473` pts). `LOS NINOS` is absent as a team (`space` appears on `#88 Players` and `Reix` on `#89 Crashers`, confirming `LOS NINOS` is a new mix). |
| Liquipedia | `https://liquipedia.net/counterstrike/CCT/2026/South_America/Series_7` | Lists the VRS South America invite and the Oct 21 `22:00 UTC` Round 5 match against `Los Niños` under the club name **`Alianza Lima Esports`** with the identical 5-man roster (`zockie, BabyRage, Slayerhz, Antuanette, NotJuanjo`). |
| Polymarket | `https://gamma-api.polymarket.com/markets/6001634` | `Alianza Lima Esports vs Los Niños (BO3)` at `2026-10-21 22:00:00+00`: `outcomePrices: ["0.49", "0.51"]`, `bestBid: 0.19`, `bestAsk: 0.79` (`spread: 0.60`), `volume: $5`, `liquidity: $542.67`. Not mapped in `data/identities.json` because `Alianza Lima Esports` vs `Zetta` is a club-name difference rather than an abbreviation of the same label, and the `$5`-volume 60-point-spread market points opposite to both HLTV `#241` and Valve VRS `#357`. |
| EGamersWorld | `https://egamersworld.com/counterstrike/match/0U32SId-H/zetta-vs-los-ninos-Wi0PWrNpb` | Displays only the `1.8 / 1.8` symmetrical placeholder pair (`0% / 0%` community tip); excluded by placeholder gate. |

## 3. Pipeline Bugs Fixed in This Session

1. **Missing `vrs.research_single` invocation in `scripts/refresh.py`:**
   - `scripts/vrs.py` defines `research_single(fixture, standings, meta, lineups=None)` (`method='research_vrs_single'`), which is documented in `sources.html` (`scripts/build.py`), validated in `scripts/validate.py` and `verification-c6/audit_snapshot.py`, and referenced in the fallback reason string in `scripts/refresh.py:336`, but was never called during `scripts/refresh.py:run()`.
   - Wired `vrs.research_single(m, standings, vrs_meta, lineups)` into `scripts/refresh.py` immediately after `research_rank_pick(m)` for any open unpicked fixture without probabilities.
2. **Float-precision boundary bug on the 60-point wide-exchange spread ceiling in `scripts/core.py`:**
   - In `scripts/core.py:quote_polymarket`, the strict 25-point spread check used a float-safe tolerance (`if spread > .25 + 1e-9:`), whereas the 60-point wide-tier ceiling two lines below used `if spread > .60:`.
   - For genuine 60.0-point spreads such as `bestBid = 0.19, bestAsk = 0.79` (observed live on Polymarket market `6001634`), IEEE-754 float subtraction produces `0.79 - 0.19 == 0.6000000000000001 > .60`, falsely rejecting a quote that `verification-c6/audit_snapshot.py` accepts under `Decimal('0.79') - Decimal('0.19') <= Decimal('.60')`.
   - Updated `scripts/core.py` to `if spread > .60 + 1e-9:`.
