# Follow-up verification — 17 October 2026

## Scope and source standard

The fresh [runner audit](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39022254146)
read Hotspawn, Polymarket, Pinnacle, HLTV and fallback esportsbook pages. Retained
`latest.json`, `harvest-summary.json`, `row-audit.md` and `probe/` files contain
observation times, response receipts and field-level results. This is not a claim
that every inherited narrative sentence or every external website has been
freshly verified. HLTV is a specialist publication, not an official tournament
organizer; operator feeds are primary for their own prices, not true win chances.

## Collection and unresolved picks

At 09:46:15 UTC: **93 feed entries; 32 open; 27 priced; four research-only;
one unsupported pick**. Three-way Hotspawn coverage is verified at that observation.
The independent audit checked all 93 rows with zero arithmetic/field failures.
Sixteen priced rows use markets (including one wide exchange); eleven use the
labelled Valve VRS model. No Hotspawn vote share supplies a probability.

The unsupported row is Hacha–LOS NINOS (1082019). Its
[HLTV fixture](https://www.hltv.org/matches/2399768/hacha-vs-los-ninos-cct-2026-south-america-series-7)
exposes neither numeric odds nor either world ranking. A
[possible Polymarket market](https://gamma-api.polymarket.com/markets/5796276)
has different labels (Hacha Esports / Los Niños). A matching time and plausible
name do not independently establish the Hacha alias, so no quote is transferred.
The unresolved page retains that reason rather than inventing a pick.

Four research-only rows are 1079634, 1081522, 1081861, 1081863. The current
snapshot contains each exact HLTV URL, rank evidence and all fallback attempts.
Each lacks a numeric HLTV quote and at least one official Valve model input.
GG.BET/EGamersWorld returned 403; Thunderpick/Rivalry pages exposed no numeric
line to this parser. HTTP success is not a validated quote. These are access or
adapter limitations, not proof that no book offers a market.

## TWC review

The fresh HLTV results capture reproduces the ten Day-1–3 series results in
`data/analysis.json` (compared by match URL, winner and oriented score). The
capture parser returns null day headings; dates are retained from earlier
match-page receipts, not falsely called re-read from these null fields.

- Day 1: 9z beat Aurora 2–0. Day 3: Aurora reversed it 2–0. Do not extrapolate
  a single upset into a persistent weakness.
- Day 2 advanced Falcons and FURIA; Day 3 advanced Aurora and BETBOOM.
- Counting the sourced series scores: FURIA/Falcons five maps each, Aurora six,
  BETBOOM eight. The favorites last played 15 October; the underdogs 16 October.
  Removed the incorrect three-three-map-series claim and rest advantage.
- Aurora's July rebuild is historical context. It is not fresh onboarding in
  October, nor proof of a quantified probability adjustment.
- At this snapshot FURIA/Aurora is 52.5/47.5; Falcons/BetBoom is 72.5/27.5,
  normalized from the operator's two-sided outcome prices. Use the live picks
  board for subsequent observations, lock times, liquidity and expiry.
- Aurora is the less speculative underdog choice at those lines; BETBOOM is
  higher variance. Neither is proven to improve leaderboard position. No
  verified opponent pick shares, user deficit or exact streak formula exists
  here. Expected base points and leaderboard rank are different objectives.

## Fixed defects and checks

1. Reproduced the scheduled 09:27 run's failing book-receipt test. It depended
   on wall-clock time. Pass the collection clock explicitly; pin test time and
   test rejection exactly at eight hours. No freshness rule was weakened.
2. Empty/expired boards had a broken `#later` jump link. Keep the target present.
3. Removed a static promise that every other open fixture has a pick.
4. Added direct source links to all six strategy table rows; separated dated
   strategy quotes from the current snapshot column.

Local checks before publication: 300 unit tests, 9 audit tests, 5 integrity
checks, 12 independent tests; 32 mobile/desktop accessibility/no-overflow scans
and seven exact-boundary browser expiry scenarios. Publication reruns the checks
and verifies the deployed files against their SHA-256 manifest.

Open PR #64 was read, not blindly merged: its rest/strategy audit informed the
correction, but its obsolete assertion that the semifinals are absent from
Hotspawn was not imported. No other branch was modified.

The refreshed snapshot also exposed a second brittle test: it required every
open match to have a pick, contradicting the explicit unresolved policy. It now
requires either a valid team pick or a documented source trail and reason, with
blank fair odds when probabilities are missing (equal-price no-edge is allowed).
That change does not loosen the independent price/identity validators.
