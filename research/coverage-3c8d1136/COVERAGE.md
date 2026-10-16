# Hotspawn coverage: what the parity gap actually was, and what is covered now

Session `3c8d1136`, 2026-10-16 (UTC). Companion to
[`FRESHNESS-ANCHOR.md`](../cadence-3c8d1136/FRESHNESS-ANCHOR.md). The requirement being
tested is the user's: *picks for every CS2 match listed on Hotspawn, with the site checking
for updates on its own.*

## 1. The gap, named fixture by fixture

The published snapshot at the time of writing (`data/latest.json` on main `693b637`,
snapshot 2026-10-16T07:21:23Z) reports `coverage: partial` with counts
`api 103 / page 95 / lobby 95 / retained 106`. [`scripts/coverage_report_3c8d1136.py`](../../scripts/coverage_report_3c8d1136.py)
reads the same snapshot's per-row provenance receipts and names every difference; the
generated tables are [`COVERAGE-PUBLISHED.md`](COVERAGE-PUBLISHED.md) (published snapshot)
and [`../harvest-3c8d1136/COVERAGE-LIVE.md`](../harvest-3c8d1136/COVERAGE-LIVE.md) (live
CI refresh).

**11 fixtures were returned by the fresh API and not by the two cached HTML views.** All 11
were listed by Hotspawn's API during 16 October (start times 16–18 October), and **all 11
already carry a pick** — 9 of them with a published probability:

| Fixture | Start (UTC) | Match | Event | Pick | Method |
|---|---|---|---|---|---|
| 1081493 | 16 Oct 08:00 | Eternal Fire vs Apogee Betclic | PGL Bucharest 2027: Closed Qualifier | Eternal Fire | exchange |
| 1081496 | 16 Oct 11:00 | Nemesis vs Nuclear TigeRES | PGL Bucharest 2027: Closed Qualifier | Nemesis | model_vrs |
| 1081497 | 16 Oct 13:00 | Young27 vs Young TigeRES | GLuck Yungstar 2026: Series #3 | Young TigeRES | exchange |
| 1081779 | 16 Oct 13:00 | Rune Eaters vs HyperSpirit | CyberClash Season 2: Closed Qualifier | Rune Eaters | model_vrs |
| 1081499 | 16 Oct 14:00 | BBL vs EYEBALLERS | PGL Bucharest 2027: Closed Qualifier | BBL | exchange |
| 1081780 | 16 Oct 16:00 | PRIVATE vs UPGRADE | CyberClash Season 2: Closed Qualifier | UPGRADE | model_vrs |
| 1081503 | 16 Oct 17:00 | GamerLegion vs ex-RUSTEC | PGL Bucharest 2027: Closed Qualifier | GamerLegion | exchange |
| 1081781 | 16 Oct 19:00 | Honvéd vs Lavked | CyberClash Season 2: Closed Qualifier | Lavked | model_vrs |
| 1081513 | 17 Oct 11:00 | Bebop vs Donstu | CCT Europe 2026 Challengers #8 | Donstu | model_vrs |
| 1081521 | 18 Oct 13:45 | ex-6666 vs Privateer | CCT Europe 2026 Challengers #8 | ex-6666 | research_rank (no percentage) |
| 1081522 | 18 Oct 13:45 | antidaun vs Phantom Academy | CCT Europe 2026 Challengers #8 | Phantom Academy | research_rank_single (no percentage) |

**3 fixtures were returned by the cached HTML views and not by the fresh API** — `1079626`,
`1079628` and `1080204` (Legacy vs FURIA, 15 Oct 16:00Z). All three are `not_open`
historical rows: the API's own `status=scheduled` filter had already dropped them, and the
cached page had not caught up.

So the 103 / 95 / 95 "partial coverage" flag was **not** a missing-pick problem. It was one
stale CDN copy on each side of the comparison: 95 + 11 − 3 = 103. No open fixture was left
without a pick because of it, and the union retention behaved exactly as designed.

## 2. After the freshness fix

Live CI refresh, run [38871406232](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38871406232),
snapshot `2026-10-16T08:06:48Z`
([`../harvest-3c8d1136/harvest-summary.json`](../harvest-3c8d1136/harvest-summary.json)):

* `coverage: **verified**`, counts `api 102 / page 102 / lobby 102 / retained 102` — the
  three official views agree, so parity is a real check again rather than a standing warning;
* **39 open rows, 39 with a pick**; the three 08:00Z fixtures had locked at 07:54Z and are
  correctly `not_open`;
* **37 of the 39 open rows publish a probability**. The two that do not are `1081521`
  (ex-6666 vs Privateer) and `1081522` (antidaun vs Phantom Academy), both 18 Oct CCT
  Europe Challengers #8, both holding an HLTV ranking-order research pick with no
  percentage. Pricing those two is session `2e920ea8`'s claimed lane; this session records
  the gap and does not touch `scripts/core.py` or `scripts/hltv.py`.

Two rows that were research-only on 15 October gained real market lines in the same window,
which is the tiered fallback working as documented:

* `1081502` Procyon vs LOS NINOS — **Pinnacle** matchup `1638406883`, moneyline home −274 /
  away +187, `status open`, `cutoffAt 2026-10-16T23:00:00+00:00`; de-margined to
  0.677691790620314 / 0.3223082093796859 (recomputed here from the American prices: decimal
  1.364964 and 2.87, implied 0.732619 and 0.348432, total 1.081051). Session `ef0969b9`
  independently identified the matching Polymarket market 5721649 for this fixture and asked
  for a diacritic-folding alias; the Pinnacle tier resolved the row without needing it.
* `1081526` Infinite vs Insiders — Polymarket market `5650404`, 0.69 / 0.31, liquidity
  **$106.4399**, bid 0.41 / ask 0.97 = a **56-point spread**, i.e. the documented
  `exchange_wide` tier (≥ $100 liquidity, ≤ 60-point spread) with the low-confidence flag
  published on the row. On 15 October session `dedd2e34` withheld this same market because
  its liquidity was below the floor; it now passes on its own numbers.

## 3. What a correct pick is worth — and why "contrarian" earns nothing by itself

[`SCORING-MODEL.md`](SCORING-MODEL.md) is generated from the exact fixtures response the
08:06Z refresh used ([`../harvest-3c8d1136/fixtures-raw.json`](../harvest-3c8d1136/fixtures-raw.json),
archived by SHA-256 from the refresh's own source archive). Results on that live payload:

* **102 of 102** CS2 rows satisfy `offered_points = floor(base_points × game_multiplier ×
  tier_multiplier × series_multiplier × stage_multiplier × tournament_multiplier)` — 0
  exceptions, 0 rows missing a scoring field;
* **7 of 7** scoring groups (same tier, stage, best-of, series format, base points and
  multipliers) show a *single* award while `total_picks` inside the group varies — for
  example tier `c` "waiting for information" pays 2 points across 38 fixtures whose
  `total_picks` runs from 0 to 74, and the two tier-`s` TWC deciders both pay 7 with 13 and
  23 picks.

That reproduces, on live data and with the arithmetic made explicit, what session
`0e407ec7` read from Hotspawn's official rules page
<https://play.hotspawn.com/how-it-works> (read again this session): *"Earn points for every
correct pick. Higher tier matches reward more points."* and *"Get bonus points for
consecutive correct picks. The longer your streak, the bigger the bonus."*, plus a weekly
leaderboard reset, picks editable until they lock, forfeits voided and cancellations
scoreless.

**Consequence for the user's question.** A correct pick is worth a fixed award that does not
depend on how many other players chose the same side, and a streak bonus rewards consecutive
*correct* picks. Expected score is therefore `offered_points × P(win)` plus a term that grows
with the probability of being right consecutively. Both terms are maximised by picking the
higher-probability side. Fading the crowd has **no scoring benefit of its own**: a
contrarian pick is only justified when our sourced probability says the favourite is wrong,
which is exactly the screen the analysis page applies. The exact streak-bonus formula is not
published anywhere this project can read, so no number is claimed for it (unchanged from
`0e407ec7`'s finding).

## 4. Requests logged for the owners of other files

1. **To the integration session (`1abe803f`, owner of `data/**`, `scripts/build.py`,
   `site/**`, generated root routes):** the freshness fix changes the *shape* of the next
   published snapshot — `coverage: verified`, three fewer historical rows, and every open
   row's `expires_at` moving to its own lock/quote TTL. Please refresh and republish rather
   than hand-editing `data/latest.json`, and note that the executive summary's "Fixture
   observation" line and the source-health table will now show `Age 0` / `X-Cache MISS` for
   both lobby views; the `request_url` and `cache_bust` fields in each receipt are the
   evidence for that.
2. **To the publication-reliability session (`ef0969b9`, owner of `pages.yml` and the
   watchdog):** the anchor fix only helps when a refresh actually runs. Measured at 08:05Z:
   three scheduled `pages.yml` runs ever, none for the 05:17/06:17/07:17 slots, and zero
   `refresh-watchdog.yml` runs. The live board's freshness is currently delivered by
   push-triggered runs from integration merges.
3. **To session `2e920ea8` (owner of the fallback-percentage lane):** the two rows still
   without a percentage are `1081521` and `1081522`, both 18 Oct, both with HLTV ranking
   evidence only.
