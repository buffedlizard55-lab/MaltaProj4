"""Regression guards for session ab18fe2a (16 October 2026).

Three things this session established from primary sources, each worth locking down
because each was, or could become, a false statement on the live site:

1. The TWC Group B decider IS on the Hotspawn board (fixture 1081775). Every capture
   taken on 15 October lacked it, and the published analysis page said so; that is now
   false and must not come back through a merge.
2. No research prose may still assert that the decider is absent or unpickable.
3. The publication workflow must request a refresh cadence that can survive the
   multi-hour GitHub scheduling delays measured in research/refresh-ab18fe2a.

These tests are offline: they read committed files only and fetch nothing.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / 'data' / 'analysis.json'
REVIEW = ROOT / 'data' / 'review-notes.json'
WORKFLOW = ROOT / '.github' / 'workflows' / 'pages.yml'
GROUP_B_ID = '1081775'

# Phrases that would re-introduce the corrected "the decider is not on the board" claim.
STALE_CLAIMS = (
    'not in hotspawn',
    "absent from the hotspawn",
    'is not listed by hotspawn',
    'cannot be picked and scores no points',
    'no betboom fixture at all',
)


def _strings(node):
    """Every string value in a nested structure, lowercased."""
    if isinstance(node, str):
        yield node.lower()
    elif isinstance(node, dict):
        for value in node.values():
            yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings(value)


class GroupBDeciderIsListed(unittest.TestCase):
    """The Group B decider has a Hotspawn fixture id, verified 2026-10-16T04:22Z."""

    def setUp(self):
        self.notes = json.loads(ANALYSIS.read_text())

    def _decider(self):
        for fixture in self.notes['day_three']['fixtures']:
            if 'Legacy' in fixture['teams'] and 'BETBOOM' in fixture['teams']:
                return fixture
        self.fail('The Group B decider is missing from day_three.fixtures')

    def test_hotspawn_fixture_id_is_recorded(self):
        self.assertEqual(self._decider().get('hotspawn_fixture'), GROUP_B_ID)

    def test_hotspawn_page_link_is_absolute(self):
        page = self._decider().get('hotspawn_page')
        self.assertTrue(page and page.startswith('https://www.hotspawn.com/matches/'),
                        'the decider needs its own Hotspawn match page link, not the generic feed')

    def test_guidance_marks_it_as_now_listed(self):
        for entry in self.notes['day_three_guidance'].get('not_listed', []):
            if 'Legacy' in entry.get('label', ''):
                self.assertTrue(entry.get('now_listed'),
                                'the not_listed card for the decider must carry now_listed: true')
                return
        self.skipTest('the decider no longer appears under not_listed at all')


class NoStaleAbsenceClaims(unittest.TestCase):
    """No published prose may still say the decider is absent or unpickable."""

    def _check(self, path, label):
        document = json.loads(path.read_text())
        for text in _strings(document):
            for claim in STALE_CLAIMS:
                self.assertNotIn(claim, text,
                                 f'{label}: stale claim {claim!r} is still published')

    def test_analysis_json_holds_no_stale_absence_claim(self):
        self._check(ANALYSIS, 'data/analysis.json')

    def test_review_notes_hold_no_stale_absence_claim(self):
        self._check(REVIEW, 'data/review-notes.json')


class RefreshCadence(unittest.TestCase):
    """The cron must be able to land inside the eight-hour evidence window."""

    @staticmethod
    def _hours(expr):
        """Rough period of a five-field cron, from its hour field. None if unclear."""
        fields = expr.split()
        hour = fields[1] if len(fields) >= 5 else None
        if hour == '*':
            return 1.0
        match = re.fullmatch(r'\*/(\d+)', hour or '')
        if match:
            return float(match.group(1))
        return None

    def test_at_least_one_schedule_entry_exists(self):
        crons = re.findall(r"cron:\s*'([^']+)'", WORKFLOW.read_text())
        self.assertTrue(crons, 'the publication workflow declares no schedule at all')

    def test_requested_interval_is_two_hours_or_less(self):
        crons = re.findall(r"cron:\s*'([^']+)'", WORKFLOW.read_text())
        periods = [p for p in (self._hours(c) for c in crons) if p is not None]
        self.assertTrue(periods, f'no parseable hour field in cron entries: {crons}')
        self.assertLessEqual(min(periods), 2.0,
                             'GitHub delayed scheduled runs by 3-5 hours on 2026-10-15, so a '
                             'cadence longer than two hours can miss the eight-hour window')

    def test_diagnosis_is_recorded_next_to_the_cron(self):
        text = WORKFLOW.read_text()
        self.assertIn('research/refresh-ab18fe2a', text,
                      'the cadence change must point at the measurement that justifies it')


if __name__ == '__main__':
    unittest.main()
