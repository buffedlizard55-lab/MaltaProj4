"""Read-only provenance audit. Never fetch, price, or change a match.

The existing independent C6 auditor replays source fields and calculations.
This supplementary check follows each accepted line back to a successful,
matching HTTP receipt and distinguishes an operator's own quote from a listing
or ranking mirror. An HTTPS bookmaker link alone does not verify a price.

Default clock = snapshot generation time, for reproducible archival review.
Pass --now to review present availability. Neither mode renews any evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REPO = '/ValveSoftware/counter-strike_regional_standings/'
FEED = ('https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures'
        '?sport_alias=cs2&status=scheduled&tenantId=1')
HLTV_STEPS = {'HLTV', 'HLTV team pages', 'HLTV lineup receipt'}
BOOK_STEPS = {'Pinnacle', 'Book research', 'Book listing re-observation',
              'Book listing gap recheck', 'Thunderpick', 'GG.BET',
              'Thunderpick (via BO3.gg API)'}
TTL = timedelta(hours=8)


def moment(value):
    if not isinstance(value, str):
        raise ValueError('ISO timestamp required')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timezone required')
    return result.astimezone(timezone.utc)


def secure_url(value, hosts=None):
    """Exact authority checks: no userinfo, lookalike suffixes, or other ports."""
    try:
        url = urlsplit(value)
        return (url.scheme == 'https' and bool(url.hostname)
                and url.username is None and url.password is None
                and url.port in (None, 443) and not url.fragment
                and (hosts is None or url.hostname in hosts))
    except (ValueError, TypeError, AttributeError):
        return False


def valve_url(value):
    return (secure_url(value, {'github.com', 'raw.githubusercontent.com'})
            and urlsplit(value).path.startswith(REPO))


def source_kind(quote):
    """Classify the actual data endpoint, never the claimed bookmaker name."""
    provider, api, page = (quote.get(k) for k in ('provider', 'api_url', 'url'))
    if (provider == 'Polymarket' and secure_url(api, {'gamma-api.polymarket.com'})
            and re.fullmatch(r'/markets/\d+', urlsplit(api).path)
            and secure_url(page, {'polymarket.com'})
            and urlsplit(page).path.startswith('/event/')):
        return 'operator_market'
    if (provider == 'Pinnacle'
            and secure_url(api, {'guest.api.arcadia.pinnacle.com'})
            and urlsplit(api).path.startswith('/0.1/')
            and secure_url(page, {'www.pinnacle.com', 'pinnacle.com'})):
        return 'operator_market'
    if provider == 'Valve VRS model' and valve_url(api) and valve_url(page):
        return 'official_input_model'
    if (provider == 'HLTV Valve ranking (Valve points)'
            and secure_url(api, {'www.hltv.org', 'hltv.org'}) and page == api
            and re.fullmatch(r'/valve-ranking/teams(?:/\d{4}/[a-z]+/\d{1,2})?', urlsplit(api).path)):
        return 'hltv_mirror_model'
    if (provider == 'Thunderpick (via BO3.gg API)'
            and secure_url(api, {'api.bo3.gg'})
            and urlsplit(api).path == '/api/v1/matches'
            and secure_url(page, {'bo3.gg'})
            and urlsplit(page).path.startswith('/matches/')):
        return 'third_party_listing'
    if (provider in {'EGamersWorld book listing', 'HLTV book listing'}
            and secure_url(api, {'egamersworld.com', 'www.egamersworld.com', 'www.hltv.org'})
            and secure_url(page, {'egamersworld.com', 'www.egamersworld.com', 'www.hltv.org'})):
        return 'third_party_listing'
    return 'unrecognized'


def receipt_ok(receipt):
    return (isinstance(receipt, dict) and receipt.get('status') == 'ok'
            and receipt.get('http_status') == 200
            and secure_url(receipt.get('url'))
            and re.fullmatch(r'[0-9a-f]{64}', str(receipt.get('sha256', ''))) is not None
            and type(receipt.get('bytes')) is int and receipt['bytes'] > 0)


def trace_quote(quote, checks):
    """Return trace problems; hashes bind declarations, not upstream truth."""
    own = quote.get('source_receipts') or []
    records = own or [c for c in checks if c.get('url') == quote.get('api_url')]
    successful = [r for r in records if receipt_ok(r)]
    if not successful:
        return ['No successful source receipt for accepted numeric evidence']
    problems = []
    for receipt in successful:
        same = [c for c in checks if c.get('url') == receipt.get('url')
                and c.get('observed_at') == receipt.get('observed_at')]
        if not any(receipt_ok(c) and c.get('sha256') == receipt.get('sha256')
                   and c.get('bytes') == receipt.get('bytes') for c in same):
            problems.append('Quote receipt does not match snapshot source-check hash/size/time')
    if not any(r.get('observed_at') == quote.get('observed_at') for r in successful):
        problems.append('Quote observation does not match a successful source observation')
    if quote.get('ranking_page_sha256') and not any(
            r.get('sha256') == quote['ranking_page_sha256'] for r in successful):
        problems.append('Ranking page hash does not match its successful HTTP receipt')
    # A forged operator label over an aggregator receipt must not gain primary status.
    kind = source_kind(quote)
    hosts = {
        'operator_market': ({'gamma-api.polymarket.com'} if quote.get('provider') == 'Polymarket'
                            else {'guest.api.arcadia.pinnacle.com'}),
        'official_input_model': {'raw.githubusercontent.com', 'api.github.com'},
        'hltv_mirror_model': {'www.hltv.org', 'hltv.org'},
        'third_party_listing': ({'api.bo3.gg'} if quote.get('provider') == 'Thunderpick (via BO3.gg API)'
                                else {'egamersworld.com', 'www.egamersworld.com', 'www.hltv.org'}),
    }.get(kind, set())
    if not all(secure_url(r.get('url'), hosts) for r in successful):
        problems.append('Accepted source receipt belongs to a different source authority')
    return problems


def archived_standings():
    """The existing unmodified, pinned Valve file; no new source is inferred."""
    try:
        meta = json.loads((ROOT / 'data/vrs/meta.json').read_text())
        name = meta['file']
        if Path(name).name != name or not valve_url(meta['raw_url']):
            return {}
        content = (ROOT / 'data/vrs' / name).read_bytes()
        if hashlib.sha256(content).hexdigest() != meta['sha256']:
            return {}
        return {meta['raw_url']: content}
    except (OSError, KeyError, TypeError, ValueError):
        return {}


def check_standings_inputs(quote, checks, documents):
    """Compare actual primary file rows, not just internally consistent numbers.

    A self-consistent fabricated point value passes arithmetic alone. Bind the
    file bytes to the recorded official HTTP response hash, then check the exact
    standing, name, points and roster for each side. Unknown files stay unknown.
    """
    content = documents.get(quote.get('api_url'))
    if content is None:
        return None, []
    digest = hashlib.sha256(content).hexdigest()
    if not any(receipt_ok(c) and c.get('url') == quote.get('api_url')
               and c.get('sha256') == digest for c in checks):
        return False, ['Official standings file hash does not match captured source receipt']
    problems, records = [], {}
    try:
        text = content.decode('utf-8')
        heading = re.search(r'Standings as of (\d{4})_(\d{2})_(\d{2})', text)
        if not heading or '-'.join(heading.groups()) != quote.get('standings_as_of'):
            problems.append('Official standings date differs from accepted model input')
        for line in text.splitlines():
            cells = [cell.strip() for cell in line.split('|')]
            if len(cells) >= 7 and cells[1].isdigit():
                standing = int(cells[1])
                if standing in records:
                    problems.append('Duplicate standing in primary file')
                records[standing] = (int(cells[2]), cells[3], [p.strip() for p in cells[4].split(',')])
        if len(records) < 50:
            problems.append('Official standings table did not parse completely')
        for index in (0, 1):
            expected = records.get(quote['standings'][index])
            actual = (quote['points'][index], quote['vrs_teams'][index], quote['rosters'][index])
            if expected != actual:
                problems.append('Model points/name/roster differ from official standings row for side ' + str(index + 1))
    except (UnicodeError, ValueError, KeyError, TypeError, IndexError):
        problems.append('Official standings inputs cannot be cross-checked')
    return not problems, problems


def independent_rows(snapshot):
    """Reuse the independent auditor, not any collector/selection function."""
    spec = importlib.util.spec_from_file_location('c6_e3fe9518', ROOT / 'verification-c6/audit_snapshot.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.inspect(snapshot)


def inspect(snapshot, now=None, standings_documents=None):
    at = moment(now or snapshot['generated_at'])
    checked, replay_errors = independent_rows(snapshot)
    checks = snapshot.get('source_checks') or []
    documents = archived_standings() if standings_documents is None else standings_documents
    rows, errors = [], list(replay_errors)
    for match, replay_problems in checked:
        problems, limitations = [], []
        official_inputs_crosschecked = None
        quote = (match.get('evidence') or [{}])[0]
        kind = source_kind(quote) if match.get('probabilities') is not None else (
            'research_only' if match.get('pick') else 'unresolved')
        if match.get('state') != 'open':
            kind = 'not_open'
        if not secure_url(match.get('source_url'), {'play.hotspawn.com', 'www.hotspawn.com', 'hotspawn.com'}):
            problems.append('Official Hotspawn HTTPS fixture link missing')
        if match.get('feed_url') != FEED:
            problems.append('Official scoped CS2 feed link changed')
        sources = match.get('fixture_sources') or []
        if not sources:
            problems.append('Fixture HTTP provenance missing')
        for source in sources:
            if not any(receipt_ok(c) and all(c.get(k) == source.get(k)
                       for k in ('url', 'observed_at', 'sha256')) for c in checks):
                problems.append('Fixture receipt does not match a successful source check')
        if kind not in {'not_open', 'unresolved', 'research_only'}:
            if kind == 'unrecognized':
                problems.append('Accepted provider and data endpoint are not a recognized pair')
            problems.extend(trace_quote(quote, checks))
        if kind == 'third_party_listing':
            limitations.append('Bookmaker odds are reported by a third-party listing, not directly confirmed on the operator; primary-only market estimate left blank.')
        if kind == 'hltv_mirror_model':
            limitations.append('Points are from HLTV\'s dated Valve-ranking mirror, not Valve\'s own standings file; this is an originated model, not betting odds.')
        if kind == 'official_input_model':
            official_inputs_crosschecked, source_problems = check_standings_inputs(quote, checks, documents)
            problems.extend(source_problems)
            if official_inputs_crosschecked is None:
                limitations.append('No independently parsed primary standings document was available to this auditor; input-file cross-check is unverified, not inferred.')
            limitations.append('Our originated calculation from dated Valve points, not a quoted or verified win probability; roster continuity and model calibration remain limitations.')
        if kind == 'operator_market':
            limitations.append('Calculated from one operator\'s captured prices, not a guarantee, bookmaker consensus, or independently calibrated forecast.')
        if match.get('method') == 'exchange_wide':
            limitations.append('Wide exchange spread: low-confidence fallback, not a featured strict quote.')
        if kind in {'official_input_model', 'hltv_mirror_model'}:
            for field, suffix in [('formula_source', '/model/fit.js'), ('calibration_source', '/modelfit.png')]:
                source = quote.get(field)
                if not valve_url(source) or not urlsplit(source).path.endswith(suffix):
                    problems.append('Model formula/calibration link is not the official Valve file')
                elif '/blob/main/' in source:
                    limitations.append('Model source link is mutable main rather than an immutable commit: ' + field)
        ladder = []
        if match.get('state') == 'open' and match.get('method') != 'exchange':
            attempts = match.get('attempts') or []
            hltv = [i for i, a in enumerate(attempts) if a.get('provider') in HLTV_STEPS]
            books = [i for i, a in enumerate(attempts) if a.get('provider') in BOOK_STEPS]
            if not hltv or not books or min(hltv) >= min(books):
                problems.append('Non-featured row lacks recorded HLTV-first then esportsbook attempts')
            ladder = [{'provider': a.get('provider'), 'status': a.get('status'),
                       'url': a.get('url'), 'reason': a.get('reason')} for a in attempts]
        if kind in {'research_only', 'unresolved'}:
            if not match.get('reason'):
                problems.append('Unpriced row has no explicit limitation')
            limitations.append(match.get('reason') or 'Unverified: no limitation recorded.')
        active = False
        try:
            deadlines = [moment(match['lock']), moment(match['start']), moment(snapshot['fixtures_observed_at']) + TTL]
            if match.get('expires_at'):
                deadlines.append(moment(match['expires_at']))
            if quote.get('observed_at'):
                deadlines.append(moment(quote['observed_at']) + TTL)
            if quote.get('updated_at'):
                deadlines.append(moment(quote['updated_at']) + TTL)
            active = (match.get('state') == 'open' and min(deadlines) > at
                      and at >= moment(snapshot['fixtures_observed_at']) - timedelta(minutes=5))
        except (KeyError, TypeError, ValueError):
            if match.get('state') == 'open':
                problems.append('Availability cannot be established from sourced timestamps')
        all_problems = list(dict.fromkeys(list(replay_problems) + problems))
        valid = not all_problems
        rows.append({'id': match['id'], 'teams': match['teams'], 'fixture_url': match.get('source_url'),
                     'evidence_url': 'evidence.html#match-' + str(match['id']),
                     'source_url': quote.get('api_url') or quote.get('url'),
                     'source_kind': kind, 'method': match.get('method'),
                     'official_standings_input_crosscheck': official_inputs_crosschecked,
                     'pick_at_snapshot': match.get('pick'),
                     'calculated_probability': match.get('probabilities') if valid else None,
                     'primary_only_market_estimate': (match.get('probabilities') if valid and kind == 'operator_market' else None),
                     'actionable_at_audit_clock': bool(active and valid and match.get('pick')),
                     'fallback_attempts': ladder, 'limitations': limitations,
                     'problems': all_problems})
        errors.extend(str(match['id']) + ': ' + problem for problem in problems)
    counts = Counter(row['source_kind'] for row in rows)
    return {'schema_version': 1, 'snapshot_generated_at': snapshot.get('generated_at'),
            'audit_clock': at.isoformat().replace('+00:00', 'Z'),
            'clock_basis': 'explicit' if now else 'snapshot_generation_time_not_live',
            'rows': rows, 'counts': dict(sorted(counts.items())),
            'actionable_at_audit_clock': sum(r['actionable_at_audit_clock'] for r in rows),
            'errors': list(dict.fromkeys(errors)),
            'scope': 'Retained-evidence provenance and independent arithmetic replay, not live upstream confirmation or forecast accuracy.'}


def markdown(result):
    def safe(value):
        return str(value or '').replace('|', '&#124;').replace('\n', ' ')
    def pct(values):
        return ' / '.join(f'{p:.1%}' for p in values) if values is not None else ''
    lines = ['# Independent source-provenance review', '',
             f"Snapshot: `{result['snapshot_generated_at']}`. Audit clock: `{result['audit_clock']}`.",
             f"Clock basis: `{result['clock_basis']}`. **This is a dated audit, not the live picks page.**", '',
             result['scope'], '',
             'Primary-only market estimate is OUR normalized calculation from operator-origin inputs, not an official forecast. ',
             'It stays blank for listings, mirrors, models, unresolved and invalid rows. Blank never means 50/50.', '',
             f"Rows: {len(result['rows'])}. Errors: {len(result['errors'])}. Categories: `{json.dumps(result['counts'], sort_keys=True)}`.", '',
             '| Official fixture | Teams | Source class | Calculated A / B | Primary-only market estimate A / B | Evidence | Limitations / errors |',
             '| --- | --- | --- | --- | --- | --- | --- |']
    for row in result['rows']:
        evidence = f"[Input]({row['source_url']})" if secure_url(row['source_url']) else ''
        lines.append('| [%s](%s) | %s | %s | %s | %s | %s | %s |' % (
            safe(row['id']), row['fixture_url'], safe(' / '.join(row['teams'])), row['source_kind'],
            pct(row['calculated_probability']), pct(row['primary_only_market_estimate']), evidence,
            safe('; '.join(row['limitations'] + row['problems']))))
    lines += ['', '## Non-featured fallback trail', '',
              'Only rows the featured strict-exchange route did not resolve are included below. ',
              'A failed/shell-only access attempt is not evidence that a bookmaker offers no odds.', '']
    for row in result['rows']:
        if not row['fallback_attempts']:
            continue
        lines += [f"### [{row['id']}]({row['fixture_url']}) — {safe(' / '.join(row['teams']))}", '']
        for attempt in row['fallback_attempts']:
            label = safe(attempt['provider'])
            if secure_url(attempt['url']):
                label = f"[{label}]({attempt['url']})"
            lines.append(f"- {label}: **{safe(attempt['status'])}** — {safe(attempt['reason'])}")
        lines.append('')
    if result['errors']:
        lines += ['## Errors', ''] + ['- ' + safe(x) for x in result['errors']]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT / 'data/latest.json')
    parser.add_argument('--out', type=Path, default=ROOT / 'runtime/provenance-e3fe9518')
    parser.add_argument('--now', help='Explicit timezone-aware ISO audit clock; never rewrites evidence')
    args = parser.parse_args(argv)
    raw = args.data.read_bytes()
    result = inspect(json.loads(raw), args.now)
    result['snapshot_sha256'] = hashlib.sha256(raw).hexdigest()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'source-audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    (args.out / 'source-audit.md').write_text(markdown(result))
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}, indent=2))
    return int(bool(result['errors']))


if __name__ == '__main__':
    raise SystemExit(main())
