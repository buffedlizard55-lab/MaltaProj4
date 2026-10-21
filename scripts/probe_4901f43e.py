"""Reachability probe for the exact sources session 4901f43e read, session-scoped.

This session read HLTV match, team and results pages, plus bo3.gg, dfrag.gg,
Strafe, maisesports and Polymarket's gamma API, through the authoring
environment's fetch path. The scheduled collector runs on a GitHub Actions
runner, and previous sessions recorded that the runner is refused by some of
those hosts (HLTV answers 403 to ``/search`` and ``/team/...``; EGamersWorld
answers 403). That asymmetry is the reason fixtures still ship without a
percentage, so it is worth measuring instead of repeating.

The probe asks the runner for every URL this session cited, with the
repository's own project User-Agent, and records:

* the HTTP status and the sha256 of the body,
* whether a marker string that this session saw on the page is present, which is
  what turns "status 200" into "the runner can actually re-read this evidence",
* one retry after a short wait for 429/5xx, never a bypass.

No bypass is attempted: no rotated user agents, no proxy, no cache-busting
tricks. A host that refuses the project's identity is recorded as refused, which
is the honest result and the reason the affected row keeps a blank percentage.

Usage::

    python -m scripts.probe_4901f43e --output research/harvest-4901f43e/probe.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

USER_AGENT = 'Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)'

# (label, url, marker this session actually saw on the page)
TARGETS = [
    ('hltv-match-zetta-los-ninos',
     'https://www.hltv.org/matches/2399865/zetta-vs-los-ninos-cct-2026-south-america-series-7',
     'Swiss round 5'),
    ('hltv-match-alliance-faze-served-for-2399867',
     'https://www.hltv.org/matches/2399867/zetta-vs-los-ninos-cct-2026-south-america-series-7',
     'RLG Tesla Cup 2026'),
    ('hltv-match-benched-gods-titanflow-postponed',
     'https://www.hltv.org/matches/2399696/benched-gods-vs-titanflow-cct-2026-challengers-europe-series-8',
     'Match postponed'),
    ('hltv-match-ground-zero-off-chops',
     'https://www.hltv.org/matches/2399888/ground-zero-vs-off-chops-dfrag-invitational-2026',
     'DFRAG Invitational 2026'),
    ('hltv-team-zetta',
     'https://www.hltv.org/team/13833/zetta',
     'Who plays for Zetta?'),
    ('hltv-event-results-cct-sa-7',
     'https://www.hltv.org/results?event=9452',
     'zetta-vs-realgotis22'),
    ('polymarket-market-6001634',
     'https://gamma-api.polymarket.com/markets/6001634',
     'cs2-ale1-ln-2026-10-21'),
    ('polymarket-event-1227336',
     'https://gamma-api.polymarket.com/events/1227336',
     'Alianza Lima Esports'),
    ('valve-vrs-357-zetta',
     'https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/'
     'live/2026/details/2026_10_05/0357--zetta--antuanette-babyrage-notjuanjo-slayerhz-zockie.md',
     'Antuanette'),
    ('dfrag-off-chops-rebrand',
     'https://dfrag.gg/counterstrike/news/thunder-downunder-core-rebrands-as-off-chops/',
     'Off Chops'),
    ('bo3gg-alianza-lima-lineup',
     'https://bo3.gg/matches/damajuana-vs-alianza-lima-esports-14-10-2026',
     'NotJuanjo'),
    ('strafe-event-cct-sa-7',
     'https://www.strafe.com/event/2026-cct-south-america-series-7-75c83e/',
     'Alianza Lima Esports'),
    ('maisesports-ale-realgotis22',
     'https://maisesports.com.br/partidas/realgotis22-vs-alianza-lima-esports-2026-10-19',
     'Alianza Lima Esports'),
    ('egamersworld-benched-gods-titanflow',
     'https://egamersworld.com/counterstrike/match/rW6Ymkl0D/benched-gods-vs-titanflow-EcLgERbZn',
     'benched gods'),
    ('liquipedia-zetta-absent',
     'https://liquipedia.net/counterstrike/Zetta',
     'no text in this page'),
]


def probe_one(session: requests.Session, label: str, url: str, marker: str) -> dict:
    attempts = []
    for attempt in (1, 2):
        started = datetime.now(timezone.utc)
        try:
            response = session.get(url, timeout=(10, 45), allow_redirects=True)
            body = response.text
            record = {
                'attempt': attempt,
                'requested_at': started.isoformat().replace('+00:00', 'Z'),
                'status': response.status_code,
                'final_url': response.url,
                'bytes': len(response.content),
                'body_sha256': hashlib.sha256(response.content).hexdigest(),
                'marker_present': marker.lower() in body.lower(),
                'marker': marker,
            }
            attempts.append(record)
            if response.status_code < 400 or response.status_code in (400, 401, 403, 404):
                break
        except requests.RequestException as exc:
            attempts.append({
                'attempt': attempt,
                'requested_at': started.isoformat().replace('+00:00', 'Z'),
                'status': None,
                'error': '%s: %s' % (type(exc).__name__, exc),
                'marker_present': False,
                'marker': marker,
            })
        time.sleep(5)
    last = attempts[-1]
    readable = bool(last.get('status') == 200 and last.get('marker_present'))
    return {
        'label': label,
        'url': url,
        'readable_from_runner': readable,
        'classification': ('readable' if readable else
                           'refused' if last.get('status') in (401, 403) else
                           'error' if last.get('status') is None else
                           'served-without-marker' if last.get('status') == 200 else
                           'unavailable'),
        'attempts': attempts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept'] = 'text/html,application/json;q=0.9,*/*;q=0.8'

    results = [probe_one(session, label, url, marker) for label, url, marker in TARGETS]
    counts: dict[str, int] = {}
    for item in results:
        counts[item['classification']] = counts.get(item['classification'], 0) + 1

    doc = {
        'schema_version': 1,
        'probe': 'scripts/probe_4901f43e.py',
        'session': '4901f43e',
        'user_agent': USER_AGENT,
        'ran_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'purpose': ('Record which of the sources cited in '
                    'research/session-4901f43e/receipts-2026-10-21.json the scheduled collector '
                    'can re-read from a GitHub Actions runner. A host that refuses is recorded as '
                    'refused; no bypass is attempted, and a refused host is a documented reason for '
                    'a blank percentage rather than a licence to infer one.'),
        'counts': counts,
        'results': results,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n')
    for item in results:
        print('%-22s %-52s %s' % (item['classification'], item['label'],
                                  item['attempts'][-1].get('status')))
    print('\ncounts: ' + json.dumps(counts, sort_keys=True))


if __name__ == '__main__':
    main()
