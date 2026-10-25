# Session 046b2e46 — every open pick, re-derived; the outage that hid them, repaired

Scope: the *data and product* half of the brief — a pick and a sourced win probability for every open
Hotspawn CS2 match, a separate unresolved/limitations register named in the executive summary, and a
phone-first route to the updated pick list — plus the publication defect that was preventing any of it from
being served.

Everything below is dated and measured. Where a value could not be confirmed from an official source it is
marked **unverified** and not filled in.

## 1. Published state at claim time (13:26 UTC)

| Fact | Value | How it was read |
| --- | --- | --- |
| `main` | `6ade440` | `git ls-remote origin main` |
| Committed snapshot | `2026-10-25T01:47:42Z`, fixture evidence `01:44:08Z` | `data/latest.json` |
| Rows / open / picked / priced / unresolved | 79 / 18 / 18 / 18 / 0 | same |
| Age of the snapshot at 13:24Z | 11 h 37 m against its own 8 h window | `generated_at` vs clock |
| Consequence | the served board withheld **every** pick | `scripts.build` on the committed data: "0 with percentages, 14 unresolved" |

The data was fine. The publisher was not: `pages.yml` failed at step 13 on both scheduled attempts
([40170923727](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40170923727) at 06:56Z,
[40193317196](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40193317196) at 12:29Z), so
`upload-pages-artifact`, the legacy `main:/` staging step and `deploy` were all skipped.

## 2. The defect, reproduced

This sandbox has no egress to the esports hosts (`curl` returns `000` for Hotspawn, HLTV, Polymarket and
BO3.gg) and cannot download Actions logs (the log blob host is not on its allowlist), so the only honest
route to the failure was a normal runner. The capture used here is session 58354934's non-publishing run
[40197480741](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40197480741)
(`research/harvest-58354934/`, snapshot `2026-10-25T13:28:50Z`, committed as
`research/session-046b2e46/captured-snapshot.json`). Replayed against `main`:

```
File "scripts/validate.py", line 122, in validate_model_row
    assert lineup_source_ok(m, team, check.get('lineup') or []), 'Model roster has no HLTV source on this row'
AssertionError: Model roster has no HLTV source on this row
```

One row: **1086697** *Projeto do KinGui* vs *Yawara*, CCT South America 2026 Series #7,
2026-10-25T19:00:00Z.

* Valve's roster for that side, per the model evidence: `drg, ALLE, ckzao, xureba, lash`.
* The HLTV lineup retained on the same row: `drg, ALLE, ckzao, xureba, lash` — identical.
* Hotspawn's label: *Projeto do KinGui*. HLTV's label on
  [match 2399904](https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7):
  *Tropa do KinGui*.
* Those two labels are **one club** according to a registered alias in `data/identities.json`
  (canonical *Tropa do KinGui*; names *Tropa do KinGui*, *Projeto do KinGui*, *ex-Keyd Stars*; anchored to
  the HLTV match page, Polymarket market 6033256, Valve's official #144 ex-Keyd Stars roster sheet and an
  EGamersWorld listing).
* `scripts.core.norm` resolves that alias. `scripts.validate.lineup_source_ok` compared **literal** names
  with `plain_name`, so the alias could never match and the build was rejected.

Correct data, wrong comparison. Nothing about the pick, the percentage or the source was wrong.

## 3. The repair that shipped, and the one withdrawn

This session built an independent repair (`same_club()` resolving both labels through `core.norm`, applied to
all three roster-provenance paths) and verified it locally. **Before it could merge, main received an
equivalent repair from session b85ad9b4** (`e9429e6`, 13:37Z): `same_club(m, team, label)` keyed on the same
`data/identities.json` register, plus a guard that the register must keep the fixture's two teams apart.
Per the shared-board protocol the two are **not stacked**: main's version is what ships, and this session's
edit to `scripts/validate.py` was dropped at integration. The tests in `tests/test_session_046b2e46.py` were
re-pointed at the shipped function so they pin what the repository actually runs.

Both repairs share the same invariant: an alias is accepted only when `data/identities.json` records it with
an https source, so the rule "a roster claim must name its HLTV page" is unchanged.

## 4. Verification performed

| Gate | Command | Result |
| --- | --- | --- |
| New regression tests (against main's shipped `same_club`) | `python -m unittest tests.test_session_046b2e46` | **24 tests OK** |
| Whole suite (the CI gate) | `python -m unittest discover -s tests` | **1,652 tests OK** (12 skipped) |
| Build on the captured snapshot | `python -m scripts.build --data …` | 78 rows, 17 with percentages, **0 without, 0 unresolved** |
| Validator | `python -m scripts.validate --data … --site public` | 78 rows / 17 calculations / 15 pages / 730 links / 20 checksums |
| Independent row audit | `verification-c6/audit_snapshot.py public/data/latest.json` | **0 failures** |
| Phone/tablet/desktop + a11y | `node tests/browser.cjs` | 32 page/viewport scans pass at 320/390/768/1440px |
| Independent ledger (new) | `python -m scripts.session_046b2e46` | **17/17 open rows reproduced, 0 failures** |

## 5. Every open pick, re-derived independently

`scripts/session_046b2e46.py` shares no code with `scripts/core.py`, `scripts/vrs.py` or
`verification-c6/audit_snapshot.py`. It re-derives each published pair from the raw evidence on the row:

* **Polymarket** — the midpoint of the market's own `bestBid`/`bestAsk`, complement for the other side;
* **book listing** — inverse decimal odds normalised to remove the overround;
* **Valve VRS** — Valve's published Glicko expectation (`RD = 75`) with Valve's published fit slope
  `p = 0.5 + 0.7986 (E - 0.5)`, from
  [`model/fit.js`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/fit.js)
  and [`modelfit.png`](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/modelfit.png).

It also re-checks orientation. The exchange and the fixture inventory publish the two clubs in different
orders on some rows — Polymarket had **paiN** as the home side on fixture 1082697 while Hotspawn lists
**BESTIA** first — so a reorder is only allowed on evidence carried by the quote: an exact folded name, a
registered identity alias, or the exchange's own `abbreviation` for that outcome (fixture 1082996 is *UNiTY*
on Hotspawn and *UNiTY esports* on the exchange, whose metadata gives `unity`). Anything else is a failure,
and the assignment must be a bijection. The ledger's own refusals are unit-tested with tampered rows:
a shifted probability, a wrong pick, wrong fair odds, a reversed quote without evidence, a missing market
link and an unlabelled model row each fail.

Full table with a source link per row: [`ROW-LEDGER.md`](ROW-LEDGER.md).

### Method mix on the captured board (17 open rows)

| Method | Rows | Where the number comes from |
| --- | --- | --- |
| `exchange` (strict Polymarket gate) | 11 | the market's own live two-sided quote |
| `exchange_wide` (labelled low-confidence) | 1 | same market, spread 26 points, published with its warning |
| `bookmaker_fallback` (BO3.gg listing) | 1 | Thunderpick `1.60 / 2.20`, de-vigged to 57.9% / 42.1% |
| `model_vrs` (our own originated line) | 4 | Valve's official standings points + Valve's formula |

## 6. Unresolved register and the executive summary

* The board carries a named section — *"Unresolved picks, and why a pick can be missing"* (`#unresolved-limits`)
  and *"Picks without a win probability — and exactly why"* (`#unresolved-picks`) — plus a dedicated
  `unresolved.html` page. On this capture it states **17 of 17 open matches have a pick; 0 are unresolved**,
  and it lists the access limitations of every source the ladder tried.
* The executive summary on the landing page links to `picks.html` (updated picks), `#unresolved-limits`
  (limitations), `unresolved.html`, `matches.html` and `analysis.html`, and repeats the live counts
  (`17 / 17 picks · 0 unresolved`). Those links are above the pick list on a phone; the fixed bottom bar
  offers *Home · Picks · Unresolved · Matches · Analysis* on every page.

## 7. Flagged for review (non-blocking, published on *Flagged for Review*)

Main already carries session b85ad9b4's record of the outage and its alias bridge
(`session-b85ad9b4-alias-bridge-publication-failure-2026-10-25`), so this session does not add a duplicate.
Its two distinct findings are:

1. `session-046b2e46-thin-model-edge-2026-10-25` — fixture 1086697 publishes a **1.2-point** model edge
   (51.0% / 49.0%). Reproducible, labelled non-market, but a product decision: is a 1.2-point originated
   edge a pick, or an unresolved row? Left visible rather than rounded.
2. `session-046b2e46-lobby-level-source-link-2026-10-25` — fixtures 1086696 and 1086697 get no per-match
   Hotspawn URL from the feed, so their fixture link is the lobby page while the price evidence still links
   the exact market or Valve file.

Also recorded, unchanged from earlier sessions: the Hotspawn endpoint still returns 61 of 78 feed rows as
`scheduled` after their start (they are retained, unpriced, on *All matches*), and the bookmaker listing used
for fixture 1082859 carries no price-update timestamp.

## 8. Provenance of every source named here

* Hotspawn fixtures: <https://play.hotspawn.com/cs2-pickems> and <https://play.hotspawn.com/lobby> —
  inventory and lock times only, **never** a probability.
* Polymarket market records: `https://gamma-api.polymarket.com/markets/<id>` (one per row, linked in the
  ledger).
* BO3.gg listing: <https://bo3.gg/matches/nexvoid-vs-alter-ego-26-10-2026>.
* Valve standings and model: pinned commit `eec4853d7bcf0f1f7efe7f0d901234bef7e98b75` of
  <https://github.com/ValveSoftware/counter-strike_regional_standings>.
* HLTV identity: <https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7>.
