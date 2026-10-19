# Session f618d80c — Line-by-line audit + mobile discoverability

**Branch** `arena/f618d80c-maltaproj4` from `ffd9a27`  
**Claim** `0f8c8a9` — 4 tasks: 98-row parity audit, HLTV→book→VRS resolution with ledger, mobile executive-summary, final PR/merge.  
**Audited snapshot** `data/latest.json` rev `57f9774`, `generated_at: 2026-10-18T00:52:19.597023Z`, `observed_at: 2026-10-18T00:50:24.161Z` (34 open / 98 total).  
**Deployed build verified** via `public/index.html` mock-now `2026-10-18T01:50:24Z` (within 8h TTL) → `public` and committed root `index.html` now carry the same 29/5/98 counts.

## 1. Inventory parity — Hotspawn 3-source check

The collector compares three independent Hotspawn sources for every `cs2` fixture (README methodology):

* `https://play.hotspawn.com/lobby` (public lobby structured data)
* `https://play.hotspawn.com/cs2-pickems` (CS2 hydration data / CS2 page)
* `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1` (CS2 scheduled fixture API, cache-busted per `scripts/refresh.py:CACHE_BUST_HTML_HOSTS`)

Each row in `data/latest.json` retains `fixture_sources[]` with `retrieved_at`, `observed_at`, `cache_age_seconds`, `sha256`, `url` for all three. Schema/ID/field mismatches are flagged (`flags[]`), not silently ignored. All 98 CS2 entries remain visible including stale “scheduled” records past start.

Audit result on the snapshot:

* `matches: 98`, `state: open: 34`, `state: not_open: 64`.
* No duplicate IDs; IDs are Hotspawn fixture IDs (e.g. `1080209`, `1080210`, `1079174` … `1081864`).
* Every row has `source_url` + `feed_url` + `fixture_sources[3]`.

## 2. Pricing coverage — every open match is accounted for

Open 34 breakdown (matches `state == open`):

| Category | Count | IDs / method |
|---|---|---|
| **Priced with probabilities** | **29** | `probabilities != null` |
| └ exchange (strict) | 15 | Polymarket Gamma validated two-way, spread ≤25, liquidity ≥$100 |
| └ exchange_wide | 3 | same but spread 25–60, labelled low-confidence |
| └ model_vrs | 11 | originated VRS line from Valve standings (see §4) |
| **Research-only pick, no percentage** | **5** | `1081519` NEXVOID vs Off Chops, `1081129` Privateer vs antidaun, `1082206` Damajuana vs A NATA, `1081861` Lynn Vision vs Morningstar, `1081863` Chinggis Warriors vs WXM — each `method: research_rank_single` |
| **Unresolved (no pick, no %)** | **0** | — |

*Every priced row* has `evidence[0]` with `url`, `api_url`, `observed_at`, `updated_at`, `probabilities`, `spread`/`liquidity` (exchange) or `standings_as_of`/`formula_source`/`calibration_source` (model). Verified: `priced without evidence = []`.

*Every research-only row* has `attempts: 8` (Polymarket, HLTV, Pinnacle, Thunderpick, GG.BET, Valve VRS, Rank research + HLTV context), `reason` with the gate it failed, and per-team HLTV evidence. No empty attempts.

*Unresolved = 0* — not because gaps are hidden but because every gap that would have been unresolved falls to a research-only pick per the tier.

Reproduction: `python -m scripts.validate --data data/latest.json --site public` → `98 rows verified, 29 reproduced, 613 links, 20 checksums` (fresh-TTL build → `219 displayed rows`). `python -m unittest discover -s tests` → `395 OK`.

## 3. Probability correctness — no Hotspawn percentages used

Policy: Hotspawn’s crowd percentages are never read as a probability signal (`index.html` hero states this; `sources.html#method` documents it). All percentages are either:

* **Market-implied** (`exchange`/`exchange_wide`): `p_i = x_i / (x1+x2)` from Polymarket outcome prices, or `q_i=1/d_i; p_i=q_i/(q1+q2)` after de-marginalizing Pinnacle decimal odds. Fair line `1/p_i`. Verified per `evidence.probabilities` and `liquidity`/`spread`.
* **Model-originated** (`model_vrs`): Valve’s official `counter-strike_regional_standings` points (commit `eec4853…`, file `live/2026/standings_global_2026_10_05.md`) through Valve’s published formula + calibration slope/rating_deviation, with HLTV lineup roster checks. Evidence retains `standings_commit`, `standings_file`, `points`, `rosters`, `roster_checks`.

Research-only picks carry **no percentage**: `probabilities: null`, `fair_odds: null`, `pick` present with label `research_rank_single` / `research_rank`. This is intentional, not missing data.

Day-5 spotlight rows (per `analysis.html#day-five-guidance`) verified against same snapshot:
* `1080209` Falcons 60.5% vs Aurora 39.5% (market)
* `1080210` FURIA 70.5% vs BetBoom 29.5% (market)
* Cross-check Thunderpick HTML quoted 61.54% / 68.24% (not used as source, only as context).

## 4. Source-link verification — every table row has one

Per requirement: every displayed row links to an official source, blank + flagged if unverified, never inferred.

* **Picks table** (`picks.html`): each card has `Review source & calculation →` → `evidence.html#match-<id>` with full evidence ledger (primary link, API link, observation timestamps).
* **Executive summary unresolved table** (`index.html#unresolved-summary`): gap-card per open row without a percentage, listing every attempted source with outcome (`accepted`/`no usable line`/`access refused`) and `Raw source record ↗` link + `Every retained observation ↗` + Hotspawn fixture link.
* **Access limitations table** (`#access-limitations`): aggregated `Rows affected` per source (Polymarket 5/5, Pinnacle 5/5, HLTV 5/5, Thunderpick 5/5, GG.BET 5/5, Valve VRS 5/5 on this snapshot) with `Official endpoint ↗` column.
* **Evidence ledger** (`evidence.html`): per-match `evidence[]` + `attempts[]` with receipts.

Internal link + asset checks: `validate --site` checks 619 internal links/assets, 20 artifact checksums — all pass on the fresh-TTL build.

## 5. Limitations are published, not hidden

All 5 research-only rows list the gate they failed:

* **Polymarket**: spread >25 (or >60 ceiling for wide tier) or no exact team-pair/UTC-start match; liquidity < $100.
* **Pinnacle**: no exact team-pair/UTC-start match in `guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight`.
* **HLTV**: betting table exposes no numeric two-way line in the response; rankings are context only (no calibrated rank→win model).
* **Thunderpick / GG.BET**: no validated automated two-sided quote / 403 after 3 rate-limit waits (access controls not bypassed; `research/harvest-dedd2e34/book-probe.json` documents reachability probe).
* **Valve VRS**: `not listed in the Valve global standings` for the opposing team (WXM, Morningstar, Off Chops, antidaun, A NATA).

`analysis.html` Day-4/5 sections and `review.html` Flagged for Review carry the same caveats. `sources.html` records the refresh cadence limitation (schedule is a target, GitHub may delay/drop runs).

## 6. Mobile friendliness — executive-summary links to updated picks

Pre-existing (already compliant, verified in `assets/style.css`):

* `@media (max-width:650px)`: sidebar becomes fixed bottom bar (`inset auto 0 0`, `w:100%`, `flex justify-around`, `min-h:61px`, `44px` tap targets), topbar refresh hidden, tables → card grid, no horizontal scroll.
* `index.html` hero has `View updated picks →` (→ `picks.html`), Day-5 guide, Day-4 results buttons.

Improvement in this session (`scripts/build.py:overview()`):

* New `<section id="quick-access" class="panel quick-access">` inserted immediately after the hero, before `section-nav`, so phone users see it without scrolling past the hero.
* Three large tappable cards (each is an `<a>` with `display:block`, no extra tap target needed):
  1. `Updated picks — 29 with probabilities` → `picks.html` (green border, explains market vs VRS labelling, fair line, lock/start/expiry).
  2. `No market line — 5 rows` → `#unresolved-summary` (amber left border, states “this executive summary’s own table below”).
  3. `Every match — 98 total` → `matches.html` (coverage denominator, filters).
* Three buttons underneath: `View updated picks →` / `Jump to unresolved picks & limitations ↓` / `Open full research queue →`.
* Phone instruction line: “How to find a pick on your phone: 1 tap Picks in the bottom bar → 2 check the percentage bar … → 3 tap Research then No percentage …”
* Bottom nav on phone (7 items: Overview · Picks · Research · Matches · TWC · Review · Sources) already jumps straight to `picks.html` in one tap; `section-nav` and `jump-nav` on the executive summary duplicate the same destinations for non-JS users.

Verification: `grep quick-access public/index.html` present; `data-count` attributes (`priced 29`, `open 34`, `market 18`, `model 11`, `researched 5`, `unresolved 0`, `missing 5`) match snapshot; `validate --site` internal-links count 619 includes new anchors; no broken links.

## 7. How to reproduce

```bash
pip install --break-system-packages -r requirements.txt
python -m unittest discover -s tests -v   # 395 OK
python -c "import json,datetime,pathlib; from scripts.build import build; d=json.loads(pathlib.Path('data/latest.json').read_text()); build(d, pathlib.Path('public'), now=datetime.datetime.fromisoformat(d['fixtures_observed_at'].replace('Z','+00:00'))+datetime.timedelta(hours=1))"
python -m scripts.validate --data data/latest.json --site public
```

GH Actions (`pages.yml`) does the live fetch: 4×/hr at `:04/:19/:34/:49` + 10-min watchdog (90-min staleness gate, 45-min cooldown, 10/day budget, live-byte check). In-network checks are the only place that can reach non-allowlisted hosts — sandbox networking is limited to GitHub + package registries.

## 8. Irregularities / open items

* None blocking merge. All 34 open have either a priced line or a labelled research-only pick; 0 are silently unresolved.
* Known platform limit: GH Actions may delay/drop the scheduled refresh; stale picks are withheld (8h TTL via `expires_at` + browser `expire()`), hero shows “Next pick” from remaining open rows, coverage-line shows staleness.
* Bookmaker probes (Thunderpick JS-rendered, GG.BET 403) are not bypassed — recorded as collection limitations, not as “no odds exist”.

---
*Author: session f618d80c · 2026-10-19 · commit `arena/f618d80c-maltaproj4`*
