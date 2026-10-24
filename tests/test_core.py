import copy
import json
import math
import unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
from scripts.core import *

NOW=dt('2026-10-14T05:00:00Z')
FIX={'id':'test','sport_alias':'cs2','participants0_name':'Alpha','participants1_name':'Beta','status':'scheduled','scheduled_start_time':'2026-10-15T10:00:00Z','lock_time':'2026-10-15T09:54:00Z'}
def fixture(): return normalize_fixtures([FIX],{},NOW)[0]
def exchange():
    return {'slug':'cs2-test','sport':{'sport':'cs2'},'markets':[{'id':'123','question':'Counter-Strike: Alpha vs Beta (BO3)','sportsMarketType':'moneyline','active':True,'closed':False,'acceptingOrders':True,'outcomes':'["Alpha","Beta"]','outcomePrices':'["0.6","0.4"]','gameStartTime':'2026-10-15T10:00:00Z','updatedAt':iso(NOW),'bestBid':.59,'bestAsk':.61,'liquidity':'1000'}]}
class CoreTests(unittest.TestCase):
    def test_devig(self):
        p,margin=devig([1.5,3.0]);self.assertAlmostEqual(p[0],2/3);self.assertAlmostEqual(sum(p),1);self.assertAlmostEqual(margin,0)
    def test_american(self):
        self.assertEqual(american(-200),1.5);self.assertEqual(american(150),2.5)
    def test_invalid_odds(self):
        for odds in ([1,2],[math.nan,2],[2,math.inf],[0,2],[2]):
            with self.assertRaises(ValueError):devig(odds)
        for v in (0,50,math.nan):
            with self.assertRaises(ValueError):american(v)
    def test_timezone_required(self):
        with self.assertRaises(ValueError):dt('2026-01-01')
    def test_millisecond_timestamp(self):self.assertEqual(iso(0),'1970-01-01T00:00:00Z')
    def test_freshness(self):
        self.assertTrue(fresh(NOW,NOW));self.assertFalse(fresh(NOW-timedelta(hours=9),NOW));self.assertFalse(fresh(NOW+timedelta(hours=1),NOW))
    def test_game_filter(self):
        self.assertEqual(normalize_fixtures([FIX|{'sport_alias':'lol'}],{},NOW),[])
    def test_crowd_not_input(self):
        a=normalize_fixtures([FIX|{'participants0_picked_percent':99}],{},NOW)
        b=normalize_fixtures([FIX|{'participants0_picked_percent':1}],{},NOW)
        self.assertEqual(a,b)
    def test_past_not_open(self):
        a=normalize_fixtures([FIX|{'lock_time':'2026-10-14T01:00:00Z'}],{},NOW)[0];self.assertEqual(a['state'],'not_open')
    def test_end_and_scheduled(self):
        a=normalize_fixtures([FIX|{'end_time':'2026-10-14T01:00:00Z'}],{},NOW)[0];self.assertEqual(a['state'],'not_open');self.assertTrue(a['flags'])
    def test_duplicate_ids(self):
        with self.assertRaises(ValueError):normalize_fixtures([FIX,FIX],{},NOW)
    def test_unannounced(self):
        for field in ('participants0_name','participants1_name'):
            self.assertEqual(normalize_fixtures([FIX|{field:'TBD'}],{},NOW)[0]['state'],'not_open')
    def test_orientation(self):
        self.assertEqual(orientation(fixture(),['Beta','Alpha'],'2026-10-15T10:00:00Z'),[1,0])
        self.assertIsNone(orientation(fixture(),['Alpha Academy','Beta'],'2026-10-15T10:00:00Z'))
        self.assertIsNone(orientation(fixture(),['Alpha','Beta'],'2026-10-16T10:00:00Z'))
    def test_exchange_resolves(self):
        f=fixture();resolve(f,polymarket_candidates([exchange()],iso(NOW)),'Polymarket',NOW);self.assertEqual(f['pick'],'Alpha');self.assertEqual(f['probabilities'],[.6,.4])
    def test_reversed_exchange(self):
        x=exchange();x['markets'][0]['outcomes']='["Beta","Alpha"]';f=fixture();resolve(f,polymarket_candidates([x],iso(NOW)),'Polymarket',NOW);self.assertEqual(f['pick'],'Beta');self.assertEqual(f['probabilities'],[.4,.6])
    def test_exchange_child_rejected(self):
        x=exchange();x['markets'][0]['sportsMarketType']='child_moneyline';self.assertEqual(polymarket_candidates([x],iso(NOW)),[])
    def test_closed_or_live(self):
        for change in ({'closed':True},{'live':True},{'ended':True}):self.assertEqual(polymarket_candidates([exchange()|change],iso(NOW)),[])
    def test_bad_market(self):
        for change in ({'closed':True},{'bestBid':0},{'bestAsk':1},{'liquidity':'0'},{'updatedAt':'2026-10-13T00:00:00Z'},{'outcomePrices':'["0","1"]'},{'outcomePrices':'["NaN","0.4"]'},{'bestBid':.1,'bestAsk':.9},{'acceptingOrders':False}):
            x=exchange();x['markets'][0].update(change);f=fixture();resolve(f,polymarket_candidates([x],iso(NOW)),'Polymarket',NOW);self.assertIsNone(f['probabilities'],change)
    def test_duplicate_candidate(self):
        f=fixture();c=polymarket_candidates([exchange()],iso(NOW));resolve(f,c+c,'Polymarket',NOW);self.assertIsNone(f['pick']);self.assertIn('ambiguous',f['attempts'][0]['reason'])
    def test_equal_market_no_pick(self):
        # Integration repair, session e86697a6 (2026-10-24): an exactly even two-way
        # line has no directional edge, so it is kept as rejected evidence and the
        # ladder continues instead of publishing 50/50 with no pick. Measured:
        # fixture 1079200 on the 16:31Z refresh took exactly that path and broke 42
        # coverage contracts. See COORDINATION.md.
        x=exchange();x['markets'][0]['outcomePrices']='["0.5","0.5"]';f=fixture();resolve(f,polymarket_candidates([x],iso(NOW)),'Polymarket',NOW);self.assertIsNone(f['probabilities']);self.assertIsNone(f['pick']);self.assertIn('exactly even',f['attempts'][0]['reason']);self.assertIn('rejected_quote',f['attempts'][0])
    def test_source_abbreviation(self):
        x=exchange();x['markets'][0]['outcomes']='["Alpha Gaming","Beta"]';x['teams']=[{'name':'Alpha Gaming','abbreviation':'alpha'}];f=fixture();resolve(f,polymarket_candidates([x],iso(NOW)),'Polymarket',NOW);self.assertEqual(f['pick'],'Alpha');self.assertTrue(f['evidence'][0]['team_metadata'])
    def test_no_guessed_alias(self):
        x=exchange();x['markets'][0]['outcomes']='["Alpha Gaming","Beta"]';f=fixture();resolve(f,polymarket_candidates([x],iso(NOW)),'Polymarket',NOW);self.assertIsNone(f['pick'])
    def test_format_conflict(self):
        f=fixture();f['best_of']=1;resolve(f,polymarket_candidates([exchange()],iso(NOW)),'Polymarket',NOW);self.assertIsNone(f['pick'])
    def test_primary_not_overwritten(self):
        f=fixture();resolve(f,polymarket_candidates([exchange()],iso(NOW)),'Polymarket',NOW);before=copy.deepcopy(f);resolve(f,[],'Pinnacle',NOW);self.assertEqual(before,f)
    def test_real_hotspawn_capture(self):
        raw=json.loads(Path('data/latest.json').read_text());f=normalize_fixtures(raw['fixture_evidence'],{},dt(raw['generated_at']));self.assertEqual(len(f),len(raw['matches']))

class PinnacleTests(unittest.TestCase):
    def setUp(self):
        self.m={'id':123,'league':{'name':'CS2 - Test'},'type':'matchup','participants':[{'alignment':'home','name':'Alpha'},{'alignment':'away','name':'Beta'}],'startTime':'2026-10-15T10:00:00Z','status':'pending'}
        self.l={'matchupId':123,'type':'moneyline','period':0,'status':'open','cutoffAt':'2026-10-15T10:00:00Z','prices':[{'designation':'home','price':-200},{'designation':'away','price':170}]}
    def test_line(self):
        c=pinnacle_candidates([self.m],[self.l],iso(NOW));f=fixture();resolve(f,c,'Pinnacle',NOW);self.assertEqual(f['pick'],'Alpha');self.assertAlmostEqual(sum(f['probabilities']),1)
    def test_map_handicap_draw_rejected(self):
        for change in ({'period':1},{'type':'spread'},{'isAlternate':True}):self.assertEqual(pinnacle_candidates([self.m],[self.l|change],iso(NOW)),[])
        self.l['prices'].append({'designation':'draw','price':500});f=fixture();resolve(f,pinnacle_candidates([self.m],[self.l],iso(NOW)),'Pinnacle',NOW);self.assertIsNone(f['probabilities'])
    def test_other_game_live_parent(self):
        for change in ({'league':{'name':'LoL - Test'}},{'parentId':44},{'isLive':True}):self.assertEqual(pinnacle_candidates([self.m|change],[self.l],iso(NOW)),[])
    def test_suspended_stale_cutoff(self):
        for change in ({'status':'suspended'},{'cutoffAt':'2026-10-13T00:00:00Z'}):
            f=fixture();resolve(f,pinnacle_candidates([self.m],[self.l|change],iso(NOW)),'Pinnacle',NOW);self.assertIsNone(f['pick'])
        f=fixture();resolve(f,pinnacle_candidates([self.m],[self.l],iso(NOW-timedelta(hours=9))),'Pinnacle',NOW);self.assertIsNone(f['pick'])

if __name__=='__main__':unittest.main()
