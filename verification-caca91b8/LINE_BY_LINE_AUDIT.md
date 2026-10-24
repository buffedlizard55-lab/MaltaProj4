# Session `caca91b8` — Complete Line-by-Line Source & Arithmetic Audit

- **Runner capture**: [`40113090316`](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40113090316)
- **Snapshot generated**: `2026-10-24T16:50:01.253200Z` (fixtures observed `2026-10-24T16:46:26.738811Z`)
- **Hotspawn 4-way coverage parity**: `verified` (`{'api': 83, 'page': 83, 'lobby': 83, 'retained': 83}`)
- **Total CS2 rows verified**: `83` (`22` open at capture, `61` past/locked)
- **Independent probability reproductions (`< 1e-9`)**: `22` / `22` (`0` failures, `0` Hotspawn probability inputs)
- **Method breakdown**: `{'exchange': 14, 'bookmaker_fallback': 3, 'model_vrs_mirror': 1, 'model_vrs': 3, 'exchange_wide': 1}`

## 1. Open Pick'em Board at Capture (22/22 Priced with Obvious Picks & Official Source Links)

| ID | Match | Start (UTC) | Pick | Win % (A / B) | Independent Replay | Method | Official Fixture & Probability Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `1079661` | Nuclear TigeRES vs ex-Zero Tenacity | `2026-10-24T17:00:00Z` | **Nuclear TigeRES** | `68.00% / 32.00%` | `68.00% / 32.00%` (`Δ=0.0e+00`) | `exchange` | [Hotspawn](https://www.hotspawn.com/matches/nuclear-tigeres-vs-ex-zero-tenacity-cct-europe-2026-series-11-1079661) · [Polymarket](https://polymarket.com/event/cs2-ntr-zerote-2026-10-24) |
| `1081154` | BakS vs ILLYRIANS | `2026-10-24T17:00:00Z` | **BakS** | `69.50% / 30.50%` | `69.50% / 30.50%` (`Δ=0.0e+00`) | `exchange` | [Hotspawn](https://www.hotspawn.com/matches/baks-vs-illyrians-cct-europe-2026-series-12-1081154) · [Polymarket](https://polymarket.com/event/cs2-baks-ill4-2026-10-24) |
| `1082695` | Galorys vs paiN | `2026-10-24T18:00:00Z` | **paiN** | `42.00% / 58.00%` | `42.00% / 58.00%` (`Δ=0.0e+00`) | `exchange` | [Hotspawn](https://www.hotspawn.com/matches/galorys-vs-pain-circuit-x-curitiba-4-1082695) · [Polymarket](https://polymarket.com/event/cs2-gls1-pain-2026-10-24) |
| `1083122` | LOS NINOS vs BORRACHEIROS | `2026-10-24T19:00:00Z` | **BORRACHEIROS** | `30.00% / 70.00%` | `30.00% / 70.00%` (`Δ=0.0e+00`) | `exchange` | [Hotspawn](https://www.hotspawn.com/matches/los-ninos-vs-borracheiros-cct-south-america-2026-series-7-1083122) · [Polymarket](https://polymarket.com/event/cs2-ln-chama-2026-10-24) |
| `1083140` | BESTIA vs Imperial | `2026-10-24T21:00:00Z` | **Imperial** | `33.50% / 66.50%` | `33.50% / 66.50%` (`Δ=0.0e+00`) | `exchange` | [Hotspawn](https://www.hotspawn.com/matches/bestia-vs-imperial-circuit-x-curitiba-4-1083140) · [Polymarket](https://polymarket.com/event/cs2-bst-imp11-2026-10-24) |
| `1083123` | Grêmio vs Yawara | `2026-10-24T22:00:00Z` | **Yawara** | `31.31% / 68.69%` | `31.31% / 68.69%` (`Δ=0.0e+00`) | `bookmaker_fallback` | [Hotspawn](https://www.hotspawn.com/matches/gremio-vs-yawara-cct-south-america-2026-series-7-1083123) · [Thunderpick (via BO3.gg API)](https://bo3.gg/matches/gremio-vs-yawara-esports-24-10-2026) · [HLTV](https://www.hltv.org/matches/2399915/grmio-vs-yawara-cct-2026-south-america-series-7) |
| `1082996` | Acend vs UNiTY | `2026-10-25T09:00:00Z` | **UNiTY** | `39.50% / 60.50%` | `39.50% / 60.50%` (`Δ=0.0e+00`) | `exchange` | [Hotspawn](https://www.hotspawn.com/matches/acend-vs-unity-nodwin-clutch-series-13-1082996) · [Polymarket](https://polymarket.com/event/cs2-ace1-unity-2026-10-25) |
| `1079198` | Metizport vs BakS | `2026-10-25T12:00:00Z` | **Metizport** | `67.50% / 32.50%` | `67.50% / 32.50%` (`Δ=0.0e+00`) | `exchange` | [Hotspawn](https://www.hotspawn.com/matches/metizport-vs-baks-nodwin-clutch-series-13-1079198) · [Polymarket](https://polymarket.com/event/cs2-mzp-baks-2026-10-25) |
| `1081156` | Spirit Academy vs LFO 10 | `2026-10-25T12:00:00Z` | **Spirit Academy** | `72.13% / 27.87%` | `72.13% / 27.87%` (`Δ=0.0e+00`) | `model_vrs_mirror` | [Hotspawn](https://www.hotspawn.com/matches/spirit-academy-vs-lfo-10-cct-europe-2026-series-12-1081156) · [HLTV Valve ranking (Valve points)](https://www.hltv.org/valve-ranking/teams/2026/october/24) · [HLTV](https://www.hltv.org/matches/2399506/spirit-academy-vs-lfo-10-cct-2026-europe-series-12) |
| `1079199` | Infinite vs BRUTE | `2026-10-25T15:00:00Z` | **BRUTE** | `46.00% / 54.00%` | `46.00% / 54.00%` (`Δ=0.0e+00`) | `exchange` | [Hotspawn](https://www.hotspawn.com/matches/infinite-vs-brute-nodwin-clutch-series-13-1079199) · [Polymarket](https://polymarket.com/event/cs2-inf6-brute-2026-10-25) |
| `1079200` | Color vs ex-Zero Tenacity | `2026-10-25T18:00:00Z` | **Color** | `68.84% / 31.16%` | `68.84% / 31.16%` (`Δ=0.0e+00`) | `model_vrs` | [Hotspawn](https://www.hotspawn.com/matches/color-vs-ex-zero-tenacity-nodwin-clutch-series-13-1079200) · [Valve VRS model](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) · [HLTV](https://www.hltv.org/matches/2399115/color-vs-ex-zero-tenacity-nodwin-clutch-series-13) |
| `1081158` | FORZE Reload vs ex-RUSTEC | `2026-10-25T18:00:00Z` | **FORZE Reload** | `53.00% / 47.00%` | `53.00% / 47.00%` (`Δ=0.0e+00`) | `exchange` | [Hotspawn](https://www.hotspawn.com/matches/forze-reload-vs-ex-rustec-cct-europe-2026-series-12-1081158) · [Polymarket](https://polymarket.com/event/cs2-forzer-rustec-2026-10-25) |
| `1082858` | Ground Zero vs Off Chops | `2026-10-26T03:00:00Z` | **Off Chops** | `32.50% / 67.50%` | `32.50% / 67.50%` (`Δ=0.0e+00`) | `exchange_wide` | [Hotspawn](https://www.hotspawn.com/matches/ground-zero-vs-off-chops-dfrag-invitational-2026-1082858) · [Polymarket](https://polymarket.com/event/cs2-gz1-offcho-2026-10-25) · [HLTV](https://www.hltv.org/matches/2399888/ground-zero-vs-off-chops-dfrag-invitational-2026) |
| `1082859` | NEXVOID vs Alter Ego | `2026-10-26T03:00:00Z` | **NEXVOID** | `57.52% / 42.48%` | `57.52% / 42.48%` (`Δ=0.0e+00`) | `bookmaker_fallback` | [Hotspawn](https://www.hotspawn.com/matches/nexvoid-vs-alter-ego-dfrag-invitational-2026-1082859) · [Thunderpick (via BO3.gg API)](https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026) · [HLTV](https://www.hltv.org/matches/2399889/nexvoid-vs-alter-ego-dfrag-invitational-2026) |
| `1082860` | FlyQuest vs Staqued | `2026-10-27T03:00:00Z` | **FlyQuest** | `92.30% / 7.70%` | `92.30% / 7.70%` (`Δ=0.0e+00`) | `bookmaker_fallback` | [Hotspawn](https://www.hotspawn.com/matches/flyquest-vs-staqued-dfrag-invitational-2026-1082860) · [Thunderpick (via BO3.gg API)](https://bo3.gg/matches/flyquest-vs-staqued-27-10-2026) · [HLTV](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026) |
| `1082861` | Rooster vs Abyssal | `2026-10-27T03:00:00Z` | **Abyssal** | `42.50% / 57.50%` | `42.50% / 57.50%` (`Δ=0.0e+00`) | `exchange` | [Hotspawn](https://www.hotspawn.com/matches/rooster-vs-abyssal-dfrag-invitational-2026-1082861) · [Polymarket](https://polymarket.com/event/cs2-rstr-abyssa-2026-10-26) |
| `1082897` | B8 vs K27 | `2026-10-27T08:00:00Z` | **B8** | `60.50% / 39.50%` | `60.50% / 39.50%` (`Δ=0.0e+00`) | `exchange` | [Hotspawn](https://www.hotspawn.com/matches/b8-vs-k27-tesla-cup-2026-1082897) · [Polymarket](https://polymarket.com/event/cs2-b8-k271-2026-10-27) |
| `1082898` | Alliance vs FaZe | `2026-10-27T11:00:00Z` | **FaZe** | `35.00% / 65.00%` | `35.00% / 65.00%` (`Δ=0.0e+00`) | `exchange` | [Hotspawn](https://www.hotspawn.com/matches/alliance-vs-faze-tesla-cup-2026-1082898) · [Polymarket](https://polymarket.com/event/cs2-all-faze-2026-10-27) |
| `1082900` | Luminosity vs HOTU | `2026-10-27T17:00:00Z` | **Luminosity** | `52.50% / 47.50%` | `52.50% / 47.50%` (`Δ=0.0e+00`) | `exchange` | [Hotspawn](https://www.hotspawn.com/matches/luminosity-vs-hotu-tesla-cup-2026-1082900) · [Polymarket](https://polymarket.com/event/cs2-lg6-hotu-2026-10-27) |
| `1082901` | Envy vs GamerLegion | `2026-10-27T20:00:00Z` | **GamerLegion** | `45.50% / 54.50%` | `45.50% / 54.50%` (`Δ=0.0e+00`) | `exchange` | [Hotspawn](https://www.hotspawn.com/matches/envy-vs-gamerlegion-tesla-cup-2026-1082901) · [Polymarket](https://polymarket.com/event/cs2-envy-gl1-2026-10-27) |
| `1082792` | HOTU vs The Huns | `2026-10-31T09:00:00Z` | **HOTU** | `85.18% / 14.82%` | `85.18% / 14.82%` (`Δ=0.0e+00`) | `model_vrs` | [Hotspawn](https://www.hotspawn.com/matches/hotu-vs-the-huns-moscow-cyber-games-2026-1082792) · [Valve VRS model](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) · [HLTV](https://www.hltv.org/matches/2399437/hotu-vs-the-huns-gluck-moscow-cyber-games-2026) |
| `1082793` | 5star vs 1WIN | `2026-10-31T13:00:00Z` | **1WIN** | `24.30% / 75.70%` | `24.30% / 75.70%` (`Δ=0.0e+00`) | `model_vrs` | [Hotspawn](https://www.hotspawn.com/matches/5star-vs-1win-moscow-cyber-games-2026-1082793) · [Valve VRS model](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) · [HLTV](https://www.hltv.org/matches/2399438/1win-vs-5star-gluck-moscow-cyber-games-2026) |

## 2. Non-Open Feed Entries Verified Not Priced (61/61 Past or Locked)

| ID | Match | Start (UTC) | Lock (UTC) | State | Official Fixture Link |
| --- | --- | --- | --- | --- | --- |
| `1052746` | Fortress vs Endless Journey | `2026-06-26T10:30:00Z` | `2026-06-26T10:24:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1051339` | Acend vs Infinite | `2026-06-26T12:00:00Z` | `2026-06-26T11:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1051301` | CYBERSHOKE Prospects vs PCIFIC | `2026-06-26T13:00:00Z` | `2026-06-26T12:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053068` | Johnny Speeds vs ReThink | `2026-06-26T13:00:00Z` | `2026-06-26T12:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052747` | Sashi Academy vs eternal premium | `2026-06-26T13:10:00Z` | `2026-06-26T13:04:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053146` | Atrix vs Clutchain | `2026-06-26T14:00:00Z` | `2026-06-26T13:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1051340` | Walczaki vs Inner Circle | `2026-06-26T15:00:00Z` | `2026-06-26T14:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053069` | roamsfiest vs train launcher | `2026-06-26T16:45:00Z` | `2026-06-26T16:39:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052686` | shimmer vs MIBR fe | `2026-06-26T17:45:00Z` | `2026-06-26T17:39:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1051789` | MIBR Academy vs Isurus | `2026-06-26T18:00:00Z` | `2026-06-26T17:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053070` | ReThink vs train launcher | `2026-06-26T19:00:00Z` | `2026-06-26T18:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1051790` | Keyd vs Yawara | `2026-06-26T21:00:00Z` | `2026-06-26T20:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052748` | Inner Circle Academy vs sAw | `2026-06-27T08:00:00Z` | `2026-06-27T07:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053071` | Johnny Speeds vs roamsfiest | `2026-06-27T10:00:00Z` | `2026-06-27T09:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052749` | Misa vs WROTBERRY | `2026-06-27T10:30:00Z` | `2026-06-27T10:24:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052180` | NEW VISION vs Julie&Cie | `2026-06-27T11:00:00Z` | `2026-06-27T10:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052181` | Just Players vs OlyBet | `2026-06-27T11:00:00Z` | `2026-06-27T10:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1051800` | ShindeN vs MIBR Academy | `2026-06-27T13:00:00Z` | `2026-06-27T12:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052699` | Vasco vs Red Feet | `2026-06-27T13:00:00Z` | `2026-06-27T12:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052183` | Misa vs Wampirki | `2026-06-27T13:45:00Z` | `2026-06-27T13:39:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1051341` | Sharks vs Inner Circle | `2026-06-27T13:50:00Z` | `2026-06-27T13:44:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052599` | Mai Tai vs Megoshort | `2026-06-27T14:00:00Z` | `2026-06-27T13:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053072` | train launcher vs roamsfiest | `2026-06-27T14:10:00Z` | `2026-06-27T14:04:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052357` | BIG Academy vs BERG | `2026-06-27T15:00:00Z` | `2026-06-27T14:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1051801` | Bounty Hunters vs UNO MILLE | `2026-06-27T16:00:00Z` | `2026-06-27T15:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052700` | GameHunters vs VEXA | `2026-06-27T16:00:00Z` | `2026-06-27T15:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1051342` | ex-Tricked vs Acend | `2026-06-27T17:00:00Z` | `2026-06-27T16:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053073` | roamsfiest vs ReThink | `2026-06-27T17:00:00Z` | `2026-06-27T16:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052701` | paiN Academy vs Alka | `2026-06-27T19:00:00Z` | `2026-06-27T18:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053313` | Fake do Biru vs LP | `2026-06-27T19:00:00Z` | `2026-06-27T18:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1051803` | Fluxo vs Keyd | `2026-06-27T22:00:00Z` | `2026-06-27T21:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052702` | Procyon vs BESTIA Academy | `2026-06-27T22:00:00Z` | `2026-06-27T21:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052750` | Honvéd vs OlyBet | `2026-06-28T08:00:00Z` | `2026-06-28T07:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052751` | ex-MANA vs Subtop De France | `2026-06-28T10:50:00Z` | `2026-06-28T10:44:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052185` | sAw vs Entropy | `2026-06-28T11:00:00Z` | `2026-06-28T10:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053431` | GAMEHARMONY vs Coalesce | `2026-06-28T11:00:00Z` | `2026-06-28T10:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053432` | Leo vs Aimhaus | `2026-06-28T11:00:00Z` | `2026-06-28T10:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053433` | GAMEHARMONY vs Aimhaus | `2026-06-28T12:00:00Z` | `2026-06-28T11:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053434` | Leo vs Coalesce | `2026-06-28T12:00:00Z` | `2026-06-28T11:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052698` | ex-KRÜ vs MAGICOS | `2026-06-28T13:00:00Z` | `2026-06-28T12:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053435` | GAMEHARMONY vs Leo | `2026-06-28T13:00:00Z` | `2026-06-28T12:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053436` | Aimhaus vs Coalesce | `2026-06-28T13:00:00Z` | `2026-06-28T12:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1051343` | Sharks vs ex-Tricked | `2026-06-28T13:35:00Z` | `2026-06-28T13:29:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052186` | Lilmix vs Subtop De France | `2026-06-28T13:45:00Z` | `2026-06-28T13:39:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052187` | BIG Academy vs Endless Journey | `2026-06-28T13:45:00Z` | `2026-06-28T13:39:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052184` | Atreides vs Donstu | `2026-06-28T14:05:00Z` | `2026-06-28T13:59:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052696` | Yawara vs Blitzkrieg | `2026-06-28T16:00:00Z` | `2026-06-28T15:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053439` | 6666 vs ASTRAL | `2026-06-28T16:00:00Z` | `2026-06-28T15:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053469` | BERG vs SINQU REHTI | `2026-06-28T16:00:00Z` | `2026-06-28T15:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053441` | ASTRAL vs BERG | `2026-06-28T17:00:00Z` | `2026-06-28T16:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053470` | 6666 vs SINQU REHTI | `2026-06-28T17:00:00Z` | `2026-06-28T16:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1051344` | Inner Circle vs Acend | `2026-06-28T17:30:00Z` | `2026-06-28T17:24:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1051804` | Fluxo vs UNO MILLE | `2026-06-28T18:00:00Z` | `2026-06-28T17:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053442` | 6666 vs BERG | `2026-06-28T18:00:00Z` | `2026-06-28T17:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053471` | ASTRAL vs SINQU REHTI | `2026-06-28T18:00:00Z` | `2026-06-28T17:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052697` | METANOIA Wolves vs Guara | `2026-06-28T19:05:00Z` | `2026-06-28T18:59:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1053679` | ShindeN vs LP | `2026-06-28T21:15:00Z` | `2026-06-28T21:09:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1052695` | MIBR Academy vs Patins de Ferrari | `2026-06-28T22:00:00Z` | `2026-06-28T21:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1055478` | illwill vs Lavked | `2026-07-10T08:00:00Z` | `2026-07-10T07:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1081105` | SUKEBAN vs your end | `2026-10-13T22:00:00Z` | `2026-10-13T21:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
| `1079621` | Gothic vs Lavked | `2026-10-14T08:00:00Z` | `2026-10-14T07:54:00Z` | `not_open` | [Hotspawn](https://play.hotspawn.com/cs2-pickems) |
