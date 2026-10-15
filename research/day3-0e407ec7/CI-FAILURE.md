# Why the 21:22 UTC publication run failed — diagnosis by session 0e407ec7

**Status: resolved on `main` by session d3af051a (PR #18, merge `1eeabbe`).** This file is the independent
diagnosis this session claimed on the shared board, kept because it reproduces the failure from retained evidence
and because the same class of mismatch is the reason this session's own research snapshot still shows it.

## 1. What failed

- Workflow: `.github/workflows/pages.yml` (`Verify, refresh and publish CS2 Scout`).
- Run: **38809354350**, scheduled 2026-10-15 21:22 UTC.
- Step: **"Build and independently verify every row, calculation and internal link"**, specifically
  `python verification-c6/audit_snapshot.py runtime/latest.json --output runtime/independent-row-audit.md`.
- Effect: `verify-build` exited non-zero → the `deploy` job (which `needs: verify-build`) never ran → nothing was
  published, and the live site kept serving the previous successful build. That is the workflow behaving correctly:
  a build that cannot be independently verified is not allowed to deploy.

## 2. The exact failing row

Reproduced by this session from its own retained harvest (workflow
`.github/workflows/harvest-0e407ec7.yml`, run **38818433905**, snapshot `2026-10-15T22:38:20.799818Z`,
SHA-256 `3acb9a6bcd98f720135e88478ef003bb6243cd5df09ed4d91825675de46e1852`), which was produced by the pre-fix code:

```
research/harvest-0e407ec7/row-audit.md:5   Rows checked: **86** · Arithmetic/field failures: **1**
research/harvest-0e407ec7/row-audit.md:92  | [1081529](https://play.hotspawn.com/cs2-pickems) | Nexus / WROTBERRY |
                                           Not priced; blank values checked |
                                           Research pick without exactly one verified rank per team |
research/harvest-0e407ec7/logs/row-audit.exit            exit=1
research/harvest-0e407ec7/logs/published-row-audit.exit  exit=1
research/harvest-0e407ec7/logs/refresh.exit              exit=0
research/harvest-0e407ec7/logs/build.exit                exit=0
research/harvest-0e407ec7/logs/validate.exit             exit=0
```

Only the independent auditor failed. The refresh, the build and the validator all exited 0, which is why the
pipeline died at the audit step rather than earlier: the row was internally consistent but could not be
re-verified from the retained evidence.

## 3. Root cause

Fixture **1081529 Nexus / WROTBERRY** (DraculaN Season 7) has no usable exchange or bookmaker line, so the pipeline
fell back to the research tier and picked the better-ranked team from HLTV ranking context.

Two different normalisers were involved:

- `scripts/core.py` resolves ranks through `norm()`, which is **alias-aware** (it applies `ALIAS_MAP` built from
  `data/identities.json`). With the `WROTBERRY ↔ WBT` alias registered, the feed name `WROTBERRY` matched ranking
  evidence recorded under `WBT` (#109) and `Nexus` (#139), so the pipeline produced a directional research pick.
- `verification-c6/audit_snapshot.py` (at `6a5335cc`) resolved the same evidence through `name()`:

  ```python
  def name(value):
      return ''.join(c for c in unicodedata.normalize('NFKC', value).casefold() if c.isalnum())
  ```

  `name()` is deliberately **not** alias-aware — the auditor is meant to be independent of the pipeline's own
  mapping. So `name('WROTBERRY') != name('WBT')`, the auditor found zero ranking hits for that team, and line 76 of
  the old auditor fired:

  ```python
  hits = [v for k, v in ranks.items() if k and k == name(team)]
  require(len(hits) == 1 and isinstance(hits[0], int) and hits[0] > 0,
          'Research pick without exactly one verified rank per team')
  ```

In one sentence: **the pipeline could see a rank for WROTBERRY only by way of an alias, and the independent auditor
refused to accept a rank it could not see under the fixture's own name.** The auditor was right to refuse; the row
was carrying a pick whose evidence was not self-contained.

## 4. The fix now on `main`, and this session's verification of it

`main` (`9757a74`, which includes d3af051a's fix and PR #24's later hardening) carries the fix: ranking evidence is stored **per team under the name the fixture uses**,
and a one-sided tier `research_rank_single` exists for fixtures where only one of the two teams has a verifiable
world ranking. The auditor now accepts `research_rank*` methods and checks each tier explicitly
(`verification-c6/audit_snapshot.py`, lines 62–98 in the current revision).

Verified by this session against the published snapshot, not against the commit message:

```
$ python verification-c6/audit_snapshot.py data/latest.json --output /tmp/row-audit.md && tail -1 /tmp/row-audit.md
/tmp/row-audit.md: 0 failures

$ python -m scripts.validate --data data/latest.json --site .
  "pages": 15, "internal_links_and_assets_checked": 557,
  "artifact_checksums_verified": 20, "displayed_match_rows_verified": 210
```

Coverage effect of the same fix, measured on three snapshots (pre-fix = this session's own harvest at 22:38Z, produced by the
pre-fix code; the two post-fix rows are `data/latest.json` before and after PR #24 added the VRS model tier):

| Snapshot | open rows | with a published probability | research-only pick, no percentage | **no pick at all** |
| --- | --- | --- | --- | --- |
| pre-fix (`research/harvest-0e407ec7/latest.json`) | 22 | 15 | 4 | **3** — `1079586` NIP/Team Liquid, `1081502` Procyon/LOS NINOS, `1081526` Infinite/Insiders |
| post-fix (`data/latest.json`, capture generated 2026-10-15T22:37:11Z) | 22 | 17 | 5 | **0** |
| post-fix, after PR #24 added the VRS model tier (`data/latest.json`, capture generated 2026-10-15T23:12:43Z) | 22 | **20** — 12 `exchange`, 5 `exchange_wide`, 3 `model_vrs` | 2 — `research_rank_single` | **0** |

So the fix did two things at once: it made the research evidence self-contained for the auditor, and it removed the
three rows that had no supported pick, which is what the user's "a pick for every match" requirement needs.

## 5. Separate failure in this session's own harvester (not the publication path)

Run 38818433905 also failed its last step, for an unrelated reason: `scripts/harvest_0e407ec7.py` built
`open_pick_methods` as `dict(collections.Counter(m.get('method') for m in opens))`, and three open rows carry
`method: null`, so `json.dumps(..., sort_keys=True)` raised

```
TypeError: '<' not supported between instances of 'str' and 'NoneType'
```

(`research/harvest-0e407ec7/logs/summary.exit` = `exit=1`, traceback in `logs/summary.txt`). Keys are now
stringified, `tests/test_harvest_0e407ec7.py` reproduces the `None`-method case and asserts the counts are
re-derived from the snapshot rather than authored, and re-running the summariser on the exact snapshot that crashed
now exits 0:

```
$ python -m scripts.harvest_0e407ec7 --runtime research/harvest-0e407ec7/latest.json --output /tmp/harvest-check
"open_pick_methods": {"None": 3, "exchange": 9, "exchange_wide": 6, "research_rank": 4}
```

## 6. What this session asked for and what it did itself

The shared board records that this session claimed **report only** for the production failure, because
`scripts/**`, `tests/**`, `.github/workflows/pages.yml` and `verification-c6/audit_snapshot.py` were claimed by
sessions d3af051a and e54807b3. The code fix was theirs; the diagnosis, the reproduction from retained evidence and
the post-fix verification above are this session's. This session changed no shared pipeline file — only its own
`scripts/harvest_0e407ec7.py`, its own workflow, its own research directory, additive entries in
`data/analysis.json` / `data/review-notes.json`, and one new test file with a session-unique name.
