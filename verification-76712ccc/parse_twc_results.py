"""Line-by-line verification of the TWC 2026 record from retained HLTV page captures.

Every value printed here is read out of a raw HLTV match page that this repository
already stores (research/harvest-76712ccc/hltv-<match id>.html, captured with its
SHA-256 in probe-report.json and raw-index.json). Nothing is typed in by hand: the
series score comes from the page's own team blocks and each map score comes from the
page's own map holders, so a change in the source changes this output.

Usage:
    python verification-76712ccc/parse_twc_results.py [--harvest research/harvest-76712ccc]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

# Match ids are discovered from the retained event pages, not hard-coded, so the
# list cannot drift from the captures.
TWC_LABELS = ('HLTV_TWC_results', 'HLTV_TWC_schedule')
ROOT = Path(__file__).resolve().parents[1]


def discover(harvest: Path):
    ids = {}
    for label in TWC_LABELS:
        for suffix in ('.html',):
            page = harvest / (label + suffix)
            if not page.exists():
                continue
            soup = BeautifulSoup(page.read_text(encoding='utf-8', errors='replace'), 'html.parser')
            for link in soup.select('a[href*="/matches/"]'):
                href = link.get('href') or ''
                if href.startswith('/matches/') and 'thunderpick' in href:
                    match_id = href.split('/matches/')[1].split('/')[0]
                    ids.setdefault(match_id, 'https://www.hltv.org' + href)
    return ids


def parse_match(path: Path):
    soup = BeautifulSoup(path.read_text(encoding='utf-8', errors='replace'), 'html.parser')
    series, seen = [], set()
    for block in soup.select('.team'):
        text = ' '.join(block.get_text(' ', strip=True).split())
        m = re.match(r'^(?P<name>.+?)\s+(?P<score>\d+)$', text)
        if not m or m.group('name').strip() in seen:
            continue
        seen.add(m.group('name').strip())
        series.append({'team': m.group('name').strip(), 'score': int(m.group('score'))})
        if len(series) == 2:
            break
    if len(series) != 2:
        series = []
    maps = []
    for holder in soup.select('.mapholder'):
        name_el = holder.select_one('.mapname')
        name = name_el.get_text(' ', strip=True) if name_el else None
        results = holder.select_one('.results')
        if results is None or 'played' not in (results.get('class') or []):
            continue
        cells = [' '.join(x.get_text(' ', strip=True).split()) for x in results.select(':scope > *')]
        left = right = None
        stats = None
        for cell in cells:
            m = re.match(r'^(?P<team>.+?)\s+(?P<score>\d+)$', cell)
            if not m:
                if cell.startswith('STATS'):
                    stats = cell.replace('STATS', '').strip(' ()')
                continue
            if left is None:
                left = {'team': m.group('team').strip(), 'score': int(m.group('score'))}
            elif right is None:
                right = {'team': m.group('team').strip(), 'score': int(m.group('score'))}
        maps.append({'map': name, 'left': left, 'right': right, 'half_scores': stats})
    date = None
    for el in soup.select('.date'):
        text = ' '.join(el.get_text(' ', strip=True).split())
        m = re.search(r'(\d{1,2})(?:st|nd|rd|th)? of (\w+ \d{4})', text)
        if m:
            date = '%s %s' % (m.group(1), m.group(2))
            break
    event = None
    for el in soup.select('.event a, .event'):
        text = ' '.join(el.get_text(' ', strip=True).split())
        if 'Thunderpick' in text:
            event = text
            break
    return {'date': date, 'event': event, 'series': series, 'maps': maps,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--harvest', default='research/harvest-76712ccc')
    parser.add_argument('--output', default='verification-76712ccc/TWC-RESULTS.json')
    parser.add_argument('--markdown', default='verification-76712ccc/TWC-RESULTS.md')
    args = parser.parse_args()

    harvest = Path(args.harvest)
    discovered = discover(harvest)
    results, missing = {}, []
    for match_id, url in sorted(discovered.items()):
        page = harvest / ('hltv-%s.html' % match_id)
        if not page.exists():
            missing.append({'match_id': match_id, 'url': url, 'reason': 'no retained capture'})
            continue
        parsed = parse_match(page)
        parsed['url'] = url
        parsed['match_id'] = match_id
        results[match_id] = parsed

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'results': results, 'missing_captures': missing},
                              indent=1, ensure_ascii=False, sort_keys=True) + '\n')

    lines = ['# Thunderpick World Championship 2026 — results read from retained HLTV captures', '',
             'Every row below is parsed out of a raw match page kept in `research/harvest-76712ccc/`;',
             'the page SHA-256 is recorded per match. A blank series score means the page was captured',
             'before the match was played.', '',
             '| Match | Date | Series | Maps (left–right) | HLTV capture SHA-256 | Source |',
             '| --- | --- | --- | --- | --- | --- |']
    for match_id, r in sorted(results.items()):
        series = ' vs '.join('%s %s' % (t['team'], t['score']) for t in r['series']) or 'not played at capture time'
        maps = '; '.join('%s %s %s–%s %s' % (m['map'], (m['left'] or {}).get('team', '?'),
                                             (m['left'] or {}).get('score', '?'),
                                             (m['right'] or {}).get('score', '?'),
                                             (m['right'] or {}).get('team', '?'))
                         for m in r['maps'] if m['left'] and m['right'])
        lines.append('| %s | %s | %s | %s | `%s` | [HLTV](%s) |' % (match_id, r['date'] or '—', series,
                                                                  maps or '—', r['sha256'][:16], r['url']))
    if missing:
        lines += ['', '## Captures not retained in this harvest', '']
        for item in missing:
            lines.append('- %s — %s (%s)' % (item['match_id'], item['url'], item['reason']))
    Path(args.markdown).write_text('\n'.join(lines) + '\n')
    print('parsed %d TWC match pages, %d without a capture -> %s' % (len(results), len(missing), out))


if __name__ == '__main__':
    main()
