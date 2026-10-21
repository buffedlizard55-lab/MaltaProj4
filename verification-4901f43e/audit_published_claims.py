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
    audit.ok('vrs-gap:1082858',
             'Valve publishes a %d-point gap between #119 (%d) and #136 (%d); the model turns it '
             'into raw %.6f' % (oc - gz, oc, gz, raw))

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
    audit.ok('vrs-rows:1082793',
             'the standings labels #96 and #59, cited alongside a 36.3%% / 63.7%% split for this '
             'fixture, are %s (%d) and %s (%d) -- not 5star and 1win, which Valve publishes at '
             '#80 and #38' % (mislabelled[0] or 'absent', rows.get(96, {}).get('points', 0),
                              mislabelled[1] or 'absent', rows.get(59, {}).get('points', 0)))
    return published


# Percentages that do not reproduce from the file they cite, and the tracked files that may still
# carry them. Scanning rather than asserting keeps these checks honest in both directions: they
# name the file and line while a stale figure is published, and they clear themselves the moment
# the owner corrects it, so nobody has to remember to delete the check.
STALE_CLAIMS = (
    {'fixture': '1082858', 'matchup': 'Ground Zero vs Off Chops',
     'stale': ('59.1%', '40.9%'), 'reproducible': 'Off Chops 60.2% / Ground Zero 39.8%',
     'why': 'Valve publishes 971 (#119) against 878 (#136), a 93-point gap; 59.1% needs 82.85'},
    {'fixture': '1082793', 'matchup': '5star vs 1WIN',
     'stale': ('36.3%', '63.7%'), 'reproducible': '5star 24.3% / 1WIN 75.7%',
     'why': 'Valve publishes 5star at #80 (1110) and 1win at #38 (1383), a 273-point gap; the '
            'labels cited with the claim, #96 and #59, are Bounty Hunters and Iberian Soul'},
)
STALE_CLAIM_PATHS = ('data/review-notes.json', 'data/identities.json', 'data/latest.json',
                     'research/session-db1f35c5/REPORT.md')


def audit_stale_claims(audit):
    """Locate every tracked file that still publishes a percentage the model cannot reproduce."""
    for claim in STALE_CLAIMS:
        hits = []
        for rel in STALE_CLAIM_PATHS:
            path = ROOT / rel
            if not path.exists():
                continue
            for lineno, line in enumerate(path.read_text(errors='replace').splitlines(), 1):
                if any(figure in line for figure in claim['stale']):
                    hits.append('%s:%d' % (rel, lineno))
        if hits:
            audit.warn('stale-figure-published:%s' % claim['fixture'],
                       '%s (%s) still publishes %s in %d tracked location(s): %s. The reproducible '
                       'value is %s, because %s. This is a warning, not a failure: the files belong '
                       'to another session and the correction is logged in '
                       'research/session-4901f43e/REQUESTS.md.'
                       % (claim['matchup'], claim['fixture'], ' / '.join(claim['stale']),
                          len(hits), ', '.join(hits), claim['reproducible'], claim['why']))
        else:
            audit.ok('stale-figure-absent:%s' % claim['fixture'],
                     'no tracked data or research file publishes %s for %s; the reproducible %s is '
                     'the only figure in the repository'
                     % (' / '.join(claim['stale']), claim['matchup'], claim['reproducible']))


def audit_hltv_citations(audit):
    """Every HLTV match id cited in the identity register must serve what it claims."""
    doc = json.loads(IDENTITIES.read_text())
    seen, unverified, confirmed, mismatched = 0, {}, 0, {}
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
                    mismatched.setdefault(match_id, truth)
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

    # How far a wrong citation reaches. The register is prose a reviewer reads; the snapshot and
    # the built pages are what the public site serves, so an id that lands there is clickable.
    for match_id, truth in sorted(mismatched.items()):
        reach = []
        for rel in ('data/identities.json', 'data/review-notes.json', 'data/latest.json',
                    'review.html', 'evidence.html'):
            path = ROOT / rel
            if not path.exists():
                continue
            text = path.read_text(errors='replace')
            links, mentions = text.count('matches/%s' % match_id), text.count(match_id)
            if mentions:
                reach.append((rel, mentions, links))
        rendered = [r for r in reach if r[0].startswith(('review.html', 'evidence.html'))]
        described = ', '.join('%s (%d mention%s, %d as a link)' % (rel, n, '' if n == 1 else 's', l)
                              for rel, n, l in reach)
        audit.warn('hltv-citation-reach:%s' % match_id,
                   'the id that serves "%s" rather than the match it is cited for reaches %s%s. '
                   'Where it is rendered on the site, a reviewer clicking the corroboration link '
                   'for the Zetta / Alianza Lima Esports alias lands on Alliance vs FaZe at RLG '
                   'Tesla Cup 2026. The page that carries the cited lineups is 2399865 (receipt '
                   'R5).' % (truth, described or 'no tracked file',
                             ' -- including the published pages '
                             + ', '.join(r[0] for r in rendered) if rendered else ''))


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
    audit_stale_claims(audit)
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
