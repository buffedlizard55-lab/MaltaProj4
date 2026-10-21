# Session `db1f35c5` Research & Line-by-Line Verification Report (`2026-10-21`)

## Executive Summary

At `2026-10-21T19:57:45Z`, the live production Hotspawn CS2 board contained **13 open upcoming fixtures**:
- **9 of 13** carried two-sided win probabilities (`4` Polymarket `exchange` / `exchange_wide`, `5` Valve `model_vrs`).
- **3 of 13** carried unpriced rank-only picks (`1082837 Zetta vs LOS NINOS` **picking the wrong favourite `Zetta`**, `1082858 Ground Zero vs Off Chops`, and `1082860 FlyQuest vs Staqued`).
- **1 of 13** had **no pick and no probability at all** (`1081597 benched gods vs TitanFlow`).

Every single open match on Hotspawn (`13 / 13 = 100.0%`) was audited line by line against primary sources (`gamma-api.polymarket.com`, `polymarket.com/esports/cs2`, `hltv.org`, `dfrag.gg`, `ValveSoftware/counter-strike_regional_standings` commit `eec4853d7b`, HLTV's `2026-10-21` Valve Regional Standings engine, `guest.api.arcadia.pinnacle.com`, `picklebet.com`, `stavka.tv`, `esportsinsider.com`, and `egamersworld.com`):

1. **`1082837` — `Zetta vs LOS NINOS` (`2026-10-21T22:00:00Z`, lock `21:54:00Z`, CCT South America 2026 Series #7)**:
   - **Critical correction & upgrade (`research_rank_single` `Zetta` -> Tier-1 `exchange` `LOS NINOS` `~61.5%` / `Zetta` `~38.5%`)**:
   - Proved from HLTV match `2399867`, Valve VRS `#357` (`0357--zetta--antuanette-babyrage-notjuanjo-slayerhz-zockie.md`), Strafe's CCT SA Series 7 team roster table, and PandaScore match `1762303` that Peruvian five-man roster **`Zetta`** (`Antuanette, BabyRage, Notjuanjo, Slayerhz, zockie`) is entered on Polymarket (`event 1227336`, `cs2-ale1-ln-2026-10-21`) under its former club tag **`Alianza Lima Esports`** at the identical `2026-10-21T22:00:00Z` UTC start against `Los Niños` (`$451.02` traded volume, `$3,240.93` moneyline CLOB liquidity, `0.38 / 0.39` bid/ask = `1¢` spread).
   - Without this verified alias, one-sided HLTV world rank (`Zetta #241`, `LOS NINOS Unranked`) selected the `~38.5%` underdog `Zetta`.

2. **`1082858` — `Ground Zero vs Off Chops` (`2026-10-26T03:00:00Z`, DFRAG Invitational 2026)**:
   - **Upgraded (`research_rank` -> calibrated two-sided `model_vrs`: `Off Chops 59.1%` / `Ground Zero 40.9%`)**:
   - Confirmed via DFRAG's official rebrand announcement, HLTV match `2399888`, Valve official global standings `#119` (`971 pts`), and HLTV's `2026-10-21` Asia regional Valve standings (`#14 Off Chops`, `913 pts`) that `Off Chops` (`dexter, Gratisfaction, Liazz, damyo, viridian`) retains **4/5 players** from `THUNDER dOWNUNDER` (`dexter, Gratisfaction, Liazz, TjP, viridian`).
   - Flagged on `review.html` that `Ground Zero` (`#136`, `878 pts`) fields stand-in `tucks` in place of `hazr` (`4/5` overlap) and trails `0–3` in recent LAN maps (`2399888`).

3. **`1081597` — `benched gods vs TitanFlow` (`2026-10-22T11:00:00Z`, CCT Europe 2026 Challengers #8)**:
   - **Resolved last `pick: null` gap (`null` -> `research_vrs_single` `benched gods`) + active schedule/integrity flags on `review.html`**:
   - Verified from Oct 21 Lower Bracket Round 2 results on HLTV (`2399691`: `benched gods 2–1 ex-6666`, lineup `Wign, facer, norescue, yoyoS2, K014NZ` = **5/5** match with Valve `#157`, `811 pts`, disambiguating `#329`; `2399692`: `TitanFlow 2–0 Noir Verse`, lineup `ves111, ZzZoOm, Saiman Strit, keeisen, Henma` = absent from `eec4853d7b`) that both teams advanced into Lower Bracket Round 3 #2 (`2399696`), where HLTV subsequently cleared slots to `TBA` and stamped **`Match postponed`** (alongside `2399698`), causing all bookmakers/exchanges to withhold lines.
   - Corroborated directionally against HLTV's rolling `2026-10-21` Valve global ranking (`benched gods #161` `791 pts` vs `TitanFlow #235` `664 pts`) and flagged both the `Match postponed` status (`2399696`) and prior opponent forfeiture note (`2399470`) prominently on `review.html`.

4. **`1082860` — `FlyQuest vs Staqued` (`2026-10-27T03:00:00Z`, DFRAG Invitational 2026)**:
   - Audited all 52 teams in the `2026-10-21` Asia/Oceania Valve regional ranking, Valve's `2026-10-05` global file, Polymarket's full CS2 slate through Nov 4, Pinnacle, Picklebet, Stavka, EsportsInsider, and EGamersWorld (`1.8/1.8` placeholder rejected in `data/book-receipts.json`): `Staqued` holds zero Valve ranking row and zero open betting market six days out, so `FlyQuest` (`HLTV #61`, `Valve #86` `1093 pts`) properly remains a non-market `research_rank_single` pick with blank probabilities.

## Full 13-Match Live Verified Open Slate (`2026-10-21T20:47:31Z`, PR `#119` -> `884f36e` / `179789e`)

- **PR**: `https://github.com/buffedlizard55-lab/MaltaProj4/pull/119`
- **Live deployment runs**: [`39671597469`](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39671597469) (`884f36e`) & [`39673399889`](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39673399889) (`179789e`) — both `verify-build` and `deploy` (`Verify live Pages bytes match this exact build`) **PASSED**.

| Hotspawn ID | Matchup | Start (UTC) | Method (Live) | Pick | Verified Win % (Live `20:47Z`) | Primary Source |
|---|---|---|---|---|---|---|
| `1082837` | Zetta vs LOS NINOS | `2026-10-21 22:00Z` | `exchange` (Polymarket) | **LOS NINOS** | `19.5% / 80.5%` | `https://gamma-api.polymarket.com/markets/6001634` |
| `1081870` | Vitalem Aerem vs Rare Atom | `2026-10-22 05:00Z` | `exchange_wide` (Polymarket) | **Rare Atom** | `40.0% / 60.0%` | `https://gamma-api.polymarket.com/markets/6024922` |
| `1081597` | benched gods vs TitanFlow | `2026-10-22 11:00Z` | `research_vrs_single` | **benched gods** | Blank (postponed / no market) | `https://www.hltv.org/matches/2399691/benched-gods-vs-ex-6666-cct-2026-challengers-europe-series-8` |
| `1081600` | Donstu vs Banda chuya | `2026-10-22 13:45Z` | `model_vrs` | **Banda chuya** | `42.4% / 57.6%` | `standings_global_2026_10_05.md` (`#197` vs `#165`) |
| `1082688` | Imperial vs Turma do Pagode | `2026-10-22 14:00Z` | `exchange` (Polymarket) | **Imperial** | `77.0% / 23.0%` | `https://gamma-api.polymarket.com/markets/5972064` |
| `1082689` | BESTIA vs ShindeN | `2026-10-22 14:00Z` | `exchange` (Polymarket) | **BESTIA** | `52.5% / 47.5%` | `https://gamma-api.polymarket.com/markets/5972071` |
| `1082882` | UNiTY vs Apogee Betclic | `2026-10-22 14:00Z` | `exchange` (Polymarket) | **Apogee Betclic** | `44.0% / 56.0%` | `https://gamma-api.polymarket.com/markets/6024716` |
| `1082858` | Ground Zero vs Off Chops | `2026-10-26 03:00Z` | `model_vrs` | **Off Chops** | `39.8% / 60.2%` | `ValveSoftware/counter-strike_regional_standings` (`Ground Zero` vs `THUNDER dOWNUNDER`) |
| `1082859` | NEXVOID vs Alter Ego | `2026-10-26 03:00Z` | `model_vrs` | **NEXVOID** | `68.2% / 31.8%` | `ValveSoftware/counter-strike_regional_standings` (`NEXVOID` vs `Alter Ego`) |
| `1082860` | FlyQuest vs Staqued | `2026-10-27 03:00Z` | `research_rank_single` | **FlyQuest** | Blank (Staqued unranked / no market) | `https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026` |
| `1082861` | Rooster vs Abyssal | `2026-10-27 03:00Z` | `model_vrs` | **Abyssal** | `48.2% / 51.8%` | `ValveSoftware/counter-strike_regional_standings` (`Rooster` vs `Abyssal`) |
| `1082792` | HOTU vs The Huns | `2026-10-31 09:00Z` | `model_vrs` | **HOTU** | `85.2% / 14.8%` | `ValveSoftware/counter-strike_regional_standings` (`HOTU` vs `The Huns`) |
| `1082793` | 5star vs 1WIN | `2026-10-31 13:00Z` | `model_vrs` | **1WIN** | `24.3% / 75.7%` | `ValveSoftware/counter-strike_regional_standings` (`5star` vs `1WIN`) |
