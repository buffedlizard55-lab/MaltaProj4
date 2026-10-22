"""Fail the build on altered primary facts, unsupported prices or broken links."""
import argparse
import json
import math
import hashlib
import re
from pathlib import Path
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup
from scripts import hltv, vrs
from scripts.core import (
    IDENTITIES, normalize_fixtures, dt, iso, norm, plain_name, orientation, fresh,
    polymarket_candidates, pinnacle_candidates, quote_polymarket, quote_pinnacle,
    quote_book, book_candidate, calculator_for, pick_deadline,
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
        # Researched two-way book listing (scripts.core.book_candidate): the
        # full receipt is the raw evidence and the calculator replays it.
        assert q.get('updated_at') is None, 'No bookmaker price-change time was supplied'
        assert str(raw.get('id')) == q['id'], 'Book listing id differs from raw evidence'
        assert q['api_url'] == (raw.get('api_url') or raw.get('url')), 'Book listing URL differs from raw evidence'
        candidates = [book_candidate(raw)]
    assert len(candidates) == 1, 'Raw evidence does not establish a whole-match CS2 candidate'
    candidate = candidates[0]
    assert candidate['teams'] == q['source_teams'], 'Raw outcome/participant names do not match identity'
    assert iso(candidate['start']) == iso(q['start']), 'Raw source start differs from identity'
    return candidate



def lineup_source_ok(m, team, lineup):
    """Whether a stored lineup is reproducible from an HLTV page on the same row.

    The HLTV fixture page is the usual source. When HLTV publishes only a TBA
    bracket slot (no team names), the roster comes from that club's own HLTV
    team page and the row must carry its URL. Rows with neither source cannot
    be re-checked offline, so they are left to the other identity assertions
    (``label_count``) rather than being silently treated as sourced.
    """
    want = sorted(plain_name(x) for x in (lineup or []))
    if not want:
        return False
    for item in (m.get('hltv_context') or {}).get('lineups') or []:
        if plain_name(item.get('team') or '') == plain_name(team):
            if sorted(plain_name(x) for x in item.get('players') or []) == want:
                return True
    # A retained lineup receipt (data/lineup-receipts.json) is another HLTV
    # source: it must name this fixture, its exact teams and a match-page URL.
    for receipt in hltv.lineup_receipts():
        if str(receipt.get('fixture_id') or '') != str(m.get('id') or ''):
            continue
        if receipt.get('teams') != list(m.get('teams') or []):
            continue
        for item in receipt.get('lineups') or []:
            if plain_name(item.get('team') or '') != plain_name(team):
                continue
            if not str(item.get('source') or '').startswith('https://www.hltv.org/matches/'):
                continue
            if sorted(plain_name(x) for x in item.get('players') or []) == want:
                return True
    for item in (m.get('hltv_team_pages') or {}).get('teams') or []:
        if plain_name(item.get('team') or '') != plain_name(team):
            continue
        if not str(item.get('url') or '').startswith('https://www.hltv.org/team/'):
            continue
        if sorted(plain_name(x) for x in (item.get('lineup') or item.get('players') or [])) == want:
            return True
    return False


def validate_model_row(m, q, now):
    """Originated VRS line: inputs, formula, calibration, identity and pick."""
    assert q['provider'] == 'Valve VRS model', 'Model row with a non-model quote'
    for url in (q['url'], q['formula_source'], q['calibration_source'], *q['details_urls']):
        parts = urlsplit(url)
        assert parts.scheme == 'https' and parts.netloc == 'github.com' and parts.path.startswith('/' + vrs.OWNER_REPO + '/'), 'Model input is not the official Valve repository'
    assert urlsplit(q['api_url']).netloc in ('raw.githubusercontent.com', 'github.com') and vrs.OWNER_REPO in q['api_url']
    assert q['fixture_teams'] == m['teams'], 'Model quote orientation differs from the fixture'
    for team, label in zip(m['teams'], q['vrs_teams']):
        assert norm(team) == norm(label), 'VRS label does not map to the fixture team (exact or verified alias)'
    for team, check, count in zip(m['teams'], q['roster_checks'], q['label_counts']):
        if check['overlap'] is None:
            assert count == 1, 'Duplicated VRS label used without a roster check'
        else:
            assert check['overlap'] >= vrs.ROSTER_OVERLAP, 'Roster overlap below Valve\'s continuity rule'
            if m.get('hltv_team_pages') or (m.get('hltv_context') or {}).get('lineups'):
                assert lineup_source_ok(m, team, check.get('lineup') or []), 'Model roster has no HLTV source on this row'
    assert q['calibration_slope'] == vrs.SLOPE and q['rating_deviation'] == vrs.RD
    raw = vrs.expected(*q['points'])
    expected = [vrs.calibrated(raw), 1 - vrs.calibrated(raw)]
    assert abs(q['raw_expected'][0] - raw) < 1e-12 and abs(sum(q['raw_expected']) - 1) < 1e-12
    for i, p in enumerate(expected):
        for value in (m['probabilities'][i], q['probabilities'][i]):
            assert math.isfinite(value) and abs(value - p) < 1e-12, 'Model probability not reproducible'
        assert abs(m['fair_odds'][i] - 1 / p) < 1e-9
    assert fresh(q['observed_at'], now), 'Model inputs observed more than eight hours before the snapshot'
    age = (now.date() - dt(q['standings_as_of'] + 'T00:00:00Z').date()).days
    assert 0 <= age <= vrs.MAX_STANDINGS_AGE_DAYS, 'VRS standings too old for an originated line'
    assert vrs.MODEL_FLAG in m['flags'], 'Model row is not labelled as a non-market estimate'
    pick = None if abs(expected[0] - expected[1]) < .0001 else m['teams'][0 if expected[0] > expected[1] else 1]
    assert m['pick'] == pick, 'Pick does not follow the model probabilities'
    meta_path = vrs.VENDORED / 'meta.json'
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if q.get('standings_commit') == meta['commit'] and q['standings_file'] == meta['file']:
            # Same official file as the vendored copy: verify every input row.
            table = vrs.parse((vrs.VENDORED / meta['file']).read_text())
            for team, label, points, standing, roster, count in zip(m['teams'], q['vrs_teams'], q['points'], q['standings'], q['rosters'], q['label_counts']):
                row = [r for r in table['teams'] if r['standing'] == standing and r['name'] == label]
                assert len(row) == 1 and row[0]['points'] == points and row[0]['roster'] == roster, 'Model input differs from the official standings file'
                assert count == sum(norm(r['name']) == norm(team) for r in table['teams'])


def validate_mirror_row(m, q, now):
    """Originated VRS line from HLTV's dated Valve ranking view.

    Same arithmetic and identity rules as the official-file model, but the
    inputs are read from HLTV's page. This function therefore checks what the
    official-file path checks (formula, calibration, roster continuity, pick)
    plus the provenance rules specific to the mirror: the page is HLTV's Valve
    ranking, it is dated, the ranking is a complete long list, and the tier was
    only used for a club Valve's own monthly file does not resolve uniquely.
    """
    from scripts import vrs_mirror
    assert q['provider'] == vrs_mirror.PROVIDER, 'Mirror row with a non-mirror quote'
    parts = urlsplit(q['url'])
    # The canonical entry point is /valve-ranking/teams; HLTV also serves the
    # very same dated view with the ranking date in the path
    # (/valve-ranking/teams/2026/october/22). Both are HLTV's Valve ranking
    # and nothing else is accepted.
    dated = re.match(r'^/valve-ranking/teams/\d{4}/[a-z]+/\d{1,2}$', parts.path or '')
    assert parts.scheme == 'https' and parts.netloc == 'www.hltv.org' \
        and (parts.path == '/valve-ranking/teams' or dated), \
        'Mirror input is not HLTV\'s Valve ranking page'
    assert q['api_url'] == q['url']
    for url in (q['formula_source'], q['calibration_source']):
        bit = urlsplit(url)
        assert bit.scheme == 'https' and bit.netloc == 'github.com' and bit.path.startswith('/' + vrs.OWNER_REPO + '/'), \
            'Mirror formula or calibration is not Valve\'s own repository'
    assert q['fixture_teams'] == m['teams'], 'Mirror quote orientation differs from the fixture'
    for team, label in zip(m['teams'], q['vrs_teams']):
        if norm(team) == norm(label):
            continue
        assert any({plain_name(team), plain_name(label)} <= {plain_name(n) for n in item['names']}
                   for item in IDENTITIES), 'Mirror label does not map to the fixture team (exact or verified alias)'
    for team, check, count in zip(m['teams'], q['roster_checks'], q['label_counts']):
        if check['overlap'] is None:
            assert count == 1, 'Duplicated mirror label used without a roster check'
        else:
            assert check['overlap'] >= vrs.ROSTER_OVERLAP, 'Mirror roster overlap below Valve\'s continuity rule'
            if m.get('hltv_team_pages') or (m.get('hltv_context') or {}).get('lineups'):
                assert lineup_source_ok(m, team, check.get('lineup') or []), 'Mirror roster has no HLTV source on this row'
    assert q['ranking_teams_count'] >= 100, 'Mirror ranking is not a complete list'
    assert all(isinstance(p, int) and p > 0 for p in q['points']), 'Mirror points are not positive integers'
    assert len({norm(x) for x in q['vrs_teams']}) == 2, 'Mirror rows map both clubs to one label'
    assert q['calibration_slope'] == vrs.SLOPE and q['rating_deviation'] == vrs.RD
    raw = vrs.expected(*q['points'])
    expected = [vrs.calibrated(raw), 1 - vrs.calibrated(raw)]
    assert abs(q['raw_expected'][0] - raw) < 1e-12 and abs(sum(q['raw_expected']) - 1) < 1e-12
    for i, p in enumerate(expected):
        for value in (m['probabilities'][i], q['probabilities'][i]):
            assert math.isfinite(value) and abs(value - p) < 1e-12, 'Mirror probability not reproducible'
        assert abs(m['fair_odds'][i] - 1 / p) < 1e-9
    assert fresh(q['observed_at'], now), 'Mirror inputs observed more than eight hours before the snapshot'
    age = (now.date() - dt(q['ranking_as_of'] + 'T00:00:00Z').date()).days
    assert 0 <= age <= vrs.MAX_STANDINGS_AGE_DAYS, 'Mirror ranking too old for an originated line'
    assert vrs_mirror.MODEL_FLAG in m['flags'], 'Mirror row is not labelled as a non-market estimate'
    pick = None if abs(expected[0] - expected[1]) < .0001 else m['teams'][0 if expected[0] > expected[1] else 1]
    assert m['pick'] == pick, 'Pick does not follow the mirror probabilities'
    official = q.get('official_file') or {}
    assert official.get('as_of'), 'Mirror row must record the official standings date it was needed instead of'
    meta_path = vrs.VENDORED / 'meta.json'
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if official.get('commit') == meta['commit'] and official.get('file') == meta['file']:
            table = vrs.parse((vrs.VENDORED / meta['file']).read_text())
            counts = [sum(norm(row['name']) == norm(label) for row in table['teams']) for label in q['vrs_teams']]
            assert any(count != 1 for count in counts), \
                'Mirror line published although Valve\'s own file resolves both clubs uniquely'


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
            if m['method'] == 'research_vrs_single':
                # Final research tier: one team resolves in Valve's official
                # global standings, the other is genuinely absent from that
                # file. Reproducible from the stored per-team VRS evidence;
                # publishes a pick and no numbers.
                assert m['pick'] in m['teams'], 'Research pick is not one of the two teams'
                research = m.get('vrs_research') or {}
                resolved = research.get('resolved_vrs')
                assert isinstance(resolved, list) and len(resolved) == 2, 'Research pick without per-team VRS evidence'
                assert {r.get('team') for r in resolved} == set(m['teams']), 'VRS evidence does not cover both fixture labels'
                assert str(research.get('source') or '').startswith('https://github.com/ValveSoftware/counter-strike_regional_standings/blob/'), 'VRS research pick lacks its official standings link'
                assert research.get('standings_as_of') and isinstance(research.get('teams_count'), int) and research['teams_count'] >= 50
                listed = [r for r in resolved if r.get('status') == 'listed']
                absent = [r for r in resolved if r.get('status') == 'absent']
                assert len(listed) == 1 and len(absent) == 1, 'One-sided VRS tier without exactly one listed and one absent team'
                row = listed[0]
                assert m['pick'] == row['team'], 'One-sided research pick does not follow the listed team'
                assert isinstance(row.get('standing'), int) and row['standing'] > 0 and isinstance(row.get('points'), int)
                assert row.get('vrs_name') and isinstance(row.get('roster'), list) and row['roster']
                if plain_name(row['vrs_name']) != plain_name(row['team']):
                    used = [i for i in IDENTITIES
                            if plain_name(row['team']) in {plain_name(n) for n in i['names']}
                            and plain_name(row['vrs_name']) in {plain_name(n) for n in i['names']}]
                    assert used, 'Standings label mapping lacks a registered identity source'
                assert (row['roster_overlap'] >= 3 if row.get('roster_overlap') is not None else row.get('label_count') == 1), 'VRS identity not established'
                if row.get('roster_overlap') is not None:
                    overlap = len({plain_name(x) for x in (row.get('lineup') or [])} & {plain_name(x) for x in row['roster']})
                    assert overlap == row['roster_overlap'], 'Stored roster overlap cannot be reproduced'
                    if m.get('hltv_team_pages') or (m.get('hltv_context') or {}).get('lineups'):
                        assert lineup_source_ok(m, row['team'], row.get('lineup') or []), 'Research roster has no HLTV source on this row'
                assert absent[0].get('label_count') == 0, 'Absent claim without a zero label count'
                assert 'not a market probability' in (m.get('reason') or ''), 'Research pick must be labelled as non-market'
                assert not m['evidence'], 'Research pick must not carry a price quote'
                continue
            if str(m['method'] or '').startswith('research_rank'):
                # Full-coverage tiers: a labelled research pick with no numbers.
                # It must be reproducible from the stored per-team rank evidence.
                assert m['pick'] in m['teams'], 'Research pick is not one of the two teams'
                context = m.get('hltv_context') or {}
                resolved = context.get('resolved_ranks')
                assert isinstance(resolved, list) and len(resolved) == 2, 'Research pick without per-team rank evidence'
                assert {r.get('team') for r in resolved} == set(m['teams']), 'Rank evidence does not cover both fixture labels'
                ranked = [r for r in resolved if isinstance(r.get('hltv_rank'), int) and r['hltv_rank'] > 0]
                for row in ranked:
                    assert str(row.get('rank_source') or '').startswith('https://www.hltv.org/'), 'Ranked row lacks its HLTV ranking link'
                    assert row.get('hltv_name'), 'Ranked row lacks the HLTV team label'
                    if plain_name(row['hltv_name']) != plain_name(row['team']):
                        assert str(row.get('alias_source') or '').startswith('https://'), 'Label mapping lacks a primary source'
                if m['method'] == 'research_rank':
                    assert len(ranked) == 2, 'Full ranking tier without both ranks'
                    assert ranked[0]['hltv_rank'] != ranked[1]['hltv_rank'], 'Research pick on an equal ranking is not directional'
                    assert m['pick'] == min(ranked, key=lambda r: r['hltv_rank'])['team'], 'Research pick does not follow the verified ranking order'
                else:
                    assert m['method'] == 'research_rank_single', 'Unknown research tier'
                    assert len(ranked) == 1, 'One-sided ranking tier without exactly one ranked team'
                    assert m['pick'] == ranked[0]['team'], 'One-sided research pick does not follow the ranked team'
                    other = next(r for r in resolved if r is not ranked[0])
                    assert other.get('status') in ('unranked', 'no_rank_row'), 'One-sided claim without a genuinely absent ranking row'
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
        if m['method'] == 'model_vrs':
            validate_model_row(m, q, now)
            continue
        if m['method'] == 'model_vrs_mirror':
            validate_mirror_row(m, q, now)
            continue
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
        calculator = calculator_for(q['provider'])
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
        check = m.get('model_check') or {}
        if check.get('status') == 'ok':
            raw = vrs.expected(*check['points'])
            assert all(abs(a - b) < 1e-12 for a, b in zip(check['probabilities'], [vrs.calibrated(raw), 1 - vrs.calibrated(raw)])), 'Model comparison not reproducible'
            assert all(norm(a) == norm(b) for a, b in zip(m['teams'], check['vrs_teams'])), 'Model comparison team mapping differs'
    assert seen == set(originals)
    return {'rows_verified_against_primary_snapshot': len(seen),
            'probability_calculations_reproduced': priced}



def verify_recommendation_deadlines(soup, lookup, observed):
    """Non-table recommendations must share the sourced row's exact lifetime.

    New summary cards must not become indefinite picks when tables expire.
    Blank/unresolved labels are not recommendations and need no deadline.
    """
    selector = '.glance-row, .glance-card-mobile, .queue a, .unresolved-row, [data-next-expires]'
    for block in soup.select(selector):
        anchor = block if block.name == 'a' else block.find('a', href=True)
        fragment = urlsplit(anchor.get('href', '') if anchor else '').fragment
        assert fragment.startswith('match-') and fragment[6:] in lookup, 'Recommendation lacks a known evidence row'
        row = lookup[fragment[6:]]
        if not row.get('pick'):
            continue
        expected = pick_deadline(row, observed)
        attr = 'data-next-expires' if block.has_attr('data-next-expires') else 'data-glance-expires'
        assert expected and block.get(attr) == expected, 'Summary recommendation deadline differs from sourced lifetime'


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
        if path.name == 'picks.html' and path.parent == root:
            assert set(ids) == {m['id'] for m in published['matches'] if m['state'] == 'open'}, 'Picks must contain every open fixture, including research-only and unresolved rows'
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
                if str(m['method'] or '').startswith('research_'):
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
            if row.select_one('.prob-pair, .pick-cell .pick'):
                assert row.get('data-expires'), 'Recommendation has no complete expiry deadline'
        verify_recommendation_deadlines(soup, lookup, published.get('fixtures_observed_at'))
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
