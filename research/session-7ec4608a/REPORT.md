# Session 7ec4608a — Hotspawn reverse-engineering, HLTV+esportsbook research, and mobile executive-summary audit

**Branch:** `arena/7ec4608a-maltaproj4` from `40e1fab` (main 2026-10-21T21:27Z, 75 rows / 13 open)
**Date:** 2026-10-22 01:10 UTC
**Goal:** The user's request — *picks for every match* (not only the featured ones), with a research ladder of **HLTV then esportsbooks** for any row the exchange/bookmaker tiers cannot price; a dedicated **unresolved & limitations** section surfaced in the executive summary; a **reverse-engineered Hotspawn lobby** that republishes a full, updated CS2 pick board every 4–8 hours; and a site that is **obviously findable and readable on a phone**.

## 1. Hotspawn reverse-engineering audit (verified live + from code)

Hotspawn publishes its CS2 fixtures in three places that the collector compares **by fixture ID + primary fields**, not just card count. All three were verified as the sources actually queried by `scripts/refresh.py` and `scripts/inventory.py`:

| Source | URL discovered in Hotspawn's public JavaScript | Evidence |
|---|---|---|
| **1. Requested lobby** | `https://play.hotspawn.com/lobby` | Rendered HTML (hydration `ng-state` script) — checked via `Sources.get('lobby', bustable=True)` with CDN cache-bust |
| **2. CS2 pickems page** | `https://play.hotspawn.com/cs2-pickems` | Same hydration scheme |
| **3. Scheduled CS2 API** | `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1` | Exact tenant-1 scheduled-CS2 query found in `play.hotspawn.com` JS (`api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`) |

**How the inventory is verified:**
- `scripts/inventory.py::discover` fetches all three, extracts the fixture array from each page's `ng-state`, normalizes via `scripts.core.normalize_fixtures`, and compares **ID sets** *and* **primary fields** (`teams`, `start`, `lock`, `competition`, `tier`, `best_of`, `status`). A mismatch sets `coverage: partial` and is flagged; `coverage: verified` requires all three to agree.
- The fixture `id` is the Hotspawn primary key; `source_url` per row points to the Hotspawn match page (or the lobby fallback); `feed_url` is the tenant API.
- Past-start scheduled records are **retained** but marked `state: not_open` with flag *“Scheduled feed entry is past its start; current match status is unverified.”* They are not claimed as upcoming or as completed results.
- Wrong-game / unexpected empty / malformed discovery never erases the last good inventory (`inventory['retained']` path).

**Refresh cadence vs the 4–8 hour promise:**
- **Scheduled refresh:** `pages.yml` cron `4,19,34,49 * * * *` — four attempts per hour (~every 15 min, offset off :00).
- **Watchdog:** `refresh-watchdog.yml` cron `*/10 * * * *` — every 10 minutes it reads `https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json`; if `snapshot_generated_at` is >90 min old it dispatches `pages.yml` with 45-min cooldown, 10/day budget.
- **Legacy fallback guard:** `scripts/publish_root_fallback.py` with 4-hour cooldown ensures the committed root fallback never lags more than one slot behind the artifact.
- All three are documented in `sources.html` and the executive summary's freshness line; GitHub may delay/drop runs, so every probability carries its own `observed_at`/`expires_at` (8-hour evidence window) and the strip turns red when stale.

## 2. Full coverage check at this snapshot (21 Oct 21:24Z)

`data/latest.json` `generated_at: 2026-10-21T21:27:36Z`, `fixtures_observed_at: 2026-10-21T21:24:01Z`, `coverage: verified`, 75 rows.

| Metric | Count | Evidence |
|---|---|---|
| Total feed entries | 75 | `data/latest.json` `matches.length` |
| Open (sourced lock & start in future, no end_time, no flags) | 13 | `state: open` |
| With win probability | 11 | `probabilities != null` |
| With pick (including research-only) | 13 | `pick != null` (13/13 open) |
| Research-only (pick, no percentage) | 2 | `method: research_vrs_single` (1081597) and `research_rank_single` (1082860) |
| Without any pick | 0 | — |

Every open fixture therefore has a **sourced pick**; two publish **no percentage** because no market or two-team model line cleared the gates. They are not treated as 50/50.

Open fixture table (verified from `data/latest.json`):

| ID | Teams | Start | Competition | Pick | Method | Probability |
|---|---|---|---|---|---|---|
| 1082837 | Zetta vs LOS NINOS | 2026-10-21T22:00Z | CCT South America #7 | LOS NINOS | exchange | 15.5% / 84.5% (Polymarket) |
| 1081870 | Vitalem Aerem vs Rare Atom | 2026-10-22T05:00Z | ESL Challenger Atlanta closed | Rare Atom | exchange_wide | 39.0% / 61.0% (wide, spread published) |
| 1081597 | benched gods vs TitanFlow | 2026-10-22T11:00Z | CCT Europe Challengers #8 | benched gods | research_vrs_single | — (research only) |
| 1081600 | Donstu vs Banda chuya | 2026-10-22T13:45Z | Moscow Cyber Games | Banda chuya | model_vrs | 42.4% / 57.6% (VRS) |
| 1082688 | Imperial vs Turma do Pagode | 2026-10-22T14:00Z | CCT South America #7 | Imperial | exchange | 77.0% / 23.0% |
| 1082689 | BESTIA vs ShindeN | 2026-10-22T14:00Z | CCT South America #7 | ShindeN | exchange | 46.5% / 53.5% |
| 1082882 | UNiTY vs Apogee Betclic | 2026-10-22T14:00Z | CCT South America #7 | Apogee Betclic | exchange | 43.5% / 56.5% |
| 1082858 | Ground Zero vs Off Chops | 2026-10-26T03:00Z | DFRAG Invitational | Off Chops | model_vrs | 39.8% / 60.2% (VRS) |
| 1082859 | NEXVOID vs Alter Ego | 2026-10-26T03:00Z | DFRAG Invitational | NEXVOID | model_vrs | 68.2% / 31.8% |
| 1082860 | FlyQuest vs Staqued | 2026-10-27T03:00Z | DFRAG Invitational | FlyQuest | research_rank_single | — (research only) |
| 1082861 | Rooster vs Abyssal | 2026-10-27T03:00Z | DFRAG Invitational | Abyssal | model_vrs | 48.2% / 51.8% |
| 1082792 | HOTU vs The Huns | 2026-10-31T09:00Z | Moscow Cyber Games | HOTU | model_vrs | 85.2% / 14.8% |
| 1082793 | 5star vs 1WIN | 2026-10-31T13:00Z | Moscow Cyber Games | 1WIN | model_vrs | 24.3% / 75.7% |

Picks for every match are therefore **present**; the next section documents why two have no percentage and what was tried to resolve them.

## 3. HLTV-then-esportsbook research for the two no-percentage rows

Both rows were re-checked against every tier the collector documents. The attempts below are taken verbatim from `data/latest.json` `attempts` plus additional manual reads on 2026-10-22 via `web_search`/`fetch_page` (runner-independent, documented with URLs).

### 3.1 1081597 — benched gods vs TitanFlow (CCT Europe 2026 Challengers #8, 2026-10-22T11:00Z, lock 10:54Z)

| Source | Result | Detail | Link |
|---|---|---|---|
| **Polymarket (strict + wide)** | No exact pair+UTC-start | Retrieved registry + paginated active events; no `benched gods`/`TitanFlow` at 11:00Z | https://gamma-api.polymarket.com/sports |
| **HLTV fixture page** | No usable line | `HLTV betting table does not expose a numeric two-way line` — rankings/context only | https://www.hltv.org/matches/2399696/match (TBA slot, postponed) |
| **HLTV team pages** | Resolved (identity only) | Exact-label search → unique page per team; benched gods roster Wign/K014NZ/facer/norescue/yoyoS2 matches Valve #157 (811 pts) 5/5; TitanFlow absent from Valve standings | https://www.hltv.org/team/13599/benched-gods + https://www.hltv.org/team/14021/titanflow |
| **Pinnacle** | No match | No pending parent match at that start | https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight |
| **Thunderpick** | No validated quote | Access succeeded but no automated two-way quote extracted (JS rendering / missing adapter) | https://thunderpick.io/esports/cs2-betting |
| **GG.BET** | Access refused | HTTP 403 after 3 waits (10s/30s/60s) | https://gg.bet/en/esports/counter-strike |
| **EGamersWorld** | Placeholder rejected | Both sides 1.8/1.8 — identical default pair refused by policy | https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn |
| **bo3.gg** | No odds | Event page shows no two-way line for this fixture while pricing control fixtures | https://bo3.gg/matches |
| **Valve VRS model (2-team)** | No line | TitanFlow not listed in 2026-10-05 global standings (380 teams) | https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md |
| **Research HLTV rank** | Unusable | Neither team carries world-ranking number in fixture | https://www.hltv.org/ranking/teams |
| **Research VRS single** | **Pick: benched gods** (no percentage) | Exactly one team resolves in Valve standings (benched gods #157, 811 pts, roster-verified) while TitanFlow absent — one-sided standings pick | Same Valve file |

**Published verdict:** `research_vrs_single` pick `benched gods`, no probability. Every rejection is kept in `evidence.html#match-1081597` and `unresolved.html`.

### 3.2 1082860 — FlyQuest vs Staqued (DFRAG Invitational 2026, 2026-10-27T03:00Z, lock 02:54Z)

| Source | Result | Detail | Link |
|---|---|---|---|
| **Polymarket** | No match | No active event at that UTC start | https://gamma-api.polymarket.com/sports |
| **HLTV** | Identity confirmed, no line | HLTV fixture page exists; one team world-ranked (#61 FlyQuest), other absent — research rank single | https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026 |
| **Pinnacle** | No match | No DFRAG Invitational market yet | https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight |
| **Thunderpick / GG.BET** | No validated quote / 403 | Same as above | — |
| **EGamersWorld** | Placeholder rejected | Both sides 1.8/1.8 | https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3 |
| **bo3.gg** | No odds | DFRAG event page lists fixture with no line | https://bo3.gg/ |
| **Valve VRS** | No line | Staqued not listed in 2026-10-05 global standings nor 2026-10-21 Asia regional | Same Valve file |
| **Research rank single** | **Pick: FlyQuest** (no percentage) | FlyQuest HLTV world #61, Staqued absent in same fixture — one-sided ranking pick | https://www.hltv.org/team/12774/flyquest |

**Published verdict:** `research_rank_single` pick `FlyQuest`, no probability. Same evidence linkage.

### 3.3 Research chain for non-featured matches

The same ladder applies to **every** open fixture, not only the two above: strict exchange → HLTV → Pinnacle → wide exchange → EGamersWorld re-observed receipt → VRS 2-team model → HLTV rank tiers → VRS one-sided tier. A later refresh that finds a new two-way book listing (via `data/book-receipts.json`) automatically outranks the model line for that row. All limitations are surfaced in `index.html#unresolved-summary` and `unresolved.html` with the provider, attempt status, reason, and endpoint link — never as 50/50.

## 4. Executive-summary mobility & discoverability audit

**Requirement:** *Executive summary provides links within our site to where updated picks can be found; visitor on phone can find picks easily; readable and accessible.*

**Current executive summary (`index.html`) — verified by reading the built file and its CSS/JS:**

| Element | Location | Mobile treatment | Verified |
|---|---|---|---|
| **Freshness strip** | Immediately below `head`, first visible panel | Sticky-style border, red when stale, shows `observed_at`, `open/priced/research/unresolved` counts, links to `picks.html`, `#picks-at-a-glance`, `unresolved.html` | Yes — `scripts/build.py:fresh_strip`, `assets/style.css:.fresh-strip` with `@media(max-width:650px)` stacking |
| **Hero + next pick** | Below strip | Grid collapses to single column on ≤850px; action buttons wrap | Yes |
| **Start here · tap a card** | `id=start-here` | 4 cards in responsive grid; `start-note` explains bottom bar | Yes — `.start-grid` responsive |
| **Picks at a glance** | `id=picks-at-a-glance` | Desktop: 3-col grid rows; Mobile: `@media(max-width:650px)` → 1-col stacked + hidden `glance-card-mobile` cards (tappable, 52px+ tall, probability bar) | Yes |
| **Section nav + jump bar** | Below glance | `section-nav` + `.jump-nav` flex-wrap with 40px+ tap targets on mobile (`flex:1 1 44%`) | Yes |
| **Coverage line + stats** | `id=coverage` | Stats grid 3→1 column on mobile | Yes |
| **Phone tips panel** | `id=phone-tips` | Explicit “Two taps to the picks” guidance | Yes |
| **Today’s picks / Later** | `id=today`, `id=later` | Tables with mobile `overflow:visible` + card fallback | Yes |
| **Unresolved & limitations** | `id=unresolved-summary` | `gap-grid` 2-col →1-col on mobile; `gap-card` with limitation checklist; `lim-now` banner naming unresolved fixtures by name/date/link | Yes |
| **Bottom persistent nav** | Every page, `nav.mobile-tabs` | `display:none` desktop, `display:flex` fixed bottom on ≤650px; 5 tabs (Home/Picks/Unresolved/Matches/TWC) ≥60px tall, icon + label, `aria-current` | Yes |
| **Search/filter (picks/matches)** | `picks.html`/`matches.html` | `flex:wrap`, 44px inputs, `min-width:200px` search | Yes |

**Accessibility:** Skip link, `aria-label` on nav/sections, `aria-hidden` on bars, `role=group` on probabilities, `aria-label` on percentages, 44px minimum tap targets (WCAG 2.5.5), color contrast on dark hero, `focus-visible` rings.

**No horizontal scroll:** `shell` has `min-width:0`, `tbody tr` at ≤650px uses `minmax(0,1fr)` grid, `teams` wraps, `overflow-wrap:anywhere` on panels/gaps/long tokens.

## 5. Line-by-line verification (official sources only)

See `VERIFICATION.md` in this directory for the per-row source-link audit (all 75 rows, 13 open). Every displayed value traces to an official Hotspawn, Polymarket, Pinnacle, Valve, or HLTV endpoint; where no official numeric line exists the percentage is blank and the reason is flagged. Calculations are reproduced from stored raw fields via `scripts/core.py::devig`/`quote_*` and verified by `scripts/validate.py` (11 probability reproductions at last build) and `verification-c6/audit_snapshot.py`.

## 6. Publication & Pages setup

- `pages.yml` builds on every `main` push and 4×/hour schedule; `actions/cache` retains `runtime/latest.json`; `scripts/validate` + `verification-c6` + `npm run test:browser` gate before deploy.
- `refresh-watchdog.yml` dispatches a fresh build when the live `build-info.json` is >90 min old.
- Legacy `main:/` fallback is re-staged only inside the 8-hour window and after 4-hour cooldown via `scripts/publish_root_fallback.py` — verified by `scripts.validate --data data/latest.json --site .` before commit.
- Live Pages config is `build_type: legacy, source: main:/` (verified via `GET /repos/{owner}/{repo}/pages`); artifact + legacy race is measured in `research/harvest-93fafca6` and handled by the cooldown.

## 7. Irregularities flagged (not blocking)

Flagged items are published on `review.html` per `data/review-notes.json`; latest additions in this session: `7ec4608a-benched-gods-titanflow-esportsbook-2026-10-22` and `7ec4608a-flyquest-staqued-esportsbook-2026-10-22` (no new probability, documented placeholder/absence limitations, source links for EGamersWorld/bo3.gg/Valve/HLTV).
