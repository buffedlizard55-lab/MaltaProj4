"""Session 138cbedd regression tests.

Two things are locked down here:

1. The freshness strip must not advertise a slot that has already passed. The
   build states the first slot after its own snapshot; ``assets/app.js``
   recomputes it against the reader's clock and prints the snapshot's age, and
   the browser suite (``tests/browser_138cbedd.cjs``) drives the real page.
2. The independent board auditor must actually fail. Every corruption below is
   applied to the committed snapshot in memory and the auditor must reject it —
   an auditor that only ever passes would verify nothing.
"""
import copy
import importlib.util
import json
import re
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/latest.json').read_text(encoding='utf-8'))
AUDIT_PATH = ROOT / 'verification-138cbedd/audit_board.py'


def load_auditor():
    spec = importlib.util.spec_from_file_location('audit_138cbedd', AUDIT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_audit(payload):
    """Audit an in-memory snapshot through the real CLI code path."""
    import tempfile

    auditor = load_auditor()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'snapshot.json'
        path.write_text(json.dumps(payload), encoding='utf-8')
        return auditor.audit(str(path), identities_path=str(ROOT / 'data/identities.json'))


class SlotArithmetic(unittest.TestCase):
    def setUp(self):
        from scripts.build import next_check, next_slot, SLOT_MINUTES
        self.next_check = next_check
        self.next_slot = next_slot
        self.slots = SLOT_MINUTES

    def utc(self, text):
        return datetime.fromisoformat(text.replace('Z', '+00:00'))

    def test_slots_are_the_published_cadence(self):
        self.assertEqual(self.slots, (4, 19, 34, 49))

    def test_next_slot_is_strictly_after_the_instant(self):
        cases = {
            '2026-10-23T08:32:56Z': '2026-10-23T08:34:00Z',
            '2026-10-23T08:34:00Z': '2026-10-23T08:49:00Z',
            '2026-10-23T08:34:01Z': '2026-10-23T08:49:00Z',
            '2026-10-23T08:49:00Z': '2026-10-23T09:04:00Z',
            '2026-10-23T08:50:00Z': '2026-10-23T09:04:00Z',
            '2026-10-23T23:59:30Z': '2026-10-24T00:04:00Z',
        }
        for given, expected in cases.items():
            self.assertEqual(self.next_slot(given), self.utc(expected), given)

    def test_next_check_stays_the_named_entry_point(self):
        self.assertEqual(self.next_check('2026-10-23T08:32:56.593552Z'),
                         self.utc('2026-10-23T08:34:00Z'))

    def test_unparseable_and_missing_inputs_return_none(self):
        for bad in (None, '', 'not-a-date', {}):
            self.assertIsNone(self.next_check(bad), bad)


class FreshnessStripMarkup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Render the executive summary from the committed snapshot with the
        # build's own entry point, so this test never depends on a local
        # ``public/`` directory existing (the CI unit step runs before a build).
        from scripts import build
        cls.html = build.overview(copy.deepcopy(DATA))

    def test_strip_has_a_recomputable_slot(self):
        self.assertIn('data-slot-minutes="4,19,34,49"', self.html)
        match = re.search(r'<span id="next-slot">next slot (\d\d):(\d\d) UTC</span>', self.html)
        self.assertIsNotNone(match, 'the build states a fallback slot inside #next-slot')
        minute = int(match.group(2))
        self.assertIn(minute, (4, 19, 34, 49))

    def test_build_time_slot_is_after_the_snapshot(self):
        observed = DATA['generated_at']
        slot = re.search(r'<span id="next-slot">next slot (\d\d):(\d\d) UTC</span>', self.html)
        self.assertIsNotNone(slot)
        stamp = datetime.fromisoformat(observed.replace('Z', '+00:00'))
        candidate = stamp.replace(hour=int(slot.group(1)), minute=int(slot.group(2)),
                                  second=0, microsecond=0)
        if candidate <= stamp:
            candidate += timedelta(hours=1)
        self.assertGreater(candidate, stamp)

    def test_strip_carries_a_runtime_age(self):
        self.assertIn('<span class="fresh-age" id="fresh-age"></span>', self.html)

    def test_app_js_recomputes_both_values(self):
        js = (ROOT / 'site/assets/app.js').read_text(encoding='utf-8')
        self.assertIn("querySelector('#next-slot')", js)
        self.assertIn("querySelector('#fresh-age')", js)
        self.assertIn('refresh target', js)
        self.assertIn('renderClock(now)', js)

    def test_stylesheet_marks_an_overdue_snapshot(self):
        css = (ROOT / 'site/assets/style.css').read_text(encoding='utf-8')
        self.assertIn('.fresh-strip .fresh-age[data-overdue="1"]', css)
        # Both copies are shipped: the build reads site/assets, the staged root
        # serves assets/. They must stay byte-identical (also pinned elsewhere).
        self.assertEqual((ROOT / 'assets/style.css').read_bytes(),
                         (ROOT / 'site/assets/style.css').read_bytes())
        self.assertEqual((ROOT / 'assets/app.js').read_bytes(),
                         (ROOT / 'site/assets/app.js').read_bytes())


class BoardAuditorAcceptsTheCommittedSnapshot(unittest.TestCase):
    def test_committed_snapshot_passes_every_check(self):
        auditor, data, counts = run_audit(DATA)
        self.assertEqual(auditor.failures, [])
        self.assertGreater(len(auditor.checks), 500)
        self.assertEqual(counts['rows'], len(DATA['matches']))
        self.assertEqual(counts['open'], counts['picked'])

    def test_every_priced_row_was_recomputed_from_its_own_raw_fields(self):
        auditor, data, _ = run_audit(DATA)
        priced = [r for r in data['matches'] if r.get('probabilities')]
        self.assertTrue(priced)
        recomputed = [r for r in auditor.rows if r['max_error'] is not None]
        self.assertEqual(len(recomputed), len(priced))
        self.assertLessEqual(max(r['max_error'] for r in recomputed), 1e-6)


class BoardAuditorRejectsCorruption(unittest.TestCase):
    """Each mutation must produce at least one failure with a matching reason."""

    def first_priced(self, payload):
        for row in payload['matches']:
            if row.get('probabilities'):
                return row
        self.fail('the committed snapshot has paved rows')

    def assertRejected(self, payload, needle):
        auditor, _, _ = run_audit(payload)
        self.assertTrue(auditor.failures, 'the auditor must reject this corruption')
        labels = ' | '.join(f['label'] + ' ' + f['detail'] for f in auditor.failures)
        self.assertIn(needle, labels, labels)

    def test_probability_that_no_longer_sums_to_one(self):
        payload = copy.deepcopy(DATA)
        row = self.first_priced(payload)
        row['probabilities'] = [row['probabilities'][0] + 0.1, row['probabilities'][1]]
        self.assertRejected(payload, 'probabilities sum to 1')

    def test_probability_edited_away_from_its_source(self):
        payload = copy.deepcopy(DATA)
        row = self.first_priced(payload)
        p = row['probabilities']
        row['probabilities'] = [p[1], p[0]]  # swap: still sums to 1, now wrong side
        self.assertRejected(payload, 'match the recomputation')

    def test_pick_that_is_not_the_larger_probability(self):
        payload = copy.deepcopy(DATA)
        row = self.first_priced(payload)
        row['pick'] = row['teams'][1] if row['pick'] == row['teams'][0] else row['teams'][0]
        self.assertRejected(payload, 'larger probability')

    def test_pick_that_is_not_one_of_the_teams(self):
        payload = copy.deepcopy(DATA)
        self.first_priced(payload)['pick'] = 'Some Other Team'
        self.assertRejected(payload, 'not one of the two teams')

    def test_open_row_with_no_pick(self):
        payload = copy.deepcopy(DATA)
        row = self.first_priced(payload)
        row.update(pick=None, probabilities=None, fair_odds=None, method=None)
        row['reason'] = ''
        self.assertRejected(payload, 'unresolved row states its reason')

    def test_research_tier_smuggling_a_probability(self):
        payload = copy.deepcopy(DATA)
        self.first_priced(payload)['method'] = 'research_rank'
        self.assertRejected(payload, 'research tier publishes no number')

    def test_fair_odds_that_are_not_one_over_p(self):
        payload = copy.deepcopy(DATA)
        row = self.first_priced(payload)
        row['fair_odds'] = [1.01, 1.01]
        self.assertRejected(payload, 'fair odds are 1/p')

    def test_model_points_edited(self):
        payload = copy.deepcopy(DATA)
        row = next(r for r in payload['matches'] if r.get('method') == 'model_vrs')
        row['evidence'][0]['points'] = [999, 1]
        self.assertRejected(payload, 'match the recomputation')

    def test_listing_odds_edited(self):
        payload = copy.deepcopy(DATA)
        row = next(r for r in payload['matches'] if r.get('method') == 'bookmaker_fallback')
        row['evidence'][0]['raw']['odds'] = [1.10, 8.00]
        self.assertRejected(payload, 'match the recomputation')

    def test_expiry_beyond_the_match_start(self):
        payload = copy.deepcopy(DATA)
        row = self.first_priced(payload)
        start = datetime.fromisoformat(row['start'].replace('Z', '+00:00'))
        row['expires_at'] = (start + timedelta(minutes=5)).isoformat().replace('+00:00', 'Z')
        self.assertRejected(payload, 'expiry not after the match start')

    def test_expiry_beyond_the_evidence_window(self):
        payload = copy.deepcopy(DATA)
        stamp = datetime.fromisoformat(payload['fixtures_observed_at'].replace('Z', '+00:00'))
        # A row whose own lock and start are far enough away that only the
        # 8-hour evidence rule can reject the expiry we write.
        row = next(r for r in payload['matches']
                   if r.get('probabilities') and r['state'] == 'open'
                   and datetime.fromisoformat(r['start'].replace('Z', '+00:00')) > stamp + timedelta(hours=12))
        seen = datetime.fromisoformat(row['evidence'][0]['observed_at'].replace('Z', '+00:00'))
        row['expires_at'] = (seen + timedelta(hours=9)).isoformat().replace('+00:00', 'Z')
        self.assertRejected(payload, '8-hour evidence window')

    def test_hotspawn_carrying_a_price(self):
        payload = copy.deepcopy(DATA)
        row = self.first_priced(payload)
        row['evidence'][0]['provider'] = 'Hotspawn'
        row['evidence'][0]['odds'] = [1.5, 2.5]
        self.assertRejected(payload, 'Hotspawn evidence carries no price')

    def test_duplicate_fixture_id(self):
        payload = copy.deepcopy(DATA)
        payload['matches'][1]['id'] = payload['matches'][0]['id']
        self.assertRejected(payload, 'fixture ids are unique')

    def test_open_row_that_already_started(self):
        payload = copy.deepcopy(DATA)
        row = self.first_priced(payload)
        row['start'] = payload['generated_at']
        self.assertRejected(payload, 'open row starts after the snapshot')

    def test_non_open_row_that_keeps_a_pick(self):
        payload = copy.deepcopy(DATA)
        closed = next(r for r in payload['matches'] if r.get('state') != 'open')
        closed.update(pick=closed['teams'][0], probabilities=[0.6, 0.4], fair_odds=[1.67, 2.5],
                      method='exchange')
        self.assertRejected(payload, 'non-open row publishes no pick or number')

    def test_missing_evidence_on_a_picked_row(self):
        payload = copy.deepcopy(DATA)
        self.first_priced(payload)['evidence'] = []
        self.assertRejected(payload, 'picked row keeps its evidence')

    def test_missing_expiry_on_a_priced_row(self):
        payload = copy.deepcopy(DATA)
        self.first_priced(payload)['expires_at'] = None
        self.assertRejected(payload, 'priced row has no expiry')


if __name__ == '__main__':
    unittest.main()
