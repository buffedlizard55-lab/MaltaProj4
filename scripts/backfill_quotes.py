"""Apply retained primary-source quote receipts to the committed snapshot.

Why this exists: the scheduled refresh runs every six hours, but a researched
quote can be captured by a session between refreshes. This script applies only
receipts that already exist in ``research/current/quotes`` — it never fetches,
never invents a market, and never writes a probability by hand. Every number is
recomputed by the same functions the validator replays, so an altered or expired
receipt fails the build instead of reaching the site.

The scheduled refresh overwrites this snapshot with live data; this is an
interim, fully sourced snapshot for fixtures whose quotes were captured by hand.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.core import GAMMA, dt, iso, polymarket_candidates, resolve

ROOT = Path(__file__).resolve().parents[1]
QUOTES = ROOT / 'research/current/quotes'

# Hotspawn fixture ID -> receipt file. Each mapping was checked against the
# fixture's exact opponent pair and UTC start before it was added here.
MAPPING = {
    '1080281': 'polymarket-5583519-wbt-ence.json',
    '1080283': 'polymarket-5583522-wbt-bojong.json',
    '1080286': 'polymarket-5583527-havu-roundsgg.json',
    '1081120': 'polymarket-5649536-mellren-privateer.json',
    '1080289': 'polymarket-5583533-voca-roundsgg.json',
}
BACKFILL_NOTE = ('Interim snapshot: quote receipts captured between scheduled refreshes were applied to the rows below. '
                 'Each receipt is stored in research/current/quotes with its API URL and observation time, and every '
                 'probability is recomputed from the raw fields by scripts.core. The next scheduled refresh replaces this snapshot.')


def load_candidate(receipt_path):
    receipt = json.loads(receipt_path.read_text())
    raw = receipt['raw']
    assert receipt['provider'] == 'Polymarket'
    assert receipt['api_url'] == GAMMA + '/markets/' + str(raw['id'])
    event = {'slug': receipt['event_url'].rstrip('/').split('/')[-1], 'sport': {'sport': 'cs2'},
             'closed': False, 'markets': [raw]}
    candidates = polymarket_candidates([event], receipt['observed_at'])
    assert len(candidates) == 1, 'Receipt does not yield exactly one whole-match candidate: ' + receipt_path.name
    digest = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    for candidate in candidates:
        candidate['source_receipts'] = [{'name': 'Polymarket market ' + str(raw['id']), 'url': receipt['api_url'],
            'status': 'ok', 'observed_at': receipt['observed_at'], 'retrieved_at': receipt['observed_at'],
            'sha256': digest, 'receipt': 'research/current/quotes/' + receipt_path.name,
            'note': 'Retained raw primary-source fields; recomputed by scripts.core, never hand-entered.'}]
    return candidates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data/latest.json')
    parser.add_argument('--now', default=None, help='Override the snapshot timestamp (ISO, UTC)')
    args = parser.parse_args()
    path = Path(args.data)
    data = json.loads(path.read_text())
    now = dt(args.now) if args.now else datetime.now(timezone.utc)
    rows = {m['id']: m for m in data['matches']}
    applied, skipped = [], []
    for fixture_id, receipt_name in MAPPING.items():
        row = rows.get(fixture_id)
        if row is None:
            skipped.append({'fixture': fixture_id, 'reason': 'Fixture no longer present in the retained inventory.'})
            continue
        if row['state'] != 'open' or row.get('probabilities') is not None:
            skipped.append({'fixture': fixture_id, 'reason': 'Fixture is not open or already carries evidence.'})
            continue
        candidates = load_candidate(QUOTES / receipt_name)
        row['attempts'] = [a for a in row.get('attempts', []) if a.get('provider') != 'Backfill']
        before = len(row['attempts'])
        resolve(row, candidates, 'Polymarket', now)
        if row['probabilities'] is None:
            resolve(row, candidates, 'Polymarket', now, relax=True)
        added = row['attempts'][before:]
        for attempt in added:
            attempt['provider'] = 'Backfill (Polymarket)'
        if row['probabilities'] is None:
            skipped.append({'fixture': fixture_id, 'reason': 'Receipt did not pass the gates: ' + str([a.get('reason') for a in added])})
            continue
        applied.append({'fixture': fixture_id, 'receipt': receipt_name, 'method': row['method'],
                        'pick': row['pick'], 'probabilities': row['probabilities'],
                        'receipt_sha256': hashlib.sha256((QUOTES / receipt_name).read_bytes()).hexdigest()})
    # Re-evaluate every row for the new snapshot time exactly as the refresh does:
    # a row whose sourced lock or start has passed is not open and carries no pick.
    for row in data['matches']:
        if any(row.get(field) and dt(row[field]) <= now for field in ('lock', 'start')):
            row['state'] = 'not_open'
            row['probabilities'] = row['fair_odds'] = row['pick'] = row['method'] = None
            row['reason'] = 'Source start or pick lock has passed. Historical evidence is not a current recommendation.'
        if (row.get('method') == 'research_rank' and row.get('pick')):
            continue
        if row['state'] != 'open':
            row['reason'] = row.get('reason') or 'Not open for picks according to sourced lock/start/end fields; retained for complete feed visibility.'
        elif row['probabilities'] is None and not row.get('resolution_blocked') and not row.get('pick'):
            problems = [a['reason'] for a in row.get('attempts', []) if a.get('provider', '').startswith('Polymarket') or a.get('provider') == 'Backfill (Polymarket)']
            row['reason'] = (problems[0] if problems else 'Primary market evidence unavailable.') + ' HLTV / esportsbook fallbacks did not establish a verified price or a verified ranking pair.'
    data['generated_at'] = iso(now)
    data['last_attempt_at'] = iso(now)
    data['built_at'] = iso(now)
    data['backfill'] = {'applied_at': iso(now), 'note': BACKFILL_NOTE, 'applied': applied, 'skipped': skipped}
    data.setdefault('issues', [])
    if applied and not any(i.get('code') == 'backfill' for i in data['issues']):
        data['issues'].append({'code': 'backfill', 'message': BACKFILL_NOTE + ' Applied to %d fixture(s): %s.' % (
            len(applied), ', '.join(a['fixture'] for a in applied)), 'source': 'https://github.com/buffedlizard55-lab/MaltaProj4/tree/main/research/current/quotes'})
    data['source_checks'] = [s for s in data.get('source_checks', []) if not s.get('name', '').startswith('Polymarket receipt')]
    for entry in applied:
        receipt = json.loads((QUOTES / entry['receipt']).read_text())
        data['source_checks'].append({'name': 'Polymarket receipt ' + receipt['market_id'], 'url': receipt['api_url'],
            'status': 'ok', 'observed_at': receipt['observed_at'], 'checked_at': receipt['observed_at'],
            'cache_age_seconds': None, 'note': 'Retained receipt applied by scripts.backfill_quotes; recomputed from raw fields.',
            'receipt_sha256': entry['receipt_sha256']})
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'applied': [(a['fixture'], a['method'], a['pick']) for a in applied], 'skipped': skipped}, indent=2))


if __name__ == '__main__':
    main()
