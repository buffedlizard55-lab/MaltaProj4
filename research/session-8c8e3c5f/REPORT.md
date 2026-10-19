# Session 8c8e3c5f — every-match picks: research for the rows the featured method cannot resolve (2026-10-19)

## What was asked

A pick for **every** Hotspawn CS2 match, including low-tier fixtures not covered by
Polymarket; for matches that cannot be resolved like the featured picks, look first
to HLTV and then to esportsbook lines; a separate unresolved-picks + limitations
section inside the executive summary; and an executive summary whose links make the
updated picks findable on a phone in seconds.

## Fresh-snapshot gap audit (the starting point, measured, not assumed)

Harvest run **39197881440** (real unmodified `scripts.refresh` in GitHub Actions,
snapshot generated 2026-10-19T04:07:37Z, committed at
[`research/harvest-8c8e3c5f/snapshot.json`](../harvest-8c8e3c5f/snapshot.json),
gap detail in [`gaps.json`](../harvest-8c8e3c5f/gaps.json)):

| Open | With probability | Research pick, no % | No pick at all |
| --- | --- | --- | --- |
| 34 | 31 (market + VRS model) | 2 | **1** |

The one fixture with no pick: **1082157 — Sangal vs Aurora YB**, Stake Ranked
Episode 6: Closed Qualifier, 2026-10-20T12:00:00Z (lock 11:54Z).
Recorded attempts in that snapshot: Polymarket candidate existed as "Sangal vs
Aurora Young Blood" (market 5850565) but was rejected as an unverified alias;
HLTV candidate existed as "Sangal vs Aurora Young Blud" (match 2399777) but was
rejected on the same label; Pinnacle had no exact pair; Thunderpick gave no
validated automated quote; GG.BET returned 404 to the collector; the VRS model
failed on "Aurora YB: not listed in the Valve global standings".

## Research, in the requested order (HLTV first, then esportsbooks)

1. **HLTV.** Match page 2399777 — "Sangal vs. Aurora Young Blud at Stake Ranked
   Episode 6 Closed Qualifier", Bo3 Round of 16, 20 Oct. Read directly this
   session: Sangal HLTV world **#45** / VRS #38; Aurora Young Blud HLTV
   **Unranked** / VRS Unranked on the fixture; lineups Sangal
   R4DYX/Joey/bnox/adamS/puuha, Young Blud Re1GN/meetyoxanaji/fluffy/Sa1nTy/ms2180.
   HLTV's betting table for this fixture shows a Stake promotional row and **no
   numeric two-way odds** — consistent with the collector's recorded limitation.
   HLTV fan-vote percentages on the page (86.2/13.8 at read time) were **not**
   used, per policy. Source: <https://www.hltv.org/matches/2399777/sangal-vs-aurora-young-blud-stake-ranked-episode-6-closed-qualifier>
2. **Identity (the actual blocker).** Liquipedia's team page **Aurora Young Blud**
   is redirected from **Aurora Young Blood**, and its Upcoming Matches lists this
   exact fixture (Oct 20, Stake Ranked Ep. 6 Qualifier Round 1) abbreviated
   **"Aurora YB" vs Sangal** — i.e. Hotspawn's label for the same team. So the
   three labels are one academy team; aurora (main team, HLTV 11861) is separate
   and is never mapped. Registered in `data/identities.json` with these sources:
   HLTV 2399777 + <https://liquipedia.net/counterstrike/Aurora_Young_Blud>.
   With the alias, existing tiers engage: HLTV exact-fixture ranks
   (Sangal #45 vs unranked ⇒ `research_rank_single`), and the Polymarket
   candidate can finally be evaluated against the normal quote gates.
3. **Valve standings.** The official 2026-10-05 global file (380 teams) lists
   **Aurora Young Blud #326, 526 points** — but with roster
   k1nco/kurosse/meetyoxanaji/r1pa4/redzed, which shares only one player
   (meetyoxanaji) with the current HLTV lineup, so the model line is correctly
   **refused** under Valve's 3-player roster-continuity rule. Sangal resolves
   cleanly (#40, 1362 pts, lineup overlap 5). Source:
   <https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md>
4. **Esportsbooks.** EGamersWorld's match page, read directly this session
   (anchored near 04:06Z by the HLTV countdown on the parallel read), shows a
   real two-sided header line — **Sangal 1.08 / Aurora Young Blud 6.28**, Bo3,
   20.10.2026 12:00 UTC — not the 1.8/1.8 placeholder this project rejects.
   De-margined: Sangal 85.3% / Young Blud 14.7% (overround 8.5%). Stored as a
   dated receipt in `data/book-receipts.json`
   (`egw-41yaj8BdVx-sangal-aurora-young-blud`); it expires 2026-10-19T12:06Z
   under the 8-hour evidence window, before the fixture locks, after which the
   row falls back to its research tier. Source:
   <https://egamersworld.com/counterstrike/match/41yaj8BdVx/sangal-vs-aurora-young-blud-t529SG6szs>
   Thunderpick / GG.BET outcomes for this fixture are whatever the collector
   records per-refresh (snapshot above: no validated quote / 404); no access
   control was bypassed and no line was inferred from tipster pages.

## Durable change: one-sided Valve standings tier (`research_vrs_single`)

The Sangal row is fixed by the alias, but the class it belonged to — *no HLTV
fixture, no market, one team in the official standings* — will recur. New final
tier in `scripts/vrs.py::research_single`, after every market/model/HLTV-rank
tier, with the model's identity rules and strict refusal cases; it publishes a
pick and **no probability**. Fully specified in Sources & methodology
("Primary picks → research fallback", item 7) and re-derived by
`scripts/validate.py` and the independent auditor from evidence stored on the row.

## Executive summary / phone changes

* **Picks at a glance** (`#picks-at-a-glance`) directly under the hero: every open
  match in start order, bold team = pick, percentage beside it, whole row taps
  through to evidence; research-only and no-pick rows say so and point at the
  limitations section. Browser expiry withholds closed/expired picks in this
  list just as it does in the tables (`data-glance-*` deadlines in `app.js`).
* Hero actions: "See every pick ↓" (the glance) + "View updated picks →"
  (`picks.html`). Jump nav gains "All picks at a glance".
* **Limitations for generating these picks** (`#pick-limitations`) inside the
  executive summary's unresolved section: six plain-language limitations with
  links, ahead of the per-match attempts table and the measured access-limitations
  table. The separate `unresolved.html` research queue is unchanged.

## What "every match" can and cannot promise

After this session the ladder is: featured exchange/bookmaker line → researched
book listing → wide exchange (labelled) → originated VRS model line → HLTV rank
pair → HLTV single rank → one-sided Valve standings → blank + published attempts.
A fixture can still end blank — e.g. neither team resolvable in HLTV or the
standings, or every label present-but-ambiguous. That outcome is published with
its attempts; no percentage is ever invented, and Hotspawn crowd votes are never
an input. Hotspawn coverage itself is re-checked every 15 minutes by the
publication workflow (plus the stale-watchdog), so newly listed matches enter
this ladder automatically with no manual input.

## Flagged for review

* **Young Blud roster vs the 5 Oct standings:** HLTV's current lineup shares one
  player with the listed roster, so no VRS-derived percentage exists for this
  team until a newer Valve file lists the current roster. Recorded in
  `data/review-notes.json` (`identity-aurora-yb` / `vrs-young-blud-roster`).
* **EGW receipt expiry:** the 1.08/6.28 listing is a dated observation that
  expires 2026-10-19T12:06Z; if the row later shows a research-only pick, that
  is the intended fallback, not a data loss.
