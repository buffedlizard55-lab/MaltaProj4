# Session fbea4413 — Line-by-Line Verification, Fallback Ladder & Mobile Audit Report

- **Snapshot generated at:** `2026-10-24T16:40:40.748952Z`
- **Fixtures observed at:** `2026-10-24T16:37:04.190185Z`
- **Total Hotspawn CS2 feed rows:** `83` (`20` open, `63` past/locked `not_open`, including `1079661` and `1081154` withdrawn at their `16:54:00Z` lock boundary)
- **Open matches with a pick:** `20` / `20`
- **Open matches with win probabilities:** `20` / `20`
- **Open unresolved matches:** `0`
- **Independent verifier problems:** `0`

## 1. Fallback Ladder Distribution (Open Matches)

| Method | Rung Description | Open Rows |
| --- | --- | ---: |
| `exchange` | Polymarket CS2 series moneyline (strict gate: spread <= 25 pts, liquidity >= $100) | 12 |
| `pinnacle` | Pinnacle public esports moneyline (de-vigged) | 0 |
| `exchange_wide` | Polymarket wide-spread moneyline (25 < spread <= 60 pts, liquidity >= $100, labelled low confidence) | 1 |
| `bookmaker_fallback` | Researched bookmaker listing (Thunderpick via BO3.gg / EGW, de-vigged) | 3 |
| `model_vrs` | Originated Valve Regional Standings (VRS) model (`standings_global_2026_10_05.md`, Glicko RD=75 + 0.7986 slope) | 3 |
| `model_vrs_mirror` | Originated VRS model from HLTV dated Valve ranking (`/valve-ranking/teams`, same formula & calibration) | 1 |
| `research_*` | Sourced HLTV / VRS research pick without percentage | 0 |
| `None` | Unresolved (fail-closed blank with explicit limitation reason) | 0 |

## 2. Line-by-Line Verification of All 20 Open CS2 Matches

| Fixture ID | UTC Start | Lock (UTC) | Competition | Team 1 vs Team 2 | Method | Team 1 Win % | Team 2 Win % | Fair Odds | Pick | Official Hotspawn Link | External Evidence / Standings Link |
| --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| `1082695` | `2026-10-24T18:00:00Z` | `2026-10-24T17:54:00Z` | Circuit X Curitiba #4 | Galorys vs paiN | `exchange` | 42.00% | 58.00% | 2.38 / 1.72 | **paiN** | [Hotspawn](https://www.hotspawn.com/matches/galorys-vs-pain-circuit-x-curitiba-4-1082695) | [Source](https://polymarket.com/event/cs2-gls1-pain-2026-10-24) |
| `1083122` | `2026-10-24T19:00:00Z` | `2026-10-24T18:54:00Z` | CCT South America 2026 Series #7 | LOS NINOS vs BORRACHEIROS | `exchange` | 29.00% | 71.00% | 3.45 / 1.41 | **BORRACHEIROS** | [Hotspawn](https://www.hotspawn.com/matches/los-ninos-vs-borracheiros-cct-south-america-2026-series-7-1083122) | [Source](https://polymarket.com/event/cs2-ln-chama-2026-10-24) |
| `1083140` | `2026-10-24T21:00:00Z` | `2026-10-24T20:54:00Z` | Circuit X Curitiba #4 | BESTIA vs Imperial | `exchange` | 33.50% | 66.50% | 2.99 / 1.50 | **Imperial** | [Hotspawn](https://www.hotspawn.com/matches/bestia-vs-imperial-circuit-x-curitiba-4-1083140) | [Source](https://polymarket.com/event/cs2-bst-imp11-2026-10-24) |
| `1083123` | `2026-10-24T22:00:00Z` | `2026-10-24T21:54:00Z` | CCT South America 2026 Series #7 | Grêmio vs Yawara | `bookmaker_fallback` | 31.31% | 68.69% | 3.19 / 1.46 | **Yawara** | [Hotspawn](https://www.hotspawn.com/matches/gremio-vs-yawara-cct-south-america-2026-series-7-1083123) | [Source](https://bo3.gg/matches/gremio-vs-yawara-esports-24-10-2026) |
| `1082996` | `2026-10-25T09:00:00Z` | `2026-10-25T08:54:00Z` | NODWIN Clutch Series #13 | Acend vs UNiTY | `exchange` | 39.50% | 60.50% | 2.53 / 1.65 | **UNiTY** | [Hotspawn](https://www.hotspawn.com/matches/acend-vs-unity-nodwin-clutch-series-13-1082996) | [Source](https://polymarket.com/event/cs2-ace1-unity-2026-10-25) |
| `1079198` | `2026-10-25T12:00:00Z` | `2026-10-25T11:54:00Z` | NODWIN Clutch Series #13 | Metizport vs BakS | `exchange` | 67.50% | 32.50% | 1.48 / 3.08 | **Metizport** | [Hotspawn](https://www.hotspawn.com/matches/metizport-vs-baks-nodwin-clutch-series-13-1079198) | [Source](https://polymarket.com/event/cs2-mzp-baks-2026-10-25) |
| `1081156` | `2026-10-25T12:00:00Z` | `2026-10-25T11:54:00Z` | CCT Europe 2026 Series #12 | Spirit Academy vs LFO 10 | `model_vrs_mirror` | 72.13% | 27.87% | 1.39 / 3.59 | **Spirit Academy** | [Hotspawn](https://www.hotspawn.com/matches/spirit-academy-vs-lfo-10-cct-europe-2026-series-12-1081156) | [Source](https://www.hltv.org/valve-ranking/teams/2026/october/24) |
| `1079199` | `2026-10-25T15:00:00Z` | `2026-10-25T14:54:00Z` | NODWIN Clutch Series #13 | Infinite vs BRUTE | `exchange` | 46.00% | 54.00% | 2.17 / 1.85 | **BRUTE** | [Hotspawn](https://www.hotspawn.com/matches/infinite-vs-brute-nodwin-clutch-series-13-1079199) | [Source](https://polymarket.com/event/cs2-inf6-brute-2026-10-25) |
| `1079200` | `2026-10-25T18:00:00Z` | `2026-10-25T17:54:00Z` | NODWIN Clutch Series #13 | Color vs ex-Zero Tenacity | `model_vrs` | 68.84% | 31.16% | 1.45 / 3.21 | **Color** | [Hotspawn](https://www.hotspawn.com/matches/color-vs-ex-zero-tenacity-nodwin-clutch-series-13-1079200) | [Source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |
| `1081158` | `2026-10-25T18:00:00Z` | `2026-10-25T17:54:00Z` | CCT Europe 2026 Series #12 | FORZE Reload vs ex-RUSTEC | `exchange` | 52.50% | 47.50% | 1.90 / 2.11 | **FORZE Reload** | [Hotspawn](https://www.hotspawn.com/matches/forze-reload-vs-ex-rustec-cct-europe-2026-series-12-1081158) | [Source](https://polymarket.com/event/cs2-forzer-rustec-2026-10-25) |
| `1082858` | `2026-10-26T03:00:00Z` | `2026-10-26T02:54:00Z` | DFRAG Invitational 2026 | Ground Zero vs Off Chops | `exchange_wide` | 33.00% | 67.00% | 3.03 / 1.49 | **Off Chops** | [Hotspawn](https://www.hotspawn.com/matches/ground-zero-vs-off-chops-dfrag-invitational-2026-1082858) | [Source](https://polymarket.com/event/cs2-gz1-offcho-2026-10-25) |
| `1082859` | `2026-10-26T03:00:00Z` | `2026-10-26T02:54:00Z` | DFRAG Invitational 2026 | NEXVOID vs Alter Ego | `bookmaker_fallback` | 57.52% | 42.48% | 1.74 / 2.35 | **NEXVOID** | [Hotspawn](https://www.hotspawn.com/matches/nexvoid-vs-alter-ego-dfrag-invitational-2026-1082859) | [Source](https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026) |
| `1082860` | `2026-10-27T03:00:00Z` | `2026-10-27T02:54:00Z` | DFRAG Invitational 2026 | FlyQuest vs Staqued | `bookmaker_fallback` | 92.30% | 7.70% | 1.08 / 12.99 | **FlyQuest** | [Hotspawn](https://www.hotspawn.com/matches/flyquest-vs-staqued-dfrag-invitational-2026-1082860) | [Source](https://bo3.gg/matches/flyquest-vs-staqued-27-10-2026) |
| `1082861` | `2026-10-27T03:00:00Z` | `2026-10-27T02:54:00Z` | DFRAG Invitational 2026 | Rooster vs Abyssal | `exchange` | 42.50% | 57.50% | 2.35 / 1.74 | **Abyssal** | [Hotspawn](https://www.hotspawn.com/matches/rooster-vs-abyssal-dfrag-invitational-2026-1082861) | [Source](https://polymarket.com/event/cs2-rstr-abyssa-2026-10-26) |
| `1082897` | `2026-10-27T08:00:00Z` | `2026-10-27T07:54:00Z` | Tesla Cup 2026 | B8 vs K27 | `exchange` | 60.50% | 39.50% | 1.65 / 2.53 | **B8** | [Hotspawn](https://www.hotspawn.com/matches/b8-vs-k27-tesla-cup-2026-1082897) | [Source](https://polymarket.com/event/cs2-b8-k271-2026-10-27) |
| `1082898` | `2026-10-27T11:00:00Z` | `2026-10-27T10:54:00Z` | Tesla Cup 2026 | Alliance vs FaZe | `exchange` | 35.00% | 65.00% | 2.86 / 1.54 | **FaZe** | [Hotspawn](https://www.hotspawn.com/matches/alliance-vs-faze-tesla-cup-2026-1082898) | [Source](https://polymarket.com/event/cs2-all-faze-2026-10-27) |
| `1082900` | `2026-10-27T17:00:00Z` | `2026-10-27T16:54:00Z` | Tesla Cup 2026 | Luminosity vs HOTU | `exchange` | 52.50% | 47.50% | 1.90 / 2.11 | **Luminosity** | [Hotspawn](https://www.hotspawn.com/matches/luminosity-vs-hotu-tesla-cup-2026-1082900) | [Source](https://polymarket.com/event/cs2-lg6-hotu-2026-10-27) |
| `1082901` | `2026-10-27T20:00:00Z` | `2026-10-27T19:54:00Z` | Tesla Cup 2026 | Envy vs GamerLegion | `exchange` | 45.50% | 54.50% | 2.20 / 1.83 | **GamerLegion** | [Hotspawn](https://www.hotspawn.com/matches/envy-vs-gamerlegion-tesla-cup-2026-1082901) | [Source](https://polymarket.com/event/cs2-envy-gl1-2026-10-27) |
| `1082792` | `2026-10-31T09:00:00Z` | `2026-10-31T08:54:00Z` | Moscow Cyber Games 2026 | HOTU vs The Huns | `model_vrs` | 85.18% | 14.82% | 1.17 / 6.75 | **HOTU** | [Hotspawn](https://www.hotspawn.com/matches/hotu-vs-the-huns-moscow-cyber-games-2026-1082792) | [Source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |
| `1082793` | `2026-10-31T13:00:00Z` | `2026-10-31T12:54:00Z` | Moscow Cyber Games 2026 | 5star vs 1WIN | `model_vrs` | 24.30% | 75.70% | 4.12 / 1.32 | **1WIN** | [Hotspawn](https://www.hotspawn.com/matches/5star-vs-1win-moscow-cyber-games-2026-1082793) | [Source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |

## 3. Mobile & Desktop Viewport Verification (Chromium)

| Viewport | `index.html` Overflow | `#freshness-strip` (y) | `#exec-quicknav` / `#exec-summary` (y) | First Pick Card / Row on `index.html` (y) | `picks.html` Overflow | First Pick on `picks.html` (y) | First Probability on `picks.html` (y) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `320x568` | `False` | `113..284px` | `290..328px` | `336..523px` | `False` | `368..391px` | `425..452px` |
| `390x844` | `False` | `117..288px` | `300..346px` | `360..567px` | `False` | `334..357px` | `392..421px` |
| `412x915` | `False` | `117..288px` | `300..346px` | `360..567px` | `False` | `334..357px` | `392..421px` |
| `768x1024` | `False` | `253..473px` | `491..836px` | `1145..1213px` | `False` | `710..732px` | `706..729px` |
| `1440x900` | `False` | `249..407px` | `425..659px` | `968..1036px` | `False` | `626..648px` | `622..645px` |

## 4. Flagged Irregularities & Limitations (Published on `review.html` and `unresolved.html`)

1. **Fixture `1079200` (`Color` vs `ex-Zero Tenacity`, NODWIN Clutch Series #13, `2026-10-25T18:00:00Z`):** Polymarket market `https://gamma-api.polymarket.com/markets/6072812` quoted an exact `0.50 / 0.50` midpoint (`bestBid: 0.49`, `bestAsk: 0.51`, `liquidity: $6,026.90`, `volume: null`). Because an exact 50/50 quote provides no directional edge, it is retained in `no_edge_lines` / `attempts` as non-directional market context and the fixture continues down the fallback ladder to Valve's official VRS standings (`standings_global_2026_10_05.md`: `Color` #57 with 1,249 pts vs `ex-Zero Tenacity` #93 with 1,066 pts), resolving to **Color** (`68.8%` vs `31.2%`, `model_vrs`).
2. **Fixture `1082858` (`Ground Zero` vs `Off Chops`, ESL Challenger League Season 51 Oceania Cup #2, `2026-10-26T03:00:00Z`):** Priced via the labelled wide-spread exchange tier (`exchange_wide`, spread 55 percentage points, liquidity $1,718.54) and mapped through the primary-sourced rename `THUNDER dOWNUNDER` -> `Off Chops` (`https://liquipedia.net/counterstrike/Logitech_G_Pro_Series/2026`, confirmed by 4/5 HLTV roster continuity at `https://www.hltv.org/team/14095/off-chops`).
3. **Fixtures `1083123` (`Grêmio` vs `Yawara`), `1082859` (`NEXVOID` vs `Alter Ego`), and `1082860` (`FlyQuest` vs `Staqued`):** Not listed on Polymarket or Pinnacle; priced via de-vigged Thunderpick decimal moneylines captured from BO3.gg match pages (`bookmaker_fallback`), explicitly flagged that the listing supplies observation timestamps rather than operator tick timestamps.
4. **Fixture `1081156` (`Spirit Academy` vs `LFO 10`, CCT Season 3 Europe Series #12, `2026-10-25T12:00:00Z`):** `LFO 10` is absent from Valve's monthly `2026-10-05` standings file; priced via `model_vrs_mirror` from HLTV's dated Valve ranking (`https://www.hltv.org/valve-ranking/teams/2026/october/22`, `Spirit Academy` #120 with 810 pts vs `LFO 10` #217 with 597 pts -> `Spirit Academy` `72.1%` vs `27.9%`).
5. **63 past-dated / locked Hotspawn CS2 feed entries (`state: not_open`):** Hotspawn's scheduled API (`status=scheduled`) continues to return fixtures whose sourced `lock` or `start` timestamp has passed (including `1079661` and `1081154` at `2026-10-24T16:54:00Z`). All 63 are retained in `matches.html` for full 83/83 feed parity and auditability, and withheld (`pick=None`, `probabilities=None`) from active picks.
