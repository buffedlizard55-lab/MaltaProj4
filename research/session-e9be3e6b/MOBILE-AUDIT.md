# Session e9be3e6b — mobile audit

Measured `2026-10-24T06:49:04.758Z` against the locally built Pages artifact served under `/MaltaProj4/` with headless Chromium (playwright-core + @sparticuz/chromium). Script: `verification-e9be3e6b/mobile_probe.cjs`. Raw receipt: `mobile-measurements.json`.

## Before the fix (same script, earlier commit of this branch)

| Viewport | `#exec-summary` y | First pick y | First probability y | Tab bar y |
|---|---|---|---|---|
| 320 × 568 | 8661 | 320 | 447 | 507 |
| 390 × 844 | 8506 | 324 | 451 | 783 |

The executive-summary bar was visible in the DOM but came **after the entire 31-card pick list**. Cause: two mobile order blocks both ended with `main>*{order:7}` and neither assigned `#exec-summary` an explicit order, so the later block overrode an earlier `order:5`. The top green "View updated picks" button still worked, but the explicitly labelled summary navigation was effectively at the page bottom.

## After the scoped phone block

| Viewport | Summary y | Summary folded? | Summary links | First pick y | Both probabilities y | Tab bar y | Stale banner hidden | Horizontal overflow | Pick-board rows | Hotspawn links | External price links |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 320 × 568 | 309 | **no** | 8 | 371 | 498 | 507 | True | **no** | 31 | 31 | 40 |
| 390 × 844 | 309 | **no** | 8 | 375 | 502 | 783 | True | **no** | 31 | 31 | 40 |
| 768 × 1024 | 491 | **no** | 8 | n/a | n/a | none | True | **no** | 31 | 31 | 40 |
| 1440 × 900 | 425 | **no** | 8 | n/a | n/a | none | True | **no** | 31 | 31 | 40 |

`firstPickTop` / `firstProbabilityTop` are `n/a` at 768 and 1440 because the phone-only `.glance-card-mobile` cards are hidden there; the desktop table renders instead.

**Tap test:** at 320 × 568 a real click on `#exec-summary a[href="picks.html"]` navigated to `/MaltaProj4/picks.html` whose heading is "Updated CS2 picks.".

## What the probe asserts

* no horizontal overflow on `index.html`, `picks.html` or `unresolved.html` at 320, 390, 768 and 1440 px;
* the executive summary is outside any `<details>` and is actually visible (non-zero box, not `display:none`);
* its eight links include `picks.html`, `#picks-at-a-glance`, `unresolved.html`, `#unresolved-summary`, `matches.html` and `review.html`, all without a preliminary tap;
* on phones the summary is above the pick list and above y=500;
* the first pick and both of its percentages are above the fixed tab bar at 320 × 568 (498 < 507);
* the separate unresolved section exists on the home page and the unresolved page states "Every source tried, in order" plus the coverage boundary;
* the pick board shows 31 rows with 31 official Hotspawn match links and 40 external exchange/bookmaker/Valve links;
* the runtime stale banner is hidden while the snapshot is inside its eight-hour window, and there are no uncaught page errors.

## What changed in CSS

A single scoped block was appended to the canonical `site/assets/style.css` and re-staged to the identical root copy:

```css
@media(max-width:650px){
  body[data-page="index"] #freshness-strip{padding-bottom:6px}
  body[data-page="index"] main>#exec-summary{order:3}
  body[data-page="index"] #exec-summary{padding:4px 9px;margin-bottom:0}
  body[data-page="index"] #exec-summary>.eyebrow,
  body[data-page="index"] #exec-summary>.exec-bar-line,
  body[data-page="index"] #exec-summary>.exec-bar-note{display:none}
  body[data-page="index"] #exec-summary .exec-bar-links a{min-height:44px}
}
```

The full sentence and note remain at widths above 650 px; the section keeps `aria-label="Executive summary"`. Consolidating the two older duplicated order blocks is left to their owner and is recorded on Flagged for Review.

