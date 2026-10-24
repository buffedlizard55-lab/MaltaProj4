# Hotspawn coverage and verification summary

- Snapshot generated: `2026-10-24T16:28:44.690826Z`
- Fixture evidence observed: `2026-10-24T16:25:13.759973Z`
- Snapshot SHA-256: `3f33d2b2f8ba8b636988cbebe9a995c659501029f0f07ff2e08a256f1ec3cadf`
- Three-view coverage flag: **verified**; counts: `{"api": 83, "page": 83, "lobby": 83, "retained": 83}`
- Fixtures: **83**; open: **22**; with a pick: **21**; with a probability: **22**; fully resolved: **21**
- Research-only picks without a percentage: **0**; open rows without a pick: **1**
- Open-row methods: `{"bookmaker_fallback": 3, "exchange": 15, "exchange_wide": 1, "model_vrs": 2, "model_vrs_mirror": 1}`
- Added vs previous: `none`; removed: `['1079193', '1079195', '1079658', '1079659', '1079660', '1081152', '1081153', '1083120', '1083121']`
- Independent + additional integrity failures: **0**

Hotspawn is used only for fixture identity, schedule and lock state. It is not a probability source. Blank values are not replaced with guesses.

## Changed fixture facts vs the previous committed snapshot

- None.

## Open-row gaps and limitations

### 1079200 — Color vs ex-Zero Tenacity

- Start: `2026-10-25T18:00:00Z`; pick: `None`; probability: `50.0% / 50.0%`; method: `exchange`
- Limitation: Equal verified prices; no directional edge.
- Fixture: [Hotspawn](https://www.hotspawn.com/matches/color-vs-ex-zero-tenacity-nodwin-clutch-series-13-1079200); evidence: [source](https://gamma-api.polymarket.com/markets/6072812), [source](https://polymarket.com/event/cs2-color-zerote-2026-10-25)
- Source attempts:
  - Polymarket: resolved — Exact pair and UTC start; two-way series winner validated. (https://gamma-api.polymarket.com/markets/6072812)
