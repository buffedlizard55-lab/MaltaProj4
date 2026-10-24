"""Unresolved-row ledger for session d2a55add.

Why this exists
---------------
The featured picks are the rows a strict Polymarket exchange line resolves.
Every other open Hotspawn CS2 row still has to earn a pick, and the order the
collector must try is fixed by the request behind this session:

1. HLTV first - exact fixture identity, world rankings, lineups, recent form
   and head-to-head on the fixture's own HLTV page;
2. then esportsbooks and betting lines - Pinnacle's esports moneyline, the
   labelled wide exchange tier, researched bookmaker listings (bo3.gg /
   EGamersWorld receipts re-observed against the live listing), Thunderpick
   and GG.BET access attempts;
3. then our own originated Valve VRS model line (and its HLTV mirror);
4. then a research-only pick (ranking order, one-sided standings, HLTV form)
   with no percentage;
5. anything left is unresolved: no pick, no percentage, and this ledger is
   the published record of exactly what was tried and why it was not enough.

This module never prices anything. It reads one refreshed snapshot and writes
a dated ledger (JSON + Markdown) covering every open row that the featured
exchange tier did not resolve, in ladder order, with the row's own recorded
attempts. A row whose recorded attempts contain no HLTV step or no book step
is flagged as an irregularity instead of being described as researched: a
missing attempt is a collection gap, never evidence that no line exists.

Usage: python -m scripts.gap_probe_d2a55add --snapshot runtime/latest.json \
           --output research/harvest-d2a55add
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import summary

ROOT = Path(__file__).resolve().parents[1]

# Provider labels as scripts.refresh records them, grouped by ladder step.
HLTV_PROVIDERS = ('HLTV', 'HLTV team pages', 'HLTV lineup receipt')
BOOK_PROVIDERS = ('Pinnacle', 'Book research', 'Book listing re-observation',
                  'Book listing gap recheck', 'Thunderpick',
                  'Thunderpick (via BO3.gg API)', 'GG.BET')
EXCHANGE_PROVIDERS = ('Polymarket',)


def _attempts(match):
    return [a for a in (match.get('attempts') or []) if isinstance(a, dict)]


def _step(match, providers):
    """Best recorded outcome for one ladder step: resolved > error > unresolved."""
    seen = [a for a in _attempts(match) if (a.get('provider') or '') in providers]
    if not seen:
        return 'not recorded', []
    statuses = {str(a.get('status') or '') for a in seen}
    if 'resolved' in statuses:
        status = 'resolved'
    elif 'error' in statuses:
        status = 'access refused or failed'
    else:
        status = 'no usable line'
    return status, [{'provider': a.get('provider'), 'status': a.get('status'),
                     'reason': a.get('reason'), 'url': a.get('url')} for a in seen]


def ledger(snapshot):
    """One entry per open row the strict exchange tier did not resolve."""
    rows = []
    irregularities = []
    for m in snapshot.get('matches') or []:
        if m.get('state') != 'open':
            continue
        if m.get('method') == 'exchange' and m.get('probabilities') is not None:
            continue  # featured pick: resolved the same way as the headline board
        kind, label, basis = summary.origin(m)
        limitation = (summary.limitation(m) if m.get('probabilities') is None
                      else 'Not applicable: this row carries a win probability (%s).' % basis)
        hltv_status, hltv_attempts = _step(m, HLTV_PROVIDERS)
        book_status, book_attempts = _step(m, BOOK_PROVIDERS)
        exchange_status, exchange_attempts = _step(m, EXCHANGE_PROVIDERS)
        flags = []
        if hltv_status == 'not recorded':
            flags.append('No HLTV attempt recorded for a non-featured row; '
                         'HLTV must be tried first.')
        if book_status == 'not recorded':
            flags.append('No esportsbook/betting-line attempt recorded for a '
                         'non-featured row; a book line must be tried after HLTV.')
        entry = {
            'id': m.get('id'), 'teams': m.get('teams'),
            'competition': m.get('competition'), 'start': m.get('start'),
            'lock': m.get('lock'), 'pick': m.get('pick'),
            'method': m.get('method'), 'origin': kind, 'origin_label': label,
            'probabilities': m.get('probabilities'),
            'exchange_step': exchange_status,
            'hltv_first_step': hltv_status, 'hltv_attempts': hltv_attempts,
            'book_step': book_status, 'book_attempts': book_attempts,
            'limitation': limitation,
            'source_url': m.get('source_url'),
            'flags': sorted(set((m.get('flags') or []))) ,
            'irregularities': flags,
        }
        rows.append(entry)
        for flag in flags:
            irregularities.append({'id': m.get('id'), 'teams': m.get('teams'),
                                   'irregularity': flag})
    rows.sort(key=lambda r: (r.get('start') or '', str(r.get('id'))))
    counts = {
        'non_featured_open': len(rows),
        'with_probability': sum(r['probabilities'] is not None for r in rows),
        'research_only_pick': sum(r['probabilities'] is None and bool(r['pick']) for r in rows),
        'unresolved_no_pick': sum(not r['pick'] for r in rows),
        'hltv_not_recorded': sum(r['hltv_first_step'] == 'not recorded' for r in rows),
        'book_not_recorded': sum(r['book_step'] == 'not recorded' for r in rows),
    }
    return {'generated_at': snapshot.get('generated_at'),
            'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
            'counts': counts, 'rows': rows, 'irregularities': irregularities}


def render_markdown(book):
    c = book['counts']
    lines = ['# Unresolved & non-featured pick ledger — session d2a55add', '',
             'Snapshot generated `%s`; fixtures observed `%s`.' % (
                 book.get('generated_at'), book.get('fixtures_observed_at')), '',
             'Every open Hotspawn CS2 row that the featured strict-exchange tier did not '
             'resolve, in start order. HLTV is tried first, then esportsbook/betting '
             'lines, then the originated VRS model, then research-only evidence. '
             'Nothing here invents a price: a blank percentage means unverified.', '',
             '| Count | Rows |', '| --- | --- |',
             '| Non-featured open rows | %d |' % c['non_featured_open'],
             '| …with a win probability (book/model/wide) | %d |' % c['with_probability'],
             '| …research-only pick, no percentage | %d |' % c['research_only_pick'],
             '| …unresolved, no pick at all | %d |' % c['unresolved_no_pick'],
             '| …missing a recorded HLTV attempt (irregularity) | %d |' % c['hltv_not_recorded'],
             '| …missing a recorded book attempt (irregularity) | %d |' % c['book_not_recorded'],
             '']
    for r in book['rows']:
        lines += ['## %s vs %s (`%s`)' % (r['teams'][0], r['teams'][1], r['id']),
                  '',
                  '- Competition: %s · starts %s UTC · lock %s UTC' % (
                      r['competition'], r['start'], r['lock']),
                  '- Published answer: **%s** — pick `%s`, method `%s`, probabilities `%s`' % (
                      r['origin_label'], r['pick'], r['method'], r['probabilities']),
                  '- Exchange (featured) step: %s' % r['exchange_step'],
                  '- HLTV first: %s' % r['hltv_first_step'],
                  '- Esportsbook lines next: %s' % r['book_step'],
                  '- Limitation: %s' % r['limitation'],
                  '- Hotspawn source: %s' % r['source_url']]
        for a in r['hltv_attempts'] + r['book_attempts']:
            lines.append('  - attempt `%s` → %s: %s (%s)' % (
                a['provider'], a['status'], a['reason'], a['url']))
        for flag in r['irregularities']:
            lines.append('  - **IRREGULARITY:** %s' % flag)
        lines.append('')
    if book['irregularities']:
        lines += ['## Irregularities for manual review', '']
        for item in book['irregularities']:
            lines.append('- `%s` %s — %s' % (item['id'], item['teams'], item['irregularity']))
        lines.append('')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output', default='research/harvest-d2a55add')
    args = parser.parse_args()
    snapshot = json.loads(Path(args.snapshot).read_text())
    book = ledger(snapshot)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'unresolved-ledger.json').write_text(
        json.dumps(book, indent=2, ensure_ascii=False) + '\n')
    (out / 'unresolved-ledger.md').write_text(render_markdown(book))
    print(json.dumps(book['counts'], indent=2, sort_keys=True))
    if book['irregularities']:
        print('IRREGULARITIES: %d (recorded in the ledger, non-blocking)' % len(book['irregularities']))


if __name__ == '__main__':
    main()
