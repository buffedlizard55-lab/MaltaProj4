"""Render a fully static, source-linked dashboard; usable without JavaScript."""
import csv
import html
import json
from datetime import timedelta
from pathlib import Path
from collect import DATA, ROOT, parse_time, iso

OUT = ROOT / 'docs'
REPO = 'https://github.com/buffedlizard55-lab/MaltaProj4'


def esc(value):
    return html.escape('' if value is None else str(value), quote=True)


def link(url, text):
    if not url or not str(url).startswith(('https://', 'data/', 'picks.html', 'review.html', 'sources.html', 'unresolved.html')):
        return ''
    return f'<a href="{esc(url)}">{esc(text)} ↗</a>'


def time_label(t):
    return parse_time(t).strftime('%d %b · %H:%M UTC') if t else 'Unverified time'


def badge(text, cls=''):
    return f'<span class="badge {cls}">{esc(text)}</span>'


def row_html(r):
    p = r['probabilities']
    teams = r['teams']
    method = r['method']
    kind = {'market': ('Market-derived', 'green'), 'model': ('Research model', 'amber')}.get(method, ('Unresolved' if r['state'] != 'locked' else 'Locked / past', 'muted'))
    chances = ''.join(f'<div class="team-line"><span>{esc(t)}</span><strong class="probability">{p[i]*100:.1f}%</strong></div>' if p else f'<div class="team-line"><span>{esc(t)}</span><span aria-label="Unverified probability" class="blank">—</span></div>' for i,t in enumerate(teams))
    bar = f'<div class="splitbar probability" aria-hidden="true"><i style="width:{p[0]*100:.1f}%"></i></div>' if p else ''
    pick = esc(r['pick']) if r['pick'] else ('No lean' if p else 'No verified pick')
    explanation = ''.join(f'<li>{esc(x)}</li>' for x in r['limitations'])
    sources = link(r['fixture_source'], 'Hotspawn fixture')
    evidence = ''
    for e in r['evidence']:
        sources += link(e['url'], e['source'])
        if e.get('prices'):
            evidence += f'<p>Observed share prices ({esc(" / ".join(teams))}): {esc(" / ".join(str(v) for v in e["prices"]))}. Normalized proportionally to 100%. Market updated {esc(time_label(e["updated_at"]))}. Reported liquidity: ${e["liquidity"]:,.2f}.</p>'
            evidence += link(e['api_url'], 'Official market API')
        if e.get('ratings'):
            evidence += f'<p>Valve points ({esc(time_label(e["as_of"]))}): ' + '; '.join(f'{esc(v["name"])} {v["points"]} · listed roster: {esc(v["roster"])}' for v in e['ratings']) + '.</p>'
        if p:
            evidence += '<p class="fair">Our fair decimal line (1 / probability): ' + ' / '.join(f'{1/v:.2f}' for v in p) + '. Calculated, not an offered sportsbook price.</p>'
    attempts = ''.join(f'<li>{link(a["url"], a["source"])} — {esc(a["result"])}</li>' for a in r['attempts'])
    details = f'<details><summary>Evidence & limitations</summary>{evidence}<ul>{explanation}</ul>'
    if attempts:
        details += '<h4>Resolution trail</h4><ol>' + attempts + '</ol>'
    details += f'<p>Fixture checked {esc(time_label(r["fixture_verified_at"]))}. Hotspawn status: {esc(r["source_status"])}. Best of: {esc(r["best_of"]) or "unverified"}. Lock: {esc(time_label(r["lock_at"]))}.</p></details>'
    return f'''<tr id="match-{esc(r['id'])}" data-state="{esc(r['state'])}" data-method="{esc(method)}" data-tier="{esc(r['tier'])}" data-lock="{esc(r['lock_at'])}" data-search="{esc(' '.join(teams) + ' ' + (r['tournament'] or ''))}">
<td data-label="Match"><div class="match-meta">{esc(time_label(r['start_at']))} · {esc((r['tier'] or '?').upper())} tier</div><h3>{esc(teams[0])} <span class="versus">vs</span> {esc(teams[1])}</h3><div class="tournament">{esc(r['tournament'])}</div><a class="permalink" href="picks.html#match-{esc(r['id'])}">#{esc(r['id'])}</a></td>
<td data-label="Win probability">{chances}{bar}<span class="expiry-note">Snapshot expired or match locked — refresh required.</span></td>
<td data-label="Our pick">{badge(*kind)}<strong class="decision">{pick}</strong>{details}</td>
<td data-label="Sources" class="row-sources">{sources}</td></tr>'''


def table(rows, filters=False):
    controls = '''<form class="filters" role="search" onsubmit="return false"><label>Find a match<input id="search" type="search" placeholder="Team or tournament" autocomplete="off"></label><label>Show<select id="status"><option value="open">Open at refresh</option><option value="all">All source fixtures</option><option value="market">Market-derived picks</option><option value="model">Research-model picks</option><option value="unresolved">Unresolved</option><option value="locked">Locked / past</option></select></label><label>Tier<select id="tier"><option value="all">All tiers</option><option value="s">S tier</option><option value="a">A tier</option><option value="b">B tier</option><option value="c">C tier</option><option value="d">D tier</option></select></label><button type="reset">Reset</button></form><p id="result-count" class="small" aria-live="polite"></p>''' if filters else ''
    if not rows:
        return '<div class="empty"><h3>Nothing to list here.</h3><p>See <a href="picks.html">all matches</a> for the complete source inventory.</p></div>'
    return controls + '<div class="table-wrap"><table class="match-table"><caption class="sr-only">CS2 matches, calculated probabilities, picks and official sources</caption><thead><tr><th scope="col">Match & schedule</th><th scope="col">Win probability</th><th scope="col">Our pick & analysis</th><th scope="col">Official sources</th></tr></thead><tbody>' + ''.join(row_html(r) for r in rows) + '</tbody></table></div><p id="no-results" class="empty" hidden>No matches match these filters. Try clearing the search or selecting all fixtures.</p>'


def shell(page, title, subtitle, content, data):
    nav = [('index.html','Overview'), ('picks.html','All picks'), ('unresolved.html','Unresolved'), ('review.html','Flagged for Review'), ('sources.html','Sources & method')]
    navhtml = ''.join(f'<a href="{url}" {"aria-current=page" if page == url else ""}>{text}</a>' for url,text in nav)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="Source-linked CS2 picks for the Hotspawn lobby. Market probabilities, research fallbacks and transparent coverage gaps."><title>{esc(title)} · Spawn Signal</title><link rel="stylesheet" href="assets/style.css"><script defer src="assets/app.js"></script></head>
<body data-updated="{esc(data['fixture_checked_at'])}"><a href="#main" class="skip">Skip to content</a><header><div class="topbar"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">S<span>↗</span></span><span>SPAWN<span class="brand-light"> SIGNAL</span><small>HOTSPAWN CS2 PICK DESK</small></span></a><a class="source-visit" href="https://play.hotspawn.com/cs2-pickems">Open Hotspawn ↗</a></div><nav aria-label="Main navigation">{navhtml}</nav></header>
<main id="main"><div class="page-heading"><div><p class="eyebrow">COUNTER-STRIKE 2 / RESEARCH DASHBOARD</p><h1>{esc(title)}</h1><p class="lead">{esc(subtitle)}</p></div><div class="refresh"><span id="freshness" class="status-dot">Snapshot</span><span>Checked {esc(time_label(data['fixture_checked_at']))}</span><small>Scheduled every 6 hours · not real time</small><a href="{REPO}/actions/workflows/refresh.yml">Update history ↗</a></div></div><div id="stale-notice" class="notice danger" hidden>This snapshot is over eight hours old. Picks are hidden until a successful refresh. Check <a href="{REPO}/actions">automation status</a>; source coverage is not currently verified.</div>
{content}</main><footer><div><strong>Independent research. Not Hotspawn.</strong><p>Probabilities are estimates, not guarantees. Model-only picks are clearly labeled. No community voting data is used. Informational use only · 18+.</p></div><div><a href="data/snapshot.json">Download JSON</a><a href="data/matches.csv">Download CSV</a><a href="{REPO}">Repository ↗</a></div></footer></body></html>'''


def build():
    d = json.loads((DATA / 'snapshot.json').read_text())
    rows = d['matches']
    opened = [r for r in rows if r['state'] != 'locked']
    market = [r for r in opened if r['method'] == 'market']
    model = [r for r in opened if r['method'] == 'model']
    unresolved = [r for r in opened if r['state'] == 'unresolved']
    flagged = [r for r in rows if r['flags']]
    coverage = d['coverage']
    overview = f'''<section class="hero-panel"><div><div class="eyebrow">EXECUTIVE SUMMARY</div><h2>Your next pick.<br>With the evidence behind it.</h2><p>Every fixture stays in the list. We use external series moneylines first, then research-backed estimates. When the evidence runs out, we say so.</p><div class="actions"><a class="button primary" href="picks.html">See all updated picks <span>→</span></a><a class="button secondary" href="unresolved.html">Review unresolved matches</a></div></div><div class="hero-note"><span class="tiny-label">COVERAGE AT LAST REFRESH</span><strong>{len(opened)}<small>open fixtures</small></strong><div>{len(market) + len(model)} with probabilities · {len(unresolved)} unresolved</div><p>{len(rows)} total source rows retained, including locked / past fixtures.</p></div></section>
<section class="metrics" aria-label="Coverage breakdown"><a href="picks.html?view=market"><span class="metric-label">MARKET-DERIVED</span><strong>{len(market):02}</strong><span>External moneylines <b>↗</b></span></a><a href="picks.html?view=model"><span class="metric-label">RESEARCH FALLBACK</span><strong>{len(model):02}</strong><span>Model-only estimates <b>↗</b></span></a><a href="unresolved.html"><span class="metric-label">UNRESOLVED</span><strong>{len(unresolved):02}</strong><span>Evidence still missing <b>↗</b></span></a><a href="picks.html?view=all"><span class="metric-label">SOURCE INVENTORY</span><strong>{len(rows):02}</strong><span>All tiers, all listed rows <b>↗</b></span></a></section>
<div class="summary-grid"><section class="panel"><div class="section-kicker">01 / WHAT TO USE</div><h2>A clear route to your picks</h2><ul class="steps"><li><span>1</span><div><a href="picks.html">All picks</a><p>Each team’s probability, our lean, start time and evidence in one place. Filter by team, tier or method.</p></div></li><li><span>2</span><div><a href="unresolved.html">Unresolved matches</a><p>{len(unresolved)} open rows lack usable market prices and a qualified fallback. Probabilities remain blank, not 50/50.</p></div></li><li><span>3</span><div><a href="review.html">Flagged for Review</a><p>Model assumptions, thin markets and old fixtures still labeled scheduled are surfaced for review.</p></div></li></ul></section><section class="panel warm"><div class="section-kicker">02 / LIMITATIONS</div><h2>Know what is—and isn’t—verified</h2><p><strong>{coverage['collected']} / {esc(coverage['advertised']) or 'unknown'} lobby rows captured.</strong> Count status: {esc(coverage['status'])}. This measures inventory coverage, not prediction accuracy.</p><p>HLTV is attempted before esportsbooks for matches without an accepted featured-market moneyline. Blocked sources cannot support a line.</p><p>Research fallbacks use Valve’s published ranking points. They are uncalibrated estimates; current rosters and vetoes are not verified. They are never presented as bookmaker quotes.</p><a href="sources.html">Read the methodology →</a></section></div>'''
    if d['issues']:
        overview += '<div class="notice danger"><strong>Refresh limitations</strong><ul>' + ''.join(f'<li>{esc(i)}</li>' for i in d['issues']) + '</ul></div>'
    preview = sorted(market + model, key=lambda r: r['start_at'])[:4]
    overview += '<section class="section-title"><div><p class="eyebrow">UP NEXT</p><h2>The next researched matches</h2></div><a href="picks.html">View full list →</a></section>' + table(preview)
    pages = {'index.html': ('The pick desk', 'A complete match list. Independent probabilities. No guesswork disguised as evidence.', overview)}
    pages['picks.html'] = ('All matches & picks', f'{len(rows)} source fixtures · {len(opened)} open at refresh. Times are shown in UTC.',
        '<div class="notice"><strong>Read the label.</strong> Market-derived = normalized external share prices. Research model = calculated estimate from Valve points, not a betting line. Blank = unverified. “Our pick” is the higher estimated probability, not a guarantee.</div>' + table(rows, True))
    unresolved_content = '<div class="notice amber"><strong>No unsupported picks.</strong> These open matches have no accepted external series moneyline and no qualified exact-name ranking fallback. Expand each row to see the source attempts and the specific limitation. They are retried automatically on the next scheduled run.</div>' + table(unresolved)
    pages['unresolved.html'] = ('Unresolved picks', f'{len(unresolved)} open matches need more evidence. No manual input is required.', unresolved_content)
    reviews = '<div class="notice amber">Flags do not remove a match from the inventory. Source facts, calculated estimates and unknown values remain separate. Source access failures are also listed on <a href="sources.html">Sources & method</a>.</div><section class="panel"><h2>Review register</h2><div class="table-wrap"><table><thead><tr><th>Match</th><th>Issue requiring review</th><th>Official source</th></tr></thead><tbody>'
    for r in flagged:
        reviews += f'<tr><td><a href="picks.html#match-{esc(r["id"])}">{esc(" vs ".join(r["teams"]))}</a></td><td>{esc(" ".join(r["flags"]))}</td><td>{link(r["fixture_source"],"Hotspawn")}' + ''.join(link(e['url'], e['source']) for e in r['evidence']) + '</td></tr>'
    for issue in d['issues']:
        reviews += f'<tr><td>Refresh</td><td>{esc(issue)}</td><td>{link(coverage["source"], "Hotspawn")}</td></tr>'
    reviews += '</tbody></table></div></section><section class="panel"><h2>Unresolved is also a review outcome</h2><p>Unknown team identities, absent ratings and inaccessible lines are not replaced with guesses.</p><a class="button secondary" href="unresolved.html">See unresolved matches →</a></section>'
    pages['review.html'] = ('Flagged for Review', f'{len(flagged)} fixture rows have explicit flags. Published limitations do not block updates.', reviews)
    sources = '''<div class="summary-grid"><section class="panel"><div class="section-kicker">THE RESOLUTION LADDER</div><h2>Evidence first. Fallbacks second.</h2><ol class="method-list"><li><strong>Hotspawn → fixture inventory only.</strong> Parse public Angular transfer-state JSON from the dedicated CS2 lobby. Keep stable fixture IDs, team names, tiers and UTC timestamps. Compare the embedded count with “All tiers”. Never ingest voting percentages into the model.</li><li><strong>Polymarket → external series moneyline.</strong> Discover the CS2 series from the official sports metadata API and exhaust event pagination. Accept only active, open, order-accepting, two-team moneylines with positive liquidity, updated within eight hours. Exact names and start times within one hour must match uniquely. No fuzzy academy/main-roster matching.</li><li><strong>Only missing market matches → HLTV, then esportsbooks.</strong> Try HLTV’s public match page, GG.BET, Thunderpick, Pinnacle and Rivalry. Access and parsing limitations are recorded per match. A successful HTML response alone is not a verified line. No CAPTCHA or regional restriction bypass.</li><li><strong>Still unresolved → Valve research model.</strong> Use the latest non-future global standings, no older than 35 days. Require unique exact-name matches for both teams. No invented default rating for unranked teams.</li><li><strong>Still missing evidence → blank.</strong> Publish the match, source trail and reason. Retry every refresh. Locked or ended matches are retained without invented retrospective picks.</li></ol></section><section class="panel warm"><div class="section-kicker">HOW WE CALCULATE</div><h2>Our probabilities & fair lines</h2><p><strong>Prediction markets:</strong> for observed prices q₁ and q₂, p₁ = q₁ / (q₁ + q₂); p₂ = 1 − p₁. This removes the total-price imbalance, not all market biases, fees or spread effects.</p><p><strong>Sportsbook formula:</strong> if a validated two-sided decimal quote becomes available, p₁ = (1/o₁) / (1/o₁ + 1/o₂). No sportsbook quotes are invented when access fails.</p><p><strong>Research model v1:</strong> p₁ = 1 / (1 + 10<sup>g(R₂−R₁)/400</sup>), where R is published Valve points and g = 1 / √(1 + 3(ln(10)/400)² × 350² / π²).</p><p>The fixed rating deviation of 350 is our conservative modeling assumption, not an observed team statistic. The equation follows Valve’s public Glicko expected-score function. This is not Valve’s official forecast and has not been independently calibrated. No BO1/BO3 adjustment or roster inference is made.</p><p><strong>Our fair line:</strong> 1 / p. This is a calculated decimal line, never a claim that a bookmaker offers it. The higher probability is the pick; exactly equal probabilities mean no lean.</p><p><a href="https://github.com/ValveSoftware/counter-strike_regional_standings/blob/master/model/glicko.js">Valve model source ↗</a> · <a href="https://docs.polymarket.com/market-data/discover-markets">Polymarket API documentation ↗</a></p></section></div>'''
    sources += '<section class="panel"><h2>Source health at the last run</h2><p>“Retrieved” verifies access, not every value on a page. A blocked source is not evidence that the match has no betting market.</p><div class="table-wrap"><table><thead><tr><th>Official source</th><th>HTTP / status</th><th>Finding</th><th>Checked (UTC)</th></tr></thead><tbody>'
    for a in d['source_audit']:
        sources += f'<tr><td>{link(a["url"], a["name"])}</td><td>{esc(a.get("http_status"))} · {esc(a.get("status"))}</td><td>{esc(a.get("detail", "Public source response captured; inputs validated separately."))}</td><td>{esc(time_label(a["checked_at"]))}</td></tr>'
    sources += '</tbody></table></div></section>'
    sources += f'''<section class="panel"><h2>Automation, provenance & coverage limits</h2><p>GitHub Actions is scheduled at 00:17, 06:17, 12:17 and 18:17 UTC. Schedules can be delayed or disabled by GitHub; this is not a real-time service or a guaranteed six-hour SLA. The next nominal refresh after this build is around {esc(time_label(iso(parse_time(d['generated_at']) + timedelta(hours=6))))}.</p><p>A failed fixture refresh retains the previous fixture inventory with its original observation timestamp, but blanks actionable probabilities. The page warns and suppresses picks after eight hours. Expired lock times also suppress displayed picks in JavaScript-enabled browsers. Without JavaScript, always check the printed observation and lock times.</p><p>The public lobby currently includes old “scheduled” rows. These are retained and flagged, not silently treated as new matches. Missing pagination counts, duplicate fixture IDs and changed source schemas fail closed. No claim is made about fixtures hidden behind authentication or omitted by Hotspawn itself.</p><p>Market identity requires exact normalized names; different spelling or a rescheduled start over one hour will fall back rather than risk assigning the wrong line. Model input dates, points and listed rosters are retained in each row’s evidence. Current rosters are not confirmed.</p><p>{link('data/evidence/fixtures.json','Captured fixture inputs')} · {link('data/snapshot.json','Full snapshot and audit trail')} · {link(REPO + '/actions/workflows/refresh.yml', 'Scheduled run history')}</p><p>Every deployment retains a downloadable data artifact for 30 days. Data and CSV values are explicitly as-of the snapshot, not live quotes. This site neither places bets nor submits Hotspawn picks.</p></section>'''
    pages['sources.html'] = ('Sources & methodology', 'A reproducible process, with the limits left in—not edited out.', sources)
    for path, (title, subtitle, content) in pages.items():
        (OUT / path).write_text(shell(path, title, subtitle, content, d))
    (OUT / '.nojekyll').touch()
    with (DATA / 'matches.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['fixture_id','team_1','team_2','start_utc','lock_utc','tournament','tier','state','method','team_1_probability','team_2_probability','pick','observed_at','official_fixture_source','analysis_sources','limitations'])
        for r in rows:
            writer.writerow([r['id'], *r['teams'], r['start_at'], r['lock_at'], r['tournament'], r['tier'], r['state'], r['method'], *(r['probabilities'] or ['', '']), r['pick'], r['fixture_verified_at'], r['fixture_source'], ' | '.join(e['url'] for e in r['evidence']), ' | '.join(r['limitations'])])
    print(f'Built {len(pages)} pages, {len(rows)} source-linked rows.')


if __name__ == '__main__':
    build()
