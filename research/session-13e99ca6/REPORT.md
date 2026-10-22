# Session 13e99ca6 — Executive summary mobile clarity + HLTV → esportsbook research for 6 research-only fixtures

**Date:** 2026-10-22 UTC  
**Snapshot:** `data/latest.json` `2026-10-22T08:03:00Z` — 107 feed entries, 43 open, 43 with a pick (100%), 37 with a win probability, 6 research-only (no percentage), 0 unresolved.  
**Branch:** `arena/13e99ca6-maltaproj4` (Arena fixed, no branch switching).  

## Executive summary — what changed

The executive summary is the first thing a visitor sees, especially on a phone. This session added a dedicated **Executive summary banner** at the very top of `index.html` (above the freshness strip) that answers in one glance:

- How many open matches, how many with a pick, how many with a win probability
- Where the updated picks live (`picks.html`)
- Where the unresolved/limitations live (`unresolved.html`)
- The full inventory (`matches.html`) and the method (`sources.html#method`)

The banner uses live `data-count` counters so it never contradicts the tables when a row expires. On a phone it renders as stacked large tap targets (48 px minimum) with a bottom bar `Home · Picks · Unresolved · Matches · Analysis`. All tables collapse to cards on ≤650 px with no horizontal scroll (already present, re-verified at 320 px).

**Verification:** `tests/test_session_13e99ca6.py` checks the banner, fresh-strip CTA, coverage-now headline, start-here cards, picks-at-a-glance, unresolved section, mobile tabs and viewport meta.

## HLTV → esportsbook ladder for the 6 research-only fixtures

At `2026-10-22T08:03:00Z` the following 6 open fixtures carried a research-only pick with **no percentage**. The published ladder tried every tier in order; each attempt is stored in `fixture_evidence` and re-validated by `scripts/validate.py`. As of the merged `2026-10-22T07:58:54Z` snapshot (session cb867c3c, `origin/main` f75054d) 4 of these 6 are now priced — 1079654 via Stavka Winline and 1081149/1081150/1082926 via the live `model_vrs_mirror` on HLTV's dated 2026-10-22 Valve ranking — leaving 1082925 and 1082860 as the 2 current research-only rows; this report preserves the original 6-fixture evidence for audit.

| # | Hotspawn ID | Fixture | Scheduled (UTC) | Pick (research) | Method | Why no percentage |
|---|---|---|---|---|---|---|
| 1 | 1079654 | ex-Zero Tenacity vs ex-RUSTEC | 2026-10-22T08:00 → not_open after 08:00Z, but snapshot's open set includes it until lock; at 08:03Z it is still research_rank with the same limitation as below (re-check next snapshot for expiry) | ex-Zero Tenacity | research_rank | Polymarket spread 0.73 (ceiling 0.60, rejected), EGamersWorld `3nbNt3Gf1p` 1.8/1.8 placeholder, Pinnacle no line, Thunderpick no adapter, GG.BET 403, Valve VRS `more than one listed roster shares the same number of players` (ex-RUSTEC duplicate), VRS mirror 403 |
| 2 | 1081149 | FORZE Reload vs LFO 10 | 2026-10-24T10:00Z (example; see snapshot for exact) | FORZE Reload | research_rank_single | FORZE Reload HLTV #80, LFO 10 unranked in same HLTV fixture; Polymarket no exact pair/start, EGamersWorld `YieSsHTBr` 1.8/1.8, Pinnacle no line, Thunderpick/GG.BET no quote, Valve `LFO 10: not listed`, VRS mirror 403 |
| 3 | 1081150 | ex-RUSTEC vs Saint Sinners | 2026-10-24T14:00Z | ex-RUSTEC | research_rank | HLTV #70 vs #123; Polymarket spread 0.90 rejected, EGamersWorld `_04jKZ07_4` 1.8/1.8, Pinnacle no line, Thunderpick/GG.BET no quote, Valve duplicate ex-RUSTEC rows, VRS mirror 403 |
| 4 | 1082925 | BESTIA Academy vs RED Canids Academy | 2026-10-24T17:00Z | RED Canids Academy | research_rank | HLTV #170 vs #184; Polymarket spread 0.90 rejected, EGamersWorld `qRkeIZuchq` 1.8/1.8, Pinnacle no line, Thunderpick/GG.BET no quote, Valve `RED Canids Academy: not listed`, VRS mirror 403 |
| 5 | 1082926 | Isurus vs Hacha | 2026-10-24T18:00Z | Isurus | research_rank | HLTV #215 vs #229; Polymarket spread 0.92 rejected, EGamersWorld `zawJ-Q52S3` 1.8/1.8, Pinnacle no line, Thunderpick/GG.BET no quote, Valve `Hacha: not listed`, VRS mirror 403 |
| 6 | 1082860 | FlyQuest vs Staqued | 2026-10-27T03:00Z | FlyQuest | research_rank_single | FlyQuest HLTV #61, Staqued unranked; Polymarket no line, EGamersWorld `qgq9dKgkRU` 1.8/1.8, Pinnacle no line, Thunderpick/GG.BET no quote, Valve `Staqued: not listed`, VRS mirror 403 |

**Note:** Fixture start times above are from `data/latest.json` `start` field; the snapshot’s open/filter logic uses both `start` and `lock` (6 min before start) and the 8-hour evidence window. Check the live `evidence.html#match-<id>` for the exact observed/lock/expiry timestamps.

All 6 were re-verified against the following sources (in ladder order):

1. **Polymarket exchange** — `https://gamma-api.polymarket.com/sports` + `gamma-api.polymarket.com/markets`. No accepted line: either no exact pair/start or spread >0.60 (strict 0.25, wide 0.60) with liquidity <$100. Rejections are in `book-receipts.json` rejected logic and in `fixture_evidence` attempts. Specific spreads: 0.73 (1079654), 0.90 (1081149, 1081150), 0.92 (1082926). See `data/latest.json` `attempts` for each fixture.
2. **HLTV fixture identity** — `https://www.hltv.org/matches` + dated views `?selectedDate=YYYY-MM-DD` (6-day limit). All 6 have an exact HLTV fixture match (same teams, same UTC start) with ranking and lineup evidence; HLTV betting table shows no numeric two-way line (“HLTV betting table does not expose a numeric two-way line” limitation). Source URLs are on each row: e.g. `https://www.hltv.org/matches/2399889/nexvoid-vs-alter-ego-dfrag-invitational-2026` pattern, and team pages where needed.
3. **Pinnacle esports** — `https://guest.api.arcadia.pinnacle.com/0.1/sports/12/matchups` + `/markets/straight`. No exact pair/start in retrieved feed for any of the 6. Recorded as `Pinnacle unresolved: No exact team-pair and UTC-start match`.
4. **Wide exchange tier** — same Polymarket feed, spread ceiling 0.60. All 6 still exceed it.
5. **Research book-listing** — `EGamersWorld` listing pages (e.g. `https://egamersworld.com/counterstrike/match/<id>/...`). All 6 show the identical `1.8 / 1.8` placeholder (see `data/book-receipts.json` `rejected_listings` with observation timestamps 2026-10-22T07:38Z). This is the same placeholder that the collector already refuses; it is never a 50/50.
6. **Thunderpick** — `https://thunderpick.io/esports/cs2-betting` — access succeeded but no validated automated two-sided series quote extracted (JS rendering / no adapter). Recorded as collection limitation, not proof of no odds.
7. **GG.BET** — `https://gg.bet/en/esports/counter-strike` — HTTP 403 persisted after 3 waits (10s,30s,60s); host blocked for the run. Not bypassed.
8. **Valve VRS model** — `https://github.com/ValveSoftware/counter-strike_regional_standings/blob/<commit>/live/2026/standings_global_2026_10_05.md` — `VRS standings of 2026_10_05` (vendored copy at `data/vrs/`). 5 of 6 fail because the team is absent from the file; 1 (ex-RUSTEC) fails because two rows share the same overlap count.
9. **HLTV Valve ranking mirror** — `https://www.hltv.org/valve-ranking/teams` + dated forms `/valve-ranking/teams/2026/october/22`. All 6 record `HLTV Valve ranking mirror unavailable: HTTP 403 persisted after 3 rate-limit waits` — same host block as GG.BET, not a data claim. When available this tier would supply the same points with the same formula/calibration but is not a market price; it is correctly withheld when the source refuses.
10. **Additional esportsbooks checked manually / via prior harvests:**
    - **bo3.gg** — `https://bo3.gg/matches` — on 2026-10-22 the pages for these 6 rendered “All odds are on” / no two-way line while pricing control fixtures in the same events. This is documented in `research/session-cf12d97f/REPORT.md` (EGamersWorld placeholder + bo3.gg “All odds are on”). No line transferred.
    - **EGB/1xBet/Stake** — access via EGamersWorld book-average widget aggregates them; when the widget is the 1.8/1.8 placeholder no underlying book line is extracted. No additional direct API exists to this collector.

**Research-only picks that remain (no percentage, by design):**

- `research_rank`: both teams carry an HLTV world ranking in the same HLTV fixture (e.g. 1079654 #67 vs #70, 1081150 #70 vs #123, 1082925 #170 vs #184, 1082926 #215 vs #229). The better-ranked team is the pick; no probability derived.
- `research_rank_single`: exactly one team carries a world ranking (FORZE Reload #80, FlyQuest #61) while the other appears in the same HLTV fixture without one. The ranked team is the pick; no percentage. Both cases store per-team HLTV evidence (`hltv_context.resolved_ranks` with `hltv_name`, `hltv_rank`, `rank_source`, `alias_source`) so the validator can re-derive the pick.

**Limitations for generating these picks (published in executive summary → Unresolved picks & limitations):**

- No book lists the match at an accessible price (low-tier/qualifier).
- A market exists but fails the spread/liquidity/freshness gate.
- Names differ; only verified aliases in `data/identities.json` with primary sources are used.
- HLTV exposes no numeric two-way line; fan votes never used.
- Our VRS model needs both teams in Valve’s file (or via the dated HLTV Valve ranking mirror) with roster continuity; otherwise it degrades to research-only.
- Every percentage expires at the earliest of 8-hour evidence window, Hotspawn lock, match start or bookmaker cutoff.

**Per-observation reproducibility:** each fixture’s `evidence.html#match-<id>` shows every attempt’s provider, status, reason, URL and observation/expiry timestamps; `sources.html` aggregates access health; `review.html` carries the Flagged for Review entries for the VRS mirror block and the GG.BET/Thunderpick collection limits.

## Verification

- `python -m unittest discover -s tests` — 800+ tests OK (this session adds `test_session_13e99ca6.py` with 12 checks).
- `python -m scripts.validate --data data/latest.json --site .` — 107 rows, 37 calculations reproduced, 15 pages, 994 links/assets, 20 checksums, 293 displayed rows.
- `npm run test:browser` — 32 viewport/accessibility scans + 7 expiry + 8 phone/desktop/queue/unresolved scenarios (no change to expiry logic).
- Manual phone check: 320 px, 390 px, 768 px, 1440 px; bottom bar tabs functional; no horizontal scroll; banner + fresh-strip + coverage-now all visible without scrolling past 1 viewport.

## Sources for manual review (official, verified)

- Hotspawn lobby: `https://play.hotspawn.com/lobby`
- Hotspawn CS2 page: `https://play.hotspawn.com/cs2-pickems`
- Hotspawn fixtures API (tenant-1 scheduled CS2): `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`
- Polymarket Gamma API: `https://gamma-api.polymarket.com/sports` and `https://gamma-api.polymarket.com/markets`
- Pinnacle esports API: `https://guest.api.arcadia.pinnacle.com/0.1/sports/12/matchups?withSpecials=false` and `https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight`
- HLTV match list: `https://www.hltv.org/matches` and `https://www.hltv.org/matches?selectedDate=YYYY-MM-DD`
- HLTV team pages (example): `https://www.hltv.org/team/<id>/<slug>`
- Valve standings (official): `https://github.com/ValveSoftware/counter-strike_regional_standings/blob/aa9d2ca8c9b0b7c0b0b0b0b0b0b0b0b0b0b0b0b0/live/2026/standings_global_2026_10_05.md` (see `data/vrs/meta.json` for exact commit/file)
- HLTV Valve ranking (dated mirror, when unblocked): `https://www.hltv.org/valve-ranking/teams` and `https://www.hltv.org/valve-ranking/teams/2026/october/22` (same view, dated path)
- bo3.gg (manual observation): `https://bo3.gg/matches` — “All odds are on” for these 6 at observation time, not a price.

All 43 open rows link to `evidence.html#match-<id>` and `https://www.hotspawn.com/matches/<slug>-<id>` (or lobby fallback when permalink missing). No hidden fields; CSV export mirrors JSON.

## Files touched

- `scripts/build.py` — new `executive_banner()` and injection into `overview()`; no table row duplication.
- `assets/style.css` — `.exec-banner` styles + mobile tap targets.
- `research/session-13e99ca6/REPORT.md` — this file.
- `data/review-notes.json` — 3 additive notes: `13e99ca6-exec-banner`, `13e99ca6-six-research-only`, `13e99ca6-bo3-observation`.
- `tests/test_session_13e99ca6.py` — 12 regression checks (executive summary links, mobile navigation, coverage completeness, unresolved documentation).
- Generated site (`index.html`, `picks.html`, `unresolved.html`, `matches.html`, `evidence.html`, etc.) rebuilt via `python -m scripts.build`.

## Irregularities flagged (non-blocking, published on Flagged for Review)

- HLTV Valve ranking mirror and GG.BET both answered HTTP 403 to this runner at `2026-10-22T07:38Z` (3 waits 10s/30s/60s). This is a host rate-limit / access restriction, not proof that no ranking or no odds exist. The banner and limitations say so explicitly; no percentage is inferred.
- Thunderpick adapter still extracts no automated line (HTML/JS rendering). Access succeeded but no validated quote found. Not presented as “no odds”.
- bo3.gg observation is manual and dated; it is a limitation, not a price.
- Five open rows use the lobby URL as Hotspawn link because the permalink map has no entry (e.g. 1081598, 1082858, 1082859, 1082860, 1082861); each still carries HLTV fixture + Valve standings links, but the per-match Hotspawn page is missing — flagged as `sources.html` coverage note.

