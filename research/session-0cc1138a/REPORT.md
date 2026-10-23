# Session `0cc1138a` — coverage, pick resolution, and phone access

Branch `arena/0cc1138a-maltaproj4` (this session) · work completed 2026-10-23, 09:40–11:00Z

This session was asked for four things: picks for **every** match (not only the
ones a featured market covers), a research answer for the matches that cannot be
resolved the same way as the featured picks, a **separate section** for the
unresolved ones with the limitations for generating a pick, and an executive
summary whose links make the picks findable on a phone. It also had to verify the
existing board line by line against official sources, flag irregularities, and
publish without waiting for review.

What was already true when this session started (verified, not assumed): the
committed board at `2026-10-23T08:32:56.593552Z` carried **92 fixtures, 30 open,
30 picks, 30 win probabilities, 0 unresolved**. So the gap this session had to
close was not "no picks" — it was *proof* that the 30 picks are right, a phone
layout that shows **both** teams' chances, a dedicated unresolved/limitations
section that is honest about *how* the remaining rows are (and are not) priced,
and the discovery of the two fixtures the live lobby lists that the board does
not carry.

---

## 1. Line-by-line re-derivation of every published pick (independent code)

`research/session-0cc1138a/verify_0cc1138a.py` imports nothing from `scripts/`.
It re-reads the committed snapshot and rebuilds each number from the archived
primary evidence:

| Tier | Input | Re-derivation | Rows |
| --- | --- | --- | --- |
| `exchange` / `exchange_wide` | Polymarket `outcomePrices` for the exact pair | `p_i = x_i / Σx` | 21 |
| `bookmaker_fallback` | EGamersWorld listing decimal odds | `q_i = 1/d_i`, `p_i = q_i/Σq` | 2 |
| `model_vrs` | Valve global standings points | Glicko expectation at RD 75, then `p = 0.5 + 0.7986·(E − 0.5)` | 7 |

Result on the committed snapshot:

```
rows checked: 30 · re-derived: 30 · failures: 0
```

Every row also passed these independent assertions: the two published
probabilities sum to 1; the pick is the larger probability; the published fair
decimal line equals `1/p`; the fixture link and the evidence link are `https`;
and a row with no evidence URL is reported rather than skipped.

**Name mapping.** Exchanges label clubs differently from Hotspawn (`BakS eSports`
/ `BakS`, `ALKA` / `Alka`, `Los Niños` / `LOS NINOS`, `LPH Gaming` / `LPH`). The
verifier maps each source outcome onto the fixture's team order (accent-folded,
alphanumeric, unambiguous prefix of ≥3 characters) and **fails closed** when a
label is ambiguous. That matters: the `1079657 BakS vs BRUTE` market lists
`Brute` first, so an order-blind read of `0.505/0.495` would have flipped the
pick. The verifier caught exactly that in its first run (reported as a failure,
then fixed by mapping, never by editing the board).

## 2. Valve's calibration constant — checked at the source

The model's 0.7986 slope comes from Valve's own published model-fit chart
(`modelfit.png` in `ValveSoftware/counter-strike_regional_standings`), which reads
`y = 0.7986x + 0.126`. The image was downloaded and read this session; the slope
and intercept match the constant used by `scripts/vrs.py`. Valve's README states
the same in words ("the slope is shallower than we'd like"), and `model/fit.js`
shows the fixed rating deviation `rd: 75` used by `priorWinExpectation`.

Points were re-checked for all 14 model-side team entries against Valve's
`standings_global_2026_10_05.md` at commit `eec4853` (380 rows parsed): 14/14
points-and-rank pairs matched the published table, e.g. Phantom Academy #172/783,
Banda Chuya #165/801, Acend #63/1197, 1WIN #38/1383, The Huns #122/944.

## 3. Live resolution research (what was tried, in order)

Every open row's ladder was re-read from the snapshot's own `attempts` records.
For the 10 rows with no exchange line, the ladder ran: Polymarket → HLTV identity
and lineups → Pinnacle → wide exchange tier → researched book listing → our
Valve VRS model. The 7 `model_vrs` rows and 2 `bookmaker_fallback` rows are the
outcome of that ladder; **no row needed the qualitative research tiers** on this
snapshot.

Live spot-checks this session (fresh reads, external to the pipeline):

| Fixture | Live read 09:44–09:56Z | Board (08:32Z) | Note |
| --- | --- | --- | --- |
| 1079655 Nuclear TigeRES vs ILLYRIANS | Polymarket 6036897 `0.85/0.15`, bid 0.84 / ask 0.86, liquidity $6,048, `acceptingOrders: true` | 0.865/0.135 | price moved 1.5 pts in 75 min; board value is dated and within its 8-hour window |
| 1079657 BakS vs BRUTE | 6035008 `0.505/0.495`, bid 0.50 / ask 0.51 | 0.495/0.505 | market lists **Brute first**; board order is correct |
| 1083014 K27 vs Virtus.pro | 6069288 `0.56/0.44`, bid 0.55 / ask 0.57 | 0.565/0.435 | mid 0.56 = board value at capture |
| 1082901 Envy vs GamerLegion | 6037120 `0.465/0.535`, spread 3 pts | 0.465/0.535 | unchanged |
| 1082860 FlyQuest vs Staqued | EGamersWorld page: FlyQuest **1.001**, Staqued **12**, "all bookmakers have agreed that FlyQuest is the favorite… 1.014 / 11.95" | 0.923/0.077 from 1.001/12 | de-vig re-checked: 0.92300/0.07700 — matches to 5 decimals |

Sources: `https://gamma-api.polymarket.com/markets/{6036897,6035008,6069288,6037120}`
and `https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3`.

## 4. Two irregularities found and published (not silently fixed)

Full text and source links are on **Flagged for Review**
(`review.html#session-0cc1138a-lobby-count-parity-2026-10-23`,
`review.html#session-0cc1138a-1081606-no-match-page-2026-10-23`).

1. **Coverage parity.** The live lobby's own filters report **94** CS2 entries
   (`All tiers (94)`; the 23 per-tournament counts sum to 94) while the committed
   feed — and therefore the board — carries **92**. Per-tournament comparison
   isolates the two: CCT Europe 2026 Series #12 is 3 on the lobby and 2 on the
   board (fixture **1081149 FORZE Reload vs LFO 10** was in the 06:17Z board and
   has since left the feed, and is not retained as a closed row), and
   **VOID Autumn Cup 2026** is 1 on the lobby and 0 on the board. The second one
   was not visible in the rendered Closing-Soon/Upcoming lists at capture time,
   so it is flagged rather than guessed. This is the one requirement this session
   could **not** close: the board cannot list a fixture the feed does not return,
   and it currently drops a fixture instead of retaining it as closed.
2. **Missing match page.** 29 of 30 open rows link their own Hotspawn match page;
   `1081606 JiJieHao vs Eternal Fire` links the CS2 pick'em page because the
   lobby renders it without a match link. No URL was invented.

## 5. Phone access and the unresolved section (what changed)

* **Both teams, one card.** Every phone card in *Picks at a glance* now prints
  **both** teams' win chances — our pick in bold green under a `OUR PICK` label,
  the opponent's share immediately beneath in muted type, with the favourite's
  bar under the two rows. Before this change a phone card showed only the
  favourite's percentage. Both byte-identical `style.css` copies and `app.js`
  carry it, and the expiry handler now withdraws the opponent's number too
  (`Withheld`), so an expired card cannot keep showing one live-looking price.
* **A separate unresolved/limitations section in the executive summary**:
  `#unresolved-limits`, placed directly under the pick list. It states how many
  open matches have no percentage (and how many have no pick at all), names the
  sources that returned no exact pair from this snapshot's recorded attempts,
  names any source that refused access with its reason, and lists the four
  structural limitations (our line needs both teams; names/times must match
  exactly; evidence expires; access blocks are not evidence of absence). Every
  number is counted from the snapshot; the sentence "a source that refuses or
  omits a price is a collection limit, not a finding" is pinned by test so a
  future edit cannot turn a 403 into a claim that a book has no line. It links
  to `#unresolved-summary`, `unresolved.html` and `review.html`.
* Navigation: the in-page jump bar now carries `#unresolved-limits` as *Why a
  pick can be missing*. The freshness strip's three links were left exactly as
  another session's test pins them (`picks.html`, `#picks-at-a-glance`,
  `unresolved.html`).

Measured in Chromium (fresh build, 390×844 and 320×568):
`#picks-at-a-glance` at y=582, first card at y=821, no horizontal overflow on any
page; `#unresolved-limits` sits after the 30 cards, i.e. reachable from the jump
bar and from the top-of-page links.

## 6. Verification performed this session

| Gate | Command | Result |
| --- | --- | --- |
| Unit + independent suites | `python -m unittest discover -s tests` | **1079 tests, OK (3 skipped)** |
| Independent row/arithmetic/link validator | `python -m scripts.validate --data data/latest.json --site .` | 92 rows, 30 calculations reproduced, 827 links, 20 checksums, 224 displayed rows |
| Independent re-derivation | `python research/session-0cc1138a/verify_0cc1138a.py` | 30/30 reproduced, 0 failures |
| Browser, a11y, expiry, phone placement | `npm run test:browser` | 6 suites green (32 page/viewport scans, 320/390/768/1440px) |
| Root fallback consistency | `python -m scripts.stage_legacy` then validator | root `build-info.json` hashes match the shipped assets |

New regression suite: `tests/test_session_0cc1138a.py` (21 tests) — independent
re-derivation incl. four corruptions (reversed prices, flipped pick, non-https
source, ambiguous labels), both-team phone cards, expiry withdrawal of the
opponent's number, the unresolved section's counted text, and lobby parity for
the 30 observed fixture IDs.

## 7. Limitations of this session's work

* No network from the agent sandbox: every live read above came through the
  browser-fetch tool, which returns rendered text/JSON. Prices are therefore
  quoted as *observed at a stated minute*, not streamed.
* The two coverage gaps in §4 are **not fixed** — they are published. Fixing them
  needs either a lobby-scrape tier (to catch fixtures the scheduled API omits) or
  retention of fixtures that leave the feed as closed rows; both touch
  `scripts/refresh.py` and `scripts/harvest.py`, which this session did not own.
* Probabilities are market-implied or model estimates; none is a guarantee, and
  the site says so in every tier label.
