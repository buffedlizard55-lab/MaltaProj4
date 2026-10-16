"""Session dedd2e34's research harvest: no value is edited, only re-derived.

Why this exists: the authoring sandbox reaches GitHub and package registries
only, so the real refresh and the independent auditors must run on an Actions
runner. This script copies exactly what those steps produced, recomputes every
count from the snapshot itself (never from a hand-typed number), and records a
SHA-256 digest per file so each figure quoted in COORDINATION.md or on the site
can be re-checked line by line.

It never publishes, never invents a probability, and never modifies a row.
Extra outputs over a plain harvest:

* ``market-ledger.json`` - one entry per open fixture with the raw external
  inputs the published percentage came from (provider, market id, bid/ask,
  liquidity, observation and update stamps, expiry deadline) so a reader can
  recompute the devigged probability by hand.
* ``book-probe.json`` - read-only accessibility probe of the esportsbook
  endpoints this project would need to widen market coverage for low-tier
  fixtures. Statuses are recorded exactly as returned; nothing is retried
  against an access restriction and no result is treated as a price.
"""
import argparse
import collections
import datetime
import hashlib
import json
import math
import pathlib
import shutil
import sys

FIELDS = ('id', 'teams', 'competition', 'tier', 'best_of', 'start', 'lock', 'state',
          'probabilities', 'fair_odds', 'pick', 'method', 'reason', 'flags', 'source_url',
          'feed_url', 'expires_at', 'resolution_blocked')


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def recompute(quote):
    """Re-derive the devigged probability from the raw quote, if it is present.

    Returns None whenever the inputs needed for the arithmetic are absent, so a
    missing value is reported as missing rather than quietly assumed.
    """
    prices = quote.get('prices') or (quote.get('raw') or {}).get('outcomePrices')
    if prices:
        try:
            values = [float(p) for p in prices]
        except (TypeError, ValueError):
            return None
        if len(values) != 2 or not all(math.isfinite(v) and v > 0 for v in values):
            return None
        total = sum(values)
        return [v / total for v in values]
    line = quote.get('raw') or {}
    american = [p.get('price') for p in (line.get('prices') or [])]
    if len([a for a in american if isinstance(a, (int, float))]) == 2:
        decimals = []
        for value in american:
            value = float(value)
            if not math.isfinite(value) or abs(value) < 100:
                return None
            decimals.append(1 + (value / 100 if value > 0 else 100 / -value))
        implied = [1 / d for d in decimals]
        total = sum(implied)
        return [v / total for v in implied]
    return None


def summarise(snapshot, run_id, branch):
    matches = snapshot.get('matches') or []
    opens = [m for m in matches if m.get('state') == 'open']
    priced = [m for m in opens if m.get('probabilities')]
    model = [m for m in opens if m.get('method') == 'model_vrs']
    research_only = [m for m in opens if m.get('pick') and not m.get('probabilities')]
    no_pick = [m for m in opens if not m.get('pick')]
    rows = [{k: m.get(k) for k in FIELDS} for m in sorted(
        opens, key=lambda r: (r.get('start') or '', r.get('id') or ''))]
    ledger = []
    for m in opens:
        for quote in (m.get('evidence') or []):
            recomputed = recompute(quote)
            published = m.get('probabilities')
            ledger.append({
                'fixture_id': m.get('id'),
                'teams': m.get('teams'),
                'provider': quote.get('provider'),
                'market_id': quote.get('id'),
                'url': quote.get('url'),
                'api_url': quote.get('api_url'),
                'observed_at': quote.get('observed_at'),
                'updated_at': quote.get('updated_at'),
                'prices': quote.get('prices'),
                'best_bid': (quote.get('raw') or {}).get('bestBid'),
                'best_ask': (quote.get('raw') or {}).get('bestAsk'),
                'liquidity': (quote.get('raw') or {}).get('liquidity'),
                'volume': (quote.get('raw') or {}).get('volume'),
                'tier': quote.get('tier'),
                'spread': (quote.get('spread') if quote.get('spread') is not None
                           else ((float(quote['raw']['bestAsk']) - float(quote['raw']['bestBid']))
                                 if (quote.get('raw') or {}).get('bestAsk') is not None
                                 and (quote.get('raw') or {}).get('bestBid') is not None else None)),
                'expires_at': m.get('expires_at'),
                'published_probabilities': published,
                'recomputed_probabilities': recomputed,
                # A published row with no recomputable raw pair is reported, not hidden.
                'replay': (None if recomputed is None or published is None else
                           all(abs(a - b) <= 1e-9 for a, b in zip(recomputed, published))),
            })
    summary = {
        'run_id': run_id,
        'branch': branch,
        'harvested_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
        'snapshot': {
            'generated_at': snapshot.get('generated_at'),
            'last_attempt_at': snapshot.get('last_attempt_at'),
            'refresh_started_at': snapshot.get('refresh_started_at'),
            'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
            'coverage': snapshot.get('coverage'),
            'refresh_hours': snapshot.get('refresh_hours'),
            'stale_after_hours': snapshot.get('stale_after_hours'),
            'rows_total': len(matches),
            'rows_open': len(opens),
            'rows_open_with_market_prices': len([m for m in priced if str(m.get('method')).startswith('exchange')
                                                or m.get('method') == 'bookmaker_fallback']),
            'rows_open_with_model_prices': len(model),
            'rows_open_with_prices': len(priced),
            'rows_open_with_pick_no_price': len(research_only),
            'rows_open_without_pick': len(no_pick),
            'open_pick_methods': {str(k): v for k, v in
                                  collections.Counter(m.get('method') for m in opens).items()},
            'unresolved_open_ids': [m.get('id') for m in no_pick],
            'research_only_ids': [m.get('id') for m in research_only],
            'open_rows': rows,
            'issues': snapshot.get('issues'),
            'coverage_counts': snapshot.get('coverage_counts'),
            'inventory_changes': snapshot.get('inventory_changes'),
            'source_checks': snapshot.get('source_checks'),
        },
        'market_ledger': ledger,
    }
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', default='runtime/latest.json')
    parser.add_argument('--output', default='research/harvest-dedd2e34')
    parser.add_argument('--run-id', type=int, default=None)
    parser.add_argument('--branch', default=None)
    parser.add_argument('--book-probe', default='runtime/book-probe.json')
    parser.add_argument('--coverage-gap', default='runtime/coverage-gap.json')
    args = parser.parse_args()

    out = pathlib.Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    runtime = pathlib.Path(args.runtime)
    if not runtime.exists():
        print('No refreshed snapshot at %s; nothing to harvest.' % runtime, file=sys.stderr)
        return 2
    snapshot = json.loads(runtime.read_text())
    summary = summarise(snapshot, args.run_id, args.branch)
    (out / 'latest.json').write_text(json.dumps(snapshot, indent=1, sort_keys=True) + '\n')
    (out / 'market-ledger.json').write_text(json.dumps(summary['market_ledger'], indent=1, sort_keys=True) + '\n')
    for name in ('row-audit.md', 'published-row-audit.md', 'coverage-gap.md', 'book-probe.json',
                 'coverage-gap.json'):
        for base in (pathlib.Path('runtime'), pathlib.Path(args.runtime).parent):
            src = base / name
            if src.exists():
                shutil.copyfile(src, out / name)
                break
    for name in ('refresh.txt', 'row-audit.txt', 'build.txt', 'validate.txt',
                 'coverage-gap.txt', 'book-probe.txt'):
        src = out / 'logs' / name
        if src.exists():
            shutil.copyfile(src, out / ('log-' + name))
    summary['files'] = {p.name: digest(p) for p in sorted(out.iterdir())
                        if p.is_file() and p.name != 'harvest-summary.json'}
    (out / 'harvest-summary.json').write_text(json.dumps(summary, indent=1, sort_keys=True) + '\n')
    head = {k: v for k, v in summary['snapshot'].items()
            if k not in ('open_rows', 'source_checks', 'inventory_changes')}
    head['ledger_rows'] = len(summary['market_ledger'])
    head['ledger_replay_mismatch'] = sum(1 for x in summary['market_ledger'] if x['replay'] is False)
    head['ledger_unrecomputable'] = sum(1 for x in summary['market_ledger'] if x['replay'] is None)
    print(json.dumps(head, indent=1, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
