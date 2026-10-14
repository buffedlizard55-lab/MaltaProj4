# Research and verification findings — 14 October 2026

## Scope and provenance

The repository initially contained only a one-line README. There was **no existing featured-pick implementation** to preserve or repair. The new primary method uses independently sourced exchange prices; fallback research is restricted to otherwise unresolved fixtures.

The initial environment permitted raw outbound requests only to package registries and GitHub. Read-only public-source requests were therefore verified in the GitHub Actions refresh environment as well as via page retrieval. This is why sandbox `curl` failures are not reported as Hotspawn downtime.

## Hotspawn reverse engineering

Primary pages: [CS2 lobby](https://play.hotspawn.com/cs2-pickems) and [general lobby](https://play.hotspawn.com/lobby).

Inspected public assets:
- [Main Angular bundle observed during research](https://play.hotspawn.com/main-YP6WRS3L.js).
- [Fixture service bundle](https://play.hotspawn.com/chunk-KNRGAKZR.js).
- [Lobby component bundle](https://play.hotspawn.com/chunk-RNH2KFU4.js).

Bundle filenames can change on deployment; the production collector does not rely on those filenames.

Findings checked against the public HTML and bundle:

1. `script#ng-state` includes Angular transfer-cache records with `u` (URL), `b` (body), `s` (status). A record ending in `/api/v1/fixtures` holds the fixture array. Another embedded record holds official match permalinks. We read that embedded data; no administrative write or authenticated endpoint is called.
2. The Hotspawn tenant is `1`; its game configuration includes CS2 and LoL. The CS2 lobby calls `getFixtures({sport_alias: ..., status:"scheduled", tenantId: ...})`. The service copies those exact parameter names into the query string.
3. Exact public query: <https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1>. The **unfiltered** endpoint also includes irrelevant historical/test fixtures and must not establish lobby coverage.
4. Both the scoped API and the page returned 88 CS2 IDs in the initial comparison. The visible page rendered only open cards; the filters included older scheduled records. “Matches this week”, “total feed records”, and “open picks” have different meanings and are not interchangeable.
5. `scheduled_start_time` and `lock_time` are epoch milliseconds, so UTC can be established without assuming a browser timezone. The rendered pages showed timezone-dependent wall-clock times. We use the raw timestamps and display UTC explicitly.
6. All returned CS2 rows remain visible. Past locks, past starts and contradictory `scheduled` plus `end_time` fields are flagged, not removed or assumed to be completed outcomes.
7. `participants*_picked_percent` and `total_picks` are intentionally excluded from stored fixture evidence and all calculation inputs. A test confirms arbitrary changes to those fields cannot affect picks.
8. `best_of` is often null. It stays blank. External BO metadata is not used to silently fill missing Hotspawn facts.

## External sources

### Polymarket (primary)

Official [sports registry](https://gamma-api.polymarket.com/sports) identified `sport=cs2`, `series=10310` in the observation. Production discovers this dynamically instead of guessing tag IDs. The generic Games tag includes non-CS2 markets and is not sufficient.

Official documentation: <https://docs.polymarket.com/market-data/discover-markets>.

The official events response contains `markets`, source outcome names, binary `outcomePrices`, `sportsMarketType`, `gameStartTime`, `updatedAt`, `bestBid`, `bestAsk`, liquidity, and active/closed/accepting-order flags. It also supplies explicit team abbreviations. For example, its “Sashi Esport” team entry publishes abbreviation `sashi`, and its Copenhagen team entry publishes `eac`; those are attributable mappings rather than guessed suffix removal. The complete used team records are retained with accepted evidence.

Important irregularity: `active=true&closed=false` **at event level** can still return old events whose child markets are closed. Child state, actual match start and whole-match type must be checked. Map winners, totals and handicaps must not be substituted for series winner.

Examples inspected directly (prices are not hardcoded):
- <https://polymarket.com/event/cs2-ast10-sashi-2026-10-14>
- <https://polymarket.com/event/cs2-furia-bb3-2026-10-14>
- <https://polymarket.com/event/cs2-wbt-ence-2026-10-15>

The WBT/ENCE page showed zero traded volume at inspection and nontrivial price/spread differences across UI quote types. The application stores API outcome prices and labels the result as a calculated market estimate, never a directly executable betting price. Wide spreads are flagged. Liquidity/spread gates are project policy, not a claim of forecast calibration.

### HLTV (first research fallback)

[Match list](https://www.hltv.org/matches) initially returned HTTP 403 in one raw-client probe, then succeeded with the production HTTP client. Accessibility must therefore be measured on each run, not assumed constant.

Verified current list selectors: `.match-teams`, `.match-teamname` and `.match-time[data-unix]`. Duplicated “time/event” listings are deduplicated by match URL.

Inspected individual pages:
- [PCIFIC vs Ryvex](https://www.hltv.org/matches/2399463/pcific-vs-ryvex-cct-2026-europe-series-12-closed-qualifier).
- [Banda Chuya vs 6666](https://www.hltv.org/matches/2399462/banda-chuya-vs-6666-cct-2026-europe-series-12-closed-qualifier).
- [WBT vs ENCE](https://www.hltv.org/matches/2399420/wbt-vs-ence-elisa-breakout-series-2).
- [WBT team profile](https://www.hltv.org/team/13683/wbt).

The retrieved betting tables showed promotional text, not numeric two-way bookmaker odds. `Pick a winner` percentages elsewhere on the same page are fan votes, not betting probabilities. Official HLTV ranking values can provide context, but a ranking ordinal does not justify an invented win percentage. No calibrated empirical model has been established, so this implementation deliberately does not issue rank-derived picks. Exact-match context and source links are preserved for unresolved fixtures.

`WROTBERRY`/`WBT` and other renamed/academy labels require stronger primary-source identity evidence than a similar name or search snippet. They remain unresolved instead of automatically merging organizations/rosters. HLTV and Polymarket naming differences are shown as candidate links for review.

### Pinnacle (working bookmaker fallback)

Official public endpoints inspected:
- <https://guest.api.arcadia.pinnacle.com/0.1/sports/12/leagues>
- <https://guest.api.arcadia.pinnacle.com/0.1/sports/12/matchups?withSpecials=false>
- <https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight>

Sport 12 includes multiple esports, so `league.name` must start with `CS2 - `. Matchup IDs join price rows to fixture participants; `designation` maps prices to home/away. Only a pending non-live parent `matchup`, period `0`, open non-alternate `moneyline`, two sides and a future cutoff are accepted. American odds are converted to decimal before removing overround. Every accepted quote retains the raw matchup and raw price row.

Initial successful fallbacks included 9z/Aurora, Falcons/Ninjas in Pyjamas, and MIBR/BC.Game. Coverage and odds may change. The price feed does not provide a price-change timestamp in these rows; observation time/cache age and this limitation are shown. A single bookmaker is not a market consensus.

### Thunderpick and GG.BET (limitations, not fabricated adapters)

- Official [Thunderpick CS2 page](https://thunderpick.io/esports/cs2-betting) sometimes returned HTTP 403 and sometimes a small JavaScript application shell. Browser inspection in the runner reached a Cloudflare security-verification page, not validated lines. No bypass was attempted. The HTML shell's HTTP 200 is not claimed as successful odds retrieval.
- Official [GG.BET CS2 page](https://gg.bet/en/esports/counter-strike) returned a regional-access message in page retrieval and HTTP 403 from the runner. No proxy, login or bypass is used.
- Other odds aggregators surfaced in search, but unattributable secondary quotes were not promoted to verified bookmaker facts. HLTV's specialist context is distinguished from an operator's own quote.

## Explicit identity register

BetBoom / BetBoom Team / BB Team were checked against the [official organization page](https://betboom.team/) (uses “BB TEAM”, “BetBoom Team” and identifies the CS2 roster) and the indexed excerpt of the [official store about page](https://shop.betboom.team/page/about-us) (uses “BetBoom” and “BetBoom Team”). A subsequent full-page retrieval of that store URL failed; that supplementary check is not represented as a successful direct fetch. See `data/identities.json`. All other unregistered aliases remain rejected, and exact opposing team + UTC start are still required. These aliases do not equate a main roster with an academy roster.

## Publication and verification limits

- Every primary fixture fact is compared with its stored source row; every accepted probability/fair line is recomputed independently.
- Evidence JSON contains retrieval times, raw accepted fields, primary URLs and full-response SHA-256 receipts. Production refresh archives full responses as short-lived Actions artifacts instead of accumulating large datasets in Git.
- The application checks all local links/assets/anchors and source-link presence. A live external site may require region/login/browser checks later; successful source observation is not a guarantee that every external URL stays reachable forever.
- Phone/tablet/desktop Chromium and axe checks are executable, not a claim of certification on every physical device or assistive technology.
- Unknown facts remain null/blank. Published flags do not block deployment. Any build, arithmetic, identity, local-link or accessibility regression does block deployment.
