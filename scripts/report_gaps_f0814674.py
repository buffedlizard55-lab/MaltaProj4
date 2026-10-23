"""Read-only coverage report for the current board (session f0814674).

Answers one question per open fixture: does it publish a pick, and does it
publish a reproducible win probability? Writes machine-readable JSON plus a
human-readable Markdown table. It never edits the board, the receipts or the
published pages; the caller (a GitHub-hosted harvest workflow) commits the
report next to the snapshot it describes so the numbers stay dated.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def winner_share(fixture):
    """The pick's published share. Rows store ``probabilities`` in fixture order."""
    probs = fixture.get('probabilities')
    if isinstance(probs, dict):
        values = list(probs.values())
    elif isinstance(probs, (list, tuple)):
        values = list(probs)
    else:
        return None
    if len(values) != 2:
        return None
    try:
        numbers = [float(v) for v in values]
    except (TypeError, ValueError):
        return None
    teams = fixture.get('teams') or []
    pick = fixture.get('pick')
    if pick in teams and len(teams) == 2:
        return numbers[teams.index(pick)]
    return max(numbers)


def summarise(snapshot):
    matches = snapshot.get('matches') or []
    open_rows = [m for m in matches if m.get('state') == 'open']
    unpicked = [m for m in open_rows if not m.get('pick')]
    unpriced = [m for m in open_rows if not m.get('probabilities')]
    methods = Counter(m.get('method') or 'none' for m in open_rows)
    return {
        'snapshot_generated_at': snapshot.get('generated_at'),
        'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
        'coverage_counts': snapshot.get('coverage_counts'),
        'total_rows': len(matches),
        'open_rows': len(open_rows),
        'open_with_pick': len(open_rows) - len(unpicked),
        'open_with_probability': len(open_rows) - len(unpriced),
        'open_without_pick': [str(m.get('id')) for m in unpicked],
        'open_without_probability': [str(m.get('id')) for m in unpriced],
        'methods': dict(sorted(methods.items())),
        'rows': [{
            'id': str(m.get('id')),
            'teams': m.get('teams'),
            'competition': m.get('competition'),
            'start': m.get('start'),
            'pick': m.get('pick'),
            'method': m.get('method'),
            'probabilities': m.get('probabilities'),
            'reason': m.get('reason'),
            'winner_share': winner_share(m),
            'winner_share_pct': (round(winner_share(m) * 100, 1)
                                 if winner_share(m) is not None else None),
            'expires_at': m.get('expires_at'),
            'evidence_urls': [e.get('url') for e in (m.get('evidence') or []) if e.get('url')],
        } for m in open_rows],
    }


def markdown(report):
    lines = ['# Open-board coverage report (session f0814674)', '',
             f"Snapshot `{report['snapshot_generated_at']}` · fixture evidence "
             f"`{report['fixtures_observed_at']}`.", '',
             f"**{report['open_rows']} open · {report['open_with_pick']} with a pick · "
             f"{report['open_with_probability']} with a win probability · "
             f"{len(report['open_without_probability'])} without a probability · "
             f"{len(report['open_without_pick'])} without a pick.**", '',
             '| Fixture | Match | Start (UTC) | Pick | Method | Win % | Source |',
             '| --- | --- | --- | --- | --- | --- | --- |']
    for row in report['rows']:
        teams = ' vs '.join(row['teams'] or [])
        share = (f"{row['winner_share'] * 100:.1f}%" if row['winner_share'] is not None else '—')
        source = row['evidence_urls'][0] if row['evidence_urls'] else '—'
        lines.append(f"| `{row['id']}` | {teams} | {row['start']} | {row['pick'] or '—'} | "
                     f"`{row['method'] or 'none'}` | {share} | {source} |")
    lines += ['', '## Method mix', '', '| Method | Rows |', '| --- | --- |']
    for method, count in report['methods'].items():
        lines.append(f'| `{method}` | {count} |')
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', default='data/latest.json')
    parser.add_argument('--output', default='research/harvest-f0814674')
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    snapshot = json.loads(Path(args.snapshot).read_text())
    report = summarise(snapshot)
    (out / 'coverage-report.json').write_text(json.dumps(report, indent=1, ensure_ascii=False))
    (out / 'COVERAGE.md').write_text(markdown(report))
    print(json.dumps({k: report[k] for k in ('open_rows', 'open_with_pick', 'open_with_probability',
                                             'open_without_pick', 'open_without_probability')}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
