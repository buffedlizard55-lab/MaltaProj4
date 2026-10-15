"""Read-only primary-source research; no cookies, logins or restriction bypass."""
import json
from datetime import datetime, timezone
from pathlib import Path
from scripts.refresh import Sources
from bs4 import BeautifulSoup

excerpts = []

sources = Sources(datetime.now(timezone.utc))
for name, url in [
    ('Stake CS2', 'https://stake.com/en/sports/esports/counter-strike'),
    ('BetBoom official identity', 'https://betboom.team/'),
    ('BetBoom official shop identity', 'https://shop.betboom.team/page/about-us'),
    ('Polymarket discovery documentation', 'https://docs.polymarket.com/market-data/discover-markets'),
]:
    try:
        body, receipt = sources.get(name, url, False)
        soup = BeautifulSoup(body, 'html.parser')
        for el in soup(['script', 'style']):
            el.decompose()
        excerpts.append({'name': name, 'source': url, 'receipt': receipt,
                         'text': soup.get_text(' ', strip=True)[:80000]})
    except ValueError:
        pass
Path('runtime').mkdir(exist_ok=True)
Path('runtime/research-receipts.json').write_text(json.dumps(sources.log, indent=2))
print(json.dumps(sources.log, indent=2))

Path('runtime/research-excerpts.json').write_text(json.dumps(excerpts, indent=2))
