"""Session 0b26ea9a: capture the refreshed board and audit every open fixture.

This module never invents a value. It reads a snapshot produced by
``python -m scripts.refresh`` and writes, under ``research/session-0b26ea9a/``:

* ``snapshot-<stamp>.json``  - the exact refreshed snapshot (the primary capture),
* ``gaps-<stamp>.json``      - one record per open fixture, with the pick, the
  method, both probabilities (or null), and every recorded attempt,
* ``GAPS-<stamp>.md``        - the same, in a form a human can read line by line.

The refresh runs on GitHub's runners because this project's sandbox cannot open
the public sources directly; the committed files are the dated capture, not a
hand-edited copy of a live value.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE_DIR = ROOT / 'research' / 'session-0b26ea9a'
MARKET_METHODS = ('exchange', 'exchange_wide', 'pinnacle', 'bookmaker_fallback')
MODEL_METHODS = ('model_vrs',)


def stamp(generated_at: str) -> str:
    """A filesystem-safe stamp derived from the snapshot, never from the clock."""
    cleaned = (generated_at or '').replace('-', '').replace(':', '').replace('.', '')
    cleaned = cleaned.replace('T', 'T').replace('Z', 'Z')
    return cleaned or datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def attempt_line(attempt: dict) -> str:
    return '%s: %s - %s (%s)' % (
        attempt.get('provider') or '?',
        attempt.get('status') or '?',
        (attempt.get('reason') or '').strip().replace('\n', ' '),
        attempt.get('url') or 'no url',
    )


def gap_record(match: dict) -> dict:
    probabilities = match.get('probabilities')
    pick = match.get('pick')
    method = match.get('method')
    if probabilities is not None:
        kind = 'market' if method in MARKET_METHODS else ('model' if method in MODEL_METHODS else 'other')
    elif pick:
        kind = 'research-only (no percentage)'
    else:
        kind = 'no pick'
    return {
        'id': str(match.get('id')),
        'teams': match.get('teams'),
        'competition': match.get('competition'),
        'tier': match.get('tier'),
        'start': match.get('start'),
        'lock': match.get('lock'),
        'state': match.get('state'),
        'pick': pick,
        'method': method,
        'probability': probabilities,
        'kind': kind,
        'expires_at': match.get('expires_at'),
        'evidence': [{k: e.get(k) for k in ('provider', 'url', 'observed_at', 'expires_at', 'probabilities')}
                     for e in (match.get('evidence') or [])],
        'hltv_context': (match.get('hltv_context') or {}).get('source'),
        'attempts': [attempt_line(a) for a in (match.get('attempts') or [])],
        'flags': match.get('flags') or [],
        'reason': match.get('reason'),
    }


def build_capture(snapshot: dict) -> tuple[dict, str]:
    opens = [m for m in snapshot.get('matches', []) if m.get('state') == 'open']
    records = sorted((gap_record(m) for m in opens), key=lambda r: (r.get('start') or '', r['id']))
    counts: dict[str, int] = {}
    for record in records:
        counts[record['kind']] = counts.get(record['kind'], 0) + 1
    capture = {
        'schema_version': 1,
        'session': '0b26ea9a',
        'snapshot_generated_at': snapshot.get('generated_at'),
        'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
        'coverage': snapshot.get('coverage'),
        'rows_total': len(snapshot.get('matches', [])),
        'rows_open': len(opens),
        'counts_by_kind': counts,
        'gaps': records,
        'source_checks': [{k: c.get(k) for k in ('name', 'url', 'status', 'http_status', 'observed_at', 'error')}
                          for c in snapshot.get('source_checks', [])],
        'issues': snapshot.get('issues', []),
    }
    lines = [
        '# Session 0b26ea9a capture - %s' % (snapshot.get('generated_at') or 'unknown time'),
        '',
        'Snapshot `%s`, fixture observation `%s`, coverage **%s**.' % (
            snapshot.get('generated_at'), snapshot.get('fixtures_observed_at'), snapshot.get('coverage')),
        '',
        '| Open rows | %d | Total feed rows | %d |' % (len(opens), len(snapshot.get('matches', []))),
        '| --- | --- | --- | --- |',
        '',
        '## Counts by kind',
        '',
    ]
    for kind, count in sorted(counts.items()):
        lines.append('- **%s**: %d' % (kind, count))
    lines += ['', '## Every open fixture', '',
              '| Fixture | Teams | Start (UTC) | Pick | Probability | Method |',
              '| --- | --- | --- | --- | --- | --- |']
    for r in records:
        prob = '-'
        if r['probability'] is not None:
            prob = ' / '.join('%.1f%%' % (p * 100) for p in r['probability'])
        lines.append('| %s | %s | %s | %s | %s | %s |' % (
            r['id'], ' vs '.join(r['teams'] or []), r['start'] or '-', r['pick'] or '-',
            prob, r['method'] or '-'))
    for r in records:
        if r['kind'] in ('market', 'model'):
            continue
        lines += ['', '### %s - %s' % (r['id'], ' vs '.join(r['teams'] or [])),
                  '', '- Kind: **%s**' % r['kind'], '- Start: %s' % (r['start'] or '-'),
                  '- Reason: %s' % (r['reason'] or '-')]
        if r['attempts']:
            lines.append('- Attempts:')
            for a in r['attempts']:
                lines.append('  - %s' % a)
        if r['flags']:
            lines.append('- Flags: %s' % '; '.join(r['flags']))
    problems = [i for i in snapshot.get('issues', []) if i.get('code') != 'feed_status']
    if problems:
        lines += ['', '## Snapshot issues (excluding the routine feed_status note)', '']
        for issue in problems:
            lines.append('- **%s**: %s (%s)' % (issue.get('code'), issue.get('message'), issue.get('source')))
    return capture, '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output', default=str(CAPTURE_DIR))
    args = parser.parse_args()
    snapshot = json.loads(Path(args.snapshot).read_text())
    capture, markdown = build_capture(snapshot)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    when = stamp(snapshot.get('generated_at'))
    (out / ('snapshot-%s.json' % when)).write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    (out / ('gaps-%s.json' % when)).write_text(json.dumps(capture, indent=2, ensure_ascii=False) + '\n')
    (out / ('GAPS-%s.md' % when)).write_text(markdown)
    (out / 'LATEST.md').write_text(markdown)
    print(json.dumps({'snapshot': when, 'rows_open': capture['rows_open'],
                      'counts_by_kind': capture['counts_by_kind']}, indent=2))


if __name__ == '__main__':
    main()
