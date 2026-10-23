# Session 9b97d585 — final full-coverage, source and phone verification

**Dated evidence:** runner [39935049772](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39935049772); snapshot generated `2026-10-23T09:58:40.958746Z`; Hotspawn fixture evidence observed `2026-10-23T09:55:02.253339Z`; snapshot SHA-256 `bd52fa4093dd2cce7d159b8deab51b7db3b705f1a438924feabb3b2cf0ebf649`. This is a dated observation, not a claim that prices remain available after their individual expiries.

## 1. Result

- Three-view inventory parity: **92 API / 92 CS2 page / 92 general lobby / 92 retained**, coverage `verified`, no added/removed fixture IDs and no changed team/start/lock/state facts against the 08:32Z board.
- **30 open matches: 30 picks, 30 two-team probabilities, 30 fully resolved, 0 unresolved.** The other 62 records are not open by sourced timestamps/status and stay blank.
- Methods: **20 strict exchange + 3 labelled wide exchange + 2 dated bookmaker listings + 5 official-file VRS models**.
- Quarantine withheld **0 rows**; the independent C6 replay plus this session’s additional source/coverage checks reported **0 integrity failures**. Build validation reproduced **30 calculations**, checked **817 internal links/assets**, **20 checksums** and **221 displayed match rows**.
- Every fixture and every open pick is listed with its original source links in [row-ledger.md](../harvest-9b97d585/row-ledger.md); raw retained evidence is in [snapshot.json](../harvest-9b97d585/snapshot.json), and the independent replay is [independent-row-audit.md](../harvest-9b97d585/independent-row-audit.md).

Hotspawn is used only for fixture identity, event, start and lock. It is never a probability input. No crowd vote, placeholder pair, inferred value or 50/50 filler is used.

**Integration update:** main run [39935797381](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39935797381) subsequently published a newer verified snapshot (`2026-10-23T10:05:50.376420Z`, fixture evidence `10:02:13.241104Z`) with the same 92/30/30/30 coverage and method mix. That newer board is what this branch publishes; the 09:58Z capture above remains the dated independent harvest. The combined row ledger is [integrated-row-ledger.md](integrated-row-ledger.md), and PR #222's feed-scope explanation and all three of its review notes, plus PR #223's freshness-clock repair and PR #218's HLTV recent-form fallback, are preserved.

## 2. How the lobby is covered and refreshed

The collector cross-checks the scoped fixture API, `play.hotspawn.com/cs2-pickems` hydration, and `play.hotspawn.com/lobby`. The two HTML views receive a measured cache-busting query because prior CDN reads served stale `Age`/`X-Cache: HIT` copies; the API is not cache-busted because it rejects an unknown query argument. Fixture observation time is derived from the actual response/cache receipt, not the later build clock.

The publication ladder is strict exchange → HLTV identity/ranking/lineup research → Pinnacle → labelled wide exchange → researched book listing → originated Valve VRS → HLTV dated Valve view → research-only pick → unresolved with limitations. The scheduled workflow targets :04/:19/:34/:49 each hour plus a watchdog; evidence expires after at most eight hours and earlier at lock/start/book cutoff. Cron delivery is not guaranteed, so the dated scheduler gap below remains flagged.

## 3. Low-tier and wide-line review

### Wide exchange lines (external, but low precision)

| Fixture | Teams | Pick | Team 1 / team 2 | Spread | Liquidity | VRS comparison | Official market |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| 1079198 | Metizport vs BakS | Metizport | 71.0% / 29.0% | 34 points | $872.36 | 73.8% / 26.2% | [Polymarket 6072799](https://gamma-api.polymarket.com/markets/6072799) |
| 1079200 | Color vs ex-Zero Tenacity | ex-Zero Tenacity | 35.0% / 65.0% | 58 points | $684.12 | 68.8% / 31.2% | [Polymarket 6072812](https://gamma-api.polymarket.com/markets/6072812) |
| 1082858 | Ground Zero vs Off Chops | Off Chops | 26.5% / 73.5% | 37 points | $2,525.36 | 39.8% / 60.2% | [Polymarket 6066508](https://gamma-api.polymarket.com/markets/6066508) |

These rows pass only the documented wide tier: the strict 25-point rejection is retained, the spread and low-confidence warning are published, and the 60-point ceiling/liquidity/freshness gates still apply. **1079200 is a specific review case:** the external wide mid favours ex-Zero Tenacity (65.0%) while the VRS comparison favours Color (68.8%); the board keeps the external pick and exposes the disagreement rather than averaging the two.

### Dated bookmaker listings

| Fixture | Teams | Pick | Decimal pair | De-vigged team 1 / team 2 | Observed | Expires | Listing |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1082859 | NEXVOID vs Alter Ego | NEXVOID | 1.61 / 2.14 | 57.1% / 42.9% | 2026-10-23T05:07:00Z | 2026-10-23T13:07:00Z | [EGamersWorld](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/nexvoid-vs-alter-ego-HfdcJeXmT) |
| 1082860 | FlyQuest vs Staqued | FlyQuest | 1.001 / 12.0 | 92.3% / 7.7% | 2026-10-23T05:05:00Z | 2026-10-23T13:05:00Z | [EGamersWorld](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3) |

These are aggregator displays of bookmaker odds, not independently verified operator APIs. They have no operator price-update timestamp, retain their original observation/expiry, and are labelled accordingly. The fresh runner could not renew them because EGamersWorld returned 403; no new price was inferred.

### Originated VRS lines

| Fixture | Teams | Pick | Valve standings (rank / points) | Calibrated team 1 / team 2 | Official input |
| --- | --- | --- | --- | --- | --- |
| 1081605 | Phantom Academy vs Banda chuya | Banda chuya | Phantom Academy #172 / 783; Banda Chuya #165 / 801 | 48.0% / 52.0% | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |
| 1082996 | Acend vs UNiTY | Acend | Acend #63 / 1197; UNiTY #69 / 1167 | 53.3% / 46.7% | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |
| 1082861 | Rooster vs Abyssal | Abyssal | Rooster #205 / 718; Abyssal #195 / 734 | 48.2% / 51.8% | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |
| 1082792 | HOTU vs The Huns | HOTU | HOTU #31 / 1437; The Huns #122 / 944 | 85.2% / 14.8% | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |
| 1082793 | 5star vs 1WIN | 1WIN | 5star #80 / 1110; 1win #38 / 1383 | 24.3% / 75.7% | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |

VRS values are our originated model estimates, not betting prices. They use Valve’s published points, expectation formula and fit calibration; roster identity checks remain on each row.

## 4. Unresolved section and current source limitations

There are **no unresolved open rows in this dated capture**. The executive summary still contains its separate `#unresolved-summary` / `#pick-limitations` section and links to `unresolved.html`, so a future unresolved row is not hidden. No result here asserts that every future match can always be priced.

Current source-access limitations recorded by the refresh:
- **GG.BET fallback access** — HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. ([source](https://gg.bet/en/esports/counter-strike)).
- **Book listing re-observation egw-4kaAQWgKEx-flyquest-staqued** — HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run. ([source](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3)).
- **Book listing re-observation egw-4kaAQWgKEx-nexvoid-alter-ego** — Skipped after earlier access/rate restriction on this host: 403 ([source](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/nexvoid-vs-alter-ego-HfdcJeXmT)).
- **Book listing gap recheck 1081605** — Skipped after earlier access/rate restriction on this host: 403 ([source](https://egamersworld.com/counterstrike/match/rW6Ymkl0D/phantom-academy-vs-banda-chuya-SqCDyX7RB)).
- **Book listing gap recheck 1082861** — Skipped after earlier access/rate restriction on this host: 403 ([source](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/rooster-vs-team-abyssal-P1tTp3RAg8)).
- **Book listing gap recheck 1082996** — Skipped after earlier access/rate restriction on this host: 403 ([source](https://egamersworld.com/counterstrike/match/Nk9F-Ov54e/acend-vs-unity-esports-iwaKSVfgf)).
- **Book listing gap recheck 1082792** — Skipped after earlier access/rate restriction on this host: 403 ([source](https://egamersworld.com/counterstrike/match/EkalRNMvVx/hotu-vs-the-huns-esports-SfdtzDhiK)).
- **Book listing gap recheck 1082793** — Skipped after earlier access/rate restriction on this host: 403 ([source](https://egamersworld.com/counterstrike/match/EkalRNMvVx/1win-vs-5star-esports-4hTvdd1uN)).

The 62 not-open records are also a feed irregularity: the scheduled feed retains past-start/past-lock entries, sometimes with an end time. They remain visible on All matches and Flagged for Review, never as future recommendations.

A separate dated Actions API check found the most recent scheduled pages run at 07:20:51Z and scheduled watchdog run at 05:31:38Z, despite the more frequent cron targets. A push-triggered publish and this manually dispatched capture did succeed. This delivery gap and the phone defect/fix are published as additive notes on **Flagged for Review**.

## 5. Executive summary and phone measurements

The landing page links directly to `picks.html`, the in-page `#picks-at-a-glance` list, `unresolved.html`, `matches.html`, and the unresolved/limitations section. Native disclosures preserve deep links without forcing a phone user through the full site guide.

Measured before the fix on the 08:32Z board at 320×568: first pick y=835, probabilities y=696; the runtime summary also said “0 of them carry no win probability” while all 30 rows were priced.

After the fix: first pick y=367.7–391.0; probabilities y=441.0–467.3; fixed tab bar starts at y=507. No horizontal overflow; percent signs stay on one line; filters still work after the cards. See [before](picks-320-before.png) / [after](picks-320-after.png) screenshots and [mobile-after.json](mobile-after.json).

Static `scripts.summary` and runtime `assets/app.js` now share count-aware all-priced, research-only and singular grammar. `tests/browser_9b97d585.cjs` replays four counter scenarios and the 320×568 layout; it is registered in `npm run test:browser`.

## 6. Verification and coordination

- Runner 39935049772: committed-board unit/audit/integrity/C6/validator gates → real refresh → quarantine → independent C6 row audit → this session’s row audit → fresh build/validator → complete browser suite, **all successful**.
- Local candidate: full unit/audit/integrity/C6 suites, static root and public validators, and all eight browser suites including the new regression are run again on the exact integrated head before the PR. The integrated candidate passed **1,167 unit tests (3 skipped), 9 audits, 5 integrity tests, 12 C6 tests, independent C6 row replay, this session’s additional audit, both validators, and all 8 browser suites**; machine-readable counts are in `verification.json`.
- Session 0fae12a5’s earlier read-only verification (merged PR #216) is preserved. COORDINATION/README/review-note conflicts were resolved as unions. Generated pages were rebuilt from the newer main snapshot rather than rolling it back; no other session’s research was discarded.
- The additional audit derives accepted methods from `scripts.summary.ORIGINS`, avoiding a false failure when another documented fallback is added. It distinguishes integrity failures from honest coverage gaps and never edits a price or pick.

PR [#224](https://github.com/buffedlizard55-lab/MaltaProj4/pull/224) merged at 2026-10-23T10:42:10Z as `9a12b81ae0c19852e7bd7232fa9833fc8a1ae332`, after exact-head run [39939994292](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39939994292) passed. Post-merge publication run [39940962520](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39940962520) is being tracked; the live-Pages receipt remains pending and is not claimed yet.

**Publication repair:** that post-merge run failed only the feed-scope unit test at 10:55Z. Three 11:00Z matches had correctly passed their 10:54Z lock, so the built panel said 27 open while the test demanded 30. `tests/test_session_51a9c98a.py` now builds its dated fixture at `generated_at`, making the disclosure assertion deterministic without changing production expiry behavior. This session's browser test now selects currently open rows by lock/start and still expects every source-open row after reset. The combined candidate passes **1,196 unit tests**, all independent audits, both validators (813 links/assets) and all eight browser suites. Main PR #231's independent dynamic built-count fix is retained alongside the deterministic fixture clock. A missing closing brace in the later short-phone CSS merge is also repaired in both byte-identical copies. PR #230's BO3.gg/Thunderpick adapter and identity/source fixes are preserved. At the 11:06Z verification clock the three locked matches are closed correctly, leaving **27 active picks / 27 probabilities**; the 30/30 figures above remain tied to their dated captures. The live-Pages receipt remains pending until a repaired main run deploys.
