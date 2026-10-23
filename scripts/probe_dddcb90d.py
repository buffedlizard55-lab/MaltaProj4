"""Session dddcb90d dated coverage audit and unpriced-row source ladder.

Run on the GitHub runner (the sandbox cannot reach the esports hosts):

    python -m scripts.refresh --output runtime/latest.json
    python -m scripts.quarantine runtime/latest.json || true
    python -m scripts.probe_dddcb90d --snapshot runtime/latest.json \
        --previous data/latest.json --output research/harvest-dddcb90d

What it writes to the output directory:

* ``coverage-audit.json`` / ``coverage-audit.md`` - the fresh three-view
  inventory counts from the refresh's own ``inventory.discover`` parity block,
  the refresh's added/removed ids against the previous committed snapshot, and
  an explicit per-shared-fixture start/lock diff against the committed board
  (this is where a feed-vs-page start change such as fixture 1081149 shows up
  as a dated conflict instead of a silent overwrite).
* ``unpriced-ladder.json`` - for every open row that still carries no
  probability: the row's method, pick, attempts tail, plus this run's direct,
  dated re-reads of the standing ladder sources (HLTV match pages, the
  Polymarket market for the exact pair when one exists, Pinnacle's esports
  league list, and the two EGamersWorld listing URLs parsed through
  ``scripts.books.parse_listing`` so the adapter's own verdict - pair bound,
  placeholder, parse miss - is recorded verbatim).  Nothing here writes a
  price: the ladder output is refusal-or-fact evidence only.

Every fetched body is stored with its SHA-256 so a reviewer can replay the
observation.  The module never guesses a URL: only the Hotspawn/HLTV ids and
the listing URLs already present in the committed receipts are requested.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from datetime import datetime, timezone

from scripts.books import parse_listing
from scripts.core import iso


FIXED_SOURCES = (
    # (key, url) - identity/schedule context for the two blank-% rows.
    ('hltv_1081149', 'https://www.hltv.org/matches/2399499/forze-reload-vs-lfo-10-cct-2026-europe-series-12'),
    ('hltv_1082860', 'https://www.hltv.org/matches/2399890/flyquest-vs-staqued-dfrag-invitational-2026'),
    ('poly_market_1082860', 'https://gamma-api.polymarket.com/markets/6066520'),
    ('poly_events_forze', 'https://gamma-api.polymarket.com/events?slug=cs2-forzer-skr2-2026-10-23'),
    ('pinnacle_leagues', 'https://guest.api.arcadia.pinnacle.com/0.1/sports/12/leagues?all=false'),
    ('pinnacle_cct_s12', 'https://guest.api.arcadia.pinnacle.com/0.1/leagues/237685/matchups'),
    # Known listing URLs straight from the committed rejected_listings (never guessed).
    ('egw_1081149', 'https://egamersworld.com/counterstrike/match/HiXMAaC8L/forze-reload-vs-_04jKZ07_4'),
    ('egw_1082860', 'https://egamersworld.com/counterstrike/match/4kaAQWgKEx/flyquest-vs-staqued-zawJ-Q52S3'),
)

FACT_FIELDS = ('scheduled_start_time', 'lock_time', 'status', 'tier', 'best_of')


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def diff_starts(snapshot, previous):
    """Per shared fixture: committed vs fresh start/lock/status, only differences."""
    prev = {str(m['id']): m for m in previous.get('matches', [])}
    out = []
    for m in snapshot.get('matches', []):
        old = prev.get(str(m['id']))
        if not old:
            continue
        changed = {}
        for field in ('start', 'lock', 'state'):
            if old.get(field) != m.get(field):
                changed[field] = {'previous': old.get(field), 'fresh': m.get(field)}
        if changed:
            out.append({'id': str(m['id']),
                        'teams': m.get('teams') or [old.get('team1'), old.get('team2')],
                        'changed': changed})
    return out


def blank_rows(snapshot):
    rows = []
    for m in snapshot.get('matches', []):
        if m.get('state') != 'open':
            continue
        probs = m.get('probabilities')
        if probs is not None:
            continue
        rows.append({
            'id': str(m.get('id')),
            'teams': m.get('teams'),
            'start': m.get('start'),
            'lock': m.get('lock'),
            'pick': m.get('pick'),
            'method': m.get('method'),
            'reason': m.get('reason'),
            'source_url': m.get('source_url'),
            'attempts_tail': (m.get('attempts') or [])[-6:],
        })
    return rows


def ladder(src, rows, out_dir: Path):
    """Dated direct re-reads of the standing ladder for the blank-% rows."""
    observed_at = iso(datetime.now(timezone.utc))
    receipts = {'observed_at': observed_at, 'sources': {}}
    for key, url in FIXED_SOURCES:
        entry = {'url': url}
        try:
            payload, receipt = src.get(f'session dddcb90d {key}', url,
                                       as_json=url.startswith('https://gamma-api')
                                       or url.startswith('https://guest.api'))
            body = payload if isinstance(payload, str) else json.dumps(payload, sort_keys=True)
            entry.update(status='read', observed_at=receipt['observed_at'],
                         sha256=_sha(body.encode('utf-8')), bytes=len(body))
            if url.endswith('/HiXMAaC8L/forze-reload-vs-_04jKZ07_4') or 'flyquest-vs-staqued' in url:
                # The adapter's own verdict on each known listing page.
                readings = parse_listing(body)
                entry['parse_listing'] = [
                    {k: r.get(k) for k in ('team1', 'team2', 'start', 'odds', 'bound_to_labels')}
                    for r in readings]
            if 'gamma-api.polymarket.com/markets/' in url and isinstance(payload, dict):
                entry['market'] = {k: payload.get(k) for k in (
                    'question', 'sportsMarketType', 'gameStartTime', 'eventStartTime',
                    'bestBid', 'bestAsk', 'spread', 'liquidity', 'outcomePrices',
                    'acceptingOrders', 'active', 'closed', 'updatedAt')}
            if 'pinnacle' in url and isinstance(payload, list):
                names = []
                for item in payload:
                    if isinstance(item, dict):
                        league = (item.get('league') or {}).get('name')
                        parent = item.get('parent') or {}
                        parts = [p.get('name') for p in parent.get('participants') or []]
                        names.append({'league': league, 'participants': parts,
                                      'startTime': item.get('startTime') or parent.get('startTime')})
                entry['items'] = names
            if 'hltv.org/matches/' in url and isinstance(payload, str):
                # A numeric two-way line would contain decimal odds in the betting
                # table; record the raw page hash and the fan-vote percentages only
                # as refused context, never as an input.
                entry['mentions_decimal_odds'] = (' odds ' in payload.lower())
        except Exception as exc:  # a failed read is a dated refusal, not a crash
            entry.update(status='error', error=f'{type(exc).__name__}: {exc}')
        receipts['sources'][key] = entry
    envelope = dict(receipts)
    envelope['rows'] = rows
    (out_dir / 'unpriced-ladder.json').write_text(
        json.dumps(envelope, indent=1, ensure_ascii=False) + '\n')
    return receipts


def audit(snapshot, previous, out_dir: Path):
    observed = iso(datetime.now(timezone.utc))
    prev_ids = {str(m['id']) for m in previous.get('matches', [])}
    fresh_ids = {str(m['id']) for m in snapshot.get('matches', [])}
    report = {
        'observed_at': observed,
        'snapshot_generated_at': snapshot.get('generated_at'),
        'previous_generated_at': previous.get('generated_at'),
        'coverage_counts_fresh': snapshot.get('coverage_counts'),
        'coverage_counts_previous': previous.get('coverage_counts'),
        'coverage_flag_fresh': snapshot.get('coverage'),
        'issues_fresh': snapshot.get('issues'),
        'inventory_changes_fresh': snapshot.get('inventory_changes'),
        'added_vs_committed': sorted(fresh_ids - prev_ids),
        'removed_vs_committed': sorted(prev_ids - fresh_ids),
        'fixture_conflicts_fresh': snapshot.get('fixture_conflicts'),
        'start_or_lock_diffs_vs_committed': diff_starts(snapshot, previous),
        'blank_percentage_open_rows': blank_rows(snapshot),
    }
    (out_dir / 'coverage-audit.json').write_text(
        json.dumps(report, indent=1, ensure_ascii=False) + '\n')

    lines = [
        '# Coverage audit (session dddcb90d, runner-dated)',
        '',
        f'- observed: {observed}',
        f'- fresh snapshot generated: {snapshot.get("generated_at")}',
        f'- committed snapshot generated: {previous.get("generated_at")}',
        f'- fresh coverage counts: {json.dumps(snapshot.get("coverage_counts"))}',
        f'- committed coverage counts: {json.dumps(previous.get("coverage_counts"))}',
        f'- fresh inventory changes: {json.dumps(snapshot.get("inventory_changes"))}',
        f'- added vs committed: {report["added_vs_committed"] or "none"}',
        f'- removed vs committed: {report["removed_vs_committed"] or "none"}',
        f'- fixture conflicts (fresh): {json.dumps(report["fixture_conflicts_fresh"])}',
        '',
        '## Start/lock differences against the committed board',
        '',
    ]
    if report['start_or_lock_diffs_vs_committed']:
        for d in report['start_or_lock_diffs_vs_committed']:
            lines.append(f'- {d["id"]} {" vs ".join(d["teams"])}: {json.dumps(d["changed"])}')
    else:
        lines.append('- none')
    lines += ['', '## Open rows without a percentage (fresh)', '']
    for r in report['blank_percentage_open_rows']:
        lines.append(f'- {r["id"]} {" vs ".join(r["teams"] or [])} start={r["start"]} '
                     f'method={r["method"]} pick={r["pick"]}')
    (out_dir / 'coverage-audit.md').write_text('\n'.join(lines) + '\n')
    return report


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', required=True)
    parser.add_argument('--previous', default='data/latest.json')
    parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)

    from scripts.refresh import Sources
    snapshot = json.loads(Path(args.snapshot).read_text())
    previous = json.loads(Path(args.previous).read_text())
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    report = audit(snapshot, previous, out_dir)
    rows = report['blank_percentage_open_rows']
    src = Sources(datetime.now(timezone.utc))
    receipts = ladder(src, rows, out_dir)
    (out_dir / 'refresh-snapshot.json').write_text(json.dumps(snapshot, indent=1) + '\n')

    print(json.dumps({
        'coverage_fresh': report['coverage_counts_fresh'],
        'added': len(report['added_vs_committed']),
        'removed': len(report['removed_vs_committed']),
        'start_diffs': len(report['start_or_lock_diffs_vs_committed']),
        'blank_rows': len(rows),
        'ladder_reads': {k: v.get('status') for k, v in receipts['sources'].items()},
    }, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
