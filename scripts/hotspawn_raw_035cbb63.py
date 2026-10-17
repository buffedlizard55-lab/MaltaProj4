"""Raw Hotspawn capture for the session-035cbb63 inventory audit (research only).

The refresh at 2026-10-17T00:59Z reported all three Hotspawn sources unusable:
the fixtures API returned a body that is not JSON ("Expecting value: line 1
column 1") and both HTML pages returned HTTP 200 with "hydration data missing".
Neither failure can be diagnosed from the collector's own log line, because the
log records the exception and not the bytes.

This script records the bytes: real HTTP status, response headers, content
length, a SHA-256 of the body and the first 4 KB of the body for each official
source, plus whether the Next.js hydration markers the collector relies on
(``__NEXT_DATA__``, ``self.__next_f``) are present in the HTML at all.

It changes no collector behaviour and publishes nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests

TARGETS = [
    ('fixtures_api', 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1'),
    ('cs2_pickems_page', 'https://play.hotspawn.com/cs2-pickems'),
    ('lobby_page', 'https://play.hotspawn.com/lobby'),
]
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8',
           'Accept-Language': 'en-US,en;q=0.9'}
MARKERS = ('__NEXT_DATA__', 'self.__next_f', 'window.__NUXT__', '__remixContext', 'buildId',
           # scripts/core.py hotspawn_state() requires <script id="ng-state">: Angular's
           # server-side transfer state. This audit must measure that exact marker.
           'ng-state', 'id="ng-state"', '_ngcontent')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='research/inventory-035cbb63')
    args = parser.parse_args()
    out = Path(args.output)
    (out / 'raw').mkdir(parents=True, exist_ok=True)
    report = {'captured_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
              'session': '035cbb63', 'targets': []}
    for name, url in TARGETS:
        entry = {'name': name, 'url': url}
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            body = response.content
            entry.update(http_status=response.status_code,
                         content_type=response.headers.get('content-type', ''),
                         server=response.headers.get('server', ''),
                         cf_ray=response.headers.get('cf-ray', ''),
                         bytes=len(body),
                         sha256=hashlib.sha256(body).hexdigest(),
                         headers={k: v for k, v in response.headers.items()})
            text = body.decode('utf-8', 'replace')
            entry['markers_present'] = {m: (m in text) for m in MARKERS}
            entry['looks_like_json'] = text.lstrip()[:1] in ('[', '{')
            entry['looks_like_html'] = text.lstrip()[:1].lower() == '<'
            # A Cloudflare interstitial or an error page is short and distinctive.
            entry['head'] = text[:1200]
            entry['marker_positions'] = {m: text.find(m) for m in MARKERS}
            (out / 'raw' / (name + '.txt')).write_text(text[:200000])
        except Exception as exc:
            entry.update(error=f'{type(exc).__name__}: {exc}')
        report['targets'].append(entry)
    (out / 'raw-capture.json').write_text(json.dumps(report, indent=2) + '\n')

    lines = ['# Raw Hotspawn capture — session 035cbb63', '',
             f"Captured: {report['captured_at']}", '',
             'Recorded because the 2026-10-17T00:59Z refresh could not use any of the three '
             'official sources. Bytes, not assumptions.', '']
    for entry in report['targets']:
        lines.append(f"## {entry['name']} — `{entry['url']}`")
        if 'error' in entry:
            lines.append('')
            lines.append(f"- **request failed:** {entry['error']}")
            continue
        lines += ['',
                  f"- HTTP {entry['http_status']} · content-type `{entry['content_type']}` · "
                  f"{entry['bytes']} bytes · sha256 `{entry['sha256'][:16]}…`",
                  f"- looks like JSON: {entry['looks_like_json']} · looks like HTML: {entry['looks_like_html']}",
                  '- hydration markers present: '
                  + ', '.join(f'`{k}`={v}' for k, v in entry['markers_present'].items()),
                  '', 'First 1200 characters of the body:', '', '```', entry['head'], '```', '']
    (out / 'RAW-CAPTURE.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps([{'name': t['name'], 'http': t.get('http_status'),
                       'bytes': t.get('bytes'), 'error': t.get('error'),
                       'markers': t.get('markers_present')} for t in report['targets']], indent=2))


if __name__ == '__main__':
    main()
