# Session e141a921 — full-board acceptance and release candidate

**Observation date:** 23 October 2026  
**Branch:** `arena/e141a921-maltaproj4`  
**Fresh collection:** GitHub Actions [run 39934335176](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39934335176), non-publishing `[capture]` harvest  
**Final PR / merge / deployment receipt:** recorded in [`COORDINATION.md`](../../COORDINATION.md) after publication; this report remains the dated candidate audit rather than being relabelled as a later capture.

## Result

The fresh runner board covers every CS2 fixture returned by Hotspawn and gives every then-open match a visible pick and two independently originated probabilities:

| Check | Fresh result |
| --- | ---: |
| Hotspawn API / CS2 page / lobby / retained fixture IDs | **92 / 92 / 92 / 92** |
| Retained rows | **92** |
| Open by sourced start, lock and status | **30** |
| Open rows with a pick | **30** |
| Open rows with a replayed probability pair | **30** |
| Open research-only rows | **0** |
| Open unresolved rows | **0** |
| Inventory changes, fixture conflicts, row errors, global errors | **0** |

The fixture observation was `2026-10-23T09:46:57.459953Z`; the snapshot was generated at `2026-10-23T09:50:31.582900Z`. The retained raw snapshot SHA-256 is `4694e557b1c23140f9d48d01137ff6e9fc5bfdcf2dc1a726ef1be189d17a0c42`. Evidence and the independent 92-row ledger are in [`research/harvest-e141a921/`](../harvest-e141a921/).

The 62 non-open rows stay visible on **All matches** with blank picks/probabilities. They are not represented as future picks or completed results. Hotspawn supplies fixture membership, teams, start and lock only; it supplies no probability signal.

## Probability provenance

| Method | Open rows | Interpretation |
| --- | ---: | --- |
| `exchange` | 20 | Strict, fresh two-sided external exchange quote |
| `exchange_wide` | 3 | External quote outside the strict 25-point spread ceiling, explicitly low confidence |
| `bookmaker_fallback` | 2 | Previously retained, dated external bookmaker listing with automatic expiry |
| `model_vrs` | 5 | Reproducible model originated from Valve's official standings and roster checks |

Thus 25 rows use external market/book evidence and five use the disclosed VRS model. No row uses Hotspawn, HLTV fan votes, a guessed ranking conversion, a default 50/50 line, or an inferred blank-filling value.

The collector attempts strict exchange coverage first. For rows that remain unresolved it tries HLTV, then Pinnacle and the other configured bookmaker/listing sources. The wide tier and originated model follow the actual code order documented below. No supplemental gap probe was needed in this capture because all 30 open rows were already picked and priced; see `research/harvest-e141a921/gap-research.txt`.

## Review findings and corrections

### Wide-tier documentation now matches execution

The executive-summary ladder and standalone methodology previously said a wide quote was usable only when a row would otherwise have no pick. `scripts/refresh.py` actually tries that tier before the VRS model. Fresh rows `1079198` and `1079200` therefore changed from `model_vrs` to `exchange_wide` without any algorithm change in this session.

The documentation now states the real order: strict exchange, HLTV, Pinnacle, labelled wide quote, then originated model. It explicitly says a wide line can supersede a model line and that the VRS comparison remains published. A regression test checks both the summary ladder and standalone methodology. No threshold, collector, pick, model, or probability behavior was changed.

### Three wide rows are visibly flagged

| Fixture | External probabilities | Spread | Retained VRS comparison | Review meaning |
| --- | ---: | ---: | ---: | --- |
| `1079198` Metizport–BakS | 71.0% / 29.0% | 34 points | 73.8466% / 26.1534% | Same favourite; low-confidence wide quote |
| `1082858` Ground Zero–Off Chops | 28.0% / 72.0% | 34 points | 39.8310% / 60.1690% | Same favourite; low-confidence wide quote |
| `1079200` Color–ex-Zero Tenacity | 35.0% / 65.0% | **58 points** | **68.8395% / 31.1605%** | **Opposite favourites: market picks ex-Zero Tenacity; VRS favours Color** |

For `1079200`, the external midpoint is `[0.35, 0.65]`; its source quote had `bestBid 0.06`, `bestAsk 0.64` and `$684.1234` liquidity. The 58-point spread passes the existing 60-point ceiling but is not precise. The board keeps the external-line pick, publishes the opposite-direction VRS comparison, and labels the row low confidence. The disagreement is not silently reconciled.

An additive `data/review-notes.json` entry links all three Polymarket inputs, Valve's official standings, the source-access limitations and the Actions capture. It appears on **Flagged for Review** in the fresh build.

### Source-access limitations

GG.BET returned HTTP 403 after bounded 10/30/60-second waits. One EGamersWorld re-observation also returned 403; six later checks on that host were skipped after the restriction. These are published limitations, not evidence that a pick is unsupported.

The two retained EGamersWorld book lines were not described as freshly re-read: fixture `1082859` retains its 05:07Z observation and 13:07Z expiry; `1082860` retains its 05:05Z observation and 13:05Z expiry. The build/browser expiry gates withhold them if no valid renewal arrives.

## Independent acceptance

The fresh candidate was built into `public/` with the corrected documentation and additive review note, then checked without changing source data:

- `scripts.probe_e141a921`: status `pass`; 92-row parity, evidence, arithmetic/orientation and gap audit.
- Independent C6 audit: 92 rows, all 30 calculations reproduced, zero failures.
- `scripts.validate`: **92 rows, 30 calculations, 15 pages, 817 internal links/assets, 20 checksums, 221 displayed match rows**.
- `verification-071642e7`: **15 pages, 515 table rows, zero errors**.
- `verification-767649ba`: **2,573 checks, zero failures/advisories, 515 linked table rows**.
- `verification-80504414`: **1,929 checks, zero failures; zero zero-link or internal-only table rows**.
- Unit suite: **1,069 tests, OK, 3 skipped**; includes 11 session tests.
- Independent suites: **9 audits + 5 integrity + 12 C6 tests, all OK**.
- Complete browser suite: **32 accessibility/no-overflow scans at 320/390/768/1440px**, plus navigation, filters, six redirects, evidence anchors, expiry, unresolved/research-only safeguards, live counts and first-phone-screen pick/probability placement.

Machine-readable receipts and browser/test output are retained in [`verification-e141a921/`](../../verification-e141a921/). One historical report belonging to session `86b56cf6`, touched as an unintended side effect of an older auditor, was restored unchanged; no concurrent evidence was overwritten.

## Mobile and navigation review

The executive summary links directly to updated picks, all matches, unresolved/research-only rows, Flagged for Review, sources and evidence. The phone board puts the first pick and its probability on the first screen at 320px and 390px. Every open card shows both teams' percentages, an obvious pick, and an official/manual-review source. Blank unresolved/research-only values remain blank rather than becoming fabricated numbers.

No UI defect was found in this pass, so no unrelated styling or navigation behavior was changed.

## Update cadence

Production retains four scheduled publication opportunities per hour (`:04`, `:19`, `:34`, `:49` UTC), freshness gating, and the separate ten-minute live-receipt watchdog with a 90-minute stale threshold and cooldown/budget guards. This is substantially tighter than the requested 4–8-hour board window. Historical scheduled starts are sparse/coalesced, so the final receipt uses observed run and public-build timestamps rather than claiming that cron alone guarantees delivery. A failed refresh retains the last verified board with a stale warning; it never rewrites source time.

## Release boundary

The candidate above is not, by itself, a deployment claim. The fixed branch is registered in `pages.yml` so its trusted push runs the same refresh, fail-closed quarantine, independent audit, build, validation, unit and browser gates as main. Only a green main merge run, successful Pages deployment and exact live-byte verification complete delivery. Those final identifiers and the resulting fresh snapshot are recorded in `COORDINATION.md`.

## Combined-main addendum — 10:05 UTC snapshot

PR #216 and PR #222 merged while this candidate was being checked. The branch was rebased both times. Their claims, reports, tests, feed-scope UI, three review notes and generated board were retained; no source or probability work was reverted. README conflicts were resolved by keeping both sessions' sections. The review-note conflict was resolved as a JSON union, producing 174 unique notes, including all three `51a9c98a` notes and this session's wide-quote note. The wide-tier correction auto-merged cleanly with the new feed-scope builder code.

The resulting committed main snapshot (`2026-10-23T10:05:50.376420Z`, fixture evidence `10:02:13.241104Z`) was then rebuilt with this session's changes and independently checked: **92/92/92/92 parity, 30 open, 30 picks, 30 probability pairs, zero unresolved**, with the same 20/3/2/5 method mix as the 09:50 candidate. There were no inventory/start/lock/state changes from that candidate.

Combined gates: **1,098 unit tests OK (3 skipped)**; 9 audits + 5 integrity + 12 C6 tests OK; C6 row audit zero failures; validator **92 rows / 30 calculations / 15 pages / 821 links/assets / 20 checksums / 221 displayed rows**; 071642e7 **517 table rows / zero errors**; 80504414 **1,931 checks / zero failures**; and the complete browser suite green. Receipts use the `combined-` prefix in `verification-e141a921/`.

The newly merged `51a9c98a` review note also supplies the missing schedule measurement: between 07:20Z and 09:55Z GitHub delivered one `pages.yml` schedule event and no watchdog schedule events despite the configured crons, while push/PR events continued. This is retained as a platform-delivery limitation, not rewritten as a collector failure. Actual board refreshes in this window continued through verified main pushes; final delivery timestamps are recorded separately.
