"""Fail the build on altered primary facts, unsupported prices or broken links."""
import argparse
import json
import math
import hashlib
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
from scripts.core import (
    normalize_fixtures, dt, iso, norm, orientation, fresh,
    polymarket_candidates, pinnacle_candidates, quote_polymarket, quote_pinnacle,
    GAMMA, PIN,
)


def reconstruct_quote(q, schema_version=1):
    """Rebuild a candidate from the ORIGINAL fields, never the derived labels.

    Legacy bootstrap evidence did not retain event/parent metadata. That is
    explicitly a historical format; v2 refreshes require those fields too.
    """
    raw = q['raw']
    if q['provider'] == 'Polymarket':
        assert str(raw['id']) == q['id'], 'Market ID differs from raw evidence'
        assert q['api_url'] == GAMMA + '/markets/' + q['id']
        assert iso(raw['updatedAt']) == iso(q['updated_at'])
        if schema_version >= 2:
            assert isinstance(q.get('event'), dict), 'Missing original exchange event'
        event = dict(q.get('event') or {'slug': urlsplit(q['url']).path.split('/')[-1]})
        if 'teams' in event:
            assert (event['teams'] or []) == q.get('team_metadata', [])
        else:
            event['teams'] = q.get('team_metadata', [])
        event['markets'] = [raw]
        candidates = polymarket_candidates([event], q['observed_at'])
    elif q['provider'] == 'Pinnacle':
        assert q['api_url'] == PIN + '/sports/12/markets/straight'
        match, line = dict(raw['matchup']), raw['line']
        assert str(match['id']) == q['id'] and match['id'] == line['matchupId']
        if schema_version >= 2:
            assert 'type' in match and 'parentId' in match, 'Missing original parent-match metadata'
        else:
            # v1 only retained a subset; its collector had checked this field.
            match.setdefault('type', 'matchup')
        candidates = pinnacle_candidates([match], [line], q['observed_at'])
        assert q.get('updated_at') is None, 'No bookmaker price-change time was supplied'
    else:
        raise AssertionError('Unknown probability provider')
    assert len(candidates) == 1, 'Raw evidence does not establish a whole-match CS2 candidate'
    candidate = candidates[0]
    assert candidate['teams'] == q['source_teams'], 'Raw outcome/participant names do not match identity'
    assert iso(candidate['start']) == iso(q['start']), 'Raw source start differs from identity'
    return candidate


def validate_data(data):
    now = dt(data['generated_at'])
    originals = {m['id']: m for m in normalize_fixtures(data['fixture_evidence'], {}, now)}
    assert len(originals) == len(data['matches']), 'Fixture completeness mismatch'
    seen, priced = set(), 0
    for m in data['matches']:
        assert m['id'] not in seen, 'Duplicate displayed ID'
        seen.add(m['id'])
        original = originals[m['id']]
        for field in ('teams', 'team_ids', 'competition', 'start', 'lock', 'tier', 'best_of', 'source_status'):
            assert m[field] == original[field], f"{m['id']} altered primary fact: {field}"
        source = urlsplit(m['source_url'])
        assert source.scheme == 'https' and source.netloc in ('play.hotspawn.com', 'www.hotspawn.com')
        if m['probabilities'] is None:
            assert m['pick'] is None and m['fair_odds'] is None, 'Unknowns must remain blank'
            continue
        priced += 1
        assert m['state'] == original['state'] == 'open' and len(m['evidence']) == 1
        assert not m.get('resolution_blocked'), 'Conflicting fixture membership cannot supply a pick'
        assert fresh(data['fixtures_observed_at'], now)
        q = m['evidence'][0]
        candidate = reconstruct_quote(q, data.get('schema_version', 1))
        teams = candidate['teams'][:]
        for i, aliases in enumerate(candidate.get('team_aliases', [])):
            targets = [t for t in m['teams'] if norm(t) in {norm(a) for a in aliases if a}]
            if len(targets) == 1:
                teams[i] = targets[0]
        order = orientation(m, teams, candidate['start'])
        assert order is not None, 'Unverified raw team/time identity'
        if m.get('best_of') is not None:
            assert candidate.get('best_of') is not None and str(candidate['best_of']) == str(m['best_of'])
        calculator = quote_polymarket if q['provider'] == 'Polymarket' else quote_pinnacle
        replay = calculator(candidate, order, now)  # status, age, spread, liquidity, cutoff, margin
        expected_method = 'exchange' if q['provider'] == 'Polymarket' else 'bookmaker_fallback'
        assert m['method'] == expected_method
        probabilities = replay['probabilities']
        assert all(math.isfinite(p) and 0 < p < 1 for p in probabilities)
        assert abs(sum(probabilities) - 1) < 1e-9
        assert len(m['probabilities']) == len(m['fair_odds']) == len(q['probabilities']) == 2
        for i, p in enumerate(probabilities):
            for value in (m['probabilities'][i], q['probabilities'][i]):
                assert math.isfinite(value) and abs(value - p) < 1e-9, 'Probability not reproducible'
            assert math.isfinite(m['fair_odds'][i]) and abs(m['fair_odds'][i] - 1 / p) < 1e-9
        for field in ('spread', 'liquidity', 'overround', 'decimal_odds'):
            if field in replay:
                assert q[field] == replay[field], 'Altered calculated quote field: ' + field
        pick = None if abs(probabilities[0] - probabilities[1]) < .0001 else m['teams'][0 if probabilities[0] > probabilities[1] else 1]
        assert m['pick'] == pick, 'Pick does not follow the verified probabilities'
    assert seen == set(originals)
    return {'rows_verified_against_primary_snapshot': len(seen),
            'probability_calculations_reproduced': priced}


def validate_site(directory):
    root = Path(directory).resolve()
    pages = {p: BeautifulSoup(p.read_text(), 'html.parser') for p in root.glob('*.html')}
    count = 0
    assert len(pages) >= 8, 'Missing required site pages'
    for path, soup in pages.items():
        assert soup.select_one('meta[name="viewport"]')
        assert len(soup.select('h1')) == 1
        assert soup.select_one('nav[aria-label="Main navigation"]')
        for row in soup.select('tr[data-match]'):
            assert any(urlsplit(a.get('href', '')).netloc in ('www.hotspawn.com', 'play.hotspawn.com')
                       for a in row.select('a')), 'Row lacks official source'
            if row.select_one('.prob-pair'):
                assert row.get('data-expires'), 'Recommendation has no complete expiry deadline'
        for a in soup.select('[href],script[src]'):
            url = a.get('href') or a.get('src')
            parsed = urlsplit(url)
            if parsed.scheme:
                assert parsed.scheme == 'https', 'Unexpected non-HTTPS external link'
                continue
            assert not parsed.netloc, 'Protocol-relative external link'
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            assert target.is_relative_to(root), f'Escaping link: {url}'
            assert target.exists(), f'Broken internal link from {path.name}: {url}'
            if parsed.fragment and target in pages:
                assert pages[target].find(id=unquote(parsed.fragment)), f'Broken anchor: {url}'
            count += 1
    manifest=json.loads((root/'build-info.json').read_text())
    for relative,digest in manifest['files'].items():
        target=(root/relative).resolve()
        assert target.is_relative_to(root) and target.is_file(), 'Invalid manifest path'
        assert hashlib.sha256(target.read_bytes()).hexdigest()==digest, 'Build manifest checksum mismatch: '+relative
    return {'pages': len(pages), 'internal_links_and_assets_checked': count, 'artifact_checksums_verified':len(manifest['files'])}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data/latest.json')
    parser.add_argument('--site', default='public')
    args = parser.parse_args()
    report = validate_data(json.loads(Path(args.data).read_text())) | validate_site(args.site)
    Path('runtime').mkdir(exist_ok=True)
    Path('runtime/validation.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
