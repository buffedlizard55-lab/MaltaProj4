"""Compare the official lobby, CS2 page and scoped API without dropping rows."""
import copy
import json
import time
from pathlib import Path
from urllib.parse import urlsplit
from scripts.core import HOTSPAWN, FIXTURES, dt, iso, hotspawn_state, normalize_fixtures

INVENTORY_RECEIPTS = Path(__file__).resolve().parents[1] / 'data' / 'inventory-receipts.json'

LOBBY = 'https://play.hotspawn.com/lobby'
FACT_FIELDS = (
    'participants0_name', 'participants1_name', 'participants0_id', 'participants1_id',
    'scheduled_start_time', 'lock_time', 'end_time', 'status',
    'competition_name', 'competition_id', 'tier', 'best_of',
)


def problem(code, message, source):
    return {'code': code, 'message': message, 'source': source}


def checked_rows(rows):
    if not isinstance(rows, list):
        raise ValueError('Expected a complete array; changed pagination/schema needs review')
    if any(not isinstance(r, dict) or r.get('id') is None or not str(r['id']).strip() for r in rows):
        raise ValueError('Malformed fixture object or missing ID')
    cs2 = [r for r in rows if r.get('sport_alias') == 'cs2']
    if rows and not cs2:
        raise ValueError('Nonempty fixture response contains no CS2 rows; scope drift is not an empty lobby')
    if len({str(r['id']) for r in cs2}) != len(cs2):
        raise ValueError('Duplicate CS2 fixture IDs; complete coverage unverified')
    return cs2


def retained(previous, now, source_log, flags):
    if previous is None:
        raise RuntimeError('No usable Hotspawn snapshot; refuse to publish an invented empty inventory')
    data = copy.deepcopy(previous)
    data.update(last_attempt_at=iso(now), coverage='stale', source_checks=source_log,
                issues=flags + [problem('retained', 'Last successful inventory retained. This attempt did not establish a current complete list; original evidence times are unchanged.', HOTSPAWN)])
    return {'retained': data}


# Measured on 2026-10-22: at 01:22:32Z the publication runner was answered with a
# non-JSON body from the fixtures API *and* with both lobby pages missing their
# `ng-state` hydration block, seven minutes after the same three URLs returned a
# complete 97-fixture inventory (run 39704142204, 01:11Z). One DNS/CDN edge or a
# short challenge window can therefore cost a whole publication slot and leave the
# board on a four-hour-old retained snapshot. When *nothing* usable comes back, the
# three views are re-read once after a wait and both reads stay in the evidence log;
# a host that keeps refusing is still blocked, and a second failure retains the last
# good inventory exactly as before.
DISCOVERY_RETRY_WAITS = (20.0,)

SOURCES = (
    ('api', 'Hotspawn CS2 fixtures', FIXTURES, True),
    ('page', 'Hotspawn CS2 lobby', HOTSPAWN, False),
    ('lobby', 'Hotspawn general lobby', LOBBY, False),
)


def _read_sources(src, flags, snapshots, links, now):
    for key, name, url, json_response in SOURCES:
        try:
            payload, receipt = src.get(name, url, json_response)
            if json_response:
                rows = payload
            else:
                rows, page_links = hotspawn_state(payload)
                links.update({str(k): v for k, v in page_links.items() if v})
            rows = checked_rows(rows)
            # Validate each source on its own before considering union/parity.
            normalize_fixtures(rows, {}, now)
            snapshots.append({'key': key, 'url': url, 'rows': rows, 'receipt': receipt})
        except (ValueError, KeyError, TypeError, OverflowError, AttributeError) as exc:
            flags.append(problem(key, str(exc), url))


def load_inventory_receipts(path=None):
    """Read reviewed inventory exceptions; malformed JSON is never silent."""
    document = json.loads(Path(path or INVENTORY_RECEIPTS).read_text())
    if not isinstance(document, dict) or document.get('schema_version') != 1 \
            or not isinstance(document.get('receipts'), list):
        raise ValueError('Unrecognized reviewed inventory receipt schema')
    return document['receipts']


def validate_inventory_receipt(review):
    """Validate an exact-row exception before it can cause a network read."""
    if not isinstance(review, dict):
        raise ValueError('Inventory receipt is not an object')
    required = ('fixture_id', 'teams', 'start', 'api_url', 'match_url', 'listed_url',
                'reviewed_at', 'valid_from', 'valid_until', 'basis')
    missing = [key for key in required if review.get(key) in (None, '')]
    if missing:
        raise ValueError('Inventory receipt missing: ' + ', '.join(missing))
    forbidden = {'pick', 'probabilities', 'fair_odds', 'method', 'evidence'} & set(review)
    if forbidden:
        raise ValueError('Inventory receipt cannot supply pick/probability fields: ' + ', '.join(sorted(forbidden)))
    ident = str(review['fixture_id'])
    if not ident.strip():
        raise ValueError('Inventory receipt fixture ID is blank')
    teams = review['teams']
    if not isinstance(teams, list) or len(teams) != 2 \
            or any(not isinstance(team, str) or not team.strip() for team in teams) \
            or len(set(teams)) != 2:
        raise ValueError('Inventory receipt needs two distinct team labels')
    for key, host in (('api_url', 'phpstack-1372681-6459848.cloudwaysapps.com'),
                      ('match_url', 'www.hotspawn.com'), ('listed_url', 'play.hotspawn.com')):
        parsed = urlsplit(review[key])
        if parsed.scheme != 'https' or parsed.netloc != host:
            raise ValueError('Inventory receipt has an unofficial ' + key)
    if urlsplit(review['api_url']).path != '/api/v1/fixtures':
        raise ValueError('Inventory supplement must query the official fixtures API')
    iso(review['start'])
    iso(review['reviewed_at'])
    if not dt(review['valid_from']) < dt(review['valid_until']):
        raise ValueError('Inventory receipt validity interval is empty')
    if not str(review['basis']).strip():
        raise ValueError('Inventory receipt needs a review basis')
    return ident


def reviewed_supplements(src, now, snapshots, links, flags, receipts):
    """Union only exact, currently eligible rows from reviewed official queries.

    A receipt is a bounded response to a measured upstream inventory mismatch,
    not a second source of picks. The whole competition response is schema
    checked, then exactly the registered ID is selected and its pair/start must
    match the review. Any failure makes coverage partial instead of silently
    restoring a false parity claim.
    """
    added, failed = {}, []
    primary_ids = [{str(row['id']) for row in source['rows']} for source in snapshots]
    for review in receipts:
        ident = str((review or {}).get('fixture_id') or 'unknown')
        try:
            ident = validate_inventory_receipt(review)
            if not dt(review['valid_from']) <= now < dt(review['valid_until']):
                continue
            # Once every primary view returns the row, the exception is unnecessary.
            if len(primary_ids) == 3 and all(ident in ids for ids in primary_ids):
                continue
            payload, source_receipt = src.get('Hotspawn reviewed inventory supplement ' + ident,
                                              review['api_url'], True)
            rows = checked_rows(payload)
            selected = [row for row in rows if str(row['id']) == ident]
            if len(selected) != 1:
                raise ValueError('official competition response does not contain exactly one registered row')
            row = selected[0]
            if [row.get('participants0_name'), row.get('participants1_name')] != review['teams']:
                raise ValueError('team pair differs from the reviewed receipt')
            if iso(row.get('scheduled_start_time')) != iso(review['start']):
                raise ValueError('UTC start differs from the reviewed receipt')
            normalize_fixtures([row], {}, now)
            snapshots.append({'key': 'reviewed-supplement-' + ident, 'url': review['api_url'],
                              'rows': [row], 'receipt': source_receipt})
            links[ident] = review['match_url']
            added[ident] = review
            flags.append(problem('reviewed_inventory_supplement', review['basis'], review['listed_url']))
        except (ValueError, KeyError, TypeError, OverflowError, AttributeError) as exc:
            failed.append(ident)
            flags.append(problem('inventory_supplement',
                                 'Reviewed fixture %s could not be revalidated: %s' % (ident, exc),
                                 (review or {}).get('api_url') or HOTSPAWN))
    return added, failed


def discover(src, now, previous=None, receipts=None):
    flags, snapshots, links = [], [], {}
    receipts = load_inventory_receipts() if receipts is None else receipts
    # The API is the primary field representation. HTML sources add any missing
    # IDs and independently expose conflicts, rather than silently overwriting it.
    _read_sources(src, flags, snapshots, links, now)
    # The real refresh reader opts in (scripts.refresh.Sources sets this from
    # DISCOVERY_RETRY_WAITS); a test or a probe with a stub reader stays single-pass.
    waits = getattr(src, 'discovery_retry_waits', ())
    for index, wait in enumerate(waits):
        if snapshots:
            break
        flags.append(problem('discovery_retry',
                             'No usable Hotspawn view on the first read; re-reading the same three URLs after %gs. '
                             'Both reads are in the source log.' % wait, HOTSPAWN))
        time.sleep(wait)
        # A refused host stays refused: only the views that were not blocked are retried.
        _read_sources(src, flags, snapshots, links, now)
    if not snapshots:
        return retained(previous, now, src.log, flags)
    primary_count = len(snapshots)
    supplements, supplement_failures = reviewed_supplements(
        src, now, snapshots, links, flags, receipts)
    sets = [{str(r['id']) for r in s['rows']} for s in snapshots]
    complete = (primary_count == 3 and not supplements and not supplement_failures
                and all(ids == sets[0] for ids in sets))
    raw, provenance, conflicts = {}, {}, []
    observations = [s['receipt']['observed_at'] for s in snapshots]
    for source in snapshots:
        receipt = {k: v for k, v in source['receipt'].items()
                   if k in ('observed_at', 'sha256', 'cache_age_seconds', 'retrieved_at')}
        receipt['url'] = source['url']
        for row in source['rows']:
            ident = str(row['id'])
            if ident not in raw:
                raw[ident] = row
                provenance[ident] = [receipt]
            else:
                differences = {field: {'primary': raw[ident].get(field), 'comparison': row.get(field)}
                               for field in FACT_FIELDS if raw[ident].get(field) != row.get(field)}
                provenance[ident].append(receipt)
                if differences:
                    conflicts.append({'id': ident, 'primary_source': provenance[ident][0]['url'],
                                      'comparison_source': source['url'], 'differences': differences})
    if conflicts:
        complete = False
        flags.append(problem('fixture_conflicts', f'{len({c["id"] for c in conflicts})} fixtures have conflicting official fields. Values are shown as reported by the primary source; picks withheld for those rows.', HOTSPAWN))
    if not complete:
        sizes = ', '.join(f'{s["key"]}: {len(s["rows"])}' for s in snapshots)
        detail = (f'{primary_count}/3 primary sources usable; {len(supplements)} reviewed supplement(s); '
                  f'{len(supplement_failures)} supplement failure(s)')
        flags.append(problem('coverage_difference', f'Current lobby parity is unverified ({sizes}; {detail}). Union retained, no missing-source result treated as an empty lobby.', HOTSPAWN))
    if not raw and previous and previous.get('matches'):
        flags.append(problem('unexpected_empty', 'Unexpected empty normalized CS2 inventory; previous list retained for review.', FIXTURES))
        return retained(previous, now, src.log, flags)
    if not raw and not complete:
        return retained(previous, now, src.log, flags)

    prior_only = []
    if not complete and previous:
        prior_fields = {str(r['id']): r for r in previous.get('fixture_evidence', [])}
        for match in previous.get('matches', []):
            # On partial discovery, missing *still-open* previous entries cannot
            # be declared removed. Keep them visible but never price them anew.
            if (match['id'] not in raw and match['id'] in prior_fields and match.get('lock')
                    and match.get('start') and dt(match['lock']) > now and dt(match['start']) > now):
                ident = match['id']
                raw[ident] = prior_fields[ident]
                prior_only.append(ident)
                old_observed = previous['fixtures_observed_at']
                provenance[ident] = [{'url': match.get('feed_url', FIXTURES), 'observed_at': old_observed,
                                      'retained_from_previous_snapshot': True}]
                observations.append(old_observed)
    matches = normalize_fixtures(list(raw.values()), links, now)
    conflicting = {c['id'] for c in conflicts}
    for match in matches:
        match['fixture_sources'] = provenance[match['id']]
        if match['id'] in supplements:
            review = supplements[match['id']]
            match['feed_url'] = review['api_url']
            match['inventory_receipt'] = {key: review[key] for key in
                ('fixture_id', 'listed_url', 'match_url', 'api_url', 'reviewed_at', 'valid_until', 'basis')}
            match['flags'].append('Reviewed supplemental inventory row; the primary Hotspawn views do not all return it.')
        if match['id'] in conflicting or match['id'] in prior_only:
            reason = ('Official fixture sources disagree on identity, schedule or status.' if match['id'] in conflicting
                      else 'Only present in the previous snapshot; current membership is unverified after partial discovery.')
            match['resolution_blocked'] = True
            match['flags'].append(reason)
            match['reason'] = reason + ' No recommendation until the fixture can be verified.'
            match['attempts'].append({'provider': 'Hotspawn discovery', 'status': 'unresolved', 'reason': reason, 'url': HOTSPAWN})
    if prior_only:
        flags.append(problem('retained_open_rows', f'{len(prior_only)} previously open fixtures retained with unverified current membership. No pick issued for them.', HOTSPAWN))
    old_ids = {m['id'] for m in previous.get('matches', [])} if previous else set()
    return {'raw': list(raw.values()), 'matches': matches, 'flags': flags,
            'coverage': 'verified' if complete else 'partial',
            'observed_at': min(observations, key=dt), 'conflicts': conflicts,
            'counts': {key: next((len(s['rows']) for s in snapshots if s['key'] == key), None)
                       for key in ('api', 'page', 'lobby')} | {'retained': len(matches)},
            'changes': {'compared_with': previous.get('generated_at') if previous else None,
                        'added_ids': sorted(set(raw) - old_ids), 'removed_ids': sorted(old_ids - set(raw))}}
