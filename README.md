# CS2 Pick Desk — Hotspawn research dashboard

Source-linked, mobile-first static dashboard for CS2 Hotspawn Pick’ems. GitHub Pages serves `site/`. The executive summary links directly to all match picks, unresolved picks, methodology and flagged irregularities.

## Run locally

```sh
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m http.server 8000 --bind 0.0.0.0 --directory site
```

## Automatic refresh

`.github/workflows/pages.yml` runs every six hours and on main changes. It renders public sources with Playwright, retains last good data on failure, checks HLTV for fallback research, attempts conservative direct sportsbook matching, runs tests and publishes an artifact to Pages. GitHub schedules are best effort, not a freshness guarantee. Previous data is recovered from the last successful snapshot artifact. No data commits to main or secrets are needed.

The initial source research captured 18 upcoming lobby cards plus one tournament-only fixture. This is **not verified full weekly coverage**: lobby weekly/filter counts differ. The app exposes this discrepancy. The collector must not silently promise full coverage when source extraction is partial or blocked.

Only exact, independently verified two-sided match-winner lines support a probability. Missing identities, aliases or dates stay unresolved. Model output is explicitly labeled calculated, never official. No arbitrary rank-to-probability or default 50/50 fallback is used. A calibrated historical-results fallback is not yet deployed; see the unresolved page.

## Evidence

- https://play.hotspawn.com/cs2-pickems — fixture inventory, never win probabilities
- https://www.hotspawn.com/counter-strike/tournament/elisa-breakout-series-2 — confirmed UTC schedule
- https://www.hltv.org/matches — independent fallback research
- https://thunderpick.io/esports/cs2-betting — direct bookmaker winner lines

Every displayed fixture has its official Hotspawn link. Every accepted line has a direct bookmaker link and observation time. See `COORDINATION.md` and the Flagged for Review page for limitations. Browser-local research timestamps record retrieval, not bookmaker quote issuance. Odds may change immediately.
