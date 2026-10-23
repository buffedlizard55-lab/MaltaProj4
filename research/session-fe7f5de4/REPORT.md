# Session fe7f5de4 — complete CS2 pick coverage and mobile access

**Status:** research in progress. This report does not claim a fresh source read until the dated harvest and its receipts are present.

## Requested outcome

1. Discover every CS2 fixture currently listed by Hotspawn and recheck the inventory automatically.
2. Resolve each open fixture through the existing external-market path where possible. For only the remaining rows, research HLTV first and then esportsbook/listing sources. Hotspawn is never a probability input.
3. Publish an obvious pick and both teams' supported win probabilities. Where evidence cannot support a percentage or pick, leave the unsupported fields blank and publish a separate unresolved/limitations section linked from the executive summary.
4. Make the updated-picks destination and the unresolved section easy to find and read on a phone.
5. Replay every displayed value from retained evidence, flag irregularities, run all build/browser gates, and merge only a verified build.

## Starting-point audit (committed snapshot, not a new web observation)

`data/latest.json` says it was generated at **2026-10-22T20:15:52.839962Z**, with fixture evidence observed at **2026-10-22T20:12:15.855097Z**. It contains **84 retained rows and 23 rows marked open**. Of those 23, **23 have a directional pick and 21 have numerical probabilities**. The two research-only rows in this dated file are:

| Hotspawn fixture | Teams | Published method | Published limitation | Official fixture link |
| --- | --- | --- | --- | --- |
| 1081149 | FORZE Reload vs LFO 10 | `research_vrs_single`; pick FORZE Reload; no percentage | One-sided Valve standings evidence only; HLTV bracket slot lacked team labels, so club pages were used for roster identity | [Hotspawn fixture](https://www.hotspawn.com/matches/forze-reload-vs-lfo-10-cct-europe-2026-series-12-1081149) |
| 1082860 | FlyQuest vs Staqued | `research_rank_single`; pick FlyQuest; no percentage | One-sided HLTV world-ranking evidence only; no verified two-way line | [Hotspawn fixture](https://www.hotspawn.com/matches/flyquest-vs-staqued-dfrag-invitational-2026-1082860) |

These are historical file contents, not assertions that the matches are still open or that the same picks remain current. A fresh harvest must supersede them.

## Source order and acceptance rules

| Order | Source | Permitted use | Reject / flag |
| --- | --- | --- | --- |
| 1 | [Hotspawn CS2 lobby](https://play.hotspawn.com/cs2-pickems), [general lobby](https://play.hotspawn.com/lobby), and the fixture API used by those pages | Fixture membership, teams, competition, start/lock and official row link | Crowd percentages or any Hotspawn pick signal as probability; partial or wrong-game discovery replacing a good inventory |
| 2 | [Polymarket Gamma API](https://gamma-api.polymarket.com/sports) | Exact team-pair/start, two-sided series-winner prices with raw timestamps, spread and liquidity | Wrong market type, ambiguous identity, one-sided/equal placeholders, stale or illiquid quotes |
| 3 | [HLTV matches](https://www.hltv.org/matches), exact fixture pages and club pages | Exact identity, start, lineup and ranking context; HLTV's dated Valve-points view may feed the separately labelled originated VRS model | Fan votes, ranking order presented as a calibrated probability, numeric comparison rows not independently confirmed at an operator |
| 4 | [Pinnacle guest esports API](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight) | Exact two-way moneyline with reproducible fixture/market identity | Alias guesses, wrong start/format, absent timestamps or unmatched markets |
| 5 | Official bookmaker/listing pages already supported by the collector, including [EGamersWorld CS2 listings](https://egamersworld.com/counterstrike/matches), [Thunderpick CS2](https://thunderpick.io/esports/cs2-betting), and [GG.BET Counter-Strike](https://gg.bet/en/esports/counter-strike) | Only a validated, dated, two-sided series line bound to both labels; listing provenance must remain explicit | `1.8 / 1.8` and other placeholders, refused access treated as “no odds,” parsed values without a current source receipt |
| 6 | [Valve's official regional standings](https://github.com/ValveSoftware/counter-strike_regional_standings) and Valve's published model formula/calibration | Clearly labelled original model line only when both team identities and roster continuity resolve | Invented rank-to-probability conversion, one-team points presented as a two-team probability, ambiguous roster identity |

## Verification plan

- Preserve raw source receipts, observation timestamps and SHA-256 hashes in the dated harvest.
- Compare the complete Hotspawn ID set across API, CS2 page and lobby; do not confuse retained historical rows with currently open fixtures.
- Recompute every accepted de-vigged market probability and every VRS expected score from the stored inputs.
- Confirm every open row appears on the pick board; every no-percentage/no-pick row appears in both the executive-summary limitations and the dedicated unresolved page.
- Check every table row for an external source link and every generated internal link/asset.
- Exercise 320px and 390px phone viewports, keyboard/hash navigation, expiry behavior, accessibility and horizontal overflow.
- Record any contradiction or unverified item on Flagged for Review rather than filling it in.

## Fresh research results

Pending the first current-day harvest. No new probability, roster, alias, or match fact has been added by this session yet.
