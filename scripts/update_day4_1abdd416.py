"""Session 1abdd416: the day-4 semi-final enrichment, merged on top of session 1068802c.

Run once, after the 1068802c merge. It does not rewrite what that session published:
the day-3 result rows, the day-4 points list and every still-true caveat are kept
verbatim, and this script only adds the 23:52 UTC market captures, the picks, the
sharp-book cross-check and the caveats that the older text no longer reflects.

Sources read for this session's additions (2026-10-16/17 UTC):

* HLTV results, event 8932 ............... https://www.hltv.org/results?event=8932
* HLTV schedule, event 8932 .............. https://www.hltv.org/events/8932/matches
* HLTV match 2399412 (Aurora 2-0 9z) ..... scores, halves, veto, ratings
* HLTV match 2399413 (BETBOOM 2-1 Legacy)  scores, halves, veto, ratings
* HLTV match 2399414 / 2399415 .......... semi-final clocks, formats, lineups, VRS ranks
* HLTV news 45718 / 45739 / 45082 ....... day-one upset; decider report; Aurora roster dating
* Polymarket Gamma 5778024 / 5787759 .... semi-final moneylines, capture 23:51:16Z
* Pinnacle guest esports straight feed .. matchups 1638536356 / 1638595724, period 0
* Valve standings 2026-10-05, commit eec4853  points, rosters and the >=3-player rule
* Hotspawn CS2 fixtures feed (harvest) ... 83 rows at 23:52Z, no main-event TWC fixture

Raw responses: research/harvest-1abdd416/.
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / 'data/analysis.json'
IDENTITIES = ROOT / 'data/identities.json'

VALVE_COMMIT = 'eec4853d7bcf0f1f7efe7f0d901234bef7e98b75'
STANDINGS = ('https://github.com/ValveSoftware/counter-strike_regional_standings/blob/' + VALVE_COMMIT +
             '/live/2026/standings_global_2026_10_05.md')
RESULTS = 'https://www.hltv.org/results?event=8932'
HARVEST = 'research/harvest-1abdd416'

SIX_SIX_ALIAS = {
    "canonical": "6666",
    "names": ["6666", "ex-6666"],
    "source": ('https://github.com/ValveSoftware/counter-strike_regional_standings/blob/' + VALVE_COMMIT +
               '/live/2026/details/2026_10_05/0127--6666--amster-denzy-kl1o-rendysky-skch.md'),
    "additional_source": ('https://www.hltv.org/matches/2399681/'
                         'ex-6666-vs-privateer-cct-2026-challengers-europe-series-8'),
    "basis": (
        "Roster-parity mapping used only where a roster check is available, per Valve's own published rule "
        "(model/team.js, TEAM_OVERLAP_TO_SHARE_ROSTER = 3: rosters sharing at least three players are treated as "
        "the same team, verified at commit " + VALVE_COMMIT[:7] + "). Hotspawn's own feed uses both spellings for "
        "the club - '6666' in its June 2026 Urban Riga Open rows (fixture ids 1053439, 1053470 and 1053442) and "
        "'ex-6666' in the October CCT row (fixture 1081521) - but naming is not the evidence: the binding test is "
        "the roster overlap, which the model re-checks on every run. Valve's detail file for the 6666 standing at "
        "#127 lists amster, dENZY, kL1o, rendysky and skcH on 923.2 points; the HLTV fixture for CCT Europe 2026 "
        "Challengers #8 lists the team labelled ex-6666 as skcH, kL1o, amster, rendysky and stefienson, four shared "
        "players. The standings' other row labelled 6666 (#368, 424.5 points; auth0ri, m4d4ra, rickangel, skcH) "
        "shares one, so the overlap selects exactly one row and the model still refuses the label if the overlap or "
        "the uniqueness test fails. Scope: CS2 main-team label only, and an exact opponent pair plus UTC start is "
        "still required for any fixture."),
}

DAY4_CARDS = [
    {
        "label": "FURIA vs Aurora",
        "event": "Thunderpick World Championship 2026, semi-final 1 (best of 3, Malta)",
        "teams": ["FURIA", "Aurora"],
        "points": [1829, 1716],
        "now_listed": False,
        "pick": "FURIA",
        "pick_detail": ("Market 52.5% (Polymarket) and 53.0% (Pinnacle, de-margined): both market lines make FURIA "
                        "the favourite by a small margin, and our model makes it 62.2%. Aurora are the contrarian "
                        "side at 47-48% \u2014 a coin flip, not a long shot."),
        "market": {
            "label": "Polymarket moneyline, market 5778024, capture 23:52 UTC 16 October",
            "detail": ("FURIA 52.5% / Aurora 47.5% \u2014 outcome prices 0.525 / 0.475, best bid 0.52, best ask 0.53 "
                       "(1-point spread), $158,627.63 liquidity, accepting orders, market updated "
                       "2026-10-16T23:51:16Z, gameStartTime 2026-10-17 14:00 UTC. On the same event the map "
                       "handicap prices FURIA to win 2-0 at 28% (market 5778026), i.e. the market expects a "
                       "three-map series more often than not."),
            "url": "https://gamma-api.polymarket.com/markets/5778024",
            "link_label": "Official Polymarket market \u2197",
        },
        "book_line": {
            "label": "Pinnacle moneyline, matchup 1638536356, capture 23:52 UTC 16 October",
            "detail": ("FURIA -125 / Aurora +103 (decimal 1.80 / 2.03), whole-match market, status open, cutoff "
                       "2026-10-17T14:00:00Z. Overround 4.8%, inside the project's 25% bookmaker gate; de-margined "
                       "by the published method this is FURIA 53.0% / Aurora 47.0%. One sharp bookmaker is a "
                       "cross-check, not a consensus."),
            "url": "https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight",
            "link_label": "Pinnacle's public esports feed \u2197",
        },
        "timing": ("HLTV's machine-readable clock is 2026-10-17T14:00:00Z and Polymarket's own gameStartTime field "
                   "reads 2026-10-17 14:00:00+00, so the two sources agree on the start. Series format: best of 3 "
                   "(LAN)."),
        "why": ("Both the exchange and the sharp bookmaker call this a near coin flip, while our model (Valve's "
                "5 October standings, which predate this week) reads FURIA 62.2%. Aurora at 47-48% is the cheapest "
                "differentiation on the slate and the case is sourced rather than hopeful: they beat Ninjas in "
                "Pyjamas 2-0 on day two and 9z 2-0 in the Group A decider, and HLTV's head-to-head block on this "
                "fixture lists a 1-1 record over the last 30 days including an Aurora 2-1 win at ESL Pro League "
                "Season 24. FURIA answered with a 2-0 over BETBOOM on day one and a 2-1 over Legacy on day two. "
                "HLTV's own match page calls Aurora the bookmaker favourite with the better form ranking while the "
                "exchange and Pinnacle both price FURIA: the sources disagree on direction at the margin, and that "
                "disagreement is published rather than smoothed over. Leaderboard default: FURIA, because Hotspawn "
                "awards a fixed number of points per correct pick and the market's favourite is the "
                "higher-probability side. Contrarian side: Aurora, on the grounds that the market's edge is only "
                "about four points."),
        "hltv_url": "https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026",
        "standings_url": STANDINGS,
        "sources": [
            {"label": "HLTV: FURIA vs Aurora fixture page (clock, VRS ranks, lineups)",
             "url": "https://www.hltv.org/matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026"},
            {"label": "HLTV: Aurora 2-0 9z in the Group A decider",
             "url": "https://www.hltv.org/matches/2399412/aurora-vs-9z-thunderpick-world-championship-2026"},
            {"label": "HLTV: FURIA 2-1 Legacy (day two)",
             "url": "https://www.hltv.org/matches/2399411/legacy-vs-furia-thunderpick-world-championship-2026"},
            {"label": "HLTV: day-one upset report (9z 2-0 Aurora)",
             "url": "https://www.hltv.org/news/45718/9z-beat-aurora-2-0-to-kick-off-twc-2026"},
        ],
    },
    {
        "label": "Falcons vs BETBOOM",
        "event": "Thunderpick World Championship 2026, semi-final 2 (best of 3, Malta)",
        "teams": ["Falcons", "BETBOOM"],
        "points": [1843, 1596],
        "now_listed": False,
        "pick": "Falcons",
        "pick_detail": ("Market 79.5% (Polymarket) and 76.0% (Pinnacle, de-margined); our model 73.9%. BETBOOM at "
                        "20-24% are the only side with a scheduling argument, and that is the contrarian side of "
                        "the slate."),
        "market": {
            "label": "Polymarket moneyline, market 5787759, capture 23:52 UTC 16 October",
            "detail": ("Falcons 79.5% / BETBOOM 20.5% \u2014 outcome prices 0.795 / 0.205, best bid 0.79, best ask "
                       "0.80 (1-point spread), $60,452.33 liquidity on the moneyline ($183,300.98 on the event), "
                       "accepting orders, market updated 2026-10-16T23:51:16Z, gameStartTime 2026-10-17 17:00 UTC."),
            "url": "https://gamma-api.polymarket.com/markets/5787759",
            "link_label": "Official Polymarket market \u2197",
        },
        "book_line": {
            "label": "Pinnacle moneyline, matchup 1638595724, capture 23:52 UTC 16 October",
            "detail": ("Falcons -389 / BB Team +298 (decimal 1.257 / 3.98), whole-match market, status open, cutoff "
                       "2026-10-17T17:00:00Z. Overround 4.7%, inside the project's 25% bookmaker gate; de-margined "
                       "this is Falcons 76.0% / BB Team 24.0%. Pinnacle's label is BB Team, which the identity "
                       "register already maps to BetBoom from the organisation's own site."),
            "url": "https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight",
            "link_label": "Pinnacle's public esports feed \u2197",
        },
        "timing": ("HLTV's machine-readable clock and Polymarket's gameStartTime both read 2026-10-17T17:00:00Z. "
                   "Series format: best of 3 (LAN). BETBOOM qualified by beating Legacy 2-1 in the Group B decider "
                   "on 16 October."),
        "why": ("Every source agrees on direction here: the exchange says 79.5%, the sharp bookmaker 76.0% and our "
                "model 73.9%. The only sourced argument for the underdog is the schedule: BETBOOM have played on all "
                "three days so far (2-1 PARIVISION on 15 October, then the 2-1 decider over Legacy on 16 October), "
                "which is two three-map series in two days, while Falcons last played on 15 October. Rest is a "
                "structural observation from the fixture list, not a measured performance effect, and the market has "
                "to be wrong for the contrarian side to pay: the de-margined lines put BETBOOM between roughly 21% "
                "and 24%, so taking them is a deliberate swing and should be capped if taken at all. Leaderboard "
                "default: Falcons. Contrarian side: BETBOOM, at the outside edge of the 15-40% band."),
        "hltv_url": "https://www.hltv.org/matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026",
        "standings_url": STANDINGS,
        "sources": [
            {"label": "HLTV: Falcons vs BETBOOM fixture page (clock, VRS ranks, lineups)",
             "url": "https://www.hltv.org/matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026"},
            {"label": "HLTV: BETBOOM 2-1 Legacy in the Group B decider",
             "url": "https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026"},
            {"label": "HLTV: BETBOOM qualify for the playoffs over Legacy",
             "url": "https://www.hltv.org/news/45739/betboom-qualify-for-twc-playoffs-over-legacy"},
            {"label": "HLTV: BETBOOM 2-1 PARIVISION (day two)",
             "url": "https://www.hltv.org/matches/2399410/parivision-vs-betboom-thunderpick-world-championship-2026"},
        ],
    },
]

# Appended to the points list session 1068802c published; theirs stay verbatim.
DAY4_EXTRA_POINTS = [
    {"claim": "Day 3: both group deciders are now final \u2014 Aurora 2-0 9z and BETBOOM 2-1 Legacy.",
     "detail": ("Cache 13-11 (8:4, then 5:7) and Inferno 13-4 (9:3, then 4:1) closed Group A; Nuke 16-13 to BETBOOM "
                "in overtime (4:8, 8:4, 4:1), Dust2 13-11 to Legacy and Mirage 13-11 to BETBOOM decided Group B. "
                "An earlier session could only corroborate the Inferno 13-4 second-hand; both match pages now carry "
                "the scorelines and the veto, so that caveat is closed. The two semi-finalists who came through the "
                "deciders are the two teams with the shortest turnaround."),
     "source": "https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026"},
    {"claim": "The day-four rest difference is one day, and it belongs to BETBOOM.",
     "detail": ("BETBOOM played on 14, 15 and 16 October, including two three-map series on the last two days; "
                "Falcons and FURIA both last played on 15 October; Aurora played on 16 October (a 2-0). Read from "
                "HLTV's event results and schedule pages. It is a schedule observation, not a measured fatigue "
                "effect, and it is the only underdog-side argument the sources support for either semi-final."),
     "source": RESULTS},
]

# Corrections to text session 1068802c published that its own later work superseded.
POINT_FIXES = [
    ("Day 3: Aurora beat 9z 2-0 in the Group A decider",
     "The Inferno scoreline is published as 13-4 by dust2.com.br and EGamersWorld; this session did not re-verify "
     "that single map score on HLTV, so only the series score and the Cache result are treated as primary.",
     "The Inferno scoreline is 13-4 on HLTV's match page read on 16 October (9:3, then 4:1), so that single map "
     "score is primary here as well."),
]
KEEP_UNVERIFIED = {
    3: '3rd-place',
    4: 'standings file is dated 2026-10-05',
    5: 'unchanged since 8 July 2026',
    6: 'Two Valve-standings readings disagree',
    7: 'forecast of FURIA 26.5%',
    11: 'Rest and turnaround effects are structural',
    12: 'Map win-rates quoted',
}

FORECAST_FIX = (
    "The Day-4 semis section on this page publishes a HLTV match-page forecast of FURIA 26.5% / Aurora 73.5%.",
    "An earlier session published a HLTV match-page forecast of FURIA 26.5% / Aurora 73.5% for this fixture and "
    "flagged it as not captured. That number is withdrawn from this block rather than repeated: the HLTV "
    "odds-and-prediction page for match 2399414, read again on 17 October "
    "(https://www.hltv.org/betting/analytics/2399414/furia-vs-aurora-thunderpick-world-championship-2026), shows the "
    "two teams' pros and cons, the head-to-head, the veto and handicap tables and a bookmaker area whose extractor "
    "returns no numeric two-sided line, and the read did not reproduce a numeric forecast row. What HLTV's page does "
    "state is that Aurora is the bookmaker favourite with the better form ranking, which is reported as HLTV's view "
    "and is not used as a price or as a model input anywhere on this site.")

START_ITEM = (
    "The semi-final start times on this page are not inferred. HLTV's machine-readable start timestamps "
    "(2026-10-17T14:00:00Z and 2026-10-17T17:00:00Z, captured into research/harvest-1abdd416/) agree with "
    "Polymarket's own gameStartTime fields for both fixtures. The countdown clock HLTV displays on the page is "
    "UTC-4 for this event and is never used as a source.")

NEW_UNVERIFIED = [
    "Neither semi-final is on the Hotspawn CS2 feed. The 23:52 UTC harvest on 16 October returned 83 rows and no "
    "main-event Thunderpick World Championship fixture (the feed carries only the separate 'Thunderpick World "
    "Championship 2026: South American Series #1'), so no board pick, tier or points value is published for the "
    "semi-finals and discovery continues hourly.",
    "HLTV's odds comparison table returned zero numeric bookmaker rows on both semi-final pages in the 23:52 UTC "
    "capture (research/harvest-1abdd416/hltv-twc-2399414.json and -2399415.json carry an empty betting list), and "
    "the DOM diagnostic on two other pages shows the only .provider row is a Stake promotion with no odds cells. No "
    "HLTV bookmaker line is published here, and the absence is recorded as a retrieval limitation rather than as "
    "'no odds exist'.",
    "Pinnacle's line is single-book. It is a sharp cross-check with a 4.7-4.8% overround, not a consensus, and the "
    "project publishes the de-margined value as its own calculation on top of the bookmaker's raw American prices.",
    "Pinnacle's labels are matched by exact matchup and league (CS2 - TP World Championship) plus the UTC cutoff, "
    "because 'FURIA' and '9z' also appear in Pinnacle's other sports. 'BB Team' is mapped to BetBoom by the identity "
    "register, whose source is the organisation's own site.",
    "The day-one upset remains an outlier, not a pattern: the same pairing reversed 2-0 two days later, and the "
    "higher-ranked side took the series in eight of the ten series played on days one to three.",
]

DAY4_NOTE_APPENDIX = (
    " Day-4 semi-final enrichment added on 16 October 2026 (UTC) by session 1abdd416, on top of session 1068802c's "
    "merge: the two semi-final cards now carry a pick, the exchange line captured at 23:52 UTC (Polymarket markets "
    "5778024 and 5787759), a de-margined Pinnacle cross-check (matchups 1638536356 and 1638595724, same capture) "
    "and the recomputed Valve-standings model lines. The weekday in the day-4 date label was corrected to Saturday. "
    "Raw responses: " + HARVEST + "/.")


def main():
    analysis = json.loads(ANALYSIS.read_text())
    identities = json.loads(IDENTITIES.read_text())
    day4 = analysis['day_four_guidance']

    if any(card.get('book_line') for card in day4['not_listed']):
        raise SystemExit('day-four cards already carry a book_line; refusing to run twice')

    existing = next((item for item in identities['aliases'] if item['canonical'] == '6666'), None)
    if existing is None:
        identities['aliases'].append(copy.deepcopy(SIX_SIX_ALIAS))
        identities['reviewed_at'] = '2026-10-16'
        IDENTITIES.write_text(json.dumps(identities, indent=2, ensure_ascii=False) + '\n')
    else:
        assert existing['names'] == SIX_SIX_ALIAS['names'], existing['names']

    # --- day 3: keep the published row, add the half scores read from the match page.
    for row in analysis['day_three_results']['matches']:
        if row['winner'] == 'BETBOOM' and 'halves' not in row['maps']:
            row['maps'] = ("Nuke 16-13 (halves 4:8; 8:4; 4:1 in overtime), Dust2 11-13 (7:5; 4:8), "
                           "Mirage 13-11 (7:5; 6:6)")

    # --- day 4: add to what session 1068802c published, replace only what is stale.
    points = copy.deepcopy(day4['points'])
    for point in DAY4_EXTRA_POINTS:
        assert all(point['claim'] != p['claim'] for p in points)
        points.append(point)

    for claim_prefix, stale, replacement in POINT_FIXES:
        point = next(p for p in points if p['claim'].startswith(claim_prefix))
        assert stale in point['detail'], point['detail'][:80]
        point['detail'] = point['detail'].replace(stale, replacement)

    unverified = []
    for index, needle in sorted(KEEP_UNVERIFIED.items()):
        item = day4['unverified'][index]
        assert needle in item, (index, item[:60])
        if index == 3:
            item = item + (" HLTV publishes them as matches 2399416 (third-place decider) and 2399417 (grand "
                           "final), both still without teams.")
        unverified.append(item)
    stale_forecast = next(u for u in unverified if FORECAST_FIX[0] in u)
    unverified[unverified.index(stale_forecast)] = FORECAST_FIX[1]
    unverified.append(START_ITEM)
    unverified.extend(NEW_UNVERIFIED)

    day4.update({
        "date": "Day 4 \u00b7 Saturday 17 October 2026",
        "nav_label": "Day-4 picks",
        "card": ("Both semi-finals are confirmed and priced: FURIA\u2013Aurora at 14:00 UTC and "
                 "Falcons\u2013BETBOOM at 17:00 UTC, each with the exchange line, a sharp bookmaker cross-check "
                 "and our own model line, plus the contrarian side and its price."),
        "headline": "Day-four picks: both semi-finals, priced from three independent sources",
        "summary": (
            "Semi-final day in Malta, and both semi-finals are fixed and priced. FURIA play Aurora at 14:00 UTC "
            "and Falcons play BETBOOM at 17:00 UTC, after BETBOOM beat Legacy 2-1 in the Group B decider on "
            "16 October. Each card below carries the exchange line (Polymarket's official API, captured 23:52 UTC), "
            "a sharp bookmaker cross-check (Pinnacle's public esports feed, same capture, de-margined by our "
            "published method) and our own Valve-standings model, so the three can be compared rather than blended. "
            "Neither semi-final is on Hotspawn's CS2 feed, so these are research guidance rather than board "
            "submissions and carry no tier or points value. Hotspawn awards a fixed number of points per correct "
            "pick, so the leaderboard-optimal choice is the higher-probability team unless there is a specific "
            "reason to believe the favourite is wrong: the pick is stated on each card, and the contrarian side of "
            "each fixture is given with its price and its sourced case. The day's only real underdog argument is "
            "BETBOOM's back-to-back three-map series. The fixtures table above this section covers the board rows "
            "Hotspawn does list for 17 October."),
        "points_label": "What day one to day three actually showed, re-verified from the match pages",
        "points": points,
        "not_listed": copy.deepcopy(DAY4_CARDS),
        "unverified": unverified,
    })

    analysis['reviewed_at'] = '2026-10-16'
    analysis['reviewed_at_utc'] = '2026-10-16T23:52:00Z'
    analysis['note'] = analysis['note'] + DAY4_NOTE_APPENDIX

    text = json.dumps(analysis, indent=2, ensure_ascii=False) + '\n'
    if text.count('"day_four_guidance"') != 1:
        raise SystemExit('duplicate day_four_guidance key')
    ANALYSIS.write_text(text)
    print('day-4 points:', len(points), '| cards:', len(day4['not_listed']),
          '| unverified:', len(unverified), '| day-3 rows:', len(analysis['day_three_results']['matches']))


if __name__ == '__main__':
    main()
