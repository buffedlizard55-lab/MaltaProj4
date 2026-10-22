# Session d88949c4 — restore the scheduled refresh gate

**Date:** 2026-10-22 (UTC)  
**Scope:** deterministic verification of the retained `bf09aa40` Off Chops snapshot; no production model, fixture data, market receipt, or site output changed.

## Finding and repair

GitHub Actions run [39731049149](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39731049149), created at 05:58:02Z, failed in `Unit and independent failure-mode tests`. Its later source-refresh, build, and deploy steps were skipped. The same failure reproduced locally in `tests/test_session_bf09aa40.py::TestHarvestGapEvidence::test_the_live_refresh_now_prices_the_off_chops_fixture`.

That test replays the immutable snapshot at `research/harvest-bf09aa40/snapshot.json` (generated `2026-10-21T21:18:58.345679Z`; the model evidence was observed at `21:18:58.286925Z`) but validated it against `datetime.now()`. Once that historical observation was more than eight hours old, the replay correctly rejected it as stale *for a new recommendation*; the test's use of wall-clock time was wrong for a historical replay. The assertion now validates the retained quote as of the snapshot's own `generated_at`, so its age gate remains active and deterministic without refreshing or rewriting old evidence.

## Source check

The calculation's retained Valve inputs were checked directly against the official, immutable Valve standings file at commit `eec4853d7bcf0f1f7efe7f0d901234bef7e98b75`: [Valve Global Standings, 2026-10-05](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md). I retrieved the file through GitHub's Contents API at that commit, decoded the returned bytes, and compared them to the vendored copy; both SHA-256 hashes are `df96e7fc3cd91a2687ec08cac0128e50cc4e4e55346581679572e881d79ae61b`. The official rows show Ground Zero at 878 points / rank 136 and THUNDER dOWNUNDER at 971 points / rank 119. This repair does not alter those inputs or the already-registered Off Chops identity mapping.

## Verification performed

- Targeted historical regression: **1 test passed**.
- Main unit suite: **763 tests passed**.
- Independent audit suite: **9 passed**; integrity suite: **12 passed**; C6 snapshot audit tests: **5 passed**.
- `scripts.validate --data data/latest.json --site .`: **97 source rows**, **29 reproduced probability calculations**, **15 pages**, **941 internal links/assets**, **20 artifact checksums**, and **278 displayed match rows** verified.
- Browser suite: **32 page/viewport accessibility and overflow scans** across 320/390/768/1440px; seven board-expiry scenarios, four quote-boundary/future-clock scenarios, and eight additional phone/desktop/queue/unresolved-summary scenarios passed.
- `npm ci --ignore-scripts`: 0 reported vulnerabilities.

## Irregularities / limitations

- The failed scheduled run did not reach its refresh step, so it is not evidence of an external-source outage or a new market finding. The scheduled update can resume only after the test gate is green and a trusted `main` run reaches the refresh step; that post-merge run and live deployment still need confirmation.
- The retained 2026-10-21 snapshot is historical and is not presented here as a current market quote. No probability, roster fact, or fixture value was inferred or updated as part of this test-only repair.
