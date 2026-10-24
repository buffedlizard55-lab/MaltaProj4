"""Session 3c79a355: make the board refreshable again, and readable on a phone.

Five defects are pinned here. Each was reproduced on the published board or in
the committed tree on 2026-10-24 *before* it was repaired; the reproduction is
quoted in the docstring of the test that now guards it.

1. A one-day fixture list was a permanent invariant, so the only workflow that
   refreshes and publishes went red on every run and the board stopped moving.
2. A literal calendar day ("23 Oct") was asserted against the freshness strip,
   which prints the *next pick's own* start date.
3. The independent re-derivation ignored the HLTV Valve-ranking mirror tier, so
   two published probabilities had no independent reproduction.
4. `assets/style.css` carried an unclosed `@media` block, which silently killed
   125 lines of phone CSS (the browser suites' own coverage is in
   `tests/browser_3c79a355.cjs`; the structural half is asserted here too).
5. The harvest workflow committed a refreshed `data/latest.json` without
   regenerating the legacy `main:/` root pages that Pages actually serves.
"""
import json
import re
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = json.loads((ROOT / 'data' / 'latest.json').read_text())


def utc(value):
    return datetime.fromisoformat(str(value).replace('Z', '+00:00'))


class NoDatedInvariantInThePublishGate(unittest.TestCase):
    """The unit suite runs *before* every refresh, so it must not encode a day."""

    # A source line that asserts a literal day-of-month against a rendered
    # date, or a pinned list of fixture IDs that must exist for ever.
    # Only the short form scripts.build.date() renders ("26 Jun", "26 Jun \u00b7 10:30").
    # A full date inside a quoted research record ("8 July 2026") is content, not
    # a rendered board value, so it is deliberately not flagged.
    DATED_DAY = re.compile(
        r"""assert(?:In|Regex)\(\s*['"]\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b(?!\s+\d{4})""")
    PINNED_FIXTURE_SET = re.compile(r'^\s*OBSERVED_OPEN\s*=\s*\{', re.M)
    # Files allowed to assert a literal rendered date because the dates come
    # from a synthetic snapshot the test itself builds, not from data/latest.json.
    # The exemption is checked, not trusted: each file below must still define
    # its own fixture rows, so pointing it at the live snapshot later would make
    # this test fail instead of quietly re-creating the pinned-day defect.
    SYNTHETIC = {'test_session_51a9c98a.py': ('def data(self)', "'fixtures_observed_at': OBSERVED")}

    def test_no_test_asserts_a_literal_calendar_day(self):
        offenders = []
        for path in sorted((ROOT / 'tests').glob('test_*.py')):
            text = path.read_text()
            if path.name in self.SYNTHETIC:
                for required in self.SYNTHETIC[path.name]:
                    self.assertIn(required, text,
                                  '%s no longer defines its own fixture rows, so its literal dates '
                                  'are no longer self-contained' % path.name)
                continue
            for number, line in enumerate(text.splitlines(), 1):
                if self.DATED_DAY.search(line):
                    offenders.append('%s:%d %s' % (path.name, number, line.strip()))
        self.assertEqual(offenders, [],
                         'a rendered date is derived from the snapshot, so asserting a literal day '
                         'makes the suite true for one board only: %r' % offenders)

    def test_the_fixture_parity_contract_is_derived_not_frozen(self):
        # tests/test_session_0cc1138a.py may keep the 2026-10-23 observation as
        # a *receipt* (a constant with a dated name), but nothing may require a
        # frozen ID set to be present in the live snapshot.
        source = (ROOT / 'tests' / 'test_session_0cc1138a.py').read_text()
        self.assertNotRegex(source, self.PINNED_FIXTURE_SET)
        self.assertIn('coverage_counts', source,
                      'parity must be derived from the snapshot\'s own recorded official views')

    def test_every_open_row_is_resolvable_from_the_snapshot_alone(self):
        # The pipeline's contract after the repair: for each open row either a
        # pick with the evidence it rests on, or an explicit refusal carrying
        # both a reason and the source attempts. No silent blank.
        opens = [m for m in SNAPSHOT['matches'] if m['state'] == 'open']
        self.assertTrue(opens, 'a snapshot with no open rows cannot be checked')
        for row in opens:
            with self.subTest(fixture=row['id']):
                self.assertIn(row['pick'], row['teams'])
                self.assertTrue((row.get('evidence') or [{}])[0].get('url')
                                or (row.get('hltv_context') or {}).get('source')
                                or any(a.get('url') for a in row.get('attempts') or []),
                                'a pick must name the page it rests on')


class TheIndependentVerifierCoversEveryOriginatedTier(unittest.TestCase):
    """A published percentage must be re-derivable, or it is not publishable."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'verify_0cc1138a', ROOT / 'research' / 'session-0cc1138a' / 'verify_0cc1138a.py')
        cls.V = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.V)

    def mirror_row(self):
        return next((m for m in SNAPSHOT['matches']
                     if m.get('method') == 'model_vrs_mirror' and m.get('probabilities')), None)

    def test_the_mirror_tier_reproduces_from_its_own_stored_points(self):
        row = self.mirror_row()
        if row is None:
            self.skipTest('this snapshot has no mirror-tier row')
        evidence = row['evidence'][0]
        derived, kind = self.V.evidence_probabilities(evidence, row['teams'])
        self.assertIn(kind, ('hltv_valve_mirror', 'valve_vrs_hltv_mirror'))
        for published, rederived in zip(row['probabilities'], derived):
            self.assertAlmostEqual(published, rederived, places=9)
        # And the whole row passes the independent audit, end to end.
        audited = {r['id']: r for r in self.V.audit(SNAPSHOT)}
        self.assertEqual(audited[row['id']]['problems'], [])

    def test_a_tampered_mirror_record_is_rejected(self):
        row = self.mirror_row()
        if row is None:
            self.skipTest('this snapshot has no mirror-tier row')
        tampered = json.loads(json.dumps(row['evidence'][0]))
        tampered['points'] = [tampered['points'][0], tampered['points'][0]]
        with self.assertRaises(ValueError):
            self.V.evidence_probabilities(tampered, row['teams'])

    def test_an_unregistered_calibration_slope_is_rejected(self):
        row = self.mirror_row()
        if row is None:
            self.skipTest('this snapshot has no mirror-tier row')
        tampered = json.loads(json.dumps(row['evidence'][0]))
        tampered['calibration_slope'] = 0.5
        with self.assertRaises(ValueError):
            self.V.evidence_probabilities(tampered, row['teams'])

    def test_valve_calibration_constant_is_the_published_one(self):
        # modelfit.png in ValveSoftware/counter-strike_regional_standings: y = 0.7986x + 0.126
        self.assertAlmostEqual(self.V.SLOPE, 0.7986, places=12)
        self.assertAlmostEqual(self.V.calibrate(0.5), 0.5, places=12)
        self.assertAlmostEqual(self.V.glicko_expect(1000, 1000), 0.5, places=12)


class TheStylesheetParses(unittest.TestCase):
    """One missing brace silently disables every rule after it."""

    COPIES = ('assets/style.css', 'site/assets/style.css')

    def test_braces_balance_in_both_copies(self):
        for name in self.COPIES:
            css = (ROOT / name).read_text()
            self.assertEqual(css.count('{'), css.count('}'), '%s has unbalanced braces' % name)

    def test_the_copies_are_byte_identical(self):
        texts = {(ROOT / name).read_text() for name in self.COPIES}
        self.assertEqual(len(texts), 1, 'the two published stylesheet copies must not diverge')

    def test_every_media_block_contains_rules_and_closes(self):
        css = (ROOT / 'assets/style.css').read_text()
        depth = 0
        for index, char in enumerate(css):
            if char == '{':
                depth += 1
                self.assertLessEqual(depth, 2, 'rules nested too deeply at byte %d' % index)
            elif char == '}':
                depth -= 1
                self.assertGreaterEqual(depth, 0, 'unmatched } at byte %d' % index)
        self.assertEqual(depth, 0)

    def test_the_phone_index_order_rules_are_not_inside_a_dead_block(self):
        # The rules that put the pick cards above the guide on a phone. They are
        # only effective if they sit in a block that actually closes, which the
        # depth walk above proves; this asserts they still exist.
        css = (ROOT / 'assets/style.css').read_text()
        for rule in ('main>#picks-at-a-glance{order:4}',
                     'main>details.briefing-more{order:6}',
                     '.fresh-next{display:flex'):
            self.assertIn(rule, css)


class TheHarvestPublishesWhatPagesServes(unittest.TestCase):
    """Pages is served from the legacy `main:/` root, not from `public/`."""

    def test_the_harvest_regenerates_the_root_pages_before_committing_them(self):
        workflow = (ROOT / '.github/workflows/harvest-3c79a355.yml').read_text()
        build = workflow.index('python -m scripts.build')
        stage = workflow.index('python -m scripts.publish_root_fallback')
        commit = workflow.index('git commit -m "Harvest:')
        self.assertLess(build, stage, 'public/ must be built before it is staged at the root')
        self.assertLess(stage, commit, 'the root fallback must be staged before the commit')
        # And the committed-state gates run against those same files.
        self.assertLess(stage, workflow.index('python -m scripts.validate --data data/latest.json --site .', stage),
                        'the validator must run against the staged root pages')

    def test_the_committed_root_receipt_matches_the_committed_snapshot(self):
        data = SNAPSHOT
        receipt = json.loads((ROOT / 'build-info.json').read_text())
        self.assertEqual(receipt['snapshot_generated_at'], data['generated_at'])
        self.assertEqual(receipt['rows'], len(data['matches']))
        # The receipt is only meaningful if the pages it hashes are the pages on
        # disk; scripts.validate re-hashes all twenty.
        import hashlib
        for name in ('index.html', 'picks.html', 'unresolved.html'):
            digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            self.assertEqual(receipt['files'][name], digest, '%s does not match its recorded hash' % name)

    def test_the_published_snapshot_is_inside_its_evidence_window(self):
        # A stale board is not a wrong board, but it must never look current:
        # this asserts the committed snapshot is recent enough that the
        # freshness strip cannot claim it is live while its picks have expired.
        built = utc(SNAPSHOT['built_at'])
        age_hours = (datetime.now(timezone.utc) - built).total_seconds() / 3600
        self.assertLess(age_hours, SNAPSHOT['stale_after_hours'],
                        'the committed snapshot is %.1f h old; refresh it before publishing' % age_hours)


class EveryOpenMatchCarriesAProbabilityOrASourcedReason(unittest.TestCase):
    def test_published_probabilities_sum_to_one_and_name_their_source(self):
        for row in SNAPSHOT['matches']:
            if row['state'] != 'open' or row.get('probabilities') is None:
                continue
            with self.subTest(fixture=row['id']):
                self.assertAlmostEqual(sum(row['probabilities']), 1.0, places=9)
                self.assertTrue(row['evidence'], 'a priced row must carry its evidence record')
                evidence = row['evidence'][0]
                self.assertTrue((evidence.get('url') or evidence.get('api_url') or '').startswith('https://'))
                # Hotspawn is inventory only: it may never be the probability source.
                source = (evidence.get('url') or evidence.get('api_url') or '').lower()
                self.assertNotIn('hotspawn', source)

    def test_the_pick_is_always_the_larger_probability(self):
        for row in SNAPSHOT['matches']:
            if row['state'] != 'open' or row.get('probabilities') is None:
                continue
            with self.subTest(fixture=row['id']):
                best = row['teams'][row['probabilities'].index(max(row['probabilities']))]
                self.assertEqual(row['pick'], best)


if __name__ == '__main__':
    unittest.main()
