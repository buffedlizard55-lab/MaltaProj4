# Day 4 and day 5 readiness — Thunderpick World Championship 2026 playoffs

Session `3c8d1136`, written 2026-10-16 ~08:20Z, i.e. while the two group deciders are still
open (14:00Z and 17:00Z). This is a readiness note: what is **verified**, what the board will
do **automatically** when the playoff fixtures appear, and what must stay **blank** until a
source publishes it.

## 1. The remaining four fixtures, verified from HLTV's own match pages

All four pages were read in this session; each shows the same event
([8932](https://www.hltv.org/events/8932/thunderpick-world-championship-2026)), a LAN venue
and a server-rendered countdown.

| Fixture | HLTV page | Displayed clock | Format | Stage | Teams known? |
|---|---|---|---|---|---|
| Semi-final 1 | [2399414](https://www.hltv.org/matches/2399414/furia-vs-aurora-9z-winner-thunderpick-world-championship-2026) | `10:00 · 17th of October 2026` | **Best of 3 (LAN)** | `* Semi-final` | [FURIA](https://www.hltv.org/team/8297/furia) vs *Aurora/9z winner* |
| Semi-final 2 | [2399415](https://www.hltv.org/matches/2399415/falcons-vs-betboom-legacy-winner-thunderpick-world-championship-2026) | `13:00 · 17th of October 2026` | **Best of 3 (LAN)** | `* Semi-final` | [Falcons](https://www.hltv.org/team/11283/falcons) vs *BETBOOM/Legacy winner* |
| 3rd place | [2399416](https://www.hltv.org/matches/2399416/thunderpick-world-championship-2026-3rd-place-decider-match-thunderpick-world-championship-2026) | `07:30 · 18th of October 2026` | **Best of 3 (LAN)** | `* 3rd place decider match` | both TBD |
| Grand final | [2399417](https://www.hltv.org/matches/2399417/thunderpick-world-championship-2026-grand-final-thunderpick-world-championship-2026) | `11:00 · 18th of October 2026` | **Best of 5 (LAN)** | `* Grand final` | both TBD |

### Deriving UTC — and exactly how far that derivation can be trusted

HLTV prints no timezone. The offset is anchored on the two fixtures whose UTC starts are
machine-verified from two independent sources:

* Aurora vs 9z — Hotspawn `scheduled_start_time 1792159200000` = **14:00:00Z**, Polymarket
  market 5733288 `gameStartTime "2026-10-16 14:00:00+00"`, while HLTV displays `10:00`;
* BetBoom vs Legacy — Hotspawn `1792170000000` = **17:00:00Z**, Polymarket market 5763247
  `"2026-10-16 17:00:00+00"`, while HLTV displays `13:00`.

So HLTV's displayed clock for this event is **UTC − 4**. Applying it, and cross-checking with
the countdowns each page carried when it was read:

| Fixture | Derived start (UTC) | Countdown as read | Implied render instant | Status |
|---|---|---|---|---|
| Aurora vs 9z | 2026-10-16 **14:00Z** (verified) | `5h 49m 4s` | 08:10:56Z | **verified** — machine-readable timestamp exists |
| BetBoom vs Legacy | 2026-10-16 **17:00Z** (verified) | `8h 45m 13s` | 08:14:47Z | **verified** |
| Semi-final 1 | 2026-10-17 **14:00Z** | `1d 5h 41m 6s` | 08:18:54Z | **derived — unverified** |
| Semi-final 2 | 2026-10-17 **17:00Z** | `1d 8h 41m 5s` | 08:18:55Z | **derived — unverified** |
| 3rd place | 2026-10-18 **11:30Z** | `2d 3h 10m 51s` | 08:19:09Z | **derived — unverified** |
| Grand final | 2026-10-18 **15:00Z** | `2d 6h 40m 50s` | 08:19:10Z | **derived — unverified** |

The six implied render instants land inside the minutes in which the pages were actually
fetched (08:10–08:19Z), which is a second, independent corroboration of the −4 offset: a
UTC+0 reading would put all six render instants four hours earlier than the fetch. Even so,
the four playoff starts are **derived, not verified**, and this project does not publish a
derived time as a value: no start, lock or deadline for those fixtures is written to the
board until Hotspawn lists them (its `scheduled_start_time` is machine-readable) or a market
carries a `gameStartTime`.

## 2. What Hotspawn has listed — and has not

From the retained raw fixtures response of the 08:06:33Z refresh
([`../harvest-3c8d1136/fixtures-raw.json`](../harvest-3c8d1136/fixtures-raw.json), 102 rows):

* Thunderpick World Championship 2026 appears **twice**: `1080205` (Aurora vs 9z, 14:00Z) and
  `1081775` (BetBoom vs Legacy, 17:00Z). Both are `tier "s"`, `stage "group stage and
  playoffs"`, `base_points 2`, multipliers game 1.25 × tier 3 × series 1 × stage 1 ×
  tournament 1 ⇒ **`offered_points` 7**.
* **No semi-final, 3rd-place or grand-final fixture is listed yet**, which is expected: two of
  the four semi-finalists are decided today.
* The feed is already carrying 17 and 18 October fixtures from other events (`1079170`,
  `1079171`, `1079173`, `1081513` on 17 Oct; `1081126`, `1081521`, `1081522` on 18 Oct), all
  with picks. So discovery of later dates is not the constraint — the playoffs simply are not
  in the feed yet.

Do **not** assume the semifinals will also be worth 7 points. `offered_points` is read from
the payload when the fixture appears; a different `stage` or `series_multiplier` (a Bo5 final
is a plausible candidate for one) changes the award, and guessing it would break the
no-inference rule.

## 3. What happens automatically when they are listed

1. The refresh reads the fixtures API plus both HTML lobby views. With the cache-bust fix in
   [`scripts/refresh.py`](../../scripts/refresh.py), a newly listed fixture is seen in the
   **same** refresh instead of up to ~4 hours later — this is exactly the failure that made
   BetBoom vs Legacy (listed 04:22Z on 16 Oct) invisible to the HTML views until 07:49Z.
2. The row is priced by the documented tier order: exchange gate → HLTV identity research →
   Pinnacle line → wide-quote tier → originated VRS model line → HLTV ranking research-only
   pick. No manual input at any step.
3. The pick deadline is the earliest of the fixture's own Hotspawn lock, the quote's
   eight-hour TTL, any bookmaker cutoff, the start time and the fixture observation window —
   now anchored on the real observation time rather than a cached copy.

## 4. Readiness gaps, with owners

| Gap | Evidence | Who |
|---|---|---|
| **No external line exists for either semi-final yet.** HLTV shows no `Betting` section on [2399414](https://www.hltv.org/matches/2399414/furia-vs-aurora-9z-winner-thunderpick-world-championship-2026) or [2399415](https://www.hltv.org/matches/2399415/falcons-vs-betboom-legacy-winner-thunderpick-world-championship-2026) (both list only `Lineups`), and the 08:06:48Z refresh found no Polymarket or Pinnacle market for either | this session | closes itself when a market opens; until then the row falls back to the originated VRS model line, labelled as such |
| **Identity readiness for the semi-finalists.** Aliases already exist for Aurora (`Aurora Gaming`), BetBoom (`BetBoom Team`), Falcons (`Team Falcons`) and NIP. `9z`, `Legacy` and `FURIA` matched on their exact labels in today's markets. If Polymarket labels FURIA differently (for example `FURIA Esports`), no alias exists yet and the market gate will reject the match with a recorded reason | `data/identities.json` (read this session: canonicals Aurora, BC.Game, BetBoom, Betclic Apogee Esports, EAC, Falcons, Insiders, Liquid, Ninjas in Pyjamas, Privateer, ROUNDS, WBT) | `1abe803f` — do **not** pre-register a speculative alias; add it only when a market exists and the fixture parity is sourced |
| **Hotspawn publishes no series format** (`best_of`/`series_format` are null for 102 of 102 rows), so a Bo5 grand final will not be distinguishable from a Bo3 on the board from Hotspawn data alone | retained raw response | integration session — irregularity #4 in [`LIVE-BOARD-VERIFICATION.md`](../../verification-3c8d1136/LIVE-BOARD-VERIFICATION.md) |
| **Publication reliability**: no scheduled refresh ran for the 05:17/06:17/07:17 UTC slots and the watchdog has never run, so day-4 coverage depends on push-triggered runs | Actions run history read at 08:05Z | `ef0969b9` |

## 5. Day-4 read, labelled as analysis (not verified fact, not a probability)

Sourced structural factors that will matter once the semi-finalists are set — all of them
read from the results and schedule above, none of them measured effects:

* **Rest asymmetry is symmetric between the two semi-finals.** FURIA and Falcons won their
  winners' matches on 15 October and have roughly two days off; whoever wins today's deciders
  plays a Bo3 at 14:00Z or 17:00Z and returns **exactly 24 hours later** for the semi-final.
  The same shape applied to NIP on day 3 (less than 24 hours between its TWC exit and the
  Stake Pulse Beat III quarter-final), which is the sourced reason the analysis page lists for
  leaning away from NIP there.
* **Both semi-finalists from the deciders arrive off a Bo3 win**, so their maps played in the
  previous 24 hours is three, against zero for FURIA and Falcons.
* **The grand final is Bo5**, which reduces single-map variance relative to the Bo3s; a
  favourite's edge is worth more over five maps than over three, and an underdog's upset path
  is narrower.
* **Form on record at this event**: Falcons 2–0 NIP and 2–1 9z; FURIA 2–0 BETBOOM and 2–1
  Legacy; the decider winners will each have beaten one eliminated team and lost one series.

Applying the scoring evidence in
[`../coverage-3c8d1136/SCORING-MODEL.md`](../coverage-3c8d1136/SCORING-MODEL.md) — a correct
pick is worth a fixed award that does not depend on how many other players chose the same
side, plus an unpublished bonus for consecutive correct picks — the leaderboard-optimal
choice on day 4 is still the higher-probability team. A contrarian pick is justified only by a
sourced factor plus a price that leaves room, never by the crowd split itself. When the
semi-final lines appear, the same screen the analysis page applies today applies to them.

## 6. Sources

HLTV event page and six match pages (linked above, read 2026-10-16 08:10–08:19Z) ·
Polymarket Gamma markets [5733288](https://gamma-api.polymarket.com/markets/5733288),
[5763247](https://gamma-api.polymarket.com/markets/5763247),
[5732258](https://gamma-api.polymarket.com/markets/5732258),
[5583525](https://gamma-api.polymarket.com/markets/5583525),
[5650404](https://gamma-api.polymarket.com/markets/5650404) · Pinnacle guest API matchup
1638406883 (`https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight`) ·
Hotspawn fixtures API and both lobby views (retained in
[`../harvest-3c8d1136/`](../harvest-3c8d1136/)) · Hotspawn rules page
<https://play.hotspawn.com/how-it-works> · Valve VRS standings
[`live/2026/standings_global_2026_10_05.md`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)
at commit `eec4853d` · HLTV team pages
[11861](https://www.hltv.org/team/11861/aurora),
[11283](https://www.hltv.org/team/11283/falcons),
[8297](https://www.hltv.org/team/8297/furia) · HLTV news
[45082](https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan) ·
[Liquipedia Aurora Gaming](https://liquipedia.net/counterstrike/Aurora_Gaming) ·
Hotspawn editorial day-3 preview (context only)
<https://www.hotspawn.com/counter-strike/news/thunderpick-world-championship-2026-day-3-preview>.

Not cited: `esports.gg`, which publishes incorrect dates for this event and is excluded by a
standing irregularity in `COORDINATION.md`.
