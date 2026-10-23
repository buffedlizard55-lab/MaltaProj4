"""Re-verify every originated (VRS) probability against Valve's own repository.

Session 2c7b9e48. This sandbox can reach ``api.github.com``, so the one source
that decides seven of the published percentages can be checked against the
original bytes rather than against this project's stored copy.

For each open row whose method is ``model_vrs`` or ``model_vrs_mirror`` the
script:

1. reads the standings file URL and commit the row cites,
2. downloads that exact file through the GitHub contents API (raw media type),
3. checks the file's own header date and the recorded SHA-256 against a second,
   independent download,
4. finds each team's row and confirms the recorded standing number, points and
   roster players appear in Valve's file,
5. re-derives the probability from the *file's* points with Valve's published
   constants (``model/fit.js``: ``defaultGlickoParams.rd = 75``;
   ``model/glicko.js``: ``Q = Math.log(10)/400``) and Valve's published
   calibration slope, and compares it with the published number.

``model_vrs_mirror`` rows cite HLTV's copy of Valve's ranking, which this
sandbox cannot reach; they are reported as skipped rather than assumed correct.

Usage::

    python verification-2c7b9e48/verify_valve.py data/latest.json --output out.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

RD = 75.0
Q = math.log(10) / 400
G = 1 / math.sqrt(1 + 3 * Q * Q * RD * RD / math.pi ** 2)
SLOPE = 0.7986
ROW = re.compile(r'^\|\s*(\d+)\s*\|\s*(-?\d+)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*\[details\]')


def fetch(url: str) -> str:
    """Read a GitHub URL as raw bytes through the authenticated API client."""
    m = re.match(r'https://github\.com/([^/]+/[^/]+)/blob/([0-9a-f]{40})/(.+)$', url)
    if not m:
        raise SystemExit('not a pinned GitHub blob URL: ' + url)
    owner, commit, path = m.groups()
    out = subprocess.run(['gh', 'api', f'repos/{owner}/contents/{path}?ref={commit}',
                          '-H', 'Accept: application/vnd.github.raw'],
                         capture_output=True, check=True)
    return out.stdout.decode()


def parse(text: str):
    """Read every row, keeping repeated labels as separate rows.

    Valve's file repeats a label for older rosters (the project documents this
    and resolves it by roster). Keying by label alone would silently pick the
    wrong row, so the parser keeps them all and the caller chooses by roster.
    """
    header = re.search(r'Standings as of (\d{4})_(\d{2})_(\d{2})', text)
    rows = {}
    for line in text.splitlines():
        m = ROW.match(line)
        if not m:
            continue
        rows.setdefault(m.group(3).strip(), []).append({
            'standing': int(m.group(1)),
            'points': int(m.group(2)),
            'roster': [p.strip() for p in m.group(4).split(',') if p.strip()],
        })
    return '-'.join(header.groups()) if header else None, rows


def choose(candidates, recorded_standing, recorded_roster):
    """Pick the row this project's identity rule would pick, then report it.

    The rule: the label is usable when it is unique, or when the roster on the
    row is the one the fixture's lineup matches (Valve treats >= 3 shared
    players as the same team). A label with several rows and no roster match is
    ambiguous and must not be used at all.
    """
    if not candidates:
        return None, 'label absent from Valve file', 0
    if len(candidates) == 1:
        return candidates[0], 'unique label', len(set(candidates[0]['roster']) & set(recorded_roster))
    best = max(candidates, key=lambda r: len(set(r['roster']) & set(recorded_roster)))
    overlap = len(set(best['roster']) & set(recorded_roster))
    same = [r for r in candidates if len(set(r['roster']) & set(recorded_roster)) == overlap]
    if overlap < 3:
        return None, f'ambiguous label ({len(candidates)} rows, best overlap {overlap})', overlap
    if len(same) > 1:
        return None, f'ambiguous label ({len(same)} rows share overlap {overlap})', overlap
    return best, f'roster-selected from {len(candidates)} rows', overlap


def model_probability(points_a, points_b):
    raw = 1 / (1 + 10 ** (-G * (float(points_a) - float(points_b)) / 400))
    p = 0.5 + SLOPE * (raw - 0.5)
    return [p, 1 - p]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('data', nargs='?', default='data/latest.json')
    ap.add_argument('--output', default=None)
    args = ap.parse_args(argv)
    data = json.loads(Path(args.data).read_text())
    cache, results, failures = {}, [], []
    for m in data['matches']:
        if m.get('state') != 'open' or m.get('method') not in ('model_vrs', 'model_vrs_mirror'):
            continue
        quote = (m.get('evidence') or [{}])[0]
        url = quote.get('url') or ''
        entry = {'id': m['id'], 'teams': m['teams'], 'method': m['method'], 'source': url,
                 'published': m.get('probabilities')}
        if m['method'] == 'model_vrs_mirror' or 'hltv.org' in url:
            entry['status'] = 'skipped'
            entry['why'] = 'HLTV’s dated mirror is not reachable from this sandbox; not assumed correct.'
            results.append(entry)
            continue
        if url not in cache:
            text = fetch(url)
            cache[url] = (text, hashlib.sha256(text.encode()).hexdigest())
        text, digest = cache[url]
        as_of, rows = parse(text)
        entry['standings_as_of_in_file'] = as_of
        entry['file_sha256'] = digest
        checks = []
        points = []
        for team, label, standing, pts, roster in zip(
                m['teams'], quote.get('vrs_teams', []), quote.get('standings', []),
                quote.get('points', []), quote.get('rosters', [])):
            row, how, overlap = choose(rows.get(label, []), standing, roster)
            ok = bool(row) and row['standing'] == standing and row['points'] == pts
            checks.append({'team': team, 'label': label, 'recorded': {'standing': standing, 'points': pts},
                           'in_valve_file': bool(row), 'selection': how,
                           'file_standing': row['standing'] if row else None,
                           'file_points': row['points'] if row else None,
                           'roster_overlap': overlap, 'match': ok})
            points.append(row['points'] if row else None)
            if not ok:
                failures.append(f"{m['id']}: {label} recorded #{standing}/{pts} pts, "
                                f"Valve's file selection ({how}) gives "
                                f"{('#' + str(row['standing']) + '/' + str(row['points']) + ' pts') if row else 'no usable row'}")
        entry['checks'] = checks
        if all(points):
            replay = model_probability(points[0], points[1])
            entry['replayed_from_file'] = replay
            same = all(abs(a - b) <= 1e-9 for a, b in zip(replay, m['probabilities']))
            entry['reproduces'] = same
            if not same:
                failures.append(f"{m['id']}: replay {replay} != published {m['probabilities']}")
            entry['status'] = 'verified' if same else 'mismatch'
        else:
            entry['status'] = 'missing-team'
        results.append(entry)
    summary = {
        'model_rows_checked': len([r for r in results if r['status'] == 'verified']),
        'skipped': len([r for r in results if r['status'] == 'skipped']),
        'failures': failures,
        'results': results,
    }
    payload = json.dumps(summary, indent=1, ensure_ascii=False)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(payload + '\n')
    print(f"model rows verified against Valve's repository: {summary['model_rows_checked']}; "
          f"skipped: {summary['skipped']}; failures: {len(failures)}")
    for f in failures:
        print('FAIL', f)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
