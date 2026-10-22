"""Session 2ec8cd6c — re-verify the VRS model's official input against its primary source.

Live-reads Valve's official counter-strike_regional_standings repository through
the GitHub contents API (the only official source reachable from the authoring
sandbox; GitHub-hosted runners have the same access), then byte-compares the
newest official global standings file with the vendored copy the build falls
back on and with the file the snapshot's model rows cite. Writes a dated
receipt, valve-file-receipt.json, beside this file.

Exit code 0 iff the vendored copy is byte-identical to the live official file
and the file the snapshot cites is that same official file.
"""
import datetime
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API = 'https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings'
FILE_RE = 'standings_global_'


def get(url, accept='application/vnd.github+json'):
    req = urllib.request.Request(url, headers={'Accept': accept, 'User-Agent': 'cs2-scout-session-2ec8cd6c'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.read()


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    receipt = {'session': '2ec8cd6c', 'observed_at': now.strftime('%Y-%m-%dT%H:%M:%SZ')}

    status, body = get(API + '/contents/live/2026')
    entries = json.loads(body)
    global_files = sorted(e['name'] for e in entries if e['name'].startswith(FILE_RE) and e['name'].endswith('.md'))
    receipt['listing'] = {
        'url': API + '/contents/live/2026',
        'http_status': status,
        'global_files': global_files,
        'newest_global_file': global_files[-1] if global_files else None,
    }

    newest = global_files[-1]
    status, live_bytes = get(API + '/contents/live/2026/' + newest, accept='application/vnd.github.raw')
    live_sha = hashlib.sha256(live_bytes).hexdigest()
    receipt['live_file'] = {
        'url': API + '/contents/live/2026/' + newest,
        'http_status': status,
        'bytes': len(live_bytes),
        'sha256': live_sha,
    }

    meta = json.loads((ROOT / 'data' / 'vrs' / 'meta.json').read_text())
    vendored = ROOT / 'data' / 'vrs' / meta['file']
    vendored_sha = hashlib.sha256(vendored.read_bytes()).hexdigest()
    receipt['vendored_file'] = {
        'path': str(vendored.relative_to(ROOT)),
        'meta': meta,
        'sha256': vendored_sha,
    }

    snap = json.loads((ROOT / 'data' / 'latest.json').read_text())
    cited = None
    for m in snap['matches']:
        for ev in m.get('evidence') or []:
            if ev.get('provider') == 'Valve VRS model' and ev.get('standings_file'):
                cited = ev['standings_file']
                break
        if cited:
            break
    receipt['snapshot_cited_file'] = cited

    ok = (
        newest == meta['file']
        and live_sha == vendored_sha
        and cited == meta['file']
        and vendored_sha == meta.get('sha256')
    )
    receipt['checks'] = {
        'newest_official_file_matches_vendored_meta': newest == meta['file'],
        'vendored_bytes_equal_live_official_bytes': live_sha == vendored_sha,
        'snapshot_model_rows_cite_the_same_official_file': cited == meta['file'],
        'vendored_sha_matches_recorded_sha': vendored_sha == meta.get('sha256'),
    }
    receipt['status'] = 'pass' if ok else 'fail'

    out = Path(__file__).resolve().parent / 'valve-file-receipt.json'
    out.write_text(json.dumps(receipt, indent=1) + '\n')
    print(json.dumps(receipt, indent=1))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
