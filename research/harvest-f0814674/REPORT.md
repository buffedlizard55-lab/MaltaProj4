# Session f0814674 — why the board showed no picks, and the coverage pass that fixed it

**Date:** 2026-10-23 (UTC)
**Branch:** `arena/f0814674-maltaproj4`
**Delivery:** [PR #196](https://github.com/buffedlizard55-lab/MaltaProj4/pull/196) merged as `a030476` at 2026-10-23T05:11:43Z
**Deployment:** run [39904410713](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39904410713) — `verify-build` success, `deploy` success, including the step **"Verify live Pages bytes match this exact build"**.

## 1. The symptom the user reported

The public page at `https://buffedlizard55-lab.github.io/MaltaProj4/` rendered:

> 20 open CS2 match(es) · **0 with a pick** · 0 with a win probability · 20 unresolved
> *Snapshot expired or timestamp unverified: all current picks are withheld*

and the header sentence next to it still claimed *"Every one of the 23 open matches has a pick"*. Two different numbers, both on screen at once, neither current.

## 2. Root cause, line by line

1. `data/latest.json` was generated at **2026-10-22T20:15:52Z** and never replaced.
2. The scheduled publication workflow (`.github/workflows/pages.yml`) runs `Unit and independent failure-mode tests` **before** `Refresh official sources`, `Build and verify` and `deploy`.
3. That unit step failed on the scheduled runs at **2026-10-22T23:26:37Z** (run `39871808909`) and **2026-10-23T01:49:32Z** (run `39886171791`). Every later step was skipped, so nothing could refresh the snapshot.
4. The two failing assertions pinned the *tier label* one historical snapshot recorded for research-only rows:
   - `tests/test_session_75ebd2d6.py`: `assertEqual(m["method"], exp["method"])` expected `research_rank_single` for fixture `1081149`;
   - `tests/test_session_13e99ca6.py`: `assertTrue(str(m['method']).startswith('research_rank'))` while its own loop already accepted `research_vrs_single`.
5. Fixture `1081149` (FORZE Reload vs LFO 10) legitimately moved `research_rank_single` → `research_vrs_single` when Valve's official standings resolved FORZE Reload. A *better* data refresh turned the gate red, and because the gate runs first, publication stopped permanently while the evidence aged out.

The failure reproduces on the exact `7b9180d` tree in a local virtualenv and disappears with this session's patch. It is a test defect, not a data or source defect: the board, prices and sources were correct.

## 3. What changed

| File | Change |
| --- | --- |
| `tests/test_session_75ebd2d6.py` | accepts any `research_*` tier; still requires a pick from the fixture's own teams, no probability, no fair odds and the explicit "No verified market line. Research pick only:" limitation |
| `tests/test_session_13e99ca6.py` | same invariant, with the historical reason recorded inline |
| `tests/test_session_f0814674.py` (new) | 13 tests: a meta-guard that fails if any test pins a research tier again, the full-coverage contract (pick from own teams, two probabilities summing to 1, pick = higher side, research rows never priced), and the executive-summary discoverability/phone contract. A row without a pick must carry a written reason instead of blocking publication |
| `scripts/report_gaps_f0814674.py` (new) | read-only coverage report: open rows by `state == 'open'`, pick, method, the pick's own share (probabilities are stored in fixture order, as a two-value list), source URL; writes `coverage-report.json` + `COVERAGE.md` |
| `scripts/build.py`, `site/assets/app.js` | the executive-summary completeness sentence is now `[data-completeness]` and is regenerated in the browser from the same runtime counts as the `[data-count]` numbers, including the 8-hour stale state, so prose and numbers cannot disagree |
| `.github/workflows/harvest-f0814674.yml` (new) | non-publishing capture on the Arena branch: refresh → quarantine → coverage report → unpriced-row probe (10-minute ceiling) → independent audit → build/validate → commit dated evidence |

## 4. Fresh official-source capture (run 39902922561)

Fixture evidence observed **2026-10-23T04:55:44Z**, snapshot **2026-10-23T04:59:16Z**. Refresh summary:

```json
{"coverage": "verified", "matches": 92, "priced": 29, "research_only": 1, "unresolved_without_any_pick": 0}
```

- **92 Hotspawn CS2 fixtures**, of which **30 open**.
- **30 of 30 open matches carry a pick** (`0` without a pick).
- **29 of 30 carry a reproduced win probability**: 17 `exchange`, 2 `exchange_wide`, 9 `model_vrs`, 1 `model_vrs_mirror`, plus 1 research-only row with a blank percentage.
- Independent row audit (`verification-c6/audit_snapshot.py`): **92 rows, 0 arithmetic or field failures**.
- `scripts.validate`: 92 rows verified against the retained snapshot, 29 calculations reproduced, 839 internal links/assets, 20 checksums, 231 displayed rows.

Rows, methods, percentages and source links: [`COVERAGE.md`](COVERAGE.md) · machine-readable [`coverage-report.json`](coverage-report.json) · raw snapshot [`refresh-snapshot.json`](refresh-snapshot.json) · [`row-audit.md`](row-audit.md).

## 5. The one row without a percentage at 04:59Z — `1082860` FlyQuest vs Staqued (27 Oct 2026, 03:00Z)

> **Follow-up, same morning.** At **05:05:00Z** a later capture (session `071642e7`) found a real listing for this fixture on EGamersWorld `4kaAQWgKEx`: Thunderpick `1.001 / 12.0` at the exact UTC start, corroborated on the same page by Rainbet `1.01 / 11.76`, Underdog `1.01 / 12.01`, CocoBet `1.02 / 11.91`, FanDuel `1.01 / 12.02` and Fanatics `1.02 / 11.97`, and cross-checked against bo3.gg. That line passes the gates and the row is published as `bookmaker_fallback` **92.3% / 7.7%**, so the board on `main` (`2026-10-23T05:22:51Z`) is **30 open · 30 picks · 30 with a win probability · 0 unresolved**. The table below records what *this* 04:59Z probe saw and why it refused to invent a number; the row then closed on its own when a book published a pair.

Researched HLTV first, then the esportsbook and betting-line ladder; every read is dated and archived under [`unresolved-probe/`](unresolved-probe/).

| Step | Source | What it returned |
| --- | --- | --- |
| 1 | HLTV fixture page and betting table | fixture and lineups confirmed; **no numeric two-way line** |
| 2 | Polymarket market `6066520` | spreads **0.88** with ~$126 liquidity — refused by the ≤0.60 spread gate; a wide spread is not evidence of a 50/50 |
| 3 | esportsbook listings (EGamersWorld, bo3.gg, Stavka/Winline, Pinnacle, GG.BET, Thunderpick) | no listing carrying an exact pair + exact UTC start |
| 4 | Valve Regional Standings (official file) | FlyQuest present (HLTV world #61); **Staqued absent**, and no unique 3-of-5 roster match — a one-sided ranking cannot produce a two-team probability |

Verdict at 04:59Z: a research pick (`FlyQuest`) with a blank percentage — inventing a number would have breached the evidence rules, so the row stayed blank with its sources in the executive summary's **Unresolved picks & limitations** section and on `unresolved.html`. It upgraded automatically as soon as a book published a real pair, which is exactly what happened at 05:05Z (see the follow-up above).

## 6. Verification performed

- **974 unit tests OK** (1 skipped) on the merged tree; `audits` 9 OK; `verification-95b588c2` 5 OK; `verification-c6` 12 OK.
- `scripts.validate --data data/latest.json --site .`: 92 rows, 29 calculations, 839 links/assets, 20 checksums.
- Four browser suites: 32 viewport/accessibility scans at 320/390/768/1440 px, expiry scenarios, phone CTA and first-list position at 320/390 px.
- CI on `main`: `Unit and independent failure-mode tests` **success** (it had failed on the two preceding scheduled runs), then refresh, quarantine, build, browser checks, root-fallback commit `547be25`, Pages deploy and the exact live-byte check.
- Live check after deployment: `build-info.json` serves 92 rows built `2026-10-23T05:22:51Z`; the executive summary renders **30 open · 30 with a pick · 29 with a win probability · 0 unresolved** with in-site links to `picks.html`, `unresolved.html`, `matches.html` and `sources.html#method` on the first screen.

## 7. Flagged for review (non-blocking)

1. **Pinned-tier timebomb (fixed here).** Publication was blocked for ~9 hours by data-driven test assertions. The meta-guard in `tests/test_session_f0814674.py` is the regression test; the incident is recorded on the Flagged-for-Review page.
2. **Legacy `main:/` Pages builds errored twice.** GitHub's legacy build for `a030476` and `547be25` returned "Page build failed." (no message) while the next build succeeded and the artifact deploy passed the live-byte check. No content cause found: 65 new files, all regular files, largest 556 KB, no symlinks, 92 MB tree. Treated as a service-side transient, recorded because the legacy source is what serves the root fallback.
3. **`1082860` stays blank** with the limitations in §5. Not a defect; it is the honest outcome of the ladder.
4. **HLTV access is intermittent** from some environments (403s already documented by earlier sessions); the probe records refusals as data, never as a price.
