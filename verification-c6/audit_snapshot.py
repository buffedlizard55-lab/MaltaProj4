"""Independent read-only audit; does not import or change the collector.

Usage: python verification-c6/audit_snapshot.py path/to/latest.json --output report.md
Checks retained evidence and arithmetic, not live external-source availability.
"""
import argparse
import hashlib
import json
import math
import re
import unicodedata
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit


def date(value):
    if str(value).isdigit():
        return datetime.fromtimestamp(int(value) / 1000, timezone.utc)
    result = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timezone is missing')
    return result


def name(value):
    # Independent mirror of the collector's diacritic folding (NFKD + drop
    # combining marks), so "Los Niños" and "LOS NINOS" resolve to one key here too.
    folded = unicodedata.normalize('NFKD', value).casefold()
    folded = ''.join(c for c in folded if not unicodedata.combining(c))
    return ''.join(c for c in unicodedata.normalize('NFKC', folded) if c.isalnum())


def array(value):
    return json.loads(value) if isinstance(value, str) else value


# Independent re-implementation of Valve's published VRS expectation
# (model/fit.js + model/glicko.js, fixed RD 75) and its published fit slope.
VRS_REPO = 'ValveSoftware/counter-strike_regional_standings'
VRS_Q = math.log(10) / 400
VRS_G = 1 / math.sqrt(1 + 3 * VRS_Q * VRS_Q * 75.0 * 75.0 / math.pi ** 2)


def vrs_probability(points_a, points_b):
    raw = 1 / (1 + 10 ** (-VRS_G * (float(points_a) - float(points_b)) / 400))
    return raw, 0.5 + 0.7986 * (raw - 0.5)


def same_team(label, team, identities):
    """Exact normalized label, or a registered alias with a primary-source link."""
    if name(label) == name(team):
        return True
    return any(identity.get('source') and {name(label), name(team)} <= {name(n) for n in identity.get('names', [])}
               for identity in identities)


def official_vrs_url(url, hosts=('github.com',)):
    parts = urlsplit(url or '')
    return parts.scheme == 'https' and parts.hostname in hosts and parts.path.startswith('/' + VRS_REPO + '/')


def inspect(snapshot):
    errors, rows = [], []
    raw = snapshot['fixture_evidence']
    evidence = {str(r['id']): r for r in raw}
    matches = snapshot['matches']
    ids = [m['id'] for m in matches]
    if len(ids) != len(set(ids)) or len(raw) != len(evidence):
        errors.append('Duplicate IDs in matches or fixture evidence')
    if set(ids) != set(evidence):
        errors.append('Stored fixture evidence and rendered inventory differ')
    captured = date(snapshot['generated_at'])
    for m in matches:
        problems = []
        def require(condition, message):
            if not condition:
                problems.append(message)
        try:
            r = evidence[m['id']]
            require(m['teams'] == [r.get('participants0_name'), r.get('participants1_name')], 'Team labels changed')
            require(m['team_ids'] == [r.get('participants0_id'), r.get('participants1_id')], 'Team IDs changed')
            for out, source in [('competition', 'competition_name'), ('tier', 'tier'), ('best_of', 'best_of'), ('source_status', 'status')]:
                require(m[out] == r.get(source), out + ' changed or inferred')
            for out, source in [('start', 'scheduled_start_time'), ('lock', 'lock_time')]:
                expected = r.get(source)
                require((m[out] is None if not expected else date(m[out]) == date(expected)), out + ' differs from raw timestamp')
            require(urlsplit(m['source_url']).hostname in {'play.hotspawn.com', 'www.hotspawn.com', 'hotspawn.com'}, 'Official fixture link missing')
            require(not any('picked' in k or k == 'total_picks' for k in r), 'Crowd fields retained in probability evidence')
            p = m['probabilities']
            if p is None and m.get('method') == 'research_vrs_single':
                # One-sided Valve standings tier: a pick with no numbers at all.
                # Re-derived here from the per-team evidence stored on the row.
                require(m.get('pick') in m['teams'], 'Research pick is not one of the two teams')
                require(m['fair_odds'] is None and not m.get('evidence'), 'Research row carries derived numbers or a quote')
                require('not a market probability' in (m.get('reason') or ''), 'Research pick not labelled as non-market')
                require(any('no probability published' in flag.lower() for flag in m.get('flags', [])), 'Research pick lacks its low-confidence flag')
                research = m.get('vrs_research') or {}
                require(official_vrs_url(research.get('source')), 'Research pick lacks its official Valve standings link')
                require(date(research.get('observed_at')) <= captured, 'Research standings observation is dated after the snapshot')
                age = (captured.date() - date(str(research.get('standings_as_of')) + 'T00:00:00+00:00').date()).days
                require(0 <= age <= 62, 'VRS standings too old for a research pick')
                require(isinstance(research.get('teams_count'), int) and research['teams_count'] >= 50, 'Standings size not recorded')
                resolved = research.get('resolved_vrs')
                require(isinstance(resolved, list) and len(resolved) == 2, 'Research pick without per-team VRS evidence')
                if isinstance(resolved, list) and len(resolved) == 2:
                    require([r.get('team') for r in resolved] == m['teams'], 'VRS evidence does not cover both fixture labels in order')
                    listed = [r for r in resolved if r.get('status') == 'listed']
                    absent = [r for r in resolved if r.get('status') == 'absent']
                    require(len(listed) == 1 and len(absent) == 1, 'One-sided VRS tier without exactly one listed and one absent team')
                    if len(listed) == 1 and len(absent) == 1:
                        row = listed[0]
                        require(m['pick'] == row['team'], 'One-sided research pick does not follow the listed team')
                        require(isinstance(row.get('standing'), int) and row['standing'] > 0 and isinstance(row.get('points'), int), 'Listed row lacks standing or points')
                        require(bool(row.get('vrs_name')) and isinstance(row.get('roster'), list) and bool(row['roster']), 'Listed row lacks its standings label or roster')
                        require(same_team(row.get('vrs_name') or '', row['team'], row.get('identity_sources', [])), 'Standings label is neither exact nor a sourced alias')
                        require(row['roster_overlap'] >= 3 if row.get('roster_overlap') is not None else row.get('label_count') == 1, 'VRS identity not established')
                        if row.get('roster_overlap') is not None:
                            overlap = len({name(x) for x in (row.get('lineup') or [])} & {name(x) for x in row['roster']})
                            require(overlap == row['roster_overlap'], 'Stored roster overlap cannot be reproduced')
                        require(absent[0].get('label_count') == 0, 'Absent claim without a zero label count')
            elif p is None and str(m.get('method') or '').startswith('research_rank'):
                # Full-coverage research tiers: a pick with no numbers at all.
                # The auditor does not import the collector, so it re-derives the
                # pick from the per-team evidence stored on the row itself.
                require(m.get('pick') in m['teams'], 'Research pick is not one of the two teams')
                require(m['fair_odds'] is None and not m.get('evidence'), 'Research row carries derived numbers or a quote')
                require('not a market probability' in (m.get('reason') or ''), 'Research pick not labelled as non-market')
                require(any('no probability published' in flag.lower() for flag in m.get('flags', [])), 'Research pick lacks its low-confidence flag')
                context = m.get('hltv_context') or {}
                pages = m.get('hltv_team_pages') or {}
                # Rank evidence sits on the fixture record, or on the two
                # clubs' own HLTV team pages when HLTV lists no fixture page
                # (session 174afa4f). Each is replayed from its own raw
                # record; a team-page pick may not cite a fixture page.
                team_pages_mode = context.get('resolved_ranks') is None and isinstance(pages.get('resolved_ranks'), list)
                if team_pages_mode:
                    require(bool(pages.get('observed_at')), 'Team-page rank pick lacks its observation time')
                    if pages.get('observed_at'):
                        require(date(pages.get('observed_at')) <= captured, 'Team-page evidence is dated after the snapshot')
                    resolved = pages.get('resolved_ranks')
                    raw_pages = {name(r.get('team')): r for r in pages.get('teams', []) if isinstance(r, dict) and r.get('team')}
                    require(len(raw_pages) == 2, 'Team-page rank pick without both stored team pages')
                else:
                    require(str(context.get('source', '')).startswith('https://www.hltv.org/'), 'Research pick lacks an HLTV source')
                    require(date(context.get('observed_at')) <= captured, 'Research context is dated after the snapshot')
                    resolved = context.get('resolved_ranks')
                    raw_pages = {}
                require(isinstance(resolved, list) and len(resolved) == 2, 'Research pick without per-team rank evidence')
                if isinstance(resolved, list) and len(resolved) == 2:
                    require([r.get('team') for r in resolved] == m['teams'], 'Rank evidence does not cover both fixture labels in order')
                    raw_ranks = {name(r.get('team')): r.get('hltv_rank') for r in context.get('ranks', []) if isinstance(r, dict)}
                    ranked = []
                    for row in resolved:
                        if team_pages_mode:
                            require(row.get('evidence') == 'hltv_team_pages', 'Team-page rank evidence mislabelled')
                            raw_page = raw_pages.get(name(row.get('team')))
                            require(raw_page is not None, 'Resolved rank has no stored team page')
                            if raw_page is not None:
                                require(str(raw_page.get('url') or '').startswith('https://www.hltv.org/team/'), 'Team-page evidence is not an HLTV team page')
                                require(row.get('team_page_url') == raw_page.get('url'), 'Resolved rank cites a different team page')
                                require(raw_page.get('label') == row.get('hltv_name'), 'Resolved label differs from the stored page heading')
                                if row.get('hltv_rank') is not None:
                                    require(raw_page.get('world_rank_status') == 'ranked' and raw_page.get('world_rank') == row['hltv_rank'], 'Published rank differs from the stored team page')
                                    require(raw_page.get('world_rank_source') == row.get('rank_source'), 'Ranking link differs from the stored team page')
                                elif row.get('status') == 'unranked':
                                    require(raw_page.get('world_rank_status') == 'unranked' and raw_page.get('world_rank') is None, 'Unranked claim without HLTV stating the absence')
                        if row.get('hltv_rank') is None:
                            continue
                        require(isinstance(row['hltv_rank'], int) and row['hltv_rank'] > 0, 'Non-numeric rank published')
                        require(str(row.get('rank_source') or '').startswith('https://www.hltv.org/'), 'Ranked row lacks its HLTV ranking link')
                        require(row.get('hltv_name'), 'Ranked row lacks the HLTV team label')
                        if name(row.get('hltv_name')) != name(row['team']):
                            require(str(row.get('alias_source') or '').startswith('https://'), 'Label mapping lacks a primary source')
                        if not team_pages_mode:
                            require(raw_ranks.get(name(row.get('hltv_name'))) == row['hltv_rank'], 'Published rank differs from the retained HLTV context')
                        ranked.append(row)
                    if m['method'] == 'research_rank':
                        require(len(ranked) == 2, 'Full ranking tier without both ranks')
                        if len(ranked) == 2:
                            require(ranked[0]['hltv_rank'] != ranked[1]['hltv_rank'], 'Research pick on an equal ranking is not directional')
                            require(m['pick'] == min(ranked, key=lambda r: r['hltv_rank'])['team'], 'Research pick does not follow the verified ranking order')
                    else:
                        require(m['method'] == 'research_rank_single', 'Unknown research tier')
                        require(len(ranked) == 1, 'One-sided ranking tier without exactly one ranked team')
                        if len(ranked) == 1:
                            require(m['pick'] == ranked[0]['team'], 'One-sided research pick does not follow the ranked team')
                            other = next((r for r in resolved if r is not ranked[0]), {})
                            require(other.get('status') in ('unranked', 'no_rank_row'), 'One-sided claim without a genuinely absent ranking row')
            elif p is None and m.get('method') == 'research_form':
                # Final research tier (session b6e37c61): HLTV recent form, then
                # lifetime head-to-head series wins. Re-derived here from the
                # raw parsed results stored on the row (context['form'] mapped
                # through context['team_map']), with the published bounds:
                # at least 3 results per side, an equal comparison window of at
                # most 10. Publishes a pick and no numbers at all.
                require(m.get('pick') in m['teams'], 'Form pick is not one of the two teams')
                require(m['fair_odds'] is None and not m.get('evidence'), 'Form row carries derived numbers or a quote')
                require('not a market probability' in (m.get('reason') or ''), 'Form pick not labelled as non-market')
                require(any('no probability published' in flag.lower() for flag in m.get('flags', [])), 'Form pick lacks its low-confidence flag')
                context = m.get('hltv_context') or {}
                require(str(context.get('source', '')).startswith('https://www.hltv.org/'), 'Form pick lacks an HLTV source')
                require(date(context.get('observed_at')) <= captured, 'Form context is dated after the snapshot')
                form = context.get('form') if isinstance(context.get('form'), dict) else {}
                team_map = context.get('team_map') if isinstance(context.get('team_map'), dict) else {}
                resolved = context.get('resolved_form')
                require(isinstance(resolved, list) and len(resolved) == 2, 'Form pick without per-team form evidence')
                detail = context.get('form_detail') or {}
                window = detail.get('window')
                require(isinstance(window, int) and 3 <= window <= 10, 'Form pick window outside the published bounds')
                if isinstance(resolved, list) and len(resolved) == 2 and isinstance(window, int):
                    require([r.get('team') for r in resolved] == m['teams'], 'Form evidence does not cover both fixture labels in order')
                    wins = {}
                    for row in resolved:
                        label = row.get('hltv_name')
                        require(label and team_map.get(label) == row.get('team'), 'Form label does not map to the fixture label on this row')
                        raw = [r for r in (form.get(label) or [])
                               if isinstance(r, dict) and isinstance(r.get('won'), bool) and r.get('opponent') and r.get('score')]
                        require(len(raw) >= window, 'Stored form summary covers more results than the raw evidence holds')
                        used = raw[:window]
                        require(row.get('results') == used, 'Form results differ from the retained HLTV evidence')
                        wins[row.get('team')] = sum(1 for r in used if r['won'])
                        require(row.get('wins') == wins[row.get('team')] and row.get('losses') == window - wins[row.get('team')],
                                'Form win totals cannot be reproduced')
                    if wins.get(m['teams'][0]) != wins.get(m['teams'][1]):
                        require(detail.get('basis') == 'recent_form', 'Form pick basis mislabelled')
                        require(m['pick'] == max(m['teams'], key=lambda t: wins.get(t, -1)), 'Form pick does not follow the recent-results edge')
                    else:
                        require(detail.get('basis') == 'head_to_head', 'Level form without a head-to-head basis')
                        h2h = context.get('head_to_head') or {}
                        stored = (detail.get('head_to_head') or {}).get('wins') or {}
                        teams, hwins = h2h.get('teams') or [], h2h.get('wins') or []
                        require(len(teams) == 2 and len(hwins) == 2 and all(t in team_map for t in teams),
                                'Head-to-head evidence missing from the row')
                        if len(teams) == 2 and len(hwins) == 2:
                            mapped = {team_map[t]: w for t, w in zip(teams, hwins) if t in team_map}
                            require(mapped == stored, 'Head-to-head summary differs from the retained HLTV evidence')
                            require(mapped.get(m['teams'][0]) != mapped.get(m['teams'][1]), 'Form pick on a level head-to-head')
                            require(m['pick'] == max(m['teams'], key=lambda t: mapped.get(t, -1)), 'Form pick does not follow the head-to-head edge')
            elif p is None:
                require(m['pick'] is None and m['fair_odds'] is None and m['method'] is None, 'Unverified row has a derived value')
                require(bool(m['reason']), 'Unresolved/non-open row lacks explanation')
            elif m.get('method') == 'model_vrs':
                # Originated line: recompute from the retained Valve inputs only.
                require(m['state'] == 'open', 'Non-open row has actionable probability')
                require(date(m['lock']) > captured and date(m['start']) > captured, 'Pick already locked at generation')
                require(len(p) == 2 and all(math.isfinite(x) and 0 < x < 1 for x in p), 'Invalid probability')
                require(len(m['evidence']) == 1, 'Expected one selected source')
                q = m['evidence'][0]
                require(q['provider'] == 'Valve VRS model', 'Model row without its model record')
                require(all(official_vrs_url(u) for u in [q['url'], q['formula_source'], q['calibration_source'], *q['details_urls']]), 'Model input outside the official Valve repository')
                require(official_vrs_url(q['api_url'], ('raw.githubusercontent.com', 'github.com')), 'Model data URL outside the official Valve repository')
                require(-300 <= (captured - date(q['observed_at'])).total_seconds() <= 28800, 'Stale model input observation')
                age = (captured.date() - date(q['standings_as_of'] + 'T00:00:00+00:00').date()).days
                require(0 <= age <= 62, 'VRS standings too old for an originated line')
                require(q['fixture_teams'] == m['teams'], 'Model orientation differs from the fixture')
                identities = q.get('identity_sources', [])
                require(all(same_team(v, t, identities) for t, v in zip(m['teams'], q['vrs_teams'])), 'VRS label is neither exact nor a sourced alias')
                for check, count in zip(q['roster_checks'], q['label_counts']):
                    require(check['overlap'] >= 3 if check['overlap'] is not None else count == 1, 'VRS roster identity not established')
                require(q['calibration_slope'] == 0.7986 and q['rating_deviation'] == 75, 'Model constants differ from Valve\'s published values')
                raw, cal = vrs_probability(*q['points'])
                expected = [cal, 1 - cal]
                require(abs(q['raw_expected'][0] - raw) < 1e-10, 'Raw VRS expectation mismatch')
                require(all(abs(x - y) < 1e-10 for x, y in zip(p, expected)), 'Independent model calculation mismatch')
                require(all(abs(x - 1 / y) < 1e-10 for x, y in zip(m['fair_odds'], expected)), 'Fair odds mismatch')
                pick = None if abs(expected[0] - expected[1]) < .0001 else m['teams'][expected[1] > expected[0]]
                require(m['pick'] == pick, 'Wrong pick orientation')
                require(any('not a market price' in flag for flag in m.get('flags', [])), 'Model row not labelled as a non-market estimate')
            elif m.get('method') == 'model_vrs_mirror':
                # Originated line whose points come from HLTV's dated view of
                # Valve's ranking because Valve's monthly file cannot resolve a
                # club. Recomputed here from the retained inputs, independently
                # of the collector, with the same provenance rules.
                require(m['state'] == 'open', 'Non-open row has actionable probability')
                require(date(m['lock']) > captured and date(m['start']) > captured, 'Pick already locked at generation')
                require(len(p) == 2 and all(math.isfinite(x) and 0 < x < 1 for x in p), 'Invalid probability')
                require(len(m['evidence']) == 1, 'Expected one selected source')
                q = m['evidence'][0]
                require(q.get('provider') == 'HLTV Valve ranking (Valve points)', 'Mirror row without its mirror record')
                ranking = urlsplit(q.get('url') or '')
                require(ranking.scheme == 'https' and ranking.hostname == 'www.hltv.org'
                        and re.fullmatch(r'/valve-ranking/teams(/\d{4}/[a-z]+/\d{1,2})?', ranking.path or '') is not None,
                        'Mirror input is not HLTV Valve ranking')
                require(q.get('api_url') == q.get('url'), 'Mirror data URL differs from its page')
                require(all(official_vrs_url(u) for u in (q.get('formula_source'), q.get('calibration_source'))),
                        'Mirror formula or calibration outside Valve\'s repository')
                require(-300 <= (captured - date(q['observed_at'])).total_seconds() <= 28800, 'Stale mirror observation')
                age = (captured.date() - date(str(q.get('ranking_as_of')) + 'T00:00:00+00:00').date()).days
                require(0 <= age <= 62, 'Mirror ranking too old for an originated line')
                require(q.get('fixture_teams') == m['teams'], 'Mirror orientation differs from the fixture')
                identities = q.get('identity_sources', [])
                require(all(same_team(v, t, identities) for t, v in zip(m['teams'], q.get('vrs_teams') or [])),
                        'Mirror label is neither exact nor a sourced alias')
                require(len(q.get('roster_checks') or []) == 2, 'Mirror row without two roster checks')
                for check, count in zip(q.get('roster_checks') or [], q.get('label_counts') or []):
                    require(check['overlap'] >= 3 if check.get('overlap') is not None else count == 1,
                            'Mirror roster identity not established')
                require(isinstance(q.get('ranking_teams_count'), int) and q['ranking_teams_count'] >= 100,
                        'Mirror ranking is not a complete list')
                require(all(isinstance(x, int) and x > 0 for x in q.get('points') or []), 'Mirror points invalid')
                require((q.get('official_file') or {}).get('as_of'),
                        'Mirror row does not record the official standings it replaced')
                require(q.get('calibration_slope') == 0.7986 and q.get('rating_deviation') == 75,
                        'Mirror constants differ from Valve\'s published values')
                raw, cal = vrs_probability(*q['points'])
                expected = [cal, 1 - cal]
                require(abs(q['raw_expected'][0] - raw) < 1e-10, 'Raw mirror expectation mismatch')
                require(all(abs(x - y) < 1e-10 for x, y in zip(p, expected)), 'Independent mirror calculation mismatch')
                require(all(abs(x - 1 / y) < 1e-10 for x, y in zip(m['fair_odds'], expected)), 'Fair odds mismatch')
                pick = None if abs(expected[0] - expected[1]) < .0001 else m['teams'][expected[1] > expected[0]]
                require(m['pick'] == pick, 'Wrong pick orientation')
                require(any('not a market price' in flag for flag in m.get('flags', [])),
                        'Mirror row not labelled as a non-market estimate')
            else:
                require(m['state'] == 'open', 'Non-open row has actionable probability')
                require(date(m['lock']) > captured and date(m['start']) > captured, 'Pick already locked at generation')
                require(len(p) == 2 and all(math.isfinite(x) and 0 < x < 1 for x in p), 'Invalid probability')
                require(abs(sum(p) - 1) < 1e-10, 'Probabilities do not sum to one')
                require(len(m['evidence']) == 1, 'Expected one selected independently verified source')
                q = m['evidence'][0]
                check = m.get('model_check') or {}
                if check.get('status') == 'ok':
                    _, cal = vrs_probability(*check['points'])
                    require(abs(check['probabilities'][0] - cal) < 1e-10 and abs(check['probabilities'][1] - (1 - cal)) < 1e-10, 'Model comparison mismatch')
                    require(all(same_team(v, t, check.get('identity_sources', [])) for t, v in zip(m['teams'], check['vrs_teams'])), 'Model comparison mapped to another team')
                require(date(q['start']) == date(m['start']), 'External UTC start mismatch')
                require(-300 <= (captured - date(q['observed_at'])).total_seconds() <= 28800, 'Stale observation used')
                source_names = q['source_teams']
                aliases = [{name(t)} for t in source_names]
                for i, t in enumerate(source_names):
                    for meta in q.get('team_metadata', []):
                        if meta['name'] == t and meta.get('abbreviation'):
                            aliases[i].add(name(meta['abbreviation']))
                    for identity in q.get('identity_sources', []):
                        if name(t) in {name(n) for n in identity['names']}:
                            require(bool(identity.get('source')), 'Alias has no primary-source link')
                            aliases[i].update(name(n) for n in identity['names'])
                    listed = (q.get('team_aliases') or [None, None])
                    if i < len(listed) and listed[i]:
                        introduced = [n for n in listed[i] if name(n) != name(t)]
                        if introduced:
                            sources = q.get('alias_sources') or (q.get('raw') or {}).get('alias_sources') or []
                            src = sources[i] if i < len(sources) else None
                            require(str(src or '').startswith('https://'), 'Alias has no primary-source link')
                        aliases[i].update(name(n) for n in listed[i])
                order = []
                for t in m['teams']:
                    candidates = [i for i, accepted in enumerate(aliases) if name(t) in accepted]
                    require(len(candidates) == 1, 'Unverified or ambiguous alias')
                    if len(candidates) != 1:
                        raise ValueError('Cannot orient quote safely')
                    order.append(candidates[0])
                require(set(order) == {0, 1}, 'Both teams map to the same outcome')
                if q['provider'] == 'Polymarket':
                    line = q['raw']
                    require(line['sportsMarketType'] == 'moneyline', 'Not a match-winner market')
                    require(array(line['outcomes']) == source_names, 'Exchange outcome order changed')
                    require(line['active'] and not line['closed'] and line['acceptingOrders'], 'Closed exchange quote used')
                    weights = [Decimal(str(x)) for x in array(line['outcomePrices'])]
                    require(-300 <= (captured-date(line['updatedAt'])).total_seconds() <= 28800, 'Stale exchange price used')
                    bid, ask = Decimal(str(line['bestBid'])), Decimal(str(line['bestAsk']))
                    spread = ask - bid
                    strict = spread <= Decimal('.25')
                    wide = q.get('tier') == 'wide_exchange' and m.get('method') == 'exchange_wide'
                    require(0 < bid <= ask < 1, 'Invalid two-sided exchange quote')
                    if wide:
                        # Low-confidence tier: it may exist only where strict fails,
                        # inside the documented ceiling, with its rejection published.
                        require(not strict and spread <= Decimal('.60'), 'Wide tier outside its documented bounds')
                        require(bool(q.get('strict_rejection')), 'Wide tier without the strict rejection recorded')
                        require('Low confidence' in (q.get('warning') or ''), 'Wide tier without its low-confidence warning')
                        require(any('Low confidence' in flag for flag in m.get('flags', [])), 'Wide tier not flagged on the row')
                        require(m.get('method') == 'exchange_wide', 'Wide tier method label mismatch')
                    else:
                        require(strict, 'Exchange spread gate failed')
                        require(m.get('method') == 'exchange', 'Strict exchange row carries a different method label')
                    require(Decimal(str(line['liquidity'])) >= 100, 'Exchange liquidity gate failed')
                elif isinstance(q['raw'].get('odds'), list) and len(q['raw']['odds']) == 2:
                    # Researched two-way decimal book listing: independent de-vig
                    # from the receipt's own odds fields, same gates as the collector.
                    raw = q['raw']
                    require(str(raw.get('id')) == str(q['id']), 'Book listing id mismatch')
                    require(q['api_url'] == (raw.get('api_url') or raw.get('url')), 'Book listing link mismatch')
                    require(all(isinstance(x, (int, float)) and math.isfinite(float(x)) and x > 1 for x in raw['odds']),
                            'Invalid decimal odds')
                    weights = [1 / Decimal(str(x)) for x in raw['odds']]
                    require(Decimal('-.02') <= sum(weights) - 1 <= Decimal('.25'), 'Bookmaker margin gate failed')
                    require(date(raw['observed_at']) == date(q['observed_at']), 'Book listing observation time mismatch')
                elif q['provider'] == 'Pinnacle':
                    matchup, line = q['raw']['matchup'], q['raw']['line']
                    require(matchup['id'] == line['matchupId'], 'Bookmaker join mismatch')
                    require(matchup['league']['name'].startswith('CS2 - '), 'Wrong esport')
                    require(matchup['status'] == 'pending' and not matchup['isLive'], 'Live/closed fixture used')
                    require(line['status'] == 'open' and line['period'] == 0 and line['type'] == 'moneyline' and not line['isAlternate'], 'Invalid bookmaker market')
                    require(date(line['cutoffAt']) > captured, 'Expired bookmaker quote')
                    participants = {x['alignment']: x['name'] for x in matchup['participants']}
                    require([participants['home'], participants['away']] == source_names, 'Bookmaker outcome order changed')
                    prices = {x['designation']: Decimal(str(x['price'])) for x in line['prices']}
                    odds = [1 + (v/100 if v > 0 else 100/-v) for v in [prices['home'], prices['away']]]
                    weights = [1/x for x in odds]
                    require(Decimal('-.02') <= sum(weights)-1 <= Decimal('.25'), 'Bookmaker margin gate failed')
                elif q['provider'] == 'Kalshi':
                    # Two binary "<team> wins" markets under one event ticker.
                    # Independently re-derived here (session 32efbb66): the
                    # scheduled start comes from each market's own contract
                    # sentence with an explicit EST/EDT offset, cross-checked
                    # against the wall-clock time encoded in the event
                    # ticker; occurrence_datetime is never a start.
                    raw = q['raw']
                    markets = raw.get('markets') or []
                    require(raw.get('event_ticker') == q['id'], 'Kalshi event ticker mismatch')
                    require(q['api_url'] == 'https://api.elections.kalshi.com/trade-api/v2/events/' + q['id'],
                            'Kalshi API link mismatch')
                    require(len(markets) == 2, 'Kalshi quote without exactly two team markets')
                    require([mk.get('yes_sub_title') for mk in markets] == source_names,
                            'Kalshi outcome order changed')
                    months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7,
                              'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12, 'January': 1,
                              'February': 2, 'March': 3, 'April': 4, 'June': 6, 'July': 7,
                              'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
                    ticker_months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7,
                                     'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
                    weights = []
                    spread = Decimal('0')
                    liquidity = Decimal('0')
                    starts = set()
                    for mk in markets:
                        require(mk.get('market_type') == 'binary' and mk.get('status') == 'active'
                                and (mk.get('result') or '') == '', 'Kalshi market is not an open binary market')
                        require(str(mk.get('ticker') or '').startswith(q['id'] + '-'),
                                'Kalshi market does not belong to the quoted event')
                        require(mk.get('title') == str(mk.get('yes_sub_title')) + ' wins'
                                and mk.get('no_sub_title') == mk.get('yes_sub_title'),
                                'Kalshi market is not a team match-winner market')
                        require('refers to the full match' in str(mk.get('rules_secondary') or ''),
                                'Kalshi contract does not define a full-match market')
                        require(all(label in str(mk.get('rules_primary') or '') for label in source_names),
                                'Kalshi contract text does not name both teams')
                        hit = re.search(r'originally scheduled for ([A-Z][a-z]+) (\d{1,2}), (\d{4}) at '
                                        r'(\d{1,2}):(\d{2}) (AM|PM) ([A-Z]{2,4})', str(mk.get('rules_primary') or ''))
                        tick = re.match(r'^KXCS2GAME-(\d{2})(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)'
                                        r'(\d{2})(\d{2})(\d{2})', q['id'])
                        require(hit is not None and tick is not None, 'Kalshi scheduled start is not stated exactly')
                        mon, day, year, hour, minute, meridiem, tz_name = hit.groups()
                        require(tz_name in ('EST', 'EDT') and mon in months, 'Kalshi start timezone is ambiguous')
                        hour24 = int(hour) % 12 + (12 if meridiem == 'PM' else 0)
                        wall = (int(year), months[mon], int(day), hour24, int(minute))
                        require(wall == (2000 + int(tick.group(1)), ticker_months[tick.group(2)],
                                         int(tick.group(3)), int(tick.group(4)), int(tick.group(5))),
                                'Kalshi rules start disagrees with its event ticker')
                        from datetime import timedelta
                        starts.add(datetime(*wall, tzinfo=timezone.utc)
                                   - timedelta(hours=-5 if tz_name == 'EST' else -4))
                        bid, ask = Decimal(str(mk['yes_bid_dollars'])), Decimal(str(mk['yes_ask_dollars']))
                        bid_size, ask_size = Decimal(str(mk['yes_bid_size_fp'])), Decimal(str(mk['yes_ask_size_fp']))
                        require(0 < bid <= ask < 1 and bid_size > 0 and ask_size > 0,
                                'Kalshi two-sided quote unavailable')
                        spread = max(spread, ask - bid)
                        liquidity += Decimal(str(mk['open_interest_fp'])) + min(bid_size * bid, ask_size * ask)
                        weights.append((bid + ask) / 2)
                    require(len(starts) == 1, 'Kalshi team markets state different scheduled starts')
                    require(starts.pop() == date(q['start']), 'Kalshi stored start differs from its contract text')
                    require(spread <= Decimal('.25'), 'Kalshi spread gate failed')
                    require(liquidity >= 50, 'Kalshi liquidity gate failed')
                    require(Decimal('.95') <= sum(weights) <= Decimal('1.05'), 'Kalshi pair of prices is inconsistent')
                    require(m.get('method') == 'exchange', 'Kalshi row carries a different method label')
                else:
                    raise ValueError('Unknown provider; independent recalculation unavailable')
                expected = [float(weights[i]/sum(weights)) for i in order]
                require(all(abs(x-y) < 1e-10 for x, y in zip(p, expected)), 'Independent probability calculation mismatch')
                require(all(abs(x-1/y) < 1e-10 for x, y in zip(m['fair_odds'], expected)), 'Fair odds mismatch')
                pick = None if abs(expected[0]-expected[1]) < .0001 else m['teams'][expected[1] > expected[0]]
                require(m['pick'] == pick, 'Wrong pick orientation')
                require(bool(q.get('api_url')) and bool(q.get('url')), 'External source links missing')
        except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
            problems.append('Cannot verify row: ' + str(exc))
        rows.append((m, problems))
        errors.extend(f"{m['id']}: {p}" for p in problems)
    return rows, errors


def report(snapshot, digest):
    rows, errors = inspect(snapshot)
    result = ['# Independent retained-evidence audit', '',
        'This audits the archived evidence and arithmetic, not the present live lobby or current prices.',
        f"Snapshot: `{snapshot['generated_at']}` · SHA-256: `{digest}`", '',
        f"Rows checked: **{len(rows)}** · Arithmetic/field failures: **{len(errors)}**", '',
        '| Fixture | Teams | Probability source | Result |', '| --- | --- | --- | --- |']
    for m, problems in rows:
        q = m['evidence'][0] if m.get('evidence') else None
        source = f"[{q['provider']}]({q['api_url']})" if q else 'Not priced; blank values checked'
        result.append(f"| [{m['id']}]({m['source_url']}) | {' / '.join(t or 'Unverified' for t in m['teams'])} | {source} | {'; '.join(problems) if problems else 'Consistent with stored evidence'} |")
    result += ['', '## Limitations', '',
        '- Successful audit means internally consistent with retained source fields, not independent confirmation of the entire live upstream response.',
        '- Alias source URLs are checked for presence. Their organizational claims require separate primary-source review.',
        '- Source access, incomplete upstream inventory, calibration, and later cancellations cannot be established by arithmetic checks.',
        '- Snapshot-time open/closed status is not a promise of current availability. Live refresh and mobile stale/lock suppression remain deployment acceptance requirements.']
    return '\n'.join(result)+'\n', errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    content = args.snapshot.read_bytes()
    text, errors = report(json.loads(content), hashlib.sha256(content).hexdigest())
    args.output.write_text(text)
    print(f'{args.output}: {len(errors)} failures')
    for error in errors:
        print('FAILED ' + error)
    raise SystemExit(bool(errors))
