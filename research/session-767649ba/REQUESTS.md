# Session `767649ba` Cross-Session Requests (`2026-10-22 UTC`)

Per `COORDINATION.md`, session `767649ba` left files actively modified by concurrent PRs (`scripts/vrs_anchor_2d0a85f2.py`, `data/identities.json`, `data/review-notes.json`, `tests/test_session_7ec4608a.py`) untouched and logs exact primary-source requests below for their respective owners or the next uncontested maintenance sweep:

1. **`data/identities.json` (`Zetta` primary source slug correction — owner of `identities.json`):**
   - Current URL `https://www.hltv.org/matches/2399867/los-ninos-vs-zetta-cct-season-3-south-america-series-7` points to another match ID (`2399867`), and stage label `"Group Stage"` should read `"Swiss Round 5"`.
   - Verified primary replacement: `https://www.hltv.org/matches/2399865/zetta-vs-los-ninos-cct-season-3-south-america-series-7` (`Swiss Round 5`).

2. **`data/review-notes.json` (`1082858` historical prose percentage — owner of `review-notes.json`, e.g., PR `#139` / `#145`):**
   - Check if the note for `1082858` (`Ground Zero vs Off Chops`) still quotes `Off Chops 59.1% / Ground Zero 40.9%` in narrative text while the actual published `model_vrs` vector (`971` vs `878` pts, Glicko `RD=75` calibrated with Valve `SLOPE = 0.7986`) is **`Off Chops 60.2% / Ground Zero 39.8%`** (`0.602402 / 0.397598`). Note: `json.dumps(..., indent=1)` formatting must be preserved on `data/review-notes.json`.

3. **`scripts/vrs_anchor_2d0a85f2.py` (misleading flag wording when both opponents have VRS entries):**
   - `with_anchors()` appends `"Roster anchor used: ... — research pick only, no percentage published."` whenever an anchor lineup is injected, even if the fixture subsequently resolves to a numeric two-sided `model_vrs` line (e.g., if `TitanFlow` enters the next monthly Valve global file opposite `benched gods`). Only attach the `"no percentage published"` suffix when `row["probabilities"] is None`.

4. **PR `#139` (`tests/test_session_7ec4608a.py` mutable-snapshot hazard warning):**
   - `tests/test_session_7ec4608a.py` asserts `probabilities is None` on live fixture IDs `1081597` and `1082860` inside `data/latest.json`. Once either fixture receives real pre-match exchange/bookmaker odds (e.g., `DFRAG Invitational` markets opening before `2026-10-27T03:00Z`), pinning `probabilities is None` on live rows would block automated refreshes. Prefer fixture-copied unit assertions (as in `tests/test_session_767649ba.py`) over mutable `data/latest.json` state assertions.
