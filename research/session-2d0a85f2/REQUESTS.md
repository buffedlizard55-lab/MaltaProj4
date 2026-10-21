# Session 2d0a85f2 — change requests for shared / other-session outputs

Logged here instead of editing files this session does not own (coordination rule).
Session 96ea1af8 owns `scripts/build.py`, `site/assets/style.css`, `site/assets/app.js`, the root staged
`*.html`, `README.md` and the `pages.yml` branch trigger while its claim is live. Pick-table data
(`data/*.json`, `data/matches.csv`) is a shared output, changed only by the final integration session —
which this session will run once 96ea1af8's tasks are done (or handed over per the 60-minute stale-claim rule).

| # | Request | Target file(s) | Evidence | Why it is safe |
| --- | --- | --- | --- | --- |
| R-1 | When a fixture's HLTV page has no lineup, let `research_vrs_single` consult `data/vrs-anchors.json` for an official-HLTV-played-match lineup before declining (exact roster overlap under Valve's own ≥3 rule; still pick-only, never a percentage). | `scripts/refresh.py` (lineup lookup), new `data/vrs-anchors.json` | receipts R1, R5, R6, R7; `research/session-2d0a85f2/anchors.json`; tests `tests/test_session_2d0a85f2.py` | Fail-closed validation in `scripts/apply_2d0a85f2.py`; no price, no alias, no fuzzy match; only unblocks row 1081597 which currently shows NO pick. |
| R-2 | Run `python -m scripts.apply_2d0a85f2 --apply` at integration to install the anchor and the five Flagged-for-Review notes. | `data/vrs-anchors.json`, `data/review-notes.json` | this session's receipts | Idempotent; dry run by default; unit-tested. |
| R-3 (optional, corrected) | Add an `identity_source` column to `data/matches.csv` carrying `hltv_context.source` (official HLTV match URL) so the CSV alone shows the identity link of research-only rows. NOT a requirement fix: re-verification showed the CSV `source` column already carries the official Hotspawn URL on every row and the HTML tables already link HLTV for research rows (`scripts/build.py` 107-108, 804). | CSV writer in `scripts/build.py`, `tests/` CSV schema assertions | FINDINGS I-4 (corrected) | Additive column; every existing consumer keeps working; schema tests updated in the same change. |
| R-4 | Extend the executive summary's "Unresolved picks & their limitations" block with this session's dated limitations: Thunderpick carries no DFRAG or benched-gods/TitanFlow line (bo3.gg affiliate rendering shows lines for control fixtures), Kalshi's CS2 series has zero open markets, GG.BET 403, the HLTV start conflict (1081597) and the 22:00Z CCT SA identity conflict (1082837). | `scripts/build.py` summary section, `README.md` | receipts R2, R4, R8, R10, R11 | Text only; every sentence already has a linked receipt. |
| R-5 | Keep the phone-first nav: verify on 320/390px that the unresolved section anchor `#unresolved-summary` is reachable from the executive summary in one tap (browser tests already assert anchors; add this id to the assertion list). | `tests/browser.cjs`, `site/assets/app.js` if needed | user brief (mobile discoverability) | Test-only change unless an assertion fails. |

## Sequencing

1. 96ea1af8 completes and merges (or its claim goes stale ≥60 min with no commits → handover logged in
   COORDINATION.md).
2. This session rebases on merged `main`, applies R-1 (code) and R-2 (data), rebuilds, re-verifies line by line
   (`scripts.validate`, `verification-c6`, browser suite), then R-3/R-4/R-5 as needed.
3. PR to `main`, merge, confirm the Pages deploy and live bytes, record everything in COORDINATION.md.
