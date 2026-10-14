"""Independent read-only audit; does not import or change the collector.

Usage: python verification-c6/audit_snapshot.py path/to/latest.json --output report.md
Checks retained evidence and arithmetic, not live external-source availability.
"""
import argparse
import hashlib
import json
import math
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
    return ''.join(c for c in unicodedata.normalize('NFKC', value).casefold() if c.isalnum())


def array(value):
    return json.loads(value) if isinstance(value, str) else value


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
            if p is None:
                require(m['pick'] is None and m['fair_odds'] is None and m['method'] is None, 'Unverified row has a derived value')
                require(bool(m['reason']), 'Unresolved/non-open row lacks explanation')
            else:
                require(m['state'] == 'open', 'Non-open row has actionable probability')
                require(date(m['lock']) > captured and date(m['start']) > captured, 'Pick already locked at generation')
                require(len(p) == 2 and all(math.isfinite(x) and 0 < x < 1 for x in p), 'Invalid probability')
                require(abs(sum(p) - 1) < 1e-10, 'Probabilities do not sum to one')
                require(len(m['evidence']) == 1, 'Expected one selected independently verified source')
                q = m['evidence'][0]
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
                    require(0 < bid <= ask < 1 and ask-bid <= Decimal('.25'), 'Exchange spread gate failed')
                    require(Decimal(str(line['liquidity'])) >= 100, 'Exchange liquidity gate failed')
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
    raise SystemExit(bool(errors))
