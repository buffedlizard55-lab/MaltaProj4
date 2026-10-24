"""Session e334b970: the board must be refreshable, and the report must be re-derivable.

Two defects are covered here, both reproduced before they were repaired.

1. **A pinned calendar day stopped publication.** ``tests/test_session_f89bb1f8``
   asserted the literal string ``'23 Oct'`` in the phone freshness strip. The
   strip prints the *next pick's* start date from whatever snapshot is built, so
   the assertion was true only for one day's board. It is one of the reasons the
   scheduled publish never reached its refresh step.

2. **A pinned lobby set stopped publication.** ``tests/test_session_0cc1138a``
   pinned 30 fixture IDs from the 2026-10-23T09:44Z lobby read; Hotspawn later
   stopped serving ``1079655``, and because it was already missing from the
   11:25Z baseline, ``inventory_changes.removed_ids`` never named it, so the
   suite failed on every later snapshot. Repaired on ``main`` by sessions
   019a253a/d2a55add (parity now checked against the retained archive and the
   snapshot's own ``coverage_counts``, and covered by
   ``tests/test_session_019a253a.py``); this file keeps the rotation-proof
   half - the scanner below - and does not duplicate that coverage.

The third group proves the coverage receipt (``scripts/audit_e334b970``) and the
independent re-derivation (``research/session-0cc1138a/verify_0cc1138a.py``)
cover **every** evidence tier the board actually publishes — the mirror tier was
priced in production while the independent verifier had no branch for it, so a
whole class of published percentages was never re-derived by the auditor.
"""
import copy
import importlib.util
import json
import re
import unittest
from pathlib import Path

from scripts import audit_e334b970

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())


def load_verifier():
    spec = importlib.util.spec_from_file_location(
        'verify_0cc1138a', ROOT / 'research' / 'session-0cc1138a' / 'verify_0cc1138a.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_verifier()

# A calendar day written into an assertion (`'23 Oct'`) can only be true for one
# board. These files load the live snapshot, so a literal day is a time bomb.
LIVE_SNAPSHOT_TESTS = ['test_session_f89bb1f8.py', 'test_session_0cc1138a.py']
MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')


class NoPinnedCalendarDay(unittest.TestCase):
    def test_live_snapshot_tests_do_not_assert_a_literal_day(self):
        offenders = []
        for name in LIVE_SNAPSHOT_TESTS:
            text = (ROOT / 'tests' / name).read_text()
            for number, line in enumerate(text.splitlines(), 1):
                if line.lstrip().startswith('#'):
                    continue
                if re.search(r"assert(In|Equal)\([^\n]*'(\d{1,2} (?:%s))'" % '|'.join(MONTHS), line):
                    offenders.append('%s:%d %s' % (name, number, line.strip()))
        self.assertEqual(offenders, [], 'a literal day in a live-snapshot assertion: %r' % offenders)


class EveryPricedTierIsReDerivable(unittest.TestCase):
    """No tier may publish a percentage the independent verifier cannot rebuild."""

    def test_every_open_priced_method_has_a_re_derivation_branch(self):
        audit = V.audit(SNAPSHOT)
        unverified = [(r['id'], r['method']) for r in audit if r['published'] and r['re_derived'] is None]
        self.assertEqual(unverified, [], 'priced rows the independent verifier cannot rebuild: %r' % unverified)

    def test_the_mirror_tier_reproduces_valve_expectation(self):
        mirror = [m for m in SNAPSHOT['matches']
                  if m['state'] == 'open' and m['method'] == 'model_vrs_mirror']
        if not mirror:
            self.skipTest('no mirror-tier row in this snapshot')
        for match in mirror:
            evidence = match['evidence'][0]
            expected = [V.calibrate(V.glicko_expect(*evidence['points'])),
                        1 - V.calibrate(V.glicko_expect(*evidence['points']))]
            for published, rebuilt in zip(match['probabilities'], expected):
                self.assertAlmostEqual(published, rebuilt, places=9, msg=match['id'])

    def test_the_mirror_branch_refuses_to_invent_points(self):
        with self.assertRaises(KeyError):
            V.evidence_probabilities({'provider': 'HLTV Valve ranking (Valve points)'})


class CoverageReceipt(unittest.TestCase):
    def test_counts_come_from_the_snapshot(self):
        receipt = audit_e334b970.build(copy.deepcopy(SNAPSHOT))
        opens = [m for m in SNAPSHOT['matches'] if m['state'] == 'open']
        self.assertEqual(receipt['counts']['open'], len(opens))
        self.assertEqual(receipt['counts']['open_with_pick'], sum(1 for m in opens if m.get('pick')))
        self.assertEqual(receipt['counts']['open_with_probability'],
                         sum(1 for m in opens if m.get('probabilities') is not None))
        self.assertEqual(receipt['board_rows'], len(SNAPSHOT['matches']))
        self.assertEqual(receipt['feed_rows'], len(SNAPSHOT['fixture_evidence']))

    def test_every_unresolved_row_carries_its_limitation_and_attempts(self):
        for row in audit_e334b970.build(copy.deepcopy(SNAPSHOT))['unresolved']:
            self.assertTrue(row['limitation'], row['id'])
            self.assertTrue(row['source_url'], row['id'])
            self.assertTrue(row['attempts'], row['id'])
            self.assertTrue(any(a.get('url') for a in row['attempts']), row['id'])

    def test_a_row_without_a_limitation_is_reported_not_hidden(self):
        snap = copy.deepcopy(SNAPSHOT)
        opens = [m for m in snap['matches'] if m['state'] == 'open']
        if not opens:
            self.skipTest('no open row')
        row = opens[0]
        row['probabilities'] = row['fair_odds'] = row['pick'] = row['method'] = None
        row['reason'] = ''
        receipt = audit_e334b970.build(snap)
        self.assertIn(row['id'], [r['id'] for r in receipt['unresolved']])
        self.assertTrue([p for p in receipt['contract']['problems'] if p.startswith(row['id'])],
                        'a blanks row with no stated limitation must be a contract problem')

    def test_the_receipt_never_turns_a_blank_into_a_number(self):
        snap = copy.deepcopy(SNAPSHOT)
        for match in snap['matches']:
            match['probabilities'] = None
            match['pick'] = None
            match['method'] = None
        receipt = audit_e334b970.build(snap)
        self.assertEqual(receipt['counts']['open_with_probability'], 0)
        self.assertEqual(receipt['counts']['open_with_pick'], 0)
        self.assertEqual(receipt['method_mix'], {})

    def test_the_markdown_states_the_capture_clock_it_used(self):
        text = audit_e334b970.markdown(audit_e334b970.build(copy.deepcopy(SNAPSHOT)))
        self.assertIn(SNAPSHOT['fixtures_observed_at'], text)
        self.assertIn("the capture's own clock", text)


class LiveHarvestIsNonPublishing(unittest.TestCase):
    """The capture workflow may commit receipts; it may never publish the site."""

    def setUp(self):
        self.text = (ROOT / '.github' / 'workflows' / 'harvest-e334b970.yml').read_text()

    def test_it_never_deploys_pages(self):
        self.assertNotIn('deploy-pages', self.text)
        self.assertNotIn('upload-pages-artifact', self.text)
        self.assertFalse(re.search(r'^\s*pages:\s*write', self.text, re.M))

    def test_it_only_pushes_its_own_branch(self):
        push_lines = [line.strip() for line in self.text.splitlines() if line.strip().startswith('git push')]
        self.assertTrue(push_lines)
        for line in push_lines:
            self.assertIn('arena/e334b970-maltaproj4', line)

    def test_it_runs_the_independent_auditor_before_the_receipt(self):
        refresh = self.text.index('scripts.refresh')
        audit = self.text.index('verification-c6/audit_snapshot.py runtime/latest.json')
        receipt = self.text.index('scripts.audit_e334b970')
        self.assertLess(refresh, audit)
        self.assertLess(audit, receipt)


if __name__ == '__main__':
    unittest.main()
