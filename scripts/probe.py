import asyncio,json,pathlib
from playwright.async_api import async_playwright
async def main():
    out=pathlib.Path('diagnostics');out.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser=await p.chromium.launch()
        page=await browser.new_page(timezone_id='UTC')
        responses=[]
        async def response(r):
            if 'json' in r.headers.get('content-type',''):
                try: responses.append({'url':r.url,'data':await r.json()})
                except Exception: pass
        page.on('response',response)
        for name,url in [('hotspawn','https://play.hotspawn.com/cs2-pickems'),('thunderpick','https://thunderpick.io/esports/cs2-betting'),('hltv','https://www.hltv.org/matches')]:
            try:
                await page.goto(url,wait_until='domcontentloaded',timeout=60000)
                await page.wait_for_timeout(15000)
                (out/f'{name}.html').write_text(await page.content())
                (out/f'{name}.txt').write_text(await page.locator('body').inner_text())
            except Exception as e: print(name,str(e))
        (out/'responses.json').write_text(json.dumps(responses))
        await browser.close()
asyncio.run(main())
