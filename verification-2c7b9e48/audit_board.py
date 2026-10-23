"""Independent, zero-collector audit of the published CS2 pick board.

Written for session 2c7b9e48. It never imports ``scripts``: every rule below is
re-implemented from the published data and the official sources it cites, so a
bug in the production collector cannot hide itself by being reused here.

What is checked, row by row
---------------------------
1. **Shape and identity.** Every fixture has a unique Hotspawn id, two distinct
   non-empty team labels and a parseable UTC start. The side order used for the
   probabilities is the fixture's own order.
2. **Official source link.** Every row must carry a link to the official
   Hotspawn record (``www.hotspawn.com`` / ``play.hotspawn.com``) and a feed
   link to Hotspawn's own API host. A row without a primary source is an error,
   not a warning: the project's verification contract is source-first.
3. **Coverage.** An ``open`` row must publish a pick. A pick must name one of
   that fixture's own two teams. A row that cannot be priced must instead carry
   a documented limitation and at least one recorded source attempt with a URL
   and a status. A non-open row must carry a reason and must not publish a pick
   or a probability.
4. **Arithmetic replay.** Probabilities are recomputed from the raw price
   fields the snapshot stores: Polymarket outcome prices (exchange tiers),
   decimal odds (bookmaker tiers) and Valve's published Glicko-to-win formula
   with Valve's published calibration slope (model tiers). Stored values must
   match the replay; the two sides must sum to one.
5. **Side mapping.** The quote's own team labels must map onto the fixture's two
   teams without guessing, and the replayed probabilities must be in the
   fixture's order. A swapped pair is a detectable corruption.
6. **No Hotspawn probabilities.** No probability provider may be Hotspawn or a
   Hotspawn crowd vote: Hotspawn supplies the fixture list only.
7. **Built pages.** If ``--site`` is given: every fixture appears in
   ``matches.html`` inside its own row with an official link, every open row
   appears in ``picks.html`` with its pick and both percentages, every
   unresolved row appears in ``unresolved.html`` *and* in the executive summary
   (``index.html``), and every internal link and anchor resolves.

Usage::

    python verification-2c7b9e48/audit_board.py data/latest.json \
        --site public --output research/session-2c7b9e48/audit.json

Exit code 0 means no errors. Warnings never change the exit code; they are the
review queue, not a failure.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

HOTSPAWN_HOSTS = {'hotspawn.com', 'www.hotspawn.com', 'play.hotspawn.com'}
# Hotspawn's own fixture API host. The CS2 lobby page hydrates its fixture list
# from this endpoint (the repository's capture receipts record the request made
# by play.hotspawn.com itself), so it is a Hotspawn host, not a third party. It
# is kept as a named constant so a future host change is a one-line review.
HOTSPAWN_API_HOSTS = {'phpstack-1372681-6459848.cloudwaysapps.com'}
OFFICIAL_HOSTS = HOTSPAWN_HOSTS | {
    'hltv.org', 'www.hltv.org',
    'polymarket.com', 'www.polymarket.com', 'gamma-api.polymarket.com',
    'egamersworld.com', 'www.egamersworld.com',
    'bo3.gg', 'www.bo3.gg',
    'pinnacle.com', 'www.pinnacle.com', 'guest.api.arcadia.pinnacle.com',
    'thunderpick.io', 'gg.bet', 'liquipedia.net',
    'github.com', 'raw.githubusercontent.com', 'api.github.com',
}
PRICED_METHODS = {'exchange', 'exchange_wide', 'bookmaker', 'bookmaker_fallback',
                  'model_vrs', 'model_vrs_mirror'}
UNPRICED_PICK_METHODS = {'research_rank', 'research_rank_single', 'research_vrs_single'}
ALL_METHODS = PRICED_METHODS | UNPRICED_PICK_METHODS
# Valve's published model constants (model/fit.js, model/glicko.js, modelfit.png),
# re-declared here instead of imported from scripts.vrs.
VALVE_RD = 75.0
VALVE_Q = math.log(10) / 400
VALVE_G = 1 / math.sqrt(1 + 3 * VALVE_Q * VALVE_Q * VALVE_RD * VALVE_RD / math.pi ** 2)
VALVE_SLOPE = 0.7986
TOL = 1e-9


def norm(label):
    """Accent-, case-, punctuation- and whitespace-insensitive label key."""
    text = unicodedata.normalize('NFKD', str(label or '')).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]', '', text.lower())


def words(label):
    text = unicodedata.normalize('NFKD', str(label or '')).encode('ascii', 'ignore').decode()
    return [w for w in re.split(r'[^a-z0-9]+', text.lower()) if w]


def host(url):
    try:
        return (urlparse(str(url)).hostname or '').lower()
    except ValueError:
        return ''


def official(url):
    return host(url) in OFFICIAL_HOSTS or host(url) in HOTSPAWN_API_HOSTS


def parse_time(value):
    return datetime.fromisoformat(str(value).replace('Z', '+00:00'))


class Failure(Exception):
    pass


# --------------------------------------------------------------------------- #
# Arithmetic replay
# --------------------------------------------------------------------------- #
def de_vig(quotes):
    """Normalise positive prices or inverse decimal odds onto a probability pair."""
    if len(quotes) != 2:
        raise Failure('expected two prices, got %r' % (quotes,))
    values = [float(q) for q in quotes]
    if any(v <= 0 for v in values):
        raise Failure('non-positive price in %r' % (quotes,))
    total = sum(values)
    if total <= 0:
        raise Failure('price pair sums to zero')
    return [v / total for v in values]


def decimal_odds(odds):
    if len(odds) != 2:
        raise Failure('expected two decimal odds, got %r' % (odds,))
    values = [float(o) for o in odds]
    if any(o <= 1.0 for o in values):
        raise Failure('decimal odds must exceed 1.0: %r' % (odds,))
    inverse = [1.0 / o for o in values]
    total = sum(inverse)
    return [i / total for i in inverse]


def valve_model(points):
    """Valve's own expected-win formula applied to two published point totals."""
    if len(points) != 2:
        raise Failure('expected two point totals, got %r' % (points,))
    a, b = float(points[0]), float(points[1])
    raw = 1 / (1 + 10 ** (-VALVE_G * (a - b) / 400))
    p_a = 0.5 + VALVE_SLOPE * (raw - 0.5)
    return [p_a, 1 - p_a]


def replay(match, quote):
    """Return the probability pair implied by this row's own raw evidence."""
    method = match.get('method')
    raw = quote.get('raw') or {}
    if method in ('exchange', 'exchange_wide'):
        prices = raw.get('outcomePrices')
        if isinstance(prices, str):
            prices = json.loads(prices)
        if not prices:
            raise Failure('exchange row stores no outcome prices')
        return de_vig(prices)
    if method in ('bookmaker', 'bookmaker_fallback'):
        odds = raw.get('odds')
        if not odds:
            raise Failure('bookmaker row stores no decimal odds')
        return decimal_odds(odds)
    if method in ('model_vrs', 'model_vrs_mirror'):
        points = quote.get('points')
        if not points:
            raise Failure('model row stores no Valve point totals')
        return valve_model(points)
    raise Failure('unknown method %r cannot be replayed' % (method,))


# --------------------------------------------------------------------------- #
# Side mapping
# --------------------------------------------------------------------------- #
def label_matches(fixture_label, source_label, aliases):
    """True when a quote label can only mean this fixture's team."""
    a, b = norm(fixture_label), norm(source_label)
    if not a or not b:
        return False
    if a == b:
        return True
    wa, wb = words(fixture_label), words(source_label)
    if wa and wb and (wa == wb[:len(wa)] if len(wa) <= len(wb) else wb == wa[:len(wb)]):
        # A whole-word prefix such as "LPH" for "LPH Gaming" is a label variant,
        # not a fuzzy guess; "Academy" sides are only ever matched inside the
        # same quote, and an ambiguous pairing fails closed below.
        return True
    for record in aliases:
        names = {norm(n) for n in record.get('names', [])}
        names.add(norm(record.get('canonical')))
        if a in names and b in names:
            return True
    return False


def mapping(fixture_teams, source_teams, aliases):
    """Unique permutation fixture->source, or a Failure when it is ambiguous."""
    if len(source_teams) != 2 or len(fixture_teams) != 2:
        raise Failure('expected two labels on each side')
    forward = [label_matches(f, s, aliases) for f in fixture_teams for s in source_teams]
    matches = [[label_matches(f, s, aliases) for s in source_teams] for f in fixture_teams]
    direct = matches[0][0] and matches[1][1] and not (matches[0][1] and matches[1][0])
    swapped = matches[0][1] and matches[1][0] and not (matches[0][0] and matches[1][1])
    if direct:
        return (0, 1)
    if swapped:
        return (1, 0)
    if all(any(row) for row in matches) and sum(sum(row) for row in matches) == 2:
        # Exactly one admissible pairing exists; use it.
        return (0, 1) if matches[0][0] else (1, 0)
    del forward
    raise Failure('quote labels %r do not map uniquely onto %r' % (source_teams, fixture_teams))


# --------------------------------------------------------------------------- #
# Row checks
# --------------------------------------------------------------------------- #
class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.checks = 0

    def check(self, condition, code, message):
        self.checks += 1
        if not condition:
            self.errors.append({'code': code, 'message': message})
        return bool(condition)

    def warn(self, condition, code, message):
        self.checks += 1
        if not condition:
            self.warnings.append({'code': code, 'message': message})
        return bool(condition)


def audit_rows(data, aliases, report):
    matches = data.get('matches') or []
    report.check(bool(matches), 'board.empty', 'the snapshot contains no fixture rows')
    ids = [str(m.get('id')) for m in matches]
    report.check(len(ids) == len(set(ids)), 'board.duplicate_ids', 'duplicate Hotspawn fixture ids')
    counts = Counter(m.get('state') for m in matches)
    open_rows = [m for m in matches if m.get('state') == 'open']
    priced = [m for m in open_rows if m.get('probabilities') is not None]
    picked = [m for m in open_rows if m.get('pick')]
    unresolved = [m for m in open_rows if not m.get('pick')]

    for m in matches:
        mid = str(m.get('id'))
        teams = m.get('teams') or []
        report.check(len(teams) == 2 and all(str(t).strip() for t in teams) and norm(teams[0]) != norm(teams[1]),
                     'row.teams', f'{mid}: two distinct team labels are required, got {teams!r}')
        try:
            start = parse_time(m.get('start'))
        except (TypeError, ValueError):
            start = None
        report.check(start is not None, 'row.start', f'{mid}: unparseable UTC start {m.get("start")!r}')
        source_url = m.get('source_url') or ''
        report.check(official(source_url) and host(source_url) in HOTSPAWN_HOSTS,
                     'row.official_source', f'{mid}: no official Hotspawn source link ({source_url!r})')
        feed_url = m.get('feed_url') or ''
        report.check(host(feed_url) in HOTSPAWN_HOSTS | HOTSPAWN_API_HOSTS, 'row.feed_source',
                     f'{mid}: no official Hotspawn feed link ({feed_url!r})')
        report.check(m.get('state') in ('open', 'not_open'), 'row.state',
                     f'{mid}: unknown state {m.get("state")!r}')

        method = m.get('method')
        probs = m.get('probabilities')
        pick = m.get('pick')
        if method is not None:
            report.check(method in ALL_METHODS, 'row.method', f'{mid}: unknown method {method!r}')
        if pick is not None:
            report.check(pick in teams, 'row.pick_not_in_fixture',
                         f'{mid}: pick {pick!r} is not one of {teams!r}')
        if probs is not None:
            report.check(len(probs) == 2, 'row.probability_pair', f'{mid}: probabilities are not a pair')
            if len(probs) == 2:
                total = float(probs[0]) + float(probs[1])
                report.check(abs(total - 1.0) <= TOL, 'row.probability_sum',
                             f'{mid}: probabilities sum to {total!r}, not 1')
                favourite = teams[0] if probs[0] > probs[1] else (teams[1] if probs[1] > probs[0] else None)
                report.check(pick == favourite, 'row.pick_follows_probability',
                             f'{mid}: pick {pick!r} is not the higher-probability side ({favourite!r})')
                fair = m.get('fair_odds')
                if fair is not None:
                    report.check(all(abs(float(f) - 1 / float(p)) <= 1e-6 for f, p in zip(fair, probs)),
                                 'row.fair_odds', f'{mid}: fair odds are not 1/probability')
            report.check(method in PRICED_METHODS, 'row.method_priced',
                         f'{mid}: a priced row must carry a priced method, got {method!r}')
            evidence = m.get('evidence') or []
            report.check(len(evidence) >= 1, 'row.evidence', f'{mid}: priced row stores no evidence')
            if evidence:
                quote = evidence[0]
                provider = str(quote.get('provider') or '')
                report.check('hotspawn' not in provider.lower(), 'row.provider_hotspawn',
                             f'{mid}: probability provider is Hotspawn ({provider!r})')
                report.check(official(quote.get('url') or quote.get('api_url') or ''),
                             'row.provider_official', f'{mid}: price source is not on the official allowlist')
                try:
                    replayed = replay(m, quote)
                except Failure as exc:
                    replayed = None
                    report.check(False, 'row.replay', f'{mid}: {exc}')
                if replayed is not None:
                    labels = quote.get('source_teams') or teams
                    try:
                        order = mapping(teams, labels, aliases)
                    except Failure as exc:
                        order = None
                        report.check(False, 'row.side_mapping', f'{mid}: {exc}')
                    if order is not None:
                        ordered = [replayed[order[0]], replayed[order[1]]]
                        report.check(all(abs(a - float(b)) <= TOL for a, b in zip(ordered, probs)),
                                     'row.replay_mismatch',
                                     f'{mid}: stored {probs!r} != replayed {ordered!r} from {quote.get("provider")!r}')
        else:
            report.check(method is None, 'row.method_without_probability',
                         f'{mid}: method {method!r} is set without a probability')
            report.check(m.get('fair_odds') is None, 'row.fair_without_probability',
                         f'{mid}: fair odds are set without a probability')
        if m.get('state') == 'open':
            report.check(bool(pick), 'coverage.open_without_pick',
                         f'{mid}: open fixture publishes no pick and no limitation row')
            if pick:
                report.check(method is not None, 'coverage.pick_without_method',
                             f'{mid}: pick {pick!r} has no recorded method')
                if probs is None:
                    report.check(method in UNPRICED_PICK_METHODS, 'coverage.unpriced_method',
                                 f'{mid}: unpriced pick must be a documented research tier, got {method!r}')
                    report.check(str(m.get('reason') or '').strip() != '', 'coverage.limitation',
                                 f'{mid}: unpriced pick must state its limitation')
            if not pick:
                report.check(str(m.get('reason') or '').strip() != '', 'coverage.unresolved_reason',
                             f'{mid}: unresolved row must state why')
                attempts = m.get('attempts') or []
                report.check(bool(attempts), 'coverage.unresolved_attempts',
                             f'{mid}: unresolved row must list the sources it tried')
                for attempt in attempts:
                    report.check(official(attempt.get('url') or ''), 'coverage.attempt_url',
                                 f'{mid}: source attempt without an official URL: {attempt.get("provider")!r}')
                    report.check(str(attempt.get('status') or '').strip() != '', 'coverage.attempt_status',
                                 f'{mid}: source attempt without a status: {attempt.get("provider")!r}')
        else:
            report.check(pick is None, 'closed.pick', f'{mid}: a non-open row must not publish a pick')
            report.check(probs is None, 'closed.probability',
                         f'{mid}: a non-open row must not publish a probability')
            report.check(str(m.get('reason') or '').strip() != '', 'closed.reason',
                         f'{mid}: a non-open row must state why it carries no pick')

    # One market cannot price two different fixtures: a reused quote id would
    # silently copy one match's probabilities onto another.
    seen = {}
    for m in matches:
        for quote in (m.get('evidence') or [])[:1]:
            key = str(quote.get('id') or '')
            if not key:
                continue
            if key in seen and seen[key] != str(m.get('id')):
                report.check(False, 'row.quote_reused',
                             f'{key}: quote is used for both {seen[key]} and {m.get("id")}')
            seen[key] = str(m.get('id'))
            quoted_start = quote.get('start')
            if quoted_start:
                try:
                    delta = abs((parse_time(quoted_start) - parse_time(m.get('start'))).total_seconds())
                except (TypeError, ValueError):
                    delta = None
                report.check(delta is not None and delta <= 60, 'row.quote_start',
                             f'{m.get("id")}: quote start {quoted_start!r} differs from the fixture start {m.get("start")!r}')

    declared = data.get('coverage_counts') or {}
    report.check(declared.get('retained', len(matches)) == len(matches), 'counts.retained',
                 f'coverage_counts.retained={declared.get("retained")} but {len(matches)} rows are published')
    report.check(declared.get('api', len(matches)) == len(matches), 'counts.api',
                 'coverage_counts.api does not match the published row count')
    coverage = data.get('coverage') or {}
    for source, count in (coverage.items() if isinstance(coverage, dict) else []):
        report.check(count == len(matches), 'counts.coverage',
                     f'coverage[{source!r}]={count} does not match {len(matches)} rows')
    return {
        'rows': len(matches),
        'open': len(open_rows),
        'open_picked': len(picked),
        'open_priced': len(priced),
        'open_unpriced_pick': len([m for m in open_rows if m.get('pick') and m.get('probabilities') is None]),
        'open_unresolved': len(unresolved),
        'not_open': len(matches) - len(open_rows),
        'states': dict(counts),
        'methods': dict(Counter(m.get('method') for m in open_rows)),
    }


# --------------------------------------------------------------------------- #
# Built-page checks
# --------------------------------------------------------------------------- #
class Anchors(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])
        if tag == 'tr' and attrs.get('data-match'):
            self.rows.append(attrs['data-match'])


def page_rows(html_text):
    """Split the document into {fixture id: row markup} using data-match attributes."""
    blocks = {}
    for chunk in re.split(r'(?=<tr\b)', html_text):
        m = re.search(r'data-match="([^"]+)"', chunk)
        if m:
            blocks.setdefault(m.group(1), '')
            blocks[m.group(1)] += chunk
            # Trim at the next </tr> so a block cannot absorb its neighbours.
            cut = chunk.find('</tr>')
            if cut >= 0:
                blocks[m.group(1)] = chunk[:cut]
    return blocks


def audit_site(data, site, report):
    site = Path(site)
    parsed = {}
    pages = {name: (site / name).read_text() for name in
             ('index.html', 'picks.html', 'matches.html', 'unresolved.html', 'review.html')}
    parsers = {}
    for name, text in pages.items():
        p = Anchors()
        p.feed(text)
        parsers[name] = p

    matches = data['matches']
    match_rows = page_rows(pages['matches.html'])
    pick_rows = page_rows(pages['picks.html'])
    unresolved_rows = page_rows(pages['unresolved.html'])
    summary_rows = page_rows(pages['index.html'])

    report.check(len(match_rows) == len(matches), 'site.matches_rows',
                 f'matches.html renders {len(match_rows)} data-match rows for {len(matches)} fixtures')
    for m in matches:
        mid = str(m['id'])
        row = match_rows.get(mid)
        if not report.check(row is not None, 'site.row_missing', f'{mid}: absent from matches.html'):
            continue
        hrefs = re.findall(r'href="([^"]+)"', row)
        report.check(any(host(h) in HOTSPAWN_HOSTS for h in hrefs), 'site.row_source',
                     f'{mid}: matches.html row has no official Hotspawn link')
        report.check(any(official(h) for h in hrefs), 'site.row_official',
                     f'{mid}: matches.html row has no official source link')
        report.check(f'evidence.html#match-{mid}' in row, 'site.row_evidence',
                     f'{mid}: matches.html row does not link its evidence')
        if m.get('state') == 'open':
            prows = pick_rows.get(mid)
            if report.check(prows is not None, 'site.pick_missing', f'{mid}: open row absent from picks.html'):
                if m.get('pick'):
                    text = re.sub(r'<[^>]+>', ' ', prows)
                    report.check(m['pick'] in text, 'site.pick_team',
                                 f'{mid}: pick {m["pick"]!r} is not printed on picks.html')
                if m.get('probabilities'):
                    for team, p in zip(m['teams'], m['probabilities']):
                        label = f'{team} {p * 100:.1f} percent'
                        report.check(label in prows, 'site.pick_label',
                                     f'{mid}: picks.html omits aria-label {label!r}')
        if m.get('state') == 'open' and not m.get('pick'):
            report.check(mid in unresolved_rows, 'site.unresolved_missing',
                         f'{mid}: unresolved fixture is absent from unresolved.html')
            report.check(mid in summary_rows, 'site.summary_unresolved_missing',
                         f'{mid}: unresolved fixture is absent from the executive summary')
    report.check('unresolved-picks' in parsers['index.html'].ids, 'site.summary_section',
                 'the executive summary has no #unresolved-picks section')
    report.check('exec-banner' in parsers['index.html'].ids, 'site.summary_banner',
                 'the executive summary has no #exec-banner')
    for anchor in ('picks.html', 'unresolved.html', 'matches.html'):
        report.check(anchor in parsers['index.html'].links, 'site.summary_link',
                     f'the executive summary does not link {anchor}')

    # Internal navigation: every local href resolves, and every fragment exists.
    for name, parser in parsers.items():
        for href in parser.links:
            if href.startswith(('http://', 'https://', 'mailto:', '#')) or href.startswith('data:'):
                if href.startswith('#') and href[1:] and href[1:] not in parser.ids:
                    report.check(False, 'site.fragment', f'{name}: #{href[1:]} does not exist on the page')
                continue
            target, _, fragment = href.partition('#')
            target = target.split('?', 1)[0]
            path = (site / unquote(target)).resolve()
            if not report.check(path.is_file(), 'site.link', f'{name}: {href} does not resolve'):
                continue
            if fragment and path.suffix == '.html':
                target_parser = parsers.get(path.name)
                if target_parser is None:
                    target_parser = parsed.get(path)
                    if target_parser is None:
                        target_parser = Anchors()
                        target_parser.feed(path.read_text())
                        parsed[path] = target_parser
                report.check(fragment in target_parser.ids, 'site.fragment',
                             f'{name}: {href} points at a missing anchor')


# --------------------------------------------------------------------------- #
def audit(data, site=None, identities=None):
    report = Report()
    aliases = (identities or {}).get('aliases', [])
    counts = audit_rows(data, aliases, report)
    if site:
        audit_site(data, site, report)
    # The board must never look fresher than it is: a build with no snapshot
    # clock cannot prove anything, so refuse it rather than trusting the rows.
    report.check(str(data.get('fixtures_observed_at') or '').strip() != '', 'snapshot.observed',
                 'the snapshot has no fixture observation time')
    report.check(str(data.get('generated_at') or '').strip() != '', 'snapshot.generated',
                 'the snapshot has no generation time')
    if data.get('fixtures_observed_at') and data.get('generated_at'):
        report.check(parse_time(data['fixtures_observed_at']) <= parse_time(data['generated_at']),
                     'snapshot.clock_order', 'fixtures_observed_at is later than generated_at')
    return {'counts': counts, 'checks': report.checks,
            'errors': report.errors, 'warnings': report.warnings}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('data', nargs='?', default='data/latest.json')
    parser.add_argument('--site', default=None, help='built site directory to cross-check')
    parser.add_argument('--identities', default='data/identities.json')
    parser.add_argument('--output', default=None)
    parser.add_argument('--markdown', default=None)
    args = parser.parse_args(argv)
    data = json.loads(Path(args.data).read_text())
    identities = json.loads(Path(args.identities).read_text()) if Path(args.identities).is_file() else {'aliases': []}
    result = audit(data, args.site, identities)
    result['audited_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    result['data'] = str(args.data)
    result['site'] = str(args.site) if args.site else None
    payload = json.dumps(result, indent=1, ensure_ascii=False)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(payload + '\n')
    print(f"checks: {result['checks']}  errors: {len(result['errors'])}  warnings: {len(result['warnings'])}")
    c = result['counts']
    print(f"rows: {c['rows']}  open: {c['open']}  picked: {c['open_picked']}  priced: {c['open_priced']}  "
          f"unpriced picks: {c['open_unpriced_pick']}  unresolved: {c['open_unresolved']}")
    for item in result['errors']:
        print('ERROR', item['code'], item['message'])
    for item in result['warnings'][:20]:
        print('WARN ', item['code'], item['message'])
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        lines = ['# Independent board audit — session 2c7b9e48', '',
                 f"Audited `{args.data}`" + (f" against `{args.site}`" if args.site else '') + '.', '',
                 f"- Checks executed: **{result['checks']}**",
                 f"- Errors: **{len(result['errors'])}**",
                 f"- Warnings: **{len(result['warnings'])}**", '',
                 '| Measure | Value |', '| --- | --- |']
        for key, value in c.items():
            lines.append(f'| {key} | {value} |')
        if result['errors']:
            lines += ['', '## Errors', ''] + [f"- `{e['code']}` — {e['message']}" for e in result['errors']]
        if result['warnings']:
            lines += ['', '## Warnings (review queue)', ''] + [f"- `{w['code']}` — {w['message']}" for w in result['warnings']]
        Path(args.markdown).write_text('\n'.join(lines) + '\n')
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
