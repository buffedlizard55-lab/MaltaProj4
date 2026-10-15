# Hotspawn CS2 Scout

A simple, mobile-first pick dashboard for **every CS2 fixture returned by Hotspawn's lobby feeds**. Hotspawn establishes which matches belong on the board; it **never supplies win probabilities**.

## Find the picks

**[Executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/)** · **[Updated picks](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html)** · [All matches](https://buffedlizard55-lab.github.io/MaltaProj4/matches.html) · [Unresolved picks](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html) · [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html) · [Sources & methodology](https://buffedlizard55-lab.github.io/MaltaProj4/sources.html) · [Evidence ledger](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html)

Both teams' probabilities, our fair decimal lines, the selected team and primary-source links are explicit. Phone layouts use readable match cards and a persistent bottom navigation. Search and tournament/status filters work without a login. All matches defaults to open entries; select **All entries** to see retained non-open records too.

**Full fixture coverage is not full probability coverage.** Unknown percentages stay blank. The executive summary includes a separate unresolved section and links to the limitations behind every missing pick. The project is independent of Hotspawn and betting operators and does not place bets or submit picks.

## Evidence and calculations

1. Reverse-engineer only Hotspawn's public page data: compare the [requested lobby](https://play.hotspawn.com/lobby), [CS2 page](https://play.hotspawn.com/cs2-pickems) and [exact tenant-1 scheduled-CS2 query](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1) found in its public JavaScript. Compare IDs **and primary fields**, not just a card count. Retain all returned tiers, including past scheduled records; do not call them upcoming or completed without evidence.
2. Discover CS2 in [Polymarket's official registry](https://gamma-api.polymarket.com/sports) and paginate active events. Require a whole-match moneyline, two exact matched teams, exact UTC start, fresh observation/update, open accepting market, finite prices, two-sided quote, at least $100 liquidity and spread no greater than 25 percentage points. Known Hotspawn series format must agree. These quality thresholds are project policy, not proven forecast calibration.
3. **Only missing picks** enter fallback research: [HLTV](https://www.hltv.org/matches) first, then [Pinnacle's official public esports lines](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight), then Thunderpick/GG.BET access checks. Additional investigation covers Rivalry, Stake and official organization identities. Access checks are not presented as functioning quote adapters. No access restrictions are bypassed.
4. Produce **our calculated fair lines**: for decimal odds `d₁,d₂`, let `qᵢ=1/dᵢ`, then `pᵢ=qᵢ/(q₁+q₂)`. For exchange outcome prices, normalize the two weights to sum to one. Our fair decimal price is `1/pᵢ`; the pick is the larger probability. A genuine equal-price pair has no directional edge. These are derived market estimates, not bookmaker consensus or a calibrated independent performance model.
5. Keep accepted featured/primary picks; fallbacks do not overwrite them. Never substitute Hotspawn/HLTV fan votes, guessed aliases, academy squads, a rank-to-probability formula or a default 50/50. Narrow organization-name mappings have primary links in [the identity register](data/identities.json); roster continuity is not inferred.
6. Preserve original fields, quote inputs, observation/update timestamps, response hashes, source receipts and rejected-quote reasons. Every match links to an evidence entry and an official Hotspawn page/API. JSON and CSV exports keep unknown values blank/null.

Research: [original implementation findings](research/FINDINGS.md), [15 October integration/source review](research/INTEGRATION-2026-10-15.md), [independent row audit](research/current/ROW-AUDIT.md), [independent capture comparison](research/current/snapshot-audit.json). All observed counts are dated snapshots, not permanent coverage promises.

## Automatic operation — no routine input

[The publication workflow](.github/workflows/pages.yml) refreshes at **00:17, 06:17, 12:17 and 18:17 UTC**: a six-hour target within the requested 4–8-hour range. Main changes and workflow dispatch also refresh. PRs run offline verification without fetching external sources or publishing.

- Restore the latest successful snapshot from Actions cache; `data/latest.json` is the committed bootstrap, not the permanently live dataset. The production JSON updates on Pages without data commits to main. The repository also includes a small verified static root fallback because the pre-existing Pages configuration is legacy `main:/`; scheduled updates still use the validated artifact, not manual edits. To regenerate that fallback after an intentional code update, run `python -m scripts.stage_legacy` after build and validation.
- Re-query all three Hotspawn views, discover new matches automatically, compare inventory changes, and research only uncovered picks. If sources disagree or one fails, retain the union and flag coverage. Still-open previous-only rows survive partial discovery with unverified membership and **no new pick**.
- Wrong-game, malformed, unavailable or unexpectedly empty discovery cannot erase the last good inventory or renew its freshness timestamps.
- Picks expire at the **earliest** fixture-age TTL, quote observation/update TTL, Hotspawn lock, match start or bookmaker cutoff. The maximum evidence age is eight hours. Build-time and browser-time checks apply to the table, featured card, evidence labels and counts. With JavaScript disabled, explicit warnings and per-line observation/expiry times remain visible.
- A failed test/build prevents publication. Source access failures become visible review findings, not invented data. Full raw responses and test reports are retained as Actions artifacts for seven days; durable row-level evidence is in the published JSON.
- Deployment verifies every public file against the exact build's SHA-256 manifest. [Build receipt](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) · [Workflow history](https://github.com/buffedlizard55-lab/MaltaProj4/actions).

GitHub may delay scheduled jobs or disable inactive public-repository schedules. Public sources can change or restrict access. The six-hour cadence is a target, not a guarantee; expiry warnings prevent a failed refresh from appearing fresh. See [COORDINATION.md](COORDINATION.md) for the actual PR/merge/deployment record rather than assuming a branch build means a live site.

## Run locally

Python 3.11+ builds a dependency-free static front end. Node 22 is only for browser verification.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m scripts.build
python -m scripts.validate
python -m http.server 8000 --bind 0.0.0.0 --directory public
```

Refresh public sources (normal outbound internet access required):

```sh
python -m scripts.refresh --output runtime/latest.json
python -m scripts.build --data runtime/latest.json
python -m scripts.validate --data runtime/latest.json
python verification-c6/audit_snapshot.py runtime/latest.json --output runtime/row-audit.md
```

Browser and independent checks:

```sh
npm ci --ignore-scripts
npm run test:browser
python -m unittest discover -s audits -p 'test_*.py' -v
python verification-95b588c2/test_integrity.py
python -m unittest discover -s verification-c6 -p 'test_*.py' -v
python -m scripts.audit_capture --snapshot data/latest.json \
  --fixtures research/current/fixture-source.json --output runtime/capture-audit.json
```

The last command deliberately requires a separately retained primary response with the same fixture ID set. It must not assert a partial union is identical to a single API response. Browser tests start and stop their own local test server and check the GitHub Pages subpath, navigation, filters, evidence anchors, 320/390/768/1440px layouts, WCAG A/AA scans and exact expiry boundaries.

## Concurrent work preserved

The separately completed d1bae160 dashboard and its eight passing tests are retained verbatim in [the integration handoff](research/handoffs/d1bae160/README.md), with its main history merged rather than overwritten. Six old public routes redirect to the current views; only one workflow publishes on the six-hour schedule. The older date-only matching/seeded quotes are not silently promoted past the stricter current UTC/market/expiry gates.

## Code map

| Scope | Purpose |
| --- | --- |
| `scripts/inventory.py` | Three-source parity, conflict blocking and last-good inventory retention |
| `scripts/core.py` | Strict identity matching, accepted quote gates, calculations and shared expiry |
| `scripts/hltv.py`, `scripts/refresh.py` | Missing-pick research and read-only collection with source receipts |
| `scripts/build.py`, `site/assets/` | Pre-rendered mobile dashboard, progressive enhancement and build manifest |
| `scripts/validate.py`, `tests/` | Raw-evidence replay, source/link/hash checks and unit/browser regressions |
| `audits/`, `verification-95b588c2/`, `verification-c6/` | Preserved independent audits, including historical findings now fixed |
| `data/review-notes.json` | Sourced findings published on Flagged for Review |
| `research/`, `COORDINATION.md` | Primary-source research, preserved handoffs and integration record |

Missing data is an intentional, visible result—not a placeholder to fill with guesses. No winning outcome, profitable strategy, current roster or complete sportsbook coverage is certified.
