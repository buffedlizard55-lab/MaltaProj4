# Day-4 review and guidance — session 621776e4

Written 2026-10-16 (UTC). Covers TWC 2026 days 1–3 (14–16 Oct) and the day-4 board
(17 Oct, semi-final day), plus the coverage fixes made to price every open Hotspawn
CS2 row.

Every number below is either (a) a quote from the linked primary source, or (b) a
value recomputed by `scripts/vrs.py` from Valve's own standings file. Nothing here
is inferred. Where a source disagreed, both readings are printed.

---

## 1. Days 1–3, verified against HLTV's event record

Event: Thunderpick World Championship 2026, 14–18 Oct 2026, Malta, $1,000,000, 8 teams.
Event record: <https://www.hltv.org/events/8932/thunderpick-world-championship-2026>
Results: <https://www.hltv.org/results?event=8932> (read 16 Oct ≈19:35Z and ≈20:05Z)

### Day 1 — 14 Oct 2026 (all four openers were sweeps)

| Series | Result | HLTV |
|---|---|---|
| 9z vs Aurora (Group A) | **9z 2-0 Aurora** — Inferno 13-11, Nuke 13-1 | [2399384](https://www.hltv.org/matches/2399384) · [HLTV news 45718](https://www.hltv.org/news/45718/9z-beat-aurora-2-0-to-kick-off-twc-2026) |
| Falcons vs NIP (Group A) | Falcons 2-0 NIP | [2399385](https://www.hltv.org/matches/2399385) |
| Legacy vs PARIVISION (Group B) | Legacy 2-0 PARIVISION | [2399386](https://www.hltv.org/matches/2399386) |
| FURIA vs BETBOOM (Group B) | FURIA 2-0 BETBOOM | [2399387](https://www.hltv.org/matches/2399387) |

The day-1 upset the user asked about: HLTV's report gives 9z's **luchov a 1.61 rating,
+6.61% swing and 97.4 ADR** — the map was closed on Inferno (13-11) and 13-1 on Nuke,
which was Aurora's own pick. HLTV match pages do not expose map scorelines to the
first chunks of a page fetch, so the 13-11 / 13-1 lines above come from HLTV news
45718 and are labelled primary there, not here.

### Day 2 — 15 Oct 2026

| Series | Result | HLTV |
|---|---|---|
| Aurora vs NIP (Group A elimination) | Aurora 2-0 NIP — Cache 13-9, Dust2 13-7, Wicadia 45-25 / 1.65 rating | [2399408](https://www.hltv.org/matches/2399408) |
| 9z vs Falcons (Group A winners') | Falcons 2-1 9z | [2399409](https://www.hltv.org/matches/2399409) |
| PARIVISION vs BETBOOM (Group B elimination) | BETBOOM 2-1 PARIVISION | [2399410](https://www.hltv.org/matches/2399410) |
| Legacy vs FURIA (Group B winners') | FURIA 2-1 Legacy | [2399411](https://www.hltv.org/matches/2399411) |

### Day 3 — 16 Oct 2026

| Series | Result | HLTV |
|---|---|---|
| Aurora vs 9z (Group A decider) | Aurora 2-0 9z — Cache 13-11 (HT 8-4, then 5-7); Inferno published as 13-4 | [2399412](https://www.hltv.org/matches/2399412) · [HLTV news 45736](https://www.hltv.org/news/45736/aurora-beat-9z-to-secure-third-consecutive-top-four-appearance) |
| BETBOOM vs Legacy (Group B decider) | **Not published at 20:05Z** — scheduled 17:00Z | [2399413](https://www.hltv.org/matches/2399413) |

Flagged: the **Inferno 13-4 scoreline is only corroborated by dust2.com.br /
EGamersWorld**, not by HLTV. It is published on the board as
secondary-corroborated, not as a verified HLTV number.

Flagged: **BETBOOM vs Legacy had no published result 3 hours after its 17:00Z
start.** The semi-final-2 opponent was therefore genuinely undecided at the time of
writing, and the board carries two conditional cards for that slot instead of one
pick. No result was claimed for it.

---

## 2. The Aurora roster question

The premise "a recent Aurora roster change explains the day-1 loss" **does not hold.**

- HLTV team page: <https://www.hltv.org/team/11861/aurora> — active five **XANTARES,
  woxic, Jimpphat, kyxsan, Wicadia**; HLTV rank #6, Valve standings #9 (1716 points).
- HLTV's most recent transfer news is **8 July 2026**: kyxsan in from Falcons —
  <https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan>.
  Jimpphat and coach ash were signed 3 July 2026. **No transfer in October 2026.**
- The team that lost 2-0 on day 1 is the same five that beat NIP 2-0 on day 2 and 9z
  2-0 on day 3. Aurora also **lead 9z 4-2 in maps** head-to-head per HLTV.

So day 1 was map-level variance, not an onboarding or rest effect. That matters for
the strategy question: across days 1–3 **the higher-ranked side (Valve standings) won
eight of ten series**. Hotspawn awards a fixed amount per correct pick — multipliers
come from tier, stage and format, not from how the crowd split — so a contrarian pick
only pays if the favourite is wrong, and nothing in this week's evidence says
favourites are being overrated at this event.

The contrarian read that *does* survive the evidence is narrower, and it is published
on the board as such: **Falcons vs Legacy** is the one day-4 pairing where the crowd-
priced favourite and the model disagree (see §3).

---

## 3. Day-4 board — 17 October 2026

Times below are UTC. HLTV displays this event's clock as UTC−4, so HLTV's "10:00"
is 14:00Z; the machine-readable start used by the pipeline is the UTC one.

### Semi-final 1 — FURIA vs Aurora, 14:00Z (Bo3, LAN)

- HLTV match: <https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026>
- Market line (primary): Polymarket market **5778024** (event 1200431) —
  **FURIA 0.52 / Aurora 0.48**, bid 0.51, ask 0.53, spread 0.02, liquidity
  **$10,151.23**, start 2026-10-17T14:00:00Z. Read from the official API at
  2026-10-16T19:34:52Z: <https://gamma-api.polymarket.com/markets/5778024>.
  Map-handicap sibling 5778026 prices FURIA −1.5 at 0.185.
- Our model line: Valve standings FURIA **1829** vs Aurora **1716** →
  `vrs.calibrated(vrs.expected(...))` = **62.2% / 37.8%**.
  Standings file: `standings_global_2026_10_05.md`, commit
  `eec4853d7bcf0f1f7efe7f0d901234bef7e98b75` —
  <https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md>
- **Direction agrees, size disagrees.** The market calls it a coin flip; the model
  makes FURIA a clear favourite. Aurora's week (beat NIP 2-0, beat 9z 2-0, dropped
  one map to no one) is the strongest argument the market is right.

### Semi-final 2 — Falcons vs (BETBOOM or Legacy), 17:00Z (Bo3, LAN)

- HLTV match: <https://www.hltv.org/matches/2399415/falcons-vs-betboom-legacy-winner-thunderpick-world-championship-2026>
- Falcons **1843** points. **Legacy 1931** → model **40.4% / 59.6%** (Legacy favoured).
  **BETBOOM 1596** → model **73.9% / 26.1%** (Falcons favoured, the widest day-4 gap).
- No Polymarket market existed for this fixture at the check, and no Pinnacle matchup
  carried it. Both cards are published as **conditional cards, not picks**, because
  the opponent was undecided (§1, day 3).
- Contrarian note: if Legacy win the decider, our model disagrees with the event's
  narrative favourite. That is the one day-4 spot where "contrarian but not stupid"
  has support: Legacy are the second-highest rated team in the event (1931 points)
  and took FURIA to three maps on day 2.

### Third place — 18 Oct 11:30Z (Bo3) · Final — 18 Oct 15:00Z (Bo5)

HLTV pages 2399416 and 2399417. Not on the Hotspawn feed and not priced at the check;
the pipeline will pick them up automatically when Hotspawn lists them (see §5).

### Row-level day-4 picks (Hotspawn rows)

| Hotspawn row | Fixture | Pick | Basis |
|---|---|---|---|
| 1081515 | Apogee Betclic vs Nemesis, PGL Bucharest 2027 CQ UB semi, 14:00Z | **Nemesis** | Exchange, market 5776037 — 0.32 / 0.68 at the 19:35Z read, **0.305 / 0.695** at the 19:50Z refresh |
| 1081888 | NIP vs Heroic, Stake Pulse Beat III | NIP | Exchange; exchange makes Heroic the favourite, our read leans NIP on rest/travel grounds |
| 1081513 | Bebop vs Donstu, CCT Europe 2026 Challengers #8 | Bebop | Model only — no exchange, Pinnacle or HLTV line exists |

---

## 4. Coverage fix: the renamed-club row

At the start of this session **one open row had no pick at all**: `1081515`,
"Apogee Betclic vs Nemesis". Its own attempt record named the near-miss: Hotspawn
writes **Apogee Betclic**, HLTV writes **Betclic** (team 12916), and Polymarket writes
**Betclic Apogee Esports**. The identity gate rejected the match rather than guess.

Fix — primary-source alias, no fuzzy matching:

- HLTV match page confirming the labels and the pairing:
  <https://www.hltv.org/matches/2399660/betclic-vs-nemesis-pgl-bucharest-2027-closed-qualifier>
  (Betclic team 12916, Poland; Nemesis team 13355, Russia; Bo3 online, UB semi,
  PGL Bucharest 2027 Closed Qualifier, event 9449).
- Official market: <https://gamma-api.polymarket.com/markets/5776037> — event 1200120,
  outcomes `["Betclic Apogee Esports","Team Nemesis"]`, `gameStartTime`
  `2026-10-17 14:00:00+00`, liquidity $3,296.78, spread 0.04.
- Corroborating org label: Hotspawn team page
  <https://www.hotspawn.com/counter-strike/teams/betclic-apogee-esports>.
- `data/identities.json`: `Betclic` added to the **existing** `Betclic Apogee Esports`
  entry (an earlier session had already registered that canonical — no duplicate was
  created), plus a new `Nemesis` / `Team Nemesis` entry. Both carry `source`,
  `additional_source`, `basis` and `reviewed_at: 2026-10-16`.

Result, verified by a live CI refresh at **2026-10-16T19:50:21Z**:
row `1081515` → pick **Nemesis**, probabilities **0.305 / 0.695**, method `exchange`,
fair odds 3.279 / 1.439. The gate still requires both team labels *and* the exact UTC
start to match, so the alias cannot bridge a different opponent or a shifted start —
both cases are pinned by tests.

The identity fix is narrow on purpose. Valve's standings list `Nemesis` (#29, 1455
points) but not `Apogee Betclic`, which is why the model could never originate a line
for this fixture; only the market could price it.

---

## 5. Coverage and cadence

- Discovery is automatic: every refresh pulls Hotspawn's fixtures API and its lobby
  JSON, so a new CS2 match appears without human input.
- Cadence: `.github/workflows/pages.yml` runs at **:04, :19, :34, :49 past each hour**
  (within the 4–8 hour requirement, and well inside the 8-hour expiry gate
  `core.MAX_AGE`), with `refresh-watchdog.yml` re-triggering if the published board
  goes stale.
- Pricing ladder per row: Polymarket (exact labels + exact UTC start, with freshness,
  spread, liquidity and sum gates) → Pinnacle esports moneylines → the same exchange
  pass with a wide-spread allowance (`exchange_wide`) → bookmaker probes → our Valve
  standings model (`model_vrs`) → single- or two-sided HLTV ranking research. A row
  that reaches the end gets a **blank percentage**, never a default 50/50.
- Verified at the 19:50Z refresh: **83 rows sourced, 21 open, 17 priced, 4 with a
  research pick and no percentage, 0 with no pick at all.**

---

## 6. Unresolved picks and their limitations (as published)

Four open rows carry a pick and **no percentage**. They are listed in the executive
summary (`index.html#unresolved-summary`), on `unresolved.html`, and per row on
`evidence.html`.

| Row | Fixture | Pick | Why no percentage |
|---|---|---|---|
| 1081521 | ex-6666 vs Privateer, CCT Europe 2026 Challengers #8, 18 Oct 13:45Z | ex-6666 | Two-sided HLTV ranks exist (ex-6666 #80, Privateer #226) but no market line and neither team is in Valve's standings |
| 1081522 | antidaun vs Phantom Academy, same event, 18 Oct 13:45Z | Phantom Academy | Only one side is world-ranked (#178); one-sided ranking evidence is not a probability |
| 1081861 | Lynn Vision vs Morningstar, VOID Autumn Cup 2026, 20 Oct 03:00Z | Lynn Vision | One-sided ranking only (Lynn Vision #39); no market line; Morningstar absent from standings |
| 1081863 | Chinggis Warriors vs WXM, same event, 20 Oct | Chinggis Warriors | One-sided ranking only; no market line; WXM absent from standings |

Provider-level limitations, measured in the same refresh and now published in the
executive summary (`index.html#access-limitations`):

- **Polymarket** — 4 of 4 rows: no market in the active CS2 series carried both exact
  labels at the exact UTC start. Full registry queried; nothing matched fuzzily.
- **Pinnacle** — 4 of 4 rows: no matchup carried both labels at this start.
- **HLTV** — 4 of 4 rows: the odds-comparison table exposed no numeric two-way line.
  Ranks and lineups were read and published as context; no rank-to-probability formula
  is applied, so this is not a hidden line.
- **Thunderpick** — 4 of 4 rows: HTTP 200, but odds are rendered client-side, so no
  server-side quote could be extracted. Collection limitation, not evidence the odds
  do not exist. No bot protection bypassed.
- **GG.BET** — 4 of 4 rows: HTTP 403 Forbidden. Nothing read, nothing implied. No bot
  protection bypassed.
- **Our originated model line** — 4 of 4 rows: at least one side is absent from
  `standings_global_2026_10_05.md`, which also predates this week's results.
- **EGamersWorld** (probed by this session's research workflow, not by the refresh):
  403. Its BetBoom-vs-Legacy line that priced row 1081526 earlier had already lapsed
  after ~8 hours, and that row is now `exchange_wide` on its own merits.

### Flagged for review

1. **BETBOOM vs Legacy (2399413) had no published result 3 hours after its 17:00Z
   start**, so the day-4 semi-final-2 opponent is published as two conditional cards.
2. **Inferno 13-4 in the day-3 decider is secondary-corroborated only**
   (dust2.com.br, EGamersWorld); HLTV's page fetch exposes per-map player tables but
   not scorelines in the retrievable chunks.
3. **HLTV genuinely publishes no two-way odds for these fixtures — verified, not
   assumed.** The first reading this session was wrong and is corrected here: it
   suspected a stale selector because all 19 harvested pages returned zero numeric
   rows. A DOM capture run for that purpose
   (`research/harvest-621776e4/hltv-betting-dom.json`, pages 2399660 and 2399681, both
   HTTP 200) shows `.match-betting-list tr.provider` **matches exactly one row** on
   both pages, and that row is a Stake promotional entry whose odds cell is
   `<td class="noOdds" colspan="2">` containing promo copy. The extractor is correct;
   HLTV's odds comparison carries no numbers for these matches. `scripts/hltv.py` was
   therefore **not** changed.
4. **Bookmaker access from the CI runner**: gg.bet 403, egamersworld 403;
   thunderpick.io and rivalry.com return 200 with client-side-only odds.
5. **Pinnacle name collisions**: `9z` and `FURIA` appear in other sports
   (matchup 1638481921 is Rainbow Six), so Pinnacle matches are gated on league and
   exact start as well as labels.

---

## 7. What was run, and what came back

| Check | Command | Result |
|---|---|---|
| Unit + integration tests | `.venv/bin/python -m unittest discover -s tests` | **206 tests, OK** (195 baseline + 11 new in `tests/test_priced_coverage_621776e4.py`) |
| Audit suites | `unittest discover -s verification-c6` / `-95b588c2` / `audits` | 12 OK / 5 OK / 9 OK |
| Site build | `python -m scripts.build --data research/harvest-621776e4/snapshot.json` | 9 primary pages + 6 legacy redirects, 83 sourced rows, 17 priced, 4 unresolved |
| Validator | `python -m scripts.validate --data …/snapshot.json` | pass — 571 internal links and assets checked, 203 displayed rows verified, 20 artifact checksums |
| Live end-to-end refresh | CI `harvest-621776e4.yml`, run 38957800101 | success; snapshot 19:50:21Z; row 1081515 priced 0.305/0.695 |
