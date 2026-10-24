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

## 3. Fresh captures and the 89-versus-88 upstream disagreement

Three non-publishing runner captures read the production sources on 24 October:

| Run | Fixture evidence / snapshot (UTC) | Result |
| --- | --- | --- |
| [40066481741](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40066481741) | 05:32 / 05:35 | 88 rows; 25 open; all 25 picked and priced |
| [40067086847](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40067086847) | 05:41 / 05:44 | 88 rows; raw API/CS2/general-lobby bytes retained; all local and runner audits passed |
| [40067947765](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40067947765) | 05:53:56 / 05:57:32 | 89-row reviewed candidate and four raw responses retained; the old independent auditor then rejected the scoped supplement URL |

An independent rendered read of the CS2-specific page reported **89** current-week filter entries, including one VOID Autumn Cup 2026 entry, while the general lobby reported **88**. The runner's raw CS2 HTML, general-lobby HTML and scheduled API response each contained 88 hydrated fixtures and no Chinggis Warriors/Rare Atom row. Thus this was an upstream response disagreement, not a reason to change a parser until its counts looked equal.

The official competition-scoped fixtures API (`competition_id=36412`) returned 13 VOID fixtures and identified the relevant exact row without guessing an ID:

- **1083045 — Chinggis Warriors vs Rare Atom — VOID Autumn Cup 2026 — 2026-10-24T03:00:00Z**.
- Its official Hotspawn match page confirms `FIN`, Chinggis Warriors **2–0** Rare Atom.
- The competition-scoped `status=scheduled` query returns no row; the unfiltered competition query continues to return the exact ended row, so receipt revalidation does not depend on a status remaining scheduled.
- No Hotspawn crowd field or match result is used as a probability. The row is `not_open`, with null pick, probabilities, fair odds and method.

## 4. Bounded reviewed-supplement implementation

`data/inventory-receipts.json` registers only fixture 1083045, its expected teams/start, official API/match/listing URLs, review basis and a hard expiry of `2026-10-26T00:00:00Z`. `scripts/inventory.py` now:

1. validates the receipt schema, official hosts and fixtures-API path, and rejects any pick/probability fields;
2. skips inactive receipts and skips a receipt when all three primary views already contain the ID;
3. re-fetches and schema-checks the official competition response every refresh, requiring exactly one registered ID plus the reviewed pair and UTC start;
4. sends the selected row through the same normalization, duplicate/conflict, provenance and not-open logic as every primary row;
5. retains only that ID, not the other 12 competition-history rows; and
6. leaves coverage **partial**, publishes a `coverage_difference` finding and fails closed on identity/source drift.

Fourteen focused workflow/receipt/auditor tests cover the positive union, expiry, already-covered skip, changed teams, missing ID, unofficial URL, forbidden probability/pick fields, registered-feed replay and tampering. The public methodology and a dated Flagged for Review note disclose the mechanism and the unresolved upstream disagreement.

## 5. Reproduced candidate-gate repairs

The 89-row candidate initially produced one `9b97d585` integrity failure: `row lacks the exact scoped Hotspawn fixture-feed link`. The auditor had hard-coded the scheduled-feed URL even though the supplemental row's actual evidence is the competition-scoped URL. It now accepts an alternate feed only when it exactly matches the committed registered receipt, fixture ID, official host/path/query, match URL and raw provenance. Arbitrary scoped URLs still fail.

After staging the validated build, the complete suite reproduced and narrowly repaired:

- exact-parity accounting in `scripts/audit_f89bb1f8.py`: retained rows may equal the common primary count plus distinct reviewed supplements; unexplained extras and primary disagreement still fail;
- disclosed-partial assertions in `tests/test_session_75ebd2d6.py` and `tests/test_session_fe7f5de4.py`, without deleting ID-set or row-coverage assertions;
- a hard-coded `23 Oct` phone-strip assertion in `tests/test_session_f89bb1f8.py`, now derived from the first pick's UTC start; and
- the independent `0cc1138a` arithmetic replay, which now recognizes `HLTV Valve ranking (Valve points)` evidence and independently recomputes it from the two archived Valve point values, fixed rating deviation 75 and slope 0.7986. Altered mirror calibration parameters are rejected.

No union row was dropped to restore a count, and no price, identity or freshness gate was relaxed.

## 6. Final integrated candidate verification

The staged candidate is `data/latest.json`, generated **2026-10-24T05:57:32.061308Z** from fixture evidence observed **05:53:56.542706Z**, built **06:04:34.297664Z**. It contains **89 rows: 25 open and 64 not open**. All 25 open rows have a pick and a two-team probability pair; none is unresolved. Method mix: **12 exchange, 2 exchange_wide, 2 bookmaker_fallback, 7 model_vrs, 2 model_vrs_mirror**. The one reviewed supplement is the ended 1083045 row described above.

Final local gates on the exact staged bytes:

- **1,211 unit tests passed**, one skipped.
- **9 source-audit tests, 5 integrity tests and 12 independent-C6 tests passed**.
- C6 row audit: **0 failures**. Independent `9b97d585` audit: **0 integrity failures**, 25/25 open rows fully resolved.
- Independent `0cc1138a` replay: **25/25 probabilities re-derived, 0 failures**.
- Independent `f89bb1f8` coverage audit: **25 future rows, 25 picks, 0 unresolved**, with reviewed supplement 1083045 accounted separately.
- Raw-byte inventory audit: **265 row/source comparisons and 6,360 retained non-crowd field comparisons, 0 mismatches**. All three 88-row primary responses are completely retained; only 1083045 is used from the 13-row supplement response.
- Build/root validators: **89 rows, 25 calculations, 15 pages, 818 internal links/assets, 20 checksums, 218 displayed rows**.
- All **8 browser suites passed**, including 32 viewport/accessibility scans, 320/390px first-screen pick/probability placement, navigation, filters, evidence anchors, internal links and exact expiry behavior.

Evidence files: `row-audit.md`, `independent-probabilities.json`, `raw-inventory-audit.json`, `final-verification.json`, and the four raw responses under `research/harvest-f533492a/sources/`. Capture 40067947765 is not misreported as a successful end-to-end run: it failed the old auditor after retaining the candidate. The repaired gates above were rerun locally, and a separate PR/Actions deployment plus public-byte verification remains required before any live-publication claim.
