# Day-2 → Day-3 verification, session `ab18fe2a`

Written 2026-10-16, 04:2x–05:0x UTC. Every line below was re-read from the source it cites.
Nothing is copied from another session's conclusions; where this session agrees with an
earlier one, the agreement is noted with both sources.

Evidence standard: Hotspawn establishes the fixture inventory only and is never a
probability input. HLTV supplies identity, results, rankings, lineups and context.
Probabilities come only from observed market lines. Anything unverifiable stays blank
and flagged.

Sandbox note: `bash` in this session reaches GitHub and package registries only, so
HLTV, Hotspawn and Polymarket were read through the page-retrieval path, and GitHub
Actions data through the GitHub API. No access control was bypassed.

---

## 1. Day-2 results — re-read from the source, line by line

Source: <https://www.hltv.org/results?event=8932> (HLTV results, event 8932).

| Date | Series (HLTV order) | Score | Matches the published day-2 table? |
|---|---|---|---|
| 15 Oct | Legacy vs FURIA | 1–2 FURIA | yes |
| 15 Oct | PARIVISION vs BETBOOM | 1–2 BETBOOM | yes |
| 15 Oct | 9z vs Falcons | 1–2 Falcons | yes |
| 15 Oct | Aurora vs Ninjas in Pyjamas | 2–0 Aurora | yes |
| 14 Oct | FURIA vs BETBOOM | 2–0 | yes |
| 14 Oct | Legacy vs PARIVISION | 2–0 | yes |
| 14 Oct | Falcons vs Ninjas in Pyjamas | 2–0 | yes |
| 14 Oct | 9z vs Aurora | 2–0 9z | yes |

All eight series scores on the published analysis page reproduce exactly. **No
correction needed this session.** (Session `0e407ec7` had already corrected the
BETBOOM–PARIVISION Anubis score from 13-2 to 13-4; that correction stands.)

Playoff bracket, read from <https://www.hltv.org/events/8932/thunderpick-world-championship-2026>:
semi-finals are **Falcons vs the BETBOOM/Legacy winner** and **FURIA vs the Aurora/9z
winner**. Falcons and FURIA are already through; NIP and PARIVISION are eliminated.
That confirms both 16 October matches are deciders and nothing else.

## 2. Day-3 schedule — machine-verified, not derived

| Fixture | HLTV page | HLTV displayed clock | HLTV countdown | Derived UTC | Hotspawn feed | Verdict |
|---|---|---|---|---|---|---|
| Aurora vs 9z (Group A decider) | [2399412](https://www.hltv.org/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026) | 10:00, 16 Oct | 9h 43m at 04:17Z | **14:00Z** | `1080205`, `scheduled_start_time` 1792159200000 = 14:00Z | two independent sources agree |
| BetBoom vs Legacy (Group B decider) | [2399413](https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026) | 13:00, 16 Oct | 12h 43m at 04:17Z | **17:00Z** | `1081775`, `scheduled_start_time` 1792170000000 = 17:00Z | three sources agree |

HLTV's *displayed* clock is reader-local and is **not** UTC (irregularity
`hltv-times-2026-10-15`). Both derived UTC values are confirmed by the Hotspawn feed's
millisecond timestamps and, for the Group B decider, by Polymarket's
`gameStartTime` / `eventStartTime`. Both matches are best of 3 on LAN.

## 3. The Group B decider is now on the Hotspawn board — correction

This is the substantive finding of the session.

Every capture taken on 15 October — including this repository's committed
`data/latest.json` and session `0e407ec7`'s own independent harvest — contained **no
BETBOOM fixture at all**. The published analysis page therefore said, correctly at the
time, that the decider "is not listed by Hotspawn" and "scores no points".

At **2026-10-16T04:22Z** the Hotspawn CS2 scheduled feed now returns it:

- fixture **1081775**, competition 35859 (Thunderpick World Championship 2026)
- participants **BetBoom** (id 115660) vs **Legacy** (id 130389)
- `scheduled_start_time` 1792170000000 = **2026-10-16T17:00:00Z**, `lock_time` = 16:54:00Z
- `tier` **s**, `offered_points` **7**, `stage` "group stage and playoffs"
- `total_picks` 6, crowd split 17% BetBoom / 83% Legacy (never used as a probability)

Receipt: [`receipts/hotspawn-fixture-1081775.json`](receipts/hotspawn-fixture-1081775.json).
Cross-checked against Hotspawn's own public match page, which renders "BetBoom vs
Legacy", 17:00, 16 OCT, and lists the lineups BetBoom `s1ren / Magnojez / d1Ledez /
zorte / Boombl4` and Legacy `latto / n1ssim / arT / dumau / try`.

**Identity requires no new alias.** `data/identities.json` already maps canonical
`BetBoom` to `['BetBoom', 'BetBoom Team', 'BB Team']`, and `scripts/core.py` reduces
names by casefolding and stripping non-alphanumerics before consulting the alias map,
so Hotspawn's `BetBoom` and Polymarket's `BetBoom Team` are the same identity. No fuzzy
matching, no academy/main-team conflation.

**The line clears the strict tier.** Polymarket market 5763247, read cache-busted at
`updatedAt` 2026-10-16T04:21:07Z: Legacy **0.655** / BetBoom Team **0.345**, bid 0.65,
ask 0.66 (1-point spread), liquidity $26,994, volume $6,751, `active` true, `closed`
false, `acceptingOrders` true, `sportsMarketType` moneyline. Every gate passes.
Receipt: [`receipts/polymarket-5763247-2026-10-16T0421Z.json`](receipts/polymarket-5763247-2026-10-16T0421Z.json).

Across four dated states (22:45:08Z, 22:53:08Z, 23:17:08Z, 04:21:07Z) **the favourite
never changed**; the spread fell 10 → 9 → 7 → 1 points and liquidity grew about
fourfold. The line firmed up; it did not move.

Consequences applied in this session: `day_three.fixtures[1].hotspawn_fixture` is set
from `null` to `"1081775"`, the stale "absent" notes are corrected, and the contrarian
`limits` text that called the Group A decider "the only day-three fixture this board can
act on" is corrected to two.

## 4. Aurora's roster change — the premise, checked

The briefing assumed a recent Aurora roster change makes them upsettable again.

Read from <https://www.hltv.org/team/11861/aurora> on 2026-10-16:

- current five: **XANTARES, woxic, Jimpphat, kyxsan (IGL), Wicadia**
- coach: **Ashley 'ash' Battye**
- **Valve Regional Standings #5** (EU #5); **HLTV world ranking #6**
- average player age 25.5

Trade coverage dates the rebuild: Jimpphat from MOUZ, ash from GamerLegion, kyxsan
completing the five on **8 July 2026**; MAJ3R, soulfly and coach Fabre moved to the
inactive roster. Three of the five players predate the change.

**Conclusion:** the change is real but roughly a full ranking cycle old, over which
Aurora climbed to #5 in the world. "New roster still bedding in" is not supported by
the ranking evidence as a reason they lost to 9z, so this project does **not** use it as
the contrarian case. The sourced case for 9z is narrower and stronger: a 2–0
head-to-head two days earlier in this same event, plus a map win over the group winner,
Falcons. Recorded as `aurora-roster-change-2026-10-16` on Flagged for Review.

Dates come from trade press and are labelled reporting; the lineup, coach and both
rankings were read from HLTV directly. Separately, Aurora's own site
<https://auroragg.com/> lists **Polymarket among its partners**, a disclosed conflict of
interest for a project that reads Polymarket lines — restated because it applies to any
Aurora row.

## 5. Rest asymmetry — checked, and there is none

Source: <https://www.hltv.org/results?event=8932>.

- Group A: Aurora beat NIP 2–0 on 15 Oct; 9z lost 1–2 to Falcons on 15 Oct.
- Group B: BETBOOM beat PARIVISION 2–1 on 15 Oct; Legacy lost 1–2 to FURIA on 15 Oct.

Both teams in each decider last played on the same day, so fatigue is not a usable
differentiator on day three. The only sourced freshness factor on this slate is NIP's
sub-24-hour turnaround from Malta to Sweden, which costs the Stake Pulse Beat III row,
not either TWC decider.

## 6. Corrections made in this session

| # | What was wrong | Correction | Source |
|---|---|---|---|
| 1 | `day_three.fixtures[1].hotspawn_fixture` was `null` | `"1081775"` | Hotspawn feed + match page |
| 2 | `hotspawn_note` said the fixture was absent and scored no points | rewritten to record the listing, with the raw fields and the reason no new alias is needed | same |
| 3 | `day_three_guidance.not_listed[0]` presented it as unlisted | `now_listed: true`, label and `why` corrected, pricing added | same + market 5763247 |
| 4 | `day_three.contrarian.limits` called Group A "the only day-three fixture this board can act on" | corrected to two, with BETBOOM at 34.5% inside the band | same |

Every other published day-2 and day-3 number was re-read and matched.

## 7. Explicitly unverified / not claimed

- The Hotspawn fixtures endpoint rejects unknown query parameters (HTTP 400), so that
  read could **not** be cache-busted. The listing is dated by retrieval time (04:22Z),
  not by a payload timestamp.
- No probability in this project is taken from a manual read. All published
  probabilities come from the scheduled Actions refresh.
- Whether Hotspawn will keep fixture 1081775 listed until lock is unknown.
- The Aurora rebuild date (8 July 2026) is trade-press reporting, not an official
  organisation statement found by this session.
- "Contrarian" means against the market favourite. Crowd pick shares are deliberately
  not used, so crowd behaviour is not measured.
