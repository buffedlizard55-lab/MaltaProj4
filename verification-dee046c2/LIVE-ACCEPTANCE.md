# Live board acceptance record — session dee046c2 (2026-10-21)

Dated, read-only acceptance verification of the published site at the phone-first requirements.
Full investigation detail with raw receipts: `../research/session-dee046c2/REPORT.md`;
cross-session requests: `../research/session-dee046c2/REQUESTS.md`.

## Where the picks are (phone flow)

1. **[Landing page](https://buffedlizard55-lab.github.io/MaltaProj4/)** — first screen is the
   executive summary: freshness strip (snapshot time, next-check slots, open/pick/probability
   counts), then **Picks at a glance** — every open match in start order as tappable cards with
   the pick in bold and the win percentage, `_Research only · no percentage — why ↓_` or
   `_Unresolved — why ↓_` labels where the evidence ends there, then the
   **Unresolved picks & limitations** block (`#unresolved-summary` → `#pick-limitations`), which
   since PR #115 *names* every open fixture without a pick instead of only counting it.
2. Bottom navigation (Home · Picks · Unresolved · Matches · TWC) persists; the
   **[Updated picks](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html)** page is the
   canonical board; **[Unresolved & limits](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html)**
   carries every pick without a market line and its limitation; every row links to its
   **[evidence block](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html)** (source
   URLs, timestamps, hashes) and the whole flag register is on
   **[Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html)**.
3. Layout acceptance is executed on **every** CI run: the Playwright suite scans the pages at
   320/390/768/1440 px with axe WCAG and horizontal-overflow checks plus expiry/research-quote
   scenarios (see any listed run's `verify-build` job).

## Dated observations

| UTC | Read | Result |
| --- | --- | --- |
| 20:11:53Z | live `build-info.json` (served) | rev `47f230b`, built 19:57:45Z, 76 rows — fresh artifact |
| ~20:12Z | live `index.html` (served) | committed root fallback (18 Oct data) with red **"Snapshot expired… Current picks are withheld"** strip — legacy-pages race, safety design held, mobile layout confirmed present (cards, glance list, bottom-nav note, limitations block) |
| 20:18–20:27Z | main runs 39668307571 / 39669384223 | `deploy => success` incl. step "Verify live Pages bytes match this exact build" — site restored to artifact bytes at head `63f4172`/`b2e204a` |
| 20:28:07–20:33:15Z | harvest run 39669752785 (this session's probe) | see REPORT §3: every open row replayed from primary sources; 3/3 exchange rows **delta 0.0**; new Polymarket listing auto-priced 1081870; Pinnacle confirmed no line for the four gap fixtures; VRS replay exact for all unique-label rows |
| 20:44:08–20:49:19Z | harvest run 39672321101 (post-PR-#119 merged code) | `coverage verified · 75 rows · 11 priced · 2 research-only · 0 unresolved without a pick`; quarantine 0 withheld; 75/75 rows audited with 0 failures; exchange/model rows re-replayed (delta 0.0 where the source was reachable; the pre-lock Zetta market moved −5.5 pt after its own observation — dated quote, label unchanged) |
| ~20:52Z | live `index.html` + `build-info.json` | artifact rev `884f36e`, built 20:47:31Z, 75 rows; executive summary: **"13 open · 13 with a pick · 11 with a win probability · 0 unresolved"**; all 13 in Picks-at-a-glance + phone cards; the two research-only rows linked to "why"; `#runtime-stale` wording visible to text extractors only (hidden div; documented artifact of non-JS reads) |

## Cadence vs the 4–8 h requirement (measured, not asserted)

Scheduled + push publications on `main` 12:39Z→20:35Z: worst gap between successful publications
was **4 h 13 m** (15:03→19:16, schedule-merged); the cron itself is `4,19,34,49 * * * *` and the
watchdog ticks every 10 min, i.e. the *target* cadence is ~15 min — four times tighter than the
4–8 h ask — with the eight-hour evidence window as the hard ceiling (expired data is withheld by
words and by banner). Requests R-1/R-2 (see `REQUESTS.md`) tighten delivery further: re-staging
the root fallback from a fresh snapshot, and giving the watchdog triggers that survive scheduler
degradation.

## Status of the four "no market line" fixtures at this session's last two snapshots

| Fixture | 20:28Z (run 39669752785) | 20:44Z, post-#119 (run 39672321101) |
| --- | --- | --- |
| 1082837 Zetta vs LOS NINOS | research pick, no % | **exchange** via the verified Zetta↔Alianza Lima Esports identity: pick **LOS NINOS**, 14/86 at its 20:40Z observation (live replay 20:45Z showed the pre-lock move; alias corroborated at 20:50Z from Valve's own roster row + the market's own event text + a third-site lineup read; HLTV itself was 403 to every automated channel in this window, so the identity note stays published on `review.html` for human sign-off) |
| 1081597 benched gods vs TitanFlow | unresolved, no pick, complete refusal ledger | **research_vrs_single** pick: **benched gods** (Valve #157, 811 pts, 5/5 lineup via the registered HLTV receipt), probabilities deliberately blank; `Match postponed` flag surfaced on the row and `review.html` |
| 1082858 Ground Zero vs Off Chops | research rank pick, no % | **model_vrs 39.83/60.17** pick Off Chops — replayed from Valve's file at commit `eec4853` with **delta 0.0** (this session also requested PR #119's report prose be corrected: it says 40.9/59.1 and 36.3/63.7 for two rows the pipeline publishes as 39.83/60.17 and 24.30/75.70) |
| 1082860 FlyQuest vs Staqued | research rank_single pick, no % | unchanged — **FlyQuest** research pick; Staqued genuinely absent from Valve's global file (verified by grep at the pinned commit 20:5xZ); no percentage invented |
