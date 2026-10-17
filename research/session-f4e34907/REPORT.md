# Final-day integration audit

## Reproduction

- Networked source run: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39066005984
- Snapshot: `snapshot.json`; source observations and request receipts: `probe/`.
- Independent document reads: `MANUAL-READS.md` (transcribed fields, not raw HTML).
- Row replay: `local-row-audit.md`, zero failures.
- `python -m scripts.day5_f4e34907` replays the two semi-final series from the retained HLTV response and updates only dated research content, never market probabilities.
- `python -m unittest discover -s tests`: 323 tests pass, including fresh replay of all 12 Days 1–4 series, confirmed final opponents/UTC clock, final-day navigation, no unknown-opponent excuse for known teams, and exact future pair/start discovery.
- Independent suites: 9 audit + 5 integrity + 12 c6 checks pass.
- Build validator: 81 primary rows, 13 calculations, 15 pages, 571 internal links/assets, 20 checksums and 195 displayed rows.
- Browser: 32 responsive/accessibility scans and seven exact expiry scenarios pass. PR checks also rerun the build and browser suite on GitHub.

## Source scope

Hotspawn is official for its own fixture inventory, never probability. Polymarket and Pinnacle are primary operator sources for their returned lines. Valve publishes model inputs and methodology. HLTV is specialist secondary evidence for tournament facts, NOT organizer verification. Sunday organizer-confirmed facts remain unverified; unknown numeric prices stay blank. The final-day cards are research-only ranking baselines and conditional strategy, not calibrated odds or submitted picks.

At 20:18 UTC: 81 entries / 18 open / 13 numeric lines / four research-only / one unsupported. Both Sunday TWC fixtures were absent from that capture, despite HLTV confirming the opponent pairs. This is a dated membership statement, never a claim about future board availability. The production refresher rechecks the board and pricing hierarchy; a later exact-pair/exact-start match links the research cards to the expiry-checked live board.

## Publication

PR https://github.com/buffedlizard55-lab/MaltaProj4/pull/69 merged at 2026-10-17T20:30:48Z as `cf5dee1508c00e9552e9d823df0e5fe6a3b9657e` after passing checks. Production refresh/deployment run: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39067030523 . Its deployment receipt verifies actual live build bytes, not merely workflow success.

Production run **succeeded**, including the exact live-byte verification and evidence upload. No deploy retry was needed. This report and the post-merge coordination receipt are retained on the session branch after the implementation merge.
