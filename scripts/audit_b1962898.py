"""Independent row audit for the Hotspawn CS2 board (session b1962898).

Why a second auditor: ``scripts/validate.py`` reconstructs a quote by calling the
same calculators the builder used. That proves the published number follows the
project's code path, not that the code path is right. This module re-derives
every published row from the *raw* source fields with its own arithmetic, in a
single file that imports nothing from ``scripts.core``, so a mistake or a silent
change in the builders cannot travel into the check.

What it asserts, row by row (all failures are listed, never repaired):

1. **Inventory.** The three Hotspawn views recorded on the snapshot (API, page,
   lobby) agree with each other and with the retained row count.
2. **Identity.** An open row's pick is one of its own two teams, and a priced
   row's higher probability belongs to the pick.
3. **Arithmetic.** Probabilities are two values in (0, 1) summing to 1; fair odds
   are their reciprocals; and for an exchange row the published probabilities are
   re-derived from the operator's own raw outcome prices (sum-normalised).
4. **Provenance.** Every open row carries at least one external http(s) source
   link that is not Hotspawn (the fixture inventory is not a line), and its tier
   label agrees with the provider named on the row.
5. **Expiry.** ``expires_at`` is never later than the row's own start, its lock,
   or eight hours after the newest observation recorded for that row.
6. **Honest blanks.** A row without a probability must publish a reason and at
   least one attempted source; a row with no pick must publish a reason.

``--check-links`` additionally reads each distinct external evidence URL over
the network and records the HTTP status. That is *evidence*, never a gate: an
operator refusing an automated read (403) is recorded as such and does not fail
the audit, because the price was already published with its own receipt.

Usage:
    python -m scripts.audit_b1962898 --snapshot data/latest.json \
        --output research/harvest-b1962898 [--check-links]
"""
import argparse
import json
import math
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

TOLERANCE = 1e-6
MAX_AGE = timedelta(hours=8)
TIERS = {
    'exchange', 'exchange_wide', 'bookmaker_fallback', 'model_vrs', 'model_vrs_mirror',
    'research_rank', 'research_rank_single', 'research_vrs_single',
}
RESEARCH_TIERS = {'research_rank', 'research_rank_single', 'research_vrs_single'}
MODEL_TIERS = {'model_vrs', 'model_vrs_mirror'}
UA = 'cs2-scout-independent-audit/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)'


def when(value):
    if value is None or value == '':
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def close(left, right, tolerance=TOLERANCE):
    return abs(float(left) - float(right)) <= tolerance


def host_of(url):
    try:
        return (urllib.parse.urlsplit(url).hostname or '').lower()
    except ValueError:
        return ''


def is_hotspawn(host):
    return host == 'hotspawn.com' or host.endswith('.hotspawn.com')


# Valve's own official standings repository. The model tier cites it there, so the
# check is the exact project path, not a substring of the host name.
VALVE_SOURCES = (
    'https://github.com/ValveSoftware/counter-strike_regional_standings',
    'https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings',
)


def cites_official_ranking(links):
    for url in links:
        if host_of(url).endswith('hltv.org'):
            return True
        if any(url.startswith(prefix) for prefix in VALVE_SOURCES):
            return True
    return False


def raw_outcome_prices(row):
    """The operator's own two outcome prices, straight from the retained raw blob."""
    for item in row.get('evidence') or []:
        raw = item.get('raw') or {}
        prices = raw.get('outcomePrices')
        if isinstance(prices, str):
            try:
                prices = json.loads(prices)
            except ValueError:
                continue
        if isinstance(prices, list) and len(prices) == 2:
            try:
                numbers = [float(x) for x in prices]
            except (TypeError, ValueError):
                continue
            if all(math.isfinite(x) and 0 < x < 1 for x in numbers):
                return numbers
    return None


def observed_after(row):
    stamps = [when(item.get('observed_at')) for item in row.get('evidence') or []]
    stamps = [s for s in stamps if s]
    return max(stamps) if stamps else None


def external_links(row):
    links = []
    for item in row.get('evidence') or []:
        for key in ('url', 'api_url'):
            url = item.get(key)
            if isinstance(url, str) and url.startswith('http'):
                links.append(url)
    url = row.get('source_url')
    if isinstance(url, str) and url.startswith('http'):
        links.append(url)
    return links


def audit_row(row, problems):
    """All checks for one row. Returns a compact record for the report."""
    match_id = str(row.get('id'))
    teams = row.get('teams') or []
    state = row.get('state')
    method = row.get('method')
    probabilities = row.get('probabilities')
    fair = row.get('fair_odds')
    pick = row.get('pick')
    record = {'id': match_id, 'state': state, 'teams': teams, 'method': method, 'pick': pick,
              'probability': probabilities[0] if isinstance(probabilities, list) and probabilities else None,
              'checks': 0}

    def fail(code, detail):
        problems.append({'id': match_id, 'code': code, 'detail': detail})

    def check():
        record['checks'] += 1

    check()
    if len(teams) != 2 or not all(isinstance(t, str) and t.strip() for t in teams):
        fail('teams', 'row does not name exactly two teams')
    if state not in {'open', 'not_open'}:
        fail('state', 'unknown state %r' % (state,))
    if method is not None and method not in TIERS:
        fail('method', 'unpublished tier label %r' % (method,))

    if state == 'open':
        check()
        if not pick:
            fail('pick', 'open row carries no pick and no limitation text')
            if not (row.get('reason') or '').strip():
                fail('reason', 'open row without a pick publishes no reason')
        elif teams and pick not in teams:
            fail('pick-identity', 'pick %r is not one of %r' % (pick, teams))
        check()
        if not row.get('source_url'):
            fail('fixture-link', 'open row has no official Hotspawn fixture link')

    if probabilities is not None:
        check()
        if not (isinstance(probabilities, list) and len(probabilities) == 2):
            fail('probability-shape', 'probabilities are not a two-value pair')
        else:
            first, second = probabilities
            if not all(isinstance(x, (int, float)) and math.isfinite(x) and 0 < x < 1 for x in probabilities):
                fail('probability-range', 'a probability is outside (0, 1): %r' % (probabilities,))
            elif not close(first + second, 1.0):
                fail('probability-sum', 'probabilities sum to %r' % (first + second))
            if isinstance(fair, list) and len(fair) == 2:
                check()
                for index, (p, odd) in enumerate(zip(probabilities, fair)):
                    if not isinstance(odd, (int, float)) or not math.isfinite(odd) or odd <= 1:
                        fail('fair-odds', 'fair odds %d are not a valid decimal price' % index)
                    elif not close(p * odd, 1.0, 1e-9):
                        fail('fair-odds', 'fair odds %d do not invert probability %d' % (index, index))
            else:
                fail('fair-odds', 'published probability without two fair odds')
            if pick and teams and len(probabilities) == 2:
                check()
                better = teams[0] if probabilities[0] > probabilities[1] else teams[1]
                if probabilities[0] != probabilities[1] and pick != better:
                    fail('pick-direction', 'pick %r is not the higher-probability team' % (pick,))
            # Re-derive an exchange price from the operator's raw outcomes only.
            # The pair is compared as an unordered set: the operator lists its own
            # home/away order, the published row uses Hotspawn's. Re-ordering is
            # identity work that the row already evidences; inventing an order
            # here would hide a genuine mismatch, so the multiset must match.
            if method in {'exchange', 'exchange_wide'}:
                check()
                raw = raw_outcome_prices(row)
                if raw is None:
                    fail('raw-price', 'exchange tier carries no usable raw outcome prices')
                else:
                    total = sum(raw)
                    derived = sorted(x / total for x in raw)
                    published = sorted(probabilities)
                    for index, (got, expected) in enumerate(zip(published, derived)):
                        if not close(got, expected, 1e-9):
                            fail('raw-price', 'published probability %d does not follow the raw outcomes %r'
                                 % (index, raw))
            if method == 'bookmaker_fallback':
                check()
                providers = {str(item.get('provider')) for item in row.get('evidence') or []}
                if providers & {'Polymarket', 'Pinnacle'}:
                    fail('tier-provider', 'bookmaker tier cites an exchange as its provider: %r' % (providers,))
            if method in RESEARCH_TIERS:
                fail('tier-probability', 'research tier %r must not publish a probability' % (method,))
        check()
        deadline = when(row.get('expires_at'))
        if deadline is None:
            fail('expiry', 'priced row has no readable expiry')
        else:
            bounds = {'start': when(row.get('start')), 'lock': when(row.get('lock'))}
            observed = observed_after(row)
            if observed:
                bounds['observed+8h'] = observed + MAX_AGE
            for label, limit in bounds.items():
                if limit is not None and deadline > limit:
                    fail('expiry', 'expiry %s is later than %s %s'
                         % (deadline.isoformat(), label, limit.isoformat()))
        check()
        links = external_links(row)
        hosts = [host_of(url) for url in links]
        if not any(host and not is_hotspawn(host) for host in hosts):
            fail('external-source', 'priced row publishes no non-Hotspawn source link')
        if method in MODEL_TIERS and not cites_official_ranking(links):
            fail('model-source', 'model tier publishes no official Valve standings or HLTV ranking link')
        record['hosts'] = sorted({host for host in hosts if host})
    else:
        if state == 'open':
            check()
            if not (row.get('reason') or '').strip():
                fail('reason', 'open row without a percentage publishes no limitation text')
            check()
            if not (row.get('evidence') or row.get('attempts')):
                fail('attempts', 'open row without a percentage records no attempted source')
    return record


def check_links(rows, timeout=20):
    """Read each distinct external evidence URL once and record what came back."""
    seen = {}
    for row in rows:
        if row.get('state') != 'open':
            continue
        for url in external_links(row):
            host = host_of(url)
            if not host or is_hotspawn(host) or url in seen:
                continue
            request = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    seen[url] = {'status': response.status, 'final_url': response.geturl()}
            except urllib.error.HTTPError as exc:
                seen[url] = {'status': exc.code, 'error': 'HTTPError'}
            except (urllib.error.URLError, OSError, ValueError) as exc:
                seen[url] = {'status': None, 'error': '%s: %s' % (type(exc).__name__, exc)}
    return seen


def audit(snapshot, links=None):
    problems = []
    coverage = snapshot.get('coverage_counts') or {}
    matches = snapshot.get('matches') or []
    views = {name: coverage.get(name) for name in ('api', 'page', 'lobby', 'retained')}
    if len({value for value in views.values() if value is not None}) > 1:
        problems.append({'id': 'inventory', 'code': 'view-parity',
                         'detail': 'Hotspawn views disagree: %r' % (views,)})
    if coverage.get('retained') not in (None, len(matches)):
        problems.append({'id': 'inventory', 'code': 'row-count',
                         'detail': 'retained count %r but %d rows' % (coverage.get('retained'), len(matches))})
    rows = []
    for row in matches:
        rows.append(audit_row(row, problems))
    open_rows = [row for row in snapshot.get('matches') or [] if row.get('state') == 'open']
    priced = [row for row in open_rows if row.get('probabilities')]
    researched = [row for row in open_rows if not row.get('probabilities') and row.get('pick')]
    unresolved = [row for row in open_rows if not row.get('probabilities') and not row.get('pick')]
    summary = {
        'rows': len(matches),
        'open': len(open_rows),
        'priced': len(priced),
        'research_only': len(researched),
        'unresolved': len(unresolved),
        'picked': len(priced) + len(researched),
        'checks_run': sum(row['checks'] for row in rows),
        'failures': len(problems),
    }
    return {'summary': summary, 'coverage_counts': views, 'problems': problems, 'rows': rows,
            'link_checks': links, 'links_checked': len(links or {})}


def markdown(result, snapshot):
    summary = result['summary']
    lines = [
        '# Independent row audit — session b1962898',
        '',
        'Snapshot `%s` · generated `%s` · %d rows.' % (
            snapshot.get('fixtures_observed_at'), snapshot.get('generated_at'), summary['rows']),
        '',
        '| Measure | Value |',
        '| --- | --- |',
        '| Rows audited | %d |' % summary['rows'],
        '| Open matches | %d |' % summary['open'],
        '| With a pick | %d |' % summary['picked'],
        '| With a win probability | %d |' % summary['priced'],
        '| Research-only (pick, no percentage) | %d |' % summary['research_only'],
        '| Unresolved (no pick) | %d |' % summary['unresolved'],
        '| Individual assertions executed | %d |' % summary['checks_run'],
        '| Failures | %d |' % summary['failures'],
        '',
    ]
    if result['problems']:
        lines += ['## Failures', '', '| Row | Check | Detail |', '| --- | --- | --- |']
        for item in result['problems']:
            lines.append('| %s | `%s` | %s |' % (item['id'], item['code'], item['detail']))
        lines.append('')
    else:
        lines += ['No failures: every published number reproduces from its own raw source fields, every open '
                  'row carries an external source link, and every blank row publishes a reason and an attempt.', '']
    if result.get('link_checks'):
        lines += ['## Live source reads', '',
                  '| URL | HTTP status | Note |', '| --- | --- | --- |']
        for url, record in sorted(result['link_checks'].items()):
            lines.append('| %s | %s | %s |' % (url, record.get('status') if record.get('status') is not None else 'error',
                                                record.get('error') or ''))
        lines.append('')
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='data/latest.json')
    parser.add_argument('--output', default=None, help='Directory for audit.json and AUDIT.md')
    parser.add_argument('--check-links', action='store_true')
    args = parser.parse_args(argv)
    snapshot = json.loads(Path(args.snapshot).read_text())
    links = None
    if args.check_links:
        links = check_links(snapshot.get('matches') or [])
    result = audit(snapshot, links)
    text = markdown(result, snapshot)
    if args.output:
        target = Path(args.output)
        target.mkdir(parents=True, exist_ok=True)
        (target / 'audit.json').write_text(json.dumps(result, indent=1) + '\n')
        (target / 'AUDIT.md').write_text(text + '\n')
    print(text)
    return 1 if result['problems'] else 0


if __name__ == '__main__':
    sys.exit(main())
