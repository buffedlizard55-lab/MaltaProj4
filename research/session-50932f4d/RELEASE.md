# Verified CS2 Scout release

**Live:** https://buffedlizard55-lab.github.io/MaltaProj4/
**Picks:** https://buffedlizard55-lab.github.io/MaltaProj4/picks.html
**Flagged for Review:** https://buffedlizard55-lab.github.io/MaltaProj4/review.html

## Final actual-public recheck — 18:29 UTC

[Readback 40120717059](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40120717059)
again passes public bytes, source arithmetic/clocks, all four actual-clock device
sizes, merge ancestry and all four public review rows. It observes revision
`1e1298f24486a209d77fe40e5139777be06414dd`, which includes the implementation
merge and is in main's ancestry. Inventory remains **81/81/81/81**; **19 picks
and probability pairs for 19 eligible open matches**, zero unresolved, 62 not
open. The newer snapshot completed **18:04:39 UTC**, with fixtures observed
**18:01:06 UTC**. Source errors: **0**; exact file hashes checked: **20**.

Six of 12 operator comparisons still match their captured inputs; six show
price movement. These remain dated estimates, not claimed current execution
prices. No new prices or observation clocks were written by the verifier.
The first remaining fixture's verified lock is **18:54 UTC**; this final run is
an actual-clock recheck, not evidence of an assumed 18:24 deadline crossing.
[Latest row ledger](live/40120717059/live-source-audit.md) ·
[Latest mobile receipt](live/40120717059/live-mobile.json) ·
[Latest revision binding](live/40120717059/revision-binding.json) ·
[Latest review proof](live/40120717059/review-presence.json).

Both implementation [#294](https://github.com/buffedlizard55-lab/MaltaProj4/pull/294)
and receipt/regression [#309](https://github.com/buffedlizard55-lab/MaltaProj4/pull/309)
are merged. #309's independent audit and full build/browser checks passed.
The initial delivery and recovery receipt below is retained as dated history.

## Initial delivery verification — 17:57 UTC

At **2026-10-24 17:57 UTC**, the actual public site contained:

| Check | Verified result |
|---|---:|
| Official API / page / lobby / retained inventory | 81 / 81 / 81 / 81 |
| Eligible open matches | 19 |
| Sourced picks and two-sided probability pairs | 19 / 19 |
| Unresolved picks at that check | 0 |
| Other retained, not-open fixtures | 62 |
| Market-derived / clearly labelled model estimates | 15 / 4 |
| Exact published file hashes checked | 20 |
| This session's review findings present in public table rows | 4 / 4 |

The source snapshot completed at **17:54:57 UTC**, with fixtures observed at
**17:51:18 UTC**. Counts are dated, not a promise that every fixture stays open.
Two fixtures disappeared from the official inventory relative to the earlier
83-row capture; those earlier receipts remain archived. Hotspawn is used for
membership and schedules, never for probability or crowd-vote calculations.

The actual-device-clock browser check passed at **320, 390, 768 and 1440px**.
On the 320×568 phone, the first pick and both percentages occupy y=413–469,
above the tab bar at y=507. Links, expiry and freshness behavior passed.

## Delivery evidence

- [Implementation PR #294](https://github.com/buffedlizard55-lab/MaltaProj4/pull/294), merged as `a73f4ef3cbc0644852cd5f80be501a34ad50ab6f`.
- [Successful replacement publisher](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40117720878): build, strict staged-root gate and deploy pass.
- [Independent live verification](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40118330046): actual public bytes, source calculations/clocks, mobile behavior, merge ancestry and review presence all pass.
- Published revision: `0fc9719042366ed5cf4d95f1eb151fdc2f531a2c`, verified to include the implementation merge.
- [Row-by-row source ledger](live/40118330046/live-source-audit.md), [mobile proof](live/40118330046/live-mobile.json), [revision binding](live/40118330046/revision-binding.json), [published review proof](live/40118330046/review-presence.json), [machine-readable release receipt](release-receipt.json).

## Repairs and tests

The integration binds bookmaker readings to the right event, rejects conflicting
widgets or unjustified clock renewals, preserves genuine neutral evidence while
allowing supported later fallbacks, and isolates fixed historical examples from
a changing live board. Missing facts are not filled with invented percentages.

The first post-merge root gate exposed a separate test-isolation defect: a unit
fixture accidentally copied an existing runtime audit file. The exact failure
and uploaded artifact are retained. We adopted the completed upstream fix and
added a synthetic regression that reproduces the leak without touching real
source data, then verifies isolation, directory restoration and intact evidence.

**Final combined checks: 1,602 unit tests pass, 7 explicit historical skips,
and all 13 browser suites pass.** There are 25 focused regressions from this
session. [Unit log](release-unit.log) · [Browser log](release-browser.log) ·
[Reproduced environment failure](ambient-runtime-red.log) ·
[Passing isolated checks](ambient-runtime-green.log).

## Refresh and limitations

- Publication is scheduled to check every 15 minutes, with a **60-minute freshness budget** for scheduled runs; new revisions also publish. A separate watchdog checks every 10 minutes. GitHub's scheduling and upstream availability remain best-effort, not a guaranteed SLA.
- Twelve operator markets were independently rechecked: ten still matched the captured prices; Acend–UNiTY (1082996) and Infinite–BRUTE (1079199) had moved. The site publishes dated snapshot estimates, not guaranteed current ticks. No new prices are invented from those comparison flags.
- Three BO3.gg bookmaker listings are explicitly secondary evidence, **not direct operator confirmation**. Missing operator update times stay unverified.
- Four estimates are originated models, not official bookmaker prices or proven forecasts. The project's symmetric transformation is distinguished from Valve's published fit.
- The dated upstream prose/input mismatch is published on Flagged for Review, with a [correction request](https://github.com/buffedlizard55-lab/MaltaProj4/pull/284#issuecomment-6387046793). A separate [nonblocking diagnostic-order/text request](https://github.com/buffedlizard55-lab/MaltaProj4/pull/300#issuecomment-6387752015) is recorded without editing that owner's workflow.
