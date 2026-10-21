# Session 0b26ea9a — scheduled publication restored, and the last unpicked fixture audited

Read first: `COORDINATION.md`. This file records what this session measured and
what it changed. Every value below is either reproduced from a file in this
repository or quoted from a dated, linked public page. Nothing is inferred.

Scope note: several sessions worked on the 2026-10-21 refresh at the same time.
Main (`710e985`, PR #99, session 5ed35e72) landed its own fix for the same
blocked fixture while this branch was running: a label mapping for
`ex-CYBERSHOKE` and the missing collector call to the one-sided standings tier.
This branch therefore keeps only what main does not have — the proof that the
tier is reachable and replayable, a latent `NameError` fix on the branch that
tier takes, two refused two-way displays, and this record. Where main's decision
differs from an earlier draft of this session's work, main's narrower decision is
kept and the difference is written down in §5.

## 1. The site had stopped updating, and the cause was a test

At 12:36 UTC on 2026-10-21 the live site was still serving the build from
**2026-10-20T07:44:51Z** (`build-info.json`, revision `b648875`, 96 rows) — 21
hours past its own eight-hour evidence ceiling, so every open pick on the board
was already expired.

The scheduled publish workflow had failed on **every** scheduled slot from
2026-10-20 onwards. `gh run list --workflow=pages.yml` gave the ids; each
failed in 27–30 s with steps 9+ skipped, which places the failure in step 8,
*Unit and independent failure-mode tests*, before any source was contacted.

Reproduced locally with `python -m unittest discover -s tests`: three failures,
all in `tests/test_session_133fe7ca.py`. `fixture_for()` scored its fixture
against `datetime.now()` while pinning the fixture start to
`2026-10-20T12:00:00Z`. Once that instant passed, `normalize_fixtures` marked the
row `not_open`, and `research_rank_pick()` correctly refused to price a closed
fixture. A correct production refusal had been turned into a red gate by a
wall-clock test.

Main fixed the same fragility in PR #96 (`arena/3a695af9`) while this session was
reproducing it. This branch keeps main's `PINNED_NOW` and adds
`FixedReferenceClockTests`, which asserts the pinned instant is before the
fixture's own lock and start, so the outage cannot silently return.

**Measured effect:** after the fix, the same workflow passed end to end — tests,
refresh, quarantine, build, independent audit, browser suite — and committed its
fresh capture, which is the snapshot audited in §2.

## 2. Per-fixture audit of the 12:47Z refresh

`scripts/capture_0b26ea9a.py` writes the exact refreshed snapshot and one record
per open fixture (pick, method, both probabilities, expiry, every attempt with
its URL and reason). It is kept here for reproduction; no workflow step depends
on it any more.

Board `2026-10-21T12:47:40Z`: 81 feed rows, 19 open, fixture observation
12:44:10Z, coverage verified. 12 priced by a market line, 4 by the Valve-standings
model, 2 research-only, **1 with no pick at all**: **1082762, ex-CYBERSHOKE vs
BlinkDagger** (CIS LAN Championship #9, 15:00Z).

## 3. Why that row had no pick

### The tier was implemented but never called

`scripts/vrs.py research_single` is the documented final tier: exactly one team
resolves in Valve's official global standings and the other label is genuinely
absent. On the base commit it was implemented, rendered as `research_vrs_single`,
accepted by `scripts/validate.py`, replayed by
`verification-c6/audit_snapshot.py` and covered by tests — but
`scripts/refresh.py` never called it. The tier could not fire, and nothing on
the board could show that. Main's refresh now calls it (verified here by
`CollectorWiringTests`, which pins the call site, its order after the ranking
tiers, and its guard: open rows, no probabilities, no pick, standings loaded).

### A latent crash on the branch it would take

`scripts/validate.py` line 139 referenced an undefined `IDENTITY_REGISTER` inside
the tier's "the standings label differs from the feed label" check. No published
row had ever reached that branch, so the suite stayed green on a branch that
would have raised `NameError`. It is now bound to `IDENTITIES`, which the module
already imported, and
`test_a_renamed_standings_label_passes_the_registered_mapping_check` replays that
exact path.

### The source record for the club is contradictory

- HLTV match page 2399839 shows `VRS: #78` for the `ex-CYBERSHOKE` label, linked
  to team id 14106.
- HLTV's team page for **the same id** says the team has no active players, no
  world rank, no roster, no transfers, and has played no matches, and its FAQ
  answers "ex-CYBERSHOKE doesn't have a world rank at the moment".

Published as an irregularity. **Nothing on this site is derived from the #78
figure.** Valve's file lists `CYBERSHOKE` at #61 (1201) and #171 (786); the bare
label appears twice, so the identity rules cannot pick a roster without a
lineup.

### Esportsbooks

| Source | Read | Display | Outcome |
| --- | --- | --- | --- |
| EGamersWorld listing | 12:59Z | 1.8 / 1.8 on both sides | **rejected** — identical default placeholder, the same pattern already recorded for other fixtures |
| kushvsporte.ru (aggregator) | 12:56Z | 1.12 / 5.59, no book named | **rejected** — not a book's own listing, no update timestamp, affiliate price links; its own search-index excerpt the same morning read 1.06 / 7.28 |
| HLTV betting analytics | 12:47Z | no numeric two-way line | no line |
| winline.ru | 2026-10-21 | public CS2 pages carried no readable line | no line |

Both displays are appended to `data/book-receipts.json` → `rejected_listings`
with values, timestamps, URLs and reasons. **No probability is published from
either.**

## 4. What the exchange did while this was happening

At **12:50:57Z** a Polymarket market for the exact pair and UTC start opened
(event `cs2-cs1-bli4-2026-10-21`, market 5971981): outcomes
`["CYBERSHOKE Esports", "BlinkDagger"]`, `outcomePrices` 0.825 / 0.175, bid 0.82
/ ask 0.83, `liquidity` 1,920.994, `acceptingOrders` true. The next refresh
priced the row through the strict exchange gate at **82.5% / 17.5%, pick
ex-CYBERSHOKE**. Both values are the collector's own output in the dated
captures under `research/session-0b26ea9a/`; nothing was hand-entered.

## 5. Decisions kept from main, and one this session declined

- **Kept:** main maps `ex-CYBERSHOKE` → `CYBERSHOKE Esports` on exact
  opponent-pair plus exact UTC-start parity (HLTV match page, Liquipedia CIS LAN
  #9, Polymarket event 1224206) and deliberately does **not** map the bare
  `CYBERSHOKE` label, because Valve lists two different CYBERSHOKE rosters.
- **Declined:** an earlier draft of this branch mapped the feed label straight to
  `CYBERSHOKE` and relied on Valve's three-player roster rule to choose #61 over
  #171. That inference is defensible, but it would have overridden a merged
  decision from another session, and HLTV's own team page says the club has no
  roster to reason about. It is not in this branch.
- **Consequence, published:** because the register maps labels to *each other*
  while the standings tier matches Valve's *own* labels, the one-sided tier still
  cannot resolve this particular club. That limitation is in the Flagged for
  Review note `0b26ea9a-one-sided-tier` rather than worked around.
- **Also published, not resolved by this session:** main holds a
  `stavka-cybershoke-blinkdagger-1082762` receipt for this fixture that quotes a
  cross-operator price panel (Winline 1.14 / BetBoom 7.50) from a media page
  rather than one book's own listing. It is flagged by its own note, and it does
  not price the published row — the row is built from the exchange quote, which
  outranks it. This session could not independently verify that panel: the page
  as read here was an editorial tip page, and winline.ru's public CS2 pages
  carried no readable line.

## 6. Verification performed

| Gate | Result |
| --- | --- |
| `python -m unittest discover -s tests` | 487 tests OK |
| audits / integrity / verification-c6 | 9 / 5 / 12 OK |
| `python -m scripts.build` + `scripts.validate` | 98 rows, 29 calculations reproduced, 15 pages, 613 links/assets, 20 checksums, 184 displayed rows |
| `npm run test:browser` | 32 accessibility/no-overflow scans at 320/390/768/1440 px + 11 expiry scenarios |
| Actions on this branch | full pipeline green, `deploy` skipped on PRs by design |

The executive summary was also read as a 390 px screenshot: hero actions,
`Picks at a glance` in start order, the `#unresolved-summary` section with its
numbered limitations, and the persistent five-tab phone bar.

## 7. What is not claimed

No probability for 1082762 from any refused display. No claim that the
cross-operator panel is wrong — only that it is not a book's own two-way line.
No claim that this branch fixed the outage (main did, in PR #96); this branch
keeps the regression that prevents it returning. No claim that the one-sided
tier resolves this club: it does not, and that is published.
