"""Session 019a253a: every listed match must resolve to a pick, and the
publication pipeline must not be stopped by a rotated board.

What this suite proves, and why
-------------------------------
1. **The scheduled pipeline was down for ~16 hours and nothing said so.** The
   unit gate runs before refresh/build/deploy in
   `.github/workflows/pages.yml`, and one snapshot-coupled assertion
   (`tests/test_session_0cc1138a.py::LiveHotspawnCoverage`) raised
   ``KeyError: '1079655'`` once those 23 October fixtures left Hotspawn's
   ``status=scheduled`` feed. Every scheduled run since then failed at that
   step, so the public board froze and then withheld every pick when its
   eight-hour window closed. The fix pins the historical parity contract to
   the retained archive instead of the rotating `data/latest.json`; the guards
   below keep the contract honest in both directions.

2. **"Every match has a pick" is a test, not a sentence.** The coverage audit
   (`scripts.audit_f89bb1f8`) is replayed here against the committed snapshot
   at the snapshot's own clock: every fixture whose lock and start are still
   future must be open, name one of its two teams, and either publish two
   probabilities summing to 1 with the better side picked, or be explicitly
   labelled research-only with no numbers. An unresolved row must publish its
   reason, an attempted provider and an https source. The audit is also run
   against a board advanced 30 days, which is what a rotation looks like, so a
   future refresh cannot fail this suite for the wrong reason.

3. **The fallback ladder is published, with counts, in the executive summary.**
   The separate unresolved section now states every rung in the order
   `scripts.refresh` tries it (exchange → HLTV → Pinnacle → wide exchange →
   esportsbook listing → our Valve-standings model → research-only) with the
   number of open rows this snapshot resolved at each rung, generated from the
   snapshot's own methods. Nothing on that line is typed by hand.

4. **No probability may originate on Hotspawn.** Hotspawn supplies fixture
   inventory and locks only; the evidence URL behind every published
   percentage must be an external operator, an external listing or Valve/HLTV
   rating data.

5. **Every published method is classified everywhere.** A pick method that one
   registry knows and another does not is how a row gets mislabelled in the
   summary or falsely failed by an auditor, so the registries are compared
   against each other.
"""
import copy
import json
import re
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from scripts import audit_f89bb1f8, build, summary
from scripts.build import overview, unresolved_limits_card
from tests.test_session_0cc1138a import archived_coverage_problems

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())

# Session a22008ff (2026-10-24): see the note in test_session_d2b90de7.py. Fixture
# 1083121 rotated out of Hotspawn's lobby, so this alias replay now reads the
# repository's own retained capture of the board while the row was open. A row
# missing from both places is a failure, never a skip.
ALIAS_ARCHIVE = ROOT / 'research' / 'harvest-ce45f672' / 'snapshot.json'


def retained_alias_row(row_id, rows):
    for match in rows:
        if str(match.get('id')) == str(row_id):
            return match, 'data/latest.json'
    if not ALIAS_ARCHIVE.exists():
        raise AssertionError('the retained alias capture %s is missing' % ALIAS_ARCHIVE)
    archived = json.loads(ALIAS_ARCHIVE.read_text()).get('matches') or []
    for match in archived:
        if str(match.get('id')) == str(row_id):
            return match, str(ALIAS_ARCHIVE.relative_to(ROOT))
    raise AssertionError('fixture %s is in neither the board nor the retained capture' % row_id)
ARCHIVE = json.loads((ROOT / 'research' / 'harvest-9b97d585' / 'snapshot.json').read_text())
INDEX = overview(copy.deepcopy(SNAPSHOT))


def moment(value):
    return datetime.fromisoformat(str(value).replace('Z', '+00:00'))


def open_rows(snapshot=None):
    return [m for m in (snapshot or SNAPSHOT)['matches'] if m['state'] == 'open']


def future_rows(snapshot=None):
    clock = moment((snapshot or SNAPSHOT)['built_at'])
    return [m for m in (snapshot or SNAPSHOT)['matches']
            if m.get('lock') and moment(m['lock']) > clock and moment(m['start']) > clock]


class EveryFutureMatchResolves(unittest.TestCase):
    """The coverage audit, replayed at the snapshot's own clock."""

    def audit(self, snapshot):
        return audit_f89bb1f8.audit(snapshot, moment(snapshot['built_at']))

    def test_committed_snapshot_passes_the_coverage_audit(self):
        failures, stats = self.audit(SNAPSHOT)
        self.assertEqual(failures, [])
        self.assertEqual(stats['future_rows'], stats['future_with_pick'] + stats['future_unresolved'])
        self.assertGreater(stats['future_rows'], 0)

    def test_no_published_open_row_is_blank(self):
        for m in open_rows():
            self.assertTrue(m.get('pick') or m.get('reason'), m['id'])
            if m.get('pick'):
                self.assertIn(m['pick'], m['teams'], m['id'])
                self.assertTrue((m.get('evidence') or [{}])[0].get('url'), m['id'])

    def test_every_published_percentage_is_a_two_way_pair(self):
        for m in open_rows():
            p = m.get('probabilities')
            if p is None:
                continue
            self.assertEqual(len(p), 2, m['id'])
            self.assertAlmostEqual(sum(p), 1.0, places=9, msg=m['id'])
            self.assertEqual(m['pick'], m['teams'][p.index(max(p))], m['id'])
            for value, team in zip(p, m['teams']):
                self.assertAlmostEqual(m['fair_odds'][m['teams'].index(team)], 1.0 / value, places=9, msg=m['id'])
            # A published number must die at the earliest of its gates.
            self.assertIsNotNone(m.get('expires_at'), m['id'])
            self.assertLessEqual(moment(m['expires_at']), moment(m['start']), m['id'])
            if m.get('lock'):
                self.assertLessEqual(moment(m['expires_at']), moment(m['lock']), m['id'])

    def test_a_rotated_board_still_satisfies_the_contract(self):
        # What tomorrow's snapshot looks like: the same fixtures, a clock past
        # every start. The coverage rules must hold without raising, which is
        # exactly what the old hard-pinned test could not do.
        rotated = copy.deepcopy(SNAPSHOT)
        later = moment(SNAPSHOT['built_at']) + timedelta(days=30)
        rotated['built_at'] = later.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        failures, stats = self.audit(rotated)
        # The only failure a rotation is allowed to add is the audit's own
        # freshness rule, which is about the snapshot's age, not coverage.
        self.assertEqual([f for f in failures if 'evidence window' not in f], [])
        self.assertEqual(stats['future_rows'], 0)

    def test_history_is_pinned_to_the_archive_not_the_live_file(self):
        # The 09:44Z lobby observation is checked against the retained read.
        self.assertEqual(archived_coverage_problems(ARCHIVE), [])
        # ...and the live file is allowed to have moved on from it.
        self.assertIn('matches', SNAPSHOT)


class NoProbabilityFromHotspawn(unittest.TestCase):
    def test_every_priced_row_cites_an_external_or_rating_source(self):
        for m in open_rows():
            if not m.get('probabilities'):
                continue
            urls = [e.get('url') or '' for e in m.get('evidence') or []]
            self.assertTrue(urls, m['id'])
            for url in urls:
                self.assertTrue(url.startswith('https://'), (m['id'], url))
                self.assertNotIn('hotspawn.com', url, (m['id'], url))

    def test_the_fixture_itself_still_links_to_hotspawn(self):
        for m in open_rows():
            url = str(m.get('source_url') or '')
            self.assertTrue(url.startswith('https://www.hotspawn.com/')
                            or url.startswith('https://play.hotspawn.com/'), m['id'])

    def test_no_row_publishes_a_crowd_percentage(self):
        for m in SNAPSHOT['matches']:
            blob = json.dumps({k: v for k, v in m.items() if k in ('probabilities', 'pick', 'method')})
            self.assertNotIn('picked_percent', blob, m['id'])
            self.assertNotIn('votes', blob, m['id'])


class LadderIsPublishedInTheExecutiveSummary(unittest.TestCase):
    def setUp(self):
        self.html = unresolved_limits_card(copy.deepcopy(SNAPSHOT))
        self.soup = BeautifulSoup(self.html, 'html.parser')

    def test_section_keeps_its_identity_and_heading(self):
        section = self.soup.select_one('#unresolved-limits')
        self.assertIsNotNone(section)
        self.assertIn('Unresolved picks, and why a pick can be missing',
                      section.select_one('h2').get_text(' ', strip=True))

    def test_every_rung_is_named_with_its_own_count(self):
        block = self.soup.select_one('[data-ladder-counts]')
        self.assertIsNotNone(block)
        text = block.get_text(' ', strip=True)
        for step in summary.ladder_rows():
            self.assertIn(step['title'], text)
        counts = self.soup.select('[data-ladder-count]')
        self.assertEqual({c['data-ladder-count'] for c in counts},
                         {step['key'] for step in summary.ladder_rows()} | {'none'})

    def test_counts_equal_the_snapshot_methods(self):
        # Recompute the rung counts independently from the published methods.
        expected = {}
        for m in open_rows():
            if m.get('probabilities') is not None or m.get('pick'):
                expected[summary.METHOD_STEP.get(m.get('method'), 'none')] = \
                    expected.get(summary.METHOD_STEP.get(m.get('method'), 'none'), 0) + 1
        for node in self.soup.select('[data-ladder-count]'):
            self.assertEqual(int(node.get_text(strip=True)),
                             expected.get(node['data-ladder-count'], 0), node['data-ladder-count'])
        self.assertEqual(sum(int(n.get_text(strip=True)) for n in self.soup.select('[data-ladder-count]')),
                         len(open_rows()))

    def test_hltv_and_esportsbook_are_explicitly_linked(self):
        hrefs = {a['href'] for a in self.soup.select('a[href]')}
        self.assertIn('https://www.hltv.org/matches', hrefs)
        self.assertIn('https://egamersworld.com/counterstrike/matches', hrefs)
        self.assertIn('sources.html#model', hrefs)
        self.assertIn('unresolved.html', hrefs)

    def test_the_summary_carries_the_section_and_its_links(self):
        soup = BeautifulSoup(INDEX, 'html.parser')
        self.assertIsNotNone(soup.select_one('#unresolved-limits'))
        hrefs = {a['href'] for a in soup.select('a[href]')}
        for target in ('picks.html', 'unresolved.html', 'matches.html', 'review.html', 'sources.html#method'):
            self.assertIn(target, hrefs)


class RegistriesAgree(unittest.TestCase):
    """A method that one registry knows and another does not is a mislabel."""

    def test_every_published_method_is_labelled_and_classified(self):
        for method in build.METHOD_LABELS:
            self.assertIn(method, summary.ORIGINS, method)
            self.assertIn(method, summary.METHOD_STEP, method)
            self.assertIn(method, build.METHOD_TAGS, method)
            self.assertIn(method, build.METHOD_KIND, method)

    def test_the_coverage_auditor_knows_every_method(self):
        # Session 019a253a: `research_form` was missing here, so the first board
        # that used the recent-form rung would have been failed by the auditor
        # that is supposed to confirm coverage. The auditor must classify every
        # method the build can publish, and may not classify one that the
        # summary cannot name (that would be an unlabelled tier).
        audited = audit_f89bb1f8.PRICED | audit_f89bb1f8.RESEARCH
        self.assertLessEqual(set(build.METHOD_LABELS), audited,
                             'the coverage auditor must know every method the build can publish')
        self.assertLessEqual(audited, set(summary.ORIGINS),
                             'the coverage auditor must not know a method the summary cannot name')
        self.assertFalse(audit_f89bb1f8.PRICED & audit_f89bb1f8.RESEARCH)

    def test_every_published_method_maps_to_a_ladder_rung(self):
        keys = {step['key'] for step in summary.ladder_rows()}
        self.assertLessEqual(set(summary.METHOD_STEP.values()), keys)


class StylesheetIntegrity(unittest.TestCase):
    """A stylesheet that ends inside a media block silently disables phone CSS.

    Session 019a253a measured this on the 2026-10-24 build: one unclosed
    ``@media(max-width:650px) and (max-height:700px)`` block meant every rule
    after it only applied on screens 700px tall or less, so a 390x844 phone never
    received the phone layout (first pick card at y=723 instead of y=324).
    """

    COPIES = ('site/assets/style.css', 'assets/style.css')

    def test_both_published_copies_are_byte_identical(self):
        texts = [(ROOT / name).read_text() for name in self.COPIES]
        self.assertEqual(texts[0], texts[1],
                         'the source stylesheet and the published root copy must match')

    def test_no_block_is_left_open_at_end_of_file(self):
        text = (ROOT / 'site' / 'assets' / 'style.css').read_text()
        stripped = re.sub(r'/\*.*?\*/', '', text, flags=re.S)          # comments
        stripped = re.sub(r'"[^"\n]*"|\'[^\'\n]*\'', '', stripped)      # quoted values
        depth = 0
        for index, character in enumerate(stripped):
            if character == '{':
                depth += 1
            elif character == '}':
                depth -= 1
                self.assertGreaterEqual(depth, 0,
                    'unbalanced closing brace at offset %d' % index)
        self.assertEqual(depth, 0,
            'the stylesheet ends inside an open block; every rule after it is gated to that block')

    def test_phone_media_queries_are_closed_where_they_open(self):
        # A cheap structural check: each @media query's braces must close before
        # the next top-level @media, which is what the unclosed block broke.
        text = (ROOT / 'site' / 'assets' / 'style.css').read_text()
        stripped = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
        depth = 0
        for match in re.finditer(r'@media[^{]*\{', stripped):
            start = match.end() - 1
            depth = 0
            for character in stripped[start:]:
                depth += 1 if character == '{' else (-1 if character == '}' else 0)
                if depth == 0:
                    break
            self.assertEqual(depth, 0, 'unclosed @media block: %s' % match.group(0).strip())


class RegisteredAliasesReplayInTheIndependentVerifier(unittest.TestCase):
    """A documented alias must be reproducible by the independent re-derivation.

    Session 019a253a: fixture 1083121 (Projeto do KinGui vs MEIA NOITE) published
    a Polymarket price under Polymarket's own label "Tropa do KinGui". The mapping
    is registered in data/identities.json with primary sources, and PR #266
    aligned the verifier on the full contract: an alias is honoured only when the
    *evidence record itself* carries a receipted identity source (https source and
    written basis) **and** the same label pair belongs to a group in the committed
    register. This suite pins both halves, so neither a receipt without a register
    entry nor a register entry without a receipt can silently price a row.
    """

    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'verify_0cc1138a_alias', ROOT / 'research' / 'session-0cc1138a' / 'verify_0cc1138a.py')
        cls.verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.verifier)

    def sourced_entries(self):
        register = json.loads((ROOT / 'data' / 'identities.json').read_text())
        return [e for e in register['aliases']
                if str(e.get('source') or '').startswith('https://')
                and len(str(e.get('basis') or '')) > 40 and e.get('names')]

    def test_every_sourced_register_group_is_receipted(self):
        entries = self.sourced_entries()
        self.assertGreaterEqual(len(entries), 20)
        for entry in entries:
            groups = self.verifier.alias_groups({'identity_sources': [entry]})
            self.assertEqual(len(groups), 1, entry['canonical'])
            for name in [entry['canonical']] + list(entry['names']):
                self.assertIn(self.verifier.norm(name), groups[0], entry['canonical'])

    def test_a_register_entry_without_a_receipt_is_refused(self):
        # Choose a register pair that prefix matching cannot already bridge
        # (Tropa do KinGui / Projeto do KinGui), otherwise the assertion would
        # pass for the wrong reason.
        pair = None
        for entry in self.sourced_entries():
            for name in entry['names']:
                if not self.verifier.same_team(entry['canonical'], name):
                    pair = (entry['canonical'], name)
                    break
            if pair:
                break
        self.assertIsNotNone(pair, 'the register must contain at least one non-prefix alias')
        self.assertEqual(self.verifier.alias_groups({}), [])
        self.assertEqual(self.verifier.alias_groups({'identity_sources': []}), [])
        # No receipt: the two labels must not be treated as one team.
        self.assertFalse(self.verifier.same_team(*pair))
        # With the receipt they are, which is the contract that prices the row.
        entry = next(e for e in self.sourced_entries() if e['canonical'] == pair[0])
        self.assertEqual(len(self.verifier.alias_groups({'identity_sources': [entry]})), 1)

    def test_an_unregistered_or_unreceipted_alias_is_refused(self):
        self.assertFalse(self.verifier.same_team('Projeto do KinGui', 'Some Other Club'))
        self.assertEqual(self.verifier.alias_groups(
            {'identity_sources': [{'names': ['A', 'B'], 'source': 'https://example.org/x', 'basis': 'x'}]}), [])

    def test_the_published_row_that_used_the_alias_still_replays(self):
        row, _source = retained_alias_row('1083121', SNAPSHOT['matches'])
        self.assertEqual(row.get('method'), 'exchange')
        ev = row['evidence'][0]
        labels = json.loads(ev['raw']['outcomes'])
        prices = [0.615, 0.385]
        self.assertEqual(self.verifier.order_prices(labels, prices, row['teams'], ev=ev), prices)
        with self.assertRaises(ValueError):
            # Without the row's receipt the same labels cannot be mapped.
            self.verifier.order_prices(labels, prices, row['teams'])


class MobileEntryPoint(unittest.TestCase):
    def test_every_page_has_viewport_and_the_phone_tab_bar(self):
        for page in ('index.html', 'picks.html', 'unresolved.html', 'matches.html'):
            text = (ROOT / page).read_text()
            self.assertIn('name="viewport"', text, page)
            self.assertIn('class="mobile-tabs"', text, page)
            self.assertIn('href="picks.html"', text, page)

    def test_the_summary_names_picks_first_in_its_own_navigation(self):
        soup = BeautifulSoup(INDEX, 'html.parser')
        nav = soup.select_one('.exec-summary-links')
        self.assertIsNotNone(nav)
        links = [a['href'] for a in nav.select('a[href]')]
        self.assertEqual(links[0], 'picks.html')
        self.assertIn('#picks-at-a-glance', links)


if __name__ == '__main__':
    unittest.main()
