# Session f533492a — fresh Hotspawn CS2 coverage and integration report

Date: 2026-10-24 (UTC). Fixed Arena branch: `arena/f533492a-maltaproj4`.

## 1. Starting state and publication incident

The committed `data/latest.json` was generated at `2026-10-23T11:47:19.504519Z`, with fixture evidence observed at `2026-10-23T11:43:39.234092Z` and 90 retained feed rows. Those are dated facts about the starting artifact, not a claim of current coverage on 24 October.

The official GitHub Actions API showed five consecutive scheduled `Verify, refresh and publish CS2 Scout` failures, all at step 8, **Unit and independent failure-mode tests**, before the source-refresh step:

| Run | Scheduled at (UTC) | Result |
| --- | --- | --- |
| [39956197341](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39956197341) | 2026-10-23 12:49:03 | failure, unit/independent gate |
| [39998307424](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39998307424) | 2026-10-23 17:50:02 | failure, unit/independent gate |
| [40025828846](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40025828846) | 2026-10-23 21:18:45 | failure, unit/independent gate |
| [40042111432](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40042111432) | 2026-10-23 23:53:03 | failure, unit/independent gate |
| [40062143026](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40062143026) | 2026-10-24 04:23:24 | failure, unit/independent gate |

Local reproduction with the pinned dependencies: **1,195 tests, one failure and one error**, both in `tests/test_session_0cc1138a.py::LiveHotspawnCoverage`.

- `test_snapshot_covers_the_observed_lobby_fixtures` still required historical lobby IDs `1079655` and `1081148`.
- `test_each_observed_fixture_is_published_with_a_pick_and_an_official_link` raised `KeyError: '1081148'`.
- The current snapshot contains neither ID in `matches` nor in its raw `fixture_evidence`. Its `inventory_changes.removed_ids` is empty because that field compares only with the immediately preceding snapshot, not with the historical 23 October 09:44 observation.

### Narrow repair

The historical observation remains binding for every ID that the current official feed still returns. Membership now comes from the snapshot's complete current `fixture_evidence`, not solely from the one-refresh `removed_ids` delta. The second test skips an ID only when it is absent from both current raw evidence and the board; every retained/current row keeps its pick-before-lock, blank-after-lock, official-link, and live-evidence assertions. No pick, probability, source timestamp, or production freshness rule was changed.

Verification after the repair:

- `python -m unittest tests.test_session_0cc1138a.LiveHotspawnCoverage -v`: **2 tests passed**.
- `python -m unittest discover -s tests`: **1,195 tests passed, 3 skipped**.
- `python -m unittest discover -s audits -p 'test_*.py'`: **9 passed**.
- `python verification-95b588c2/test_integrity.py`: **5 passed**.
- `python -m unittest discover -s verification-c6 -p 'test_*.py'`: **12 passed**.
- `python -m scripts.validate --data data/latest.json --site .`: **90 rows, 27 probability calculations reproduced, 15 pages, 810 internal links/assets, 20 checksums, 212 displayed match rows**.

### Publication-gate ordering repair

The incident was also structural: the scheduled workflow ran data-dependent tests against the committed board before it was allowed to refresh that board. Moving only the test step would not have fixed the input mismatch, because the tests read `data/latest.json` and root HTML while the collector writes `runtime/latest.json`.

The trusted sequence now refreshes and quarantines first, independently audits/builds/validates the candidate, then calls `scripts.stage_legacy` to stage those hash-verified bytes in the runner workspace. The complete unit, independent-audit, root-link and browser gates run against that candidate. Staging has no commit, push, artifact-upload or deployment effect; all publication effects remain downstream of every gate. Pull requests still skip the network refresh and rebuild/test the committed candidate through the same sequence. No test or independent validator was removed or made non-blocking.

`tests/test_session_f533492a.py` adds six ordering and gate-preservation regressions. After this change the complete local suite is **1,201 tests passed, 3 skipped**. Fresh-candidate browser and deployment evidence remains a separate required gate.

## 2. Fresh-source capture plan

`.github/workflows/harvest-f533492a.yml` runs the production read-only refresh on ordinary GitHub Actions egress. It queries the official Hotspawn fixture API, CS2 pick'em page and general lobby, then the configured external evidence ladder (exchange/book listings, HLTV, Valve standings and originated model/research tiers). It never deploys Pages and never pushes to `main`.

The capture retains the refreshed snapshot, source attempts, independent row audit, per-row source ledger, gap summary, build/validator output and browser results. Receipts are returned even if a later verification gate fails; a failed capture is evidence for diagnosis, not an approved publication candidate.

Standing evidence rules:

1. Hotspawn provides fixture identity, start and lock evidence only—never match probability.
2. Hotspawn/HLTV crowd votes are excluded.
3. Only rows unresolved by the featured market tiers receive the HLTV-first, then esportsbook/listing research pass.
4. Unknown values remain null/blank with a source-linked limitation; no 50/50 filler or guessed identity is allowed.
5. Every accepted numeric probability must be replayable from its retained external quote or the published Valve-model inputs and formula.

Fresh results and row-by-row findings will be appended only after the runner returns them.
