"""Fail the build on unsafe calculations, missing row provenance or broken internal links."""
import json
import math
from pathlib import Path
from urllib.parse import unquote, urlparse
from bs4 import BeautifulSoup
from collect import DATA, ROOT, pair_normalize, rating_probability


def validate():
    d = json.loads((DATA / 'snapshot.json').read_text())
    raw = json.loads((DATA / 'evidence/fixtures.json').read_text())['fixtures']
    inputs = {str(r['id']): r for r in raw}
    ids = [r['id'] for r in d['matches']]
    assert len(ids) == len(set(ids)), 'Duplicate IDs'
    assert set(ids) == set(inputs), 'Incomplete row inventory'
    assert len(ids) == d['coverage']['collected']
    if d['coverage']['status'] == 'count-matched':
        assert len(ids) == d['coverage']['advertised']
    for r in d['matches']:
        f = inputs[r['id']]
        assert r['teams'] == [f['participants0_name'], f['participants1_name']]
        assert r['tournament'] == f['competition_name']
        assert urlparse(r['fixture_source']).hostname in ('www.hotspawn.com', 'play.hotspawn.com')
        assert r['fixture_verified_at']
        if r['probabilities'] is None:
            assert r['pick'] is None
        else:
            assert r['state'] == 'priced'
            p = r['probabilities']
            assert all(math.isfinite(v) and 0 < v < 1 for v in p)
            assert abs(sum(p) - 1) < 1e-6
            assert r['pick'] == (r['teams'][p.index(max(p))] if p[0] != p[1] else None)
            e = r['evidence'][0]
            if r['method'] == 'market':
                assert p == pair_normalize(e['prices'])
                assert urlparse(e['url']).hostname == 'polymarket.com'
            elif r['method'] == 'model':
                assert p == rating_probability([v['points'] for v in e['ratings']])
                assert urlparse(e['url']).hostname == 'github.com'
                assert 'ValveSoftware/counter-strike_regional_standings/' in e['url']
            else:
                raise AssertionError('Unsupported probability method')
        assert 'picked_percent' not in json.dumps(r), 'Community votes leaked into inference'
    pages = list((ROOT / 'docs').glob('*.html'))
    parsed = {p: BeautifulSoup(p.read_text(), 'html.parser') for p in pages}
    for p, soup in parsed.items():
        assert soup.select_one('h1') and soup.select_one('main')
        page_ids = [el['id'] for el in soup.select('[id]')]
        assert len(page_ids) == len(set(page_ids)), f'Duplicate HTML IDs: {p}'
        for tag in soup.select('[href], [src]'):
            ref = tag.get('href') or tag.get('src')
            u = urlparse(ref)
            if u.scheme or u.netloc:
                assert u.scheme == 'https', f'Unsafe URL {ref}'
                continue
            path = (p.parent / unquote(u.path)).resolve() if u.path else p
            assert path.is_file(), f'Broken local link {p.name}: {ref}'
            if u.fragment and path.suffix == '.html':
                assert parsed[path].find(id=u.fragment), f'Broken anchor {ref}'
    print(f'Validated every one of {len(ids)} rows, calculations, source hosts, and all internal links in {len(pages)} pages.')


if __name__ == '__main__':
    validate()
