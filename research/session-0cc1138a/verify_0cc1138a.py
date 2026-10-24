"""Independent re-derivation of every published pick (session 0cc1138a).

This file deliberately does NOT import anything from ``scripts/``. It re-reads the
committed snapshot and rebuilds each number from the archived primary evidence:

* Polymarket rows: the exchange mid is ``p_i = x_i / (x_1 + x_2)`` over the raw
  ``outcomePrices`` string exactly as the Gamma API returned it.
* EGamersWorld listing rows: decimal odds de-vigged with ``q_i = 1 / d_i`` and
  ``p_i = q_i / (q_1 + q_2)``; the overround is ``q_1 + q_2 - 1``.
* Valve VRS model rows: Valve's own Glicko expectation at fixed rating deviation
  (``model/fit.js`` -> ``model/glicko.js``) and Valve's published fit slope from
  ``modelfit.png`` (observed = 0.7986 x expected + 0.126).

It then checks, for every row: the pick is the larger probability, the fair
decimal line is ``1 / p``, the two sides sum to one, the evidence carries a
resolvable https source, and open rows are never left silently blank.

Run:  python3 research/session-0cc1138a/verify_0cc1138a.py [--json]
"""
import argparse
import json
import math
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RD = 75.0
Q = math.log(10) / 400
G = 1 / math.sqrt(1 + 3 * Q * Q * RD * RD / math.pi ** 2)
SLOPE = 0.7986
TOL = 1e-9


def glicko_expect(pa, pb):
    return 1 / (1 + 10 ** (-G * (float(pa) - float(pb)) / 400))


def calibrate(raw):
    return 0.5 + SLOPE * (raw - 0.5)


def norm(name):
    """Lowercase, strip accents (Ni\u00f1os -> ninos) and keep alphanumerics only."""
    folded = unicodedata.normalize('NFKD', str(name))
    folded = ''.join(ch for ch in folded if not unicodedata.combining(ch))
    return ''.join(ch for ch in folded.lower() if ch.isalnum())


def same_team(a, b, identity_sources=()):
    """Lenient but explicit label match: identical, one label is a prefix word run,
    or both labels belong to a receipted identity_sources entry on the evidence record.

    Exchanges list the same club under a longer label ("BakS eSports" for Hotspawn's
    "BakS") or under a verified organization alias stored in ``ev['identity_sources']``
    with a primary https source and written basis (e.g. "Tropa do KinGui" for
    "Projeto do KinGui" on fixture 1083121). Anything else is reported, never guessed.
    """
    a, b = norm(a), norm(b)
    if not a or not b:
        return False
    if a == b:
        return True
    short, long = sorted((a, b), key=len)
    if len(short) >= 3 and long.startswith(short):
        return True
    for entry in identity_sources or ():
        if not isinstance(entry, dict):
            continue
        src = str(entry.get('source') or '')
        basis = str(entry.get('basis') or '').strip()
        if not src.startswith('https://') or not basis:
            continue
        group = {norm(n) for n in (entry.get('names') or ()) if norm(n)}
        if a in group and b in group:
            return True
    return False


IDENTITIES_PATH = Path(__file__).resolve().parents[2] / 'data' / 'identities.json'


def committed_identity_groups():
    """Sourced alias groups from the committed data/identities.json file."""
    try:
        raw = json.loads(IDENTITIES_PATH.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []
    groups = []
    for entry in (raw.get('aliases') or raw.get('identities') if isinstance(raw, dict) else raw) or []:
        if not isinstance(entry, dict):
            continue
        source = entry.get('source') or ''
        basis = str(entry.get('basis') or '').strip()
        names = entry.get('names') or []
        if str(source).startswith('https://') and basis and isinstance(names, list):
            groups.append({norm(n) for n in names if n})
    return groups


def alias_groups(ev):
    """Reviewed identity groups carried on the evidence record AND in data/identities.json.

    A source may list a club under a reviewed alias that is not a prefix of
    the Hotspawn label (Projeto do KinGui vs Tropa do KinGui, sessions
    174afa4f / a30d31a0 / cecfe864 / ea2e254c). The mapping is accepted only
    when the evidence record carries an ``https://`` source and a written
    ``basis``, AND the same pair is a subset of one group in the committed
    ``data/identities.json`` registry (which also carries an https source and
    a written basis). PR #266 aligned the competing tests on this full
    contract; an unregistered, basis-less or non-https alias still fails
    closed.
    """
    entries = ev.get('identity_sources') if isinstance(ev, dict) else ev
    committed = committed_identity_groups()
    groups = []
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        source = entry.get('source') or ''
        basis = str(entry.get('basis') or '').strip()
        names = entry.get('names') or []
        if str(source).startswith('https://') and basis and isinstance(names, list):
            candidate = {norm(n) for n in names if n}
            if candidate and any(candidate <= reg for reg in committed):
                groups.append(candidate)
    return groups


def order_prices(labels, prices, teams, ev=None):
    """Map source outcome order onto the fixture's team order, refusing ambiguity."""
    groups = alias_groups(ev)

    def matches(label, team):
        if same_team(label, team):
            return True
        return any(norm(label) in g and norm(team) in g for g in groups)

    mapping = []
    for team in teams:
        hits = [i for i, label in enumerate(labels) if matches(label, team)]
        if len(hits) != 1:
            raise ValueError('cannot map %r to exactly one source outcome %r' % (team, labels))
        mapping.append(hits[0])
    if len(set(mapping)) != len(mapping):
        raise ValueError('two teams mapped to the same source outcome %r' % (labels,))
    return [prices[i] for i in mapping]


def evidence_probabilities(ev, teams=None):
    """Independent probabilities from a single evidence record, in fixture team order."""
    provider = ev.get('provider')
    if provider == 'Valve VRS model':
        raw = glicko_expect(ev['points'][0], ev['points'][1])
        return [calibrate(raw), 1 - calibrate(raw)], 'valve_vrs'
    if provider == 'HLTV Valve ranking (Valve points)':
        # Integration repair (session d2a55add, 2026-10-24): the documented
        # model_vrs_mirror tier (scripts.summary.ORIGINS) postdates this
        # verifier. Its evidence carries the same Valve points in fixture
        # order and the pipeline applies the identical Glicko expectation and
        # calibration, so the row is re-derived here under its own label
        # instead of being reported as irreproducible. No math is shared with
        # the pipeline beyond Valve's published formula, as before.
        raw = glicko_expect(ev['points'][0], ev['points'][1])
        return [calibrate(raw), 1 - calibrate(raw)], 'valve_vrs_hltv_mirror'
    if 'decimal_odds' in ev:
        q = [1 / float(d) for d in ev['decimal_odds']]
        p = [v / sum(q) for v in q]
        if teams:
            p = order_prices(ev.get('source_teams') or teams, p, teams, ev)
        return p, 'listing_devig'
    raw = ev.get('raw') or {}
    prices = raw.get('outcomePrices')
    if prices:
        x = [float(v) for v in (json.loads(prices) if isinstance(prices, str) else prices)]
        p = [v / sum(x) for v in x]
        labels = json.loads(raw['outcomes']) if isinstance(raw.get('outcomes'), str) else raw.get('outcomes')
        if teams and labels:
            p = order_prices(labels, p, teams, ev)
        return p, 'exchange_mid'
    raise ValueError('no reproducible price in evidence record')


def audit(snapshot):
    rows = [m for m in snapshot['matches'] if m['state'] == 'open']
    out = []
    for m in sorted(rows, key=lambda x: (x.get('start') or '', x['id'])):
        checks, problems = [], []
        probs = m.get('probabilities')
        ev = (m.get('evidence') or [None])[0]
        calc = None
        if ev:
            try:
                calc, kind = evidence_probabilities(ev, m['teams'])
            except Exception as exc:                     # noqa: BLE001 - reported, not raised
                problems.append('evidence not reproducible: %s' % exc)
        if probs is None:
            problems.append('no published probability')
        else:
            if abs(sum(probs) - 1) > TOL:
                problems.append('probabilities do not sum to 1')
            else:
                checks.append('sum=1')
            if calc is not None:
                delta = max(abs(probs[i] - calc[i]) for i in (0, 1))
                if delta > 1e-6:
                    problems.append('published %.6f != re-derived %.6f' % (probs[0], calc[0]))
                else:
                    checks.append('%s reproduced (max delta %.2e)' % (kind, delta))
            pick = m.get('pick')
            best = m['teams'][probs.index(max(probs))]
            if abs(probs[0] - probs[1]) < .0001:
                if pick is not None or not m.get('reason'):
                    problems.append('neutral line needs no directional pick and a limitation')
            elif pick != best:
                problems.append('pick %r is not the larger probability %r' % (pick, best))
            else:
                checks.append('pick is the favourite')
            fair = m.get('fair_odds')
            if fair:
                if max(abs(fair[i] - 1 / probs[i]) for i in (0, 1)) > 1e-6:
                    problems.append('fair odds are not 1/p')
                else:
                    checks.append('fair odds = 1/p')
        for url in (m.get('source_url'), (ev or {}).get('url'), (ev or {}).get('api_url')):
            if url is not None and not str(url).startswith('https://'):
                problems.append('non-https source: %r' % url)
        if not (ev or {}).get('url') and not (ev or {}).get('api_url'):
            problems.append('no source link on the evidence record')
        out.append({
            'id': m['id'],
            'teams': m['teams'],
            'start': m['start'],
            'competition': m.get('competition'),
            'method': m.get('method'),
            'pick': m.get('pick'),
            'published': probs,
            're_derived': calc,
            'provider': (ev or {}).get('provider'),
            'source': (ev or {}).get('url') or (ev or {}).get('api_url'),
            'fixture_source': m.get('source_url'),
            'checked': checks,
            'problems': problems,
        })
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default=str(ROOT / 'data' / 'latest.json'))
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args(argv)
    snapshot = json.loads(Path(args.data).read_text())
    rows = audit(snapshot)
    failed = [r for r in rows if r['problems']]
    summary = {
        'snapshot_generated_at': snapshot.get('generated_at'),
        'fixtures_total': len(snapshot['matches']),
        'open_rows': len(rows),
        'rows_with_pick': sum(1 for r in rows if r['pick']),
        'rows_with_probability': sum(1 for r in rows if r['published']),
        'rows_re_derived': sum(1 for r in rows if r['re_derived']),
        'rows_failing': len(failed),
    }
    if args.json:
        print(json.dumps({'summary': summary, 'rows': rows}, indent=1))
        return 1 if failed else 0
    print('snapshot %s: %d fixtures, %d open, %d picks, %d probabilities'
          % (summary['snapshot_generated_at'], summary['fixtures_total'], summary['open_rows'],
             summary['rows_with_pick'], summary['rows_with_probability']))
    for r in rows:
        print('| %s | %s vs %s | %s | %s | %s | %s |'
              % (r['id'], r['teams'][0], r['teams'][1], r['method'],
                 '%.3f / %.3f' % tuple(r['published']) if r['published'] else '—',
                 r['pick'] or '—', 'OK' if not r['problems'] else 'FAIL: ' + '; '.join(r['problems'])))
    print('rows checked: %d · re-derived: %d · failures: %d'
          % (summary['open_rows'], summary['rows_re_derived'], summary['rows_failing']))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
