# The freshness anchor: a cached HTML copy was expiring every pick on the board early

Session `3c8d1136`, written 2026-10-16 (UTC). Every number below comes from a receipt in
this repository or from a linked primary source; nothing is copied from another session's
conclusion without saying so.

## 1. The defect, stated precisely

Three pieces of code decide how long a published pick stays usable:

1. [`scripts/refresh.py`](../../scripts/refresh.py) · `Sources.get` — `observed_at = retrieved_at − Age`,
   where `Age` is the HTTP cache-age header of the response actually received.
2. [`scripts/inventory.py`](../../scripts/inventory.py) · `discover` — `'observed_at': min(observations, key=dt)`,
   i.e. the **oldest** of the three Hotspawn views anchors the whole board
   (`fixtures_observed_at`).
3. [`scripts/core.py`](../../scripts/core.py) · `pick_deadline` — the single recommendation
   deadline is `min(fixture_observed_at + 8 h, quote observed_at + 8 h, quote updated_at + 8 h,
   Pinnacle cutoff, fixture lock, fixture start)`.

Hotspawn serves its two public HTML lobby views through a CDN, and the fixtures API does
not. On the production refresh of **2026-10-16T07:21:05Z** (main `693b637`, the build
published at <https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json>):

| Official view | HTTP | Retrieved (UTC) | `Age` (s) | Observed (UTC) | CS2 fixtures |
|---|---|---|---|---|---|
| [fixtures API](https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1) | 200 | 07:21:05.706130 | not supplied | 07:21:05.706130 | 103 |
| [CS2 lobby page](https://play.hotspawn.com/cs2-pickems) | 200 | 07:21:06.341148 | **14241** | 03:23:45.341148 | 95 |
| [general lobby](https://play.hotspawn.com/lobby) | 200 | 07:21:06.528544 | **6251** | 05:36:55.528544 | 95 |

So the board was anchored at **03:23:45Z** and every open pick carried
`expires_at 2026-10-16T11:23:45.341148Z` — **2 h 30 m before the TWC Group A decider
(Aurora vs 9z, 14:00Z)** and **5 h 30 m before the Group B decider (BetBoom vs Legacy,
17:00Z)**. A reader who opened the site at 12:00Z saw the "picks are withheld" state for
both deciders even though the underlying market lines were minutes old and the fixtures
had not started. Coverage was simultaneously reported as `partial` (103 / 95 / 95), which
is a true statement about the three responses but a misleading one about the board: the
fresh API and the fresh page already agreed, and only the cached general lobby differed.

**It is still live at the time of writing.** The board published at
`2026-10-16T08:21:00Z` (revision `41ff936f`, the merge of PR #38, read from
<https://buffedlizard55-lab.github.io/MaltaProj4/data/latest.json>) reports
`fixtures_observed_at: 2026-10-16T05:36:54.850797Z` and `coverage: partial`, because the
general lobby answered `Age 9828` (observed 05:36:54Z) and the CS2 page `Age 3192`
(observed 07:27:30Z) while the API was fresh. Applying the production deadline function to
that published anchor, both deciders on the live board expire at **13:36:54Z** — 17 minutes
before Aurora vs 9z's own 13:54Z lock, and more than three hours before BetBoom vs Legacy's
16:54Z lock. That is the same mechanism as the 07:21Z build above, which is why the numbers
are arithmetic on published inputs rather than a new inference: at 07:21Z the identical
anchor+8 h rule produced `expires_at 11:23:45.341148Z` on every later row.

## 2. The measurement

[`scripts/cdn_probe_3c8d1136.py`](../../scripts/cdn_probe_3c8d1136.py) requests each of
the three public views three times — once plain and twice with a distinct `_cb` query
argument — and records the response headers, byte length, SHA-256 and parsed CS2 fixture
ID set. Receipt: [`research/harvest-3c8d1136/cdn-probe.json`](../harvest-3c8d1136/cdn-probe.json)
from Actions run [38869016384](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38869016384),
`probed_at 2026-10-16T07:44:06Z`:

| View | Plain `Age` | Plain CS2 IDs | `_cb` `Age` | `_cb` `X-Cache` | `_cb` CS2 IDs |
|---|---|---|---|---|---|
| fixtures API | not supplied | 103 | **HTTP 400** (`_cb` rejected) | – | – |
| `/cs2-pickems` | 973 s | 103 | **0** | **MISS** | **103** |
| `/lobby` | 7620 s | **95** | **0** | **MISS** | **103** |

Read together with the earlier session `ab18fe2a` receipt
[`research/day3-ab18fe2a/receipts/hotspawn-fixture-1081775.json`](../day3-ab18fe2a/receipts/hotspawn-fixture-1081775.json),
which independently recorded that this API rejects an unknown query argument with HTTP 400
("property _ should not exist"), the picture is complete:

* the fixtures API is always fresh and must **not** be cache-busted;
* both HTML views can be hours stale, and one distinct query argument returns a current
  copy (`Age: 0`, `X-Cache: MISS`) with the **same 103 fixtures the API returned in the
  same minute**.

## 3. The fix

Contained in [`scripts/refresh.py`](../../scripts/refresh.py) only:

* `CACHE_BUST_HTML_HOSTS = ('play.hotspawn.com',)` and `CACHE_BUST_ARGUMENT = '_cb'`;
  `Sources.bustable()` returns true only for an HTML (non-JSON) request to those hosts, so
  the fixtures API, Polymarket, Pinnacle, HLTV and Valve are fetched exactly as before.
* Attempt 0 uses the cache-busted URL; the existing retry falls back to the canonical URL,
  so a source that rejects the argument degrades to the previous behaviour instead of
  failing the refresh.
* The receipt keeps `url` canonical (that is the link published as evidence) and adds
  `request_url`, the `cache_bust` token and `cache_status` (`X-Cache` / `CF-Cache-Status`).
* No probability, pick, tier, gate, TTL or identity rule is touched. `pick_deadline` and
  `scripts/core.py` are unchanged (that file is claimed by session `2e920ea8`).

## 4. Before and after, on live refreshes

Both runs are this session's own non-publishing harvest workflow on branch
`arena/3c8d1136-maltaproj4`; each ran the real, unmodified `scripts.refresh`.

| | run [38869016384](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38869016384) (before) | run [38869616511](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38869616511) (after) | run [38871406232](https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/38871406232) (after, 17 min later) |
|---|---|---|---|
| refresh `generated_at` | 07:44:25Z | 07:50:16Z | 08:06:48Z |
| Hotspawn `Age` (api / page / lobby) | – / 996 / 7632 | – / **0** / **0** | – / **0** / **0** |
| `fixtures_observed_at` | **05:36:55Z** | **07:49:57Z** | **08:06:33Z** |
| `coverage` | partial | **verified** | **verified** |
| `coverage_counts` | api 103 / page 103 / lobby 95 / retained 106 | **103 / 103 / 103 / 103** | **102 / 102 / 102 / 102** |
| `coverage_difference` issue | raised | **gone** | **gone** |
| open rows / with a pick | 42 / 42 | 42 / 42 | 39 / 39 |

Effect on the two fixtures the user asked about (deadlines recomputed with the
production function `scripts.core.pick_deadline`, not by hand):

| Fixture | Start (UTC) | Deadline before the fix | Deadline after the fix | Gain |
|---|---|---|---|---|
| [Aurora vs 9z](https://www.hltv.org/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026) (Hotspawn 1080205) | 14:00 | 11:23:45Z | **13:54:00Z** (its own lock) | +150 min |
| [BetBoom vs Legacy](https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026) (Hotspawn 1081775) | 17:00 | 11:23:45Z | **15:49:10Z** (quote TTL) | +265 min |

Across all 42 open rows of the 07:44Z/07:49Z pair the median gain is **257.5 minutes**
and the maximum **266.2 minutes**; no row's deadline moved earlier. After the fix the
binding constraint is what it should be — the fixture's own Hotspawn lock, the market
quote's eight-hour TTL or the bookmaker cutoff — not a CDN's cache.

The 08:06Z run also shows the fix helping coverage in the other direction: three fixtures
that only the *cached* general lobby still carried (`1079626`, `1079628`, `1080204` — all
already played on 15–16 October) dropped out, so `removed_ids` in
[`research/harvest-3c8d1136/latest.json`](../harvest-3c8d1136/latest.json) lists exactly
those three and nothing else. A newly listed fixture (the way BetBoom vs Legacy appeared at
04:22Z on 16 October) is now seen in the same refresh instead of up to four hours later.

## 5. Verification

* 25 independent tests in [`verification-3c8d1136/test_source_freshness.py`](../../verification-3c8d1136/test_source_freshness.py)
  cover: the query argument preserving the public URL's own parameters; only HTML views on
  the measured host being busted; the canonical URL staying the published evidence link;
  the retry falling back to the plain URL when a source answers HTTP 400; and the probe
  never reporting a successful bust or an ID parity it did not measure.
* All 149 pre-existing tests in `tests/`, the 9 in `audits/`, `verification-95b588c2/test_integrity.py`
  and the 12 in `verification-c6` still pass, and `python -m scripts.validate --data
  data/latest.json --site .` is green (635 internal links, 283 displayed rows, 20 artifact
  checksums). No existing test file was edited.
* `research/harvest-3c8d1136/row-audit.md` — the independent row auditor
  (`verification-c6/audit_snapshot.py`) ran against the post-fix snapshot in CI.

## 6. Limits, honestly

* The fix makes each refresh force two CDN misses (two origin renders, ~537 KB and ~1 s
  each, measured). At the hourly cadence that is two extra origin requests an hour on a
  public page; it is not a load test and it is not a bypass — the same public URL is
  requested, with an argument the site accepts.
* If Hotspawn later rejects `_cb` on the HTML views, the retry restores the previous
  behaviour and the receipt records the fallback; the refresh does not fail.
* This does **not** fix the scheduler. Measured while writing this: `pages.yml` has three
  scheduled runs in the repository's whole history (2026-10-15T16:59:51Z success,
  2026-10-15T21:22:25Z failure, 2026-10-16T04:33:39Z failure) and none for the 05:17,
  06:17 or 07:17 UTC slots; `refresh-watchdog.yml` has **zero** runs. Publication
  reliability is session `ef0969b9`'s claimed lane and is logged as a request below rather
  than edited here. What this fix guarantees is narrower and real: when a refresh does run,
  its eight-hour evidence window starts at the time the data was actually observed.
