"""Distil the 408eb0af publication diagnostic into one readable Markdown report.

Run only by `.github/workflows/diag-408eb0af.yml`, which reproduces the exact
sequence the publisher runs on a *live* snapshot. This module reads the captured
`runtime/` directory and writes facts, never conclusions:

  * the return code of every gate, in the order the publisher runs them;
  * the board the fresh snapshot actually produced (rows / open / picks /
    two-way probabilities / unresolved / method mix);
  * for every gate that failed, the failing test names and the last lines of its
    own output, so the report is readable without job logs (this project's
    authoring sandbox cannot read results-receiver logs or artifact blobs).

Nothing here recomputes, repairs or rewrites a pick. If a gate failed, the
report says which row or assertion failed and stops there.
"""
import argparse
import collections
import json
import os
import re
from pathlib import Path

GATES = [
    ('refresh_rc', 'Refresh official sources'),
    ('quarantine_rc', 'Quarantine rows the audit cannot reproduce'),
    ('row_audit_rc', 'Independent row audit of the fresh snapshot'),
    ('build_rc', 'Build'),
    ('validate_rc', 'Validate build (links, checksums, contract)'),
    ('published_row_audit_rc', 'Independent row audit of the built artifact'),
    ('unittest_rc', 'Unit and failure-mode suite'),
    ('audits_rc', 'Archive auditor suite'),
    ('integrity_rc', 'Integrity checks'),
    ('verification_c6_rc', 'verification-c6 suite'),
]

# Which captured file is worth quoting for a failing gate.
LOG_FOR = {
    'refresh_rc': 'refresh.log',
    'quarantine_rc': 'quarantine.log',
    'row_audit_rc': 'row-audit.log',
    'build_rc': 'build.log',
    'validate_rc': 'validate.log',
    'published_row_audit_rc': 'published-row-audit.log',
    'unittest_rc': 'unittest.log',
    'audits_rc': 'audits.log',
    'integrity_rc': 'integrity.log',
    'verification_c6_rc': 'verification-c6.log',
}
# Reports that carry the audited detail even when the gate passed.
REPORT_FOR = {
    'row_audit_rc': 'row-audit.md',
    'published_row_audit_rc': 'published-row-audit.md',
}

FAILURE_LINE = re.compile(r'^(FAIL|ERROR):|^[a-zA-Z_.]+Error:|^AssertionError|^Traceback|^::error|'
                          r'^[A-Za-z_]*Error: |^E +|^\s*assert', re.MULTILINE)
TAIL_LINES = 40
MAX_LINES = 120


def rc_values(runtime):
    values = {}
    path = runtime / 'diag.env'
    if not path.exists():
        return values
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        if '=' in line:
            key, _, value = line.partition('=')
            try:
                values[key.strip()] = int(value.strip())
            except ValueError:
                values[key.strip()] = value.strip()
    return values


def board(snapshot):
    """Facts about the snapshot, counted the same way the site counts them."""
    rows = snapshot.get('matches') or []
    open_rows = [row for row in rows if row.get('state') == 'open']
    priced = [row for row in open_rows if row.get('probabilities')]
    picked = [row for row in open_rows if row.get('pick')]
    unresolved = [row for row in open_rows if not row.get('probabilities')]
    methods = collections.Counter((row.get('method') or 'none') for row in open_rows)
    return {
        'generated_at': snapshot.get('generated_at'),
        'rows': len(rows),
        'open': len(open_rows),
        'picks': len(picked),
        'priced': len(priced),
        'unresolved': len(unresolved),
        'methods': dict(methods),
        'priced_without_pick': [row.get('id') for row in open_rows
                                if row.get('probabilities') and not row.get('pick')],
        'picked_without_price': [row.get('id') for row in open_rows
                                 if row.get('pick') and not row.get('probabilities')],
        'unresolved_rows': [(row.get('id'), ' vs '.join(row.get('teams') or []),
                             row.get('reason'))
                            for row in unresolved],
        'coverage': snapshot.get('coverage'),
        'coverage_counts': snapshot.get('coverage_counts'),
        'issues': snapshot.get('issues'),
    }


def quote_log(runtime, name):
    path = runtime / name
    if not path.exists():
        return ['(no %s was captured)' % name]
    text = path.read_text(encoding='utf-8', errors='replace')
    lines = text.splitlines()
    picked = []
    seen = set()
    for line in lines:
        if FAILURE_LINE.search(line):
            key = line.strip()
            if key and key not in seen:
                seen.add(key)
                picked.append(line.rstrip())
    tail = [line.rstrip() for line in lines[-TAIL_LINES:]]
    out = []
    if picked:
        out.append('Failure lines (first %d):' % min(len(picked), MAX_LINES))
        out.append('```')
        out.extend(picked[:MAX_LINES])
        out.append('```')
    out.append('Last %d lines of `%s`:' % (len(tail), name))
    out.append('```')
    out.extend(tail)
    out.append('```')
    return out


def report(runtime, run_id=None):
    lines = ['# 408eb0af publication diagnostic', '']
    if run_id:
        lines.append('Run: https://github.com/buffedlizard55-lab/MaltaProj4/actions/runs/%s' % run_id)
    lines.append('Reproduced on GitHub runners, which is the only environment this project can read '
                 'Hotspawn, HLTV and bookmaker sources from. Nothing below is a repair: it is the '
                 'measurement the publisher gate is failing on.')
    lines.append('')

    values = rc_values(runtime)
    lines.append('## Gate return codes, in publisher order')
    lines.append('')
    lines.append('| Gate | rc | Result |')
    lines.append('| --- | --- | --- |')
    first_failure = None
    for key, label in GATES:
        value = values.get(key)
        if value is None:
            result = 'not run'
        elif value == 0:
            result = 'pass'
        else:
            result = '**FAIL**'
            if first_failure is None:
                first_failure = key
        lines.append('| %s | %s | %s |' % (label, '' if value is None else value, result))
    lines.append('')
    if first_failure:
        lines.append('First failing gate: **%s** (`%s`).' % (dict(GATES)[first_failure], first_failure))
    else:
        lines.append('Every captured gate returned 0.')
    lines.append('')

    snapshot_path = runtime / 'latest.json'
    if snapshot_path.exists():
        snapshot = json.loads(snapshot_path.read_text(encoding='utf-8'))
        facts = board(snapshot)
        lines.append('## The board this snapshot produced')
        lines.append('')
        lines.append('| Fact | Value |')
        lines.append('| --- | --- |')
        for key in ('generated_at', 'coverage', 'rows', 'open', 'picks', 'priced', 'unresolved'):
            lines.append('| %s | `%s` |' % (key, facts[key]))
        lines.append('| method mix | `%s` |' % json.dumps(facts['methods'], sort_keys=True))
        lines.append('| coverage counts | `%s` |' % json.dumps(facts['coverage_counts'], sort_keys=True))
        lines.append('')
        if facts['priced_without_pick']:
            lines.append('Rows priced with no pick (a contract violation): `%s`'
                         % ', '.join(str(i) for i in facts['priced_without_pick']))
            lines.append('')
        if facts['picked_without_price']:
            lines.append('Rows picked with no probability: `%s`'
                         % ', '.join(str(i) for i in facts['picked_without_price']))
            lines.append('')
        if facts['unresolved_rows']:
            lines.append('Unresolved open rows (no probability, no pick):')
            lines.append('')
            for fixture, teams, reason in facts['unresolved_rows']:
                lines.append('- `%s` %s — %s' % (fixture, teams, reason or '(no reason recorded)'))
            lines.append('')
        for issue in facts['issues'] or []:
            lines.append('- issue `%s`: %s (%s)' % (issue.get('code'), issue.get('message'),
                                                   issue.get('source')))
        lines.append('')
    else:
        lines.append('## The board this snapshot produced')
        lines.append('')
        lines.append('No `latest.json` was captured, so the refresh never wrote a snapshot.')
        lines.append('')

    for key, label in GATES:
        value = values.get(key)
        if value == 0:
            continue
        lines.append('## %s — `%s` returned %s' % (label, key, value))
        lines.append('')
        log = LOG_FOR.get(key)
        if log:
            lines.extend(quote_log(runtime, log))
        report_name = REPORT_FOR.get(key)
        if report_name and (runtime / report_name).exists():
            text = (runtime / report_name).read_text(encoding='utf-8').splitlines()
            lines.append('')
            lines.append('`%s` (first 80 lines):' % report_name)
            lines.append('```')
            lines.extend(text[:80])
            lines.append('```')
        lines.append('')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', default='runtime')
    parser.add_argument('--output', required=True)
    parser.add_argument('--run-id', default=os.environ.get('GITHUB_RUN_ID'))
    args = parser.parse_args(argv)
    text = report(Path(args.runtime), args.run_id)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding='utf-8')
    print(text[:4000])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
