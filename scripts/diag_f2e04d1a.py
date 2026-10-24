"""Summarise a diagnostic run's artefacts into one line-oriented report.

Session f2e04d1a. Read-only: it never builds, never refreshes and never writes a
pick. Its output is emitted as GitHub annotations by
``.github/workflows/diag-f2e04d1a.yml`` because this sandbox cannot read workflow
logs or artifact blobs, and the failure has to be attributable to a named check.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

RUNTIME = Path('runtime')


def read(name: str, limit: int | None = None) -> str:
    path = RUNTIME / name
    try:
        text = path.read_text(errors='replace')
    except OSError:
        return ''
    return text[-limit:] if limit else text


def snapshot_line(path: str, tag: str) -> str:
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        return f'{tag}: unreadable ({exc})'
    rows = data.get('matches') or []
    open_rows = [m for m in rows if m.get('state') == 'open']
    return (
        f"{tag}: generated_at={data.get('generated_at')} rows={len(rows)} "
        f"open={len(open_rows)} picks={sum(bool(m.get('pick')) for m in open_rows)} "
        f"priced={sum(m.get('probabilities') is not None for m in open_rows)} "
        f"unresolved={sum(m.get('probabilities') is None for m in open_rows)}"
    )


def unresolved(path: str) -> list[str]:
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return []
    out = []
    for match in data.get('matches') or []:
        if match.get('state') == 'open' and match.get('probabilities') is None:
            out.append(
                'UNRESOLVED id=%s teams=%s pick=%r method=%r'
                % (match.get('id'), match.get('teams'), match.get('pick'), match.get('method'))
            )
    return out


def main() -> int:
    rc = read('diag.env').replace('\n', ' ').strip()
    print(f'RC: {rc or "none recorded"}')
    print(snapshot_line('runtime/committed-latest.json', 'COMMITTED'))
    print(snapshot_line('runtime/latest.json', 'FRESH'))
    for line in unresolved('runtime/latest.json'):
        print(line)
    staged = read('staged-files.txt').strip().replace('\n', ' ')
    print(f'STAGED: {staged or "none"}')
    publish = read('publish.log', 3000).strip().replace('\n', '|')
    print(f'PUBLISH: {publish or "missing"}')
    validate = read('validate.log', 8000).strip().replace('\n', '|')
    print(f'VALIDATE: {validate or "missing"}')
    fails = [line for line in read('unittest.log').splitlines() if re.match(r'^(FAIL|ERROR):', line)]
    print('UNITTEST_FAILS: ' + ('|'.join(fails[:40]) or 'none'))
    unit_tail = read('unittest.log', 8000).strip().replace('\n', '|')
    print(f'UNITTEST_TAIL: {unit_tail or "missing"}')
    refresh = read('refresh.log', 2500).strip().replace('\n', '|')
    print(f'REFRESH: {refresh or "missing"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
