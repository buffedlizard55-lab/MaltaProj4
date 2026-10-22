"""Targeted HLTV-first probe for open rows without a win probability (session 241b0c14).

Why this exists
---------------
The featured ladder in ``scripts.refresh`` already tries, in order, the strict
Polymarket gate, HLTV identity research, Pinnacle, the labelled wide-exchange
tier, researched book listings and the two Valve VRS model tiers. A row that
still publishes no percentage after that ladder is exactly the row the project
owner asked to be researched by hand: HLTV first, then esportsbooks. This
probe performs that dated second look on a runner with normal outbound access
(the authoring sandbox reaches GitHub and package registries only) and writes
compact, receipt-backed evidence to ``research/session-241b0c14/capture/``.

What it can and cannot do
-------------------------
* It only ever *reads*. It never writes ``data/latest.json``, never prices a
  row and never changes a pick. Pricing stays with ``scripts.refresh`` and its
  existing gates; if this probe finds an exact-pair, exact-UTC-start,
  label-bound asymmetric two-way line, the finding is recorded here so a human
  session can add a dated receipt to ``data/book-receipts.json`` and let the
  next scheduled refresh replay it.
* Hotspawn is the fixture inventory only. Crowd votes (Hotspawn or HLTV) are
  never read as probabilities. HLTV world ranks are identity/context evidence,
  never converted to a percentage. The identical 1.8/1.8 EGamersWorld
  placeholder, an unnamed opponent slot, an unbound odds pair and any URL slug
  that was not discovered on the operator's own listing page are refusals.
* Every HTTP read goes through ``scripts.refresh.Sources``, so each result
  carries the same receipt fields as the production collector (HTTP status,
  SHA-256, bytes, cache-adjusted observation time, rate-limit waits). A source
  that refuses access is recorded with its status; nothing is bypassed.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from scripts import books as books_probe
from scripts import summary
from scripts.core import GAMMA, PIN, iso, norm, plain_name

DECIMAL = re.compile(r'^\d{1,3}\.\d{1,3}$')
STAVKA_LISTING = 'https://stavka.tv/matches/csgo'
# bo3.gg event pages already recorded in this repository for the competitions
# the blank-percentage rows belong to (scripts/apply_2d0a85f2.py). No bo3 URL
# is constructed here; an unmapped competition is recorded as not probed.
BO3_EVENT_PAGES = {
    'DFRAG Invitational 2026': 'https://bo3.gg/tournaments/dfrag-invitational-2026',
    'CCT South America 2026 Series #7': 'https://bo3.gg/tournaments/cct-south-america-2026-series-7',
}


def _cell(value):
    return str(value or '').replace('|', '\\|').replace('\n', ' ')


def diff_snapshots(old, new):
    """Fixture-level diff between the committed board and a fresh capture.

    Pure function. Probabilities are compared at the published precision
    (one decimal of a percent) so float noise never reads as a change, while
    any pick, method, state or priced/unpriced movement is always reported.
    """
    old_by = {str(m['id']): m for m in (old or {}).get('matches') or []}
    new_by = {str(m['id']): m for m in (new or {}).get('matches') or []}

    def rounded(m):
        probs = m.get('probabilities')
        return [round(p * 1000) / 10 for p in probs] if probs else None

    changed = []
    for ident in sorted(set(old_by) & set(new_by)):
        a, b = old_by[ident], new_by[ident]
        fields = {}
        for key in ('state', 'pick', 'method', 'start', 'lock'):
            if a.get(key) != b.get(key):
                fields[key] = [a.get(key), b.get(key)]
        if rounded(a) != rounded(b):
            fields['probabilities_pct'] = [rounded(a), rounded(b)]
        if fields:
            changed.append({'id': ident, 'teams': b.get('teams'), 'changes': fields})
    blank = lambda snap: sorted(
        str(m['id']) for m in snap.get('matches') or []
        if m.get('state') == 'open' and m.get('probabilities') is None)
    unpicked = lambda snap: sorted(
        str(m['id']) for m in snap.get('matches') or []
        if m.get('state') == 'open' and not m.get('pick'))
    return {
        'committed_generated_at': (old or {}).get('generated_at'),
        'fresh_generated_at': (new or {}).get('generated_at'),
        'added_fixture_ids': sorted(set(new_by) - set(old_by)),
        'removed_fixture_ids': sorted(set(old_by) - set(new_by)),
        'changed_rows': changed,
        'blank_percentage_committed': blank(old or {}),
        'blank_percentage_fresh': blank(new or {}),
        'unpicked_committed': unpicked(old or {}),
        'unpicked_fresh': unpicked(new or {}),
    }


def polymarket_verdict(raw):
    """Describe one Gamma market against the project's two spread gates.

    Pure function over the operator's own fields. This mirrors, but never
    replaces, ``scripts.core.quote_polymarket``: the refresh remains the only
    code that may publish a number.
    """
    try:
        bid, ask = float(raw.get('bestBid')), float(raw.get('bestAsk'))
        spread = ask - bid
    except (TypeError, ValueError):
        return {'verdict': 'refused', 'reason': 'No numeric two-sided bid/ask in the market response.'}
    try:
        liquidity = float(raw.get('liquidity') or 0)
    except (TypeError, ValueError):
        liquidity = 0.0
    prices = raw.get('outcomePrices')
    verdict = {
        'best_bid': bid, 'best_ask': ask, 'spread_points': round(spread * 100, 1),
        'liquidity_usd': liquidity, 'outcome_prices': prices,
        'updated_at': raw.get('updatedAt'), 'accepting_orders': raw.get('acceptingOrders'),
        'active': raw.get('active'), 'closed': raw.get('closed'),
    }
    if liquidity < 100:
        verdict.update(verdict='refused', reason='Liquidity below the $100 floor.')
    elif spread <= 0.25 + 1e-9:
        verdict.update(verdict='strict_gate_shape',
                       reason='Spread and liquidity fit the strict gate shape; the refresh still owns freshness, identity and publication.')
    elif spread <= 0.60 + 1e-9:
        verdict.update(verdict='wide_gate_shape',
                       reason='Spread fits only the labelled low-confidence wide tier (25-60 points); the refresh still owns freshness, identity and publication.')
    else:
        verdict.update(verdict='refused',
                       reason='Spread exceeds the 60-point ceiling for the low-confidence tier; the midpoint is not a tradable price.')
    return verdict


def listing_verdict(readings, fixture):
    """Accept only an exact-pair, exact-start, label-bound asymmetric reading.

    ``scripts.books.parse_listing`` already drops the 1.8/1.8 placeholder and
    identical pairs, so an empty list here means the page offered nothing the
    project may use. Label equality uses ``scripts.core.norm`` (registered
    identities only, no fuzzy matching).
    """
    wanted = sorted(norm(t) for t in fixture['teams'])
    for reading in readings or []:
        if sorted(norm(reading.get(k) or '') for k in ('team1', 'team2')) != wanted:
            continue
        try:
            if iso(reading['start']) != iso(fixture['start']):
                continue
        except (TypeError, ValueError, KeyError):
            continue
        if not reading.get('bound_to_labels'):
            continue
        odds = reading.get('odds') or []
        if len(odds) != 2 or odds[0] == odds[1] or min(odds) <= 1.0:
            continue
        return {'verdict': 'candidate_line', 'reading': reading,
                'reason': 'Exact team pair, exact UTC start and an asymmetric two-way pair bound to both labels. '
                          'Candidate for a dated book receipt; the refresh replays identity, freshness and margin before publishing.'}
    return {'verdict': 'refused', 'readings_seen': len(readings or []),
            'reason': 'No reading re-confirmed the exact pair, UTC start and a label-bound asymmetric pair '
                      '(placeholder, unbound, unnamed-opponent and wrong-fixture readings are refused).'}


def stavka_candidates(hrefs, fixture):
    """Discover candidate Stavka match URLs from the operator's own listing.

    Discovery only: a slug that merely contains both team names earns a fetch,
    never a price. ``listing_verdict`` still has to confirm the page itself.
    """
    needles = [plain_name(t) for t in fixture['teams']]
    out = []
    for href in hrefs or []:
        slug = plain_name(href.rsplit('/', 1)[-1])
        if all(n and n in slug for n in needles):
            out.append(href if href.startswith('https://') else 'https://stavka.tv' + href)
    return sorted(set(out))


def mirror_presence(standings, fixture):
    """Which sides appear at all in HLTV's dated Valve-points list.

    Presence only. Valve's roster-continuity rule, duplicated-label handling
    and the formula stay in ``scripts.vrs_mirror`` during the refresh; a club
    being present here is not a line.
    """
    rows = (standings or {}).get('teams') or []
    out = []
    for team in fixture['teams']:
        hits = [{'standing': r['standing'], 'points': r['points'], 'name': r['name']}
                for r in rows if norm(r['name']) == norm(team)]
        out.append({'team': team, 'listed_rows': hits})
    return out


def _hltv_numeric_rows(html):
    """Numeric two-way rows in HLTV's odds-comparison table (mirrors scripts/hltv.py)."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    rows = []
    for row in soup.select('.match-betting-list tr.provider'):
        cells = row.find_all('td', recursive=False)
        values = [c.get_text(' ', strip=True) for c in cells]
        odds = [v for v in values[1:] if DECIMAL.fullmatch(v)]
        if len(odds) == 2:
            rows.append({'bookmaker': values[0] if values else '', 'odds': [float(v) for v in odds]})
    return rows


def _guard(label, fn):
    try:
        return fn()
    except Exception as exc:  # an access refusal is evidence, never a crash or a price
        return {'step': label, 'verdict': 'error', 'reason': str(exc)[:500]}


def rows_markdown(snapshot):
    """Every open row, one line each, with its official source links."""
    c = summary.counts(snapshot['matches'])
    out = [
        '# Fresh open-board audit — session 241b0c14',
        '',
        'Snapshot generated **' + str(snapshot.get('generated_at')) + '** · fixtures observed **'
        + str(snapshot.get('fixtures_observed_at')) + '** · inventory coverage **'
        + str(snapshot.get('coverage')) + '**.',
        '',
        '%d feed rows · %d open · %d with a pick · %d with a win probability '
        '(%d market · %d model) · %d research-only · %d without a pick.'
        % (c['feed_rows'], c['open'], c['with_pick'], c['priced'], c['market'], c['model'],
           c['research'], c['no_pick']),
        '',
        'Hotspawn supplies fixture membership and lock times only; it is never a probability input. '
        'Blank % means no verified two-way line or two-team model input exists — never 50/50.',
        '',
        '| Fixture | Start (UTC) | Pick | Team 1 % / Team 2 % | Method | Sources | Limitation / flags |',
        '| --- | --- | --- | --- | --- | --- | --- |',
    ]
    for m in sorted((m for m in snapshot['matches'] if m['state'] == 'open'),
                    key=lambda m: (m.get('start') or '', m['id'])):
        probs = ('%.1f / %.1f' % (m['probabilities'][0] * 100, m['probabilities'][1] * 100)
                 if m.get('probabilities') else '')
        quotes = m.get('evidence') or []
        evidence = (quotes[0].get('url') if quotes else None) or (m.get('hltv_context') or {}).get('source')
        links = '[Hotspawn](' + m['source_url'] + ')'
        if evidence:
            links += ' · [Evidence](' + evidence + ')'
        limit = m.get('reason') or '; '.join(m.get('flags') or [])
        out.append('| ' + ' | '.join(_cell(x) for x in (
            '%s: %s vs %s' % (m['id'], m['teams'][0], m['teams'][1]),
            m.get('start'), m.get('pick'), probs, m.get('method'), links, limit)) + ' |')
    out.append('')
    return '\n'.join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='runtime/latest.json', help='Fresh refresh output')
    parser.add_argument('--committed', default='data/latest.json', help='Committed board to diff against')
    parser.add_argument('--output', default='research/session-241b0c14/capture')
    args = parser.parse_args(argv)

    fresh = json.loads(Path(args.snapshot).read_text())
    committed_path = Path(args.committed)
    committed = json.loads(committed_path.read_text()) if committed_path.exists() else {}
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'snapshot.json').write_text(json.dumps(fresh, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    (output / 'diff.json').write_text(json.dumps(diff_snapshots(committed, fresh), indent=2, ensure_ascii=False) + '\n')
    (output / 'counts.json').write_text(json.dumps(
        {k: v for k, v in summary.counts(fresh['matches']).items()
         if k not in ('research_rows', 'blank_rows')}, indent=2) + '\n')
    (output / 'rows.md').write_text(rows_markdown(fresh))

    targets = sorted(
        (m for m in fresh['matches'] if m['state'] == 'open' and m.get('probabilities') is None),
        key=lambda m: (m.get('start') or '', m['id']))

    from scripts.refresh import Sources
    now = datetime.now(timezone.utc)
    src = Sources(now)
    report = {'probe': 'session-241b0c14', 'started_at': iso(now),
              'fresh_snapshot_generated_at': fresh.get('generated_at'),
              'targets': [m['id'] for m in targets], 'fixtures': {}}

    # Shared reads first: Pinnacle's two feeds and HLTV's dated Valve ranking
    # answer for every target at once.
    pin = _guard('pinnacle_feeds', lambda: {
        'matchups': src.get('Pinnacle esports fixtures (probe 241b0c14)',
                            PIN + '/sports/12/matchups?withSpecials=false')[0],
        'lines': src.get('Pinnacle esports moneylines (probe 241b0c14)',
                         PIN + '/sports/12/markets/straight')[0]})
    mirror = {'standings': None, 'meta': None, 'problem': None}
    if targets:
        def _mirror():
            from scripts import vrs_mirror
            standings, meta, problem = vrs_mirror.fetch(src, datetime.now(timezone.utc))
            return {'standings': standings, 'meta': meta, 'problem': problem}
        mirror = _guard('hltv_dated_valve_ranking', _mirror)
        if isinstance(mirror, dict) and mirror.get('verdict') == 'error':
            mirror = {'standings': None, 'meta': None, 'problem': mirror.get('reason')}

    book_doc = {}
    try:
        book_doc = json.loads(Path('data/book-receipts.json').read_text())
    except (OSError, ValueError):
        book_doc = {}
    rejected = book_doc.get('rejected_listings') or []
    receipts = book_doc.get('receipts') or []

    stavka_hrefs = []
    if targets:
        def _stavka_listing():
            from bs4 import BeautifulSoup
            html, _receipt = src.get('Stavka CS2 listing (probe 241b0c14)', STAVKA_LISTING, False)
            soup = BeautifulSoup(html, 'html.parser')
            return sorted({a['href'] for a in soup.select('a[href^="/matches/csgo/"]') if a.get('href')})
        found = _guard('stavka_listing', _stavka_listing)
        stavka_hrefs = found if isinstance(found, list) else []
        report['stavka_listing'] = ({'hrefs_seen': len(stavka_hrefs)} if isinstance(found, list) else found)

    for m in targets:
        entry = {'id': m['id'], 'teams': m['teams'], 'competition': m.get('competition'),
                 'start': m.get('start'), 'pick': m.get('pick'), 'method': m.get('method'),
                 'reason_on_board': m.get('reason'), 'steps': []}
        ctx = m.get('hltv_context') or {}

        # 1. HLTV first: the exact fixture page the board already resolved.
        if ctx.get('source'):
            def _hltv(url=ctx['source']):
                html, _receipt = src.get('HLTV fixture ' + m['id'] + ' (probe 241b0c14)', url, False)
                numeric = _hltv_numeric_rows(html)
                return {'step': 'hltv_fixture_page', 'url': url,
                        'numeric_two_way_rows': numeric,
                        'verdict': 'secondary_rows_only' if numeric else 'no_numeric_line',
                        'reason': ('HLTV comparison rows are secondary quotes, never published without '
                                   'confirmation at the named operator.' if numeric else
                                   'HLTV betting table exposes no numeric two-way line in this response. '
                                   'Rankings/lineups confirm identity only.')}
            entry['steps'].append(_guard('hltv_fixture_page', _hltv))
        else:
            entry['steps'].append({'step': 'hltv_fixture_page', 'verdict': 'not_recorded',
                                   'reason': 'The fresh snapshot carries no HLTV fixture URL for this row; no URL was guessed.'})
        entry['steps'].append({
            'step': 'hltv_dated_valve_ranking', 'url': 'https://www.hltv.org/valve-ranking/teams',
            'problem': mirror.get('problem'),
            'presence': mirror_presence(mirror.get('standings'), m) if mirror.get('standings') else None,
            'reason': 'Presence in the dated Valve-points list only; the refresh applies the roster rule and formula.'})

        # 2. Polymarket: re-read every market id the board's attempts recorded.
        market_ids = sorted({
            str((a.get('rejected_quote') or {}).get('id'))
            for a in m.get('attempts') or [] if (a.get('rejected_quote') or {}).get('id')})
        if market_ids:
            for mid in market_ids:
                def _poly(mid=mid):
                    raw, _receipt = src.get('Polymarket market ' + mid + ' (probe 241b0c14)',
                                            GAMMA + '/markets/' + mid)
                    return {'step': 'polymarket_market', 'market_id': mid,
                            'url': GAMMA + '/markets/' + mid,
                            'question': raw.get('question'), **polymarket_verdict(raw)}
                entry['steps'].append(_guard('polymarket_market', _poly))
        else:
            entry['steps'].append({'step': 'polymarket_market', 'verdict': 'not_recorded',
                                   'reason': 'No exact-pair market id is recorded on the row; the refresh feed read found none.'})
        def _search(team=m['teams'][0]):
            raw, _receipt = src.get('Polymarket public search (probe 241b0c14)',
                                    GAMMA + '/public-search?q=' + quote(team))
            events = raw.get('events') if isinstance(raw, dict) else None
            return {'step': 'polymarket_public_search', 'query': team,
                    'events_returned': len(events) if isinstance(events, list) else None,
                    'slugs': [e.get('slug') for e in events[:10]] if isinstance(events, list) else None,
                    'reason': 'Discovery check only; an exact pair + UTC start in the events feed remains the publication gate.'}
        entry['steps'].append(_guard('polymarket_public_search', _search))

        # 3. Pinnacle: exact pair + exact start through the production filter.
        def _pin():
            from scripts.core import orientation, pinnacle_candidates
            observed = iso(datetime.now(timezone.utc))
            cands = pinnacle_candidates(pin['matchups'], pin['lines'], observed)
            hits = [{'id': c['id'], 'teams': c['teams'], 'start': c['start']}
                    for c in cands if orientation(m, c['teams'], c['start']) is not None]
            return {'step': 'pinnacle_exact_pair', 'url': PIN + '/sports/12/markets/straight',
                    'verdict': 'exact_pair_found' if hits else 'no_exact_pair', 'hits': hits}
        entry['steps'].append(_guard('pinnacle_exact_pair', _pin) if 'matchups' in pin else
                               {'step': 'pinnacle_exact_pair', 'verdict': 'error',
                                'reason': (pin or {}).get('reason', 'Pinnacle feeds unavailable to this probe.')})

        # 4. EGamersWorld: every URL already on the research register for this row.
        egw_urls = sorted({r['url'] for r in rejected + receipts
                           if str(r.get('fixture_id')) == str(m['id']) and r.get('url')})
        if egw_urls:
            for url in egw_urls:
                def _egw(url=url):
                    html, _receipt = src.get('EGamersWorld listing ' + m['id'] + ' (probe 241b0c14)', url, False)
                    return {'step': 'egamersworld_listing', 'url': url,
                            **listing_verdict(books_probe.parse_listing(html), m)}
                entry['steps'].append(_guard('egamersworld_listing', _egw))
        else:
            entry['steps'].append({'step': 'egamersworld_listing', 'verdict': 'not_recorded',
                                   'reason': 'No EGamersWorld URL is recorded for this fixture; no slug was guessed.'})

        # 5. Stavka/Winline: listing-discovered pages only.
        candidates = stavka_candidates(stavka_hrefs, m)
        if candidates:
            for url in candidates[:3]:
                def _stavka(url=url):
                    html, _receipt = src.get('Stavka match ' + m['id'] + ' (probe 241b0c14)', url, False)
                    return {'step': 'stavka_winline_panel', 'url': url,
                            'discovered_from': STAVKA_LISTING,
                            **listing_verdict(books_probe.parse_listing(html), m)}
                entry['steps'].append(_guard('stavka_winline_panel', _stavka))
        else:
            entry['steps'].append({'step': 'stavka_winline_panel', 'verdict': 'not_listed',
                                   'reason': 'No Stavka listing href names both teams; no match slug was guessed. '
                                             'This is a discovery limit, not proof that no operator prices the fixture.'})

        # 6. bo3.gg recorded event page: coverage evidence only, never a line.
        bo3_url = BO3_EVENT_PAGES.get(m.get('competition') or '')
        if bo3_url:
            def _bo3(url=bo3_url):
                html, _receipt = src.get('bo3.gg event page (probe 241b0c14)', url, False)
                text = re.sub(r'<[^>]+>', ' ', html)
                return {'step': 'bo3_event_page', 'url': url,
                        'both_teams_named': all(plain_name(t) in plain_name(text) for t in m['teams']),
                        'all_odds_are_on_message_seen': 'All odds are on' in text,
                        'reason': 'Coverage check only; bo3.gg affiliate odds are secondary and are never published without operator confirmation.'}
            entry['steps'].append(_guard('bo3_event_page', _bo3))
        else:
            entry['steps'].append({'step': 'bo3_event_page', 'verdict': 'not_recorded',
                                   'reason': 'No bo3.gg event page is recorded in this repo for this competition; no URL was guessed.'})

        report['fixtures'][m['id']] = entry

    report['finished_at'] = iso(datetime.now(timezone.utc))
    report['source_receipts'] = src.log
    (output / 'targeted.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'targets': report['targets'],
                      'verdicts': {fid: [(s.get('step'), s.get('verdict')) for s in e['steps']]
                                   for fid, e in report['fixtures'].items()}}, indent=2))


if __name__ == '__main__':
    main()
