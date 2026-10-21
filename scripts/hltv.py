"""HLTV context for missing picks. Its crowd votes and ranks never become odds."""
import re
from bs4 import BeautifulSoup
from scripts.core import dt,iso,orientation,norm

BASE='https://www.hltv.org'
# HLTV's /matches page shows one local day and a limited window, so an open
# fixture that starts on a later day can be missing from it even though HLTV
# publishes it on its own dated view. Measured, not assumed: on the
# 2026-10-21T20:10:54Z refresh (research/harvest-bf09aa40/snapshot.json) fixture
# 1081597 (benched gods vs TitanFlow, CCT Europe 2026 Challengers #8, start
# 2026-10-22T11:00:00Z) had no candidate in the front list, so it collected no
# HLTV identity, no ranks and no lineups, and the run ended with *no pick at
# all* for that match. HLTV serves the same fixtures per day at
# /matches?selectedDate=YYYY-MM-DD, so those pages are read for exactly the
# unmatched fixtures' UTC dates. Nothing is relaxed: the exact opponent pair and
# the exact UTC start are still required, and a dated page that is refused or
# empty is recorded as a source state, never inferred around.
DATE_PAGE_LIMIT=4


def date_views(matches,candidates):
    """UTC dates of the fixtures the front HLTV list did not contain."""
    days=[]
    for m in matches:
        if any(orientation(m,c['teams'],c['start']) is not None for c in candidates):
            continue
        try:
            day=dt(m['start']).date().isoformat()
        except (TypeError,ValueError,OSError,OverflowError):
            continue
        if day not in days:
            days.append(day)
    return sorted(days)


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
    # Second read: HLTV's own dated views, for the fixtures the front list did
    # not contain. Bounded, logged, and never a substitute for exact identity.
    dated=[]
    missing=[m for m in matches if all(orientation(m,c['teams'],c['start']) is None for c in candidates)]
    if missing:
        seen={c['url'] for c in candidates}
        for day in date_views(missing,candidates)[:DATE_PAGE_LIMIT]:
            url=BASE+'/matches?selectedDate='+day
            try:
                page,_=src.get('HLTV matches '+day,url,False)
                extra=discover(page)
            except ValueError as e:
                dated.append({'url':url,'status':'error','error':str(e)[:200]})
                continue
            added=0
            for c in extra:
                if c['url'] not in seen:
                    seen.add(c['url']);candidates.append(c);added+=1
            dated.append({'url':url,'status':'ok','fixtures_listed':len(extra),'new_candidates':added})
    for m in matches:
        exact=[c for c in candidates if orientation(m,c['teams'],c['start']) is not None]
        attempt={'provider':'HLTV','status':'unresolved','url':BASE+'/matches'}
        if dated:
            attempt['date_views']=dated
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
            if dated:
                attempt['reason']+=' Dated HLTV views also read: '+', '.join(d['url'] for d in dated)+'.'
            attempt['candidates']=[{'teams':c['teams'],'url':c['url']} for c in candidates if c['start']==m['start'] and set(map(norm,c['teams'])) & set(map(norm,m['teams']))]
            # Diagnostic for the one case that matters: the same opponent pair
            # listed by HLTV at a *different* UTC start. Recorded, never used -
            # an assumed start correction is exactly what this project refuses.
            near=[{'teams':c['teams'],'start':c['start'],'url':c['url']} for c in candidates
                  if set(map(norm,c['teams']))==set(map(norm,m['teams']))]
            if near:
                attempt['same_pair_other_start']=near[:6]
        m['attempts'].append(attempt)
