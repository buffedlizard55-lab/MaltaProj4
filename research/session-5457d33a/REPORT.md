# Follow-up verification — 18 October 2026

## Scope and findings

The existing implementation already contains inventory discovery, external-market pricing, source receipts, four-days-of-results review, final-day research, mobile navigation, unresolved coverage and scheduled publication. This session does not claim to have independently re-fetched historical esports facts. The sandbox allows GitHub/package hosts only. Source research remains dated and attributed in the existing evidence pages.

The prior coordination log identified a reproducible destructive-maintenance hazard: `scripts/day5_f4e34907.py` rebuilt research cards without their later Thunderpick market blocks, reverted the review date and restored the incorrect combined Malta-time parenthetical. It is not part of the refresh workflow, but manually rerunning it could destroy newer evidence. The applier now refuses newer research, any existing market block, or missing/invalid/timezone-naive chronology before reading old receipts or writing data. Historical permitted output uses explicit UTC and a derived Unix start instead of the ambiguous parenthetical. No odds, production rows, source timestamps or generated pages changed.

## Verification performed here

- 355 unit/regression tests passed, including six new preservation/chronology tests.
- 9 independent failure-mode audit tests, 5 integrity tests and 12 c6 tests passed.
- Build/validator replayed the committed historical bootstrap: 81 sourced rows, 13 calculations, 568 internal links/assets, 20 artifact hashes and 192 displayed rows. These are not current coverage figures: source timestamps remain unchanged.
- 32 browser viewport/accessibility scans passed at 320/390/768/1440px; seven board-expiry and four research-quote boundary/future-clock cases passed.
- Production run [39077459088](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/39077459088) was inspected through GitHub's API: refresh, independent row audit, browser checks, deployment and exact live-byte verification all succeeded. That proves the recorded pipeline checks, not the accuracy of every esports claim or uninterrupted future refresh delivery.

## Source links and limitations

- [Official Hotspawn lobby](https://play.hotspawn.com/lobby): fixture membership only, never probability.
- [Existing day-5 official-book receipt](../session-e0fd5a32/day5-lines.json) and [verification report](../session-e0fd5a32/DAY5-ODDS-VERIFICATION.md): historical observed prices, not renewed by this fix.
- [Existing final-integration report](../session-cc88483d/REPORT.md): source boundaries, days 1–4 and unresolved matches.
- [Current picks](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html), [Day-5 guide](https://buffedlizard55-lab.github.io/MaltaProj4/analysis.html#day-five-guidance), [unresolved](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html), [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html).

No fabricated probability is substituted for absent two-sided lines. Historical final-day quotes expire separately from the board; do not present them as live recommendations. The pre-existing single-book discrepancy, official-organizer verification gaps, source restrictions and missing leaderboard-distribution data remain visible. A contrarian choice is not proven positive expected value merely because an earlier underdog won.

## Publication blocker found on fresh inventory

PR #75 merged successfully, but production run 39081708156 correctly withheld publication when refreshed match content overflowed at 320px. Runner-only diagnostic collection preserved the actual assertion in `deploy-failure.txt`; sandbox log redirects were blocked. Mobile match cards now use zero-minimum grid tracks, wrap team names and time/diagnostic text, and constrain badges. The browser test additionally injects long unbroken content into each cell at 320px without removing the existing full-site overflow/accessibility checks. Local build, hash/link validation, 32 scans, the new stress scenario and 11 expiry cases pass. Root fallback regenerated through the standard verified staging script without refreshing or relabelling historical bootstrap data.
