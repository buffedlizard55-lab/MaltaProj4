"""Dated copies of Valve's official global standings, for past fixtures.

Valve publishes the standings monthly
(``ValveSoftware/counter-strike_regional_standings/live/<year>/standings_global_<Y>_<M>_<D>.md``).
The refresh pipeline only ever needs the newest file, because it prices matches
that have not started. But the Hotspawn fixture feed still returns CS2 rows from
June 2026, and pricing a June fixture with October standings is wrong twice
over: the points have moved, and a label the October file repeats for two
different rosters may have been unique in June.

So the historical ladder uses the newest official file whose ``as_of`` date is
on or before the fixture's own sourced start. Each copy here is Valve's file
byte-for-byte, with the commit it came from, so any consumer can re-fetch and
compare. ``data/vrs/history.json`` is the index; the ``.md`` files sit beside
it under ``data/vrs/history/``.

Nothing in this module invents a value. A file whose bytes do not match the
published blob is rejected, and a fixture older than every vendored file is
priced from the oldest one with that stated explicitly on the row.
"""
import base64
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from scripts import vrs
from scripts.core import iso

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'data' / 'vrs' / 'history'
INDEX = ROOT / 'data' / 'vrs' / 'history.json'


def _fetch_json(url, headers):
    import urllib.request
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode())


def fetch_history(years=None, token=None, now=None):
    """Vendor every global standings file Valve publishes for these years.

    Best-effort: any failure leaves the already-vendored copies untouched and
    returns the problem string, because a refresh must not fail on the
    historical tier alone.
    """
    now = now or datetime.now(timezone.utc)
    # One year of monthly files is ~750 KB and covers every fixture the feed
    # returns; older copies are not needed and would only bloat the repository.
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'hotspawn-cs2-scout'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    try:
        names = []
        for year in years or (now.year,):
            listing = _fetch_json(vrs.API + '/contents/live/%d' % year, headers)
            names += ['live/%d/%s' % (year, x['name']) for x in listing if vrs.FILE_RE.match(x.get('name', ''))]
        if not names:
            return 'No global standings files found in the official repository'
        DIR.mkdir(parents=True, exist_ok=True)
        previous = {}
        if INDEX.is_file():
            previous = {e['file']: e for e in json.loads(INDEX.read_text()).get('files', [])}
        entries = []
        for path in sorted(names):
            name = path.rsplit('/', 1)[1]
            commits = _fetch_json(vrs.API + '/commits?path=%s&per_page=1' % path, headers)
            commit = commits[0]['sha']
            raw_url = '%s/%s/%s' % (vrs.RAW, commit, path)
            blob = _fetch_json('%s/contents/%s?ref=%s' % (vrs.API, path, commit), headers)
            text = base64.b64decode(blob['content'])
            standings = vrs.parse(text.decode())  # fails closed on a malformed table
            year = vrs.FILE_RE.match(name).group(1)
            entry = {
                'file': name,
                'path': path,
                'as_of': standings['as_of'],
                'teams': len(standings['teams']),
                'commit': commit,
                'raw_url': raw_url,
                'blob_url': '%s/%s/%s' % (vrs.BLOB, commit, path),
                'details_base': '%s/%s/live/%s/' % (vrs.BLOB, commit, year),
                'sha256': hashlib.sha256(text).hexdigest(),
                'bytes': len(text),
                'observed_at': iso(now),
                'origin': 'live official repository',
            }
            # Valve's published bytes for a past month never change, so the
            # index must not churn on every refresh: keep the first observation
            # time when the copy is byte-identical to the one already vendored.
            old = previous.get(name)
            if old and old.get('sha256') == entry['sha256'] and old.get('commit') == commit:
                entry['observed_at'] = old.get('observed_at') or entry['observed_at']
            entries.append(entry)
            (DIR / name).write_bytes(text)
        index = {
            'schema_version': 1,
            'repository': vrs.OWNER_REPO,
            'note': ('Unmodified copies of Valve\'s official monthly global standings files, kept so a past fixture is '
                     'priced from the ranking that was current when it was scheduled. Every number the historical '
                     'ladder publishes is re-derivable from these bytes plus Valve\'s own published formula.'),
            'updated_at': iso(now),
            'files': entries,
        }
        # The stamp only moves when Valve actually published something new, so a
        # refresh that changes nothing leaves the committed index untouched.
        if INDEX.is_file():
            existing = json.loads(INDEX.read_text())
            if existing.get('files') == entries:
                index['updated_at'] = existing.get('updated_at') or index['updated_at']
        INDEX.write_text(json.dumps(index, indent=2) + '\n')
        return None
    except Exception as exc:  # noqa: BLE001 - best-effort tier, never fails a refresh
        return 'Dated standings vendoring failed (%s); existing copies used.' % str(exc)[:160]


def load():
    """The vendored dated files, oldest first, as (standings, meta) pairs."""
    if not INDEX.is_file():
        return []
    index = json.loads(INDEX.read_text())
    out = []
    for entry in index['files']:
        path = DIR / entry['file']
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError('Vendored standings copy does not match its published checksum: ' + entry['file'])
        meta = dict(entry)
        meta['observed_at'] = entry.get('observed_at') or iso(datetime.now(timezone.utc))
        out.append((vrs.parse(raw.decode()), meta))
    out.sort(key=lambda pair: pair[0]['as_of'])
    return out


def select(start_iso, history):
    """(standings, meta, note) for a fixture start, or (None, None, why).

    The newest file published on or before the fixture's start date is the
    ranking that was current when the match was scheduled. A fixture older than
    every vendored file falls back to the oldest one and says so.
    """
    if not history:
        return None, None, 'No dated Valve standings copy is vendored in this repository.'
    from scripts.core import dt
    try:
        start = dt(start_iso).date()
    except (TypeError, ValueError, OverflowError, OSError):
        return history[-1][0], history[-1][1], 'Fixture start is unverifiable, so the newest dated copy was used.'
    applicable = [pair for pair in history if _date(pair[0]['as_of']) <= start]
    if applicable:
        standings, meta = applicable[-1]
        return standings, meta, None
    standings, meta = history[0]
    return standings, meta, ('The fixture predates every vendored copy of Valve\'s standings, so the oldest available '
                            '(%s) was used and may post-date the fixture.' % standings['as_of'])


def _date(value):
    return datetime.strptime(value, '%Y-%m-%d').date()
