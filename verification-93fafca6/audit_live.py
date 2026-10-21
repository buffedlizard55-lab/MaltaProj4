#!/usr/bin/env python3
"""Independent acceptance audit of the LIVE deployed GitHub Pages bytes.

Why this exists (measured 2026-10-21, session 93fafca6)
-------------------------------------------------------
Every other gate in this repository inspects a build this repository produced:
``scripts/validate.py`` and ``verification-c6/audit_snapshot.py`` read the local
``public/`` tree, the browser suite drives a local test server, and
``scripts/verify_live.py`` polls the live site only *inside* the deploy job that
just published it. Nothing audits what a phone visitor actually gets at an
arbitrary moment - and this repository has a documented reason to need one.

GitHub Pages is configured ``build_type: legacy`` with ``source: main:/``
(``GET /repos/buffedlizard55-lab/MaltaProj4/pages``), so every push to ``main``
also fires GitHub's own ``pages-build-deployment``, which publishes the
**committed root fallback** to the same site that ``pages.yml`` publishes the
fresh artifact to. Whichever lands last wins. On 2026-10-21 the sequence was
observed directly:

* 20:11Z live ``build-info.json`` = revision ``47f230b``, built
  ``2026-10-21T19:57:45Z``, 76 rows (the verified artifact);
* 20:12:40Z a legacy Pages build for commit ``63f4172`` completed;
* 20:14Z the same URL returned revision ``88b1b2c3``, built
  ``2026-10-18T00:52:19Z``, **98 rows** - a 3.8-day-old board with every pick
  expired;
* 20:20:28Z ``pages.yml`` run 39668307571 finished deploying and the fresh
  artifact was served again.

The owner-level fix (``PUT /repos/{owner}/{repo}/pages`` with
``{"build_type":"workflow"}``) was re-attempted by this session and returned
**HTTP 403** (``X-Accepted-Github-Permissions: pages=write,administration=write``;
the integration token carries no OAuth scopes), the same verdict sessions
a980a709 and 1abdd416 recorded. So the race cannot be removed from a branch; it
has to be *measured*, and the deployed bytes have to be audited as delivered.

What this auditor checks
------------------------
It fetches the live site (or reads a saved offline copy), pairs it with an
optional same-minute ``scripts.refresh`` snapshot, and reports findings at four
levels (``pass``/``info``/``warn``/``fail``):

1.  ``receipt-readable``       - the live build receipt parses and carries the
                                 revision, build time, snapshot time and row count.
2.  ``publisher-identity``     - which of the two publishers is being served right
                                 now, and how old the served snapshot is.
3.  ``manifest-consistency``   - every file in the live manifest is byte-identical
                                 to its own published SHA-256, which is what a torn
                                 or mixed deployment (fresh HTML over stale data)
                                 would break.
4.  ``summary-links``          - the executive summary links, inside the site, to
                                 the updated pick list and every sibling page.
5.  ``summary-anchors``        - ``#picks-at-a-glance`` and ``#unresolved-summary``
                                 exist and ``#pick-limitations`` is nested inside
                                 the summary, not on another page.
6.  ``glance-completeness-live``  - the deployed page lists exactly its own open
                                 fixtures in the at-a-glance block.
7.  ``glance-completeness-fresh`` - and it lists every fixture a fresh refresh
                                 says is open now (the "missing pick" case).
8.  ``pick-coverage``          - every open row has a pick, or is named in the
                                 limitations block with its limitation.
9.  ``probability-not-from-hotspawn`` - a published percentage always has at
                                 least one non-Hotspawn primary-source link.
10. ``freshness-copy-honest``  - a stale board says it is stale in the deployed
                                 bytes, and the client-side expiry hook ships.
11. ``mobile-markers``         - phone requirements: viewport, persistent tab bar,
                                 >=44px tap targets, and tables that collapse to
                                 cards instead of forcing a horizontal scroll.
12. ``external-evidence-reachable`` (opt-in) - the evidence links behind open
                                 rows answer, with 403/429 recorded as access
                                 limits rather than broken links.

Stdlib only, no writes to any shared path. Exit status is 1 when any finding is
a ``fail``, so CI can gate on it; ``--report-level`` narrows what is printed.
Nothing here invents a value: an unreadable source produces a finding, never a
number.
"""
import argparse
import datetime
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

LIVE_BASE = 'https://buffedlizard55-lab.github.io/MaltaProj4/'
UA = 'cs2-scout-live-audit/1.0 (session 93fafca6; +https://github.com/buffedlizard55-lab/MaltaProj4)'

# Inventory source, never a probability input (project policy, README §"Evidence
# and calculations" 1 and 5).
HOTSPAWN_HOSTS = ('play.hotspawn.com', 'phpstack-1372681-6459848.cloudwaysapps.com')

CORE_PAGES = ('index.html', 'picks.html', 'unresolved.html', 'matches.html',
              'analysis.html', 'review.html', 'sources.html', 'evidence.html',
              'methodology.html', '404.html')
CORE_ASSETS = ('assets/style.css', 'assets/app.js')
CORE_DATA = ('data/latest.json',)
# The pages a phone reader is expected to navigate between.
TABBED_PAGES = ('index.html', 'picks.html', 'unresolved.html', 'matches.html')

STALE_HOURS = 8.0
MIN_TAP_TARGET_PX = 44
PHONE_BREAKPOINT = 650

PASS, INFO, WARN, FAIL = 'pass', 'info', 'warn', 'fail'
LEVEL_ORDER = {PASS: 0, INFO: 1, WARN: 2, FAIL: 3}


# --------------------------------------------------------------------------- #
# primitives
# --------------------------------------------------------------------------- #
def utc(value):
    """Parse an ISO-8601 timestamp into an aware UTC datetime, or None."""
    if not value:
        return None
    try:
        text = str(value).strip()
        if text.endswith('Z'):
            text = text[:-1] + '+00:00'
        parsed = datetime.datetime.fromisoformat(text)
    except (ValueError, TypeError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc)


def now_utc(value=None):
    return utc(value) or datetime.datetime.now(datetime.timezone.utc)


def hours_between(later, earlier):
    if not later or not earlier:
        return None
    return (later - earlier).total_seconds() / 3600.0


def sha256_hex(payload):
    return hashlib.sha256(payload).hexdigest()


def cache_bust(url, token):
    """Append one distinct, clearly labelled argument; the canonical URL stays.

    Every pair must be a **tuple**: ``urllib.parse.urlencode`` raises
    ``TypeError: not a valid non-string sequence or mapping object`` when the
    first element of the sequence is a list, which is what ``str.split('=', 1)``
    returns. The bug stays hidden while the cache-busted URL has no query at all
    (``[] + [tuple]`` starts with a tuple), so it only fires on a URL that
    already carries arguments.
    """
    parts = urllib.parse.urlsplit(url)
    pairs = [tuple(pair.split('=', 1)) if '=' in pair else (pair, '')
             for pair in parts.query.split('&') if pair]
    query = urllib.parse.urlencode(pairs + [('_liveaudit', token)])
    return parts._replace(query=query).geturl()


def preview(items, limit=10, fmt=str):
    """Render at most ``limit`` items and say, out loud, how many were omitted.

    A truncated evidence list must never read like a complete one. An audit line
    that counts 13 missing fixtures and names 10 leaves the reader to guess the
    other three, and a guessed gap is exactly what this repository refuses to
    publish. Every call site that shortens a list therefore states the total.
    """
    shown = '; '.join(fmt(i) for i in list(items)[:limit])
    if len(items) > limit:
        shown += ' ... and %d more, %d in total (only the first %d are named here)' % (
            len(items) - limit, len(items), limit)
    return shown


def http_get(url, timeout=30):
    """Return (status, body_bytes, error). Never raises."""
    request = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*',
                                                   'Cache-Control': 'no-cache'})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read(), None
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read()
        except Exception:  # pragma: no cover - defensive
            body = b''
        return exc.code, body, 'HTTP %s' % exc.code
    except Exception as exc:  # network/DNS/TLS/timeout
        return None, b'', '%s: %s' % (type(exc).__name__, exc)


def join(base, name):
    return urllib.parse.urljoin(base if base.endswith('/') else base + '/', name)


# --------------------------------------------------------------------------- #
# html helpers (regex + a small tag matcher; no third-party parser)
# --------------------------------------------------------------------------- #
def element_slice(html, element_id):
    """Return the outer HTML of the first element carrying ``id=element_id``.

    Uses a tag counter, so nested same-name elements are handled. Returns None
    when the id is absent.
    """
    match = re.search(r'id="%s"' % re.escape(element_id), html)
    if not match:
        return None
    start = html.rfind('<', 0, match.start())
    if start < 0:
        return None
    tag_match = re.match(r'<\s*([A-Za-z][A-Za-z0-9]*)', html[start:])
    if not tag_match:
        return None
    tag = tag_match.group(1).lower()
    pattern = re.compile(r'<\s*/?\s*%s(?=[\s>/])' % re.escape(tag), re.IGNORECASE)
    depth = 0
    for found in pattern.finditer(html, start):
        token = found.group(0)
        closing = token.replace(' ', '').startswith('</')
        if closing:
            depth -= 1
            if depth == 0:
                end = html.find('>', found.end())
                return html[start:(end + 1 if end >= 0 else found.end())]
        else:
            # A self-closing tag never changes depth.
            gt = html.find('>', found.end())
            if gt >= 0 and html[gt - 1:gt] == '/':
                continue
            depth += 1
    return html[start:]


def has_element_id(html, element_id):
    return re.search(r'id="%s"' % re.escape(element_id), html) is not None


def nested_inside(html, inner_id, outer_id):
    """True when the inner element's markup sits inside the outer element's."""
    outer = element_slice(html, outer_id)
    if outer is None:
        return False
    return re.search(r'id="%s"' % re.escape(inner_id), outer) is not None


def relative_hrefs(html):
    """Every href that stays inside the site (no scheme, no protocol-relative)."""
    out = []
    for href in re.findall(r'href="([^"]+)"', html):
        if href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
            continue
        if '://' in href or href.startswith('//'):
            continue
        out.append(href)
    return out


def coverage_rows(html):
    """Rows from the page's own embedded ``#coverage-data`` JSON block."""
    block = element_slice(html, 'coverage-data')
    if block is None:
        return None
    match = re.search(r'>(\[.*\])<', block, re.DOTALL)
    if not match:
        return None
    try:
        rows = json.loads(match.group(1))
    except ValueError:
        return None
    return rows if isinstance(rows, list) else None


def glance_ids(html):
    """Fixture ids listed in ``#picks-at-a-glance``, in document order."""
    block = element_slice(html, 'picks-at-a-glance')
    if block is None:
        return None
    return re.findall(r'evidence\.html#match-(\w+)', block)


def viewport_meta(html):
    match = re.search(r'<meta[^>]+name="viewport"[^>]*>', html)
    if not match:
        return None
    return match.group(0)


def css_rule(css, selector):
    """Return the declaration body of the first rule matching ``selector``."""
    index = css.find(selector)
    if index < 0:
        return None
    brace = css.find('{', index)
    if brace < 0:
        return None
    end = css.find('}', brace)
    return css[brace + 1:end if end >= 0 else len(css)]


def px_value(declarations, prop):
    if not declarations:
        return None
    match = re.search(r'%s\s*:\s*([0-9.]+)px' % re.escape(prop), declarations)
    return float(match.group(1)) if match else None


def last_px(css, selector, prop):
    """The cascading value of ``prop`` for ``selector``: the LAST rule that sets it.

    A stylesheet can declare the same selector several times - this one sets
    ``.source-links a{min-height:32px}`` inside the general phone block and then
    ``min-height:44px`` in a later phone block, where the later rule is what a
    phone renders. Reading only the first match would report a tap target the
    deployed page does not actually use, so every exact-selector rule is scanned
    and the last declared value wins.
    """
    pattern = re.compile(r'(?<![\w.-])%s\s*\{([^{}]*)\}' % re.escape(selector))
    value = None
    for match in pattern.finditer(css or ''):
        found = px_value(match.group(1), prop)
        if found is not None:
            value = found
    return value


def media_blocks(css, max_width):
    """Every declaration body inside ``@media(max-width:<max_width>px)``."""
    bodies = []
    pattern = re.compile(r'@media\s*\(\s*max-width\s*:\s*(\d+)px\s*\)\s*\{')
    for match in pattern.finditer(css):
        if int(match.group(1)) != max_width:
            continue
        depth, index = 1, match.end()
        while index < len(css) and depth:
            if css[index] == '{':
                depth += 1
            elif css[index] == '}':
                depth -= 1
            index += 1
        bodies.append(css[match.end():index - 1])
    return bodies


# --------------------------------------------------------------------------- #
# findings
# --------------------------------------------------------------------------- #
class Report:
    def __init__(self):
        self.findings = []

    def add(self, check, level, title, detail='', links=()):
        self.findings.append({'check': check, 'level': level, 'title': title,
                              'detail': detail, 'links': list(links)})
        return self.findings[-1]

    @property
    def worst(self):
        return max((LEVEL_ORDER[f['level']] for f in self.findings), default=0)

    def counts(self):
        out = {PASS: 0, INFO: 0, WARN: 0, FAIL: 0}
        for finding in self.findings:
            out[finding['level']] += 1
        return out

    def failed(self):
        return [f for f in self.findings if f['level'] == FAIL]


# --------------------------------------------------------------------------- #
# the audit
# --------------------------------------------------------------------------- #
def audit(live, report, committed_receipt=None, head_sha=None, snapshot=None,
          now=None, check_external=False, external_limit=25, external_statuses=None):
    """Run every check against ``live`` (name -> {status, body, sha256, error}).

    ``live`` values are dicts with keys ``status`` (int or None), ``body``
    (bytes) and ``error`` (str or None). Returns the report.
    """
    now = now or now_utc()

    def text(name):
        entry = live.get(name) or {}
        body = entry.get('body') or b''
        try:
            return body.decode('utf-8', 'replace')
        except Exception:  # pragma: no cover - defensive
            return ''

    # -- 1. receipt ----------------------------------------------------------
    receipt = None
    entry = live.get('build-info.json') or {}
    if entry.get('status') == 200 and entry.get('body'):
        try:
            receipt = json.loads(entry['body'].decode('utf-8', 'replace'))
        except ValueError:
            receipt = None
    if not isinstance(receipt, dict) or not isinstance(receipt.get('files'), dict):
        report.add('receipt-readable', FAIL,
                   'The live build receipt could not be read',
                   'GET build-info.json returned status %s (%s). Without the receipt the '
                   'served revision, build time and snapshot time are unknown, so nothing '
                   'below can be dated.' % (entry.get('status'), entry.get('error') or 'unparsable'),
                   [join(LIVE_BASE, 'build-info.json')])
        return report
    built_at = utc(receipt.get('built_at'))
    snapshot_at = utc(receipt.get('snapshot_generated_at'))
    live_revision = receipt.get('revision')
    missing = [k for k in ('revision', 'built_at', 'snapshot_generated_at', 'rows') if not receipt.get(k) and receipt.get(k) != 0]
    report.add('receipt-readable', FAIL if missing else PASS,
               'Live build receipt read' + (': missing %s' % ', '.join(missing) if missing else ''),
               'revision `%s`, built `%s`, snapshot `%s`, %s rows, %d files in the manifest.'
               % (live_revision, receipt.get('built_at'), receipt.get('snapshot_generated_at'),
                  receipt.get('rows'), len(receipt['files'])),
               [join(LIVE_BASE, 'build-info.json')])

    # -- 2. publisher identity ----------------------------------------------
    age_hours = hours_between(now, snapshot_at)
    age_at_build = hours_between(built_at, snapshot_at)
    committed_revision = (committed_receipt or {}).get('revision')
    if committed_revision and live_revision == committed_revision:
        publisher = ('the committed root fallback (legacy `main:/` Pages build), revision `%s`'
                     % live_revision)
    elif head_sha and live_revision == head_sha:
        publisher = 'the verified workflow artifact for the current `main` HEAD `%s`' % head_sha[:12]
    else:
        publisher = 'a workflow artifact for commit `%s`' % (live_revision or 'unknown')
    level = INFO
    detail = ('Served by %s. Snapshot age at read time %.2f h; age when built %s h. '
              'HEAD `%s`, committed root receipt `%s`.'
              % (publisher, age_hours if age_hours is not None else -1,
                 ('%.2f' % age_at_build) if age_at_build is not None else 'unknown',
                 (head_sha or 'unspecified')[:12], (committed_revision or 'unspecified')[:12]))
    if committed_revision and live_revision == committed_revision and head_sha and live_revision != head_sha:
        level = WARN
        detail += (' The legacy publisher is serving the committed fallback instead of the fresh '
                   'artifact: this is the documented dual-publisher race, and the board a visitor '
                   'reads is not the board the last verified run produced.')
    report.add('publisher-identity', level, 'Which publisher is serving the live site', detail,
               ['https://github.com/buffedlizard55-lab/MaltaProj4/actions',
                'https://api.github.com/repos/buffedlizard55-lab/MaltaProj4/pages'])
    if age_hours is None:
        report.add('publisher-identity', FAIL, 'The served snapshot has no readable timestamp',
                   'Neither `snapshot_generated_at` nor `built_at` parses, so freshness cannot be '
                   'established and no age claim is made.')
    elif age_hours > STALE_HOURS:
        report.add('live-board-fresh', FAIL,
                   'The live board is outside its %d-hour evidence window' % int(STALE_HOURS),
                   'The served snapshot is %.2f h old (generated `%s`, read `%s`). Every percentage '
                   'on the live site is expired evidence and must not be used as a current pick. '
                   'This is a publication-state finding, not a data finding: the next verified '
                   '`pages.yml` run restores the fresh artifact.'
                   % (age_hours, receipt.get('snapshot_generated_at'), now.isoformat().replace('+00:00', 'Z')),
                   ['https://github.com/buffedlizard55-lab/MaltaProj4/actions/workflows/pages.yml'])
    else:
        report.add('live-board-fresh', PASS,
                   'The live board is inside its %d-hour evidence window' % int(STALE_HOURS),
                   'Snapshot generated `%s`, read `%s`: %.2f h old.'
                   % (receipt.get('snapshot_generated_at'), now.isoformat().replace('+00:00', 'Z'), age_hours))

    # -- 3. manifest consistency --------------------------------------------
    checked = mismatched = absent = 0
    problems = []
    for name, expected in sorted(receipt['files'].items()):
        got = live.get(name)
        if got is None or not got.get('fetched'):
            continue  # not fetched by this run; not a finding
        checked += 1
        if got.get('status') == 200:
            actual = got.get('sha256') or sha256_hex(got.get('body') or b'')
            if actual != expected:
                mismatched += 1
                problems.append('%s: manifest %s, served %s' % (name, expected[:12], actual[:12]))
        else:
            absent += 1
            problems.append('%s: HTTP %s (%s)' % (name, got.get('status'), got.get('error') or 'no response'))
    nav_absent = [p for p in problems if p.split(':')[0] in CORE_PAGES + CORE_ASSETS + CORE_DATA]
    if not checked:
        report.add('manifest-consistency', INFO, 'No manifest file was fetched by this run',
                   'Pass --files to compare the served bytes against the published SHA-256 manifest.')
    elif mismatched or nav_absent:
        report.add('manifest-consistency', FAIL,
                   'The served bytes do not match the live build manifest',
                   '%d of %d fetched files differ or are missing. A mismatch means two publishers '
                   'wrote different file sets to the same site (a torn deployment), or the manifest '
                   'is not the manifest of the served build. Details: %s'
                   % (mismatched + len(nav_absent), checked, '; '.join(problems[:12])),
                   [join(LIVE_BASE, 'build-info.json')])
    else:
        report.add('manifest-consistency', PASS,
                   'Every fetched file is byte-identical to the live manifest',
                   '%d files compared by SHA-256; %d differences; %d unavailable (non-navigation '
                   'paths only).' % (checked, mismatched, absent))

    # A route can also be missing without appearing in the served manifest at all
    # (for example when the second publisher's file set is smaller), so the core
    # navigation targets are checked directly whenever they were really fetched.
    unavailable = []
    for name in CORE_PAGES + CORE_ASSETS + CORE_DATA:
        got = live.get(name)
        if got and got.get('fetched') and got.get('status') != 200:
            unavailable.append('%s: HTTP %s (%s)' % (name, got.get('status'), got.get('error') or 'no response'))
    if unavailable:
        report.add('core-routes-available', FAIL,
                   'A core page or asset is not served by the live site',
                   '%d of the %d routes a phone reader navigates between did not answer 200: %s. '
                   'A missing route is a broken link on the live site, not a data question.'
                   % (len(unavailable), len(CORE_PAGES) + len(CORE_ASSETS) + len(CORE_DATA),
                      '; '.join(unavailable)),
                   [join(LIVE_BASE, u.split(':')[0]) for u in unavailable])
    else:
        answered = [n for n in CORE_PAGES + CORE_ASSETS + CORE_DATA
                    if (live.get(n) or {}).get('fetched')]
        report.add('core-routes-available', PASS if answered else INFO,
                   'Every fetched core route answered 200' if answered
                   else 'No core route was fetched by this run',
                   '%d routes checked: %s.' % (len(answered), ', '.join(answered[:12]) or 'none'))

    index_html = text('index.html')
    if not index_html:
        report.add('summary-links', FAIL, 'The live executive summary could not be read',
                   'GET index.html returned status %s (%s).'
                   % ((live.get('index.html') or {}).get('status'),
                      (live.get('index.html') or {}).get('error')))
        return report

    # -- 4. in-site links from the executive summary -------------------------
    hrefs = relative_hrefs(index_html)
    targets = {h.split('#')[0].split('?')[0] for h in hrefs}
    required = ('picks.html', 'unresolved.html', 'matches.html', 'analysis.html',
                'review.html', 'sources.html', 'evidence.html')
    missing_links = [r for r in required if r not in targets]
    section_nav = re.search(r'<nav[^>]*class="section-nav"[^>]*aria-label="([^"]*)"[^>]*>(.*?)</nav>',
                            index_html, re.DOTALL)
    nav_links = relative_hrefs(section_nav.group(2)) if section_nav else []
    if missing_links:
        report.add('summary-links', FAIL,
                   'The executive summary does not link every sibling page',
                   'Missing in-site targets: %s. A phone reader must reach the updated pick list, '
                   'the unresolved section and the review page without leaving the summary.'
                   % ', '.join(missing_links))
    elif not section_nav:
        report.add('summary-links', WARN,
                   'No labelled "where the picks are" navigation block was found',
                   'All %d required in-site links are present, but no `nav.section-nav` with an '
                   'aria-label was detected, so the shortcut block may have moved.'
                   % len(required))
    else:
        report.add('summary-links', PASS,
                   'The executive summary links the pick list and every sibling page',
                   '%d in-site targets found, including all %d required. The labelled shortcut nav '
                   '("%s") carries %d links: %s.'
                   % (len(targets), len(required), section_nav.group(1), len(nav_links),
                      ', '.join(sorted({l.split("#")[0] for l in nav_links})[:8])))

    # -- 5. summary anchors and nesting --------------------------------------
    anchors = ('freshness-strip', 'picks-at-a-glance', 'unresolved-summary', 'pick-limitations')
    absent_anchors = [a for a in anchors if not has_element_id(index_html, a)]
    if absent_anchors:
        report.add('summary-anchors', FAIL, 'Executive-summary anchors are missing',
                   'Absent ids: %s. These are the in-page destinations the summary links to.'
                   % ', '.join('#' + a for a in absent_anchors))
    elif not nested_inside(index_html, 'pick-limitations', 'unresolved-summary'):
        report.add('summary-anchors', FAIL,
                   '#pick-limitations is not inside the executive summary',
                   'The unresolved-picks limitations block must be a section *of* the summary '
                   '(#unresolved-summary), not a separate page, per the standing brief.')
    else:
        report.add('summary-anchors', PASS,
                   'The summary carries the glance list and the unresolved limitations block',
                   '#freshness-strip, #picks-at-a-glance and #unresolved-summary exist, and '
                   '#pick-limitations is nested inside #unresolved-summary.')

    # -- 6/7. glance completeness -------------------------------------------
    rows = coverage_rows(index_html)
    live_open = [str(r.get('id')) for r in rows if r.get('state') == 'open'] if rows else None
    ids = glance_ids(index_html)
    if rows is None:
        report.add('glance-completeness-live', WARN,
                   'The page carries no readable #coverage-data block',
                   'The embedded row index could not be parsed, so the glance list cannot be '
                   'compared against the page\u2019s own open fixtures.')
    elif ids is None:
        report.add('glance-completeness-live', FAIL, 'No #picks-at-a-glance list was found',
                   'The block is missing from the deployed executive summary.')
    else:
        glance_set, open_set = set(ids), set(live_open)
        if glance_set != open_set:
            report.add('glance-completeness-live', FAIL,
                       'The deployed glance list does not match the page\u2019s own open fixtures',
                       'Listed but not open: %s. Open but not listed: %s. (%d listed, %d open.)'
                       % (sorted(glance_set - open_set) or 'none', sorted(open_set - glance_set) or 'none',
                          len(ids), len(live_open)))
        else:
            report.add('glance-completeness-live', PASS,
                       'Every open fixture on the live board is in the at-a-glance list',
                       '%d open fixtures, %d glance rows, identical id sets, in start-time order.'
                       % (len(open_set), len(ids)))

    if snapshot is not None and ids is not None:
        fresh_rows = snapshot.get('matches') or []
        fresh_open = [str(m.get('id')) for m in fresh_rows if m.get('state') == 'open']
        fresh_at = utc(snapshot.get('generated_at'))
        lag = hours_between(fresh_at, snapshot_at) if fresh_at else None
        missing_now = [i for i in fresh_open if i not in set(ids)]
        live_only = [i for i in ids if i not in set(fresh_open)]
        if missing_now:
            names = {str(m.get('id')): ' vs '.join(m.get('teams') or []) for m in fresh_rows}
            report.add('glance-completeness-fresh', FAIL,
                       'The live board does not show %d fixture(s) that are open now' % len(missing_now),
                       'A refresh at `%s` (%s) lists these open fixtures with no row on the live '
                       'board: %s. The published board lags the lobby by %s.'
                       % (snapshot.get('generated_at'),
                          ('%.2f h' % lag) if lag is not None else 'unknown lag',
                          preview(missing_now,
                                  fmt=lambda i: '%s (%s)' % (i, names.get(i, 'unknown teams'))),
                          ('%.2f h' % lag) if lag is not None else 'an unknown interval'))
        else:
            # A paired refresh that did not itself reach `coverage: verified` can
            # agree with the live board for the wrong reason: at
            # 2026-10-21T21:24:10Z both sides were the same 3.8-day-old 98-row
            # board, so "every open fixture is present" proved nothing. That is
            # reported as a warning instead of a pass; `live-board-fresh` carries
            # the real verdict. A snapshot that reports no coverage at all is
            # left a pass, with the omission stated rather than assumed away.
            coverage = snapshot.get('coverage')
            weak = coverage is not None and coverage != 'verified'
            report.add('glance-completeness-fresh', WARN if weak else PASS,
                       'The paired refresh was not verified, so this comparison proves less' if weak
                       else 'The live board covers every fixture open in the paired fresh refresh',
                       'Refresh `%s`%s lists %d open fixtures; all %d appear on the live board. '
                       '%d live row(s) are no longer open in the refresh (%s), which is expected '
                       'when a match locks or starts between the two reads.%s'
                       % (snapshot.get('generated_at'),
                          ' reports coverage `%s` and' % coverage if coverage is not None
                          else ' reports no coverage verdict and',
                          len(fresh_open), len(fresh_open), len(live_only),
                          preview(live_only, limit=8) or 'none',
                          ' An unverified refresh can match a stale board vacuously, so this is a '
                          'warning: check `live-board-fresh` for the served snapshot\'s real age.'
                          if weak else ''))

    # -- 8/9. picks, limitations and probability sourcing --------------------
    data_entry = live.get('data/latest.json') or {}
    data = None
    if data_entry.get('status') == 200 and data_entry.get('body'):
        try:
            data = json.loads(data_entry['body'].decode('utf-8', 'replace'))
        except ValueError:
            data = None
    if not isinstance(data, dict) or not isinstance(data.get('matches'), list):
        report.add('pick-coverage', WARN, 'The live snapshot JSON could not be read',
                   'GET data/latest.json returned status %s (%s); pick coverage and probability '
                   'sourcing cannot be audited from the deployed bytes.'
                   % (data_entry.get('status'), data_entry.get('error') or 'unparsable'))
    else:
        matches = data['matches']
        open_rows = [m for m in matches if m.get('state') == 'open']
        unpicked = [m for m in open_rows if not m.get('pick')]
        priced = [m for m in open_rows if m.get('probabilities')]
        research = [m for m in open_rows if m.get('pick') and not m.get('probabilities')]
        limitations = element_slice(index_html, 'pick-limitations') or ''
        limitations_text = re.sub(r'<[^>]+>', ' ', limitations).lower()
        unnamed = []
        for row in unpicked:
            teams = [t for t in (row.get('teams') or []) if t]
            named = (str(row.get('id')) in limitations
                     or any(t.lower() in limitations_text for t in teams))
            if not named:
                unnamed.append('%s (%s)' % (row.get('id'), ' vs '.join(teams) or 'unknown teams'))
        if unnamed:
            report.add('pick-coverage', FAIL,
                       'An open fixture has no pick and is not named in the limitations block',
                       'Unnamed: %s. The brief requires every unresolved pick to appear in a '
                       'separate section with its limitation.' % '; '.join(unnamed))
        else:
            report.add('pick-coverage', PASS,
                       'Every open fixture has a pick, or is named with its limitation',
                       '%d open: %d priced, %d research-only picks, %d with no pick%s.'
                       % (len(open_rows), len(priced), len(research), len(unpicked),
                          (' - each named in #pick-limitations' if unpicked else '')))

        unlinked, hotspawn_only = [], []
        for row in priced:
            urls = [str(e.get('url') or '') for e in (row.get('evidence') or []) if isinstance(e, dict)]
            external = [u for u in urls if u.startswith('http')
                        and urllib.parse.urlsplit(u).hostname not in HOTSPAWN_HOSTS]
            if not urls:
                unlinked.append(str(row.get('id')))
            elif not external:
                hotspawn_only.append(str(row.get('id')))
        if unlinked or hotspawn_only:
            report.add('probability-not-from-hotspawn', FAIL,
                       'A published percentage lacks an external primary source',
                       'No evidence link at all: %s. Only Hotspawn links (inventory source, never a '
                       'probability input): %s.' % (unlinked or 'none', hotspawn_only or 'none'))
        else:
            hosts = sorted({urllib.parse.urlsplit(u).hostname
                            for row in priced for u in
                            [str(e.get('url') or '') for e in (row.get('evidence') or []) if isinstance(e, dict)]
                            if u.startswith('http')})
            report.add('probability-not-from-hotspawn', PASS,
                       'Every published percentage carries a non-Hotspawn primary source link',
                       '%d priced open rows, each with at least one dated external evidence link. '
                       'Evidence hosts seen: %s.' % (len(priced), preview(sorted(hosts), fmt=str) or 'none'))
        methods = {}
        for row in open_rows:
            methods[row.get('method') or 'none'] = methods.get(row.get('method') or 'none', 0) + 1
        report.add('open-row-methods', INFO, 'How the live open rows are priced',
                   ', '.join('%s: %d' % (k, v) for k, v in sorted(methods.items())))

    # -- 10. honest freshness copy ------------------------------------------
    # `scripts/build.py::fresh_strip` renders the strip against the *wall clock at
    # render time* (`fresh(data['last_attempt_at'], datetime.now())`), while the
    # receipt's `built_at` is carried over from the snapshot itself. The two only
    # coincide for an artifact built straight after a refresh. That difference is
    # used as a publisher fingerprint below, and it is why this check is written
    # against the read instant rather than against `built_at`.
    strip_match = re.search(r'<div[^>]*class="fresh-strip([^"]*)"[^>]*id="freshness-strip"[^>]*>(.*?)</div>\s*<(?:section|div)',
                            index_html, re.DOTALL)
    strip_html = strip_match.group(0) if strip_match else (element_slice(index_html, 'freshness-strip') or '')
    strip_classes = strip_match.group(1) if strip_match else ''
    says_stale = 'older than 8 hours' in strip_html or ' stale' in strip_classes
    now_stale = age_hours is not None and age_hours > STALE_HOURS
    built_stale = age_at_build is not None and age_at_build > STALE_HOURS
    if not strip_html:
        report.add('freshness-copy-honest', FAIL, 'No freshness strip was found on the live page',
                   'The first thing a phone reader needs - when this was checked and whether it is '
                   'still inside its evidence window - is absent.')
    elif now_stale and not says_stale:
        report.add('freshness-copy-honest', FAIL,
                   'Expired data is presented as current on the live page',
                   'The served snapshot is %.2f h old (over the %.0f h window) but the deployed '
                   'freshness strip does not say so. Expired evidence must never look like a live '
                   'board.' % (age_hours, STALE_HOURS))
    elif says_stale and not now_stale:
        report.add('freshness-copy-honest', WARN,
                   'The live strip says "older than 8 hours" while the receipt is fresh',
                   'Receipt snapshot `%s` is %.2f h old at read time, yet the deployed HTML warns '
                   'that it is expired. The served page was therefore rendered at a later instant '
                   'than the receipt it ships with - the signature of the committed root fallback '
                   'being republished by the legacy `main:/` Pages build (render-time staleness %s). '
                   'A reader is told the board is expired when the data itself is not.'
                   % (receipt.get('snapshot_generated_at'), age_hours,
                      'stale' if built_stale else 'not stale per the receipt'))
    else:
        appjs = text('assets/app.js')
        hook = bool(appjs) and 'live-expired' in appjs and has_element_id(index_html, 'runtime-stale')
        report.add('freshness-copy-honest', PASS if hook else WARN,
                   'The deployed freshness copy matches the served snapshot',
                   'Snapshot `%s` is %.2f h old at read time and the strip says stale=%s, so the '
                   'copy and the data agree. Client-side expiry hook (assets/app.js `live-expired` '
                   '+ #runtime-stale) %s.'
                   % (receipt.get('snapshot_generated_at'),
                      age_hours if age_hours is not None else -1, bool(says_stale),
                      'ships, so a row whose deadline passes while the page is open is re-expired '
                      'in the browser' if hook else
                      'was NOT detected, so a browser cannot re-expire a row whose deadline passes '
                      'while the page is open'))
    if strip_html and now_stale is not None:
        report.add('render-vs-receipt', INFO,
                   'Render-time fingerprint of the served HTML',
                   'Strip says stale=%s; receipt age at read time %.2f h; receipt age at its own '
                   '`built_at` %s h. A strip that is stale while the receipt is not proves the HTML '
                   'was rendered after the snapshot it carries.'
                   % (bool(says_stale), age_hours if age_hours is not None else -1,
                      ('%.2f' % age_at_build) if age_at_build is not None else 'unknown'))

    # -- 11. phone markers ---------------------------------------------------
    css = text('assets/style.css')
    phone_problems = []
    for page in CORE_PAGES:
        html = text(page)
        if not html:
            continue
        meta = viewport_meta(html)
        if not meta or 'width=device-width' not in meta:
            phone_problems.append('%s has no device-width viewport meta' % page)
    for page in TABBED_PAGES:
        html = text(page)
        if html and 'mobile-tabs' not in html:
            phone_problems.append('%s has no persistent phone tab bar (.mobile-tabs)' % page)
    if not css:
        phone_problems.append('assets/style.css could not be read, so tap targets are unverifiable')
    else:
        blocks = media_blocks(css, PHONE_BREAKPOINT)
        if not blocks:
            phone_problems.append('no @media(max-width:%dpx) phone breakpoint in the stylesheet'
                                  % PHONE_BREAKPOINT)
        else:
            joined = '\n'.join(blocks)
            tabs = last_px(joined, '.mobile-tabs a', 'min-height')
            if tabs is None:
                tabs = last_px(css, '.mobile-tabs a', 'min-height')
            if tabs is not None and tabs < MIN_TAP_TARGET_PX:
                phone_problems.append('.mobile-tabs a min-height %.0fpx is below the %dpx tap target'
                                      % (tabs, MIN_TAP_TARGET_PX))
            if 'mobile-tabs' not in joined:
                phone_problems.append('the phone breakpoint does not style .mobile-tabs')
            if not re.search(r'table\s*\{[^}]*min-width\s*:\s*0', joined):
                phone_problems.append('the phone breakpoint never resets table min-width to 0, so '
                                      'tables keep forcing a horizontal scroll on a 320px screen')
            link_target = last_px(joined, '.source-links a', 'min-height')
            if link_target is None:
                link_target = last_px(css, '.source-links a', 'min-height')
            if link_target is not None and link_target < MIN_TAP_TARGET_PX:
                phone_problems.append('.source-links a min-height %.0fpx is below the %dpx tap target'
                                      % (link_target, MIN_TAP_TARGET_PX))
            glance_target = last_px(joined, '.glance-row', 'min-height')
            if glance_target is not None and glance_target < MIN_TAP_TARGET_PX:
                phone_problems.append('.glance-row min-height %.0fpx is below the %dpx tap target'
                                      % (glance_target, MIN_TAP_TARGET_PX))
    if phone_problems:
        report.add('mobile-markers', FAIL, 'Phone-readability requirements are not met',
                   '; '.join(phone_problems))
    else:
        tabs = last_px(css, '.mobile-tabs a', 'min-height')
        link_target = last_px(css, '.source-links a', 'min-height')
        report.add('mobile-markers', PASS, 'The deployed pages meet the phone requirements',
                   'Device-width viewport on all %d readable pages; persistent .mobile-tabs bar on '
                   '%s; @media(max-width:%dpx) breakpoint present; tab tap target %s; evidence-link '
                   'tap target %s; tables collapse to cards (min-width:0) instead of scrolling '
                   'sideways.'
                   % (len([p for p in CORE_PAGES if text(p)]), '/'.join(TABBED_PAGES),
                      PHONE_BREAKPOINT, ('%.0fpx' % tabs) if tabs else 'declared',
                      ('%.0fpx' % link_target) if link_target else 'declared'))

    # -- 12. external evidence reachability (opt-in) -------------------------
    if check_external and isinstance(data, dict) and isinstance(data.get('matches'), list):
        statuses = external_statuses if external_statuses is not None else {}
        urls = []
        for row in data['matches']:
            if row.get('state') != 'open':
                continue
            for evidence in row.get('evidence') or []:
                url = str((evidence or {}).get('url') or '')
                if url.startswith('http') and url not in urls:
                    urls.append(url)
        broken, limited = [], []
        for url in urls[:external_limit]:
            status = statuses.get(url)
            if status is None:
                status, _, _ = http_get(url, timeout=25)
            if status in (404, 410):
                broken.append('%s -> HTTP %s' % (url, status))
            elif status != 200:
                limited.append('%s -> %s' % (url, status if status else 'unreachable'))
        if broken:
            report.add('external-evidence-reachable', FAIL,
                       'A primary source link behind an open row does not resolve',
                       preview(broken))
        else:
            report.add('external-evidence-reachable', WARN if limited else PASS,
                       'Primary source links behind open rows were re-requested',
                       '%d distinct URLs checked. %d answered 200. Access-limited or unanswered '
                       '(recorded, not treated as broken, and never bypassed): %s'
                       % (min(len(urls), external_limit),
                          max(0, min(len(urls), external_limit) - len(limited)),
                          preview(limited) or 'none'))
    return report


# --------------------------------------------------------------------------- #
# fetching
# --------------------------------------------------------------------------- #
def collect(base_url, names, token='1', timeout=30, fetcher=http_get):
    """Fetch each name from the live site, cache-busted, returning the live dict."""
    live = {}
    for name in names:
        url = cache_bust(join(base_url, name), token)
        status, body, error = fetcher(url, timeout=timeout)
        live[name] = {'status': status, 'body': body, 'error': error, 'fetched': True,
                      'sha256': sha256_hex(body) if body else None, 'url': url,
                      'canonical_url': join(base_url, name)}
    return live


def load_offline(directory, names):
    """Read saved bytes from a directory instead of the network."""
    live = {}
    root = Path(directory)
    for name in names:
        path = root / name
        if path.exists():
            body = path.read_bytes()
            live[name] = {'status': 200, 'body': body, 'error': None, 'fetched': True,
                          'sha256': sha256_hex(body), 'url': str(path),
                          'canonical_url': join(LIVE_BASE, name)}
        else:
            # Never fetched, so never a finding: an offline copy only proves
            # something about the files that were actually saved.
            live[name] = {'status': None, 'body': b'', 'error': 'not saved offline',
                          'fetched': False, 'sha256': None, 'url': str(path),
                          'canonical_url': join(LIVE_BASE, name)}
    return live


def save_receipts(live, directory, keep=('build-info.json', 'index.html')):
    """Persist a small, dated copy of the served bytes for line-by-line review."""
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    saved = []
    for name in keep:
        entry = live.get(name) or {}
        if entry.get('status') == 200 and entry.get('body'):
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(entry['body'])
            saved.append({'name': name, 'bytes': len(entry['body']),
                          'sha256': entry.get('sha256'), 'path': str(target)})
    manifest = root / 'live-files.json'
    manifest.write_text(json.dumps(
        [{'name': name, 'status': (e or {}).get('status'), 'error': (e or {}).get('error'),
          'sha256': (e or {}).get('sha256'), 'bytes': len((e or {}).get('body') or b''),
          'url': (e or {}).get('canonical_url')} for name, e in sorted(live.items())],
        indent=2, sort_keys=True) + '\n')
    saved.append({'name': 'live-files.json', 'path': str(manifest)})
    return saved


# --------------------------------------------------------------------------- #
# reporting
# --------------------------------------------------------------------------- #
def to_markdown(report, context):
    counts = report.counts()
    base = context.get('base_url') or ''
    source = ('Read at `%s` from the offline copy `%s`.' % (context.get('read_at'), base)
              if base.startswith('offline copy') else
              'Read at `%s` from <%s>.' % (context.get('read_at'), base))
    lines = ['# Independent audit of the live published site',
             '',
             source,
             '',
             '| Check | Level | Finding |', '| --- | --- | --- |']
    for finding in report.findings:
        lines.append('| `%s` | %s | %s |' % (finding['check'], finding['level'].upper(),
                                             finding['title'].replace('|', '\\|')))
    lines += ['',
              '**%d pass · %d info · %d warn · %d fail**' % (counts[PASS], counts[INFO],
                                                             counts[WARN], counts[FAIL]), '',
              '## Detail', '']
    for finding in report.findings:
        lines.append('### `%s` — %s' % (finding['check'], finding['level'].upper()))
        lines.append('')
        lines.append('**%s**' % finding['title'])
        lines.append('')
        if finding['detail']:
            lines.append(finding['detail'])
            lines.append('')
        for link in finding['links']:
            lines.append('- <%s>' % link)
        if finding['links']:
            lines.append('')
    lines += ['## Served files', '',
              '| File | HTTP | SHA-256 (served) |', '| --- | --- | --- |']
    for name, entry in sorted((context.get('live_index') or {}).items()):
        lines.append('| `%s` | %s | `%s` |' % (name, entry.get('status'),
                                               (entry.get('sha256') or '-')[:16]))
    lines.append('')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--base-url', default=LIVE_BASE)
    parser.add_argument('--offline-dir', default=None,
                        help='read saved bytes from this directory instead of fetching')
    parser.add_argument('--save-dir', default=None, help='persist fetched bytes and an index here')
    parser.add_argument('--files', default=None,
                        help='comma-separated site paths; default is the live manifest plus core pages')
    parser.add_argument('--snapshot', default=None,
                        help='a same-minute scripts.refresh snapshot to compare open-fixture coverage against')
    parser.add_argument('--head-sha', default=None, help='current main HEAD, to identify the publisher')
    parser.add_argument('--committed-receipt', default='build-info.json',
                        help='repo root build-info.json (the legacy fallback the root publisher serves)')
    parser.add_argument('--check-external', action='store_true',
                        help='re-request the primary source links behind open rows')
    parser.add_argument('--external-limit', type=int, default=25)
    parser.add_argument('--external-statuses', default=None,
                        help='JSON file mapping URL -> status, to replay a recorded reachability run')
    parser.add_argument('--now', default=None, help='override the read instant (tests only)')
    parser.add_argument('--output', default=None, help='write the markdown report here')
    parser.add_argument('--json', dest='json_out', default=None, help='write the findings JSON here')
    parser.add_argument('--token', default=None, help='cache-busting token (default: the read instant)')
    args = parser.parse_args(argv)

    now = now_utc(args.now)
    token = args.token or now.strftime('%Y%m%dT%H%M%SZ')

    committed = None
    if args.committed_receipt and Path(args.committed_receipt).exists():
        try:
            committed = json.loads(Path(args.committed_receipt).read_text())
        except ValueError:
            committed = None

    # The manifest is read first so the file list comes from the served build.
    if args.offline_dir:
        probe = load_offline(args.offline_dir, ['build-info.json'])
    else:
        probe = collect(args.base_url, ['build-info.json'], token=token)
    names = ['build-info.json']
    try:
        receipt = json.loads((probe['build-info.json']['body'] or b'{}').decode('utf-8', 'replace'))
        names += sorted(receipt.get('files') or {})
    except ValueError:
        receipt = {}
    for extra in CORE_PAGES + CORE_ASSETS + CORE_DATA:
        if extra not in names:
            names.append(extra)
    if args.files:
        names = [n.strip() for n in args.files.split(',') if n.strip()]
        if 'build-info.json' not in names:
            names.insert(0, 'build-info.json')

    if args.offline_dir:
        live = load_offline(args.offline_dir, names)
        if not (live.get('build-info.json') or {}).get('body'):
            live['build-info.json'] = probe['build-info.json']
    else:
        live = collect(args.base_url, names, token=token)

    snapshot = None
    if args.snapshot and Path(args.snapshot).exists():
        try:
            snapshot = json.loads(Path(args.snapshot).read_text())
        except ValueError:
            snapshot = None

    statuses = None
    if args.external_statuses and Path(args.external_statuses).exists():
        try:
            statuses = json.loads(Path(args.external_statuses).read_text())
        except ValueError:
            statuses = None

    report = Report()
    audit(live, report, committed_receipt=committed, head_sha=args.head_sha, snapshot=snapshot,
          now=now, check_external=args.check_external, external_limit=args.external_limit,
          external_statuses=statuses)

    context = {'read_at': now.isoformat().replace('+00:00', 'Z'),
               'base_url': ('offline copy at %s (canonical base %s)' % (args.offline_dir, args.base_url)
                            if args.offline_dir else args.base_url),
               'live_index': {n: {'status': e.get('status'), 'sha256': e.get('sha256'),
                                  'error': e.get('error')} for n, e in live.items()},
               'counts': report.counts(), 'head_sha': args.head_sha,
               'committed_revision': (committed or {}).get('revision')}
    markdown = to_markdown(report, context)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(markdown)
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(json.dumps(
            {'context': context, 'findings': report.findings}, indent=2, ensure_ascii=False) + '\n')
    if args.save_dir:
        save_receipts(live, args.save_dir)
    print(markdown)
    return 1 if report.failed() else 0


if __name__ == '__main__':
    sys.exit(main())
