"""Read-only diagnostics for session d15e84e5 (never publishes anything).

Why this exists
---------------
On 2026-10-24 the scheduled publisher went red at step 15 of
``.github/workflows/pages.yml`` ("Keep the legacy main:/ root fallback on the
verified build") on every run after 08:26Z, while steps 8-14 (unit gate,
refresh, independent audit, build, validate, browser suites) passed. Because the
deploy job needs that step, the public board froze at the 08:06Z snapshot and
then withheld every pick once its eight-hour evidence window closed.

The job logs are not readable from the session that has to repair this (the
log and artifact download hosts are outside its egress allow list), so the
failing gate has to be identified from the run's own *annotations*. This module
turns a fresh read-only refresh into a small, annotated report:

* what Hotspawn actually listed at the refresh minute (row counts, coverage,
  open rows, methods, unresolved rows with their recorded reason and attempted
  providers);
* the result of the exact two commands step 15 runs after staging
  (``scripts.validate --data data/latest.json --site .`` and
  ``unittest discover -s tests``) against a freshly staged root.

It only prints. It writes no site file, no snapshot and no receipt, and it never
touches git.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


def _escape(text):
    """One-line workflow-command payload (GitHub strips newlines in annotations)."""
    text = str(text).replace('\r', ' ').replace('\n', ' | ')
    return re.sub(r'\s+', ' ', text).strip()[:3500]


def annotate(level, title, text):
    print('::%s title=%s::%s' % (level, _escape(title), _escape(text)), flush=True)


def snapshot_summary(data):
    matches = data.get('matches') or []
    open_rows = [m for m in matches if m.get('state') == 'open']
    priced = [m for m in open_rows if m.get('probabilities') is not None]
    unresolved = [m for m in open_rows if not m.get('pick')]
    return {
        'generated_at': data.get('generated_at'),
        'fixtures_observed_at': data.get('fixtures_observed_at'),
        'coverage': data.get('coverage'),
        'rows': len(matches),
        'states': dict(Counter(m.get('state') for m in matches)),
        'open': len(open_rows),
        'open_with_pick': sum(1 for m in open_rows if m.get('pick')),
        'open_with_probability': len(priced),
        'methods': dict(Counter(m.get('method') or 'none' for m in open_rows)),
        'coverage_counts': data.get('coverage_counts'),
        'unresolved': [
            {
                'id': m.get('id'),
                'teams': m.get('teams'),
                'competition': m.get('competition'),
                'tier': m.get('tier'),
                'start': m.get('start'),
                'reason': m.get('reason'),
                'attempts': [
                    {'provider': a.get('provider'), 'status': a.get('status'),
                     'reason': a.get('reason'), 'url': a.get('url')}
                    for a in (m.get('attempts') or [])
                ],
            }
            for m in unresolved
        ],
        'issues': data.get('issues'),
        'fixture_conflicts': data.get('fixture_conflicts'),
        'inventory_changes': data.get('inventory_changes'),
        'source_checks': [
            {'name': c.get('name'), 'url': c.get('url'), 'status': c.get('status'),
             'error': c.get('error')}
            for c in (data.get('source_checks') or [])
        ],
    }


def emit_summary(path):
    data = json.loads(Path(path).read_text())
    summary = snapshot_summary(data)
    annotate('notice', 'd15e84e5 snapshot', json.dumps(
        {k: summary[k] for k in ('generated_at', 'fixtures_observed_at', 'coverage', 'rows',
                                 'states', 'open', 'open_with_pick', 'open_with_probability',
                                 'methods', 'coverage_counts')}, ensure_ascii=False))
    for item in summary['unresolved']:
        annotate('warning', 'unresolved %s' % item['id'], json.dumps(item, ensure_ascii=False))
    if not summary['unresolved']:
        annotate('notice', 'd15e84e5 unresolved', 'no open row lacks a pick')
    for check in summary['source_checks']:
        if check.get('status') not in (None, 'ok', 'fresh'):
            annotate('warning', 'source %s' % check.get('name'), json.dumps(check, ensure_ascii=False))
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    return summary


def emit_gates(validate_log, unit_log):
    for label, path in (('validate', validate_log), ('unit', unit_log)):
        try:
            text = Path(path).read_text(errors='replace')
        except OSError as error:
            annotate('error', 'd15e84e5 %s' % label, 'no log: %s' % error)
            continue
        failures = [line.strip() for line in text.splitlines()
                    if line.startswith(('FAIL:', 'ERROR:', 'AssertionError', 'Traceback'))
                    or 'altered primary fact' in line]
        annotate('notice', 'd15e84e5 %s result' % label, 'tail: ' + ' | '.join(
            line.strip() for line in text.strip().splitlines()[-12:]))
        if failures:
            annotate('warning', 'd15e84e5 %s failures' % label,
                     ' | '.join(failures[:25]))
        else:
            annotate('notice', 'd15e84e5 %s failures' % label, 'none')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('snapshot', nargs='?', default=None,
                        help='snapshot JSON to summarise (read-only)')
    parser.add_argument('--emit', action='store_true', help='print workflow annotations')
    parser.add_argument('--emit-gates', nargs=2, metavar=('VALIDATE_LOG', 'UNIT_LOG'), default=None)
    args = parser.parse_args(argv)
    if args.emit_gates:
        emit_gates(*args.emit_gates)
        return 0
    if not args.snapshot:
        parser.error('a snapshot path is required unless --emit-gates is used')
    if args.emit:
        emit_summary(args.snapshot)
    else:
        print(json.dumps(snapshot_summary(json.loads(Path(args.snapshot).read_text())),
                         indent=1, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
