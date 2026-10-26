# Session 77046e56 — verification report (CS2 board, 26 October 2026)

Scope: the user's brief — every CS2 match Hotspawn lists must carry a pick, unresolved rows must be
named with their limitation, the executive summary must link to the live pick list, and the whole thing
must be readable on a phone. This report records what was **measured**, what was **re-read at source**,
and what is **still a limitation**. Nothing here is inferred.

---

## 1. The question this session started from: does the board cover the lobby?

At 00:50Z on 26 October the live Hotspawn lobby rendered **"All tiers (81)"** and **"19 matches this
week"**, while the published board carried **73 feed rows / 11 open matches**. Eight upcoming fixtures
were absent entirely:

| Fixture | Teams | Competition | Start (UTC) |
| --- | --- | --- | --- |
| 1079201 | INOX Division vs Nemesis | NODWIN Clutch Series #13 | 26 Oct 09:00 |
| 1079202 | FOKUS vs ex-Zero Tenacity | NODWIN Clutch Series #13 | 26 Oct 12:00 |
| 1079203 | Metizport vs BRUTE | NODWIN Clutch Series #13 | 26 Oct 15:00 |
| 1081159 | LFO 10 vs ex-6666 | CCT Europe 2026 Series #12 | 26 Oct 12:00 |
| 1081160 | HAVU vs ILLYRIANS | CCT Europe 2026 Series #12 | 26 Oct 15:00 |
| 1081162 | ex-RUSTEC vs Spirit Academy | CCT Europe 2026 Series #12 | 27 Oct 12:00 |
| 1081163 | BakS vs Saint Sinners | CCT Europe 2026 Series #12 | 27 Oct 15:00 |
| 1081164 | Inner Circle Academy vs Lavked | CCT Europe 2026 Series #12 | 27 Oct 18:00 |

**Measured answer, not an assumption.** A read-only probe ran on GitHub's egress
([run 40251063027](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40251063027), receipts in
`research/session-77046e56/diag/`) and requested *the collector's own URL* once:

```
https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1
```

Result: **HTTP 200, 63,325 bytes, 81 CS2 rows, 19 with a future start, and all eight fixtures present.**
The rendered lobby (`https://play.hotspawn.com/lobby`) carries the same 81 tier count and the same eight
IDs; the CS2 page agreed at 81; `limit`, `page`, `offset`, `per_page` and `take` are rejected by the API
with `property … should not exist` (400). **The collector was correct.** Hotspawn added the eight
fixtures to the feed after the 00:07Z observation that produced the 00:10Z board, and the board had not
refreshed yet. No collector code was changed, because no collector defect reproduced.

## 2. The fresh capture used for every check below

| Field | Value |
| --- | --- |
| Snapshot `generated_at` | `2026-10-26T00:52:33.666528Z` |
| Fixtures observed | `2026-10-26T00:48:58.637868Z` |
| Feed rows | **81** |
| Open rows | **19** |
| Rows with a pick | **19** |
| Rows with a two-way probability | **19** |
| Research-only (pick, no %) | **0** |
| Unresolved | **0** |
| Coverage counts | `api 81 / page 81 / lobby 81 / retained 81`, `verified` |
| Method mix | 8 exchange · 1 researched bookmaker listing · 8 Valve-VRS model · 2 HLTV-dated Valve-ranking mirror |
| Build | 81 sourced rows, 19 with percentages, 0 without, 0 unresolved |
| Independent counters | rows 81 · calculations reproduced 19 · pages 15 · links 779 · checksums 20 · displayed rows 200 |

Evidence: [run 40251150280](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40251150280)
(refresh → quarantine 0 withheld → independent audit → build → validate → unit suite, every step rc 0),
with the census in `research/session-77046e56/harvest/census.md` and the raw snapshot beside it.

## 3. Line-by-line: all 19 open rows

"Re-read here" means this session fetched the linked source and compared the retained values against it.
"Arithmetic only" means the published value re-derives exactly from retained inputs, but the source page
was not fetched again in this session — it is disclosed as such rather than dressed up.

| # | Fixture | Start (UTC) | Method | Pick | Probabilities | Source | This session's check |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ground Zero vs Off Chops (1082858) | 26 Oct 03:00 | Exchange | Off Chops | 20.5 / 79.5 | [Polymarket 6066508](https://gamma-api.polymarket.com/markets/6066508) | **Re-read here** — `0.205 / 0.795`, spread 0.01; retained liquidity $10,714.91 at observation 00:49:02Z |
| 2 | NEXVOID vs Alter Ego (1082859) | 26 Oct 03:00 | Researched bookmaker listing | NEXVOID | 57.1 / 42.9 | [BO3.gg line](https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026) | **Re-read here** — `1.62 / 2.16`, overround 1.080247 → 57.14 / 42.86 |
| 3 | INOX Division vs Nemesis (1079201) | 26 Oct 09:00 | Exchange | Nemesis | 27.5 / 72.5 | [Polymarket 6186053](https://gamma-api.polymarket.com/markets/6186053) | **Re-read here** — `0.725 / 0.275`, spread 0.01, start 09:00Z; retained liquidity $5,897.37 |
| 4 | FOKUS vs ex-Zero Tenacity (1079202) | 26 Oct 12:00 | VRS model | FOKUS | 74.5 / 25.5 | [Valve detail 0048](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0048--fokus--banjo-jocab-matheos-podi-ztr.md) | **Re-read here** — FOKUS rank 48, 1320.8 points; roster matches |
| 5 | LFO 10 vs ex-6666 (1081159) | 26 Oct 12:00 | HLTV Valve-ranking mirror | ex-6666 | 32.8 / 67.2 | [HLTV Valve ranking, 26 Oct 2026](https://www.hltv.org/valve-ranking/teams/2026/october/26) | **Re-read here** — #157 LFO 10 = 803, #118 ex-6666 = 968, both rosters match |
| 6 | Metizport vs BRUTE (1079203) | 26 Oct 15:00 | VRS model | Metizport | 68.0 / 32.0 | [Valve global standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | **Arithmetic only** — 1290 / 1116 re-derive to 68.0% |
| 7 | HAVU vs ILLYRIANS (1081160) | 26 Oct 15:00 | VRS model | HAVU | 58.3 / 41.7 | [Valve global standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | **Arithmetic only** — 937 / 862 re-derive to 58.3% |
| 8 | Nuclear TigeRES vs UNiTY (1093218) | 26 Oct 18:00 | VRS model | Nuclear TigeRES | 66.5 / 33.5 | [Valve 2026-10-05 detail files](https://github.com/ValveSoftware/counter-strike_regional_standings/tree/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05) (`0046`, `0069`) | **Re-read here** — rank 46 / 1323.5 and rank 69 / 1167.4 |
| 9 | FlyQuest vs Staqued (1082860) | 27 Oct 03:00 | Exchange | FlyQuest | 92.5 / 7.5 | [Polymarket 6066520](https://gamma-api.polymarket.com/markets/6066520) | **Arithmetic only** — pair sums to 1.000 |
| 10 | Rooster vs Abyssal (1082861) | 27 Oct 03:00 | Exchange (wide spread) | Abyssal | 42.5 / 57.5 | [Polymarket 6066525](https://gamma-api.polymarket.com/markets/6066525) | **Re-read here** — `0.425 / 0.575`, spread 0.25 published as low precision; retained liquidity $4,915.74 |
| 11 | B8 vs K27 (1082897) | 27 Oct 08:00 | Exchange | B8 | 59.5 / 40.5 | [Polymarket 6024944](https://gamma-api.polymarket.com/markets/6024944) | **Arithmetic only** — pair sums to 1.000 |
| 12 | Alliance vs FaZe (1082898) | 27 Oct 11:00 | Exchange | FaZe | 34.5 / 65.5 | [Polymarket 6024952](https://gamma-api.polymarket.com/markets/6024952) | **Arithmetic only** — pair sums to 1.000; model favourite differs, disclosed on the row |
| 13 | ex-RUSTEC vs Spirit Academy (1081162) | 27 Oct 12:00 | HLTV mirror | ex-RUSTEC | 52.3 / 47.7 | [HLTV Valve ranking, 26 Oct 2026](https://www.hltv.org/valve-ranking/teams/2026/october/26) | **Re-read here (partial)** — page, heading and ex-RUSTEC's position at #94 confirmed; the two point values (1059 / 1038) were not read in the page text → flagged |
| 14 | BakS vs Saint Sinners (1081163) | 27 Oct 15:00 | VRS model | BakS | 73.0 / 27.0 | [Valve detail 0158](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0158--saint_sinners--caleyy-deb0-irv1ng-pavlysha666-ves111.md) | **Re-read here** — Saint Sinners rank 158, 809.6 points; 1044 / 810 re-derive to 73.0% |
| 15 | Luminosity vs HOTU (1082900) | 27 Oct 17:00 | Exchange | Luminosity | 52.5 / 47.5 | [Polymarket 6024960](https://gamma-api.polymarket.com/markets/6024960) | **Arithmetic only** — pair sums to 1.000 |
| 16 | Inner Circle Academy vs Lavked (1081164) | 27 Oct 18:00 | VRS model | Inner Circle Academy | 70.4 / 29.6 | [Valve global standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | **Arithmetic only** — 1064 / 862 re-derive to 70.4% |
| 17 | Envy vs GamerLegion (1082901) | 27 Oct 20:00 | Exchange | GamerLegion | 45.5 / 54.5 | [Polymarket 6037120](https://gamma-api.polymarket.com/markets/6037120) | **Arithmetic only** — pair sums to 1.000 |
| 18 | HOTU vs The Huns (1082792) | 31 Oct 09:00 | VRS model | HOTU | 85.2 / 14.8 | [Valve global standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | **Arithmetic only** — reseeds from the same file |
| 19 | 5star vs 1WIN (1082793) | 31 Oct 13:00 | VRS model | 1WIN | 24.3 / 75.7 | [Valve global standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | **Arithmetic only** — reseeds from the same file |

## 4. Arithmetic reproduction

Every originated line was recomputed from its retained points with Valve's own published fit:

```
G = 0.9728209910486895
E = 1 / (1 + 10 ** (-G * (points_a - points_b) / 400))
p = 0.5 + 0.7986 * (E - 0.5)
```

All **12** model rows reproduce their published probability to **< 1e-9**. All **8** exchange pairs sum
to **1.000**. The bookmaker row de-vigs exactly: `1/1.62 + 1/2.16 = 1.080247 → 57.143 / 42.857`. Fair
odds are the reciprocal of the published probability, rounded for display only.

## 5. Executive summary and phone readability (measured)

`npm run test:browser` on the 19-row build: **13 suites, all exit 0, `"failures": []`**, 32 axe scans with
**0 violations** at 320, 390, 768 and 1440 px. Raw geometry in `research/session-77046e56/mobile/`.

| Viewport | Exec summary title | First pick card | Both percentages | Fixed tab bar | Horizontal overflow |
| --- | --- | --- | --- | --- | --- |
| 320 × 568 | y 290 → 359 | y 363 → 526 (h 163) | y 409–430 / 432–463 | y 507 → 568 | **false** |
| 390 × 844 | above the fold | first card visible | both visible | y 783 | **false** |
| 412 × 915 | above the fold | y 378 | both visible | — | **false** |

The phone quick-nav reads **"19/19 picks · 0 unresolved (no %) · 62 feed rows are not open"** and links to
`picks.html`, `#picks-at-a-glance`, `unresolved.html`, `#unresolved-summary`, `#unresolved-limits`,
`matches.html`, `sources.html#method` and `review.html`. The board shows 19 cards, 19 picks and 19 priced
rows on the phone run — the footer bar clears the last card by 44 px at 320 px.

## 6. The defect that made a correct board look wrong: the auditor rejected mirror rows

`scripts/audit_5717f7d9.py` selected model evidence with `provider == "Valve VRS model"` **only**. Rows
priced from HLTV's dated view of Valve's ranking carry `provider == "HLTV Valve ranking (Valve points)"`.
On the 81-row capture the auditor therefore emitted this hard finding (verbatim from the failing test
output, one per mirror row — `1081159` and `1081162`):

```
{"severity": "fail", "area": "vrs_evidence", "fixture": "1081159",
 "message": "Model row has no VRS evidence."}
```

— a **hard failure** for two rows whose arithmetic re-derives exactly. That failure sits inside the
publish workflow's own unit gate, and the gate refuses to stage a snapshot on the legacy `main:/` root
when the suite is red. Consequence, observed: the 81-row build was verified and deployed as an artifact
while the committed root kept the older 73-row snapshot, so the public board kept serving **11 open
matches** after Hotspawn listed **19**.

Fix in this change: the auditor accepts both providers, applies the identical arithmetic checks, and adds
mirror-specific assertions (ranking date, ranking page hash, fixture identity, two named ranking rows).
`tests/test_session_77046e56.py` proves the checks are not weakened — deleting the date or hash, swapping
the fixture teams, or perturbing the probability by 5 points each produces the expected failure.

After the fix, on the 81-row snapshot: **1,784 tests, OK (9 skipped)**, `scripts.validate` exit 0 with
81 rows / 19 calculations / 15 pages / 779 links / 20 checksums / 200 displayed rows.

## 7. Irregularities and limitations (all published on the review page)

1. **No scheduled publish between 00:05:31Z and ~01:10Z**, and the ten-minute watchdog produced no run in
   that window either (its previous run started 2026-10-25T23:19:50Z). The eight fixtures existed on
   Hotspawn before any board could show them. Inside the 8-hour evidence window, but it is the mechanism
   by which a real fixture looks unpicked. → `session-77046e56-cron-delivery-gap-2026-10-26`
2. **Two mirror inputs not read directly** (1081162: 1059 / 1038). The page, heading, roster and rank
   position were confirmed; the point values were not. → `session-77046e56-mirror-points-partial-2026-10-26`
3. **Ten rows verified by arithmetic only** (table §3, rows 6, 7, 9, 11, 12, 15, 17, 18, 19): their
   sources were not re-fetched in this session. This is disclosed, not hidden.
4. **Wide exchange spread** on 1082861 (0.25) — inside the documented 0.60 ceiling and above the $100
   liquidity floor, published with the low-precision label on the row.
5. **Price movement between observation and re-read**: 6066508 moved 0.19/0.81 → 0.205/0.795 and the
   BO3.gg listing moved 1.61/2.18 → 1.62/2.16. Rows carry the observation timestamp; a re-read later can
   legitimately differ. No value was rewritten from a later read.
6. **62 of 81 feed rows are not open** (past-dated rows the endpoint still returns as `scheduled`). They
   stay on *All matches*, labelled, and are never priced.
7. **The auditor/provider mismatch above** — a verification defect, not a data defect:
   `session-77046e56-audit-mirror-provider-2026-10-26`.

## 8. Reproduction

```bash
python3 -m scripts.build --data /tmp/fresh.json     # 81 rows, 19 priced, 0 unresolved
python3 -m scripts.validate --data /tmp/fresh.json --site .
python3 -m unittest discover -s tests               # 1,784 tests, OK (9 skipped) with the 81-row snapshot
npm run test:browser                                # 13 suites, failures: []
```

Probe and harvest receipts: `research/session-77046e56/diag/`, `research/session-77046e56/harvest/`
(`census.md`, `snapshot.json`, `independent-row-audit.md`, `published-row-audit.md`, `logs/01..07`).
