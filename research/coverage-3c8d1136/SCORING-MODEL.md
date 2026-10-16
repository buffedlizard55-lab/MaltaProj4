# Does a correct Hotspawn pick score fixed points, or a share of a pool?

Read from Hotspawn's own public fixture payload (retained raw response). No crowd percentage is used as a probability anywhere in this project.

- CS2 rows read: **102**
- rows carrying `base_points` + `points_breakdown` + `offered_points`: **102**
- rows where `offered_points == floor(base_points x the five multipliers)`: **102**
- exceptions to that formula: **0**
- rows missing a scoring field (left blank, never inferred): **0**
- scoring groups (tier, stage, best-of, series format, base points, multipliers): **7**
- groups where the award varies: **0**
- groups where crowd volume varies but the award does not: **7**

## Scoring groups

| Tier | Stage | Best of | Fixtures | Award(s) | `total_picks` range | Multipliers | Example fixtures |
|---|---|---|---|---|---|---|---|
| c | waiting for information | None | 38 | 2 | 0–74 | {"game_multiplier": 1.25, "series_multiplier": 1, "stage_multiplier": 1, "tier_multiplier": 1, "tournament_multiplier": 1} | 1052746, 1052747, 1051789, 1051790 |
| b | waiting for information | None | 33 | 3 | 0–24 | {"game_multiplier": 1.25, "series_multiplier": 1, "stage_multiplier": 1, "tier_multiplier": 1.5, "tournament_multiplier": 1} | 1051339, 1051340, 1052699, 1051341 |
| c | None | None | 20 | 2 | 0–5 | {"game_multiplier": 1.25, "series_multiplier": 1, "stage_multiplier": 1, "tier_multiplier": 1, "tournament_multiplier": 1} | 1053068, 1051301, 1053069, 1053070 |
| b | qualifier | None | 4 | 3 | 8–10 | {"game_multiplier": 1.25, "series_multiplier": 1, "stage_multiplier": 1, "tier_multiplier": 1.5, "tournament_multiplier": 1} | 1081493, 1081496, 1081499, 1081503 |
| c | qualifier | None | 3 | 2 | 8–9 | {"game_multiplier": 1.25, "series_multiplier": 1, "stage_multiplier": 1, "tier_multiplier": 1, "tournament_multiplier": 1} | 1081779, 1081780, 1081781 |
| b | None | None | 2 | 3 | 1–3 | {"game_multiplier": 1.25, "series_multiplier": 1, "stage_multiplier": 1, "tier_multiplier": 1.5, "tournament_multiplier": 1} | 1053146, 1052686 |
| s | group stage and playoffs | None | 2 | 7 | 13–23 | {"game_multiplier": 1.25, "series_multiplier": 1, "stage_multiplier": 1, "tier_multiplier": 3, "tournament_multiplier": 1} | 1080205, 1081775 |

## Conclusion

Every CS2 fixture publishes offered_points = floor(base_points x the five points_breakdown multipliers), and the award does not move where crowd volume does: 7 of 7 scoring groups show a different total_picks range with one single award. On this evidence a correct pick is worth a fixed number of points, so the leaderboard-optimal pick is the higher-probability team and a crowd split adds no score of its own. This is inferred from Hotspawn's own public fixture payload; an official Hotspawn rules page would outrank it.
