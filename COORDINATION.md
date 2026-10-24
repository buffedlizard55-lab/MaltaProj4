

## Session b0163396 claim — expiry-safe fallback ladder browser assertion (2026-10-24 UTC)

Read the shared board before claiming. No active owner is editing this browser assertion. The product's freshness gate intentionally removes expired percentages; the fallback ladder then puts those open rows under its explicit `none` rung. The existing browser test incorrectly excludes `none` when summing rung counts, so it fails on a valid stale/withheld snapshot (reproduced against the committed snapshot after its 8-hour evidence window). This is a test-contract correction only; do not alter picks, source data, expiry behavior, rendered pages, or shared navigation.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Make the executive-summary fallback ladder browser assertion sum every rung, including `none`, and verify both fully priced and withheld/expired scenarios | in progress | b0163396 | `tests/browser_019a253a.cjs`, `COORDINATION.md` | 2026-10-24 |

Verification performed before editing: `python -m scripts.validate --data data/latest.json --site .` passed (92 rows, 29 reproduced calculations, 15 pages, 858 links/assets, 20 checksums, 227 displayed rows); Python unit suite passed (1,484 tests, 1 skipped). Building `public/` from the retained snapshot at the actual runner clock correctly withheld old probabilities, after which `npm run test:browser` exposed the bad assumption: 22 open rows were in `none`, but the assertion summed only zero-price-method rows. This does not establish a current live refresh; the retained snapshot is older than its eight-hour evidence window and the site correctly fails closed.
