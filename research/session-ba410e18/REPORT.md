# Independent acceptance audit — 2026-10-24

## Executive finding

The integrated dashboard already implements the requested CS2 coverage, research fallbacks, separate limitations section, phone navigation and scheduled refresh. On the retained Hotspawn observation from **2026-10-24 06:16:00 UTC**, the latest snapshot has **92 rows (92 API / 92 page / 92 lobby / 92 retained), 31 open matches, 31 picks, 31 win probabilities and 0 unresolved rows**. The snapshot is not using Hotspawn votes as probability input.

I do **not** mark the delivery as fully clean: the legacy Pages root stylesheet does not match the stylesheet shipped by the workflow artifact, and the local full Python unit suite has an independent-verifier failure for a source-mapped team alias. Both findings are reported below and logged in `COORDINATION.md`; the stylesheet issue is also already present on the site's Flagged for Review page. An active PR (#250) claims the stylesheet repair and is not yet green/mergeable at the time of this audit.

## Snapshot and coverage checked

- Repository build receipt: `build-info.json` says built at `2026-10-24T06:19:43.860972Z`, from snapshot `2026-10-24T06:19:43.492019Z`, 92 rows. Snapshot SHA-256: `ae127443c707c6de75e7bce0e3d827620d5ef4a5c8b40ef2b89b2c4bd352b619`.
- Source observation: `data/latest.json` records the official Hotspawn fixtures endpoint, CS2 pick'em lobby and general lobby as HTTP 200 at `06:16:00–06:16:02Z`; all four retained inventory counts are 92 and `fixture_conflicts` is empty. Six IDs were added and two removed relative to the previous comparison snapshot.
- At the snapshot clock, 31 of 92 rows are open; 61 are retained but not open by the sourced status/time checks. They remain visible on **All matches** and are not treated as upcoming recommendations.
- Open-row methods: **16 strict Polymarket exchange lines, 3 labelled wide Polymarket lines, 3 researched listing estimates, 6 Valve-standings model lines, and 3 model lines using HLTV's dated Valve-ranking mirror**. This is 22 market-derived rows and 9 model-derived rows; it is not 31 bookmaker quotes.
- The 15 non-featured rows (all methods other than the strict `exchange` tier) each record an HLTV attempt before the Pinnacle attempt. Rows that remain unpriced by those checks continue through the recorded wide-exchange, sportsbook-listing or Valve model stages. No research-only or blank row remains in this snapshot.

### Sources and limitations

The source links retained with the rows and source-check receipts are available in [the evidence ledger](../../evidence.html), [methodology/source health](../../sources.html), and [`data/latest.json`](../../data/latest.json). The collector uses:

- [Hotspawn CS2 Pick'ems](https://play.hotspawn.com/cs2-pickems), [Hotspawn lobby](https://play.hotspawn.com/lobby), and the [Hotspawn scheduled-fixtures feed](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1) for fixture identity, inventory and locks only.
- [HLTV match pages](https://www.hltv.org/matches) for fixture identity/ranking/lineup research; HLTV community votes are excluded. Three model rows use the dated [HLTV Valve-ranking view](https://www.hltv.org/valve-ranking/teams/2026/october/24) as the explicitly labelled point-source mirror where the official monthly file cannot resolve the team.
- The [Polymarket Gamma API](https://gamma-api.polymarket.com/sports), [Pinnacle public esports moneyline API](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight), and [Valve's official Regional Standings repository](https://github.com/ValveSoftware/counter-strike_regional_standings). The model is a derived estimate from Valve points/formula, not a market quote or a Valve match prediction.
- [Thunderpick's CS2 page](https://thunderpick.io/esports/cs2-betting) returned HTTP 200 but no validated automated two-sided quote was extracted. The three accepted `bookmaker_fallback` rows are explicitly labelled **Listing estimate** and link to the [BO3.gg CS2 feed](https://api.bo3.gg/api/v1/matches?page%5Boffset%5D=0&page%5Blimit%5D=100&filter%5Bmatches.status%5D%5Bin%5D=upcoming&filter%5Bmatches.discipline_id%5D%5Beq%5D=1&sort=start_date&with=teams,tournament); that is a third-party listing feed, not a directly verified Thunderpick operator quote. Treat these three rows as the documented limitation they are, not as a sportsbook consensus.
- [GG.BET](https://gg.bet/en/esports/counter-strike) returned HTTP 403; the current run records an EGamersWorld listing recheck HTTP 403 and later skipped rechecks after that access restriction. Restrictions are not bypassed and a refusal is not interpreted as proof a book has no price.

Prices have source, freshness and match/lock gates. The page withholds expired rows rather than carrying old odds forward. The current `unresolved.html` and the `#unresolved-picks` section on the home page remain present even when the unresolved count is zero, and explain what is attempted and why a percentage may be blank.

## Findability and mobile checks

The landing page has an executive-summary/coverage strip with in-site routes to the updated pick board, the pick list on the page, the unresolved/limitations section and all matches. The separate pages are [Picks](../../picks.html), [Unresolved & limitations](../../unresolved.html), [All matches](../../matches.html), [Methodology](../../sources.html), and [Flagged for Review](../../review.html). A five-tab phone navigation and 44px tap-target rules are present.

I built the candidate output to `public/` from this exact snapshot, then ran `npm run test:browser`: **all 9 browser suites passed**, including viewport/accessibility/no-overflow scans at 320/390/768/1440px, expiry behavior, navigation and the first pick with both probabilities above the phone tab bar. `scripts.validate` on both the committed snapshot and built artifact reported **92 source rows, 31 probability calculations, 15 pages, 874 internal links/assets, 20 checksum checks and 234 displayed row instances**.

## Verification performed

| Check | Result |
| --- | --- |
| `python -m scripts.coverage_contract --snapshot data/latest.json --require-fresh` (at 06:27:28Z) | Pass: inventory fresh, 92 total, 31 actionable (22 market / 9 model), 0 unresolved/expired, 0 problems |
| `python verification-c6/audit_snapshot.py data/latest.json` | Pass: 92 retained rows, 0 arithmetic/field failures; the report itself cautions that this does not independently confirm the live upstream response or every identity premise |
| `python -m scripts.validate --data data/latest.json --site .` | Pass: 92 rows, 31 probability calculations, 15 pages, 874 links/assets, 20 checksums, 234 displayed row instances |
| Audit suite / integrity suite / verification-c6 tests | Pass: 9 / 5 / 12 tests |
| `npm run test:browser` (after a fresh local `scripts.build`) | Pass: all 9 suites |
| `python -m unittest discover -s tests -v` | **Not green:** 1,233 tests ran, 8 failures, 1 error, 1 skipped. Six failures are assertions that `assets/style.css` and `site/assets/style.css` must match. The other two failures and one error share the alias issue below. |

## Findings requiring review

### 1. Root Pages stylesheet differs from the tested artifact

GitHub's Pages API reports `build_type=legacy`, source `main:/`. The checked-in root `assets/style.css` hash is `c4f8aad18726328185a4cd6811df7ae3d9b803756897228e3f599ab6b209b989`; it has one unmatched opening brace at `@media(max-width:650px) and (max-height:700px)`. `scripts.build` copies `site/assets/style.css` instead: its hash (and the generated `public/assets/style.css` hash) is `c121ed1d231aa60bb2a7725c5487a5c0f96cf08ae9bdc558dbdf902ec692e897`, with the media block closed. The committed root `build-info.json` hashes the old root stylesheet, not the artifact stylesheet.

I independently rendered the committed root pages and the generated artifact in Chromium. At **390x844**, the root version's fixed tab bar begins at y=783 and the first card's probability rows begin at **y=798**, underneath the tab bar. The artifact version's same rows begin at **y=451**, well above it. At **320x568**, the root probability rows end at y=507, exactly where the tab bar begins. This reproduces the root-vs-artifact difference; the artifact browser suite passing does not prove the legacy root stylesheet is fixed.

The existing [Flagged for Review entry](../../review.html#session-d2a55add-css-unclosed-media-2026-10-24) already records the stylesheet irregularity. PR [#250](https://github.com/buffedlizard55-lab/MaltaProj4/pull/250) claims to synchronize the copies. At 06:40Z it was still open with `DIRTY` merge state; its `verify-build` had passed at 06:38Z on the PR branch's 88-row snapshot, not on the current 92-row snapshot. I did not edit either stylesheet because that scope is actively claimed by that session.

### 2. One alias row is not reproducible by the independent legacy verifier

The full local suite reports a shared independent-verifier failure for fixture **1083121**, Hotspawn `Projeto do KinGui` vs `MEIA NOITE`, where Polymarket's captured outcome label is `Tropa do KinGui`. The snapshot includes a dated `identity_sources` record with the exact opponent/start and corroborating fixture/lineup sources; the alias has already been published as **Needs review** at [the identity note](../../review.html#92e3275c-tropa-do-kingui-alias-2026-10-22). However, `tests/test_session_0cc1138a.py`'s separate `verify_0cc1138a.order_prices` path does not accept that recorded mapping and reports that it cannot map the Hotspawn label to the two Polymarket outcomes. This creates the two dependent failures and one error in the full suite.

The capture arithmetic and coverage contract pass, but I do not treat that as a substitute for resolving the contradictory verifier result. Either teach the independent verifier to consume only this exact, source-bound identity record (and test it), or withhold this row's borrowed market line until its identity is accepted. Do not broaden the alias with fuzzy matching. The current PR #250 diff adds model-arithmetic checks but does not include this alias reconciliation; I logged the request in `COORDINATION.md` rather than editing another session's verifier.

## Refresh and publication state

- `.github/workflows/pages.yml` is configured at four scheduled checks per hour (`:04`, `:19`, `:34`, `:49` UTC); `.github/workflows/refresh-watchdog.yml` checks every 10 minutes and dispatches the verified pipeline only when the published snapshot is overdue. GitHub may delay schedule events; the site uses an eight-hour evidence limit and withholds stale lines.
- Fresh publication run [40068512182](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40068512182) completed successfully at **06:32:24Z**. Its unit/audit/build/browser steps and the **“Verify live Pages bytes match this exact build”** step were green, so the workflow artifact was confirmed live at that time.
- The separate legacy branch-source deployment [40069996301](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40069996301) was still queued when last checked (06:40Z; its build job had succeeded, but deploy remained queued). Because the repository's Pages API reports `main:/`, I do not claim a final post-queue root deployment state here; it needs a fresh byte/layout verification after that run completes.
- Main's newer push verification [40069834693](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40069834693) remained queued at 06:40Z. PR #250's check passed at 06:38Z on its older 88-row branch snapshot, but the PR remained `DIRTY`; that is not verification of the current 92-row snapshot. The successful 400685 run predates main's newer commit and therefore does not make the current full local unit suite green.

## Disposition

The requested product surfaces and automatic fallback ladder are present and a fresh, verified data snapshot is published. Coverage was complete **at the recorded observation**, not guaranteed for future fixtures before Hotspawn lists them or a source posts a usable line. The root mobile stylesheet and the one identity/verifier contradiction remain explicitly documented; the final line must be withheld or the verifier reconciled before claiming every gate is green. No live price, pick or probability was edited by this audit.
