"""Dated, read-only research probe for the rows that publish no win probability.

Session 4fd13975. Runs on a GitHub-hosted runner after ``scripts.refresh`` (or
standalone) and answers one question per open row without a percentage: can any
verified source — HLTV first, then esportsbooks and esports betting lines —
supply a publishable two-way line or a Valve-points identity that the existing
tiers missed?

Rules baked into the probe:

* every read is recorded with its URL, HTTP status, observation time and
  SHA-256 of the response body; the body is archived as deterministic gzip so
  the read is replayable byte-for-byte;
* a symmetric 1.8/1.8 (or any identical) pair is a placeholder refusal, never
  a 50/50; an editorial or fan vote is recorded as refused context, never a
  market line;
* a Valve-ranking row is reported as an *identity candidate* only — nothing is
  registered or mapped by the probe; a human-readable report names the exact
  observation that would have to be verified first;
* no value is invented. A miss is data.

The probe writes research files only. It never edits the board, the receipts
register or the published pages.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.books import parse_listing
from scripts.core import dt, iso, norm
from scripts.refresh import Sources
from scripts import vrs_mirror

UA_SUFFIX = ' (research probe session 4fd13975)'
PLACEHOLDER = (1.8, 1.8)
DATE_SLUG_RE = re.compile(r'/matches/csgo/(\d{2}-\d{2}-\d{2})-([a-z0-9-]+)')
ODDS_PAIR_RE = re.compile(r'(\d+\.\d+)\s*(?:/|—|–|-|vs)\s*(\d+\.\d+)')
FAN_VOTE_RE = re.compile(r'(\d{1,3}(?:\.\d+)?)%')


def archive(body: bytes, destination: Path) -> str | None:
    if not body:
        return None
    digest = hashlib.sha256(body).hexdigest()
    target = destination / (digest + '.gz')
    if not target.exists():
        target.write_bytes(gzip.compress(body, mtime=0))
    return 'raw/' + target.name


def read(src: Sources, name: str, url: str, raw_dir: Path, records: list) -> str | None:
    try:
        payload, evidence = src.get(name + UA_SUFFIX, url, False)
    except Exception as exc:
        records.append({'url': url, 'status': 'error', 'reason': str(exc)[:300],
                        'observed_at': iso(datetime.now(timezone.utc))})
        return None
    body = payload if isinstance(payload, (bytes, str)) else str(payload)
    if isinstance(body, str):
        body = body.encode('utf-8', 'replace')
    record = dict(evidence or {})
    record.setdefault('observed_at', iso(datetime.now(timezone.utc)))
    record['url'] = url
    record['status'] = record.get('http_status') or 'ok'
    record['archive'] = archive(body, raw_dir)
    record['bytes'] = len(body)
    records.append(record)
    return body.decode('utf-8', 'replace')


def stavka_slug(team: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', team.lower()).strip('-')


def probe_fixture(fixture: dict, snapshot: dict, src: Sources, raw_dir: Path,
                  standings_rows: list, now: datetime) -> dict:
    records: list = []
    teams = fixture.get('teams') or []
    start = fixture.get('start')
    findings = {
        'fixture_id': str(fixture.get('id')),
        'teams': teams,
        'start': start,
        'competition': fixture.get('competition'),
        'current_pick': fixture.get('pick'),
        'current_method': fixture.get('method'),
        'reads': records,
        'stavka_readings': [],
        'egw_readings': [],
        'hltv_betting_rows': [],
        'hltv_fan_vote_refused': None,
        'polymarket_quotes': [],
        'pinnacle_hits': [],
        'access_checks': [],
        'valve_identity_candidates': [],
        'verdict': None,
    }
    if len(teams) != 2 or not start:
        findings['verdict'] = 'Fixture row lacks the two team labels or the UTC start; nothing probed.'
        return findings

    # --- Stavka.tv / Winline licensed book listing (slug discovery + reads) ---
    try:
        day = dt(start).date()
    except Exception:
        day = now.date()
    slugs = []
    t1, t2 = stavka_slug(teams[0]), stavka_slug(teams[1])
    for offset in (-1, 0, 1):
        d = day + timedelta(days=offset)
        stamp = d.strftime('%d-%m-%Y')
        for pair in (f'{t1}-{t2}', f'{t2}-{t1}'):
            url = f'https://stavka.tv/matches/csgo/{stamp}-{pair}'
            if url not in slugs:
                slugs.append(url)
    for url in slugs:
        html = read(src, 'Stavka listing probe', url, raw_dir, records)
        if not html:
            continue
        if 'Ошибка 404' in html or 'page not found' in html.lower():
            records[-1]['status'] = '404 recorded as a miss'
            continue
        try:
            for reading in parse_listing(html):
                reading['url'] = url
                reading['placeholder'] = [float(x) for x in reading['odds']] == list(PLACEHOLDER)
                findings['stavka_readings'].append(reading)
        except Exception as exc:
            records[-1]['parse_error'] = str(exc)[:200]

    # --- EGamersWorld listing pages (placeholder refusal re-check) ---
    egw_urls = []
    receipts_doc = Path('data/book-receipts.json')
    try:
        doc = json.loads(receipts_doc.read_text())
        for entry in (doc.get('rejected_listings') or []) + (doc.get('receipts') or []):
            if str(entry.get('fixture_id')) == str(fixture.get('id')) and entry.get('url') \
                    and 'egamersworld.com' in entry.get('url', ''):
                egw_urls.append(entry['url'])
    except (OSError, ValueError):
        pass
    for url in dict.fromkeys(egw_urls):
        html = read(src, 'EGamersWorld listing probe', url, raw_dir, records)
        if not html:
            continue
        try:
            readings = parse_listing(html)
        except Exception as exc:
            records[-1]['parse_error'] = str(exc)[:200]
            readings = []
        if not readings:
            stripped = re.sub(r'<[^>]+>', ' ', html)
            pair = ODDS_PAIR_RE.search(stripped[:20000])
            findings['egw_readings'].append({
                'url': url, 'status': 'no bound asymmetric pair parsed',
                'first_pair_seen': list(pair.groups()) if pair else None,
                'placeholder_18': ('1.8' in stripped and stripped.count('1.8 Make a bet 1.8') > 0),
            })
        for reading in readings:
            reading['url'] = url
            findings['egw_readings'].append(reading)

    # --- HLTV fixture page: betting table and (refused) fan vote ---
    hltv_source = (fixture.get('hltv_context') or {}).get('source')
    if hltv_source:
        html = read(src, 'HLTV fixture probe', hltv_source, raw_dir, records)
        if html:
            section = html.split('id="betting"', 1)[-1][:20000] if 'id="betting"' in html else html
            for m in ODDS_PAIR_RE.finditer(re.sub(r'<[^>]+>', ' ', section)):
                a, b = float(m.group(1)), float(m.group(2))
                if (a, b) != PLACEHOLDER and a != b:
                    findings['hltv_betting_rows'].append([a, b])
            if 'noOdds' in html or 'No promocode available' in html:
                findings['hltv_betting_rows_note'] = ('Betting table renders the promotional/no-odds cell; '
                                                     'no numeric two-way line in this response.')
            vote = re.search(r'Pick a winner(.{0,600})', re.sub(r'<[^>]+>', ' ', html), re.S)
            if vote:
                values = [float(v) for v in FAN_VOTE_RE.findall(vote.group(1))]
                findings['hltv_fan_vote_refused'] = {
                    'displayed_percentages': values[:2],
                    'reason': 'HLTV fan vote / pick percentages are recorded as refused context and never '
                              'used as a probability input (project policy).',
                    'url': hltv_source,
                }

    # --- Polymarket: row attempt markets + team search ---
    market_ids = set()
    for attempt in fixture.get('attempts') or []:
        for key in ('url', 'api_url'):
            for m in re.finditer(r'gamma-api\.polymarket\.com/markets/(\d+)', str(attempt.get(key) or '')):
                market_ids.add(m.group(1))
        quote = attempt.get('rejected_quote') or {}
        if quote.get('id'):
            market_ids.add(str(quote['id']))
    for market_id in sorted(market_ids):
        url = f'https://gamma-api.polymarket.com/markets/{market_id}'
        html = read(src, 'Polymarket market probe', url, raw_dir, records)
        if not html:
            continue
        try:
            market = json.loads(html)
            bid = market.get('bestBid')
            ask = market.get('bestAsk')
            spread = None if bid is None or ask is None else abs(float(ask) - float(bid))
            findings['polymarket_quotes'].append({
                'id': str(market_id),
                'question': market.get('question'),
                'outcomePrices': market.get('outcomePrices'),
                'bestBid': bid, 'bestAsk': ask, 'spread': spread,
                'liquidity': market.get('liquidity'),
                'acceptingOrders': market.get('acceptingOrders'),
                'updatedAt': market.get('updatedAt'),
                'url': url,
                'gate': ('pass-candidate' if spread is not None and spread <= 0.60
                         and float(market.get('liquidity') or 0) >= 100 else 'refused-by-gate'),
            })
        except ValueError:
            records[-1]['parse_error'] = 'response was not a market JSON object'

    # --- Pinnacle guest feed: exact pair + start scan ---
    feed = read(src, 'Pinnacle feed probe',
                'https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight',
                raw_dir, records)
    if feed:
        try:
            data = json.loads(feed)
            text = json.dumps(data)
            hits = [team for team in teams if re.search(re.escape(team), text, re.I)]
            findings['pinnacle_hits'] = {
                'team_labels_found': hits,
                'verdict': ('exact pair present; needs manual line extraction' if len(hits) == 2
                            else 'no exact pair in retrieved feed'),
            }
        except ValueError:
            findings['pinnacle_hits'] = {'verdict': 'feed response was not JSON'}

    # --- Access-only checks for the remaining operators ---
    for label, url in (
            ('GG.BET', 'https://gg.bet/en/esports/counter-strike'),
            ('Thunderpick', 'https://thunderpick.io/esports/cs2-betting'),
            ('bo3.gg search', 'https://bo3.gg/matches?search=' + re.sub(r'\s+', '+', teams[0]))):
        html = read(src, label + ' access probe', url, raw_dir, records)
        findings['access_checks'].append({
            'provider': label, 'url': url,
            'status': 'read' if html else 'unreadable or refused',
            'note': ('Access check only; no validated two-way series quote extracted. A refusal is a '
                     'collection limitation, not evidence that no odds exist.'),
        })

    # --- HLTV dated Valve ranking: identity candidates only ---
    for row in standings_rows or []:
        roster = [p.strip() for p in (row.get('roster') or []) if p.strip()]
        label_hit = any(norm(row.get('name') or '') == norm(team) for team in teams)
        if not roster:
            continue
        for idx, team in enumerate(teams):
            lineup = []
            for rank in (fixture.get('hltv_context') or {}).get('lineups') or []:
                if norm(rank.get('team') or '') == norm(team):
                    lineup = [p.strip() for p in rank.get('players') or []]
            shared = {norm(p) for p in roster} & {norm(p) for p in lineup}
            if label_hit or len(shared) >= 3:
                findings['valve_identity_candidates'].append({
                    'fixture_team': team,
                    'ranking_label': row.get('name'),
                    'points': row.get('points'),
                    'rank': row.get('standing'),
                    'players': roster,
                    'shared_players': sorted(shared),
                    'label_exact_match': label_hit,
                    'status': 'candidate only — NOT registered; requires ≥3 overlapping players with '
                              'the row\'s own HLTV lineup and a primary-source identity link before use',
                })

    # --- Verdict: everything the probe found, nothing it did not ---
    publishable = [r for r in findings['stavka_readings'] + findings['egw_readings']
                   if not r.get('placeholder') and r.get('bound_to_labels')]
    if publishable:
        findings['verdict'] = ('A bound asymmetric two-way pair is present on a listing page; '
                               'integration requires a dated receipt with identity evidence.')
    elif findings['valve_identity_candidates']:
        findings['verdict'] = ('No market line; Valve-points identity candidate(s) found and reported '
                               'for manual verification only.')
    else:
        findings['verdict'] = ('No publishable line and no new Valve-points identity found in this run. '
                               'The row keeps its research-only pick with blank percentages and its '
                               'source-linked limitation.')
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', default='data/latest.json')
    parser.add_argument('--output', default='research/harvest-4fd13975')
    args = parser.parse_args()
    out = Path(args.output)
    raw_dir = out / 'raw'
    out.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    snapshot = json.loads(Path(args.snapshot).read_text())
    now = datetime.now(timezone.utc)
    src = Sources(now)

    targets = [m for m in snapshot.get('matches', [])
               if m.get('state') == 'open' and not m.get('probabilities')]
    report = {
        'probe': 'scripts/probe_4fd13975.py',
        'observed_at': iso(now),
        'snapshot_generated_at': snapshot.get('generated_at'),
        'open_rows_without_probability': [str(m.get('id')) for m in targets],
        'fixtures': [],
    }
    standings_rows = []
    try:
        parsed, _meta, problem = vrs_mirror.fetch(src, now)
        if isinstance(parsed, dict):
            standings_rows = parsed.get('teams') or []
            report['valve_ranking_as_of'] = parsed.get('as_of')
            report['valve_ranking_meta'] = _meta
        if problem:
            report['valve_ranking_error'] = problem
        report['valve_ranking_rows_seen'] = len(standings_rows)
    except Exception as exc:
        report['valve_ranking_error'] = str(exc)[:300]

    for fixture in targets:
        report['fixtures'].append(probe_fixture(fixture, snapshot, src, raw_dir, standings_rows, now))

    (out / 'unresolved-probe.json').write_text(json.dumps(report, indent=1, ensure_ascii=False))
    lines = ['# Session 4fd13975 — unresolved-row research probe', '',
             f'Observed {report["observed_at"]}. Snapshot `{report["snapshot_generated_at"]}`. '
             f'{len(targets)} open row(s) without a win probability: '
             + ', '.join(report['open_rows_without_probability']) + '.', '']
    for finding in report['fixtures']:
        lines.append(f'## {finding["fixture_id"]} — {" vs ".join(finding["teams"])} '
                     f'({finding["start"]})')
        lines.append(f'- Current board state: pick `{finding["current_pick"]}` '
                     f'via `{finding["current_method"]}`.')
        lines.append(f'- Verdict: {finding["verdict"]}')
        if finding['stavka_readings']:
            for reading in finding['stavka_readings']:
                lines.append(f'- Stavka reading on `{reading.get("url")}`: odds {reading.get("odds")}, '
                             f'bound={reading.get("bound_to_labels")}, start {reading.get("start")}.')
        if finding['egw_readings']:
            for reading in finding['egw_readings']:
                lines.append(f'- EGamersWorld `{reading.get("url")}`: '
                             + (f'odds {reading.get("odds")}' if reading.get('odds')
                                else str(reading.get('status'))))
        if finding['hltv_betting_rows']:
            lines.append(f'- HLTV betting rows: {finding["hltv_betting_rows"]}')
        else:
            lines.append('- HLTV betting table: no numeric two-way line in this response.')
        if finding['hltv_fan_vote_refused']:
            vote = finding['hltv_fan_vote_refused']
            lines.append(f'- HLTV fan vote {vote["displayed_percentages"]} recorded as refused context.')
        for quote in finding['polymarket_quotes']:
            lines.append(f'- Polymarket {quote["id"]}: spread {quote["spread"]}, '
                         f'liquidity {quote["liquidity"]}, gate {quote["gate"]}.')
        for candidate in finding['valve_identity_candidates']:
            lines.append(f'- Valve identity candidate: fixture team `{candidate["fixture_team"]}` vs '
                         f'ranking label `{candidate["ranking_label"]}` '
                         f'({candidate["points"]} pts) sharing {candidate["shared_players"]}. '
                         f'{candidate["status"]}')
        lines.append(f'- Reads recorded: {len(finding["reads"])} (raw bytes archived under `raw/`).')
        lines.append('')
    (out / 'REPORT.md').write_text('\n'.join(lines))
    print(json.dumps({'fixtures_probed': len(targets),
                      'output': str(out),
                      'valve_ranking_rows_seen': report.get('valve_ranking_rows_seen')}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
