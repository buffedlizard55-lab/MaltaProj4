"""Read-only CDN freshness probe for Hotspawn's three public views (session 3c8d1136).

Why this exists
---------------
At the production refresh of 2026-10-16T07:21:05Z (main `693b637`, published at
https://buffedlizard55-lab.github.io/MaltaProj4/build-info.json) the three Hotspawn
views answered with very different cache ages:

* fixtures API  - no ``Age`` header, i.e. fresh, 103 CS2 fixtures
* ``/cs2-pickems`` - ``Age: 14241`` (about 3 h 57 m), 95 fixtures
* ``/lobby``       - ``Age: 6251``  (about 1 h 44 m), 95 fixtures

``scripts.refresh.Sources.get`` derives ``observed_at = retrieved_at - Age`` and
``scripts.inventory.discover`` anchors the whole board at ``min(observations)``, so one
cached HTML copy moved every open pick's deadline from 15:21Z to **11:23:45Z** - before
both Thunderpick World Championship day-3 deciders (14:00Z and 17:00Z). The board also
reported ``coverage: partial`` for the same reason.

What this script measures
-------------------------
Whether requesting the *same public URL* with a distinct cache-busting query argument
returns a fresher copy (``Age`` near zero) and whether the three views then agree on the
CS2 fixture ID set. It publishes nothing, writes no data file, bypasses no access control
and never treats a failed fetch as an empty lobby: every response's headers, byte length,
SHA-256 and parsed ID set are written to ``--output`` so each claim can be re-checked
line by line against the receipts.
"""
import argparse
import datetime
import hashlib
import json
import os
import time
import uuid
from pathlib import Path
from urllib.parse import urlencode, urlsplit

import requests

from scripts.core import FIXTURES, HOTSPAWN, hotspawn_state

LOBBY = 'https://play.hotspawn.com/lobby'
VIEWS = (('api', 'Hotspawn CS2 fixtures', FIXTURES, True),
         ('page', 'Hotspawn CS2 lobby', HOTSPAWN, False),
         ('lobby', 'Hotspawn general lobby', LOBBY, False))
HEADER_KEYS = ('age', 'date', 'last-modified', 'etag', 'cache-control', 'expires',
               'cf-cache-status', 'x-cache', 'x-varnish', 'via', 'server')
USER_AGENT = 'Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)'


def bust(url, token):
    """Append a distinct, clearly labelled cache-busting argument to a public URL."""
    parts = urlsplit(url)
    query = urlencode([(k, v) for k, v in (pair.split('=', 1) for pair in parts.query.split('&') if pair)]
                      + [('_cb', token)])
    return parts._replace(query=query).geturl()


def ids_of(payload, as_json):
    rows = payload if as_json else hotspawn_state(payload)[0]
    if not isinstance(rows, list):
        raise ValueError('Unexpected fixture payload type %s' % type(rows).__name__)
    cs2 = [str(r['id']) for r in rows if isinstance(r, dict) and r.get('sport_alias') == 'cs2']
    if len(set(cs2)) != len(cs2):
        raise ValueError('Duplicate CS2 fixture IDs; coverage cannot be claimed')
    return sorted(set(cs2))


def fetch(session, url, as_json, attempts=2):
    last = None
    for attempt in range(attempts):
        record = {'url': url, 'requested_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}
        try:
            response = session.get(url, timeout=(10, 40))
            record['http_status'] = response.status_code
            response.raise_for_status()
            record['headers'] = {k: response.headers.get(k) for k in HEADER_KEYS if response.headers.get(k)}
            age = response.headers.get('Age')
            record['age_seconds'] = max(0, int(age)) if age is not None else None
            record['bytes'] = len(response.content)
            record['sha256'] = hashlib.sha256(response.content).hexdigest()
            body = response.json() if as_json else response.text
            if not as_json and any(marker in body.lower() for marker in
                                   ('not accepting visitors from your region', 'just a moment...', 'access denied')):
                raise ValueError('Access restriction or challenge page; not usable evidence')
            record['cs2_ids'] = ids_of(body, as_json)
            record['status'] = 'ok'
            return record
        except (requests.RequestException, ValueError, json.JSONDecodeError) as exc:
            record.update(status='error', error=str(exc)[:250])
            last = record
            if attempt + 1 < attempts:
                time.sleep(2)
    return last


def probe(nonce=None, pause_seconds=3):
    nonce = nonce or uuid.uuid4().hex[:12]
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    results = []
    for key, name, url, as_json in VIEWS:
        for variant in ('plain', 'bust-a', 'bust-b'):
            target = url if variant == 'plain' else bust(url, '%s-%s-%d' % (nonce, variant, int(time.time())))
            record = fetch(session, target, as_json)
            record.update(view=key, name=name, variant=variant, canonical_url=url,
                          cache_busted=variant != 'plain')
            results.append(record)
            time.sleep(pause_seconds)
    return {'probed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
            'nonce': nonce, 'requests': results, 'summary': summarise(results)}


def summarise(results):
    """Pure function over the receipts: no receipt, no claim."""
    summary = {}
    for key, _name, url, _json in VIEWS:
        rows = [r for r in results if r['view'] == key]
        plain = next((r for r in rows if r['variant'] == 'plain'), None)
        busted = [r for r in rows if r['cache_busted']]
        entry = {'url': url,
                 'plain_status': (plain or {}).get('status'),
                 'plain_age_seconds': (plain or {}).get('age_seconds'),
                 'plain_ids': len((plain or {}).get('cs2_ids') or []),
                 'busted': [{'variant': r['variant'], 'status': r['status'], 'url': r['url'],
                             'age_seconds': r.get('age_seconds'), 'bytes': r.get('bytes'),
                             'sha256': r.get('sha256'), 'ids': len(r.get('cs2_ids') or []),
                             'headers': r.get('headers'), 'error': r.get('error')} for r in busted]}
        ok_busted = [r for r in busted if r.get('status') == 'ok' and r.get('age_seconds') is not None]
        entry['cache_bust_measured'] = bool(ok_busted)
        entry['cache_bust_effective'] = bool(ok_busted) and all(r['age_seconds'] <= 60 for r in ok_busted)
        entry['same_object_as_plain'] = bool(plain and plain.get('sha256')
                                             and all(r.get('sha256') == plain['sha256'] for r in busted if r.get('sha256')))
        summary[key] = entry
    ids = {}
    for key in ('api', 'page', 'lobby'):
        for variant in ('plain', 'bust-a', 'bust-b'):
            row = next((r for r in results if r['view'] == key and r['variant'] == variant), None)
            if row and row.get('status') == 'ok':
                ids['%s/%s' % (key, variant)] = set(row['cs2_ids'])
    summary['id_sets'] = {k: len(v) for k, v in ids.items()}
    if {'api/plain', 'page/plain', 'lobby/plain'} <= set(ids):
        plain_sets = [ids['api/plain'], ids['page/plain'], ids['lobby/plain']]
        summary['plain_parity'] = all(s == plain_sets[0] for s in plain_sets)
        summary['plain_api_only'] = sorted(ids['api/plain'] - (ids['page/plain'] | ids['lobby/plain']))
        summary['plain_html_only'] = sorted((ids['page/plain'] | ids['lobby/plain']) - ids['api/plain'])
    busted_keys = ('api/bust-a', 'page/bust-a', 'lobby/bust-a')
    if set(busted_keys) <= set(ids):
        busted_sets = [ids[k] for k in busted_keys]
        summary['busted_parity'] = all(s == busted_sets[0] for s in busted_sets)
        summary['busted_api_only'] = sorted(ids['api/bust-a'] - (ids['page/bust-a'] | ids['lobby/bust-a']))
        summary['busted_html_only'] = sorted((ids['page/bust-a'] | ids['lobby/bust-a']) - ids['api/bust-a'])
    summary['conclusion'] = (
        'A distinct cache-busting argument returned a fresh copy of both HTML views '
        '(Age <= 60 s) and the three views agreed on the CS2 fixture ID set.'
        if all(summary[k]['cache_bust_effective'] for k in ('page', 'lobby')) and summary.get('busted_parity')
        else 'Cache-busting did not measurably defeat the CDN for at least one HTML view; '
             'the Age-derived observation time must keep anchoring the board. See the receipts.')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='research/harvest-3c8d1136/cdn-probe.json')
    parser.add_argument('--nonce', default=os.environ.get('GITHUB_RUN_ID'))
    args = parser.parse_args()
    report = probe(nonce=args.nonce)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + '\n')
    print(json.dumps(report['summary'], indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
