# Session 9fca16ca — final delivery audit and integration report

**Live dashboard:** <https://buffedlizard55-lab.github.io/MaltaProj4/>

The site is a static GitHub Pages dashboard with an [executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/index.html), the [updated pick board](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html), a dedicated [unresolved-and-limitations page](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html), the [complete feed](https://buffedlizard55-lab.github.io/MaltaProj4/matches.html), the [evidence ledger](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html), the [source ladder](https://buffedlizard55-lab.github.io/MaltaProj4/sources.html), the [Flagged for Review page](https://buffedlizard55-lab.github.io/MaltaProj4/review.html) and the [tournament analysis](https://buffedlizard55-lab.github.io/MaltaProj4/analysis.html). The executive summary links to the pick board, unresolved limitations, all matches and the methodology both in the visible summary bars and in the phone tab bar.

## What was verified

The merged board at snapshot `2026-10-25T14:22:27.352651Z` has **78 Hotspawn CS2 feed rows, 16 open, 16 picks, 16 probability pairs and 0 unresolved**. The 62 past-dated records that the endpoint still returns as `status: scheduled` remain on All matches with blank probabilities and are explicitly flagged; they are not treated as future picks. Hotspawn supplies fixture inventory, names, locks and starts only. Its crowd percentages are never used to derive a probability.

| Method | Rows | Source of probability |
| --- | ---: | --- |
| `exchange` | 11 | [Polymarket Gamma API](https://gamma-api.polymarket.com/sports) whole-match outcome prices |
| `bookmaker_fallback` | 1 | [Thunderpick series moneyline through the BO3.gg API](https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026), de-vigged |
| `model_vrs` | 4 | Originated lines from [Valve's official regional standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md), with HLTV fixture/roster checks, Valve's [fit.js](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/fit.js) and the published calibration |

Every open row has a directional pick, both teams' percentages, fair decimal lines, the method label, a dated evidence receipt, an expiry deadline, an official Hotspawn fixture link and an external official price/model link. The reproducible [line-by-line ledger](ROW-LEDGER.md) lists all 16 rows with source links and arithmetic checks; [independent-verification.md](independent-verification.md) is the separate bd650209 verifier replayed on this merged snapshot. [SUMMARY.json](SUMMARY.json) is the machine-readable result.

For low-tier fixtures without an accepted featured line, the retained attempts show the required ladder: strict exchange gate → [HLTV](https://www.hltv.org/matches) identity/lineups → [Pinnacle esports moneylines](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight) → labelled wide-exchange tier → [Thunderpick](https://thunderpick.io/esports/cs2-betting) / [BO3.gg](https://api.bo3.gg/api/v1/matches?page[offset]=0&page[limit]=100&filter[matches.status][in]=upcoming&filter[matches.discipline_id][eq]=1&sort=start_date&with=teams,tournament) listings → an originated Valve-VRS model line. [GG.BET](https://gg.bet/en/esports/counter-strike) and [EGamersWorld](https://egamersworld.com/counterstrike/match/EkalRNMvVx/hotu-vs-the-huns-esports-SfdtzDhiK) returned access restrictions on the runner; they are recorded as limitations, never bypassed. No blocked source is treated as evidence that no market exists.

## Direct official-source checks

At 14:18–14:23 UTC this session read the official pages/APIs directly: the [Hotspawn lobby](https://play.hotspawn.com/lobby), the [Hotspawn fixture API](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1), eleven individual Polymarket market endpoints, the [Pinnacle moneyline API](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight), [Thunderpick](https://thunderpick.io/esports/cs2-betting), [BO3.gg](https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026), [GG.BET](https://gg.bet/en/esports/counter-strike), [EGamersWorld](https://egamersworld.com/counterstrike/match/EkalRNMvVx/hotu-vs-the-huns-esports-SfdtzDhiK), [HLTV match pages](https://www.hltv.org/matches/2399115/color-vs-ex-zero-tenacity-nodwin-clutch-series-13), the [dated Valve ranking mirror](https://www.hltv.org/valve-ranking/teams/2026/october/25), Valve's [official standings](https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) and its model source.

All eleven current exchange quotes and the researched BO3/Thunderpick line reproduce the merged snapshot's stored orientation and probabilities. The official Valve file's vendored copy matches its recorded SHA-256; the four originated model lines use the exact standings, points and roster rows, and HLTV pages confirm identity. [official-checks.json](official-checks.json) contains every direct-source URL and the observation window. An earlier 13:54 snapshot had three quotes that moved by 0.5–1.0 percentage points before the next normal gated refresh; the 14:22 capture replaced those raw receipts. No value was edited by hand.

## Gate results on the final candidate

| Gate | Result |
| --- | --- |
| `python -m unittest discover -s tests` | **1,701 tests OK**, 12 skipped |
| `python -m unittest discover -s audits` | 9 OK |
| `verification-95b588c2/test_integrity.py` | 5 OK |
| `python -m unittest discover -s verification-c6` | 12 OK |
| `scripts.validate --site .` and `--site public` | 78 rows, 16 reproduced calculations, 15 pages, 726 links/assets, 20 checksums, 181 displayed rows |
| `verification-c6/audit_snapshot.py public/data/latest.json` | 0 failures |
| `research/session-bd650209/verify_board.py` | 16/16 open rows PASS |
| `scripts.coverage_contract` | 16 open, 12 market, 4 model, 0 unresolved, 0 expired, 0 problems |
| `npm run test:browser` | all 13 Chromium suites pass; no horizontal overflow at 320/390/412px; both percentages and the pick clear the fixed phone tab bar |
| `research/session-9fca16ca/build_report.py` | 16/16 open rows, 0 row/HTML/receipt failures, 20/20 manifest checksums, 0 concurrent quote differences |

Logs are in [`logs/`](logs/) and the generated receipt is [`build-info.json`](../../build-info.json). The publisher uses a 15-minute cron (`:04`, `:19`, `:34`, `:49`) plus a 10-minute freshness watchdog, with an eight-hour evidence window and browser-side expiry; this exceeds the requested 4–8-hour refresh target without weakening expiry rules.

## Flagged for review (non-blocking)

- Later official quote movement on an earlier snapshot, now resolved by the normal 14:22 capture. [Review note](https://buffedlizard55-lab.github.io/MaltaProj4/review.html#session-9fca16ca-dated-market-drift-2026-10-25).
- Low-tier source access limitations, labelled model lines and the no-tick-timestamp listing. [Review note](https://buffedlizard55-lab.github.io/MaltaProj4/review.html#session-9fca16ca-fallback-access-limitations-2026-10-25).
- Two open rows link to the official Hotspawn lobby because the feed supplies no per-fixture slug; no slug was invented.
- All 16 open rows have `best_of: null` because the official feed did not state a series format; the value is blank, not inferred.
- Fixture 1082858 carries a wide-spread, low-precision warning; fixture 1082861 is a labelled wide-exchange tier; fixture 1082859's listing has no operator price-update timestamp.
- All four originated lines use Valve's 2026-10-05 standings, which are inside the published model age limit but are a model input, not a live bookmaker price.
- The legacy `main:/` Pages build and the Actions artifact can show different receipt timestamps while a deployment is building; the site itself remains inside its evidence window and `scripts.verify_live.py` is the final byte-consistency gate. See the final integration receipt in `COORDINATION.md`.

No flagged irregularity is hidden, and none blocks publication. Values that could not be confirmed from a linked official source remain blank and marked unverified; no 50/50 filler, crowd vote, guessed slug or invented price is used.
