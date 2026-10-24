# Publication-continuity audit — 2026-10-24T06:22:28+00:00

Verdict: **frozen** — the board the public sees is frozen

| Field | Value | Source |
| --- | --- | --- |
| published revision | `unreadable` | [build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) |
| published built_at | `unreadable` | [build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) |
| published snapshot | `unreadable` | [build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) |
| committed snapshot | `2026-10-24T05:59:34.228578Z` | [data/latest.json](https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/data/latest.json) |
| stated evidence TTL | `8 h` | [data/latest.json](https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/data/latest.json) |

## Findings

- **FROZEN** `receipt_unreadable` — the live build receipt exposes no readable snapshot_generated_at, so the published board cannot be shown to be current
- **PASS** `publish_chain_in_flight` — a pages.yml run is pending on main (https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40069834693)
- **PASS** `rows_sourced` — all 25 open rows carry an official hotspawn.com fixture link, at least one evidence URL inside the official-host allowlist, and a pick or a recorded reason
- **PASS** `picks_reproducible` — every published open-row pick is the larger of its own two probabilities, and each pair sums to 1.000 within 0.01
