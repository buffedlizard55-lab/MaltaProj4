# Final integration research — 15 October 2026

Session `c4d25599`, fixed branch `arena/c4d25599-maltaproj4`. Earlier work and boards are preserved; this report distinguishes checks actually repeated here from historical reports.

## Observed inventory and current-source audit

The **08:40 UTC capture** has 80 CS2 entries, 17 open by source start/lock/end fields, 12 accepted probability pairs, and 5 unresolved open matches. The scoped API, CS2 HTML hydration and general lobby hydration all contain the same 80 IDs, with no conflicting compared primary fields. These are dated capture counts, not permanent or guaranteed coverage.

- [Official requested lobby](https://play.hotspawn.com/lobby)
- [Official CS2 page](https://play.hotspawn.com/cs2-pickems)
- [Exact public scoped fixture request](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1)
- [Current-source research workflow](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38707288305)
- Retained response: `current/fixture-source.json`; source checks and accepted/rejected raw observations: `current/refresh.json`.
- `current/snapshot-audit.json`: the preserved **independent** 95b588c2 auditor compares all 80 rows against the separately retained primary response and independently reproduces all 12 price calculations with Decimal arithmetic. The wrapper changes input locations, not the audit assertions.
- `current/ROW-AUDIT.md`: a second independent implementation (c6e9f285) checks every stored source field and calculation, without importing production normalization or probability functions.

The 63 non-open entries are not asserted to be completed results. Hotspawn retains old `scheduled` rows. Missing best-of remains null. Crowd percentages are excluded from fixture evidence and all calculation inputs.

## Research of missing picks (not replacement of featured picks)

1. **HLTV first:** the runner successfully read the current list and exactly matched applicable individual fixtures. It retrieved rankings and match context, but the captured betting rows did not provide a verified numeric bookmaker pair. Fan voting percentages are not odds. [HLTV matches](https://www.hltv.org/matches).
2. **Pinnacle:** read its official public [matchups](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/matchups?withSpecials=false) and [straight markets](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight). Parent CS2 matchup, pending/non-live, period zero, non-alternate open moneyline, home/away alignment, future cutoff and exact UTC identity are required. MIBR / BC.Game was an accepted fallback in this capture. The bookmaker supplies no price-change timestamp in the captured row; observation time is not silently substituted as an update time.
3. **Other official books:** [Thunderpick](https://thunderpick.io/esports/cs2-betting) and [Rivalry](https://www.rivalry.com/esports/counter-strike-betting) returned application shells to the runner; [Stake](https://stake.com/en/sports/esports/counter-strike) returned 403. [GG.BET](https://gg.bet/en/esports/counter-strike) returned 403 from the runner and an explicit regional restriction through separate page retrieval. No bypass was attempted. Separate rendered-page retrieval showed Thunderpick prices, but without a repeatable validated quote/UTC adapter for scheduled automation; these were not copied into production as fresh automatic prices.
4. **Identity research:** narrow Falcons / Team Falcons and ROUNDS / RoundsGG mappings were confirmed against the organizations' own pages and recorded in `data/identities.json`. This resolved the missing 9z / Falcons exchange match without fuzzy suffix removal or academy substitution. Official references: [Falcons Store](https://store.falcons.sa/en), [ROUNDS CS2 announcement identifying its @roundsgg handle](https://rounds.gg/2026/05/01/rounds-cs2-attend-vrs-lan-tournament-in-sweden-with-full-hltv-coverage/). Primary response receipts and excerpts are in `current/receipts.json` / `current/excerpts.json`.

### Unresolved limitations in this capture

| Hotspawn fixture | Limitation | Review evidence |
| --- | --- | --- |
| [WROTBERRY / ENCE](https://www.hotspawn.com/matches/wrotberry-vs-ence-elisa-breakout-series-2-1080281) | External listings use WBT; no checked primary statement explicitly establishes this alias. | [WhiteBIT's own announcement identifies WBT as WhiteBIT Team](https://blog.whitebit.com/en/w-group-launches-whitebit-team/); [HLTV WBT / ENCE](https://www.hltv.org/matches/2399420/wbt-vs-ence-elisa-breakout-series-2). The announcement was readable through page retrieval, while direct runner access returned 403. |
| [WROTBERRY / BOJONG](https://www.hotspawn.com/matches/wrotberry-vs-bojong-elisa-breakout-series-2-1080283) | Same unresolved organization/roster label; no odds transfer. | [Official external market](https://gamma-api.polymarket.com/markets/5583522). |
| [HAVU / RoundsGG](https://www.hotspawn.com/matches/havu-vs-roundsgg-elisa-breakout-series-2-1080286) | Primary exchange spread exceeds project policy; no accepted fallback pair. | [Official market](https://gamma-api.polymarket.com/markets/5583527), [HLTV context](https://www.hltv.org/matches/2399425/havu-vs-rounds-elisa-breakout-series-2). |
| [mellren / Privateer](https://www.hotspawn.com/matches/mellren-vs-privateer-cct-europe-2026-series-12-play-in-1081120) | External label Privateer Gaming remains unregistered; the candidate also had a wide spread. No inferred alias or invented price. | [Official market](https://gamma-api.polymarket.com/markets/5649536), [Privateer Gaming's official teams page](https://www.privateergaming.co.uk/teams), [HLTV match](https://www.hltv.org/matches/2399471/mellren-vs-privateer-cct-2026-europe-series-12-closed-qualifier). |
| [RoundsGG / Voca](https://www.hotspawn.com/matches/roundsgg-vs-voca-elisa-breakout-series-2-1080289) | Primary exchange spread exceeds policy; no accepted fallback pair. | [Official market](https://gamma-api.polymarket.com/markets/5583533), [HLTV context](https://www.hltv.org/matches/2399428/voca-vs-rounds-elisa-breakout-series-2). |

These rows are not permanently unpriceable; the scheduled refresh tries again. They are explicitly included in the executive summary, Unresolved picks and Flagged for Review. No full probability-coverage claim is made.

## Integration fixes and verification

- Reproduced inherited V01/V02/V03/V05 before fixing them: browser ignored source-update age; NaN/infinite liquidity passed; validator trusted derived identity and incomplete quality checks; a wrong-game response could erase the last good inventory.
- Added a single earliest deadline covering fixture age, price observation age, source update age, source lock/start and bookmaker cutoff. Build, rows, hero, evidence labels and coverage counts enforce it. Unpriced rows also close at lock. Expired priced rows can enter the unresolved view without a new download.
- Validator now reconstructs candidates from **raw** outcomes/participants/events/markets and replays market/sport/series/status/age/cutoff/liquidity/spread gates before comparing calculations.
- Three official inventory views are reconciled by ID **and fields**. Conflict rows cannot supply a pick. Normalized empty/wrong-game results retain the last good list. Partial discovery keeps still-open previous-only rows, marked unverified and blocked from pricing.
- Locally repeated 55 production Python tests, 9 original audit tests, 5 inherited integrity regressions and 12 independent audit tests: **81 passing Python tests**.
- Chromium/axe scans cover seven pages at 320, 390, 768 and 1440px: **28 scans**, with zero automated WCAG A/AA violations and no horizontal page overflow. Seven deterministic expiry scenarios cover the exact boundary, bookmaker cutoff, malformed deadline, fixture TTL, pick lock, unresolved-row lock, and an unexpired control. The inherited real-capture source-update expiry regression also passed.
- [Live-source integration CI run 38707429592](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38707429592) passed all collection/build/independent audit/browser steps. This was a **branch verification**, not a Pages deployment.
- Every internal page/link/anchor is checked. A generated build manifest hashes all public HTML, assets, JSON and CSV. Production deployment verifies live bytes against that exact manifest, not just an HTTP 200 or a familiar title.
- Old Actions versions produced Node 20 deprecation annotations. Maintained Node 24 versions were checked against official GitHub releases and pinned to commit SHA; versions/links are in `action-versions.json`. Ubuntu is pinned to 24.04 rather than relying on the announced imminent `ubuntu-latest` migration.

## Publication distinction

The repository's existing Pages mode was legacy `main:/`. Direct mode changes returned HTTP 403; a separate pages-write-scoped setup attempt also failed, and the unsupported setup job was removed. Artifact publication and live-route verification from main remain the integration workflow's responsibility. **The final PR, merge and actual deployment result are recorded in COORDINATION.md only after they happen.**

Automated tests verify what sources reported and whether calculations follow the declared method. They do not certify true winning chances, a current roster, access in every region, profitability, or the absence of upstream errors.
