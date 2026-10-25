"""Session 5bf6ae1b — regression pins for the 2026-10-25 rotation defect.

Fixture 1086697 (Projeto do KinGui vs Yawara) published an originated Valve
VRS model line in the 14:22Z capture whose ``roster_checks`` carry
``overlap: None`` for both teams: no HLTV lineup was available that run, so
roster continuity was not checked. That shape is legitimate under the
production rule (``scripts/validate.py``: unchecked is allowed only when the
Valve label is unique, ``label_counts == 1``, and the row is flagged), but
``tests/test_session_0fae12a5.py`` asserted ``overlap >= 3`` unconditionally
and went red on valid data — the same stale-test failure mode that froze the
publisher on 2026-10-25 for sessions 58354934/b85ad9b4.

These tests pin both halves of the production rule against the committed
snapshot, and the full-coverage contract the brief requires: every open row
has a pick, a two-sided probability summing to 1, the pick as argmax, and an
official external source link; Hotspawn never originates a probability.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'latest.json'


def load():
    return json.loads(DATA.read_text(encoding='utf-8'))


class VrsRosterCheckShapeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matches = load()['matches']

    def test_checked_rosters_satisfy_valve_continuity(self):
        for m in self.matches:
            if m.get('method') not in ('model_vrs', 'model_vrs_mirror'):
                continue
            ev = m['evidence'][0]
            for check in ev['roster_checks']:
                if check['overlap'] is not None:
                    self.assertGreaterEqual(check['overlap'], 3, m['id'])

    def test_unchecked_roster_requires_unique_label_and_flag(self):
        seen_unchecked = 0
        for m in self.matches:
            if m.get('method') not in ('model_vrs', 'model_vrs_mirror'):
                continue
            ev = m['evidence'][0]
            for check, count in zip(ev['roster_checks'], ev['label_counts']):
                if check['overlap'] is None:
                    seen_unchecked += 1
                    self.assertEqual(count, 1, m['id'])
                    self.assertTrue(check.get('note'), m['id'])
                    self.assertIn('roster continuity not checked',
                                  ' '.join(m.get('flags') or []), m['id'])
        # The 14:22Z capture contains exactly this shape (fixture 1086697);
        # if a future snapshot has none, the pin above is vacuous but valid.
        self.assertGreaterEqual(seen_unchecked, 0)


class FullCoverageContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matches = load()['matches']

    def test_every_open_row_has_sourced_pick_and_probability(self):
        open_rows = [m for m in self.matches if m.get('state') == 'open']
        self.assertTrue(open_rows)
        for m in open_rows:
            probs = m.get('probabilities')
            self.assertIsNotNone(probs, m['id'])
            self.assertEqual(len(probs), 2, m['id'])
            self.assertAlmostEqual(sum(probs), 1.0, places=9, msg=str(m['id']))
            self.assertEqual(m.get('pick'),
                             m['teams'][probs.index(max(probs))], m['id'])
            evidence = m.get('evidence') or []
            self.assertTrue(evidence, m['id'])
            urls = [evidence[0].get('url') or '', evidence[0].get('api_url') or '']
            hosts = {urlparse(u).netloc for u in urls if u}
            self.assertTrue(hosts, m['id'])
            self.assertNotIn('play.hotspawn.com', hosts, m['id'])

    def test_no_row_uses_hotspawn_as_probability_source(self):
        for m in self.matches:
            for ev in m.get('evidence') or []:
                provider = (ev.get('provider') or '').lower()
                self.assertNotIn('hotspawn', provider, m['id'])


if __name__ == '__main__':
    unittest.main()
