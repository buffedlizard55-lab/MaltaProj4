"""Read-only independent audit of retained source evidence (Python standard library).

Usage: python audit_snapshot.py /path/to/implementation > snapshot-audit.json
This does NOT fetch live sources or certify true winning probabilities. It uses
an independently retained official response, not the production normalizer.
"""
import hashlib
import json
import sys
import unicodedata
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path


def norm(value):
    return ''.join(c for c in unicodedata.normalize('NFKC', value).casefold() if c.isalnum())


def utc_ms(value):
    return datetime.fromtimestamp(int(value) / 1000, timezone.utc) if value else None


def utc_iso(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')) if value else None


def run(root):
    source_file = root / 'research/probe/fixtures.txt'
    raw_bytes = source_file.read_bytes()
    original = json.loads(raw_bytes)
    originals = {str(r['id']): r for r in original if r['sport_alias'] == 'cs2'}
    assert len(originals) == len([r for r in original if r['sport_alias'] == 'cs2']), 'Duplicate source IDs'
    data = json.loads((root / 'data/latest.json').read_text())
    register = json.loads((root / 'data/identities.json').read_text())['aliases']
    alias = {norm(n): norm(r['canonical']) for r in register for n in r['names']}
    def key(name):
        name = norm(name)
        return alias.get(name, name)
    assert {m['id'] for m in data['matches']} == set(originals), 'Source ID set differs'
    assert len(data['matches']) == len(originals), 'Output contains duplicates'
    rows = []
    for m in data['matches']:
        source = originals[m['id']]
        assert m['teams'] == [source['participants0_name'], source['participants1_name']]
        assert m['team_ids'] == [source['participants0_id'], source['participants1_id']]
        for field, raw in [('competition','competition_name'),('tier','tier'),('best_of','best_of'),('source_status','status')]:
            assert m[field] == source[raw], (m['id'], field)
        assert utc_iso(m['start']) == utc_ms(source['scheduled_start_time']), m['id']
        assert utc_iso(m['lock']) == utc_ms(source['lock_time']), m['id']
        assert m['source_url'].startswith(('https://play.hotspawn.com/', 'https://www.hotspawn.com/'))
        row = {'id':m['id'], 'teams':m['teams'], 'hotspawn_source':m['source_url'],
               'original_fields':'match retained primary response',
               'probability_check': 'blank / unverified', 'external_source':None}
        if m['probabilities'] is None:
            assert m['pick'] is None and m['fair_odds'] is None
            rows.append(row)
            continue
        assert source['status'] == 'scheduled' and not source.get('end_time')
        assert utc_iso(m['lock']) > utc_iso(data['generated_at'])
        assert utc_iso(m['start']) > utc_iso(data['generated_at'])
        q = m['evidence'][0]
        for stamp in (data['fixtures_observed_at'], q['observed_at']):
            assert -300 <= (utc_iso(data['generated_at']) - utc_iso(stamp)).total_seconds() <= 8*3600
        if q['provider'] == 'Polymarket':
            r = q['raw']
            names = json.loads(r['outcomes']) if isinstance(r['outcomes'],str) else r['outcomes']
            raw_values = json.loads(r['outcomePrices']) if isinstance(r['outcomePrices'],str) else r['outcomePrices']
            values = list(map(Decimal, map(str, raw_values)))
            for i, name in enumerate(names):
                matching = [t for t in q.get('team_metadata',[]) if t.get('name') == name]
                abbreviations = [t.get('abbreviation') for t in matching if t.get('abbreviation')]
                for target in m['teams']:
                    if key(target) in [key(a) for a in abbreviations]:
                        names[i] = target
            assert utc_iso(r.get('gameStartTime') or r.get('eventStartTime')) == utc_iso(m['start'])
            assert r['sportsMarketType'] == 'moneyline'
            assert r['active'] and not r['closed'] and r['acceptingOrders']
            assert Decimal(str(r['liquidity'])).is_finite() and Decimal(str(r['liquidity'])) >= 100
            bid, ask = Decimal(str(r['bestBid'])), Decimal(str(r['bestAsk']))
            assert 0 < bid <= ask < 1 and ask - bid <= Decimal('.25')
            for stamp in (q['observed_at'], r['updatedAt']):
                age = (utc_iso(data['generated_at']) - utc_iso(stamp)).total_seconds()
                assert -300 <= age <= 8*3600
        elif q['provider'] == 'Pinnacle':
            r = q['raw']; match = r['matchup']; line = r['line']
            people = {p['alignment']:p['name'] for p in match['participants']}
            names = [people['home'], people['away']]
            raw_prices = {p['designation']:Decimal(str(p['price'])) for p in line['prices']}
            values=[]
            for side in ('home','away'):
                american = raw_prices[side]
                decimal = 1 + (american/100 if american>0 else 100/-american)
                values.append(1/decimal)
            assert line['type']=='moneyline' and line['period']==0 and line['status']=='open'
            assert line['matchupId']==match['id'] and match['status']=='pending' and not match['isLive']
            assert utc_iso(match['startTime']) == utc_iso(m['start'])
            assert utc_iso(line['cutoffAt']) > utc_iso(data['generated_at'])
        else:
            raise AssertionError('Unknown provider')
        assert len(names) == 2 and len(values) == 2
        assert len(set(map(key,names))) == 2
        assert set(map(key,names)) == set(map(key,m['teams'])), (m['id'],'raw identity')
        ordered = [values[list(map(key,names)).index(key(t))] for t in m['teams']]
        probabilities = [v/sum(ordered) for v in ordered]
        for i,p in enumerate(probabilities):
            assert p.is_finite() and 0<p<1
            assert abs(p - Decimal(str(m['probabilities'][i]))) < Decimal('1e-9')
            assert abs(1/p - Decimal(str(m['fair_odds'][i]))) < Decimal('1e-9')
        winner = None if abs(probabilities[0]-probabilities[1]) < Decimal('.0001') else m['teams'][0 if probabilities[0]>probabilities[1] else 1]
        assert winner == m['pick']
        row.update(probability_check='independently reproduced from retained raw price fields', external_source=q['api_url'])
        rows.append(row)
    return {'scope':'Historical retained-source audit; not a live data fetch or true-chance certification',
            'implementation':str(root), 'source_capture_sha256':hashlib.sha256(raw_bytes).hexdigest(),
            'snapshot_generated_at':data['generated_at'], 'row_count':len(rows),
            'priced_rows_recomputed':sum(r['external_source'] is not None for r in rows), 'rows':rows}


if __name__ == '__main__':
    print(json.dumps(run(Path(sys.argv[1])), indent=2, ensure_ascii=False))
