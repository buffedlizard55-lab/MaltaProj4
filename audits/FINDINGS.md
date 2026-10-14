# Independent verification audit · 14 October 2026

Owner: session `21bf0503`. This is a **historical audit**, not the live picks feed.
Implementation and deployment remain with the active integration session(s).

## Executive summary for integration

- Preserve all **88** CS2 records returned in Hotspawn's embedded state, but distinguish the **28 future/current records and 28 rendered cards** from **60 records with past dates still labeled scheduled**. The weekly header, filter count, and upcoming-card count are different measures; do not report 88 actionable picks.
- Four actionable cards have no detail permalink. Parse the embedded `ng-state` or the full cards, not just `View Match` anchors. Keep those rows even when their probability is unresolved.
- Source probabilities must never come from Hotspawn popularity or HLTV's fan voting widget. Retrieved bookmaker/exchange quotes and separately labeled model estimates are different kinds of evidence.
- At least one low-tier Polymarket market has a very wide spread, no recorded volume, and no last trade. Its midpoint must not become a confident 50.5% pick. The exact observation and source are below.
- Keep a conspicuous **All picks** link and a separate **Unresolved picks / Flagged for Review** link on the landing page, show last successful source refresh (not just build time), and display the unresolved count and source limitations there.

## Findings and official manual-review links

| ID | Finding checked | Evidence / official source | Required handling |
| --- | --- | --- | --- |
| A01 | Embedded state contains 88 CS2 records, all labeled `scheduled`; 60 scheduled dates precede observation, 28 do not. DOM contains 28 `.vs-card` elements. | [Hotspawn CS2 lobby](https://play.hotspawn.com/cs2-pickems); [preserved response](https://github.com/buffedlizard55-lab/MaltaProj4/blob/eba7790/data/diagnostics/hotspawn.html) | Retain full inventory; past-date status inconsistency belongs in review, not actionable picks. Past date alone does not verify match completion or winner. |
| A02 | Enjoy–B8 Academy, Banda chuya–6666, Ryvex–PCIFIC, mellren–Privateer have no detail permalink in the observed state. | [Official lobby](https://play.hotspawn.com/lobby); [row-level audit JSON](hotspawn-membership-2026-10-14.json) | Use lobby source link for these rows. Missing permalink must not drop a match or create a guessed URL. |
| A03 | Enjoy–B8 Academy is displayed as Oct 14 04:00 in retrieved text, but its source epoch is `1791964800000`, which converts to **08:00 UTC**. | [Official CS2 lobby](https://play.hotspawn.com/cs2-pickems) | Parse source epoch; do not label browser-local display time as UTC. Conversion is a derived value, not a separate official observation. |
| A04 | Hotspawn response headers have retrieval date `2026-10-14T04:42:38Z`, `Age: 7097`, and `X-Cache: HIT`. | [Response headers](https://github.com/buffedlizard55-lab/MaltaProj4/blob/eba7790/data/diagnostics/hotspawn.headers); [official source](https://play.hotspawn.com/cs2-pickems) | Distinguish retrieval age from upstream data age; refreshing a cached page does not make its contents newly generated. |
| A05 | Gothic–Lavked HLTV page shows 33.3% / 66.7% below “Pick a winner / Please login to vote”; betting panel retrieved here contains a Stake US casino promotion, not paired prices. | [HLTV match](https://www.hltv.org/matches/2399298/gothic-vs-lavked-cct-2026-europe-series-11) | Reject fan percentages and promo numbers as odds. HLTV is authoritative for its own statistics, not a bookmaker quote merely because its page contains numbers. |
| A06 | HLTV's Gothic–Lavked analysis labels Gothic unranked and Lavked #140, and notes KENSI and jakekeS each have fewer than five matches with the core. | [HLTV analytics](https://www.hltv.org/betting/analytics/2399298/gothic-vs-lavked-cct-2026-europe-series-11) | No invented rank for an unranked team. No automatic rank-to-probability percentage. Roster uncertainty must be surfaced if a documented model is used. |
| A07 | Stake's public CS2 page yields paired two-way match-winner decimal quotes; the fetched English URL redirected to German, which uses comma decimals. | [Official Stake CS2 page](https://stake.com/de/sports/esports/counter-strike) | Parse explicit two-way match markets, team order and localized odds. An observation is not a guarantee a scheduled runner can access that page. |
| A08 | The attempted Thunderpick `/esports/counter-strike-2` route redirects to 404. Its real CS2 route is `/esports/cs2-betting`, with American odds in the retrieved featured cards. | [Official Thunderpick CS2 page](https://thunderpick.io/esports/cs2-betting) | Do not confuse `+435` count of additional markets with a team's odds; require semantic market labels and both outcomes. |
| A09 | GG.bet returns “This internet site is not accepting visitors from your region.” Pinnacle esports-hub retrieval failed with HTTP 500. | [GG.bet](https://gg.bet/en/esports); [Pinnacle](https://www.pinnacle.com/en/esports-hub) | Log access failure, do not claim no betting markets exist; do not bypass region restrictions. Other valid Pinnacle public endpoints may behave differently. |
| A10 | Polymarket public market discovery is documented as unauthenticated; the official CS2 page includes Enjoy–B8 Academy and Gothic–Lavked. | [Official discovery docs](https://docs.polymarket.com/market-data/discover-markets); [official CS2 page](https://polymarket.com/esports/cs2) | Low tier does not by itself imply no featured-source market. Exhaust the ordinary route before falling back, then check HLTV followed by books. |
| A11 | `mellren vs Privateer Gaming` moneyline snapshot: outcomePrices 0.505/0.495, bestBid 0.07, bestAsk 0.94, liquidity 182.5393, volume null, lastTradePrice null; updatedAt `2026-10-14T04:27:30.024627Z`. | [Official event](https://polymarket.com/event/cs2-mellre-pg5-2026-10-16); [API](https://gamma-api.polymarket.com/events/slug/cs2-mellre-pg5-2026-10-16); [preserved API response](https://github.com/buffedlizard55-lab/MaltaProj4/blob/9627ef2/research/probe/cs2-events.txt) | 87 percentage-point spread and no recorded trade are not precise evidence of 50.5% strength. Mark weak market / unresolved until stronger evidence. Privateer vs Privateer Gaming identity also needs source verification. |
| A12 | Valve publishes regional standings and model source. The fit code explicitly returns -1 for missing team ratings; its default rating deviation is 75. | [Official repository](https://github.com/ValveSoftware/counter-strike_regional_standings); [fit.js](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/model/fit.js); [glicko.js](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/model/glicko.js) | Possible independent research-model input, NOT bookmaker odds. Require a dated snapshot, verified roster identity, explicit model assumptions and out-of-sample calibration. Do not replace missing ratings with 1500 or unranked with a guessed number. |

## Fallback acceptance requirements

1. Discover every official CS2 record, including no-permalink and low-tier records. Keep stable source IDs. Report discovery failure separately from zero matches.
2. Resolve the existing featured source first. Require correct sport, teams, UTC start/event identity, two-outcome **match winner** market, not map winner, handicap, tournament outright or another meeting between the same teams.
3. For still-unresolved matches, inspect HLTV's match/analytics/roster data, then public esportsbook lines. Log the attempted source and actual result per row; a generic source list is not evidence that a row was researched.
4. Prefer a current paired line from one source. Decimal no-vig normalization is `p(A) = (1 / dA) / ((1 / dA) + (1 / dB))`, `p(B) = 1 - p(A)`. This is **our derived market estimate**, not an officially guaranteed win probability. Do not splice the best A price from one book with B from another to claim a book's margin-free probability.
5. For exchanges, distinguish midpoint, last trade, bid and ask. Use quote age, spread, volume and available liquidity to reject weak or stale estimates. A newly updated event timestamp is not proof of a fresh quote or trade.
6. An own model is permitted only as a labeled research estimate using verified inputs, recorded formula/version, uncertainty and calibration limitations. HLTV ranking alone has no verified universal probability mapping. Do not fabricate 50/50 to fill missing data.
7. If no defensible estimate survives these gates: leave pick and probability null; show the row, sources attempted, reason, last attempt and retry status in **Unresolved picks** and count it in the summary.
8. Recheck every 4–8 hours (e.g. six-hour schedule), preserve the last successful dataset on outage, and prominently mark stale rows. Scheduled workflows can be delayed; this is not a real-time odds feed.

## Mobile / publishing acceptance checklist

These are requirements to test after integration, **not claims already passed**:

- At 320px, 375px, 390px and 768px, a visitor can reach all picks in one obvious tap; neither side's probability nor the selected team requires horizontal scrolling.
- Executive summary links to all picks, unresolved picks, methodology and source status; counts agree with the dataset.
- Clear source type, time zone and freshness; low confidence is not communicated by color alone.
- Semantic table headers or equivalent accessible row labels, keyboard focus styles, readable text and sufficiently large touch targets.
- Internal relative links resolve under `/MaltaProj4/`; no client calls to localhost, private API keys or required manual input.
- Validate every sourced row, exclude crowd votes, test reversed outcomes, aliases, ambiguous matches, no data, stale data, failed providers, invalid odds, 50/50 ties and canceled matches.
- Build/tests pass; PR is merged; Pages deployment is confirmed successful before claiming the site is live.

## Reproduction

`python -m unittest discover -s audits -p 'test_*.py' -v`

`python audits/hotspawn_audit.py /path/to/captured-hotspawn.html --observed-at 2026-10-14T04:42:38Z`

The JSON contains source facts and explicitly named deterministic UTC conversions only. It excludes popularity percentages, fabricated probabilities and guessed best-of formats. Its SHA-256 identifies the precise HTML audited. It is not a substitute for the six-hour refresh collector.
