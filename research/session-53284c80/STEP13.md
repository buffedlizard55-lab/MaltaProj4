# Session 53284c80 — independent reproduction of the step-13 freeze

Measured 2026-10-25 13:30–13:40 UTC. Not copied from another session's snapshot.

## What failed

`pages.yml` scheduled runs
[40170923727](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40170923727)
and
[40193317196](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40193317196)
both died at *Build and independently verify every row, calculation and internal
link*. Refresh and quarantine succeeded; `upload-pages-artifact` was skipped;
`deploy` then failed with no `github-pages` artifact. The committed 01:47Z
snapshot aged out of its 8-hour window, so the live board withheld every pick.

## Independent reproduction (this sandbox, no live Hotspawn)

Using the committed identity register and `scripts.validate.lineup_source_ok`
on a synthetic row shaped like Hotspawn fixture `1086697`:

| Comparison | Result |
| --- | --- |
| `plain_name("Projeto do KinGui")` | `projetodokingui` |
| `plain_name("Tropa do KinGui")` | `tropadokingui` |
| `core.norm` of both labels | equal (`tropadokingui`) |
| identity register | names `Tropa do KinGui`, `Projeto do KinGui`, `ex-Keyd Stars` |
| identity primary source | https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7 |
| identity corroboration | https://gamma-api.polymarket.com/markets/6033256 |
| `lineup_source_ok` with the Hotspawn label (before the fix) | **False** |
| `lineup_source_ok` with the HLTV label (before the fix) | True |

`verification-c6/audit_snapshot.py` already uses `same_team()` (identity-aware),
so quarantine reports zero failures. Step 13 then runs `scripts.validate`,
which used `plain_name`, so one model row kills the whole publish.

## Fix

`scripts.validate.same_club` now uses `core.norm`. The roster still has to
match player-for-player on an HLTV page carried on the row. Unregistered
labels still fail. Session 046b2e46 claimed the same file on PR #314 with
the same comparison; this session reproduced the defect independently and
keeps the change so a merge of either branch unblocks publication.

## What this does *not* claim

No live Hotspawn / HLTV / Polymarket bytes were read from this sandbox. A
fresh capture is running as
[40197787382](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40197787382)
(`research/harvest-53284c80/` once it lands).
