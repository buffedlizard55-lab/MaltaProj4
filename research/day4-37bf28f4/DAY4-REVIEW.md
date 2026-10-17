# Day-4 review, full-pick coverage audit and mobile exec-summary check — session 37bf28f4 (17 October 2026)

Scope claimed in `COORDINATION.md` before starting: `research/day4-37bf28f4/**`,
`research/harvest-37bf28f4/**`, `data/analysis.json`, `scripts/twc_day4_37bf28f4.py`,
`data/latest.json` (read-only this round), `scripts/build.py`, `site/**`, `assets/style.css`,
`index.html`, `README.md`, `data/review-notes.json`.

Everything below was read on 17 October 2026 between 00:50Z and 01:10Z through the sandbox's
document-retrieval path. Field-level receipts: `research/harvest-37bf28f4/day4-live-reads.json`.
No value is inferred; where a source did not expose a field it is recorded as absent.

## 1. Day 1–3 results, re-verified line by line

| Day | Series (winner first) | Score | Source read |
| --- | --- | --- | --- |
| 14 Oct | 9z–Aurora | 2-0 | https://www.hltv.org/results?event=8932 · match page https://www.hltv.org/matches/2399384/9z-vs-aurora-thunderpick-world-championship-2026 |
| 14 Oct | Falcons–Ninjas in Pyjamas | 2-0 | results list |
| 14 Oct | Legacy–PARIVISION | 2-0 | results list |
| 14 Oct | FURIA–BETBOOM | 2-0 | results list |
| 15 Oct | Aurora–Ninjas in Pyjamas | 2-0 | match page https://www.hltv.org/matches/2399408/aurora-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026 |
| 15 Oct | Falcons–9z | 2-1 | results list |
| 15 Oct | BETBOOM–PARIVISION | 2-1 | results list |
| 15 Oct | FURIA–Legacy | 2-1 | results list |
| 16 Oct | Aurora–9z | 2-0 | match page 2399412 (verified by session bca04a82; re-checked against the results list) |
| 16 Oct | BETBOOM–Legacy | 2-1 | match page 2399413 (verified by session bca04a82; re-checked against the results list) |

Verified details that the day-4 block publishes:

* **9z 2-0 Aurora (14 Oct)** — veto: 9z removed Anubis, Aurora removed Ancient, **9z picked Inferno**,
  **Aurora picked Nuke**, 9z removed Mirage, Aurora removed Cache, Dust2 left over. Inferno 13-11
  (halves 8:4, 5:7), Nuke 13-1 (11:1, 2:0). luchov 38-20, +6.61% swing, 97.4 ADR, 86.8% KAST, 1.61 rating.
  HLTV's report also calls Aurora "the fifth-ranked team in the VRS" and records that 9z gained 62 VRS points.
  Sources: match page 2399384 and https://www.hltv.org/news/45718/9z-beat-aurora-2-0-to-kick-off-twc-2026
* **Aurora 2-0 Ninjas in Pyjamas (15 Oct)** — Group A elimination match; Ninjas in Pyjamas picked Cache,
  Aurora picked Dust2, Nuke left over. Cache 13-9 (7:5, 6:4), Dust2 13-7 (9:3, 4:4). Wicadia 45-25, 1.65 rating.
  Source: match page 2399408.
* **Structure across the ten series** — six finished 2-0 and four needed a third map; both opening-match
  losers (Aurora, BETBOOM) reached the semi-finals by winning their next two; 9z–Aurora is the only pairing
  that met twice and it split 1-1. Source: the results list above.

## 2. Aurora's "recent roster change" — premise checked, and it does not hold for this week

HLTV's announcement for the rebuild (https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan,
dated 8-7-2026) puts kyxsan's arrival from Falcons on **8 July 2026** and Jimpphat plus coach ash
"earlier on Friday" (3 July 2026), replacing MAJ3R, soulfly and Fabre. The five in Malta are XANTARES,
woxic, Wicadia, Jimpphat, kyxsan, with ash coaching. There is no October change and no player still being
onboarded, so the requested "recent roster change" factor cannot be used for day four — the block states
this explicitly rather than inventing an onboarding angle.

## 3. Scoring facts that change the contrarian argument

* Official rules page (https://play.hotspawn.com/how-it-works): points for every correct pick, "higher tier
  matches reward more points", **"get bonus points for consecutive correct picks. The longer your streak,
  the bigger the bonus"**, weekly leaderboard reset, free to play, and "picks lock 5 minutes before the
  scheduled start time".
* Hotspawn's own fixture API, read at 00:50Z: every CS2 row carries `lock_offset_sec: 360`, `base_points`,
  `offered_points` and a `points_breakdown` object (game / tier / series / stage / tournament multipliers;
  tier c = 2 points at 1.25/1/1/1/1, tier b = 3 at 1.25/1.5/1/1/1). None of those fields depends on the
  crowd figure, so a pick earns the same whether it follows or fades the crowd.
* Neither Thunderpick semi-final is on the feed, so a TWC pick scores nothing in the pick'em; the streak
  risk lives on the board rows (tiers S/B/C), not on the analysis cards. This is the day-4-specific
  consequence of the streak bonus and it is now published as a day-4 point.

## 4. Coverage audit — every open fixture has a pick

Read from the live board rather than assumed: `picks.html` and `unresolved.html` on
https://buffedlizard55-lab.github.io/MaltaProj4/ were read at 01:02Z and the site banner reports the
00:43–00:45Z snapshot with **21 open fixtures: 17 with published probabilities (8 market, 9 model),
4 labelled research-only picks with no percentage, 0 without any supported pick**. The unresolved page
lists every non-market row with its limitation and the gate it failed. The two Thursday fixtures that an
earlier session flagged as identity-blocked (BET-M 33, Leo Team) remain flagged, not aliased — see
`data/review-notes.json` entries `identity-bet-m-33` and `identity-leo-team`.

## 5. What this session added

1. **Day-4 block** (`data/analysis.json` → `day_four_guidance`), applied by
   `scripts/twc_day4_37bf28f4.py` (idempotent, re-runnable): the scoring note rewritten from the API's own
   fields, the streak-bonus note, the Sunday schedule note, the group-structure note, and the day-2 point
   split so the map detail is sourced to the match page instead of the results list.
2. **New "Unresolved & limitations" block** rendered inside the day-4 guidance
   (`#day-four-guidance-unpriced`), carrying the third-place decider and grand final — both unpriced
   because their participants do not exist yet — plus the standing limitation for every other non-market
   row on the board, each with its source.
3. **Executive-summary pointer**: the summary now carries a notice that counts the TWC items without a
   price and links straight to that block and to `unresolved.html`, so the phone reader is one tap from
   the picks and one tap from the limitations.
4. **Withdrawal**: the earlier "higher-ranked side won eight of the ten series" sentence was removed here
   (and in the block's own limitations list), because no primary source with per-series rank granularity
   was re-read. Flagged on the review page as `withdrawn-rank-count-2026-10-17`.
5. **Lock-time discrepancy recorded** as `lock-time-wording-2026-10-17`: the rules page says five minutes,
   the API's per-fixture `lock_offset_sec` is 360 (six minutes); the board keeps using the earlier,
   conservative value.

## 6. Verification run for this change set

| Check | Result |
| --- | --- |
| `python -m unittest discover -s tests` | 279 tests, OK |
| `python -m unittest discover -s audits -p 'test_*.py'` | 9 tests, OK |
| `python verification-95b588c2/test_integrity.py` | 5 tests, OK |
| `python -m unittest discover -s verification-c6 -p 'test_*.py'` | 12 tests, OK |
| `python -m scripts.build` | 9 primary pages + 6 legacy redirects, 83 sourced rows, 17 priced, 4 unresolved |
| `python -m scripts.validate` | 83 rows verified against the snapshot, 17 calculations reproduced, 573 links, 20 checksums, 202 displayed rows |
| `npm run test:browser` | 32 accessibility/no-overflow scans at 320/390/768/1440px + 7 expiry scenarios, OK |

## 7. Limitations this session did not close

* The two Sunday matches cannot be priced until their participants exist and an operator opens a market.
  No placeholder number is published for them.
* Liquipedia has no page for this event at `/counterstrike/Thunderpick_World_Championship/2026` ("There is
  currently no text in this page."), so no wiki cross-check exists for the schedule, rosters or results.
* Live source collection still runs on GitHub Actions rather than in this sandbox: the shell here can only
  reach GitHub and the package registries, so the committed `data/latest.json` remains the bootstrap
  snapshot and production refreshes hourly from the runner.
