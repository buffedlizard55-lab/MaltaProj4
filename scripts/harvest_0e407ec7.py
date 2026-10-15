"""Assemble this session's research harvest without editing a single value.

The authoring sandbox reaches GitHub and package registries only, so the real
refresh runs on an Actions runner. This script only copies what the refresh and
the independent auditors already produced, re-derives counts from the snapshot
itself (never from a hand-written number) and records SHA-256 digests so every
figure quoted in the coordination log can be re-checked line by line.

It never publishes, never invents a probability and never modifies a row.
"""
import argparse
import collections
import datetime
import hashlib
import json
import pathlib
import shutil
import sys


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def summarise(snapshot, run_id, branch):
    matches = snapshot.get('matches') or []
    opens = [m for m in matches if m.get('state') == 'open']
    priced = [m for m in opens if m.get('probabilities')]
    research_only = [m for m in opens if m.get('pick') and not m.get('probabilities')]
    no_pick = [m for m in opens if not m.get('pick')]
    rows = []
    for m in sorted(opens, key=lambda r: (r.get('start') or '', r.get('id') or '')):
        rows.append({
            'id': m.get('id'),
            'teams': m.get('teams'),
            'competition': m.get('competition'),
            'tier': m.get('tier'),
            'start': m.get('start'),
            'lock': m.get('lock'),
            'best_of': m.get('best_of'),
            'state': m.get('state'),
            'probabilities': m.get('probabilities'),
            'fair_odds': m.get('fair_odds'),
            'pick': m.get('pick'),
            'method': m.get('method'),
            'reason': m.get('reason'),
            'flags': m.get('flags'),
            'evidence': [{'provider': e.get('provider'), 'url': e.get('url'), 'api_url': e.get('api_url'),
                          'observed_at': e.get('observed_at'), 'probabilities': e.get('probabilities')}
                         for e in (m.get('evidence') or [])],
            'attempts': m.get('attempts'),
        })
    return {
        'run_id': run_id,
        'branch': branch,
        'harvested_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
        'snapshot': {
            'generated_at': snapshot.get('generated_at'),
            'last_attempt_at': snapshot.get('last_attempt_at'),
            'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
            'coverage': snapshot.get('coverage'),
            'rows_total': len(matches),
            'rows_open': len(opens),
            'rows_open_with_prices': len(priced),
            'rows_open_with_pick_no_price': len(research_only),
            'rows_open_without_pick': len(no_pick),
            # Keys are stringified: a row with no method at all reports None, and
            # json.dumps(sort_keys=True) cannot order None against strings.
            'open_pick_methods': {str(k): v for k, v in collections.Counter(m.get('method') for m in opens).items()},
            'unresolved_open_ids': [m.get('id') for m in no_pick],
            'open_rows': rows,
            'issues': snapshot.get('issues'),
            'coverage_counts': snapshot.get('coverage_counts'),
            'inventory_changes': snapshot.get('inventory_changes'),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', default='runtime/latest.json')
    parser.add_argument('--output', default='research/harvest-0e407ec7')
    parser.add_argument('--run-id', type=int, default=None)
    parser.add_argument('--branch', default=None)
    parser.add_argument('--source-checks', action='store_true', help='Include the raw per-source access checks')
    args = parser.parse_args()

    out = pathlib.Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    runtime = pathlib.Path(args.runtime)
    if not runtime.exists():
        print('No refreshed snapshot at %s; nothing to harvest.' % runtime, file=sys.stderr)
        return 2
    snapshot = json.loads(runtime.read_text())
    if args.source_checks:
        summary = summarise(snapshot, args.run_id, args.branch)
        summary['snapshot']['source_checks'] = snapshot.get('source_checks')
    else:
        summary = summarise(snapshot, args.run_id, args.branch)
    (out / 'latest.json').write_text(json.dumps(snapshot, indent=1, sort_keys=True) + '\n')
    for name in ('row-audit.md', 'published-row-audit.md'):
        src = pathlib.Path('runtime') / name
        if src.exists():
            shutil.copyfile(src, out / name)
    for name in ('refresh.json', 'validate.json', 'build.json'):
        src = runtime.parent / name
        if src.exists():
            shutil.copyfile(src, out / name)
    files = sorted(p for p in out.iterdir() if p.is_file() and p.name != 'harvest-summary.json')
    summary['files'] = {p.name: digest(p) for p in files}
    (out / 'harvest-summary.json').write_text(json.dumps(summary, indent=1, sort_keys=True) + '\n')
    head = {k: v for k, v in summary['snapshot'].items() if k not in ('open_rows', 'source_checks', 'inventory_changes')}
    print(json.dumps(head, indent=1, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
