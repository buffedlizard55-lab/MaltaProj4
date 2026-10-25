"""Replay the publication pipeline and record the exact return code of every step.

Why this exists (measured, 2026-10-25): ``pages.yml`` has been red at the step
*Build and independently verify every row, calculation and internal link* on the
scheduled runs at 06:56Z (40170923727) and 12:29Z (40193317196), while the same
step passed at 01:43Z (40151731896). The last successful publication therefore
stamped ``build-info.json`` at 2026-10-25T01:47:42Z and the committed legacy
``main:/`` root has served that snapshot ever since. Once a snapshot leaves the
eight-hour evidence window the site withholds every pick, so this single failing
step is what a phone visitor experiences as "no picks".

The authoring sandbox can reach GitHub and package registries only, so the real
refresh has to run on a runner, and this project's runner job logs are not
readable from that sandbox (they redirect to blob storage, which is outside the
allowlist). This script is the read-back channel: it runs the same commands the
publisher runs, captures the complete stdout/stderr of each one plus its return
code, copies the refreshed snapshot, and the workflow commits the bundle to the
session branch so it can be read and reproduced line by line.

It derives nothing. Every command is the unmodified command from ``pages.yml``;
the only additions are the return-code capture and the copy of the snapshot.
"""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PY = sys.executable

STEPS = [
    ('01-committed-validate',
     [PY, '-m', 'scripts.validate', '--data', 'data/latest.json', '--site', '.'],
     'Validate the committed board exactly as the publisher does before refreshing.'),
    ('02-committed-unit',
     [PY, '-m', 'unittest', 'discover', '-s', 'tests'],
     'The unit suite the publisher runs before it refreshes.'),
    ('03-refresh',
     [PY, '-m', 'scripts.refresh', '--output', 'runtime/latest.json'],
     'Refresh every official source (Hotspawn feed and lobby, Polymarket, books, HLTV, Valve VRS).'),
    ('04-quarantine',
     [PY, '-m', 'scripts.quarantine', 'runtime/latest.json'],
     'Withhold any row the independent audit cannot reproduce.'),
    ('05-row-audit',
     [PY, 'verification-c6/audit_snapshot.py', 'runtime/latest.json', '--output', 'runtime/independent-row-audit.md'],
     'Independent row audit of the refreshed snapshot.'),
    ('06-build',
     [PY, '-m', 'scripts.build', '--data', 'runtime/latest.json'],
     'Build the static site from the refreshed snapshot.'),
    ('07-validate-fresh',
     [PY, '-m', 'scripts.validate', '--data', 'runtime/latest.json'],
     'Validate the freshly built site (this is the step that fails on main).'),
    ('08-published-audit',
     [PY, 'verification-c6/audit_snapshot.py', 'public/data/latest.json', '--output', 'runtime/published-row-audit.md'],
     'Independent row audit of the built artifact.'),
    ('09-fresh-unit',
     [PY, '-m', 'unittest', 'discover', '-s', 'tests'],
     'The unit suite against the freshly refreshed board.'),
]

TAIL = 4000


def run(command, log_dir, name):
    started = datetime.datetime.now(datetime.timezone.utc)
    proc = subprocess.run(command, capture_output=True, text=True, env=dict(os.environ))
    finished = datetime.datetime.now(datetime.timezone.utc)
    body = (
        'command: %s\n'
        'started: %s\n'
        'finished: %s\n'
        'return code: %d\n'
        '----- stdout -----\n%s\n'
        '----- stderr -----\n%s\n'
        % (' '.join(command), started.isoformat(), finished.isoformat(), proc.returncode,
           proc.stdout, proc.stderr)
    )
    (log_dir / (name + '.log')).write_text(body)
    return {
        'step': name,
        'command': ' '.join(command),
        'return_code': proc.returncode,
        'stdout_tail': proc.stdout[-TAIL:],
        'stderr_tail': proc.stderr[-TAIL:],
        'log': name + '.log',
    }


def describe(path):
    if not path.exists() or not path.stat().st_size:
        return {'error': 'no snapshot'}
    data = json.loads(path.read_text())
    rows = data.get('matches') or []
    open_rows = [row for row in rows if row.get('state') == 'open']
    priced = [row for row in open_rows if row.get('probabilities') is not None]
    picked = [row for row in open_rows if row.get('pick')]
    return {
        'generated_at': data.get('generated_at'),
        'rows_total': len(rows),
        'rows_open': len(open_rows),
        'open_with_probability': len(priced),
        'open_with_pick': len(picked),
        'open_without_pick': len(open_rows) - len(picked),
        'methods': {m: sum(1 for row in open_rows if row.get('method') == m)
                    for m in sorted({str(row.get('method')) for row in open_rows})},
        'coverage': data.get('coverage'),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='research/session-b85ad9b4')
    args = parser.parse_args()
    out = Path(args.out)
    log_dir = out / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    Path('runtime').mkdir(parents=True, exist_ok=True)

    results = []
    for name, command, why in STEPS:
        print('== %s ==' % name, flush=True)
        result = run(command, log_dir, name)
        result['why'] = why
        results.append(result)
        print('rc=%d' % result['return_code'], flush=True)
        # The publisher's own gate: once the built site fails validation or the
        # published audit, the remaining steps are meaningless. Keep going anyway
        # so a single bundle shows every failure, but record the first red step.
    first_red = next((item for item in results if item['return_code'] != 0), None)

    snapshot = Path('runtime/latest.json')
    if snapshot.exists() and snapshot.stat().st_size:
        shutil.copyfile(snapshot, out / 'snapshot.json')

    summary = {
        'session': 'b85ad9b4',
        'captured_at': datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z'),
        'head_sha': os.environ.get('GITHUB_SHA'),
        'run_id': os.environ.get('GITHUB_RUN_ID'),
        'run_url': ('https://github.com/%s/actions/runs/%s'
                    % (os.environ.get('GITHUB_REPOSITORY'), os.environ.get('GITHUB_RUN_ID'))),
        'first_red_step': None if first_red is None else first_red['step'],
        'first_red_return_code': None if first_red is None else first_red['return_code'],
        'committed_snapshot': describe(Path('data/latest.json')),
        'fresh_snapshot': describe(snapshot),
        'steps': results,
    }
    (out / 'diag.json').write_text(json.dumps(summary, indent=2) + '\n')

    lines = [
        '# Publication replay — session b85ad9b4',
        '',
        'Run: %s' % summary['run_url'],
        'Captured: %s' % summary['captured_at'],
        '',
        'First red step: **%s** (rc=%s)' % (summary['first_red_step'], summary['first_red_return_code']),
        '',
        '| # | Step | Return code |',
        '| --- | --- | --- |',
    ]
    for item in results:
        lines.append('| %s | %s | %s |' % (item['step'][:2], item['why'], item['return_code']))
    lines += ['', '## Snapshot counts', '', '```json',
              json.dumps({'committed': summary['committed_snapshot'],
                          'fresh': summary['fresh_snapshot']}, indent=2), '```']
    for item in results:
        if item['return_code'] != 0:
            lines += ['', '## Failure output: %s' % item['step'], '', '```',
                      'command: ' + item['command'],
                      'return code: %d' % item['return_code'],
                      '--- stdout (tail) ---', item['stdout_tail'],
                      '--- stderr (tail) ---', item['stderr_tail'], '```']
    (out / 'REPORT.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines)[:12000], flush=True)


if __name__ == '__main__':
    main()
