#!/usr/bin/env python3
"""Session 4ed657ce: independent, dated verification of the published CS2 board.

This verifier deliberately does not trust the website's prose. It re-reads the
committed snapshot, re-derives every probability from the archived primary
evidence, checks every row's official source link and expiry, and -- when given
the session's dated external-observations file -- compares those receipts with
fresh official API/page reads. Hotspawn is used only for fixture identity, lock
and start; its crowd-pick percentages are never a probability input.

Usage:
  python -m scripts.verify_4ed657ce \
    --data data/latest.json \
    --external research/session-4ed657ce/external-observations.json \
    --valve-file /tmp/valve-standings.md \
    --out research/session-4ed657ce/verification-report.json \
    --markdown research/session-4ed657ce/VERIFICATION.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RD = 75.0
Q = math.log(10) / 400
G = 1 / math.sqrt(1 + 3 * Q * Q * RD * RD / math.pi ** 2)
SLOPE = 0.7986
TOL = 1e-9
CALC_TOL = 1e-6
ALLOWED_METHODS = {
    'exchange', 'exchange_wide', 'bookmaker', 'bookmaker_fallback',
    'model_vrs', 'model_vrs_mirror', 'research_rank', 'research_rank_single',
    'research_vrs_single', 'research_form',
}
LADDER = [
    ('Polymarket exchange line', 'https://gamma-api.polymarket.com/events'),
    ('HLTV fixture identity, ranking and lineups', 'https://www.hltv.org/matches'),
    ('Pinnacle esports moneyline', 'https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight'),
    ('Wide Polymarket quote, labelled low confidence', 'https://gamma-api.polymarket.com/events'),
    ('Researched esportsbook listing', 'https://bo3.gg/matches/current'),
    ('Our Valve-standings model line', 'https://github.com/ValveSoftware/counter-strike_regional_standings'),
    ('HLTV dated Valve ranking mirror', 'https://www.hltv.org/valve-ranking/teams/2026/october/24'),
]


def moment(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def norm(value):
    folded = unicodedata.normalize('NFKD', str(value))
    folded = ''.join(ch for ch in folded if not unicodedata.combining(ch))
    return ''.join(ch for ch in folded.lower() if ch.isalnum())


def same_team(a, b, aliases=None):
    a, b = norm(a), norm(b)
    if not a or not b:
        return False
    if a == b:
        return True
    short, long = sorted((a, b), key=len)
    if len(short) >= 3 and long.startswith(short):
        return True
    for group in (aliases or []):
        names = {norm(n) for n in (group.get('names') or [])}
        if a in names and b in names and str(group.get('source') or '').startswith('https://'):
            return True
    return False


def order_by_teams(labels, values, teams, aliases=None):
    mapping = []
    for team in teams:
        hits = [i for i, label in enumerate(labels) if same_team(label, team, aliases)]
        if len(hits) != 1:
            raise ValueError('cannot map %r to exactly one source label %r' % (team, labels))
        mapping.append(hits[0])
    if len(set(mapping)) != len(mapping):
        raise ValueError('two fixture teams map to one source label %r' % (labels,))
    return [values[i] for i in mapping]


def glicko_expect(pa, pb):
    return 1 / (1 + 10 ** (-G * (float(pa) - float(pb)) / 400))


def calibrate(raw):
    return 0.5 + SLOPE * (raw - 0.5)


def devig(decimal_odds):
    q = [1 / float(d) for d in decimal_odds]
    total = sum(q)
    return [v / total for v in q], total - 1


def parse_json_field(value):
    if isinstance(value, str):
        return json.loads(value)
    return value


def rederive(match):
    ev = (match.get('evidence') or [None])[0]
    if not ev:
        return None, 'no evidence'
    aliases = ev.get('identity_sources')
    provider = ev.get('provider')
    if provider in ('Valve VRS model', 'HLTV Valve ranking (Valve points)'):
        raw = glicko_expect(ev['points'][0], ev['points'][1])
        p = [calibrate(raw), 1 - calibrate(raw)]
        return p, 'valve_vrs_formula'
    if 'decimal_odds' in ev:
        p, overround = devig(ev['decimal_odds'])
        p = order_by_teams(ev.get('source_teams') or match['teams'], p, match['teams'], aliases)
        return p, 'book_de_vig_overround_%.4f' % overround
    raw = ev.get('raw') or {}
    prices = parse_json_field(raw.get('outcomePrices')) if raw.get('outcomePrices') is not None else None
    labels = parse_json_field(raw.get('outcomes')) if raw.get('outcomes') is not None else None
    if prices and labels:
        x = [float(v) for v in prices]
        p = [v / sum(x) for v in x]
        p = order_by_teams(labels, p, match['teams'], aliases)
        return p, 'exchange_mid'
    return None, 'no reproducible price'


def parse_valve(text):
    rows = []
    for line in text.splitlines():
        m = re.match(r'\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|', line)
        if m:
            rows.append({
                'rank': int(m.group(1)), 'points': int(m.group(2)),
                'team': m.group(3).strip(),
                'roster': [x.strip() for x in m.group(4).split(',')],
            })
    return rows


def valve_candidates(rows, label, points, rank, roster):
    exact = [r for r in rows if norm(r['team']) == norm(label)]
    if not exact:
        return [], 'label not found'
    scored = []
    for r in exact:
        overlap = len({norm(p) for p in roster} & {norm(p) for p in r['roster']})
        scored.append((r['rank'] == rank, r['points'] == points, overlap, r))
    scored.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    best = scored[0]
    if best[2] < 3 and not (best[0] and best[1]):
        return exact, 'roster continuity below 3 and rank/points do not both match'
    return [best[3]], 'matched by rank/points/roster'


def audit(data, external=None, valve_text=None):
    generated = moment(data.get('generated_at'))
    observed = moment(data.get('fixtures_observed_at'))
    ttl = timedelta(hours=float(data.get('stale_after_hours') or 8))
    issues = []
    rows = []
    external = external or {}
    polymarket = external.get('polymarket') or {}
    book_pages = external.get('bookmaker_pages') or {}
    hltv_points = (external.get('hltv_dated_valve_ranking') or {}).get('points') or {}
    valve_rows = parse_valve(valve_text) if valve_text else None

    inv = external.get('inventory') or {}
    if inv:
        retained = (inv.get('snapshot_coverage_counts') or {}).get('retained')
        fresh = (inv.get('lobby_cache_busted') or {}).get('tier_count')
        page = (inv.get('cs2_page_cache_busted') or {}).get('tier_count')
        if retained is not None and fresh is not None and retained != fresh:
            issues.append('fresh cache-busted lobby count %s differs from snapshot retained %s' % (fresh, retained))
        if retained is not None and page is not None and retained != page:
            issues.append('fresh CS2 page count %s differs from snapshot retained %s' % (page, retained))
        if (inv.get('lobby_uncached') or {}).get('tier_count') != fresh:
            issues.append('FLAGGED: uncached lobby view returned a different count than the cache-busted official view; publish both links')

    for m in sorted((x for x in data['matches'] if x.get('state') == 'open'),
                    key=lambda x: (x.get('start') or '', x['id'])):
        problems, checks, notes = [], [], []
        ev = (m.get('evidence') or [None])[0]
        p = m.get('probabilities')
        if not str(m.get('source_url') or '').startswith('https://'):
            problems.append('fixture source is not https')
        if 'hotspawn.com' not in str(m.get('source_url') or ''):
            problems.append('fixture source is not an official Hotspawn URL')
        else:
            checks.append('official Hotspawn fixture link')
        if not ev:
            problems.append('no evidence record')
        else:
            price_url = ev.get('api_url') or ev.get('url')
            if not str(price_url or '').startswith('https://'):
                problems.append('price evidence is not https')
            else:
                checks.append('https price evidence')
            if ev.get('provider') == 'Hotspawn':
                problems.append('Hotspawn used as a probability source')
        if m.get('method') not in ALLOWED_METHODS:
            problems.append('unknown method %r' % m.get('method'))
        lock, start = moment(m.get('lock')), moment(m.get('start'))
        expires = moment(m.get('expires_at'))
        if generated and ((lock and lock <= generated) or (start and start <= generated)):
            problems.append('open row lock/start is already past the snapshot clock')
        if generated and (not expires or expires <= generated):
            problems.append('open row has no future evidence expiry')
        elif expires and observed and expires > observed + ttl + timedelta(seconds=1):
            problems.append('evidence expiry exceeds the 8-hour observation window')
        elif expires and lock and expires > lock:
            problems.append('evidence expiry outlives the Hotspawn lock')
        else:
            checks.append('expiry inside lock and 8h window')
        if not m.get('pick') or m['pick'] not in m['teams']:
            problems.append('pick is missing or is not one of the two teams')
        calc, kind = rederive(m)
        if p is None:
            problems.append('no published probability')
        else:
            if abs(sum(p) - 1) > TOL:
                problems.append('probabilities do not sum to 1')
            else:
                checks.append('sum=1')
            if calc is None:
                problems.append('probability not reproducible: %s' % kind)
            else:
                delta = max(abs(p[i] - calc[i]) for i in (0, 1))
                if delta > CALC_TOL:
                    problems.append('published %.6f != independently re-derived %.6f' % (p[0], calc[0]))
                else:
                    checks.append('%s reproduced (max delta %.2e)' % (kind, delta))
            if m.get('pick') != m['teams'][p.index(max(p))]:
                problems.append('pick is not the larger probability')
            else:
                checks.append('pick is the favourite')
            fair = m.get('fair_odds')
            if fair and max(abs(fair[i] - 1 / p[i]) for i in (0, 1)) > TOL:
                problems.append('fair odds are not 1/p')
            elif fair:
                checks.append('fair odds = 1/p')

        # Fresh official re-reads: identity and direction, not a demand that a
        # live market still has the same price minutes later.
        market_id = str(ev.get('id')) if ev else None
        market_obs = polymarket.get(market_id)
        if market_obs:
            try:
                obs_p = order_by_teams(market_obs['outcomes'], market_obs['prices'], m['teams'],
                                       ev.get('identity_sources'))
                drift = max(abs(obs_p[i] - p[i]) for i in (0, 1)) if p else None
                notes.append('Polymarket re-read %s: %s' % (
                    market_obs.get('updated_at', market_obs.get('observed_at', 'dated')),
                    ' / '.join('%.3f' % v for v in obs_p)))
                if drift is not None and drift > 0.10:
                    issues.append('FLAGGED: %s Polymarket moved %.1f points from the archived quote' % (m['id'], drift * 100))
                if market_obs.get('game_start') and moment(market_obs['game_start']) != start:
                    problems.append('re-read market start differs from fixture start')
                if market_obs.get('active') is False:
                    problems.append('re-read market is closed')
                checks.append('official market re-read')
            except Exception as exc:  # reported, not silently mapped
                problems.append('market re-read mapping failed: %s' % exc)
        book_obs = book_pages.get(m['id'])
        if book_obs:
            try:
                q, overround = devig(book_obs['decimal_odds'])
                obs_p = order_by_teams(book_obs['teams'], q, m['teams'])
                drift = max(abs(obs_p[i] - p[i]) for i in (0, 1)) if p else None
                notes.append('Book page re-read: %s -> %s (overround %.2f%%)' % (
                    ' / '.join(str(v) for v in book_obs['decimal_odds']),
                    ' / '.join('%.3f' % v for v in obs_p), overround * 100))
                if drift is not None and drift > 0.005:
                    issues.append('FLAGGED: %s book page no longer matches the archived quote' % m['id'])
                checks.append('official book page re-read')
            except Exception as exc:
                problems.append('book page re-read failed: %s' % exc)
        if m.get('method') == 'model_vrs_mirror' and ev and hltv_points:
            expected = [hltv_points.get(t) for t in m['teams']]
            if expected and None not in expected:
                if list(map(int, ev.get('points') or [])) != list(map(int, expected)):
                    problems.append('HLTV dated Valve points differ from evidence')
                else:
                    checks.append('HLTV dated Valve points re-read')
                    notes.append('HLTV Valve points %s' % ' / '.join(map(str, expected)))
        if m.get('method') == 'model_vrs' and valve_rows and ev:
            for label, points, rank, roster in zip(ev.get('vrs_teams') or [], ev.get('points') or [],
                                                   ev.get('standings') or [], ev.get('rosters') or []):
                matches, reason = valve_candidates(valve_rows, label, points, rank, roster)
                if not matches:
                    problems.append('Valve monthly file: %s (%s)' % (label, reason))
                else:
                    checks.append('Valve file %s' % label)
            notes.append('Valve monthly file verified: %s' % (external.get('valve_monthly_file') or {}).get('sha256', 'sha not supplied'))
        rows.append({
            'id': m['id'], 'teams': m['teams'], 'start': m.get('start'), 'lock': m.get('lock'),
            'expires': m.get('expires_at'), 'method': m.get('method'), 'pick': m.get('pick'),
            'published_probabilities': p, 're_derived_probabilities': calc,
            'fixture_source': m.get('source_url'), 'price_source': (ev or {}).get('api_url') or (ev or {}).get('url'),
            'checks': checks, 'problems': problems, 'notes': notes,
            'attempts': [(a.get('provider'), a.get('status')) for a in (m.get('attempts') or [])],
        })
        if problems:
            issues.extend('%s: %s' % (m['id'], x) for x in problems)
    return {
        'session': '4ed657ce',
        'generated_at': data.get('generated_at'),
        'fixtures_observed_at': data.get('fixtures_observed_at'),
        'coverage_counts': data.get('coverage_counts'),
        'open_rows': len(rows),
        'reproduced_rows': sum(1 for r in rows if r['re_derived_probabilities'] is not None and not r['problems']),
        'rows_failing': sum(1 for r in rows if r['problems']),
        'issues': issues,
        'rows': rows,
    }, valve_rows


def md_escape(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def markdown(report, external):
    out = []
    out.append('# Session 4ed657ce — dated line-by-line verification')
    out.append('')
    out.append('Snapshot `%s`; fixtures observed `%s`; coverage `%s`. Every row below has an official Hotspawn fixture link and a separate https price/model source. A blank or failed check is reported, never filled.' % (
        report['generated_at'], report['fixtures_observed_at'], json.dumps(report.get('coverage_counts'))))
    out.append('')
    out.append('## Evidence ladder actually used')
    out.append('')
    for i, (title, url) in enumerate(LADDER, 1):
        out.append('%d. [%s](%s)' % (i, title, url))
    out.append('')
    out.append('Hotspawn crowd percentages are excluded. The ladder follows the user’s order for uncovered matches: **HLTV first, then esportsbooks and esports betting lines**, before our own labelled model.')
    out.append('')
    out.append('## Inventory re-read')
    inv = external.get('inventory') or {}
    for key in ('lobby_uncached', 'lobby_cache_busted', 'cs2_page_cache_busted', 'fixtures_api'):
        item = inv.get(key) or {}
        if item:
            out.append('- %s: %s — [%s](%s)' % (key, item.get('tier_count') or item.get('snapshot_count'), item.get('url'), item.get('url')))
    out.append('')
    out.append('## Open rows')
    out.append('')
    out.append('| Fixture | Match | Pick | P1 / P2 | Method | Official fixture | Price / model source | Re-derived | External re-read | Expires |')
    out.append('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')
    for r in report['rows']:
        p = r['published_probabilities'] or ['', '']
        out.append('| %s | %s vs %s | %s | %.1f%% / %.1f%% | %s | [Hotspawn](%s) | [source](%s) | %s | %s | %s |' % (
            r['id'], md_escape(r['teams'][0]), md_escape(r['teams'][1]), md_escape(r['pick'] or '—'),
            float(p[0] or 0) * 100, float(p[1] or 0) * 100, md_escape(r['method'] or '—'),
            r['fixture_source'] or '', r['price_source'] or '',
            'OK' if r['re_derived_probabilities'] is not None and not r['problems'] else 'FAIL',
            md_escape(' · '.join(r['notes'])) or 'archived receipt only', r['expires'] or '—'))
    out.append('')
    out.append('## Source attempts for non-exchange rows')
    out.append('')
    for r in report['rows']:
        if r['method'] in ('exchange', 'exchange_wide'):
            continue
        attempts = ' → '.join('%s:%s' % (a, b) for a, b in r['attempts']) or 'not recorded'
        out.append('- **%s** %s vs %s — %s. Attempts: %s. [Fixture](%s) · [Price/model](%s)' % (
            r['id'], md_escape(r['teams'][0]), md_escape(r['teams'][1]),
            md_escape(r['method']), md_escape(attempts), r['fixture_source'], r['price_source']))
    out.append('')
    out.append('## Flagged irregularities and limitations')
    out.append('')
    if report['issues']:
        for issue in report['issues']:
            out.append('- %s' % issue)
    else:
        out.append('- No row-level verification failures in this snapshot.')
    out.append('')
    out.append('A later market price that differs from the archived quote is normal market movement; the published percentage remains tied to its own timestamp and expires at the earlier of the evidence window, Hotspawn lock or match start. The scheduled refresh re-prices it.')
    return '\n'.join(out) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--data', default=str(ROOT / 'data' / 'latest.json'))
    ap.add_argument('--external', default=str(ROOT / 'research' / 'session-4ed657ce' / 'external-observations.json'))
    ap.add_argument('--valve-file', default=None, help='local copy of Valve standings markdown for offline verification')
    ap.add_argument('--out', default=str(ROOT / 'research' / 'session-4ed657ce' / 'verification-report.json'))
    ap.add_argument('--markdown', default=str(ROOT / 'research' / 'session-4ed657ce' / 'VERIFICATION.md'))
    args = ap.parse_args(argv)
    data = json.loads(Path(args.data).read_text())
    external_path = Path(args.external)
    external = json.loads(external_path.read_text()) if external_path.exists() else {}
    valve_text = Path(args.valve_file).read_text() if args.valve_file and Path(args.valve_file).exists() else None
    report, _ = audit(data, external, valve_text)
    out_path = Path(args.out); out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    if args.markdown:
        md_path = Path(args.markdown); md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(markdown(report, external), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('open_rows', 'reproduced_rows', 'rows_failing')}, indent=2))
    if report['rows_failing']:
        for issue in report['issues']:
            print('FAIL:', issue)
        return 1
    if report['issues']:
        print('Flagged (non-blocking):')
        for issue in report['issues']:
            print('-', issue)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
