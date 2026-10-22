"""Session cf12d97f regressions: the publication gate must not expire on the
wall clock, and every committed snapshot must be internally consistent.

Defect repaired here
---------------------
The scheduled publication stopped on 2026-10-22 (run 39731049149 failed at
*Unit and independent failure-mode tests*). The failing assertion was
``tests/test_session_bf09aa40.py``::

    validate_model_row(row, quote, datetime.now(timezone.utc))

``row`` is a **historical committed capture**
(``research/harvest-bf09aa40/snapshot.json``, observed 2026-10-21T21:18:58Z).
``scripts.validate.validate_model_row`` re-checks the eight-hour evidence
window against the ``now`` it is given, so measuring that dated capture
against the wall clock makes the test fail exactly eight hours after the
capture - and, because the test gate runs before the refresh, it blocks every
publication slot from 2026-10-22T05:18Z onward.

The repair measures the dated capture against **its own capture time**. The
freshness gate itself is untouched and still rejects a stale row; the tests
below prove both halves of that.
"""
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.core import dt
from scripts.validate import validate_model_row

ROOT = Path(__file__).resolve().parents[1]
HARVEST_SNAPSHOT = json.loads((ROOT / 'research/harvest-bf09aa40/snapshot.json').read_text())


class TestHistoricalSnapshotReplay(unittest.TestCase):
    """The dated harvest capture must replay at its own capture time."""

    def setUp(self):
        self.row = next(m for m in HARVEST_SNAPSHOT['matches'] if m['id'] == '1082858')
        self.quote = self.row['evidence'][0]

    def test_the_row_replays_against_the_snapshot_capture_time(self):
        validate_model_row(self.row, self.quote, dt(HARVEST_SNAPSHOT['generated_at']))

    def test_the_eight_hour_gate_is_still_real(self):
        # Nine hours after the capture the same row is stale, exactly as the
        # live pipeline requires. The repair removed the wall-clock coupling,
        # not the evidence window.
        with self.assertRaises(AssertionError) as caught:
            validate_model_row(self.row, self.quote,
                               dt(HARVEST_SNAPSHOT['generated_at']) + timedelta(hours=9))
        self.assertIn('eight hours', str(caught.exception))

    def test_the_repaired_test_no_longer_measures_a_dated_capture_against_the_clock(self):
        source = (ROOT / 'tests/test_session_bf09aa40.py').read_text()
        self.assertNotIn('validate_model_row(row, quote, datetime.now(timezone.utc))', source,
                         'a dated capture must never be replayed against the wall clock')

    def test_every_committed_snapshot_is_fresh_at_its_own_capture_time(self):
        # General invariant: a snapshot's own evidence must be inside the
        # eight-hour window measured from that snapshot's generation time.
        for path in sorted(ROOT.glob('research/**/snapshot.json')):
            try:
                snapshot = json.loads(path.read_text())
            except (ValueError, OSError):
                continue
            generated = snapshot.get('generated_at')
            if not generated:
                continue
            for row in snapshot.get('matches') or []:
                for quote in row.get('evidence') or []:
                    observed = quote.get('observed_at')
                    if not observed:
                        continue
                    age = (dt(generated) - dt(observed)).total_seconds()
                    self.assertLess(age, 8 * 3600,
                                     '%s: %s has evidence older than the window at capture time'
                                     % (path.relative_to(ROOT), row.get('id')))
                    self.assertGreater(age, -600,
                                       '%s: %s evidence is dated after its capture'
                                       % (path.relative_to(ROOT), row.get('id')))

    def test_the_committed_harvest_capture_still_carries_its_own_numbers(self):
        # Guard against "fixing" the failure by editing the published numbers.
        self.assertEqual(self.row['method'], 'model_vrs')
        self.assertEqual(self.row['pick'], 'Off Chops')
        self.assertAlmostEqual(sum(self.row['probabilities']), 1.0, places=12)
        self.assertEqual(self.quote['points'], [878, 971])
        self.assertEqual(self.quote['observed_at'], '2026-10-21T21:18:58.286925Z')
        self.assertEqual(HARVEST_SNAPSHOT['generated_at'], '2026-10-21T21:18:58.345679Z')
        self.assertLess((dt(HARVEST_SNAPSHOT['generated_at'])
                         - dt('2026-10-21T21:18:58.286925Z')).total_seconds(), 60)


if __name__ == '__main__':
    unittest.main()
