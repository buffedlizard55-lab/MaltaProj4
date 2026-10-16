# Independent audit of what is actually published — 16 October 2026

Session `ef0969b9`, independent-verification lane. Everything here was read from the
live site or from the source APIs named, with the read time recorded. Nothing was
inferred, and anything not re-read is marked as such.

## 1. The published artifact

| Read | Endpoint | Result |
| --- | --- | --- |
| 07:30Z | `…/build-info.json?cb=ef0969b9-0730` (cache-busted) | revision `693b6374c033a0bc1e1e6489414c79cffce828b2`, `built_at` `2026-10-16T07:27:52.068181Z`, `snapshot_generated_at` `2026-10-16T07:27:51.689935Z`, **106 rows**, 20 files with sha256 |
| 07:28Z | `…/build-info.json` (no cache-buster, same URL) | revision `f91ca1a9…`, `built_at` `2026-10-16T05:11:55.617221Z`, 95 rows — **the previous artifact** |

That second row is a measured, reproducible trap, not an anomaly: two reads of the
same URL ~2 minutes apart returned two different artifacts, and only the
cache-busted one matched the site's own page content (`Observed 16 Oct · 07:27 UTC`
on every row). It independently confirms the request already on the board from
`ab18fe2a` and `dedd2e34`, and it means **any staleness check that reads
`build-info.json` without a cache-buster can report a false "stale" or a false
"fresh"**. The new `pages.yml` live check uses `?deployment=<run_id>`, which is the
correct treatment.

`693b6374` is the current `origin/main` (PR #35 merge), so the live site is built from
the tip of `main`, not from a stale branch.

## 2. Row-level replay against the source markets

Sampled rows, re-read from the market API at 07:23–07:31Z, compared with the row the
site publishes:

| Row (site) | Site values (07:27Z build) | Source re-read | Verdict |
| --- | --- | --- | --- |
| NiP vs Team Liquid (1079586) | 49.5% / 50.5%, pick Team Liquid, "Exchange line", `Polymarket 5732258` | `5732258`: outcomes `["NIP","Liquid"]`, `0.495 / 0.505`, `updatedAt` 07:31:09Z, spread 0.01, liquidity $313,966 | **exact match** |
| Aurora vs 9z (1080205) | 69.5% / 30.5%, pick Aurora, `Polymarket 5733288` | `5733288`: `0.695 / 0.305`, bid 0.69/ask 0.70, `eventStartTime` 14:00Z | **exact match** |
| BetBoom vs Legacy (1081775) | 36.5% / 63.5%, pick Legacy, `Polymarket 5763247` | `5763247`: `0.635 / 0.365`, read 07:23Z | **exact match** |
| Procyon vs LOS NINOS (1081502) | 67.2% / 32.8%, "Bookmaker fallback", Pinnacle link, observed 07:18Z | Polymarket event `1192433` / market `5721649`: `0.69 / 0.31`, `gameStartTime` 16:00Z, `updatedAt` 07:21:08Z | **agree within 1.8 points** across two independent sources; the fixture is no longer unpriced |
| Voca vs Phantom (1080285) | 45.5% / 54.5%, pick Phantom, row itself flags "favourite differs" from the VRS model (53.9% Voca) | not re-read this session (market `5583525`) | **unverified here** — the row's own flag is present and consistent with an exchange line below the model |

No sampled row showed a number without a named source, and no row showed a
probability that the cited market did not carry.

## 3. Coverage and the "no pick" requirement

Read from the live executive summary and the complete unresolved page (2 chunks):

* **106 feed entries, 42 open.** 39 open matches carry a published probability — 27
  from betting markets and 12 from the labelled VRS model line; 3 carry a labelled
  research-only pick with **no** percentage; **0 open matches have no supported pick**.
* The unresolved page lists 15 rows, and every row states its limitation. The three
  research-only rows are explicit one-sided ranking signals ("only one team is
  world-ranked", "no percentage is published") rather than silent guesses.
* Footer of both pages: "Blank percentages = unverified; never a default 50/50." The
  rows I checked follow that rule.
* The executive summary's own numbers ("39 of 42 open matches…") match the counts on
  the picks page and the unresolved page, and each is an in-site link
  (`picks.html`, `index.html#unresolved-summary`, `analysis.html#guidance`,
  `matches.html?status=open`).

## 4. Refresh cadence, measured

* The gap between the two published artifacts I observed today is
  **05:11:55Z → 07:27:52Z = 2h16m** — inside the user's 4–8 h window.
* That delivery came from **push-triggered** runs (PR #35 merge and the harvest
  commits), not from the schedule: the scheduled-run record is still only three runs
  ever, with none for the 05:17/06:17/07:17Z slots (`gh api …/runs?event=schedule`).
* Consequence, stated plainly: **the 4–8 h requirement is currently satisfied by
  merge activity, not by the scheduler.** The staggered cron plus the freshness gate
  in this session's PR #36 is aimed at that gap; the watchdog remains the backstop.

## 5. What this audit could not verify, and why

* **Live byte checksums.** The sandbox cannot open raw HTTP to the Pages host (TLS
  EOF), so the 20 sha256 values in the receipt are quoted from the site, not
  recomputed here. The workflow's post-deploy step recomputes them in CI with a
  cache-buster.
* **Job logs/artifacts.** `gh run view --log` and `gh run download` fail with EOF from
  this sandbox, so CI conclusions are step-level only.
* **Hotspawn-side inventory.** The Hotspawn endpoints were not re-fetched for this
  audit; "every listed match" is therefore checked as "every row the board publishes",
  not re-derived from Hotspawn.
* **One sampled market** (`5583525`, Voca vs Phantom) was not re-read; the row is
  marked unverified above rather than assumed correct.
