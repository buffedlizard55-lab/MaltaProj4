# Hotspawn board versus HLTV schedule - coverage gap check

Checked 2026-10-16T05:01:07.659398Z · method: Exact normalized team-pair identity plus exact UTC start. Same identity rule as the collector: no fuzzy aliasing, no assumed schedule corrections.

| Teams | UTC start | Kind | Note | Source |
| --- | --- | --- | --- | --- |
| (not measured) |  |  | This check could not read both sources, so no coverage conclusion is drawn from it. See the access problems below. | https://www.hltv.org/events/8932/matches |
- Access problem at https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1: module 'datetime' has no attribute 'now'
- Access problem at https://www.hltv.org/events/8932/matches: module 'datetime' has no attribute 'now'
