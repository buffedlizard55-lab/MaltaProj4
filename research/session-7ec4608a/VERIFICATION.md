# Line-by-line verification — session 7ec4608a

Snapshot: 2026-10-21T21:27:36.742398Z (observed 2026-10-21T21:24:01.824961Z), coverage=verified, rows=75

## Open fixtures (13) — every row must have source link to official site; blank if unverified stays blank and flagged

| # | Fixture | Hotspawn source | Pick source | Probability source | Verified | Notes |
|---|---|---|---|---|---|---|
| 1082837 | Zetta vs LOS NINOS (2026-10-21T22:00:00Z) | [Hotspawn](https://www.hotspawn.com/matches/zetta-vs-los-ninos-cct-south-america-2026-series-7-1082837) | LOS NINOS (exchange) | Polymarket: 15.5% / 84.5% | ✓ |  |
| 1081870 | Vitalem Aerem vs Rare Atom (2026-10-22T05:00:00Z) | [Hotspawn](https://www.hotspawn.com/matches/vitalem-aerem-vs-rare-atom-void-autumn-cup-2026-1081870) | Rare Atom (exchange_wide) | Polymarket: 39.0% / 61.0% | ✓ |  |
| 1081597 | benched gods vs TitanFlow (2026-10-22T11:00:00Z) | [Hotspawn](https://www.hotspawn.com/matches/benched-gods-vs-titanflow-cct-europe-2026-challengers-8-1081597) | benched gods (research_vrs_single) | https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md: — (research-only, no percentage) | ✓ |  |
| 1081600 | Donstu vs Banda chuya (2026-10-22T13:45:00Z) | [Hotspawn](https://www.hotspawn.com/matches/donstu-vs-banda-chuya-cct-europe-2026-challengers-8-1081600) | Banda chuya (model_vrs) | Valve VRS model: 42.4% / 57.6% | ✓ |  |
| 1082688 | Imperial vs Turma do Pagode (2026-10-22T14:00:00Z) | [Hotspawn](https://www.hotspawn.com/matches/imperial-vs-turma-do-pagode-circuit-x-curitiba-4-1082688) | Imperial (exchange) | Polymarket: 77.0% / 23.0% | ✓ |  |
| 1082689 | BESTIA vs ShindeN (2026-10-22T14:00:00Z) | [Hotspawn](https://www.hotspawn.com/matches/bestia-vs-shinden-circuit-x-curitiba-4-1082689) | ShindeN (exchange) | Polymarket: 46.5% / 53.5% | ✓ |  |
| 1082882 | UNiTY vs Apogee Betclic (2026-10-22T14:00:00Z) | [Hotspawn](https://www.hotspawn.com/matches/unity-vs-apogee-betclic-stake-ranked-episode-6-closed-qualifier-1082882) | Apogee Betclic (exchange) | Polymarket: 43.5% / 56.5% | ✓ |  |
| 1082858 | Ground Zero vs Off Chops (2026-10-26T03:00:00Z) | [Hotspawn](https://play.hotspawn.com/cs2-pickems) | Off Chops (model_vrs) | Valve VRS model: 39.8% / 60.2% | ✓ |  |
| 1082859 | NEXVOID vs Alter Ego (2026-10-26T03:00:00Z) | [Hotspawn](https://play.hotspawn.com/cs2-pickems) | NEXVOID (model_vrs) | Valve VRS model: 68.2% / 31.8% | ✓ |  |
| 1082860 | FlyQuest vs Staqued (2026-10-27T03:00:00Z) | [Hotspawn](https://play.hotspawn.com/cs2-pickems) | FlyQuest (research_rank_single) | https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026: — (research-only, no percentage) | ✓ |  |
| 1082861 | Rooster vs Abyssal (2026-10-27T03:00:00Z) | [Hotspawn](https://play.hotspawn.com/cs2-pickems) | Abyssal (model_vrs) | Valve VRS model: 48.2% / 51.8% | ✓ |  |
| 1082792 | HOTU vs The Huns (2026-10-31T09:00:00Z) | [Hotspawn](https://www.hotspawn.com/matches/hotu-vs-the-huns-moscow-cyber-games-2026-1082792) | HOTU (model_vrs) | Valve VRS model: 85.2% / 14.8% | ✓ |  |
| 1082793 | 5star vs 1WIN (2026-10-31T13:00:00Z) | [Hotspawn](https://www.hotspawn.com/matches/5star-vs-1win-moscow-cyber-games-2026-1082793) | 1WIN (model_vrs) | Valve VRS model: 24.3% / 75.7% | ✓ |  |

## Not-open sample (first 5 of 62)
- 1052746 ['Fortress', 'Endless Journey'] state=not_open flags=['Hotspawn reports scheduled status and an end time simultaneously.']
- 1051339 ['Acend', 'Infinite'] state=not_open flags=['Hotspawn reports scheduled status and an end time simultaneously.']
- 1051301 ['CYBERSHOKE Prospects', 'PCIFIC'] state=not_open flags=['Hotspawn reports scheduled status and an end time simultaneously.']
- 1053068 ['Johnny Speeds', 'ReThink'] state=not_open flags=['Hotspawn reports scheduled status and an end time simultaneously.']
- 1052747 ['Sashi Academy', 'eternal premium'] state=not_open flags=['Hotspawn reports scheduled status and an end time simultaneously.']

## Checker
- `python -m scripts.validate --data data/latest.json --site .` at 2026-10-22 01:10 UTC: 75 rows, 11 probability calculations reproduced, 15 pages, 655 links/assets, 20 checksums, 176 displayed rows — **pass**
- `python -m unittest discover -s tests` : 602 OK (01:10 UTC)
- `python -m unittest discover -s verification-c6` : 12 OK, 5 integrity OK
- No hallucinated values: every percentage devigged from stored raw odds/prices; research-only rows publish no percentage per policy; identical 1.8/1.8 placeholder never accepted.
- Hotspawn reverse-engineering: lobby + cs2-pickems + fixtures API IDs/fields compared; schedule 4×/hour + 10-min watchdog covers 4–8h promise.
- Mobile: viewport meta, 320px+ no horizontal scroll, bottom nav 5 tabs ≥60px, glance cards, fresh-strip at top with links, jump bar.
