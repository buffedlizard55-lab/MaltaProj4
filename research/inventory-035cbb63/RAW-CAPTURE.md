# Raw Hotspawn capture — session 035cbb63

Captured: 2026-10-17T01:25:29.912649Z

Recorded because the 2026-10-17T00:59Z refresh could not use any of the three official sources. Bytes, not assumptions.

## fixtures_api — `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`

- HTTP 200 · content-type `application/json; charset=utf-8` · 76400 bytes · sha256 `44db0ec39c596ca0…`
- looks like JSON: True · looks like HTML: False
- hydration markers present: `__NEXT_DATA__`=False, `self.__next_f`=False, `window.__NUXT__`=False, `__remixContext`=False, `buildId`=False

First 1200 characters of the body:

```
[{"id":"1052746","competition_id":"35005","competition_name":"European Pro League Series 8 Play-In","sport_alias":"cs2","sport_name":"Counter-Strike 2","status":"scheduled","scheduled_start_time":"1782469800000","lock_time":"1782469440000","lock_offset_sec":360,"offered_points":2,"base_points":2,"best_of":null,"series_format":null,"tier":"c","stage":"waiting for information","points_breakdown":{"game_multiplier":1.25,"tier_multiplier":1,"series_multiplier":1,"stage_multiplier":1,"tournament_multiplier":1},"start_time":"1782474327439","end_time":"1782478260961","total_picks":10,"participants0_id":"251690","participants0_name":"Fortress","participants0_picked_percent":20,"participants0_score":0,"participants1_id":"239669","participants1_name":"Endless Journey","participants1_picked_percent":80,"participants1_score":0},{"id":"1051339","competition_id":"35437","competition_name":"DraculaN Season 7","sport_alias":"cs2","sport_name":"Counter-Strike 2","status":"scheduled","scheduled_start_time":"1782475200000","lock_time":"1782474840000","lock_offset_sec":360,"offered_points":3,"base_points":2,"best_of":null,"series_format":null,"tier":"b","stage":"waiting for information","points_breakd
```

## cs2_pickems_page — `https://play.hotspawn.com/cs2-pickems`

- HTTP 200 · content-type `text/html;charset=UTF-8` · 459538 bytes · sha256 `e434e2484a62221a…`
- looks like JSON: False · looks like HTML: True
- hydration markers present: `__NEXT_DATA__`=False, `self.__next_f`=False, `window.__NUXT__`=False, `__remixContext`=False, `buildId`=False

First 1200 characters of the body:

```
<!DOCTYPE html><html lang="en" data-beasties-container><head>
  <meta charset="utf-8">
  <title>CS2 Pick'ems Lobby | Hotspawn Play</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<style>@font-face{font-family:'Inter';font-style:normal;font-weight:300;font-display:swap;src:url(https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa2JL7SUc.woff2) format('woff2');unicode-range:U+0460-052F, U+1C80-1C8A, U+20B4, U+2DE0-2DFF, U+A640-A69F, U+FE2E-FE2F;}@font-face{font-family:'Inter';font-style:normal;font-weight:300;font-display:swap;src:url(https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa0ZL7SUc.woff2) format('woff2');unicode-range:U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116;}@font-face{font-family:'Inter';font-style:normal;font-weight:300;font-display:swap;src:url(https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa2ZL7SUc.woff2) format('woff2');unicode-range:U+1F00-1FFF;}@font-face{font-
```

## lobby_page — `https://play.hotspawn.com/lobby`

- HTTP 200 · content-type `text/html;charset=UTF-8` · 335025 bytes · sha256 `fbfa847d4a7e542f…`
- looks like JSON: False · looks like HTML: True
- hydration markers present: `__NEXT_DATA__`=False, `self.__next_f`=False, `window.__NUXT__`=False, `__remixContext`=False, `buildId`=False

First 1200 characters of the body:

```
<!DOCTYPE html><html lang="en" data-beasties-container><head>
  <meta charset="utf-8">
  <title>Pick'ems Lobby | Hotspawn Play</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<style>@font-face{font-family:'Inter';font-style:normal;font-weight:300;font-display:swap;src:url(https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa2JL7SUc.woff2) format('woff2');unicode-range:U+0460-052F, U+1C80-1C8A, U+20B4, U+2DE0-2DFF, U+A640-A69F, U+FE2E-FE2F;}@font-face{font-family:'Inter';font-style:normal;font-weight:300;font-display:swap;src:url(https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa0ZL7SUc.woff2) format('woff2');unicode-range:U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116;}@font-face{font-family:'Inter';font-style:normal;font-weight:300;font-display:swap;src:url(https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa2ZL7SUc.woff2) format('woff2');unicode-range:U+1F00-1FFF;}@font-face{font-fami
```

