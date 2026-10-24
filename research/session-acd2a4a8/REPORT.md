# Session acd2a4a8 — picks for every Hotspawn CS2 match (2026-10-24)

## What was wrong

The live board had been frozen at the 2026-10-24T08:06:51Z snapshot. At
16:07Z the independent audit (`gh run view 40110028068`) measured the live
snapshot 29,041 seconds old, outside its 8-hour window, with **0 actionable
picks**. The last scheduled publisher run (40097410704) passed refresh,
build, the independent audit and the browser suites, then failed at its
final *legacy root-fallback* gate.

This sandbox cannot reach Hotspawn/HLTV/Polymarket/Pinnacle (egress is
github/pypi/npm only, and Actions log/artifact hosts are also outside the
allowlist), so the failure was reproduced with the repo's established
non-publishing harvest pattern: `.github/workflows/harvest-acd2a4a8.yml`
refreshes on a GitHub-hosted runner, replays the publisher's exact staged
root gate, and commits receipts to `research/session-acd2a4a8/`.

## Root cause (measured, harvest run at 16:30Z)

Fresh snapshot: 83 feed rows, 22 open, 21 with a pick. One row —
**1079200, Color vs ex-Zero Tenacity** (NODWIN Clutch Series #13,
2026-10-25T18:00:00Z) — carried a newly opened Polymarket market
(6072812, https://polymarket.com/event/cs2-color-zerote-2026-10-25) priced
0.5/0.5, bestBid 0.49 / bestAsk 0.51, volume null. The collector published
`probabilities [0.5, 0.5]`, `pick None`, "Equal verified prices; no
directional edge." The board contracts forbid exactly that state (a priced
row must carry its larger side as pick; a 50/50 is never a published
probability), so the staged-root replay failed with **42 unit failures +
3 errors**, all tracing to this row or to dated fixtures that had rotated
out of the feed. One such row therefore blocked publication of every pick.

## Fix

Policy (extending session ce45f672's wide-tier rule to every tier): an
exactly even line is **rejected evidence, not a published probability**,
and the fallback ladder continues — HLTV first, then Pinnacle/esportsbook
lines, researched book listings, our originated VRS model, the HLTV Valve
ranking mirror, and the HLTV research tiers (ranking, one-sided standings,
recent form). The rejection and its reason stay on the row's attempts.

- `scripts/core.py` — `resolve()` rejects an exactly even quote at any
  tier; `book_research_pick()` does the same for researched listings.
- `scripts/vrs.py`, `scripts/vrs_mirror.py` — equal Valve points publish
  no model line; research tiers can still originate a pick.
- `scripts/build.py` — methodology page now states this policy.
- Tests encoding the old pick-less 50/50 were updated with dated
  justification (`test_core`, `test_session_92e3275c`,
  `test_session_ce45f672`, `test_vrs_mirror_6dd6f287`); new coverage in
  `tests/test_session_acd2a4a8.py`.
- Dated-fixture tests that indexed the rotating snapshot
  (`test_session_35c6e1e9` fixture 1083121, `test_session_e9be3e6b`
  fixtures 1082859/1081152) now skip when the fixture has rotated out —
  the pattern `test_session_019a253a` already uses — instead of reddening
  the publisher's gate for every other row.
- Phone findability: on ≤650px cards the pick row now renders directly
  under the team names, ahead of the probability block. Measured at
  320px on the 16:46Z board: first pick y=863 → **y=660**, first
  probability y=718, both on the first 844px screen. Both stylesheet
  copies kept byte-identical; the root `build-info.json` checksum for
  `assets/style.css` was synced.

## Verification (final harvest, snapshot 2026-10-24T17:00:40Z)

- Coverage verified 83/83/83/83 (api/page/lobby/retained).
- **20 open matches, 20 with a pick, 20 with a win probability,
  0 research-only, 0 unresolved.** Methods: 12 exchange, 2 wide exchange,
  2 bookmaker, 3 VRS model, 1 HLTV mirror model. Fixture 1079200 resolved
  as **Color, 68.8%, `model_vrs`** after its even exchange quote was
  rejected (16:46Z board).
- Publisher root gate replayed on the fresh snapshot: unit **1,487 OK**,
  `scripts.validate` OK, audits OK (`research/session-acd2a4a8/root-*.log`).
- All 11 Chromium browser suites pass (`browser_rc=0`), including the
  executive-summary prose/counter agreement and first-screen phone pick.
- Independent row audit: `research/session-acd2a4a8/independent-row-audit.md`.
- Locally on the committed baseline: 1,487 unit tests OK,
  `scripts.validate --site .` OK.

## Flagged for review (non-blocking)

`acd2a4a8-even-line-fallthrough-2026-10-24` in `data/review-notes.json`:
a genuinely traded, liquid market that is truly even also falls through
now; its 50/50 is retained in the rejected-quote attempt record but not
displayed, and any pick comes from a lower, labelled tier.

## Cadence

Unchanged and already in place: `pages.yml` attempts publication four
times an hour and `refresh-watchdog.yml` checks the live receipt every
10 minutes (dispatches when the published snapshot is >90 minutes old).
With the root gate unblocked, the next main run publishes a fresh board;
the 4–8 hour promise is met by the publisher's own freshness gate.
