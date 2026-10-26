"""Session 32efbb66, light HLTV team-page markup probe (non-publishing).

The full harvest probe's HLTV section was rate-limited (HTTP 403, host
blocked for the run) because it issued a second HLTV sweep minutes after the
production refresh from the same runner address - the documented pacing
limit, worked as designed. This probe is deliberately tiny: three team
pages, nothing else, in its own run, so the markup question can be answered
without competing with a refresh.

Question being measured: does an HLTV *team* page publish recent completed
results in markup that a fail-closed parser can read (the production
``past_results`` parser reads match pages only)? If yes, the final
recent-form research tier can be extended to fixtures HLTV has no match
page for - the exact low-tier case that currently falls through.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup

from scripts.core import norm
from scripts.refresh import Sources
from scripts import hltv

TEAMS = [('FaZe', 'https://www.hltv.org/team/6667/faze'), ('HAVU', None), ('ILLYRIANS', None)]
OUT = Path('research/session-32efbb66')
RESULT_HINT = re.compile(r'result|past-match|recent', re.I)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    src = Sources(datetime.now(timezone.utc))
    report = {'probed_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'), 'teams': []}
    for team, known_url in TEAMS:
        row = {'team': team}
        try:
            url = known_url
            if url is None:
                listing, _ = src.get('HLTV team search ' + team, hltv.SEARCH + quote(team), False)
                candidates = {u: l for u, l in hltv.search_teams(listing).items() if norm(l) == norm(team)}
                if len(candidates) != 1:
                    row['error'] = '%d exact-label team pages' % len(candidates)
                    report['teams'].append(row)
                    continue
                url = next(iter(candidates))
            page, receipt = src.get('HLTV team page ' + team, url, False)
            row['url'], row['observed_at'] = url, receipt['observed_at']
            soup = BeautifulSoup(page, 'html.parser')
            row['profile'] = hltv.team_profile(page, team)
            row['match_page_parser_on_team_page'] = hltv.past_results(soup)
            classes = {}
            for el in soup.find_all(True):
                for cls in el.get('class') or []:
                    if RESULT_HINT.search(cls):
                        classes[cls] = classes.get(cls, 0) + 1
            row['resultish_classes'] = dict(sorted(classes.items(), key=lambda kv: -kv[1])[:40])
            snippets = {}
            for cls in list(classes)[:6]:
                el = soup.select_one('.' + cls)
                if el is not None:
                    snippets[cls] = str(el)[:8000]
            row['snippets'] = snippets
            slug = re.sub(r'[^a-z0-9]+', '-', norm(team))[:40] or 'team'
            (OUT / ('hltv-team-%s.html' % slug)).write_text(page[:600_000])
        except ValueError as e:
            row['error'] = str(e)[:300]
        report['teams'].append(row)
    report['source_log'] = src.log
    (OUT / 'team-page-probe.json').write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps({'teams_read': sum(1 for r in report['teams'] if 'url' in r),
                      'parser_rows': {r['team']: sum(len(v) for v in (r.get('match_page_parser_on_team_page') or {}).values())
                                      for r in report['teams']}}))


if __name__ == '__main__':
    main()
