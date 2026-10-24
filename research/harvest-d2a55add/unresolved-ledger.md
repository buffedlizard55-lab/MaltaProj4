# Unresolved & non-featured pick ledger — session d2a55add

Snapshot generated `2026-10-24T05:33:25.228862Z`; fixtures observed `2026-10-24T05:29:46.418656Z`.

Every open Hotspawn CS2 row that the featured strict-exchange tier did not resolve, in start order. HLTV is tried first, then esportsbook/betting lines, then the originated VRS model, then research-only evidence. Nothing here invents a price: a blank percentage means unverified.

| Count | Rows |
| --- | --- |
| Non-featured open rows | 13 |
| …with a win probability (book/model/wide) | 13 |
| …research-only pick, no percentage | 0 |
| …unresolved, no pick at all | 0 |
| …missing a recorded HLTV attempt (irregularity) | 0 |
| …missing a recorded book attempt (irregularity) | 0 |

## HAVU vs Azuolas (`1081152`)

- Competition: CCT Europe 2026 Series #12 · starts 2026-10-24T11:00:00Z UTC · lock 2026-10-24T10:54:00Z UTC
- Published answer: **Our own VRS model line** — pick `HAVU`, method `model_vrs`, probabilities `[0.5815710671661513, 0.41842893283384874]`
- Exchange (featured) step: no usable line
- HLTV first: no usable line
- Esportsbook lines next: access refused or failed
- Limitation: Not applicable: this row carries a win probability (Valve’s official standings points through Valve’s own expected-win formula).
- Hotspawn source: https://www.hotspawn.com/matches/havu-vs-azuolas-cct-europe-2026-series-12-1081152
  - attempt `HLTV` → unresolved: HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. Recent results and head-to-head wins are recorded for the final research tier only; no probability is derived from them. (https://www.hltv.org/matches/2399502/havu-vs-azuolas-cct-2026-europe-series-12)
  - attempt `Pinnacle` → unresolved: No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - attempt `Thunderpick` → unresolved: Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - attempt `GG.BET` → error: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - attempt `Thunderpick (via BO3.gg API)` → unresolved: Fixture found on BO3.gg with exact UTC start, but no active sportsbook moneyline is posted yet (bet_updates is null). (https://bo3.gg/matches/havu-vs-azuolas-24-10-2026)

## Saint Sinners vs 6yuBoJlbl (`1081153`)

- Competition: CCT Europe 2026 Series #12 · starts 2026-10-24T14:00:00Z UTC · lock 2026-10-24T13:54:00Z UTC
- Published answer: **Our own VRS model line** — pick `6yuBoJlbl`, method `model_vrs`, probabilities `[0.2930462353295323, 0.7069537646704678]`
- Exchange (featured) step: no usable line
- HLTV first: no usable line
- Esportsbook lines next: access refused or failed
- Limitation: Not applicable: this row carries a win probability (Valve’s official standings points through Valve’s own expected-win formula).
- Hotspawn source: https://www.hotspawn.com/matches/saint-sinners-vs-6yubojlbl-cct-europe-2026-series-12-1081153
  - attempt `HLTV` → unresolved: HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. Recent results and head-to-head wins are recorded for the final research tier only; no probability is derived from them. (https://www.hltv.org/matches/2399503/6yubojlbl-vs-saint-sinners-cct-2026-europe-series-12)
  - attempt `Pinnacle` → unresolved: No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - attempt `Thunderpick` → unresolved: Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - attempt `GG.BET` → error: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - attempt `Thunderpick (via BO3.gg API)` → unresolved: Fixture found on BO3.gg with exact UTC start, but no active sportsbook moneyline is posted yet (bet_updates is null). (https://bo3.gg/matches/6yubojlbl-vs-saint-sinners-24-10-2026)

## BakS vs ILLYRIANS (`1081154`)

- Competition: CCT Europe 2026 Series #12 · starts 2026-10-24T17:00:00Z UTC · lock 2026-10-24T16:54:00Z UTC
- Published answer: **Our own VRS model line** — pick `BakS`, method `model_vrs`, probabilities `[0.6875248688198947, 0.3124751311801053]`
- Exchange (featured) step: no usable line
- HLTV first: no usable line
- Esportsbook lines next: access refused or failed
- Limitation: Not applicable: this row carries a win probability (Valve’s official standings points through Valve’s own expected-win formula).
- Hotspawn source: https://www.hotspawn.com/matches/baks-vs-illyrians-cct-europe-2026-series-12-1081154
  - attempt `HLTV` → unresolved: HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. Recent results and head-to-head wins are recorded for the final research tier only; no probability is derived from them. (https://www.hltv.org/matches/2399504/baks-vs-illyrians-cct-2026-europe-series-12)
  - attempt `Pinnacle` → unresolved: No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - attempt `Thunderpick` → unresolved: Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - attempt `GG.BET` → error: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - attempt `Thunderpick (via BO3.gg API)` → unresolved: Fixture found on BO3.gg with exact UTC start, but no active sportsbook moneyline is posted yet (bet_updates is null). (https://bo3.gg/matches/baks-esports-vs-illyrians-24-10-2026)

## Acend vs UNiTY (`1082996`)

- Competition: NODWIN Clutch Series #13 · starts 2026-10-25T09:00:00Z UTC · lock 2026-10-25T08:54:00Z UTC
- Published answer: **Our own VRS model line** — pick `Acend`, method `model_vrs`, probabilities `[0.5334625793926856, 0.4665374206073144]`
- Exchange (featured) step: no usable line
- HLTV first: no usable line
- Esportsbook lines next: access refused or failed
- Limitation: Not applicable: this row carries a win probability (Valve’s official standings points through Valve’s own expected-win formula).
- Hotspawn source: https://www.hotspawn.com/matches/acend-vs-unity-nodwin-clutch-series-13-1082996
  - attempt `HLTV` → unresolved: HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. Recent results and head-to-head wins are recorded for the final research tier only; no probability is derived from them. (https://www.hltv.org/matches/2399112/acend-vs-unity-nodwin-clutch-series-13)
  - attempt `Pinnacle` → unresolved: No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - attempt `Thunderpick` → unresolved: Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - attempt `GG.BET` → error: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - attempt `Thunderpick (via BO3.gg API)` → unresolved: Fixture found on BO3.gg with exact UTC start, but no active sportsbook moneyline is posted yet (bet_updates is null). (https://bo3.gg/matches/acend-cs2-vs-unity-25-10-2026)
  - attempt `Book listing gap recheck` → unresolved: Skipped after earlier access/rate restriction on this host: 403 (https://egamersworld.com/counterstrike/match/Nk9F-Ov54e/acend-vs-unity-esports-iwaKSVfgf)

## Metizport vs BakS (`1079198`)

- Competition: NODWIN Clutch Series #13 · starts 2026-10-25T12:00:00Z UTC · lock 2026-10-25T11:54:00Z UTC
- Published answer: **Betting-market line · wide quote** — pick `Metizport`, method `exchange_wide`, probabilities `[0.705, 0.295]`
- Exchange (featured) step: resolved
- HLTV first: no usable line
- Esportsbook lines next: no usable line
- Limitation: Not applicable: this row carries a win probability (Polymarket quote past the strict spread ceiling, published as low confidence).
- Hotspawn source: https://www.hotspawn.com/matches/metizport-vs-baks-nodwin-clutch-series-13-1079198
  - attempt `HLTV` → unresolved: HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. Recent results and head-to-head wins are recorded for the final research tier only; no probability is derived from them. (https://www.hltv.org/matches/2399113/metizport-vs-baks-nodwin-clutch-series-13)
  - attempt `Pinnacle` → unresolved: No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)

## Spirit Academy vs LFO 10 (`1081156`)

- Competition: CCT Europe 2026 Series #12 · starts 2026-10-25T12:00:00Z UTC · lock 2026-10-25T11:54:00Z UTC
- Published answer: **Our VRS model line · HLTV mirror** — pick `Spirit Academy`, method `model_vrs_mirror`, probabilities `[0.7118171988597648, 0.2881828011402352]`
- Exchange (featured) step: no usable line
- HLTV first: no usable line
- Esportsbook lines next: access refused or failed
- Limitation: Not applicable: this row carries a win probability (Valve points published by HLTV’s dated ranking, through the same formula; not a market price).
- Hotspawn source: https://www.hotspawn.com/matches/spirit-academy-vs-lfo-10-cct-europe-2026-series-12-1081156
  - attempt `HLTV` → unresolved: HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. Recent results and head-to-head wins are recorded for the final research tier only; no probability is derived from them. (https://www.hltv.org/matches/2399506/spirit-academy-vs-lfo-10-cct-2026-europe-series-12)
  - attempt `Pinnacle` → unresolved: No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - attempt `Thunderpick` → unresolved: Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - attempt `GG.BET` → error: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - attempt `Thunderpick (via BO3.gg API)` → unresolved: No exact team-pair and UTC-start match in the live BO3.gg CS2 feed. (https://api.bo3.gg/api/v1/matches?page[offset]=0&page[limit]=100&filter[matches.status][in]=upcoming&filter[matches.discipline_id][eq]=1&sort=start_date&with=teams,tournament)

## FORZE Reload vs ex-RUSTEC (`1081158`)

- Competition: CCT Europe 2026 Series #12 · starts 2026-10-25T18:00:00Z UTC · lock 2026-10-25T17:54:00Z UTC
- Published answer: **Our VRS model line · HLTV mirror** — pick `FORZE Reload`, method `model_vrs_mirror`, probabilities `[0.5740422049729164, 0.42595779502708364]`
- Exchange (featured) step: no usable line
- HLTV first: no usable line
- Esportsbook lines next: access refused or failed
- Limitation: Not applicable: this row carries a win probability (Valve points published by HLTV’s dated ranking, through the same formula; not a market price).
- Hotspawn source: https://www.hotspawn.com/matches/forze-reload-vs-ex-rustec-cct-europe-2026-series-12-1081158
  - attempt `HLTV` → unresolved: HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. Recent results and head-to-head wins are recorded for the final research tier only; no probability is derived from them. (https://www.hltv.org/matches/2399508/forze-reload-vs-ex-rustec-cct-2026-europe-series-12)
  - attempt `Pinnacle` → unresolved: No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - attempt `Thunderpick` → unresolved: Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - attempt `GG.BET` → error: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - attempt `Thunderpick (via BO3.gg API)` → unresolved: Fixture found on BO3.gg with exact UTC start, but no active sportsbook moneyline is posted yet (bet_updates is null). (https://bo3.gg/matches/forze-reload-vs-ex-rustec-25-10-2026)

## Ground Zero vs Off Chops (`1082858`)

- Competition: DFRAG Invitational 2026 · starts 2026-10-26T03:00:00Z UTC · lock 2026-10-26T02:54:00Z UTC
- Published answer: **Betting-market line · wide quote** — pick `Off Chops`, method `exchange_wide`, probabilities `[0.285, 0.715]`
- Exchange (featured) step: resolved
- HLTV first: no usable line
- Esportsbook lines next: no usable line
- Limitation: Not applicable: this row carries a win probability (Polymarket quote past the strict spread ceiling, published as low confidence).
- Hotspawn source: https://www.hotspawn.com/matches/ground-zero-vs-off-chops-dfrag-invitational-2026-1082858
  - attempt `HLTV` → unresolved: HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. Recent results and head-to-head wins are recorded for the final research tier only; no probability is derived from them. (https://www.hltv.org/matches/2399888/ground-zero-vs-off-chops-dfrag-invitational-2026)
  - attempt `Pinnacle` → unresolved: No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)

## NEXVOID vs Alter Ego (`1082859`)

- Competition: DFRAG Invitational 2026 · starts 2026-10-26T03:00:00Z UTC · lock 2026-10-26T02:54:00Z UTC
- Published answer: **Bookmaker line · researched listing** — pick `NEXVOID`, method `bookmaker_fallback`, probabilities `[0.5755968169761273, 0.4244031830238727]`
- Exchange (featured) step: no usable line
- HLTV first: no usable line
- Esportsbook lines next: resolved
- Limitation: Not applicable: this row carries a win probability (A dated two-way price read from a bookmaker listing page).
- Hotspawn source: https://www.hotspawn.com/matches/nexvoid-vs-alter-ego-dfrag-invitational-2026-1082859
  - attempt `HLTV` → unresolved: HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. Recent results and head-to-head wins are recorded for the final research tier only; no probability is derived from them. (https://www.hltv.org/matches/2399889/nexvoid-vs-alter-ego-dfrag-invitational-2026)
  - attempt `Pinnacle` → unresolved: No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - attempt `Thunderpick` → unresolved: Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - attempt `GG.BET` → error: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - attempt `Thunderpick (via BO3.gg API)` → resolved: Exact pair and UTC start verified on BO3.gg CS2 API; live Thunderpick series moneyline (1.6 / 2.17) validated. (https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026)
  - attempt `Book research` → resolved: Exact fixture id, opponent pair and UTC start verified against the listed two-way book line; probabilities de-vigged by scripts.core.quote_book and replayed by the validator. (https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026)

## FlyQuest vs Staqued (`1082860`)

- Competition: DFRAG Invitational 2026 · starts 2026-10-27T03:00:00Z UTC · lock 2026-10-27T02:54:00Z UTC
- Published answer: **Bookmaker line · researched listing** — pick `FlyQuest`, method `bookmaker_fallback`, probabilities `[0.9230059226213368, 0.07699407737866316]`
- Exchange (featured) step: no usable line
- HLTV first: no usable line
- Esportsbook lines next: resolved
- Limitation: Not applicable: this row carries a win probability (A dated two-way price read from a bookmaker listing page).
- Hotspawn source: https://www.hotspawn.com/matches/flyquest-vs-staqued-dfrag-invitational-2026-1082860
  - attempt `HLTV` → unresolved: HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. Recent results and head-to-head wins are recorded for the final research tier only; no probability is derived from them. (https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026)
  - attempt `Pinnacle` → unresolved: No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - attempt `Thunderpick` → unresolved: Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - attempt `GG.BET` → error: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - attempt `Thunderpick (via BO3.gg API)` → resolved: Exact pair and UTC start verified on BO3.gg CS2 API; live Thunderpick series moneyline (1.001 / 12.0) validated. (https://bo3.gg/matches/flyquest-vs-staqued-27-10-2026)
  - attempt `Book research` → resolved: Exact fixture id, opponent pair and UTC start verified against the listed two-way book line; probabilities de-vigged by scripts.core.quote_book and replayed by the validator. (https://bo3.gg/matches/flyquest-vs-staqued-27-10-2026)

## Rooster vs Abyssal (`1082861`)

- Competition: DFRAG Invitational 2026 · starts 2026-10-27T03:00:00Z UTC · lock 2026-10-27T02:54:00Z UTC
- Published answer: **Our own VRS model line** — pick `Abyssal`, method `model_vrs`, probabilities `[0.4821232933348442, 0.5178767066651557]`
- Exchange (featured) step: no usable line
- HLTV first: no usable line
- Esportsbook lines next: access refused or failed
- Limitation: Not applicable: this row carries a win probability (Valve’s official standings points through Valve’s own expected-win formula).
- Hotspawn source: https://www.hotspawn.com/matches/rooster-vs-abyssal-dfrag-invitational-2026-1082861
  - attempt `HLTV` → unresolved: HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. Recent results and head-to-head wins are recorded for the final research tier only; no probability is derived from them. (https://www.hltv.org/matches/2399891/rooster-vs-abyssal-dfrag-invitational-2026)
  - attempt `Pinnacle` → unresolved: No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - attempt `Thunderpick` → unresolved: Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - attempt `GG.BET` → error: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - attempt `Thunderpick (via BO3.gg API)` → unresolved: Fixture found on BO3.gg with exact UTC start, but no active sportsbook moneyline is posted yet (bet_updates is null). (https://bo3.gg/matches/rooster-vs-abyssal-27-10-2026)
  - attempt `Book listing gap recheck` → unresolved: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://egamersworld.com/counterstrike/match/4kaAQWgKEx/rooster-vs-team-abyssal-P1tTp3RAg8)

## HOTU vs The Huns (`1082792`)

- Competition: Moscow Cyber Games 2026 · starts 2026-10-31T09:00:00Z UTC · lock 2026-10-31T08:54:00Z UTC
- Published answer: **Our own VRS model line** — pick `HOTU`, method `model_vrs`, probabilities `[0.851799765370461, 0.14820023462953902]`
- Exchange (featured) step: no usable line
- HLTV first: no usable line
- Esportsbook lines next: access refused or failed
- Limitation: Not applicable: this row carries a win probability (Valve’s official standings points through Valve’s own expected-win formula).
- Hotspawn source: https://www.hotspawn.com/matches/hotu-vs-the-huns-moscow-cyber-games-2026-1082792
  - attempt `HLTV` → unresolved: HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. Recent results and head-to-head wins are recorded for the final research tier only; no probability is derived from them. (https://www.hltv.org/matches/2399437/hotu-vs-the-huns-gluck-moscow-cyber-games-2026)
  - attempt `Pinnacle` → unresolved: No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - attempt `Thunderpick` → unresolved: Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - attempt `GG.BET` → error: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - attempt `Thunderpick (via BO3.gg API)` → unresolved: No exact team-pair and UTC-start match in the live BO3.gg CS2 feed. (https://api.bo3.gg/api/v1/matches?page[offset]=0&page[limit]=100&filter[matches.status][in]=upcoming&filter[matches.discipline_id][eq]=1&sort=start_date&with=teams,tournament)
  - attempt `Book listing gap recheck` → unresolved: Skipped after earlier access/rate restriction on this host: 403 (https://egamersworld.com/counterstrike/match/EkalRNMvVx/hotu-vs-the-huns-esports-SfdtzDhiK)

## 5star vs 1WIN (`1082793`)

- Competition: Moscow Cyber Games 2026 · starts 2026-10-31T13:00:00Z UTC · lock 2026-10-31T12:54:00Z UTC
- Published answer: **Our own VRS model line** — pick `1WIN`, method `model_vrs`, probabilities `[0.242985776930831, 0.757014223069169]`
- Exchange (featured) step: no usable line
- HLTV first: no usable line
- Esportsbook lines next: access refused or failed
- Limitation: Not applicable: this row carries a win probability (Valve’s official standings points through Valve’s own expected-win formula).
- Hotspawn source: https://www.hotspawn.com/matches/5star-vs-1win-moscow-cyber-games-2026-1082793
  - attempt `HLTV` → unresolved: HLTV betting table does not expose a numeric two-way line in this response. Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity. Recent results and head-to-head wins are recorded for the final research tier only; no probability is derived from them. (https://www.hltv.org/matches/2399438/1win-vs-5star-gluck-moscow-cyber-games-2026)
  - attempt `Pinnacle` → unresolved: No exact team-pair and UTC-start match in retrieved feed. (https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
  - attempt `Thunderpick` → unresolved: Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds. (https://thunderpick.io/esports/cs2-betting)
  - attempt `GG.BET` → error: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. (https://gg.bet/en/esports/counter-strike)
  - attempt `Thunderpick (via BO3.gg API)` → unresolved: No exact team-pair and UTC-start match in the live BO3.gg CS2 feed. (https://api.bo3.gg/api/v1/matches?page[offset]=0&page[limit]=100&filter[matches.status][in]=upcoming&filter[matches.discipline_id][eq]=1&sort=start_date&with=teams,tournament)
  - attempt `Book listing gap recheck` → unresolved: Skipped after earlier access/rate restriction on this host: 403 (https://egamersworld.com/counterstrike/match/EkalRNMvVx/1win-vs-5star-esports-4hTvdd1uN)
