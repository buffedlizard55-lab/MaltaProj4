# Delivery audit — eaff7cce — 22 October 2026 UTC

## What was verified, and what was not

This is source/provenance and implementation verification, **not forecast accuracy**.
Hotspawn supplies inventory only. Crowd picks from Hotspawn, HLTV, EGW or an editorial
poll are not probability inputs. No unsupported percentage, player, alias or result
was filled in. Unknown probabilities and fair odds remain null/blank.

The [07:49:59Z capture](capture/snapshot.json), produced by the normal read-only
collector in [run 39742129915](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39742129915),
reconciles **107 API / 107 CS2-page / 107 lobby IDs**. The oldest contributing fixture
observation is 07:44Z, not the completion/attempt clock. [Primary inventory audit](capture/primary-inventory-audit.json)
compares **every retained non-crowd field of all 107 rows** to the exact official API
response. [Independent row audit](capture/row-audit.md): **zero failures**.
[URL/time/hash archive index](capture/evidence-index.json): 47 source checks, 40 exact
successful response bodies, no successful response missing its archive; errors and
host access refusals are retained. Exact bodies are compressed under `capture/raw/`.

At the observation clock:

| Inventory | Open | With a selected team | Numerical | Market / secondary listing | Originated official-file VRS | Qualitative only | Unresolved |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 107 | 46 | 45 | 39 | 27 | 12 | 6 | 1 |

Market split: 22 strict exchange, three wide-exchange/low-confidence, two researched
secondary listings. No HLTV Valve-mirror probability was accepted: that runner read
returned persistent 403. **61 records were not open by sourced timestamps/status**;
they remain in the inventory and are not asserted to be final results. Later builds
and browser clocks close further rows at their original start/lock/deadline, so
live counts correctly decrease from this dated table. Publication never renews a
quote or invents a newer fixture observation.

[Open-row source/probability/limitation table](capture/rows.md) and the complete
107-row independent audit provide the line-by-line accounting. The public pick
board includes all open rows, including research-only and unresolved entries;
All matches retains non-open rows. Every row links its official Hotspawn fixture
and its external probability/ranking input through the evidence ledger.

## Every remaining no-percentage fixture

The collector attempts strict exchange, **HLTV identity/context first**, Pinnacle,
wide exchange, esportsbook access and the researched-listing tier before model,
dated Valve mirror and qualitative tiers. A candidate label is not an alias.

| Hotspawn ID / fixture | Supported selection at 07:49Z | Why no probability / source |
| --- | --- | --- |
| [1082919 Projeto do KinGui–Martians](https://www.hotspawn.com/matches/projeto-do-kingui-vs-martians-cct-south-america-2026-series-7-1082919) | **Unresolved; blank** | [HLTV near match 2399904](https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7) and [exchange market 6033256](https://gamma-api.polymarket.com/markets/6033256) use **Tropa**, not Projeto. See conflicting rosters below. No global mapping or borrowed odds. |
| [1079654 ex-Zero Tenacity–ex-RUSTEC](https://www.hotspawn.com/matches/ex-zero-tenacity-vs-ex-rustec-cct-europe-2026-series-11-1079654) | ex-Zero Tenacity, ranking-only | [HLTV 2399331](https://www.hltv.org/matches/2399331/ex-zero-tenacity-vs-ex-rustec-cct-2026-europe-series-11): #67 / #70, BO3, no numerical betting pair. Strict/wide exchange gates fail; ex-RUSTEC duplicate Valve-roster overlap is ambiguous; EGW denied on runner, rendered 1.8/1.8 is rejected. STAVKA is an unaccepted lead below. |
| [1081149 FORZE Reload–LFO 10](https://www.hotspawn.com/matches/forze-reload-vs-lfo-10-cct-europe-2026-series-12-1081149) | FORZE Reload, one-sided ranking-only | [HLTV 2399499](https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12): FORZE #80, other side unranked in that world-ranking context. LFO absent from official Valve file; no numerical HLTV/Pinnacle pair. [EGW unnamed-opponent slot](https://egamersworld.com/counterstrike/match/HiXMAaC8L/forze-reload-vs-_04jKZ07_4) and 1.8/1.8 are not acceptable identity/price evidence. |
| [1081150 ex-RUSTEC–Saint Sinners](https://www.hotspawn.com/matches/ex-rustec-vs-saint-sinners-cct-europe-2026-series-12-1081150) | ex-RUSTEC, ranking-only | [HLTV 2399500](https://www.hltv.org/matches/2399500/ex-rustec-vs-saint-sinners-cct-2026-europe-series-12): #70 / #123; no numerical pair. Same ambiguous ex-RUSTEC model identity and weak exchange. [EGW 1.8/1.8](https://egamersworld.com/counterstrike/match/HiXMAaC8L/ex-rustec-vs-saint-sinners-qRkeIZuchq) rejected; STAVKA editorial is not odds. |
| [1082925 BESTIA Academy–RED Canids Academy](https://www.hotspawn.com/matches/bestia-academy-vs-red-canids-academy-cct-south-america-2026-series-7-1082925) | RED Canids Academy, ranking-only | [HLTV 2399910](https://www.hltv.org/matches/2399910/bestia-academy-vs-red-canids-academy-cct-2026-south-america-series-7): #184 / #170, no numerical betting pair. Wide-exchange ceiling fails; RED Academy absent from official Valve file. Main-team RED Canids is not substituted. |
| [1082926 Isurus–Hacha](https://www.hotspawn.com/matches/isurus-vs-hacha-cct-south-america-2026-series-7-1082926) | Isurus, ranking-only | [HLTV 2399911](https://www.hltv.org/matches/2399911/isurus-vs-hacha-cct-2026-south-america-series-7): #215 / #229; no numerical two-way betting pair. Hacha absent from official Valve file; exchange exceeds policy. Rank distance is not converted into a percentage. |
| [1082860 FlyQuest–Staqued](https://www.hotspawn.com/matches/flyquest-vs-staqued-dfrag-invitational-2026-1082860) | FlyQuest, one-sided ranking-only | [HLTV 2399890](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026): FlyQuest world #61, Staqued unranked in that context, BO3; no numerical pair. Staqued absent from official Valve file. [EGW 1.8/1.8](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3) rejected. |

For **each** row the retained attempts show no exact Pinnacle pair, Thunderpick's
accessible HTML without an extracted validated two-sided series quote, persistent
GG.BET 403, and the unavailable HLTV Valve mirror. These are collection limitations,
not claims that no bookmaker anywhere offers the match. No paid access, geoblock,
challenge or denied host was bypassed.

### Newly listed identity irregularity — not papered over

The official [Hotspawn Projeto team page](https://www.hotspawn.com/counter-strike/teams/projeto-do-kingui-205414)
currently renders brokeN, remix, cLd, Ltz and rw, with 2025 result history. The
[HLTV near-match fixture](https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7)
renders drg, ALLE, ckzao, xureba and lash, while its
[team overview](https://www.hltv.org/team/13151/tropa-do-kingui) says no active roster.
[EGW](https://egamersworld.com/counterstrike/match/0U32SId-H/projeto-do-kingui-vs-martians-esports-3j3hkufF0)
uses Projeto with the newer five but supplies placeholder odds. These are direct
rendered-page observations, distinguished from the complete collector capture;
matching an opponent/date does not resolve contradictory roster continuity.
No alias or lineup receipt was added. Finding `eaff7cce-projeto-martians-identity-2026-10-22`
is published on Flagged for Review and the unresolved row is counted in the summary.

### Targeted follow-up — successful capture, not automatic acceptance

[Run 39743815363](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39743815363)
completed successfully and returned commit `3260ee7`. All **six** accessible
response archives replay with both gzip and exact-body SHA-256 checks; the seventh
(EGW) remained HTTP 403 after the normal bounded waits. See
[targeted/report.json](targeted/report.json) and the explicit
[targeted-review.json](targeted-review.json). None of its seven targets is
implicitly accepted as a probability or alias.

The retained STAVKA Nuxt data now **does** confirm ex-Zero Tenacity–ex-RUSTEC,
`2026-10-23T08:00:00+00:00`, CS2 and BO3. Its promotional `maxBookmakerOdds.one_two`
contains Winline-attributed `w1=1.90 / w2=1.80`; the parallel match odds object
attributes the same pair to `stavkaTV`. This is secondary listing evidence, **not
an independently verified operator quote**. No price-update time or operator
availability is established. `updatedAt=2026-10-22T00:00:08+00:00` also appears as
the NewsArticle modification date and is not silently treated as an odds update.
The linked [Winline event](https://winline.ru/plus/16986733) rendered only a spinner
in the separate page-retrieval tool. The editorial **1.88 total-over-2.5** and
**3.25 exact 2:1 score** are not winner probabilities. This session adds no book
receipt from the promotional panel; a separately reviewed listing estimate from
another session must retain its secondary-source limitation rather than be
called verified operator odds. The Saint Sinners page has no bound two-way panel.

The archived Hotspawn and HLTV pages confirm the exact shared Projeto/Tropa
opponent, event and UTC start, but also preserve the old-profile/current-lineup
discrepancy described above. EGW's runner refusal does not negate the separately
observed rendered page, nor independently corroborate it. The **07:49 capture**
therefore remains immutable with one unresolved row. Concurrent identity evidence
and the final integrated publication are accounted separately below; historical
capture counts are not a permanent claim about what a later refresh can resolve.

## Demonstrated defects repaired without weakening the evidence policy

1. **Scheduled pre-refresh test expired an immutable historical capture.** The
   historical bf09 replay now validates at its captured clock. Concurrent main
   independently repaired the same line; its implementation was adopted verbatim.
   The live eight-hour TTL remains strict, including its exact boundary and future
   clock rejection; this session's tests cover both historical reproducibility
   and present-time refusal.
2. **Previously rejected listing URLs were never revisited automatically.** The
   bounded EGW watcher now reads known URLs for current unpriced non-conflicting
   fixtures before originating a model line. It requires exact identity/start,
   known format confirmation, label-bound asymmetric odds, margin gates, a fresh
   collector/cache-adjusted timestamp and retained response receipts. A rejection
   is not a price. The live run's 403 prevented a new accepted watcher line;
   unit-tested support is not claimed as a live coverage increase.
3. **Existing listing re-observation used run-start time.** It now preserves the
   collector's actual cache-adjusted `observed_at`; missing, invalid or old clocks
   cannot renew a receipt. Synthetic positive test readers were explicitly given
   their declared observation clock; original assertions remain intact.
4. **Freshness strip confused an attempt with fixture evidence.** It now uses
   `fixtures_observed_at` at the build clock, displays both clocks, fails closed on
   missing/malformed/future evidence and shares browser live-expiry counters.
5. **A11y green did not mean picks were discoverable.** A real 390×844 rendering
   put the first pick list at y=3186 and duplicated boards/evidence generated a
   40,000+px page. Native keyboard-accessible disclosures now fold duplicate
   guides, secondary tables and research ladders, without dropping a fixture or
   source. The first-screen 46px CTA stays visible. Every legacy hash target opens
   all ancestor disclosures and scrolls into view.

Verified browser measurements after the targeted layout change (current starts
may change row counts, not the structural budget):

| Viewport | Pick-board CTA y / height | First home pick list y | Home height |
| --- | --- | --- | --- |
| 320×568 | 413 / 46 px | 1409 px | 14901 px |
| 390×844 | 395 / 46 px | 1245 px | 12539 px |

No broad redesign: the original category pages, source tables, anchors, search,
filters, CSV/JSON, methodology and persistent five-tab phone navigation remain.
The bounded source probe is non-publishing and writes only this session's branch.

## Capture/audit failure accounting

First run 39741450689 failed before returning source evidence; an artifact was
uploaded. Second run 39742129915 successfully collected and independently audited
all 107 rows, then the new **reporter** failed because it applied the publication
contract directly to collector output, before the build derives `expires_at`.
The retained failure log is not hidden. Reporter replay now derives deadlines on
a copy via the exact production `pick_deadline` function: zero contract problems
at the observation clock. **The retained snapshot, original bytes and all source
observation/update clocks are unchanged.** Calculated deadlines and normalization
are explicit in [coverage-report.json](capture/coverage-report.json).

## Integration / verification / publication

Main advanced concurrently through PRs #167/#170/#171 to `35184b0`. Every other
session's coordination, notes, tests, research and the 07:42Z generated snapshot
were preserved in an additive merge; the equivalent historical-test implementation
was not duplicated. Final integration uses the newer 07:49Z verified capture,
rebuilds/validates the combined site, then stages the root fallback from that
hash-checked build. No source timestamp is changed to make it fresh.

Final pre-integration release checks: **819 unit tests**, including 35 own
regressions, and independent suites **9 + 5 + 12** pass. Root validator: **107 rows,
36 live calculations, 15 pages, 994 links/assets, 20 checksums, 292 displayed rows**.
The independent c6 row audit has zero failures; the 7271 audit reports 107 rows /
43 open / no errors; the 7676 audit completes **3,103 checks with zero failures or
advisories**. Full browser checks pass: 32 viewport/WCAG/overflow scans, seven board
and four quote-boundary cases, eight phone/queue cases and the own first-screen
CTA, legacy-hash, keyboard and unresolved-section regressions. Exact audit JSONs
are retained beside this report. These are passing local gates, **not** a claim
that the release has merged or deployed. Concurrent main changes will be preserved
and the combined tree reverified before publication.

PR/merge and actual live-byte receipts are recorded only after they complete.
