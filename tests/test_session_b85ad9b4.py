"""Session b85ad9b4: the 2026-10-25 publisher failure and the alias bridge it exposed.

What was measured
-----------------
The public board read "Last checked 25 Oct 2026 · 01:47 UTC", 14 open matches, **0 with a
pick**, 0 with a win probability, "Snapshot expired or timestamp unverified: all current
picks are withheld". The schedule was running; the publisher was not. On `main` (`6ade440`):

| Run | Slot | Result |
| --- | --- | --- |
| 40151731896 | 01:43Z | success — stamped `build-info.json` at `01:47:42Z` |
| 40143667147 | 23:40Z | failure at *Build and independently verify every row, calculation and internal link* |
| 40170923727 | 06:56Z | same step |
| 40193317196 | 12:29Z | same step, so no artifact, so `deploy` failed with *No artifacts named "github-pages"* |

This sandbox has no egress to Hotspawn, HLTV or Polymarket and this repository's job logs
redirect to blob storage outside the host allowlist, so the failing step could not be read
from here. `.github/workflows/diag-b85ad9b4.yml` replayed the publication commands on
GitHub's egress and committed every return code and log to `research/session-b85ad9b4/`
(run 40197667220): steps 01-06 and 08-09 returned 0; **`07-validate-fresh` returned 1** with

    scripts/validate.py:122 in validate_model_row
    AssertionError: Model roster has no HLTV source on this row

The row was Hotspawn fixture **1086697** `Projeto do KinGui vs Yawara` (CCT South America
2026 Series #7, 2026-10-25T19:00Z), an originated Valve-VRS line. Its roster continuity was
verified against the HLTV fixture page, whose own heading for that club is **`Tropa do
KinGui`**, so `hltv_context.lineups` stores the lineup under `Tropa do KinGui`. The offline
re-check looked the heading up with `plain_name()` — an exact folded comparison — while the
rest of the model verification (`norm()`, `ALIAS_MAP`) resolves the two spellings through
`data/identities.json`. The row is correct; the re-check could not read it. A correct row
that cannot be re-checked fails `scripts.validate`, and that is the step that died.

The fix is in `scripts/validate.py`: `lineup_source_ok` now resolves the heading with
`same_club`, which keeps the exact match as the primary rule and permits the identity
register as the only bridge, under the module's existing alias rules — both spellings
inside one entry, that entry linking an https source, and the register keeping the
fixture's two teams apart so one team's lineup can never satisfy the other. No new fuzzy
matching, no inferred value, no relaxed arithmetic: the probabilities, the roster overlap,
the pick orientation and the 8-hour freshness rules are all unchanged.

What this module pins
---------------------
1. the exact case that froze publication, reproduced from the retained capture;
2. the four ways the bridge must refuse: a different club, an unregistered spelling, a
   register entry with no primary source, and a register that collapses both fixture teams;
3. that the whole captured snapshot now validates, so the next publication can build it.
"""
import json
import unittest
from pathlib import Path

from scripts import validate
from scripts.core import IDENTITIES, plain_name

CAPTURE = Path('research/session-b85ad9b4/snapshot.json')
FIXTURE_ID = '1086697'
KIN_GUI_LINEUP = ['drg', 'ALLE', 'ckzao', 'xureba', 'lash']
YAWARA_LINEUP = ['brn$', 'j0w', 'deemO', 'tele', 'mlhzin']


def row(teams, lineups, fixture_id=FIXTURE_ID):
    """The shape the collector stores: HLTV headings, fixture labels alongside."""
    return {
        'id': fixture_id,
        'teams': list(teams),
        'hltv_context': {'teams': [item['team'] for item in lineups], 'lineups': lineups},
    }


class AliasBridge(unittest.TestCase):
    def setUp(self):
        self.row = row(['Projeto do KinGui', 'Yawara'],
                       [{'team': 'Tropa do KinGui', 'players': list(KIN_GUI_LINEUP)},
                        {'team': 'Yawara', 'players': list(YAWARA_LINEUP)}])

    def test_hltv_heading_reproduces_the_lineup(self):
        # The measured failure: plain_name() cannot see across the two spellings.
        self.assertNotEqual(plain_name('Projeto do KinGui'), plain_name('Tropa do KinGui'))
        self.assertTrue(validate.lineup_source_ok(self.row, 'Projeto do KinGui', KIN_GUI_LINEUP))

    def test_register_entry_behind_the_bridge_is_sourced(self):
        entry = [item for item in IDENTITIES
                 if {'Projeto do KinGui', 'Tropa do KinGui'} <= set(item['names'])]
        self.assertEqual(len(entry), 1, 'the identity register must hold exactly one such pair')
        self.assertTrue(entry[0]['source'].startswith('https://'))
        self.assertTrue(plain_name(entry[0]['canonical']) in
                        {plain_name(n) for n in entry[0]['names']})

    def test_the_other_teams_lineup_never_satisfies_this_team(self):
        self.assertFalse(validate.lineup_source_ok(self.row, 'Projeto do KinGui', YAWARA_LINEUP))
        self.assertFalse(validate.lineup_source_ok(self.row, 'Yawara', KIN_GUI_LINEUP))

    def test_an_unregistered_spelling_is_not_an_alias(self):
        changed = row(['Projeto do KinGui', 'Yawara'],
                      [{'team': 'Totally Different Org', 'players': list(KIN_GUI_LINEUP)},
                       {'team': 'Yawara', 'players': list(YAWARA_LINEUP)}])
        self.assertFalse(validate.lineup_source_ok(changed, 'Projeto do KinGui', KIN_GUI_LINEUP))

    def test_a_register_entry_without_a_primary_source_is_not_usable(self):
        original = validate.IDENTITIES
        stripped = [dict(item, source='') if 'Projeto do KinGui' in item['names'] else item
                    for item in original]
        validate.IDENTITIES = stripped
        try:
            self.assertFalse(validate.lineup_source_ok(self.row, 'Projeto do KinGui', KIN_GUI_LINEUP))
        finally:
            validate.IDENTITIES = original

    def test_a_register_that_collapses_the_fixture_teams_disables_the_bridge(self):
        # ex-Keyd Stars and Tropa do KinGui are one entry; a fixture that listed both
        # as separate opponents would be ambiguous, so the bridge must refuse.
        collapsed = row(['ex-Keyd Stars', 'Tropa do KinGui'],
                        [{'team': 'Tropa do KinGui', 'players': list(KIN_GUI_LINEUP)},
                         {'team': 'Yawara', 'players': list(YAWARA_LINEUP)}])
        self.assertFalse(validate.lineup_source_ok(collapsed, 'ex-Keyd Stars', KIN_GUI_LINEUP))

    def test_the_lineup_still_has_to_match_player_for_player(self):
        self.assertFalse(validate.lineup_source_ok(self.row, 'Projeto do KinGui',
                                                   KIN_GUI_LINEUP + ['Invented Player']))
        self.assertFalse(validate.lineup_source_ok(self.row, 'Projeto do KinGui', []))

    def test_a_team_page_heading_is_bridged_too(self):
        pages = {'id': FIXTURE_ID, 'teams': ['Projeto do KinGui', 'Yawara'],
                 'hltv_team_pages': {'teams': [
                     {'team': 'Tropa do KinGui', 'url': 'https://www.hltv.org/team/13151/tropa-do-kingui',
                      'lineup': list(KIN_GUI_LINEUP)}]}}
        self.assertTrue(validate.lineup_source_ok(pages, 'Projeto do KinGui', KIN_GUI_LINEUP))


@unittest.skipUnless(CAPTURE.is_file(), 'retained publication capture not present')
class CapturedSnapshot(unittest.TestCase):
    """The exact snapshot the replay captured, and the row that failed it."""

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CAPTURE.read_text())

    def test_the_failing_row_is_a_model_row_with_an_aliased_hltv_heading(self):
        match = next(m for m in self.data['matches'] if m['id'] == FIXTURE_ID)
        self.assertEqual(match['teams'], ['Projeto do KinGui', 'Yawara'])
        self.assertEqual(match['method'], 'model_vrs')
        self.assertEqual([item['team'] for item in match['hltv_context']['lineups']],
                         ['Tropa do KinGui', 'Yawara'])
        self.assertIsNotNone(match['probabilities'])
        self.assertIn(match['pick'], match['teams'])

    def test_the_captured_row_reproduces_its_roster_check(self):
        match = next(m for m in self.data['matches'] if m['id'] == FIXTURE_ID)
        quote = match['evidence'][0]
        for team, check in zip(match['teams'], quote['roster_checks']):
            self.assertGreaterEqual(check['overlap'], 4)
            self.assertTrue(validate.lineup_source_ok(match, team, check['lineup']), team)

    def test_every_row_of_the_captured_snapshot_validates(self):
        # The whole point: this is the snapshot the publisher refused to build.
        validate.validate_data(self.data)
        model = [m for m in self.data['matches'] if str(m.get('method') or '').startswith('model_')]
        self.assertTrue(model, 'the capture must contain the model rows this defect concerned')
        for match in model:
            self.assertIsNotNone(match['probabilities'], match['id'])
            self.assertIn(match['pick'], match['teams'], match['id'])


if __name__ == '__main__':
    unittest.main()
