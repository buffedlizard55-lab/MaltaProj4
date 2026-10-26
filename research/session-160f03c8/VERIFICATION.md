# Session 160f03c8 — independent coverage and mobile verification

**Observed:** 2026-10-26 00:52 UTC. This is an audit of the checked-in and deployed snapshot, plus a separately fetched live Hotspawn view. It is not a new odds capture, and it does not validate forecast accuracy.

## Executive finding

The checked-in/live board is internally consistent for its own observation (`2026-10-26T00:10:49.639616Z`): 73 retained fixture rows, 11 open rows, and 11 picks with probabilities. I independently found a **live Hotspawn inventory mismatch** after that snapshot. The public Hotspawn general lobby displayed 81 CS2 entries / 19 matches this week and listed eight future fixtures absent from the 73-row snapshot. Hotspawn's separate `/cs2-pickems` page displayed 72 entries. The three surfaces therefore do not agree at the time of review. The eight records were not silently added or assigned odds: the available evidence verifies their Hotspawn identity/scheduled UTC time only, not a current external price or an independently supported pick. The mismatch is published as **Flagged for Review**; a fresh three-surface capture is needed before claiming full live coverage.

## Audited snapshot and row-level results

The committed capture identifies the fixture feed, both Hotspawn HTML surfaces and source retrieval times in `data/latest.json` (`source_checks` and `fixture_evidence`). Capture: fixture feed read 00:07:16Z; `/cs2-pickems` read 00:07:17Z; `/lobby` read 00:07:18Z; board generated 00:10:49Z. Each source check is HTTP 200; the independent capture counts are 73/73/73/73 for API/page/lobby/retained rows. This establishes parity for that capture only, not for later changes to Hotspawn.

| Check | Observed value | Verification |
| --- | --- | --- |
| Snapshot | `2026-10-26T00:10:49.639616Z`; fixture read `00:07:16.611284Z` | Read from `data/latest.json`; the live executive-summary page reported its last check as 00:10 UTC at review time. |
| Snapshot coverage | 73 rows: 62 not open, 11 open | Recounted the JSON rows and states; its sourced-status note explains the 62 past-dated feed entries. |
| Open rows with a pick | 11 / 11 | Recounted `state == open` rows; all have a named `pick`. |
| Open rows with probabilities | 11 / 11 | Recounted non-null probabilities; the independent snapshot audit reproduced all 11 calculations with zero errors. |
| Methods on the snapshot | 7 exchange, 1 researched bookmaker listing, 3 originated Valve VRS model lines | Counted `method` values in the 11 open rows. The model rows are explicitly labeled non-market estimates. |
| Unresolved / research-only open rows in that snapshot | 0 / 0 | Recounted the open rows. This does **not** establish that the newer eight fixtures have picks. |
| Third-party-listing caveat | NEXVOID–Alter Ego: BO3.gg listing-derived estimate; listing has no price-update timestamp | The row itself flags the limitation and shows the observation time; it is not represented as a direct operator API quote. |
| Crowdsourced Hotspawn percentages | Not used | The build and method state explicitly that Hotspawn vote percentages are never win probabilities. |

### Every open snapshot row and its recorded evidence URL

Probability order is the source order of the two teams. The figures below are from the captured snapshot, not freshly re-priced at 00:52Z. A source link is shown for each match and its recorded pricing input.

| Hotspawn fixture | Snapshot probabilities | Pick / method | Recorded pricing or model source |
| --- | --- | --- | --- |
| [Ground Zero vs Off Chops](https://www.hotspawn.com/matches/ground-zero-vs-off-chops-dfrag-invitational-2026-1082858) | 19.0% / 81.0% | Off Chops · exchange | [Polymarket event](https://polymarket.com/event/cs2-gz1-offcho-2026-10-25) |
| [NEXVOID vs Alter Ego](https://www.hotspawn.com/matches/nexvoid-vs-alter-ego-dfrag-invitational-2026-1082859) | 57.5% / 42.5% | NEXVOID · researched listing | [BO3.gg listing](https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026) |
| [Nuclear TigeRES vs UNiTY](https://www.hotspawn.com/matches/nuclear-tigeres-vs-unity-nodwin-clutch-series-13-1093218) | 66.5% / 33.5% | Nuclear TigeRES · our VRS model | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |
| [FlyQuest vs Staqued](https://www.hotspawn.com/matches/flyquest-vs-staqued-dfrag-invitational-2026-1082860) | 92.5% / 7.5% | FlyQuest · exchange | [Polymarket event](https://polymarket.com/event/cs2-fly-staque-2026-10-26) |
| [Rooster vs Abyssal](https://www.hotspawn.com/matches/rooster-vs-abyssal-dfrag-invitational-2026-1082861) | 42.5% / 57.5% | Abyssal · wide-spread exchange (flagged low precision) | [Polymarket event](https://polymarket.com/event/cs2-rstr-abyssa-2026-10-26) |
| [B8 vs K27](https://www.hotspawn.com/matches/b8-vs-k27-tesla-cup-2026-1082897) | 59.5% / 40.5% | B8 · exchange | [Polymarket event](https://polymarket.com/event/cs2-b8-k271-2026-10-27) |
| [Alliance vs FaZe](https://www.hotspawn.com/matches/alliance-vs-faze-tesla-cup-2026-1082898) | 37.5% / 62.5% | FaZe · exchange | [Polymarket event](https://polymarket.com/event/cs2-all-faze-2026-10-27) |
| [Luminosity vs HOTU](https://www.hotspawn.com/matches/luminosity-vs-hotu-tesla-cup-2026-1082900) | 52.5% / 47.5% | Luminosity · exchange | [Polymarket event](https://polymarket.com/event/cs2-lg6-hotu-2026-10-27) |
| [Envy vs GamerLegion](https://www.hotspawn.com/matches/envy-vs-gamerlegion-tesla-cup-2026-1082901) | 45.5% / 54.5% | GamerLegion · exchange | [Polymarket event](https://polymarket.com/event/cs2-envy-gl1-2026-10-27) |
| [HOTU vs The Huns](https://www.hotspawn.com/matches/hotu-vs-the-huns-moscow-cyber-games-2026-1082792) | 85.2% / 14.8% | HOTU · our VRS model | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |
| [5star vs 1WIN](https://www.hotspawn.com/matches/5star-vs-1win-moscow-cyber-games-2026-1082793) | 24.3% / 75.7% | 1WIN · our VRS model | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |

The source URL for each Hotspawn fixture is present in its JSON row, and the validator confirms official fixture links and all displayed row links. See [the row evidence ledger](../../evidence.html) for per-row observations, expiries, rejected lines and calculations.

## Live Hotspawn mismatch found after the snapshot

At 00:52Z, separately fetched official Hotspawn pages showed:

* [`/lobby`](https://play.hotspawn.com/lobby): “All tiers (81)” and “19 matches this week”; it rendered the eight fixtures below.
* [`/cs2-pickems`](https://play.hotspawn.com/cs2-pickems): “All tiers (72)” and “19 matches this week”.
* The committed `data/latest.json` snapshot has 73 `fixture_evidence` records and does not contain any of these eight IDs. It was generated at 00:10:49Z. The [Hotspawn fixture-feed URL](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1) returned records for these IDs when independently fetched after that capture.

| Missing from the 00:10Z snapshot | Scheduled start (UTC; official feed milliseconds) | Hotspawn match page |
| --- | --- | --- |
| `1079201` · INOX Division vs Nemesis | 2026-10-26 09:00 | [Hotspawn](https://www.hotspawn.com/matches/inox-division-vs-nemesis-nodwin-clutch-series-13-1079201) |
| `1081159` · LFO 10 vs ex-6666 | 2026-10-26 12:00 | [Hotspawn](https://www.hotspawn.com/matches/lfo-10-vs-ex-6666-cct-europe-2026-series-12-1081159) |
| `1079202` · FOKUS vs ex-Zero Tenacity | 2026-10-26 12:00 | [Hotspawn](https://www.hotspawn.com/matches/fokus-vs-ex-zero-tenacity-nodwin-clutch-series-13-1079202) |
| `1081160` · HAVU vs ILLYRIANS | 2026-10-26 15:00 | [Hotspawn](https://www.hotspawn.com/matches/havu-vs-illyrians-cct-europe-2026-series-12-1081160) |
| `1079203` · Metizport vs BRUTE | 2026-10-26 15:00 | [Hotspawn](https://www.hotspawn.com/matches/metizport-vs-brute-nodwin-clutch-series-13-1079203) |
| `1081162` · ex-RUSTEC vs Spirit Academy | 2026-10-27 12:00 | [Hotspawn](https://www.hotspawn.com/matches/ex-rustec-vs-spirit-academy-cct-europe-2026-series-12-1081162) |
| `1081163` · BakS vs Saint Sinners | 2026-10-27 15:00 | [Hotspawn](https://www.hotspawn.com/matches/baks-vs-saint-sinners-cct-europe-2026-series-12-1081163) |
| `1081164` · Inner Circle Academy vs Lavked | 2026-10-27 18:00 | [Hotspawn](https://www.hotspawn.com/matches/inner-circle-academy-vs-lavked-cct-europe-2026-series-12-1081164) |

**Do not infer the missing eight picks from Hotspawn vote share.** Their Hotspawn source records verify names, IDs and scheduled times only. No current Polymarket/Pinnacle/bookmaker line, HLTV ranking evidence or Valve-model identity/roster calculation was verified here for those eight. They must be re-harvested and sent through the existing ladder; until then they are a known coverage gap, not silently “resolved” rows.

**Refresh observation:** the Pages card still showed “Last checked 26 Oct 2026 · 00:10 UTC” when read at 00:52Z. GitHub Actions listed the last successful publish workflow as run [40247657442](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40247657442), started at 00:05:31Z and finished 00:14:35Z; no later publish run appeared in the run list at audit time. This is evidence of refresh lag relative to the advertised 15-minute target, not proof that the next scheduled or watchdog run will fail. Workflow timing remains best-effort, as the site itself discloses.

## Navigation, limitations and mobile verification

The live executive summary directly links to **Updated picks**, **Unresolved & limitations**, **All matches**, **How we price**, and **Flagged for review**. It separates current open pick coverage from “62 feed rows are not open” and explains the model vs market labels. The phone navigation keeps Picks, Unresolved and Matches available on every page. The unresolved page and the home-page evidence-gap section explain the fallback ladder, no-line limitations, and the rule that blank is not 50/50.

Verification performed locally on the exact checked-in snapshot:

* `.venv/bin/python -m scripts.validate --data data/latest.json --site .` — pass; 73 sourced rows, 11 reproduced probability calculations, 15 pages, 693 internal links/assets, 20 checksums and 165 displayed match rows.
* [`independent-audit.md`](independent-audit.md) — 73/73 rows, 0 arithmetic/field failures; this replays retained evidence and explicitly does not prove live-source completeness.
* `.venv/bin/python -m unittest discover -s tests` — **1,778 tests passed, 14 skipped**.
* `.venv/bin/python -m scripts.build --data data/latest.json --out public` followed by `npm run test:browser` — all 13 browser suites passed, including 320/390/768/1440px widths, no horizontal overflow, WCAG A/AA scans, navigation, filters, evidence anchors and stale-data withholding.
* In the 320×568 browser measurement, the compact summary at y=290 links to Updated picks and Unresolved & limits; the first board card starts at y=272, exposes both team probabilities (19.0% / 81.0%) and ends below the fixed bar only as normal scroll content; no horizontal overflow. Existing test also confirms the phone CTA and team chances are readable above the tab bar on the tested layout.
* The first browser invocation, before running the documented static build, failed because `public/data/latest.json` did not yet exist. After the standard build step, the complete browser suite passed. No tracked test artifacts were retained.

## Result / limitation at the original audit time

The site’s information hierarchy and phone layout pass. The 00:10Z saved board’s arithmetic and in-snapshot row provenance pass. At the 00:52Z audit time, the later Hotspawn observation showed at least eight scheduled fixtures missing and conflicting inventory totals across Hotspawn surfaces. The note was correctly non-blocking at that time; the original 73-row capture must not be described as fully current.

## Post-merge follow-up: the later capture resolved the eight-row gap

PR [#353](https://github.com/buffedlizard55-lab/MaltaProj4/pull/353) merged as `8598f73671429cea040b4940b72bec374366f3d0`. Its Pages workflow refreshed the feed after the 00:52Z audit. The live [build receipt](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json?cb=160f03c8-final) reports that merged revision and build time `2026-10-26T01:17:03Z`. A cache-busted [executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/?cb=160f03c8-final-2) reports **81 feed rows, 19 open matches, 19 picks, 19 win-probability pairs and 0 unresolved open matches** (9 external-market lines and 10 labelled Valve VRS-model lines). The [live pick board](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html?cb=160f03c8-audit) verifies that the eight IDs absent from the earlier 73-row snapshot are now included, with a per-row evidence link and source timestamp:

| Hotspawn fixture | Live probabilities | Pick and method | Direct supporting source |
| --- | --- | --- | --- |
| [1079201 · INOX Division vs Nemesis](https://www.hotspawn.com/matches/inox-division-vs-nemesis-nodwin-clutch-series-13-1079201) | 29.0% / 71.0% | Nemesis · external market | [Polymarket market 6186053](https://gamma-api.polymarket.com/markets/6186053) |
| [1081159 · LFO 10 vs ex-6666](https://www.hotspawn.com/matches/lfo-10-vs-ex-6666-cct-europe-2026-series-12-1081159) | 32.8% / 67.2% | ex-6666 · Valve VRS estimate using HLTV's dated ranking mirror | [HLTV Valve ranking, 2026-10-26](https://www.hltv.org/valve-ranking/teams/2026/october/26) · [HLTV fixture](https://www.hltv.org/matches/2399509/lfo-10-vs-ex-6666-cct-2026-europe-series-12) |
| [1079202 · FOKUS vs ex-Zero Tenacity](https://www.hotspawn.com/matches/fokus-vs-ex-zero-tenacity-nodwin-clutch-series-13-1079202) | 74.5% / 25.5% | FOKUS · Valve VRS estimate | [Valve official standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) · [HLTV fixture](https://www.hltv.org/matches/2399117/fokus-vs-ex-zero-tenacity-nodwin-clutch-series-13) |
| [1081160 · HAVU vs ILLYRIANS](https://www.hotspawn.com/matches/havu-vs-illyrians-cct-europe-2026-series-12-1081160) | 58.3% / 41.7% | HAVU · Valve VRS estimate | [Valve official standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) · [HLTV fixture](https://www.hltv.org/matches/2399510/havu-vs-illyrians-cct-2026-europe-series-12) |
| [1079203 · Metizport vs BRUTE](https://www.hotspawn.com/matches/metizport-vs-brute-nodwin-clutch-series-13-1079203) | 68.0% / 32.0% | Metizport · Valve VRS estimate | [Valve official standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) · [HLTV fixture](https://www.hltv.org/matches/2399118/metizport-vs-brute-nodwin-clutch-series-13) |
| [1081162 · ex-RUSTEC vs Spirit Academy](https://www.hotspawn.com/matches/ex-rustec-vs-spirit-academy-cct-europe-2026-series-12-1081162) | 52.3% / 47.7% | ex-RUSTEC · Valve VRS estimate using HLTV's dated ranking mirror | [HLTV Valve ranking, 2026-10-26](https://www.hltv.org/valve-ranking/teams/2026/october/26) · [HLTV fixture](https://www.hltv.org/matches/2399512/ex-rustec-vs-spirit-academy-cct-2026-europe-series-12) |
| [1081163 · BakS vs Saint Sinners](https://www.hotspawn.com/matches/baks-vs-saint-sinners-cct-europe-2026-series-12-1081163) | 73.0% / 27.0% | BakS · Valve VRS estimate | [Valve official standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) · [HLTV fixture](https://www.hltv.org/matches/2399513/baks-vs-saint-sinners-cct-2026-europe-series-12) |
| [1081164 · Inner Circle Academy vs Lavked](https://www.hotspawn.com/matches/inner-circle-academy-vs-lavked-cct-europe-2026-series-12-1081164) | 70.4% / 29.6% | Inner Circle Academy · Valve VRS estimate | [Valve official standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) · [HLTV fixture](https://www.hltv.org/matches/2399514/inner-circle-academy-vs-lavked-cct-2026-europe-series-12) |

The later published snapshot resolves the **observed eight-fixture absence**: one row is backed by an external market, and seven by transparently labelled Valve-ranking estimates (five from Valve's official standings and two from HLTV's dated Valve-ranking mirror). None uses Hotspawn crowd percentages. This does not establish why the earlier surfaces disagreed or guarantee that a future capture will always be complete; retain the 00:52Z discrepancy as dated history, not as a current missing-picks claim.

**Workflow limitation:** Pages deployment and the step verifying the live bytes against the exact build succeeded in run [40252713620](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40252713620). The separate “Keep the legacy main:/ root fallback on the verified build” step failed its validator/unit gate, leaving the overall workflow red; detailed action logs could not be retrieved (GitHub Actions log request ended with EOF). Do not call the whole workflow green. The deployed Pages artifact and its live build receipt were verified despite that independent legacy-root failure.
