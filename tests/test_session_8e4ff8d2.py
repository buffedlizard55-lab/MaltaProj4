"""Session 8e4ff8d2: the publish freeze of 2026-10-25, and the two repairs.

Measured, not assumed. The live board was withholding every pick because the
committed snapshot (2026-10-25T01:47:42Z) had left its eight-hour window, and the
scheduled publisher had stopped completing: runs 40170923727 (06:56Z) and
40193317196 (12:29Z) failed at *Build and independently verify every row,
calculation and internal link* after the refresh and quarantine had both passed.
A non-publishing diagnostic run (40197572628) reproduced the step by step and
named it: ``scripts.validate`` exit 1 with ``AssertionError: Model roster has no
HLTV source on this row``.

The row was Hotspawn fixture ``1086697`` -- *Projeto do KinGui* vs *Yawara* in
CCT South America 2026 Series #7. The model tier priced it from Valve's own
standings row for *ex-Keyd Stars* after verifying the roster against HLTV, whose
match page labels the same club *Tropa do KinGui*; that mapping is a registered,
primary-sourced alias (``data/identities.json``, and the row's own
``identity_sources``). Every pricing tier already resolved the alias, but
``lineup_source_ok`` compared the lineup's team label to the Hotspawn label
exactly, so the roster evidence the model had just used was declared unsourced.
One row was therefore enough to stop the whole board from publishing.

These tests pin both repairs and the measurement path that found them.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from scripts import validate

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'research' / 'session-8e4ff8d2' / 'snapshot-40197572628.json'
DIAG = ROOT / 'scripts' / 'diag_8e4ff8d2.py'

REGISTERED = ['drg', 'ALLE', 'ckzao', 'xureba', 'lash']


class AliasRosterSourceTests(unittest.TestCase):
    """The roster evidence for a registered rename is sourced, not fuzzy."""

    def row(self, **extra):
        row = {'id': '1086697', 'teams': ['Projeto do KinGui', 'Yawara'],
               'hltv_context': {'lineups': [
                   {'team': 'Tropa do KinGui', 'players': REGISTERED},
                   {'team': 'Yawara', 'players': ['brn$', 'j0w', 'deemO', 'tele', 'mlhzin']},
               ]}}
        row.update(extra)
        return row

    def test_registered_alias_label_is_a_valid_lineup_source(self):
        self.assertTrue(validate.same_club(self.row(), 'Projeto do KinGui', 'Tropa do KinGui'))
        self.assertTrue(validate.lineup_source_ok(self.row(), 'Projeto do KinGui', REGISTERED))

    def test_unregistered_label_is_still_refused(self):
        self.assertFalse(validate.same_club(self.row(), 'Projeto do KinGui', 'Some Other Club'))

    def test_alias_does_not_excuse_a_different_roster(self):
        self.assertFalse(validate.lineup_source_ok(self.row(), 'Projeto do KinGui', REGISTERED + ['Invented Player']))

    def test_an_unlinked_alias_is_not_a_bridge(self):
        """Only a primary-sourced register entry maps two spellings; nothing else."""
        row = {'id': 'x', 'teams': ['Alpha', 'Beta']}
        self.assertFalse(validate.same_club(row, 'Alpha', 'Alpha Esports'))

    def test_register_entries_pin_a_primary_source(self):
        register = json.loads((ROOT / 'data' / 'identities.json').read_text())
        entry = next(i for i in register['aliases'] if i['canonical'] == 'Tropa do KinGui')
        self.assertIn('Projeto do KinGui', entry['names'])
        self.assertTrue(entry['source'].startswith('https://www.hltv.org/matches/'))

    def test_the_real_capture_now_validates(self):
        """The exact row that froze publication is accepted by the real validator."""
        snapshot = json.loads(SNAPSHOT.read_text())
        row = next(m for m in snapshot['matches'] if m['id'] == '1086697')
        quote = row['evidence'][0]
        for team, check in zip(row['teams'], quote['roster_checks']):
            self.assertTrue(validate.lineup_source_ok(row, team, check['lineup']),
                            f'{team} roster has no reproducible HLTV source')


class ShortPhoneLayoutTests(unittest.TestCase):
    """Both served stylesheets carry the same short-phone compaction."""

    FILES = (ROOT / 'site' / 'assets' / 'style.css', ROOT / 'assets' / 'style.css')

    def test_served_stylesheets_are_identical_and_balanced(self):
        first, second = (path.read_text() for path in self.FILES)
        self.assertEqual(first, second, 'the served stylesheet drifted from the canonical copy')
        self.assertEqual(first.count('{'), first.count('}'), 'unbalanced braces nest later phone rules')

    def test_short_phone_block_keeps_both_probabilities_on_the_first_screen(self):
        for path in self.FILES:
            text = path.read_text()
            block = re.search(
                r'@media\(max-width:650px\) and \(max-height:700px\)\{(?:(?!\n\}).)*?prob-team-labels span'
                r'\{(?:(?!\}).)*?white-space:nowrap', text, re.S)
            self.assertIsNotNone(block, f'{path.name} lost the short-phone probability compaction')


class DiagnosticTests(unittest.TestCase):
    """The measurement path that named the defect keeps working offline."""

    def test_report_names_the_failing_command(self):
        import tempfile

        module = __import__('scripts.diag_8e4ff8d2', fromlist=['main'])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'diag.env').write_text('build_rc=0\nvalidate_rc=1\n')
            (root / 'validate.log').write_text(
                'Traceback (most recent call last):\n'
                "AssertionError: Model roster has no HLTV source on this row\n")
            report = module.collect(root)
            self.assertEqual(report['failing'], ['validate (public/)'])
            markdown = module.render_markdown(report)
            self.assertIn('Model roster has no HLTV source', markdown)
            annotations = module.annotation_lines(report)
            self.assertTrue(any('validate (public/)' in line for line in annotations))

    def test_workflow_never_publishes(self):
        workflow = (ROOT / '.github' / 'workflows' / 'diag-8e4ff8d2.yml').read_text()
        uses = [line for line in workflow.splitlines()
                if line.strip().lstrip('- ').startswith('uses:')]
        self.assertTrue(uses, 'the diagnostic must still pin its actions')
        for forbidden in ('deploy-pages', 'upload-pages-artifact', 'publish_root_fallback --public'):
            self.assertFalse(any(forbidden in line for line in uses),
                             f'the diagnostic must never publish ({forbidden})')
        self.assertIn('::error title=diag 8e4ff8d2::', DIAG.read_text())


if __name__ == '__main__':
    unittest.main()
