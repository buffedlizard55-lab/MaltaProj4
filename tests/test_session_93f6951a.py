"""Regression tests for session 93f6951a's independent verifier.

The verifier lives in ``verification-93f6951a/verify_board.py`` and shares no code
with ``scripts/``. These tests pin three things:

1. it passes on the committed board and on every future board (no snapshot value
   is hard-coded, so a refresh cannot turn the suite red by itself);
2. it actually fails on each class of corruption, so a green run means something;
3. it fails when a published page loses an internal anchor, loses an open row, or
   a row loses its outbound official source link.
"""
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('verify_board_93f6951a',
                                              REPO / 'verification-93f6951a' / 'verify_board.py')
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


class CommittedBoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads((REPO / 'data/latest.json').read_text())

    def test_every_committed_row_verifies(self):
        verifier = verify.SiteVerifier(REPO, verify.load_identities(str(REPO / 'data/identities.json')))
        for row in self.snapshot['matches']:
            verifier.verify_row(row)
        verifier.verify_site(self.snapshot)
        self.assertEqual(verifier.failures, [],
                         'the committed board must re-derive with no failures: %s'
                         % verifier.failures[:5])
        self.assertGreater(verifier.checks, 1000)

    def test_every_open_row_has_a_pick_and_a_probability(self):
        opens = [r for r in self.snapshot['matches'] if r.get('state') == 'open']
        self.assertTrue(opens, 'the committed snapshot must contain at least one open fixture')
        for row in opens:
            self.assertTrue(row.get('pick'), 'open row %s has no pick' % row['id'])
            self.assertEqual(len(row.get('probabilities') or []), 2,
                             'open row %s has no two-sided probability' % row['id'])
            self.assertEqual(row['probabilities'][0] + row['probabilities'][1], 1.0,
                             'open row %s probabilities do not sum to 1' % row['id'])


class CorruptionTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads((REPO / 'data/latest.json').read_text())
        self.priced = [r for r in self.snapshot['matches']
                       if r.get('state') == 'open' and r.get('probabilities')]
        if not self.priced:
            self.skipTest('no priced open row to corrupt')

    def failures_after(self, mutate):
        import copy
        bad = copy.deepcopy(self.snapshot)
        target = [r for r in bad['matches'] if r['id'] == self.priced[0]['id']][0]
        mutate(target)
        verifier = verify.RowVerifier(verify.load_identities(str(REPO / 'data/identities.json')))
        for row in bad['matches']:
            verifier.verify_row(row)
        return verifier.failures

    def test_pick_outside_the_two_teams_is_refused(self):
        self.assertTrue(self.failures_after(lambda r: r.__setitem__('pick', 'Not A Team')))

    def test_probabilities_that_do_not_sum_to_one_are_refused(self):
        self.assertTrue(self.failures_after(
            lambda r: r.__setitem__('probabilities', [r['probabilities'][0] - 0.02, r['probabilities'][1]])))

    def test_a_pick_against_the_price_is_refused(self):
        def flip(row):
            row['pick'] = row['teams'][1] if row['pick'] == row['teams'][0] else row['teams'][0]
        self.assertTrue(self.failures_after(flip))

    def test_a_tampered_price_is_refused(self):
        def tamper(row):
            evidence = row['evidence'][0]
            raw = evidence.get('raw') or {}
            if isinstance(raw.get('outcomePrices'), str):
                prices = json.loads(raw['outcomePrices'])
                prices[0] = str(float(prices[0]) * 1.05)
                raw['outcomePrices'] = json.dumps(prices)
                row['probabilities'] = list(reversed(row['probabilities']))
            elif evidence.get('points'):
                evidence['points'] = [evidence['points'][0] + 40, evidence['points'][1]]
            else:
                self.skipTest('module %r has no locally tamperable input' % row.get('method'))
        self.assertTrue(self.failures_after(tamper))

    def test_a_row_with_no_official_source_is_refused(self):
        def strip(row):
            row['source_url'] = ''
            row['evidence'] = []
            row['fixture_sources'] = []
            row['attempts'] = []
        self.assertTrue(self.failures_after(strip))

    def test_an_expiry_after_kick_off_is_refused(self):
        self.assertTrue(self.failures_after(lambda r: r.__setitem__('expires_at', r['start'])))

    def test_a_row_with_no_pick_and_no_reason_is_refused(self):
        def blank(row):
            row.update({'pick': None, 'probabilities': None, 'fair_odds': None,
                        'method': None, 'reason': '', 'attempts': []})
        self.assertTrue(self.failures_after(blank))

    def test_an_unlabelled_research_pick_is_refused(self):
        def unlabel(row):
            row.update({'probabilities': None, 'fair_odds': None, 'method': None})
        self.assertTrue(self.failures_after(unlabel))

    def test_plain_http_is_refused(self):
        self.assertTrue(self.failures_after(
            lambda r: r.__setitem__('source_url', 'http://play.hotspawn.com/cs2-pickems')))

    def test_self_test_catches_every_case(self):
        caught = verify.selftest(self.snapshot)
        self.assertEqual(set(caught.values()), {True}, caught)


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for path in REPO.glob('*.html'):
            shutil.copy(path, self.tmp / path.name)
        self.snapshot = json.loads((REPO / 'data/latest.json').read_text())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_site(self):
        verifier = verify.SiteVerifier(self.tmp, verify.load_identities(str(REPO / 'data/identities.json')))
        verifier.verify_site(self.snapshot)
        return verifier

    def test_a_broken_internal_anchor_is_refused(self):
        page = self.tmp / 'index.html'
        page.write_text(page.read_text().replace('href="#picks-at-a-glance"',
                                                 'href="#picks-at-a-glance-missing"'))
        failures = self.run_site().failures
        self.assertTrue([f for f in failures if f['code'] == 'S3'],
                        'a missing anchor must fail the site check')

    def test_a_missing_open_row_on_the_board_is_refused(self):
        first = [r for r in self.snapshot['matches'] if r.get('state') == 'open'][0]['id']
        page = self.tmp / 'picks.html'
        page.write_text(page.read_text().replace('data-match="%s"' % first, 'data-match="removed"'))
        failures = self.run_site().failures
        self.assertTrue([f for f in failures if f['code'] == 'S1' and f['row'] == str(first)])

    def test_an_open_row_missing_from_the_summary_is_refused(self):
        first = [r for r in self.snapshot['matches'] if r.get('state') == 'open'][0]['id']
        page = self.tmp / 'index.html'
        text = page.read_text().replace(str(first), '0000000')
        page.write_text(text)
        failures = self.run_site().failures
        self.assertTrue([f for f in failures if f['code'] == 'S1' and f['row'] == str(first)])


if __name__ == '__main__':
    unittest.main()
