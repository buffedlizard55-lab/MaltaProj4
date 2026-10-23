# Independent FlyQuest–Staqued book-line verification

**Independent re-read completed by:** `2026-10-23T05:36:27Z`  
**Fixture:** Hotspawn `1082860`; HLTV `2399890`; DFRAG Invitational 2026 Group B BO3; exact UTC start `2026-10-27T03:00:00Z`.

This note resolves the apparent contradiction between runner HTTP 403 receipts and the separately added book-listing receipt. A 403 in one runner is a collection limitation, not proof that a readable page or odds do not exist. The independent page retrieval below succeeded.

## Source reads

1. [HLTV match 2399890](https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026) is the identity/start authority: FlyQuest vs Staqued, DFRAG Invitational 2026, BO3, `2026-10-27T03:00:00Z`. Ranking and fan-vote fields are not probability inputs.
2. [EGamersWorld's exact fixture page](https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3) independently retrieved successfully. Its title identifies `FlyQuest VS Staqued` and `27.10.2026 at 03:00`; the rendered fixture is BO3 in DFRAG Invitational 2026. The page visibly renders **FlyQuest `1.001`**, **Staqued `12`**, and the linked two-way `1.001 — Make a bet — 12` widget. The page also has a separate analytics estimate (`1.012 / 11.945`); that different aggregate is **not** the receipt input and is not averaged in.
3. [bo3.gg's exact fixture page](https://bo3.gg/matches/flyquest-vs-staqued-27-10-2026) independently retrieved successfully and corroborates the same DFRAG Group B BO3 and two-way winner line: **FlyQuest `1.001` / Staqued `12`** (its market widget rounds this to `1.00 / 12.00`). Its visible local-time rendering is `Oct 26, 23:00`; the UTC binding comes from HLTV, not from converting that local display by assumption.

## Arithmetic replay

```text
raw implied FlyQuest = 1 / 1.001 = 0.999000999000999...
raw implied Staqued  = 1 / 12    = 0.083333333333333...
overround            = sum - 1   = 0.082334332334332... (8.2334%)
normalized FlyQuest  = 0.9230059226213368 -> 92.3%
normalized Staqued   = 0.0769940773786632 ->  7.7%
fair odds            = 1.0834166666666667 / 12.98801198801199
```

These values exactly match the merged `bookmaker_fallback` ledger and `scripts.core.quote_book` replay. The pick is **FlyQuest**. This is a **researched bookmaker-listing** probability, not a Hotspawn signal, HLTV fan vote, ranking conversion, or Polymarket midpoint.

## Limitations that remain published

- EGamersWorld/bo3.gg are listings, not a retained direct operator API response; the source and method remain labelled `bookmaker_fallback` / researched bookmaker listing.
- The listing supplies no per-price update timestamp, so the dated observation and standard eight-hour expiry apply. Expiry must withhold the current pick rather than present it as evergreen.
- Polymarket market `6066520` remains rejected: its exact-fixture quote has an extremely wide bid/ask spread and is not averaged with this book line.
- Runner 403s remain in the attempt ledger. They do not erase the independently readable source, and this successful read does not claim that every runner can always retrieve the page.
