# Session afed58c5 — CS2 coverage, sources, mobile and delivery

**Started:** 2026-10-24 16:23 UTC  
**Fixed branch:** `arena/afed58c5-maltaproj4`  
**Status:** source capture and integration in progress; this report does not yet claim a current published board.

## User requirements being tested

1. Re-read every CS2 fixture in Hotspawn's pick'em inventory on a recurring 4–8-hour (or denser) workflow, including low-tier matches.
2. Never use Hotspawn's crowd percentages as win probabilities. Resolve featured rows through the existing external-market path; only rows that path cannot resolve enter the HLTV-first, then esportsbook/exchange/model/research ladder.
3. Give every open match an obvious pick and two-sided win probability when reproducible external evidence or the explicitly labelled originated model supports them. Otherwise leave unknown values blank and publish the exact limitation in a separate unresolved section linked from the executive summary.
4. Make the executive summary a phone-friendly index to the updated picks, the at-a-glance cards, unresolved limitations, all matches and flagged findings.
5. Re-derive every displayed number and check every row's official source link before integration. Publish irregularities rather than hiding them.

## Measured starting state — not a current-pick claim

- The committed/public manifest is [`build-info.json`](../../build-info.json), revision `71eddff72730e81b45bcebb2eaf3ecc054cab356`, snapshot `2026-10-24T08:06:51.009717Z`, 92 retained feed rows. The live [manifest](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) returned those same values when read through the retrieval tool on 24 October.
- At approximately 16:30 UTC the live [executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/) explicitly said **“Snapshot expired or timestamp unverified. Current picks are withheld.”** It displayed 22 still-open rows but zero current picks. This is the intended fail-closed behaviour for old evidence, not an acceptable refreshed result.
- GitHub's official [run 40097410704](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40097410704) (scheduled at 13:16 UTC) passed its pre-refresh unit suite, official-source refresh, quarantine, build, independent row audit and browser step. It then failed at **“Keep the legacy main:/ root fallback on the verified build”** with the annotation **“The staged root failed its own validator or unit gate”**; deployment was skipped. Runs 40084520702, 40082763751 and 40080448344 failed at the same step. The fresh-capture workflow below records the post-refresh unit failure instead of guessing its cause.
- GitHub's official [Pages API](https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages) reports legacy `main:/` publishing. The latest Pages build at inspection was commit `45fc6ba3244750e2b7fa2118b15b5e7114901e5b`, created 10:05 UTC.

## Independent official-source observations (retrieval tool, 24 October)

These observations establish the need for a fresh capture. The runner snapshot, not this prose, is the line-by-line source of the integration candidate.

| Source | Manual review link | Observed result | Use permitted here |
| --- | --- | --- | --- |
| Hotspawn CS2 pick'em page | https://play.hotspawn.com/cs2-pickems?cb=202610241630 | Page rendered successfully and its own filters reported **All tiers (83)** / **All tournaments (83)**. It listed current and future fixtures, including low-tier C events. | Fixture inventory, teams, competition and locks only. The displayed “% picked” crowd votes were read only as page text and are explicitly rejected as probability inputs. |
| Hotspawn general lobby | https://play.hotspawn.com/lobby?cb=202610241630 | Independently rendered the same **83** CS2 filter count and matching visible fixture links. | Second official inventory view; never a probability source. |
| Hotspawn public scheduled-CS2 feed | https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1 | Official JSON endpoint returned fixture objects with IDs, participants, scheduled starts and lock times. The complete exact response and three-view parity are being captured on the authorized runner. | Structured fixture facts only; `participants*_picked_percent` is never used. |
| HLTV match index | https://www.hltv.org/matches | Official match index rendered successfully. | Identity, fixtures, rankings and form research. HLTV community votes are not market probabilities. |
| Public dashboard manifest | https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json | Confirmed the expired 08:06:51Z snapshot/revision above. | Deployment/freshness verification only. |

The 83-count observation differs from the old 92-row retained feed because Hotspawn rotates records out of its scheduled endpoint. No missing old row is silently reclassified as a current match; the fresh three-view capture determines the new retained set and open subset.

## Fresh authorized-runner capture

- Workflow: [`.github/workflows/harvest-afed58c5.yml`](../../.github/workflows/harvest-afed58c5.yml)
- First run: [40111530750](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40111530750), triggered by commit `857d8b1` with `[capture]`.
- The job is **non-publishing**. It runs the same refresh/quarantine/build path as production, the independent C6 row audit, the zero-shared-code pick re-derivation, the per-rung coverage ledger, a gap-only research probe, the complete committed unit suite against the refreshed snapshot, and all browser suites. It commits only dated evidence under `research/harvest-afed58c5/` to this fixed branch.
- Essential refresh/audit/build failures fail the job. Post-refresh unit and browser failures are retained as diagnostics for repair and are **not** waived at final integration.

## Local baseline verification and one stale-board browser defect

Using the pinned dependencies in `requirements.txt` and a clean Node install:

- `python -m unittest discover -s tests`: **1,484 tests passed, one skipped**.
- `scripts.validate --site .`: 92 rows, 29 historical calculations reproduced, 15 pages, 858 internal links/assets, 20 checksums, 227 displayed match rows.
- `scripts.validate --site public`: 92 rows, 29 historical calculations reproduced, 15 pages, 931 internal links/assets, 20 checksums, 245 displayed match rows.
- The browser command passed the general 32 page/viewport accessibility/no-overflow scans and expiry suite, then failed `tests/browser_019a253a.cjs`: on the expired board there are 22 open fixtures with every current pick withheld, while its fallback-ladder assertion expects method counts summing to 22 and gets zero. This is a real stale-snapshot accounting/test mismatch, retained for scoped repair if it also affects the fresh candidate; it is not being “fixed” by restoring expired probabilities or fabricating picks.

## Evidence rules and current limitations

- Hotspawn and HLTV crowd votes are not betting lines and are never probability inputs.
- A bookmaker/exchange quote must retain its exact fixture identity, start, source URL, observation/update time and calculation inputs. Wide or illiquid lines follow the existing published gates and labels; equal/placeholder prices are refused.
- Originated VRS estimates are calculations, not “official odds” or guaranteed forecasts. Their Valve/HLTV inputs and formula must replay exactly.
- Missing or contradictory evidence stays blank and appears on **Unresolved & limitations** and **Flagged for Review**. Source access restrictions are recorded, not bypassed.
- The authoring sandbox cannot make ordinary bash requests to the esports hosts. Retrieval-tool observations are documented above; the full automated source read runs on GitHub-hosted egress with durable receipts.

## Official Valve model-source verification

At 16:30:09 UTC, Valve's official repository head was still [`eec4853d…`](https://github.com/ValveSoftware/counter-strike_regional_standings/commit/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75) (“Updating Regional Standings for 10/5/2026”), and the Contents API listed `standings_global_2026_10_05.md` as the newest global file. The exact official file and the vendored input both hash to `df96e7fc3cd91a2687ec08cac0128e50cc4e4e55346581679572e881d79ae61b` (byte-identical). The official `fit.js`, `glicko.js` and `modelfit.png` were retrieved at that same pinned commit and are retained under [`official-valve/`](official-valve/) with hashes in [`official-valve-check.json`](official-valve-check.json).

The official chart was visually read as **“Expected vs. Observed Win Rate — y = 0.7986x + 0.126.”** The site's methodology explicitly applies only the **0.7986 slope symmetrically around 50%**, not the `+0.126` intercept, so both sides sum to 100%. That is a disclosed project modelling choice; these are originated estimates, not official Valve probabilities or bookmaker lines. This distinction remains mandatory on every model row.

HLTV's dated [Valve global ranking for 24 October 2026](https://www.hltv.org/valve-ranking/teams/2026/october/24) also rendered successfully with the heading “Valve global ranking on October 24th, 2026.” It is a secondary presentation of Valve points and is never mislabeled as an operator price.

## Integration / publication receipt

Pending. No PR, merge, current coverage count or successful deployment is claimed yet.
