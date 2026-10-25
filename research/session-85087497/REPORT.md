# Session 85087497 — picks for every Hotspawn CS2 match (2026-10-25)

## Executive summary

**Where the updated picks are (phone-first):**
[Executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/#exec-summary) ·
[Updated picks — the full board](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html) ·
[Every pick on the landing page](https://buffedlizard55-lab.github.io/MaltaProj4/#picks-at-a-glance) ·
[Unresolved picks & limitations](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html)
(also as a section inside the summary:
[#unresolved-summary](https://buffedlizard55-lab.github.io/MaltaProj4/#unresolved-summary)) ·
[All matches](https://buffedlizard55-lab.github.io/MaltaProj4/matches.html) ·
[How we price](https://buffedlizard55-lab.github.io/MaltaProj4/sources.html#method) ·
[Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html)

**What was actually wrong.** At 13:27 UTC the live site showed “14 open · 0 with a
pick” — not because sources lacked lines, but because the publisher had been
failing since 06:56Z and the 01:47Z snapshot had aged out of its 8-hour window.
The harvest replay (run
[40197633940](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40197633940))
on a fresh 13:31Z snapshot found the board itself complete — 78 feed rows,
17 open, **17 with a pick and a win probability, 0 research-only, 0 unresolved**
(11 exchange · 1 wide exchange · 1 Thunderpick-via-BO3 bookmaker listing ·
4 Valve-VRS model) — and the publication gate failing on one assertion:
`scripts.validate` rejected fixture 1086697's model roster because HLTV's
exact-start fixture page names the club *Tropa do KinGui* while Hotspawn lists
*Projeto do KinGui* (identical starting five; a sourced `data/identities.json`
alias). The collector and the independent auditor already accept that alias;
the validator compared raw labels. A second blocker on the same board:
`picks.html`'s first probabilities rendered 12px below the fixed tab bar on a
320×568 phone (browser gate).

**What changed.**

1. Validator identity bridge — implemented independently here and, in parallel,
   by session b85ad9b4; **main's stricter version was adopted** on merge
   (`same_club`: exact label, or both spellings inside one identity-register
   entry that carries an https source, with the fixture's two teams kept
   distinct; the five players must still match exactly). This session's
   regression tests run against the merged implementation.
2. Short-phone layout: picks cards return ~34px of vertical chrome at
   ≤650×700px; first probabilities now end at y=443 vs the tab bar at y=507
   (was y=519). No font or content change.
3. Executive-summary clarity: the phone quick-nav count now reads
   “unresolved (no %)” (it counts rows without a percentage; the freshness
   strip's “unresolved” counts rows with no pick), and the always-visible
   summary bar gains a one-tap [How we price](https://buffedlizard55-lab.github.io/MaltaProj4/sources.html#method) link.
4. Fallback-source probe (`scripts/probe_85087497.py`, below) for future rows
   no market prices, plus two Flagged-for-Review notes.

**Unresolved picks & limitations (separate section, as briefed).** On the
fresh board there are **none**: 17/17 open rows carry a pick and a percentage.
When a row cannot be priced it appears, named with its reason and every
rejected source, in the executive summary's unresolved section and on
[unresolved.html](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html);
percentages stay **blank — never 50/50**. The standing limitations are listed
under “Limitations” below and on the site itself.

## How a pick is produced for a match no featured market covers

Order exactly as `scripts/refresh.py` runs it (probabilities never come from
Hotspawn):

1. **Polymarket exchange** (tight, funded, fresh two-way series market; exact
   pair + exact UTC start).
2. **HLTV research** — exact fixture identity, lineups and rankings (context;
   HLTV votes and rank numbers are never a price).
3. **Pinnacle** esports moneyline (guest API), de-vigged.
4. **Wide exchange quote** — labelled low-confidence, real spread published,
   liquidity floor kept.
5. **Thunderpick / GG.BET access attempts** — recorded per row; no validated
   automated quote is extractable from their public pages (see limitations).
6. **Researched/automated book listings** — Thunderpick series odds via the
   public BO3.gg API (`scripts/bo3.py`, exact pair+start, de-vigged) and dated
   EGamersWorld/СТАВКА receipts re-observed before use (`scripts/books.py`);
   the identical 1.8/1.8 placeholder pair is refused.
7. **Our originated model line** — Valve's official VRS standings points through
   Valve's published formula/calibration (`model_vrs`), rosters confirmed by
   HLTV lineups; then the same formula on HLTV's dated Valve-ranking mirror
   (`model_vrs_mirror`) for clubs newer than Valve's monthly file.
8. **Research picks with no percentage** — HLTV world-ranking order
   (both/one team), one-sided Valve standings presence, then HLTV recent
   form / head-to-head from the fixture's own match page.
9. **Unresolved** — blank probability, pick empty only if nothing sourced
   supports one, with every attempt and its rejection gate published.

On the 13:31Z board this ladder needed rungs 1, 4, 6 and 7 only.

### Additional sources researched this session (for rung-9 rows)

`scripts/probe_85087497.py` runs in the harvest on a GitHub runner and records
receipts (URL, HTTP status, bytes, sha256) in
`research/harvest-85087497/probe.json`:

- **Kalshi public Trade API** — market data needs no key
  ([docs.kalshi.com quick start](https://docs.kalshi.com/getting_started/quick_start_market_data));
  CS2 dominates Kalshi's esports volume
  ([Esports Insider, 2026-07-03](https://esportsinsider.com/2026/07/kalshi-esports-prediction-markets-june-2026)).
  **Measured 2026-10-25T14:01Z** (probe receipts in
  `research/harvest-85087497/probe.json`): 15,393 series listed keylessly;
  the moneyline series **KXCS2GAME held 120 open markets = 60 paired
  two-sided events** (one “<Team> wins” Yes/No market per side,
  `yes_sub_title` naming the team). Paired by `event_ticker` and matched with
  the project's exact-label/register rule (`scripts.core.norm`, never
  substring), **11 of the 16 open Hotspawn fixtures have an exact Kalshi
  event**, including low-tier DFRAG/CCT rows — e.g. B8 vs K27
  (`KXCS2GAME-26OCT270400K27B8`, bids/asks 0.57/0.60 and 0.39/0.41). Two
  near-misses are correctly excluded by exact labels: BESTIA vs paiN (Kalshi
  titles read “BESTIA Academy wins”) and Projeto do KinGui vs Yawara (Kalshi
  side is an abbreviation, `YawTDKG`). Start identity is the hard part an
  adapter must solve, and the data proves why: for 10 of the 11 matches,
  Kalshi's `expected_expiration_time` is exactly Hotspawn start + 4h (and the
  ticker encodes the US-Eastern start), but for BORRACHEIROS vs RED Canids
  Academy Kalshi's fields imply a 19:00Z start against Hotspawn's 16:00Z —
  under this project's exact-start rule that event must be **rejected**, not
  borrowed. Spreads also vary from tight (0.03) to unusable (Rooster
  0.31–0.55, Off Chops 0.51–0.79), so the Polymarket spread/liquidity/age
  gates would have to apply unchanged. **Decision:** no fixture on the
  current board needs Kalshi (0 unpriced), and wiring a new exchange into the
  validator + independent auditor is a session-sized change that must not be
  rushed into the publisher on the day it was unblocked. The probe now
  measures paired coverage on every harvest (`paired_events_by_series`,
  `exact_pair_leads`), and the adapter design is flagged for review with
  these receipts. (First probe version found 0 leads because it required both
  team names inside one market's text — Kalshi never puts them there; the
  pairing correction is unit-tested offline against the retained markets.)
- **HLTV dated world-ranking page**: a single plain request from the runner
  to `https://www.hltv.org/ranking/teams/2026/october/25` answered **HTTP 403**
  at 14:01Z (5,650 bytes, receipt in `probe.json`). The production collector's
  HLTV reads are paced and retried (`scripts.refresh.Sources`) and mostly
  succeed; the standalone ranking view is therefore recorded as
  rate-limit-sensitive and is **not** used as a price source — ranking order
  already feeds the research-only rung through HLTV fixture/team pages, and
  no published calibration exists to turn HLTV ranking points into an honest
  win percentage, so none is invented.
- **Keyed aggregators** (odds-api.io, oddspapi, PandaScore/GRID-style feeds)
  cover books such as GG.BET/Thunderpick/Bet365 but require an API key/account;
  the brief requires no manual input and this project holds no such key, so
  they are a recorded limitation, not an adapter. Example of the shape:
  [odds-api.io CS2](https://odds-api.io/esports/cs2).
- HLTV's own match pages expose no independently confirmed numeric two-way
  line to this collector (standing finding, re-stated on the method page);
  HLTV fan votes are never used.

## Line-by-line verification of the fresh board (2026-10-25T13:31:28Z snapshot)

Every row below was re-derived from the retained raw evidence in
`research/harvest-85087497/refresh-snapshot.json`; the independent auditor
(`verification-c6/audit_snapshot.py`) reports **0 failures** on the same file,
and `scripts.validate` passes after the fix. Exchange rows: published
probabilities equal the raw `outcomePrices` (orientation re-checked — e.g.
1082697's market lists paiN first and is flipped to the Hotspawn order) and sum
to 1. Book row: probabilities de-vig from the stored decimal odds. Model rows:
points/standings from Valve's 2026-10-05 file at commit `eec4853`, formula
replayed by the validator.

| Fixture | Start (UTC) | Match | Method | Pick | Win % (team1/team2) | Source |
| --- | --- | --- | --- | --- | --- | --- |
| 1085542 | 25 Oct 14:00 | ex-Zero Tenacity vs Spirit Academy | exchange | ex-Zero Tenacity | 59.5 / 40.5 | [Polymarket](https://polymarket.com/event/cs2-zerote-tsa-2026-10-25) |
| 1079199 | 25 Oct 15:00 | Infinite vs BRUTE | exchange | BRUTE | 43.5 / 56.5 | [Polymarket](https://polymarket.com/event/cs2-inf6-brute-2026-10-25) |
| 1086696 | 25 Oct 16:00 | BORRACHEIROS vs RED Canids Academy | exchange | RED Canids Academy | 42.5 / 57.5 | [Polymarket](https://polymarket.com/event/cs2-chama-reda-2026-10-25) |
| 1079200 | 25 Oct 18:00 | Color vs ex-Zero Tenacity | model_vrs (1249 vs 1066 pts) | Color | 68.8 / 31.2 | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |
| 1081158 | 25 Oct 18:00 | FORZE Reload vs ex-RUSTEC | exchange | FORZE Reload | 56.5 / 43.5 | [Polymarket](https://polymarket.com/event/cs2-forzer-rustec-2026-10-25) |
| 1082697 | 25 Oct 18:00 | BESTIA vs paiN | exchange | paiN | 42.5 / 57.5 | [Polymarket](https://polymarket.com/event/cs2-pain-bst-2026-10-25) |
| 1086697 | 25 Oct 19:00 | Projeto do KinGui vs Yawara | model_vrs (854 vs 845 pts) | Projeto do KinGui | 51.0 / 49.0 | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) + HLTV lineup under the register alias “Tropa do KinGui” |
| 1082858 | 26 Oct 03:00 | Ground Zero vs Off Chops | exchange | Off Chops | 35.5 / 64.5 | [Polymarket](https://polymarket.com/event/cs2-gz1-offcho-2026-10-25) |
| 1082859 | 26 Oct 03:00 | NEXVOID vs Alter Ego | bookmaker listing (Thunderpick via BO3.gg, 1.60/2.20, 8.0% overround) | NEXVOID | 57.9 / 42.1 | [BO3.gg match](https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026) |
| 1082860 | 27 Oct 03:00 | FlyQuest vs Staqued | exchange | FlyQuest | 92.5 / 7.5 | [Polymarket](https://polymarket.com/event/cs2-fly-staque-2026-10-26) |
| 1082861 | 27 Oct 03:00 | Rooster vs Abyssal | wide exchange (spread 0.26, labelled) | Abyssal | 42.0 / 58.0 | [Polymarket](https://polymarket.com/event/cs2-rstr-abyssa-2026-10-26) |
| 1082897 | 27 Oct 08:00 | B8 vs K27 | exchange | B8 | 59.5 / 40.5 | [Polymarket](https://polymarket.com/event/cs2-b8-k271-2026-10-27) |
| 1082898 | 27 Oct 11:00 | Alliance vs FaZe | exchange | FaZe | 37.5 / 62.5 | [Polymarket](https://polymarket.com/event/cs2-all-faze-2026-10-27) |
| 1082900 | 27 Oct 17:00 | Luminosity vs HOTU | exchange | Luminosity | 52.5 / 47.5 | [Polymarket](https://polymarket.com/event/cs2-lg6-hotu-2026-10-27) |
| 1082901 | 27 Oct 20:00 | Envy vs GamerLegion | exchange | GamerLegion | 45.5 / 54.5 | [Polymarket](https://polymarket.com/event/cs2-envy-gl1-2026-10-27) |
| 1082792 | 31 Oct 09:00 | HOTU vs The Huns | model_vrs (1437 vs 944 pts) | HOTU | 85.2 / 14.8 | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |
| 1082793 | 31 Oct 13:00 | 5star vs 1WIN | model_vrs (1110 vs 1383 pts) | 1WIN | 24.3 / 75.7 | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |

Fixture identity for every row: the Hotspawn fixtures feed and lobby
(`https://play.hotspawn.com/lobby`, `https://play.hotspawn.com/cs2-pickems`)
plus each row's Hotspawn match page, retained in the snapshot's
`fixture_sources` with sha256 receipts.

## Phone measurements (Chromium, `research/session-85087497/measure-*.cjs`)

| Viewport | Board | Exec quick-nav (first screen) | Picks-at-a-glance starts | picks.html first probabilities |
| --- | --- | --- | --- | --- |
| 320×568 | stale 01:47Z (before) | y=380, “0/14 picks · 14 unresolved” | y=439 | **y=519 bottom — under tab bar (507)** on the fresh board before the CSS fix |
| 320×568 | fresh 13:31Z (after) | y=290, “17/17 picks · 0 unresolved (no %)” | y=361 | **y=443 bottom — 64px clear** |
| 390×844 | fresh (after) | y=300 | y=368 | clear (browser suites pass) |
| 412×915 | fresh (after) | y=300 | y=368 | clear (browser suites pass) |

No horizontal overflow at 320/390/412 on index, picks or unresolved
(`mobile-before.json` / `mobile-after.json`, `picks320-*.json`).

## Limitations (why a future row can still publish no percentage)

- No accessible book lists the match: Polymarket and Pinnacle are the keyless
  machine-readable lines; Thunderpick odds arrive via BO3.gg only when
  BO3 lists the fixture with active `bet_updates`; GG.BET answers datacenter
  IPs 403; EGamersWorld frequently serves the identical 1.8/1.8 placeholder,
  which is refused. Keyed aggregator APIs need an account this project does
  not hold (no manual input allowed by the brief).
- A market exists but fails a gate (stale update, spread >25pts — 60 in the
  labelled wide tier — or <$100 liquidity): shown as a rejected observation,
  never a percentage.
- Exactly even two-way prices carry no direction: the ladder continues to
  books/model instead of inventing a pick from a coin-flip quote.
- Names differ between sites: only exact pair + exact UTC start, or a sourced
  identity-register entry, may move a price between sources.
- HLTV confirms identity/lineups/rankings but exposes no confirmed numeric
  two-way line; HLTV votes are never used.
- The VRS model needs both teams resolvable in Valve's standings (or HLTV's
  dated mirror) with roster continuity; duplicated labels that Valve's own
  rule cannot separate degrade to research-only or unresolved.
- Timing: every percentage expires at the earliest of its 8-hour evidence
  window, the Hotspawn lock, match start or book cutoff. Refresh is scheduled
  every 15 minutes in `pages.yml` (cron `4,19,34,49`) plus a watchdog —
  inside the briefed 4–8h promise — but a multi-hour gate failure like
  2026-10-25's withholds picks by design rather than serving stale numbers.
- Pages remains `build_type: legacy`, source `main:/` (API-verified
  2026-10-25); the guarded root-fallback staging step is therefore part of
  the delivery path and must stay green.

## Verification performed

- Committed tree before changes: 1,606 unit tests OK, `validate --site .` rc=0,
  independent audit 0 failures — the defect was fresh-snapshot-specific.
- Harvest 40197633940 (fresh 13:31Z): reproduced the exact failing gate;
  coverage 17 open / 17 picked / 17 priced / 0 unresolved.
- After fixes, locally on the fresh snapshot: `validate` rc=0, audit 0 failures,
  `npm run test:browser` — all 13 suites pass.
- `pages.yml` on this branch, run
  [40199003224](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40199003224):
  **success** end-to-end (unit → refresh → quarantine → build/validate →
  browser) on a runner-fresh snapshot.
- After merging `main` (b85ad9b4's alias bridge adopted, a7f788c8's
  artifact-ready deploy guard, #313's browser-gate tolerance): 1,630 unit
  tests OK (12 skipped), audits 9 OK, integrity 5 OK, verification-c6 12 OK,
  `validate --site .` rc=0 on the restaged root.
- Harvest [40199883762](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40199883762)
  on the merged tree (fresh 2026-10-25T14:01:00Z snapshot): 16 open / 16
  picked / 16 priced / 0 unresolved (fixture 1085542 had locked), refresh,
  quarantine (withheld 0), build, `validate` (fresh and staged-root) rc=0,
  both row audits 0 failures, all browser suites pass. Its staged-root unit
  gate exposed one more latent freeze of the same family:
  `test_session_0fae12a5` assumed every model row's roster `overlap` is an
  integer, but at 14:01Z HLTV pacing withheld 1086697's lineup and the model
  legitimately published with `overlap=None` under unique standings labels
  (the validator's own contract). The test now mirrors that contract
  (None ⇒ label count 1; otherwise ≥3) and passes on both snapshots.
- HARVEST4_TODO

## Flagged for review (non-blocking)

- `session-85087497-validator-alias-freeze-2026-10-25` — root cause, the
  validator/collector identity alignment (merged form: b85ad9b4's
  `same_club`), and the standing alias-scope caveat.
- `session-85087497-short-phone-picks-fold-2026-10-25` — the 12px fold
  deficit, the chrome-only compaction, the remaining headroom and what could
  exhaust it; plus the “unresolved (no %)” wording and the new method link.
- `session-85087497-kalshi-fallback-probe-2026-10-25` — Kalshi KXCS2GAME
  paired-event coverage (11/16 exact), the BORRACHEIROS start-time conflict
  that an adapter must reject, spread range, and the decision to ship the
  measuring probe before any pricing adapter; plus the `overlap=None`
  staged-root test fragility found at 14:01Z and the HLTV ranking-page 403.
