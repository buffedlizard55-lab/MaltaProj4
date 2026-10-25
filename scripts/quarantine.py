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
import copy
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


def contract_violations(match):
    """Publication contracts a row must satisfy before it is shown as a pick.

    These are checked here, in the publication path, rather than in the
    independent auditor: the auditor also replays *archived* snapshots, and a
    historical row that legitimately published an even pair under an older rule
    must stay auditable rather than turn its archive red.

    Session f2e04d1a measured why this matters. A tight Polymarket mid of
    exactly 0.50/0.50 for fixture 1079200 produced a priced row with no pick.
    The independent audit accepted it (it reproduced "no directional edge"),
    `scripts.validate` accepted the rendered page, and only the unit suite
    refused it - so every scheduled publish from 09:03Z to 16:00Z failed at the
    root-fallback gate and the live page withheld every pick. The source rule is
    fixed in scripts.core/vrs/vrs_mirror; this is the backstop that turns any
    recurrence into one visibly blank row instead of a frozen board.
    """
    if match.get('state') != 'open':
        return []
    probabilities, pick = match.get('probabilities'), match.get('pick')
    if probabilities is None:
        return []
    problems = []
    if len(probabilities) != 2 or abs(sum(probabilities) - 1) > 1e-6:
        problems.append('Published probability pair is not two numbers summing to 1')
    if abs(probabilities[0] - probabilities[1]) < .0001:
        problems.append('Exactly even published pair supports no directional pick')
    if pick not in (match.get('teams') or []):
        problems.append('Priced row has no directional pick among its two teams')
    elif abs(probabilities[0] - probabilities[1]) >= .0001:
        expected = match['teams'][0 if probabilities[0] > probabilities[1] else 1]
        if pick != expected:
            problems.append('Pick does not follow the larger published probability')
    return problems


def _withhold(match, problems, source):
    """Blank a row's recommendation and keep its values for manual review."""
    match['withheld'] = {'problems': problems,
                         'source': source,
                         'values': {k: match.get(k) for k in ('method', 'pick', 'probabilities', 'fair_odds')},
                         'evidence': match.get('evidence') or []}
    match.update(probabilities=None, fair_odds=None, pick=None, method=None, evidence=[])
    match.pop('model_check', None)
    match['reason'] = ('Withheld: %s could not reproduce this row (%s). '
                       'No pick is published for it until a later refresh passes.' % (source, '; '.join(problems)))[:600]
    match.setdefault('flags', []).append('Pick withheld after failing the independent row audit; manual review needed.')
    match.setdefault('attempts', []).append({'provider': 'Independent audit', 'status': 'error',
        'reason': '; '.join(problems)[:400], 'url': REPO + '/blob/main/verification-c6/audit_snapshot.py'})


def _subset_for(data, match):
    """The minimum snapshot the repository validator needs for one row."""
    ids = {str(match.get('id'))}
    return {'schema_version': data.get('schema_version', 2),
            'generated_at': data.get('generated_at'),
            'fixtures_observed_at': data.get('fixtures_observed_at'),
            'issues': data.get('issues') or [],
            'fixture_conflicts': data.get('fixture_conflicts') or [],
            'matches': [match],
            'fixture_evidence': [row for row in (data.get('fixture_evidence') or [])
                                 if str(row.get('id')) in ids]}


def validation_violations(data):
    """Rows the repository's own data validator cannot reproduce.

    ``scripts.validate.validate_data`` is the gate that decides whether the
    built site may be published, and until now a single row it rejected failed
    that gate for the whole snapshot: the artifact was never uploaded, the
    legacy root was never staged, and the public board withheld *every* pick
    until a later refresh happened to produce a cleaner snapshot. That is how
    2026-10-25T06:41Z and 12:29Z froze the board (fixture 1086697, an
    alias-mapped roster; see ``scripts.validate.same_club`` for the root fix).

    This backstop keeps the gate's standard and removes its blast radius: it
    withholds only the row(s) whose own recommendation cannot be verified, and
    only after proving that withholding exactly those rows makes the whole
    snapshot pass. If that proof fails -- i.e. the problem is snapshot-level, or
    it is not confined to these rows -- nothing is withheld and the caller still
    fails loudly, so a broken site is never published.
    """
    try:
        from scripts.validate import validate_data
    except Exception:  # the validator is part of this repository; never guess
        return {}
    try:
        validate_data(data)
        return {}
    except AssertionError as error:
        message = str(error) or 'repository data validator assertion'
    except Exception:
        # Not a contract assertion (I/O, schema, unexpected type): do not turn
        # it into a blank pick, leave the run to fail with its own traceback.
        return {}
    suspects = {}
    for match in data.get('matches') or []:
        if match.get('state') != 'open':
            continue
        if match.get('pick') is None and match.get('probabilities') is None:
            continue
        try:
            validate_data(_subset_for(data, match))
        except AssertionError as inner:
            suspects[match['id']] = ['Fails the repository data validator: ' + (str(inner) or message)]
        except Exception:
            continue
    if not suspects:
        return {}
    trial = copy.deepcopy(data)
    for match in trial.get('matches') or []:
        if match.get('id') in suspects:
            _withhold(match, suspects[match['id']], 'the repository data validator')
    try:
        validate_data(trial)
    except Exception:
        # Withholding these rows does not repair the snapshot, so the snapshot
        # itself is the problem. Blanking picks would hide that; do not.
        return {}
    return suspects


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
        extra = contract_violations(m)
        if extra:
            failing.setdefault(m['id'], []).extend(extra)
    for m in data['matches']:
        problems = failing.get(m['id'])
        if not problems:
            continue
        _withhold(m, problems, 'the independent row audit')
    if failing:
        data.setdefault('issues', []).append({'code': 'audit_quarantine',
            'message': '%d row(s) withheld after failing the independent row audit: %s. Their picks are not published.' % (
                len(failing), ', '.join(sorted(failing))),
            'source': REPO + '/actions'})
    # Backstop for the *other* gate that publication runs: the repository data
    # validator. Same standard, one row's blast radius instead of the board's.
    rejected = validation_violations(data)
    for m in data['matches']:
        problems = rejected.get(m['id'])
        if problems:
            failing.setdefault(m['id'], []).extend(problems)
            _withhold(m, problems, 'the repository data validator')
    if rejected:
        data.setdefault('issues', []).append({'code': 'validation_quarantine',
            'message': '%d row(s) withheld because the repository data validator could not reproduce them: %s. '
                       'Every other row still publishes; these stay blank and named in the unresolved section.' % (
                len(rejected), ', '.join(sorted(rejected))),
            'source': REPO + '/blob/main/scripts/validate.py'})
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
    # Fail here, with the assertion named, rather than later in the build step.
    try:
        from scripts.validate import validate_data
        validate_data(data)
    except AssertionError as error:
        raise SystemExit('The snapshot still fails the repository data validator after quarantine: %s' % error)
    except ImportError:
        pass


if __name__ == '__main__':
    main()
