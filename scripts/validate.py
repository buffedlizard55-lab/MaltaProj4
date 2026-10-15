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
            assert m['fair_odds'] is None, 'Unknowns must remain blank'
            if m['method'] == 'research_rank':
                # Full-coverage tier: a labelled research pick with no numbers.
                # It must be reproducible from the stored HLTV context alone.
                assert m['pick'] in m['teams'], 'Research pick is not one of the two teams'
                context = m.get('hltv_context') or {}
                ranks = {r.get('team'): r.get('hltv_rank') for r in context.get('ranks', []) if isinstance(r, dict)}
                known = [(t, next((v for n, v in ranks.items() if n and norm(n) == norm(t)), None)) for t in m['teams']]
                assert all(isinstance(v, int) and v > 0 for _, v in known), 'Research pick without both verified ranks'
                assert len({v for _, v in known}) == 2, 'Research pick on an equal ranking is not directional'
                assert m['pick'] == min(known, key=lambda item: item[1])[0], 'Research pick does not follow the verified ranking order'
                assert context.get('source', '').startswith('https://www.hltv.org/'), 'Research pick lacks its HLTV source'
                assert 'not a market probability' in (m.get('reason') or ''), 'Research pick must be labelled as non-market'
                assert not m['evidence'], 'Research pick must not carry a price quote'
                continue
            assert m['pick'] is None, 'Unknowns must remain blank'
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
        expected_method = 'exchange' if q['provider'] == 'Polymarket' else 'bookmaker_fallback'
        if q['provider'] == 'Polymarket' and q.get('tier') == 'wide_exchange':
            # Low-confidence tier: it may only be used where the strict gate fails,
            # and the published spread must be the real one.
            assert m['method'] == 'exchange_wide'
            try:
                quote_polymarket(candidate, order, now)
                raise AssertionError('Wide tier published although the strict gate passes')
            except ValueError:
                pass
            replay = quote_polymarket(candidate, order, now, allow_wide=True)
            assert replay['tier'] == 'wide_exchange' and m['evidence'][0].get('tier') == 'wide_exchange'
            assert 'Low confidence' in (m['evidence'][0].get('warning') or '')
            assert 'Low confidence' in ' '.join(m['flags'])
            assert m['evidence'][0].get('strict_rejection'), 'Wide tier must record the strict rejection'
        else:
            replay = calculator(candidate, order, now)  # status, age, spread, liquidity, cutoff, margin
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
    manifest=json.loads((root/'build-info.json').read_text())
    pages = {root/name: BeautifulSoup((root/name).read_text(), 'html.parser') for name in manifest['files'] if name.endswith('.html')}
    published = json.loads((root / 'data/latest.json').read_text())
    validate_data(published)
    lookup = {m['id']: m for m in published['matches']}
    count = 0
    displayed_rows = 0
    assert len(pages) >= 8, 'Missing required site pages'
    for path, soup in pages.items():
        rows = soup.select('tr[data-match]')
        ids = [row['data-match'] for row in rows]
        assert len(ids) == len(set(ids)), 'Duplicate rendered match: ' + str(path)
        if path.name == 'matches.html':
            assert set(ids) == set(lookup), 'All matches must contain the full retained inventory'
        for row in rows:
            m = lookup[row['data-match']]
            expected_teams = ' '.join(t for t in (m['teams'][0], 'vs', m['teams'][1]) if t)
            assert ' '.join(row.select_one('.teams').get_text(' ', strip=True).split()) == ' '.join(expected_teams.split())
            sources = {a.get('href') for a in row.select('.source-links a')}
            assert m['source_url'] in sources and 'evidence.html#match-' + m['id'] in sources
            pair = row.select('.prob-pair span')
            if m['probabilities'] is None:
                assert not pair, 'Unsupported rendered probability'
                rendered = row.select_one('.pick-cell .pick')
                if m['method'] == 'research_rank':
                    assert rendered is not None and rendered.get_text() == m['pick'], 'Rendered research pick differs'
                    assert row.select_one('.pick-cell .research-only'), 'Research pick must be labelled as non-market'
                else:
                    assert rendered is None, 'Unsupported rendered recommendation'
            else:
                assert [label.get_text() for label in row.select('.prob-team-labels span')] == m['teams']
                assert len(pair) == 2
                for label, probability in zip(pair, m['probabilities']):
                    assert abs(float(label.get_text().rstrip('%')) / 100 - probability) <= .00051, 'Rendered probability differs from verified data'
                pick = row.select_one('.pick-cell .pick')
                assert (pick.get_text() if pick else None) == m['pick'], 'Wrong displayed pick'
            displayed_rows += 1
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
    import csv
    with (root / 'data/matches.csv').open() as f:
        exported = list(csv.DictReader(f))
    assert len(exported) == len(lookup) and {row['hotspawn_id'] for row in exported} == set(lookup), 'CSV inventory differs'
    for row in exported:
        m = lookup[row['hotspawn_id']]
        q = m['evidence'][0] if m['evidence'] else {}
        assert row['expires_utc'] == (m.get('expires_at') or ''), 'CSV expiry differs from verified data'
        assert row['quote_observed_utc'] == (q.get('observed_at') or '')
        assert row['quote_updated_utc'] == (q.get('updated_at') or '')
        assert row['snapshot_generated_utc'] == published['generated_at']
        assert row['snapshot_fixture_observed_utc'] == published['fixtures_observed_at']
        assert row['build_utc'] == published['built_at']
        assert [row['team_1'], row['team_2']] == [t or '' for t in m['teams']]
        assert row['source'] == m['source_url'] and row['price_source'] == (q.get('api_url') or '')
        assert row['pick'] == (m['pick'] or '')
        if m['probabilities'] is None:
            assert not row['p_team_1'] and not row['p_team_2'] and not row['fair_decimal_1'] and not row['fair_decimal_2']
        else:
            for field, value in zip(('p_team_1', 'p_team_2', 'fair_decimal_1', 'fair_decimal_2'), m['probabilities'] + m['fair_odds']):
                assert math.isclose(float(row[field]), value, rel_tol=1e-10, abs_tol=1e-10), 'CSV calculation differs'
    manifest=json.loads((root/'build-info.json').read_text())
    for relative,digest in manifest['files'].items():
        target=(root/relative).resolve()
        assert target.is_relative_to(root) and target.is_file(), 'Invalid manifest path'
        assert hashlib.sha256(target.read_bytes()).hexdigest()==digest, 'Build manifest checksum mismatch: '+relative
    return {'pages': len(pages), 'internal_links_and_assets_checked': count,
            'artifact_checksums_verified': len(manifest['files']),
            'displayed_match_rows_verified': displayed_rows}


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
