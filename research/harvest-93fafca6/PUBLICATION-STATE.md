# Publication state of the live site

Read at `2026-10-21T21:48:31.568019Z` from the GitHub API and the live build receipt.

| Question | Answer | Source |
| --- | --- | --- |
| How is Pages configured? | `build_type: legacy`, source `main:/`, site status `built` | [GET /repos/buffedlizard55-lab/MaltaProj4/pages](https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages) |
| Which publisher is serving now? | `committed-root-fallback` — **the legacy root fallback overwrote the verified artifact** | live [build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) revision `ac5c81648d40e4b851ae954b6acb00acfdbee096` |
| What does the live receipt say? | built `2026-10-21T21:27:37.090500Z`, snapshot `2026-10-21T21:27:36.742398Z`, 75 rows, 0.35 h old | [live build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) |
| What does the committed root fallback say? | revision `ac5c81648d40e4b851ae954b6acb00acfdbee096`, built `2026-10-21T21:27:37.090500Z`, 75 rows | [build-info.json on main](https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/build-info.json) |
| Is the served board inside its 8-hour evidence window? | yes | derived from the two timestamps above |
| Can the legacy builder still overwrite it? | **yes** | Pages `build_type` above |

## Last Pages builds (both publishers write here)

| Created (UTC) | Status | Commit |
| --- | --- | --- |
| 2026-10-21T21:47:50Z | built | `2d5da84766ee58941d70d3f356366d7d4b346609` |
| 2026-10-21T21:44:31Z | built | `1b2d92e4df9082d99c16731d66d14f2209b10b20` |
| 2026-10-21T21:28:38Z | built | `c55b4b0eeb3e5adfa78204b6627e850872820bd6` |
| 2026-10-21T21:26:34Z | built | `edb16405530407397c4f811f1db4dca31fbe00dd` |
| 2026-10-21T21:22:16Z | built | `ac5c81648d40e4b851ae954b6acb00acfdbee096` |
| 2026-10-21T21:16:45Z | built | `7148716ef03785bb69f6d0c1d50534df91473387` |

## Last publication workflow runs

| Started (UTC) | Event | Conclusion | Run |
| --- | --- | --- | --- |
| 2026-10-21T21:47:52Z | push | None | [39681645436](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39681645436) |
| 2026-10-21T21:47:48Z | pull_request | failure | [39681637719](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39681637719) |
| 2026-10-21T21:47:39Z | pull_request | None | [39681619032](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39681619032) |
| 2026-10-21T21:45:19Z | pull_request | success | [39681317742](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39681317742) |
| 2026-10-21T21:44:32Z | push | None | [39681213626](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39681213626) |
| 2026-10-21T21:42:03Z | pull_request | success | [39680891989](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39680891989) |
| 2026-10-21T21:42:00Z | push | success | [39680885622](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39680885622) |
| 2026-10-21T21:39:23Z | pull_request | failure | [39680542604](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39680542604) |

## Owner-level fix attempt

`PUT https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages` with payload `{"build_type": "workflow"}`

* HTTP status: **403** (HTTP 403)
* GitHub says these permissions are accepted: `pages=write,administration=write`
* Request id: `D003:3C011A:B7DBD:128941:6AD93330`
* Response: `{"message":"Resource not accessible by integration","documentation_url":"https://docs.github.com/rest/pages/pages#update-information-about-a-apiname-pages-site","status":"403"}`

The setting must be changed by someone holding `pages: write` (Settings → Pages → Build and deployment → Source → GitHub Actions). Until then both publishers keep writing to the same URL.

