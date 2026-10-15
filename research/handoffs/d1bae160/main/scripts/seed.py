"""Transcription of official pages inspected 2026-10-15; not synthetic fixtures."""
import json
from datetime import datetime, timezone
from pathlib import Path
now=datetime.now(timezone.utc).isoformat()
rows=[]
def add(id,a,b,tournament,slug,date,time=None,odds=None,book=None):
    rows.append(dict(id=str(id),teams=[a,b],tournament=tournament,source='https://www.hotspawn.com/matches/'+slug+'-'+str(id),lobby='https://play.hotspawn.com/cs2-pickems',date=date,startUtc=(date+'T'+time+':00Z') if time else None,observedAt=now,odds=odds,bookSource=book,oddsAt=now if odds else None,reason=None if odds else 'No independently verified, unambiguous two-sided match-winner line. Team aliases, schedule or market availability require verification.'))
t='Thunderpick World Championship 2026'; base='https://thunderpick.io/esports/cs2-betting/thunderpick-world-championship-2026/11024/'
for id,a,b,slug,odds,path in [(1080201,'Aurora','Ninjas in Pyjamas','aurora-vs-ninjas-in-pyjamas',[-333,220],'aurora-vs-ninjas-in-pyjamas/2825093'),(1080202,'9z','Falcons','9z-vs-falcons',None,None),(1080203,'PARIVISION','BetBoom','parivision-vs-betboom',None,None),(1080204,'Legacy','FURIA','legacy-vs-furia',[110,-154],'legacy-vs-furia/2826623')]:
    add(id,a,b,t,slug+'-thunderpick-world-championship-2026','2026-10-15',odds=odds,book=base+path if path else None)
base='https://thunderpick.io/esports/cs2-betting/pulse-beat-iii/11173/'
add(1079440,'MIBR','BC.Game','Stake Pulse Beat III','mibr-vs-bc-game-stake-pulse-beat-iii','2026-10-15',odds=[-147,105],book=base+'mibr-vs-bc-game/2767837')
add(1079442,'Heroic','Envy','Stake Pulse Beat III','heroic-vs-envy-stake-pulse-beat-iii','2026-10-15')
pairs=[('WROTBERRY','EAC'),('ENCE','BOJONG'),('WROTBERRY','ENCE'),('EAC','BOJONG'),('WROTBERRY','BOJONG'),('EAC','ENCE'),('Voca','Phantom'),('HAVU','RoundsGG'),('Voca','HAVU'),('Phantom','RoundsGG'),('RoundsGG','Voca'),('Phantom','HAVU')]
for i,(a,b) in enumerate(pairs):
    # First fixture already absent from upcoming lobby snapshot: retained as tournament-only.
    add(1080279+i,a,b,'Elisa BreakOut Series #2',a.lower()+'-vs-'+b.lower()+'-elisa-breakout-series-2','2026-10-15' if i<6 else '2026-10-16',f'{8+(i%6)*2:02}:00',[-455,280] if i==1 else None,'https://thunderpick.io/esports/cs2-betting/elisa-breakout-series-2/11360/ence-vs-bojong/2807501' if i==1 else None)
    if i==0: rows[-1]['inventoryNote']='Tournament fixture; not present in upcoming lobby extraction (may already be locked).'
add(1081120,'mellren','Privateer','CCT Europe 2026 Series #12 Play-In','mellren-vs-privateer-cct-europe-2026-series-12-play-in','2026-10-16')
Path('site/data/matches.json').write_text(json.dumps(dict(observedAt=now,lastAttemptAt=None,collectionStatus='Research snapshot; automated refresh not yet verified',coverage='Partial: 18 upcoming lobby cards + 1 tournament-only fixture. Weekly count 72; filter count 80. Full inventory not verified.',matches=rows,sourceChecks=[]),indent=2)+'\n')
