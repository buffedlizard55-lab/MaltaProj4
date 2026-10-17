# Day-5 odds verification and contrarian assessment — session e0fd5a32

Observed **2026-10-17 20:20 UTC**. Every number below was read from the linked page in this session;
no value is recalled or inferred. Machine-readable receipts: [`day5-lines.json`](day5-lines.json).

## 1. What actually happened on Day 4 (17 October)

| Fixture | Result | Maps | Source (read 20:16Z) |
| --- | --- | --- | --- |
| Semi-final 1: FURIA vs Aurora | **FURIA 2-0** | Dust2 13-8 (9:3; 4:5), Inferno 13-10 (8:4; 5:6); Nuke not played | <https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026> |
| Semi-final 2: Falcons vs BETBOOM | **BETBOOM 2-1** | Anubis 5-13 (Falcons), Dust2 16-14, Mirage 13-7 | <https://www.hltv.org/matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026> |

Veto, Semi-final 1: Aurora removed Ancient, FURIA removed Anubis, Aurora picked Dust2, FURIA picked
Inferno, Aurora removed Cache, FURIA removed Mirage, Nuke left over.

Veto, Semi-final 2: BETBOOM removed Inferno, Falcons removed Cache, BETBOOM picked Anubis, Falcons picked
Dust2, BETBOOM removed Ancient, Falcons removed Nuke, Mirage left over.

**The second upset of the event.** BETBOOM were the underdog against Falcons. The last retained
Polymarket quote for that semi-final (read 10:35Z, before the match) had Falcons at 72.5% and BETBOOM at
27.5% (`research/day4-85c33bf9/DAY4-LIVE-2026-10-17.md`, market 5787759). BETBOOM won the series 2-1.
The Day-1 9z–Aurora result was therefore not a one-off: two of the playoff series with a clear market
favourite went to the dog (9z over Aurora on 14 October, BETBOOM over Falcons on 17 October); Aurora then
won the rematch 2-0 on 16 October.

## 2. Day 5 fixtures (18 October)

| Time (UTC) | Fixture | Format | HLTV page |
| --- | --- | --- | --- |
| 11:30 | Aurora vs Falcons — third-place decider | Best of 3, LAN | <https://www.hltv.org/matches/2399416/aurora-vs-falcons-thunderpick-world-championship-2026> |
| 15:00 | FURIA vs BETBOOM — grand final | Best of 5, LAN | <https://www.hltv.org/matches/2399417/furia-vs-betboom-thunderpick-world-championship-2026> |

The UTC times come from the same pages' countdown clocks; the visible clock on the retrieved pages is
UTC-4 (07:30 and 11:00), which is consistent with the 17 October semi-final page showing 13:00 for the
17:00 UTC start.

Team identity on the day-5 pages is no longer TBA: the third-place page resolves to **Aurora vs Falcons**
(the losers of the two semi-finals) and the grand-final page resolves to **FURIA vs BETBOOM**. The
BETBOOM confirmation also follows from the second semi-final: FURIA had already qualified, and HLTV's
Aurora page labels match 2399416 as `aurora-vs-falcons-betboom-loser`.

## 3. Official bookmaker prices and our de-vig probabilities

Thunderpick, the event's title sponsor, is the only operator found with a two-way Day-5 match price.
Prices are American, read from the specific market pages at **20:20:54Z**.

| Fixture | Team | American | Decimal | Raw implied | De-vig probability | Our fair decimal |
| --- | --- | --- | --- | --- | --- | --- |
| Aurora–Falcons | Aurora | +170 | 2.7000 | 37.037% | **34.47%** | 2.901 |
| Aurora–Falcons | Falcons | −238 | 1.4202 | 70.414% | **65.53%** | 1.526 |
| FURIA–BETBOOM | FURIA | −286 | 1.3497 | 74.093% | **68.24%** | 1.465 |
| FURIA–BETBOOM | BETBOOM | +190 | 2.9000 | 34.483% | **31.76%** | 3.149 |

Source, third place: <https://thunderpick.io/esports/cs2-betting/thunderpick-world-championship-2026/11024/aurora-vs-falcons/2843582>
Source, final: <https://thunderpick.io/esports/cs2-betting/thunderpick-world-championship-2026/11024/furia-vs-bb-team/2843592>

Method (identical to the project's published rule): for decimal odds `d`, raw implied `q = 1/d`; the
de-vig probability is `q_i / (q_1 + q_2)`; fair decimal is `1 / p_i`. Overrounds are 7.451% and 8.576%.
The arithmetic is reproduced in `scripts/day5_e0fd5a32.py` and asserted in
`tests/test_day5_e0fd5a32.py`.

**Flagged display inconsistency.** The Thunderpick tournament card, re-read at 20:20Z, still showed
Aurora +150 / Falcons −208 (37.20% / 62.80% de-vig), while the specific market page showed
+170 / −238 in the same minute. Both pages belong to the same operator, so this is published as an
internal inconsistency and flagged for review, **not** as a confirmed line move. The market page is the
published quote because it is the specific market; the card price is retained as a cross-read.

**Model cross-check (not a market price).** Valve's 5 October standings, run through the project's
published VRS formula, give Aurora 36.37% / Falcons 63.63% and FURIA 72.89% / BETBOOM 27.11%. These
figures predate every TWC 2026 result and are shown only to demonstrate that the Thunderpick prices are
not wildly out of line; they are never published as probabilities.

## 4. Picks and the contrarian test

| Fixture | Pick | Probability | Is the dog playable? |
| --- | --- | --- | --- |
| Aurora–Falcons | **Falcons** | 65.53% | Aurora at 34.47% is the only defensible contrarian on the final day. |
| FURIA–BETBOOM | **FURIA** | 68.24% | BETBOOM at 31.76% is contrarian but not supported. |

Why Falcons: HLTV ranks Falcons #5 and Aurora #6, Falcons lead the head-to-head 1-0 in the last 30 days,
and both pages make Falcons the clear favourite.

Why Aurora is still the measured contrarian: HLTV's analytics summary gives Aurora the better recent
form ranking, and Falcons arrive off a semi-final loss in which they were the 72.5% favourite. Aurora
last played at 14:00Z and Falcons at 17:00Z, so Aurora had about **three** more hours of recovery before
the 11:30Z start and played two maps rather than three. Those are schedule and form facts, not a measured
fatigue effect. At +170 a top-6 team in a best-of-three is a reasonable small-stake differentiation play;
it is not a stronger pick than Falcons.

Why BETBOOM is not the same case: FURIA beat BETBOOM **2-0 in both meetings in the last 30 days**,
including 2-0 on 14 October at this event (HLTV analytics and match page). FURIA is ranked #4 versus
#14, has won 4 of its last 5, and the final is a **best-of-five**, which gives the deeper and
better-ranked side more room to absorb one bad map. BETBOOM's semi-final win was real and well earned,
but nothing in the head-to-head or the format supports 31.76% as an underestimate. Taking BETBOOM here
is the kind of contrarian pick the brief rules out: it fades evidence rather than a market inefficiency.

## 5. The "recent Aurora roster change" premise — checked, not supported

Aurora's current five is **XANTARES, woxic, Wicadia, Jimpphat, kyxsan**, coached by ash. HLTV's team
page (read 20:20Z) lists exactly the same five as Valve's 5 October roster file, and HLTV's announcement
dates kyxsan's move from Falcons to **8 July 2026**, with Jimpphat and ash joining the same day
(<https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan>). By 18 October that
five has played together for more than three months. **There is no onboarding or new-player factor to
price.** The premise appears to refer to the July rebuild and should not be used as a Day-5 upset
reason. The same check on the other Day-5 teams finds their active fives unchanged from the 5 October
Valve file: Falcons (karrigan, NiKo, TeSeS, m0NESY, kyousuke), FURIA (FalleN, yuurih, YEKINDAR,
KSCERATO, molodoy) and BETBOOM (Boombl4, zorte, S1ren, d1Ledez, Magnojez).

## 6. What this means for the Hotspawn leaderboard

The Day-5 TWC fixtures are **not Hotspawn board rows**. The CS2 pick'em page read at 20:18Z listed 81
board fixtures in its current filter, and the board's tournament filter names "Thunderpick World
Championship 2026: South American Series #1" but not the main event. Neither Day-5 fixture can be
submitted, so neither earns pick'em points or feeds a streak. The leaderboard-relevant picks remain the
81 board fixtures on the picks page; the Day-5 probabilities here are research/analysis picks.

That also changes the contrarian calculus. A pick'em entry gains nothing by fading the crowd on a match
that does not score. On the scoring board, the existing rule applies: follow the strongest available
price, and use an underdog only where the evidence supports it, because a broken streak costs the
consecutive-correct bonus. The official rules page describes that bonus
(<https://play.hotspawn.com/how-it-works>); its exact formula is not published. The same page says higher-tier
matches award more points, so on the scoring board the best value is the highest-tier row that can actually be
submitted; the two TWC semi-final rows were tier **s**. Spending a pick on a fixture that is not on the board earns
nothing.

## 7. Unresolved and limitations

| Item | Status | Why |
| --- | --- | --- |
| Second bookmaker cross-check for either Day-5 fixture | **Unresolved** | HLTV exposed no numeric line. Pinnacle's public matchups feed read at 20:10Z carried no TWC Day-5 fixture, and its league list does not name the event; Polymarket had no head-to-head Day-5 market at 20:22Z. Only Thunderpick exposed a two-way price. |
| Third-place price consistency | **Flagged** | Tournament card +150/−208 versus market page +170/−238 within the same minute. Published price is the market page. |
| Live price at lock | **Unresolved by design** | These are 20:20Z observations; the matches start 11:30Z and 15:00Z on 18 October. The site must expire them, not present them as live. |
| Hotspawn board coverage for Day-5 TWC | **Confirmed absent** | The main event is not in the pick'em tournament filter; no board row exists to pick. |
| Exact streak-bonus formula | **Unresolved** | The rules page states a bonus exists but does not publish the formula. |

## 8. Verification performed

- Both Day-4 match pages were opened and the score, map scores, halves and veto were read directly.
- Both Day-5 match pages were opened; teams, format and start were read directly.
- Both Thunderpick market pages were opened and the American prices were read directly; the tournament
  card was read as a cross-check.
- The de-vig and fair-odds values were recomputed from the American prices by
  `scripts/day5_e0fd5a32.py`; `tests/test_day5_e0fd5a32.py` asserts the published values.
- Aurora's rebuild dates were read from the HLTV announcement and the team page; the active five was
  compared with Valve's published roster file.
- Hotspawn's CS2 pick'em page was read to confirm the absence of the main event from the board.
- No Hotspawn crowd percentage is used as a probability anywhere in this document.
