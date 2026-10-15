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
