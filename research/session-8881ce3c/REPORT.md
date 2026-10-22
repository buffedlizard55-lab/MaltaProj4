# Independent live coverage and release audit

**Session:** `8881ce3c`  
**Audit time:** 2026-10-22 01:10 UTC  
**Published revision checked:** `40e1fab4313fc25f320d0cf08bffe9e5ee4f5443`  
**Published build timestamp:** 2026-10-22 00:55:06 UTC  
**Result:** the live board is current within its published eight-hour evidence window and the visible coverage arithmetic is internally consistent. All open matches have a pick; seven have only a research pick without a win percentage. No truly unresolved open match was shown in the summary at the time checked.

## Sources opened

- [Hotspawn lobby (official)](https://play.hotspawn.com/lobby) — the CS2 filter displayed 74 fixtures in the weekly lobby at read time. This is the lobby's weekly/filter count, not the count of currently open fixtures.
- [Hotspawn CS2 Pick'ems page (official)](https://play.hotspawn.com/cs2-pickems)
- [Hotspawn public scheduled-CS2 feed](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1)
- [Live dashboard executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/)
- [Live updated-picks board](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html)
- [Live unresolved and non-market board](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html)
- [Live evidence ledger](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html)
- [Live methodology and source limits](https://buffedlizard55-lab.github.io/MaltaProj4/sources.html#method)
- [Live review flags](https://buffedlizard55-lab.github.io/MaltaProj4/review.html)
- [Published build manifest](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json)
- [Successful refresh, verification and deploy run](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39702130404)
- Example primary evidence shown by the board: [Polymarket market 6024922](https://gamma-api.polymarket.com/markets/6024922), [Valve's official CS2 standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md), and [HLTV match page for GenOne–Spirit Academy](https://www.hltv.org/matches/2399327/genone-vs-spirit-academy-cct-2026-europe-series-11).

## Coverage reconciliation

The live `build-info.json` reports the audited revision, a 00:55:06Z build and 97 feed rows. The executive summary reported **35 open fixtures, 35 picks, 28 with win probabilities, and 0 unresolved**. It breaks the 28 probabilities into **8 market-derived and 20 VRS-model-derived** estimates; the remaining **7 fixtures are research-only picks with no percentage**.

The pick board states 28 probability-bearing entries. The separate “Unresolved & non-market picks” page states 27 entries: the same 20 VRS model rows plus the 7 research-only rows. Thus 28 + 27 − 20 = 35 unique open fixtures; the page counts are complementary/overlapping views, not 55 different fixtures. Its “unresolved” wording covers the research queue; it does not mean all 27 are unresolved. The live executive summary correctly reported zero open fixtures without any pick at audit time.

The Hotspawn weekly CS2 filter count of 74 is not a competing open-match count: it includes the wider weekly listing, whereas the dashboard's 35 is the feed's current actionable/open subset after its start/lock gates. Hotspawn's public lobby and CS2 page establish inventory only. Their crowd-pick percentages are expressly excluded from the probability methods.

## Verification performed

1. Read the official Hotspawn lobby and CS2 page and confirmed active CS2 match cards include the public team/event listings and individual Hotspawn match links.
2. Read the published manifest and executive summary: snapshot `2026-10-22T00:55:05.742549Z`; 97 rows; 35 open; 35 picked; 28 probabilities; zero unresolved. Read the pick and non-market pages and reconciled their row counts as above.
3. Spot-checked the rendered source pattern: a market-priced example exposes a Polymarket market link and a calculation/evidence link; model rows expose Valve standings and HLTV fixture/lineup links; ranking-only research rows disclose that no percentage is supported and link the HLTV context and attempted sources. Every sampled entry links to its Hotspawn fixture (one row may use the official CS2 landing page where no specific match URL is emitted by the source).
4. Checked GitHub Actions run [39702130404](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39702130404): all listed steps succeeded, including live-source refresh, independent row audit/build validation, browser/mobile/accessibility/expiry tests, verified legacy fallback staging and exact live Pages byte verification. Both `verify-build` and `deploy` concluded `success`.
5. In the checked-out repository, `python -m unittest discover -s tests` passed **602 tests**; `scripts.validate` passed on the committed baseline (**75 rows, 11 calculations, 15 pages, 655 internal links/assets, 20 checksums, 176 displayed rows**). Built that committed baseline to ignored `public/`; the generated artifact validator passed (**75 rows, 10 calculations, 649 internal links/assets, 20 checksums, 174 displayed rows**). `npm run test:browser` passed **32 page/viewport accessibility and no-overflow scans** at 320/390/768/1440 px, plus navigation, filters, anchors, legacy routes and expiry behavior; the dedicated expiry suite also passed seven board scenarios and four research-quote boundary/future-clock scenarios. The local checkout's tracked snapshot is older than the live snapshot, so these local figures are historical-baseline checks; the live/current revision verification is the successful 00:50Z scheduled Actions run and its exact-live-byte check.

## Limitations and irregularities to keep visible

- **Seven picks are not win probabilities.** They use source-backed, one-sided research (for example a published ranking when only one side can be verified). They must remain explicitly “research only” and must not be converted to 50/50, an inferred line, or a model percentage. The site correctly withholds the percentage and documents the evidence/limitation per row.
- **Model probabilities are internally originated, not bookmaker quotes.** The site labels VRS model lines distinctly from market lines; rankings/model inputs are not equivalent to current market consensus or a guarantee of outcome.
- **Coverage is conditional on public-source access and successful scheduled runs.** The workflow attempts a refresh four times per hour with a watchdog; GitHub scheduling, source changes and book restrictions can still delay/fail refresh. The board expires stale evidence rather than promising that every future slot will publish.
- **Some rows have schedule/identity/source caveats** recorded in the review/evidence pages; these are not hidden or used to manufacture prices. The 74 weekly lobby filter count should not be described as 74 simultaneously open matches.
- The page-text extraction tool included a stale-banner sentence despite also showing “Snapshot inside its 8-hour evidence window.” The project deliberately ships that banner hidden until browser-time expiry; local browser expiry checks passed, so this text-extraction artifact is not evidence that the live browser displayed a stale warning.

No data, source receipt, model result, or generated page was changed by this audit. The only project changes are this audit report and the matching coordination-board claim/completion record.

## Post-merge receipt

- PR [#141](https://github.com/buffedlizard55-lab/MaltaProj4/pull/141) merged to `main` at 2026-10-22 01:19Z as `c20dee5cb8390b1c7c10af896012a9542a3e1616`. Its rebase-updated PR verification run [39704645986](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39704645986) passed `verify-build`; deploy was skipped for the pull request as designed. The PR changes only this audit report and coordination metadata; it does not alter the published site.
- After the merge, the live manifest was re-read: revision `4ec8c973df28020d837b11132c7f88545e9e309f`, 97 rows, build `2026-10-22T01:17:55Z`; the live summary still showed 35 open, 35 picked, 28 with probabilities, and 0 unresolved. Those bytes were published by the successful scheduled/main workflow before the documentation-only merge. The exact-live-byte deployment check for the prior build was green in run [39702130404](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39702130404).
- A post-merge main workflow was watched to completion with a successful CLI exit. Individual job details were not fetched afterward because GitHub API rate limiting returned HTTP 403; therefore this audit does not claim that the documentation-only merge triggered a new Pages deployment. Live manifest and summary reads confirm the currently served site remains fresh and complete.
