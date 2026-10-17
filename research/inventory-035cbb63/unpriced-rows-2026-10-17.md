# The five open rows that have a pick but no percentage — session 035cbb63

Checked: 17 October 2026, 00:55–01:10 UTC, against the verified snapshot generated
**2026-10-17T01:03:04Z** (`research/harvest-035cbb63/snapshot.json`, 96 rows, three-way Hotspawn
parity api = page = lobby = 96, `coverage: verified`).
Reviewed by: session `035cbb63`. Every number below is copied from a retained response; nothing is
recalled or estimated.

## The rows

| Hotspawn id | Fixture | Competition | Start (UTC) | Published pick | Percentage |
| --- | --- | --- | --- | --- | --- |
| 1081511 | VP.Future vs Black Phoenix | GLuck Yungstar 2026: Series #3 | 2026-10-17 09:00 | Black Phoenix | **blank** |
| 1079634 | Lavked vs LFO 10 | CCT Europe 2026 Series #11 | 2026-10-17 11:00 | Lavked | **blank** |
| 1081522 | antidaun vs Phantom Academy | CCT Europe 2026 Challengers #8 | 2026-10-18 13:45 | Phantom Academy | **blank** |
| 1081861 | Lynn Vision vs Morningstar | VOID Autumn Cup 2026 | 2026-10-20 03:00 | Lynn Vision | **blank** |
| 1081863 | Chinggis Warriors vs WXM | VOID Autumn Cup 2026 | 2026-10-20 07:00 | Chinggis Warriors | **blank** |

Method on all five: `research_rank_single` — a pick from HLTV-verified fixture identity plus a
one-sided ranking, and **no** probability. The remaining 29 open rows all carry a percentage
(exchange, bookmaker, wide exchange, or the labelled VRS model line).

## What each source actually returned

Retained per-row HLTV reads (HTTP 200):

| Row | HLTV match page | numeric quote rows in HLTV's betting table | HLTV world rank | VRS rank on HLTV |
| --- | --- | --- | --- | --- |
| 1081511 | [2399646](https://www.hltv.org/matches/2399646/vpfuture-vs-black-phoenix-gluck-yungstar-2026-series-3) (01:01:14Z) | 0 | VP.Future unranked · Black Phoenix #57 | none · 66 |
| 1079634 | [2399311](https://www.hltv.org/matches/2399311/lavked-vs-lfo-10-cct-2026-europe-series-11) (01:01:15Z) | 0 | Lavked #140 · LFO 10 unranked | 141 · 166 |
| 1081522 | [2399682](https://www.hltv.org/matches/2399682/antidaun-vs-phantom-academy-cct-2026-challengers-europe-series-8) (00:55:55Z) | 0 | antidaun unranked · Phantom Academy #178 | 255 · 172 |
| 1081861 | [2399576](https://www.hltv.org/matches/2399576/lynn-vision-vs-morningstar-macemedia-void-autumn-cup-2026) (00:55:55Z) | 0 | Lynn Vision #39 · Morningstar unranked | 70 · none |
| 1081863 | [2399578](https://www.hltv.org/matches/2399578/chinggis-warriors-vs-wxm-macemedia-void-autumn-cup-2026) (00:55:56Z) | 0 | Chinggis Warriors #61 · WXM unranked | 58 · none |

HLTV gives identity and ranking order — which is what the published pick rests on — and no numeric
line. That is a property of these fixtures, not a defect: HLTV carries no betting table for GLuck
Yungstar, CCT Challengers or VOID Autumn Cup group matches.

## Why the Valve VRS model cannot originate a line for them

The originated line needs **both** teams in Valve's official global standings. Grepping the vendored
official file `data/vrs/standings_global_2026_10_05.md`
([ValveSoftware/counter-strike_regional_standings @ eec4853](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)):

| Team | In Valve's file? | Roster note |
| --- | --- | --- |
| Black Phoenix | **no** | — |
| VP.Future | **no** | — |
| LFO 10 | **no** | — |
| Lavked | **no** | — |
| Phantom Academy | **yes** — standing 172, 783 pts | `Ayteel, Brain47, Dr3nquu, kalyambys, stefienson`; HLTV lists `…, La1roN` (4/5) |
| antidaun | **no** | — |
| Lynn Vision | **yes** — standing 64, 1190 pts | `C4LLM3SU3, EmiliaQAQ, Starry, Westmelon, z4KR`; exact 5/5 with HLTV |
| Morningstar | **no** | — |
| Chinggis Warriors | **yes, twice** — standings 87 (1084 pts) and 220 (685 pts) | HLTV lineup `ROUX, sk0R, cool4st, tikuak, fury5k` matches 4/5 of standing 87 |
| WXM | **no** | — |

Every one of the five rows has **at least one team with no Valve standings entry**, so a two-sided
originated line is impossible for all five. The reasons recorded in the snapshot
("not listed in the Valve global standings") are accurate.

## A related row that *did* get priced, and why that is not the same thing

Row **1081521 (ex-6666 vs Privateer)** also looked unpriced at 00:55Z and is now published at
**ex-6666 78.2% / Privateer 21.8%** from the VRS model (923 vs 608 points). The difference is that
the identity register already resolves `ex-6666` to Valve's `6666` standing #127 on a cited basis,
not by inference: Valve's own published rule (`model/team.js`,
`TEAM_OVERLAP_TO_SHARE_ROSTER = 3` — rosters sharing at least three players are the same team,
verified at commit `eec4853`), and the fact that Valve's detail file for #127 lists
`amster, dENZY, kL1o, rendysky, skcH` while HLTV's fixture lists the team labelled `ex-6666` as
`skcH, kL1o, amster, rendysky, stefienson` — four shared players, where the *other* `6666` row
(#368) shares only one, so the overlap selects exactly one standing.
Register entry: `data/identities.json`; sources
[Valve detail file](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0127--6666--amster-denzy-kl1o-rendysky-skch.md)
and [HLTV 2399681](https://www.hltv.org/matches/2399681/ex-6666-vs-privateer-cct-2026-challengers-europe-series-8).
Note that the pick direction did not change: `research_rank` had already named ex-6666.

An earlier draft of this file said the `ex-6666` / `6666` pair was "deliberately not aliased". That
was this session's error and is corrected here — the mapping exists and its basis is published.

## One ambiguity that is recorded, not resolved

`Chinggis Warriors` appears **twice** in Valve's file (standings 87 and 220, different rosters).
HLTV's lineup for 1081863 matches 4 of 5 of standing 87. Choosing 87 over 220 would still be an
inference, and the opponent `WXM` has no standings entry at all, so the row stays unpriced either
way. The ambiguity is on the record for manual review rather than silently resolved.

## What would change this

A book listing — any two-sided, dated, replayable moneyline — for these five fixtures. That is the
mechanism another session is adding; this dossier only records what the primary sources say today,
so the next reader can check the claim without repeating the search.
