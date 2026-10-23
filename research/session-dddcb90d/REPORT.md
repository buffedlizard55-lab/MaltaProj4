# Session dddcb90d — research & verification report (2026-10-23 UTC)

Branch: `arena/dddcb90d-maltaproj4`. Every observation below is dated and
source-linked; nothing on this page is a probability input unless it passed the
standing gates (exact pair + exact UTC start, asymmetric two-way, ≤25-point
strict / ≤60-point wide spread with ≥$100 liquidity, 8-hour evidence window,
Valve VRS model only where labelled). Hotspawn crowd percentages and HLTV fan
votes are inventory/never inputs.

## 1. CI repair (done, pushed)

The scheduled publish was red on runs 39871808909 / 39886171791 because two
tests pinned research methods that the 2026-10-22T20:15Z refresh legitimately
moved within the documented research ladder (`1081149` → `research_vrs_single`).
Repairs (membership-only pins, pick/blank%/reason pins intact) are in
`tests/test_session_75ebd2d6.py` and `tests/test_session_13e99ca6.py`; local
suite 961 OK; regression pins in `tests/test_session_dddcb90d.py` (15 tests).

## 2. Blank-percentage rows: HLTV-first ladder, dated 2026-10-23

### 1081149 — FORZE Reload vs LFO 10 (research pick FORZE Reload, blank %)

| Source | Read at (UTC) | Observation | Verdict |
| --- | --- | --- | --- |
| HLTV [2399499](https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12) | ~05:25 | Betting table carries only Stake promo logos — no numeric two-way line; countdown 2h34m53s ⇒ start ≈ 08:00Z; "Pick a winner" 88.9/11.1 is a fan vote | no line; fan vote refused |
| Hotspawn fixture feed (committed board) | 2026-10-22 20:12 | `scheduled_start_time` 1792764000000 = 14:00Z, lock 13:54Z | conflict side A |
| Hotspawn lobby page | ~04:52 | card `Oct 23, 04:00` US Eastern (=08:00Z), `Locks in 03:01:49` (⇒07:54Z lock) | conflict side B |
| EGamersWorld [HiXMAaC8L](https://egamersworld.com/counterstrike/match/HiXMAaC8L/forze-reload-vs-_04jKZ07_4) | ~05:46 | title `23.10.2026 at 08:00`, countdown 2:14:08 ⇒ 08:00Z; odds still 1.8/1.8 placeholder with a **blank opponent slot** (adapter: parse miss) | refused |
| Polymarket [cs2-forzer-skr2-2026-10-23](https://gamma-api.polymarket.com/events?slug=cs2-forzer-skr2-2026-10-23) | ~05:40 | only FORZE event in the slot — opponent **Sökerorg**, `gameStartTime` 08:00Z (description text still 14:00Z) | opponent mismatch → no exact pair; nothing transferred |
| Pinnacle [league 237685](https://guest.api.arcadia.pinnacle.com/0.1/leagues/237685/matchups) | ~05:55 | CCT European Series 12 has exactly one matchup: Inner Circle Academy vs Spirit Academy — no FORZE/LFO | no exact pair |

Outcome: **blank percentage stays**; pick stays `research_vrs_single` FORZE
Reload. The six-hour start/lock disagreement is published as flagged review note
`session-dddcb90d-1081149-start-conflict-2026-10-23` (no value restated from it).

### 1082860 — FlyQuest vs Staqued (research pick FlyQuest, blank %)

| Source | Read at (UTC) | Observation | Verdict |
| --- | --- | --- | --- |
| HLTV [2399890](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026) | ~05:47 | betting table promo-only (Stake logos, "No promocode available"); fan vote 82.6/17.4 | no line; fan vote refused |
| Polymarket [market 6066520](https://gamma-api.polymarket.com/markets/6066520) (whole-match moneyline, event `cs2-fly-staque-2026-10-26`, created 2026-10-22T21:35:23Z — after the board's last refresh) | 05:38 | exact pair + `gameStartTime` 2026-10-27T03:00:00Z ✓, liquidity $126.21, acceptingOrders ✓, outcomePrices 0.51/0.49, **bestBid 0.07 / bestAsk 0.95 = 88-point spread** | **refused** (>60 wide ceiling; midpoint never converted); exchange tier prices it automatically if the book tightens before lock 2026-10-27T02:54Z |
| Pinnacle [esports leagues](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/leagues?all=false) | ~05:50 | no DFRAG league exists | no pair → refused |
| EGamersWorld [4kaAQWgKEx](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3) | ~05:57 | widget `1.001 / 12` (second value not a decimal → adapter parse miss by design); same page's EGWxxxBOT sentence says `1.012 / 11.945` — widget and sentence disagree | no receipt registered |

Outcome: **blank percentage stays**; pick stays `research_rank_single` FlyQuest.
Published as review note `session-dddcb90d-1082860-new-exchange-listing-2026-10-23`.

## 3. Coverage audit (lobby vs refreshed board)

Method: non-publishing harvest `.github/workflows/harvest-dddcb90d.yml` runs
`scripts.refresh` on the runner (the sandbox cannot reach the esports hosts),
then `scripts/probe_dddcb90d.py` writes `coverage-audit.{json,md}` under
`research/harvest-dddcb90d/`: fresh three-view counts (`inventory.discover`
parity over fixtures API + CS2 page + general lobby), added/removed ids against
the committed board, per-fixture start/lock diffs (the 1081149 conflict shows up
here mechanically), and the blank-% rows' state.

Carried irregularity from claim time: the 2026-10-23 ~05:00Z lobby read shows
**92 CS2 fixtures in the tier filter vs the board's 84 retained rows** (9-hour
stale board, red publish). The audit files and the post-merge scheduled refresh
reconcile this; any residual gap is flagged on `review.html`, never silently
normalised.

## 4. Mobile / phone first-screen fix (done, pushed)

`tests/browser_eaff7cce.cjs`'s stale-mode failures at 320×568 were fixed in the
claimed CSS scope (both byte-identical `assets/style.css` copies): stale-strip
links ordered first (CTA was y=575 > 504 limit), the stale `.fresh-state` line
that duplicates `#runtime-stale` hidden at phone width, banner/jump-nav/actions
compacted so `#picks-at-a-glance` lands ≈1600px < 1700px. All four browser
suites pass in both server-stale and server-fresh/client-stale states.

## 5. Line-by-line review output

- `data/review-notes.json`: +2 dated notes (1081149 start conflict; 1082860 new
  exchange listing refused at 88 points) — rendered on the Flagged for Review
  page by the existing build.
- Flags carried from claim time remain published by their owners' notes: red
  runs 39871808909/39886171791 (this session's repair), legacy pages run
  39847473264, 92-vs-84 coverage gap, HLTV mirror 403 recurrence, refused-listing
  metadata inconsistencies.
