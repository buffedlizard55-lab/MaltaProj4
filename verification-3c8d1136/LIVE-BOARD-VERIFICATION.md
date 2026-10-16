# Live board verification — session `3c8d1136`, 16 October 2026

Every line below was read from a primary source in this session and is reproduced with the
receipt that proves it. Values that could not be read are left blank and flagged; nothing is
inferred. Two snapshots are used:

* **published** — `data/latest.json` on main `693b637`, snapshot `2026-10-16T07:21:23Z`,
  build published at <https://buffedlizard55-lab.github.io/MaltaProj4/> (`build-info.json`
  revision `0ba6742d`, `built_at 07:24:04Z`);
* **live** — this session's own CI refresh, run
  [38871406232](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38871406232),
  snapshot `2026-10-16T08:06:48Z`, retained in
  [`research/harvest-3c8d1136/latest.json`](../research/harvest-3c8d1136/latest.json) with
  the raw Hotspawn fixtures response in
  [`research/harvest-3c8d1136/fixtures-raw.json`](../research/harvest-3c8d1136/fixtures-raw.json).

## 1. The two Thunderpick deciders — verified line by line

### Aurora vs 9z · Hotspawn `1080205` · 16 Oct 14:00Z · Group A decider · best of 3 (LAN)

| Item | Board value | Primary source read in this session | Result |
|---|---|---|---|
| Fixture inventory | `1080205`, teams Aurora / 9z | Hotspawn fixtures API and both lobby views, 102/102/102 agreement at 08:06:33Z | **verified** (Hotspawn is used for inventory only) |
| Start | `2026-10-16T14:00:00Z` | Hotspawn `scheduled_start_time 1792159200000`; Polymarket `gameStartTime "2026-10-16 14:00:00+00"` and `eventStartTime 2026-10-16T14:00:00Z`; [HLTV 2399412](https://www.hltv.org/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026) displays `10:00 16 Oct` with countdown `5h 49m 4s` ⇒ 14:00:00Z − 5:49:04 = 08:10:56Z, the minute it was read | **verified**, three independent sources |
| Lock | `2026-10-16T13:54:00Z` | Hotspawn `lock_time 1792158840000`, `lock_offset_sec 360` | **verified** (but see irregularity #3) |
| Format | *blank* | Hotspawn `best_of: null`, `series_format: null` for **102 of 102** rows; Polymarket question says `(BO3)`; HLTV says `Best of 3 (LAN)` | left blank on the board per the no-inference rule — irregularity #4 |
| Probability | Aurora **0.695** / 9z **0.305** | [Polymarket market 5733288](https://gamma-api.polymarket.com/markets/5733288), `outcomePrices ["0.695","0.305"]` for outcomes `["Aurora Gaming","9z"]`, `updatedAt 2026-10-16T08:05:07.810983Z`, `active true`, `closed false`, `acceptingOrders true`, `sportsMarketType moneyline` | **reproduced exactly** |
| Market quality | — | same market: `bestBid 0.69`, `bestAsk 0.70` (1-point spread), liquidity **$102,430.3165** at 08:06Z (was $100,199.2177 at 07:43Z) | **verified**, above the exchange gate |
| Fair odds | 1.4388489208633095 / 3.278688524590164 | recomputed here as 1 ÷ p: 1.4388489208633095 / 3.278688524590164 | **exact match** |
| Pick | **Aurora** | the higher of the two sourced probabilities | **consistent with policy** |
| Model cross-check | VRS 0.6796 / 0.3204 | Valve standings `live/2026/standings_global_2026_10_05.md` at commit `eec4853d`, 1716 vs 1543 points | model and market agree within 1.6 points |
| Source link on the row | `https://www.hotspawn.com/matches/aurora-vs-9z-thunderpick-world-championship-2026-1080205` | taken from the snapshot's own `source_url`; never constructed | **verified** |

### BetBoom vs Legacy · Hotspawn `1081775` · 16 Oct 17:00Z · Group B decider · best of 3 (LAN)

| Item | Board value | Primary source read in this session | Result |
|---|---|---|---|
| Start | `2026-10-16T17:00:00Z` | Hotspawn `scheduled_start_time 1792170000000`; Polymarket `gameStartTime "2026-10-16 17:00:00+00"`; [HLTV 2399413](https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026) displays `13:00 16 Oct` with countdown `8h 45m 13s` ⇒ 17:00:00Z − 8:45:13 = 08:14:47Z | **verified** |
| Lock | `2026-10-16T16:54:00Z` | Hotspawn `lock_time 1792169640000`, `lock_offset_sec 360` | **verified** (irregularity #3) |
| Probability | BetBoom **0.365** / Legacy **0.635** | [Polymarket market 5763247](https://gamma-api.polymarket.com/markets/5763247), `outcomePrices ["0.635","0.365"]` for outcomes `["Legacy","BetBoom Team"]`, `updatedAt 2026-10-16T08:05:07.810983Z`, accepting orders | **reproduced, and mapped by name — not by position**: Polymarket lists Legacy first, the board lists BetBoom first, and the board's `[0.365, 0.635]` is correct for its own team order |
| Market quality | — | `bestBid 0.63`, `bestAsk 0.64`, liquidity **$109,719.2318** at 08:06Z (was $107,169.8693 at 07:43Z) | **verified** |
| Fair odds | 2.73972602739726 / 1.574803149606299 | 1 ÷ p recomputed here | **exact match** |
| Pick | **Legacy** | the higher sourced probability | **consistent with policy** |
| Model cross-check | VRS 0.2068 / 0.7932 | same Valve standings, 1596 vs 1931 points | the model is **more** bullish on Legacy than the market (15.8 points); disagreement is published on the analysis page, not used as a pick |
| Source link on the row | `https://www.hotspawn.com/matches/betboom-vs-legacy-thunderpick-world-championship-2026-1081775` | snapshot `source_url` | **verified** |

Both fixtures are worth **7 leaderboard points** (`tier "s"`, `base_points 2`,
`points_breakdown` game 1.25 × tier 3 × series 1 × stage 1 × tournament 1 ⇒ floor(7.5) = 7;
`stage "group stage and playoffs"`), read from Hotspawn's own payload.

## 2. Rows that moved since the published build — and why that is correct

| Fixture | Published 07:21Z | Live 07:49Z / 08:06Z | Source |
|---|---|---|---|
| `1079586` Ninjas in Pyjamas vs Team Liquid (Stake Pulse Beat III Playoffs, 08:00Z) | NIP 0.505 / Liquid 0.495, pick **NIP** | 0.495 / 0.505, pick **Team Liquid** | [market 5732258](https://gamma-api.polymarket.com/markets/5732258) `outcomePrices ["0.495","0.505"]`, `updatedAt 2026-10-16T07:49:10.803008Z`, liquidity **$307,592.3098**, bid 0.49 / ask 0.50. The exchange crossed; the pick followed it. Fixture locked 07:54Z and left the feed by 08:06Z |
| `1080285` Voca vs Phantom (Elisa BreakOut Series #2 Group B, 08:00Z, BO1) | 0.455 / 0.545, pick **Phantom** | row now `not_open`, pick withheld, flag "Scheduled feed entry is past its start; current match status is unverified." | [market 5583525](https://gamma-api.polymarket.com/markets/5583525) `updatedAt 07:49:10.803008Z`, liquidity $54,793.5341. Withholding after the lock is the documented behaviour |
| `1081502` Procyon vs LOS NINOS (CCT South America 2026 Series #7, 16:00Z) | research-only, **no percentage** | **0.677691790620314 / 0.3223082093796859**, pick Procyon, method `bookmaker_fallback` | Pinnacle matchup **1638406883**, league `CS2 - CCT South America Series` (id 235977), participants Procyon `home` / LOS NINOS `away`, `startTime 2026-10-16T16:00:00Z`, `bestOfX 3`, `status pending`, moneyline **home −274 / away +187**, `cutoffAt 2026-10-16T23:00:00+00:00`, observed `2026-10-16T07:56:20.110106Z`. Recomputed here: decimal 1.364964 / 2.87 ⇒ implied 0.732619 / 0.348432 ⇒ total 1.081051 ⇒ de-margined **0.677691790620314 / 0.3223082093796859**. Row keeps its published flag "Single bookmaker; price update timestamp not supplied. Observation time shown." |
| `1081526` Infinite vs Insiders (DraculaN Group A, **19 Oct 09:00Z**, BO1) | research-only, no percentage | **0.69 / 0.31**, pick Infinite, method `exchange_wide`, flag "Low confidence: wide two-sided quote (spread 56 points). Market mid only; the true value is uncertain." | [market 5650404](https://gamma-api.polymarket.com/markets/5650404) `outcomePrices ["0.69","0.31"]`, liquidity **$106.4399**, bid 0.41 / ask 0.97 ⇒ spread **56 points**, `updatedAt 2026-10-16T07:37:08.092487Z`. Passes the documented wide tier (≥ $100 liquidity, ≤ 60-point spread) and is labelled low confidence |
| `1079626`, `1079628`, `1080204` | `not_open` historical rows present only because a cached lobby still listed them | **removed** | `removed_ids` in the live snapshot; the fresh API and both fresh HTML views agree they are no longer scheduled fixtures |

Net effect on the open board: **39 open rows, 39 with a pick, 37 with a published
probability** at 08:06:48Z.

## 3. Day-1 to day-3 results, re-read from the official event page

[HLTV event 8932](https://www.hltv.org/events/8932/thunderpick-world-championship-2026)
(Malta, 14–18 October 2026, $1,000,000 — $500,000 player prize pool plus $500,000 club
share, 8 teams, two GSL-style groups), read in this session:

| Group | Series | Result |
|---|---|---|
| A opening | Falcons vs NIP | **2–0** |
| A opening | 9z vs Aurora | **2–0** (the day-1 upset on the board's own model line) |
| A winners' | Falcons vs 9z | **2–1** |
| A elimination | NIP vs Aurora | **0–2** |
| A decider | 9z vs Aurora | pending, 16 Oct 14:00Z |
| B opening | Legacy vs PARIVISION | **2–0** |
| B opening | FURIA vs BETBOOM | **2–0** |
| B winners' | Legacy vs FURIA | **1–2** |
| B elimination | PARIVISION vs BETBOOM | **1–2** |
| B decider | BETBOOM vs Legacy | pending, 16 Oct 17:00Z |

Placements already fixed: **7th–8th PARIVISION and NIP**, $10,000 each plus $10,000 club
share. Prize distribution read from the same page: 1st $250,000 + $250,000 club, 2nd
$125,000 + $125,000, 3rd $50,000 + $50,000, 4th $25,000 + $25,000, 5th–6th $15,000 +
$15,000.

## 4. The Aurora roster premise — corrected again, independently

The user's brief mentions "a recent roster change for Aurora". Read directly this session:

* [HLTV team 11861 · Aurora](https://www.hltv.org/team/11861/aurora): main lineup
  **XANTARES, woxic, Jimpphat, kyxsan, Wicadia**, coach **ash**; transfer list shows
  *kyxsan transfers from Falcons to Aurora — Jul 8th 2026* and *ash joins Aurora as coach —
  Jul 3rd 2026*; MAJ3R listed as **BENCHED**; Jimpphat and kyxsan each **105 days** on the
  team and 63 maps.
* [HLTV news 45082](https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan)
  (8 July 2026): kyxsan completes the rebuild, replacing MAJ3R, soulfly and coach Fabre
  alongside Jimpphat and ash; the new international Aurora debuted at BLAST Bounty 2026
  Season 2 from 21 July.
* [Liquipedia · Aurora Gaming](https://liquipedia.net/counterstrike/Aurora_Gaming) timeline:
  29 June bench Fabre · 2 July bench MAJ3R and soulfly · 3 July sign Jimpphat and ashhh ·
  8 July acquire kyxsan from Team Falcons.

**Conclusion:** there is **no October 2026 roster change**. The relevant change is the
8 July 2026 rebuild — a new in-game leader, a new coach, a new rifler and a switch from
Turkish to English communication, ~14 weeks and 63 maps before this decider. That is a real
onboarding factor (it is why the day-1 loss to 9z and the day-2 win over NIP both look like
variance rather than a settled read), but it is not new information on the day of the match,
and this board does not treat it as a probability input. This independently reproduces the
correction recorded by sessions `1abe803f` and `ab18fe2a`.

## 5. Hotspawn's own editorial — context only, never a probability input

[Legacy and Aurora in Last Chance Saloon – Thunderpick World Championship 2026 Day 3
Preview](https://www.hotspawn.com/counter-strike/news/thunderpick-world-championship-2026-day-3-preview),
Daniel Morris, Counter-Strike Content Lead, **15 October 2026**: *"My prediction: 9z 1:2
Aurora"* and *"My prediction: BetBoom 0:2 Legacy"*, reasoning that Aurora "have had a little
time to warm up to the event" after the day-1 loss, and that BetBoom "found themselves in
that position in the first place" against PARIVISION.

Recorded because it is the pick'em host's own published read and it **agrees with both board
picks**. Per the project's standing rule, Hotspawn is used to establish fixture inventory and
— separately, from its rules page — scoring; no Hotspawn opinion, crowd percentage or
prediction is used as a probability anywhere on this site.

## 6. Irregularities found in this session

1. **Fixed and proved in CI — the freshness anchor was a cached HTML copy.** `fixtures_observed_at`
   was `2026-10-16T03:23:45Z` on the published build because the general lobby answered with
   `Age 6251` (and the CS2 page `Age 14241`), and `inventory.discover` anchors at the oldest
   observation. Every open row therefore expired at 11:23:45Z — hours before its own fixture.
   Detail, measurement and before/after in
   [`research/cadence-3c8d1136/FRESHNESS-ANCHOR.md`](../research/cadence-3c8d1136/FRESHNESS-ANCHOR.md).
2. **Fixed and proved in CI — `coverage: partial` was a staleness artifact.** 103 / 95 / 95
   became 102 / 102 / 102 (`verified`) once the HTML views were current; the 11 API-only
   fixtures all already carried picks, and the 3 HTML-only fixtures were finished matches.
   Detail in [`research/coverage-3c8d1136/COVERAGE.md`](../research/coverage-3c8d1136/COVERAGE.md).
3. **Hotspawn's rules page and its own feed disagree on the lock offset** (previously found by
   session `0e407ec7`, re-verified here): the rules page says picks lock **5 minutes** before
   start, while every current fixture carries `lock_offset_sec: 360` (**6 minutes**) —
   `1080205` start 14:00:00Z, lock 13:54:00Z. The board publishes the feed's earlier,
   stricter lock time. Both values are published as given; nothing averaged.
4. **Hotspawn publishes no series format at all**: `best_of` and `series_format` are `null`
   for **102 of 102** rows in the retained response, so the documented "known Hotspawn series
   format must agree" check can never fire. Both line sources do publish it — Polymarket in
   the market question (`(BO3)`, `(BO1)`) and Pinnacle as `bestOfX` (3 for matchup
   1638406883). The board correctly leaves format blank rather than importing it; the gap is
   logged for the integration session because a *sourced* format field would strengthen the
   fixture-to-market gate.
5. **Two open rows still have a pick but no probability** — `1081521` ex-6666 vs Privateer and
   `1081522` antidaun vs Phantom Academy, both 18 Oct, CCT Europe 2026 Challengers #8, both
   resting on HLTV ranking evidence only. Session `2e920ea8`'s claimed lane.
6. **No scheduled refresh ran for the 05:17, 06:17 or 07:17 UTC slots**; `pages.yml` has three
   scheduled runs in the repository's history (15 Oct 16:59:51Z success, 15 Oct 21:22:25Z
   failure, 16 Oct 04:33:39Z failure) and `refresh-watchdog.yml` has **zero**. The live board's
   freshness is currently delivered by push-triggered runs. Session `ef0969b9`'s claimed lane;
   logged as a request rather than edited here.
7. **HLTV match pages carry a server-rendered countdown**, and the six pages read in this
   session imply render instants of 08:10:56Z, 08:14:47Z, 08:18:54Z, 08:18:55Z, 08:19:09Z and
   08:19:10Z when the starts are taken as 14:00Z/17:00Z on 16 Oct and 14:00Z/17:00Z on 17 Oct
   plus 11:30Z/15:00Z on 18 Oct. Those agree with the minute each page was fetched, which is
   the arithmetic behind the UTC offset derivation in
   [`research/day4-3c8d1136/DAY4-READINESS.md`](../research/day4-3c8d1136/DAY4-READINESS.md).
   Recorded because the same class of caching that produced irregularity #1 can silently date
   any third-party page; HLTV displays no timezone on the page itself.

## 7. What this session did **not** touch

`scripts/core.py`, `scripts/hltv.py`, `scripts/build.py`, `data/*.json`, `site/**`, generated
root routes, `pages.yml`, `refresh-watchdog.yml` and `tests/**` are claimed by other sessions.
The only production code changed here is `scripts/refresh.py` (fetch layer: cache-busting and
receipt fields), plus this session's own read-only scripts under `scripts/*_3c8d1136.py`, its
workflow `.github/workflows/harvest-3c8d1136.yml`, its tests under `verification-3c8d1136/`
and its research directories. Requests for the other files are logged in `COORDINATION.md`.
