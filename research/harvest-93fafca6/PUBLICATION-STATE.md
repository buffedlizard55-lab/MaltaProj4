# Publication state of the live site

Read at `2026-10-21T21:43:55.900741Z` from the GitHub API and the live build receipt.

| Question | Answer | Source |
| --- | --- | --- |
| How is Pages configured? | `build_type: legacy`, source `main:/`, site status `built` | [GET /repos/buffedlizard55-lab/MaltaProj4/pages](https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages) |
| Which publisher is serving now? | `committed-root-fallback` — **the legacy root fallback overwrote the verified artifact** | live [build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) revision `ac5c81648d40e4b851ae954b6acb00acfdbee096` |
| What does the live receipt say? | built `2026-10-21T21:27:37.090500Z`, snapshot `2026-10-21T21:27:36.742398Z`, 75 rows, 0.27 h old | [live build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) |
| What does the committed root fallback say? | revision `ac5c81648d40e4b851ae954b6acb00acfdbee096`, built `2026-10-21T21:27:37.090500Z`, 75 rows | [build-info.json on main](https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/build-info.json) |
| Is the served board inside its 8-hour evidence window? | yes | derived from the two timestamps above |
| Can the legacy builder still overwrite it? | **yes** | Pages `build_type` above |

## Last Pages builds (both publishers write here)

| Created (UTC) | Status | Commit |
| --- | --- | --- |
| 2026-10-21T21:28:38Z | built | `c55b4b0eeb3e5adfa78204b6627e850872820bd6` |
| 2026-10-21T21:26:34Z | built | `edb16405530407397c4f811f1db4dca31fbe00dd` |
| 2026-10-21T21:22:16Z | built | `ac5c81648d40e4b851ae954b6acb00acfdbee096` |
| 2026-10-21T21:16:45Z | built | `7148716ef03785bb69f6d0c1d50534df91473387` |
| 2026-10-21T21:14:07Z | built | `47c1b9d3917ed97bf4510fcfbe476103121ceb93` |
| 2026-10-21T21:11:31Z | built | `87db124a0bab668243e67e534e897dfda513a3ea` |

## Last publication workflow runs

| Started (UTC) | Event | Conclusion | Run |
| --- | --- | --- | --- |
| 2026-10-21T21:42:03Z | pull_request | success | [39680891989](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39680891989) |
| 2026-10-21T21:42:00Z | push | None | [39680885622](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39680885622) |
| 2026-10-21T21:39:23Z | pull_request | failure | [39680542604](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39680542604) |
| 2026-10-21T21:37:53Z | pull_request | failure | [39680345344](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39680345344) |
| 2026-10-21T21:37:50Z | push | failure | [39680339589](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39680339589) |
| 2026-10-21T21:37:22Z | pull_request | failure | [39680279310](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39680279310) |
| 2026-10-21T21:29:14Z | push | failure | [39679174581](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39679174581) |
| 2026-10-21T21:26:35Z | push | failure | [39678819340](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39678819340) |

## Owner-level fix attempt

`PUT https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages` with payload `{"build_type": "workflow"}`

* HTTP status: **403** (HTTP 403)
* GitHub says these permissions are accepted: `pages=write,administration=write`
* Request id: `CC03:2030B:17B16DA:4CFF3F2:6AD9321D`
* Response: `{"message":"Resource not accessible by integration","documentation_url":"https://docs.github.com/rest/pages/pages#update-information-about-a-apiname-pages-site","status":"403"}`

The setting must be changed by someone holding `pages: write` (Settings → Pages → Build and deployment → Source → GitHub Actions). Until then both publishers keep writing to the same URL.

