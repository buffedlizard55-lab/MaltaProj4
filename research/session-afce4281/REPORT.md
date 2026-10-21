# Session afce4281 — every-match pick audit (2026-10-21)

## Fresh snapshot audited

Harvest run [39602467812](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39602467812)
(real `scripts.refresh` on a trusted runner; sandbox reaches GitHub/package registries only).
Snapshot: `research/harvest-afce4281/snapshot.json`, generated 2026-10-21T12:51:25Z,
Hotspawn inventory verified across api/page/lobby (81 fixtures).

Open fixtures: **19**. With a pick: **18** (market `exchange`, originated `model_vrs`,
`bookmaker_fallback`, and labelled research-only picks). With **no pick**: **1**.

## The one unresolved fixture — 1082762 ex-CYBERSHOKE vs BlinkDagger

Collector ledger (in the snapshot): Polymarket candidate existed but the alias was
unverified; HLTV exposed no numeric two-way line; Pinnacle had no exact pair/start;
Thunderpick yielded no validated quote; GG.BET returned HTTP 403; Valve VRS model
could not list `ex-CYBERSHOKE` under that label; neither team carried an HLTV world-rank
number, so no ranking tier fired. Hotspawn was used for inventory only, never probability.

### Research, in the requested order

1. **HLTV first** — [match 2399839](https://www.hltv.org/matches/2399839/ex-cybershoke-vs-blinkdagger-winline-mpkbk-cis-lan-season-9):
   same event (WINLINE MPKBK CIS LAN Season 9), same teams, 2026-10-21 15:00 UTC, BO3.
   Team 14106 `ex-CYBERSHOKE` fields bl1x1, Mokuj1n, nota, yiksrezo, shoke; HLTV shows
   **VRS #78** for it and no VRS rank for BlinkDagger. HLTV fan votes (74.6/25.4) were
   **not** used as probability, per project rules.
2. **Esportsbook / exchange lines** — [Polymarket market 5971981](https://gamma-api.polymarket.com/markets/5971981):
   "CYBERSHOKE Esports vs BlinkDagger (BO3) – CIS LAN Championship Group C",
   `gameStartTime 2026-10-21 15:00:00+00`, outcome prices **0.82 / 0.18**,
   best bid/ask 0.81/0.83 (spread 0.02), liquidity **$1,981.53**, updated
   2026-10-21T12:42:59Z (read directly, 2026-10-21). EGW's listing for this fixture
   showed placeholder 1.8/1.8 and was rejected as unusable, consistent with the
   project's placeholder-odds rule; a Russian odds aggregator listing
   (kushvsporte, CYBERSHOKE 1.06 / BlinkDagger 7.28) corroborates the favourite
   direction but was not used as a priced source.
3. **Identity** — [Liquipedia CYBERSHOKE Esports](https://liquipedia.net/counterstrike/CYBERSHOKE_Esports)
   lists this exact fixture and the same roster (Mokuj1n, nota, yiksrezo, bl1x1, shoke)
   and records the organisation as disbanded 2026-10-13 — explaining the `ex-` prefix
   for the continuing roster. Valve's official 2026-10-05 global standings
   (`data/vrs/standings_global_2026_10_05.md`) list CYBERSHOKE twice: #61
   (Alkaren, alpha, Mokuj1n, nota, yiksrezo) and #171 (alpha, bl1x1, fluffy, glowiing,
   Mokuj1n). The HLTV lineup overlaps #61 by 3 and #171 by 2, so Valve's
   roster-continuity rule selects #61 uniquely.

### Fix applied

One bounded identity registered in `data/identities.json`:
`CYBERSHOKE` = {CYBERSHOKE, CYBERSHOKE Esports, ex-CYBERSHOKE}, main team only —
**CYBERSHOKE Prospects is explicitly excluded**. Exact opponent + UTC start are
still required by every gate. No code path, gate, or threshold was loosened.
Consequence on the next refresh: the Polymarket candidate can pass the strict
exchange gates (liquidity ≥ $100, spread ≤ 25 pts) and price the row; if that
quote expires or is withdrawn, `research_vrs_single` can still publish a
pick-only (no percentage) row from the one-sided Valve standings evidence.
Tests: `tests/test_session_afce4281.py`.

### Limitations (also published in the executive summary, #pick-limitations)

- Research-only picks carry **no percentage** — one-sided ranking/standings
  evidence cannot produce a calibrated probability, so the number stays blank.
- Low-tier fixtures may have no bookmaker listing at all, a placeholder listing
  (rejected), a blocked source (e.g. GG.BET 403), or a name the books spell
  differently; each such row stays in Unresolved with its reason until a
  primary source resolves it.
- Evidence expires (≤ 8 h, earlier at lock/start/cutoff); an expired pick is
  withdrawn rather than shown as current.

## Flagged for review

- `ex-` identity depends on roster continuity after the org's recorded
  disbanding (2026-10-13); if the roster changes, the alias basis must be
  re-checked. Published on Flagged for Review via this report.

Verification refresh requested after the identity registration (harvest run follows this commit).

## Verified outcome

Post-fix harvest snapshot (2026-10-21T12:59:49Z, committed by the harvest runner):
**19 open fixtures, 19 with a pick, 17 with a published probability** (2 research-only,
no percentage). Fixture 1082762 resolved via the strict Polymarket exchange gates as
**ex-CYBERSHOKE 82.5%** (market 5971981, observed 2026-10-21T12:52:49Z) — the alias
was the only missing gate. Zero open fixtures without a pick in that snapshot;
counts are a dated observation, not a permanent coverage promise.
