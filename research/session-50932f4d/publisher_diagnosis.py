"""Retain an exact failed publisher artifact/log without refreshing or publishing."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile


def main():
    target = json.loads(Path('research/session-50932f4d/release-target.json').read_text())
    run = str(target.get('failed_publisher_run') or '')
    if not run:
        print('No failed publisher requested; no artifact or source fetch.')
        return
    if not re.fullmatch(r'\d+', run):
        raise ValueError('A real recorded publisher run ID is required')
    out = Path('research/session-50932f4d/live') / os.environ['GITHUB_RUN_ID']
    out.mkdir(parents=True, exist_ok=True)
    download = Path('runtime') / ('failed-publisher-' + run)
    subprocess.run(['gh', 'run', 'download', run, '--name', 'github-pages',
                    '--repo', os.environ['GITHUB_REPOSITORY'], '--dir', str(download)], check=True)
    archives = list(download.rglob('artifact.tar'))
    if len(archives) != 1:
        raise ValueError('Expected exactly one Pages artifact archive')
    raw = archives[0].read_bytes()
    if len(raw) > 30_000_000:
        raise ValueError('Publisher archive exceeds the diagnostic size limit')
    compressed = gzip.compress(raw, mtime=0)
    (out / 'publisher-public.tar.gz').write_bytes(compressed)
    wanted = {'data/latest.json': 'publisher-snapshot.json',
              'build-info.json': 'publisher-build-info.json'}
    found = set()
    with tarfile.open(archives[0]) as archive:
        for member in archive:
            name = member.name.removeprefix('./')
            if name in wanted and member.isfile():
                body = archive.extractfile(member).read(4_000_001)
                if len(body) > 4_000_000:
                    raise ValueError('Publisher evidence exceeds the diagnostic size limit')
                (out / wanted[name]).write_bytes(body)
                found.add(name)
    if found != set(wanted):
        raise ValueError('The exact artifact lacks a snapshot or manifest')
    log = subprocess.run(['gh', 'run', 'view', run, '--repo', os.environ['GITHUB_REPOSITORY'],
                          '--log-failed'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out / 'publisher-failure.log').write_bytes(log.stdout[-2_000_000:])
    receipt = {'publisher_run': int(run), 'publisher_url':
               f'https://github.com/{os.environ["GITHUB_REPOSITORY"]}/actions/runs/{run}',
               'artifact_tar_sha256': hashlib.sha256(raw).hexdigest(),
               'saved_archive_bytes': len(compressed), 'log_exit_code': log.returncode,
               'log_original_bytes': len(log.stdout), 'log_truncated': len(log.stdout) > 2_000_000,
               'scope': 'Exact failed-run artifact and log; no collection, stage, production edit or deployment.'}
    (out / 'publisher-diagnosis.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    if log.returncode:
        raise SystemExit(log.returncode)


if __name__ == '__main__':
    main()
