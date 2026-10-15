"""Public rendered-source collection. Fail closed; never use Hotspawn vote shares.

Output updates only the deployment artifact, not main or another working branch.
"""
import asyncio,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
URL='https://play.hotspawn.com/cs2-pickems'
def stamp(): return datetime.now(timezone.utc).isoformat()

def lobby_cards(html):
    soup=BeautifulSoup(html,'html.parser'); found={}
    for a in soup.find_all('a',href=True):
        href=a['href']
        if 'hotspawn.com' not in href or not re.search(r'(?:-|information-)(\d{6,})(?:$|[?&])',href): continue
        id=re.search(r'(\d{6,})(?:$|[?&])',href).group(1)
        for parent in a.parents:
            text=parent.get_text('\n',strip=True)
            # A card, not the container for the entire page.
            if text.count('Who will win?')!=1: continue
            names=re.findall(r'([^\n]+)\n\d+%\s*picked',text)
            if len(names)!=2: continue
            before=text.split('Points available')[0].strip().splitlines()
            # Times displayed by lobby are not promoted to UTC without schema evidence.
            found[id]=dict(id=id,teams=names,tournament=before[-1] if before else '',source=urljoin(URL,href),lobby=URL,date=None,startUtc=None,observedAt=stamp(),odds=None,oddsAt=None,bookSource=None,reason='Independent two-sided match-winner odds not verified for this fixture.')
            break
    return list(found.values())

async def render(page,url):
    await page.goto(url,wait_until='domcontentloaded',timeout=60000)
    await page.wait_for_timeout(5000)
    for _ in range(12):
        previous=await page.locator('body').inner_text()
        await page.evaluate('window.scrollTo(0,document.body.scrollHeight)')
        await page.wait_for_timeout(1000)
        if await page.locator('body').inner_text()==previous: break
    text=await page.locator('body').inner_text()
    if re.search(r'Just a moment|Verify you are human|Access denied',text,re.I): raise RuntimeError('Access blocked; no anti-bot bypass attempted')
    return await page.content(),text

async def main():
    path=ROOT/'site/data/matches.json'; data=json.loads(path.read_text()); now=stamp(); checks=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch()
        page=await browser.new_page(timezone_id='UTC',locale='en-US')
        try:
            html,text=await render(page,URL)
            matches=lobby_cards(html)
            if not matches: raise RuntimeError('No complete fixture cards extracted; retaining last successful inventory')
            old={m['id']:m for m in data['matches']}
            for m in matches:
                previous=old.get(m['id'])
                if previous and previous['teams']==m['teams']:
                    for key in ('date','startUtc','odds','oddsAt','bookSource','reason'):
                        m[key]=previous.get(key)
            # Missing rows retained but explicitly not presented as current lobby fixtures.
            ids={m['id'] for m in matches}
            for m in data['matches']:
                if m['id'] not in ids:
                    m['inventoryNote']='Not seen in latest lobby extraction; may be locked, removed or missed. Historical inventory only.'
                    matches.append(m)
            data['matches']=matches; data['observedAt']=now
            data['coverage']=f'Partial / unverified completeness: {len(ids)} cards captured this run. Weekly/filter counts may include other populations. Historical missing rows retained and labeled.'
            data['collectionStatus']='Inventory refreshed; independent market refresh checked separately.'
            checks.append(dict(name='Hotspawn inventory',url=URL,status=f'{len(ids)} cards extracted; completeness unverified',at=now))
        except Exception as e:
            data['collectionStatus']='Inventory refresh failed; previous snapshot retained.'
            checks.append(dict(name='Hotspawn inventory',url=URL,status=str(e),at=now))
        # Check HLTV first for unresolved fixtures, then sportsbook sources. No invented Elo.
        for name,url in [('HLTV fallback research','https://www.hltv.org/matches'),('Thunderpick winner lines','https://thunderpick.io/esports/cs2-betting')]:
            try:
                html,text=await render(page,url)
                if name.startswith('Thunderpick'):
                    updated=refresh_book(data['matches'],html)
                    status=f'{updated} unambiguous same-date markets refreshed. Other fixtures remain unresolved or historical.'
                else: status='Page retrieved for fallback research; no calibrated historical model available. No inferred probabilities.'
                checks.append(dict(name=name,url=url,status=status,at=now))
            except Exception as e: checks.append(dict(name=name,url=url,status=str(e),at=now))
        await browser.close()
    data['lastAttemptAt']=now;data['sourceChecks']=checks
    path.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(checks,indent=2))


def refresh_book(matches,html):
    """Conservative text-card parser: same exact teams, event, explicit date and paired odds.
    Decimal display is converted to American for a single stored representation.
    No aliases or fuzzy team matching. Ambiguity never produces an update.
    """
    soup=BeautifulSoup(html,'html.parser'); updated=0
    event_tokens={'Thunderpick World Championship 2026':'thunderpick-world-championship-2026','Stake Pulse Beat III':'pulse-beat-iii','Elisa BreakOut Series #2':'elisa-breakout-series-2'}
    for m in matches:
        if not m.get('date') or m['tournament'] not in event_tokens: continue
        candidates={}
        for a in soup.find_all('a',href=True):
            href=urljoin('https://thunderpick.io',a['href'])
            if event_tokens[m['tournament']] not in href or '-vs-' not in href: continue
            for parent in a.parents:
                text=parent.get_text('\n',strip=True)
                # Stop once containing multiple fixtures or substantial page wrappers.
                if len(text)>1800: break
                lines=[x.strip() for x in text.splitlines() if x.strip()]
                if not all(team in lines for team in m['teams']): continue
                date=datetime.fromisoformat(m['date'])
                if not re.search(date.strftime('%b')+r'\s+'+str(date.day)+r'\b',text): continue
                pair=re.search(r'([+-]\d{3,4}|\d+\.\d{2})\s*vs\s*([+-]\d{3,4}|\d+\.\d{2})',text)
                if not pair: continue
                prices=[float(x) for x in pair.groups()]
                prices=[(x-1)*100 if 1<x<100 and x>=2 else -100/(x-1) if 1<x<2 else x for x in prices]
                if lines.index(m['teams'][0])>lines.index(m['teams'][1]): prices.reverse()
                candidates[href]=prices
                break
        if len(candidates)==1:
            m['bookSource'],m['odds']=next(iter(candidates.items()));m['oddsAt']=stamp();m['reason']=None;updated+=1
    return updated

if __name__=='__main__': asyncio.run(main())
