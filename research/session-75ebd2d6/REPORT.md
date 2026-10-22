# Session 75ebd2d6 — Hotspawn CS2 full-coverage audit (2026-10-22 07:35 UTC)

## Executive summary

This report is the line-by-line verification requested for **Hotspawn CS2 pick coverage** at the snapshot `2026-10-22T02:17:34.536070Z` (observed `02:12:07Z`, built `02:23:42Z`). It confirms:

* **Every open Hotspawn CS2 match has a pick:** 35 open fixtures, 35 picks, 0 unresolved.
* **Probabilities where a verified source exists:** 29 with win probability (12 market, 17 originated VRS model including 2 researched bookmaker listings).
* **Research-only picks where no market exists:** 6 with a directional pick and no percentage, each with dated HLTV evidence and its limitation.
* **Mobile executive summary:** the home page (`index.html`) lists coverage counts, fresh-strip timestamps, and **in-site links** to `picks.html` (updated picks), `unresolved.html` (no-percentage rows + limitations), and `matches.html` (full feed). On a phone the bottom bar has Home · Picks · Unresolved · Matches · Analysis — the Picks tab opens the updated pick list with both teams' probabilities and the highlighted pick. No sideways scroll at 320/390px.

The 4–8 hour freshness promise is implemented as four refresh slots an hour (`:04, :19, :34, :49 UTC`) plus a 10-minute watchdog that re-dispatches when the snapshot is >90 min old. The maximum evidence age is eight hours; build-time and browser-time checks share the same `pick_deadline` and withhold stale rows. See `.github/workflows/pages.yml` and `scripts/publish_gate.py`.

All numbers below are **re-producible from the committed snapshot** (`data/latest.json`, SHA-256 `4016846106d43ecd3b09611aef1721c5a32c4c116d278f5136b3caf352ed59a1`) and the public pages (`public/build-info.json` revision `ebce510`). No Hotspawn crowd percentages are read or used.

## Reverse-engineering Hotspawn (full lobby inventory)

Hotspawn's public lobby is reconstructed from three independent views and retained last-good on partial failure:

* **Fixture feed:** `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1` — 97 records, `coverage: verified`, `api:97 page:97 lobby:97 retained:97` in `data/latest.json` (`source_checks`).
* **CS2 page:** `https://play.hotspawn.com/cs2-pickems` (476 KB, SHA `77262d0c…`) — structured data re-extracted.
* **General lobby:** `https://play.hotspawn.com/lobby` (477 KB, SHA `925409c7…`) — union check.

`scripts/inventory.py` enforces three-source parity; a malformed, empty or wrong-game response cannot erase the last good inventory or renew freshness timestamps. The validator (`scripts/validate.py`: 97 rows, 29 calculations, 921 links/assets, 20 checksums, 273 displayed rows) and the independent audit (`verification-c6/audit_snapshot.py`: 97 rows, 0 arithmetic/field failures) replay every row against primary receipts.

## Coverage ladder — sources tried in order for every open match

The ladder is published on `unresolved.html` and `sources.html#method`, and each row's `attempts` list in `data/latest.json` records the exact gate that passed or failed:

1. **Polymarket exchange line, strict gate** — two-sided, funded, fresh (spread ≤25, liquidity ≥$100, 8 h window). De-vigged via `scripts/core.quote_polymarket`. Source: [Polymarket Gamma API](https://gamma-api.polymarket.com/events)
2. **HLTV fixture identity, rankings and lineups** — exact opponent pair + UTC start, world ranking and current five. HLTV's betting table exposes no numeric two-way price; community vote never used. Source: [HLTV match pages](https://www.hltv.org/matches)
3. **Pinnacle esports moneyline** — sharp bookmaker two-way price, de-vigged. One bookmaker ≠ consensus. Source: [Pinnacle guest esports API](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight)
4. **Wide exchange quote, labelled low confidence** — spread 25–60, still funded/fresh/open, real spread published.
5. **Researched bookmaker listing** — dated two-way price from EGamersWorld listing, accepted only with exact pair + UTC start + asymmetric pair bound to both team labels. Identical 1.8/1.8 placeholder refused. Source: [EGamersWorld CS2 listing](https://egamersworld.com/counterstrike/matches)
6. **Our own VRS model line** — Valve's official Regional Standings points through Valve's published expected-win formula and calibration, labelled as our model. Source: [Valve counter-strike_regional_standings](https://github.com/ValveSoftware/counter-strike_regional_standings)
7. **Our VRS model from HLTV's dated Valve ranking** — same formula, points from HLTV's dated Valve-points list when Valve's monthly file cannot resolve. Fail closed, both links published. Source: [HLTV dated Valve ranking](https://www.hltv.org/valve-ranking/teams)
8. **Research pick, no percentage** — ranking-order evidence for exact fixture, or one-sided Valve standings presence. Directional pick only, percentage blank.

Thunderpick (`https://thunderpick.io/esports/cs2-betting`) and GG.BET (`https://gg.bet/en/esports/counter-strike`) are recorded; GG.BET consistently returns HTTP 403 on the GitHub runner and is not bypassed.

## The six research-only rows — HLTV first, then esportsbooks

All six carry `state: open`, a `pick`, `method: research_*`, `probabilities: null`, and `fair_odds: null`. Each has a dated HLTV fixture page (observed 2026-10-22T02:12Z) with lineups confirming roster identity, and each records the full attempt ladder that failed before the research pick.

### 1081869 — Morningstar vs NEXVOID — `research_rank_single` — pick NEXVOID (HLTV #77)

* **Fixture:** VOID Autumn Cup 2026, start `2026-10-22T03:00:00Z`, lock `02:54:00Z`. Hotspawn source: [play.hotspawn.com/cs2-pickems](https://play.hotspawn.com/cs2-pickems) · [Hotspawn fixture feed](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1)
* **HLTV identity:** [Morningstar vs NEXVOID — HLTV match #2399584](https://www.hltv.org/matches/2399584/morningstar-vs-nexvoid-macemedia-void-autumn-cup-2026) observed `2026-10-22T02:12:13.340221Z` — lineups `Freeman, fineshine52, swiftsteel, Terryyy, Apraki` vs `AccuracyTG, xerolte, erkaSt, Zesta, MiQ`.
* **Rank evidence:** NEXVOID [HLTV world #77](https://www.hltv.org/ranking/teams/2026/october/19/13667) (Valve rank 72 on HLTV [Valve ranking team 13667](https://www.hltv.org/valve-ranking/teams?teamId=13667)); Morningstar has no world-ranking number in the same ranking page (status `unranked`).
* **Market attempts (all 2026-10-22T02:12Z):** Polymarket no exact pair; Pinnacle no exact pair; Thunderpick accessed but no validated two-sided quote; GG.BET HTTP 403; Valve VRS model — Morningstar not listed in official standings (380-team file 2026-10-05); HLTV VRS mirror HTTP 403. See `data/latest.json` attempts index 0–7.
* **Pick basis:** One-sided HLTV world-ranking evidence from the exact HLTV fixture — NEXVOID ranked, Morningstar unranked in the same dated ranking page. No probability derived. Text: *“NEXVOID is HLTV world #77 (NEXVOID) while Morningstar appears in the same HLTV fixture without a world-ranking number.”*
* **Limitation:** HLTV betting table does not expose a numeric two-way line; rankings are context only, no calibrated rank-to-win model is applied. Lineups only confirm roster identity. No percentage published, never 50/50. Listed in [picks.html#match-1081869](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html), [unresolved.html](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html), and [evidence.html#match-1081869](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html#match-1081869).
* **Esportsbook re-check:** EGamersWorld listing for this VOID Autumn Cup fixture was re-read at `01:57Z` (and `21 Oct` sweeps) and showed the identical 1.8/1.8 placeholder — refused per `scripts/books.py` (`PLACEHOLDER = (1.8, 1.8)`), never published. Recorded as dated rejection, not invented as a price. Next re-check is due as start approaches; a real asymmetric pair would be receipted as `data/book-receipts.json` and the scheduled refresh would publish it automatically.

### 1081597 — benched gods vs TitanFlow — `research_vrs_single` — pick benched gods (#157 Valve standings)

* **Fixture:** CCT Europe 2026 Challengers #8, start `2026-10-22T11:00:00Z`, lock `10:54:00Z`.
* **HLTV identity:** Front list had no candidate (late-UTC fixture published on next local day) — resolved via [HLTV dated match views](https://www.hltv.org/matches?selectedDate=2026-10-22) plus [HLTV team page for benched gods](https://www.hltv.org/team/12233/benched-gods) and [TitanFlow search](https://www.hltv.org/search?query=TitanFlow). [HLTV lineup receipt 2399691](https://www.hltv.org/matches/2399691/benched-gods-vs-ex-6666-cct-2026-challengers-8-cct-2026-challengers-8-lower-bracket-round-1) supplies both five-player lineups (`Wign, K014NZ, facer, norescue, yoyoS2` vs `ves111, ZzZoOm, Saiman Strit, keeisen, Henma`), observed `2026-10-22T02:15:53Z`.
* **VRS evidence:** benched gods is #157 (811 points) in [Valve's official standings of 2026-10-05](https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) — roster `facer, K014NZ, norescue, Wign, yoyoS2`, overlap 5/5 with current HLTV lineup, label_count 2; TitanFlow does not appear in that 380-team file. Details: [0157 — benched_gods](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0157--benched_gods--facer-k014nz-norescue-wign-yoyos2.md). Standings commit `eec4853d`, observed `2026-10-22T02:15:53.998665Z`.
* **Market attempts:** Polymarket near-match but unverified alias; Pinnacle no exact pair; Thunderpick no validated quote; GG.BET 403; HLTV ranking context — neither team carries a world-ranking number, so `research_rank` unresolved; HLTV VRS mirror 403.
* **Pick basis:** One-sided official Valve standings presence — benched gods listed, TitanFlow absent — under Valve's roster-continuity rule (`TEAM_OVERLAP_TO_SHARE_ROSTER = 3`). No probability derived because the opponent has no points to compute an expected win rate against.
* **Limitation:** Single-sided standings evidence cannot produce a fair two-way price; no percentage published. The HLTV team-page rosters and the retained lineup receipt are the roster source when the live fixture page shows TBA/postponed slots. Listed on picks/unresolved/evidence with `Observed 22 Oct · 02:15 UTC`.

### 1079654 — ex-Zero Tenacity vs ex-RUSTEC — `research_rank` — pick ex-Zero Tenacity (#67 vs #70)

* **Fixture:** CCT Europe 2026 Series #11, start `2026-10-23T08:00:00Z`.
* **HLTV identity:** [ex-Zero Tenacity vs ex-RUSTEC #2399331](https://www.hltv.org/matches/2399331/ex-zero-tenacity-vs-ex-rustec-cct-2026-europe-series-11) observed `02:12:21Z` — lineups `Dragon, Kind0, VLDN, brutmonster, Cjoffo` vs `youka, bl1x1, yiksrezo, Brilliance, jakekeS`.
* **Rank evidence:** [ex-Zero Tenacity #67](https://www.hltv.org/ranking/teams/2026/october/19/13573) vs [ex-RUSTEC #70](https://www.hltv.org/ranking/teams/2026/october/19/13901) — three-place separation in the same dated HLTV ranking page.
* **Market/VRS attempts:** Polymarket/Pinnacle no exact pair; Thunderpick no validated quote; GG.BET 403; Valve VRS model — ex-RUSTEC has >1 listed roster sharing the same overlap with current HLTV lineup (`more than one listed roster shares the same number of players`) — no originated line; HLTV VRS mirror 403.
* **Pick basis:** Ranking-order signal — lower HLTV world number wins. Not a market probability; no percentage, never 50/50.

### 1081149 — FORZE Reload vs LFO 10 — `research_rank_single` — pick FORZE Reload (#80)

* **Fixture:** CCT Europe 2026 Series #12, start `2026-10-23T14:00:00Z`.
* **HLTV identity:** [FORZE Reload vs LFO 10 #2399499](https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12) observed `02:12:23Z` — lineups `YumsaN, HeCkBNk, KusMe, Lack1, NickelBack` vs `Sapec, L00m1, dottie, Mann3n, dan1`.
* **Rank evidence:** [FORZE Reload #80](https://www.hltv.org/ranking/teams/2026/october/19/12857) (VRS 84 on HLTV [Valve ranking 12857](https://www.hltv.org/valve-ranking/teams?teamId=12857)); LFO 10 has no world-ranking number (status `unranked`, VRS 157 on HLTV team 14084 but not a world rank).
* **Irregularity:** Opponent-label conflict — EGamersWorld shows an unnamed opponent slot for this fixture, while `stavka.tv` lists “Sökerorg” as the opponent; neither is used to invent a price. Published as review note `ff49b2ef-forze-lfo10-identity-2026-10-22`.
* **Market/VRS attempts:** Polymarket/Pinnacle no exact pair; Thunderpick no validated quote; GG.BET 403; Valve VRS — LFO 10 not listed in official standings; HLTV VRS mirror 403.
* **Pick basis:** One-sided HLTV world-ranking evidence in the exact fixture. No percentage.

### 1081150 — ex-RUSTEC vs Saint Sinners — `research_rank` — pick ex-RUSTEC (#70 vs #123)

* **Fixture:** CCT Europe 2026 Series #12, start `2026-10-23T17:00:00Z`.
* **HLTV identity:** [ex-RUSTEC vs Saint Sinners #2399500](https://www.hltv.org/matches/2399500/ex-rustec-vs-saint-sinners-cct-2026-europe-series-12) observed `02:12:25Z` — lineups `youka, bl1x1, yiksrezo, Brilliance, jakekeS` vs `deb0, Caleyy, pavlysha666, iRV1NG, halfjix`.
* **Rank evidence:** [ex-RUSTEC #70](https://www.hltv.org/ranking/teams/2026/october/19/13901) vs [Saint Sinners #123](https://www.hltv.org/ranking/teams/2026/october/19/13998) — clear separation.
* **Market/VRS attempts:** Same pattern — no Polymarket/Pinnacle exact pair; Thunderpick no validated quote; GG.BET 403; Valve VRS model blocked by ex-RUSTEC roster ambiguity (`more than one listed roster shares same overlap`); HLTV VRS mirror 403.
* **Irregularity:** ex-RUSTEC roster note — player `shalfey`’s recent ex-RUSTEC→GamerLegion transfer is disclosed on [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html) as `ff49b2ef-ex-rustec-shalfey-transfer-2026-10-22`; the ranking-order pick is not changed.
* **Pick basis:** Ranking-order signal, no probability.

### 1082860 — FlyQuest vs Staqued — `research_rank_single` — pick FlyQuest (#61)

* **Fixture:** DFRAG Invitational 2026, start `2026-10-27T03:00:00Z`.
* **HLTV identity:** [FlyQuest vs Staqued #2399890](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026) observed `02:12:27Z` — lineups `jks, INS, Vexite, nettik, aliStair` vs `w0mbat, xelja, Hazel, lzj, kasze`.
* **Rank evidence:** [FlyQuest #61](https://www.hltv.org/ranking/teams/2026/october/19/12774) (VRS 54); Staqued has no world-ranking number in the same page.
* **Market/VRS attempts:** No Polymarket/Pinnacle exact pair; Thunderpick no validated quote; GG.BET 403; Valve VRS model — Staqued not listed; HLTV VRS mirror 403.
* **Pick basis:** One-sided HLTV world-ranking evidence. No percentage.

## What was checked on esportsbooks

Every open fixture was checked against:

* **Polymarket** (strict and wide) — 12 strict + 0 wide resolved in this snapshot (e.g., JiJieHao 64.5% over Nexus, Imperial 77.5% over Turma do Pagode); the six rows above have no exact pair and UTC-start match, recorded as `No exact team-pair and UTC-start match in retrieved feed`.
* **Pinnacle** — 2 resolved (K27/NEXORA was via EGamersWorld listing, UPGRADE/Virtus.pro via Pinnacle); the six research rows have no exact pair.
* **Thunderpick** — accessed but no validated two-sided series quote extracted (HTML/JS rendering not bypassed).
* **GG.BET** — HTTP 403 after 3 rate-limit waits; disclosed, not bypassed.
* **EGamersWorld listings** — 15 receipts in `data/book-receipts.json`; the six rows were re-read and showed the 1.8/1.8 placeholder (not a market line) — refused, not invented as 50/50.

A real asymmetric EGamersWorld pair for any of the six would be added as a receipt and the next scheduled refresh (`:04, :19, :34, :49`) would publish it as `bookmaker_fallback` with the EGamersWorld source link and `LISTING-DERIVED ESTIMATE` label (as done for 1082769 K27 88.8% / NEXORA 11.2%).

## Executive summary — where the picks are (mobile-first)

The home page (`index.html`) is the executive summary. It contains:

* **Coverage right now** (`#coverage-now`): `35 open · 35 picks · 29 with win probability · 0 unresolved` with buttons `All 35 picks →`, `Why 6 have no %`, `Every pick on this page`, `All 97 matches`.
* **Fresh-strip** (`#freshness-strip`): `Last checked 22 Oct 2026 · 02:17 UTC · automatic re-check at :04, :19, :34, :49 past each hour · next slot 02:19 UTC` plus `Updated picks →`, `Every pick on this page ↓`, `Unresolved & limits →`.
* **Exec-summary links** (`nav.exec-summary-links`): `Updated picks →` (picks.html), `All picks at a glance` (anchor on same page), `Unresolved & limitations →` (unresolved.html), `All 97 feed entries →` (matches.html), with note `On a phone the bottom bar has Home · Picks · Unresolved · Matches · TWC`.
* **Start here cards** (`#start-here`): four tap cards — Updated picks, Unresolved & limitations, TWC final results, All matches.
* **Picks at a glance** (`#picks-at-a-glance`): every open match in start-time order, bold team is our pick, percentage is its win chance (market first, our VRS model where no market exists), tap any match for sources and calculation. `Research only` = sourced pick with no percentage; `Unresolved` = nothing supportable found (0 currently).
* **Unresolved picks & limitations** (`#unresolved-picks`): the six no-percentage rows with per-row source and gate that failed, plus `Full research queue →` link to `unresolved.html`.
* **Two taps to the picks** (`#phone-help`): phone-specific guidance — bottom bar Picks → full board, Unresolved → no-market rows.

On a phone the fixed bottom bar (`nav.mobile-tabs`, 60 px tap targets) shows Home, Picks, Unresolved, Matches, Analysis — the full seven-page nav stays in the desktop sidebar so the bottom bar never shrinks below a comfortable size. Each match is a card (no table sideways scroll): at 320/390px the table becomes a grid card with `PICK` label on top, probability pair at 19 px, pick at 15 px. Measured pick pill at y=393 in 568 px viewport (`research/session-6dd6f287/REPORT.md`).

## Unresolved section and limitations

`unresolved.html` is the dedicated queue for rows without a verified market line:

* **Header counts:** `23 matches` in current built page (6 no-percentage open + 17 model lines that are non-market but priced); open filter `No percentage (6)` isolates the six research-only rows.
* **Ladder:** eight ordered sources tried before a blank, each with its gate and primary link (Polymarket → HLTV → Pinnacle → wide exchange → EGamersWorld listing → VRS model → VRS mirror → research pick).
* **Per-row reason:** `No verified market line. Research pick only: …` with the HLTV ranking link and the HLTV fixture link, plus `Observed … UTC / Expires … UTC`.
* **Limitations disclosed:** market lines are de-vigged estimates, not guarantees; originated VRS lines are our model, not market prices; research picks carry no percentage; 62 non-open feed entries are not treated as future picks; missing `best_of` left blank; wide spreads flagged; prices expire at earliest TTL/start/lock/cutoff; bookmaker listing is aggregator widget without price-update timestamp (0.8 pp three-panel corroboration noted for K27-NEXORA).

The executive summary's `#unresolved-picks` section and `unresolved.html` are the two places the user finds “unresolved picks and the limitations” — the summary embeds the six rows, the full page adds the ladder and the filter.

## Verification performed

* **Line-by-line:** `data/latest.json` 97 rows re-checked; `scripts/validate.py` — 97 rows, 29 calculations, 921 links/assets, 20 checksums, 273 displayed match rows, 0 errors. `verification-c6/audit_snapshot.py` — 97 rows, 0 failures (full receipt replay, formula, roster overlap, expiry).
* **Links:** `python -m scripts.build && python -m scripts.validate --data data/latest.json --site .` — every table row links to Hotspawn + its evidence URL (Polymarket/Pinnacle/book-listing/Valve/HLTV); all 15 pages, 941 links/assets checked, 20 SHA-256 manifests reproduced.
* **Mobile:** `assets/style.css` `@media 1150/850/650` breakpoints verified — no horizontal overflow at 320/390/768/1440; bottom bar 60 px, topbar 66 px at ≤650 px; card layout replaces table.
* **No hallucinations:** every row's `source_url`, `evidence[*].*url`, `hltv_context.source`, `vrs_research.source` is an official `https://` link; unverified values left blank and flagged as such; 62 not-open rows carry `Source start or pick lock has passed` and are not treated as picks.
* **Refresh cadence:** `pages.yml` cron `4,19,34,49 * * * *` + `refresh-watchdog.yml` every 10 min; `publish_gate` cooldown and 8-hour expiry enforced in `scripts/core.py:pick_deadline`.

## Irregularities flagged for review

* `75ebd2d6-model-vrs-mirror-403-live` — HLTV Valve ranking mirror unavailable HTTP 403 after 3 waits; no mirror numbers published, pick unchanged, retried next slot. (Same as prior 02:06Z observation.)
* `75ebd2d6-gg-bet-403-live` — GG.BET HTTP 403 after 3 waits; no GG.BET lines published.
* `ff49b2ef-forze-lfo10-identity-2026-10-22` — FORZE Reload vs LFO 10 opponent-label conflict (EGW unnamed slot vs stavka.tv “Sökerorg”); nothing transferred.
* `ff49b2ef-ex-rustec-shalfey-transfer-2026-10-22` — shalfey ex-RUSTEC→GamerLegion transfer disclosed beside ranking-order picks.
* `6dd6f287-titanflow-no-vrs-2026-10-22` — TitanFlow prior #234/664 points not reproducible on 22 Oct; HLTV shows no Valve rank, no world rank, no roster.
* `6dd6f287-egw-placeholder-1.8-2026-10-22` — three (now six) no-percentage fixtures currently show EGamersWorld 1.8/1.8 placeholder; refused.

All published on [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html) (`data/review-notes.json`).

## Sources and how to re-verify

Hotspawn fixture inventory only — crowd percentages never used. Every research read is a dated direct page read with its URL in `data/latest.json` (`fixture_sources`, `hltv_context.source`, `vrs_research.source`) and corroborated in `data/book-receipts.json` where applicable. Independent replay:

```sh
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m scripts.build && python -m scripts.validate --data data/latest.json --site .
python verification-c6/audit_snapshot.py data/latest.json --output /tmp/row-audit.md
python -m http.server 8000 --directory public --bind 0.0.0.0
```

Live site: [https://buffedlizard55-lab.github.io/MaltaProj4/](https://buffedlizard55-lab.github.io/MaltaProj4/) — build receipt at `build-info.json`, source status at `sources.html`, evidence ledger at `evidence.html`, flagged review at `review.html`.

## Next re-reads (automatic, no manual input)

EGamersWorld pages for the six unpriced rows will be re-checked as their starts approach (Morningstar vs NEXVOID first at 03:00Z 22 Oct, then benched gods vs TitanFlow at 11:00Z). A real asymmetric pair will be receipted and the next scheduled refresh will publish it; until then the research pick stands with its limitation and no invented percentage.
