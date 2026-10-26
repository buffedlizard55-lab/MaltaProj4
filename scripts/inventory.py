"""Compare the official lobby, CS2 page and scoped API without dropping rows."""
import copy
import time
from scripts.core import HOTSPAWN, FIXTURES, dt, iso, hotspawn_state, normalize_fixtures

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
            # The two HTML views are kept verbatim so the run can also compare the
            # fixtures the *lobby page links to* against the ids the feed returned
            # (scripts.lobby_gap). That comparison never adds a row: a lobby
            # listing carries no feed start/lock time, so a lobby-only fixture
            # cannot be priced without inventing one.
            snapshots.append({'key': key, 'url': url, 'rows': rows, 'receipt': receipt,
                              'html': None if json_response else payload})
        except (ValueError, KeyError, TypeError, OverflowError, AttributeError) as exc:
            flags.append(problem(key, str(exc), url))


def discover(src, now, previous=None):
    flags, snapshots, links = [], [], {}
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
    sets = [{str(r['id']) for r in s['rows']} for s in snapshots]
    complete = len(snapshots) == 3 and all(ids == sets[0] for ids in sets)
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
        flags.append(problem('coverage_difference', f'Current lobby parity is unverified ({sizes}; {len(snapshots)}/3 sources usable). Union retained, no missing-source result treated as an empty lobby.', HOTSPAWN))
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
    # Fixtures the lobby page links to but this capture's feed did not return.
    # Recorded, never synthesized: see scripts.lobby_gap and the session receipt.
    from scripts.lobby_gap import compare as lobby_compare, ids_from_html
    lobby_ids = set()
    for snapshot in snapshots:
        lobby_ids.update(ids_from_html(snapshot.get('html')))
    lobby = lobby_compare([str(k) for k in raw], sorted(lobby_ids))
    if lobby['missing_from_feed']:
        flags.append(problem('lobby_gap',
            '%d fixture(s) linked from the Hotspawn lobby are absent from this capture\'s official '
            'fixture feed: %s. No start or lock time is published for them, so no pick is issued; '
            'they are retried on the next refresh.'
            % (lobby['missing_count'], ', '.join(lobby['missing_from_feed'])), LOBBY))
    return {'raw': list(raw.values()), 'matches': matches, 'flags': flags,
            'coverage': 'verified' if complete else 'partial',
            'observed_at': min(observations, key=dt), 'conflicts': conflicts,
            'lobby': lobby,
            'counts': {key: next((len(s['rows']) for s in snapshots if s['key'] == key), None)
                       for key in ('api', 'page', 'lobby')} | {'retained': len(matches)},
            'changes': {'compared_with': previous.get('generated_at') if previous else None,
                        'added_ids': sorted(set(raw) - old_ids), 'removed_ids': sorted(old_ids - set(raw))}}
