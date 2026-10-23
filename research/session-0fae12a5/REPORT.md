# Session 0fae12a5 — full-coverage verification + discoverability audit

**Session:** `0fae12a5` · **Branch:** `arena/0fae12a5-maltaproj4` · **Base:** `origin/main be81768`
**Work window:** 2026-10-23 09:45–10:30 UTC · **Snapshot verified:** `2026-10-23T08:32:56Z` (92 rows)
**Live bytes at check time:** identical to `be81768` (`build-info.json` revision
`4716f970…`, `built_at 2026-10-23T08:32:56.949905Z`, 92 rows — fetched live 10:00Z).

Scope pledge (kept): this session edits only `COORDINATION.md`,
`research/session-0fae12a5/**` and `tests/test_session_0fae12a5.py`.
Shared outputs (`data/*`, root pages, `scripts/*`, workflows) are read-only in this session.
Sibling session `e141a921` (claim 09:45Z, harvest run `39934335176` in progress) owns
`research/session-e141a921/**`, `research/harvest-e141a921/**`, `scripts/probe_e141a921.py`,
`.github/workflows/harvest-e141a921.yml`, `tests/test_session_e141a921.py`,
`verification-e141a921/**` plus conditional scopes — **no file overlap** with this session.
The full fresh-feed diff is left to that session's runner harvest; this session verifies the
committed board and the live sources independently.

## 1. Result in one paragraph

**30 open fixtures, 30 picks, 30 win probabilities, 0 unresolved, 0 without a pick.**
Every open row's probability pair sums to 1, every fair-odds pair is the exact reciprocal,
every pick is the argmax, all 7 originated VRS lines recompute exactly from Valve's official
standings file (byte-identical vendored copy, sha256
`df96e7fc…ae61b`), both book lines de-vig exactly from their dated receipts, and all 30 open
fixture IDs match the live Hotspawn lobby's Closing Soon + Upcoming cards one-for-one
(checked ~09:55Z). The executive summary links to the updated picks in five places, carries the
separate unresolved/limitations section, and the phone layout (viewport, `mobile-tabs` bottom
bar with Home·Picks·Unresolved·Matches·Analysis, card breakpoints at 650px/360px) is present on
every main page. Two non-blocking flags: (a) no scheduled refresh/watchdog run since 07:20:51Z
(~2.5h delivery gap; board still fresh via push-triggered runs, inside the 8h window);
(b) lobby filter facets show 94 CS2 entries (B40/C54) vs snapshot 92 (B39/C53) — open set
unaffected (30/30 match), reconciled by the next automated refresh.

## 2. Line-by-line verification (all 30 open rows)

Machine-readable ledger: [`checks.json`](checks.json) (generated, not hand-typed).
Method mix: 20× `exchange`, 7× `model_vrs`, 2× `bookmaker_fallback`, 1× `exchange_wide`.

| # | Fixture | Pick | Prob. | Method | Verified |
| --- | --- | --- | --- | --- | --- |
| 1079655 | Nuclear TigeRES vs ILLYRIANS (CCT EU S11) | Nuclear TigeRES | 86.5/13.5 | exchange | Live Polymarket 6036897 09:58Z: same pair/BO3/comp/start 11:00Z, active, accepting, liq $6048, spread 0.02; live 0.85/0.15 vs snapshot 0.865/0.135 (08:28Z) — moved, pick unchanged |
| 1081148 | Inner Circle Academy vs Spirit Academy | Spirit Academy | 42.5/57.5 | exchange | Snapshot receipt 6033288 exact pair+start; math ✓ |
| 1081605 | Phantom Academy vs Banda chuya | Banda chuya | 48.0/52.0 | model_vrs | **End-to-end live check:** HLTV 2399699 live 10:05Z — same pair/event/BO3, start 07:00 ET disp = 11:00Z, betting table has NO numeric line, lineups exactly `[Brain47,Ayteel,Dr3nquu,kalyambys,La1roN]` / `[tomiko,maaryy,AdrieN,Showk,mwlky]`; VRS #172/783 vs #165/801 in official file; overlap 4/4; math ✓ |
| 1081606 | JiJieHao vs Eternal Fire | Eternal Fire | 44.5/55.5 | exchange | Snapshot receipt 6066473 exact pair+start; math ✓ |
| 1082926 | Isurus vs Hacha | Isurus | 69.0/31.0 | exchange | 6036925; math ✓ |
| 1082980 | LPH vs WBT Academy | WBT Academy | 35.5/64.5 | exchange | 6065781; math ✓ |
| 1083014 | K27 vs Virtus.pro | K27 | 56.5/43.5 | exchange | 6069288; math ✓ |
| 1082924 | BORRACHEIROS vs QUINTESSÊNCIA | BORRACHEIROS | 63.5/36.5 | exchange | 6036909; math ✓ |
| 1079657 | BakS vs BRUTE | BRUTE | 49.5/50.5 | exchange | Snapshot receipt; math ✓ |
| 1081150 | ex-RUSTEC vs Saint Sinners | ex-RUSTEC | 68.0/32.0 | exchange | Snapshot receipt; math ✓ |
| 1082693 | BESTIA vs Galorys | BESTIA | 58.5/41.5 | exchange | Snapshot receipt; math ✓ |
| 1082925 | BESTIA Academy vs RED Canids Academy | RED Canids Academy | 35.5/64.5 | exchange | Snapshot receipt; math ✓ |
| 1083025 | paiN vs Imperial | Imperial | 38.5/61.5 | exchange | Snapshot receipt; math ✓ |
| 1082923 | Alka vs LOS NINOS | Alka | 75.5/24.5 | exchange | Snapshot receipt; math ✓ |
| 1079193 | FOKUS vs ex-6666 | FOKUS | 78.5/21.5 | exchange | Snapshot receipt; math ✓ |
| 1079195 | Nuclear TigeRES vs FORZE Reload | Nuclear TigeRES | 59.0/41.0 | exchange | Snapshot receipt; math ✓ |
| 1082996 | Acend vs UNiTY | Acend | 53.3/46.7 | model_vrs | VRS #63/1197 vs #69/1167 in official file; overlaps 4/5; math ✓ |
| 1079198 | Metizport vs BakS | Metizport | 73.8/26.2 | model_vrs | VRS #53/1290 vs #100/1044; overlaps 5/4; math ✓ |
| 1079199 | Infinite vs BRUTE | BRUTE | 43.5/56.5 | exchange | Snapshot receipt; math ✓ |
| 1079200 | Color vs ex-Zero Tenacity | Color | 68.8/31.2 | model_vrs | VRS #57/1249 vs #93/1066; overlaps 5/5; math ✓ |
| 1082858 | Ground Zero vs Off Chops | Off Chops | 26.5/73.5 | exchange_wide | Spread 0.39 (fails strict ≤0.25, passes wide ≤0.60), liq $2494.45 ≥ $100, active+accepting, exact pair+start 2026-10-26T03:00Z; math ✓ |
| 1082859 | NEXVOID vs Alter Ego | NEXVOID | 57.1/42.9 | bookmaker_fallback | Receipt `egw-…-nexvoid-vs-alter-ego`, 1.61/2.14 obs. 05:07Z, HLTV 2399889 identity; de-vig exact; start 2026-10-26T03:00Z ✓ |
| 1082860 | FlyQuest vs Staqued | FlyQuest | 92.3/7.7 | bookmaker_fallback | Receipt `egw-…-flyquest-vs-staqued`, 1.001/12.0 obs. 05:05Z, HLTV 2399890 identity; de-vig exact; start 2026-10-27T03:00Z ✓ |
| 1082861 | Rooster vs Abyssal | Abyssal | 48.2/51.8 | model_vrs | Polymarket 6066525 correctly rejected (spread >60 ceiling, recorded); VRS #205/718 vs #195/734; overlaps 3/3 (≥3 rule); math ✓ |
| 1082897 | B8 vs K27 | B8 | 62.5/37.5 | exchange | 6024944; math ✓ |
| 1082898 | Alliance vs FaZe | FaZe | 34.0/66.0 | exchange | 6024952; math ✓ |
| 1082900 | Luminosity vs HOTU | Luminosity | 55.0/45.0 | exchange | 6024960; math ✓ |
| 1082901 | Envy vs GamerLegion | GamerLegion | 46.5/53.5 | exchange | 6037120; math ✓ |
| 1082792 | HOTU vs The Huns | HOTU | 85.2/14.8 | model_vrs | VRS #31/1437 vs #122/944 (duplicate "The Huns" #213/701 correctly rejected by lineup: 4 vs ≤2 overlap); overlaps 5/4; math ✓ |
| 1082793 | 5star vs 1WIN | 1WIN | 24.3/75.7 | model_vrs | VRS #80/1110 vs #38/1383; overlaps 5/5; math ✓ |

"Math ✓" = probabilities sum to 1 (±1e-9), fair odds are exact reciprocals, pick is the
argmax, and (VRS rows) raw+calibrated values recompute bit-for-bit with the documented formula.
All 62 `not_open` rows carry a `reason` and/or `flags` and publish no pick-as-recommendation.

### Dated external receipts (this session, primary sources only)

1. **Valve standings file** — fetched via `api.github.com` 2026-10-23 ~10:00Z at pinned commit
   `eec4853d7bcf0f1f7efe7f0d901234bef7e98b75`: byte-identical to `data/vrs/` vendored copy
   (sha256 `df96e7fc3cd91a2687ec08cac0128e50cc4e4e55346581679572e881d79ae61b`, 382 rows).
   All 14 VRS team rows (standing/points/roster) confirmed verbatim, including duplicate-label
   disambiguation (`Banda Chuya` #165 vs #373, `The Huns` #122 vs #213).
2. **Valve model code** — same commit: `model/fit.js` (`rd: 75`), `model/glicko.js`
   (`Q = ln(10)/400`, `g = 1/sqrt(1+3Q²·rd²/π²)`, `ev = 1/(1+10^(g(r-ro)/(-400)))`),
   `model/team.js` (`TEAM_OVERLAP_TO_SHARE_ROSTER = 3`). The board's formula, RD and
   3-player roster rule reproduce the official code exactly.
3. **Polymarket 6036897** (fixture 1079655) — live read 09:58Z, quoted above. Market stays
   active/accepting; the 1.5pt drift since the 08:28Z snapshot does not change the pick.
4. **Hotspawn lobby** — live read ~09:55Z: all 30 open IDs present in Closing Soon + Upcoming
   with matching pairs, competitions, tiers and lock countdowns (locks = start − 6 min,
   e.g. 11:00Z starts locking in 01:12:03 at ~09:48Z). Hotspawn crowd percentages were read
   for inventory context only and are never probability inputs.
5. **Hotspawn fixture feed** (`status=scheduled`) — live read ~10:00Z: newest entries
   (…1082897/1082898/1082900/1082901/1082792/1082793, through 2026-10-31) all in snapshot;
   no fixture ID above snapshot max `1083025` observed.
6. **HLTV 2399699** (fixture 1081605) — live read 10:05Z: identity/start/BO3 confirmed,
   betting table carries no numeric two-way line (only a Stake promo row), fan vote
   76.9/23.1 correctly unused, both lineups match the snapshot's `roster_checks` exactly.
7. **Deployed site bytes** — live `build-info.json` 10:00Z identical to committed `be81768`
   build (all 20 file hashes match).

## 3. Own-research resolution pass (rows without a pick)

**Zero rows needed it.** All 30 open rows already carry a pick with a reproduced probability
from a supported tier, so no new HLTV→esportsbook resolution was required and none was
attempted. Had any row lacked a pick, the ladder would have been: HLTV fixture/betting page →
Pinnacle guest API → bo3.gg / EGamersWorld / OddsPortal listings with exact-pair+UTC-start
identity, publishing a percentage only from a reproducible two-way line or the labelled VRS
model. The standing limitation catalogue (no book lists low-tier matches; wide/stale/thin
quotes rejected with numbers shown; no guessed aliases; HLTV votes never used; model needs
both teams in Valve standings) is published in the executive summary's
[limitations section](https://buffedlizard55-lab.github.io/MaltaProj4/#pick-limitations) and on
`unresolved.html`.

## 4. Executive summary / discoverability / mobile audit (read-only)

Checked against the committed build (identical to live bytes):

- **In-site links to the updated picks** (index.html): freshness strip CTA
  (`picks.html`, `#picks-at-a-glance`, `unresolved.html`), `exec-banner` buttons
  (Updated picks / Unresolved & limits / Flagged for review / All 92 / How we price),
  `exec-summary-links` nav, `jump-nav` anchors, coverage/CTAs — all present and pointing at
  real anchors (`#picks-at-a-glance`, `#unresolved-picks`, `#unresolved-summary`,
  `#pick-limitations`, `#coverage` all exist).
- **Separate unresolved/limitations section in the summary**: `#unresolved-summary` with the
  9-item `#pick-limitations` catalogue plus the live "lim-now" sentence; counts are
  runtime-regenerated (`data-count` spans), so prose cannot disagree with figures.
- **Phone readability**: `viewport` meta on all main pages; `nav.mobile-tabs`
  (Home·Picks·Unresolved·Matches·Analysis, `aria-current` set) hidden on desktop,
  `position:fixed` bottom bar at phone widths; breakpoints at 1150/850/650/360px turn tables
  into cards; buttons ≥44px touch targets. No `tabbar` class exists — earlier receipts used
  that word generically for `mobile-tabs`; no defect.
- **Stale banner**: `#runtime-stale` ("Snapshot expired… picks are withheld") is `hidden` in
  static HTML and revealed by JS only when stale; text scrapers show it but browsers do not
  while fresh. No defect.
- Counts rendered live match the snapshot (30 open · 30 picked · 30 priced · 0 unresolved;
  23 market + 7 model).

## 5. Refresh-cadence audit (4–8h requirement)

- Pipeline: `pages.yml` cron `4,19,34,49 * * * *` + `refresh-watchdog.yml` `*/10 * * * *`;
  8h evidence window; JS expiry at earliest of quote TTL / lock / start / cutoff.
- **Flag (non-blocking): no `schedule`-event run of either workflow since `39917123080`
  (2026-10-23T07:20:51Z, success); 0 queued/in-progress at 10:05Z.** Push-triggered runs kept
  the board fresh (08:32:56Z, ~1.5h old at check time — inside the 4–8h promise), but the
  ~2.5h schedule silence matches the repo's documented GitHub-delivery flakiness
  (`research/refresh-ab18fe2a/DIAGNOSIS.md`), not a code failure: the last three main runs
  (`39923464907`, `39924864346` + watchdogs) are green. Fix ownership stays with the
  workflow owners; this session does not touch `.github/workflows/*`. If the gap persists
  past the 8h window the site fails closed (stale banner + withheld picks) rather than
  serving expired lines as current.
- **Flag (non-blocking): lobby filter facets read 94 CS2 entries (B40/C54) at ~09:55Z vs
  snapshot 92 (B39/C53, all three views agreeing, `inventory_changes` empty).** The open set
  — the only part that carries picks — matches exactly (30/30 IDs, §2), and no ID above the
  snapshot max was observed in the live feed tail, so this is facet-vs-view counting (or two
  entries that entered after 08:29Z and await the next refresh), not missing picks. The
  sibling `e141a921` runner harvest will reconcile it; no action in this session.

## 6. Test coverage added

`tests/test_session_0fae12a5.py` (offline, snapshot-agnostic — pins invariants, never counts
or tier labels, per the 22–23 Oct deadlock lesson): probability/fair-odds/pick coherence for
every row; evidence + Hotspawn source link presence; official-host allowlist for probability
inputs (Hotspawn crowd data can never be a probability source); VRS formula/parameter
recompute against `scripts/vrs.py`; book de-vig recompute; exec-summary link/anchor,
unresolved-section and phone-layout contracts on the committed pages.

## 7. Irregularities for review (all non-blocking, none touch picks)

1. Scheduled-refresh delivery gap since 07:20:51Z (§5).
2. Lobby facet count 94 vs snapshot inventory 92 (§5).
3. Snapshot Polymarket prices drift from live (e.g. 6036897: 0.865/0.135 @08:28Z →
   0.85/0.15 @09:58Z) — expected market movement; snapshots are timestamped and expire.
