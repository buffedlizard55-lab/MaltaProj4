# Preserved concurrent integration (historical, not current picks)

`main/` is a byte-for-byte archive of the tree at main commit
`b3d8d6067528e7b912ac576e4f401d06e04b52b3`. It preserves the separately
completed d1bae160 implementation, research, source snapshot and tests rather than
discarding them in the integration conflict. Its latest separate coordination
handoff is `../d1bae160.md`. The complete code history is also a parent of the merge.

The active dashboard/collector is the repository-root c4d25599 integration. Do not
interpret this historical seed dataset, its dates or the older parser's looser
matching gates as current recommendations. There is one active production workflow.
The public `/methodology.html` and old `/site/*.html` routes redirect to the new
current views instead of publishing a second stale dashboard.

All eight original Python tests were re-run successfully in this directory using
its original pinned requirements on 15 October 2026. The active implementation's
81 tests, primary-response replay, exact UTC/market/quality/expiry gates and 28
browser accessibility scans are separate, stricter acceptance checks.
