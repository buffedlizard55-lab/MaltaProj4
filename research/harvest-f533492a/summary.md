# Hotspawn coverage and verification summary

- Snapshot generated: `2026-10-24T05:57:32.061308Z`
- Fixture evidence observed: `2026-10-24T05:53:56.542706Z`
- Snapshot SHA-256: `e059e0c4bfa1e0f4910f4cc2f5c6454cc8ae36a964817308f4916f4bf202b4f1`
- Three-view coverage flag: **partial**; counts: `{"api": 88, "page": 88, "lobby": 88, "retained": 89}`
- Fixtures: **89**; open: **25**; with a pick: **25**; with a probability: **25**; fully resolved: **25**
- Research-only picks without a percentage: **0**; open rows without a pick: **0**
- Open-row methods: `{"bookmaker_fallback": 2, "exchange": 12, "exchange_wide": 2, "model_vrs": 7, "model_vrs_mirror": 2}`
- Added vs previous: `['1079658', '1079659', '1079660', '1079661', '1081152', '1081153', '1081154', '1081156', '1081158', '1083045']`; removed: `['1079657', '1081150', '1081605', '1081606', '1082693', '1082923', '1082924', '1082925', '1082980', '1083014', '1083025']`
- Independent + additional integrity failures: **1**

Hotspawn is used only for fixture identity, schedule and lock state. It is not a probability source. Blank values are not replaced with guesses.

## Changed fixture facts vs the previous committed snapshot

- `1082926` Isurus vs Hacha: `{"state": {"previous": "open", "current": "not_open"}}`

## Open-row gaps and limitations

No open-row coverage gaps in this dated snapshot. Later refreshes may produce gaps; those remain visible rather than being filled with invented values.

## Integrity failures

- 1083045: row lacks the exact scoped Hotspawn fixture-feed link
