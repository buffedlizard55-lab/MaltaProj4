# Session ff49b2ef — 2026-10-22: unpriced-row research sweep, exec-summary verification, integration

Branch: `arena/ff49b2ef-maltaproj4` (claims at top of `COORDINATION.md`, 2026-10-22 01:12 UTC).
All times UTC. Every read below was performed by direct page/API retrieval on 22 October 2026
unless a different date is stated.

## 1. Inventory audit (live board vs repository)

| Fact | Value | Source |
| --- | --- | --- |
| Live deployment | revision `40e1fab4`, built 2026-10-22T00:55:06Z from snapshot 00:55:05Z, 97 rows | https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json |
| Live snapshot meta | coverage "verified", fixtures observed 00:51:14Z, refresh_hours 1, stale_after 8h, per-feed sha256 receipts | https://buffedlizard55-lab.github.io/MaltaProj4/data/latest.json |
| Open rows | 35 open · 35 with a pick · 28 with a win probability · 0 unresolved (no pick at all) | https://buffedlizard55-lab.github.io/MaltaProj4/index.html |
| Probability split | 8 market/bookmaker lines (7 Polymarket + 1 Pinnacle fallback), 20 Valve VRS model lines | https://buffedlizard55-lab.github.io/MaltaProj4/picks.html |
| Research-only rows (pick, no %) | 1081869, 1081597, 1082769, 1079654, 1081149, 1081150, 1082860 | https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html |
| Local `data/latest.json` | stale 21:27Z 21 Oct bootstrap (75 rows) — not the live board; left untouched per the staging policy | repo file |
| Hotspawn API quirk | `status=scheduled` still returns June fixtures (1052746, 1051339, …); inventory refresh's time filters handle this; no change needed | https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1 |

The scheduled refresh (pages.yml, :04/:19/:34/:49 + watchdog) is healthy: it discovered and
priced 22 new fixtures between the 21:27 local bootstrap and the 00:55 live snapshot.

## 2. Research sweep over the seven unpriced rows

Mandated order per row: HLTV identity/lines → esportsbooks & esports betting lines.
Polymarket and Pinnacle are re-checked by the scheduled refresh itself every run (its
attempts and exclusions are already published per row); this session added the manual
esportsbook layer.

### 2.1 RESOLVED — 1082769 K27 vs NEXORA (CIS LAN Championship #9, 22 Oct 17:30)

* **EGamersWorld book listing, read 01:56 UTC: NEXORA 8.1 / K27 1.021**
  (https://egamersworld.com/counterstrike/match/4yp_dlKtNl/nexora-vs-k27-U_TH-dVYT).
  The same page served the 1.8/1.8 placeholder on 21 Oct; its book-average widget filled
  in within ~16h of start. EGWxxxBOT summary on the page: "K27 are listed as the favorites…
  odds on them are equal to 1.021. NEXORA… about 8.1."
* De-vig (scripts.core.quote_book): 1/1.021 = 0.979432, 1/8.1 = 0.123457, overround 10.29%,
  **K27 88.81% / NEXORA 11.19%**, fair odds 1.126 / 8.933, pick **K27**.
* Receipt: **collision resolved by keeping exactly one line source.** Concurrent session
  767649ba (claim 01:18 UTC, six minutes after this session's 01:12 UTC claim — neither saw
  the other's branch claim) independently captured the same EGW pair at 01:12 UTC and its
  receipt `egw-4yp_dlKtNl-nexora-k27` was already on `main` at rebase time (02:2x UTC), with
  richer corroboration (СТАВКА ТВ Betcity 7.80 / Melbet 1.06 → 88.04/11.96; Kushvsporte
  8.20/1.04 → 88.74/11.26). This session's receipt copy (`…-2026-10-22`, observed 01:56 UTC)
  recorded the same pair and was **dropped** — the repository bar rejects duplicate listing
  pairs for one fixture, and overwriting theirs would have discarded their work. Kept from
  this session: the 01:56 UTC re-read (second timestamped sighting 44 min later), the
  Kushvsporte per-price operator attribution detail (price links labelled Лига Ставок /
  WinLine), and the later placeholder re-reads for the other rows.
* **Corroboration (never the line):** Kushvsporte named-operator panel read 01:19 UTC
  (https://kushvsporte.ru/event/6993380-k27-nexora): "П1 1.04 (price link labelled
  Лига Ставок) / П2 8.2 (price link labelled WinLine)" — same shape to within one point of
  vig. This file already refused Kushvsporte as a *line* source for fixture 1082762 (its
  panel there carried no per-price operator names); it is therefore kept as corroboration
  only, and the published line is the EGamersWorld listing — the file's established class.
* Verification replayed through `scripts.core.book_research_pick` (see tests): the merged
  receipt prices the row to bookmaker_fallback with the research flag; after the 8h
  observation window the quote refuses ("Researched book listing is stale") and the row
  reverts to the research tier. `scripts/books.py` re-observes the EGW URL every refresh and
  renews the pair only while the page re-confirms it.
* Flagged on the review source: `ff49b2ef-k27-nexora-egw-line-2026-10-22` (collision log +
  independent confirmation).

### 2.2 Concurrent work merged mid-sweep (nothing discarded)

Rebasing onto `main` at ~02:20 UTC (and again at ~02:5x UTC) brought PRs
[#146](https://github.com/buffedlizard55-lab/MaltaProj4/pull/146) (session 6dd6f287: a labelled
`model_vrs_mirror` tier over HLTV's dated Valve ranking), [#154]/[#155] (session 7271c5d5: the
29-priced board, a 4-source K27 corroboration note, and a bookmaker-replay orientation fix) and
[#156] (session 5f1df842). The mirror tier was expected to price 1079654/1081149/1081150, but
the 02:00:46Z snapshot this session verified still publishes those rows as research-only picks
with no percentage — the mirror tier fails closed on an ex-RUSTEC standings label tie and on
LFO 10's absence from the standings file (its own tests document both refusals). This session
claims no percentages for them and keeps only its dated placeholder reads and flags.

## 2.3 UNRESOLVED (six rows; documented ceiling: research pick, no percentage)

| Row | Start | Reads on 22 Oct | Sources that do NOT price it |
| --- | --- | --- | --- |
| 1081869 Morningstar vs NEXVOID | 03:00 | EGW 1.8/1.8 at 01:57 (direct read, 63 min before start) | HLTV 2399584 has only a login-gated fan vote (never used) and no book panel; stavka.tv preview (no operator panel); bo3.gg links Thunderpick without a line; EGW odds-comparison page omits the pair |
| 1081597 benched gods vs TitanFlow | 11:00 | EGW 1.8/1.8 at 02:00 (direct read, 3rd dated reading) | EGW prices sibling CCT Challengers #8 fixtures (Ryvex vs Quintessence: Thunderpick 2.24/1.55 …) so the absence is real coverage; existing HLTV "postponed"/TBA vs Hotspawn-open conflict flag and the TitanFlow no-roster irregularity (session 6dd6f287) stand |
| 1082860 FlyQuest vs Staqued | 27 Oct 03:00 | (prior session 21 Oct: EGW 1.8/1.8; Polymarket/Pinnacle/Picklebet/Stavka/EsportsInsider all absent; Staqued in neither Valve file) | unchanged |

All five new placeholder reads are recorded in `data/book-receipts.json → rejected_listings`
with observation times; **no percentage is invented anywhere** (blank + flag, never 50/50).

### 2.4 Structural finding (published in `ff49b2ef-unpriced-rows-sweep-2026-10-22`)

EGamersWorld fills its book-average widget *late* (K27-NEXORA: placeholder on 21 Oct → live
pair ~16h before start), but the scheduled refresh only re-observes URLs already present in
`data/book-receipts.json`. Nothing automatically notices a newly filled EGW page for a row
without a receipt. Recommended follow-up before the 23 Oct starts: re-read the CCT
Europe pages and record receipts if real asymmetric pairs appear. (benched gods vs
TitanFlow starts first at 11:00 today — its EGW page may still fill.)

## 3. Identity / roster irregularities flagged

1. `ff49b2ef-forze-lfo10-identity-2026-10-22` — EGW's listing for 1081149 has an empty
   opponent label; its opponent team page publishes dan1/Sapec/Mann3n/dottie/L00m1 (the
   LFO 10 players per HLTV), while stavka.tv's same-day page labels the opponent
   "Sökerorg". Labels conflict → nothing transferred, row keeps its HLTV-verified pick.
2. `ff49b2ef-ex-rustec-shalfey-transfer-2026-10-22` — HLTV news (21 Oct): shalfey leaves
   ex-RUSTEC for GamerLegion. Ranking-order picks 1079654/1081150 use the published HLTV
   rank (#70, observed 00:51 UTC) with the caveat published; picks unchanged, no numbers.

## 4. Site verification (executive summary, links, mobile posture)

Read live on 22 Oct 00:55Z build:

* Executive summary: freshness strip ("Last checked 22 Oct · 00:55 UTC"), hero next pick,
  "Then next" list, **nav cards with in-site links** to `picks.html`, `#unresolved-summary`
  (unresolved & limits), `analysis.html`, `matches.html`.
* "Picks at a glance" lists **every open row** with pick + percentage or "Research only ·
  no percentage — why ↓" (35 rows enumerated across chunks), each row linking to its
  `evidence.html#match-…` anchor.
* The unresolved/limitations section is included in the executive summary
  (`#unresolved-summary` + the `unresolved.html` queue with per-row limitation text and
  every attempted source).
* `picks.html` markets/models rows all carry pick + % + source link; "27 non-market or
  unresolved matches →" cross-links the research queue.
* Mobile posture: pre-rendered dashboard with bottom nav and fluid panels; layout widths
  (320/390/768/1440) are covered by the existing browser suite (`npm run test:browser`),
  which the PR workflow exercises; no template changes were needed this session, so no
  site/** edits were made.

## 5. Deliverables

* `data/book-receipts.json` — duplicate K27 receipt dropped in favour of the merged
  `egw-4yp_dlKtNl-nexora-k27` (767649ba, richer corroboration); +8 dated placeholder
  rejections from this session's reads (01:57-02:08 UTC plus three 21 Oct 20:05 readings the
  concurrent rewrite had displaced, restored by union); indent=1 preserved; no other
  session's entry altered or removed.
* `data/review-notes.json` — +4 notes (`ff49b2ef-*`, all with dated labelled sources),
  appended to the 102 notes already on main.
* `tests/test_session_ff49b2ef.py` — locks the receipt math, staleness refusal, the five
  placeholder rejections, the no-placeholder-receipt invariant, and the review notes.
* `README.md` — dated 22 October coverage paragraph added beside the 21 October one.
* `research/session-ff49b2ef/REPORT.md` — this report.

## 6. Local verification run

* `python -m unittest discover -s tests` (venv with `requirements.txt`) — full suite.
* `python -m scripts.validate --data data/latest.json --site .` — validated the committed
  snapshot + root fallback as a matched set (no root re-staging from the stale bootstrap;
  the next main refresh rebuilds and re-stages from a fresh snapshot).

## 7. What the next refresh does with this

The merged receipt already prices 1082769 as a labelled `bookmaker_fallback` (K27 88.8% /
NEXORA 11.2%, research flag, observation time shown) on every pages.yml run; `scripts/books.py`
renews its observation while EGW re-confirms the pair. If EGW reverts the page to its
placeholder, the observation expires and the row returns to its research pick with no
percentage — by design, never a guessed number. The six remaining research-only rows pick
up a percentage automatically the moment any checked source publishes an asymmetric two-way
line that passes its gates.
