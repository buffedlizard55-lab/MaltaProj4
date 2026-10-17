# Board line hunt — 2026-10-17 (session bc70eb9a)

Objective: find a real, dated, citable two-way external line for the unpriced/open rows of the
Hotspawn CS2 board (snapshot 11:23Z: 90 rows, 25 open; three research-only rows) and for the two
day-5 TWC fixtures. Rule: Hotspawn vote data is never a probability source; a line must come from
an external market/book with a source URL; anything unverifiable stays blank and flagged.

All observations below were made 2026-10-17 between ~20:20Z and ~21:30Z (UTC), from this sandbox
via the fetch tools. Every "not found" is dated, not asserted.

## Row-by-row findings

### 1081519 — NEXVOID vs Off Chops (new row; DFRAG Logitech G Pro Series 2026; 2026-10-18T03:00Z)

- Board: row first visible in the ~20:20Z lobby read (absent from the 11:23Z snapshot).
  https://www.hotspawn.com/matches/ (board row 1081519, "NEXVOID vs Off Chops", B side x1.5).
- Fixture identity: HLTV match 2399547, DFRAG Logitech G Pro Series 2026 (event 9437), "Consolidation
  final", Bo3 LAN, displayed 23:00 on 17 Oct (= 03:00Z; HLTV displayed in US Eastern here).
  https://www.hltv.org/matches/2399547/nexvoid-vs-off-chops-dfrag-logitech-g-pro-series-2026
- HLTV betting section (betting/analytics/2399547): no numeric two-way line in the static response
  (bookmaker odds are JS-rendered; the page's only price content is a Stake promotion). The
  community vote on that page (78.3/21.7) is **not** a probability and was not used.
- EGamersWorld (/counterstrike/matches): **HTTP 500 at ~20:25Z and again at ~20:30Z** — site-side
  failure; no line obtained.
- Polymarket: no event for this fixture (slug lookups and the closed-semifinal search surface
  nothing; see TWC section for method). Pinnacle guest feed (sports/12): the only CS2 matchups
  listed at ~20:45Z were two "CS2 - STK Pulse Beat" fixtures (NiP–MIBR, others); no DFRAG row.
- **Resolution (data path, no market):** identity bridge — Off Chops is a renamed THUNDER
  dOWNUNDER (Valve global #119, 971.3 pts; 4/5 roster overlap, old roster dissolved on HLTV;
  full 380-row scan unique). See identity-entries-justification.md. Registered in
  data/identities.json (additive entry, claimed). The pipeline will originate the model line on
  its next refresh: expected NEXVOID 52.68% / Off Chops 47.32%, pick NEXVOID (pipeline-computed,
  not hardcoded; verified by replay on the vendored 2026-10-05 standings).

### 1081522 — antidaun vs Phantom Academy (CCT Europe 2026 Challengers #8; 2026-10-18T13:45Z)

- Board: open, method `research_rank_single`, pick Phantom Academy, **no probability** (11:23Z
  snapshot). https://www.hotspawn.com/matches/antidaun-vs-phantom-academy-cct-europe-2026-challengers-8-1081522
- Fixture identity: HLTV match 2399682 (same series, displayed 09:45 on 18 Oct = 13:45Z).
  https://www.hltv.org/matches/2399682/antidaun-vs-phantom-academy-cct-2026-challengers-europe-series-8
- HLTV betting section: no numeric two-way line in the static response (same JS-rendering
  limitation as above); the captured hltv_context in the snapshot (observed 2026-10-17T11:21Z)
  records `numeric_quote_rows: 0`.
- Polymarket: no market for this fixture (slug lookups empty; the CCT series had no event
  surfaced in the active-events scan retained by session 76712ccc either).
- Pinnacle: not listed (only STK Pulse Beat CS2 at ~20:45Z).
- EGamersWorld: HTTP 500 (as above).
- **Resolution (data path, no market):** identity bridge — antidaun is a renamed Strael Bora
  (Valve global #217, 691.6 pts; 4/5 roster overlap vs the HLTV lineup of match 2399476: newhope,
  AdaMmMm, levantino, Pedrinho2011, svn; old roster dissolved; scan unique). Registered in
  data/identities.json. Expected pipeline line: antidaun 40.04% / Phantom Academy 59.96%, pick
  Phantom Academy (same pick as the current research fallback; adds the two-way probability).

### 1081861 — Lynn Vision vs Morningstar (VOID Autumn Cup 2026; 2026-10-20T03:00Z)

- Board: open, `research_rank_single`, pick Lynn Vision, no probability.
- Market sweep: Polymarket — no market (no event for the VOID Autumn Cup in the active scan;
  slug guesses for 2026-10-20 returned nothing). Pinnacle — not listed. EGamersWorld — HTTP 500.
  HLTV betting — no numeric line in static response.
- **No data path either:** Morningstar is absent from **all 380 rows** of the Valve global
  standings of 2026-10-05 (full roster-overlap scan, zero shared players with any listed row;
  also absent from the region files retained by session 76712ccc). VRS cannot originate a line.
- **Status: stays blank + flagged** ("Research pick on one-sided ranking evidence... no
  probability published") — exactly the state the board already carries. Lynn Vision is listed
  (global #64, 1190 pts) but a line needs both teams.

### 1081863 — Chinggis Warriors vs WXM (VOID Autumn Cup 2026; 2026-10-20T07:00Z)

- Market sweep: same as 1081861 — no Polymarket/Pinnacle/EGW/HLTV numeric line found at
  2026-10-17 ~21:30Z.
- **Data path partially available, still blocked:** Chinggis Warriors **is** listed (global #87,
  1084 pts; the label appears twice in the standings, disambiguated by the HLTV lineup ROUX,
  sk0R, cool4st, tikuak, fury5k — 4/5 verified against #87). But **WXM is absent from all 380
  rows** (zero overlap scan). VRS therefore cannot originate a line.
- **Status: stays blank + flagged**, as on the board.

### 1081862, 1081864 (other VOID Autumn Cup rows)

- Already priced by earlier sessions' receipts (book research lines in data/book-receipts.json);
  nothing to do. No market change observed this session.

## Day-5 TWC fixtures (not yet on the Hotspawn board at 21:30Z — research-only)

### Grand final: FURIA vs BETBOOM (HLTV 2399417, 15:00Z, Bo5)

- Polymarket: **no market yet** (2026-10-17 ~20:40–21:00Z). Method and evidence:
  - Precedent: the TWC semifinal events were created the evening before (Falcons–BetBoom event
    1201748, slug `cs2-fal2-bb3-2026-10-17`, $5.13M volume, Map-1 market closed 18:17:02Z,
    match-winner resolved; FURIA–Aurora market 5778024 slug `cs2-furia-aur1-2026-10-17`, $827K
    volume, resolved 16:29:02Z, resolution source hltv.org).
  - Slug lookups for the final day returned empty: `cs2-fur2-bb3-2026-10-18`,
    `cs2-furia-betboom-2026-10-18` (both `[]` at ~20:45Z).
  - Conclusion (dated): Polymarket had not listed the grand final as of 21:00Z. The pipeline's
    Polymarket tier will pick it up automatically once listed (next refresh window 4/19/34/49).
- Pinnacle: no TWC league in the guest feed's league list at ~20:45Z (only LoL Worlds, Valorant
  Champions, MPL ID/MY, CS2 STK Pulse Beat, LoL Play-In).
- EGamersWorld: HTTP 500 (two attempts, ~20:25Z/~20:30Z).
- **No line to publish; the board has no row for this fixture yet either.** When both the board
  row and a market exist, the next refresh prices it; otherwise it lands as a flagged
  research-only row like 1081522 was.

### 3rd place decider: Aurora vs Falcons (HLTV 2399416, 11:30Z, Bo3)

- Polymarket: **no market yet** (same method; slug lookups `cs2-aurora-gaming-falcons-2026-10-18`
  and the `cs2-aur1-fal2-2026-10-18` pattern returned empty at ~20:45Z).
- Pinnacle / EGamersWorld / HLTV betting: same negative results as above (no numeric line in any
  static response; EGW 500).
- **No line to publish; not yet on the board.**

## Summary for the integrators

| Row / fixture | External line found? | Path to a number |
| --- | --- | --- |
| 1081519 NEXVOID–Off Chops | No market anywhere (dated attempts above) | **model_vrs via new identity entry** — expected 52.68/47.32, pipeline-computed next refresh |
| 1081522 antidaun–Phantom Academy | No market anywhere | **model_vrs via new identity entry** — expected 40.04/59.96, pipeline-computed next refresh |
| 1081861 Lynn Vision–Morningstar | No market anywhere | None — Morningstar unlisted in all Valve lists; stays blank + flagged |
| 1081863 Chinggis Warriors–WXM | No market anywhere | None — WXM unlisted in all Valve lists; stays blank + flagged |
| TWC GF (FURIA–BETBOOM) | No market yet (21:00Z) | Auto on next refresh once Polymarket/Pinnacle list it + board row exists |
| TWC 3rd place (Aurora–Falcons) | No market yet (21:00Z) | Same |

Irregularities logged: (1) EGamersWorld HTTP 500 on /counterstrike/matches at ~20:25Z and
~20:30Z (site-side, not request-side); (2) HLTV's betting-analytics pages expose no numeric
two-way odds in the static response for any fixture checked (JS-rendered) — qualitative only;
(3) Hotspawn's raw fixtures API still returns stale June-2026 data (known; the lobby HTML is the
current board) — not used for any probability; (4) no other irregularity found in the verified
TWC results (all 10 played matches reconcile with HLTV's own labels and clocks; the apparent
4-hour offset is HLTV's US-Eastern display, not a data conflict).
