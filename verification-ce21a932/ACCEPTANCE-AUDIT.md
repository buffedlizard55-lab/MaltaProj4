# Acceptance Audit — ce21a932 (2026-10-21T22:45Z)

## Scope
Independent line-by-line verification of committed snapshot, build, and site against official sources. Verification only; no shared implementation files edited beyond branch-trigger addition.

## Snapshot
- File: `data/latest.json` (SHA-256 `294fb120b8adb9a81c686764a63d4481ddadeef1f27f1533dcd5757e7c0861c0`)
- Generated: 2026-10-18T00:52:19.597023Z, fixtures_observed_at 2026-10-18T00:50:24.161000Z, last_attempt_at 2026-10-18T00:52:19.597023Z
- Rows: 98 total, 34 open, 29 with probabilities (18 market incl. 3 exchange_wide, 11 VRS model), 5 research-only, 0 unresolved (0 without pick)
- Open fixtures sample:
  - 1081519 NEXVOID vs Off Chops — research_rank_single → NEXVOID (no %), HLTV 2399547, NEXVOID #101 vs unranked Off Chops, Valve missing Off Chops
  - 1081129 Privateer vs antidaun — research_rank_single → Privateer, HLTV 2399564, Privateer #102 vs unranked
  - 1082206 Damajuana vs A NATA — research_rank_single → Damajuana, HLTV 2399588, Damajuana #? vs unranked
  - 1081861 Lynn Vision vs Morningstar — research_rank_single → Lynn Vision, HLTV 2399576
  - 1081863 Chinggis Warriors vs WXM — research_rank_single → Chinggis Warriors, HLTV 2399578
  - All other 29 priced: validated via scripts/core strict gates (liquidity ≥$100, spread ≤25, fresh ≤8h, two-sided, de-margined/normalized)
- Coverage verified via `python -c` counting state==open and method grouping; matches executive summary counts (34/29/5/0).

## Evidence Rules Checked
- Hotspawn inventory only, never probability input (3-source parity: lobby, cs2-pickems, fixtures API; SHA-256 logged per source)
- Exchange strict gate: liquidity $100, spread ≤25, ≤8h freshness, bid/ask valid, two-sided; wide tier ≤60 with label; overround via `p = x/(x₁+x₂)` or `q=1/d, p=q₁/(q₁+q₂)` replayed
- Pinnacle sharp line before wide tier; HLTV identity/ranking fallback before book listing; VRS model only after market fails; research tiers only where no line exists
- Every table row has source link to official site (Hotspawn fixture, Gamma API, Pinnacle, HLTV match, Valve standings); unverified stays blank flagged (5 research-only have no percentage, reason documented)
- No hallucinations: each probability recalculated from stored raw evidence in `evidence.html` ledger; validator and independent auditor replayed 29 calculations

## Build & Site Verification
- `python -m scripts.build --data data/latest.json --now 2026-10-18T00:52:19.597023Z --out public` → Built 9 primary +6 legacy, 98 rows, 29/5/0
- `python -m scripts.validate --data data/latest.json --site public` → rows_verified 98, probability_calculations_reproduced 29, pages 15, internal_links 836, checksums 20, displayed_rows 258 — OK
- `python verification-c6/audit_snapshot.py data/latest.json` → 0 failures, 98 rows checked, arithmetic passed
- `audits` 9 tests OK, `tests` 494 tests OK
- Browser suite: 32 viewport accessibility/no-overflow scans at 320/390/768/1440px, 7 expiry scenarios, 4 quote-clock boundaries — Passed
- Root legacy fallback byte-identical to public (index.html identical); build-info.json built_at matches snapshot generated_at (with ms precision variance documented)

## Mobile & Executive Summary Checks
- Freshness strip: Last checked 18 Oct 00:52 UTC, next slot 01:04 UTC, 34 open · 34 with pick · 29 with win probability · 0 unresolved, links to Updated picks, Every pick on this page, Unresolved & limits
- Picks at a glance: every open match in start-time order, bold pick + percentage, tap to evidence, mobile cards `.glance-card-mobile` visible at ≤650px, no horizontal scroll, thumb-sized blocks at 320px verified via browser scan
- Start here cards: Updated picks, Unresolved & limitations, TWC final results, All matches — grid responsive, bottom phone tabs Home/Picks/Unresolved/Matches/TWC
- Unresolved summary: 5 gap cards with per-provider attempts (Polymarket, Pinnacle, HLTV, Thunderpick, GG.BET 403, Valve VRS missing team), access limitations table 6 sources × rows affected, methodology link
- Phone guide: "Two taps to the picks" panel, "On a phone: bottom bar has..." note, filter search/status/event functional without JS fallback

## Schedule & Deployment
- Cron: 4,19,34,49 * * * * (4×/hr) + watchdog 10min via `.github/workflows/refresh_watchdog.yml`; publish_gate enforces freshness, stale retained with warning
- Legacy Pages source: branch `main` path `/`; public artifact uploaded via `upload-pages-artifact`, verified via `scripts/verify_live.py` byte poll
- Pending: add `arena/ce21a932-maltaproj4` to pages.yml push list for this branch's verification deploy

## Irregularities Flagged
- Non-blocking: Committed fallback is stale (18 Oct) vs live artifact would be fresh; stale snapshot correctly expires via JS and shows warning — disclosed in review.html and freshness strip
- GG.BET HTTP 403, Thunderpick no validated adapter — recorded not bypassed; HLTV no numeric line — historical DOM evidence at research/harvest-621776e4/hltv-betting-dom.json
- VRS model missing 5 teams (Off Chops, antidaun, A NATA, Morningstar, WXM) — documented per-row, falls to research_rank_single tier

## Files
- This audit, plus runtime copies of audit_snapshot output and validate JSON, stored in `verification-ce21a932/`
