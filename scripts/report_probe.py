from pathlib import Path
from bs4 import BeautifulSoup
import json
from collect import lobby_cards
print('## Source diagnostics\n```text')
b=Path('diagnostics/browser.txt').read_text();print('Browser checks:', 'FAILED' if 'Traceback' in b else 'PASSED all 15 viewport/page combinations');print(b[-1500:] if 'Traceback' in b else '')
data=json.loads(Path('site/data/matches.json').read_text())
print('Inventory records:',len(data['matches']))
print('Upcoming records:',sum(not m.get('historical') for m in data['matches']))
print('Priced:',sum(bool(m.get('odds')) for m in data['matches']))
print(json.dumps(data['sourceChecks'],indent=2))
print('```')
