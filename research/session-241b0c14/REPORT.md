# Session 241b0c14 — picks for every Hotspawn CS2 match: fresh audit, HLTV→esportsbooks research for the rows without a percentage, and executive-summary verification (2026-10-22)

## 0. What the owner asked, and what "done" can honestly mean

The requirement is a pick for **every** CS2 match listed on Hotspawn
(<https://play.hotspawn.com/lobby>), refreshed every 4–8 hours, with a win
probability for each team derived from **external** betting lines (never from
Hotspawn), HLTV tried first and esportsbooks second for any match the featured
tiers cannot price, a separate unresolved-picks section with limitations
inside the executive summary, and a phone-readable summary that links straight
to the updated picks. The standing verification rule bounds all of that:
*every value must replay from an official source; anything unconfirmable
stays blank and flagged — never inferred, never 50/50.*

So "a pick for every match" is delivered by the existing ladder (market line →
labelled Valve VRS model line → sourced research pick), while "a percentage
for every match" is delivered **only where a reproducible two-way line or a
two-team model input exists**. Inventing the remaining percentages from
placeholders, 90-point books or crowd votes would be exactly the hallucination
the project forbids; those rows publish their pick, a blank percentage and the
named reason instead.

## 1. Board state this session started from (committed snapshot)

`data/latest.json` generated **2026-10-22T07:58:54Z** (fixtures observed
07:56:52Z), unchanged through merges #179/#180/#183/#177:

| Measure | Count |
| --- | --- |
| Hotspawn CS2 feed rows | 107 |
| Open (lock and start in the future, scheduled) | 43 |
| Open with a pick | **43 / 43** |
| Open with a win probability | **41 / 43** — 22 `exchange` · 3 `exchange_wide` · 3 `bookmaker_fallback` · 10 `model_vrs` · 3 `model_vrs_mirror` |
| Research-only, blank % | **2** — `1082925`, `1082860` (below) |
| No pick at all | 0 |

Refresh cadence already exceeds the 4–8-hour requirement on paper —
`pages.yml` attempts publication four times an hour (`4,19,34,49 * * * *`)
plus a stale-watchdog — but at claim time (08:53Z) the **live site was not
serving this board**: a direct read of
<https://buffedlizard55-lab.github.io/MaltaProj4/> showed "Last checked
08:21 UTC", 104 feed rows, 36 with a win probability and fixture `1082919`
unpicked, while `main` publish runs sat queued and then failed at
*Refresh official sources*. Root cause (found and fixed by session cb867c3c,
PR #183, merged 09:11:59Z): when GG.BET answered 403 to both transports,
`curl_cffi`'s exception type escaped `requests`-based handling and crashed the
refresh. This session did not duplicate that fix; it merged it.

## 2. Full-board line-by-line audit and the fresh-capture runs

The board was audited line by line from the committed snapshot with the
probe's own table code: **`board-rows-2026-10-22.md`** lists all 43 open rows
(pick, both percentages or blank, method, Hotspawn + evidence links,
limitation) and reproduces the counts in §1 exactly (43 picks · 41 priced =
28 market + 13 model · 2 research-only · 0 unpicked). Every priced row's
arithmetic is independently reproduced by `scripts/validate.py` (41
calculations) and every row carries its official source link on the site.

Inventory freshness beyond the snapshot was checked directly: a manual read
of the Hotspawn CS2 fixtures API on 2026-10-22 (~09:33 UTC) ends at fixture
`1082793` (5star vs 1WIN, 2026-10-31) — the committed board's last row — with
no appended fixtures. Full ID-set parity is a property of the scheduled
pipeline (every refresh re-reads the feed and fails closed on coverage
regression), not of this report.

Repeatability: `.github/workflows/harvest-241b0c14.yml` runs the unmodified
`scripts.refresh` + `scripts.quarantine` + `verification-c6/audit_snapshot.py`
+ `scripts/probe_241b0c14.py` on a runner (the authoring sandbox cannot reach
esports hosts) and commits receipts to `capture/`. Run **39751961987**
(triggered on pre-#183 code) **failed closed** at the refresh and committed
nothing — the gate behaving as designed; run **39755290976** (current code)
was still queued behind the day's runner backlog at the time of writing and
will add its dated receipts to `capture/` when it executes. Nothing in this
report depends on inventing outside those receipts: §3 is today's dated
manual reads, cross-checked against the snapshot's own attempt ledgers.

## 3. HLTV first, then esportsbooks — for the two rows without a percentage

Only rows the featured tiers leave unpriced were researched, per the brief.
Manual reads below were taken through a rendering fetcher on **2026-10-22
between 08:58 and 09:09 UTC** (page countdowns cross-check the UTC starts);
where the snapshot's attempt ledger is cited, those reads are the 07:56–07:57Z
collector's, recorded per fixture in `data/latest.json`. The runner probe
re-reads the same URLs with SHA-256 receipts in `capture/targeted.json` when
run 39755290976 executes. Crowd votes were observed on both HLTV pages and
**excluded** — they are not probabilities on this site.

### 3.1 `1082925` — BESTIA Academy vs RED Canids Academy, CCT South America 2026 Series #7, 2026-10-23T19:00:00Z, Bo3

Board: pick **RED Canids Academy** (`research_rank`, HLTV #170 vs #184), blank %.

| Source tried (in order) | Dated observation | Verdict |
| --- | --- | --- |
| HLTV fixture [2399910](https://www.hltv.org/matches/2399910/bestia-academy-vs-red-canids-academy-cct-2026-south-america-series-7) | Same pair/event; countdown 1d 10h 14m ⇒ 19:00Z 23 Oct (page-local "15:00 23 Oct" is the same instant). Betting table contains only a Stake social-casino promo row — **no numeric two-way odds**. Ranks: BESTIA Academy HLTV **#184**, VRS **#244**; RED Canids Academy HLTV **#170**, **VRS: Unranked**. Lineups Jotag3/lezy/F4QQ/Lekzi/agt vs n1cks/rafa/sanc/gtw/FasteR (FasteR tagged Substitute). Community vote 100%/0% observed, not used. | Identity + ranking order confirmed; no line |
| Polymarket [market 6036921](https://gamma-api.polymarket.com/markets/6036921) | Exact pair + `gameStartTime 2026-10-23 19:00:00+00`. Manual read: `outcomePrices 0.5/0.5`, `bestBid 0.05`, `bestAsk 0.95`, **spread 0.90**, liquidity **$131.23**, `updatedAt 2026-10-22T08:28:57Z`, `ready:false`, `funded:false` (0.5/0.5 = untraded midpoint, not a 50/50 assessment). Runner re-read 09:44Z: `bestBid 0.07`, `bestAsk 0.71`, **spread 64 points**, liquidity **$172.04**, updated **09:42:57Z**, accepting orders. | **Refused at both reads** — spread exceeds the 60-point wide-tier ceiling; if it tightens to ≤60 before the 18:54Z lock the automated ladder prices it with no manual step |
| Pinnacle guest API | No exact pair + UTC start in the retrieved feed (board attempt ledger; runner re-check in `targeted.json`). | No line listed to this collector |
| EGamersWorld [canonical page](https://egamersworld.com/counterstrike/match/0U32SId-H/bestia-academy-vs-red-canids-academy-3nbNt3Gf1p) | Title "23.10.2026 at 19:00", CCT SA Series #7, Bo3, countdown 1d 10h 5m; odds strip **1.8 / Make a bet / 1.8** (independently read at 08:49Z by session 86b56cf6; runner read 403'd). | **Refused** — identical placeholder pair, never 50/50 |
| Stavka.tv ([CS2 listing](https://stavka.tv/matches/csgo), [CCT SA predictions page](https://stavka.tv/predictions/csgo/cct-south-america-series-7-)) | Day listing (22 Oct fixtures) names neither team; predictions page carries tipster forecasts, not an operator panel for this fixture. No match URL discovered; none guessed. | Not listed on the pages read (discovery limit, §5) |
| bo3.gg [CCT SA event page](https://bo3.gg/tournaments/cct-south-america-2026-series-7) | Event covered; upcoming cards show the affiliate text "All odds are on", no two-way price for this fixture. | No publishable line (secondary affiliate odds are never used unconfirmed) |
| Valve official standings [2026-10-05 file](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) + HLTV dated Valve ranking | RED Canids Academy is **not listed** in Valve's file and is **VRS Unranked** on HLTV, so no two-team points difference exists for either model tier. Nothing is derived from BESTIA Academy's points alone. | Model line impossible today |

**Conclusion:** the pick stands (ranking order #170 over #184, exact fixture),
the percentage stays blank, and the limitation above is what the executive
summary's unresolved section and `unresolved.html` publish for this row.

### 3.2 `1082860` — FlyQuest vs Staqued, DFRAG Invitational 2026, 2026-10-27T03:00:00Z, Bo3 LAN

Board: pick **FlyQuest** (`research_rank_single`, HLTV #61 vs unranked), blank %.

| Source tried (in order) | Dated observation | Verdict |
| --- | --- | --- |
| HLTV fixture [2399890](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026) | Same pair/event (Group B opening, LAN); countdown 4d 18h 14m ⇒ 03:00Z 27 Oct. Betting table promo-only — **no numeric odds**. FlyQuest HLTV **#61**, VRS **#54**; Staqued carries **no world-ranking number**. Lineups jks/INS/Vexite/nettik/aliStair vs w0mbat/xelja/Hazel/lzj/kasze. Community vote 84.6%/15.4% observed, not used. | Identity + one-sided ranking confirmed; no line |
| Polymarket / Pinnacle | No exact pair + UTC start in either retrieved feed (board attempt ledger; runner re-check in `targeted.json`, including a Gamma public-search discovery read). | No market listed to this collector |
| EGamersWorld [match page](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3) | Title "27.10.2026 at 03:00", DFRAG Invitational 2026, Bo3; odds strip **1.8 / Make a bet / 1.8**. (EGW's Staqued roster block is incomplete — KRAXYT plus a "noName" fifth vs HLTV's five; identity still exact by pair + start + event.) | **Refused** — placeholder |
| Stavka.tv [CS2 listing](https://stavka.tv/matches/csgo) | DFRAG fixtures do not appear on today's listing; no match URL discovered; none guessed. | Not listed on the page read (discovery limit, §5) |
| bo3.gg [DFRAG event page](https://bo3.gg/tournaments/dfrag-invitational-2026) | FlyQuest vs Staqued card present (match link `flyquest-vs-staqued-27-10-2026` discovered there) with "All odds are on" — no two-way price. Event FAQ still describes rosters as unannounced. | No publishable line |
| Valve official standings + HLTV dated Valve ranking | Staqued is absent from Valve's 2026-10-05 file and from HLTV's Valve ranking (board attempts; runner presence check in `targeted.json`), so neither model tier can compute a two-team line. FlyQuest's 1093 points alone imply no percentage. | Model line impossible today |

**Conclusion:** pick FlyQuest stands on one-sided ranking evidence; percentage
blank with the limitation published. This fixture is five days out — EGW is
known to fill its widget late (session ff49b2ef), and PR #177's
`watch_unpriced` now re-reads this exact rejected URL on every refresh, so a
real asymmetric pair will price automatically if one appears.

## 4. Executive summary & phone verification (no UI files edited by this session)

Verified on the merged tree (13e99ca6 banner + eaff7cce phone-first rework),
built locally from the committed snapshot:

* `index.html` (Executive summary) opens with the exec banner + freshness
  strip carrying live `data-count` counters and in-site links:
  **Updated picks → `picks.html`**, **Every pick on this page ↓
  `#picks-at-a-glance`**, **Unresolved & limits → `unresolved.html`**, plus
  the coverage card, Picks-at-a-glance list (every open match, bold pick +
  %), and the **separate `#unresolved-picks` section** ("Picks without a win
  probability — and exactly why") listing both blank-% rows with pick,
  limitation, flags and Hotspawn/HLTV/evidence links, followed by the ordered
  source ladder. `tests/test_session_241b0c14.py::TestExecutiveSummaryLinks`
  pins the anchors/hrefs.
* `npm run test:browser` passed locally: 32 page/viewport accessibility +
  no-overflow scans at **320/390/768/1440px**, 7 board-expiry + 4
  research-boundary scenarios, 8 phone/desktop/queue/unresolved scenarios,
  and the first-screen CTA scenarios (44px+ tap target, first pick list
  within 1700px at 320/390px, legacy anchors, keyboard disclosures).
* Publication path: `pages.yml` (4 slots/hour + watchdog) → refresh →
  quarantine/audits → build → validator → browser gates → Pages artifact +
  legacy root fallback → live-byte verification. The final live-byte receipt
  for this session's merge is recorded in `COORDINATION.md`, and the
  fallback's committed root pages are the deployment bytes to compare.

## 5. Limitations for generating picks (the honest ceiling)

1. **No accessible market exists** for some low-tier/academy/LAN-qualifier
   fixtures on any source this collector may read (Polymarket, Pinnacle,
   EGW/Stavka listings, bo3). Absence from the pages read is *not* proof no
   bookmaker anywhere prices them — Thunderpick renders no extractable quote
   and GG.BET answers 403 (recorded, never bypassed).
2. **A market exists but is untradable**: a 73–92-point Polymarket book or the
   EGW 1.8/1.8 placeholder. Publishing either midpoint would fabricate
   precision (0.5/0.5 on an untraded book is a placeholder, not 50/50).
3. **No two-team model input**: one club (RED Canids Academy, Staqued) has no
   Valve points in the official monthly file *or* HLTV's dated mirror, so the
   originated VRS line cannot be computed. One-sided points never become a %.
4. **Identity must be exact**: pair + UTC start + registered aliases only.
   Similar names, wrong-event pages and guessed slugs are refused even when a
   price is visible elsewhere.
5. **Freshness**: every line expires with its 8-hour evidence window, fixture
   lock/start and market-update clocks; Hotspawn adds fixtures continuously,
   so coverage is always stated as dated counts, never a permanent promise.
6. **Discovery is listing-bound**: Stavka/EGW match pages are followed only
   from recorded register URLs or the operator's own listing pages. A fixture
   absent from today's day-scoped listing may still gain a page later; the
   15-minute refresh (incl. EGW gap recheck) is the mechanism that catches it.

## 6. Irregularities flagged (published on Flagged for Review; none blocks merge)

1. **Stale EGW register prose for `1082925`** (`data/book-receipts.json`,
   superseded additively by this session, originals untouched): (a) the
   `zawJ-Q52S3/...-zawJ-Q52S3` URL redirects to the generic
   `/counterstrike/matches` listing today and its recorded start
   (`2026-10-22T20:00:00Z`) matches no Hotspawn row; (b) the
   `fQ0D-T2eM/...-3nbNt3Gf1p` entry describes a "2026-10-23T22:00:00Z Aorus
   League" match, but the page canonicalises to
   `0U32SId-H/bestia-academy-vs-red-canids-academy-3nbNt3Gf1p` titled
   23.10.2026 **19:00** in CCT SA Series #7 — this fixture; (c) one reason
   cites "HLTV #191 vs #227", contradicting both the snapshot and today's
   HLTV read (#184 vs #170) and, taken literally, the pick direction. The
   refusal outcome (1.8/1.8) was correct in every case.
2. **VRS badge drift**: snapshot records BESTIA Academy `vrs_rank_on_hltv`
   243 (07:57Z); HLTV showed #244 at ~09:02Z. No number on the board depends
   on it (research pick uses world ranks #184/#170).
3. **Session 13e99ca6 report table** (`research/session-13e99ca6/REPORT.md`,
   not edited by this session) lists superseded/wrong starts and EGW ids for
   several fixtures (e.g. `1082925` at "2026-10-24T17:00Z"; actual
   2026-10-23T19:00:00Z per Hotspawn/HLTV/Polymarket above) from its earlier
   08:03Z board basis. Current values are in `data/latest.json` and §3 here.
4. **13e99ca6 exec-banner wording** ("Every open match has a pick") is static
   prose: true on today's board, but it would overstate coverage the day an
   unpicked fixture appears. Logged as a request to the build owners in
   `COORDINATION.md`; this session does not edit `scripts/build.py`.
5. **Live-vs-repo divergence at claim time** (§1): the deployed site lagged
   the committed board while publish runs queued/failed pre-#183. Final
   live-byte verification after this session's merge decides whether it is
   closed; the receipt is recorded in `COORDINATION.md`.

## 7. Sources (all read 2026-10-22; every board row links its own)

Hotspawn CS2 fixtures API + lobby views (inventory only) ·
HLTV matches [2399910](https://www.hltv.org/matches/2399910/bestia-academy-vs-red-canids-academy-cct-2026-south-america-series-7),
[2399890](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026),
[ranking](https://www.hltv.org/ranking/teams/2026/october/19/13026),
[dated Valve ranking](https://www.hltv.org/valve-ranking/teams) ·
Polymarket Gamma [market 6036921](https://gamma-api.polymarket.com/markets/6036921) ·
[Pinnacle guest esports API](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight) ·
EGamersWorld pages in §3 · [Stavka CS2 listing](https://stavka.tv/matches/csgo) ·
bo3.gg event pages in §3 ·
[Valve official standings 2026-10-05](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md)
(byte-verified newest by session 2ec8cd6c).
Runner receipts land in `capture/targeted.json` (`source_receipts`: URL, HTTP
status, SHA-256, bytes, cache-adjusted `observed_at` per read) when run
39755290976 executes; the two manual-read refusals above are already recorded
in `data/book-receipts.json` + `data/review-notes.json` (2026-10-22 entries,
observation window disclosed in each reason).

## 8. What is deliberately not claimed

No new percentage, pick change or threshold change. No rank, rating, crowd
vote, tipster forecast or affiliate widget was converted into a probability.
"Not listed on the pages read" is never restated as "no bookmaker offers
odds". Model lines remain labelled estimates, market lines remain
market-implied (fees excluded), and dated counts are not accuracy claims.
