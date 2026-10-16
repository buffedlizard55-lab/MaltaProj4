# Researched book-listing fallback tier — evidence, method and limitations

Session **2e920ea8**, 16 October 2026 (UTC). Requirement served: *"We need to be
able to generate picks for every match… provide a percentage of how likely each
team will win based on all of our research into cs2 esports using known betting
sites lines and hltv"* and *"Do your own research to find a way to resolve a pick
for any matches that we don't have a pick for. Try hltv, then try looking at
esportsbooks and esports betting lines."*

Published alongside this file:

* `data/book-receipts.json` — the dated receipts the new tier consumes.
* `scripts/core.py` — `book_candidate`, `quote_book`, `calculator_for`,
  `book_research_pick`, and the `plain_name` diacritic fold.
* `scripts/validate.py` — validator replay of the researched listing.
* `verification-c6/audit_snapshot.py` — independent de-vig branch for it.
* `tests/test_book_research_2e920ea8.py` — 28 tests, including validator and
  independent-auditor replay of the same row.

## 1. What was resolved

| Row | Fixture | Listing (read, UTC) | Two-way line | De-vigged | Published as |
| --- | --- | --- | --- | --- | --- |
| 1081526 | Infinite vs Insiders · DraculaN S7 · 19 Oct 09:00Z · Bo1 | [EGamersWorld match page](https://egamersworld.com/counterstrike/match/V1JAWhPomg/infinite-gaming-vs-insiders-esport-sy3npvC5f), 07:32 | 1.39 / 2.65 | **65.6% / 34.4%** (overround 9.68%) | `bookmaker_fallback`, evidence "EGamersWorld book listing" |
| 1081502 | Procyon vs LOS NINOS · CCT SA #7 · 16 Oct 16:00Z · Bo3 | [EGamersWorld match page](https://egamersworld.com/counterstrike/match/0U32SId-H/procyon-vs-los-ninos-NQ8TFsKyF), 07:27 | 1.34 / 2.85 | 68.0% / 32.0% | Backup receipt only; the automated Pinnacle tier already prices this row (67.2 / 32.8 at 07:27 build). The two sources agree within 1 point. |

The EGWxxxBOT summary on each page states the same book averages ("odds on them
are 1.339… 2.929" for the CCT fixture; "average odds 1.39… about 2.65" for the
DraculaN fixture), quoted in the receipts as corroboration.

## 2. Ladder used, exactly as the brief ordered

1. **HLTV first.** The match pages are already fetched by the automated ladder
   (`scripts/hltv.py`). For rows 1081521, 1081522 and 1081526 the retained
   refresh attempts record: *"HLTV betting table does not expose a numeric
   two-way line in this response"* (see each row's `attempts` in
   `data/latest.json`). Identity, rankings and lineups were taken from HLTV:
   [2399590 Infinite–Insiders](https://www.hltv.org/matches/2399590/infinite-vs-insiders-digital-crusade-draculan-season-7),
   [2399681 ex-6666–Privateer](https://www.hltv.org/matches/2399681/ex-6666-vs-privateer-cct-2026-challengers-europe-series-8),
   [2399682 antidaun–Phantom Academy](https://www.hltv.org/matches/2399682/antidaun-vs-phantom-academy-cct-2026-challengers-europe-series-8).
2. **Esportsbook / esports betting lines.** EGamersWorld match listings (an
   esports betting aggregator whose pages name book averages and show a two-way
   decimal line). Exchange (Polymarket) and Pinnacle were already tried by the
   automated ladder before this tier and are never overridden by it.
3. **Only then** the rank-only research pick (unchanged, still publishes **no**
   percentage).

## 3. What was rejected, and why (this is the unresolved/limitations section)

| Row | Fixture | What was found | Why no percentage is published |
| --- | --- | --- | --- |
| 1081521 | ex-6666 vs Privateer · 18 Oct 13:45Z | [EGW listing](https://egamersworld.com/counterstrike/match/EkjkYUfoNl/ex-6666-vs-privateer-gaming-sfo_MjtRV) shows **1.8 / 1.8** (read 07:44Z). Polymarket: no listing for this pair/start located (slug probe and public-search negative). Pinnacle: no exact pair/start in the retrieved feed (row attempts). VRS model: ex-6666 not in the Valve global standings. | Identical default odds are a **listing placeholder**, not a market. Publishing it would fabricate a 50/50, which this project refuses. HLTV rank order (#80 vs #226) supplies the pick direction only. |
| 1081522 | antidaun vs Phantom Academy · 18 Oct 13:45Z | [EGW listing](https://egamersworld.com/counterstrike/match/EkjkYUfoNl/antidaun-vs-phantom-academy-zXFTwo17o8) shows **1.8 / 1.8** (read 07:44Z). Polymarket: only a resolved 15 Oct ESEA market for antidaun surfaced. VRS model: antidaun not in the standings. | Same: placeholder odds. Pick direction from HLTV (#178 Phantom Academy side; antidaun unranked in the world ranking). |
| 1081526 (exchange tier) | Infinite vs Insiders | Polymarket market [5650404](https://gamma-api.polymarket.com/markets/5650404) (`cs2-inf6-ins-2026-10-19`) exists: outcomes ["Infinite","Insiders Esport"], but `updatedAt` 2026-10-15T08:26:50Z and bestBid 0.41 / bestAsk 0.97. | The exchange tier correctly rejects it (observation older than eight hours; a 56-point joke book is not a line). The researched listing above is the fresh two-sided source instead. If the exchange book trades again within the evidence window, the automated tier outranks this receipt and replaces it. |

**Limitation that applies to every receipt:** the listing supplies no
price-change timestamp, so the observation ages out under the same eight-hour
evidence window as every other quote (`scripts.core.MAX_AGE`). After the window
(15:32Z today for the DraculaN receipt) the row reverts to the research-only
tier — with a pick and a blank percentage — until a listed line is re-observed.
An automated book adapter (fetching the listing on every refresh) would remove
this limitation; none exists in `scripts/refresh.py` yet and adding one was
outside this session's claimed scope (logged for a follow-up).

## 4. Identity handling (no invented aliases)

The listings use slightly different labels than the board ("Infinite Gaming" vs
"Infinite", "Insiders Esport" vs "Insiders"). Each receipt carries the exact
alias list **with primary-source links** (HLTV match page establishing the exact
opponent pair and UTC start, plus Liquipedia's DraculaN group listing linking
HLTV 2399590). The independent auditor refuses any alias without an
`https://` source link (regression-tested). The fixture-id + opponent-pair +
UTC-start triple must all match before a line is used.

`plain_name` now folds diacritics (NFKD + drop combining marks), so "Los
Niños" and "LOS NINOS" resolve to one key. This is the fix session **ef0969b9**
requested in `research/ef0969b9/UNPRICED-FIXTURE-LINES.md` §1; it is name
normalisation only and changes no probability. Regression note: the auditor's
independent `name()` mirrors the same fold so a diacritic pair cannot pass the
collector and fail the auditor (or vice versa).

## 5. Reproducibility

`quote_book` re-derives every published number from the receipt's raw two-way
decimal odds on each build: `p_i = (1/o_i) / Σ(1/o_j)`, margin bounds −2%…25%,
observation freshness, observation ≤ start. The validator (`reconstruct_quote` +
`calculator_for`) and the independent auditor (`verification-c6` branch)
replay the same inputs separately and refuse altered odds, forged probabilities,
missing alias sources and stale observations (all regression-tested in
`tests/test_book_research_2e920ea8.py`). No number in the receipts file is
hand-derived: only odds and timestamps are recorded as observed.

## 6. Manual-review links (everything above is reproducible from these)

* EGW listings: [Infinite–Insiders](https://egamersworld.com/counterstrike/match/V1JAWhPomg/infinite-gaming-vs-insiders-esport-sy3npvC5f) ·
  [Procyon–LOS NINOS](https://egamersworld.com/counterstrike/match/0U32SId-H/procyon-vs-los-ninos-NQ8TFsKyF) ·
  [ex-6666–Privateer](https://egamersworld.com/counterstrike/match/EkjkYUfoNl/ex-6666-vs-privateer-gaming-sfo_MjtRV) ·
  [antidaun–Phantom Academy](https://egamersworld.com/counterstrike/match/EkjkYUfoNl/antidaun-vs-phantom-academy-zXFTwo17o8)
* HLTV fixtures: [2399590](https://www.hltv.org/matches/2399590/infinite-vs-insiders-digital-crusade-draculan-season-7) ·
  [2399672](https://www.hltv.org/matches/2399672/procyon-vs-los-ninos-cct-2026-south-america-series-7) ·
  [2399681](https://www.hltv.org/matches/2399681/ex-6666-vs-privateer-cct-2026-challengers-europe-series-8) ·
  [2399682](https://www.hltv.org/matches/2399682/antidaun-vs-phantom-academy-cct-2026-challengers-europe-series-8)
* Polymarket reads (cache-busted, dated): [5650404](https://gamma-api.polymarket.com/markets/5650404) (dormant Infinite–Insiders book),
  [5721649](https://gamma-api.polymarket.com/markets/5721649) (Procyon–Los Niños 0.69/0.31 at 07:21:08Z, cf. ef0969b9 §1).
* Liquipedia: [DraculaN Season 7](https://liquipedia.net/counterstrike/DraculaN/Season_7).
