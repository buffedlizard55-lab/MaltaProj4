# Session 6dd6f287 — closing the no-percentage gap, and what could not be closed

**Date:** 22 October 2026, 01:15–03:00 UTC
**Branch:** `arena/6dd6f287-maltaproj4` (from `main` `40e1fab`)
**Board at the start of the session (live site, 00:55Z snapshot):** 35 open CS2 fixtures,
**35 with a pick**, **28 with a published win probability** (8 market, 20 originated VRS model),
**7 research-only with no percentage**, 0 unresolved.

Every fixture already had a pick. The real gap was *percentages*, so this session worked on
that and on the verification of the three rows that still cannot honestly be given one.

## 1. What was read, and when

| Source | Read | What it established |
| --- | --- | --- |
| [Hotspawn lobby / CS2 pick'ems](https://play.hotspawn.com/cs2-pickems) + fixtures API | via the published board's own snapshot metadata (site `build-info.json`, 00:55Z) | fixture inventory only; never a probability |
| [HLTV Valve global ranking, 22 Oct 2026](https://www.hltv.org/valve-ranking/teams/2026/october/22) | 22 Oct ~01:20Z | dated heading "Valve global ranking on October 22nd, 2026"; **points and roster per club** (`#1 Vitality … 1993 Valve points`) |
| [HLTV NEXORA vs K27](https://www.hltv.org/matches/2399846/nexora-vs-k27-winline-mpkbk-cis-lan-season-9) | 22 Oct ~01:10Z | NEXORA **VRS #282** (HLTV world: unranked), K27 **VRS #31** / HLTV #46 |
| [HLTV FORZE Reload vs LFO 10](https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12) | 22 Oct ~01:25Z | LFO 10 **VRS #157**, HLTV world unranked |
| [HLTV Morningstar vs NEXVOID](https://www.hltv.org/matches/2399584/morningstar-vs-nexvoid-macemedia-void-autumn-cup-2026) | 22 Oct ~01:25Z | Morningstar **VRS Unranked**, NEXVOID **VRS #72** |
| [HLTV TitanFlow team page](https://www.hltv.org/team/14021/titanflow) | 22 Oct ~01:55Z | **no Valve rank, no world rank, no roster**, no upcoming matches |
| [HLTV DFRAG Invitational 2026](https://www.hltv.org/events/9414/dfrag-invitational-2026) | 22 Oct ~01:58Z | Staqued in Group B, no ranking shown |
| [EGamersWorld benched gods vs TitanFlow](https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn) | 22 Oct ~01:15Z | **1.8 / 1.8** both sides — placeholder, rejected |
| [EGamersWorld Morningstar vs NEXVOID](https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/morningstar-vs-nexvoid-e_MT2tamL) | 22 Oct ~01:10Z | **1.8 / 1.8** placeholder |
| [EGamersWorld FlyQuest vs Staqued](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3) | 22 Oct ~01:58Z | **1.8 / 1.8** placeholder |
| [Valve standings 2026-10-05](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | 22 Oct ~01:20Z (GitHub API) | K27 #32, NEXVOID #113, FlyQuest #86, ex-RUSTEC #92 **and** #152, ex-Zero Tenacity #93, Saint Sinners #158, FORZE Reload #84, benched gods #157 **and** #329; **no NEXORA, Morningstar, TitanFlow, LFO 10 or Staqued row** |
| [Valve `model/fit.js`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/model/fit.js) · [`modelfit.png`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/modelfit.png) | unchanged, already in the repo | formula (RD 75) and published calibration slope 0.7986 |

Sandbox note: this session's shell could reach `api.github.com` only, so every other page was read
through the retrieval tool and its exact URL is listed above. No page was paraphrased into a number.

## 2. What changed

**`scripts/vrs_mirror.py` (new).** Valve's GitHub standings file is monthly (newest is 2026-10-05).
A club that entered the ranking later, or that sits below the file's publication cutoff, has no row,
so the two-team line cannot run and the fixture fell to a research pick with no percentage. HLTV
publishes the *same* Valve ranking continuously, dated, with the same points and the same roster per
club, so it is now read **only** for rows still unpriced after every market tier and the official-file
model line.

- Reuses `scripts.vrs.expected` (Valve `fit.js`, RD 75, which reduces to the Glicko expected score),
  `calibrated` (Valve's published slope 0.7986, applied symmetrically), `identify` (Valve's
  three-player roster-continuity rule) and the eight-hour evidence window. No new constant.
- Fails closed on: a page whose rows say *HLTV points* instead of *Valve points*, a missing dated
  heading, fewer than 100 parsed rows, non-monotonic positions, duplicate labels without a lineup,
  or a club absent from the page. Each is a recorded miss; the row keeps its research-only pick.

**`scripts/refresh.py`.** Runs the mirror only when at least one open row is still unpriced, after
`vrs.apply` and before the research tiers; a fetch/parse failure becomes a `vrs_mirror` finding and
an attempt row, never a price.

**`scripts/build.py`.** New method `model_vrs_mirror`: label *Our VRS model line · HLTV Valve
ranking*, model-kind badge, `is_model()` used everywhere the official-file model was special-cased,
the dated page linked on the row, and a sources-page paragraph describing the tier and its limits.

**`scripts/validate.py`.** `validate_mirror_row` recomputes the probability from the stored points,
checks the calibration constants, provenance (hltv.org page for the ranking, Valve's repo for the
formula and calibration), roster identity, freshness, the eight-hour/62-day windows, and asserts the
tier was only used for a label Valve's own file does not resolve uniquely (checked against the
vendored copy when the recorded commit matches).

**`verification-c6/audit_snapshot.py`.** An independent branch for the new method, with its own
implementation of Valve's expectation (`vrs_probability`) and the same provenance rules, so the
publisher's hard gate reproduces the row instead of quarantining it.

**Tests.** `tests/test_vrs_mirror_6dd6f287.py` — 23 tests: the parser rejects the HLTV *world*
ranking page (wrong points label), a missing date header, a short or unordered table; identity uses
Valve's roster rule; pricing, pick orientation, equal-points behaviour, the refusal cases (unlisted
club, duplicate label without a lineup) and the never-overwrite-a-market rule; validator acceptance
and rejection (altered points, non-HLTV URL, missing flag, short ranking, stale inputs); and wiring
checks for build/refresh/validate.

## 3. Verification performed

```
python -m unittest discover -s tests                      → 625 tests OK (602 before, +23)
python -m scripts.build --data data/latest.json --out …    → 9 primary pages + 6 legacy redirects
python -m scripts.validate --data data/latest.json --site …→ 75 rows, 11 calculations, 15 pages,
                                                             649 links/assets, 20 checksums
python verification-c6/audit_snapshot.py data/latest.json  → 0 failures
```

End-to-end smoke test on a throwaway copy of the snapshot (`/tmp`, never committed): fixture
`1081597` converted from `research_vrs_single` to `model_vrs_mirror` with the recorded per-team
inputs produced *12* reproduced calculations (11 before), passed `scripts.validate`, passed the
independent auditor with **0 failures**, and `scripts.quarantine` withheld **0** rows. The numbers
used in that smoke test were not published: see §4.

## 4. Irregularities flagged for review

1. **TitanFlow has no Valve rank today.** A note recorded on 21 October cited TitanFlow at VRS #234
   with 664 points. Read directly on 22 October, HLTV's TitanFlow page shows `Valve ranking VRS -`,
   `World ranking -`, "TitanFlow does not currently have a roster" and no upcoming matches. The
   earlier figure is **not reproducible** and was not carried forward; the smoke test in §3 used it
   only to exercise the validator. Published note:
   `6dd6f287-titanflow-no-vrs-2026-10-22` (published on Flagged for Review).
2. **Three fixtures still publish no percentage, and the reason is a missing ranking, not a missing
   pick.** Morningstar (VRS Unranked), TitanFlow (no rank/roster) and Staqued (unranked, absent from
   Valve's file) each block the two-team formula; all three listings read on EGamersWorld serve the
   identical 1.8/1.8 placeholder, which this project rejects as a placeholder. Published note:
   `6dd6f287-egw-placeholder-1.8-2026-10-22` (published on Flagged for Review).
3. **Provenance limit of the new tier.** HLTV's page is a dated *rendering* of Valve's ranking, not
   Valve's own file. The numbers are Valve's; the delivery is second-hand. The row says so, links
   the dated page and keeps the official filings date it superseded. Published note:
   `6dd6f287-model-vrs-mirror-tier` (published on Flagged for Review).
4. **Live-markup risk, stated rather than hidden.** The parser was exercised against the retained
   HLTV ranking page in `research/harvest-76712ccc/HLTV_world_ranking.html` (same ranked-team
   markup, points label flipped to Valve's wording) and against that page unmodified, where it
   correctly refuses. If HLTV changes the markup, the tier records a parse miss and no row changes.

## 5. Expected effect on the next refresh

Four of the seven no-percentage rows should now carry a percentage from the mirror tier
(K27 vs NEXORA, FORZE Reload vs LFO 10, and the two ex-RUSTEC fixtures, where Valve's file repeats
the `ex-RUSTEC` label and HLTV's page lists one row per club). The remaining three keep a research
pick with their stated limitation until a book publishes an asymmetric two-way line or the clubs are
ranked. Nothing is assumed about which rows qualify at refresh time: the tier either resolves both
clubs from the page it actually read or records why it did not.
