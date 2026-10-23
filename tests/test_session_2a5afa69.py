"""Session 2a5afa69 — row-by-row board audit, no network, no invented values.

These tests pin the two things the auditor is allowed to say about a row:

* a published percentage must be reproducible from that row's own retained
  evidence (exchange price pair, bookmaker decimal odds, or Valve points
  through Valve's published formula), otherwise the row fails the audit;
* a row without a pick must be published by name together with every source
  that was tried, and the auditor must never fill the blank in.

They also prove the audit is read-only: the snapshot passed in is unchanged.
"""
import copy
import json
import pathlib
import unittest
from datetime import datetime, timedelta, timezone

from scripts import audit_board_2a5afa69 as audit_mod
from scripts import vrs
from scripts.audit_board_2a5afa69 import audit, markdown, reproduce

NOW = datetime(2026, 10, 23, 5, 0, tzinfo=timezone.utc)
OBSERVED = '2026-10-23T04:55:00Z'


def exchange_row(probs=(0.6, 0.4), mid='900001', pick='Alpha', **over):
    row = {
        'id': mid, 'teams': ['Alpha', 'Bravo'], 'start': '2026-10-23T12:00:00Z',
        'competition': 'CCT Europe 2026 Series #1', 'tier': 'b', 'state': 'open',
        'source_url': 'https://www.hotspawn.com/matches/alpha-vs-bravo-900001',
        'pick': pick, 'method': 'exchange', 'probabilities': list(probs),
        'evidence': [{'provider': 'Polymarket', 'url': 'https://polymarket.com/event/x',
                      'api_url': 'https://gamma-api.polymarket.com/markets/1',
                      'observed_at': OBSERVED, 'updated_at': OBSERVED,
                      'probabilities': [0.6, 0.4], 'spread': 0.02, 'liquidity': 5000.0}],
        'attempts': [{'provider': 'Polymarket', 'status': 'resolved', 'url': 'https://gamma-api.polymarket.com/markets/1',
                      'reason': 'Exact pair and UTC start; two-way series winner validated.'}],
        'reason': None, 'expires_at': '2026-10-23T11:54:00Z',
    }
    row.update(over)
    return row


def model_row(mid='900002'):
    points = [1500.0, 1200.0]
    p0 = vrs.calibrated(vrs.expected(points[0], points[1]))
    return {
        'id': mid, 'teams': ['Charlie', 'Delta'], 'start': '2026-10-24T12:00:00Z',
        'competition': 'DACH CS Masters Season 5', 'tier': 'c', 'state': 'open',
        'source_url': 'https://www.hotspawn.com/matches/charlie-vs-delta-900002',
        'pick': 'Charlie', 'method': 'model_vrs', 'probabilities': [p0, 1 - p0],
        'evidence': [{'provider': 'Valve VRS model', 'url': 'https://github.com/ValveSoftware/x',
                      'api_url': 'https://raw.githubusercontent.com/ValveSoftware/x',
                      'observed_at': OBSERVED, 'points': points, 'probabilities': [p0, 1 - p0]}],
        'attempts': [], 'reason': None, 'expires_at': '2026-10-24T11:54:00Z',
    }


def open_snapshot(rows):
    return {'generated_at': '2026-10-23T04:56:00Z', 'fixtures_observed_at': OBSERVED,
            'built_at': '2026-10-23T04:57:00Z', 'matches': rows}


class ReproductionRules(unittest.TestCase):
    def test_exchange_row_reproduces_and_tampered_pair_does_not(self):
        ok, why = reproduce(exchange_row(), NOW)
        self.assertTrue(ok, why)
        bad, why = reproduce(exchange_row(probs=(0.7, 0.3)), NOW)
        self.assertFalse(bad)
        self.assertIn('normalised exchange price', why)

    def test_exchange_row_without_spread_or_liquidity_record_fails(self):
        row = exchange_row()
        row['evidence'][0].pop('spread')
        ok, why = reproduce(row, NOW)
        self.assertFalse(ok)
        self.assertIn('spread or liquidity', why)

    def test_bookmaker_decimal_odds_are_de_vigged(self):
        row = exchange_row(probs=(0.5, 0.5), mid='900003')
        row['method'] = 'bookmaker_fallback'
        row['evidence'][0] = {'provider': 'Winline', 'url': 'https://stavka.tv/x',
                              'observed_at': OBSERVED, 'decimal_odds': [1.90, 1.90]}
        ok, why = reproduce(row, NOW)
        self.assertTrue(ok, why)
        row['probabilities'] = [0.6, 0.4]
        self.assertFalse(reproduce(row, NOW)[0])

    def test_model_row_is_recomputed_from_valve_points(self):
        row = model_row()
        ok, why = reproduce(row, NOW)
        self.assertTrue(ok, why)
        self.assertIn('Valve points', why)
        row['probabilities'] = [0.9, 0.1]
        self.assertFalse(reproduce(row, NOW)[0])

    def test_stale_evidence_and_research_percentages_fail(self):
        row = exchange_row()
        row['evidence'][0]['observed_at'] = '2026-10-23T01:00:00Z'  # 4h old at NOW? still inside 8h
        self.assertTrue(reproduce(row, NOW)[0])
        row['evidence'][0]['observed_at'] = '2026-10-22T18:00:00Z'  # 11h old
        self.assertFalse(reproduce(row, NOW)[0])
        research = exchange_row(mid='900004', method='research_rank_single')
        self.assertFalse(reproduce(research, NOW)[0])
        self.assertIn('research tier', reproduce(research, NOW)[1])

    def test_pick_must_name_a_fixture_team(self):
        report = audit(open_snapshot([exchange_row(pick='Echo')]), NOW)
        self.assertFalse(report['rows'][0]['pick_is_a_team'])


class UnpickedRowsArePublishedNotFilledIn(unittest.TestCase):
    def row_without_pick(self):
        return {
            'id': '900005', 'teams': ['Echo', 'Foxtrot'], 'start': '2026-10-25T09:00:00Z',
            'competition': 'Thunderpick World Championship 2026: South American Series #1',
            'tier': 'c', 'state': 'open', 'pick': None, 'method': None, 'probabilities': None,
            'source_url': 'https://www.hotspawn.com/matches/echo-vs-foxtrot-900005',
            'attempts': [
                {'provider': 'HLTV', 'status': 'unresolved', 'url': 'https://www.hltv.org/matches',
                 'reason': 'No unique exact team-pair and UTC-start match; renamed teams are not inferred.'},
                {'provider': 'Pinnacle', 'status': 'unresolved',
                 'url': 'https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/straight',
                 'reason': 'No exact team-pair and UTC-start match in retrieved feed.'},
                {'provider': 'EGamersWorld', 'status': 'error', 'url': 'https://egamersworld.com/counterstrike/match/x',
                 'reason': 'HTTP 403 persisted; host blocked for this run.'},
            ],
            'reason': 'No verified market line and no usable HLTV ranking evidence.',
            'expires_at': None,
        }

    def test_audit_keeps_the_row_blank_and_lists_every_attempt(self):
        snapshot = open_snapshot([exchange_row(), self.row_without_pick()])
        report = audit(snapshot, NOW)
        self.assertEqual(report['rows_without_pick'], ['900005'])
        self.assertEqual(report['rows_with_pick'], 1)
        out = markdown(report)
        self.assertIn('900005 — Echo vs Foxtrot', out)
        for provider in ('HLTV', 'Pinnacle', 'EGamersWorld'):
            self.assertIn(provider, out)
        self.assertIn('HTTP 403', out)
        # The blank row is not given a percentage or a pick anywhere.
        row = next(r for r in report['rows'] if r['id'] == '900005')
        self.assertIsNone(row['probabilities'])
        self.assertIsNone(row['pick'])

    def test_every_open_row_appears_and_closed_rows_are_skipped(self):
        closed = exchange_row(mid='900006', state='not_open')
        report = audit(open_snapshot([exchange_row(), self.row_without_pick(), closed]), NOW)
        self.assertEqual([r['id'] for r in report['rows']], ['900001', '900005'])
        self.assertEqual(report['rows_open'], 2)

    def test_audit_is_read_only(self):
        snapshot = open_snapshot([exchange_row(), self.row_without_pick()])
        before = copy.deepcopy(snapshot)
        audit(snapshot, NOW)
        self.assertEqual(snapshot, before)


class RealCommittedBoard(unittest.TestCase):
    """The committed board must pass the same row-by-row auditor."""

    def test_committed_snapshot_reproduces_or_reports_the_gap(self):
        data = json.loads(pathlib.Path('data/latest.json').read_text())
        report = audit(data)
        opens = [m for m in data['matches'] if m['state'] == 'open']
        self.assertEqual(report['rows_open'], len(opens))
        self.assertEqual(report['rows_failing_reproduction'], [])
        # A pick, when present, always names a fixture team.
        self.assertTrue(all(r['pick_is_a_team'] for r in report['rows'] if r['pick']))
        # Every open row is either priced or explicitly research-only/unresolved.
        for r in report['rows']:
            if r['probabilities'] is not None:
                self.assertIn(r['method'], audit_mod.MARKET + audit_mod.MODEL, r['id'])
            elif r['pick']:
                self.assertTrue(str(r['method']).startswith('research_'), r['id'])
            else:
                self.assertTrue(r['attempts'], r['id'])


if __name__ == '__main__':
    unittest.main()


class ExecutiveSummaryMobileOrder(unittest.TestCase):
    """Picks first, guide second — proven from the rendered index, not a mock.

    Session 2a5afa69: the previous order put the site guide, the coverage block
    and the hero between a phone and the first pick, so the list began ~1,600px
    down. These assertions lock the new order and keep every section reachable.
    """

    @classmethod
    def setUpClass(cls):
        from bs4 import BeautifulSoup
        from scripts import build
        cls.data = json.loads(pathlib.Path('data/latest.json').read_text())
        cls.html = build.overview(copy.deepcopy(cls.data))
        cls.soup = BeautifulSoup(cls.html, 'html.parser')
        cls.opens = [m for m in cls.data['matches'] if m['state'] == 'open']

    def pos(self, needle):
        return self.html.find(needle)

    def test_fresh_strip_comes_before_anything_else(self):
        self.assertLess(self.pos('id="freshness-strip"'), self.pos('id="picks-at-a-glance"'))
        self.assertLess(self.pos('id="freshness-strip"'), self.pos('id="exec-banner"'))

    def test_picks_come_before_the_unresolved_section_and_the_details(self):
        # The descriptive guide (banner, jump nav, coverage block, hero and
        # start-here cards) sits above the list inside one folded <details>, so
        # it costs a single ~50px line on a phone. The pick list itself must
        # precede the separate unresolved section and the long detail tables.
        self.assertLess(self.pos('id="picks-at-a-glance"'), self.pos('id="unresolved-picks"'))
        self.assertLess(self.pos('id="picks-at-a-glance"'), self.pos('id="detailed-summary"'))
        guide = self.soup.select_one('#exec-banner').find_parent('details')
        self.assertIsNotNone(guide)
        self.assertIsNone(guide.get('open'), 'the guide must be folded by default')
        # The hero lives inside that folded guide, not in front of the picks.
        hero = self.soup.select_one('.hero')
        self.assertIsNotNone(hero)
        self.assertIsNotNone(hero.find_parent('details'))

    def test_fresh_strip_leads_with_counts_then_the_pick_cta(self):
        strip = self.soup.select_one('#freshness-strip')
        text = strip.get_text(' ', strip=True)
        self.assertLess(text.find('open CS2 match'), text.find('Last checked'))
        links = [a['href'] for a in strip.select('a')]
        self.assertEqual(links[0], 'picks.html')
        self.assertGreaterEqual(len(strip.select('[data-count]')), 4)

    def test_guide_remains_folded_and_keeps_its_anchors(self):
        for anchor in ('exec-banner', 'start-here'):
            node = self.soup.select_one('#' + anchor)
            self.assertIsNotNone(node, anchor)
            self.assertIsNotNone(node.find_parent('details'), anchor)

    def test_every_open_pick_is_listed_with_a_percentage_or_an_explicit_blank(self):
        section = self.soup.select_one('#picks-at-a-glance')
        rows = section.select('a.glance-row')
        self.assertEqual(len(rows), len(self.opens))
        for m in self.opens:
            row = next(a for a in rows if a['href'].endswith('match-' + m['id']))
            text = row.get_text(' ', strip=True)
            if m['probabilities'] is not None:
                self.assertRegex(text, r'\d+\.\d%')
            else:
                self.assertNotRegex(text, r'50/50')
                self.assertIn('no percentage' if m.get('pick') else 'No pick yet', text)

    def test_unresolved_pointer_is_inside_the_pick_list_and_counted(self):
        section = self.soup.select_one('#picks-at-a-glance')
        note = section.select_one('.glance-note')
        self.assertIsNotNone(note)
        missing = [m for m in self.opens if m['probabilities'] is None]
        text = note.get_text(' ', strip=True)
        if missing:
            self.assertIn(note.select_one('a')['href'], ('#unresolved-picks', 'unresolved.html'))
            self.assertIn('no percentage' if any(m.get('pick') for m in missing) else 'no supported pick', text)
        else:
            # A fully priced board says so; there is nothing to jump to and no
            # link is fabricated to fill the space.
            self.assertIn('Every open match is priced or has a sourced research pick', text)
            self.assertIsNone(note.select_one('a'))

    def test_unresolved_section_still_carries_every_blank_row_and_the_ladder(self):
        section = self.soup.select_one('#unresolved-picks')
        self.assertIsNotNone(section)
        self.assertLess(self.pos('id="picks-at-a-glance"'), self.pos('id="unresolved-picks"'))
        expected = sorted(m['id'] for m in self.opens if m['probabilities'] is None)
        listed = sorted(a['href'].split('match-')[-1] for a in section.select('a.unresolved-row'))
        self.assertEqual(listed, expected)
        self.assertIn('What is tried, in order, before a blank is published',
                      section.get_text(' ', strip=True))
        for provider in ('HLTV', 'Polymarket', 'Pinnacle'):
            self.assertIn(provider, section.get_text(' ', strip=True))


class ExecutiveSummaryPhoneSizes(unittest.TestCase):
    """320px is the narrowest phone we promise; nothing may be clipped."""

    def test_no_row_depends_on_horizontal_scroll(self):
        css = pathlib.Path('site/assets/style.css').read_text()
        self.assertIn('.glance-card-mobile', css)
        self.assertIn('@media(max-width:650px)', css)
        # The card layout replaces the desktop grid on phones.
        self.assertRegex(css, r'@media\(max-width:650px\)[^}]*glance-row\{grid-template-columns:1fr')
