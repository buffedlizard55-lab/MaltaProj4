"""Measure which HLTV URL shapes this runner may read (session 1d50bcb4).

The form bridge needs a club's own results page
(``https://www.hltv.org/results?team=<id>``). On 2026-10-22 the scheduled
refresh had already read HLTV match pages successfully in the same run, yet
that results page answered HTTP 403 three times, so the bridge published no
line. Rather than guess at the cause, this probe asks the host once for each
URL shape the project would like to use, with the project's own User-Agent and
no other header, and records the status code, byte count and a short excerpt of
what came back. It never retries into a different answer and never rewrites a
request. The output is committed as research, not used as evidence for a pick.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

import requests

UA = 'Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)'
URLS = [
    ('results_team', 'https://www.hltv.org/results?team=13602'),
    ('results_event', 'https://www.hltv.org/results?event=8932'),
    ('team_page', 'https://www.hltv.org/team/13602/morningstar'),
    ('team_results_hash', 'https://www.hltv.org/team/13602/morningstar#tab-results'),
    ('matches_team', 'https://www.hltv.org/matches?team=13602'),
    ('match_page', 'https://www.hltv.org/matches/2399413/betboom-vs-legacy-thunderpick-world-championship-2026'),
    ('ranking', 'https://www.hltv.org/ranking/teams'),
]


def main(path='research/session-1d50bcb4/hltv-probe.json'):
    session = requests.Session()
    session.headers['User-Agent'] = UA
    rows = []
    for name, url in URLS:
        row = {'name': name, 'url': url, 'checked_at': datetime.now(timezone.utc).isoformat()}
        try:
            r = session.get(url, timeout=(10, 30))
            row.update(status=r.status_code, bytes=len(r.content),
                       content_type=r.headers.get('Content-Type'),
                       server=r.headers.get('Server'),
                       cache=r.headers.get('CF-Cache-Status') or r.headers.get('X-Cache'))
            text = r.text
            row['has_result_con'] = 'result-con' in text
            row['title'] = (text.split('<title>', 1)[1].split('</title>', 1)[0].strip()
                            if '<title>' in text else None)
            row['excerpt'] = ' '.join(text[:400].split())[:200]
        except requests.RequestException as exc:
            row.update(status=None, error=str(exc)[:200])
        rows.append(row)
    doc = {'captured_at': datetime.now(timezone.utc).isoformat(), 'user_agent': UA, 'probes': rows}
    with open(path, 'w') as handle:
        json.dump(doc, handle, indent=2)
    print(json.dumps([{'name': r['name'], 'status': r.get('status'), 'bytes': r.get('bytes'),
                       'result_con': r.get('has_result_con')} for r in rows], indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
