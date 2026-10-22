"""Session dee046c2: independent dated re-read of every open fixture's primary sources.

Read-only by design. This probe never edits a snapshot, never writes data files
and never publishes. It fetches, at the runner's own clock:

* the Hotspawn fixture API (inventory only — ids, starts, team labels);
* each open row's Polymarket market again through the Gamma API, recomputing the
  exact normalisation ``scripts.core.quote_polymarket`` performs;
* Pinnacle's public esports matchup and straight-moneyline feeds, searched for
  every open fixture by the same exact-pair, exact-start rule as production;
* HLTV's upcoming list and the match page of every open fixture it lists, using
  ``scripts.hltv.discover``/``scripts.hltv.context`` so the parse is identical
  to the collector's;
* the researched book listing for the one fixture with no pick (EGamersWorld)
  through ``scripts.books.parse_listing``, plus the documented bo3.gg read and
  the two access-only checks (Thunderpick, GG.BET) the collector itself runs;
* Valve's official standings through ``scripts.vrs.fetch`` and the model line
  through ``scripts.vrs.line`` for every row published from the model, and for
  every research-only row, recording exactly why the line applies or refuses.

Everything lands in ``research/harvest-dee046c2/probe.json`` with a UTC stamp
per read; raw bodies are saved under ``research/harvest-dee046c2/raw/`` so a
human can re-derive any number from the committed file. A value this probe
cannot fetch is recorded as a refusal, never as zero.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from scripts import books, core, hltv, vrs
from scripts.refresh import Sources


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


class Raw:
    def __init__(self, outdir: Path):
        self.dir = outdir
        self.dir.mkdir(parents=True, exist_ok=True)

    def save(self, name, data) -> dict:
        raw = data if isinstance(data, bytes) else data.encode('utf-8', 'replace')
        path = self.dir / name
        path.write_bytes(raw)
        return {'file': str(path.relative_to(self.dir.parent)), 'bytes': len(raw),
                'sha256': sha256_bytes(raw)}


def probe_inventory(src, snapshot, raw):
    """Re-read the three Hotspawn views; confirm every open fixture still exists."""
    out = {}
    data, receipt = src.get('Hotspawn fixture API', core.FIXTURES)
    rows = data.get('data') if isinstance(data, dict) else data
    rec = raw.save('hotspawn-fixtures.json', json.dumps(data))
    live = {}
    for row in rows or []:
        if isinstance(row, dict) and row.get('sport_alias') == 'cs2':
            live[str(row.get('id'))] = {
                'teams': [row.get('participants0_name'), row.get('participants1_name')],
                'start': core.iso(row['scheduled_start_time']) if row.get('scheduled_start_time') else None,
                'status': row.get('status'), 'end_time': bool(row.get('end_time'))}
    out['api'] = {'count_cs2': len(live), 'observed_at': receipt['observed_at'], **rec}
    for m in [m for m in snapshot['matches'] if m['state'] == 'open']:
        live_row = live.get(m['id'])
        exact = bool(live_row and live_row['teams'] == m['teams'] and live_row['start'] == m['start']
                     and live_row['status'] == 'scheduled' and not live_row['end_time'])
        out.setdefault('open_rows', {})[m['id']] = {
            'still_listed': bool(live_row), 'exact_match_start_status': exact,
            'api': live_row}
    for name, url in [('lobby', 'https://play.hotspawn.com/lobby'),
                      ('cs2_pickems', 'https://play.hotspawn.com/cs2-pickems')]:
        try:
            html, r = src.get('Hotspawn ' + name, url, False)
            entry = {'status': 'ok', 'observed_at': r['observed_at'], **raw.save('hotspawn-%s.html' % name, html)}
        except Exception as e:  # noqa: BLE001 - recorded, never raised
            entry = {'status': 'refused', 'error': str(e)[:240]}
        out[name] = entry
    return out


def probe_exchange(src, snapshot, raw, findings):
    """Re-read every published exchange market and replay the normalisation."""
    out = []
    for m in [x for x in snapshot['matches'] if x['state'] == 'open']:
        ev = next((e for e in (m.get('evidence') or [])
                   if isinstance(e, dict) and e.get('provider') == 'Polymarket'), None)
        if m.get('probabilities') is None or ev is None:
            continue
        entry = {'id': m['id'], 'teams': m['teams'], 'start': m['start'],
                 'method': m.get('method'), 'published_probabilities': m['probabilities'],
                 'published_observed_at': ev.get('observed_at'), 'market_id': ev.get('id')}
        try:
            d, r = src.get('Polymarket market replay ' + str(ev['id']),
                           'https://gamma-api.polymarket.com/markets/%s' % ev['id'])
            entry['reobserved_at'] = r['observed_at']
            entry['raw'] = raw.save('polymarket-%s.json' % ev['id'], json.dumps(d))
            prices = [float(x) for x in json.loads(d.get('outcomePrices') or '[]')]
            labels = [str(x) for x in json.loads(d.get('outcomes') or '[]')]
            entry.update({
                'question': d.get('question'), 'labels': labels,
                'outcome_prices': prices,
                'best_bid': d.get('bestBid'), 'best_ask': d.get('bestAsk'),
                'spread_points': round((float(d.get('bestAsk') or 0) - float(d.get('bestBid') or 0)) * 100, 2)
                if d.get('bestAsk') is not None and d.get('bestBid') is not None else None,
                'liquidity': d.get('liquidity'), 'volume': d.get('volume'),
                'active': d.get('active'), 'closed': d.get('closed'),
                'accepting_orders': d.get('acceptingOrders'),
                'market_start_date': d.get('startDate') or d.get('eventStartTime'),
                'end_date': d.get('endDate')})
            if len(prices) == 2 and all(0 < p < 1 for p in prices):
                p0 = prices[0] / sum(prices)
                order = core.orientation(m, ev.get('source_teams') or [], ev.get('start') or m['start'])
                entry['market_outcome_labels'] = labels
                if order is not None:
                    entry['first_team_prob_replay'] = round(p0 if order[0] == 0 else 1 - p0, 6)
                    pub = m['probabilities'][0]
                    entry['delta_first_team_vs_published'] = round((p0 if order[0] == 0 else 1 - p0) - pub, 6)
                    if abs(entry['delta_first_team_vs_published']) > 0.05:
                        findings.append('%s: exchange moved >5 points since the row observed it (dated quote, not an error)' % m['id'])
                else:
                    findings.append('%s: replay identity could not be oriented to the published row' % m['id'])
            else:
                findings.append('%s: replay market did not expose two finite prices' % m['id'])
        except Exception as e:  # noqa: BLE001
            entry['status'] = 'refused'
            entry['error'] = str(e)[:240]
            findings.append('%s: exchange replay failed (%s)' % (m['id'], str(e)[:120]))
        out.append(entry)
    return out


def probe_pinnacle(src, snapshot, raw, findings):
    """Search Pinnacle's public feeds for every open fixture, exact pair + start."""
    out = {'status': 'skipped'}
    open_rows = [m for m in snapshot['matches'] if m['state'] == 'open']
    try:
        matchups, mr = src.get('Pinnacle esports fixtures', core.PIN + '/sports/12/matchups?withSpecials=false')
        lines, lr = src.get('Pinnacle esports moneylines', core.PIN + '/sports/12/markets/straight')
        raw.save('pinnacle-matchups.json', json.dumps(matchups))
        observed = min(mr['observed_at'], lr['observed_at'], key=core.dt)
        candidates = core.pinnacle_candidates(matchups, lines, observed)
        out = {'status': 'ok', 'observed_at': observed, 'cs2_candidates': len(candidates)}
        per = {}
        for m in open_rows:
            hits = [c for c in candidates if core.orientation(m, c['teams'], c['start']) is not None]
            rec = {'exact_candidates': len(hits)}
            if hits:
                c = hits[0]
                order = core.orientation(m, c['teams'], c['start'])
                values = {p['designation']: p['price'] for p in c['line']['prices']}
                odds = [core.american(values['home']), core.american(values['away'])]
                p, margin = core.devig(odds)
                rec.update({'published_decimal': odds, 'devig_margin': round(margin, 4),
                            'probabilities_first_team': [round(p[i], 6) for i in order]})
                pub = m.get('probabilities')
                if pub is None:
                    findings.append('%s: Pinnacle now lists an exact moneyline where the board has none '
                                    '(%s vs %s; logged for the owning session, not applied here)'
                                    % (m['id'], m['teams'][0], m['teams'][1]))
                else:
                    rec['delta_first_team_vs_published'] = round(p[order[0]] - pub[0], 6)
            per[m['id']] = rec
        out['per_open_fixture'] = per
    except Exception as e:  # noqa: BLE001
        out = {'status': 'refused', 'error': str(e)[:240]}
        findings.append('Pinnacle public feed refused: ' + str(e)[:120])
    return out


def probe_hltv(src, snapshot, raw, findings):
    """HLTV discovery + match-page context for every open fixture, repo-identical parse."""
    out = {}
    try:
        page, r = src.get('HLTV upcoming', hltv.BASE + '/matches', False)
        raw.save('hltv-matches.html', page)
        out['listing'] = {'observed_at': r['observed_at'], 'matches_found': len(hltv.discover(page))}
        candidates = hltv.discover(page)
    except Exception as e:  # noqa: BLE001
        out['listing'] = {'status': 'refused', 'error': str(e)[:240]}
        findings.append('HLTV /matches refused: ' + str(e)[:120])
        return out
    for m in [x for x in snapshot['matches'] if x['state'] == 'open']:
        exact = [c for c in candidates if core.orientation(m, c['teams'], c['start']) is not None]
        entry = {'hltv_exact': len(exact)}
        if len(exact) == 1:
            try:
                time.sleep(1.0)
                html, hr = src.get('HLTV match ' + m['id'], exact[0]['url'], False)
                entry['url'] = exact[0]['url']
                entry['observed_at'] = hr['observed_at']
                entry['raw'] = raw.save('hltv-%s.html' % m['id'], html)
                ctx = hltv.context(html, m)
                entry['ranks'] = ctx['ranks']
                entry['numeric_quote_rows'] = ctx['numeric_quote_rows']
                entry['limitation'] = ctx['limitation']
                if ctx['numeric_quote_rows']:
                    findings.append('%s: HLTV match page exposed %d numeric provider rows at %s '
                                    '(secondary quotes; flag for the pricing session)'
                                    % (m['id'], ctx['numeric_quote_rows'], exact[0]['url']))
            except Exception as e:  # noqa: BLE001
                entry['status'] = 'refused'
                entry['error'] = str(e)[:240]
        out[m['id']] = entry
    return out


def probe_gap_books(src, snapshot, raw, findings):
    """EGW listing + bo3.gg + access-only checks for the rows the ladder could not price."""
    out = {}
    gap_rows = [m for m in snapshot['matches'] if m['state'] == 'open' and m.get('probabilities') is None]
    egw_urls = {'1081597': 'https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn'}
    bo3_urls = {'1081597': 'https://bo3.gg/matches/benched-gods-vs-titanflow-22-10-2026'}
    for m in gap_rows:
        rec = {}
        for key, urls in (('egw', egw_urls), ('bo3', bo3_urls)):
            url = urls.get(m['id'])
            if not url:
                continue
            try:
                time.sleep(1.0)
                html, r = src.get('EGW listing ' + m['id'] if key == 'egw' else 'bo3 ' + m['id'], url, False)
                entry = {'url': url, 'observed_at': r['observed_at'], 'raw': raw.save('%s-%s.html' % (key, m['id']), html)}
                if key == 'egw':
                    readings = books.parse_listing(html)
                    want = {core.norm(t) for t in m['teams']}
                    for reading in readings:
                        pair = {core.norm(reading['team1']), core.norm(reading['team2'])}
                        reading['exact_pair'] = pair == want and len(pair) == 2
                        reading['exact_start'] = (reading['start'] or '')[:19] == m['start'][:19]
                    entry['parse_readings'] = readings
                rec[key] = entry
            except Exception as e:  # noqa: BLE001
                rec[key] = {'url': url, 'status': 'refused', 'error': str(e)[:200]}
                findings.append('%s: %s refused (%s)' % (m['id'], url, str(e)[:80]))
        rec['note'] = ('Research-only: this probe does not price anything; it records what the '
                       'book pages show at this timestamp for the session owning data/book-receipts.json.')
        out[m['id']] = rec
    for provider, url in [('Thunderpick', 'https://thunderpick.io/esports/cs2-betting'),
                          ('GG.BET', 'https://gg.bet/en/esports/counter-strike')]:
        if not gap_rows:
            break
        try:
            _, r = src.get(provider + ' access check', url, False)
            out.setdefault('access_checks', {})[provider] = {'status': 'reachable', 'observed_at': r['observed_at'],
                                                              'meaning': 'access only; not a quote adapter'}
        except Exception as e:  # noqa: BLE001
            out.setdefault('access_checks', {})[provider] = {'status': 'refused', 'error': str(e)[:160]}
    return out


def probe_vrs(src, snapshot, raw, token, findings):
    """Replay the originated model line for every model row and try each research row."""
    out = {}
    ref_now = core.dt(snapshot['generated_at']) if snapshot.get('generated_at') else datetime.now(timezone.utc)
    standings, meta, problem = vrs.fetch(src, ref_now, token)
    out['fetch'] = {'problem': problem, 'as_of': (standings or {}).get('as_of'),
                    'file': (meta or {}).get('file'), 'commit': (meta or {}).get('commit'),
                    'teams': (standings or {}).get('counts', {}).get('teams') if standings else None}
    if standings is None:
        findings.append('VRS fetch refused; model rows could not be replayed')
        return out
    for m in [x for x in snapshot['matches'] if x['state'] == 'open']:
        quote, reason = vrs.line(m, standings, meta)
        rec = {'method': m.get('method'), 'model_refuses': reason is not None,
               'refusal_reason': reason}
        if quote is not None:
            rec.update({'model_probabilities': [round(x, 6) for x in quote['probabilities']],
                        'standings_rows': quote['standings'], 'points': quote['points']})
            if m.get('probabilities') is not None and m.get('method') == 'model_vrs':
                rec['delta_first_team_vs_published'] = round(quote['probabilities'][0] - m['probabilities'][0], 8)
                if abs(quote['probabilities'][0] - m['probabilities'][0]) > 5e-6:
                    findings.append('%s: model replay differs from published row' % m['id'])
            elif m.get('probabilities') is None:
                findings.append('%s: VRS model line is now computable for a research-only row '
                                '(%s); pricing decision belongs to the owning session' % (m['id'], reason or ''))
        out[m['id']] = rec
    return out


def probe_merged_claims(src, snapshot, raw, findings):
    """Independent dated re-read of the two claims PR #119 puts on the board.

    1. The Zetta ↔ Alianza Lima Esports alias: the fixture's exclusion record
       quotes Polymarket event 1227336 — re-read the event so a human can check
       the exact pair, start and liquidity without trusting the register text.
    2. The 'Match postponed' state for benched gods vs TitanFlow: re-read
       HLTV's event page for CCT 2026 Challengers Europe Series #8 and record
       what it says about slot 2399696 / TitanFlow / benched gods.
    """
    out = {}
    try:
        d, r = src.get('Polymarket event 1227336 (Zetta alias)',
                       'https://gamma-api.polymarket.com/events/1227336')
        out['polymarket_event_1227336'] = {
            'observed_at': r['observed_at'],
            'raw': raw.save('polymarket-event-1227336.json', json.dumps(d)),
            'title': d.get('title'), 'slug': d.get('slug'),
            'start': d.get('startDate') or d.get('eventStartTime'),
            'markets': [{'question': m.get('question'),
                         'outcomes': m.get('outcomes'), 'outcomePrices': m.get('outcomePrices'),
                         'bestBid': m.get('bestBid'), 'bestAsk': m.get('bestAsk'),
                         'liquidity': m.get('liquidity'), 'active': m.get('active'),
                         'closed': m.get('closed'), 'acceptingOrders': m.get('acceptingOrders'),
                         'resolutionSource': m.get('resolutionSource') or m.get('umaResolutionSource')}
                        for m in (d.get('markets') or [])[:4]]}
    except Exception as e:  # noqa: BLE001
        out['polymarket_event_1227336'] = {'status': 'refused', 'error': str(e)[:200]}
        findings.append('could not re-read Polymarket event 1227336: ' + str(e)[:120])
    for name, url, needles in [
        ('hltv-event-9453', 'https://www.hltv.org/events/9453/cct-2026-challengers-europe-series-8',
         ['benched', 'TitanFlow', '2399696', 'postpon']),
        ('hltv-zetta-2399865', 'https://www.hltv.org/matches/2399865/zetta-vs-los-ninos-cct-2026-south-america-series-7',
         ['Zetta', 'LOS NINOS', 'odds']),
    ]:
        try:
            time.sleep(1.0)
            html, r = src.get(name, url, False)
            text = re.sub(r'<[^>]+>', ' ', html)
            hits = {}
            for needle in needles:
                pos = text.lower().find(needle.lower())
                hits[needle] = None if pos < 0 else re.sub(r'\s+', ' ', text[max(0, pos - 90):pos + 140]).strip()
            out[name] = {'url': url, 'observed_at': r['observed_at'],
                         'bytes': len(html.encode('utf-8', 'replace')),
                         'sha256': sha256_bytes(html.encode('utf-8', 'replace')),
                         'context': hits}
            raw.save(name + '.html', html)
        except Exception as e:  # noqa: BLE001
            out[name] = {'url': url, 'status': 'refused', 'error': str(e)[:200]}
            findings.append('%s refused: %s' % (name, str(e)[:100]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', required=True)
    ap.add_argument('--out', default='research/harvest-dee046c2')
    args = ap.parse_args()
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    raw = Raw(outdir / 'raw')
    snapshot = json.loads(Path(args.snapshot).read_text())
    src = Sources(datetime.now(timezone.utc))
    findings: list[str] = []
    result = {'session': 'dee046c2', 'probe_started_at': now_iso(),
              'policy': 'read-only; Hotspawn inventory only; every number replayed from a fetched primary source; refusals recorded, never zeroed',
              'snapshot_generated_at': snapshot.get('generated_at'),
              'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
              'coverage': snapshot.get('coverage')}
    result['inventory'] = probe_inventory(src, snapshot, raw)
    result['exchange'] = probe_exchange(src, snapshot, raw, findings)
    result['pinnacle'] = probe_pinnacle(src, snapshot, raw, findings)
    result['hltv'] = probe_hltv(src, snapshot, raw, findings)
    result['gap_books'] = probe_gap_books(src, snapshot, raw, findings)
    result['vrs'] = probe_vrs(src, snapshot, raw, os.environ.get('GITHUB_TOKEN'), findings)
    result['merged_claims'] = probe_merged_claims(src, snapshot, raw, findings)
    result['source_log'] = src.log
    result['findings'] = findings
    result['probe_finished_at'] = now_iso()
    (outdir / 'probe.json').write_text(json.dumps(result, indent=1) + '\n')
    print(json.dumps({'findings': findings,
                      'coverage': result['coverage'],
                      'open_ids': [m['id'] for m in snapshot['matches'] if m['state'] == 'open']}, indent=1))


if __name__ == '__main__':
    main()
