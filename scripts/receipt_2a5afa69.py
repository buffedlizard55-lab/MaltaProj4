"""Compact, human-readable receipt for one freshly captured board (session 2a5afa69).

Reads a ``scripts.refresh`` snapshot and the matching ``board-audit.json`` and
prints markdown small enough to post as a GitHub issue comment (the runner's
uploaded artifacts and raw logs are not reachable from every environment). Every
line is copied from the snapshot: no value is rounded up, inferred or filled in.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MAX_CHARS = 60000


def money(value):
    try:
        return '%.2f' % float(value)
    except (TypeError, ValueError):
        return '—'


def pct(pair, pick, teams):
    if not pair or len(pair) != 2:
        return '—'
    a, b = pair
    return '%.1f%% / %.1f%%' % (a * 100, b * 100) if pick in teams else '%.1f%% / %.1f%%' % (a * 100, b * 100)


def row_line(r):
    pair = r.get('probabilities')
    when = (r.get('start') or '').replace('T', ' ').replace(':00Z', ' UTC')
    pick = r.get('pick') or '**(no pick)**'
    source = r.get('source_url') or ''
    ev = (r.get('evidence') or [{}])[0]
    link = ev.get('api_url') or ev.get('url') or ''
    note = ' | %s %s' % (ev.get('provider', ''), ('spread %s, liquidity $%s' % (money(ev.get('spread')), money(ev.get('liquidity'))))
                         if ev.get('spread') is not None else '') if ev else ''
    return '| %s | %s vs %s | %s | %s | `%s` | %s | [fixture](%s)%s |' % (
        when, r['teams'][0], r['teams'][1], pick,
        ('%.1f%% / %.1f%%' % (pair[0] * 100, pair[1] * 100)) if pair else '—',
        r.get('method'), ('%s' % link) if link else '—', source, note)


def build(snapshot, report):
    out = []
    out.append('**Snapshot** `%s` · fixture evidence `%s` · audit `%s`' % (
        snapshot.get('generated_at'), snapshot.get('fixtures_observed_at'), report.get('audited_at')))
    out.append('')
    out.append('| Rows | Open | With a pick | With a % | Reproduced | Without a pick |')
    out.append('| --- | --- | --- | --- | --- | --- |')
    out.append('| %s | %s | %s | %s | %s | %s |' % (
        report.get('rows_total'), report.get('rows_open'), report.get('rows_with_pick'),
        report.get('rows_with_percentage'), report.get('rows_reproduced'),
        ','.join(report.get('rows_without_pick') or []) or 'none'))
    out.append('')
    out.append('**Coverage status:** `%s` · source checks: %d · issues: %d' % (
        snapshot.get('coverage'), len(snapshot.get('source_checks') or []), len(snapshot.get('issues') or [])))
    for issue in (snapshot.get('issues') or [])[:12]:
        out.append('- %s — %s — %s' % (issue.get('code'), (issue.get('message') or '')[:300], issue.get('source')))
    out.append('')
    out.append('### Every open fixture, line by line')
    out.append('')
    out.append('| Start (UTC) | Match | Pick | Win % | Method | Evidence | Fixture |')
    out.append('| --- | --- | --- | --- | --- | --- | --- |')
    for r in report.get('rows', []):
        out.append(row_line(r))
    missing = [r for r in report.get('rows', []) if not r.get('pick')]
    if missing:
        out.append('')
        out.append('### Open rows with no pick, and every source tried')
        for r in missing:
            out.append('')
            out.append('**%s — %s vs %s** (%s)' % (r['id'], r['teams'][0], r['teams'][1], r.get('competition')))
            out.append('')
            out.append('Limitation recorded: %s' % (r.get('reason') or 'not recorded'))
            out.append('')
            out.append('| Source tried | Status | Reason | Link |')
            out.append('| --- | --- | --- | --- |')
            for a in r.get('attempts') or []:
                out.append('| %s | %s | %s | %s |' % (
                    a.get('provider'), a.get('status'), (a.get('reason') or '').replace('|', '/'), a.get('url') or '—'))
    text = '\n'.join(out)
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + '\n\n…receipt truncated by the poster; the full JSON is in the run artifact.'
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--audit', default='research/harvest-2a5afa69/board-audit.json')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    snapshot = json.loads(Path(args.snapshot).read_text())
    report = json.loads(Path(args.audit).read_text())
    text = build(snapshot, report)
    Path(args.output).write_text(text + '\n')
    print('receipt chars:', len(text))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
