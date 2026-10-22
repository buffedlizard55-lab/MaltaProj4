# Session 5f1df842 — workbook, coverage limits, and the 22 October line audit

**Scope of this session**: make the published board complete and honest about what it cannot price.
Everything below is either something I read myself on the source (URL given) or a hash of a document
this repository captured. Nothing here is inferred, and no percentage is invented.

Snapshot under audit: `research/session-5f1df842/harvest/latest.json` (verified read, 97 fixtures,
35 open, 28 priced, 7 research-only, **0 open rows without a pick**). The live board published at
2026-10-22T01:54Z moved `1082769` to a bookmaker line, so it now reports 29 priced and 6 research-only;
the seven-row audit below is unchanged, row by row.

---

## 1. Automated market research is refused at EGamersWorld

I wrote `scripts/probe_5f1df842.py` to look for two-way lines on EGW's own listing pages, politely
(1 request/second, honest user agent `Hotspawn-CS2-Research/1.0`, one HTTP read per URL, every body
hashed). It runs as a `continue-on-error: true` step of `harvest-5f1df842.yml`, so a refusal can never
break a harvest.

| Read (workflow run 39704832864) | Result |
| --- | --- |
| `https://egamersworld.com/counterstrike/matches` | **HTTP 403**, 5,651 B body, sha256 `8b1a19b7…` |
| `https://egamersworld.com/counterstrike/matches?page=2` | **HTTP 403**, 5,708 B body, sha256 `155fe4a3…` |
| `https://egamersworld.com/counterstrike/matches?page=3` | **HTTP 403**, 5,708 B body, sha256 `d3cb98bd…` |

`listing_matches_seen: 0`, `candidates: 0`. **Conclusion: EGW's listing cannot be harvested from
GitHub's runners.** The probe stays in the workflow as an evidence recorder, not as a data source, and
it is documented as such in the code. Manual research through a rendering fetcher still works, which
is how the audit below was done.

---

## 2. The 22 October line audit — all seven research-only rows

Method per row: open the fixture's own EGW page, read the odds strip exactly as published, and
compare it with the line the row already refuses. EGW publishes genuine two-ways for some fixtures
(for example Vitalem Aerem **2.59** / Rare Atom **1.47** on the same listing), so a uniform pair is a
placeholder, not a coin flip — and a placeholder never becomes a probability on this site.

| Fixture | Pair, start (UTC) | EGW page read | Verdict |
| --- | --- | --- | --- |
| `1081869` | Morningstar / NEXVOID, 2026-10-22T03:00Z, Bo3 | [EJcHRdr5Vx/morningstar-vs-nexvoid-e_MT2tamL](https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/morningstar-vs-nexvoid-e_MT2tamL) — `1.8 / Make a bet / 1.8`, no bookmaker named, no update time | Placeholder → **no line**; research-only pick stands |
| `1081597` | benched gods / TitanFlow, 2026-10-22T11:00Z, Bo3 | [rW6Ymkl0D/benched-gods-vs-titanflow](https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn) — `1.8 / 1.8` | Placeholder → **no line** |
| `1082769` | K27 / NEXORA, 2026-10-22T17:30Z, Bo3 | [4yp_dlKtNl/nexora-vs-k27](https://egamersworld.com/counterstrike/match/4yp_dlKtNl/nexora-vs-k27-U_TH-dVYT) — **8.1 / 1.021**, with EGW's own tip text calling K27 the bookmakers' favourite at 1.021 and NEXORA about 8.1 at 13:30 site time (= 17:30Z) | **Genuine asymmetric line** → priced by the refresh as `bookmaker_fallback` |
| `1079654` | ex-Zero Tenacity / ex-RUSTEC, 2026-10-23T08:00Z, Bo3 | [_rW8GEyWK/ex-zero-tenacity-vs-ex-rustec](https://egamersworld.com/counterstrike/match/_rW8GEyWK/ex-zero-tenacity-vs-ex-rustec-YieSsHTBr) — `1.8 / 1.8`, both rosters 5/5 | Placeholder → **no line** |
| `1081149` | FORZE Reload / **LFO 10**, 2026-10-23T14:00Z, Bo3 | [HiXMAaC8L/forze-reload-vs-_04jKZ07_4](https://egamersworld.com/counterstrike/match/HiXMAaC8L/forze-reload-vs-_04jKZ07_4) — opponent field is **blank** (`un` flag, no name, no logo), `1.8 / 1.8` | Placeholder → **no line**; identity resolved below |
| `1081150` | ex-RUSTEC / Saint Sinners, 2026-10-23T17:00Z, Bo3 | [HiXMAaC8L/ex-rustec-vs-saint-sinners](https://egamersworld.com/counterstrike/match/HiXMAaC8L/ex-rustec-vs-saint-sinners-qRkeIZuchq) — `1.8 / 1.8` | Placeholder → **no line** |
| `1082860` | FlyQuest / Staqued, 2026-10-27T03:00Z, Bo3 | [DFRAG26/flyquest-vs-staqued](https://egamersworld.com/counterstrike/match/DFRAG26/flyquest-vs-staqued) — `1.8 / 1.8` six days out | Placeholder → **no line** |

### One correction to my own hand search, and why it matters

My first pass could not find an EGW page for `1082769` (an EGW search for `K27` returns the site
homepage rather than a result list, and I will not guess a slug). The refresh did find it, at
`4yp_dlKtNl/nexora-vs-k27-U_TH-dVYT`, and it publishes a **real** two-way — `8.1 / 1.021`, with EGW's
own tip text naming K27 the bookmakers' favourite at 1.021 — so that row is now a `bookmaker_fallback`
line (K27 88.8%, de-vigged) rather than a research pick. I re-read the page myself to confirm the
numbers before recording this.

That contrast is exactly why the placeholder rule exists and how it is applied: `1.8 / 1.8` on both
sides, with no bookmaker and no update time, is refused; an asymmetric pair bound to both team labels
(`8.1` / `1.021`, or `2.59` / `1.47` on the listing) is accepted as a listed price. The state after the
01:54Z publication is therefore **35 open, 29 priced, 6 research-only, 0 without a pick**, and the six
remaining rows are exactly the five EGW placeholders plus `1082860`, whose page also serves `1.8 / 1.8`.

### The blank Series #12 opponent is LFO 10 — resolved, not guessed

EGW's CCT Europe 2026 Series #12 bracket lists
[FORZE Reload vs ⟨blank⟩](https://egamersworld.com/counterstrike/event/cct-europe-2026-series-12-HiXMAaC8L)
at 23.10.26 10:00 site time. Three facts tie that row to fixture `1081149`:

1. the slot is identical — 23.10.26 10:00 site-local = **2026-10-23T14:00Z**, the Hotspawn start;
2. the same bracket lists ex-RUSTEC vs Saint Sinners at 13:00 site time, which matches fixture
   `1081150` at 17:00Z, so the bracket's clock and Hotspawn's clock agree across the event;
3. the blank page's five players — `dan1`, `Sapec`, `Mann3n`, `dottie`, `L00m1` — are **exactly** the
   five HLTV publishes for LFO 10 in
   [HLTV 2399499](https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12)
   (5/5 roster match).

So EGW's missing name is a rendering gap on their side, not a different fixture. The row keeps its
Hotspawn labels ("FORZE Reload" / "LFO 10") and gains no probability from this.

### Why these seven carry a pick but no percentage

The documented ladder (`sources.html#method`) stops short of a number whenever the only surviving
evidence is one-sided: a research-only pick means "this side is ahead on official standings and that is
all we can source", never a modelled or eyeballed probability. Rows `1081597` (`#157`, 811 pts, one
sided), `1081869`, `1082769`, `1081149` and `1082860` are one-sided signals; `1079654` and `1081150`
are ranking-order signals on both sides (HLTV #67 vs #70 and #70 vs #123). No book, exchange or HLTV
numeric line exists for any of the seven as of 2026-10-22T01:2xZ.

---

## 3. The harvest regression, and the fix that keeps a slot from being lost

Run `39704142204` (01:11Z) returned a **verified** 97-fixture inventory. Run `39704832864`, seven
minutes later, came back with:

- the fixtures API answering **200 with a non-JSON body** (12,110 B, sha256 `3c4d3141…`), and
- both Hotspawn pages missing their `ng-state` hydration block ("Hotspawn hydration data missing;
  cannot claim empty lobby"),

so `scripts.inventory.discover` retained the 21:27Z inventory (75 fixtures, `coverage: stale`) and the
committed snapshot went **backwards** from verified to stale. Retaining the last good list is the correct
fail-closed behaviour, but silently publishing an older board is not what "fresh every 4–8 hours" means.

Two bounded retries now turn that transient into a successful read instead of a stale board:

| Change | Where | Behaviour |
| --- | --- | --- |
| A JSON source that answers 200 with a non-JSON body is re-asked on the same URL after 5 s, then 20 s | `scripts.refresh.Sources.get` (`JSON_RETRY_WAITS`) | Same request, same URL, no bypass; three attempts then fail closed exactly as before |
| When **no** Hotspawn view is usable, the three views are re-read once after 20 s | `scripts.inventory.discover` (`DISCOVERY_RETRY_WAITS`) | Only opted in by the real reader, so stub readers and tests stay single-pass; a host that keeps refusing is still blocked |

Refusals (401/403/429) are still never retried as if the source had merely asked us to slow down, and a
persistent non-JSON body still raises. Covered by four new tests in `tests/test_session_5f1df842.py`
(`SourceRetryTests`); the whole suite is green.

The committed fallback board was also moved forward to the last **verified** read (97 fixtures,
01:15:54Z) so the repository never ships the stale 75-row list as its fallback.

---

## 4. What a reader should take from this

- Full coverage holds on this snapshot: 35 open fixtures, 28 priced, 7 research-only, **0 without a
  pick**.
- Seven rows cannot be priced from any source the project accepts. Their limitations are stated on the
  row, on `unresolved.html`, and on the Flagged for Review page — not hidden.
- EGW's uniform `1.8 / 1.8` is a placeholder. It is refused everywhere it appears, including on the
  blank-opponent row.
- Automated listing research at EGW is dead (403). Hand research through a rendering fetcher is the
  recorded path, and each row above carries the exact page that was read.
- The remaining way to convert any of the seven into a two-way line is a real book price appearing
  before the fixture's lock time; the 15-minute refresh will pick it up and replace the research pick
  automatically.
