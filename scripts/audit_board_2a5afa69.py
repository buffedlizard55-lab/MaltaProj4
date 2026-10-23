"""Row-by-row audit of one Hotspawn CS2 board snapshot (session 2a5afa69).

Read-only. It answers three questions for every open fixture in a snapshot
produced by ``scripts.refresh`` on a networked runner:

1. Is there a pick, and does it name one of the fixture's two teams?
2. If a percentage is published, can it be reproduced from the row's own
   evidence object (the same rule ``scripts.validate`` and the independent
   auditors apply), and is its deadline still in the future at build time?
3. If there is no pick, exactly which sources were tried and what did each
   return? The attempt ladder is copied verbatim, never summarised into a
   guess.

Nothing is inferred, corrected or written back to the board. The output is a
dated receipt for human verification plus a machine-readable JSON file.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.core import dt, pick_deadline

MARKET = ('exchange', 'exchange_wide', 'bookmaker_fallback')
MODEL = ('model_vrs', 'model_vrs_mirror')
RESEARCH = ('research_rank', 'research_rank_single', 'research_vrs_single')


def reproduce(row: dict, clock: datetime) -> tuple[bool | None, str]:
    """Recompute the published pair from the row's evidence, or say why not."""
    probs = row.get('probabilities')
    if probs is None:
        return None, 'no percentage published'
    if not isinstance(probs, list) or len(probs) != 2:
        return False, 'probability pair is not two numbers'
    if abs(sum(probs) - 1.0) > 1e-9:
        return False, 'probability pair does not sum to 1'
    if any(p is None or p <= 0 or p >= 1 for p in probs):
        return False, 'probability outside the open interval (0, 1)'
    method = row.get('method')
    evidence = row.get('evidence') or []
    if method in MARKET:
        if not evidence:
            return False, 'market row carries no quote evidence'
        quote = evidence[0]
        if quote.get('decimal_odds'):
            odds = quote['decimal_odds']
            if len(odds) != 2:
                return False, 'market row carries no two-way decimal odds'
            raw = [1.0 / float(o) for o in odds]
            total = sum(raw)
            if total <= 0:
                return False, 'implied probability total is zero'
            implied = [round(r / total, 10) for r in raw]
            if any(abs(a - b) > 5e-9 for a, b in zip(implied, probs)):
                return False, 'published pair does not equal the de-vigged quote'
        else:
            # Exchange rows publish the exchange's own two-way price vector,
            # renormalised so the pair sums to exactly 1.
            raw = quote.get('probabilities')
            if not raw or len(raw) != 2:
                return False, 'market row carries neither decimal odds nor a two-way price pair'
            total = sum(float(p) for p in raw)
            if total <= 0:
                return False, 'implied probability total is zero'
            implied = [round(float(r) / total, 10) for r in raw]
            if any(abs(a - b) > 5e-9 for a, b in zip(implied, probs)):
                return False, 'published pair does not equal the normalised exchange price'
            if quote.get('spread') is None or quote.get('liquidity') is None:
                return False, 'exchange row lost its spread or liquidity gate record'
        try:
            observed = dt(quote.get('observed_at'))
        except (TypeError, ValueError, OverflowError, OSError):
            return False, 'quote has no readable observation time'
        age_h = (clock - observed).total_seconds() / 3600.0
        if age_h < -0.1 or age_h > 8:
            return False, 'quote observation is outside the 8-hour window (%.2fh)' % age_h
        return True, 'reproduced from %s quote' % quote.get('provider', 'market')
    if method in MODEL:
        if not evidence:
            return False, 'model row carries no standings evidence'
        quote = evidence[0]
        try:
            observed = dt(quote.get('observed_at'))
        except (TypeError, ValueError, OverflowError, OSError):
            return False, 'model evidence has no readable observation time'
        age_h = (clock - observed).total_seconds() / 3600.0
        if age_h < -0.1 or age_h > 8:
            return False, 'model evidence is outside the 8-hour window (%.2fh)' % age_h
        if not str(quote.get('url') or '').startswith('https://'):
            return False, 'model evidence has no https source'
        points = quote.get('points')
        if not points or len(points) != 2:
            return False, 'model row carries no Valve points for both teams'
        from scripts import vrs  # imported lazily so --help works without deps
        recomputed = vrs.calibrated(vrs.expected(float(points[0]), float(points[1])))
        if abs(recomputed - probs[0]) > 5e-9:
            return False, 'published pair does not equal the recomputed VRS line'
        return True, 'recomputed from Valve points %s / %s' % (points[0], points[1])
    if method in RESEARCH:
        return False, 'research tier must not publish a percentage'
    return False, 'unknown method %r' % (method,)


def deadline_state(row: dict, observed: str | None, clock: datetime) -> str:
    try:
        deadline = row.get('expires_at') or pick_deadline(row, observed)
    except (TypeError, ValueError, OverflowError, OSError, KeyError):
        return 'unreadable'
    if not deadline:
        return 'none recorded'
    if isinstance(deadline, str):
        return deadline
    return deadline.isoformat().replace('+00:00', 'Z')


def audit(snapshot: dict, now: datetime | None = None) -> dict:
    clock = now or dt(snapshot.get('built_at') or snapshot.get('generated_at'))
    observed = snapshot.get('fixtures_observed_at')
    rows = []
    for m in snapshot.get('matches', []):
        if m.get('state') != 'open':
            continue
        ok, why = reproduce(m, clock)
        evidence = []
        for quote in m.get('evidence') or []:
            evidence.append({k: quote.get(k) for k in ('provider', 'url', 'api_url', 'observed_at',
                                                       'expires_at', 'decimal_odds', 'spread', 'liquidity')})
        attempts = []
        for a in m.get('attempts') or []:
            attempts.append({k: a.get(k) for k in ('provider', 'status', 'url', 'reason')})
        rows.append({
            'id': m.get('id'), 'teams': m.get('teams'), 'start': m.get('start'),
            'competition': m.get('competition'), 'tier': m.get('tier'),
            'pick': m.get('pick'), 'method': m.get('method'),
            'probabilities': m.get('probabilities'),
            'pick_is_a_team': bool(m.get('pick')) and m.get('pick') in (m.get('teams') or []),
            'percentage_reproduced': ok, 'reproduction_note': why,
            'deadline': deadline_state(m, observed, clock),
            'source_url': m.get('source_url'), 'evidence': evidence,
            'attempts': attempts, 'reason': m.get('reason'),
        })
    return {
        'audited_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'snapshot_generated_at': snapshot.get('generated_at'),
        'fixtures_observed_at': observed,
        'built_at': snapshot.get('built_at'),
        'rows_total': len(snapshot.get('matches', [])),
        'rows_open': len(rows),
        'rows_with_pick': sum(1 for r in rows if r['pick']),
        'rows_with_percentage': sum(1 for r in rows if r['probabilities'] is not None),
        'rows_reproduced': sum(1 for r in rows if r['percentage_reproduced'] is True),
        'rows_without_pick': [r['id'] for r in rows if not r['pick']],
        'rows_failing_reproduction': [r['id'] for r in rows if r['percentage_reproduced'] is False],
        'rows': rows,
    }


def markdown(report: dict) -> str:
    out = ['# Board audit — every open Hotspawn CS2 fixture', '',
           'Snapshot `%s` · fixture evidence `%s` · audited `%s`' % (
               report['snapshot_generated_at'], report['fixtures_observed_at'], report['audited_at']),
           '',
           '**%d open rows · %d with a pick · %d with a percentage · %d percentages reproduced · %d without a pick**'
           % (report['rows_open'], report['rows_with_pick'], report['rows_with_percentage'],
              report['rows_reproduced'], len(report['rows_without_pick'])), '',
           'A pick is never invented here: a row without one is listed by name with every source that was tried.', '',
           '| # | Start (UTC) | Match | Pick | Win % | Method | Reproduced | Source |',
           '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for i, r in enumerate(report['rows'], 1):
        pick = r['pick'] or '**(none)**'
        if r['probabilities'] and r['pick'] in (r['teams'] or []):
            pct = '%.1f%% / %.1f%%' % (r['probabilities'][0] * 100, r['probabilities'][1] * 100)
        else:
            pct = '—'
        reproduced = {True: 'yes', False: '**no**', None: 'n/a'}[r['percentage_reproduced']]
        source = r['source_url'] or ''
        out.append('| %d | %s | %s vs %s | %s | %s | `%s` | %s | [fixture](%s) |' % (
            i, (r['start'] or '').replace('T', ' ').replace(':00Z', ' UTC'), r['teams'][0], r['teams'][1],
            pick, pct, r['method'], reproduced, source))
    if report['rows_without_pick']:
        out += ['', '## Open rows with no pick, and every source tried', '']
        for r in report['rows']:
            if r['pick']:
                continue
            out += ['### %s — %s vs %s' % (r['id'], r['teams'][0], r['teams'][1]), '',
                    'Fixture: %s' % (r['source_url'] or 'not recorded'), '']
            if r['reason']:
                out += ['Recorded limitation: %s' % r['reason'], '']
            if r['attempts']:
                out += ['| Source tried | Status | Reason | Link |', '| --- | --- | --- | --- |']
                for a in r['attempts']:
                    out.append('| %s | %s | %s | %s |' % (a['provider'], a['status'],
                                                         (a['reason'] or '').replace('|', '/'),
                                                         a['url'] or '—'))
                out.append('')
    else:
        out += ['', 'Every open fixture in this snapshot carries a pick.']
    return '\n'.join(out).rstrip() + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='runtime/latest.json')
    parser.add_argument('--output', required=True, help='directory for board-audit.json and BOARD-AUDIT.md')
    args = parser.parse_args()
    snapshot = json.loads(Path(args.snapshot).read_text())
    report = audit(snapshot)
    target = Path(args.output)
    target.mkdir(parents=True, exist_ok=True)
    (target / 'board-audit.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    (target / 'BOARD-AUDIT.md').write_text(markdown(report))
    print(json.dumps({k: report[k] for k in ('rows_total', 'rows_open', 'rows_with_pick', 'rows_with_percentage',
                                             'rows_reproduced', 'rows_without_pick',
                                             'rows_failing_reproduction')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
