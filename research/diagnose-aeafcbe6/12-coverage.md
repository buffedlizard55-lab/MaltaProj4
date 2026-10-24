snapshot generated_at: 2026-10-24T17:21:22.169288Z
fixtures_observed_at: 2026-10-24T17:17:46.960016Z
rows: 81 open: 20
open with pick: 20
open with probabilities: 20
open unpriced: []
open without pick: []
methods: {'exchange': 12, 'bookmaker_fallback': 3, 'model_vrs_mirror': 1, 'model_vrs': 3, 'exchange_wide': 1}
coverage: verified coverage_counts: {'api': 81, 'page': 81, 'lobby': 81, 'retained': 81}
issues: [{"code": "feed_status", "message": "61 feed entries are not open by sourced timestamps/status. They remain in All matches and are not treated as future picks.", "source": "https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1"}]
