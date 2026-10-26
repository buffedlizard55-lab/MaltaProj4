# Session b964dffd — picks for every open match, incl. low-tier fixtures with no featured market (2026-10-26)

## What the user asked

Every CS2 match listed on Hotspawn must carry a pick — including low-tier
matches not covered by feature markets such as Polymarket. For matches that
cannot be resolved the same way as the featured picks, research other
information sources in order (HLTV first, then esportsbooks / esports betting
lines), originate our own line where no market exists, keep a separate
unresolved section with the limitations, and make the executive summary easy
to find and read on a phone. No Hotspawn percentage may be used as a
probability. Refresh target: every 4–8 hours.

## What was actually wrong at session start (measured, not assumed)

The committed/live board was build `2026-10-26T00:10:50Z` (snapshot
`2026-10-26T00:10:49Z`, fixtures observed `00:07:16Z`): 73 feed rows,
**11 open · 11 picks · 11 win-probability pairs · 0 unresolved**. It was
internally consistent and validated clean locally
(`scripts.validate --data data/latest.json --site .` → 73 rows, 11
calculations reproduced; 1,778 unit tests OK, 14 skipped; audits 9;
integrity 5; verification-c6 12; `tests/browser.cjs` passed).

A direct read of <https://play.hotspawn.com/lobby> at ~00:49Z showed **19
matches this week / 81 CS2 entries**: the board's 11 open matches **plus 8
fixtures absent from the snapshot entirely**:

| ID | Match | Competition | Start (UTC, from the fresh capture) |
|---|---|---|---|
| 1079201 | INOX Division vs Nemesis | NODWIN Clutch Series #13 | 2026-10-26 09:00 |
| 1079202 | FOKUS vs ex-Zero Tenacity | NODWIN Clutch Series #13 | 2026-10-26 12:00 |
| 1081159 | LFO 10 vs ex-6666 | CCT Europe 2026 Series #12 | 2026-10-26 12:00 |
| 1079203 | Metizport vs BRUTE | NODWIN Clutch Series #13 | 2026-10-26 15:00 |
| 1081160 | HAVU vs ILLYRIANS | CCT Europe 2026 Series #12 | 2026-10-26 15:00 |
| 1081162 | ex-RUSTEC vs Spirit Academy | CCT Europe 2026 Series #12 | 2026-10-27 12:00 |
| 1081163 | BakS vs Saint Sinners | CCT Europe 2026 Series #12 | 2026-10-27 15:00 |
| 1081164 | Inner Circle Academy vs Lavked | CCT Europe 2026 Series #12 | 2026-10-27 18:00 |

Session 160f03c8 independently measured the same eight at 00:52Z and flagged
them on main as `session-160f03c8-hotspawn-inventory-drift-2026-10-26`
(PR #353), asking for a re-harvest of all three Hotspawn surfaces and the
existing market/HLTV/book/model ladder. This session performed exactly that.

**Why the 00:10Z board did not have them.** At the 00:07Z observation all
three official views agreed (fixtures API 73 = CS2 page 73 = general lobby
73, `coverage: verified` in that snapshot). At this session's 00:56Z
observation all three agreed again at 81 = 81 = 81, and
`inventory_changes.added_ids` is exactly those eight IDs with
`removed_ids: []`. So the fixtures were added to Hotspawn's surfaces between
00:07Z and 00:56Z (the lobby's weekly board rolled over during that window;
160f03c8 also saw the surfaces transiently disagree, 81 vs 72, mid-rollout).
No discovery-code defect was reproduced. The visible gap for a site visitor
between ~00:49Z and the next successful publish is a freshness limitation,
not a coverage-logic one, and it is flagged for review.

## Fresh capture (the evidence everything below stands on)

Non-publishing runner capture
[40251666216](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40251666216)
(checkout `639cb79`, GitHub egress — this sandbox reaches only
GitHub/package registries). Raw receipts in `research/harvest-b964dffd/`:

* `refresh.log`: `{"coverage": "verified", "matches": 81, "priced": 19,
  "research_only": 0, "unresolved_without_any_pick": 0}`
* Snapshot `2026-10-26T01:00:10.246310Z`, fixtures observed
  `2026-10-26T00:56:34Z`, coverage counts **api 81 · page 81 · lobby 81 ·
  retained 81**, exactly the 8 IDs added, none removed.
* Quarantine: 0 rows withheld. Independent `verification-c6` row audit:
  81 rows, 0 failures (`independent-row-audit.md`, snapshot SHA-256
  `e5dfe92812c42a0979078e97a12e6f3f51d99f9fe7ec392b047f1af0d0d4301c`).
* Candidate build + `scripts.validate`: 81 rows, 19 probability
  calculations reproduced, 15 pages, 779 links/assets, 20 checksums,
  200 displayed rows. All 13 browser suites passed on the fresh candidate
  (`browser.log`), including the phone measurements below.

Result on the fresh board: **19 open · 19 picks · 19 win-probability
pairs · 0 unresolved · 0 research-only** — 8 strict Polymarket exchange
lines, 1 BO3.gg/Thunderpick bookmaker listing, 8 originated Valve-VRS model
lines, 2 originated HLTV-dated-Valve-ranking (mirror) model lines. The full
per-row ledger with source links is `row-ledger.md` in this directory.

### How the 8 new low-tier fixtures were resolved (ladder, per-row attempts)

The ladder tried, in order, for each row below: Polymarket strict → HLTV
fixture identity (page found for every one; its betting table exposes no
numeric two-way price to the collector) → Pinnacle → Polymarket wide →
Thunderpick / GG.BET access probes → BO3.gg book feed (Thunderpick lines) →
Valve VRS model (monthly file, 2026-10-05) → HLTV dated Valve-ranking
mirror model. Attempt-by-attempt records are in the snapshot
(`matches[].attempts`) and rendered per row on `evidence.html`.

| ID | Result | Pick (win %) | Why the rungs above it did not price it |
|---|---|---|---|
| 1079201 | Polymarket strict exchange | Nemesis 72.5 / 27.5 | — featured market exists (market 6186053, spread 1 pt, $5,798 liquidity) |
| 1079202 | Valve VRS model | FOKUS 74.5 / 25.5 | No exact Polymarket/Pinnacle/BO3 match; HLTV 2399117 confirms fixture, no numeric line; VRS #48 1321 pts vs #93 1066 |
| 1081159 | **HLTV-mirror VRS model** | ex-6666 67.2 / 32.8 | Polymarket alias mismatch (no fuzzy match); Valve monthly file has **no LFO 10 row**; HLTV's 2026-10-26 Valve ranking: LFO 10 #157 803 pts vs ex-6666 #118 968 |
| 1079203 | Valve VRS model | Metizport 68.0 / 32.0 | No exact market match; VRS #53 1290 vs #75 1116; duplicated "BRUTE" label (#75/#218) disambiguated by 4/5 HLTV roster overlap |
| 1081160 | Valve VRS model | HAVU 58.3 / 41.7 | Polymarket spread >60 pt ceiling; BO3 found fixture, no book line posted yet; VRS #124 937 vs #141 862 |
| 1081162 | **HLTV-mirror VRS model** | ex-RUSTEC 52.3 / 47.7 | Polymarket liquidity <$100; BO3 no line yet; monthly-file VRS refused (two ex-RUSTEC rosters tied on HLTV overlap); mirror #94 1059 vs #101 1038 |
| 1081163 | Valve VRS model | BakS 73.0 / 27.0 | Polymarket spread >60; BO3 no line yet; VRS "BAKS" #100 1044 vs #158 810 (4/5 roster overlap each) |
| 1081164 | Valve VRS model | Inner Circle Academy 70.4 / 29.6 | Polymarket spread >60; BO3 no line yet; VRS #94 1064 vs #143 862 |

## Independent verification performed by this session

1. **Re-derived all 19 probabilities from the stored evidence with code
   that shares no pipeline imports**: exchange prices normalised, bookmaker
   decimal odds de-vigged, model lines recomputed from Valve's published
   formula (`g = 1/sqrt(1+3q²RD²/π²)`, `E = 1/(1+10^(-gΔ/400))`,
   calibration `p = 0.5 + 0.7986(E-0.5)`, RD 75 — Valve's `model/fit.js` /
   `modelfit.png`). All 19 matched the published digits exactly; every pick
   is the favourite; fair odds are exact reciprocals. Pinned as regressions
   in `tests/test_session_b964dffd.py` against the archived harvest snapshot
   (rotation-proof: future boards cannot break them).
2. **Live spot-checks against official pages** (2026-10-26 ~01:05Z, this
   session, not the snapshot):
   * Polymarket event `cs2-nem-inox-2026-10-26`: live "Team Nemesis 72¢ /
     INOX Division 32¢" asks, BO3, "October 26, 2026 at 5:00 AM ET"
     (= 09:00Z) — consistent with the snapshot's 72.5/27.5 at 00:52Z.
     <https://polymarket.com/event/cs2-nem-inox-2026-10-26>
   * BO3.gg match page: Thunderpick moneyline **1.62 / 2.16** for
     NEXVOID vs Alter Ego — the exact digits in the snapshot evidence
     (de-vig 57.1/42.9). <https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026>
   * HLTV match 2399509 (LFO 10 vs ex-6666): page shows **VRS #157** (LFO 10)
     and **VRS #118** (ex-6666), lineups identical to the retained rosters,
     and a Betting table with one promo row and **no numeric two-way
     price** — confirming both the mirror inputs and the documented HLTV
     limitation. HLTV's fan vote (25/75) was not used.
     <https://www.hltv.org/matches/2399509/lfo-10-vs-ex-6666-cct-2026-europe-series-12>
   * Vendored official Valve file `standings_global_2026_10_05.md` (commit
     `eec4853d…`) carries the exact points/standings/rosters used by every
     `model_vrs` row above (e.g. FOKUS 1321 #48, ex-Zero Tenacity 1066 #93,
     BAKS 1044 #100).
3. **Executive summary / phone, measured on the fresh candidate**
   (`browser.log`, suite `browser_aeafcbe6`): at 320×568, 390×844 and
   412×915 the quicknav reads "Executive summary · 19/19 picks · 0
   unresolved (no %) · 62 feed rows are not open" with links to
   `picks.html`, `#picks-at-a-glance`, `unresolved.html`,
   `#unresolved-summary`, `#unresolved-limits`; the first pick (Off Chops)
   and **both** percentages (20.5% / 79.5%) render above the fixed tab bar
   with no horizontal overflow. All 13 browser suites passed.
4. **Publisher-gate simulation**: installing the fresh snapshot alone
   (stale root HTML) fails 22 unit tests — 21 are site↔data mismatch noise
   that pass once the root is staged the publisher's way
   (`scripts.publish_root_fallback`), leaving exactly **1 genuine
   failure**, below.

## Defect found and fixed (would have blocked this board on main)

`scripts/audit_5717f7d9.py` (an independent auditor whose tests run in both
publisher gates) routes `model_vrs_mirror` rows into `_audit_vrs` but only
accepted evidence with `provider == "Valve VRS model"`. Mirror evidence is
provided by `"HLTV Valve ranking (Valve points)"`, so **any board with a
mirror-tier pick failed the staged-root unit gate** with "Model row has no
VRS evidence" (rows 1081159, 1081162 here) — the same defect class fixed in
a different verifier on 2026-10-24. The fix binds the expected provider to
the method (a swapped provider now fails explicitly), keeps every existing
re-derivation, and adds mirror-specific checks (dated `ranking_as_of` not
after the snapshot, retained page SHA-256, HLTV dated-ranking URL,
disclosure flag). Regressions incl. tamper cases:
`tests/test_session_b964dffd.py`. After the fix,
`tests.test_session_5717f7d9` (18 tests) passes on the staged fresh board.

## Unresolved picks & limitations (the separate section the brief requires)

On this capture there are **0 unresolved open rows and 0 research-only
picks** — that is a property of this board, not a promise. The standing
limitations, each already published in the executive summary
(`#unresolved-picks`, `#unresolved-limits`, `#unresolved-summary`) and on
`unresolved.html`, and each measured again on this capture:

* HLTV confirms identity/lineups/rankings but exposed **no numeric two-way
  price** on any of the 8 new fixtures' pages (re-verified live on
  2399509); its fan vote is never a probability.
* Polymarket does not cover every low-tier fixture with a usable market:
  on this capture 4 of the 8 new rows had no exact match, 3 breached the
  60-point wide-tier spread ceiling, 1 had <$100 liquidity, 1 failed exact
  alias matching (no fuzzy matching is ever used).
* Pinnacle returned no exact fixture match for any of the 8.
* BO3.gg listed 4 of the 8 fixtures with **no active sportsbook moneyline
  posted yet** (`bet_updates is null`); Thunderpick's own site has no
  validated automated adapter; **GG.BET answered HTTP 403** after three
  rate-limit waits and EGamersWorld listing rechecks 403'd likewise —
  access limits are recorded, never bypassed.
* Valve's monthly standings file (2026-10-05) cannot resolve clubs that
  entered after its cut (LFO 10) and repeats labels for old rosters
  (ex-RUSTEC tie) — the HLTV dated mirror of the same ranking covers those,
  with its own dated page as the source, and is labelled as such.
* Model lines are estimates from standings points through Valve's own
  formula/calibration — never market prices, and labelled "not a market
  price" on every row. 1081162 (52.3/47.7) is effectively a coin flip.
* 62 past-dated feed rows remain on All Matches unpriced by design; only
  open rows carry picks. Hotspawn can add fixtures between publication
  slots (measured above); the publisher now runs every 15 minutes with a
  60-minute freshness gate and an 8-hour evidence expiry, so such fixtures
  appear within the next slot that passes its gates, and stale picks are
  withheld rather than shown.

## Irregularities flagged for review (non-blocking, published)

1. `session-b964dffd-inventory-rollout-gap-2026-10-26` — the 8-fixture
   rollout window above and its resolution by this capture (companion to
   160f03c8's open flag, which is left untouched).
2. `session-b964dffd-auditor-mirror-tier-2026-10-26` — the
   `audit_5717f7d9` mirror defect, its blast radius (any mirror board
   fails the staged-root gate), and the fix.
3. `session-b964dffd-browser-test-dirties-tree-2026-10-26` — running the
   browser suites rewrites the tracked file
   `research/session-aeafcbe6/mobile-measurements.json`; that dirtied tree
   made harvest run 40251080446's `git pull --rebase` refuse and its
   receipts were lost (run 40251666216 re-captured with a hardened commit
   step; the status receipt is `commit-step-status.txt`). Logged as a
   request in COORDINATION.md rather than editing another session's test.

## What was not verified

* Live prices after the capture minute: every percentage above is a dated
  observation with an expiry, exactly as published; markets move.
* The deleted first harvest's snapshot (run 40251080446) — its receipts
  were never committed for the reason in flag 3; nothing in this report
  rests on it.
* HLTV/Pinnacle/BO3 pages for all 19 rows by eye: three live spot-checks
  above, plus machine re-derivation and the independent `verification-c6`
  audit over all 81 rows.

## Addendum (integration, ~01:25Z): cross-session corroboration

While this session worked, main merged PRs #353 (session 160f03c8's flag),
#354 and #357 (session 77046e56). Session 77046e56's own runner harvest
(`research/session-77046e56/harvest/snapshot.json`, generated
2026-10-26T00:52:33Z) is an independent capture of the same board. Compared
row by row with this session's 01:00:10Z capture: identical open set (19),
identical pick and identical method on all 19 rows, and maximum probability
difference 0.00 percentage points on every row. 77046e56 also re-read the
1081159 mirror inputs at source (HLTV 26 October Valve ranking: LFO 10 #157
803 pts, ex-6666 #118 968 pts — the same digits), and measured that GitHub
delivered no scheduled publish run between 00:05Z and their note, i.e. the
hour-long 73-row visibility gap was scheduler delivery, not collection
(`session-77046e56-cron-delivery-gap-2026-10-26`). For 1081162, 77046e56
did not eyeball the two point values; this session eyeballed HLTV match
2399512 confirming **VRS #94 (ex-RUSTEC)** and **VRS #101 (Spirit
Academy)** and both lineups (4/5 and 5/5 against the retained rosters),
and the point digits (1059 / 1038) were parsed identically by two
independent runner captures of the same dated page eight minutes apart.
This session did not eyeball those two point digits in the ranking page's
own text.

Final integration merged `origin/main` (to PR #357) first — conflicts only
in `COORDINATION.md` (append/append; both sides kept verbatim) and
`data/review-notes.json` (union by id: 285 notes, no divergent same-id
note) — then rebuilt and re-staged the root from the newer 01:00Z capture,
so upstream review notes and research are preserved and rendered.
