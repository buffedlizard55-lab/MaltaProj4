# Session 5bf1c3eb — every-match pick coverage, the closed-window register, and the mobile executive summary

**Session:** `arena/5bf1c3eb-maltaproj4`
**Live harvest:** run [40251492364](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40251492364)
(fixtures observed `2026-10-26T00:53:32Z`, snapshot generated `2026-10-26T00:57:14Z`), second run
[40253421231](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40253421231) retains the per-row
no-line receipts for the non-market-priced rows. Neither run publishes or deploys anything.

## 1. What the brief asked, and what the live board actually shows

| Question from the brief | Measured answer (official sources) |
| --- | --- |
| Full list of Hotspawn CS2 matches | **81 feed rows** returned by the fixtures endpoint with `status: scheduled` at `2026-10-26T00:53:32Z`; the public lobby's own filter header reads "All tiers (81)" and "This week 19 matches this week" (read independently at `2026-10-26T01:2xZ` via `play.hotspawn.com/cs2-pickems?_cb=5bf1c3eb-verify`). The collector's three-view cross-check agrees: `coverage_counts {api: 81, page: 81, lobby: 81, retained: 81}`, `fixture_conflicts: 0`. |
| A pick for every match | **19 of 19 open rows carry a pick and a two-way win probability; 0 open rows are unresolved.** Verified both from the runner snapshot and, fixture by fixture, against the lobby's own 19 rendered matches (8 "Closing Soon" + 11 "Upcoming"): the id sets are identical in both directions. |
| Picks for matches no betting site covers | 10 of the 19 are priced **without** a featured exchange line: 7 from our labelled Valve-VRS model line, 2 from the same model fed by HLTV's dated Valve ranking mirror, 1 from a researched bookmaker listing. The ladder that produces them (HLTV identity → Pinnacle → wide exchange → researched listing → VRS model → HLTV mirror → research ranks → recent form) is unchanged and re-ran green on this capture. |
| Separate section for the matches that cannot have a pick | Added: `#closed-windows` on the executive summary page and on the unresolved page, linked from the always-visible executive bar, the executive banner and the unresolved section. 62 rows, each with its own `lock_time`, scheduled start, limitation and official source link. |

## 2. The 62 rows with no pick are not unresolved research

Every one of the 62 pick-less rows has a Hotspawn `lock_time` earlier than the snapshot's observation clock, so
the pick window is closed **on the source itself**. Publishing a percentage for them would be an invented
recommendation, so the board publishes the rule and the evidence instead:

* 62 rows, scheduled `2026-06-26` to `2026-10-25` UTC, each retained with its own `lock_time`
  (`lock = start − 360 s` on every row of this feed).
* **50 of the 62 carry an upstream data conflict**: the endpoint returns `status: "scheduled"` beside an
  `end_time` in the past. Example, fixture `1052746` Fortress v Endless Journey: `scheduled_start_time`
  `2026-06-26T10:30:00Z`, `start_time` `2026-06-26T11:45:27Z`, `end_time` `2026-06-26T12:51:00Z`,
  `status "scheduled"`, observed `2026-10-26T00:53:32Z`.
* The feed also returns `participants*_picked_percent` (Hotspawn's crowd split) for many of these rows. The
  brief forbids Hotspawn as a probability source, so those numbers are never converted into a pick or a
  percentage; the register states that explicitly.
* Flagged, not repaired: `review.html#session-5bf1c3eb-hotspawn-stale-scheduled-2026-10-26`.

Per-row evidence: `gaps/gap-report.json` → `closed_rows_that_cannot_take_a_pick` (derived only from the
snapshot's retained `fixture_evidence`, reproducible offline).

## 3. Per-row line-source receipts for the non-featured picks

`gaps/gap-report.json` (run 40254113329, probed `2026-10-26T01:28:55Z`) re-reads, for each of the 10 open rows
whose published line is **not** a featured exchange line, the outside sources the brief names, in order. Every
response is retained with its HTTP status and read time:

| Source | Measured at 01:28Z | Result for the 10 non-market rows |
| --- | --- | --- |
| HLTV search per club | HTTP 200 | Every club resolves to exactly one HLTV team page (identity confirmed); HLTV renders no numeric two-way price to this collector, consistent with the dated 25 Oct re-check on the method page. |
| BO3.gg upcoming feed (Thunderpick odds) | HTTP 200 · 221 rows | Loose token-overlap candidates exist for 9 of 10 rows, but **none names the exact opponent pair at the exact UTC start with an active two-way price**; the 4 "with odds" candidates are different fixtures (e.g. `ECSTATIC vs MASONIC`, `Luminosity vs HOTU`) that share one token. None passed the pipeline's exact identity+start gate, which is why these rows carry the model line. |
| EGamersWorld bookmaker-average listing | **HTTP 403** | Access refused, recorded as a limitation (matches the dated 2026-10-25 access probe). No price inferred from a refusal. |
| Polymarket public event search per club | HTTP 200 · 491 sport entries | **0 events whose title contains both clubs** for all 10 rows — i.e. these fixtures are genuinely not covered on Polymarket, the case the brief describes. |
| Pinnacle guest esports endpoints | HTTP 200 · 26 CS2 matchups / 1070 moneyline rows | Using the pipeline's own matcher (`scripts.core.pinnacle_candidates`), **0 two-way moneylines for the exact pair** on all 10 rows. An earlier draft of this probe used a looser name search and produced a misleading "Spirit" ~ "Spirit Academy" hit; that matcher was replaced and the receipts re-taken in this run. |

Conclusion recorded per row: the model label (`model_vrs` / `model_vrs_mirror`) on these 10 rows is honest — the
exchange, the sharp book, the affiliate feed and the book listing were each asked for that exact fixture in the
same minute and none supplied a usable two-way price. Valve's official standings supplied the line instead, and
the row says so.

## 4. Site changes (all rendered from the snapshot, no hand-typed counts)

* `scripts/summary.py::closed_register` / `closed_sentence` — the third register as a pure function of one
  snapshot: id, teams, competition, tier, scheduled start, lock, feed status, feed start/end, the upstream
  conflict flag and the per-row limitation sentence.
* `scripts/build.py::closed_windows_section` — the section itself: headline counts, the limitations list, the
  folded 62-row table (official Hotspawn link + feed link + evidence anchor per row) and links to
  `matches.html?status=not_open`, the standing coverage rules and the unresolved queue. Rendered on
  `index.html` (inside the executive summary) and `unresolved.html`.
* Executive-summary routes added: `#closed-windows` in the always-visible executive bar, the executive banner
  button row, and the unresolved section's footer. The pinned four-link `.exec-summary-links` nav
  (session 7ec4608a) is deliberately untouched, so the summary keeps exactly one set of focused destinations.
* Phone geometry is unchanged: the section is inserted **after** the pick list and the unresolved section, so
  nothing above the first pick card moved. Measured by `tests/browser_9b97d585.cjs` on the rebuilt board:
  first-screen summary y=363 at 320x568 (identical to the pre-change baseline), no horizontal overflow at
  320/390/768/1440, axe wcag2a/aa/21aa clean on all 8 pages × 4 widths.

## 5. Gates on this tree

`python -m unittest discover -s tests` → 1788 tests OK (14 skipped, incl. the 10 new
`tests/test_session_5bf1c3eb.py` regressions) · `audits` 9 OK · `verification-95b588c2` 5 OK ·
`verification-c6` 12 OK · `scripts.validate` RC 0 on the built site · `npm run test:browser` RC 0
(13 Chromium suites, `"failures": []`).

## 6. Irregularities flagged for manual review (non-blocking)

1. `session-5bf1c3eb-hotspawn-stale-scheduled-2026-10-26` — Hotspawn returns 50 rows with `status: "scheduled"`
   beside a past `end_time`; retained verbatim, disclosed on Flagged for Review, never repaired by inference.
2. The committed root snapshot this session started from (`generated_at 2026-10-26T00:10:49Z`, 73 rows / 11
   open) was already consistent with the live board at its own clock; the difference to this harvest
   (81 rows / 19 open) is ordinary feed rotation between refresh slots, not a defect.
