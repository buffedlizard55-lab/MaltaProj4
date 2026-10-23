"""Session 8fdf1f99 — publish-gate repair, unresolved-pick research, phone audit.

What this session found and fixed
---------------------------------
``main`` was red from 2026-10-22T20:16Z: two tests pinned the *historical*
research sub-method of live snapshot rows (``research_rank_single``), and the
scheduled refresh re-derived those rows from the Valve standings tier
(``research_vrs_single``). The refresh job runs the unit suite *before* it reads
any source, so the failure blocked every publication slot and the public board
was left on the 20:15Z snapshot, past the 8-hour evidence window that
``assets/app.js`` enforces — which is why the live site withheld every pick.

The assertions in those two files now pin the invariant (a research tier, a pick
that is one of the two teams, no percentage) instead of a value that legitimately
changes with each refresh. This file adds:

* the drift-tolerant assertions themselves, so the repair cannot silently revert;
* a structural audit of every open row (pick in teams, research rows never carry
  a percentage, every unpriced row is named in the unresolved section);
* the session's own research receipt (fixture 1082860) replayed against the
  committed snapshot through the production pricing path;
* the executive-summary and phone checks the user asked for.

Run: python -m unittest discover -s tests -v
"""
import copy
import json
import re
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.core import book_candidate, book_receipts, book_research_pick, norm

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())
INDEX = (ROOT / 'index.html').read_text()
UNRESOLVED = (ROOT / 'unresolved.html').read_text()
PICKS = (ROOT / 'picks.html').read_text()
RECEIPTS = json.loads((ROOT / 'data' / 'book-receipts.json').read_text())['receipts']
MARKET_METHODS = {'exchange', 'exchange_wide', 'bookmaker_fallback'}
MODEL_METHODS = {'model_vrs', 'model_vrs_mirror'}


def receipt(fixture_id):
    return next(r for r in RECEIPTS if str(r.get('fixture_id')) == str(fixture_id))


class PublishGateDriftTests(unittest.TestCase):
    """The publish gate must not pin a value that a routine refresh changes."""

    def test_research_tier_assertions_are_drift_tolerant(self):
        rank_file = (ROOT / 'tests' / 'test_session_13e99ca6.py').read_text()
        prelock_file = (ROOT / 'tests' / 'test_session_75ebd2d6.py').read_text()
        self.assertNotIn("startswith('research_rank')", rank_file)
        self.assertIn("startswith('research_')", rank_file)
        self.assertNotIn('self.assertEqual(m["method"], exp["method"], mid)', prelock_file)
        self.assertIn('startswith("research_")', prelock_file)

    def test_no_open_row_publishes_a_percentage_outside_a_priced_tier(self):
        for m in SNAPSHOT['matches']:
            if m['state'] != 'open' or m.get('probabilities') is None:
                continue
            self.assertIn(m.get('method'), MARKET_METHODS | MODEL_METHODS, m['id'])
            self.assertAlmostEqual(sum(m['probabilities']), 1.0, places=12, msg=m['id'])
            self.assertEqual(len(m['probabilities']), 2, m['id'])

    def test_every_research_row_has_a_pick_and_no_percentage(self):
        for m in SNAPSHOT['matches']:
            if not str(m.get('method') or '').startswith('research_'):
                continue
            self.assertEqual(m['state'], 'open', m['id'])
            self.assertIsNone(m['probabilities'], m['id'])
            self.assertIsNone(m['fair_odds'], m['id'])
            self.assertIn(m['pick'], m['teams'], m['id'])
            self.assertIsNotNone(m.get('reason'), m['id'])

    def test_every_open_row_has_a_pick(self):
        """The user's requirement: a pick for every match listed on Hotspawn."""
        for m in SNAPSHOT['matches']:
            if m['state'] != 'open':
                continue
            self.assertTrue(m.get('pick'), 'open row without a pick: %s' % m['id'])
            self.assertIn(m['pick'], m['teams'], m['id'])

    def test_every_unpriced_open_row_is_named_in_the_unresolved_sections(self):
        for m in SNAPSHOT['matches']:
            if m['state'] != 'open' or m.get('probabilities') is not None:
                continue
            for page, name in ((INDEX, 'index.html'), (UNRESOLVED, 'unresolved.html')):
                for team in m['teams']:
                    self.assertIn(team, page, '%s missing from %s' % (team, name))


class UnresolvedResearchReceiptTests(unittest.TestCase):
    """The session's researched line, replayed through the production path."""

    def test_every_receipt_carries_a_dated_https_observation(self):
        for r in RECEIPTS:
            self.assertTrue(str(r.get('url') or '').startswith('https://'), r.get('id'))
            self.assertTrue(str(r.get('observed_at') or '').endswith('Z'), r.get('id'))
            self.assertTrue(str(r.get('start') or '').endswith('Z'), r.get('id'))
            # Fixture ids are Hotspawn numeric ids; a few historical receipts are
            # pinned exchange snapshots whose id names the market instead.
            self.assertTrue(str(r.get('id') or ''), r.get('id'))
            self.assertTrue(str(r.get('fixture_id') or ''), r.get('id'))
            self.assertEqual(len(r['source_teams']), 2, r.get('id'))
            self.assertEqual(len(r['team_aliases']), 2, r.get('id'))
            self.assertTrue(all(a for a in r['team_aliases']), r.get('id'))
            self.assertEqual(len(r['odds']), 2, r.get('id'))
            if str(r.get('id', '')).startswith(('egw-', 'stavka-')):
                # Decimal bookmaker odds are always above evens' inverse floor.
                self.assertGreater(min(r['odds']), 1.0, r.get('id'))
            candidate = book_candidate(r)
            self.assertEqual(candidate['fixture_id'], str(r['fixture_id']))

    def test_flyquest_staqued_receipt_prices_its_fixture(self):
        r = receipt('1082860')
        row = next(m for m in SNAPSHOT['matches'] if str(m['id']) == '1082860')
        # The listing start must be the fixture start the board publishes.
        self.assertEqual(r['start'], row['start'])
        fixture = copy.deepcopy(row)
        fixture.update(probabilities=None, fair_odds=None, pick=None, method=None,
                       evidence=[], attempts=[], state='open', resolution_blocked=None)
        observed = datetime.strptime(r['observed_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        book_research_pick(fixture, receipts=[r], now=observed + timedelta(minutes=5))
        self.assertEqual(fixture['method'], 'bookmaker_fallback')
        self.assertEqual(fixture['pick'], 'FlyQuest')
        self.assertAlmostEqual(fixture['probabilities'][0], 1 / 1.001 / (1 / 1.001 + 1 / 12), places=12)
        self.assertAlmostEqual(sum(fixture['probabilities']), 1.0, places=12)
        quote = fixture['evidence'][0]
        self.assertEqual(quote['decimal_odds'], [1.001, 12.0])
        self.assertTrue(quote['url'].startswith('https://egamersworld.com/'))

    def test_unlisted_team_rows_record_why_no_model_line_exists(self):
        """A club with no published Valve points cannot get an originated line."""
        r = receipt('1082860')
        self.assertIn('no Valve VRS row', r['limitation'])
        row = next(m for m in SNAPSHOT['matches'] if str(m['id']) == '1082860')
        if row.get('probabilities') is None:
            self.assertIn(row['pick'], row['teams'])


class ExecutiveSummaryAndPhoneTests(unittest.TestCase):
    def test_summary_links_the_updated_pick_list_and_unresolved_section(self):
        for href in ('href="picks.html"', 'href="unresolved.html"', 'href="matches.html"'):
            self.assertIn(href, INDEX)
        self.assertIn('id="unresolved-picks"', INDEX)
        self.assertIn('id="picks-at-a-glance"', INDEX)
        self.assertIn('Where the updated picks are', INDEX)

    def test_unresolved_section_states_its_limitations(self):
        self.assertIn('Limitations for generating these picks', INDEX)
        self.assertIn('Every source tried', UNRESOLVED)
        self.assertIn('blank', INDEX.lower())

    def test_phone_markup_is_present_on_every_page(self):
        pages = {name: (ROOT / name).read_text() for name in
                 ('index.html', 'picks.html', 'unresolved.html', 'matches.html')}
        for name, html in pages.items():
            self.assertIn('name="viewport"', html, name)
            self.assertIn('width=device-width', html, name)
            self.assertIn('class="mobile-tabs"', html, name)
            self.assertEqual(len(re.findall(r'class="mobile-tabs"[^>]*>(.*?)</nav>', html, re.S)), 1, name)

    def test_each_match_is_linked_from_the_pick_board(self):
        open_rows = [m for m in SNAPSHOT['matches'] if m['state'] == 'open']
        self.assertGreater(len(open_rows), 0)
        for m in open_rows:
            self.assertIn(m['teams'][0], PICKS, m['id'])


class UnresolvedLimitationCopyTests(unittest.TestCase):
    """The separate unresolved section must explain each limitation class."""

    def test_limitation_classes_are_documented_in_site(self):
        html = INDEX + UNRESOLVED
        # The published limitation ladder, verbatim from the executive summary.
        for phrase in ('No book lists the match',
                       'A market exists but fails a gate',
                       'Our model needs both teams',
                       'HLTV has no usable line'):
            self.assertIn(phrase, html)

    def test_no_row_claims_a_50_50_when_nothing_was_found(self):
        for m in SNAPSHOT['matches']:
            if m.get('probabilities') is None:
                self.assertNotEqual(m.get('pick'), '50/50', m['id'])
                self.assertNotIn('50/50', m.get('reason') or '', m['id'])


if __name__ == '__main__':
    unittest.main()
