"""Per-row census of a refreshed CS2 snapshot, for session 77046e56.

Reads a snapshot produced by ``python -m scripts.refresh`` and prints -- and
writes -- one line per open fixture: teams, start, pick, both probabilities, the
pricing method, how many outside sources the row carries, and, for any row with
no percentage, the recorded reason and every attempted provider.

Nothing here publishes, prices or edits a row. It is a reader, so its counts can
be compared against what the site later renders.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import Counter
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output', default='research/session-77046e56/harvest')
    args = parser.parse_args()

    data = json.loads(pathlib.Path(args.snapshot).read_text())
    rows = data.get('matches', [])
    now = datetime.now(timezone.utc)
    opens = [r for r in rows if r.get('state') == 'open']
    methods = Counter(r.get('method') or 'none' for r in opens)
    picks = [r for r in opens if r.get('pick')]
    priced = [r for r in opens if r.get('probabilities')]

    out = []
    out.append('# Refreshed snapshot census — session 77046e56')
    out.append('')
    out.append('| Field | Value |')
    out.append('| --- | --- |')
    out.append('| Snapshot generated_at | %s |' % data.get('generated_at'))
    out.append('| Fixtures observed_at | %s |' % data.get('fixtures_observed_at'))
    out.append('| Read by this census | %s |' % now.isoformat())
    out.append('| Feed rows | %s |' % len(rows))
    out.append('| Open rows | %s |' % len(opens))
    out.append('| Open rows with a pick | %s |' % len(picks))
    out.append('| Open rows with a two-way probability | %s |' % len(priced))
    out.append('| Open rows with a pick but no percentage | %s |' % len([r for r in opens if r.get('pick') and not r.get('probabilities')]))
    out.append('| Open rows with neither | %s |' % len([r for r in opens if not r.get('pick') and not r.get('probabilities')]))
    out.append('| Coverage | %s |' % data.get('coverage'))
    out.append('| Methods | %s |' % ', '.join('%s: %s' % (k, v) for k, v in sorted(methods.items())))
    out.append('| Coverage counts | `%s` |' % json.dumps(data.get('coverage_counts', {})))
    out.append('')
    out.append('## Every open fixture')
    out.append('')
    out.append('| # | ID | Start (UTC) | Teams | Competition | Tier | Pick | Probability | Method | Sources on row | Flags |')
    out.append('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    for index, row in enumerate(sorted(opens, key=lambda r: (r.get('start') or '', r['id'])), 1):
        probs = row.get('probabilities')
        if probs and row.get('pick'):
            named = ['%s %.1f%%' % (team, p * 100) for team, p in zip(row['teams'], probs)]
            probability = ' · '.join(named)
        elif probs:
            probability = ' · '.join('%.1f%%' % (p * 100) for p in probs)
        else:
            probability = '—'
        sources = _source_count(row)
        out.append('| %s | %s | %s | %s vs %s | %s | %s | %s | %s | %s | %s | %s |' % (
            index, row['id'], row.get('start'), row['teams'][0], row['teams'][1],
            row.get('competition'), row.get('tier'), row.get('pick') or '—',
            probability, row.get('method') or '—', sources,
            '; '.join(row.get('flags') or []) or '—'))
    out.append('')
    out.append('## Rows without a two-way probability')
    out.append('')
    blanks = [r for r in opens if not r.get('probabilities')]
    if not blanks:
        out.append('None: every open fixture carries a two-way probability in this snapshot.')
    for row in blanks:
        out.append('### %s — %s vs %s (%s)' % (row['id'], row['teams'][0], row['teams'][1], row.get('start')))
        out.append('')
        out.append('* Pick: %s' % (row.get('pick') or 'none'))
        out.append('* Method: %s' % (row.get('method') or 'none'))
        out.append('* Reason: %s' % (row.get('reason') or 'none'))
        for attempt in row.get('attempts') or []:
            out.append('* Attempt: %s → %s%s%s' % (
                attempt.get('provider'), attempt.get('status'),
                ' — ' + str(attempt.get('reason')) if attempt.get('reason') else '',
                ' (' + str(attempt.get('url')) + ')' if attempt.get('url') else ''))
        out.append('')
    out.append('## Issues recorded by the refresh')
    out.append('')
    for issue in data.get('issues') or []:
        out.append('* `%s` %s — %s' % (issue.get('code'), issue.get('message'), issue.get('source')))
    if not data.get('issues'):
        out.append('None.')

    text = '\n'.join(out) + '\n'
    target = pathlib.Path(args.output)
    target.mkdir(parents=True, exist_ok=True)
    (target / 'census.md').write_text(text)
    print(text)
    (target / 'snapshot.json').write_text(json.dumps(data, indent=1) + '\n')
    return 0


def _source_count(row):
    urls = set()
    for item in row.get('evidence') or []:
        for key in ('url', 'source_url', 'feed_url'):
            if item.get(key):
                urls.add(item[key])
        for receipt in item.get('source_receipts') or []:
            if receipt.get('url'):
                urls.add(receipt['url'])
        for quote in item.get('quotes') or []:
            if quote.get('url'):
                urls.add(quote['url'])
    if row.get('source_url'):
        urls.add(row['source_url'])
    return len(urls)


if __name__ == '__main__':
    raise SystemExit(main())
