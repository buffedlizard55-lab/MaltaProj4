# Aurora — roster-change deep dive (user question: day-1 upset + "roster change")

Session bc70eb9a, checked 2026-10-17 (UTC). The short answer: **Aurora did not change its roster
during TWC 2026** — the same five players played every match of the event, and the team page's
current lineup is identical. The "change" story is the **July 2026 rebuild** (~3 months before
this event), which produced the current core; it had been fully installed well before day 1.

## Current roster (HLTV team page, read 2026-10-17 ~20:55Z)

Source: https://www.hltv.org/team/11861/aurora

| Player | Nationality |
| --- | --- |
| XANTARES (Ismailcan Dörtkardeş) | Türkiye |
| woxic (Özgür Eker) | Türkiye |
| Jimpphat (Jimi Salo) | Finland |
| kyxsan (Damjan Stoilkovski) | North Macedonia |
| Wicadia (Ali Haydar Yalçın) | Türkiye |

Coach: Ashley 'ash' Battye (UK). Rankings on the team page at read time: HLTV world #6,
Türkiye #1; Valve VRS #6 (Europe #5). Average player age 25.5. Weeks in top30 for core: 161.

## In-tournament lineup verification (day 1 vs day 4, player by player)

- Day 1 — 2399384 (9z 2–0 Aurora, 14 Oct): Aurora table on the match page lists
  Jimpphat, woxic, XANTARES, Wicadia, kyxsan.
  https://www.hltv.org/matches/2399384/9z-vs-aurora-thunderpick-world-championship-2026
- Day 4 — 2399414 (FURIA 2–0 Aurora, 17 Oct): Aurora table on the match page lists
  Wicadia, Jimpphat, XANTARES, woxic, kyxsan.
  https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026
- Day 2 — 2399408 (Aurora 2–0 NiP): same five in the stats table (Wicadia 1.65, kyxsan, Jimpphat
  et al. — table read 2026-10-17).
- Day 3 — 2399412 (Aurora 2–0 9z): same five (kyxsan 1.45, Jimpphat 1.31 in the match table).

Same set of five in all four days ⇒ **no in-tournament roster change.** No mid-event transfers
appear on the team page (the page's transfer sections show none in this period).

## The real rebuild (context, pre-event)

The current core (XANTARES/woxic/Wicadia + Jimpphat + kyxsan, coach ash) is the July 2026
rebuild of the Serbian-founded organization; the team page's own "team period" clock and the
weeks-in-top30-for-core figure (161 weeks for this core) show it is an established, not new,
lineup. Prior sessions of this project recorded the same conclusion from strafe.com and HLTV
news (see data/analysis.json sources). Nothing changed between that rebuild and day 1 of TWC.

## Performance shape across the event (from the verified results table)

| Day | Match | Result | Aurora match-level signal (HLTV tables) |
| --- | --- | --- | --- |
| 1 | 2399384 vs 9z | 0–2 | Team sub-1.0 across the board (Jimpphat 1.19 best; kyxsan 0.53); lost 13-11 + 13-1 |
| 2 | 2399408 vs NiP | 2–0 | Wicadia 1.65; Cache 13-9, Dust2 13-7 |
| 3 | 2399412 vs 9z | 2–0 | kyxsan 1.45, Jimpphat 1.31; Cache 13-11, Inferno 13-4 — reversed the day-1 result vs the same opponent |
| 4 | 2399414 vs FURIA | 0–2 | Team ~0.70–0.94; Dust2 8-13, Inferno 10-13; Wicadia 1.18 on the losing Inferno |

Reading: the day-1 "upset" was 9z beating a #6-world team cold (13-11, 13-1); Aurora then won
its elimination path without dropping a map (4–0 maps over days 2–3) and lost the semifinal
cleanly to the eventual finalist. The 9z H2H is 1–1 inside the event.

## Relevance to day 5 (3rd place decider vs Falcons, 11:30Z)

- Rest: Aurora's semifinal ended after 2 maps (14:00Z slot); Falcons played 3 maps with OT.
  Both teams are in the same time slot group for 2399416 at 11:30Z.
- Roster: stable (verified above) — no injury/rotation unknown to surface on HLTV at read time.
- Directional note only (see twc-2026-results-verified.md): structural lean Aurora on rest and
  2-map fatigue; no probability published — no external two-way market existed at 21:30Z.
