# Session 8fdf1f99 — "the site says there are picks but shows none"

Date: 2026-10-23 (UTC). Author: session 8fdf1f99.

## 1. What the user saw, and what it actually was

The report was three complaints in one: *the updated picks page shows no picks*,
*no picks are shown in the "Where the updated picks are" section*, and *matches
without a pick have no explanation*.

The board itself was complete. The live page was serving a snapshot captured at
`2026-10-22T20:15:52Z`. Every percentage on this site carries an evidence
deadline (eight hours from observation, or the pick lock, whichever is sooner),
and once a row's evidence passes its deadline the runtime deliberately withholds
the number rather than showing a stale one. At 04:15Z on 23 October every row on
the published board crossed that line at once, so the site had 30 open matches,
30 picks in the data, and nothing it was willing to show. It was not a rendering
bug and it was not a data gap: **nothing had published for ten hours**.

Why nothing published: the `Unit and independent failure-mode tests` step of
`Verify, refresh and publish CS2 Scout` was failing on `main` (runs
[39871808909](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39871808909)
at 23:26Z and
[39886171791](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39886171791)
at 01:49Z, both failing at step 8). Two tests pinned the *historical* research
sub-tier of two live fixtures (`research_rank_single`). The 20:15Z refresh had
re-derived those rows from Valve's standings tier (`research_vrs_single`), which
is a legitimate, better-sourced answer to the same question. The tests were
therefore comparing today's data with yesterday's route to it, and they went red
the moment the data improved.

Fix (merged as PRs #196 and #200/#205): assert the invariant — *a research row
is still a research row, its pick is one of the two teams, and it publishes no
percentage* — and never a historical method string or a historical pick.

## 2. Why it stayed dark for ten hours

The cadence watchdog behaved correctly: after three consecutive failures on the
same commit it stopped dispatching into a broken gate
(`scripts/refresh_watchdog.py`, `evaluate()` → `stop`). The defect was that the
only place it said so was a workflow log. A red gate that stops publication is
exactly the event a human needs to see.

This session therefore gives the watchdog one write beyond its dispatch:
when it stops because the gate is red, it opens **one** deduplicated issue
(`Publish gate is red: no CS2 picks can be published`) naming the decision, the
consecutive failures, the frozen snapshot time, the live site, and the last
three failing runs, then keeps that issue's body current. It never duplicates
the issue, never re-opens it after a human closes it while the gate is healthy,
and a failure in the alert path cannot break the tick. `issues: write` was added
to the watchdog workflow for this single purpose; the workflow still never
touches data or the site.

## 3. Coverage: every open match, priced or honestly blank

At the repaired snapshot (`2026-10-23T05:22:51Z`, on `main`) the board carries
92 feed entries, 30 open, **30 picks, 30 win probabilities, 0 unresolved**. The
two rows that had been research-only were resolved as follows.

### 3.1 `1082860` FlyQuest vs Staqued — external line, 92.30% / 7.70%

Staqued has no row in Valve's published standings in any file, so the originated
model cannot price this match; both sessions that researched it converged on the
same external line rather than inventing a rating:

| source | reading |
| --- | --- |
| [EGamersWorld match page](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3) | FlyQuest 1.001 / Staqued 12.0 (its own book-average sentence: 1.012 / 11.945) |
| [bo3.gg](https://bo3.gg/matches/flyquest-vs-staqued-27-10-2026) | FlyQuest 1.00 / Staqued 12.00, same Bo3, same start |
| [Polymarket](https://polymarket.com/esports/cs2/dfrag-invitational) | 51 / 50 with `$0` volume — not a market price, not used |
| [HLTV fixture 2399890](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026) | identity: exact opponent pair, `2026-10-27T03:00:00Z`, Bo3; FlyQuest world #61 / VRS #54, Staqued unranked |

De-vigged from the label-bound two-way pair: **92.30% / 7.70%**, overround
8.23%. The identity evidence (HLTV fixture parity plus both team pages) and the
corroborating second listing are stored with the receipt, and the receipt is
re-read by `scripts/books.py` on every refresh, so the row reverts to a research
pick rather than holding a stale number if the listing moves.

### 3.2 `1081149` FORZE Reload vs LFO 10 — model line from the dated mirror, 78.1% / 21.9%

LFO 10 is absent from Valve's 2026-10-05 global file (which lists LFO 7, 8 and 9
— different rosters), so the model could not see it on 22 October. HLTV's dated
view of Valve's ranking ([`valve-ranking/teams/2026/october/23`](https://www.hltv.org/valve-ranking/teams/2026/october/23))
publishes LFO 10 at VRS #151, and the existing, verified `model_vrs_mirror` tier
reads exactly that page with the same Valve formula and calibration. The first
refresh that read the 23 October view priced the row at **78.1%** for FORZE
Reload — the pipeline's own number, not a hand-written one. HLTV's fixture page
[2399499](https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12)
independently shows `VRS: #151` for LFO 10, and Hotspawn's feed timestamp
(`1792742400000` = `2026-10-23T08:00:00Z`, lock 07:54Z) is what the board uses.
The earlier suspicion of a start-time conflict was checked and does not exist:
Hotspawn's lobby renders in UTC−4 (04:00), which is the same instant.

## 4. What the site must keep doing

`tests/test_session_8fdf1f99.py` pins the user-facing contract, all against a
build of the committed snapshot:

* every open match has a pick, and the pick is one of the two teams;
* a match either has two probabilities that sum to 1 with dated evidence, or it
  is a research row with a stated limitation — never a blank and never 50/50;
* everything without a percentage is listed on `unresolved.html` with its
  reason, and the executive summary always links the limitations section and
  says the words "never 50/50";
* the executive summary's own counts (open, with a pick, with a probability)
  agree with the data it summarises, so prose cannot drift from numbers;
* `picks.html` contains every open fixture id and is one tap from the summary;
* the phone layout keeps the viewport at 320 px with no horizontal overflow
  (also enforced by `npm run test:browser`, five suites, 32 layout scans);
* no test file may pin a historical method or a historical probability for a
  live fixture id — the exact defect that caused this outage.

## 5. Residual risks (flagged, not hidden)

* **Evidence expiry is the sharp edge.** A ten-hour publishing gap is invisible
  below the surface and total on the surface. The escalation issue in §2 makes
  the next one visible within ten minutes; it does not make the board publish.
* **Aggregator prices.** `1082860` is priced from a listing site's aggregated
  two-way quote, not from a single operator's own feed. It is labelled
  `bookmaker_fallback` on the row, carries the receipt URL and the observation
  time, and expires like every other quote.
* **Monthly standings.** A team that moves roster between Valve's monthly cuts is
  a known blind spot of the model tier; the row then falls back to a research
  pick rather than guessing.
