"""Name the exact row that fails ``scripts.validate``, offline.

``scripts.validate.validate_data`` fails on the first bad row with a bare
assertion message and no fixture id, which is why the red publication gate on
main read only ``Model roster has no HLTV source on this row`` and nothing else.

This replays the repository's *own* ``validate_data`` once per priced row, on a
one-row copy of the snapshot (that row in ``matches`` and in
``fixture_evidence``, so the completeness assertion still holds), and prints the
fixture id, both team labels, the method and the assertion text for every row
that fails. It never edits the snapshot and never relaxes a check.
"""
import argparse
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts import validate as V  # noqa: E402


def replay(data, match):
    one = copy.deepcopy(data)
    one['matches'] = [copy.deepcopy(match)]
    one['fixture_evidence'] = [e for e in data['fixture_evidence']
                               if str(e.get('id')) == str(match.get('id'))]
    V.validate_data(one)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('snapshot')
    args = ap.parse_args()
    data = json.loads(Path(args.snapshot).read_text())
    priced = [m for m in data['matches'] if m.get('evidence')]
    failures = []
    for m in priced:
        try:
            replay(data, m)
        except AssertionError as exc:
            failures.append((m, str(exc)))
        except (KeyError, TypeError, ValueError) as exc:
            failures.append((m, '%s: %s' % (type(exc).__name__, exc)))
    print('priced rows replayed one at a time: %d' % len(priced))
    print('rows failing the repository validator: %d' % len(failures))
    for m, message in failures:
        print('FAIL %s | %s | %s | %s' % (m.get('id'), ' vs '.join(m.get('teams') or []),
                                          m.get('method'), message))
        q = (m.get('evidence') or [{}])[0]
        print('     vrs_teams       : %s' % (q.get('vrs_teams'),))
        print('     label_counts    : %s' % (q.get('label_counts'),))
        print('     roster_checks   : %s' % json.dumps(q.get('roster_checks'))[:500])
        ctx = m.get('hltv_context') or {}
        print('     hltv lineups    : %s' % [(i.get('team'), len(i.get('players') or []))
                                             for i in (ctx.get('lineups') or [])])
        print('     hltv team pages : %s' % [(i.get('team'), len(i.get('lineup') or []))
                                             for i in ((m.get('hltv_team_pages') or {}).get('teams') or [])])
        print('     qualifications  : %s' % json.dumps({k: v for k, v in m.items()
                                                       if k in ('state', 'method', 'pick', 'flags', 'reason')})[:600])
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
