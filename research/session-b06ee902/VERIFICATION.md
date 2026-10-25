# Independent audit of the 25 October 2026 board — session b06ee902

**Scope.** Re-verify the picks the site is publishing against the primary sources themselves, one row at a
time, and state plainly which rows this session did **not** re-read. No number below is inferred: every
value is either quoted from the source named beside it or recomputed here from that source's published
inputs, and the recomputation is printed so it can be checked by hand.

**Nothing here is a new forecast.** It is a check that the published board says what its sources say.

---

## 1. The board that was audited

| Fact | Value | Where it comes from |
| --- | --- | --- |
| Snapshot | `data/latest.json`, generated `2026-10-25T13:46:54.275795Z` | the file's own `generated_at` |
| Fixture rows | 78 | `coverage_counts`: api 78 / page 78 / lobby 78 / retained 78 |
| Open rows | **17, every one with a pick and a win probability, 0 unresolved** | each row's `state`, `pick`, `probabilities` |
| Past-dated rows | 61, all with a start before the audit clock; **0 future rows are excluded** | recomputed over all 78 rows |
| Method mix | 11 strict exchange · 1 wide exchange (labelled) · 1 bookmaker listing · 4 originated Valve-VRS lines | each row's `method` |
| Committed build | `build-info.json` revision `27ba90ce…`, built `2026-10-25T13:46:54Z`, 78 rows | `build-info.json` |
| Live build at audit time | revision `06915a8…`, built `2026-10-25T13:56:26Z`, 78 rows, 16 open / 16 picks / 0 unresolved | <https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json?cb=b06ee902> |

The live board carries 16 open matches rather than 17 because fixture `1085542` (start `14:00Z`, lock
`13:54Z`) left the board when its lock passed between the two captures. That is the documented expiry rule
working, not a missing pick.

The board rotates, so this audit is pinned to a snapshot rather than to "today": `main` moved on to the
`2026-10-25T14:22:27Z` snapshot (78 rows, 16 open, 16 picks, 16 percentages, 0 unresolved — 11 exchange,
1 bookmaker listing, 4 Valve-VRS) while this report was being written. Its open set is **checked by id**
to be exactly this audit's 17 rows minus the expired `1085542` — no row added, none dropped beyond that
expiry — so every check below still applies to it. (The Rooster/Abyssal row re-classified from the labelled
wide tier to the strict tier between the two captures because its spread came in at exactly 0.25, which is
inside the "25 points or less" gate; that is the label doing its job, not a change of source.)

**Gates re-run on the committed tree** (`.venv/bin/python`, dependencies pinned in `requirements.txt`):

| Gate | Command | Result |
| --- | --- | --- |
| Unit suite | `python -m unittest discover -s tests` | **1,628 tests, OK (12 skipped)**, 33 s |
| Audit suite | `python -m unittest discover -s audits -p 'test_*.py'` | 9 tests, OK |
| Integrity | `python verification-95b588c2/test_integrity.py` | 5 tests, OK |
| Independent verifier | `python -m unittest discover -s verification-c6 -p 'test_*.py'` | 12 tests, OK |
| Site validation | `python -m scripts.validate --data data/latest.json --site .` | 78 rows / 17 calculations reproduced / 15 pages / 730 links / 20 checksums / 182 displayed rows |

---

## 2. Every open row, its pick, and what this session could confirm

Legend — **re-verified**: the session opened the source itself and compared it with the row.
**Not re-read**: the row's stored evidence is internally consistent and passes the independent verifier,
but this session did not open the source, so it is *not* claiming a fresh confirmation.

| # | Fixture (id) | Start (UTC) | Pick | Published % | Method | Source on the row | This session |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ex-Zero Tenacity vs Spirit Academy (1085542) | 25 Oct 14:00 | ex-Zero Tenacity | 59.0 | exchange | [Polymarket 6158059](https://gamma-api.polymarket.com/markets/6158059) | **re-verified** — same pair, same teams, price now 0.61; see §4 |
| 2 | Infinite vs BRUTE (1079199) | 25 Oct 15:00 | BRUTE | 56.5 | exchange | [Polymarket 6072808](https://gamma-api.polymarket.com/markets/6072808) | **re-verified** — exact match 0.435 / 0.565 |
| 3 | BORRACHEIROS vs RED Canids Academy (1086696) | 25 Oct 16:00 | RED Canids Academy | 57.5 | exchange | [Polymarket 6158760](https://gamma-api.polymarket.com/markets/6158760) | not re-read |
| 4 | Color vs ex-Zero Tenacity (1079200) | 25 Oct 18:00 | Color | 68.84 | model (VRS) | [Valve standings 2026-10-05](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | **re-verified** — recomputed to 12 dp, §3 |
| 5 | FORZE Reload vs ex-RUSTEC (1081158) | 25 Oct 18:00 | FORZE Reload | 56.5 | exchange | [Polymarket 6098416](https://gamma-api.polymarket.com/markets/6098416) | **re-verified** — exact match 0.565 / 0.435 |
| 6 | BESTIA vs paiN (1082697) | 25 Oct 18:00 | paiN | 57.5 | exchange | [Polymarket 6166390](https://gamma-api.polymarket.com/markets/6166390) | **re-verified** — same pair, price now 0.585 |
| 7 | Projeto do KinGui vs Yawara (1086697) | 25 Oct 19:00 | Projeto do KinGui | 51.01 | model (VRS) | [Valve standings 2026-10-05](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | **re-verified** — recomputed to 12 dp, §3 |
| 8 | Ground Zero vs Off Chops (1082858) | 26 Oct 03:00 | Off Chops | 63.5 | exchange (spread 23 pts, warned) | [Polymarket 6066508](https://gamma-api.polymarket.com/markets/6066508) | not re-read |
| 9 | NEXVOID vs Alter Ego (1082859) | 26 Oct 03:00 | NEXVOID | 57.89 | bookmaker listing | [BO3.gg listing](https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026) | **re-verified** — page prints 1.60 / 2.20, §4 |
| 10 | FlyQuest vs Staqued (1082860) | 27 Oct 03:00 | FlyQuest | 92.5 | exchange | [Polymarket 6066520](https://gamma-api.polymarket.com/markets/6066520) | not re-read |
| 11 | Rooster vs Abyssal (1082861) | 27 Oct 03:00 | Abyssal | 57.0 | wide exchange (spread 26 pts) | [Polymarket 6066525](https://gamma-api.polymarket.com/markets/6066525) | **re-verified** — 0.425 / 0.575, spread 0.25 |
| 12 | B8 vs K27 (1082897) | 27 Oct 08:00 | B8 | 59.5 | exchange | [Polymarket 6024944](https://gamma-api.polymarket.com/markets/6024944) | not re-read |
| 13 | Alliance vs FaZe (1082898) | 27 Oct 11:00 | FaZe | 62.5 | exchange | [Polymarket 6024952](https://gamma-api.polymarket.com/markets/6024952) | **re-verified** — exact match 0.375 / 0.625 |
| 14 | Luminosity vs HOTU (1082900) | 27 Oct 17:00 | Luminosity | 52.5 | exchange | [Polymarket 6024960](https://gamma-api.polymarket.com/markets/6024960) | not re-read |
| 15 | Envy vs GamerLegion (1082901) | 27 Oct 20:00 | GamerLegion | 54.5 | exchange | [Polymarket 6037120](https://gamma-api.polymarket.com/markets/6037120) | not re-read |
| 16 | HOTU vs The Huns (1082792) | 31 Oct 09:00 | HOTU | 85.18 | model (VRS) | [Valve standings 2026-10-05](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | **re-verified** — recomputed, plus duplicate-label check, §3 |
| 17 | 5star vs 1WIN (1082793) | 31 Oct 13:00 | 1WIN | 75.70 | model (VRS) | [Valve standings 2026-10-05](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | **re-verified** — recomputed to 12 dp, §3 |

**Coverage of this audit: 11 of 17 rows re-verified against the source, 6 explicitly not.** The six are named
above rather than counted as verified. The board's own independent verifier (`verification-c6/audit_snapshot.py`)
re-derives all 17 from the retained evidence on every publication; this session's contribution is that the
sources themselves were opened.

---

## 3. The four originated model lines, recomputed from Valve's own file

Inputs: `live/2026/standings_global_2026_10_05.md` at commit `eec4853d7bcf0f1f7efe7f0d901234bef7e98b75`.
Formula: Valve's `model/fit.js` evaluates a match with a fixed rating deviation (`rd : 75`, line 15) through
`model/glicko.js`, whose expected score is `g = 1 / sqrt(1 + 3 q² RD² / π²)`, `q = ln 10 / 400`,
`ev = 1 / (1 + 10^(g·(r − ro)/(−400)))`. Calibration: `p = 0.5 + 0.7986 · (E − 0.5)`.

Recomputed here from the raw markdown, importing none of `scripts/`:

| Fixture | Valve rows used (standing, points) | Raw E | Published | Recomputed | Δ |
| --- | --- | --- | --- | --- | --- |
| Color vs ex-Zero Tenacity | #57 Color 1249 · #93 ex-Zero Tenacity 1066 | 0.735906802852 | 0.688395172758 / 0.311604827242 | 0.688395172758 / 0.311604827242 | 0 |
| Projeto do KinGui vs Yawara | #144 ex-Keyd Stars 854 · #147 Yawara 845 | 0.512597351004 | 0.510060244512 / 0.489939755488 | 0.510060244512 / 0.489939755488 | 0 |
| HOTU vs The Huns | #31 HOTU 1437 · #122 The Huns 944 | 0.940520617794 | 0.851799765370 / 0.148200234630 | 0.851799765370 / 0.148200234630 | 0 |
| 5star vs 1WIN | #80 5star 1110 · #38 1win 1383 | 0.178169016943 | 0.242985776931 / 0.757014223069 | 0.242985776931 / 0.757014223069 | 0 |

Every pair sums to 1.000000000000. The published digits are the file's Glicko points through Valve's formula;
nothing was re-tuned here.

**The duplicate label, checked line by line.** Valve's file contains **two** rows called *The Huns*:

```
| 122      |    944 | The Huns | Annihilation, Bart4k, bexyz, controlez, Cozen      | …
| 213      |    701 | The Huns | Bart4k, controlez, nin9, sk0R, xerolte              | …
```

The lineup recorded on the row from HLTV is `Bart4k, controlez, bexyz, Cozen, DarkMeister`: 4 players shared
with #122 and 2 with #213, so exactly one row satisfies Valve's own "three players or more is the same team"
rule and the row is resolvable rather than ambiguous. **Sensitivity:** had #213 been used, the same fixture
would publish **88.66 / 11.34** instead of **85.18 / 14.82** — the pick does not change, the probability moves
3.5 points. That is why the choice is written down here instead of being left implicit.

**Is the 20-day-old standings file stale?** No — it is the newest file Valve has published. The repository's
`HEAD` is `eec4853d7bcf0f1f7efe7f0d901234bef7e98b75` (last commit `Updating Regional Standings for 10/5/2026`,
`2026-10-05`), the pinned commit equals `HEAD`, and `live/2026/` contains no `standings_global_*.md` later than
`2026_10_05`. Valve publishes monthly; the collector's own ceiling is 62 days (`MAX_STANDINGS_AGE_DAYS`).

---

## 4. What the exchanges and the book itself said, read by this session

Each row below was opened directly. "Drift" is the change between the row's recorded observation (`13:41Z`)
and this session's read; the pick is unchanged unless stated.

| Fixture | Source | Recorded on the row | Read now | Drift | Same fixture? |
| --- | --- | --- | --- | --- | --- |
| ex-Zero Tenacity vs Spirit Academy | [Polymarket 6158059](https://gamma-api.polymarket.com/markets/6158059) | 0.59 / 0.41, spread 0.02, $1,231 | 0.61 / 0.39, bestBid 0.60 / bestAsk 0.62, `updatedAt 14:14:38Z` | +2 pts toward the pick | yes — outcomes `["ex-Zero Tenacity","Spirit Academy"]` |
| Infinite vs BRUTE | [Polymarket 6072808](https://gamma-api.polymarket.com/markets/6072808) | 0.435 / 0.565, spread 0.01, $56,384 | 0.435 / 0.565, bestBid 0.43 / bestAsk 0.44, `updatedAt 14:12:37Z` | 0 | yes — outcomes `["Infinite","Brute"]`, start `15:00Z` |
| FORZE Reload vs ex-RUSTEC | [Polymarket 6098416](https://gamma-api.polymarket.com/markets/6098416) | 0.565 / 0.435, spread 0.01, $11,260 | 0.565 / 0.435, bestBid 0.56 / bestAsk 0.57, `updatedAt 14:16:38Z` | 0 | yes — start `18:00Z` |
| BESTIA vs paiN | [Polymarket 6166390](https://gamma-api.polymarket.com/markets/6166390) | paiN 0.575, spread 0.01, $97,121 | paiN 0.585, bestBid 0.58 / bestAsk 0.59, `updatedAt 14:16:38Z` | +1 pt toward the pick | yes — start `18:00Z` |
| Rooster vs Abyssal | [Polymarket 6066525](https://gamma-api.polymarket.com/markets/6066525) | 0.43 / 0.57, spread 0.26, $3,288 | 0.425 / 0.575, bestBid 0.30 / bestAsk 0.55 (spread 0.25), `updatedAt 14:16:38Z` | −0.5 pt | yes — start `2026-10-27T03:00Z`; the wide-spread warning is still the right label |
| Alliance vs FaZe | [Polymarket 6024952](https://gamma-api.polymarket.com/markets/6024952) | 0.375 / 0.625, spread 0.01, $8,751 | 0.375 / 0.625, bestBid 0.37 / bestAsk 0.38, `updatedAt 14:14:38Z` | 0 | yes — start `2026-10-27T11:00Z` |
| NEXVOID vs Alter Ego | [BO3.gg (Thunderpick)](https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026) | 1.60 / 2.20, overround 0.0795 → 57.89 / 42.11 | page prints **1 1.60 / 2 2.20** | 0 | yes — same title, DFRAG Invitational 2026, listed `Oct 25, 23:00`, both five-man lineups shown |

Bookmaker arithmetic, re-done by hand: `1/1.60 = 0.625000`, `1/2.20 = 0.454545`, overround `1.079545`;
`0.625000 / 1.079545 = 0.578947` and `0.454545 / 1.079545 = 0.421053` — the two digits the row publishes.

---

## 5. Irregularities, each with its source

Flagged for review rather than quietly accepted. None of them changes a pick on this board.

1. **The 0.7986 calibration slope is read off a chart, not a number in Valve's text.** The repository's
   `readme.md` (line 37) states the correlation (Spearman's rho 0.98) and says "the slope is shallower than
   we'd like … would be closer to 1", but prints no slope value; the figure is `modelfit.png`, an image. The
   project applies 0.7986 symmetrically. Source:
   [Valve readme](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/readme.md),
   [modelfit.png](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/modelfit.png).
   Already on the review page as `vrs-model-2026-10-15`; re-confirmed by this session, not re-discovered.
2. **One fixture has two different start times across sources.** Polymarket `6158059` carries
   `gameStartTime 2026-10-25 14:30:00+00` and `eventStartTime 2026-10-25T14:30:00Z`, while its own description
   says "initially scheduled for October 25, 2026 at 10:00 AM ET" (= 14:00Z) — which is Hotspawn's start.
   The board locks at Hotspawn's `13:54Z`, i.e. 36 minutes before the exchange's listed start. Conservative
   (the pick expires early rather than late), but it is a genuine disagreement about the fixture and is
   flagged below.
3. **Valve's published standings are 20 days old** at publication (`2026-10-05`). Verified as the newest file
   Valve has published, not a collector fault; disclosed here so the age is never mistaken for freshness.
4. **Extreme values deserve a second look, not a silent pass.** FlyQuest 92.5% and HOTU 85.2% are the two
   most one-sided lines; both are re-derived (FlyQuest from the exchange mid, HOTU above), and both carry the
   source's own spread/liquidity or Valve points beside them on the evidence page.
5. **The Hotspawn feed keeps returning past-dated rows as `scheduled`** — 61 of 78 on this snapshot, every one
   with a start before the audit clock, and **0** rows with a future start are withheld. Already flagged as
   `feed_status` on every snapshot.

**Not a defect, but worth knowing when checking the live site:** `build-info.json` served without a
cache-busting query returned the `01:47Z` build while `build-info.json?cb=…` returned the same-origin `13:56Z`
build. Verifying deployed bytes therefore needs a cache-buster, or a false "the deploy is stale" reading
follows.

---

## 6. Reproducing this audit

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -m unittest discover -s audits -p 'test_*.py'
.venv/bin/python verification-95b588c2/test_integrity.py
.venv/bin/python -m unittest discover -s verification-c6 -p 'test_*.py'
.venv/bin/python -m scripts.validate --data data/latest.json --site .
git clone --depth 1 https://github.com/ValveSoftware/counter-strike_regional_standings /tmp/valve
git -C /tmp/valve rev-parse HEAD          # must equal the commit pinned in each model row's evidence
curl -s https://gamma-api.polymarket.com/markets/6072808   # any id from §4
```

The row-by-row evidence, including each market's raw response hash and observation time, is inside
`data/latest.json` under `matches[].evidence`, and rendered per row at `evidence.html#match-<id>`.
