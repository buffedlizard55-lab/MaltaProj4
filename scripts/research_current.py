"""One-off, read-only primary-source investigation for the integration handoff.

No accounts, proxy services or access-control workarounds. Normal scheduled
operation uses refresh.py, not this diagnostic. Large raw responses stay in the
seven-day Actions artifact; only compact receipts/excerpts enter Git.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup
from scripts.refresh import Sources
from scripts.core import polymarket_candidates, pinnacle_candidates

OUT = Path('research/current')
OUT.mkdir(parents=True, exist_ok=True)
snapshot = json.loads((OUT / 'refresh.json').read_text())
receipts = snapshot['source_checks']
excerpts = []


def archived(receipt):
    return json.loads((Path('runtime/sources') / (receipt['sha256'] + '.json')).read_text())


exchange = []
matchups, lines = None, None
for receipt in receipts:
    if receipt['status'] != 'ok':
        continue
    name = receipt['name']
    if name == 'Hotspawn CS2 fixtures':
        (OUT / 'fixture-source.json').write_text(json.dumps(archived(receipt), indent=2) + '\n')
    if name.startswith('Polymarket events page'):
        for candidate in polymarket_candidates(archived(receipt), receipt['observed_at']):
            exchange.append({k:v for k,v in candidate.items() if k != 'market'})
    if name == 'Pinnacle esports fixtures':
        matchups = archived(receipt)
    if name == 'Pinnacle esports moneylines':
        lines = archived(receipt)
(OUT / 'exchange-candidates.json').write_text(json.dumps(exchange, indent=2) + '\n')
if matchups is not None and lines is not None:
    (OUT / 'bookmaker-candidates.json').write_text(json.dumps(
        pinnacle_candidates(matchups, lines, snapshot['last_attempt_at']), indent=2) + '\n')

sources = Sources(datetime.now(timezone.utc))
for name, url in [
    ('General Hotspawn lobby', 'https://play.hotspawn.com/lobby'),
    ('Thunderpick official CS2 listing', 'https://thunderpick.io/esports/cs2-betting'),
    ('Rivalry official CS2 listing', 'https://www.rivalry.com/esports/counter-strike-betting'),
    ('Stake official CS2 listing', 'https://stake.com/en/sports/esports/counter-strike'),
    ('BetBoom official identity', 'https://betboom.team/'),
    ('WhiteBIT official team announcement', 'https://blog.whitebit.com/en/w-group-launches-whitebit-team/'),
    ('HLTV WBT team context', 'https://www.hltv.org/team/13683/wbt'),
    ('Polymarket discovery documentation', 'https://docs.polymarket.com/market-data/discover-markets'),
]:
    try:
        body, receipt = sources.get(name, url, False)
        soup = BeautifulSoup(body, 'html.parser')
        scripts = [s.get('src') for s in soup.select('script[src]')]
        structured = [s.get_text() for s in soup.select('script[type="application/ld+json"]')]
        for el in soup(['script', 'style']):
            el.decompose()
        excerpts.append({'name': name, 'url': url, 'receipt': receipt,
                         'text': soup.get_text(' ', strip=True)[:60000],
                         'public_script_urls': scripts, 'json_ld': structured})
    except ValueError:
        pass
(OUT / 'receipts.json').write_text(json.dumps(sources.log, indent=2) + '\n')
(OUT / 'excerpts.json').write_text(json.dumps(excerpts, indent=2) + '\n')
print(json.dumps(sources.log, indent=2))
