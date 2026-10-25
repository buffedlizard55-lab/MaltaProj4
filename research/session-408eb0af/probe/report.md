# Pre-match line-source reachability probe

Captured on GitHub runners at **2026-10-25T13:42:55.229281Z** (the only egress this project can reach these hosts from).

One GET per endpoint, no credentials, no retries against a refusal, bodies committed beside this report under `bodies/`. A row states what came back, not what it means.

| Source | HTTP | Bytes | Final host | Note |
| --- | --- | --- | --- | --- |
| hotspawn-fixtures-api | 200 | 61044 | phpstack-1372681-6459848.cloudwaysapps.com | JSON array, 78 entries; first entry keys: base_points, best_of, competition_id, competition_name, end_time, id, lock_offset_sec, lock_time, offered_points, participants0_id, participants0_name, participants0_picked_percent, participants0_score, participants1_id; markers: Thunderpick x8 |
| hotspawn-lobby | 200 | 301776 | play.hotspawn.com | decoded 199942 characters; markers: Thunderpick x2 |
| polymarket-sports | 200 | 155942 | gamma-api.polymarket.com | JSON array, 491 entries; first entry keys: createdAt, id, image, name, ordering, primaryTagId, resolution, series, sport, tags |
| pinnacle-moneylines | 200 | 578359 | guest.api.arcadia.pinnacle.com | declared JSON but did not parse |
| pinnacle-matchups | 200 | 103002 | guest.api.arcadia.pinnacle.com | JSON array, 36 entries; first entry keys: ageLimit, altTeaser, featureOrder, hasAltSpread, hasAltTotal, hasBetshare, hasLive, hasMarkets, id, isBetshareEnabled, isFeatured, isHighlighted, isLive, isPromoted; markers: moneyline x36, Moneyline x110 |
| bo3-matches | 200 | 103555 | api.bo3.gg | JSON object, keys: links, results, total; markers: team_1 x38 |
| hltv-matches | 200 | 643491 | www.hltv.org | decoded 199992 characters; markers: odds x1 |
| hltv-ranking | 200 | 1154783 | www.hltv.org | decoded 199903 characters; markers: odds x1 |
| hltv-valve-ranking | 200 | 1674384 | www.hltv.org | decoded 199903 characters; markers: odds x1 |
| egamersworld-cs2 | 403 | 5715 | egamersworld.com | decoded 5715 characters |
| stavka-cs2 | 200 | 465998 | stavka.tv | decoded 199945 characters; markers: bookmaker x1 |
| thunderpick-cs2 | 200 | 14610 | thunderpick.io | decoded 14610 characters; markers: Thunderpick x7, odds x1 |
| ggbet-cs2 | 403 | 126 | gg.bet | decoded 126 characters |
| bovada-cs2 | 404 | 2 | www.bovada.lv | decoded 2 characters |
| oddspedia-cs2 | 400 | 0 | oddspedia.com | decoded 0 characters |
