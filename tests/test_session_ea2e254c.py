"""Session ea2e254c: tall-phone layout and sourced-alias re-derivation, pinned.

Measured on this session's base ``dce494b``: ``python -m unittest discover -s tests``
returned 8 failures / 1 error, and ``pages.yml`` runs that suite *before* it
refreshes sources, so no scheduled run ever published. Two defects:

1. The served root stylesheet ``assets/style.css`` had drifted from
   ``site/assets/style.css`` and was missing one closing brace, so the
   ``@media(max-width:650px) and (max-height:700px)`` block swallowed the rest of
   the file - every later phone rule then applied only on viewports shorter than
   700 px, and at 390x844 the phone layout was simply not in effect. Main now
   pins brace **balance** (tests/test_session_174afa4f.py). Balance alone does not
   prevent the *semantic* regression: a rule may sit, balanced, inside a
   ``max-height`` query and tall phones still lose it. The tests below assert the
   enclosing at-rule for the specific phone-ordering selectors, and that the
   served copy is the same bytes as the canonical one.

2. The independent re-derivation refused fixture 1083121 because Polymarket
   labels the club ``Tropa do KinGui`` where Hotspawn says ``Projeto do KinGui``.
   The row carries a reviewed, HLTV-sourced alias. These tests hold the alias
   path to its evidence: only an https source that names **both** labels
   verbatim may map a source outcome onto a team, and a tampered price on that
   row must still be rejected.
"""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())
SERVED_CSS = (ROOT / 'assets' / 'style.css').read_text()
SITE_CSS = (ROOT / 'site' / 'assets' / 'style.css').read_text()


def load_verifier():
    spec = importlib.util.spec_from_file_location(
        'verify_ea2e254c', ROOT / 'research' / 'session-0cc1138a' / 'verify_0cc1138a.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load_verifier()


def enclosing_at_rules(css, selector):
    """At-rule preludes enclosing every rule whose selector matches ``selector``.

    A brace-depth walk, deliberately not a CSS parser: it keeps the stack of
    ``@media`` preludes open at each depth and records the stack in force where
    the selector starts a rule.
    """
    found = []
    stack, buf = [], ''
    for ch in css:
        if ch == '{':
            prelude = buf.strip()
            buf = ''
            if prelude.startswith('@'):
                stack.append(prelude)
            else:
                if stack and selector in prelude:
                    found.append(list(stack))
                stack.append('')
        elif ch == '}':
            if stack:
                stack.pop()
            buf = ''
        else:
            buf += ch
    return found


class PhoneLayoutSurvivesATallPhone(unittest.TestCase):
    def test_served_and_canonical_stylesheets_are_the_same_bytes(self):
        self.assertEqual(SERVED_CSS, SITE_CSS,
                         'assets/style.css (served by the root pages) must equal '
                         'site/assets/style.css (copied into the published artifact)')

    def test_phone_ordering_is_not_nested_in_a_short_viewport_query(self):
        # 390x844 is taller than 700px; these selectors carry the phone layout.
        for selector in ('body[data-page="index"] main>#picks-at-a-glance',
                         'body[data-page="index"] main>#exec-summary',
                         'body[data-page="index"] main>.page-head',
                         'body[data-page=picks] main>.table-wrap'):
            contexts = enclosing_at_rules(SERVED_CSS, selector)
            self.assertTrue(contexts, '%s is not styled at all' % selector)
            for stack in contexts:
                self.assertNotIn('max-height', ' '.join(stack),
                                 '%s only applies on short viewports: %r' % (selector, stack))

    def test_the_phone_ordering_applies_at_a_tall_phone(self):
        contexts = enclosing_at_rules(SERVED_CSS, 'body[data-page="index"] main>#exec-summary')
        self.assertTrue(any('max-width:650px' in ' '.join(s) for s in contexts),
                        'the summary ordering must apply at phone widths, not only short ones')


class AliasedExchangeRowStillReproduces(unittest.TestCase):
    ROW_ID = '1083121'

    def row(self, row_id=None):
        row_id = row_id or self.ROW_ID
        rows = [m for m in SNAPSHOT['matches'] if m['id'] == row_id]
        if not rows:
            # The board rotates: fixtures lock and leave the feed. The invariants
            # below are about how an aliased exchange row is verified, not about
            # one fixture staying open, so a rotated row is skipped rather than
            # pinned (a pinned ID is what froze earlier pipelines).
            self.skipTest('fixture %s has rotated out of the feed' % row_id)
        return rows[0]

    def test_the_row_ships_its_alias_evidence(self):
        ev = self.row()['evidence'][0]
        entries = ev.get('identity_sources') or []
        self.assertTrue(entries, 'the aliased row must ship its identity evidence')
        self.assertTrue(any(str(e.get('source', '')).startswith('https://') for e in entries))
        names = {n for e in entries for n in e.get('names', [])}
        self.assertIn('Tropa do KinGui', names)
        self.assertIn('Projeto do KinGui', names)

    def test_alias_groups_require_https_source_basis_and_a_committed_entry(self):
        # Full tightened contract (sessions 174afa4f / a30d31a0 / cecfe864): a
        # source label may map onto a fixture label only through a register entry
        # that (a) carries an https source, (b) carries a written basis, and
        # (c) matches a group committed in data/identities.json.
        registry = json.loads((ROOT / 'data' / 'identities.json').read_text())['aliases']
        entry = next(a for a in registry if 'Tropa do KinGui' in a['names'])
        good = {'identity_sources': [{'source': entry['source'],
                                      'names': entry['names'],
                                      'basis': entry['basis']}]}
        self.assertEqual(len(V.alias_groups(good)), 1)
        # No written basis: refused.
        self.assertEqual(V.alias_groups({'identity_sources': [
            {'source': entry['source'], 'names': entry['names']}]}), [])
        # Non-https source: refused.
        self.assertEqual(V.alias_groups({'identity_sources': [
            {'source': 'http://insecure.example/x', 'names': entry['names'],
             'basis': entry['basis']}]}), [])
        # https + basis but a pair no committed registry entry names: refused.
        self.assertEqual(V.alias_groups({'identity_sources': [
            {'source': 'https://example.org/alias', 'names': ['Alpha One', 'Beta Two'],
             'basis': 'synthetic'}]}), [])

    def test_an_unregistered_label_is_still_refused(self):
        ev = {'identity_sources': [{'source': 'https://example.org/alias',
                                    'names': ['Tropa do KinGui', 'Projeto do KinGui']}]}
        with self.assertRaises(ValueError):
            V.order_prices(['Tropa do KinGui', 'MEIA NOITE'], [0.615, 0.385],
                           ['Someone Else', 'MEIA NOITE'], ev)

    def test_the_alias_maps_the_source_order_onto_the_fixture(self):
        ev = self.row()['evidence'][0]
        prices = V.order_prices(['MEIA NOITE', 'Tropa do KinGui'], [0.385, 0.615],
                                ['Projeto do KinGui', 'MEIA NOITE'], ev)
        self.assertEqual(prices, [0.615, 0.385])

    def test_the_published_number_is_rebuilt_from_the_aliased_source(self):
        row = self.row()
        prices, kind = V.evidence_probabilities(row['evidence'][0], row['teams'])
        self.assertEqual(kind, 'exchange_mid')
        for published, rebuilt in zip(row['probabilities'], prices):
            self.assertAlmostEqual(published, rebuilt, places=9)

    def test_a_tampered_price_on_an_aliased_row_is_still_rejected(self):
        # Any open row priced through a source label that only resolves via its
        # alias register, or the canonical KinGui row when it is still listed.
        candidates = [m for m in SNAPSHOT['matches']
                      if m['state'] == 'open' and m.get('probabilities')
                      and (m.get('evidence') or [{}])[0].get('identity_sources')]
        if not candidates:
            self.skipTest('no open row currently carries an alias register')
        row = candidates[0]
        doc = copy.deepcopy(SNAPSHOT)
        target = next(m for m in doc['matches'] if m['id'] == row['id'])
        target['probabilities'] = [target['probabilities'][1], target['probabilities'][0]]
        target['pick'] = target['teams'][1]
        failures = [r for r in V.audit(doc) if r['problems']]
        self.assertIn(row['id'], [r['id'] for r in failures])
        blob = ' '.join(p for r in failures if r['id'] == row['id'] for p in r['problems'])
        self.assertIn('re-derived', blob)


class BoardStillAnswersTheBrief(unittest.TestCase):
    """Every open match has a pick, a win probability and an official source;
    the executive summary links the board and the limitations section in-site;
    every page declares a mobile viewport."""

    def test_every_open_row_is_picked_priced_and_sourced(self):
        open_rows = [m for m in SNAPSHOT['matches'] if m['state'] == 'open']
        self.assertTrue(open_rows)
        for m in open_rows:
            self.assertIsNotNone(m.get('pick'), m['id'])
            self.assertIn(m['pick'], m['teams'], m['id'])
            self.assertEqual(len(m.get('probabilities') or []), 2, m['id'])
            self.assertAlmostEqual(sum(m['probabilities']), 1, places=9)
            self.assertEqual(m['pick'],
                             m['teams'][m['probabilities'].index(max(m['probabilities']))], m['id'])
            self.assertTrue(str(m.get('source_url', '')).startswith('https://'), m['id'])
            ev = (m.get('evidence') or [{}])[0]
            self.assertTrue(ev.get('url') or ev.get('api_url'), m['id'])

    def test_no_probability_comes_from_hotspawn(self):
        for m in SNAPSHOT['matches']:
            for ev in m.get('evidence') or []:
                blob = json.dumps(ev).lower()
                self.assertNotIn('picked_percent', blob, m['id'])

    def test_the_unresolved_section_and_index_links_are_published(self):
        index = (ROOT / 'index.html').read_text()
        for anchor in ('id="exec-summary"', 'id="unresolved-summary"', 'id="pick-limitations"',
                       'href="picks.html"', 'href="unresolved.html"', 'href="matches.html"',
                       'href="review.html"'):
            self.assertIn(anchor, index)
        self.assertIn('Limitations for generating these picks', index)

    def test_every_page_declares_a_mobile_viewport(self):
        for page in ('index.html', 'picks.html', 'matches.html', 'unresolved.html',
                     'analysis.html', 'review.html', 'sources.html', 'evidence.html'):
            html = (ROOT / page).read_text()
            self.assertIn('name="viewport"', html, page)
            self.assertIn('width=device-width', html, page)


if __name__ == '__main__':
    unittest.main()
