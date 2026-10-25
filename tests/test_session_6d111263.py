"""Session 6d111263 — the publisher freeze of 2026-10-25 and its fix.

Fixture 1086697 (Projeto do KinGui vs Yawara, CCT 2026 South America Series 7)
carries an HLTV context whose lineup for the first team is labelled "Tropa do
KinGui" — HLTV's own club name, registered as a source-backed alias of the
Hotspawn fixture label in data/identities.json (the same entry the VRS label
check at ``norm(team) == norm(label)`` already accepts). ``lineup_source_ok``
compared labels with ``plain_name`` equality only, so the model row's roster
check failed and ``scripts.validate`` crashed the publisher's *Build and
independently verify* step on every scheduled run from 2026-10-24T23:40Z until
the fix, while the live board aged past its eight-hour evidence window and
withheld every pick.

Rule under test: a label on the HLTV side matches the fixture team when it is
the exact normalized label, or when both labels sit inside one entry of
data/identities.json that itself carries a primary source link. Nothing else —
unregistered labels and source-less identities must keep failing.
"""
import json
import unittest
from pathlib import Path
from unittest import mock

from scripts import validate
from scripts import core

ROOT = Path(__file__).resolve().parents[1]

PLAYERS_KIN = ['drg', 'ALLE', 'ckzao', 'xureba', 'lash']
PLAYERS_YAW = ['brn$', 'j0w', 'deemO', 'tele', 'mlhzin']

SOURCED_IDENTITY = {
    'canonical': 'Tropa do KinGui',
    'names': ['Tropa do KinGui', 'Projeto do KinGui', 'ex-Keyd Stars'],
    'source': 'https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-martians-cct-2026-south-america-series-7',
}
UNSOURCED_IDENTITY = {'canonical': 'Tropa do KinGui',
                      'names': ['Tropa do KinGui', 'Projeto do KinGui']}


def row():
    return {
        'id': '1086697',
        'teams': ['Projeto do KinGui', 'Yawara'],
        'hltv_context': {
            'source': 'https://www.hltv.org/matches/2399918/tropa-do-kingui-vs-yawara-cct-2026-south-america-series-7',
            'lineups': [
                {'team': 'Tropa do KinGui', 'players': PLAYERS_KIN},
                {'team': 'Yawara', 'players': PLAYERS_YAW},
            ],
        },
    }


class SourcedLabelMatch(unittest.TestCase):
    def test_exact_normalized_label_matches(self):
        self.assertTrue(validate.sourced_label_match('Yawara', 'Yawara'))
        self.assertTrue(validate.sourced_label_match('LOS NINOS', 'Los Niños'))

    def test_registered_pair_with_a_source_matches_in_both_directions(self):
        with mock.patch.object(validate, 'IDENTITIES', [SOURCED_IDENTITY]):
            self.assertTrue(validate.sourced_label_match('Tropa do KinGui', 'Projeto do KinGui'))
            self.assertTrue(validate.sourced_label_match('Projeto do KinGui', 'Tropa do KinGui'))

    def test_registered_pair_without_a_source_is_rejected(self):
        with mock.patch.object(validate, 'IDENTITIES', [UNSOURCED_IDENTITY]):
            self.assertFalse(validate.sourced_label_match('Tropa do KinGui', 'Projeto do KinGui'))

    def test_unregistered_label_is_rejected(self):
        with mock.patch.object(validate, 'IDENTITIES', [SOURCED_IDENTITY]):
            self.assertFalse(validate.sourced_label_match('Tropa do KinGui', 'Yawara'))
        with mock.patch.object(validate, 'IDENTITIES', []):
            self.assertFalse(validate.sourced_label_match('Tropa do KinGui', 'Projeto do KinGui'))


class LineupSourceOkAlias(unittest.TestCase):
    def test_context_lineup_under_the_hltv_label_is_accepted(self):
        with mock.patch.object(validate, 'IDENTITIES', [SOURCED_IDENTITY]):
            self.assertTrue(validate.lineup_source_ok(row(), 'Projeto do KinGui', PLAYERS_KIN))

    def test_context_lineup_needs_the_exact_players(self):
        with mock.patch.object(validate, 'IDENTITIES', [SOURCED_IDENTITY]):
            self.assertFalse(validate.lineup_source_ok(row(), 'Projeto do KinGui', PLAYERS_KIN + ['Invented']))

    def test_context_lineup_under_an_unknown_label_is_rejected(self):
        data = row()
        data['hltv_context']['lineups'][0]['team'] = 'Unregistered Club Name'
        with mock.patch.object(validate, 'IDENTITIES', [SOURCED_IDENTITY]):
            self.assertFalse(validate.lineup_source_ok(data, 'Projeto do KinGui', PLAYERS_KIN))

    def test_lineup_receipt_branch_accepts_the_registered_alias(self):
        receipt = {'fixture_id': '1086697', 'teams': ['Projeto do KinGui', 'Yawara'],
                   'lineups': [{'team': 'Tropa do KinGui', 'players': PLAYERS_KIN,
                                'source': 'https://www.hltv.org/matches/2399918/tropa-do-kingui-vs-yawara-cct-2026-south-america-series-7'}]}
        data = {'id': '1086697', 'teams': ['Projeto do KinGui', 'Yawara']}
        with mock.patch.object(validate, 'IDENTITIES', [SOURCED_IDENTITY]), \
                mock.patch.object(validate.hltv, 'lineup_receipts', lambda: [receipt]):
            self.assertTrue(validate.lineup_source_ok(data, 'Projeto do KinGui', PLAYERS_KIN))
        # The identity is what carries the receipt branch, not the fixture id.
        with mock.patch.object(validate, 'IDENTITIES', []), \
                mock.patch.object(validate.hltv, 'lineup_receipts', lambda: [receipt]):
            self.assertFalse(validate.lineup_source_ok(data, 'Projeto do KinGui', PLAYERS_KIN))

    def test_team_page_branch_accepts_the_registered_alias(self):
        data = {'id': '1086697', 'teams': ['Projeto do KinGui', 'Yawara'],
                'hltv_team_pages': {'observed_at': '2026-10-25T13:33:00Z', 'teams': [
                    {'team': 'Tropa do KinGui', 'lineup': PLAYERS_KIN,
                     'url': 'https://www.hltv.org/team/13151/tropa-do-kingui'}]}}
        with mock.patch.object(validate, 'IDENTITIES', [SOURCED_IDENTITY]):
            self.assertTrue(validate.lineup_source_ok(data, 'Projeto do KinGui', PLAYERS_KIN))
        with mock.patch.object(validate, 'IDENTITIES', []):
            self.assertFalse(validate.lineup_source_ok(data, 'Projeto do KinGui', PLAYERS_KIN))


class IncidentReplay(unittest.TestCase):
    """The exact snapshot that failed the publisher must now validate, and the
    identity register must remain the only reason it does."""

    SNAPSHOT = ROOT / 'research' / 'harvest-6d111263' / 'snapshot.json'

    @classmethod
    def setUpClass(cls):
        if not cls.SNAPSHOT.exists():
            raise AssertionError(
                f'{cls.SNAPSHOT} is missing; it is the committed receipt of run '
                '40197851926 and the incident replay depends on it')
        cls.data = json.loads(cls.SNAPSHOT.read_text())

    def fixture(self):
        matches = [m for m in self.data['matches'] if m['id'] == '1086697']
        self.assertEqual(len(matches), 1, 'fixture 1086697 must be in the receipt snapshot')
        return matches[0]

    def test_model_row_validates_against_the_registered_alias(self):
        m = self.fixture()
        now = core.dt(self.data['generated_at'])
        self.assertEqual(m['method'], 'model_vrs')
        validate.validate_model_row(m, m['evidence'][0], now)

    def test_the_same_row_fails_without_the_identity_register(self):
        m = self.fixture()
        now = core.dt(self.data['generated_at'])
        with mock.patch.object(validate, 'IDENTITIES', []):
            with self.assertRaises(AssertionError):
                validate.validate_model_row(m, m['evidence'][0], now)

    def test_full_data_gate_on_the_receipt_snapshot(self):
        # scripts.validate's data half: every row, calculation and primary
        # fact of the refreshed candidate that the publisher rejected.
        report = validate.validate_data(self.data)
        self.assertEqual(report['rows_verified_against_primary_snapshot'], len(self.data['matches']))
        self.assertGreater(report['probability_calculations_reproduced'], 0)


if __name__ == '__main__':
    unittest.main()
