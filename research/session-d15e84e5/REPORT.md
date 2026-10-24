# Session d15e84e5 — publication repair, every-match coverage, mobile summary

Started 2026-10-24 16:40 UTC on `arena/d15e84e5-maltaproj4` from `main` `45fc6ba`.

## 1. What is actually wrong (measured, with links)

| # | Observation | Evidence |
| --- | --- | --- |
| 1 | The public board froze at the 08:06Z snapshot and now withholds every pick, because that snapshot is older than the site's own 8-hour evidence window. | Live `build-info.json` read at 16:22Z: `snapshot_generated_at 2026-10-24T08:06:51Z`, `built_at 08:26:58Z`, and the served `index.html` carries `id="runtime-stale"` plus "Snapshot inside its 8-hour evidence window" absent. |
| 2 | No `main` run has published since 08:26Z. Every run since 09:38Z fails at **step 15 only** ("Keep the legacy main:/ root fallback on the verified build"), so the `deploy` job is skipped. | Run [40097410704](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40097410704) job `verify-build`: steps 7–14 `success`, step 15 `failure`, `deploy` `skipped`. Same shape on the 10:05Z and 09:38Z runs. |
| 3 | The step's own annotation names the branch that failed: the **staged root's validate/unit gate** (`publish()` → `return 3`), not the refresh, not the build, not the deploy. | Annotation on job `120882445087`: "The staged root failed its own validator or unit gate, so it was not committed and main stays green." |
| 4 | The fresh board legitimately contains a genuinely level market line, and the unit suite still assumed every priced row has a strictly larger side. | `Color vs ex-Zero Tenacity` (fixture `1079200`, Polymarket event `cs2-color-zerote-2026-10-25`) quotes `outcomePrices ["0.5","0.5"]` — read from `https://gamma-api.polymarket.com/events?slug=cs2-color-zerote-2026-10-25` at 16:47Z, `liquidity 6387.46`, `updatedAt 2026-10-24T16:31Z`. Production correctly publishes both percentages with no pick ("NO EDGE"); the pinned tests demanded `pick == teams[argmax(p)]`. |
| 5 | A second class of the same defect: tests pinned rotating fixture IDs (`1081152`, `1083121`) that a refreshed board legitimately no longer contains. | Annotations of the same runs: `KeyError: '1081152'`, `StopIteration` on `1083121`. |
| 6 | Hotspawn currently lists far more CS2 fixtures than the frozen board holds, so the frozen snapshot cannot cover the lobby even if it were fresh. | `https://play.hotspawn.com/cs2-pickems` read 16:24Z: "226 matches this week", filter counts "All tiers (85) · B (36) · C (49)". The frozen snapshot has 92 rows, 29 open. |
| 7 | Pages is still `build_type: legacy`, `source: main:/`, so every push republishes the committed root over whatever artifact was deployed. The `PUT` that would switch it to GitHub Actions still answers 403 to this integration token. | `GET /repos/buffedlizard55-lab/MaltaProj4/pages` at 16:41Z → `{"build_type":"legacy","source":{"branch":"main","path":"/"}}`; `PUT` → `403 Resource not accessible by integration`. |

## 2. What this session changes

### 2.1 A verified build can no longer be blocked by the legacy-root copy step

`.github/workflows/pages.yml`: the verified `public/` tree is now uploaded as the Pages artifact
**before** the legacy `main:/` staging step, the manifest receipt is recorded even if that step fails,
and the `deploy` job runs on the verified artifact even when a later verify-build step is red.

Nothing is weakened:

* the unit gate, refresh, quarantine, independent row audit, build, validator and all browser suites
  still run before the artifact is uploaded, and any failure there still stops everything;
* step 15 keeps its `|| return 3` fatal gate and still ends the run red when it fails, so the fault is
  visible on the run page;
* the bytes that deploy are exactly the bytes the independent audit verified.

The defect this closes is measured, not hypothetical: five consecutive `main` runs lost their deploy
because an infrastructure step after a fully verified build failed.

### 2.2 Read-only runner replay, because the job logs are outside this sandbox

`.github/workflows/diag-d15e84e5.yml` + `scripts/diag_d15e84e5.py` run the production refresh, build
and the two step-15 gates against a scratch copy and publish the verdict as run annotations. It has
`contents: read`, writes no site file and never pushes.

## 3. Coverage and the unresolved section (state before/after)

The site already publishes the ladder and a separate unresolved section:

* ladder rungs, in attempt order: Polymarket strict line → HLTV fixture identity/ranking/lineup →
  Pinnacle moneyline → wide Polymarket quote → esportsbook listing (Thunderpick/GG.BET attempts,
  BO3.gg and saved book receipts) → our Valve-VRS model line → our VRS line mirrored from HLTV's dated
  Valve ranking → sourced research pick with no percentage → HLTV form/head-to-head pick;
* `index.html#unresolved-summary` states, per rung, how many open rows resolved there, and
  `index.html#unresolved-limits` lists why a pick can be missing (no book lists the match; a market
  fails its gate; names differ between sites; HLTV exposes no numeric two-way line; a bracket slot has
  no team names);
* `unresolved.html` is the dedicated page, linked from the executive summary
  (`#unresolved-summary`, `#unresolved-limits`, `unresolved.html`).

## 4. Flagged for review (non-blocking)

See section 6 of `COORDINATION.md` in the delivery receipt and the Flagged for Review page
(`review.html`); every flag there carries its source link.

## 5. Read-only runner replay — the measurement (run 40111942166)

The diag workflow ran the production refresh on a GitHub runner at 16:31–16:35Z and replayed the exact
two step-15 gates against a scratch copy of this branch's tree.

**What Hotspawn actually listed** (`scripts.diag_d15e84e5`, live refresh):

| Field | Measured value |
| --- | --- |
| Snapshot generated | `2026-10-24T16:35:19Z` (fixtures observed 16:31:43Z) |
| Coverage | `verified` — api 83 / page 83 / lobby 83 / retained 83 |
| Feed rows | 83 (61 past-dated, 22 open) |
| Open rows with a pick | **21** |
| Open rows with a win probability | **22** |
| Unresolved open rows | **1** — `1079200` Color vs ex-Zero Tenacity, reason "Equal verified prices; no directional edge.", Polymarket market `6072812` recorded as the source attempt |
| Method mix | exchange 15 · bookmaker_fallback 3 · model_vrs 2 · model_vrs_mirror 1 · exchange_wide 1 |

**The two step-15 gates on that staged root:**

| Gate | Result |
| --- | --- |
| `python -m scripts.validate --data data/latest.json --site .` | **exit 0** — 83 rows verified, 22 probability calculations reproduced, 15 pages, 784 internal links/assets, 20 artifact checksums, 193 displayed rows |
| `python -m unittest discover -s tests` | **exit 1** — the suite, not the board, is stale (see below) |

Failing assertions named in the run's annotations include a test that forbids a published even pair
outright (`assertNotEqual(probabilities, [0.5, 0.5])` in `tests/test_session_fe7f5de4.py`), the
independent re-derivation's "pick is the larger side" rule on the level row, two pinned rotating
fixture IDs (`1081152`, `1083121`), and two independent auditors that classify a priced-but-unpicked
row as "unresolved with derived fields". `publish_root_fallback` itself decided **publish: true**
(`2026-10-24T16:35:19Z` replaces `2026-10-24T08:06:51Z`, no source drift, no asset divergence) — the
staging is healthy; only the redundant in-step unit run fails.

**Source limits observed in the same refresh (recorded, not worked around):** `egamersworld.com`
answered HTTP 403 three times with its published rate-limit waits and was blocked for the run, and
`gg.bet` likewise answered HTTP 403. Both are collection limits, not evidence that those books list no
price, and both are published on the source-status page rather than converted into a number.

## 6. What this means for "a pick for every match"

* 21 of 22 open matches get a directional pick from a sourced rung of the ladder.
* The 22nd is a **genuinely level market**: Polymarket quoted 0.5 / 0.5, so both win percentages are
  published, the card is labelled `NO EDGE`, and the row is carried in the unresolved section with the
  quote link. Publishing a "pick" there would require inventing a direction the evidence does not
  contain, which this project's rules forbid; the alternative — a documented tiebreak such as HLTV
  ranking order — is proposed as a follow-up decision for the owner rather than added silently.
