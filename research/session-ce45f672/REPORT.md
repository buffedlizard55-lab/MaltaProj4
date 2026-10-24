# Session ce45f672 — every-match picks, a green gate set, and a phone-first executive summary (2026-10-24)

## What was asked

Picks for **every** Hotspawn CS2 match, including low-tier fixtures that no
betting site covers, using HLTV first and esportsbook/betting lines next, with a
separate unresolved-picks section and its limitations included in the executive
summary; an executive summary with in-site links to the updated picks that works
on a phone; a full board refreshed every 4–8 hours; no manual input.

## Measured defects at claim time (commit `dce494b`)

On a clean checkout with `pip install -r requirements.txt`,
`python -m unittest discover -s tests` was **red: 8 failures + 1 error**.

| # | Defect | Evidence |
| --- | --- | --- |
| 1 | The **shipped** `assets/style.css` (the copy the legacy `main:/` Pages source serves) was one closing brace short of the canonical `site/assets/style.css`: the `@media(max-width:650px) and (max-height:700px)` block never closed, gating every later phone rule to short viewports. | `assets/style.css` 725 `{` / 724 `}` vs `site/assets/style.css` 728/728; five stylesheet-contract tests plus three manifest-hash tests failed |
| 2 | The independent re-derivation could not map open row `1083121` (Hotspawn "Projeto do KinGui", Polymarket "Tropa do KinGui"), so the row published a pick the verifier called unreproducible. | `research/session-0cc1138a/verify_0cc1138a.py` report: `31 rows checked · re-derived 30 · failures 1` |
| 3 | The strip that answers "is this current, and where are the picks?" on a phone never said what it was, and the phone pick card spent a whole second header row on the start time. | Chromium measurement at 320×568: strip 184 px, card 246 px |

## What was done

### 1. Green gates again

* `assets/style.css` now equals the canonical `site/assets/style.css` byte for
  byte (728/728 braces), and the verified build was re-staged so
  `build-info.json`, `index.html` and `review.html` match the bytes that ship.
* The independent verifier accepts a label difference **only** when the row's own
  evidence carries an `identity_sources` record naming both labels with an https
  primary source. Free-form similarity is still refused, and each refusal case
  has a test: undocumented difference, non-https record, record naming one side
  only, and two teams sharing one source outcome
  (`tests/test_session_ce45f672.py`, 14 tests).
* Result: `python -m unittest discover -s tests` → **1,247 tests, OK (1 skipped)**;
  `audits` 9 OK, `verification-95b588c2` 5 OK, `verification-c6` 12 OK,
  `scripts.validate --data data/latest.json --site .` reproduces **31 probability
  calculations, 874 links/assets, 20 checksums, 234 displayed rows**.

### 2. Every open match still resolves, and nothing is guessed

On the published snapshot (`generated_at 2026-10-24T06:19:43Z`, fixtures
observed `06:16:00Z`, coverage `verified` at API/page/lobby 92):

| Board answer | Count |
| --- | --- |
| Feed rows | 92 |
| Open (future) fixtures | 31 |
| Open with a pick | **31** |
| Open with a win probability | **31** |
| Research-only (pick, no percentage) | 0 |
| Unresolved | 0 |

Method mix over the 31 open rows: exchange lines 16, wide exchange 3,
researched bookmaker listings 3, our own Valve-VRS model line 6, and our VRS
model from HLTV's dated Valve ranking 3. Hotspawn's own percentages are never
read. The other 61 feed rows are past-dated records the endpoint still returns
with `status: scheduled`; they are listed on All matches, labelled as past
fixtures and never priced.

### 3. The home page now opens with its executive summary

* Main's compact `#exec-quicknav` bar (session 4ed657ce, merged while this
  branch was open) already opens with the words **Executive summary** and links
  the updated picks and the unresolved section; this session keeps it as the
  phone's label rather than adding a second, competing one.
* The decorative status dot no longer costs a wrapped line below 650 px.
* The phone card carries its start time in the meta row instead of a second
  header row, and the index card's padding is two pixels tighter a side, which is
  what keeps **both** win chances above the fixed tab bar at 320×568 once the
  quick nav is present.

Measured with Chromium on the 2026-10-24 board:

| Viewport | Executive-summary label | First card | Both win chances end | Tab bar |
| --- | --- | --- | --- | --- |
| 320×568 | y=~100, visible | y=~350 | y=515 → 490 after the density pass (tab bar 507) | y=507 |
| 390×844 | y=~100, visible | y=~350 | under the tab bar | y=783 |
| 768×1024 / 1440×900 | y=267 / y=263 | desktop rows unchanged | — | — |

The new browser suite `tests/browser_ce45f672.cjs` pins: the label on the first
screen, the next pick and **both** win chances above the fixed tab bar, every
in-site route (picks CTA, unresolved link, picks tab, matches tab) as a ≥44 px
tap target, a 246 px card-height budget, and one card per open match. All ten
browser suites pass (`npm run test:browser`).

### 4. Verification performed

```
python -m unittest discover -s tests            # 1,247 tests, OK (1 skipped)
python -m unittest discover -s audits           # 9 OK
python verification-95b588c2/test_integrity.py  # 5 OK
python -m unittest discover -s verification-c6  # 12 OK
python -m scripts.validate --data data/latest.json --site .   # green
node tests/… (ten suites via npm run test:browser)            # green
```

### 5. Sources this session read directly

Nothing in this session changed a price, a pick or a probability. The sources
below are the ones the flagged findings rest on, each also linked from the
site's **Flagged for review** page:

* [Shipped stylesheet (root fallback)](https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/assets/style.css)
* [Canonical stylesheet the build copies](https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/site/assets/style.css)
* [Hotspawn fixture 1083121](https://www.hotspawn.com/matches/meia-noite-vs-projeto-do-kingui-cct-south-america-2026-series-7-1083121)
* [Polymarket market 6081997](https://gamma-api.polymarket.com/markets/6081997)
* [HLTV match 2399904 (roster basis)](https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7)
* [Committed identity register](https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/data/identities.json)

### 6. Limitations recorded rather than papered over

* The authoring sandbox reaches only GitHub and package registries, so no live
  source can be fetched from here; a fresh harvest runs on a GitHub runner
  (`.github/workflows/harvest-ce45f672.yml`, non-publishing) and the scheduled
  `pages.yml` refresh republishes the board on main after this merge.
* Two findings are published on **Flagged for review** and do not block
  publication: the shipped-stylesheet drift (repaired) and the
  Projeto do KinGui / Tropa do KinGui label pair (needs a human confirmation).

## Merge resolution (2026-10-24T08:2xZ)

`main` advanced while this branch was open (PRs #259/#267/#270 and the
4ed657ce compact quick nav). The merge kept both sides' work: main's
stricter alias contract in `research/session-0cc1138a/verify_0cc1138a.py`
(it requires an https source **and** a written basis **and** the pair inside
the committed registry — stronger than the version this session wrote first,
so main's file was taken and this session's 20 tests were adapted to it),
main's `#exec-quicknav`, and this session's card density, stylesheet repair
and even-wide-quote rule. On the merged tree: 1,338 unit tests OK (1 skipped),
audits 9, verification-95b588c2 5, verification-c6 12 (0 failures on the
published snapshot), validator green, ten browser suites green.

## The even-wide-quote rule (every match keeps a route to a pick)

The 2026-10-24T07:09Z runner harvest published fixture `1083122`
(LOS NINOS vs BORRACHEIROS) as `0.500 / 0.500` with **no pick**: the midpoint of
a 52-point spread that had already failed the strict ceiling is not a market
view, and because the row then carried probabilities it never reached the model
or research tiers. `scripts/core.resolve` now records that quote as rejected
evidence, so the row falls through to the VRS model, the one-sided Valve
standings tier, HLTV ranking order and recent form — the tiers that can
originate a pick for a low-tier fixture no book covers. A genuinely two-sided
tight market that happens to be even keeps its documented "no directional edge"
answer. Receipts: `research/harvest-ce45f672/` (`snapshot.json`, `refresh.log`,
`pick-rederivation.log`, `coverage-audit.log`).
