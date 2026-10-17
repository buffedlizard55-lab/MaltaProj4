# Hotspawn CS2 Scout

A simple, mobile-first pick dashboard for **every CS2 fixture returned by Hotspawn's lobby feeds**. Hotspawn establishes which matches belong on the board; it **never supplies win probabilities**.

## Find the picks

**[Executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/)** · **[Updated picks](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html)** · [All matches](https://buffedlizard55-lab.github.io/MaltaProj4/matches.html) · [Unresolved & research-only picks](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html) · [TWC analysis & Day-4 guidance](https://buffedlizard55-lab.github.io/MaltaProj4/analysis.html) · [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html) · [Sources & methodology](https://buffedlizard55-lab.github.io/MaltaProj4/sources.html) · [Evidence ledger](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html)

Both teams' probabilities, our fair decimal lines, the selected team and primary-source links are explicit. Phone layouts use readable match cards and a persistent bottom navigation. Search and tournament/status filters work without a login. All matches defaults to open entries; select **All entries** to see retained non-open records too.

**Full fixture coverage with tiered picks.** Every open fixture is attempted in a fixed order and its outcome is published: strict exchange gate → HLTV identity research → Pinnacle bookmaker line → labelled wide-quote tier → **researched book-listing line** (a dated, identity-verified two-way price read from a book's own listing page, which outranks our own model) → **our originated VRS model line** (Valve's official standings points through Valve's own published formula and calibration, with HLTV lineups confirming each roster) → HLTV-verified ranking tiers that can produce a **research-only pick with no published percentage**. If none applies, the row stays blank and unresolved. The executive summary links the pick board, the unresolved section (every pick without a market line, with its limitation) and the tournament analysis (day 1 to day 5 of the Thunderpick World Championship, including the Saturday 17 October semi-final guidance and the Sunday 18 October bracket) directly, and it carries its own "Unresolved picks & their limitations" notice that counts the TWC items with no price and links to them; phone layouts use tappable cards plus a persistent bottom navigation bar, and the summary also carries a "then next" queue of the following picks with their prices and a jump bar to today's picks, the later board, the unresolved section and the coverage line. The day-4 analysis block ends with a **"What still has no price, and why"** table (the Sunday third-place decider and best-of-five grand final have no participants yet, so no market exists and no percentage is published for them) and with the sourced scoring facts, including Hotspawn's streak bonus for consecutive correct picks. The project is independent of Hotspawn and betting operators and does not place bets or submit picks.

## Evidence and calculations

1. Reverse-engineer only Hotspawn's public page data: compare the [requested lobby](https://play.hotspawn.com/lobby), [CS2 page](https://play.hotspawn.com/cs2-pickems) and [exact tenant-1 scheduled-CS2 query](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1) found in its public JavaScript. Compare IDs **and primary fields**, not just a card count. Retain all returned tiers, including past scheduled records; do not call them upcoming or completed without evidence.
2. Discover CS2 in [Polymarket's official registry](https://gamma-api.polymarket.com/sports) and paginate active events. Require a whole-match moneyline, two exact matched teams, exact UTC start, fresh observation/update, open accepting market, finite prices, two-sided quote, at least $100 liquidity and spread no greater than 25 percentage points. Known Hotspawn series format must agree. These quality thresholds are project policy, not proven forecast calibration.
3. **Only missing picks** enter fallback research: [HLTV](https://www.hltv.org/matches) first (identity, rankings, lineups), then [Pinnacle's official public esports lines](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight) (before the wide exchange tier, because a sharp bookmaker line outranks a wide quote), then researched book-listing receipts (a dated, replayable two-way price from a book's own page, captured by hand where the site refuses the automated runner), then Thunderpick/GG.BET access checks. Additional investigation covers Rivalry, Stake and official organization identities. Access checks are not presented as functioning quote adapters. No access restrictions are bypassed.
4. Produce **our calculated fair lines**: for decimal odds `d₁,d₂`, let `qᵢ=1/dᵢ`, then `pᵢ=qᵢ/(q₁+q₂)`. For exchange outcome prices, normalize the two weights to sum to one. Our fair decimal price is `1/pᵢ`; the pick is the larger probability. A genuine equal-price pair has no directional edge. These are derived market estimates, not bookmaker consensus or a calibrated independent performance model.
5. Keep accepted featured/primary picks; fallbacks do not overwrite them. Never substitute Hotspawn/HLTV fan votes, guessed aliases, academy squads, an HLTV-rank-to-probability formula or a default 50/50. Narrow organization-name mappings have primary links in [the identity register](data/identities.json); roster continuity is not inferred.
6. **Wide-quote tier** (`exchange_wide`): a two-sided exchange quote that fails only the 25-point spread ceiling may still price a fixture when the market is open, accepting orders, fresh, and holds at least $100 of liquidity, with spread ≤ 60 points. The real spread, the strict rejection and a low-confidence warning are published; below $100 liquidity is never accepted. **Research-only tiers, no numbers**: with no usable line, an exact HLTV fixture identity can produce a pick with blank probabilities and blank fair odds. When both teams' world rankings are exposed on that fixture page the better-ranked team is the pick (`research_rank`); when exactly one team carries a published world ranking there and the other appears in the same fixture without one, that team is the pick (`research_rank_single`). Either way the row stores both teams' evidence — fixture label, HLTV label, rank, ranking link, and the primary source of any label mapping — so the pick is re-derivable from the snapshot alone, and both validators reject a stripped or edited row.
7. Preserve original fields, quote inputs, observation/update timestamps, response hashes, source receipts and rejected-quote reasons. Every match links to an evidence entry and an official Hotspawn page/API. JSON and CSV exports keep unknown values blank/null. CSV includes quote observation/update, expiry, snapshot and build timestamps; downloading an old file does not renew a line.
8. **Originated line** (`model_vrs`, [scripts/vrs.py](scripts/vrs.py)): only where no market line passes its gates. Inputs are [Valve's official Regional Standings](https://github.com/ValveSoftware/counter-strike_regional_standings) points; the expected win rate is Valve's own `fit.js` formula (Glicko, rating deviation 75), calibrated with the slope from Valve's published model-fit chart (0.7986, applied symmetrically). A Valve label is used only when unique, or when the HLTV lineup shares at least three players with exactly one listed roster (Valve's roster rule). Beside market rows the model line is shown for comparison and never changes the pick. The build validator and the independent auditor recompute every model row; [a vendored copy](data/vrs/) of the official file is used only if the live fetch fails.

Research: [Day-4 review, coverage audit & scoring facts](research/day4-37bf28f4/DAY4-REVIEW.md) with its [field-level source receipts](research/harvest-37bf28f4/day4-live-reads.json), [Day-2 review & Day-3 guidance](research/day2/DAY2-REVIEW-2026-10-15.md), [Day-1 review](research/day1/DAY1-REVIEW-2026-10-15.md), [original implementation findings](research/FINDINGS.md), [15 October integration/source review](research/INTEGRATION-2026-10-15.md), [independent row audit](research/current/ROW-AUDIT.md), [independent capture comparison](research/current/snapshot-audit.json). All observed counts are dated snapshots, not permanent coverage promises.

## Automatic operation — no routine input

[The publication workflow](.github/workflows/pages.yml) attempts a refresh **four times an hour at :04, :19, :34 and :49 UTC**. A separate watchdog checks the published snapshot every 10 minutes and dispatches the same verified workflow when the snapshot is more than 90 minutes old, subject to a cooldown and dispatch budget. These are trigger targets, not a guarantee of successful source access or GitHub delivery; the public site expires stale evidence rather than presenting it as current. The schedule was tightened after delayed and missed runs; see `research/refresh-ab18fe2a/DIAGNOSIS.md` for the historical measurements. Main changes also refresh. PRs run offline verification without fetching external sources or publishing.

- Restore the latest successful snapshot from Actions cache; `data/latest.json` is the committed bootstrap, not the permanently live dataset. The production JSON updates on Pages without data commits to main. The repository also includes a small verified static root fallback because the pre-existing Pages configuration is legacy `main:/`; scheduled updates still use the validated artifact, not manual edits. To regenerate that fallback after an intentional code update, run `python -m scripts.stage_legacy` after build and validation.
- Re-query all three Hotspawn views, discover new matches automatically, compare inventory changes, and research only uncovered picks. If sources disagree or one fails, retain the union and flag coverage. Still-open previous-only rows survive partial discovery with unverified membership and **no new pick**.
- Wrong-game, malformed, unavailable or unexpectedly empty discovery cannot erase the last good inventory or renew its freshness timestamps.
- Picks expire at the **earliest** fixture-age TTL, quote observation/update TTL, Hotspawn lock, match start or bookmaker cutoff. The maximum evidence age is eight hours. Build-time and browser-time checks apply to the table, featured card, evidence labels and counts. With JavaScript disabled, explicit warnings and per-line observation/expiry times remain visible.
- A failed test/build prevents publication. Source access failures become visible review findings, not invented data. Full raw responses and test reports are retained as Actions artifacts for seven days; durable row-level evidence is in the published JSON.
- Deployment verifies every public file against the exact build's SHA-256 manifest. [Build receipt](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) · [Workflow history](https://github.com/buffedlizard55-lab/MaltaProj4/actions).

GitHub may delay scheduled jobs or disable inactive public-repository schedules. Public sources can change or restrict access. The 15-minute publication schedule and 10-minute watchdog are targets, not guarantees; expiry warnings prevent a failed refresh from appearing fresh. A single row that the independent audit cannot reproduce is withheld ([scripts/quarantine.py](scripts/quarantine.py)) rather than blocking every verified row; snapshot-level failures still block publication. See [COORDINATION.md](COORDINATION.md) for the actual PR/merge/deployment record rather than assuming a branch build means a live site.

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

The separately completed d1bae160 dashboard and its eight passing tests are retained verbatim in [the integration handoff](research/handoffs/d1bae160/README.md), with its main history merged rather than overwritten. Six old public routes redirect to the current views; only one workflow publishes on the scheduled refresh. The older date-only matching/seeded quotes are not silently promoted past the stricter current UTC/market/expiry gates.

## Code map

| Scope | Purpose |
| --- | --- |
| `scripts/inventory.py` | Three-source parity, conflict blocking and last-good inventory retention |
| `scripts/core.py` | Strict identity matching, accepted quote gates, calculations and shared expiry |
| `scripts/hltv.py`, `scripts/refresh.py` | Missing-pick research (identity, rankings, lineups) and read-only collection with source receipts |
| `scripts/vrs.py`, `data/vrs/` | Originated lines from Valve's official standings with Valve's formula and calibration |
| `scripts/quarantine.py` | Withholds any row the independent audit cannot reproduce, before the audit gate |
| `scripts/build.py`, `site/assets/` | Pre-rendered mobile dashboard, progressive enhancement and build manifest |
| `scripts/validate.py`, `tests/` | Raw-evidence replay, source/link/hash checks and unit/browser regressions |
| `audits/`, `verification-95b588c2/`, `verification-c6/` | Preserved independent audits, including historical findings now fixed |
| `scripts/backfill_quotes.py`, `research/current/quotes/` | Applies retained primary-source receipts between scheduled refreshes; every value recomputed, never hand-typed |
| `data/analysis.json`, `analysis.html` | TWC Day-1 to Day-3 reviews, the live Day-4 block (semi-final cards, contract/streak scoring facts, the unpriced Sunday table), model-vs-market screen; research only, never a probability input |
| `scripts/twc_day4_37bf28f4.py` | Re-runnable, idempotent applier for the day-4 block: scoring facts, streak bonus, Sunday schedule, group structure, day-2 map sourcing and the withdrawn-count correction |
| `data/review-notes.json` | Sourced findings published on Flagged for Review |
| `research/`, `COORDINATION.md` | Primary-source research, preserved handoffs and integration record |

Missing data is an intentional, visible result—not a placeholder to fill with guesses. No winning outcome, profitable strategy, current roster or complete sportsbook coverage is certified.
