# Session 8e4ff8d2 — the board was withholding every pick; the publisher is green again

## What was measured before anything was changed

| Fact | Value | Where it comes from |
| --- | --- | --- |
| Published snapshot | `2026-10-25T01:47:42.430039Z`, 79 feed rows, 18 open | `data/latest.json` on `main` (`6ade440`) |
| Age of that snapshot at claim time | **11.7 h** against an 8-hour evidence window | `data/latest.json` `generated_at` vs 13:30Z |
| Consequence | the live site renders *"Snapshot expired or timestamp unverified. Current picks are withheld."* | `index.html` on `main` |
| Last successful publish run | [40151731896](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40151731896) (01:43Z) | Actions API |
| Failed publish runs since | [40170923727](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40170923727) (06:56Z), [40193317196](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40193317196) (12:29Z) | Actions API |
| Independent audit verdict | `"inside_eight_hour_window": false`, `"error": "Live snapshot is expired"` | [40190478424](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40190478424) |
| Pages configuration | `build_type: legacy`, source `main:/`, `status: built` | `GET /repos/.../pages` |

Both failed runs completed *Unit and independent failure-mode tests*, *Refresh official sources* and
*Withhold any row the independent audit cannot reproduce*, and then failed
**`Build and independently verify every row, calculation and internal link`**
(`verify-build: .github#31`, exit 1). That step owns four commands; `upload-pages-artifact` and `deploy`
were skipped, so nothing could reach the site.

## How the failing assertion was named

This sandbox reaches `github.com` / `api.github.com` only, so workflow logs (served from
`productionresultssa17.blob.core.windows.net`) and artifact blobs are unreadable here, and every official
source (Hotspawn, HLTV, Polymarket, Pinnacle) is unreachable. The measurement therefore ran on GitHub's
own egress: `.github/workflows/diag-8e4ff8d2.yml` (non-publishing — no `deploy-pages`, no
`upload-pages-artifact`, no root-fallback commit) refreshed the sources, ran each command of the failing
step separately, and emitted the return codes and failing lines as check-run annotations plus a committed
receipt.

Run [40197572628](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40197572628):

```
refresh_rc=0  quarantine_rc=0  row_audit_rc=0  build_rc=0
validate_rc=1 <- the failing command
published_audit_rc=0  publish_rc=0  staged_validate_rc=1  staged_unit_rc=1  browser_rc=1
```

```
File "scripts/validate.py", line 376, in validate_data
  validate_model_row(m, q, now)
File "scripts/validate.py", line 122, in validate_model_row
  assert lineup_source_ok(m, team, check.get('lineup') or []), 'Model roster has no HLTV source on this row'
AssertionError: Model roster has no HLTV source on this row
```

The capture (`research/session-8e4ff8d2/snapshot-40197572628.json`) shows one row failing, everything else
consistent: Hotspawn fixture **`1086697` Projeto do KinGui vs Yawara** (CCT South America 2026 Series #7,
2026-10-25T19:00Z), priced by our own Valve-VRS line.

## The defect and the repair

* Valve's official 2026-10-05 standings list that Brazilian core as **`ex-Keyd Stars`** (854 points,
  #144), so the model priced the fixture from that row.
* The roster evidence comes from HLTV match page **2399904**, which labels the same club
  **`Tropa do KinGui`**.
* `Tropa do KinGui` ↔ `Projeto do KinGui` is a **registered, primary-sourced alias**:
  `data/identities.json` (`names: [Tropa do KinGui, Projeto do KinGui, ex-Keyd Stars]`,
  `source: https://www.hltv.org/matches/2399904/...`), and the row carries the same entry in its own
  `identity_sources`. Every pricing tier already resolved it — `validate_model_row` accepts the alias for
  the Valve label.
* `scripts.validate.lineup_source_ok` compared the lineup's team label to the Hotspawn label **exactly**.
  So the very roster the model had just verified was declared unsourced and the whole board refused to
  publish.

Repair (`scripts/validate.py`):

* new `_sourced_aliases(m, team)` — name groups for a club from the reviewed register
  (`data/identities.json`) **or** the row's own `identity_sources`, and **only** when the entry carries an
  `https://` primary source;
* new `lineup_team_matches(m, team, label)` — exact name, or a label inside one of those groups;
* `lineup_source_ok` now uses it for the HLTV fixture lineups, the retained lineup receipts and the HLTV
  team pages. The five stored players must still match the page exactly. No fuzzy matching, no suffix
  stripping, no unregistered label, and no inference added.

Second defect, found while verifying the same fresh build: `tests/browser_019a253a.cjs` failed with
*"the first probabilities must clear the tab bar at 320x568"*. Measured on the fresh board at 320×568, the
first card's percentages ended at y=519 under a tab bar at y=507 — the pick and the numbers could not both
be read on a short phone. `site/assets/style.css` (copied byte-identically to `assets/style.css`) now
tightens the card on phones ≤700px tall: 13px padding, an 11px row gap, and the two team labels above the
percentages on one ellipsised line each. No number is changed and no content is removed; the full names
remain in the team block directly above, in each percentage's `aria-label`, and in the row's sources.

## Verification on the same fresh snapshot (`2026-10-25T13:30:38Z`)

| Gate | Result |
| --- | --- |
| Coverage | 78 feed rows · **17 open · 17 picks · 17 win probabilities · 0 unresolved** |
| Method mix | 12 exchange · 1 wide exchange · 4 our own Valve-VRS model line |
| `scripts.validate --data data/latest.json --site .` | exit 0 — 78 rows, 17 calculations, 15 pages, 730 links/assets, 20 checksums, 182 displayed rows |
| Unit suite | **1,616 tests OK** (12 skipped) |
| Audits / integrity / verification-c6 | 9 OK · 5 OK · 12 OK |
| Independent row auditor (`verification-c6/audit_snapshot.py`) | 0 failures |
| Chromium suites (`npm run test:browser`) | all pass, 0 assertion errors |
| Phone measurement (`research/session-8e4ff8d2/mobile-measurements.json`) | 320×568: pick 362–385, both percentages 414–441, tab bar top 507 → **clear**; 390×844 and 412×915 also clear, no horizontal overflow |

## Sources used

* Actions API for every run cited: `/repos/buffedlizard55-lab/MaltaProj4/actions/runs/<id>` and
  `/actions/runs/<id>/jobs` (40170923727, 40193317196, 40197572628, 40190478424, 40151731896) and
  `/repos/buffedlizard55-lab/MaltaProj4/pages`.
* HLTV match 2399904 — the primary source behind the alias:
  <https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7>
* Valve's official global standings (pinned commit `eec4853d`):
  <https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md>
* The refreshed capture itself, with every row's own source URLs and observation times:
  `research/session-8e4ff8d2/snapshot-40197572628.json`, and the diagnostic logs in
  `research/session-8e4ff8d2/logs/40197572628/`.

Hotspawn supplies fixture inventory, start and lock times only — never a pick or a probability. No price,
pick or percentage was edited by hand in this session; every number in the rebuilt board is the one the
refresh produced from the sources above.

## Flagged for review (non-blocking)

1. **The board withheld every pick for 11.6 hours** (2026-10-25T06:56Z → this repair) because a single
   team-label alias made the roster-source check fail, not because any source was missing or any price was
   wrong. Published on **Flagged for Review** as
   `session-8e4ff8d2-alias-roster-source-froze-the-publisher-2026-10-25`.
2. **The 4 non-market rows are our own model line, not market prices.** They are labelled
   `Valve VRS model estimate` on every row, and the executive summary and `sources.html` say so.
3. **The 61 past-dated feed records** Hotspawn still returns as `scheduled` keep appearing in *All matches*
   and are never presented as current picks.
4. **Pages remains `build_type: legacy` with source `main:/`.** The committed root fallback is what
   visitors receive, so the staged-root step is the delivery path and must keep passing.
5. **`.github/workflows/diag-8e4ff8d2.yml` is kept** as a non-publishing, push-triggered diagnostic for this
   branch only (it cannot be dispatched until it exists on the default branch). It never deploys and never
   commits a root fallback; `tests/test_session_8e4ff8d2.py` fails if that changes.

## Integration note — the repair was already on `main` when this branch rebased (2026-10-25 13:55Z)

While this session was verifying, `main` advanced to `23744d4` and session **b85ad9b4** had merged an
equivalent repair (**PR #316**): `scripts/validate.py` gained `same_club()`, which bridges the same
Hotspawn/HLTV club label through the sourced identity register, and it is applied in `lineup_source_ok` for
the fixture lineups, the retained lineup receipts and the HLTV team pages. Session a7f788c8's board entry also
names sessions 601ce27c (PR #313, test repair) and 046b2e46 (PR #314) working the same defect.

Per this repository's coordination rule, the rebase **adopted `main`'s version of `scripts/validate.py`
wholesale and dropped this session's duplicate `_sourced_aliases()` / `lineup_team_matches()` helpers** rather
than layering a second implementation over the one that shipped. What this session contributes on top, all
re-verified after the rebase on the merged tree:

* the non-publishing diagnostic (`scripts/diag_8e4ff8d2.py`, `.github/workflows/diag-8e4ff8d2.yml`) and its
  receipt, which is how the failing assertion was named from a sandbox that cannot read workflow logs;
* the independent re-verification of the upstream repair against the **real failing row** rather than a
  synthetic one — `tests/test_session_8e4ff8d2.py` asserts that fixture `1086697`'s stored roster is now
  reproducible, that an unregistered label is still refused, that the alias never excuses a different roster,
  and that an unsourced spelling is not a bridge;
* the **fresh capture** `2026-10-25T13:30:38Z` published on this branch (main's committed snapshot was still
  the expired `01:47:42Z` one), with 17 open / 17 picks / 17 win probabilities / 0 unresolved;
* the short-phone stylesheet repair, which the browser gate still needed on that fresh board
  (`tests/browser_019a253a.cjs`: percentages ended at y=519 under a 507px tab bar);
* a review note on **Flagged for Review** recording both the outage and the overlap.

Post-rebase gates on the merged tree: `scripts.validate` exit 0 (public and root), **1,629 unit tests OK**,
audits 9 OK, integrity 5 OK, verification-c6 12 OK, all Chromium suites pass, and the phone receipt shows the
pick at 362–385 and both percentages at 414–441 against the 507px tab bar at 320×568.

## Publication capture adopted (2026-10-25 14:00Z)

The capture committed earlier on this branch (`2026-10-25T13:30:38Z`) carried a first row locking at
`13:54Z`. That row expired while the pull request's browser gate was running, so app.js correctly withheld it
and `tests/browser_019a253a.cjs` failed on the PR head
([40199433314](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40199433314) — every step up to
*Build and independently verify* passed, only *Phone, tablet, desktop, accessibility and exact-boundary expiry
checks* failed). The same branch's non-publishing diagnostic run
([40199429511](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40199429511)) had meanwhile run the
whole publisher pipeline on a fresh capture and returned
`refresh_rc=0 quarantine_rc=0 row_audit_rc=0 build_rc=0 validate_rc=0 published_audit_rc=0 publish_rc=0
staged_validate_rc=0 staged_unit_rc=0 npm_rc=0 browser_rc=0`.

This branch therefore publishes that capture — `2026-10-25T13:54:18Z`, fixtures observed `13:50:44Z`:
**78 feed rows · 16 open · 16 picks · 16 win probabilities · 0 unresolved**, earliest lock `14:54Z`
(10 exchange, 1 wide exchange, 1 researched bookmaker listing, 4 our own Valve-VRS model line).
Regenerated from it: unit suite **1,629 tests OK**, audits 9, integrity 5, verification-c6 12, independent
row auditor 0 failures, all Chromium suites, and the phone receipt at 320×568 (pick 362–385, both
percentages 414–441, tab bar 507).
