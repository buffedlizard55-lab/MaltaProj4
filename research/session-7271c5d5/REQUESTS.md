# Session `7271c5d5` — Cross-Session Handoff Notes

Per `COORDINATION.md` ownership rules, session `7271c5d5` avoided editing shared files actively claimed in open sibling PRs (`data/review-notes.json` in PRs `#145` / `#151`; `scripts/*` and `site/*` in PRs `#147` / `#151`). Ready-to-merge artifacts are staged in `research/session-7271c5d5/`:

1. **`data/review-notes.json` (`indent=1` drop-in entries in `research/session-7271c5d5/REVIEW-NOTES-TO-ADD.json`):**
   - `k27-nexora-1082769-four-source-corroboration-2026-10-22`: documents the 4-source corroboration behind `egw-4yp_dlKtNl-nexora-k27` (`88.8% / 11.2%`), including Polymarket market `6029909` (`$151.01` liquidity, `16:00Z` vs `17:30Z` PandaScore start-time offset) and Stavka/Betcity+Melbet (`7.80 / 1.06` -> `88.0%`).
   - `benched-gods-titanflow-1081597-morrow-seeding-and-forfeit-fix-2026-10-22`: documents HLTV LB R1 elimination of `MORROW` (`ex-6666 1-0 MORROW`), `benched gods`' `1-0` default forfeit win (`2399691`), HLTV `2399696` `Match postponed`, and Polymarket `6028868` wrong-opponent seeding (`MORROW vs TitanFlow`).
   - `bestia-shinden-1082689-cross-venue-split-2026-10-22`: documents the cross-venue near-coin-flip split (`ShindeN 52.5%` on Polymarket vs `BESTIA 50.8%` on Picklebet AU, `50.5%` on Stavka, and `57.5%` on Valve VRS).
   - Also note in `data/review-notes.json` item `line-audit-2026-10-22` (added in PR `#149`): the FlyQuest source URL still points to synthetic `.../match/DFRAG26/flyquest-vs-staqued`; replace with canonical `https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3` (already updated in `data/book-receipts.json`).

2. **`scripts/core.py::orientation` optional bounded start-tolerance audit note (for `scripts/core.py` owner `ac4743a3`):**
   - Strict `0s` start-time equality rightly prevented silent mis-joining, and blocked Polymarket `6029909` (`K27 vs NEXORA`, `16:00:00Z` PandaScore vs `17:30:00Z` HLTV/Hotspawn) where Quarterfinal 3 of `CIS LAN Championship #9` shifted by 90 minutes on the same LAN day. Keeping exact `0s` equality in automated orientation while pricing such shifted slots explicitly via corroborated receipts in `data/book-receipts.json` preserves zero-false-join safety.
