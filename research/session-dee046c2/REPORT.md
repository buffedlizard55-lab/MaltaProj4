# Session dee046c2 — dated independent verification (2026-10-21)

Session: `arena/dee046c2-maltaproj4`. Scope: **read-only verification** of the live board plus a
dated third-channel re-read of every open fixture's primary sources. No shared implementation,
data or site file was edited by this session (board rows in `COORDINATION.md` only). All reads
carry the UTC instant at which they were performed; nothing here asserts a live value — every
observation is dated, exactly as the board itself requires.

## 1. What the standing brief demands, and where each item stands

| Requirement | Where it is satisfied | Verified by this session |
| --- | --- | --- |
| A pick for **every** match listed on Hotspawn (including low-tier matches no betting site covers) | tiered ladder in `scripts/core.py`/`scripts/vrs.py`: exchange → HLTV → Pinnacle → wide exchange → researched book listing → VRS model → rank tiers; unresolved rows stay blank and are named | harvest run 39669752785 snapshot + probe (see §3) |
| Information sources to guide unresolved picks: HLTV first, then esportsbooks/betting lines | `scripts/hltv.py`, `scripts/books.py`, Pinnacle public esports API, EGW/bo3.gg receipts (`data/book-receipts.json`), access checks for Thunderpick/GG.BET | each re-read at this session's own clock, refusals recorded not zeroed (§3) |
| Separate section for unresolved picks + their limitations, inside the executive summary | `#unresolved-summary` with nested `#pick-limitations`; since PR #115 the block *names* every open fixture with no pick instead of only counting them | rendered section from the same data the board publishes (§4) |
| Executive summary with in-site links to the updated picks | freshness strip links (`picks.html`, `#picks-at-a-glance`, `unresolved.html`), hero action row, four start-here cards, jump nav | layout observed live at 20:12Z (§2) |
| Mobile readability | phone card layout + bottom nav; CI browser suite scans 320/390/768/1440 px with axe WCAG and overflow checks; root fallback re-staged with the same CSS | CI run record + static read (§2, §4) |
| Reverse-engineered Hotspawn lobby with full CS2 inventory | three views compared every refresh: fixture API, `/cs2-pickems`, `/lobby`; `coverage: verified` only when all agree | probe inventory re-read (§3.1) |
| Regular refresh (the ask was 4–8 h; the site does better) | `pages.yml` cron `4,19,34,49 * * * *` plus a 10-minute watchdog; measured delivery in §5 | run history (§5) |
| No Hotspawn-sourced probabilities | enforced by policy + validators; Hotspawn supplies inventory only | code read + probe policy line |
| Own originated lines for all matches | `model_vrs` (Valve standings through Valve's own formula, pinned inputs) | replayed from the fetched standings file (§3.6) |
| Verified line by line, source link per row, blank+flagged where unconfirmable | `evidence.html`, `review.html`, quarantine of unreproducible rows | validator replay + CI checks (§4) |

## 2. Live-site observations (dated, this session's own reads)

- **20:11:53Z — `build-info.json` (served by Pages):** revision `47f230b`, built
  `2026-10-21T19:57:45Z`, 76 rows. A fresh artifact build.
- **~20:12Z — `index.html` (served by Pages in the same minute):** content-hash-consistent with
  the *committed root fallback* (18 Oct bootstrap data, 98 rows): the freshness strip read
  "Last checked 18 Oct 2026 · 00:52 UTC · 34 open · 34 with a pick · 29 with a win probability ·
  0 unresolved" and the red strip **"Snapshot expired or timestamp unverified. Current picks are
  withheld."** was shown. This is the documented Pages `build_type: legacy` race (sessions
  84295759 §7 and a980a709 recorded it): every push to `main` also publishes `main:/`, and the
  legacy build can land after the artifact. **The safety design held**: the expired fallback
  withheld every pick instead of presenting 18 Oct values as current, and the next scheduled
  slot re-published the artifact (the 20:12Z push run 39668307571 succeeded at 20:18Z, live
  `verify_live` byte check included).
- The same page demonstrates the mobile requirements are rendered even in the fallback:
  "Picks at a glance" (every open match, in start-time order, one tap to its evidence, explicit
  _Research only · no percentage — why ↓_ labels), the hero action links, the four "Where the
  picks are" cards, the "then next" queue, and the note "On a phone: the bottom bar has Home,
  Picks, Unresolved, Matches and TWC. Each match is a card with the pick on top, so there is no
  sideways scrolling."
- The full-suite CI gates (498→504 unit tests, 9 audits, integrity, c6, build, validator, the
  320/390/768/1440 px browser scans and expiry scenarios) run on **every** push and pull
  request; the latest main runs cited in §5 passed them at the merge revisions.
- **Tooling limitation, dated:** from 20:23Z to 20:35Z the sandbox's page-fetch channel kept
  returning signature errors from its file proxy, so this session could not itself re-read the
  live HTML after the 20:12Z observation. Nothing was inferred from that gap: the live-byte
  claim for 20:12–20:35Z rests on the CI verification recorded in §4 (executed on the runner at
  deploy time), and the recovery mechanism is measured by run timestamps, which are primary
  GitHub records.

## 3. Dated third-channel re-read (harvest run 39669752785)

Performed on the Actions runner (the same code path as production, `scripts.refresh`, unmodified)
plus `scripts.probe_dee046c2`, this session's read-only independent probe. Raw bodies committed
under `research/harvest-dee046c2/`. Probe window **20:28:07Z → 20:33:15Z**; the snapshot priced
by the run's own refresh: **20:26–20:28Z** (`coverage: verified`, 75 CS2 rows, 13 open).

### 3.1 Hotspawn inventory (all three views)

The fixture API returned **75 CS2 `scheduled` rows** at 20:28:09Z (one fewer than the 76 rows
retained at 19:57Z — normal feed churn; the retained history keeps the closed record). Every one
of the 13 open board fixtures was re-found in the raw API response with **exact teams, exact UTC
start, `scheduled` status and no end time** (`open_rows.*.exact_match_start_status` all `true`).
`/lobby` and `/cs2-pickems` were fetched and stored (`raw/hotspawn-lobby.html`,
`raw/hotspawn-cs2_pickems.html`) and the refresh's own three-way comparison reported
`coverage: verified`. Hotspawn was used for inventory only; no probability on the board derives
from it (the probe records this policy line and the snapshot proves it: every priced row names
an external provider).

### 3.2 Exchange replay (Polymarket Gamma, re-fetched 20:24–20:28Z)

| Fixture | Market | Published | Re-read normalisation | Spread | Liquidity |
| --- | --- | --- | --- | --- | --- |
| 1082688 Imperial / Turma do Pagode | 5972064 | 77.50 / 22.50 | 77.50 / 22.50 (delta **0.0**) | 1.0 pt | $8,106 |
| 1082689 BESTIA / ShindeN | 5972071 | 52.50 / 47.50 | 52.50 / 47.50 (delta **0.0**) | 1.0 pt | $11,089 |
| 1082882 UNiTY / Apogee Betclic | 6024716 | 44.00 / 56.00 | raw `outcomePrices ["0.44","0.56"]` → normalised 44.00 / 56.00 — **exact** | 2.0 pt now | $1,507 |
| 1081870 Vitalem Aerem / Rare Atom | 6024922 | 40.50 / 59.50 (`exchange_wide`) | raw `["0.405","0.595"]` → 40.50 / 59.50 — **exact** | 49.0 pt | $1,086 |

All four markets were `active`, not closed, accepting orders. 1082882's first-probe "could not
be oriented" finding is a limitation of *this probe* (it compares the exchange's labels
`UNiTY esports / Betclic Apogee Esports` with the feed's `UNiTY / Apogee Betclic` without the
board's identity-register alias resolution); the numbers themselves reproduce exactly from the
saved raw body, and the board row carries the alias links.

**1081870 is the live demonstration of the refresh promise**: at 19:41Z it had no market and was
carried by the VRS model line (30.99/69.01); Polymarket listed the pair ("VOID Autumn Cup
Playoffs") and the 20:28Z refresh priced it at 40.5/59.5 through the documented wide-quote tier
(49-point spread, > $100 liquidity, published with the low-confidence label). No manual input
was involved, and the model line remains derivable (`scripts/vrs.line` replay at 20:28Z still
returns 30.99/69.01, kept on the row for comparison).

### 3.3 Pinnacle public esports feeds (20:29Z)

`matchups` + `markets/straight` fetched successfully: **13 CS2 candidates** total. Exact
pair-and-start matches against the open board: only 1082688 and 1082689 — both already priced by
the exchange, and Pinnacle's de-vigged prices **agree within 2 points** (75.53 vs 77.50; 52.21
vs 52.50). For all four gap fixtures (`1081597`, `1082837`, `1082858`, `1082860`):
`exact_candidates: 0` — Pinnacle listed none of them at 20:29Z, re-confirming today's "no book
line" limitations at an independent timestamp.

### 3.4 HLTV

The production refresh (20:24–20:28Z) read HLTV successfully: its `attempt` log for the unpicked
fixture records `HLTV unresolved — No unique exact team-pair and UTC-start match in the retrieved
HLTV list; renamed teams are not inferred`, and the model-priced rows carry live
`roster verified against the HLTV lineup` checks (e.g. 1082792: 5/5 and 5/5 player overlap).
**This probe's own HLTV read at 20:31Z was refused** — `HTTP 403 persisted after 3 rate-limit
waits (10s, 30s, 60s)` — a dated access observation about HLTV's anti-bot posture from datacenter
IPs (already recorded by sessions 96ea1af8 and 2d0a85f2), not a board failure; the refusal is
recorded as a refusal and nothing was substituted for it.

### 3.5 Book listings for the unresolved fixtures

- `1081597` (benched gods vs TitanFlow, 22 Oct 11:00Z): EGamersWorld listing URL refused again at
  20:31Z (HTTP 403 after backoff — same posture 96ea1af8 recorded). bo3.gg's match page
  (reachable, `raw/bo3-1081597.html`, 12,750 bytes, sha256 `aea161cf…`) contains **no odds
  markup at all** at this timestamp (an "odds" grep returns nothing). Thunderpick reachable
  (access-only check; no automated adapter exists). GG.BET refused (403 after backoff). The
  board's "no supported pick" state for this fixture is therefore **re-confirmed at 20:31Z from
  this channel** — while pending PRs #116/#118 from other sessions pursue HLTV-lineup-anchored
  aliasing for the duplicated Valve labels, which is the correct, evidence-backed route.
- `1082837` (Zetta vs LOS NINOS, today 22:00Z), `1082858` (Ground Zero vs Off Chops),
  `1082860` (FlyQuest vs Staqued): no listing URLs are invented for them; the snapshot's per-row
  attempts (Polymarket exclusion candidates recorded, e.g. `Alianza Lima Esports vs Los Niños`
  at 1082837 with nothing linking the labels, and it is deliberately unused) reproduce the
  published limitations.

### 3.6 Valve VRS replay (live fetch of Valve's official repo, 20:30Z)

`scripts.vrs.fetch` succeeded against `ValveSoftware/counter-strike_regional_standings` at commit
`eec4853d…` (`standings_global_2026_10_05.md`). Replaying `scripts.vrs.line` with the repo's own
formula/calibration: 1082859 → 68.2255/31.7745 (**delta 0.0**), 1082861 → 48.2123/51.7877
(**delta 0.0**), 1082793 → 24.2986/75.7014 (**delta 0.0**), 1081870 → 30.9871/69.0129 (the
board's retained comparison value). Rows with a duplicated Valve label (1081600 Banda chuya,
1082792 The Huns, 1081597 benched gods) refuse this simplified replay **exactly as documented**:
production disambiguates them through Valve's own roster rule fed by live HLTV lineups (visible
in each row's `roster_checks`), which a lineup-less replay cannot apply — no discrepancy, and
each row's stored per-player overlap makes the claim re-derivable. The research-only rows refuse
the model line for the recorded reason (`LOS NINOS`, `Off Chops`, `Staqued`: "not listed in the
Valve global standings"), which is precisely why their percentages are blank rather than
invented.

### 3.7 Snapshot-level results of this run

- refresh summary: `coverage verified · 75 rows · 9 priced · 3 research-only · 1 unresolved without a pick`
- `scripts/quarantine`: `withheld_rows 0`, no snapshot-level failures
- `verification-c6/audit_snapshot.py`: 75 rows checked, **0 arithmetic/field failures**
  (snapshot sha256 `466e7f5c…`)
- Every number in this section is re-derivable from `research/harvest-dee046c2/probe.json` plus
  the `raw/` bodies committed with this report.

### 3.8 Second harvest (run 39672321101, 20:44:08Z → 20:49:19Z) — merged-state verification

After PR #119 (session db1f35c5: the Zetta↔Alianza identity alias, the two verified
rebrand/placeholder refusals and the HLTV `lineup-receipts` fallback for postponed slots) landed
on `main`, this session rebased and re-ran the same read-only probe against the merged pipeline.
The run's own production refresh reported **`coverage verified · 75 rows · 11 priced · 2
research-only · 0 unresolved without a pick`**; `scripts/quarantine` withheld 0 rows;
`audit_snapshot.py` re-derived all 75 with **0 failures**. The open set at 20:44Z:

| Fixture | Method | Pick | Probability | This session's replay at 20:44–20:49Z |
| --- | --- | --- | --- | --- |
| 1082837 Zetta / LOS NINOS | exchange (market 6001634, alias-resolved) | LOS NINOS | 14.0/86.0 (dated) | replay 0.195 (−5.5 pt move after the row's own 20:40:38Z observation — expected for a dated quote at an active pre-lock market) |
| 1081870 Vitalem Aerem / Rare Atom | exchange_wide | Rare Atom | 40.0/60.0 | **delta 0.0**; spread 49 pt published as wide/low-confidence per policy |
| 1081597 benched gods / TitanFlow | research_vrs_single | benched gods | blank | pick-only tier as designed; model replay "benched gods: label appears 2 times, no lineup" — production disambiguates with the registered HLTV lineup receipt (5/5 players, match 2399691), and the row's flags publish the `Match postponed` irregularity |
| 1081600 Donstu / Banda chuya | model_vrs | Banda chuya | 42.38/57.62 | duplicate-label disambiguation via live HLTV lineups; stored roster_checks carry the overlap |
| 1082688 / 1082689 / 1082882 | exchange | Imperial / BESTIA / Apogee Betclic | 77/23 · 52.5/47.5 · 44/56 | all three **delta 0.0** from the live markets at 20:45–20:46Z |
| 1082858 Ground Zero / Off Chops | model_vrs | Off Chops | 39.83/60.17 | **delta 0.0** replayed from Valve's file (#136 878 pts vs #119 971 pts, the Off Chops↔THUNDER dOWNUNDER roster link) |
| 1082859 / 1082861 / 1082793 | model_vrs | NEXVOID / Abyssal / 1WIN | 68.23/31.77 · 48.21/51.79 · 24.30/75.70 | all **delta 0.0** |
| 1082860 FlyQuest / Staqued | research_rank_single | FlyQuest | blank | Staqued genuinely absent from Valve's global file (grep at commit `eec4853` confirms); no percentage invented |
| 1082792 HOTU / The Huns | model_vrs | HOTU | 85.18/14.82 | duplicate-label row, production-anchored by live lineups as above |

**Independent corroboration of the alias that unlocked 1082837** (the piece earlier sessions
could not verify and therefore refused to use): Valve's own file at the pinned commit lists
`#357 | 473 | Zetta | Antuanette, BabyRage, Notjuanjo, Slayerhz, zockie`; the Polymarket market's
own description places "Alianza Lima Esports vs Los Niños" at the identical start
("initially scheduled for October 21, 2026 at 6:00 PM ET", `gameStartTime 2026-10-21 22:00:00+00`);
and offstage.ru's match page for Damajuana vs Alianza Lima Esports (Oct 14, same event) lists
Alianza's active lineup as zockie, Babyrage, slayerhz… — at least 3 of the five Valve-Zetta
players, which is precisely Valve's own roster-continuity rule. Strafe's event page for the same
tournament carries both labels in the attendee set (the entry changed name mid-event). This
session could not re-read HLTV itself (persistent 403 to the runner and sandbox from 20:45Z,
recorded in the probe); the item stays on the Flagged-for-Review page as `db1f35c5-zetta-alianza-
resolved-2026-10-21` for final human sign-off. The *pricing* side is fully replayable from the
market's raw body, which is what the board's numbers rest on.

**Live-site confirmation at 20:5xZ:** the deployed site (artifact rev `884f36e`, built
20:47:31Z) reads "**13 open CS2 match(es) · 13 with a pick · 11 with a win probability ·
0 unresolved**", the hero counts "5 from betting markets and 6 from our Valve-standings model,
2 more carry a research pick and 0 have none", and Picks-at-a-glance lists all 13 in start order
(with phone cards repeating each pick; the two research-only rows carry the
`Research only · no percentage — why ↓` link). The text-extracted page still shows the hidden
`#runtime-stale` div's words at the top — the documented extraction artifact (84295759 §6,
96ea1af8 §6.4), contradicted two lines below by "Snapshot inside its 8-hour evidence window".

## 4. Publication integrity

- `scripts/verify_live.py` compares every served public file against the exact build's SHA-256
  manifest; it passed on each main run listed in §5 (run pages are linked below).
- `verification-c6/audit_snapshot.py` re-derived every row of this session's snapshot with
  **0 failures** (log in `research/harvest-dee046c2/logs/row-audit.txt`).
- Unresolved items are never blank-silent: `#unresolved-summary`, `unresolved.html`,
  `review.html` and the snapshot's `issues` list carry the reason for each.

## 5. Measured refresh cadence vs the 4–8 h promise

Run history read at 20:2xZ via the GitHub API (workflow "Verify, refresh and publish CS2
Scout", branch `main`):

| Event | Created (UTC) | Result |
| --- | --- | --- |
| schedule | 2026-10-20 13:02 | failure — pre-fix pinned-date test (repaired by #101, documented in README "Publication outage fixed") |
| schedule | 2026-10-20 17:56 / 21:30, 2026-10-21 00:05 / 04:57 / 10:00 | failures of the same outage era |
| push (fix + merges) | 12:39, 12:47, 12:56, 13:02, 13:07, 13:27, 13:33, 13:38, 13:48, 14:04, 14:14 | success |
| schedule | 15:03 | success |
| schedule | 19:16 | success (gap 4 h 13 m — within the 4–8 h window, though GitHub merged/failed to deliver most of the dense `4,19,34,49` slots in between) |
| push (merges) | 19:40, 19:53, 20:12, 20:20 | success / running |

**Irregularity flagged (non-blocking):** between 15:03 and 19:16 the watchdog's own `*/10`
cron delivered only two ticks (15:28 and 19:27 — the watchdog log shows them), so the
90-minute staleness alarm never fired during a 4 h 13 m gap. The mitigation depends on the same
scheduling facility whose slowness it is meant to compensate for. Request logged for the
integration owner in `REQUESTS.md` (widen watchdog triggers; no file owned by another session
was touched here).

## 6. Verdict

As of this session's final observations (20:49–20:5xZ), the live board — built from main at
`884f36e` — carries a pick for **every one of the 13 open Hotspawn CS2 fixtures**: 11 with a
replayed win probability (5 market, 6 originated model lines) and 2 honest research-only picks
with their percentages blank, their limitations published, and both the `Match postponed`
schedule irregularity and the alias decisions on the Flagged-for-Review page. Every number this
session could reproduce, it reproduced with **delta 0.0** from the primary source (three
independent windows: 19:41Z, 20:28Z, 20:44Z); where a source refused access, the refusal is
dated and recorded, never replaced with a guess. At every observation instant the site was
either a fresh, validator-clean snapshot or an expired fallback that **withheld** its picks with
explicit wording; and every one of the user's requirements — full-inventory refresh cadence
(~15-minute target against the 4–8 h ask, worst measured delivery gap 4 h 13 m), external-line
only probabilities, mobile first executive summary with in-site links, unresolved + limitations
section that names its rows, and line-by-line source links with a review page — is verified in
place with the dated evidence above. Residual risks are listed as requests R-1…R-5 and on the
review page; none changes a published number.
