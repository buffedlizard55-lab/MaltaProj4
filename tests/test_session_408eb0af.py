"""Session 408eb0af — the roster-provenance gate, and a backstop that cannot freeze the board.

Measured, not assumed
--------------------
The scheduled publisher failed at step 13 ("Build and independently verify every
row, calculation and internal link") on 2026-10-24T23:40Z (run 40143667147),
2026-10-25T06:56Z (40170923727) and 2026-10-25T12:29Z (40193317196), so nothing
deployed and the site withheld every pick once the committed snapshot left its
eight-hour window.

Two sessions replayed the same failure independently on GitHub's egress:

* this session's replay, run 40197625638, committed at
  `research/session-408eb0af/report-40197625638.md`, and
* session b85ad9b4's replay, run 40197667220, committed at
  `research/session-b85ad9b4/logs/`,

and both returned `refresh=0 quarantine=0 audit=0 build=0 unittest=0`,
`validate=1`, with one assertion:

    AssertionError: Model roster has no HLTV source on this row

on fixture 1086697, Projeto do KinGui vs Yawara (CCT South America 2026 Series
#7). The row's roster is proven by HLTV match 2399918, whose heading for that
club reads "Tropa do KinGui", while the Hotspawn label is "Projeto do KinGui".
Both spellings sit in one sourced entry of `data/identities.json`.

The fix shipped in PR #316 (session b85ad9b4): `scripts.validate.same_club`
bridges the two labels **only** through a register entry that links an https
source and keeps the fixture's two teams apart. This session verified that tree
independently — the full unit suite and `scripts.validate` both pass on the very
snapshot the publisher refused — and merged it rather than shipping a second,
parallel implementation of the same rule.

What this module still owns
---------------------------
The gap that let one row take the whole board down. `scripts.quarantine` runs
*before* build in the publisher and already withholds single rows the
independent audit cannot reproduce; a certificate the validator cannot issue had
no such path, so it failed the run. `roster_lineage_violations` gives the
validator's own assertion that row-level path, so a future unprovable roster
blanks one row and flags it instead of freezing publication. It re-uses
`scripts.validate.lineup_source_ok`, so the two can never disagree.
"""
import copy
import json
import unittest
from pathlib import Path

from scripts import quarantine, validate
from scripts.core import dt

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / 'research/session-b85ad9b4/snapshot.json'


def captured_row(fixture_id='1086697'):
    """The exact row the failing publication refused to build."""
    data = json.loads(CAPTURE.read_text(encoding='utf-8'))
    return copy.deepcopy(next(m for m in data['matches'] if str(m['id']) == str(fixture_id)))


class ShippedRuleTests(unittest.TestCase):
    """The rule that shipped in #316, re-checked from this session's side."""

    def test_registered_pair_is_one_club(self):
        row = captured_row()
        self.assertTrue(validate.same_club(row, 'Projeto do KinGui', 'Tropa do KinGui'))
        self.assertEqual(row['hltv_context']['lineups'][0]['team'], 'Tropa do KinGui')

    def test_exact_label_is_always_accepted(self):
        row = captured_row()
        self.assertTrue(validate.same_club(row, 'Yawara', 'yawara'))

    def test_unregistered_spelling_is_refused(self):
        row = captured_row()
        self.assertFalse(validate.same_club(row, 'Projeto do KinGui', 'Projeto KinGui'),
                         'a plausible spelling that is not in the register must never pass')
        self.assertFalse(validate.same_club(row, 'Projeto do KinGui', 'Tropa do KinGui Esports'))

    def test_players_must_still_match_exactly(self):
        row = captured_row()
        quote = row['evidence'][0]
        wrong = list(quote['roster_checks'][0]['lineup'])[:-1] + ['someone-else']
        self.assertFalse(validate.lineup_source_ok(row, row['teams'][0], wrong))


class PublicationBackstopTests(unittest.TestCase):
    def test_captured_row_is_not_withheld(self):
        self.assertEqual(quarantine.contract_violations(captured_row()), [])

    def test_unprovable_model_row_is_withheld_rather_than_frozen(self):
        row = captured_row()
        row['hltv_context']['lineups'][0]['team'] = 'Projeto KinGui'  # plausible, unregistered
        self.assertEqual(quarantine.contract_violations(row),
                         ['Model roster for %s has no HLTV source on this row' % row['teams'][0]])

    def test_backstop_ignores_rows_it_cannot_judge(self):
        row = captured_row()
        market = dict(row, method='exchange')
        market['evidence'] = [{'provider': 'Polymarket'}]
        self.assertEqual(quarantine.contract_violations(market), [])
        research = dict(row, probabilities=None, pick=row['pick'], method='research_rank', evidence=[])
        self.assertEqual(quarantine.contract_violations(research), [])
        bare = copy.deepcopy(row)
        bare['hltv_context'].pop('lineups', None)
        bare['hltv_team_pages'] = None
        self.assertEqual(quarantine.contract_violations(bare), [])

    def test_the_whole_captured_board_validates(self):
        """The publisher's own gate over every row of the captured snapshot."""
        data = json.loads(CAPTURE.read_text(encoding='utf-8'))
        now = dt(data['generated_at'])
        open_rows = [m for m in data['matches'] if m['state'] == 'open']
        self.assertEqual(len(open_rows), 17)
        for row in open_rows:
            self.assertIn(row['pick'], row['teams'], 'open row %s has no directional pick' % row['id'])
            self.assertAlmostEqual(sum(row['probabilities']), 1.0, places=12)
            self.assertEqual(quarantine.contract_violations(row), [])
        for row in data['matches']:
            if row.get('method') == 'model_vrs' and row.get('evidence'):
                validate.validate_model_row(row, row['evidence'][0], now)


if __name__ == '__main__':
    unittest.main()
