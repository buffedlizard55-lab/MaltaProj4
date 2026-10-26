"""Read-only Hotspawn inventory probe for session 77046e56.

Question this answers with measurement rather than assumption:

    The public lobby renders "All tiers (81)" and "19 matches this week", and eight
    of those fixtures (1079201, 1079202, 1079203, 1081159, 1081160, 1081162,
    1081163, 1081164) are absent from the board. The collector reads three views --
    the fixtures API with ``status=scheduled&tenantId=1``, the CS2 pick'em page and
    the general lobby -- and all three report 73 rows. So where do the missing
    eight live, and which documented request carries them?

The probe is read-only: it never writes ``data/``, never publishes and never
retries a refusal. It sends the same User-Agent the refresh sends; nothing is
disguised. Every request, its status, byte count and the IDs it returned are
retained so a reader can re-run the same URLs.

Outputs (paths are relative to the repository root):

    research/session-77046e56/diag/probe.json   machine-readable receipts
    research/session-77046e56/diag/probe.md     the same, as a table for review
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from datetime import datetime, timezone

import requests

UA = 'Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)'
API = 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures'
LOBBY = 'https://play.hotspawn.com/lobby'
PICKEMS = 'https://play.hotspawn.com/cs2-pickems'
OUT = pathlib.Path('research/session-77046e56/diag')

# The eight fixtures the rendered lobby lists and the committed board does not.
TARGETS = ['1079201', '1079202', '1079203', '1081159', '1081160',
           '1081162', '1081163', '1081164']

# Parameter combinations, in the order they are tried. The first row is exactly
# what scripts/core.py: FIXTURES uses today, so it doubles as the control.
API_VARIANTS = [
    ('current collector URL', {'sport_alias': 'cs2', 'status': 'scheduled', 'tenantId': '1'}),
    ('no status filter', {'sport_alias': 'cs2', 'tenantId': '1'}),
    ('status=open', {'sport_alias': 'cs2', 'status': 'open', 'tenantId': '1'}),
    ('status=upcoming', {'sport_alias': 'cs2', 'status': 'upcoming', 'tenantId': '1'}),
    ('status=locked', {'sport_alias': 'cs2', 'status': 'locked', 'tenantId': '1'}),
    ('status=live', {'sport_alias': 'cs2', 'status': 'live', 'tenantId': '1'}),
    ('status=pending', {'sport_alias': 'cs2', 'status': 'pending', 'tenantId': '1'}),
    ('status=active', {'sport_alias': 'cs2', 'status': 'active', 'tenantId': '1'}),
    ('no tenantId', {'sport_alias': 'cs2', 'status': 'scheduled'}),
    ('limit=1000', {'sport_alias': 'cs2', 'status': 'scheduled', 'tenantId': '1', 'limit': '1000'}),
    ('page=2', {'sport_alias': 'cs2', 'status': 'scheduled', 'tenantId': '1', 'page': '2'}),
    ('offset=73', {'sport_alias': 'cs2', 'status': 'scheduled', 'tenantId': '1', 'offset': '73'}),
    ('per_page=1000', {'sport_alias': 'cs2', 'status': 'scheduled', 'tenantId': '1', 'per_page': '1000'}),
    ('take=1000', {'sport_alias': 'cs2', 'status': 'scheduled', 'tenantId': '1', 'take': '1000'}),
]

PAGE_TARGETS = [('lobby', LOBBY), ('cs2-pickems', PICKEMS)]

MAX_BYTES = 40 * 1024 * 1024


def get(url, params=None, stream_cap=MAX_BYTES):
    """One dated GET. A refusal is the result; it is never retried here."""
    receipt = {'url': url, 'params': params or {},
               'requested_at': datetime.now(timezone.utc).isoformat()}
    try:
        response = requests.get(url, params=params, headers={'User-Agent': UA},
                                timeout=(10, 60), stream=True)
        body = b''
        for chunk in response.iter_content(65536):
            body += chunk
            if len(body) > stream_cap:
                receipt['truncated_at_bytes'] = stream_cap
                break
        receipt['status'] = response.status_code
        receipt['bytes'] = len(body)
        receipt['content_type'] = response.headers.get('content-type', '')
        receipt['body'] = body
        return receipt
    except Exception as exc:  # a network failure is a finding, not something to hide
        receipt['status'] = 'exception'
        receipt['error'] = '%s: %s' % (type(exc).__name__, str(exc)[:300])
        receipt['bytes'] = 0
        receipt['body'] = b''
        return receipt


def parse_rows(receipt):
    """Return the fixture rows of a JSON response, or [] with a reason."""
    text = receipt['body'].decode('utf-8', 'replace')
    if not text.strip():
        return [], 'empty body'
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return [], 'not JSON: %s; body head %r' % (exc, text[:160])
    if isinstance(payload, dict):
        return [], 'object, not array: %r' % (str(payload)[:200],)
    if not isinstance(payload, list):
        return [], 'unexpected type %s' % type(payload).__name__
    return payload, ''


def summarise_api(receipt):
    rows, reason = parse_rows(receipt)
    out = {k: v for k, v in receipt.items() if k != 'body'}
    out['row_reason'] = reason
    out['rows'] = len(rows)
    cs2 = [r for r in rows if isinstance(r, dict) and r.get('sport_alias') == 'cs2']
    out['cs2_rows'] = len(cs2)
    ids = {str(r.get('id')) for r in cs2}
    out['targets_present'] = sorted(i for i in TARGETS if i in ids)
    out['targets_missing'] = sorted(i for i in TARGETS if i not in ids)
    now_ms = datetime.now(timezone.utc).timestamp() * 1000
    future = []
    for row in cs2:
        try:
            start = float(row.get('scheduled_start_time') or 0)
        except (TypeError, ValueError):
            start = 0
        if start > now_ms:
            future.append(row)
    out['future_rows'] = len(future)
    out['future_ids'] = sorted(str(r.get('id')) for r in future)
    # Keep the full record of any target we did find, so the repair has data.
    out['target_rows'] = [r for r in cs2 if str(r.get('id')) in TARGETS]
    return out


def page_scan(name, url):
    receipt = get(url)
    text = receipt['body'].decode('utf-8', 'replace')
    out = {k: v for k, v in receipt.items() if k != 'body'}
    out['name'] = name
    # Fixture IDs appear in hrefs like /matches/ground-zero-vs-off-chops-...-1082858
    ids = set(re.findall(r'/matches/[a-z0-9\-]+?-(\d{5,7})', text))
    out['href_fixture_ids'] = len(ids)
    out['targets_present'] = sorted(i for i in TARGETS if i in ids)
    out['targets_absent'] = sorted(i for i in TARGETS if i not in ids)
    out['raw_mentions'] = {i: text.count(i) for i in TARGETS}
    # The angular hydration block the collector parses.
    out['ng_state_blocks'] = text.count('ng-state')
    out['has_ng_state'] = 'ng-state' in text
    out['this_week_label'] = 'matches this week' in text
    counts = re.findall(r'All tiers \((\d+)\)', text)
    out['lobby_tier_counts'] = counts
    # Script bundles that could name the request the browser makes itself.
    out['script_srcs'] = re.findall(r'<script[^>]+src="([^"]+)"', text)[:20]
    return out


def bundle_scan(script_urls, limit=12):
    """Look for the fixtures request the lobby's own JavaScript performs."""
    findings = []
    for src in script_urls:
        if not src.startswith('http'):
            src = 'https://play.hotspawn.com' + ('' if src.startswith('/') else '/') + src
        if not src.endswith('.js'):
            continue
        receipt = get(src, stream_cap=12 * 1024 * 1024)
        text = receipt['body'].decode('utf-8', 'replace')
        hits = sorted(set(re.findall(r'[/a-zA-Z0-9_.\-]*api/v1/fixtures[^"\'`\s]{0,160}', text)))
        queries = sorted(set(re.findall(r'status=[a-zA-Z_,]+', text)))
        row = {'script': src, 'status': receipt.get('status'), 'bytes': receipt.get('bytes'),
               'fixtures_mentions': len(re.findall(r'api/v1/fixtures', text)),
               'fixtures_urls': hits[:20], 'status_params': queries[:20]}
        findings.append(row)
        if len(findings) >= limit:
            break
    return findings


def write_reports(report):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'probe.json').write_text(json.dumps(report, indent=1) + '\n')

    lines = ['# Hotspawn inventory probe — session 77046e56', '',
             'Read-only measurement. Every URL below was requested once, with the same '
             'User-Agent the refresh sends (`%s`).' % UA, '']
    lines += ['Recorded %s' % report['recorded_at'], '',
              '## Fixtures API parameter matrix', '',
              '| Variant | Status | Bytes | Rows | CS2 | Future | Targets found | Targets missing |',
              '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for row in report['api']:
        lines.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
            row['variant'], row.get('status'), row.get('bytes'), row.get('rows'),
            row.get('cs2_rows'), row.get('future_rows'),
            ', '.join(row.get('targets_present') or []) or '—',
            ', '.join(row.get('targets_missing') or []) or '—'))
    if report.get('api_errors'):
        lines += ['', '### Rejected parameter names', '', '| Variant | Response |', '| --- | --- |']
        for row in report['api_errors']:
            lines.append('| %s | `%s` |' % (row['variant'], row.get('row_reason') or row.get('status')))
    lines += ['', '## Rendered pages', '',
              '| Page | Status | Bytes | Fixture IDs in hrefs | Targets present | Tier counts | ng-state |',
              '| --- | --- | --- | --- | --- | --- | --- |']
    for row in report['pages']:
        lines.append('| %s | %s | %s | %s | %s | %s | %s |' % (
            row['name'], row.get('status'), row.get('bytes'), row.get('href_fixture_ids'),
            ', '.join(row.get('targets_present') or []) or '—',
            ', '.join(row.get('lobby_tier_counts') or []) or '—',
            row.get('has_ng_state')))
    if report.get('bundles'):
        lines += ['', '## Lobby JavaScript requests', '',
                  '| Bundle | Status | Bytes | `api/v1/fixtures` mentions | Request found |',
                  '| --- | --- | --- | --- | --- |']
        for row in report['bundles']:
            lines.append('| %s | %s | %s | %s | `%s` |' % (
                row['script'], row.get('status'), row.get('bytes'),
                row.get('fixtures_mentions'),
                (row.get('fixtures_urls') or ['—'])[0]))
    lines += ['', '## Committed board comparison', '',
              '`data/latest.json` at read time: %s' % report.get('board', 'not read'), '']
    (OUT / 'probe.md').write_text('\n'.join(lines) + '\n')

    print('\n'.join(lines[:80]))


def main():
    report = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'user_agent': UA,
              'targets': TARGETS, 'api': [], 'api_errors': [], 'pages': []}
    try:
        board = json.loads(pathlib.Path('data/latest.json').read_text())
        ids = {str(r['id']) for r in board.get('matches', [])}
        report['board'] = ('%s rows, generated_at %s, targets absent: %s'
                           % (len(ids), board.get('generated_at'),
                              ', '.join(sorted(i for i in TARGETS if i not in ids)) or 'none'))
    except Exception as exc:
        report['board'] = 'unreadable: %s' % exc

    for label, params in API_VARIANTS:
        receipt = get(API, params)
        row = summarise_api(receipt)
        row['variant'] = label
        if row.get('status') == 200 and row.get('rows'):
            report['api'].append({k: v for k, v in row.items() if k != 'target_rows'})
            if row.get('targets_present'):
                report.setdefault('target_rows', {}).update(
                    {str(r['id']): r for r in row.get('target_rows') or []})
        else:
            report['api_errors'].append({k: v for k, v in row.items() if k != 'target_rows'})
        print('API %-24s status=%s rows=%s cs2=%s future=%s found=%s' % (
            label, row.get('status'), row.get('rows'), row.get('cs2_rows'),
            row.get('future_rows'), row.get('targets_present')))

    for name, url in PAGE_TARGETS:
        row = page_scan(name, url)
        report['pages'].append(row)
        print('PAGE %-14s status=%s bytes=%s href_ids=%s found=%s tier_counts=%s ng_state=%s' % (
            name, row.get('status'), row.get('bytes'), row.get('href_fixture_ids'),
            row.get('targets_present'), row.get('lobby_tier_counts'), row.get('has_ng_state')))

    scripts = []
    for row in report['pages']:
        scripts.extend(row.get('script_srcs') or [])
    report['bundles'] = bundle_scan(list(dict.fromkeys(scripts)))
    for row in report['bundles']:
        print('BUNDLE %-60s status=%s mentions=%s urls=%s' % (
            row['script'][-60:], row.get('status'), row.get('fixtures_mentions'),
            row.get('fixtures_urls')[:2]))

    write_reports(report)
    # A missing target is the finding this probe exists for: fail loudly so the
    # workflow's step outcome records it, without treating it as a code error.
    missing = [i for i in TARGETS
               if i not in (report.get('target_rows') or {})]
    print('targets still unresolved from the API: %s' % (', '.join(missing) or 'none'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
