# Session b85ad9b4 — the 2026-10-25 publisher failure: diagnosis, repair, verification

Status: **diagnosed and repaired**; offline verification green, GitHub-egress re-verification in
progress. Nothing in this file is inferred: every number below is the output of the command next
to it, or a field of a committed receipt.

## 1. What a visitor saw

Read from the public site at 2026-10-25T13:26Z:

> Last checked 25 Oct 2026 · 01:47 UTC · 11h 40m ago · past the 90-minute refresh target
> **14 open CS2 match(es) · 0 with a pick · 0 with a win probability · 14 unresolved**
> *Snapshot expired or timestamp unverified: all current picks are withheld*

The observation that matters: the *data* was complete at 01:47Z (18 open, 18 picks, 18
probabilities, 0 unresolved). The board was not withholding because a pick could not be
found. It was withholding because it was old, and it was old because the publisher could not
replace it.

## 2. Why the publisher stopped

| Run | Slot (UTC) | Outcome |
| --- | --- | --- |
| 40151731896 | 01:43Z | success — `build-info.json` stamped `built_at 2026-10-25T01:47:42Z` |
| 40143667147 | 23:40Z (24 Oct) | failure at *Build and independently verify every row, calculation and internal link* |
| 40170923727 | 06:56Z | failure at the same step |
| 40193317196 | 12:29Z | failure at the same step → no `github-pages` artifact → `deploy` failed |

Pages is `build_type: legacy` with source `main:/`, so the committed root is what visitors
receive; the frozen 01:47Z root therefore outlived its own eight-hour window. This sandbox
has no egress to Hotspawn, HLTV or Polymarket, and this repository's job logs redirect to
blob storage outside the host allowlist, so the failing step was replayed on GitHub's egress
by the dispatch-only, non-publishing workflow `.github/workflows/diag-b85ad9b4.yml`
(`scripts/diag_b85ad9b4.py`): it runs each publication command unmodified, records its return
code and full stdout/stderr, copies the refreshed snapshot, and commits the bundle here.

Run **40197667220** (capture `2026-10-25T13:32:27Z`):

| Step | Command | rc |
| --- | --- | --- |
| 01 | `scripts.validate --data data/latest.json --site .` | 0 |
| 02 | `unittest discover -s tests` (committed tree) | 0 |
| 03 | `scripts.refresh --output runtime/latest.json` | 0 |
| 04 | `scripts.quarantine runtime/latest.json` | 0 |
| 05 | `verification-c6/audit_snapshot.py runtime/latest.json` | 0 |
| 06 | `scripts.build --data runtime/latest.json` | 0 |
| **07** | **`scripts.validate --data runtime/latest.json`** | **1** |
| 08 | `verification-c6/audit_snapshot.py public/data/latest.json` | 0 |
| 09 | `unittest discover -s tests` (fresh board) | 0 |

```
File "scripts/validate.py", line 376, in validate_data
    validate_model_row(m, q, now)
File "scripts/validate.py", line 122, in validate_model_row
    assert lineup_source_ok(m, team, check.get('lineup') or []), 'Model roster has no HLTV source on this row'
AssertionError: Model roster has no HLTV source on this row
```

## 3. The row and the exact mismatch

Hotspawn fixture **1086697** — `Projeto do KinGui` vs `Yawara`, CCT South America 2026 Series #7,
2026-10-25T19:00Z, a tier-C fixture with no exchange or bookmaker market in the capture. It was
priced by the ladder's originated Valve-VRS line: `model_vrs`, 0.5101 / 0.4899, pick
`Projeto do KinGui`, inputs Valve's official 2026-10-05 global standings (854 vs 845 points).

| Fact | Value | Source |
| --- | --- | --- |
| Hotspawn label | `Projeto do KinGui` | Hotspawn CS2 pick'em lobby |
| HLTV heading on the fixture page | `Tropa do KinGui` | HLTV match 2399918 |
| Valve's row for the same roster | `ex-Keyd Stars`, standing 144, 854 points | Valve 2026-10-05 standings |
| Roster the row verified | drg, ALLE, ckzao, xureba, lash (overlap 4 of 5) | HLTV match page lineups |

`hltv_context.lineups` stores the lineup under HLTV's own heading, `Tropa do KinGui`.
`lineup_source_ok` looked the heading up with `plain_name()` — an exact folded comparison —
which cannot see across `projetodokingui` / `tropadokingui`. The rest of the model
verification does see across it, because `scripts.core.norm()` resolves names through
`data/identities.json`, whose single sourced entry already holds `Tropa do KinGui`,
`Projeto do KinGui` and `ex-Keyd Stars` together.

So the row was correct and the re-check could not read it. A correct row that cannot be
re-checked fails `scripts.validate`; that is the step that died. It is not a one-off: any
future snapshot with an originated model line for a club whose HLTV heading differs from
Hotspawn's spelling would have frozen publication the same way.

## 4. The repair

`scripts/validate.py` only. `lineup_source_ok` now resolves the heading through a new
`same_club()`, which:

1. keeps the exact `plain_name` comparison as the primary rule — unchanged;
2. permits the identity register as the **only** bridge, under the module's existing alias
   rules: both spellings inside one `data/identities.json` entry, that entry linking an
   `https://` source, and the register keeping the fixture's two teams apart (`norm` of the two
   labels must differ), so a lineup published for one team can never satisfy the other;
3. applies to all three HLTV sources the function already accepted (fixture-page lineups,
   retained lineup receipts, and the clubs' own team pages);
4. changes no probability, no overlap threshold, no pick orientation, no freshness or
   standings-age rule, and adds no fuzzy, substring or prefix matching.

## 5. Verification

Offline, on the retained capture (`snapshot.json`, the exact file the failing run produced):

```
scripts.validate --data research/session-b85ad9b4/snapshot.json --site <built>
  78 rows / 17 calculations / 15 pages / 730 internal links and assets / 20 checksums / 182 displayed rows
scripts.build
  17 open rows · 17 with a percentage · 0 without · 0 unresolved
unittest discover -s tests
  1,617 tests OK (7 skipped), including the 11 new regressions
audits + verification-95b588c2 + verification-c6
  9 / 5 / 12 checks OK
```

`tests/test_session_b85ad9b4.py` pins the measured case and the four ways the bridge must
refuse: a different club, an unregistered spelling, a register entry with no primary source,
and a register that collapses both fixture teams. It also re-validates every row of the
captured snapshot, which is the snapshot the publisher refused to build.

The GitHub-egress re-verification of a *newly refreshed* snapshot is the second replay run
recorded in `diag.json`/`REPORT.md` in this directory; its return codes are the acceptance
signal, not a claim made here in advance.

## 6. Sources (all official)

- Hotspawn CS2 pick'em lobby — <https://play.hotspawn.com/cs2-pickems>
- HLTV match 2399918 (the heading `Tropa do KinGui`) —
  <https://www.hltv.org/matches/2399918/tropa-do-kingui-vs-yawara-cct-2026-south-america-series-7>
- HLTV match 2399904 (primary source on the identity-register entry) —
  <https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7>
- Valve official standings 2026-10-05 —
  <https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md>
- Actions runs 40151731896, 40143667147, 40170923727, 40193317196, 40197667220 —
  <https://github.com/buffedlizard55-lab/MaltaProj4/actions>

## 7. Irregularities flagged for review

Recorded in `data/review-notes.json` as
`session-b85ad9b4-alias-bridge-publication-failure-2026-10-25` and published on the site's
Flagged for Review page:

1. The repair widens what the validator accepts as an HLTV roster source. It is gated on the
   sourced identity register, but it is a widening and a reviewer should confirm the rule.
2. The defect was a standing trap, not a one-off: any originated model row for a club with a
   different HLTV heading would have blocked publication.
3. Nothing announces a red publisher publicly until the eight-hour window lapses; the site's
   expiry banner is the only signal, and by then every pick is already withheld.
