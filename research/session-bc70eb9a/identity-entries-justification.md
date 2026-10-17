# bc70eb9a — data/identities.json additions: justification (checked 2026-10-17 ~20:55–21:10 UTC)

Claimed in COORDINATION.md (bc70eb9a claim extension, ~20:35 UTC). **Two additive entries only**; no
existing entry is modified. Both are *renamed-team* mappings of the same class as the existing
`6666`/`ex-6666` entry (added 2026-10-16), and both rely on the roster-overlap test that Valve
publishes in its own standings code (`model/team.js`, `TEAM_OVERLAP_TO_SHARE_ROSTER = 3`, verified at
commit `eec4853d7bcf0f1f7efe7f0d901234bef7e98b75`), not on name similarity.

How the pipeline consumes this: `scripts/core.py` `norm()` folds every `names[]` entry of an alias
record onto `canonical`; `scripts/vrs.py` `identify()` compares `norm(row.name)` against
`norm(board team)` and, when a lineup is available, re-checks roster overlap ≥ 3 before pricing.
So a verified entry in this register is what lets the VRS model price board rows whose Hotspawn
label does not literally appear in Valve's standings. No code change is involved.

## Entry 1 — `THUNDER dOWNUNDER` (canonical) ↔ `Off Chops`

- **Board row:** Hotspawn fixture 1081519, "NEXVOID vs Off Chops", DFRAG Logitech G Pro Series 2026,
  start `2026-18T03:00:00Z` (board feed, read 2026-10-17 ~20:20 UTC; row absent from the 11:23Z
  published snapshot, present in the ~20:20Z lobby).
- **HLTV fixture:** match 2399547 "NEXVOID vs Off Chops", DFRAG Logitech G Pro Series 2026
  (event 9437), displayed 23:00 on 17 Oct — i.e. 03:00Z (HLTV displayed in US Eastern in this
  sandbox; the 4-hour offset reconciles exactly with the board start, so no irregularity):
  <https://www.hltv.org/matches/2399547/nexvoid-vs-off-chops-dfrag-logitech-g-pro-series-2026>
- **HLTV team "Off Chops"** (14095): young team label, Valve #128 (Asia #12), no HLTV world rank,
  team period 6 days at read time: <https://www.hltv.org/team/14095/off-chops>
- **HLTV team "THUNDER dOWNUNDER"** (13486): **no active roster — dissolved** on HLTV (most recent
  event IEM Cologne 2026): <https://www.hltv.org/team/13486/thunder-downunder>
- **Off Chops lineup** (HLTV 2399547, read 2026-10-17): viridian, dexter, Liazz, Gratisfaction, damyo.
- **Valve standings row** (2026-10-05 snapshot, global #119, Asia #10, 971.3 pts), official detail
  file at commit `eec4853d`: dexter, Gratisfaction, Liazz, TjP, viridian —
  <https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0119--thunder_downunder--dexter-gratisfaction-liazz-tjp-viridian.md>
- **Overlap: 4 of 5** (dexter, Gratisfaction, Liazz, viridian; TjP replaced by damyo) ≥ 3 ⇒ same team
  under Valve's published rule.
- **Uniqueness:** a full scan of all 380 rows of the 2026-10-05 global standings (vendored in
  `data/vrs/standings_global_2026_10_05.md`, meta commit `eec4853d`) found **no other row** sharing
  ≥ 3 players with the Off Chops lineup, so `identify()`'s uniqueness test selects exactly one row.
- **Opponent sanity:** NEXVOID itself is an exact standings label (global #113, 995 pts; detail file
  <https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0113--nexvoid--accuracytg-erkast-miq-xerolte-zesta.md>)
  and needs no alias.
- **Scope:** CS2 main-team label only; exact opponent pair and UTC start still required per match.
  No academy/junior inference.

**Expected pipeline output once merged and a refresh runs** (model_vrs, Valve formula, RD 75,
Glicko expected score then the repo's calibration `p = 0.5 + 0.7986*(E − 0.5)`):
NEXVOID 995 vs THUNDER dOWNUNDER 971 → E = 0.53355 → **NEXVOID 52.68% / Off Chops 47.32%**,
pick NEXVOID. (Computed 2026-10-17 for cross-check only — the pipeline must produce the number,
it is not hardcoded.)

## Entry 2 — `Strael Bora` (canonical) ↔ `antidaun`

- **Board row:** Hotspawn fixture 1081522, "antidaun vs Phantom Academy", CCT Europe 2026
  Challengers #8, start `2026-10-18T13:45:00Z` (11:23Z published snapshot, state open,
  method `research_rank_single`, no probability).
- **HLTV fixture:** match 2399682 "antidaun vs Phantom Academy", CCT 2026 Challengers Europe Series 8,
  displayed 09:45 on 18 Oct — i.e. 13:45Z, exact board match:
  <https://www.hltv.org/matches/2399682/antidaun-vs-phantom-academy-cct-2026-challengers-europe-series-8>
- **HLTV team "antidaun"** (14085): **no active roster on the team page** (placeholder silhouettes,
  no VRS, no HLTV world rank), 25% win rate last 3 months, recent results listed
  (beat Noir Verse 2-0 on 16 Oct, match 2399472; lost to mellren 2-0 on 17 Oct, match 2399476):
  <https://www.hltv.org/team/14085/antidaun>
- **HLTV team "Strael Bora"** (13546): **no active roster — dissolved** on HLTV (timeline showed
  5 Star / maddeN / newhope / AdaMmMm / svn with maddeN ~313 days, newhope ~319 days at read time):
  <https://www.hltv.org/team/13546/strael-bora>
- **antidaun lineup** (HLTV match 2399476, read 2026-10-17): newhope, AdaMmMm, levantino,
  Pedrinho2011, svn:
  <https://www.hltv.org/matches/2399476/mellren-vs-antidaun-cct-2026-europe-series-12-closed-qualifier>
- **Valve standings row** (2026-10-05 snapshot, global #217, Europe, 691.6 pts), official detail
  file at commit `eec4853d`: AdaMmMm, levantino, maddeN, newhope, svn —
  <https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0217--strael_bora--adammmm-levantino-madden-newhope-svn.md>
- **Overlap: 4 of 5** (AdaMmMm, levantino, newhope, svn; maddeN replaced by Pedrinho2011) ≥ 3 ⇒
  same team under Valve's published rule.
- **Uniqueness:** same full-standings scan as Entry 1 — **no other row** shares ≥ 3 players with the
  antidaun lineup.
- **Opponent sanity:** Phantom Academy is an exact standings label (global #172, 783 pts; detail file
  <https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0172--phantom_academy--ayteel-brain47-dr3nquu-kalyambys-stefienson.md>)
  and needs no alias.
- **Scope:** CS2 main-team label only; exact opponent pair and UTC start still required per match.
  No academy/junior inference. (The label "antidaun" is also not case-folded to anything else:
  no other Hotspawn board row uses an "antidaun" or "Strael" label.)

**Expected pipeline output once merged and a refresh runs:** Strael Bora 692 vs Phantom Academy 783
→ E(Phantom Academy) = 0.624713 → **Phantom Academy 59.96% / antidaun 40.04%**, pick Phantom
Academy (the same pick the current `research_rank_single` fallback already makes — the change adds
the missing two-way probability instead of changing the pick).

## Verification method (both entries)

1. Read the Hotspawn board row (lobby HTML + fixture feed) to fix the exact label, opponent, event
   and UTC start.
2. Read the HLTV team pages for both the board label and the candidate standings label — both old
   labels (THUNDER dOWNUNDER 13486, Strael Bora 13546) show "no active roster", i.e. dissolved,
   while both board labels (Off Chops 14095, antidaun 14085) are live young labels.
3. Read the current lineup of the board label from a recent HLTV match page (2399547 / 2399476).
4. Read the official Valve standings detail file (raw file at the pinned commit `eec4853d`) for the
   candidate row, and compare player-by-player (4/5 in both cases).
5. Scanned all 380 standings rows for any row with ≥ 3 shared players; none.

No line, probability or pick was taken from Hotspawn's vote data at any point.
