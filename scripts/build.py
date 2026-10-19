"""Build an accessible, fully static dashboard. No browser-side API dependencies."""
import argparse
import copy
import csv
import html
import hashlib
import os
import subprocess
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from scripts.core import dt, iso, fresh, pick_deadline, HOTSPAWN, FIXTURES, GAMMA, PIN, norm, IDENTITIES as IDENTITY_REGISTER
from scripts import vrs

ROOT=Path(__file__).resolve().parents[1]
REPO='https://github.com/buffedlizard55-lab/MaltaProj4'

def e(v): return html.escape(str(v if v is not None else ''),quote=True)
def link(url,label,cls=''): return f'<a class="{e(cls)}" href="{e(url)}">{e(label)}</a>'
def date(v,full=False):
    if not v: return ''
    return dt(v).strftime('%d %b %Y · %H:%M UTC' if full else '%d %b · %H:%M')
def tag(text,kind=''): return f'<span class="badge {kind}">{e(text)}</span>'
ICONS={
'index':'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
'picks':'<path d="m5 12 4 4L20 5"/><path d="M20 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h9"/>',
'matches':'<path d="M5 4h14v17H5zM8 2v4m8-4v4M5 9h14M8 13h3m2 0h3m-8 4h3m2 0h3"/>',
'review':'<path d="m12 3 10 17H2L12 3zM12 9v5m0 2v1"/>',
'sources':'<path d="M4 3h11l5 5v13H4zM14 3v6h6M8 13h8m-8 4h5"/>',
'analysis':'<path d="M4 20V10m5 10V4m5 16v-7m5 7V7"/>',
'unresolved':'<path d="M12 9v5m0 3v.01M4.5 4.5h15v15h-15z"/>'}
NAV=[('index','Overview'),('picks','Picks'),('unresolved','Research'),('matches','Matches'),('analysis','TWC analysis'),('review','Review'),('sources','Sources')]


def page(name,title,body,data):
    nav=''.join(f'<a href="{slug}.html"'+(' aria-current="page"' if name==slug or (name=='unresolved' and slug=='picks') or (name=='evidence' and slug=='sources') else '')+f'><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[slug]}</svg><span>{label}</span></a>' for slug,label in NAV)
    brand='<span class="brandmark" aria-hidden="true"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m5 19 14-14M6 5h13v13"/></svg></span><span class="brandname">hotspawn<span>CS2 SCOUT</span></span>'
    observed=data.get('fixtures_observed_at')
    coverage_rows=[{k:m.get(k) for k in ('id','state','start','lock','expires_at')} | {'priced':m['probabilities'] is not None,
        'model':m.get('method')=='model_vrs',
        'research':m['probabilities'] is None and bool(m.get('pick')) and str(m.get('method') or '').startswith('research_')} for m in data['matches']]
    coverage_json=json.dumps(coverage_rows,separators=(',',':')).replace('<','\\u003c')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#132c28"><meta name="description" content="Independent CS2 pick research for the Hotspawn lobby. External market probabilities, clear sources, and honest coverage limitations."><title>{e(title)} · CS2 Scout</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><script src="assets/app.js" defer></script></head><body data-observed="{e(observed)}"><script type="application/json" id="coverage-data">{coverage_json}</script>
<a class="skip" href="#main">Skip to content</a><aside class="sidebar"><a class="brand" href="index.html" aria-label="CS2 Scout home">{brand}</a><p class="nav-label">RESEARCH DESK</p><nav class="nav" aria-label="Main navigation">{nav}</nav><div class="sidebar-footer"><p><span class="dot"></span>Automatic checks · every 15 min + stale watchdog</p><p>External lines + our VRS model. No crowd picks.</p><p>Independent research.<br>Not affiliated with Hotspawn.</p>{link(REPO,'View project ↗')}</div></aside>
<div class="shell"><header class="topbar"><a class="brand mobile-brand" href="index.html" aria-label="CS2 Scout home">{brand}</a><div class="context"><span class="game-tag">CS2</span><span>Counter-Strike 2</span><span class="muted"> / &nbsp; Research dashboard</span></div><span class="refresh">Last check: {e(date(data['last_attempt_at']))} UTC</span></header>
<main id="main"><div id="runtime-stale" class="notice error" role="status" hidden><strong>Snapshot expired or timestamp unverified.</strong> Current picks are withheld. The schedule is a target, not a guarantee. Check the {link(REPO+'/actions','refresh workflow')} and {link('sources.html','source status')}.</div><noscript><div class="notice error"><strong>Live expiry checks require JavaScript.</strong> Treat numeric entries as dated observations, not current recommendations. Each line shows its observation and expiry; no automatic current-time check is possible with JavaScript off.</div></noscript>{body}</main>
<footer><p>Independent research; not affiliated with Hotspawn or betting operators. Not betting advice. Market-implied probabilities are estimates, not guarantees. No bets or Hotspawn picks are placed by this site.</p><div>{link('sources.html','Methodology')}{link('data/latest.json','JSON data')}{link('data/matches.csv','CSV export')}{link('build-info.json','Build receipt')}{link(REPO,'GitHub ↗')}</div></footer></div></body></html>'''


def head(kicker,title,desc,data):
    return f'<div class="page-head"><div><p class="eyebrow">{e(kicker)}</p><h1>{e(title)}</h1><p class="muted">{desc}</p></div><span class="date-pill">{e(dt(data["last_attempt_at"]).strftime("%a, %d %b %Y"))}</span></div>'


METHOD_LABELS={'exchange':'Exchange line','bookmaker_fallback':'Bookmaker line','exchange_wide':'Wide exchange · low confidence','model_vrs':'Our VRS model line · no market','research_rank':'Research pick · no market line','research_rank_single':'Research pick · one ranking only','research_vrs_single':'Research pick · one Valve listing only'}
METHOD_TAGS={'exchange':'Exchange line','bookmaker_fallback':'Bookmaker fallback','exchange_wide':'Wide line · low confidence','model_vrs':'Our model line','research_rank':'Research only','research_rank_single':'Research only · one ranking','research_vrs_single':'Research only · Valve listing'}
METHOD_KIND={'exchange':'gray','bookmaker_fallback':'gray','exchange_wide':'warning','model_vrs':'model','research_rank':'warning','research_rank_single':'warning','research_vrs_single':'warning'}
MARKET_METHODS=('exchange','bookmaker_fallback','exchange_wide')


def array(value):
    return json.loads(value) if isinstance(value, str) else value


def is_research(m):
    return str(m.get('method') or '').startswith('research_')


def market_rows(rows): return [m for m in rows if m['probabilities'] is not None and m.get('method') in MARKET_METHODS]
def non_market_rows(rows): return [m for m in rows if m['state']=='open' and m.get('method') not in MARKET_METHODS]


def probability(m):
    if m['probabilities'] is None:
        if m.get('pick'):
            return '<div class="probability research-prob" role="group" aria-label="No verified market probability; research pick only"><p class="research-note">No verified market line. Blank means unverified, never 50/50.</p></div>'
        return '<div class="probability" role="group" aria-label="Unverified probability: blank"></div>'
    a=round(m['probabilities'][0]*100,1);b=round(100-a,1)
    label='OUR MODEL LINE (VRS)' if m.get('method')=='model_vrs' else 'OUR FAIR LINE'
    check=m.get('model_check') or {}
    model=''
    if check.get('status')=='ok':
        x=check['probabilities'][0]*100
        model=f'<div class="model-line">VRS model: {x:.1f}% / {100-x:.1f}%'+(' · <strong>favourite differs</strong>' if not vrs.gap(m)[1] else '')+'</div>'
    return f'<div class="probability"><div class="prob-team-labels"><span>{e(m["teams"][0])}</span><span>{e(m["teams"][1])}</span></div><div class="prob-pair"><span class="{"fav" if a>b else ""}" aria-label="{e(m["teams"][0])} {a:.1f} percent">{a:.1f}%</span><span class="{"fav" if b>a else ""}" aria-label="{e(m["teams"][1])} {b:.1f} percent">{b:.1f}%</span></div><div class="prob-bar" aria-hidden="true"><i style="width:{a}%"></i></div><div class="prob-label">{label} · {m["fair_odds"][0]:.2f} / {m["fair_odds"][1]:.2f}</div>{model}</div>'


def table(matches,review=False,label='Match table'):
    if not matches: return '<div class="panel empty">No matches in this category at the last successful check. See All matches for the retained feed.</div>'
    rows=[]
    for m in sorted(matches,key=lambda item:(item['state']!='open', (dt(item['start']).timestamp() if item['state']=='open' else -dt(item['start']).timestamp()) if item.get('start') else float('inf'),item['id'])):
        research=is_research(m)
        state='not_open' if m['state']!='open' else ('priced' if m['probabilities'] is not None else ('research' if research and m.get('pick') else 'unresolved'))
        evidence=m['evidence'][0] if m['evidence'] else {}
        obs=evidence.get('observed_at','')
        research_only=' research-only' if research else ''
        pick=(f'<span class="pick{research_only}">{e(m["pick"])}</span>'+tag(METHOD_TAGS.get(m['method'],'Exchange line'),METHOD_KIND.get(m['method'],'gray'))) if m['pick'] else tag('No directional edge' if m['probabilities'] is not None else ('Unresolved' if state=='unresolved' else 'Not open'),'warning' if state=='unresolved' else 'gray')
        source=link(m['source_url'],'Hotspawn ↗')+link('evidence.html#match-'+m['id'],'Evidence & lines')
        if evidence and evidence.get('provider')=='Valve VRS model':
            source+=link(evidence['url'],'Valve standings ↗')
        elif evidence: source+=link(evidence['api_url'],evidence['provider']+' ↗')
        if m.get('hltv_context') and (research or m['method']=='model_vrs'):
            source+=link(m['hltv_context'].get('source'),'HLTV fixture & lineups ↗' if m['method']=='model_vrs' else 'HLTV fixture & ranking ↗')
        if m.get('method')=='research_vrs_single' and (m.get('vrs_research') or {}).get('source'):
            source+=link(m['vrs_research']['source'],'Valve standings ↗')
        if evidence:
            source+=f'<span class="quote-time">Observed {e(date(obs))} UTC<br>Expires {e(date(m.get("expires_at")))} UTC</span>'
        elif research and m.get('method')=='research_vrs_single':
            source+=f'<span class="quote-time">No price quote. Valve standings of {e((m.get("vrs_research") or {}).get("standings_as_of"))}, observed {e(date((m.get("vrs_research") or {}).get("observed_at")))} UTC</span>'
        elif research:
            source+=f'<span class="quote-time">No price quote. Ranking context observed {e(date((m.get("hltv_context") or {}).get("observed_at")))} UTC</span>'
        reason=''
        if review:
            items=[m['reason']] if m.get('reason') else []
            items+=m['flags']
            reason='<td class="review-reason"><ul>'+''.join('<li>'+e(i)+'</li>' for i in dict.fromkeys(items) if i)+'</ul>'+link('evidence.html#match-'+m['id'],'View each attempted source →')+'</td>'
        needs=' needs-pick' if m['state']=='open' and m['probabilities'] is None else ''
        rows.append(f'''<tr class="row{needs}" data-needs="{'1' if needs else '0'}" data-match="{e(m['id'])}" data-status="{state}" data-search="{e((' '.join(t or '' for t in m['teams'])+' '+(m['competition'] or '')+' '+m['id']).lower())}" data-event="{e(m['competition'])}" data-start="{e(m['start'])}" data-lock="{e(m['lock'])}" data-expires="{e(m.get('expires_at'))}" data-evidence="{e(obs)}"><td class="team-col"><div class="teams">{e(m['teams'][0])}<span>vs</span>{e(m['teams'][1])}</div><div class="competition">{e(m['competition'])} · {e((m['tier'] or '').upper()) or 'Tier unverified'}</div></td><td class="time-cell">{e(date(m['start']))}<span class="small">UTC · locks {e(dt(m['lock']).strftime('%H:%M')) if m['lock'] else 'unverified'}</span></td><td>{probability(m)}</td><td class="pick-cell">{pick}</td>{reason}<td class="source-links">{source}</td></tr>''')
    return '<div class="table-wrap" tabindex="0" role="region" aria-label="'+e(label)+'"><table role="table"><caption>Whole-match winner only. Blank percentages = unverified; never a default 50/50. Times UTC.</caption><thead><tr><th scope="col">Match / event</th><th scope="col">Start / lock</th><th scope="col">Win probability</th><th scope="col">Our pick</th>'+('<th scope="col">Limitation / review flag</th>' if review else '')+'<th scope="col">Sources</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'


def starts_on(m, day):
    """Whether a fixture starts on the snapshot's UTC calendar day."""
    try:
        return bool(m.get('start')) and dt(m['start']).date() == day
    except (ValueError, TypeError):
        return False


def gap_ledger(rows, captured):
    """Every source this project tried for an unpriced row, with the numbers it saw.

    The user asked for a pick on every fixture and, where one cannot be made,
    for the reason and the external evidence that was found. A rejected quote is
    therefore shown with its raw state - mid price, bid/ask, spread, liquidity
    and how old the exchange's own last update was - so the reader can see the
    line exists and judge for themselves why it is not publishable here. It is
    labelled as a rejected observation and never as a pick or a probability.
    """
    blocks = []
    for m in rows:
        items = []
        seen = set()
        for attempt in m.get('attempts') or []:
            # The collector queries the exchange twice (a second pass relaxes the
            # spread ceiling only), so an identical rejection would otherwise be
            # listed twice. The raw list stays on evidence.html; this summary reads
            # once per source and gate.
            fingerprint = (attempt.get('provider'), attempt.get('reason'),
                           (attempt.get('rejected_quote') or {}).get('api_url'),
                           ((attempt.get('rejected_quote') or {}).get('raw') or {}).get('updatedAt'))
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            status = str(attempt.get('status') or 'unresolved')
            label = {'resolved': 'accepted', 'unresolved': 'no usable line', 'error': 'access refused or failed'}.get(status, status)
            line = f'<li><strong>{e(attempt.get("provider"))}</strong> · {e(label)}<p class="muted">{e(attempt.get("reason"))}</p>'
            quote = attempt.get('rejected_quote') or {}
            raw = quote.get('raw') or {}
            detail = []
            try:
                outcomes = array(raw.get('outcomes'))
                prices = [float(x) for x in array(raw.get('outcomePrices'))]
                if len(outcomes) == 2 and len(prices) == 2:
                    detail.append('quoted mid: ' + ' / '.join('%s %.1f%%' % (o, p * 100) for o, p in zip(outcomes, prices)))
            except (TypeError, ValueError, KeyError):
                pass
            for key, fmt in (('bestBid', 'bid %.2f'), ('bestAsk', 'ask %.2f'), ('liquidity', 'liquidity $%.2f'),
                              ('volume', 'volume $%.2f'), ('spread', 'spread %.2f')):
                value = raw.get(key)
                if value in (None, ''):
                    continue
                try:
                    detail.append(fmt % float(value))
                except (TypeError, ValueError):
                    detail.append(fmt % e(value))
            try:
                detail.append('bid-ask gap %.1f points, where a published line needs 25 or less'
                              % ((float(raw['bestAsk']) - float(raw['bestBid'])) * 100))
            except (KeyError, TypeError, ValueError):
                pass
            updated = raw.get('updatedAt') or quote.get('updated_at')
            if updated:
                try:
                    hours = (captured - dt(updated)).total_seconds() / 3600
                    detail.append('exchange last update %.1f h before this snapshot' % hours)
                except (ValueError, TypeError):
                    detail.append('exchange last update ' + e(date(updated)) + ' UTC')
            if detail:
                line += '<p class="small"><span class="rejected-line">rejected observation</span> · ' + e(' · '.join(detail)) + '</p>'
            target = quote.get('api_url') or attempt.get('url')
            if target:
                line += link(target, 'Raw source record ↗')
            items.append(line + '</li>')
        if not items:
            items = ['<li><p class="muted">' + e(m.get('reason') or 'No attempt was recorded for this fixture.') + '</p></li>']
        blocks.append('<div class="gap-card"><h3>' + e(' vs '.join(m['teams'])) + '</h3><p class="competition">'
                      + e(m.get('competition') or 'competition not stated') + ' · ' + e(date(m.get('start'))) + ' UTC'
                      + (f' · tier {e(m["tier"].upper())}' if m.get('tier') else '') + '</p>'
                      + '<ul class="checklist">' + ''.join(items) + '</ul>'
                      + '<p class="small">' + link('evidence.html#match-' + m['id'], 'Every retained observation for this row ↗')
                      + ' · ' + link(m['source_url'], 'Hotspawn fixture ↗') + '</p></div>')
    if not blocks:
        return ''
    return ('<div class="gap-grid">' + ''.join(blocks) + '</div>')


def filters(matches,default='all'):
    events=sorted({m['competition'] for m in matches if m['competition']})
    states=[('needs','No percentage'),('all','All entries'),('open','Open matches'),('priced','With probabilities'),('research','Research-only pick'),('unresolved','Unresolved'),('not_open','Not open / past')]
    return '<div class="filters"><label class="search" for="search">Search team, tournament or match ID<input id="search" type="search" placeholder="Find a team or match…" autocomplete="off"></label><label for="status">Show<select id="status">'+''.join(f'<option value="{s}"'+(' selected' if s==default else '')+f'>{l}</option>' for s,l in states)+'</select></label><label for="event">Tournament<select id="event"><option value="all">All tournaments</option>'+''.join(f'<option value="{e(x)}">{e(x)}</option>' for x in events)+'</select></label><button id="reset" class="filter-button" type="button">Reset</button><span id="result-count" class="count" role="status" aria-live="polite">'+str(len(matches))+' matches</span></div>'


def glance(data, opens):
    """Every open match in one phone-readable list, at the top of the summary.

    This is the executive summary's answer to "where are the picks?": bold team
    is the pick, the number beside it is that team's win chance, and the whole
    row is one tap to the evidence. Rows repeat no ``data-match`` table markup
    (the validator keeps one rendered table row per fixture); expiry is instead
    handled in app.js from the ``data-glance-*`` deadlines, exactly like the
    hero's next pick. A missing percentage stays visibly missing here too.
    """
    rows=[]
    for m in sorted(opens, key=lambda x:(x.get('start') or '', x['id'])):
        if m['probabilities'] is not None and m.get('pick'):
            ix=m['teams'].index(m['pick'])
            pick=('<span class="glance-pick">Pick: <strong>'+e(m['pick'])+'</strong> '
                  '<span class="numbers">'+('%.1f%%' % (m['probabilities'][ix]*100))+'</span></span>')
            kind='Our VRS model line' if m.get('method')=='model_vrs' else ('Wide market line · low confidence' if m.get('method')=='exchange_wide' else 'Market line')
            priced='1'
        elif m['probabilities'] is not None:
            pick='<span class="glance-pick">No directional edge <span class="numbers">'+('%.1f%% / %.1f%%' % (m['probabilities'][0]*100, m['probabilities'][1]*100))+'</span></span>'
            kind='Our VRS model line' if m.get('method')=='model_vrs' else 'Market line'
            priced='1'
        elif m.get('pick'):
            pick='<span class="glance-pick">Research pick: <strong>'+e(m['pick'])+'</strong></span>'
            kind='Research only · no percentage — why ↓'
            priced='0'
        else:
            pick='<span class="glance-pick glance-none">No pick yet</span>'
            kind='Unresolved · no percentage — why ↓'
            priced='0'
        rows.append('<li><a class="glance-row" href="evidence.html#match-'+e(m['id'])+'" data-glance-start="'+e(m.get('start'))+'" data-glance-lock="'+e(m.get('lock'))+'" data-glance-expires="'+e(m.get('expires_at'))+'" data-glance-priced="'+priced+'">'
                    '<span class="glance-when">'+e(date(m.get('start')))+' UTC</span>'
                    '<span class="glance-teams">'+e(m['teams'][0])+' <span class="muted">vs</span> '+e(m['teams'][1])+'</span>'
                    +pick+'<span class="glance-kind">'+e(kind)+'</span></a></li>')
    if not rows:
        listing='<p>No open Hotspawn CS2 fixture at the last successful check. '+link('matches.html','See the retained feed →')+'</p>'
    else:
        listing='<ol class="glance-list">'+''.join(rows)+'</ol>'
    return ('<section class="panel glance" id="picks-at-a-glance" aria-label="Picks at a glance">'
            '<p class="eyebrow muted">Executive summary · every open match</p><h2>Picks at a glance</h2>'
            '<p class="glance-how">In start-time order: the <strong>bold team is our pick</strong> and the percentage is its win chance '
            '(market line first, our VRS model where no market exists). Tap any match for its sources and calculation. '
            '<em>Research only</em> means a sourced pick with <strong>no percentage</strong>; <em>No pick yet</em> means nothing supportable was found — '
            'both are explained in <a href="#unresolved-summary">Unresolved picks &amp; limitations</a> below.</p>'
            +listing
            +'<p class="small glance-foot">Snapshot '+e(date(data['last_attempt_at'],True))+'. The board re-checks Hotspawn every 15 minutes (plus a stale-watchdog). '
            +link('picks.html','Full updated pick board →')+' · '+link('unresolved.html','Unresolved &amp; limitations →')+' · '+link('matches.html','All matches →')+'</p></section>')


def overview(data):
    matches=data['matches'];opens=[m for m in matches if m['state']=='open'];priced=[m for m in opens if m['probabilities'] is not None];missing=[m for m in opens if m['probabilities'] is None]
    market=market_rows(opens);model=[m for m in opens if m.get('method')=='model_vrs']
    researched=[m for m in missing if m.get('pick')];unresolved=[m for m in missing if not m.get('pick')]
    nonmarket=non_market_rows(matches)
    percent=round(len(priced)/len(opens)*100) if opens else 0
    next_pick=next((m for m in priced if m['pick']),None)
    next_html='<p class="eyebrow">No verified next pick</p><p>Missing evidence stays visible. Check the unresolved list for each limitation.</p>'
    if next_pick:
        m=next_pick;ix=m['teams'].index(m['pick']);q=m['evidence'][0]
        basis='our VRS model estimate, no market line' if m.get('method')=='model_vrs' else q['provider']+' · market-implied, not guaranteed'
        next_html=f'<div data-next-lock="{e(m["lock"])}" data-next-expires="{e(m.get("expires_at"))}"><p class="eyebrow">Next pick · {e(date(m["start"]))} UTC</p><div class="next-teams">{e(m["teams"][0])}<span>vs</span>{e(m["teams"][1])}</div><div class="pick-big">{e(m["pick"])} <span class="numbers">{m["probabilities"][ix]*100:.1f}%</span></div><small>{e(basis)}</small><br>{link("evidence.html#match-"+m["id"],"Review source & calculation →")}</div>'
    # The next few picks after that one, so a phone lands on the board itself
    # instead of a wall of text: every entry is one tap from its evidence.
    upcoming=sorted([m for m in priced if m.get('pick') and m is not next_pick],key=lambda m:m.get('start') or '')[:3]
    queue_html=''
    if upcoming:
        items=''
        for m in upcoming:
            ix=m['teams'].index(m['pick'])
            kind='model line' if m.get('method')=='model_vrs' else 'market line'
            items+=('<li><a href="evidence.html#match-'+e(m['id'])+'"><span class="queue-teams">'+e(m['teams'][0])
                    +' <span class="muted">vs</span> '+e(m['teams'][1])+'</span><span class="queue-pick">'+e(m['pick'])
                    +' <span class="numbers">'+('%.1f%%' % (m['probabilities'][ix]*100))+'</span></span>'
                    '<span class="queue-when">'+e(date(m['start']))+' UTC · '+e(kind)+'</span></a></li>')
        queue_html='<div class="queue"><p class="eyebrow muted">Then next</p><ul>'+items+'</ul></div>'
    body=head('Executive summary','The CS2 briefing.','Every listed match in one place. External lines first, our own model line where no market exists, a clear pick for each.',data)
    body+=f'<section class="hero" aria-label="Find your picks"><div><div class="eyebrow">Hotspawn lobby intelligence</div><h2>Your next pick.<br>Backed by external lines.</h2><p><span data-count="priced">{len(priced)}</span> of <span data-count="open">{len(opens)}</span> open matches have a win probability: <span data-count="market">{len(market)}</span> from betting markets and <span data-count="model">{len(model)}</span> from our Valve-standings model. <span data-count="researched">{len(researched)}</span> more carry a research pick and <span data-count="unresolved">{len(unresolved)}</span> have none. Hotspawn’s crowd percentages are never used.</p><div class="actions">{link("#picks-at-a-glance","See every pick ↓","button")}{link("picks.html","View updated picks →","button secondary")}{link(guidance_href(analysis_notes()),guidance_label(analysis_notes(),"Day-4 guidance")+" ↗","button secondary")}{link("analysis.html#day-four-results","Day-4 results ↗","button secondary")}</div></div><div class="hero-side">{next_html}{queue_html}</div></section>'
    body+=glance(data,opens)
    body+=('<nav class="section-nav" aria-label="Where the picks are">'
        +link('picks.html','Updated picks ('+str(len(priced))+')')
        +('<a href="unresolved.html?status=needs">No percentage (<span data-count="missing">'+str(len(missing))+'</span>)</a>')
        +link('matches.html','Every match ('+str(len(matches))+')')
        +link('analysis.html','TWC day 1–5 analysis')+link('analysis.html#day-four-results','Day-4 results')+link('analysis.html#day-three-results','Day-3 results (record)')+'</nav>')
    # One-tap jumps inside this page, for a phone that has to find the picks
    # without scrolling past the whole summary.
    body+=('<nav class="jump-nav" aria-label="Jump to a section of this page">'
        +link('#picks-at-a-glance','All picks at a glance')+link('#today','Today’s picks')+link('#later','Later on the board')
        +link('#unresolved-summary','Unresolved & limitations')+link('#coverage','Coverage')+'</nav>')
    body+=f'''<section class="panel start-here" id="start-here" aria-label="Start here"><p class="eyebrow muted">Start here · tap a card</p><h2>Where the picks are</h2><div class="start-grid"><a class="start-card" href="picks.html"><strong>Updated picks</strong><span>Every open match with a probability: market lines first, our model line where no market exists.</span></a><a class="start-card" href="#unresolved-summary"><strong>Unresolved & limitations</strong><span>Picks without a market line, research-only picks and anything still unresolved, with the reason.</span></a><a class="start-card" href="analysis.html#day-four-results"><strong>Day-4 results</strong><span>FURIA 2-0 Aurora and BETBOOM 2-1 Falcons. The Sunday bracket is now populated; each result links to HLTV.</span></a><a class="start-card" href="{e(guidance_href(analysis_notes()))}"><strong>{e(guidance_label(analysis_notes(),"Day-4 guidance"))}</strong><span>{e((front_page_plan(analysis_notes()) or {}).get("card","Day-3 decider results and the contrarian-but-not-stupid semi-final reads, with sources."))}</span></a><a class="start-card" href="matches.html"><strong>All matches</strong><span>The complete Hotspawn feed, including closed entries.</span></a></div><p class="start-note">On a phone: the bottom bar jumps between Overview, Picks, Research, Matches, TWC analysis, Review and Sources. Each match is a card with the pick on top, so no zooming or horizontal scrolling is needed.</p></section>'''
    body+=(f'<div class="notice info" id="coverage-line"><strong>Coverage at {e(date(data["last_attempt_at"]))} UTC:</strong> '
        f'{len(opens)} open fixture(s) — {len(priced)} with published probabilities ({len(market)} from markets, {len(model)} from our VRS model), {len(researched)} with a labelled research-only pick and no percentage, '
        f'{len(unresolved)} with no supported pick yet. {link("picks.html","Open the pick board →")} · {link("#unresolved-summary","Jump to the unresolved section ↓")}</div>')
    body+=f'<section class="stats" aria-label="Coverage at last check" id="coverage"><a class="stat" href="matches.html?status=open"><div class="stat-label">Open matches <span>↗</span></div><strong data-count="open">{len(opens):02d}</strong><span class="stat-foot">{len(matches)} total feed entries</span></a><a class="stat green" href="picks.html"><div class="stat-label">With probabilities <span>↗</span></div><strong data-count="priced">{len(priced):02d}</strong><span class="stat-foot"><span data-count="percent">{percent}</span>% of open · {len(market)} market · {len(model)} model</span></a><a class="stat amber" href="unresolved.html"><div class="stat-label">No market line <span>↗</span></div><strong>{len(nonmarket):02d}</strong><span class="stat-foot">{len(model)} model line(s) · {len(researched)} research pick(s) · {len(unresolved)} unresolved</span></a></section>'
    body+=f'<section class="panel" id="phone-tips" aria-label="How to use this site on your phone"><p class="eyebrow muted">📱 On your phone</p><h2>Find your picks in 2 taps</h2><div class="start-grid"><div class="start-card"><strong>1. Read Picks at a glance</strong><span>The list at the top of this page already shows every open match with our pick and its win percentage. Or use the bottom bar — Overview, Picks, Research, Matches and TWC analysis — and tap <em>Picks</em> for the full board. No login, no scrolling sideways.</span></div><div class="start-card"><strong>2. Check the percentage</strong><span>Each match card shows both teams, the win probability bar, and the pick on top. Market lines (green) or our VRS model (blue). If it says “Research only” there is no percentage — that’s intentional, not missing data.</span></div><div class="start-card"><strong>3. See the limits</strong><span>Tap <em>Research</em> for the full no-market list, then choose <em>No percentage</em> to see why <strong data-count="missing">{len(missing)}</strong> currently open match(es) have no verified win percentage. Some still have a research-only pick; unsupported numbers stay blank. Every row links to the source attempts.</span></div></div><p class="start-note">The collector compares Hotspawn’s <a href="https://play.hotspawn.com/lobby">lobby</a>, <a href="https://play.hotspawn.com/cs2-pickems">CS2 page</a> and <a href="https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1">fixture API</a>. The workflow checks on a 15-minute schedule, with a freshness gate and a 10-minute watchdog that requests a refresh when the published snapshot is over 90 minutes old. GitHub may delay runs; observation and expiry times are shown, and stale prices are withheld. <a href="sources.html">Check refresh health →</a></p></section>'
    if model:
        body+=f'<div class="notice info"><strong>Our own lines fill the market gaps.</strong> {len(model)} open match(es) have no usable betting line, so the probability is <strong>our originated line</strong>: Valve’s official Regional Standings points run through Valve’s own published win-expectation formula and calibration. It is labelled on every row and never presented as a market price. {link("sources.html#model","How the model works and how it compares with the market →")}</div>'
    if researched:
        body+=f'<div class="notice info"><strong>Research-only picks, clearly labelled.</strong> {len(researched)} open match(es) could not be priced by a market or our model, so the pick comes from sourced research only — HLTV fixture identity and ranking order, or one team listed in Valve’s official standings while the other is absent from that file — with <strong>no percentage</strong>. {link("unresolved.html","See each one and why →")}</div>'
    body+=f'<div class="notice"><strong>Coverage is not the same as certainty.</strong> {len(unresolved)} open match(es) have no supported pick at all. Names can differ across providers, some markets lack usable prices, model inputs can be ambiguous, and HLTV or esportsbook access may be restricted. {link("unresolved.html","See every non-market and unresolved match →")}</div>'
    _plan=front_page_plan(analysis_notes()) or {}
    if _plan.get('unpriced'):
        body+=(f'<div class="notice info" id="twc-unpriced"><strong>Unresolved picks &amp; their limitations ({e(_plan.get("nav_label","TWC"))}): '
            f'{len(_plan["unpriced"])} research item(s) flagged.</strong> '
            'These are dated research limitations, not proof a market is still absent. '
            'The current Hotspawn board counts above come from the latest refresh; unsupported values stay blank. '
            +link(guidance_href(analysis_notes(),'-unpriced'),'See each limitation and its source →')
            +link('unresolved.html','All non-market rows →')+'</div>')
    if data['coverage']!='verified':
        body+='<div class="notice error"><strong>Full current lobby coverage is unverified.</strong> A source failed, changed, or disagreed. '+link('review.html','See source irregularities →')+'</div>'
    if any(i.get('code')=='audit_quarantine' for i in data.get('issues',[])):
        body+='<div class="notice error"><strong>Some picks were withheld.</strong> The independent row audit could not reproduce at least one row, so its pick is not published. '+link('review.html','See which rows and why →')+'</div>'
    # Only priced rows are listed here. Rows without a market line already have
    # their own section below, and repeating a fixture ID on one page would break
    # the validator's "one rendered row per fixture" rule.
    today=[m for m in priced if starts_on(m, dt(data['generated_at']).date())]
    later=[m for m in priced if not starts_on(m, dt(data['generated_at']).date())]
    today_priced=len(today)
    today_research=[m for m in researched + unresolved if starts_on(m, dt(data['generated_at']).date())]
    # A snapshot captured late in the UTC day can have nothing left that starts today.
    # The section still has to answer "where is my pick?", so it relabels to the next
    # fixtures rather than publishing an empty "Today's picks" heading.
    if today:
        board=('<div class="section-heading" id="today"><div><p class="eyebrow muted">Executive summary · today</p>'
               f'<h2>Today\'s picks · {e(date(data["generated_at"]))} UTC</h2>'
               f'<p>{today_priced} priced pick(s) start today, in start-time order: the team named in the pick box is the recommendation, and the percentage beside it is its '
               'market-implied or modelled chance. '
               + (f'{len(today_research)} more fixture(s) today have no usable market line and are listed in the gaps section below with the reason. ' if today_research else '')
               + 'All times are UTC; a pick is withheld once its evidence or the Hotspawn lock passes.</p></div>'
               +link('picks.html','All updated picks →')+'</div>'+table(today,label="Today\'s picks")
               +('<div class="section-heading" id="later"><div><h2>Later on the board</h2><p>Open fixtures after today, in start-time order.</p></div>'
                 +link('picks.html','Full board →')+'</div>'+table(later[:8],label='Later picks') if later else ''))
    else:
        board=('<div class="section-heading" id="today"><div><p class="eyebrow muted">Executive summary · next up</p>'
               f'<h2>Next on the board · captured {e(date(data["generated_at"]))} UTC</h2>'
               '<p>No priced fixture starts on the capture date any more, so these are the next open picks, in start-time order. '
               + (f'{len(today_research)} fixture(s) with no usable market line are listed in the gaps section below with the reason. ' if today_research else '')
               + 'All times are UTC; a pick is withheld once its evidence or the Hotspawn lock passes.</p></div>'
               +link('picks.html','All updated picks →')+'</div>'+table(later[:8],label='Later picks'))
    if 'id="later"' not in board:
        board += '<section id="later"><h2>Later on the board</h2><p>No additional priced rows in this section. '+link('picks.html','Check the full pick board →')+'</p></section>'
    body+=board
    gap=[m for m in nonmarket if m['probabilities'] is None]
    body+=('<section id="unresolved-summary"><div class="section-heading"><div><p class="eyebrow muted">Executive summary · evidence gaps</p>'
           '<h2>Matches with no market line, and what was tried</h2><p>Rows above this section already carry a percentage: from a market where one exists, '
           'or from <strong>our own</strong> VRS model line where it does not. The rows here have a sourced pick and <strong>no percentage</strong>, or nothing '
           'supportable at all. Every rejected external line is shown with its numbers and the gate it failed. Blank means unverified, never 50/50.</p></div>'
           +link('unresolved.html','Full research queue →')+'</div>'
           +('<div class="panel limitations" id="pick-limitations"><h3>Limitations for generating these picks</h3>'
             '<ul class="checklist">'
             '<li><strong>No book lists the match.</strong> Low-tier and qualifier fixtures are often absent from Polymarket and Pinnacle, the two accessible line sources; Thunderpick and GG.BET gave this collector no validated automated quote, and access controls are not bypassed. '+link('sources.html','Source status →')+'</li>'
             '<li><strong>A market exists but fails a gate.</strong> Stale updates, spreads wider than 25 points (60 in the labelled wide tier) or under $100 of liquidity are shown as rejected observations below, never published as a percentage.</li>'
             '<li><strong>Names differ between sites.</strong> Odds move between sources only for an exact team pair and UTC start, or a label in the '+link('sources.html#method','verified alias register')+'; a renamed or academy label that no primary source links stays unresolved rather than guessed.</li>'
             '<li><strong>HLTV has no usable line.</strong> HLTV fixture pages confirm identity, lineups and rankings; their betting tables expose no independently confirmed numeric two-way line to this collector, and HLTV fan votes are never used.</li>'
             '<li><strong>Our model needs both teams.</strong> The '+link('sources.html#model','VRS model')+' prices a match only when both teams resolve in Valve’s official standings with their current rosters. With one side missing it degrades to a pick-only research tier, and with neither side resolvable the row stays unresolved with the attempts listed below.</li>'
             '<li><strong>Timing.</strong> Every percentage expires at the earliest of its 8-hour evidence window, the Hotspawn lock, match start or bookmaker cutoff, so a pick can disappear before a match begins if its evidence ages out and no refresh lands.</li>'
             '</ul></div>')
           +table(gap,True,label='Open matches without a market line')
           +gap_ledger([m for m in gap if m['state']=='open'], dt(data['generated_at']))+access_limitations(data)+'</section>')
    body+=f'<div class="freshness">Fixture observation: {e(date(data.get("fixtures_observed_at"),True))} · scheduled checks every 15 minutes at :04, :19, :34 and :49 UTC (GitHub may delay them), with a watchdog check every 10 minutes that dispatches the same verified pipeline when the published snapshot is over 90 minutes old · {link("sources.html","Refresh health ↗")}</div>'
    body+=f'''<div class="two-col"><section class="panel" id="how-picks"><p class="eyebrow muted">How picks are made</p><h2>Evidence before a favorite.</h2><ol class="method-steps"><li><div><strong>Find every Hotspawn CS2 fixture</strong><p>Compare the public lobby’s structured data with its own fixture feed.</p></div></li><li><div><strong>Price it from the market</strong><p>Validated exchange prices (Polymarket) or a bookmaker line (Pinnacle), normalized or de-margined.</p></div></li><li><div><strong>Originate our own line where no market exists</strong><p>Valve’s official standings points through Valve’s published formula and calibration, with HLTV lineups confirming each roster.</p></div></li><li><div><strong>Then research, never guess</strong><p>HLTV-verified identity and ranking order, or one-sided presence in Valve’s official standings, as a research-only pick with no percentage. Anything left stays unresolved.</p></div></li></ol>{link('sources.html#method','Read the methodology →')}{link('analysis.html','TWC review & contrarian screen →')}</section><section class="panel"><p class="eyebrow muted">Coverage notes</p><h2>What needs attention</h2><ul class="checklist"><li><span class="tick">↗</span>{len(matches)-len(opens)} feed entries are not open by sourced timestamps.</li><li><span class="tick">↗</span>Missing series format is left blank, not inferred.</li><li><span class="tick">↗</span>Wide exchange spreads are flagged as low precision; model lines are labelled; research-only picks carry no percentage.</li><li><span class="tick">↗</span>Prices expire at the earliest source TTL, start, lock or bookmaker cutoff.</li></ul>{link('review.html','Open Flagged for Review →')}</section></div>'''
    return body


def access_limitations(data):
    """Why a pick may carry no percentage, aggregated from this snapshot's own attempts.

    Every line is a measured result of the refresh that produced the table above, so a
    provider that starts returning usable lines disappears from this panel on its own.
    No line is a fixed editorial statement and no probability is implied by a gap.
    """
    opens=[m for m in data['matches'] if m['state']=='open']
    unpriced=[m for m in opens if m['probabilities'] is None]
    if not unpriced:
        return ''
    checks=data.get('source_checks') or []
    meta=json.loads((ROOT/'data/vrs/meta.json').read_text())
    urls={'Polymarket':GAMMA+'/markets','Pinnacle':PIN+'/markets/straight','HLTV':'https://www.hltv.org/matches',
          'Thunderpick':next((c['url'] for c in checks if c.get('name')=='Thunderpick fallback access'),'https://thunderpick.io/esports/cs2-betting'),
          'GG.BET':next((c['url'] for c in checks if c.get('name')=='GG.BET fallback access'),'https://gg.bet/en/esports/counter-strike'),
          'Valve VRS model':meta['blob_url']}
    detail={
      'Polymarket':'No accepted exchange line for these rows; see the recorded attempts below.',
      'Pinnacle':'No accepted bookmaker line for these rows; see the recorded attempts below.',
      'HLTV':'No accepted numeric line for these rows. Historical DOM evidence at research/harvest-621776e4/hltv-betting-dom.json showed a noOdds promotional cell on the sampled pages; this is not proof that every current fixture lacks odds.',
      'Thunderpick':'No usable quote accepted by this collector. A request failure or JavaScript-only response does not prove no odds exist.',
      'GG.BET':'No usable quote accepted by this collector; access restrictions are not bypassed.',
      'Valve VRS model':'No accepted model line for these rows. Missing standings, roster or identity inputs are not filled in.',
    }
    reasons={provider:sorted({a.get('reason') or a.get('status') or 'Unspecified limitation'
                for m in unpriced for a in m.get('attempts') or [] if a.get('provider')==provider})
             for provider in detail}
    counts={}
    for m in unpriced:
        providers={(attempt.get('provider') or '').strip() for attempt in m.get('attempts') or []}
        for provider in providers & detail.keys():
            counts[provider]=counts.get(provider,0)+1
    order=['Polymarket','Pinnacle','HLTV','Thunderpick','GG.BET','Valve VRS model']
    body=''.join('<tr><td data-label="Source"><strong>%s</strong></td><td data-label="Rows">%d of %d</td>'
                 '<td data-label="Limitation">%s</td><td data-label="Link" class="source-links">%s</td></tr>'
                 % (e(provider),counts[provider],len(unpriced),e(detail[provider])+'<ul>'+''.join('<li>'+e(reason)+'</li>' for reason in reasons[provider])+'</ul>',
                    link(urls.get(provider,'sources.html'),'Official endpoint ↗'))
                 for provider in order if counts.get(provider))
    return ('<div class="section-heading" id="access-limitations"><div><p class="eyebrow muted">Executive summary · access limitations</p>'
            '<h3>Why these rows have no percentage</h3><p class="muted">Counted from the attempts recorded for the %d open rows above. '
            'A blank percentage means no validated probability was accepted, never 50/50.</p></div>%s</div>'
            '<div class="table-wrap" tabindex="0" role="region" aria-label="Access limitations"><table role="table">'
            '<caption>Each limitation is a measured result of this refresh, with the endpoint that produced it.</caption>'
            '<thead><tr><th scope="col">Source</th><th scope="col">Rows affected</th><th scope="col">Limitation</th><th scope="col">Link</th></tr></thead>'
            '<tbody>%s</tbody></table></div>'
            % (len(unpriced),link('sources.html','Source health ↗'),body))


def checks_table(data):
    rows=[]
    for s in data['source_checks']:
        cache_age = str(s['cache_age_seconds'])+'s' if s.get('cache_age_seconds') is not None else 'not supplied'
        detail = (f"HTTP {s.get('http_status','')} · cache age {cache_age}" if s['status']=='ok' else s.get('error','Unverified'))
        rows.append(f'<tr><td data-label="Source"><strong>{e(s["name"])}</strong></td><td data-label="Status"><span class="source-status {"error" if s["status"]!="ok" else ""}">{e(s["status"].upper())}</span></td><td data-label="Observation">{e(date(s.get("observed_at") or s.get("checked_at"),True))}</td><td data-label="Result">{e(detail)}</td><td data-label="Official link" class="source-links">{link(s["url"],"Official endpoint ↗")}</td></tr>')
    return '<div class="table-wrap" tabindex="0" role="region" aria-label="Source health table"><table class="source-table" role="table"><caption>Latest refresh attempt. HTTP success alone does not verify a usable match price.</caption><thead><tr><th>Source</th><th>Status</th><th>Observation</th><th>Result</th><th>Link</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'


def model_comparison(data):
    """Rows where both a market line and our model line exist (open matches)."""
    rows=[m for m in data['matches'] if m['state']=='open' and m['probabilities'] is not None and (m.get('model_check') or {}).get('status')=='ok']
    return sorted(rows,key=lambda m:m['start'] or '')


def model_section(data):
    meta=json.loads((ROOT/'data/vrs/meta.json').read_text())
    sample=next((m['evidence'][0] for m in data['matches'] if m.get('method')=='model_vrs' and m.get('evidence')),None)
    commit=(sample or {}).get('standings_commit') or meta['commit']
    blob='https://github.com/ValveSoftware/counter-strike_regional_standings/blob/'+commit
    standings_url=(sample or {}).get('url') or meta['blob_url']
    as_of=(sample or {}).get('standings_as_of') or '2026-10-05'
    rows=model_comparison(data)
    body=''
    if rows:
        diffs=[abs(m['model_check']['probabilities'][0]-m['probabilities'][0]) for m in rows]
        agree=sum(1 for m in rows if vrs.gap(m)[1])
        table_rows=''.join('<tr><td>'+e(m['teams'][0])+' <span class="muted">vs</span> '+e(m['teams'][1])+'<div class="competition">'+e(m['competition'])+' · '+e(date(m['start']))+' UTC</div></td><td>%.1f%%</td><td>%.1f%%</td><td>%+.1f</td><td>%s</td><td class="source-links">%s%s</td></tr>'%(
            m['probabilities'][0]*100,m['model_check']['probabilities'][0]*100,(m['model_check']['probabilities'][0]-m['probabilities'][0])*100,
            'Yes' if vrs.gap(m)[1] else '<strong>No</strong>',link('evidence.html#match-'+m['id'],'Evidence'),link(m['model_check']['source'],'Valve standings ↗')) for m in rows)
        body=f'<p><strong>Live check against the market:</strong> across the {len(rows)} open matches that have both a market line and a model line in this snapshot, the mean absolute difference is <strong>{sum(diffs)/len(diffs)*100:.1f} percentage points</strong> and the favourite agrees in <strong>{agree} of {len(rows)}</strong>. Disagreements are flagged on the pick board and on the {link("analysis.html#model-vs-market","contrarian screen")}.</p><div class="table-wrap" tabindex="0" role="region" aria-label="Model versus market"><table role="table"><caption>First-named team’s chance: market line vs our VRS model line. The pick always follows the market where one exists.</caption><thead><tr><th scope="col">Match</th><th scope="col">Market</th><th scope="col">Model</th><th scope="col">Diff (pts)</th><th scope="col">Same favourite</th><th scope="col">Sources</th></tr></thead><tbody>'+table_rows+'</tbody></table></div>'
    return f'''<section class="panel prose" id="model"><p class="eyebrow muted">Originated lines · v1</p><h2>Our own line where no market exists: the VRS model.</h2><p><strong>Inputs (official):</strong> Valve’s {link(standings_url,"Regional Standings")} of {e(as_of)}, published in Valve’s own GitHub repository. The <em>Points</em> column is each team’s Glicko rank value ({link(blob+"/model/report.js","report.js")} prints <code>glickoTeam.rank()</code>).</p><p><strong>Formula (Valve’s, not ours):</strong> Valve evaluates its model by giving every match an expected win rate from the points difference ({link(blob+"/model/fit.js","fit.js")}, <code>priorWinExpectation</code>, rating deviation 75, using {link(blob+"/model/glicko.js","glicko.js")}). That procedure reduces exactly to <code>E = 1 / (1 + 10^(−g·(Pa − Pb)/400))</code> with <code>g = 1/√(1 + 3q²·75²/π²)</code> and <code>q = ln10/400</code>. Our test suite ports Valve’s procedure line by line and checks the closed form to 12 decimals.</p><p><strong>Calibration (Valve’s published fit):</strong> Valve’s {link(blob+"/modelfit.png","model-fit chart")} reports observed = 0.7986 × expected + 0.126, so the raw expectation is overconfident. We apply the published slope symmetrically, <code>p = 0.5 + 0.7986·(E − 0.5)</code>, so both sides sum to 100%.</p><p><strong>Identity:</strong> exact team labels or the sourced alias register only. Valve’s standings repeat some labels for older rosters, so a label is used only when it is unique or when the current HLTV lineup shares at least three players with exactly one listed roster, Valve’s own roster-continuity rule ({link(blob+"/model/team.js","team.js")}). Otherwise no model line is produced.</p><p><strong>Where it is used:</strong> only when no market line passes its gates. Beside market-priced rows it is shown for comparison and never changes the pick. Every model row is recomputed by the build validator and by the independent auditor.</p>{body}<p class="fineprint">Limitations: standings update monthly, so recent roster changes, stand-ins, map pools, LAN/online and best-of format are not modelled. It is a rating-based estimate, not a market price and not a guarantee.</p></section>'''


def methodology(data):
    return head('Audit trail','Sources & methodology.','Raw observations, transparent calculations, and honest limitations.',data)+checks_table(data)+model_section(data)+f'''<section class="panel prose" id="method"><p class="eyebrow muted">Calculation policy · v1</p><h2>One fixture list. Independent probabilities.</h2><p><strong>Discovery:</strong> {link(HOTSPAWN,'Hotspawn CS2 lobby')} establishes which fixtures belong here. Its CS2 hydration data, the {link("https://play.hotspawn.com/lobby","general lobby")} and {link(FIXTURES,'CS2 scheduled fixture API')} are compared by fixture ID and primary fields. All returned CS2 entries remain visible, including stale “scheduled” records. Schema, ID-set and field mismatches are flagged; missing pages are not silently ignored. Conflicting rows cannot supply picks. Partial discovery retains still-open previous-only entries with unverified membership; a wrong-game or unexpected empty result never erases the last good inventory.</p><p><strong>Identity:</strong> only exact case/punctuation-normalized team pairs and exact UTC starts are accepted. Polymarket’s own published team abbreviations may map to Hotspawn names; those team records are retained with the evidence. The small {link(REPO+"/blob/main/data/identities.json","verified alias register")} covers only explicitly registered organization labels ({e(', '.join(i['canonical'] for i in IDENTITY_REGISTER))}), with primary links and narrow CS2 scope recorded. BetBoom labels were checked on {link("https://betboom.team/","the organization’s official site")}. No fuzzy name matching, guessed team aliases, academy/main-team conflation, or assumed start-time corrections. Duplicate candidates are rejected. Known Hotspawn series format, if supplied, must agree with the external source. Where it is not supplied, it remains blank.</p><h2>Primary picks → research fallback</h2><ol><li>Discover CS2 from {link(GAMMA+'/sports','Polymarket’s sports registry')}, paginate every active event page, then validate the whole-match moneyline. Closed, live, map-only, handicap, totals, stale and malformed markets cannot supply a pick.</li><li>Only unresolved matches enter fallback research: try {link('https://www.hltv.org/matches','HLTV')} first. HLTV is a specialist source, not an official betting operator. Current automation may be denied. Ranks and fan votes are not probabilities; no uncalibrated rank-to-win formula is deployed.</li><li>Try {link(PIN+'/sports/12/markets/straight','Pinnacle’s public esports lines')} with its fixture feed, period 0, a pending parent match, open two-way moneyline and valid future cutoff. Then check {link('https://thunderpick.io/esports/cs2-betting','Thunderpick')} and {link('https://gg.bet/en/esports/counter-strike','GG.BET')} for remaining gaps. Their access restrictions or missing validated adapters are recorded separately. Access controls are not bypassed.</li><li><strong>Labelled wide-quote tier.</strong> For a fixture that would otherwise have no pick at all, an exchange quote that fails only the 25-point spread ceiling can still be accepted — but only when the market is open, accepting orders, has a fresh observation and update, is genuinely two-sided, and holds at least $100 of liquidity. The real spread is published, the row is flagged low confidence, the strict rejection is retained, and a 60-point ceiling still applies. This is a coverage decision, not a claim of precision.</li><li><strong>Our originated line.</strong> If no market line passes its gates, the {link('#model','VRS model')} prices the match from Valve’s official standings with Valve’s own formula and calibration, after confirming each roster against the HLTV lineup. The row is labelled as our model line, never as a market price. Pinnacle is tried before the wide exchange tier because a sharp bookmaker line outranks a wide quote.</li><li><strong>Research-only tiers, no numbers.</strong> A fixture with no usable line and no model line may receive a pick from an exact HLTV fixture identity (same opponent pair and UTC start). When both teams’ world rankings are exposed on that page the better-ranked team becomes the pick (<code>research_rank</code>); when exactly one team carries a published world ranking there and the other appears in the same fixture without one, that team becomes the pick (<code>research_rank_single</code>). Each row stores its per-team evidence — fixture label, HLTV label, rank, HLTV ranking link and the primary link for any label mapping — so the pick is re-derivable from the snapshot alone. The HLTV link is published, the row is labelled research-only, and probabilities and fair odds stay <em>blank</em>. This is a ranking-order signal, never a market probability.</li><li><strong>One-sided Valve standings tier, no numbers.</strong> If HLTV never listed the fixture at all, a row can still be resolved when exactly one team resolves in <a href="#model">Valve’s official global standings</a> under the model’s own identity rules (unique label, or a current HLTV lineup sharing at least three players with exactly one listed roster) and the other team’s label is genuinely absent from that file (<code>research_vrs_single</code>). A present-but-unresolvable label is not absent, and an HLTV-displayed VRS rank for the supposedly absent team blocks the tier. The pick is the listed team; no probability is derived from a single points value.</li><li>If no tier applies, probabilities, fair odds and the pick all stay blank. {link('unresolved.html','Unresolved picks')} gives the reason and every attempted source. There is no claim that a pick can always be generated, and no default 50/50.</li></ol><h2>Our lines: calculated, not guessed</h2><p>For decimal odds <code>d₁, d₂</code>, compute <code>qᵢ = 1 / dᵢ</code>, then <code>pᵢ = qᵢ / (q₁ + q₂)</code>. The overround is <code>q₁ + q₂ − 1</code>. American odds convert to decimal using <code>1 + A/100</code> for positive A, or <code>1 + 100/|A|</code> for negative A. Our fair decimal line is <code>1 / pᵢ</code>.</p><p>For two exchange outcome prices <code>x₁, x₂</code>, use <code>pᵢ = xᵢ / (x₁ + x₂)</code>. This is market-implied analysis, not an independently calibrated statistical forecast or a tradable quote. It excludes trading fees. We keep the primary accepted source; fallback lines do not overwrite primary picks or pretend to be a multi-book consensus.</p><p>A directional pick is the team with the larger probability; exactly equal verified prices get “no directional edge.” Unknown matches never default to 50/50. Display percentages are rounded to one decimal and complement to 100; downloadable data keeps full precision.</p><h2>Quality and freshness gates</h2><ul><li>Evidence must be no more than eight hours old, using both observation time (adjusted for HTTP cache Age) and exchange market update time. One expiry deadline also includes fixture age, match start, Hotspawn lock and bookmaker cutoff, and is enforced in the build and browser. A market update is not proof of a recent trade.</li><li>Exchange liquidity must be at least $100, with a valid two-sided bid/ask and spread no greater than 25 percentage points. Spreads over 10 points are flagged as low precision. These are conservative project policy thresholds, not validated accuracy guarantees.</li><li>Bookmaker overround must fall between −2% and 25%. Pinnacle does not supply a price-change timestamp in this response; that limitation is shown. One bookmaker is not consensus.</li><li>Lock times come from Hotspawn’s feed. Recommendations are withheld at lock, not only at match start. Not-open records are not claimed to be completed results.</li><li>Schedule: four publication attempts per hour at :04, :19, :34 and :49 UTC via {link(REPO+'/actions','GitHub Actions')}. A separate watchdog checks the live build receipt every 10 minutes and dispatches the same verified workflow only when the published snapshot is older than 90 minutes, with a 45-minute cooldown, a ten-dispatch daily budget and a hard stop if the receipt cannot be read. Historical measurements on 16 October 2026 found delayed and missed runs under the earlier, slower schedule; the detailed diagnosis is linked in the repository. GitHub may still delay or drop jobs or disable schedules; no exact delivery guarantee is possible. The last successful snapshot is retained on failure, with a prominent stale warning, and never relabeled fresh.</li><li>Bookmaker reachability is measured, not assumed: the last research probe read {link(REPO+'/blob/main/research/harvest-dedd2e34/book-probe.json','twelve endpoints')} from a normal internet egress. Polymarket's Gamma API and Pinnacle's guest esports API returned usable JSON; GG.BET (page and public sport API), Thunderpick's CS2 page, Oddschecker and Pinnacle's outright endpoint refused access (403/401), and api.thunderpick.com does not resolve. So for a low-tier fixture the honest ceiling is 'no accessible two-sided line', which is why such rows fall to our model line or a labelled research pick instead of an invented number.</li></ul><h2>Verification scope</h2><p>Every displayed match fact is traced to the official Hotspawn response; this verifies what the source reported, not that contradictory source records are correct. Every accepted price retains the official operator’s raw fields and timestamp. Calculated probabilities are explicitly derived. We checked the initial snapshot row by row with executable assertions and source links; future data is verified by the same schema, identity, market-type, freshness and arithmetic rules. This does not certify team rosters, the true chance of winning, bookmaker accuracy, or every website on the internet.</p><p>{link('evidence.html','Inspect evidence for every row →')} · {link('data/latest.json','Download the complete audit snapshot')} · {link('review.html','Flagged for Review')}</p></section>'''


def analysis_notes():
    """data/analysis.json is static research content: never a probability source."""
    return json.loads((ROOT/'data/analysis.json').read_text())


def live_line(m):
    """Short, honest description of a row's current line for the guidance table."""
    if m is None:
        return '<span class="muted">Not in the current Hotspawn feed</span>',''
    if m['state']!='open':
        return '<span class="muted">Closed (lock or start passed)</span>',''
    if m['probabilities'] is None:
        return ('<span class="muted">No probability · research pick</span>' if m.get('pick') else '<span class="muted">Unresolved</span>'),(m.get('pick') or '')
    p=m['probabilities'];kind='model' if m.get('method')=='model_vrs' else 'market'
    text=f'{e(m["teams"][0])} {p[0]*100:.1f}% · {e(m["teams"][1])} {p[1]*100:.1f}% <span class="muted">({kind})</span>'
    check=m.get('model_check') or {}
    if check.get('status')=='ok':
        text+=f'<div class="model-line">VRS model: {check["probabilities"][0]*100:.1f}% / {check["probabilities"][1]*100:.1f}%</div>'
    return text,(m.get('pick') or 'No directional edge')


def guidance_plans(notes):
    """Every published guidance block, oldest first.

    ``data/analysis.json`` keeps one ``*_guidance`` object per tournament day, in file
    order. The last one is the current day's guidance: the executive summary takes its
    label from it and links to the anchor that ``analysis_page`` gives it, so a new day
    never leaves the front page pointing at a finished day.
    """
    return [(key,notes[key]) for key in notes if key.endswith('_guidance') and isinstance(notes.get(key),dict)]


def latest_guidance(notes):
    plans=guidance_plans(notes)
    return plans[-1][1] if plans else None


def front_page_plan(notes):
    """The guidance block the front page points at.

    ``data/analysis.json`` may name the block the executive summary links to
    (``front_page_plan``). Without that key the newest block is used. This lets
    a later, still-unpriced day be published on the analysis page without
    moving the front page away from the day that is actually being played.
    """
    key=notes.get('front_page_plan')
    plan=notes.get(key) if isinstance(key,str) else None
    if isinstance(plan,dict):
        return plan
    return latest_guidance(notes)


def guidance_href(notes, suffix=''):
    """Use the selected block's actual rendered anchor, never a hardcoded day."""
    plan = front_page_plan(notes)
    for key, candidate in guidance_plans(notes):
        if candidate is plan:
            anchor = {'day_three_guidance': 'guidance', 'day_four_guidance': 'day-four-guidance',
                      'day_five_guidance': 'day-five-guidance'}.get(key)
            if anchor:
                return 'analysis.html#' + anchor + suffix
    return 'analysis.html'


def guidance_anchor(notes):
    """Compatibility helper; one source of truth for the selected day link."""
    return guidance_href(notes).partition('#')[2] or 'guidance'


def guidance_label(notes,fallback='Tournament guidance'):
    plan=front_page_plan(notes)
    return (plan or {}).get('nav_label') or fallback


def guidance_section(data,notes,plan_key='day_three_guidance',section_id='guidance',aria='Day-three guidance'):
    plan=notes.get(plan_key)
    if not plan: return ''
    archive=('<div class="notice info"><strong>Archived pre-match research.</strong> Prices and bracket notes below describe their dated observations, not current picks. Sunday opponent names and the latest research are in the final-day guide above. '+link('picks.html','Use the current pick board →')+'</div>' if plan.get('archived') else '')
    lookup={m['id']:m for m in data['matches']}
    rows=''
    for f in plan.get('fixtures',[]):
        m=lookup.get(f['hotspawn_id'])
        line,pick=live_line(m)
        when=(e(date(m['start']))+' UTC') if m and m.get('start') else ''
        sources=''.join(link(x['url'],x['label']+' ↗') for x in f['sources'])
        if m: sources=link(m['source_url'],'Hotspawn ↗')+link('evidence.html#match-'+m['id'],'Evidence')+sources
        rows+=f'<tr><td><strong>{e(f["label"])}</strong><div class="competition">{e(f["event"])} · {when}</div></td><td>{line}</td><td><span class="pick">{e(pick)}</span><span class="small muted">board pick</span></td><td><span class="pick alt-pick">{e(f["contrarian"])}</span>{tag(f["verdict"],"warning")}</td><td class="review-reason">{e(f["why"])}</td><td class="source-links">{sources}</td></tr>'
    cards=''; any_listed=False
    for f in plan.get('not_listed',[]):
        candidates=[m for m in data['matches'] if f.get('start_utc') and m.get('start')==f['start_utc'] and {norm(t) for t in m['teams']}=={norm(t) for t in f['teams']}]
        current_match=candidates[0] if len(candidates)==1 else None
        points=f.get('points')
        if points and len(points)==2:
            raw=vrs.expected(*points);p=vrs.calibrated(raw)
            model_line=(f'<p><strong>VRS model:</strong> {e(f["teams"][0])} {p*100:.1f}% · {e(f["teams"][1])} {(1-p)*100:.1f}% '
                        f'<span class="muted">(Valve points {points[0]} vs {points[1]}; model estimate, not a market price)</span></p>')
        else:
            model_line=('<p class="muted"><strong>VRS model:</strong> not computable for this fixture. The opponent pair is not '
                        'known yet, so there is nothing to run the model on and no percentage is published.</p>')
        if f.get('model_limitation'):
            model_line='<p class="muted"><strong>Model limitation:</strong> '+e(f['model_limitation'])+'</p>'
        mk=f.get('market')
        market_line=(f'<p><strong>{e(mk["label"])}:</strong> {e(mk["detail"])}</p>' if mk else '')
        market_link=(link(mk['url'],mk.get('link_label','Official market ↗')) if mk else '')
        bk=f.get('book_line')
        book_line=(f'<p><strong>{e(bk["label"])}:</strong> {e(bk["detail"])}</p>' if bk else '')
        book_link=(link(bk['url'],bk.get('link_label','Bookmaker feed ↗')) if bk else '')
        pick_line=(f'<p class="card-pick"><strong>Pick:</strong> <span class="pick">{e(f["pick"])}</span> '
                   f'<span class="muted">{e(f.get("pick_detail",""))}</span></p>' if f.get('pick') else '')
        if mk and mk.get('expires_at'):
            hidden=' hidden' if dt(mk['expires_at'])<=datetime.now(timezone.utc) else ''
            note=mk.get('note') or 'Dated market observation, not a live board quote.'
            receipt_url=mk.get('receipt_url') or REPO+'/blob/main/research/session-e0fd5a32/day5-lines.json'
            pick_line=('<div data-research-quote data-research-observed="'+e(mk.get('observed_at'))+'" data-research-expires="'+e(mk['expires_at'])+'"'+hidden+'>'+pick_line+market_line+'</div>'
                       '<p class="muted small">'+e(note)+' Expires '+e(date(mk['expires_at'],True))+'. '+link(receipt_url,'Historical receipt ↗')+'</p>')
            market_line=''
        if current_match:
            any_listed=True
            current_line,current_pick=live_line(current_match)
            pick_line=('<p><strong>Current board line:</strong> '+link('picks.html','Open the expiry-checked pick board →')+'</p>'
                       +('<p class="card-pick"><strong>Board pick:</strong> <span class="pick">'+e(current_match.get('pick') or '')+'</span> <span class="muted">(row '+e(current_match['id'])+'; the live percentage is on the pick board)</span></p>' if current_match.get('pick') else '')
                       +link('evidence.html#match-'+current_match['id'],'Current evidence →'))
        cards+=f'<article class="panel"><p class="eyebrow muted">{e("Now on the Hotspawn board" if current_match else "Dated fixture research · check current board")}</p><h3>{e(f["label"])} · {e(f["event"])}</h3>{pick_line}{market_line}{book_line}{model_line}<p class="muted">{e(f["timing"])}</p><p>{e(f["why"])}</p><div class="actions">{link(f["hltv_url"],"HLTV match page ↗")}{link(f["standings_url"],f.get("standings_label","Valve standings ↗"))}{market_link}{book_link}{"".join(link(x["url"],x["label"]+" ↗") for x in f["sources"])}</div></article>'
    unpriced=''
    if plan.get('unpriced'):
        unpriced_rows=''.join(
            '<tr><td><strong>'+e(u['label'])+'</strong><div class="competition">'+e(u['when'])+'</div></td>'
            '<td><span class="badge amber">'+e(u['status'])+'</span></td>'
            '<td class="review-reason">'+e(u['limitation'])+'</td>'
            '<td class="source-links">'+''.join(link(s['url'],s['label']+' ↗') for s in u['sources'])+'</td></tr>'
            for u in plan['unpriced'])
        unpriced=('<section class="panel" id="'+e(section_id)+'-unpriced" aria-label="'
                  +e(plan.get('unpriced_label') or 'Unresolved picks and limitations')+'">'
                  '<p class="eyebrow muted">'+e(plan.get('unpriced_label') or 'Unresolved & limitations')+'</p>'
                  '<h3>What still has no price, and why</h3>'
                  '<p class="muted">Nothing below is given a placeholder percentage. Each row states the limitation '
                  'that stopped it being priced, with the source for its schedule or its access check.</p>'
                  '<div class="table-wrap" tabindex="0" role="region" aria-label="Unresolved picks and limitations">'
                  '<table role="table"><caption>Unresolved items, the reason, and the source.</caption><thead><tr>'
                  '<th scope="col">Item</th><th scope="col">Status</th><th scope="col">Limitation</th>'
                  '<th scope="col">Sources</th></tr></thead><tbody>'+unpriced_rows+'</tbody></table></div></section>')
    unverified='<div class="notice"><strong>Explicitly unverified.</strong><ul>'+''.join('<li>'+e(x)+'</li>' for x in plan.get('unverified',[]))+'</ul></div>'
    points=''
    if plan.get('points'):
        points=('<section class="panel" id="'+e(section_id)+'-read"><p class="eyebrow muted">'
                +e(plan.get('points_label') or 'What the sourced facts support')+'</p><ul class="checklist">'
                +''.join('<li><strong>'+e(x['claim'])+'</strong> <span class="muted">'+e(x['detail'])+'</span> '
                         +link(x['source'],'Source ↗')+'</li>' for x in plan['points'])+'</ul></section>')
    table_html=''
    if rows:
        table_html=f'<div class="table-wrap" tabindex="0" role="region" aria-label="{e(aria)}"><table role="table"><caption>Board pick = the market favourite (or our model line where no market exists). Contrarian option = the underdog worth considering, with the reason. Current lines follow the snapshot and expire with their evidence. Strategy commentary is dated research, not a live quote.</caption><thead><tr><th scope="col">Match</th><th scope="col">Current line</th><th scope="col">Board pick</th><th scope="col">Contrarian option</th><th scope="col">Why</th><th scope="col">Sources</th></tr></thead><tbody>{rows}</tbody></table></div>'
    else:
        table_html=('<p class="muted">The fixtures in this guidance block are now on the Hotspawn board; '
                    'the dated research cards below link to the live, expiry-checked board lines.</p>' if any_listed else
                    '<p class="muted">No Hotspawn board row is priced through this guidance table. '
                    'The cards below carry the fixtures that are not listed, with the evidence for each.</p>')
    return f'<section id="{e(section_id)}">{archive}<div class="section-heading"><div><p class="eyebrow muted">{e(plan["date"])}</p><h2>{e(plan["headline"])}</h2><p>{e(plan["summary"])}</p></div>{link("picks.html","Full pick board →")}</div>{table_html}<div class="two-col">{cards}</div>{points}{unpriced}{unverified}</section>'


def analysis_page(data):
    notes=json.loads((ROOT/'data/analysis.json').read_text())
    event=notes['event']
    live={m['id']:m for m in data['matches']}
    body=head('Tournament analysis · thunderpick world championship','What days one to four mean for the final day.','Sourced results, the 9z–Aurora upset and its reversal, and a dated final-day decision guide. Strategy is not a probability input.',data)
    body+='<div class="notice info"><strong>This page is research and strategy, not a pick list.</strong> Picks and probabilities come only from '+link('picks.html','the updated picks page')+'. Every factual line below carries its source link; strategy statements are labelled as analysis. Nothing here is used as a probability input.</div>'
    body+='<nav class="section-nav" aria-label="On this page">'+link('#day-five-guidance',(notes.get('day_five_guidance') or {}).get('nav_label','Day-5 guidance'))+link('#day-five-guidance-unpriced','Final-day limits')+link('#day-four-guidance','Day-4 guidance (record)')+link('#day-four-guidance-unpriced','Day-4 limits')+link('#day-four-results','Day-4 results')+link('#day-three-results','Day-3 results')+link('#guidance','Day-3 guidance (record)')+link('#day-three','Deciders')+link('#day-two','Day-2 results')+link('#day-two-read','Day-2 read')+link('#upset','Upset review')+link('#strategy','Strategy rules')+link('#model-vs-market','Model vs market')+'</nav>'
    body+=f'<section class="panel"><p class="eyebrow muted">Event context</p><h2>{e(event["name"])}</h2><p class="muted">{e(event["location"])} · {e(event["dates"])} · {e(event["prize_pool"])} · {event["teams"]} teams. {e(event["format_note"])}</p><div class="actions">{link(event["url"],"HLTV event page ↗")}{link(event["results_url"],"HLTV results ↗")}{link(event["format_source"],"Format summary ↗")}</div></section>'
    body+='<span id="day-four"></span>'
    body+=guidance_section(data,notes,'day_five_guidance','day-five-guidance','Day-five guidance')
    body+=guidance_section(data,notes,'day_four_guidance','day-four-guidance','Day-four guidance')
    body+=guidance_section(data,notes)
    for day in [notes['day_one'], notes['day_two']]+([notes['day_three_results']] if notes.get('day_three_results') else [])+([notes['day_four_results']] if notes.get('day_four_results') else []):
        rows=''
        for m in day['matches']:
            maps=(e(m['maps']) if m.get('maps') else '<span class="muted">not collected</span>')+(f'<div class="small muted">Veto: {e(m["veto"])}</div>' if m.get('veto') else '')
            stage=f'<div class="competition">{e(m["stage"])}</div>' if m.get('stage') else ''
            note=e(m['detail']) if m.get('detail') else ''
            flag=f'<p class="muted small">Flag: {e(m["flag"])}</p>' if m.get('flag') else ''
            rows+=f'<tr><td><strong>{e(m["winner"])}</strong> <span class="muted">beat</span> {e(m["loser"])}{stage}</td><td>{e(m["score"])}</td><td>{maps}</td><td>{note}{flag}</td><td class="source-links">{link(m["match_url"],"Match ↗")}{link(m["report_url"],"Results ↗")}{link(m["hltv_report_url"],"HLTV report ↗") if m.get("hltv_report_url") else ""}</td></tr>'
        body+=f'<section id="{e(day.get("key") or day["label"].split()[0].lower()+"-"+day["label"].split()[2])}"><div class="section-heading"><div><p class="eyebrow muted">{e(day["label"])}</p><h2>Every result</h2><p>{e(day.get("note","Series scores as published by HLTV."))} Blank cells were not collected, never inferred.</p></div>{link(day["results_url"],"HLTV results ↗")}</div><div class="table-wrap" tabindex="0" role="region" aria-label="{e(day["label"])} results"><table role="table"><caption>{e(day["label"])} results of the Thunderpick World Championship 2026.</caption><thead><tr><th scope="col">Result</th><th scope="col">Score</th><th scope="col">Maps (winner first)</th><th scope="col">Detail</th><th scope="col">Sources</th></tr></thead><tbody>'+rows+'</tbody></table></div></section>'
    if notes.get('day_two_more'):
        more=''.join(f'<li><strong>{e(p["claim"])}</strong> <span class="muted">{e(p["detail"])}</span> '+link(p['source'],'Source ↗')+'</li>' for p in notes['day_two_more']['points'])
        body+=f'<section class="panel" id="day-two-more"><p class="eyebrow muted">Day two · HLTV reports</p><h2>{e(notes["day_two_more"]["headline"])}</h2><ul class="checklist">{more}</ul></section>'
    cards=''
    for point in notes['upset_context']['points']:
        quote=f'<blockquote>{e(point["quote"])}</blockquote>' if point.get('quote') else ''
        cards+=f'<article class="panel"><h3>{e(point["claim"])}</h3>{quote}<p class="muted">{e(point["detail"])}</p>{link(point["source"],"Primary source ↗")}</article>'
    body+=f'<section id="upset"><div class="section-heading"><div><p class="eyebrow muted">Upset review</p><h2>{e(notes["upset_context"]["headline"])}</h2><p>Why the market favourite lost, using sourced facts only.</p></div></div><div class="two-col">'+cards+'</div></section>'
    changed=''.join(f'<li><strong>{e(p["claim"])}</strong> <span class="muted">{e(p["detail"])}</span> '+link(p["source"],'Source ↗')+'</li>' for p in notes['day_two_analysis']['points'])
    body+=f'<section class="panel" id="day-two-read"><p class="eyebrow muted">Day two read</p><h2>{e(notes["day_two_analysis"]["headline"])}</h2><ul class="checklist">'+changed+'</ul></section>'
    day_three=notes['day_three']
    rows=''
    for fixture in day_three['fixtures']:
        fixture_id=str(fixture.get('hotspawn_fixture') or '')
        match=live.get(fixture_id) if fixture_id else None
        if match and match.get('state')=='open' and match.get('probabilities'):
            ix=0 if match['probabilities'][0]>match['probabilities'][1] else 1
            state=('<span class="pick">'+e(match['pick'])+'</span> '+tag(METHOD_TAGS.get(match['method'],'Exchange line'),'gray')
                   +'<div class="small">'+('%.1f%%' % (match['probabilities'][ix]*100))+' · '+e(date(match['start']))+' UTC</div>')
            board=link('picks.html','Live row →')+link('evidence.html#match-'+match['id'],'Evidence →')
        elif match and match.get('pick'):
            state=('<span class="pick research-only">'+e(match['pick'])+'</span> '+tag('Research only','warning')
                   +'<div class="small muted">No probability published</div>')
            board=link('unresolved.html','Live row →')+link('evidence.html#match-'+match['id'],'Evidence →')
        elif match:
            state='<span class="muted">Open, no verified line yet</span>'
            board=link('unresolved.html','Limitations →')
        else:
            state='<span class="muted">Not listed by the Hotspawn feed at the last check, so no pick is generated for it</span>'
            board=link('matches.html','All matches →')
        market='<span class="muted">No market line recorded</span>'
        if fixture.get('market'):
            market=(e(fixture['market']['label'])+'<p class="muted small">'+e(fixture['market']['detail'])+'</p>'
                    +link(fixture['market']['url'],'Official market ↗'))
        start_cell='<span class="muted">time not fixed in the sources read</span>'
        if fixture.get('start_utc'):
            start_cell=e(fixture['start_utc'])+'<span class="small"> UTC</span>'
        rows+=('<tr><td><strong>'+e(fixture['teams'][0])+'</strong> <span class="muted">vs</span> '+e(fixture['teams'][1])
               +'<div class="competition">'+e(fixture['stage'])+'</div></td><td>'+start_cell+'</td><td>'+state+'</td><td>'+market+'</td>'
               +'<td class="source-links">'+link(fixture['hltv_match'],'HLTV fixture ↗')+link(fixture['hotspawn_url'],'Hotspawn feed ↗')+board+'</td></tr>')
    points=''.join(f'<li><strong>{e(p["claim"])}</strong> <span class="muted">{e(p["detail"])}</span> '+link(p["source"],'Source ↗')+'</li>' for p in day_three['points'])
    contrarian=day_three['contrarian']
    body+=(f'<section id="day-three"><div class="section-heading"><div><p class="eyebrow muted">Day three · 16 October 2026</p>'
           f'<h2>{e(day_three["headline"])}</h2><p>The two group deciders, with the live state of each row on this site.</p></div>'
           +link('picks.html','Open the live pick board →')+'</div>'
           '<div class="table-wrap" tabindex="0" role="region" aria-label="Day three fixtures and their live state">'
           '<table role="table"><caption>Day-three fixtures. The pick column is rebuilt from the current snapshot; the market column cites the external line this project uses.</caption>'
           '<thead><tr><th scope="col">Fixture</th><th scope="col">Start</th><th scope="col">Our live pick</th><th scope="col">External line</th><th scope="col">Sources</th></tr></thead>'
           '<tbody>'+rows+'</tbody></table></div>'
           '<div class="two-col"><section class="panel"><p class="eyebrow muted">Read for day three</p><h3>What the sourced facts support</h3><ul class="checklist">'+points+'</ul></section>'
           f'<section class="panel"><p class="eyebrow muted">Contrarian candidate</p><h3>{e(contrarian["pick"])}</h3><p>{e(contrarian["why"])}</p>'
           '<ul class="checklist">'+''.join(f'<li>{e(x)}</li>' for x in contrarian['not_stupid_check'])+'</ul>'
           f'<p class="muted small">{e(contrarian["limits"])}</p></section></div></section>')
    rule_rows=''
    for i,rule in enumerate(notes['strategy']['rules'],1):
        rule_sources=" ".join(link(x["url"],x["label"]) for x in rule.get("sources",[]))
        rule_rows+=f'<tr><td>{i}</td><td><strong>{e(rule["rule"])}</strong><p class="muted">{e(rule["why"])}</p></td><td>{e(rule["verify"])}</td><td>{rule_sources}</td></tr>'
    body+=f'<section id="strategy"><div class="section-heading"><div><p class="eyebrow muted">Strategy</p><h2>{e(notes["strategy"]["headline"])}</h2><p>{e(notes["strategy"]["summary"])}</p></div></div><div class="table-wrap" tabindex="0" role="region" aria-label="Contrarian screening rules"><table role="table"><caption>Contrarian screening rules used on this project; strategy, not verified outcomes.</caption><thead><tr><th scope="col">#</th><th scope="col">Rule</th><th scope="col">How it is verified</th><th scope="col">Sources</th></tr></thead><tbody>'+rule_rows+'</tbody></table></div>'
    body+='<div class="notice"><strong>Explicitly unverified.</strong><ul>'+''.join('<li>'+e(x)+'</li>' for x in notes['strategy']['unverified'])+'</ul></div></section>'
    body+=contrarian_screen(data)
    body+=f'<section class="panel"><p class="eyebrow muted">Keep reading</p><h2>Where the numbers live</h2><ul class="checklist"><li>{link("picks.html","Every open match with its probabilities and pick →")}</li><li>{link("unresolved.html","Research-only picks, unresolved rows and their limitations →")}</li><li>{link("matches.html","The complete Hotspawn feed, including closed entries →")}</li><li>{link("sources.html","Methodology, source health and the calculation policy →")}</li></ul></section>'
    return body


def contrarian_screen(data):
    """Live screens over the current snapshot: underdog band and model/market disagreement."""
    rows=[]
    for m in sorted(data['matches'],key=lambda x:x['start'] or ''):
        if m['state']!='open':continue
        matchup=f'<div class="teams">{e(m["teams"][0])}<span>vs</span>{e(m["teams"][1])}</div><div class="competition">{e(m["competition"])} · {e(date(m["start"]))} UTC</div>'
        if is_research(m) and m.get('pick'):
            sources=link(m['hltv_context'].get('source') if m.get('hltv_context') else 'https://www.hltv.org/ranking/teams','HLTV fixture & ranking ↗')+link('evidence.html#match-'+m['id'],'Evidence')
            rows.append('<tr><td>'+matchup+'</td><td>'+e(m['pick'])+' <span class="muted">(research pick)</span></td><td><span class="muted">No probability</span></td><td>'+tag('Research only','warning')+' '+sources+'</td></tr>')
            continue
        p=m['probabilities']
        if p is None:continue
        ix=0 if p[0]<p[1] else 1
        if not .15<=p[ix]<=.40:continue
        tier=METHOD_LABELS.get(m['method'],m['method'])
        rows.append('<tr><td>'+matchup+'</td><td>'+e(m['teams'][ix])+'</td><td>%.1f%% <span class="muted">vs %.1f%%</span></td><td>%s %s %s</td></tr>'%(p[ix]*100,p[1-ix]*100,tag(tier,METHOD_KIND.get(m['method'],'gray')),link('picks.html','Pick board →'),link('evidence.html#match-'+m['id'],'Evidence')))
    caption='Underdogs priced between 15% and 40% in the current snapshot, plus research-only picks. A screen, not a recommendation: confirm the source and the lock time before acting.'
    empty='<tr><td colspan="4" class="muted">No open match currently sits in the 15–40% underdog band in this snapshot.</td></tr>'
    out='<section id="contrarian"><div class="section-heading"><div><p class="eyebrow muted">Live screen</p><h2>Contrarian candidates from the current snapshot</h2><p>Rebuilt from every refresh. The band is a strategy choice, not a probability claim.</p></div>'+link('unresolved.html','Unresolved queue →')+'</div><div class="table-wrap" tabindex="0" role="region" aria-label="Contrarian candidates"><table role="table"><caption>'+e(caption)+'</caption><thead><tr><th scope="col">Match</th><th scope="col">Underdog side</th><th scope="col">Implied chance</th><th scope="col">Evidence</th></tr></thead><tbody>'+(''.join(rows) or empty)+'</tbody></table></div></section>'
    split=[m for m in model_comparison(data) if not vrs.gap(m)[1] or abs(vrs.gap(m)[0])>=.10]
    srows=''
    for m in split:
        c=m['model_check'];mk=m['probabilities']
        side=m['teams'][0] if c['probabilities'][0]>mk[0] else m['teams'][1]
        srows+='<tr><td><div class="teams">%s<span>vs</span>%s</div><div class="competition">%s · %s UTC</div></td><td>%.1f%% / %.1f%%</td><td>%.1f%% / %.1f%%</td><td>%s%s</td><td class="source-links">%s%s</td></tr>'%(e(m['teams'][0]),e(m['teams'][1]),e(m['competition']),e(date(m['start'])),mk[0]*100,mk[1]*100,c['probabilities'][0]*100,c['probabilities'][1]*100,e(side),' '+tag('Favourite differs','warning') if not vrs.gap(m)[1] else '',link('evidence.html#match-'+m['id'],'Evidence'),link(c['source'],'Valve standings ↗'))
    sempty='<tr><td colspan="5" class="muted">Our model and the market agree within 10 points on every comparable open match in this snapshot.</td></tr>'
    out+='<section id="model-vs-market"><div class="section-heading"><div><p class="eyebrow muted">Live screen</p><h2>Where our model and the market disagree</h2><p>Disagreement is a reason to look closer, not a pick by itself: the market may know about a roster change, stand-in or form the monthly standings miss.</p></div>'+link('sources.html#model','How the model works →')+'</div><div class="table-wrap" tabindex="0" role="region" aria-label="Model and market disagreements"><table role="table"><caption>Open matches where the favourite differs or the gap is at least 10 points. The board pick still follows the market.</caption><thead><tr><th scope="col">Match</th><th scope="col">Market</th><th scope="col">VRS model</th><th scope="col">Model leans to</th><th scope="col">Sources</th></tr></thead><tbody>'+(srows or sempty)+'</tbody></table></div></section>'
    return out


def model_inputs(q):
    if q.get('provider')!='Valve VRS model': return ''
    rows=''.join(f'<tr><td>{e(team)}</td><td>{e(label)}</td><td>#{standing}</td><td>{points}</td><td>{e(chk["note"])}'+(f' ({chk["overlap"]} of 5 players)' if chk.get('overlap') else '')+f'</td><td class="source-links">{link(url,"Valve team detail ↗")}</td></tr>' for team,label,standing,points,chk,url in zip(q['fixture_teams'],q['vrs_teams'],q['standings'],q['points'],q['roster_checks'],q['details_urls']))
    return (f'<p class="notice warning"><strong>Our originated line, not a market price.</strong> Raw Valve expectation {q["raw_expected"][0]*100:.2f}% / {q["raw_expected"][1]*100:.2f}%; after Valve’s published calibration slope {q["calibration_slope"]}: {q["probabilities"][0]*100:.2f}% / {q["probabilities"][1]*100:.2f}%. Data origin: {e(q["standings_origin"])}. Formula: {link(q["formula_source"],"fit.js ↗")} · calibration: {link(q["calibration_source"],"modelfit.png ↗")}.</p>'
        '<div class="table-wrap"><table role="table"><caption>Model inputs from Valve’s official standings.</caption><thead><tr><th scope="col">Hotspawn team</th><th scope="col">Valve label</th><th scope="col">Standing</th><th scope="col">Points</th><th scope="col">Identity check</th><th scope="col">Source</th></tr></thead><tbody>'+rows+'</tbody></table></div>')


def evidence_page(data):
    body=head('Row-by-row verification','The evidence ledger.','Each match, its original facts, every fallback attempt, and the exact calculation inputs.',data)
    raw={str(r['id']):r for r in data.get('fixture_evidence',[])}
    for m in data['matches']:
        q=m['evidence'][0] if m['evidence'] else None
        line=''
        if q:
            p=m['probabilities'] or q['probabilities']
            method=e(METHOD_LABELS.get(m['method'],m['method']))
            tier=''
            if q.get('tier')=='wide_exchange':
                tier=f'<p class="notice warning"><strong>Low-confidence tier.</strong> This quote passed every gate except the 25-point spread ceiling; the published spread is {float(q["spread"]):.2f}. Strict rejection: {e(q.get("strict_rejection"))}</p>'
            line=f'<p class="evidence-status notice info" data-evidence-status data-expires="{e(m.get("expires_at"))}">{"Current evidence at build time; check expiry below." if m["probabilities"] is not None else "Historical evidence only — not a current pick."}</p><p><strong>Method:</strong> {method}. <strong>Calculated probabilities at observation:</strong> {p[0]*100:.1f}% / {p[1]*100:.1f}%. <strong>Our fair decimal lines:</strong> {1/p[0]:.3f} / {1/p[1]:.3f}. These are derived estimates, not offered bets.</p>{tier}<p>Observed: {e(date(q["observed_at"],True))}. Price updated: {e(date(q.get("updated_at"),True)) or "unverified / not supplied"}. Expires: {e(date(m.get("expires_at"),True))}. Source: {link(q["api_url"],q["provider"]+" official API ↗") if q["provider"]!="Valve VRS model" else link(q["url"],"Valve standings of "+q["standings_as_of"]+" ↗")}.</p>{model_inputs(q)}<pre>{e(json.dumps(q,indent=2,ensure_ascii=False))}</pre>'
        else:
            if is_research(m) and m.get('pick'):
                line='<p class="notice warning"><strong>Research-only pick: '+e(m['pick'])+'.</strong> No verified market line exists for this fixture, so <strong>no probability or fair line is published</strong>. '+e(m.get('reason'))+'</p>'
            else:
                line='<p><strong>Probability and fair line:</strong> blank / unverified. '+e(m.get('reason'))+'</p>'
        if m.get('hltv_context'):
            context=m['hltv_context']
            line+='<h3>HLTV context (not a probability)</h3><p>'+e(context['limitation'])+' '+link(context['source'],'HLTV match research ↗')+'</p><pre>'+e(json.dumps(context,indent=2,ensure_ascii=False))+'</pre>'
        if m.get('vrs_research'):
            vresearch=m['vrs_research']
            line+='<h3>Valve standings research (not a probability)</h3><p>One-sided presence in Valve’s official global standings can support a pick only; no percentage is derived from a single points value. '+link(vresearch.get('source'),'Valve standings ↗')+'</p><pre>'+e(json.dumps(vresearch,indent=2,ensure_ascii=False))+'</pre>'
        attempts=''.join(f'<li><strong>{e(a["provider"])} — {e(a["status"])}</strong>: {e(a.get("reason"))} {link(a["url"],"Source ↗")}'+(' <ul>'+''.join('<li>'+e(' vs '.join(c['teams']))+' · '+link(c['url'],'Candidate source (identity unverified)')+'</li>' for c in a.get('candidates',[]))+'</ul>' if a.get('candidates') else '')+'</li>' for a in m['attempts'])
        rejected=''.join('<details><summary>Rejected '+e(a['provider'])+' observation (not a pick)</summary><pre>'+e(json.dumps(a['rejected_quote'],indent=2,ensure_ascii=False))+'</pre></details>' for a in m['attempts'] if a.get('rejected_quote'))
        provenance='<h3>Fixture source receipts</h3><pre>'+e(json.dumps(m.get('fixture_sources',[]),indent=2,ensure_ascii=False))+'</pre>' if m.get('fixture_sources') else ''
        conflicts=[c for c in data.get('fixture_conflicts',[]) if c['id']==m['id']]
        if conflicts: provenance+='<h3>Conflicting official fields — unverified</h3><pre>'+e(json.dumps(conflicts,indent=2,ensure_ascii=False))+'</pre>'
        body+=f'<details class="panel evidence" id="match-{e(m["id"])}"><summary>{e(m["teams"][0])} vs {e(m["teams"][1])} <span class="muted small">· {e(date(m["start"]))} UTC · #{e(m["id"])}</span></summary><div class="evidence-content"><p>{link(m["source_url"],"Hotspawn match/lobby ↗")} · {link(m["feed_url"],"Official fixture API ↗")}</p><p><strong>Source competition:</strong> {e(m["competition"])}. <strong>Source best-of:</strong> {e(m["best_of"])} <span class="muted">{("(unverified / not supplied)" if m["best_of"] is None else "")}</span></p>{line}{provenance}{rejected}<h3>Source attempts</h3><ol>{attempts or "<li>No pre-match research: source timestamps do not show an open pick.</li>"}</ol><h3>Original fixture fields (crowd percentages excluded)</h3><pre>{e(json.dumps(raw.get(m["id"],{}),indent=2,ensure_ascii=False))}</pre></div></details>'
    return body


def build(data,out,now=None):
    now=now or datetime.now(timezone.utc)
    data=copy.deepcopy(data)
    data['built_at']=iso(now)
    for m in data['matches']:
        m['expires_at']=pick_deadline(m,data.get('fixtures_observed_at'))
        if any(m.get(field) and dt(m[field])<=now for field in ('lock','start')):
            m['state']='not_open';m['probabilities']=m['fair_odds']=m['pick']=m['method']=None
            m['reason']='Source start or pick lock has passed. Historical evidence is not a current recommendation.'
        elif m['probabilities'] is not None and (not m['expires_at'] or dt(m['expires_at'])<=now or not fresh(data.get('fixtures_observed_at'),now) or not all(fresh(q['observed_at'],now) and (not q.get('updated_at') or fresh(q['updated_at'],now)) for q in m['evidence'])):
            m['probabilities']=m['fair_odds']=m['pick']=m['method']=None
            m['reason']='Evidence deadline passed (observation/update TTL or bookmaker cutoff); historical observation retained in the ledger.'
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shutil.copytree(ROOT/'site/assets',out/'assets',dirs_exist_ok=True)
    (out/'.nojekyll').touch()
    (out/'data').mkdir(exist_ok=True)
    (out/'data/latest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    with (out/'data/matches.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['hotspawn_id','team_1','team_2','competition','start_utc','lock_utc','state','p_team_1','p_team_2','pick','fair_decimal_1','fair_decimal_2','method','source','price_source','limitation','quote_observed_utc','quote_updated_utc','expires_utc','snapshot_generated_utc','snapshot_fixture_observed_utc','build_utc'])
        for m in data['matches']:
            q=m['evidence'][0] if m['evidence'] else {}
            writer.writerow([m['id'],*m['teams'],m['competition'],m['start'],m['lock'],m['state'],*(m['probabilities'] or ['','']),m['pick'],*(m['fair_odds'] or ['','']),m['method'],m['source_url'],q.get('api_url'),m['reason'],q.get('observed_at'),q.get('updated_at'),m.get('expires_at'),data['generated_at'],data['fixtures_observed_at'],data['built_at']])
    matches=data['matches'];priced=[m for m in matches if m['state']=='open' and m['probabilities'] is not None]
    no_probability=[m for m in matches if m['state']=='open' and m['probabilities'] is None]
    unresolved=[m for m in no_probability if not m.get('pick')]
    nonmarket=non_market_rows(matches)
    pages={'index':('Executive summary',overview(data)),
        'picks':('Updated picks',head('The pick board','Updated CS2 picks.','The market favorite, both win probabilities, and the source behind every pick.',data)+'<nav class="section-nav" aria-label="Pick lists">'+link('picks.html','Updated picks ('+str(len(priced))+')')+('<a href="unresolved.html?status=needs">No percentage (<span data-count="missing">'+str(len(no_probability))+'</span>)</a>')+link('unresolved.html','No market line ('+str(len(nonmarket))+')')+link('matches.html','All matches')+'</nav><div class="notice info">Market-implied probabilities first; where no market exists, our labelled VRS model line. Estimates, not promises. Matches without a market line are listed separately: '+link('unresolved.html',str(len(nonmarket))+' non-market or unresolved matches →')+'</div>'+filters(priced,'priced')+table(priced)),
        'matches':('All matches',head('Complete coverage','Every listed fixture.','All CS2 records returned by the official Hotspawn lobby feed, including not-open entries.',data)+filters(matches,'open')+table(matches)),
        'analysis':('TWC analysis',analysis_page(data)),
        'unresolved':('Unresolved picks',head('Research queue','Unresolved & non-market picks.','Every open match without a usable betting line: our model line, a research-only pick, or an honest blank. Each row states its limitation.',data)+'<nav class="section-nav" aria-label="Pick lists">'+('<a href="unresolved.html?status=needs">No percentage (<span data-count="missing">'+str(len(no_probability))+'</span>)</a>')+link('picks.html','Updated picks ('+str(len(priced))+')')+link('matches.html','All matches')+'</nav><div class="notice">Order of evidence: strict exchange gate → HLTV identity research → Pinnacle bookmaker line → labelled wide-exchange tier → <strong>our VRS model line</strong> (Valve standings, Valve formula, HLTV lineups confirm rosters) → HLTV ranking order as a research-only pick with <strong>no probability</strong>. Thunderpick and GG.BET access is recorded, never bypassed. Name mismatches, stale data, ambiguous rosters and access failures are disclosed below. '+link('sources.html#method','Read the limits →')+'</div>'+filters(nonmarket,'all')+table(nonmarket,True,label='Open matches without a market line')),
        'sources':('Sources and methodology',methodology(data)),
        'evidence':('Evidence ledger',evidence_page(data))}
    review=head('Published irregularities','Flagged for Review.','These limitations are visible, not silently filled in. They do not prevent publication.',data)
    review+='<div class="actions">'+link('unresolved.html','Open unresolved picks →','button')+link('sources.html','Source health & method →')+'</div>'
    review+='<section class="panel" style="margin-top:22px"><h2>Refresh & coverage findings</h2><ul>'
    for flag in data['issues']:
        review+='<li>'+e(flag['message'])+' '+link(flag['source'],'Source ↗')+'</li>'
    review+='</ul><p>'+link('sources.html','Every source attempt, including blocked providers →')+'</p></section>'
    notes=json.loads((ROOT/'data/review-notes.json').read_text())
    review+='<section id="research-findings"><h2>Research findings & audit resolution</h2><p class="muted">Each finding states its own research date and scope. For current access results, see '+link('sources.html','source health')+'. Every limitation is retained for manual review.</p><div class="table-wrap"><table class="source-table" role="table"><caption>Historical research findings and current implementation safeguards; not a claim of 100% probability coverage.</caption><thead><tr><th scope="col">Status</th><th scope="col">Finding / limitation</th><th scope="col">Review sources</th></tr></thead><tbody>'
    for note in notes:
        review+='<tr id="'+e(note['id'])+'"><td data-label="Status">'+tag(note['status'],'gray' if note['status'].startswith('Fixed') else 'warning')+'</td><td data-label="Finding">'+e(note['finding'])+'</td><td data-label="Sources" class="source-links">'+''.join(link(source['url'],source['label']+' ↗') for source in note['sources'])+'</td></tr>'
    review+='</tbody></table></div></section><h2>Row-by-row flags</h2>'
    review+=filters([m for m in matches if m['flags'] or m in no_probability])+table([m for m in matches if m['flags'] or m in no_probability],True)
    pages['review']=('Flagged for Review',review)
    for slug,(title,body) in pages.items():
        if slug in ('matches','picks','unresolved','review'):
            body+='<div id="filter-empty" class="panel empty" hidden>No matches fit these filters. Try another team, event or status.</div><noscript><p class="notice info">JavaScript is off. All rows below are available; filters and live expiry checks require JavaScript. Always check source timestamps and lock times.</p></noscript>'
        (out/(slug+'.html')).write_text(page(slug,title,body,data))
    (out/'404.html').write_text(page('404','Page not found',head('404','Page not found.','Return to the '+link('index.html','executive summary')+' or '+link('picks.html','updated picks')+'.',data),data))
    # Preserve public links from the independently published earlier dashboard.
    aliases={'methodology.html':'sources.html','site/index.html':'../index.html',
             'site/picks.html':'../picks.html','site/unresolved.html':'../unresolved.html',
             'site/review.html':'../review.html','site/methodology.html':'../sources.html'}
    for old,target in aliases.items():
        destination=out/old
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CS2 Scout · Page moved</title><meta http-equiv="refresh" content="0;url='+target+'"></head><body><main><h1>This CS2 Scout page has moved</h1><nav aria-label="Main navigation">'+link(target,'Continue to the current dashboard')+'</nav><p>Existing research and source history are preserved in the repository. This route does not publish an old set of picks.</p></main></body></html>')
    revision=os.environ.get('GITHUB_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    files=[*out.glob('*.html'),*out.glob('site/*.html'),*out.glob('assets/*'),out/'data/latest.json',out/'data/matches.csv']
    manifest={'schema_version':1,'revision':revision,'built_at':data['built_at'],'snapshot_generated_at':data['generated_at'],'rows':len(matches),'files':{str(path.relative_to(out)):hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files) if path.is_file()}}
    (out/'build-info.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Built {len(pages)+1} primary pages + {len(aliases)} legacy redirects; {len(matches)} sourced rows, {len(priced)} with percentages, {len(no_probability)} without percentages, {len(unresolved)} unresolved.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--data',default='data/latest.json');parser.add_argument('--out',default='public')
    args=parser.parse_args();build(json.loads(Path(args.data).read_text()),args.out)
