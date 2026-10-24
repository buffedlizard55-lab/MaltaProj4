snapshot generated_at: 2026-10-24T16:37:28.993492Z
fixtures_observed_at: 2026-10-24T16:33:55.358712Z
rows: 83 open: 22
open with pick: 21
open with probabilities: 22
open unpriced: []
open without pick: ['1079200']
methods: {'exchange': 15, 'bookmaker_fallback': 3, 'model_vrs_mirror': 1, 'exchange_wide': 1, 'model_vrs': 2}
coverage: verified coverage_counts: {'api': 83, 'page': 83, 'lobby': 83, 'retained': 83}
issues: [{"code": "feed_status", "message": "61 feed entries are not open by sourced timestamps/status. They remain in All matches and are not treated as future picks.", "source": "https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1"}]
