"""Session 046b2e46: the alias that kept every pick off the public board.

Measured, not assumed
---------------------
`pages.yml` runs 40170923727 (06:56Z) and 40193317196 (12:29Z) on 2026-10-25 both
failed at step 13, so `upload-pages-artifact`, the legacy `main:/` staging step
and `deploy` were all skipped and the public board could not advance past the
01:47Z snapshot. The authoring sandbox cannot read Actions logs (the log blob
host is outside its allowlist), so the defect was captured on a normal runner by
session 58354934 (`research/harvest-58354934/`, run 40197480741, snapshot
2026-10-25T13:28:50Z). That capture reproduces exactly:

    File "scripts/validate.py", line 122, in validate_model_row
        assert lineup_source_ok(m, team, check.get('lineup') or []),
               'Model roster has no HLTV source on this row'
    AssertionError: Model roster has no HLTV source on this row

One row caused it: fixture `1086697` (*Projeto do KinGui* vs *Yawara*,
CCT South America 2026 Series #7, 2026-10-25T19:00:00Z). Hotspawn labels the
club *Projeto do KinGui*; HLTV's own match page for the same slot (match
2399904) labels it *Tropa do KinGui*, and `data/identities.json` already
registers those two names as one club with primary sources. The Valve roster
check for that side is `drg, ALLE, ckzao, xureba, lash`, and the HLTV lineup on
the same row is the identical five players — the roster evidence was complete
and correct. Only the *label comparison* in `lineup_source_ok` was wrong: it
compared literal names (`plain_name`) instead of identity-resolved names
(`core.norm`), so a registered alias could never match.

**Who shipped the repair.** Main received an equivalent alias bridge first, from
session b85ad9b4 (`e9429e6`, 13:37Z: `same_club(m, team, label)` keyed on the
same `data/identities.json` register, with an extra guard that the register must
keep the fixture's two teams apart). This session's independent repair was
withdrawn at integration rather than stacked on top of it, per the shared-board
protocol; the tests below were re-pointed at the shipped function so they pin
what main actually runs. They cover the same two halves: the alias is accepted,
and a genuinely unknown label is still refused.
"""
import json
import unittest
from pathlib import Path

from scripts import validate
from scripts.core import IDENTITIES, norm, plain_name

ROOT = Path(__file__).resolve().parents[1]

# The exact evidence carried by the captured row, quoted from
# research/harvest-58354934/snapshot.json (fixture 1086697).
HLTV_LABEL = 'Tropa do KinGui'
FIXTURE_LABEL = 'Projeto do KinGui'
VALVE_ROSTER = ['drg', 'ALLE', 'ckzao', 'xureba', 'lash']
HLTV_ROSTER = ['drg', 'ALLE', 'ckzao', 'xureba', 'lash']


def model_row(hltv_team=HLTV_LABEL, players=None):
    """A `model_vrs` row shaped exactly like the captured one."""
    return {
        'id': '1086697',
        'teams': [FIXTURE_LABEL, 'Yawara'],
        'team_ids': ['13151', '13230'],
        'competition': 'CCT South America 2026 Series #7',
        'start': '2026-10-25T19:00:00Z',
        'lock': '2026-10-25T18:54:00Z',
        'source_url': 'https://play.hotspawn.com/cs2-pickems',
        'hltv_context': {
            'source': 'https://www.hltv.org/matches/2399904/tropa-do-kingui-vs-yawara-cct-2026-south-america-series-7',
            'lineups': [
                {'team': hltv_team, 'players': list(players or HLTV_ROSTER)},
                {'team': 'Yawara', 'players': ['brn$', 'j0w', 'deemO', 'tele', 'mlhzin']},
            ],
        },
    }


class RegisteredAliasIsOneClub(unittest.TestCase):
    """`same_club` may only merge labels that carry a source record."""

    def row(self):
        return model_row()

    def test_the_captured_alias_resolves_to_one_club(self):
        self.assertNotEqual(plain_name(FIXTURE_LABEL), plain_name(HLTV_LABEL),
                            'these labels differ literally; that is the defect')
        self.assertEqual(norm(FIXTURE_LABEL), norm(HLTV_LABEL),
                         'the identity register must resolve them to one club')
        self.assertTrue(validate.same_club(self.row(), FIXTURE_LABEL, HLTV_LABEL))
        self.assertTrue(validate.same_club(self.row(), HLTV_LABEL, FIXTURE_LABEL))

    def test_case_and_punctuation_are_normalisation_not_aliasing(self):
        row = {'teams': ['benched gods', 'TitanFlow']}
        self.assertTrue(validate.same_club(row, 'benched gods', 'Benched  Gods'))
        self.assertTrue(validate.same_club({'teams': ['Los Niños', 'TitanFlow']}, 'Los Niños', 'LOS NINOS'))

    def test_an_unregistered_label_is_still_a_different_club(self):
        # No record in data/identities.json joins these; guessing one is what
        # this guard exists to prevent.
        self.assertFalse(validate.same_club(self.row(), 'Tropa do KinGui', 'Yawara'))
        self.assertFalse(validate.same_club(self.row(), 'Projeto do KinGui', 'FURIA'))
        self.assertFalse(validate.same_club(self.row(), '', FIXTURE_LABEL))
        # lineup_source_ok() always passes `item.get('team') or ''`, so a missing
        # heading arrives here as empty text rather than None.
        self.assertFalse(validate.same_club(self.row(), FIXTURE_LABEL, ''))

    def test_a_register_that_would_collapse_the_fixture_is_refused(self):
        # The shipped guard: an exact name match is always accepted (it is
        # unambiguous), but the *alias* bridge is refused when the fixture's own
        # two labels already resolve to one club, so a lineup can never be
        # borrowed across them.
        row = {'teams': ['Projeto do KinGui', 'Tropa do KinGui']}
        self.assertTrue(validate.same_club(row, 'Projeto do KinGui', 'Projeto do KinGui'))
        self.assertFalse(validate.same_club(row, 'Projeto do KinGui', 'Tropa do KinGui'),
                         'a collapsed fixture must not be bridged by the register')

    def test_the_alias_record_names_its_primary_sources(self):
        record = next((item for item in IDENTITIES
                       if {plain_name(n) for n in item['names']} >= {plain_name(FIXTURE_LABEL),
                                                                   plain_name(HLTV_LABEL)}), None)
        self.assertIsNotNone(record, 'the alias this validator relies on must be registered')
        self.assertTrue(str(record.get('source', '')).startswith('https://www.hltv.org/matches/'),
                        'an alias must be anchored to an HLTV match page')
        self.assertTrue(str(record.get('additional_source', '')).startswith('https://'),
                        'an alias must carry a second, independent corroboration')
        self.assertTrue(record.get('basis'), 'an alias must record why it was accepted')


class RosterProvenanceIsUnchanged(unittest.TestCase):
    """The fix must accept the alias and refuse everything else."""

    def test_the_captured_row_now_passes(self):
        row = model_row()
        self.assertTrue(validate.lineup_source_ok(row, FIXTURE_LABEL, VALVE_ROSTER),
                        'the HLTV lineup for the registered alias is a valid source')

    def test_a_different_lineup_is_still_refused(self):
        row = model_row()
        self.assertFalse(validate.lineup_source_ok(row, FIXTURE_LABEL, VALVE_ROSTER + ['Stand-in']))

    def test_a_lineup_from_another_club_is_still_refused(self):
        row = model_row()
        row['hltv_context']['lineups'] = [
            {'team': 'Yawara', 'players': list(HLTV_ROSTER)},
        ]
        self.assertFalse(validate.lineup_source_ok(row, FIXTURE_LABEL, VALVE_ROSTER),
                         'an unrelated club\'s roster cannot vouch for this one')

    def test_an_empty_lineup_is_never_sourced(self):
        row = model_row()
        self.assertFalse(validate.lineup_source_ok(row, FIXTURE_LABEL, []))

    def test_team_pages_and_receipts_use_the_same_identity_rule(self):
        row = model_row()
        row.pop('hltv_context')
        row['hltv_team_pages'] = {
            'observed_at': '2026-10-25T13:28:00Z',
            'teams': [{'team': HLTV_LABEL, 'lineup': list(HLTV_ROSTER),
                       'url': 'https://www.hltv.org/team/13151/tropa-do-kingui'}],
        }
        self.assertTrue(validate.lineup_source_ok(row, FIXTURE_LABEL, VALVE_ROSTER),
                        'the club team page is keyed by HLTV\'s label for the same club')
        row['hltv_team_pages']['teams'][0]['url'] = 'https://example.com/not-hltv'
        self.assertFalse(validate.lineup_source_ok(row, FIXTURE_LABEL, VALVE_ROSTER),
                         'a non-HLTV page never vouches for a roster')


class ThePublishedSnapshotReplaysClean(unittest.TestCase):
    """The captured snapshot that failed step 13 must pass the validator."""

    SNAPSHOT = ROOT / 'research' / 'session-046b2e46' / 'captured-snapshot.json'

    def setUp(self):
        if not self.SNAPSHOT.exists():
            self.skipTest('captured snapshot receipt is not present')

    def test_every_row_validates_and_every_open_match_is_picked(self):
        data = json.loads(self.SNAPSHOT.read_text())
        report = validate.validate_data(data)
        self.assertEqual(report['rows_verified_against_primary_snapshot'], len(data['matches']))
        self.assertEqual(report['probability_calculations_reproduced'],
                         sum(1 for m in data['matches'] if m['probabilities'] is not None))

    def test_the_alias_row_is_the_one_that_carried_the_defect(self):
        data = json.loads(self.SNAPSHOT.read_text())
        row = next(m for m in data['matches'] if m['id'] == '1086697')
        self.assertEqual(row['method'], 'model_vrs')
        self.assertEqual(row['teams'], [FIXTURE_LABEL, 'Yawara'])
        labels = [x.get('team') for x in row['hltv_context']['lineups']]
        self.assertIn(HLTV_LABEL, labels, 'the row stores HLTV\'s own label, unrewritten')
        self.assertTrue(validate.lineup_source_ok(row, FIXTURE_LABEL, VALVE_ROSTER))


if __name__ == '__main__':
    unittest.main()


class IndependentLedgerReDerivesEveryOpenPick(unittest.TestCase):
    """`scripts.session_046b2e46` must reproduce the board, and must bite.

    The ledger re-derives each published percentage from the raw evidence with
    its own arithmetic (Polymarket midpoint, de-vigged decimal odds, Valve's
    published Glicko formula and fit slope). A verifier that cannot fail is not
    a verifier, so every check below is paired with a tampered copy that must
    fail.
    """

    SNAPSHOT = ROOT / 'research' / 'session-046b2e46' / 'captured-snapshot.json'

    @classmethod
    def setUpClass(cls):
        if not cls.SNAPSHOT.exists():
            raise unittest.SkipTest('captured snapshot receipt is not present')
        cls.data = json.loads(cls.SNAPSHOT.read_text())
        cls.by_id = {m['id']: m for m in cls.data['matches']}

    def row(self, fixture_id):
        import copy
        return copy.deepcopy(self.by_id[fixture_id])

    def test_polymarket_midpoint_is_the_published_pair(self):
        from scripts import session_046b2e46 as ledger
        row = self.row('1085542')
        problems, probs, note, url, api = ledger.check_row(row, ledger.parse_time(
            self.data['fixtures_observed_at']))
        self.assertEqual(problems, [])
        self.assertEqual([round(p, 6) for p in probs], [0.595, 0.405])
        self.assertIn('midpoint', note)
        self.assertTrue(url.startswith('https://polymarket.com/event/'))

    def test_market_published_in_the_opposite_order_is_oriented_not_reversed(self):
        from scripts import session_046b2e46 as ledger
        row = self.row('1082697')          # Polymarket: paiN first; Hotspawn: BESTIA first
        self.assertEqual(row['teams'], ['BESTIA', 'paiN'])
        self.assertEqual(row['evidence'][0]['source_teams'], ['paiN', 'BESTIA'])
        problems, probs, _, _, _ = ledger.check_row(row, ledger.parse_time(
            self.data['fixtures_observed_at']))
        self.assertEqual(problems, [])
        self.assertEqual([round(p, 6) for p in probs], [0.425, 0.575])
        self.assertEqual(row['pick'], 'paiN')

    def test_exchange_abbreviation_identifies_the_club(self):
        # Fixture 1082996 is 'UNiTY' on Hotspawn and 'UNiTY esports' on the
        # exchange, whose own metadata carries the abbreviation 'unity'.
        from scripts import session_046b2e46 as ledger
        self.assertEqual(ledger.orient(['Acend', 'UNiTY'], ['Acend', 'UNiTY esports'],
                                       [{'name': 'UNiTY esports', 'abbreviation': 'unity'}]),
                         {'Acend': 0, 'UNiTY': 1})
        # Session b964dffd (2026-10-26): 'UNiTY esports' is now ALSO joined to
        # 'UNiTY' by a sourced identity record in data/identities.json (rule 1
        # in orient's docstring; Polymarket market 6186061 + HLTV 2399119), so
        # that exact pair legitimately orients without abbreviation metadata.
        # The refusal direction is therefore pinned on a label no identity
        # record covers.
        with self.assertRaises(ValueError):
            ledger.orient(['Acend', 'UNiTY'], ['Acend', 'UNiTY Gaming'], [])

    def test_book_listing_is_de_vigged(self):
        from scripts import session_046b2e46 as ledger
        row = self.row('1082859')
        problems, probs, note, _, _ = ledger.check_row(row, ledger.parse_time(
            self.data['fixtures_observed_at']))
        self.assertEqual(problems, [])
        self.assertEqual([round(p, 4) for p in probs], [0.5789, 0.4211])
        self.assertIn('de-vigged', note)

    def test_valve_model_is_recomputed_from_its_published_formula(self):
        from scripts import session_046b2e46 as ledger
        row = self.row('1086697')
        problems, probs, note, url, _ = ledger.check_row(row, ledger.parse_time(
            self.data['fixtures_observed_at']))
        self.assertEqual(problems, [])
        self.assertAlmostEqual(probs[0], 0.5100602445, places=9)
        self.assertIn('Glicko', note)
        self.assertTrue(url.startswith('https://github.com/ValveSoftware/'))

    def test_the_whole_captured_board_reproduces(self):
        from scripts import session_046b2e46 as ledger
        receipt = ledger.build_receipt(self.data)
        self.assertEqual(receipt['failures'], [])
        self.assertEqual(len(receipt['open']), 17)
        self.assertEqual(receipt['unpicked'], [])
        self.assertEqual(receipt['unpriced'], [])

    def test_a_tampered_probability_fails(self):
        from scripts import session_046b2e46 as ledger
        row = self.row('1085542')
        row['probabilities'] = [0.62, 0.38]
        problems, _, _, _, _ = ledger.check_row(row, ledger.parse_time(
            self.data['fixtures_observed_at']))
        self.assertTrue(any('re-derives to' in p for p in problems), problems)

    def test_a_tampered_pick_fails(self):
        from scripts import session_046b2e46 as ledger
        row = self.row('1085542')
        row['pick'] = 'Spirit Academy'
        problems, _, _, _, _ = ledger.check_row(row, ledger.parse_time(
            self.data['fixtures_observed_at']))
        self.assertTrue(any('does not follow the higher probability' in p for p in problems), problems)

    def test_tampered_fair_odds_fail(self):
        from scripts import session_046b2e46 as ledger
        row = self.row('1085542')
        row['fair_odds'] = [1.5, 2.0]
        problems, _, _, _, _ = ledger.check_row(row, ledger.parse_time(
            self.data['fixtures_observed_at']))
        self.assertTrue(any('fair odds' in p for p in problems), problems)

    def test_a_reversed_quote_without_evidence_fails(self):
        from scripts import session_046b2e46 as ledger
        row = self.row('1085542')
        row['evidence'][0]['source_teams'] = ['Someone Else', 'Spirit Academy']
        problems, _, _, _, _ = ledger.check_row(row, ledger.parse_time(
            self.data['fixtures_observed_at']))
        self.assertTrue(any('cannot map' in p for p in problems), problems)

    def test_a_missing_market_link_fails(self):
        from scripts import session_046b2e46 as ledger
        row = self.row('1085542')
        row['evidence'][0]['url'] = ''
        problems, _, _, _, _ = ledger.check_row(row, ledger.parse_time(
            self.data['fixtures_observed_at']))
        self.assertTrue(any('no public URL' in p for p in problems), problems)

    def test_an_unlabelled_model_row_fails(self):
        from scripts import session_046b2e46 as ledger
        row = self.row('1086697')
        row['flags'] = [f for f in row['flags'] if 'not a market price' not in f]
        problems, _, _, _, _ = ledger.check_row(row, ledger.parse_time(
            self.data['fixtures_observed_at']))
        self.assertTrue(any('not labelled non-market' in p for p in problems), problems)
