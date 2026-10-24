# Session 50932f4d — fallback evidence and release verification

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

## Verified release — 2026-10-24 17:57 UTC

**Delivered on [GitHub Pages](https://buffedlizard55-lab.github.io/MaltaProj4/).**
[PR #294](https://github.com/buffedlizard55-lab/MaltaProj4/pull/294) merged as
`a73f4ef3cbc0644852cd5f80be501a34ad50ab6f`. The actual public revision
`0fc9719042366ed5cf4d95f1eb151fdc2f531a2c` includes that merge.
[Replacement publisher 40117720878](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40117720878)
passes verify-build, the strict staged-root gate and deployment.
[Independent readback 40118330046](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40118330046)
checks actual public bytes, source arithmetic/clocks, four device sizes, merge
ancestry and all four published review entries — **all successful**.

Current-at-check official inventory parity: **81 API / 81 page / 81 lobby / 81
retained**. **19 open / 19 picks / 19 probability pairs / 0 unresolved**, with
62 retained not-open rows. Pricing comprises 12 operator-origin markets, three
explicit secondary book listings, three official-input models and one dated
HLTV mirror model. Snapshot generated 17:54:57Z; fixture observation 17:51:18Z.
The two IDs absent relative to the earlier 83-row capture are 1079661/1081154;
the earlier capture remains archived, not overwritten or relabelled current.

See [concise release report](RELEASE.md), [machine-readable receipt](release-receipt.json),
[actual public row ledger](live/40118330046/live-source-audit.md),
[mobile receipt](live/40118330046/live-mobile.json),
[merge binding](live/40118330046/revision-binding.json) and
[public review proof](live/40118330046/review-presence.json).

The first post-merge publisher's one failure was **test environment leakage**,
not a pricing defect: its harvester fixture read ambient `runtime/published-row-audit.md`.
Completed upstream `bf14ce5` isolates the test's working directory. We adopted
that fix rather than editing the owner's helper/test, and added a deterministic
synthetic regression in our own test file. It fails before the completed fix,
passes after it, verifies restoration of the caller's directory, and checks
that ambient evidence was not deleted to make the assertion pass. The final
combined branch passes **1,602 units (7 explicit historical skips) and all 13
browser suites**, including 25 own regressions. Full logs retain intentional
negative-test diagnostics; their overall unittest result is `OK`.

Limitations remain explicit: two of 12 operator price comparisons moved after
the capture (1082996/1079199); their archived values are not claimed to be
current ticks. Three book listings are not directly operator-confirmed. A
reproducible originated model is not a proven forecast. Cron is best-effort.
The dated #284 prose/input discrepancy and #300 diagnostic-upload ordering/text
request remain nonblocking review follow-ups; their owners' files are untouched.

All following candidate/diagnosis sections are **historical**, including files
named `final-*`; the actual delivery receipt is the `live/40118330046/` record
above. No source timestamps were advanced to conceal any failure.

## Historical integration status — 2026-10-24T17:04:53.547342+00:00

**Locally verified; own PR/public readback still pending.** The combined candidate
retains all **83** source fixtures. At **16:59:31 UTC**, **20** remain open and all
20 have a sourced pick and both win probabilities (**16 market-derived / 4
model-derived**); two more reached their verified lock times and remain visible
as not open. **1,514 unit tests and all 11 browser suites pass.** Three new
source-quality findings are rendered on Flagged for Review. See
[integration checks](integration-checks.json), [current-row source ledger](final-source-audit/source-audit.md),
[actual-clock coverage](final-coverage.json), [unit log](final-unit.log) and
[browser log](final-browser.log). This is not yet a claim that this branch is live.

## What was actually checked

This is a **dated audit**, not the current picks board. Use the site's
[executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/) and
[Updated picks](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html) for the
latest published snapshot. A local build is not proof of publication.

The shared [runner capture 40111409631](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40111409631)
observed Hotspawn fixtures at **2026-10-24 16:25:13 UTC** and completed at
**16:28:44 UTC**. We reused it rather than running another identical collector.
The [immutable captured snapshot](https://github.com/buffedlizard55-lab/MaltaProj4/blob/e42c1ecc59b3a5127c780d861f933ddbe14fb93e/research/harvest-2b856884/snapshot.json)
has SHA-256 `3f33d2b2f8ba8b636988cbebe9a995c659501029f0f07ff2e08a256f1ec3cadf`.

| Finding at that observation | Result | Source for manual review |
| --- | --- | --- |
| Inventory parity | 83 API / 83 CS2 page / 83 lobby / 83 retained records | [Hotspawn lobby](https://play.hotspawn.com/lobby), [CS2 page](https://play.hotspawn.com/cs2-pickems), [official fixture endpoint](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1) |
| Open matches | 22; the other 61 feed records are retained, not current recommendations | [Captured timestamps and raw fixture evidence](https://github.com/buffedlizard55-lab/MaltaProj4/blob/e42c1ecc59b3a5127c780d861f933ddbe14fb93e/research/harvest-2b856884/snapshot.json) |
| Numerical coverage | 22 two-sided probability estimates; 21 directional picks | [Every-row source ledger](captured-source-ledger.md) |
| Genuine equal line | Color–ex-Zero Tenacity: captured exchange 0.5 / 0.5; no supported favourite | [Operator market](https://polymarket.com/event/cs2-color-zerote-2026-10-25), [official Hotspawn fixture](https://www.hotspawn.com/matches/color-vs-ex-zero-tenacity-nodwin-clutch-series-13-1079200) |
| Primary / secondary / model distinction | 16 exchange lines (one explicitly wide), 3 bookmaker **listing** estimates, 2 official-file VRS models, 1 HLTV-mirror VRS model | [Row-by-row provenance and fallback attempts](captured-source-ledger.md) |
| Independent arithmetic and provenance replay | C6: zero failures; source-authority audit: zero errors | [Machine-readable audit](captured-source-audit.json), [verification receipt](verification-receipt.json) |

**No unsupported pick is added to close a count.** A genuine equal, sourced line
is not a fabricated 50/50 placeholder. Conversely, a source failure must not
become a made-up percentage. The two-sided estimate and the directional-pick
counts are distinct. The three BO3.gg listings confirm what BO3.gg returned,
not a fresh direct operator read; direct Thunderpick-price confirmation remains
unverified. Failed access is not evidence that a bookmaker has no line.

## Seven fallback rows, independently recalculated

These are the **16:28 UTC captured estimates**, not a new price observation. Only rows that the strict featured tier could not resolve were researched through HLTV and the later source ladder. HLTV supplied identity/context but zero extracted numeric quote rows for each of these seven records.

| Fixture (official inventory source) | Captured basis / inputs | Derived team probabilities (fixture order) | Limitation and supporting source |
| --- | --- | --- | --- |
| [Grêmio vs Yawara](https://www.hotspawn.com/matches/gremio-vs-yawara-cct-south-america-2026-series-7-1083123) | BO3.gg listing: 2.94 / 1.34 | 31.3% / 68.7% | Direct operator odds/update time unverified; these are de-margined listing estimates, not a fresh operator confirmation. [Input source](https://bo3.gg/matches/gremio-vs-yawara-esports-24-10-2026) · [HLTV identity](https://www.hltv.org/matches/2399915/grmio-vs-yawara-cct-2026-south-america-series-7) |
| [Spirit Academy vs LFO 10](https://www.hotspawn.com/matches/spirit-academy-vs-lfo-10-cct-europe-2026-series-12-1081156) | Originated model: 1042 / 819 points | 72.1% / 27.9% | HLTV dated Valve-ranking mirror, not the monthly official file or a market line. [Input source](https://www.hltv.org/valve-ranking/teams/2026/october/24) · [HLTV identity](https://www.hltv.org/matches/2399506/spirit-academy-vs-lfo-10-cct-2026-europe-series-12) |
| [Ground Zero vs Off Chops](https://www.hotspawn.com/matches/ground-zero-vs-off-chops-dfrag-invitational-2026-1082858) | Wide exchange: 27-point spread | 32.5% / 67.5% | Low precision: spread exceeds the featured gate. The market mid is not an assurance of the true win rate. [Input source](https://polymarket.com/event/cs2-gz1-offcho-2026-10-25) · [HLTV identity](https://www.hltv.org/matches/2399888/ground-zero-vs-off-chops-dfrag-invitational-2026) |
| [NEXVOID vs Alter Ego](https://www.hotspawn.com/matches/nexvoid-vs-alter-ego-dfrag-invitational-2026-1082859) | BO3.gg listing: 1.61 / 2.18 | 57.5% / 42.5% | Direct operator odds/update time unverified; these are de-margined listing estimates, not a fresh operator confirmation. [Input source](https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026) · [HLTV identity](https://www.hltv.org/matches/2399889/nexvoid-vs-alter-ego-dfrag-invitational-2026) |
| [FlyQuest vs Staqued](https://www.hotspawn.com/matches/flyquest-vs-staqued-dfrag-invitational-2026-1082860) | BO3.gg listing: 1.001 / 12 | 92.3% / 7.7% | Direct operator odds/update time unverified; these are de-margined listing estimates, not a fresh operator confirmation. [Input source](https://bo3.gg/matches/flyquest-vs-staqued-27-10-2026) · [HLTV identity](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026) |
| [HOTU vs The Huns](https://www.hotspawn.com/matches/hotu-vs-the-huns-moscow-cyber-games-2026-1082792) | Originated model: 1437 / 944 points | 85.2% / 14.8% | Official 5 October standings inputs; originated model, not market odds; roster continuity checked, forecast accuracy unverified. [Input source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) · [HLTV identity](https://www.hltv.org/matches/2399437/hotu-vs-the-huns-gluck-moscow-cyber-games-2026) |
| [5star vs 1WIN](https://www.hotspawn.com/matches/5star-vs-1win-moscow-cyber-games-2026-1082793) | Originated model: 1110 / 1383 points | 24.3% / 75.7% | Official 5 October standings inputs; originated model, not market odds; roster continuity checked, forecast accuracy unverified. [Input source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) · [HLTV identity](https://www.hltv.org/matches/2399438/1win-vs-5star-gluck-moscow-cyber-games-2026) |

## Narrow production repair

Only `scripts/books.py` changed in this session's source-adapter work. The
featured exchange tier, HLTV lookup order, bookmaker margin gates, model formula,
quote clocks and source data were not changed.

Reproducible defects in the previous generic listing parser:

1. It stopped at the first odds widget even when that widget belonged to an
   unrelated pair, suppressing a later valid labelled pair.
2. It assigned a `startDate` found within 400 characters of a name, even if the
   timestamp belonged to another JSON object. JSON key order or a long description
   could also hide a valid event.
3. Two contradictory labelled price pairs silently selected the first one.

The repair decodes one JSON-LD event, binds its start to that **same object**,
checks any stated home/away labels, supports escaped names and `@graph`, and
examines all widgets. Multiple event declarations or distinct matching prices
are refused. Repeated identical widgets for the single event are deduplicated.
Malformed/duplicate-key JSON, absent timezones, default odds, missing labels,
and expired/missing source observations remain refusals. STAVKA's existing
canonical Nuxt parser is unchanged.

**17 synthetic regression tests** cover these contracts; their Alpha/Bravo odds
are explicitly test-only, never research observations. All **1,501 baseline unit
tests pass (one skipped)**. This does not assert that an EGamersWorld live page
was reachable or that the repair changed any current probability; the three
listing rows in this capture came through the separate BO3.gg adapter.

## Official model inputs rechecked independently

We fetched the following directly from Valve's GitHub contents API. The official
repository head was `eec4853d7bcf0f1f7efe7f0d901234bef7e98b75`; hashes and links
are in [verification-receipt.json](verification-receipt.json).

| Input | Confirmed reading | Official source |
| --- | --- | --- |
| Global standings | The committed 5 October file is byte-identical to Valve's file, SHA-256 `df96e7fc3cd91a2687ec08cac0128e50cc4e4e55346581679572e881d79ae61b` | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |
| Points meaning | `Points` is printed from `glickoTeam.rank()` | [report.js](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/report.js#L98-L117) |
| Expected score | `Q = ln(10)/400`; Glicko `g` and logistic expected-score expression | [glicko.js](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/glicko.js#L54-L63) |
| Evaluation RD | Fixed RD 75 in the evaluation defaults | [fit.js](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/fit.js#L14-L18) |
| Roster continuity | At least three shared players | [team.js](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/team.js#L5) |
| Published fit chart | Visually read `y = 0.7986x + 0.126` from the fetched image | [modelfit.png](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/modelfit.png) |

**Model limitation:** the project applies the chart's slope symmetrically around
50%, i.e. an intercept of **0.1007**, not the chart's printed 0.126. This is the
project's disclosed model transformation, not an official Valve forecast or a
bookmaker's price. Reproducing the calculation does not validate predictive
accuracy for a specific low-tier fixture.

## Integration defects reported to the active owners

No publishing, refresh, build, CSS, or legacy verifier file owned by another
active session was edited for this diagnosis. A full staged-tree replay ran in
an ignored scratch copy using the shared fresh snapshot.

- It produced **42 failures and 3 errors**. Many legacy audits assume every
  priced row has a directional pick, incorrectly rejecting the genuine equal
  line. Two tests also select fixture IDs `1083121` and `1081152` from the rotating
  current snapshot after those fixtures have left the feed. The exact traceback
  evidence is in [staged-root-test-failures.txt](staged-root-test-failures.txt).
- The runtime summary says all 22 rows have picks despite the 21-pick count;
  the existing phone suite correctly catches it. The static limitations
  summary also confuses probability coverage with directional picks. Repair
  requested in `COORDINATION.md` for the owners of `scripts/build.py` and
  `site/assets/app.js`.
- On an expired build, `browser_019a253a.cjs` excludes the `none` ladder rung then
  expects the remaining sum to equal all open rows (0 versus 22). Honest missing
  evidence must not deadlock a repair PR.

The existing source/mobile verifier **passes** on the fresh local build at
320 / 390 / 768 / 1440 px: no horizontal overflow, in-site summary links,
one-tap match evidence, both team probabilities, distinct market/listing/model
labels and expiry. [Measurements](captured-mobile.json) use the snapshot clock;
they are **not live deployment proof**. Full browser publication checks remain
blocked by the summary discrepancy until the owning session's repair lands.

## Release status

The session's dedicated readback workflow is manual/explicit-marker only, never
scheduled. It reuses the existing independent public-byte/source auditor and
actual-device-clock mobile suite, writes dated receipts only to this fixed
branch, and checks that the public build includes the requested merge revision.
It neither changes picks nor deploys a site. Final PR and production verification
results are recorded below only after the relevant operations succeed.

## Subsequent completed-owner recovery (16:36 capture)

PR [#282](https://github.com/buffedlizard55-lab/MaltaProj4/pull/282) merged as
`ea4418c` after its audit and verify-build checks passed. Its nonpublishing
[capture](https://github.com/buffedlizard55-lab/MaltaProj4/blob/e9153c2bacb93594a8813efc3b11ac353cfcd363/research/diag-ac5bcb06/snapshot.json)
is generated **16:36:35.343927Z**, with fixtures observed **16:33:03.096322Z**,
SHA256 `8b3a48756701b7348c2a318624d7528f833ff5478d030024f409320a2c12af9d`.
Our independent C6 and source/arithmetic replays find zero errors: **83 retained,
22 open, 22 directional picks and 22 probability pairs** at its snapshot clock.

The formerly neutral Color–ex-Zero Tenacity market is still a real **50/50
market**, retained in rejected-quote evidence; it was not turned into a market
favorite. Further research now supplies a distinctly labelled **originated
Valve-input model**, **68.8395% / 31.1605%**, favoring Color. The official pinned
standings independently confirm **Color 1249 points** and **ex-Zero Tenacity
1066 points**, with the captured five-player lineups overlapping each official
roster five of five. Those inputs reproduce the estimate; they do not establish
its predictive accuracy or invalidate the neutral market view. The two source
kinds must remain distinct. This recovery capture is not proof of deployment.

[Durability request to the completed owner](https://github.com/buffedlizard55-lab/MaltaProj4/pull/282#issuecomment-6386834312):
tests of fixed historical prices must remain entirely archival when live prices
or evidence tiers rotate. Scope remains with #281; no competing test edits here.

## Residual neutral-model repair and integrated gate results

The independently sourced official-file and dated-mirror model tiers could
still stop on equal points with percentages but no pick. Five new synthetic
regressions reproduced this separate future publication risk. Both tiers now
preserve the complete neutral quote, identity inputs, original observation and
source in inspectable rejected/context evidence, leave recommendation fields
blank, and continue later research. A newer mirror may supply its own distinct
estimate; it cannot relabel the old neutral estimate or infer a winner. A
missing club or conflicting roster cannot produce neutral context at all.
The formula, nonneutral estimates, source clocks and no-overwrite gates are
unchanged. The legacy mirror test now asserts that exact evidence-preserving
contract, not a forced winner.

**22 session tests pass**, including the 17 parser cases and five model cases.
The combined baseline and real recovered staged-root gates each run **1,506
tests successfully** (one / seven documented skips respectively). The recovered
root reproduces **22 probability pairs across 83 retained fixtures**, with 15
pages, 788 links/assets, 20 manifest hashes and 195 displayed rows validated.
This is the independently replayed 16:36 capture, not a refreshed source read.

The full fresh browser chain subsequently exposed the same **320px picks-page
y=863** issue independently repaired by completed PR #281. That upstream layout
repair is being adopted rather than duplicated; final browser and actual-clock
public checks must still be recorded after integration.

## Historical test isolation completed

Two additional synthetic mutations leave the historical fixture IDs in the
rotating feed but change their evidence tier. The previously conditional archive
fallback then fails (one assertion failure, one indexing error). The two dated
alias/arithmetic cases now **always** use their genuine retained 08:06 source
rows. No current-board audit is weakened or switched to old data. The 24 session
tests and combined 106 parser/model/alias/arithmetic cases pass.

Completed upstream #281/#283 has now been merged into this fixed branch: its
source-context disclosure and exact y=863 mobile repair are adopted unchanged.
The next gate runs against that combined tree and its 16:40 source capture.

## Newly integrated prose discrepancy: correction requested

[Request to PR #284's owner](https://github.com/buffedlizard55-lab/MaltaProj4/pull/284#issuecomment-6387046793):
the review prose accompanying the 16:40 capture does not match two cited evidence
records. Ground Zero–Off Chops has a **26-point** spread and **6795.216** liquidity
in that capture (DFRAG Invitational 2026), not the stated 55-point / 1718.54
figures. Spirit Academy–LFO 10 uses the **24 October** HLTV Valve view,
**1042 / 819 points**, **#99 / #151**, not the 22 October / 810 / 597 / #120 / #217
prose. A missing label in the monthly file does not establish when a club joined
the ranking. The actual stored estimates and their arithmetic are not changed.
We did not edit the other owner's report, verifier or note without handoff.
