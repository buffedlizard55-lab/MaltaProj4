"""Hotspawn inventory-completeness audit (session 035cbb63, research only).

Why this exists
---------------
The standing brief asks for "full coverage of all picks that are available on
the site". The collector reads exactly one scoped endpoint:

    /api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1

and then checks it for parity against two HTML pages. Parity proves the three
sources agree; it does **not** prove the scope of the query is complete. If
Hotspawn exposes CS2 fixtures under another ``status`` value, or paginates the
response, the board could be internally consistent and still be missing rows.

This script measures that question instead of assuming an answer. It requests a
fixed matrix of query variants against the same official host, records the real
HTTP status and the real row/id set for each, and reports any CS2 fixture id that
a variant exposes but the collector's query does not. Every variant is recorded,
including ones that fail, and a failure is never reported as "no such fixtures".

It publishes nothing, edits no collector file and never supplies a probability.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests

BASE = 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures'
COLLECTOR = BASE + '?' + urlencode({'sport_alias': 'cs2', 'status': 'scheduled', 'tenantId': '1'})

# Each variant is a research question, not a proposed change. ``note`` records
# what the variant is testing so a reader can judge the result without guessing.
VARIANTS = [
    ({'sport_alias': 'cs2', 'status': 'scheduled', 'tenantId': '1'},
     'baseline: exactly what scripts/core.py requests today'),
    ({'sport_alias': 'cs2', 'tenantId': '1'},
     'no status filter: does the endpoint default to a wider or narrower set?'),
    ({'sport_alias': 'cs2', 'status': 'upcoming', 'tenantId': '1'},
     'is there an "upcoming" status distinct from "scheduled"?'),
    ({'sport_alias': 'cs2', 'status': 'live', 'tenantId': '1'},
     'is there a "live" status that carries pickable matches?'),
    ({'sport_alias': 'cs2', 'status': 'finished', 'tenantId': '1'},
     'is there a "finished" status (result rows, not picks)?'),
    ({'sport_alias': 'cs2', 'status': 'open', 'tenantId': '1'},
     'is there an "open" status?'),
    ({'tenantId': '1', 'status': 'scheduled'},
     'no sport filter: how many non-CS2 rows share the endpoint?'),
    ({'sport_alias': 'cs2', 'status': 'scheduled', 'tenantId': '1', 'page': '2'},
     'pagination probe: does a second page exist?'),
    ({'sport_alias': 'cs2', 'status': 'scheduled', 'tenantId': '1', 'per_page': '1000'},
     'page-size probe: does a larger page return more rows?'),
    ({'sport_alias': 'cs2', 'status': 'scheduled', 'tenantId': '1', 'limit': '100', 'offset': '100'},
     'limit/offset probe: does offsetting return a different window?'),
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
           'Accept': 'application/json, text/plain, */*'}


def fetch(params, note, timeout=25):
    """One variant, one honest record. Never raise; never invent a result."""
    url = BASE + '?' + urlencode(params)
    record = {'params': params, 'url': url, 'note': note,
              'observed_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
    except Exception as exc:  # network/DNS/TLS — recorded, not swallowed
        record.update(http_status=None, error=f'{type(exc).__name__}: {exc}',
                      rows_total=None, rows_cs2=None, ids=[])
        return record
    record['http_status'] = response.status_code
    record['content_type'] = response.headers.get('content-type', '')
    record['bytes'] = len(response.content)
    if response.status_code != 200:
        record.update(rows_total=None, rows_cs2=None, ids=[],
                      error=f'HTTP {response.status_code}')
        return record
    try:
        payload = response.json()
    except ValueError as exc:
        record.update(rows_total=None, rows_cs2=None, ids=[],
                      error=f'not JSON: {exc}')
        return record
    if isinstance(payload, dict):
        # A paginated envelope would look like this; record the shape either way.
        rows = payload.get('data') or payload.get('fixtures') or payload.get('results') or []
        record['envelope_keys'] = sorted(payload)[:20]
    else:
        rows = payload if isinstance(payload, list) else []
    if not isinstance(rows, list):
        record.update(rows_total=None, rows_cs2=None, ids=[], error='unexpected row container')
        return record
    cs2 = [r for r in rows if isinstance(r, dict) and r.get('sport_alias') == 'cs2']
    record['rows_total'] = len(rows)
    record['rows_cs2'] = len(cs2)
    record['ids'] = sorted({str(r.get('id')) for r in cs2 if r.get('id') is not None})
    record['statuses'] = sorted({str(r.get('status')) for r in cs2 if r.get('status')})
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='research/inventory-035cbb63')
    parser.add_argument('--snapshot', default=None,
                        help='optional refreshed snapshot to compare the board against')
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    records = [fetch(params, note) for params, note in VARIANTS]
    baseline = next(r for r in records if r['params'].get('status') == 'scheduled'
                    and 'page' not in r['params'] and 'per_page' not in r['params']
                    and 'limit' not in r['params'] and r['params'].get('sport_alias') == 'cs2')
    baseline_ids = set(baseline.get('ids') or [])

    extra = {}
    for record in records:
        if record is baseline or not record.get('ids'):
            continue
        new_ids = sorted(set(record['ids']) - baseline_ids)
        if new_ids:
            extra[record['url']] = {'note': record['note'], 'http_status': record['http_status'],
                                    'rows_cs2': record['rows_cs2'], 'ids_not_in_baseline': new_ids}

    board_ids = set()
    board_note = 'no snapshot supplied; board membership not compared'
    if args.snapshot and Path(args.snapshot).exists():
        snap = json.loads(Path(args.snapshot).read_text())
        board_ids = {str(m['id']) for m in snap.get('matches', [])}
        board_note = (f'compared with {args.snapshot} '
                      f'(generated_at {snap.get("generated_at")}, {len(board_ids)} board rows)')

    report = {
        'audited_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'session': '035cbb63',
        'collector_query': COLLECTOR,
        'question': ('Does the collector\'s scoped query return every CS2 fixture Hotspawn '
                     'exposes on this endpoint, or does another status value / pagination '
                     'expose fixtures the board never sees?'),
        'baseline_rows_cs2': baseline.get('rows_cs2'),
        'baseline_statuses': baseline.get('statuses'),
        'board_comparison': board_note,
        'variants': records,
        'fixtures_exposed_outside_the_baseline_query': extra,
        'board_rows_missing_from_baseline': sorted(board_ids - baseline_ids) if board_ids else None,
        'baseline_rows_missing_from_board': sorted(baseline_ids - board_ids) if board_ids else None,
    }
    (out / 'inventory-audit.json').write_text(json.dumps(report, indent=2) + '\n')

    lines = ['# Hotspawn inventory-completeness audit — session 035cbb63', '',
             f"Audited: {report['audited_at']}", '',
             'Question: ' + report['question'], '',
             f"Collector query: `{COLLECTOR}`", '',
             f"Baseline CS2 rows: {report['baseline_rows_cs2']} "
             f"(statuses reported: {', '.join(report['baseline_statuses'] or []) or 'none'})", '',
             f"Board comparison: {board_note}", '',
             '## Every variant measured', '',
             '| Variant | note | HTTP | rows (all) | rows (CS2) | statuses |',
             '| --- | --- | --- | --- | --- | --- |']
    for r in records:
        lines.append('| `{params}` | {note} | {http} | {total} | {cs2} | {st} |'.format(
            params=urlencode(r['params']), note=r['note'],
            http=r.get('http_status') if r.get('http_status') is not None else 'error',
            total=r.get('rows_total') if r.get('rows_total') is not None else '—',
            cs2=r.get('rows_cs2') if r.get('rows_cs2') is not None else '—',
            st=', '.join(r.get('statuses') or []) or (r.get('error') or '—')))
    lines += ['', '## Fixtures exposed outside the baseline query', '']
    if extra:
        for url, info in extra.items():
            lines.append(f"- `{url}` — {info['note']}; {info['rows_cs2']} CS2 rows; "
                         f"{len(info['ids_not_in_baseline'])} id(s) not in the baseline: "
                         f"{', '.join(info['ids_not_in_baseline'][:40])}")
    else:
        lines.append('None. Every variant that returned CS2 rows returned ids that are already in '
                     'the baseline set, so no measured evidence of missing coverage was found. '
                     'This is a measurement of the variants listed above, not a proof about '
                     'endpoints that were not probed.')
    if board_ids:
        lines += ['', '## Board vs baseline', '',
                  f"- board rows not in the baseline response: "
                  f"{', '.join(report['board_rows_missing_from_baseline']) or 'none'}",
                  f"- baseline rows not on the board: "
                  f"{', '.join(report['baseline_rows_missing_from_board']) or 'none'}"]
    lines += ['', '## Limitations', '',
              '- The probe covers the query variants listed above. A parameter name not guessed '
              'here (for example an undocumented competition or date filter) is not covered.',
              '- A non-200 response is recorded as a limitation, never as "no such fixtures".',
              '- HTML pages (lobby, cs2-pickems) are already compared by scripts/inventory.py; '
              'this audit adds the API-scope question, it does not replace that parity check.',
              '- No probability, pick or roster inference is produced here.']
    (out / 'FINDINGS.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'baseline_rows_cs2': report['baseline_rows_cs2'],
                      'variants_measured': len(records),
                      'extra_fixture_sources': len(extra),
                      'board_rows_missing_from_baseline': report['board_rows_missing_from_baseline'],
                      'baseline_rows_missing_from_board': report['baseline_rows_missing_from_board']},
                     indent=2))


if __name__ == '__main__':
    main()
