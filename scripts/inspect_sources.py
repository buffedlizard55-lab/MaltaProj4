"""One-off read-only fallback research, not used by production refresh."""
import json
from pathlib import Path
import requests
from playwright.sync_api import sync_playwright

out=Path('research/probe');out.mkdir(parents=True,exist_ok=True)
urls={
 'hltv-pcific':'https://www.hltv.org/matches/2399463/pcific-vs-ryvex-cct-2026-europe-series-12-closed-qualifier',
 'hltv-banda':'https://www.hltv.org/matches/2399462/banda-chuya-vs-6666-cct-2026-europe-series-12-closed-qualifier',
 'hltv-wbt':'https://www.hltv.org/matches/2399420/wbt-vs-ence-elisa-breakout-series-2',
}
for name,url in urls.items():
 try:
  r=requests.get(url,timeout=30,headers={'User-Agent':'Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)'})
  (out/(name+'.txt')).write_text(r.text)
 except Exception as exc: print(name,str(exc))
with sync_playwright() as p:
 browser=p.chromium.launch()
 page=browser.new_page()
 receipts=[]
 def record(response):
  if 'thunderpick' not in response.url: return
  content_type=response.headers.get('content-type','')
  if 'json' not in content_type: return
  try:
   body=response.json()
   receipts.append({'url':response.url,'status':response.status,'data':body})
  except Exception: pass
 page.on('response',record)
 try:
  page.goto('https://thunderpick.io/esports/cs2-betting',wait_until='domcontentloaded',timeout=45000)
  page.wait_for_timeout(12000)
  (out/'thunderpick-rendered.txt').write_text(page.content())
  (out/'thunderpick-api.json').write_text(json.dumps(receipts,indent=2))
 except Exception as exc: print('browser',str(exc))
 browser.close()
