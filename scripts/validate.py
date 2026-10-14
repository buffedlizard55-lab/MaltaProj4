"""Audit every row back to primary-source fields and check every internal link."""
import argparse
import json
import math
from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup
from scripts.core import (normalize_fixtures,dt,iso,norm,orientation,devig,american,
    quote_polymarket,quote_pinnacle,fresh)


def validate_data(data):
    raw=data['fixture_evidence'];now=dt(data['generated_at'])
    originals={m['id']:m for m in normalize_fixtures(raw,{},now)}
    assert len(originals)==len(data['matches']), 'Fixture completeness mismatch'
    seen=set();priced=0
    for m in data['matches']:
        assert m['id'] not in seen, 'Duplicate displayed ID';seen.add(m['id'])
        original=originals[m['id']]
        for field in ('teams','team_ids','competition','start','lock','tier','best_of','source_status'):
            assert m[field]==original[field], f"{m['id']} altered primary fact: {field}"
        assert m['source_url'].startswith(('https://play.hotspawn.com/','https://www.hotspawn.com/'))
        if m['probabilities'] is None:
            assert m['pick'] is None and m['fair_odds'] is None, 'Unknowns must remain blank'
            continue
        priced+=1
        assert m['state']=='open' and len(m['evidence'])==1
        assert fresh(data['fixtures_observed_at'],now)
        q=m['evidence'][0]
        assert q['api_url'].startswith(('https://gamma-api.polymarket.com/','https://guest.api.arcadia.pinnacle.com/'))
        assert fresh(q['observed_at'],now)
        teams=q['source_teams'][:]
        for i,t in enumerate(teams):
            aliases=[a.get('abbreviation') for a in q.get('team_metadata',[]) if a.get('name')==t]
            targets=[n for n in m['teams'] if norm(n) in {norm(a) for a in aliases if a}]
            if len(targets)==1: teams[i]=targets[0]
        order=orientation(m,teams,q['start']);assert order is not None,'Unverified team/time identity'
        if q['provider']=='Polymarket':
            r=q['raw'];prices=json.loads(r['outcomePrices']) if isinstance(r['outcomePrices'],str) else r['outcomePrices']
            p=[float(prices[i])/sum(map(float,prices)) for i in order]
            assert r['sportsMarketType']=='moneyline' and r['active'] and not r['closed'] and r['acceptingOrders']
            assert fresh(r['updatedAt'],now)
        elif q['provider']=='Pinnacle':
            line=q['raw']['line'];match=q['raw']['matchup'];assert line['period']==0 and line['type']=='moneyline' and line['status']=='open'
            assert match['status']=='pending' and not match['isLive'] and match['id']==line['matchupId']
            assert match['league']['name'].startswith('CS2 - ')
            v={a['designation']:a['price'] for a in line['prices']}
            calculated,_=devig([american(v['home']),american(v['away'])]);p=[calculated[i] for i in order]
        else: raise AssertionError('Unknown probability provider')
        assert all(math.isfinite(x) and 0<x<1 for x in p) and abs(sum(p)-1)<1e-9
        for i in range(2):
            assert abs(m['probabilities'][i]-p[i])<1e-9, 'Probability not reproducible'
            assert abs(m['fair_odds'][i]-1/p[i])<1e-9, 'Fair odds not reproducible'
        assert m['pick']==(None if abs(p[0]-p[1])<.0001 else m['teams'][0 if p[0]>p[1] else 1])
    assert seen==set(originals)
    return {'rows_verified_against_primary_snapshot':len(seen),'probability_calculations_reproduced':priced}


def validate_site(directory):
    root=Path(directory).resolve();pages={p:BeautifulSoup(p.read_text(),'html.parser') for p in root.glob('*.html')}
    count=0
    for path,soup in pages.items():
        assert soup.select_one('meta[name="viewport"]')
        assert len(soup.select('h1'))==1
        assert soup.select_one('nav[aria-label="Main navigation"]')
        for row in soup.select('tr[data-match]'):
            assert any(a.get('href','').startswith(('https://www.hotspawn.com/','https://play.hotspawn.com/')) for a in row.select('a')), 'Row lacks official source'
        for a in soup.select('[href],script[src]'):
            url=a.get('href') or a.get('src');parsed=urlsplit(url)
            if parsed.scheme:
                assert parsed.scheme=='https','Unexpected non-HTTPS external link';continue
            target=(path.parent/unquote(parsed.path)).resolve() if parsed.path else path
            assert target.is_relative_to(root),f'Escaping link: {url}'
            assert target.exists(),f'Broken internal link from {path.name}: {url}'
            if parsed.fragment and target in pages:
                assert pages[target].find(id=unquote(parsed.fragment)),f'Broken anchor: {url}'
            count+=1
    return {'pages':len(pages),'internal_links_and_assets_checked':count}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/latest.json');p.add_argument('--site',default='public');a=p.parse_args()
    report=validate_data(json.loads(Path(a.data).read_text()))|validate_site(a.site)
    Path('runtime').mkdir(exist_ok=True);Path('runtime/validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
