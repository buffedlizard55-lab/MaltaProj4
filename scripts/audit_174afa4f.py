"""Session 174afa4f: dated coverage audit (9b97d585 core + session deltas).

Runs after a real refresh + quarantine. It never collects odds and never
changes a pick. The line-by-line ledger, independent C6 replay and gap
accounting come from ``scripts.audit_9b97d585`` unchanged; this wrapper adds
the two records this session is responsible for:

* every open row whose research pick rests on HLTV *team-page* ranks (the
  new fail-closed fallback in ``scripts.core._team_page_rank_rows``), with
  the ranks and page links it was derived from;
* the publish-deadlock guard: whether the snapshot's own verified feed
  evidence proves that fixtures present in the previous snapshot but absent
  now were removed by Hotspawn (raw evidence IDs == published IDs under
  ``coverage == 'verified'``), rather than dropped by the collector.

Usage:
    python -m scripts.audit_174afa4f --snapshot runtime/latest.json \
        --previous data/latest.json --output research/harvest-174afa4f

Exit code is nonzero only on integrity failures. An honestly unresolved
open row is a visible coverage gap, not an integrity failure.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import audit_9b97d585
from scripts import summary as summary_module


def team_page_rank_rows(snapshot):
    """Open rows decided by HLTV team-page ranks, with their stored evidence."""
    out = []
    for match in snapshot.get('matches') or []:
        pages = match.get('hltv_team_pages') or {}
        resolved = pages.get('resolved_ranks')
        if not isinstance(resolved, list):
            continue
        out.append({
            'id': str(match.get('id')),
            'teams': match.get('teams'),
            'start': match.get('start'),
            'pick': match.get('pick'),
            'method': match.get('method'),
            'probabilities': match.get('probabilities'),
            'pages_observed_at': pages.get('observed_at'),
            'resolved_ranks': resolved,
            'team_pages': [
                {'team': row.get('team'), 'label': row.get('label'),
                 'world_rank': row.get('world_rank'),
                 'world_rank_status': row.get('world_rank_status'),
                 'url': row.get('url'), 'observed_at': row.get('observed_at')}
                for row in pages.get('teams') or [] if isinstance(row, dict)
            ],
        })
    return out


def deadlock_guard(snapshot, previous):
    """Prove (or refute) that vanished fixtures were removed by the feed."""
    evidence = {str(x.get('id')) for x in snapshot.get('fixture_evidence') or []
                if isinstance(x, dict) and x.get('id') is not None}
    known = {str(m.get('id')) for m in snapshot.get('matches') or []}
    previous_ids = {str(m.get('id')) for m in (previous or {}).get('matches') or []}
    vanished = sorted(previous_ids - known)
    collector_complete = bool(evidence) and evidence == known
    verified = snapshot.get('coverage') == 'verified'
    return {
        'coverage': snapshot.get('coverage'),
        'coverage_counts': snapshot.get('coverage_counts'),
        'raw_evidence_ids': len(evidence),
        'published_ids': len(known),
        'collector_complete_evidence_equals_published': collector_complete,
        'vanished_vs_previous': vanished,
        'vanished_proved_feed_removed': [i for i in vanished if i not in evidence]
            if (verified and collector_complete) else [],
        'vanished_unproved': vanished if not (verified and collector_complete)
            else [i for i in vanished if i in evidence],
        'inventory_changes_reported_by_refresh': snapshot.get('inventory_changes'),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', required=True, type=Path)
    parser.add_argument('--previous', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    snapshot_bytes = args.snapshot.read_bytes()
    snapshot = json.loads(snapshot_bytes)
    previous = (json.loads(args.previous.read_bytes())
                if args.previous and args.previous.exists() else {})

    result = audit_9b97d585.audit(snapshot, previous, snapshot_bytes)
    audit_9b97d585.write_reports(result, args.output, snapshot_bytes)

    counts = summary_module.counts(snapshot.get('matches') or [])
    delta = {
        'schema_version': 1,
        'session': '174afa4f',
        'snapshot_generated_at': snapshot.get('generated_at'),
        'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
        'summary_counts': {key: counts[key] for key in (
            'feed_rows', 'open', 'with_pick', 'priced', 'market', 'model',
            'research', 'no_pick', 'without_percentage', 'percent')},
        'completeness_sentence': summary_module.completeness_sentence(counts),
        'team_page_rank_rows': team_page_rank_rows(snapshot),
        'deadlock_guard': deadlock_guard(snapshot, previous),
        'integrity_failures': result['integrity_failures'],
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'session-174afa4f.json').write_text(
        json.dumps(delta, ensure_ascii=False, indent=1) + '\n')
    guard = delta['deadlock_guard']
    lines = [
        '# Session 174afa4f — audit deltas',
        '',
        f"- Snapshot generated: `{delta['snapshot_generated_at']}`; fixture evidence: `{delta['fixtures_observed_at']}`",
        f"- Completeness: {delta['completeness_sentence']}",
        f"- Summary counts: `{json.dumps(delta['summary_counts'])}`",
        f"- Team-page rank rows: **{len(delta['team_page_rank_rows'])}**",
        f"- Deadlock guard: coverage `{guard['coverage']}`, evidence IDs {guard['raw_evidence_ids']} "
        f"vs published {guard['published_ids']} (equal: {guard['collector_complete_evidence_equals_published']}); "
        f"vanished vs previous `{guard['vanished_vs_previous'] or 'none'}`, "
        f"proved feed-removed `{guard['vanished_proved_feed_removed'] or 'none'}`, "
        f"unproved `{guard['vanished_unproved'] or 'none'}`",
        '',
        '## HLTV team-page rank rows',
        '',
    ]
    if not delta['team_page_rank_rows']:
        lines.append('None in this snapshot (the tier fires only when HLTV lists no '
                     'fixture page and both exact team pages carry usable rank evidence).')
    for row in delta['team_page_rank_rows']:
        ranks = ', '.join(
            f"{item.get('team')} #{item.get('hltv_rank')}" if item.get('hltv_rank')
            else f"{item.get('team')} ({item.get('status')})"
            for item in row['resolved_ranks'])
        pages = '; '.join(f"[{item['team']}]({item['url']})" for item in row['team_pages'])
        lines.append(f"- `{row['id']}` {' vs '.join(row['teams'] or [])} → pick **{row['pick']}** "
                     f"(`{row['method']}`, no %): {ranks}; pages observed `{row['pages_observed_at']}`: {pages}")
    (args.output / 'session-174afa4f.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'counts': result['counts'],
                      'coverage_complete': result['coverage_complete'],
                      'team_page_rank_rows': len(delta['team_page_rank_rows']),
                      'integrity_failures': len(result['integrity_failures'])}, indent=1))
    return bool(result['integrity_failures'])


if __name__ == '__main__':
    raise SystemExit(main())
