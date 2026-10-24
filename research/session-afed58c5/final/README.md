# Final merged-candidate verification — 2026-10-24

This directory records local verification of the merged implementation and `data/latest.json`, not a claim that GitHub Pages has deployed these bytes.

## Candidate

- Snapshot generated: `2026-10-24T16:40:40.748952Z`
- Fixtures observed: `2026-10-24T16:37:04.190185Z`
- Local build: `2026-10-24T16:53:10.015363Z`, revision `0b21241f6f478d61f64b2facce0090b7322ce3bc`
- 83 official fixture rows; 22 captured-open picks; 22 probability pairs
- Methods: 14 exchange, 1 wide exchange, 3 bookmaker fallback, 3 official-file VRS model, 1 HLTV-mirror VRS model
- Source snapshot SHA-256: `5fdeefc003771b6fba7a55d3108baddbe16b4345a63d2fab63e52a8ac821c49b`
- Staged public-data SHA-256: `47390594b7d893a4aeccdf56a9752d56f80ab0b638ec33a88fa4a4006ce39f6b`

## Passing gates

- `unit.log`: 1,490 tests, 7 skipped, OK
- `audits.log`: 9 tests, OK
- `c6-tests.log`: 12 tests, OK
- `root-validate.log` and `public-validate.log`: 83 rows, 22 calculations, 15 pages, 787 links/assets, 20 checksums, 195 displayed rows
- `c6.log` / `published-c6.log`: zero independent row failures
- `independent-rederivation.json`: second independent replay exited zero
- `coverage-contract.json`: inventory fresh, 22 actionable rows, zero problems
- `ledger/`: 22/22 captured-open coverage complete, zero integrity failures
- `browser.log`: complete `npm run test:browser` chain passed with `pipefail` enabled

## Lock-time boundary

Two fixtures locked at 16:54 UTC while the browser chain was running. The default Open board therefore showed 20 runtime-open rows, while the 22 captured rows and closed warnings remained available. Test-only changes select runtime-visible rows and preserve Reset's intentional All entries behavior. Production lock enforcement and generated public bytes were not changed.

`browser-lock-boundary.log`, `browser-remaining.log`, and `browser-tail.log` retain the failed/intermediate diagnosis. Only `browser.log` is the final complete-chain receipt.

## Reproduce

```bash
python -m unittest discover -s tests
python -m unittest discover -s audits -p 'test_*.py'
python -m unittest discover -s verification-c6 -p 'test_*.py'
python -m scripts.validate --data data/latest.json --site .
python -m scripts.build --data data/latest.json
python -m scripts.validate --data data/latest.json
python verification-c6/audit_snapshot.py data/latest.json --output independent-row-audit.md
python verification-c6/audit_snapshot.py public/data/latest.json --output published-row-audit.md
python research/session-0cc1138a/verify_0cc1138a.py --data data/latest.json --json
python -m scripts.coverage_contract --snapshot data/latest.json --require-fresh --output coverage-contract.json
python -m scripts.audit_9b97d585 --snapshot data/latest.json --previous research/diag-ac5bcb06/snapshot.json --output ledger
npm run test:browser
```
