# Session b214c818 — research report

**Date:** 2026-10-19 (reads 04:10–05:00 UTC) · **Branch:** `arena/b214c818-maltaproj4`
**Question:** Can every open Hotspawn CS2 fixture the board cannot price like the featured rows be
researched (HLTV identity/ranking first, then esportsbook/betting lines) into a pick — including the
unverified Sangal–"Aurora YB" row — and can the executive summary be made phone-first with obvious
in-site links to the picks and the unresolved/limitations section?

**Answer:** Yes. All 11 open research targets now have a pick: 5 carry dated two-way book lines read
from listing pages (one of them the previously unpickable Sangal row, after a sourced label
mapping), 4 retain their label-only model lines after the listings that serve them turned out to
show placeholder odds only, and 2 retain research-only picks with no percentage. Nothing is
inferred: two identical-odds listings are recorded as **rejections**, and one model line is flagged
against secondary quotes that disagree with it.

Verbatim capture data, decision notes and identity evidence: `captures.json` in this directory.
Registers updated by `scripts/session_b214c818.py` (idempotent): `data/book-receipts.json` (this
session's 4 unique receipts + 6 `rejected_listings` — the fifth listing, Sangal–Aurora YB, was
already on file from parallel session 133fe7ca at the same pair/odds and is kept as-is),
`data/review-notes.json` (3 dated findings; the Aurora identity finding is already published by
session 133fe7ca's note and is not duplicated). The hero's archived Day-4 buttons had already been
replaced on `main` by the parallel sessions' in-site jumps (See every pick ↓ / Unresolved & limits);
this session's hero patch was dropped in favor of that merged version.

## Method

1. Fixture inventory from the Hotspawn feed snapshot (already captured by the previous refresh);
   open rows without a verified external line became the research queue. Hotspawn crowd
   percentages are never used.
2. HLTV first: each queued fixture was opened at `hltv.org` (exact match page where one exists) to
   verify the opponent pair, UTC start (read off the countdown), Best-of, and to collect lineup or
   ranking evidence. Liquipedia and the official Valve Regional Standings
   (`ValveSoftware/counter-strike_regional_standings`) were used only for identity resolution.
3. Esportsbooks second: the operator's/aggregator's own match pages at egamersworld.com (EGW) were
   read live. Two-way bookmaker-odds displays are accepted only as an **asymmetric** pair bound to
   both team labels on the same match page (with matching UTC start); the identical pair 1.8/1.8
   that EGW serves when no bookmaker data exists is the listing's placeholder and is rejected by
   policy (it would fabricate a 50/50). Secondary aggregators (kushvsporte.ru, stavka.tv,
   macesports.ru) and prediction markets (Polymarket, Robinhood) were consulted for corroboration
   or conflict flags only — never as receipts. HLTV fan votes are never used.
4. Accepted pairs were de-vigged by `scripts.core.quote_book` (round-the-books / overround, the
   same replay the validator runs) at the observation time, checked against the row's exact
   fixture start and aliases, and written as receipts. `scripts/books.py` re-reads each accepted
   listing URL on every scheduled refresh and renews the observation only when the live page
   re-confirms the exact pair, UTC start and an asymmetric bound pair.

Reads were made with the Arena retrieval tools (the runner's egress cannot reach these hosts
directly); every observation below is dated and linked in `captures.json`.

## Accepted listing lines (5)

All observed 2026-10-19; margin = displayed overround; window = 8 hours, renewable by
`scripts/books.py` while the page keeps re-confirming the pair.

| Fixture | Event | Book line (de-vigged) | Pick | Observed | Listing |
| --- | --- | --- | --- | --- | --- |
| 1081532 ASTRAL – Leo (Bo1, 19 Oct 10:45Z) | Digital Crusade DraculaN S7 | 2.05 / 1.68 → 45.0% / 55.0% (margin 8.3%) | Leo | 04:36Z | [V1JAWhPomg](https://egamersworld.com/counterstrike/match/V1JAWhPomg/astral-esports-vs-leo-team-8fOCBVAsJ) |
| 1081552 Nemesis – Nuclear TigeRES (Bo3, 19 Oct 14:00Z) | PGL Bucharest 2027 CQ | 1.75 / 2.00 → 53.3% / 46.7% (margin 7.1%) | Nemesis | 04:31Z | [4JaFCnn5Ve](https://egamersworld.com/counterstrike/match/4JaFCnn5Ve/team-nemesis-vs-nuclear-tigeres-L6K0vG-5-) |
| 1079181 Fire Flux – ex-6666 (Bo3, 19 Oct 17:00Z) | NODWIN Clutch Series 13 | 2.23 / 1.56 → 41.2% / 58.8% (margin 8.9%) | ex-6666 | 04:40Z | [Nk9F-Ov54e](https://egamersworld.com/counterstrike/match/Nk9F-Ov54e/fire-flux-esports-vs-ex-6666-g84ZstIes) |
| 1079646 Lavked – ex-6666 (Bo3, 20 Oct 17:00Z) | CCT Europe 2026 S11 | 2.20 / 1.57 → 41.6% / 58.4% (margin 9.1%) | ex-6666 | 04:40Z | [_rW8GEyWK](https://egamersworld.com/counterstrike/match/_rW8GEyWK/lavked-vs-ex-6666-7kGDDWVoD) |
| 1082157 Sangal – Aurora YB (Bo3, 20 Oct 12:00Z) | Stake Ranked Ep. 6 CQ | 1.08 / 6.28 → 85.3% / 14.7% (margin 8.5%) | Sangal | 04:13Z | [41yaj8BdVx](https://egamersworld.com/counterstrike/match/41yaj8BdVx/sangal-vs-aurora-young-blud-t529SG6szs) |

Every pair is a two-sided display of bookmaker odds from an aggregator listing; the underlying
bookmaker is unnamed and supplies no price-update timestamp — one listing, not consensus. Each row
publishes that limitation and its observation time. Corroboration exists on three pages (EGWxxxBOT
bookmaker-average sentences on 1079181 and 1079646 matching the displayed pairs; secondary
previews within a consistent distance) and is stored with the receipt. Two receipts also mark a
**contradiction cross-check**: the prior model line for 1081532 preferred ASTRAL (Valve rows 113 vs
117 on 18 Oct) while the book prices Leo — the documented ladder lets the market tier outrank the
model, and both numbers remain visible.

## Rejected listings (6) — negative findings, kept visible

Every one of these pages showed only the identical placeholder pair **1.8/1.8** (no bookmaker
data). Publishing it would fabricate a 50/50, so each row keeps its next documented tier:

| Fixture | Listing (UTC start) | What the row keeps |
| --- | --- | --- |
| 1081130 PCIFIC Espor – ILLYRIANS | [1sGIL2gAYu](https://egamersworld.com/counterstrike/match/1sGIL2gAYu/pcific-espor-vs-illyrians-GbfpHB8g8H) (19 Oct 08:00Z) | VRS model line; lineups captured for any later real listing |
| 1079643 The Last Resort – LFO 10 | [_rW8GEyWK](https://egamersworld.com/counterstrike/match/_rW8GEyWK/the-last-resort-vs-xWf8Vr4Hp) (19 Oct 17:00Z) | research-only pick (HLTV #159 over unranked LFO 10), no percentage; the listing leaves the opponent slot **unnamed** |
| 1079644 BakS eSports – ILLYRIANS | [_rW8GEyWK](https://egamersworld.com/counterstrike/match/_rW8GEyWK/baks-esports-vs-illyrians-ozacJiuxA) (20 Oct 11:00Z) | VRS model line; lineups captured |
| 1081862 Rare Atom – Alter Ego | [EJcHRdr5Vx](https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/rare-atom-vs-alter-ego-O8GeLuSod4) (20 Oct 05:00Z) | VRS model line (Rare Atom 59.5%), **flagged**: secondary quotes (Alter Ego ≈1.60 / Rare Atom ≈2.20) favour the opposite side; a cached EGW list snippet showed an asymmetric pair with unresolvable side order. Nothing averaged or guessed. |
| 1081863 Chinggis Warriors – WXM | [EJcHRdr5Vx](https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/chinggis-warriors-vs-wxm-_ddme1I7dZ) (20 Oct 07:00Z) | research-only pick (HLTV #61 over unranked WXM), no percentage; WXM publishes no roster (five unnamed slots) |
| 1081864 NEXVOID – Vitalem Aerem | [EJcHRdr5Vx](https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/nexvoid-vs-vitalem-aerem-LHqHITkk7x) (20 Oct 09:00Z) | VRS model line; lineups captured |

## Identity resolution — Sangal's opponent (1082157)

The only fixture without any pick had an **unverified opponent label** ("Aurora YB"). The mapping is
a label mapping only (no fuzzy matching, no academy/main-team conflation):

* Liquipedia's team page: *Aurora Young Blud (formerly stylized as AuroraYoung Blood)* is Aurora
  Gaming's academy team — [liquipedia.net/counterstrike/Aurora_Young_Blud](https://liquipedia.net/counterstrike/Aurora_Young_Blud);
* Liquipedia's Sangal Esports page lists this exact fixture as *"Sangal vs Aurora YB"*, Stake Ranked
  Ep. 6 Qual-Round 1, Oct 20 14:00 CEST (= 12:00 UTC) — [liquipedia.net/counterstrike/Sangal_Esports](https://liquipedia.net/counterstrike/Sangal_Esports);
* HLTV lists the same slot as *Sangal vs Aurora Young Blud* (match 2399777, Ro16, Bo3, 20 Oct 12:00
  UTC) and gives the team its own page (HLTV team 12366) — [hltv.org/matches/2399777](https://www.hltv.org/matches/2399777/sangal-vs-aurora-young-blud-stake-ranked-episode-6-closed-qualifier).

Only one team can occupy that slot; exact opponent and UTC start remain required on every use.
Plain **"Aurora"** (the main roster, VRS #6/#9) is deliberately *not* in this mapping. No official
rename statement exists for the short labels, so the mapping is published as a review finding
(session 133fe7ca's `aurora-yb-alias-133fe7ca` note, kept as the single published finding; this
session's independent evidence is in `captures.json`). HLTV's fan vote (86/14) on the fixture exists
and is excluded. At integration time the same mapping was found already registered in
`data/identities.json` by parallel session 133fe7ca (corroborated by session 8c8e3c5f); the entry is
kept as-is and this session's capture is additional evidence, not a second entry.

## Other identity/lineup evidence collected

* 1081532: the two Valve-standings "Leo" rosters (#112: aimy/drac/leen/next1me/Tarkky vs #340) are
  told apart by the EGW lineup (aimy, drac, leen, next1me) — the listing's Leo is the HLTV-ranked
  side; the receipt maps labels, not rosters.
* 1081552: HLTV 2399665 lower-bracket final, Bo3, 19 Oct 14:00Z — resolves a search-cache snippet
  that wrongly showed 17:00 and default odds.
* 1079181 / 1079646: Valve rosters (Fire Flux: Cizzx/Quality/xEternaLxx/zemix/zer0UKY; 6666:
  amster/dENZY/kL1o/rendysky/skcH) match both pages' lineups; ex-6666 = Valve label "6666".
* Rejected pages' lineups (PCIFIC, BakS, ILLYRIANS, NEXVOID, Vitalem Aerem) are captured so a later
  real listing can be identity-checked instantly.

## New negative findings (kept visible)

1. **Placeholder-odds listings** — six listings above display 1.8/1.8 only. These are rejections,
   recorded in `data/book-receipts.json` under `rejected_listings` with URLs, displayed values and
   reasons, and summarised on Flagged for Review (`b214c818-default-odds-rejections`).
2. **Secondary-quote conflict on 1081862** — stavka.tv's Alter Ego 1.60 / Rare Atom ≈2.20 vs our
   VRS line Rare Atom 59.5%; flagged, not resolved (`b214c818-rare-atom-alter-ego-conflict`).
3. **Aggregator-line limitation** — every accepted line is one aggregator's display of bookmaker
   odds with no price-update timestamp; the observation window and the automated re-observer are
   the expiry answer (`b214c818-book-line-upgrades`).
4. **Search-cache staleness** — EGW snippets showed default odds (Nemesis page 17:00/1.8) on three
   queued pages; live re-reads replaced them. Snippets are never receipts.

## Implementation summary

* `data/book-receipts.json`: this session's 4 unique receipts (replayed by `scripts/validate.py`
  from raw fields) + 6 rejections; the Sangal listing receipt was already on file (session 133fe7ca,
  same pair and odds one minute earlier) and is kept as the single entry.
* `scripts/books.py` (new): per-receipt re-observer used by the scheduled refresh; renews an
  observation only on a fully re-confirmed reading (JSON-LD name pair + exact UTC start + asymmetric
  odds bound to both labels), refuses 1.8/1.8 placeholders and unbound pairs, records parse misses
  as data. The committed research record is never rewritten.
* `scripts/refresh.py`: additive hook — re-observe, then price with the (possibly renewed) receipts
  before the VRS model tier; re-observation attempts land on the affected rows.
* `data/review-notes.json`: 3 dated findings (placeholder rejections, the 1081862 conflict flag,
  the aggregator-line limitation); the identity finding is already published by session 133fe7ca.
* `scripts/build.py`: this session's hero-button patch was **dropped at integration** — the parallel
  sessions had already replaced the archived Day-4 buttons with in-site jumps (See every pick ↓,
  View updated picks →, Unresolved & limits →).
* `tests/test_session_b214c818.py`: receipt replay (exact de-vig numbers), pick ladder for each of
  the five fixtures, eight-hour expiry behaviour, rank-tier fallback, placeholder refusals,
  identity mappings (including the "plain Aurora is not mapped" hazard), re-observer parse
  (placeholder / markup change / wrong start / access error) and register idempotency.

## Expected post-merge board (next live refresh)

All 11 open research targets have picks: 5 market-priced `bookmaker_fallback` rows (41–85%
favourites as above), 4 label-only `model_vrs` rows (1081130, 1079644, 1081862, 1081864 — 1081862
flagged), 2 research-only rows with no percentage (The Last Resort over LFO 10; Chinggis Warriors
over WXM, via the ranking/standings research tiers) — each with a link to its listing, HLTV fixture
and the dated receipt or rejection. If a listing stops re-confirming after 8 hours, the row visibly
falls back to the model/research tier rather than keeping a stale price.
