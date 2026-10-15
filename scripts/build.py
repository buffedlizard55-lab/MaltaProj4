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
from scripts.core import dt, iso, fresh, pick_deadline, HOTSPAWN, FIXTURES, GAMMA, PIN, IDENTITIES as IDENTITY_REGISTER
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
'analysis':'<path d="M4 20V10m5 10V4m5 16v-7m5 7V7"/>'}
NAV=[('index','Overview'),('picks','Picks'),('matches','All matches'),('analysis','TWC analysis'),('review','Review'),('sources','Sources')]


def page(name,title,body,data):
    nav=''.join(f'<a href="{slug}.html"'+(' aria-current="page"' if name==slug or (name=='unresolved' and slug=='picks') or (name=='evidence' and slug=='sources') else '')+f'><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[slug]}</svg><span>{label}</span></a>' for slug,label in NAV)
    brand='<span class="brandmark" aria-hidden="true"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m5 19 14-14M6 5h13v13"/></svg></span><span class="brandname">hotspawn<span>CS2 SCOUT</span></span>'
    observed=data.get('fixtures_observed_at')
    coverage_rows=[{k:m.get(k) for k in ('id','state','start','lock','expires_at')} | {'priced':m['probabilities'] is not None,
        'model':m.get('method')=='model_vrs',
        'research':m['probabilities'] is None and bool(m.get('pick')) and m.get('method')=='research_rank'} for m in data['matches']]
    coverage_json=json.dumps(coverage_rows,separators=(',',':')).replace('<','\\u003c')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#132c28"><meta name="description" content="Independent CS2 pick research for the Hotspawn lobby. External market probabilities, clear sources, and honest coverage limitations."><title>{e(title)} · CS2 Scout</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><script src="assets/app.js" defer></script></head><body data-observed="{e(observed)}"><script type="application/json" id="coverage-data">{coverage_json}</script>
<a class="skip" href="#main">Skip to content</a><aside class="sidebar"><a class="brand" href="index.html" aria-label="CS2 Scout home">{brand}</a><p class="nav-label">RESEARCH DESK</p><nav class="nav" aria-label="Main navigation">{nav}</nav><div class="sidebar-footer"><p><span class="dot"></span>Automatic checks · every 2h</p><p>External lines + our VRS model. No crowd picks.</p><p>Independent research.<br>Not affiliated with Hotspawn.</p>{link(REPO,'View project ↗')}</div></aside>
<div class="shell"><header class="topbar"><a class="brand mobile-brand" href="index.html" aria-label="CS2 Scout home">{brand}</a><div class="context"><span class="game-tag">CS2</span><span>Counter-Strike 2</span><span class="muted"> / &nbsp; Research dashboard</span></div><span class="refresh">Last check: {e(date(data['last_attempt_at']))} UTC</span></header>
<main id="main"><div id="runtime-stale" class="notice error" role="status" hidden><strong>Snapshot expired or timestamp unverified.</strong> Current picks are withheld. The schedule is a target, not a guarantee. Check the {link(REPO+'/actions','refresh workflow')} and {link('sources.html','source status')}.</div><noscript><div class="notice error"><strong>Live expiry checks require JavaScript.</strong> Treat numeric entries as dated observations, not current recommendations. Each line shows its observation and expiry; no automatic current-time check is possible with JavaScript off.</div></noscript>{body}</main>
<footer><p>Independent research; not affiliated with Hotspawn or betting operators. Not betting advice. Market-implied probabilities are estimates, not guarantees. No bets or Hotspawn picks are placed by this site.</p><div>{link('sources.html','Methodology')}{link('data/latest.json','JSON data')}{link('data/matches.csv','CSV export')}{link('build-info.json','Build receipt')}{link(REPO,'GitHub ↗')}</div></footer></div></body></html>'''


def head(kicker,title,desc,data):
    return f'<div class="page-head"><div><p class="eyebrow">{e(kicker)}</p><h1>{e(title)}</h1><p class="muted">{desc}</p></div><span class="date-pill">{e(dt(data["last_attempt_at"]).strftime("%a, %d %b %Y"))}</span></div>'


METHOD_LABELS={'exchange':'Exchange line','bookmaker_fallback':'Bookmaker line','exchange_wide':'Wide exchange · low confidence','model_vrs':'Our VRS model line · no market','research_rank':'Research pick · no market line'}
METHOD_TAGS={'exchange':'Exchange line','bookmaker_fallback':'Bookmaker line','exchange_wide':'Wide line · low confidence','model_vrs':'Our model line','research_rank':'Research only'}
METHOD_KIND={'exchange':'gray','bookmaker_fallback':'gray','exchange_wide':'warning','model_vrs':'model','research_rank':'warning'}
MARKET_METHODS=('exchange','bookmaker_fallback','exchange_wide')


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
        model=f'<div class="model-line">VRS model: {x:.1f}% / {100-x:.1f}%'+(' · <strong>favourite differs</strong>' if not check.get('same_favourite') else '')+'</div>'
    return f'<div class="probability"><div class="prob-team-labels"><span>{e(m["teams"][0])}</span><span>{e(m["teams"][1])}</span></div><div class="prob-pair"><span class="{"fav" if a>b else ""}" aria-label="{e(m["teams"][0])} {a:.1f} percent">{a:.1f}%</span><span class="{"fav" if b>a else ""}" aria-label="{e(m["teams"][1])} {b:.1f} percent">{b:.1f}%</span></div><div class="prob-bar" aria-hidden="true"><i style="width:{a}%"></i></div><div class="prob-label">{label} · {m["fair_odds"][0]:.2f} / {m["fair_odds"][1]:.2f}</div>{model}</div>'


def table(matches,review=False,label='Match table'):
    if not matches: return '<div class="panel empty">No matches in this category at the last successful check. See All matches for the retained feed.</div>'
    rows=[]
    for m in sorted(matches,key=lambda item:(item['state']!='open', (dt(item['start']).timestamp() if item['state']=='open' else -dt(item['start']).timestamp()) if item.get('start') else float('inf'),item['id'])):
        state='not_open' if m['state']!='open' else ('priced' if m['probabilities'] is not None else ('research' if m.get('method')=='research_rank' and m.get('pick') else 'unresolved'))
        evidence=m['evidence'][0] if m['evidence'] else {}
        obs=evidence.get('observed_at','')
        research_only=' research-only' if m['method']=='research_rank' else ''
        pick=(f'<span class="pick{research_only}">{e(m["pick"])}</span>'+tag(METHOD_TAGS.get(m['method'],'Exchange line'),METHOD_KIND.get(m['method'],'gray'))) if m['pick'] else tag('No directional edge' if m['probabilities'] is not None else ('Unresolved' if state=='unresolved' else 'Not open'),'warning' if state=='unresolved' else 'gray')
        source=link(m['source_url'],'Hotspawn ↗')+link('evidence.html#match-'+m['id'],'Evidence & lines')
        if evidence and evidence.get('provider')=='Valve VRS model':
            source+=link(evidence['url'],'Valve standings ↗')
        elif evidence: source+=link(evidence['api_url'],evidence['provider']+' ↗')
        if m.get('hltv_context') and m['method'] in ('research_rank','model_vrs'):
            source+=link(m['hltv_context'].get('source'),'HLTV fixture & lineups ↗' if m['method']=='model_vrs' else 'HLTV fixture & ranking ↗')
        if evidence:
            source+=f'<span class="quote-time">Observed {e(date(obs))} UTC<br>Expires {e(date(m.get("expires_at")))} UTC</span>'
        elif m['method']=='research_rank':
            source+=f'<span class="quote-time">No price quote. Ranking context observed {e(date((m.get("hltv_context") or {}).get("observed_at")))} UTC</span>'
        reason=''
        if review:
            items=[m['reason']] if m.get('reason') else []
            items+=m['flags']
            reason='<td class="review-reason"><ul>'+''.join('<li>'+e(i)+'</li>' for i in dict.fromkeys(items) if i)+'</ul>'+link('evidence.html#match-'+m['id'],'View each attempted source →')+'</td>'
        rows.append(f'''<tr data-match="{e(m['id'])}" data-status="{state}" data-search="{e((' '.join(t or '' for t in m['teams'])+' '+(m['competition'] or '')+' '+m['id']).lower())}" data-event="{e(m['competition'])}" data-start="{e(m['start'])}" data-lock="{e(m['lock'])}" data-expires="{e(m.get('expires_at'))}" data-evidence="{e(obs)}"><td class="team-col"><div class="teams">{e(m['teams'][0])}<span>vs</span>{e(m['teams'][1])}</div><div class="competition">{e(m['competition'])} · {e((m['tier'] or '').upper()) or 'Tier unverified'}</div></td><td class="time-cell">{e(date(m['start']))}<span class="small">UTC · locks {e(dt(m['lock']).strftime('%H:%M')) if m['lock'] else 'unverified'}</span></td><td>{probability(m)}</td><td class="pick-cell">{pick}</td>{reason}<td class="source-links">{source}</td></tr>''')
    return '<div class="table-wrap" tabindex="0" role="region" aria-label="'+e(label)+'"><table role="table"><caption>Whole-match winner only. Blank percentages = unverified; never a default 50/50. Times UTC.</caption><thead><tr><th scope="col">Match / event</th><th scope="col">Start / lock</th><th scope="col">Win probability</th><th scope="col">Our pick</th>'+('<th scope="col">Limitation / review flag</th>' if review else '')+'<th scope="col">Sources</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'


def filters(matches,default='all'):
    events=sorted({m['competition'] for m in matches if m['competition']})
    states=[('all','All entries'),('open','Open matches'),('priced','With probabilities'),('research','Research-only pick'),('unresolved','Unresolved'),('not_open','Not open / past')]
    return '<div class="filters"><label class="search" for="search">Search team, tournament or match ID<input id="search" type="search" placeholder="Find a team or match…" autocomplete="off"></label><label for="status">Show<select id="status">'+''.join(f'<option value="{s}"'+(' selected' if s==default else '')+f'>{l}</option>' for s,l in states)+'</select></label><label for="event">Tournament<select id="event"><option value="all">All tournaments</option>'+''.join(f'<option value="{e(x)}">{e(x)}</option>' for x in events)+'</select></label><button id="reset" class="filter-button" type="button">Reset</button><span id="result-count" class="count" role="status" aria-live="polite">'+str(len(matches))+' matches</span></div>'


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
    body=head('Executive summary','The CS2 briefing.','Every listed match in one place. External lines first, our own model line where no market exists, a clear pick for each.',data)
    body+=f'<section class="hero" aria-label="Find your picks"><div><div class="eyebrow">Hotspawn lobby intelligence</div><h2>Your next pick.<br>Backed by external lines.</h2><p><span data-count="priced">{len(priced)}</span> of <span data-count="open">{len(opens)}</span> open matches have a win probability: <span data-count="market">{len(market)}</span> from betting markets and <span data-count="model">{len(model)}</span> from our Valve-standings model. <span data-count="researched">{len(researched)}</span> more carry a research pick and <span data-count="unresolved">{len(unresolved)}</span> have none. Hotspawn’s crowd percentages are never used.</p><div class="actions">{link("picks.html","View updated picks →","button")}{link("analysis.html#day-three","Day-3 guidance ↗","button secondary")}</div></div><div class="hero-side">{next_html}</div></section>'
    body+=f'''<section class="panel start-here" id="start-here" aria-label="Start here"><p class="eyebrow muted">Start here · tap a card</p><h2>Where the picks are</h2><div class="start-grid"><a class="start-card" href="picks.html"><strong>Updated picks</strong><span>Every open match with a probability: market lines first, our model line where no market exists.</span></a><a class="start-card" href="#unresolved-summary"><strong>Unresolved & limitations</strong><span>Picks without a market line, research-only picks and anything still unresolved, with the reason.</span></a><a class="start-card" href="analysis.html#day-three"><strong>Day-3 guidance</strong><span>Day-2 review and Friday's contrarian-but-not-stupid picks, with sources.</span></a><a class="start-card" href="matches.html"><strong>All matches</strong><span>The complete Hotspawn feed, including closed entries.</span></a></div><p class="start-note">On a phone: the bottom bar jumps between Overview, Picks, All matches, Analysis, Review and Sources. Each match is a card with the pick on top, so no zooming or horizontal scrolling is needed.</p></section>'''
    body+=f'<section class="stats" aria-label="Coverage at last check" id="coverage"><a class="stat" href="matches.html?status=open"><div class="stat-label">Open matches <span>↗</span></div><strong data-count="open">{len(opens):02d}</strong><span class="stat-foot">{len(matches)} total feed entries</span></a><a class="stat green" href="picks.html"><div class="stat-label">With probabilities <span>↗</span></div><strong data-count="priced">{len(priced):02d}</strong><span class="stat-foot"><span data-count="percent">{percent}</span>% of open · {len(market)} market · {len(model)} model</span></a><a class="stat amber" href="unresolved.html"><div class="stat-label">No market line <span>↗</span></div><strong>{len(nonmarket):02d}</strong><span class="stat-foot">{len(model)} model line(s) · {len(researched)} research pick(s) · {len(unresolved)} unresolved</span></a></section>'
    if model:
        body+=f'<div class="notice info"><strong>Our own lines fill the market gaps.</strong> {len(model)} open match(es) have no usable betting line, so the probability is <strong>our originated line</strong>: Valve’s official Regional Standings points run through Valve’s own published win-expectation formula and calibration. It is labelled on every row and never presented as a market price. {link("sources.html#model","How the model works and how it compares with the market →")}</div>'
    if researched:
        body+=f'<div class="notice info"><strong>Research-only picks, clearly labelled.</strong> {len(researched)} open match(es) could not be priced by a market or our model, so the pick comes from HLTV-verified fixture identity and ranking order, with <strong>no percentage</strong>. {link("unresolved.html","See each one and why →")}</div>'
    body+=f'<div class="notice"><strong>Coverage is not the same as certainty.</strong> {len(unresolved)} open match(es) have no supported pick at all. Names can differ across providers, some markets lack usable prices, model inputs can be ambiguous, and HLTV or esportsbook access may be restricted. {link("unresolved.html","See every non-market and unresolved match →")}</div>'
    if data['coverage']!='verified':
        body+='<div class="notice error"><strong>Full current lobby coverage is unverified.</strong> A source failed, changed, or disagreed. '+link('review.html','See source irregularities →')+'</div>'
    if any(i.get('code')=='audit_quarantine' for i in data.get('issues',[])):
        body+='<div class="notice error"><strong>Some picks were withheld.</strong> The independent row audit could not reproduce at least one row, so its pick is not published. '+link('review.html','See which rows and why →')+'</div>'
    body+='<div class="section-heading"><div><h2>Next on the board</h2><p>Upcoming picks with a probability, in start-time order.</p></div>'+link('picks.html','All updated picks →')+'</div>'+table(priced[:5])
    body+='<section id="unresolved-summary"><div class="section-heading"><div><p class="eyebrow muted">Executive summary · evidence gaps</p><h2>Picks without a market line, and unresolved matches</h2><p>Model lines carry <strong>our</strong> percentage, labelled as a model estimate. Research-only rows carry a sourced pick with <strong>no percentage</strong>. Unresolved rows have neither. Each row lists its limitation. Blank means unverified, never 50/50.</p></div>'+link('unresolved.html','Full research queue →')+'</div>'+table(nonmarket,True,label='Open matches without a market line')+'</section>'
    body+=f'<div class="freshness">Fixture observation: {e(date(data.get("fixtures_observed_at"),True))} · automatic checks every two hours at :17 UTC (GitHub may delay them) · {link("sources.html","Refresh health ↗")}</div>'
    body+=f'''<div class="two-col"><section class="panel" id="how-picks"><p class="eyebrow muted">How picks are made</p><h2>Evidence before a favorite.</h2><ol class="method-steps"><li><div><strong>Find every Hotspawn CS2 fixture</strong><p>Compare the public lobby’s structured data with its own fixture feed.</p></div></li><li><div><strong>Price it from the market</strong><p>Validated exchange prices (Polymarket) or a bookmaker line (Pinnacle), normalized or de-margined.</p></div></li><li><div><strong>Originate our own line where no market exists</strong><p>Valve’s official standings points through Valve’s published formula and calibration, with HLTV lineups confirming each roster.</p></div></li><li><div><strong>Then research, never guess</strong><p>HLTV-verified identity and ranking order as a research-only pick with no percentage. Anything left stays unresolved.</p></div></li></ol>{link('sources.html#method','Read the methodology →')}{link('analysis.html','TWC review & contrarian screen →')}</section><section class="panel"><p class="eyebrow muted">Coverage notes</p><h2>What needs attention</h2><ul class="checklist"><li><span class="tick">↗</span>{len(matches)-len(opens)} feed entries are not open by sourced timestamps.</li><li><span class="tick">↗</span>Missing series format is left blank, not inferred.</li><li><span class="tick">↗</span>Wide exchange spreads are flagged as low precision; model lines are labelled; research-only picks carry no percentage.</li><li><span class="tick">↗</span>Prices expire at the earliest source TTL, start, lock or bookmaker cutoff.</li></ul>{link('review.html','Open Flagged for Review →')}</section></div>'''
    return body


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
        agree=sum(1 for m in rows if m['model_check'].get('same_favourite'))
        table_rows=''.join('<tr><td>'+e(m['teams'][0])+' <span class="muted">vs</span> '+e(m['teams'][1])+'<div class="competition">'+e(m['competition'])+' · '+e(date(m['start']))+' UTC</div></td><td>%.1f%%</td><td>%.1f%%</td><td>%+.1f</td><td>%s</td><td class="source-links">%s%s</td></tr>'%(
            m['probabilities'][0]*100,m['model_check']['probabilities'][0]*100,(m['model_check']['probabilities'][0]-m['probabilities'][0])*100,
            'Yes' if m['model_check'].get('same_favourite') else '<strong>No</strong>',link('evidence.html#match-'+m['id'],'Evidence'),link(m['model_check']['source'],'Valve standings ↗')) for m in rows)
        body=f'<p><strong>Live check against the market:</strong> across the {len(rows)} open matches that have both a market line and a model line in this snapshot, the mean absolute difference is <strong>{sum(diffs)/len(diffs)*100:.1f} percentage points</strong> and the favourite agrees in <strong>{agree} of {len(rows)}</strong>. Disagreements are flagged on the pick board and on the {link("analysis.html#model-vs-market","contrarian screen")}.</p><div class="table-wrap" tabindex="0" role="region" aria-label="Model versus market"><table role="table"><caption>First-named team’s chance: market line vs our VRS model line. The pick always follows the market where one exists.</caption><thead><tr><th scope="col">Match</th><th scope="col">Market</th><th scope="col">Model</th><th scope="col">Diff (pts)</th><th scope="col">Same favourite</th><th scope="col">Sources</th></tr></thead><tbody>'+table_rows+'</tbody></table></div>'
    return f'''<section class="panel prose" id="model"><p class="eyebrow muted">Originated lines · v1</p><h2>Our own line where no market exists: the VRS model.</h2><p><strong>Inputs (official):</strong> Valve’s {link(standings_url,"Regional Standings")} of {e(as_of)}, published in Valve’s own GitHub repository. The <em>Points</em> column is each team’s Glicko rank value ({link(blob+"/model/report.js","report.js")} prints <code>glickoTeam.rank()</code>).</p><p><strong>Formula (Valve’s, not ours):</strong> Valve evaluates its model by giving every match an expected win rate from the points difference ({link(blob+"/model/fit.js","fit.js")}, <code>priorWinExpectation</code>, rating deviation 75, using {link(blob+"/model/glicko.js","glicko.js")}). That procedure reduces exactly to <code>E = 1 / (1 + 10^(−g·(Pa − Pb)/400))</code> with <code>g = 1/√(1 + 3q²·75²/π²)</code> and <code>q = ln10/400</code>. Our test suite ports Valve’s procedure line by line and checks the closed form to 12 decimals.</p><p><strong>Calibration (Valve’s published fit):</strong> Valve’s {link(blob+"/modelfit.png","model-fit chart")} reports observed = 0.7986 × expected + 0.126, so the raw expectation is overconfident. We apply the published slope symmetrically, <code>p = 0.5 + 0.7986·(E − 0.5)</code>, so both sides sum to 100%.</p><p><strong>Identity:</strong> exact team labels or the sourced alias register only. Valve’s standings repeat some labels for older rosters, so a label is used only when it is unique or when the current HLTV lineup shares at least three players with exactly one listed roster, Valve’s own roster-continuity rule ({link(blob+"/model/team.js","team.js")}). Otherwise no model line is produced.</p><p><strong>Where it is used:</strong> only when no market line passes its gates. Beside market-priced rows it is shown for comparison and never changes the pick. Every model row is recomputed by the build validator and by the independent auditor.</p>{body}<p class="fineprint">Limitations: standings update monthly, so recent roster changes, stand-ins, map pools, LAN/online and best-of format are not modelled. It is a rating-based estimate, not a market price and not a guarantee.</p></section>'''


def methodology(data):
    return head('Audit trail','Sources & methodology.','Raw observations, transparent calculations, and honest limitations.',data)+checks_table(data)+model_section(data)+f'''<section class="panel prose" id="method"><p class="eyebrow muted">Calculation policy · v1</p><h2>One fixture list. Independent probabilities.</h2><p><strong>Discovery:</strong> {link(HOTSPAWN,'Hotspawn CS2 lobby')} establishes which fixtures belong here. Its CS2 hydration data, the {link("https://play.hotspawn.com/lobby","general lobby")} and {link(FIXTURES,'CS2 scheduled fixture API')} are compared by fixture ID and primary fields. All returned CS2 entries remain visible, including stale “scheduled” records. Schema, ID-set and field mismatches are flagged; missing pages are not silently ignored. Conflicting rows cannot supply picks. Partial discovery retains still-open previous-only entries with unverified membership; a wrong-game or unexpected empty result never erases the last good inventory.</p><p><strong>Identity:</strong> only exact case/punctuation-normalized team pairs and exact UTC starts are accepted. Polymarket’s own published team abbreviations may map to Hotspawn names; those team records are retained with the evidence. The small {link(REPO+"/blob/main/data/identities.json","verified alias register")} covers only explicitly registered organization labels ({e(', '.join(i['canonical'] for i in IDENTITY_REGISTER))}), with primary links and narrow CS2 scope recorded. BetBoom labels were checked on {link("https://betboom.team/","the organization’s official site")}. No fuzzy name matching, guessed team aliases, academy/main-team conflation, or assumed start-time corrections. Duplicate candidates are rejected. Known Hotspawn series format, if supplied, must agree with the external source. Where it is not supplied, it remains blank.</p><h2>Primary picks → research fallback</h2><ol><li>Discover CS2 from {link(GAMMA+'/sports','Polymarket’s sports registry')}, paginate every active event page, then validate the whole-match moneyline. Closed, live, map-only, handicap, totals, stale and malformed markets cannot supply a pick.</li><li>Only unresolved matches enter fallback research: try {link('https://www.hltv.org/matches','HLTV')} first. HLTV is a specialist source, not an official betting operator. Current automation may be denied. Ranks and fan votes are not probabilities; no uncalibrated rank-to-win formula is deployed.</li><li>Try {link(PIN+'/sports/12/markets/straight','Pinnacle’s public esports lines')} with its fixture feed, period 0, a pending parent match, open two-way moneyline and valid future cutoff. Then check {link('https://thunderpick.io/esports/cs2-betting','Thunderpick')} and {link('https://gg.bet/en/esports/counter-strike','GG.BET')} for remaining gaps. Their access restrictions or missing validated adapters are recorded separately. Access controls are not bypassed.</li><li><strong>Labelled wide-quote tier.</strong> For a fixture that would otherwise have no pick at all, an exchange quote that fails only the 25-point spread ceiling can still be accepted — but only when the market is open, accepting orders, has a fresh observation and update, is genuinely two-sided, and holds at least $100 of liquidity. The real spread is published, the row is flagged low confidence, the strict rejection is retained, and a 60-point ceiling still applies. This is a coverage decision, not a claim of precision.</li><li><strong>Our originated line.</strong> If no market line passes its gates, the {link('#model','VRS model')} prices the match from Valve’s official standings with Valve’s own formula and calibration, after confirming each roster against the HLTV lineup. The row is labelled as our model line, never as a market price. Pinnacle is tried before the wide exchange tier because a sharp bookmaker line outranks a wide quote.</li><li><strong>Research-only tier, no numbers.</strong> A fixture with no usable line and no model line may receive a pick from an exact HLTV fixture identity (same opponent pair and UTC start) when both teams’ world rankings are exposed on that page, or when one team is ranked and HLTV explicitly marks the opponent “Unranked” on the same page with consistent VRS badges. The better-ranked team becomes the pick, the HLTV link is published, the row is labelled research-only, and probabilities and fair odds stay <em>blank</em>. This is a ranking-order signal, never a market probability.</li><li>If neither tier applies, probabilities, fair odds and the pick all stay blank. {link('unresolved.html','Unresolved picks')} gives the reason and every attempted source. There is no claim that a pick can always be generated, and no default 50/50.</li></ol><h2>Our lines: calculated, not guessed</h2><p>For decimal odds <code>d₁, d₂</code>, compute <code>qᵢ = 1 / dᵢ</code>, then <code>pᵢ = qᵢ / (q₁ + q₂)</code>. The overround is <code>q₁ + q₂ − 1</code>. American odds convert to decimal using <code>1 + A/100</code> for positive A, or <code>1 + 100/|A|</code> for negative A. Our fair decimal line is <code>1 / pᵢ</code>.</p><p>For two exchange outcome prices <code>x₁, x₂</code>, use <code>pᵢ = xᵢ / (x₁ + x₂)</code>. This is market-implied analysis, not an independently calibrated statistical forecast or a tradable quote. It excludes trading fees. We keep the primary accepted source; fallback lines do not overwrite primary picks or pretend to be a multi-book consensus.</p><p>A directional pick is the team with the larger probability; exactly equal verified prices get “no directional edge.” Unknown matches never default to 50/50. Display percentages are rounded to one decimal and complement to 100; downloadable data keeps full precision.</p><h2>Quality and freshness gates</h2><ul><li>Evidence must be no more than eight hours old, using both observation time (adjusted for HTTP cache Age) and exchange market update time. One expiry deadline also includes fixture age, match start, Hotspawn lock and bookmaker cutoff, and is enforced in the build and browser. A market update is not proof of a recent trade.</li><li>Exchange liquidity must be at least $100, with a valid two-sided bid/ask and spread no greater than 25 percentage points. Spreads over 10 points are flagged as low precision. These are conservative project policy thresholds, not validated accuracy guarantees.</li><li>Bookmaker overround must fall between −2% and 25%. Pinnacle does not supply a price-change timestamp in this response; that limitation is shown. One bookmaker is not consensus.</li><li>Lock times come from Hotspawn’s feed. Recommendations are withheld at lock, not only at match start. Not-open records are not claimed to be completed results.</li><li>Schedule: every two hours at :17 UTC via {link(REPO+'/actions','GitHub Actions')}, so a delayed run still lands well inside the eight-hour evidence window. GitHub may delay jobs or disable inactive public-repository schedules; no exact delivery guarantee is possible. The last successful snapshot is retained on failure, with a prominent stale warning, and never relabeled fresh.</li></ul><h2>Verification scope</h2><p>Every displayed match fact is traced to the official Hotspawn response; this verifies what the source reported, not that contradictory source records are correct. Every accepted price retains the official operator’s raw fields and timestamp. Calculated probabilities are explicitly derived. We checked the initial snapshot row by row with executable assertions and source links; future data is verified by the same schema, identity, market-type, freshness and arithmetic rules. This does not certify team rosters, the true chance of winning, bookmaker accuracy, or every website on the internet.</p><p>{link('evidence.html','Inspect evidence for every row →')} · {link('data/latest.json','Download the complete audit snapshot')} · {link('review.html','Flagged for Review')}</p></section>'''


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


def day_three(data,notes):
    plan=notes.get('day_three')
    if not plan: return ''
    lookup={m['id']:m for m in data['matches']}
    rows=''
    for f in plan['fixtures']:
        m=lookup.get(f['hotspawn_id'])
        line,pick=live_line(m)
        when=(e(date(m['start']))+' UTC') if m and m.get('start') else ''
        sources=''.join(link(x['url'],x['label']+' ↗') for x in f['sources'])
        if m: sources=link(m['source_url'],'Hotspawn ↗')+link('evidence.html#match-'+m['id'],'Evidence')+sources
        rows+=f'<tr><td><strong>{e(f["label"])}</strong><div class="competition">{e(f["event"])} · {when}</div></td><td>{line}</td><td><span class="pick">{e(pick)}</span><span class="small muted">board pick</span></td><td><span class="pick alt-pick">{e(f["contrarian"])}</span>{tag(f["verdict"],"warning")}</td><td class="review-reason">{e(f["why"])}</td><td class="source-links">{sources}</td></tr>'
    cards=''
    for f in plan.get('not_listed',[]):
        raw=vrs.expected(*f['points']);p=vrs.calibrated(raw)
        cards+=f'<article class="panel"><p class="eyebrow muted">Not on Hotspawn yet</p><h3>{e(f["label"])} · {e(f["event"])}</h3><p><strong>VRS model:</strong> {e(f["teams"][0])} {p*100:.1f}% · {e(f["teams"][1])} {(1-p)*100:.1f}% <span class="muted">(Valve points {f["points"][0]} vs {f["points"][1]}; model estimate, not a market price)</span></p><p class="muted">{e(f["timing"])}</p><p>{e(f["why"])}</p><div class="actions">{link(f["hltv_url"],"HLTV match page ↗")}{link(f["standings_url"],"Valve standings ↗")}{"".join(link(x["url"],x["label"]+" ↗") for x in f["sources"])}</div></article>'
    unverified='<div class="notice"><strong>Explicitly unverified.</strong><ul>'+''.join('<li>'+e(x)+'</li>' for x in plan.get('unverified',[]))+'</ul></div>'
    return f'<section id="day-three"><div class="section-heading"><div><p class="eyebrow muted">{e(plan["date"])}</p><h2>{e(plan["headline"])}</h2><p>{e(plan["summary"])}</p></div>{link("picks.html","Full pick board →")}</div><div class="table-wrap" tabindex="0" role="region" aria-label="Day-three guidance"><table role="table"><caption>Board pick = the market favourite (or our model line where no market exists). Contrarian option = the underdog worth considering, with the reason. Lines refresh every two hours.</caption><thead><tr><th scope="col">Match</th><th scope="col">Current line</th><th scope="col">Board pick</th><th scope="col">Contrarian option</th><th scope="col">Why</th><th scope="col">Sources</th></tr></thead><tbody>{rows}</tbody></table></div><div class="two-col">{cards}</div>{unverified}</section>'


def analysis_page(data):
    notes=json.loads((ROOT/'data/analysis.json').read_text())
    event=notes['event']
    body=head('TWC review · thunderpick world championship','Day 1, day 2 and what to pick on day 3.','Sourced results, the 9z–Aurora upset, and contrarian-but-not-stupid guidance that updates with every refresh.',data)
    body+='<div class="notice info"><strong>Research and strategy, built on the pick board.</strong> Board picks and probabilities come only from '+link('picks.html','the updated picks page')+'. Every factual line below carries its source link; strategy statements are labelled as analysis. Nothing here feeds a probability.</div>'
    body+='<nav class="section-nav" aria-label="On this page">'+link('#day-three','Day-3 guidance')+link('#day-two','Day-2 review')+link('#day-one','Day-1 review')+link('#strategy','Strategy rules')+link('#model-vs-market','Model vs market')+'</nav>'
    body+=f'<section class="panel"><p class="eyebrow muted">Event context</p><h2>{e(event["name"])}</h2><p class="muted">{e(event["location"])} · {e(event["dates"])} · {e(event["prize_pool"])} · {event["teams"]} teams. {e(event["format_note"])}</p><div class="actions">{link(event["url"],"HLTV event page ↗")}{link(event["results_url"],"HLTV results ↗")}{link(event["format_source"],"Format summary ↗")}</div></section>'
    body+=day_three(data,notes)
    if notes.get('day_two'):
        rows=''
        for m in notes['day_two']['matches']:
            rows+=f'<tr><td><strong>{e(m["winner"])}</strong> <span class="muted">beat</span> {e(m["loser"])}<div class="competition">{e(m["stage"])}</div></td><td>{e(m["score"])}</td><td>{e(m["maps"])}<div class="small muted">Veto: {e(m["veto"])}</div></td><td class="review-reason">{e(m["detail"])}</td><td class="source-links">{link(m["match_url"],"Match ↗")}{link(m["report_url"],"Report ↗")}</td></tr>'
        body+=f'<section id="day-two"><div class="section-heading"><div><p class="eyebrow muted">Day two · {e(notes["day_two"]["date"])}</p><h2>Every day-two result</h2><p>Series, maps and vetoes as published by HLTV.</p></div>{link(notes["day_two"]["results_url"],"HLTV results ↗")}</div><div class="table-wrap" tabindex="0" role="region" aria-label="Day-two results"><table role="table"><caption>Day-two results of the Thunderpick World Championship 2026 group stage.</caption><thead><tr><th scope="col">Result</th><th scope="col">Score</th><th scope="col">Maps &amp; veto</th><th scope="col">Key detail</th><th scope="col">Sources</th></tr></thead><tbody>'+rows+'</tbody></table></div>'
        take=''.join(f'<li><strong>{e(p["claim"])}</strong> <span class="muted">{e(p["detail"])}</span> '+link(p['source'],'Source ↗')+'</li>' for p in notes['day_two_takeaways']['points'])
        body+=f'<section class="panel"><p class="eyebrow muted">Takeaways</p><h2>{e(notes["day_two_takeaways"]["headline"])}</h2><ul class="checklist">{take}</ul></section></section>'
    rows=''
    for m in notes['day_one']['matches']:
        maps=e(m['maps']) if m['maps'] else '<span class="muted">not collected</span>'
        rows+=f'<tr><td><strong>{e(m["winner"])}</strong> <span class="muted">beat</span> {e(m["loser"])}</td><td>{e(m["score"])}</td><td>{maps}</td><td class="source-links">{link(m["match_url"],"Match ↗")}{link(m["report_url"],"Report ↗")}</td></tr>'
    body+=f'<section id="day-one"><div class="section-heading"><div><p class="eyebrow muted">Day one · 14 October 2026</p><h2>Every day-one result</h2><p>Series scores as published by HLTV. Blank cells were not collected, never inferred.</p></div>{link(notes["day_one"]["results_url"],"HLTV results ↗")}</div><div class="table-wrap" tabindex="0" role="region" aria-label="Day-one results"><table role="table"><caption>Day-one results of the Thunderpick World Championship 2026 group stage.</caption><thead><tr><th scope="col">Result</th><th scope="col">Score</th><th scope="col">Maps</th><th scope="col">Sources</th></tr></thead><tbody>'+rows+'</tbody></table></div></section>'
    cards=''
    for point in notes['upset_context']['points']:
        quote=f'<blockquote>{e(point["quote"])}</blockquote>' if point.get('quote') else ''
        cards+=f'<article class="panel"><h3>{e(point["claim"])}</h3>{quote}<p class="muted">{e(point["detail"])}</p>{link(point["source"],"Primary source ↗")}</article>'
    body+=f'<section id="upset"><div class="section-heading"><div><p class="eyebrow muted">Upset review</p><h2>{e(notes["upset_context"]["headline"])}</h2><p>Why the market favourite lost, using sourced facts only.</p></div></div><div class="two-col">'+cards+'</div></section>'
    rule_rows=''
    for i,rule in enumerate(notes['strategy']['rules'],1):
        rule_rows+=f'<tr><td>{i}</td><td><strong>{e(rule["rule"])}</strong><p class="muted">{e(rule["why"])}</p></td><td>{e(rule["verify"])}</td></tr>'
    body+=f'<section id="strategy"><div class="section-heading"><div><p class="eyebrow muted">Strategy</p><h2>{e(notes["strategy"]["headline"])}</h2><p>{e(notes["strategy"]["summary"])}</p></div></div><div class="table-wrap" tabindex="0" role="region" aria-label="Contrarian screening rules"><table role="table"><caption>Contrarian screening rules used on this project; strategy, not verified outcomes.</caption><thead><tr><th scope="col">#</th><th scope="col">Rule</th><th scope="col">How it is verified</th></tr></thead><tbody>'+rule_rows+'</tbody></table></div>'
    body+='<div class="notice"><strong>Explicitly unverified.</strong><ul>'+''.join('<li>'+e(x)+'</li>' for x in notes['strategy']['unverified'])+'</ul></div></section>'
    body+=contrarian_screen(data)
    return body


def contrarian_screen(data):
    """Live screens over the current snapshot: underdog band and model/market disagreement."""
    rows=[]
    for m in sorted(data['matches'],key=lambda x:x['start'] or ''):
        if m['state']!='open':continue
        matchup=f'<div class="teams">{e(m["teams"][0])}<span>vs</span>{e(m["teams"][1])}</div><div class="competition">{e(m["competition"])} · {e(date(m["start"]))} UTC</div>'
        if m.get('method')=='research_rank' and m.get('pick'):
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
    split=[m for m in model_comparison(data) if not m['model_check'].get('same_favourite') or abs(m['model_check']['difference'])>=.10]
    srows=''
    for m in split:
        c=m['model_check'];mk=m['probabilities']
        side=m['teams'][0] if c['probabilities'][0]>mk[0] else m['teams'][1]
        srows+='<tr><td><div class="teams">%s<span>vs</span>%s</div><div class="competition">%s · %s UTC</div></td><td>%.1f%% / %.1f%%</td><td>%.1f%% / %.1f%%</td><td>%s%s</td><td class="source-links">%s%s</td></tr>'%(e(m['teams'][0]),e(m['teams'][1]),e(m['competition']),e(date(m['start'])),mk[0]*100,mk[1]*100,c['probabilities'][0]*100,c['probabilities'][1]*100,e(side),' '+tag('Favourite differs','warning') if not c.get('same_favourite') else '',link('evidence.html#match-'+m['id'],'Evidence'),link(c['source'],'Valve standings ↗'))
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
            if m.get('method')=='research_rank' and m.get('pick'):
                line='<p class="notice warning"><strong>Research-only pick: '+e(m['pick'])+'.</strong> No verified market line exists for this fixture, so <strong>no probability or fair line is published</strong>. '+e(m.get('reason'))+'</p>'
            else:
                line='<p><strong>Probability and fair line:</strong> blank / unverified. '+e(m.get('reason'))+'</p>'
        if m.get('hltv_context'):
            context=m['hltv_context']
            line+='<h3>HLTV context (not a probability)</h3><p>'+e(context['limitation'])+' '+link(context['source'],'HLTV match research ↗')+'</p><pre>'+e(json.dumps(context,indent=2,ensure_ascii=False))+'</pre>'
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
    matches=data['matches'];priced=[m for m in matches if m['state']=='open' and m['probabilities'] is not None];unresolved=[m for m in matches if m['state']=='open' and m['probabilities'] is None]
    nonmarket=non_market_rows(matches)
    pages={'index':('Executive summary',overview(data)),
        'picks':('Updated picks',head('The pick board','Updated CS2 picks.','The market favorite, both win probabilities, and the source behind every pick.',data)+'<nav class="section-nav" aria-label="Pick lists">'+link('picks.html','Updated picks')+link('unresolved.html','Unresolved picks')+link('matches.html','All matches')+'</nav><div class="notice info">Market-implied probabilities first; where no market exists, our labelled VRS model line. Estimates, not promises. Matches without a market line are listed separately: '+link('unresolved.html',str(len(nonmarket))+' non-market or unresolved matches →')+'</div>'+filters(priced,'priced')+table(priced)),
        'matches':('All matches',head('Complete coverage','Every listed fixture.','All CS2 records returned by the official Hotspawn lobby feed, including not-open entries.',data)+filters(matches,'open')+table(matches)),
        'analysis':('TWC analysis',analysis_page(data)),
        'unresolved':('Unresolved picks',head('Research queue','Unresolved & non-market picks.','Every open match without a usable betting line: our model line, a research-only pick, or an honest blank. Each row states its limitation.',data)+'<nav class="section-nav" aria-label="Pick lists">'+link('picks.html','Updated picks')+link('unresolved.html','Unresolved picks')+link('matches.html','All matches')+'</nav><div class="notice">Order of evidence: strict exchange gate → HLTV identity research → Pinnacle bookmaker line → labelled wide-exchange tier → <strong>our VRS model line</strong> (Valve standings, Valve formula, HLTV lineups confirm rosters) → HLTV ranking order as a research-only pick with <strong>no probability</strong>. Thunderpick and GG.BET access is recorded, never bypassed. Name mismatches, stale data, ambiguous rosters and access failures are disclosed below. '+link('sources.html#method','Read the limits →')+'</div>'+filters(nonmarket,'all')+table(nonmarket,True,label='Open matches without a market line')),
        'sources':('Sources and methodology',methodology(data)),
        'evidence':('Evidence ledger',evidence_page(data))}
    review=head('Published irregularities','Flagged for Review.','These limitations are visible, not silently filled in. They do not prevent publication.',data)
    review+='<div class="actions">'+link('unresolved.html','Open unresolved picks →','button')+link('sources.html','Source health & method →')+'</div>'
    review+='<section class="panel" style="margin-top:22px"><h2>Refresh & coverage findings</h2><ul>'
    for flag in data['issues']:
        review+='<li>'+e(flag['message'])+' '+link(flag['source'],'Source ↗')+'</li>'
    review+='</ul><p>'+link('sources.html','Every source attempt, including blocked providers →')+'</p></section>'
    notes=json.loads((ROOT/'data/review-notes.json').read_text())
    review+='<section id="research-findings"><h2>Research findings & audit resolution</h2><p class="muted">Research checked 15 October 2026. For current access results, see '+link('sources.html','source health')+'. Every limitation is retained for manual review.</p><div class="table-wrap"><table class="source-table" role="table"><caption>Historical research findings and current implementation safeguards; not a claim of 100% probability coverage.</caption><thead><tr><th scope="col">Status</th><th scope="col">Finding / limitation</th><th scope="col">Review sources</th></tr></thead><tbody>'
    for note in notes:
        review+='<tr id="'+e(note['id'])+'"><td data-label="Status">'+tag(note['status'],'gray' if note['status'].startswith('Fixed') else 'warning')+'</td><td data-label="Finding">'+e(note['finding'])+'</td><td data-label="Sources" class="source-links">'+''.join(link(source['url'],source['label']+' ↗') for source in note['sources'])+'</td></tr>'
    review+='</tbody></table></div></section><h2>Row-by-row flags</h2>'
    review+=filters([m for m in matches if m['flags'] or m in unresolved])+table([m for m in matches if m['flags'] or m in unresolved],True)
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
    print(f'Built {len(pages)+1} primary pages + {len(aliases)} legacy redirects; {len(matches)} sourced rows, {len(priced)} priced, {len(unresolved)} unresolved.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--data',default='data/latest.json');parser.add_argument('--out',default='public')
    args=parser.parse_args();build(json.loads(Path(args.data).read_text()),args.out)
