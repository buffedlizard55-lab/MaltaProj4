"""Smoke-check all navigation and mobile/desktop layouts against local static site."""
import asyncio,threading,http.server,functools
from pathlib import Path
from playwright.async_api import async_playwright
async def main():
    server=http.server.ThreadingHTTPServer(('127.0.0.1',8765),functools.partial(http.server.SimpleHTTPRequestHandler,directory='site'))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    async with async_playwright() as p:
        browser=await p.chromium.launch()
        for width in (375,768,1280):
            page=await browser.new_page(viewport={'width':width,'height':900})
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            for name in ('index','picks','unresolved','methodology','review'):
                await page.goto(f'http://127.0.0.1:8765/{name}.html')
                await page.wait_for_function("!document.querySelector('#status').textContent.includes('Loading')")
                assert not errors, errors
                assert await page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'),(width,name,'horizontal overflow')
                if name=='picks':
                    assert await page.locator('tbody tr').count()>0
                    await page.locator('#search').fill('ENCE')
                    assert await page.locator('tbody tr').count()>0
                if width==375:
                    Path('diagnostics').mkdir(exist_ok=True)
                    await page.screenshot(path=f'diagnostics/mobile-{name}.png',full_page=True)
            await page.close()
        await browser.close()
    server.shutdown()
asyncio.run(main())
