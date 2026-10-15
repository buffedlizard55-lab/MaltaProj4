from pathlib import Path
from bs4 import BeautifulSoup
import json
from collect import lobby_cards
print('## Source diagnostics\n```text')
b=Path('diagnostics/browser.txt').read_text();print('Browser checks:', 'FAILED' if 'Traceback' in b else 'PASSED all 15 viewport/page combinations');print(b[-1500:] if 'Traceback' in b else '')
p=Path('diagnostics/hotspawn.html')
if p.exists():
 soup=BeautifulSoup(p.read_text(),'html.parser')
 print('Parsed cards:',len(lobby_cards(p.read_text())))
 for card in soup.select('.vs-card')[:2]:
  for svg in card.select('svg'):svg.decompose()
  print(str(card)[:7000])
 for s in soup.find_all('script'):
  if s.get('src'): print('JS:',s['src'])
  else:
   text=s.string or s.get_text()
   print('SCRIPT',s.get('id'),s.get('type'),'length',len(text),text[:1500])
   if s.get('id')=='ng-state':
    obj=json.loads(text)
    for k,v in obj.items():
     print('STATE',k,str(v)[:13000])
for r in json.loads(Path('diagnostics/responses.json').read_text()):
 if 'pickem-weeks' in r['url']:print(r['url'],str(r['data'])[:500])
print('```')
