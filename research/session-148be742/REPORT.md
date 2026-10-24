# Session 148be742 — every-match pick coverage, phone-first summary, and the publish gate that was red

Written 2026-10-24. Every number below is read from a file in this repository or from a link
printed beside it. Nothing here is estimated.

## 1. Why the board was frozen before this session

`gh run list` at 05:34Z on 24 Oct 2026:

| Run | Workflow | Conclusion | Failing step |
| --- | --- | --- | --- |
| [40062143026](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40062143026) | Verify, refresh and publish CS2 Scout | `failure` (schedule) | `Unit and independent failure-mode tests` |
| [40042111432](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40042111432) | Verify, refresh and publish CS2 Scout | `failure` (schedule) | `Unit and independent failure-mode tests` |

Each failed before the refresh step, so nothing could be read from Hotspawn and nothing could be
published. The committed board was `data/latest.json` built at **2026-10-23T11:47:19Z** — 18 hours
old, longer than the 8-hour evidence window, so the live pages had withheld every pick.

Reproduced locally with `python -m unittest discover -s tests`:

```
FAIL: test_snapshot_covers_the_observed_lobby_fixtures
AssertionError: Items in the first set but not the second: '1079655', '1081148'
ERROR: test_each_observed_fixture_is_published_with_a_pick_and_an_official_link
KeyError: '1079655'
```

Both fixtures were read from the lobby at 09:44Z on 23 Oct by session `0cc1138a` and have since left
Hotspawn's feed. The suite excused a missing fixture only when `inventory_changes.removed_ids` named it,
but that field is a *delta against the previous refresh*; the committed snapshot carries
`removed_ids: []` because the drop happened between two cached snapshots. The test, not the data, was
wrong, and it blocked every publish.

**Repair** (`tests/test_session_0cc1138a.py`, additive and stricter): parity is now asserted against
`fixture_evidence` — the raw fixtures response the build was rendered from — in *both* directions
(`feed - board == board - feed == {}`), and the pinned 09:44Z lobby set is excused only for fixtures the
feed no longer returns. `tests/test_session_148be742.py::FeedParity` pins it, including a case where
`removed_ids` is empty.

## 2. The fresh, independent capture this session used

My sandbox has no egress to `play.hotspawn.com`, `hltv.org` or the editors' APIs (measured:
`curl https://play.hotspawn.com/lobby` → `SSL_ERROR_SYSCALL`), and `workflow_dispatch` is refused for
this repository token (`HTTP 403 Resource not accessible by integration`). So the source read runs on
the runner, from a branch-scoped harness that only reads sources and commits its own snapshot:
[`.github/workflows/harvest-148be742.yml`](../.github/workflows/harvest-148be742.yml),
run [40066630014](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40066630014) → **success**.

| Field | Value |
| --- | --- |
| Snapshot generated | `2026-10-24T05:59:34.228578Z` (the capture this branch ships, produced by `main`'s pipeline) |
| Fixture evidence observed | `2026-10-24T05:55:58.459230Z` |
| Feed rows | 88 |
| Open CS2 matches | **25** |
| Open with a pick | **25** |
| Open with a win probability | **25** |
| Research-only (pick, no %) | 0 |
| Unresolved (no pick) | **0** |
| Fixture conflicts | 0 |

Every figure in this table is re-read from the committed `data/latest.json` after the merge; the
five-fixture method mix below is identical in both captures.

Method mix of the 25 open rows: 12 `exchange`, 7 `model_vrs`, 2 `exchange_wide`, 2 `model_vrs_mirror`,
2 `bookmaker_fallback`. Evidence providers: Polymarket 14, Valve VRS 7, HLTV Valve ranking (Valve points)
2, Thunderpick via BO3.gg API 2.

**Second, independent capture (cross-check).** The harness run above produced its own capture eleven
minutes later, committed as [`snapshot.json`](snapshot.json) —
`generated_at 2026-10-24T05:44:31.614923Z`, `fixtures_observed_at 2026-10-24T05:40:50.615207Z`,
coverage `verified` at 88/88/88/88. Compared field by field with the capture this branch ships:

* identical fixture set — 88 feed records, 25 open matches, in both;
* identical pick on all 25 rows;
* four exchange mids moved between the two reads, as a live order book does: 1079658 `33.0 → 31.5%`,
  1079661 `62.5 → 61.0%`, 1082858 `29.0 → 28.5%`, 1082898 `34.5 → 35.0%` for the first-listed team.

Both captures therefore agree on the inventory and on every directional pick, and neither is treated as
more authoritative than its own observation timestamp says.

Independent row audit shipped with the harness capture:
[`independent-row-audit.md`](independent-row-audit.md) — 88 rows checked, 0 arithmetic/field failures.

## 3. Line-by-line verification of the published numbers

Two rows were re-read from their cited primary source and recomputed by hand.

**(a) Exchange row — fixture 1079193, FOKUS vs ex-6666, published FOKUS 78.5% / 21.5%.**
Source: <https://gamma-api.polymarket.com/markets/6065787> (read 2026-10-24).
The live market returns `"outcomes":"[\"FOKUS\", \"ex-6666\"]"`,
`"outcomePrices":"[\"0.785\", \"0.215\"]"`, `"eventStartTime":"2026-10-24T08:00:00Z"`,
`"endDate":"2026-10-24T14:00:00Z"`. The row stores the same prices, the same UTC start and the same
outcome order, so `p = x / Σx = 0.785 / 1.000` reproduces the published 78.5% exactly.

**(b) Originated model row — fixture 1081152, HAVU vs Azuolas, published HAVU 58.1571% / 41.8429%.**
Source: Valve's official standings file, at the commit the row cites —
<https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md>
(fetched byte-for-byte through `api.github.com` at 05:59Z):

```
| 124 | 937 | HAVU    | 8Juho8, Alxc, ottob, p3kko, uli |
| 140 | 863 | Azuolas | MAGILA, maty, StreakN, Uzman, yakuza |
```

Recomputation with Valve's own published formula (`model/fit.js` prior expectation at fixed rating
deviation 75, and the `modelfit.png` calibration `observed = 0.7986 × expected + 0.126`):

```
G = 1/√(1 + 3q²RD²/π²),  q = ln10/400,  RD = 75
E = 1/(1 + 10^(−G·(937−863)/400)) = 0.602143
calibrated = 0.5 + 0.7986·(0.602143 − 0.5) = 0.581571
```

which is the published `0.5815710671661513` to every printed digit, and `1 − p = 0.4184289` the other
side. The row's stored Valve rosters match the file's rosters for both clubs.

## 4. How a pick is produced for a match that cannot be priced like the featured picks

The ladder is unchanged in order, and every rung is recorded per row in `attempts` with its own URL.
Counts below are the recorded attempts across the 25 open rows of this snapshot.

| # | Rung | Source | Result in this snapshot |
| --- | --- | --- | --- |
| 1 | Exchange moneyline, strict gates | <https://gamma-api.polymarket.com/markets> via `/sports` + `/events` | 14 resolved (12 strict, 2 wide) |
| 2 | HLTV fixture identity, ranks, lineups | <https://www.hltv.org/matches> | 13 attempted, context only — HLTV publishes no numeric two-way line |
| 3 | Pinnacle esports moneyline | <https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight> | 13 attempted, no exact pair/start |
| 4 | Sportsbook via BO3.gg public API (Thunderpick lines) | <https://api.bo3.gg/api/v1/matches> | 2 resolved, 9 listed without an active moneyline |
| 5 | Thunderpick HTML / GG.BET HTML | <https://thunderpick.io/esports/cs2-betting>, <https://gg.bet/en/esports/counter-strike> | GG.BET `HTTP 403` on 11 rows (recorded, never bypassed) |
| 6 | Our own line — Valve VRS points + Valve's formula | Valve's file (7 rows), HLTV's dated Valve ranking (2 rows) | 9 resolved, all labelled “originated line, not a market price” |
| 7 | Research pick, no percentage: HLTV world ranking order | <https://www.hltv.org/ranking/teams> | 0 needed at this snapshot |
| 8 | Research pick, no percentage: HLTV recent form, then lifetime head-to-head | the fixture's own HLTV match page | 0 needed at this snapshot |

**Deliberately not done:** converting an HLTV world rank into a win percentage. HLTV publishes no
calibrated rank-to-win model, so any such number would be invented rather than sourced. A row that
reaches rung 7 publishes the pick and *no* percentage, and the limitation is printed with it. This is
recorded as a review note rather than left implicit.

**Sources researched for the low-tier gap (access measured, not assumed):**

| Source | What it offers | Access |
| --- | --- | --- |
| <https://bo3.gg/matches/current> | CS2 schedule with Thunderpick moneylines (decimal, both sides) per match | readable; the machine path is the JSON API already integrated in `scripts/bo3.py` |
| <https://www.hltv.org/matches> | fixture identity, ranks, lineups, rosters, recent results | readable; used for identity and the final research rungs |
| <https://www.pinnacle.com/en/esports/counter-strike-2/matchups> | sharp two-way lines where listed | machine path is the Arcadia guest API; nothing for the low-tier fixtures in this capture |
| <https://gg.bet/en/esports/counter-strike> | bookmaker lines | **HTTP 403** from the runner, recorded per row |
| <https://thunderpick.io/esports/cs2-betting> | bookmaker lines | client-side shell; no server-rendered odds, so the BO3.gg API path is used instead |

Nothing above is treated as a probability unless the two-sided price is parseable, fresh, and bound to
the exact team pair and UTC start.

## 5. Two defects found and fixed in the site

**(a) The phone layout was trapped in a short-phone media query.** `site/assets/style.css` had a missing
`}`: the block opened at line 449 under `@media(max-width:650px) and (max-height:700px)` never closed, so
the entire phone-first treatment for the executive summary (eyebrow hidden, hero demoted, pick list
promoted, first card pulled to the top) was nested inside a *height ≤ 700 px* query and applied only to
short phones. A brace scan reports one unclosed block; Chromium confirms the effect. Measured with
Chromium before and after, on the 05:44Z build:

| Viewport | First pick card before | First pick card after |
| --- | --- | --- |
| 320 × 568 | 324 px | 324 px |
| 390 × 844 | **745 px** (below the 844 px fold) | **324 px** |
| 430 × 932 | 745 px | 324 px |
| 768 × 1024 | n/a (desktop rows) | n/a (desktop rows) |

No horizontal overflow at any of those widths. `tests/test_session_148be742.py::PhoneStylesheet` now
fails if either published copy of the stylesheet becomes unbalanced or if the summary layout is nested
under a height query again.

The same missing brace also swallowed the *next* session's fix. Session `d2a55add` added an always-visible
executive-summary bar (`#exec-summary`) and re-stated the phone ordering for "every phone height" inside a
block that itself landed inside the unclosed height query, so on a 390x844 phone the bar inherited the
catch-all `order:7` and rendered 6,951 px down the page, after every pick and both unresolved sections.
With the brace repaired and an explicit top-level ordering block at the end of the stylesheet, measured on
the merged build:

| Viewport | First pick card | Summary bar `#exec-summary` | `#unresolved-limits` |
| --- | --- | --- | --- |
| 320 × 568 | 324 px | 7,052 px | 7,283 px |
| 390 × 844 | 324 px | 6,951 px | 7,148 px |
| 430 × 932 | 324 px | 6,951 px | 7,148 px |
| 768 × 1024 | desktop rows | 491 px | 3,322 px |

The bar therefore follows the pick list on phones, exactly as its own design note intends, and the first
screen already answers "where are the picks?" — the freshness strip carries `View updated picks` and
`Unresolved` as 44 px targets, and the bottom tab bar carries `Picks` and `Unresolved` on every page.

**(b) The unresolved section read as if it had rows when it had none.** With full coverage the summary
printed “0 of the 25 open matches publish no win percentage; 0 of those have no supported pick. Each row
below states…” above an empty list. The lead now states the complete-coverage case in words, and the
follow-up sentence is only printed when rows exist.

Additionally, the freshness strip's unresolved count is now a link to the in-page
`#unresolved-limits` section, so the separate unresolved/limitations section is one tap from the first
phone screen.

## 6. Gates run on this branch (all local, same commands the workflow runs)

| Gate | Result |
| --- | --- |
| `python -m unittest discover -s tests` | **1215 tests, OK** (1 skipped) — includes 19 new tests in `tests/test_session_148be742.py` |
| `python -m unittest discover -s audits -p 'test_*.py'` | 9 tests, OK |
| `python verification-95b588c2/test_integrity.py` | 5 checks, OK |
| `python -m unittest discover -s verification-c6 -p 'test_*.py'` | 12 tests, OK |
| `python verification-c6/audit_snapshot.py data/latest.json` | 0 failures (see `independent-row-audit.md`) |
| `python -m scripts.validate --data data/latest.json` | 88 rows, 25 calculations reproduced, 15 pages, 816 links/assets, 20 checksums, 217 displayed rows |
| `python -m scripts.audit_148be742 --data data/latest.json --site .` | **PASS** — 25 open, 25 picked, 25 priced, 0 research-only, 0 unresolved |
| `npm run test:browser` | 8 suites passed (32 a11y/no-overflow scans at 320/390/768/1440, phone first-screen, expiry, freshness clock) |

`scripts/audit_148be742.py` is new and is wired into the publishing workflow, so a future snapshot that
leaves an open match unpicked, unpriced without a limitation, or missing from the pick board fails the
run instead of publishing.

## 7. Flagged for review (non-blocking, published on `review.html`)

1. **Roster continuity accepted at the minimum.** Fixture 1081152 (HAVU vs Azuolas) is priced from Valve's
   file where Azuolas' listed roster (MAGILA, maty, StreakN, Uzman, yakuza) shares only 3 of 5 players with
   the HLTV lineup used for the check (maty, yakuza, Berzius, StreakN, Sh1karee). `scripts/vrs.py`
   `ROSTER_OVERLAP = 3`, so the row passes by design; it is disclosed here for a human decision on
   whether 3/5 is the right threshold for a priced line.
2. **The blocked publish gate was invisible for 18 hours.** The watchdog's escalation path exists, but the
   failing step was a test, and the board simply went stale. Fixed at the source; the new audit adds a
   second, independent reason for a future run to stop before publishing bad data.
3. **GG.BET remains `HTTP 403`** for the runner on 11 of the 25 open rows. Recorded as a collection
   limitation; it is not evidence that no price exists.
4. **Snapshot staleness is disclosed, not hidden.** If the next scheduled run does not land inside the
   8-hour window, the pages withhold picks themselves (existing behaviour, unchanged).

## 8. Reproduction

```
pip install -r requirements.txt
python -m scripts.build --data data/latest.json
python -m scripts.validate --data data/latest.json
python -m scripts.audit_148be742 --data data/latest.json --site .
python -m unittest discover -s tests
npm ci --ignore-scripts && npm run test:browser
```
