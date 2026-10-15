"""Withhold any row the independent audit cannot reproduce, instead of
blocking every other verified row.

The independent auditor (verification-c6/audit_snapshot.py) stays the hard
gate: after this step it is run again and must report zero failures. A row it
rejects is never published as a pick: its pick, probabilities and fair odds
are removed, its evidence is moved under ``withheld`` for manual review, and
the reason is shown on the Flagged for Review page. Snapshot-level failures
(duplicate IDs, inventory mismatches) cannot be quarantined and still fail.

Usage: python -m scripts.quarantine runtime/latest.json
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/buffedlizard55-lab/MaltaProj4'
AUDITOR = ROOT / 'verification-c6/audit_snapshot.py'


def auditor():
    spec = importlib.util.spec_from_file_location('independent_audit_snapshot', AUDITOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def quarantine(data, audit=None):
    audit = audit or auditor()
    rows, _ = audit.inspect(data)
    # A failing comparison never removes a verified market pick: drop only the comparison.
    for m, problems in rows:
        if problems and all(p.startswith('Model comparison') for p in problems):
            m.pop('model_check', None)
    rows, errors = audit.inspect(data)
    failing = {m['id']: problems for m, problems in rows if problems}
    for m in data['matches']:
        problems = failing.get(m['id'])
        if not problems:
            continue
        m['withheld'] = {'problems': problems,
                         'values': {k: m.get(k) for k in ('method', 'pick', 'probabilities', 'fair_odds')},
                         'evidence': m.get('evidence') or []}
        m.update(probabilities=None, fair_odds=None, pick=None, method=None, evidence=[])
        m.pop('model_check', None)
        m['reason'] = ('Withheld: the independent row audit could not reproduce this row (%s). '
                       'No pick is published for it until a later refresh passes.' % '; '.join(problems))[:600]
        m.setdefault('flags', []).append('Pick withheld after failing the independent row audit; manual review needed.')
        m.setdefault('attempts', []).append({'provider': 'Independent audit', 'status': 'error',
            'reason': '; '.join(problems)[:400], 'url': REPO + '/blob/main/verification-c6/audit_snapshot.py'})
    if failing:
        data.setdefault('issues', []).append({'code': 'audit_quarantine',
            'message': '%d row(s) withheld after failing the independent row audit: %s. Their picks are not published.' % (
                len(failing), ', '.join(sorted(failing))),
            'source': REPO + '/actions'})
    structural = [e for e in errors if e.split(':', 1)[0] not in failing]
    return failing, structural


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('snapshot')
    args = parser.parse_args()
    path = Path(args.snapshot)
    data = json.loads(path.read_text())
    failing, structural = quarantine(data)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    os.replace(tmp, path)
    for row, problems in sorted(failing.items()):
        print('Withheld %s: %s' % (row, '; '.join(problems)))
    print(json.dumps({'withheld_rows': len(failing), 'snapshot_level_failures': structural}))
    if structural:
        raise SystemExit('Snapshot-level audit failures cannot be quarantined: ' + '; '.join(structural))


if __name__ == '__main__':
    main()
