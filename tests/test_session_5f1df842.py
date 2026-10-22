"""Session 5f1df842: a complete-pick executive summary that is phone-readable.

What is asserted, and why each assertion exists:

1. ``scripts.summary`` counts a real snapshot the way the page displays it. The
   regression it guards against is a headline that says "every match has a pick"
   while a row further down publishes none, so every count is re-derived here
   from the fixture rows themselves rather than from the helper under test.
2. A row without a verified two-sided line keeps no percentage and no fair odds
   through the build, and one-sided evidence is reported as a *research* pick,
   never as a market probability. Nothing in this session's code can turn a blank
   into a number.
3. The executive summary carries the coverage block, an in-site link to the
   updated pick list, and its own unresolved/limitations section with the
   ordered ladder of sources; every ladder step links an official source.
4. The unresolved section renders the same number of rows as the snapshot has
   unpriced open fixtures, each with its own reason and official links.
5. Phone layout: the unresolved rows are visible at 390 px (they must not reuse
   ``.glance-row``, which is hidden on phones in favour of the glance cards) and
   the new secondary buttons keep light-theme colours on a light panel.
"""
import json
import re
import sys
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import build, summary  # noqa: E402


def snapshot():
    """A minimal snapshot shaped exactly like data/latest.json."""
    return {
        'schema_version': 2,
        'generated_at': '2026-10-22T00:55:00Z',
        'last_attempt_at': '2026-10-22T00:55:00Z',
        'fixtures_observed_at': '2026-10-22T00:54:00Z',
        'coverage': 'verified',
        'refresh_hours': 1,
        'stale_after_hours': 8,
        'coverage_counts': {'api': 4, 'page': 4, 'lobby': 4, 'retained': 4},
        'issues': [],
        'fixture_conflicts': [],
        'inventory_changes': [],
        'fixture_evidence': [],
        'source_checks': [],
        'matches': [
            # 1. Market line: two-sided Polymarket quote.
            {'id': '1', 'teams': ['Alpha', 'Bravo'], 'team_ids': ['a', 'b'],
             'competition': 'Test Cup', 'tier': 'b', 'best_of': 3,
             'start': '2026-10-23T10:00:00Z', 'lock': '2026-10-23T09:54:00Z',
             'source_status': 'scheduled', 'state': 'open',
             'source_url': 'https://www.hotspawn.com/matches/alpha-vs-bravo-test-cup-1',
             'feed_url': 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1',
             'flags': [], 'probabilities': [0.62, 0.38], 'fair_odds': [1.6129, 2.6316],
             'pick': 'Alpha', 'method': 'exchange',
             'evidence': [{'provider': 'Polymarket', 'id': 'm1',
                           'api_url': 'https://gamma-api.polymarket.com/markets/m1',
                           'url': 'https://polymarket.com/event/alpha-bravo',
                           'observed_at': '2026-10-22T00:50:00Z',
                           'updated_at': '2026-10-22T00:49:00Z'}],
             'attempts': [{'provider': 'Polymarket', 'status': 'resolved',
                           'url': 'https://gamma-api.polymarket.com/events'}],
             'reason': None, 'expires_at': None},
            # 2. Originated model line, no market.
            {'id': '2', 'teams': ['Charlie', 'Delta'], 'team_ids': ['c', 'd'],
             'competition': 'Test Cup', 'tier': 'c', 'best_of': 3,
             'start': '2026-10-24T10:00:00Z', 'lock': '2026-10-24T09:54:00Z',
             'source_status': 'scheduled', 'state': 'open',
             'source_url': 'https://www.hotspawn.com/matches/charlie-vs-delta-test-cup-2',
             'feed_url': 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1',
             'flags': [], 'probabilities': [0.55, 0.45], 'fair_odds': [1.8182, 2.2222],
             'pick': 'Charlie', 'method': 'model_vrs',
             'evidence': [{
                 'provider': 'Valve VRS model', 'id': 'vrs-1',
                 'url': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/abc/live/2026/standings_global_2026_10_05.md',
                 'api_url': 'https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/abc/live/2026/standings_global_2026_10_05.md',
                 'observed_at': '2026-10-22T00:50:00Z', 'updated_at': None,
                 'standings_as_of': '2026-10-05', 'standings_origin': 'test fixture, not a live read',
                 'standings_commit': 'abc', 'standings_file': 'standings_global_2026_10_05.md',
                 'fixture_teams': ['Charlie', 'Delta'], 'vrs_teams': ['Charlie', 'Delta'],
                 'standings': [10, 20], 'points': [1500, 1400],
                 'rosters': [['p1', 'p2', 'p3', 'p4', 'p5'], ['p6', 'p7', 'p8', 'p9', 'p10']],
                 'roster_checks': [{'note': 'unique label', 'overlap': None},
                                   {'note': 'unique label', 'overlap': None}],
                 'details_urls': [
                     'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/abc/live/2026/details/charlie.md',
                     'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/abc/live/2026/details/delta.md'],
                 'raw_expected': [0.5597, 0.4403], 'calibration_slope': 0.7986,
                 'probabilities': [0.55, 0.45],
                 'formula_source': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/model/fit.js',
                 'calibration_source': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/modelfit.png'}],
             'attempts': [{'provider': 'Polymarket', 'status': 'unresolved',
                           'url': 'https://gamma-api.polymarket.com/events'},
                          {'provider': 'Valve VRS model', 'status': 'resolved',
                           'url': 'https://github.com/ValveSoftware/counter-strike_regional_standings'}],
             'reason': 'Originated line: Valve VRS model estimate, not a market price.',
             'expires_at': None},
            # 3. Research pick, one-sided Valve standing, no percentage.
            {'id': '3', 'teams': ['Echo', 'Foxtrot'], 'team_ids': ['e', 'f'],
             'competition': 'Test Cup', 'tier': 'c', 'best_of': None,
             'start': '2026-10-25T10:00:00Z', 'lock': '2026-10-25T09:54:00Z',
             'source_status': 'scheduled', 'state': 'open',
             'source_url': 'https://www.hotspawn.com/matches/echo-vs-foxtrot-test-cup-3',
             'feed_url': 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1',
             'flags': ['Research pick on one-sided Valve standings evidence.'],
             'probabilities': None, 'fair_odds': None, 'pick': 'Echo',
             # Synthetic source observation: required by the finite research TTL.
             # This is test-only metadata, never a published official value.
             'vrs_research': {'observed_at': '2026-10-22T00:50:00Z'},
             'method': 'research_vrs_single', 'evidence': [],
             'attempts': [{'provider': 'HLTV', 'status': 'unresolved',
                           'url': 'https://www.hltv.org/matches'}],
             'reason': 'No verified market line. Research pick only: Echo is listed in the official standings while Foxtrot is absent.',
             'expires_at': None},
            # 4. Nothing at all: the blank must stay blank and be explained.
            {'id': '4', 'teams': ['Golf', 'Hotel'], 'team_ids': ['g', 'h'],
             'competition': 'Test Cup', 'tier': 'c', 'best_of': None,
             'start': '2026-10-26T10:00:00Z', 'lock': '2026-10-26T09:54:00Z',
             'source_status': 'scheduled', 'state': 'open',
             'source_url': 'https://www.hotspawn.com/matches/golf-vs-hotel-test-cup-4',
             'feed_url': 'https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1',
             'flags': [], 'probabilities': None, 'fair_odds': None, 'pick': None,
             'method': None, 'evidence': [],
             'attempts': [{'provider': 'GG.BET', 'status': 'error',
                           'url': 'https://gg.bet/en/esports/counter-strike'}],
             'reason': 'No verified market line; the bookmaker refused access.',
             'expires_at': None},
        ],
    }


def built(snap=None):
    snap = snap or snapshot()
    before = {m['id']: dict(m) for m in snap['matches']}
    out = ROOT / 'runtime' / 'session-5f1df842-test-build'
    # The build stamps built_at and expiry; run it on a fixed clock so the test
    # is deterministic and no row can expire because the wall clock moved.
    build.build(json.loads(json.dumps(snap)), out,
                now=build.dt('2026-10-22T01:00:00Z'))
    data = json.loads((out / 'data' / 'latest.json').read_text())
    return data, {name: BeautifulSoup((out / (name + '.html')).read_text(), 'html.parser')
                  for name in ('index', 'picks', 'unresolved')}, before


class CountTests(unittest.TestCase):
    """The counts must describe the rows, not a hand-written total."""

    @classmethod
    def setUpClass(cls):
        cls.data, cls.pages, cls.before = built()

    def test_counts_match_the_rows_independently(self):
        rows = [m for m in self.data['matches'] if m['state'] == 'open']
        c = summary.counts(self.data['matches'])
        self.assertEqual(c['open'], 4)
        self.assertEqual(c['priced'], len([m for m in rows if m.get('probabilities') is not None]))
        self.assertEqual(c['with_pick'], len([m for m in rows if m.get('pick')]))
        self.assertEqual(c['market'], 1)
        self.assertEqual(c['model'], 1)
        self.assertEqual(c['research'], 1)
        self.assertEqual(c['no_pick'], 1)
        self.assertEqual(c['without_percentage'], 2)
        self.assertEqual(c['percent'], 50)

    def test_origin_labels_every_published_method(self):
        kinds = {m['method']: summary.origin(m)[0] for m in self.data['matches'] if m.get('method')}
        self.assertEqual(kinds['exchange'], 'market')
        self.assertEqual(kinds['model_vrs'], 'model')
        self.assertEqual(kinds['research_vrs_single'], 'research')

    def test_unknown_method_is_not_silently_priced(self):
        kind, label, _basis = summary.origin({'method': 'brand_new_tier', 'probabilities': [0.5, 0.5]})
        self.assertEqual(kind, 'unknown')
        self.assertIn('Unclassified', label)

    def test_an_empty_board_is_described_as_empty_not_complete(self):
        c = summary.counts([])
        self.assertEqual(c['open'], 0)
        self.assertEqual(summary.completeness_sentence(c), 'No open CS2 fixture at the last check.')


class NoInventedNumberTests(unittest.TestCase):
    """A blank stays blank; a research pick is never published as a probability."""

    @classmethod
    def setUpClass(cls):
        cls.data, cls.pages, cls.before = built()

    def test_unpriced_rows_keep_no_number_through_the_build(self):
        for row in self.data['matches']:
            if row['id'] in ('3', '4'):
                self.assertIsNone(row['probabilities'], row['id'])
                self.assertIsNone(row['fair_odds'], row['id'])
                self.assertNotIn('probabilities', json.dumps(row.get('evidence') or []))

    def test_research_row_keeps_its_pick_and_has_no_percentage_on_the_page(self):
        html = str(self.pages['index'])
        section = self.pages['index'].select_one('#unresolved-picks')
        self.assertIsNotNone(section)
        text = section.get_text(' ', strip=True)
        self.assertIn('Echo', text)
        self.assertIn('no %', text)
        self.assertNotRegex(text, r'Echo\s+\d+\.\d\s?%')
        self.assertIn('Blank means unverified', html)

    def test_blank_row_is_listed_with_its_own_reason(self):
        section = self.pages['index'].select_one('#unresolved-picks')
        text = section.get_text(' ', strip=True)
        self.assertIn('Golf', text)
        self.assertIn('No supported pick', text)
        self.assertIn('refused access', text)

    def test_no_default_fifty_fifty_anywhere(self):
        for page in self.pages.values():
            body = page.get_text(' ', strip=True)
            self.assertNotIn('50/50 default', body)
            self.assertNotIn('assumed 50', body)


class ExecutiveSummaryTests(unittest.TestCase):
    """The summary has to answer the question and link to the answer."""

    @classmethod
    def setUpClass(cls):
        cls.data, cls.pages, cls.before = built()
        cls.index = cls.pages['index']

    def test_coverage_block_sits_before_the_hero(self):
        html = str(self.pages['index'])
        self.assertIn('id="coverage-now"', html)
        self.assertIn('id="unresolved-picks"', html)
        self.assertLess(html.find('id="freshness-strip"'), html.find('id="coverage-now"'))
        self.assertLess(html.find('id="coverage-now"'), html.find('class="hero"'))
        self.assertLess(html.find('id="picks-at-a-glance"'), html.find('id="unresolved-picks"'))

    def test_coverage_block_states_the_numbers_and_the_links(self):
        block = self.index.select_one('#coverage-now')
        text = block.get_text(' ', strip=True)
        self.assertIn('4 open CS2 matches', text)
        self.assertIn('3 picks', text)
        self.assertIn('2 with a win probability', text)
        hrefs = {a['href'] for a in block.select('a[href]')}
        self.assertIn('picks.html', hrefs)
        self.assertIn('#unresolved-picks', hrefs)
        self.assertIn('#picks-at-a-glance', hrefs)
        self.assertIn('matches.html', hrefs)
        self.assertIn('sources.html#method', hrefs)

    def test_unresolved_section_is_inside_the_summary_and_complete(self):
        section = self.index.select_one('#unresolved-picks')
        rows = section.select('a.unresolved-row')
        expected = [m['id'] for m in self.data['matches']
                    if m['state'] == 'open' and m['probabilities'] is None]
        self.assertEqual([a['href'].split('match-')[-1] for a in rows], expected)
        for row in rows:
            text = row.get_text(' ', strip=True)
            self.assertTrue(re.search(r'\d{1,2} \w{3}', text), text)  # a dated start
            self.assertTrue(row['href'].startswith('evidence.html#match-'))

    def test_every_unresolved_row_links_an_official_source(self):
        section = self.index.select_one('#unresolved-picks')
        for item in section.select('li.unresolved-item'):
            hrefs = [a['href'] for a in item.select('a[href]')]
            official = [h for h in hrefs if any(host in h for host in (
                'https://www.hotspawn.com/', 'https://play.hotspawn.com/',
                'https://www.hltv.org/', 'https://github.com/ValveSoftware/'))]
            self.assertTrue(official, hrefs)
            # and the row is explained in prose, not left as an unexplained blank
            self.assertTrue(item.select_one('.unresolved-why'))

    def test_ladder_is_ordered_and_every_step_has_an_official_source(self):
        section = self.index.select_one('#unresolved-picks')
        steps = section.select('ol.ladder > li')
        self.assertEqual(len(steps), len(summary.LADDER))
        titles = [li.find('strong').get_text(' ', strip=True) for li in steps]
        for i, title in enumerate(titles):
            self.assertTrue(title.startswith('%d.' % (i + 1)), title)
        allowed = ('https://gamma-api.polymarket.com', 'https://www.hltv.org',
                   'https://guest.api.arcadia.pinnacle.com', 'https://egamersworld.com',
                   'https://github.com/ValveSoftware/counter-strike_regional_standings')
        for li in steps:
            hrefs = [a['href'] for a in li.select('a[href]')]
            self.assertTrue(any(h.startswith(allowed) for h in hrefs), hrefs)

    def test_ladder_matches_the_publication_order_in_refresh(self):
        """The summary must not describe a tier order the collector does not use."""
        source = (ROOT / 'scripts' / 'refresh.py').read_text()
        order = [marker for marker in ('Polymarket events page', 'from scripts.hltv import research',
                                       'Pinnacle esports moneylines', 'relax=True',
                                       'book_research_pick', 'vrs.apply', 'research_rank_pick')
                 if marker in source]
        self.assertEqual(order, ['Polymarket events page', 'from scripts.hltv import research',
                                 'Pinnacle esports moneylines', 'relax=True',
                                 'book_research_pick', 'vrs.apply', 'research_rank_pick'])
        self.assertEqual([step[0] for step in summary.LADDER],
                         ['exchange', 'hltv', 'pinnacle', 'exchange_wide', 'book', 'model_vrs', 'research'])

    def test_ladder_sources_are_the_ones_the_collector_reads(self):
        from scripts import core
        self.assertEqual(summary.LADDER[0][4], core.GAMMA + '/events')
        self.assertEqual(summary.LADDER[2][4], core.PIN + '/sports/12/markets/straight')

    def test_unresolved_page_carries_the_same_completeness_answer(self):
        page = self.pages['unresolved']
        intro = page.select_one('#unresolved-overview')
        self.assertIsNotNone(intro)
        text = intro.get_text(' ', strip=True)
        self.assertIn('4 open matches', text)
        self.assertIn('3 with a pick', text)
        self.assertEqual(len(intro.select('ol.ladder > li')), len(summary.LADDER))

    def test_picks_page_still_links_the_unresolved_rows(self):
        hrefs = {a['href'] for a in self.pages['picks'].select('a[href]')}
        self.assertIn('unresolved.html', hrefs)


class PhoneLayoutTests(unittest.TestCase):
    """CSS rules that decide whether a phone can read the new sections."""

    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / 'assets' / 'style.css').read_text()

    def test_unresolved_rows_do_not_reuse_the_phone_hidden_class(self):
        html = str(built()[1]['index'])
        segment = html[html.find('id="unresolved-picks"'):]
        self.assertNotIn('glance-row', segment[:4000])
        # the rule that hides .glance-row on phones must still exist, so the
        # assertion above is about our markup rather than a dead stylesheet
        self.assertIn('.glance-row{display:none!important}', self.css.replace(' ', ''))

    def test_unresolved_rows_have_their_own_mobile_layout(self):
        self.assertIn('.unresolved-row{', self.css)
        mobile = self.css[self.css.find('@media(max-width:650px){', self.css.find('.unresolved-row{')):]
        self.assertIn('.unresolved-row{grid-template-columns:1fr', mobile)

    def test_light_panel_secondary_button_is_readable(self):
        self.assertIn('.panel .button.secondary', self.css)
        rule = self.css[self.css.find('.panel .button.secondary'):]
        self.assertIn('background:white', rule[:200])
        self.assertIn('color:#255d3b', rule[:200])

    def test_the_site_stylesheet_is_the_one_that_ships(self):
        shipped = (ROOT / 'site' / 'assets' / 'style.css').read_text()
        self.assertEqual(shipped, self.css,
                         'site/assets/style.css is what the build copies; keep it identical to assets/style.css')


class NavigationTests(unittest.TestCase):
    def test_mobile_tab_label_is_readable_without_an_acronym(self):
        labels = [label for _slug, label in build.MOBILE_NAV]
        self.assertEqual(labels, ['Home', 'Picks', 'Unresolved', 'Matches', 'Analysis'])
        self.assertEqual(len(labels), 5)


class SourceRetryTests(unittest.TestCase):
    """A transient non-JSON body must not cost a publication slot (measured 22 Oct).

    At 01:22:32Z the publication runner received a non-JSON body from the fixtures
    API and two lobby pages without their hydration block, seven minutes after the
    same URLs answered 97 fixtures, so the refresh fell back to a four-hour-old
    inventory. These tests pin the fix: one bounded re-read, and a persistent
    failure still blocks.
    """

    def test_json_source_is_re_read_once_then_succeeds(self):
        from scripts import refresh as refresh_module

        class Response:
            def __init__(self, body):
                self.content = body
                self.headers = {}
                self.status_code = 200
                self.text = body.decode()

            def raise_for_status(self):
                return None

            def json(self):
                return json.loads(self.content)

        class Session:
            def __init__(self):
                self.headers = {}
                self.calls = 0

            def get(self, url, timeout=None, headers=None):
                self.calls += 1
                if self.calls == 1:
                    return Response(b'<html>challenge page</html>')
                return Response(b'[{"id":"1","sport_alias":"cs2"}]')

        src = refresh_module.Sources(build.dt('2026-10-22T01:00:00Z'))
        src.session = Session()
        src.json_retry_waits = (0.0,)
        body, record = src.get('Hotspawn CS2 fixtures', 'https://example.test/api', True)
        self.assertEqual(body, [{'id': '1', 'sport_alias': 'cs2'}])
        self.assertEqual(src.session.calls, 2)
        self.assertEqual(record['status'], 'ok')

    def test_persistent_non_json_still_fails_closed(self):
        from scripts import refresh as refresh_module

        class Response:
            content = b'<html>challenge page</html>'
            headers = {}
            status_code = 200
            text = '<html>challenge page</html>'

            def raise_for_status(self):
                return None

            def json(self):
                return json.loads(self.content)

        class Session:
            def __init__(self):
                self.headers = {}
                self.calls = 0

            def get(self, url, timeout=None, headers=None):
                self.calls += 1
                return Response()

        src = refresh_module.Sources(build.dt('2026-10-22T01:00:00Z'))
        src.session = Session()
        src.json_retry_waits = (0.0, 0.0)
        with self.assertRaises(ValueError):
            src.get('Hotspawn CS2 fixtures', 'https://example.test/api', True)
        self.assertEqual(src.session.calls, 3)

    def test_a_real_reader_opts_into_a_whole_discovery_retry(self):
        from scripts import refresh as refresh_module
        from scripts import inventory
        src = refresh_module.Sources(build.dt('2026-10-22T01:00:00Z'))
        self.assertEqual(src.discovery_retry_waits, inventory.DISCOVERY_RETRY_WAITS)

    def test_discovery_stays_single_pass_for_a_stub_reader(self):
        """Inventory tests use stub readers; they must not sleep or re-read."""
        from scripts import inventory

        class Reader:
            def __init__(self):
                self.calls = []
                self.log = []

            def get(self, name, url, as_json):
                self.calls.append(url)
                raise ValueError('refused')

        reader = Reader()
        previous = {'matches': [], 'generated_at': '2026-10-22T00:00:00Z'}
        result = inventory.discover(reader, build.dt('2026-10-22T01:00:00Z'), previous)
        self.assertEqual(len(reader.calls), 3)
        self.assertEqual(result['retained']['coverage'], 'stale')


class RealSnapshotTests(unittest.TestCase):
    """The published snapshot in this repository must satisfy the same rules."""

    def test_published_snapshot_counts_are_consistent(self):
        data = json.loads((ROOT / 'data' / 'latest.json').read_text())
        c = summary.counts(data['matches'])
        self.assertEqual(c['open'], len([m for m in data['matches'] if m['state'] == 'open']))
        self.assertEqual(c['priced'] + c['without_percentage'], c['open'])
        self.assertEqual(c['market'] + c['model'] + c['research'] + c['no_pick'],
                         c['open'])
        self.assertLessEqual(c['market'] + c['model'], c['priced'])


if __name__ == '__main__':
    unittest.main()
