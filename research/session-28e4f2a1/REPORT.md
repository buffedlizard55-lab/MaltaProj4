# Session 28e4f2a1 — delivery report (2026-10-26)

Branch `arena/28e4f2a1-maltaproj4`, from `main` @ `eca5117`. Owner: session `28e4f2a1`.
Snapshot audited throughout: `data/latest.json`, `generated_at` `2026-10-26T00:10:49.639616Z`,
fixtures observed `2026-10-26T00:07:16.611284Z` — **73 feed rows, 11 open, 11 picks, 11 win
probabilities, 0 unresolved**.

## 1. What changed on the site

| Change | Why | Where |
| --- | --- | --- |
| `#picks-directory`: a counts-driven table of every pick source | The summary said *how many* picks existed but never *where* they were; a phone reader had to know that market lines sit on `picks.html` and research-only rows on `unresolved.html` | `scripts/build.py` (`DIRECTORY_STEPS`, `directory_buckets`, `pick_directory`), inside `#unresolved-limits` on the home page and at the top of `unresolved.html` |
| One row per published ladder step, **including zeros**, plus a "no pick" row and a total | A tier that answered for nothing must print 0, not disappear — that is how coverage drifts silently | same |
| Each row links the **official source** of that kind of line and the **page on this site** that lists those picks | Every claim on this project carries a source link; the user's requirement is to find the picks, not to trust a sentence | same |
| An unclassified `method` is counted under "no pick" **and named** | A new tier must never be folded into a known one | `pick_directory` |
| `#exec-summary` gains a "Picks by category ↓" link | One tap from the desktop summary bar to the directory | `exec_summary_bar` |
| `unresolved.html` gains the directory plus a "Jump to the match rows ↓" link to `#unresolved-rows` | The page repeats the explanation, so it must offer a way past it | `unresolved_page` (extracted from `build()` so the page can be rendered in tests) |
| HLTV limitation stated in the directory, with links | "Try HLTV, then esportsbooks" is the ladder; HLTV supplies identity/rankings but **no numeric two-way line** to this collector, and its vote is never a probability | same |
| Phone rules for the directory | 9 rows × 5 cells must stay readable at 320 px without hiding a count | `assets/style.css` + `site/assets/style.css` (byte-identical copies) |
| `tests/test_session_28e4f2a1.py` (22 tests) and `tests/browser_28e4f2a1.cjs` (3 viewports × 2 pages) | Regressions for the above, measured rather than asserted | new files; registered in `package.json` |
| Committed root manifest `assets/style.css` checksum refreshed | The committed root fallback and its manifest must describe the bytes that ship (sessions 35c6e1e9 / dddcb90d / 9fca16ca pin this) | `build-info.json` (one hash) |

Nothing in `data/latest.json`, the picks, the probabilities or the ladder policy was changed by this
session. The directory **reports** what the snapshot already decided.

## 2. Line-by-line verification of every open row

Each row was re-derived from its own stored raw bytes by two runners that do **not** import
`scripts/` (so a production bug cannot make them pass):

* `python3 research/session-28e4f2a1/verify_lines.py` → `line-receipt.json` — 11 rows, **125 checks, 0 failures**.
  De-vig arithmetic, two-sided/funding/freshness gates, overround band, fair-odds reciprocity,
  pick = strictly higher side, and — for Polymarket rows — the market's own `gameStartTime`
  equal to the fixture's UTC start.
* `python3 research/session-28e4f2a1/verify_model.py` → `model-receipt.json` — 10 model-derived rows,
  **10 reproduced to < 1e-12, 0 problems**, with every points value located in Valve's official file.

| # | Fixture (Hotspawn id) | Match | Start (UTC) | Pick | Published probability | Line source | Re-derived |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [1082858](https://gamma-api.polymarket.com/markets/6066508) | Ground Zero vs Off Chops — DFRAG Invitational 2026 | 2026-10-26T03:00:00Z | **Off Chops** | 19.00% / 81.00% | Polymarket exchange (Gamma API) | 14/14 checks, pass + model reproduced |
| 2 | [1082859](https://api.bo3.gg/api/v1/matches?page[offset]=0&page[limit]=100&filter[matches.status][in]=upcoming&filter[matches.discipline_id][eq]=1&sort=start_date&with=teams,tournament) | NEXVOID vs Alter Ego — DFRAG Invitational 2026 | 2026-10-26T03:00:00Z | **NEXVOID** | 57.52% / 42.48% | BO3.gg / Thunderpick listing | 9/9 checks, pass + model reproduced |
| 3 | [1093218](https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | Nuclear TigeRES vs UNiTY — NODWIN Clutch Series #13 | 2026-10-26T18:00:00Z | **Nuclear TigeRES** | 66.50% / 33.50% | Valve official standings (our model) | 6/6 checks, pass + model reproduced |
| 4 | [1082860](https://gamma-api.polymarket.com/markets/6066520) | FlyQuest vs Staqued — DFRAG Invitational 2026 | 2026-10-27T03:00:00Z | **FlyQuest** | 92.50% / 7.50% | Polymarket exchange (Gamma API) | 14/14 checks, pass |
| 5 | [1082861](https://gamma-api.polymarket.com/markets/6066525) | Rooster vs Abyssal — DFRAG Invitational 2026 | 2026-10-27T03:00:00Z | **Abyssal** | 42.50% / 57.50% | Polymarket exchange (Gamma API) | 14/14 checks, pass + model reproduced |
| 6 | [1082897](https://gamma-api.polymarket.com/markets/6024944) | B8 vs K27 — Tesla Cup 2026 | 2026-10-27T08:00:00Z | **B8** | 59.50% / 40.50% | Polymarket exchange (Gamma API) | 14/14 checks, pass + model reproduced |
| 7 | [1082898](https://gamma-api.polymarket.com/markets/6024952) | Alliance vs FaZe — Tesla Cup 2026 | 2026-10-27T11:00:00Z | **FaZe** | 37.50% / 62.50% | Polymarket exchange (Gamma API) | 14/14 checks, pass + model reproduced |
| 8 | [1082900](https://gamma-api.polymarket.com/markets/6024960) | Luminosity vs HOTU — Tesla Cup 2026 | 2026-10-27T17:00:00Z | **Luminosity** | 52.50% / 47.50% | Polymarket exchange (Gamma API) | 14/14 checks, pass + model reproduced |
| 9 | [1082901](https://gamma-api.polymarket.com/markets/6037120) | Envy vs GamerLegion — Tesla Cup 2026 | 2026-10-27T20:00:00Z | **GamerLegion** | 45.50% / 54.50% | Polymarket exchange (Gamma API) | 14/14 checks, pass + model reproduced |
| 10 | [1082792](https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | HOTU vs The Huns — Moscow Cyber Games 2026 | 2026-10-31T09:00:00Z | **HOTU** | 85.18% / 14.82% | Valve official standings (our model) | 6/6 checks, pass + model reproduced |
| 11 | [1082793](https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | 5star vs 1WIN — Moscow Cyber Games 2026 | 2026-10-31T13:00:00Z | **1WIN** | 24.30% / 75.70% | Valve official standings (our model) | 6/6 checks, pass + model reproduced |

Rows 1–2 and 4–9 verify against Polymarket market records and the BO3.gg/Thunderpick line stored on
the row; rows 3, 10 and 11 are our own originated lines and verify against Valve's official bytes.

## 3. The model, re-checked against Valve's own code and data

| Claim | Official source | Result |
| --- | --- | --- |
| The model's input file is the official one | [standings_global_2026_10_05.md at commit `eec4853`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | byte-identical to `data/vrs/standings_global_2026_10_05.md`, sha256 `df96e7fc3cd91a2687ec08cac0128e50cc4e4e55346581679572e881d79ae61b`, 77,872 bytes; the retained copy is `valve-live-2026-10-05.md` |
| Expected-win form | [`model/fit.js`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/fit.js) `priorWinExpectation`, `defaultGlickoParams.rd = 75`; [`model/glicko.js`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/glicko.js) `g()`/`ev()` | Glicko expected score at fixed RD 75, `Q = ln(10)/400`, reproduced independently |
| Calibration slope 0.7986 | [`modelfit.png`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/modelfit.png) — chart label `y = 0.7986x + 0.126`; [readme](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/readme.md) | the label was read off the chart image itself, not assumed |
| Roster continuity rule (3 players) | [`model/team.js`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/team.js) `TEAM_OVERLAP_TO_SHARE_ROSTER = 3` | applied to the repeated `The Huns` label: #122 = 4 shared players, #213 = 2 → #122 chosen uniquely (not by rank) |
| Alias `Envy` → `3DMAX` | [HLTV 2399870](https://www.hltv.org/matches/2399870/envy-vs-gamerlegion-rlg-tesla-cup-2026), [HLTV news 45594](https://www.hltv.org/news/45594/envy-return-to-cs-with-ex-3dmax-roster) | the registered rename is what lets the model read Envy's own standings row (`3DMAX`, 1500 pts) |
| Alias `Off Chops` → `THUNDER dOWNUNDER` | [Liquipedia Logitech G Pro Series 2026](https://liquipedia.net/counterstrike/Logitech_G_Pro_Series/2026), [HLTV team 14095](https://www.hltv.org/team/14095/off-chops) | registered rename, roster-overlap confirmed |

## 4. Live counter-checks (dated, so the next session can re-run them)

| Read at | Source | What it showed | Consequence |
| --- | --- | --- | --- |
| 2026-10-26 ~00:47Z | [`markets?id=6066508`](https://gamma-api.polymarket.com/markets?id=6066508&limit=1) | Ground Zero vs Off Chops: `outcomePrices` 0.205 / 0.795, `gameStartTime` `2026-10-26 03:00:00+00`, liquidity $10,419.86, accepting orders; the snapshot recorded 0.19 / 0.81 at 00:06Z | the market is live and the start matches; the price moved within the hour, which is why every percentage carries its own observation and expiry |
| 2026-10-26 ~00:47Z | [`markets?id=6186061`](https://gamma-api.polymarket.com/markets?id=6186061&limit=1) | Nuclear TigeRES vs UNiTY: 0.605 / 0.395, liquidity $6,140.85, `gameStartTime` **15:00Z** while Hotspawn's feed and the row's HLTV fixture say **18:00Z** | the exact-UTC-start gate refuses the price; the row keeps our labelled model line (66.50%) and the conflict is flagged — see review note `session-28e4f2a1-fixture-1093218-start-conflict-2026-10-26` |
| 2026-10-26 ~00:57Z | [Hotspawn CS2 lobby](https://play.hotspawn.com/cs2-pickems) | "Tier / Tournament / Team — All (72)", 10 rendered open pick cards, `NODWIN Clutch Series #13 (1)` in the tournament filter | coverage is driven by the fixtures API (11 open rows); the lobby surface did not render fixture 1093218 among its cards at read time. Recorded, not acted on; no value inferred |

## 5. Measurements (not claims)

`research/session-28e4f2a1/phone-directory-measurements.json`, produced by
`node tests/browser_28e4f2a1.cjs` against the generated `public/` artifact:

| Viewport | Page | Horizontal overflow | Category rows | Counts sum to total | First count hidden by the tab bar |
| --- | --- | --- | --- | --- | --- |
| 320×568 (iPhone SE) | index | none | 9 (8 categories + total) | 11 = 11 | no |
| 320×568 | unresolved | none | 9 | 11 = 11 | no |
| 390×844 (iPhone 14) | index | none | 9 | 11 = 11 | no |
| 390×844 | unresolved | none | 9 | 11 = 11 | no |
| 412×915 (Pixel 7) | index | none | 9 | 11 = 11 | no |
| 412×915 | unresolved | none | 9 | 11 = 11 | no |

At 390 px the directory is 2,352 px tall (nine cards of ~196–221 px), which is why the unresolved page
carries its own "Jump to the match rows ↓" link.

## 6. Commands (re-runnable)

```bash
python3 research/session-28e4f2a1/verify_lines.py     # 125 checks, 0 failures
python3 research/session-28e4f2a1/verify_model.py     # 10/10 reproduced, 0 problems
python3 -m scripts.build --data data/latest.json      # 9 primary pages + 6 legacy redirects
python3 -m scripts.validate --data data/latest.json --site .
python3 -m unittest discover -s tests                 # 1,800 tests
node tests/browser_28e4f2a1.cjs                       # 3 viewports x 2 pages
```

## 7. Irregularities flagged for review (none block publication)

1. **Fixture 1093218 start conflict** — Hotspawn feed and HLTV say 18:00Z, Polymarket's live market says
   15:00Z; the market price (60.5%) is therefore not attached and the row keeps the model line (66.5%).
   Direction agrees, magnitude differs. Note `session-28e4f2a1-fixture-1093218-start-conflict-2026-10-26`.
2. **Lobby vs API inventory surface** — the public lobby rendered 10 open cards at 00:57Z while the
   official fixtures API returns 11 open rows. The site follows the API (documented methodology); the
   discrepancy is recorded inside the same note.
3. **Directory counts are dated** — the table describes the snapshot named above it. A page served
   after its eight-hour window shows that snapshot's counts while the board withholds expired picks;
   the paragraph above the table says so. Note
   `session-28e4f2a1-executive-summary-directory-2026-10-26`.
4. **Category policy is a product decision** — Pinnacle and the researched book listing are separate
   rows; research-only and unresolved share the "no pick / no percentage" split by percentage, not by
   pick. Recorded in the same note for a reviewer to change if they disagree.

## 8. What was *not* done, and why

* **No market line was force-attached to fixture 1093218.** The gate exists to stop a price landing on
  the wrong kick-off; the conflict is published instead.
* **The committed root pages were not hand-staged.** The publisher regenerates them from this same code;
  hand-staging over a branch snapshot is the failure mode session 6d111263 documented. The one exception
  is the manifest checksum, which the repository's own suites require to match the shipped stylesheet.
* **`scripts/refresh.py`, `scripts/core.py`, `scripts/validate.py` and `.github/workflows/**` were not
  touched.** The ladder, its gates and the four-slot-per-hour schedule already deliver the 4–8 hour
  coverage promise; changing them was not needed for this brief.
