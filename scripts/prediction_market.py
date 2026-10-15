"""Official Gamma market discovery, fail-closed on identity/date/market type.
Only an exact two-team Match Winner market is accepted. Never map/handicap.
"""
import json,re,urllib.request
from datetime import datetime

def slug(team): return re.sub(r'[^a-z0-9]+','-',team.casefold()).strip('-')
def accept(event,fixture):
    if event.get('closed') or not event.get('active'):return None
    markets=[]
    for market in event.get('markets',[]):
        if market.get('groupItemTitle')!='Match Winner' or market.get('closed') or not market.get('acceptingOrders'):continue
        try:
            names=json.loads(market['outcomes']); prices=[float(x) for x in json.loads(market['outcomePrices'])]
            if len(names)!=2 or len(prices)!=2 or any(not 0<x<1 for x in prices):continue
            if {x.casefold() for x in names}!={x.casefold() for x in fixture['teams']}:continue
            start=datetime.fromisoformat(market['gameStartTime'].replace(' ','T'))
            if start.date().isoformat()!=fixture['date']:continue
            # Explicit competition included in the official title; no fuzzy event joins.
            if fixture['tournament'].casefold() not in event.get('title','').casefold():continue
            ordered=[prices[[x.casefold() for x in names].index(t.casefold())] for t in fixture['teams']]
            total=sum(ordered);p=[x/total for x in ordered]
            odds=[-100*x/(1-x) if x>=.5 else 100*(1-x)/x for x in p]
            markets.append(dict(odds=odds,bookSource='https://polymarket.com/event/'+event['slug'],sourceType='prediction market',rawPrices=ordered,startUtc=start.isoformat(),marketUpdatedAt=market.get('updatedAt')))
        except (KeyError,ValueError,TypeError,ZeroDivisionError):continue
    return markets[0] if len(markets)==1 else None

def fetch_market(fixture):
    if not fixture.get('date'):return None
    a,b=map(slug,fixture['teams'])
    for x,y in [(a,b),(b,a)]:
        url=f'https://gamma-api.polymarket.com/events?slug=cs2-{x}-{y}-{fixture["date"]}'
        req=urllib.request.Request(url,headers={'User-Agent':'CS2PickDesk/1.0 (public market research)'})
        with urllib.request.urlopen(req,timeout=20) as response:events=json.load(response)
        accepted=[r for event in events if (r:=accept(event,fixture))]
        if len(accepted)==1:return accepted[0]
    return None
