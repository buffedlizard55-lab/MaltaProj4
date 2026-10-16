# Hotspawn three-way parity, fixture by fixture

Snapshot `2026-10-16T07:44:25.663837Z` (fixtures observed `2026-10-16T05:36:55.488681Z`, built `None`), coverage **partial**, counts {"api": 103, "lobby": 95, "page": 103, "retained": 106}.

## Source observation times

| Source | HTTP | Retrieved (UTC) | Observed (UTC) | `Age` (s) |
|---|---|---|---|---|
| [Hotspawn CS2 fixtures](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1) | 200 | 2026-10-16T07:44:06.725269Z | 2026-10-16T07:44:06.725269Z | None |
| [Hotspawn CS2 lobby](https://play.hotspawn.com/cs2-pickems) | 200 | 2026-10-16T07:44:07.280056Z | 2026-10-16T07:27:31.280056Z | 996 |
| [Hotspawn general lobby](https://play.hotspawn.com/lobby) | 200 | 2026-10-16T07:44:07.488681Z | 2026-10-16T05:36:55.488681Z | 7632 |

## ID sets

| Source | CS2 fixtures |
|---|---|
| api | 103 |
| lobby | 95 |
| page | 103 |
| retained | 0 |

## Present only in the fresh API (0)

None.


## Present only in the cached HTML views (3)

| Fixture | Start (UTC) | Match | Event | State | Pick | Method | Probabilities | Expires (UTC) |
|---|---|---|---|---|---|---|---|---|
| [1079626](https://play.hotspawn.com/cs2-pickems) | 2026-10-15T11:00:00Z | Walczaki vs mellren | CCT Europe 2026 Series #11 | not_open | (none) | (none) | (none) |  |
| [1080204](https://play.hotspawn.com/cs2-pickems) | 2026-10-15T16:00:00Z | Legacy vs FURIA | Thunderpick World Championship 2026 | not_open | (none) | (none) | (none) |  |
| [1079628](https://play.hotspawn.com/cs2-pickems) | 2026-10-15T17:00:00Z | Gothic vs LFO 10 | CCT Europe 2026 Series #11 | not_open | (none) | (none) | (none) |  |

## Open coverage

- open rows: **42**
- open rows with a pick: **42**
- open rows without a pick: **0**
- earliest open-row expiry: `None`
- page/lobby symmetric difference: ['1079626', '1079628', '1080204', '1081493', '1081496', '1081497', '1081499', '1081503', '1081513', '1081521', '1081522', '1081779', '1081780', '1081781']
- rows with no attributable source receipt: none
