# Day-3 results, Day-4 guidance, full coverage and deploy repair — verification record

Session `9a81b26f`, 2026-10-16 (UTC). Method: every factual claim below was read
from the linked primary source in this session unless marked *inherited*
(already verified by an earlier session and re-used without re-reading).
Retrieval-tooling reads are research; every published probability comes from
the Actions-runner refresh. Manual market reads were cache-busted and dated
by the payload `updatedAt` (standing irregularity
`polymarket-cached-manual-reads-2026-10-16`). HLTV displayed clocks are
reader-local (UTC−4 for this event) and were never read as UTC.

## A. Day 1 / Day 2 / Day 3 results — line by line

Source for all series scores (read twice, ~19:32Z and ~19:42Z):
<https://www.hltv.org/results?event=8932>

| # | Series (HLTV) | Published on site | This session |
|---|---|---|---|
| A1 | 9z 2-0 Aurora (14 Oct, [2399384](https://www.hltv.org/matches/2399384/9z-vs-aurora-thunderpick-world-championship-2026)) | Day-one table: Inferno 13-11, Nuke 13-1; luchov 1.61 | Series score **re-read and matched**. Map scores / rating / veto *inherited* (verified from the match page by 0e407ec7/a56d155f). |
| A2 | Falcons 2-0 NIP ([2399385](https://www.hltv.org/matches/2399385/falcons-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026)) | Day-one table (map detail flagged as betting-preview-sourced) | Series score **matched**; flag retained. |
| A3 | Legacy 2-0 PARIVISION ([2399386](https://www.hltv.org/matches/2399386/legacy-vs-parivision-thunderpick-world-championship-2026)) | Day-one table, maps blank | Series score **matched**; maps stay blank. |
| A4 | FURIA 2-0 BETBOOM ([2399387](https://www.hltv.org/matches/2399387/furia-vs-betboom-thunderpick-world-championship-2026)) | Day-one table, maps blank | Series score **matched**; maps stay blank. |
| A5 | Aurora 2-0 NIP ([2399408](https://www.hltv.org/matches/2399408/aurora-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026)), Falcons 2-1 9z ([2399409](https://www.hltv.org/matches/2399409/9z-vs-falcons-thunderpick-world-championship-2026)), BETBOOM 2-1 PARIVISION ([2399410](https://www.hltv.org/matches/2399410/parivision-vs-betboom-thunderpick-world-championship-2026)), FURIA 2-1 Legacy ([2399411](https://www.hltv.org/matches/2399411/legacy-vs-furia-thunderpick-world-championship-2026)) | Day-two table with maps/vetoes/ratings | All four series scores **matched**. Map-level detail *inherited* (verified per match page by 0e407ec7; Anubis 13-4 correction already on main). |
| A6 | **Aurora 2-0 9z, Group A decider** ([2399412](https://www.hltv.org/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026), read ~19:35Z) | New `day_three_results` | **Verified from the match page:** "Match over", Cache **13-11** (8:4; 5:7), Inferno **13-4** (9:3; 4:1); veto *Aurora removed Ancient, 9z removed Anubis, Aurora picked Cache, 9z picked Inferno, Aurora removed Nuke, 9z removed Dust2, Mirage left over*; kyxsan **33-20 / 1.45**, Jimpphat **31-18 / 1.31** (Rating 3.0 as printed). Only values visible in the read are published. |
| A7 | BETBOOM vs Legacy, Group B decider ([2399413](https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026), read ~19:35Z and ~19:50Z) | No result row; conditional Day-4 cards + review note | **LIVE 1-1 at both reads:** Nuke **16-13** BETBOOM (4:8; 8:4) (4:1 OT), Dust2 **13-11** Legacy (BETBOOM halves 7:5; 4:8), Mirage pending. Veto as recorded in the review note. No winner claimed. |

## B. Aurora roster change (the brief's premise, checked again)

- Current five on HLTV semi-final page 2399414 (read this session):
  **woxic, XANTARES, Wicadia, Jimpphat, kyxsan** — HLTV #6 / VRS #5 — identical
  to the Valve 2026-10-05 standings roster (Jimpphat, kyxsan, Wicadia, woxic,
  XANTARES, 1716 pts, vendored file line re-read this session).
- Dating *inherited and not contradicted*: rebuild completed 8 July 2026
  (kyxsan; Jimpphat + coach ash days earlier) — ~14 weeks before Day 4.
  The "recent roster change / onboarding" upset thesis is therefore **not
  supported** as a live factor, in agreement with sessions ab18fe2a/dedd2e34/
  1abe803f. What the record does support: Aurora lost to this exact opponent
  profile once (Day 1), then removed the losing map and reversed the series
  in two maps (A6). Day-4 guidance uses rest, map pool and price band —
  not roster recency.

## C. Day-4 semi-finals — what is verified, derived, and blank

| Item | State | Source |
|---|---|---|
| Semi 1 pairing FURIA vs Aurora, Bo3 (LAN), semi-final | **Verified** (page retitled `furia-vs-aurora-…`; Aurora slot filled) | [HLTV 2399414](https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026) |
| Semi 2 Falcons vs TBD, Bo3 (LAN) | **Verified as TBD** | [HLTV 2399415](https://www.hltv.org/matches/2399415/falcons-vs-betboom-legacy-winner-thunderpick-world-championship-2026) |
| FURIA lineup FalleN/KSCERATO/molodoy/YEKINDAR/yuurih; HLTV #4 | **Verified** (= VRS roster 5/5, 1829 pts) | HLTV 2399414 lineups + vendored standings |
| Map win-rates (3 mo) quoted in guidance | **Verified as printed** (Cache 42/56, Dust2 50/56, Mirage 60/62, Inferno 71/56, Nuke 64/78, Ancient 50/—(1 map), Anubis 0/75; FURIA first) | HLTV 2399414 map-stats table |
| Valve points: Legacy 1931, Falcons 1843, FURIA 1829, Aurora 1716, BETBOOM 1596, 9z 1543 | **Verified** in vendored `standings_global_2026_10_05.md` (same commit `eec4853` the live harvest fetched) | `data/vrs/` + harvest source checks |
| Model %: FURIA 62.2/Aurora 37.8; Falcons 40.4/Legacy 59.6; Falcons 73.9/BETBOOM 26.1 | **Computed with `scripts.vrs`** (Valve formula + published calibration); rendered by the builder from points, never hand-typed into HTML | `scripts/vrs.py` |
| Semi UTC starts 14:00Z / 17:00Z | **Derived, unverified** (displayed 10:00/13:00 + UTC−4 anchor; countdowns 18h24m/21h24m at ~19:35Z corroborate). Published as no start value. | HLTV 2399414/2399415 + decider anchors (3c8d1136) |
| Hotspawn listing / tier / points / format for semis | **Absent** at 19:31Z + 19:44Z harvests (83 rows, verified 83/83/83); `absent_from_board` for semi 1 | `research/harvest-9a81b26f/coverage-gap.md` |
| HLTV fan vote (29.2/70.8 on 2399414), HLTV Betting logos | Seen and **deliberately unused** (crowd/widget, no numeric pair; standing policy) | HLTV 2399414 |

Contrarian reads (labelled analysis on the page, never probability inputs):
Aurora = Day-4 swing (band + map pool + improving form vs rest/rating);
Legacy-if-through = model-backed lean if the market favours Falcons;
BETBOOM-if-through = pass (thin path). Fixed-award + streak-bonus scoring
(copied rule: tier S 7 / B 3 / C 2 from the feed, verified by 3c8d1136 over
102 rows) keeps the favourite EV-optimal; the exact streak formula remains
unpublished and unclaimed.

## D. Full-coverage audit (harvests 38955474182 + 38957108290)

- 19:31Z: 83 rows, verified 83/83/83, **21 open: 16 priced, 4 research-only,
  1 without any pick (1081515)**. Root cause traced row-by-row through
  `attempts[]`: Polymarket 5776037 + HLTV 2399660 are the same fixture
  (receipt `quotes/polymarket-5776037-betclic-nemesis.json`); labels failed
  on `Team Nemesis`/`Betclic`; VRS label `Betclic`; HLTV ranks exist (#71/#46)
  contrary to the collector's alias-gap reason. Book probe (same harvest):
  Pinnacle + Polymarket reachable; GG.BET/Thunderpick/Oddschecker 403 —
  so for gaps the honest order remains exchange → HLTV identity → Pinnacle →
  wide tier → VRS model → research rank.
- Fix: two sourced aliases in `data/identities.json` (fixture parity +
  5/5 roster corroboration read from HLTV 2399660 this session:
  Betclic = Demho/Prism/ex1st/Qlocuu/ultimate; Nemesis =
  mag1k3Y/Sdaim/tex1y/SELLTER/r3salt). No code change, no fuzzy matching.
- 19:44Z: **21 open, 17 priced (6 exchange, 2 exchange_wide, 9 model_vrs),
  4 research-only, 0 without a pick.** 1081515 priced strict-exchange
  (Nemesis 0.69 at that observation). Research-only rows keep blank
  percentages with published reasons: 1081521 (rank pair #80/#226),
  1081522 / 1081861 / 1081863 (one-sided ranks) — *inherited reasons,
  re-read in the harvest snapshot*. Model comparison for 1081515 correctly
  unavailable (duplicate Betclic label, no lineup on the market path).
- Independent checks on the adopted snapshot: `audit_snapshot.py` **0
  failures** (data + built public copy), quarantine **0 withheld**,
  validator **17 calculations reproduced, 566 links, 20 checksums**.

## E. Deploy repair — measurement, fix, proof standard

Measured via the Actions jobs API (sandbox cannot read run logs; EOF on the
log/artifact hosts — recorded, not worked around):

- 38936303441: verify-build refresh done 17:00:47Z; deploy 17:01:52–17:01:57Z
  (success); verify step 17:01:57→17:01:57Z (failure). Deployment 7124811549
  created 17:01:40Z, updated 17:02:00Z — verification raced propagation.
- Live `build-info.json` at ~19:30Z: revision `40b13d3`, `built_at`
  17:00:47Z, 83 rows — **that "failed" run's build was live**. Same shape
  38902730567 (12:46Z) and PR #41 push run 38955319335 (failure, 19:3xZ).
- Pages API: `build_type: legacy`, source `main:/` — dual-build race on
  pushes remains possible; settings change not attempted from a branch.
- Fix `scripts/verify_live.py` (poll ≤360s, per-attempt cache-bust, exact-byte
  or coherent-newer standard, receipt keys preserved + attempts/elapsed)
  + 11 unit tests + `pages.yml` (checkout + `contents: read` in deploy job,
  `python3 scripts/verify_live.py`, this branch in push triggers).
  **Proof pending:** first main publish runs after merge must go green;
  recorded as flagged until then.

## F. Local verification performed (this branch, 16 Oct evening)

- `.venv/bin/python -m unittest discover -s tests` → **206 OK** (195 inherited
  + 11 new verify-live). One earlier run showed 3 errors against stale
  committed root HTML vs new data; after `stage_legacy` the suite is green —
  committed root fallback and `data/latest.json` must land together (they do).
- audits 9 OK · verification-c6 12 OK · integrity 5 OK.
- `scripts.build` (83 rows, 17 priced) + `scripts.validate` (public **and**
  `--site .` root fallback) green; row audits 0 failures; quarantine 0.
- `npm run test:browser` → 32 accessibility/no-overflow scans at
  320/390/768/1440px + 7 expiry scenarios passed.
- Render spot-checks: `#day-four-guidance`, `#day-three-results` present;
  exec-summary Day-4 links present; model 62.2% rendered from points.

## G. Irregularities (all on Flagged for Review)

`deploy-verify-spurious-failure-2026-10-16` ·
`twc-semifinals-not-listed-2026-10-16` ·
`fixture-1081515-alias-2026-10-16` (resolved) ·
`group-b-decider-live-2026-10-16`. Nothing blocking; nothing inferred.
