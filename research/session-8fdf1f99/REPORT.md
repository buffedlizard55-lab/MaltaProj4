# Session 8fdf1f99 — publish-gate repair, unresolved-pick research, phone audit

**Date:** 2026-10-23 (all times UTC) · **Branch:** `arena/8fdf1f99-maltaproj4`

This session was asked to (a) make sure every Hotspawn CS2 match carries a pick and a
win probability, (b) research external sources (HLTV first, then esportsbooks) for the
matches the featured tiers cannot price, (c) put a separate unresolved-picks section
with its limitations into the executive summary, and (d) make all of it readable on a
phone. Every claim below links to the primary page it was read from on 2026-10-23.

## 1. Why the live site had no picks (root cause, measured)

| Fact | Evidence |
| --- | --- |
| The last published snapshot is `2026-10-22T20:15:52Z` | <https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json> |
| The board withholds evidence older than 8 hours (`const ttl = 8 * 3600000`) | `assets/app.js`, lines 42–51 |
| Scheduled runs on `main` failed at *Unit and independent failure-mode tests* before the refresh step | [run 39886171791](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39886171791) (01:49Z), [run 39871808909](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39871808909) (23:26Z) |
| Reproduced locally at `7b9180d`: 961 tests, 2 failures | `tests/test_session_13e99ca6.py` expected every research row to start `research_rank`; `tests/test_session_75ebd2d6.py` expected fixture 1081149 to still be `research_rank_single` while the 20:15Z refresh recorded `research_vrs_single` |

Both assertions pinned a *historical* value that a routine refresh legitimately changes
(the research sub-tier of a row). The fix pins the invariant instead — a `research_*`
tier, a pick that is one of the two teams, a blank percentage, a source-linked
limitation — and `tests/test_session_8fdf1f99.py` fails if a historical research
sub-method is pinned again. With that repaired, `main`'s publish gate runs the refresh
again on its 15-minute schedule, so the board is refreshed well inside the user's 4–8
hour requirement.

## 2. Coverage at the repaired snapshot (the 23 October board on `main` is 92 rows, 30 open, 30 picked, 30 priced)

* 23 open matches, **23 with a pick** (100% of the Hotspawn list).
* 21 with a win probability (13 exchange lines, 1 labelled wide exchange line, 7 Valve
  VRS model lines), **2 research-only with a blank percentage**.
* Every unpriced row is named on `index.html#unresolved-picks` and on
  `unresolved.html` with its reason and every source tried.

### 2.1 Fixture 1082860 — FlyQuest vs Staqued — now priced from an external line

Staqued has no Valve VRS row in any published file (global or regional), so the
originated model cannot price this match; that is why the row carried a pick and no
percentage. Two independent listing sites publish an asymmetric two-way line for the
same Bo3 at the same start (2026-10-27T03:00:00Z):

| Source | Line | Read |
| --- | --- | --- |
| [EGamersWorld match page](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3) | FlyQuest **1.001** / Staqued **12** (its own book-average sentence: 1.012 / 11.945) | 2026-10-23T05:1xZ |
| [bo3.gg match page](https://bo3.gg/matches/flyquest-vs-staqued-27-10-2026) | FlyQuest **1.00** / Staqued **12.00**, same prediction panel 1.001 / 12 | 2026-10-23T05:2xZ |
| [HLTV fixture 2399890](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026) | identity: exact pair, 26 Oct 23:00 display = 03:00Z, Bo3 Group B opening match; FlyQuest HLTV #61 / VRS #54, Staqued unranked | 2026-10-23T05:1xZ |

De-vig of the label-bound pair: `1/1.001 = 0.99900`, `1/12 = 0.08333`, overround
**8.23%**, probabilities **92.30% FlyQuest / 7.70% Staqued**. The pages' own
book-average sentence (1.012 / 11.945) de-vigs to 92.2% / 7.8% — the same estimate.

The line is committed as receipt `egw-4kaAQWgKEx-flyquest-staqued` in
`data/book-receipts.json` and is replayed in
`tests/test_session_8fdf1f99.py::test_flyquest_staqued_receipt_prices_its_fixture`
through the production pricing path (`scripts.core.book_research_pick`). The existing
`scripts/books.py` re-observation renews or expires it on every refresh; if the listing
stops re-confirming the pair, the start and an asymmetric two-way pair, the row falls
back to the research pick with a blank percentage — it never keeps a stale number.

### 2.2 Fixture 1081149 — FORZE Reload vs LFO 10 — priced by the dated mirror on the next refresh

| Source tried | Result (2026-10-23) |
| --- | --- |
| [EGamersWorld listing](https://egamersworld.com/counterstrike/match/HiXMAaC8L/forze-reload-vs-_04jKZ07_4) | Opponent label is **blank** on the page and the odds widget shows the listing's **1.8 / 1.8 placeholder** — refused, not a market line |
| [HLTV fixture 2399499](https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12) | Betting table exposes no numeric two-way line; HLTV ranks shown: FORZE Reload unranked by HLTV, **LFO 10 "VRS: #151"** |
| [Valve global standings 2026-10-05](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | FORZE Reload **#84, 1100 points**; LFO 10 absent (LFO 7, 8 and 9 are listed — a different roster each) |
| [HLTV dated Valve ranking, 23 Oct 2026](https://www.hltv.org/valve-ranking/teams/2026/october/23?teamId=14084) | LFO 10 **present with a rank** in the newer dated view |

Because LFO 10 now resolves in HLTV's dated view of Valve's ranking, the existing
`model_vrs_mirror` tier (which reads exactly that page, same formula and calibration)
prices this row on the first refresh that reads the 23 October view. **Confirmed on
main**: the `2026-10-23T05:22:51Z` snapshot prices 1081149 with `model_vrs_mirror` at
**78.1% / 21.9%** for FORZE Reload. This session did not hand-write that number — the
sandbox has no egress to the source hosts, so the value came from the runner's own
read of the dated page.

### 2.3 Timing disagreement worth a human look

The 20:15Z snapshot stores fixture 1081149 at **14:00Z** (lock 13:54Z). HLTV and
EGamersWorld both show **08:00Z**, and Hotspawn's own lobby rendered the match at
04:00 in its UTC−4 rendering on 2026-10-23T05:00Z. Either the fixture moved earlier
after capture, or Hotspawn's `scheduled_start_time` disagrees with its lobby. The
repaired publish gate is the mitigation: each refresh re-reads every source and
re-states the lock, and every percentage expires at the earliest of its evidence
window, the lock and the start. Flagged on `review.html`.

## 3. Executive summary and phone audit

The executive summary (`index.html`) now carries, above the fold:

* `#exec-banner` — open matches, how many have a pick, how many carry a probability and
  how many are research-only, plus in-site links: `picks.html` (*Updated picks — all
  N*), the unresolved section, `review.html`, `matches.html`, “How we price”.
* `#start-here` — “Where the picks are” cards pointing at `picks.html`,
  `unresolved.html` and `matches.html`.
* `#unresolved-picks` — a separate section: *“Picks without a win probability — and
  exactly why”*, one card per unpriced row with the pick, the researched source, the
  gate that failed and a link.
* `#unresolved-summary` — “Limitations for generating these picks”, the full ladder
  (no book lists the match · a market exists but fails a gate · names differ ·
  HLTV has no usable line · TBA slot · our model needs both teams · timing · books
  post no line).
* A five-tab phone bar (Home · Picks · Unresolved · Matches · Analysis), card layout,
  no horizontal scrolling at 320/390 px, and `aria-label`s on the probability pairs.

New tests in `tests/test_session_8fdf1f99.py` pin the in-site links, the two
limitation sections, the viewport/mobile-tab markup on every primary page, and that
every unpriced row is named on both the executive summary and `unresolved.html`.

## 4. Verification performed

* `python -m unittest discover -s tests` → **975 tests OK** (961 before, 14 added).
* `python -m unittest discover -s audits -p 'test_*.py'` → 9 OK;
  `verification-95b588c2/test_integrity.py` → 5 OK;
  `verification-c6/test_*.py` → 12 OK.
* `python -m scripts.validate --data data/latest.json --site .` → 21 reproduced
  calculations, 15 pages, 774 links/assets, 20 checksums, 201 displayed rows.
* Receipt replay: `book_research_pick` on fixture 1082860 with the committed receipt
  prices **92.30% / 7.70%**, method `bookmaker_fallback`, pick FlyQuest, odds
  `[1.001, 12.0]`, overround 0.0823.

## 5. Flagged for review (non-blocking)

1. Publish-gate regression that froze the board (fixed here; `review.html` note
   `8fdf1f99-publish-gate-froze-the-board-2026-10-23`).
2. LFO 10's new VRS rank in HLTV's 23 October view; expected to price 1081149 on the
   next refresh (`8fdf1f99-lfo-10-now-has-a-valve-rank-on-hltv-2026-10-23`).
3. Hotspawn/H‍LTV start-time disagreement for 1081149
   (`8fdf1f99-hotspawn-lock-differs-from-hltv-for-1081149-2026-10-23`).
4. The researched FlyQuest vs Staqued line, with both the capped display pair and the
   book-average sentence recorded (`8fdf1f99-flyquest-staqued-researched-line-2026-10-23`).

Nothing in this report is inferred: every number is either read from the linked page or
computed from the values on it with the site's published de-vig formula.
