"""Every-match coverage report for session 233b8a0e.

Answers one question with no interpretation: for every CS2 fixture the Hotspawn
feed returned, did this snapshot produce a pick, and from which rung of the
documented ladder? It reads the snapshot and reports only values present in it.

Rungs, in the publication order used by ``scripts.refresh`` (see
``sources.html#method``): Polymarket strict exchange, HLTV fixture identity
research, Pinnacle moneyline, labelled wide exchange, researched bookmaker
listing, our Valve-VRS model line, the same model from HLTV's dated view of
Valve's ranking, one-sided Valve standings, and HLTV ranking/form research.

Nothing here creates, corrects or infers a pick. A row with no pick is listed
with its own recorded ``reason`` and every recorded attempt, so the separate
unresolved section of the site can quote it verbatim.
"""
import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RUNG_LABELS = (
    ('exchange', 'Polymarket exchange line, strict gate'),
    ('exchange_wide', 'Wide exchange quote, labelled low confidence'),
    ('bookmaker_fallback', 'Researched bookmaker listing (Thunderpick via bo3.gg)'),
    ('bookmaker', 'Bookmaker moneyline'),
    ('pinnacle', 'Pinnacle esports moneyline'),
    ('model_vrs', 'Our own Valve-VRS model line'),
    ('model_vrs_mirror', "Our VRS model from HLTV's dated Valve ranking"),
    ('research_rank', 'HLTV ranking-order research pick (no percentage)'),
    ('research_rank_single', 'HLTV one-sided ranking research pick (no percentage)'),
    ('research_vrs_single', 'One-sided Valve standings research pick (no percentage)'),
    ('research_form', 'HLTV recent-form research pick (no percentage)'),
)


def moment(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00')).astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def report(snapshot):
    matches = snapshot.get('matches') or []
    observed = moment(snapshot.get('fixtures_observed_at') or snapshot.get('generated_at'))
    open_rows = [m for m in matches if m.get('state') == 'open']
    past = [m for m in matches if m.get('state') != 'open']
    picks = [m for m in open_rows if m.get('pick')]
    priced = [m for m in open_rows if m.get('probabilities') is not None]
    unpriced = [m for m in open_rows if m.get('probabilities') is None]
    unresolved = [m for m in open_rows if not m.get('pick')]
    # A verified line priced exactly even publishes a probability and no pick
    # (``scripts.summary.is_no_edge``); it is neither "picked" nor "unresolved",
    # and counting it as either is what made the 2026-10-24 publish gate red.
    from scripts import summary as _summary
    no_edge = [m for m in open_rows if _summary.is_no_edge(m)]
    methods = Counter(str(m.get('method')) for m in open_rows)
    rungs = [{'method': method, 'label': label, 'rows': methods.get(method, 0),
              'ids': [m['id'] for m in open_rows if str(m.get('method')) == method]}
             for method, label in RUNG_LABELS]
    unknown = [{'method': method, 'rows': count,
                'ids': [m['id'] for m in open_rows if str(m.get('method')) == method]}
               for method, count in methods.items()
               if method not in {m for m, _ in RUNG_LABELS}]
    ledger = []
    for m in sorted(unresolved, key=lambda x: (x.get('start') or '', x['id'])):
        ledger.append({
            'id': m['id'],
            'teams': m['teams'],
            'start': m.get('start'),
            'competition': m.get('competition'),
            'source_url': m.get('source_url'),
            'reason': m.get('reason'),
            'no_edge': _summary.is_no_edge(m),
            'attempts': [{'provider': a.get('provider'), 'status': a.get('status'),
                          'reason': a.get('reason'), 'url': a.get('url')}
                         for a in (m.get('attempts') or [])],
        })
    research_only = [m['id'] for m in unpriced if m.get('pick')]
    return {
        'snapshot_generated_at': snapshot.get('generated_at'),
        'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
        'coverage': snapshot.get('coverage'),
        'observed_utc': observed.isoformat().replace('+00:00', 'Z') if observed else None,
        'rows_total': len(matches),
        'rows_past_dated': len(past),
        'rows_open': len(open_rows),
        'open_with_pick': len(picks),
        'open_with_probability': len(priced),
        'open_research_only': len(research_only),
        'open_unresolved': len(unresolved),
        'open_no_edge': len(no_edge),
        'open_no_edge_ids': [m['id'] for m in no_edge],
        'rungs': rungs,
        'unknown_methods': unknown,
        'unresolved_ledger': ledger,
    }


def markdown(summary):
    lines = [
        '# Every-match coverage — snapshot %s' % summary['snapshot_generated_at'],
        '',
        'Fixture evidence read at **%s** (UTC). Coverage status: **%s**.'
        % (summary['observed_utc'], summary['coverage']),
        '',
        '| Measure | Rows |', '| --- | --- |',
        '| Hotspawn CS2 feed records | %d |' % summary['rows_total'],
        '| Past-dated records (not presented as current picks) | %d |' % summary['rows_past_dated'],
        '| Open matches | %d |' % summary['rows_open'],
        '| Open matches with a pick | %d |' % summary['open_with_pick'],
        '| Open matches with a win probability | %d |' % summary['open_with_probability'],
        '| Open matches with a research pick and no percentage | %d |' % summary['open_research_only'],
        '| Open matches with no pick at all | %d |' % summary['open_unresolved'],
        '',
        '## Which rung produced each pick',
        '',
        '| Rung (publication order) | Rows | Fixture IDs |', '| --- | --- | --- |',
    ]
    for rung in summary['rungs']:
        lines.append('| %s (`%s`) | %d | %s |'
                     % (rung['label'], rung['method'], rung['rows'], ', '.join(rung['ids']) or '—'))
    for extra in summary['unknown_methods']:
        lines.append('| UNRECOGNISED `%s` | %d | %s |'
                     % (extra['method'], extra['rows'], ', '.join(extra['ids'])))
    lines += ['', '## Unresolved ledger (HLTV first, then esportsbook lines)', '']
    if not summary['unresolved_ledger']:
        lines.append('None: every open match in this snapshot carries a pick. The section stays '
                     'published on the site so a later snapshot that cannot price a row is visible '
                     'in the same place.')
    for row in summary['unresolved_ledger']:
        lines.append('### %s — %s vs %s' % (row['id'], row['teams'][0], row['teams'][1]))
        lines.append('')
        lines.append('* %s · %s · %s' % (row['competition'], row['start'], row['source_url']))
        lines.append('* Recorded limitation: %s' % (row['reason'] or 'unverified'))
        if row['attempts']:
            lines.append('* Attempted sources:')
            for attempt in row['attempts']:
                lines.append('  * %s — %s: %s %s' % (attempt['provider'], attempt['status'],
                                                     attempt['reason'], attempt['url']))
        else:
            lines.append('* No source attempt was recorded for this row — flagged as unverified.')
        lines.append('')
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output', default='research/harvest-233b8a0e')
    args = parser.parse_args()
    snapshot = json.loads(Path(args.snapshot).read_text())
    summary = report(snapshot)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'coverage.json').write_text(json.dumps(summary, indent=1) + '\n')
    (out / 'coverage.md').write_text(markdown(summary))
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ('unresolved_ledger', 'rungs', 'unknown_methods')}, indent=1))
    for rung in summary['rungs']:
        print('%-6d %-62s %s' % (rung['rows'], rung['label'], rung['method']))
    if summary['open_unresolved']:
        print('unresolved: ' + ', '.join(r['id'] for r in summary['unresolved_ledger']))


if __name__ == '__main__':
    main()
