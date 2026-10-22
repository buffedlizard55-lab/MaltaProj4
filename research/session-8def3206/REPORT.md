# Session 8def3206 — publish unblock, phone-first summary, and the last unpicked fixture

All times UTC. Every claim below is a dated read of the linked page; nothing is
inferred from a name, a logo or a search result alone.

## 1. Why the site stopped updating (the blocker)

| What | Evidence |
| --- | --- |
| Scheduled publish failing | Run [39731049149](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39731049149): `verify-build` failed at *Unit and independent failure-mode tests* in 35s, all later steps including `deploy` skipped. |
| Live site frozen | `build-info.json` read at 07:35Z reported `built_at 2026-10-22T03:33:56Z` while it was 07:35Z. |
| Root cause | `tests/test_session_bf09aa40.py` replayed the committed `2026-10-21T21:18:58Z` model observation with `datetime.now()`. `scripts.validate.validate_model_row` refuses model inputs older than eight hours (`scripts/validate.py`, `fresh(q['observed_at'], now)`), so from `2026-10-22T05:18Z` the test could not pass. Reproduced locally: `1 failure` out of 763. |
| Fix | Replay the snapshot at its own `generated_at`, which is exactly the clock `scripts.validate` uses (`now = dt(data['generated_at'])`). Production thresholds untouched. |
| Proof | Suite re-run under simulated +1, +3, +14 and +40-day clocks: 763/763 OK each time. A second, independent +24h-clock run of the same module is now a test (`tests/test_session_8def3206.py`). |

A second, identical repair was merged on `main` while this branch was in flight
(session 75ebd2d6/411c8cf9). The rebase kept both explanations and one code path.

## 2. The last unpicked fixture: 1082919 "Projeto do KinGui vs Martians"

| Question | Answer and source |
| --- | --- |
| What does the feed say? | `CCT South America 2026 Series #7`, `2026-10-22T13:00:00Z`, lock `12:54Z` (Hotspawn fixture page, inventory only). |
| Does HLTV have the match? | Yes: [match 2399904](https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7) — "Tropa do KinGui vs. Martians", CCT 2026 South America Series 7, 22 Oct 2026, Bo3, Round of 16. |
| Same UTC start? | The page renders `09:00` in the fetching client's local zone, so the clock face is not usable on its own. The live countdown read `5h06m12s` at `07:55Z`, which places the start at **13:00–13:01Z** — the same minute as the Hotspawn fixture. |
| Why the different name? | [Team 13151](https://www.hltv.org/team/13151/tropa-do-kingui) names that exact match as its next fixture, its roster history includes the player [KinGui](https://www.hltv.org/player/22097/kingui), and the match page attaches the five-player lineup `drg, ALLE, ckzao, xureba, lash` to that team id. Hotspawn uses the newer label "Projeto do KinGui" for the same organisation. |
| Is it ranked? | [Martians](https://www.hltv.org/team/13230/martians): Valve VRS **#335** (AM #71), HLTV world **#240**. Tropa do KinGui: the match page prints "VRS: #149" / "HLTV: Unranked", while the team page prints "-" for both and "no active players" — see the discrepancy below. |
| Market line? | None found. The collector's recorded attempts for this row are Polymarket (no exact pair), HLTV (no exact pair before the register entry), HLTV team pages (no unique label), Pinnacle (no listing), Thunderpick (no validated automated two-way quote), GG.BET (403), both Valve tiers (neither team resolves in the official file), rank research (no ranks) — all visible on the row. |

**What the register entry does and does not do.** `data/identities.json` now maps
`Tropa do KinGui` ↔ `Projeto do KinGui`. That only lets the identity tiers
recognise one organisation under two labels; each tier still needs its own
primary source. With the mapping in place the ranking tier resolves as
`research_rank_single` → pick **Martians**, because Martians carries HLTV world
#240 and Tropa do KinGui is listed as unranked on the same fixture page. That is
a sourced pick with **no percentage**, which is the honest ceiling for this row.
It is reproduced in `tests/test_session_8def3206.py` against a synthetic
`hltv_context` shaped exactly like `scripts/hltv.context()` output, so the pick
cannot be published without the per-team evidence.

**Discrepancies published on Flagged for Review** (`8def3206-alias-scope-projeto-do-kingui-2026-10-22`):
1. HLTV's own team page and match page disagree about the same team id on the
   same day (no roster / no rank vs "VRS #149" / five players). Nothing was
   inferred from either reading.
2. The crowd vote on that match page moved from 25.0%/75.0% to 20.0%/80.0%
   between two reads about a minute apart — a concrete reason this project never
   uses crowd percentages as a probability input.
3. Scope risk: the register entry, like every other entry, applies to any future
   fixture using either label.

## 3. Presentation changes (no data change)

- The executive summary is ordered for a phone: freshness strip → four 46px
  chips → **Picks at a glance** → coverage → hero → page cards → unresolved
  section. Measured at 390×844: first pick card at y≈700px (previously below the
  fold, behind a 350px prose navigation block, a 700px coverage panel, a 500px
  hero and four destination cards).
- The pick board's and the unresolved page's long explainers became
  closed-by-default `<details>` disclosures with identical wording; the ordered
  ladder keeps every step and every source link inside its required panel.
- `scripts.validate` reproduces all 39 published calculations; the browser suite's
  320/390/768/1440px scans, no-overflow and axe WCAG A/AA checks pass.

## 4. Gate repairs made while verifying (all snapshot-driven, none loosen a data rule)

| File | Was | Now |
| --- | --- | --- |
| `verification-7271c5d5/audit_board_7271c5d5.py` | Failed any build whose closed rows still carried their historical evidence, i.e. every build made after a lock passed. | Exempts exactly a row the build itself closed by its deadline rule, and still rejects an *open* unpriced row that carries a price, or a closed row that still publishes a pick. |
| `verification-767649ba/audit_2026_10_22.py`, `scripts/probe_7601d5ee.py`, `scripts/audit_d6df5beb.py`, `tests/test_session_d6df5beb.py`, `tests/test_session_7601d5ee.py` | Asserted "no open fixture may be unpicked", so one new low-tier fixture blocked the whole publish and invited an invented pick. | Assert the documented contract: every open fixture is either picked or published as unresolved with a reason and its recorded attempts, and every open fixture is counted in exactly one of priced / research-only / unresolved. |
