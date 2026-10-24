# Hotspawn coverage and verification summary

- Snapshot generated: `2026-10-24T05:34:01.441501Z`
- Fixture evidence observed: `2026-10-24T05:30:27.487614Z`
- Snapshot SHA-256: `c63d16fc9b7101c44e2d9b42c1a2669164e7e0068c738d2c8acebb25d8c6f569`
- Three-view coverage flag: **verified**; counts: `{"api": 88, "page": 88, "lobby": 88, "retained": 88}`
- Fixtures: **88**; open: **25**; with a pick: **25**; with a probability: **25**; fully resolved: **25**
- Research-only picks without a percentage: **0**; open rows without a pick: **0**
- Open-row methods: `{"bookmaker_fallback": 2, "exchange": 12, "exchange_wide": 2, "model_vrs": 7, "model_vrs_mirror": 2}`
- Added vs previous: `['1079658', '1079659', '1079660', '1079661', '1081152', '1081153', '1081154', '1081156', '1081158']`; removed: `['1079657', '1081150', '1081605', '1081606', '1082693', '1082923', '1082924', '1082925', '1082980', '1083014', '1083025']`
- Independent + additional integrity failures: **0**

Hotspawn is used only for fixture identity, schedule and lock state. It is not a probability source. Blank values are not replaced with guesses.

## Changed fixture facts vs the previous committed snapshot

- `1082926` Isurus vs Hacha: `{"state": {"previous": "open", "current": "not_open"}}`

## Open-row gaps and limitations

No open-row coverage gaps in this dated snapshot. Later refreshes may produce gaps; those remain visible rather than being filled with invented values.
