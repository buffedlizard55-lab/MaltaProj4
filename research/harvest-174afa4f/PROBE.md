# Session 174afa4f — fallback-source probe (diagnostic only)

Diagnostic only: no value recorded here is a price input. Hotspawn was not read for probabilities; no alias was guessed; nothing defaults to 50/50.

- Probed at `2026-10-24T05:54:23.730524Z` against snapshot `2026-10-24T05:54:23.068654Z`.
- Targets (open rows the featured exchange/Pinnacle tiers did not price): **13**

| ID | Match | Start (UTC) | Current state |
| --- | --- | --- | --- |
| 1081152 | HAVU vs Azuolas | 2026-10-24T11:00:00Z | priced by a lower tier (model_vrs) |
| 1081153 | Saint Sinners vs 6yuBoJlbl | 2026-10-24T14:00:00Z | priced by a lower tier (model_vrs) |
| 1081154 | BakS vs ILLYRIANS | 2026-10-24T17:00:00Z | priced by a lower tier (model_vrs) |
| 1082996 | Acend vs UNiTY | 2026-10-25T09:00:00Z | priced by a lower tier (model_vrs) |
| 1079198 | Metizport vs BakS | 2026-10-25T12:00:00Z | priced by a lower tier (exchange_wide) |
| 1081156 | Spirit Academy vs LFO 10 | 2026-10-25T12:00:00Z | priced by a lower tier (model_vrs_mirror) |
| 1081158 | FORZE Reload vs ex-RUSTEC | 2026-10-25T18:00:00Z | priced by a lower tier (model_vrs_mirror) |
| 1082858 | Ground Zero vs Off Chops | 2026-10-26T03:00:00Z | priced by a lower tier (exchange_wide) |
| 1082859 | NEXVOID vs Alter Ego | 2026-10-26T03:00:00Z | priced by a lower tier (bookmaker_fallback) |
| 1082860 | FlyQuest vs Staqued | 2026-10-27T03:00:00Z | priced by a lower tier (bookmaker_fallback) |
| 1082861 | Rooster vs Abyssal | 2026-10-27T03:00:00Z | priced by a lower tier (model_vrs) |
| 1082792 | HOTU vs The Huns | 2026-10-31T09:00:00Z | priced by a lower tier (model_vrs) |
| 1082793 | 5star vs 1WIN | 2026-10-31T13:00:00Z | priced by a lower tier (model_vrs) |

## HLTV first

- Ranking list ([official](https://www.hltv.org/ranking/teams)): not read: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run.; labels present: `none`. The collector already reads each exact team page for gap rows; this only measures whether polling the list would add teams.
- Fixture odds-table scan `1081152` HAVU vs Azuolas: not read: Skipped after earlier access/rate restriction on this host: 403; markers `None`; decimal tokens `None` — .
- Fixture odds-table scan `1081153` Saint Sinners vs 6yuBoJlbl: not read: Skipped after earlier access/rate restriction on this host: 403; markers `None`; decimal tokens `None` — .
- Fixture odds-table scan `1081154` BakS vs ILLYRIANS: not read: Skipped after earlier access/rate restriction on this host: 403; markers `None`; decimal tokens `None` — .
- Fixture odds-table scan `1082996` Acend vs UNiTY: not read: Skipped after earlier access/rate restriction on this host: 403; markers `None`; decimal tokens `None` — .
- Fixture odds-table scan `1079198` Metizport vs BakS: not read: Skipped after earlier access/rate restriction on this host: 403; markers `None`; decimal tokens `None` — .
- Fixture odds-table scan `1081156` Spirit Academy vs LFO 10: not read: Skipped after earlier access/rate restriction on this host: 403; markers `None`; decimal tokens `None` — .

## Esportsbooks and esports betting lines

- Pinnacle near-miss diagnostic: CS2 matchup candidates `18`; `1081152` exact=0 same-pair/other-start=0 one-team/same-start=0; `1081153` exact=0 same-pair/other-start=0 one-team/same-start=0; `1081154` exact=0 same-pair/other-start=0 one-team/same-start=0; `1082996` exact=0 same-pair/other-start=0 one-team/same-start=0; `1079198` exact=0 same-pair/other-start=0 one-team/same-start=0; `1081156` exact=0 same-pair/other-start=0 one-team/same-start=0; `1081158` exact=0 same-pair/other-start=0 one-team/same-start=0; `1082858` exact=0 same-pair/other-start=0 one-team/same-start=0; `1082859` exact=0 same-pair/other-start=0 one-team/same-start=0; `1082860` exact=0 same-pair/other-start=0 one-team/same-start=0; `1082861` exact=0 same-pair/other-start=0 one-team/same-start=0; `1082792` exact=0 same-pair/other-start=0 one-team/same-start=0; `1082793` exact=0 same-pair/other-start=0 one-team/same-start=0
- BO3 pagination: read at `2026-10-24T05:56:05.365168Z` (230221 bytes, sha `de04fc5d4b7f…`); first-page items `100` of page limit `100`; payload keys `['links', 'results', 'total']`; total field `{"count": 279, "pages": 3, "offset": 0, "limit": 100}`.
- EGamersWorld listing discovery ([official](https://egamersworld.com/counterstrike/matches)): not read: HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run.; readings parsed `0`; exact bound readings for targets: `0`.
- Kalshi public markets API ([official](https://api.elections.kalshi.com/trade-api/v2/markets?status=open&limit=200)): read at `2026-10-24T05:57:41.713609Z` (949299 bytes, sha `0eb5b53a2c51…`); target labels present `none`.
- OddsPortal ([official](https://www.oddsportal.com/esports/counter-strike/)): read at `2026-10-24T05:49:57.277496Z` (338191 bytes, sha `e0bc089ec8e4…`); target labels present `['UNiTY']`.

Full hashed endpoint records are in `probe.json`. No price from this probe was applied to any pick or percentage.
