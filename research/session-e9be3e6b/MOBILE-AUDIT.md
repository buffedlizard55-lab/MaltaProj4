# Session e9be3e6b — mobile audit

Measured `2026-10-24T07:17:10.835Z` against the locally built Pages artifact served under `/MaltaProj4/` with headless Chromium (playwright-core + @sparticuz/chromium). Script: `verification-e9be3e6b/mobile_probe.cjs`. Raw receipt: `mobile-measurements.json`.

## The defect both sessions measured

| Viewport | `#exec-summary` y (before) | First pick y | First probability y | Tab bar y |
|---|---|---|---|---|
| 320 × 568 | 8661 | 320 | 447 | 507 |
| 390 × 844 | 8506 | 324 | 451 | 783 |

The executive-summary bar was visible in the DOM but came **after the entire 31-card pick list**. Two mobile order blocks both ended with `main>*{order:7}` and neither assigned `#exec-summary` an order, so the later block overrode an earlier `order:5`. The top green button still worked, but the explicitly labelled summary navigation was effectively at the page bottom.

## Two fixes, one retained

This branch first appended a scoped block that moved a compact full bar to y=309 with 44px tap targets. Upstream PR #267 (session 4ed657ce) independently measured the same defect and instead added a 48px `#exec-quicknav` above the list while leaving the full bar after it, so the first card keeps its headroom. On merging `origin/main` this branch **adopted the upstream quick-nav and dropped its own duplicate CSS block**; otherwise two navigation rows would stack and push the first probability below the fixed tab bar.

## After adopting the upstream quick-nav

| Viewport | Quick nav y | Quick nav links | Full summary y | First pick y | Both probabilities y | Tab bar y | Stale banner hidden | Horizontal overflow | Pick-board rows | Hotspawn links | External price links |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 320 × 568 | 314 | picks.html, #unresolved-limits | 8711 | 370 | 497 | 507 | True | **no** | 31 | 31 | 40 |
| 390 × 844 | 314 | picks.html, #unresolved-limits | 8556 | 374 | 501 | 783 | True | **no** | 31 | 31 | 40 |
| 768 × 1024 | hidden (desktop) | picks.html, #unresolved-limits | 491 | n/a | n/a | none | True | **no** | 31 | 31 | 40 |
| 1440 × 900 | hidden (desktop) | picks.html, #unresolved-limits | 425 | n/a | n/a | none | True | **no** | 31 | 31 | 40 |

At 768 and 1440 px the phone-only `.glance-card-mobile` cards and the quick nav are hidden; the desktop table and the full `#exec-summary` bar render instead. The quick nav's `top` therefore reads 0 there because a `display:none` box has no position — the probe asserts visibility only at phone widths.

**Tap test:** at 320 × 568 a real click on `#exec-quicknav a[href="picks.html"]` navigated to `/MaltaProj4/picks.html` whose heading is "Updated CS2 picks.".

## What the probe asserts

* no horizontal overflow on `index.html`, `picks.html` or `unresolved.html` at 320, 390, 768 and 1440 px;
* the full executive summary is outside any `<details>` and visible, with in-site links to `picks.html`, `#picks-at-a-glance`, `unresolved.html`, `#unresolved-summary`, `matches.html` and `review.html` (plus the new `#unresolved-limits` anchor);
* on phones the quick nav is visible, outside any `<details>`, above the pick list and above y=500, and its links include `picks.html` and `#unresolved-limits`;
* the first pick and both percentages are above the fixed tab bar at 320 × 568 (497 < 507);
* the separate unresolved section exists on the home page and the unresolved page states "Every source tried, in order" plus the coverage boundary;
* the pick board shows 31 rows with 31 official Hotspawn match links and 40 external exchange/bookmaker/Valve links;
* the runtime stale banner is hidden while the snapshot is inside its eight-hour window, and there are no uncaught page errors.

## CSS retained (upstream PR #267)

```css
.exec-quicknav{display:none}
@media(max-width:650px){
  body[data-page="index"] main>#exec-quicknav{order:3}
  .exec-quicknav{display:flex;flex-direction:row;align-items:center;gap:8px;...}
  .exec-quicknav-actions a{...min-height:40px...}
}
```

The full sentence, note and all ten links remain on `#exec-summary` (after the list on phones, near the top on desktop). Consolidating the two older duplicated `main>*{order:7}` blocks is still left to their owner and is recorded on Flagged for Review.

