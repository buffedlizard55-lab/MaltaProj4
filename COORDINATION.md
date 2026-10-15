# Shared task board

## Current ownership

Session **c4d25599** is the final integrator. Arena fixes this session to `arena/c4d25599-maltaproj4`; no other branch will be created, changed, or pushed.

| Task | Status | Owner | File scope | Updated (UTC) |
| --- | --- | --- | --- | --- |
| Integrate preserved implementation and independent audits; verify and fix collection, identity matching, evidence expiry and fallback coverage | in progress | c4d25599 | scripts/**, tests/**, data/**, requirements.txt, research/**, audits/**, .gitignore | 2026-10-15 |
| Final mobile dashboard, executive summary, picks, unresolved and Flagged for Review pages | in progress | c4d25599 (final integration) | site/**, docs/**, index.html, README.md, package*.json | 2026-10-15 |
| Scheduled refresh, build/security/browser checks, PR merge and verified GitHub Pages publication | in progress | c4d25599 (final integration) | .github/**, root deployment files, COORDINATION.md | 2026-10-15 |
| Earlier independent source and acceptance audits | needs review | 21bf0503, 95b588c2, c6e9f285, f65f940e | audits/** and their uniquely named verification/research directories (preserve on integration) | 2026-10-14 |

## Coordination log

- 2026-10-15: Read local main and enumerated **all remote heads and their coordination boards** before claiming work. Local fetch initially exposes only main; all actual remote branches were checked with GitHub/git. Main still contains only README.md; prior PRs #2, #3, #4 and #6 remain open. All earlier claims are older than 60 minutes without commits (latest observed 2026-10-14 08:42:34 UTC). Taking over unfinished final integration under the user's stale-claim rule. No active claim is overwritten.
- Preserve the ee1fb536 implementation, 66b553de integration/research, independent audits and all earlier coordination histories. Review rather than blindly combine overlapping implementations. Previous verification statements are historical, not verification by this session. Other branches remain untouched.
- Before implementation, commit and push this claim. Run `git pull --rebase` (with merge preservation where needed) before every subsequent push. Keep work on this session's fixed branch. Log any conflicts and resolve without discarding other work.
- Evidence standard: Hotspawn establishes the fixture inventory only, never probability. Keep the featured external-line method; try attributable HLTV evidence and then primary esportsbook lines only for uncovered fixtures. Only independently reproducible calculations on verified inputs may be published as derived probabilities. Unknown facts/odds/probabilities remain blank; unresolved picks and source/access limitations are visible in the executive summary and Flagged for Review.
- Sandbox networking is limited to GitHub and package registries. Live non-allowlisted source checks must run through normal GitHub Actions networking or available retrieval tools; do not claim a source was checked when it was not. No paywall/access-control bypass, credential solicitation, fabricated rows or probability estimates from Hotspawn votes.
- Outstanding inherited findings to independently reproduce and address: source-update TTL not enforced in the browser; non-finite liquidity accepted; validator missing evidence/identity checks; a wrong-game API payload can erase last-good inventory; Pages previously showed only the README and configuration changes returned 403. Irregularities do not block publication, but broken builds or false verification do.
