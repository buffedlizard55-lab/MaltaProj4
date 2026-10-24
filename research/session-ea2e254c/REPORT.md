# Session ea2e254c — every-match picks, the tall-phone layout, and live line verification

**Branch:** `arena/ea2e254c-maltaproj4` · **Start base:** `dce494b` · **Rebased onto:** `5ddf0f2` (PR #251)
**Measured:** 2026-10-24 06:20–07:15 UTC · **Snapshot under test:** `2026-10-24T06:19:43Z` (fixtures observed 06:16:00Z)

## 1. The brief, and what the repo already had

| Requirement | State |
| --- | --- |
| A pick for **every** match listed on Hotspawn | 92 feed rows · **31 open · 31 picked · 31 priced · 0 unresolved** |
| A **separate unresolved section** with the limitations, linked from the executive summary | `#unresolved-summary` + `#pick-limitations`, linked from `#exec-summary` and `unresolved.html` |
| Executive summary with **in-site links** to the updated picks | `#exec-summary` bar, always visible, phone bottom bar `Home · Picks · Unresolved · Matches · Analysis` |
| **Mobile** readability | 9 Chromium suites: 320/390/768/1440 px, axe WCAG 2.1 AA, no horizontal overflow, phone-first pick placement |
| Refresh every 4–8 h | cron `4,19,34,49 * * * *` + 10-minute watchdog |
| **Never** Hotspawn's percentages | exchange / wide exchange / bookmaker listing / Valve VRS / HLTV mirror only; asserted by test |

The board was already complete. This session's work was to prove that **line by line**
and to close the delivery/layout defects that were still open at its base.

## 2. What was actually broken at the base commit

`python -m unittest discover -s tests` on untouched `dce494b` → **8 failures, 1 error** of 1,233.
`pages.yml` runs that suite *before* refreshing sources, so scheduled runs died at
*Unit and independent failure-mode tests* and never reached refresh → build → deploy.

1. **Served stylesheet drift (6 failures).** `assets/style.css` (what every root page links to, i.e.
   the legacy root fallback) had drifted from `site/assets/style.css` and was **missing one closing
   brace**. The `@media(max-width:650px) and (max-height:700px)` block opening at line 491 swallowed
   the remaining ~9 KB — including the home-page phone ordering. On a 390×844 phone (taller than
   700 px) **none** of those rules applied. That is the reported "confusing on my phone".
2. **Alias-blind verifier (3 failures).** Fixture `1083121` is priced from Polymarket `6081997`,
   whose outcomes read `["Tropa do KinGui","MEIA NOITE"]` while Hotspawn lists `Projeto do KinGui`.
   The row ships a reviewed, HLTV-sourced alias; the verifier compared raw labels only and reported
   a reproducible 61.5% as irreproducible.

**Concurrency note, stated plainly.** While this session was verifying, PR **#251** merged to `main`
and repaired the same two defects upstream (canonical CSS +6 lines in a balanced block; an
`alias_groups()` path in `verify_0cc1138a.py`). Rather than land a duplicate diff, this session
rebased onto `5ddf0f2`, re-ran every gate on the merged tree, and kept only what is additive:
a **semantic** CSS regression test, alias tests bound to the evidence rules, live line verification,
and four published findings. Nothing from #251 was discarded or overwritten.

## 3. What this session adds

* `tests/test_session_ea2e254c.py` (13 tests). The key one that existing pins do not cover:
  `test_phone_ordering_is_not_nested_in_a_short_viewport_query` walks brace depth and asserts the
  **enclosing at-rule** of each phone-ordering selector. Brace *balance* (already pinned) cannot catch
  a rule that sits, balanced, inside `max-height:700px` — tall phones still lose the layout.
  Also: served copy must equal canonical copy byte for byte; alias accepted only from an https register
  group naming **both** labels; unregistered labels still refused; tampered price on the aliased row
  still rejected; every open row picked/priced/sourced; no `picked_percent`; exec-summary and
  limitations anchors present on `index.html`; every page declares a mobile viewport.
* Four additive entries in `data/review-notes.json` (canonical `indent=1`), published on `review.html`.

## 4. Live source verification (re-read outside the sandbox, 06:30–07:00Z)

| Method | Row | Board value | Live read | Result |
| --- | --- | --- | --- | --- |
| `exchange` | 1079193 FOKUS–ex-6666 | 0.78 / 0.22 | Polymarket `6065787` → `["0.78","0.22"]`, bid 0.77 ask 0.79, start `2026-10-24 08:00:00+00` | **exact** |
| `exchange_wide` | 1081154 BakS–ILLYRIANS | 0.585 / 0.415 | Polymarket `6098193` → `["0.585","0.415"]`, bid 0.37 ask 0.80 | **exact** |
| `bookmaker_fallback` | 1083123 Grêmio–Yawara | 0.3077 / 0.6923 | bo3.gg → Thunderpick **2.97 / 1.32**; de-vig `[1/2.97, 1/1.32]` → 0.30769 / 0.69231 | **exact** |
| `model_vrs` | 1081152 HAVU–Azuolas | points 937 / 863 | Valve `standings_global_2026_10_05.md` @ `eec4853`: HAVU **937** (#124), Azuolas **863** (#140) | **exact** |
| `model_vrs_mirror` | 1083122 LOS NINOS–BORRACHEIROS | points 573 / 744 | HLTV Valve regional ranking 24 Oct 2026: BORRACHEIROS **744** (#34) | **1 of 2** |
| Fixture reality | 1082695 Galorys–paiN | board row | Hotspawn match page: 24 OCT 18:00, Circuit X Curitiba #4, both lineups, "Pick'Ems — Predict the winner of this match" | **confirmed** |
| Alias source | 1083121 | 0.615 | HLTV team/13151 *Tropa do KinGui* + fixture 2399904 in the same event; Polymarket opponent/start identical | **parity confirmed** |

The VRS arithmetic was also recomputed by hand: `Q = ln10/400`, `G = 0.97337`,
`E = 1/(1+10^(−G·74/400)) = 0.6022`, `0.5 + 0.7986·(E−0.5) = 0.58157` — the published 58.157%.

## 5. Gates on the rebased tree

| Gate | Result |
| --- | --- |
| `unittest discover -s tests` | **1,267 tests OK** (1 skipped; 13 new) |
| `unittest discover -s audits` / `verification-95b588c2` / `verification-c6` | 9 / 5 / 12 OK |
| `verification-c6/audit_snapshot.py public/data/latest.json` | **0 failures** |
| `research/session-0cc1138a/verify_0cc1138a.py` | **31/31 re-derived, 0 failures** |
| `scripts.validate --data data/latest.json --site .` | 92 rows · 31 calculations · 15 pages · **874 links/assets** · 20 checksums · 234 displayed rows |
| `npm run test:browser` | **9 suites green** (32 page/viewport scans, expiry, research-quote, phone-first at 320×568 **and** 390×844) |

## 6. Findings published for review (non-blocking)

* `session-ea2e254c-tall-phone-css-trap-2026-10-24` — the drift, and why balance-only pinning is not enough.
* `session-ea2e254c-alias-verify-2026-10-24` — alias verified by fixture parity; the **rename statement**
  was not found on any HLTV page read this session.
* `session-ea2e254c-pickem-lobby-render-2026-10-24` — the pick'em page's own filter read *All tournaments (88)*
  and rendered 25 cards while the API/board carry 92/31; six board fixtures were absent from the rendered
  view but each has its own Hotspawn match page with a pick'em prompt (1082695 opened and confirmed).
* `session-ea2e254c-live-line-spotchecks-2026-10-24` — the table in §4, including the one value that is
  verified only arithmetically.

## 7. Files touched

`tests/test_session_ea2e254c.py` (new), `data/review-notes.json` (4 additive notes, `indent=1`),
`research/session-ea2e254c/REPORT.md` (this file), `COORDINATION.md` (claim + receipt), and generated
pages + `build-info.json` via `scripts.build` / `scripts.stage_legacy` only.
