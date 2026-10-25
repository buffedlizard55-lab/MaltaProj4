# Independent line-by-line audit — session 5717f7d9

**Date:** 2026-10-25 · **Snapshot audited:** `data/latest.json` generated
`2026-10-25T13:46:54Z` (fixture evidence observed `13:43:19Z`) · **Base commit:** `d5b0739`
(merge of PR #322).

## 1. Scope and independence

The standing brief is a pick and a win probability for **every** CS2 match Hotspawn lists,
originated from external betting lines and HLTV — never from Hotspawn itself — with a separate
unresolved/limitations section, mobile discoverability, and an official source link on every row.

This session is an **independent verification**, not another publisher/diagnostic run (that space is
actively owned by other sessions; see `COORDINATION.md`). The auditor
[`scripts/audit_5717f7d9.py`](../../scripts/audit_5717f7d9.py) imports **no `scripts.*` code**. It
re-implements the name normalisation, the de-vig, and Valve's Glicko expected-score formula from the
documented primary rules, and re-derives every published number from retained evidence. A shared bug
therefore cannot validate itself. Machine-readable outputs:
[`audit-report.json`](audit-report.json), [`row-ledger.json`](row-ledger.json),
[`row-ledger.md`](row-ledger.md), [`mobile-probe.json`](mobile-probe.json).

## 2. Measured coverage — every open match is picked

| Metric | Value |
| --- | --- |
| Feed rows returned by the Hotspawn fixtures endpoint | **78** |
| Open (future) matches | **17** |
| Open matches with a pick | **17 (100%)** |
| Open matches with a win probability | **17 (100%)** |
| Open matches unresolved (no pick and no %) | **0** |
| Past/not-open feed rows, never priced | **61** |

Method mix on the 17 open rows: **11 strict Polymarket exchange lines · 1 labelled low-confidence
wide-exchange line · 1 researched esportsbook listing (Thunderpick via BO3.gg) · 4 originated Valve
VRS model lines.** There is no `model_vrs_mirror` or research-only row on this snapshot because the
primary rungs reached every fixture.

## 3. Every probability re-derived from primary evidence

All checks are arithmetic on retained evidence; nothing is inferred or filled in.

* **Exchange (11 rows) and wide exchange (1 row).** Each published probability equals the named
  Polymarket `outcomePrices` entry after orienting the exchange's outcome array to the fixture's team
  order. Two orientation cases were confirmed rather than assumed: fixture `1082697`
  (BESTIA/paiN) where Polymarket lists the teams in the reverse order, and `1079199`
  (Infinite/**BRUTE**) where the exchange spells the club `Brute` (case-fold identity). Markets are
  `active`, not `closed`, `acceptingOrders: true`, observed ~0.09 h before the snapshot. Strict rows
  have spread ≤ 0.25 and liquidity ≥ $100; the single wide row (`1082861`, spread 0.26, liquidity
  $3,287) sits inside the 0.60 ceiling and carries the visible low-confidence warning flag.
* **Researched bookmaker line (1 row).** `1082859` NEXVOID/Alter Ego re-derives exactly from the
  retained Thunderpick decimal odds 1.60 / 2.20: inverse probabilities normalised by their sum give
  0.578947 / 0.421053 (overround 7.95%), matching the published figures to 1e-9. The row discloses
  that this is a researched listing with no automated adapter and no price-update timestamp.
* **Originated Valve VRS model (4 rows).** Each re-derives from the two clubs' retained Valve points
  with the Glicko expected score at RD 75 (`g = 1/√(1+3q²RD²/π²)`,
  `E = 1/(1+10^(−g·Δ/400))`) and Valve's published fit calibration
  `p = 0.5 + 0.7986·(E−0.5)`. All four match the published probability to 1e-9, the retained
  `raw_expected` matches the re-derived expectation, probabilities sum to 1, and every row carries
  the "model estimate, not a market price" flag plus links to Valve's `model/fit.js` and
  `modelfit.png`.
* **Vendored-file cross-check.** The retained points, standing numbers and rosters were matched
  against the vendored official standings
  [`data/vrs/standings_global_2026_10_05.md`](../../data/vrs/standings_global_2026_10_05.md)
  (Valve commit `eec4853d…`). The duplicated Valve label **"The Huns"** (standing 122 = 944 pts and
  standing 213 = 701 pts, two different rosters) is correctly disambiguated to **standing 122** by a
  **4/5 HLTV roster overlap** — Valve's own ≥3-shared-player identity rule — never by name guessing.
* **Universal invariants.** Every open row: two probabilities in (0,1) summing to 1; fair odds equal
  the inverse probabilities; the pick is the favourite (a true 0.5/0.5 would publish no directional
  pick); at least one evidence entry with a working source URL; an `expires_at`; and **no probability
  evidence cites a Hotspawn host** — Hotspawn supplies inventory only. All 61 not-open rows carry no
  pick, probability or method.

## 4. The low-tier ladder really runs HLTV → esportsbooks → our model

The per-fixture `attempts` ledger shows the order the brief asks for, on the rows the featured
Polymarket path could not price. For example `1082792` HOTU vs The Huns and `1082793` 5star vs 1WIN
each record, in order: Polymarket strict (unresolved) → **HLTV** fixture/ranking/lineup (no numeric
two-way line) → **Pinnacle** (no exact pair) → Polymarket wide (unresolved) → **Thunderpick** probe →
**GG.BET** (HTTP 403) → **BO3.gg** feed → book gap recheck → **Valve VRS model (resolved)**. The
bookmaker row `1082859` is resolved one rung earlier by the BO3.gg/Thunderpick listing, and the wide
row `1082861` by the relaxed exchange tier. No fixture is dropped to a blank without this documented
trail, and the separate [Unresolved & non-market picks](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html)
page plus the executive-summary limitations section are rendered even at a zero unresolved count.

## 5. Mobile / discoverability — measured, not asserted

[`mobile-probe.cjs`](mobile-probe.cjs) drives headless Chromium against the committed root pages at
real phone widths (receipt [`mobile-probe.json`](mobile-probe.json), no page errors at any width):

| Width | index horizontal overflow | "Updated picks" link above the fold | Phone tab bar | picks.html overflow / % shown |
| --- | --- | --- | --- | --- |
| 320 px | none | yes (quicknav y≈316) | present, 5 links | none / both teams' % |
| 390 px | none | yes (y≈300) | present, 5 links | none / both teams' % |
| 412 px | none | yes (y≈300) | present, 5 links | none / both teams' % |

The executive summary's `#exec-quicknav` links in-site to **Updated picks** (`picks.html`) and
**Unresolved & limits** (`#unresolved-limits`); the fixed bottom bar reads Home · Picks · Unresolved ·
Matches · Analysis on every real page. Every one of the 17 priced rows on `picks.html` has an
external official source link and shows both teams' percentages and the pick. Internal links resolve
(including the `?status=…` filtered routes); `methodology.html` is a redirect stub to `sources.html`
and is correctly exempt from the tab-bar rule.

## 6. Irregularities and limitations (source-linked, none blocking)

The auditor returns **0 hard failures and 0 unexplained flags**. Three `info`-level observations
remain, each a recurring, already-disclosed limitation rather than a new defect — so no duplicate
Flagged-for-Review note was added (the board's additive rule is one note per new finding):

1. **Fixtures `1086696` and `1086697` have no dedicated Hotspawn match page**, so their official
   Hotspawn link is the pick'em lobby (`https://play.hotspawn.com/cs2-pickems`). The per-row primary
   source remains the fixtures-feed API receipt, retained with a sha256 in `fixture_sources`. The
   structural phenomenon is already flagged under review note
   `session-0cc1138a-1081606-no-match-page-2026-10-23`; this audit names the two current fixtures.
2. **GG.BET was unreachable from the runner (HTTP 403 after rate-limit waits)** on this snapshot, and
   two EGamersWorld gap rechecks for `1082792`/`1082793` returned 403. This is the documented
   book-access limitation (see review notes `book-access` and
   `esportsbook-access-probe-2026-10-16`); neither row needed those hosts because higher rungs or the
   VRS model resolved them.
3. **61 of 78 feed rows are past-dated** records the endpoint still returns with
   `status: scheduled`; they are labelled past fixtures, excluded from picks, and never priced
   (snapshot `issues[0].code = feed_status`).

## 7. Gates run locally

* `python -m scripts.audit_5717f7d9` → exit 0, 0 fail / 0 flag / 3 info.
* `python -m unittest tests.test_session_5717f7d9` → **18 tests OK** (positive contracts plus six
  synthetic tamper tests proving the auditor fails closed).
* Full suite `python -m unittest discover -s tests` → **1,646 tests OK (12 skipped)**.
* Canonical `python -m scripts.validate --data data/latest.json --site .` → exit 0
  (78 rows / 17 calculations / 15 pages / 730 links / 20 checksums / 182 displayed rows).
* Headless Chromium mobile probe → no overflow, no page errors at 320/390/412 px.

## 8. Official sources used for manual review

* Hotspawn fixtures feed (inventory only):
  `https://phpstack-1372681-645984.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`
  and lobby `https://play.hotspawn.com/cs2-pickems`.
* Polymarket Gamma API (exchange lines): `https://gamma-api.polymarket.com/events`.
* Pinnacle guest esports API: `https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight`.
* HLTV matches and dated Valve ranking: `https://www.hltv.org/matches`,
  `https://www.hltv.org/valve-ranking/teams/2026/october/25`.
* BO3.gg CS2 feed (researched Thunderpick listing): `https://api.bo3.gg/api/v1/matches`.
* Valve official Regional Standings (model inputs, formula and calibration):
  `https://github.com/ValveSoftware/counter-strike_regional_standings`
  (blob commit `eec4853d7bcf0f1f7efe7f0d901234bef7e98b75`, `model/fit.js`, `modelfit.png`).
