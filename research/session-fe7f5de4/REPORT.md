# Session fe7f5de4 — complete CS2 pick coverage and mobile access

**Status:** PR #197 merged at `2026-10-23T05:41:12Z` (`3f6a3b6`). The 30/30 board is preserved by later merged sessions, but the independently read live site still served the older 29/30 `a030476` build during the publication race. A narrow verified-artifact publisher follow-up is in progress; no final live-byte receipt is claimed yet.

## Requested outcome

1. Discover every CS2 fixture currently listed by Hotspawn and recheck the inventory automatically.
2. Resolve each open fixture through the existing external-market path where possible. For only the remaining rows, research HLTV first and then esportsbook/listing sources. Hotspawn is never a probability input.
3. Publish an obvious pick and both teams' supported win probabilities. Where evidence cannot support a percentage or pick, leave the unsupported fields blank and publish a separate unresolved/limitations section linked from the executive summary.
4. Make the updated-picks destination and the unresolved section easy to find and read on a phone.
5. Replay every displayed value from retained evidence, flag irregularities, run all build/browser gates, and merge only a verified build.

## Starting-point audit (committed snapshot, not a new web observation)

`data/latest.json` says it was generated at **2026-10-22T20:15:52.839962Z**, with fixture evidence observed at **2026-10-22T20:12:15.855097Z**. It contains **84 retained rows and 23 rows marked open**. Of those 23, **23 have a directional pick and 21 have numerical probabilities**. The two research-only rows in this dated file are:

| Hotspawn fixture | Teams | Published method | Published limitation | Official fixture link |
| --- | --- | --- | --- | --- |
| 1081149 | FORZE Reload vs LFO 10 | `research_vrs_single`; pick FORZE Reload; no percentage | One-sided Valve standings evidence only; HLTV bracket slot lacked team labels, so club pages were used for roster identity | [Hotspawn fixture](https://www.hotspawn.com/matches/forze-reload-vs-lfo-10-cct-europe-2026-series-12-1081149) |
| 1082860 | FlyQuest vs Staqued | `research_rank_single`; pick FlyQuest; no percentage | One-sided HLTV world-ranking evidence only; no verified two-way line | [Hotspawn fixture](https://www.hotspawn.com/matches/flyquest-vs-staqued-dfrag-invitational-2026-1082860) |

These are historical file contents, not assertions that the matches are still open or that the same picks remain current. A fresh harvest must supersede them.

## Source order and acceptance rules

| Order | Source | Permitted use | Reject / flag |
| --- | --- | --- | --- |
| 1 | [Hotspawn CS2 lobby](https://play.hotspawn.com/cs2-pickems), [general lobby](https://play.hotspawn.com/lobby), and the fixture API used by those pages | Fixture membership, teams, competition, start/lock and official row link | Crowd percentages or any Hotspawn pick signal as probability; partial or wrong-game discovery replacing a good inventory |
| 2 | [Polymarket Gamma API](https://gamma-api.polymarket.com/sports) | Exact team-pair/start, two-sided series-winner prices with raw timestamps, spread and liquidity | Wrong market type, ambiguous identity, one-sided/equal placeholders, stale or illiquid quotes |
| 3 | [HLTV matches](https://www.hltv.org/matches), exact fixture pages and club pages | Exact identity, start, lineup and ranking context; HLTV's dated Valve-points view may feed the separately labelled originated VRS model | Fan votes, ranking order presented as a calibrated probability, numeric comparison rows not independently confirmed at an operator |
| 4 | [Pinnacle guest esports API](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight) | Exact two-way moneyline with reproducible fixture/market identity | Alias guesses, wrong start/format, absent timestamps or unmatched markets |
| 5 | Official bookmaker/listing pages already supported by the collector, including [EGamersWorld CS2 listings](https://egamersworld.com/counterstrike/matches), [Thunderpick CS2](https://thunderpick.io/esports/cs2-betting), and [GG.BET Counter-Strike](https://gg.bet/en/esports/counter-strike) | Only a validated, dated, two-sided series line bound to both labels; listing provenance must remain explicit | `1.8 / 1.8` and other placeholders, refused access treated as “no odds,” parsed values without a current source receipt |
| 6 | [Valve's official regional standings](https://github.com/ValveSoftware/counter-strike_regional_standings) and Valve's published model formula/calibration | Clearly labelled original model line only when both team identities and roster continuity resolve | Invented rank-to-probability conversion, one-team points presented as a two-team probability, ambiguous roster identity |

## Verification plan

- Preserve raw source receipts, observation timestamps and SHA-256 hashes in the dated harvest.
- Compare the complete Hotspawn ID set across API, CS2 page and lobby; do not confuse retained historical rows with currently open fixtures.
- Recompute every accepted de-vigged market probability and every VRS expected score from the stored inputs.
- Confirm every open row appears on the pick board; every no-percentage/no-pick row appears in both the executive-summary limitations and the dedicated unresolved page.
- Check every table row for an external source link and every generated internal link/asset.
- Exercise 320px and 390px phone viewports, keyboard/hash navigation, expiry behavior, accessibility and horizontal overflow.
- Record any contradiction or unverified item on Flagged for Review rather than filling it in.

## Fresh research results

### Dated inventory capture

GitHub Actions run [39902861458](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39902861458) completed successfully on commit `40c1946`. It refreshed the complete Hotspawn inventory, quarantined invalid rows, built a non-publishing candidate, and ran the independent C6 row auditor. The immutable handoff is:

- `research/harvest-fe7f5de4/refresh-snapshot.json`, generated **2026-10-23T04:58:44.267970Z** from fixtures observed **2026-10-23T04:55:05.613441Z**; pre-build SHA-256 `5bbf4ca1693c035d53d13b42c16194469a98b6312961eaa89b90348fbd6c0ecb`.
- `research/harvest-fe7f5de4/row-audit.md`: **92 rows checked, zero arithmetic/field failures**.
- Coverage is `api=92`, `page=92`, `lobby=92`, `retained=92`: all four inventory views agree. Of the 92 retained rows, **30 are open; all 30 have picks; 29 have numerical probabilities**. The other 62 are explicitly not open, not silently deleted.

The 30 open rows comprise **17 `exchange`, 2 `exchange_wide`, 9 `model_vrs`, 1 `model_vrs_mirror`, and 1 `research_rank_single`**. Hotspawn crowd data is absent from every probability ledger. FORZE Reload–LFO 10 moved from one-sided research to a replayable `model_vrs_mirror` line; BESTIA Academy–RED Canids Academy has an exact exchange line. Neither remains a coverage gap.

### Former sole no-percentage row: FlyQuest–Staqued (later resolved)

Fixture **1082860**, FlyQuest vs Staqued, DFRAG Invitational 2026, starts at **2026-10-27T03:00:00Z**. At the 04:58 capture, the pick was **FlyQuest** under `research_rank_single` and probabilities/fair odds were correctly blank for that dated evidence. This was not the final state: a later book-listing receipt was independently verified as described below.

The dated evidence supports that limitation rather than a number:

1. [HLTV fixture 2399890](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026) confirms the exact pair and start, lists FlyQuest at world #61, and gives Staqued no world-ranking number. Its numeric betting comparison is not a validated operator two-way series quote, and fan votes are excluded.
2. [HLTV's dated Valve-ranking mirror](https://www.hltv.org/valve-ranking/teams/2026/october/23) resolves FlyQuest but not Staqued. One-sided ranking/points evidence cannot originate a two-team probability.
3. [Polymarket market 6066520](https://gamma-api.polymarket.com/markets/6066520) is the exact DFRAG BO3 market but fails the quote gates. The first current probe retained 0.50/0.50 outcome placeholders, best bid 0.05, best ask 0.95, spread 0.90, and about $123.69 liquidity. A later independent sibling read retained 0.51/0.49 but best bid 0.07, best ask 0.95, spread 0.88, and $126.2095 liquidity. Neither midpoint nor last outcome price is publishable.
4. The Pinnacle guest moneyline feed contains no exact pair/start line. Stavka's discovered candidate URLs return 404; EGamersWorld and GG.BET return 403 in the runner. Thunderpick returns only an application shell; the retained browser attempt is a Cloudflare challenge with empty API capture. bo3.gg has no validated two-way quote. These are collection limitations, not claims that odds do not exist.

A second, independent run by session `f0814674` reached the same verdict at 04:59–05:04 UTC; its retained report is [`research/harvest-f0814674/unresolved-probe/REPORT.md` on commit `47f110e`](https://github.com/buffedlizard55-lab/MaltaProj4/blob/47f110e7456b6e1c81b2268d72bd818b7159bf2f/research/harvest-f0814674/unresolved-probe/REPORT.md). This session's targeted run [39903529164](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39903529164) subsequently completed successfully and is included: at 05:21Z it again found only fixture 1082860 unpriced, recorded 13 reads with raw-byte archives, and refused Polymarket at spread 0.90 / liquidity $123.6943. See `research/harvest-fe7f5de4/targeted/`. That run itself found no usable new line or points identity, and no cancellation is claimed.

**Final resolution after PR #200:** the merged tree added a dated EGamersWorld receipt for **1.001 / 12.0**. This session independently re-read both that exact page and bo3.gg after the runner 403 receipts; both currently render the same FlyQuest–Staqued BO3 winner line. Exact pair/start binding comes from HLTV, and independent decimal arithmetic produces **92.3006% / 7.6994%** (displayed **92.3% / 7.7%**), fair odds **1.0834 / 12.9880**, with an 8.2334% overround. The accepted method is `bookmaker_fallback`, not an exchange midpoint or ranking conversion. Aggregator/no-price-timestamp limitations and the rejected Polymarket quote remain flagged. The full dated read and arithmetic are in `flyquest-book-verification.md`; the earlier blank remains historical evidence, not the published final value.

### Mobile and executive-summary changes

The existing site was revised, not replaced:

- A visible first-screen `View updated picks →` CTA links directly to `picks.html`.
- Compact coverage facts precede the pick list. Methodology, coverage proof, and limitations remain in one native keyboard-accessible executive guide; existing deep links still reveal the relevant disclosure.
- At 320/390px, glance cards use a two-column team/probability grid and hide only duplicated source/timestamp prose, never a pick, probability, or limitation. The full source-linked board remains one tap away.
- Final measured home positions: CTA **y=396.6px**; pick-list heading **625.6px at 320px / 581.6px at 390px**; first actual pick card **864.2px / 767.2px**. The starting 390px list heading was 1461.7px. All 30 open matches have home cards and full pick-board rows.

### Candidate verification

PR #196 and its publisher were preserved during the first rebase. PR #200 then landed the new book receipt, parser/pipeline safeguards, and review flags before this PR merged. The final integration preserves all of that work and uses main's inventory snapshot generated **2026-10-23T05:22:51.144308Z** (fixtures observed **05:19:12.192777Z**), plus the independently verified dated book receipt and run 39903529164's receipts. Final coverage is **92 retained / 30 open / 30 picks / 30 numerical probability pairs / 0 current no-percentage rows**; methods are **18 `exchange`, 1 `exchange_wide`, 1 `bookmaker_fallback`, 9 `model_vrs`, 1 `model_vrs_mirror`**. Both sessions' 320px CSS safeguards and all coordination sections were explicitly unioned. The combined tree was rebuilt to `public/`, validated, staged to the legacy root, validated again, and re-audited; `audit-c6-final.md` records **92 rows / zero failures**. Earlier 04:58/04:59 and 29/30 states remain dated evidence, not claims to be the final coverage.

- **92 rows** verified against the primary snapshot; **30 probability calculations** reproduced; **15 pages**; **830 internal links/assets**; **20 artifact checksums**; **230 displayed match rows**.
- **987 unit tests** passed (1 skip); 9 repository audit tests, 5 integrity acceptance tests, and 12 C6 auditor tests passed. This combined head preserves session f0814674's completed patches from `4940873` (research-tier test invariants) and `82cfb60` (runtime completeness prose), with attribution; it does not fork or discard that work.
- All five browser suites passed: 32 page/viewport accessibility/no-overflow scans, expiry/lock/quote cases, legacy deep links, native keyboard disclosures, the new 320/390px all-open-row pick/probability/source/blank checks, and stale-prose/counter agreement on both summary pages.
- Independent auditors: C6 **0 failures**; 7271 **0 errors**; 767649ba **2,575 checks / 0 failures / 0 advisories**; 80504414 **1,921 checks / 0 failures**; 2ec8cd6c **302 checks / 0 failures**; 86b56cf6 and 7601d5ee **status ok**; 071642e7 **15 pages / 511 rendered table rows / 0 errors**. Receipts are retained under `research/session-fe7f5de4/`.
- Published-claim auditor 4901f43e: **67 passed / 0 failed / 2 warnings**. One warning locates a stale Off Chops figure only in another session's historical report; the current board and rendered review note use the corrected value and the dated approximation note remains on Flagged for Review. The other says 17 historical identity citations were not re-read by that older auditor; this is explicitly not treated as fresh confirmation.

No unsupported probability was added. Deployment is not claimed until the PR merge and live-byte verification complete.

## Merge and publication follow-through

PR [#197](https://github.com/buffedlizard55-lab/MaltaProj4/pull/197) merged at **2026-10-23T05:41:12Z**, merge commit `3f6a3b60ba94d8613b79dd647fd837022ece7979`, from final head `fe7ff94f09e34ef668445bc22cc6ea24c5cda9e8`. PRs #198, #203, #205 and #201 subsequently merged additively. In particular, #203 added a separate NEXVOID–Alter Ego book receipt, moving the integrated method mix to **18 strict exchange / 1 wide exchange / 2 bookmaker listings / 8 VRS / 1 VRS mirror**, while retaining FlyQuest–Staqued at **92.3% / 7.7%** and this session's mobile UI.

Publication did not immediately follow the merge:

- Live `build-info.json` still identified **`a030476337786184ca52f5c1e095744b756d96f3`**, built `2026-10-23T05:22:51.477590Z`, and the live executive summary reported **30 picks / 29 with a win probability**. This is the outgoing PR #196 build, not the final result.
- Main run [39907133618](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39907133618) passed unit, refresh, quarantine, independent row audit, build/validation and browser gates. It then exhausted the legacy `main:/` root rebase/push retries after newer main commits and stopped before uploading/deploying its verified Actions artifact.
- Legacy runs 39907133743, 39907586829, 39908167220 and 39908775847 were **cancelled as superseded**, not treated as successful or as test failures. The last had built and reported successfully, but its queued deploy was cancelled when PR #201 advanced main at 06:10Z.

The follow-up changes only the publisher's final three-retry failure handling and its own regression test. All source, arithmetic, build, validation, unit and browser gates remain blocking; there is no step-level `continue-on-error`. Only an exhausted root **push race** becomes a warning, allowing the already-verified Actions artifact to deploy while the newest root publishes independently. No older root is force-pushed over a newer main and no source observation or probability changes.

Before this publisher-only edit, the integrated main candidate passed **1,002 unit tests / 1 skip**, C6 with zero failures, root validation (**92 rows / 30 calculations / 15 pages / 828 links/assets / 20 checksums / 229 displayed rows**) and the independent 071642e7 audit (**515 table rows / zero errors**). Final PR-head CI and public bytes will be recorded separately only after they actually succeed.
