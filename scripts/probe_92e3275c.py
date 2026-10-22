"""Read-only access probe for session 92e3275c.

Question this answers with evidence rather than assumption: which of the public
pages the refresh depends on can a GitHub-hosted runner actually read, and in
particular whether HLTV's dated Valve ranking page (the ``model_vrs_mirror``
source) is reachable from that IP range.

The probe sends exactly the same User-Agent the refresh sends
(``scripts/refresh.py`` Sources). Nothing about the request is disguised,
rewritten or re-signed; a block is reported as a block. Output is a JSON block
in the job log so the result is dated and reviewable.
"""
from __future__ import annotations

import json
import pathlib
import sys
from datetime import datetime, timezone

import requests

UA = 'Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)'

TARGETS = [
    ('hltv-fixtures-control', 'https://www.hltv.org/matches'),
    ('hltv-vrs-mirror-global', 'https://www.hltv.org/valve-ranking/teams'),
    ('hltv-vrs-mirror-dated', 'https://www.hltv.org/valve-ranking/teams/2026/october/21'),
    ('hltv-vrs-mirror-europe', 'https://www.hltv.org/valve-ranking/teams/2026/october/21/region/Europe'),
    ('hltv-vrs-team-link', 'https://www.hltv.org/valve-ranking/teams?teamId=12857'),
    ('hltv-world-ranking', 'https://www.hltv.org/ranking/teams/2026/october/19'),
    ('hltv-match-page', 'https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12'),
    ('egw-listing', 'https://egamersworld.com/counterstrike/match/4yp_dlKtNl/nexora-vs-k27-U_TH-dVYT'),
    ('hotspawn-feed', 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1'),
    ('pinnacle-lines', 'https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight'),
]

MARKERS = {
    'hltv-vrs-mirror-global': 'Valve points',
    'hltv-vrs-mirror-dated': 'Valve points',
    'hltv-vrs-mirror-europe': 'Valve points',
    'hltv-fixtures-control': 'matches',
    'hotspawn-feed': 'sport_alias',
}


def probe(name, url):
    row = {'name': name, 'url': url}
    try:
        r = requests.get(url, headers={'User-Agent': UA}, timeout=(10, 40))
        row['status'] = r.status_code
        row['bytes'] = len(r.content or b'')
        text = r.text or ''
        marker = MARKERS.get(name)
        if marker:
            row['marker'] = marker
            row['marker_found'] = marker in text
            row['marker_count'] = text.count(marker)
        if 'Valve points' in text:
            row['valve_points_count'] = text.count('Valve points')
        if r.status_code >= 400:
            row['body_head'] = text[:200].replace('\n', ' ')
    except Exception as exc:  # a failure is the result, not an error to hide
        row['status'] = 'exception'
        row['error'] = '%s: %s' % (type(exc).__name__, str(exc)[:200])
    return row


def summarise(path):
    """Print what the dry run would publish: per-method counts and the blank rows."""
    import collections
    data = json.loads(pathlib.Path(path).read_text())
    rows = data.get('matches') or []
    open_rows = [m for m in rows if m.get('state') == 'open']
    methods = collections.Counter((m.get('method') or 'none') for m in open_rows)
    print(json.dumps({
        'rows_total': len(rows),
        'open': len(open_rows),
        'with_pick': sum(1 for m in open_rows if m.get('pick')),
        'with_probability': sum(1 for m in open_rows if m.get('probabilities')),
        'methods': dict(methods),
        'blank_percentage': [
            {'id': m.get('id'), 'teams': m.get('teams'), 'start': m.get('start'),
             'method': m.get('method'), 'pick': m.get('pick'),
             'reason': (m.get('reason') or '')[:160]}
            for m in open_rows if not m.get('probabilities')
        ],
        'issues': data.get('issues'),
    }, indent=1))


def annotate_probe():
    """One workflow annotation per source, so the result is readable on the run page."""
    for name, url in TARGETS:
        row = probe(name, url)
        detail = 'status=%s bytes=%s' % (row.get('status'), row.get('bytes'))
        if 'marker_count' in row:
            detail += ' marker=%r x%s' % (row['marker'], row['marker_count'])
        if row.get('valve_points_count'):
            detail += ' valve_points_rows=%s' % row['valve_points_count']
        if row.get('error'):
            detail += ' error=%s' % row['error']
        print('::warning::PROBE %s %s %s' % (name, detail, url))


def annotate_snapshot(path):
    """Workflow annotations for the dry run: coverage, methods, blanks, issues."""
    import collections
    data = json.loads(pathlib.Path(path).read_text())
    rows = data.get('matches') or []
    opens = [m for m in rows if m.get('state') == 'open']
    methods = collections.Counter((m.get('method') or 'none') for m in opens)
    print('::warning::DRYRUN rows=%s open=%s pick=%s probability=%s' % (
        len(rows), len(opens), sum(1 for m in opens if m.get('pick')),
        sum(1 for m in opens if m.get('probabilities'))))
    print('::warning::DRYRUN methods %s' % dict(methods))
    for m in opens:
        if not m.get('probabilities'):
            print('::warning::DRYRUN blank %s %s %s pick=%s method=%s' % (
                m.get('id'), ' vs '.join(m.get('teams') or []), m.get('start'),
                m.get('pick'), m.get('method')))
    for issue in data.get('issues') or []:
        print('::warning::DRYRUN issue %s: %s' % (issue.get('code'), str(issue.get('message'))[:180]))


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--summarise':
        summarise(sys.argv[2])
        annotate_snapshot(sys.argv[2])
        return 0
    annotate_probe()
    return 0


def _legacy_main():
    results = [probe(name, url) for name, url in TARGETS]
    print(json.dumps({'probed_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                      'user_agent': UA, 'results': results}, indent=1))
    return 0 if all(isinstance(r.get('status'), int) and r['status'] < 400 for r in results) else 0


if __name__ == '__main__':
    sys.exit(main())
