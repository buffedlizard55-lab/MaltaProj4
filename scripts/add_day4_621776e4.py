"""Add the verified day-4 guidance block to data/analysis.json (session 621776e4)."""
import json
from pathlib import Path

PATH = Path('data/analysis.json')
STANDINGS = ('https://github.com/ValveSoftware/counter-strike_regional_standings/blob/'
             'eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md')
RESULTS = 'https://www.hltv.org/results?event=8932'

day_four = {
    "date": "Day 4 \u00b7 Friday 17 October 2026",
    "nav_label": "Day-4 guidance",
    "anchor": "guidance-day4",
    "card": "Semi-final day: the priced board picks, the contrarian side of each, and the two semi-finals Hotspawn had not listed yet.",
    "headline": "Day-four guidance: two semi-finals, priced from the market and from our own model",
    "summary": ("Semi-final day in Malta. Both semi-finals are priced below from primary sources: the FURIA\u2013Aurora line was "
                "read from Polymarket's official API at 19:35 UTC on 16 October, and both are also priced by our own Valve-standings "
                "model so the two can be compared. Neither semi-final was on the Hotspawn feed at that check, so the board publishes "
                "no pick for them yet \u2014 it will price them automatically the moment Hotspawn lists them. The table above this "
                "section covers the fixtures that ARE on the board for 17 October. Scoring on Hotspawn awards a fixed number of points "
                "per correct pick, so the leaderboard-optimal choice is always the higher-probability team; the contrarian column exists "
                "for the cases where you judge the favourite to be wrong, not because going against the crowd is worth anything by itself."),
    "points_label": "What day one to day three actually showed",
    "points": [
        {"claim": "Day 1: 9z beat Aurora 2-0 \u2014 the upset that opened the event.",
         "detail": "Inferno 13-11, then 13-1 on Nuke, which was Aurora's own map pick. HLTV's report gives luchov a 1.61 rating, +6.61% swing and 97.4 ADR, and notes Aurora were the fifth-ranked team in the VRS going in.",
         "source": "https://www.hltv.org/news/45718/9z-beat-aurora-2-0-to-kick-off-twc-2026"},
        {"claim": "Day 1: all four openers were sweeps.",
         "detail": "9z 2-0 Aurora, Falcons 2-0 Ninjas in Pyjamas, Legacy 2-0 PARIVISION, FURIA 2-0 BETBOOM \u2014 so after one day nobody in either group had dropped a series.",
         "source": RESULTS},
        {"claim": "Day 2: Aurora survived elimination and 9z took a map off Falcons.",
         "detail": "Aurora 2-0 Ninjas in Pyjamas (Cache 13-9, Dust2 13-7, Wicadia 45-25 and a 1.65 rating), Falcons 2-1 9z, BETBOOM 2-1 PARIVISION, FURIA 2-1 Legacy. Both winners' matches went the distance, which is the first sign that the seeded order was not holding.",
         "source": RESULTS},
        {"claim": "Day 3: Aurora beat 9z 2-0 in the Group A decider and reached the semi-finals.",
         "detail": "Cache 13-11 (half-time 8-4, then 5-7) and Inferno, for a 2-0 series win. The Inferno scoreline is published as 13-4 by dust2.com.br and EGamersWorld; this session did not re-verify that single map score on HLTV, so only the series score and the Cache result are treated as primary. This was the rematch of the day-one upset and it went the other way, so the two teams split their Malta meetings 1-1 in series and 9z finish 5th/6th.",
         "source": "https://www.hltv.org/news/45736/aurora-beat-9z-to-secure-third-consecutive-top-four-appearance"},
        {"claim": "Aurora's roster change is from July, not from this week.",
         "detail": "HLTV dates Aurora's last transfer to 8 July 2026 (kyxsan in from Falcons), with Jimpphat and coach ash signed on 3 July. The five in Malta are XANTARES, woxic, Wicadia, Jimpphat and kyxsan. There is no October roster change and no new player still being onboarded, so 'recent roster change' cannot be used as a day-four factor.",
         "source": "https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan"},
        {"claim": "The day-one upset is not evidence that upsets pay.",
         "detail": "9z's win was a genuine outlier: the same pairing reversed 2-0 two days later. Across days 1-3 the higher-ranked side won eight of the ten series, and the two exceptions were the same two teams. Form at this event has been noisy, not inverted.",
         "source": RESULTS},
        {"claim": "Hotspawn scores a correct pick with a fixed award.",
         "detail": "Multipliers come from tier, stage and format, not from how the crowd split, which was re-checked across 102 CS2 rows in verification-3c8d1136/LIVE-BOARD-VERIFICATION.md. A crowd-contrarian pick therefore earns exactly the same as a crowd-following pick when it is right \u2014 contrarianism only helps if the favourite is genuinely wrong.",
         "source": "https://play.hotspawn.com/how-it-works"},
    ],
    "fixtures": [
        {"hotspawn_id": "1081515",
         "label": "Apogee Betclic vs Nemesis",
         "event": "PGL Bucharest 2027 Closed Qualifier, upper bracket semi-final (best of 3)",
         "contrarian": "Apogee Betclic",
         "verdict": "Priced underdog, 32%",
         "why": ("This row had no pick at all until 16 October because the three sources label the same club differently: Hotspawn writes "
                 "'Apogee Betclic', HLTV writes 'Betclic' and Polymarket writes 'Betclic Apogee Esports'. The verified identity mapping now "
                 "connects them, and the same fixture's UTC start (2026-10-17T14:00:00Z) matches on both sources, so the exchange line is "
                 "attached: Nemesis 68% / Apogee Betclic 32%. Apogee Betclic therefore sit inside the 15-40% contrarian band with a real "
                 "market price behind them rather than a guess."),
         "sources": [
             {"label": "Polymarket market 5776037 (0.32 / 0.68, spread 4 points, $3,296.78 liquidity)",
              "url": "https://gamma-api.polymarket.com/markets/5776037"},
             {"label": "HLTV fixture 2399660 (Betclic vs Nemesis, same upper-bracket slot)",
              "url": "https://www.hltv.org/matches/2399660/betclic-vs-nemesis-pgl-bucharest-2027-closed-qualifier"},
         ]},
        {"hotspawn_id": "1081888",
         "label": "Ninjas in Pyjamas vs Heroic",
         "event": "Stake Pulse Beat III",
         "contrarian": "Ninjas in Pyjamas",
         "verdict": "Lean, near coin flip",
         "why": ("NIP were eliminated in Malta on day 2 by Aurora (Cache 13-9, Dust2 13-7) and travel straight back into this fixture, while "
                 "Heroic have had no LAN minutes this week. The exchange still makes Heroic the favourite, so the priced gap is small enough "
                 "that the scheduling and form argument is worth more than the ranking difference \u2014 but it is a lean, not a swing."),
         "sources": [
             {"label": "HLTV result: Aurora 2-0 Ninjas in Pyjamas (15 October)",
              "url": "https://www.hltv.org/matches/2399408/aurora-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026"},
             {"label": "HLTV: NIP's schedule after the early TWC exit",
              "url": "https://www.hltv.org/news/45724/nip-spared-scheduling-headache-after-early-thunderpick-world-championship-exit"},
         ]},
        {"hotspawn_id": "1081513",
         "label": "Bebop vs Donstu",
         "event": "CCT Europe 2026 Challengers #8",
         "contrarian": "Bebop",
         "verdict": "Model-priced only, no market",
         "why": ("No exchange market, no Pinnacle matchup and no HLTV odds row exist for this fixture, so the only number on the board is our "
                 "own Valve-standings model line, which is a near coin flip. Treat it as the weakest evidence class on the page: the model is "
                 "calibrated on monthly standings that predate this week, and it is labelled as a model estimate everywhere it appears."),
         "sources": [{"label": "Valve official standings (2026-10-05, commit eec4853)", "url": STANDINGS}]},
    ],
    "not_listed": [
        {"label": "FURIA vs Aurora",
         "event": "Thunderpick World Championship 2026, semi-final 1 (best of 3, Malta)",
         "teams": ["FURIA", "Aurora"],
         "points": [1829, 1716],
         "now_listed": False,
         "timing": "HLTV's machine-readable start is 2026-10-17T14:00:00Z (HLTV displays 10:00 because this event's clock is UTC\u22124).",
         "market": {"label": "Polymarket, read 16 Oct 19:35 UTC",
                    "detail": "FURIA 52% / Aurora 48% \u2014 market 5778024, bid 0.51 / ask 0.53 (2-point spread), $10,151.23 liquidity, accepting orders, updated 19:34:52 UTC. The same event's map handicap prices FURIA to win 2-0 at 18.5%, i.e. the market expects a three-map series more often than not.",
                    "url": "https://gamma-api.polymarket.com/markets/5778024",
                    "link_label": "Official Polymarket market \u2197"},
         "why": ("This is the day's real decision. The market and our model agree on direction and disagree on size: Polymarket calls it a "
                 "coin flip, while Valve's standings make FURIA a 62% favourite. The sourced case for the 48% side is Aurora's week \u2014 they "
                 "answered the day-one upset by beating NIP 2-0 and 9z 2-0, and XANTARES/woxic/Wicadia have LAN form \u2014 against FURIA's "
                 "higher HLTV world ranking (#4 vs #6) and their own 2-0 and 2-1 group wins. With a 48% price there is no meaningful edge "
                 "either way, so the honest reading is: pick FURIA unless you specifically believe the market is overrating them, in which "
                 "case Aurora at 48% is the cheapest differentiation available on day four."),
         "hltv_url": "https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026",
         "standings_url": STANDINGS,
         "sources": [
             {"label": "HLTV: Aurora beat 9z to reach the semi-finals",
              "url": "https://www.hltv.org/news/45736/aurora-beat-9z-to-secure-third-consecutive-top-four-appearance"},
             {"label": "HLTV: 9z beat Aurora 2-0 on day one",
              "url": "https://www.hltv.org/news/45718/9z-beat-aurora-2-0-to-kick-off-twc-2026"},
             {"label": "HLTV: FURIA came back to beat Legacy 2-1",
              "url": "https://www.hltv.org/matches/2399411/legacy-vs-furia-thunderpick-world-championship-2026"},
         ]},
        {"label": "Falcons vs Legacy (if Legacy take the Group B decider)",
         "event": "Thunderpick World Championship 2026, semi-final 2 (best of 3, Malta)",
         "teams": ["Falcons", "Legacy"],
         "points": [1843, 1931],
         "now_listed": False,
         "timing": "HLTV's machine-readable start is 2026-10-17T17:00:00Z. Opponent conditional on the decider, which had not been published when this was written.",
         "why": ("Conditional card, not a pick: Legacy are the second-highest rated team in the event on Valve's standings (1931 points, "
                 "above Falcons' 1843), so our model makes Legacy a 59.6% favourite over the Cologne Major champions. No betting market "
                 "existed for this semi-final at the 19:35 UTC check, so no market probability is published \u2014 the model number is the "
                 "only one, and it is labelled as ours."),
         "hltv_url": "https://www.hltv.org/matches/2399415/falcons-vs-betboom-legacy-winner-thunderpick-world-championship-2026",
         "standings_url": STANDINGS,
         "sources": [
             {"label": "HLTV: FURIA 2-1 Legacy (day 2)",
              "url": "https://www.hltv.org/matches/2399411/legacy-vs-furia-thunderpick-world-championship-2026"},
             {"label": "HLTV: Falcons 2-1 9z to top Group A",
              "url": "https://www.hltv.org/news/45728/falcons-secure-playoff-berth-at-twc-2026"},
         ]},
        {"label": "Falcons vs BetBoom (if BetBoom take the Group B decider)",
         "event": "Thunderpick World Championship 2026, semi-final 2 (best of 3, Malta)",
         "teams": ["Falcons", "BetBoom"],
         "points": [1843, 1596],
         "now_listed": False,
         "timing": "Same fixture and start as the card above; only the opponent differs. Opponent conditional on the decider.",
         "why": ("Conditional card, not a pick. Against BetBoom our model reads Falcons 73.9%, the widest gap of the three day-four "
                 "possibilities, because BetBoom are the lowest rated of the four semi-final candidates on Valve's standings (1596 points). "
                 "BetBoom have already lost to FURIA 2-0 and needed three maps to remove PARIVISION. No market line existed at the check."),
         "hltv_url": "https://www.hltv.org/matches/2399415/falcons-vs-betboom-legacy-winner-thunderpick-world-championship-2026",
         "standings_url": STANDINGS,
         "sources": [
             {"label": "HLTV: FURIA 2-0 BETBOOM (day 1)",
              "url": "https://www.hltv.org/matches/2399387/furia-vs-betboom-thunderpick-world-championship-2026"},
             {"label": "HLTV: BETBOOM 2-1 PARIVISION (day 2)",
              "url": "https://www.hltv.org/matches/2399410/parivision-vs-betboom-thunderpick-world-championship-2026"},
         ]},
    ],
    "unverified": [
        "The Group B decider (BetBoom vs Legacy, HLTV 2399413, 17:00 UTC start) had not appeared in HLTV's event results when this was written \u2014 checked at 20:05 UTC on 16 October \u2014 and Polymarket's market 5763247 was still accepting orders at 19:34 UTC. The semi-final 2 opponent is therefore unknown and no pick or percentage is published for it.",
        "No betting line existed for either semi-final 2 possibility at the 19:35 UTC check: Polymarket had no Falcons event for 17 October, and Pinnacle's 'CS2 - TP World Championship' league listed only the decider matchup (1638481889) plus its live child.",
        "Hotspawn had listed neither semi-final, the 3rd-place decider (HLTV 2399416) nor the best-of-five grand final (HLTV 2399417) at the 19:35 UTC check, so the board publishes no pick for any of them yet. Discovery is automatic and runs hourly.",
        "The 3rd-place decider and grand final have no teams at all yet, so nothing about them can be priced.",
        "Valve's standings file is dated 2026-10-05 (commit eec4853), which predates this week's results. Every model percentage here is a comparison beside market lines, never a market price and never an override of one.",
        "Aurora's roster has been unchanged since 8 July 2026, so no onboarding, stand-in or rest factor is available for day four; anyone reasoning from a 'recent Aurora roster change' is reasoning from a change that happened three months ago.",
    ],
}

data = json.loads(PATH.read_text())
if 'day_four_guidance' in data:
    raise SystemExit('day_four_guidance already present')
data['day_four_guidance'] = day_four
data['reviewed_at'] = '2026-10-16'
data['reviewed_at_utc'] = '2026-10-16T20:20:00Z'
data['note'] = data['note'] + (
    " Day-4 block added 16 October 2026 (UTC) by session 621776e4: day-1/2/3 results re-read from HLTV's event results page "
    "(https://www.hltv.org/results?event=8932), the semi-final line read from Polymarket's official API at 19:35 UTC "
    "(market 5778024, receipts in research/harvest-621776e4/), the semi-final starts taken from HLTV's machine-readable "
    "timestamps, and the Aurora roster premise checked against HLTV news 45082 and dated to 8 July 2026.")
PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
print('day_four_guidance written:', len(data['day_four_guidance']['points']), 'points,',
      len(data['day_four_guidance']['fixtures']), 'fixtures,', len(data['day_four_guidance']['not_listed']), 'cards')
