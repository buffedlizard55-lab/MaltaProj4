# Cross-Session Requests from Session `7601d5ee` (`2026-10-22`)

Per `COORDINATION.md`, `data/book-receipts.json`, `data/review-notes.json`, and `data/identities.json` are outside session `7601d5ee`'s file scope. The primary-source receipts below are ready to merge into those shared data files.

---

## Request 1 — Add Vave Prematch Moneyline Receipts to `data/book-receipts.json`

### 1A. Fixture `1082769` — **K27 vs NEXORA** (`2026-10-22T17:30:00Z`, CIS LAN Championship #9)

Currently resolved on the live board via `research_rank_single` (`pick: K27`, `probabilities: null`). Adding this verified Vave prematch moneyline upgrades `1082769` to a priced `bookmaker_research` row (`88.8% K27 / 11.2% NEXORA`, fair odds `1.13 / 8.94`), which also matches HLTV's 22 Oct 2026 Valve Global Ranking (`#31 K27 1396 pts vs #282 NEXORA 596 pts` -> `89.04% / 10.96%`):

```json
{
  "fixture_id": "1082769",
  "teams": [
    "K27",
    "NEXORA"
  ],
  "competition": "CIS LAN Championship #9",
  "start": "2026-10-22T17:30:00Z",
  "provider": "Vave (via EGamersWorld)",
  "url": "https://egamersworld.com/counterstrike/tip/nexora-vs-k27-U_TH-dVYT/4yp_dlKtNl",
  "additional_url": "https://egamersworld.com/counterstrike/match/nexora-vs-k27-U_TH-dVYT",
  "hltv_url": "https://www.hltv.org/matches/2399846/nexora-vs-k27-winline-mpkbk-cis-lan-season-9",
  "observed_at": "2026-10-22T01:21:00Z",
  "decimal_odds": [
    1.021,
    8.1
  ],
  "probabilities": [
    0.888109,
    0.111891
  ],
  "overround": 0.102875,
  "basis": "Verified prematch moneyline on EGamersWorld's Vave tip receipt (NEXORA 8.1 / K27 1.021; match listing index shows NEXORA 8.2 / K27 1.04) for WINLINE MPKBK CIS LAN Season 9 Group D opening match at 2026-10-22T17:30:00Z, corroborated by HLTV match 2399846 and HLTV's 22 Oct 2026 Valve Global Ranking (#31 K27 1396 pts vs #282 NEXORA 596 pts -> 89.04% / 10.96%)."
}
```

### 1B. Fixture `1079188` — **Bushido Wildcats vs ex-6666** (`2026-10-22T08:00:00Z`, NODWIN Clutch Series #13)

Currently priced by `model_vrs` from the `2026-10-05` Valve VRS (`#114 Bushido Wildcats 982 pts vs #127 6666 923 pts` -> `56.5% Bushido Wildcats / 43.5% ex-6666`). Vave's prematch moneyline (`2.26 / 1.55`), HLTV's 19 Oct 2026 World Ranking (`#113 vs #72`), and HLTV's 22 Oct 2026 Valve Global Ranking (`#121 898 pts vs #117 918 pts` -> `47.8% / 52.2%`) all favour **ex-6666**:

```json
{
  "fixture_id": "1079188",
  "teams": [
    "Bushido Wildcats",
    "ex-6666"
  ],
  "competition": "NODWIN Clutch Series #13",
  "start": "2026-10-22T08:00:00Z",
  "provider": "Vave (via EGamersWorld)",
  "url": "https://egamersworld.com/counterstrike/tip/bushido-wildcats-vs-ex-6666-Xs452MP7y/Nk9F-Ov54e",
  "additional_url": "https://egamersworld.com/counterstrike/match/bushido-wildcats-vs-ex-6666-Xs452MP7y",
  "hltv_url": "https://www.hltv.org/matches/2399105/bushido-wildcats-vs-ex-6666-nodwin-clutch-series-13",
  "observed_at": "2026-10-22T01:21:00Z",
  "decimal_odds": [
    2.26,
    1.55
  ],
  "probabilities": [
    0.406819,
    0.593181
  ],
  "overround": 0.087639,
  "basis": "Verified prematch moneyline on EGamersWorld's Vave tip receipt (Bushido Wildcats 2.26 / ex-6666 1.55; match listing index shows 2.35 / 1.50) for NODWIN Clutch Series #13 at 2026-10-22T08:00:00Z, corroborated by HLTV match 2399105 (#113 Bushido Wildcats vs #72 ex-6666) and HLTV's 22 Oct 2026 Valve Global Ranking (#121 Bushido Wildcats 898 pts vs #117 6666 918 pts)."
}
```

---

## Request 2 — Add Review Notes to `data/review-notes.json` (`indent=1`)

1. **`1082769` (K27 vs NEXORA)**: Document both the Vave prematch moneyline (`K27 1.021 / NEXORA 8.10` -> `88.81% / 11.19%`) and HLTV's 22 Oct 2026 Valve Global Ranking (`#31 K27 1396 pts vs #282 NEXORA 596 pts` -> `89.04% / 10.96%`).
2. **`1079188` (Bushido Wildcats vs ex-6666)**: Flag the directional divergence between the 5 Oct 2026 VRS model (`56.5% Bushido Wildcats / 43.5% ex-6666`) and the newer 22 Oct 2026 VRS (`47.8% / 52.2%`), HLTV World Ranking (`#113 vs #72`), and Vave prematch moneyline (`40.7% / 59.3%` in favour of `ex-6666`).
3. **`1079654` (ex-Zero Tenacity vs ex-RUSTEC)** and **`1081150` (ex-RUSTEC vs Saint Sinners)**: Document why `ex-RUSTEC` (`youka, bl1x1, yiksrezo, Brilliance, jakekeS`) ties `3/5` with both `#92 (1066 pts)` and `#152 (824 pts)` in the 5 Oct 2026 VRS file, and record the 22 Oct 2026 VRS points (`#91 RUSTEC 1073 pts` vs `#95 ex-Zero Tenacity 1053 pts` -> `47.8% / 52.2%`; `#91 RUSTEC 1073 pts` vs `#133 Saint Sinners 898 pts` -> `68.1% / 31.9%`).
4. **`1081149` (FORZE Reload vs LFO 10)**: Document that `LFO 10` (`team/14084`, formerly `#156 Entropy 813 pts` in 5 Oct VRS) shares `3/5` players (`dottie, flaw, Sapec`) on its 22 Oct 2026 VRS roster (`#157 805 pts: dottie, flaw, Sapec, Mann3n, L00m1`), but fielded `dan1` in place of `flaw` on HLTV match `2399499` (`Sapec, dottie, L00m1, Mann3n, dan1`), reducing overlap with the 5 Oct `Entropy` roster to `2/5` and rightly triggering the fail-closed roster-continuity guard.
