# Session 227839d2 — line-by-line verification log

**Date:** 19 October 2026 (UTC). **Branch:** `arena/227839d2-maltaproj4`.
**Scope:** the completed Thunderpick World Championship 2026, the new pick record, the archive gate, and a re-verification of the repo's published result rows.

Every claim below was checked against the URL beside it. Anything that could not be checked is listed under "Not verified" and was left blank or removed rather than filled in.

## 1. Final-day results (new rows published this session)

| Row | Published value | Official source | Result |
| --- | --- | --- | --- |
| Event status | Finished, 14–18 October 2026 | https://www.hltv.org/results?event=8932 | Matches. The results page opens with `Finished` and the event banner. |
| Grand final | FURIA 3-2 BETBOOM, best of 5 | https://www.hltv.org/matches/2399417/furia-vs-betboom-thunderpick-world-championship-2026 | Matches. Page header `3 : 2`, `Best of 5 (LAN) * Grand final`. |
| Grand final maps | Dust2 13-6; Ancient 16-19; Nuke 9-13; Mirage 13-11; Cache 13-6 | same page | Matches, including the overtime map (Ancient 16-19). |
| Grand final veto | FURIA rm Anubis; BETBOOM rm Inferno; FURIA Dust2; BETBOOM Ancient; FURIA Nuke; BETBOOM Mirage; Cache left over | same page | Matches verbatim. |
| Third place | Aurora 2-1 Falcons, best of 3 | https://www.hltv.org/matches/2399416/aurora-vs-falcons-thunderpick-world-championship-2026 | Matches. `2 : 1`, `Best of 3 (LAN) * 3rd place decider match`. |
| Third-place maps | Anubis 8-13; Dust2 19-17; Nuke 13-9 | same page | Matches. Aurora lost map 1, won the next two. |
| Event winner | FURIA | https://www.hltv.org/matches/2399417/... | Matches. FURIA won three of five maps. |

The series scores are also re-read on the aggregate results page, so the two pages agree.

## 2. Pick record (derived, no new probability)

| Pick | Price published here | Where the price came from | Official winner | Scored |
| --- | --- | --- | --- | --- |
| FURIA (semi-final, 17 Oct) | 52.5% | Polymarket market 5778024, 00:51Z 17 Oct (already in `data/analysis.json`) | FURIA 2-0 Aurora — https://www.hltv.org/matches/2399414/... | correct |
| Falcons (semi-final, 17 Oct) | 79.5% | Polymarket market 5787759, 00:51Z 17 Oct | BETBOOM 2-1 Falcons — https://www.hltv.org/matches/2399415/... | incorrect |
| Falcons (3rd place, 18 Oct) | 60.5% | Board row 1080209 in the retained snapshot | Aurora 2-1 Falcons — https://www.hltv.org/matches/2399416/... | incorrect |
| FURIA (grand final, 18 Oct) | 70.5% | Board row 1080210 in the retained snapshot | FURIA 3-2 BETBOOM — https://www.hltv.org/matches/2399417/... | correct |

Totals: 2 of 4, mean published chance 65.8% (arithmetic: (52.5+79.5+60.5+70.5)/4 = 65.75, rounded to 65.8). Contrarian calls: 3, of which 1 landed (BetBoom).
The 79.5% miss is published, not removed. The record is labelled as too small to test calibration.

## 3. Correction found while re-verifying earlier rows

* `day_two` BETBOOM–PARIVISION stored `Ancient 13-10 (PARIVISION), Anubis 4-13, Mirage 7-13` next to a `2-1` series score.
  The HLTV page (https://www.hltv.org/matches/2399410/parivision-vs-betboom-thunderpick-world-championship-2026) shows PARIVISION 13-10 Ancient, then BETBOOM 13-4 Anubis and 13-7 Mirage.
  Corrected to `Ancient 10-13 (PARIVISION); Anubis 13-4; Mirage 13-7` with a visible `Correction:` note on the page. Series score unchanged. Published on Flagged for Review as `day2-map-orientation-227839d2`.
* Remaining losing maps in the same tables now name the team that won them (`Anubis 5-13 (Falcons)`, `Dust2 11-13 (Legacy · …)`), and the column header reads "Maps (series winner first)".
* A new test recomputes every stored map list against its series score (14 series across five days), so this class of error now fails the build.

## 4. Rows re-checked and found consistent (no change)

| Day | Series | Source | Check |
| --- | --- | --- | --- |
| 1 | 9z 2-0 Aurora; Inferno 13-11, Nuke 13-1 | https://www.hltv.org/matches/2399384/... | Matches. |
| 3 | Aurora 2-0 9z (Cache 13-11, Inferno 13-4) and BETBOOM 2-1 Legacy | https://www.hltv.org/results?event=8932 | Series scores match. |
| 4 | FURIA 2-0 Aurora (Dust2 13-8, Inferno 13-10) | https://www.hltv.org/matches/2399414/... | Matches. |
| 4 | BETBOOM 2-1 Falcons (Anubis 5-13, Dust2 16-14, Mirage 13-7) | https://www.hltv.org/results?event=8932 | Series score matches; map order matches the stored veto. |

## 5. Not verified (left as-is, or blank)

* **Organizer documents** (Thunderpick's own bracket/results pages) were not opened for this session; the map scores rest on HLTV match pages. The published `flag` fields say so.
* **HLTV acceptance of the 07:30 / 11:55 local start times.** The match pages show local (CEST) clock times; the stored UTC starts (11:30 / 15:00) come from earlier sessions' `start_unix` reads and were not re-derived here. No pick depends on them any more because both series are final.
* **Live Hotspawn inventory beyond the retained snapshot.** Direct HTTPS access to `play.hotspawn.com` and `buffedlizard55-lab.github.io` is blocked in this sandbox (TLS `SSL_ERROR_SYSCALL`). The live 01:50Z build receipt and the lobby document were read through the retrieval tool instead, and are quoted as observations, not re-scraped data.
* **Live prices in the committed snapshot.** The committed `data/latest.json` is the 18 October 00:52Z snapshot; rebuilding it on 19 October correctly withholds its now-expired quotes. That is why a local build shows 0 priced rows while the production site (fresh refresh) shows the live count. It is a freshness behaviour, not a regression.
* **`site/*.html` legacy stubs** are untouched; they redirect to the current routes and were verified by the browser suite (six redirect scenarios).

## 6. Gates run on this branch

* `python -m unittest discover -s tests` — **409 tests OK** (14 new in `tests/test_finale_227839d2.py`).
* `python -m unittest discover -s audits` — 9 OK. `verification-c6` — 12 OK. `verification-95b588c2/test_integrity.py` — 5 OK.
* `verification-c6/audit_snapshot.py public/data/latest.json` — 0 failures.
* `python -m scripts.build` then `python -m scripts.validate` — 98 rows verified, 29 calculations reproduced, 618 links/assets, 20 checksums, 219 displayed rows.
* `npm run test:browser` — 32 page/viewport accessibility and no-overflow scans at 320/390/768/1440 px, six legacy redirects, seven expiry scenarios, four research-quote boundary cases.
* Visual check at 390 px and 1440 px (`/home/user/shots/`, not committed): result cards stack on a phone, the pick-record table collapses into cards, no horizontal overflow.


## Re-check after integration with PR #87 (`2b3e239`)

PR #87 (session `133fe7ca`) published its own `day_five_results` block and `results_section()` in
`scripts/build.py` while this branch was open. The merged page therefore renders:

| Element | Source after the merge | Page anchor |
| --- | --- | --- |
| Tournament-complete summary (champion, grand-final link, record headline) | this session (`event_summary`) | `#twc-final-summary` |
| Day-five results table, vetoes, pick outcomes, 19 Oct re-read note | PR #87 (`results_section`) | `#day-five-results` |
| Pick record, four picks with the price shown at the time | this session (`pick_record_block`) | `#pick-record` |
| Day-two map-orientation correction | this session (`maps_note` on the row) | `#day-two` |

Both final-day records are compared by `tests/test_finale_227839d2.py::CrossBlockConsistency`, so a
change to either one without the other fails the build. The day-five results are **not** rendered
twice: this session's earlier `finale_block` table was dropped in favour of #87's.

Archive gate re-checked after the merge: `overview()` for a 2026-10-18T01:00Z build keeps the
final-day guide and shows no archive notice; for a 2026-10-19T04:00Z build the hero exposes
"TWC final results" and "How our picks did", the start-here grid carries the TWC results card, the
`#twc-archive` notice replaces the stale unpriced-items notice, and `#day-five-guidance` is no longer
linked. `analysis_page()` renders `#twc-final-summary` and `#pick-record` only for the later build.

Not verified, and left untouched: map scores for the grand final were transcribed once from the HLTV
match page (the page itself carries that flag); the Aurora–Falcons local clock time is displayed but
no start time is inferred.
