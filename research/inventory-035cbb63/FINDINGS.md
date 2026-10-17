# Hotspawn inventory-completeness audit — session 035cbb63

Audited: 2026-10-17T01:37:27.528973Z

Question: Does the collector's scoped query return every CS2 fixture Hotspawn exposes on this endpoint, or does another status value / pagination expose fixtures the board never sees?

Collector query: `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`

Baseline CS2 rows: 96 (statuses reported: scheduled)

Board comparison: compared with runtime/latest.json (generated_at 2026-10-17T01:32:09.961809Z, 96 board rows)

## Every variant measured

| Variant | note | HTTP | rows (all) | rows (CS2) | statuses |
| --- | --- | --- | --- | --- | --- |
| `sport_alias=cs2&status=scheduled&tenantId=1` | baseline: exactly what scripts/core.py requests today | 200 | 96 | 96 | scheduled |
| `sport_alias=cs2&tenantId=1` | no status filter: does the endpoint default to a wider or narrower set? | 200 | 10337 | 10337 | cancelled, ended, forfeited, scheduled, started |
| `sport_alias=cs2&status=upcoming&tenantId=1` | is there an "upcoming" status distinct from "scheduled"? | 200 | 0 | 0 | — |
| `sport_alias=cs2&status=live&tenantId=1` | is there a "live" status that carries pickable matches? | 200 | 0 | 0 | — |
| `sport_alias=cs2&status=finished&tenantId=1` | is there a "finished" status (result rows, not picks)? | 200 | 0 | 0 | — |
| `sport_alias=cs2&status=open&tenantId=1` | is there an "open" status? | 200 | 0 | 0 | — |
| `tenantId=1&status=scheduled` | no sport filter: how many non-CS2 rows share the endpoint? | 200 | 392 | 96 | scheduled |
| `sport_alias=cs2&status=scheduled&tenantId=1&page=2` | pagination probe: does a second page exist? | 400 | — | — | HTTP 400 |
| `sport_alias=cs2&status=scheduled&tenantId=1&per_page=1000` | page-size probe: does a larger page return more rows? | 400 | — | — | HTTP 400 |
| `sport_alias=cs2&status=scheduled&tenantId=1&limit=100&offset=100` | limit/offset probe: does offsetting return a different window? | 400 | — | — | HTTP 400 |

## Fixtures exposed outside the baseline query

- `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&tenantId=1` — no status filter: does the endpoint default to a wider or narrower set?; 10337 CS2 rows; 10241 id(s) not in the baseline: 1, 1000076, 1000077, 1000078, 1000097, 1000098, 1000167, 1000168, 1000169, 1000170, 1000171, 1000172, 1000173, 1000174, 1000175, 1000176, 1000177, 1000178, 1000179, 1000180, 1000181, 1000182, 1000183, 1000184, 1000185, 1000186, 1000187, 1000188, 1000189, 1000190, 1000191, 1000192, 1000193, 1000194, 1000195, 1000196, 1000197, 1000199, 1000213, 1000214

## Board vs baseline

- board rows not in the baseline response: none
- baseline rows not on the board: none

## Limitations

- The probe covers the query variants listed above. A parameter name not guessed here (for example an undocumented competition or date filter) is not covered.
- A non-200 response is recorded as a limitation, never as "no such fixtures".
- HTML pages (lobby, cs2-pickems) are already compared by scripts/inventory.py; this audit adds the API-scope question, it does not replace that parity check.
- No probability, pick or roster inference is produced here.
