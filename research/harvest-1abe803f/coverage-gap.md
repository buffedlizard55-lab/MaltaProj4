# Hotspawn board versus HLTV schedule - coverage gap check

Checked 2026-10-16T07:18:36.246585Z · method: Exact normalized team-pair identity plus exact UTC start. Same identity rule as the collector: no fuzzy aliasing, no assumed schedule corrections.

| Teams | UTC start | Kind | Note | Source |
| --- | --- | --- | --- | --- |
| (no gap found) |  |  | Every HLTV fixture on this event page is on the board. | https://www.hltv.org/events/8932/matches |

Hotspawn CS2 rows read: 103 (open by lock: 42) · fixtures scheduled on this HLTV event page: 2 · board rows that are not on this event page: 101

Read the last number as context, not as a gap: the board covers every CS2 event Hotspawn lists, while this page lists one tournament, so those rows belong to other competitions. The direction that matters is the other one - every fixture HLTV schedules for this event must appear on the board, and a missing one is reported above as absent_from_board. A fixture HLTV has already finished is not on its scheduled page at all, so a past series cannot be used to prove a board gap.

