# Publication-continuity audit — 2026-10-24T06:02:29+00:00

Verdict: **frozen** — the board the public sees is frozen

| Field | Value | Source |
| --- | --- | --- |
| published revision | `unreadable` | [build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) |
| published built_at | `unreadable` | [build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) |
| published snapshot | `unreadable` | [build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) |
| committed snapshot | `2026-10-23T11:47:19.504519Z` | [data/latest.json](https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/data/latest.json) |
| stated evidence TTL | `8 h` | [data/latest.json](https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/data/latest.json) |

## Findings

- **FROZEN** `receipt_unreadable` — the live build receipt exposes no readable snapshot_generated_at, so the published board cannot be shown to be current
- **FROZEN** `publish_chain_red` — 5 consecutive failed pages.yml runs on main on one unmoved commit 5d56f35e; publication is not advancing; failed step(s): Unit and independent failure-mode tests (verify-build)
  - run: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40062143026
  - run: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40042111432
  - run: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40025828846
  - run: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39998307424
  - run: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39956197341
  - run 40062143026 failed step: `Unit and independent failure-mode tests (verify-build)` (GitHub jobs endpoint)
  - run 40042111432 failed step: `Unit and independent failure-mode tests (verify-build)` (GitHub jobs endpoint)
  - run 40025828846 failed step: `Unit and independent failure-mode tests (verify-build)` (GitHub jobs endpoint)
  - run 39998307424 failed step: `Unit and independent failure-mode tests (verify-build)` (GitHub jobs endpoint)
  - run 39956197341 failed step: `Unit and independent failure-mode tests (verify-build)` (GitHub jobs endpoint)
- **PASS** `rows_sourced` — all 27 open rows carry an official hotspawn.com fixture link, at least one evidence URL inside the official-host allowlist, and a pick or a recorded reason
- **PASS** `picks_reproducible` — every published open-row pick is the larger of its own two probabilities, and each pair sums to 1.000 within 0.01
