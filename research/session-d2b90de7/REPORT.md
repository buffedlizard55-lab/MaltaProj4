# Session d2b90de7 — report (2026-10-24)

Branch: `arena/d2b90de7-maltaproj4` (Arena-fixed), based on `5d56f35` == `origin/main` at claim time;
re-played onto `dce494b` (post-#245) at ~06:35Z, `afaa07a` (post-#251/#258/#260) at ~07:00Z,
`7be8660` (post-#257/#261/#263) at ~07:20Z, `d0faf73` (post-#267) at ~07:45Z `232d196`
(post-#270) at ~08:00Z, `ef7c213` (post-#259) at ~08:15Z and `59679c2` (post-#269) at
~08:30Z as concurrent sessions merged.
Claim: COORDINATION.md, 2026-10-24 05:40 UTC.

Status: **complete** — freeze measured and root-caused; full capture taken and verified line by line;
TWO post-merge RED states of main's unit gate found in the sandbox (row 1083121 alias refusal +
stale root CSS at `dce494b`, repaired by PRs #251/#260; hardened-verifier vs synthetic-fixture
collision at `7be8660`, repaired by PR #267 concurrently with this session's prepared takeover,
which was withdrawn); every competing repair edit dropped at integration in favour of merged work;
all gates green on the final integrated tree; receipts in COORDINATION.md and PR
[#252](https://github.com/buffedlizard55-lab/MaltaProj4/pull/252).

## 1. P0 measured at claim: publication frozen ~18h, every scheduled run dead at the unit step

- Live public receipt read 05:30Z (`https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json`):
  revision `92d248d2e5193e533aa3e6345384946ec14a1462`, `built_at 2026-10-23T11:47:19.761843Z`,
  `snapshot_generated_at 2026-10-23T11:47:19.504519Z`, 90 rows. `stale_after_hours` is 8 →
  the live executive summary renders "**Snapshot expired or timestamp unverified.** Current picks
  are withheld" (read 05:33Z, quoted in §5).
- Schedule runs of *Verify, refresh and publish CS2 Scout* on main since the last success
  (push run 39947383151, 11:37Z): **39956197341** (12:49:03Z), **39998307424** (17:50:02Z),
  **40025828846** (21:18:45Z), **40042111432** (23:53:03Z), **40062143026** (04:23:24Z) —
  all `failure`, all under 60s, all at step *Unit and independent failure-mode tests*.
  (GitHub delivered only these five of ~70 cron slots in the window — the documented
  schedule-delivery flakiness; the watchdog's dispatches are budget-limited and also could not
  repair a unit-step failure.)
- Local reproduction in the sandbox (`.venv`, requirements.txt + pytest): `python -m unittest
  discover -s tests` → **Ran 1195 tests, FAILED (failures=1, errors=1, skipped=3)**. Both in
  `tests/test_session_0cc1138a.py::LiveHotspawnCoverage`:
  - `test_snapshot_covers_the_observed_lobby_fixtures`: `AssertionError: '1081148' '1079655' :
    lobby fixture missing from the board`
  - `test_each_observed_fixture_is_published_with_a_pick_and_an_official_link`:
    `KeyError: '1081148'`

### Root cause (verified against the committed snapshot, not assumed)

The class pins the 30 fixture IDs rendered open on `https://play.hotspawn.com/lobby` at
2026-10-23 09:44Z. The committed snapshot (`data/latest.json`, generated 11:47:19Z) retains 90
rows and 90 raw `fixture_evidence` records; the ID sets are equal; **neither contains `1081148`
or `1079655`** — the Hotspawn feed itself rotated both out. The b6e37c61 repair excused
feed-removed IDs via `inventory_changes.removed_ids`, but that field is a diff against the
*immediately previous* snapshot only: at 11:47Z it compares with 11:25:13Z, by which time both
fixtures were already gone, so `removed_ids == []` and the excuse no longer fired. Same deadlock
class as the two 2026-10-23 repairs; a hand-maintained diff key re-deadlocks at every rotation.

### Repair (takeover under the 60-minute rule; owner 0cc1138a's last receipt 2026-10-23 11:05Z)

`LiveHotspawnCoverage.board_gap(snapshot, observed)` now derives the excuse from the snapshot's
**own retained raw feed evidence**: an observed fixture is excused only when the feed record list
the snapshot itself kept (`fixture_evidence`, always emitted by `scripts/refresh.py` line ~581) no
longer contains it. Teeth kept: a fixture the feed still returns but the board dropped remains a
hard failure (regression `test_a_row_the_feed_still_returns_can_never_be_excused`). Snapshots that
predate retained feed evidence fall back to the previous `removed_ids` rule
(`test_legacy_snapshot_without_feed_evidence_falls_back_to_removed_ids`). No published value is
changed (`test_repair_changes_no_published_row_field`). 11 regressions in
`tests/test_session_d2b90de7.py`; commit `7278d39`.

Local gates after the repair (all green, measured in-sandbox):
- `python -m unittest discover -s tests` → **Ran 1206 tests, OK (skipped=3)**
- `python -m unittest discover -s audits -p 'test_*.py'` → 9 OK
- `python verification-95b588c2/test_integrity.py` → 5 OK
- `python -m unittest discover -s verification-c6 -p 'test_*.py'` → 12 OK
- `python -m scripts.validate --data data/latest.json --site .` → exit 0 (15 pages, 810
  links/assets, 20 checksums, 212 displayed rows)

## 2. Fresh capture

- Live lobby read from this session at ~05:28–05:32Z: 88 CS2 facet entries (B 43 / C 45),
  **25 open cards** rendered; full fixture-by-fixture table with official URLs in
  `research/session-d2b90de7/lobby-read-2026-10-24T0530Z.md`. Crowd-vote percentages recorded as
  refused context only, per policy.
- Runner capture: `.github/workflows/harvest-d2b90de7.yml` (non-publishing), run
  [40067605793](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40067605793),
  evidence committed under `research/harvest-d2b90de7/` (refresh + quarantine + coverage report +
  unresolved-row probe + independent C6 row audit + audit_9b97d585 ledger + build/validate + all
  eight browser suites against the fresh candidate).

## 3. Fresh capture result and line-by-line verification (2026-10-24)

Runner capture [40067605793](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40067605793)
(all steps green): snapshot **2026-10-24T05:57:43Z**, fixture evidence **05:54:04Z**.
Coverage `verified`, API/page/lobby/retained parity **88 / 88 / 88 / 88**, quarantine withheld **0**
rows, independent C6 row audit **0 failures**, `audit_9b97d585` ledger `coverage_complete: true` with
**0 integrity failures**, unresolved-row probe found **0 rows to probe**.

**25 open · 25 picks · 25 win probabilities · 0 unresolved.** Method mix: 12 `exchange` (Polymarket
strict), 2 `exchange_wide` (labelled low precision: Metizport–BakS 70.5%, Ground Zero–Off Chops
73.0%), 2 `bookmaker_fallback` (Thunderpick odds via BO3.gg's dated listings), 7 `model_vrs`
(originated from Valve's official standings), 2 `model_vrs_mirror` (HLTV's dated 2026-10-24 view of
the Valve ranking, used only where Valve's monthly file cannot resolve a club).

Independent checks performed by this session (not copied from the runner):

1. **Open-set parity against my own lobby read.** The 25 open fixture IDs of the snapshot equal the
   25 cards I rendered from `https://play.hotspawn.com/lobby` at 05:28–05:32Z, 1:1, both directions
   empty (§ table in `lobby-read-2026-10-24T0530Z.md`). Crowd-vote percentages were recorded as
   refused context only.
2. **C6 replay in the sandbox.** `verification-c6/audit_snapshot.py` on
   `research/harvest-d2b90de7/refresh-snapshot.json`: **0 failures**.
3. **Second independent re-deriver.** `research/session-0cc1138a/verify_0cc1138a.py` (shares no code
   with the pipeline): **25 rows checked · 25 re-derived · 0 failures** — after this session added
   the missing additive `model_vrs_mirror` branch (§4).
4. **Valve standings authenticity.** `data/vrs/standings_global_2026_10_05.md` is byte-identical to
   Valve's pinned-commit file (both sha256 `df96e7fc3cd91a2687ec08cac0128e50cc4e4e55346581679572e881d79ae61b`,
   fetched via `api.github.com` from `ValveSoftware/counter-strike_regional_standings@eec4853d…`).
5. **Live exchange spot-check.** Polymarket market `6075573` re-read at ~06:04Z via the Gamma API:
   moneyline, outcomes `["Acend","FORZE Reload"]`, `gameStartTime 2026-10-24 08:00:00+00` (equals the
   Hotspawn feed start), `acceptingOrders: true`, prices now `0.315/0.685` vs `0.325/0.675` observed
   at 05:54:08Z — normal drift, same direction, pick (FORZE Reload) unchanged.
6. **Live book spot-checks (bo3.gg).** NEXVOID vs Alter Ego page shows **1.60 / 2.17**; de-vig
   `q=0.625+0.460829=1.085829` → **57.56% / 42.44%**, exactly the published row. FlyQuest vs Staqued
   page shows **1.001 / 12** (Thunderpick); de-vig `1.082334` → **92.30% / 7.70%**, exactly the
   published row. Both pages name the same fixture, tournament (DFRAG Invitational 2026) and Bo3.
7. **Live HLTV mirror spot-check.** `https://www.hltv.org/valve-ranking/teams/2026/october/24`
   ("Valve global ranking on October 24th, 2026") read live: **#102 Spirit Academy — 1030 Valve
   points** (roster VILBy, Kiryasoo, Netrix, s1nside, k0gaSs) and **#151 LFO 10 — 819 Valve points**
   (roster dottie, flaw, Sapec, Mann3n, L00m1), both exactly as stored on the row evidence. Valve's
   October-05 file genuinely lacks LFO 10 (only LFO 7/8/9) and lists ex-RUSTEC twice — the documented
   reasons the originated-model tier refused and the labelled mirror tier answered.
8. **Arithmetic re-derivation by hand** for both mirror rows: Glicko `g(rd 75)=0.97254`,
   `E(1030,819)=0.765236` → calibrated `0.711817` ✓; `E(1141,1074)=0.592715` → `0.574042` ✓.

**Unresolved-row research pass: nothing to resolve.** The probe step found 0 open rows without a
probability, so the HLTV-first / esportsbooks fallback ladder had no subject this cycle. The ladder
itself remains implemented and exercised by the suite; two rows the *previous* board could not price
(FlyQuest–Staqued, and the FORZE Reload–ex-RUSTEC ambiguity) are now priced from dated, replayable
external evidence rather than invented numbers.

## 4. Concurrent-repair integration (supersession log)

While this session's capture and verification were running, four other sessions repaired the same
deadlock — and the second-order RED it left behind — and merged first:

- **cb16f548 — [PR #245](https://github.com/buffedlizard55-lab/MaltaProj4/pull/245), merged to main
  2026-10-24 06:20:45Z**: `LiveHotspawnCoverage` now asserts parity on an *archived same-instant
  observation* with rotation guards (a fully rotated board cannot break the gate; a still-future
  fixture that vanishes is still reported), and staged a newer board — snapshot
  **2026-10-24T06:19:43Z**, parity 92/92/92/92, **31 open · 31 picks · 31 probabilities**
  (16 exchange, 3 wide, 3 book listings, 6 originated VRS, 3 labelled HLTV-mirror VRS).
- **d2a55add (inside the same integration)**: additive `model_vrs_mirror` branch in
  `research/session-0cc1138a/verify_0cc1138a.py`, and the freshness strip's literal `'23 Oct'` pin
  in `tests/test_session_f89bb1f8.py` derived from the row's own start via the builder's formatter.
- **174afa4f — PRs #251/#258**: claimed the same second-order P0 this session had found ("main's
  unit gate is red at dce494b — publisher rollback + verifier alias gap"): the board's new row
  `1083121` (Hotspawn *Projeto do KinGui* vs Polymarket outcome *Tropa do KinGui*) was refused by
  the strict re-deriver despite the sourced alias record session 9f3e77d2 stored on the evidence
  (HLTV match 2399904 fixture parity + Valve roster continuity, 22 Oct), and the legacy root
  `assets/style.css` was stale against `site/assets/style.css`. PR #251's verifier maps reviewed
  identity aliases from the evidence (`alias_groups`) and regenerated the root on the 06:19Z board,
  repairing both.
- **a30d31a0 — PR #260**: the root fallback now refuses builds made from older source
  (`source_drift`) and makes its in-step gates fatal.
- **ea2e254c — PR #257**: semantic tall-phone CSS pins and the sourced-alias regression tests for
  row `1083121`.
- **cecfe864 — PRs #261/#263**: `alias_groups` hardened to dual registration (evidence record needs
  an https source AND a written basis, and the committed `data/identities.json` registry must name
  the same labels), pages.yml root-fallback replay hardening, and a 31-open board line-by-line
  ledger. Merging #257's tests with #263's hardening left main `7be8660` RED again in its own unit
  gate (the synthetic fixture in `test_session_ea2e254c.py` predates the hardening and lacks the
  `basis` field).
- **4ed657ce — PR #267**: resolved that alias-gate deadlock (row receipt plus committed register,
  adopting the full dual-registration contract), updated the synthetic fixtures, added an
  independent `scripts/verify_4ed657ce.py` re-deriver and rebuilt the root fallback. This session
  had measured the same failure on pristine `7be8660` and prepared a dated takeover supplying the
  `basis` fixture field; #267 shipped first, so the takeover was **withdrawn** — this PR ships no
  shared-test edits at all.

This session had independently developed its own deadlock repair (excuse derived from the snapshot's
retained raw `fixture_evidence` — a fixture the feed still returned could never be excused — with
11 regressions), staged its own 05:57Z board, and — after measuring pristine `dce494b` RED in the
sandbox (3 failures + 1 error in `tests/test_session_0cc1138a.py`) — its own equivalents of the two
second-order repairs (`alias_teams()` in the verifier, root rebuild/re-stage propagating d2a55add's
CSS fix). At integration, **all competing edits to the shared files** (`tests/test_session_0cc1138a.py`,
`verify_0cc1138a.py`, `tests/test_session_f89bb1f8.py`, `data/latest.json` and the generated pages)
were **dropped in favour of the merged repairs and the newer board** rather than layered over another
session's work; the repairs address the same measured failures and ship with their owners' guard
tests. Nothing of the other sessions' work was discarded. What this session keeps on main is its
unique evidence and its offline invariants:

| Retained artifact | Content |
| --- | --- |
| `.github/workflows/harvest-d2b90de7.yml` | the non-publishing capture workflow (`[capture]` branch trigger) |
| `research/harvest-d2b90de7/**` | run receipts, refresh snapshot, all gate logs, audits, coverage report, browser log, quarantine log |
| `research/session-d2b90de7/lobby-read-2026-10-24T0530Z.md` | this session's independent lobby read at 05:28–05:32Z, 25-row open table with vote/refusal annotations |
| `research/session-d2b90de7/REPORT.md` | this report |
| `tests/test_session_d2b90de7.py` | offline invariants: receipt consistency, lobby-read ↔ snapshot 1:1, every published probability re-derived from stored evidence with arithmetic written in the test file only, alias-record acceptance/refusal, both dated notes published |
| `data/review-notes.json` | the two dated notes (union-merged with main's; no note removed) |

## 5. Executive summary, unresolved section and phone verification

Measured on this session's staged 05:57Z candidate (superseded by main's 06:19Z board — every gate
below re-passed on the integrated tree, §6, including all nine browser suites): `index.html` links `picks.html`, `unresolved.html`,
`matches.html`, `#picks-at-a-glance`, `#unresolved-summary` and carries the `#unresolved-limits`
section (rendered even at 0 unresolved, per the standing contract); `matches.html#feed-scope` reads
"63 of 88 feed rows are past fixtures"; the completeness sentence agrees with the runtime counters
(browser suite `browser_f0814674` checks prose/counter agreement fresh and 8h-stale). Phone gates:
all 8 browser suites pass on the staged build, including first-pick-and-both-probabilities inside
the first screen at 320/390px, placement above the 320×568 tab bar (`browser_9b97d585`), no
horizontal overflow at 320/390/768/1440 and WCAG 2 AA axe scans on all 8 pages × 4 viewports
(`browser.cjs`, 32 scans).

## 6. Integration gates

**On this session's staged 05:57Z candidate (history):** 1206 unit OK (1 skipped) · audits 9 OK ·
integrity 5 OK · C6 12 OK · validator exit 0 (88 rows, 25 reproduced calculations, 15 pages, 813
links/assets, 20 checksums, 216 displayed rows) · 8/8 browser suites · staging via the publisher's
own path (`scripts.build` → `scripts.publish_root_fallback`, `"publish": true … 2026-10-24T05:57:43Z
replaces 2026-10-23T11:47:19Z"`). This staging was withdrawn at integration in favour of PR #245's
newer board (§4).

**On the exact integrated tree shipped in PR #252** (main `59679c2` + this session's evidence,
docs, notes union and the regenerated review stage; no shared-test edits):

- Measured on the way here: pristine `dce494b` (PR #245's merge) failed its own unit gate —
  3 failures + 1 error in `tests/test_session_0cc1138a.py`. Row `1083121` (*Projeto do KinGui* vs
  Polymarket outcome *Tropa do KinGui*, alias recorded on the evidence by session 9f3e77d2 on
  22 Oct from HLTV match 2399904 fixture parity + Valve roster continuity) was refused by the
  strict re-deriver, and the legacy root `assets/style.css` was stale against
  `site/assets/style.css` (d2a55add's unclosed-`@media` repair never propagated; the
  both-copies test failed) — the next scheduled run would have deadlocked again. Sessions
  174afa4f (PR #251: verifier `alias_groups` mapping + root regeneration) and a30d31a0 (PR #260:
  publisher source-drift refusal) shipped those repairs first; this session's concurrent
  equivalents were withdrawn at integration (§4), and it keeps the offline regressions
  (`StoredIdentityAliasesAreHonoredNotGuessed`: the recorded alias reproduces the published price;
  stripping or guessing the record still raises).
- Second measured RED, one hour later: pristine `7be8660` (merge of PR #263 over PR #257) failed
  `tests/test_session_ea2e254c.py::test_alias_groups_keep_only_https_sourced_groups` — cecfe864's
  hardened `alias_groups` requires a written `basis` (plus committed-registry dual registration)
  that ea2e254c's synthetic fixture predates. This session prepared a dated takeover; PR #267
  (4ed657ce) shipped the repair first and the takeover was withdrawn (published board unaffected
  throughout — real evidence carries source and basis; verify standalone 31/31 on every tree).
- `python -m unittest discover -s tests` → **1345 OK (1 skipped)**
- `python -m unittest discover -s audits -p 'test_*.py'` → **9 OK**
- `python verification-95b588c2/test_integrity.py` → **5 OK**
- `python -m unittest discover -s verification-c6 -p 'test_*.py'` → **12 OK**
- `research/session-0cc1138a/verify_0cc1138a.py` standalone on the committed board → **31 rows
  checked · 31 re-derived · 0 failures**
- `python -m scripts.validate --data data/latest.json --site .` → exit 0: **92 rows, 31 reproduced
  probability calculations, 15 pages, 878 internal links/assets, 20 artifact checksums, 234
  displayed match rows**
- `npm run test:browser` → **9/9 suites pass** (PR #245 added `browser_cb16f548.cjs`)
- Root regeneration is note-driven only: `review.html` renders the 187-note union and
  `build-info.json`/`data/matches.csv` carry the new build receipt; every other staged byte equals
  main's regeneration, and no price, pick or probability changed.

Two additive `data/review-notes.json` entries (union-merged, no note removed):
`session-d2b90de7-publish-deadlock-2026-10-24` (outage record, supersession and merged-repair
provenance) and `session-d2b90de7-coverage-measurement-2026-10-24` (this capture's coverage, method
mix, live spot-checks and remaining source limitations: GG.BET 403, Thunderpick direct-adapter
limit, Pinnacle absence, 63 past-dated rows never priced).

## 7. PR / merge / deploy receipt

- PR: [#252](https://github.com/buffedlizard55-lab/MaltaProj4/pull/252) (`arena/d2b90de7-maltaproj4`
  → `main`). The first head (staged 05:57Z board + competing repairs) was withdrawn and re-played
  onto `dce494b`, then `afaa07a`, then `7be8660`, then `d0faf73`, then `232d196`, then `ef7c213`, then `59679c2` as PRs
  #245/#246/#251/#257/#258/#259/#260/#261/#263/#267/#269/#270 merged (§4); the final head carries only this
  session's evidence, offline invariant suite, notes union, docs and the note-driven review-stage
  regeneration — no shared-test edits.
- Merge commit, publish run and live-byte verification: appended to COORDINATION.md in the
  follow-up receipt commit once `main` deploys.
