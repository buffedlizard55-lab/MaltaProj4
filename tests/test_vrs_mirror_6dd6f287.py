"""Session 6dd6f287: the HLTV Valve-ranking mirror tier.

The tier exists for one situation: a Hotspawn fixture whose clubs cannot both
be resolved in Valve's monthly GitHub standings file, so the official-file model
line cannot run and the row would otherwise publish a research pick with no
percentage. HLTV publishes the same Valve ranking, dated, continuously.

Everything here is fail-closed evidence handling, not a forecast test: a page
that is not the Valve view, a missing date, a short or unordered table, an
ambiguous label, or a club that is simply not listed must never produce a
number.
"""
import copy
import json
import re
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts import validate, vrs, vrs_mirror

ROOT = Path(__file__).resolve().parents[1]
# A retained HLTV ranking page (the world-ranking view, 2026-10-12). Its markup
# is the same ranked-team layout this parser reads; only the label inside the
# points span differs, which is exactly what the fail-closed check keys on.
RANKING_HTML = ROOT / 'research/harvest-76712ccc/HLTV_world_ranking.html'


def valve_view_html():
    """The retained page with its points label flipped to Valve's wording.

    This is a parser fixture, not a claim about the live page: the live page is
    read at refresh time and its own dated heading is what gets published.
    """
    html = RANKING_HTML.read_text(encoding='utf-8', errors='replace')
    return re.sub(r'(<span class="gtSmartphone-only">\s*)HLTV(\s*</span>)', r'\1Valve\2', html)


class ParseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.standings = vrs_mirror.parse(valve_view_html())

    def test_world_ranking_page_is_not_valve_evidence(self):
        # "HLTV points" is a different ranking. A parser that accepted it would
        # be inventing the word "Valve".
        with self.assertRaises(ValueError):
            vrs_mirror.parse(RANKING_HTML.read_text(encoding='utf-8', errors='replace'))

    def test_dated_heading_is_read(self):
        self.assertEqual('2026-10-12', self.standings['as_of'])
        self.assertIn('ranking on October 12th, 2026', self.standings['heading'])

    def test_table_is_complete_and_ordered(self):
        rows = self.standings['teams']
        self.assertGreaterEqual(len(rows), 100)
        self.assertEqual([r['standing'] for r in rows], list(range(1, len(rows) + 1)))
        first = rows[0]
        self.assertEqual('Spirit', first['name'])
        self.assertIsInstance(first['points'], int)
        self.assertGreater(first['points'], 0)
        self.assertEqual(5, len(first['roster']))

    def test_short_or_unordered_table_is_a_miss(self):
        rows = self.standings['teams'][:40]
        self.assertFalse(vrs_mirror._complete(rows))
        shuffled = copy.deepcopy(rows)
        shuffled[0]['standing'], shuffled[1]['standing'] = shuffled[1]['standing'], shuffled[0]['standing']
        self.assertFalse(vrs_mirror._complete(shuffled))

    def test_missing_date_header_is_a_miss(self):
        html = valve_view_html().replace('ranking on October', 'listing from October')
        with self.assertRaises(ValueError):
            vrs_mirror.parse(html)

    def test_identify_uses_valve_roster_continuity(self):
        standings = {'as_of': '2026-10-12', 'heading': 'x', 'teams': [
            {'standing': 1, 'points': 1000, 'name': 'Dup', 'roster': ['a', 'b', 'c', 'd', 'e'], 'details': ''},
            {'standing': 2, 'points': 800, 'name': 'Dup', 'roster': ['v', 'w', 'x', 'y', 'z'], 'details': ''},
        ]}
        entry, note = vrs.identify('Dup', standings)
        self.assertIsNone(entry)
        self.assertIn('appears 2 times', note)
        entry, _ = vrs.identify('Dup', standings, ['a', 'b', 'c', 'q', 'e'])
        self.assertEqual(1, entry['standing'])


def fixture():
    return {'id': '999001', 'teams': ['Alpha', 'Bravo'], 'state': 'open', 'probabilities': None,
            'fair_odds': None, 'pick': None, 'method': None, 'evidence': [], 'attempts': [], 'flags': []}


def standings(alpha=1435, bravo=700, extra_duplicate=False):
    """A ranking of 120 clubs: the two on the fixture plus filler rows.

    The published table is long by construction, which is what the validator
    requires; the interesting rows keep their real-world shape (a top-40 club
    and a club only Valve's continuous view lists).
    """
    rows = []
    for standing in range(1, 121):
        rows.append({'standing': standing, 'points': 1500 - standing * 4,
                     'name': 'Filler %03d' % standing,
                     'roster': ['f%d' % (standing * 10 + i) for i in range(5)], 'details': ''})
    rows[30] = {'standing': 31, 'points': alpha, 'name': 'Alpha',
                'roster': ['a1', 'a2', 'a3', 'a4', 'a5'], 'details': ''}
    rows[99] = {'standing': 100, 'points': bravo, 'name': 'Bravo',
                'roster': ['b1', 'b2', 'b3', 'b4', 'b5'], 'details': ''}
    rows[79] = {'standing': 80, 'points': 811, 'name': 'Absent',
                'roster': ['c1', 'c2', 'c3', 'c4', 'c5'], 'details': ''}
    if extra_duplicate:
        rows[109] = {'standing': 110, 'points': 600, 'name': 'Bravo',
                     'roster': ['z1', 'z2', 'z3', 'z4', 'z5'], 'details': ''}
    return {'as_of': '2026-10-12', 'heading': 'Valve global ranking on October 12th, 2026', 'teams': rows}


STANDINGS = standings()
META = {'url': vrs_mirror.RANKING, 'observed_at': '2026-10-22T01:00:00Z', 'sha256': 'x' * 64,
        'as_of': '2026-10-12', 'heading': STANDINGS['heading'], 'teams_count': len(STANDINGS['teams']),
        'parsed_by': 'ranked-team blocks'}
OFFICIAL = {'file': 'standings_global_2026_10_05.md', 'commit': 'e' * 40, 'as_of': '2026-10-05'}


class ApplyTests(unittest.TestCase):
    def test_two_listed_clubs_get_a_reproducible_line(self):
        row = fixture()
        vrs_mirror.apply(row, STANDINGS, META, {}, OFFICIAL)
        self.assertEqual('model_vrs_mirror', row['method'])
        self.assertEqual('Alpha', row['pick'])
        quote = row['evidence'][0]
        self.assertEqual(vrs_mirror.PROVIDER, quote['provider'])
        self.assertEqual(vrs_mirror.RANKING, quote['url'])
        self.assertEqual([1435, 700], quote['points'])
        raw = vrs.expected(1435, 700)
        self.assertAlmostEqual(vrs.calibrated(raw), row['probabilities'][0], places=12)
        self.assertAlmostEqual(1.0, sum(row['probabilities']), places=12)
        self.assertIn(vrs_mirror.MODEL_FLAG, row['flags'])
        self.assertIn('HLTV\'s dated Valve ranking', ' '.join(row['flags']))
        self.assertEqual('2026-10-05', quote['official_file']['as_of'])

    def test_pick_follows_the_larger_probability(self):
        row = fixture()
        flipped = standings(alpha=700, bravo=1435)
        vrs_mirror.apply(row, flipped, META, {}, OFFICIAL)
        self.assertEqual('Bravo', row['pick'])

    def test_unlisted_club_is_a_recorded_miss(self):
        row = fixture()
        row['teams'] = ['Alpha', 'Nowhere']
        vrs_mirror.apply(row, STANDINGS, META, {}, OFFICIAL)
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['method'])
        self.assertEqual('unresolved', row['attempts'][-1]['status'])
        self.assertIn('not listed', row['attempts'][-1]['reason'])

    def test_a_market_line_is_never_overwritten(self):
        row = fixture()
        row.update(probabilities=[0.6, 0.4], method='exchange', pick='Alpha')
        vrs_mirror.apply(row, STANDINGS, META, {}, OFFICIAL)
        self.assertEqual('exchange', row['method'])
        self.assertEqual([0.6, 0.4], row['probabilities'])
        self.assertEqual([], row['attempts'])

    def test_duplicate_label_needs_a_lineup(self):
        duplicated = standings(extra_duplicate=True)
        row = fixture()
        vrs_mirror.apply(row, duplicated, META, {}, OFFICIAL)
        self.assertIsNone(row['probabilities'])
        self.assertIn('appears 2 times', row['attempts'][-1]['reason'])
        resolved = fixture()
        vrs_mirror.apply(resolved, duplicated, META, {'Bravo': ['b1', 'b2', 'b3', 'b4', 'b5']}, OFFICIAL)
        self.assertEqual('model_vrs_mirror', resolved['method'])
        self.assertGreaterEqual(resolved['evidence'][0]['roster_checks'][1]['overlap'], vrs.ROSTER_OVERLAP)

    def test_equal_points_give_no_directional_edge(self):
        # Integration repair, session e86697a6 (2026-10-24): an exactly even
        # model estimate is now retained as rejected evidence and the research
        # tiers continue, instead of publishing numbers with no pick (a state
        # this project's own coverage contracts forbid, measured on fixture
        # 1079200 at 16:31Z).
        level = standings(alpha=1435, bravo=1435)
        row = fixture()
        vrs_mirror.apply(row, level, META, {}, OFFICIAL)
        self.assertIsNone(row['pick'])
        self.assertIsNone(row['probabilities'])
        self.assertEqual(row['attempts'][-1]['status'], 'unresolved')
        self.assertEqual([0.5, 0.5], row['attempts'][-1]['rejected_quote']['probabilities'])


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 22, 2, 0, tzinfo=timezone.utc)
        self.row = fixture()
        vrs_mirror.apply(self.row, STANDINGS, META, {}, OFFICIAL)

    def test_a_faithful_row_passes(self):
        validate.validate_mirror_row(self.row, self.row['evidence'][0], self.now)

    def test_altered_points_fail(self):
        quote = copy.deepcopy(self.row['evidence'][0])
        quote['points'] = [1435, 1400]
        with self.assertRaises(AssertionError):
            validate.validate_mirror_row(self.row, quote, self.now)

    def test_non_hltv_source_fails(self):
        quote = copy.deepcopy(self.row['evidence'][0])
        quote['url'] = quote['api_url'] = 'https://example.com/ranking'
        with self.assertRaises(AssertionError):
            validate.validate_mirror_row(self.row, quote, self.now)

    def test_missing_flag_fails(self):
        row = copy.deepcopy(self.row)
        row['flags'] = [f for f in row['flags'] if f != vrs_mirror.MODEL_FLAG]
        with self.assertRaises(AssertionError):
            validate.validate_mirror_row(row, row['evidence'][0], self.now)

    def test_short_ranking_fails(self):
        quote = copy.deepcopy(self.row['evidence'][0])
        quote['ranking_teams_count'] = 12
        with self.assertRaises(AssertionError):
            validate.validate_mirror_row(self.row, quote, self.now)

    def test_stale_inputs_fail(self):
        old = datetime(2026, 10, 22, 20, 0, tzinfo=timezone.utc)
        with self.assertRaises(AssertionError):
            validate.validate_mirror_row(self.row, self.row['evidence'][0], old)


class WiringTests(unittest.TestCase):
    def test_build_treats_the_mirror_as_a_model_row(self):
        from scripts import build
        self.assertEqual('Our model line · HLTV mirror', build.METHOD_TAGS['model_vrs_mirror'])
        self.assertTrue(build.is_model({'method': 'model_vrs_mirror'}))
        self.assertTrue(build.is_model({'method': 'model_vrs'}))
        self.assertFalse(build.is_model({'method': 'exchange'}))
        self.assertFalse(build.is_research({'method': 'model_vrs_mirror'}))

    def test_refresh_tries_the_mirror_only_when_a_row_is_still_unpriced(self):
        source = (ROOT / 'scripts/refresh.py').read_text()
        self.assertIn('mirror_open = [m for m in open_matches if m[\'probabilities\'] is None]', source)
        self.assertIn('vrs_mirror.apply(m, mirror_standings, mirror_meta, lineups, official)', source)

    def test_method_is_documented_in_the_pages_build(self):
        source = (ROOT / 'scripts/build.py').read_text()
        self.assertIn('model_vrs_mirror', source)
        self.assertIn('HLTV’s dated view of Valve’s ranking', source)

    def test_validator_dispatches_the_new_method(self):
        source = (ROOT / 'scripts/validate.py').read_text()
        self.assertIn("if m['method'] == 'model_vrs_mirror':", source)
        self.assertIn('validate_mirror_row(m, q, now)', source)

    def test_refresh_records_a_parse_miss_as_a_finding(self):
        source = (ROOT / 'scripts/refresh.py').read_text()
        self.assertIn("flags.append(issue('vrs_mirror'", source)
        self.assertIn("'provider': 'HLTV Valve ranking mirror', 'status': 'error'", source)


if __name__ == '__main__':
    unittest.main()
