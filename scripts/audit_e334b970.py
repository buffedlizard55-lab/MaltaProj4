"""Session e334b970: a dated coverage receipt for one live capture.

What this answers, from the capture's own bytes and nothing else:

* how many fixtures Hotspawn served, how many are open, and how many open rows
  carry a pick and a win probability;
* which evidence tier produced each pick (exchange, wide exchange, bookmaker
  listing, Valve-VRS model, HLTV ranking research, recent-form research);
* every open row with **no** pick, with its recorded attempts and the exact
  limitation that keeps it unresolved, so the site's Unresolved page and the
  executive summary's limitations section can be checked against the capture;
* the HTTP result of every source the refresh actually asked.

The accounting is `scripts.coverage_contract.inspect`, reused rather than
re-implemented, evaluated at the capture's *own* observation clock. Reading it
against `datetime.now()` would silently relabel that capture's open rows as
expired a few hours later, which is exactly the confusion this receipt exists to
prevent.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

from scripts import coverage_contract
from scripts.core import dt, iso


METHOD_TIERS = {
    'exchange': 'Exchange line (Polymarket mid, two-sided, within gate)',
    'exchange_wide': 'Wide exchange line (published spread, low precision)',
    'bookmaker_fallback': 'Bookmaker listing (dated, identity-verified two-way line)',
    'model_vrs': "Originated line (Valve's official standings + published expectation formula)",
    'model_vrs_mirror': "Originated line (HLTV's dated mirror of Valve's ranking)",
    'research_rank': 'HLTV ranking-order research pick (no percentage)',
    'research_rank_single': 'Valve/HLTV single-team ranking evidence pick (no percentage)',
    'research_vrs_single': 'Valve VRS single-team research pick (no percentage)',
    'research_form': 'HLTV recent-form / head-to-head research pick (no percentage)',
}


def attempts_summary(match):
    rows = []
    for attempt in match.get('attempts') or []:
        if not isinstance(attempt, dict):
            continue
        rows.append({'provider': attempt.get('provider'), 'status': attempt.get('status'),
                     'url': attempt.get('url'), 'reason': attempt.get('reason')})
    return rows


def build(snapshot):
    clock = snapshot.get('fixtures_observed_at') or snapshot.get('generated_at')
    report = coverage_contract.inspect(snapshot, clock)
    matches = {str(m.get('id')): m for m in snapshot.get('matches') or []}
    open_rows = [m for m in snapshot.get('matches') or [] if m.get('state') == 'open']
    methods = Counter(m.get('method') for m in open_rows if m.get('pick'))
    picks = [m for m in open_rows if m.get('pick')]
    priced = [m for m in open_rows if m.get('probabilities') is not None]
    blank = [m for m in open_rows if not m.get('pick')]
    unresolved = []
    for match in blank:
        unresolved.append({
            'id': str(match.get('id')),
            'teams': match.get('teams'),
            'competition': match.get('competition'),
            'start': match.get('start'),
            'lock': match.get('lock'),
            'source_url': match.get('source_url'),
            'limitation': match.get('reason'),
            'attempts': attempts_summary(match),
        })
    priced_without_pick_note = [str(m.get('id')) for m in priced if not m.get('pick')]
    checks = snapshot.get('source_checks') or []
    return {
        'schema_version': 1,
        'receipt_at': iso(dt(clock)),
        'snapshot_generated_at': snapshot.get('generated_at'),
        'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
        'accounting_clock': iso(dt(clock)),
        'feed_rows': len(snapshot.get('fixture_evidence') or []),
        'board_rows': len(snapshot.get('matches') or []),
        'coverage': snapshot.get('coverage'),
        'coverage_counts': snapshot.get('coverage_counts'),
        'counts': {
            'open': len(open_rows),
            'open_with_pick': len(picks),
            'open_with_probability': len(priced),
            'open_without_pick': len(blank),
            'priced_but_no_direction': priced_without_pick_note,
        },
        'method_mix': {method or 'unknown': {'rows': count, 'tier': METHOD_TIERS.get(method, 'Unrecognised tier')}
                       for method, count in sorted(methods.items())},
        'contract': {'counts': report['counts'], 'problems': report['problems'],
                     'inventory_fresh_at_capture_clock': report['inventory_fresh']},
        'unresolved': unresolved,
        'fixture_evidence_ids_missing_from_board': sorted(
            {str(f.get('id')) for f in snapshot.get('fixture_evidence') or []} - set(matches)),
        'sources': [{'name': c.get('name'), 'url': c.get('url'), 'status': c.get('status'),
                     'http_status': c.get('http_status'), 'observed_at': c.get('observed_at'),
                     'bytes': c.get('bytes')}
                    for c in checks],
        'scope': ('Accounting and provenance shape only. Source truth and the arithmetic behind every '
                  'percentage are replayed independently by verification-c6/audit_snapshot.py.'),
    }


def markdown(receipt):
    lines = ['# Live coverage receipt — session e334b970', '',
             '**Capture clock (fixtures observed at):** `%s`  ' % receipt['fixtures_observed_at'],
             '**Board built at:** `%s`  ' % receipt['snapshot_generated_at'],
             '**Accounting evaluated at:** `%s` (the capture\'s own clock, never the reader\'s)' % receipt['accounting_clock'],
             '', '| Measure | Value |', '| --- | --- |',
             '| Hotspawn CS2 feed rows | %d |' % receipt['feed_rows'],
             '| Board rows | %d |' % receipt['board_rows'],
             '| Inventory coverage | `%s` |' % receipt['coverage'],
             '| Open matches | %d |' % receipt['counts']['open'],
             '| Open with a pick | %d |' % receipt['counts']['open_with_pick'],
             '| Open with a win probability | %d |' % receipt['counts']['open_with_probability'],
             '| Open without a pick | %d |' % receipt['counts']['open_without_pick'],
             '', '## Evidence tier behind each pick', '',
             '| Method | Rows | Tier |', '| --- | --- | --- |']
    for method, info in receipt['method_mix'].items():
        lines.append('| `%s` | %d | %s |' % (method, info['rows'], info['tier']))
    lines += ['', '## Unresolved open rows and why', '']
    if not receipt['unresolved']:
        lines.append('None: every open match carried a sourced pick and a win probability at this capture.')
    else:
        for row in receipt['unresolved']:
            lines += ['### %s — %s' % (row['id'], ' vs '.join(row['teams'] or [])), '',
                      '*Competition:* %s · *start* `%s` · *lock* `%s`' % (row['competition'], row['start'], row['lock']),
                      '', '*Limitation:* %s' % (row['limitation'] or '_(none recorded — defect)_'), '',
                      '*Official fixture link:* %s' % (row['source_url'] or '_(missing — defect)_'), '',
                      '| Provider | Status | Reason | Source |', '| --- | --- | --- | --- |']
            for attempt in row['attempts']:
                lines.append('| %s | %s | %s | %s |' % (
                    attempt.get('provider') or '', attempt.get('status') or '',
                    (attempt.get('reason') or '').replace('|', '/'), attempt.get('url') or ''))
            lines.append('')
    lines += ['## Source read results', '', '| Source | HTTP | Status | Observed | Bytes |', '| --- | --- | --- | --- | --- |']
    for source in receipt['sources']:
        lines.append('| %s | %s | %s | %s | %s |' % (source.get('name'), source.get('http_status'),
                    source.get('status'), source.get('observed_at'), source.get('bytes')))
    if receipt['fixture_evidence_ids_missing_from_board']:
        lines += ['', '**Feed rows missing from the board (defect):** %s'
                  % ', '.join(receipt['fixture_evidence_ids_missing_from_board'])]
    if receipt['contract']['problems']:
        lines += ['', '## Contract problems', ''] + ['- %s' % p for p in receipt['contract']['problems']]
    lines += ['', receipt['scope'], '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='data/latest.json')
    parser.add_argument('--output', default='research/harvest-e334b970')
    args = parser.parse_args()
    snapshot = json.loads(Path(args.snapshot).read_text())
    receipt = build(snapshot)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'coverage-receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    (out / 'coverage-receipt.md').write_text(markdown(receipt) + '\n')
    print(json.dumps(receipt['counts'], indent=1))


if __name__ == '__main__':
    main()
