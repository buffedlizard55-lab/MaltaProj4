# Session 92e3275c — every open fixture priced or explained, and the mirror tier switched on

Branch `arena/92e3275c-maltaproj4`. Everything below is measured on a GitHub-hosted
runner against the live sources, not estimated from the sandbox: the authoring
environment can reach GitHub and the package registries only, so the refresh, the
independent audit, the build, the validator and the browser gates all ran in
[harvest run 39750587088](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39750587088)
and the board it produced is the snapshot committed on this branch
(`data/latest.json`, `built_at 2026-10-22T08:58:49.567419Z`).

## Result in one table

| Measure | Before this session (02:23Z board) | After (08:58Z board) |
| --- | --- | --- |
| Hotspawn CS2 fixtures retained | 97 | **104** |
| Open fixtures | 35 | **43** |
| Open fixtures with a pick | 35 | **43** |
| Open fixtures with a win probability | 29 | **41** |
| Open fixtures with a pick and no percentage | 6 | **2** |
| Unresolved (no pick at all) | 0 | **0** |
| `model_vrs_mirror` rows (HLTV's view of Valve's ranking) | 0 (HTTP 403 every run) | **4** |
| Windows where the alias register could price 1082919 | 0 | **1 (live quote used)** |

Method mix on the 08:58Z board, all 43 open rows accounted for:
`exchange 24`, `model_vrs_mirror 4`, `model_vrs 9`, `bookmaker_fallback 2`,
`exchange_wide 2`, `research_rank 1`, `research_rank_single 1`.

The two rows that still carry a pick with no percentage are, with their own
published reasons:

- `1082925` BESTIA Academy vs RED Canids Academy, 2026-10-23T19:00Z — `research_rank`:
  RED Canids Academy is HLTV world #170 against BESTIA Academy #184. A ranking-order
  signal, no market line readable, no percentage published.
- `1082860` FlyQuest vs Staqued, 2026-10-27T03:00Z — `research_rank_single`: FlyQuest is
  HLTV world #61 while Staqued appears in the same HLTV fixture with no world-ranking
  number. One-sided evidence, no percentage published.

Nothing was filled in to make the count look better: a blank stays blank and carries
its reason on the row, in the unresolved/limitations section and on
[Flagged for Review](../../review.html).

## What changed, and why

### 1. The Valve-ranking mirror was read after the host had already been rate-limited

Measured, not assumed. [`scripts/probe_92e3275c.py`](../../scripts/probe_92e3275c.py) fetched
`https://www.hltv.org/valve-ranking/teams` from a GitHub runner with the refresh's own
User-Agent and got **HTTP 200, 1,631,235 bytes**
([probe run 39743668680](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39743668680)),
while every scheduled board recorded *"HLTV Valve ranking mirror unavailable: HTTP 403
persisted after 3 rate-limit waits (10s, 30s, 60s); host blocked for this run."* The
difference is order, not access: the mirror used to be requested **after** the
per-fixture HLTV sweep (~50 page loads), which is what earned the 403 and the
run-long host block.

`scripts/refresh.py` now reads the dated Valve ranking **first**, immediately after the
open-fixture list is built, and the late tier uses that one read instead of fetching
again. It still records a refusal as a refusal, and the request is not disguised.

Effect on this board: the live page parsed as
`ranking on October 22nd, 2026`, **396 teams**, `parsed_by: ranked-team blocks`, and four
fixtures that could not be priced from Valve's monthly GitHub file now carry a
percentage from the same public points:

| Fixture | Points (standings) | Model probability |
| --- | --- | --- |
| `1079654` ex-Zero Tenacity vs ex-RUSTEC | 1053 (#95) / 1073 (#91) | 47.8% / 52.2%, pick ex-RUSTEC |
| `1081149` FORZE Reload vs LFO 10 | 1104 (#85) / 805 (#157) | 77.3% / 22.7%, pick FORZE Reload |
| `1081150` ex-RUSTEC vs Saint Sinners | 1073 (#91) / 898 (#133) | 68.1% / 31.9%, pick ex-RUSTEC |
| `1082926` Isurus vs Hacha | 719 (#200) / 438 (#378) | 76.2% / 23.8%, pick Isurus |

These are **originated model lines, not market prices**: the points come from HLTV's dated
view of Valve's ranking because Valve's own file cannot resolve both clubs on the row,
and every row publishes that dated page, the formula link, the calibration link and the
limitation.

### 2. The probe marker that reported zero was a markup artefact, not a parse failure

The probe counts a marker in the raw bytes, and reported `marker='Valve points' x0` on a
page the parser reads successfully. The retained page shows why: HLTV renders the unit
inside a mobile-only span —

```html
<span class="points">(972<span class="gtSmartphone-only"> HLTV</span> points)</span>
```

— so the literal substring `Valve points` never appears in the bytes while the rendered
text reads `1993 Valve points`. Checked directly:

```text
raw 0 stripped 1
```

The parser reads the *rendered text* of the points node, keys on the word `Valve`, and
refuses the world-ranking view, which says `HLTV points`. The probe now reports the
tag-stripped count beside the raw count, so a future run cannot read a split-tag phrase as
a block. The probe records are the run links above; nothing in the page request changed.

### 3. One team, two labels: `Tropa do KinGui` = `Projeto do KinGui`

Hotspawn publishes `Projeto do KinGui vs Martians` (fixture 1082919); HLTV and Polymarket
publish `Tropa do KinGui vs Martians` for the same match. Without a register entry, that
row had no market identity at all — the 02:23Z board carried
`attempts: "Unverified opponent/alias or roster-name mismatch; no fuzzy match was used."`

The register entry is evidence-based, not name-based:

- identical start `2026-10-22T13:00:00Z`, same opponent, same event
  (CCT South America 2026 Series #7) in Hotspawn's feed, HLTV match 2399904, EGamersWorld
  and Polymarket market 6033256;
- the **same five players** — ALLE, ckzao, drg, xureba, lash — on EGamersWorld's
  "Projeto do KinGui" side and on HLTV's match roster for "Tropa do KinGui";
- recorded limitation: HLTV's team-overview page for id 13151 still prints an older roster
  (KinGui, cLd, brokeN, Ltz, remix), so the overview page is not used as roster evidence.

On the 08:58Z board the row resolved through the **strict** exchange tier: Polymarket
6033256, spread 22.0 points (≤ 25), liquidity $228.46 (≥ $100), observed 08:56:57Z,
probabilities **66.0% / 34.0%**, pick **Projeto do KinGui**. The wide tier was also tested
end to end and remains available for a 25–60 point spread.

EGamersWorld's page for the same fixture prints **1.8 / 1.8** — a placeholder pair, not a
market. It is refused (identical prices on both sides cannot be a de-vigged 50/50) and is
never used as a probability.

## Verification actually run

| Gate | Result |
| --- | --- |
| Real refresh of every source, on a runner | `harvest-92e3275c` run 39750587088, green |
| Independent snapshot audit (`verification-c6/audit_snapshot.py`) before build | clean |
| Quarantine pass (withhold any row the audit cannot reproduce) | nothing withheld |
| Build | 104 sourced rows, 41 with percentages, 2 without, 0 unresolved |
| `scripts.validate --site public` and `--site .` | 276 displayed rows, 20 checksums verified |
| Unit + failure-mode suites | **776 unit**, 9 audit, 12 independent-auditor tests, integrity checks — all pass |
| Browser gates | 32 page/viewport accessibility and no-overflow scans (320/390/768/1440px), 7 expiry scenarios, 8 phone/queue/unresolved scenarios |
| Legacy pinned suites that required a priced 1082919 | pass on this snapshot (`probe_7601d5ee`, `test_session_d6df5beb`, `verification-767649ba`) |

Every one of those gates is repeated by the production workflow on `main`; the session's
own harvest is the same pipeline with publication removed, because `pages.yml` refreshes
live sources only on `main` and on its fixed branch list.

## Phone-first summary

The home page is rebuilt as a briefing rather than a reference dump: the four numbers
(43 open · 43 picks · 41 with a probability · 0 unresolved) with one-tap links to
**Updated picks**, **All picks at a glance**, **Unresolved & limitations** and **All 104
matches**; the long reference tables (gap ledger, per-source coverage, access limitations)
fold into `<details>` blocks; and the jump-link bar sits above the fold on a phone. The
home page dropped from 40,768 px to 19,108 px tall at 390 px wide in the last measurement
of this layout, and the browser gates assert no horizontal overflow at 320/390/768/1440px
on every page.

## Flagged for Review (published on the site)

1. **`92e3275c-tropa-do-kingui-alias-2026-10-22`** — the two-label identity, its five
   sources, and the stale HLTV overview roster.
2. **`92e3275c-egw-1.8-placeholder-1082919`** — EGamersWorld's 1.8/1.8 listing refused as a
   placeholder; the published 66/34 comes only from the exchange quote.
3. **`92e3275c-mirror-tier-live-2026-10-22`** — the mirror tier's first live numbers, the
   read-order fix, and the split-tag marker explanation.
4. **`92e3275c-two-rows-without-percentage-2026-10-22`** — the two remaining blank
   percentages and exactly what input each is missing.

## Limits of this claim

- Every number is a **dated observation**. This board is 08:58Z; the schedule refreshes at
  :04, :19, :34 and :49 past each hour, best effort, and the site withholds expired picks.
- Hotspawn supplies **fixture inventory only**. None of its crowd percentages is a
  probability, a pick or a model input anywhere in this work.
- The mirror line is Valve's ranking **as HLTV publishes it**, not Valve's monthly file, and
  it is an originated model estimate rather than a market price. A page that prints
  `HLTV points`, an unreadable date header, fewer than 100 rows or a duplicated label
  without a lineup still produces no number.
- The exchange quote for 1082919 is a single venue's midpoint with a real 22-point spread.
  It is not a consensus and not a tradable quote; fees are excluded.
- Roster changes, stand-ins, map pools, LAN/online and best-of format are not modelled.
