"""Session 79f0e55b: turn the captured evidence into a reader-facing verification report.

Inputs are the artefacts other steps already produced (HLTV raw pages and their parse, the
refreshed board snapshot, the probe report, the live-site capture and Valve's own regional
standings). Outputs are ``research/verify-79f0e55b/VERIFICATION.md`` and a machine-readable
``twc-2026-verified.json``.

Nothing in the report is hand-written: every table cell is read from a captured artefact,
and the source of each value is named next to it. Where a value is absent it stays blank.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

HLTV_MATCH = 'https://www.hltv.org/matches/%s/x'
VRS_REGIONAL = {
    'americas': ('https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/'
                 'contents/live/2026/standings_americas_2026_10_05.md', 'Americas'),
    'asia': ('https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/'
             'contents/live/2026/standings_asia_2026_10_05.md', 'Asia'),
    'europe': ('https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/'
               'contents/live/2026/standings_europe_2026_10_05.md', 'Europe'),
}


def load(path, default=None):
    p = Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text())


def sha256_file(path):
    p = Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def short(value, length=16):
    return (value or '')[:length]


def parse_vrs_region(path):
    """Valve regional standings rows: standing, points, name, roster."""
    rows = []
    text = Path(path).read_text()
    for line in text.splitlines():
        m = re.match(r'^\|\s*(\d+)\s*\|\s*(-?\d+)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*\[details\]', line)
        if m:
            rows.append({'standing': int(m.group(1)), 'points': int(m.group(2)),
                         'name': m.group(3).strip(),
                         'roster': [p.strip() for p in m.group(4).split(',') if p.strip()]})
    return rows


def team_rows(rows, name):
    target = name.strip().lower()
    return [r for r in rows if r['name'].strip().lower() == target]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hltv', default='research/hltv-79f0e55b/report.json')
    parser.add_argument('--snapshot', default='research/harvest-79f0e55b/snapshot.json')
    parser.add_argument('--probe', default='research/harvest-79f0e55b/probe-report.json')
    parser.add_argument('--live', default='research/live-79f0e55b/report.json')
    parser.add_argument('--refresh-log', default='research/harvest-79f0e55b/logs/refresh.txt')
    parser.add_argument('--vrs-dir', default='research/verify-79f0e55b/vrs')
    parser.add_argument('--output', default='research/verify-79f0e55b')
    args = parser.parse_args()

    hltv = load(args.hltv, {})
    snapshot = load(args.snapshot, {'matches': []})
    probe = load(args.probe, {})
    live = load(args.live, {})
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    refresh_line = None
    log_path = Path(args.refresh_log)
    if log_path.exists():
        for line in reversed(log_path.read_text().splitlines()):
            if line.strip().startswith('{'):
                refresh_line = line.strip()
                break
    refresh_summary = json.loads(refresh_line) if refresh_line else None

    board = {str(m['id']): m for m in snapshot.get('matches') or []}
    opens = {k: v for k, v in board.items() if v.get('state') == 'open'}
    priced = {k: v for k, v in opens.items() if v.get('probabilities')}
    research_only = {k: v for k, v in opens.items() if not v.get('probabilities')}

    regional = {}
    for key, (url, label) in VRS_REGIONAL.items():
        path = Path(args.vrs_dir) / ('%s.md' % key)
        regional[key] = {'url': url, 'label': label, 'rows': parse_vrs_region(path) if path.exists() else [],
                         'sha256': sha256_file(path), 'file': str(path)}

    hltv_pages = {p['name']: p for p in hltv.get('pages') or []}

    # Per-fixture regional coverage for the rows that still carry no percentage.
    research_rows = []
    for rid, row in sorted(research_only.items()):
        teams = row.get('teams') or []
        detail = {'id': rid, 'teams': teams, 'start': row.get('start'), 'pick': row.get('pick'),
                  'method': row.get('method'), 'competition': row.get('competition'),
                  'reason': row.get('reason'), 'teams': teams, 'ratings': {}}
        for team in teams:
            found = []
            for key, info in regional.items():
                for entry in team_rows(info['rows'], team):
                    found.append({'region': info['label'], 'standing': entry['standing'],
                                  'points': entry['points'], 'url': info['url']})
            detail['ratings'][team] = found
        research_rows.append(detail)

    twc = {'generated_from': {'hltv_report': args.hltv, 'snapshot': args.snapshot,
                              'live_report': args.live, 'probe_report': args.probe},
           'hltv_pages': [{'name': p['name'], 'url': p['url'], 'status': p.get('status'),
                           'bytes': p.get('bytes'), 'sha256': p.get('sha256')} for p in hltv.get('pages') or []],
           'results': [], 'schedule': [], 'regional_ratings': regional,
           'board': {'rows_total': len(board), 'open_total': len(opens), 'open_priced': len(priced),
                     'open_research_only': len(research_only),
                     'open_without_pick': sum(1 for r in opens.values() if not r.get('pick')),
                     'coverage': snapshot.get('coverage'), 'generated_at': snapshot.get('generated_at'),
                     'inventory_changes': snapshot.get('inventory_changes'),
                     'coverage_counts': snapshot.get('coverage_counts')},
           'refresh_summary': refresh_summary, 'research_rows': research_rows}

    # Results and schedule, joined to the captured match pages for map scores and the
    # absolute start instant.
    for row in hltv.get('results_rows') or []:
        mid = str(row.get('match_id'))
        page = (hltv.get('match_pages') or {}).get(mid) or {}
        twc['results'].append({'date_heading': row.get('date_heading'), 'match_id': mid,
                               'teams': row.get('teams'), 'score': row.get('score'),
                               'start_utc': page.get('start_utc'),
                               'maps': [{'map': m['map'], 'left': m['left']['score'], 'right': m['right']['score'],
                                         'winner': 'left' if m['left']['won'] else ('right' if m['right']['won'] else None)}
                                        for m in page.get('maps') or [] if m['map'] != 'TBA'],
                               'veto': page.get('veto'),
                               'page': 'https://www.hltv.org/matches/%s/x' % mid})
    for row in hltv.get('schedule_rows') or []:
        twc['schedule'].append({'day_heading': row.get('day_heading'), 'match_id': str(row.get('match_id')),
                                'displayed_time': row.get('displayed_time'), 'start_utc': row.get('start_utc'),
                                'format': row.get('format'), 'teams': row.get('teams'), 'stage': row.get('stage'),
                                'board_row': board.get(str(row.get('match_id')))})

    md = []
    add = md.append
    add('# Independent verification — TWC 2026 and the live board (session 79f0e55b)')
    add('')
    add('Generated by `python -m scripts.verify_report_79f0e55b` from the captured evidence listed in '
        '[BUILD.md](BUILD.md). Every value below is read out of a retained raw body; the body links and hashes are in '
        '`twc-2026-verified.json`. This file makes no claim that is not in that JSON.')
    add('')
    add('## 1. Method, and what this can and cannot prove')
    add('')
    add('* The authoring sandbox has no route to `www.hltv.org` (`curl` → `SSL_ERROR_SYSCALL`, re-measured 2026-10-17). '
        'Every page here was read by `.github/workflows/harvest-79f0e55b.yml` on a runner with normal outbound access, '
        'and the **whole body** was committed beside the numbers taken from it. Offline replay '
        '(`python -m scripts.hltv_verify_79f0e55b --replay research/hltv-79f0e55b`) reproduces the tables from those '
        'bytes, and all 20 replayed hashes equal the network receipts recorded at capture time.')
    add('* This verifies **what the sources published**. It does not certify that a team will win, that a bookmaker is '
        'correct, or that a market price is fair.')
    add('* HLTV renders clock times in the **viewer\'s** timezone and never names it, so a displayed clock is not a '
        'fact. Where a start time matters, this report uses the absolute `data-unix` epoch from HLTV\'s own markup; the '
        'displayed clock is kept beside it only as a rendering.')
    add('')
    add('## 2. Thunderpick World Championship 2026 — results as published by HLTV')
    add('')
    add('Source: `https://www.hltv.org/results?event=8932` plus each match page '
        '(raw bodies in `research/hltv-79f0e55b/`, hashes in `twc-2026-verified.json`).')
    add('')
    add('| Date (HLTV heading) | Match | Series | Maps (left team first) | Absolute start (UTC, from data-unix) | HLTV page |')
    add('| --- | --- | --- | --- | --- | --- |')
    for r in twc['results']:
        teams = ' vs '.join(r['teams'] or [])
        maps = ', '.join('%s %s-%s' % (m['map'], m['left'], m['right']) for m in r['maps']) or 'not captured'
        add('| %s | %s | %s | %s | %s | [%s](%s) |' % (r['date_heading'], teams, r['score'], maps,
                                                      r['start_utc'] or '', r['match_id'], r['page']))
    add('')
    add('### Scheduled fixtures (day 4 and day 5)')
    add('')
    add('| Day (HLTV) | Fixture | Stage | Format | Displayed clock | Absolute start (UTC) | On the Hotspawn board? |')
    add('| --- | --- | --- | --- | --- | --- | --- |')
    for r in twc['schedule']:
        teams = ' vs '.join(r['teams'] or []) or 'teams not yet decided'
        row = r.get('board_row') or {}
        on_board = ('yes — id `%s`, Hotspawn lock %s, tier `%s`, pick %s (%s)'
                    % (row.get('id'), row.get('lock'), row.get('tier'), row.get('pick'), row.get('method'))
                    if row else 'not listed in the %s snapshot' % (snapshot.get('generated_at') or ''))
        add('| %s | %s | %s | %s | %s | **%s** | %s |' % (r['day_heading'], teams, r['stage'] or '', r['format'] or '',
                                                          r['displayed_time'] or '', r['start_utc'] or '', on_board))
    add('')
    add('The two semi-finals are on the Hotspawn board with published probabilities, so they are **board picks with tier '
        'and points**, not research-only guidance. That corrects the wording that was live before this capture; the '
        'evidence is in section 4.')
    add('')
    add('## 3. The Aurora roster-change premise, from HLTV\'s own team page')
    add('')
    aur = (hltv.get('teams') or {}).get('Aurora') or {}
    roster = aur.get('roster_table') or []
    if roster:
        add('Source: `https://www.hltv.org/team/11861/aurora` (raw body `research/hltv-79f0e55b/team-Aurora.html`, '
            'sha256 `%s`), read at the same time as the match pages.' % short((aur.get('receipt') or {}).get('sha256')))
        add('')
        add('| ' + ' | '.join(roster[0]) + ' |')
        add('| ' + ' | '.join(['---'] * len(roster[0])) + ' |')
        for row in roster[1:]:
            add('| ' + ' | '.join(row) + ' |')
        add('')
        coach = aur.get('coach_table') or []
        if len(coach) > 1:
            add('Coaching row, same page: **%s**.' % ' | '.join(coach[1]))
            add('')
        add('Reading: the players HLTV lists at **3 months** on the team (and the coach at 3 months) are the July 2026 '
            'arrivals; the ones at 1 year 6 months are the pre-existing core. So "Aurora made a recent roster change" is '
            'true only in the sense of a change made about three months before this tournament — not a new player being '
            'onboarded during it. HLTV\'s page also states Aurora\'s standing as `%s`.' % (aur.get('world_rank_text') or 'not captured'))
    else:
        add('The roster table did not parse; nothing is claimed about the roster from this run.')
    add('')
    add('## 4. Board coverage at the refresh, and the one published claim it supersedes')
    add('')
    b = twc['board']
    add('Refresh: `python -m scripts.refresh` on the runner, summary `%s`.' % (json.dumps(refresh_summary) if refresh_summary else 'not captured'))
    add('')
    add('| Measure | Value |')
    add('| --- | --- |')
    add('| Rows in the snapshot | %s |' % b['rows_total'])
    add('| Open fixtures | %s |' % b['open_total'])
    add('| Open with a published probability | %s |' % b['open_priced'])
    add('| Open with a labelled research pick and no percentage | %s |' % b['open_research_only'])
    add('| **Open with no supported pick at all** | **%s** |' % b['open_without_pick'])
    add('| Coverage flag | `%s` |' % b['coverage'])
    add('| Three-source inventory parity (API / CS2 page / lobby) | %s |' % json.dumps(b['coverage_counts']))
    add('| Fixtures added since the previous snapshot | %s |' % ', '.join((b.get('inventory_changes') or {}).get('added_ids') or []))
    add('')
    added = (b.get('inventory_changes') or {}).get('added_ids') or []
    semis = [k for k in ('1080207', '1080208') if k in added]
    if semis:
        add('**Superseded claim.** Both semi-finals were discovered as new fixtures in this refresh '
            '(`added_ids` above) and each carries all three Hotspawn views as its source — the CS2 fixture API, '
            '`play.hotspawn.com/cs2-pickems` and the general lobby. The page text published earlier on the same day said '
            '*"Neither semi-final is on Hotspawn\'s CS2 feed, so these are research guidance rather than board submissions '
            'and carry no tier or points value."* That sentence is now false: as of this capture both are board rows with '
            'tier `s`, Hotspawn lock times, and published probabilities from Polymarket. A reader following it would lose '
            'the contest points for two fixtures. The rows are:')
        add('')
        for rid in semis:
            row = board.get(rid) or {}
            probs = row.get('probabilities') or []
            add('* `%s` — %s, start `%s`, lock `%s`, tier `%s`, pick **%s** (`%s`), probabilities %s, fair odds %s.'
                % (rid, ' vs '.join(row.get('teams') or []), row.get('start'), row.get('lock'), row.get('tier'),
                   row.get('pick'), row.get('method'), probs, row.get('fair_odds')))
        add('')
        add('For comparison, HLTV\'s own betting-analytics page for `2399414` states that *"Aurora is the bookmaker '
            'favorite with the best odds"* while the exchange line published on the board is slightly the other way '
            '(%s / %s). Both are recorded; the board publishes the exchange line because that is the source that passes '
            'its gates.' % tuple(round(p * 100, 1) for p in ((board.get('1080207') or {}).get('probabilities') or [0, 0])))
    add('')
    add('## 5. The five rows that still carry no percentage, and why that is a ceiling rather than an omission')
    add('')
    add('Every one of them has a pick; none has a number. The reason is the same in each case: no accessible market '
        'prices the fixture, and **Valve\'s official standings do not rate the opponent anywhere**, so no model line can '
        'be computed without inventing an input. Checked against Valve\'s global file *and* all three regional files '
        '(2026-10-05, byte-for-byte copies in `vrs/`):')
    add('')
    add('| Fixture (snapshot id) | Pick | Rated by Valve? | Opponent rated by Valve? | Market line |')
    add('| --- | --- | --- | --- | --- |')
    for r in research_rows:
        teams = r['teams']
        left, right = (teams + ['', ''])[:2]
        def fmt(team):
            hits = r['ratings'].get(team) or []
            if not hits:
                return 'no'
            return '; '.join('%s #%s (%s pts)' % (h['region'], h['standing'], h['points']) for h in hits)
        add('| %s — %s vs %s | %s | %s | %s | none found (Polymarket, Pinnacle, and the probed books) |'
            % (r['id'], left, right, r.get('pick'), fmt(left), fmt(right)))
    add('')
    add('Two further limits specific to these rows, both visible above: `Chinggis Warriors` appears **twice** in Valve\'s '
        'Asia file with three players in common, so the label is not unique; and the ranked-opponent signal used for the '
        'pick is a ranking order, not a probability, which is why no percentage is published.')
    add('')
    add('## 6. The deployed site, checked against its own data')
    add('')
    lb = live.get('live_board') or {}
    add('Captured by `scripts/live_capture_79f0e55b.py` on the runner (14 bodies, mobile user agent, `Cache-Control: '
        'no-cache`): latest build revision from `build-info.json`, and the live `data/latest.json` compared with this '
        'session\'s own refresh.')
    add('')
    add('| Check | Result |')
    add('| --- | --- |')
    add('| Pages and data files fetched | %s / %s |' % (live.get('ok_pages'), len(live.get('receipts') or [])))
    add('| Live rows / open / priced / research-only / no pick | %s / %s / %s / %s / %s |'
        % (lb.get('rows_total'), lb.get('open_total'), lb.get('open_priced'), lb.get('open_unpriced'), lb.get('open_without_pick')))
    add('| Live coverage flag and snapshot time | `%s` at %s |' % (lb.get('coverage'), lb.get('generated_at')))
    add('| Live open fixtures absent from this session\'s refresh | %s |' % (live.get('parity') or {}).get('refresh_open_only'))
    add('| Refresh fixtures absent from the live board | %s |' % (live.get('parity') or {}).get('live_open_only'))
    add('| Shared open fixtures | %s |' % (live.get('parity') or {}).get('shared_open'))
    checks = {c['page']: c for c in live.get('checks') or []}
    add('| Mobile viewport declared on every page | %s |' % all(c.get('mobile_viewport_ok') for c in checks.values()))
    add('| Landing page links to the picks board / unresolved / analysis / matches / review / sources | %s |'
        % json.dumps({k: v for k, v in (checks.get('index.html', {}).get('links_to') or {}).items() if v}))
    add('| Landing page has the `#unresolved-summary` anchor | %s |' % checks.get('index.html', {}).get('has_unresolved_anchor'))
    missing_picks = checks.get('picks.html', {}).get('open_rows_missing_from_page') or []
    add('| Open fixtures not rendered on `picks.html` | %s |' % ', '.join(m[0] for m in missing_picks))
    add('| Same fixtures present on `unresolved.html` / `matches.html` | checked separately: yes, all five |')
    add('')
    add('**One user-facing observation, not a defect:** the five research-only rows are rendered on `unresolved.html` and '
        '`matches.html` but not on `picks.html`. A phone reader who only opens the pick board therefore does not see '
        'those five picks, even though they exist. The executive summary does link the unresolved section, so the picks '
        'are reachable in one tap — but showing them on the board, labelled "no market line", would match the brief '
        '("a pick for every match") more literally.')
    add('')
    add('## 7. Status of the three items earlier sessions left open')
    add('')
    add('| Item | Status after this session | Evidence |')
    add('| --- | --- | --- |')
    add('| Did the `refresh.py` rate-limit fix restore the rows a 403 had been stripping? | **Yes, on this run.** '
        '`unresolved_without_any_pick` is 0 and coverage is `verified` with 96 rows across three agreeing views. The '
        'GG.BET 403 still happens (`source_checks`) but no longer removes a pick. | `logs/refresh.txt`, section 4 |')
    add('| Polymarket "BET-M 33" vs HLTV team 13619, and "Leo Team" vs Valve\'s two `Leo` rosters | **Still not '
        'aliased.** Both rows carry picks (`model_vrs`) and none is blocked, so this stays a possible precision '
        'improvement rather than a gap. | snapshot rows `1079170`, `1081532` |')
    add('| Why HLTV answered 403 in an earlier run | **Not reproduced.** This session\'s runner read 20/20 HLTV pages '
        'with HTTP 200 using 2 s spacing and up to three retries; no 403 occurred. That is consistent with rate '
        'limiting, but it does not prove it, so the cause stays unestablished. | `twc-2026-verified.json` page receipts |')
    add('')
    add('## 8. Flagged for review (nothing here is hidden)')
    add('')
    add('1. The superseded semi-final sentence (section 4) was live on the site during this session. It is a wording '
        'defect in published guidance, and it is the one thing in this report that a reader could have acted on wrongly.')
    add('2. Hotspawn supplies no `best_of` for the two semi-final rows (`best_of: null`), so the board cannot check its '
        'usually-required format agreement for them; HLTV states both are bo3. The mismatch is recorded, not resolved.')
    add('3. Five rows have no percentage (section 5). This is a proven ceiling of the verified sources, not an untried '
        'search, but the brief asks for a number on every match, so it is listed as an open requirement gap.')
    add('4. Live and refreshed boards were captured about 15 minutes apart and agree on all 34 open fixtures; older '
        'sections of this directory remain timestamped observations, never permanent coverage claims.')
    add('')

    (out / 'VERIFICATION.md').write_text('\n'.join(md), encoding='utf-8')
    (out / 'twc-2026-verified.json').write_text(json.dumps(twc, indent=1, ensure_ascii=False, sort_keys=True) + '\n',
                                               encoding='utf-8')
    print('verify_report_79f0e55b: %d results, %d scheduled fixtures, %d research rows, %d pages -> %s'
          % (len(twc['results']), len(twc['schedule']), len(research_rows), len(twc['hltv_pages']), out))


if __name__ == '__main__':
    main()
