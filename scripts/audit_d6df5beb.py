"""Independent audit for session d6df5beb (no network access).

Replays the dated receipt in ``research/session-d6df5beb/receipt-2026-10-18.json``:

* every one of the twelve completed TWC 2026 series must be internally consistent
  (series score, map winners, map count against the best-of);
* every venue quote must clear the same two-sided quality gate the production
  collector applies to exchange rows (prices sum to 1, spread <= 25 points,
  liquidity >= $100) and must name the same UTC start as HLTV;
* the Thunderpick de-vig must reproduce the published arithmetic;
* the two venues must agree on the favourite and be compared, not blended;
* the published data files must still agree with the receipt, and every open
  Hotspawn row must carry a pick (with a reason when no probability exists).

The script never fetches a source: a stale price cannot be silently renewed by
running it. Exit code 1 means a hard failure; INFO lines are findings for review.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RECEIPT = ROOT / 'research' / 'session-d6df5beb' / 'receipt-2026-10-18.json'
TOLERANCE = 1e-6


# --------------------------------------------------------------------------- #
# arithmetic
# --------------------------------------------------------------------------- #
def decimal_from_american(price: int) -> float:
    if price == 0:
        raise ValueError('American price cannot be zero')
    return 1 + (price / 100 if price > 0 else 100 / abs(price))


def implied_from_american(price: int) -> float:
    if price == 0:
        raise ValueError('American price cannot be zero')
    return 100 / (price + 100) if price > 0 else abs(price) / (abs(price) + 100)


def devig_american(prices: dict[str, int]) -> dict:
    """Two-way de-vig by proportional normalisation (the project's method)."""
    teams = list(prices)
    if len(teams) != 2:
        raise ValueError('de-vig needs exactly two prices')
    a, b = teams
    raw = {a: implied_from_american(prices[a]), b: implied_from_american(prices[b])}
    overround = raw[a] + raw[b]
    if not overround > 1:
        raise ValueError('two-way book cannot have an overround at or below 1')
    probs = {a: raw[a] / overround, b: raw[b] / overround}
    return {
        'decimal': {a: decimal_from_american(prices[a]), b: decimal_from_american(prices[b])},
        'raw_implied': raw,
        'overround': overround,
        'probabilities': probs,
        'fair_decimal': {a: 1 / probs[a], b: 1 / probs[b]},
    }


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #
class Audit:
    def __init__(self):
        self.rows: list[tuple[str, str, str]] = []

    def check(self, ok: bool, label: str, detail: str = '') -> bool:
        self.rows.append(('PASS' if ok else 'FAIL', label, detail))
        return ok

    def info(self, label: str, detail: str = '') -> None:
        self.rows.append(('INFO', label, detail))

    @property
    def failures(self) -> list[tuple[str, str, str]]:
        return [r for r in self.rows if r[0] == 'FAIL']


def audit_receipt(receipt: dict, audit: Audit) -> dict:
    series = receipt['series']
    audit.check(len(series) == 12, 'twelve completed series in receipt', f'found {len(series)}')

    by_day: dict[int, int] = {}
    totals = {'maps': 0}
    for s in series:
        tag = f"day {s['day']} {s['winner']} {s['score']} {s['loser']}"
        by_day[s['day']] = by_day.get(s['day'], 0) + 1
        wins = s['score'].split('-')
        w, l = int(wins[0]), int(wins[1])
        ok_score = (w == 2 and l in (0, 1))
        audit.check(ok_score, f'{tag}: legal best-of-three series score', s['score'])
        # map winners must match the series score
        mw = sum(1 for m in s['maps'] if m['winner'] == s['winner'])
        ml = sum(1 for m in s['maps'] if m['winner'] == s['loser'])
        audit.check(mw == w and ml == l, f'{tag}: map winners match the series score',
                    f'winner maps {mw}, loser maps {ml}')
        played = [m for m in s['maps'] if not m.get('not_played')]
        audit.check(len(played) == w + l, f'{tag}: one map entry per played map',
                    f'{len(played)} entries for {w + l} maps')
        audit.check(len(s['maps']) <= s['best_of'], f'{tag}: maps fit the best-of',
                    f"{len(s['maps'])} <= {s['best_of']}")
        for m in played:
            a, b = (int(x) for x in m['score'].split('-'))
            winner_side = max(a, b)
            if not m.get('overtime'):
                audit.check(winner_side == 13 and min(a, b) <= 11,
                            f'{tag}: {m["map"]} is a regulation 13-round result', m['score'])
            else:
                audit.check(winner_side >= 16 and winner_side - min(a, b) >= 2,
                            f'{tag}: {m["map"]} is a legal overtime result', m['score'])
        if not s['match_url'].startswith('https://www.hltv.org/matches/'):
            audit.check(False, f'{tag}: primary source is an HLTV match page', s['match_url'])
        totals['maps'] += len(played)

    audit.check(by_day.get(1) == 4 and by_day.get(2) == 4 and by_day.get(3) == 2 and by_day.get(4) == 2,
                'day distribution 4/4/2/2', str(by_day))
    audit.check(totals['maps'] == 29, 'twenty-nine maps played across the event', str(totals['maps']))
    return {'series': len(series), 'maps': totals['maps'], 'by_day': by_day}


def audit_fixtures(receipt: dict, audit: Audit) -> dict:
    out = {}
    for fx in receipt['fixtures']:
        a, b = fx['team_a'], fx['team_b']
        audit.check(fx['start_utc'].startswith('2026-10-18T'),
                    f'{a}-{b}: Sunday start', fx['start_utc'])
        audit.check(fx['best_of'] in (3, 5), f'{a}-{b}: best-of is 3 or 5', str(fx['best_of']))
        venues = fx['venue_quotes']
        audit.check(len({v['venue'] for v in venues}) == 2,
                    f'{a}-{b}: two independent venues', ','.join(v['venue'] for v in venues))
        polly = next(v for v in venues if v['venue'] == 'Polymarket')
        tp = next(v for v in venues if v['venue'] == 'Thunderpick')

        # exchange gate, identical thresholds to scripts/core.py
        total = sum(polly['prices'].values())
        audit.check(abs(total - 1.0) <= TOLERANCE,
                    f'{a}-{b}: Polymarket two-sided prices sum to 1.000', f'{total:.6f}')
        audit.check(polly['spread'] <= .25 + 1e-9,
                    f'{a}-{b}: Polymarket spread inside the 25-point gate', str(polly['spread']))
        audit.check(polly['liquidity_usd'] >= 100,
                    f'{a}-{b}: Polymarket liquidity above $100', f"${polly['liquidity_usd']:,.2f}")
        audit.check(polly['closed'] is False and polly['accepting_orders'] is True,
                    f'{a}-{b}: Polymarket market open and accepting orders')
        audit.check(polly['game_start_time_utc'] == fx['start_utc'],
                    f'{a}-{b}: Polymarket start matches HLTV', polly['game_start_time_utc'])
        bid, ask = polly['best_bid'], polly['best_ask']
        audit.check(0 < bid < ask < 1, f'{a}-{b}: Polymarket bid/ask ordered', f'{bid}/{ask}')
        # the quote must be two-sided around the published price
        audit.check(bid < polly['prices'][a] <= ask or bid <= polly['prices'][a] < ask,
                    f'{a}-{b}: published price sits inside the quote', str(polly['prices'][a]))

        devig = devig_american(tp['american'])
        polly_probs = dict(polly['prices'])
        gap = {t: abs(devig['probabilities'][t] - polly_probs[t]) for t in (a, b)}
        favourite_tp = max(devig['probabilities'], key=devig['probabilities'].get)
        favourite_polly = max(polly_probs, key=polly_probs.get)
        audit.check(favourite_tp == favourite_polly,
                    f'{a}-{b}: both venues agree on the favourite', f'{favourite_tp}')
        audit.check(max(gap.values()) <= .05,
                    f'{a}-{b}: venue de-vig gap within 5 points',
                    ', '.join(f'{t} {gap[t] * 100:.2f}pt' for t in (a, b)))
        audit.check(1.0 < devig['overround'] <= 1.15,
                    f'{a}-{b}: Thunderpick overround inside the 15% gate',
                    f"{devig['overround']:.4f}")
        out[f'{a}-{b}'] = {
            'thunderpick_devig': {t: round(devig['probabilities'][t], 6) for t in (a, b)},
            'thunderpick_overround': round(devig['overround'], 6),
            'polymarket': polly_probs,
            'gap_points': {t: round(gap[t] * 100, 2) for t in (a, b)},
            'pick': favourite_polly,
            'start_utc': fx['start_utc'],
            'venue_updated_at': polly['updated_at_utc'],
        }
    return out


def audit_published_data(receipt: dict, audit: Audit, latest_path: Path | None = None) -> dict:
    analysis = json.loads((ROOT / 'data' / 'analysis.json').read_text())
    latest = json.loads((latest_path or (ROOT / 'data' / 'latest.json')).read_text())
    out: dict = {}

    published = {}
    for key in ('day_one', 'day_two', 'day_three_results', 'day_four_results'):
        block = analysis.get(key) or {}
        for m in block.get('matches') or []:
            published[(m['winner'], m['loser'])] = m.get('score')
    for s in receipt['series']:
        key = (s['winner'], s['loser'])
        got = published.get(key)
        audit.check(got == s['score'], f'published result {key[0]} {s["score"]} {key[1]}',
                    'absent or different: %r' % (got,))
    audit.check(len(published) == 12, 'twelve series published on the analysis page', str(len(published)))

    # blank map scores that are now verifiable
    blank = [(k, v) for k, v in published.items() if not v]
    audit.check(not blank, 'no published series score left blank', str(blank))
    blanks = []
    for key, block in (('day_one', analysis.get('day_one')),):
        for m in (block or {}).get('matches') or []:
            if not m.get('maps'):
                blanks.append(f"{m['winner']}-{m['loser']}")
    if blanks:
        audit.info('map scores still blank on the site but verified in this receipt',
                   ', '.join(blanks))
    out['published_series'] = len(published)

    guide = analysis.get('day_five_guidance') or {}
    cards = {tuple(c.get('teams') or []): c for c in guide.get('not_listed') or []}
    for fx in receipt['fixtures']:
        key = (fx['team_a'], fx['team_b'])
        card = cards.get(key) or cards.get((fx['team_b'], fx['team_a']))
        audit.check(card is not None, f"Day-5 card exists for {key[0]}-{key[1]}")
        if not card:
            continue
        audit.check(card.get('pick') in key, f"Day-5 card pick is one of the two teams ({key[0]}-{key[1]})",
                    str(card.get('pick')))
        audit.check(bool(card.get('market')), f"Day-5 card carries a dated market block ({key[0]}-{key[1]})")
        audit.check(card.get('start_utc') == fx['start_utc'],
                    f"Day-5 card start matches the fixture ({key[0]}-{key[1]})",
                    str(card.get('start_utc')))

    open_rows = [m for m in latest.get('matches', []) if m.get('state') == 'open']
    audit.check(bool(open_rows), 'snapshot has open rows', str(len(open_rows)))
    methods: dict[str, int] = {}
    for row in open_rows:
        rid = row.get('id')
        audit.check(bool(row.get('pick')), f'row {rid} has a pick', str(row.get('pick')))
        audit.check(row.get('pick') in (row.get('teams') or []), f'row {rid} pick is one of its teams',
                    str(row.get('pick')))
        audit.check(bool(row.get('reason') or row.get('probabilities')),
                    f'row {rid} has a probability or a documented reason')
        probs = row.get('probabilities')
        if probs is not None:
            audit.check(len(probs) == 2 and abs(sum(probs) - 1) <= 1e-6,
                        f'row {rid} two-way probability sums to 1', str(sum(probs)))
            audit.check(bool(row.get('expires_at')), f'row {rid} probability carries an expiry')
        methods[row.get('method') or 'none'] = methods.get(row.get('method') or 'none', 0) + 1
    mains = [m for m in latest.get('matches', [])
             if m.get('competition') == 'Thunderpick World Championship 2026']
    audit.check(not mains, 'main TWC event is absent from the Hotspawn snapshot (research-only Day 5)',
                f'{len(mains)} rows')
    out.update({'open_rows': len(open_rows), 'methods': methods,
                'priced_rows': sum(1 for r in open_rows if r.get('probabilities')),
                'research_only': sum(1 for r in open_rows if not r.get('probabilities'))})
    return out


def audit_rendered(audit: Audit) -> dict:
    out = {}
    for page, needles in (
        ('analysis.html', ('day-five-guidance',)),
        ('picks.html', ('Open matches', 'All matches')),
        ('unresolved.html', ('Unresolved',)),
        ('index.html', ('picks.html',)),
    ):
        path = ROOT / page
        ok = path.exists() and path.stat().st_size > 1000
        audit.check(ok, f'{page} is rendered', f'{path.stat().st_size if path.exists() else 0} bytes')
        if ok:
            text = path.read_text(errors='ignore')
            for needle in needles:
                audit.check(needle in text, f'{page} contains {needle!r}')
        out[page] = ok
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--receipt', type=Path, default=DEFAULT_RECEIPT)
    ap.add_argument('--data', type=Path, help='audit a different latest.json (e.g. the live snapshot)')
    ap.add_argument('--output', type=Path)
    args = ap.parse_args(argv)

    receipt = json.loads(args.receipt.read_text())
    audit = Audit()
    summary = audit_receipt(receipt, audit)
    summary['fixtures'] = audit_fixtures(receipt, audit)
    summary.update(audit_published_data(receipt, audit, args.data))
    summary['rendered'] = audit_rendered(audit)

    lines = ['# Session d6df5beb independent audit', '',
             f"Receipt: `{args.receipt.relative_to(ROOT)}`  ",
             f"Receipt observation window: {receipt['observed_window_utc']}", '',
             f"Series: {summary['series']} · maps: {summary['maps']} · by day: {summary['by_day']}", '',
             '| Result | Check | Detail |', '| --- | --- | --- |']
    lines += [f'| {status} | {label} | {detail} |' for status, label, detail in audit.rows]
    lines += ['', '## Day-5 two-venue comparison', '',
              '| Fixture | Start (UTC) | Thunderpick de-vig | Polymarket | Gap (points) | Pick |',
              '| --- | --- | --- | --- | --- | --- |']
    for name, fx in summary['fixtures'].items():
        tp = fx['thunderpick_devig']
        pm = fx['polymarket']
        gap = fx['gap_points']
        tp_txt = ' / '.join(f'{t} {p * 100:.2f}%' for t, p in tp.items())
        pm_txt = ' / '.join(f'{t} {p * 100:.1f}%' for t, p in pm.items())
        gap_txt = ' / '.join(f'{g:.2f}' for g in gap.values())
        lines.append(f"| {name} | {fx['start_utc']} | {tp_txt} | {pm_txt} | {gap_txt} | {fx['pick']} |")
    lines += ['', '## Open Hotspawn rows', '',
              f"Open rows: {summary['open_rows']} · priced: {summary['priced_rows']} · "
              f"research-only (blank percentage, documented reason): {summary['research_only']}", '',
              'Methods: ' + ', '.join(f'{k} {v}' for k, v in sorted(summary['methods'].items())), '',
              f"**Failures: {len(audit.failures)}**"]
    report = '\n'.join(lines) + '\n'

    if args.output:
        args.output.write_text(report)
        print(f'wrote {args.output}')
    else:
        print(report)
    return 1 if audit.failures else 0


if __name__ == '__main__':
    sys.exit(main())
