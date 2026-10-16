# Source attempts for the research-only rows — 16 October 2026

Session `ef0969b9`, external-line sourcing lane. Purpose: try the user's ordered
fallback (HLTV first, then esportsbooks / esports betting lines) for every open row
that still has **no** priced pick, and record the result — including negative results
— so the limitation shown on the site is backed by a dated attempt rather than an
assumption.

Rows in scope, read from the live `unresolved.html` at 07:27Z (build `693b6374`):

| Row | Fixture | Start (UTC) | Published state |
| --- | --- | --- | --- |
| 1081521 | ex-6666 vs Privateer — CCT Europe Challengers #8 | 18 Oct 13:45Z | research-only pick, no percentage |
| 1081522 | antidaun vs Phantom Academy — CCT Europe Challengers #8 | 18 Oct 13:45Z | research-only pick, one-sided ranking, no percentage |
| 1081526 | Infinite vs Insiders — DraculaN Season 7 | 19 Oct 09:00Z | research-only pick, one-sided ranking, no percentage |

## Attempts made in this session (all reads dated)

| Source | Query | Result |
| --- | --- | --- |
| **HLTV (first in the order)** | already applied by the pipeline and visible on each row: `hltv.org/matches/2399681`, `/2399682`, `/2399590` linked as "HLTV fixture & ranking" | Provides identity and ranking order only; HLTV publishes no numeric bookmaker pair, so this step cannot produce a percentage. The rows carry that evidence and say so. |
| **Polymarket (exchange)** | `public-search?q=Privateer` | Only **closed** history: "Privateer Gaming vs DimoniX Esports (BO1) — ESEA Advanced Europe Regular Season", market `5710564`, resolved 16 Oct 00:10Z. No open market for the 18 Oct CCT fixture. |
| **Polymarket (exchange)** | `public-search?q=Insiders` | Only **closed** history: "Insiders Esport vs EmberKoca (BO3) — CCT Europe Contenders #8", event `873777`, resolved 19 Aug 2026. No open market for the 19 Oct DraculaN fixture. |
| **Polymarket (exchange)** | `public-search?q=Infinite` (earlier this session) | Only **closed** history: "K27 vs Infinite (BO3) — StarLadder StarSeries European Qualifier Group A", event `734210`, resolved 23 Jul 2026. No open market for the 19 Oct DraculaN fixture. |
| **Pinnacle (esportsbook)** | `guest.api.arcadia.pinnacle.com/0.1/sports/12/matchups?withSpecials=false` | **HTTP 401, `"No authorization token provided"`** at ~07:45Z. The same endpoint answered earlier in this session (51 matchups, incl. CS2), so the guest feed is now token-gated for this collector. Access is not bypassed and no credentials are used; the row limitation stands. |
| **Thunderpick / GG.BET / Stake / Rivalry** | already attempted by the pipeline | Published on `review.html`: Thunderpick and Rivalry returned application shells, Stake returned HTTP 403, GG.BET restricted access; "HTTP 200 alone is not accepted as successful odds collection". Not re-attempted here to avoid re-hammering blocked endpoints. |

## What this means for these three rows (stated plainly)

* No usable two-sided external line was found for any of them from this collector
  today, so **no percentage can be published without inventing one**. The rows keep
  their labelled research-only pick and blank percentages, and they are listed on
  `unresolved.html` with the limitation printed on the row — which is exactly the
  behaviour the brief asks for ("if genuinely impossible, say so on the page").
* The site's executive summary already mirrors this: 42 open matches, 39 with a
  published probability, **3 research-only with no percentage, 0 with no pick**, and a
  link from the summary to the unresolved/limitations section
  (`index.html#unresolved-summary`).
* Because these fixtures start on 18–19 October, there is still time for a later
  refresh to pick up a listing if a market opens; nothing here should be read as
  "no line will ever exist".

## Reproduction

```sh
# exchange coverage for a team name (returns closed history first; a market only
# counts if the exact opponent pair and UTC start match)
https://gamma-api.polymarket.com/public-search?q=<exact team spelling>&cb=<stamp>

# bookmaker feed used by the pipeline (may be token-gated)
https://guest.api.arcadia.pinnacle.com/0.1/sports/12/matchups?withSpecials=false
```

No Hotspawn number is used anywhere in this file, and no fan-vote percentage is
converted into a probability.
