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
    normalize_fixtures,polymarket_candidates,pinnacle_candidates,resolve,record_polymarket_exclusions,
    pick_deadline)

try:
    from curl_cffi import requests as _cffi_requests
except ImportError:  # optional runtime transport fallback for TLS-fingerprinted hosts
    _cffi_requests = None

_REAL_SESSION_GET = requests.Session.get


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

# A JSON endpoint that answers 200 with an error or bot-check page is retried on
# the same URL after these waits, in order, and then fails closed. Measured on
# 2026-10-22 (see Sources._read); the waits are long enough to outlast a short
# edge-cache or challenge window and short enough to keep a publication attempt
# inside its 15-minute budget.
JSON_RETRY_WAITS = (5.0, 20.0)


class RateLimited(Exception):
    """The server asked us to slow down; the wait is the caller's decision."""

    def __init__(self, status, retry_after=None):
        super().__init__('HTTP %s rate limit' % status)
        self.status = status
        self.retry_after = retry_after


def cache_bust(url, token):
    """Return ``url`` with one distinct, clearly labelled argument appended.

    The public URL's existing query is kept byte-for-byte.  Building a list with
    ``str.split`` and passing it to :func:`urlencode` used to raise ``TypeError``
    as soon as a cache-busted URL already had a query string; decoding and
    re-encoding would also change escaped values.  Appending one encoded pair is
    both simpler and faithful to the canonical request.  Nothing is signed,
    bypassed or rewritten, and the canonical URL remains the evidence link.
    """
    parts = urlsplit(url)
    added = urlencode(((CACHE_BUST_ARGUMENT, token),))
    query = parts.query + ('&' if parts.query else '') + added
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
        # Waits before re-asking a JSON source that answered 200 with a non-JSON
        # body. Instance attribute for the same reason: tests shorten it.
        self.json_retry_waits = JSON_RETRY_WAITS
        # A whole-discovery re-read when no Hotspawn view is usable at all; see
        # scripts.inventory.DISCOVERY_RETRY_WAITS for the measurement behind it.
        from scripts.inventory import DISCOVERY_RETRY_WAITS
        self.discovery_retry_waits = DISCOVERY_RETRY_WAITS

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
        # A JSON source gets one extra attempt for a non-JSON 200 body: that is a
        # transport-level error page, not a refusal, and re-asking the same URL is
        # the documented response. HTML views keep their original two attempts.
        attempts = 3 if as_json else 2
        for attempt in range(attempts):
            # Attempt 0 asks the CDN for a current copy; the retry falls back to the
            # canonical URL, so a source that rejects the extra argument (as the fixtures
            # API does with HTTP 400) is still read exactly as before.
            token = '%d-%s' % (int(time.time() * 1000), uuid.uuid4().hex[:8]) if bustable and attempt == 0 else None
            target = cache_bust(url, token) if token else url
            record['request_url'] = target
            record['cache_bust'] = token
            try:
                r = self.session.get(target, timeout=(10,30), headers=headers)
                if (r.status_code == 403 and _cffi_requests is not None
                        and type(self.session) is requests.Session
                        and 'get' not in self.session.__dict__
                        and requests.Session.get is _REAL_SESSION_GET):
                    # The fingerprinted transport raises its own error types, which
                    # are not requests exceptions, so nothing it does may escape this
                    # block: a refusal there has to end up as the same rate-limit
                    # decision the plain transport would produce (wait, then block
                    # the host for the run), and a broken fingerprinted transport
                    # has to fall back to the response the plain transport already
                    # got. Measured on 2026-10-22: an unguarded curl_cffi refusal
                    # aborted the whole refresh (run 39750217188, step "Refresh
                    # official sources"), which blocked every publication slot.
                    try:
                        merged_headers = dict(self.session.headers)
                        if headers:
                            merged_headers.update(headers)
                        r_alt = _cffi_requests.get(target, timeout=25, headers=merged_headers,
                                                   impersonate='chrome')
                        if r_alt.status_code < 400:
                            r = r_alt
                            record['tls_fallback'] = 'used'
                        else:
                            record['tls_fallback'] = 'refused: HTTP %s' % r_alt.status_code
                    except Exception as tls_error:
                        record['tls_fallback'] = 'failed: ' + str(tls_error)[:180]
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
                if as_json:
                    try:
                        body = r.json()
                    except ValueError as parse_error:
                        # A 200 whose body is not JSON is an error or bot-check
                        # page, not the API. Measured on 2026-10-22: the
                        # Hotspawn fixtures API answered the publication runner
                        # with 12,110 bytes of non-JSON at 01:22:35Z (sha256
                        # 3c4d3141b63385b6af7932252e769063ee7b5586a9e85fc7ed2d63f6b6ce7265)
                        # seven minutes after the same URL answered a full
                        # 97-fixture array, and the refresh fell back to a
                        # four-hour-old inventory. One extra bounded wait turns
                        # that transient into a successful read instead of a
                        # partial board; nothing about the request changes and a
                        # persistent failure still blocks exactly as before.
                        record.update(status='error',
                                      error='Non-JSON body: ' + str(parse_error)[:200])
                        if attempt >= len(self.json_retry_waits):
                            raise ValueError(record['error']) from parse_error
                        record['json_retry_wait_seconds'] = self.json_retry_waits[attempt]
                        time.sleep(self.json_retry_waits[attempt])
                        continue
                    if not isinstance(body, (list, dict)):
                        raise ValueError('JSON body is neither an object nor an array')
                else:
                    body = r.text
                    if any(x in body.lower() for x in ['not accepting visitors from your region', 'just a moment...', 'access denied']):
                        raise ValueError('Access restriction or challenge page; not usable evidence')
                record.pop('json_retry_wait_seconds', None)
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
                if status in (401,403,404,429) or attempt >= attempts - 1:
                    raise ValueError(record['error']) from e
                time.sleep(2)
            except ValueError as e:
                # A 200 response that is not usable evidence (stale CDN copy, or a
                # region/challenge page). Unchanged from before: one retry on the
                # canonical URL, then a hard failure. This is deliberately *not*
                # treated as a rate limit, so a closed source is never retried as
                # though it had merely asked us to slow down.
                record.update(status='error', error=str(e)[:250])
                if attempt >= attempts - 1:
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


def fixture_lineups(match):
    """Roster evidence for the Valve identity rule, with its provenance.

    Precedence, and every step is sourced on the row:

    1. the live HLTV fixture page's own lineups;
    2. each club's own HLTV team page (``scripts.hltv.team_pages``), which is
       what exists when HLTV publishes the bracket slot as TBA;
    3. a retained, dated lineup receipt captured from HLTV match pages in the
       same event (``data/lineup-receipts.json``, session db1f35c5).

    Valve's roster-continuity rule only needs a current five to tell repeated
    standings labels apart, so a missing source at one step falls through to
    the next instead of silently disabling the tier.
    """
    from scripts.hltv import fallback_lineups
    lineups={x['team']:x['players'] for x in (match.get('hltv_context') or {}).get('lineups',[]) if x.get('players')}
    for row in (match.get('hltv_team_pages') or {}).get('teams',[]):
        players=row.get('players') or row.get('lineup')
        if players:
            lineups.setdefault(row['team'],players)
    receipt=None
    if len(lineups)<2:
        received, receipt = fallback_lineups(match)
        for team, players in (received or {}).items():
            lineups.setdefault(team, players)
    return lineups, receipt


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
    # the research flag and the observation time. Session b214c818: before
    # pricing, each retained listing URL is re-read (scripts/books.py) and its
    # observation renewed only when the live page re-confirms the exact pair,
    # UTC start and an asymmetric two-way pair; a parse miss leaves the receipt
    # to expire into the lower tiers, never a guessed price.
    from scripts.core import book_research_pick, book_receipts as load_book_receipts
    from scripts import books as books_probe
    receipts = books_probe.for_unpriced(load_book_receipts(), open_matches)
    if receipts:
        try:
            receipts, reobserved = books_probe.reobserve(receipts, src, now)
            for record in reobserved:
                if record.get('status') in ('renewed', 'parse_miss', 'error'):
                    for m in open_matches:
                        if m['probabilities'] is None and str(m.get('id')) == str(record.get('fixture_id') or ''):
                            m['attempts'].append({'provider': 'Book listing re-observation', 'status':
                                'resolved' if record.get('status') == 'renewed' else 'unresolved',
                                'reason': record.get('reason'), 'url': record.get('url')})
        except Exception as e:
            flags.append(issue('book_reobserve', str(e), 'https://egamersworld.com/counterstrike/matches'))
    for m in open_matches:
        if m['probabilities'] is None:
            book_research_pick(m, receipts=receipts, now=now)
    # Originated lines: Valve's official standings points and Valve's own
    # published expected-win formula and calibration. Used only where no market
    # line passed its gates; shown beside market lines for comparison.
    from scripts import vrs
    from scripts import vrs_anchor_2d0a85f2 as vrs_anchor  # R-1: anchors for duplicated Valve labels
    standings, vrs_meta, vrs_problem = vrs.fetch(src, datetime.now(timezone.utc), os.environ.get('GITHUB_TOKEN'))
    if vrs_problem:
        flags.append(issue('vrs',vrs_problem,vrs.BLOB.rsplit('/blob',1)[0]))
    if standings:
        for m in open_matches:
            lineups, lineup_receipt = fixture_lineups(m)
            if lineup_receipt and not any(a.get('provider')=='HLTV lineup receipt' for a in m['attempts']):
                m['attempts'].append({
                    'provider':'HLTV lineup receipt',
                    'status':'resolved',
                    'url':lineup_receipt['lineups'][0]['source'],
                    'reason':lineup_receipt['reason'],
                })
                if lineup_receipt.get('flag') and lineup_receipt['flag'] not in m['flags']:
                    m['flags'].append(lineup_receipt['flag'])
            if m['probabilities'] is None:
                vrs.apply(m,standings,vrs_meta,lineups)
            else:
                vrs.compare(m,standings,vrs_meta,lineups)
    # Second originated tier, skipped entirely when every row is already priced:
    # Valve's monthly file cannot resolve a club that entered the standings
    # after it was cut. HLTV publishes the same ranking, dated, continuously, so
    # it is read only for those rows - same formula, same calibration, fail
    # closed, and the row says which dated page supplied the points.
    mirror_open = [m for m in open_matches if m['probabilities'] is None]
    if mirror_open:
        try:
            from scripts import vrs_mirror
            mirror_standings, mirror_meta, mirror_problem = vrs_mirror.fetch(src, datetime.now(timezone.utc))
        except Exception as e:  # a broken adapter is a finding, never a price
            mirror_standings, mirror_meta, mirror_problem = None, None, 'HLTV Valve ranking mirror error: %s' % e
        if mirror_problem:
            flags.append(issue('vrs_mirror', mirror_problem, 'https://www.hltv.org/valve-ranking/teams'))
            for m in mirror_open:
                m['attempts'].append({'provider': 'HLTV Valve ranking mirror', 'status': 'error',
                    'reason': mirror_problem, 'url': 'https://www.hltv.org/valve-ranking/teams'})
        elif mirror_standings:
            official = ({'file': vrs_meta.get('file'), 'commit': vrs_meta.get('commit'),
                         'as_of': standings['as_of']} if standings else None)
            for m in mirror_open:
                if m['probabilities'] is not None:
                    continue
                lineups, _ = fixture_lineups(m)
                vrs_mirror.apply(m, mirror_standings, mirror_meta, lineups, official)
    # Final research tier: a sourced pick from verified HLTV fixture identity
    # and ranking order, with no probability. Anything left stays unresolved.
    from scripts.core import research_rank_pick
    for m in matches:
        if m['state']=='open' and m['probabilities'] is None:
            research_rank_pick(m)
    if standings:
        for m in open_matches:
            if m['probabilities'] is None and not m.get('pick'):
                lineups, _ = fixture_lineups(m)
                lineups = vrs_anchor.with_anchors(m, lineups)
                vrs.research_single(m,standings,vrs_meta,lineups)
    # Say exactly which page confirmed the roster when HLTV had no fixture
    # lineup, so a published row never implies evidence it does not have.
    for m in matches:
        if m['state']!='open' or not m.get('hltv_team_pages'):
            continue
        if m.get('method') not in ('model_vrs','research_vrs_single'):
            continue
        if (m.get('hltv_context') or {}).get('lineups'):
            continue
        if any(a.get('provider')=='HLTV lineup receipt' for a in m.get('attempts') or []):
            continue
        note=(' HLTV lists this bracket slot without team names, so the roster was confirmed from each club\'s '
              'own HLTV team page (recorded on the row) before Valve\'s roster-continuity rule was applied.')
        m['reason']=(m.get('reason') or '')+note
        m['flags'].append('Roster confirmed from the clubs\' HLTV team pages: the HLTV fixture page is a TBA bracket slot.')
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
        m['expires_at'] = pick_deadline(m, fixture_observed) if m['state'] == 'open' else None
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
