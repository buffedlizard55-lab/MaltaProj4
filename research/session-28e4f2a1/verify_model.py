"""Session 28e4f2a1 — independent re-derivation of every VRS model line.

Deliberately does NOT import ``scripts/``: the official markdown is parsed here
again, Valve's own formula is re-implemented from
``model/fit.js`` + ``model/glicko.js`` (Glicko expected score with fixed
RD 75) and the calibration slope read off ``modelfit.png`` (0.7986), so a bug
in the production model cannot make this pass.

Inputs (all official bytes retained beside this script):
  research/session-28e4f2a1/valve-live-2026-10-05.md
      byte-for-byte copy of
      github.com/ValveSoftware/counter-strike_regional_standings/blob/
      eec4853d.../live/2026/standings_global_2026_10_05.md
  data/latest.json
      the snapshot the site was built from
"""
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OFFICIAL = HERE / 'valve-live-2026-10-05.md'
ROW = re.compile(r'^\|\s*(\d+)\s*\|\s*(-?\d+)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*\[details\]')

# Valve's own constants: model/fit.js defaultGlickoParams.rd = 75,
# model/glicko.js Q = ln(10)/400 and addPendingMatch's g()/ev().
RD = 75.0
Q = math.log(10) / 400
G = 1 / math.sqrt(1 + 3 * Q * Q * RD * RD / (math.pi ** 2))
SLOPE = 0.7986          # modelfit.png: "y = 0.7986x + 0.126"
OVERLAP = 3             # model/team.js TEAM_OVERLAP_TO_SHARE_ROSTER


def expected(a, b):
    return 1 / (1 + 10 ** (-G * (float(a) - float(b)) / 400))


def calibrated(raw):
    return 0.5 + SLOPE * (raw - 0.5)


def table(path):
    rows = []
    for line in path.read_text().splitlines():
        m = ROW.match(line)
        if m:
            rows.append({'standing': int(m.group(1)), 'points': int(m.group(2)),
                         'name': m.group(3).strip(),
                         'roster': [p.strip() for p in m.group(4).split(',') if p.strip()]})
    return rows


def main():
    rows = table(OFFICIAL)
    by_name = {}
    for r in rows:
        by_name.setdefault(r['name'].strip().lower(), []).append(r)
    snap = json.loads((ROOT / 'data' / 'latest.json').read_text())
    out = {'official_file': {'path': str(OFFICIAL.relative_to(ROOT)),
                             'sha256': hashlib.sha256(OFFICIAL.read_bytes()).hexdigest(),
                             'rows': len(rows)},
           'snapshot_generated_at': snap['generated_at'],
           'rows': [], 'problems': []}
    for m in snap['matches']:
        if m.get('state') != 'open':
            continue
        quote = (m.get('evidence') or [{}])[0]
        check = m.get('model_check') or {}
        kind = None
        payload = None
        if m.get('method') == 'model_vrs':
            kind, payload = 'published_line', quote
        elif m.get('method') == 'model_vrs_mirror':
            kind, payload = 'mirror_line', quote
        elif check.get('status') == 'ok':
            kind, payload = 'market_check', check
        else:
            continue
        teams = payload.get('vrs_teams') or []
        points = payload.get('points') or []
        if len(teams) != 2 or len(points) != 2:
            out['problems'].append('%s: model payload lacks two resolved VRS teams' % m['id'])
            continue
        record = {'fixture': m['id'], 'kind': kind, 'fixture_teams': m['teams'],
                  'vrs_teams': teams, 'snapshot_points': points,
                  'confirmed': []}
        if kind == 'mirror_line':
            # The mirror tier's points come from HLTV's dated copy of Valve's
            # ranking, not from the monthly Valve file retained beside this
            # script, so the bytes-level confirmation below cannot apply. What
            # CAN be re-derived offline is the arithmetic, and what CAN be
            # pinned is the provenance: the dated page, its sha256 and the
            # Valve file the mirror itself cites. A mirror row without all of
            # those is a problem, not a pass.
            record['mirror_provenance'] = {
                'ranking_url': payload.get('url'),
                'ranking_as_of': payload.get('ranking_as_of'),
                'ranking_page_sha256': payload.get('ranking_page_sha256'),
                'ranking_teams_count': payload.get('ranking_teams_count'),
                'cited_valve_file': payload.get('official_file'),
            }
            prov = record['mirror_provenance']
            if not (str(prov['ranking_url'] or '').startswith('https://www.hltv.org/valve-ranking/')
                    and prov['ranking_as_of'] and len(str(prov['ranking_page_sha256'] or '')) == 64):
                out['problems'].append('%s: mirror line lacks dated HLTV provenance' % m['id'])
            if prov['cited_valve_file'] != {'file': 'standings_global_2026_10_05.md',
                                            'commit': 'eec4853d7bcf0f1f7efe7f0d901234bef7e98b75',
                                            'as_of': '2026-10-05'}:
                out['problems'].append('%s: mirror line cites an unexpected Valve file %r'
                                       % (m['id'], prov['cited_valve_file']))
            raw = expected(points[0], points[1])
            p = [calibrated(raw), 1 - calibrated(raw)]
            published = payload.get('probabilities')
            record.update(raw_expected=raw, recomputed=p, published=published,
                          reproduces=bool(published) and max(abs(a - b) for a, b in zip(p, published)) < 1e-12)
            if not record['reproduces']:
                out['problems'].append('%s: recomputed %r != published %r' % (m['id'], p, published))
            out['rows'].append(record)
            continue
        for name, point in zip(teams, points):
            hits = by_name.get(name.strip().lower(), [])
            record['confirmed'].append({'team': name, 'listed_rows': hits,
                                        'points_match': any(h['points'] == point for h in hits)})
            if not hits:
                out['problems'].append('%s: %s is not in the official file' % (m['id'], name))
            elif not any(h['points'] == point for h in hits):
                out['problems'].append('%s: %s points %r not found in the official file'
                                       % (m['id'], name, point))
        raw = expected(points[0], points[1])
        p = [calibrated(raw), 1 - calibrated(raw)]
        record['raw_expected'] = raw
        record['recomputed'] = p
        published = payload.get('probabilities')
        record['published'] = published
        record['reproduces'] = bool(published) and max(abs(a - b) for a, b in zip(p, published)) < 1e-12
        if not record['reproduces']:
            out['problems'].append('%s: recomputed %r != published %r' % (m['id'], p, published))
        # A club label that Valve repeats must be distinguished by roster, never
        # by picking the better-ranked row.
        lineups = [c.get('lineup') for c in (payload.get('roster_checks') or [])]
        for index, confirm in enumerate(record['confirmed']):
            if len(confirm['listed_rows']) > 1:
                lineup = lineups[index] if index < len(lineups) else None
                scored = []
                for h in confirm['listed_rows']:
                    overlap = (len({x.lower() for x in lineup} & {x.lower() for x in h['roster']})
                               if lineup else None)
                    scored.append({'standing': h['standing'], 'overlap': overlap})
                chosen = points[index]
                best = max((x['overlap'] for x in scored if x['overlap'] is not None), default=None)
                winners = [x for x in scored if x['overlap'] == best]
                chosen_row = next(h for h in confirm['listed_rows'] if h['points'] == chosen)
                verified = (bool(lineup) and best is not None and best >= OVERLAP
                            and len(winners) == 1 and winners[0]['standing'] == chosen_row['standing'])
                if not verified:
                    out['problems'].append(
                        '%s: repeated label %r resolved to a roster the stored lineup does not '
                        'uniquely select (overlaps %r, chosen standing %d)'
                        % (m['id'], confirm['team'], scored, chosen_row['standing']))
                record.setdefault('duplicate_labels', []).append(
                    {'team': confirm['team'], 'lineup': lineup, 'overlap_by_row': scored,
                     'chosen_points': chosen, 'chosen_standing': chosen_row['standing'],
                     'roster_rule_verified': verified,
                     'rows': [{'standing': h['standing'], 'points': h['points'], 'roster': h['roster']}
                              for h in confirm['listed_rows']]})
        out['rows'].append(record)
    out['summary'] = {'model_rows': len(out['rows']),
                      'reproduced': sum(1 for r in out['rows'] if r['reproduces']),
                      'problems': len(out['problems'])}
    (HERE / 'model-receipt.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out['summary']))
    for problem in out['problems']:
        print('PROBLEM', problem)
    return 0 if not out['problems'] else 1


if __name__ == '__main__':
    sys.exit(main())
