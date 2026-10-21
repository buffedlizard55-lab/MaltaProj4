# Independent audit of the live published site

Read at `2026-10-21T21:33:51.555391Z` from <https://buffedlizard55-lab.github.io/MaltaProj4/>.

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

revision `ac5c81648d40e4b851ae954b6acb00acfdbee096`, built `2026-10-21T21:27:37.090500Z`, snapshot `2026-10-21T21:27:36.742398Z`, 75 rows, 20 files in the manifest.

- <https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json>

### `publisher-identity` — INFO

**Which publisher is serving the live site**

Served by a workflow artifact for commit `ac5c81648d40e4b851ae954b6acb00acfdbee096`. Snapshot age at read time 0.10 h; age when built 0.00 h. HEAD `c55b4b0eeb3e`, committed root receipt `88b1b2c3b969`.

- <https://github.com/buffedlizard55-lab/MaltaProj4/actions>
- <https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages>

### `live-board-fresh` — PASS

**The live board is inside its 8-hour evidence window**

Snapshot generated `2026-10-21T21:27:36.742398Z`, read `2026-10-21T21:33:51.555391Z`: 0.10 h old.

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

Refresh `2026-10-21T21:33:51.164538Z` lists 13 open fixtures; all 13 appear on the live board. 0 live row(s) are no longer open in the refresh (none), which is expected when a match locks or starts between the two reads.

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

Snapshot `2026-10-21T21:27:36.742398Z` is 0.10 h old at read time and the strip says stale=False, so the copy and the data agree. Client-side expiry hook (assets/app.js `live-expired` + #runtime-stale) ships, so a row whose deadline passes while the page is open is re-expired in the browser.

### `render-vs-receipt` — INFO

**Render-time fingerprint of the served HTML**

Strip says stale=False; receipt age at read time 0.10 h; receipt age at its own `built_at` 0.00 h. A strip that is stale while the receipt is not proves the HTML was rendered after the snapshot it carries.

### `mobile-markers` — PASS

**The deployed pages meet the phone requirements**

Device-width viewport on all 10 readable pages; persistent .mobile-tabs bar on index.html/picks.html/unresolved.html/matches.html; @media(max-width:650px) breakpoint present; tab tap target 60px; evidence-link tap target 44px; tables collapse to cards (min-width:0) instead of scrolling sideways.

### `external-evidence-reachable` — PASS

**Primary source links behind open rows were re-requested**

6 distinct URLs checked. 6 answered 200. Access-limited or unanswered (recorded, not treated as broken, and never bypassed): none

## Served files

| File | HTTP | SHA-256 (served) |
| --- | --- | --- |
| `404.html` | 200 | `8e3b62bd3774bcd9` |
| `analysis.html` | 200 | `a97cdb6ece6d8434` |
| `assets/app.js` | 200 | `0ce71e400147771e` |
| `assets/favicon.svg` | 200 | `5b0ba0da9b9bec50` |
| `assets/style.css` | 200 | `521b56ef13d1784c` |
| `build-info.json` | 200 | `a25d3d14ab9b1c82` |
| `data/latest.json` | 200 | `11f567106094121c` |
| `data/matches.csv` | 200 | `642c5e509a5eb745` |
| `evidence.html` | 200 | `a223b5d27a239194` |
| `index.html` | 200 | `e9609acc22b3ede9` |
| `matches.html` | 200 | `fa510a60a60c11d7` |
| `methodology.html` | 200 | `db6dd3e60721627f` |
| `picks.html` | 200 | `87137fcc486ad59e` |
| `review.html` | 200 | `0c87db88dd6c9d8a` |
| `site/index.html` | 200 | `7ad39335aef2960a` |
| `site/methodology.html` | 200 | `130024ea27020261` |
| `site/picks.html` | 200 | `de8e71d8a3a1f7b2` |
| `site/review.html` | 200 | `91547a7e0d0e5b1e` |
| `site/unresolved.html` | 200 | `d8c18e13a798f6d0` |
| `sources.html` | 200 | `3b0c4ec5f0c067c3` |
| `unresolved.html` | 200 | `8ad2ea1a642c77cf` |

