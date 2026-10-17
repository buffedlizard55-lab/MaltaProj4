# Day-4 pick-logic audit — session c97c1986

**Checked:** 2026-10-17 (UTC)
**Scope:** independent consistency review of the Day-1–3 TWC results, Day-4 semifinal guidance, and the published contrarian-strategy table. This audit uses retained HLTV/result captures and dated market receipts in the repository; it does not claim a fresh read of external markets at the time this file was written.

## Primary result checks

The retained HLTV match pages are parsed and hashed in [`verification-76712ccc/TWC-RESULTS.json`](../../verification-76712ccc/TWC-RESULTS.json), with a readable table in [`verification-76712ccc/TWC-RESULTS.md`](../../verification-76712ccc/TWC-RESULTS.md). The result sequence relevant to the upset thesis is:

| Day | Verified result | Why it matters for the pick discussion | HLTV source |
| --- | --- | --- | --- |
| 1 · 14 Oct | 9z 2–0 Aurora; Inferno 13–11, Nuke 13–1 | A genuine market upset, including a one-round Nuke map on Aurora's pick. | [HLTV report](https://www.hltv.org/news/45718/9z-beat-aurora-2-0-to-kick-off-twc-2026) · [match 2399384](https://www.hltv.org/matches/2399384/9z-vs-aurora-thunderpick-world-championship-2026) |
| 2 · 15 Oct | Aurora 2–0 NIP; Falcons 2–1 9z; FURIA 2–1 Legacy; BETBOOM 2–1 PARIVISION | Aurora immediately won its elimination match; 9z took a map from Falcons but lost the series. Day-2 outcomes do not support treating the opener as a stable new ranking order. | [HLTV event results](https://www.hltv.org/results?event=8932) · [Aurora–NIP](https://www.hltv.org/matches/2399408/aurora-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026) · [Falcons–9z](https://www.hltv.org/matches/2399409/9z-vs-falcons-thunderpick-world-championship-2026) |
| 3 · 16 Oct | Aurora 2–0 9z; BETBOOM 2–1 Legacy | The day-1 pairing reversed in a 2–0 rematch. BETBOOM qualified after the three-map decider, including Nuke overtime. | [Aurora–9z](https://www.hltv.org/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026) · [BETBOOM–Legacy](https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026) · [HLTV report](https://www.hltv.org/news/45739/betboom-qualify-for-twc-playoffs-over-legacy) |

The day-1 9z win is not, by itself, evidence that 9z should be preferred in a later match: Aurora's next results include a 2–0 over NIP and a 2–0 rematch win. The updated page frames the upset as noisy evidence and does not turn it into a probability.

### Day-1 result fields checked line by line

All four published Day-1 rows were compared with their retained HLTV match-page capture and 64-character SHA-256 in the receipt above. This review found two previously blank map fields and one row whose map attribution pointed to a betting preview despite a retained HLTV result capture. The JSON now uses HLTV for that row and fills only the scores that appear in the captured pages.

| Match | HLTV-captured map scores | HLTV match page | Capture SHA-256 prefix |
| --- | --- | --- | --- |
| 9z 2–0 Aurora | Inferno 13–11; Nuke 13–1 | [2399384](https://www.hltv.org/matches/2399384/9z-vs-aurora-thunderpick-world-championship-2026) | `a181a303d4997cfb` |
| Falcons 2–0 Ninjas in Pyjamas | Ancient 16–13 (overtime); Dust2 13–6 | [2399385](https://www.hltv.org/matches/2399385/falcons-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026) | `847327aacc6c3285` |
| Legacy 2–0 PARIVISION | Dust2 13–11; Mirage 16–14 (overtime) | [2399386](https://www.hltv.org/matches/2399386/legacy-vs-parivision-thunderpick-world-championship-2026) | `c2efc593c1562024` |
| FURIA 2–0 BETBOOM | Ancient 13–10; Mirage 13–9 | [2399387](https://www.hltv.org/matches/2399387/furia-vs-betboom-thunderpick-world-championship-2026) | `28b7fec23d9a0199` |

The explicit overtime labels are supported by the overtime-half fields in the retained HLTV page captures, not inferred from the final score alone.

## Aurora roster premise

HLTV's roster report dates the rebuild to **8 July 2026**, around three months before this TWC semifinal day: [HLTV's Aurora rebuild report](https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan). The current lineup and event results are separately linked from [Aurora's HLTV team page](https://www.hltv.org/team/11861/aurora). The report corrects the user's “recent roster change” premise for Day 4: this was not a same-week signing or an untested October lineup. The July move can be part of historical context, but the cited Day-4 facts do not establish a live onboarding penalty.

## Dated Day-4 line reads (not live-updated by this audit)

The raw research summary is [`research/day4-bca04a82/MARKET-READS.md`](../day4-bca04a82/MARKET-READS.md); the corresponding bookmaker/exchange receipts are in [`data/book-receipts.json`](../../data/book-receipts.json). The reported reads are dated **00:00–00:10 UTC on 17 October**.

| Semi-final | Polymarket Match Winner | Pinnacle whole-match moneyline, de-margined | Pick implication | Receipt sources |
| --- | --- | --- | --- | --- |
| FURIA–Aurora, 14:00 UTC | 52.5% / 47.5% | −125 / +103 → 53.0% / 47.0% after removing a 4.82% overround | FURIA is the narrow market favorite; Aurora is a near-even, lower-variance market underdog. | [Polymarket market 5778024](https://gamma-api.polymarket.com/markets/5778024) · [Pinnacle guest API](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight) · [time-stamped receipts](../../data/book-receipts.json) |
| Falcons–BETBOOM, 17:00 UTC | 79.5% / 20.5% | −389 / +298 → 76.0% / 24.0% after removing a 4.68% overround | Falcons is the clear market favorite; BETBOOM is the higher-variance swing. | [Polymarket market 5787759](https://gamma-api.polymarket.com/markets/5787759) · [Pinnacle guest API](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight) · [time-stamped receipts](../../data/book-receipts.json) |

For Pinnacle the arithmetic is reproducible: convert American odds to decimal, take reciprocals, then normalize by their sum. Polymarket's two outcome prices sum to 1 at the captured precision; no fee adjustment is claimed. The third comparison is the project's separately labelled VRS model, not another market: its dated Valve standings and model fit are documented in the cards and methodology. The market lines, model, and HLTV live VRS do not fully agree on FURIA–Aurora; that disagreement remains visible instead of being blended away.

## Rest/load audit and correction

The Day-4 prose previously called BETBOOM's consecutive three-map series “the day's only real underdog argument” and described the schedule in a way that could read as support for BETBOOM. That reverses the sign of the rest evidence. Results pages show **both market underdogs** (Aurora and BETBOOM) played on 16 October, while their opponents (FURIA and Falcons) last played on 15 October. From the retained series scores, the event map totals are:

| Team | Last TWC match date | TWC maps through group stage | Result-page evidence |
| --- | --- | ---: | --- |
| FURIA | 15 Oct | 5 | [14 Oct vs BETBOOM](https://www.hltv.org/matches/2399387/furia-vs-betboom-thunderpick-world-championship-2026) · [15 Oct vs Legacy](https://www.hltv.org/matches/2399411/legacy-vs-furia-thunderpick-world-championship-2026) |
| Aurora | 16 Oct | 6 | [14 Oct vs 9z](https://www.hltv.org/matches/2399384/9z-vs-aurora-thunderpick-world-championship-2026) · [15 Oct vs NIP](https://www.hltv.org/matches/2399408/aurora-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026) · [16 Oct vs 9z](https://www.hltv.org/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026) |
| Falcons | 15 Oct | 5 | [14 Oct vs NIP](https://www.hltv.org/matches/2399385/falcons-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026) · [15 Oct vs 9z](https://www.hltv.org/matches/2399409/9z-vs-falcons-thunderpick-world-championship-2026) |
| BETBOOM | 16 Oct | 8 | [14 Oct vs FURIA](https://www.hltv.org/matches/2399387/furia-vs-betboom-thunderpick-world-championship-2026) · [15 Oct vs PARIVISION](https://www.hltv.org/matches/2399410/parivision-vs-betboom-thunderpick-world-championship-2026) · [16 Oct vs Legacy](https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026) |

So rest is a **counterweight to both underdogs**, with BETBOOM carrying the heavier map load; it is not evidence in BETBOOM's favor. The approximate 22-hour BETBOOM turnaround depends on an estimated match-finish time and is now labelled approximate. This schedule evidence is not a measured fatigue effect.

## Revised contrarian reading

- **Baseline picks:** FURIA, then Falcons, because both are the higher-probability side in the captured external moneylines. These are analysis cards, not Hotspawn submissions.
- **Cleaner contrarian lean:** Aurora at about 47–48%. The price is close to even, while Aurora's Day-2/Day-3 results, live HLTV VRS position and 2026 head-to-head give a sourced reason to consider the smaller side. FURIA's extra rest and lighter map load are counterweights; no day-four roster-onboarding claim is used.
- **High-variance swing:** BETBOOM at about 20–24%. Its 2–0 June head-to-head win over Falcons and recent event results are a real upset case, but current market/VRS readings and the shorter turnaround point toward Falcons. BETBOOM is not a default pick and rest is not cited in its favor.
- **Leaderboard caveat:** Hotspawn's cited rules award points by correct pick/tier; this project has no verified user pick-share feed. A market underdog is not proof that Hotspawn entrants all chose the favorite, and no crowd-contrarian or leaderboard edge is claimed. The two TWC semifinals were absent from Hotspawn's CS2 feed in the 00:15 UTC nine-chunk read, so the cards have no Hotspawn tier/points value; see the [official lobby](https://play.hotspawn.com/lobby) and [scoped fixture feed](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1).

## Verification performed in this session

- Compared the Day-1 result rows with all four retained HLTV match-page captures and SHA-256 receipts; winner and series scores were unchanged, two previously blank Day-1 map fields were filled, and one map-score attribution was corrected from a third-party preview to HLTV.
- Recomputed the two Pinnacle no-vig percentages from the documented American lines; cross-checked the displayed Polymarket outcome prices and timestamps against retained receipts.
- Recomputed TWC map totals from each sourced series score: FURIA 5, Aurora 6, Falcons 5, BETBOOM 8.
- Corrected the executive summary, BETBOOM card, and rest finding to separate the historical upset case from the countervailing schedule evidence.
- Rebased onto the later main publication without dropping its Hotspawn scoring/crowd facts, Sunday unpriced-fixture table, or withdrawn ranking-count correction; only stale rest/contrarian wording was replaced.
- Added source links to every row in the contrarian-strategy table. The roster and fatigue rules are explicitly heuristics, not forecasts.

## Remaining limitations / flags

1. Polymarket/Pinnacle figures above are a **00:00–00:10 UTC capture**, not a live quote guaranteed at match time. Re-check the operator links before using a line.
2. HLTV is a specialist results/roster source, not the tournament organizer. Source links identify what was actually read; an official tournament-side match feed was not substituted.
3. The exact finish time for BETBOOM's decider is approximate; only its 16 October result and the next-day semifinal schedule are treated as verified here.
4. The source set does not include Hotspawn user pick-share, a calibrated historical leaderboard model, or a measured fatigue model. No claimed leaderboard lift follows from these picks.
5. The TWC main-event semifinals were not on the Hotspawn feed at the recorded 00:15 UTC read. They remain research-only, separately linked cards, not added as invented Hotspawn rows.
