# Session 174afa4f — final report (2026-10-24)

## Outcome

Runner capture [40067406754](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40067406754):
fixtures observed `2026-10-24T05:50:47.971271Z`, snapshot generated
`2026-10-24T05:54:23.068654Z`, SHA-256
`a4f42c2d4e16dc1655c7f254c607f6a41a634782b07571511fba8509beff3f35`.
**88 fixtures, 25 open, 25/25 with a pick and both win probabilities**
(exchange 12, model_vrs 7, exchange_wide 2, bookmaker_fallback 2,
model_vrs_mirror 2); 0 unresolved, 0 without %, 0 integrity failures across
three independent replays (verification-c6, session-0cc1138a verifier,
`scripts.audit_174afa4f`). Full ledger: `research/harvest-174afa4f/row-ledger.md`.

Hand re-derivations (no pipeline code):
- `1079193` (exchange): stored Gamma prices `[0.785, 0.215]` → `78.5%/21.5%` exact.
- `1081156` (model_vrs_mirror): points 1030/819 → Glicko RD75 raw
  `0.765235660981`, calibrated `0.711817198860` = published to 1e-12.
- `1082860` (bookmaker_fallback): decimal `1.001/12.0` → de-vig
  `92.3006%/7.6994%` = published.

## P0: publish deadlock un-deadlocked

Scheduled publishing had failed since `2026-10-23T12:49Z`: the pre-refresh
lobby-parity test excused vanished fixtures only via
`inventory_changes.removed_ids` (delta vs the *previous* snapshot), so
`1079655`/`1081148`, removed by Hotspawn two rotations earlier, failed
forever before refresh could run. `feed_removed_ids()` now also proves
feed-removal from the snapshot's own verified evidence
(`coverage == 'verified'` + raw `fixture_evidence` IDs exactly equal
published IDs + ID absent from raw evidence). Collector drops and
partial/retained coverage are never excused; unit tests pin all cases.
Live proof: all 11 fixtures that vanished between snapshots are proved
feed-removed, 0 unproved (`research/harvest-174afa4f/session-174afa4f.md`).
Same defect class: `test_session_f89bb1f8` hard-coded `'23 Oct'`; it now
asserts the strip shows the first pick's own start date.

## Fallback ladder: what was added, HLTV first

**HLTV team-page rank tier** (`scripts/core.py`, methods `research_rank` /
`research_rank_single`, pick **without** a %): when HLTV lists no fixture
page, each club's own exact-heading HLTV team page (already collected into
`hltv_team_pages`, previously never read by the ladder) may decide the pick.
Both pages must re-verify: one stored page per label on an
`https://www.hltv.org/team/` URL with observation time; heading normalizes
to the fixture label; `ranked` only with a positive rank; `unranked` only
when HLTV stated the absence; anything else is `rank_unknown` and blocks a
one-sided claim. Fixture-page ranks keep precedence. Evidence is stored
under `hltv_team_pages.resolved_ranks` and replayed independently by
`scripts/validate.py` and verification-c6; the tier expires after 8 h like
every source; no rank-to-% formula is invented. It fired 0 times in this
capture because higher tiers priced every open row — it exists for the
cycles where they do not.

**Probe of the 13 rows featured tiers missed** (`scripts/probe_174afa4f.py`,
`research/harvest-174afa4f/PROBE.md`; diagnostic only, never a price input):
- Pinnacle: 18 CS2 matchups, **zero** exact or near-miss rows for all 13 —
  genuinely not offered, not an alias/start problem.
- BO3: payload total `279` over 3 pages — the collector's window covers it;
  pagination is not a gap.
- Kalshi public API: read (949 KB), none of the 13 fixtures' labels present.
- OddsPortal: read; only `UNiTY` label present (discovery signal only).
- HLTV ranking list and EGamersWorld listing: HTTP 403 persisted after the
  published waits in the probe run — recorded as dated limitations, never
  bypassed, never stated as "no odds exist".
- Researched and rejected with measurement: Valve's regional standings
  files (americas/asia/europe `2026_10_05`) are strict subsets of the
  global file (349 unique teams) — zero added model coverage.

Current ladder position for the record: strict Polymarket → HLTV context →
Pinnacle → wide Polymarket → Thunderpick/GG.BET attempts → BO3/EGW book
receipts → Valve VRS file model → HLTV-mirror VRS model → HLTV research
rank (fixture page, now team pages) → single-rank/VRS-single → research
form. Hotspawn is used only for fixture identity/schedule/lock, never as a
probability input; no 50/50 default exists anywhere.

## Phone: visible executive summary + a latent CSS bug

New `#exec-summary` (`scripts/build.py`, `site/assets/style.css`): always
visible directly under the freshness strip — the live completeness sentence
and counters (same `data-count` spans the runtime updates) plus three
≥46 px in-site taps: **Updated picks**, **All picks on this page**,
**Unresolved & limitations**. The full briefing stays folded below
("Site guide, navigation & full briefing"); every previous anchor and
counter survives.

Found while measuring: a missing `}` in `style.css` had nested ~140 lines
of phone CSS — including session f89bb1f8's first-screen compaction —
inside `@media (max-height:700px)`, so tall phones (e.g. 390×844) never
received it. Closed the brace; re-measured with Chromium
(`research/session-174afa4f/measure-phone-geometry.cjs`): at 390×844 the
pick list now starts at **519 px** and the first pick card at **529 px**
(was 1024/1210 px with the summary bar before compaction); at 320×568,
580/590 px. All eight browser suites pass locally and are re-run in CI. A
brace-balance regression test pins the stylesheet. Also fixed: the harvest
workflow's `| tee` steps masked a failing browser assertion in run
40067406754 (job still showed success); the workflow now runs with
`shell: bash` (pipefail). Production `pages.yml` never piped its gate.

## Verification record

- `python -m unittest discover -s tests` — 1216 OK (1 skipped) against the
  fresh committed snapshot; `audits` 9 OK; `verification-95b588c2` 5 OK;
  `verification-c6` 12 OK; C6 snapshot audit 0 failures
  (`research/session-174afa4f/committed-row-audit.md`).
- `scripts.validate --data data/latest.json --site .` — 15 pages, 821
  links/assets, 20 checksums, 216 displayed rows verified.
- `npm run test:browser` — all 8 suites pass on the staged build.
- The session-0cc1138a independent verifier learned the pre-existing
  `model_vrs_mirror` evidence shape (its first open mirror rows): same
  Valve math, plus dated-page identity and stored-intermediate re-derivation.
- Harvest workflow gates (pre-refresh suite, refresh, quarantine 0 rows,
  C6, audit, probe, build, validate) all ran on the runner; the browser
  step's masked failure is documented above and was re-run locally to green.

## Irregularities flagged for review (non-blocking)

1. **Masked harvest gates (historical):** earlier sessions' harvest
   workflows used the same `| tee` pattern without pipefail; their browser
   steps may have hidden failures. Recommend the same one-line fix when
   those workflows are next touched. Production was never affected.
2. **CSS brace nesting (historical):** tall phones ran without the
   f89bb1f8 first-screen compaction from 2026-10-23 until this session.
   Any phone geometry measured only at 320×568 in that window should be
   re-measured at 390×844 before being cited.
3. **Dated source limitations:** HLTV ranking list, HLTV fixture odds
   tables and the EGamersWorld listing refused the probe's reads
   (HTTP 403 after waits, 2026-10-24). Nothing is claimed about their
   contents. Kalshi's first 200 open markets carried none of the target
   fixtures; a CS2-specific Kalshi series scan remains unprobed.
4. **`1082860` price shape:** Thunderpick's stored line is `1.001/12.0`
   (8.2% overround) — inside the published gates and de-vigged exactly,
   but extreme; the row is labelled `bookmaker_fallback` on the site.
5. **PR #233** (`arena/9b97d585-maltaproj4`, snapshot-clock test) remains
   open/conflicting and targets a different test; it is not needed for the
   deadlock fix and was not touched.

## Files

Claimed scope only: `tests/test_session_0cc1138a.py` (parity oracle),
`tests/test_session_f89bb1f8.py` (date literal), `scripts/core.py`,
`scripts/validate.py`, `verification-c6/audit_snapshot.py`,
`scripts/summary.py`, `scripts/build.py`, `site/assets/style.css` +
`assets/style.css`, `research/session-0cc1138a/verify_0cc1138a.py`
(mirror replay), new `scripts/audit_174afa4f.py`,
`scripts/probe_174afa4f.py`, `.github/workflows/harvest-174afa4f.yml`,
`tests/test_session_174afa4f.py`, `research/harvest-174afa4f/`,
`research/session-174afa4f/`, `COORDINATION.md`, and — as integration
session — `data/latest.json`, `data/matches.csv`, the generated root
pages and `build-info.json` (staged via `scripts.stage_legacy` from the
verified build), plus the `pages.yml` branch-list line.
