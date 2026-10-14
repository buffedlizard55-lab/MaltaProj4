import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.refresh import run
from scripts.core import hotspawn_state

class FailedSources:
    def __init__(self,now):self.log=[]
    def get(self,*args,**kwargs):raise ValueError('HTTP 503 source unavailable')
class EmptySources(FailedSources):
    def get(self,name,url,as_json=True):
        if not as_json:return '<script id="ng-state">{"x":{"u":"https://example.org/api/v1/fixtures","b":[]}}</script>',{'observed_at':'2026-10-14T05:00:00Z'}
        return [],{'observed_at':'2026-10-14T05:00:00Z'}
class BrokenSchemaSources(FailedSources):
    def get(self,name,url,as_json=True):
        if not as_json:raise ValueError('page missing')
        return [{'sport_alias':'cs2'}],{'observed_at':'2026-10-14T05:00:00Z'}
class RefreshTests(unittest.TestCase):
    def setUp(self):self.previous=json.loads(Path('data/latest.json').read_text())
    def test_failure_preserves_success_timestamp_and_all_rows(self):
        with patch('scripts.refresh.Sources',FailedSources):new=run(copy.deepcopy(self.previous))
        self.assertEqual(new['matches'],self.previous['matches']);self.assertEqual(new['generated_at'],self.previous['generated_at']);self.assertEqual(new['coverage'],'stale');self.assertTrue(new['issues'])
    def test_empty_is_not_claimed_full_coverage(self):
        with patch('scripts.refresh.Sources',EmptySources):new=run(copy.deepcopy(self.previous))
        self.assertEqual(len(new['matches']),len(self.previous['matches']));self.assertEqual(new['coverage'],'stale')
    def test_schema_change_does_not_destroy_snapshot(self):
        with patch('scripts.refresh.Sources',BrokenSchemaSources):new=run(copy.deepcopy(self.previous))
        self.assertEqual(new['matches'],self.previous['matches']);self.assertEqual(new['coverage'],'stale')
    def test_no_first_snapshot_fails_closed(self):
        with patch('scripts.refresh.Sources',FailedSources):
            with self.assertRaises(RuntimeError):run(None)
    def test_hydration_missing_is_not_empty(self):
        with self.assertRaises(ValueError):hotspawn_state('<html>Cloudflare</html>')
