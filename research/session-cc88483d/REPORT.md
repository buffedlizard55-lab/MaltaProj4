# Final-day source review — session cc88483d

Research date: **17 October 2026, UTC**. This is a dated audit, not a live-price endpoint.

## Executive outcome

- [HLTV event results](https://www.hltv.org/results?event=8932), retrieved **20:18:50Z**, contain twelve completed series. Executable tests replay every published series winner and score against this capture.
- Day four: **FURIA 2–0 Aurora; BETBOOM 2–1 Falcons**. This session did not collect map scores or finish times. During integration, session f4e34907’s independently sourced map scores were preserved with explicit document-read provenance; finish times remain blank. The result parser's date headings are null; day-four attribution uses retained semi-final timestamps and the published schedule, not an invented heading.
- [Third-place match](https://www.hltv.org/matches/2399416/aurora-vs-falcons-thunderpick-world-championship-2026): **Aurora–Falcons, 18 October 11:30 UTC**, Unix timestamp `1792323000000`.
- [Grand final](https://www.hltv.org/matches/2399417/furia-vs-betboom-thunderpick-world-championship-2026): **FURIA–BETBOOM, 18 October 15:00 UTC**, Unix timestamp `1792335600000`.
- Fixture-specific HLTV ranking-order research leans: **Falcons** (#5 vs Aurora #6), **FURIA** (#4 vs BETBOOM #14). These are **not market prices**. No Sunday percentages or fair odds are invented. The older sourced BO3/BO5 schedule remains attributed historical evidence; the new parser's format field is null.
- At the production inventory observation (**20:16:56Z**) neither Sunday fixture was listed on Hotspawn. Do not imply these research leans were scoreable board picks. Subsequent scheduled refreshes can discover new fixtures without user input.

## Contrarian reasoning (analysis, not verified causation)

9z's opening sweep did not repeat: Aurora won their day-three rematch 2–0. BETBOOM's successive 2–1 wins over PARIVISION, Legacy and Falcons give a specific competitive case to investigate; they do not establish a pricing error at an unknown final price. The final-day research ranks are closer for Aurora–Falcons, so that is the less speculative alternative to examine *once* a verified external line exists. Neither an underdog nor a ranking gap establishes crowd contrarianism.

Summing the twelve verified series scores gives FURIA **7** and BETBOOM **11** maps before the final. On Saturday FURIA played the earlier scheduled two-map semi-final; BETBOOM played the later three-map one. This is map-load/schedule context, **not a measured fatigue effect**. Sunday motivation is unknown. Aurora's reported July rebuild is not a new October roster shock; the attempted fresh news reread was denied and is not called verified this session.

[Hotspawn's rules](https://play.hotspawn.com/how-it-works) successfully re-read **20:25:42Z** state correct-pick points, higher-tier rewards, consecutive-pick bonuses and a weekly leaderboard reset. No verified streak formula, current crowd shares, personal position or leaderboard distribution is available. Consequently no optimal rank-climbing or positive-EV claim is made. Safer default: the supported favourite; an alternative while chasing is an explicit variance preference.

## Full-board coverage and unresolved rows

Production refresh: [Actions run 39066029539](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39066029539).
Snapshot generated **20:18:48Z**; three-way inventory parity **verified**, **81** returned entries / **18** open: **7** market probabilities (6 strict exchange, 1 wide/low-confidence), **6** originated VRS model estimates, **4** research-only picks without percentages, **1** unsupported row. These are dated counts, never a permanent coverage guarantee.

Every open row is attempted, irrespective of tier. Featured accepted lines are retained; remaining rows go through HLTV identity research, sportsbook lines, labelled wide/receipt tiers, the roster-checked Valve model, then ranking-only research. Unsupported values stay blank. Both validators reproduce numerical calculations; browser expiry removes stale prices and picks.

| Hotspawn ID / pair | Outcome at capture | Limitation | Primary source |
| --- | --- | --- | --- |
| 1081519 · NEXVOID–Off Chops | NEXVOID research-only; percentage blank | One HLTV ranking only; Off Chops absent from Valve global standings; no accepted two-way line | [HLTV fixture](https://www.hltv.org/matches/2399547/nexvoid-vs-off-chops-dfrag-logitech-g-pro-series-2026) |
| 1081522 · antidaun–Phantom Academy | Phantom Academy research-only; percentage blank | One HLTV ranking only; antidaun absent from Valve global standings; no accepted two-way line | [HLTV fixture](https://www.hltv.org/matches/2399682/antidaun-vs-phantom-academy-cct-2026-challengers-europe-series-8) |
| 1081861 · Lynn Vision–Morningstar | Lynn Vision research-only; percentage blank | One HLTV ranking only; Morningstar absent from Valve global standings; no accepted two-way line | [HLTV fixture](https://www.hltv.org/matches/2399576/lynn-vision-vs-morningstar-macemedia-void-autumn-cup-2026) |
| 1081863 · Chinggis Warriors–WXM | Chinggis Warriors research-only; percentage blank | One HLTV ranking only; WXM absent from Valve global standings; no accepted two-way line | [HLTV fixture](https://www.hltv.org/matches/2399578/chinggis-warriors-vs-wxm-macemedia-void-autumn-cup-2026) |
| 1082019 · Hacha–LOS NINOS | No supported pick; percentage blank | Exact exchange pair exists but parent event says ended; neither model nor ranking research resolved it | [Operator parent event](https://gamma-api.polymarket.com/events/1203504), [HLTV fixture](https://www.hltv.org/matches/2399768/hacha-vs-los-ninos-cct-2026-south-america-series-7) |

### Hacha investigation: do not trade a contradictory event

[Targeted run 39066865956](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39066865956) at **20:28Z** captured [event 1203504](https://gamma-api.polymarket.com/events/1203504) with `ended: true`, but [market 5796276](https://gamma-api.polymarket.com/markets/5796276) with `active: true`, `acceptingOrders: true`, `outcomePrices: [0.505,0.495]`, future `gameStartTime: 22:00Z`. Do not publish these as valid win probabilities. The prior generic “no exact pair” message concealed the upstream event exclusion. New diagnostics expose exact-match closed/live/ended status in the source-attempt ledger, **without changing the rejection policy**. Tests prove no pick is produced and existing featured picks are untouched.

The targeted Sunday slug queries returned empty arrays. These are candidate-slug checks, **not proof** that no market exists under any other name. The full active CS2 event list and Pinnacle esports feed were also captured and manually inspected: no matching Sunday pair in those responses. Pinnacle did have a different-game FURIA fixture (League of Legends); it is not used as a CS2 line.

## Sources, access and audit boundaries

- `probe/hltv-twc-results.json`: twelve result rows, source URL and response observation timestamp.
- `probe/hltv-twc-2399416.json` and `2399417.json`: current opponent pairs, lineups, rankings and machine-readable start times; empty betting rows and null current format fields remain explicit.
- `probe/polymarket-active-cs2.json`, `probe/pinnacle-esports.json`: official operator inputs. The event-schedule probe also collected unrelated sidebar fixtures; those are **not** counted as TWC results or added to the Hotspawn inventory.
- `targeted/hacha-event.json` / `hacha-market.json`: raw operator state conflict, with receipt/hash and timestamps.
- `tournament/hotspawn-rules.html`, `.txt`, `manifest.json`: successful official rules read; **failed** subsequent HLTV raw-page/news rereads (403 after 10/30/60-second bounded waits) retained. No access restrictions bypassed. Earlier successful parsed receipts are evidence; no claim that the later HTML reread succeeded.
- EGamersWorld runner access was refused; GG.BET was refused; Thunderpick returned HTML without a validated numeric adapter. These are collection limitations, not evidence of universal bookmaker absence. Each current row now prints its actual recorded attempt reason rather than a hardcoded historical 403/HTML claim.
- Existing alias/roster reports and older day-one map details are retained historical research, not re-certified by checking an unrelated page. The incoming session’s day-four map scores are retained with its independent document-read provenance; this session does not relabel its blocked raw reread successful.

## UI/integration changes

- Executive-summary label **and URL** now select the same guidance day; regression tests exercise day 3, 4 and 5.
- One-tap updated picks, day-four results, final-day guide and unresolved limitations on phone; current lines remain on the separate picks board.
- Final-day guide appears first; day-three/day-four pre-match records are explicitly archived, including their once-accurate TBA text.
- Unsupported final-day percentages are absent. Generic “model unavailable because opponents unknown” wording no longer falsely labels the now-populated bracket TBA.
- Root static fallback and runtime artifact are built by the standard generator, not hand-edited tables. The incoming session regenerated the derived quote dossier with its existing builder (raw historical receipts remain unchanged); tests check current rows against the current generated evidence ledger rather than requiring new fixtures in old documents.

## Verification performed

- **333** combined unit/regression tests; **9** audit tests; **5** independent integrity tests; **12** c6 tests passed.
- Current independent row audit: **81 rows, zero failures** (`final-row-audit.md`). It checks retained source fields and arithmetic, not the objective truth of upstream feeds.
- Root build validator: **81** primary rows, **13** reproduced probability calculations, **15** HTML routes, **575** internal links/assets, **20** artifact checksums and **195** displayed match rows checked at the current build. Internal-link checks do not claim external source uptime.
- Browser: **32** page/viewport no-overflow/accessibility scans at **320/390/768/1440px**, navigation/filter/subpath checks, plus **seven** exact-boundary expiry scenarios passed. Final build rerun before PR checks.
- Source-access failures, unverified format/map/finish-time fields, absent final lines/board membership, leaderboard limitations and Hacha status conflict are published on **Flagged for Review**. None is silently filled in.

## Concurrent integration

While PR #71 was being prepared, session f4e34907 merged PR #69 with overlapping final-day work. Both histories and complete research directories are preserved. The merged guide retains its independently read semi-final map scores and BO3/BO5 format provenance, our stricter source-attempt explanations and parent-event exclusion diagnostics, and its exact-pair/exact-start future-board discovery links. Incoming guidance is archived verbatim in `integrated-f4e34907-guidance.json` for audit; conflicting generated HTML is rebuilt from the combined data. The later 20:18:48Z verified snapshot is used without blending observations. Organizer confirmation remains explicitly unverified. Combined tests: 333. Full checks rerun after reconciliation.
