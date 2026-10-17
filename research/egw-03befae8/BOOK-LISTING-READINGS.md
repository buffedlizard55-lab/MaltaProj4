# Book-listing readings, session 03befae8 (17 October 2026)

Every reading below was made from a normal page read of the source named in each
row, on 17 October 2026 between 00:15 and 00:50 UTC. The automated pipeline
could not make these reads: the project's own runner is refused by
EGamersWorld with **HTTP 403** after three rate-limit waits (10 s, 30 s, 60 s),
and this project does not change how its requests identify themselves in order
to get past a block. The refusal is logged in
`research/harvest-03befae8/logs/egw-probe.txt`; the capture itself is in
`research/harvest-03befae8/egw/egw-probe.json`.

## What the listing pages carry

EGamersWorld publishes, for many CS2 fixtures, a two-sided **bookmaker-average**
line in plain text. Three sentence forms were observed:

1. "According to leading bookmakers predictions, the team X are the favorite with
   average odds A at the moment. Respectively, bookmakers consider Y to be the
   outsider of the match with odds on a victory in the sum of about B."
   (example: Bebop vs Donstu Esports, A = 1.493, B = 2.415)
2. "Bookmakers make X the favourites at A, with Y the underdogs at B."
   (example: NiP vs Heroic, A = 1.67, B = 2.16)
3. "X are listed as the favorites of the match in the majority of bookmakers and
   odds on them are equal to A. Y, in turn, are the outsiders of the match. Odds
   on their victory are about B." (example: ex-6666 vs Privateer Gaming,
   A = 1.15, B = 4.5)

Form 3 was not covered by the probe's regular expressions and is recorded here so
the next reader does not have to rediscover it. The header row of the same page
repeats the pair, which is the cross-check used for every accepted reading.

## Readings taken

| Hotspawn row | Fixture | Source page | Displayed | Reading | Outcome |
|---|---|---|---|---|---|
| 1081521 | ex-6666 vs Privateer | [EGW match page](https://egamersworld.com/counterstrike/match/rW6Ymkl0D/ex-6666-vs-privateer-gaming-sfo_MjtRV) | ex-6666 **1.15** / Privateer Gaming **4.5** | 17 Oct 00:45 UTC | **Accepted** → receipt `egw-rW6Ymkl0D-ex-6666-privateer`, de-margined to 79.6% / 20.4% |
| 1081513 | Bebop vs Donstu | [EGW match page](https://egamersworld.com/counterstrike/match/rW6Ymkl0D/bebop-vs-donstu-esports-N96TxtN4P) | Bebop 1.5 / Donstu 2.35 (header), book average **1.493 / 2.415** | 17 Oct 00:35 UTC | Not needed: the row is already priced by a Pinnacle moneyline (matchup 1638582117, 0.613 / 0.387) |
| 1081511 | VP.Future vs Black Phoenix | [EGW match page](https://egamersworld.com/counterstrike/match/Eklp98tP5Ee/vpfuture-vs-black-phoenix-dGceA4XCC) | 1.8 / 1.8 | 17 Oct 00:20 UTC | **Refused**: identical default odds, a placeholder rather than a market |
| 1079634 | Lavked vs LFO 10 | [EGW match page](https://egamersworld.com/counterstrike/match/_rW8GEyWK/lavked-vs-z6CTAa5pD) | 1.8 / 1.8, and the opponent's name, logo, rating and record are all blank ("Lavked VS ") | 17 Oct 00:25 UTC | **Refused**: no opponent pair to verify identity against, and identical default odds |
| 1081522 | antidaun vs Phantom Academy | [EGW match page](https://egamersworld.com/counterstrike/match/rW6Ymkl0D/antidaun-vs-phantom-academy-zXFTwo17o8) | 1.8 / 1.8 | 17 Oct 00:30 UTC | **Refused**: identical default odds |
| 1081861 | Lynn Vision vs Morningstar | [EGW match page](https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/lynn-vision-vs-morningstar-7AWA3eTHD) | 1.8 / 1.8 | 17 Oct 00:30 UTC | **Refused**: identical default odds |
| 1081863 | Chinggis Warriors vs WXM | [EGW match page](https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/chinggis-warriors-vs-wxm-_ddme1I7dZ) | 1.8 / 1.8 | 17 Oct 00:30 UTC | **Refused**: identical default odds |

## Why the accepted reading is safe to publish

* **Identity.** The EGW page states the fixture as "ex-6666 VS Privateer Gaming …
  18.10.2026 at 13:45 … BO3" in the CCT Europe 2026 Challengers #8 event, which
  is the same opponent pair, the same competition and the same UTC start as
  Hotspawn row 1081521 (start 2026-10-18T13:45:00Z, lock 13:39 UTC) and HLTV
  match 2399681. "Privateer" and "Privateer Gaming" are the same club, which the
  project's identity register already bridges.
* **Two-sided and non-default.** 1.15 and 4.5 are not identical, and the
  de-margined line (79.6% / 20.4%, overround 9.2%) is inside the project's
  25% bookmaker-margin bound.
* **Cross-check.** The same page's own book-average sentence repeats the pair
  (1.15 / 4.5), and the line agrees with our own Valve-standings model for the
  same row (78.2% / 21.8% in the 00:54 UTC capture), so the two independent
  sources point the same way.
* **Fail-closed.** The receipt ages out after the standard eight-hour window
  (observed 2026-10-17T00:45:00Z). After that the row falls back to the model
  line and the reason is published on the row; it never keeps a stale price.

## Why the five refused rows stay without a percentage

Polymarket has no active market for any of the five (checked through the
exchange's own event list for the active CS2 series, and through its public
search for "Phantom Academy" and "Morningstar", which returned only closed
2025 fixtures), Pinnacle has no matchup for them, Thunderpick is reachable but
renders its prices in JavaScript, and GG.BET refuses the runner with the same
403. The listing adds no two-sided line for any of the five. The honest output
is therefore a research-only pick with **no percentage**, which is what the
board already publishes, with the reason attached.
