"""Session f2e04d1a: a level market must never become a priced row with no pick.

Measured failure being pinned here (2026-10-24T16:37Z live snapshot): fixture
1079200 Color vs ex-Zero Tenacity returned a tight, two-sided Polymarket mid of
exactly 0.50/0.50. ``scripts.core.resolve`` stored those probabilities with
``pick=None``, and because every later tier is gated on ``probabilities is None``
the row could never be rescued. The published board then carried one priced row
with no directional pick; the unit suite (correctly) refuses that board, so every
scheduled publish from 09:03Z onwards failed at the root-fallback gate and the
live page withheld all picks once its snapshot aged past eight hours.

The rule: a level price is real evidence of *no market edge*, not a
recommendation. It is recorded as rejected evidence so the model and research
tiers can originate a dated pick of their own.
"""
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from scripts import core

ROOT = Path(__file__).resolve().parents[1]
START = '2026-10-25T18:00:00Z'


def fixture():
    return {
        'id': '1079200',
        'teams': ['Color', 'ex-Zero Tenacity'],
        'start': START,
        'lock': START,
        'state': 'open',
        'probabilities': None,
        'fair_odds': None,
        'pick': None,
        'method': None,
        'best_of': None,
        'evidence': [],
        'attempts': [],
        'flags': [],
    }


def candidate():
    return {
        'id': 'pm-1',
        'teams': ['Color', 'ex-Zero Tenacity'],
        'start': START,
        'api_url': 'https://gamma-api.polymarket.com/events/pm-1',
    }


def quote(p0, p1):
    return {
        'provider': 'Polymarket',
        'api_url': 'https://gamma-api.polymarket.com/events/pm-1',
        'url': 'https://polymarket.com/event/pm-1',
        'observed_at': '2026-10-24T16:00:00Z',
        'updated_at': '2026-10-24T16:00:00Z',
        'probabilities': [p0, p1],
        'raw': {},
        'tier': 'exchange',
    }


class LevelMarketCannotPick(unittest.TestCase):
    def resolve_with(self, probabilities):
        box = fixture()
        now = datetime.now(timezone.utc)
        with mock.patch.object(core, 'quote_polymarket',
                               return_value=quote(*probabilities)):
            core.resolve(box, [candidate()], 'Polymarket', now)
        return box

    def test_exactly_even_quote_is_rejected_and_left_unpriced(self):
        box = self.resolve_with([0.5, 0.5])
        self.assertIsNone(box['probabilities'], 'a level price must not become a probability')
        self.assertIsNone(box['fair_odds'])
        self.assertIsNone(box['pick'], 'a level price cannot support a directional pick')
        self.assertIsNone(box['method'])
        self.assertEqual(box['evidence'], [])
        self.assertEqual(len(box['attempts']), 1)
        attempt = box['attempts'][0]
        self.assertEqual(attempt['status'], 'unresolved',
                         'the ladder must continue, not stop the row')
        self.assertIn('exactly even', attempt['reason'])
        self.assertEqual(attempt['rejected_quote']['notice'],
                         'Rejected evidence, not a pick or verified probability.')

    def test_even_pair_inside_rounding_is_also_rejected(self):
        box = self.resolve_with([0.50004, 0.49996])
        self.assertIsNone(box['probabilities'])
        self.assertIn('exactly even', box['attempts'][0]['reason'])

    def test_a_real_edge_is_still_published_with_its_pick(self):
        box = self.resolve_with([0.62, 0.38])
        self.assertEqual(box['probabilities'], [0.62, 0.38])
        self.assertEqual(box['pick'], 'Color', 'pick must follow the larger probability')
        self.assertEqual(box['method'], 'exchange')
        self.assertAlmostEqual(box['fair_odds'][0], 1 / 0.62)
        self.assertEqual(box['attempts'][0]['status'], 'resolved')

    def test_orientation_is_kept_when_the_quote_is_reversed(self):
        # The real quote function returns probabilities in fixture order using
        # the `order` mapping, so the mock has to do the same to be faithful.
        box = fixture()

        def ordered(cand, order, now, **kwargs):
            return quote(0.30, 0.70).__class__ and dict(
                quote(0.30, 0.70),
                probabilities=[quote(0.30, 0.70)['probabilities'][i] for i in order])

        reversed_candidate = dict(candidate(), teams=['ex-Zero Tenacity', 'Color'])
        with mock.patch.object(core, 'quote_polymarket', side_effect=ordered):
            core.resolve(box, [reversed_candidate], 'Polymarket',
                         datetime.now(timezone.utc))
        self.assertEqual(box['probabilities'], [0.70, 0.30])
        self.assertEqual(box['pick'], 'Color')


class IndependentAuditRejectsAnEvenPair(unittest.TestCase):
    """The auditor is the gate that feeds quarantine; it must not sanction it."""

    def audit(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'independent_audit_snapshot',
            ROOT / 'verification-c6/audit_snapshot.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def committed(self):
        return json.loads((ROOT / 'data/latest.json').read_text())

    def test_every_priced_committed_row_has_a_directional_pick(self):
        data = self.committed()
        for row in data['matches']:
            if row.get('probabilities'):
                self.assertIsNotNone(row.get('pick'), row['id'])
                self.assertIn(row['pick'], row['teams'], row['id'])

    def test_a_violating_row_is_caught_by_the_publication_contract(self):
        # The rule lives in the publication path (scripts.quarantine), not in the
        # archive auditor, so historical snapshots that legitimately published an
        # even pair under the old rule stay auditable.
        from scripts import quarantine
        data = self.committed()
        row = next(m for m in data['matches']
                   if m.get('probabilities') and m.get('method') == 'exchange')
        row['probabilities'] = [0.5, 0.5]
        row['fair_odds'] = [2.0, 2.0]
        row['pick'] = None
        problems = quarantine.contract_violations(row)
        self.assertTrue(any('Exactly even published pair' in p for p in problems), problems)
        self.assertTrue(any('no directional pick' in p for p in problems), problems)

    def test_the_committed_snapshot_still_passes(self):
        rows, errors = self.audit().inspect(self.committed())
        self.assertEqual(errors, [], errors[:3])


class QuarantineTurnsAViolationIntoAVisibleBlank(unittest.TestCase):
    """A row that breaks the contract must be withheld, never freeze the board."""

    def test_withheld_row_carries_a_limitation_and_no_numbers(self):
        from scripts import quarantine
        data = json.loads((ROOT / 'data/latest.json').read_text())
        row = next(m for m in data['matches']
                   if m.get('probabilities') and m.get('method') == 'exchange')
        row['probabilities'] = [0.5, 0.5]
        row['fair_odds'] = [2.0, 2.0]
        row['pick'] = None
        failing, structural = quarantine.quarantine(data)
        self.assertEqual(structural, [])
        self.assertIn(row['id'], failing)
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['pick'])
        self.assertTrue(row['reason'].startswith('Withheld:'))
        self.assertIn('withheld', row)
        self.assertTrue(any('Exactly even published pair' in p
                            for p in row['withheld']['problems']))


class PublishGateKeepsTheHardStop(unittest.TestCase):
    """The intent of the guard is unchanged: a broken root is never committed."""

    def test_the_publisher_still_refuses_a_root_that_fails_its_own_gate(self):
        text = (ROOT / '.github/workflows/pages.yml').read_text()
        self.assertIn('python -m scripts.validate --data data/latest.json --site . || return 3', text)
        self.assertIn('python -m unittest discover -s tests || return 3', text)
        self.assertIn('[ "$rc" = "3" ]', text)


if __name__ == '__main__':
    unittest.main()
