"""Public read-only refresh. Source failures are data, never synthetic probabilities."""
import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlencode,urlsplit
import requests
from bs4 import BeautifulSoup
from scripts.core import (HOTSPAWN,FIXTURES,PIN,GAMMA,dt,iso,fresh,hotspawn_state,
    normalize_fixtures,polymarket_candidates,pinnacle_candidates,resolve)


class Sources:
    def __init__(self, now):
        self.now = now
        self.log = []
        self.blocked_hosts = {}
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)'

    def get(self, name, url, as_json=True):
        record = {'name':name, 'url':url, 'checked_at':iso(datetime.now(timezone.utc))}
        self.log.append(record)
        host=urlsplit(url).netloc
        if host in self.blocked_hosts:
            record.update(status='error',error='Skipped after earlier access/rate restriction on this host: '+self.blocked_hosts[host])
            raise ValueError(record['error'])
        for attempt in range(2):
            try:
                r = self.session.get(url, timeout=(10,30))
                record['http_status'] = r.status_code
                r.raise_for_status()
                age_header = r.headers.get('Age')
                age = max(0, int(age_header)) if age_header is not None else None
                retrieved = datetime.now(timezone.utc)
                observed = retrieved - timedelta(seconds=age or 0)
                record.pop('error', None)
                record.update(status='ok', retrieved_at=iso(retrieved), observed_at=iso(observed), cache_age_seconds=age,
                    sha256=hashlib.sha256(r.content).hexdigest(), bytes=len(r.content))
                if not fresh(observed, retrieved):
                    raise ValueError('Source HTTP cache is over eight hours old')
                archive = Path('runtime/sources')
                archive.mkdir(parents=True, exist_ok=True)
                (archive / (record['sha256'] + ('.json' if as_json else '.html'))).write_bytes(r.content)
                body = r.json() if as_json else r.text
                if not as_json and any(x in body.lower() for x in ['not accepting visitors from your region', 'just a moment...', 'access denied']):
                    raise ValueError('Access restriction or challenge page; not usable evidence')
                return body, record
            except (requests.RequestException,ValueError) as e:
                record.update(status='error', error=str(e)[:250])
                # Never bypass access restrictions or repeatedly hit denied sources.
                if record.get('http_status') in (401,403,429):
                    self.blocked_hosts[host]=str(record['http_status'])
                if record.get('http_status') in (401,403,404,429) or attempt == 1:
                    raise ValueError(record['error']) from e
                time.sleep(2)


def issue(code, message, source):
    return {'code':code, 'message':message, 'source':source}


def run(previous=None):
    now = datetime.now(timezone.utc)
    src = Sources(now)
    from scripts.inventory import discover
    inventory = discover(src, now, previous)
    if 'retained' in inventory:
        return inventory['retained']
    flags, matches = inventory['flags'], inventory['matches']
    raw, fixture_observed = inventory['raw'], inventory['observed_at']
    coverage = inventory['coverage']
    open_matches = [m for m in matches if m['state']=='open' and not m.get('resolution_blocked')]
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
            candidates = polymarket_candidates(batch,receipt['observed_at'])
            for candidate in candidates:
                candidate['source_receipts'] = [receipt.copy()]
            events.extend(candidates)
            if len(batch)<100:
                break
        else:
            raise ValueError('Exchange pagination safety cap reached')
        for m in open_matches:
            resolve(m,events,'Polymarket',datetime.now(timezone.utc))
    except (ValueError,KeyError,TypeError) as e:
        flags.append(issue('exchange',str(e),GAMMA+'/sports'))
        for m in open_matches:
            m['attempts'].append({'provider':'Polymarket','status':'error','reason':str(e),'url':GAMMA+'/sports'})

    unresolved = [m for m in open_matches if m['probabilities'] is None]
    if unresolved:
        # Research fallback order: HLTV first, then directly verified esportsbook lines.
        from scripts.hltv import research
        research(unresolved,src)
        try:
            matchups, mr = src.get('Pinnacle esports fixtures',PIN+'/sports/12/matchups?withSpecials=false')
            lines, lr = src.get('Pinnacle esports moneylines',PIN+'/sports/12/markets/straight')
            observed = min(mr['observed_at'],lr['observed_at'],key=dt)
            candidates = pinnacle_candidates(matchups,lines,observed)
            for candidate in candidates:
                candidate['source_receipts'] = [mr.copy(),lr.copy()]
            for m in unresolved:
                resolve(m,candidates,'Pinnacle',datetime.now(timezone.utc))
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
                status, reason = 'unresolved','Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds.'
            except ValueError as e:
                status, reason = 'error',str(e)
            for m in unresolved:
                m['attempts'].append({'provider':provider,'status':status,'reason':reason,'url':url})
    completed = datetime.now(timezone.utc)
    for m in matches:
        if any(m.get(field) and dt(m[field]) <= completed for field in ('lock','start')):
            m['state']='not_open'
            m['probabilities']=m['fair_odds']=m['pick']=m['method']=None
        if m['state']!='open':
            m['reason']='Not open for picks according to sourced lock/start/end fields; retained for complete feed visibility.'
        elif m['probabilities'] is None and not m.get('resolution_blocked'):
            problems = [a['reason'] for a in m['attempts'] if a['provider']=='Polymarket']
            m['reason']=(problems[0] if problems else 'Primary market evidence unavailable.')+' HLTV / esportsbook fallbacks did not establish a verified price.'
    stale_count = sum(m['state']!='open' for m in matches)
    if stale_count:
        flags.append(issue('feed_status',f'{stale_count} feed entries are not open by sourced timestamps/status. They remain in All matches and are not treated as future picks.',FIXTURES))
    return {'schema_version':2,'generated_at':iso(completed),'last_attempt_at':iso(completed),
        'refresh_started_at':iso(now),
        'fixtures_observed_at':fixture_observed, 'coverage':coverage,
        'refresh_hours':6,'stale_after_hours':8, 'matches':matches,
        'source_checks':src.log,'issues':flags,
        'coverage_counts':inventory['counts'], 'fixture_conflicts':inventory['conflicts'],
        'inventory_changes':inventory['changes'],
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
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+'\n');os.replace(tmp,path)
    print(json.dumps({'coverage':data['coverage'],'matches':len(data['matches']),
        'priced':sum(m['probabilities'] is not None for m in data['matches']),
        'unresolved':sum(m['state']=='open' and m['probabilities'] is None for m in data['matches'])}))

if __name__=='__main__':
    main()
