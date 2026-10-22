# Session `cb867c3c` — Live Coverage Audit, Primary-Source Line Upgrades & Refresh Hardening (2026-10-22)

## Executive Summary

On `2026-10-22` (`07:42Z–08:15Z`), `origin/main` carried:
1. **Unpicked open match `1082919` (`Projeto do KinGui vs Martians`, `2026-10-22T13:00:00Z`)**, caused by unmapped team identity between Hotspawn (`Projeto do KinGui`) and HLTV / Polymarket (`Tropa do KinGui`).
2. **Cloudflare `HTTP 403` rate-limit sleep overhead (`3 x 100s = 300s`)** when plain `urllib3` TLS probed `www.hltv.org` and `egamersworld.com`.
3. **Three latent live-refresh timebombs on `main`:**
   - `tests/test_coverage_76712ccc.py` omitted `'model_vrs_mirror'` from its priced-method allowlist (`('exchange', 'exchange_wide', 'book', 'bookmaker_fallback', 'model_vrs')`), causing any committed snapshot containing live `model_vrs_mirror` rows (`1081149`, `1081150`, `1082926`) to fail Step 7 of `pages.yml`.
   - `tests/test_session_75ebd2d6.py` pinned exact point-in-time snapshot counts (`(35, 46)` open / `(97, 107)` total) and `probabilities is None` on rows that upgrade on subsequent live refreshes.
   - `verification-7271c5d5/audit_board_7271c5d5.py` treated post-lock build-time historical evidence rows (`Source start or pick lock has passed.`) as errors whenever a refresh crossed a `:54` lock boundary.

## Verified `2026-10-22T07:58:54.670274Z` Board Results (`107` Total, `43` Open)

- **Open matches with verified picks:** **`43 / 43` (`100.0%`, `0` unresolved)**
- **Open matches with reproducible numerical win probabilities & fair decimal odds:** **`41 / 43` (`95.3%`)**:
  - `exchange` (strict Polymarket CLOB `<= 25` pt spread): **`22`**
  - `exchange_wide` (Polymarket wide tier `<= 60` pt spread, low-confidence flag): **`3`** — including **`1082919 Projeto do KinGui vs Martians`** (`75.0% / 25.0%` via [Polymarket market 6033256](https://gamma-api.polymarket.com/markets/6033256), corroborated by licensed bookmaker backup `Winline 1.06 / 7.26` -> `87.2% / 12.8%`)
  - `bookmaker_fallback`: **`3`** — Pinnacle `1082920` (`45.3% / 54.7%`), Pinnacle `1082921` (`16.9% / 83.1%`), and **`1079654 ex-Zero Tenacity vs ex-RUSTEC`** (`48.6% / 51.4%` from live Winline moneyline `П1 1.90 / П2 1.80` on [Stavka.tv](https://stavka.tv/matches/csgo/23-10-2026-ex-zero-tenacity-ex-rustec), automated in `scripts/books.py`)
  - `model_vrs` (official Valve Regional Standings file): **`10`**
  - `model_vrs_mirror` (HLTV dated `2026-10-22` Valve ranking mirror): **`3`** (`1081149 FORZE Reload vs LFO 10` `77.3% / 22.7%`, `1081150 ex-RUSTEC vs Saint Sinners` `68.1% / 31.9%`, `1082926 Isurus vs Hacha` `76.2% / 23.8%`)
- **Open qualitative HLTV research picks (blank percentage, zero guessed numbers):** **`2 / 43`** (`1082925 BESTIA Academy vs RED Canids Academy` -> `RED Canids Academy`, HLTV `#170` vs `#184`; `1082860 FlyQuest vs Staqued` -> `FlyQuest`, HLTV `#61` vs unranked)

## Merged PRs & Live `main` Verification Receipts

1. **PR [#175](https://github.com/buffedlizard55-lab/MaltaProj4/pull/175)** — merged to `main` as `f75054d8601127f62a36c605ef0941e62a4eb59c` (`verify-build` run `39748441916` green in `1m38s`).
2. **PR [#183](https://github.com/buffedlizard55-lab/MaltaProj4/pull/183)** — merged to `main` as `43e49ad0fe5e0c5f40eb15d043de8d5395f407f8` (`verify-build` run `39751709560` green in `2m31s`): preserved `requests.Response` when `curl_cffi` `HTTP 403` fallback also receives `>= 400` (`GG.BET fallback access`), verified live in `main` run `39755946440` where all live refresh, independent withhold/audit, link validation, and Playwright viewport/accessibility steps passed 100% green.
3. **PR [#189](https://github.com/buffedlizard55-lab/MaltaProj4/pull/189)** — merged to `main` as `6d8a2ffc5db3a497ea6bb7be6fca16a1d9da051a` (`verify-build` run `39758628888` green), unblocking live `main` run `39761026666` (`completed|success`, root fallback commit `3b21d18` + live `actions/deploy-pages` deployment).
4. **Dated HLTV Valve ranking mirror fix across independent auditors (`verification-c6/audit_snapshot.py:204`, `verification-4901f43e/audit_published_claims.py:426`):** Fixed exact-path rejection of `/valve-ranking/teams/YYYY/month/D` that falsely withheld `1081149`, `1081150`, and `1082926` in `3b21d18`, restoring all three live `2026-10-22T10:12:19.607253Z` (`sha256: c88fd2fff49b45ef755dca9fccf3949a8bd695d5694f4bff832c7c2302f40355`) `model_vrs_mirror` rows on the live `2026-10-22T10:15:59.388662Z` board (**`104` total rows, `43 / 43` = `100.0%` open picks, `42 / 43` = `97.7%` reproducible numerical probabilities, `1` `research_rank_single` [`1082860`], `0` unresolved, `935 / 935` unit tests `OK`**).

