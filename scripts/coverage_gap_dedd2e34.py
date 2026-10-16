"""Coverage gap check: what Hotspawn lists versus an independent schedule.

This project may only price fixtures the Hotspawn feed lists, so a fixture that
exists on the tournament schedule but not on the board is invisible to the pick
list - it cannot be picked and scores nothing. That distinction matters to the
user and has to be measured, not remembered, so this script recomputes it from
live sources on every run:

1. the Hotspawn CS2 fixture API, exactly as the collector reads it;
2. HLTV's event match list for the Thunderpick World Championship 2026.

Rows are matched on exact normalized team pairs plus the exact UTC start, using
the same identity rules as the collector (no fuzzy aliasing). Anything found on
HLTV but not on Hotspawn is published as a gap with its source link; anything on
Hotspawn but not on the HLTV page is reported as unmatchable-by-this-method,
because the HLTV page covers one event only.

Read-only. It never writes to data/ or public/ and never produces a
probability. It exists for research and for the analysis page's gap section.
"""
import argparse
import datetime
import json
import pathlib
import re
import sys

from bs4 import BeautifulSoup

from scripts.core import dt, iso, norm
from scripts.inventory import checked_rows

HOTSPAWN_FIXTURES = ('https://phpstack-1372681-6459848.cloudwaysapps.com'
                     '/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1')
EVENT = 'https://www.hltv.org/events/8932/matches'
BASE = 'https://www.hltv.org'
UA = {'User-Agent': 'Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)'}


def get(url, timeout=25):
    """Fetch through the collector's own client.

    HLTV answers 403 to a plain urllib request from the same egress but 200 to
    the session the collector uses, so the gap check must not invent its own
    HTTP path: reusing Sources makes a failure mean the same thing here as it
    does for the pipeline.
    """
    from scripts.refresh import Sources
    body, receipt = Sources(datetime.datetime.now(datetime.timezone.utc)).get('Coverage gap source', url, as_json=url.endswith('.json') or 'fixtures?' in url)
    return body, {'Date': receipt.get('observed_at'), 'x-status': receipt.get('http_status')}


def hotspawn_ids():
    body, headers = get(HOTSPAWN_FIXTURES)
    rows = checked_rows(body if isinstance(body, list) else json.loads(body))
    observed = headers.get('Date')
    out = {}
    for row in rows:
        ident = str(row['id'])
        teams = [row.get('participants0_name'), row.get('participants1_name')]
        start = row.get('scheduled_start_time')
        out[ident] = {
            'id': ident,
            'teams': teams,
            'key': tuple(sorted(map(norm, teams))) if all(teams) else None,
            'start': iso(start) if start else None,
            'lock': iso(row['lock_time']) if row.get('lock_time') else None,
            'competition': row.get('competition_name'),
            'tier': row.get('tier'),
            'status': row.get('status'),
        }
    return out, observed, rows


def hltv_matches(html):
    """Fixture entries on an HLTV event/matches page: names plus unix start."""
    soup = BeautifulSoup(html, 'html.parser')
    found = {}
    for anchor in soup.select('a.match-teams[href^="/matches/"]'):
        teams = [t.get_text(strip=True) for t in anchor.select('.match-teamname')]
        stamp = anchor.parent.select_one('.match-time[data-unix]') if anchor.parent else None
        if len(teams) != 2 or stamp is None:
            continue
        url = BASE + anchor['href']
        found[url] = {'teams': teams, 'start': iso(stamp['data-unix']), 'url': url,
                      'key': tuple(sorted(map(norm, teams)))}
    if not found:
        raise ValueError('HLTV event page selectors returned no fixtures; page changed or access denied')
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='runtime/coverage-gap.json')
    parser.add_argument('--markdown', default='runtime/coverage-gap.md')
    parser.add_argument('--hltv-file', default=None,
                        help='Optional saved HLTV page (for offline replay in tests)')
    args = parser.parse_args()
    now = datetime.datetime.now(datetime.timezone.utc)
    problems = []
    board, board_date, board_rows = {}, None, []
    try:
        board, board_date, board_rows = hotspawn_ids()
    except Exception as exc:  # recorded, never guessed around
        problems.append({'source': HOTSPAWN_FIXTURES, 'error': str(exc)[:300]})
    schedule = {}
    try:
        if args.hltv_file:
            page = pathlib.Path(args.hltv_file).read_text()
        else:
            page, _ = get(EVENT)
        schedule = hltv_matches(page)
    except Exception as exc:
        problems.append({'source': EVENT, 'error': str(exc)[:300]})

    board_pairs = {tuple(sorted({norm(t) for t in row['teams']})) for row in board.values()
                   if all(row['teams'])}
    board_starts = {(row['start'] or '') for row in board.values()}
    gaps, matched = [], []
    for url, row in sorted(schedule.items(), key=lambda kv: (kv[1]['start'], kv[0])):
        key = tuple(sorted({norm(t) for t in row['teams']}))
        pair_on_board = key in board_pairs
        start_on_board = row['start'] in board_starts
        if pair_on_board and start_on_board:
            matched.append({'fixture': row, 'match': 'exact pair and UTC start present on the board'})
        elif pair_on_board:
            gaps.append({**row, 'url': url, 'kind': 'pair_listed_other_start',
                         'note': 'Hotspawn lists this pair but not at this UTC start; schedule may differ.'})
        else:
            gaps.append({**row, 'url': url, 'kind': 'absent_from_board',
                         'note': 'On the HLTV event schedule but not in the Hotspawn CS2 feed at this check, '
                                 'so this project cannot list a pick row for it and it scores no points.'})
    for row in board.values():
        if row['key'] and row['key'] not in {r['key'] for r in schedule.values()}:
            gaps.append({'teams': row['teams'], 'start': row['start'], 'id': row['id'],
                         'kind': 'board_only', 'url': 'https://play.hotspawn.com/cs2-pickems',
                         'note': 'On the Hotspawn board but outside this HLTV event page; not a defect, '
                                 'the schedule compared here covers one event only.'})
    open_board = [row for row in board.values()
                  if row['lock'] and dt(row['lock']) > now and row['status'] == 'scheduled']
    payload = {
        'checked_at': iso(now),
        'method': ('Exact normalized team-pair identity plus exact UTC start. Same identity rule as the '
                   'collector: no fuzzy aliasing, no assumed schedule corrections.'),
        'hotspawn': {'url': HOTSPAWN_FIXTURES, 'rows': len(board_rows), 'source_date_header': board_date,
                     'open_by_lock': len(open_board)},
        'hltv': {'url': EVENT, 'fixtures': len(schedule)},
        'matched': matched,
        'gaps': [g for g in gaps if g['kind'] != 'board_only'],
        'board_only_count': sum(1 for g in gaps if g['kind'] == 'board_only'),
        'problems': problems,
    }
    out = pathlib.Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1, sort_keys=True) + '\n')
    lines = ['# Hotspawn board versus HLTV schedule - coverage gap check', '',
             'Checked %s · method: %s' % (payload['checked_at'], payload['method']), '',
             '| Teams | UTC start | Kind | Note | Source |', '| --- | --- | --- | --- | --- |']
    for gap in payload['gaps']:
        lines.append('| %s | %s | %s | %s | %s |' % (' vs '.join(gap['teams']), gap['start'] or '',
                                                     gap['kind'], gap['note'], gap['url']))
    if not payload['gaps']:
        if problems:
            lines.append('| (not measured) |  |  | This check could not read both sources, so no coverage '
                         'conclusion is drawn from it. See the access problems below. | %s |' % EVENT)
        else:
            lines.append('| (no gap found) |  |  | Every HLTV fixture on this event page is on the board. | %s |' % EVENT)
    if not problems:
        lines += ['', 'Hotspawn CS2 rows read: %d (open by lock: %d) · fixtures scheduled on this HLTV event page: %d · '
                  'board rows that are not on this event page: %d'
                  % (payload['hotspawn']['rows'], payload['hotspawn']['open_by_lock'], payload['hltv']['fixtures'],
                     payload['board_only_count']),
                  '', 'Read the last number as context, not as a gap: the board covers every CS2 event Hotspawn lists, '
                  'while this page lists one tournament, so those rows belong to other competitions. The direction that '
                  'matters is the other one - every fixture HLTV schedules for this event must appear on the board, and '
                  'a missing one is reported above as absent_from_board. A fixture HLTV has already finished is not on '
                  'its scheduled page at all, so a past series cannot be used to prove a board gap.', '']
    for problem in payload['problems']:
        lines.append('- Access problem at %s: %s' % (problem['source'], problem['error']))
    pathlib.Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(args.markdown).write_text('\n'.join(lines) + '\n')
    print(json.dumps({'gaps': len(payload['gaps']), 'matched': len(matched),
                      'problems': len(problems)}, sort_keys=True))
    return 0 if not problems else 3


if __name__ == '__main__':
    raise SystemExit(main())
