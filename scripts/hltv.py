"""HLTV context for missing picks. Its crowd votes and ranks never become odds."""
import json
from pathlib import Path
import re
from bs4 import BeautifulSoup
from scripts.core import iso,orientation,norm

BASE='https://www.hltv.org'
LINEUP_RECEIPTS_PATH=Path(__file__).resolve().parents[1]/'data/lineup-receipts.json'


def lineup_receipts():
    if not LINEUP_RECEIPTS_PATH.exists():
        return []
    return json.loads(LINEUP_RECEIPTS_PATH.read_text()).get('receipts',[])


def fallback_lineups(fixture,receipts=None):
    """Verified same-event HLTV match lineups when live HLTV clears slots to TBA/postponed."""
    existing={x['team']:x['players'] for x in (fixture.get('hltv_context') or {}).get('lineups',[]) if x.get('players')}
    if existing:
        return existing,None
    for receipt in (lineup_receipts() if receipts is None else receipts):
        if str(receipt.get('fixture_id') or '')!=str(fixture.get('id') or ''):
            continue
        if orientation(fixture,receipt.get('teams',[]),receipt.get('start')) is None:
            continue
        mapped={}
        for entry in receipt.get('lineups',[]):
            if entry.get('team') and entry.get('players') and str(entry.get('source') or '').startswith(BASE+'/matches/'):
                mapped[entry['team']]=list(entry['players'])
        if len(mapped)==2:
            return mapped,receipt
    return {},None


def discover(html):
    soup=BeautifulSoup(html,'html.parser');found={}
    for anchor in soup.select('a.match-teams[href^="/matches/"]'):
        teams=[t.get_text(strip=True) for t in anchor.select('.match-teamname')]
        timestamp=anchor.parent.select_one('.match-time[data-unix]')
        if len(teams)!=2 or timestamp is None:continue
        url=BASE+anchor['href']
        found[url]={'teams':teams,'start':iso(timestamp['data-unix']),'url':url}
    if not found: raise ValueError('HLTV match-list selectors returned no verified identities')
    return list(found.values())


def context(html,fixture):
    soup=BeautifulSoup(html,'html.parser')
    clock=soup.select_one('.timeAndEvent .time[data-unix]')
    teams=soup.select('.team1-gradient .teamName, .team2-gradient .teamName')
    names=[t.get_text(strip=True) for t in teams]
    if clock is None or orientation(fixture,names,clock['data-unix']) is None:
        raise ValueError('HLTV detail identity/start does not exactly match the fixture')
    ranks=[]
    for el in soup.select('.teamRanking'):
        team=el.parent.select_one('a[href^="/team/"]')
        rank=el.select_one('.hltv-ranking')
        if not team or norm(team.get_text(strip=True)) not in set(map(norm,fixture['teams'])):continue
        match=re.search(r'#(\d+)',rank.get_text()) if rank else None
        # HLTV prints an explicit "Unranked" badge; a missing badge is not the same thing.
        badge=el.select_one('.ranking-badge.unranked')
        vrs=el.select_one('a.vrs-ranking')
        vrs_match=re.search(r'#(\d+)',vrs.get_text()) if vrs else None
        ranks.append({'team':team.get_text(strip=True),'hltv_rank':int(match.group(1)) if match else None,
            'source':BASE+rank['href'] if rank else None,
            'hltv_unranked':bool(badge is not None and match is None and 'unranked' in badge.get_text().casefold()),
            'vrs_rank_on_hltv':int(vrs_match.group(1)) if vrs_match else None,
            'vrs_source':BASE+vrs['href'] if vrs is not None and vrs.get('href') else None})
    lineups=[]
    for box in soup.select('div.lineups div.lineup'):
        head=box.select_one('.box-headline a[href^="/team/"]') or box.select_one('.box-headline .text-ellipsis')
        players=[p.get_text(strip=True) for p in box.select('td.player .player-compare .text-ellipsis')]
        if head is None or not players:continue
        label=head.get_text(strip=True)
        if norm(label) not in set(map(norm,fixture['teams'])):continue
        lineups.append({'team':label,'players':list(dict.fromkeys(players))[:7]})
    numeric=[]
    for row in soup.select('.match-betting-list tr.provider'):
        cells=row.find_all('td',recursive=False)
        if len(cells)<3:continue
        values=[c.get_text(' ',strip=True) for c in cells[1:3]]
        if all(re.fullmatch(r'\d+\.\d+',v) for v in values):
            numeric.append(values)
    return {'teams':names,'start':iso(clock['data-unix']),'ranks':ranks,'lineups':lineups,
        'numeric_quote_rows':len(numeric),
        'limitation': ('HLTV shows numeric comparison rows, but these are secondary quotes not independently confirmed at an official bookmaker.' if numeric else 'HLTV betting table does not expose a numeric two-way line in this response.')+' Rankings are context only; no calibrated rank-to-win model is applied to HLTV ranks. Lineups only confirm roster identity.'}


def research(matches,src):
    try:
        page,_=src.get('HLTV fallback discovery',BASE+'/matches',False)
        candidates=discover(page)
    except ValueError as e:
        for m in matches:
            m['attempts'].append({'provider':'HLTV','status':'error','reason':str(e)+' No crowd votes or ranks substituted.','url':BASE+'/matches'})
        return
    for m in matches:
        exact=[c for c in candidates if orientation(m,c['teams'],c['start']) is not None]
        attempt={'provider':'HLTV','status':'unresolved','url':BASE+'/matches'}
        if len(exact)==1:
            url=exact[0]['url'];attempt['url']=url
            try:
                page,receipt=src.get('HLTV match '+m['id'],url,False)
                details=context(page,m)
                m['hltv_context']=details|{'source':url,'observed_at':receipt['observed_at']}
                attempt['reason']=details['limitation']
            except ValueError as e:
                attempt.update(status='error',reason=str(e))
        else:
            attempt['reason']='No unique exact team-pair and UTC-start match in the retrieved HLTV list; renamed teams are not inferred.'
            attempt['candidates']=[{'teams':c['teams'],'url':c['url']} for c in candidates if c['start']==m['start'] and set(map(norm,c['teams'])) & set(map(norm,m['teams']))]
        m['attempts'].append(attempt)
