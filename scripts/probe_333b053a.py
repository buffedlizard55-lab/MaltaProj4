"""Summarise a live refresh snapshot for session 333b053a's line-by-line audit."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def summarise(snapshot_path: Path) -> dict:
    raw_bytes = snapshot_path.read_bytes()
    data = json.loads(raw_bytes)
    matches = data.get('matches', [])
    open_rows = [m for m in matches if m.get('state') == 'open']
    methods = Counter(str(m.get('method')) for m in open_rows)

    rows_out = []
    for m in open_rows:
        ev = (m.get('evidence') or [{}])[0] if m.get('evidence') else None
        rows_out.append({
            'id': m['id'],
            'teams': m['teams'],
            'team_ids': m.get('team_ids'),
            'competition': m.get('competition'),
            'start': m.get('start'),
            'lock': m.get('lock'),
            'tier': m.get('tier'),
            'best_of': m.get('best_of'),
            'source_url': m.get('source_url'),
            'method': m.get('method'),
            'pick': m.get('pick'),
            'probabilities': m.get('probabilities'),
            'fair_odds': m.get('fair_odds'),
            'expires_at': m.get('expires_at'),
            'flags': m.get('flags', []),
            'reason': m.get('reason'),
            'evidence_summary': ({
                'provider': ev.get('provider'),
                'id': ev.get('id'),
                'url': ev.get('url'),
                'api_url': ev.get('api_url'),
                'observed_at': ev.get('observed_at'),
                'updated_at': ev.get('updated_at'),
                'spread': ev.get('spread'),
                'liquidity': ev.get('liquidity'),
                'overround': ev.get('overround'),
                'decimal_odds': ev.get('decimal_odds'),
                'points': ev.get('points'),
                'standings': ev.get('standings'),
                'vrs_teams': ev.get('vrs_teams'),
                'roster_checks': ev.get('roster_checks'),
                'standings_as_of': ev.get('standings_as_of') or ev.get('ranking_as_of'),
            } if ev else None),
            'model_check': m.get('model_check'),
            'hltv_context': m.get('hltv_context'),
            'hltv_team_pages': m.get('hltv_team_pages'),
            'vrs_research': m.get('vrs_research'),
            'attempts': m.get('attempts', []),
        })

    return {
        'session': '333b053a',
        'snapshot_sha256': hashlib.sha256(raw_bytes).hexdigest(),
        'generated_at': data.get('generated_at'),
        'fixtures_observed_at': data.get('fixtures_observed_at'),
        'coverage': data.get('coverage'),
        'coverage_counts': data.get('coverage_counts'),
        'rows_total': len(matches),
        'rows_not_open': sum(m.get('state') != 'open' for m in matches),
        'rows_open': len(open_rows),
        'rows_open_with_pick': sum(bool(m.get('pick')) for m in open_rows),
        'rows_open_with_prices': sum(m.get('probabilities') is not None for m in open_rows),
        'rows_open_research_only': sum(
            m.get('probabilities') is None and bool(m.get('pick')) for m in open_rows
        ),
        'rows_open_unresolved': [m['id'] for m in open_rows if not m.get('pick')],
        'open_methods': dict(sorted(methods.items())),
        'issues': data.get('issues', []),
        'source_checks_count': len(data.get('source_checks', [])),
        'source_checks_errors': [
            c for c in data.get('source_checks', []) if c.get('status') != 'ok'
        ],
        'open_rows': rows_out,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output', default='research/session-333b053a/refresh-probe.json')
    args = parser.parse_args()
    snap = Path(args.snapshot)
    if not snap.exists():
        raise SystemExit(f'Missing snapshot: {snap}')
    summary = summarise(snap)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'open_rows'}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
