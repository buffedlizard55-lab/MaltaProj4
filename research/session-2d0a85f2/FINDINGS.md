# Session 2d0a85f2 — line-by-line verification, gap research and irregularities (2026-10-21)

Scope: independent of session 96ea1af8 (active, owns `scripts/build.py`, `site/assets/*`, root staged
`*.html`, `README.md`, `pages.yml`). Nothing in another session's scope is edited here. Raw receipts:
[`receipts-2026-10-21.json`](receipts-2026-10-21.json). Board evidence:
[`research/harvest-2d0a85f2/board.md`](../harvest-2d0a85f2/board.md) (fresh CI refresh, run
[39664773335](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39664773335)) and
[`live-board.md`](../harvest-2d0a85f2/live-board.md) (the bytes a phone visitor received at 19:20Z).

## 1. Board state verified at 2026-10-21T19:51Z (fresh refresh == live published board)

76 Hotspawn CS2 records, 13 open, 12 carry a pick, 9 publish both percentages; coverage
`verified` with api/page/lobby/retained all 76 (three-source parity holds).
Open rows without a percentage: **1082837** Zetta vs LOS NINOS, **1082858** Ground Zero vs Off Chops,
**1082860** FlyQuest vs Staqued (research-only tiers). Open row with **no pick at all**: **1081597**
benched gods vs TitanFlow. No open row is shown past its evidence expiry. Every priced open row links its
evidence (Polymarket event page or Valve's standings blob); the three research-only rows carry their HLTV
match page in `hltv_context.source` but no `evidence[]` entry — see irregularity I-4.

## 2. Methodology verified against official sources (line by line)

| Claim in repo | Official source checked | Result |
| --- | --- | --- |
| VRS Glicko `g`, `E`, `rd = 75` ([scripts/vrs.py](../../scripts/vrs.py)) | Valve [`model/glicko.js`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/model/glicko.js), [`model/fit.js`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/model/fit.js) via api.github.com | **Verified.** `Q = ln(10)/400`, `g = 1/sqrt(1+3Q²RD²/π²)`, `ev = 1/(1+10^(g(r−ro)/−400))`, `defaultGlickoParams.rd = 75` match the repo exactly. |
| Calibration slope 0.7986 / intercept 0.126 | Valve [`modelfit.png`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/modelfit.png), downloaded (sha256 c8fc0fd5…) and read as an image, kept at [`modelfit-official.png`](modelfit-official.png) | **Verified.** Chart prints `y = 0.7986x + 0.126`. The repo applies the slope symmetrically around 50% instead of the intercept; that deviation is disclosed in the file docstring and keeps the two sides summing to 1. |
| Roster-overlap identity rule (≥3 shared players) | Valve [`model/team.js`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/model/team.js) `TEAM_OVERLAP_TO_SHARE_ROSTER = 3` | **Verified.** |
| Vendored standings are unmodified and current | `git hash-object data/vrs/standings_global_2026_10_05.md` = `2aa2805…` == official blob sha; official `live/2026` listing has no newer global file; repo HEAD of Valve = `eec4853` (2026-10-05) | **Verified.** sha256 matches `data/vrs/meta.json`. |
| Exchange gates: liquidity ≥ $100, spread ≤ 25 (wide tier ≤ 60) | [scripts/core.py](../../scripts/core.py) lines 258–274 | **Verified by reading**; a genuine 25.0-point spread passes ("no greater than 25"), below-$100 liquidity is never accepted. |
| Three Hotspawn views agree, 4×/h refresh, 8 h expiry | CI source_checks (all three 200 at 19:48Z) and live build receipt 19:20Z | **Verified.** |

## 3. Gap research — HLTV first, then esportsbooks (per the brief)

### 1081597 benched gods vs TitanFlow (2026-10-22T11:00Z) — currently NO pick
- HLTV: no match page with this exact pair **and** Hotspawn's UTC start; HLTV's own listings place the pair at a
  different date/time (irregularity I-1). HLTV therefore supplies no ranks/lineups for this fixture.
- Polymarket (registry + events), Pinnacle public esports lines: no exact pair+start (CI attempt ledger).
- Thunderpick via bo3.gg: **no line** for this fixture while the same event page shows 1.55/2.24 for
  Quintessence vs Ryvex (R2) → absence is per-fixture.
- EGamersWorld: identical 1.8/1.8 placeholder → rejected by policy (R3). GG.BET: HTTP 403 (CI).
- Kalshi: zero open CS2 game markets at observation time (R4).
- **Resolvable as a research pick, not a price.** Valve's standings carry two `benched gods` rosters
  (#157 811 pts, #329 516 pts). The fixture lineup published on bo3.gg (R1) and the played HLTV lineup of the
  team's latest match (R6, official HLTV) are both `Wign, K014NZ, facer, yoyoS2, norescue` → 5 shared players
  with #157, 2 with #329 → exactly one entry satisfies Valve's own ≥3 rule. TitanFlow is absent from the
  standings. Exactly-one-team-listed is precisely the `research_vrs_single` condition, so the honest upgrade is:
  **pick = benched gods, no percentage**, limitation text stating the roster anchor and that no market line
  exists. Implemented at integration by `scripts/apply_2d0a85f2.py` + the collector option requested in
  REQUESTS.md (R-1/R-2); not applied now because pick-table data is a shared output.

### 1082837 Zetta vs LOS NINOS (2026-10-21T22:00Z) — research pick, no percentage
- HLTV match 2399865 confirms identity, event, Swiss round 5 and the 22:00Z start; its betting block carries no
  numeric odds (Stake promo only); its 75/25 community vote is rejected by policy (R9).
- The 22:00Z slot of the same event is carried by bo3.gg and Polymarket as **Alianza Lima Esports vs Los Niños**
  (R10) — an unsourced label conflict, so that price is not attachable (wrong-game risk). Polymarket registry has
  no Zetta market for this start (CI).
- Thunderpick/bo3.gg: fixture absent; Kalshi empty; Pinnacle absent; GG.BET 403.
- **Outcome stands**: research pick Zetta (HLTV #241 vs unranked opponent), blank percentages, limitation already
  published; this session adds the R9/R10 receipts and irregularity I-2 to the Flagged page payload.

### 1082858 Ground Zero vs Off Chops and 1082860 FlyQuest vs Staqued (DFRAG Invitational 2026, LAN Brisbane)
- bo3.gg event page lists all four DFRAG fixtures with **no lines at all** (R11); the page's own FAQ says rosters
  are unannounced, consistent with books staying off the event.
- Polymarket/Pinnacle absent (CI); Kalshi empty (R4); GG.BET 403 (CI); EGW re-observation failed (CI).
- Valve standings resolve Ground Zero (#136, 878 pts) and FlyQuest (#86, 1093 pts) but not Off Chops / Staqued →
  exactly-one-team cases; the collector already publishes the correct research-only picks. No percentage can be
  sourced without inventing one. **Outcome stands**, receipts added.

## 4. Irregularities flagged for review (nothing hidden, nothing filled in)

- **I-1 (start conflict, 1081597).** HLTV listings place benched gods vs TitanFlow at a different date/time than
  Hotspawn/EGW/bo3.gg (2026-10-22T11:00Z). Links: [HLTV 2026-10-22 filter](https://www.hltv.org/matches?selectedDate=2026-10-22),
  [HLTV 2026-10-24 filter](https://www.hltv.org/matches?selectedDate=2026-10-24),
  [Hotspawn fixture](https://www.hotspawn.com/matches/benched-gods-vs-titanflow-cct-europe-2026-challengers-8-1081597).
  Effect: HLTV evidence cannot attach until sources agree; the row keeps Hotspawn's timestamps.
- **I-2 (identity conflict, 22:00Z CCT SA #7 slot).** Hotspawn+HLTV say Zetta vs LOS NINOS; bo3.gg+Polymarket carry
  Alianza Lima Esports vs Los Niños. No alias evidence exists, so the Polymarket price is withheld.
- **I-3 (source availability).** GG.BET returns HTTP 403 to the collector and EGamersWorld re-observation fails;
  both remain listed as access checks, not adapters. Kalshi currently lists no open CS2 markets at all. These are
  collection limits, not proof that no line exists.
- **I-4 (evidence link gap on research-only rows).** Rows 1082837/1082858/1082860 carry their HLTV URL only in
  `hltv_context.source`; the published CSV's `source` column is empty for them even though the user requirement is
  "every table row must have a source link". Fix requested in REQUESTS.md (R-3): surface the HLTV match link as the
  row's source in the CSV and tables, labelled as identity evidence (not a price).
- **I-5 (fan vote proximity).** HLTV's page for 1082837 displays a 75/25 community vote. It is excluded by policy;
  flagged so a reviewer can confirm it never entered any published number.

## 5. What this session did NOT do

No probability, pick, alias or roster continuity was invented; no file in another session's scope was touched; the
pick-table data was not modified (shared output — applied at integration only). Every "no line" statement above is
backed by a dated receipt or by the CI attempt ledger of the same snapshot the live site serves.
