"""Dated, reproducible reachability probe for pre-match CS2 line sources.

Why this exists
---------------
The site has to tell the reader *why* a match carries a line or does not, and
that answer changes as operators change their access rules. This probe reads a
fixed, public list of endpoints **once each**, on GitHub's egress (the only
place this project can reach them), and records what came back: HTTP status,
final URL, content type, byte count, SHA-256 and a mechanically derived note
(JSON shape, or which literal strings appear in the first bytes). The raw body
of each response is committed beside the report, capped, so every sentence on
the site can be re-checked against the exact bytes the runner saw.

It deliberately makes no judgement. It does not price anything, does not retry
a refusal into a bypass, sends no credentials, and writes only under
``research/session-408eb0af/probe/``. Nothing here can publish a pick.

Run: python -m scripts.probe_sources_408eb0af --output research/session-408eb0af/probe
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from scripts.core import GAMMA, PIN

UA = 'MaltaProj4-cs2-scout/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4; read-only research probe)'
TIMEOUT = 25
BODY_CAP = 128 * 1024

# Every endpoint is a public, unauthenticated page or API that a reader of a
# CS2 fixture could also open. `why` is the question it answers on the site.
TARGETS = (
    ('hotspawn-fixtures-api',
     'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1',
     'Hotspawn feed: does it still return the fixture inventory the board is built from?'),
    ('hotspawn-lobby', 'https://play.hotspawn.com/lobby',
     'Hotspawn lobby page: inventory cross-check.'),
    ('polymarket-sports', GAMMA + '/sports',
     'Polymarket exchange registry: the strict market tier.'),
    ('pinnacle-moneylines', PIN + '/sports/12/markets/straight',
     'Pinnacle guest esports moneylines: the sharp-book tier.'),
    ('pinnacle-matchups', PIN + '/sports/12/matchups?withSpecials=false',
     'Pinnacle fixture feed that binds the moneylines to teams and starts.'),
    ('bo3-matches', 'https://api.bo3.gg/api/v1/matches?page[limit]=100&filter[matches.status][eq]=upcoming',
     'BO3.gg public API: documented route to a Thunderpick series moneyline.'),
    ('hltv-matches', 'https://www.hltv.org/matches',
     'HLTV fixture list: identity, rankings and lineups (never a probability).'),
    ('hltv-ranking', 'https://www.hltv.org/ranking/teams',
     'HLTV world ranking: the dated ranking-order research tier.'),
    ('hltv-valve-ranking', 'https://www.hltv.org/valve-ranking/teams',
     'HLTV dated view of Valve points: the model mirror tier.'),
    ('egamersworld-cs2', 'https://egamersworld.com/counterstrike/matches',
     'EGamersWorld listing: the researched book-listing tier.'),
    ('stavka-cs2', 'https://stavka.tv/matches/csgo',
     'STAVKA listing: second researched book-listing route.'),
    ('thunderpick-cs2', 'https://thunderpick.io/esports/cs2-betting',
     'Thunderpick page: is any price server-rendered for a plain GET?'),
    ('ggbet-cs2', 'https://gg.bet/en/esports/counter-strike',
     'GG.BET page: measured refusal history.'),
    ('bovada-cs2',
     'https://www.bovada.lv/services/sports/event/coupon/events/A/description/esports/counter-strike',
     'Bovada public JSON: candidate independent book source for low-tier fixtures.'),
    ('oddspedia-cs2', 'https://oddspedia.com/api/v1/getMatchList?sport=counter-strike',
     'Oddspedia public JSON: candidate multi-book aggregator for low-tier fixtures.'),
)

# Literal markers worth reporting verbatim. They are counts/booleans only; a
# marker that appears is not evidence of a usable line, only of a page shape.
MARKERS = ('Thunderpick', 'Pinnacle', 'Bet365', 'bet365', '1xBet', 'GG.BET',
           'Betway', 'moneyline', 'Moneyline', 'открыт', 'Make a bet', 'П1',
           'odds', '"coefficient"', 'team_1', 'bookmaker')


def note_for(kind, body):
    """Facts derived mechanically from the captured bytes (``body`` is bytes)."""
    if isinstance(body, str):
        body = body.encode('utf-8')
    facts = []
    if kind == 'json':
        try:
            data = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            return ['declared JSON but did not parse']
        if isinstance(data, list):
            facts.append('JSON array, %d entries' % len(data))
            if data and isinstance(data[0], dict):
                facts.append('first entry keys: ' + ', '.join(sorted(data[0])[:14]))
        elif isinstance(data, dict):
            facts.append('JSON object, keys: ' + ', '.join(sorted(data)[:14]))
        else:
            facts.append('JSON scalar')
    else:
        text = body.decode('utf-8', 'replace')
        facts.append('decoded %d characters' % len(text))
    text = body.decode('utf-8', 'replace')
    hits = ['%s x%d' % (m, text.count(m)) for m in MARKERS if m in text]
    if hits:
        facts.append('markers: ' + ', '.join(hits))
    return facts


def probe(target, session):
    label, url, why = target
    started = datetime.now(timezone.utc)
    record = {'label': label, 'url': url, 'why': why, 'requested_at': started.isoformat().replace('+00:00', 'Z')}
    try:
        response = session.get(url, timeout=TIMEOUT, headers={'User-Agent': UA, 'Accept': '*/*'})
    except Exception as exc:  # network refusal is data, not a crash
        record.update(status=None, error='%s: %s' % (type(exc).__name__, str(exc)[:300]))
        record['elapsed_ms'] = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        return record, b''
    body = response.content or b''
    kind = 'json' if 'json' in (response.headers.get('content-type') or '').lower() else 'html'
    record.update(status=response.status_code,
                  final_url=response.url,
                  content_type=response.headers.get('content-type'),
                  bytes=len(body),
                  sha256=hashlib.sha256(body).hexdigest(),
                  elapsed_ms=int((datetime.now(timezone.utc) - started).total_seconds() * 1000),
                  note=note_for(kind, body[:200000]))
    return record, body[:BODY_CAP]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='research/session-408eb0af/probe')
    args = parser.parse_args(argv)
    out = Path(args.output)
    (out / 'bodies').mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    records = []
    for target in TARGETS:
        record, body = probe(target, session)
        records.append(record)
        if body:
            (out / 'bodies' / (record['label'] + '.body')).write_bytes(body)
        print('%-26s status=%-5s bytes=%s' % (record['label'], record.get('status'), record.get('bytes')))
        time.sleep(2.0)  # polite: never more than one request every two seconds

    generated = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    (out / 'probe.json').write_text(json.dumps({'generated_at': generated, 'user_agent': UA,
                                                'targets': records}, indent=1))
    lines = ['# Pre-match line-source reachability probe', '',
             'Captured on GitHub runners at **%s** (the only egress this project can reach these hosts from).' % generated,
             '', 'One GET per endpoint, no credentials, no retries against a refusal, '
             'bodies committed beside this report under `bodies/`. A row states what came back, not what it means.', '',
             '| Source | HTTP | Bytes | Final host | Note |', '| --- | --- | --- | --- | --- |']
    for record in records:
        from urllib.parse import urlsplit
        host = urlsplit(record.get('final_url') or record['url']).netloc
        note = '; '.join(record.get('note') or []) or record.get('error') or ''
        lines.append('| %s | %s | %s | %s | %s |' % (record['label'], record.get('status') or 'error',
                                                    record.get('bytes') or 0, host, note.replace('|', '/')))
    (out / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
