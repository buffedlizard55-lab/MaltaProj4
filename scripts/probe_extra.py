"""Read-only primary-source research; no cookies, logins or restriction bypass."""
import json
from datetime import datetime, timezone
from pathlib import Path
from scripts.refresh import Sources

sources = Sources(datetime.now(timezone.utc))
for name, url in [
    ('Stake CS2', 'https://stake.com/en/sports/esports/counter-strike'),
    ('BetBoom official identity', 'https://betboom.team/'),
    ('BetBoom official shop identity', 'https://shop.betboom.team/page/about-us'),
    ('Polymarket discovery documentation', 'https://docs.polymarket.com/market-data/discover-markets'),
]:
    try:
        sources.get(name, url, False)
    except ValueError:
        pass
Path('runtime').mkdir(exist_ok=True)
Path('runtime/research-receipts.json').write_text(json.dumps(sources.log, indent=2))
print(json.dumps(sources.log, indent=2))
