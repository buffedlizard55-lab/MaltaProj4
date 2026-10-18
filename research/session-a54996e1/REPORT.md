# Session a54996e1 — Day-5 final-day report (2026-10-18)

## What was asked
Review Day 1–4 TWC 2026 (incl. the 9z–Aurora upset and Aurora's roster change), guide Day-5 picks
contrarian-but-not-stupid, generate a pick for every Hotspawn CS2 match (HLTV → esportsbooks fallback
for uncovered rows), publish unresolved + limitations in the executive summary, and make the site
findable/readable on a phone. No manual input; verify line-by-line; no invented values.

## Verified today (2026-10-18, UTC)
- **HLTV results re-read ~00:45Z** (https://www.hltv.org/results?event=8932): 12 series — Oct 14: 9z 2-0
  Aurora, Falcons 2-0 NiP, Legacy 2-0 PARIVISION, FURIA 2-0 BETBOOM; Oct 15: Falcons 2-1 9z, Aurora 2-0
  NiP, FURIA 2-1 Legacy, BETBOOM 2-1 PARIVISION; Oct 16: Aurora 2-0 9z, BETBOOM 2-1 Legacy; Oct 17:
  FURIA 2-0 Aurora, BETBOOM 2-1 Falcons. Matches the published Day 1–4 tables; no correction needed.
- **Day-5 fixtures (HLTV 2399416/2399417, re-read ~00:45Z):** Aurora–Falcons BO3 11:30Z; FURIA–BETBOOM
  BO5 15:00Z. VRS: Aurora 1839 (#6) vs Falcons 1858 (#5); FURIA 1858 (#4) vs BETBOOM 1681 (#9).
  HLTV fan votes on those pages are crowd votes, not probabilities — not used.
- **Aurora roster premise:** rebuild dated 8 July 2026 (HLTV news 45082: kyxsan IGL, Jimpphat, coach ash).
  ~14 weeks before TWC — a real structural change, not a fresh October onboarding shock. The Day-1 loss
  is better explained by the sourced schedule/form context in analysis.html than by "new roster".
- **Thunderpick book re-read 00:55Z** (official market pages, receipt day5-lines.json):
  Aurora +140 / Falcons −200 → de-vig **Falcons 61.54% / Aurora 38.46%** (overround 8.33%).
  Verified line move from +170/−238 (17 Oct 20:20Z, Falcons 65.53%). FURIA −286 / BETBOOM +190
  unchanged → **FURIA 68.24% / BETBOOM 31.76%** (overround 8.58%).
- **Hotspawn board (harvest run 39084235336, snapshot 00:52:19Z, 98 rows, three-way parity verified,**
  **independent row audit 0 failures):** both Sunday fixtures ARE now board rows — 1080209 Falcons–Aurora
  (Falcons **60.5%**, Polymarket), 1080210 FURIA–BetBoom (FURIA **70.5%**, Polymarket), tier S.
  Two independent sources agree on both favourites within 2.3 points.

## Board coverage at 00:52Z
34 open: 29 priced (exchange/model), 5 research-only picks with **no percentage** (1081519, 1081129,
1082206, 1081861, 1081863 — one-sided HLTV ranking evidence), **0 open rows with no pick**.
Every open row therefore has a pick; unresolved limitations are in the executive summary
(#unresolved-summary) and unresolved.html, with per-row attempted sources.

## Contrarian-but-not-stupid (Day 5)
- Default: **Falcons** and **FURIA** (supported by both the board exchange and the book).
- Only measured alternative: **Aurora (~38–40%)** — closest line, overnight shortening toward Aurora,
  19-point VRS gap. A chasing/variance pick, not an edge claim.
- Higher-variance swing: **BETBOOM (~30%)** — three straight 2-1 wins (PARIVISION, Legacy, Falcons) is a
  concrete form case; rest argues *against* it (11 maps played vs FURIA's 7; map load is a count, not a
  measured fatigue effect). Their Day-1 meeting was FURIA 2-0.
- Lesson from Day 1→3: the 9z upset did not repeat (Aurora won the rematch 2-0). Roster-change, rest or
  crowd-share claims without a dated source are not pick reasons. No crowd pick shares, leaderboard
  distribution or streak formula are published, so no optimal rank-climbing claim is made.

## Irregularities flagged (also on Flagged for Review)
1. Lobby document read 00:48Z showed 81 matches / no Sunday rows; harvest 00:52Z verified 98 rows
   including both Sunday rows. Earlier read superseded; runner receipts control. (Possible caching —
   unverified cause.)
2. EGamersWorld still displays the superseded Aurora 2.73 / Falcons 1.42. Flagged stale, not used.
3. Thunderpick book observations expire 08:55Z, before both starts — cross-check only, not at-lock.
4. Organizer (Thunderpick) confirmation of results/schedule/roster not collected; HLTV is secondary.

## Automation
pages.yml refreshes on main every 15 min (:04/:19/:34/:49 UTC, target not guarantee) with a 10-min
watchdog; picks expire at TTL/lock/start in browser and build. This session's harvest workflow is
non-publishing; publication is via the PR merge to main below.
