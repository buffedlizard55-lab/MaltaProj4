# Supplemental publication and unresolved-row review

- **Reviewed:** 2026-10-21, approximately 20:00 UTC
- **Repository branch:** `arena/be76b2d0-maltaproj4`
- **Current public source snapshot inspected:** 2026-10-21 19:57:45 UTC
- **Scope:** Independent check of the live executive summary, open-match inventory, published decisions and source-link trail; targeted follow-up on the remaining unresolved fixture. This supplements, rather than duplicates, the broader acceptance report in `verification-592ce4e8/ACCEPTANCE-AUDIT.md`.

## Publication and freshness

- Live dashboard: <https://buffedlizard55-lab.github.io/MaltaProj4/>
- Build receipt: <https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json>
- Updated picks: <https://buffedlizard55-lab.github.io/MaltaProj4/picks.html>
- Unresolved and non-market board: <https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html>
- Flagged-for-review page: <https://buffedlizard55-lab.github.io/MaltaProj4/review.html>

The live receipt now reports revision `47f230bd83c2626d818cee24f511dde97a7bcdd8`, built at 19:57:45Z from a 19:57:45Z snapshot, with 76 feed rows. This superseded the earlier 19:20Z/77-row snapshot after PR #114. Main run [39665584240](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39665584240) completed successfully at 19:59:09Z; verification, mobile/accessibility/expiry checks, deployment, and exact live-byte verification passed. The live snapshot is well inside the documented eight-hour evidence window. GitHub Pages remains `legacy`, sourced from `main:/` ([Pages status](https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages)); the legacy-source race remains a disclosed non-blocking configuration caveat.

### Earlier branch-only refresh (not production)

The active session 96ea1af8 refresh run [39664105574](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39664105574) retained a 19:47:12Z snapshot: 13 open fixtures, four with no probability, and `1081597` still the sole no-pick row. Its row-audit report checked 76 entries with zero arithmetic/field failures. The retained source audit says benched gods is ambiguous in the two duplicate Valve rows without a lineup, TitanFlow is absent from the 5 October file, and the current HLTV rank lookup did not establish a usable ranking pair. The same run's stored HLTV search/team probes returned HTTP 403, as did its sample direct page probes. Deployment was skipped on that feature branch. The later 19:57Z main refresh is the current public source of truth; the earlier branch artifact remains useful only as a research receipt.

The executive summary links directly to Updated picks and Unresolved & limits. Its Picks at a glance section lists all 13 open fixtures and links each match to its evidence-ledger anchor. The pick board displays both team probabilities where a numeric estimate exists, plus the originating market/model label. The mobile bottom bar links Home, Picks, Unresolved, Matches, and TWC. The merged acceptance report records the passing phone/tablet/desktop and accessibility checks; the follow-up main run also passed its browser/a11y/expiry gate.

## Open-row inventory as rendered on the live site

Every line below is linked to the live row evidence ledger. That ledger carries the fixture inventory link and the row-specific HLTV, Valve/model, or market evidence used by the dashboard. Values below are transcribed from the public executive summary/pick pages; they are not fresh independent probability calculations.

| Hotspawn fixture ID | Match | Published decision | Row evidence |
| --- | --- | --- | --- |
| 1082837 | Zetta vs LOS NINOS | Zetta — research-only; no probability | [Evidence](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-1082837) |
| 1081870 | Vitalem Aerem vs Rare Atom | Rare Atom — 59.0%, Polymarket wide line, low confidence (model comparison 69.0%) | [Evidence](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-1081870) |
| 1081597 | benched gods vs TitanFlow | Unresolved; no pick or probability | [Evidence](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-1081597) |
| 1081600 | Donstu vs Banda chuya | Banda chuya — 57.6%, Valve/VRS model | [Evidence](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-1081600) |
| 1082688 | Imperial vs Turma do Pagode | Imperial — 77.0%, external market | [Evidence](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-1082688) |
| 1082689 | BESTIA vs ShindeN | BESTIA — 52.5%, external market | [Evidence](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-1082689) |
| 1082882 | UNiTY vs Apogee Betclic | Apogee Betclic — 58.5%, external market | [Evidence](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-1082882) |
| 1082858 | Ground Zero vs Off Chops | Off Chops — research-only; no probability | [Evidence](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-1082858) |
| 1082859 | NEXVOID vs Alter Ego | NEXVOID — 68.2%, Valve/VRS model | [Evidence](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-1082859) |
| 1082860 | FlyQuest vs Staqued | FlyQuest — research-only; no probability | [Evidence](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-1082860) |
| 1082861 | Rooster vs Abyssal | Abyssal — 51.8%, Valve/VRS model | [Evidence](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-1082861) |
| 1082792 | HOTU vs The Huns | HOTU — 85.2%, Valve/VRS model | [Evidence](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-1082792) |
| 1082793 | 5star vs 1WIN | 1WIN — 75.7%, Valve/VRS model | [Evidence](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-1082793) |

This reconciles to the current live summary: 13 open fixtures; 9 numerical probabilities (4 market, 5 model); 3 research-only picks; 1 unresolved row. Hotspawn is used for fixture inventory, not as a probability source. The successful main run [39665584240](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39665584240) verified the newer snapshot, replayed row calculations and links, passed the phone/accessibility/expiry checks, and confirmed exact live bytes.

## New market observations in the 19:57 snapshot

The public refresh changed the evidence basis for two open rows since 19:20: Vitalem Aerem–Rare Atom now uses Polymarket market [6024922](https://gamma-api.polymarket.com/markets/6024922) at 41.0% / 59.0% (Rare Atom picked), and UNiTY–Apogee now uses market [6024716](https://gamma-api.polymarket.com/markets/6024716) at 41.5% / 58.5% (Apogee picked). The rendered table timestamps both observations at 19:52Z and shows their expiry. A direct API read of 6024922 after deployment returned the same 0.41/0.59 two-way `outcomePrices`, `active=true`, `acceptingOrders=true`, $1,003.57 liquidity, and best bid/ask 0.16/0.66 (a 50-point spread). That response carries `updatedAt=2026-10-21T19:58:56Z`, later than the 19:57:45Z build snapshot, so it corroborates the post-deploy market state but is not the exact source observation used by the build; the published row retains its 19:52Z observation time. The page's **Our fair line** 41% / 59% is the normalized API `outcomePrices` pair, with reciprocal fair odds 2.44 / 1.69; it is not a separate bookmaker price or independent model. The `outcomePrices` estimate is not an executable quote: the very wide top-of-book is why this row is labelled **wide line · low confidence**. It exceeds the strict 25-point gate but is inside the documented 60-point ceiling and above the $100 floor. The specific row carries the low-confidence flag, and the public [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html) page explains the non-blocking wide-tier policy exception and its precision trade-off. The live row also preserves its 31.0%/69.0% Valve-model comparison, not as the market pick basis.

For 6024716, the direct API re-read returned 0.415/0.585, exact 22 October 14:00Z start, active/accepting state, $1,006.10 liquidity, and a 0.36/0.47 bid/ask (11-point gap). The board records the 19:52Z observation. Imperial–Turma do Pagode is published at 77.0% / 23.0% from market 5972064 at the same 19:52Z observation; a later API re-read returned 0.775/0.225 with a 0.76/0.79 bid/ask and last trade 0.77. This small cross-time difference is recorded as a time-sensitive quote, not silently overwritten; the row carries its observation time and expiry, and the next refresh should re-observe it.

## Follow-up research on #1081597 — still unresolved

The row is **benched gods vs TitanFlow**, scheduled by the live inventory for 22 October 2026 at 11:00 UTC, CCT Europe 2026 Challengers #8. The review checked the following sources:

- [Hotspawn fixture](https://www.hotspawn.com/matches/benched-gods-vs-titanflow-cct-europe-2026-challengers-8-1081597) establishes the dashboard inventory only.
- [EGamersWorld matchup](https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn) confirms the pair, event, best-of-three format, and 22 October 11:00 UTC start. Its page displays `1.8` for each side, but does not identify a bookmaker or validate a timestamped two-way quote. Those values are not accepted as odds.
- [HLTV 22 October match listing](https://www.hltv.org/matches?selectedDate=2026-10-22) and the [HLTV CCT event page](https://www.hltv.org/events/9453/cct-2026-challengers-europe-series-8) provide schedule/event context. No dedicated exact-match detail page and lineup were verified in this review.
- The vendored [official Valve global standings snapshot dated 5 October 2026](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) lists two benched gods entries but no TitanFlow entry. It cannot supply the two-team inputs for the published Valve model.
- The [21 October HLTV-hosted regional VRS page](https://www.hltv.org/valve-ranking/teams/2026/october/21/region/Europe) surfaced in search with newer ranking results for both teams. It is an HLTV-hosted ranking view, not the vendored official Valve snapshot, and the exact rows were not independently read in this review; do not transfer search-result snippets into the official model.

No bookmaker/API quote with attributable source, market timestamp, and both sides was verified. The symmetric EGamersWorld display is not a price source. The ranking material also does not establish an admissible model probability. Therefore this report adds **no pick and no percentage**; keeping the row blank is the evidence-consistent result pending the active source-research pass.

### Suggested follow-up for the active research owner

Session `96ea1af8` owns a concurrent fresh-snapshot/source review and final integration. Please verify whether a current, directly read HLTV ranking source plus exact team identities can support a clearly labelled **research-only** selection for #1081597 under the existing rules. If it cannot, retain the blank. Do not promote the EGamersWorld 1.8/1.8 display to a bookmaker quote. If the manually confirmed schedule sources are adopted, consider clarifying the unresolved explanation to say the fixture/time are confirmed but no acceptable odds or ranking basis supports a pick; the current automated message says no exact pair/start was found in its retrieved feed.

## Non-blocking display note

Text-only extraction of the live pages shows both the stale-warning template and the “snapshot inside its 8-hour evidence window” status. The prior acceptance audit reports that JavaScript gates the warning in the browser and that expiry/boundary scenarios passed. This extraction alone is not evidence of a user-visible warning; keep the existing caveat flagged and use the browser checks as the visual source of truth.

## Conclusion

The live board exposes all 13 open rows with a source-led decision, blank probability where unsupported, and a prominent unresolved section. The only gap is #1081597. The current evidence confirms its schedule but not an attributable line or supportable winner, so an invented percentage would violate the user's verification rule. The separate active session owns any further source work or implementation changes; no shared code/data files were changed here.
