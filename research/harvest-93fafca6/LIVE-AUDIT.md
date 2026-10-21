# Independent audit of the live published site

Read at `2026-10-21T21:52:09.137791Z` from <https://buffedlizard55-lab.github.io/MaltaProj4/>.

| Check | Level | Finding |
| --- | --- | --- |
| `receipt-readable` | PASS | Live build receipt read |
| `publisher-identity` | INFO | Which publisher is serving the live site |
| `live-board-fresh` | PASS | The live board is inside its 8-hour evidence window |
| `manifest-consistency` | PASS | Every fetched file is byte-identical to the live manifest |
| `core-routes-available` | PASS | Every fetched core route answered 200 |
| `summary-links` | PASS | The executive summary links the pick list and every sibling page |
| `summary-anchors` | PASS | The summary carries the glance list and the unresolved limitations block |
| `glance-completeness-live` | PASS | Every open fixture on the live board is in the at-a-glance list |
| `glance-completeness-fresh` | PASS | The live board covers every fixture open in the paired fresh refresh |
| `pick-coverage` | PASS | Every open fixture has a pick, or is named with its limitation |
| `probability-not-from-hotspawn` | PASS | Every published percentage carries a non-Hotspawn primary source link |
| `open-row-methods` | INFO | How the live open rows are priced |
| `freshness-copy-honest` | PASS | The deployed freshness copy matches the served snapshot |
| `render-vs-receipt` | INFO | Render-time fingerprint of the served HTML |
| `mobile-markers` | PASS | The deployed pages meet the phone requirements |
| `external-evidence-reachable` | PASS | Primary source links behind open rows were re-requested |

**13 pass · 3 info · 0 warn · 0 fail**

## Detail

### `receipt-readable` — PASS

**Live build receipt read**

revision `1b2d92e4df9082d99c16731d66d14f2209b10b20`, built `2026-10-21T21:48:39.650256Z`, snapshot `2026-10-21T21:48:39.360126Z`, 75 rows, 20 files in the manifest.

- <https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json>

### `publisher-identity` — INFO

**Which publisher is serving the live site**

Served by a workflow artifact for commit `1b2d92e4df9082d99c16731d66d14f2209b10b20`. Snapshot age at read time 0.06 h; age when built 0.00 h. HEAD `01310874c79b`, committed root receipt `ac5c81648d40`.

- <https://github.com/buffedlizard55-lab/MaltaProj4/actions>
- <https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages>

### `live-board-fresh` — PASS

**The live board is inside its 8-hour evidence window**

Snapshot generated `2026-10-21T21:48:39.360126Z`, read `2026-10-21T21:52:09.137791Z`: 0.06 h old.

### `manifest-consistency` — PASS

**Every fetched file is byte-identical to the live manifest**

20 files compared by SHA-256; 0 differences; 0 unavailable (non-navigation paths only).

### `core-routes-available` — PASS

**Every fetched core route answered 200**

13 routes checked: index.html, picks.html, unresolved.html, matches.html, analysis.html, review.html, sources.html, evidence.html, methodology.html, 404.html, assets/style.css, assets/app.js.

### `summary-links` — PASS

**The executive summary links the pick list and every sibling page**

13 in-site targets found, including all 7 required. The labelled shortcut nav ("Where the picks are") carries 6 links: analysis.html, matches.html, picks.html, unresolved.html?status=needs.

### `summary-anchors` — PASS

**The summary carries the glance list and the unresolved limitations block**

#freshness-strip, #picks-at-a-glance and #unresolved-summary exist, and #pick-limitations is nested inside #unresolved-summary.

### `glance-completeness-live` — PASS

**Every open fixture on the live board is in the at-a-glance list**

13 open fixtures, 26 glance rows, identical id sets, in start-time order.

### `glance-completeness-fresh` — PASS

**The live board covers every fixture open in the paired fresh refresh**

Refresh `2026-10-21T21:52:08.685813Z` reports coverage `verified` and lists 13 open fixtures; all 13 appear on the live board. 0 live row(s) are no longer open in the refresh (none), which is expected when a match locks or starts between the two reads.

### `pick-coverage` — PASS

**Every open fixture has a pick, or is named with its limitation**

13 open: 11 priced, 2 research-only picks, 0 with no pick.

### `probability-not-from-hotspawn` — PASS

**Every published percentage carries a non-Hotspawn primary source link**

11 priced open rows, each with at least one dated external evidence link. Evidence hosts seen: github.com; polymarket.com.

### `open-row-methods` — INFO

**How the live open rows are priced**

exchange: 4, exchange_wide: 1, model_vrs: 6, research_rank_single: 1, research_vrs_single: 1

### `freshness-copy-honest` — PASS

**The deployed freshness copy matches the served snapshot**

Snapshot `2026-10-21T21:48:39.360126Z` is 0.06 h old at read time and the strip says stale=False, so the copy and the data agree. Client-side expiry hook (assets/app.js `live-expired` + #runtime-stale) ships, so a row whose deadline passes while the page is open is re-expired in the browser.

### `render-vs-receipt` — INFO

**Render-time fingerprint of the served HTML**

Strip says stale=False; receipt age at read time 0.06 h; receipt age at its own `built_at` 0.00 h. A strip that is stale while the receipt is not proves the HTML was rendered after the snapshot it carries.

### `mobile-markers` — PASS

**The deployed pages meet the phone requirements**

Device-width viewport on all 10 readable pages; persistent .mobile-tabs bar on index.html/picks.html/unresolved.html/matches.html; @media(max-width:650px) breakpoint present; tab tap target 60px; evidence-link tap target 44px; tables collapse to cards (min-width:0) instead of scrolling sideways.

### `external-evidence-reachable` — PASS

**Primary source links behind open rows were re-requested**

6 distinct URLs checked. 6 answered 200. Access-limited or unanswered (recorded, not treated as broken, and never bypassed): none

## Served files

| File | HTTP | SHA-256 (served) |
| --- | --- | --- |
| `404.html` | 200 | `1c7aaa9e7b922a3d` |
| `analysis.html` | 200 | `991cb0ab337d9b18` |
| `assets/app.js` | 200 | `0ce71e400147771e` |
| `assets/favicon.svg` | 200 | `5b0ba0da9b9bec50` |
| `assets/style.css` | 200 | `521b56ef13d1784c` |
| `build-info.json` | 200 | `71d470fbd9784e01` |
| `data/latest.json` | 200 | `635aa1328921a280` |
| `data/matches.csv` | 200 | `a9fe46b86f92d43d` |
| `evidence.html` | 200 | `de1e7f935b30ce68` |
| `index.html` | 200 | `a71c8d47741b7600` |
| `matches.html` | 200 | `ce07369c8dd34024` |
| `methodology.html` | 200 | `db6dd3e60721627f` |
| `picks.html` | 200 | `684ff7cf67948569` |
| `review.html` | 200 | `a9061422bf32d476` |
| `site/index.html` | 200 | `7ad39335aef2960a` |
| `site/methodology.html` | 200 | `130024ea27020261` |
| `site/picks.html` | 200 | `de8e71d8a3a1f7b2` |
| `site/review.html` | 200 | `91547a7e0d0e5b1e` |
| `site/unresolved.html` | 200 | `d8c18e13a798f6d0` |
| `sources.html` | 200 | `551bb6147985300b` |
| `unresolved.html` | 200 | `c43cd72c4d4e6cd3` |

