"""Session b214c818 regressions: researched listing receipts, the Aurora Young
Blud label mapping, placeholder-odds rejections, and the automated listing
re-observer (scripts/books.py).

Every expected probability here is independently de-vigged from the raw decimal
odds recorded in research/session-b214c818/captures.json; the pipeline must
reproduce exactly these numbers through scripts.core.quote_book.
"""
import copy
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts import books
from scripts.core import (
    ALIAS_MAP, book_candidate, book_research_pick, book_receipts, devig, norm,
    plain_name, quote_book, research_rank_pick,
)

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = json.loads((ROOT / 'research/session-b214c818/captures.json').read_text())
RECEIPTS_DOC = json.loads((ROOT / 'data/book-receipts.json').read_text())
IDENTITIES = json.loads((ROOT / 'data/identities.json').read_text())

EXPECTED = {  # fixture_id -> (odds, expected probabilities, expected pick)
    '1081532': ([2.05, 1.68], [0.45040214, 0.54959786], 'Leo'),
    '1081552': ([1.75, 2.00], [0.53333333, 0.46666667], 'Nemesis'),
    '1079181': ([2.23, 1.56], [0.41160950, 0.58839050], 'ex-6666'),
    '1079646': ([2.20, 1.57], [0.41644562, 0.58355438], 'ex-6666'),
    '1082157': ([1.08, 6.28], [0.85326087, 0.14673913], 'Sangal'),
}
FIXTURE_TEAMS = {
    '1081532': ['ASTRAL', 'Leo'],
    '1081552': ['Nemesis', 'Nuclear TigeRES'],
    '1079181': ['Fire Flux', 'ex-6666'],
    '1079646': ['Lavked', 'ex-6666'],
    '1082157': ['Sangal', 'Aurora YB'],
}
REJECT_IDS = ['1081130', '1079643', '1079644', '1081862', '1081863', '1081864']


def fixture_for(fixture_id, start, teams=None):
    return {
        'id': fixture_id,
        'teams': list(teams or FIXTURE_TEAMS[fixture_id]),
        'state': 'open',
        'start': start,
        'lock': None,
        'best_of': None,
        'probabilities': None,
        'fair_odds': None,
        'pick': None,
        'method': None,
        'evidence': [],
        'attempts': [],
        'flags': [],
        'reason': None,
    }


def receipt_by_fixture():
    return {r['fixture_id']: r for r in RECEIPTS_DOC['receipts']
            if r['fixture_id'] in EXPECTED}


class TestReceipts(unittest.TestCase):
    def test_five_receipts_present_with_captured_odds(self):
        found = receipt_by_fixture()
        self.assertEqual(sorted(found), sorted(EXPECTED))
        for fixture_id, (odds, _p, _pick) in EXPECTED.items():
            self.assertEqual([float(x) for x in found[fixture_id]['odds']], odds)

    def test_every_receipt_replays_to_expected_probabilities(self):
        for fixture_id, (odds, expected, _pick) in EXPECTED.items():
            receipt = receipt_by_fixture()[fixture_id]
            candidate = book_candidate(receipt)
            quote = quote_book(candidate, [0, 1], datetime(2026, 10, 19, 5, 0, tzinfo=timezone.utc))
            for got, want in zip(quote['probabilities'], expected):
                self.assertAlmostEqual(got, want, places=7, msg=fixture_id)
            # Independent recomputation from the raw odds only.
            independent = devig(odds)[0]
            for got, want in zip(independent, expected):
                self.assertAlmostEqual(got, want, places=7, msg=fixture_id)

    def test_receipt_identity_fields_are_sourced(self):
        for receipt in receipt_by_fixture().values():
            self.assertTrue(receipt['url'].startswith('https://'))
            self.assertTrue(receipt['identity_evidence'], receipt['id'])
            for item in receipt['identity_evidence']:
                self.assertTrue(item['url'].startswith('https://'), receipt['id'])
            self.assertTrue(receipt['limitation'], receipt['id'])
            self.assertEqual(receipt['provider'], 'EGamersWorld book listing')

    def test_book_research_pick_prices_each_fixture(self):
        for fixture_id, (_odds, expected, pick) in EXPECTED.items():
            receipt = receipt_by_fixture()[fixture_id]
            row = fixture_for(fixture_id, receipt['start'])
            book_research_pick(row, receipts=[receipt],
                               now=datetime(2026, 10, 19, 5, 0, tzinfo=timezone.utc))
            self.assertEqual(row['method'], 'bookmaker_fallback', fixture_id)
            self.assertEqual(row['pick'], pick, fixture_id)
            for got, want in zip(row['probabilities'], expected):
                self.assertAlmostEqual(got, want, places=7, msg=fixture_id)

    def test_researched_line_expires_after_eight_hours(self):
        """Once the observation is outside the eight-hour window the listing
        must stop pricing the row; the row drops to the documented lower tiers
        instead of keeping a stale price."""
        receipt = receipt_by_fixture()['1082157']
        row = fixture_for('1082157', receipt['start'])
        late = datetime(2026, 10, 19, 13, 0, tzinfo=timezone.utc)  # > 8h after 04:13
        book_research_pick(row, receipts=[receipt], now=late)
        self.assertIsNone(row['probabilities'], 'expired listing must not keep a price')
        self.assertIsNone(row['pick'])

    def test_post_expiry_ladder_reaches_rank_single(self):
        """With no receipt matching this fixture at all, the ladder falls to
        the one-sided ranking tier: a pick and no percentage, sourced."""
        row = fixture_for('1099999', '2026-10-20T12:00:00Z', ['Sangal', 'Aurora YB'])
        row['hltv_context'] = {
            'teams': ['Sangal', 'Aurora Young Blud'],
            'start': '2026-10-20T12:00:00Z',
            'source': 'https://www.hltv.org/matches/2399777/sangal-vs-aurora-young-blud-stake-ranked-episode-6-closed-qualifier',
            'ranks': [
                {'team': 'Sangal', 'hltv_rank': 45,
                 'source': 'https://www.hltv.org/ranking/teams/2026/october/19'},
                {'team': 'Aurora Young Blud', 'hltv_rank': None,
                 'source': 'https://www.hltv.org/ranking/teams/2026/october/19'},
            ],
            'lineups': [],
        }
        research_rank_pick(row)
        self.assertIsNone(row['probabilities'])
        self.assertEqual(row['pick'], 'Sangal')
        self.assertEqual(row['method'], 'research_rank_single')
        self.assertTrue(any('no probability' in f for f in row['flags']))
        # The identity mapping carries its primary link on the resolved row.
        loser = next(r for r in row['hltv_context']['resolved_ranks'] if r['team'] == 'Aurora YB')
        self.assertEqual(loser['hltv_name'], 'Aurora Young Blud')
        self.assertTrue(str(loser['alias_source']).startswith('https://'))

    def test_rejected_placeholders_never_price(self):
        rejected = {(r['fixture_id'], tuple(r['displayed']))
                    for r in RECEIPTS_DOC['rejected_listings']}
        for fixture_id in REJECT_IDS:
            self.assertIn((fixture_id, (1.8, 1.8)), rejected, fixture_id)
        loaded = book_receipts()
        self.assertFalse(any(r['fixture_id'] in REJECT_IDS for r in loaded))
        # And no receipt for these fixtures exists anywhere in the priced set.
        self.assertFalse(any(r['fixture_id'] in REJECT_IDS for r in RECEIPTS_DOC['receipts']))


class TestIdentity(unittest.TestCase):
    def test_aurora_yb_maps_to_aurora_young_blud(self):
        self.assertEqual(norm('Aurora YB'), norm('Aurora Young Blud'))
        self.assertEqual(norm('Aurora YB'), norm('Aurora Young Blood'))

    def test_main_aurora_is_not_mapped(self):
        self.assertNotEqual(norm('Aurora'), norm('Aurora YB'))
        self.assertNotEqual(norm('Aurora'), norm('Aurora Young Blud'))
        self.assertNotIn(plain_name('Aurora'),
                         {plain_name(n) for a in IDENTITIES['aliases']
                          if a['canonical'] == 'Aurora Young Blud' for n in a['names']})

    def test_alias_entry_is_sourced(self):
        entry = next(a for a in IDENTITIES['aliases'] if a['canonical'] == 'Aurora Young Blud')
        links = str(entry.get('source') or '') + ' ' + str(entry.get('additional_source') or '')
        self.assertIn('https://liquipedia.net/', links)
        self.assertIn('https://www.hltv.org/', links)
        self.assertIn('academy', entry['basis'])


class TestBooksReobserver(unittest.TestCase):
    HTML_OK = '''
    <html><head>
    <script type="application/ld+json">{"name":"Sangal VS Aurora Young Blud",
    "description":"Sangal VS Aurora Young Blud: Stake Ranked Episode 6 Closed Qualifier",
    "startDate":"2026-10-20T12:00:00.000Z","endDate":"2026-10-20T15:00:00.000Z",
    "homeTeam":{"name":"Sangal"},"awayTeam":{"name":"Aurora Young Blud"}}</script>
    </head><body>
    <div class="teams"><a>Sangal</a><a class="koeff">1.08</a>
    <a>Make a bet</a><a class="koeff">6.28</a><a>Aurora Young Blud</a></div>
    </body></html>
    '''
    HTML_PLACEHOLDER = HTML_OK.replace('>1.08<', '>1.8<').replace('>6.28<', '>1.8<')
    HTML_BROKEN = ('<html><body><div>no odds widget any more, only '
                   '"2026-10-20T12:00:00.000Z" and "Sangal VS Aurora Young Blud" text'
                   '</div></body></html>')

    def fixture_receipt(self):
        return copy.deepcopy(receipt_by_fixture()['1082157'])

    def test_parse_listing_binds_pair_and_start(self):
        readings = books.parse_listing(self.HTML_OK)
        self.assertEqual(len(readings), 1)
        reading = readings[0]
        self.assertEqual((reading['team1'], reading['team2']), ('Sangal', 'Aurora Young Blud'))
        self.assertEqual(reading['start'], '2026-10-20T12:00:00.000Z')
        self.assertEqual(tuple(reading['odds']), (1.08, 6.28))
        self.assertTrue(reading['bound_to_labels'])

    def test_parse_listing_refuses_placeholder_pair(self):
        self.assertEqual(books.parse_listing(self.HTML_PLACEHOLDER), [])

    def test_parse_miss_is_empty_not_a_guess(self):
        self.assertEqual(books.parse_listing(self.HTML_BROKEN), [])
        self.assertEqual(books.parse_listing(''), [])

    class StubSources:
        def __init__(self, html):
            self.html = html
            self.seen = []

        def get(self, name, url, as_json=True, headers=None):
            self.seen.append(url)
            return self.html, {'name': name, 'url': url}

    def test_reobserve_renews_only_verified_readings(self):
        receipt = self.fixture_receipt()
        before = receipt['observed_at']
        out, records = books.reobserve([receipt], self.StubSources(self.HTML_OK),
                                       datetime(2026, 10, 19, 6, 0, tzinfo=timezone.utc))
        self.assertEqual(records[0]['status'], 'renewed')
        self.assertEqual(out[0]['observed_at'], '2026-10-19T06:00:00Z')
        self.assertEqual(out[0]['odds'], [1.08, 6.28])
        self.assertNotEqual(out[0]['observed_at'], before)
        # The committed research record is never mutated in place.
        self.assertEqual(receipt['observed_at'], before)

    def test_reobserve_leaves_receipt_stale_on_placeholder_or_markup_change(self):
        for html in (self.HTML_PLACEHOLDER, self.HTML_BROKEN):
            receipt = self.fixture_receipt()
            out, records = books.reobserve([receipt], self.StubSources(html),
                                           datetime(2026, 10, 19, 6, 0, tzinfo=timezone.utc))
            self.assertEqual(records[0]['status'], 'parse_miss')
            self.assertEqual(out[0]['observed_at'], receipt['observed_at'])

    def test_reobserve_refuses_a_different_start(self):
        receipt = self.fixture_receipt()
        html = self.HTML_OK.replace('2026-10-20T12:00:00.000Z', '2026-10-20T13:00:00.000Z')
        out, records = books.reobserve([receipt], self.StubSources(html),
                                       datetime(2026, 10, 19, 6, 0, tzinfo=timezone.utc))
        self.assertEqual(records[0]['status'], 'parse_miss')
        self.assertEqual(out[0]['observed_at'], receipt['observed_at'])

    def test_reobserve_records_access_errors(self):
        class Failing(self.StubSources):
            def get(self, name, url, as_json=True, headers=None):
                raise ValueError('HTTP 403 rate limit')

        receipt = self.fixture_receipt()
        out, records = books.reobserve([receipt], Failing(None),
                                       datetime(2026, 10, 19, 6, 0, tzinfo=timezone.utc))
        self.assertEqual(records[0]['status'], 'error')
        self.assertEqual(out[0]['observed_at'], receipt['observed_at'])


class TestRegisters(unittest.TestCase):
    def test_capture_decisions_match_registers(self):
        # Every accepted capture must be represented on file by its fixture and
        # pair; parallel sessions may hold the receipt under their own capture
        # id (e.g. the Sangal read), and duplicate fixture lines are refused.
        accepts = {c['fixture_id'] for c in CAPTURES['accepts']}
        rejects = {(c['fixture_id'], c['observed_at']) for c in CAPTURES['rejects']}
        have_ids = [r['id'] for r in RECEIPTS_DOC['receipts']]
        self.assertEqual(len(have_ids), len(set(have_ids)), 'duplicate receipt ids')
        for receipt in RECEIPTS_DOC['receipts']:
            self.assertFalse([r['id'] for r in RECEIPTS_DOC['receipts']
                              if r is not receipt and r['fixture_id'] == receipt['fixture_id']
                              and list(map(float, r['odds'])) == list(map(float, receipt['odds']))],
                             'duplicate listing pair for fixture ' + str(receipt['fixture_id']))
        self.assertTrue(accepts <= {r['fixture_id'] for r in RECEIPTS_DOC['receipts']})
        have_rejects = {(r['fixture_id'], r['observed_at'])
                        for r in RECEIPTS_DOC['rejected_listings']}
        self.assertTrue(rejects <= have_rejects)

    def test_review_notes_flag_all_findings(self):
        notes = json.loads((ROOT / 'data/review-notes.json').read_text())
        have = {n['id'] for n in notes}
        for note_id in ('b214c818-default-odds-rejections',
                        'b214c818-rare-atom-alter-ego-conflict', 'b214c818-book-line-upgrades'):
            self.assertIn(note_id, have)
        # The identity finding is published once, by the parallel session that
        # first registered the mapping; this session's evidence is in captures.
        self.assertIn('aurora-yb-alias-133fe7ca', have)
        entry = next(n for n in notes if n['id'] == 'b214c818-rare-atom-alter-ego-conflict')
        self.assertTrue(all(s['url'].startswith('https://') for s in entry['sources']))

    def test_applier_is_idempotent(self):
        import scripts.session_b214c818 as applier
        before = (len(RECEIPTS_DOC['receipts']),
                  len(RECEIPTS_DOC['rejected_listings']),
                  len(IDENTITIES['aliases']),
                  len(json.loads((ROOT / 'data/review-notes.json').read_text())))
        applier.main()
        after_doc = json.loads((ROOT / 'data/book-receipts.json').read_text())
        after = (len(after_doc['receipts']),
                 len(after_doc['rejected_listings']),
                 len(json.loads((ROOT / 'data/identities.json').read_text())['aliases']),
                 len(json.loads((ROOT / 'data/review-notes.json').read_text())))
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
