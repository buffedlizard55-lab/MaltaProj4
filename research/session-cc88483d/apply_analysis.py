import json
from pathlib import Path
p=Path('data/analysis.json');x=json.loads(p.read_text())
base='https://www.hltv.org/'
results=base+'results?event=8932'
third=base+'matches/2399416/aurora-vs-falcons-thunderpick-world-championship-2026'
final=base+'matches/2399417/furia-vs-betboom-thunderpick-world-championship-2026'
repo='https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/research/session-cc88483d/'
api='https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1'
x['front_page_plan']='day_five_guidance'
x['day_four_results']={
 'date':'2026-10-17','label':'Day four · 17 October 2026 · semi-finals','key':'day-four-results',
 'results_url':results,'matches':[
 {'winner':'FURIA','loser':'Aurora','score':'2-0','maps':None,'stage':'Semi-final',
  'match_url':base+'matches/2399414/furia-vs-aurora-thunderpick-world-championship-2026',
  'report_url':results,'detail':'Series result re-read from HLTV at 20:18 UTC on 17 October. FURIA advances to the final; Aurora is named in the third-place fixture. Map scores were not collected and remain blank.',
  'flag':'Result-list day headings were not exposed by the parser; the semi-final date is corroborated by the published event schedule and retained pre-match timestamps, not inferred from an absent heading.'},
 {'winner':'BETBOOM','loser':'Falcons','score':'2-1','maps':None,'stage':'Semi-final',
  'match_url':base+'matches/2399415/falcons-vs-betboom-thunderpick-world-championship-2026',
  'report_url':results,'detail':'HLTV lists Falcons 1-2 BETBOOM at 20:18 UTC on 17 October. BETBOOM advances to the final; Falcons is named in the third-place fixture. This is the day-four upset relative to the retained pre-match exchange and bookmaker lines, not a retrospective probability estimate.',
  'flag':'Map scores and finish times uncollected. Earlier day-four guidance is a dated pre-match record, not a current recommendation.'}
 ]}
x['day_five_guidance']={
 'date':'Day 5 · Sunday 18 October 2026 · research observed 17 October 20:18 UTC',
 'nav_label':'Day-5 final-day guide','anchor':'day-five-guidance',
 'card':'The bracket is now populated: FURIA–BETBOOM in the final (15:00 UTC), Aurora–Falcons for third (11:30 UTC). Read the day-four results and the sourced research-only leans; current board prices are separate.',
 'headline':'Final day: FURIA–BETBOOM and Aurora–Falcons, not TBA',
 'summary':'Day four produced another upset: BETBOOM beat Falcons 2-1, while FURIA swept Aurora 2-0. The match pages now confirm the Sunday opponent pairs. Without an accepted match-market line in this 20:18 UTC capture, the dated research leans are FURIA and Falcons from the fixture-specific HLTV ranking order, not invented win percentages. The close ranking comparison in Aurora–Falcons makes it the less speculative alternative to investigate if deliberately chasing variance; it is not proof of an edge. Neither Sunday fixture was on the 20:16 UTC Hotspawn feed, so these are research, not scoreable board picks at that observation. The automated picks page remains the authority for subsequent listings, probabilities and lock times.',
 'fixtures':[],
 'not_listed':[
 {'label':'Third-place decider · Aurora vs Falcons','event':'Thunderpick World Championship 2026 · third place',
  'teams':['Aurora','Falcons'],'now_listed':False,'pick':'Falcons',
  'pick_detail':'Research-only ranking lean: HLTV #5 Falcons vs #6 Aurora on this exact fixture. No numeric probability or fair odds; this narrow ranking gap is not a measured edge.',
  'timing':'18 October 11:30 UTC, from HLTV start_unix 1792323000000 re-read 17 October 20:18 UTC. Earlier sourced schedule records best of three; the current parser returned no format text, so no new format verification is claimed.',
  'why':'Analysis: Aurora is the closer-ranked alternative to investigate, but only after an external match price appears. Both teams lost their semi-final; no verified evidence establishes reduced motivation. Aurora played two maps in the earlier scheduled semi-final, Falcons three in the later one. That is schedule/map-load context, not proof of fatigue. July roster-change reporting is not a fresh onboarding shock in mid-October.',
  'hltv_url':third,'standings_url':third,'standings_label':'Fixture-specific HLTV rankings',
  'sources':[{'label':'Day-four series results','url':results},{'label':'Dated fixture/rank/lineup receipt','url':repo+'probe/hltv-twc-2399416.json'}, {'label':'Aurora rebuild report (8 July; historical)','url':base+'news/45082/official-aurora-complete-rebuild-with-kyxsan'}]},
 {'label':'Grand final · FURIA vs BETBOOM','event':'Thunderpick World Championship 2026 · grand final',
  'teams':['FURIA','BETBOOM'],'now_listed':False,'pick':'FURIA',
  'pick_detail':'Research-only ranking lean: HLTV #4 FURIA vs #14 BETBOOM on this exact fixture. Not a bookmaker probability. An upset win over Falcons does not itself make BETBOOM value at an unknown final price.',
  'timing':'18 October 15:00 UTC, from HLTV start_unix 1792335600000 re-read 17 October 20:18 UTC. Earlier sourced schedule records best of five; current format extraction is blank. Do not reuse a semi-final best-of-three price for this final.',
  'why':'Analysis: BETBOOM has a concrete competitive case—three straight 2-1 wins over PARIVISION, Legacy and Falcons after losing 0-2 to FURIA on day one. But FURIA also beat Legacy and swept Aurora, and the two teams have played 7 and 11 maps respectively across the verified event results. FURIA played the earlier two-map semi-final, BETBOOM the later three-map one. None of this quantifies fatigue or proves a pricing error. Default to the better-supported line once a fresh final market exists; a BETBOOM swing remains a high-variance decision, not an automatic upset pick.',
  'hltv_url':final,'standings_url':final,'standings_label':'Fixture-specific HLTV rankings',
  'sources':[{'label':'All twelve completed series','url':results},{'label':'Dated fixture/rank/lineup receipt','url':repo+'probe/hltv-twc-2399417.json'}]}
 ],
 'points_label':'How days one to four change the final-day decision (analysis)',
 'points':[
 {'claim':'Day one is a warning against certainty, not an instruction to fade every favourite.',
  'detail':'9z swept Aurora 2-0 on day one, but Aurora swept the same opponent 2-0 in the day-three decider. A repeat matchup need not repeat its result. This is a sourced example, not a calibrated frequency for Sunday.', 'source':results},
 {'claim':'Day two and day three provide the stronger BETBOOM case than a roster rumour.',
  'detail':'The retrieved results confirm BETBOOM 2-1 PARIVISION, 2-1 Legacy and now 2-1 Falcons. FURIA won 2-0 against BETBOOM, 2-1 against Legacy and 2-0 against Aurora. The final is a rematch, but the opening sweep cannot be converted into a final probability.', 'source':results},
 {'claim':'Day four changed the bracket, not the rules of expected points.',
  'detail':'FURIA 2-0 Aurora and Falcons 1-2 BETBOOM are the newly completed results. The prior Falcons market favourite lost; that does not retroactively make a BETBOOM pick correct by method, nor make every subsequent underdog good value.', 'source':results},
 {'claim':'Protect a streak unless there is a price-based reason to spend it.',
  'detail':'Hotspawn rules re-read at 20:25 UTC say correct picks earn points, higher-tier matches reward more, consecutive correct picks earn bonuses, and the leaderboard resets weekly. No verified bonus formula or current user pick shares are available here. Without those and your standings, this project cannot calculate an optimal leaderboard strategy. Default to the supported favourite; choosing a close alternative while chasing is a risk preference, not proven positive expected value.',
  'source':'https://play.hotspawn.com/how-it-works'},
 {'claim':'A research fixture does not earn Hotspawn points until it is actually listed.',
  'detail':'The independently checked 20:16 UTC feed had 81 entries and neither Sunday TWC fixture. Automatic future refreshes can discover newly listed rows. Until then these cards are research only; do not confuse the separately named Thunderpick South America qualifier with the Malta main event.', 'source':api}
 ],
 'unpriced_label':'Final-day unresolved prices and coverage limitations',
 'unpriced':[
 {'label':'Aurora vs Falcons · third-place decider','when':'18 October · 11:30 UTC', 'status':'Teams verified; no accepted market probability in this capture',
  'limitation':'HLTV exposes the opponent pair, start and rankings but no numeric two-way betting row. Neither the active CS2 exchange event capture nor the filtered Pinnacle esports feed contains this matchup. This describes the observed feeds, not every bookmaker. Research lean Falcons; percentages and fair odds stay blank. Not on Hotspawn at 20:16 UTC.',
  'sources':[{'label':'HLTV fixture','url':third},{'label':'Operator exchange evidence','url':repo+'probe/polymarket-active-cs2.json'},{'label':'Operator bookmaker evidence','url':repo+'probe/pinnacle-esports.json'}]},
 {'label':'FURIA vs BETBOOM · grand final','when':'18 October · 15:00 UTC','status':'Teams verified; no accepted market probability in this capture',
  'limitation':'No matching final market in the observed active CS2 exchange events or Pinnacle esports matchups; HLTV betting extraction is empty. Research lean FURIA only. No semi-final quote, old head-to-head price or BO3-to-BO5 conversion is reused. Blank means unverified, not 50/50.',
  'sources':[{'label':'HLTV fixture','url':final},{'label':'Exchange market capture','url':repo+'probe/polymarket-active-cs2.json'},{'label':'Bookmaker capture','url':repo+'probe/pinnacle-esports.json'}]},
 {'label':'Current Hotspawn rows without accepted market lines','when':'Re-evaluated automatically at every refresh','status':'See the live unresolved and non-market board',
  'limitation':'The 20:18 UTC production snapshot has 18 open rows: 7 market probabilities, 6 originated VRS estimates, 4 research-only picks with blank percentages, and Hacha–LOS NINOS unresolved. The separate later probe sees a Hacha quote rejected by production; its event status is being audited, not overridden. Counts are dated, not a promise of permanent coverage.',
  'sources':[{'label':'Hotspawn official fixture feed','url':api},{'label':'All current limitations on this site','url':'https://buffedlizard55-lab.github.io/MaltaProj4/unresolved.html'},{'label':'Dated independent audit','url':repo+'row-audit.md'}]}
 ],
 'unverified':[
 'No current Sunday market probability is verified in these receipts. These ranking-order leans are dated research, not live model or betting lines. Subsequent board lines are independently checked and may disagree.',
 'The source parser returned null day headings on the result list and null current format text on both final-day pages. Series scores, opponent pairs, Unix start times, rankings and lineups were read; map scores and finish times were not. The earlier sourced BO3/BO5 schedule is historical evidence, not a fresh field read.',
 'A later raw HTML re-capture was refused by HLTV with 403 after the normal bounded waits. It was not bypassed; the earlier successful parsed response receipts are retained. Aurora’s July transfer date was not freshly re-read during that blocked capture; it remains attributed historical reporting, not a new roster development.',
 'No verified crowd pick shares, current leaderboard distribution, personal position or streak-bonus formula are available. A market underdog is not necessarily a crowd contrarian; no optimal rank-climbing claim is made.',
 'Neither newly populated final-day matchup was in the observed Hotspawn inventory. This is an observation at 20:16 UTC, not a permanent absence claim; scheduled refreshes re-check the board.'
 ]}
p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
