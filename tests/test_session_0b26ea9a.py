"""Session 0b26ea9a: the last unpicked fixture, a tier that never ran, and a
latent NameError on the branch it would have taken.

Read on the pre-merge base commit (``b648875``) on 2026-10-21: the refreshed
board carried 19 open fixtures, 18 had a pick, and 1082762 (ex-CYBERSHOKE vs
BlinkDagger, CIS LAN Championship #9) had none. Two independent reasons:

* ``scripts/vrs.py`` already implemented ``research_single`` - the documented
  final tier for "exactly one team resolves in Valve's official global
  standings, the other label is genuinely absent" - and the build, the
  validator and the independent auditor all handled ``research_vrs_single``.
  But no collector called it, so the tier could not fire in production.
* Hotspawn's label ``ex-CYBERSHOKE`` did not resolve to the exchange's
  ``CYBERSHOKE Esports``, so the fixture had no line either.

Main landed both fixes in parallel (session 5ed35e72, PR #99), with a narrower
mapping anchored on the exact opponent pair and UTC start and a deliberate
refusal to map the bare ``CYBERSHOKE`` label. This module therefore keeps what
main does not have: proof that the one-sided tier really is reachable and that
both independent checks replay it, the fix for an undefined name on that
branch, and the record of two refused two-way displays for the fixture.

Nothing here asserts a probability for 1082762: no single book's own two-way
line was available (EGamersWorld showed the identical 1.8/1.8 placeholder;
HLTV's betting table exposed no numeric line; an aggregator displayed
1.12/5.59 with no book named). Both displays are rejections, not prices.
"""
import importlib.util
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts import vrs
from scripts.core import iso, norm, normalize_fixtures
from scripts.validate import validate_data

ROOT = Path(__file__).resolve().parents[1]
TABLE = vrs.parse((ROOT / 'data/vrs/standings_global_2026_10_05.md').read_text())
IDENTITIES = json.loads((ROOT / 'data/identities.json').read_text())
RECEIPTS = json.loads((ROOT / 'data/book-receipts.json').read_text())
NOTES = json.loads((ROOT / 'data/review-notes.json').read_text())

NOW = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)
START = NOW + timedelta(hours=20)
LINEUP = ['bl1x1', 'Mokuj1n', 'nota', 'yiksrezo', 'shoke']


def load_auditor():
    spec = importlib.util.spec_from_file_location('audit_snapshot', ROOT / 'verification-c6/audit_snapshot.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def meta():
    doc = json.loads((ROOT / 'data/vrs/meta.json').read_text())
    return dict(doc, origin='test vendored copy', observed_at=iso(NOW))


def fixture():
    raw = {'id': '1082762', 'sport_alias': 'cs2', 'participants0_name': 'ex-CYBERSHOKE',
           'participants1_name': 'BlinkDagger', 'participants0_id': '209616',
           'participants1_id': '209617', 'status': 'scheduled',
           'scheduled_start_time': iso(START), 'lock_time': iso(START - timedelta(minutes=6)),
           'competition_name': 'CIS LAN Championship #9', 'tier': 'c'}
    row = normalize_fixtures([raw], {}, NOW)[0]
    row.update(probabilities=None, fair_odds=None, pick=None, method=None, evidence=[],
               flags=[], attempts=[], reason=None)
    row['hltv_context'] = {
        'teams': ['ex-CYBERSHOKE', 'BlinkDagger'], 'start': iso(START),
        'ranks': [
            {'team': 'ex-CYBERSHOKE', 'hltv_rank': None, 'source': None, 'hltv_unranked': True,
             'vrs_rank_on_hltv': 78,
             'vrs_source': 'https://www.hltv.org/valve-ranking/teams?teamId=14106'},
            {'team': 'BlinkDagger', 'hltv_rank': None, 'source': None, 'hltv_unranked': True,
             'vrs_rank_on_hltv': None, 'vrs_source': None},
        ],
        'lineups': [{'team': 'ex-CYBERSHOKE', 'players': LINEUP},
                    {'team': 'BlinkDagger', 'players': ['Aunkere', 'airscape', 'OverDrive',
                                                        'D9D9VOLODYA', 'h0sster']}],
        'source': 'https://www.hltv.org/matches/2399839/ex-cybershoke-vs-blinkdagger-winline-mpkbk-cis-lan-season-9',
        'observed_at': iso(NOW), 'numeric_quote_rows': 0, 'limitation': 'context only',
    }
    return raw, row


def lineups(row):
    """The collector passes HLTV lineups; without them a duplicated Valve label
    cannot be told apart and the tier correctly stays silent."""
    return {entry['team']: entry['players'] for entry in row['hltv_context']['lineups']}


def snapshot(row, raw):
    return {'schema_version': 2, 'generated_at': iso(NOW), 'last_attempt_at': iso(NOW),
            'fixtures_observed_at': iso(NOW), 'coverage': 'verified', 'matches': [row],
            'fixture_evidence': [raw], 'issues': [], 'source_checks': []}


class CybershokeIdentityTests(unittest.TestCase):
    def test_ex_label_maps_to_the_org_label_only(self):
        # main's register maps the feed label to the exchange/Liquipedia label
        # on fixture parity, and leaves the bare club label alone because
        # Valve lists two different CYBERSHOKE rosters.
        self.assertEqual(norm('ex-CYBERSHOKE'), norm('CYBERSHOKE Esports'))
        self.assertNotEqual(norm('ex-CYBERSHOKE'), norm('CYBERSHOKE'))
        self.assertNotEqual(norm('CYBERSHOKE Prospects'), norm('CYBERSHOKE Esports'))

    def test_register_entry_cites_primary_sources(self):
        entry = next(a for a in IDENTITIES['aliases'] if 'ex-CYBERSHOKE' in a['names'])
        self.assertIn('CYBERSHOKE Esports', entry['names'])
        self.assertNotIn('CYBERSHOKE Prospects', entry['names'])
        self.assertNotIn('CYBERSHOKE', entry['names'])
        self.assertTrue(entry['source'].startswith('https://www.hltv.org/matches/2399839/'))
        self.assertIn('exact opponent pair', entry['basis'])
        self.assertIn('2026-10-21T15:00:00Z', entry['basis'])

    def test_a_renamed_label_does_not_reach_the_standings_by_itself(self):
        # Honest limit, published rather than papered over: the register maps
        # labels to each other, and the standings tier matches Valve's own
        # labels. main's mapping therefore cannot make this club resolvable in
        # Valve's file, which is one reason the fixture is flagged for review.
        entry, note = vrs.identify('ex-CYBERSHOKE', TABLE, LINEUP)
        self.assertIsNone(entry)
        self.assertIn('not listed', note)

    def test_the_standings_tier_itself_still_resolves_a_listed_label(self):
        # The tier is not broken; the label simply is not in Valve's file under
        # the name the register chose. A duplicated listed label needs a lineup.
        entry, note = vrs.identify('CYBERSHOKE', TABLE, LINEUP)
        self.assertIsNotNone(entry, note)
        self.assertEqual((entry['standing'], entry['points']), (61, 1201))
        self.assertEqual(entry['roster_overlap'], 3)
        unresolved, why = vrs.identify('CYBERSHOKE', TABLE, None)
        self.assertIsNone(unresolved)
        self.assertIn('appears', why)


class OneSidedTierTests(unittest.TestCase):
    """The tier must be reachable and must publish no number of any kind."""

    def quoted(self):
        """The row exactly as captured, with a standings table that carries the
        feed's own label for the #61 roster. The tier is about a label that is
        listed versus one that is absent, not about renaming rows to fit."""
        raw, row = fixture()
        table = dict(TABLE)
        table['teams'] = [dict(t, name='ex-CYBERSHOKE') if t['name'] == 'CYBERSHOKE' and t['standing'] == 61 else t
                          for t in TABLE['teams']]
        return raw, row, table

    def test_a_one_sided_fixture_gets_a_pick_and_no_numbers(self):
        raw, row, table = self.quoted()
        vrs.research_single(row, table, meta(), lineups(row))
        self.assertEqual((row['pick'], row['method']), ('ex-CYBERSHOKE', 'research_vrs_single'))
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['fair_odds'])
        self.assertEqual(row['evidence'], [])
        self.assertIn('not a market probability', row['reason'])
        resolved = {r['team']: r for r in row['vrs_research']['resolved_vrs']}
        self.assertEqual(resolved['ex-CYBERSHOKE']['status'], 'listed')
        self.assertEqual(resolved['ex-CYBERSHOKE']['standing'], 61)
        self.assertEqual(resolved['BlinkDagger']['status'], 'absent')
        self.assertEqual(resolved['BlinkDagger']['label_count'], 0)

    def test_both_independent_checks_replay_the_row(self):
        # scripts/validate.py referenced an undefined IDENTITY_REGISTER on this
        # very branch; this replay is what would have crashed on it.
        raw, row, table = self.quoted()
        vrs.research_single(row, table, meta(), lineups(row))
        data = snapshot(row, raw)
        validate_data(data)
        _, errors = load_auditor().inspect(data)
        self.assertEqual(errors, [])

    def test_a_renamed_standings_label_passes_the_registered_mapping_check(self):
        # scripts/validate.py referenced an undefined IDENTITY_REGISTER on this
        # exact branch: a research pick whose Valve label differs from the
        # feed's label. Replay it, so the name must be bound.
        raw, row, table = self.quoted()
        vrs.research_single(row, table, meta(), lineups(row))
        row['vrs_research']['resolved_vrs'][0]['vrs_name'] = 'CYBERSHOKE Esports'
        validate_data(snapshot(row, raw))

    def test_hltv_displayed_vrs_rank_for_the_absent_team_blocks_it(self):
        raw, row, table = self.quoted()
        row['hltv_context']['ranks'][1]['vrs_rank_on_hltv'] = 240
        vrs.research_single(row, table, meta(), lineups(row))
        self.assertIsNone(row['pick'])
        self.assertEqual(row['attempts'][-1]['status'], 'unresolved')


class CollectorWiringTests(unittest.TestCase):
    """The tier must actually be called, after the HLTV ranking tiers."""

    source = (ROOT / 'scripts/refresh.py').read_text()

    def test_refresh_calls_the_final_tier(self):
        self.assertIn('vrs.research_single(', self.source)

    def test_it_runs_after_the_ranking_tiers(self):
        self.assertGreater(self.source.index('vrs.research_single('), self.source.index('research_rank_pick(m)'))

    def test_it_only_runs_for_open_rows_without_a_pick(self):
        call = self.source[self.source.index('vrs.research_single(') - 400:self.source.index('vrs.research_single(') + 120]
        self.assertIn("m['state']=='open'", call)
        self.assertIn('m[\'probabilities\'] is None', call)
        self.assertIn("not m.get('pick')", call)


class RejectedLineTests(unittest.TestCase):
    def test_no_researched_receipt_prices_the_published_row(self):
        # main holds a cross-operator panel receipt for this fixture that is
        # flagged for review; the published row must not be built from it.
        snapshot = json.loads((ROOT / 'data/latest.json').read_text())
        row = next((m for m in snapshot['matches'] if str(m['id']) == '1082762'), None)
        if row is not None and row.get('probabilities'):
            self.assertNotIn('bookmaker_fallback', str(row.get('method')),
                             'a cross-operator panel must not become the published line')

    def test_both_refused_lines_are_recorded_with_values_and_reasons(self):
        rejected = [r for r in RECEIPTS['rejected_listings'] if str(r.get('fixture_id')) == '1082762']
        urls = {r['url'] for r in rejected}
        self.assertIn('https://egamersworld.com/counterstrike/match/4yp_dlKtNl/ex-cybershoke-vs-blinkdagger-5sOoK5oHU4', urls)
        self.assertIn('https://kushvsporte.ru/event/6990334-cybershoke-blinkdagger', urls)
        egw = next(r for r in rejected if 'egamersworld' in r['url'])
        self.assertEqual(egw['displayed'], [1.8, 1.8])
        agg = next(r for r in rejected if 'kushvsporte' in r['url'])
        self.assertEqual(agg['displayed'], [1.12, 5.59])
        for record in rejected:
            self.assertTrue(record['reason'].strip())
            self.assertTrue(record['observed_at'].endswith('Z'))

    def test_the_limitation_is_published_for_review(self):
        note = next(n for n in NOTES if n['id'] == '0b26ea9a-one-sided-tier')
        self.assertTrue(note['finding'])
        urls = [s['url'] for s in note['sources']]
        self.assertTrue(any('hltv.org/matches/2399839' in u for u in urls))
        self.assertTrue(any('ValveSoftware/counter-strike_regional_standings' in u for u in urls))


if __name__ == '__main__':
    unittest.main()
