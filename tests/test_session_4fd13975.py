"""Session 4fd13975 — regression tests for the research deliverables.

Two user requirements are locked down here, together with the evidence rules
that keep them honest:

1. Every match on the board carries a pick, and the rows that publish no win
   probability are grouped in their own section with the limitation and its
   source links, linked directly from the executive summary.
2. The executive summary links to the updated pick list and everything is
   readable and reachable on a phone (viewport, bottom navigation, per-row
   cards with an unmissable pick and explicit probability text).
3. The new watch path (scripts/books.watch) lets the scheduled refresh
   re-read listing pages that were rejected earlier and promotes a receipt
   only when the live page re-confirms the exact fixture pair, the exact UTC
   start and an asymmetric two-way pair bound to both labels. Placeholders,
   mismatches and access failures stay refusals; data/book-receipts.json is
   never modified by the watch.
"""
from __future__ import annotations

import json
import re
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts import books
from scripts.core import book_research_pick

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 22, 9, 0, tzinfo=timezone.utc)

FIXTURE_START = '2026-10-27T03:00:00Z'


def fixture(**over):
    base = {
        'id': '1082860',
        'teams': ['FlyQuest', 'Staqued'],
        'state': 'open',
        'start': FIXTURE_START,
        'lock': '2026-10-27T02:54:00Z',
        'competition': 'DFRAG Invitational 2026',
        'source_url': 'https://www.hotspawn.com/matches/flyquest-vs-staqued-dfrag-invitational-2026-1082860',
        'best_of': 3,
        'pick': 'FlyQuest',
        'method': 'research_rank_single',
        'probabilities': None,
        'fair_odds': None,
        'evidence': [],
        'attempts': [],
        'flags': [],
    }
    base.update(over)
    return base


def egw_page(team1='FlyQuest', team2='Staqued', start='2026-10-27T03:00:00.000Z',
             odds1='1.72', odds2='2.10', second_label='Staqued'):
    """HTML in the shape scripts.books.parse_listing reads: JSON-LD name pair
    and startDate near each other, then the odds widget
    ``team1 od1 Make a bet od2 team2``."""
    return (
        '<html><body><script type="application/ld+json">'
        '{"name":"%s VS %s","description":"x","startDate":"%s"}'
        '</script><div class="odds"><span>%s</span> %s Make a bet %s <span>%s</span></div>'
        '</body></html>' % (team1, team2, start, team1, odds1, odds2, second_label)
    )


class FakeSources:
    """Serves canned HTML per URL; records every read."""

    def __init__(self, pages):
        self.pages = dict(pages)
        self.reads = []

    def get(self, name, url, as_json=True, headers=None):
        self.reads.append(url)
        if url not in self.pages:
            raise ValueError('HTTP 404 for ' + url)
        return self.pages[url], {'observed_at': NOW.isoformat().replace('+00:00', 'Z'),
                                 'sha256': 'f' * 64, 'http_status': 200, 'url': url}


class TestListingGapRecheck(unittest.TestCase):
    """The gap-recheck watch (scripts.books.watch_unpriced, landed on main from
    the sibling session that implemented it in parallel) must keep these
    guarantees. Session 4fd13975 implemented the same feature independently;
    on rebase the sibling implementation was kept verbatim and these tests were
    rewritten against it so the user-facing rules stay locked down either way:
    a previously rejected listing page is re-read for an open unpriced fixture
    and a receipt is accepted only when the live page states the exact fixture
    team pair and the exact fixture UTC start with an asymmetric two-way pair
    bound to both labels — and nothing else ever becomes a number."""

    URL = 'https://egamersworld.com/counterstrike/match/test/test-page'

    def setUp(self):
        self.row = fixture(best_of=None)
        self.rejected = [{
            'fixture_id': '1082860',
            'teams': ['FlyQuest', 'Staqued'],
            'url': self.URL,
            'observed_at': '2026-10-22T07:52:00Z',
            'displayed': [1.8, 1.8],
            'reason': 'placeholder',
        }]

    def watch(self, pages, row=None):
        src = FakeSources(pages)
        receipts, records = books.watch_unpriced(
            [], [row or self.row], src, NOW, register=self.rejected)
        return receipts, records, src

    def test_promotes_only_verified_live_pair(self):
        receipts, records, _src = self.watch({self.URL: egw_page()})
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0]['odds'], [1.72, 2.10])
        self.assertEqual(records[0]['status'], 'resolved')
        # Identity comes from the fixture row + the live reading, never from
        # the stale rejected entry's copied fields.
        self.assertEqual(receipts[0]['start'], FIXTURE_START)
        self.assertEqual(receipts[0]['fixture_id'], '1082860')

    def test_placeholder_stays_refused(self):
        receipts, records, _src = self.watch({self.URL: egw_page(odds1='1.8', odds2='1.8')})
        self.assertEqual(receipts, [])
        self.assertEqual(records[0]['status'], 'unresolved')

    def test_start_mismatch_stays_refused(self):
        receipts, records, _src = self.watch(
            {self.URL: egw_page(start='2026-10-28T03:00:00.000Z')})
        self.assertEqual(receipts, [])
        self.assertEqual(records[0]['status'], 'unresolved')

    def test_team_mismatch_stays_refused(self):
        receipts, records, _src = self.watch(
            {self.URL: egw_page(team1='SomeOtherClub', second_label='Staqued')})
        self.assertEqual(receipts, [])
        self.assertEqual(records[0]['status'], 'unresolved')

    def test_rejected_entry_with_foreign_teams_is_never_read(self):
        bad = [dict(self.rejected[0], teams=['Someone', 'Else'])]
        src = FakeSources({self.URL: egw_page()})
        receipts, records = books.watch_unpriced(
            [], [self.row], src, NOW, register=bad)
        self.assertEqual(receipts, [])
        self.assertEqual(records, [])
        self.assertEqual(src.reads, [])

    def test_non_listing_urls_are_never_read(self):
        bad = [dict(self.rejected[0], url='https://evil.example.com/x')]
        src = FakeSources({'https://evil.example.com/x': egw_page()})
        receipts, records = books.watch_unpriced(
            [], [self.row], src, NOW, register=bad)
        self.assertEqual(receipts, [])
        self.assertEqual(src.reads, [])

    def test_access_failure_is_data_never_a_number(self):
        receipts, records, _src = self.watch({})
        self.assertEqual(receipts, [])
        self.assertEqual(records[0]['status'], 'unresolved')
        self.assertIn('404', records[0]['reason'])

    def test_closed_or_priced_rows_are_not_watched(self):
        closed = fixture(state='not_open', best_of=None)
        priced = fixture(id='1082925', probabilities=[0.6, 0.4], best_of=None)
        src = FakeSources({self.URL: egw_page()})
        receipts, records = books.watch_unpriced(
            [], [closed, priced], src, NOW, register=self.rejected)
        self.assertEqual(receipts, [])
        self.assertEqual(records, [])
        self.assertEqual(src.reads, [])

    def test_fixture_with_known_format_stays_unpriced(self):
        # A known series format needs a separately verified listing format;
        # nothing is inferred, so the row keeps its blank percentage.
        row = fixture(best_of=3)
        receipts, records, _src = self.watch({self.URL: egw_page()}, row=row)
        self.assertEqual(receipts, [])
        self.assertEqual(records[0]['status'], 'unresolved')

    def test_equal_live_pair_picks_no_directional_edge(self):
        # Identical pairs are refused at parse level: the watch can never turn
        # a coin-flip claim or a placeholder into a 50/50.
        receipts, records, _src = self.watch({self.URL: egw_page(odds1='2.05', odds2='2.05')})
        self.assertEqual(receipts, [])
        self.assertEqual(records[0]['status'], 'unresolved')

    def test_promoted_receipt_prices_the_row_end_to_end(self):
        receipts, _records, _src = self.watch({self.URL: egw_page()})
        row = fixture(pick=None, method=None, best_of=None)
        book_research_pick(row, receipts=receipts, now=NOW)
        self.assertEqual(row['method'], 'bookmaker_fallback')
        self.assertEqual(row['pick'], 'FlyQuest')
        self.assertAlmostEqual(sum(row['probabilities']), 1.0, places=9)
        self.assertGreater(row['probabilities'][0], row['probabilities'][1])
        self.assertTrue(any('listing' in f.lower() or 'bookmaker' in f.lower()
                            for f in row['flags']))

    def test_watch_never_modifies_the_receipts_register(self):
        register = ROOT / 'data' / 'book-receipts.json'
        before = register.read_bytes()
        self.watch({self.URL: egw_page()})
        self.assertEqual(register.read_bytes(), before)

    def test_aliased_listing_labels_promote_through_the_identity_register(self):
        row = fixture(id='1079999', teams=['WBT', 'EAC'],
                      start='2026-10-25T08:00:00Z', best_of=None)
        page = egw_page(team1='WROTBERRY', team2='EAC',
                        start='2026-10-25T08:00:00.000Z', second_label='EAC')
        rejected = [{'fixture_id': '1079999', 'teams': ['WBT', 'EAC'],
                     'url': 'https://egamersworld.com/counterstrike/match/x/y',
                     'displayed': [1.8, 1.8]}]
        src = FakeSources({rejected[0]['url']: page})
        receipts, records = books.watch_unpriced([], [row], src, NOW, register=rejected)
        self.assertEqual(len(receipts), 1, records)
        self.assertEqual(receipts[0]['odds'], [1.72, 2.10])


class TestExecutiveSummaryDiscoverability(unittest.TestCase):
    """The user must land on the picks in one or two taps from the summary."""

    @classmethod
    def setUpClass(cls):
        cls.index = (ROOT / 'index.html').read_text()
        cls.picks = (ROOT / 'picks.html').read_text()
        cls.unresolved = (ROOT / 'unresolved.html').read_text()
        cls.data = json.loads((ROOT / 'data' / 'latest.json').read_text())
        cls.open_rows = [m for m in cls.data['matches'] if m.get('state') == 'open']

    def test_summary_links_to_the_updated_picks_list(self):
        section = self.index.split('id="start-here"', 1)[-1].split('</section>', 1)[0]
        self.assertIn('href="picks.html"', section)
        self.assertRegex(self.index, r'<nav class="mobile-tabs"[^>]*>.*href="picks\.html"',
                         msg='phone navigation must link the pick list')

    def test_summary_carries_the_unresolved_limitations_section(self):
        self.assertIn('id="unresolved-summary"', self.index)
        section = self.index.split('id="unresolved-summary"', 1)[-1].split('</section>', 1)[0]
        self.assertIn('unresolved.html', section)
        for m in self.open_rows:
            if m.get('probabilities') is None:
                for team in m['teams']:
                    self.assertIn(team, section,
                                  msg='unresolved summary must name the team whose row has no percentage')

    def test_every_open_fixture_appears_on_the_picks_page(self):
        for m in self.open_rows:
            self.assertRegex(self.picks, r'data-match="%s"' % re.escape(str(m['id'])),
                             msg='open fixture %s missing from picks.html' % m['id'])

    def test_every_open_row_on_picks_carries_a_source_link(self):
        body = re.sub(r'<script[^>]*>.*?</script>', '', self.picks, flags=re.S)
        for m in self.open_rows:
            row_html = re.search(
                r'<tr class="row[^"]*"[^>]*data-match="%s"[^>]*>.*?</tr>' % re.escape(str(m['id'])),
                body, re.S)
            self.assertIsNotNone(row_html, 'row %s not rendered' % m['id'])
            block = row_html.group(0)
            self.assertIn('source-links', block)
            self.assertTrue(re.search(r'href="https://[^"]*(hotspawn\.com|hltv\.org|polymarket\.com)', block),
                            msg='row %s must link an official source' % m['id'])

    def test_research_rows_show_the_pick_and_never_a_guessed_percentage(self):
        body = re.sub(r'<script[^>]*>.*?</script>', '', self.picks, flags=re.S)
        for m in self.open_rows:
            if m.get('probabilities') is not None or not m.get('pick'):
                continue
            row_html = re.search(
                r'<tr class="row[^"]*"[^>]*data-match="%s"[^>]*>.*?</tr>' % re.escape(str(m['id'])),
                body, re.S).group(0)
            self.assertIn(m['pick'], row_html)
            self.assertRegex(row_html, r'class="pick[^"]*"[^>]*>%s<' % re.escape(m['pick']))
            self.assertRegex(row_html, r'Blank means unverified, never 50/50|No verified market')
            self.assertNotRegex(row_html, r'\b50(?:\.0)?%\b')

    def test_unresolved_page_lists_every_row_without_a_percentage(self):
        for m in self.open_rows:
            if m.get('probabilities') is None:
                self.assertIn(str(m['id']), self.unresolved)
                self.assertIn(m['teams'][0], self.unresolved)
                self.assertIn(m['teams'][1], self.unresolved)

    def test_unresolved_page_states_the_limitations_with_sources(self):
        self.assertRegex(self.unresolved, r'Every source tried')
        for m in self.open_rows:
            if m.get('probabilities') is None:
                block = self.unresolved.split('data-match="%s"' % m['id'], 1)
                if len(block) == 2:
                    self.assertRegex(block[1][:4000], r'href="https://')
                    break

    def test_priced_rows_display_both_probabilities(self):
        body = re.sub(r'<script[^>]*>.*?</script>', '', self.picks, flags=re.S)
        shown = 0
        for m in self.open_rows:
            p = m.get('probabilities')
            if not p:
                continue
            row_html = re.search(
                r'<tr class="row[^"]*"[^>]*data-match="%s"[^>]*>.*?</tr>' % re.escape(str(m['id'])),
                body, re.S).group(0)
            for team, prob in zip(m['teams'], p):
                self.assertIn(team, row_html)
                self.assertIn('%.1f%%' % (prob * 100), row_html,
                              msg='row %s must display %s win probability' % (m['id'], team))
            shown += 1
        self.assertEqual(shown, sum(1 for m in self.open_rows if m.get('probabilities')))


class TestMobileLayoutContract(unittest.TestCase):
    PAGES = ('index.html', 'picks.html', 'matches.html', 'unresolved.html',
             'review.html', 'analysis.html', 'sources.html', 'evidence.html')

    def test_viewport_meta_on_every_primary_page(self):
        for name in self.PAGES:
            html = (ROOT / name).read_text()
            self.assertIn('name="viewport"', html, msg=name + ' must set the mobile viewport')
            self.assertIn('width=device-width', html, msg=name + ' must scale to the phone width')

    def test_phone_navigation_reaches_picks_and_unresolved(self):
        for name in self.PAGES:
            html = (ROOT / name).read_text()
            nav = re.search(r'<nav class="mobile-tabs".*?</nav>', html, re.S)
            self.assertIsNotNone(nav, name + ' must carry the phone navigation')
            for target in ('picks.html', 'unresolved.html', 'matches.html'):
                self.assertIn('href="%s"' % target, nav.group(0), msg='%s nav misses %s' % (name, target))

    def test_stylesheet_covers_phone_widths(self):
        css = (ROOT / 'assets' / 'style.css').read_text()
        self.assertIn('@media', css)
        self.assertIn('.mobile-tabs', css)
        self.assertRegex(css, r'@media[^{]*max-width\s*:\s*(4[0-9]{2}|[5-9][0-9]{2}|1[0-9]{3})px')


if __name__ == '__main__':
    unittest.main()


class TestIndependentAuditorAcceptsDatedMirror(unittest.TestCase):
    """Regression: the independent auditor must accept the same mirror
    provenance the validator accepts.

    The mirror tier reads HLTV's *dated* Valve-ranking view
    (/valve-ranking/teams/2026/october/22) because one refused canonical read
    blocks HLTV for the whole run. scripts/validate.py learned that form in
    session cf12d97f, but verification-c6/audit_snapshot.py still required the
    canonical path — so the quarantine step withheld three fully valid
    model_vrs_mirror picks (1081149, 1081150, 1082926) on the 10:15Z snapshot
    and the public board showed open matches with no pick at all. These tests
    pin the shared rule on real retained evidence and keep the negative control.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'audit_snapshot_4fd13975', ROOT / 'verification-c6' / 'audit_snapshot.py')
        cls.audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.audit)
        cls.data = json.loads((ROOT / 'data' / 'latest.json').read_text())

    def mirror_rows(self):
        return [m for m in self.data['matches'] if m.get('method') == 'model_vrs_mirror']

    def test_real_mirror_rows_pass_the_independent_auditor(self):
        rows = self.mirror_rows()
        if not rows:
            self.skipTest('no model_vrs_mirror rows in this snapshot')
        problems, _errors = self.audit.inspect(self.data)
        failing = {m['id']: p for m, p in problems if p}
        for m in rows:
            self.assertNotIn(m['id'], failing, msg=str(failing.get(m['id']))[:400])

    def test_dated_url_is_accepted_and_a_foreign_host_is_not(self):
        import copy
        rows = self.mirror_rows()
        if not rows:
            self.skipTest('no model_vrs_mirror rows in this snapshot')
        probe = copy.deepcopy(self.data)
        target = next(m for m in probe['matches'] if m.get('method') == 'model_vrs_mirror')
        quote = target['evidence'][0]
        self.assertRegex(quote['url'], r'^https://www\.hltv\.org/valve-ranking/teams'
                                       r'(/\d{4}/[a-z]+/\d{1,2})?$')
        problems, _errors = self.audit.inspect(probe)
        target_problems = next(p for m, p in problems if m['id'] == target['id'])
        self.assertFalse(any('Mirror input' in p for p in target_problems),
                         msg='dated HLTV view must be accepted: %s' % target_problems)
        # Negative control: the same quote from a foreign host must still fail.
        probe2 = copy.deepcopy(self.data)
        target2 = next(m for m in probe2['matches'] if m.get('method') == 'model_vrs_mirror')
        target2['evidence'][0]['url'] = 'https://example.com/valve-ranking/teams'
        target2['evidence'][0]['api_url'] = target2['evidence'][0]['url']
        problems2, _errors2 = self.audit.inspect(probe2)
        target2_problems = next(p for m, p in problems2 if m['id'] == target2['id'])
        self.assertTrue(any('Mirror input' in p for p in target2_problems),
                        msg='a foreign host must still be rejected')
