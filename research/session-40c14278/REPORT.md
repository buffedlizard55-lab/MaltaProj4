# 21 October 2026 refresh and coverage audit

## Repair

Three tests in `tests/test_session_133fe7ca.py` normalized an October 20 fixture using the wall clock. After lock, normalization correctly returned a non-open state and the tests failed, blocking the publication workflow before refresh. The fixture helper now uses 19 October 04:30 UTC, consistent with its existing receipt assertions. **No production expiry, identity or quote-quality rule changed.**

Failure confirmed by [scheduled run job metadata](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39581284152) and reproduced locally (three failures / 440 tests). After repair all 440 pass.

## Current source research

[Trusted-runner harvest](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39601085903), snapshot `research/harvest-40c14278/snapshot.json`, independently re-derived with zero row-audit failures. Inventory: 81 retained rows, 19 open at 12:41:11 UTC. 16 priced, two qualitative picks, one unresolved. A priced 50/50 market has no directional pick and is not a synthetic filler.

| Fixture | Finding | Primary source |
| --- | --- | --- |
| 1079648 G2 Ares–ILLYRIANS | Verified equal exchange prices; no directional edge. Existing primary line retained, no fallback override. | https://gamma-api.polymarket.com/markets/5994489 |
| 1082762 ex-CYBERSHOKE–BlinkDagger | Neither team has a usable HLTV world ranking or numeric HLTV quote. Exchange label CYBERSHOKE Esports is not proven equivalent to ex-CYBERSHOKE. No Pinnacle pair/start. Leave pick and percentage blank. | https://www.hltv.org/matches/2399839/ex-cybershoke-vs-blinkdagger-winline-mpkbk-cis-lan-season-9 ; https://gamma-api.polymarket.com/markets/5971981 |
| 1082763 UPGRADE–flacons | Existing sourced research pick UPGRADE; no verified market percentage. Do not confuse flacons with Falcons. | https://www.hltv.org/matches/2399840/upgrade-vs-flacons-winline-mpkbk-cis-lan-season-9 |
| 1082837 Zetta–LOS NINOS | Existing sourced research pick Zetta; exchange instead names Alianza Lima Esports. No alias guessed. | https://www.hltv.org/matches/2399865/zetta-vs-los-ninos-cct-2026-south-america-series-7 ; https://gamma-api.polymarket.com/markets/6001634 |

HLTV was checked first by the collector and the unresolved fixture was independently read through the retrieval tool. Its betting table contains a casino promotion, not two numeric odds. Its 74.6/25.4 fan vote is **not** a line and was discarded. HLTV-displayed VRS #78 is context, not an independent win probability.

The collector then checked the official Pinnacle feed, Thunderpick and GG.BET, with per-row receipts in `gaps.json`: Pinnacle no exact pair/start, Thunderpick no validated line extraction, GG.BET HTTP 403. Additional targeted Thunderpick/GG.BET searches returned no usable fixture-specific primary quotes. This is not proof of market absence.

Secondary EGamersWorld searches surfaced these pages:
- https://egamersworld.com/counterstrike/match/4yp_dlKtNl/ex-cybershoke-vs-blinkdagger-5sOoK5oHU4
- https://egamersworld.com/counterstrike/match/4yp_dlKtNl/upgrade-vs-flacons-7Y3AgyjdHd
- https://egamersworld.com/counterstrike/match/0U32SId-H/zetta-vs-los-ninos-Wi0PWrNpb

They showed 1.8/1.8 or incomplete listing prices; direct retrieval of the first returned HTTP 502. No quote is accepted from search snippets. Other secondary pages gave incompatible team labels/stats and are not promoted. Unknown fields remain blank.

## Verification

440 unit tests, nine audit tests, five integrity tests, twelve independent-validator tests pass. Fresh snapshot build validates all 81 rows, 16 calculations, 667 links/assets and 20 checksums. Browser suite passes 32 accessibility/layout scans at 320/390/768/1440 px plus seven board expiry and four research-quote boundary scenarios. Existing mobile executive summary, picks-at-a-glance and unresolved/limitations links are preserved.

Publication receipt and PR are recorded in the coordination board after deployment; this research file does not claim a branch build is live.
