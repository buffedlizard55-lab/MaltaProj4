# Session fe7f5de4 — complete CS2 pick coverage and mobile access

**Status:** verified release candidate; PR, merge, and live-Pages receipt still pending. The dated runner harvest and retained receipts below supersede the historical starting-point audit.

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

### Sole remaining no-percentage row: FlyQuest–Staqued

Fixture **1082860**, FlyQuest vs Staqued, DFRAG Invitational 2026, starts at **2026-10-27T03:00:00Z**. The pick remains **FlyQuest** under `research_rank_single`; probabilities and fair odds remain blank.

The dated evidence supports that limitation rather than a number:

1. [HLTV fixture 2399890](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026) confirms the exact pair and start, lists FlyQuest at world #61, and gives Staqued no world-ranking number. Its numeric betting comparison is not a validated operator two-way series quote, and fan votes are excluded.
2. [HLTV's dated Valve-ranking mirror](https://www.hltv.org/valve-ranking/teams/2026/october/23) resolves FlyQuest but not Staqued. One-sided ranking/points evidence cannot originate a two-team probability.
3. [Polymarket market 6066520](https://gamma-api.polymarket.com/markets/6066520) is the exact DFRAG BO3 market but fails the quote gates. The first current probe retained 0.50/0.50 outcome placeholders, best bid 0.05, best ask 0.95, spread 0.90, and about $123.69 liquidity. A later independent sibling read retained 0.51/0.49 but best bid 0.07, best ask 0.95, spread 0.88, and $126.2095 liquidity. Neither midpoint nor last outcome price is publishable.
4. The Pinnacle guest moneyline feed contains no exact pair/start line. Stavka's discovered candidate URLs return 404; EGamersWorld and GG.BET return 403 in the runner. Thunderpick returns only an application shell; the retained browser attempt is a Cloudflare challenge with empty API capture. bo3.gg has no validated two-way quote. These are collection limitations, not claims that odds do not exist.

A second, independent run by session `f0814674` reached the same verdict at 04:59–05:04 UTC; its retained report is [`research/harvest-f0814674/unresolved-probe/REPORT.md` on commit `47f110e`](https://github.com/buffedlizard55-lab/MaltaProj4/blob/47f110e7456b6e1c81b2268d72bd818b7159bf2f/research/harvest-f0814674/unresolved-probe/REPORT.md). This session's duplicate queued probe (run 39903529164) is therefore not needed for the decision. The integration token cannot cancel Actions runs (HTTP 403), so any eventual evidence commit will be reconciled without replacing a newer release.

### Mobile and executive-summary changes

The existing site was revised, not replaced:

- A visible first-screen `View updated picks →` CTA links directly to `picks.html`.
- Compact coverage facts precede the pick list. Methodology, coverage proof, and limitations remain in one native keyboard-accessible executive guide; existing deep links still reveal the relevant disclosure.
- At 320/390px, glance cards use a two-column team/probability grid and hide only duplicated source/timestamp prose, never a pick, probability, or limitation. The full source-linked board remains one tap away.
- Final measured home positions: CTA **y=396.6px**; pick-list heading **625.6px at 320px / 581.6px at 390px**; first actual pick card **864.2px / 767.2px**. The starting 390px list heading was 1461.7px. All 30 open matches have home cards and full pick-board rows.

### Candidate verification

The exact promoted 92-row candidate was built to `public/`, validated, staged to the legacy root, and validated again:

- **92 rows** verified against the primary snapshot; **29 probability calculations** reproduced; **15 pages**; **839 internal links/assets**; **20 artifact checksums**; **231 displayed match rows**.
- **969 unit tests** passed (1 skip); 9 repository audit tests, 5 integrity acceptance tests, and 12 C6 auditor tests passed.
- All five browser suites passed: 32 page/viewport accessibility/no-overflow scans, expiry/lock/quote cases, legacy deep links, native keyboard disclosures, and the new 320/390px all-open-row pick/probability/source/blank checks.
- Independent auditors: C6 **0 failures**; 7271 **0 errors**; 767649ba **2,590 checks / 0 failures / 0 advisories**; 80504414 **1,917 checks / 0 failures**; 2ec8cd6c **300 checks / 0 failures**; 86b56cf6 and 7601d5ee **status ok**. Receipts are retained under `research/session-fe7f5de4/`.
- Published-claim auditor 4901f43e: **67 passed / 0 failed / 2 warnings**. One warning locates a stale Off Chops figure only in another session's historical report; the current board and rendered review note use the corrected value and the dated approximation note remains on Flagged for Review. The other says 17 historical identity citations were not re-read by that older auditor; this is explicitly not treated as fresh confirmation.

No unsupported probability was added. Deployment is not claimed until the PR merge and live-byte verification complete.
