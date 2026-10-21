# Session 1395f539 — the last unpicked fixture

**Question.** On the live board at 2026-10-21T19:57Z (build `47f230b`, 13 open fixtures) every Hotspawn CS2 match
carried a pick except fixture **1081597 — benched gods vs TitanFlow**, CCT Europe 2026 Challengers #8,
2026-10-22T11:00:00Z (lock 10:54Z). The user requires a pick for every match. This session establishes, from primary
sources, whether that fixture can be resolved honestly, and if so on what evidence.

All observations below were made on **2026-10-21 between 20:00Z and 20:30Z**.

## 1. Why the existing ladder stopped

| Tier (in order) | Result for 1081597 | Evidence |
| --- | --- | --- |
| Polymarket exchange | No event for the pair | The refresh records a per-row Polymarket rejection; no market carried both labels. |
| HLTV fixture discovery | **No fixture page naming the two teams** | HLTV's CCT Europe Series 8 schedule lists this slot as `2399696 / cct-2026-challengers-europe-series-8-lower-bracket-round-3-2-...` with **TBA on both sides**: <https://www.hltv.org/matches/2399696/cct-2026-challengers-europe-series-8-lower-bracket-round-3-2-cct-2026-challengers-europe-series-8> |
| Pinnacle | Queried on every refresh; nothing accepted | Recorded per row by `scripts/refresh.py`; no invented line. |
| Book-listing receipts | EGamersWorld publishes **1.80 / 1.80** for the two sides | <https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn> — an identical pair is EGW's documented placeholder (the same pattern recorded for Zetta–LOS NINOS in session `84295759`), so it is refused rather than converted into 50/50. |
| VRS model line | **Stopped**: Valve's standings list `benched gods` **twice** and the collector had no lineup to tell the rows apart | Valve global standings 2026-10-05: `#157 / 811` (facer, K014NZ, norescue, Wign, yoyoS2) and `#329 / 516` (BloodyK, f1chper, K014NZ, MisterHy, Wign). |
| One-sided Valve tier | **Stopped** for the same reason: it needs the listed team's roster verified before it may call the other label absent. | `scripts/vrs.py research_single` → `identify()` → "label appears 2 times … no lineup was available". |

So the only missing input was **a current roster for `benched gods`**, and the only place it exists is HLTV's own team
page, which does not depend on the TBA bracket slot.

## 2. What was added

`scripts/hltv.py` → **`team_pages()` / `team_profile()` / `search_teams()`**

1. Public HLTV search for each Hotspawn label (`https://www.hltv.org/search?query=…`).
2. Keep only `/team/<id>/<slug>` links whose visible label **normalizes exactly** to the fixture label. **Zero hits or
   more than one hit refuses the tier** — no fuzzy matching, no academy/main conflation.
3. Read that team page and require its own `<h1>` heading to normalize to the label again.
4. Record the page's published starting five (its "The main lineup of X is …" answer), the world-rank link if it is a
   pure `#N`, an explicit "doesn't have a world rank" statement (only then is a team called *unranked*; otherwise the
   status is `unknown`), and the Valve-ranking link when present.

`scripts/refresh.py` → `fixture_lineups()` merges those rosters into the identity input for the **existing** Valve
tiers (originated two-team line and the one-sided research tier). Nothing about the probability formula, the gates or
the tier order changed.

## 3. Result for 1081597

| Step | Observation | Source |
| --- | --- | --- |
| Search hit for `benched gods` | exactly one team page | <https://www.hltv.org/search?query=benched%20gods> |
| Search hit for `TitanFlow` | exactly one team page | <https://www.hltv.org/search?query=TitanFlow> |
| benched gods roster | Wign, K014NZ, facer, norescue, yoyoS2 — **5/5 match** the 811-point Valve row, 0/5 on the 516-point row | <https://www.hltv.org/team/13599/benched-gods> |
| HLTV rank context on that page | Valve #161, world #204 | same page |
| TitanFlow page | no active roster, "doesn't have a world rank", Valve ranking `-` | <https://www.hltv.org/team/14021/titanflow> |
| Valve global standings 2026-10-05 | `benched gods` #157 / 811 points; **TitanFlow absent from the 380-team file** | <https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md> |
| Valve **Europe** standings 2026-10-05 (checked so the "absent" claim is not an artefact of one file) | `benched gods` #116 / 811 and #219 / 516; **TitanFlow absent** | <https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_europe_2026_10_05.md> |

**Corroboration, and what the parallel session's receipt adds.** Session db1f35c5 (merged in PR #119 while this branch
was open) captured the two feeder matches in the same event — [benched gods 2-1 ex-6666 (HLTV 2399691)](https://www.hltv.org/matches/2399691/benched-gods-vs-ex-6666-cct-2026-challengers-europe-series-8)
and [TitanFlow 2-0 Noir Verse (HLTV 2399692)](https://www.hltv.org/matches/2399692/noir-verse-vs-titanflow-cct-2026-challengers-europe-series-8)
— in `data/lineup-receipts.json`, which gives **TitanFlow's five** (ves111, ZzZoOm, Saiman Strit, keeisen, Henma) as
well as benched gods'. The two independent methods **agree on benched gods' roster** (Wign, K014NZ, facer, norescue,
yoyoS2), and the integration keeps both sources with a stated precedence: live HLTV fixture lineup → the clubs' own
team pages → the retained receipt. That receipt also records an irregularity this session confirmed independently:
HLTV marks bracket slot **2399696 "Match postponed"** while Hotspawn keeps 2026-10-22 11:00Z open. The board therefore
publishes the pick against Hotspawn's own lock time and keeps the schedule conflict visible on Flagged for Review; if
Hotspawn updates or locks the row, the normal expiry rules withdraw it.

**Published outcome:** method `research_vrs_single`, pick **benched gods**, **no percentage, no fair odds, no quote**.
The row states that benched gods is #157 in Valve's official global standings of 2026-10-05 (811 points) while TitanFlow
does not appear in that 380-team file at all, that this is one-sided standings evidence and not a market probability,
and that the roster was confirmed from the clubs' HLTV team pages because the HLTV fixture page is a TBA slot. Both
team-page URLs are printed in the row's Sources column, and the standings link, the standings date and the observation
times are printed beside them.

## 4. Limits disclosed on the row and on Flagged for Review

1. **Identity is by exact label on two independent team pages**, not by an HLTV fixture page that names both teams. The
   shared competition (CCT Europe 2026 Challengers #8) and the exact Hotspawn labels are the only cross-checks.
2. **Valve's published files are dated 2026-10-05.** Valve may add TitanFlow to a later publication, which would turn
   this one-sided pick into a two-team model line (and therefore a percentage). Until then the row says "absent from
   that file", which is exactly what was verified, and nothing stronger.
3. **`benched gods` is listed twice in Valve's standings.** The row resolves only because the HLTV roster matches one
   of the two rosters 5/5 under Valve's own three-player continuity rule.
4. **No esportsbook line was accepted.** EGW's 1.80/1.80 is a placeholder and is refused; the collector keeps the
   rejection in the evidence ledger instead of publishing 50/50.
5. **The fixture may be postponed.** HLTV marks slot 2399696 "Match postponed" (both feeder matches are complete),
   while Hotspawn still lists 11:00Z on 22 October. The pick is bounded by Hotspawn's lock time and disappears at lock,
   and the conflict is on Flagged for Review; no attempt is made to guess a rescheduled time.
6. **HLTV displays local time.** Its fixture page for this bracket slot renders "07:00", which is a timezone rendering,
   not a different start; Hotspawn's 11:00Z remains the only start used for identity.

## 5. Verification performed in this session

- `python -m unittest discover -s tests` — **512 tests, OK** (14 new: search/heading parsing, refusal on ambiguity and
  on a near-match heading, roster hand-off into `refresh.fixture_lineups`, the one-sided pick itself, and the row's
  rendered links).
- `python -m scripts.build` + `python -m scripts.validate` — **98 sourced rows, 29 calculations replayed, 15 pages,
  615 links/assets, 20 checksums, 184 displayed rows** on the committed bootstrap snapshot, unchanged.
- `npm run test:browser` — **32 page/viewport accessibility and no-overflow scans at 320/390/768/1440 px**, filters,
  six legacy redirects, evidence anchors, seven expiry scenarios and four quote-clock boundaries.
- A **synthetic end-to-end row** was run through the shipped validator with the real Valve standings file and the real
  team-page parsing path: `validate_data` accepts the `research_vrs_single` row, and the validator now *requires* the
  stored lineup to be reproducible from an HLTV URL present on the row (a new assertion; removing the source fails it).
- Branch workflow run (verify-build) after the change: `success`.

## 6. Irregularities flagged (non-blocking)

- `data/review-notes.json` → `1395f539-team-page-tier`: the identity basis, the duplicate Valve label, the TBA HLTV
  slot and the refused EGW placeholder, with links.
- A cosmetic defect found while auditing the phone layout: the executive summary's glance footer printed the literal
  text `Unresolved &amp; limitations` (the label was escaped twice). Fixed, and a regression test now asserts that no
  double-escaped ampersand reaches the rendered page.
