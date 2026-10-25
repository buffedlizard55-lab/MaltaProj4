# Session bd650209 — independent reproduction, repair verification, and phone evidence

Everything here was measured, not recalled. Sources are linked at the bottom. No pick, price or
probability was edited by hand, and no value was inferred, reconstructed or filled in.

## 1. What was wrong, and how it was proved

The public board had withheld **every** pick since the `2026-10-25T01:47:42Z` snapshot aged out of its
eight-hour evidence window. Two scheduled publication runs failed in the same step, so
`upload-pages-artifact`, the legacy `main:/` root staging and `deploy` were skipped:

| Run | Event | Failing `verify-build` step | `deploy` |
| --- | --- | --- | --- |
| [40193317196](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40193317196) (12:29Z) | schedule | *Build and independently verify every row, calculation and internal link* | failed at *Verify live Pages bytes match this exact build* |
| [40170923727](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40170923727) (06:56Z) | schedule | same | same |

Action logs are not downloadable from the authoring sandbox (only `github.com`, `api.github.com`,
`registry.npmjs.org` and `pypi.org` are reachable), so this session ran the **real, unmodified pipeline**
on a GitHub runner and committed the receipts. The gate is data-dependent: the green push run of
`6ade440` did not carry a fresh refresh, so it could not see it.

## 2. Reproduction on a runner (run 40198565605, non-publishing)

`research/session-bd650209/receipt.json` records one exit code per step:

| Step | rc |
| --- | --- |
| `scripts.refresh` (real official-source read) | 0 |
| `scripts.quarantine` | 0 |
| `verification-c6/audit_snapshot.py runtime/latest.json` | **0 — 78 rows, 0 failures** |
| `scripts.build` | 0 — 78 rows, 16 open, 16 with percentages, 0 unresolved |
| `scripts.validate` | **1** |
| `verification-c6/audit_snapshot.py public/data/latest.json` | 0 |
| `unittest discover -s tests` | 0 |
| per-row replay (`diagnose.py`) | **1** |

Captured snapshot: `2026-10-25T13:56:28.969391Z`, fixtures observed `13:52:54Z`, coverage `verified`
(api 78 / lobby 78 / page 78 / retained 78). The whole capture is committed as
`captured-snapshot.json`, so every number below can be re-derived offline.

The pre-fix failure, named row by row (`logs/row-diagnosis.txt`):

```
priced rows replayed one at a time: 17
rows failing the repository validator: 1
FAIL 1086697 | Projeto do KinGui vs Yawara | model_vrs | Model roster has no HLTV source on this row
     vrs_teams       : ['ex-Keyd Stars', 'Yawara']
     roster_checks   : [{"lineup": ["drg","ALLE","ckzao","xureba","lash"], "overlap": 4, ...}, ...]
     hltv lineups    : [('Tropa do KinGui', 5), ('Yawara', 5)]
```

`scripts/validate.py` re-checked the model row's roster against the HLTV lineup by literal normalised
name. Hotspawn labels the club *Projeto do KinGui*; HLTV's own page for the same fixture labels it
*Tropa do KinGui*. The two labels are one club in `data/identities.json` — an alias record whose own
sources are HLTV match 2399904, Polymarket market 6033256 and Valve's #144 ex-Keyd Stars roster sheet —
so the evidence was correct and could never match. One row therefore turned the whole publisher red.

## 3. The repair was landed by another session; this session verified it independently

`main` `06915a8` (PR [#316](https://github.com/buffedlizard55-lab/MaltaProj4/pull/316), session
b85ad9b4) replaced the literal comparison with `same_club()`, which resolves both labels through
`core.norm` — the register of **sourced** aliases only. This session did not edit that code; it
verified it on its **own** capture, which the fix's author never saw:

| Gate, on the same committed snapshot `13:56:28Z` | Before the fix | After the fix |
| --- | --- | --- |
| `scripts.validate --data captured-snapshot.json` | rc **1** (row 1086697) | **rc 0** — 78 rows, 16 calculations, 15 pages, 751 links, 20 checksums |
| `verification-c6/audit_snapshot.py captured-snapshot.json` | 0 failures | 0 failures — 78 rows |
| `scripts.build` | 16/16 percentages | 16 with percentages, 0 without, **0 unresolved** |
| `verify_board.py` (this session) | — | **16 of 16 rows pass every re-derived check** |
| `unittest discover -s tests` | — | **1,619 tests OK** (7 skipped) |
| Chromium suites (`npm run test:browser`) | — | **all 13 suites pass** |

Independent check of the repair's *narrowness*, run here against the register itself: of the 31 alias
records, **no two registered clubs collapse together** under the new comparison; `Acend` vs
`Acend Academy` (an unregistered suffix pair) stays distinct; `LOS NINOS` vs `Los Niños` folds as
before. The rule "a roster claim must name its HLTV page" is unchanged.

## 4. Coverage of every match at that capture

78 Hotspawn CS2 feed rows · **16 open · 16 picks · 16 win probabilities · 0 unresolved**.
Ladder used: 10 exchange · 1 wide exchange · 1 researched book listing · 4 originated Valve-VRS model
lines. Events: CCT Europe 2026 Series #12, CCT South America 2026 Series #7, Circuit X Curitiba #4,
DFRAG Invitational 2026, Moscow Cyber Games 2026, NODWIN Clutch Series #13, Tesla Cup 2026.

The four matches **no exchange or book listed** — exactly the low-tier case in the brief — carry a
labelled originated line built from Valve's official standings, never from Hotspawn:

| Fixture | Match | Our line | Pick | Why no market line |
| --- | --- | --- | --- | --- |
| [1079200](https://www.hotspawn.com/matches/color-vs-ex-zero-tenacity-nodwin-clutch-series-13-1079200) | Color vs ex-Zero Tenacity | 68.8% / 31.2% | Color | Polymarket parent event is `ended=true`; the exchange price cannot be used |
| [1086697](https://play.hotspawn.com/cs2-pickems) | Projeto do KinGui vs Yawara | 51.0% / 49.0% | Projeto do KinGui | No market found; originated from Valve standings (roster overlap 4/5 on both sides) |
| [1082792](https://www.hotspawn.com/matches/hotu-vs-the-huns-moscow-cyber-games-2026-1082792) | HOTU vs The Huns | 85.2% / 14.8% | HOTU | Exchange quote outside the spread/liquidity gate; no Pinnacle listing |
| [1082793](https://www.hotspawn.com/matches/5star-vs-1win-moscow-cyber-games-2026-1082793) | 5star vs 1WIN | 24.3% / 75.7% | 1WIN | Exchange spread above the 60-point ceiling; no Pinnacle listing |

Every row, its two percentages, its pick, its method, its fair odds and its source link is re-derived
in `VERIFICATION.md` (generated by `verify_board.py`, machine JSON in `verification.json`).
The verifier is falsifiable: `tests/test_session_bd650209.py` proves that a flipped pick, a broken sum,
wrong fair odds, a missing source link, an impossible percentage and an already-locked row each fail
the check that covers them.

## 5. Phone evidence, measured in Chromium against this build

`measure_phone.cjs` → `phone-measurements.json`. The executive summary sits **above the pick list** on
a phone, and the first pick's two percentages clear the fixed tab bar:

| Viewport | Executive summary | First pick row | Both percentages above the tab bar | Sideways scroll |
| --- | --- | --- | --- | --- |
| 320×568 | quick nav at y=290 with *16/16 picks · 0 unresolved*, *Updated picks →*, *Unresolved & limits ↓* | picks.html y=280 | yes — percentage pair ends 452 < tab bar 507 | none |
| 390×844 | quick nav at y=300, same in-site links | picks.html y=243 | yes — 421 < 783 | none |
| 414×896 | quick nav at y≈300 | picks.html y≈243 | yes | none |

`index.html` first screen at 320 px reads *Executive summary* → *CS2 picks & probabilities* → the
one-line completeness caption → the two tap targets, in that order. The separate unresolved section is
`unresolved.html` (`#unresolved-limits`, `#unresolved-summary`) and is linked from the quick nav, the
executive bar and the footer.

## 6. Irregularities flagged for review (non-blocking)

1. **Two open rows link to the lobby, not to a fixture page.** Fixtures 1086696 and 1086697 carry
   `https://play.hotspawn.com/cs2-pickems` as their row link because the inventory this run read linked
   no per-fixture page for them. The link is official Hotspawn and no slug was invented. Published as
   `session-bd650209-fixture-page-link-missing-2026-10-25` on Flagged for Review.
2. **All 16 open rows have `best_of: null`.** The Hotspawn feed does not state the series format; it is
   left blank rather than inferred, as the repository's rule requires.
3. **Fixture 1082858 (Ground Zero vs Off Chops)** is priced from a Polymarket quote whose spread is
   23 points — inside the strict 25-point gate, but it carries the *wide spread; low precision* warning.
4. **Fixture 1082859 (NEXVOID vs Alter Ego)** uses a researched Thunderpick listing read through the
   BO3.gg API; the listing supplies no operator price-update timestamp, so only the observation time is
   published.
5. **All four originated lines rest on Valve's `2026-10-05` global standings** (20 days old at that
   capture, inside the published 62-day rule). They are model estimates, labelled as such on every row,
   and are not market prices.
6. **Source limitations seen in the attempts ledger on these rows:** GG.BET answered HTTP 403 after three
   documented rate-limit waits, and the Thunderpick adapter extracted no validated two-sided series
   quote. Both are recorded as collection limitations, never as evidence that no line exists.

## 7. What this session did not do

It did not edit `scripts/validate.py` (another session's landed repair, verified here instead), did not
touch `pages.yml`, and did not regenerate the root pages by hand — the publisher rebuilds them from a
fresh snapshot, which is the only path that can also clear the eight-hour expiry window.

## 8. Sources

- Failing runs: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40193317196 ·
  https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40170923727 ·
  https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40143667147
- This session's reproduction run (non-publishing): https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40198565605
- The landed repair: PR https://github.com/buffedlizard55-lab/MaltaProj4/pull/316 (commit `06915a8`)
- Hotspawn inventory: https://play.hotspawn.com/lobby · https://play.hotspawn.com/cs2-pickems ·
  fixture feed `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`
- Identity evidence for the failing row:
  https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7 ·
  https://gamma-api.polymarket.com/markets/6033256 ·
  https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0144--ex-keyd_stars--ckzao-drg-lash-xureba-zede.md
- Exchange quotes (examples): https://gamma-api.polymarket.com/markets/6066508 ·
  https://gamma-api.polymarket.com/markets/6066525 · https://gamma-api.polymarket.com/markets/6158760
- Originated-line inputs: https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md
- Book listing: https://api.bo3.gg/api/v1/matches?page[offset]=0&page[limit]=100&filter[matches.status][in]=upcoming&filter[matches.discipline_id][eq]=1&sort=start_date&with=teams,tournament
