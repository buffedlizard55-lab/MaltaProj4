# Session 8e9bf19f — independent verification of the integrated board (2026-10-22)

Scope: the merged result of PR [#175](https://github.com/buffedlizard55-lab/MaltaProj4/pull/175) (`cb867c3c`, Stavka/Winline tier + `model_vrs_mirror` + 403 transport fallback) and PR [#177](https://github.com/buffedlizard55-lab/MaltaProj4/pull/177) (`eaff7cce`, phone-first pick surface, source-clock safeguards), integrated on branch `arena/8e9bf19f-maltaproj4`.

Everything below was read by hand on **2026-10-22** with the timestamps given. Nothing in this report is copied from a previous session's claim without re-reading the page.

## 1. Snapshot under verification

| Item | Value | Source |
| --- | --- | --- |
| Fixture inventory | 107 rows, 43 open, 43 with a pick, 41 with a win probability, 2 research-only (no percentage), 0 with no pick at all | `data/latest.json`, `generated_at 2026-10-22T07:58:54.670274Z` |
| Pages built from it | 15 pages, 964 internal links/assets, 20 checksums, 283 displayed rows, 41 calculations replayed | `python -m scripts.validate --data data/latest.json --site public` and `--site .` |
| Hotspawn is inventory only | every `source_url`/`feed_url` is Hotspawn; no Hotspawn percentage appears in any `probabilities` field | `data/latest.json`, spot-checked row by row for the 8 newest rows |

## 2. What was re-read at the primary source

### 2.1 `1079654` ex-Zero Tenacity vs ex-RUSTEC — Winline two-way line

- **Stavka.tv match header, read 2026-10-22T08:55Z:** `П11.90` + Winline logo, `П21.80` + Winline logo → [stavka.tv/matches/csgo/23-10-2026-ex-zero-tenacity-ex-rustec](https://stavka.tv/matches/csgo/23-10-2026-ex-zero-tenacity-ex-rustec). This confirms the stored receipt (`odds: [1.9, 1.8]`, `observed_at 07:50Z`) and its provider label.
- **Kickoff-time check.** The page renders `04:00 23 октября`. HLTV renders the same fixture as `04:00 23rd of October 2026` → [HLTV match 2399331](https://www.hltv.org/matches/2399331/ex-zero-tenacity-vs-ex-rustec-cct-2026-europe-series-11). Both pages were rendered through the same fetcher, whose clock is UTC−4 (the KinGui fixture stored at 13:00Z renders as `09:00` on Stavka), so `04:00` = **08:00 UTC**, which is exactly Hotspawn's and HLTV's start. **No schedule discrepancy** — the stored `start: 2026-10-23T08:00:00Z` is correct.
- **Identity.** HLTV page title and header confirm `ex-Zero Tenacity vs. ex-RUSTEC at CCT 2026 Europe Series 11`, Bo3, Round of 16, HLTV `#67` for ex-Zero Tenacity — matching the receipt's identity note (#67 vs #70).
- **Arithmetic.** `1/1.90 = 0.526316`, `1/1.80 = 0.555556`, sum `1.081871` → `48.65% / 51.35%`; published `[0.4864864864864864, 0.5135135135135135]`, fair odds `[2.0556, 1.9474]`. Exact to 1e-12 (`tests/test_session_8e9bf19f.py::BookmakerLineArithmetic`).

### 2.2 `1082919` Projeto do KinGui vs Martians — exchange row + book corroboration

- **Polymarket Gamma market 6033256, read 2026-10-22T08:52Z** ([gamma-api.polymarket.com/markets/6033256](https://gamma-api.polymarket.com/markets/6033256)): `outcomes ["Tropa do KinGui","Martians"]`, `outcomePrices ["0.66","0.34"]`, `bestBid 0.55`, `bestAsk 0.77`, `spread 0.22`, `liquidity 228.46`, `gameStartTime 2026-10-22 13:00:00+00`, `acceptingOrders true`, resolution source `https://hltv.org`. The market is live, named, and starts at Hotspawn's stored 13:00Z.
- **Stavka.tv header, read 2026-10-22T09:02Z:** `П11.06` / `П27.26`, both Winline → de-vig `87.26% / 12.74%`, matching the stored backup receipt. Kickoff renders `09:00 22 октября` = 13:00Z under the same UTC−4 clock.
- **Published row:** `exchange_wide 75.0% / 25.0%`, pick Projeto do KinGui. It stays on the exchange by policy even though the book price is tighter and more extreme — see the irregularity in §4.1.

### 2.3 The three `model_vrs_mirror` rows

- **Page read, 2026-10-22T08:44Z:** [hltv.org/valve-ranking/teams](https://www.hltv.org/valve-ranking/teams) redirects to the dated view `…/2026/october/22` whose heading is **“Valve global ranking on October 22nd, 2026”**, listing 396 ranked teams with `(N Valve points)` per club — the exact page, heading and parse the stored evidence records (`ranking_teams_count 396`, `ranking_page_sha256 519060d0…`).
- **Arithmetic replayed** from the recorded points with Valve's published formula (`scripts/vrs.py`: Glicko RD 75, slope 0.7986): `1104/805 → 0.773250480009`, `1073/898 → 0.681368837323`, `719/438 → 0.762177602651` — each equal to the published value to 12 decimal places.
- **Cross-check against Valve's own file** (`data/vrs/standings_global_2026_10_05.md`): FORZE Reload #84 / 1100 → mirror #85 / 1104; ex-RUSTEC #92 / 1066 → #91 / 1073; Isurus #173 / 783 → #200 / 719; Saint Sinners #158 / 810 → #133 / 898. Ordering and magnitude are consistent with 17 days of movement, and **LFO 10, Hacha and Staqued are the three clubs absent from Valve's 2026-10-05 file** — exactly the rows the mirror tier exists for. This is a consistency check, not a re-read of each row's points (see §3).

## 3. What this session did **not** verify by hand

- **Per-club Valve point values on HLTV's 396-row table.** The table paginates at roughly four clubs per rendered chunk; paging to #85, #91, #133, #157, #200 and #378 was out of budget. Those six values rest on the collector's recorded page hash plus the exact arithmetic replay in §2.3 and the validator, **not** on a second human read today. They are model inputs, not market prices.
- **Pinnacle / Thunderpick / GG.BET** access was not retried by this session; their adapters' `403` and “no validated quote” outcomes are carried over from the refresh run and are displayed per row as rejected or failed observations.
- **No source was fetched through the refresh pipeline by this session.** This environment reaches `hltv.org`, `stavka.tv` and the Polymarket Gamma API through the page fetcher only; `python -m scripts.refresh` was not run here, so the snapshot's own collection receipts are unchanged.

## 4. Irregularities flagged for review

Published on the site's **Flagged for Review** page through `data/review-notes.json`.

1. **`1082919` published percentage is a wide-book midpoint that has since moved.** The stored observation (07:38Z) used bid `0.54` / ask `0.96` (midpoint 75.0%); by 08:52Z the same market quoted `0.55` / `0.77` (midpoint 66.0%) with spread `0.22`. The pick is unaffected and the row is labelled *low confidence*, but the number a reader sees is the 75% midpoint of a 42-cent-wide book, not the current 66% mid. The Winline backup on the same fixture (1.06 / 7.26) implies 87.3% — a 12-point spread across two sources. Nothing is overwritten here; the row keeps its dated observation and expires at 15:38Z unless re-observed.
2. **`1079654` directional disagreement.** Winline prices ex-RUSTEC a marginal favourite (48.65% / 51.35%), while HLTV's world ranking has ex-Zero Tenacity one place higher (#67 vs #70) and the morning's research-only pick was ex-Zero Tenacity. The book tier outranks the ranking tier by policy, so the published pick flipped to **ex-RUSTEC at 51.35%**. It is a coin flip priced by one bookmaker at a 8.19% overround; it should be read as such.
3. **“0 unresolved” is precise but can be misread.** No open row lacks a pick; two rows (`1082925` BESTIA Academy vs RED Canids Academy, `1082860` FlyQuest vs Staqued) carry a research-only pick with a blank percentage. The summary renders `unresolved 0` next to `missing 2` and names both rows with their per-source limitations, so the page does not claim a percentage it does not have — verified in the built `index.html`, not just in the data.

## 5. Verification performed on the integrated build

- `python -m unittest discover -s tests` — **853 tests OK** (843 inherited + 10 from this session).
- `python -m unittest discover -s audits -p 'test_*.py'` — 9 OK; `verification-95b588c2/test_integrity.py` — 5 OK; `verification-c6` — 12 OK.
- `python -m scripts.build --data data/latest.json` — 9 primary pages + 6 legacy redirects; `python -m scripts.validate` on `public/` and on the root fallback — 107 rows, 41 calculations, 15 pages, 964 links/assets, 20 checksums, 283 displayed rows, no errors.
- `npm run test:browser` — 32 viewport/accessibility/no-overflow scans at 320/390/768/1440px, 7 expiry scenarios, 8 phone/desktop/queue/unresolved scenarios, plus the first-screen CTA test (44px tap target, first pick list within 1700px at 320px).
