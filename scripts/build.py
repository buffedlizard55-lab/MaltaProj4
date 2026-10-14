"""Build an accessible, fully static dashboard. No browser-side API dependencies."""
import argparse
import copy
import csv
import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from scripts.core import dt, iso, fresh, HOTSPAWN, FIXTURES, GAMMA, PIN

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
'sources':'<path d="M4 3h11l5 5v13H4zM14 3v6h6M8 13h8m-8 4h5"/>'}
NAV=[('index','Overview'),('picks','Picks'),('matches','All matches'),('review','Review'),('sources','Sources')]


def page(name,title,body,data):
    nav=''.join(f'<a href="{slug}.html"'+(' aria-current="page"' if name==slug or (name=='unresolved' and slug=='review') or (name=='evidence' and slug=='sources') else '')+f'><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[slug]}</svg><span>{label}</span></a>' for slug,label in NAV)
    brand='<span class="brandmark" aria-hidden="true">↗</span><span class="brandname">hotspawn<span>CS2 SCOUT</span></span>'
    observed=data.get('fixtures_observed_at')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#132c28"><meta name="description" content="Independent CS2 pick research for the Hotspawn lobby. External market probabilities, clear sources, and honest coverage limitations."><title>{e(title)} · CS2 Scout</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><script src="assets/app.js" defer></script></head><body data-observed="{e(observed)}">
<a class="skip" href="#main">Skip to content</a><aside class="sidebar"><a class="brand" href="index.html" aria-label="CS2 Scout home">{brand}</a><p class="nav-label">RESEARCH DESK</p><nav class="nav" aria-label="Main navigation">{nav}</nav><div class="sidebar-footer"><p><span class="dot"></span>Automatic checks · every 6h</p><p>External lines. No crowd picks.</p><p>Independent research.<br>Not affiliated with Hotspawn.</p>{link(REPO,'View project ↗')}</div></aside>
<div class="shell"><header class="topbar"><a class="brand mobile-brand" href="index.html" aria-label="CS2 Scout home">{brand}</a><div class="context"><span class="game-tag">CS2</span><span>Counter-Strike 2</span><span class="muted"> / &nbsp; Research dashboard</span></div><span class="refresh">Last check: {e(date(data['last_attempt_at']))} UTC</span></header>
<main id="main"><div id="runtime-stale" class="notice error" role="status" hidden><strong>Snapshot over eight hours old.</strong> Current picks are withheld. The schedule is a target, not a guarantee. Check the {link(REPO+'/actions','refresh workflow')} and {link('sources.html','source status')}.</div>{body}</main>
<footer><p>Independent analysis, not betting advice. Market-implied probabilities are estimates, not guarantees. No bets or Hotspawn picks are placed by this site.</p><div>{link('sources.html','Methodology')}{link('data/latest.json','JSON data')}{link('data/matches.csv','CSV export')}{link(REPO,'GitHub ↗')}</div></footer></div></body></html>'''


def head(kicker,title,desc,data):
    return f'<div class="page-head"><div><p class="eyebrow">{e(kicker)}</p><h1>{e(title)}</h1><p class="muted">{desc}</p></div><span class="date-pill">{e(dt(data["last_attempt_at"]).strftime("%a, %d %b %Y"))}</span></div>'


def probability(m):
    if m['probabilities'] is None:
        return '<div class="probability" aria-label="Unverified probability: blank"></div>'
    a=round(m['probabilities'][0]*100,1);b=round(100-a,1)
    return f'<div class="probability"><div class="prob-pair"><span class="{"fav" if a>b else ""}" aria-label="{e(m["teams"][0])} {a:.1f} percent">{a:.1f}%</span><span class="{"fav" if b>a else ""}" aria-label="{e(m["teams"][1])} {b:.1f} percent">{b:.1f}%</span></div><div class="prob-bar" aria-hidden="true"><i style="width:{a}%"></i></div><div class="prob-label">TEAM 1 / TEAM 2 · CALCULATED</div></div>'


def table(matches,review=False):
    if not matches: return '<div class="panel empty">No matches in this category at the last successful check. See All matches for the retained feed.</div>'
    rows=[]
    for m in matches:
        state='not_open' if m['state']!='open' else ('priced' if m['probabilities'] is not None else 'unresolved')
        evidence=m['evidence'][0] if m['evidence'] else {}
        obs=evidence.get('observed_at','')
        pick=(f'<span class="pick">{e(m["pick"])}</span>'+tag('Bookmaker fallback' if m['method']=='bookmaker_fallback' else 'Exchange line')) if m['pick'] else tag('No directional edge' if m['probabilities'] is not None else ('Unresolved' if state=='unresolved' else 'Not open'),'warning' if state=='unresolved' else 'gray')
        source=link(m['source_url'],'Hotspawn ↗')+link('evidence.html#match-'+m['id'],'Evidence & lines')
        if evidence: source+=link(evidence['api_url'],evidence['provider']+' ↗')
        reason=''
        if review:
            items=[m['reason']] if m.get('reason') else []
            items+=m['flags']
            reason='<td class="review-reason"><ul>'+''.join('<li>'+e(i)+'</li>' for i in dict.fromkeys(items) if i)+'</ul>'+link('evidence.html#match-'+m['id'],'View each attempted source →')+'</td>'
        rows.append(f'''<tr data-match="{e(m['id'])}" data-status="{state}" data-search="{e((' '.join(t or '' for t in m['teams'])+' '+(m['competition'] or '')+' '+m['id']).lower())}" data-event="{e(m['competition'])}" data-lock="{e(m['lock'])}" data-evidence="{e(obs)}"><td class="team-col"><div class="teams">{e(m['teams'][0])}<span>vs</span>{e(m['teams'][1])}</div><div class="competition">{e(m['competition'])} · {e((m['tier'] or '').upper()) or 'Tier unverified'}</div></td><td class="time-cell">{e(date(m['start']))}<span class="small">UTC · locks {e(dt(m['lock']).strftime('%H:%M')) if m['lock'] else 'unverified'}</span></td><td>{probability(m)}</td><td class="pick-cell">{pick}</td>{reason}<td class="source-links">{source}</td></tr>''')
    return '<div class="table-wrap"><table role="table"><caption>Whole-match winner only. Blank percentages = unverified; never a default 50/50. Times UTC.</caption><thead><tr><th scope="col">Match / event</th><th scope="col">Start / lock</th><th scope="col">Win probability</th><th scope="col">Our pick</th>'+('<th scope="col">Limitation / review flag</th>' if review else '')+'<th scope="col">Sources</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'


def filters(matches,default='all'):
    events=sorted({m['competition'] for m in matches if m['competition']})
    states=[('all','All entries'),('open','Open matches'),('priced','With probabilities'),('unresolved','Unresolved'),('not_open','Not open / past')]
    return '<div class="filters"><label class="search" for="search">Search team, tournament or match ID<input id="search" type="search" placeholder="Find a team or match…" autocomplete="off"></label><label for="status">Show<select id="status">'+''.join(f'<option value="{s}"'+(' selected' if s==default else '')+f'>{l}</option>' for s,l in states)+'</select></label><label for="event">Tournament<select id="event"><option value="all">All tournaments</option>'+''.join(f'<option value="{e(x)}">{e(x)}</option>' for x in events)+'</select></label><button id="reset" class="filter-button" type="button">Reset</button><span id="result-count" class="count" role="status" aria-live="polite">'+str(len(matches))+' matches</span></div>'


def overview(data):
    matches=data['matches'];opens=[m for m in matches if m['state']=='open'];priced=[m for m in opens if m['probabilities'] is not None];missing=[m for m in opens if m['probabilities'] is None]
    fallback=sum(m['method']=='bookmaker_fallback' for m in priced)
    percent=round(len(priced)/len(opens)*100) if opens else 0
    next_pick=next((m for m in priced if m['pick']),None)
    next_html='<p class="eyebrow">No verified next pick</p><p>Missing evidence stays visible. Check the unresolved list for each limitation.</p>'
    if next_pick:
        m=next_pick;ix=m['teams'].index(m['pick']);q=m['evidence'][0]
        next_html=f'<div data-next-lock="{e(m["lock"])}" data-next-evidence="{e(q["observed_at"])}"><p class="eyebrow">Next sourced pick · {e(date(m["start"]))} UTC</p><div class="next-teams">{e(m["teams"][0])}<span>vs</span>{e(m["teams"][1])}</div><div class="pick-big">{e(m["pick"])} <span class="numbers">{m["probabilities"][ix]*100:.1f}%</span></div><small>{e(q["provider"])} · market-implied, not guaranteed</small><br>{link("evidence.html#match-"+m["id"],"Review source & calculation →")}</div>'
    body=head('Executive summary','The CS2 briefing.','Every listed match in one place. Independent lines. Clear picks.',data)
    body+=f'<section class="hero" aria-label="Find your picks"><div><div class="eyebrow">Hotspawn lobby intelligence</div><h2>Your next pick.<br>Backed by external lines.</h2><p>{len(priced)} of {len(opens)} open matches have sourced probabilities. We never use Hotspawn’s crowd percentages to choose a winner.</p><div class="actions">{link("picks.html","View updated picks →","button")}{link("unresolved.html","Unresolved picks ↗","button secondary")}</div></div><div class="hero-side">{next_html}</div></section>'
    body+=f'<section class="stats" aria-label="Coverage at last check"><a class="stat" href="matches.html?status=open"><div class="stat-label">Open matches <span>↗</span></div><strong>{len(opens):02d}</strong><span class="stat-foot">{len(matches)} total feed entries</span></a><a class="stat green" href="picks.html"><div class="stat-label">With probabilities <span>↗</span></div><strong>{len(priced):02d}</strong><span class="stat-foot">{percent}% coverage · {fallback} book fallback</span></a><a class="stat amber" href="unresolved.html"><div class="stat-label">Unresolved <span>↗</span></div><strong>{len(missing):02d}</strong><span class="stat-foot">Evidence gaps, never guesses</span></a></section>'
    body+=f'<div class="notice"><strong>Coverage is not the same as certainty.</strong> {len(missing)} open matches still need verifiable lines. Some names do not match across providers, some markets lack usable prices, and HLTV / esportsbook access may be restricted. {link("unresolved.html","See every unresolved match and limitation →")}</div>'
    if data['coverage']!='verified':
        body+='<div class="notice error"><strong>Full current lobby coverage is unverified.</strong> A source failed, changed, or disagreed. '+link('review.html','See source irregularities →')+'</div>'
    body+='<div class="section-heading"><div><h2>Next on the board</h2><p>Upcoming picks, in start-time order. All tiers included.</p></div>'+link('picks.html','All updated picks →')+'</div>'+table(priced[:5])
    body+=f'<div class="freshness">Fixture observation: {e(date(data.get("fixtures_observed_at"),True))} · checks target 00:17, 06:17, 12:17 and 18:17 UTC · {link("sources.html","Refresh health ↗")}</div>'
    body+=f'''<div class="two-col"><section class="panel"><p class="eyebrow muted">How picks are made</p><h2>Evidence before a favorite.</h2><ol class="method-steps"><li><div><strong>Find every Hotspawn CS2 fixture</strong><p>Compare the public lobby’s structured data with its own fixture feed.</p></div></li><li><div><strong>Calculate independent probabilities</strong><p>Validate external series-winner prices. Normalize exchange prices or remove bookmaker margin.</p></div></li><li><div><strong>Research only the gaps</strong><p>Try HLTV, then esportsbook lines. If identity or price cannot be verified, leave it unresolved.</p></div></li></ol>{link('sources.html#method','Read the methodology →')}</section><section class="panel"><p class="eyebrow muted">Coverage notes</p><h2>What needs attention</h2><ul class="checklist"><li><span class="tick">↗</span>{len(matches)-len(opens)} feed entries are not open by sourced timestamps.</li><li><span class="tick">↗</span>Missing series format is left blank, not inferred.</li><li><span class="tick">↗</span>Wide exchange spreads are flagged as low precision.</li><li><span class="tick">↗</span>Prices expire after eight hours or at the pick lock.</li></ul>{link('review.html','Open Flagged for Review →')}</section></div>'''
    return body


def checks_table(data):
    rows=[]
    for s in data['source_checks']:
        detail = (f"HTTP {s.get('http_status','')} · cache age {s.get('cache_age_seconds',0)}s" if s['status']=='ok' else s.get('error','Unverified'))
        rows.append(f'<tr><td data-label="Source"><strong>{e(s["name"])}</strong></td><td data-label="Status"><span class="source-status {"error" if s["status"]!="ok" else ""}">{e(s["status"].upper())}</span></td><td data-label="Observation">{e(date(s.get("observed_at") or s.get("checked_at"),True))}</td><td data-label="Result">{e(detail)}</td><td data-label="Official link" class="source-links">{link(s["url"],"Official endpoint ↗")}</td></tr>')
    return '<div class="table-wrap"><table class="source-table" role="table"><caption>Latest refresh attempt. HTTP success alone does not verify a usable match price.</caption><thead><tr><th>Source</th><th>Status</th><th>Observation</th><th>Result</th><th>Link</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'


def methodology(data):
    return head('Audit trail','Sources & methodology.','Raw observations, transparent calculations, and honest limitations.',data)+checks_table(data)+f'''<section class="panel prose" id="method"><p class="eyebrow muted">Calculation policy · v1</p><h2>One fixture list. Independent probabilities.</h2><p><strong>Discovery:</strong> {link(HOTSPAWN,'Hotspawn CS2 lobby')} establishes which fixtures belong here. Its public hydration data and {link(FIXTURES,'CS2 scheduled fixture API')} are compared by fixture ID. All returned CS2 entries remain visible, including stale “scheduled” records. An array schema or count mismatch is flagged; missing pages are not silently ignored.</p><p><strong>Identity:</strong> only exact case/punctuation-normalized team pairs and exact UTC starts are accepted. Polymarket’s own published team abbreviations may map to Hotspawn names; those team records are retained with the evidence. No fuzzy name matching, guessed team aliases, academy/main-team conflation, or assumed start-time corrections. Duplicate candidates are rejected. Known Hotspawn series format, if supplied, must agree with the external source. Where it is not supplied, it remains blank.</p><h2>Primary picks → research fallback</h2><ol><li>Discover CS2 from {link(GAMMA+'/sports','Polymarket’s sports registry')}, paginate every active event page, then validate the whole-match moneyline. Closed, live, map-only, handicap, totals, stale and malformed markets cannot supply a pick.</li><li>Only unresolved matches enter fallback research: try {link('https://www.hltv.org/matches','HLTV')} first. HLTV is a specialist source, not an official betting operator. Current automation may be denied. Ranks and fan votes are not probabilities; no uncalibrated rank-to-win formula is deployed.</li><li>Try {link(PIN+'/sports/12/markets/straight','Pinnacle’s public esports lines')} with its fixture feed, period 0, a pending parent match, open two-way moneyline and valid future cutoff. Then check {link('https://thunderpick.io/esports/cs2-betting','Thunderpick')} and {link('https://gg.bet/en/esports/counter-strike','GG.BET')} for remaining gaps. Their access restrictions or missing validated adapters are recorded separately. Access controls are not bypassed.</li><li>If none establishes a verified price, probabilities and fair odds stay blank. {link('unresolved.html','Unresolved picks')} gives the reason and every attempted source. There is no claim that a pick can always be generated.</li></ol><h2>Our lines: derived, not bookmaker quotes</h2><p>For decimal odds <code>d₁, d₂</code>, compute <code>qᵢ = 1 / dᵢ</code>, then <code>pᵢ = qᵢ / (q₁ + q₂)</code>. The overround is <code>q₁ + q₂ − 1</code>. American odds convert to decimal using <code>1 + A/100</code> for positive A, or <code>1 + 100/|A|</code> for negative A. Our fair decimal line is <code>1 / pᵢ</code>.</p><p>For two exchange outcome prices <code>x₁, x₂</code>, use <code>pᵢ = xᵢ / (x₁ + x₂)</code>. This is market-implied analysis, not an independently calibrated statistical forecast or a tradable quote. It excludes trading fees. We keep the primary accepted source; fallback lines do not overwrite primary picks or pretend to be a multi-book consensus.</p><p>A directional pick is the team with the larger probability; exactly equal verified prices get “no directional edge.” Unknown matches never default to 50/50. Display percentages are rounded to one decimal and complement to 100; downloadable data keeps full precision.</p><h2>Quality and freshness gates</h2><ul><li>Evidence must be no more than eight hours old, using both observation time (adjusted for HTTP cache Age) and exchange market update time. A market update is not proof of a recent trade.</li><li>Exchange liquidity must be at least $100, with a valid two-sided bid/ask and spread no greater than 25 percentage points. Spreads over 10 points are flagged as low precision. These are conservative project policy thresholds, not validated accuracy guarantees.</li><li>Bookmaker overround must fall between −2% and 25%. Pinnacle does not supply a price-change timestamp in this response; that limitation is shown. One bookmaker is not consensus.</li><li>Lock times come from Hotspawn’s feed. Recommendations are withheld at lock, not only at match start. Not-open records are not claimed to be completed results.</li><li>Schedule: every six hours at :17 UTC via {link(REPO+'/actions','GitHub Actions')}. GitHub may delay jobs or disable inactive public-repository schedules. No four-to-eight-hour delivery guarantee is possible. The last successful snapshot is retained on failure, with a prominent stale warning, and never relabeled fresh.</li></ul><h2>Verification scope</h2><p>Every displayed match fact is traced to the official Hotspawn response. Every accepted price retains the official operator’s raw fields and timestamp. Calculated probabilities are explicitly derived. We checked the initial snapshot row by row with executable assertions and source links; future data is verified by the same schema, identity, market-type, freshness and arithmetic rules. This does not certify team rosters, the true chance of winning, bookmaker accuracy, or every website on the internet.</p><p>{link('evidence.html','Inspect evidence for every row →')} · {link('data/latest.json','Download the complete audit snapshot')} · {link('review.html','Flagged for Review')}</p></section>'''


def evidence_page(data):
    body=head('Row-by-row verification','The evidence ledger.','Each match, its original facts, every fallback attempt, and the exact calculation inputs.',data)
    raw={str(r['id']):r for r in data.get('fixture_evidence',[])}
    for m in data['matches']:
        q=m['evidence'][0] if m['evidence'] else None
        line=''
        if q:
            p=m['probabilities'] or q['probabilities']
            line=f'<p><strong>Calculated probabilities:</strong> {p[0]*100:.1f}% / {p[1]*100:.1f}%. <strong>Our fair decimal lines:</strong> {1/p[0]:.3f} / {1/p[1]:.3f}. These are derived estimates, not offered bets.</p><p>Observed: {e(date(q["observed_at"],True))}. Price updated: {e(date(q.get("updated_at"),True)) or "unverified / not supplied"}. Source: {link(q["api_url"],q["provider"]+" official API ↗")}.</p><pre>{e(json.dumps(q,indent=2,ensure_ascii=False))}</pre>'
        else:
            line='<p><strong>Probability and fair line:</strong> blank / unverified. '+e(m.get('reason'))+'</p>'
        attempts=''.join(f'<li><strong>{e(a["provider"])} — {e(a["status"])}</strong>: {e(a.get("reason"))} {link(a["url"],"Official source ↗")}'+(' <ul>'+''.join('<li>'+e(' vs '.join(c['teams']))+' · '+link(c['url'],'Candidate source (identity unverified)')+'</li>' for c in a.get('candidates',[]))+'</ul>' if a.get('candidates') else '')+'</li>' for a in m['attempts'])
        body+=f'<details class="panel evidence" id="match-{e(m["id"])}"><summary>{e(m["teams"][0])} vs {e(m["teams"][1])} <span class="muted small">· {e(date(m["start"]))} UTC · #{e(m["id"])}</span></summary><div class="evidence-content"><p>{link(m["source_url"],"Hotspawn match/lobby ↗")} · {link(m["feed_url"],"Official fixture API ↗")}</p><p><strong>Source competition:</strong> {e(m["competition"])}. <strong>Source best-of:</strong> {e(m["best_of"])} <span class="muted">{("(unverified / not supplied)" if m["best_of"] is None else "")}</span></p>{line}<h3>Source attempts</h3><ol>{attempts or "<li>No pre-match research: source timestamps do not show an open pick.</li>"}</ol><h3>Original fixture fields (crowd percentages excluded)</h3><pre>{e(json.dumps(raw.get(m["id"],{}),indent=2,ensure_ascii=False))}</pre></div></details>'
    return body


def build(data,out,now=None):
    now=now or datetime.now(timezone.utc)
    data=copy.deepcopy(data)
    for m in data['matches']:
        if m['lock'] and dt(m['lock'])<=now:
            m['state']='not_open';m['probabilities']=m['fair_odds']=m['pick']=None
        elif m['probabilities'] is not None and (not fresh(data.get('fixtures_observed_at'),now) or not all(fresh(q['observed_at'],now) and (not q.get('updated_at') or fresh(q['updated_at'],now)) for q in m['evidence'])):
            m['probabilities']=m['fair_odds']=m['pick']=None
            m['reason']='Evidence expired after eight hours; historical observation retained in the ledger.'
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shutil.copytree(ROOT/'site/assets',out/'assets',dirs_exist_ok=True)
    (out/'.nojekyll').touch()
    (out/'data').mkdir(exist_ok=True)
    (out/'data/latest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    with (out/'data/matches.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['hotspawn_id','team_1','team_2','competition','start_utc','lock_utc','state','p_team_1','p_team_2','pick','fair_decimal_1','fair_decimal_2','method','source','price_source','limitation'])
        for m in data['matches']:
            writer.writerow([m['id'],*m['teams'],m['competition'],m['start'],m['lock'],m['state'],*(m['probabilities'] or ['','']),m['pick'],*(m['fair_odds'] or ['','']),m['method'],m['source_url'],m['evidence'][0]['api_url'] if m['evidence'] else '',m['reason']])
    matches=data['matches'];priced=[m for m in matches if m['state']=='open' and m['probabilities'] is not None];unresolved=[m for m in matches if m['state']=='open' and m['probabilities'] is None]
    pages={'index':('Executive summary',overview(data)),
        'picks':('Updated picks',head('The pick board','Updated CS2 picks.','The market favorite, both win probabilities, and the source behind every pick.',data)+'<div class="notice info">These are calculated market-implied probabilities, not promises. Missing matches are not hidden: '+link('unresolved.html',str(len(unresolved))+' unresolved matches →')+'</div>'+filters(priced)+table(priced)),
        'matches':('All matches',head('Complete coverage','Every listed fixture.','All CS2 records returned by the official Hotspawn lobby feed, including not-open entries.',data)+filters(matches)+table(matches)),
        'unresolved':('Unresolved picks',head('Research queue','Unresolved picks.','No verified line, no invented percentage. Every gap stays on the board.',data)+'<div class="notice">Primary exchange evidence is attempted first. Only missing picks enter HLTV → Pinnacle → Thunderpick → GG.BET fallback research. Name mismatches, stale data and access failures are disclosed below. '+link('sources.html#method','Read the limits →')+'</div>'+filters(unresolved)+table(unresolved,True)),
        'sources':('Sources and methodology',methodology(data)),
        'evidence':('Evidence ledger',evidence_page(data))}
    review=head('Published irregularities','Flagged for Review.','These limitations are visible, not silently filled in. They do not prevent publication.',data)
    review+='<div class="actions">'+link('unresolved.html','Open unresolved picks →','button')+link('sources.html','Source health & method →')+'</div>'
    review+='<section class="panel" style="margin-top:22px"><h2>Refresh & coverage findings</h2><ul>'
    for flag in data['issues']:
        review+='<li>'+e(flag['message'])+' '+link(flag['source'],'Official source ↗')+'</li>'
    review+='</ul><p>'+link('sources.html','Every source attempt, including blocked providers →')+'</p></section>'
    review+=filters([m for m in matches if m['flags'] or m in unresolved])+table([m for m in matches if m['flags'] or m in unresolved],True)
    pages['review']=('Flagged for Review',review)
    for slug,(title,body) in pages.items():
        if slug in ('matches','picks','unresolved','review'):
            body+='<div id="filter-empty" class="panel empty" hidden>No matches fit these filters. Try another team, event or status.</div><noscript><p class="notice info">JavaScript is off. All rows below are available; filters and live expiry checks require JavaScript. Always check source timestamps and lock times.</p></noscript>'
        (out/(slug+'.html')).write_text(page(slug,title,body,data))
    (out/'404.html').write_text(page('404','Page not found',head('404','Page not found.','Return to the '+link('index.html','executive summary')+' or '+link('picks.html','updated picks')+'.',data),data))
    print(f'Built {len(pages)+1} pages; {len(matches)} sourced rows, {len(priced)} priced, {len(unresolved)} unresolved.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--data',default='data/latest.json');parser.add_argument('--out',default='public')
    args=parser.parse_args();build(json.loads(Path(args.data).read_text()),args.out)
