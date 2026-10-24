"""Session 174afa4f regression tests.

Three behaviours are pinned here, each with its corruption negatives:

1. The un-deadlocked lobby-parity oracle in ``tests.test_session_0cc1138a``:
   a fixture the verified feed no longer returns is provably feed-removed;
   a fixture the collector dropped, or any excuse under partial coverage,
   is not.
2. The HLTV team-page rank fallback (``scripts.core._team_page_rank_rows``):
   a pick without a percentage from official team pages only when both
   exact pages carry usable, heading-verified rank evidence -- never a
   probability, never an inference over a missing rank.
3. The always-visible executive summary on the landing page: live
   completeness counters and large in-site links to the updated picks,
   this page's pick list, and the unresolved/limitations section, ordered
   directly under the freshness strip on a phone.
"""
import copy
import json
import unittest
from pathlib import Path

from scripts import audit_174afa4f, core, probe_174afa4f, summary
from scripts.build import exec_summary_bar, overview
from tests.test_session_0cc1138a import feed_removed_ids

ROOT = Path(__file__).resolve().parents[1]
NOW = '2026-10-24T06:00:00Z'


def snapshot(coverage='verified', evidence_ids=('1', '2'), match_ids=('1', '2'),
             removed=()):
    return {
        'coverage': coverage,
        'fixture_evidence': [{'id': i} for i in evidence_ids],
        'matches': [{'id': i} for i in match_ids],
        'inventory_changes': {'removed_ids': list(removed)},
    }


class FeedRemovedProofTests(unittest.TestCase):
    def test_previous_rotation_removal_is_excused_by_feed_evidence(self):
        # 9 was on the lobby at observation time; the current snapshot's delta
        # records no removal for it, but the verified raw feed -- proven
        # complete against the published rows -- no longer contains it.
        self.assertEqual(feed_removed_ids(snapshot(), {'1', '9'}), {'9'})

    def test_collector_drop_is_never_excused(self):
        # Raw evidence still contains 9 but no row was published for it: the
        # parity proof collapses and nothing is excused.
        data = snapshot(evidence_ids=('1', '2', '9'), match_ids=('1', '2'))
        self.assertEqual(feed_removed_ids(data, {'9'}), set())

    def test_partial_or_retained_coverage_excuses_nothing_extra(self):
        for coverage in ('partial', 'retained', None):
            with self.subTest(coverage=coverage):
                self.assertEqual(
                    feed_removed_ids(snapshot(coverage=coverage), {'9'}), set())

    def test_removal_recorded_in_latest_delta_is_excused(self):
        self.assertEqual(
            feed_removed_ids(snapshot(removed=('9',)), {'9'}), {'9'})

    def test_still_listed_fixture_is_never_excused(self):
        self.assertEqual(feed_removed_ids(snapshot(), {'1', '2'}), set())

    def test_deadlock_guard_agrees_with_oracle(self):
        current = snapshot()
        previous = {'matches': [{'id': '1'}, {'id': '9'}]}
        guard = audit_174afa4f.deadlock_guard(current, previous)
        self.assertEqual(guard['vanished_vs_previous'], ['9'])
        self.assertEqual(guard['vanished_proved_feed_removed'], ['9'])
        self.assertEqual(guard['vanished_unproved'], [])
        dropped = audit_174afa4f.deadlock_guard(
            snapshot(evidence_ids=('1', '2', '9'), match_ids=('1', '2')), previous)
        self.assertEqual(dropped['vanished_proved_feed_removed'], [])
        self.assertEqual(dropped['vanished_unproved'], ['9'])


def team_pages(rank_a, rank_b, heading_a='Alpha', heading_b='Bravo',
               url_a='https://www.hltv.org/team/111/alpha',
               url_b='https://www.hltv.org/team/222/bravo'):
    def view(team, rank, heading, url):
        return {'team': team, 'label': heading,
                'world_rank': rank,
                'world_rank_status': 'ranked' if rank else ('unranked' if rank is None else 'rank_unknown'),
                'world_rank_source': 'https://www.hltv.org/ranking/teams' if rank else None,
                'observed_at': NOW, 'url': url}
    return {'status': 'available', 'observed_at': NOW,
            'teams': [view('Alpha', rank_a, heading_a, url_a),
                      view('Bravo', rank_b, heading_b, url_b)]}


def fixture(rank_a, rank_b, **kw):
    return {'id': '9001', 'teams': ['Alpha', 'Bravo'], 'start': '2026-10-25T12:00:00Z',
            'lock': '2026-10-25T12:00:00Z',
            'state': 'open', 'pick': None, 'probabilities': None, 'fair_odds': None,
            'method': None, 'reason': None, 'expires_at': None,
            'evidence': [], 'attempts': [], 'flags': [],
            'hltv_team_pages': team_pages(rank_a, rank_b, **kw)}


class TeamPageRankTierTests(unittest.TestCase):
    @staticmethod
    def applied(m):
        core.research_rank_pick(m)  # mutates in place; returns None either way
        return m['pick'] is not None

    def test_better_rank_picks_without_probability(self):
        m = fixture(12, 40)
        self.assertTrue(self.applied(m))
        self.assertEqual(m['pick'], 'Alpha')
        self.assertEqual(m['method'], 'research_rank')
        self.assertIsNone(m['probabilities'])
        resolved = m['hltv_team_pages']['resolved_ranks']
        self.assertEqual([r['hltv_rank'] for r in resolved], [12, 40])
        self.assertTrue(all(r['evidence'] == 'hltv_team_pages' for r in resolved))
        self.assertNotIn('hltv_context', m)

    def test_single_ranked_side_picks_with_single_method(self):
        m = fixture(None, 25)
        self.assertTrue(self.applied(m))
        self.assertEqual((m['pick'], m['method']), ('Bravo', 'research_rank_single'))
        self.assertIsNone(m['probabilities'])

    def test_unknown_rank_never_becomes_unranked(self):
        m = fixture(10, 0)  # 0 is not a positive rank -> rank_unknown
        m['hltv_team_pages']['teams'][1]['world_rank_status'] = 'rank_unknown'
        self.assertFalse(self.applied(m))
        self.assertIsNone(m['pick'])

    def test_equal_ranks_and_both_unranked_pick_nothing(self):
        for ranks in ((30, 30), (None, None)):
            with self.subTest(ranks=ranks):
                m = fixture(*ranks)
                self.assertFalse(self.applied(m))
                self.assertIsNone(m['pick'])

    def test_heading_mismatch_blocks_the_tier(self):
        m = fixture(5, 90, heading_a='Different Squad')
        self.assertFalse(self.applied(m))

    def test_missing_url_or_timestamp_blocks_the_tier(self):
        m = fixture(5, 90)
        del m['hltv_team_pages']['teams'][0]['url']
        self.assertFalse(self.applied(m))
        m = fixture(5, 90)
        m['hltv_team_pages']['teams'][1]['observed_at'] = None
        self.assertFalse(self.applied(m))

    def test_fixture_page_ranks_take_precedence_over_team_pages(self):
        m = fixture(12, 40)
        m['hltv_context'] = {'observed_at': NOW,
            'source': 'https://www.hltv.org/matches/2390000/alpha-vs-bravo',
            'ranks': [{'team': 'Alpha', 'hltv_rank': 33, 'source': 'https://www.hltv.org/ranking/teams'},
                      {'team': 'Bravo', 'hltv_rank': 8, 'source': 'https://www.hltv.org/ranking/teams'}]}
        self.assertTrue(self.applied(m))
        self.assertEqual(m['pick'], 'Bravo')
        self.assertIn('resolved_ranks', m['hltv_context'])
        self.assertNotIn('resolved_ranks', m['hltv_team_pages'])

    def test_team_page_evidence_expires_like_every_source(self):
        m = fixture(12, 40)
        self.assertTrue(self.applied(m))
        deadline = core.pick_deadline(m, NOW)
        self.assertIsNotNone(deadline)
        self.assertEqual(deadline, '2026-10-24T14:00:00Z')  # observed + 8 h

    def test_rank_resolution_reads_team_pages_only(self):
        m = fixture(None, 25)
        _context, info = core.rank_resolution(m)
        expected = core._team_page_rank_rows(m)
        self.assertEqual(info, expected)
        self.assertEqual([r['status'] for r in info], ['unranked', 'ranked'])


class ExecSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'data' / 'latest.json').read_text())
        cls.bar = exec_summary_bar(copy.deepcopy(cls.data))
        cls.page = overview(copy.deepcopy(cls.data))
        cls.css = (ROOT / 'site' / 'assets' / 'style.css').read_text()

    def test_bar_carries_live_counts_and_in_site_links(self):
        counts = summary.counts(self.data['matches'])
        self.assertIn('id="exec-summary"', self.bar)
        self.assertIn('data-completeness', self.bar)
        for href in ('href="picks.html"', 'href="#picks-at-a-glance"',
                     'href="#unresolved-picks"', 'href="unresolved.html"',
                     'href="matches.html"', 'href="sources.html#method"'):
            self.assertIn(href, self.bar)
        for name, key in (('open', 'open'), ('picked', 'with_pick'),
                          ('priced', 'priced'), ('missing', 'without_percentage'),
                          ('unresolved', 'no_pick')):
            self.assertIn('data-count="%s">%d<' % (name, counts[key]), self.bar)

    def test_bar_sits_between_freshness_and_pick_list(self):
        fresh = self.page.find('id="freshness-strip"')
        bar = self.page.find('id="exec-summary"')
        glance = self.page.find('id="picks-at-a-glance"')
        self.assertTrue(-1 < fresh < bar < glance)

    def test_phone_order_and_touch_targets(self):
        self.assertIn('body[data-page="index"] main>#exec-summary{order:3}', self.css)
        self.assertIn('.exec-summary .exec-summary-actions .button{flex:1 1 0;min-height:46px', self.css)
        self.assertIn('.exec-summary .small{display:none}', self.css)
        # Canonical CSS and the committed root copy must stay byte-identical.
        self.assertEqual(self.css.encode(),
                         (ROOT / 'assets' / 'style.css').read_bytes())


class ProbeTargetTests(unittest.TestCase):
    def test_targets_are_exactly_the_non_featured_open_rows(self):
        rows = [
            {'id': '1', 'state': 'open', 'pick': 'A', 'probabilities': [.6, .4], 'method': 'exchange'},
            {'id': '2', 'state': 'open', 'pick': None, 'probabilities': None, 'method': None,
             'teams': ['A', 'B'], 'start': NOW, 'reason': 'x', 'attempts': []},
            {'id': '3', 'state': 'open', 'pick': 'B', 'probabilities': None, 'method': 'research_rank',
             'teams': ['A', 'B'], 'start': NOW, 'attempts': []},
            {'id': '4', 'state': 'open', 'pick': 'A', 'probabilities': [.55, .45], 'method': 'model_vrs',
             'teams': ['A', 'B'], 'start': NOW, 'attempts': []},
            {'id': '5', 'state': 'not_open', 'pick': None, 'probabilities': None, 'method': None},
        ]
        found = {row['id']: row['kind'] for row in probe_174afa4f.targets({'matches': rows})}
        self.assertEqual(set(found), {'2', '3', '4'})
        self.assertTrue(found['2'].startswith('no pick'))
        self.assertTrue(found['3'].startswith('pick without %'))
        self.assertIn('model_vrs', found['4'])
        # The probe is diagnostic: it must not attach a price to any target.
        for row in probe_174afa4f.targets({'matches': rows}):
            self.assertNotIn('probabilities', row)


class StylesheetBraceBalanceTests(unittest.TestCase):
    def test_no_media_block_is_left_unclosed(self):
        # Regression pin: one missing '}' after the max-height picks block
        # silently nested ~140 lines of phone CSS (including the f89bb1f8
        # first-screen compaction) inside (max-height:700px), so tall
        # phones never received it. The shipped stylesheet must balance.
        css = (ROOT / 'site' / 'assets' / 'style.css').read_text()
        depth = 0
        for line in css.splitlines():
            depth += line.count('{') - line.count('}')
            self.assertGreaterEqual(depth, 0)
        self.assertEqual(depth, 0)


class CommittedBoardConsistencyTests(unittest.TestCase):
    def test_committed_index_contains_the_visible_summary(self):
        index = (ROOT / 'index.html').read_text()
        self.assertIn('id="exec-summary"', index)
        self.assertIn('href="picks.html"', index)
        self.assertIn('href="#unresolved-picks"', index)


if __name__ == '__main__':
    unittest.main()
