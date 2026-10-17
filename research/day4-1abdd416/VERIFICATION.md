# Day-4 semi-final picks, day-1/2/3 re-verification — session 1abdd416

Written 2026-10-16/17 (UTC). Scope: Thunderpick World Championship 2026 (Malta, 14–18 Oct),
days 1–3 results and the day-4 semi-finals, plus the 6666/ex-6666 identity bridge that prices
one previously unpriced Hotspawn row.

Method: every published number below is either (a) read from the linked primary source in this
session, (b) recomputed by `scripts/vrs.py` from Valve's official standings file, or (c) taken
from a raw response committed under `research/harvest-1abdd416/` and re-checked here. Values that
could not be read stay blank. The authoring sandbox reaches GitHub and package registries only, so
the live refresh and the raw captures were produced by
`.github/workflows/harvest-1abdd416.yml` (run
[38983606403](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38983606403), success,
57 s) on branch `arena/1abdd416-maltaproj4`; this session read HLTV and Polymarket through the
tooling's page reader, which is research retrieval, not publishing input.

---

## 1. Day 1, day 2 and day 3 — what changed since the published review

The event record read this session: <https://www.hltv.org/results?event=8932>.

| Day | Series | Result | Source read here |
| --- | --- | --- | --- |
| 1 (14 Oct) | 9z vs Aurora | 9z 2-0 Aurora (the upset) | results page; detail re-used from HLTV news 45718 |
| 1 | Falcons vs NIP, Legacy vs PARIVISION, FURIA vs BETBOOM | all four openers swept | results page |
| 2 (15 Oct) | Aurora 2-0 NIP, Falcons 2-1 9z, BETBOOM 2-1 PARIVISION, FURIA 2-1 Legacy | winners' matches both went the distance | results page |
| 3 (16 Oct) | **Aurora 2-0 9z** (Group A decider) | Cache 13-11, Inferno 13-4 | [2399412](https://www.hltv.org/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026) |
| 3 | **BETBOOM 2-1 Legacy** (Group B decider) | Nuke 16-13 (OT), Dust2 11-13, Mirage 13-11 | [2399413](https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026) |

The Group B decider was still live at 1-1 when session 9a81b26f wrote the day-3 block and was
recorded as final by session 1068802c later the same evening. This session re-read the match page:
series 2-1 to BETBOOM, Nuke 16-13 in overtime (halves 4:8; 8:4; 4:1 in OT), Dust2 13-11 to Legacy,
Mirage 13-11 to BETBOOM (7:5; 6:6), veto *BETBOOM removed Inferno, Legacy removed Anubis, BETBOOM
picked Nuke, Legacy picked Dust2, BETBOOM removed Cache, Legacy removed Ancient, Mirage left over*.
The half scores were added to the published row; the published row's own detail, source links and
flag were kept.

The day-one upset (the user's original question) is unchanged and stays as published: 9z beat
Aurora 2-0, HLTV's report credits luchov with a 1.61 rating, +6.61% swing and 97.4 ADR
([news 45718](https://www.hltv.org/news/45718/9z-beat-aurora-2-0-to-kick-off-twc-2026)). Aurora's
roster premise is also unchanged: the last transfer HLTV dates is 8 July 2026
([news 45082](https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan)), so
there is no day-4 onboarding story to trade on.

## 2. Day 4 (17 October): both semi-finals, priced three ways

Schedule and clocks — <https://www.hltv.org/events/8932/matches>:

| Slot | Fixture | HLTV | Machine start (UTC) | Format |
| --- | --- | --- | --- | --- |
| Semi-final 1 | FURIA vs Aurora | [2399414](https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026) | 2026-10-17T14:00:00Z | best of 3, LAN |
| Semi-final 2 | Falcons vs BETBOOM | [2399415](https://www.hltv.org/matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026) | 2026-10-17T17:00:00Z | best of 3, LAN |
| Third place | no teams yet | 2399416 | 2026-10-18T11:30:00Z | — |
| Grand final | no teams yet | 2399417 | 2026-10-18T15:00:00Z | best of 5 |

HLTV displays clocks in the reader's timezone (UTC-4 for this event). Only the machine
`start_utc` values are used, and both agree with Polymarket's own `gameStartTime` fields.

### 2.1 Exchange line (Polymarket official API, captured 2026-10-16T23:51:16Z)

| Market | Outcome prices | Bid/ask | Spread | Liquidity | Start |
| --- | --- | --- | --- | --- | --- |
| [5778024](https://gamma-api.polymarket.com/markets/5778024) FURIA vs Aurora | 0.525 / 0.475 | 0.52 / 0.53 | 1 pt | $158,627.63 | 2026-10-17 14:00+00 |
| [5787759](https://gamma-api.polymarket.com/markets/5787759) Falcons vs BETBOOM | 0.795 / 0.205 | 0.79 / 0.80 | 1 pt | $60,452.33 | 2026-10-17 17:00+00 |

Both markets report `acceptingOrders: true`. `5787759` is the event's series moneyline inside
event [1201748](https://gamma-api.polymarket.com/events/1201748); its Map 1 Winner market
(`5787757`, 0.68/0.32) is not used as a series price. The 19:35 read published earlier by
session 621776e4 (52/48 on 5778024) is superseded by this capture, and the card says so by
quoting the capture timestamp.

### 2.2 Sharp-bookmaker cross-check (Pinnacle guest esports feed, same capture)

| Matchup | League / cutoff | Period-0 moneyline | Decimal | Overround | De-margined |
| --- | --- | --- | --- | --- | --- |
| 1638536356 FURIA (home) vs Aurora | CS2 - TP World Championship, 2026-10-17T14:00:00Z | -125 / +103 | 1.80 / 2.03 | 4.8% | FURIA 53.0% / Aurora 47.0% |
| 1638595724 Falcons (home) vs BB Team | CS2 - TP World Championship, 2026-10-17T17:00:00Z | -389 / +298 | 1.257 / 3.98 | 4.7% | Falcons 76.0% / BB Team 24.0% |

Conversion and de-margining are the project's published method (`q = 1/d`, `p = q/Σq`). Pinnacle
labels the second fixture's away side "BB Team"; the identity register maps that to BetBoom from
the organisation's own site. Matchups are matched by exact league, participants and UTC cutoff
because "FURIA" and "9z" also appear in Pinnacle's other sports. Period-1 and period-2 moneylines
on these matchups are map markets and are never quoted as the series line.

### 2.3 Our originated line (Valve standings, 2026-10-05, commit eec4853)

| Fixture | Points (both sides) | Model | Fair decimal |
| --- | --- | --- | --- |
| FURIA vs Aurora | 1829 vs 1716 | FURIA 62.2% / Aurora 37.8% | 1.61 / 2.65 |
| Falcons vs BETBOOM | 1843 vs 1596 | Falcons 73.9% / BETBOOM 26.1% | 1.35 / 3.83 |

The model is context beside the market, never a replacement: the standings predate this week, and
both cards print the market first.

### 2.4 Picks

| Fixture | Pick | Why | Contrarian side |
| --- | --- | --- | --- |
| FURIA vs Aurora | **FURIA** | both market lines (52.5% exchange, 53.0% de-margined Pinnacle) make FURIA the favourite; the model is wider at 62.2% | Aurora at 47-48%, a coin flip with a sourced case (2-0 over NIP, 2-0 over 9z in the decider, 1-1 head-to-head in the last 30 days) |
| Falcons vs BETBOOM | **Falcons** | every source agrees on direction (79.5% exchange, 76.0% Pinnacle, 73.9% model) | BETBOOM at 20-24%: the only underdog argument is the schedule, and the market has to be wrong for it to pay |

Neither fixture is on Hotspawn's CS2 feed (83 rows in the 23:52Z harvest, none in the main TWC
event), so these are research guidance with no tier or points value.

## 3. The 6666 / ex-6666 identity bridge (one previously unpriced row)

Row 1081521 (ex-6666 vs Privateer, CCT Europe 2026 Challengers #8, 2026-10-18T13:45Z) had a
research-only pick and no probability because the VRS model returned
`ex-6666: not listed in the Valve global standings`.

- Valve's standings file lists **two** rows labelled `6666`: standing #127, 923.2 points, roster
  `amster, dENZY, kL1o, rendysky, skcH`
  ([detail file](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0127--6666--amster-denzy-kl1o-rendysky-skch.md))
  and standing #368, 424.5 points, roster `auth0ri, m4d4ra, rickangel, skcH`.
- HLTV's fixture page for that match shows the team labelled `ex-6666` with
  `skcH, kL1o, amster, rendysky, stefienson`
  ([2399681](https://www.hltv.org/matches/2399681/ex-6666-vs-privateer-cct-2026-challengers-europe-series-8)).
- Overlap with #127 is **4 players**; with #368 it is **1**. The overlap therefore selects exactly
  one row, and `vrs.identify` still refuses the label when the overlap or the uniqueness test fails
  (covered by `tests/test_day4_1abdd416.py::SixSixIdentityTests::test_a_different_roster_does_not_bridge`).

Registered in `data/identities.json` as canonical `6666` with names `["6666", "ex-6666"]`, with the
Valve detail file and the HLTV fixture as its two source links and the roster rule stated in the
entry's `basis`. Effect, replayed from the frozen harvest: row 1081521 flips to a `model_vrs` line
(ex-6666 78.2% / Privateer 21.8%, standings [127, 271], points [923, 608]) while the other three
unpriced rows keep their research-only picks. The alias changes no other fixture — the label also
appears on three closed June rows, which no pricing path touches.
The roster rule cited is Valve's own (`model/team.js`, `TEAM_OVERLAP_TO_SHARE_ROSTER = 3`); the
model re-checks it on every run rather than trusting the register.

## 4. Irregularities found and what was done

1. **The day-4 date label said "Friday 17 October 2026".** 17 October 2026 is a Saturday (the site's
   own board header for 16 October reads Friday). Corrected to "Day 4 · Saturday 17 October 2026".
2. **The published caveat list still described the Group B decider as unresolved** after the same
   session's own results update had recorded it as final. Rewritten for the 23:52Z state; the
   superseded caveats are replaced rather than left to contradict the results table.
3. **A stale second-hand Inferno caveat** ("published as 13-4 by dust2.com.br and EGamersWorld")
   survived the day-3 update in the points list. The HLTV match page carries 13-4 (9:3; 4:1), so the
   sentence now cites the match page and the caveat is closed.
4. **Source divergence, published not smoothed:** HLTV's own match page calls Aurora the bookmaker
   favourite with the better form ranking, while the exchange (52.5%) and Pinnacle (53.0%
   de-margined) both price FURIA. Separately, HLTV's live page shows VRS #6 FURIA / VRS #5 Aurora
   while Valve's file has FURIA #7 / Aurora #9. Both readings are on the page; the market line
   governs the pick.
5. **HLTV's odds table is empty in the capture** (both semi-final pages return no numeric bookmaker
   rows). Recorded as a retrieval limitation, not as "no odds exist".
6. **Pinnacle is a single book.** Its de-margined line is published as one sharp cross-check, not a
   consensus; the exchange remains the primary line.

## 5. Board coverage at the same capture

`research/harvest-1abdd416/ledger.json`: 83 rows, 21 open, 17 with a published probability, 4
open rows with a research-only pick and no percentage, **0 open rows with no pick at all**
(`rows_open_no_pick: []`). The three rows that remain unpriced after this session's alias each name
a team the official standings do not list (`antidaun`, `Morningstar`, `WXM`) and are listed, with
their per-source attempts, in the executive summary's limitations section.
