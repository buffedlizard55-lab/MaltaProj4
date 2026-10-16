# Hotspawn board versus HLTV schedule - coverage gap check

Checked 2026-10-16T19:31:23.598241Z · method: Exact normalized team-pair identity plus exact UTC start. Same identity rule as the collector: no fuzzy aliasing, no assumed schedule corrections.

| Teams | UTC start | Kind | Note | Source |
| --- | --- | --- | --- | --- |
| FURIA vs Aurora | 2026-10-17T14:00:00Z | absent_from_board | On the HLTV event schedule but not in the Hotspawn CS2 feed at this check, so this project cannot list a pick row for it and it scores no points. | https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026 |

Hotspawn CS2 rows read: 83 (open by lock: 21) · fixtures scheduled on this HLTV event page: 1 · board rows that are not on this event page: 83

Read the last number as context, not as a gap: the board covers every CS2 event Hotspawn lists, while this page lists one tournament, so those rows belong to other competitions. The direction that matters is the other one - every fixture HLTV schedules for this event must appear on the board, and a missing one is reported above as absent_from_board. A fixture HLTV has already finished is not on its scheduled page at all, so a past series cannot be used to prove a board gap.

