"""Public read-only refresh. Source failures are data, never synthetic probabilities."""
import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from scripts.core import (HOTSPAWN,FIXTURES,PIN,GAMMA,dt,iso,fresh,hotspawn_state,
    normalize_fixtures,polymarket_candidates,pinnacle_candidates,resolve)


class Sources:
    def __init__(self, now):
        self.now = now
        self.log = []
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)'

    def get(self, name, url, as_json=True):
        record = {'name':name, 'url':url, 'checked_at':iso(self.now)}
        self.log.append(record)
        for attempt in range(2):
            try:
                r = self.session.get(url, timeout=(10,30))
                record['http_status'] = r.status_code
                r.raise_for_status()
                age = max(0, int(r.headers.get('Age', 0)))
                observed = datetime.now(timezone.utc) - timedelta(seconds=age)
                record.update(status='ok', observed_at=iso(observed), cache_age_seconds=age,
                    sha256=hashlib.sha256(r.content).hexdigest(), bytes=len(r.content))
                if not fresh(observed, self.now):
                    raise ValueError('Source HTTP cache is over eight hours old')
                body = r.json() if as_json else r.text
                if not as_json and any(x in body.lower() for x in ['not accepting visitors from your region', 'just a moment...', 'access denied']):
                    raise ValueError('Access restriction or challenge page; not usable evidence')
                return body, record
            except (requests.RequestException,ValueError) as e:
                record.update(status='error', error=str(e)[:250])
                # Never bypass access restrictions or repeatedly hit denied sources.
                if record.get('http_status') in (401,403,404,429) or attempt == 1:
                    raise ValueError(record['error']) from e
                time.sleep(2)


def issue(code, message, source):
    return {'code':code, 'message':message, 'source':source}


def run(previous=None):
    now = datetime.now(timezone.utc)
    src = Sources(now)
    flags = []
    html_rows, links, api_rows = None, {}, None
    html_observed = None
    try:
        html, receipt = src.get('Hotspawn CS2 lobby',HOTSPAWN,False)
        html_rows, links = hotspawn_state(html)
        html_observed = receipt['observed_at']
    except ValueError as e:
        flags.append(issue('lobby',str(e),HOTSPAWN))
    try:
        api_rows, receipt = src.get('Hotspawn CS2 fixtures',FIXTURES)
        if not isinstance(api_rows,list):
            raise ValueError('Fixture API is no longer a complete array; pagination must be reviewed')
        fixture_observed = receipt['observed_at']
    except ValueError as e:
        api_rows = None
        flags.append(issue('fixtures',str(e),FIXTURES))
        fixture_observed = html_observed
    raw = api_rows if api_rows is not None else html_rows
    coverage = 'verified' if api_rows is not None and html_rows is not None else 'partial'
    if api_rows is not None and html_rows is not None:
        a = {str(x['id']) for x in api_rows if x.get('sport_alias')=='cs2'}
        h = {str(x['id']) for x in html_rows if x.get('sport_alias')=='cs2'}
        if a != h:
            coverage = 'partial'
            flags.append(issue('coverage_difference',f'API and cached page differ: {len(a-h)} API-only and {len(h-a)} page-only fixtures. Union retained; full current lobby parity unverified.',HOTSPAWN))
            raw = api_rows + [x for x in html_rows if str(x['id']) not in a and x.get('sport_alias')=='cs2']
    if raw is None:
        if previous is None:
            raise RuntimeError('No verified Hotspawn snapshot is available; refuse empty publish')
        previous['last_attempt_at'] = iso(now)
        previous['coverage'] = 'stale'
        previous['source_checks'] = src.log
        previous['issues'] = flags + [issue('retained','Hotspawn refresh failed. Last successful snapshot retained, not a current list.',HOTSPAWN)]
        # Never renew evidence freshness because a refresh failed.
        return previous
    if not raw and previous and previous.get('matches'):
        previous.update(last_attempt_at=iso(now), coverage='stale', source_checks=src.log,
            issues=flags+[issue('unexpected_empty','Unexpected empty lobby; previous list retained for review.',HOTSPAWN)])
        return previous
    matches = normalize_fixtures(raw,links,now)
    open_matches = [m for m in matches if m['state']=='open']
    try:
        sports, _ = src.get('Polymarket sports registry',GAMMA+'/sports')
        cs2 = [s for s in sports if s.get('sport')=='cs2']
        if len(cs2)!=1:
            raise ValueError('CS2 registry is ambiguous or absent')
        events, seen_ids = [], set()
        for offset in range(0,5000,100):
            params = urlencode({'series_id':cs2[0]['series'],'active':'true','closed':'false',
                'end_date_min': now.strftime('%Y-%m-%dT00:00:00Z'), 'limit':100,'offset':offset, 'order':'id','ascending':'true'})
            batch, receipt = src.get(f'Polymarket events page {offset//100+1}',GAMMA+'/events?'+params)
            if not isinstance(batch,list):
                raise ValueError('Unexpected Polymarket pagination schema')
            ids = {str(e['id']) for e in batch}
            if ids & seen_ids:
                raise ValueError('Repeated exchange event page; coverage unverified')
            seen_ids |= ids
            events.extend(polymarket_candidates(batch,receipt['observed_at']))
            if len(batch)<100:
                break
        else:
            raise ValueError('Exchange pagination safety cap reached')
        for m in open_matches:
            resolve(m,events,'Polymarket',now)
    except (ValueError,KeyError,TypeError) as e:
        flags.append(issue('exchange',str(e),GAMMA+'/sports'))
        for m in open_matches:
            m['attempts'].append({'provider':'Polymarket','status':'error','reason':str(e),'url':GAMMA+'/sports'})

    unresolved = [m for m in open_matches if m['probabilities'] is None]
    if unresolved:
        # Research fallback order: HLTV first, then directly verified esportsbook lines.
        hltv = 'https://www.hltv.org/matches'
        try:
            page, _ = src.get('HLTV fallback discovery',hltv,False)
            soup = BeautifulSoup(page,'html.parser')
            match_urls = sorted({'https://www.hltv.org'+a['href'] for a in soup.select('a[href^="/matches/"]')})
            hltv_reason = (f'HLTV reachable ({len(match_urls)} match links), but no directly verified bookmaker price or validated statistical model was established. Crowd votes and ranks are not win probabilities.')
            status = 'unresolved'
        except ValueError as e:
            hltv_reason = 'HLTV automated access failed: ' + str(e) + '. No rank or crowd-vote probability substituted.'
            status = 'error'
        for m in unresolved:
            m['attempts'].append({'provider':'HLTV','status':status,'reason':hltv_reason,'url':hltv})
        try:
            matchups, mr = src.get('Pinnacle esports fixtures',PIN+'/sports/12/matchups?withSpecials=false')
            lines, lr = src.get('Pinnacle esports moneylines',PIN+'/sports/12/markets/straight')
            observed = min(mr['observed_at'],lr['observed_at'])
            candidates = pinnacle_candidates(matchups,lines,observed)
            for m in unresolved:
                resolve(m,candidates,'Pinnacle',now)
        except (ValueError,KeyError,TypeError) as e:
            flags.append(issue('pinnacle',str(e),PIN+'/sports/12/markets/straight'))
            for m in unresolved:
                m['attempts'].append({'provider':'Pinnacle','status':'error','reason':str(e),'url':PIN+'/sports/12/markets/straight'})
        unresolved = [m for m in unresolved if m['probabilities'] is None]
        for provider,url in [('Thunderpick','https://thunderpick.io/esports/cs2-betting'),('GG.BET','https://gg.bet/en/esports/counter-strike')]:
            if not unresolved:
                break
            try:
                _, _ = src.get(provider+' fallback access',url,False)
                status, reason = 'unresolved','Page reachable; no verified two-way series-winner adapter. Values withheld rather than guessed from page text.'
            except ValueError as e:
                status, reason = 'error',str(e)
            for m in unresolved:
                m['attempts'].append({'provider':provider,'status':status,'reason':reason,'url':url})
    for m in matches:
        if m['state']!='open':
            m['reason']='Not open for picks according to sourced lock/start/end fields; retained for complete feed visibility.'
        elif m['probabilities'] is None:
            problems = [a['reason'] for a in m['attempts'] if a['provider']=='Polymarket']
            m['reason']=(problems[0] if problems else 'Primary market evidence unavailable.')+' HLTV / esportsbook fallbacks did not establish a verified price.'
    stale_count = sum(m['state']!='open' for m in matches)
    if stale_count:
        flags.append(issue('feed_status',f'{stale_count} feed entries are not open by sourced timestamps/status. They remain in All matches and are not treated as future picks.',FIXTURES))
    return {'schema_version':1,'generated_at':iso(now),'last_attempt_at':iso(now),
        'fixtures_observed_at':fixture_observed, 'coverage':coverage,
        'refresh_hours':6,'stale_after_hours':8, 'matches':matches,
        'source_checks':src.log,'issues':flags,
        'coverage_counts':{'api':len(api_rows) if api_rows is not None else None,'page':len(html_rows) if html_rows is not None else None,'retained':len(matches)},
        'fixture_evidence':[{k:v for k,v in x.items() if 'picked' not in k and k!='total_picks'} for x in raw if x.get('sport_alias')=='cs2']}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='runtime/latest.json')
    parser.add_argument('--previous',default='data/latest.json')
    args=parser.parse_args()
    previous_path = Path(args.output) if Path(args.output).exists() else Path(args.previous)
    previous=json.loads(previous_path.read_text()) if previous_path.exists() else None
    data=run(previous)
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n');os.replace(tmp,path)
    print(json.dumps({'coverage':data['coverage'],'matches':len(data['matches']),
        'priced':sum(m['probabilities'] is not None for m in data['matches']),
        'unresolved':sum(m['state']=='open' and m['probabilities'] is None for m in data['matches'])}))

if __name__=='__main__':
    main()
