# Session 53284c80 — claim and starting measurements

Branch: `arena/53284c80-maltaproj4` (Arena-fixed; no other branch is used).
Claimed: 2026-10-25 13:30 UTC.

## Why this session exists

The user asked for a pick (or an explicit unresolved limitation) for every
Counter-Strike 2 match listed on Hotspawn, including low-tier fixtures that
Polymarket does not cover; an executive summary with in-site links to the
updated pick list; a separate unresolved section; and a phone-readable
dashboard that refreshes every 4–8 hours from official sources, never using
Hotspawn as a probability.

## Measured starting state

Read from the committed tree at `6ade440` and from the GitHub API. Not inferred.

| Fact | Value | Source |
| --- | --- | --- |
| Snapshot generated | 2026-10-25T01:47:42Z | `data/latest.json` |
| Fixture evidence | 2026-10-25T01:44:08Z | `data/latest.json` |
| Rows / open / picks / probabilities / unresolved | 79 / 18 / 18 / 18 / 0 | `data/latest.json` |
| Pages source | legacy `main:/` | `GET /repos/buffedlizard55-lab/MaltaProj4/pages` |
| Last successful scheduled publish | run 40151731896 | Actions API |
| Last two scheduled publishes | failed at step 13 (runs 40170923727, 40193317196) | Actions API |
| Snapshot age at claim | 11.6 hours (> 8-hour evidence window) | device clock 13:25Z |

The live board is therefore required to withhold every pick until a verified
refresh is published. This sandbox cannot reach Hotspawn, HLTV, Polymarket or
the books, so the harvest workflow in `.github/workflows/harvest-53284c80.yml`
runs the real refresh on GitHub's egress and commits receipts under
`research/harvest-53284c80/`.
