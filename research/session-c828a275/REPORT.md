# Session c828a275 — independent audit of the published CS2 board (22 October 2026)

Branch `arena/c828a275-maltaproj4`, from `main` at `40e1fab` (PR #138); rebased over PRs #142/#143/#149, which
moved the committed snapshot from 2026-10-21T21:27Z (75 rows, 13 open) to 2026-10-22T01:28Z (97 rows, 35 open).
**Both snapshots are audited below** — the auditor was re-run on the newer board when the rebase brought it in,
because a table of numbers that silently describes a board the repository no longer ships is exactly the kind of
stale claim this project keeps getting bitten by. Everything in this report is offline-verifiable from the repository: the audit script, the snapshot it reads and the register it consults
are all committed. Nothing here re-fetches an operator page — see §6 for what that does and does not prove.

## 1. What was asked, and what already existed

The request is: a pick for **every** CS2 match Hotspawn lists, external betting lines (never Hotspawn's own
crowd numbers) behind each probability, a separate section for anything unresolved with its limitations,
an executive summary that links to the pick list, and a phone-readable layout — refreshed every 4–8 hours.

At the start of this session all of that existed on `main` except the last mile: 13 open rows, 13 picks,
11 percentages, 2 research-only picks, 0 rows with nothing. So this session did **not** rebuild the pipeline.
It verified it line by line, fixed what was false, and recorded what is still missing.

Two things this session could not do, and did not pretend to: reach any odds page (the sandbox resolves only
`github.com`, `api.github.com`, `pypi.org`, `registry.npmjs.org`), and dispatch the publication workflow
(`POST /actions/workflows/.../dispatches` → **HTTP 403 "Resource not accessible by integration"**, the same
refusal recorded for the Pages settings change).

## 2. The independent audit, and how to reproduce it

`python research/session-c828a275/audit_board.py data/latest.json` → `research/session-c828a275/board-audit.json`

It re-derives each open row from that row's own stored receipt, never from the rendered summary:

| Check | What it proves |
| --- | --- |
| Two distinct teams; the row is still open at snapshot time (start and lock both in the future) | The fixture is really on the board |
| A pick is published and is one of the two teams | The pick is not a stray label |
| Two finite probabilities in (0,1) summing to 1 to 1e-9 | No 50/50 filler, no rounding drift |
| The pick is the higher-probability side | Pick and numbers agree |
| Fair odds equal 1/p to 1e-9 | The advertised line is the reciprocal of the published chance |
| Market rows: published probability equals the raw `outcomePrices`, to 1e-9 | The number was copied, not computed differently |
| Market rows: raw outcome names equal the two fixture teams, directly or through a register entry that carries a primary source and a written basis | Identity, including the two alias rows |
| Market rows: raw start equals the Hotspawn start; market open and accepting orders; liquidity ≥ 100; spread inside the tier's gate (25 points, 60 in the wide tier) | The published gates actually held |
| Model rows: both points values appear verbatim in the vendored official standings file, and the probability reproduces from Valve's formula (Glicko RD 75, slope 0.7986) | The originated line is arithmetic on a primary document |
| Expiry equals the earliest of the fixture-observation window, lock, start and every quote observation/update window (a faithful reproduction of `scripts.core.pick_deadline`) | Evidence cannot outlive its window |
| Research rows: a stated "no percentage" reason, and the one-sided decision re-derived (ranked team only / listed team only) | A research pick is not a disguised percentage |
| Every row carries at least one https link on a known official host, and all http links are on known hosts | "Every row has a source" |

**Results.** 2026-10-21T21:27Z snapshot: 13 open rows, 13 picks, 11 percentages, 2 research-only, 0 without a
pick, **223 checks, 0 failures**. 2026-10-22T01:28Z snapshot (the board the repository now ships): 35 open rows,
35 picks, 28 percentages, 7 research-only, 0 without a pick, **587 checks, 0 failures**. `board-audit.json` holds
the second run.

Six checks failed across the two runs. All six were defects in the *auditor* (two of them surfaced only when the
newer board arrived with a Pinnacle bookmaker row and two two-sided ranking rows), and each was fixed by making the
check stricter rather than by relaxing it:

1. "Every http link is on an official host" failed on the collector's own feed URL,
   `phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?...` — the third-party app host the Hotspawn
   lobby itself calls (recorded as `feed_url` on every row). Added to the host list as a feed host, with a
   comment saying why, rather than dropped from the check.
2. "Expiry is the earliest of …" failed for the six model rows because the auditor used
   `generated_at` while `pick_deadline` uses `fixtures_observed_at` (21:24:01Z) and the quote observation.
   The published value (05:24:01Z) is the *earlier*, more conservative one. The auditor now reproduces
   `pick_deadline` exactly, including Pinnacle's `cutoffAt` when present.
3. "Raw outcome names are the two fixture teams" failed for two rows — and this is the interesting one, so
   it is kept as a real check with an explicit alias path. `1082837` is stored as `Zetta` / `LOS NINOS` but
   the Polymarket market names `Alianza Lima Esports` / `Los Niños`; `1082882` is stored as `UNiTY` /
   `Apogee Betclic` but the market names `UNiTY esports` / `Betclic Apogee Esports`. Both mappings are in
   `data/identities.json` with a primary source and a written basis, and the row carries the register entry
   under `identity_sources`, so the check now passes only when (a) the pair matches after folding, directly
   or through the register, **and** (b) every register entry used has an https source and a non-empty basis.
4. A `bookmaker_fallback` row (1082770 UPGRADE vs Virtus.pro) has no exchange `outcomePrices`; it stores the
   book's decimal odds. The auditor now de-vigs those odds, requires two of them, requires the published
   probabilities and the stored overround to reproduce (2.35 / 1.5435 → 7.34% overround → 39.6% / 60.4%), and
   requires the overround to sit inside the published −2%..25% gate.
5. Two `research_rank` rows (1079654, 1081150) failed the "states no percentage" check on wording: their flag
   says "no probability published", which is the same promise in different words. The check now accepts either
   phrase **and** additionally requires that such a row carries no probabilities and no fair odds at all, which
   is stricter than the wording test it replaced.
6. The identity check itself was unsound, and the 02:17Z board exposed it. `same_team` compared
   `ALIAS_MAP.get(a) == ALIAS_MAP.get(b)`, which returns `None == None` — **true** — for any two labels that are
   not in the register, so every unregistered pair compared equal. It passed only because the fixtures it ran on
   happened to be exact matches. Fixture 1081596 is the counter-example: the market lists
   `[" Phantom Academy", "Falcons Force"]` at `0.41 / 0.59` while the fixture is `Falcons Force vs Phantom
   Academy`, so the correct answer requires re-orienting the numbers, and the broken check would have accepted
   either order. The check now resolves each outcome label to exactly one fixture team (folded name, the
   marketplace's own published abbreviation, or a register entry with a primary source and a written basis),
   requires a one-to-one mapping, and only then aligns the prices. It also records the route that matched
   (`name or register`, `market abbreviation 'unity'`), which is how 1082882 turned out to be licensed by
   Polymarket's abbreviation rather than by the register — now written up in the alias-scope review note.
7. The ranking tier previously only re-derived the one-sided case. It now also re-derives the two-sided case:
   exactly two ranked teams, different ranks, the better-ranked team is the pick, both rank links are on
   hltv.org, and neither team is recorded as unranked.

## 3. Line by line, as published (2026-10-21T21:27Z snapshot)

| Fixture | Match | Start (UTC) | Method | Pick | Probabilities | Expires (UTC) | Primary source on the row |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1082837 | Zetta vs LOS NINOS | 2026-10-21T22:00 | exchange (strict) | LOS NINOS | 15.5% / 84.5% | lock 21:54 | Polymarket market 6001634 |
| 1081870 | Vitalem Aerem vs Rare Atom | 2026-10-22T05:00 | exchange_wide (46 pts) | Rare Atom | 39.0% / 61.0% | 04:54 | Polymarket market 6024922 |
| 1081597 | benched gods vs TitanFlow | 2026-10-22T11:00 | research_vrs_single | benched gods | — (no percentage) | — | Valve standings 2026-10-05 + both HLTV team pages + lineup receipt |
| 1081600 | Donstu vs Banda chuya | 2026-10-22T13:45 | model_vrs | Banda chuya | 42.4% / 57.6% | 05:24:01 | Valve standings (DONSTU 732, Banda Chuya 801) |
| 1082688 | Imperial vs Turma do Pagode | 2026-10-22T14:00 | exchange | Imperial | 77.0% / 23.0% | 05:16:57 | Polymarket market 5972064 |
| 1082689 | BESTIA vs ShindeN | 2026-10-22T14:00 | exchange | ShindeN | 46.5% / 53.5% | 05:18:58 | Polymarket market 5972071 |
| 1082882 | UNiTY vs Apogee Betclic | 2026-10-22T14:00 | exchange | Apogee Betclic | 43.5% / 56.5% | 05:14:57 | Polymarket market 6024716 |
| 1082858 | Ground Zero vs Off Chops | 2026-10-26T03:00 | model_vrs | Off Chops | 39.8% / 60.2% | 05:24:01 | Valve standings (Ground Zero 878, THUNDER dOWNUNDER 971) |
| 1082859 | NEXVOID vs Alter Ego | 2026-10-26T03:00 | model_vrs | NEXVOID | 68.2% / 31.8% | 05:24:01 | Valve standings (NEXVOID 995, Alter Ego 819) |
| 1082860 | FlyQuest vs Staqued | 2026-10-27T03:00 | research_rank_single | FlyQuest | — (no percentage) | — | HLTV fixture 2399890 + HLTV world ranking #61 |
| 1082861 | Rooster vs Abyssal | 2026-10-27T03:00 | model_vrs | Abyssal | 48.2% / 51.8% | 05:24:01 | Valve standings (Rooster 718, Abyssal 734) |
| 1082792 | HOTU vs The Huns | 2026-10-31T09:00 | model_vrs | HOTU | 85.2% / 14.8% | 05:24:01 | Valve standings (HOTU 1437, The Huns 944) |
| 1082793 | 5star vs 1WIN | 2026-10-31T13:00 | model_vrs | 1WIN | 24.3% / 75.7% | 05:24:01 | Valve standings (5star 1110, 1win 1383) |

Every market row was checked against its raw receipt: `outcomePrices` equal to the published numbers, raw
start equal to the Hotspawn start, `closed: false`, `acceptingOrders: true`, liquidity ≥ 100 and the spread
inside its tier. The two rows worth a reader's attention are the wide one (1081870: quoted bid/ask 0.16 /
0.62 around a published mid of 0.39 — flagged as `c828a275-wide-tier-midpoint-2026-10-22`) and the
underdog-of-the-board 1082689 (BESTIA 46.5% vs ShindeN 53.5%, a 7-point edge at 1-cent spread and the
largest liquidity on the board, 24,551.95).

The rebase then brought in the 22 October refresh, whose board is the one the repository now ships, so the
same audit was re-run against it: 35 open fixtures, every one with a pick, 28 with a published percentage
(7 strict exchange, 1 wide exchange, 1 Pinnacle bookmaker, 19 Valve-model), 7 research-only with no
percentage, 587 checks and 0 failures. A third run against `main`'s 2026-10-22T02:17Z snapshot (after #146's mirror tier landed)
gives 35 open, 35 picks, 29 percentages, 6 research-only and **594 checks, 0 failures**. Per-row detail for the
01:28Z run — including the exact raw prices, gates,
expiry and sources for each of the 35 — is in `board-audit.json`. Two rows changed tier between the snapshots
and are worth naming: 1081870 moved from the wide tier (61.0% inside a 16c/62c market) to a strict exchange
line at 28.5% / 71.5% on a 0.26/0.31 quote with 5,098.73 of liquidity, and 1079189 FORZE Reload vs Just Players
appeared as a new strict exchange row at 66.5% / 33.5%. A 61% reading that becomes 71.5% for the same team
inside four hours is recorded, not smoothed away: the review note on that fixture keeps both readings and
argues for publishing bid/ask bounds.

## 4. The rows without a percentage — the only coverage gap

Seven of the 35 open rows carry a pick and no number. Each blocker was re-derived here from the vendored stand-
ings file and the row's own lineup, not read off the row's prose:

| Fixture | Match | Start (UTC) | Pick | Verified blocker |
| --- | --- | --- | --- | --- |
| 1081869 | Morningstar vs NEXVOID | 2026-10-22T03:00 | NEXVOID | Morningstar absent from Valve's 380-team global file; NEXVOID listed at 995 pts (5/5 lineup) — no two-sided difference exists |
| 1081597 | benched gods vs TitanFlow | 2026-10-22T11:00 | benched gods | TitanFlow absent from that file; `benched gods` listed twice (811 and 516 pts) with no HLTV fixture lineup to tell the rows apart |
| 1082769 | K27 vs NEXORA | 2026-10-22T17:30 | K27 | NEXORA absent; K27 listed at 1,435 pts (5/5) |
| 1079654 | ex-Zero Tenacity vs ex-RUSTEC | 2026-10-23T08:00 | ex-Zero Tenacity | both labels resolve, but `ex-RUSTEC` appears **twice** (1,066 and 824 pts) and the current five shares exactly three players with both |
| 1081149 | FORZE Reload vs LFO 10 | 2026-10-23T14:00 | FORZE Reload | LFO 10 absent; FORZE Reload listed at 1,100 pts (4/5) |
| 1081150 | ex-RUSTEC vs Saint Sinners | 2026-10-23T17:00 | ex-RUSTEC | the same duplicated `ex-RUSTEC` label against Saint Sinners (810 pts, 4/5) |
| 1082860 | FlyQuest vs Staqued | 2026-10-27T03:00 | FlyQuest | Staqued absent; FlyQuest listed at 1,093 pts (5/5); HLTV world #61, no numeric line on the fixture page |

Two different limits are visible in that table, and they deserve different answers.

**The opponent is genuinely absent from Valve's file.** Four rows. Valve publishes a 380-team global table and no
regional table is vendored, so there is no second official points value of the same scale to difference. Adding a
regional file would not help these rows either: the two teams would have to share one regional file, and mixing a
global points value with a regional one is not a like-for-like difference. What would close them is a calibrated
rank-difference model (fit published point differences against dated pre-match outcomes, hold out a later period,
publish only inside a stated tolerance and date the fit on the row). That needs a historical results sample this
sandbox could not fetch, so it is written up on Flagged for Review as the route, not approximated with a guessed
curve.

**Valve's own roster rule refuses to choose.** Two rows, and the refusal is correct. Valve's model treats any two
rosters sharing three players as the same team (`TEAM_OVERLAP_TO_SHARE_ROSTER = 3`); `ex-RUSTEC` has two rows in
the file, and the current five (youka, bl1x1, yiksrezo, Brilliance, jakekeS) shares exactly three with each. The
two rows are worth 1,066 and 824 points, which against Saint Sinners' 810 implies roughly 74% and 51% for the same
side. Publishing either would be a coin-flip dressed as a model line. What would close these rows is a source that
disambiguates the label — a dated roster-change announcement, the kind of primary evidence the Off Chops alias
needed — not a rule that picks the higher points value.

For all seven, no source tried produced a two-way price: Polymarket has no validated exact-pair market, Pinnacle's
esports feed has no listing, Thunderpick and GG.BET produced no automated two-way quote (GG.BET returns an access
error), and HLTV's fixture pages expose no numeric two-way line to this collector, whose fan votes are never used.

## 5. Site and phone pass

Verified in a headless Chromium at 320 / 390 / 768 / 1440 px plus `npm run test:browser` (32 page/viewport
accessibility and no-overflow scans, subpath URLs, navigation, filters, six legacy redirects, evidence
anchors, exact expiry boundaries; 7 board expiry scenarios and 4 research-quote boundary scenarios — all
passing). Checked on a 390 px phone viewport against the rebuilt pages:

* The executive summary opens with the freshness strip (last check, re-check cadence, next slot, and the
  counts), then three in-site links — **Updated picks**, **Every pick on this page** (the
  `#picks-at-a-glance` anchor) and **Unresolved & limits** — then the "Start here" cards and the plain sentence
  "On a phone: the bottom bar has Home, Picks, Unresolved, Matches and TWC".
* Each pick card carries **both** teams' percentages with their names above them (`Vitalem Aerem 39.0%` /
  `Rare Atom 61.0%`), the pick in a labelled row below, the method tag, our fair decimal line, the VRS
  comparison where one exists, and the source links. Nothing scrolls sideways; the bottom bar stays fixed.
* `unresolved.html` and the `#unresolved-summary` section state, per row, why no percentage exists and which
  sources were tried; the six limitation classes (no book lists it, a market fails a gate, names differ,
  HLTV has no usable line, HLTV has no team names, the model needs both teams) are printed in full.
* Runtime expiry behaves: at 01:13Z, four hours after the snapshot, the pages showed 12 open rows, 12 picks
  and 10 percentages — the Zetta vs LOS NINOS row had correctly dropped to "not open" at its 21:54Z lock
  instead of being presented as a live pick.

The screenshots were taken against the 21:27Z board (the newest at the time); the 01:28Z board renders through the
same templates, and `scripts.build` + `scripts.validate` were re-run on it after the rebase (75 → 97 rows, 176 →
276 displayed rows, 655 → 908 links and assets, 20 checksums, 28 reproduced calculations, all green). No layout or copy change was needed in `scripts/build.py`; the pages already do what the request asks, which
is why this session changed no rendering code.

## 6. What this verification does and does not prove

It proves internal consistency, identity, arithmetic and expiry for every published row: the number on the
page is the number in the receipt, the receipt's teams are the fixture's teams (with every alias traced to a
primary source), and no percentage outlives its window. It does not prove that an operator's page still shows
that price — no source was re-fetched here — and it does not certify that the market is right. The scheduled
workflow (`pages.yml`, cron `4,19,34,49 * * * *`, plus a 10-minute watchdog) is what re-reads every source;
this report measures the build it produced at 21:27Z.

Two environment facts worth carrying forward, both re-measured today:
`GET /repos/.../pages` still returns `"build_type": "legacy"`, `"source": {"branch": "main", "path": "/"}`, so
every push to `main` still republishes the committed root fallback over the artifact; and
`gh workflow run pages.yml` answers **403** for this integration, so a forced re-publication is not available
from here — only the schedule and `main` pushes deliver.

## 7. Files touched by this session

| File | Change |
| --- | --- |
| `research/session-c828a275/audit_board.py` | New read-only auditor, 223 checks over the open board |
| `research/session-c828a275/board-audit.json` | New machine-readable result (13 rows, 0 failures) |
| `research/session-c828a275/REPORT.md` | This report |
| `data/review-notes.json` | Three additive notes: alias scope risk, wide-tier midpoint, and the two no-percentage rows with the route that would close them |
| `README.md` | Corrected a sentence that still said the Zetta–LOS NINOS market was "deliberately unused" after the alias made it live; added §"Independent verification" |
| `COORDINATION.md` | Claim, sources, verification and completion record; one rebase conflict with session 6d00dce8's block and one with the 5f1df842 review notes, both resolved by keeping every session's text (99 notes after the union, none dropped) |

`python -m scripts.build` was run locally into `public/` (gitignored) and its output checked: the three new notes
render as rows on `public/review.html` with their source links. The **committed root fallback** (`index.html`,
`review.html`, `build-info.json`, …) was deliberately left untouched: it still carries the 21:27Z build, which is
inside its evidence window until 05:24Z, and re-staging it by hand from a snapshot this session did not fetch is
exactly the mistake that froze the site for three days on 21 October. The next `main` publication runs
`publish_root_fallback` on a fresh snapshot and carries the notes to both publication paths.

Not touched: `scripts/build.py`, `scripts/refresh.py`, `scripts/core.py`, `assets/**`, `site/**`, the
snapshot's numbers, or any other session's research directory.
