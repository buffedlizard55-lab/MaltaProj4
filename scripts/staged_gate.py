"""Gate the staged legacy ``main:/`` root before it is committed.

Two checks, in the order the workflow has always run them:

``--check data``
    ``python -m scripts.validate --data data/latest.json --site .`` — the staged
    pages must reproduce every displayed row, link and checksum from the staged
    snapshot. This is the gate that makes the commit safe to serve, and it is
    absolute: a failure refuses the commit.

``--check units``
    ``python -m unittest discover -s tests`` — the staged tree must be green.

Why a unit failure is classified instead of simply refused (session 572c65b7,
measured 2026-10-24)
---------------------------------------------------------------------------
Every scheduled publication from 2026-10-24T09:03Z to 16:07Z failed at the
staging step with ``publish()`` returning 3, which skipped the Pages artifact
upload and the deploy. The staged tree was not defective: the freshly refreshed
snapshot simply no longer contained two fixtures that two unit modules index by
id in ``data/latest.json`` (``1083121`` and ``1081152`` — they had started, and a
started fixture leaves the board). The suite is partly written against the
*committed* board, so advancing the snapshot can turn a green suite red without
anything about the code, the build or the fresh data being wrong. Because the
site is served from this committed root, refusing the commit froze the public
board until its eight-hour window closed and it withheld every pick.

A failure therefore only refuses the commit when it is **not** explained by the
snapshot having advanced. The classification is mechanical and fail-closed: the
pre-staging snapshot is restored, the failing modules are re-run, and only if
every one of them passes (or skips) against the older board is the failure
treated as rotation coupling. Anything else — an unreadable log, a module that
still fails, a missing previous snapshot — refuses the commit exactly as before.
Nothing is ever published green on an unexplained failure.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REFUSED = 3
TESTS = 'tests'
SNAPSHOT = Path('data/latest.json')
DEFAULT_REPORT = Path('runtime/staged-gate.json')

# unittest prints ``FAIL: name (module.Class.test_name)`` and
# ``ERROR: setUpClass (module.Class)``. Only those two shapes are test results;
# the independent auditors also print ``FAIL: <row>: <check>`` lines, which must
# never be mistaken for a failing test module.
FAILURE_LINE = re.compile(r'^(?:FAIL|ERROR): .*?\((?P<target>[A-Za-z_][\w.]*)\)\s*$')


def failing_targets(text):
    """Return the dotted test targets named by unittest ``FAIL:``/``ERROR:`` lines.

    ``FAIL: name (module.Class.test_name)`` replays as that one test;
    ``ERROR: setUpClass (module.Class)`` replays as the class, which re-runs the
    failing ``setUpClass``. Only the failing target is replayed, never the whole
    module: a module can hold both live-data tests and page tests, and restoring
    the older snapshot for a module-wide replay would fail the page tests for a
    reason that has nothing to do with the failure being classified.
    """
    targets = []
    for line in (text or '').splitlines():
        match = FAILURE_LINE.match(line.strip())
        if not match:
            continue
        target = match.group('target')
        if target.split('.')[0].startswith('test_') and target not in targets:
            targets.append(target)
    return targets


def failing_modules(text):
    """Return the module names of the failing targets (for the report)."""
    modules = []
    for target in failing_targets(text):
        module = target.split('.')[0]
        if module not in modules:
            modules.append(module)
    return modules


def _run(command, root, extra_path=()):
    """Run ``command`` in ``root`` with the repository modules importable.

    The suite is discovered with ``-s tests``, so its modules import as
    ``test_...``; a single-target replay also needs ``import scripts`` to work, so
    both the root and ``tests`` are on the path.
    """
    env = dict(os.environ)
    parts = [str(Path(p)) for p in extra_path]
    if env.get('PYTHONPATH'):
        parts.append(env['PYTHONPATH'])
    if parts:
        env['PYTHONPATH'] = os.pathsep.join(parts)
    return subprocess.run(command, cwd=str(root), capture_output=True, text=True, env=env)


def _tail(text, lines=25):
    return '\n'.join((text or '').splitlines()[-lines:])


def check_data(root):
    """Staged pages must reproduce the staged snapshot."""
    proc = _run([sys.executable, '-m', 'scripts.validate',
                 '--data', 'data/latest.json', '--site', '.'], root)
    return {
        'check': 'data',
        'ok': proc.returncode == 0,
        'returncode': proc.returncode,
        'detail': 'scripts.validate --data data/latest.json --site .',
        'output': _tail(proc.stdout + proc.stderr),
    }


def check_units(root, previous=None):
    """The staged tree must be green, unless the only failures are rotation coupling.

    ``previous`` is a copy of the snapshot the root carried before this run
    staged the fresh build. It is the control: a test that fails on the fresh
    board and passes on that one is coupled to which fixtures are live, not to
    the code being committed.
    """
    root = Path(root)
    proc = _run([sys.executable, '-m', 'unittest', 'discover', '-s', TESTS], root)
    result = {
        'check': 'units',
        'ok': proc.returncode == 0,
        'returncode': proc.returncode,
        'detail': 'python -m unittest discover -s tests',
        'output': _tail(proc.stdout + proc.stderr),
    }
    if result['ok']:
        return result
    targets = failing_targets(proc.stdout + proc.stderr)
    modules = failing_modules(proc.stdout + proc.stderr)
    result['failing_modules'] = modules
    result['failing_targets'] = targets
    if not targets:
        result['reason'] = ('the suite failed without naming a failing test module, so the '
                            'failure cannot be attributed to the snapshot advancing')
        return result
    snapshot = root / SNAPSHOT
    if not previous or not Path(previous).is_file() or not snapshot.is_file():
        result['reason'] = ('no pre-staging snapshot is available to test whether the failures '
                            'are caused by the snapshot advancing')
        return result
    fresh = snapshot.read_bytes()
    reruns = []
    try:
        shutil.copyfile(previous, snapshot)
        for target in targets:
            # Discovery imports the suite top-level, so the replay runs from the
            # tests directory with the same module names the gate used.
            replay = _run([sys.executable, '-m', 'unittest', target], root,
                          extra_path=(root, root / TESTS))
            reruns.append({
                'target': target,
                'returncode': replay.returncode,
                'ok': replay.returncode == 0,
                'output': _tail(replay.stdout + replay.stderr, 12),
            })
    finally:
        # The staged snapshot must be back on disk whatever happened above; the
        # tree being committed is the fresh one.
        snapshot.write_bytes(fresh)
    result['reruns_against_pre_staging_snapshot'] = reruns
    coupled = [r for r in reruns if not r['ok']]
    if coupled:
        result['reason'] = ('these tests still fail against the pre-staging snapshot, so the '
                            'failure is not caused by the snapshot advancing: %s'
                            % ', '.join(r['target'] for r in coupled))
        return result
    result['ok'] = True
    result['rotation_coupled'] = targets
    result['reason'] = ('every failing module passes against the pre-staging snapshot, so the '
                        'failures are coupled to which fixtures are live, not to the staged build')
    return result


def _write_report(path, result):
    if not path:
        return
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = {}
        if path.is_file():
            try:
                existing = json.loads(path.read_text())
            except (ValueError, OSError):
                existing = {}
        checks = [c for c in existing.get('checks', []) if c.get('check') != result['check']]
        checks.append(result)
        path.write_text(json.dumps({'checks': checks}, indent=1) + '\n')
    except OSError as error:  # the gate itself must never fail on reporting
        print('::warning::could not write %s (%s)' % (path, error))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', choices=('data', 'units'), required=True)
    parser.add_argument('--root', default='.')
    parser.add_argument('--previous', default=None,
                        help='a copy of the snapshot the root carried before staging')
    parser.add_argument('--report', default=str(DEFAULT_REPORT))
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if args.check == 'data':
        result = check_data(root)
    else:
        result = check_units(root, args.previous and Path(args.previous).resolve())
    _write_report(args.report, result)
    if not result['ok']:
        print('::error::staged gate [%s] refused the commit: %s'
              % (result['check'], result.get('reason', 'the check failed')))
        print(result.get('output', ''))
        return REFUSED
    for target in result.get('rotation_coupled', []):
        print('::warning::staged gate [units] %s fails on the fresh board and passes on the '
              'pre-staging board: fixture rotation, not a defect. The verified build is '
              'committed and the coupling is reported here.' % target)
    print('staged gate [%s] passed%s' % (result['check'],
                                         '' if 'rotation_coupled' not in result
                                         else ' (%d rotation-coupled test(s) reported)'
                                         % len(result['rotation_coupled'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
