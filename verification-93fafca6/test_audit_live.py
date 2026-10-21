"""Failure-mode tests for the independent live-site auditor.

Offline and deterministic: every case builds the served bytes in memory, so no
network, no clock and no repository file is touched. Each test pins one rule the
auditor claims to enforce, and the paired "healthy" site proves the rule does not
fire on a correct deployment (a check that only ever fails is not a check).

Run: ``python -m unittest discover -s verification-93fafca6 -p 'test_*.py' -v``
"""
import contextlib
import datetime
import re
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

# ``verification-93fafca6`` contains a dash, so it is not an importable package
# name; the auditor is loaded by path, exactly as ``verification-c6/test_audit.py``
# loads ``audit_snapshot.py``.
_spec = importlib.util.spec_from_file_location('audit_live', Path(__file__).with_name('audit_live.py'))
al = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(al)

NOW = al.utc('2026-10-21T20:14:00Z')
FRESH_SNAPSHOT = '2026-10-21T19:57:45.210692Z'
STALE_SNAPSHOT = '2026-10-18T00:52:19.597023Z'
HEAD = '63f4172cb50aff8b2a36b2e01514b3e121a3d792'
FALLBACK_REVISION = '88b1b2c3b96954e64f614ad08342cc74aeb289fe'

VIEWPORT = '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'

PHONE_CSS = """
.mobile-tabs{display:none}
@media(max-width:850px){.table-wrap{overflow-x:auto}table{min-width:610px}}
@media(max-width:650px){body{font-size:14px}.mobile-tabs{display:flex}
.mobile-tabs a{flex:1;min-height:60px;font-size:9.5px}
table{min-width:0;display:block}
.source-links a{font-size:11px;min-height:32px}}
@media(max-width:650px){.source-links a{min-height:44px;display:inline-flex}}
"""


def row(fixture_id, state='open', pick=None, probabilities=None, method=None, evidence=(), teams=None):
    return {'id': fixture_id, 'state': state, 'teams': teams or ['Alpha', 'Beta'],
            'start': '2026-10-22T14:00:00Z', 'lock': '2026-10-22T13:54:00Z',
            'pick': pick, 'probabilities': probabilities, 'method': method,
            'evidence': [{'url': u, 'observed_at': FRESH_SNAPSHOT} for u in evidence],
            'attempts': [], 'flags': [], 'expires_at': None}


def coverage_script(rows):
    slim = [{'id': r['id'], 'state': r['state'], 'start': r.get('start'),
             'lock': r.get('lock'), 'expires_at': r.get('expires_at'),
             'priced': bool(r.get('probabilities')), 'model': r.get('method') == 'model_vrs',
             'research': bool(r.get('pick')) and not r.get('probabilities')} for r in rows]
    return '<script type="application/json" id="coverage-data">%s</script>' % json.dumps(slim)


def glance(rows):
    items = ''.join(
        '<li><a class="glance-row" href="evidence.html#match-%s" data-glance-start="%s" '
        'data-glance-priced="%d"><span class="glance-teams">%s</span></a></li>'
        % (r['id'], r.get('start'), 1 if r.get('probabilities') else 0, ' vs '.join(r['teams']))
        for r in rows if r['state'] == 'open')
    return ('<section class="panel glance" id="picks-at-a-glance"><h2>Picks at a glance</h2>'
            '<ol class="glance-list">%s</ol></section>' % items)


def index_html(rows, stale_strip=False, limitations_names=(), tabs=True, nav=True,
               nest_limitations=True):
    strip_state = ('Snapshot is older than 8 hours: every percentage below is expired and must not '
                   'be used as a current pick' if stale_strip
                   else 'Snapshot inside its 8-hour evidence window')
    strip = ('<div class="fresh-strip %s" id="freshness-strip"><span class="fresh-main">'
             '<strong>Last checked</strong></span><span class="fresh-state">%s</span></div>'
             '<section class="hero"></section>' % ('stale' if stale_strip else 'live', strip_state))
    section_nav = ('<nav class="section-nav" aria-label="Where the picks are">'
                   '<a href="picks.html">Updated picks</a>'
                   '<a href="unresolved.html?status=needs">No percentage</a>'
                   '<a href="matches.html">Every match</a></nav>') if nav else ''
    links = ''.join('<a href="%s">%s</a>' % (p, p) for p in
                    ('picks.html', 'unresolved.html', 'matches.html', 'analysis.html',
                     'review.html', 'sources.html', 'evidence.html'))
    named = ''.join('<li><a href="evidence.html#match-%s">%s</a> has no accessible two-way line.'
                    '</li>' % (name, name) for name in limitations_names)
    limitations = ('<div class="panel limitations" id="pick-limitations"><h3>Limitations for '
                   'generating these picks</h3><ul class="checklist">%s<li>No book lists the match.'
                   '</li></ul></div>' % named)
    summary = ('<section id="unresolved-summary"><h2>Matches with no market line</h2>%s</section>'
               % limitations) if nest_limitations else (
        '<section id="unresolved-summary"><h2>Matches with no market line</h2></section>%s'
        % limitations)
    mobile = ('<nav class="mobile-tabs" aria-label="Phone navigation"><a href="index.html">'
              '<span>Home</span></a></nav>') if tabs else ''
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">%s<title>t</title></head>'
            '<body data-observed="%s">%s<div id="runtime-stale" class="notice error" hidden></div>'
            '%s%s%s%s%s%s</body></html>'
            % (VIEWPORT, FRESH_SNAPSHOT, coverage_script(rows), strip, section_nav, links,
               glance(rows), summary, mobile))


def site(rows, revision=HEAD, snapshot_at=FRESH_SNAPSHOT, built_at='2026-10-21T19:57:45Z',
         stale_strip=False, css=PHONE_CSS, extra=None, tamper=(), limitations_names=(),
         nest_limitations=True, nav=True, with_app_js=True):
    """Build an in-memory served-file map exactly as `collect()` would return."""
    bodies = {
        'index.html': index_html(rows, stale_strip=stale_strip,
                                limitations_names=limitations_names, nav=nav,
                                nest_limitations=nest_limitations).encode(),
        'assets/style.css': css.encode(),
        'data/latest.json': json.dumps({'schema_version': 2, 'generated_at': snapshot_at,
                                        'matches': rows}).encode(),
    }
    if with_app_js:
        bodies['assets/app.js'] = b"const x=1; row.classList.add('live-expired');"
    for name, body in (extra or {}).items():
        bodies[name] = body
    receipt = {'schema_version': 1, 'revision': revision, 'built_at': built_at,
               'snapshot_generated_at': snapshot_at, 'rows': len(rows),
               'files': {n: al.sha256_hex(b) for n, b in bodies.items()}}
    for name in tamper:
        bodies[name] = bodies[name] + b'<!-- rewritten by a second publisher -->'
    bodies['build-info.json'] = json.dumps(receipt, indent=2).encode()
    live = {}
    for name, body in bodies.items():
        live[name] = {'status': 200, 'body': body, 'error': None, 'fetched': True,
                      'sha256': al.sha256_hex(body), 'canonical_url': al.join(al.LIVE_BASE, name)}
    return live, receipt


def run(live, **kwargs):
    report = al.Report()
    kwargs.setdefault('now', NOW)
    kwargs.setdefault('head_sha', HEAD)
    al.audit(live, report, **kwargs)
    return report


def levels(report, check):
    return [f['level'] for f in report.findings if f['check'] == check]


def findings(report, check):
    return [f for f in report.findings if f['check'] == check]


HEALTHY_ROWS = [
    row('1082688', pick='Imperial', probabilities=[0.775, 0.225], method='exchange',
        evidence=('https://gamma-api.polymarket.com/markets/5972064',), teams=['Imperial', 'Turma do Pagode']),
    row('1081600', pick='Banda chuya', probabilities=[0.4238, 0.5762], method='model_vrs',
        evidence=('https://github.com/ValveSoftware/counter-strike_regional_standings',),
        teams=['Donstu', 'Banda chuya']),
    row('1082837', pick='Zetta', probabilities=None, method='research_rank_single',
        evidence=('https://www.hltv.org/matches/2400001/zetta-vs-los-ninos',), teams=['Zetta', 'LOS NINOS']),
    row('1052746', state='not_open', teams=['Fortress', 'Endless Journey']),
]


class TestHtmlHelpers(unittest.TestCase):
    def test_element_slice_handles_nested_same_tag_elements(self):
        html = '<div id="a"><div id="b">inner</div><p>x</p></div><div id="c">after</div>'
        self.assertEqual(al.element_slice(html, 'a'), '<div id="a"><div id="b">inner</div><p>x</p></div>')
        self.assertEqual(al.element_slice(html, 'c'), '<div id="c">after</div>')
        self.assertIsNone(al.element_slice(html, 'missing'))

    def test_nested_inside_is_true_only_for_real_containment(self):
        inside = '<section id="outer"><div id="inner">x</div></section>'
        outside = '<section id="outer">x</section><div id="inner">y</div>'
        self.assertTrue(al.nested_inside(inside, 'inner', 'outer'))
        self.assertFalse(al.nested_inside(outside, 'inner', 'outer'))

    def test_last_px_follows_the_cascade_not_the_first_match(self):
        # The stylesheet declares 32px first and 44px later; a phone renders 44px.
        self.assertEqual(al.last_px(PHONE_CSS, '.source-links a', 'min-height'), 44.0)
        self.assertEqual(al.last_px(PHONE_CSS, '.mobile-tabs a', 'min-height'), 60.0)
        self.assertIsNone(al.last_px(PHONE_CSS, '.never-declared', 'min-height'))
        # The first-match reading this replaces would have reported a failing 32px.
        self.assertEqual(al.px_value(al.css_rule(PHONE_CSS, '.source-links a'), 'min-height'), 32.0)

    def test_media_blocks_selects_only_the_requested_max_width(self):
        self.assertEqual(len(al.media_blocks(PHONE_CSS, 650)), 2)
        self.assertEqual(len(al.media_blocks(PHONE_CSS, 850)), 1)
        self.assertEqual(al.media_blocks(PHONE_CSS, 320), [])

    def test_coverage_rows_and_glance_ids_read_the_deployed_page(self):
        html = index_html(HEALTHY_ROWS)
        rows = al.coverage_rows(html)
        self.assertEqual([r['id'] for r in rows], ['1082688', '1081600', '1082837', '1052746'])
        self.assertEqual(al.glance_ids(html), ['1082688', '1081600', '1082837'])
        self.assertIsNone(al.coverage_rows('<html></html>'))
        self.assertIsNone(al.glance_ids('<html></html>'))


class TestReceiptAndPublisher(unittest.TestCase):
    def test_unparsable_receipt_fails_closed_and_stops(self):
        live = {'build-info.json': {'status': 200, 'body': b'not json', 'error': None,
                                    'sha256': 'x', 'canonical_url': 'u'}}
        report = run(live)
        self.assertEqual(levels(report, 'receipt-readable'), [al.FAIL])
        self.assertEqual(len(report.findings), 1, 'nothing downstream may guess a value')

    def test_missing_receipt_file_fails_closed(self):
        live = {'build-info.json': {'status': 404, 'body': b'', 'error': 'HTTP 404',
                                    'sha256': None, 'canonical_url': 'u'}}
        report = run(live)
        self.assertEqual(levels(report, 'receipt-readable'), [al.FAIL])
        self.assertIn('404', findings(report, 'receipt-readable')[0]['detail'])

    def test_artifact_for_current_head_is_reported_as_information(self):
        live, _ = site(HEALTHY_ROWS)
        report = run(live)
        self.assertEqual(levels(report, 'publisher-identity'), [al.INFO])
        self.assertEqual(levels(report, 'live-board-fresh'), [al.PASS])
        self.assertIn('verified workflow artifact', findings(report, 'publisher-identity')[0]['detail'])

    def test_legacy_fallback_serving_is_warned_and_named(self):
        live, _ = site(HEALTHY_ROWS, revision=FALLBACK_REVISION, snapshot_at=STALE_SNAPSHOT,
                       built_at='2026-10-18T00:52:19Z', stale_strip=True)
        report = run(live, committed_receipt={'revision': FALLBACK_REVISION})
        self.assertEqual(levels(report, 'publisher-identity'), [al.WARN])
        detail = findings(report, 'publisher-identity')[0]['detail']
        self.assertIn('committed root fallback', detail)
        self.assertIn('dual-publisher race', detail)
        # and the visitor-visible consequence is a failure, not a shrug
        self.assertEqual(levels(report, 'live-board-fresh'), [al.FAIL])

    def test_board_inside_the_window_passes_and_outside_fails(self):
        fresh, _ = site(HEALTHY_ROWS)
        self.assertEqual(levels(run(fresh), 'live-board-fresh'), [al.PASS])
        stale, _ = site(HEALTHY_ROWS, snapshot_at=STALE_SNAPSHOT, built_at='2026-10-18T00:52:19Z',
                        stale_strip=True)
        self.assertEqual(levels(run(stale), 'live-board-fresh'), [al.FAIL])
        self.assertIn('91.', findings(run(stale), 'live-board-fresh')[0]['detail'])


class TestManifestConsistency(unittest.TestCase):
    def test_identical_bytes_pass(self):
        live, _ = site(HEALTHY_ROWS)
        report = run(live)
        self.assertEqual(levels(report, 'manifest-consistency'), [al.PASS])

    def test_a_torn_deployment_fails(self):
        # One publisher writes fresh HTML over another publisher's data file.
        live, _ = site(HEALTHY_ROWS, tamper=('data/latest.json',))
        report = run(live)
        self.assertEqual(levels(report, 'manifest-consistency'), [al.FAIL])
        self.assertIn('data/latest.json', findings(report, 'manifest-consistency')[0]['detail'])

    def test_a_missing_navigation_page_fails(self):
        live, _ = site(HEALTHY_ROWS)
        live['picks.html'] = {'status': 404, 'body': b'', 'error': 'HTTP 404', 'fetched': True,
                              'sha256': None, 'canonical_url': al.join(al.LIVE_BASE, 'picks.html')}
        report = run(live)
        # The pick board is the destination the executive summary links to, so a
        # 404 is a broken live route even though no manifest entry covers it.
        self.assertEqual(levels(report, 'core-routes-available'), [al.FAIL])
        self.assertIn('picks.html', findings(report, 'core-routes-available')[0]['detail'])

    def test_a_file_not_fetched_by_this_run_is_never_a_finding(self):
        live, _ = site(HEALTHY_ROWS)
        live['picks.html'] = {'status': None, 'body': b'', 'error': 'not saved offline',
                              'fetched': False, 'sha256': None,
                              'canonical_url': al.join(al.LIVE_BASE, 'picks.html')}
        report = run(live)
        self.assertEqual(levels(report, 'core-routes-available'), [al.PASS])
        self.assertEqual(levels(report, 'manifest-consistency'), [al.PASS])

    def test_all_core_routes_answered(self):
        live, _ = site(HEALTHY_ROWS)
        report = run(live)
        self.assertEqual(levels(report, 'core-routes-available'), [al.PASS])
        self.assertIn('index.html', findings(report, 'core-routes-available')[0]['detail'])


class TestExecutiveSummary(unittest.TestCase):
    def test_healthy_summary_links_and_anchors_pass(self):
        live, _ = site(HEALTHY_ROWS)
        report = run(live)
        self.assertEqual(levels(report, 'summary-links'), [al.PASS])
        self.assertEqual(levels(report, 'summary-anchors'), [al.PASS])

    def test_a_missing_pick_list_link_fails(self):
        live, _ = site(HEALTHY_ROWS)
        html = re.sub(r'<a href="picks\.html[^"]*">[^<]*</a>', '', live['index.html']['body'].decode())
        self.assertNotIn('picks.html', html)
        live['index.html']['body'] = html.encode()
        live['index.html']['sha256'] = al.sha256_hex(html.encode())
        report = run(live)
        self.assertEqual(levels(report, 'summary-links'), [al.FAIL])
        self.assertIn('picks.html', findings(report, 'summary-links')[0]['detail'])

    def test_limitations_outside_the_summary_fails(self):
        live, _ = site(HEALTHY_ROWS, nest_limitations=False)
        report = run(live)
        self.assertEqual(levels(report, 'summary-anchors'), [al.FAIL])
        self.assertIn('not inside', findings(report, 'summary-anchors')[0]['title'])

    def test_a_missing_glance_block_fails(self):
        live, _ = site(HEALTHY_ROWS)
        html = live['index.html']['body'].decode()
        start = html.find('<section class="panel glance"')
        end = html.find('</section>', start) + len('</section>')
        live['index.html']['body'] = (html[:start] + html[end:]).encode()
        report = run(live)
        self.assertEqual(levels(report, 'summary-anchors'), [al.FAIL])
        self.assertEqual(levels(report, 'glance-completeness-live'), [al.FAIL])


class TestGlanceCompleteness(unittest.TestCase):
    def test_glance_list_matches_the_pages_own_open_rows(self):
        live, _ = site(HEALTHY_ROWS)
        report = run(live)
        self.assertEqual(levels(report, 'glance-completeness-live'), [al.PASS])
        self.assertIn('3 open fixtures', findings(report, 'glance-completeness-live')[0]['detail'])

    def test_an_open_row_missing_from_the_glance_list_fails(self):
        rows = list(HEALTHY_ROWS)
        live, _ = site(rows)
        html = live['index.html']['body'].decode()
        start = html.find('<li><a class="glance-row" href="evidence.html#match-1082837"')
        end = html.find('</li>', start) + len('</li>')
        live['index.html']['body'] = (html[:start] + html[end:]).encode()
        report = run(live)
        self.assertEqual(levels(report, 'glance-completeness-live'), [al.FAIL])
        self.assertIn('1082837', findings(report, 'glance-completeness-live')[0]['detail'])

    def test_a_freshly_open_fixture_absent_from_the_live_board_fails(self):
        live, _ = site(HEALTHY_ROWS)
        newer = {'generated_at': '2026-10-21T20:12:00Z',
                 'matches': HEALTHY_ROWS + [row('1082999', pick=None, teams=['New', 'Fixture'])]}
        report = run(live, snapshot=newer)
        self.assertEqual(levels(report, 'glance-completeness-fresh'), [al.FAIL])
        detail = findings(report, 'glance-completeness-fresh')[0]['detail']
        self.assertIn('1082999', detail)
        self.assertIn('New vs Fixture', detail)

    def test_a_matching_fresh_snapshot_passes_and_lists_closed_rows(self):
        live, _ = site(HEALTHY_ROWS)
        newer = {'generated_at': '2026-10-21T20:12:00Z',
                 'matches': [r for r in HEALTHY_ROWS if r['id'] != '1082837']}
        report = run(live, snapshot=newer)
        self.assertEqual(levels(report, 'glance-completeness-fresh'), [al.PASS])
        self.assertIn('1082837', findings(report, 'glance-completeness-fresh')[0]['detail'])


class TestPickCoverageAndSourcing(unittest.TestCase):
    def test_every_open_row_picked_or_named(self):
        rows = HEALTHY_ROWS + [row('1081597', pick=None, teams=['benched gods', 'TitanFlow'])]
        live, _ = site(rows, limitations_names=('1081597',))
        report = run(live)
        self.assertEqual(levels(report, 'pick-coverage'), [al.PASS])
        self.assertIn('1 with no pick', findings(report, 'pick-coverage')[0]['detail'])

    def test_an_unnamed_gap_fails(self):
        rows = HEALTHY_ROWS + [row('1081597', pick=None, teams=['benched gods', 'TitanFlow'])]
        live, _ = site(rows)
        report = run(live)
        self.assertEqual(levels(report, 'pick-coverage'), [al.FAIL])
        self.assertIn('benched gods vs TitanFlow', findings(report, 'pick-coverage')[0]['detail'])

    def test_a_team_name_also_satisfies_the_naming_rule(self):
        rows = HEALTHY_ROWS + [row('1081597', pick=None, teams=['benched gods', 'TitanFlow'])]
        live, _ = site(rows, limitations_names=('TitanFlow',))
        self.assertEqual(levels(run(live), 'pick-coverage'), [al.PASS])

    def test_a_probability_sourced_only_from_hotspawn_fails(self):
        rows = [row('1082688', pick='Imperial', probabilities=[0.775, 0.225], method='exchange',
                    evidence=('https://play.hotspawn.com/cs2-pickems',))]
        live, _ = site(rows)
        report = run(live)
        self.assertEqual(levels(report, 'probability-not-from-hotspawn'), [al.FAIL])
        self.assertIn('Only Hotspawn links', findings(report, 'probability-not-from-hotspawn')[0]['detail'])

    def test_a_probability_with_no_evidence_at_all_fails(self):
        rows = [row('1082688', pick='Imperial', probabilities=[0.775, 0.225], method='exchange')]
        live, _ = site(rows)
        report = run(live)
        self.assertEqual(levels(report, 'probability-not-from-hotspawn'), [al.FAIL])
        self.assertIn('No evidence link', findings(report, 'probability-not-from-hotspawn')[0]['detail'])

    def test_external_evidence_passes_and_reports_its_hosts(self):
        live, _ = site(HEALTHY_ROWS)
        report = run(live)
        self.assertEqual(levels(report, 'probability-not-from-hotspawn'), [al.PASS])
        self.assertIn('gamma-api.polymarket.com',
                      findings(report, 'probability-not-from-hotspawn')[0]['detail'])

    def test_unreadable_snapshot_json_is_a_warning_not_a_guess(self):
        live, _ = site(HEALTHY_ROWS)
        live['data/latest.json'] = {'status': 500, 'body': b'', 'error': 'HTTP 500',
                                    'sha256': None, 'canonical_url': 'u'}
        report = run(live)
        self.assertEqual(levels(report, 'pick-coverage'), [al.WARN])
        self.assertEqual(levels(report, 'probability-not-from-hotspawn'), [])


class TestFreshnessCopy(unittest.TestCase):
    def test_expired_data_presented_as_current_fails(self):
        live, _ = site(HEALTHY_ROWS, snapshot_at=STALE_SNAPSHOT, built_at='2026-10-18T00:52:19Z',
                       stale_strip=False)
        report = run(live)
        self.assertEqual(levels(report, 'freshness-copy-honest'), [al.FAIL])
        self.assertIn('presented as current', findings(report, 'freshness-copy-honest')[0]['title'])

    def test_fresh_receipt_with_a_stale_strip_warns_as_the_fallback_fingerprint(self):
        live, _ = site(HEALTHY_ROWS, stale_strip=True)
        report = run(live)
        self.assertEqual(levels(report, 'freshness-copy-honest'), [al.WARN])
        self.assertIn('rendered at a later instant', findings(report, 'freshness-copy-honest')[0]['detail'])
        self.assertEqual(levels(report, 'render-vs-receipt'), [al.INFO])

    def test_agreeing_copy_passes_and_requires_the_client_side_hook(self):
        live, _ = site(HEALTHY_ROWS)
        self.assertEqual(levels(run(live), 'freshness-copy-honest'), [al.PASS])
        no_js, _ = site(HEALTHY_ROWS, with_app_js=False)
        self.assertEqual(levels(run(no_js), 'freshness-copy-honest'), [al.WARN])

    def test_a_missing_strip_fails(self):
        live, _ = site(HEALTHY_ROWS)
        html = live['index.html']['body'].decode().replace('id="freshness-strip"', 'id="moved"')
        live['index.html']['body'] = html.encode()
        self.assertEqual(levels(run(live), 'freshness-copy-honest'), [al.FAIL])


class TestMobileMarkers(unittest.TestCase):
    def test_healthy_phone_deployment_passes_with_its_measured_targets(self):
        live, _ = site(HEALTHY_ROWS)
        report = run(live)
        self.assertEqual(levels(report, 'mobile-markers'), [al.PASS])
        detail = findings(report, 'mobile-markers')[0]['detail']
        self.assertIn('tab tap target 60px', detail)
        self.assertIn('evidence-link tap target 44px', detail)

    def test_a_missing_viewport_fails(self):
        live, _ = site(HEALTHY_ROWS)
        html = live['index.html']['body'].decode().replace(VIEWPORT, '')
        live['index.html']['body'] = html.encode()
        report = run(live)
        self.assertEqual(levels(report, 'mobile-markers'), [al.FAIL])
        self.assertIn('viewport', findings(report, 'mobile-markers')[0]['detail'])

    def test_a_missing_phone_tab_bar_fails(self):
        live, _ = site(HEALTHY_ROWS, extra={'picks.html': b'<html><head>' + VIEWPORT.encode() +
                                            b'</head><body>no tabs</body></html>'})
        report = run(live)
        self.assertEqual(levels(report, 'mobile-markers'), [al.FAIL])
        self.assertIn('picks.html', findings(report, 'mobile-markers')[0]['detail'])

    def test_tables_that_force_a_horizontal_scroll_fail(self):
        css = PHONE_CSS.replace('table{min-width:0;display:block}', '')
        live, _ = site(HEALTHY_ROWS, css=css)
        report = run(live)
        self.assertEqual(levels(report, 'mobile-markers'), [al.FAIL])
        self.assertIn('horizontal scroll', findings(report, 'mobile-markers')[0]['detail'])

    def test_a_small_tap_target_fails_on_the_cascaded_value(self):
        css = PHONE_CSS.replace('.source-links a{min-height:44px;display:inline-flex}', '')
        live, _ = site(HEALTHY_ROWS, css=css)
        report = run(live)
        self.assertEqual(levels(report, 'mobile-markers'), [al.FAIL])
        self.assertIn('32px', findings(report, 'mobile-markers')[0]['detail'])

    def test_an_unreadable_stylesheet_fails_rather_than_assuming(self):
        live, _ = site(HEALTHY_ROWS)
        live['assets/style.css'] = {'status': 404, 'body': b'', 'error': 'HTTP 404',
                                    'sha256': None, 'canonical_url': 'u'}
        report = run(live)
        self.assertEqual(levels(report, 'mobile-markers'), [al.FAIL])
        self.assertIn('unverifiable', findings(report, 'mobile-markers')[0]['detail'])


class TestExternalReachability(unittest.TestCase):
    def test_recorded_statuses_are_replayed_without_a_network_call(self):
        live, _ = site(HEALTHY_ROWS)
        statuses = {'https://gamma-api.polymarket.com/markets/5972064': 200,
                    'https://github.com/ValveSoftware/counter-strike_regional_standings': 200,
                    'https://www.hltv.org/matches/2400001/zetta-vs-los-ninos': 200}
        report = run(live, check_external=True, external_statuses=statuses)
        self.assertEqual(levels(report, 'external-evidence-reachable'), [al.PASS])

    def test_a_dead_primary_link_fails(self):
        live, _ = site(HEALTHY_ROWS)
        statuses = {'https://gamma-api.polymarket.com/markets/5972064': 404,
                    'https://github.com/ValveSoftware/counter-strike_regional_standings': 200,
                    'https://www.hltv.org/matches/2400001/zetta-vs-los-ninos': 200}
        report = run(live, check_external=True, external_statuses=statuses)
        self.assertEqual(levels(report, 'external-evidence-reachable'), [al.FAIL])

    def test_an_access_limited_source_warns_and_is_not_called_broken(self):
        live, _ = site(HEALTHY_ROWS)
        statuses = {'https://gamma-api.polymarket.com/markets/5972064': 200,
                    'https://github.com/ValveSoftware/counter-strike_regional_standings': 200,
                    'https://www.hltv.org/matches/2400001/zetta-vs-los-ninos': 403}
        report = run(live, check_external=True, external_statuses=statuses)
        self.assertEqual(levels(report, 'external-evidence-reachable'), [al.WARN])
        self.assertIn('never bypassed', findings(report, 'external-evidence-reachable')[0]['detail'])

    def test_the_check_is_opt_in(self):
        live, _ = site(HEALTHY_ROWS)
        self.assertEqual(levels(run(live), 'external-evidence-reachable'), [])


class TestCommandLine(unittest.TestCase):
    def test_offline_run_reports_and_exits_nonzero_on_a_failure(self):
        live, _ = site(HEALTHY_ROWS, revision=FALLBACK_REVISION, snapshot_at=STALE_SNAPSHOT,
                       built_at='2026-10-18T00:52:19Z', stale_strip=True)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, entry in live.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(entry['body'])
            out, js, saved = root / 'report.md', root / 'report.json', root / 'receipts'
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = al.main(['--offline-dir', str(root), '--head-sha', HEAD,
                                '--committed-receipt', str(root / 'build-info.json'),
                                '--now', '2026-10-21T20:14:00Z', '--output', str(out),
                                '--json', str(js), '--save-dir', str(saved)])
            self.assertIn('Independent audit of the live published site', stdout.getvalue())
            self.assertEqual(code, 1)
            self.assertTrue(out.exists() and js.exists())
            payload = json.loads(js.read_text())
            self.assertEqual(payload['context']['committed_revision'], FALLBACK_REVISION)
            self.assertTrue(any(f['level'] == al.FAIL for f in payload['findings']))
            self.assertTrue((saved / 'live-files.json').exists())
            self.assertTrue((saved / 'build-info.json').exists())

    def test_a_healthy_offline_site_exits_zero(self):
        live, _ = site(HEALTHY_ROWS)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, entry in live.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(entry['body'])
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = al.main(['--offline-dir', str(root), '--head-sha', HEAD,
                                '--committed-receipt', str(root / 'build-info.json'),
                                '--now', '2026-10-21T20:14:00Z', '--output', str(root / 'r.md')])
            self.assertEqual(code, 0, Path(root, 'r.md').read_text())


class TestPrimitives(unittest.TestCase):
    def test_utc_parsing_and_age(self):
        self.assertIsNone(al.utc(None))
        self.assertIsNone(al.utc('not a timestamp'))
        self.assertEqual(al.utc('2026-10-21T20:14:00Z'),
                         datetime.datetime(2026, 10, 21, 20, 14, tzinfo=datetime.timezone.utc))
        self.assertAlmostEqual(al.hours_between(al.utc('2026-10-21T20:14:00Z'),
                                                al.utc('2026-10-21T19:57:45Z')), 0.27, places=2)
        self.assertIsNone(al.hours_between(None, al.utc('2026-10-21T19:57:45Z')))

    def test_cache_bust_preserves_the_canonical_query(self):
        url = 'https://example.test/build-info.json?a=1&b=2'
        busted = al.cache_bust(url, 'T1')
        self.assertIn('a=1', busted)
        self.assertIn('b=2', busted)
        self.assertIn('_liveaudit=T1', busted)
        self.assertNotIn('_liveaudit', url)

    def test_cache_bust_works_on_a_url_with_no_query(self):
        self.assertEqual(al.cache_bust('https://example.test/lobby', 'T2'),
                         'https://example.test/lobby?_liveaudit=T2')

    def test_cache_bust_survives_a_valueless_argument(self):
        # A list pair (what str.split returns) makes urlencode raise TypeError;
        # the pairs must be tuples. scripts/refresh.py has the same shape and is
        # only saved by the cache-busted URLs having no query at all.
        busted = al.cache_bust('https://example.test/lobby?flag&a=1', 'T3')
        self.assertIn('_liveaudit=T3', busted)
        self.assertIn('a=1', busted)

    def test_http_get_never_raises(self):
        status, body, error = al.http_get('https://invalid.invalid./x', timeout=1)
        self.assertIsNone(status)
        self.assertEqual(body, b'')
        self.assertTrue(error)


if __name__ == '__main__':
    unittest.main(verbosity=2)
