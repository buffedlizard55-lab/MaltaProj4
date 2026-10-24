# Session 93f6951a — independent verification of the published board (2026-10-24)

This session's question was narrow: **does the live board actually answer "which team,
how likely, and on whose word" for every open Hotspawn CS2 fixture, and is the answer
re-derivable from the evidence the page itself links?** Everything below is measured,
not asserted. No number here was copied from another session's notes.

## 1. What the live site served

`https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json` at 17:0xZ:

| field | value |
| --- | --- |
| revision | `f5eaafbc77cbc712ea32409bce37a9bd4e78e1ad` |
| built_at | 2026-10-24T16:58:49Z |
| snapshot_generated_at | 2026-10-24T16:40:40Z |
| rows | 83 |

The rendered executive summary on that build reads **"20 open CS2 match(es) · 20 with a
pick · 20 with a win probability · 0 unresolved"**, and the pick board lists both teams'
percentages, the pick, the fair line, the model line where one exists, and a linked
source per row. 16 rows are market-derived, 4 are our own Valve-VRS model line
(`model_vrs`, `model_vrs_mirror`).

## 2. Why the board was frozen for eight hours before that

At 16:26Z the same URL still served revision `71eddff`, `built_at 08:26:58Z`,
`snapshot_generated_at 08:06:51Z` — 8h23m old, past the 8-hour evidence window, so the
page correctly rendered *"Snapshot expired or timestamp unverified … 0 with a pick"*
and withheld every pick. The scheduled run at 13:16Z
([40097410704](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40097410704))
had failed in `verify-build` at the step *Keep the legacy main:/ root fallback on the
verified build*, annotated *"The staged root failed its own validator or unit gate, so
it was not committed and main stays green."*

This session reproduced that locally from its own non-publishing capture
(`research/harvest-93f6951a/`, 16:34:01Z): the staged build succeeded, `scripts.validate`
passed, and `python -m unittest discover -s tests` failed with 42 failures and 3 errors.
Most came from one class: **tests that index the live snapshot by a fixture id**. Hotspawn
rotates fixtures out of the feed within hours, so `next(m for m in SNAPSHOT['matches'] if
m['id'] == '1083121')` (and `1081152`, `1082859`, `1082769`, …) raised `StopIteration` /
`KeyError` for fixtures that no longer existed. The row data was healthy — the gate was
pinned to identities that expire.

Main's own repair landed as `ac5bcb06` (read the pinned row from a retained capture when
it is no longer live) and `65cacdc` (an even verified line is not turned into an invented
pick); the board republished at 16:58:49Z and has refreshed since.

## 3. Independent replay of the committed board

`verification-93f6951a/verify_board.py` shares no code with `scripts/`. It re-derives
every published probability from the row's own stored receipt (de-vig of the recorded
`decimal_odds`, exchange mid, or Valve-VRS expectation from the recorded points), checks
that the pick is one of the named teams and is the larger probability, that the source
URL is an official `https` page, that the row is inside its evidence window, that the
rendered pages carry every open row and both percentages, and that the displayed counts
equal the data.

```
rows 83 · open_rows 20 · open_with_pick 20 · open_with_probability 20
open_unpriced 0 · checks 3380 · failure_count 0
```

`tests/test_session_93f6951a.py` runs it in the unit gate and proves it fails on each
class of corruption (a tampered pick, a re-priced row, a missing open card, a dropped
source link), so a green run means something.

## 4. Live source spot checks (not from any stored receipt)

| fixture | board says | live source at 17:08Z |
| --- | --- | --- |
| `1082695` Galorys vs paiN | paiN 58.0% (`exchange`) | Polymarket `6101181`: outcomePrices `0.42/0.58`, bestBid `0.41`, bestAsk `0.43`, spread `0.02`, liquidity **$44,209** — exact match |
| `1082860` FlyQuest vs Staqued | FlyQuest 92.3% (`bookmaker_fallback`, Thunderpick `1.001/12.0`) | Polymarket `6066520`: mid `0.525` but bestBid `0.10` / bestAsk `0.95`, spread `0.85`, liquidity **$111** — not a tradeable price, and the ladder refused it; the 92.3% line is the one corroborated by six named books in `data/book-receipts.json` |

The second row is the useful one: the number that *looks* extreme is the one with the
better evidence, and the number that looks moderate is noise on a $111 market. The board
chose correctly and says so on the row.

## 5. One boundary left as a documented limitation (not changed)

On this session's own 16:55Z capture, Polymarket `6066520` quoted bestBid `0.35` /
bestAsk `0.95` — a spread of exactly `0.60`. The `exchange_wide` tier accepts up to and
including `0.60`, so that capture published `65.0 / 35.0` for `1082860`, while six books
said `92.3 / 7.7`. The row was labelled *"Low confidence: wide two-sided quote"*, so the
reader is told, but a spread-at-the-ceiling quote outranks a six-book consensus in the
current ladder order. That ordering is a deliberate, test-pinned policy owned by other
sessions' work; this session recorded the measurement rather than re-ranking the ladder.

## 6. Phone layout

`mobile-measurements.{json,md}` were taken at 16:49Z on the 16:34 build (22 open rows):
zero horizontal overflow at 320/390/412/768/1440 px, four percentages on the first
screen at every phone size, and 17 in-site links to the pick board. They describe that
build, not the current 20-row board; the repository's own browser suites
(`tests/browser_*.cjs`) run against the current build in CI.

## 7. Reproduce

```
python verification-93f6951a/verify_board.py --data data/latest.json --site .
python -m unittest tests.test_session_93f6951a -v
```
