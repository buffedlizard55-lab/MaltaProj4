"""Build the quote-availability dossier for every open fixture that carries a
pick but no published probability.

Session 76712ccc. Read-only with respect to everything outside
``research/quotes-76712ccc``: it reads the committed snapshot, the vendored
Valve standings and the retained raw receipts, recomputes every decision with
the same code the pipeline uses (``scripts.vrs``), and writes

    research/quotes-76712ccc/UNPRICED-FIXTURE-LINES.json
    research/quotes-76712ccc/UNPRICED-FIXTURE-LINES.md

No number is ever typed in by hand: a probability appears in the output only
when ``scripts.vrs.line`` originates it from the Valve standings plus the
captured HLTV lineup, and the reason a probability is missing is the exact
string the model returned.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import scripts.core  # noqa: F401  (import first: populates ALIAS_MAP from data/identities.json)
from scripts import vrs

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DATA = ROOT / 'data/latest.json'
VENDORED = ROOT / 'data/vrs/standings_global_2026_10_05.md'
VENDORED_META = ROOT / 'data/vrs/meta.json'
# Receipts retained by this session (raw bytes, hashed below).
RECEIPTS = {
    'valve-standings_global_2026_10_05.md': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/live/2026/standings_global_2026_10_05.md',
    'valve-standings_europe_2026_10_05.md': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/live/2026/standings_europe_2026_10_05.md',
    'valve-standings_asia_2026_10_05.md': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/live/2026/standings_asia_2026_10_05.md',
    'valve-standings_americas_2026_10_05.md': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/live/2026/standings_americas_2026_10_05.md',
}
# Raw market scans retained in this session's harvest directory, cited by hash.
MARKET_RECEIPTS = {
    'polymarket-cs2-scan.json': 'https://gamma-api.polymarket.com/events?closed=false&limit=100&offset=0',
    'pinnacle-sweep.json': 'https://guest.api.arcana.pinnacle.com/0.1/leagues',
    'pinnacle-league-moneylines.json': 'https://guest.api.arcana.pinnacle.com/0.1/leagues/230242/markets/straight',
    'book-probes.json': 'https://thunderpick.io/esports/cs2-betting',
    'hotspawn-fixtures.json': 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1',
}


def rel(path):
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def harvest_receipts():
    out = []
    base = ROOT / 'research/harvest-76712ccc'
    for name, url in MARKET_RECEIPTS.items():
        path = base / name
        if not path.exists():
            continue
        entry = {'file': 'research/harvest-76712ccc/' + name, 'url': url, 'sha256': sha256(path)}
        if name in ('polymarket-cs2-scan.json', 'pinnacle-sweep.json'):
            entry['observed_at'] = _observed(json.loads(path.read_text()))
        out.append(entry)
    return out


def _observed(payload):
    """Earliest of the scan's own observation stamps when it has no single one."""
    stamps = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == 'observed_at' and isinstance(value, str):
                    stamps.append(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    return min(stamps) if stamps else None


def valve_receipts():
    return [{'file': 'research/quotes-76712ccc/' + name, 'url': url, 'sha256': sha256(OUT / name)}
            for name, url in RECEIPTS.items()]


def load_standings():
    meta = json.loads(VENDORED_META.read_text())
    meta.update({'observed_at': meta.get('vendored_at'), 'origin': 'vendored snapshot (data/vrs)'})
    return vrs.parse(VENDORED.read_text()), meta


def lineups_of(row):
    return {x['team']: x['players'] for x in (row.get('hltv_context') or {}).get('lineups', [])}


def identity_report(row, standings, lineups):
    report = []
    for team in row['teams']:
        lineup = next((v for k, v in lineups.items() if k and vrs.norm(k) == vrs.norm(team)), None)
        entry, note = vrs.identify(team, standings, lineup)
        item = {'label': team, 'lineup': lineup, 'note': note}
        if entry is None:
            item['status'] = 'absent'
        else:
            item.update(status='resolved', vrs_name=entry['name'], standing=entry['standing'],
                        points=entry['points'], overlap=entry['roster_overlap'], roster=entry['roster'])
        report.append(item)
    return report


def regional_absence(team):
    """Which official Valve lists (2026-10-05) carry this label, raw-file only."""
    hits = []
    for name in RECEIPTS:
        path = OUT / name
        for line in path.read_text().splitlines():
            m = vrs.ROW_RE.match(line)
            if m and vrs.norm(m.group(3)) == vrs.norm(team):
                hits.append({'file': name, 'standing': int(m.group(1)), 'points': int(m.group(2)),
                             'roster': m.group(4).strip()})
    return hits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default=str(DATA))
    parser.add_argument('--observed-at', default=None)
    args = parser.parse_args()
    observed_at = args.observed_at or datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    snapshot = json.loads(Path(args.data).read_text())
    standings, meta = load_standings()

    rows = []
    for row in snapshot['matches']:
        if row.get('state') != 'open' or row.get('pick') is None:
            continue
        if row.get('probabilities') is not None and row.get('method') != 'research_rank' \
                and not str(row.get('method') or '').startswith('research'):
            continue
        lineups = lineups_of(row)
        quote, reason = vrs.line(row, standings, meta, lineups)
        context = row.get('hltv_context') or {}
        item = {
            'fixture_id': row['id'], 'teams': row['teams'], 'competition': row.get('competition'),
            'start': row.get('start'), 'tier': row.get('tier'), 'best_of': row.get('best_of'),
            'pick': row.get('pick'), 'pick_method': row.get('method'), 'flags': row.get('flags'),
            'hotspawn_source': row.get('source_url'),
            'hltv': {'url': context.get('source'), 'observed_at': context.get('observed_at'),
                     'ranks': context.get('ranks'), 'lineups': context.get('lineups'),
                     'limitation': context.get('limitation')},
            'market_absence': [{'provider': a['provider'], 'status': a['status'], 'reason': a['reason'],
                                'url': a['url']} for a in row.get('attempts', [])],
            'valve_identity': identity_report(row, standings, lineups),
            'valve_lists_checked': {team: regional_absence(team) for team in row['teams']},
        }
        if quote is None:
            item['decision'] = {'probability': None, 'method': None, 'blocker': reason}
        else:
            item['decision'] = {
                'probability': quote['probabilities'],
                'method': 'model_vrs',
                'vrs_teams': quote['vrs_teams'], 'points': quote['points'], 'standings': quote['standings'],
                'roster_checks': quote['roster_checks'], 'standings_as_of': quote['standings_as_of'],
                'source': quote['url'], 'formula_source': quote['formula_source'],
                'calibration_source': quote['calibration_source'],
                'note': 'Originated by scripts.vrs from the Valve standings plus the HLTV lineup. '
                        'Not a market price.',
            }
        rows.append(item)

    document = {
        'session': '76712ccc',
        'purpose': 'Per-fixture quote availability for every open pick with no published probability: '
                   'who was probed, what the raw receipts say, and the exact blocker.',
        'observed_at': observed_at,
        'snapshot': {'file': args.data if Path(args.data).is_absolute() else str(Path(args.data)),
                     'generated_at': snapshot.get('generated_at'), 'rows': len(snapshot['matches']),
                     'open': sum(1 for r in snapshot['matches'] if r.get('state') == 'open'),
                     'open_without_probability': sum(1 for r in snapshot['matches']
                                                     if r.get('state') == 'open' and r.get('probabilities') is None)},
        'policy': ['Hotspawn pick percentages are never used as a probability.',
                   'A probability exists only when a retained market receipt validates, or when scripts.vrs '
                   'originates a labelled model line from both teams\' Valve standings points plus the HLTV lineup.',
                   'A team that appears in no Valve list stays blank and is flagged, never estimated.'],
        'valve_receipts': valve_receipts(),
        'market_receipts': harvest_receipts(),
        'fixtures': rows,
    }
    (OUT / 'UNPRICED-FIXTURE-LINES.json').write_text(json.dumps(document, indent=1, sort_keys=False) + '\n')
    render_markdown(document)
    print('wrote UNPRICED-FIXTURE-LINES.json with %d fixtures' % len(rows))


def render_markdown(document):
    lines = [
        '# Quote availability for every pick without a published probability',
        '',
        'Built by `research/quotes-76712ccc/build_dossier.py` from the committed snapshot of %s. Every row below'
        % document['snapshot'].get('generated_at'),
        'is recomputed, not typed: the market column quotes the pipeline\'s own attempt records, the model column is',
        'the output of `scripts.vrs.line` over the vendored Valve standings of 2026-10-05 plus the HLTV lineup, and a',
        'blank model cell means that function returned no line (the reason is printed verbatim).',
        '',
        '| Fixture | Start (UTC) | Competition | Pick | Market probes | Model line |',
        '| --- | --- | --- | --- | --- | --- |',
    ]
    for row in document['fixtures']:
        probes = '; '.join('%s: %s' % (a['provider'], a['status']) for a in row['market_absence'])
        decision = row['decision']
        if decision['probability'] is None:
            model = 'blank — %s' % decision['blocker']
        else:
            model = '**%.2f%% / %.2f%%** (VRS model, %s)' % (decision['probability'][0] * 100,
                                                            decision['probability'][1] * 100,
                                                            ', '.join('%s #%d %d pts'
                                                                      % (n, s, p) for n, s, p
                                                                      in zip(decision['vrs_teams'],
                                                                             decision['standings'],
                                                                             decision['points'])))
        lines.append('| %s vs %s (`%s`) | %s | %s | %s | %s | %s |'
                     % (row['teams'][0], row['teams'][1], row['fixture_id'], row['start'],
                        row['competition'], row['pick'], probes, model))
    lines += ['', '## Per-fixture detail', '']
    for row in document['fixtures']:
        lines.append('### %s vs %s — Hotspawn fixture %s' % (row['teams'][0], row['teams'][1], row['fixture_id']))
        lines.append('')
        lines.append('- Competition / start: %s, %s%s.' % (row['competition'], row['start'],
                                                            '' if row['best_of'] in (None, 0) else ' (best of %s)' % row['best_of']))
        lines.append('- Pick published by the pipeline: **%s** (%s).' % (row['pick'], row['pick_method']))
        if row['hltv'].get('url'):
            lines.append('- Fixture identity: [HLTV match page](%s), captured %s.'
                         % (row['hltv']['url'], row['hltv'].get('observed_at')))
        for entry in row['valve_identity']:
            if entry['status'] == 'resolved':
                lines.append('- Valve standings: `%s` → **%s** #%d, %d points, %d of 5 lineup players matched'
                             ' (`%s`).' % (entry['label'], entry['vrs_name'], entry['standing'], entry['points'],
                                           entry['overlap'], ', '.join(entry['roster'])))
            else:
                hits = row['valve_lists_checked'].get(entry['label']) or []
                where = ('no list carries the label' if not hits else
                         'label rows: ' + '; '.join('%s #%d' % (h['file'].split('_')[1].split('.')[0], h['standing'])
                                                    for h in hits))
                lines.append('- Valve standings: `%s` — %s (%s).' % (entry['label'], entry['note'], where))
        for attempt in row['market_absence']:
            lines.append('- %s probe: *%s* — %s ([source](%s)).' % (attempt['provider'], attempt['status'],
                                                                   attempt['reason'], attempt['url']))
        decision = row['decision']
        if decision['probability'] is None:
            lines.append('- **Published probability: blank.** Blocker: %s' % decision['blocker'])
        else:
            lines.append('- **Published probability: %s %s and %s %s** from the labelled VRS model '
                         '(%s).' % (row['teams'][0], fmt(decision['probability'][0]), row['teams'][1],
                                    fmt(decision['probability'][1]), decision['note']))
            lines.append('- Roster continuity checks: %s.' % '; '.join(
                '`%s` lineup (%s) shares %s of 5 players with the standings roster' % (team, ', '.join(r['lineup'] or []), r['overlap'])
                for team, r in zip(decision['vrs_teams'], decision['roster_checks'])))
            lines.append('- Reproducible: the pipeline applies this same line automatically on its next run '
                         '(`scripts.vrs.apply`), so the unresolved `Valve VRS model` probe above is superseded here.')
        lines.append('')
    lines += ['## Retained receipts', '',
              '| File | SHA-256 | Source |', '| --- | --- | --- |']
    for receipt in document['valve_receipts'] + document['market_receipts']:
        lines.append('| `%s` | `%s` | %s |' % (receipt['file'], receipt['sha256'][:16], receipt['url']))
    lines += ['', '## Policy', ''] + ['- ' + p for p in document['policy']] + ['']
    (OUT / 'UNPRICED-FIXTURE-LINES.md').write_text('\n'.join(lines))


def fmt(value):
    return '%.2f%%' % (value * 100)


if __name__ == '__main__':
    main()
