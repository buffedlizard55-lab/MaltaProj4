# Session `2c7b9e48` — coverage for every match, phone-first picks, line-by-line verification

**Branch:** `arena/2c7b9e48-maltaproj4` · **Base:** `main` @ `be8176886157a2c0dc58b9b2437df1756231e358`
**Snapshot audited:** `data/latest.json`, generated `2026-10-23T08:32:56.593552Z`, fixtures observed
`2026-10-23T08:29:19.125787Z`, 92 rows.
**Audit artifacts:** [`AUDIT.md`](AUDIT.md) · [`audit-subset.json`](audit-subset.json) ·
[`valve-verification.json`](valve-verification.json)

This report separates three things on purpose:

1. what was **verified against an official source** in this session (with the source link),
2. what was **verified only from the repository's own stored receipts**, because the source is
   unreachable from this sandbox,
3. what remains **unverified or irregular** and is published on the *Flagged for Review* page.

Nothing below is inferred. Where a check could not be made, it says so.

---

## 1. What was asked, and where it is answered

| Request | Where it is satisfied | How it is checked |
| --- | --- | --- |
| A pick for **every** match, including low-tier CS2 and matches no betting site lists | `scripts/refresh.py` publication ladder (exchange → HLTV → Pinnacle → wide exchange → book listing → Valve VRS model → HLTV ranking research → one-sided Valve tier). New in this session: the executive summary's **`#every-match`** panel, which accounts for every feed entry and states what is published for each group | `verification-2c7b9e48/audit_board.py` fails an open row that has neither a pick, a priced probability, nor a documented limitation with its attempted sources; `tests/test_session_2c7b9e48.py` re-runs that rule on the committed board |
| Try **HLTV first**, then esportsbooks / betting lines | The ladder's stored `attempts` per row (HLTV match page, then Polymarket/Pinnacle, then Thunderpick/GG.BET/EGamersWorld) | The auditor requires every unresolved row to list each attempt with an official URL and a status; counts are in §3 |
| A **separate section** for anything unresolved, with its limitations, **inside the executive summary** | `#unresolved-picks` (already present) and the new `#every-match` panel, both in `index.html`; the full queue is `unresolved.html` | `audit_board.py` checks that a fixture without a pick appears in `unresolved.html` **and** in the executive summary, and that its reason and attempts are published |
| Executive summary that **links to where the updated picks are** | `#exec-banner`, `.exec-summary-links`, `#picks-quick`, footer and phone tab bar all link `picks.html`, `unresolved.html`, `matches.html`, `#picks-at-a-glance`, `#every-match` | `audit_board.py` (`site.summary_link`, `site.summary_section`) and `tests/browser_2c7b9e48.cjs` |
| **Mobile-readable**: find the picks easily on a phone | New `#picks-quick` strip at the top of `picks.html`: the next picks with their percentage, each one tap from its evidence, above the fold at 320×568 and 390×844 | `tests/browser_2c7b9e48.cjs` asserts from rendered text that a pick **and its percentage** are inside the first screen at both widths, that the strip agrees with the board row, and that no page overflows sideways |
| 4–8 hour refresh of the Hotspawn list | `.github/workflows/pages.yml` runs four slots an hour (`:04 :19 :34 :49`) plus a watchdog; the executive summary prints the cadence | Run history via `gh run list` (§5) |
| **No Hotspawn percentages** | No probability provider may be Hotspawn | `audit_board.py` rule `row.provider_hotspawn`, plus the repository's `86b56cf6` auditor |
| **Line-by-line verification, sources, no invention** | §2 and §4 | `audit_board.py` (**2,696 checks, 0 errors, 0 warnings** on this snapshot) |

---

## 2. Verified against an official source in this session

### 2.1 Valve's own standings file (the input to 7 of the 30 published probabilities)

`verification-2c7b9e48/verify_valve.py` downloads the **exact pinned file** through the GitHub
contents API and re-derives each percentage from the file's own points:

* file: `standings_global_2026_10_05.md` at commit `eec4853d7bcf0f1f7efe7f0d901234bef7e98b75`
  (`github.com/ValveSoftware/counter-strike_regional_standings`) — header line
  *“Standings as of 2026_10_05”* confirmed in the retrieved bytes;
* constants from Valve's code at the same commit: `model/fit.js` line 15 `rd : 75`
  (`defaultGlickoParams`) and `model/glicko.js` line 4 `const Q = Math.log(10) / 400`;
* `priorWinExpectation` in `fit.js` (lines 109-128) computes `1 - winΔ/(winΔ+lossΔ)`; because the
  single-match rating delta uses one fixed RD and one K factor for both outcomes, this reduces
  exactly to the Glicko expected score the repository implements. **Re-derived, not copied.**

Result: **7 of 7 model rows verified, 0 failures.** Each row's recorded standing, points and roster
that appears in Valve's file was confirmed, and the published probability was reproduced from the
file's points to within 1e-9:

| Fixture | Teams (Valve points from the file) | Published | Reproduced |
| --- | --- | --- | --- |
| 1081605 | Phantom Academy 783 / Banda Chuya 801 | 47.99% / 52.01% | ✓ |
| 1082996 | Acend 1197 / UNiTY 1167 | 53.35% / 46.65% | ✓ |
| 1079198 | Metizport 1290 / BakS 1044 | 73.85% / 26.15% | ✓ |
| 1079200 | Color 1249 / ex-Zero Tenacity 1066 | 68.84% / 31.16% | ✓ |
| 1082861 | Rooster 718 / Abyssal 734 | 48.21% / 51.79% | ✓ |
| 1082792 | HOTU 1437 / The Huns 944 | 85.18% / 14.82% | ✓ |
| 1082793 | 5star 1110 / 1win 1383 | 24.30% / 75.70% | ✓ |

Two of those labels appear **twice** in Valve's file, and the verifier reproduces the project's
documented rule rather than guessing:

* `Banda Chuya` — #165 / 801 pts (*AdrieN, ezox, maaryy, Showk, tomiko*) and #373 / 402 pts
  (*ezox, manio*). The fixture's HLTV lineup matches the first at 5/5, so #165 is the correct row.
* `The Huns` — #122 / 944 pts (*Annihilation, Bart4k, bexyz, controlez, Cozen*) and #213 / 701 pts
  (*Bart4k, controlez, nin9, sk0R, xerolte*). The lineup matches the first at 5/5.

A naive label lookup returns the wrong row and produces a wrong probability; the auditor's first
run did exactly that and was corrected to follow the roster rule. `tests/test_session_2c7b9e48.py`
now locks the rule in (four refusal cases: absent label, ambiguous label, duplicate label, and a
correctly selected duplicate).

### 2.2 Every market probability replays from the raw price stored with it

`audit_board.py` recomputes all 30 published pairs from the raw fields inside each row
(`outcomePrices` for Polymarket, decimal `odds` for book listings, Valve `points` for the model),
maps the quote's own team labels onto the fixture's teams, and requires the stored value to match:

* 23 market/model rows with a two-sided quote → **exact match, sides in the fixture's order**;
* every pair sums to 1.0 within 1e-9; fair odds equal `1/p`;
* the pick is the higher-probability side on every priced row;
* no row's provider is Hotspawn;
* no two fixtures share one market id; every quote's start equals its fixture start within 60s.

### 2.3 The published bytes, the manifest and the internal links

* `build-info.json` lists 20 files; **all 20 SHA-256 digests match the files on disk** after the
  rebuild (`scripts.stage_legacy` refuses to copy a tree that does not match).
* `scripts.validate`: 92 rows, 15 pages, **832 internal links/assets and anchors resolve**, 20
  artifact checksums verified, 224 displayed match rows verified, 0 failures.
* `verification-c6/audit_snapshot.py`: **0 failures**. `verification-95b588c2/test_integrity.py`:
  5/5 OK. `verification-86b56cf6/audit_repo_86b56cf6.py`: 0 errors.
* Live deployment read at the start of the session (`buffedlizard55-lab.github.io/MaltaProj4`):
  `build-info.json` served revision `4716f970…`, built `2026-10-23T08:32:56.949905Z`, 92 rows — the
  same snapshot audited here, so this audit describes what is actually published.

---

## 3. Coverage accounting for this snapshot (from the data, not from prose)

| Group | Rows | What the site publishes |
| --- | --- | --- |
| Open, priced | **30** | pick + both probabilities + fair line + method + source |
| Open, research-only pick (no percentage) | **0** | — (the tier exists and is exercised by tests) |
| Open, unresolved | **0** | — (the section exists and is exercised by tests) |
| Feed entries already started or locked | **62** | blank by rule, with source, timestamps and reason |

How the 30 were obtained, from the stored `attempts`:

| Attempt | Rows | Outcome |
| --- | --- | --- |
| Polymarket exchange | 21 resolved / 40 attempts | strict gate or labelled wide tier |
| Valve VRS model line | 7 resolved | Valve's official standings, roster-verified |
| Bookmaker listing research (EGamersWorld) | 2 resolved | dated two-way prices, de-vigged |
| HLTV match page | 10 attempted, 0 numeric lines | HLTV exposes rankings/lineups to this collector, not a two-sided number; fan votes refused |
| Pinnacle moneyline | 10 attempted, 0 matches | no exact team pair + UTC start in the retrieved feed |
| Thunderpick | 9 attempted, 0 quotes | page reachable, no validated two-sided series quote extracted |
| GG.BET | 9 attempted, 0 quotes | HTTP 403 persisted through three rate-limit waits |
| EGamersWorld re-check (gap watcher) | 8 attempted, 0 quotes | HTTP 403 on re-read |

**The 62 blank rows are not a coverage failure.** 58 of them are Hotspawn entries dated June–July
2026 that the feed still returns with `status: scheduled`; **50 of the 62 carry Hotspawn's own
`end_time`**, which is how this site knows they were played rather than postponed. Publishing a pick
for a match that finished four months ago would be hindsight, so the row stays blank and keeps its
source, its two timestamps and the reason. This is now stated in the executive summary panel with
the live count computed from the snapshot.

---

## 4. What could **not** be verified here, and why that is stated rather than papered over

This sandbox has outbound network access to `github.com`, `api.github.com`,
`codeload.github.com`, `registry.npmjs.org` and PyPI **only**. Measured in this session:

| Host | Result |
| --- | --- |
| `play.hotspawn.com`, `hltv.org`, `egamersworld.com`, the Hotspawn feed API | connection failed (no route) |
| `gamma-api.polymarket.com`, `guest.api.arcadia.pinnacle.com` | connection failed (no route) |
| `api.github.com`, `github.com`, `buffedlizard55-lab.github.io` (via page reader) | reachable |

Consequences, stated plainly:

* **No new price was collected in this session.** Every market line audited here was captured by the
  scheduled GitHub Actions runner and is stored with its raw response, id, observation time and
  source URL. The live refresh on merge runs in an environment that *can* reach those hosts; this
  sandbox cannot and does not claim to.
* **HLTV and Polymarket raw responses could not be re-fetched.** Their numbers are therefore
  verified by replay from the stored raw fields (§2.2) and by the independent auditors, not by a
  fresh read against the provider.
* **`model_vrs_mirror` (HLTV's copy of Valve's ranking)** has no rows in this snapshot; the verifier
  would skip them rather than assume they are right.
* **Valve's calibration slope (0.7986)** is published in `modelfit.png`, an image in Valve's
  repository. The formula and RD are verified from code; the slope cannot be machine-read from an
  image, so it remains a cited constant. Every model row states it and links the image.

---

## 5. Repository review — findings and irregularities (flagged, non-blocking)

1. **The published board is fresher than the committed fallback can be.** The scheduled pipeline
   rebuilt the site at 08:32Z; the committed root copy is only replaced when step 15 of
   `pages.yml` succeeds, and that step has failed in bursts before (recorded in `COORDINATION.md`
   for sessions `d4c74d77`/`fe7f5de4`). The mitigation is in place (guarded, retried root publish
   plus a stale banner), but a burst of pushes can still leave the root one snapshot behind. Not
   fixed here: it is a workflow-owned file and a known, documented trade-off.
2. **62 stale “scheduled” feed entries** from June/July 2026. They are displayed with the reason and
   counted on `review.html` via `data/latest.json` → `issues[]`. Treated as a Hotspawn feed artifact,
   not as upcoming matches.
3. **Empty `best_of` on several fixtures** (`null` in Hotspawn's response). The site prints
   “unverified / not supplied” instead of assuming Bo1/Bo3.
4. **HLTV/Pinnacle/Thunderpick/GG.BET access limits** are recorded per row and on `sources.html`.
   No access control is bypassed.
5. **One wide, low-confidence market line is published** (`Ground Zero vs Off Chops`, spread beyond
   the strict ceiling, `exchange_wide`). It is labelled in the method column and on the row; it is a
   coverage decision, and the strict rejection is retained in the evidence ledger.
6. **The pick lock is 6 minutes before start** on this feed (`lock_offset_sec: 360`). A refresh
   landing inside that window withholds the pick rather than showing a late one.

All six are visible to a reader of the site; none of them is silently filled in.

---

## 6. Changes made in this session

| File | Change | Why |
| --- | --- | --- |
| `verification-2c7b9e48/audit_board.py` (new) | zero-collector auditor: 2,696 checks over rows, arithmetic, side mapping, providers, internal links and the built pages | the request “every match must have a pick” needs a rule that fails when it is not true |
| `verification-2c7b9e48/verify_valve.py` (new) | re-derives every VRS percentage from Valve's own file at the cited commit | the only probability input that this sandbox can verify at source |
| `tests/test_session_2c7b9e48.py` (new) | 32 tests: real-board acceptance, 12 corruptions that must be refused, label/roster mapping, arithmetic, Valve duplicate-label rule | a gate that cannot fail is not a gate |
| `tests/browser_2c7b9e48.cjs` (new, wired into `npm run test:browser`) | first-screen pick + percentage at 320×568 and 390×844, strip/board agreement, reachable filters, every-match panel totals | the phone requirement, measured rather than asserted |
| `scripts/build.py` | `picks_quick()` strip on `picks.html`; `every_match()` panel in the executive summary; table anchor id; filter-bar id | pick visible on the first phone screen; every feed entry accounted for |
| `site/assets/style.css`, `assets/style.css` (kept byte-identical) | phone ordering for the board, card layout for the every-match panel | no sideways scrolling, nothing overlapping |
| `package.json` | `test:browser` runs the new suite | CI runs it |

Rebuilt root fallback (`index.html`, `picks.html`, `unresolved.html`, `matches.html`,
`review.html`, `analysis.html`, `sources.html`, `evidence.html`, `404.html`, `data/*`,
`build-info.json`) so the committed root and the artifact are the same bytes.
