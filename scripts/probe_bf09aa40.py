"""Targeted line probe for the fixtures the featured method cannot price.

Why this exists
---------------
The user asked for a pick on **every** Hotspawn CS2 match and for a win
probability wherever research supports one: HLTV first, then esportsbooks and
esports betting lines. On the live board a small number of open fixtures end up
with no percentage (research-only picks) or with no pick at all, because
Polymarket does not list them, Pinnacle's guest esports API does not either, and
the originated Valve-standings model refuses them.

This probe measures what *is* published for exactly those fixtures. It is an
evidence step, never a price:

* it selects the gap rows from a real refreshed snapshot (``scripts.refresh``);
* it reads each candidate listing once with the project's own read-only client
  and keeps status, byte count, SHA-256 and observation time;
* it runs the two parsers this repository already ships
  (``scripts.egw_probe.sniff`` for EGamersWorld's bookmaker-average sentences
  and ``scripts.books.parse_listing`` for the JSON-LD / odds-widget listing) so
  the output says whether a receipt written from that page could be renewed by
  the scheduled re-observer;
* it re-checks the two automated markets (Polymarket, Pinnacle) for the exact
  opponent pair, so "no market exists" is a measurement and not an assumption;
* it records whether HLTV lists the fixture and what ranks it displays.

Nothing here converts a price into a probability, nothing is retried against an
access restriction, and a refused host is recorded as a finding. Run it on an
Actions runner (the authoring sandbox has no route to these hosts).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from scripts import books as books_probe
from scripts import egw_probe
from scripts.core import (ALIAS_MAP, GAMMA, PIN, dt, iso, norm,
                          pinnacle_candidates, polymarket_candidates)
from scripts.refresh import Sources

EGW_LISTING = 'https://egamersworld.com/counterstrike/matches'
STAVKA_LISTING = 'https://stavka.tv/matches/csgo'
EGW_MATCH_LINK_RE = egw_probe.MATCH_LINK_RE
STAVKA_MATCH_LINK_RE = re.compile(r'href="(/matches/csgo/[^"]+)"')
MAX_BODY_KEEPS = 40


def comparable(label):
    """Map a displayed book label to its registered canonical form, or itself."""
    return ALIAS_MAP.get(norm(label), norm(label))


def pair_matches(reading_pair, teams):
    """Exact two-way identity: each book label maps to one distinct board team."""
    wanted = {comparable(t) for t in teams}
    mapped = {comparable(x) for x in reading_pair}
    return mapped == wanted and len(wanted) == 2


def start_matches(value, start):
    try:
        return iso(value) == iso(start)
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def gap_rows(snapshot):
    rows = []
    for row in snapshot.get('matches') or []:
        if row.get('state') != 'open':
            continue
        if row.get('probabilities') is not None and row.get('pick'):
            continue
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--pages', type=int, default=40,
                        help='How many EGamersWorld match pages to capture from the listing.')
    parser.add_argument('--stavka-pages', type=int, default=25,
                        help='How many stavka.tv CS2 match pages to capture from the listing.')
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    src = Sources(now)
    snapshot = json.loads(Path(args.snapshot).read_text())
    gaps = gap_rows(snapshot)

    report = {
        'probed_at': iso(now),
        'snapshot_generated_at': snapshot.get('generated_at'),
        'policy': ('One read per URL with the project client; access refusals are recorded, never '
                   'retried or bypassed. Prices are recorded as displayed and never converted to a '
                   'probability by this probe.'),
        'gap_rows': [{
            'id': r['id'], 'teams': r['teams'], 'competition': r.get('competition'),
            'tier': r.get('tier'), 'best_of': r.get('best_of'), 'start': r.get('start'),
            'pick': r.get('pick'), 'method': r.get('method'),
            'probabilities': r.get('probabilities'), 'reason': r.get('reason'),
            'hltv_source': (r.get('hltv_context') or {}).get('source'),
            'attempt_providers': sorted({a.get('provider') for a in (r.get('attempts') or [])
                                         if a.get('provider')}),
        } for r in gaps],
        'pages': [],
        'markets': {},
        'matches_found': [],
    }
    bodies_kept = 0

    def capture(name, url, keep_if_reading=True, force_keep=False):
        """One logged read. Raw body is kept only when it is worth reviewing."""
        nonlocal bodies_kept
        record = {'name': name, 'url': url,
                  'checked_at': iso(datetime.now(timezone.utc))}
        try:
            body, evidence = src.get(name, url, as_json=False)
        except Exception as exc:  # a refusal is data, never a number
            record.update(status='error', error='%s: %s' % (type(exc).__name__, str(exc)[:220]))
            report['pages'].append(record)
            return record, ''
        record.update({k: v for k, v in (evidence or {}).items() if k not in ('name', 'url')})
        record['body_sha256'] = hashlib.sha256(body.encode('utf-8', 'replace')).hexdigest()
        record['egw_readings'] = egw_probe.sniff(body)
        record['listing_readings'] = books_probe.parse_listing(body)
        keep = force_keep or (keep_if_reading and
                              (record['egw_readings'] or record['listing_readings']))
        if keep and bodies_kept < MAX_BODY_KEEPS:
            slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')[:70] or 'page'
            (out / (slug + '.html')).write_text(body, encoding='utf-8')
            (out / (slug + '.sha256')).write_text(record['body_sha256'] + '\n', encoding='utf-8')
            bodies_kept += 1
            record['body_file'] = slug + '.html'
        report['pages'].append(record)
        return record, body

    # 1. EGamersWorld: listing -> match pages -> bookmaker-average sentences.
    listing, listing_html = capture('egw-listing', EGW_LISTING, force_keep=True)
    links, seen = [], set()
    for match in EGW_MATCH_LINK_RE.finditer(listing_html or ''):
        href = match.group(1).replace('/counterstrike/tip/', '/counterstrike/match/')
        if href not in seen:
            seen.add(href)
            links.append(href)
    report['egw_listing_links'] = links
    for href in links[:args.pages]:
        label = href.rsplit('/', 1)[-1]
        record, body = capture('egw ' + label, 'https://egamersworld.com' + href)
        for reading in (record.get('egw_readings') or []):
            for row in gaps:
                if pair_matches((reading.get('favourite_team'), reading.get('outsider_team')),
                                row['teams']):
                    report['matches_found'].append({
                        'fixture_id': row['id'], 'teams': row['teams'],
                        'source': 'EGamersWorld bookmaker-average sentence',
                        'url': record['url'], 'sha256': record.get('sha256'),
                        'observed_at': record.get('observed_at'), 'reading': reading})

    # 2. stavka.tv: the cross-operator panel already used for one receipt.
    st_listing, st_html = capture('stavka-listing', STAVKA_LISTING, force_keep=True)
    st_links, st_seen = [], set()
    for match in STAVKA_MATCH_LINK_RE.finditer(st_html or ''):
        if match.group(1) not in st_seen:
            st_seen.add(match.group(1))
            st_links.append(match.group(1))
    report['stavka_listing_links'] = st_links
    for href in st_links[:args.stavka_pages]:
        label = href.rsplit('/', 1)[-1]
        record, _body = capture('stavka ' + label, 'https://stavka.tv' + href)
        for reading in (record.get('listing_readings') or []):
            for row in gaps:
                if pair_matches((reading.get('team1'), reading.get('team2')), row['teams']):
                    report['matches_found'].append({
                        'fixture_id': row['id'], 'teams': row['teams'],
                        'source': 'stavka.tv cross-operator odds panel',
                        'url': record['url'], 'sha256': record.get('sha256'),
                        'observed_at': record.get('observed_at'), 'reading': reading,
                        'bound_to_labels': reading.get('bound_to_labels')})

    # 3. The two automated markets, re-checked for these exact pairs right now.
    try:
        events, evidence = src.get('Polymarket CS2 events (gap re-check)',
                                   GAMMA + '/events?tag_slug=cs2&active=true&closed=false&limit=100&offset=0')
        candidates = polymarket_candidates(events, evidence['observed_at'])
        report['markets']['polymarket'] = {
            'status': 'ok', 'url': evidence['url'], 'observed_at': evidence['observed_at'],
            'cs2_moneyline_markets': len(candidates),
            'labels': sorted({t for c in candidates for t in c['teams']}),
            'gap_hits': [{
                'fixture_id': row['id'], 'teams': row['teams'],
                'market_teams': c['teams'], 'prices': c['prices'],
                'liquidity': (c.get('raw') or {}).get('liquidity'),
                'volume': (c.get('raw') or {}).get('volume'),
                'url': c['url'], 'start': c.get('start'),
            } for row in gaps for c in candidates
                if pair_matches(c['teams'], row['teams'])],
        }
    except Exception as exc:
        report['markets']['polymarket'] = {'status': 'error', 'error': str(exc)[:220]}

    try:
        matchups, m_evidence = src.get('Pinnacle esports matchups (gap re-check)',
                                       PIN + '/sports/12/matchups?withSpecials=false')
        lines, l_evidence = src.get('Pinnacle esports straight lines (gap re-check)',
                                    PIN + '/sports/12/markets/straight')
        candidates = pinnacle_candidates(matchups, lines, m_evidence['observed_at'])
        report['markets']['pinnacle'] = {
            'status': 'ok', 'url': m_evidence['url'], 'observed_at': m_evidence['observed_at'],
            'cs2_moneyline_markets': len(candidates),
            'gap_hits': [{
                'fixture_id': row['id'], 'teams': row['teams'], 'market_teams': c['teams'],
                'line': c['raw'].get('line'), 'start': c.get('start'), 'status': c.get('status'),
            } for row in gaps for c in candidates if pair_matches(c['teams'], row['teams'])],
        }
    except Exception as exc:
        report['markets']['pinnacle'] = {'status': 'error', 'error': str(exc)[:220]}

    # 4. HLTV: does it list the fixture, and what does it display for each team?
    hltv = []
    for row in gaps:
        source = (row.get('hltv_context') or {}).get('source')
        # The collector stores the HLTV fixture page as a plain URL string; an
        # object form is accepted too so a schema change is not a crash.
        url = source if isinstance(source, str) else (source or {}).get('url')
        entry = {'fixture_id': row['id'], 'teams': row['teams'], 'url': url,
                 'collector_context': {
                     'ranks': (row.get('hltv_context') or {}).get('ranks'),
                     'lineups': [x.get('team') for x in
                                 ((row.get('hltv_context') or {}).get('lineups') or [])]}}
        if url:
            record, _body = capture('hltv ' + str(row['id']), url)
            entry.update(status=record.get('status'), sha256=record.get('sha256'),
                         error=record.get('error'))
        else:
            entry.update(status='not_listed_by_collector',
                         note='The collector found no HLTV fixture page for this pair and start.')
        hltv.append(entry)
    report['hltv'] = hltv

    (out / 'probe-report.json').write_text(json.dumps(report, indent=1) + '\n', encoding='utf-8')
    print('gap rows: %d' % len(gaps))
    for row in report['gap_rows']:
        print('  %-9s %-42s pick=%-18s method=%s' % (
            row['id'], ' vs '.join(row['teams'])[:42], row['pick'], row['method']))
    print('pages probed: %d (errors: %d)' % (
        len(report['pages']), sum(1 for p in report['pages'] if p.get('status') == 'error')))
    print('exact book-listing hits: %d' % len(report['matches_found']))
    for hit in report['matches_found']:
        print('  %s %s -> %s' % (hit['fixture_id'], hit['source'], hit['url']))
    for name in ('polymarket', 'pinnacle'):
        info = report['markets'].get(name) or {}
        print('%s: %s (gap hits: %s)' % (name, info.get('status'),
                                         len(info.get('gap_hits') or []) if info.get('status') == 'ok' else 'n/a'))


if __name__ == '__main__':
    main()
