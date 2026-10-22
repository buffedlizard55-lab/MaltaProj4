# Acceptance Audit — Session `7601d5ee` (`2026-10-22`)

- **Session ID**: `7601d5ee`
- **Branch**: `arena/7601d5ee-maltaproj4`
- **Audited Snapshot (`data/latest.json`)**: `2026-10-22T01:28:24.176572Z`
- **Live GitHub Pages URL**: `https://buffedlizard55-lab.github.io/MaltaProj4/`

---

## 1. Requirement-by-Requirement Verification Matrix

| # | User Requirement / Constraint | Verification Method | Result |
|---:|---|---|---|
| 1 | **Complete Hotspawn CS2 inventory (`https://play.hotspawn.com/lobby`)**: collect, organize, analyze, and maintain all CS2 matches updated every 4–8 hours (`refresh_hours: 1`, `stale_after_hours: 8`). | Cross-checked `https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1`, `https://play.hotspawn.com/cs2-pickems`, and `https://play.hotspawn.com/lobby`: `97` CS2 rows (`35` open, `62` non-open historical rows), `0` fixture conflicts. | **PASS (`97 / 97`)** |
| 2 | **Generate picks for every open CS2 match on Hotspawn** (including low-tier matches and matches missing from Polymarket). | All **35 / 35** open matches carry a verified pick: `8` Polymarket (`7 exchange` + `1 exchange_wide`), `1` Pinnacle (`bookmaker_fallback`), `19` Valve VRS model (`model_vrs`), and `7` research-only picks (`4 research_rank_single`, `2 research_rank`, `1 research_vrs_single`). | **PASS (`35 / 35`, `0` unresolved)** |
| 3 | **Never use Hotspawn as an indicator for match probability** (inventory only; no crowd-pick percentages). | Verified by `scripts/inventory.py`, `scripts/validate.py`, and `verification-7601d5ee/audit_board_7601d5ee.py` (`FORBIDDEN_HOTSPAWN_TOKENS` absent across all 9 HTML pages and `data/latest.json`). | **PASS** |
| 4 | **Originate probabilities/lines from external esports betting lines and HLTV / Valve Regional Standings (VRS)**; research HLTV then esportsbooks/betting lines only for matches that cannot be resolved the same way as featured picks. | Verified tier order in `scripts/refresh.py`: `exchange` -> `bookmaker` -> `book_research_pick` -> `vrs.apply` -> `research_rank_pick` -> `research_single_rank_pick` -> `vrs.research_single`. Every priced row (`28`) re-derives its exact probabilities and fair odds from its raw evidence quote in `audit_board_7601d5ee.py`. | **PASS** |
| 5 | **Include a separate section for unresolved / unpriced picks and their limitations**, and include this in the executive summary. | Verified `unresolved.html` (`26` `tbody` rows covering the `7` research-only open matches and their per-provider attempt logs) and the executive summary on `index.html` linking directly to `picks.html`, `unresolved.html`, and `review.html`. | **PASS** |
| 6 | **Mobile-friendly executive summary on the landing page** making picks and win probabilities immediately obvious on phone/mobile devices. | Verified `meta name="viewport" content="width=device-width, initial-scale=1"` on all 9 pages, responsive mobile cards/tables in `assets/style.css`, and the executive summary on `index.html`. | **PASS** |
| 7 | **Line-by-line verification against official verified trusted sources with source links on every table row**; leave unconfirmed values blank and flag them on `review.html` (no hallucinations). | Verified by `verification-7601d5ee/audit_board_7601d5ee.py`: every `tbody tr` across `picks.html` (`28`), `unresolved.html` (`26`), `matches.html` (`97`), `evidence.html` (`38`), `review.html` (`184`), and `sources.html` (`68`) has at least one `https://` official source link; all `7` research-only rows leave probability/fair-odds blank (`—`) and are listed on `review.html`. | **PASS** |

---

## 2. Reproducible Verification Commands

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate.py
.venv/bin/python scripts/probe_7601d5ee.py
.venv/bin/python verification-7601d5ee/audit_board_7601d5ee.py
```
