# Unpriced fixtures: external-line evidence and the one proven source-side gap

Session `ef0969b9`, 16 October 2026 (UTC). Deliverable for the integration session
(`1abe803f`) and the publisher of `research/refresh-ab18fe2a/DIAGNOSIS.md` (`ab18fe2a`).
This file is evidence and a change request. It does **not** edit `data/**`,
`scripts/build.py`, `scripts/core.py` or `scripts/refresh.py` — those are outside this
session's claimed file scope.

Requirement it serves: every match gets a pick, probabilities must come from known
external betting lines (or our own originated lines), and values that cannot be
confirmed from a source stay blank.

## 1. Row 1081502, Procyon Gaming vs LOS NINOS — a live Polymarket line exists today

Our live board carries this as the only unpriced fixture today
(`unresolved.html`: "No price quote", research-only, 16 Oct 16:00Z). Polymarket does
have it, and it has been trading through the day.

Read 2026-10-16T07:2x-07:27Z via `fetch_page`
(`https://gamma-api.polymarket.com/events?id=1192433&cb=ef0969b9-ev1192433`):

| Field | Value |
| --- | --- |
| Event | `1192433`, ticker/slug `cs2-pcy-ln-2026-10-16`, "Counter-Strike: Procyon Gaming vs Los Niños (BO3) - CCT South America Series 7 Group Stage" |
| Series | `10310` ("Counter Strike", `recurrence: daily`) — the same series `scripts/refresh.py` already queries |
| Whole-match market | `5721649`, outcomes `["Procyon Gaming","Los Niños"]`, prices **0.69 / 0.31** (read 07:21:08Z `updatedAt`); liquidity $6,291.07, volume $56.06 |
| Map 1 market | `5721647`, `0.605 / 0.395`, bid 0.57 / ask 0.64, spread 0.07, liquidity $2,040 |
| Game start | `gameStartTime` `2026-10-16 16:00:00+00`; event `endDate` `2026-10-16T22:00:00Z`; event `updatedAt` 07:27:44Z |
| Book state | `acceptingOrders: true`, `active: true`, `closed: false`; resolution source hltv.org |

Book state matters as much as the price: bid 0.57 / ask 0.64 on the map-1 market is a
7-point spread with $2,040 of liquidity, i.e. inside the repository's own
`exchange_wide` tolerance (spread > 25 and ≤ 60 points requires ≥ $100 liquidity),
while the whole-match market quotes a tighter pair. **This is a two-sided external
quote that our pipeline should be able to publish**; the row does not need
research-only treatment.

### Why the pipeline missed it (two things verified, one left open)

1. **Filters are satisfied.** The event is `series_id 10310`, `active: true`,
   `closed: false`, `endDate 2026-10-16T22:00:00Z >= 2026-10-16T00:00:00Z` — exactly
   the four conditions in `scripts/refresh.py`'s Polymarket branch
   (`GAMMA/sports` → `sport == 'cs2'` → `GAMMA/events?series_id=…&active=true&closed=false&end_date_min=…`).
   So the feed query *should* return it.
2. **The names cannot match.** Verified with the repository's own code:
   `python -c "from scripts.core import ALIAS_MAP, plain_name"` →
   `plain_name("Los Niños")` folds to `losniños` (no diacritic folding), while HLTV
   spells the team `LOS NINOS` (`losninos`); neither `procyon`, `procyongaming`,
   `losninos`, `losniños` nor `infinite` has an `ALIAS_MAP` entry (`insiders` does).
   A pair match is therefore impossible for this fixture regardless of the feed.
3. **Whether the feed page containing the event is reached is still open.** The refresh
   reason recorded for the row is "No exact team-pair and UTC-start match in retrieved
   feed", which is consistent with (2), but this session cannot see the run's retrieved
   pages (job logs are not retrievable from the sandbox), so pagination coverage is
   *unverified*. Do not assume the query shape is complete until a run prints the
   number of events retrieved.

### Request (files owned by 1abe803f)

* Add `ALIAS_MAP` entries (or an equivalent exact-pair mapping) for at least
  `procyon` → `procyon gaming`, `procyongaming`, `losninos`/`losniños` →
  `los ninos`, `infinite` → `infinite` in `data/identities.json`.
* Fold diacritics in `scripts/core.py:plain_name` (NFKD + strip combining marks) so
  "Los Niños" and "LOS NINOS" resolve to the same key. This is a name-normalisation
  change, not a probability change: it only lets an existing market line be found.
* Nothing else in the pick logic changes, and nothing here overrides the repository's
  "never a default 50/50" rule.

## 2. The other currently unpriced rows — what was checked, and what was found

All of these already carry a model line (VRS-based) on the live site, so no pick is
missing; what is missing is an external market quote. Checked 16 Oct 07:2xZ, and
recorded here as negative results so the queries are not repeated blindly:

| Row | Attempted | Result |
| --- | --- | --- |
| aimclub vs BASEMENT BOYS (19 Oct 09:00Z) | `public-search?q=Basement Boys` → event `1183120`, market `5650407` | Exists, prices `0.495/0.505`, but the book is bid 0.03 / ask 0.96 with $254.35 liquidity — a 93-point spread. `refresh.py` is right to reject it (spread ceiling); do **not** publish this as a line |
| BET-M vs Just Players (17 Oct 08:00Z) | `public-search?q=BET-M` (also `events_status=active`, `limit_per_type=50`) | Only resolved history (BET-M 33 vs Partizan, Apr 2026; B8 vs BET-M 33, Sep 2026). No market for the 17 Oct fixture surfaced. Unresolved |
| GenOne vs Butterfly (17 Oct 11:00Z) | `public-search?q=GenOne` | Only resolved history (KOLESIE vs GenOne, Jun 2026). Unresolved |
| Infinite vs Insiders (19 Oct 09:00Z) | `public-search?q=Infinite` | Only resolved history (K27 vs Infinite, Jul 2026). Unresolved |
| Nexus vs WROTBERRY (DraculaN B) | `public-search?q=Nexus` | Non-esports noise (a token project). Unresolved |
| BakS vs Fire Flux, Banda chuya vs Enjoy, ASTRAL vs Leo | not yet re-queried this session | Unresolved; the live `unresolved.html` rows for them still show "No price quote" |

`public-search` is loose text search ordered by relevance/volume and returns closed
markets first, so it is only usable when the exact Polymarket team spelling is known.
For these rows the honest status is "no external quote located with the queries
attempted", not "no line exists".

## 3. Enumeration methods that do and do not work (measured)

| Query | Verdict |
| --- | --- |
| `gamma/events?id=<id>` | ✅ Works, returns the event with all child markets and prices. Use it to confirm a single fixture |
| `gamma/markets?slug=<slug>` | ✅ Works (used for Procyon, 19 Oct DraculaN markets) |
| `gamma/markets?tag_id=100780&closed=false&active=true&limit=N&order=id&ascending=false` | ✅ Works: tag 100780 is "counter strike 2"; newest-first page 0 is the live/today set |
| `…&game_start_time_min=…&game_start_time_max=…` | ❌ Appears ignored: with a 17 Oct window the API returned a 2026-03-10 market (id 1544458) |
| `…&order=gameStartTime&ascending=true` | ❌ Ignored: same request returned the March market |
| `gamma/events?…&order=id&ascending=true` (refresh's own shape, and `ascending=false`) | ⚠️ Returns the crypto/MicroStrategy end of the id space, not CS fixtures; fine only as a paging source with an id/date filter |
| `gamma/public-search?q=<team>` | ⚠️ Loose; good when it hits, useless for pre-listing fixtures |
| `gamma/events/pagination?tag_slug=counter-strike` | ⚠️ `hasMore:false`, `totalResults:2` (Valve sticker trade-up events only) |

## 4. What this session did *not* do

* No edit to `data/**`, `scripts/refresh.py`, `scripts/core.py` or `scripts/build.py`.
* No price, probability or pick was written into any published data file.
* No number in this document is derived from Hotspawn or from any Hotspawn fan vote.
* Every figure above is quoted with the endpoint and the UTC read time that produced
  it; anything not read from a source is marked unresolved rather than estimated.
