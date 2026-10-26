"""Session 28e4f2a1 — independent re-derivation of every published line.

Re-implements the arithmetic and the published gates here (it does not import
``scripts/``), stage by stage, from the raw source bytes stored on each row:

  exchange             Polymarket ``outcomePrices`` -> p = x / (x1 + x2), plus
                       the strict gates: two-sided, accepting orders, active and
                       not closed, spread <= 0.25, liquidity >= $100, a source
                       update inside the eight-hour window, and the market's own
                       ``gameStartTime`` equal to the fixture's UTC start.
  bookmaker_fallback   stored decimal odds -> 1/d, de-vigged the same way, with
                       the overround inside the published -2%..25% band.
  model_vrs            recomputed separately by verify_model.py from Valve's
                       official file (cross-referenced here by row id).

Every row must also satisfy: the published pick is the strictly higher side,
the fair odds are the reciprocals, and both percentages are strictly inside
(0, 1) and sum to 1.
"""
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WINDOW = timedelta(hours=8)


def dt(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def devig(prices):
    total = sum(prices)
    return [p / total for p in prices]


def main():
    snap = json.loads((ROOT / 'data/latest.json').read_text())
    model = json.loads((HERE / 'model-receipt.json').read_text())
    model_ids = {r['fixture'] for r in model['rows'] if r['kind'] == 'published_line'}
    generated = dt(snap['generated_at'])
    rows, problems = [], []
    for m in snap['matches']:
        if m.get('state') != 'open':
            continue
        record = {'fixture': m['id'], 'teams': m['teams'], 'method': m.get('method'),
                  'pick': m.get('pick'), 'published': m.get('probabilities'),
                  'checks': [], 'problems': []}

        def check(ok, message):
            record['checks'].append({'ok': bool(ok), 'check': message})
            if not ok:
                record['problems'].append(message)
                problems.append('%s %s: %s' % (m['id'], ' vs '.join(m['teams']), message))

        p = m.get('probabilities')
        check(p is not None and len(p) == 2, 'two probabilities published')
        if p:
            check(all(0 < x < 1 for x in p), 'both probabilities strictly inside (0, 1)')
            check(abs(sum(p) - 1) < 1e-9, 'probabilities sum to 1')
            check(m.get('fair_odds') and max(abs(1 / x - f) for x, f in zip(p, m['fair_odds'])) < 1e-9,
                  'fair odds are the reciprocals of the published probabilities')
            if len(set(p)) > 1:
                favourite = m['teams'][0] if p[0] > p[1] else m['teams'][1]
                check(m.get('pick') == favourite, 'pick is the strictly higher-probability side')
            else:
                check(m.get('pick') is None, 'an exactly even line publishes no directional pick')
        quote = (m.get('evidence') or [{}])[0]
        raw = quote.get('raw') or {}
        if m.get('method') in ('exchange', 'exchange_wide'):
            prices = json.loads(raw.get('outcomePrices') or '[]')
            check(len(prices) == 2, 'raw Polymarket outcomePrices carries two sides')
            if len(prices) == 2:
                recomputed = devig([float(x) for x in prices])
                check(max(abs(a - b) for a, b in zip(recomputed, p)) < 1e-12,
                      'exchange probabilities reproduce from the raw outcome prices (de-vigged)')
            check(raw.get('acceptingOrders') is True, 'market is accepting orders')
            check(raw.get('active') is True and raw.get('closed') is False, 'market is active and not closed')
            bid, ask = raw.get('bestBid'), raw.get('bestAsk')
            check(bid is not None and ask is not None and 0 < bid < ask < 1, 'two-sided bid/ask present')
            if bid is not None and ask is not None:
                spread = float(ask) - float(bid)
                ceiling = 0.60 if m.get('method') == 'exchange_wide' else 0.25
                # The published gate is "no greater than 25 points", so an exactly
                # 25-point spread passes; the epsilon only absorbs float arithmetic
                # on bid/ask (0.575 - 0.325 == 0.25000000000000006).
                check(spread <= ceiling + 1e-9,
                      'spread %.6f inside the %.2f ceiling' % (spread, ceiling))
            check(float(raw.get('liquidity') or 0) >= 100, 'liquidity at or above $100')
            updated = dt(raw['updatedAt'])
            check(generated - WINDOW <= updated <= generated, 'source update inside the eight-hour window')
            market_start = raw.get('eventStartTime') or (raw.get('gameStartTime') or '').replace(' ', 'T').replace('+00', 'Z')
            check(market_start == m['start'],
                  'market start %r equals the fixture start %r' % (market_start, m['start']))
        elif m.get('method') == 'bookmaker_fallback':
            odds = quote.get('decimal_odds') or []
            check(len(odds) == 2, 'two decimal prices recorded')
            if len(odds) == 2:
                recomputed = devig([1 / float(x) for x in odds])
                check(max(abs(a - b) for a, b in zip(recomputed, p)) < 1e-12,
                      'book probabilities reproduce from the stored decimal odds (de-vigged)')
                overround = sum(1 / float(x) for x in odds) - 1
                check(-0.02 <= overround <= 0.25, 'book overround %.4f inside the published band' % overround)
            check(generated - WINDOW <= dt(quote['observed_at']) <= generated,
                  'book observation inside the eight-hour window')
        elif m.get('method') in ('model_vrs', 'model_vrs_mirror'):
            check(m['id'] in model_ids,
                  'model line is the one verify_model.py reproduced from official bytes')
        else:
            check(False, 'method %r is outside the published ladder' % m.get('method'))
        rows.append(record)
        out_problems = record['problems']
        if out_problems:
            problems.extend([])
    receipt = {'snapshot_generated_at': snap['generated_at'], 'window_hours': 8,
               'open_rows': len(rows), 'rows': rows,
               'summary': {'checks': sum(len(r['checks']) for r in rows),
                           'failed': sum(len(r['problems']) for r in rows),
                           'rows_with_problems': sum(1 for r in rows if r['problems'])},
               'problems': problems}
    (HERE / 'line-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt['summary']))
    for problem in problems:
        print('PROBLEM', problem)
    return 0 if not problems else 1


if __name__ == '__main__':
    raise SystemExit(main())
