"""Session 148be742: pick coverage for every open match, and a phone-first summary.

What this session had to prove
------------------------------
1. This repository's scheduled publisher was red for eighteen hours and the
   board froze at 2026-10-23T11:47Z. The cause was a test, not the data:
   ``tests/test_session_0cc1138a.py`` excused a missing lobby fixture only when
   ``inventory_changes.removed_ids`` named it, and that field is a delta against
   the previous 20-minute snapshot, so it is empty when a fixture drops between
   two cached snapshots. Parity is now read from the snapshot's own raw feed
   evidence, in both directions. ``FeedParity`` pins that.
2. The executive summary must link the updated pick list and carry a separate,
   source-linked unresolved/limitations section. ``ExecutiveSummaryLinks`` pins
   that on a real build of the committed snapshot.
3. Every open row must carry a pick, a sourced probability where one exists, or
   a published limitation. ``CoverageContract`` runs ``scripts.audit_148be742``
   over the committed snapshot and over deliberately corrupted copies.
4. The phone's first screen must show a pick. The CSS that lays the summary out
   for phones was nested inside ``@media (max-width:650px) and (max-height:700px)``
   by a missing closing brace, so it applied only to short phones and a modern
   390x844 device pushed the first pick card to y=745. ``PhoneStylesheet`` pins
   the brace balance and the top-level placement; the measured result at
   320x568, 390x844 and 430x932 is y=324 (see research/session-148be742/REPORT.md).
"""
import copy
import json
import re
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import audit_148be742 as audit
from scripts import build as builder

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())
CSS = (ROOT / 'site' / 'assets' / 'style.css').read_text()
PUBLIC_CSS = (ROOT / 'assets' / 'style.css').read_text()


def build_pages(data, now=None):
    """Build the dashboard for ``data`` into a temp dir and return its path."""
    out = Path(tempfile.mkdtemp(prefix='cs2-scout-148be742-'))
    clock = now or datetime.fromisoformat(
        (data.get('built_at') or data['fixtures_observed_at']).replace('Z', '+00:00'))
    builder.build(copy.deepcopy(data), out, now=clock)
    return out


class FeedParity(unittest.TestCase):
    def test_board_and_raw_feed_agree_in_both_directions(self):
        evidence = {str(x.get('id')) for x in SNAPSHOT['fixture_evidence'] if x.get('id')}
        board = {m['id'] for m in SNAPSHOT['matches']}
        self.assertTrue(evidence, 'the snapshot carries no raw fixture evidence')
        self.assertEqual(evidence - board, set(), 'feed fixture missing from the board')
        self.assertEqual(board - evidence, set(), 'board row with no raw feed fixture')

    def test_parity_does_not_depend_on_a_delta_field(self):
        # The defect this session repaired: a fixture that left the feed is
        # excused by absence from the feed evidence, not by removed_ids.
        doc = copy.deepcopy(SNAPSHOT)
        doc['inventory_changes'] = {'compared_with': doc['generated_at'],
                                    'added_ids': [], 'removed_ids': []}
        dropped = doc['matches'][0]['id']
        doc['matches'] = [m for m in doc['matches'] if m['id'] != dropped]
        doc['fixture_evidence'] = [x for x in doc['fixture_evidence']
                                   if str(x.get('id')) != dropped]
        evidence = {str(x.get('id')) for x in doc['fixture_evidence']}
        board = {m['id'] for m in doc['matches']}
        self.assertEqual(evidence ^ board, set())

    def test_the_committed_snapshot_is_inside_its_evidence_window(self):
        clock = datetime.fromisoformat(
            (SNAPSHOT.get('built_at') or SNAPSHOT['generated_at']).replace('Z', '+00:00'))
        observed = datetime.fromisoformat(SNAPSHOT['fixtures_observed_at'].replace('Z', '+00:00'))
        self.assertLess((clock - observed).total_seconds(), 8 * 3600)


class CoverageContract(unittest.TestCase):
    """Every open match: a pick, a sourced probability, or a published limit."""

    @classmethod
    def setUpClass(cls):
        cls.site = build_pages(SNAPSHOT)

    def test_every_open_match_has_a_pick_and_the_pages_show_it(self):
        result = audit.audit(SNAPSHOT, self.site)
        self.assertTrue(result['passed'], '\n'.join(result['problems']))
        self.assertEqual(result['open_with_pick'], result['open'])
        self.assertEqual(result['open_resolved'], result['open']) if 'open_resolved' in result else None

    def test_a_priced_row_without_its_quote_is_rejected(self):
        doc = copy.deepcopy(SNAPSHOT)
        row = next(m for m in doc['matches'] if m['state'] == 'open' and m['probabilities'])
        row['evidence'] = []
        problems = audit.audit_snapshot(doc)[1]
        self.assertTrue(any('no retained quote' in p for p in problems), problems)

    def test_probabilities_that_do_not_sum_to_one_are_rejected(self):
        doc = copy.deepcopy(SNAPSHOT)
        row = next(m for m in doc['matches'] if m['state'] == 'open' and m['probabilities'])
        row['probabilities'] = [row['probabilities'][0], row['probabilities'][1] + 0.1]
        problems = audit.audit_snapshot(doc)[1]
        self.assertTrue(any('sum to' in p for p in problems), problems)

    def test_reversing_the_pick_is_rejected(self):
        doc = copy.deepcopy(SNAPSHOT)
        row = next(m for m in doc['matches'] if m['state'] == 'open' and m['probabilities'])
        row['pick'] = row['teams'][1 - row['teams'].index(row['pick'])]
        problems = audit.audit_snapshot(doc)[1]
        self.assertTrue(any('not the more likely team' in p for p in problems), problems)

    def test_a_row_with_no_pick_and_no_limitation_is_rejected(self):
        doc = copy.deepcopy(SNAPSHOT)
        row = next(m for m in doc['matches'] if m['state'] == 'open')
        row.update(pick=None, probabilities=None, fair_odds=None, method=None,
                   reason='', attempts=[], expires_at=None)
        problems = audit.audit_snapshot(doc)[1]
        self.assertTrue(any('has no pick at all' in p for p in problems), problems)
        self.assertTrue(any('no limitation' in p for p in problems), problems)
        self.assertTrue(any('no sourced attempt' in p for p in problems), problems)

    def test_a_research_pick_may_not_publish_a_number(self):
        doc = copy.deepcopy(SNAPSHOT)
        row = next(m for m in doc['matches'] if m['state'] == 'open')
        row.update(pick=row['teams'][0], probabilities=None, fair_odds=[1.8, 1.8],
                   method='research_rank', reason='No verified market line.',
                   attempts=[{'provider': 'Rank research', 'status': 'resolved',
                              'url': 'https://www.hltv.org/ranking/teams'}])
        problems = audit.audit_snapshot(doc)[1]
        self.assertTrue(any('must not publish fair odds' in p for p in problems), problems)

    def test_a_fixture_the_build_retired_is_not_demanded_on_the_board(self):
        # The defect that stopped the publishing job on 2026-10-24: once the wall
        # clock crossed a kick-off, the committed snapshot still called the row
        # open while the rebuilt board had retired it by design, so the coverage
        # gate failed on clock drift alone. The gate must judge the pages at the
        # clock they were built at.
        doc = copy.deepcopy(SNAPSHOT)
        clock = datetime.fromisoformat(
            (doc.get('built_at') or doc['generated_at']).replace('Z', '+00:00'))
        later = [m for m in doc['matches'] if m['state'] == 'open' and m['probabilities']
                 and datetime.fromisoformat(m['start'].replace('Z', '+00:00')) > clock]
        self.assertTrue(later, 'no open row starts after the snapshot clock')
        row = later[0]
        row['start'] = (clock - timedelta(minutes=5)).isoformat().replace('+00:00', 'Z')
        row['lock'] = row['start']
        site = build_pages(doc, now=clock)
        result = audit.audit(doc, site)
        self.assertIn(row['id'], result['expired_at_build'])
        self.assertTrue(result['passed'], '\n'.join(result['problems']))

    def test_a_future_fixture_missing_from_the_board_is_still_rejected(self):
        doc = copy.deepcopy(SNAPSHOT)
        clock = datetime.fromisoformat(
            (doc.get('built_at') or doc['generated_at']).replace('Z', '+00:00'))
        upcoming = [m for m in doc['matches'] if m['state'] == 'open' and m['probabilities']
                    and datetime.fromisoformat(m['start'].replace('Z', '+00:00')) > clock]
        self.assertTrue(upcoming, 'no open row starts after the snapshot clock')
        row = upcoming[0]
        retired = copy.deepcopy(doc)
        twin = next(m for m in retired['matches'] if m['id'] == row['id'])
        twin['start'] = (clock - timedelta(minutes=5)).isoformat().replace('+00:00', 'Z')
        twin['lock'] = twin['start']
        site = build_pages(retired, now=clock)
        problems, expired = audit.audit_pages(doc, site)
        self.assertNotIn(row['id'], expired)
        self.assertTrue(any(row['id'] in p and 'not on the pick board' in p for p in problems))

    def test_a_stale_quote_is_rejected(self):
        doc = copy.deepcopy(SNAPSHOT)
        row = next(m for m in doc['matches'] if m['state'] == 'open' and m['probabilities'])
        row['evidence'][0]['observed_at'] = '2020-01-01T00:00:00Z'
        problems = audit.audit_snapshot(doc)[1]
        self.assertTrue(any('older than the 8-hour window' in p for p in problems), problems)


class ExecutiveSummaryLinks(unittest.TestCase):
    """The summary must point at the picks and carry the unresolved section."""

    @classmethod
    def setUpClass(cls):
        site = build_pages(SNAPSHOT)
        cls.index = (site / 'index.html').read_text()
        cls.soup = BeautifulSoup(cls.index, 'html.parser')
        cls.opens = [m for m in SNAPSHOT['matches'] if m['state'] == 'open']

    def test_the_summary_links_the_updated_pick_list(self):
        hrefs = {a['href'] for a in self.soup.find_all('a', href=True)}
        self.assertIn('picks.html', hrefs)
        self.assertIn('#picks-at-a-glance', hrefs)
        self.assertIn('unresolved.html', hrefs)

    def test_the_unresolved_count_is_a_tap_target_to_the_limits_section(self):
        strip = self.soup.select_one('#freshness-strip')
        link = strip.select_one('a.fresh-unresolved')
        self.assertIsNotNone(link, 'the unresolved count is not a link on the first screen')
        self.assertEqual(link['href'], '#unresolved-limits')
        self.assertIsNotNone(self.soup.select_one('#unresolved-limits'))

    def test_the_unresolved_section_states_the_limitations(self):
        section = self.soup.select_one('#unresolved-limits')
        text = section.get_text(' ', strip=True).lower()
        for phrase in ('50/50', 'collection limit', 'both teams', 'must match exactly',
                       'evidence expires'):
            self.assertIn(phrase, text)
        # There is a second, row-by-row section with the ladder behind it.
        self.assertIsNotNone(self.soup.select_one('#unresolved-picks'))

    def test_the_summary_says_nothing_is_blank_only_when_it_is_true(self):
        missing = [m for m in self.opens if m['probabilities'] is None or not m.get('pick')]
        text = self.soup.select_one('#unresolved-picks').get_text(' ', strip=True)
        if missing:
            self.assertNotIn('Nothing is blank', text)
            for m in missing:
                self.assertIn(m['id'], text)
        else:
            self.assertIn('carries a pick and a win probability', text)

    def test_every_open_card_prints_both_teams_and_both_numbers(self):
        cards = {a['href'].rsplit('-', 1)[-1]: a
                 for a in self.soup.select('#picks-at-a-glance a.glance-card-mobile')}
        self.assertEqual(len(cards), len(self.opens))
        for m in self.opens:
            text = cards[m['id']].get_text(' ', strip=True)
            for team in m['teams']:
                self.assertIn(team, text, m['id'])
            if m['probabilities']:
                for p in m['probabilities']:
                    self.assertIn('%.1f%%' % (p * 100), text, m['id'])


class PhoneStylesheet(unittest.TestCase):
    """The summary's phone layout must not be trapped in a short-phone query."""

    def blocks(self, css):
        """Yield (condition, selector-ish text) for every rule, with nesting."""
        out, stack = [], []
        line = 1
        start = 0
        for index, ch in enumerate(css):
            if ch == '\n':
                line += 1
            elif ch == '{':
                head = css[start:index].strip().split('}')[-1].strip()
                stack.append((head, line))
                start = index + 1
            elif ch == '}':
                if stack:
                    head, start_line = stack.pop()
                    if head.startswith('@media'):
                        out.append(('media', head, [h for h, _ in stack]))
                    else:
                        out.append(('rule', head, [h for h, _ in stack],
                                    [h for h, _ in stack if h.startswith('@media')]))
                start = index + 1
        return out

    def test_both_published_copies_are_brace_balanced(self):
        for name, css in (('site/assets/style.css', CSS), ('assets/style.css', PUBLIC_CSS)):
            depth = 0
            for ch in css:
                depth += (ch == '{') - (ch == '}')
                self.assertGreaterEqual(depth, 0, '%s closes a block it never opened' % name)
            self.assertEqual(depth, 0, '%s has an unclosed block' % name)

    def test_the_summary_phone_layout_is_not_nested_in_a_height_query(self):
        for name, css in (('site/assets/style.css', CSS), ('assets/style.css', PUBLIC_CSS)):
            nested = []
            for entry in self.blocks(css):
                if entry[0] != 'rule' or 'data-page="index"' not in entry[1]:
                    continue
                if any('max-height' in cond for cond in entry[3]):
                    nested.append(entry[1])
            self.assertEqual(nested, [], '%s nests the summary layout in a height query: %r'
                             % (name, nested[:3]))

    def test_the_summary_layout_reaches_a_tall_phone(self):
        # 650px wide is the phone breakpoint and 844 is a modern phone height,
        # so a rule under `max-height:700px` cannot be what makes a phone work.
        self.assertIn('body[data-page="index"] main{display:flex;flex-direction:column}', CSS)
        self.assertNotRegex(CSS, r'@media\(max-width:650px\) and \(max-height:700px\)\{[^}]*'
                                 r'data-page="index"\] main\{display:flex')

    def test_the_strip_link_is_styled_in_both_copies(self):
        for name, css in (('site/assets/style.css', CSS), ('assets/style.css', PUBLIC_CSS)):
            self.assertIn('a.fresh-unresolved', css, name)


if __name__ == '__main__':
    unittest.main()
