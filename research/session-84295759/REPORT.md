# Session 84295759 — why the board went stale, and the last unpriced fixture

Read 2026-10-21 between 12:39 and 12:52 UTC. Every figure below is a verbatim
reading of the linked primary source at that time; nothing is averaged, inferred
or carried over from an earlier snapshot.

## 1. The published board was 29 hours old, and the cause was a test clock

`gh run list --branch main` showed the scheduled publisher failing at
2026-10-20T13:02:43Z, 17:56:21Z, 21:30:58Z, 2026-10-21T00:05:28Z, 04:57:06Z and
10:00:04Z. Every one of those runs failed in the same step, `Unit and
independent failure-mode tests`, before the refresh, build and deploy steps could
run:

| Run | Conclusion | Failing step |
| --- | --- | --- |
| [39427081979](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39427081979) | failure | Unit and independent failure-mode tests |
| [39470396362](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39470396362) | failure | Unit and independent failure-mode tests |
| [39500988384](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39500988384) | failure | Unit and independent failure-mode tests |
| [39519156900](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39519156900) | failure | Unit and independent failure-mode tests |
| [39546824882](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39546824882) | failure | Unit and independent failure-mode tests |
| [39581284152](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39581284152) | failure | Unit and independent failure-mode tests |

Reproduced locally on `main` at `b648875`: `python -m unittest discover -s tests`
ran 440 tests and failed 3, all in `tests/test_session_133fe7ca.py`. The fixture
helper set `now = datetime.now(timezone.utc)` while the fixture it builds starts
2026-10-20T12:00:00Z, so from 2026-10-20 12:00 UTC onward the row was no longer
open and the research tier legitimately refused it. Production behaviour was
correct; only the test clock was wrong.

The fix (`now` pinned to the receipt's observation window) was already open as
[PR #96](https://github.com/buffedlizard55-lab/MaltaProj4/pull/96) from session
3a695af9 with a passing `verify-build`. This session did not edit that file and
did not open a competing patch; it merged with #96 and re-ran the pipeline
(section 4).

Live `build-info.json` before the fix, for the record:
`revision b648875…`, `built_at 2026-10-20T07:44:51.704588Z`, 96 rows
(<https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json>).

## 2. The gap list this session worked from

The freshest independent collection on 2026-10-21T12:41Z (session 40c14278's
trusted-runner harvest) reported 19 open fixtures, 16 priced, 2 research-only
picks and these four gaps:

| Fixture | Match | Start (UTC) | State then |
| --- | --- | --- | --- |
| 1079648 | G2 Ares vs ILLYRIANS | 2026-10-21T14:00Z | priced at exactly 50/50, so no directional pick |
| 1082762 | ex-CYBERSHOKE vs BlinkDagger | 2026-10-21T15:00Z | no pick, no percentage |
| 1082763 | UPGRADE vs flacons | 2026-10-21T15:00Z | research pick only, no percentage |
| 1082837 | Zetta vs LOS NINOS | 2026-10-21T22:00Z | research pick only, no percentage |

## 3. HLTV first, then the books

### 1082763 UPGRADE vs flacons — solved with an exact exchange line

* HLTV match [2399840](https://www.hltv.org/matches/2399840/upgrade-vs-flacons-winline-mpkbk-cis-lan-season-9):
  `UPGRADE vs. flacons`, WINLINE MPKBK CIS LAN Season 9, Group C opening match,
  21 October 2026, countdown resolving to 15:00 UTC. Team pages: UPGRADE
  [13989](https://www.hltv.org/team/13989/upgrade) (`HLTV: #74`, `VRS: #86`) and
  flacons [13932](https://www.hltv.org/team/13932/flacons). HLTV's own betting
  table exposed no numeric two-way line; its fan-vote widget read 75.6% / 24.4%
  and is **not** used as a probability anywhere in this project.
* Polymarket market [5971986](https://gamma-api.polymarket.com/markets/5971986):
  `UPGRADE vs Team flacons (BO3) - CIS LAN Championship Group C`,
  `gameStartTime 2026-10-21 15:00:00+00`, `outcomePrices ["0.955","0.045"]`,
  `bestBid 0.95`, `bestAsk 0.96` (1.0-point spread), `liquidity 2954.121`,
  `acceptingOrders true`, `updatedAt 2026-10-21T12:34:58.113464Z`,
  `resolutionSource https://hltv.org`.
* Identity: only the generic leading `Team ` differs. One club named flacons
  exists in this competition, and the opponent pair plus UTC start are exact.
  Registered in `data/identities.json` as canonical `flacons`
  (`["flacons","Team flacons"]`) with both URLs above and the same
  fixture-parity basis as the existing `Falcons`/`Team Falcons` and
  `Insiders`/`Insiders Esport` entries.
* Result after the alias: de-vigged **UPGRADE 95.5% / flacons 4.5%**, pick
  UPGRADE, method `exchange`. The price is the exchange's own two-way quote; the
  only thing this session supplied is the label mapping, which the resolver still
  gates on the exact pair and exact UTC start.

### 1079648 G2 Ares vs ILLYRIANS — resolved by the market itself

Polymarket market [5994489](https://gamma-api.polymarket.com/markets/5994489):
`G2 Ares vs ILLYRIANS (BO3) - CCT Europe Series #11 Group Stage`,
`gameStartTime 2026-10-21 14:00:00+00`, now `outcomePrices ["0.505","0.495"]`,
`bestBid 0.50`, `bestAsk 0.51` (1.0-point spread), `liquidity 5219.7215`,
`acceptingOrders true`, `updatedAt 2026-10-21T12:42:59.763364Z`. The 12:41Z
snapshot had captured an exact 0.50/0.50, which correctly produced no directional
pick; the market has since moved, so the next refresh prices it. No code change
was needed and none was made for this row.

### 1082762 ex-CYBERSHOKE vs BlinkDagger — priced, and reproduced with two caveats

* HLTV match [2399839](https://www.hltv.org/matches/2399839/ex-cybershoke-vs-blinkdagger-winline-mpkbk-cis-lan-season-9):
  `ex-CYBERSHOKE vs. BlinkDagger`, same event, Group C opening match, 15:00 UTC.
  Lineups block: `HLTV: Unranked`, `VRS: #78`.
* HLTV team page [14106](https://www.hltv.org/team/14106/ex-cybershoke) reads, in
  HLTV's own words: `ex-CYBERSHOKE does not currently have a roster.`,
  `ex-CYBERSHOKE haven't participated in any events or leagues yet.`,
  `Couldn't find any recent results for ex-CYBERSHOKE`. The entity has a fixture
  but no roster, no results and no ranking of its own.
* Polymarket market [5971981](https://gamma-api.polymarket.com/markets/5971981)
  prices `CYBERSHOKE Esports vs BlinkDagger` at `["0.82","0.18"]`,
  `gameStartTime 2026-10-21 15:00:00+00`, `liquidity 1981.5339`.
* The published board instead prices this row from a **different, later receipt**
  (added by a parallel session after this session's first read):
  [stavka.tv](https://stavka.tv/matches/csgo/21-10-2026-cybershoke-esports-blinkdagger),
  observed 12:46Z. Re-read independently at **13:15Z** it renders the fixture as
  `CYBERSHOKE — BlinkDagger`, 11:00 on 21 October, with `П1 1.14` tagged
  **Winline** and `П2 7.50` tagged **BetBoom**, and its Russian preview calls the
  same Russian roster `ex-CYBERSHOKE (#76 VRS)`. The published 86.8% reproduces
  from those two numbers: `1/1.14 = 0.877`, `1/7.50 = 0.133`, normalised to
  86.8% / 13.2%.
* This session's own first read (`data/review-notes.json` id
  `ex-cybershoke-identity-84295759`) has been rewritten to match what is actually
  published. What remains true and is on Flagged for Review: the 1.14 and 7.50
  prices come from **two different operators**, not one bookmaker's two-way
  market; the source is a media/prediction page rather than the operators' own
  odds pages; and the club appears under two labels (`CYBERSHOKE` on Polymarket,
  `ex-CYBERSHOKE` on HLTV and Hotspawn). Nothing is averaged with the Polymarket
  price, and the row should be re-observed before its number is treated as
  settled.

### 1082837 Zetta vs LOS NINOS — no usable line exists on either path

* HLTV match [2399865](https://www.hltv.org/matches/2399865/zetta-vs-los-ninos-cct-2026-south-america-series-7):
  `Zetta vs. LOS NINOS`, CCT 2026 South America Series 7, Swiss round 5,
  21 October 2026 18:00 local = 22:00 UTC. Zetta
  [13833](https://www.hltv.org/team/13833/zetta) carries `HLTV: #241`, `VRS: #366`;
  LOS NINOS [14092](https://www.hltv.org/team/14092/los-ninos) carries no world
  ranking, which is why only the one-sided research pick exists. HLTV fan votes
  read 80.0% / 20.0% and are not used.
* EGamersWorld's listing
  ([match page](https://egamersworld.com/counterstrike/match/0U32SId-H/zetta-vs-los-ninos-Wi0PWrNpb))
  was read at 12:56Z and renders `Zetta 1.8` and `LOS NINOS 1.8` — the identical
  placeholder pair this project rejects elsewhere, not a two-way price.
* Polymarket's only near candidate is `Alianza Lima Esports vs Los Niños`
  ([market 6001634](https://gamma-api.polymarket.com/markets/6001634)): a
  different opponent, `outcomePrices ["0.49","0.51"]` with `bestBid 0.19` /
  `bestAsk 0.79` (a 60-point spread), `liquidity 542.6664` and `volume 5`. It
  cannot price this fixture, and the fact that it shares the 22:00Z start with
  HLTV's `Zetta vs LOS NINOS` is recorded as a source conflict for review rather
  than resolved by inference.
* Decision: the research-only pick stands with **no percentage**; the limitation
  (no two-way line, one side unranked in both HLTV and Valve's standings) is
  published rather than filled with a guess.

## 4. Verification

* `python -m unittest discover -s tests` — 449 tests, OK (including the nine new
  regressions in `tests/test_session_84295759.py`), with PR #96 merged.
* `python -m unittest discover -s audits -p 'test_*.py'` — 9 OK;
  `python verification-95b588c2/test_integrity.py` — 5 OK;
  `python -m unittest discover -s verification-c6 -p 'test_*.py'` — 12 OK.
* `python -m scripts.build` and `python -m scripts.validate` green.
* End-to-end runner build on this session's branch (which includes the real
  refresh against Hotspawn, Polymarket, Pinnacle and HLTV):
  [run 39601536436](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39601536436)
  — unit/audit/integrity steps, `Refresh official sources`, `Withhold any row the
  independent audit cannot reproduce`, `Build and independently verify every row,
  calculation and internal link`, and the phone/tablet/desktop accessibility and
  expiry suite all succeeded.

## 5. Limitations held to

* Hotspawn supplies fixture inventory only; no Hotspawn field ever becomes a
  probability.
* A missing percentage stays missing. Nothing here is a 50/50 filler, and the
  one 50/50 reading that was genuine (a market trading at exactly 0.50/0.50) was
  published as "no directional edge" rather than as a pick.
* HLTV fan votes were read and deliberately not used.
* The `flacons` alias is a label mapping with two primary sources; it does not
  assert roster continuity, an academy link or a result.
