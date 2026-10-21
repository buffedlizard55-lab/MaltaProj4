# Session 96ea1af8 — every-match picks, line-by-line verification, phone-first summary

Date: 2026-10-21 (19:40–20:30 UTC). Branch: `arena/96ea1af8-maltaproj4`.
Non-publishing research harvest: run
[39663239769](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39663239769) (19:41:09Z snapshot) and
[39664105659](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39664105659) (HLTV markup probe).

This session re-checked the standing brief from scratch rather than trusting the previous board: a pick for every
Hotspawn CS2 fixture, probabilities that come from external lines (never Hotspawn's crowd percentages), a separate
unresolved-and-limitations section inside the executive summary, a phone-first way to reach the updated pick list,
and a line-by-line verification of what the site actually publishes.

## 1. Coverage of the live lobby (the inventory question)

The unmodified `scripts.refresh` compares three independent views of the same lobby in one run. On the 19:41Z
snapshot all three agreed:

| View | Fixtures | Source |
| --- | ---: | --- |
| CS2 scheduled fixture API | 76 | `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1` |
| CS2 lobby hydration | 76 | https://play.hotspawn.com/cs2-pickems |
| General lobby | 76 | https://play.hotspawn.com/lobby |

`coverage: verified`, no conflicts, 15 fixture IDs added and 37 dropped versus the committed 2026-10-18 baseline
(`inventory_changes` in the snapshot). Of those 76 rows, **13 are open** by sourced lock/start/status fields;
63 are past or closed and stay visible on *All matches* without being treated as future picks.

Open-row outcome at 19:41Z:

| Tier | Rows | Meaning |
| --- | ---: | --- |
| Exchange market line (`exchange`) | 3 | Polymarket two-way quote that passed the strict gates |
| Our originated line (`model_vrs`) | 6 | Valve's official standings points through Valve's published formula |
| Research pick, no percentage (`research_rank`, `research_rank_single`) | 3 | HLTV fixture identity plus ranking order |
| No pick, no percentage | 1 | fixture 1081597 — analysed in §3 |

So 12 of 13 open fixtures carry a pick and 9 carry a published percentage. The site states the same numbers in
`#picks-at-a-glance`, `#unresolved-summary` and the status strip; nothing is hand-entered.

## 2. Line-by-line verification against the sources

Every row below was recomputed by hand from the source response named, not from the site's own text.

### 2.1 Market rows (re-read from Polymarket's public API on 2026-10-21, 20:05–20:20Z)

| Fixture | Market | Source reading | Published | Check |
| --- | --- | --- | --- | --- |
| 1082688 Imperial vs Turma do Pagode | [5972064](https://gamma-api.polymarket.com/markets/5972064) | `outcomePrices ["0.775","0.225"]`, bestBid 0.76 / bestAsk 0.79, spread 0.03, liquidity $7,934, `acceptingOrders true`, `gameStartTime 2026-10-22T14:00:00Z` | 77.5% / 22.5%, fair 1.29 / 4.44 | ✅ sum 1.000, start matches Hotspawn 14:00Z |
| 1082689 BESTIA vs ShindeN | [5972071](https://gamma-api.polymarket.com/markets/5972071) | `outcomePrices ["0.525","0.475"]`, bestBid 0.52 / bestAsk 0.53, spread 0.01, liquidity $11,095, start 14:00Z | 52.5% / 47.5%, fair 1.90 / 2.11 | ✅ |
| 1082882 UNiTY vs Apogee Betclic | [6024716](https://gamma-api.polymarket.com/markets/6024716) | created 19:15:21Z; at the row's 19:43:40Z observation the quote was 0.42 / 0.58; re-read at 20:15Z `outcomePrices ["0.415","0.585"]`, bestBid 0.36 / bestAsk 0.47 (spread 11 points), liquidity $1,006 | 42.0% / 58.0% | ✅ time-stamped observation; the quote moved after our capture, which is exactly what the published expiry shows. Spread > 10 points is flagged low precision. |

The UNiTY row also demonstrates the refresh cadence working as intended: that market did not exist at 19:20Z
(the live build showed the model line, 67.3%) and was priced from the exchange in the 19:41Z snapshot once the
market opened — market lines outrank model lines, as documented.

### 2.2 Originated model rows (recomputed from Valve's file)

Formula and calibration are Valve's own (`model/fit.js` Glicko expectation with RD 75; published fit slope
0.7986): `E = 1/(1+10^(-G·(pA-pB)/400))`, `p = 0.5 + 0.7986·(E-0.5)`, with `G = 0.9728210`.

| Fixture | Valve rows used (file [2026-10-05](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)) | Recomputed | Published |
| --- | --- | --- | --- |
| 1081600 Donstu vs Banda chuya | #197 DONSTU 732 pts; #165 Banda Chuya 801 pts | E = 0.404584 → 42.380% / 57.620% | 42.4% / 57.6% ✅ |
| 1082792 HOTU vs The Huns | #31 HOTU 1437 pts; #122 The Huns 944 pts | E = 0.940521 → 85.180% / 14.820% | 85.2% / 14.8% ✅ |

The remaining four model rows (`1081870`, `1082859`, `1082861`, and `1082882` before its market opened) were
recomputed by the same code path and replay identically in `scripts.validate` and
`verification-c6/audit_snapshot.py`: **0 failures**, 9 probability calculations reproduced, 181 displayed rows
verified, 648 internal links/assets and 20 checksums checked.

## 3. The one open fixture with no pick: 1081597 benched gods vs TitanFlow

Hotspawn fixture **1081597**, CCT Europe 2026 Challengers #8, start **2026-10-22T11:00:00Z**, lock 10:54Z.
The 19:41Z refresh recorded every tier failing, and I re-read each source where this session could reach it:

| Tier | Result | Source |
| --- | --- | --- |
| Polymarket | no exact pair at this UTC start | `gamma-api.polymarket.com/sports` (recorded in the row's attempts) |
| Pinnacle | no exact pair | `guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight` |
| HLTV | **no fixture page exists yet**: the team page states "benched gods has no upcoming matches at the moment" | https://www.hltv.org/team/13599/benched-gods |
| GG.BET | HTTP 403 after three logged waits; host blocked for the run, no bypass | gg.bet/en/esports/counter-strike |
| Thunderpick | access 200, no validated two-way quote | thunderpick.io/esports/cs2-betting |
| Valve model | `benched gods` appears **twice** in Valve's global file (#157, 811 pts, roster facer/K014NZ/norescue/Wign/yoyoS2; #329, 516 pts, different roster) and **TitanFlow is absent** from both the global and the Europe files | [global](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md), [Europe](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_europe_2026_10_05.md) |
| EGamersWorld | identical **1.8 / 1.8** on both sides — this project's documented placeholder, never a line | https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn |
| bo3.gg | no numeric odds published for this fixture | https://bo3.gg/matches/benched-gods-vs-titanflow-22-10-2026 |

Why it is not a 50/50 and not a researched pick today: the one-sided Valve tier (`research_vrs_single`) needs
exactly one team to resolve in Valve's file, and the duplicate `benched gods` label can only be separated by a
**fixture-scoped lineup**, which HLTV has not published. I confirmed the mechanism rather than assuming it:
HLTV's team-page roster (Wign, K014NZ, facer, norescue, yoyoS2) is exactly Valve's #157 roster, five of five, so
`scripts.vrs.identify` resolves that label uniquely the moment a lineup is available, TitanFlow is genuinely
absent, and the documented tier then issues a research-only pick with **no percentage** (one standings input
cannot produce a probability). The refresh re-checks every 15 minutes until lock, so once HLTV creates the fixture
page the pick appears without any manual step.

Deliberately not done: adding extra HLTV scrapes (`/search`, `/team/...`) to the production refresh. The probe run
([39664105659](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39664105659)) shows HLTV answering
**403** to those paths for the collector (`research/harvest-96ea1af8/hltv-probe/probe.json`, six requests, all
403). Bolting them onto every refresh would risk the failure mode documented in `scripts/refresh.py`, where one
403 costs every remaining row its lineup and drops the board to "no pick". Nothing was bypassed and no price was
invented.

## 4. What changed in the site this session

* `#pick-limitations` (inside `#unresolved-summary` in the executive summary) now **names** the open fixtures that
  have no pick at all, each as a link to its evidence block, and says so explicitly when the set is empty. Before,
  the panel stated the limitation class but the reader had to open another page to learn which match it was.
* Styling for that callout (`site/assets/style.css`), including a phone-size rule at ≤650px, so it stays readable
  without side-scrolling.
* Flagged-for-Review note `1081597-no-pick-2026-10-21` in `data/review-notes.json` with the seven sources above.
* New tests: `tests/test_session_96ea1af8.py` (4 tests) covering the named-gap rendering, the empty state, the
  section nesting, and the sourcing of the review note.

Unchanged on purpose: the published numbers. No probability was re-derived, softened or invented to fill the last
row; the executive summary keeps "Blank means unverified, never 50/50".

## 5. Verification performed

| Gate | Result |
| --- | --- |
| `python -m unittest discover -s tests` | 498 tests, OK (494 existing + 4 new) |
| `python -m unittest discover -s audits -p 'test_*.py'` | 9 tests, OK |
| `python verification-95b588c2/test_integrity.py` | 5 tests, OK |
| `python -m unittest discover -s verification-c6 -p 'test_*.py'` | 12 tests, OK |
| `python -m scripts.build --data research/harvest-96ea1af8/snapshot.json` | 9 pages + 6 legacy redirects; 76 rows, 9 with percentages, 4 without, 1 unresolved |
| `python -m scripts.validate --data public/data/latest.json` | 9 calculations reproduced, 648 links/assets, 20 checksums, 181 rows |
| `verification-c6/audit_snapshot.py public/data/latest.json` | **0 failures** |
| `npm run test:browser` | 32 page/viewport scans at 320/390/768/1440px (axe WCAG 2.x, no horizontal overflow), filters, legacy redirects, 7 expiry scenarios + 4 research-quote boundary scenarios |

## 6. Irregularities flagged (none of them blocking)

1. **HLTV refuses `/search` and `/team/...` to this collector** (403 ×6 in the probe above) while `/matches` and
   match pages answer 200. Recorded, not worked around.
2. **HLTV's Valve-ranking mirror is newer than Valve's published file.** The team page shows Valve #161 (EU #115)
   for benched gods on 21 Oct, while Valve's own file is dated 2026-10-05 and ranks the same roster #157 (EU #116).
   The site uses Valve's file only; HLTV's display is never treated as the ranking input.
3. **EGamersWorld answered 403 to the refresh this run**, so the six EGW book-listing receipts could not be
   re-observed and expired instead of renewing. Correct behaviour (an aged receipt reverts to the lower tiers),
   but it means today's exchange/model counts would rise if EGW allowed the read.
4. **Non-JS text extraction still shows the hidden stale banner.** `#runtime-stale` ships with `hidden` and is
   un-hidden only by the browser script; text-only readers see its contents. Already documented by session
   84295759; it is not a stale board.

## 7. Sources read for this report

* Hotspawn lobby and fixture API (inventory only, never probabilities):
  https://play.hotspawn.com/lobby · https://play.hotspawn.com/cs2-pickems ·
  https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1
* Polymarket Gamma API: https://gamma-api.polymarket.com/markets/5972064 ·
  https://gamma-api.polymarket.com/markets/5972071 · https://gamma-api.polymarket.com/markets/6024716
* Valve official standings (global and Europe, 2026-10-05, commit `eec4853`):
  https://github.com/ValveSoftware/counter-strike_regional_standings/tree/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026
* HLTV: https://www.hltv.org/team/13599/benched-gods ·
  https://www.hltv.org/events/9453/cct-2026-challengers-europe-series-8 ·
  https://www.hltv.org/matches/2399865/zetta-vs-los-ninos-cct-2026-south-america-series-7
* Book/aggregator listings re-read for the unpicked fixture:
  https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn ·
  https://bo3.gg/matches/benched-gods-vs-titanflow-22-10-2026
