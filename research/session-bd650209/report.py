"""Line-by-line report for session bd650209's reproduction runs.

Reads one refreshed snapshot (and, when present, the built copy) and prints the
facts this session is accountable for, so the numbers in COORDINATION.md are
copied from a committed receipt instead of being recalled:

* how many feed rows there are and how many are open;
* for every open row: pick, method, both probabilities, expiry, reason;
* which open rows have no pick and which have a pick but no probability;
* which rows carry a probability without a directional pick (the contract that
  froze the publisher on 2026-10-24);
* the method mix and the coverage block of the snapshot;
* whether the "unresolved" rows name a fixture URL and their attempts.

Nothing is computed that the snapshot does not already contain.
"""
import argparse
import collections
import json
import sys
from pathlib import Path


def load(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def pct(v):
    return '—' if v is None else '%.1f%%' % (float(v) * 100.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('snapshot')
    ap.add_argument('--built', default=None, help='public/data/latest.json when the build succeeded')
    ap.add_argument('--json', default=None, help='write the same facts as JSON here')
    args = ap.parse_args()

    d = load(args.snapshot)
    matches = d.get('matches') or []
    open_rows = [m for m in matches if m.get('state') == 'open']

    no_pick = [m for m in open_rows if not m.get('pick')]
    pick_no_prob = [m for m in open_rows if m.get('pick') and m.get('probabilities') is None]
    priced_no_pick = [m for m in open_rows if m.get('probabilities') is not None and not m.get('pick')]
    priced = [m for m in open_rows if m.get('probabilities') is not None]

    methods = collections.Counter(str(m.get('method')) for m in open_rows)
    states = collections.Counter(str(m.get('state')) for m in matches)

    print('== snapshot')
    for k in ('schema_version', 'generated_at', 'last_attempt_at', 'refresh_started_at',
              'fixtures_observed_at', 'coverage', 'refresh_hours', 'stale_after_hours', 'built_at'):
        print('%-22s %s' % (k, d.get(k)))
    print('%-22s %s' % ('rows', len(matches)))
    print('%-22s %s' % ('states', dict(states)))
    print('%-22s %s' % ('open', len(open_rows)))
    print('%-22s %s' % ('open_with_pick', len(open_rows) - len(no_pick)))
    print('%-22s %s' % ('open_with_probability', len(priced)))
    print('%-22s %s' % ('priced_without_pick', len(priced_no_pick)))
    print('%-22s %s' % ('pick_without_probability', len(pick_no_prob)))
    print('%-22s %s' % ('no_pick', len(no_pick)))
    print('%-22s %s' % ('method_mix', dict(methods)))
    print('%-22s %s' % ('coverage_counts', d.get('coverage_counts')))
    print('%-22s %s' % ('issues', d.get('issues')))

    print('\n== every open row')
    for m in sorted(open_rows, key=lambda r: (str(r.get('start')), str(r.get('id')))):
        probs = m.get('probabilities') or [None, None]
        print('%s %s | %s vs %s | %s | %s | %s | pick=%s | method=%s | expires=%s' % (
            m.get('id'), m.get('start'), (m.get('teams') or ['?', '?'])[0], (m.get('teams') or ['?', '?'])[1],
            pct(probs[0]), pct(probs[1]), m.get('tier'), m.get('pick'), m.get('method'), m.get('expires_at')))
        if m.get('reason'):
            print('    reason: %s' % m.get('reason'))
        for a in (m.get('attempts') or [])[:8]:
            print('    attempt: %s' % json.dumps(a, sort_keys=True)[:300])

    if no_pick or pick_no_prob or priced_no_pick:
        print('\n== contract problems')
        for m in no_pick:
            print('NO PICK: %s %s vs %s (%s)' % (m.get('id'), (m.get('teams') or ['?', '?'])[0],
                                                (m.get('teams') or ['?', '?'])[1], m.get('reason')))
        for m in pick_no_prob:
            print('PICK WITHOUT PROBABILITY: %s %s -> %s (%s)' % (
                m.get('id'), m.get('teams'), m.get('pick'), m.get('method')))
        for m in priced_no_pick:
            print('PROBABILITY WITHOUT PICK: %s %s %s' % (m.get('id'), m.get('teams'), m.get('probabilities')))

    evidence = d.get('fixture_evidence') or {}
    print('\n== unresolved-row source completeness (audit contract)')
    missing_url = []
    missing_attempts = []
    for m in no_pick:
        ev = evidence.get(str(m.get('id'))) if isinstance(evidence, dict) else None
        urls = [u for u in ((ev or {}).get('sources') or []) if isinstance(u, dict)]
        if not urls:
            missing_url.append(m.get('id'))
        if not (m.get('attempts') or []):
            missing_attempts.append(m.get('id'))
    print('unresolved_without_official_fixture_url %s' % (missing_url or 0))
    print('unresolved_without_source_attempts   %s' % (missing_attempts or 0))

    if args.built:
        b = load(args.built)
        bopen = [m for m in b.get('matches') or [] if m.get('state') == 'open']
        print('\n== built copy')
        print('rows %s | open %s | picks %s | probabilities %s' % (
            len(b.get('matches') or []), len(bopen),
            sum(1 for m in bopen if m.get('pick')),
            sum(1 for m in bopen if m.get('probabilities') is not None)))

    if args.json:
        Path(args.json).write_text(json.dumps({
            'snapshot': args.snapshot,
            'generated_at': d.get('generated_at'),
            'fixtures_observed_at': d.get('fixtures_observed_at'),
            'rows': len(matches),
            'states': dict(states),
            'open': len(open_rows),
            'open_with_pick': len(open_rows) - len(no_pick),
            'open_with_probability': len(priced),
            'no_pick': [{'id': m.get('id'), 'teams': m.get('teams'), 'reason': m.get('reason'),
                         'attempts': len(m.get('attempts') or [])} for m in no_pick],
            'pick_without_probability': [{'id': m.get('id'), 'teams': m.get('teams'),
                                          'pick': m.get('pick'), 'method': m.get('method')} for m in pick_no_prob],
            'priced_without_pick': [{'id': m.get('id'), 'teams': m.get('teams'),
                                     'probabilities': m.get('probabilities')} for m in priced_no_pick],
            'method_mix': dict(methods),
            'coverage': d.get('coverage'),
            'coverage_counts': d.get('coverage_counts'),
            'issues': d.get('issues'),
            'unresolved_without_fixture_url': missing_url,
            'unresolved_without_attempts': missing_attempts,
        }, indent=1, sort_keys=True), encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
