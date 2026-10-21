"""HLTV context for missing picks. Its crowd votes and ranks never become odds."""
import json
from pathlib import Path
import re
from urllib.parse import quote
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
SEARCH=BASE+'/search?query='
TEAM_PAGE_PROVIDER='HLTV team pages'


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
    # A bracket slot with TBA teams can never carry a fixture lineup, so the
    # clubs' own pages are read next (identity and roster context only).
    team_pages(matches,src)


def search_teams(html):
    """Exact HLTV team links from a public search response, keyed by URL.

    Only ``/team/<id>/<slug>`` anchors are kept. Nothing here decides whether a
    label is "close enough": the caller requires exactly one anchor whose label
    normalizes to the fixture label, and refuses otherwise.
    """
    soup=BeautifulSoup(html,'html.parser');found={}
    for anchor in soup.select('a[href^="/team/"]'):
        href=anchor.get('href') or ''
        if not re.fullmatch(r'/team/\d+/[^/?#]+',href):continue
        label=' '.join(anchor.get_text(' ',strip=True).split())
        if label:found.setdefault(BASE+href,label)
    return found


def team_profile(html,team):
    """Roster and world-ranking context from a club's own public HLTV page.

    The page is identified by its own heading, which must normalize to the
    fixture label; a search hit alone is never enough. The roster is the page's
    own FAQ answer ("The main lineup of X is A, B, C, D & E"), and the world
    rank is the link HLTV attaches to a pure ``#N`` label. When the page states
    no rank, that only counts as *unranked* if HLTV says so in words
    ("doesn't have a world rank"); anything else is returned as ``unknown`` and
    must not be presented as an absence.
    """
    soup=BeautifulSoup(html,'html.parser')
    heading=soup.select_one('.profile-team-name h1') or soup.select_one('h1')
    label=' '.join(heading.get_text(' ',strip=True).split()) if heading is not None else ''
    if not label or norm(label)!=norm(team):
        raise ValueError('HLTV team page heading %r is not an exact match for %r' % (label,team))
    text=' '.join(soup.get_text(' ',strip=True).split())
    # Inline links leave stray spaces around punctuation and the ampersand
    # ("Wign , K014NZ & yoyoS2 ."), so normalise those before matching.
    text=re.sub(r'\s*&\s*',' & ',text)
    text=re.sub(r'\s+([,.;:])',r'\1',text)
    lineup=[]
    hit=re.search(r'The main lineup of .{0,200}? is (.+?)(?:\.\s|\s+What\b|$)',text)
    if hit:
        lineup=[re.sub(r'\s+',' ',part).strip() for part in re.split(r'\s*(?:,|&|\band\b)\s*',hit.group(1)) if part.strip()]
    rank=None;rank_source=None
    for anchor in soup.select('a[href^="/ranking/teams/"]'):
        digits=re.fullmatch(r'#(\d+)',anchor.get_text(' ',strip=True).replace(' ',''))
        if digits and '/details/' in (anchor.get('href') or ''):
            rank=int(digits.group(1));rank_source=BASE+anchor['href'];break
    explicit_absence=bool(re.search(r"(?:doesn't|does not) have a world rank",text))
    roster_absent=bool(re.search(r'does not currently have a roster|has no active players in their lineup',text))
    vrs_rank=None;vrs_source=None
    for anchor in soup.select('a[href^="/valve-ranking/teams"]'):
        digits=re.fullmatch(r'#(\d+)',anchor.get_text(' ',strip=True).replace(' ',''))
        if digits:
            vrs_rank=int(digits.group(1));vrs_source=BASE+(anchor.get('href') or '');break
    return {'team':team,'label':label,'lineup':lineup,
        'world_rank':rank,'world_rank_status':'ranked' if rank else ('unranked' if explicit_absence else 'unknown'),
        'world_rank_source':rank_source,'roster_absent':roster_absent,
        'vrs_rank':vrs_rank,'vrs_source':vrs_source,
        'limitation':'Team-page roster and ranking are identity context only; no probability is derived from an HLTV rank.'}


def team_pages(matches,src):
    """Own-page identity for fixtures HLTV has not populated with team names.

    A bracket slot can exist on HLTV with TBA teams (fixture 1081597 on
    2026-10-22 was one), so the fixture page can never supply a lineup. The two
    clubs' own team pages still do, and the Valve model needs a current roster
    only to tell repeated Valve standings labels apart. This reads each label's
    search result, requires exactly one exact-label team page, then reads that
    page. Every failure is recorded and nothing is inferred from a near match.
    """
    for fixture in matches:
        if fixture.get('state')!='open' or fixture.get('probabilities') is not None or fixture.get('hltv_context'):
            continue
        rows,problem=[],None
        for team in fixture['teams']:
            try:
                listing,_=src.get('HLTV team search '+team,SEARCH+quote(team),False)
                candidates={url:label for url,label in search_teams(listing).items() if norm(label)==norm(team)}
                if len(candidates)!=1:
                    raise ValueError('%d HLTV team pages carry that exact label; a unique identity is required' % len(candidates))
                url,_=next(iter(candidates.items()))
                page,receipt=src.get('HLTV team page '+team,url,False)
                rows.append(team_profile(page,team)|{'url':url,'observed_at':receipt['observed_at']})
            except ValueError as e:
                problem='%s: %s' % (team,str(e));rows=[];break
        attempt={'provider':TEAM_PAGE_PROVIDER,'url':SEARCH+quote(fixture['teams'][0])}
        if problem or len(rows)!=2:
            attempt.update(status='unresolved',
                reason=(problem or 'both team pages were not read')+'. No roster or ranking is inferred from a name search alone.')
            fixture['attempts'].append(attempt);continue
        fixture['hltv_team_pages']={'observed_at':min(row['observed_at'] for row in rows),'teams':rows,
            'limitation':('HLTV has no fixture page carrying these two teams, so each label was resolved to exactly one '
                'HLTV team page by its own heading. The pages supply roster and ranking context only; they never supply a probability.')}
        attempt.update(status='resolved',
            reason='Both labels resolve to exactly one HLTV team page each; roster and world-ranking context recorded, no probability derived.')
        fixture['attempts'].append(attempt)
