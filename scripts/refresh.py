"""Public read-only refresh. Source failures are data, never synthetic probabilities."""
import argparse
import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlencode,urlsplit
import requests
from bs4 import BeautifulSoup
from scripts.core import (HOTSPAWN,FIXTURES,PIN,GAMMA,dt,iso,fresh,hotspawn_state,
    normalize_fixtures,polymarket_candidates,pinnacle_candidates,resolve,record_polymarket_exclusions)


# Measured, not assumed (research/harvest-3c8d1136/cdn-probe.json, run 38869016384,
# 2026-10-16T07:43:47Z-07:44:06Z): Hotspawn's two public HTML lobby views are served
# through a CDN that answered the plain URLs with `Age: 973` and `Age: 7620`
# (`X-Cache: HIT`), while the *same* public URLs with one distinct query argument
# answered `Age: 0`, `X-Cache: MISS` and 103 CS2 fixtures instead of 95 - identical to
# the fixtures API read in the same minute. The fixtures API itself answers with no
# `Age` header but rejects an unknown query argument with HTTP 400, so it is never
# cache-busted. This matters because `Sources.get` derives
# `observed_at = retrieved_at - Age` and `inventory.discover` anchors the whole board at
# `min(observed_at)`: one cached HTML copy moved every open pick's deadline hours into
# the past (11:23:45Z on the 07:21Z build, 13:36:55Z on the 07:44Z build) and reported
# `coverage: partial` while the fresh API and the fresh page already agreed.
CACHE_BUST_HTML_HOSTS = ('play.hotspawn.com',)
CACHE_BUST_ARGUMENT = '_cb'

# Measured, not assumed. On the 2026-10-16T23:53:53Z harvest (run 38983767301,
# research/harvest-498cc7dd/probe-report.json) `https://www.hltv.org/matches` answered
# HTTP 403 to this project's own User-Agent while every other source in the same run
# answered 200, and the identical HLTV read at 19:57Z the same evening had answered
# 200 (research/harvest-621776e4/hltv-unpriced-*.json, sha256 recorded). One 403 was
# enough to block the host for the rest of that run, so all eight open fixtures that
# depended on HLTV lost their roster lineups (which disambiguate repeated Valve
# standings labels) and their ranking-order fallback: the board dropped from
# "every open row has a pick" to eight rows with no pick at all.
#
# A rate-limited 403/429 is a request to slow down, not a refusal to serve this
# project, so the correct response is to wait and ask again -- same URL, same
# headers, nothing rewritten, signed, spoofed or bypassed. `Retry-After` is honoured
# when the server sends it. Every attempt stays in the evidence log, and a host that
# keeps refusing is still blocked so a genuinely closed source is never hammered.
RATE_LIMIT_STATUSES = (403, 429)
RATE_LIMIT_BACKOFF = (10.0, 30.0, 60.0)
RATE_LIMIT_BACKOFF_CAP = 120.0


class RateLimited(Exception):
    """The server asked us to slow down; the wait is the caller's decision."""

    def __init__(self, status, retry_after=None):
        super().__init__('HTTP %s rate limit' % status)
        self.status = status
        self.retry_after = retry_after


def cache_bust(url, token):
    """Return `url` with one distinct, clearly labelled argument appended.

    The public URL's own query is preserved verbatim; nothing is signed, bypassed or
    rewritten, and the canonical URL stays the one published as evidence.
    """
    parts = urlsplit(url)
    pairs = [pair.split('=', 1) for pair in parts.query.split('&') if pair]
    query = urlencode(pairs + [(CACHE_BUST_ARGUMENT, token)])
    return parts._replace(query=query).geturl()


class Sources:
    def __init__(self, now):
        self.now = now
        self.log = []
        self.blocked_hosts = {}
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Hotspawn-CS2-Research/1.0 (+https://github.com/buffedlizard55-lab/MaltaProj4)'
        # Instance attribute so tests can shorten it; production uses the measured
        # backoff above and never a zero wait.
        self.rate_limit_backoff = RATE_LIMIT_BACKOFF

    def bustable(self, url, as_json):
        """Only the measured CDN-cached HTML views are cache-busted, never a JSON API."""
        return not as_json and urlsplit(url).netloc in CACHE_BUST_HTML_HOSTS

    def get(self, name, url, as_json=True, headers=None):
        """One source read, with a bounded, logged wait on a rate-limit response.

        A 403/429 is retried on the *same* URL with the *same* headers after a
        published wait; nothing about the request is altered to slip past the
        limit. When the limit persists, the host is blocked exactly as before and
        every attempt stays in ``self.log`` as evidence.
        """
        record = {'name':name, 'url':url, 'checked_at':iso(datetime.now(timezone.utc))}
        self.log.append(record)
        host=urlsplit(url).netloc
        if host in self.blocked_hosts:
            record.update(status='error',error='Skipped after earlier access/rate restriction on this host: '+self.blocked_hosts[host])
            raise ValueError(record['error'])
        backoff = list(self.rate_limit_backoff)
        waits = []
        for round_index in range(len(backoff) + 1):
            try:
                return self._read(record, url, as_json, headers)
            except RateLimited as e:
                if round_index >= len(backoff):
                    # The source refused repeatedly: block it, as a denied source
                    # always was, and say exactly how many waits preceded that.
                    self.blocked_hosts[host] = str(e.status)
                    record.update(status='error',
                        error='HTTP %s persisted after %d rate-limit waits (%s); host blocked for this run.' % (
                            e.status, len(waits), ', '.join('%gs' % w['waited_seconds'] for w in waits) or 'no wait completed'))
                    record['rate_limit_waits'] = waits
                    raise ValueError(record['error']) from e
                wait = e.retry_after if e.retry_after is not None else backoff[round_index]
                wait = min(max(float(wait), 0.0), RATE_LIMIT_BACKOFF_CAP)
                waits.append({'round':round_index + 1, 'http_status':e.status,
                    'retry_after_header':e.retry_after, 'waited_seconds':wait})
                record['rate_limit_waits'] = waits
                time.sleep(wait)
        raise ValueError('Unreachable rate-limit handling for ' + url)

    def _read(self, record, url, as_json, headers):
        bustable = self.bustable(url, as_json)
        host = urlsplit(url).netloc
        for attempt in range(2):
            # Attempt 0 asks the CDN for a current copy; the retry falls back to the
            # canonical URL, so a source that rejects the extra argument (as the fixtures
            # API does with HTTP 400) is still read exactly as before.
            token = '%d-%s' % (int(time.time() * 1000), uuid.uuid4().hex[:8]) if bustable and attempt == 0 else None
            target = cache_bust(url, token) if token else url
            record['request_url'] = target
            record['cache_bust'] = token
            try:
                r = self.session.get(target, timeout=(10,30), headers=headers)
                record['http_status'] = r.status_code
                r.raise_for_status()
                age_header = r.headers.get('Age')
                age = max(0, int(age_header)) if age_header is not None else None
                cache_status = r.headers.get('X-Cache') or r.headers.get('CF-Cache-Status')
                retrieved = datetime.now(timezone.utc)
                observed = retrieved - timedelta(seconds=age or 0)
                record.pop('error', None)
                record.update(status='ok', retrieved_at=iso(retrieved), observed_at=iso(observed), cache_age_seconds=age,
                    cache_status=cache_status,
                    sha256=hashlib.sha256(r.content).hexdigest(), bytes=len(r.content))
                if not fresh(observed, retrieved):
                    raise ValueError('Source HTTP cache is over eight hours old')
                archive = Path('runtime/sources')
                archive.mkdir(parents=True, exist_ok=True)
                (archive / (record['sha256'] + ('.json' if as_json else '.html'))).write_bytes(r.content)
                body = r.json() if as_json else r.text
                if not as_json and any(x in body.lower() for x in ['not accepting visitors from your region', 'just a moment...', 'access denied']):
                    raise ValueError('Access restriction or challenge page; not usable evidence')
                return body, record
            except requests.RequestException as e:
                status = getattr(getattr(e, 'response', None), 'status_code', None)
                record.update(status='error', error=str(e)[:250], http_status=status)
                retry_after = self._retry_after(getattr(e, 'response', None))
                if status in RATE_LIMIT_STATUSES:
                    # Asked to slow down: let the caller wait and ask again.
                    raise RateLimited(status, retry_after) from e
                # Never bypass access restrictions or repeatedly hit denied sources.
                if status == 401:
                    self.blocked_hosts[host] = str(status)
                if status in (401,403,404,429) or attempt == 1:
                    raise ValueError(record['error']) from e
                time.sleep(2)
            except ValueError as e:
                # A 200 response that is not usable evidence (stale CDN copy, or a
                # region/challenge page). Unchanged from before: one retry on the
                # canonical URL, then a hard failure. This is deliberately *not*
                # treated as a rate limit, so a closed source is never retried as
                # though it had merely asked us to slow down.
                record.update(status='error', error=str(e)[:250])
                if attempt == 1:
                    raise
                time.sleep(2)

    @staticmethod
    def _retry_after(response):
        """Integer seconds from a Retry-After header, or None (HTTP dates ignored)."""
        if response is None:
            return None
        raw = response.headers.get('Retry-After') if hasattr(response, 'headers') else None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None


def issue(code, message, source):
    return {'code':code, 'message':message, 'source':source}


def run(previous=None):
    now = datetime.now(timezone.utc)
    src = Sources(now)
    from scripts.inventory import discover
    inventory = discover(src, now, previous)
    if 'retained' in inventory:
        return inventory['retained']
    flags, matches = inventory['flags'], inventory['matches']
    raw, fixture_observed = inventory['raw'], inventory['observed_at']
    coverage = inventory['coverage']
    open_matches = [m for m in matches if m['state']=='open' and not m.get('resolution_blocked')]
    exchange_events = None
    try:
        sports, _ = src.get('Polymarket sports registry',GAMMA+'/sports')
        cs2 = [s for s in sports if s.get('sport')=='cs2']
        if len(cs2)!=1:
            raise ValueError('CS2 registry is ambiguous or absent')
        events, seen_ids, excluded_batches = [], set(), []
        for offset in range(0,5000,100):
            params = urlencode({'series_id':cs2[0]['series'],'active':'true','closed':'false',
                'end_date_min': now.strftime('%Y-%m-%dT00:00:00Z'), 'limit':100,'offset':offset, 'order':'id','ascending':'true'})
            batch, receipt = src.get(f'Polymarket events page {offset//100+1}',GAMMA+'/events?'+params)
            if not isinstance(batch,list):
                raise ValueError('Unexpected Polymarket pagination schema')
            ids = {str(e['id']) for e in batch}
            if ids & seen_ids:
                raise ValueError('Repeated exchange event page; coverage unverified')
            seen_ids |= ids
            excluded_batches.append((batch, receipt.copy()))
            candidates = polymarket_candidates(batch,receipt['observed_at'])
            for candidate in candidates:
                candidate['source_receipts'] = [receipt.copy()]
            events.extend(candidates)
            if len(batch)<100:
                break
        else:
            raise ValueError('Exchange pagination safety cap reached')
        for m in open_matches:
            resolve(m,events,'Polymarket',datetime.now(timezone.utc))
        for batch, receipt in excluded_batches:
            record_polymarket_exclusions(open_matches, batch, receipt['observed_at'], receipt)
        exchange_events = events
    except (ValueError,KeyError,TypeError) as e:
        flags.append(issue('exchange',str(e),GAMMA+'/sports'))
        for m in open_matches:
            m['attempts'].append({'provider':'Polymarket','status':'error','reason':str(e),'url':GAMMA+'/sports'})

    unresolved = [m for m in open_matches if m['probabilities'] is None]
    if unresolved:
        # HLTV first: exact fixture identity, rankings and lineups (context only).
        from scripts.hltv import research
        research(unresolved,src)
        # A sharp bookmaker line outranks a wide exchange quote.
        try:
            matchups, mr = src.get('Pinnacle esports fixtures',PIN+'/sports/12/matchups?withSpecials=false')
            lines, lr = src.get('Pinnacle esports moneylines',PIN+'/sports/12/markets/straight')
            observed = min(mr['observed_at'],lr['observed_at'],key=dt)
            candidates = pinnacle_candidates(matchups,lines,observed)
            for candidate in candidates:
                candidate['source_receipts'] = [mr.copy(),lr.copy()]
            for m in unresolved:
                resolve(m,candidates,'Pinnacle',datetime.now(timezone.utc))
        except (ValueError,KeyError,TypeError) as e:
            flags.append(issue('pinnacle',str(e),PIN+'/sports/12/markets/straight'))
            for m in unresolved:
                m['attempts'].append({'provider':'Pinnacle','status':'error','reason':str(e),'url':PIN+'/sports/12/markets/straight'})
        # Documented low-confidence tier: a wide but genuinely two-sided, funded,
        # fresh, open exchange quote, with its real spread published. Liquidity
        # below $100 stays rejected.
        if exchange_events is not None:
            for m in [m for m in unresolved if m['probabilities'] is None]:
                resolve(m,exchange_events,'Polymarket',datetime.now(timezone.utc),relax=True)
        unresolved = [m for m in unresolved if m['probabilities'] is None]
        for provider,url in [('Thunderpick','https://thunderpick.io/esports/cs2-betting'),('GG.BET','https://gg.bet/en/esports/counter-strike')]:
            if not unresolved:
                break
            try:
                _, _ = src.get(provider+' fallback access',url,False)
                status, reason = 'unresolved','Access succeeded but no validated automated two-sided series quote was extracted. HTML/JavaScript rendering or an unavailable adapter is a collection limitation, not evidence that the bookmaker offers no odds.'
            except ValueError as e:
                status, reason = 'error',str(e)
            for m in unresolved:
                m['attempts'].append({'provider':provider,'status':status,'reason':reason,'url':url})
    # Researched book-listing lines: a dated, identity-verified two-way line
    # read from a book's own listing page is an external price, so it outranks
    # our own originated model line. It runs after the automated exchange and
    # bookmaker tiers and before the model, and every line it publishes carries
    # the research flag and the observation time.
    from scripts.core import book_research_pick
    for m in open_matches:
        if m['probabilities'] is None:
            book_research_pick(m, now=now)
    # Originated lines: Valve's official standings points and Valve's own
    # published expected-win formula and calibration. Used only where no market
    # line passed its gates; shown beside market lines for comparison.
    from scripts import vrs
    standings, vrs_meta, vrs_problem = vrs.fetch(src, datetime.now(timezone.utc), os.environ.get('GITHUB_TOKEN'))
    if vrs_problem:
        flags.append(issue('vrs',vrs_problem,vrs.BLOB.rsplit('/blob',1)[0]))
    if standings:
        for m in open_matches:
            lineups = {x['team']:x['players'] for x in (m.get('hltv_context') or {}).get('lineups',[])}
            if m['probabilities'] is None:
                vrs.apply(m,standings,vrs_meta,lineups)
            else:
                vrs.compare(m,standings,vrs_meta,lineups)
    # Final research tier: a sourced pick from verified HLTV fixture identity
    # and ranking order, with no probability. Anything left stays unresolved.
    from scripts.core import research_rank_pick
    for m in matches:
        if m['state']=='open' and m['probabilities'] is None:
            research_rank_pick(m)
    completed = datetime.now(timezone.utc)
    for m in matches:
        if any(m.get(field) and dt(m[field]) <= completed for field in ('lock','start')):
            m['state']='not_open'
            m['probabilities']=m['fair_odds']=m['pick']=m['method']=None
        if m['state']!='open':
            m['reason']='Not open for picks according to sourced lock/start/end fields; retained for complete feed visibility.'
        elif m['probabilities'] is None and not m.get('resolution_blocked') and not m.get('pick'):
            problems = [a['reason'] for a in m['attempts'] if a['provider']=='Polymarket']
            m['reason']=(problems[0] if problems else 'Primary market evidence unavailable.')+' HLTV / esportsbook fallbacks, the Valve VRS model and one-sided Valve standings evidence did not establish a verified line, a two-team ranking pair, or single-team ranking evidence.'
    stale_count = sum(m['state']!='open' for m in matches)
    if stale_count:
        flags.append(issue('feed_status',f'{stale_count} feed entries are not open by sourced timestamps/status. They remain in All matches and are not treated as future picks.',FIXTURES))
    return {'schema_version':2,'generated_at':iso(completed),'last_attempt_at':iso(completed),
        'refresh_started_at':iso(now),
        'fixtures_observed_at':fixture_observed, 'coverage':coverage,
        'refresh_hours':1,'stale_after_hours':8, 'matches':matches,
        'source_checks':src.log,'issues':flags,
        'coverage_counts':inventory['counts'], 'fixture_conflicts':inventory['conflicts'],
        'inventory_changes':inventory['changes'],
        'fixture_evidence':[{k:v for k,v in x.items() if 'picked' not in k and k!='total_picks'} for x in raw if x.get('sport_alias')=='cs2']}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='runtime/latest.json')
    parser.add_argument('--previous',default='data/latest.json')
    args=parser.parse_args()
    previous_path = Path(args.output) if Path(args.output).exists() else Path(args.previous)
    previous=json.loads(previous_path.read_text()) if previous_path.exists() else None
    data=run(previous)
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+'\n');os.replace(tmp,path)
    print(json.dumps({'coverage':data['coverage'],'matches':len(data['matches']),
        'priced':sum(m['probabilities'] is not None for m in data['matches']),
        'research_only':sum(m['state']=='open' and m['probabilities'] is None and bool(m.get('pick')) for m in data['matches']),
        'unresolved_without_any_pick':sum(m['state']=='open' and m['probabilities'] is None and not m.get('pick') for m in data['matches'])}))

if __name__=='__main__':
    main()
