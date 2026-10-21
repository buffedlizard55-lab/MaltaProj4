# Publication state of the live site

Read at `2026-10-21T20:42:15.771645Z` from the GitHub API and the live build receipt.

| Question | Answer | Source |
| --- | --- | --- |
| How is Pages configured? | `build_type: legacy`, source `main:/`, site status `building` | [GET /repos/buffedlizard55-lab/MaltaProj4/pages](https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages) |
| Which publisher is serving now? | `unknown` | live [build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) revision `None` |
| What does the live receipt say? | unreadable (HTTP `None`) | [live build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) |
| What does the committed root fallback say? | revision `88b1b2c3b96954e64f614ad08342cc74aeb289fe`, built `2026-10-18T00:52:19Z`, 98 rows | [build-info.json on main](https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/build-info.json) |
| Is the served board inside its 8-hour evidence window? | unknown | derived from the two timestamps above |
| Can the legacy builder still overwrite it? | **yes** | Pages `build_type` above |

## Last Pages builds (both publishers write here)

| Created (UTC) | Status | Commit |
| --- | --- | --- |
| 2026-10-21T20:35:17Z | building | `884f36eb27b11865d2f36577f9e1ea8ec55bf67e` |
| 2026-10-21T20:20:02Z | built | `b2e204a3cc835f1b957229a474df25d03e7ea553` |
| 2026-10-21T20:12:40Z | built | `63f4172cb50aff8b2a36b2e01514b3e121a3d792` |
| 2026-10-21T19:53:42Z | built | `47f230bd83c2626d818cee24f511dde97a7bcdd8` |
| 2026-10-21T19:40:26Z | built | `d03badd4d8030e523daaef79eb9f78413a8f858b` |
| 2026-10-21T14:14:50Z | built | `88b1b2c3b96954e64f614ad08342cc74aeb289fe` |

## Last publication workflow runs

| Started (UTC) | Event | Conclusion | Run |
| --- | --- | --- | --- |
| 2026-10-21T20:40:33Z | pull_request | None | [39672346357](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39672346357) |
| 2026-10-21T20:40:29Z | push | None | [39672335521](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39672335521) |
| 2026-10-21T20:40:08Z | pull_request | None | [39672282810](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39672282810) |
| 2026-10-21T20:36:00Z | pull_request | None | [39671700152](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39671700152) |
| 2026-10-21T20:35:55Z | push | None | [39671686959](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39671686959) |
| 2026-10-21T20:35:54Z | push | None | [39671684045](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39671684045) |
| 2026-10-21T20:35:25Z | push | None | [39671613603](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39671613603) |
| 2026-10-21T20:35:18Z | push | None | [39671597469](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39671597469) |

## Owner-level fix attempt

`PUT https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages` with payload `{"build_type": "workflow"}`

* HTTP status: **403** (HTTP 403)
* GitHub says these permissions are accepted: `pages=write,administration=write`
* Request id: `806E:285EA4:6F3A8:B63A5:6AD923A9`
* Response: `{"message":"Resource not accessible by integration","documentation_url":"https://docs.github.com/rest/pages/pages#update-information-about-a-apiname-pages-site","status":"403"}`

The setting must be changed by someone holding `pages: write` (Settings → Pages → Build and deployment → Source → GitHub Actions). Until then both publishers keep writing to the same URL.

