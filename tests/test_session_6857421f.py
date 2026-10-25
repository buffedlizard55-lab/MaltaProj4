"""Session 6857421f: the 2026-10-25 publisher failure, and the phone defect
underneath it.

What this suite proves, and why
-------------------------------
1. **The publisher was red for eleven hours and the board withheld every pick.**
   The public build at 2026-10-25T13:26Z was built from the
   `2026-10-25T01:47:42Z` snapshot. The board's own `stale_after_hours` is 8, so
   at that clock the site was withholding every pick. Both scheduled publisher
   runs on `6ade440` -- 40170923727 (06:56Z) and 40193317196 (12:29Z) -- failed
   at the same step, *Build and independently verify every row, calculation and
   internal link*, which runs **after** the unit gate, the live refresh and the
   quarantine had all passed. The failing sub-command was named by a runner
   replay that committed its own receipt (`research/diag-6857421f/`):
   `published_validate_rc=1`, with

       scripts/validate.py:122  AssertionError: Model roster has no HLTV source on this row

   on the 2026-10-25T13:34:30Z capture. The row was fixture **1086697**
   (Hotspawn *Projeto do KinGui* vs *Yawara*): the ladder fell through
   Polymarket, HLTV, Pinnacle, Thunderpick and GG.BET to our own Valve-standings
   model line, whose roster check comes from HLTV's fixture page
   `https://www.hltv.org/matches/2399918/tropa-do-kingui-vs-yawara-cct-2026-south-america-series-7`
   -- and HLTV prints *Tropa do KinGui*, the registered alias, for the same five
   players. `lineup_source_ok` compared labels with `plain_name`, so a
   correctly sourced roster looked unsourced. The test below is the same
   comparison in both directions: the registered alias must resolve, and an
   **unregistered** label must still be refused.

2. **The phone board failed its own 320x568 contract.** The same replay recorded
   `browser_rc=1` from `tests/browser_019a253a.cjs:105` ("the first
   probabilities must clear the tab bar"). Measured on that build, the first
   card's percentages sat at y=493-519 against a tab bar at y=507: twelve
   pixels behind the bar. Two sessions repaired this; `main` carries session
   58354934's implementation (on short phones the numbers move directly under
   the pick and the start/lock line follows them), so this session adopted that
   code and dropped its own duplicate stylesheet edit. The tests below pin the
   contract instead: both published stylesheet copies byte-identical and
   balanced, no phone rule hiding a percentage, a fair line, a model comparison,
   a flag or a source link, and the four suites that measure the geometry
   registered as browser gates.

3. **Neither repair may hide evidence.** The tests assert that the phone block
   hides nothing but the duplicated labels, that both published stylesheet
   copies are byte-identical, and that every open row still carries its own
   official source link.
"""
import json
import re
import unittest
from pathlib import Path

from scripts import validate
from scripts.core import norm

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())
IDENTITIES = json.loads((ROOT / 'data' / 'identities.json').read_text())['aliases']

KIN_GUI = ['drg', 'ALLE', 'ckzao', 'xureba', 'lash']
YAWARA = ['brn$', 'j0w', 'deemO', 'tele', 'mlhzin']


def row(lineups, teams=('Projeto do KinGui', 'Yawara'), team_pages=None):
    """A minimal model row carrying only what ``lineup_source_ok`` reads."""
    fixture = {'id': '1086697', 'teams': list(teams),
               'hltv_context': {'lineups': lineups}}
    if team_pages:
        fixture['hltv_team_pages'] = {'teams': team_pages}
    return fixture


class RegisteredAliasLineupTest(unittest.TestCase):
    """The measured failure: a sourced roster rejected for printing the alias."""

    hltv_lineups = [{'team': 'Tropa do KinGui', 'players': KIN_GUI},
                    {'team': 'Yawara', 'players': YAWARA}]

    def test_hltv_alias_label_resolves_to_the_fixture_team(self):
        # This is the exact 2026-10-25T13:34:30Z shape: Hotspawn prints
        # "Projeto do KinGui", HLTV's fixture page prints "Tropa do KinGui".
        self.assertTrue(validate.lineup_source_ok(
            row(self.hltv_lineups), 'Projeto do KinGui', KIN_GUI))

    def test_exact_label_still_resolves(self):
        self.assertTrue(validate.lineup_source_ok(
            self.hltv_lineups and row(self.hltv_lineups), 'Yawara', YAWARA))

    def test_alias_used_by_the_fix_is_registered_with_a_primary_source(self):
        # The comparison may only accept labels the reviewed register carries,
        # and every entry must name an https source and a written basis.
        group = [a for a in IDENTITIES
                 if 'Projeto do KinGui' in a['names'] and 'Tropa do KinGui' in a['names']]
        self.assertEqual(len(group), 1, 'the alias pair must be registered exactly once')
        self.assertEqual(norm('Projeto do KinGui'), norm('Tropa do KinGui'))
        self.assertTrue(str(group[0]['source']).startswith('https://'))
        self.assertTrue(group[0]['basis'].strip())

    def test_unregistered_label_is_still_refused(self):
        # An unregistered rename must not become a sourced roster: the whole
        # point of the alias register is that a human recorded the basis.
        self.assertFalse(validate.lineup_source_ok(
            row([{'team': 'Some Other Club', 'players': KIN_GUI},
                 {'team': 'Yawara', 'players': YAWARA}]),
            'Projeto do KinGui', KIN_GUI))

    def test_alias_does_not_license_a_different_roster(self):
        self.assertFalse(validate.lineup_source_ok(
            row([{'team': 'Tropa do KinGui', 'players': KIN_GUI[:4] + ['someone-else']},
                 {'team': 'Yawara', 'players': YAWARA}]),
            'Projeto do KinGui', KIN_GUI))

    def test_missing_lineup_stays_unsourced(self):
        self.assertFalse(validate.lineup_source_ok(
            row([{'team': 'Yawara', 'players': YAWARA}]), 'Projeto do KinGui', KIN_GUI))
        self.assertFalse(validate.lineup_source_ok(row([]), 'Projeto do KinGui', []))

    def test_team_page_path_also_accepts_the_registered_alias(self):
        fixture = row([], team_pages=[{'team': 'Tropa do KinGui', 'lineup': KIN_GUI,
                                       'url': 'https://www.hltv.org/team/11606/tropa-do-kingui'}])
        self.assertTrue(validate.lineup_source_ok(fixture, 'Projeto do KinGui', KIN_GUI))

    def test_team_page_needs_an_hltv_url(self):
        fixture = row([], team_pages=[{'team': 'Tropa do KinGui', 'lineup': KIN_GUI,
                                       'url': 'https://example.test/team/1'}])
        self.assertFalse(validate.lineup_source_ok(fixture, 'Projeto do KinGui', KIN_GUI))


class CapturedSnapshotStillValidatesTest(unittest.TestCase):
    """The repaired validator must pass the capture that stopped the publisher."""

    def test_the_20_25_13_34_capture_validates(self):
        capture = ROOT / 'research' / 'diag-6857421f' / 'snapshot-quarantined.json'
        self.assertTrue(capture.exists(), 'the runner receipt must stay in the repository')
        import contextlib
        import io
        data = json.loads(capture.read_text())
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            report = validate.validate_data(data)
        self.assertEqual(report['rows_verified_against_primary_snapshot'], len(data['matches']))
        self.assertGreater(report['probability_calculations_reproduced'], 0)

    def test_every_open_row_on_the_committed_board_has_an_official_source(self):
        for match in SNAPSHOT['matches']:
            if match['state'] != 'open':
                continue
            self.assertTrue(str(match['source_url']).startswith('https://'), match['id'])
            self.assertTrue(match['source_url'].startswith(
                ('https://www.hotspawn.com/', 'https://play.hotspawn.com/')), match['id'])


class PhoneBoardContractTest(unittest.TestCase):
    """The phone board is measured by the browser suites; nothing here hides a number.

    Two sessions repaired the same 320x568 defect on 2026-10-25. `main` carries
    session 58354934's implementation (on short phones the percentages move
    directly under the pick and the start/lock line follows them, plus a
    tighter card), so this session adopted that code and dropped its own
    duplicate stylesheet edit. What is pinned here is the contract the repair
    must keep, not one implementation of it: the two published stylesheet copies
    stay byte-identical and balanced, no phone rule hides a percentage, a fair
    line, a model comparison, a flag or a source link, and the two browser
    suites that measure the geometry are registered in `npm run test:browser`.
    """

    def stylesheets(self):
        return [(ROOT / 'site/assets/style.css'), (ROOT / 'assets/style.css')]

    def test_published_copies_are_byte_identical(self):
        first, second = self.stylesheets()
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_braces_balance(self):
        for path in self.stylesheets():
            text = path.read_text()
            self.assertEqual(text.count('{') - text.count('}'), 0, path)

    def test_no_phone_rule_hides_evidence(self):
        text = (ROOT / 'site/assets/style.css').read_text()
        blocks = re.findall(r'@media\(max-width:650px\)[^{]*\{(.*?)\n\}', text, re.S)
        self.assertTrue(blocks, 'the phone stylesheet must exist')
        forbidden = ('.prob-pair', '.prob-label', '.model-line', '.source-links',
                     '.badge', '.pick', '.time-cell', '.evidence', '.flags')
        for block in blocks:
            for selector in forbidden:
                self.assertNotRegex(
                    block, re.escape(selector) + r'[^{}]*\{[^{}]*display:\s*none',
                    f'{selector} may not be hidden on a phone')

    def test_the_phone_measurements_are_registered_browser_gates(self):
        package = json.loads((ROOT / 'package.json').read_text())
        command = package['scripts']['test:browser']
        for suite in ('tests/browser_019a253a.cjs', 'tests/browser_9b97d585.cjs',
                      'tests/browser_ce45f672.cjs', 'tests/browser_aeafcbe6.cjs'):
            self.assertIn(suite, command)
            self.assertTrue((ROOT / suite).exists())

    def test_the_measured_board_still_renders_both_percentages(self):
        capture = json.loads((ROOT / 'research' / 'diag-6857421f' /
                              'snapshot-quarantined.json').read_text())
        from scripts import build
        html = build.table([m for m in capture['matches'] if m['state'] == 'open'], True)
        self.assertGreaterEqual(html.count('percent"'), 2)
        self.assertIn('aria-label="', html)


if __name__ == '__main__':
    unittest.main()
