from pathlib import Path
from bs4 import BeautifulSoup
import json
print('## Source diagnostics\n```text')
print(Path('diagnostics/browser.txt').read_text()[-6000:])
for name in ('hotspawn','thunderpick','hltv'):
 p=Path(f'diagnostics/{name}.html')
 if not p.exists(): continue
 soup=BeautifulSoup(p.read_text(),'html.parser')
 print('\nSOURCE',name,'TITLE',soup.title)
 print(soup.get_text('\n',strip=True)[:2500])
 if name=='hotspawn':
  a=next((a for a in soup.find_all('a',href=True) if '1080280' in a['href']),None)
  if a:
   for parent in list(a.parents)[:5]: print(str(parent)[:6500])
 print('JSON response URLs:')
for r in json.loads(Path('diagnostics/responses.json').read_text()):
 print(r['url'][:300], str(r['data'])[:300])
print('```')
