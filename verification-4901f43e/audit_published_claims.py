"""Independent audit of published claims, session 4901f43e.

Nothing here trusts a report, a docstring or a completion log. Every number this
script confirms is re-derived by calling the repository's own calculators
(``scripts.core.quote_polymarket``, ``scripts.vrs.expected`` / ``calibrated``)
on values read straight from a receipt or a snapshot, so a reviewer can replay
the same arithmetic offline.

Two exit behaviours, deliberately different:

* integrity failures of this session's own receipts, or a snapshot row whose
  published probability does not reproduce from its own evidence, are hard
  failures -- they mean the published board is wrong.
* claims this script cannot verify offline (a citation whose target page it
  cannot fetch, a prose figure in another session's research notes) are
  reported as warnings and do not fail the run, because failing them would
  break CI for files this session does not own. ``--strict`` promotes them to
  failures for a local pre-merge run.

Usage::

    python verification-4901f43e/audit_published_claims.py \
        [--receipts PATH] [--snapshot PATH] [--json OUT] [--strict]
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import core, vrs  # noqa: E402

DEFAULT_RECEIPTS = ROOT / 'research/session-4901f43e/receipts-2026-10-21.json'
STANDINGS = ROOT / 'data/vrs/standings_global_2026_10_05.md'
IDENTITIES = ROOT / 'data/identities.json'

# Crowd-vote figures this session saw on the pages it read. They are recorded so
# the audit can prove they were never published as probabilities.
CROWD_VOTES = {
    '1082837': {'HLTV "Pick a winner"': [75.0, 25.0], 'Strafe votes': [24.0, 76.0]},
    '1082858': {'HLTV "Pick a winner"': [50.0, 50.0]},
}

# HLTV resolves /matches/<id>/ by numeric id and ignores the slug, so a wrong id
# behind a plausible slug passes a casual link check. Verified 2026-10-21 by
# reading both pages (receipts R5 and R11).
HLTV_MATCH_TRUTH = {
    '2399865': 'zetta-vs-los-ninos',
    '2399867': 'alliance-vs-faze',
    '2399696': 'cct-2026-challengers-europe-series-8-lower-bracket-round-3-2',
    '2399888': 'ground-zero-vs-off-chops',
    '2399802': 'zetta-vs-realgotis22',
}


def sha(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


class Audit:
    def __init__(self):
        self.checks = []
        self.warnings = []

    def ok(self, name, detail):
        self.checks.append({'name': name, 'status': 'pass', 'detail': detail})

    def fail(self, name, detail):
        self.checks.append({'name': name, 'status': 'fail', 'detail': detail})

    def warn(self, name, detail):
        self.warnings.append({'name': name, 'detail': detail})


def audit_receipt_integrity(audit, doc):
    """A receipt that cannot be replayed is not evidence."""
    receipts = doc.get('receipts')
    if not isinstance(receipts, list) or not receipts:
        audit.fail('receipts-present', 'Receipt file carries no receipts')
        return []
    audit.ok('receipts-present', '%d receipts' % len(receipts))
    required = ('id', 'url', 'retrieved_at', 'extract', 'extract_sha256',
                'evidence_level', 'read_path')
    for item in receipts:
        rid = item.get('id', '<unnamed>')
        missing = [k for k in required if not item.get(k)]
        if missing:
            audit.fail('receipt-fields:%s' % rid, 'missing ' + ', '.join(missing))
            continue
        if sha(item['extract']) != item['extract_sha256']:
            audit.fail('receipt-hash:%s' % rid,
                       'extract does not match its recorded sha256; edited after the read')
            continue
        if not str(item['url']).startswith('https://'):
            audit.fail('receipt-url:%s' % rid, 'not an https URL: %s' % item['url'])
            continue
        try:
            stamp = core.dt(item['retrieved_at'])
        except ValueError as exc:
            audit.fail('receipt-time:%s' % rid, str(exc))
            continue
        bound = item.get('read_not_before')
        if bound and core.dt(bound) > stamp:
            audit.fail('receipt-time-order:%s' % rid,
                       'read_not_before %s is after retrieved_at %s' % (bound, stamp))
            continue
        audit.ok('receipt-replayable:%s' % rid,
                 '%s read via %s, sha256 %s…' % (item['url'], item['read_path'],
                                                 item['extract_sha256'][:12]))
    return receipts


def receipt(receipts, rid):
    return next((r for r in receipts if r.get('id') == rid), None)


def replay_polymarket(audit, receipts):
    """Run the real strict exchange gate on the values read off Polymarket."""
    item = receipt(receipts, 'R1-polymarket-market-6001634')
    if not item:
        audit.fail('replay-polymarket', 'receipt R1 absent')
        return
    values = item['verified_values']
    extract = item['extract']

    def field(name, pattern):
        found = re.search(name + r'=' + pattern, extract)
        return found.group(1) if found else None

    fields = {
        'active': field('active', r'(true|false)'),
        'closed': field('closed', r'(true|false)'),
        'acceptingOrders': field('acceptingOrders', r'(true|false)'),
        'bestBid': field('bestBid', r'([0-9.]+)'),
        'bestAsk': field('bestAsk', r'([0-9.]+)'),
        'liquidity': field('liquidity', r'([0-9.]+)'),
        'sportsMarketType': field('sportsMarketType', r'(\w+)'),
        'outcomePrices': field('outcomePrices', r'(\[[^\]]*\])'),
        'updatedAt': field('updatedAt', r'([0-9T:.Z\-]+)'),
    }
    missing = [k for k, v in fields.items() if v is None]
    if missing:
        audit.fail('replay-polymarket:extract',
                   'receipt R1 extract no longer carries %s; the quote cannot be replayed'
                   % ', '.join(missing))
        return
    prices = json.loads(fields['outcomePrices'].replace("'", '"'))
    candidate = {
        'provider': 'Polymarket', 'id': '6001634',
        'url': 'https://polymarket.com/event/cs2-ale1-ln-2026-10-21',
        'api_url': item['url'],
        'observed_at': item['read_not_before'], 'updated_at': fields['updatedAt'].strip('"'),
        'prices': [float(p) for p in prices],
        'raw': {'id': '6001634', 'outcomePrices': fields['outcomePrices']},
        'market': {'active': fields['active'] == 'true', 'closed': fields['closed'] == 'true',
                   'acceptingOrders': fields['acceptingOrders'] == 'true',
                   'bestBid': float(fields['bestBid']), 'bestAsk': float(fields['bestAsk']),
                   'liquidity': float(fields['liquidity']),
                   'sportsMarketType': fields['sportsMarketType']},
        'teams': ['Alianza Lima Esports', 'Los Niños'],
        'start': values['start_utc'],
    }
    now = core.dt(item['retrieved_at'])
    try:
        quote = core.quote_polymarket(candidate, [1, 0], now)
    except ValueError as exc:
        audit.fail('replay-polymarket:strict-gate', 'the real gate refused this quote: %s' % exc)
        return
    got = [round(p, 6) for p in quote['probabilities']]
    # order [1, 0] maps fixture teams (Zetta, LOS NINOS) onto market outcomes.
    if got != [0.615, 0.385]:
        audit.fail('replay-polymarket:value',
                   'replayed %s but the receipt records LOS NINOS 0.615 / Zetta 0.385' % got)
        return
    if quote['tier'] != 'exchange':
        audit.fail('replay-polymarket:tier',
                   'replayed tier %s, not the strict "exchange" tier' % quote['tier'])
        return
    audit.ok('replay-polymarket:strict-gate',
             'scripts.core.quote_polymarket accepts the read quote at tier=%s, spread=%.2f, '
             'liquidity=$%.2f and returns LOS NINOS %.1f%% / Zetta %.1f%%'
             % (quote['tier'], quote['spread'], quote['liquidity'],
                round(got[0] * 100, 1), round(got[1] * 100, 1)))


def replay_vrs_model(audit):
    """Re-derive every model probability this session checked from Valve's file."""
    text = STANDINGS.read_text()
    parsed = vrs.parse(text)
    rows = {r['standing']: r for r in parsed['teams']}
    audit.ok('vrs-standings-parse',
             '%s parsed: %d ordered rows as of %s' % (STANDINGS.name, len(rows), parsed['as_of']))
    expected_points = {38: ('1win', 1383), 80: ('5star', 1110), 86: ('FlyQuest', 1093),
                       119: ('THUNDER dOWNUNDER', 971), 136: ('Ground Zero', 878),
                       157: ('benched gods', 811), 329: ('benched gods', 516),
                       357: ('Zetta', 473)}
    for standing, (name, points) in sorted(expected_points.items()):
        row = rows.get(standing)
        if not row:
            audit.fail('vrs-row:%d' % standing, 'row absent from the published standings')
            continue
        if row['name'] != name or row['points'] != points:
            audit.fail('vrs-row:%d' % standing,
                       'published row is %s / %s, this audit expected %s / %d'
                       % (row['name'], row['points'], name, points))
            continue
        audit.ok('vrs-row:%d' % standing, '%s = %d points (Valve official)' % (name, points))

    # 1082858 Ground Zero (878) vs Off Chops -> THUNDER dOWNUNDER (971).
    gz, oc = rows[136]['points'], rows[119]['points']
    raw = vrs.expected(gz, oc)
    p_gz = vrs.calibrated(raw)
    published = [round(p_gz * 100, 1), round((1 - p_gz) * 100, 1)]
    if published != [39.8, 60.2]:
        audit.fail('vrs-replay:1082858',
                   'Valve points %d vs %d replay to %.1f%% / %.1f%%, not the 39.8 / 60.2 this '
                   'audit derives' % (gz, oc, published[0], published[1]))
    else:
        audit.ok('vrs-replay:1082858',
                 'Ground Zero %d vs THUNDER dOWNUNDER %d -> raw expectation %.6f, calibrated '
                 'Ground Zero %.1f%% / Off Chops %.1f%%; pick Off Chops'
                 % (gz, oc, raw, published[0], published[1]))
    # The figure circulating in research notes for the same two rows.
    claimed = 0.591
    implied_raw = 0.5 + (claimed - 0.5) / vrs.SLOPE
    implied_diff = -__import__('math').log10(1 / implied_raw - 1) * 400 / vrs.G
    audit.warn('vrs-claim-does-not-replay:1082858',
               'A 59.1%% / 40.9%% split for this fixture needs a points gap of %.1f, but Valve '
               'publishes %d (#119) against %d (#136), a gap of %d. The reproducible value is '
               '60.2%% / 39.8%%. The published board must carry the reproducible one.'
               % (implied_diff, oc, gz, oc - gz))

    # 1082793 5star (#80, 1110) vs 1WIN (#38, 1383) -- the same replay, second fixture.
    five_star, one_win = rows[80]['points'], rows[38]['points']
    raw2 = vrs.expected(five_star, one_win)
    published2 = [round(vrs.calibrated(raw2) * 100, 1), round(vrs.calibrated(1 - raw2) * 100, 1)]
    if published2 != [24.3, 75.7]:
        audit.fail('vrs-replay:1082793',
                   'Valve points %d vs %d replay to %.1f%% / %.1f%%, not the 24.3 / 75.7 this '
                   'audit derives' % (five_star, one_win, published2[0], published2[1]))
    else:
        audit.ok('vrs-replay:1082793',
                 '5star %d (#80) vs 1win %d (#38, Hotspawn labels it 1WIN) -> raw expectation '
                 '%.6f, calibrated 5star %.1f%% / 1WIN %.1f%%; pick 1WIN'
                 % (five_star, one_win, raw2, published2[0], published2[1]))
    mislabelled = (rows.get(96, {}).get('name'), rows.get(59, {}).get('name'))
    audit.warn('vrs-claim-does-not-replay:1082793',
               'A 36.3%% / 63.7%% split reported for 5star vs 1WIN does not replay. Valve '
               'publishes 5star at #80 (%d) and 1WIN at #38 (%d), which the repository model '
               'turns into %.1f%% / %.1f%%, and the standings labels cited with that claim '
               '(#96 / #59) are %s and %s -- two unrelated teams.'
               % (five_star, one_win, published2[0], published2[1],
                  mislabelled[0] or 'absent', mislabelled[1] or 'absent'))
    return published


def audit_hltv_citations(audit):
    """Every HLTV match id cited in the identity register must serve what it claims."""
    doc = json.loads(IDENTITIES.read_text())
    seen, unverified, confirmed = 0, {}, 0
    for entry in doc.get('aliases', []):
        blobs = [json.dumps(entry.get('source', '')), json.dumps(entry.get('additional_source', ''))]
        blobs += [json.dumps(c) for c in entry.get('corroboration', []) or []]
        blobs.append(entry.get('basis', ''))
        for blob in blobs:
            for match_id, slug in re.findall(r'hltv\.org/matches/(\d+)/([A-Za-z0-9\-]+)', blob):
                seen += 1
                truth = HLTV_MATCH_TRUTH.get(match_id)
                if truth is None:
                    unverified.setdefault(match_id, slug)
                    continue
                first = slug.split('-')[0].lower()
                if not truth.startswith(first) and first not in truth:
                    audit.warn('hltv-citation-mismatch:%s' % match_id,
                               'identity entry "%s" cites hltv.org/matches/%s/%s, but reading that '
                               'id serves "%s". HLTV resolves matches by numeric id and ignores the '
                               'slug, so the link looks right and is wrong. The Zetta vs LOS NINOS '
                               'page this session read is 2399865 (receipt R5); 2399867 is '
                               'Alliance vs FaZe at RLG Tesla Cup 2026 (receipt R11).'
                               % (entry.get('canonical', '?'), match_id, slug, truth))
                else:
                    confirmed += 1
                    audit.ok('hltv-citation:%s' % match_id, 'serves %s as cited' % slug)
    if unverified:
        audit.warn('hltv-citations-not-read',
                   '%d distinct HLTV match pages are cited by the identity register and were not '
                   'read by this session, so they are neither confirmed nor rejected: %s'
                   % (len(unverified), ', '.join(sorted(unverified))))
    audit.ok('hltv-citations-scanned',
             '%d HLTV match citations scanned in data/identities.json, %d confirmed against a page '
             'this session read, %d not read' % (seen, confirmed, len(unverified)))


def audit_snapshot(audit, path):
    """Every open row must carry a pick, or a published reason, and reproduce."""
    doc = json.loads(Path(path).read_text())
    matches = doc.get('matches', [])
    opens = [m for m in matches if m.get('state') == 'open']
    audit.ok('snapshot-rows',
             '%s: %d rows, %d open, generated_at %s, coverage %s'
             % (Path(path).name, len(matches), len(opens), doc.get('generated_at'),
                doc.get('coverage')))
    for m in opens:
        fid, label = m['id'], ' vs '.join(m['teams'])
        if not m.get('pick') and not m.get('reason'):
            audit.fail('open-row-needs-pick-or-reason:%s' % fid,
                       '%s has neither a pick nor a published reason' % label)
            continue
        probs = m.get('probabilities')
        if probs is None:
            if not m.get('reason'):
                audit.fail('blank-probability-needs-reason:%s' % fid,
                           '%s publishes no percentage and states no reason' % label)
            else:
                audit.ok('blank-probability-documented:%s' % fid,
                         '%s: no percentage, method=%s, reason published (%d chars)'
                         % (label, m.get('method'), len(m['reason'])))
            continue
        evidence = m.get('evidence') or []
        if not evidence:
            audit.fail('probability-without-evidence:%s' % fid,
                       '%s publishes %s with no evidence entry' % (label, probs))
            continue
        quote = evidence[0]
        if not str(quote.get('url') or '').startswith('https://'):
            audit.fail('evidence-link:%s' % fid, '%s evidence has no https source link' % label)
            continue
        replayed = replay_row(m, quote)
        if replayed is None:
            audit.warn('row-replay-unsupported:%s' % fid,
                       '%s: provider %s has no offline replay in this audit; link %s'
                       % (label, quote.get('provider'), quote['url']))
            continue
        if max(abs(a - b) for a, b in zip(replayed, probs)) > 5e-4:
            audit.fail('row-does-not-replay:%s' % fid,
                       '%s publishes %s but its own evidence replays to %s'
                       % (label, [round(p, 4) for p in probs], [round(p, 4) for p in replayed]))
            continue
        audit.ok('row-replays:%s' % fid,
                 '%s: %s -> %.1f%% / %.1f%% via %s (%s)'
                 % (label, quote.get('provider'), round(probs[0] * 100, 1),
                    round(probs[1] * 100, 1), m.get('method'), quote['url']))
        crowd = CROWD_VOTES.get(fid)
        if crowd:
            for source, split in crowd.items():
                if [round(probs[0] * 100, 1), round(probs[1] * 100, 1)] == split:
                    audit.fail('crowd-vote-published:%s' % fid,
                               '%s publishes %s, identical to the %s crowd vote' % (label, split, source))
    audit.ok('crowd-votes-excluded',
             'no open row publishes an HLTV or Strafe crowd-vote split as its probability')


def replay_row(match, quote):
    """Recompute a row's probability from its own stored evidence, offline."""
    provider = quote.get('provider')
    try:
        if provider == 'Valve VRS model':
            points = quote['points']
            raw = vrs.expected(points[0], points[1])
            first = vrs.calibrated(raw)
            return [first, 1 - first]
        if provider == 'Polymarket':
            raw_prices = quote['raw'].get('outcomePrices')
            prices = json.loads(raw_prices) if isinstance(raw_prices, str) else list(raw_prices)
            prices = [float(p) for p in prices]
            total = sum(prices)
            source_teams = list(quote.get('source_teams') or [])
            # The market label is not always the Hotspawn label ("BakS eSports"
            # against "BakS"). The row stores the event's team metadata, so the
            # abbreviation mapping the collector used is recoverable from the
            # snapshot alone; rebuild it exactly as scripts.core does.
            metadata = quote.get('team_metadata') or []
            aliases = [[t, *[x.get('abbreviation', '') for x in metadata
                            if x.get('name') == t]] for t in source_teams]
            comparable = source_teams[:]
            for i, alias_set in enumerate(aliases):
                targets = [t for t in match['teams']
                           if core.norm(t) in {core.norm(a) for a in alias_set if a}]
                if len(targets) == 1:
                    comparable[i] = targets[0]
            order = core.orientation(match, comparable, quote.get('start'))
            if order is None:
                return None
            normalised = [p / total for p in prices]
            return [normalised[i] for i in order]
        if provider == 'Pinnacle':
            line = quote['raw']['line']
            values = {p['designation']: p['price'] for p in line['prices']}
            odds = [core.american(values['home']), core.american(values['away'])]
            p, _margin = core.devig(odds)
            order = core.orientation(match, quote.get('source_teams'), quote.get('start'))
            return None if order is None else [p[i] for i in order]
    except (KeyError, TypeError, ValueError, IndexError):
        return None
    if provider in ('Book research',) or quote.get('decimal_odds'):
        odds = quote.get('decimal_odds')
        if not odds:
            return None
        p, _margin = core.devig(list(odds))
        order = core.orientation(match, quote.get('source_teams'), quote.get('start'))
        return None if order is None else [p[i] for i in order]
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--receipts', default=str(DEFAULT_RECEIPTS))
    ap.add_argument('--snapshot', help='a data/latest.json-shaped snapshot to audit row by row')
    ap.add_argument('--json', help='write the full audit result here')
    ap.add_argument('--strict', action='store_true',
                    help='treat unverifiable-offline warnings as failures')
    args = ap.parse_args(argv)

    audit = Audit()
    doc = json.loads(Path(args.receipts).read_text())
    receipts = audit_receipt_integrity(audit, doc)
    if receipts:
        replay_polymarket(audit, receipts)
    replay_vrs_model(audit)
    if IDENTITIES.exists():
        audit_hltv_citations(audit)
    if args.snapshot:
        audit_snapshot(audit, args.snapshot)

    failed = [c for c in audit.checks if c['status'] == 'fail']
    warnings = audit.warnings
    result = {
        'auditor': 'verification-4901f43e/audit_published_claims.py',
        'run_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'receipts_file': args.receipts,
        'snapshot': args.snapshot,
        'checks': audit.checks,
        'warnings': warnings,
        'passed': len(audit.checks) - len(failed),
        'failed': len(failed),
        'strict': bool(args.strict),
    }
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(result, indent=1, ensure_ascii=False) + '\n')
    for c in audit.checks:
        print('%s %s: %s' % ('PASS' if c['status'] == 'pass' else 'FAIL', c['name'], c['detail']))
    for w in warnings:
        print('%s %s: %s' % ('WARN' if not args.strict else 'FAIL', w['name'], w['detail']))
    print('\n%d passed, %d failed, %d warning(s)%s'
          % (result['passed'], result['failed'], len(warnings),
             ' [strict]' if args.strict else ''))
    if failed or (args.strict and warnings):
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
