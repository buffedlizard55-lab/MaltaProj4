# Independent source and phone review — session e3fe9518

## Latest complete local release gates — 2026-10-24 08:18 UTC

**Main `63e7d39` plus this integration: 1,472 unit tests OK (one skip), 43 own tests; 9 audits, 5 integrity, 12 independent C6; all 11 npm browser suites and three own four-viewport clock runs pass (14 pass receipts).** Actual-device-clock run is against the **local canonical artifact**, not public Pages proof. Snapshot, honest overdue/90-minute warning, simulated five-hour lock rotation, all source-class labels, both shares on every active card, whole first score-pair bottom, all preserved closed-card warnings and true eight-hour expiry are checked. [Exact release receipt](release-verification.json), [unit log](unit-release.log), [browser log](browser-release.log), [current independent source audit](current-source-audit.md).

Current build: **92 inventory rows, 29 open / 29 picks / 29 probability pairs, 63 not open, zero unresolved.** The original immutable 06:19 capture had31 open: two subsequently passed their sourced locks. Only their six derived recommendation fields are withdrawn; every raw fixture/evidence/source receipt and observation time, and every other row, is identical. This is **not a new harvest or re-pricing**. Models remain9 (6 official-file inputs +3 HLTV-mirror inputs); 3 book listings are not independently operator-confirmed ticks. Current exact primary-source file check covers12 team sides. All221 upstream review entries survive unchanged +3 own (224 total).

Both root and canonical validators: **15 pages, 92 source rows, 29 reproduced pairs, 862 links/assets, 20 checksums, 230 displayed rows**. Independent C6 and source audit: zero failures. `DatedVerificationTests` retains every historical31-row/source/tamper assertion against the existing SHA-bound archive; a separate current-row provenance/ID-set gate allows genuine unsupported blanks rather than freezing collection. No test weakened or source timestamp renewed.

**Public release verification remains pending until merge/deployment.** A local pass or a branch-mode audit of an older production release is never counted as proof that this release is public. GitHub Checks annotations provide compact escaped hash-bound receipts through the allowed API; artifact/log result hosts outside the allowlist are not proxied or bypassed.


## Executive result (dated capture, not a live-site claim)

The audited input is the preserved [snapshot](snapshot.json), generated
**2026-10-24T06:19:43.492019Z**, fixtures observed **06:16:00.648005Z**,
SHA-256 `ae127443c707c6de75e7bce0e3d827620d5ef4a5c8b40ef2b89b2c4bd352b619`.
It contains **92 official-feed rows, 31 open matches, 31 picks, 31 calculated
probability pairs, 0 research-only picks and 0 unresolved open matches**.
The other 61 rows are past/not-open source records, not missing future picks.
No retroactive picks are invented for them.

| Category at capture | Rows | Meaning / source for manual review |
| --- | ---: | --- |
| Strict exchange | 16 | Our normalized calculations from [Polymarket's own CS2 market API](https://gamma-api.polymarket.com/sports); per-market links in the row ledger |
| Wide exchange fallback | 3 | Same operator, but a wide-spread, explicitly low-confidence line; [exact source inputs](source-audit.json) |
| Bookmaker listing fallback | 3 | Thunderpick prices **reported by BO3.gg**, not directly confirmed operator prices; [BO3.gg's own CS2 API](https://api.bo3.gg/api/v1/matches?page%5Boffset%5D=0&page%5Blimit%5D=100&filter%5Bmatches.status%5D%5Bin%5D=upcoming&filter%5Bmatches.discipline_id%5D%5Beq%5D=1&sort=start_date&with=teams,tournament) |
| Official-file originated model | 6 | Our calculations from [Valve's immutable October 5 standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md), not betting odds |
| HLTV-mirror originated model | 3 | Our calculations from [HLTV's dated Valve-points table](https://www.hltv.org/valve-ranking/teams/2026/october/24); secondary mirror inputs, not operator odds |
| Past/not-open feed records | 61 | Values deliberately blank; original [official Hotspawn scoped feed](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1) reports these records |

**Where to go on the site:** [updated picks](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html),
[executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/index.html#exec-summary),
[all matches](https://buffedlizard55-lab.github.io/MaltaProj4/matches.html),
[unresolved picks and limitations](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html),
[Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html).
These are destinations, not a claim that the public deployment has already caught up.
The live verification receipt is required before claiming publication.

## What this session added (no duplicate collector or probability model)

- [`scripts/audit_e3fe9518.py`](../../scripts/audit_e3fe9518.py) follows every fixture
  receipt and accepted quote back to the snapshot's successful HTTP source-check
  hash, byte count, observation time and exact source authority. It calls the
  existing collector-independent C6 auditor for arithmetic/identity replay,
  rather than duplicating or importing the pick selector.
- It independently parses Valve's actual standings document and checks each
  official-model side's **standing, team name, points and roster** against its
  hash-bound primary file. This catches self-consistent fabricated inputs that
  arithmetic checks alone cannot catch. All six current official-file model
  rows (12 sides) match the primary document.
- It separates direct-operator inputs, third-party listings, official-input
  models and HLTV-mirror models. The **primary-only market-estimate column
  stays blank for every listing and model**. A successful audit is internal
  and primary-file consistency, never a verified true probability of winning.
- [The full source table](source-audit.md) has an official fixture link on each
  of its 92 rows, separate calculated/primary-only columns, source links and
  limitations. Its fallback trail names every recorded attempt for all 15
  non-featured matches. All have recorded **HLTV first, then esportsbook**
  attempts. A failed or shell-only fetch is never called proof of no odds.
- [`tests/browser_e3fe9518.cjs`](../../tests/browser_e3fe9518.cjs) checks the real
  rendered values for **every** actionable phone card, both teams in fixture
  order, the marked pick, model/listing/wide-line labels, the executive-summary
  destinations, 44px first-screen updated-picks CTA, one-tap evidence and full
  first-card probability visibility above the fixed nav. It checks 320×568,
  390×844, 768×1024 and 1440×900. The archival test pins the clock, not the DOM;
  it never hides a stale notice to manufacture a fresh screen. A second genuine
  expired clock verifies that both teams' percentages and table picks vanish.
- The read-only [verification workflow](../../.github/workflows/verification-e3fe9518.yml)
  runs on this scope's changes and every six hours. Its runner can reach source
  hosts unavailable to the authoring sandbox. It verifies actual Pages bytes,
  independently rechecks the operator inputs, records drift without repricing
  the archived snapshot, and runs phone acceptance at the real device clock.
  It has **contents: read**, cannot push, does not harvest or generate picks,
  and never bypasses access controls. PR checks remain offline.

## Primary documents actually retrieved and checked

[Machine-readable primary-document receipts](primary-document-checks.json)
record the exact GitHub Contents API requests at immutable commit
`eec4853d7bcf0f1f7efe7f0d901234bef7e98b75`, successful `gh api` retrievals,
byte counts and SHA-256 digests. No HTTP status was invented from a command's
exit status. The downloaded standings file's SHA-256 is
`df96e7fc3cd91a2687ec08cac0128e50cc4e4e55346581679572e881d79ae61b`,
identical to the existing vendored file and its official-source capture.

| Primary document | Checked fact | Official source |
| --- | --- | --- |
| `model/fit.js` | `defaultGlickoParams.rd = 75`; `priorWinExpectation` uses the Glicko win/loss deltas | [Valve source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/fit.js) |
| `model/glicko.js` | Expected-score implementation used by the published fit | [Valve source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/glicko.js) |
| `model/team.js` | `TEAM_OVERLAP_TO_SHARE_ROSTER = 3`, comparison uses `overlap >=` | [Valve source](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/team.js#L5) |
| `modelfit.png` | Chart visually inspected; printed fit is `y = 0.7986x + 0.126` | [Valve chart](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/modelfit.png) |
| Global standings, October 5 | All 12 official-model team/point/roster inputs match their exact standings rows | [Valve standings](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md) |

The project applies the chart's slope symmetrically around 50%:
`p = 0.5 + 0.7986 × (E − 0.5)`. That symmetry is **our model's documented
choice**, not an official forecast or a claim of current out-of-sample calibration.

## Limitations and irregularities (do not disguise as source verification)

1. **Third-party prices:** rows 1083123 (Grêmio/Yawara), 1082859
   (NEXVOID/Alter Ego), 1082860 (FlyQuest/Staqued) contain BO3.gg-reported
   Thunderpick quotes, not raw operator responses. The audit keeps primary-only
   market values blank. The site already labels these cards listing-derived.
   A blanket methodology sentence, “Every accepted price retains the official
   operator’s raw fields and timestamp”, overstates this evidence. The exact
   builder correction is requested from its active owner in
   [PR #251](https://github.com/buffedlizard55-lab/MaltaProj4/pull/251#issuecomment-6380987169);
   no competing builder edit was made.
2. **Ranking mirror and mutable references:** three mirror rows use HLTV's dated
   Valve table instead of Valve's monthly file. This is allowed research input,
   but not a primary operator price. Their formula/chart links use mutable
   `/blob/main/`; immutable checked equivalents are linked above. No unsupported
   primary probability is filled in.
3. **Publication vs canonical UI:** on base `dce494b`, `site/assets/style.css`
   already has balanced blocks, but shipped `assets/style.css` is an older copy
   with brace balance +1. Public/ regenerated by the canonical builder passes
   phone geometry, but the committed root does not contain those repaired bytes.
   This is already owned by PR #250; exact reproduction and hashes were sent to
   [that owner](https://github.com/buffedlizard55-lab/MaltaProj4/pull/250#issuecomment-6380914486).
4. **Publication-gate alias drift:** the new fixture 1083121 has Hotspawn label
   `Projeto do KinGui` and Polymarket label `Tropa do KinGui`, with an explicit
   sourced identity-register entry. C6 replays it, but the older 0cc1138a verifier
   ignores that mapping and fails its gate. Its active owner was notified in
   the same comment. Nothing is “fixed” by inventing a mapping or deleting a test.
5. **Collection ceilings:** the captured attempts include GG.BET HTTP 403 and
   shell-only Thunderpick responses. These show access/adapter limitations,
   not bookmaker non-coverage. The separate unresolved page and executive-summary
   limitations must remain available even when their current open-row count is zero.
6. **Cadence:** the main refresh workflow requests :04/:19/:34/:49 UTC and the
   watchdog targets a 90-minute-old snapshot; the new audit is every six hours.
   These are trigger targets, not guarantees of GitHub delivery or source access.
   The eight-hour expiry is the fail-closed evidence ceiling, not a promise of
   refreshed source data.

## Verification status

- Supplemental suite: **37 tests passed**, including primary-file fabrication,
  receipt hash/size/time corruption, authority spoofing, unsupported provider,
  fallback-order omissions, actual expiry, and live-state drift negatives.
- Independent C6: **92 rows / 31 price calculations**, zero failures.
- Supplementary provenance: **92 rows**, zero errors; 6 official-model rows
  cross-checked against the hash-matched actual Valve file.
- Canonical build validator: 15 pages, 92 source rows, 31 calculations,
  874 internal links/assets, 20 artifact checksums, 234 displayed rows.
- New phone/source acceptance: passed all four viewports with no DOM overrides;
  [receipt](canonical-mobile.json).
- Initial full unit run: **1,233 tests, 8 failures, 1 error, 1 skip**. These are
  the committed/root CSS mismatch and legacy alias-verifier gap described above;
  they are not attributed to the new files and are **not reported as green**.
- Upstream repairs arrived during integration: **PR #251 merged as `5ddf0f2`**.
  Its owner fixed the new explicit identity-alias replay and staged matching
  root/canonical CSS. The pre-push rebase had one COORDINATION prepend conflict;
  both session blocks were preserved in full. The planned PR #250 handoff was
  superseded; no files from that pending branch were fetched or edited.
- **Integrated full unit suite: 1,291 tests OK (one skip)**. Rebuilt and validated
  the 92-row/31-calculation tree; new all-card phone/expiry checks pass on that
  integrated source. Existing independent 9 audit + 5 integrity + 12 C6 tests and
  all nine existing browser suites passed before rebase and are re-run for release.
- Three own, additive source-linked findings (`session-e3fe9518-*`) are now
  published through the existing Flagged for Review builder: primary/listing
  provenance, verified primary model inputs versus mirrors, and the source-side
  publication-gate recovery. The blanket methodology wording remains flagged,
  not hidden by an overlapping builder edit.
- GitHub's shared REST budget was exhausted at 06:44Z (0/5000; reset 07:10:07Z).
  The watcher was stopped; REST polling is paused until reset. No authentication
  failure, token change or access-control workaround is involved.
- Actual live publication and merged-PR receipts remain pending. No publication
  success is inferred from a local build or an API queue status.

### Initial integrated local gates (before main advanced)

All **1,291 unit tests (one skip), 9 audits, 5 integrity, 12 C6 tests and ten browser suites** pass after the three own review notes are added, with canonical indent=1 UTF-8 preserved. Root and public validators pass: 92 rows, 31 calculations, 874 internal links/assets, 20 checksums, 234 displayed rows. All 185 existing review entries are preserved unchanged. [Exact release receipt](release-verification.json) · [Browser log](browser-release.log). Actual publication is still tracked separately.

### Completed-owner copy handoff and strict release expectation

PR #258/main `4b083af` records owner 174afa4f's **tasks done**. The previously requested one-sentence verification-scope correction was still unmade. After publishing a narrow handoff claim, final integration corrected **only that copy** in `scripts/build.py`; no fallback, calculation or navigation changed. A new assertion prevents a bookmaker listing/link from again being represented as an official operator raw response. The source-linked review finding remains open for the genuinely unconfirmed operator ticks, not for copy now repaired. Main PR #260 (`afaa07a`)'s source-drift publication guard and fatal gates are preserved.

Unmerged-branch remote checks now explicitly label their expected release as **observed production, not this unmerged branch**. Main (and local strict-release runs) must match the merged manifest or a coherent newer release. Two negative/positive tests prevent branch checks from silently claiming an unreleased build is live. No GitHub API quota workaround is involved; these are ordinary public-site HTTP reads.

### Final integrated release gates — main `184e22f` plus this release

**1,322 unit tests OK (one skip), including 40 own supplemental tests; 9 audits, 5 integrity, 12 C6; all ten browser suites pass.** Both root and public validators: 15 pages, 92 sourced rows, 31 reproduced probability pairs, 874 links/assets, 20 checksum matches, 234 displayed rows. The independent source audit has zero errors. All 189 upstream review entries survive unchanged, plus the three own entries. Entire source JSON equals main after excluding build metadata. [Exact release receipt](release-verification.json) and [full browser log](browser-release.log). Corrected source-verification copy is generated canonically, not hand-edited into HTML. PR/actual live publication proof follows after deployment.

### Combined-main fixture contract repaired, not weakened

Main #261 correctly requires an HTTPS source, written basis and committed alias-register membership; #257's old positive-only fixture omitted the basis. The 1,329-test combined repeat caught exactly that one mismatch (all ten browser suites passed). Scope was claimed after #257 marked its test work done, and reported to [#261](https://github.com/buffedlizard55-lab/MaltaProj4/pull/261#issuecomment-6381248119) and [#257](https://github.com/buffedlizard55-lab/MaltaProj4/pull/257#issuecomment-6381260177). The positive fixture now reads the **actual already-reviewed registry entry**, not an invented basis or a loose HTTPS link. Removing the basis/source or using HTTP is explicitly refused. All original assertions and the hardened verifier remain unchanged; 13 owner-module tests pass. The subsequent full integrated repeat determines release status. Main #265's three dated review findings are also retained (194 upstream + 3 own entries).

### Current combined-main gate and observable remote receipts

The owner fixed the same incomplete alias fixture in merged #266; that upstream version and its stronger negatives are retained, and the duplicate own fixture patch was dropped. On main #267 + this branch, **1,345 unit tests pass (one skip), including 42 own tests; all nine legacy browser suites pass**. Source/number inputs are unchanged. Validator now checks **878** links/assets because the upstream summary quicknav adds four links. All 201 upstream review notes + three own IDs are preserved.

**Not release-green yet:** the unchanged strict own test finds the new summary quicknav clips the first score pair at 320x568 (top497.328, height55.688, bottom553.016; fixed tab top507). The owner's saved measurement tests only the top. Reported with exact bounds to [#267](https://github.com/buffedlizard55-lab/MaltaProj4/pull/267#issuecomment-6381438957); its active CSS scope remains untouched until a fix/handoff. No weakened test or fabricated fresh DOM.

Original runner40071009978 completed06:52:42: canonical and actual public-source/byte steps succeeded, live-mobile step failed. Its exact mobile cause is unknown: ordinary log retrieval redirects to a non-allowlisted results host and fails EOF. Subsequent runs now publish compact escaped source/mobile receipts as **normal GitHub Checks annotations**, readable through the supported GitHub API, in addition to artifacts. They bind the exact asset-verified manifest to the adjacent snapshot read and retain real failure/phone bounds. This is ordinary CI output, not a proxy or credential workaround. Separate unit tests reject annotation command injection and cross-deployment read races. A403 on cancelling one obsolete own run was respected (no Actions-write permission); no further cancellation attempted. PR #264 is open and deliberately unmerged until the full first-card acceptance passes.

### Final docs-only main update also re-tested

Main `0fc34cd` adds only coordination/e9be3e6b dated receipts after `63e7d39`. Both sides are retained; **every public byte, executable and source field remains unchanged**. Full unit repeat after that merge: **1,472 OK, one skip**. The exact snapshot hash in the release receipt still matches. No simulated or local actual-clock test is called public Pages proof.
