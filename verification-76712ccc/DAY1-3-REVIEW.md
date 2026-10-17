# Independent review of the published Thunderpick World Championship 2026 day-1 to day-3 record

Session 76712ccc, written 2026-10-17 (UTC). Every row below was read out of a raw HLTV match page
retained in `research/harvest-76712ccc/` by `verification-76712ccc/parse_twc_results.py`; the per-page
SHA-256 is in `verification-76712ccc/TWC-RESULTS.json` and reproduced in `TWC-RESULTS.md`. Where a
claim in the published board (`data/analysis.json` at the merge base `dc6a802`) is checked against
those captures, the check is stated as pass or flag.

## 1. Verified results (all four group days read from the retained captures)

| Day | Series | Maps (from the retained page) | Capture | Match page |
| --- | --- | --- | --- | --- |
| 1 | 9z 2–0 Aurora | Inferno 13–11, Nuke 13–1 | `a181a303…` | [2399384](https://www.hltv.org/matches/2399384/9z-vs-aurora-thunderpick-world-championship-2026) |
| 1 | Falcons 2–0 Ninjas in Pyjamas | Ancient 16–13, Dust2 13–6 | `847327aa…` | [2399385](https://www.hltv.org/matches/2399385/falcons-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026) |
| 1 | Legacy 2–0 PARIVISION | Dust2 13–11, Mirage 16–14 | `c2efc593…` | [2399386](https://www.hltv.org/matches/2399386/legacy-vs-parivision-thunderpick-world-championship-2026) |
| 1 | FURIA 2–0 BETBOOM | Ancient 13–10, Mirage 13–9 | `28b7fec2…` | [2399387](https://www.hltv.org/matches/2399387/furia-vs-betboom-thunderpick-world-championship-2026) |
| 2 | Aurora 2–0 Ninjas in Pyjamas | Cache 13–9, Dust2 13–7 | `2a83ccd9…` | [2399408](https://www.hltv.org/matches/2399408/aurora-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026) |
| 2 | Falcons 2–1 9z | Nuke 9z 9–13 Falcons, Mirage 9z 13–8 Falcons, Dust2 9z 9–13 Falcons | `bb3a827f…` | [2399409](https://www.hltv.org/matches/2399409/9z-vs-falcons-thunderpick-world-championship-2026) |
| 2 | BETBOOM 2–1 PARIVISION | Ancient PARIVISION 13–10 BETBOOM, Anubis PARIVISION 4–13 BETBOOM, Mirage PARIVISION 7–13 BETBOOM | `c082465c…` | [2399410](https://www.hltv.org/matches/2399410/parivision-vs-betboom-thunderpick-world-championship-2026) |
| 2 | FURIA 2–1 Legacy | Cache Legacy 13–10 FURIA, Inferno Legacy 5–13 FURIA, Mirage Legacy 8–13 FURIA | `0b02a8df…` | [2399411](https://www.hltv.org/matches/2399411/legacy-vs-furia-thunderpick-world-championship-2026) |
| 3 | Aurora 2–0 9z | Cache 13–11, Inferno 13–4, Mirage not played | `c20c67e3…` | [2399412](https://www.hltv.org/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026) |
| 3 | BETBOOM 2–1 Legacy | Nuke BETBOOM 16–13 Legacy, Dust2 BETBOOM 11–13 Legacy, Mirage BETBOOM 13–11 Legacy | `4e820a00…` | [2399413](https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026) |

Statements in the published day-1/day-2/day-3 blocks that these captures **confirm**: the four sweeps on
day one; Aurora answering with a 2–0 over Ninjas in Pyjamas on day two; 9z taking the map Falcons picked
(Mirage 13–8) and pushing the winners' match to a decider; FURIA winning the Legacy series 2–1; three of the
four day-two series going the full three maps; Aurora's 2–0 in the group-A decider with Inferno 13–4.

## 2. Flags (follow-ups, none of them blocking a merge)

1. **Day-4 date label.** `data/analysis.json` (`day_four_guidance.date`, merge base `dc6a802`) reads
   "Day 4 · Friday 17 October 2026". 17 October 2026 is a Saturday; HLTV's own card for the semi-finals is
   dated `17th Oct 2026` ([HLTV 2399415](https://www.hltv.org/matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026)).
   Open PR #50 by session 1abdd416 says it fixes this; verify on the rendered page after that merge.
2. **Group-B decider published as unresolved.** The same block's `unverified` list states that HLTV's event
   results did not list the BETBOOM–Legacy decider at 20:05 UTC on 16 October and that a parallel read found
   it live at 1–1. The retained capture taken by this session (`4e820a00…`) carries the final page:
   **BETBOOM 2–1 Legacy** (Nuke 16–13, Dust2 11–13, Mirage 13–11), so semi-final 2 is
   **Falcons vs BETBOOM**, not a conditional. Any remaining "if Legacy take the decider" wording is stale.
3. **HLTV's live VRS differs from the dated official file our model uses.** HLTV's team pages read
   FURIA #6 (AM#1), Aurora #5, Falcons #4, while Valve's published file of 2026-10-05 has FURIA #7,
   Aurora #9, Falcons #6 ([FURIA](https://www.hltv.org/team/8297/furia),
   [Aurora](https://www.hltv.org/team/11861/aurora), [Falcons](https://www.hltv.org/team/11283/falcons),
   [Valve file](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/live/2026/standings_global_2026_10_05.md)).
   The model keeps using the dated file it can reproduce byte-for-byte; the divergence is published, not
   smoothed. This is not a data error, only a reminder that the model line is an older input than the market.
4. **Aurora's day-one collapse is an outlier, not a trend.** Aurora lost the opener 0–2 to 9z and then won
   three series in a row, including the 2–0 rematch on day three. The July roster rebuild
   (kyxsan and Jimpphat in, coach ash, completed 7 July 2026 before BLAST Bounty Season 2) means pre-July
   results describe a different core, but the rebuilt Aurora is a top-five VRS side, so "new roster, therefore
   fragile" is not a defensible read of this event
   ([HLTV news 45082](https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan)).
5. **Day-5 has no market.** No retained receipt prices the 3rd-place decider (HLTV 2399416) or the best-of-five
   grand final (HLTV 2399417); both were still without a captured market at 23:57 UTC on 16 October
   (`research/harvest-76712ccc/pinnacle-sweep.json` lists only TWC matchups for the group stage and semis).
   The board publishes no pick for them until either Hotspawn lists them or a receipt exists.

## 3. Effect of this session's coverage work on the board

`data/identities.json` gains a sourced `6666`/`ex-6666` entry (roster overlap 4 of 5 against Valve's #127
row, 1 of 5 against the #368 row), so the next scheduled refresh prices Hotspawn fixture 1081521 as an
originated `model_vrs` line: **ex-6666 78.25% / Privateer 21.75%** (923 vs 608 points, standings #127 vs
#271). `verification-c6/audit_snapshot.py` reproduces that row with 0 failures, and the pick-only count goes
from four to three: `antidaun`, `Morningstar` and `WXM` remain unlisted in every official Valve list
(global, Europe, Asia and Americas, all four retained in `research/quotes-76712ccc/`), so those rows keep a
blank probability rather than an invented one.
