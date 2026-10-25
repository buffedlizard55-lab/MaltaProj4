# Independent deployment eligibility audit — 2026-10-25

## Reproduced defect and change

[Scheduled run 40193317196](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40193317196)
passed refresh and quarantine but failed build/row verification. The GitHub jobs API
reports the Pages artifact upload as skipped while the deploy job nevertheless ran.
Its exact-byte live verification failed. `always()` was correctly intended to tolerate
failures **after** upload (legacy root staging), but the freshness-intention output alone
did not prove an artifact existed.

The deploy job now additionally requires the upload step's exported `outcome` to be
`success`. Upload is still downstream of the existing row/source/link/browser gates.
A later staging failure can still deploy the already verified artifact; a failed
refresh/build/validation/browser/upload cannot. No source fact or probability changed.
Two regression assertions protect the gate and the post-upload recovery semantics.

## Verification and limitations

* Committed root validator: 79 rows, 18 probability calculations, 15 pages,
  751 internal links/assets, 20 checksums, 186 displayed rows checked.
* Existing unit suite: 1,606 tests passed, 7 skipped (before the two new tests).
* New deployment-gate tests: 2 passed.
* Audits: 9 passed; integrity: 5 passed; independent verification-c6: 12 passed.
* Browser suite against a newly generated build of the **expired** committed snapshot:
  final phone suite fails because the expired board correctly has no visible picks;
  no horizontal overflow at its three phone widths. This is NOT claimed as a passing
  full browser gate or a fresh publication.
* Direct esports/Pages hosts and Actions log-storage hosts are unavailable under this
  sandbox's network policy. No fresh direct-source verification is claimed here.

## Parallel work — do not duplicate

[Diagnosis run 40197480741](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40197480741)
from session 58354934 committed its receipts to its own branch. Its
[validator log](https://github.com/buffedlizard55-lab/MaltaProj4/blob/arena/58354934-maltaproj4/research/harvest-58354934/validate.log)
identifies the upstream freeze as `Model roster has no HLTV source on this row`.
Independent inspection of its snapshot identifies fixture 1086697, Projeto do KinGui
vs Yawara: the HLTV context uses Tropa do KinGui and explicitly maps it to the feed
label; the roster comparator uses literal labels. That session owns the targeted
scripts repair and fresh-data integration; this change does not modify that scope.
Its runner census reports 78 feed rows / 17 open / 17 picks / 17 probabilities, but
that snapshot has **not** passed the publication validator and is not promoted here.
