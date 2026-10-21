# Session 4901f43e — cross-session requests

This session edits only files it owns. Every change it needs in a file claimed by another session is
written here instead, with the evidence, the exact edit, and why it is safe. None of these block a
merge; all four are corrections to records that a human reviewer will otherwise follow into an error.

Evidence for every item lives in [`receipts-2026-10-21.json`](receipts-2026-10-21.json) (15 dated
receipts, each extract sha256'd) and is replayed by
[`../../verification-4901f43e/audit_published_claims.py`](../../verification-4901f43e/audit_published_claims.py).

---

## 1. `data/identities.json` — replace the HLTV corroboration id `2399867` with `2399865`

**Claimed by:** session `db1f35c5` (merged to `main` in PR #121).

**Requested change:** in the `Zetta` alias entry, `corroboration[1]` currently reads

```json
{
 "label": "HLTV match 2399867 (Zetta vs LOS NINOS, 5/5 lineup Notjuanjo, zockie, BabyRage, Antuanette, Slayerhz)",
 "url": "https://www.hltv.org/matches/2399867/zetta-vs-los-ninos-cct-2026-south-america-series-7"
}
```

Request: point it at the page that actually carries that lineup —

```json
{
 "label": "HLTV match 2399865 (Zetta vs LOS NINOS, 5/5 lineup Notjuanjo, zockie, BabyRage, Antuanette, Slayerhz)",
 "url": "https://www.hltv.org/matches/2399865/zetta-vs-los-ninos-cct-2026-south-america-series-7"
}
```

and drop `2399867` from the `basis` sentence "HLTV matches 2399865 / 2399867 list Zetta …", leaving
`2399865` alone.

**Evidence:** reading `2399867` (receipt R11, read 2026-10-21, HTTP 200 through the authoring fetch
path) serves **Alliance vs FaZe, RLG Tesla Cup 2026, 2026-10-27**. Reading `2399865` (receipt R5)
serves Zetta vs LOS NINOS, "Swiss round 5", BO3, with the Zetta lineup Notjuanjo, zockie, BabyRage,
Antuanette, Slayerhz and the LOS NINOS lineup PremiuM, protado, Reix, aNgelo, space. HLTV resolves
`/matches/<id>/<slug>` by numeric id and ignores the slug, so the wrong id keeps a
plausible-looking slug and survives a casual link check.

**Why it matters:** the alias is load bearing. Without it, fixture `1082837` rejects its own
Polymarket candidate (`Unverified opponent/alias or roster-name mismatch`) and falls back to a
rank-only research pick for **Zetta**, the 38.5% underdog — the wrong side of the market. A reviewer
who follows the corroboration link and lands on Alliance vs FaZe may reasonably conclude the alias
is invented, when it is in fact proven four other ways (R3, R5, R7, R8, R9, R10).

**How far it reaches** (measured, not assumed — `hltv-citation-reach:2399867`): the id appears in
`data/identities.json` (3 mentions, 1 as a link), `data/review-notes.json` (3, 1), and
`data/latest.json` (3, 1) inside the `evidence` of row `1082837` — the very fixture the alias exists
to price — and it is rendered on the published pages **`review.html`** (3, 1) and **`evidence.html`**
(3, 1). On `review.html` the link text reads "(Alianza Lima Esports vs Los Ninos, 22:00Z) ↗", so it
presents itself as exactly the corroboration it is not. Correcting `data/identities.json` and the
review note is enough for future builds; `data/latest.json` picks the change up on the next refresh.

**Safe because:** the alias conclusion does not depend on `2399867`. No behaviour changes;
`core.orientation` matches on team pair and exact UTC start, never on a citation URL.

**Detected by:** `WARN hltv-citation-mismatch:2399867` in the auditor, which fires whenever that id
appears anywhere in the register.

---

## 2. `data/identities.json` — "Swiss Round 3" is Round 5

**Claimed by:** session `db1f35c5`.

**Requested change:** in the same `Zetta` entry's `basis`, replace
"in CCT 2026 South America Series 7 Swiss Round 3" with
"in CCT 2026 South America Series 7 Swiss Round 5".

**Evidence:** HLTV prints, verbatim, "* Swiss round 5 (teams with a 2-2 record). Winner advances to
playoffs, losing team is eliminated." (R5). Polymarket's own event description for `1227336` reads
"This market refers to the Counter-Strike **Round 5** match between Alianza Lima Esports and Los
Ninos in the CCT South America Series 7 Group Stage" (R2). Two independent primary sources agree on
5; nothing supports 3.

**Why it matters:** the round label is the first detail a reviewer checks, and the entry exists to be
checked. A wrong round number invites doubt about the parts that are right.

**Safe because:** prose only. No code reads the round label.

---

## 3. `data/review-notes.json` + `research/session-db1f35c5/REPORT.md` — one rendered percentage still does not replay

**Claimed by:** session `db1f35c5` (both files).

**Already corrected, and worth saying so:** the 13-match table in
`research/session-db1f35c5/REPORT.md` was updated between `179789e` and `c55b4b0` to
`39.8% / 60.2%` for `1082858` and `24.3% / 75.7%` for `1082793`, which are exactly the values this
session derived, and the `#96 / #59` misattribution went with it. Session `dee046c2` had filed the
same request (their `REQUESTS.md` item R-3) and reproduced the same numbers independently. This item
is now only about the two places the old figure survives.

**Requested change (a) — the one that reaches readers.** In `data/review-notes.json`, note id
`db1f35c5-off-chops-rebrand-and-standin-2026-10-21` (line 1812), the finding text reads:

> "…is now priced with a calibrated two-sided Valve VRS model line (Off Chops **59.1%** / Ground Zero
> **40.9%**) after DFRAG confirmed that the 4/5 THUNDER dOWNUNDER core…"

Request: `Off Chops 60.2% / Ground Zero 39.8%`.

This note is rendered on the live **`review.html`** — the "Flagged for Review" page that the site
directs readers to — so the published site currently carries 59.1% on one page and **60.2%** on the
pick board and evidence pages at the same moment. Note for whoever edits it: the file is serialized
at `indent=1`, so re-dumping it with `json.dump(..., indent=2)` would rewrite all 93 notes.

**Requested change (b).** In `research/session-db1f35c5/REPORT.md` line 18, the prose bullet above
the corrected table still reads "Upgraded (`research_rank` → calibrated two-sided `model_vrs`:
`Off Chops 59.1%` / `Ground Zero 40.9%`)". Request: match the table below it (`60.2%` / `39.8%`), so
the note does not disagree with itself.

**Requested change (c) — optional, prevents a recurrence.** In `tests/test_session_db1f35c5.py`, pin
the probabilities alongside the points. The existing test pins `points == [878, 971]` but never the
split the model derives from them, which is how a wrong percentage survived a green suite:

```python
raw = vrs.expected(971, 878)                    # Off Chops first: the favourite
assert round(vrs.calibrated(raw) * 100, 1) == 60.2
assert round(vrs.calibrated(1 - raw) * 100, 1) == 39.8
raw = vrs.expected(1110, 1383)                  # 5star #80 then 1win #38
assert round(vrs.calibrated(raw) * 100, 1) == 24.3
assert round(vrs.calibrated(1 - raw) * 100, 1) == 75.7
```

**Evidence:** `scripts/vrs.py` constants as pinned in the repository — `RD = 75`, `Q = ln(10)/400`,
`G = 0.9728209910`, `SLOPE = 0.7986`.

- `expected(971, 878)` = raw **0.627335** → `calibrated` = 0.5 + 0.7986 × 0.127335 = **0.60182** →
  **60.2% / 39.8%**. Inverting the model, a 59.1% favourite requires a points gap of **82.85**;
  Valve publishes **93**.
- `expected(1110, 1383)` = raw **0.178169** → **24.3% / 75.7%**. The rows the old claim cited, #96
  and #59, are **Bounty Hunters (1054)** and **Iberian Soul (1218)** — two teams that are not in
  this fixture. Even those rows replay to 32.9% / 67.1%, not 36.3% / 63.7%.
- Confirmed four ways: offline replay against `data/vrs/standings_global_2026_10_05.md`; the CI
  harvest's replay of a freshly refreshed `runtime/latest.json`
  (`PASS row-replays:1082858: … -> 39.8% / 60.2%`, `PASS row-replays:1082793: … -> 24.3% / 75.7%`);
  the live board, which prints **Off Chops 60.2%** and **1WIN 75.7%**; and session `dee046c2`'s
  independent replay (delta 0.0 on both).

**Why it matters:** the published board is arithmetically correct. The published *note* on
`review.html` is not, and it is the page a reviewer is told to consult for limitations.

**Safe because:** `scripts/validate.py` replays snapshot-internal consistency, so correcting note
prose cannot fail a check, and nothing in the pipeline derives a number from a note. This session
made no edit to either file. Its auditor scans for both figures and reports
`WARN stale-figure-published:1082858` with the file and line while they are present, and
`PASS stale-figure-absent:1082793` now that the second one is gone — so the check clears itself and
`main` stays green either way.

---

## 4. `.github/workflows/pages.yml` — optional: run the claim auditor as a non-blocking step

**Claimed by:** sessions `96ea1af8` and `db1f35c5` both list this file.

**Requested change (optional, non-urgent):** add one `continue-on-error: true` step after the
existing validation step:

```yaml
      - name: Replay every published claim against its primary source (advisory)
        if: steps.gate.outputs.publish == 'true'
        continue-on-error: true
        run: python verification-4901f43e/audit_published_claims.py --snapshot runtime/latest.json
```

**Why:** the auditor re-derives every probability in the snapshot from its own cited inputs
(Polymarket quotes through `core.quote_polymarket`, Valve rows through `vrs.expected` +
`vrs.calibrated`), checks that every blank percentage carries a published reason, checks that no row
publishes a crowd vote, and cross-checks every HLTV citation in `data/identities.json` against a
table of what those ids actually serve. It is the check that would have caught §6.3 at merge time.

**Why `continue-on-error`:** it is advisory by design. It currently emits four warnings about
another session's prose, and gating publication on prose would be the wrong trade.

**Safe because:** it writes nothing, publishes nothing, and needs no network beyond what the runner
already has — it replays from the vendored Valve file and the committed receipts. It runs in this
session's own harvest workflow today
([`.github/workflows/harvest-4901f43e.yml`](../../.github/workflows/harvest-4901f43e.yml)), so the
request is only about running it on the publishing path too.

---

## 5. URGENT — `main` is red on `unittest discover -s tests`, which blocks every future publication

**Claimed by:** sessions `76712ccc`, `e0fd5a32`, `f4e34907`, `d6df5beb` (the six failing tests) and
`1395f539` (`scripts/publish_root_fallback.py`, the commit that broke them).

**Diagnosis, reproduction and a suggested minimal fix per test:**
[`verification-4901f43e/MAIN-SUITE-BLOCKER.md`](../../verification-4901f43e/MAIN-SUITE-BLOCKER.md).
Summary: `ac5c816` is green, `c55b4b0` is red — 582 tests, **4 failures and 2 errors**, all in four
other sessions' files, reproduced in a pristine `git worktree` on `origin/main` so none of this
session's files are involved.

**What is asked:** bring those six tests back to green, or move their historical assertions onto
frozen receipts. Until then the first hard gate in `.github/workflows/pages.yml` fails, so **no
artifact is uploaded and the `deploy` job never runs** — the board stops refreshing and goes stale at
its own eight-hour limit, after which `assets/app.js` withholds every pick.

**What is explicitly *not* asked:** do not add `continue-on-error` to the test step. That would
restore publishing by deleting the only check that keeps broken data off the site, and it would hide
the four real content regressions listed in the blocker file.

**Safe because:** this session touched none of the six tests, none of the data they read, and no
workflow file. It only measured, wrote it down, and flagged it on the shared board.

---

## Not requested

- **`data/vrs/` refresh.** HLTV's live VRS mirror is newer than Valve's `2026-10-05` file (Zetta
  mirror 368 vs Valve #357; Ground Zero #128 / Off Chops #130 vs Valve #136 / #119). The repository
  is right to use Valve's own file: it is the official source and its rows are citable. PR #115
  already flagged the divergence, so no request is filed.
- **`data/book-receipts.json` `superseded_by`.** This session drafted a request about the three new
  `rejected_listings` entries omitting that field and withdrew it: 24 of 25 entries omit it. The new
  entries follow the file's convention. Recorded in `REPORT.md` §6.5.
- **`scripts/hltv.py` / `scripts/refresh.py`.** The `fallback_lineups()` path added in PR #121 was
  read line by line and behaves as documented: it only supplies lineups when live
  `hltv_context.lineups` is empty, requires an exact `fixture_id` match, requires
  `orientation(fixture, teams, start)` to succeed, requires exactly two teams each with players, and
  requires `source` to start with `https://www.hltv.org/matches/`. It never overrides a live read and
  never invents a probability. No change requested.
