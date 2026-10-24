# Session 233b8a0e — report (2026-10-24)

## What was wrong, measured not assumed

The board kept reverting to "0 picks" not because a match could not be priced but because the
publication workflow never reached the collection step. `pages.yml` runs
`python -m unittest discover -s tests` **before** it refreshes a source, so one red test freezes the
whole board until the committed snapshot ages past its eight-hour window. On `main` `dce494b` that
command was red (`Ran 1233 tests … FAILED (failures=8, errors=1)`), reproduced locally in this
sandbox.

Two of those failures were the same class of defect this session then hardened:

* the served root `assets/style.css` had 725 `{` against 724 `}` — the missing brace closed a
  short-phone media query, so every later phone rule was nested inside it;
* the independent verifier could not map Hotspawn's *Projeto do KinGui* onto the exchange's
  *Tropa do KinGui* for fixture `1083121`, although `data/identities.json` carries that rename with
  primary evidence.

Both were repaired on `main` by concurrent sessions (`cecfe864`, `ea2e254c`) while this one was in
flight. This session's versions were dropped rather than layered on top; what remains from it is the
part that does not exist elsewhere.

## What this session delivers

1. **A guard against the layout drift.** `scripts.stage_legacy.ensure_stylesheet_parity()` repairs a
   drifted root copy while staging, and `scripts.validate.validate_stylesheet()` fails any build whose
   served stylesheet is unbalanced or differs from the canonical `site/assets/style.css` (unit-tested
   for both a missing and an extra brace, plus an idempotency check).
2. **An every-match coverage ledger.** `scripts/coverage_233b8a0e.py` reports, from values already in
   the snapshot, the per-rung counts of the pick ladder and the full unresolved ledger (HLTV first,
   then esportsbook lines) with each row's own recorded reason and attempts. The same script runs in
   the non-publishing harvest workflow `.github/workflows/harvest-233b8a0e.yml`, which this sandbox
   needs because it cannot reach hotspawn, Polymarket or HLTV (measured: all three fail TLS egress;
   only GitHub and package registries answer).
3. **Four dated findings** on *Flagged for Review*, each with source links.
4. **A pinned contract on the first-screen summary route** (`tests/test_session_233b8a0e.py`): one
   route, never folded, before the pick list, in-site links only, and the full summary bar still
   naming the updated picks, the at-a-glance list, the unresolved section and page, all matches and
   flagged-for-review.

## Verification on the integrated tree

* `python -m unittest discover -s tests` — 1,317 tests OK (1 skipped)
* `python -m unittest discover -s audits -p 'test_*.py'` — 9 OK
* `python verification-95b588c2/test_integrity.py` — 5 OK
* `python -m unittest discover -s verification-c6 -p 'test_*.py'` — 12 OK
* `python -m scripts.validate --data data/latest.json --site .` — 92 rows verified against the primary
  snapshot, **31 probability calculations reproduced**, 878 links/assets, 20 artifact checksums,
  234 displayed match rows
* `npm run test:browser` — all nine Chromium suites (320/390/768/1440, accessibility, expiry, phone
  geometry)
* `python -m scripts.coverage_233b8a0e` — see `coverage.md` beside this file

## Board state at the evidence timestamp

`coverage.md` in this folder is generated from `data/latest.json` (snapshot `2026-10-24T06:19:43Z`,
fixtures observed `06:16:00Z`): 92 feed records, 61 past-dated, 31 open, 31 picks, 31 win
probabilities, 0 unresolved, with the rung-by-rung counts and an explicit statement that no row
needed the unresolved ledger at that capture.

## Open items for manual review

* The four `session-233b8a0e-*` notes on `review.html`.
* GitHub Actions capacity: during this session every workflow on the repository sat `queued` or
  `pending` for 40+ minutes (many runs across branches), so no fresh capture could be committed from a
  runner and the board continues to be the 06:16Z observation. The eight-hour window and the stale
  banner are doing exactly what they say; a starved queue is an operational limitation, not a data
  repair.
