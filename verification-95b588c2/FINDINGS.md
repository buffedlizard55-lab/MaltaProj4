# Independent acceptance audit — 95b588c2

**Audited implementation:** `01839a68829c05313b6b35e36d934dcda8cd826f` (ee1fb536 baseline selected by integrator eb962e45). Checked 2026-10-14 around 08:35–08:40 UTC. These are baseline findings, not a claim that later integration is unchanged. This session owns only `verification-95b588c2/**`. Integration fixes must be made by the owner of `scripts/**` and `site/**`.

## Reproduced irregularities requiring integration attention

| ID | Finding | Evidence / reproduction | Requested correction |
| --- | --- | --- | --- |
| V01 | Browser expiry ignores the exchange's `updated_at`; a price can outlive its eight-hour source-update TTL while retrieval time is still fresh. | Run `expiry-regression.cjs` from a built implementation root. Actual retained Legacy/PARIVISION #1080178: update 05:03:28.243504Z, observation 05:04:33.277296Z, lock 13:24Z. At simulated 13:03:29.243Z the browser still displays its probability. This is a controlled clock test, not a live 13:03 observation. [Official Polymarket discovery API](https://gamma-api.polymarket.com/sports). [Audited browser code](https://github.com/buffedlizard55-lab/MaltaProj4/blob/01839a68829c05313b6b35e36d934dcda8cd826f/site/assets/app.js). | Store/render a single expiry deadline equal to the earliest fixture TTL, price observation TTL, price-update TTL, pick lock and start; use it for both table recommendations and hero. Pinnacle cutoff should also be honored when supplied. |
| V02 | Collector's liquidity guard accepts non-finite values (`NaN`, `Infinity`). | `test_integrity.py::test_nonfinite_liquidity_rejected` fails for both values. These are **test-only mutations**, not observed official feed values. [Audited acceptance code](https://github.com/buffedlizard55-lab/MaltaProj4/blob/01839a68829c05313b6b35e36d934dcda8cd826f/scripts/core.py). | Require finite parsed liquidity, spread and raw prices before acceptance; malformed values must not pass via NaN comparisons. |
| V03 | Row validator does not bind retained raw outcome names to `source_teams`, and does not independently reapply liquidity/spread guards. | Both associated tests in `test_integrity.py` fail. A deliberately corrupted raw outcome pair or a 98-point spread/$1 liquidity still passes `validate_data`. **No actual accepted row was shown corrupted by this test.** [Audited validator](https://github.com/buffedlizard55-lab/MaltaProj4/blob/01839a68829c05313b6b35e36d934dcda8cd826f/scripts/validate.py). | Reconstruct identities from raw market outcomes / raw Pinnacle participants, and rerun every acceptance gate (including status, BO, age, spread, liquidity, cutoff, period and alignment), not only arithmetic. |
| V04 | Live source recency and Pages publication still require the integration run. | This sandbox permits GitHub/package hosts only. No fresh direct Hotspawn/HLTV/bookmaker fetch was performed by this session. Repository Pages API reported **legacy** source `main:/` at 08:33 UTC, not the proposed workflow deployment. [Pages API](https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages), [Actions](https://github.com/buffedlizard55-lab/MaltaProj4/actions). | Integrator must refresh in GitHub Actions, verify published source receipts, configure Pages, merge explicit PR number and check live routes. Do not equate passing a branch build with a deployed dashboard. |

## Verification actually performed

- Installed the pinned Python requirements and locked Node test dependencies in an isolated untracked baseline copy; did not edit another session's implementation.
- **38 baseline Python tests passed.** This is the current executable count, not the older 29-test report in its board.
- **88 retained rows compared** with the official captured Hotspawn fixture response at `research/probe/fixtures.txt`: identical ID set, team names, competition, tier, best-of and source status. Source response SHA-256: `7e87b3036211e44c1a21a4fed0d21eb4f4f6c0125117d5ef161fa0a1af20a97d`. This capture is historical evidence, not a fresh current inventory claim. [Exact public fixture query](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1).
- Baseline validator reproduced **18** initial-snapshot calculations. Building later at audit time correctly withheld three passed-lock picks, producing **15 priced / 10 unresolved / 63 not-open** of 88 rows. These counts are time-specific.
- Generated **8 pages**, checked **424** internal links/assets with the baseline validator.
- Ran browser verification: **21 page/viewport accessibility scans**, 390/768/1440px layouts, subpath URLs, navigation, filters, evidence anchors and existing broad expiry test all passed. No WCAG A/AA violations found by the automated tool; this is not certification on every device.
- Added independent tests which expose V01–V03 rather than hiding them behind expected-failure flags. The original broad expiry test advances to 2099; it does not detect differing update/observation TTL boundaries.

## Coverage/source limitations to retain on the public review page

The baseline correctly keeps all feed rows and leaves unsupported probability values blank. It does **not** provide a supported pick for every match. It must not advertise 100% probability coverage.

- [Hotspawn CS2 lobby](https://play.hotspawn.com/cs2-pickems): membership/lock timestamps only; crowd percentages are excluded from probabilities.
- [HLTV matches](https://www.hltv.org/matches): useful specialist context. Fan votes and rank ordinals are not calibrated win probabilities.
- [Polymarket](https://gamma-api.polymarket.com/sports): two-sided exchange evidence is distinct from a bookmaker consensus; source update does not prove recent trade.
- [Pinnacle official lines](https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight): a functioning fallback in retained evidence; update timestamp missing, single-book estimate explicitly flagged.
- [Thunderpick](https://thunderpick.io/esports/cs2-betting) and [GG.BET](https://gg.bet/en/esports/counter-strike): baseline includes access checks, **not verified line adapters**. HTTP success must not be called successful odds retrieval.
- Exact matching deliberately rejects unconfirmed aliases, academy/main-roster substitution and conflicting opponents. Additional independently verified aliases or a genuinely calibrated model could improve coverage; neither should be invented merely to fill cells.

## How to reproduce

From the implementation root after `pip install -r requirements.txt`, `npm ci --ignore-scripts` and `python -m scripts.build`:

```sh
python /path/to/verification-95b588c2/test_integrity.py
node /path/to/verification-95b588c2/expiry-regression.cjs
```

The baseline failures are intentional evidence of missing guards; a corrected implementation should pass. The browser regression needs a priced retained row with a source-update TTL earlier than its observation/fixture TTL and lock. If the data has already aged out, rebuild a test copy at its actual capture time rather than manufacturing a fresh production timestamp.
