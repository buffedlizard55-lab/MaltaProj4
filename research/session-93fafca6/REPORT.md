# Session 93fafca6 — independent audit of what the live site actually serves

Date: 2026-10-21, 20:20–21:20 UTC. Branch: `arena/93fafca6-maltaproj4`.
Non-publishing research harvest: run
[39673372308](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39673372308) (success; every step's
real exit status is committed under `research/harvest-93fafca6/logs/`).

Every other gate in this repository inspects a build the repository produced: `scripts/validate.py` and
`verification-c6/audit_snapshot.py` read the local `public/` tree, the browser suite drives a local server, and
`scripts/verify_live.py` polls the live site only *inside* the deploy job that just published it. This session adds
the missing layer — an audit of the **deployed bytes as delivered**, at an arbitrary moment, paired with a
same-minute real refresh — and uses it to measure the one publication defect that prior sessions could only
predict.

Scope discipline: five other sessions held live claims when this one started (`2d0a85f2`, `1395f539`, `96ea1af8`,
`bf09aa40`, `db1f35c5`), between them owning `scripts/{build,core,refresh,hltv,validate,vrs,books}.py`,
`site/assets/*`, the root staged `*.html`, `README.md`, `data/{identities,book-receipts,review-notes}.json` and
`.github/workflows/pages.yml`. This session edited **none** of them. The four open gap fixtures (`1081597`,
`1082837`, `1082858`, `1082860`) were already claimed twice over, so they were not re-researched here; they were
audited. Everything below is new files in this session's own scope.

---

## 1. What a phone visitor was actually served (verified live, 20:51:37Z)

Live receipt read cache-busted from
[build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json): revision `884f36eb`, built
`2026-10-21T20:47:31Z`, snapshot `2026-10-21T20:47:30.973488Z`, **75 rows**, 20 files in the manifest.
Full report: [`research/harvest-93fafca6/LIVE-AUDIT.md`](../harvest-93fafca6/LIVE-AUDIT.md) — **13 pass, 3 info,
0 warn, 0 fail**.

| Check | Result | What it proves |
| --- | --- | --- |
| `manifest-consistency` | PASS | all 20 served files are byte-identical to the served manifest's own SHA-256 — no torn or mixed deployment |
| `core-routes-available` | PASS | every page a phone navigates between answered 200 |
| `summary-links` | PASS | the executive summary links, inside the site, to `picks.html`, `unresolved.html`, `matches.html`, `analysis.html`, `review.html`, `sources.html`, `evidence.html`, plus the labelled "Where the picks are" shortcut nav |
| `summary-anchors` | PASS | `#freshness-strip`, `#picks-at-a-glance`, `#unresolved-summary` exist and `#pick-limitations` is nested **inside** the summary |
| `glance-completeness-live` | PASS | the 13 open fixtures in the page's own `#coverage-data` are exactly the 13 rows in the at-a-glance list |
| `glance-completeness-fresh` | PASS | every fixture a same-minute refresh (20:51:36Z) calls open is on the live board |
| `pick-coverage` | PASS | every open fixture has a pick, and the block states "Every open match currently carries a pick" |
| `probability-not-from-hotspawn` | PASS | all 11 priced rows carry at least one non-Hotspawn primary-source link (Hotspawn is inventory only) |
| `freshness-copy-honest` | PASS | the strip's claim matches the served snapshot's age, and the client-side expiry hook ships |
| `mobile-markers` | PASS | device-width viewport on all 10 pages; persistent `.mobile-tabs` bar; `@media(max-width:650px)`; tab tap target **60px**, evidence-link tap target **44px**; tables collapse to cards (`table{min-width:0;display:block}`) instead of forcing a horizontal scroll |
| `external-evidence-reachable` | PASS | **6 distinct primary-source URLs behind the open rows re-requested; 6 answered 200**; none access-limited |

Open board as served (from the live page's own `#coverage-data`, 13 rows):

| Fixture | Start (UTC) | Live state |
| --- | --- | --- |
| 1082837 Zetta vs LOS NINOS | 21 Oct 22:00 | priced |
| 1081870 Vitalem Aerem vs Rare Atom | 22 Oct 05:00 | priced (wide market line, low confidence) |
| **1081597 benched gods vs TitanFlow** | 22 Oct 11:00 | **research-only pick, no percentage** ("Research only · Valve listing") |
| 1081600 Donstu vs Banda chuya | 22 Oct 13:45 | priced (model) |
| 1082688 Imperial vs Turma do Pagode | 22 Oct 14:00 | priced |
| 1082689 BESTIA vs ShindeN | 22 Oct 14:00 | priced |
| 1082882 UNiTY vs Apogee Betclic | 22 Oct 14:00 | priced |
| 1082858 Ground Zero vs Off Chops | 26 Oct 03:00 | priced (model) |
| 1082859 NEXVOID vs Alter Ego | 26 Oct 03:00 | priced (model) |
| **1082860 FlyQuest vs Staqued** | 27 Oct 03:00 | **research-only pick, no percentage** ("Research only · one ranking") |
| 1082861 Rooster vs Abyssal | 27 Oct 03:00 | priced (model) |
| 1082792 HOTU vs The Huns | 31 Oct 09:00 | priced (model) |
| 1082793 5star vs 1WIN | 31 Oct 13:00 | priced (model) |

Methods on the live board: `exchange` 4, `exchange_wide` 1, `model_vrs` 6, `research_rank_single` 1,
`research_vrs_single` 1 — i.e. **13 of 13 open fixtures carry a pick and 11 of 13 carry a published probability**.
The two that do not publish a number say so on the page, name the reason, and link their sources (Hotspawn ↗,
Evidence & lines, Valve standings ↗). That is the brief's "separate section for unresolved picks and the
limitations", verified as delivered rather than as designed.

### 1.1 Why this session's own refresh disagrees with the live board (and why that is not a defect)

The paired refresh this branch ran at 20:48–20:51Z
([`logs/refresh.txt`](../harvest-93fafca6/logs/refresh.txt), exit 0) reported 75 rows, `coverage: verified`,
13 open, **12** picks, **9** probabilities and **1** fixture without a pick (`1081597`); the live board built at
20:47:31Z reported 13 picks and 11 probabilities. The cause is the code version, not the data: this branch is
`63f4172` plus new files, while the live artifact was built from `884f36e`, which had already merged other
sessions' work resolving `1081597` through the one-sided Valve-standings tier and pricing `1082837` and `1082858`.
Both readings are recorded; neither is smoothed over. This is precisely why the audit pairs live bytes with a
same-minute refresh instead of trusting one of them.

---

## 2. The dual-publisher race — measured, not predicted

GitHub Pages is configured `build_type: legacy`, `source: main:/`
([GET /repos/buffedlizard55-lab/MaltaProj4/pages](https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages)),
so **two** publishers write to one URL: `pages.yml`'s verified artifact via `actions/deploy-pages`, and GitHub's own
legacy builder publishing the **committed root** of `main`. The committed root is the 2026-10-18 bootstrap
(revision `88b1b2c3`, 98 rows). Whichever publisher lands last is what a visitor reads.

Observed directly this session, from two cache-busted reads of the same URL plus the Pages build API
([`PUBLICATION-STATE.md`](../harvest-93fafca6/PUBLICATION-STATE.md),
[`publication-state.json`](../harvest-93fafca6/publication-state.json)):

| Time (UTC) | Live `build-info.json` said | Cause |
| --- | --- | --- |
| ~20:11 | revision `47f230b`, built `2026-10-21T19:57:45Z`, **76 rows** | verified artifact |
| 20:12:40 | — | legacy Pages build for `63f4172` completed ([builds API](https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages/builds)) |
| ~20:15 | revision `88b1b2c3`, built **`2026-10-18T00:52:19Z`**, **98 rows** | **the legacy root fallback had overwritten the artifact** |
| 20:20:28 | — | `pages.yml` run [39668307571](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39668307571) finished deploying (verify-build ✓, deploy ✓) |
| ~20:21 onward | fresh artifact again | restored |

Stale window: **≈8 minutes**, during which the live board was a 3.8-day-old snapshot with every pick expired. The
site was honest about it — the deployed strip read *"Snapshot is older than 8 hours: every percentage below is
expired and must not be used as a current pick"* — but a visitor in that window saw June-dated rows and October-18
matches instead of the current board.

Two further irregularities appeared in the same API while measuring:

* Legacy Pages builds for `884f36e` (20:35:17Z) and `5071cad` (20:46:37Z) both finished **`errored`**, and
  `GET /pages` reported `status: "errored"` at 20:48:00Z. The next legacy build (`179789e`, 20:47:50Z, duration
  165.51 s) succeeded and the site status returned to `built` by ~21:00Z. This is the same collision shape recorded
  as `concurrent-pages-deploy-failure-2026-10-16`: two builders writing one site at once. No cause is asserted
  beyond the API's own statuses.
* The live site can therefore be in three different states within ten minutes of the same push: fresh artifact,
  stale root fallback, or mid-build.

### 2.1 The owner-level fix is refused for both token types — now with readable evidence

Prior sessions recommended one settings change and recorded that they could not make it; session c4d25599's
`pages: write`-scoped attempt (run [38706399874](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38706399874))
failed in 3 s and its log is not readable from this sandbox (the Actions log host is unreachable), so the verdict
was never on the record. This session reproduced the attempt twice and committed both responses:

| Attempt | Verdict | Evidence |
| --- | --- | --- |
| Arena integration token (`gh auth status`: `buffedlizard55-lab`, `X-Oauth-Scopes:` empty), 20:20:18Z | **HTTP 403**, `Resource not accessible by integration`, `X-Accepted-Github-Permissions: pages=write,administration=write`, request id `C962:306C0:544D9:8CACF:6AD91E81` | [`research/session-93fafca6/publication-state.json`](publication-state.json) |
| `GITHUB_TOKEN` with **explicit `pages: write`** in [`harvest-93fafca6.yml`](../../.github/workflows/harvest-93fafca6.yml), 20:48:00Z | **HTTP 403**, same body, request id `780B:1EA56B:F5241B:31FA96A:6AD92502` | [`research/harvest-93fafca6/publication-state.json`](../harvest-93fafca6/publication-state.json) |

**The single outstanding action, for the repository owner (one click, no code change):**
Settings → Pages → Build and deployment → **Source → GitHub Actions**. `pages.yml`'s deploy job already uses
`actions/deploy-pages@v5.0.1` with `pages: write` + `id-token: write` and verifies the served bytes, so workflow
mode needs nothing else; it simply stops the legacy builder from republishing the committed root. Until then the
race is bounded by the next `pages.yml` run (≈8 minutes observed, four scheduled slots an hour at :04/:19/:34/:49
plus a 10-minute watchdog), and the site states its own staleness rather than hiding it.

### 2.2 The same race, observed a second time after this PR's own merge — with the mechanism visible

The measurement was repeated independently after the merge, from a runner with normal egress
([`research/harvest-93fafca6/`](../harvest-93fafca6/) as re-harvested by run
[39677114815](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39677114815)), and it caught the
defect in the act:

| Time (UTC) | Reading | Source |
| --- | --- | --- |
| 21:10:18 | artifact for merge commit `fcaf608` built, 75 rows | `pages.yml` run [39675647149](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39675647149), success ~21:12:00Z |
| ~21:14 | live receipt = `fcaf608`, built `21:10:18Z`, 75 rows — the artifact is serving | direct read of [build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) |
| **21:14:24** | live receipt = **`88b1b2c3`**, built **`2026-10-18T00:52:19Z`**, **98 rows**, 92.37 h old; recorder verdict **`committed-root-fallback`**; Pages site status `building` | [`PUBLICATION-STATE.md`](../harvest-93fafca6/PUBLICATION-STATE.md) |
| **21:17:59** | live audit: **11 pass, 2 info, 1 warn, 2 fail** — `live-board-fresh` FAIL (92.43 h), `publisher-identity` WARN (legacy publisher named), `glance-completeness-fresh` FAIL (13 fixtures open now with no row on the served board, named in the report) | [`LIVE-AUDIT.md`](../harvest-93fafca6/LIVE-AUDIT.md) |

Two reads of the same URL **30 seconds apart** returned two different boards. The auditor was right both times:
it passed at 20:51:37Z on the fresh artifact and failed at 21:17:59Z on the stale fallback, which is what a
check that only ever passes would never have shown.

**The mechanism is now visible in the API, and it is worse than a coin flip.** During a burst of merges the legacy
builder is never gated, never cancelled and never verified, while artifact deploys can simply not happen:

* Legacy Pages builds completed `built` for **every** push to `main` in the window: 21:03:38Z `fcaf608`,
  21:10:55Z `b1adaa4`, 21:11:31Z `87db124`, 21:14:07Z `47c1b9d`, 21:16:45Z `7148716`
  ([builds API](https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages/builds)). Each one republishes the
  committed root, i.e. the 2026-10-18 board.
* Two `pages.yml` runs on `main` concluded **`cancelled` with zero jobs created and `cancel_actor: null`**:
  [39676669813](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39676669813) (`b1adaa4`, created
  21:10:57Z, updated 21:11:34Z) and [39677102451](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39677102451)
  (`47c1b9d`, created 21:14:08Z, updated 21:16:48Z). Those pushes never deployed an artifact at all, so the legacy
  build that landed seconds earlier was never overwritten.
* `pages.yml` sets `concurrency: {group: cs2-scout-${{ github.ref }}, cancel-in-progress: false}`, so the
  cancellations did not come from that setting. **Why GitHub cancelled two queued runs and recorded no actor is not
  established by these readings and is not asserted here.** What is established is the consequence: with four merges
  in seven minutes, the publisher that runs `scripts/verify_live.py` before serving was dropped twice, and the one
  that serves a 3.8-day-old board without any check ran every time.

This is the same shape as the recorded `concurrent-pages-deploy-failure-2026-10-16`, now with the cancelled-run
evidence attached. Two mitigations follow, both outside this session's scope and both logged on the board rather
than applied: the owner-level one-click switch to workflow publishing (irregularity 3 above, which removes the
second publisher entirely), and a `pages.yml` change so a dropped `main` deploy is retried instead of leaving the
last legacy build serving — `pages.yml` is a shared output and belongs to the integration session.

### 2.3 The committed root fallback, audited on its own terms

[`ROOT-FALLBACK-AUDIT.md`](../harvest-93fafca6/ROOT-FALLBACK-AUDIT.md) runs the same auditor over the committed
root bytes (`--offline-dir .`): **10 pass, 2 info, 1 warn, 1 fail**, exit 1. The one failure is
`live-board-fresh` — the fallback's snapshot is 91.36 h old, so if the legacy publisher wins, the served board is
outside its evidence window. The warning names the publisher. Everything else passes, including the honest
freshness copy, so the fallback degrades loudly rather than silently. It is also materially different data: 98 rows
/ 34 "open" (June-dated `scheduled` entries Hotspawn never closed) against the live 75 rows / 13 open.

### 2.4 How the window closed, and what this session could not do itself

The second event was not left to chance: it was measured until it healed.

* `refresh-watchdog.yml` run [39678232871](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39678232871)
  (21:22:18Z, success) dispatched `pages.yml` run
  [39678232770](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39678232770) on `main` for `ac5c816`,
  which completed **success** at 21:29:24Z with *Verify live Pages bytes match this exact build* → success.
  **Stale window ≈18 minutes** (21:11:31Z → 21:29:24Z), against ≈8 minutes for the first event; the difference is
  the three cancelled `main` deploys in between, which removed the earlier recovery opportunities.
* This session could not trigger that heal itself. `gh workflow run pages.yml --ref main` returns
  **HTTP 403 `Resource not accessible by integration`** for the same integration token that is refused the Pages
  setting and cannot dispatch workflows. The watchdog's own dispatch is therefore currently the only automated
  recovery path available to a session — worth knowing, because it means a session can detect a stale site and
  record it but not fix it.

**And the same tool then proved the recovery.** Harvest run
[39679291646](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39679291646) re-read the live site at
**21:33:51Z**: **13 pass, 3 info, 0 warn, 0 fail**, exit 0 — served by a workflow artifact for commit `ac5c8164`,
snapshot 0.10 h old, every one of the 20 manifest files byte-identical, and the paired refresh at 21:33:51Z
reporting `coverage: verified`, 75 matches, **11 priced**, 2 research-only picks and **0 fixtures without any
pick**. Fail on the stale fallback at 21:17:59Z and 21:24:10Z, pass on the restored artifact at 21:33:51Z: the
auditor discriminates in both directions on real bytes, which is the only evidence that its pass means anything.

**Methodological caveat, recorded so nobody repeats the mistake.** At ~21:24Z a page fetch from the authoring
sandbox returned revision `fcaf608` / 75 rows, while a runner's cache-busted read 10 seconds later returned the
stale fallback / 98 rows. The sandbox's fetch path served a cached copy, so a sandbox page fetch is **not**
authoritative for publication state. Every live claim in this report is backed by a committed CI receipt read
cache-busted from a runner, and where a sandbox read is quoted (the ~20:11Z and ~20:15Z pair in §2) it is quoted
because the *change* it showed was later corroborated by the API's build history.

---

## 3. Line-by-line repository review: irregularities flagged

### 3.1 Latent crash path in `scripts/refresh.py::cache_bust` (dormant, one-line fix, claimed file)

`urllib.parse.urlencode` raises `TypeError` when the first element of its sequence is a **list** rather than a
tuple. `cache_bust` builds its pairs with `str.split('=', 1)`, which returns lists:

```python
# scripts/refresh.py:61-68
pairs = [pair.split('=', 1) for pair in parts.query.split('&') if pair]
query = urlencode(pairs + [(CACHE_BUST_ARGUMENT, token)])
```

Reproduced with the repository's own code (`.venv/bin/python`, `scripts.refresh` importable):

```
cache_bust('https://play.hotspawn.com/lobby', 'T1')            -> https://play.hotspawn.com/lobby?_cb=T1
cache_bust('https://play.hotspawn.com/lobby?tenantId=1', 'T1') -> TypeError: not a valid non-string sequence or mapping object
```

*Impact today: none.* `Sources.bustable` cache-busts only HTML on `play.hotspawn.com`
(`https://play.hotspawn.com/cs2-pickems`, `https://play.hotspawn.com/lobby`), and neither URL carries a query, so
`pairs` is empty and `[] + [tuple]` starts with a tuple. It is a crash path for any future cache-busted URL with
arguments — and a refresh crash is the failure mode that costs every open row its lineup, as
`scripts/refresh.py`'s own header documents.

*The correct implementation already exists in this repository*: `scripts/cdn_probe_3c8d1136.py::bust` writes
`[(k, v) for k, v in (pair.split('=', 1) for pair in ...)]` — tuples. `scripts/refresh.py` is claimed by three
active sessions (`2d0a85f2`, `1395f539`, `db1f35c5`), so per the board rules this is logged as a
**cross-session request** in `COORDINATION.md` with the one-line patch rather than edited here. This session's own
copy of the helper (`verification-93fafca6/audit_live.py::cache_bust`) uses tuples and carries a regression test
for the valueless-argument case.

### 3.2 Everything else checked and found sound

* Local gates, all green on this branch: `python -m unittest discover -s tests` → **498 tests OK**; `audits` → 9 OK;
  `verification-95b588c2/test_integrity.py` → 5 OK; `verification-c6` → 12 OK;
  `python -m scripts.validate --data data/latest.json --site .` → 15 pages, **836** internal links/assets, 20
  artifact checksums, 258 displayed rows. This session's own suite → **80 tests OK** locally and in CI
  ([`logs/session-tests.txt`](../harvest-93fafca6/logs/session-tests.txt)).
* The repository's independent row auditor on the fresh snapshot → exit 0
  ([`row-audit.md`](../harvest-93fafca6/row-audit.md)).
* No probability anywhere on the live board is sourced from Hotspawn: all 11 priced rows carry dated external
  evidence, and the six distinct evidence URLs behind the open rows all answered 200 when re-requested from a
  runner with normal egress.
* Nothing in this session wrote to `data/`, `site/`, the root staged pages or `pages.yml`.

---

## 4. What this session added

| Path | Purpose |
| --- | --- |
| [`verification-93fafca6/audit_live.py`](../../verification-93fafca6/audit_live.py) | Independent acceptance audit of the deployed bytes: receipt, publisher identity, per-file manifest hashes, core routes, executive-summary links and anchors, glance completeness (against the page's own rows *and* a same-minute refresh), pick coverage and named limitations, non-Hotspawn probability sourcing, honest freshness copy, phone requirements, opt-in external link reachability. Stdlib only, fail-closed, exit 1 on any `fail`. |
| [`verification-93fafca6/record_publication_state.py`](../../verification-93fafca6/record_publication_state.py) | Reads the Pages configuration, Pages builds, publication run history and live receipt through the API, derives **which publisher is serving**, and re-attempts the owner-level fix recording the exact verdict; re-reads the configuration to prove a successful switch rather than trusting a status code. |
| [`verification-93fafca6/test_audit_live.py`](../../verification-93fafca6/test_audit_live.py), [`test_record_publication_state.py`](../../verification-93fafca6/test_record_publication_state.py) | 80 offline failure-mode tests: every check has a failing fixture *and* a healthy one, so no rule fires on a correct deployment. Includes the torn-deployment, stale-fallback, unnamed-gap, Hotspawn-only-source, small-tap-target and cascaded-CSS cases. |
| [`.github/workflows/harvest-93fafca6.yml`](../../.github/workflows/harvest-93fafca6.yml) | Non-publishing research harvest: real refresh, live audit, root-fallback audit, publication state, row audit, this session's tests, committed receipts with real exit statuses. Never builds `public/`, never deploys. |
| `research/harvest-93fafca6/**` | The dated receipts: `LIVE-AUDIT.md`, `ROOT-FALLBACK-AUDIT.md`, `PUBLICATION-STATE.md`, `publication-state.json`, `harvest-summary.json`, `row-audit.md`, the served `live/index.html` + `live/build-info.json` + `live/live-files.json`, and every step's log and exit status. |
| `research/session-93fafca6/**` | This report, the 20:14Z root-fallback audit, and the 20:42Z publication-state reading taken from the sandbox. |

Two audit behaviours worth calling out because they were found by testing, not assumed:

* **CSS cascade.** The deployed stylesheet declares `.source-links a{min-height:32px}` in one phone block and
  `min-height:44px` in a later one; a phone renders 44px. A first-match reading reports a tap-target failure the
  live site does not have, so the auditor takes the last declared value and a test pins the difference.
* **A truncated evidence list must declare itself.** The first real failure this auditor caught named 10 of the 13
  missing fixtures while its heading counted 13 — accurate, but it read like a complete list. `preview()` now states
  the total and how many are omitted, at all four truncating call sites, with tests pinning both the over-limit
  wording and that an omitted id never appears as though it had been listed.
* **A vacuous pass is a defect too.** At 21:24:10Z the paired refresh itself came back `coverage: stale` with the
  same 98-row board the legacy publisher was serving, so `glance-completeness-fresh` printed PASS — true, and
  meaningless. The check now reports WARN whenever the paired refresh is not `coverage: verified`, names the
  coverage verdict it got, and points at `live-board-fresh` for the real verdict; a snapshot that reports no
  coverage at all still passes, with the omission stated rather than assumed away. Three tests pin the stale,
  verified and long-locked-list cases.
* **A classification is not a claim.** `pages.yml` began re-staging the committed root from the verified build
  during this session (step *Keep the legacy main:/ root fallback on the verified build*), and at 21:52:09Z the
  legacy publisher was serving a root that carried a 0.06 h old verified snapshot — both paths fresh. The recorder
  still printed "the legacy root fallback overwrote the verified artifact", which was a true classification and a
  false claim. `legacy_clause()` now follows the timestamps: stale board, fresh board, or age unreadable each get
  their own wording, `legacy_overwrote_with_a_stale_board` is recorded separately from
  `legacy_overwrite_detected`, and three tests pin the three branches.
* **Render-time vs receipt-time staleness.** `scripts/build.py::fresh_strip` renders against the wall clock at
  render time while the receipt's `built_at` is carried over from the snapshot. Comparing the two is what
  fingerprints the root fallback: a strip that says "older than 8 hours" over a receipt that claims to have been
  built at snapshot time proves the HTML was rendered later than the data it ships.

---

## 5. Verification performed, and what is *not* claimed

Verified: the live receipt and all 20 manifest hashes; the served pages' links, anchors and nesting; the open-row
set against both the page's own index and an independent same-minute refresh; a pick or a named limitation for
every open fixture; a non-Hotspawn primary source behind every published percentage; the reachability of those
sources; the phone markers in the deployed CSS; the Pages configuration and build history through the API; both
403 verdicts; the `cache_bust` `TypeError`; and every local gate listed in §3.2.

**Not claimed:** that any published percentage is a calibrated forecast or that any pick wins; that the legacy
publisher will not overwrite the artifact again (it did, twice during this session, until the owner changes the
setting); **why** GitHub cancelled the two `main` runs with no recorded actor (the effect is evidenced, the cause
is not); that the two `errored` Pages builds have a diagnosed cause (only the API's own statuses are recorded); that the four gap
fixtures are resolved by *this* session (they were claimed and resolved by others — this session audited the
result); or that the 20:51Z coverage numbers are a permanent promise. They are dated observations.
