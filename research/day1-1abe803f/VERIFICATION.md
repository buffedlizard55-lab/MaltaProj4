# Verification log — session 1abe803f (16 October 2026, UTC)

Scope: Day-1 (14 Oct) and Day-2 (15 Oct) review of the Thunderpick World Championship 2026 pick-em, the Aurora roster premise, and the Day-3 claims in `data/analysis.json`.

Method: each claim was re-read from the primary page named below. Where a claim could not be re-read in this session, it is marked **not re-checked** and stays flagged. Probabilities are never taken from Hotspawn. Polymarket reads are from the harvest at 07:21 UTC (market `updatedAt` 07:17 UTC).

## Verdicts

| # | Claim | Verdict | Source (primary unless marked) |
|---|---|---|---|
| 1 | 9z 2-0 Aurora on 14 Oct; Inferno 13-11, Nuke 13-1 | Verified | HLTV match 2399384 |
| 2 | Veto: 9z removed Anubis, Aurora removed Ancient, 9z picked Inferno, Aurora picked Nuke, 9z removed Mirage, Aurora removed Cache, Dust2 left over | Verified | HLTV match 2399384 (the other day-one vetoes were not read; left blank) |
| 3 | luchov 1.61 rating; Aurora were 5th in VRS going in; 9z 62 VRS points (1571 total) | Verified | HLTV news 45718 |
| 4 | Falcons 2-0 NIP, FURIA 2-0 BETBOOM, Legacy 2-0 PARIVISION (14 Oct) | Verified (series score) | HLTV results, event 8932 |
| 5 | Aurora 2-0 NIP (15 Oct) | Verified | HLTV news 45724; match 2399408 |
| 6 | 9z 1-2 Falcons; Nuke Falcons 13-9, Mirage 9z 13-8, Dust2 Falcons 13-9 | Verified | HLTV match 2399409 |
| 7 | "9z won Mirage 13-8 on Falcons' pick" (day-two review) | Verified, no change | HLTV match 2399409 |
| 8 | PARIVISION 1-2 BETBOOM; Legacy 1-2 FURIA (15 Oct) | Verified (series score) | HLTV results, event 8932 |
| 9 | Falcons 2-0 NIP map scores (Ancient 16-13 OT, Dust2 13-6) | **Secondary only** — from EsportBet preview; HLTV series score confirmed | esportbet.com (flagged) |
| 10 | Aurora roster: XANTARES, woxic, Jimpphat, kyxsan (IGL), Wicadia; coach Ashley 'ash' Battye | Verified | HLTV team page 11861 |
| 11 | Aurora Valve #5 (EU #5), HLTV world #6 | Verified (page dated 16 Oct) | HLTV team page 11861 |
| 12 | Jimpphat from MOUZ and coach from GamerLegion (~3 Jul); kyxsan IGL 8 Jul 2026; MAJ3R, soulfly, coach Fabre moved to inactive after IEM Cologne | Verified (trade press; labelled as reporting) | Strafe, 8 Jul 2026 |
| 13 | Most recent verified Aurora roster change = **8 Jul 2026** (kyxsan), not days before the match | **Corrected premise** — the change is real but about 14 weeks old | Strafe 8 Jul 2026; HLTV team page |
| 14 | First LAN with the new roster ended on 20 Aug 2026 | Verified (Aurora's own news page) | auroragg.com/en |
| 15 | Aurora's site lists Polymarket as a partner (conflict-of-interest disclosure) | Verified | auroragg.com/en (partner logos) |
| 16 | Aurora were 3rd at ESL Pro League Season 24 | Verified (Aurora's own news page, 11 Oct 2026) | auroragg.com/en |
| 17 | Aurora vs 9z head-to-head: 2-1 in series, 4-2 in maps to Aurora (three meetings) | **Corrected** — the draft said "2-4 in maps"; the sign was inverted | HLTV team page 11861 (match-preview text); HLTV news 45718; HLTV 2398721 (EPL 24) |
| 18 | Aurora 2-0 9z at IEM Cologne Major Stage 3 | **Secondary only** — EGamersWorld head-to-head table, not opened separately | egamersworld.com (flagged) |
| 19 | Aurora 2-0 9z, ESL Pro League Season 24 opener, 3 Oct | Verified (HLTV 2398721 result as recorded earlier; series score re-read via HLTV news 45718) | HLTV news 45718 |
| 20 | Hotspawn picks lock 5 minutes before scheduled start | Verified | play.hotspawn.com/how-it-works |
| 21 | Fixture 1080205 lock 13:54Z (feed lock_offset 360 s, a 6-minute value) | Feed value recorded; the 1-minute gap vs the rules page stays flagged in review-notes | Hotspawn fixture feed (harvest) |
| 22 | Aurora vs 9z model: VRS 68.0% Aurora (1716 vs 1543 points, Valve 2026-10-05 standings) | Repo calculation from harvest `model_check` | Valve regional standings file (linked in harvest) |
| 23 | Aurora vs 9z exchange: 69.5% Aurora (bid 0.69 / ask 0.70, ~$90.6k liquidity) | Read at 07:21 UTC | Polymarket market 5733288 (cs2-aur1-9z-2026-10-16) |
| 24 | BETBOOM vs Legacy exchange: Legacy 63.5% / BETBOOM 36.5% (bid 0.63 / ask 0.64, ~$77.9k) | Read at 07:21 UTC | Polymarket market 5763247 |
| 25 | BETBOOM vs Legacy VRS: Legacy 79.3% (1596 vs 1931 points) | Repo calculation from harvest `model_check` | Valve standings file |
| 26 | BETBOOM vs Legacy start 17:00Z, lock 16:54Z | Verified (Hotspawn feed and Polymarket gameStartTime) | Hotspawn feed; Polymarket 5763247 |
| 27 | NIP vs Liquid = HLTV 2399262, 04:00 HLTV clock (08:00Z), Best of 3, Stake Pulse Beat III QF | Verified | HLTV match 2399262 |
| 28 | Liquid vs NIP price 50.5% / 49.5% | Read at 07:21 UTC; coin-flip, no contrarian pick claimed | Polymarket market (cs2-nip-tl1-2026-10-16) |
| 29 | Eternal Fire vs Apogee Betclic (1081493) = Eternal Fire vs Betclic Apogee Esports, 08:00Z | Verified on HLTV 2399654 and Polymarket 5732890; alias register entry added (exact pair, exact start) | HLTV 2399654; Polymarket 5732890 |
| 30 | Eternal Fire 65.5% / Betclic 34.5% (bid 0.65 / ask 0.66, ~$8.7k) | Read at 07:21 UTC; thin single-venue market | Polymarket 5732890 |
| 31 | "Betclic (Poland), #71 HLTV, #57 Valve" | Verified | HLTV team page 12916 |
| 32 | Team Liquid homepage cited for fixture 1079586 | **Flagged** — generic homepage, not a fixture page; HLTV 2399262 is the primary source | teamliquid.com (generic) |
| 33 | "coach ash" vs "ashhh" spelling | **Flagged** — Strafe says ashhh, HLTV says ash; the day-2 file (another session's) is not edited here | see review-notes `coach-name-2026-10-16` |
| 34 | Harvest cadence 1 hour; a cron every 4–8 h is the required window | Not re-checked here; see review-notes `refresh-cadence-watchdog-2026-10-16` | GitHub Actions |
| 35 | Claims about Aurora's coach's own communication comments and the HLTV interview with BIT | **Not re-checked** — left as written, flagged for review | — |
| 36 | Claims about Hotspawn 61 stale records and 103 vs 95 coverage gap | Read from the harvest; flagged | research/harvest-1abe803f |

## Corrections made in this session

1. `data/analysis.json` — head-to-head map count corrected from "2-4" to "4-2 to Aurora" (verdict 17).
2. `data/analysis.json` — "recent roster change" wording replaced with the dated timeline (verdict 13).
3. `data/analysis.json` — BETBOOM and Aurora Day-3 entries updated to the 07:21 UTC harvest values. The unverified arT / Major-stakes wording from an earlier draft was removed; the Legacy–FURIA result (verdict 8) and the repo VRS figures (verdict 25) are kept.
4. `data/analysis.json` — Team Liquid source relabelled as generic (verdict 32).
5. `data/review-notes.json` — entries added: `h2h-aurora-9z-2026-10-16`, `betclic-alias-2026-10-16`, `team-liquid-source-2026-10-16`, `coach-name-2026-10-16`, `day2-results-2026-10-16`, `stale-hotspawn-records-2026-10-16`.

## Still flagged (does not block merge)

- Verdicts 9, 18 (secondary sources for one map-score line and one head-to-head row).
- Verdict 21 (1-minute lock-offset disagreement between Hotspawn's rules page and fixture feed).
- Verdict 32, 33 (generic Team Liquid homepage; coach spelling).
- Verdict 35 (quotes from earlier sessions not re-read).
- Verdict 34 (refresh cadence wording).
