# Session e334b970 — live board repair, every-match pick coverage, phone findability

Branch `arena/e334b970-maltaproj4`, based on `main` `5d56f35`. All work, commits and pushes stay on
this branch. Nothing in this report is inferred: every claim below is either a command reproduced in
the repository, an Actions run URL, or a value read out of the capture committed next to it.

## 1. What was actually wrong when this session started

**The public site was showing an expired board.** The committed snapshot was
`2026-10-23T11:47:19Z` (`build-info.json`, 90 rows). Every open pick in it had expired, so the
pages correctly withheld prices and rendered *"0 with a pick"*. That is the right behaviour for a
stale snapshot, but it was not the cause.

**Cause (measured).** The scheduled publish workflow runs the unit suite *before* it refreshes any
source (`.github/workflows/pages.yml`, step *Unit and independent failure-mode tests*, then step
*Refresh official sources*). The Actions API shows every scheduled `Verify, refresh and publish CS2
Scout` run since 2026-10-23T12:00Z failing at that step:

| Run | Started | Result | Failing job/step |
| --- | --- | --- | --- |
| [40025828846](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40025828846) | 2026-10-23T12:1xZ | failure | `verify-build` / *Unit and independent failure-mode tests* |
| [40033438852](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40033438852) | 2026-10-23T15:xxZ | failure | same |
| [40042111432](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40042111432) | 2026-10-23T19:xxZ | failure | same |
| [40062143026](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40062143026) | 2026-10-24T04:xxZ | failure | same |

(Step-level failure attribution comes from
`GET /repos/buffedlizard55-lab/MaltaProj4/actions/runs/<id>/jobs`; the raw log archive lives on
`results-receiver.actions.githubusercontent.com`, which this sandbox cannot reach, so the failing
*assertions* were established by running the identical command locally rather than by reading that
log. Stated as a limitation, not papered over.)

Reproduced locally against the committed tree, `python -m unittest discover -s tests` returned
**1195 tests, 1 failure + 1 error**, both in `tests/test_session_0cc1138a.py::LiveHotspawnCoverage`:

```
FAIL: test_snapshot_covers_the_observed_lobby_fixtures
  AssertionError: Items in the first set but not the second: '1081148', '1079655'
ERROR: test_each_observed_fixture_is_published_with_a_pick_and_an_official_link
  KeyError: '1079655'
```

Both fixtures were pinned from the 2026-10-23T09:44Z lobby observation. Hotspawn no longer serves
them: `data/latest.json` →`fixture_evidence` (its own dated feed read at 11:43:39Z) contains neither,
and `inventory_changes.removed_ids` is empty because the 11:25Z baseline it diffs against already
lacked them. So the excuse path the earlier session added (`removed_ids`) could never fire, and the
suite failed forever after. Because the unit step runs first, **refresh, build, deploy and the
live-byte verification were all skipped** — the board froze while the world moved on.

## 2. The repair

`tests/test_session_0cc1138a.py` now derives the excuse from the snapshot's **own raw feed evidence**
(`fixture_evidence`, `_excused()`), and a new self-renewing assertion
(`test_every_fixture_the_snapshot_observed_is_on_the_board`) requires every fixture the feed returned
to be a board row. A fixture the feed still returns and the board does not publish is still a hard
failure; an absence the snapshot itself records is sourced, not a gap.

`tests/test_session_f89bb1f8.py` asserted the literal string `'23 Oct'` in the phone freshness strip.
The strip prints the *next pick's* start date from whatever snapshot is built, so that assertion was
true for exactly one day of boards — a second time bomb of the same kind. It now compares against the
row's own `start` date and still requires the `UTC` label.

`tests/test_session_e334b970.py` (new, 15 tests) locks all of this down: a scanner that fails if a
live-snapshot test asserts a literal calendar day, synthetic-snapshot tests that the parity rule
excuses only feed-recorded absences, and coverage tests for the receipt below.

## 3. A real defect found in the independent verifier

`research/session-0cc1138a/verify_0cc1138a.py` is the *independent* re-derivation of every published
pick (it deliberately imports nothing from `scripts/`). It had branches for the exchange mid, the
bookmaker de-vig and the `Valve VRS model` tier — but **not** for `HLTV Valve ranking (Valve points)`,
the mirror tier that prices rows when Valve's monthly file cannot resolve a club. On the fresh
capture that tier priced 2 of 25 open matches (`1081156` Spirit Academy vs LFO 10, `1081158`
FORZE Reload vs ex-RUSTEC), and the verifier reported `re_derived: None` for both instead of
rebuilding them. The independent auditor therefore covered 23 of 25 published percentages and said
nothing about the gap.

Fixed by adding the mirror branch (same Valve expectation, same published calibration slope 0.7986,
RD 75 — read from `points` only). `tests/test_session_e334b970.py::EveryPricedTierIsReDerivable`
now fails if any priced row on any tier cannot be re-derived, so a new tier can never ship unverified
again. This is flagged on **Flagged for Review**, not silently patched.

## 4. Fresh live capture (run [40066532380](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40066532380))

Non-publishing pipeline `.github/workflows/harvest-e334b970.yml`, run on `ubuntu-24.04`, 2026-10-24:

| Stage | Result |
| --- | --- |
| Pre-refresh unit/audit/integrity/validator gates | pass |
| `scripts.refresh` (Hotspawn feed + lobby + general lobby, HLTV, Polymarket, Pinnacle, books, Valve VRS) | pass |
| `scripts.quarantine` (withhold any row the independent replay cannot reproduce) | pass |
| `verification-c6/audit_snapshot.py` on the refreshed snapshot | **0 failures** |
| `scripts.audit_e334b970` coverage receipt | written |
| `scripts.build` + `scripts.validate` | pass |
| Phone/desktop/axe/expiry browser suites | **all 8 suites pass** |

Capture clock `2026-10-24T05:33:45.062897Z`, built `2026-10-24T05:37:20.660266Z`.

**Coverage: 88 feed rows, 88 board rows, 25 open, 25 picks, 25 win probabilities, 0 unresolved.**

| Method | Rows | What produced the number |
| --- | --- | --- |
| `exchange` | 12 | Polymarket two-sided order book, de-vigged (strict gate: ≤25-point spread, ≥$100 liquidity, ≤8 h old) |
| `model_vrs` | 7 | Valve's official standings points → Valve's published expectation formula + calibration |
| `bookmaker_fallback` | 2 | A dated, identity-verified two-way line from a bookmaker listing page |
| `exchange_wide` | 2 | Polymarket quote past the strict spread ceiling, published with its real spread |
| `model_vrs_mirror` | 2 | Same model, points from HLTV's dated mirror of Valve's ranking (Valve's monthly file cannot resolve those clubs) |

Per-row evidence, observation times, expiries and official Hotspawn links: **`ROW-LEDGER.md`** next to
this file. Raw snapshot: `research/harvest-e334b970/snapshot.json`. Receipt:
`research/harvest-e334b970/coverage-receipt.{json,md}`. Source read results with HTTP status:
same receipt, *Source read results*.

### Source ladder for matches the featured tiers cannot price

Unchanged and verified in this capture — Hotspawn supplies fixture inventory and locks only, never a
probability. When a match has no strict market line the pipeline tries, in order:

1. **HLTV** — exact fixture identity, UTC start, lineups, world ranking and ranking order
   (`https://www.hltv.org/matches`, fixture pages). HLTV's betting table exposes no numeric two-way
   line to this collector, and its community vote is never used as a probability.
2. **Esportsbooks and betting lines** — Pinnacle's guest esports moneyline, Polymarket's wide quote
   (labelled low confidence with its spread), and researched bookmaker listings on EGamersWorld
   (`https://egamersworld.com/counterstrike/matches`, Thunderpick lines via bo3.gg). GG.BET and
   EGamersWorld answered 403 to this collector on earlier captures — recorded as access limits,
   never as "no odds exist".
3. **Our own originated line** — Valve's official Regional Standings through Valve's own published
   expectation formula and calibration (`github.com/ValveSoftware/counter-strike_regional_standings`),
   plus HLTV's dated mirror of the same ranking when Valve's monthly file is stale for a club.
4. **HLTV recent form / head-to-head** — weakest tier: a pick with **no percentage**, for a fixture
   that is listed but has no market, model or ranking evidence.
5. Anything still unresolved stays blank, with the exact gate it failed, and is published on
   **Unresolved & non-market** and in the executive summary's limitations section.

## 5. Executive summary and phone

The summary already carried a separate unresolved/limitations section (`#unresolved-summary`,
`#unresolved-limits`) and in-site links to the picks; this session verified them against the fresh
build rather than assuming them:

* `index.html` renders 17 links to `picks.html`, 15 to `unresolved.html`, and all three unresolved
  anchors (`#unresolved-picks`, `#unresolved-summary`, `#unresolved-limits`) with zero unresolved
  rows, so the section does not vanish when coverage is complete.
* Measured at **320×568** and **390×844** on the rebuilt board: the first pick and **both** teams'
  win chances are on the first phone screen (pick block at y≈166 px, above the fixed tab bar), and
  the bottom tab bar gives *Home · Picks · Unresolved · Matches · Analysis* on every page.
* The eight browser suites (32 page/viewport axe+overflow scans, 320/390/768/1440 px) all pass on the
  fresh snapshot.

Screenshots captured during this session (not committed): `index` at 320 and 390 px, `picks` at
320 px — pick `FOKUS 78.5%` / `ex-6666 21.5%` visible without scrolling.

## 6. Gates run before merge

| Gate | Result |
| --- | --- |
| `python -m unittest discover -s tests` | 1,211 tests, OK (1 skip) |
| `python -m unittest discover -s audits` | 9 tests, OK |
| `python verification-95b588c2/test_integrity.py` | OK |
| `python -m unittest discover -s verification-c6` | 12 tests, OK |
| `verification-c6/audit_snapshot.py data/latest.json` | 0 failures |
| `python -m scripts.validate --data data/latest.json --site .` | 25 calculations reproduced, 15 pages, 810+ links/assets, 20 checksums, 217 displayed rows |
| `npm run test:browser` | 8 suites, 32 viewport scans, phone first-screen placement, expiry and prose/counter agreement |

## 7. Flagged for review (published on the site, non-blocking)

1. **The independent verifier had no branch for the `model_vrs_mirror` tier** while it was publishing
   2 of 25 percentages. Repaired and regression-tested here; the auditor's coverage of that tier
   before 2026-10-24 is therefore unknown and not claimed.
2. **Two tests pinned values that could only be true for one snapshot** (a lobby fixture set and a
   literal `'23 Oct'`), which stopped every scheduled publish from reaching its refresh step for
   ~17 hours. The site now states snapshot age and withholds expired picks, so the failure was
   visible rather than silent, but nothing on the page could fix it. A follow-up for the owning
   session: make the publisher fail *loudly* (issue/notification) when the pre-refresh gate fails
   repeatedly, instead of relying on the page's own freshness prose.
3. **Sandbox egress limit (this session's own limitation).** The Arena sandbox can reach only
   `github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org` and
   `files.pythonhosted.org`; Hotspawn, HLTV, Polymarket, Pinnacle, EGamersWorld and bo3.gg are all
   unreachable from it (`curl` to the fixtures endpoint fails at TLS connect). Every live value in
   this session therefore comes from a GitHub-hosted runner, and the raw response bytes are committed
   under `research/harvest-e334b970/` so they can be re-checked.
4. **Feed rows the lobby does not show, and vice versa.** The capture's feed returned 88 rows; 63 are
   past-dated records still carrying `status: scheduled`. They remain visible on *All matches*,
   labelled as past fixtures, and are never priced.
5. **Scheduler delivery.** GitHub has repeatedly delayed or dropped `schedule` events in this
   repository (documented in earlier sessions). The freshness prose on every page states the
   snapshot's age, and the 8-hour window withholds an expired board rather than presenting it as
   current.

## Sources used in this session (all re-read by the capture, HTTP 200 unless stated)

* Hotspawn fixtures API — `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`
* Hotspawn CS2 lobby — `https://play.hotspawn.com/cs2-pickems`, general lobby — `https://play.hotspawn.com/lobby`
* HLTV — `https://www.hltv.org/matches`, fixture pages, `https://www.hltv.org/valve-ranking/teams`
* Polymarket — `https://gamma-api.polymarket.com/sports`, `/events`
* Pinnacle guest esports — `https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight`
* Valve official standings — `https://github.com/ValveSoftware/counter-strike_regional_standings`
* Bookmaker listings — `https://egamersworld.com/counterstrike/matches`, Thunderpick via `https://api.bo3.gg/api/v1/matches`
