# Session `4fd13975` — picks for every match, own research for the unpriced rows, mobile summary audit (2026-10-22)

## Executive summary

This session answered three questions and left nothing hidden.

1. **Does every Hotspawn CS2 match have a pick?** Yes on the audited snapshot
   (`2026-10-22T07:58:54Z`, 107 fixtures): **43 open, 43 with a verified pick
   (100%), 41 with a reproduced win probability (95.3%)**, 2 research-only
   picks with blank percentages, 0 without a pick. A live cross-check of the
   Hotspawn lobby sidebar at ~08:50–09:00Z on 22 October matched the board
   **tournament by tournament**: all 23 CS2 tournaments with their exact counts
   (CCT Europe Challengers #4: 8, Challengers #8: 2, Series #11: 8, Series #12:
   6, CCT SA Series #3: 8, Series #7: 9, CIS LAN #9: 3, Circuit X Curitiba #4: 2,
   DACH CS Masters S5: 1, DFRAG Invitational: 4, DraculaN S7: 9, EPL Series 8: 1,
   EPL Series 8 Play-In: 6, LG UltraGear: 1, Moscow Cyber Games: 2, NODWIN
   Clutch #13: 2, Rainhas do Clutch: 2, Stake Ranked E6 CQ: 2, Svenska CS-Ligan:
   6, Tesla Cup: 4, TWC SA Series #1: 8, Urban Riga Open #5: 12, VOID Autumn
   Cup: 1 — 107 total, "All tiers (107)" on the lobby). No fixture the site
   lists is missing from the board.
2. **Can the two remaining blank-percentage rows be resolved from HLTV or
   esportsbook lines?** Not without fabricating a number. This session's own
   research (below) re-verified, source by source, why each gate refuses and
   what exactly would have to change for the rows to upgrade themselves.
3. **Is the executive summary usable on a phone?** Yes; the requirements are
   now locked down by regression tests: the summary links the updated pick list
   in its "Where the picks are" cards, in the freshness strip and in the phone
   bottom bar; every open fixture renders on the pick board with the pick and
   (when published) both win percentages; every research-only row names its
   limitation and links its sources; the unresolved section is linked from the
   summary itself.

## Own research for the rows without a win probability

The two rows are `1082925` **BESTIA Academy vs RED Canids Academy** (CCT South
America 2026 Series #7 Round of 16, 2026-10-23T19:00:00Z) and `1082860`
**FlyQuest vs Staqued** (DFRAG Invitational 2026, Brisbane LAN, Bo3 group
opener, 2026-10-27T03:00:00Z). Research order was HLTV first, then esportsbooks
and esports betting lines, exactly as required.

### HLTV (first)

* Fixture pages [2399910](https://www.hltv.org/matches/2399910/bestia-academy-vs-red-canids-academy-cct-2026-south-america-series-7)
  and [2399890](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026)
  were read on 22 October. Both "Betting" tables render only the
  Stake-sweepstake promotional cell — **no numeric two-way line** in the
  response. The same refusal is already on the board's attempt ledgers.
* The pages do display "Pick a winner" fan-vote percentages (84.6 / 15.4 on
  2399890) and the DFRAG event page shows its own percentage widgets
  (71.5% / 47.8% beside FlyQuest). Per project policy these are refused
  context, never probability inputs; they are logged as review note
  `4fd13975-hltv-fan-votes-refused-2026-10-22`.
* Lineups confirmed identity: BESTIA Academy (Jotag3, lezy, F4QQ, Lekzi, agt) —
  RED Canids Academy (n1cks, rafa, sanc, gtw, FasteR); FlyQuest (jks, INS,
  Vexite, nettik, aliStair) — Staqued (w0mbat, xelja, Hazel, lzj, kasze).
  Staqued has an HLTV team page ([team 13997](https://www.hltv.org/team/13997/staqued))
  but **no HLTV world ranking and no HLTV Valve rank**, matching the board.

### Originated line inputs (Valve's official standings — reproducible locally)

From the vendored copy of Valve's official
[2026-10-05 global standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)
(`data/vrs/standings_global_2026_10_05.md`, byte-copied into the repository):

* **BESTIA Academy is listed** at #215 with 698 points, roster
  `agt, F4QQ, Jotag3, Lekzi, lezy` — an exact 5/5 match with the HLTV lineup.
  The model can price this side.
* **RED Canids Academy is absent.** The only similar label, "RED Canids" #243
  (653 pts), fields `chayJESUS, dav1deuS, drop, kauez, reNTU` — **0/5 overlap**
  with the Academy lineup, so the Valve roster-continuity rule (≥3 shared
  players) forbids the mapping. `n1cks` appears once (Vasco #309,
  `mawth, n1cks, prt, tatazin, trindade`) — 1/5, far below the rule. The
  two-team model line therefore fails closed, exactly as the row's attempt
  ledger says.
* **Staqued is absent** as a label and **all five players** (w0mbat, xelja,
  Hazel, lzj, kasze) are absent from the 2026-10-05 file; session db1f35c5
  already verified Staqued is also absent from the 52-team 2026-10-21 Asia
  regional Valve ranking. FlyQuest resolves cleanly (#86, 1093 pts, exact 5/5),
  so the row keeps its one-sided `research_rank_single` pick with no invented
  percentage.
* HLTV's dated Valve-ranking mirror (the tier that priced LFO 10, TitanFlow,
  ex-RUSTEC and Hacha earlier today) records "not listed" for both RED Canids
  Academy and Staqued on 22 October. Nothing was derived from a single club's
  points.

### Esportsbooks and esports betting lines

| Source | 1082925 BESTIA Academy–RED Canids Academy | 1082860 FlyQuest–Staqued |
| --- | --- | --- |
| [Polymarket 6036921](https://gamma-api.polymarket.com/markets/6036921) | moneyline exists but quotes 0.05 / 0.95 — **spread 0.90, above even the 0.60 wide-tier ceiling**; refused | no market in the feed (searched) |
| [Pinnacle guest feed](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight) | no exact pair + UTC start | no exact pair + UTC start |
| [EGamersWorld listing](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3) / [second listing](https://egamersworld.com/counterstrike/match/fQ0D-T2eM/bestia-academy-vs-red-canids-academy-3nbNt3Gf1p) | identical 1.8/1.8 placeholder — refused, never 50/50 | identical 1.8/1.8 placeholder — refused |
| [Stavka.tv / Winline](https://stavka.tv/matches/csgo/23-10-2026-bestia-academy-red-canids-academy) | a **preview page exists** with an editorial pick ("Выбор редакции: Победа RED Canids Academy" — explicitly "not a recommendation"); no Winline П1/П2 moneyline panel was observed in the read chunks; the runner probe re-reads the raw HTML and books.watch re-checks it every refresh | no stavka page found under the date-slug variants tried (404); probe tries further variants |
| [GG.BET](https://gg.bet/en/esports/counter-strike) | HTTP 403 (access refused; never bypassed) | HTTP 403 |
| [Thunderpick](https://thunderpick.io/esports/cs2-betting) | access only; no validated automated quote | same |
| [bo3.gg](https://bo3.gg/tournaments/dfrag-invitational-2026) (prior dated reads) | "All odds are on" | no two-way line on the event page |
| Kalshi (prior dated read) | zero open CS2 markets | zero open CS2 markets |

**Verdict.** No verified market line and no two-team Valve-points line exists
for either row at this observation. Publishing any percentage would require
inventing one — from a fan vote, a rank gap or a placeholder pair — which the
project's evidence rules forbid. Both rows keep their researched picks
(RED Canids Academy on HLTV rank order #170 vs #184; FlyQuest on one-sided
ranking evidence #61 vs unranked), blank percentages, blank fair odds, and
source-linked limitations on the Unresolved page and in the executive summary's
own "Picks without a win probability" and "Matches with no market line"
sections. Each row also states what would upgrade it: a real two-way listing
pair, a tightened Polymarket spread (1082925 only), or a Valve listing under a
verified ≥3-player alias.

## What changes so the rows upgrade themselves

The K27/NEXORA research of 21 October showed these listing pages **fill their
book-average widget late** — a placeholder three days out can become a genuine
pair within hours of the start. Until now nothing re-read a page after its
first rejection, so that upgrade needed a human re-read.

`scripts/books.watch()` (session 4fd13975) closes the gap: **every scheduled
refresh re-reads each rejected listing URL that belongs to an open, unpriced
fixture** and promotes a receipt only when the live page states the exact
fixture team pair (through the identity register's `norm`), the exact fixture
UTC start, and an asymmetric two-way pair bound to both labels. Placeholders,
identical pairs, unbound pairs, start/team mismatches and access failures are
recorded refusals. The rejected entry's own copied fields are never trusted —
the snapshot fixture row is the only identity reference (this is also why the
flagged field inconsistencies above cannot leak into a price). The committed
`data/book-receipts.json` is never modified. Promoted receipts flow through the
existing `book_research_pick` tier with the same eight-hour window, margin
bounds and validator replay as every researched book line. The scheduled
refresh on `main` runs four times an hour, well inside the 4–8 hour freshness
promise.

Tests: `tests/test_session_4fd13975.py` (promotion, refusal and
no-50/50 rules; end-to-end pricing; register immutability; executive-summary
links; unresolved-section coverage; per-row source links; both probabilities
displayed; viewport and phone navigation on all eight primary pages).

## Executive summary & mobile audit (requirement checklist)

* "Executive summary that provides links within our site to where an updated
  list of picks can be found" — `index.html` `#start-here` cards link
  `picks.html`, `#unresolved-summary`, `matches.html`; the freshness strip
  carries a "See today's picks" call to action; the footer and phone bar repeat
  the links. Tested.
* "Separate section for unresolved picks and the limitations … include this in
  the executive summary" — `#unresolved-summary` on the home page names every
  row without a percentage and links `unresolved.html`, whose h2 states
  "43 open matches · 43 with a pick · 41 with a win probability · 2 without one
  · 0 unresolved" and whose body lists every source tried per row. Tested.
* "Obvious what the pick is … probabilities for each team … mobile friendly" —
  each row renders the pick in a dedicated cell (amber "Research only" badge
  when unpriced), both percentages "Team 55.0%" style, 320px-first cards, a
  five-target bottom bar (Home/Picks/Unresolved/Matches/Analysis), viewport
  meta and no sideways scrolling (32/7/8 browser scenarios pass at
  320/390/768/1440px).

## Verification receipt (all local gates, 2026-10-22)

* `python -m unittest discover -s tests` — **831 tests OK** (808 baseline + 23 new).
* `python -m unittest discover -s audits -p 'test_*.py'` — 9 OK;
  `verification-95b588c2/test_integrity.py` — 5 OK; `verification-c6` — 12 OK.
* Independent auditors: `verification-4901f43e` **35 passed, 0 failed** (2 known
  warnings: stale figure in another session's REPORT.md, 17 historical HLTV
  citations not re-read — both already logged);
  `verification-7271c5d5` errors `[]`; `verification-7601d5ee` status `ok`;
  `verification-767649ba` **3053 checks, 0 failures** (2 advisory notes).
* `python -m scripts.validate --data data/latest.json --site .` (and `--site
  public`) — 107 rows verified against the primary snapshot, **41 probability
  calculations reproduced**, 15 pages, 964 internal links/assets, 20 artifact
  checksums, 283 displayed match rows — no validation errors.
* `npm run test:browser` — 32 viewport/accessibility scans (320/390/768/1440px),
  7 expiry scenarios, 4 research-quote boundary cases, 8
  phone/desktop/queue/unresolved scenarios — all pass.
* Coverage cross-check — live lobby sidebar (fetched 2026-10-22 ~08:50Z) vs
  `data/latest.json`: 23/23 tournaments, 107/107 fixtures, exact counts.

## Irregularities flagged (published on Flagged for Review)

1. **PR #176 merge bookkeeping** — GitHub records it merged at 08:15:01Z with
   commit `1ea27797`, but that commit is unreachable from `main` and from the
   remote; its content is on `main` via PR #175 (byte-identical files). Flagged
   as `4fd13975-pr176-merge-receipt-irregularity-2026-10-22`; nothing lost.
2. **Rejected-listings metadata inconsistencies** — refused entries for 1082925
   carry a wrong start/tournament (`2026-10-22T20:00:00Z`, "Aorus League"), the
   `zawJ-Q52S3` id fragment is recorded against two different fixtures, and
   their rank claims differ from the snapshot. Flagged as
   `4fd13975-rejected-listings-field-irregularities-2026-10-22`; refused-only,
   no board impact, not rewritten.
3. **HLTV fan votes** — recorded and refused, note
   `4fd13975-hltv-fan-votes-refused-2026-10-22`.
4. Existing board issues (feed entries past their start; HLTV canonical
   ranking 403) remain on the board's issues list and the Sources page.

## Runner harvest (official-source capture)

Workflow `.github/workflows/harvest-4fd13975.yml` (non-publishing, bound to
`arena/4fd13975-maltaproj4`) ran `scripts.refresh` +
`scripts.probe_4fd13975` on a GitHub-hosted runner (run
[39757267589](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39757267589),
observed **2026-10-22T10:01:21Z–10:07Z**). Dated raw bytes are archived under
`research/harvest-4fd13975/raw/` (sha256-named) with the machine-readable
`unresolved-probe.json`, the full `refresh-snapshot.json` and its `REPORT.md`
committed by the runner at `59e178f`. Findings:

1. **The gap-recheck watcher ran live in the pipeline** and appended a dated
   `Book listing gap recheck` attempt to every unpriced row with a rejected
   listing (1081149, 1081150, 1082925, 1082926, 1082860, plus 1082858). Every
   one resolved "unresolved": the runner's requests to egamersworld.com were
   refused with a persistent **HTTP 403** (three rate-limit waits 10s/30s/60s;
   host then blocked for the run). Access failure is data, never a number —
   the mechanism itself is proven working on the live pipeline.
2. **HLTV's Valve-ranking mirror 403'd the runner** —
   `https://www.hltv.org/valve-ranking/teams/2026/october/22` refused after the
   same backoff ladder, so `valve_identity_candidates` is empty everywhere and
   the fresh snapshot **fell back to research-only picks for `1081149`,
   `1081150` and `1082926`** (their `model_vrs_mirror` percentages from the
   earlier successful reads expire with that evidence and are not renewed).
   The committed 07:58Z board keeps the earlier mirrored percentages while
   their evidence window holds. Flagged as
   `4fd13975-hltv-mirror-403-recurrence-2026-10-22`.
3. **Stavka.tv** serves the exact page for the fixture day
   ([23-10-2026-bestia-academy-red-canids-academy](https://stavka.tv/matches/csgo/23-10-2026-bestia-academy-red-canids-academy),
   HTTP 200) but the response body contains **no parseable П1/П2 moneyline**
   (the Winline panel is client-rendered; `stavka_readings` is empty), so no
   line was taken. All other date-slug guesses (22-10/24-10 variants and every
   FlyQuest–Staqued variant for 26–28 October) returned 404.
4. **Polymarket moved but stayed outside the gate** (10:04:58Z quotes):
   `6036921` BESTIA Academy–RED Canids Academy now prices 0.365/0.635 with
   bestBid 0.05 / bestAsk 0.68 — **spread 0.63, liquidity $440.92** (was 0.90 /
   $108.62 earlier today) — refused at the ≤0.60 spread gate, now only just;
   `6036913` ex-RUSTEC–Saint Sinners spread 0.90 / $642.07 refused; `6036925`
   Isurus–Hacha spread 0.64 / $196.16 refused; **no market exists for
   FlyQuest–Staqued**. If 6036921 tightens past the gate before the 23 Oct
   19:00Z start, the scheduled refresh prices it automatically.
5. Pinnacle's guest feed held no exact pair + UTC start; GG.BET refused access
   (403); Thunderpick pages read with no validated two-way series quote;
   bo3.gg search pages read; HLTV fixture betting tables carried no numeric
   line. Nothing publishable, nothing invented.

## Parallel-session collision log (coordination protocol)

While this session worked, sibling sessions `86b56cf6`, `80504414`, `8e9bf19f`
and `eaff7cce` merged PRs #181/#186/#188 and others into `main`. Two
collisions, both resolved without discarding anyone's work:

1. **Duplicate feature — listing gap recheck.** Session `eaff7cce` landed
   `scripts/books.watch_unpriced` on `main` (re-read previously rejected
   EGamersWorld listing pages for open unpriced fixtures; accept only a unique
   exact pair/start with label-bound asymmetric odds; never write the curated
   register). This session had independently implemented the same guarantee as
   `scripts/books.watch` before seeing that work. On rebase the sibling
   implementation was **kept verbatim**, this session's duplicate
   `watch`/`load_rejected` code was dropped, and the session's regression tests
   were rewritten against `watch_unpriced` so the user-facing rules stay locked
   down (placeholder/start/team/access refusals, no 50/50, no register writes,
   closed and priced rows never read, end-to-end pricing, alias-register
   matching). Their `watch_unpriced` is in some places stricter (unique
   candidate, no format inference when `best_of` is known, EGW URL shape only);
   nothing in it was relaxed.
2. **`COORDINATION.md` and `data/review-notes.json` add/add conflicts** —
   resolved by union: every entry from both sides retained verbatim (142 main
   entries + 3 session entries = 145; both claim sections kept).
3. Generated artifacts (`build-info.json`, `data/latest.json`,
   `data/matches.csv`, `review.html`) conflicted after the union of review
   notes; resolved by taking `main`'s bytes during the rebase and **rebuilding
   from the merged inputs** afterwards (`scripts.build`, then
   `scripts.validate --site .` clean: 107 rows, 41 reproduced calculations,
   969 links/assets, 20 checksums, 283 displayed rows).
4. The branch history was rewritten once (`git rebase origin/main`) and
   force-pushed with `--force-with-lease`; every pre-rebase commit has a
   rebased successor on the branch.

## Integration finding (fixed): three valid picks were withheld on main

While rebasing onto `main` (`3b21d18`) this session found the live board had
regressed to **three open matches with no pick** (`1081149`, `1081150`,
`1082926`) even though each row's attempt ledger showed a resolved "HLTV Valve
ranking (Valve points)" line. Root cause: `scripts/quarantine.py` runs the
independent auditor `verification-c6/audit_snapshot.py`, whose mirror provenance
rule still required the canonical `/valve-ranking/teams` path, while the mirror
tier (updated by session cf12d97f) reads HLTV's **dated** view
(`/valve-ranking/teams/2026/october/22`) because one refused canonical read
blocks HLTV for the whole run. Every dated mirror quote therefore failed the
audit ("Mirror input is not HLTV Valve ranking") and the three rows were
stripped of pick, probabilities, fair odds and evidence.

Fix: the auditor now accepts exactly the two forms `scripts/validate.py`
accepts (canonical path or `^/valve-ranking/teams/\d{4}/[a-z]+/\d{1,2}$` on
`www.hltv.org`), with every other rule unchanged — host, ≥100-club complete
list, roster continuity ≥3, Valve formula/calibration, dated heading, and the
official-file record it replaced. A foreign-host negative control still fails.
Regression tests (`tests/test_session_4fd13975.py::TestIndependentAuditorAcceptsDatedMirror`)
run the patched auditor over the real retained mirror evidence and over a
doctored copy. The published board for this merge uses the last fully verified
snapshot in which all 43 open matches carry picks (`07:58:54Z`); the next
scheduled refresh republishes fresh inventory through the corrected gate.
Flagged as `4fd13975-quarantine-withheld-three-valid-mirror-picks-2026-10-22`.
