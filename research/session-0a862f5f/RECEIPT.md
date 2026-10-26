# Session 0a862f5f — lobby/feed coverage gap, measured 2026-10-26

Everything below was read from the live official sources during this session. Each
claim names the exact URL it came from and the time it was read. Nothing here is
inferred from a screenshot, an aggregator, or Hotspawn's own crowd percentages.

## 1. The published capture the site was serving

Source: `data/latest.json` and `build-info.json` committed on `main`
(`https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/build-info.json`),
cross-checked against the GitHub Pages build list for the repository.

| Fact | Value | Source |
| --- | --- | --- |
| Build revision | `3b158a37e442b0440521a83350d4d515eb20aa49` | `build-info.json` |
| Built at | `2026-10-26T00:10:50.130013Z` | `build-info.json` |
| Fixture observation | `2026-10-26T00:07:16.611284Z` | `data/latest.json` `fixtures_observed_at` |
| Rows in snapshot | 73 (11 open, 62 past-dated) | `data/latest.json` |
| Open rows with a pick | 11 of 11 | `data/latest.json` |
| Open rows with a win probability | 11 of 11 (8 market, 3 our VRS model) | `data/latest.json` |

## 2. The public lobby, read directly

Source read: `https://play.hotspawn.com/lobby` at **2026-10-26T00:47Z** (this
session, live HTTP read of the public page; the page's own filter header reports
`All tiers (81)` and `CS2`).

The lobby listed these CS2 fixtures, which the 00:07:16Z capture does **not**
contain (the capture holds 1082858, 1082859, 1093218, 1082860, 1082861,
1082897, 1082898, 1082900, 1082901, 1082792, 1082793 among its open rows):

| Id | Fixture | Event |
| --- | --- | --- |
| 1079201 | INOX Division vs Nemesis | NODWIN Clutch Series #13 |
| 1081159 | LFO 10 vs ex-6666 | CCT Europe 2026 Series #12 |
| 1079202 | FOKUS vs ex-Zero Tenacity | NODWIN Clutch Series #13 |
| 1081160 | HAVU vs ILLYRIANS | CCT Europe 2026 Series #12 |
| 1079203 | Metizport vs BRUTE | NODWIN Clutch Series #13 |
| 1081162 | ex-RUSTEC vs Spirit Academy | CCT Europe 2026 Series #12 |
| 1081163 | BakS vs Saint Sinners | CCT Europe 2026 Series #12 |
| 1081164 | Inner Circle Academy vs Lavked | CCT Europe 2026 Series #12 |

Permalinks rendered by the lobby for these rows follow the shape
`https://www.hotspawn.com/matches/<slug>-<id>`, e.g.
`https://www.hotspawn.com/matches/inox-division-vs-nemesis-nodwin-clutch-series-13-1079201`.

## 3. The same feed, read again 50 minutes later

Source read: `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`
at **2026-10-26T00:57Z**.

The payload then contained those ids interleaved with rows the 00:07Z capture
already held — in payload order:
`1082858, 1082859, 1079201, 1081159, 1079202, 1081160, 1079203, 1093218, 1082860, …`
and `1079200` (Color vs ex-Zero Tenacity) immediately before `1082858`.
`total_picks` on those rows was **2–8**, against **42–49** on the DFRAG fixtures
captured earlier.

## 4. What that supports, and what it does not

* **Supported:** at the 00:07:16Z capture the board was complete *as of that
  observation* and the lobby at 00:47Z showed fixtures the capture lacked.
* **Supported:** the feed returned them at 00:57Z, so the collector's
  15-minute cadence will pick them up; the gap is transient, not permanent.
* **Not supported, and therefore not claimed anywhere on the site:** that the
  cause is lazy publication by Hotspawn. The correlation with `total_picks` and
  the payload order is consistent with it; it is not proof.
* **Never done:** inferring a start time, lock time, team identity or probability
  for a lobby-only row. The feed publishes `scheduled_start_time` and `lock_time`;
  a lobby listing publishes neither, and `scripts.normalize_fixtures` requires
  both, so a row cannot be priced without inventing one.

## 5. What changed in this session because of the above

* `scripts/lobby_gap.py` — parses fixture ids from the lobby/CS2 HTML the refresh
  already reads, compares them with the ids the feed returned, and returns the
  difference. No row is synthesized.
* `scripts/inventory.py` — keeps the two HTML bodies, runs that comparison, and
  records a `lobby_gap` issue naming the ids with the lobby URL when the sets
  differ.
* `scripts/refresh.py` — publishes `lobby_coverage` on the snapshot (feed count,
  lobby count, `lobby_read`, the missing ids, observation time, both official
  URLs, and the "named, never priced" note).
* `scripts/build.py` — renders that record as a **Lobby coverage** panel on the
  executive summary, the unresolved page and the Flagged for Review page. It
  renders nothing when a snapshot predates the check, so an older capture cannot
  imply parity it never measured.
* `data/review-notes.json` — the finding above, with its three source links.
* `tests/test_session_0a862f5f.py` — 11 regressions covering the parser, the
  comparison, discovery (no synthetic row, issue named), and the render paths.

## 6. Gates run on this branch

| Gate | Result |
| --- | --- |
| `python -m unittest discover -s tests` | 1,789 tests OK (14 skipped) |
| `python -m unittest discover -s audits -p 'test_*.py'` | 9 OK |
| `python verification-95b588c2/test_integrity.py` | 5 OK |
| `python -m unittest discover -s verification-c6` | 12 OK |
| `python -m scripts.validate --data data/latest.json --site public` | 73 rows, 11 calculations, 15 pages, 694 links, 20 checksums, 165 displayed rows |
| `npm run test:browser` | `"failures": []` across all 13 Chromium suites |

Measured phone geometry from the browser gates at 390 × 844: first pick card top
243 px, first team percentages at 390–420 px, tab bar at 854 px, no horizontal
overflow at 320 / 390 / 768 / 1440 px.
