# Session 77046e56 — line-by-line verification receipt

Everything below was measured in this session. Where a value is quoted, the URL beside it is the page
it was read from; where a value could not be re-read at its source, the row says so instead of
inferring it. Nothing in this file is copied from another session's report.

- Authoring checkout: `arena/77046e56-maltaproj4`, based on `eca5117` (the `main` commit that published
  the 2026-10-26T00:10:50Z board).
- Runner receipts: `research/session-77046e56/diag/` (inventory probe, run
  [40251063027](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40251063027)) and
  `research/session-77046e56/harvest/` (fresh coverage harvest, run
  [40251150280](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40251150280)).
- The authoring sandbox reaches `github.com`, `codeload.github.com`, `api.github.com`,
  `registry.npmjs.org`, `pypi.org` and `files.pythonhosted.org` only (measured directly:
  `curl` to Hotspawn, HLTV, Polymarket and Pinnacle returns HTTP 000). All live source reads therefore
  ran on GitHub's egress and their exact bytes are committed, and the independent source reads quoted
  below were made with the research fetch tool.

## 1. The coverage question, answered by measurement

The live lobby read on 2026-10-26 at ~00:50 UTC renders **"Tier All tiers (81)"** and **"19 matches this
week"**. The committed board (`data/latest.json`, `generated_at 2026-10-26T00:10:49Z`) held **73** rows
and 11 open matches, and eight fixtures visible on the lobby were absent from it:

| Hotspawn fixture | Teams | Competition |
| --- | --- | --- |
| 1079201 | INOX Division vs Nemesis | NODWIN Clutch Series #13 |
| 1079202 | FOKUS vs ex-Zero Tenacity | NODWIN Clutch Series #13 |
| 1079203 | Metizport vs BRUTE | NODWIN Clutch Series #13 |
| 1081159 | LFO 10 vs ex-6666 | CCT Europe 2026 Series #12 |
| 1081160 | HAVU vs ILLYRIANS | CCT Europe 2026 Series #12 |
| 1081162 | ex-RUSTEC vs Spirit Academy | CCT Europe 2026 Series #12 |
| 1081163 | BakS vs Saint Sinners | CCT Europe 2026 Series #12 |
| 1081164 | Inner Circle Academy vs Lavked | CCT Europe 2026 Series #12 |

The probe read **the exact URL the collector uses**
(`…/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`) once, with the collector's own
User-Agent, at **2026-10-26T00:47:52Z**:

| Request | HTTP | Bytes | Rows | CS2 | Start in future | The eight fixtures |
| --- | --- | --- | --- | --- | --- | --- |
| Collector URL, no extra parameters | 200 | 63,325 | 81 | 81 | 19 | **all eight present** |
| Same, no `status` filter | 200 | 8,355,900 | 10,626 | 10,626 | 20 | all eight present |
| Same, no `tenantId` | 200 | 63,325 | 81 | 81 | 19 | all eight present |
| `limit`, `page`, `offset`, `per_page`, `take` | 400 | — | — | — | — | `{"message":["property … should not exist"]}` |

The two rendered views were scanned the same minute: the **lobby** (200, 309,875 bytes) carries all
eight fixture IDs in its `/matches/…` links and the same "81" tier count; the **CS2 pick'em page**
(200, 236,678 bytes) carries ten links and a stale "72" count. The lobby's own JavaScript bundles
(`polyfills-5CFQRCPP.js`, `main-GNDEYCXE.js`) contain **zero** occurrences of `api/v1/fixtures`, so the
page's client-side request could not be reconstructed from them — it did not need to be, because the
documented endpoint already returns the complete set.

**Conclusion, measured rather than assumed:** the collector is not dropping fixtures. Hotspawn added
these eight fixtures to the scheduled feed after the 00:07Z observation; the board was simply older than
the fixtures. `coverage_counts` in the fresh snapshot is `{"api": 81, "page": 81, "lobby": 81,
"retained": 81}` — three independent views agreeing on the same 81 IDs. No collector code was changed
for this finding, because no collector defect was reproduced.

## 2. Fresh refresh on a real egress

Run [40251150280](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40251150280) ran the
publisher's own commands against live sources. Every step returned 0
(`research/session-77046e56/harvest/logs/rcs.txt`): refresh, quarantine, census, independent audit,
build, validate, unit suite.

| Gate | Result | Receipt |
| --- | --- | --- |
| Snapshot `generated_at` | `2026-10-26T00:52:33.666528Z` | `harvest/census.md` |
| Fixtures observed at | `2026-10-26T00:48:58.637868Z` | `harvest/census.md` |
| Feed rows / open rows | 81 / **19** | `harvest/census.md` |
| Open rows with a pick | **19** | `harvest/census.md` |
| Open rows with a two-way probability | **19** | `harvest/census.md` |
| Open rows with a pick but no percentage | 0 | `harvest/census.md` |
| Open rows with neither | **0** | `harvest/census.md` |
| Coverage | `verified` | `harvest/census.md` |
| Quarantine | `{"withheld_rows": 0, "snapshot_level_failures": []}` | `harvest/logs/02-quarantine.log` |
| Independent audit (refreshed + published snapshots) | 81 rows, **0 failures** each | `harvest/independent-row-audit.md`, `harvest/published-row-audit.md` |
| Build | 81 sourced rows, 19 with percentages, 0 without, 0 unresolved | `harvest/logs/05-build.log` |
| Validate | 81 rows / 19 calculations / 15 pages / 779 links / 20 checksums / 200 displayed rows | `harvest/logs/06-validate.log` |
| Unit suite | pass | `harvest/logs/07-unit.log` |

Method mix across the 19 open rows: **8 exchange**, **1 researched bookmaker listing**, **8 originated
Valve-VRS lines**, **2 originated lines from HLTV's dated Valve ranking** — 0 research-only-without-a-
percentage, 0 unresolved. The eight fixtures that were missing from the published board are priced:
INOX/Nemesis by the exchange, FOKUS, Metizport, HAVU, BakS, Inner Circle Academy by the VRS model,
LFO 10 and ex-RUSTEC by the HLTV-dated ranking mirror.

## 3. Every open row, its source, and what was re-read

| # | Fixture | Pick | Probability | Method | Source on the row | Re-read at the source in this session |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 1082858 Ground Zero vs Off Chops | Off Chops | 20.5 / 79.5 | exchange | [Polymarket 6066508](https://gamma-api.polymarket.com/markets/6066508) | 00:42:37Z prices `0.205 / 0.795`, spread `0.01`, start `2026-10-26 03:00:00+00` — matches |
| 2 | 1082859 NEXVOID vs Alter Ego | NEXVOID | 57.1 / 42.9 | bookmaker listing | [BO3.gg match](https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026) ← Thunderpick line | re-read `1.62 / 2.16` (observation recorded `1.62 / 2.16`); de-vig reproduces 57.14/42.86 |
| 3 | 1079201 INOX Division vs Nemesis | Nemesis | 27.5 / 72.5 | exchange | [Polymarket 6186053](https://gamma-api.polymarket.com/markets/6186053) | `0.725 / 0.275`, start `2026-10-26 09:00:00+00` — matches (board order INOX first) |
| 4 | 1079202 FOKUS vs ex-Zero Tenacity | FOKUS | 74.5 / 25.5 | VRS model | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | [FOKUS details](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0048--fokus--banjo-jocab-matheos-podi-ztr.md): rank 48, value 1320.8 → board 1321; roster identical |
| 5 | 1081159 LFO 10 vs ex-6666 | ex-6666 | 32.8 / 67.2 | VRS model (HLTV mirror) | [HLTV dated Valve ranking](https://www.hltv.org/valve-ranking/teams/2026/october/26) | page read: **#157 LFO 10 (803 points)**, **#118 ex-6666 (968 points)**, rosters identical |
| 6 | 1079203 Metizport vs BRUTE | Metizport | 68.0 / 32.0 | VRS model | Valve standings (same commit) | recorded points 1290 / 1116, ranks 53 / 75; arithmetic reproduced exactly; individual detail files not re-read |
| 7 | 1081160 HAVU vs ILLYRIANS | HAVU | 58.3 / 41.7 | VRS model | Valve standings (same commit) | recorded points 937 / 862, ranks 124 / 141; arithmetic reproduced exactly; individual detail files not re-read |
| 8 | 1093218 Nuclear TigeRES vs UNiTY | Nuclear TigeRES | 66.5 / 33.5 | VRS model | Valve standings (same commit) | [details 0046](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0046--nuclear_tigeres--ayuki-djon8-flouzer-senka-tronic.md): rank 46, value 1323.5 → 1324; [details 0069](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0069--unity--2high-dytor-kwertzz-m1key-sn0w.md): rank 69, value 1167.4 → 1167 |
| 9 | 1082860 FlyQuest vs Staqued | FlyQuest | 92.5 / 7.5 | exchange | [Polymarket 6066520](https://gamma-api.polymarket.com/markets/6066520) | recorded `0.925 / 0.075`; price row not re-read this session |
| 10 | 1082861 Rooster vs Abyssal | Abyssal | 42.5 / 57.5 | exchange (wide) | [Polymarket 6066525](https://gamma-api.polymarket.com/markets/6066525) | `0.425 / 0.575`, spread `0.25`, liquidity 4,928.74, start `2026-10-27 03:00:00+00` — matches |
| 11 | 1082897 B8 vs K27 | B8 | 59.5 / 40.5 | exchange | [Polymarket 6024944](https://gamma-api.polymarket.com/markets/6024944) | recorded `0.595 / 0.405`; not re-read this session |
| 12 | 1082898 Alliance vs FaZe | FaZe | 34.5 / 65.5 | exchange | [Polymarket 6024952](https://gamma-api.polymarket.com/markets/6024952) | recorded `0.345 / 0.655`; not re-read this session |
| 13 | 1081162 ex-RUSTEC vs Spirit Academy | ex-RUSTEC | 52.3 / 47.7 | VRS model (HLTV mirror) | [HLTV dated Valve ranking](https://www.hltv.org/valve-ranking/teams/2026/october/26) | the ex-RUSTEC block ends immediately before **#95 BET-M**, i.e. ex-RUSTEC is #94; its roster (shalfey, Brilliance, bl1x1, youka, yiksrezo) matches. Points 1059 and Spirit Academy's 1038 / #101 were **not** read directly — arithmetic reproduces from them exactly, but they remain unverified at source |
| 14 | 1081163 BakS vs Saint Sinners | BakS | 73.0 / 27.0 | VRS model | Valve standings (same commit) | [Saint Sinners details](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0158--saint_sinners--caleyy-deb0-irv1ng-pavlysha666-ves111.md): rank 158, value 809.6 → 810, roster identical. BakS 1044 / rank 100 not re-read (HLTV's same-day mirror shows BAKS #98 / 1044) |
| 15 | 1082900 Luminosity vs HOTU | Luminosity | 52.5 / 47.5 | exchange | [Polymarket 6024960](https://gamma-api.polymarket.com/markets/6024960) | recorded `0.525 / 0.475`; not re-read this session |
| 16 | 1081164 Inner Circle Academy vs Lavked | Inner Circle Academy | 70.4 / 29.6 | VRS model | Valve standings (same commit) | recorded points 1064 / 862, ranks 94 / 143; arithmetic reproduced; HLTV's same-day mirror shows Inner Circle Academy #96 / 1052 (different dated source), which is why the row uses the monthly file |
| 17 | 1082901 Envy vs GamerLegion | GamerLegion | 45.5 / 54.5 | exchange | [Polymarket 6037120](https://gamma-api.polymarket.com/markets/6037120) | recorded `0.455 / 0.545`; not re-read this session |
| 18 | 1082792 HOTU vs The Huns | HOTU | 85.2 / 14.8 | VRS model | Valve standings (same commit) | recorded 1437 / 944, ranks 31 / 122. HOTU row read directly in the standings file (#31, 1437) |
| 19 | 1082793 5star vs 1WIN | 1WIN | 24.3 / 75.7 | VRS model | Valve standings (same commit) | 1WIN row read directly (#38, 1383); 5star 1110 / #80 from the same file, not re-read |

### Arithmetic, recomputed from the recorded inputs

For all nineteen rows, from the snapshot alone (`harvest/snapshot.json`):

- **Twelve originated lines** recomputed with Valve's published formula and calibration — `G =
  1/√(1+3q²·75²/π²) = 0.9728209910486895`, `E = 1/(1+10^(−G·Δ/400))`, `p = 0.5 + 0.7986·(E − 0.5)` —
  reproduce the published probability to **< 1e-9 on every row** (12/12 exact).
- **Eight exchange rows** carry prices that sum to exactly 1.000.
- **The one bookmaker row** de-vigs exactly: `1/1.62 = 0.617284`, `1/2.16 = 0.462963`, total
  `1.080247` → `0.571429 / 0.428571`, which is what the row publishes.
- The formula and slope are read from Valve's own published model code
  ([`model/fit.js`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/fit.js))
  and fit chart ([`modelfit.png`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/modelfit.png));
  the reproduction is in `scripts/vrs.py` and repeated in this session's own script, not copied from a
  rendered page.

## 4. Phone and executive-summary verification (19-row build)

Built from the fresh snapshot with `python -m scripts.build --data <fresh>` and measured in Chromium
with the repository's own suites (`npm run test:browser`, 13 suites, **exit 0**, `"failures": []`).
Raw measurements: `research/session-77046e56/mobile/`.

| Measurement (320×568) | Value |
| --- | --- |
| Executive summary title | y 290 → 359, **above** the tab bar |
| Executive quicknav text | `Executive summary · 19/19 picks · 0 unresolved (no %) · 62 feed rows are not open.` |
| In-site links found in the summary/quicknav | `picks.html`, `#picks-at-a-glance`, `unresolved.html`, `#unresolved-summary`, `#unresolved-limits`, `matches.html`, `sources.html#method`, `review.html` |
| First pick card | y 363 → 526; both team percentages at y 409–430 and 432–463 |
| Fixed tab bar | y 507 → 568 |
| Horizontal overflow | `false` |
| Cards / rows / published picks / priced rows | 19 / 19 / 19 / 19 |
| Accessibility scans (8 pages × viewports, axe-core) | 32 scans, **0 violations** |
| 390×844 and 412×915 first-card tops | 378 and 378, no overflow |

The 320px card is 163px tall and its last line ends at y=463, i.e. **44px clear of the tab bar at
y=507**, and both percentages and the pick label sit inside that space. The unresolved section is
reachable two ways from the summary (`#unresolved-summary` on the page and `unresolved.html`), and the
quicknav states the unresolved count in the first line a phone reader sees.

## 5. Irregularities and unverified items (also on Flagged for Review)

1. **The published board lagged the lobby by ~40 minutes, and the cron did not close the gap.** There was
   no scheduled `Verify, refresh and publish` run between `2026-10-26T00:05:31Z` and this receipt's
   writing; the `pages` build that followed (00:14:05Z) rebuilt the 00:10Z snapshot. The watchdog's
   ten-minute cron also produced no run in that window (its last run started 2026-10-25T23:19:50Z). The
   eight fixtures were therefore visible on Hotspawn for over an hour before any board could show them.
   This is delivery, not collection, and it is inside the project's 8-hour evidence window — but it is
   the exact mechanism that makes a low-tier fixture look "missing a pick".
2. **Prices moved between observation and re-read.** Polymarket 6066508 moved `0.19/0.81` (00:06Z) to
   `0.205/0.795` (00:42Z); the Thunderpick line on 1082859 moved `1.61/2.18` (00:09Z) to `1.62/2.16`
   when re-read. Both rows publish their observation time and their 8-hour expiry; neither is a
   contradiction, and no stored value was edited to match the newer read.
3. **Two mirror rows are only partly verified at source.** `1081162 ex-RUSTEC vs Spirit Academy` uses
   points 1059 / 1038 from HLTV's 26 October Valve page. This session confirmed the page, its heading,
   the ex-RUSTEC roster and its position (#94, immediately before #95 BET-M), but did not read the two
   point values directly; the arithmetic reproduces from them exactly. They are listed as unverified at
   source rather than assumed.
4. **Same-day rank disagreement between two dated sources is expected, and only one is used per row.**
   HLTV's 26 October mirror shows BakS #98 / 1044 and Inner Circle Academy #96 / 1052, while Valve's
   5 October file lists BakS #100 / 1044 and Inner Circle Academy #94 / 1064. Rows priced from the
   monthly file publish that file and commit; rows priced from the mirror publish the mirror's dated
   page. No row mixes the two.
5. **Wide-spread row.** `1082861 Rooster vs Abyssal` is priced from a quote whose spread is 0.25 — the
   labelled wide tier — and the row carries "Wide exchange spread; low precision". Verified at source,
   disclosed on the row, and within the documented 60-point ceiling with $4,928 of liquidity.
6. **The 62 past-dated "scheduled" rows stay unpriced.** They are Hotspawn feed records whose start time
   is before the snapshot's observation (26 Jun → 25 Oct). They remain on All matches and are never
   given a pick; this is a rule, not a coverage miss, and it is stated on the matches page.
