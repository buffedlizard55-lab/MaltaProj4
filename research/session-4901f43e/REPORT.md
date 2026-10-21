# Session 4901f43e — independent verification of the published CS2 board

Branch `arena/4901f43e-maltaproj4`. All times UTC. Read window for every primary source in this
report: **2026-10-21T20:11:21Z → 2026-10-21T20:41:51Z**, recorded per receipt in
[`receipts-2026-10-21.json`](receipts-2026-10-21.json).

Repository state verified against:

| Thing | Value | How it was read |
| --- | --- | --- |
| `origin/main` at report time | `179789e` (PR #121 merged) | `git fetch origin main` |
| Live published build | revision `884f36e`, built `2026-10-21T20:47:31Z`, 75 rows | [build-info.json](https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) |
| Live board content | 13 open CS2 matches, 13 with a pick, 11 with a win probability, 0 unresolved | [index.html](https://buffedlizard55-lab.github.io/MaltaProj4/) |
| Valve standings the model pins | `standings_global_2026_10_05.md`, commit `eec4853d`, 380 rows | `data/vrs/meta.json` + api.github.com |

Nothing in this report is inferred. Where a value could not be read, it is written as *not read* or
*blank*, and the reason is given.

---

## 0. Scope discipline

Files this session wrote — all of them its own, none claimed by another session:

- `research/session-4901f43e/receipts-2026-10-21.json` — 15 dated receipts, each extract sha256'd
- `research/session-4901f43e/audit-baseline-2026-10-21.json` — machine-readable auditor result
- `research/session-4901f43e/REPORT.md`, `REQUESTS.md` — this file and the cross-session requests
- `research/harvest-4901f43e/**` — written by CI, not by hand
- `verification-4901f43e/audit_published_claims.py`, `ACCEPTANCE-AUDIT.md`
- `scripts/probe_4901f43e.py`, `.github/workflows/harvest-4901f43e.yml`
- `tests/test_session_4901f43e.py`
- `COORDINATION.md` — this session's own rows only

Files this session deliberately did **not** touch, because other sessions hold them:
`scripts/{build,refresh,hltv,vrs,core,validate,books}.py`, `data/{identities,book-receipts,
lineup-receipts,review-notes,latest}.json`, `site/assets/*`, the root staged `*.html`,
`README.md`, `.github/workflows/pages.yml`, `verification-c6/**`, `research/quotes-76712ccc/**`,
`research/session-db1f35c5/**`. Every change needed in those files is written as a request in
[`REQUESTS.md`](REQUESTS.md) instead of being made here.

---

## 1. How the sources were read, and what the runner can see

Two different network paths exist in this project, and they do not see the same internet:

1. **Authoring fetch path** (used for every receipt here): reached HLTV `/matches/…`, `/team/…`,
   `/results`, Polymarket's gamma API, Strafe, bo3.gg, maisesports/PandaScore, dfrag.gg and
   Liquipedia with **HTTP 200**. Valve's standings repository was read through the
   `api.github.com` contents endpoint, because `raw.githubusercontent.com` is not reachable from
   the authoring sandbox.
2. **CI runner** (`scripts/probe_4901f43e.py`, run 39674050906, committed to
   `research/harvest-4901f43e/probe.json`): refused on **6 of 6** HLTV URLs probed, on
   EGamersWorld and on Liquipedia; readable on Polymarket (both endpoints), Valve via
   `api.github.com`, dfrag.gg, Strafe and maisesports. One host, bo3.gg, answered `200` but did not
   contain the expected marker text.

| Classification | Count | Hosts |
| --- | --- | --- |
| `readable` | 6 | gamma-api.polymarket.com (×2), api.github.com, dfrag.gg, strafe.com, maisesports.com.br |
| `refused` (403) | 8 | hltv.org (×6: `/matches/2399865`, `/matches/2399867`, `/matches/2399696`, `/matches/2399888`, `/team/13833/zetta`, `/results?event=9452`), egamersworld.com, liquipedia.net |
| `served-without-marker` | 1 | bo3.gg |

The probe used the repository's own project user agent, retried once after five seconds, and never
attempted a bypass, a cache or a mirror. **Consequence:** every HLTV citation anywhere in this
repository is unverifiable from CI and rests on an authoring-path read. That is irregularity 4.

No receipt in this session was produced through the runner. Each one names the path it used.

---

## 2. Receipt register

| ID | Source | What it establishes |
| --- | --- | --- |
| R1 | [gamma-api.polymarket.com/markets/6001634](https://gamma-api.polymarket.com/markets/6001634) | `outcomePrices ["0.385","0.615"]`, sum 1.0, spread 1.0 point, liquidity $3,888.256, start `2026-10-21T22:00:00Z`, active and accepting orders |
| R2 | [gamma-api.polymarket.com/events/1227336](https://gamma-api.polymarket.com/events/1227336) | Event description: "the Counter-Strike **Round 5** match between Alianza Lima Esports and Los Ninos in the CCT South America Series 7 Group Stage"; `2026-10-21T22:00:00Z` |
| R3 | [Valve VRS #357 Zetta detail sheet](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/details/2026_10_05/0357--zetta--antuanette-babyrage-notjuanjo-slayerhz-zockie.md) | rank 357, 473 points (`final_rank_value` 472.9), roster Antuanette, BabyRage, Notjuanjo, Slayerhz, zockie |
| R4 | [Valve standings_global_2026_10_05.md](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) | the only official point values the model may use: #86 1093, #119 971, #136 878, #157 811, #329 516, #357 473 |
| R5 | [hltv.org/matches/2399865](https://www.hltv.org/matches/2399865/zetta-vs-los-ninos-cct-2026-south-america-series-7) | "Swiss round 5 (teams with a 2-2 record)", BO3, both five-player lineups verbatim, **no numeric two-way line** in the betting table, crowd vote 75/25 |
| R6 | [hltv.org/team/13833/zetta](https://www.hltv.org/team/13833/zetta) | world rank 241, HLTV's own VRS mirror 368, roster identical to R3/R5, **exactly one** upcoming match |
| R7 | [bo3.gg ALE scoreboard](https://bo3.gg/matches/damajuana-vs-alianza-lima-esports-14-10-2026) | "Alianza Lima Esports" listed with zockie, Antuanette, BabyRage, NotJuanjo, Slayerhz — 5/5 identical to R3 and R5 |
| R8 | [hltv.org/results?event=9452](https://www.hltv.org/results?event=9452) | match `2399802` "Zetta 1-0 realgotis22", 2026-10-19 |
| R9 | [maisesports / PandaScore ALE](https://maisesports.com.br/partidas/realgotis22-vs-alianza-lima-esports-2026-10-19) | the same 2026-10-19 Round-4 realgotis22 match attributed to **Alianza Lima Esports**; plus ALE vs Los Niños `2026-10-21 19:00 BRT = 22:00Z, MD3` |
| R10 | [strafe.com CCT SA Series 7](https://www.strafe.com/event/2026-cct-south-america-series-7-75c83e/) | both labels present as separate competitors; "Zetta vs SUKEBAN" `2026-10-15T16:05:00Z`; crowd votes Zetta 24 / LOS NINOS 76 |
| R11 | [hltv.org/matches/2399867](https://www.hltv.org/matches/2399867/zetta-vs-los-ninos-cct-2026-south-america-series-7) | the requested id **serves Alliance vs FaZe, RLG Tesla Cup 2026, 2026-10-27** — not Zetta |
| R12 | [hltv.org/matches/2399696](https://www.hltv.org/matches/2399696/benched-gods-vs-titanflow-cct-2026-challengers-europe-series-8) | "Match postponed", **zero** team names on the page (both slots are placeholder SVGs), BO3, `2026-10-22T11:00:00Z` |
| R13 | [hltv.org/matches/2399888](https://www.hltv.org/matches/2399888/ground-zero-vs-off-chops-dfrag-invitational-2026) | Ground Zero apocdud, Omichella, vision, **tucks (Sub)**, sliimey; Off Chops viridian, dexter, Liazz, Gratisfaction, damyo; `2026-10-26T03:00:00Z`; **no numeric two-way line**; crowd vote 50/50 |
| R14 | [dfrag.gg rebrand announcement](https://dfrag.gg/counterstrike/news/thunder-downunder-core-rebrands-as-off-chops/) | published 2026-10-11: the THUNDER dOWNUNDER core rebrands as Off Chops, new five viridian, Liazz, dexter, Gratisfaction, damyo |
| R15 | [liquipedia.net/counterstrike/Zetta](https://liquipedia.net/counterstrike/Zetta) | **page does not exist** — a negative result, recorded so nobody re-derives the alias from it |

Receipt integrity is enforced twice: `tests/test_session_4901f43e.py` recomputes every sha256, and
`verification-4901f43e/audit_published_claims.py` refuses to run against an edited extract
(both are covered by negative tests that tamper with a temporary copy).

---

## 3. Verdicts on the four fixtures that had no percentage

These are the four fixtures session `db1f35c5` resolved in PR #121. Each was re-read from primary
sources here, independently, and each verdict below is what the sources support.

### 3.1 `1082837` Zetta vs LOS NINOS — **CONFIRMED**, and the pick side is now correct

The market that prices this fixture is Polymarket `6001634` inside event `1227336`. It matches the
Hotspawn fixture on exact UTC start (`2026-10-21T22:00:00Z`) and differs only in the label for one
competitor: the market says *Alianza Lima Esports*, Hotspawn says *Zetta*.

`scripts.core.quote_polymarket` was replayed offline against the R1 values and accepts the quote at
tier `exchange` (spread 0.01 ≤ 0.25, liquidity $3,888.26 ≥ $100, prices sum to 1.0, bid < ask,
observation fresh): **LOS NINOS 0.615 / Zetta 0.385** at read time.

The board published at `2026-10-21T20:47:31Z` prints **LOS NINOS 80.5%** for the same market. Both
numbers come from market `6001634`; the market moved between 20:12Z and 20:47Z. Neither is an
error, and this session does not treat line movement as a discrepancy. What matters is the side:
before the alias existed the row was a rank-only research pick for **Zetta**, the 38.5% underdog.
It now picks the market favourite.

The alias itself is proven four independent ways (§4.1). Note that the alias register merged with a
citation this session shows to be wrong (§6.1); the alias conclusion does not depend on that
citation, because R3/R5/R7/R8/R9/R10 carry it alone.

### 3.2 `1081597` benched gods vs TitanFlow — **CONFIRMED as a research pick with no percentage**

HLTV `2399696` is stamped **"Match postponed"** and names **zero** teams (R12), so the fixture
cannot be priced from that page and cannot even be oriented from it. Both teams were instead
verified from their Lower Bracket Round 2 feeders in the same event, which is what
`data/lineup-receipts.json` now stores.

Replayed here against Valve's file with those lineups:

| Label | Valve row | Points | Roster overlap | Result |
| --- | --- | --- | --- | --- |
| benched gods | #157 | 811 | **5/5** (Wign, facer, norescue, yoyoS2, K014NZ) | identified |
| benched gods | #329 | 516 | — | correctly *not* selected; without a lineup the label is ambiguous and `vrs.identify` refuses it |
| TitanFlow | — | — | — | **not listed in the Valve global standings** |

Exactly one side resolves, so the pipeline publishes a one-sided research pick (**benched gods**)
with `probabilities: null`. That is the honest outcome: a two-sided percentage would require a
points value for TitanFlow that no official source publishes. The live board shows
"Research pick: benched gods — Research only · no percentage" ✓.

### 3.3 `1082858` Ground Zero vs Off Chops — pick direction **CONFIRMED**, published percentage **does not replay**

Off Chops is the THUNDER dOWNUNDER core rebranded (R14, published by the tournament organiser
itself on 2026-10-11), and HLTV's lineup for this fixture (R13) shares **4 of 5** players with
Valve's #119 row (`damyo` in for `TjP`). Ground Zero's HLTV lineup shares **4 of 5** with Valve's
#136 (`tucks`, marked *Substitute* on HLTV, in for `hazr`). Both clear `ROSTER_OVERLAP = 3`.

Valve publishes 971 (#119) against 878 (#136) — a **93-point** gap. The repository's own model
(`scripts/vrs.py`: `G = 0.9728209910`, `SLOPE = 0.7986`) turns that into raw `0.627335` and
calibrated **Off Chops 60.2% / Ground Zero 39.8%**. That is exactly what the live board prints.

The merged research note publishes **40.9% / 59.1%** for the same fixture and cites the same two
Valve rows. That split does not replay: 59.1% requires a points gap of **82.85**, and Valve's gap
is 93. See §5 and §6.3. This session does not edit the note (another session owns it); the request
is logged in `REQUESTS.md`.

### 3.4 `1082860` FlyQuest vs Staqued — **CONFIRMED blank**

FlyQuest resolves uniquely to Valve #86, **1093** points (R4). **Staqued does not appear anywhere
in Valve's 380-row global standings**, so no official points value exists for it. The row keeps a
research pick (**FlyQuest**) and `probabilities: null`, which is what the live board shows. No
percentage was invented for it here either.

---

## 4. Identity evidence

### 4.1 Zetta ≡ Alianza Lima Esports — four independent proofs

The alias is what allows a Polymarket price to be attached to a Hotspawn fixture, so it was checked
four separate ways. Any one of them is weak; together they are not.

1. **Same real-world match, two labels.** HLTV attributes the 2026-10-19 Round-4 match against
   realgotis22 to *Zetta* (`2399802`, R8). maisesports/PandaScore attributes the same date, same
   round, same opponent to *Alianza Lima Esports* (R9).
2. **Identical five players.** bo3.gg's "Alianza Lima Esports Scoreboard" (R7) lists zockie,
   Antuanette, BabyRage, NotJuanjo, Slayerhz. HLTV's Zetta lineup (R5) and Valve's #357 Zetta
   roster (R3) list the same five. **5/5 both ways.**
3. **Second instance of the label swap.** The 2026-10-15 SUKEBAN match is "Zetta vs SUKEBAN" at
   `2026-10-15T16:05:00Z` in Strafe's structured data (R10) and "Alianza Lima Esports vs SUKEBAN"
   at 16:00Z on Polymarket and maisesports (R9).
4. **No competing slot.** HLTV's Zetta team page lists **exactly one** upcoming match (R6), and
   today's 22:00Z Round-5 slot is Zetta-vs-LOS-NINOS on HLTV and Strafe while being
   ALE-vs-Los-Niños on Polymarket and maisesports. There is no second fixture the market could be
   referring to.

Liquipedia has no Zetta page at all (R15) — recorded as a negative result so the alias is not
mistakenly thought to rest on it.

**Trap recorded for future sessions:** Strafe carries *both* labels as separate competitors and
splits their matches between them (R10). A naive name-join on Strafe double-counts this roster, and
its standings columns cannot be summed. The alias must be anchored on exact opponent pair **and**
exact UTC start, which is what `scripts.core.orientation` already requires.

### 4.2 Off Chops ≡ THUNDER dOWNUNDER

| Evidence | Content |
| --- | --- |
| R14 (dfrag.gg, organiser's own site, 2026-10-11) | THUNDER dOWNUNDER core rebrands as **Off Chops**; new five viridian, Liazz, dexter, Gratisfaction, damyo; departed aliStair, TjP, asap |
| R13 (HLTV `2399888`) | Off Chops lineup viridian, dexter, Liazz, Gratisfaction, damyo — identical set to R14 |
| R4 (Valve #119) | THUNDER dOWNUNDER, 971 points, roster dexter, Gratisfaction, Liazz, TjP, viridian |
| Overlap | **4/5** (`damyo` for `TjP`) ≥ `ROSTER_OVERLAP = 3` |

Valve's file has **no row named "Off Chops"**. The label reaches #119 only through the alias
register: `core.norm('THUNDER dOWNUNDER') == core.norm('Off Chops') == 'offchops'`. That is pinned
by a test in this session so the distinction cannot silently disappear.

### 4.3 Roster-continuity arithmetic (all four fixtures)

| Fixture | Team | HLTV/receipt lineup | Valve row | Overlap | Rule (`ROSTER_OVERLAP = 3`) |
| --- | --- | --- | --- | --- | --- |
| 1082837 | Zetta | Notjuanjo, zockie, BabyRage, Antuanette, Slayerhz | #357 (473) | **5/5** | pass |
| 1081597 | benched gods | Wign, facer, norescue, yoyoS2, K014NZ | #157 (811) | **5/5** | pass |
| 1082858 | Ground Zero | apocdud, Omichella, vision, tucks *(Sub)*, sliimey | #136 (878) | **4/5** | pass |
| 1082858 | Off Chops | viridian, dexter, Liazz, Gratisfaction, damyo | #119 (971) | **4/5** | pass |

Absent from Valve's standings, so no points and no percentage: **TitanFlow**, **Staqued**,
**LOS NINOS**.

### 4.4 HLTV's VRS mirror disagrees with Valve's file

HLTV's team page for Zetta shows world rank **241** and a VRS mirror position of **368**, while
Valve's pinned file puts Zetta at **#357**. For the DFRAG fixtures the mirror shows Ground Zero
#128 and Off Chops #130 against Valve's #136 and #119. The mirror is newer than Valve's
`2026-10-05` file. The repository correctly uses Valve's own file — it is the official source and
the one whose rows can be cited — and PR #115 already flagged the divergence. Recorded here as an
observation, not an irregularity, and no request is made against it.

---

## 5. Independent replay of the whole 13-match open slate

Every `model_vrs` claim published in `research/session-db1f35c5/REPORT.md` was recomputed here from
Valve's own file using the repository's own calculator (`scripts.vrs.expected` +
`scripts.vrs.calibrated`). Nothing was re-derived by hand.

| Fixture | Matchup | Rows cited | Points in those rows | Reported | Replay of the cited rows | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| 1081600 | Donstu vs Banda chuya | #197 / #165 | DONSTU 732 / Banda Chuya 801 | 42.4 / 57.6 | **42.4 / 57.6** | replays |
| 1082858 | Ground Zero vs Off Chops | #136 / #119 | Ground Zero 878 / THUNDER dOWNUNDER 971 | 40.9 / 59.1 | **39.8 / 60.2** | **does not replay** |
| 1082859 | NEXVOID vs Alter Ego | #113 / #155 | NEXVOID 995 / Alter Ego 819 | 68.2 / 31.8 | **68.2 / 31.8** | replays |
| 1082861 | Rooster vs Abyssal | #205 / #195 | Rooster 718 / Abyssal 734 | 48.2 / 51.8 | **48.2 / 51.8** | replays |
| 1082792 | HOTU vs The Huns | #31 / #122 | HOTU 1437 / The Huns 944 | 85.2 / 14.8 | **85.2 / 14.8** | replays |
| 1082793 | 5star vs 1WIN | #96 / #59 | **Bounty Hunters 1054 / Iberian Soul 1218** | 36.3 / 63.7 | 32.9 / 67.1 | **does not replay** |

For `1082793` the cited rows are not the two teams in the fixture at all. Valve's file puts **5star
at #80 (1110)** and **1win at #38 (1383)**, which replay to **24.3% / 75.7%** — and that is exactly
what the live board prints for `5star vs 1WIN`. (Valve spells the row `1win`; Hotspawn labels the
team `1WIN`. Case folding in `core.norm` handles it, so no alias is needed.)

**Both disputed rows were corrected in the note while this audit was running.** Between `179789e`
and `c55b4b0` the 13-match table in `research/session-db1f35c5/REPORT.md` was updated to
`39.8% / 60.2%` for `1082858` and `24.3% / 75.7%` for `1082793` — the values derived above — and the
market rows were refreshed to the 20:47Z board. The "Primary Source" column now cites the two team
names instead of standing numbers, which removes the `#96 / #59` misattribution. Session `dee046c2`
reached the same two numbers independently (`REQUESTS.md` item R-3: 24.2986/75.7014 and
39.831/60.169, delta 0.0) and filed the same request, so three sessions now agree on the arithmetic.

What still carries the old figures is narrower than it was, and the auditor locates it exactly:

| Location | What it says | Reach |
| --- | --- | --- |
| `data/review-notes.json:1812`, note `db1f35c5-off-chops-rebrand-and-standin-2026-10-21` | "calibrated two-sided Valve VRS model line (Off Chops **59.1%** / Ground Zero **40.9%**)" | **Rendered on the live `review.html`** — the Flagged for Review page a reader is told to consult |
| `research/session-db1f35c5/REPORT.md:18` | "Upgraded (`research_rank` → calibrated two-sided `model_vrs`: Off Chops **59.1%** / Ground Zero **40.9%**)" | Prose bullet above the corrected table, so the note now disagrees with itself |

Market rows were replayed the same way where the quote was readable at audit time: `1082837`
(0.385/0.615, tier `exchange`), and in the CI harvest against a fresh snapshot `1081870`
(40.5/59.5, `exchange_wide`), `1082688` (77.0/23.0), `1082689` (46.5/53.5), `1082882` (44.5/55.5),
`1082837` again at (16.0/84.0). Differences from the numbers in earlier revisions of the note
(41.0/59.0, 41.5/58.5, 52.5/47.5, 38.5/61.5) are line movement inside the same markets, not errors;
every read is dated, and the `1082837` market moved three times in one hour (61.5% at 20:12Z, 80.5%
at 20:47Z, 84.0% at 21:16Z) while staying inside the strict `exchange` gate each time.

`1081597` and `1082860` correctly carry no percentage, for the reasons in §3.2 and §3.4.

**Summary: every published figure on the board replays. The two that did not have been corrected in
the note's table; one of them survives in a rendered review note and in the note's own prose.**

---

## 6. Irregularities

None of these block a merge. Each is recorded with its evidence, its effect on the published board,
and the request logged against the session that owns the file.

### 6.1 An HLTV citation in the merged alias register serves a different match

`data/identities.json`, entry `Zetta`, `corroboration[1]`:

> `HLTV match 2399867 (Zetta vs LOS NINOS, 5/5 lineup Notjuanjo, zockie, BabyRage, Antuanette, Slayerhz)`
> → `https://www.hltv.org/matches/2399867/zetta-vs-los-ninos-cct-2026-south-america-series-7`

Reading that id (R11) serves **Alliance vs FaZe, RLG Tesla Cup 2026, 2026-10-27**. HLTV resolves
`/matches/<id>/<slug>` by the numeric id and ignores the slug, so the URL looks correct and passes a
casual link check while pointing at an unrelated match. The page that does carry the Zetta vs LOS
NINOS lineups is **2399865** (R5), which the same entry's `basis` text already names.

- **Effect on the board:** none — the alias conclusion stands on R3/R5/R7/R8/R9/R10.
- **Effect on review:** a human following the corroboration link lands on the wrong match and may
  conclude the alias is fabricated.
- **How far it reaches** (measured by the auditor, `hltv-citation-reach:2399867`): `data/identities.json`
  (3 mentions, 1 as a link), `data/review-notes.json` (3, 1), `data/latest.json` (3, 1) — inside the
  `evidence` of row `1082837`, the very fixture the alias exists to price — and the published pages
  **`review.html` (3, 1)** and **`evidence.html` (3, 1)**. On `review.html` the link is labelled
  "(Alianza Lima Esports vs Los Ninos, 22:00Z) ↗", so it reads as exactly the corroboration it is
  not.
- **Detection:** `verification-4901f43e/audit_published_claims.py` emits
  `WARN hltv-citation-mismatch:2399867` whenever that id appears in the register, plus the reach
  warning above.
- **Request:** `REQUESTS.md` item 1.

### 6.2 The basis text says "Swiss Round 3"; both primary sources say Round 5

`data/identities.json`, entry `Zetta`, `basis`: "…in CCT 2026 South America Series 7 **Swiss Round
3**." HLTV prints "**Swiss round 5** (teams with a 2-2 record). Winner advances to playoffs, losing
team is eliminated." (R5) and Polymarket's own event description says "the Counter-Strike **Round
5** match" (R2).

- **Effect on the board:** none, because `core.orientation` matches on team pair and exact UTC
  start, not on round label.
- **Effect on review:** the round number is the kind of detail a reviewer checks first, and it is
  wrong in the record that justifies the alias.
- **Request:** `REQUESTS.md` item 2.

### 6.3 A rendered review note still publishes a percentage the model cannot reproduce

`data/review-notes.json:1812`, note id `db1f35c5-off-chops-rebrand-and-standin-2026-10-21`, status
"Verified model upgrade & stand-in note — DFRAG Invitational 2026":

> "…is now priced with a calibrated two-sided Valve VRS model line (**Off Chops 59.1% / Ground Zero
> 40.9%**) after DFRAG confirmed that the 4/5 THUNDER dOWNUNDER core … rebranded as Off Chops"

This note is **rendered on the live `review.html`**, the "Flagged for Review" page the site tells
readers to consult, so the published site carries 59.1% on one page and **60.2%** on the pick board
and evidence pages at the same moment. The same figure also survives in the prose bullet at
`research/session-db1f35c5/REPORT.md:18`, above a table that has since been corrected to 60.2%.

Valve publishes 971 (#119) against 878 (#136), a **93-point** gap. `scripts/vrs.py` turns that into
raw `0.627335` and calibrated **60.2% / 39.8%**; 59.1% would require a gap of **82.85** points. The
board, the CI harvest replay (`row-replays:1082858 → 39.8% / 60.2%`) and this session's offline
replay all agree on 60.2%.

- **Effect on the board:** the pick and its side are correct everywhere; only the note's number is
  wrong, but it is wrong on a page readers are directed to.
- **Why CI does not catch it:** `scripts/validate.py` replays snapshot-internal consistency, and
  `tests/test_session_db1f35c5.py` pins `points == [878, 971]` but never the split derived from
  them. Review-note prose is not replayed by anything.
- **A second instance was found and has already been corrected.** The same note's table claimed
  `36.3% / 63.7%` for `5star vs 1WIN` from standings `#96 / #59`, which are **Bounty Hunters
  (1054)** and **Iberian Soul (1218)** — not the teams in that fixture. The reproducible value from
  the real rows, #80 (1110) and #38 (1383), is **24.3% / 75.7%**, which the board prints. The table
  now reads 24.3/75.7; this session's auditor reports `stale-figure-absent:1082793` because no
  tracked file carries the old figure any more.
- **Detection added here:** `audit_stale_claims` scans the tracked data and research files for both
  figures and reports file and line. It warns while a stale figure is published and clears itself
  the moment the owner corrects it, so the check cannot outlive the problem it describes.
- **Request:** `REQUESTS.md` item 3.

### 6.4 Every HLTV citation in the repository is unverifiable from CI

Six of six HLTV URLs probed from the runner returned **403**, as did EGamersWorld and Liquipedia
(§1, `research/harvest-4901f43e/probe.json`). bo3.gg answered `200` without the expected marker
text. Meanwhile `scripts/refresh.py` depends on HLTV for live lineups and rankings.

- **Effect on the board:** real. In the harvest run against the pre-#121 pipeline, HLTV lineups
  were empty, so `benched gods` stayed ambiguous (`label appears 2 times in the standings and no
  lineup was available`) and fixture `1081597` shipped with **no pick at all**; `Off Chops` was
  `not listed in the Valve global standings` because nothing bridged the alias; and `1082837`
  rejected its own Polymarket candidate with `Unverified opponent/alias or roster-name mismatch`.
  The alias register and the lineup receipts are what recover those rows — which makes them load
  bearing, and makes their citations worth getting right (§6.1).
- **Effect on review:** a reviewer in CI cannot re-read any HLTV page this project cites. Only an
  authoring-path or human read can.
- **Not a request against another session:** PR #115 already flagged the HLTV 403s. This session
  adds the dated, per-URL runner-side evidence, and keeps its own receipts on the path that works.

### 6.5 Withdrawn: a fourth irregularity this session had drafted, and why it was wrong

An earlier draft of this report claimed the three new `rejected_listings` entries in
`data/book-receipts.json` were inconsistent with the file's convention because they omit
`superseded_by`. Checked against the merged file, that is false: **24 of 25** entries omit it, and
only `rejected_listings[0]` carries it. The three new entries follow the convention. The claim is
withdrawn and recorded here rather than deleted, because a verification report that quietly drops
its own mistakes is not worth reading.

### 6.6 BLOCKER: `main` is red on the test suite, which stops the site from publishing

Full write-up, reproduction and per-test diagnosis: **`verification-4901f43e/MAIN-SUITE-BLOCKER.md`**.

`unittest discover -s tests` on `main` at `c55b4b0` reports **582 tests, 4 failures, 2 errors**. The
same six tests pass on the immediately preceding commit `ac5c816`, verified in a pristine
`git worktree` containing none of this session's files. The breaking commit is the automated
"Publish the verified build to the legacy main:/ root fallback" publication, which replaced the
frozen 2026-10-18 98-row `data/latest.json` and all nine root `*.html` with the fresh 21 October
75-row build. Six tests in `test_coverage_76712ccc`, `test_day5_e0fd5a32`, `test_day5_f4e34907` and
`test_session_d6df5beb` assert against those committed artifacts as if they were frozen history.

Why it matters more than a red test run: that step is the **first hard gate** in `pages.yml`, with no
`continue-on-error`. Every later step and the entire `deploy` job depend on it, so the next scheduled
slot builds nothing, publishes nothing, and the live board goes stale at its own eight-hour limit —
after which `assets/app.js` withholds all picks rather than showing expired ones. The root-fallback
publication was the correct fix for the frozen board and it has, as a side effect, stopped the board
from updating at all.

- **Owners:** `1395f539` for `scripts/publish_root_fallback.py`; `76712ccc`, `e0fd5a32`, `f4e34907`,
  `d6df5beb` for the six tests. This session edited none of them.
- **Requests:** `REQUESTS.md` item 5, with a suggested minimal fix per test.
- **Deliberately not requested:** making the test step `continue-on-error`. That would restore
  publishing by removing the only check that keeps broken data off the site.
- **Effect on this session's merge:** none on correctness — this branch adds only new files and is
  green on the same tree (29 tests, 49/0/4 auditor) — but the merge does not unblock publication
  either, so it is recorded as an open blocker rather than quietly resolved.

---

## 7. What stays blank, and why

The board publishes 13 open matches: **13 with a pick, 11 with a win probability, 0 unresolved**.
The two without a percentage are `1081597` (benched gods vs TitanFlow) and `1082860` (FlyQuest vs
Staqued). Their limitations, each traceable to a source:

| Fixture | Why no percentage | Source |
| --- | --- | --- |
| 1081597 | HLTV's own page for the fixture is stamped "Match postponed" and names no teams; TitanFlow has no row in Valve's global standings, so there is no official points value to model from; no market lists the pair | R12, R4 |
| 1082860 | Staqued has no row in Valve's 380-team global standings; no market lists the pair | R4 |

Structural limits that apply to the whole board, verified rather than assumed:

- **HLTV exposes no numeric two-way line** for any of these fixtures. Its betting tables for
  `2399865` and `2399888` contain a Stake social-casino promotion row and nothing else (R5, R13).
  "HLTV first" therefore yields lineups, ranks, round labels and schedule truth — not prices.
- **GG.BET refuses the runner**: `HTTP 403 persisted after 3 rate-limit waits (10s, 30s, 60s)`
  (recorded in every row's provider attempts).
- **Thunderpick** answers but renders client-side: "Access succeeded but no validated automated
  two-sided series quote was extracted."
- **Pinnacle** returns a feed with no exact team-pair and UTC-start match for these fixtures.
- **EGamersWorld's 1.8/1.8 placeholder listings** are correctly rejected rather than averaged into
  a fake 50/50.

**Crowd votes are never a probability input.** Three were seen during this session and all three
were recorded and rejected: HLTV 75/25 for Zetta (R5), Strafe 24/76 the other way for the same
fixture (R10), and HLTV 50/50 with zero votes cast (R13). The first two contradict each other on
the same match, which is the clearest possible demonstration of why they cannot price anything. The
auditor asserts `crowd-votes-excluded` on every run.

Hotspawn itself is inventory only: it establishes which matches exist and when they start, and
nothing else. No percentage on the board originates from it.

---

## 8. Reproduction

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 1. Replay every published claim against Valve's file, the receipts and a snapshot.
.venv/bin/python verification-4901f43e/audit_published_claims.py \
    --snapshot data/latest.json \
    --json research/session-4901f43e/audit-baseline-2026-10-21.json

# 2. The same audit against a snapshot CI just refreshed (run inside the harvest workflow).
.venv/bin/python verification-4901f43e/audit_published_claims.py --snapshot runtime/latest.json

# 3. Receipt integrity, alias arithmetic, model arithmetic, refusals (29 tests).
.venv/bin/python -m unittest tests.test_session_4901f43e -v

# 4. Runner-side reachability of every URL cited above (needs CI network).
.venv/bin/python -m scripts.probe_4901f43e
```

Results at report time:

All numbers below were re-run on this branch after the rebase onto `c55b4b0`, so they describe the
tree as it will merge, not an earlier state.

| Check | Result |
| --- | --- |
| Auditor vs committed `data/latest.json` (75 rows, the 21 October build) | **49 passed, 0 failed, 4 warnings** — JSON at `research/session-4901f43e/audit-baseline-2026-10-21.json` |
| Auditor vs fresh CI snapshot `runtime/latest.json` (75 rows, 13 open, all replay) | **46 passed, 0 failed, 4 warnings** (harvest run 39676969126, committed at `research/harvest-4901f43e/claims-audit.txt`) |
| `tests/test_session_4901f43e.py` | **29 tests, OK** |
| `unittest discover -s tests` | **582 tests, 4 failures + 2 errors — all six pre-existing on `main`, none in this session's files** (§6.6) |
| `unittest discover -s audits` | 9 tests, OK |
| `verification-95b588c2/test_integrity.py` | 5 tests, OK |
| `unittest discover -s verification-c6` | 12 tests, OK |
| `verification-c6/audit_snapshot.py data/latest.json` | 0 failures |
| `scripts.validate --data data/latest.json --site .` | 75 rows verified against the primary snapshot, 11 probability calculations reproduced, 15 pages, 655 internal links, 20 checksums, 176 displayed rows |
| `scripts.build --data data/latest.json` | 9 primary pages + 6 legacy redirects; 75 sourced rows, 11 with percentages, 2 without, **0 unresolved** |
| `npm run test:browser` | 32 page/viewport/accessibility scans at 320/390/768/1440px (axe, no-overflow, subpath URLs, navigation, filters, six legacy redirects, evidence anchors, expiry), 7 board expiry scenarios, 4 quote-clock scenarios |

The four warnings are the findings in §6: `stale-figure-published:1082858` (the 59.1% / 40.9% that
survives in `data/review-notes.json:1812` and `research/session-db1f35c5/REPORT.md:18`, located by
file and line), `hltv-citation-mismatch:2399867`, `hltv-citation-reach:2399867` (where that wrong id
is rendered), and `hltv-citations-not-read` (15 ids this session did not read, listed by id so
nobody mistakes silence for confirmation). A fifth check, `stale-figure-absent:1082793`, now
**passes**: the 36.3% / 63.7% figure was corrected on `main` while this audit ran, and the check
cleared itself without being edited. That is the intended behaviour — these warnings describe the
repository as it is, not as it was when they were written.

They are warnings, not failures, on purpose: failing them would break `main` over prose in another
session's report, and the point of this session is to make discrepancies visible, not to weaponise
them. The one thing that *is* a blocker, the red suite in §6.6, was not caused by this session and
cannot be fixed from inside its scope; it is documented in
`verification-4901f43e/MAIN-SUITE-BLOCKER.md` instead.
