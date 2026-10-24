# Resolving a pick for a match the featured tier cannot call — worked example (session e86697a6)

**Captured 2026-10-24 ~16:40Z from a normal internet egress (this sandbox reaches only
GitHub/PyPI/npm from bash; the pages below were read with the research browser).**

The brief for this session was: *"Look for information sources to guide pick selections
only for any matches that cannot be resolved in the same way as the featured picks. Try
HLTV, then try looking at esportsbooks and esports betting lines."*

The 2026-10-24T16:31Z live refresh contained exactly one such match.

## The row

| Field | Value | Source |
| --- | --- | --- |
| Hotspawn fixture | `1079200` Color vs ex-Zero Tenacity, NODWIN Clutch Series #13, BO3 | https://play.hotspawn.com/cs2-pickems |
| Start / lock | 2026-10-25T18:00:00Z / 17:54:00Z | Hotspawn fixtures API (retained in `research/harvest-e86697a6/snapshot.json`) |
| Featured exchange line | Polymarket 0.500 / 0.500, best bid 0.49 / ask 0.51, spread 0.02, liquidity $5,989.80, updated 16:24:39Z | https://gamma-api.polymarket.com/markets/6072812 |
| Why it had no pick | The two accepted prices are exactly even, so the market supplies **no direction** | `scripts/core.py::resolve` |

Before this session the board published that 50/50 with `pick: null`. That single row broke
42 unit contracts (a pick must be the higher probability; a row with numbers and no pick is
neither priced nor unresolved, so it appeared on no unresolved surface) and left the match
with no pick at all — measured in
`research/harvest-e86697a6/post-stage-unit.log` (run
[40111614698](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40111614698)).

## What the ladder found instead (official sources, read 2026-10-24)

| Step | Evidence | What it gives |
| --- | --- | --- |
| HLTV fixture identity | https://www.hltv.org/matches/2399115/color-vs-ex-zero-tenacity-nodwin-clutch-series-13 — same pair, NODWIN Clutch Series 13, Round of 16, BO3, 14:00 HLTV local time (= 18:00Z) | identity only |
| HLTV rankings on that page | Color `HLTV: Unranked`, `VRS: #73`; ex-Zero Tenacity `VRS: #92` | no HLTV world-ranking edge (Color is unranked, so `research_rank` cannot fire) |
| HLTV community vote on that page | 73.3% / 26.7% | **never used** — a fan vote is not a probability |
| Valve official global standings, 2026-10-05 | `#57 Color 1249 pts (cronuss, lattykk, oz1k, Patsi, reyoz)`; `#93 ex-Zero Tenacity 1066 pts (brutmonster, Cjoffo, Dragon, Kind0, VLDN)` — `data/vrs/standings_global_2026_10_05.md` | both clubs are in the official file, so our originated VRS line applies |
| EGamersWorld listing | https://egamersworld.com/counterstrike/match/Nk9F-Ov54e/color-vs-ex-zero-tenacity-rvwRf5V1F — same pair, 25.10.2026 18:00, BO3, NODWIN Clutch Series 13 | a dated two-way book listing (fallback tier, `bookmaker_fallback`) |

Arithmetic from the two official Valve point values (Valve's own `fit.js` expected-win
formula, Glicko RD 75, then Valve's published calibration slope 0.7986):

```
raw  = 1 / (1 + 10 ** (-G * (1249 - 1066) / 400)) = 0.73591
p    = 0.5 + 0.7986 * (raw - 0.5)               = 0.68840   (Color)
1-p                                             = 0.31160   (ex-Zero Tenacity)
```

So the match is pickable without inventing anything: **Color at 68.8%**, labelled as our
originated model line (`model_vrs`), with the even Polymarket quote retained as rejected
evidence in the ledger.

## Rule now implemented (session e86697a6)

An exactly even two-way line at **any** market tier carries no directional edge. Instead of
publishing a bare 50/50 with no pick, the quote is retained as *rejected evidence* (prices,
spread, observation time, source URL) and the row continues down the ladder:

`strict exchange -> HLTV identity/research -> Pinnacle -> wide exchange -> researched book listing -> Valve VRS model -> HLTV VRS mirror -> ranking / one-sided / recent-form research -> blank + limitation`

The same rule now applies to an exactly even researched book line and an exactly even model
estimate. A row is only published as blank when every rung above it fails, and then it is
listed with its limitation on the unresolved page and in the executive summary.

## Reachability measured at the same time

| Source | Result |
| --- | --- |
| HLTV match page | HTTP 200, content read (lineups, rankings, VRS points) |
| Valve global standings file | vendored at `data/vrs/standings_global_2026_10_05.md`, both clubs present |
| Polymarket Gamma API market | HTTP 200, prices/bid/ask/liquidity read |
| EGamersWorld listing | HTTP 200, same pair and start |
| HLTV community vote | present, deliberately not used as a probability |

No figure above is inferred: every number is quoted from the page named beside it.
