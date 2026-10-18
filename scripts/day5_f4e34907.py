"""Historical final-day applier, guarded against replacing newer research.

This script is not a live refresh. It must refuse later research or market-enriched
cards; use scripts.refresh for inventory and quote updates instead.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'research/session-f4e34907'


REVIEWED_AT = '2026-10-17T20:24:00Z'


def ensure_safe_reapplication(notes):
    """Fail closed before any write; never silently drop market evidence."""
    reviewed = notes.get('reviewed_at_utc')
    try:
        existing = datetime.fromisoformat(reviewed.replace('Z', '+00:00'))
        if existing.tzinfo is None:
            raise ValueError('review timestamp must have a timezone')
        cutoff = datetime.fromisoformat(REVIEWED_AT.replace('Z', '+00:00'))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError('Cannot establish research chronology; refusing historical overwrite') from exc
    if existing > cutoff:
        raise ValueError('Newer research exists; refusing historical overwrite')
    plan = notes.get('day_five_guidance', {})
    if any('market' in card for card in plan.get('not_listed', [])):
        raise ValueError('Market evidence exists; refusing historical overwrite')


def apply():
    path = ROOT / 'data/analysis.json'
    notes = json.loads(path.read_text())
    ensure_safe_reapplication(notes)
    results = json.loads((EVIDENCE / 'probe/hltv-twc-results.json').read_text())
    rows = [r for d in results['days'] for r in d['results']]
    wanted = [('2399414', 'FURIA', 'Aurora', '2-0', 'Dust2 13-8; Inferno 13-10'),
              ('2399415', 'BETBOOM', 'Falcons', '2-1', 'Anubis 5-13; Dust2 16-14; Mirage 13-7')]
    matches = []
    for ident, winner, loser, score, maps in wanted:
        row = next(r for r in rows if '/'+ident+'/' in r['url'])
        a, b = map(int, row['score'].split('-'))
        assert row['teams'][0 if a > b else 1] == winner
        assert row['teams'][1 if a > b else 0] == loser
        assert f'{max(a,b)}-{min(a,b)}' == score
        matches.append(dict(winner=winner, loser=loser, score=score, maps=maps,
                            stage='Semi-final', match_url=row['url'], report_url=results['url'],
                            detail='Completed match page checked independently; map scores are winner first.',
                            flag='HLTV specialist-source result; organizer confirmation not collected.'))
    notes['day_four_results'] = dict(key='day-four-results', label='Day 4 · 17 October 2026',
        note='Both semi-finals are final. Series outcomes replayed from the 20:18 UTC runner receipt; maps and dates independently checked on each match page. HLTV is a specialist secondary source, not organizer verification.',
        results_url=results['url'], matches=matches)
    plan = notes['day_five_guidance']
    plan.update(nav_label='Day-5 picks and limits', headline='Final day: FURIA–BETBOOM and Aurora–Falcons',
        card='Both opponent pairs are now confirmed. Open the final-day guide for the research baseline, contrarian candidates and missing-line limitations; the updated picks board is the authority for current probabilities.',
        summary='Reviewed 17 October at 20:18–20:24 UTC. FURIA beat Aurora 2-0; BETBOOM upset Falcons 2-1. Sunday is FURIA–BETBOOM in the BO5 grand final and Aurora–Falcons in the BO3 third-place match. Research baselines are FURIA and Falcons (ranking order only, not priced recommendations). BETBOOM is the evidence-backed upset candidate to examine, not an automatic repeat-upset pick: it lost its opener 0-2 to FURIA, then won three consecutive elimination/playoff series. Aurora is another conditional contrarian candidate, but its July rebuild is not evidence of new October onboarding. No verified Sunday market line was returned in the retained operator scans, and neither Sunday match is in the 20:18 Hotspawn snapshot. Do not recycle semi-final prices or HLTV fan votes as final-day probabilities. Use the live board when fixtures and usable lines appear.',
        points_label='What days 1–4 support — analysis, not a new probability input',
        points=[
            dict(claim='Day 1: 9z upset Aurora 2-0; Day 3: Aurora reversed the matchup 2-0.', detail='The same pairing produced opposite sweeps. Analysis: the first upset was possible, not proof that the underdog is always undervalued. Do not extrapolate one result into an unsupported probability adjustment.', source=results['url']),
            dict(claim='Days 2–4: BETBOOM beat PARIVISION 2-1, Legacy 2-1 and Falcons 2-1.', detail='After the 0-2 FURIA opener, three consecutive series wins establish a real route to the final. Analysis: that supports considering BETBOOM, but three three-map series do not prove either exhaustion or a calibrated form boost.', source=results['url']),
            dict(claim='Day 4: FURIA beat Aurora 2-0 on Dust2 and Inferno.', detail='13-8 and 13-10. Analysis: FURIA is the conservative research baseline; BETBOOM is a conditional higher-variance alternative only after checking a fresh BO5 whole-series price and the final veto. No map-independence formula or invented BO5 multiplier is applied.', source=matches[0]['match_url']),
            dict(claim='Day 4: BETBOOM came back from losing Anubis 5-13 to win Dust2 16-14 and Mirage 13-7.', detail='Falcons lost despite taking BETBOOM’s map pick, while BETBOOM won Falcons’ Dust2 pick. Analysis: inspect the actual final veto and map pool instead of assuming the BO3 comeback transfers unchanged to a BO5.', source=matches[1]['match_url']),
            dict(claim='Aurora’s published rebuild evidence is dated July, not a verified October change.', detail='The earlier roster report is retained for manual review. Analysis: this session has no verified new transaction, illness, stand-in or quantified fatigue input; none is used to move the line.', source='https://www.hltv.org/news/45082/official-aurora-complete-rebuild-with-kyxsan')])
    plan['not_listed'] = []
    for ident, teams, label, bestof, start, pick, why in [
        ('2399416', ['Aurora','Falcons'], 'Third-place decider',3,'11:30','Falcons','Ranking-order research baseline only. Aurora is a conditional alternative, not an onboarding-based pick. Both lost their semi-finals; no motivation or fatigue adjustment has been verified.'),
        ('2399417', ['FURIA','BETBOOM'], 'Grand final',5,'15:00','FURIA','FURIA is the ranking-order research baseline. BETBOOM is the conditional upset option after beating Falcons, but already lost 0-2 to FURIA on Day 1. Without a fresh whole-series line and opponent pick-share data, there is no verified leaderboard edge.')]:
        slug='-vs-'.join(t.lower() for t in teams)
        url=f'https://www.hltv.org/matches/{ident}/{slug}-thunderpick-world-championship-2026'
        plan['not_listed'].append(dict(label=label,event=f'TWC 2026 · BO{bestof} · LAN',teams=teams,
            start_utc=f'2026-10-18T{start}:00Z',now_listed=False,pick=pick,pick_detail='Research-only ranking baseline; no probability and not a submitted Hotspawn pick.',
            timing=f'18 October, {start} UTC. Format and opponent pair checked on HLTV; no organizer confirmation collected.',
            start_unix=int(datetime.fromisoformat(f'2026-10-18T{start}:00+00:00').timestamp()),
            why=why,hltv_url=url,standings_url=url,standings_label='HLTV fixture and rankings',
            model_limitation='No independently replayed, roster-validated final-day model calculation is published in this research card. This is not a claim that the teams are unknown.',
            sources=[dict(label='Official Hotspawn lobby (inventory only)',url='https://play.hotspawn.com/lobby')]))
    plan['unpriced']=[dict(label='Sunday final-day matches',when='18 October · third place / grand final',status='Research only · no verified market line',
        limitation='Teams confirmed on individual HLTV pages. The 20:18 official Hotspawn snapshot has no Sunday TWC row; retained active CS2 exchange and Pinnacle scans returned no validated Sunday pair. HLTV’s retrieved betting sections showed no usable two-sided price; its winner-vote percentages are excluded. Operator access restrictions do not prove no odds exist elsewhere.',sources=[dict(label='Official exchange discovery',url='https://gamma-api.polymarket.com/events?series_id=10310&active=true&closed=false'),dict(label='Official Pinnacle esports lines',url='https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight'),dict(label='HLTV final',url=plan['not_listed'][1]['hltv_url'])]),
        dict(label='Leaderboard advantage, roster and rest adjustments',when='Final-day decision',status='Unverified · not quantified',limitation='No verified opponent-entry distribution, personal deficit, streak formula, new October Aurora transaction or measured fatigue. Higher win probability is the base-points default; a contrarian selection is a variance choice, not a proven edge.',sources=[dict(label='Official pick-em lobby',url='https://play.hotspawn.com/lobby')])]
    plan['unverified']=['HLTV is a specialist secondary source. Tournament-organizer confirmation of the results, schedule and current roster is not collected; these remain flagged for manual review.', 'Operator scans and board membership are dated observations, not permanent absence claims. Future refreshes may discover the Sunday fixtures and usable lines.', 'No final-day market percentage, fair price or calibrated leaderboard advantage is asserted by these strategy cards. Use current source-backed board rows, not fan-vote percentages.']
    notes['front_page_plan']='day_five_guidance'
    notes['reviewed_at_utc']='2026-10-17T20:24:00Z'
    path.write_text(json.dumps(notes,indent=2,ensure_ascii=False)+'\n')


if __name__ == '__main__':
    apply()
