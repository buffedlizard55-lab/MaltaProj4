"""Explain a snapshot's three-way Hotspawn parity gap fixture by fixture (session 3c8d1136).

``scripts.inventory.discover`` records, for every row, which of the three official
Hotspawn views attested it (``fixture_sources``). This script reads a published snapshot
and answers the question the ``coverage_difference`` flag raises but does not answer:
*which* fixtures differ, are they open, and does each one still carry a pick?

It changes no data and invents nothing: a row with no provenance receipt is reported as
unattributable rather than assigned to a source. Output is JSON plus a markdown table
that quotes only values present in the snapshot.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

API = ('https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures'
       '?sport_alias=cs2&status=scheduled&tenantId=1')
PAGE = 'https://play.hotspawn.com/cs2-pickems'
LOBBY = 'https://play.hotspawn.com/lobby'
SOURCES = (('api', API), ('page', PAGE), ('lobby', LOBBY))


def report(snapshot):
    by_id = {str(m['id']): m for m in snapshot.get('matches', [])}
    sets = defaultdict(set)
    unattributable = []
    for match in snapshot.get('matches', []):
        provenance = match.get('fixture_sources') or []
        seen = set()
        for receipt in provenance:
            url = receipt.get('url')
            for key, source in SOURCES:
                if url == source:
                    sets[key].add(str(match['id']))
                    seen.add(key)
            if receipt.get('retained_from_previous_snapshot'):
                seen.add('retained')
                sets['retained'].add(str(match['id']))
        if not seen:
            unattributable.append(str(match['id']))

    def row(ident):
        match = by_id.get(ident, {})
        return {'id': ident, 'start': match.get('start'), 'lock': match.get('lock'),
                'teams': match.get('teams'), 'competition': match.get('competition'),
                'state': match.get('state'), 'pick': match.get('pick'),
                'source_url': match.get('source_url'), 'feed_url': match.get('feed_url'),
                'method': match.get('method'), 'probabilities': match.get('probabilities'),
                'expires_at': match.get('expires_at'),
                'resolution_blocked': bool(match.get('resolution_blocked')),
                'source_status': match.get('source_status')}

    html = sets['page'] | sets['lobby']
    api_only = sorted(sets['api'] - html, key=lambda i: (by_id.get(i, {}).get('start') or '', i))
    html_only = sorted(html - sets['api'], key=lambda i: (by_id.get(i, {}).get('start') or '', i))
    open_rows = [m for m in snapshot.get('matches', []) if m.get('state') == 'open']
    return {
        'snapshot_generated_at': snapshot.get('generated_at'),
        'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
        'built_at': snapshot.get('built_at'),
        'coverage': snapshot.get('coverage'),
        'coverage_counts': snapshot.get('coverage_counts'),
        'source_observed_at': {sc.get('name'): {'url': sc.get('url'),
                                                'observed_at': sc.get('observed_at'),
                                                'retrieved_at': sc.get('retrieved_at'),
                                                'cache_age_seconds': sc.get('cache_age_seconds'),
                                                'http_status': sc.get('http_status'),
                                                'status': sc.get('status')}
                               for sc in snapshot.get('source_checks', [])
                               if 'Hotspawn' in str(sc.get('name'))},
        'ids_per_source': {key: len(sets[key]) for key, _ in SOURCES} | {'retained': len(sets['retained'])},
        'parity': sets['api'] == sets['page'] == sets['lobby'],
        'api_only': [row(i) for i in api_only],
        'html_only': [row(i) for i in html_only],
        'page_vs_lobby_symmetric_difference': sorted(sets['page'] ^ sets['lobby']),
        'unattributable_rows': unattributable,
        'open_rows': len(open_rows),
        'open_rows_with_a_pick': sum(1 for m in open_rows if m.get('pick')),
        'open_rows_without_a_pick': [row(str(m['id'])) for m in open_rows if not m.get('pick')],
        'earliest_open_expiry': min((m.get('expires_at') for m in open_rows if m.get('expires_at')), default=None),
        'issues': snapshot.get('issues'),
    }


def markdown(rep):
    lines = ['# Hotspawn three-way parity, fixture by fixture',
             '',
             'Snapshot `%s` (fixtures observed `%s`, built `%s`), coverage **%s**, counts %s.'
             % (rep['snapshot_generated_at'], rep['fixtures_observed_at'], rep['built_at'],
                rep['coverage'], json.dumps(rep['coverage_counts'], sort_keys=True)),
             '',
             '## Source observation times',
             '',
             '| Source | HTTP | Retrieved (UTC) | Observed (UTC) | `Age` (s) |',
             '|---|---|---|---|---|']
    for name, check in sorted(rep['source_observed_at'].items()):
        lines.append('| [%s](%s) | %s | %s | %s | %s |' % (
            name, check.get('url') or '', check.get('http_status'), check.get('retrieved_at'),
            check.get('observed_at'), check.get('cache_age_seconds')))
    lines += ['', '## ID sets', '', '| Source | CS2 fixtures |', '|---|---|']
    for key, count in sorted(rep['ids_per_source'].items()):
        lines.append('| %s | %s |' % (key, count))
    for label, key in (('Present only in the fresh API', 'api_only'),
                       ('Present only in the cached HTML views', 'html_only')):
        rows = rep[key]
        lines += ['', '## %s (%d)' % (label, len(rows)), '']
        if not rows:
            lines += ['None.', '']
            continue
        lines += ['| Fixture | Start (UTC) | Match | Event | State | Pick | Method | Probabilities | Expires (UTC) |',
                  '|---|---|---|---|---|---|---|---|---|']
        for row in rows:
            # Only a URL the snapshot itself carries is linked; a permalink is never constructed.
            ident = ('[%s](%s)' % (row['id'], row['source_url'])) if row.get('source_url') else row['id']
            lines.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                ident, row['start'] or '', ' vs '.join(row['teams'] or []) or '',
                row['competition'] or '', row['state'] or '', row['pick'] or '(none)',
                row['method'] or '(none)', json.dumps(row['probabilities']) if row['probabilities'] else '(none)',
                row['expires_at'] or ''))
        lines.append('')
    lines += ['## Open coverage', '',
              '- open rows: **%d**' % rep['open_rows'],
              '- open rows with a pick: **%d**' % rep['open_rows_with_a_pick'],
              '- open rows without a pick: **%d**' % len(rep['open_rows_without_a_pick']),
              '- earliest open-row expiry: `%s`' % rep['earliest_open_expiry'],
              '- page/lobby symmetric difference: %s' % (rep['page_vs_lobby_symmetric_difference'] or 'none'),
              '- rows with no attributable source receipt: %s' % (rep['unattributable_rows'] or 'none'),
              '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='data/latest.json')
    parser.add_argument('--output', default='research/coverage-3c8d1136/coverage.json')
    parser.add_argument('--markdown', default='research/coverage-3c8d1136/COVERAGE.md')
    args = parser.parse_args()
    snapshot = json.loads(Path(args.snapshot).read_text())
    rep = report(snapshot)
    for target, payload in ((args.output, json.dumps(rep, indent=2, ensure_ascii=False, sort_keys=True) + '\n'),
                            (args.markdown, markdown(rep))):
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload)
    print(json.dumps({k: rep[k] for k in ('parity', 'ids_per_source', 'open_rows', 'open_rows_with_a_pick',
                                          'earliest_open_expiry')}, indent=2, sort_keys=True))
    print('api_only=%d html_only=%d' % (len(rep['api_only']), len(rep['html_only'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
