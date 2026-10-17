"""Session 79f0e55b: capture and verify the *live* published site against its own data.

The user's brief has three testable requirements that no local build can answer, because
they are about what the deployed site actually serves:

1. **Discoverability** - the landing page must link to the picks board, the unresolved
   section, the analysis and the other views, so a phone user can get to the picks in one
   tap, and the pages must declare a mobile viewport and a persistent navigation bar.
2. **Coverage** - every open fixture on the published board must carry a pick, and every
   published probability must match the published JSON rather than being a stale render.
3. **Honesty about gaps** - rows without a market line must be visible as such, with a
   reason, and the unresolved section must exist and be reachable.

This script downloads the live pages and the live ``data/latest.json``, stores every body
with its SHA-256 and observation time, and writes a report with the checks it ran. It
never edits the site and never publishes: it is a read-only audit of production.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SITE = 'https://buffedlizard55-lab.github.io/MaltaProj4'
PAGES = ('index.html', 'picks.html', 'matches.html', 'analysis.html', 'unresolved.html',
         'review.html', 'sources.html', 'evidence.html', 'methodology.html')
ASSETS = ('build-info.json', 'data/latest.json', 'data/matches.csv', 'assets/app.js', 'assets/style.css')
UA = ('Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 '
      '(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1')


def now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def fetch(session, url, attempts=3, pause=3.0):
    record = {'url': url, 'observed_at': now_iso(), 'status': None, 'bytes': None,
              'sha256': None, 'error': None, 'attempts': 0, 'cache_control': None}
    last = None
    for attempt in range(1, attempts + 1):
        record['attempts'] = attempt
        try:
            response = session.get(url, timeout=45)
            record['status'] = response.status_code
            record['cache_control'] = response.headers.get('Cache-Control')
            body = response.content
            record['bytes'] = len(body)
            record['sha256'] = hashlib.sha256(body).hexdigest()
            if response.status_code >= 400:
                raise ValueError('HTTP %d' % response.status_code)
            return body, record
        except Exception as exc:  # noqa: BLE001
            last = '%s: %s' % (type(exc).__name__, str(exc)[:200])
            time.sleep(pause * attempt)
    record['error'] = last
    return None, record


def text_of(node):
    return re.sub(r'\s+', ' ', node.get_text(' ', strip=True)) if node is not None else None


def rows(snapshot):
    return snapshot.get('matches') or []


def summarise(snapshot):
    opens = [m for m in rows(snapshot) if m.get('state') == 'open']
    priced = [m for m in opens if m.get('probabilities')]
    unpriced = [m for m in opens if not m.get('probabilities')]
    return {
        'rows_total': len(rows(snapshot)),
        'open_total': len(opens),
        'open_priced': len(priced),
        'open_unpriced': len(unpriced),
        'open_without_pick': len([m for m in opens if not m.get('pick')]),
        'methods': {m: sum(1 for r in opens if str(r.get('method')) == m) for m in
                    sorted({str(r.get('method')) for r in opens})},
        'unpriced_ids': sorted(str(m['id']) for m in unpriced),
        'unpriced_teams': [[m['id'], m.get('teams'), m.get('pick'), m.get('method'), m.get('reason')]
                           for m in unpriced],
        'coverage': snapshot.get('coverage'),
        'generated_at': snapshot.get('generated_at'),
    }


def page_checks(name, html, snapshot):
    soup = BeautifulSoup(html, 'html.parser')
    checks = {'page': name}
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    checks['viewport'] = viewport.get('content') if viewport else None
    checks['mobile_viewport_ok'] = bool(viewport and 'width=device-width' in (viewport.get('content') or ''))
    hrefs = [a.get('href') or '' for a in soup.select('a[href]')]
    checks['links_to'] = {target: any(h.endswith(target) or target in h for h in hrefs)
                          for target in ('picks.html', 'matches.html', 'analysis.html',
                                         'unresolved.html', 'review.html', 'sources.html')}
    checks['has_unresolved_anchor'] = bool(soup.select_one('#unresolved-summary'))
    checks['nav_candidates'] = sorted({' '.join(n.get('class') or []) for n in
                                       soup.select('nav, .bottom-nav, .nav, [role="navigation"]') if n})
    checks['h1'] = text_of(soup.find('h1'))
    checks['row_cards'] = len(soup.select('table tbody tr, .match-card, .card'))
    # Every open fixture on the published board must appear on the picks or matches page.
    if name in ('picks.html', 'matches.html'):
        body = re.sub(r'\s+', ' ', soup.get_text(' ', strip=True))
        missing = []
        for row in rows(snapshot):
            if row.get('state') != 'open':
                continue
            teams = row.get('teams') or []
            if teams and not all(t in body for t in teams):
                missing.append([row.get('id'), teams])
        checks['open_rows_missing_from_page'] = missing
        checks['open_rows_expected'] = sum(1 for r in rows(snapshot) if r.get('state') == 'open')
        picks, percents = [], []
        for cell in soup.select('.pick, .pick-team, [data-pick]'):
            value = text_of(cell)
            if value:
                picks.append(value)
        for cell in soup.select('.prob, .probability, .pct, [data-probability]'):
            value = text_of(cell)
            if value:
                percents.append(value)
        checks['pick_labels_found'] = picks[:12]
        checks['probability_labels_found'] = percents[:12]
    return checks


def displayed_odds_mismatches(html, snapshot):
    """Percentages rendered on the page that no published probability rounds to."""
    soup = BeautifulSoup(html, 'html.parser')
    body = re.sub(r'\s+', ' ', soup.get_text(' ', strip=True))
    shown = set(re.findall(r'(\d{1,3}(?:\.\d)?)\s?%', body))
    published = set()
    for row in rows(snapshot):
        probs = row.get('probabilities') or []
        if isinstance(probs, dict):
            probs = [probs.get('home'), probs.get('away')]
        for value in probs:
            if isinstance(value, (int, float)):
                published.add('%.1f' % (value * 100))
                published.add('%d' % round(value * 100))
    # A page can legitimately show percentages we do not model (VRS points, ratings), so
    # this is reported as a coverage comparison, not asserted as an error.
    return sorted(shown - published)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='research/live-79f0e55b')
    parser.add_argument('--snapshot', default='runtime/latest.json',
                        help='our own refreshed snapshot, compared against the live board')
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({'User-Agent': UA, 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
    report = {'tool': 'live_capture_79f0e55b', 'site': SITE, 'started_at': now_iso(),
              'receipts': [], 'checks': [], 'errors': [], 'parity': {}}

    bodies, live_snapshot = {}, None
    for name in PAGES:
        body, receipt = fetch(session, '%s/%s' % (SITE, name))
        receipt['name'] = name
        if body is None:
            report['errors'].append({'name': name, 'error': receipt['error'], 'status': receipt['status']})
        else:
            bodies[name] = body
            (out / name).write_bytes(body)
        report['receipts'].append(receipt)
        time.sleep(1)

    for name in ASSETS:
        body, receipt = fetch(session, '%s/%s' % (SITE, name))
        receipt['name'] = name
        if body is None:
            report['errors'].append({'name': name, 'error': receipt['error'], 'status': receipt['status']})
        else:
            (out / name.replace('/', '_')).write_bytes(body)
            if name == 'data/latest.json':
                try:
                    live_snapshot = json.loads(body.decode('utf-8'))
                except Exception as exc:  # noqa: BLE001
                    report['errors'].append({'name': 'parse live snapshot', 'error': str(exc)[:200]})
        report['receipts'].append(receipt)
        time.sleep(1)

    if live_snapshot is not None:
        report['live_board'] = summarise(live_snapshot)
    else:
        report['live_board'] = None

    local_path = Path(args.snapshot)
    if local_path.exists():
        try:
            local = json.loads(local_path.read_text())
            report['refreshed_board'] = summarise(local)
            if live_snapshot is not None:
                live_ids = {str(m['id']) for m in rows(live_snapshot) if m.get('state') == 'open'}
                local_ids = {str(m['id']) for m in rows(local) if m.get('state') == 'open'}
                report['parity'] = {
                    'live_open_only': sorted(live_ids - local_ids),
                    'refresh_open_only': sorted(local_ids - live_ids),
                    'shared_open': len(live_ids & local_ids),
                }
        except Exception as exc:  # noqa: BLE001
            report['errors'].append({'name': 'parse local snapshot', 'error': str(exc)[:200]})

    html = {name: body.decode('utf-8', 'replace') for name, body in bodies.items() if name.endswith('.html')}
    for name, page in html.items():
        try:
            report['checks'].append(page_checks(name, page, live_snapshot or {'matches': []}))
        except Exception as exc:  # noqa: BLE001
            report['errors'].append({'name': 'checks %s' % name, 'error': str(exc)[:300]})
    if 'picks.html' in html and live_snapshot is not None:
        report['picks_percent_not_in_published_set'] = displayed_odds_mismatches(html['picks.html'], live_snapshot)

    report['finished_at'] = now_iso()
    report['ok_pages'] = sum(1 for r in report['receipts'] if r.get('status') == 200)
    (out / 'report.json').write_text(json.dumps(report, indent=1, ensure_ascii=False, sort_keys=True) + '\n',
                                     encoding='utf-8')
    print('live_capture_79f0e55b: %d/%d bodies ok; live board %s; refreshed board %s -> %s'
          % (report['ok_pages'], len(report['receipts']),
             (report.get('live_board') or {}).get('rows_total'),
             (report.get('refreshed_board') or {}).get('rows_total'), out))


if __name__ == '__main__':
    main()
