"""Session 37bf28f4: apply the verified 17 October day-4 block to data/analysis.json.

Run once:

    python -m scripts.twc_day4_37bf28f4

What this changes and why (all of it re-read from primary sources on 17 October 2026
between 00:50Z and 01:10Z; raw field-level receipts in research/harvest-37bf28f4/
day4-live-reads.json):

1. Scoring. Hotspawn's official how-it-works page states that players earn "bonus
   points for consecutive correct picks" and that "the longer your streak, the bigger
   the bonus", with the leaderboard resetting weekly. The day-4 block previously said
   only that a correct pick scores a fixed award. Both are true and the second one is
   the one that changes the contrarian argument, so the block now carries both: the
   fixed, crowd-independent award (re-read from the fixtures API's own
   points_breakdown fields) and the streak bonus on top.
2. Sunday. HLTV's machine-readable start timestamps put the third-place decider at
   2026-10-18T11:30:00Z (best of three) and the grand final at 2026-10-18T15:00:00Z
   (best of five, the event's only five-map series). Neither had a market at the reads:
   Pinnacle carries no such matchup and a Polymarket slug search returns no event. They
   are now published as an explicit unpriced list with their limitation, instead of the
   single "no teams at all yet" sentence the block carried before.
3. Withdrawal. The earlier "the higher-ranked side won eight of the ten series"
   sentence depended on a dated ranking snapshot that could not be re-read from a
   primary source this session, so it is withdrawn and the verified structural facts
   (six of ten series were 2-0; both opening-match losers are semi-finalists; the only
   repeat pairing split 1-1) are published in its place.

Nothing is inferred: every number here is either copied from a source field or is a
count of results read from HLTV's event results list. No probability is created.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / 'data' / 'analysis.json'

FIXTURES_API = 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1'
HOW_IT_WORKS = 'https://play.hotspawn.com/how-it-works'
RESULTS = 'https://www.hltv.org/results?event=8932'
SCHEDULE = 'https://www.hltv.org/events/8932/matches'
GRAND_FINAL = 'https://www.hltv.org/matches/2399417/thunderpick-world-championship-2026-grand-final-thunderpick-world-championship-2026'
THIRD_PLACE = 'https://www.hltv.org/matches/2399416/thunderpick-world-championship-2026-3rd-place-decider-match-thunderpick-world-championship-2026'
UNRESOLVED = 'https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html'

SCORING_FIXED = {
    'claim': 'Scoring: points come from tier, stage and format - never from how the crowd split.',
    'detail': (
        "Hotspawn's published rules pay points for correct picks and state that higher-tier matches "
        "reward more. Its own fixtures API carries the arithmetic: every CS2 row exposes base_points, "
        "offered_points and a points_breakdown object with game, tier, series, stage and tournament "
        "multipliers. Re-read on 17 October at 00:50 UTC, tier c rows offered 2 points at multipliers "
        "1.25 / 1 / 1 / 1 / 1 and tier b rows offered 3 at 1.25 / 1.5 / 1 / 1 / 1. None of those fields "
        "depends on the participants0_picked_percent crowd figure, so a pick that fades the crowd earns "
        "exactly the same as one that follows it when it is right."
    ),
    'source': FIXTURES_API,
}

STREAK_BONUS = {
    'claim': "The streak bonus is not on these semi-finals at all - it is on the board the pick'em scores.",
    'detail': (
        "Hotspawn's official rules pay a bonus for consecutive correct picks ('the longer your streak, "
        "the bigger the bonus'; the exact formula is not published, so no number is claimed - see the "
        "strategy rules below) and resets the leaderboard weekly. Points exist only for fixtures on "
        "Hotspawn's own board, and neither Thunderpick semi-final is on that feed: today's read of the "
        "CS2 feed again returned no main-event playoff fixture, only the separate South American Series "
        "qualifier. So a TWC pick made from this page scores nothing in the pick'em, and a lost underdog "
        "that costs a streak can only ever be a board row - the tier-S, tier-B and tier-C fixtures on the "
        "picks page. That is why the contrarian call on a board row is treated more strictly here than "
        "the research read on a semi-final."
    ),
    'source': HOW_IT_WORKS,
}

SUNDAY = {
    'claim': "Sunday's two remaining matches are fixed on the calendar and unpriced on both books.",
    'detail': (
        "HLTV's machine-readable start timestamps give the third-place decider 2026-10-18T11:30:00Z and "
        "the grand final 2026-10-18T15:00:00Z, and its schedule page lists the decider as best of three "
        "and the grand final as a best of five - the only five-map series at this event. Both fixtures "
        "have no participants until the semi-finals end, and neither operator had opened them at the "
        "17 October 00:50-01:00 UTC reads: Pinnacle's esports feed carries no such matchup and a "
        "Polymarket slug search returns no event. They are published as unpriced, not given a "
        "placeholder percentage."
    ),
    'source': GRAND_FINAL,
}

GROUP_STRUCTURE = {
    'claim': 'Day one had no predictive value inside these groups: both opening-match losers are semi-finalists.',
    'detail': (
        'Ten series were played across 14-16 October: six finished 2-0 and four needed a third map. '
        'Aurora and BETBOOM both lost their opening series and then won their next two to reach the '
        'semi-finals, while the two group winners, Falcons and FURIA, went unbeaten through the group. '
        '9z-Aurora is the only pairing that met twice and it split 1-1. The event has therefore been '
        'noisy rather than inverted: the opening day did not predict the groups, but the favourites have '
        'not been overturned in bulk either.'
    ),
    'source': RESULTS,
}

UPSET_OUTLIER = {
    'claim': 'The day-one upset is not evidence that upsets pay.',
    'detail': (
        "9z's win was the event's outlier: the same pairing reversed 2-0 two days later when Aurora won "
        "the Group A decider, so the two teams split their Malta meetings 1-1. An earlier version of this "
        "bullet also claimed that the higher-ranked side won eight of the ten series on days 1-3; that "
        "sentence was withdrawn on 17 October because the dated ranking snapshot behind it could not be "
        "re-read from a primary source this session, and this project does not republish an unverifiable "
        "count. The underlying results, scores and group structure are verified and published instead."
    ),
    'source': RESULTS,
}

DAY2_AURORA = {
    'claim': 'Day 2: Aurora survived elimination 2-0 against Ninjas in Pyjamas.',
    'detail': (
        'Group A elimination match, verified map by map on the match page: Cache 13-9 (halves 7:5, 6:4) '
        'and Dust2 13-7 (9:3, 4:4). Ninjas in Pyjamas picked Cache, Aurora picked Dust2, and Nuke was the '
        'leftover map that was never played. Wicadia topped the server for Aurora with 45-25 kills and a '
        '1.65 rating. Aurora therefore arrived at the day-three decider 1-1.'
    ),
    'source': 'https://www.hltv.org/matches/2399408/aurora-vs-ninjas-in-pyjamas-thunderpick-world-championship-2026',
}

DAY2_SERIES = {
    'claim': "Day 2: both winners' matches went the distance, which is where the seeded order started to slip.",
    'detail': (
        'Falcons beat 9z 2-1 in the Group A winners\' match and FURIA beat Legacy 2-1 in the Group B '
        'winners\' match, while BETBOOM beat PARIVISION 2-1 in the Group B elimination match. Together with '
        'Aurora\'s 2-0, three of the day\'s four series needed a third map, against four 2-0 sweeps on day one.'
    ),
    'source': RESULTS,
}

NEW_UNVERIFIED = [
    "The sentence 'the higher-ranked side won eight of the ten series' that appeared in an earlier day-four block was withdrawn on 17 October: it depends on each team's rank on the day of each series, and no primary ranking snapshot with that granularity was re-read this session. Results, scores and the group structure are verified and published in its place.",
    "Lock-time wording is inconsistent between Hotspawn's own surfaces: the how-it-works page says picks lock '5 minutes before the scheduled start time', while every CS2 row of the fixtures API read on 17 October carries lock_offset_sec 360, i.e. six minutes. This board uses the API's per-fixture lock_time, which is the earlier and therefore the more conservative of the two. The discrepancy is recorded rather than smoothed over.",
    "Liquipedia has no page for this event ('There is currently no text in this page.' at /counterstrike/Thunderpick_World_Championship/2026, read 17 October), so there is no wiki cross-check available for the schedule, rosters or results. Everything published about this event comes from HLTV match pages, the operators' own APIs and Valve's official standings.",
    "Sunday's start times come from HLTV's machine-readable start_unix values captured on 16 October at 23:52 UTC, plus the formats on its schedule page. HLTV renders match clocks in the reader's own timezone, so the clock text on the page (10:00 and 13:00 for the semi-finals in this session's UTC-4 read) is never used as a time source.",
]

UNPRICED = [
    {
        'label': 'Thunderpick World Championship 2026 - third-place decider',
        'when': 'Sun 18 Oct · 11:30 UTC · best of 3',
        'status': 'Unpriced - participants not yet determined',
        'limitation': (
            'Both semi-final losers play this match, so the teams do not exist until the semi-finals finish. '
            'No market was open at the 17 October 00:50-01:00 UTC reads (Pinnacle esports feed: no such matchup; '
            'Polymarket slug search: no event). No percentage is published for a fixture whose participants are '
            'unknown: the pick board prices what a source can support, or leaves the line blank and labels it. '
            'The row will be priced as soon as the teams and a market exist.'
        ),
        'sources': [
            {'url': THIRD_PLACE, 'label': 'HLTV third-place decider (start_unix 2026-10-18T11:30:00Z)'},
            {'url': SCHEDULE, 'label': 'HLTV event schedule (bo3)'},
        ],
    },
    {
        'label': 'Thunderpick World Championship 2026 - grand final',
        'when': 'Sun 18 Oct · 15:00 UTC · best of 5',
        'status': 'Unpriced - participants not yet determined',
        'limitation': (
            "The event's only five-map series, which the win probabilities on the semi-final cards are not "
            'calibrated for (they price a best-of-three). Participants are unknown until the semi-finals finish, '
            'so there is no market to read and no percentage is published.'
        ),
        'sources': [
            {'url': GRAND_FINAL, 'label': 'HLTV grand final (start_unix 2026-10-18T15:00:00Z)'},
            {'url': SCHEDULE, 'label': 'HLTV event schedule (bo5)'},
        ],
    },
    {
        'label': 'Every other open Hotspawn fixture in this project',
        'when': 'Any time on the board',
        'status': 'Priced by our model line, or a labelled research pick with no percentage',
        'limitation': (
            'Where no market line passes the project gates, the row carries either our originated VRS model '
            'estimate (Valve standings through Valve\'s own formula, labelled on the row, never presented as a '
            'market price) or an HLTV-verified ranking-order pick with blank probabilities. Access checks for '
            'GG.BET, Thunderpick and Oddschecker are recorded, not bypassed. Every such row, with the gate it '
            'failed, is listed on the unresolved page.'
        ),
        'sources': [
            {'url': UNRESOLVED, 'label': 'Unresolved & non-market picks on this site'},
            {'url': 'https://buffedlizard55-lab.github.io/MaltaProj4/sources.html#method', 'label': 'Sources & methodology'},
        ],
    },
]

CARD = ("Both semi-finals are priced (14:00 and 17:00 UTC) with the exchange line, a sharp bookmaker "
        "cross-check and our model line, while the third-place decider and the event's only best-of-five "
        "grand final are fixed for Sunday but unpriced, and Hotspawn's streak bonus changes what a lost "
        "underdog pick really costs.")

SUMMARY_ADDITION = (" Sunday is already fixed and still unpriced: the third-place decider at 11:30 UTC and the "
                    "grand final at 15:00 UTC, best of five, both waiting on the semi-finals for their teams. "
                    "Hotspawn's own published rules also pay bonus points for consecutive correct picks, which is "
                    "the strongest argument on this page for leaving a contrarian lean alone unless the price is "
                    "genuinely wrong.")


def main():
    data = json.loads(ANALYSIS.read_text())
    plan = data['day_four_guidance']

    plan['card'] = CARD
    # Idempotent: drop every previously appended copy of the addition, then append exactly one.
    summary = plan['summary']
    while SUMMARY_ADDITION.strip() and summary.rstrip().endswith(SUMMARY_ADDITION.strip()):
        summary = summary.rstrip()[: -len(SUMMARY_ADDITION.strip())].rstrip()
    plan['summary'] = summary.rstrip() + SUMMARY_ADDITION

    # The same withdrawn count also appears in the block's own limitations list, written by an
    # earlier session. Keep the verified half of that sentence and drop the count there too, so
    # the page never states a number in one place and withdraws it in another.
    retired = ('The day-one upset remains an outlier, not a pattern: the same pairing reversed 2-0 two days '
               'later, and the higher-ranked side took the series in eight of the ten series played on days '
               'one to three.')
    replacement = ('The day-one upset remains an outlier, not a pattern: the same pairing reversed 2-0 two days '
                   'later when Aurora won the Group A decider. The count of ranking-based results that an earlier '
                   'version of this block published alongside it was withdrawn on 17 October, for the reason '
                   'recorded below.')
    plan['unverified'] = [replacement if x == retired else x for x in plan['unverified']]

    # Idempotent: this script owns the scoring, streak, Sunday and group-structure notes and the
    # rewritten upset note. Every other point another session published is preserved verbatim, in
    # its original position.
    managed = {SCORING_FIXED['claim'], STREAK_BONUS['claim'], SUNDAY['claim'], GROUP_STRUCTURE['claim'],
               UPSET_OUTLIER['claim'], DAY2_AURORA['claim'], DAY2_SERIES['claim']}
    legacy = [p['claim'] for p in plan['points']
              if 'fixed award' in p['claim'] or 'never from how the crowd' in p['claim']
              or p['claim'].startswith('A streak bonus sits on top')
              # Replaced: this one sentence mixed the verified map detail (now sourced to the match
              # page) with series scores that only the results list carries.
              or p['claim'].startswith('Day 2: Aurora survived elimination and 9z took a map')]
    kept = [p for p in plan['points'] if p['claim'] not in managed and p['claim'] not in legacy]
    ordered, inserted = [], False
    for point in kept:
        if (not inserted) and point['claim'].startswith('Day 3: Aurora beat 9z 2-0'):
            ordered.extend([DAY2_AURORA, DAY2_SERIES])
        if (not inserted) and point['claim'].startswith('The day-one upset is not evidence'):
            ordered.extend([SCORING_FIXED, STREAK_BONUS, UPSET_OUTLIER])
            inserted = True
            continue
        ordered.append(point)
    if not inserted:
        ordered.extend([SCORING_FIXED, STREAK_BONUS, UPSET_OUTLIER])
    ordered.extend([SUNDAY, GROUP_STRUCTURE])
    plan['points'] = ordered
    replaced = bool(legacy)

    for entry in NEW_UNVERIFIED:
        if entry not in plan['unverified']:
            plan['unverified'].append(entry)
    plan['unpriced_label'] = 'Unresolved & limitations - what has no price yet'
    plan['unpriced'] = UNPRICED

    ANALYSIS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({
        'replaced_fixed_award_point': replaced,
        'points': [p['claim'] for p in plan['points']],
        'unverified': len(plan['unverified']),
        'unpriced': [u['label'] for u in plan['unpriced']],
    }, indent=2))


if __name__ == '__main__':
    main()
