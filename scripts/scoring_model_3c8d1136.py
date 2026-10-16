"""Is Hotspawn's pick-em scoring fixed-points or pool-split? (session 3c8d1136)

The user's question - "how do we climb the leaderboard with contrarian but not stupid
picks" - has a different answer depending on how Hotspawn scores a correct pick. If a
fixture's points are split among everyone who picked correctly, fading the crowd has
value on its own. If the points are fixed, expected score is simply
``offered_points x P(win)``, the crowd split is irrelevant to the score, and the only
edge available is a better probability.

Hotspawn's own public fixture payload carries the arithmetic needed to test this, so it
is tested rather than assumed: ``base_points`` and ``points_breakdown``
(``game_multiplier``, ``tier_multiplier``, ``series_multiplier``, ``stage_multiplier``,
``tournament_multiplier``) against the published ``offered_points``, plus the crowd fields
``total_picks`` and ``participants*_picked_percent``.

This script reads a retained raw response and reports, without editing anything:

* whether ``offered_points == floor(base_points x product(multipliers))`` for every row;
* whether ``offered_points`` varies with crowd volume inside a group of fixtures that
  share tier, stage, best-of and competition (a pool-split would vary, a fixed award
  would not);
* the range of ``total_picks`` observed inside each such group, so a reader can see how
  much crowd volume changed without the award changing.

Nothing here is a probability and no crowd percentage is ever used as one.
"""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

MULTIPLIERS = ('game_multiplier', 'tier_multiplier', 'series_multiplier',
               'stage_multiplier', 'tournament_multiplier')


def rows_of(payload):
    if isinstance(payload, dict):
        payload = payload.get('data') or payload.get('fixtures') or []
    if not isinstance(payload, list):
        raise ValueError('Unrecognized fixture payload; no scoring claim is made')
    return [r for r in payload if isinstance(r, dict) and r.get('sport_alias') == 'cs2']


def predicted(row):
    breakdown = row.get('points_breakdown') or {}
    base = row.get('base_points')
    if base is None or not all(isinstance(breakdown.get(k), (int, float)) for k in MULTIPLIERS):
        return None
    product = base
    for key in MULTIPLIERS:
        product *= breakdown[key]
    return product


def analyse(rows):
    checked, formula_holds, formula_breaks, undetermined = [], [], [], []
    for row in rows:
        expected = predicted(row)
        offered = row.get('offered_points')
        if expected is None or offered is None:
            undetermined.append({'id': row.get('id'), 'offered_points': offered,
                                 'base_points': row.get('base_points'),
                                 'points_breakdown': row.get('points_breakdown')})
            continue
        record = {'id': row.get('id'), 'competition_name': row.get('competition_name'),
                  'tier': row.get('tier'), 'stage': row.get('stage'), 'best_of': row.get('best_of'),
                  'series_format': row.get('series_format'), 'base_points': row.get('base_points'),
                  'points_breakdown': row.get('points_breakdown'), 'offered_points': offered,
                  'predicted_points': expected, 'floor_predicted': math.floor(expected),
                  'total_picks': row.get('total_picks'),
                  'picked_percent': [row.get('participants0_picked_percent'),
                                     row.get('participants1_picked_percent')]}
        checked.append(record)
        (formula_holds if math.floor(expected) == offered else formula_breaks).append(record)

    groups = defaultdict(list)
    for record in checked:
        groups[(record['tier'], record['stage'], record['best_of'], record['series_format'],
                record['base_points'], json.dumps(record['points_breakdown'], sort_keys=True))].append(record)
    group_report = []
    for key, members in sorted(groups.items(), key=lambda item: -len(item[1])):
        awards = {m['offered_points'] for m in members}
        picks = [m['total_picks'] for m in members if isinstance(m['total_picks'], int)]
        group_report.append({'tier': key[0], 'stage': key[1], 'best_of': key[2],
                             'series_format': key[3], 'base_points': key[4],
                             'points_breakdown': json.loads(key[5]), 'fixtures': len(members),
                             'distinct_offered_points': sorted(awards),
                             'total_picks_min': min(picks) if picks else None,
                             'total_picks_max': max(picks) if picks else None,
                             'example_ids': [m['id'] for m in members[:4]]})
    varying = [g for g in group_report if len(g['distinct_offered_points']) > 1]
    crowd_spread = [g for g in group_report
                    if g['total_picks_min'] is not None and g['total_picks_max'] is not None
                    and g['total_picks_max'] > g['total_picks_min']
                    and len(g['distinct_offered_points']) == 1]
    return {
        'cs2_rows': len(rows),
        'rows_with_scoring_fields': len(checked),
        'formula_floor_base_times_multipliers_holds': len(formula_holds),
        'formula_exceptions': formula_breaks,
        'rows_without_scoring_fields': undetermined,
        'groups_by_tier_stage_format': group_report,
        'groups_where_the_award_varies': varying,
        'groups_where_crowd_volume_varied_but_the_award_did_not': crowd_spread,
        'conclusion': (
            'Every CS2 fixture publishes offered_points = floor(base_points x the five '
            'points_breakdown multipliers), and the award does not move where crowd volume '
            'does: %d of %d scoring groups show a different total_picks range with one single '
            'award. On this evidence a correct pick is worth a fixed number of points, so the '
            'leaderboard-optimal pick is the higher-probability team and a crowd split adds no '
            'score of its own. This is inferred from Hotspawn\'s own public fixture payload; an '
            'official Hotspawn rules page would outrank it.'
            % (len(crowd_spread), len(group_report))
            if checked and not varying and not formula_breaks and crowd_spread else
            'The fixed-award reading is NOT established by this payload: see '
            'formula_exceptions and groups_where_the_award_varies before drawing any '
            'conclusion about contrarian value.'),
    }


def markdown(rep):
    lines = ['# Does a correct Hotspawn pick score fixed points, or a share of a pool?', '',
             'Read from Hotspawn\'s own public fixture payload (retained raw response). '
             'No crowd percentage is used as a probability anywhere in this project.', '',
             '- CS2 rows read: **%d**' % rep['cs2_rows'],
             '- rows carrying `base_points` + `points_breakdown` + `offered_points`: **%d**' % rep['rows_with_scoring_fields'],
             '- rows where `offered_points == floor(base_points x the five multipliers)`: **%d**' % rep['formula_floor_base_times_multipliers_holds'],
             '- exceptions to that formula: **%d**' % len(rep['formula_exceptions']),
             '- rows missing a scoring field (left blank, never inferred): **%d**' % len(rep['rows_without_scoring_fields']),
             '- scoring groups (tier, stage, best-of, series format, base points, multipliers): **%d**' % len(rep['groups_by_tier_stage_format']),
             '- groups where the award varies: **%d**' % len(rep['groups_where_the_award_varies']),
             '- groups where crowd volume varies but the award does not: **%d**' % len(rep['groups_where_crowd_volume_varied_but_the_award_did_not']),
             '', '## Scoring groups', '',
             '| Tier | Stage | Best of | Fixtures | Award(s) | `total_picks` range | Multipliers | Example fixtures |',
             '|---|---|---|---|---|---|---|---|']
    for group in rep['groups_by_tier_stage_format']:
        lines.append('| %s | %s | %s | %d | %s | %s–%s | %s | %s |' % (
            group['tier'], group['stage'], group['best_of'], group['fixtures'],
            ', '.join(str(a) for a in group['distinct_offered_points']),
            group['total_picks_min'], group['total_picks_max'],
            json.dumps(group['points_breakdown'], sort_keys=True),
            ', '.join(group['example_ids'])))
    if rep['formula_exceptions']:
        lines += ['', '## Exceptions to the formula', '',
                  '| Fixture | `base_points` | Multipliers | Predicted | Published |', '|---|---|---|---|---|']
        for row in rep['formula_exceptions']:
            lines.append('| %s | %s | %s | %s | %s |' % (row['id'], row['base_points'],
                                                         json.dumps(row['points_breakdown'], sort_keys=True),
                                                         row['predicted_points'], row['offered_points']))
    lines += ['', '## Conclusion', '', rep['conclusion'], '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures', default='research/harvest-3c8d1136/fixtures-raw.json')
    parser.add_argument('--output', default='research/coverage-3c8d1136/scoring-model.json')
    parser.add_argument('--markdown', default='research/coverage-3c8d1136/SCORING-MODEL.md')
    args = parser.parse_args()
    rows = rows_of(json.loads(Path(args.fixtures).read_text()))
    rep = analyse(rows)
    for target, payload in ((args.output, json.dumps(rep, indent=2, ensure_ascii=False, sort_keys=True) + '\n'),
                            (args.markdown, markdown(rep))):
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload)
    print(json.dumps({'cs2_rows': rep['cs2_rows'],
                      'rows_with_scoring_fields': rep['rows_with_scoring_fields'],
                      'formula_holds': rep['formula_floor_base_times_multipliers_holds'],
                      'formula_exceptions': len(rep['formula_exceptions']),
                      'rows_without_scoring_fields': len(rep['rows_without_scoring_fields']),
                      'scoring_groups': len(rep['groups_by_tier_stage_format']),
                      'groups_where_the_award_varies': len(rep['groups_where_the_award_varies']),
                      'groups_crowd_varied_award_did_not':
                          len(rep['groups_where_crowd_volume_varied_but_the_award_did_not'])}, indent=2))
    print(rep['conclusion'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
