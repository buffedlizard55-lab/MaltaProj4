# Session 6857421f — the 2026-10-25 publisher failure, repaired and republished

**Clock of this report:** 2026-10-25T13:35–14:05Z. **Branch:** `arena/6857421f-maltaproj4`
(Arena-fixed; no other branch is created, switched to or pushed).

## 1. What was actually wrong (measured, not inferred)

The user-visible report was "we have no picks". It was not a source outage and it was not a
missing price: the public site was serving the `2026-10-25T01:47:42Z` snapshot, and the board's
own `stale_after_hours` is 8, so every pick had been withheld since 09:47Z.

| Fact | Value | How it was read |
| --- | --- | --- |
| Public build served | `built_at 2026-10-25T01:47:42.715221Z`, snapshot `01:47:42.430039Z`, 79 rows | `https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json` |
| Board freshness policy | `stale_after_hours: 8`, `refresh_hours: 1` | `data/latest.json` |
| Snapshot age at 13:26Z | 11 h 38 m → withheld | clock read |
| Last green publisher | [40151731896](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40151731896) (01:43Z) | Actions API |
| Red publisher runs | [40170923727](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40170923727) (06:56Z), [40193317196](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40193317196) (12:29Z) | `/actions/runs/<id>/jobs` |
| Failing step (both) | *Build and independently verify every row, calculation and internal link* | same |
| Steps that had already passed | unit gate, live refresh, quarantine | same |

That step runs four commands. Actions log blobs
(`results-receiver.actions.githubusercontent.com`, `productionresultssa*.blob.core.windows.net`)
are outside this sandbox's egress allow list, so the failing command was named by a
non-publishing runner replay that committed its own receipt
([`research/diag-6857421f/00-return-codes.txt`](../diag-6857421f/00-return-codes.txt)):

```
pre_unit_rc=0        pre_validate_rc=0
refresh_rc=0         quarantine_rc=0
row_audit_rc=0       build_rc=0
published_validate_rc=1        <-- the failure
published_row_audit_rc=0       browser_rc=1
```

```
scripts/validate.py:122 AssertionError: Model roster has no HLTV source on this row
```

## 2. Defect A — the validator compared team labels as raw text

The capture in that receipt is `2026-10-25T13:34:30Z` (78 feed rows, 17 open, 17 picks, 17
probability pairs, 0 unresolved). The failing row was fixture **1086697**, Hotspawn's
*Projeto do KinGui* vs *Yawara*, competition *CCT South America 2026 Series #7*, start
`2026-10-25T19:00:00Z`.

Its ladder, in the order the site publishes it (every step is in the row's own `attempts`):

| Rung | Result | Source |
| --- | --- | --- |
| Polymarket strict exchange | refused — market `6169151` is *Tropa do KinGui vs Yawara Esports*; the **opponent** label *Yawara Esports* is not in the reviewed alias register, and no fuzzy match is allowed | [gamma-api.polymarket.com/markets/6169151](https://gamma-api.polymarket.com/markets/6169151) |
| HLTV | no numeric two-way line in the response (identity, ranking and lineups only) | [hltv.org/matches/2399918](https://www.hltv.org/matches/2399918/tropa-do-kingui-vs-yawara-cct-2026-south-america-series-7) |
| Pinnacle | no exact pair and UTC start in the feed | [guest.api.arcadia.pinnacle.com](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight) |
| Thunderpick / GG.BET / BO3.gg | no validated series quote; GG.BET HTTP 403 after three paced waits | [bo3.gg](https://bo3.gg/matches/tropa-do-kingui-vs-yawara-esports-25-10-2026) |
| **Our own Valve-VRS model line** | **resolved** — Projeto do KinGui 51.0% / Yawara 49.0%, pick *Projeto do KinGui* | [Valve standings 2026-10-05 @ eec4853](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |

The model tier's roster identity comes from that HLTV fixture page, where the same five players
(`drg, ALLE, ckzao, xureba, lash`) are printed as **Tropa do KinGui**. `scripts/validate.py`'s
`lineup_source_ok` compared the two labels with `plain_name`, so a correctly sourced roster was
reported as unsourced — the same class of defect the repo has already fixed for every other
identity assertion, which use `norm()` and the reviewed register in `data/identities.json`
(31 entries, each with an https source and a written basis).

**Repair.** `lineup_source_ok` now compares team labels with `norm()` in all three of its paths
(fixture lineups, retained lineup receipts, HLTV team pages). Everything that carries evidence
stays exact: the player names, the `https://www.hltv.org/matches/` and
`https://www.hltv.org/team/` prefixes, and the receipt's own fixture/team binding. An
**unregistered** label is still refused, and a registered alias does not license a different
roster — both are regressions in `tests/test_session_6857421f.py`.

## 3. Defect B — the phone card printed the team names twice

The same replay recorded `browser_rc=1` from `tests/browser_019a253a.cjs:105`, *"the first
probabilities must clear the tab bar at 320x568"*. Reproduced locally on the captured board and
measured in Chromium:

| Viewport | First card | pick bottom | probability-pair bottom | fixed tab bar top | verdict |
| --- | --- | --- | --- | --- | --- |
| 320x568, before | `1085542` ex-Zero Tenacity vs Spirit Academy | 443 | **519** | 507 | 12 px behind the bar |
| 320x568, after | same | 443 | **483** | 507 | clear |
| 390x844, after | same | 357 | 401 | 783 | clear |

The cause is duplication, not a missing number: the phone card printed both team names in its
heading *and* again inside the probability block, where "ex-Zero Tenacity" wraps to two lines in
a 48%-wide slot. The duplicate is now hidden inside phone cards only
(`@media(max-width:650px){tbody .prob-team-labels{display:none}}`); each percentage keeps its own
`aria-label` naming its team, and the heading still names both teams. No percentage, fair-odds
line, model comparison, flag, warning or source link is hidden. Both stylesheet copies are
byte-identical and balanced (a standing repository contract).

## 4. Full-coverage ledger for this capture — every open row, its pick and its source

All 17 open matches have a pick, two probabilities that sum to 1, and a link to the official
source that produced the number. Re-derived independently by
`verification-c6/audit_snapshot.py` (**0 failures**, table in
[`05-row-audit.md`](../diag-6857421f/05-row-audit.md)) and again by `scripts.validate`
(17 calculations reproduced).

| # | Hotspawn fixture | Start (UTC) | Our pick | Win probability (both teams) | Tier | Official source used |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [ex-Zero Tenacity vs Spirit Academy](https://www.hotspawn.com/matches/ex-zero-tenacity-vs-spirit-academy-cct-europe-2026-series-11-1085542) | 2026-10-25T14:00:00Z | **ex-Zero Tenacity** | ex-Zero Tenacity 56.5% / Spirit Academy 43.5% | exchange | [Polymarket](https://gamma-api.polymarket.com/markets/6158059) |
| 2 | [Infinite vs BRUTE](https://www.hotspawn.com/matches/infinite-vs-brute-nodwin-clutch-series-13-1079199) | 2026-10-25T15:00:00Z | **BRUTE** | Infinite 43.5% / BRUTE 56.5% | exchange | [Polymarket](https://gamma-api.polymarket.com/markets/6072808) |
| 3 | [BORRACHEIROS vs RED Canids Academy](https://play.hotspawn.com/cs2-pickems) | 2026-10-25T16:00:00Z | **RED Canids Academy** | BORRACHEIROS 42.5% / RED Canids Academy 57.5% | exchange | [Polymarket](https://gamma-api.polymarket.com/markets/6158760) |
| 4 | [Color vs ex-Zero Tenacity](https://www.hotspawn.com/matches/color-vs-ex-zero-tenacity-nodwin-clutch-series-13-1079200) | 2026-10-25T18:00:00Z | **Color** | Color 68.8% / ex-Zero Tenacity 31.2% | model_vrs | [Valve VRS model](https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |
| 5 | [FORZE Reload vs ex-RUSTEC](https://www.hotspawn.com/matches/forze-reload-vs-ex-rustec-cct-europe-2026-series-12-1081158) | 2026-10-25T18:00:00Z | **FORZE Reload** | FORZE Reload 56.5% / ex-RUSTEC 43.5% | exchange | [Polymarket](https://gamma-api.polymarket.com/markets/6098416) |
| 6 | [BESTIA vs paiN](https://www.hotspawn.com/matches/pain-vs-bestia-circuit-x-curitiba-4-1082697) | 2026-10-25T18:00:00Z | **paiN** | BESTIA 42.5% / paiN 57.5% | exchange | [Polymarket](https://gamma-api.polymarket.com/markets/6166390) |
| 7 | [Projeto do KinGui vs Yawara](https://play.hotspawn.com/cs2-pickems) | 2026-10-25T19:00:00Z | **Projeto do KinGui** | Projeto do KinGui 51.0% / Yawara 49.0% | model_vrs | [Valve VRS model](https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |
| 8 | [Ground Zero vs Off Chops](https://www.hotspawn.com/matches/ground-zero-vs-off-chops-dfrag-invitational-2026-1082858) | 2026-10-26T03:00:00Z | **Off Chops** | Ground Zero 36.5% / Off Chops 63.5% | exchange | [Polymarket](https://gamma-api.polymarket.com/markets/6066508) |
| 9 | [NEXVOID vs Alter Ego](https://www.hotspawn.com/matches/nexvoid-vs-alter-ego-dfrag-invitational-2026-1082859) | 2026-10-26T03:00:00Z | **NEXVOID** | NEXVOID 57.9% / Alter Ego 42.1% | bookmaker_fallback | [Thunderpick (via BO3.gg API)](https://api.bo3.gg/api/v1/matches?page[offset]=0&page[limit]=100&filter[matches.status][in]=upcoming&filter[matches.discipline_id][eq]=1&sort=start_date&with=teams,tournament) |
| 10 | [FlyQuest vs Staqued](https://www.hotspawn.com/matches/flyquest-vs-staqued-dfrag-invitational-2026-1082860) | 2026-10-27T03:00:00Z | **FlyQuest** | FlyQuest 92.0% / Staqued 8.0% | exchange | [Polymarket](https://gamma-api.polymarket.com/markets/6066520) |
| 11 | [Rooster vs Abyssal](https://www.hotspawn.com/matches/rooster-vs-abyssal-dfrag-invitational-2026-1082861) | 2026-10-27T03:00:00Z | **Abyssal** | Rooster 42.0% / Abyssal 58.0% | exchange_wide | [Polymarket](https://gamma-api.polymarket.com/markets/6066525) |
| 12 | [B8 vs K27](https://www.hotspawn.com/matches/b8-vs-k27-tesla-cup-2026-1082897) | 2026-10-27T08:00:00Z | **B8** | B8 59.5% / K27 40.5% | exchange | [Polymarket](https://gamma-api.polymarket.com/markets/6024944) |
| 13 | [Alliance vs FaZe](https://www.hotspawn.com/matches/alliance-vs-faze-tesla-cup-2026-1082898) | 2026-10-27T11:00:00Z | **FaZe** | Alliance 37.5% / FaZe 62.5% | exchange | [Polymarket](https://gamma-api.polymarket.com/markets/6024952) |
| 14 | [Luminosity vs HOTU](https://www.hotspawn.com/matches/luminosity-vs-hotu-tesla-cup-2026-1082900) | 2026-10-27T17:00:00Z | **Luminosity** | Luminosity 52.5% / HOTU 47.5% | exchange | [Polymarket](https://gamma-api.polymarket.com/markets/6024960) |
| 15 | [Envy vs GamerLegion](https://www.hotspawn.com/matches/envy-vs-gamerlegion-tesla-cup-2026-1082901) | 2026-10-27T20:00:00Z | **GamerLegion** | Envy 45.5% / GamerLegion 54.5% | exchange | [Polymarket](https://gamma-api.polymarket.com/markets/6037120) |
| 16 | [HOTU vs The Huns](https://www.hotspawn.com/matches/hotu-vs-the-huns-moscow-cyber-games-2026-1082792) | 2026-10-31T09:00:00Z | **HOTU** | HOTU 85.2% / The Huns 14.8% | model_vrs | [Valve VRS model](https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |
| 17 | [5star vs 1WIN](https://www.hotspawn.com/matches/5star-vs-1win-moscow-cyber-games-2026-1082793) | 2026-10-31T13:00:00Z | **1WIN** | 5star 24.3% / 1WIN 75.7% | model_vrs | [Valve VRS model](https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |

Snapshot `2026-10-25T13:34:30.593464Z` (fixtures observed `2026-10-25T13:30:57.777255Z`), 78 feed rows, 17 open, 17 picks, 17 probability pairs, 0 unresolved.

Method mix: 11 strict Polymarket exchange lines, 1 labelled wide exchange line, 1 researched
bookmaker listing (Thunderpick via the BO3.gg API), 4 originated Valve-standings model lines.
Hotspawn supplies the fixture inventory and locks only and is **never** a probability input; the
exchange/listing lines are de-vigged from both sides, and the model lines are labelled as our own
estimate wherever they appear.

## 5. Unresolved picks and their limitations (the separate section, as required)

On this capture the unresolved count is **zero**: no open row is left without a pick or a
probability. The section still renders (the site shows it even at zero, because "nothing is
missing today" is not a claim about tomorrow) and it publishes the whole ladder with a per-rung
count. Two honest limitations are carried with this capture anyway:

1. **Fixture 1086697 lost a verified market price to an unregistered opponent label.** Polymarket
   market `6169151` prices the fixture's exact UTC start, and the fixture side of the pair
   (*Projeto do KinGui* = *Tropa do KinGui*) is registered; *Yawara Esports* has no entry, so the
   pair was refused and the model line was used. Registering it needs a primary source tying
   *Yawara* to *Yawara Esports*; HLTV's fixture page prints only *Yawara*, so no alias was
   invented. Published on Flagged for Review as
   `session-6857421f-unregistered-opponent-labels-2026-10-25`.
2. **Two rows have no per-match Hotspawn page** (fixtures `1086696` and `1086697`): the lobby
   renders them without a match link, so their source link is the official CS2 pick'em page
   rather than an invented URL. This is the pre-existing, already-flagged class
   (`session-0cc1138a-1081606-no-match-page-2026-10-23`).

## 6. What was verified, line by line

| Gate | Result | Command |
| --- | --- | --- |
| Unit suite on this exact tree | **1,606 tests OK (12 skipped)** | `python -m unittest discover -s tests` |
| Audit suite | 9 OK | `python -m unittest discover -s audits -p 'test_*.py'` |
| Integrity | 5 OK | `python verification-95b588c2/test_integrity.py` |
| Independent C6 auditors | 12 OK | `python -m unittest discover -s verification-c6 -p 'test_*.py'` |
| Independent row audit on the capture | 0 failures across 78 rows | `python verification-c6/audit_snapshot.py …` |
| Validator (root, staged) | 78 rows / 17 calculations reproduced / 15 pages / 730 links / 20 checksums / 182 displayed rows | `python -m scripts.validate --data data/latest.json --site .` |
| Chromium suites | **13 suites pass** (32 page/viewport scans at 320/390/768/1440, expiry, ladder, phone placement) | `npm run test:browser` |
| Phone geometry | first pick at y=336/354 and both percentages above the tab bar at 320x568 / 390x844 | `tests/browser_019a253a.cjs`, `tests/browser_aeafcbe6.cjs` |
| Flagged for Review | 3 new source-linked notes rendered in `review.html` | `data/review-notes.json` |

## 7. Sources used in this session

* Actions API for every run cited above: `https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/actions/runs/<id>`.
* Hotspawn CS2 fixtures API and both lobby views, as re-read by the runner and recorded in
  [`research/diag-6857421f/snapshot-quarantined.json`](../diag-6857421f/snapshot-quarantined.json)
  (`source_checks` carries the URL, HTTP status, sha256 and observation clock of each).
* HLTV fixture page `https://www.hltv.org/matches/2399918/tropa-do-kingui-vs-yawara-cct-2026-south-america-series-7`.
* Polymarket Gamma API for each exchange row, cited per row in the ledger above.
* Valve's official `counter-strike_regional_standings` at commit `eec4853`, file
  `live/2026/standings_global_2026_10_05.md`, for the four model rows.
* The public site's own `build-info.json` for the withheld-state measurement.

**Not claimed:** this session cannot verify what happened inside the runner's job log (that host
is blocked here); the failing command is established from the replay's exit codes, which reproduce
the same step on the same code. Live deployment and the post-merge publisher run are recorded in
`COORDINATION.md` only once they are actually observed.
