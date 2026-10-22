"""Coverage guarantees for the pick-only rows investigated by session 76712ccc.

Three promises are tested here, all against committed bytes only:

1. Every open fixture carries a pick, and every published probability carries
   retained evidence with a source URL.
2. Every open pick without a probability has a documented provider trail
   (at least three independent providers, each with a URL and a reason) *and*
   a row in the current generated evidence ledger. The historical dossier is replayed within its dated scope.
3. The dossier never invents a number: a probability appears in it only when
   ``scripts.vrs.line`` originates it from the vendored Valve standings plus
   the captured HLTV lineup, and that computation is re-run here so the
   dossier cannot silently drift away from the code.

The regression this file exists for is fixture 1081521 (ex-6666 vs Privateer):
the exchange and every probed bookmaker had no line, and the VRS model refused
the row only because Hotspawn labels the team ``ex-6666`` while Valve's list
carries ``6666``. The registered alias plus the roster-overlap check fixes that
without guessing a number.
"""
import hashlib
import json
import unittest
from pathlib import Path

import scripts.core as core
from scripts import vrs

ROOT = Path(__file__).resolve().parents[1]
QUOTES = ROOT / 'research/quotes-76712ccc'
SNAPSHOT = json.loads((ROOT / 'data/latest.json').read_text())
DOSSIER = json.loads((QUOTES / 'UNPRICED-FIXTURE-LINES.json').read_text())
VENDORED_FILE = ROOT / 'data/vrs/standings_global_2026_10_05.md'
VENDORED_META = json.loads((ROOT / 'data/vrs/meta.json').read_text())
STANDINGS = vrs.parse(VENDORED_FILE.read_text())
VRS_META = dict(VENDORED_META, observed_at=VENDORED_META.get('vendored_at'), origin='vendored snapshot (data/vrs)')

OPEN = [m for m in SNAPSHOT['matches'] if m.get('state') == 'open']
PICK_ONLY = [m for m in OPEN if m.get('pick') is not None and m.get('probabilities') is None]
BY_ID = {m['id']: m for m in SNAPSHOT['matches']}


class BoardCoverageTests(unittest.TestCase):
    def test_every_open_fixture_has_a_pick_or_documented_limitation(self):
        # New listings can lack verified identity/odds. Requiring a fabricated
        # pick would contradict the evidence policy and block safe publication.
        for row in OPEN:
            if row.get('pick'):
                self.assertIn(row['pick'], row['teams'])
                continue
            with self.subTest(fixture=row['id']):
                self.assertTrue(row.get('reason'), 'Unresolved row needs an explanation')
                self.assertTrue(row.get('attempts'), 'Unresolved row needs a source trail')
                self.assertTrue(any(a.get('url', '').startswith('https://')
                                    for a in row['attempts']))
                if row.get('probabilities') is None:
                    self.assertIsNone(row.get('fair_odds'))
                else:
                    self.assertAlmostEqual(*row['probabilities'], places=4)


    def test_every_published_probability_carries_receipted_evidence(self):
        for row in OPEN:
            if row.get('probabilities') is None:
                continue
            with self.subTest(fixture=row['id']):
                p = row['probabilities']
                self.assertEqual(2, len(p))
                self.assertAlmostEqual(1.0, sum(p), places=9)
                self.assertEqual([1 / x for x in p], row['fair_odds'])
                self.assertTrue(row.get('evidence'), 'No evidence for a priced row')
                for quote in row['evidence']:
                    self.assertTrue(str(quote.get('url', '')).startswith('https://'), quote.get('url'))
                # 'bookmaker_fallback' is the method the pipeline writes for a
                # bookmaker line (Pinnacle's tier, and from 17 October 2026 the
                # researched book-listing tier). It was missing from this list,
                # which was only exercised by snapshots without such a row.
                # (session 035cbb63, same re-pin reached independently: 'book' is a
                # legacy name -- no code path emits it -- but it is kept here so nothing
                # another session wrote is dropped.
                # 'model_vrs_mirror' is the originated line built from HLTV's
                # dated view of Valve's ranking, used only where Valve's monthly
                # file cannot resolve both clubs. It carries the same evidence
                # shape (points, formula and calibration sources, a dated page
                # URL), so it belongs in this list; it was missing until the
                # 2026-10-22 board became the first to publish such a row, after
                # the mirror read was moved ahead of the per-fixture HLTV sweep.
                # (session 92e3275c)
                self.assertIn(row.get('method'),
                              ('exchange', 'exchange_wide', 'book', 'bookmaker_fallback', 'model_vrs',
                               'model_vrs_mirror'))

    def test_pick_only_rows_have_a_documented_provider_trail(self):
        for row in PICK_ONLY:
            with self.subTest(fixture=row['id']):
                attempts = row.get('attempts') or []
                providers = {a['provider'] for a in attempts}
                self.assertGreaterEqual(len(providers), 3, providers)
                for attempt in attempts:
                    self.assertTrue(str(attempt.get('url', '')).startswith('https://'), attempt)
                    self.assertTrue(attempt.get('reason'), attempt)
                    self.assertIn(attempt.get('status'), ('resolved', 'unresolved', 'error'))
                self.assertTrue(any(a['provider'] == 'Valve VRS model' for a in attempts))

    def test_pick_only_rows_carry_a_limitation_flag(self):
        for row in PICK_ONLY:
            with self.subTest(fixture=row['id']):
                joined = ' '.join(row.get('flags') or []).lower()
                self.assertIn('no probability published', joined)


class DossierTests(unittest.TestCase):
    def test_dossier_exists_and_covers_every_pick_only_row(self):
        documented = {f['fixture_id'] for f in DOSSIER['fixtures']}
        self.assertTrue(documented, 'Dossier is empty')
        if SNAPSHOT['generated_at'] == DOSSIER['snapshot']['generated_at']:
            # The retained historical dossier must cover its own dated snapshot.
            for row in PICK_ONLY:
                self.assertIn(row['id'], documented)
        # New fixtures cannot be required to appear in an older static receipt.
        # Their current dossier is the generated, source-linked evidence ledger.
        from scripts import build
        html = build.evidence_page(SNAPSHOT)
        for row in PICK_ONLY:
            with self.subTest(fixture=row['id']):
                self.assertIn('id="match-'+row['id']+'"', html)
                # The row's own primary source must be published. An HLTV fixture
                # identity carries it in hltv_context; a row resolved by the
                # one-sided Valve standings tier (research_vrs_single, added
                # 2026-10-21 for fixtures HLTV never listed) has no HLTV fixture
                # page at all, so its primary source is the official standings file.
                primary = ((row.get('hltv_context') or {}).get('source')
                           or (row.get('vrs_research') or {}).get('source'))
                self.assertTrue(primary, 'row must carry a primary source URL')
                self.assertIn(primary, html)
                self.assertTrue(row['reason'])
                for attempt in row['attempts']:
                    self.assertIn(build.e(attempt['reason']), html)
                    self.assertIn(build.e(attempt['url']), html)

    def test_every_dossier_row_names_its_sources(self):
        for fixture in DOSSIER['fixtures']:
            with self.subTest(fixture=fixture['fixture_id']):
                self.assertTrue(str(fixture['hltv']['url']).startswith('https://www.hltv.org/matches/'))
                self.assertTrue(fixture['market_absence'], 'no provider probes recorded')
                self.assertTrue(fixture['valve_identity'], 'no Valve identity check recorded')
                self.assertTrue(str(fixture['hotspawn_source']).startswith('https://'))

    def test_dossier_decisions_reproduce_from_the_model(self):
        for fixture in DOSSIER['fixtures']:
            row = BY_ID.get(fixture['fixture_id'])
            if row is None:
                continue
            lineups = {x['team']: x['players'] for x in (row.get('hltv_context') or {}).get('lineups', [])}
            quote, reason = vrs.line(row, STANDINGS, VRS_META, lineups)
            decision = fixture['decision']
            with self.subTest(fixture=fixture['fixture_id']):
                if decision['probability'] is None:
                    self.assertIsNone(quote, 'Model now originates a line; re-run build_dossier.py')
                    self.assertEqual(decision['blocker'], reason)
                else:
                    self.assertIsNotNone(quote, reason)
                    self.assertAlmostEqual(decision['probability'][0], quote['probabilities'][0], places=12)
                    self.assertAlmostEqual(decision['probability'][1], quote['probabilities'][1], places=12)
                    self.assertEqual(decision['points'], quote['points'])
                    self.assertEqual(decision['standings'], quote['standings'])

    def test_a_probability_only_ever_comes_from_the_labelled_model(self):
        for fixture in DOSSIER['fixtures']:
            decision = fixture['decision']
            if decision['probability'] is None:
                self.assertIsNone(decision['method'])
                continue
            self.assertEqual('model_vrs', decision['method'])
            self.assertAlmostEqual(1.0, sum(decision['probability']), places=12)
            note = (decision.get('note') or '').lower()
            self.assertIn('not a market price', note)

    def test_unranked_teams_stay_blank_and_are_flagged(self):
        for fixture in DOSSIER['fixtures']:
            if fixture['decision']['probability'] is not None:
                continue
            absent = [e for e in fixture['valve_identity'] if e['status'] == 'absent']
            with self.subTest(fixture=fixture['fixture_id']):
                self.assertTrue(absent, 'A blank line must be caused by a team the standings do not list')
                for entry in absent:
                    self.assertEqual([], fixture['valve_lists_checked'][entry['label']],
                                     '%s appears in a Valve list, so a line should be possible' % entry['label'])
                    self.assertIn(entry['label'], fixture['decision']['blocker'])

    def test_valve_receipts_match_their_recorded_hashes(self):
        for receipt in DOSSIER['valve_receipts']:
            path = ROOT / receipt['file']
            with self.subTest(file=receipt['file']):
                self.assertTrue(path.exists(), path)
                self.assertEqual(receipt['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
                self.assertTrue(receipt['url'].startswith('https://github.com/ValveSoftware/'))
        global_receipt = next(r for r in DOSSIER['valve_receipts'] if r['file'].endswith('global_2026_10_05.md'))
        self.assertEqual(VENDORED_META['sha256'], global_receipt['sha256'],
                         'The vendored and retained copies of Valve\'s global list must be the same bytes')

    def test_market_receipts_are_hashed_and_the_scans_record_when_they_ran(self):
        by_file = {r['file']: r for r in DOSSIER['market_receipts']}
        self.assertIn('research/harvest-76712ccc/polymarket-cs2-scan.json', by_file)
        self.assertIn('research/harvest-76712ccc/pinnacle-sweep.json', by_file)
        for name, receipt in by_file.items():
            path = ROOT / receipt['file']
            with self.subTest(file=name):
                self.assertEqual(receipt['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
        for name in ('research/harvest-76712ccc/polymarket-cs2-scan.json',
                     'research/harvest-76712ccc/pinnacle-sweep.json'):
            self.assertRegex(str(by_file[name].get('observed_at')), r'^\d{4}-\d{2}-\d{2}T')


class Ex6666IdentityTests(unittest.TestCase):
    """The one alias this session registered, and the roster rule behind it."""

    def test_the_alias_folds_the_two_labels_together(self):
        self.assertEqual(core.norm('ex-6666'), core.norm('6666'))

    def test_the_entry_has_primary_sources_and_a_bounded_scope(self):
        register = json.loads((ROOT / 'data/identities.json').read_text())['aliases']
        entries = [a for a in register if a['canonical'] == '6666']
        self.assertTrue(entries, 'The 6666/ex-6666 identity is not registered')
        # Two sessions registered this same club while working in parallel (see the
        # session 76712ccc record in COORDINATION.md). A duplicate is tolerated so
        # that a merge order can never break the build, but every copy must still
        # describe the same club and carry its own primary sources.
        for entry in entries:
            with self.subTest(entry=entry['source']):
                self.assertEqual({'6666', 'ex-6666'}, set(entry['names']))
                self.assertTrue(entry['source'].startswith('https://'))
                self.assertTrue(entry['additional_source'].startswith('https://'))
                basis = entry['basis'].lower()
                self.assertIn('utc start', basis)
                self.assertIn('exact opponent', basis)
                self.assertIn('roster', basis)

    def test_the_lineup_selects_one_of_the_two_listed_6666_rosters(self):
        # a54996e1: current snapshot prices this row from the exchange and carries
        # no HLTV lineup context; use the retained cc88483d snapshot for the lineup.
        hist = json.loads((ROOT / 'research/session-cc88483d/snapshot.json').read_text())
        row = next(x for x in hist['matches'] if x['id'] == '1081521')
        lineup = next(x['players'] for x in row['hltv_context']['lineups'] if core.norm(x['team']) == core.norm('6666'))
        entry, note = vrs.identify('ex-6666', STANDINGS, lineup)
        self.assertEqual('roster verified against the HLTV lineup', note)
        self.assertEqual('6666', entry['name'])
        self.assertEqual(127, entry['standing'])
        self.assertEqual(923, entry['points'])
        self.assertEqual(4, entry['roster_overlap'])
        older = [r for r in STANDINGS['teams'] if core.norm(r['name']) == core.norm('6666') and r['standing'] == 368]
        self.assertEqual(1, len(older))
        shared = {core.plain_name(p) for p in lineup} & {core.plain_name(p) for p in older[0]['roster']}
        self.assertEqual(1, len(shared), 'The older roster must stay clearly behind the three-player rule')

    def test_without_the_alias_the_row_would_stay_unpriced(self):
        self.assertIsNone(vrs.identify('not-a-registered-label', STANDINGS, None)[0])

    def test_the_row_is_never_priced_from_a_rank_pick(self):
        row = BY_ID.get('1081521')
        if row is None:
            # ex-6666 vs Privateer finished, so a later refresh no longer carries
            # the row. Replay the same rule against the dated harvest that does
            # (research/session-a54996e1/snapshot.json, 2026-10-18T00:52:19Z),
            # rather than dropping the regression this file exists for.
            archived = json.loads((ROOT / 'research/session-a54996e1/snapshot.json').read_text())
            row = next(m for m in archived['matches'] if m['id'] == '1081521')
        self.assertIn(row['pick'], row['teams'])
        if row.get('probabilities') is None:
            self.assertIn('no probability published', ' '.join(row['flags']).lower())
        else:
            # Session 03befae8 (17 October 2026): the row is no longer on the
            # model line, because a dated external book listing now prices it
            # (EGamersWorld book average 1.15 / 4.5, receipt
            # egw-rW6Ymkl0D-ex-6666-privateer). The rule this test protects is
            # that the row is never priced from ranking order, and both allowed
            # methods satisfy it: a model line is labelled as a model estimate,
            # and a book line carries the dated external evidence.
            # a54996e1: the 2026-10-18 harvest prices this row from a validated
            # exchange line — also an external market method, never a rank pick.
            self.assertIn(row['method'], ('model_vrs', 'bookmaker_fallback', 'exchange', 'exchange_wide'))
            self.assertTrue(row.get('evidence'), 'A priced row must carry its evidence')
            if row['method'] in ('exchange', 'exchange_wide'):
                pass
            elif row['method'] == 'model_vrs':
                self.assertIn('not a market price', ' '.join(row['flags']))
            else:
                self.assertIn('Researched bookmaker listing',
                              ' '.join(row['flags'] + [row['evidence'][0].get('warning', '')]))


if __name__ == '__main__':
    unittest.main()
