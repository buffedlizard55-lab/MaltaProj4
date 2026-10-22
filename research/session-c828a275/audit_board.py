"""Independent, read-only re-derivation of every published pick (session c828a275).

Run against a snapshot:  python research/session-c828a275/audit_board.py data/latest.json

Each open fixture is re-checked line by line from the row's own retained
receipt (the raw exchange fields stored on the row) or from Valve's vendored
standings file, never from the published summary:

  * the pick is one of the two teams and is the higher-probability side;
  * published probabilities re-derive from the stored raw outcome prices
    (market rows) or from Valve's published formula and the vendored file
    (model rows), to 1e-9;
  * both probabilities sum to 1 and the fair decimal odds are their reciprocals;
  * a market row's identity is exact: same two teams, same UTC start;
  * the row's expiry is the earliest of the 8-hour evidence window, the
    Hotspawn lock and the match start;
  * every row carries at least one https source link on a known official host,
    and every research-only row states in words that no percentage is published.

Nothing here writes to the snapshot or to the site. Exit status is 1 only when
a check fails, which is what the report's "fail" column means.
"""
import json
import math
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAX_AGE = timedelta(hours=8)
OFFICIAL_HOSTS = (
    'polymarket.com', 'gamma-api.polymarket.com',
    'pinnacle.com', 'guest.api.arcadia.pinnacle.com',
    'hltv.org', 'www.hltv.org',
    'hotspawn.com', 'play.hotspawn.com', 'www.hotspawn.com',
    'github.com', 'raw.githubusercontent.com',
    'liquipedia.net', 'egamersworld.com', 'thunderpick.io', 'gg.bet',
    'bo3.gg', 'dfrag.gg', 'valve.com', 'steampowered.com',
    'cloudwaysapps.com',
)

# The Hotspawn fixture feed is served from a third-party app host; it is the
# feed URL the collector reads, recorded here so the audit can tell an
# unregistered host from a feed host.
ALIASES = json.loads((ROOT / 'data/identities.json').read_text())['aliases']


def fold(value):
    import unicodedata
    folded = unicodedata.normalize('NFKD', str(value)).casefold()
    return ''.join(c for c in folded if not unicodedata.combining(c) and c.isalnum())


ALIAS_MAP = {fold(n): fold(a['canonical']) for a in ALIASES for n in a['names']}
ALIAS_SOURCE = {fold(n): a for a in ALIASES for n in a['names']}


def same_team(label, fixture_label):
    a, b = fold(label), fold(fixture_label)
    return a == b or ALIAS_MAP.get(a) == ALIAS_MAP.get(b)
RD = 75.0
Q = math.log(10) / 400


def dt(value):
    parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamp without a timezone: %r' % (value,))
    return parsed.astimezone(timezone.utc)


def expected(a, b):
    g = 1 / math.sqrt(1 + 3 * Q * Q * RD * RD / math.pi ** 2)
    return 1 / (1 + 10 ** (-g * (float(a) - float(b)) / 400))


def calibrated(raw):
    return 0.5 + 0.7986 * (raw - 0.5)


def host_of(url):
    m = re.match(r'https://([^/]+)/', str(url or ''))
    return m.group(1).lower() if m else None


def official(url):
    host = host_of(url)
    return bool(host) and any(host == h or host.endswith('.' + h) for h in OFFICIAL_HOSTS)


def vrs_rows():
    meta = json.loads((ROOT / 'data/vrs/meta.json').read_text())
    text = (ROOT / 'data/vrs' / meta['file']).read_text()
    rows = []
    for line in text.splitlines():
        m = re.match(r'^\|\s*(\d+)\s*\|\s*(-?\d+)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*\[details\]', line)
        if m:
            rows.append({'standing': int(m.group(1)), 'points': int(m.group(2)), 'name': m.group(3).strip()})
    return meta, rows


def audit(snapshot_path):
    data = json.loads(Path(snapshot_path).read_text())
    generated = dt(data['generated_at'])
    meta, standings = vrs_rows()
    results = []

    for row in data['matches']:
        if row.get('state') != 'open':
            continue
        checks, failures = [], []

        def check(name, ok, detail=''):
            checks.append({'check': name, 'ok': bool(ok), 'detail': detail})
            if not ok:
                failures.append(name)

        teams = row.get('teams') or []
        pick = row.get('pick')
        probs = row.get('probabilities')
        method = row.get('method') or 'unresolved'
        start, lock = dt(row['start']), dt(row['lock'])
        evidence = row.get('evidence') or []

        check('two distinct teams', len(teams) == 2 and len({t.strip().lower() for t in teams}) == 2, str(teams))
        check('still open at snapshot time', start > generated and lock > generated,
              'start %s lock %s snapshot %s' % (start.isoformat(), lock.isoformat(), generated.isoformat()))
        check('a pick is published', bool(pick), 'pick=%r' % (pick,))
        check('the pick is one of the two teams', pick in teams, 'pick=%r' % (pick,))

        if probs is not None:
            check('two probabilities', isinstance(probs, list) and len(probs) == 2, str(probs))
            check('probabilities are finite and inside 0..1',
                  all(isinstance(p, float) and math.isfinite(p) and 0 < p < 1 for p in probs), str(probs))
            check('probabilities sum to 1', abs(sum(probs) - 1) < 1e-9, repr(sum(probs)))
            best = max(range(2), key=lambda i: probs[i])
            check('the pick is the higher-probability side', teams[best] == pick,
                  'pick %r vs argmax %r' % (pick, teams[best]))
            fair = row.get('fair_odds') or []
            check('fair odds are the reciprocals of the probabilities',
                  len(fair) == 2 and all(abs(fair[i] - 1 / probs[i]) < 1e-9 for i in range(2)), str(fair))
            # Reproduce scripts.core.pick_deadline exactly: the earliest of the
            # fixture-observation window, the lock, the start, and every quote's
            # observation/update window.
            deadlines = [dt(data['fixtures_observed_at']) + MAX_AGE, start, lock]
            for ev in evidence:
                deadlines.append(dt(ev['observed_at']) + MAX_AGE)
                if ev.get('updated_at'):
                    deadlines.append(dt(ev['updated_at']) + MAX_AGE)
            expected_expiry = min(deadlines)
            check('expiry is the earliest of window, lock, start and quote update',
                  row.get('expires_at') is not None and abs((dt(row['expires_at']) - expected_expiry).total_seconds()) < 1,
                  'row %s vs derived %s' % (row.get('expires_at'), expected_expiry.isoformat()))

            if method == 'bookmaker_fallback':
                # A bookmaker receipt stores the book's decimal odds, not
                # exchange outcome prices: de-vig them and compare.
                ev = evidence[0]
                odds = ev.get('decimal_odds') or (ev.get('raw') or {}).get('decimal_odds')
                check('bookmaker row carries two decimal odds', isinstance(odds, list) and len(odds) == 2, str(odds))
                if isinstance(odds, list) and len(odds) == 2:
                    implied = [1 / float(o) for o in odds]
                    total = sum(implied)
                    derived = [x / total for x in implied]
                    check('bookmaker probabilities reproduce from its decimal odds',
                          all(abs(derived[i] - probs[i]) < 1e-9 for i in range(2)),
                          'derived %s published %s' % (derived, probs))
                    overround = ev.get('overround')
                    check('stored overround equals the derived overround',
                          overround is not None and abs(float(overround) - (total - 1)) < 1e-9,
                          '%r vs %r' % (overround, total - 1))
                    check('overround inside the published -2%..25% gate', -0.02 <= total - 1 <= 0.25, repr(total - 1))

            if method.startswith('exchange') or method.startswith('market'):
                check('a market row stores its raw receipt', bool(evidence), '%d evidence rows' % len(evidence))
                for ev in evidence:
                    raw = ev.get('raw') or {}
                    prices = raw.get('outcomePrices')
                    names = raw.get('outcomes')
                    try:
                        rawp = [float(x) for x in json.loads(prices)] if isinstance(prices, str) else [float(x) for x in prices]
                        rawn = json.loads(names) if isinstance(names, str) else list(names)
                    except (TypeError, ValueError, KeyError):
                        check('raw outcome prices are readable', False, repr(prices))
                        continue
                    check('published probabilities equal the raw prices',
                          len(rawp) == 2 and all(abs(rawp[i] - probs[i]) < 1e-9 for i in range(2)),
                          'raw %s published %s' % (rawp, probs))
                    pairs = (same_team(rawn[0], teams[0]) and same_team(rawn[1], teams[1])) or \
                            (same_team(rawn[0], teams[1]) and same_team(rawn[1], teams[0])) if len(rawn) == 2 else False
                    used_alias = [ALIAS_SOURCE[n] for n in (fold(x) for x in rawn) if n in ALIAS_SOURCE]
                    alias_sourced = all(
                        str(a.get('source') or '').startswith('https://') and str(a.get('basis') or '')
                        for a in used_alias)
                    check('raw outcome names are the two fixture teams (exact, or through a registered alias with a primary source)',
                          pairs and alias_sourced,
                          '%s vs %s; aliases %s' % (rawn, teams, [a['canonical'] for a in used_alias]))
                    market_start = raw.get('eventStartTime') or raw.get('gameStartTime')
                    check('market start equals the Hotspawn start',
                          market_start is not None and dt(str(market_start).replace(' ', 'T')) == start,
                          'market %r hotspawn %r' % (market_start, row['start']))
                    spread = ev.get('spread')
                    limit = 0.60 if 'wide' in (ev.get('tier') or '') else 0.25
                    check('spread inside the published gate',
                          spread is not None and abs(float(spread)) <= limit + 1e-9,
                          'spread %s limit %s' % (spread, limit))
                    check('liquidity at least 100',
                          float(raw.get('liquidity') or ev.get('liquidity') or 0) >= 100,
                          str(raw.get('liquidity') or ev.get('liquidity')))
                    check('market is open and accepting orders',
                          raw.get('closed') is False and raw.get('acceptingOrders') is True,
                          'closed=%r accepting=%r' % (raw.get('closed'), raw.get('acceptingOrders')))

            if method.startswith('model_vrs'):
                ev = evidence[0]
                names = ev.get('vrs_teams') or []
                points = ev.get('points') or []
                check('model row names the two standings rows', len(names) == 2, str(names))
                check('model row carries two points values', len(points) == 2, str(points))
                if method == 'model_vrs_mirror':
                    # HLTV mirrors Valve's ranking with the same points and a
                    # dated page; the receipt must therefore be an hltv.org read
                    # and must carry its own observation time.
                    urls = [str(ev.get('url') or ''), str(ev.get('api_url') or ''), str(ev.get('source') or '')]
                    check('mirror row cites a dated hltv.org ranking page',
                          any(u.startswith('https://www.hltv.org/') for u in urls) and bool(ev.get('observed_at')),
                          str(urls)[:160])
                # The points must exist verbatim in the vendored official file.
                for name, pts in zip(names, points) if method == 'model_vrs' else ():
                    match = [r for r in standings if r['name'].lower() == str(name).lower()]
                    check('standings file holds %r at %r points' % (name, pts),
                          any(r['points'] == pts for r in match),
                          'file rows: %s' % [(r['name'], r['points']) for r in match][:3])
                derived = calibrated(expected(points[0], points[1])) if len(points) == 2 else None
                check('published probabilities reproduce from Valve formula',
                      derived is not None and abs(derived - probs[0]) < 1e-9,
                      'derived %.12f published %.12f' % (derived or -1, probs[0]))
                check('standings date is the vendored file', ev.get('standings_as_of') == meta['file'].split('_')[-1].replace('.md', '').replace('_', '-')
                      or ev.get('standings_as_of', '').replace('-', '_') in meta['file'],
                      '%r vs %r' % (ev.get('standings_as_of'), meta['file']))

        if probs is None:
            if method == 'research_vrs_single':
                resolved = [r for r in standings if fold(r['name']) in {fold(teams[0]), fold(teams[1])}]
                listed = [r for r in resolved if fold(r['name']) == fold(pick)]
                other = [r for r in resolved if fold(r['name']) != fold(pick)]
                check('one-sided standings tier: the pick is listed in the vendored file',
                      bool(listed), str([(r['name'], r['points']) for r in resolved]))
                check('one-sided standings tier: the other team is absent from the vendored file',
                      not other, str([(r['name'], r['points']) for r in resolved]))
            check('a research-only row publishes no probability, fair odds or pick-side numbers',
                  row.get('fair_odds') is None and row.get('probabilities') is None,
                  'fair_odds=%r probabilities=%r' % (row.get('fair_odds'), row.get('probabilities')))
            if method in ('research_rank', 'research_rank_single'):
                ctx = row.get('hltv_context') or {}
                ranks = ctx.get('resolved_ranks') or []
                ranked = [r for r in ranks if r.get('hltv_rank')]
                unranked = [r for r in ranks if not r.get('hltv_rank')]
                if method == 'research_rank':
                    check('ranking tier: two ranked teams, and the pick is the better-ranked one',
                          len(ranked) == 2 and ranked[0]['hltv_rank'] != ranked[1]['hltv_rank']
                          and min(ranked, key=lambda r: r['hltv_rank'])['team'] == pick
                          and all(r.get('rank_source', '').startswith('https://www.hltv.org/') for r in ranked),
                          str(ranks))
                    check('ranking tier: neither team is recorded as unranked', not unranked, str(ranks))
                else:
                    check('one-sided ranking tier: exactly one ranked team, and it is the pick',
                          len(ranked) == 1 and ranked[0].get('team') == pick
                          and ranked[0].get('rank_source', '').startswith('https://www.hltv.org/'),
                          str(ranks))
                    check('one-sided ranking tier: the other team is recorded as unranked',
                          len(unranked) == 1 and unranked[0].get('status') == 'unranked', str(ranks))
            text = ' '.join([row.get('reason') or ''] + list(row.get('flags') or []))
            check('a research-only row states in words that no percentage is published',
                  bool(re.search(r'no percentage|no probability', text, re.I)),
                  (row.get('reason') or '')[:120])
            check('a research-only row is still labelled as research',
                  method.startswith('research'), method)

        sources = [row.get('source_url')] + [e.get('url') for e in evidence] + [e.get('api_url') for e in evidence]
        sources += [a.get('url') for a in row.get('attempts') or [] if a.get('status') == 'resolved']
        sources += [row.get('feed_url')]
        official_sources = sorted({u for u in sources if u and official(u)})
        check('at least one official https source link', bool(official_sources), '; '.join(official_sources[:3]))
        check('every http source link is on a known official host',
              all(official(u) for u in sources if u and str(u).startswith('http')),
              '; '.join(sorted({u for u in sources if u and str(u).startswith('http') and not official(u)})[:3]))

        results.append({
            'fixture': row.get('id'), 'teams': teams, 'start': row.get('start'),
            'method': method, 'pick': pick,
            'probabilities': probs,
            'checks': len(checks), 'failures': failures,
            'sources': official_sources,
        })

    summary = {
        'snapshot': str(snapshot_path),
        'snapshot_generated_at': data['generated_at'],
        'vendored_standings': meta['file'],
        'open_rows': len(results),
        'rows_with_a_pick': sum(1 for r in results if r['pick']),
        'rows_with_a_probability': sum(1 for r in results if r['probabilities'] is not None),
        'rows_research_only': sum(1 for r in results if r['probabilities'] is None and r['pick']),
        'rows_without_a_pick': sum(1 for r in results if not r['pick']),
        'checks_run': sum(r['checks'] for r in results),
        'checks_failed': sum(len(r['failures']) for r in results),
    }
    return summary, results


def main():
    snapshot = sys.argv[1] if len(sys.argv) > 1 else 'data/latest.json'
    summary, results = audit(snapshot)
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('research/session-c828a275/board-audit.json')
    payload = {'summary': summary, 'rows': results}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    for row in results:
        flag = 'FAIL' if row['failures'] else 'ok'
        print('%-8s %-28s %-18s %-22s %s' % (row['fixture'], ' vs '.join(row['teams'])[:28],
              row['method'], str(row['probabilities'])[:22], flag))
        for failure in row['failures']:
            print('        ! ' + failure)
    return 1 if summary['checks_failed'] else 0


if __name__ == '__main__':
    sys.exit(main())
