"""Session 11e17543 - every listed match carries a pick, a probability, or its own limitation.

The requirement these pin: Hotspawn decides which CS2 matches are on the board, and
every one of them must resolve to a pick or to a recorded reason it could not. The
production ladder prices only rows whose pick lock is still open, which left 62 of
the 73 rows on the 2026-10-26T00:10:49Z snapshot with nothing on them at all.

Nothing here may be satisfied by inference. A probability must re-derive from
Valve's own published formula and Valve's own published point totals; a directional
pick without one must say why; and a row no official source supports must stay blank
and name the sources that were tried.
"""
import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import build, every_match_11e17543 as em
from scripts import vrs
from scripts.core import dt, norm

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())
OUTSIDE = json.loads((ROOT / 'research' / 'session-11e17543' / 'outside-lines.json').read_text())
REPORT = em.build()
STANDINGS, META = vrs.vendored()
BY_ID = {r['id']: r for r in REPORT['rows']}


def row(fixture_id):
    return next(m for m in SNAPSHOT['matches'] if str(m['id']) == str(fixture_id))


class EveryRowIsAccountedFor(unittest.TestCase):
    def test_the_report_covers_every_row_the_feed_returns(self):
        self.assertEqual(REPORT['rows_total'], len(SNAPSHOT['matches']))
        self.assertEqual({r['id'] for r in REPORT['rows']},
                         {str(m['id']) for m in SNAPSHOT['matches']})

    def test_no_row_falls_through_the_ladder_silently(self):
        for r in REPORT['rows']:
            self.assertIn(r['ladder'], em.TIER_RANK, r['id'])
            self.assertEqual(r['ladder_label'], em.TIER_LABEL[r['ladder']], r['id'])

    def test_a_row_is_either_picked_or_names_its_limitation(self):
        gaps = [r['id'] for r in REPORT['rows'] if not r['pick'] and not r['limitation']]
        self.assertEqual([], gaps, 'unresolved rows must state why')

    def test_every_row_links_at_least_one_official_source(self):
        for r in REPORT['rows']:
            urls = [s['url'] for s in r['sources'] if s.get('url')]
            self.assertTrue(urls, r['id'])
            self.assertTrue(all(u.startswith('https://') for u in urls), (r['id'], urls))
            # Open rows carry the per-fixture Hotspawn match page; retained rows
            # carry the pick'em board. Either is official, and it must be Hotspawn.
            self.assertIn('hotspawn.com', r['source_url'], r['id'])
            self.assertEqual(r['feed_url'], em.HOTSPAWN_FEED, r['id'])

    def test_coverage_equals_the_published_counts(self):
        self.assertEqual(REPORT['with_pick'], sum(1 for r in REPORT['rows'] if r['pick']))
        self.assertEqual(REPORT['with_probability'],
                         sum(1 for r in REPORT['rows'] if r['probabilities']))
        self.assertEqual(REPORT['unresolved'],
                         sum(1 for r in REPORT['rows'] if r['ladder'] == 'unresolved'))
        self.assertEqual(sum(REPORT['counts_by_ladder'].values()), REPORT['rows_total'])

    def test_the_open_rows_keep_the_line_the_production_ladder_published(self):
        opens = [m for m in SNAPSHOT['matches'] if m['state'] == 'open']
        self.assertTrue(opens, 'the snapshot must still carry open rows for this to mean anything')
        for m in opens:
            r = BY_ID[str(m['id'])]
            self.assertEqual('pipeline', r['ladder'], m['id'])
            self.assertEqual(m['pick'], r['pick'], m['id'])
            self.assertEqual(m['probabilities'], r['probabilities'], m['id'])


class ActionabilityIsNeverImplied(unittest.TestCase):
    def test_a_passed_lock_is_labelled_not_actionable_and_says_so(self):
        observed = dt(SNAPSHOT['fixtures_observed_at'])
        for m in SNAPSHOT['matches']:
            r = BY_ID[str(m['id'])]
            passed = m.get('lock') and dt(m['lock']) < observed
            if passed:
                self.assertFalse(r['actionable'], m['id'])
                self.assertIn('pick lock', r['limitation'], m['id'])
                self.assertIn(m['lock'], r['limitation'], m['id'])
            else:
                self.assertEqual(m['state'] == 'open', r['actionable'], m['id'])

    def test_a_historical_line_is_never_worded_as_a_recommendation(self):
        for r in REPORT['rows']:
            if not r['actionable'] and r['pick']:
                self.assertIn('not a current recommendation', r['limitation'], r['id'])


class ProbabilitiesReDeriveFromValve(unittest.TestCase):
    def test_every_model_line_replays_from_the_published_points(self):
        checked = 0
        for r in REPORT['rows']:
            if r['ladder'] != 'model_vrs':
                continue
            a, b = r['vrs_points']
            expected = vrs.calibrated(vrs.expected(a, b))
            self.assertAlmostEqual(expected, r['probabilities'][0], places=9, msg=r['id'])
            self.assertAlmostEqual(1 - expected, r['probabilities'][1], places=9, msg=r['id'])
            self.assertEqual(r['pick'], r['teams'][0] if r['probabilities'][0] > 0.5 else r['teams'][1], r['id'])
            self.assertAlmostEqual(sum(r['probabilities']), 1.0, places=12, msg=r['id'])
            checked += 1
        self.assertGreater(checked, 0, 'the snapshot must still exercise the model rung')

    def test_the_point_totals_are_really_in_valves_file(self):
        points = {row['points'] for row in STANDINGS['teams']}
        for r in REPORT['rows']:
            if r['ladder'] == 'model_vrs':
                for p in r['vrs_points']:
                    self.assertIn(p, points, (r['id'], p))

    def test_the_standings_copy_used_is_the_newest_valve_publishes(self):
        # Verified 2026-10-26 against
        # https://api.github.com/repos/ValveSoftware/counter-strike_regional_standings/contents/live/2026
        # whose newest global file is standings_global_2026_10_05.md.
        self.assertEqual('standings_global_2026_10_05.md', META['file'])
        self.assertEqual('2026-10-05', STANDINGS['as_of'])
        self.assertEqual(REPORT['standings']['as_of'], STANDINGS['as_of'])


class DirectionalRungsPublishNoNumber(unittest.TestCase):
    def test_one_sided_and_bounded_picks_stay_percentage_free(self):
        for r in REPORT['rows']:
            if r['ladder'] in ('research_one_sided', 'research_bounded'):
                self.assertIsNone(r['probabilities'], r['id'])
                self.assertIsNone(r['fair_odds'], r['id'])
                self.assertTrue(r['pick'], r['id'])
                self.assertIn('no win probability' if r['ladder'] == 'research_one_sided'
                              else 'no win percentage is published', r['limitation'], r['id'])

    def test_one_sided_requires_exactly_one_club_in_the_official_standings(self):
        for r in REPORT['rows']:
            if r['ladder'] != 'research_one_sided':
                continue
            flags = [em.listed(t, STANDINGS) for t in r['teams']]
            self.assertEqual(1, flags.count(True), (r['id'], flags))
            self.assertEqual(r['pick'], r['teams'][0] if flags[0] else r['teams'][1], r['id'])

    def test_the_bounded_rung_refuses_when_the_candidate_ranges_overlap(self):
        # 6666 is listed twice by Valve (425 and 923 points) and BERG once (754).
        # 425 < 754 < 923, so the direction depends on a roster we cannot confirm.
        index, reason = em.bounded_direction(['6666', 'BERG'], STANDINGS)
        self.assertIsNone(index)
        self.assertIn('overlap', reason)
        self.assertEqual('unresolved', BY_ID['1053442']['ladder'])

    def test_the_bounded_rung_holds_for_every_roster_valve_lists(self):
        for r in REPORT['rows']:
            if r['ladder'] != 'research_bounded':
                continue
            sets = [em.candidates(t, STANDINGS) for t in r['teams']]
            self.assertGreater(max(len(sets[0]), len(sets[1])), 1, r['id'])
            lo = [(min(x['points'] for x in s), max(x['points'] for x in s)) for s in sets]
            winner = r['teams'].index(r['pick'])
            loser = 1 - winner
            self.assertGreater(lo[winner][0], lo[loser][1],
                               'the weakest reading must still win: %s' % r['id'])


class NothingIsInvented(unittest.TestCase):
    def test_a_club_absent_from_the_official_standings_is_never_priced(self):
        self.assertFalse(em.listed('Sharks', STANDINGS))
        self.assertFalse(em.listed('ex-Tricked', STANDINGS))
        self.assertEqual('unresolved', BY_ID['1051343']['ladder'])
        self.assertIsNone(BY_ID['1051343']['pick'])
        self.assertIn('not listed in the Valve global standings', BY_ID['1051343']['limitation'])

    def test_a_hotspawn_crowd_percentage_is_never_used_as_a_probability(self):
        evidence = {f['id']: f for f in SNAPSHOT['fixture_evidence']}
        for r in REPORT['rows']:
            if not r['probabilities']:
                continue
            crowd = [evidence[r['id']].get('participants%d_picked_percent' % i) for i in (0, 1)]
            crowd = [c for c in crowd if isinstance(c, (int, float)) and c not in (0, 100)]
            for c in crowd:
                for p in r['probabilities']:
                    self.assertNotAlmostEqual(
                        c / 100.0, p, places=3,
                        msg='%s publishes Hotspawn crowd %s%% as a probability' % (r['id'], c))

    def test_only_well_formed_captured_lines_can_become_a_probability(self):
        good = {'provider': 'x', 'url': 'https://example.test', 'prices': [0.62, 0.38]}
        self.assertIsNotNone(em.outside_line('1', {'1': good}))
        for broken in ({'provider': 'x', 'url': 'https://e.test', 'prices': [0.9, 0.9]},
                       {'provider': 'x', 'url': 'https://e.test', 'prices': [0.5]},
                       {'url': 'https://e.test', 'prices': [0.6, 0.4]},
                       {'provider': 'x', 'prices': [0.6, 0.4]},
                       {'provider': 'x', 'url': 'https://e.test', 'prices': ['0.6', 'x']}):
            self.assertIsNone(em.outside_line('1', {'1': broken}), broken)

    def test_the_committed_line_registry_is_well_formed(self):
        self.assertIsInstance(OUTSIDE.get('lines'), dict)
        for fixture_id, entry in OUTSIDE['lines'].items():
            self.assertIsNotNone(em.outside_line(fixture_id, {fixture_id: entry}), fixture_id)
        for attempt in OUTSIDE.get('attempts') or []:
            self.assertTrue(attempt.get('fixture_id') and attempt.get('results'), attempt)
            for res in attempt['results']:
                self.assertTrue(res.get('url', '').startswith('https://'), res)
                self.assertTrue(res.get('outcome'), res)


class PublishedSiteCarriesTheCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import tempfile
        cls.tmp = tempfile.TemporaryDirectory()
        build.build(json.loads(json.dumps(SNAPSHOT)), cls.tmp.name,
                    now=dt(SNAPSHOT['generated_at']))
        cls.matches = BeautifulSoup((Path(cls.tmp.name) / 'matches.html').read_text(), 'html.parser')
        cls.index = BeautifulSoup((Path(cls.tmp.name) / 'index.html').read_text(), 'html.parser')
        cls.unresolved = BeautifulSoup((Path(cls.tmp.name) / 'unresolved.html').read_text(), 'html.parser')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def table_rows(self, soup, section_id):
        return soup.select_one('#' + section_id).select('table tbody tr')

    def test_the_every_match_table_has_one_row_per_feed_row(self):
        rows = self.table_rows(self.matches, 'every-match')
        self.assertEqual(len(SNAPSHOT['matches']), len(rows))
        self.assertEqual({str(m['id']) for m in SNAPSHOT['matches']},
                         {tr.select_one('td').get_text(strip=True) for tr in rows})

    def test_every_published_row_carries_a_source_link(self):
        for tr in self.table_rows(self.matches, 'every-match'):
            links = [a['href'] for a in tr.select('td.source-links a[href]')]
            self.assertTrue(links, tr.get_text(' ', strip=True)[:80])

    def test_the_executive_summary_links_the_table_the_user_is_looking_for(self):
        hrefs = {a['href'] for a in self.index.select('a[href]')}
        self.assertIn('matches.html#every-match', hrefs)
        self.assertIn('picks.html', hrefs)
        self.assertIn('unresolved.html', hrefs)
        # The anchor the summary points at must exist on the page it points to.
        self.assertIsNotNone(self.matches.select_one('#every-match'))

    def test_the_unresolved_page_names_every_listed_match_without_a_pick(self):
        section = self.unresolved.select_one('#every-match-unresolved')
        self.assertIsNotNone(section)
        missing = {r['id'] for r in REPORT['rows'] if not r['pick']}
        rendered = {tr.select_one('td').get_text(strip=True)
                    for tr in section.select('table tbody tr')}
        self.assertEqual(missing, rendered)

    def test_the_unresolved_section_is_published_even_when_the_count_is_zero(self):
        self.assertIn('zero unresolved today is not a claim', build.every_match_unresolved(
            {'generated_at': SNAPSHOT['generated_at'],
             'fixtures_observed_at': SNAPSHOT['fixtures_observed_at'],
             'matches': [m for m in SNAPSHOT['matches'] if m['state'] == 'open']}))

    def test_the_banner_states_the_every_match_coverage_counts(self):
        text = self.index.get_text(' ', strip=True)
        rep = build.every_match_report(SNAPSHOT)
        self.assertIn('%d of %d listed matches have a pick' % (rep['with_pick'], rep['rows_total']), text)

    def test_no_phone_media_query_hides_the_new_coverage_table(self):
        css = (ROOT / 'site' / 'assets' / 'style.css').read_text()
        self.assertEqual(css, (ROOT / 'assets' / 'style.css').read_text(),
                         'the served stylesheet must stay byte-identical to the canonical one')
        for query in [q for q in css.split('@media') if 'max-width:650px' in q[:40]]:
            for selector in ('#every-match', '#every-match-unresolved'):
                self.assertNotIn(selector + '{display:none', query.replace(' ', ''),
                                 'a phone rule must not hide the coverage table')


class ReportArtifactsAreComplete(unittest.TestCase):
    def test_the_written_artifacts_match_the_report(self):
        rep = em.write_all()
        csv_text = (em.OUT_DIR / 'every-match-picks.csv').read_text()
        self.assertEqual(len(SNAPSHOT['matches']) + 1, len(csv_text.strip().splitlines()))
        markdown = (em.OUT_DIR / 'every-match-picks.md').read_text()
        self.assertIn('| Fixture | Match |', markdown)
        self.assertEqual(rep['rows_total'], len(json.loads(
            (em.OUT_DIR / 'every-match-picks.json').read_text())['rows']))


if __name__ == '__main__':
    unittest.main()
