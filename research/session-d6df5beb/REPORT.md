# Session d6df5beb — independent verification, 18 October 2026

Scope: line-by-line verification of the Thunderpick World Championship 2026 record
(Days 1–4), the Day-5 fixtures and prices, the Aurora roster premise, the Hotspawn
inventory and the pick coverage of every open board row. Everything below was read
by this session on 18 October 2026 between 00:38 and 00:55 UTC, except where a
historical source is explicitly named.

Machine-readable receipt: `research/session-d6df5beb/receipt-2026-10-18.json`
Reproduce: `python -m scripts.audit_d6df5beb` (216 checks) and
`python -m unittest tests.test_session_d6df5beb` (11 tests).

## 1. Verdict on the user's premises

| Premise | Verdict | Evidence |
| --- | --- | --- |
| 9z beat Aurora on Day 1 (the big upset) | **Confirmed** | 9z 2-0 Aurora, Inferno 13-11 and Nuke 13-1 — https://www.hltv.org/matches/2399384/9z-vs-aurora-thunderpick-world-championship-2026 |
| Aurora had a *recent* roster change that explains it | **Not supported** | The rebuild is dated 3–8 July 2026 (kyxsan in from Falcons on 8 July, Jimpphat and coach ash on 3 July), about 14 weeks before the event — https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan . The five in Malta are unchanged on the 18 October match page. |
| A roster-change or rest angle should drive an upset pick | **Partly** — rest only, and only for the third-place match | Aurora played 2 maps in the early semi-final; Falcons played 3 maps including a 16-14 overtime in the late one. Both play at 11:30Z. See §4. |
| Day-5 TWC matches are on the Hotspawn pick'em board | **No** | https://play.hotspawn.com/lobby at 00:50Z: 81 CS2 matches, 18 competitions, including “Thunderpick World Championship 2026: South American Series #1” (8) but **not** the main event. `data/latest.json` agrees (0 main-event rows). |

## 2. Every completed series, verified

Twelve series, 29 maps. Each row was read on its own HLTV match page (not only the
results list), and the audit checks that the map winners reproduce the series score.

| Day | Stage | Result | Maps |
| --- | --- | --- | --- |
| 1 (14 Oct) | Group A opener | **9z 2-0 Aurora** | Inferno 13-11, Nuke 13-1 |
| 1 | Group A opener | Falcons 2-0 Ninjas in Pyjamas | Ancient 16-13 (OT), Dust2 13-6 |
| 1 | Group B opener | Legacy 2-0 PARIVISION | Dust2 13-11, Mirage 16-14 (OT) |
| 1 | Group B opener | FURIA 2-0 BETBOOM | Ancient 13-10, Mirage 13-9 |
| 2 (15 Oct) | Group A winners' | Falcons 2-1 9z | Nuke 13-9, Mirage 8-13, Dust2 13-9 |
| 2 | Group A elimination | Aurora 2-0 Ninjas in Pyjamas | Cache 13-9, Dust2 13-7 |
| 2 | Group B winners' | FURIA 2-1 Legacy | Cache 10-13, Inferno 13-5, Mirage 13-8 |
| 2 | Group B elimination | BETBOOM 2-1 PARIVISION | Ancient 10-13, Anubis 13-4, Mirage 13-7 |
| 3 (16 Oct) | Group A decider | Aurora 2-0 9z | Cache 13-11, Inferno 13-4 |
| 3 | Group B decider | BETBOOM 2-1 Legacy | Nuke 16-13 (OT), Dust2 11-13, Mirage 13-11 |
| 4 (17 Oct) | Semi-final 1 | FURIA 2-0 Aurora | Dust2 13-8, Inferno 13-10 |
| 4 | Semi-final 2 | **BETBOOM 2-1 Falcons** | Anubis 5-13, Dust2 16-14 (OT), Mirage 13-7 |

Sources: the twelve match pages listed in the receipt (IDs 2399384–2399415), plus
the event results page https://www.hltv.org/results?event=8932.

Corroboration of the Day-1 narrative: HLTV's report calls Aurora “the fifth-ranked
team in the VRS” going in, gives luchov 1.61 rating / +6.61% / 97.4 ADR / 86.8% KAST,
and records that 9z earned 62 VRS points (1,571, third in the Americas)
(https://www.hltv.org/news/45718/9z-beat-aurora-2-0-to-kick-off-twc-2026).

The event was noisy, not inverted: both opening-match losers (Aurora and BETBOOM)
reached the semi-finals, and the only repeat pairing split 1-1 (9z won Day 1, Aurora
won the Day-3 decider 2-0). A single upset is not a template for a strategy.

## 3. Day 5: fixtures and prices

| Match | Start (UTC) | Format | Source |
| --- | --- | --- | --- |
| Aurora vs Falcons — third place | **2026-10-18 11:30** | Best of 3 (LAN) | https://www.hltv.org/matches/2399416/aurora-vs-falcons-thunderpick-world-championship-2026 |
| FURIA vs BETBOOM — grand final | **2026-10-18 15:00** | Best of 5 (LAN) | https://www.hltv.org/matches/2399417/furia-vs-betboom-thunderpick-world-championship-2026 |

Both pages state the format explicitly today (“Best of 3 (LAN) * 3rd place decider”,
“Best of 5 (LAN) * Grand final”), so the earlier parser null is closed. HLTV renders
clocks at UTC−4 for this event (07:30 / 11:00 on the page); the UTC values above come
from the machine-readable start and are confirmed independently by Polymarket's
`gameStartTime` fields.

### 3.1 Two independent venues now exist

This is the material change since the 17 October publication. Both Sunday matches
now have **live Polymarket moneyline markets** with strict-gate quality, where the
site previously recorded “no Sunday line” and “one bookmaker is not consensus”.

| Venue | Third place | Grand final |
| --- | --- | --- |
| **Polymarket** (official Gamma API) | market `5837604`: Aurora 0.395 / Falcons 0.605 | market `5837622`: FURIA 0.705 / BetBoom 0.295 |
| best bid / ask, spread | 0.39 / 0.40, 1 point | 0.70 / 0.71, 1 point |
| liquidity / volume | $145,280.65 / $40,449.90 | $143,551.22 / $6,149.63 |
| market `updatedAt` | 2026-10-18T00:45:16Z | 2026-10-18T00:49:15Z |
| **Thunderpick** (match page) | Aurora +140 / Falcons −200 | FURIA −286 / BETBOOM +190 |
| de-vig (proportional) | Aurora 38.46% / Falcons 61.54% | FURIA 68.24% / BETBOOM 31.76% |
| overround | 8.33% | 8.58% |
| **Venue gap** | 1.04 points (Falcons) | 2.26 points (FURIA) |

Sources:
https://gamma-api.polymarket.com/markets?slug=cs2-aur1-fal2-2026-10-18 ·
https://gamma-api.polymarket.com/markets?slug=cs2-furia-bb3-2026-10-18 ·
https://thunderpick.io/esports/cs2-betting/thunderpick-world-championship-2026/11024/aurora-vs-falcons/2843582 ·
https://thunderpick.io/esports/cs2-betting/thunderpick-world-championship-2026/11024/furia-vs-bb-team/2843592

Both Polymarket markets clear the project's own strict exchange gate — prices sum to
1.000, 1-point tick, liquidity far above the $100 floor, open and accepting orders —
so these are exchange-tier quotes, not fallbacks. The two venues agree on both
favourites, which is the useful signal; their small disagreement (1–2 points) is
published rather than averaged into a new number.

**Third-place line move (sourced):** the same Thunderpick market read Aurora +170 /
Falcons −238 at 20:20:54Z on 17 October and Aurora +140 / Falcons −200 at 00:41Z on
18 October — Aurora's raw implied price shortened from 37.04% to 41.67%. The grand
final price was unchanged over the same window. At today's read the tournament card
and the market page agree (+140/−200), so the earlier card-versus-page display
discrepancy is resolved in this snapshot.

## 4. Contrarian but not stupid: what the data supports for Day 5

Default (market-consistent) picks: **Falcons** (60.5–61.5%) and **FURIA**
(68.2–70.5%). Both are the higher-probability side on two venues and maximise
expected base points where each correct pick is worth the same award.

The only **priced differentiation** with a sourced reason is **Aurora** in the
third-place match (38.5–39.5%, inside the project's 20–40% band):

- Aurora played the earlier semi-final and only two maps (14:00Z start, over before
  16:00Z). Falcons played the later semi-final and three maps including a 16-14
  overtime (17:00Z start, finished around 19:30Z). Both play at 11:30Z, so Aurora
  have roughly four more hours of recovery and one fewer map. This is schedule
  arithmetic from the published results, **not** a measured fatigue effect.
- The market has already moved toward Aurora (+170 → +140) since last night, i.e.
  part of that read is priced.
- Against it: Falcons are ranked above Aurora on both HLTV (#5 vs #6) and VRS
  (#5 vs #6), and won the only meeting in the past 30 days (HLTV analytics page).

**BETBOOM is not the smart contrarian.** FURIA have played 7 maps to BETBOOM's 11,
FURIA won the in-event meeting 2-0, and they are 2-0 head-to-head in the last 30
days (HLTV analytics). BETBOOM's three straight 2-1 wins are real, but the map-load
argument runs against them, so a 29.5–31.8% swing has no structural edge — it is
variance, not value. If taken at all it should be a single capped swing, per the
project's own rule 5.

**Leaderboard reality check.** Neither Sunday match is a Hotspawn board row
(§1), so neither earns pick'em points. For climbing the leaderboard, the leverage is
in the **17 open board rows**, not in these two research cards: 13 are priced (6
strict exchange, 1 wide/low-confidence exchange, 6 originated VRS model lines) and 4
carry a research-only pick with a blank percentage and a documented reason. Every
open row was verified to have a pick, and every priced row's two-way percentages sum
to 1.0.

Because Hotspawn awards a fixed number of points for a correct pick (tier-weighted,
never crowd-weighted — official rules) and does not publish the streak formula or
current pick shares, no optimal rank-climbing calculation can be honest here. What
can be said: taking the higher-probability side maximises expected points, and a
contrarian swing trades expected points for differentiation.

## 5. Irregularities and flags for review

1. **Superseded limitation text (data, needs update).** `data/analysis.json →
   day_five_guidance.unpriced` and `.unverified` still say the automated receipts
   “have no Sunday line” and that a second book does not exist. That was true at
   20:16Z on 17 October; it is false as of 00:45Z on 18 October (two live Polymarket
   markets). The published cards also still carry the 20:20:54Z Thunderpick prices
   (+170/−238, 65.53%) whose quote block expires at 04:20:54Z, while the operator
   now shows +140/−200 (61.54%). Session `a54996e1` is already re-reading the
   Thunderpick side; the Polymarket side is this session's finding.
2. **Two Day-1 map scores were left blank** (“map scores were not collected”):
   Legacy–PARIVISION (Dust2 13-11, Mirage 16-14) and FURIA–BETBOOM (Ancient 13-10,
   Mirage 13-9). Both are now verified on the HLTV match pages and can be filled
   without inference.
3. **Provenance upgrade available.** The Day-1 Falcons–NiP map scores were sourced
   from a betting preview; the HLTV match page shows the same scores (Ancient 16-13
   in overtime, Dust2 13-6), so the caveat can be removed.
4. **VRS point totals not re-read.** The ranks are verified on the match pages
   (Aurora HLTV/VRS #6, Falcons #5, BETBOOM HLTV #14 / VRS #9, FURIA HLTV #4), but
   the numeric point totals quoted in earlier notes (e.g. “Falcons 1858”, “FURIA
   1858”) were not visible on the pages read today and are not repeated here.
   Identical totals for two different teams would be worth a second look.
5. **Unlabelled “Live” odds chips.** The Thunderpick tournament page shows “Live
   +315” and “Live +483” beside the two fixtures. They are not labelled with a
   market and are not used anywhere in this audit.
6. **Clock offset.** HLTV displays 07:30 / 11:00 (UTC−4) for these fixtures; a naïve
   conversion would misdate the picks by four hours. The site's UTC-only storage is
   correct and is re-confirmed here.
7. **Secondary-source claims kept as secondary.** Aurora's “third-place run” at ESL
   Pro League Season 24 is HLTV's own wording; the head-to-head list shows a 0-2
   semi-final loss to Spirit, which is consistent with a third-place match but the
   third-place match itself was not read. It is not load-bearing for any pick.
8. **No organizer confirmation.** All results and schedule facts are from HLTV match
   pages; the tournament organizer's own confirmation was not collected. HLTV is a
   specialist secondary source and is labelled as such across the site.

## 6. What this session changed

- Added this report and the dated receipt (12 series, 2 fixtures, 2 venues, 29 maps).
- Added `scripts/audit_d6df5beb.py`: 216 deterministic checks over the record, the
  venue gate, the de-vig arithmetic, the published data files and the rendered pages
  (0 failures at 01:00Z on 18 October).
- Added `tests/test_session_d6df5beb.py`: 11 tests that fail if a published result,
  a price, a gate, a pick or a Day-5 anchor drifts.
- Did **not** edit `data/analysis.json`, `data/latest.json`, `scripts/build.py`,
  `site/**` or the generated pages: those are claimed by the active session
  `a54996e1`. The four data improvements in §5 are logged as integration requests in
  `COORDINATION.md` and will be applied by this session during final integration if
  they are not already in place.

## 7. Limitations

- Prices are dated observations at 00:41–00:49 UTC, not live quotes at 11:30Z/15:00Z.
- Polymarket prices are the venue's own two-sided quote (they sum to exactly 1.000),
  so no de-vig is applied to them; the Thunderpick de-vig is this project's own
  proportional calculation on the operator's raw American prices.
- Single capture per venue. No order-book depth beyond best bid/ask was read.
- No crowd pick shares, personal leaderboard position or streak-bonus formula is
  available, so no leaderboard-optimality claim is made.
- The main TWC event's absence from the Hotspawn board is a dated observation, not a
  permanent claim; the scheduled refresh re-checks the inventory.

## 8. Live-site verification (addendum, 01:15–01:20 UTC)

The published site is built from `main` revision `3027f78` but refreshes its sources
during the deployment run, so it is **newer than the committed data file**:

- `https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json` →
  `revision 3027f782…`, `built_at 2026-10-18T00:28:29Z`,
  `snapshot_generated_at 2026-10-18T00:28:29Z`, `rows 98`.
- The live executive summary states: **34 open fixtures, 29 with probabilities
  (17 market, 12 model), 5 labelled research-only, 0 with no supported pick**, and
  the arithmetic is internally consistent (17 + 12 + 5 = 34).
- Mobile discoverability is present as described: a bottom bar (Overview, Picks,
  Needs pick, Matches, TWC analysis, Review, Sources), a "Find your picks in 2 taps"
  block, and per-match cards with the pick on top. Locally, the committed build
  passes 32 viewport/accessibility scans at 320/390/768/1440 px with zero overflow
  and zero WCAG violations, plus seven board-expiry and four research-quote boundary
  scenarios. That is the strongest available evidence for phone readability; it was
  not re-run against the live host.

**Finding (material): the live final-day cards still say a second venue does not
exist.** The published analysis page reads “One dated sportsbook line; no independent
second-book confirmation … expires at 04:20:54 UTC” for both Sunday matches. The
Polymarket markets were **created at 2026-10-17T20:55Z** — before the 00:28Z
deployment — and were trading with $143k–$145k of liquidity by 00:45Z. So the
limitation text is not merely about an expired quote: a second, exchange-tier venue
was already available when that page was built. The exact Polymarket prices at
00:28Z were not captured by this session (first verified stamp 00:45:16Z), so the
claim to make is “a second venue existed and now quotes these prices”, not “the
earlier page misstated a number”.

This is logged as an integration request for sessions `a54996e1` (Thunderpick
re-read) and `f659a6e2` (Polymarket capture), which are both active on Day-5 files.

## 9. Coordination note

Three sessions are concurrently active on the final day: `a54996e1` (claim 00:48Z;
Thunderpick re-read and integration), `f659a6e2` (claim 00:55Z; Polymarket Day-5
capture, `data/analysis.json` Day-5 keys, build/site and integration) and this one
(`d6df5beb`, 00:51Z; independent verification, session-unique files only). Their
scopes overlap each other on `data/analysis.json`, `scripts/build.py`, `site/**`,
root pages and final integration. This session does not edit any of those files
while a claim is active; it records the overlap here and in `COORDINATION.md` and
will verify (and, if needed, complete) the integration after one of them merges.
