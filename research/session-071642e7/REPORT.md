# Session `071642e7` — Full Hotspawn CS2 Coverage, Primary-Source Line-by-Line Verification & Mobile Dashboard Delivery

## 1. Root-Cause Diagnosis & Pipeline Hardening

1. **Why live Pages (`https://buffedlizard55-lab.github.io/MaltaProj4/`) showed `0 with a pick` at `2026-10-23T04:55Z`**:
   - Scheduled workflow runs `39871808909` (`2026-10-22T23:26:37Z`) and `39886171791` (`2026-10-23T01:49:32Z`) failed at `Unit and independent failure-mode tests` *before* `scripts.refresh` executed because historical session tests (`tests/test_session_13e99ca6.py`, `tests/test_session_75ebd2d6.py`) pinned obsolete snapshot IDs/methods. That froze `data/latest.json` at `2026-10-22T20:15:52Z`, causing client-side expiry protection to withhold stale picks once the 8-hour evidence window elapsed.
   - Furthermore, `.github/workflows/pages.yml` lacked a post-`publish_root_fallback` unit-test gate prior to the `cs2-scout-publisher` commit step, `scripts/session_b214c818.py` unconditionally rewrote `data/identities.json` with `indent=2` (breaking `test_session_cb867c3c.py`'s canonical `indent=1` check), and `.fresh-strip .fresh-state` wrapped above `.fresh-links` on `320×568` phones (`y = 593 > 568`, breaking `tests/browser_eaff7cce.cjs`).
2. **Fixes applied**:
   - `.github/workflows/pages.yml`: Preserved the `0 */4 * * *` (every 4 hours) schedule and added `python -m unittest discover -s tests` after `publish_root_fallback` and before `cs2-scout-publisher` commits to `main`.
   - `scripts/books.py`: Fixed `MAKE_BET_RE` and team-binding regexes (`ODD_NUM = r'\d+(?:\.\d+)?'`) so whole-integer decimal odds anchored to `Make a bet` (such as `FlyQuest 1.001 Make a bet 12 Staqued`) re-observe cleanly with `bound_to_labels=True`, while keeping generic `PAIR_RE` strict (`\d+\.\d+`) and preserving the `1.8 / 1.8` placeholder rejection.
   - `scripts/session_b214c818.py` & `data/identities.json`: Restored strict canonical `indent=1` formatting and gated file writes on actual additions so `unittest` never dirties `data/identities.json`.
   - `assets/style.css`: Set `.fresh-strip .fresh-state{font-size:10.5px;order:4}` under `@media(max-width:650px)` so the primary CTA inside `#freshness-strip` sits well above the `320×568` fold in both live and stale states.

## 2. Live Official-Source Harvest & 100% Open Match Coverage (`30 / 30` Picks & `30 / 30` Win Probabilities)

- Executed live GitHub Actions capture run [`39903552314`](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39903552314) (`generated_at: 2026-10-23T05:08:12.062394Z`, `fixtures_observed_at: 2026-10-23T05:04:38.562024Z`) archiving 30 gzipped SHA-256 primary HTTP responses under `research/session-071642e7/raw/`:
  - **Total Hotspawn CS2 fixtures retained**: `92` (`62 not_open`, `30 open`, `0` quarantined; Hotspawn crowd percentages never used).
  - **Open matches with verified picks**: **`30 / 30` (`100.0%`)**.
  - **Open matches with verified, reproducible win probabilities**: **`30 / 30` (`100.0%`)**:
    - `17` `exchange` (Polymarket strict two-sided CLOB, spread `<= 25` pts)
    - `2` `exchange_wide` (Polymarket labelled wide tier, `25 < spread <= 60` pts, flagged low confidence)
    - `1` `bookmaker_fallback` (`1082860 FlyQuest vs Staqued`, `DFRAG Invitational 2026` Group B BO3 at `2026-10-27T03:00:00Z`: HLTV match `2399890` + six live named sportsbooks on `EGamersWorld` [`Thunderpick 1.001 / 12.0` headline, `Rainbet 1.01 / 11.76`, `Underdog 1.01 / 12.01`, `CocoBet 1.02 / 11.91`, `FanDuel 1.01 / 12.02`, `Fanatics 1.02 / 11.97`], corroborated on `bo3.gg` at `1.001 / 12.0`, de-vigging to **`92.3% / 7.7%`**, fair odds **`1.083 / 12.988`**)
    - `9` `model_vrs` (Official Valve Regional Standings GitHub file `2026-10-05` + published Valve Glicko RD 75 / `0.7986` calibration)
    - `1` `model_vrs_mirror` (`1081149 FORZE Reload vs LFO 10`, `2026-10-23T08:00:00Z`: HLTV dated Valve ranking view `2026-10-23`, `1134` vs `1015` pts -> **`78.1% / 21.9%`**)

## 3. Flagged Irregularities Published on `review.html`

All four newly uncovered source/pipeline irregularities are recorded in `data/review-notes.json` and rendered on `review.html` with clickable primary-source URLs:
1. `071642e7-flyquest-staqued-polymarket-wide-clob-vs-6book-line-2026-10-23` — Polymarket `6066520` `0.07 / 0.95` (`88`-pt spread, `0.51 / 0.49` mid) properly rejected vs six live sportsbook lines (`92.3% / 7.7%`).
2. `071642e7-rooster-abyssal-polymarket-wide-clob-vs-vrs-2026-10-23` — Polymarket `6066525` `0.04 / 0.96` (`92`-pt spread, `0.50 / 0.50` mid) properly rejected vs official Valve standings `#88` (`1084` pts) vs `#157` (`803` pts) -> `83.9% / 16.1%`.
3. `071642e7-forze-reload-lfo10-hltv-dated-valve-mirror-2026-10-23` — `LFO 10` post-`2026-10-05` entry resolved via HLTV dated Valve ranking view `2026-10-23` (`78.1% / 21.9%`) and updated `2026-10-23T08:00:00Z` start time.
4. `071642e7-refresh-gate-identities-format-and-320px-fold-fixes-2026-10-23` — Pipeline unit gate ordering, `data/identities.json` `indent=1` preservation, and `320×568` fold layout fix.
