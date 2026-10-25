# Resolving picks for low-tier & unlisted CS2 matches (non-featured board)

**Research date:** 2026-10-25 (UTC) · **Researcher:** session `arena/4caf5b86-maltaproj4`
**Question asked by the owner:** *"We need picks for every match — including low-tier CS2 matches and matches not covered on Polymarket or other exchanges. Look for information sources to guide pick selections only for matches that cannot be resolved like the featured picks. Try HLTV, then esportsbooks and esports betting lines. Create a separate section for any unresolved picks and the limitations for generating them."*

This document is the research behind the **"Resolving low-tier & unlisted matches"** section that now appears in the executive summary (`index.html` → `#non-featured-research`) and on the methodology page. Every source below was opened and read on 2026-10-25; the URLs are primary and verifiable.

---

## 1. Why non-featured matches are the hard case

The featured board is easy: tier-1 CS2 fixtures are priced by dozens of books. The problem the owner describes is the **long tail** — low-tier, qualifier, regional and academy/feeder matches — where:

- **Polymarket / prediction markets do not list them.** Polymarket covers marquee CS2 only; qualifier and regional fixtures simply never get a market.
- **The "sharp" benchmark book (Pinnacle) is not openly queryable.** Pinnacle closed public API access on 2025-07-23; lines survive only as mirrors inside aggregators.
- **Some books geo-block or rate-limit this collector.** The existing probe (`research/harvest-dedd2e34/book-probe.json`, cited on `sources.html`) recorded GG.BET `403`, Thunderpick's CS2 page refusing automated access, and `api.thunderpick.com` not resolving.

So the honest ceiling for an *automated* two-sided line on a low-tier match is often: **"no accessible market line."** That is exactly why the ladder falls through to our own Valve-standings (VRS) model line and to HLTV research tiers. The research below confirms which *human-verifiable* sources exist for those same matches, so a person (or a future collector) can resolve them.

---

## 2. Source 1 — HLTV betting/analytics (the owner's first suggestion)

**Primary URL verified 2026-10-25:** <https://www.hltv.org/betting/analytics>

HLTV's analytics board lists **upcoming CS2 matches with three independent signals per fixture**:

1. **"Best Odds"** — the best bookmaker moneyline HLTV can aggregate for that exact match (when a line exists).
2. **HLTV world ranking** for each team (e.g. `Acend #131` vs `INOX Division #84`; `Metizport #59` vs `BAKS #99`; `Spirit Academy #111` vs `LFO 10 #?`).
3. **Recent form** ("won 5 of the last 5 matches"), **stand-in / roster** notices, and a **"Full match analysis"** deep link per fixture.

Crucially, this board covers **low-tier events the exchanges ignore**: at the time of reading it listed `CCT 2026 Europe Series 11`, `NODWIN Clutch Series 13`, `CCT 2026 Challengers Europe Series 8`, and `ViderGG CTRL POINT Season 2` — exactly the "low tier" fixtures the owner is worried about.

**Honest limitation (observed):** for several of those low-tier fixtures the "Best Odds" cell is a literal **`—`** (dash), i.e. HLTV aggregated **no bookmaker line** for that match even though rankings and form are present. Examples read on 2026-10-25:
- `Acend vs INOX Division` (CCT Europe S11) — `—` odds, ranks #131 / #84.
- `Metizport vs BAKS` (NODWIN Clutch S13) — `—` odds, ranks #59 / #99.
- `Legion vs BadKids` (ViderGG CTRL POINT S2) — `—` odds, BadKids unranked.
- `Quintessence vs TitanFlow` (CCT Challengers Europe S8) — `—` odds, both unranked.

**Conclusion:** HLTV is a first-class source for **identity, ranking, form and stand-in confirmation** (a research-only pick with *no percentage*), and it yields an actual **two-sided line** only when a book has priced the match. When HLTV shows a "Best Odds" number, de-vigging it (see §6) gives a market-implied probability; when it shows `—`, it supplies a ranking/form pick but no percentage. HLTV fan votes are **never** used as probability.

Supporting HLTV endpoints (verified reachable 2026-10-25):
- Odds comparison hub: <https://www.hltv.org/betting/money>
- Bookmaker ranking (which books cover CS2): <https://www.hltv.org/betting/sites> — names **Thunderpick**, **GG.BET**, **BetBoom**, **Betway**, **1xBet** as CS2 books.

---

## 3. Source 2 — Esportsbooks (the owner's second suggestion)

When HLTV shows `—`, the next rung is the books themselves. The CS2 books with the **deepest tier-2 coverage**, per HLTV's own ratings and multiple 2026 esports-betting reviews:

| Book | CS2 coverage noted | URL (verified reachable 2026-10-25) |
| --- | --- | --- |
| **Thunderpick** | "Daily CS2 rotation, from tier-one down to regional qualifiers and small online events"; crypto-native, HD streams | <https://thunderpick.io/esports/cs2-betting> |
| **GG.BET** | "Deepest CS2 markets, Tier-2 cover"; map winner, handicap, player props | <https://gg.bet/en/esports/counter-strike> |
| **BetBoom** | Sponsors CS2 events, provides match odds on stream | <https://betboom.com/> |
| **Betway** | Licensed all-rounder; ESL Pro League, IEM, Majors | <https://www.betway.com/> |

Independent 2026 reviews (esports.gg, tips.gg, win.gg, egaminghq) consistently rank **GG.BET** and **Thunderpick** as the two books with the widest CS2 menu, including regional qualifiers that tier-1-only books skip.

**Honest limitation:** these books are the best human source for a low-tier line, but they were **refused or geo-blocked to the automated collector** in the existing probe (GG.BET `403`, Thunderpick access denied). They therefore resolve a *person* looking up a fixture, not an unattended scrape. Where a book does serve a line, de-vig it (§6) and record the book + observation time.

---

## 4. Source 3 — Esports betting-line aggregators (multi-book, one card)

These present **several books' odds for the same CS2 match on a single card**, which is ideal for de-vigging to a fair probability.

- **EGamersWorld CS2 odds** — <https://egamersworld.com/counterstrike/bets> (verified 2026-10-25). Example card read live: `MOUZ vs 9z` showed **Vave 1.30 / 3.42**, **Thunderpick 1.25 / 3.50**, **Rainbet 1.26 / 3.57**, **Underdog 1.22 / 3.49**, **CocoBet 1.24 / 3.52** on one row; `G2 vs Aurora` showed Vave 2.22 / 1.63, Thunderpick 2.20 / 1.58, Rainbet 2.21 / 1.57, etc. Coverage is strongest on tier-1/tier-2.
- **BO5.gg CS2 odds** — <https://bo5.gg/cs2/betting/odds/> (54 tracked lines, refreshes per round).
- **EsportsInsider odds** — <https://esportsinsider.com/betting-odds/counter-strike>.
- **OddsPortal** — aggregates CS2 bookmaker lines (region-dependent).
- **EsportRanker CS2** — <https://esportranker.com/esports/csgo/> publishes a worked de-vig example (Vitality/Falcons across 5 books; best-odds payout 96.8%).

**Honest limitation:** aggregators mirror what books post; if no book prices the match, the aggregator has no row either. They are also region-shaped (some books/odds only show in certain geographies).

---

## 5. Source 4 — Odds depth fact base (how thin can tier-2 get?)

`OddsPapi`'s 2026 esports-odds write-up (verified) quantified CS2 coverage:
- Tier-1 (Blast Premier, 24 Aug 2026): a **median of 86 bookmakers per fixture** (min 29, max 89); Pinnacle, Bet365 and Polymarket priced all 8.
- **Minor circuits:** median **24.5 books per fixture (range 12–58)** — i.e. a low-tier match may have only a dozen prices, and the long tail can have *none* on any accessible book.

This is the quantitative backing for the ladder's fall-through: tier-2 is thin, and the tail is empty, which is why the VRS model line and HLTV research tiers exist.

---

## 6. Converting a line to a probability (the de-vig we already use)

For decimal odds `d₁, d₂`:
- implied `qᵢ = 1 / dᵢ`
- overround `= q₁ + q₂ − 1`
- fair `pᵢ = qᵢ / (q₁ + q₂)`

Example from EGamersWorld `MOUZ vs 9z` best line Vave `1.30 / 3.42`: `q = 0.769 / 0.292` → overround `6.2%` → MOUZ `72.4%`, 9z `27.6%`. This is exactly the arithmetic the site already applies to exchange and bookmaker quotes; the same formula works for any book or aggregator line we can read.

---

## 7. Resulting resolution ladder for a non-featured match

In the order it should be tried (HLTV first, per the owner's instruction, then books, then aggregators, then our own model/research):

1. **HLTV betting/analytics "Best Odds"** present → de-vig → market-implied probability + directional pick. *(Tier: external line.)*
2. **HLTV "Best Odds" = `—` but rankings/form present** → research-only pick from ranking/form, **no percentage** (`research_rank` / `research_form`).
3. **Esportsbook direct** (Thunderpick / GG.BET / BetBoom) where the book serves a line → de-vig → probability.
4. **Multi-book aggregator** (EGamersWorld / BO5 / OddsPortal) → take best odds, de-vig → probability.
5. **Our Valve-standings (VRS) model line** where both teams resolve in Valve's official standings with a confirmed roster → originated percentage, labelled `model_vrs` / `model_vrs_mirror`.
6. **Unresolved** — only when every rung records a refusal or an absence. Published as a blank (never 50/50) with the attempted sources listed.

At the 2026-10-25 snapshot, **all 18 open matches already carry a pick** (11 exchange, 2 wide-exchange, 2 bookmaker-fallback, 2 model_vrs / model_vrs_mirror, 1 bookmaker). The two `model_vrs`/`model_vrs_mirror` rows (`HOTU vs The Huns`, `5star vs 1WIN`, `Spirit Academy vs LFO 10`) are precisely the low-tier cases this research covers: no exchange line exists, so they are resolved by our originated VRS line, which HLTV ranking/form would independently support as a research-only pick.

---

## 8. Limitations to publish honestly (wired into the site)

- A low-tier match with **no line on any accessible book** cannot get a market probability; it falls to the VRS model or a ranking/form research pick, both labelled and never presented as a market price.
- **HLTV shows `—` for odds on many low-tier fixtures** — ranking/form only, no percentage.
- **Books and aggregators are region-shaped and access-controlled**; a block is recorded, never converted into a number.
- **Pinnacle is not openly queryable** (API closed 2025-07-23); its lines survive only inside aggregators.
- Every probability **expires** at the earliest of its 8-hour evidence window, Hotspawn lock, match start or bookmaker cutoff.

---

## 9. Flagged for review (non-blocking)

- **Live HLTV/esportsbook scraping is documented but not yet wired into the automated refresh.** The collector's existing probe was denied by GG.BET/Thunderpick, so the auto-pipeline still relies on Polymarket + books it can reach + the VRS model. Wiring HLTV `betting/analytics` parsing (odds where present, ranking/form where not) is a recommended enhancement, not a claim of current automated coverage. Recorded on `review.html` as `session-4caf5b86-hltv-nonfeatured-research-2026-10-25`.
- The two `model_vrs` rows are the explicit "low-tier, no exchange line" cases; they are correct but lower-confidence than an exchange line and are labelled as our model line.

---

## Source index (all opened 2026-10-25)

- HLTV analytics: https://www.hltv.org/betting/analytics
- HLTV odds hub: https://www.hltv.org/betting/money
- HLTV bookmaker list: https://www.hltv.org/betting/sites
- EGamersWorld CS2 odds: https://egamersworld.com/counterstrike/bets
- BO5.gg CS2 odds: https://bo5.gg/cs2/betting/odds/
- EsportsInsider CS2 odds: https://esportsinsider.com/betting-odds/counter-strike
- Thunderpick CS2: https://thunderpick.io/esports/cs2-betting
- GG.BET CS2: https://gg.bet/en/esports/counter-strike
- EsportRanker (de-vig example): https://esportranker.com/esports/csgo/
- OddsPapi CS2 depth write-up: https://oddspapi.io/blog/esports-odds-api-guide-how-to-get-pinnacle-cs2-lol-data-for-free/
- Pinnacle API closure notice: https://github.com/pinnacleapi/pinnacleapi-documentation
- Existing automated book-probe (cited on sources.html): research/harvest-dedd2e34/book-probe.json
