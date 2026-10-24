"""Read-only, clock-aware coverage accounting; never creates or changes a pick.

This contract checks accounting and provenance shape, NOT source truth or forecast
accuracy. Run verification-c6/audit_snapshot.py as well to replay the underlying
price/identity evidence. Unresolved rows with linked limitations are a valid
outcome; silently omitted rows and unsupported probabilities are not.
"""
import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
from urllib.parse import urlsplit

from scripts.core import dt, iso

TTL = timedelta(hours=8)
MARKET = {'exchange', 'exchange_wide', 'bookmaker_fallback'}
MODEL = {'model_vrs', 'model_vrs_mirror'}
RESEARCH = {'research_rank', 'research_rank_single', 'research_vrs_single', 'research_form'}


def https_url(value):
    try:
        parsed = urlsplit(value)
        return parsed.scheme == 'https' and bool(parsed.hostname) and not parsed.username
    except (TypeError, ValueError):
        return False


def hotspawn_url(value):
    return https_url(value) and urlsplit(value).hostname in {
        'play.hotspawn.com', 'www.hotspawn.com', 'hotspawn.com',
        'phpstack-1372681-6459848.cloudwaysapps.com'}


def timestamp(value):
    try:
        return dt(value)
    except (ValueError, TypeError, OverflowError, OSError):
        return None


def research_sources(match):
    """Only research context, never a failed bookmaker attempt, supports a pick."""
    contexts = [match.get('hltv_context') or {}, match.get('vrs_research') or {}]
    contexts.extend((match.get('hltv_team_pages') or {}).get('teams') or [])
    return sorted({c.get('source') or c.get('url') for c in contexts
                   if https_url(c.get('source') or c.get('url'))})


def inspect(snapshot, now=None):
    now = dt(now) if now is not None else datetime.now(timezone.utc)
    problems, rows, seen = [], [], set()
    observed = timestamp(snapshot.get('fixtures_observed_at'))
    inventory_fresh = observed is not None and -timedelta(minutes=5) <= now - observed < TTL
    matches = snapshot.get('matches')
    if not isinstance(matches, list):
        raise ValueError('Snapshot matches must be an array, never an inferred empty list')
    for match in matches:
        ident = str(match.get('id') or '')
        errors = []
        if not ident or ident in seen:
            errors.append('Missing or duplicate fixture ID')
        seen.add(ident)
        if not hotspawn_url(match.get('source_url')) or not hotspawn_url(match.get('feed_url')):
            errors.append('Fixture lacks an official Hotspawn source link')
        teams = match.get('teams')
        valid_teams = (isinstance(teams, list) and len(teams) == 2
                       and all(isinstance(t, str) and t.strip() for t in teams)
                       and teams[0] != teams[1])
        if not valid_teams:
            errors.append('Two distinct named teams are required')
        start, lock = timestamp(match.get('start')), timestamp(match.get('lock'))
        declared_open = match.get('state') == 'open'
        if declared_open and (start is None or lock is None):
            errors.append('Open fixture lacks a timezone-aware start or lock')
        open_now = declared_open and start is not None and lock is not None and min(start, lock) > now
        method, pick, p = match.get('method'), match.get('pick'), match.get('probabilities')
        deadlines = [value for value in (start, lock, observed + TTL if observed else None) if value]
        category = 'not_open'
        sources = []
        if declared_open:
            if pick and (not valid_teams or pick not in teams):
                errors.append('Pick is not one of the sourced fixture teams')
            if match.get('resolution_blocked') and (pick or p is not None):
                errors.append('Conflicting or unverified fixture membership cannot supply a recommendation')
            if p is not None:
                category = 'model' if method in MODEL else 'market'
                if method not in MARKET | MODEL:
                    errors.append('Numeric probability has no recognized market/model method')
                valid_p = (isinstance(p, list) and len(p) == 2
                           and all(type(v) in (int, float) and math.isfinite(v) and 0 < v < 1 for v in p)
                           and abs(sum(p) - 1) < 1e-8)
                if not valid_p:
                    errors.append('Probabilities must be two finite, normalized numbers strictly between zero and one')
                elif abs(p[0] - p[1]) >= .0001:
                    if valid_teams and pick != teams[0 if p[0] > p[1] else 1]:
                        errors.append('Directional pick does not match the higher probability')
                elif pick is not None or not match.get('reason'):
                    errors.append('An equal line needs a no-directional-edge limitation and no pick')
                else:
                    # Verified probabilities do not make a pick actionable when
                    # neither side is larger. Count this as an explicitly
                    # explained unresolved pick, not as a market recommendation.
                    category = 'unresolved'
                evidence = match.get('evidence') or []
                if not evidence:
                    errors.append('Numeric probability has no accepted evidence')
                for quote in evidence:
                    source = quote.get('url') or quote.get('api_url')
                    if not https_url(source) or hotspawn_url(source):
                        errors.append('Probability must originate outside Hotspawn with an HTTPS source')
                    else:
                        sources.append(source)
                    quote_observed = timestamp(quote.get('observed_at'))
                    if not quote_observed:
                        errors.append('Accepted evidence lacks a timezone-aware observation time')
                    else:
                        deadlines.append(quote_observed + TTL)
                        if quote_observed - now > timedelta(minutes=5):
                            errors.append('Accepted evidence observation is implausibly in the future')
                    if quote.get('updated_at'):
                        updated = timestamp(quote['updated_at'])
                        if updated:
                            deadlines.append(updated + TTL)
                        else:
                            errors.append('Accepted evidence has an invalid update timestamp')
                    if quote.get('provider') == 'Pinnacle':
                        cutoff = timestamp(((quote.get('raw') or {}).get('line') or {}).get('cutoffAt'))
                        if cutoff:
                            deadlines.append(cutoff)
                        else:
                            errors.append('Pinnacle evidence lacks a valid market cutoff')
                if not timestamp(match.get('expires_at')):
                    errors.append('Numeric probability lacks an explicit expiry')
            elif pick:
                category = 'research_only'
                sources = research_sources(match)
                if method not in RESEARCH or not sources or any(hotspawn_url(url) for url in sources):
                    errors.append('Research pick lacks a recognized tier or external supporting context source')
                contexts = [match.get('hltv_context') or {}, match.get('vrs_research') or {}]
                contexts.extend((match.get('hltv_team_pages') or {}).get('teams') or [])
                for context in contexts:
                    if not (context.get('source') or context.get('url')):
                        continue
                    context_observed = timestamp(context.get('observed_at'))
                    if context_observed is None:
                        errors.append('Research context lacks a timezone-aware observation time')
                    else:
                        deadlines.append(context_observed + TTL)
                        if context_observed - now > timedelta(minutes=5):
                            errors.append('Research context observation is implausibly in the future')
                if match.get('fair_odds') is not None:
                    errors.append('Research-only picks cannot publish numerical fair odds')
            else:
                category = 'unresolved'
            if p is None:
                attempts = match.get('attempts') or []
                if not isinstance(match.get('reason'), str) or not match['reason'].strip():
                    errors.append('Unpriced fixture lacks an explicit limitation')
                if not any(https_url(a.get('url')) and a.get('reason') for a in attempts):
                    errors.append('Unpriced fixture lacks a linked research-attempt explanation')
        expiry = timestamp(match.get('expires_at'))
        if expiry:
            deadlines.append(expiry)
        effective_expiry = min(deadlines) if deadlines else None
        actionable = open_now and inventory_fresh and not errors and category in {'market', 'model', 'research_only'}
        if p is not None or pick:
            actionable = actionable and effective_expiry is not None and effective_expiry > now
        if not open_now:
            category = 'not_open'
        elif not inventory_fresh or ((p is not None or pick) and (effective_expiry is None or effective_expiry <= now)):
            category = 'expired'
        rows.append({'id': ident, 'teams': teams, 'start': match.get('start'),
                     'lock': match.get('lock'), 'category': category, 'actionable': bool(actionable),
                     'pick': pick if actionable else None, 'method': method,
                     'effective_expiry': iso(effective_expiry) if effective_expiry else None,
                     'source_url': match.get('source_url'), 'research_sources': sources,
                     'limitation': match.get('reason'), 'evidence_url': 'evidence.html#match-' + ident,
                     'problems': errors})
        problems.extend(ident + ': ' + error for error in errors)
    counts = Counter(row['category'] for row in rows)
    return {'audit_at': iso(now), 'snapshot_generated_at': snapshot.get('generated_at'),
            'fixtures_observed_at': snapshot.get('fixtures_observed_at'),
            'inventory_fresh': inventory_fresh, 'inventory_coverage': snapshot.get('coverage'),
            'scope': 'Coverage accounting only; source truth and arithmetic require the independent row auditor.',
            'counts': {'total': len(rows), 'open_now': sum(r['category'] != 'not_open' for r in rows),
                       **{k: counts[k] for k in ('market', 'model', 'research_only', 'unresolved', 'expired', 'not_open')},
                       'actionable': sum(r['actionable'] for r in rows)},
            'problems': problems, 'rows': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='data/latest.json')
    parser.add_argument('--output', default='runtime/coverage-contract.json')
    parser.add_argument('--at', help='Explicit UTC audit clock for reproducible historical audits')
    parser.add_argument('--require-fresh', action='store_true')
    args = parser.parse_args()
    report = inspect(json.loads(Path(args.snapshot).read_text()), args.at)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    print(json.dumps({k: report[k] for k in ('audit_at', 'inventory_fresh', 'counts', 'problems')}))
    if report['problems'] or (args.require_fresh and (
            not report['inventory_fresh'] or report['inventory_coverage'] != 'verified')):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
