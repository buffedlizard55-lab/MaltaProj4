# Shared task board

Session: `arena-ee1fb536` (integration owner). Session branch is fixed by the workspace to `arena/ee1fb536-maltaproj4`; no alternate branch will be created.

| Task | Status | Owner | File scope |
| --- | --- | --- | --- |
| Research official Hotspawn match discovery and external CS2 evidence sources | in progress | arena-ee1fb536 | research/** |
| Implement auditable match refresh, probability calculation, fallback evidence and tests | in progress | arena-ee1fb536 | scripts/**, tests/**, data/**, requirements.txt, .gitignore |
| Integrate accessible mobile dashboard, executive summary, picks and review pages | in progress | arena-ee1fb536 (final integration) | site/**, README.md |
| Scheduled refresh, Pages deployment, PR/merge and deployment verification | in progress | arena-ee1fb536 (final integration) | .github/**, COORDINATION.md |

## Coordination log

- 2026-10-14: Read repository before starting. Repository contains only README.md; no existing tasks, application, match data or integrations. Remote has only main. Claimed the scopes above. No other sessions' scopes encountered. Claim will be committed and pushed before implementation.
- Verification standard: Hotspawn establishes match membership only; never probability. External primary bookmaker/exchange evidence or attributable HLTV evidence is required. Model-derived probabilities must be explicitly labeled, not represented as verified bookmaker lines. Missing facts remain blank and are published for review. Lack of access is not evidence of an empty lobby.
