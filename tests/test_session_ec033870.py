"""Session ec033870 — a sourced pick for every row the Hotspawn feed returns.

The requirement is a pick for every CS2 match listed on Hotspawn. The committed
snapshot had 29 open rows, all priced, and 63 rows with nothing at all: their
own sourced lock or start predates the snapshot, so ``scripts.build`` withdraws
``pick``/``probabilities``/``fair_odds``/``method`` and two independent audits
(``scripts/audit_9b97d585.py``, ``scripts/audit_cecfe864.py``) fail any not-open
row that carries one. Those audits are correct and are kept, so the resolved
value lives in a separate ``historical`` block and these tests hold both halves
of the contract:

* the live fields on a not-open row stay blank; and
* the historical block is not a place a number can be typed by hand — every
  tier, pick and probability is re-derived here from the vendored copies of
  Valve's official standings, and eight separate corruptions are caught.
"""
import json
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import historical, vrs, vrs_history
from scripts.build import build, has_past_picks, historical_section, past_coverage_sentence
from scripts.core import dt
from scripts.validate import validate_historical, validate_site

ROOT = Path(__file__).resolve().parents[1]


def snapshot():
    return json.loads((ROOT / 'data' / 'latest.json').read_text())


class DatedStandingsSelectionTests(unittest.TestCase):
    """A past fixture is priced from the ranking that was current for it."""

    @classmethod
    def setUpClass(cls):
        cls.history = vrs_history.load()

    def test_the_vendored_copies_are_official_and_checksum_verified(self):
        self.assertTrue(self.history, 'no dated Valve standings are vendored')
        index = json.loads((ROOT / 'data' / 'vrs' / 'history.json').read_text())
        self.assertEqual(index['repository'], 'ValveSoftware/counter-strike_regional_standings')
        for entry in index['files']:
            raw = (ROOT / 'data' / 'vrs' / 'history' / entry['file']).read_bytes()
            standings = vrs.parse(raw.decode())
            self.assertEqual(standings['as_of'], entry['as_of'])
            self.assertEqual(len(standings['teams']), entry['teams'])
            self.assertIn('github.com/ValveSoftware/counter-strike_regional_standings', entry['blob_url'])
            self.assertIn(entry['commit'], entry['blob_url'])

    def test_a_tampered_copy_is_refused_not_silently_used(self):
        path = ROOT / 'data' / 'vrs' / 'history' / self.history[0][1]['file']
        original = path.read_bytes()
        try:
            path.write_bytes(original.replace(b'|', b' ', 1))
            with self.assertRaises(ValueError):
                vrs_history.load()
        finally:
            path.write_bytes(original)
        self.assertTrue(vrs_history.load(), 'the restored copy must load again')

    def test_the_newest_file_on_or_before_the_start_wins(self):
        dates = sorted(s['as_of'] for s, _ in self.history)
        self.assertGreaterEqual(len(dates), 3)
        for as_of, meta in ((s['as_of'], m) for s, m in self.history):
            standings, chosen, note = vrs_history.select(as_of + 'T12:00:00Z', self.history)
            self.assertEqual(chosen['file'], meta['file'])
            self.assertIsNone(note, 'an exact-dated fixture never needs the fallback wording')

    def test_a_fixture_newer_than_every_file_uses_the_newest(self):
        standings, chosen, note = vrs_history.select('2099-01-01T00:00:00Z', self.history)
        self.assertEqual(chosen['file'], self.history[-1][1]['file'])
        self.assertIsNone(note)

    def test_a_fixture_older_than_every_file_says_so_instead_of_hiding_it(self):
        standings, chosen, note = vrs_history.select('1999-01-01T00:00:00Z', self.history)
        self.assertEqual(chosen['file'], self.history[0][1]['file'])
        self.assertIn('predates every vendored copy', note)


class HistoricalLadderTests(unittest.TestCase):
    """Each tier publishes exactly what its evidence supports."""

    @classmethod
    def setUpClass(cls):
        cls.history = vrs_history.load()
        cls.data = snapshot()
        cls.past = [m for m in cls.data['matches'] if m.get('state') != 'open']

    def test_the_committed_snapshot_resolves_every_not_open_row(self):
        self.assertTrue(self.past, 'the committed snapshot has no non-open row to test')
        for m in self.past:
            block = m.get('historical')
            self.assertIsNotNone(block, 'row %s has no historical block' % m['id'])
            self.assertIn(block['status'],
                          ('model_vrs', 'research_vrs_single', 'research_vrs_invariant', 'unresolved'))
            self.assertTrue(block['not_a_current_pick'])
            self.assertTrue(block['reason'])
            self.assertTrue(block['attempts'])
            # The contract the two existing audits exist to protect.
            for field in ('pick', 'probabilities', 'fair_odds', 'method'):
                self.assertIsNone(m.get(field), 'row %s carries a live %s' % (m['id'], field))

    def test_no_open_row_carries_a_historical_block(self):
        for m in self.data['matches']:
            if m.get('state') == 'open':
                self.assertNotIn('historical', m, 'open row %s' % m['id'])

    def test_every_published_number_is_valves_own_formula(self):
        priced = [m for m in self.past if m['historical']['status'] == 'model_vrs']
        self.assertTrue(priced, 'no model-tier row to verify')
        for m in priced:
            quote = m['historical']['evidence'][0]
            raw = vrs.expected(*quote['points'])
            expected = [vrs.calibrated(raw), 1 - vrs.calibrated(raw)]
            for published, derived in zip(m['historical']['probabilities'], expected):
                self.assertAlmostEqual(published, derived, places=12)
            self.assertAlmostEqual(sum(m['historical']['probabilities']), 1.0, places=12)
            self.assertEqual(m['historical']['pick'],
                             m['teams'][0 if expected[0] > expected[1] else 1])

    def test_the_non_model_tiers_publish_no_number(self):
        for m in self.past:
            block = m['historical']
            if block['status'] != 'model_vrs':
                self.assertIsNone(block['probabilities'])
                self.assertIsNone(block['fair_odds'])

    def test_the_invariant_tier_fails_closed_when_the_favourite_flips(self):
        """Acend vs Infinite is the measured counter-example, not a synthetic one.

        Valve's 2026-06-01 file lists Infinite twice — #48 with 1269 points and
        #287 with 586 — while Acend sits at #61 with 1200. Against the first
        Infinite, Acend is the underdog; against the second, the favourite. So
        no direction is publishable and the row must stay unresolved.
        """
        row = next((m for m in self.past if str(m['id']) == '1051339'), None)
        if row is None:
            self.skipTest('fixture 1051339 is no longer in the retained feed')
        standings, meta, _ = vrs_history.select(row['start'], self.history)
        resolved, why = historical._invariant({'teams': row['teams']}, standings, meta)
        self.assertIsNone(resolved)
        self.assertIn('favourite flips', why)
        self.assertEqual(row['historical']['status'], 'unresolved')
        self.assertIsNone(row['historical']['pick'])

    def test_the_invariant_tier_publishes_only_a_direction_that_survives(self):
        row = next((m for m in self.past if m['historical']['status'] == 'research_vrs_invariant'), None)
        if row is None:
            self.skipTest('no roster-invariant row in this snapshot')
        spread = row['historical']['invariant']['candidates']
        self.assertGreaterEqual(len(spread), 2, 'the tier only exists for a repeated label')
        for candidate in spread:
            favoured = candidate['probability_for_unique_side'] > 0.5
            self.assertEqual(row['historical']['pick'],
                             row['historical']['invariant']['unique_side'] if favoured
                             else row['historical']['invariant']['ambiguous_label'])

    def test_validate_reproduces_every_row_and_catches_corruptions(self):
        report = validate_historical(json.loads(json.dumps(self.data)))
        self.assertEqual(report['historical_rows_present'], len(self.past))
        self.assertEqual(report['historical_rows_reproduced'], len(self.past))
        cases = (
            ('a rewritten probability', self._tamper_probability),
            ('a rewritten pick', self._tamper_pick),
            ('a rewritten tier', self._tamper_tier),
            ('the wrong standings file', self._tamper_file),
            ('a number on a research tier', self._invent_number),
            ('a pick on an unresolved row', self._invent_pick),
            ('a doctored coverage count', self._tamper_counts),
            ('a live pick on a not-open row', self._tamper_live_pick),
        )
        for label, mutate in cases:
            broken = json.loads(json.dumps(self.data))
            mutate(broken)
            with self.assertRaises(AssertionError, msg=label):
                validate_historical(broken)

    # --- corruption helpers, each changing exactly one published value -------
    @staticmethod
    def _first(doc, status):
        row = next((m for m in doc['matches']
                    if m.get('state') != 'open' and m['historical']['status'] == status), None)
        if row is None:
            raise unittest.SkipTest('this snapshot has no %s row to corrupt' % status)
        return row

    def _tamper_probability(self, doc):
        row = self._first(doc, 'model_vrs')
        row['historical']['probabilities'] = [0.5, 0.5]

    def _tamper_pick(self, doc):
        row = self._first(doc, 'model_vrs')
        row['historical']['pick'] = row['teams'][1] if row['historical']['pick'] == row['teams'][0] else row['teams'][0]

    def _tamper_tier(self, doc):
        row = self._first(doc, 'research_vrs_single')
        row['historical']['status'] = 'model_vrs'

    def _tamper_file(self, doc):
        row = self._first(doc, 'model_vrs')
        other = next(f for f in json.loads((ROOT / 'data' / 'vrs' / 'history.json').read_text())['files']
                     if f['file'] != row['historical']['standings_file'])
        row['historical']['standings_file'] = other['file']

    def _invent_number(self, doc):
        row = self._first(doc, 'research_vrs_single')
        row['historical']['probabilities'] = [0.5, 0.5]

    def _invent_pick(self, doc):
        row = self._first(doc, 'unresolved')
        row['historical']['pick'] = row['teams'][0]

    def _tamper_counts(self, doc):
        doc['historical_coverage']['counts']['unresolved'] += 1

    def _tamper_live_pick(self, doc):
        row = next(m for m in doc['matches'] if m.get('state') != 'open')
        row['pick'] = row['teams'][0]


class RenderedSiteTests(unittest.TestCase):
    """The board shows a labelled value for every row, and says where it is."""

    @classmethod
    def setUpClass(cls):
        cls.data = snapshot()
        cls.tmp = tempfile.TemporaryDirectory()
        build(json.loads(json.dumps(cls.data)), cls.tmp.name, now=dt(cls.data['generated_at']))
        cls.root = Path(cls.tmp.name)
        cls.index = (cls.root / 'index.html').read_text(encoding='utf-8')
        cls.matches = (cls.root / 'matches.html').read_text(encoding='utf-8')
        cls.unresolved = (cls.root / 'unresolved.html').read_text(encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_built_site_reproduces_the_published_historical_values(self):
        report = validate_site(self.root)
        self.assertGreaterEqual(report['historical_rows_reproduced'], 1)

    def test_every_past_row_renders_a_labelled_value_and_no_live_pick(self):
        soup = BeautifulSoup(self.matches, 'html.parser')
        past_ids = {str(m['id']) for m in self.data['matches'] if m.get('state') != 'open'}
        self.assertTrue(past_ids)
        for row in soup.select('tr[data-match]'):
            if row['data-match'] not in past_ids:
                continue
            block = next(m for m in self.data['matches'] if str(m['id']) == row['data-match'])['historical']
            self.assertIn('Past fixture', row.get_text(' ', strip=True))
            if block.get('pick'):
                self.assertEqual(row.select_one('.hist-pick').get_text(), block['pick'])
            else:
                self.assertIsNone(row.select_one('.hist-pick'))
            # The classes the validator reserves for actionable recommendations.
            self.assertIsNone(row.select_one('.pick-cell .pick'))
            self.assertEqual(row.select('.prob-pair'), [])

    def test_the_executive_summary_counts_the_resolved_rows_and_links_them(self):
        soup = BeautifulSoup(self.index, 'html.parser')
        coverage = self.data['historical_coverage']
        text = soup.get_text(' ', strip=True)
        self.assertIn('%d of %d' % (coverage['resolved'], coverage['counts']['rows']), text)
        section = soup.find(id='past-picks')
        self.assertIsNotNone(section, 'the executive summary must contain the past-fixture section')
        hrefs = {a.get('href') for a in soup.select('a[href]')}
        self.assertIn('#past-picks', hrefs)
        self.assertIn('unresolved.html#past-unresolved', hrefs)
        self.assertIn('picks.html', hrefs)

    def test_the_limitations_are_published_verbatim_on_the_page(self):
        text = BeautifulSoup(self.index, 'html.parser').get_text(' ', strip=True)
        for limitation in self.data['historical_coverage']['limitations']:
            self.assertIn(' '.join(limitation.split())[:70], ' '.join(text.split()))

    def test_the_unresolved_page_names_every_row_it_could_not_resolve(self):
        soup = BeautifulSoup(self.unresolved, 'html.parser')
        section = soup.find(id='past-unresolved')
        self.assertIsNotNone(section)
        text = section.get_text(' ', strip=True)
        for entry in self.data['historical_coverage']['unresolved']:
            self.assertIn(' vs '.join(entry['teams']), text)

    def test_a_snapshot_without_past_rows_publishes_no_dead_anchor(self):
        data = json.loads(json.dumps(self.data))
        for m in data['matches']:
            m['state'] = 'open'
        data.pop('historical_coverage', None)
        self.assertFalse(has_past_picks(data))
        self.assertEqual(historical_section(data), '')
        self.assertNotIn('#past-picks', past_coverage_sentence(data))

    def test_the_csv_exports_the_research_value_beside_the_blank_live_fields(self):
        import csv
        with (self.root / 'data' / 'matches.csv').open() as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), len(self.data['matches']))
        exported = 0
        for row in rows:
            match = next(m for m in self.data['matches'] if str(m['id']) == row['hotspawn_id'])
            block = match.get('historical') or {}
            self.assertEqual(row['past_fixture_pick'], block.get('pick') or '')
            self.assertEqual(row['past_fixture_tier'], block.get('status') or '')
            if match.get('state') != 'open':
                self.assertEqual(row['pick'], '', 'a past row must not export a live pick')
                self.assertEqual(row['p_team_1'], '')
            if block.get('probabilities'):
                exported += 1
                self.assertAlmostEqual(float(row['past_fixture_p_team_1']), block['probabilities'][0], places=10)
        self.assertGreater(exported, 0)


if __name__ == '__main__':
    unittest.main()
