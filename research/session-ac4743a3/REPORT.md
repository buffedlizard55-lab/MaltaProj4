# Session ac4743a3 — complete pick board and evidence-lifetime audit

## Scope and evidence

Hotspawn is **inventory only**. None of its crowd-pick percentages supplies a probability, a pick or a model input. The audit uses the real collector's dated official responses, not made-up fixtures. Synthetic inputs in the new unit/browser tests are explicitly test-only and never enter a published snapshot.

Initial independent refresh: [GitHub Actions 39703933769](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39703933769), `2026-10-22T01:12:34.309670Z`, snapshot SHA-256 `61c08444a2a51f47670fe0f2aa660f5a600ae0df2eaf684b801b91eadb8ed1a8`.

- All three Hotspawn views agree on **97 CS2 records**. Past timestamps are not proof of a completed result; 62 records are simply not open for picks by their sourced start/lock.
- **35 open, 35 supported picks, 28 with probabilities:** 7 accepted exchange lines, 1 accepted Pinnacle line and 20 explicitly labelled original VRS estimates. **Seven qualitative picks have no percentage or fair odds.** No unsupported numeric value is filled in.
- [Independent row audit](capture/row-audit.md): 97 checked, **zero arithmetic/field failures**. [Exact-primary-input audit](capture/primary-inventory-audit.json): all 97 retained API records and all **2,328 non-crowd input fields** match the retained official response byte for byte after JSON decoding. This is not a claim that a schedule proves a match result.
- [Evidence index](capture/evidence-index.json) maps official URLs, observation times and SHA-256s to deterministic compressed **exact HTTP response bodies**, not rewritten excerpts. [Coverage report](capture/coverage.md) lists each open match, source attempts, accepted method and limitation. [Snapshot](capture/snapshot.json) and [counts](capture/counts.json) are replayable offline.
- A legacy `verification-95b588c2/audit_snapshot.py` wrapper was also tried. It predates qualitative picks and asserts that every unpriced row has no pick, so it is not suitable for the current supported tiers. It was **not weakened or used to certify this snapshot**. The current independent `verification-c6` auditor and production validators both reproduce all 28 probabilities.

## Verified defects fixed

1. **Incomplete Picks page:** the old page selected only numeric rows, omitting supported qualitative picks and unresolved entries. It now publishes **exactly every open fixture ID**, in chronological order, with research-only/unresolved limitations visible. The validator enforces this equality; it no longer treats missing open rows as acceptable. The home link count includes the entire board, not just priced rows.
2. **Indefinite qualitative picks:** research picks previously had no finite recommendation deadline. They now expire at the minimum of the eight-hour inventory/evidence window, actual HLTV/VRS research observation, start and lock. Missing/malformed/future research observation fails closed. A stale build clears the pick instead of baking it into new HTML.
3. **Stale phone recommendations:** the previous expiry script cleared desktop rows but could leave a team, probability and bar on a phone card, and left queue research picks active. Desktop, phone, queue and hero now share deadlines; picks and percentages are withheld together. Live counts update, including research-only counts. A static historical coverage sentence no longer claims to be a current-time guarantee.
4. **Misleading phone navigation:** only a genuinely matching bottom-tab destination receives `aria-current=page`, rather than Home being highlighted on unrelated pages.
5. **Unrelated retained book reads:** only open, unpriced, non-conflicting fixture IDs enter retained-listing HTTP re-observation. Historical/resolved/removed fixtures do not spend the refresh budget on unrelated blocked pages. The exact-pair/start/format/two-way-price gates are unchanged.
6. **Wrong Zetta citation:** `2399867` serves Alliance–FaZe despite its plausible Zetta slug. The shared identity register and rendered review note now cite **2399865**, and the Swiss round is **5**, not 3. The pre-match 22:00Z schedule is explicitly distinguished from the completed page's 22:10Z start and 0–2 result; old quotes are not renewed.
7. **Inconsistent Off Chops prose:** Valve's 971 vs 878 points reproduce **Off Chops 60.2% / Ground Zero 39.8%**, not the old 59.1/40.9 note. The live review note is corrected. The stand-in's numerical impact is unknown and is no longer guessed; a collection failure no longer claims that no sportsbook has opened a market.
8. **Live-snapshot CI whitelist:** the fresh 97-row snapshot exposed three failures in an inherited shared test that allowed neither the existing `bookmaker_fallback` method nor existing two-sided `research_rank` method. After an explicit stale-owner scope handoff in `COORDINATION.md`, the whitelist now includes those documented tiers. Pick membership, probability sum and unsupported-method assertions are preserved. Published data was not changed to appease an old test.

## Seven blank percentages — independently checked, not guessed

Only fixtures unresolved by the featured methods enter HLTV/book research. HLTV came first; the real refresh then inspected Pinnacle, wide exchange candidates and book access. Each fixture retains those attempts and the source URLs.

| Fixture | Supported qualitative pick | Why no numeric line is published | Primary review link |
| --- | --- | --- | --- |
| 1081869 Morningstar–NEXVOID | NEXVOID | One published HLTV world-rank side; Morningstar absent from the selected Valve file; no accepted two-way market line | [HLTV](https://www.hltv.org/matches/2399584/morningstar-vs-nexvoid-macemedia-void-autumn-cup-2026) |
| 1081597 benched gods–TitanFlow | benched gods | One-sided Valve presence with confirmed team-page roster; HLTV bracket slot is postponed/unnamed, and the exchange calls its opponent MORROW, an unconfirmed alias | [HLTV bracket slot](https://www.hltv.org/matches/2399696/cct-2026-challengers-europe-series-8-lower-bracket-round-3-2-cct-2026-challengers-europe-series-8) · [official market 6028868](https://gamma-api.polymarket.com/markets/6028868) |
| 1082769 K27–NEXORA | K27 | NEXORA lacks the required official dated points; current HLTV VRS rank #282 is not a points value in the selected file | [HLTV](https://www.hltv.org/matches/2399846/nexora-vs-k27-winline-mpkbk-cis-lan-season-9) |
| 1079654 ex-Zero Tenacity–ex-RUSTEC | ex-Zero Tenacity | Two equally matching ex-RUSTEC rosters prevent unique model inputs; ranking-order only | [HLTV](https://www.hltv.org/matches/2399331/ex-zero-tenacity-vs-ex-rustec-cct-2026-europe-series-11) |
| 1081149 FORZE Reload–LFO 10 | FORZE Reload | One published HLTV world-rank side; LFO 10 absent from the selected Valve file | [HLTV](https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12) |
| 1081150 ex-RUSTEC–Saint Sinners | ex-RUSTEC | The same ex-RUSTEC roster ambiguity; two HLTV ranks support only a qualitative order | [HLTV](https://www.hltv.org/matches/2399500/ex-rustec-vs-saint-sinners-cct-2026-europe-series-12) |
| 1082860 FlyQuest–Staqued | FlyQuest | Staqued is explicitly unranked on HLTV and absent from the selected Valve file | [HLTV](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026) |

Official Valve input: [pinned 5 October standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md). The published current ex-RUSTEC lineup shares three players with **each** of the #92/1066-point and #152/824-point rows. Selecting either row because it gives a convenient probability would violate the model's identity rule. The tie remains blocked.

The MORROW market is **not transferred** to benched gods merely because TitanFlow and the start slot match. Primary confirmation was not found. Third-party rename suggestions are not registered as aliases. A wide spread is not repaired by inventing a midpoint consensus.

### Collection limits

- The seven retained HLTV pages did not expose an accepted numeric two-way line. Their rankings support order, **not a calibrated chance of victory**. Promotional casino cells and crowd votes are not odds.
- Pinnacle's official current fixtures/lines provided no exact pair/start for the seven. An available FORZE–Just Players listing is a different opponent/date and is rejected.
- Thunderpick's public CS2 page is JavaScript-driven; the automated response was a shell. A separate rendered read did not resolve these seven. This is **not evidence that Thunderpick offers no odds**.
- GG.BET explicitly refuses the visiting region. That restriction is respected, not bypassed. Historical EGamersWorld 403 responses likewise do not prove market absence.
- The archived model input is the official **5 October** file, not a claim about today's Valve points. Every model row is an original estimate, not a book quote or a proven calibrated forecast.

## Verification and publication

Final local integration gates so far: **625 unit tests green**, including the shared whitelist correction and two source-correction regression tests. Independent suites: 9 audit tests, 5 integrity tests, 12 independent-auditor tests. Build validation reproduces all 28 numeric lines, covers 15 pages, 922 links/assets, 20 checksums and 284 rendered match rows. Browser checks cover 32 page/viewport scans (320/390/768/1440px), subpath URLs, accessibility, filters, legacy redirects and **19 expiry scenarios**. These are measured test results, not an esports accuracy claim.

A final post-commit refresh, complete gate run, PR/merge and live-byte verification are still in progress. Their exact result will be appended here and to the coordination board; no deployment success is claimed before the live gate passes.

## Remaining Flagged for Review — not merge blockers

- Seven blank percentages, the postponed/renamed slot and ambiguous ex-RUSTEC roster, documented above and on the site's review/unresolved pages.
- During integration, the newly merged session-6d00dce8 report's rough FlyQuest points/rank were also flagged: the pinned 5 October file is #86 / 1093 points, not the report's estimated ~1315. Different ranking dates/fields are not interchangeable, and the approximation is not a model input. The other session's receipt is preserved.
- The inherited dated `research/session-db1f35c5/REPORT.md:18` still contains the old Off Chops prose; it is preserved as another session's receipt, not used for any published calculation. The **rendered shared review note is corrected**. The older session-4901f43e auditor also lists 15 historical identity citations it did not itself read; that warning is not a finding that they are false. Its current replay reports **72 passed, 0 failed, 2 advisory warnings**. This session does not claim a new live verification of every historical alias in the repository.
- GitHub Pages is still configured `legacy`, `main:/`. The official API source-change request returned **403 `Resource not accessible by integration`**. Artifact deployment, automatic freshness watchdog, guarded root fallback and exact live-byte verification remain enabled. The permission limit is disclosed rather than reported as fixed. Both dated root and artifact copies enforce recommendation expiry, and GitHub schedules remain best-effort, not a guaranteed SLA.
