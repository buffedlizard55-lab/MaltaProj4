# Hotspawn reverse-engineering — how the full list is built every 4-8h

## Goal
Provide picks for **every** CS2 match Hotspawn lists, not just those covered by a single betting site. Hotspawn establishes inventory; it never supplies win probabilities.

## Three public sources (no credentials, no bypass)

All three are fetched in every refresh by `scripts/inventory.py` and `scripts/refresh.py`.

### 1. Lobby page — `https://play.hotspawn.com/lobby`
- What it is: Next.js public page with `__NEXT_DATA__` JSON containing all scheduled fixtures across games, including CS2, with fields `id`, `teams`, `competition`, `start`, `lock`, `tier`, `best_of`.
- How we found it: Inspect page source → script `/_next/static/chunks/pages/lobby-*.js` builds its request. Confirmed by browser view-source.
- What we keep: `sha256` of raw response, `retrieved_at`, `observed_at`, `cache_age_seconds`. Example in `data/latest.json` fixtures[0].fixture_sources[2]: url `https://play.hotspawn.com/lobby`, sha `71a5ad...`, retrieved 2026-10-17T20:16:58.210668Z.
- Verification: Matches lobby card count but we compare IDs + primary fields, not just count.

### 2. CS2 pickems page — `https://play.hotspawn.com/cs2-pickems`
- What it is: Filtered CS2-only view of the same data, confirms sport separation.
- How we found it: Linked from lobby, same `__NEXT_DATA__` structure but `sport_alias=cs2`.
- Example: fixture_sources[1] sha `335b470...`, retrieved 20:16:57.400094Z.
- Verification: Union of lobby + this page must agree on CS2 IDs; if they disagree, coverage flagged unverified, not silently merged.

### 3. Tenant API — `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`
- What it is: Direct JSON API the pages call. Returns array of fixtures with machine fields: `scheduled_start_time` (epoch ms), `lock_time` (epoch ms), `lock_offset_sec`, `participants0/1` (ids, names), `competition_id`, `tier`, `best_of`, `offered_points`, `points_breakdown` (game/tier/series/stage/tournament multipliers), `status` (scheduled), `source_status`, `team_ids`, `feed_url`.
- How we found it: Network tab in browser devtools while loading lobby → XHR to this exact URL with `tenantId=1`. Confirmed in page JS `phpstack-1372681-6459848.cloudwaysapps.com`.
- Example: fixture_sources[0] sha `0cd97ae...`, retrieved 20:16:56.155643Z.
- Verification: Same ID must carry same teams/start/lock across all three; `inventory.py` blocks on field conflicts and retains last-good inventory if any source fails or returns unexpected empty/malformed.

## Inventory logic (`scripts/inventory.py`)

```
for each source:
  fetch, hash, store
  parse fixture list (id, teams, team_ids, competition, tier, best_of, start, lock, source_status, source_url, feed_url)
  count

union = union of all source IDs
if any source field conflicts:
  flag as unverified, retain last-good
if any source empty/unavailable:
  cannot erase last-good, freshness timestamps not renewed
if previously-open rows survive partial discovery:
  keep with unverified membership, no new pick
```

## Collection logic (`scripts/refresh.py` + `scripts/core.py`, `hltv.py`, `vrs.py`)

For each open fixture:
1. Try strict Polymarket gate: exact team-pair (case/punct insensitive + alias register `data/identities.json`), exact UTC start, moneyline, fresh (<8h), open acceptingOrders, finite prices, 2-sided, ≥$100 liq, spread ≤25pp, known best_of matches. Receipts in `data/latest.json` attempts.
2. If no, try HLTV identity research (fixture exact pair + UTC), then Pinnacle sharp bookmaker line (before wide tier), then researched book-listing line (hand-captured where automation blocked), then Thunderpick/GG.BET access checks (not bypassed).
3. If no market, try originated VRS model (`scripts/vrs.py`): Valve's official standings points → Valve's fit.js formula (Glicko RD75) + calibration 0.7986, lineup-confirmed (≥3 players if label not unique). Vendored copy `data/vrs/` if live fetch fails; stale standings refused.
4. If no model, try research_rank tiers: both teams ranked → higher rank pick; one team ranked → that team pick. Both teams' evidence stored (fixture label, HLTV label, rank, ranking link, alias source) so pick is re-derivable, no percentage.
5. If none, row stays blank and unresolved, with every attempt's reason published.

## Refresh schedule (every 4-8h requirement)

- **Proposed requirement:** every 4-8h.
- **Implemented:** `pages.yml` cron `4,19,34,49 * * * *` = 4x/hour (every 15 min), offset from :00 stampede. Plus watchdog `refresh-watchdog.yml` every 10 min, dispatches verified pipeline when snapshot >90 min old (cooldown + budget). See `research/refresh-ab18fe2a/DIAGNOSIS.md` for missed/delayed run history that motivated dense schedule.
- **Expiry:** Prices expire at earliest of fixture TTL, quote observation/update TTL, Hotspawn lock, start, bookmaker cutoff (max 8h). Build + browser time checks apply. With JS off, observation/expiry times still visible, automatic current-time check disabled notice shown.

## Verification

- `tests/test_inventory.py` checks conflict blocking, empty not erasing, stale retention.
- `verification-95b588c2/test_integrity.py` and `audits/` replay every row's evidence.
- `research/current/ROW-AUDIT.md` and `research/current/snapshot-audit.json` independent capture comparison.
- Live deployment verification `scripts/verify_live.py` checks exact SHA256 manifest match, not just HTTP 200.

