# Session b1962898 — independent verification, live freshness clock, measured cadence

**Branch:** `arena/b1962898-maltaproj4` · **Base:** `main` @ `be81768` · **Date:** 2026-10-23 (UTC)

## What the user asked for, and what this session found

The request was the standing one: a pick for every Hotspawn CS2 match, a separate unresolved
section with its limitations carried into the executive summary, in-site links from that summary
to the pick list, phone-first readability, and line-by-line verification from official sources.

At claim time the board already met the coverage ask (`data/latest.json`, snapshot
`2026-10-23T08:29:19Z`, 92 rows, 30 open, **30 picks, 30 win probabilities, 0 unresolved**). So this
session did not look for coverage to invent. It verified what is published, and it fixed two
things a reader could actually see:

1. **The published freshness clock was wrong after a few minutes.** The executive summary's
   freshness strip printed a build-time constant, `next slot 08:34 UTC`, derived from the snapshot
   time. At 10:00Z the live page still advertised 08:34Z as upcoming. Fixed: the strip now states
   only the cadence in static HTML and `assets/app.js` computes the next `:04/:19/:34/:49` slot and
   the snapshot age against the reader's clock (measured: `next slot 10:34 UTC` and
   `snapshot 1h 51m old` at 10:20Z; `next slot 20:49 UTC`, `snapshot 12h 16m old` in the stale
   scenario). No-JS readers see no specific time at all, so nothing can go stale in the markup.
2. **The cadence claim was asserted, not measured.** The site said checks run "every 15 minutes".
   Reading the public Actions API for 2026-10-22T01:39Z → 2026-10-23T09:46Z (32.1 hours, 500 runs)
   shows GitHub delivered **14 scheduled runs in total — 7 of ~128 publication slots and 7 of ~193
   watchdog slots — while 296 push-triggered runs ran normally**
   (`research/session-b1962898/run-delivery.json`, source URL in the file). The method page now
   publishes that measurement with a link to the run history, and the index footer points at it.
   Freshness in practice comes from commits as much as from cron; the site already withholds
   expired picks rather than pretending, and now it says so where the claim is made.

## Verification performed

**Independent row audit, written fresh for this session** (`scripts/audit_b1962898.py`). It imports
nothing from `scripts.core`; every published number is re-derived from the operator's own raw fields
by separate arithmetic. On the refreshed capture: **92 rows, 327 assertions, 0 failures**, including—

| Check | Result on the captured board |
| --- | --- |
| Three Hotspawn views agree (API / page / lobby) and match the retained row count | 92 / 92 / 92 / 92 |
| Open matches | 30 |
| Every open match has a pick from its own two teams | 30 / 30 |
| Every priced row's probabilities are two values in (0,1) summing to 1, with fair odds that invert them | 30 / 30 |
| Exchange rows re-derived from the operator's raw `outcomePrices` (order-insensitive multiset) | 23 / 23 |
| Every priced row cites at least one non-Hotspawn source URL | 30 / 30 |
| Model rows cite Valve's official standings project or an HLTV ranking page | 5 / 5 |
| Expiry never later than start, lock, or observation + 8 h | 30 / 30 |
| Blanks: pick-without-percentage and unresolved rows carry a reason and an attempted source | 0 / 0 (none on this capture) |

**Live source reads** (runner egress, recorded in `research/harvest-b1962898/AUDIT.md`): every
Polymarket Gamma market URL on the board answered **HTTP 200** (18 distinct market APIs); the two
EGamersWorld listing pages answered **HTTP 403** to the audit's user agent. That 403 is recorded as
evidence, not treated as an error — the two rows priced from those listings keep their dated receipt
and their `bookmaker_fallback` label, and the audit does not re-derive a book price from a page it
could not read.

**Capture parity against the committed board** (`research/harvest-b1962898/COMPARISON.md`): same 92
fixtures, same 30 open, **no fixture added and none dropped** in the 83 minutes between the two
reads. 14 rows repriced: 12 moved a few points on the same exchange tier, and two (`1079198`
Metizport–BakS, `1079200` Color–ex-Zero Tenacity) moved from our `model_vrs` line to a labelled
wide exchange quote (the method mix is now 20 strict exchange, 3 wide exchange, 5 model lines and
2 bookmaker listings). Sources and clocks are retained on each row.

## Irregularities flagged for review (non-blocking)

* **`1079200` Color vs ex-Zero Tenacity — a 58-point quote outranks our model line.** Polymarket
  market `6072812` was read at 2026-10-23T09:52:47Z (exact pair, accepting orders, $684.12
  liquidity) with `bestBid 0.06 / bestAsk 0.64` — a 58-point spread, inside the project's labelled
  60-point wide tier. The row therefore publishes the midpoint `0.35 / 0.65` and picks **ex-Zero
  Tenacity**, while the model line computed from Valve's standings for the same fixture was
  `0.6884 / 0.3116` for **Color** — a 34-point disagreement in the opposite direction. Policy ranks
  a gate-passing market above the model, and the row carries its "low confidence" flag, so nothing
  was hidden; but whether a quote that wide should outrank the model at all is a policy question.
  Published on **Flagged for Review** as
  `session-b1962898-1079200-wide-quote-vs-model-2026-10-23` with the primary source links.
* **Scheduled delivery is ~4% of intent**, as measured above. The 5.5-hour gap between 01:49Z and
  07:20Z on 2026-10-23 is inside the 8-hour evidence window, so no live pick expired on this
  occasion, but a longer gap would blank the board until a commit lands. The measurement is now
  published rather than implied away.
* **EGamersWorld refuses automated reads (HTTP 403)** while the board still cites two of its
  listing pages for a dated receipt. The refusal is reproducible and recorded; it does not
  invalidate the receipt, which carries its own observation timestamp.

## Collision with session 138cbedd (same defect, one implementation kept)

Session `138cbedd` merged PR #223 on 2026-10-23 at 10:12Z with an independent repair of the *same*
freshness-strip defect (plus its own zero-collector auditor and browser suite). This branch rebased
onto it and **deleted its own duplicate clock code** — the `data-slots` / `data-age` block in
`assets/app.js` and its CSS rule — so the site carries exactly one clock: theirs
(`#next-slot`, `#fresh-age`, `data-slot-minutes`), which this session's tests now pin rather than
re-implement. Their auditor, tests and receipts are untouched; my own five tests that asserted the
removed markup were rewritten to the combined contract (4 tests, all passing). The distinct parts of
this session survive because they are additive: the measured schedule-delivery disclosure, the
independent `scripts/audit_b1962898.py` with its live source-link reads, the capture workflow and the
`1079200` wide-quote review note. Residual limitation recorded openly: with JavaScript off, their
build-time fallback text inside `#next-slot` can still name a slot that has passed.

## Rebase note (no rollback)

`main` advanced twice while this work ran. The first rebase kept this session's 09:52:43Z capture as
the newest snapshot. The second rebase adopted the **10:02:13Z** capture merged by session `51a9c98a`,
which is newer, so the published board is that one — no snapshot was rolled back and no other
session's work was dropped (their review notes and feed-scope disclosure are preserved; the conflicted
`data/review-notes.json` was union-merged by note ID, 173 + 1 = 174 notes). The independent audit was
re-run on the adopted board: **92 rows, 327 assertions, 0 failures**, method mix 20 strict exchange,
3 wide exchange, 5 model lines, 2 bookmaker listings — identical to the numbers above, and fixture
`1079200` is still published at `0.35 / 0.65` for ex-Zero Tenacity.

## Delivery gates run on the exact tree

* `python -m unittest discover -s tests` → **1,169 tests, OK (3 skipped)** on the merged tree,
  including 23 regressions in `tests/test_session_b1962898.py`.
* `python -m scripts.validate --site .` → 92 rows, 30 calculations reproduced, 15 pages, 823
  links/assets, 20 checksums, 221 displayed rows.
* `python -m scripts.audit_b1962898` → 92 rows, 327 assertions, 0 failures.
* All seven browser suites (`browser`, `expiry`, `browser_ac4743a3`, `browser_eaff7cce`,
  `browser_fe7f5de4`, `browser_f0814674`, `browser_138cbedd`) → pass, including the 320/390 px
  first-screen pick gates and the merged freshness-clock suite.

## Files touched

`scripts/build.py` (freshness strip, `CHECK_SLOTS`, measured cadence disclosure), `assets/app.js` and
`site/assets/app.js` (live clock, byte-identical), `assets/style.css` and `site/assets/style.css`
(`.fresh-age`, byte-identical), `scripts/audit_b1962898.py` (new), `tests/test_session_b1962898.py`
(new), `.github/workflows/harvest-b1962898.yml` (new, non-publishing capture), `data/latest.json`,
`data/matches.csv`, `data/review-notes.json` (one appended dated note), regenerated pages, root
`build-info.json`, `research/harvest-b1962898/**`, `research/session-b1962898/**`.
