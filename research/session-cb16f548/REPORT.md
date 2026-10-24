# Session cb16f548 — refresh recovery and complete-board receipt

## Scope and source policy

Hotspawn supplies fixture membership, teams, UTC schedule and lock state only. Its crowd percentages are not probability inputs. HLTV community sentiment is also excluded. Prices come from retained exchange/bookmaker evidence or the documented Valve VRS model; unverifiable fields remain blank. No alias, start time, pick or probability was manually entered for this integration.

## Fresh capture

Trusted non-publishing workflow run: [40066594501](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40066594501).

- Snapshot: `2026-10-24T05:40:24.418960Z`; fixture evidence: `2026-10-24T05:36:51.912500Z`.
- Snapshot SHA-256: `1e09af375e3fa3a7900b7aaee5bfb5cd5d787cfa7725e14aa153144d63e47511`.
- Three-view Hotspawn coverage: **verified**, with 88 API rows, 88 CS2-page rows, 88 lobby rows and 88 retained rows.
- 88 feed rows total: **25 open, 63 not open**. All 25 open rows have a pick and two normalized win probabilities. No open row is unresolved and no research-only row lacks a percentage in this dated capture.
- Open-row methods: 12 `exchange`, two `exchange_wide`, two `bookmaker_fallback`, seven `model_vrs`, two `model_vrs_mirror`.
- Quarantine withheld **0 rows**; the independent C6 replay and additional coverage/integrity audit reported **0 failures**.

The immutable capture, refresh/quarantine/browser logs, independent audits, complete row ledger and coverage summary are in [`harvest/`](harvest/). In particular, [`harvest/row-ledger.md`](harvest/row-ledger.md) gives every row's official fixture source and external price/model source.

## Repairs made

1. **Publication lifecycle:** the dated lobby test now uses captured official locks and explicit current removal evidence. It still rejects a still-open fixture disappearing; it no longer requires already-locked IDs to remain in every later scheduled feed. Focused synthetic before-lock and post-lock cases are in `tests/test_session_cb16f548.py`.
2. **Tall-phone layout:** closed the short-phone CSS block that had accidentally nested all later phone-first rules beneath `max-height:700px`. Canonical and root CSS are identical and brace-balanced. A small short-phone gap adjustment keeps the first probability block above the fixed tabs.
3. **Independent mirror replay:** `research/session-0cc1138a/verify_0cc1138a.py` now rebuilds `model_vrs_mirror` probabilities from the retained HLTV-published Valve points with the same independently implemented Valve formula and calibration. It does not import the collector.
4. **Rotating-board tests:** the first-pick phone test derives the expected date from the sourced fixture instead of hard-coding October 23. The lifecycle regression uses the immutable dated lobby rather than unrelated later inventory removals.
5. **Public review record:** `data/review-notes.json` records the publication outage/recovery and the tall-phone defect, with Actions and regression links. Current feed-status and per-row model/wide-quote limitations continue to render on **Flagged for Review**.

## Verification on the promoted fresh candidate

- `python -m unittest discover -s tests`: **1,200 tests, OK; 1 skipped**.
- `python -m unittest discover -s audits -p 'test_*.py'`: **9 OK**.
- `python verification-95b588c2/test_integrity.py`: **5 OK**.
- `python -m unittest discover -s verification-c6 -p 'test_*.py'`: **12 OK**.
- Independent `verify_0cc1138a.py`: **25 open rows checked, 25 re-derived, 0 failures**.
- Clock-aware coverage contract: **25 actionable; 0 unresolved; 0 expired; 0 problems**.
- `scripts.validate`: **88 rows, 25 calculations reproduced, 15 pages, 815 internal links/assets, 20 checksums, 217 displayed rows**.
- All nine Chromium suites passed, including 32 page/viewport accessibility/no-overflow scans, exact expiry boundaries, both-team probabilities, official row links, 320/390px first-screen placement, stale-copy/counter agreement, and the new tall-phone computed-order regression.

## Measured phone result

Real Chromium reads against the fresh root build are stored in [`phone-final.json`](phone-final.json); screenshots are retained beside it.

- 320×568 home: first card begins at y=320; both-team probability block is y=447–503; fixed tabs begin at y=507; pick CTA is 46px high.
- 390×844 home: first card begins at y=324; both-team probability block is y=451–507; fixed tabs begin at y=783.
- 320×568 picks: first pick's two probabilities are y=425–452, above the y=507 tab bar.
- 390×844 picks: first pick's two probabilities are y=629–658, above the y=783 tab bar.
- No measured phone viewport has horizontal overflow. The executive summary retains direct **View updated picks** and **Unresolved** links and a separate `#unresolved-limits` section.

## Publication receipt

Integration and live Pages verification are appended after the merge; the capture itself never deploys or rewrites source timestamps.
