# Independent coverage and delivery audit — 24 October 2026

## Where to find the picks

- [Executive summary](https://buffedlizard55-lab.github.io/MaltaProj4/)
- [Updated picks / both-team probabilities](https://buffedlizard55-lab.github.io/MaltaProj4/picks.html)
- [Every retained fixture](https://buffedlizard55-lab.github.io/MaltaProj4/matches.html)
- [Unresolved, research-only and limitations](https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html)
- [Flagged for Review](https://buffedlizard55-lab.github.io/MaltaProj4/review.html)
- [Evidence ledger](https://buffedlizard55-lab.github.io/MaltaProj4/evidence.html)

These are the existing production routes; this session does not claim to have
created another dashboard. The collector and mobile UI are actively owned by
other sessions, so duplicating their edits would conflict with the shared board.

## Current retained evidence, not a fabricated live observation

Audited `data/latest.json` from main commit
[`dce494b`](https://github.com/buffedlizard55-lab/MaltaProj4/commit/dce494b7209629def3eab0d023da39935b62f713):

- snapshot `2026-10-24T06:19:43.492019Z`;
- fixture evidence `2026-10-24T06:16:00.648005Z`;
- 92 API / 92 CS2 page / 92 lobby / 92 retained fixtures;
- 31 open, **31 picks, 31 probability pairs**, zero open unresolved;
- 61 historical/not-open feed entries remain listed but must not be advertised
  as current recommendations;
- methods: 16 strict exchange, 3 wide exchange, 3 indirect bookmaker listings,
  6 originated Valve VRS estimates, 3 originated estimates using HLTV's dated
  view of Valve points.

Every open row, its fixture source, probability source, classification and
limitations is in [ledger.md](ledger.md); [ledger.json](ledger.json) also preserves
every attempted provider, result, reason and URL. The ledger records the exact
snapshot SHA-256. **This is evidence replay, not a new live external-source fetch.**
The sandbox permits GitHub/package-registry egress only. The separate read-only
runner workflow verifies the public site's own manifest and files without
publishing or editing the collector.

## Fallback requirements checked

Every one of the 15 non-featured rows records HLTV research before an esportsbook
attempt (Pinnacle, then the wider exchange/book/model ladder as applicable). None
uses Hotspawn's crowd vote as a probability. Unsupported percentages must remain
blank. Originated model percentages are model estimates, not observations of a
betting line. BO3.gg bookmaker listings are indirect evidence, not direct
bookmaker confirmations. No blanket promise that future low-tier fixtures will
always have a defensible numerical probability is justified: the existing
unresolved page is the required fail-closed outcome when evidence is absent.

## Verification actually run

| Gate | Observed result | Source / reproduction |
| --- | --- | --- |
| Independent fallback audit | 92 rows, 31 open, zero auditability failures | `python -m scripts.delivery_audit_928d7320 --output research/session-928d7320` |
| New rotation-proof regressions | 15 tests, OK | [tests.log](tests.log), `python -m unittest discover -s tests -p test_session_928d7320.py` |
| Independent arithmetic replay | 92 rows, zero failures | [independent-row-audit.md](independent-row-audit.md), `python verification-c6/audit_snapshot.py data/latest.json` |
| Root validator | 92 rows, 31 reproduced calculations, 874 internal links/assets, 20 checksums, 234 displayed rows | `python -m scripts.validate --data data/latest.json --site .` |
| Independent audit tests | 9 OK | `python -m unittest discover -s audits -p 'test_*.py'` |
| Integrity tests | 5 OK | `python verification-95b588c2/test_integrity.py` |
| c6 tests | 12 OK | `python -m unittest discover -s verification-c6 -p 'test_*.py'` |
| Browser suites on newly generated public build | All nine suites pass; 32 accessibility/no-overflow scans at 320/390/768/1440 plus expiry/phone tests | `python -m scripts.build --data data/latest.json`, `npm run test:browser` |
| Full unit suite on the committed root | **Not green:** 1,248 tests, eight failures, one error, one skipped | Detailed below; not falsely reported as verified |

Python dependencies were installed in `.venv` from the pinned `requirements.txt`;
Node dependencies with `npm ci --ignore-scripts`. No dependency versions changed.

## Integration blockers and coordination

1. The root `assets/style.css` differs from the repaired canonical
   `site/assets/style.css`. Six parity assertions fail; the public build generated
   from canonical passes all phone browser suites. The served-copy repair is
   already owned/delivered in [PR #250](https://github.com/buffedlizard55-lab/MaltaProj4/pull/250).
   This session does not overwrite that work or hand-edit generated outputs.
2. Fresh fixture 1083121 (`Projeto do KinGui` vs `MEIA NOITE`) has Polymarket
   outcomes `Tropa do KinGui` / `MEIA NOITE`. Its retained evidence carries the
   sourced identity mapping, and the production-independent c6 auditor reproduces
   its probability. The older independent verifier `verify_0cc1138a.py` ignores
   `identity_sources`, causing two assertion failures plus a `None.index` error.
   Posted the exact reproduction and requested a strict source-backed alias
   repair in the owner's [PR comment](https://github.com/buffedlizard55-lab/MaltaProj4/pull/250#issuecomment-6380919960).
   No alias was guessed and no failing assertion was disabled.
3. GitHub Pages remains configured as legacy `main:/`; its API reported the
   `dce494b` build in progress, not a confirmed live deployment. A successful local
   build or a queued workflow is not evidence of a successful public deploy.
   The new `delivery-928d7320.yml` runner records the actual live byte check.

Do not merge a broken site merely to close this audit. These integration blockers
must be repaired/verified by the publishing owners or the final integration
session before claiming delivery. Existing source/access/model limitations remain
visible on the site's Unresolved and Flagged for Review routes.

## Official source check within allowed egress

Re-read Valve's pinned `model/fit.js` through GitHub's Contents API at commit
`eec4853d7bcf0f1f7efe7f0d901234bef7e98b75`; its default Glicko rating deviation is
**75** (line 15), matching the model/auditor constant. This check does not certify
future predictive accuracy or convert a model estimate into a bookmaker price.

- [Valve formula / fit implementation](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/fit.js)
- [Valve published calibration graphic](https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/modelfit.png)
- [Hotspawn lobby](https://play.hotspawn.com/lobby)
- [Hotspawn CS2 inventory](https://play.hotspawn.com/cs2-pickems)

Individual market/HLTV/Valve standings links are attached to every row in the
ledger rather than replaced by generic home-page citations.

## PR and final observed delivery state (06:35 UTC)

[PR #253](https://github.com/buffedlizard55-lab/MaltaProj4/pull/253) is open, not
merged over a failing site gate. [Live-byte audit 40070479588](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40070479588)
and [PR gate 40070562554](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40070562554)
are queued, without an allocated runner. The Pages API now reports `built` for
`dce494b`, but [dynamic run 40069996301](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/40069996301)
still has queued deploy/report jobs. Live deployment and exact bytes are therefore
**not confirmed**. No claim that these audit changes are already on the public site.
