# Line-by-line verification — session fa85eb7a (18 Oct 2026)

All claims checked against primary sources. No hallucinations; unverified stays blank.

## Hotspawn reverse-engineering (requirement: full list every 4-8h)

**Method:** Compare three public views found in Hotspawn's JavaScript:

1. **Lobby page** `https://play.hotspawn.com/lobby` — public HTML with `__NEXT_DATA__` containing fixture IDs and basic fields. Verified: the page loads without login, contains CS2 fixtures.

2. **CS2 pickems page** `https://play.hotspawn.com/cs2-pickems` — filtered CS2 view, same structure, confirms sport separation. Verified: 81 total entries in data/latest.json's fixtures_observed_at (20:16 UTC 17 Oct) match union of these two pages plus API.

3. **Tenant API** `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1` — machine-readable JSON with `scheduled_start_time`, `lock_time`, `participants0/1`, `offered_points`, `tier`, `competition_id`. Verified: data/latest.json's fixture_sources_sha256 = `0cd97ae...` for this URL, with retrieved_at 20:16:56.155643Z. Comparison is by **IDs and primary fields**, not just card count — `scripts/inventory.py` checks `id`, `teams`, `start`, `lock` for conflicts; if sources disagree, union is retained and coverage flagged as unverified.

**Refresh cadence:** `.github/workflows/pages.yml` cron `4,19,34,49 * * * *` = 4x/hour = every 15 min, inside 4-8h promise. Watchdog `.github/workflows/refresh-watchdog.yml` checks every 10 min, dispatches when snapshot >90 min old. Verified: workflow file exists, schedule documented in research/refresh-ab18fe2a/DIAGNOSIS.md, and freshness gate `scripts/publish_gate.py` prevents stale publication (max 8h TTL, per-row `expires_at`).

**Result:** Latest snapshot `data/latest.json` has 81 total, 18 open, generated 20:18 UTC 17 Oct, fixtures_observed 20:16 UTC. Coverage = verified (three-way parity). Next refresh will re-discover new fixtures automatically (inventory.py retains previous-only open rows with unverified membership and no new pick if discovery partially fails).

## TWC Day 1 — 14 Oct 2026 (upset)

**Claim:** 9z beat Aurora 2-0 (Inferno 13-11, Nuke 13-1). **Source:** `https://www.hltv.org/matches/2399384/9z-vs-aurora-thunderpick-world-championship-2026` and report `https://www.hltv.org/news/45718/9z-beat-aurora-2-0-to-kick-off-twc-2026` (luchov 1.61, 97.4 ADR, Aurora 5th in VRS). Verified: event results page `https://www.hltv.org/results?event=8932` lists 9z 2-0 Aurora.

Other Day 1 results (from results page):
- Falcons 2-0 NIP (`https://www.hltv.org/matches/2399385/falcons-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026`, Ancient 16-13 OT, Dust2 13-6 via EsportBet preview `https://esportbet.com/thunderpick-world-championship-2026-group-a-betting-tips-thursday-october-15/` — flagged as betting preview, not HLTV report)
- Legacy 2-0 PARIVISION (`https://www.hltv.org/matches/2399386/legacy-vs-parivision-thunderpick-world-championship-2026`)
- FURIA 2-0 BETBOOM (`https://www.hltv.org/matches/2399387/furia-vs-betboom-thunderpick-world-championship-2026`, report `https://www.hltv.org/news/45723/furia-fend-off-betboom-to-end-day-one-of-twc`)

**Roster change check:** Aurora rebuild 8 July 2026 (kyxsan from Falcons, Jimpphat from MOUZ, coach ash from GamerLegion) per `https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan` and Strafe `https://www.strafe.com/news/read/aurora-locks-in-new-cs2-roster-with-kyxsan-and-jimpphat/` + auroragg.com 20.08.2026 LAN debut. Team page `https://www.hltv.org/team/11861/aurora` confirms 5: XANTARES, woxic, Wicadia, Jimpphat, kyxsan, coach ash, VRS #5 / HLTV #6. **Verdict:** Change is real but 3 months old at TWC, not a fresh onboarding shock — documented in `data/analysis.json` upset_context, not used as probability input.

**Scoring:** Hotspawn rules `https://play.hotspawn.com/how-it-works` — points per correct pick, higher tier more points, streak bonus, lock before start, weekly reset. Feed's `offered_points` gives S=7 / B=3 / C=2 (see `data/latest.json` 1080207 tier S). Streak bonus formula unverified — flagged in review-notes, no number claimed.

## TWC Days 2-4

**Day 2 (15 Oct):** From `data/analysis.json` day_two (re-verified 16 Oct by 0e407ec7):
- Falcons 2-1 9z (Nuke 13-9, Mirage 8-13, Dust2 13-9) — `https://www.hltv.org/matches/2399409/9z-vs-falcons-thunderpick-world-championship-2026`, TeSeS 47-40 1.26
- Aurora 2-0 NIP (Cache 13-9, Dust2 13-7) — `https://www.hltv.org/matches/2399408/aurora-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026`, Wicadia 45-25 1.65
- FURIA 2-1 Legacy (Cache 10-13, Inferno 13-5, Mirage 13-8) — `https://www.hltv.org/matches/2399411/legacy-vs-furia-thunderpick-world-championship-2026`
- BETBOOM 2-1 PARIVISION (Ancient 13-10, Anubis 4-13, Mirage 7-13) — `https://www.hltv.org/matches/2399410/parivision-vs-betboom-thunderpick-world-championship-2026`

**Day 3 (16 Oct):** Re-read 17 Oct:
- Aurora 2-0 9z (Cache 13-11, Inferno 13-4) — `https://www.hltv.org/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026`
- BETBOOM 2-1 Legacy (Nuke 16-13 OT, Dust2 11-13, Mirage 13-11) — `https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026`, news `https://www.hltv.org/news/45739/betboom-qualify-for-twc-playoffs-over-legacy`

**Day 4 (17 Oct):** Fresh read 20:18 UTC 17 Oct (research/session-cc88483d/report):
- FURIA 2-0 Aurora (Dust2 13-8, Inferno 13-10) — `https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026`, veto: Aurora removed Ancient, FURIA removed Anubis, Aurora picked Dust2, FURIA picked Inferno
- BETBOOM 2-1 Falcons (Anubis 5-13, Dust2 16-14, Mirage 13-7) — `https://www.hltv.org/matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026`, second upset (favoured Falcons lost)

**Day 5 (18 Oct):** Confirmed 20:16 UTC 17 Oct:
- Third-place: Aurora vs Falcons 11:30 UTC — `https://www.hltv.org/matches/2399416/aurora-vs-falcons-thunderpick-world-championship-2026`, BO3 (session f4e34907 read)
- Grand final: FURIA vs BETBOOM 15:00 UTC — `https://www.hltv.org/matches/2399417/furia-vs-betboom-thunderpick-world-championship-2026`, BO5 (unique at event)
- Neither was on Hotspawn feed at 20:16 UTC (81 entries, 18 open, none TWC main event). Research prices only: Thunderpick `https://thunderpick.io/esports/cs2-betting/thunderpick-world-championship-2026/11024/aurora-vs-falcons/2843582` (Aurora +170 / Falcons -238, de-vig 34.47/65.53%, exp 04:20 UTC 18 Oct) and `https://thunderpick.io/esports/cs2-betting/thunderpick-world-championship-2026/11024/furia-vs-bb-team/2843592` (FURIA -286 / BETBOOM +190, 68.24/31.76%). Single-book, not consensus, expires before match — documented in analysis.json day_five_guidance. Market cross-check: Pinnacle had no TWC Day-5 matchup at 20:10Z probe (`research/session-cc88483d/probe/pinnacle-esports.json`), Polymarket no head-to-head Day-5 market.

**Contrarian guidance:** Documented in analysis.json strategy rules. No claim of optimal leaderboard strategy without verified crowd pick-share data. Day-5 picks default to market favourite (Falcons, FURIA); Aurora/BETBOOM are high-variance swings only if chasing, not proven EV+.

## Pick coverage (requirement: every match)

**Current open 18:** 7 market (Polymarket strict gate: moneyline, 2 exact teams, exact UTC start, fresh (<8h), open accepting, finite, 2-sided, ≥$100 liq, spread ≤25pp), 6 model (Valve standings `data/vrs/standings_global_2026_10_05.md` through fit.js Glicko RD75 + calibration 0.7986, roster confirmed by HLTV lineups with ≥3 overlap if label not unique), 4 research_rank_single (exact HLTV fixture identity, one team world-ranked, other not, no percentage), 1 unresolved (Hacha–LOS NINOS, no market/ranking/VRS).

**Fallback order verified:** `scripts/core.py` (strict gates), `scripts/hltv.py` (HLTV identity), Pinnacle before wide tier, `data/book-receipts.json` research listing, `scripts/vrs.py` model, then `research_rank`. Each attempt stored in `data/latest.json` attempts array with provider, status, reason, url.

**Unresolved details:**
- 1082019 Hacha–LOS NINOS: Polymarket market 5796276 exists (Hacha Esports vs Los Niños, 22:00Z, Polymarket lists hltv.org resolution) but parent event 1203504 says ended=true at targeted probe (research/session-cc88483d/probe/polymarket-active-cs2.json). Guard not overridden — pick stays blank, reason published. Verified alias Hacha Esports→Hacha via fixture parity (HLTV 2399768, same 22:00Z start, same competition). LOS NINOS not in Valve standings, neither HLTV-ranked in fixture, so no research pick. Flagged on review page.
- 1081519 NEXVOID–Off Chops: NEXVOID HLTV #101, Off Chops unranked — research pick NEXVOID, no probability (no HLTV rank-to-prob formula applied per policy).
- 1081522 antidaun–Phantom Academy: Phantom #178 vs unranked antidaun — research pick Phantom, no VRS (antidaun absent from Valve file).
- 1081861 Lynn Vision–Morningstar: Lynn #39 vs unranked — research Lynn, no VRS (Morningstar absent).
- 1081863 Chinggis Warriors–WXM: Chinggis #61 vs unranked — research Chinggis, no VRS (WXM absent, Chinggis has duplicate Valve entries #87/#220 needing lineup disambiguation).

**All attempts documented:** Each of 5 has 7-8 attempt entries (Polymarket, HLTV, Pinnacle, Thunderpick, GG.BET (403 after 3 waits 10/30/60s, host blocked, not bypassed), VRS, rank). Shown in executive summary gap-grid and unresolved.html with per-source limitation counts.

**No inferring:** No 50/50 defaults, no academy inference, no crowd percentages used (feed's participants0_picked_percent ignored per inventory.py), no HLTV rank formula. Quarantine `scripts/quarantine.py` withholds any row auditor cannot reproduce (test_research_tiers.QuarantineTests).

## Site and mobile

**Executive summary links:** README.md "Find the picks" + index.html hero "View updated picks →", section-nav (Updated picks (13) etc), jump-nav (Today's/Later/Unresolved/Coverage), start-here 5 cards, coverage-line banner, twc-unpriced banner, stats linked to picks/unresolved. All have 44px+ tap targets, tested.

**Mobile:** Sidebar → bottom nav at 650px (flex column → flex row, 61px height, 10px font, 19px icons). Tables → cards at 650px (grid 1fr 1fr, pick on top, no horizontal scroll). Hero 32px→29px→26px responsive. Viewport meta `width=device-width,initial-scale=1,viewport-fit=cover`, safe-area-inset, overflow-wrap anywhere for long hashes, min-height 44px on all interactive elements (axe-core checked). Browser tests `tests/browser.cjs` + `tests/expiry.cjs` run at 320/390/768/1440px, 32 viewport/accessibility scans + 7 expiry boundaries pass (see audits/**).

**No manual input:** `scripts/refresh.py` runs on GitHub Actions (4x/hour + watchdog), restores last snapshot from cache, retains union on partial failure, expires by earliest TTL/lock/start/cutoff (max 8h), fails closed on empty/malformed, no synthetic data. Documented in README.md Automatic operation.

## Irregularities flagged (Flagged for Review page)

- Thunderpick card vs market-page disagreement (+150/-208 vs +170/-238, same minute) — `review.html`
- Hacha parent event ended=true vs active moneyline — `review-notes.json`
- LFO 10 vs Sökerorg alias unverified (Polymarket 5799524 0.6/0.4 not transferred) — `review-notes.json`
- HLTV noOdds historical DOM only, not proof every fixture lacks odds — `research/harvest-621776e4/hltv-betting-dom.json`
- Lock-time wording: rules say 5 min, API lock_offset_sec 360 (6 min) — uses earlier, flagged
- Day-2 HLTV betting analytics no numeric line — not presented as probability
- Streak bonus formula unverified — no number claimed
- No crowd pick-share data — no leaderboard advantage claimed
- HLTV secondary source, organizer confirmation not collected — flagged
- 4 research-only rows have no percentage by design — limitation published
