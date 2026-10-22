# Session 7ec4608a — navigation and evidence review

## Verification boundary

This session reviewed the collector and retained evidence locally. It did **not** re-fetch Hotspawn, HLTV, Pinnacle, Thunderpick or GG.BET live. Network access from the coding environment is limited to GitHub and package registries. Existing source receipts are dated observations, not new verification. Search discovery found EGamersWorld pages for the two original unpriced fixtures, but search snippets alone were not promoted to verified operator lines.

Original retained snapshot: 2026-10-21T21:27:36Z, 75 rows, 13 marked open at capture, 11 with percentages, two research-only. Newer main was integrated during this session: 97 rows with 35 open, 28 probabilities and seven research-only at that build. These counts describe captures, not guaranteed future coverage.

## Change

Added a compact executive-summary navigation block immediately after the freshness strip, linking Updated picks, All picks at a glance, Unresolved & limitations, and All feed entries. Phone guidance explains the persistent Picks tab. Responsive CSS wraps these links; current match data and pricing acceptance policy are unchanged.

Regression tests render the template directly and compare the exact set of open fixture evidence links. They do not assume a fixed future inventory count or require a generated build folder to exist.

## Existing fallback research and limitations

For original fixtures 1081597 (benched gods–TitanFlow) and 1082860 (FlyQuest–Staqued), the retained attempt ledger records HLTV research, Pinnacle, exchange, Thunderpick and GG.BET outcomes. Their retained picks are qualitative, with no percentage. The first uses one-sided Valve standings; the second uses HLTV ranking evidence. Neither supplies two model inputs or an accepted two-way market. No new numeric line was established in this session. Existing dated findings remain on Flagged for Review; redundant notes implying fresh checks were removed.

Manual-review sources:
- [Hotspawn lobby](https://play.hotspawn.com/lobby)
- [Hotspawn CS2](https://play.hotspawn.com/cs2-pickems)
- [Official scoped fixture feed](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1)
- [HLTV FlyQuest–Staqued fixture](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026)
- [HLTV bracket slot](https://www.hltv.org/matches/2399696/match)
- [Pinnacle public lines](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
- [Valve official repository](https://github.com/ValveSoftware/counter-strike_regional_standings)

## Refresh and publication

Code review confirms three-view inventory comparison, scheduled publication attempts at :04/:19/:34/:49, and a ten-minute watchdog. These are configured targets, not a delivery SLA. GitHub can delay jobs; source failures and expiry must remain visible. Legacy Pages and workflow deployment can race; the existing guarded root fallback mitigates but does not eliminate that limitation.

Integration exposed an existing test's closed list of methods: it omitted supported bookmaker_fallback and research_rank. The test now accepts those existing methods while preserving pick-membership, explanation and probability-sum checks. No production price gate was relaxed.
