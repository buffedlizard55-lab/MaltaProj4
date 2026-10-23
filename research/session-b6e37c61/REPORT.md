# Session b6e37c61 — a pick for every match: extra sources for the unresolved set

Date: 2026-10-23. Branch: `arena/b6e37c61-maltaproj4` (base `main` `be81768`).

## 1. Mandate

Generate a pick for **every** CS2 match listed on Hotspawn, including low-tier
fixtures and fixtures no betting site (e.g. Polymarket) covers. For matches that
cannot be resolved the way the featured picks are, research extra information
sources — HLTV first, then esportsbooks / esports betting lines. Keep a separate
section for unresolved picks and their limitations inside the executive
summary, and keep the picks findable on a phone.

## 2. Pipeline audit (verified line by line against the committed snapshot)

Live state at session start (`data/latest.json` on `origin/main`, snapshot
`2026-10-23T08:32:56Z`; `origin/main` == branch base `be81768`):

| Fixtures | Open | Picks | With probability | Unresolved |
| ---: | ---: | ---: | ---: | ---: |
| 92 | 30 | 30 | 30 | 0 |

Open-match methods: 20 `exchange` (Polymarket), 1 `exchange_wide`,
2 `bookmaker_fallback` (researched book listings), 7 `model_vrs`
(original lines from Valve's official standings + Valve's expected-win
formula). The resolution ladder in `scripts/refresh.run`, in order:

1. Polymarket Gamma strict gate (`scripts.core.resolve`/`quote_polymarket`).
2. HLTV identity research — context only (`scripts.hltv.research`, dated views).
3. Pinnacle guest esports API moneyline (`quote_pinnacle`).
4. Wide exchange quote, labelled low confidence (`exchange_wide`).
5. Thunderpick/GG.BET access attempts, recorded (no validated adapter).
6. Researched book-listing receipts, re-observed each run (`scripts.books`,
   `book_research_pick`) → `bookmaker_fallback`.
7. Originated VRS model line (`scripts.vrs`), then HLTV dated Valve-ranking
   mirror (`scripts.vrs_mirror`).
8. Research-only tiers, no percentage: `research_rank`,
   `research_rank_single`, `research_vrs_single`.
9. **New this session:** `research_form` (below).

Remaining unresolved class before this session: HLTV lists the fixture but
neither team carries a usable world ranking and neither resolves in Valve's
standings (or both/one-sided logic is ambiguous) — the row ended with no pick
even though the HLTV match page publishes both teams' recent completed
results and their head-to-head record.

## 3. Sources researched for the unresolved set

### 3.1 HLTV (tried first — implemented)

`scripts.hltv.context` already reads the exact-identity match page for ranks
and lineups. The same page publishes, per team, a "Matches, past 3 months"
box and a lifetime head-to-head summary. Markup verified on real retained
HTML (`research/harvest-76712ccc/hltv-2399386.html`, Legacy vs PARIVISION):

- Box headline: `.past-matches-headline .past-matches-teamname a` (team label).
- Row: opponent (`.past-matches-team a`), recency (`.past-matches-time-ago`),
  format (`.past-matches-map a`, e.g. `bo3`), score anchor
  `.past-matches-score a.past-matches-cell` classed `won`/`lost` with text
  `1 - 2` from the box team's perspective (validated: won ⇔ first > second).
- HLTV renders the box twice (Team/Core views): rows are deduplicated by
  (opponent, when, format, score) so nothing is double-counted.
- Head-to-head: `.head-to-head` = team1, `W1 Wins`, `N Overtimes`, `W2 Wins`,
  team2 (sample: Legacy 6, overtimes 3, PARIVISION 4).

### 3.2 Esportsbooks and betting-line sources (researched; no new keyless line)

- Prior measured probe, `research/harvest-dedd2e34/book-probe.json`
  (2026-10-16, 12 endpoints): only Pinnacle's guest API and Polymarket's
  Gamma API return usable keyless JSON. GG.BET (page + public sport API),
  Thunderpick CS2 page, Oddschecker: HTTP 403. Pinnacle outrights: 401.
  `api.thunderpick.com` does not resolve. Those two usable sources are
  already rungs 1 and 3.
- Kalshi public market-data API (checked this session, 2026-10-23):
  `GET https://api.elections.Kalshi.com/trade-api/v2/series?category=Esports`
  answered `{"series": null}` — the API is readable without a key, but it
  carries no esports series today, so there is no CS2 line to consume.
- Commercial odds APIs (odds-api.io, OddsPapi, The Odds API,
  esportsodds.gg at $49/mo) all require an account/key. A keyed dependency
  cannot run in this repository's keyless public GitHub Actions pipeline
  without the owner provisioning a secret, so none was adopted. Recorded as
  a future option only if the owner supplies a key.

Conclusion: for the unresolved set the strongest additional **sourced**
signal reachable keylessly is HLTV's own recent-results/head-to-head
evidence, published as a research pick with no percentage (same contract as
the existing research tiers).

## 4. The new tier: `research_form`

`scripts.core.research_form_pick`, run last in `scripts.refresh.run` after
`vrs.research_single`. Rules (fail-closed throughout):

1. Requires the exact-identity HLTV context for the fixture (same opponent
   pair + exact UTC start, already enforced by `scripts.hltv.context`) and
   its `team_map` from that check; no fuzzy label matching.
2. Each team needs ≥ 3 parsed completed results (`MIN_FORM_MATCHES`).
3. Comparison window `N = min(results_a, results_b, 10)` — both sides judged
   over the same number of most-recent matches.
4. More wins in the window → pick, `basis='recent_form'`.
5. Exact win tie → HLTV lifetime head-to-head series wins,
   `basis='head_to_head'`.
6. Still level, or any evidence gap → stays unresolved; the reason is
   recorded on the row. No coin flip, ever.
7. Stores `resolved_form` (per-team results used, wins/losses) and
   `form_detail` (window, basis, head-to-head wins) inside `hltv_context`;
   reason states it is "not a market probability"; flag states "no
   probability published". Expiry uses the HLTV observation time via
   `research_observation`, so the pick dies on the same 8-hour evidence
   window as every other tier.

Gates updated to reproduce the pick from the stored raw evidence (not trust
the stored summary): `scripts/validate.py` (new branch) and the independent
`verification-c6/audit_snapshot.py` (new branch). Display: METHOD labels/tags
in `scripts/build.py`, origins/ladder in `scripts/summary.py`, research set
in `scripts/coverage_contract.py`, methodology item on the Sources page.

## 5. Executive summary & phone findability (verified, no change needed)

The home page (`index.html`, "Executive summary · CS2 Scout") already carries:
in-site links to `picks.html`, `unresolved.html`, `matches.html`,
`analysis.html`, plus `#picks-at-a-glance` (every open match in start order
with the bold pick and win %) and a separate `#unresolved-picks` section
("Picks without a win probability — and exactly why") with per-row
limitations and the full evidence ladder. Verified in a fresh local build.

## 6. Verification performed (local, this session)

- `python -m unittest discover -s tests`: **1075 tests OK** (3 skipped),
  including new `tests/test_session_b6e37c61.py` (17 tests: parser on real
  HLTV HTML, tier decision rules, validator + independent audit accept a
  converted `research_form` row and reject corrupted win totals, display-map
  registration).
- `audits` (9), `verification-95b588c2/test_integrity.py`,
  `verification-c6` (12): OK.
- `scripts.validate --data data/latest.json --site .`: OK (92 rows,
  224 displayed rows verified, 20 checksums).
- `verification-c6/audit_snapshot.py data/latest.json`: 0 failures.
- `scripts.build --data data/latest.json` + validate: OK. A synthetic build
  with one row converted to `research_form` renders "Research only · recent
  form" on `picks.html` and the tier text on `sources.html`.
- `npm run test:browser`: all six suites pass — 32 page/viewport
  accessibility and no-overflow scans at 320/390/768/1440px, first pick and
  its probability on the first phone screen at 320/390px, 44px pick CTA,
  expiry scenarios, filter/live-count agreement.

## 7. Limitations & flagged items (non-blocking)

- **Recent form is weak**: it ignores opponent strength, maps, and roster
  changes. It is deliberately the last rung, labelled research-only, and
  never carries a percentage.
- **HLTV availability**: HLTV rate-limits automated reads (403s recorded in
  prior sessions). If HLTV refuses a run, the form tier simply records the
  attempt and the row can still be unresolved that cycle.
- **Still-unresolvable class**: fixtures HLTV never lists, with both teams
  absent from Valve's standings, or with level form and level head-to-head,
  remain pickless by design — listed with reasons in the executive summary's
  unresolved section and on `unresolved.html`. No 50/50 is ever published.
- **Keyed odds APIs** could add real book lines for low-tier matches, but
  need an owner-provisioned API key/secret; flagged for the owner, not
  adopted silently.
