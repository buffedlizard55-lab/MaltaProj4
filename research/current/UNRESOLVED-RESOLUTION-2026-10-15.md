# Full pick coverage — how the five open gaps were resolved (session a56d155f)

Observed 2026-10-15 between 10:15 and 10:25 UTC. Goal from the request: every match listed by Hotspawn should end with a
pick where a researched source permits one, with the residual limitations published.

The 08:40 UTC snapshot had five open fixtures with no pick. Each one was researched in the requested order — HLTV first,
then esportsbook/exchange lines — and each ended with a resolved pick.

| Hotspawn fixture | External source | Exact-start check | Quote used | Tier |
| --- | --- | --- | --- | --- |
| 1080281 WROTBERRY vs ENCE (12:00Z) | Polymarket market 5583519 (WBT vs ENCE) | 2026-10-15T12:00:00Z = Hotspawn start | 0.61 / 0.39, bid 0.60 / ask 0.62, spread 0.02, liquidity $11,195.9987 | `exchange` |
| 1080283 WROTBERRY vs BOJONG (16:00Z) | Polymarket market 5583522 (WBT vs BOJONG) | 2026-10-15T16:00:00Z = Hotspawn start | 0.835 / 0.165, bid 0.83 / ask 0.84, spread 0.01, liquidity $7,183.7737 | `exchange` |
| 1080286 HAVU vs RoundsGG (16 Oct 10:00Z) | Polymarket market 5583527 | 2026-10-16T10:00:00Z = Hotspawn start | 0.695 / 0.305, bid 0.57 / ask 0.82, spread 0.25, liquidity $6,703.9342 | `exchange` (low-precision flag) |
| 1081120 mellren vs Privateer (16 Oct 14:00Z) | Polymarket market 5649536 (mellren vs Privateer Gaming) | 2026-10-16T14:00:00Z = Hotspawn start | 0.75 / 0.25, bid 0.55 / ask 0.95, spread 0.40, liquidity $2,966.0927 | `exchange_wide` (low confidence) |
| 1080289 RoundsGG vs Voca (16 Oct 16:00Z) | Polymarket market 5583533 | 2026-10-16T16:00:00Z = Hotspawn start | 0.89 / 0.11, bid 0.86 / ask 0.92, spread 0.06, liquidity $5,645.2715 | `exchange` |

Raw receipts (the exact fields the pipeline stores and replays) are saved in `research/current/quotes/` with their API URL
and observation minute. `scripts/backfill_quotes.py` applied them and every probability is recomputed by `scripts/core.py`;
`scripts/validate.py` replays them again from the raw fields, so a hand-typed number would fail the build.

## Identity work behind two of the rows

- **WROTBERRY ↔ WBT.** HLTV's Elisa BreakOut Series 2 group-A schedule lists WBT against EAC, ENCE and BOJONG on
  15 October; Hotspawn lists WROTBERRY against the same three opponents in the same group on the same day, with matching
  UTC starts for five of the six fixtures. A four-team group cannot contain both teams, so the mapping is fixture parity,
  not name guessing. Polymarket's group-A markets use WBT with the identical 12:00Z and 16:00Z starts.
  WhiteBIT's white.market announcement launches WhiteBIT Team (WBT) with the Ukrainian core previously recorded under the
  WROTBERRY tag by third-party databases. An official "renamed from WROTBERRY" statement was **not** found, so the mapping
  is restricted to exact-opponent-and-start matches and is listed on Flagged for Review.
  - https://www.hltv.org/events/9332/matches
  - https://white.market/blog/cs2-news/whitebit-team-enters-cs2-scene-w-group-launches-new-counter-strike-2-roster
  - https://game-tournaments.com/csgo/team/wrotberry
- **Privateer ↔ Privateer Gaming.** HLTV names the team Privateer for the same CCT Europe Series #12 Group D fixture that
  Hotspawn lists at 2026-10-16T14:00:00Z; Polymarket names it Privateer Gaming with the identical start and event.
  - https://www.hltv.org/matches/2399471/mellren-vs-privateer-cct-2026-europe-series-12-closed-qualifier
  - https://gamma-api.polymarket.com/markets/5649536

## New tiers added for full coverage (and their limits)

1. **Wide-quote tier (`exchange_wide`).** Accepts a two-sided exchange quote that fails *only* the 25-point spread ceiling.
   Requires: open market, accepting orders, fresh observation and update, valid two-sided bid/ask, liquidity ≥ $100, and
   spread ≤ 60 points. Publishes the real spread, the strict rejection and a low-confidence warning. Liquidity below $100 is
   never accepted. Only one fixture needed this tier in the current snapshot (mellren vs Privateer).
2. **Research-only tier (`research_rank`, no numbers).** If no market line exists, an exact HLTV fixture identity with both
   teams' world rankings can produce a pick with **no published probability or fair line** — the better-ranked side, labelled
   research-only, with the HLTV link. Without both ranks the row stays unresolved. No fixture needed this tier in the current
   snapshot; it is unit-tested and would run on the next refresh.
3. **Residual unresolved rows.** If neither tier applies, a row keeps a blank percentage, a blank fair line and a blank pick,
   with every attempted source in the evidence ledger. That remains the honest outcome and is published in the executive
   summary's unresolved section.

## HLTV access note

No numeric two-way line was exposed on the HLTV match pages checked for these fixtures (the betting blocks returned a
social-casino promo row and a fan-vote widget, both of which this project refuses to use as probabilities). HLTV was
therefore used for identity, fixture parity and ranking context only — exactly the order the request asked for.
