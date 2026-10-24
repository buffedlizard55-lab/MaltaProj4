# Hotspawn CS2 Scout

A simple, mobile-first pick dashboard for **every CS2 fixture returned by Hotspawn's lobby feeds**. Hotspawn establishes which matches belong on the board; it **never supplies win probabilities**.

## Find the picks

**[Executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/)** · **[Updated picks](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html)** · [Unresolved & research-only picks](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html) · [All matches](https://buffedlizard55-lab.github.io/MaltaProj4/matches.html) · [TWC results & Day-5 guide](https://buffedlizard55-lab.github.io/MaltaProj4/analysis.html) · [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html) · [Sources & methodology](https://buffedlizard55-lab.github.io/MaltaProj4/sources.html) · [Evidence ledger](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html)

### Live board repair and full-coverage capture — 24 October 2026

**The public board was frozen because a test, not the data, failed.** The scheduled publisher runs the
unit suite *before* it refreshes any source. `tests/test_session_0cc1138a.py` pinned 30 lobby fixture
IDs from the 2026-10-23T09:44Z observation; Hotspawn stopped serving `1079655`, and because it was
already missing from the 11:25Z baseline, `inventory_changes.removed_ids` never named it — so the
suite could never pass again, and scheduled runs
[40025828846](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40025828846),
[40033438852](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40033438852),
[40042111432](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40042111432) and
[40062143026](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40062143026) all stopped at
that step, never reaching refresh, build or deploy. A literal `'23 Oct'` assertion in
`tests/test_session_f89bb1f8.py` was the same kind of time bomb. Parity is now derived from the
snapshot's own dated `fixture_evidence` (an absence the snapshot records is sourced; a fixture the feed
still returns and the board does not publish still fails), the day assertion compares against the row's
own start date, and `tests/test_session_e334b970.py` fails if a live-snapshot test pins a calendar day.

**Fresh live capture** (non-publishing run
[40066532380](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40066532380), clock
`2026-10-24T05:33:45Z`): **88 feed rows = 88 board rows, 25 open, 25 picks, 25 win probabilities, 0
unresolved** — 12 strict Polymarket exchange lines, 2 wide exchange lines, 2 dated bookmaker listings,
7 originated Valve-VRS lines and 2 originated line from HLTV's dated mirror of Valve's ranking. Every
row, source URL, observation time and expiry is in
[`research/session-e334b970/ROW-LEDGER.md`](research/session-e334b970/ROW-LEDGER.md); the raw response
bytes are in `research/harvest-e334b970/`, and the dated receipt is
`research/harvest-e334b970/coverage-receipt.md`. Gates: 1,211 unit tests, 9 audit tests, 5 integrity
checks, 12 independent-c6 tests, `scripts.validate` and all eight browser suites.

**A defect in the independent verifier was found and repaired.** `verify_0cc1138a.py` (which shares no
code with `scripts/`) had no branch for the `model_vrs_mirror` tier, so the 2 mirror-tier percentages on
this capture were published without being re-derived by it. The branch now rebuilds them from the
retained Valve points, and a test fails if any priced row on any tier cannot be re-derived. Flagged on
**Flagged for Review** rather than quietly patched, together with the pinned-test publish freeze, the 63
past-dated feed rows the endpoint still returns as `scheduled`, and the bookmaker access limits.

**Phone:** measured on the rebuilt board at 320×568 and 390×844 — the first pick and **both** teams' win
chances are on the first screen, above the fixed tab bar, and the bottom bar gives
*Home · Picks · Unresolved · Matches · Analysis* on every page.

### Publication-freeze measurement, independent capture and evidence — 24 October 2026

**This session measured and documented the ~18-hour publication freeze, and its capture evidence is retained.** All five scheduled publish runs delivered after 2026-10-23 12:49Z (39956197341, 39998307424, 40025828846, 40042111432, 40062143026) died in under 60s at *Unit and independent failure-mode tests*, before any refresh; the live site fail-closed correctly and served `Snapshot expired or timestamp unverified. Current picks are withheld.` Reproduced locally: `LiveHotspawnCoverage` in [`tests/test_session_0cc1138a.py`](tests/test_session_0cc1138a.py) pinned the 30 lobby fixtures observed at 23 Oct 09:44Z, the feed rotated `1081148`/`1079655` out, and the `removed_ids`-diff excuse had gone empty at the next rotation. The repairs that shipped on main are cross-session: cb16f548's [PR #245](https://github.com/buffedlizard55-lab/MaltaProj4/pull/245) (archive-pinned parity with rotation guards), d2a55add's re-deriver and freshness-strip repairs, 174afa4f's [PR #251](https://github.com/buffedlizard55-lab/MaltaProj4/pull/251) (verifier maps reviewed identity aliases from the evidence — the post-merge refusal of row `1083121`'s recorded *Projeto do KinGui* ↔ *Tropa do KinGui* alias, which would have re-frozen publication) a30d31a0's [PR #260](https://github.com/buffedlizard55-lab/MaltaProj4/pull/260) (root fallback refuses builds from older source), and — after PR #263's verifier hardening collided with PR #257's synthetic alias fixture and left main briefly RED again — 4ed657ce's [PRs #266/#267](https://github.com/buffedlizard55-lab/MaltaProj4/pull/267) (alias-gate deadlock resolved with the full dual-registration contract). This session independently found and repaired the same defects on its own branch; every competing edit was dropped at integration in favour of the merged repairs rather than layered over them (logged in COORDINATION.md).

**Independent full capture retained as dated evidence.** The non-publishing runner capture [`40067605793`](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40067605793) ([receipts](research/harvest-d2b90de7/)) produced snapshot **2026-10-24T05:57:43Z**: parity **88/88/88/88**, quarantine 0, independent audits 0 failures, unresolved-probe **0 rows to probe** — **25 open · 25 picks · 25 win probabilities · 0 unresolved** (12 strict exchange, 2 labelled wide, 2 dated BO3.gg/Thunderpick listings, 7 originated Valve-VRS lines, 2 labelled HLTV-mirror VRS lines). Session-side verification, sharing no code with the pipeline: the 25 open IDs equal this session's own 05:28Z lobby read 1:1 ([table](research/session-d2b90de7/lobby-read-2026-10-24T0530Z.md), crowd votes recorded as refused context); the vendored Valve standings file is byte-identical to Valve's pinned commit `eec4853d…` (sha256 match via api.github.com); Polymarket market `6075573` re-read live through the Gamma API (moneyline, exact pair/start, accepting orders); both BO3.gg lines de-vig to the published digits exactly (1.60/2.17 → 57.6/42.4; 1.001/12 → 92.3/7.7); HLTV's dated 24 Oct Valve-ranking view confirms #102 Spirit Academy 1030 pts and #151 LFO 10 819 pts with matching rosters, and both mirror probabilities re-derive by hand from Valve's published formula. The 23 Oct lobby/feed count mismatch (94 vs 92) rotated away — both read 88 on this capture, and main's next capture read 92/92/92/92 — while its structural note stays flagged. Offline regressions pinning these receipts: [`tests/test_session_d2b90de7.py`](tests/test_session_d2b90de7.py). Full log: [`research/session-d2b90de7/REPORT.md`](research/session-d2b90de7/REPORT.md); flagged notes `session-d2b90de7-publish-deadlock-2026-10-24` and `session-d2b90de7-coverage-measurement-2026-10-24`.

### Finding the picks on a phone, and a guard against the layout drift — 24 October 2026

**The board was complete; the first screen did not say where it was.** Measured with headless Chromium
on the 06:16Z snapshot at 320×568, the always-visible executive summary rendered after all 31 cards.
While this session was measuring its own five-destination map, session 4ed657ce landed a measured
compact summary row (`#exec-quicknav`) on `main` first — a 48px row above the pick list carrying the
updated-picks link, the unresolved-limits link and the live counts, hidden on desktop where the full
bar is already high up, with a browser receipt in `research/session-4ed657ce/`. This integration
adopts that row and drops the duplicate rather than stacking two navigation blocks on the first
screen, and its own tests pin the contract (one nav, never folded, before the pick list, in-site
links, counts read from the snapshot).

**The served stylesheet cannot drift silently again.** The root `assets/style.css` — the file the
legacy `main:/` Pages source actually serves — is only regenerated by a staged publish. A single
missing `}` there nests every later phone rule inside a short-phone media query, which is how the
phone layout broke earlier on 24 October. `scripts/stage_legacy.ensure_stylesheet_parity()` now
repairs that drift while staging, and `scripts/validate.validate_stylesheet()` fails any build whose
served stylesheet is unbalanced or differs from the canonical `site/assets/style.css` (unit-tested for
a missing and an extra brace). Both copies are byte-identical and balanced on this tree.

**Every match, rung by rung.** `scripts/coverage_233b8a0e` republishes, from each capture, how many
open rows came from each step of the ladder plus the full unresolved ledger (HLTV first, then
esportsbook lines) with each row's own recorded reason and attempts. On this snapshot: 92 feed
records, 61 past-dated, **31 open, 31 picks, 31 win probabilities, 0 unresolved** — 16 strict
exchange, 3 labelled wide exchange, 3 researched bookmaker listings, 6 from our own Valve-VRS model
line, 3 from the same model on HLTV's dated view of Valve's ranking. The unresolved section is
rendered when the count is zero too, because "nothing is missing today" is not a claim about tomorrow.

Gates on the integrated tree: the full unit suite, audits, integrity, verification-c6, the validator and all nine Chromium suites, audits, integrity, verification-c6, the
validator and all nine Chromium suites.

### Final full-coverage and phone verification — 23 October 2026

Fresh non-publishing runner capture [39935049772](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39935049772) re-read the official sources and passed refresh, quarantine, independent evidence replay, build, validation and every browser gate. Its snapshot was generated at **2026-10-23T09:58:40Z** from fixture evidence observed at **09:55:02Z**. Hotspawn API / CS2 page / general lobby / retained board parity is **92 / 92 / 92 / 92**: **30 open, 30 picks, 30 win probabilities, 0 unresolved**. The 62 not-open feed records remain visible but are not presented as current picks.

The open-board method mix is **20 strict exchange lines, 3 labelled wide-exchange lines, 2 dated bookmaker listings and 5 originated Valve-VRS model lines**. Every row and its source URL is in the [fresh row ledger](research/harvest-9b97d585/row-ledger.md); the exact source response fields are retained in [snapshot.json](research/harvest-9b97d585/snapshot.json). Wide rows are low precision, not featured certainty: Metizport–BakS (34-point spread), Color–ex-Zero Tenacity (58 points, with the opposite VRS favourite retained for comparison), and Ground Zero–Off Chops (37 points). GG.BET and EGamersWorld access failures and the two book listings’ observation times/expiries remain disclosed.

**Phone repair:** at 320×568 the first pick previously sat at y=835 and its probabilities at y=696. The short-phone board now puts the match first and the pick directly below the teams: pick y=367.7–391.0, both probabilities y=441.0–467.3, above the fixed tab bar at y=507. Percent signs no longer wrap, and filters still work after the cards. The executive summary’s runtime/static prose now agrees in all-priced, research-only and singular-count cases; it no longer says “0 of them carry no win probability” when every row is priced.

Start on the **[executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/)**, tap **[Updated picks](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html)**, or use the phone bottom bar. The separate [Unresolved & non-market page](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html) and the executive summary’s limitations section remain present even when the current unresolved count is zero. Scheduler delivery is still best-effort: a dated Actions API gap is published on **Flagged for Review**, while push and manual-dispatch refreshes use the same verified pipeline.

**Integration:** the newer main run [39935797381](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39935797381) (snapshot **10:05:50Z**, fixture evidence **10:02:13Z**) is the published candidate, with the same 92/30/30/30 coverage and method mix. The combined candidate passed **1,146 unit tests**, all independent audits, both validators (**821 links/assets**) and all eight browser suites, including PR #223's freshness-clock checks and PR #218's HLTV recent-form fallback.

### Feed scope, lobby parity and a flagged delivery measurement — 23 October 2026

**The picks were already complete; what was missing was the explanation.** Read live at 09:47Z, the
Hotspawn lobby listed 30 open CS2 matches and all 30 appear on the board by fixture ID — 30 picks,
30 win probabilities (20 `exchange`, 2 `bookmaker_fallback`, 1 `exchange_wide`, 7 `model_vrs`),
0 unresolved. Two things a reader could not previously see are now on the page:

- **92 feed rows are not 92 matches.** The fixtures endpoint still returns 62 rows whose scheduled
  start predates the snapshot's own observation clock (26 Jun – 23 Oct 08:00Z) while carrying
  `status: scheduled`. *All matches* now opens with a scope panel (`#feed-scope`) stating
  "92 feed rows = 30 open matches + 62 past fixtures", links the lobby and the endpoint, and the
  executive summary names the same count. Those rows are labelled **Past fixture · not in the lobby**
  and never priced. A snapshot without past-dated rows renders no panel and no sentence
  ([`scripts/build.py`](scripts/build.py), 16 tests in [`tests/test_session_51a9c98a.py`](tests/test_session_51a9c98a.py)).
- **The lobby's clock is UTC−4.** Its cards read "Oct 23, 15:00" for fixture `1082925` whose feed
  value is `19:00:00Z`; the lobby's own countdowns agree with the feed, so this is US Eastern
  daylight time, not a conflicting start. The board publishes the feed's UTC values and converts
  nothing. Flagged on **Flagged for Review** with both sources.

**Independent line spot-check.** Polymarket `6036897` (Nuclear TigeRES vs ILLYRIANS) was re-read at
09:44Z at `0.85 / 0.15` with bid 0.84 / ask 0.86 against the board's 08:28Z observation of
86.5% — same direction, and a reminder that the published observation time is the price. EGamersWorld
shows `1.12 / 5.8` for the same fixture (de-vigged ≈ 83.8%), i.e. today's low-tier books do publish
two-way prices for these matches.

**Flagged, not fixed:** between 07:20Z and 09:55Z GitHub delivered exactly **one** `schedule` event
(07:20:51Z) while the two crons asked for ~25 ticks, and the refresh watchdog received none at all —
its listed runs are all pushes. The board therefore refreshes when a merge runs the pipeline; the
eight-hour evidence window still withholds an expired snapshot rather than presenting it as current.
A follow-up for the owning session is an external trigger, since a denser cron cannot restore a
dropped event. Full log: [`research/session-51a9c98a/REPORT.md`](research/session-51a9c98a/REPORT.md).

### Publish-outage fix and full-coverage pass — 23 October 2026

**The site was serving an expired board with 0 picks; the cause was a test, not the data.** The scheduled publish workflow runs the unit suite *before* it refreshes any source. Two tests pinned the *tier label* one historical snapshot happened to record: fixture `1081149` legitimately moved `research_rank_single` → `research_vrs_single` when Valve's official standings resolved FORZE Reload, so scheduled runs [`39871808909`](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39871808909) (23:26Z) and [`39886171791`](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39886171791) (01:49Z) failed at *Unit and independent failure-mode tests* and never reached refresh, build or deploy. The committed snapshot froze at `2026-10-22T20:15Z`, every pick passed its deadline, and the public page rendered "20 open · 0 with a pick · 0 with a win probability" beside a stale sentence claiming 23 picks.

The assertions now check the invariant (any `research_*` tier, a pick from the fixture's own teams, no percentage, no fair odds, explicit limitation), [`tests/test_session_f0814674.py`](tests/test_session_f0814674.py) fails if a test pins a research tier again (13 tests, including the full-coverage and executive-summary/phone contracts), and the executive summary's completeness sentence is regenerated at runtime from the same counts as the numbers so prose and figures cannot disagree.

**Fresh runner capture** ([`research/harvest-f0814674/`](research/harvest-f0814674/REPORT.md), run 39902922561): fixture evidence **2026-10-23T04:55:44Z**, 92 Hotspawn CS2 fixtures, **30 open, 30 with a pick, 29 with a reproduced win probability, 0 without a pick** (17 exchange, 2 wide exchange, 9 Valve VRS model, 1 HLTV dated Valve-ranking mirror, 1 research-only). Independent audit: 92 rows, 0 failures. The single blank percentage in that capture was `1082860` FlyQuest vs Staqued, where HLTV carries no numeric two-way line, Polymarket `6066520` spreads 0.88 (refused by the ≤0.60 gate) and Valve's official file lists FlyQuest but not Staqued. **A later capture the same morning (05:05Z, committed by session 071642e7 in the 05:22:51Z board) did find a real listing for that fixture** — EGamersWorld `4kaAQWgKEx` carrying Thunderpick `1.001 / 12.0` at the exact UTC start, corroborated by Rainbet, Underdog, CocoBet, FanDuel and Fanatics — so the published board is now **30 open · 30 picks · 30 with a win probability, 0 unresolved**. Nothing was invented to close that row; it closed because a book published a real pair.

**Phone board fix.** The `picks.html` board now opens with the match cards on a phone: measured at 390px the first pick sat at y=1370 (blurb, shortcut chips, long notice and the full filter stack came first) and now sits at y=461, with its probabilities at y=588 and the pick at y=662 inside the 844px first screen. The filter bar is a two-column block above the board, the chips and the explanatory notice follow it, and desktop order is unchanged. A new browser suite (`tests/browser_f0814674.cjs`) fails if the first pick or its probability leaves the first screen at 320/390px, if filtering breaks, or if the summary's completeness sentence disagrees with its own counters.

**Delivery:** [PR #196](https://github.com/buffedlizard55-lab/MaltaProj4/pull/196) merged as `a030476` at 2026-10-23T05:11:43Z. Main run [`39904410713`](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39904410713): `verify-build` success (the previously failing unit step now green), `deploy` success with the **"Verify live Pages bytes match this exact build"** step, plus the guarded root-fallback commit `547be25`. Live check after deployment: `build-info.json` serves 92 rows built `2026-10-23T05:22:51Z`, and the executive summary renders **30 open · 30 with a pick · 29 with a win probability · 0 unresolved** with its in-site pick links on the first screen. Gates on the merged tree: 974 unit tests OK, 9 audits, 5 integrity, 12 independent-c6, `scripts.validate` (92 rows, 29 calculations, 839 links/assets, 20 checksums, 231 displayed rows) and four browser suites (32 viewport/accessibility scans + phone/expiry scenarios).

### Session 4fd13975 verification pass — 22 October 2026

A line-by-line verification and unpriced-row research pass on the integrated board. **Live coverage cross-check:** the Hotspawn lobby sidebar at ~08:50–09:00Z listed all 23 CS2 tournaments with counts that match `data/latest.json` **exactly** (107/107 fixtures; e.g. CCT SA Series #7 9, DraculaN Season 7 9, Urban Riga Open #5 12, DFRAG Invitational 4). **Every open match has a pick (43/43); 41 carry reproduced win probabilities; the two blank rows stay blank on purpose:** `1082925` BESTIA Academy–RED Canids Academy and `1082860` FlyQuest–Staqued were re-researched source by source this session (HLTV betting tables carry no numeric line and fan votes are refused; Polymarket `6036921` spreads 0.90; Pinnacle/GG.BET/Thunderpick/bo3.gg/Kalshi unavailable or empty; EGamersWorld serves the 1.8/1.8 placeholder; Valve's 2026-10-05 file lists BESTIA Academy at #215 with an exact 5/5 roster but neither RED Canids Academy — the main "RED Canids" roster shares 0/5 players with the Academy lineup — nor Staqued, whose five players are absent from the file and from the 21 Oct Asia regional). Publishing a percentage for either row would require inventing one, so both keep research-only picks, blank percentages and source-linked limitations in the executive summary's own unresolved section. Full source table and receipts: [`research/session-4fd13975/REPORT.md`](research/session-4fd13975/REPORT.md). The gap-recheck watcher (sibling session's `scripts/books.watch_unpriced`, kept verbatim on rebase) now re-reads previously rejected listing pages every refresh, so these rows upgrade themselves the moment a book publishes a real pair; this session's regression tests lock the refusal rules down. Gates on the merged state: **920 unit tests**, 9 audits + 5 integrity + 12 independent-c6, auditor suites (35 passed / 3,053 checks / 0 failures), `scripts.validate` (107 rows, 41 reproduced calculations, 969 links, 283 displayed rows), and four browser suites (32 viewport/accessibility scans + 19 expiry/quote/phone scenarios). **Delivery: [PR #192](https://github.com/buffedlizard55-lab/MaltaProj4/pull/192) merged 2026-10-22T10:47Z as `df5a055`; the Pages run passed verify-build, deploy and the exact live-bytes check, and the live site serves this board with all open matches picked.** Five flagged items are on **Flagged for Review** (PR #176 orphaned merge commit; refused-listings field inconsistencies; HLTV fan votes refused; a dated flag for the recurring HLTV Valve-ranking-mirror 403; and the quarantine-withheld-picks incident, fixed through the merged PR #194 with a real-evidence regression test kept here) (archived runner evidence in [`research/harvest-4fd13975/`](research/harvest-4fd13975/)). A live runner harvest (run 39757267589, 10:01Z) also proved the gap-recheck watcher end-to-end in the pipeline (EGW refused the runner with a dated 403 — logged as data, not a number) and recorded Polymarket `6036921` tightening to spread 0.63 / $441 liquidity on `1082925`, just above the ≤0.60 gate; if it tightens further the scheduled refresh prices the row itself.

### Integrated release candidate — 22 October 2026

The combined candidate covers **all 104 retained fixtures; all 43 open matches have a pick, 41 with sourced numerical estimates and two explicitly research-only with blank percentages**. The method mix is **24 strict exchange + 2 wide exchange + 2 book/listing + 9 official-file VRS + 4 dated HLTV Valve-point mirror models**. Actual fixture evidence is **08:56:52Z**, snapshot **08:58:49Z** — never the rebuild clock. Current row/ID/source/math replay is recorded in [the release-candidate receipt](research/session-eaff7cce/release-candidate-receipt.json); the earlier 107-row exact-byte archive is retained as dated history, not relabelled as a new read.

**919 unit tests (52 own), independent 9+5+12 suites, 3,041 acceptance checks with zero failures/advisories, 104 row replays, 41 calculations, 15 pages, 964 links/assets and 20 checksums** pass, along with the complete phone/accessibility/expiry browser suites. Source/blank guards also pass later-expiry and zero-open replays without fabricating a pick. Every concurrent source fix, note, identity and native disclosure is preserved. The real STAVKA Nuxt reader remains bounded and source-clock preserving; any listing estimate is not an independently verified operator quote. [Full integration audit](research/session-eaff7cce/REPORT.md).

PR #177 is **actually merged**. The newer combined release also integrates the completed #185 source capture and latest main through #181. A stale pre-fix main Actions run is holding publication; a deliberately labelled one-shot main queue reset follows current-head CI. **Live delivery is not claimed until the public bytes are verified.**

### Earlier exact-byte source audit — 22 October 2026, 07:49 UTC

The fresh normal-collector capture reconciles **all 107 CS2 IDs** across Hotspawn's API, CS2 page and lobby. At that observation **46 were open: 39 supported numerical estimates (27 external market/listing / 12 originated official-file VRS), six qualitative picks with blank percentages, and one unresolved fixture**. All 107 retained non-crowd rows match exact official response bytes; independent row auditing reports zero failures. Counts are dated; build/browser checks close rows at their original start/lock/evidence deadline, rather than renewing them at publication. [Full row/source audit and limitations](research/session-eaff7cce/REPORT.md) · [exact source archive](research/session-eaff7cce/capture/evidence-index.json).

**At the 07:49Z capture, Projeto do KinGui–Martians remained blank**, not matched to exchange/HLTV's `Tropa do KinGui` by guessing: official team/fixture roster records conflict. The six other no-percentage rows in that capture were explicitly research-only. The secondary STAVKA winner-panel lead is not accepted as verified operator odds. Those dated findings remain on **Flagged for Review**; the integrated snapshot above preserves subsequent independently reviewed identity evidence, rather than freezing the old unresolved result.

The phone landing page retains every pick/source but folds duplicate guides, boards and long research ladders into native accessible disclosures. A 46px **Updated picks** tap target is on the first screen at 320×568 and 390×844; the current first in-page pick list is tested within 1700px at both phone widths (historical pre-fix y=3186 at 390px). Hash links reveal all ancestor disclosures. Freshness now means actual fixture evidence, not a later failed attempt. Existing expiry, search, category pages and exports are preserved.

The scheduled collector also revisits previously rejected EGW URLs for current uncovered fixtures, with exact identity/start/format, asymmetric label-bound odds and strict real-source clocks. No placeholder price, missing observation or denied access can create/renew a line. The 07:49 runner's EGW 403 is recorded; no live coverage increase from the watcher is claimed. Publication/merge receipts are recorded in [COORDINATION.md](COORDINATION.md), not inferred from a local build.

### Earlier release audit — 22 October 2026, 02:xx UTC

**07:58 UTC update (session `cb867c3c`):** On the current **107-record, 43-open** morning board (`2026-10-22T07:58:54.670274Z`), **all 43 open matches carry a verified pick (`0` unresolved)**: **41 of 43 (`95.3%`) publish full reproducible numerical win probabilities** (**22 strict Polymarket exchange, 3 wide-tier exchange, 3 bookmaker lines including live Winline `1.90 / 1.80` on `1079654 ex-Zero Tenacity vs ex-RUSTEC`, 10 official-file VRS model lines, and 3 live `model_vrs_mirror` lines on `1081149`, `1081150`, and `1082926` from HLTV's dated Valve ranking**) plus **2 qualitative HLTV research picks with blank percentages (`1082925`, `1082860`)**. Primary-source 5/5 active-roster continuity (`ALLE, ckzao, drg, xureba, lash` across [HLTV 2399904](https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7) and [EGamersWorld 3j3hkufF0](https://egamersworld.com/counterstrike/match/0U32SId-H/projeto-do-kingui-vs-martians-esports-3j3hkufF0)) resolved `1082919 Projeto do KinGui vs Martians` (`75.0% / 25.0%` via Polymarket `6033256`, with Winline `1.06 / 7.26` backup), `scripts/books.py` adds automated `stavka.tv` Winline moneyline re-observation, and `scripts/refresh.py` adds a Chrome-TLS (`curl_cffi`) `HTTP 403` transport fallback plus explicit `expires_at` stamping. Full write-up: [`research/session-cb867c3c/REPORT.md`](research/session-cb867c3c/REPORT.md).

**Release verified:** [PR #151](https://github.com/buffedlizard55-lab/MaltaProj4/pull/151) is merged; [Pages publication 39712021835](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39712021835) passed deployment and exact live-byte checks. Independent 02:43 UTC reads confirmed the 02:40 UTC published snapshot: **97 records, 35 open picks, 29 numerical estimates (14 market-derived / 15 original VRS), six qualitative picks with blank percentages**. All counts are dated and expired recommendations are withheld automatically. [Delivery receipt and limitations](research/session-ac4743a3/release-receipt.json).

The retained `2026-10-22T02:17:34Z` integrated refresh independently agrees on **97 CS2 records** across Hotspawn's API, CS2 page and lobby. Of **35 open matches, all 35 carry a supported pick**: **12 market-derived estimates (10 strict exchange, 1 Pinnacle API, 1 explicitly secondary researched listing), 17 labelled original VRS estimates and 6 qualitative picks with blank percentages**. All 29 calculations replay; all 2,328 retained non-crowd fixture fields match exact official response bytes. The new HLTV Valve-ranking mirror returned a recorded 403 to the runner, so **no mirror probabilities or projected 32/35 coverage are claimed**. These are dated coverage numbers, not guaranteed results or future delivery.

**Picks now includes every open match**, not just numeric rows. Research-only picks, phone cards, hero/queue picks and desktop rows all have finite evidence/start/lock deadlines. Missing or expired evidence withholds the recommendation rather than displaying an old team or percentage. Historical Zetta source/round and Off Chops arithmetic notes were corrected with source links.

The six remaining numeric gaps, postponed benched gods bracket slot, ambiguous ex-RUSTEC roster, source-access restrictions and Pages-setting permission limit remain visible on **Flagged for Review**, not silently filled in and not merge blockers. See the [session audit and exact source archive](research/session-ac4743a3/REPORT.md) for per-match reasons, reproducible evidence and the publication receipt.

The home page opens with a **freshness strip** — the exact snapshot time, the published re-check cadence, how many open matches carry a pick and how many do not, and three direct links to the pick board, the in-page pick list and the unresolved section — followed by four destination cards. When a snapshot passes its eight-hour evidence window the strip turns red and says so in words, so a delayed refresh can never look like a live board.

Both teams' probabilities, our fair decimal lines, the selected team and primary-source links are explicit. Phone layouts use readable match cards and a persistent bottom navigation. Search and tournament/status filters work without a login. All matches defaults to open entries; select **All entries** to see retained non-open records too.

**Full fixture coverage with tiered picks.** Every open fixture is attempted in a fixed order and its outcome is published: strict exchange gate → HLTV identity research → Pinnacle bookmaker line → labelled wide-quote tier → **researched book-listing line** (a dated, identity-verified two-way price read from a book's own listing page, which outranks our own model) → **our originated VRS model line** (Valve's official standings points through Valve's own published formula and calibration, with HLTV lineups confirming each roster) → **the same model from HLTV's dated view of Valve's ranking** (`model_vrs_mirror`, [scripts/vrs_mirror.py](scripts/vrs_mirror.py)) where Valve's monthly file cannot resolve a club: identical points, formula, calibration and roster rule, read from HLTV's dated page, which is linked on the row together with the official filing date it stood in for → HLTV-verified ranking tiers that can produce a **research-only pick with no published percentage** → a final one-sided Valve standings tier (exactly one team listed in the official global standings, the other genuinely absent; pick only, no numbers). If none applies, the row stays blank and unresolved. The executive summary links the pick board, the unresolved section (every pick without a market line, with its limitation) and the tournament analysis (day 1 to day 5 of the Thunderpick World Championship, including the Saturday 17 October semi-final guidance and the Sunday 18 October bracket) directly, and it carries its own "Unresolved picks & their limitations" notice that counts the TWC items with no price and links to them; phone layouts use tappable cards plus a persistent bottom navigation bar, and the summary opens with a **Picks at a glance** list — every open match in start order with its pick and percentage, one tap to its evidence, sized for a phone — plus a "then next" queue of the following picks with their prices and a jump bar to today's picks, the later board, the unresolved section and the coverage line. The final-day guide now records the verified day-four results (**FURIA 2-0 Aurora; BETBOOM 2-1 Falcons**) and the populated Sunday matchups (**Aurora–Falcons 11:30 UTC; FURIA–BETBOOM 15:00 UTC**). The separately sourced Thunderpick match-page observation (17 October 20:20:54 UTC) supports Falcons **65.53%** and FURIA **68.24%** after de-vigging. These are dated, single-book research prices—not submitted Hotspawn picks, a multi-book consensus or an automated Thunderpick feed. The displayed quote blocks expire at 18 October 04:20:54 UTC, before either match; later current prices are not promised. The guide distinguishes schedule/map load from unmeasured fatigue, does not treat Aurora's July rebuild as a fresh roster shock, and flags missing crowd/streak information rather than claiming an optimal leaderboard strategy. Earlier pre-match analysis is explicitly archived; its historical TBA notes and odds are not live recommendations. Every unresolved final-day item links its evidence and limitation. The project is independent of Hotspawn and betting operators and does not place bets or submit picks.

**Every open match carried a pick on 21 October 2026.** The 12:47Z snapshot listed 81 Hotspawn CS2 records, 19 of them open. All 19 have a selected team: 18 also publish a win probability (14 from a betting market, 4 from the originated VRS model) and one is a labelled research-only pick with no percentage, which is shown in the executive summary's [Unresolved picks & limitations](https://buffedlizard55-lab.github.io/MaltaProj4/#unresolved-summary) section with its reason. Two of the gaps that day existed only because the exchange spells a team differently from the feed — Hotspawn `ex-CYBERSHOKE` is Polymarket/Liquipedia `CYBERSHOKE Esports`, and Hotspawn `flacons` is `Team flacons`. Both are registered in [the identity register](data/identities.json) as label mappings anchored on the exact opponent pair and the exact 2026-10-21T15:00:00Z start across HLTV's match page, HLTV's team page, Liquipedia's event page and the Polymarket event; the next refresh priced them from the exchange at 82.0% and 95.5%. The remaining unpriced row at 12:47Z was Zetta vs LOS NINOS (22:00Z). It had no accessible two-way line at that minute: EGamersWorld served the identical 1.8/1.8 placeholder, Pinnacle had no listing, and Valve's standings omit LOS NINOS so the model line could not run. Polymarket's only event at that start is labelled `Alianza Lima Esports vs Los Niños`; **that label was later verified rather than guessed** — the row is now priced from it at 84.5% because the same five-player Peruvian squad played the event under the Alianza Lima tag, recorded in [the identity register](data/identities.json) with HLTV match 2399865, Polymarket event 1227336 and the roster comparison as its basis. The residual risk that the register applies that alias to *any* future fixture is open on [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html) as `c828a275-alias-scope-risk-2026-10-22`. Every rejected listing and every disabled adapter stays visible there instead of being filled in.

**The last unpicked fixture is now resolved (21 October 2026).** On the 19:57Z board all 13 open matches carried a pick except `benched gods vs TitanFlow` (fixture 1081597, CCT Europe 2026 Challengers #8, 22 October 11:00Z). HLTV publishes that bracket slot without team names, so there was no lineup; Valve's official standings of 2026-10-05 list `benched gods` **twice**, so Valve's own roster-continuity rule could not choose a row; and EGamersWorld quotes both sides at an identical 1.80/1.80, the placeholder pattern this project already refuses. The collector now also reads each club's **own HLTV team page**, resolved only by an *exact* label from HLTV's public search and re-checked against the page's heading, and records its published starting five. benched gods' five (Wign, K014NZ, facer, norescue, yoyoS2) match the 811-point Valve row 5/5 and the other row 0/5, which resolves the duplicate; TitanFlow is in neither Valve's global nor Valve's Europe file of the same date. The row therefore publishes `benched gods` as a **research-only pick with no percentage**, prints both team-page links, the Valve standings link and the observation times beside it, and states its limits: identity rests on two team pages rather than an HLTV fixture page, Valve may add TitanFlow in a later publication, and no book line was accepted. Full write-up: [session 1395f539](research/session-1395f539/REPORT.md).

**Every open match still carried a pick on 22 October 2026, and the research-only rows are shrinking.** The 00:55Z board listed 97 Hotspawn CS2 records, 35 of them open: all 35 carried a selected team, 28 published a win probability and 7 were labelled research-only with no percentage. Same-day research by concurrent sessions closed most of that gap: K27 vs NEXORA (22 Oct 17:30Z) now carries a labelled bookmaker-fallback line from the researched EGamersWorld book listing for the exact pair and UTC start (NEXORA 8.1 / K27 1.021, de-vigged K27 88.8% / NEXORA 11.2%), independently corroborated within 0.8 points by a СТАВКА ТВ named-operator panel (Betcity 7.80 / Melbet 1.06) and a Kushvsporte panel (1.04 / 8.2); the same morning's 02:17Z snapshot publishes 29 of 35 open rows with a percentage. Six fixtures still publish no percentage — Morningstar vs NEXVOID, benched gods vs TitanFlow, ex-Zero Tenacity vs ex-RUSTEC, FORZE Reload vs LFO 10, ex-RUSTEC vs Saint Sinners and FlyQuest vs Staqued — because every checked listing serves the identical 1.8/1.8 placeholder or nothing at all, and the labelled model_vrs_mirror tier from HLTV's dated Valve ranking fails closed on them (standings label ties, absent clubs). Their research picks keep blank probabilities, dated refusals are in [data/book-receipts.json](data/book-receipts.json), and every limitation and collision log stays visible on [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html) instead of being filled in.

**Publication outage fixed (20-21 October 2026).** Every scheduled refresh on `main` from 2026-10-20T13:02Z to 2026-10-21T10:00Z failed in the unit-test step because three tests in `tests/test_session_133fe7ca.py` compared a hard-coded 2026-10-20T12:00Z fixture start with the wall clock; once that start passed, the row was correctly `not_open` and the pick tiers declined to act. The live site therefore served a 2026-10-20T07:44:51Z build for 29 hours. The tests now pin their own observation instant, assert the row is open first, and a regression test proves the scenario still exercises an open fixture.


## Independent verification of the published board (22 October 2026)

The board was re-derived line by line from its own retained receipts, not from its summary. [`research/session-c828a275/audit_board.py`](research/session-c828a275/audit_board.py) reads a snapshot and re-checks, for every open fixture: that the pick is one of the two named teams and the higher-probability side; that each published probability equals the stored raw exchange price to 1e-9, or reproduces from Valve's published formula and the vendored official standings file; that the two sides sum to 1 and the fair decimal odds are their reciprocals; that a market row's raw outcome names are the two fixture teams, directly or through a register entry that carries a primary source and a written basis; that the raw market start equals the Hotspawn start, the market is open and accepting orders, liquidity is at least 100 and the spread is inside the gate its tier claims; that the row's expiry is the earliest of the fixture-observation window, the lock, the start and every quote observation/update window; and that every row carries at least one https link on a known official host. Result on the 2026-10-21T21:27Z snapshot: **13 open rows, 13 picks, 11 percentages, 2 research-only, 0 without a pick, 223 checks, 0 failures**. Re-run after the 22 October refresh widened the board: **35 open rows, 35 picks, 28 percentages, 7 research-only, 0 without a pick, 587 checks, 0 failures** ([`board-audit.json`](research/session-c828a275/board-audit.json) is that run). Reproduce either with `python research/session-c828a275/audit_board.py data/latest.json`.

**Where the 28 percentages and 7 research picks come from** (2026-10-22T01:28Z board): 7 strict exchange lines (Polymarket), 1 labelled wide exchange line, 1 Pinnacle bookmaker line whose probabilities re-derive from its own decimal odds and 7.3% overround, 19 originated lines from Valve's official standings through Valve's published formula and Valve's roster rule, plus 7 research-only picks with **no percentage** — 4 one-sided HLTV rankings, 2 two-sided HLTV rankings and 1 one-sided Valve listing. Each of the 7 no-percentage rows states its own blocker, and the blocker was re-derived rather than copied: in 4 the opponent is genuinely absent from Valve's 380-team global file, in 2 the *same* team name appears twice in that file with the current lineup sharing exactly three players with both rows, so Valve's own continuity rule cannot choose between 1,066 and 824 points (that choice is worth roughly 51% versus 74%, which is exactly the difference a pick must not invent), and in 1 both problems apply. No source tried produced a two-way price for any of them (Polymarket, Pinnacle, Thunderpick, GG.BET, HLTV fixture pages). Full write-up with sources: `c828a275-no-percentage-rows-and-how-to-close-them-2026-10-22` on [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html).

**Two documentation defects found and fixed by this pass**, both of the kind that makes a reader distrust the page rather than the arithmetic. (1) This file still said the Zetta–LOS NINOS Polymarket market was "deliberately unused"; the board had already priced it after the alias was verified, so the sentence above was untrue and is corrected. (2) Five open rows (`1081598`, `1082858`, `1082859`, `1082860`, `1082861`) carry the lobby URL as their Hotspawn link, because the lobby's permalink map has no entry for them; each still carries its HLTV fixture page and, where priced, the Valve standings link, so no row is source-less, but the per-match Hotspawn page is missing rather than absent-by-design. Both are recorded with evidence in [`research/session-c828a275/REPORT.md`](research/session-c828a275/REPORT.md).

**Scope of this verification, stated plainly.** This sandbox had no outbound internet except `github.com`, `api.github.com`, `pypi.org` and `registry.npmjs.org`, so no price was re-fetched here: every number above was re-derived from the receipt the collector stored, and the fetch itself is exercised by the scheduled workflow on GitHub-hosted runners. A receipt can prove internal consistency and identity; it cannot prove that an operator's page still shows the same price, which is why every row expires on its own observation window.

## Evidence and calculations

1. Reverse-engineer only Hotspawn's public page data: compare the [requested lobby](https://play.hotspawn.com/lobby), [CS2 page](https://play.hotspawn.com/cs2-pickems) and [exact tenant-1 scheduled-CS2 query](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1) found in its public JavaScript. Compare IDs **and primary fields**, not just a card count. Retain all returned tiers, including past scheduled records; do not call them upcoming or completed without evidence.
2. Discover CS2 in [Polymarket's official registry](https://gamma-api.polymarket.com/sports) and paginate active events. Require a whole-match moneyline, two exact matched teams, exact UTC start, fresh observation/update, open accepting market, finite prices, two-sided quote, at least $100 liquidity and spread no greater than 25 percentage points. Known Hotspawn series format must agree. These quality thresholds are project policy, not proven forecast calibration.
3. **Only missing picks** enter fallback research: [HLTV](https://www.hltv.org/matches) first (identity, rankings, lineups), then [Pinnacle's official public esports lines](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight) (before the wide exchange tier, because a sharp bookmaker line outranks a wide quote), then researched book-listing receipts (a dated, replayable two-way price from a book's own page, captured by hand where the site refuses the automated runner; the scheduled refresh re-reads each retained listing and renews the observation only when the page re-confirms the exact pair, UTC start and an asymmetric two-way pair — an identical placeholder pair such as 1.8/1.8 is a recorded rejection, never a 50/50), then Thunderpick/GG.BET access checks. Additional investigation covers Rivalry, Stake and official organization identities. Access checks are not presented as functioning quote adapters. No access restrictions are bypassed.
4. Produce **our calculated fair lines**: for decimal odds `d₁,d₂`, let `qᵢ=1/dᵢ`, then `pᵢ=qᵢ/(q₁+q₂)`. For exchange outcome prices, normalize the two weights to sum to one. Our fair decimal price is `1/pᵢ`; the pick is the larger probability. A genuine equal-price pair has no directional edge. These are derived market estimates, not bookmaker consensus or a calibrated independent performance model.
5. Keep accepted featured/primary picks; fallbacks do not overwrite them. Never substitute Hotspawn/HLTV fan votes, guessed aliases, academy squads, an HLTV-rank-to-probability formula or a default 50/50. Narrow organization-name mappings have primary links in [the identity register](data/identities.json); roster continuity is not inferred.
6. **Wide-quote tier** (`exchange_wide`): a two-sided exchange quote that fails only the 25-point spread ceiling may still price a fixture when the market is open, accepting orders, fresh, and holds at least $100 of liquidity, with spread ≤ 60 points. The real spread, the strict rejection and a low-confidence warning are published; below $100 liquidity is never accepted. **Research-only tiers, no numbers**: with no usable line, an exact HLTV fixture identity can produce a pick with blank probabilities and blank fair odds. When both teams' world rankings are exposed on that fixture page the better-ranked team is the pick (`research_rank`); when exactly one team carries a published world ranking there and the other appears in the same fixture without one, that team is the pick (`research_rank_single`). Either way the row stores both teams' evidence — fixture label, HLTV label, rank, ranking link, and the primary source of any label mapping — so the pick is re-derivable from the snapshot alone, and both validators reject a stripped or edited row. **Final research tier** (`research_vrs_single`, [scripts/vrs.py](scripts/vrs.py)): when HLTV never listed the fixture, exactly one team resolves in Valve's official global standings under the model line's identity rules and the other team's label is genuinely absent from that file, the listed team is the pick — again with no probability or fair odds, and with the per-team standings evidence (file, position, points, roster, label counts) stored on the row. A present-but-unresolvable label is never treated as absent, and an HLTV-displayed VRS rank for the supposedly absent team blocks the tier. **Second originated source** (`model_vrs_mirror`, [scripts/vrs_mirror.py](scripts/vrs_mirror.py)): Valve's GitHub standings file is published roughly monthly, so a club that entered the ranking after the cut-off has no row there and the two-team line cannot run. For exactly those rows the refresh reads [HLTV's dated Valve ranking](https://www.hltv.org/valve-ranking/teams) — the same ranking, the same points value and the same roster per club — and applies Valve's own formula, calibration and roster-continuity rule unchanged. It fails closed on a page whose rows say “HLTV points” rather than “Valve points”, a missing date header, fewer than 100 rows, a non-monotonic table, a duplicated label without a lineup, or a club that is not listed; each is a recorded miss and the row keeps its research-only pick. The row publishes the dated page, the official standings date it superseded, and a “not a market price” label, and both validators recompute it.
7. Preserve original fields, quote inputs, observation/update timestamps, response hashes, source receipts and rejected-quote reasons. Every match links to an evidence entry and an official Hotspawn page/API. JSON and CSV exports keep unknown values blank/null. CSV includes quote observation/update, expiry, snapshot and build timestamps; downloading an old file does not renew a line.
8. **Originated line** (`model_vrs`, [scripts/vrs.py](scripts/vrs.py)): only where no market line passes its gates. Inputs are [Valve's official Regional Standings](https://github.com/ValveSoftware/counter-strike_regional_standings) points; the expected win rate is Valve's own `fit.js` formula (Glicko, rating deviation 75), calibrated with the slope from Valve's published model-fit chart (0.7986, applied symmetrically). A Valve label is used only when unique, or when the HLTV lineup shares at least three players with exactly one listed roster (Valve's roster rule). Beside market rows the model line is shown for comparison and never changes the pick. The build validator and the independent auditor recompute every model row; [a vendored copy](data/vrs/) of the official file is used only if the live fetch fails.

Research: [21 October publish-recovery diagnosis, the `flacons`/`Team flacons` exchange line and the two fixtures that stay unresolved (84295759)](research/session-84295759/REPORT.md), [19 October listing research, placeholder rejections & Aurora identity (b214c818)](research/session-b214c818/REPORT.md), [Final-day review and verification](research/session-cc88483d/REPORT.md), [Day-4 review, coverage audit & scoring facts](research/day4-37bf28f4/DAY4-REVIEW.md) with its [field-level source receipts](research/harvest-37bf28f4/day4-live-reads.json), [Day-2 review & Day-3 guidance](research/day2/DAY2-REVIEW-2026-10-15.md), [Day-1 review](research/day1/DAY1-REVIEW-2026-10-15.md), [original implementation findings](research/FINDINGS.md), [15 October integration/source review](research/INTEGRATION-2026-10-15.md), [independent row audit](research/current/ROW-AUDIT.md), [independent capture comparison](research/current/snapshot-audit.json). All observed counts are dated snapshots, not permanent coverage promises.

## Automatic operation — no routine input

[The publication workflow](.github/workflows/pages.yml) attempts a refresh **four times an hour at :04, :19, :34 and :49 UTC**. A separate watchdog checks the published snapshot every 10 minutes and dispatches the same verified workflow when the snapshot is more than 90 minutes old, subject to a cooldown and dispatch budget. These are trigger targets, not a guarantee of successful source access or GitHub delivery; the public site expires stale evidence rather than presenting it as current. The schedule was tightened after delayed and missed runs; see `research/refresh-ab18fe2a/DIAGNOSIS.md` for the historical measurements. Main changes also refresh. PRs run offline verification without fetching external sources or publishing.

- Restore the latest successful snapshot from Actions cache; `data/latest.json` is the committed bootstrap, not the permanently live dataset. The repository also includes a small verified static root fallback because the pre-existing Pages configuration is legacy `main:/`, and that source republishes on every push — so the fallback has to carry the same verified build as the artifact, or a merge silently freezes the public board. [scripts/publish_root_fallback.py](scripts/publish_root_fallback.py) does that on every main publication: it stages the hash-verified `public/` build (and its matching `data/latest.json`) only when the snapshot is inside the 8-hour evidence window, strictly newer than the one already committed and older than a 4-hour cooldown, then commits it with the workflow token. It never promotes an older or expired build; on 2026-10-21 the old manual path did, and the site served an expired 18 Oct board for three days ([flagged](https://buffedlizard55-lab.github.io/MaltaProj4/review.html)). Manual staging with `python -m scripts.stage_legacy` is now only for an intentional code change on top of the current build, and it is guarded the same way when run through the publisher.
- Re-query all three Hotspawn views, discover new matches automatically, compare inventory changes, and research only uncovered picks. If sources disagree or one fails, retain the union and flag coverage. Still-open previous-only rows survive partial discovery with unverified membership and **no new pick**.
- Wrong-game, malformed, unavailable or unexpectedly empty discovery cannot erase the last good inventory or renew its freshness timestamps.
- Picks expire at the **earliest** fixture-age TTL, quote observation/update TTL, Hotspawn lock, match start or bookmaker cutoff. The maximum evidence age is eight hours. Build-time and browser-time checks apply to the table, featured card, evidence labels and counts. With JavaScript disabled, explicit warnings and per-line observation/expiry times remain visible.
- A failed test/build prevents publication. Source access failures become visible review findings, not invented data. Full raw responses and test reports are retained as Actions artifacts for seven days; durable row-level evidence is in the published JSON.
- Deployment verifies every public file against the exact build's SHA-256 manifest. [Build receipt](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) · [Workflow history](https://github.com/buffedlizard55-lab/MaltaProj4/actions).

GitHub may delay scheduled jobs or disable inactive public-repository schedules. Public sources can change or restrict access. The 15-minute publication schedule and 10-minute watchdog are targets, not guarantees; expiry warnings prevent a failed refresh from appearing fresh. A single row that the independent audit cannot reproduce is withheld ([scripts/quarantine.py](scripts/quarantine.py)) rather than blocking every verified row; snapshot-level failures still block publication. See [COORDINATION.md](COORDINATION.md) for the actual PR/merge/deployment record rather than assuming a branch build means a live site.

## Run locally

Python 3.11+ builds a dependency-free static front end. Node 22 is only for browser verification.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m scripts.build
python -m scripts.validate
python -m http.server 8000 --bind 0.0.0.0 --directory public
```

Refresh public sources (normal outbound internet access required):

```sh
python -m scripts.refresh --output runtime/latest.json
python -m scripts.build --data runtime/latest.json
python -m scripts.validate --data runtime/latest.json
python verification-c6/audit_snapshot.py runtime/latest.json --output runtime/row-audit.md
```

Browser and independent checks:

```sh
npm ci --ignore-scripts
npm run test:browser
python -m unittest discover -s audits -p 'test_*.py' -v
python verification-95b588c2/test_integrity.py
python -m unittest discover -s verification-c6 -p 'test_*.py' -v
python -m scripts.audit_capture --snapshot data/latest.json \
  --fixtures research/current/fixture-source.json --output runtime/capture-audit.json
```

The last command deliberately requires a separately retained primary response with the same fixture ID set. It must not assert a partial union is identical to a single API response. Browser tests start and stop their own local test server and check the GitHub Pages subpath, navigation, filters, evidence anchors, 320/390/768/1440px layouts, WCAG A/AA scans and exact expiry boundaries.

## Concurrent work preserved

The separately completed d1bae160 dashboard and its eight passing tests are retained verbatim in [the integration handoff](research/handoffs/d1bae160/README.md), with its main history merged rather than overwritten. Six old public routes redirect to the current views; only one workflow publishes on the scheduled refresh. The older date-only matching/seeded quotes are not silently promoted past the stricter current UTC/market/expiry gates.

## Code map

| Scope | Purpose |
| --- | --- |
| `scripts/inventory.py` | Three-source parity, conflict blocking and last-good inventory retention |
| `scripts/core.py` | Strict identity matching, accepted quote gates, calculations and shared expiry |
| `scripts/hltv.py`, `scripts/refresh.py` | Missing-pick research (identity, rankings, lineups), including the club's own team page when HLTV publishes only a TBA bracket slot, and read-only collection with source receipts |
| `scripts/books.py`, `data/book-receipts.json` | Dated two-way book-listing receipts (with placeholder-odds rejections) and the automated re-observer that renews an observation only on a fully re-confirmed reading |
| `scripts/session_b214c818.py`, `research/session-b214c818/` | Idempotent applier and capture record for the 2026-10-19 listing research: five listing captures (four added as receipts; the Sangal line was already on file from the parallel session), six placeholder rejections, Aurora Young Blud identity evidence |
| `scripts/vrs.py`, `data/vrs/` | Originated lines from Valve's official standings with Valve's formula and calibration, plus the one-sided standings research tier (`research_vrs_single`) |
| `scripts/vrs_mirror.py` | The same originated line from HLTV's dated Valve ranking, used only for rows Valve's monthly file cannot resolve (`model_vrs_mirror`); fails closed and is audited independently |
| `scripts/quarantine.py` | Withholds any row the independent audit cannot reproduce, before the audit gate |
| `scripts/build.py`, `site/assets/` | Pre-rendered mobile dashboard, the freshness-and-coverage strip that opens the executive summary, progressive enhancement and build manifest |
| `scripts/validate.py`, `tests/` | Raw-evidence replay, source/link/hash checks and unit/browser regressions |
| `audits/`, `verification-95b588c2/`, `verification-c6/` | Preserved independent audits, including historical findings now fixed |
| `scripts/backfill_quotes.py`, `research/current/quotes/` | Applies retained primary-source receipts between scheduled refreshes; every value recomputed, never hand-typed |
| `data/analysis.json`, `analysis.html` | TWC Day-1 to Day-3 reviews, the live Day-4 block (semi-final cards, contract/streak scoring facts, the unpriced Sunday table), model-vs-market screen; research only, never a probability input |
| `scripts/twc_day4_37bf28f4.py` | Re-runnable, idempotent applier for the day-4 block: scoring facts, streak bonus, Sunday schedule, group structure, day-2 map sourcing and the withdrawn-count correction |
| `data/review-notes.json` | Sourced findings published on Flagged for Review, including this session's `flacons` alias, the unproven `ex-CYBERSHOKE` identity and the Zetta–LOS NINOS line gap |
| `research/`, `COORDINATION.md` | Primary-source research, preserved handoffs and integration record |

## 2026-10-24 — executive summary on the first phone screen, and a green gate set (session ce45f672)

`main` was red at `dce494b`: the **shipped** `assets/style.css` was one closing brace short of the canonical
`site/assets/style.css` (the `max-height:700px` block never closed), which failed five stylesheet-contract tests and
three manifest-hash tests, and the independent re-derivation refused open row `1083121` because Hotspawn's
`Projeto do KinGui` and Polymarket's `Tropa do KinGui` are different labels. Both are repaired:
the shipped copy is byte-identical to the canonical one (728/728 braces), and the verifier now accepts a label
difference **only** when the row's own evidence carries an `identity_sources` record naming both labels with an https
primary source — every refusal case (undocumented, non-https, one-sided, two teams on one outcome) has a test.

On a phone the executive summary is the compact `#exec-quicknav` bar (added in main by session 4ed657ce) plus the
freshness strip below it; this session keeps both, drops the decorative status dot below 650 px, moves the phone
card's start time into its meta row and tightens the index card's padding — measured with Chromium so that **both**
win chances stay above the fixed tab bar at 320×568. The 2026-10-24T07:09Z runner harvest also exposed a row
published as an even `0.500/0.500` with no pick (the midpoint of a 52-point spread); `scripts/core.resolve` now
rejects that quote as evidence so the row falls through to the model and research tiers that can originate a pick. New suites: `tests/browser_ce45f672.cjs` (label on the first screen, both probabilities above
the tab bar, 44 px in-site routes, 246 px card budget, one card per open match) and `tests/test_session_ce45f672.py`
(14 tests). Full gates: 1,247 unit tests OK, audits 9, verification-95b588c2 5, verification-c6 12, validator
(31 calculations reproduced, 874 links/assets, 20 checksums, 234 displayed rows) and all ten browser suites.
Findings published, non-blocking: `session-ce45f672-shipped-stylesheet-drift-2026-10-24` and
`session-ce45f672-team-label-alias-2026-10-24`. Detail: [`research/session-ce45f672/REPORT.md`](research/session-ce45f672/REPORT.md).

## 2026-10-24 — the alias gate stops skipping, and the phone routes are pinned (session a22008ff)

`main` at `6feaafe` passed its unit suite with `OK (skipped=7)`, and all seven skips were one conditional: fixture
`1083121` had rotated out of Hotspawn's lobby, so three alias-contract suites skipped instead of checking that a source
label may be mapped onto a team only via a receipted, https-backed identity record. The publish workflow runs that suite
before it deploys, so the property was unguarded while the gate still read green. Those three files now fall back to this
repository's own retained capture of the board while the row was open (`research/harvest-ce45f672/snapshot.json`) and
**fail** rather than skip when neither the live board nor the capture carries the row: `Ran 1550 tests ... OK (skipped=1)`, and the single
remaining skip is a historical-snapshot conditional for a fixture present in neither place, not a rotation skip.

Measured with Chromium on the built pages and pinned in `tests/test_session_a22008ff.py`: the first pick on `picks.html`
sits at y=368 with both win probabilities at y=425 on a 320x568 phone (y=334 / y=392 at 390x844), the index
executive-summary row links in-site to the picks and to the unresolved/limitations section, every phone tab target is a
real page, and no page overflows horizontally at 320, 390, 412, 768 or 1440 px. The same suite checks that every open
row ships a pick, two summing probabilities and an https evidence link, that no probability is read from Hotspawn, and
that no closed row is priced.

The exactly-even exchange quote this branch originally repaired is now fixed on `main` in a different shape
(`scripts.core.resolve` keeps it as rejected evidence and publishes `no_edge_lines`), so this branch adopts main's
implementation instead of duplicating it; fixture `1079200` is picked `Color` by the originated VRS line at
0.6884 / 0.3116 with Polymarket's 0.50/0.50 quote shown as rejected context. Three findings are published on
`review.html` for manual review. Full gates: 1,550 unit tests, validator (20 calculations reproduced, 15 pages, 771
links/assets, 20 checksums, 191 displayed rows) and all twelve browser suites.

Missing data is an intentional, visible result—not a placeholder to fill with guesses. No winning outcome, profitable strategy, current roster or complete sportsbook coverage is certified.
