# Session `3c79a355` — the board was frozen, not wrong

Branch `arena/3c79a355-maltaproj4` · work done 2026-10-24, 05:26–06:20 UTC.

The request was: a pick for **every** Hotspawn CS2 match, extra sources (HLTV, then
esportsbooks and betting lines) for anything the featured picks cannot resolve, a separate
unresolved section with its limitations inside the executive summary, and a board that is
easy to read and find on a phone.

What I found first changed the order of work. **The board had 25 picks and 25 probabilities
on the day of the request; the published site showed none of them.** The site was not
missing a research tier — it was frozen for 18 hours, and once every quote aged past the
eight-hour evidence window the page correctly withdrew every pick and printed
"Snapshot expired or timestamp unverified". Fixing the freeze was the only way to deliver
anything else, so it came first, and every other item is checked against a *fresh* snapshot
rather than against the frozen one.

---

## 1. Measured state before any change

| Fact | Value | How it was read |
| --- | --- | --- |
| Published snapshot | `2026-10-23T11:47:19.504519Z`, 90 rows, 27 open, 27 picks | `data/latest.json` in the checkout, and `build-info.json` (`snapshot_generated_at`) |
| Age of that snapshot at 05:26Z | 17 h 39 m | arithmetic on the two timestamps above |
| Rendered state | "Snapshot expired or timestamp unverified. Current picks are withheld", 0 picks / 0 probabilities / 16 unresolved | Chromium render of the built `index.html`, 390×844 |
| Scheduled publishes | **five consecutive failures**, all on commit `5d56f35` | `GET /actions/workflows/pages.yml/runs`: created 2026-10-23T12:49:03Z, 17:50:02Z, 21:18:45Z, 23:53:03Z, 2026-10-24T04:23:24Z |
| Failing step | *Unit and independent failure-mode tests*, i.e. before refresh/build/deploy | `gh api /repos/.../actions/runs/40062143026/jobs`: steps 1–6 pass, step 7 red, steps 8–15 skipped |
| Watchdog | `stop`: "5 consecutive failed runs on commit 5d56f35e … requires a fix before dispatching again" | replayed `scripts.refresh_watchdog.evaluate` against the live run list and the live receipt |

The last line matters: the watchdog did exactly what it was built to do — refuse to
re-dispatch a red gate — and the escalation issue path did not fire in production
(`sync_escalation` verifies fine with the same token scope, but no issue exists), so the
outage was silent for a day. That is recorded as an open finding below rather than
"fixed" without a measurement.

## 2. Root causes, each reproduced locally before it was changed

`python -m unittest discover -s tests` on the untouched checkout: **`Ran 1195 tests …
FAILED (failures=1, errors=1)`**.

1. **A one-day fixture list was a permanent invariant.**
   `tests/test_session_0cc1138a.LiveHotspawnCoverage` pinned the thirty fixture IDs read
   from `https://play.hotspawn.com/lobby` at 09:44Z on 23 Oct and required every one of
   them to be a row in the *current* snapshot (`row = rows[fixture]`). Hotspawn expires
   fixtures continuously: `1079655` and `1081148` are absent from the 11:47Z snapshot and
   are **not** named in that snapshot's own `inventory_changes.removed_ids` (that field only
   diffs against the immediately preceding snapshot), so the test raised `KeyError`. A
   dated observation had been turned into a permanent requirement, and it took the only
   refresh-and-publish workflow down with it.
   *Repair:* parity is now asserted against the snapshot's **own recorded three-view
   inventory** (`coverage_counts` = api/page/lobby/retained) and against the retained
   `fixture_evidence` the rows were normalised from, plus a per-row contract (official
   Hotspawn link; a pick that is one of the two teams and carries its evidence; or an
   explicit refusal with a reason **and** the source attempts). The 23 Oct observation is
   kept as a dated receipt and no longer re-asserted.

2. **A literal calendar day was asserted against a rendered date.**
   `tests/test_session_f89bb1f8.py` asserted `'23 Oct'` in the phone freshness strip. The
   strip prints the *next pick's own* start date, so the assertion was true for exactly one
   board. *Repair:* assert `build.date(first['start'])` — the same value from the same
   snapshot.

3. **The independent verifier did not know the mirror tier.**
   `research/session-0cc1138a/verify_0cc1138a.py` re-derives every published percentage
   from its archived evidence and imports nothing from `scripts/`. It had no branch for
   `model_vrs_mirror` (points read from HLTV's dated view of Valve's ranking), so two
   *published* probabilities were reported as "not reproducible" while
   `scripts/validate.py` reproduced them fine — a gap in the audit, not in the row.
   *Repair:* the verifier now re-derives both originated tiers from the row's own stored
   point pair, using Valve's Glicko expectation at the rating deviation Valve publishes
   (`model/fit.js`) and Valve's fit slope `0.7986` (`modelfit.png`), and it **refuses** a
   record whose stored `raw_expected`, stored `probabilities`, slope or rating deviation
   disagree with that recomputation.

4. **One missing `}` silently disabled 125 lines of phone CSS.**
   `assets/style.css` had an unclosed `@media(max-width:650px) and (max-height:700px){`
   block. CSS error recovery treats the rest of the file as the body of the last at-rule,
   so every `body[data-page="index"]` phone rule after it was dead — measured consequences
   at 390×844: the strip rendered `Next pickFOKUS78.5%` as run-together inline text and the
   first pick card sat at **y=791**, behind the fixed tab bar (top 783). After closing the
   brace: the strip is a laid-out card (`NEXT PICK · FOKUS · 78.5%`) and the first card is
   at **y=324** — a full pick with both teams' percentages on the first screen.

5. **The harvest committed a snapshot without regenerating what Pages serves.**
   Pages is configured `build_type: legacy`, source `main:/`
   (`GET /repos/buffedlizard55-lab/MaltaProj4/pages`, read this session), so the committed
   root pages are the published bytes. My first harvest run
   ([40066501225](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40066501225))
   committed `data/latest.json` and stopped there; its own committed-state validator then
   failed with `KeyError: '1081606'` because it compared new data against day-old pages.
   *Repair:* the workflow now runs `scripts.build` → `scripts.publish_root_fallback` →
   `validate --site .` → `unittest` **against the exact files it commits**, commits their
   logs, and fails the run if any of them is red.

## 3. The fresh board this session produced

Run [40067062049](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40067062049)
on a normal GitHub egress (this authoring sandbox can reach GitHub and package registries
only — Hotspawn, HLTV, Polymarket, Pinnacle and the listing pages are unreachable from it).

Snapshot `2026-10-24T05:46:07.414253Z`: **88 feed rows, three-view parity 88/88/88/88,
25 open, 25 picks, 25 win probabilities, 0 unresolved.**

| Probability source | Rows | What it is |
| --- | --- | --- |
| Polymarket two-sided order book (de-vigged) | 12 | market line |
| Polymarket within the labelled wide tier | 2 | market line, real spread published, low confidence |
| Thunderpick, read through the BO3.gg listing API | 2 | bookmaker line, de-vigged |
| Valve regional standings through Valve's own formula | 7 | *our* originated line, labelled as a model everywhere |
| HLTV's dated view of Valve's ranking, same formula | 2 | originated line, published only where Valve's monthly file cannot resolve a club |

Every row also records what was tried and failed: Polymarket with no exact pair (24),
Pinnacle with no exact fixture (13), HLTV without a ranked pair (13), GG.BET returning HTTP
403 (11), Thunderpick HTML without a parseable two-way pair (11), book-listing rechecks
that found no line (4). Those are the recorded attempts the unresolved section reports from,
so a blank is always an explained blank.

## 4. Where the picks are, on a phone

* First screen (390×844 and 320×568): the strip names **the next pick with its percentage**
  and the counts, then the pick cards follow immediately — measured y=324 for the first
  card, no horizontal overflow at 320 px, both tap targets (strip CTA, tab bar) ≥ 40 px.
* Each card prints **both** teams' win chances with our pick tagged `OUR PICK`, plus the
  source kind and the lock time; the opponent's number is withdrawn at expiry too.
* The executive summary's in-site links (`picks.html`, `#picks-at-a-glance`,
  `unresolved.html`, `matches.html`, `sources.html`) are present on every page via the tab
  bar, the strip and the jump nav; the full guide is folded so it cannot push the picks off
  the first screen.
* `/unresolved.html` carries the separate unresolved list and the limitations for
  generating a pick; `#unresolved-limits` repeats the counted version inside the executive
  summary.

## 5. Verification performed (commands and results)

| Gate | Command | Result |
| --- | --- | --- |
| Unit and regression suite | `python -m unittest discover -s tests` | **1213 tests, OK (1 skipped)** |
| Independent audits | `python -m unittest discover -s audits -p 'test_*.py'` | **9 tests, OK** |
| Independent integrity | `python verification-95b588c2/test_integrity.py` | **5 tests, OK** |
| Independent replay (c6) | `python -m unittest discover -s verification-c6 -p 'test_*.py'` | **12 tests, OK** |
| Row/arithmetic/link/checksum validator | `python -m scripts.validate --data data/latest.json --site .` | 88 rows, 25 calculations reproduced, 813 links and assets, 20 checksums, 216 displayed rows |
| Independent retained-evidence audit | `python verification-c6/audit_snapshot.py data/latest.json` | **88 rows, 0 failures** |
| Phone/tablet/desktop, a11y, expiry | `npm run test:browser` | **9 suites green** (32 viewport scans at 320/390/768/1440 px, axe WCAG 2.1 AA, exact-boundary expiry, first-screen placement) |
| Stylesheet structure | `node tests/browser_3c79a355.cjs` | both copies parse, balanced braces, one nesting level, first card on the first screen |

New guard files: `tests/test_session_3c79a355.py` (16 tests) and
`tests/browser_3c79a355.cjs`, registered in `package.json`.

## 6. Sources

* Hotspawn CS2 inventory (fixtures only, never a probability):
  <https://play.hotspawn.com/lobby>, <https://play.hotspawn.com/cs2-pickems>,
  <https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1>
* HLTV (fixture identity, lineups, world ranking, Valve-points mirror, recent form,
  head-to-head): <https://www.hltv.org/matches>, <https://www.hltv.org/ranking/teams>,
  <https://www.hltv.org/valve-ranking/teams>
* Valve's own model inputs: <https://github.com/ValveSoftware/counter-strike_regional_standings>
  (`model/fit.js` rating deviation, `modelfit.png` slope 0.7986, `standings_global_*.md` points)
* Markets: Polymarket Gamma API (`https://gamma-api.polymarket.com/markets/{id}`), Pinnacle
  guest esports API, EGamersWorld CS2 listing, stavka.tv listing, BO3.gg (Thunderpick line)
* The freeze itself: the five failed runs above, plus the job/step records that place the
  failure before the refresh step.

## 7. Flagged for review (published on the site, non-blocking)

1. **The watchdog's escalation never reached a human.** `evaluate` returned `stop` for five
   consecutive same-commit failures, which is the documented escalation condition, yet no
   issue was opened and the site simply kept showing withheld picks. The escalation path
   reads GitHub's search API; the same call succeeds outside the runner with the same token
   scope, so the failure is in the workflow context, not in the query. Not repaired here —
   it needs one run with `gh run view --log` access, which this sandbox cannot read.
2. **`scripts.publish_root_fallback` cannot promote a same-snapshot rebuild.** Its guard
   refuses when the committed root is "at least as new", so an asset-only repair (this
   session's stylesheet) reaches the served root only alongside the next *newer* snapshot.
   That happens within the hour while refreshes are healthy, and it is why the CSS repair
   ships with a data refresh rather than on its own.
3. **GG.BET still answers HTTP 403 to the collector (11 rows).** Recorded per row as an
   access failure; never counted as evidence that the book has no line.
4. **The published root pages and the Actions artifact can briefly differ** while the legacy
   rebuild runs; the freshness strip is what keeps an expired snapshot from looking current
   in the meantime.
