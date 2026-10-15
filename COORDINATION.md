# Coordination

Session: arena/d1bae160-maltaproj4 (fixed Arena working branch).

| Task | Status | Owner | Scope |
|---|---|---|---|
| Research, collector, dashboard, tests and final integration | in progress | arena/d1bae160-maltaproj4 | Entire previously empty repository |

## Research log
- 2026-10-15: Initial repository contains README only; no other session claims.
- Official inventory: https://play.hotspawn.com/cs2-pickems and https://play.hotspawn.com/lobby . Rendered source exposed 18 upcoming cards, while weekly count was 72 and filter count 80. These counts are not equivalent; full coverage is not yet verified.
- Official fixture pages: https://www.hotspawn.com/counter-strike/tournament/elisa-breakout-series-2 confirms UTC schedule; lobby renderings showed inconsistent time zones. Do not infer UTC from lobby display.
- https://www.hotspawn.com/counter-strike/tournament/urban-riga-open-5 shows completed June fixtures despite the lobby filter listing the tournament in October. Flag stale inventory rather than treating historical results as predictions.
- Sandbox direct outbound access to Hotspawn is restricted. Collection will be tested on GitHub Actions; no bypass of authentication or anti-bot controls.

## Implementation verification
- Added mobile card/table layouts, summary deep links, unresolved and Flagged for Review pages, all source-linked.
- Four exact-identity direct bookmaker pairs accepted in research snapshot: Aurora/NiP, MIBR/BC.Game, Legacy/FURIA and ENCE/BOJONG. Other aliases deliberately rejected pending corroboration.
- All six local tests passed (probability math, invalid prices, snapshot provenance, internal links, crowd-vote exclusion, lobby parsing). JavaScript syntax checked with Node.
- Local browser binary download blocked by sandbox outbound restrictions; browser smoke checks run on GitHub Actions instead.
- Sources: https://thunderpick.io/esports/cs2-betting/thunderpick-world-championship-2026/11024 ; https://thunderpick.io/esports/cs2-betting/pulse-beat-iii/11173 ; https://thunderpick.io/esports/cs2-betting/elisa-breakout-series-2/11360 . Observation time is retrieval, not bookmaker-issued quote timestamp.
- Known limitations: full weekly coverage unverified; automated extraction not yet tested against live DOM; no calibrated historical fallback deployed. All published on Flagged for Review, not silently treated as verified.

## Publication and follow-up
- PR https://github.com/buffedlizard55-lab/MaltaProj4/pull/8 merged successfully, merge commit bbcb63785d6e8dfbd9cbc62d2bfde1ae796dc3d3.
- Pages build/deployment run https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38706162495 succeeded (including browser smoke tests at 375, 768 and 1280 px across five pages).
- Live runner inspection found the public Angular `ng-state` transfer cache contains the full returned fixture payload, including historical June entries; the collector is being updated to extract this rather than only visible cards. Explicit epoch UTC start times resolve display-time ambiguity. Weekly-count reconciliation remains unverified.
- HLTV and Thunderpick runner retrievals blocked by Cloudflare verification. No bypass attempted. Added official Polymarket Gamma API exact-date/team/competition Match Winner parser; example verified directly: https://gamma-api.polymarket.com/events?slug=cs2-ence-bojong-2026-10-15 . Wrong date, closed markets and map markets are rejected by tests.
