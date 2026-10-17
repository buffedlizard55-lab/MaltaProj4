"""Reproducible final-day source collection; no guessed teams, results or prices."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup
from scripts.refresh import Sources

OUT = Path('research/session-cc88483d/tournament')
RESULTS = 'https://www.hltv.org/results?event=8932'
SCHEDULE = 'https://www.hltv.org/events/8932/matches'

def capture():
    OUT.mkdir(parents=True, exist_ok=True)
    src = Sources(datetime.now(timezone.utc))
    manifest = []
    queue = [('results', RESULTS), ('schedule', SCHEDULE),
             ('aurora-roster', 'https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan'),
             ('hotspawn-rules', 'https://play.hotspawn.com/how-it-works')]
    seen = set()
    for name, url in queue:
        if url in seen:
            continue
        seen.add(url)
        try:
            html, receipt = src.get(name, url, False)
            (OUT / (name + '.html')).write_text(html)
            soup = BeautifulSoup(html, 'html.parser')
            (OUT / (name + '.txt')).write_text(soup.get_text(' ', strip=True))
            manifest.append({'name': name, 'url': url, 'receipt': receipt})
            if name in ('results', 'schedule'):
                for a in soup.select('a[href^="/matches/"]'):
                    href = a.get('href', '')
                    if 'thunderpick-world-championship-2026' in href:
                        ident = href.split('/')[2]
                        queue.append(('match-' + ident, 'https://www.hltv.org' + href))
        except Exception as exc:
            manifest.append({'name': name, 'url': url, 'error': str(exc)})
    (OUT / 'manifest.json').write_text(json.dumps({'pages': manifest, 'source_log': src.log}, indent=2) + '\n')

def targeted():
    out = Path('research/session-cc88483d/targeted')
    out.mkdir(parents=True, exist_ok=True)
    src = Sources(datetime.now(timezone.utc))
    for name, url in [
        ('hacha-event', 'https://gamma-api.polymarket.com/events?slug=cs2-hachae-ln-2026-10-17'),
        ('hacha-market', 'https://gamma-api.polymarket.com/markets/5796276'),
        ('furia-betboom', 'https://gamma-api.polymarket.com/events?slug=cs2-furia-bb3-2026-10-18'),
        ('aurora-falcons', 'https://gamma-api.polymarket.com/events?slug=cs2-aur1-fal2-2026-10-18'),
    ]:
        try:
            data, receipt = src.get(name, url)
            (out / (name + '.json')).write_text(json.dumps({'data': data, 'receipt': receipt}, indent=2) + '\n')
        except Exception as exc:
            (out / (name + '.json')).write_text(json.dumps({'error': str(exc)}, indent=2) + '\n')
    (out / 'source-log.json').write_text(json.dumps(src.log, indent=2) + '\n')

if __name__ == '__main__':
    if sys.argv[1:] == ['capture']:
        capture()
    elif sys.argv[1:] == ['targeted']:
        targeted()
    else:
        raise SystemExit('Usage: python -m scripts.day5_cc88483d capture|targeted')
