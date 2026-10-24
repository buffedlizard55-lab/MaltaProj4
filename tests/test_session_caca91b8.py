"""Session caca91b8 — offline regression & line-by-line verification suite.

Universal live-board assertions never pin rotating match IDs or transient prices
on ``data/latest.json``; dated 2026-10-24T16:50Z fixture arithmetic is verified
against the immutable retained runner receipt ``research/session-caca91b8/snapshot.json``.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.audit_caca91b8 import (
    ROOT,
    audit_site,
    audit_snapshot,
    independent_glicko_calibrated,
    load_sourced_alias_map,
    load_vrs_standings,
    replay_row_independently,
)

LATEST_PATH = ROOT / 'data' / 'latest.json'
RETAINED_PATH = ROOT / 'research' / 'session-caca91b8' / 'snapshot.json'
NOTES_PATH = ROOT / 'data' / 'review-notes.json'
AUDIT_DOC = ROOT / 'verification-caca91b8' / 'LINE_BY_LINE_AUDIT.md'


class UniversalLiveBoardAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.latest = json.loads(LATEST_PATH.read_text(encoding='utf-8'))

    def test_every_committed_row_passes_independent_zero_shared_code_audit(self) -> None:
        report = audit_snapshot(self.latest, ROOT)
        self.assertEqual(report['errors'], [], '\n'.join(report['errors']))
        self.assertGreater(report['rows_total'], 0)

    def test_no_hotspawn_probability_contamination_anywhere(self) -> None:
        for row in self.latest['matches']:
            for ev in row.get('evidence') or []:
                for key in ('url', 'api_url', 'provider'):
                    val = str(ev.get(key) or '').lower()
                    self.assertNotIn('hotspawn', val, row['id'])
                    self.assertNotIn('cloudwaysapps', val, row['id'])

    def test_built_root_site_exposes_unfolded_executive_links_and_review_notes(self) -> None:
        report = audit_site(ROOT, ROOT)
        self.assertEqual(report['errors'], [], '\n'.join(report['errors']))
        self.assertEqual(report['session_review_notes_checked'], 3)


class CorruptionAndTieRefusalGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.retained = json.loads(RETAINED_PATH.read_text(encoding='utf-8'))

    def test_symmetric_fifty_fifty_probability_is_refused(self) -> None:
        mutated = copy.deepcopy(self.retained)
        open_row = next(m for m in mutated['matches'] if m['state'] == 'open')
        open_row['probabilities'] = [0.5, 0.5]
        open_row['fair_odds'] = [2.0, 2.0]
        report = audit_snapshot(mutated, ROOT)
        self.assertTrue(any('50/50' in err for err in report['errors']), report['errors'])

    def test_hotspawn_evidence_host_is_refused(self) -> None:
        mutated = copy.deepcopy(self.retained)
        open_row = next(m for m in mutated['matches'] if m['state'] == 'open')
        open_row['evidence'][0]['url'] = 'https://play.hotspawn.com/cs2-pickems'
        report = audit_snapshot(mutated, ROOT)
        self.assertTrue(any('Hotspawn' in err for err in report['errors']), report['errors'])

    def test_non_featured_row_skipping_hltv_before_books_is_refused(self) -> None:
        mutated = copy.deepcopy(self.retained)
        non_ex = next(
            m for m in mutated['matches']
            if m['state'] == 'open' and m['method'] != 'exchange'
        )
        non_ex['attempts'] = [a for a in non_ex['attempts'] if a.get('provider') != 'HLTV']
        report = audit_snapshot(mutated, ROOT)
        self.assertTrue(any('HLTV' in err for err in report['errors']), report['errors'])

    def test_e9be3e6b_never_overwrites_0806z_archive_with_live_snapshot(self) -> None:
        src = (ROOT / 'tests' / 'test_session_e9be3e6b.py').read_text(encoding='utf-8')
        self.assertNotIn(
            "by_id.update({m['id']: m for m in SNAPSHOT['matches'] if m['id'] in ('1082859', '1081152')})",
            src,
        )


class RetainedCapture1650ZVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.snap = json.loads(RETAINED_PATH.read_text(encoding='utf-8'))
        cls.by_id = {m['id']: m for m in cls.snap['matches']}
        cls.alias_map = load_sourced_alias_map()
        cls.vrs_by_rank = load_vrs_standings()

    def test_retained_capture_has_full_4_way_parity_and_22_priced_open_picks(self) -> None:
        report = audit_snapshot(self.snap, ROOT)
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['coverage'], 'verified')
        self.assertEqual(report['coverage_counts'], {'api': 83, 'page': 83, 'lobby': 83, 'retained': 83})
        self.assertEqual(report['rows_open'], 22)
        self.assertEqual(report['probabilities_reproduced'], 22)

    def test_1079200_even_exchange_continues_to_valve_vrs_model(self) -> None:
        row = self.by_id['1079200']
        self.assertEqual(row['teams'], ['Color', 'ex-Zero Tenacity'])
        self.assertEqual(row['method'], 'model_vrs')
        self.assertEqual(row['pick'], 'Color')
        pm_attempts = [a for a in row['attempts'] if a.get('provider') == 'Polymarket' and a.get('rejected_quote')]
        self.assertGreaterEqual(len(pm_attempts), 1)
        self.assertEqual(pm_attempts[0]['status'], 'unresolved')
        self.assertEqual(json.loads(pm_attempts[0]['rejected_quote']['raw']['outcomePrices']), ['0.5', '0.5'])
        _, cal = independent_glicko_calibrated(1249, 1066)
        self.assertAlmostEqual(row['probabilities'][0], cal[0], places=12)
        self.assertAlmostEqual(row['probabilities'][0], 0.6883951727580038, places=12)

    def test_non_featured_bookmaker_and_mirror_rows_reproduce_to_12_places(self) -> None:
        # 1083123 Grêmio vs Yawara: Thunderpick via BO3.gg 2.94 / 1.34
        p_1083123, m_1083123 = replay_row_independently(self.by_id['1083123'], self.alias_map, self.vrs_by_rank)
        self.assertEqual(m_1083123, 'bookmaker_fallback')
        self.assertAlmostEqual(p_1083123[1], (1 / 1.34) / ((1 / 2.94) + (1 / 1.34)), places=12)
        self.assertEqual(self.by_id['1083123']['pick'], 'Yawara')

        # 1081156 Spirit Academy vs LFO 10: Sökerorg refused, HLTV dated Valve ranking 1042 vs 819
        row_1081156 = self.by_id['1081156']
        self.assertEqual(row_1081156['method'], 'model_vrs_mirror')
        self.assertEqual(row_1081156['pick'], 'Spirit Academy')
        _, cal_1081156 = independent_glicko_calibrated(1042, 819)
        self.assertAlmostEqual(row_1081156['probabilities'][0], cal_1081156[0], places=12)
        pm_cand = next(a for a in row_1081156['attempts'] if a.get('candidates'))
        self.assertEqual(pm_cand['status'], 'unresolved')
        self.assertIn('Sökerorg', pm_cand['candidates'][0]['teams'])

        # 1082792 HOTU vs The Huns (1437 vs 944) and 1082793 5star vs 1WIN (1110 vs 1383)
        self.assertAlmostEqual(self.by_id['1082792']['probabilities'][0], independent_glicko_calibrated(1437, 944)[1][0], places=12)
        self.assertAlmostEqual(self.by_id['1082793']['probabilities'][1], independent_glicko_calibrated(1110, 1383)[1][1], places=12)

    def test_review_notes_and_audit_ledger_are_committed_and_formatted(self) -> None:
        raw_notes = NOTES_PATH.read_text(encoding='utf-8')
        parsed = json.loads(raw_notes)
        self.assertEqual(raw_notes, json.dumps(parsed, indent=1, ensure_ascii=False) + '\n')
        by_note_id = {n['id']: n for n in parsed}
        for nid in (
            'session-caca91b8-archive-overwrite-defect-2026-10-24',
            'session-caca91b8-cross-source-divergence-audit-2026-10-24',
            'session-caca91b8-orgless-identity-and-book-access-2026-10-24',
        ):
            self.assertIn(nid, by_note_id)
            self.assertGreaterEqual(len(by_note_id[nid]['sources']), 3)
        self.assertTrue(AUDIT_DOC.exists())
        self.assertIn('40113090316', AUDIT_DOC.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
