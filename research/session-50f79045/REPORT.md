# Session 50f79045 report — 2026-10-21

## Scope
- Audit the live Hotspawn CS2 board and existing pick coverage.
- Verify mobile executive summary, in-site links, and the unresolved-picks section.
- Research any fixture left without a supported pick.

## Live state at audit (20:16 UTC, Pages build 8f382b7)
- 76 feed rows captured, **13 open matches**.
- **9 with a published win probability** (4 market, 5 VRS model).
- **3 research-only picks with no percentage** (Zetta–LOS NINOS, Ground Zero–Off Chops, FlyQuest–Staqued).
- **1 unresolved**: fixture 1081597 benched gods vs TitanFlow (CCT Europe 2026 Challengers #8, 22 Oct 11:00 UTC).

## Research for the unresolved fixture
- HLTV Valve global ranking dated 21 Oct 2026 lists **benched gods #160 (791 points, roster Wign/K014NZ/facer/norescue/yoyoS2)** and **TitanFlow #234 (664 points, roster Henma/Saiman Strit/keeisen)**.
- HLTV CCT Europe 2026 Challengers #8 event page lists benched gods with VRS #175 and TitanFlow in the same 16-team playoff bracket.
- EGamersWorld match page (https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn) shows the symmetric **1.8/1.8 placeholder odds pair**, which the existing gates reject as a placeholder (identical odds, no bookmaker named); no named-operator panel was found on that page.
- Polymarket/Pinnacle had no validated exact-pair line at observation; Hotspawn crowd picks (92% / 8%) are never used as a probability.
- Head-to-head on HLTV's Quintessence match page notes benched gods 2-0 and 2-1 wins over TitanFlow five weeks prior, corroborating the ranking signal.

### Result
The fixture resolves as a **research_rank_single** pick for **benched gods** with no published percentage, consistent with the existing one-sided-ranking policy. No probability is fabricated. The scheduled refresh will upgrade this to a market line or two-team VRS line if either becomes available. Flagged for manual review on Flagged for Review (note id `50f79045-benched-gods-titanflow-hltv-rank`) with all four source links.

## Mobile / executive summary
Verified live (fetch_page, cache-busted):
- The executive summary hero shows the coverage line, a "Last checked" timestamp, and three start-here cards (Updated picks, Unresolved & limitations, TWC final results, All matches).
- The Picks at a glance list renders all 13 open matches as numbered entries with the bold pick, percentage/method label and start time — readable as stacked cards on a phone (no horizontal scroll needed; each mobile row is a grid card per the existing @media(max-width:650px) rules).
- The bottom nav bar exposes Home · Picks · Unresolved · Matches · TWC for one-tap navigation on phones.
- The Unresolved picks & limitations section inside the executive summary (index.html#unresolved-summary) links directly to `unresolved.html` and lists each research-only / unresolved row with its source and the source-level access limitations (Polymarket, Pinnacle, HLTV, Thunderpick, GG.BET, Valve VRS).

## Tests / validation
- 494 Python unit tests pass.
- `scripts.build --data data/latest.json` succeeds on the committed bootstrap.
- `scripts.validate --data data/latest.json --site .` verifies 98 rows, 29 calculations reproduced, 15 pages, 836 internal links/assets, 20 artifact checksums, 258 displayed rows — 0 broken links.
- The live Pages site is served fresh by the hourly cron (build-info.json 20:16 UTC is inside the 8-hour evidence window), so the legacy committed bootstrap is only the CDN fallback.

## Irregularities (non-blocking)
- The scheduled-runner HLTV fetch occasionally rate-limits (HTTP 403) and drops ranking context; the existing backoff (10/30/60s) is in place, but a long enough block can leave a row unresolved until the next run. The 1081597 case this session is exactly that.
- EGamersWorld continues to serve symmetric 1.8/1.8 placeholder pairs on many CCT tier-C matches; these are correctly rejected.
- The vendored Valve standings file (data/vrs/standings_global_2026_10_05.md) is a month old relative to HLTV's 21 Oct live ranking; the refresh pipeline pulls the latest Valve standings from GitHub on each Actions run.
