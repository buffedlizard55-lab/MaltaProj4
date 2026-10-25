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
    problems.extend(roster_lineage_violations(match))
    return problems


MODEL_PROVIDERS = ('Valve VRS model', 'HLTV Valve ranking (Valve points)')


def roster_lineage_violations(match):
    """A model row must be able to prove its roster from an HLTV page on the row.

    Session 408eb0af. ``scripts.validate`` already asserts this for every
    originated line, and on 2026-10-25T13:30Z that assertion was the single
    reason the scheduled publisher had failed at step 13 since
    2026-10-24T23:40Z: fixture 1086697 (Hotspawn "Projeto do KinGui" vs
    "Yawara") was priced from Valve's "ex-Keyd Stars" row, and the HLTV lineup
    on the row is labelled "Tropa do KinGui". Both labels are one team in the
    verified identity register, so the assertion itself was too strict and is
    fixed at its source (``scripts.validate.lineup_source_ok`` now accepts a
    registered alias). This is the backstop: if a future row still cannot prove
    its roster, one row is withheld and visibly flagged instead of the whole
    board refusing to publish. It re-uses the validator's own function so the
    two can never disagree, and it checks nothing when the row carries no HLTV
    roster evidence at all, which is the validator's ``label_count`` case.
    """
    if match.get('state') != 'open' or not match.get('probabilities'):
        return []
    evidence = match.get('evidence') or []
    quote = evidence[0] if evidence and isinstance(evidence[0], dict) else {}
    if quote.get('provider') not in MODEL_PROVIDERS:
        return []
    if not (match.get('hltv_team_pages') or (match.get('hltv_context') or {}).get('lineups')):
        return []
    try:
        from scripts.validate import lineup_source_ok
    except Exception:  # a broken import must never invent a violation
        return []
    problems = []
    for team, check in zip(match.get('teams') or [], quote.get('roster_checks') or []):
        if not isinstance(check, dict) or check.get('overlap') is None:
            continue
        if not lineup_source_ok(match, team, check.get('lineup') or []):
            problems.append('Model roster for %s has no HLTV source on this row' % team)
    return problems


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
