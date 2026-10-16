# TWC day-3 decider cross-check — external book lines and contrarian notes

Session **2e920ea8**, 16 October 2026 (UTC). Complements (does not replace) the
verified day-1/day-2 review in `data/analysis.json` (sessions 0e407ec7,
dedd2e34, 1abe803f). Every number below is a **dated observation from an
external source**; strategy statements are labelled analysis. Hotspawn is never
a probability input.

## 1. Day-2 corroboration read at 07:36Z (independent third source)

The EGamersWorld TWC event schedule/results feed
([event page](https://egamersworld.com/counterstrike/event/thunderpick-world-championship-2026-5X5sFiL7H),
read 07:36Z) independently shows the day-2 Group B winners' match as **Legacy 1
– 2 FURIA (15.10.26)**, matching `data/analysis.json`'s day-two record (HLTV
2399410/2399411 class fixtures) and the "Legacy lost the day-two winners' match
to FURIA" premise already used in the day-three guidance. No contradiction
found.

## 2. Day-3 deciders — bookmaker lines (BC.Game listing via EGamersWorld)

Read 2026-10-16 07:36Z on the event page above ("Bets on Thunderpick World
Championship 2026 by bc.game" widget, cross-checked against the match schedule
rows):

| Fixture | Board id / HLTV | BC.Game two-way | De-vig (this doc's arithmetic) | Exchange (Polymarket, prior receipts) | VRS model (analysis.json) |
| --- | --- | --- | --- | --- | --- |
| Aurora vs 9z · Group A decider · 14:00Z · Bo3 | 1080205 / [2399412](https://www.hltv.org/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026) | **1.41 / 2.84** (widget; schedule row shows 1.4 / 2.7) | Aurora 66.8% / 9z 33.2% | 69.5 / 30.5 at 04:22Z ([market 5733288](https://gamma-api.polymarket.com/markets/5733288)) | 68.0 / 32.0 |
| BetBoom vs Legacy · Group B decider · 17:00Z · Bo3 | 1081775 / [2399413](https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026) | **2.52 / 1.50** (widget; schedule row shows 2.5 / 1.48) | BetBoom 37.3% / Legacy 62.7% | 34.5 / 65.5 at 04:21Z ([market 5763247](https://gamma-api.polymarket.com/markets/5763247)) | 20.7 / 79.3 (14-pt gap, logged by dedd2e34) |

De-vig arithmetic (reproducible): `p_i = (1/o_i) / Σ(1/o_j)`. Aurora–9z:
1/1.41 = 0.70922, 1/2.84 = 0.35211, Σ = 1.06133 → 0.6682 / 0.3318.
BetBoom–Legacy: 1/2.52 = 0.39683, 1/1.50 = 0.66667, Σ = 1.06349 → 0.3731 / 0.6269.

**Cross-check verdict:** two independent external lines per decider, agreeing on
the favourite and within 2–3 points on the dog. The bookmaker reads both dogs
slightly shorter than the exchange (9z 33.2 vs 30.5; BetBoom 37.3 vs 34.5) —
i.e. the contrarian side is not book-cheap; nobody is giving the upsets away.

## 3. Contrarian-but-not-stupid notes (ANALYSIS, not verified fact)

* The 20–40% band is where a pick-em leaderboard can be climbed, and both decider
  dogs sit inside it on **two** external sources each. That makes them
  *possible* swings, not free ones: both lose more often than they win on these
  prices.
* Aurora–9z: 9z own the day-1 upset (2-0, Inferno 13-11 / Nuke 13-1 on Aurora's
  pick — HLTV 2399384) and took Mirage off Falcons on day 2, so the dog side is
  "not stupid". Against it: Aurora's day-2 form was sharp (2-0 over NIP, Wicadia
  1.65 on the HLTV match page) and the Aurora roster premise in the older draft
  was corrected by session 1abe803f — the newest additions (kyxsan, 8 July 2026)
  are ~14 weeks old, so "onboarding chaos" is **not** a live factor.
* BetBoom–Legacy: Legacy dropped the day-2 winners' match to FURIA (1-2);
  BetBoom face elimination with Major qualification at stake. The VRS model's
  79.3% Legacy vs the market's 62.7% is a documented model-vs-market gap
  (dedd2e34's ledger) — treat the model as *a* opinion with a published gap,
  not as the line.

## 4. Drop-in fragment for `data/analysis.json` (integration request)

The integrator owns `data/analysis.json`; this session does not edit it. The
block below is ready to splice into `day_three_guidance` (e.g. as
`"crosscheck_2e920ea8"`):

```json
{
  "label": "External book cross-check (BC.Game listing via EGamersWorld, read 2026-10-16T07:36:00Z)",
  "note": "Independent bookmaker lines for both day-3 deciders; agrees with the exchange and the VRS model on the favourite within 2-3 points. Arithmetic: de-vig of the displayed two-way decimals; reproduced in research/day3-2e920ea8/CROSSCHECK.md.",
  "fixtures": [
    {
      "hotspawn_id": "1080205",
      "label": "Aurora vs 9z",
      "book_line": [1.41, 2.84],
      "book_probabilities": [0.6682, 0.3318],
      "source_url": "https://egamersworld.com/counterstrike/event/thunderpick-world-championship-2026-5X5sFiL7H",
      "read_at": "2026-10-16T07:36:00Z"
    },
    {
      "hotspawn_id": "1081775",
      "label": "BetBoom vs Legacy",
      "book_line": [2.52, 1.5],
      "book_probabilities": [0.3731, 0.6269],
      "source_url": "https://egamersworld.com/counterstrike/event/thunderpick-world-championship-2026-5X5sFiL7H",
      "read_at": "2026-10-16T07:36:00Z"
    }
  ]
}
```

Sources for every claim in this file: EGamersWorld TWC event page (07:36Z read),
HLTV match pages 2399412 / 2399413 / 2399384 / 2399408 / 2399409 (via
`data/analysis.json`'s verified records), Polymarket markets 5733288 / 5763247
(dated receipts in `research/harvest-dedd2e34/market-ledger.json`). Strategy
paragraphs are analysis and say so.
