# Session 9bbd095e — End-to-End Primary-Source Verification & Root-Staging Gate Fix Report

**Date:** `2026-10-26 UTC`  
**Branch:** `arena/9bbd095e-maltaproj4`  
**Harvest run:** [`40251642534`](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40251642534) (`research/harvest-9bbd095e/refresh-snapshot.json`, `generated_at: 2026-10-26T00:58:54.030684Z`, SHA-256 `0c9d389842bf5f08ce8dc0600dcc806a3ba8342c689b7d1bcf9deeb7b25f9e8b`)

---

## 1. Executive Summary of Findings

1. **Complete Hotspawn CS2 feed capture (`81` scheduled rows: `19` open, `62` past/locked) & automated `<4-8h` refresh cadence verified.**
   - Direct primary reads of Hotspawn's lobby (`https://play.hotspawn.com/lobby`) and public scheduled fixtures API (`https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`) confirmed **81 scheduled CS2 fixtures** (`19` open + `62` past-dated/locked), adding 8 newly-scheduled Bo3 playoffs/group matches (`1079201`, `1081159`, `1079202`, `1081160`, `1079203`, `1081162`, `1081163`, `1081164`) to the prior 11 open fixtures.
   - `.github/workflows/pages.yml` schedules 4 refresh attempts per hour (`4,19,34,49 * * * *`) with a freshness gate well inside the 4–8h target window, reinforced by `.github/workflows/refresh-watchdog.yml` checking live `build-info.json` every 10 minutes and dispatching a refresh if the published snapshot exceeds 90 minutes.
2. **19/19 open CS2 picks & two-way win probabilities verified line by line from external trusted sources — zero Hotspawn crowd-percentage usage.**
   - **8 `exchange` rows** (Polymarket strict gate: liquidity `>= $100`, spread `<= 0.25`, exact named-outcome orientation): `1082858` (`Off Chops 79.5%`), `1079201` (`Nemesis 72.5%`), `1082860` (`FlyQuest 92.5%`), `1082861` (`Abyssal 57.5%`, wide-spread warning disclosed), `1082897` (`B8 59.5%`), `1082898` (`FaZe 65.5%`), `1082900` (`Luminosity 52.5%`), `1082901` (`GamerLegion 54.5%`).
   - **1 `bookmaker_fallback` row** (de-vigged two-way bookmaker decimal odds `1.62 / 2.16` via BO3.gg API -> Thunderpick): `1082859` (`NEXVOID 57.1% / Alter Ego 42.9%`, exact pair + `2026-10-26T03:00:00Z` start verified against HLTV `2399889`).
   - **8 `model_vrs` rows** (official Valve global standings `standings_global_2026_10_05.md` commit `eec4853d...`, Valve's `model/fit.js` Glicko expectation with RD `75` + `modelfit.png` slope `0.7986`, HLTV starting-five continuity `3/5`–`5/5` on all 16 clubs): `1079202` (`FOKUS 74.5%`), `1079203` (`Metizport 68.0%`), `1081160` (`HAVU 58.3%`), `1093218` (`Nuclear TigeRES 66.5%`), `1081163` (`BakS 73.0%`), `1081164` (`Inner Circle Academy 70.4%`), `1082792` (`HOTU 85.2%`), `1082793` (`1WIN 75.7%`).
   - **2 `model_vrs_mirror` rows** (HLTV's dated Valve ranking `https://www.hltv.org/valve-ranking/teams/2026/october/26`, `389` teams, same Valve formula + `0.7986` slope, `4/5`–`5/5` HLTV roster overlap):
     - `1081159` `LFO 10 vs ex-6666` -> **`ex-6666` `67.2%`** (`32.8% / 67.2%`, `#157` `803` pts vs `#118` `968` pts, `[5/5, 5/5]` overlap; `LFO 10` absent from `2026-10-05` Valve file).
     - `1081162` `ex-RUSTEC vs Spirit Academy` -> **`ex-RUSTEC` `52.3%`** (`52.3% / 47.7%`, `#94` `1059` pts vs `#101` `1038` pts, `[4/5, 5/5]` overlap; two `ex-RUSTEC` rows tied on overlap in `2026-10-05`, whereas `2026-10-26` has a unique `#94` row).
   - Full 81-row ledger with exact math, raw inputs, and official URLs: [`ROW_AUDIT_81.md`](./ROW_AUDIT_81.md).
3. **Strict HLTV-first alternate-source research on non-featured matches only — zero fabricated aliases or inferred values.**
   - Every non-exchange open match (`11` rows) queried HLTV first (`matches/2399889`, `2399117`, `2399509`, `2399118`, `2399510`, `2399119`, `2399512`, `2399513`, `2399514`, `2399437`, `2399438`), then Pinnacle (`sports/12/markets/straight`), Thunderpick, GG.BET, and BO3.gg API (`api.bo3.gg`), falling to Valve VRS / dated HLTV Valve mirror only where no valid two-sided betting line existed.
   - **Irregularity #1 (`1081159` `LFO 10 vs ex-6666`):** Polymarket market `6231429` prices `Sökerorg vs ex-6666` at `2026-10-26T12:00:00Z` (`0.315 / 0.685`, `spread: 0.53`), whereas both Hotspawn and HLTV (`matches/2399509`, `team/14084/lfo-10`) list `LFO 10` with zero `Sökerorg` alias. Per non-inference rules, `Sökerorg` was **not** added to `data/identities.json`, market `6231429` remained refused, and the finding is published on `review.html` (`session-9bbd095e-polymarket-sokerorg-lfo10-1081159-2026-10-26`).
   - **Irregularity #2 (BO3.gg `NODWIN Clutch Series 13` afternoon slot rotation):** Hotspawn and HLTV (`events/9440/matches`) agree on all four quarterfinal UTC starts (`09:00Z`, `12:00Z` FOKUS vs ex-Zero Tenacity, `15:00Z` Metizport vs BRUTE, `18:00Z` Nuclear TigeRES vs UNiTY), while BO3.gg (`tournament_id=6149`) carries `bet_updates: null` on all four and rotates the three afternoon UTC timestamps (`12:00Z` Metizport, `15:00Z` Nuclear TigeRES, `18:00Z` FOKUS). `scripts/bo3.py`'s exact-UTC gate prevented cross-slot matching; documented on `review.html` (`session-9bbd095e-bo3-nodwin13-slot-rotation-2026-10-26`).
4. **Root-staging CI regression diagnosed and fixed (`scripts/audit_5717f7d9.py`).**
   - In both harvest run `40251642534` (`research/harvest-9bbd095e/logs/root-unit-tail.txt`) and live `main` publish run `40252224713` (Step 17 `Keep the legacy main:/ root fallback on the verified build`), `test_session_5717f7d9` failed with `Model row has no VRS evidence` on `1081159` and `1081162` because `scripts/audit_5717f7d9.py` dispatched `model_vrs_mirror` to `_audit_vrs` (`line 237`) while filtering `ev` strictly to `provider in ("Valve VRS model",)` (`line 377`).
   - Patched `_audit_vrs` in `scripts/audit_5717f7d9.py` (with zero imports from `scripts.*`) to validate `"HLTV Valve ranking (Valve points)"` on `model_vrs_mirror` rows: re-deriving Glicko + `0.7986` calibration, checking `<=8h` `observed_at` freshness, `https://www.hltv.org/valve-ranking/teams/...` URL provenance, `0..45d` `ranking_as_of` age, `>=100` `ranking_teams_count`, duplicate-label `>=3/5` HLTV roster disambiguation, dated-Valve-ranking disclosure flag, and prior unresolved `Valve VRS model` attempt. Locked down with positive + 8 synthetic fail-closed tests in `tests/test_session_9bbd095e.py` and disclosed on `review.html` (`session-9bbd095e-audit-5717f7d9-mirror-gate-2026-10-26`).

---

## 2. Executive Summary, Subpages & Mobile/Desktop Viewport Verification

Measured with headless Chromium (`@sparticuz/chromium` + `playwright-core`) across 6 viewports (`research/session-9bbd095e/viewport-geometry.json`) and all 13 repository browser suites (`npm run test:browser`):

| Viewport | Horizontal Overflow (8 pages) | `#exec-quicknav` First-Screen Box | `picks.html` First Row Both Win % Bottom | Fixed Mobile Tab Bar Top | Clear of Tab Bar |
| --- | --- | --- | --- | --- | --- |
| `320x568` (iPhone SE) | `false` (0/8 pages) | `y = 290..359` (`69px`) | `y = 426` (`20.5%` / `79.5%`) | `y = 507` | **Yes (`+81px` margin)** |
| `375x667` (iPhone SE 3) | `false` (0/8 pages) | `y = 290..346` (`57px`) | `y = 392` (`20.5%` / `79.5%`) | `y = 606` | **Yes (`+214px` margin)** |
| `390x844` (iPhone 14) | `false` (0/8 pages) | `y = 300..364` (`65px`) | `y = 421` (`20.5%` / `79.5%`) | `y = 783` | **Yes (`+362px` margin)** |
| `412x915` (Pixel 7) | `false` (0/8 pages) | `y = 300..364` (`65px`) | `y = 421` (`20.5%` / `79.5%`) | `y = 854` | **Yes (`+433px` margin)** |
| `768x1024` (iPad Portrait) | `false` (0/8 pages) | Desktop/tablet header nav active | `y = 729` | `null` (desktop nav) | **Yes** |
| `1440x900` (Desktop) | `false` (0/8 pages) | Desktop header nav active | `y = 630` | `null` (desktop nav) | **Yes** |

- **Executive summary (`index.html`):** Exposes `#exec-quicknav` above the fold on phones and `#exec-summary` with direct in-site links to `picks.html`, `#picks-at-a-glance`, `unresolved.html`, `#unresolved-summary`, `#unresolved-limits`, `matches.html`, `sources.html#method`, and `review.html`, plus the dedicated unresolved & non-market pick-generation limitations section (`#unresolved-summary` / `#unresolved-limits`).
- **Category subpages:** `picks.html` (all open picks + both win percentages + official links), `unresolved.html` (non-market & unresolved research ladder + limitations), `matches.html` (all 81 Hotspawn rows including 62 unpriced past/locked records), `review.html` (`Flagged for Review` with `282` sourced notes + row flags), `sources.html` / `methodology.html` (live source health, 4–8h schedule, formulas), `evidence.html` (per-row audit anchors), and `analysis.html`.
- **Internal link & checksum integrity:** `scripts.validate` verified `81` rows, `19` probability calculations, `15` pages (`9` primary + `6` legacy redirects), `779` internal links and assets (`0` broken links), `20` SHA-256 artifact checksums, and `200` displayed match rows.
