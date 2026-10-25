# Session fec4894f — independent reproduction of the 2026-10-25 publish freeze, and what the live board serves now

Written 2026-10-25 14:20 UTC. Everything below was measured in this session; nothing is
inferred from another session's report. Where a claim depends on a GitHub Actions run, the run
URL and the API field or page region it came from are named.

## 1. What was broken, and how it was found without reading the job log

`main` at `6ade440` had a red publisher. Two scheduled runs had failed at the same step:

| Run | Started | Failing step | Result |
| --- | --- | --- | --- |
| [40170923727](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40170923727) | 06:56:44Z | `Build and independently verify every row, calculation and internal link` | `verify-build` 4m 31s, `deploy` failed |
| [40193317196](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40193317196) | 12:29:19Z | same step | `verify-build` 4m 32s, `deploy` 6m 11s |

Evidence: `/actions/runs/<id>/jobs` (job list, per-step conclusions) and the run page's
"Annotations" table, which reported 8 errors: `verify-build ... Process completed with exit code 1`
and, in `deploy`, `Error: No artifacts named "github-pages" were found for this workflow run`
— i.e. `upload-pages-artifact` never ran because the build step before it failed.

The job log itself was **not** readable here: `gh run view --log-failed` and the
`/actions/jobs/<id>/logs` endpoint both redirect to
`productionresultssa17.blob.core.windows.net`, which answers
`curl: (35) OpenSSL SSL_connect: SSL_ERROR_SYSCALL` from this sandbox. The run's artifacts
(`audit-40193317196`, 1.64 MB) are on the same host and are equally unreachable.

So the failing command had to be reproduced on a runner. `.github/workflows/harvest-fec4894f.yml`
(included in this PR) runs the four commands of that one step **separately**, each with
`continue-on-error`, and commits every log to `research/harvest-fec4894f/`.

## 2. The failing command and the exact assertion

Run [40197553353](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40197553353),
receipt in this directory. Gates 1, 2 and 4 passed; gate 3 failed:

```
python -m scripts.validate --data runtime/latest.json
  File "scripts/validate.py", line 122, in validate_model_row
    assert lineup_source_ok(m, team, check.get('lineup') or []), 'Model roster has no HLTV source on this row'
AssertionError: Model roster has no HLTV source on this row
```

Reproduced locally on the captured snapshot (`snapshot.json` in this directory, captured
13:30:13Z, 78 rows / 17 open / 17 picks / 17 win probabilities / 0 unresolved), which isolates
the row:

```
FAIL row 1086697 ['Projeto do KinGui', 'Yawara'] team Projeto do KinGui
  VRS roster on the row      ['drg', 'ALLE', 'ckzao', 'xureba', 'lash']
  HLTV lineup on the row     {'team': 'Tropa do KinGui', 'players': ['drg','ALLE','ckzao','xureba','lash']}
```

The roster is identical and fully sourced; the two sources simply use different labels for one
club. `data/identities.json` already registers `Tropa do KinGui`, `Projeto do KinGui` and
`ex-Keyd Stars` as one club, with an HLTV match page as the primary source
(<https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7>),
and `scripts/core.norm` resolves that alias when matching fixtures — but `lineup_source_ok`
compared literal names, so correct evidence could never match. Because the assertion sits in
`validate_model_row`, it aborted the whole snapshot: `upload-pages-artifact`, the legacy `main:/`
staging step and `deploy` were all skipped, and the public board aged past its eight-hour evidence
window with every pick withheld.

**Ownership.** `main` fixed this independently at `e9429e6` (`same_club`, PRs
[#314](https://github.com/buffedlizard55-lab/MaltaProj4/pull/314) /
[#322](https://github.com/buffedlizard55-lab/MaltaProj4/pull/322)), before this session had a
fix ready to merge. This session reproduced the defect and **stood down** rather than layering a
second version; the reproduction and the captured failing snapshot are kept here as independent
evidence for that repair.

## 3. A process defect in this session's own harness (recorded, and fixed)

The first version of the harvest workflow wrote every gate as
`python ... 2>&1 | tee log | tail -n`, so the step's exit status was `tail`'s. A red gate was
therefore recorded as `success`, and `run.json` from run 40197553353 claims eight green exit codes
even though gate 3 had failed. The logs in this directory are the authoritative record for that
run. Every step that pipes now sets `set -o pipefail`, so the next receipt's exit codes are
truthful. This is also a warning for anyone reading older receipts in this repository: check the
log, not the outcome field.

## 4. What the public site serves now (measured, with a cache-buster)

GitHub Pages serves its edge copy for a while, so a plain fetch of the public site returned the
**01:47:42Z build** for more than two hours after newer builds had been published. Re-reading the
same URLs with a cache-busting query returned the current bytes, which is also why
`scripts/verify_live.py` appends `?deployment=...` to every attempt:

| Read at 14:13Z | URL | Result |
| --- | --- | --- |
| No cache-buster | `…/MaltaProj4/build-info.json` | revision `cbe9dce`, built `2026-10-25T01:47:42Z`, 79 rows — an edge copy, not the live deployment |
| Cache-buster | `…/MaltaProj4/build-info.json?cb=1413` | revision `06915a8`, built `2026-10-25T13:56:26Z`, snapshot `13:56:26Z`, **78 rows** |
| Cache-buster | `…/MaltaProj4/picks.html?cb=1416` | the pick board renders 16 open rows, each with a pick, both teams' percentages, a method label, an "Expires" time and its own source links |

Rows read directly from that page (first three, verbatim): `Infinite vs BRUTE` → pick `BRUTE`,
43.5% / 56.5%, "OUR FAIR LINE · 2.30 / 1.77", Polymarket market 6072808; `Color vs ex-Zero
Tenacity` → pick `Color`, 68.8% / 31.2%, "OUR MODEL LINE (VRS)", Valve standings `2026-10-05`
commit `eec4853` plus the HLTV fixture page; `Projeto do KinGui vs Yawara` → pick `Projeto do
KinGui`, 51.0% / 49.0%, model line, HLTV fixture 2399918. Every row carries a `hotspawn.com` or
`play.hotspawn.com` link plus `Evidence & lines`.

`build` and `validate` on `main`'s committed snapshot (`d5b0739`, generated 13:46:54Z) reproduce:
78 rows, 16 with percentages at this clock (one fixture has since passed its lock), **0 without a
percentage and 0 unresolved**; 15 pages, 724 links/assets, 20 checksums, 180 displayed rows. The
committed `index.html` carries
`<span data-completeness>Every one of the 17 open matches has a pick, and every pick carries a win
probability.</span>`, and the stale notice is `hidden` in the served markup
(`<div id="runtime-stale" class="notice error" role="status" hidden>`), so it is only revealed by
`assets/app.js` if the built timestamp cannot be verified.

All twelve Chromium suites pass on that tree at 320×568, 390×844, 412×915, 768 and 1440px
(`npm run test:browser`), including the phone gate "first pick and both probabilities above the
320x568 tab bar".

## 5. Limitations recorded here, not papered over

* A cache-busted read is the only valid read of this deployment. Any future "live bytes" claim in
  a receipt must say which URL was read and whether it was cache-busted.
* The row `1086697` model line rests on Valve's 2026-10-05 standings, 20 days old at publication.
  That is inside `scripts/vrs.py` `MAX_STANDINGS_AGE_DAYS = 62` because Valve publishes monthly,
  but it is an old input for a published percentage and is stated on the row.
* This session could not independently confirm any live betting line against an external book:
  outbound access here is limited to `github.com`, `codeload.github.com`, `api.github.com`,
  `registry.npmjs.org` and `pypi.org`. Source-line verification was performed by the refresh
  runner (receipts in `data/`, `research/harvest-fec4894f/`) and by the independent auditor
  `verification-c6/audit_snapshot.py`, whose replay of every stored quote is part of the gates
  above. Where no line exists, the row keeps its labelled model line or stays in the unresolved
  section with its attempts; no value here was filled in by hand.

## 6. Files

| File | What it is |
| --- | --- |
| `.github/workflows/harvest-fec4894f.yml` | non-publishing diagnostic harness: refreshes, rebuilds, runs the four publish gates separately, writes a coverage receipt for every open match, commits the receipts to the session branch |
| `research/harvest-fec4894f/snapshot.json` | the 13:30:13Z capture that fails `scripts.validate` on `main`@`6ade440` and passes with the alias-aware check |
| `research/harvest-fec4894f/validate-fresh.log`, `post-refresh-validate.log`, `post-refresh-integrity.log`, `post-refresh-unit.log` | the failing gate and its 16 downstream unit failures |
| `research/harvest-fec4894f/coverage.json` | per-match pick, probabilities, method, reason and attempted source URLs for all 17 open matches |
| `research/harvest-fec4894f/row-audit.md`, `published-row-audit.md` | `verification-c6/audit_snapshot.py` replays of the candidate and of the published copy |
