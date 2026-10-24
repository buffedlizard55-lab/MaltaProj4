snapshot generated_at: 2026-10-24T17:09:41.700511Z
fixtures_observed_at: 2026-10-24T17:06:10.456805Z
rows: 83 open: 20
open with pick: 20
open with probabilities: 20
open unpriced: []
open without pick: []
methods: {'exchange': 12, 'bookmaker_fallback': 2, 'model_vrs_mirror': 1, 'model_vrs': 3, 'exchange_wide': 2}
coverage: verified coverage_counts: {'api': 83, 'page': 83, 'lobby': 83, 'retained': 83}
issues: [{"code": "feed_status", "message": "63 feed entries are not open by sourced timestamps/status. They remain in All matches and are not treated as future picks.", "source": "https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1"}]
