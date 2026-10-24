"""Independent, zero-dependency re-derivation of every published CS2 row.

This module shares **no code** with ``scripts/`` on purpose. Everything it knows
about a row is either in the snapshot itself (the stored evidence, the raw
exchange response fields, the Valve standings points and the documented formula)
or in the HTML this repository publishes. If a number cannot be rebuilt from
those inputs alone, this verifier fails the row; it never fills a value in.

Checks, per row (``R`` ids are reported in the output):

R1  the row's state is one of the states the site publishes, and ``lock`` does
    not fall after ``start`` (Hotspawn's pick lock is at or before kick-off);
R2  a pick, when present, is exactly one of the two named teams;
R3  a two-sided probability is two finite numbers in (0, 1) that sum to 1;
R4  the pick is the higher-probability side (or the row publishes no
    probability, in which case it must be a labelled research row);
R5  ``fair_odds[i] == 1 / p[i]`` to 1e-9;
R6  the published probabilities are re-derived from the stored source:
      * Polymarket exchange row -> raw ``outcomePrices`` normalised to sum 1;
      * bookmaker row           -> decimal odds inverted and de-vigged, and the
                                   stored overround re-computed from those odds;
      * Valve VRS model row     -> Valve's own published formula, implemented
                                   here from the documented constants, applied
                                   to the stored points;
R7  every row carries at least one absolute https link on a documented official
    host, and no ``http://`` link anywhere;
R8  ``expires_at`` is not later than the earliest of the lock, the start and the
    row's own observation + 8 hours;
R9  a row with no pick must record a reason and at least one attempted source,
    and must not publish a probability;
R10 the research (no-number) tiers must resolve to the team the stored evidence
    names, and must not publish probabilities.

Site checks (``S`` ids):

S1  every open row appears exactly once as a ``data-match`` row in
    ``picks.html`` and once in ``index.html``'s pick list;
S2  every one of those rows carries an outbound official https source link;
S3  every relative link and anchor in every published page resolves to a real
    file and a real ``id`` (no broken internal navigation);
S4  ``index.html`` links to ``picks.html`` and ``unresolved.html`` from the
    executive summary, above the pick list;
S5  the unresolved/limitations section exists on ``index.html`` and names every
    open row that has no probability.

Usage:
    python verification-93f6951a/verify_board.py [--data data/latest.json]
        [--site .] [--json OUT] [--markdown OUT] [--selftest]
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

# --- documented constants -------------------------------------------------
# Valve's own model code, read at the pinned commit this project links to:
#   model/fit.js   defaultGlickoParams.rd = 75
#   model/fit.js   priorWinExpectation() compares the rank delta of a win with
#                  the rank delta of a loss with a fixed RD, which reduces to
#                  the Glicko expected score below.
VRS_RATING_DEVIATION = 75.0
VRS_Q = math.log(10) / 400.0
VRS_G = 1.0 / math.sqrt(1.0 + 3.0 * VRS_Q * VRS_Q * VRS_RATING_DEVIATION ** 2 / math.pi ** 2)

# Hosts this project accepts as a *primary* source for a row. Everything else is
# allowed as context, but a row without one of these is not source-linked.
OFFICIAL_HOSTS = (
    'hotspawn.com', 'play.hotspawn.com',
    'hltv.org',
    'polymarket.com', 'gamma-api.polymarket.com',
    'github.com',                      # Valve's official standings repository
    'valvesoftware.com',
    'pinnacle.com', 'api.pinnacle.com',
    'bo3.gg',
    'thunderpick.io', 'thunderpick.com',
    'gg.bet',
    'egamersworld.com',
    'liquipedia.net',
)

MODEL_METHODS = ('model_vrs', 'model_vrs_mirror')
EXCHANGE_METHODS = ('exchange', 'exchange_wide')
BOOK_METHODS = ('bookmaker', 'bookmaker_fallback', 'pinnacle')
RESEARCH_METHODS = ('research_rank', 'research_rank_single', 'research_vrs_single', 'research_form')


def fold(name) -> str:
    """Case-, diacritic- and punctuation-insensitive form of a team label."""
    text = unicodedata.normalize('NFKD', str(name or ''))
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = text.casefold()
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    return ' '.join(text.split())


def official(host: str) -> bool:
    host = (host or '').lower()
    return any(host == h or host.endswith('.' + h) for h in OFFICIAL_HOSTS)


def parse_time(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def vrs_expected(points_a, points_b):
    """Glicko expected score with RD 75 — Valve's priorWinExpectation reduction."""
    return 1.0 / (1.0 + 10 ** (-VRS_G * (float(points_a) - float(points_b)) / 400.0))


def calibrated(raw, slope):
    return 0.5 + float(slope) * (raw - 0.5)


def links_in(value, found=None):
    """Collect every absolute http(s) URL anywhere inside a nested structure."""
    found = [] if found is None else found
    if isinstance(value, str):
        found.extend(re.findall(r'https?://[^\s"\'<>)]+', value))
    elif isinstance(value, dict):
        for item in value.values():
            links_in(item, found)
    elif isinstance(value, (list, tuple)):
        for item in value:
            links_in(item, found)
    return found


class RowVerifier:
    def __init__(self, identities=None):
        self.checks = 0
        self.failures = []
        # canonical label -> set of folded names, built from the repository's own
        # reviewed register. Every entry must carry an https source, or the alias
        # is not usable as a name mapping at all.
        self.aliases = {}
        self.alias_problems = []
        for entry in (identities or {}).get('aliases', []):
            source = str(entry.get('source') or '')
            names = entry.get('names') or []
            if not source.startswith('https://'):
                self.alias_problems.append('alias %r has no https source' % (entry.get('canonical'),))
                continue
            group = {fold(n) for n in names if n}
            for name in group:
                self.aliases.setdefault(name, set()).update(group)

    def same_team(self, fixture_name, source_name, abbreviation=None):
        """True when both labels provably mean the same club.

        Three documented routes, and nothing else:

        1. folding (case, diacritics, punctuation) — a spelling difference, not a
           judgement (``LOS NINOS`` / ``Los Niños``);
        2. a reviewed entry in ``data/identities.json`` that itself links an https
           source (``BakS`` / ``BakS eSports``);
        3. the exchange's own published team record: the methodology accepts
           "Polymarket's own published team abbreviations" as a mapping, so an
           abbreviation that folds to the fixture label is accepted (measured on
           the 2026-10-24 board: outcome ``UNiTY esports``, abbreviation
           ``unity``, fixture ``UNiTY`` — Polymarket team 170947).

        An unregistered label without such a record is a failure, never a fuzzy
        match.
        """
        if fold(fixture_name) == fold(source_name):
            return True
        group = self.aliases.get(fold(fixture_name))
        if group and fold(source_name) in group:
            return True
        return bool(abbreviation) and fold(abbreviation) == fold(fixture_name)

    def check(self, ok, row_id, code, message):
        self.checks += 1
        if not ok:
            self.failures.append({'row': row_id, 'code': code, 'message': message})
        return ok

    # -- individual rows ---------------------------------------------------
    def verify_row(self, row):
        rid = str(row.get('id'))
        state = row.get('state')
        start = parse_time(row.get('start'))
        lock = parse_time(row.get('lock'))

        self.check(state in ('open', 'not_open'), rid, 'R1',
                   'state %r is not a published state' % state)
        if start and lock:
            self.check(lock <= start, rid, 'R1',
                       'lock %s falls after start %s' % (lock, start))

        teams = row.get('teams') or []
        self.check(len(teams) == 2 and all(isinstance(t, str) and t.strip() for t in teams),
                   rid, 'R1', 'teams must be two non-empty names, got %r' % (teams,))

        pick = row.get('pick')
        probs = row.get('probabilities')
        if state != 'open':
            # A closed row publishes no current recommendation by design.
            self.check(pick in (None, '', []), rid, 'R2',
                       'a closed row carries a pick (%r); historical picks are not current picks' % (pick,))
            return

        if pick not in (None, '', []):
            self.check(pick in teams, rid, 'R2', 'pick %r is not one of the two teams %r' % (pick, teams))

        if probs is not None:
            ok = isinstance(probs, list) and len(probs) == 2
            self.check(ok, rid, 'R3', 'probabilities must be two numbers, got %r' % (probs,))
            if ok:
                a, b = probs
                self.check(all(isinstance(x, (int, float)) and math.isfinite(x) and 0 < x < 1 for x in (a, b)),
                           rid, 'R3', 'probability outside (0,1): %r' % (probs,))
                self.check(abs((a + b) - 1.0) <= 1e-9, rid, 'R3',
                           'probabilities sum to %r, not 1' % (a + b))
                if pick in teams:
                    self.check(pick == teams[0] if a >= b else pick == teams[1], rid, 'R4',
                               'pick %r is not the higher-probability side (%r for %r)' % (pick, probs, teams))
                self.check(a != b, rid, 'R4', 'a priced row must be directional, got %r' % (probs,))

                fair = row.get('fair_odds')
                self.check(isinstance(fair, list) and len(fair) == 2, rid, 'R5',
                           'fair_odds missing for a priced row')
                if isinstance(fair, list) and len(fair) == 2:
                    for p, f in zip(probs, fair):
                        self.check(abs(f - 1.0 / p) <= 1e-9, rid, 'R5',
                                   'fair odds %r is not 1/%r' % (f, p))
                self.re_derive(rid, row, probs)
        else:
            # A pick shown without a percentage must say which research tier
            # produced it; otherwise the page is presenting an unlabelled pick.
            self.check(pick in (None, '', []) or row.get('method') in RESEARCH_METHODS,
                       rid, 'R4',
                       'a pick published without a probability must be labelled with a research '
                       'tier, method=%r' % (row.get('method'),))

        # R7 - source links
        urls = links_in(row)
        absolute = [u for u in urls if urlsplit(u).scheme in ('http', 'https')]
        self.check(any(urlsplit(u).scheme == 'https' and official(urlsplit(u).hostname or '')
                       for u in absolute), rid, 'R7',
                   'no https link on a documented official host')
        self.check(not [u for u in absolute if urlsplit(u).scheme == 'http'], rid, 'R7',
                   'row contains an insecure http:// link')

        # R8 - expiry
        expires = parse_time(row.get('expires_at'))
        if probs is not None:
            self.check(expires is not None, rid, 'R8', 'a priced row must carry an expiry')
            if expires:
                ceilings = [t for t in (start, lock) if t]
                observation = parse_time((row.get('evidence') or [{}])[0].get('observed_at')) \
                    if row.get('evidence') and isinstance(row['evidence'][0], dict) else None
                if observation:
                    ceilings.append(observation + timedelta(hours=8))
                self.check(not ceilings or expires <= min(ceilings), rid, 'R8',
                           'expiry %s is later than its earliest ceiling %s'
                           % (expires, min(ceilings) if ceilings else None))

        # R9 - an unresolved row must say why and what it tried
        if pick in (None, '', []):
            self.check(bool((row.get('reason') or '').strip()), rid, 'R9',
                       'a row with no pick must record a reason')
            self.check(bool(row.get('attempts')), rid, 'R9',
                       'a row with no pick must record at least one attempted source')
            self.check(probs is None, rid, 'R9',
                       'a row with no pick must not publish a probability')

        # R10 - research picks must be re-derivable from the stored evidence
        if row.get('method') in RESEARCH_METHODS:
            self.check(probs is None, rid, 'R10',
                       'research tier %r must publish no probability' % row.get('method'))
            self.check(self.research_pick_holds(row), rid, 'R10',
                       'research pick %r is not supported by the stored evidence' % (pick,))

    def re_derive(self, rid, row, probs):
        method = row.get('method') or ''
        evidence = row.get('evidence') or []
        teams = row.get('teams') or []
        self.check(bool(evidence), rid, 'R6', 'a priced row has no stored evidence')
        if not evidence:
            return
        ev = evidence[0]

        if method in EXCHANGE_METHODS:
            raw = ev.get('raw') or {}
            try:
                outcomes = json.loads(raw.get('outcomes') or '[]')
                prices = json.loads(raw.get('outcomePrices') or '[]')
            except (TypeError, ValueError):
                self.check(False, rid, 'R6', 'exchange row has unparseable outcomes')
                return
            ok = len(outcomes) == 2 and len(prices) == 2
            self.check(ok, rid, 'R6', 'exchange row must carry two outcomes and two prices')
            if not ok:
                return
            try:
                x = [float(p) for p in prices]
            except (TypeError, ValueError):
                self.check(False, rid, 'R6', 'exchange prices are not numeric')
                return
            total = sum(x)
            self.check(total > 0, rid, 'R6', 'exchange prices sum to zero')
            # The exchange's own team records carry the abbreviations the
            # methodology accepts as a label mapping, keyed by the outcome name.
            abbreviations = {}
            for record in (ev.get('team_metadata') or []):
                if isinstance(record, dict) and record.get('name'):
                    abbreviations[fold(record['name'])] = record.get('abbreviation')
            for team, published in zip(teams, probs):
                values = [share / total for name, share in zip(outcomes, x)
                          if self.same_team(team, name, abbreviations.get(fold(name)))]
                if not values:
                    self.check(False, rid, 'R6',
                               'evidence outcomes %r do not name fixture team %r and neither the '
                               'register nor a published abbreviation maps them' % (outcomes, team))
                    continue
                self.check(len(values) == 1, rid, 'R6',
                           'more than one exchange outcome maps to fixture team %r' % (team,))
                self.check(abs(values[0] - published) <= 1e-9, rid, 'R6',
                           'published %r for %r != re-derived %r'
                           % (published, team, round(values[0], 9)))
            return

        if method in BOOK_METHODS:
            raw = ev.get('raw') or {}
            odds = ev.get('decimal_odds') or raw.get('odds')
            self.check(isinstance(odds, list) and len(odds) == 2, rid, 'R6',
                       'bookmaker row must carry two decimal odds')
            if not (isinstance(odds, list) and len(odds) == 2):
                return
            try:
                odds = [float(o) for o in odds]
            except (TypeError, ValueError):
                self.check(False, rid, 'R6', 'bookmaker odds are not numeric')
                return
            self.check(all(o > 1.0 for o in odds), rid, 'R6', 'decimal odds must exceed 1.0')
            q = [1.0 / o for o in odds]
            total = sum(q)
            derived = [v / total for v in q]
            for published, value in zip(probs, derived):
                self.check(abs(published - value) <= 1e-9, rid, 'R6',
                           'published %r != de-vigged %r' % (published, value))
            if ev.get('overround') is not None:
                self.check(abs(float(ev['overround']) - (total - 1.0)) <= 1e-6, rid, 'R6',
                           'recorded overround %r != re-computed %r'
                           % (ev['overround'], total - 1.0))
            return

        if method in MODEL_METHODS:
            points = ev.get('points')
            self.check(isinstance(points, list) and len(points) == 2, rid, 'R6',
                       'model row must carry two VRS points values')
            if not (isinstance(points, list) and len(points) == 2):
                return
            try:
                a, b = float(points[0]), float(points[1])
            except (TypeError, ValueError):
                self.check(False, rid, 'R6', 'model points are not numeric')
                return
            self.check(a != b, rid, 'R6', 'identical points cannot produce a directional model line')
            raw = vrs_expected(a, b)
            slope = ev.get('calibration_slope')
            self.check(slope is not None, rid, 'R6', 'model row must record its calibration slope')
            if slope is None:
                return
            p1 = calibrated(raw, slope)
            self.check(abs(p1 - probs[0]) <= 1e-9, rid, 'R6',
                       'published %r != formula %r (points %r)' % (probs[0], p1, points))
            self.check(abs((1 - p1) - probs[1]) <= 1e-9, rid, 'R6',
                       'second side %r != 1 - %r' % (probs[1], p1))
            recorded = ev.get('raw_expected')
            if isinstance(recorded, list) and recorded:
                self.check(abs(float(recorded[0]) - raw) <= 1e-9, rid, 'R6',
                           'recorded raw expectation %r != %r' % (recorded[0], raw))
            return

        # Any other method that publishes a number must still be documented here.
        self.check(False, rid, 'R6', 'method %r has no independent re-derivation path' % (method,))

    def research_pick_holds(self, row):
        pick = row.get('pick')
        ev = (row.get('evidence') or [{}])[0]
        ranks = ev.get('ranks') or ev.get('team_ranks')
        if isinstance(ranks, list) and len(ranks) == 2 and all(isinstance(r, int) and r > 0 for r in ranks):
            return pick == (row['teams'][0] if ranks[0] < ranks[1] else row['teams'][1])
        # one-sided tiers: the listed team is the pick, the other is absent
        listed = ev.get('listed') or ev.get('listed_team') or ev.get('vrs_team')
        if isinstance(listed, str) and listed:
            return pick == listed
        form = ev.get('form') or ev.get('recent_form')
        if isinstance(form, dict):
            a = form.get('team1_wins', form.get('home_wins'))
            b = form.get('team2_wins', form.get('away_wins'))
            if isinstance(a, int) and isinstance(b, int) and a != b:
                return pick == (row['teams'][0] if a > b else row['teams'][1])
        return False


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.rows = []          # (match id, list of href)
        self._current = None
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if 'id' in attributes:
            self.ids.add(attributes['id'])
        if tag == 'a' and attributes.get('href'):
            self.links.append(attributes['href'])
        if 'data-match' in attributes:
            self.rows.append({'id': attributes['data-match'], 'hrefs': [], 'state': attributes.get('data-status')})
            self._current = self.rows[-1]
        elif tag == 'a' and self._current is not None and attributes.get('href'):
            self._current['hrefs'].append(attributes['href'])

    def handle_endtag(self, tag):
        if tag == 'tr' and self._current is not None:
            self._current = None


def parse_page(path):
    parser = Anchors()
    parser.feed(Path(path).read_text(encoding='utf-8', errors='replace'))
    return parser


class SiteVerifier(RowVerifier):
    def __init__(self, root, identities=None):
        super().__init__(identities)
        self.root = Path(root)

    def page(self, name):
        return self.root / name

    def verify_site(self, snapshot):
        pages = sorted(p.name for p in self.root.glob('*.html'))
        parsed = {name: parse_page(self.page(name)) for name in pages}
        for name, data in parsed.items():
            for href in data.links:
                self.check_site_link(name, href, parsed)

        open_rows = [r for r in snapshot.get('matches', []) if r.get('state') == 'open']
        picks = parsed.get('picks.html')
        index = parsed.get('index.html')
        self.check(picks is not None, 'site', 'S1', 'picks.html is missing')
        self.check(index is not None, 'site', 'S1', 'index.html is missing')
        if not picks or not index:
            return
        picks_by_id = {}
        for row in picks.rows:
            picks_by_id.setdefault(row['id'], []).append(row)
        index_ids = {row['id'] for row in index.rows}

        index_html = self.page('index.html').read_text(encoding='utf-8', errors='replace')
        for row in open_rows:
            rid = str(row['id'])
            found = picks_by_id.get(rid, [])
            self.check(len(found) == 1, rid, 'S1',
                       'picks.html must carry this open row exactly once, found %d' % len(found))
            # The executive summary names every open fixture in its glance list
            # (data-glance-* markup), which deliberately carries no data-match so
            # the validator keeps one rendered table row per fixture.
            self.check(rid in index_html, rid, 'S1',
                       'the executive summary never names this open row')
            for entry in found:
                self.check(any(urlsplit(h).scheme == 'https' and official(urlsplit(h).hostname or '')
                               for h in entry['hrefs'] if h.startswith('http')), rid, 'S2',
                           'the picks.html row carries no outbound official https source link')

        html = index_html
        self.check('picks.html' in html, 'site', 'S4', 'index.html never links to picks.html')
        self.check('unresolved.html' in html, 'site', 'S4', 'index.html never links to unresolved.html')
        self.check('id="unresolved-summary"' in html or 'unresolved-summary' in html, 'site', 'S5',
                   'the executive summary has no unresolved/limitations section')
        for row in open_rows:
            if not row.get('probabilities'):
                self.check(str(row['id']) in html, 'site', 'S5',
                           'an unpriced open row is not named in the summary')

    def check_site_link(self, page, href, parsed):
        self.checks += 1
        parts = urlsplit(href)
        if parts.scheme in ('mailto', 'tel', 'javascript'):
            return
        if parts.scheme in ('http', 'https'):
            if parts.scheme == 'http':
                self.failures.append({'row': page, 'code': 'S3', 'message': 'insecure link %s' % href})
            return
        target = parts.path or page
        target_path = (self.root / target).resolve()
        if target_path.is_dir():
            target_path = target_path / 'index.html'
        if not target_path.exists():
            self.failures.append({'row': page, 'code': 'S3',
                                  'message': 'link %r targets a missing file %r' % (href, target)})
            return
        if parts.fragment and target_path.suffix == '.html':
            ids = parsed.get(target_path.name)
            if ids is None:
                ids = parse_page(target_path)
            if parts.fragment not in ids.ids and not self.fragment_is_generated(parts.fragment):
                self.failures.append({'row': page, 'code': 'S3',
                                      'message': 'link %r targets a missing anchor %r' % (href, parts.fragment)})

    @staticmethod
    def fragment_is_generated(fragment):
        # Anchors created client-side by site/assets/app.js from the row data.
        return fragment in ('main', 'top') or fragment.startswith('match-')


def selftest(snapshot):
    """Corrupt the snapshot in known ways and prove the verifier refuses each."""
    import copy

    def run(mutate):
        bad = copy.deepcopy(snapshot)
        rows = [r for r in bad['matches'] if r.get('state') == 'open' and r.get('probabilities')]
        if not rows:
            raise SystemExit('selftest needs at least one priced open row')
        mutate(rows[0])
        verifier = RowVerifier(load_identities())
        for row in bad['matches']:
            verifier.verify_row(row)
        return verifier.failures

    cases = {
        'pick is not a team': lambda r: r.__setitem__('pick', 'Nobody FC'),
        'probabilities sum to 1.01': lambda r: r.__setitem__('probabilities', [r['probabilities'][0] + 0.01,
                                                                             r['probabilities'][1]]),
        'pick is the underdog': lambda r: r.__setitem__('pick', r['teams'][1] if r['pick'] == r['teams'][0]
                                                        else r['teams'][0]),
        'fair odds off by 1%': lambda r: r.__setitem__('fair_odds', [r['fair_odds'][0] * 1.01,
                                                                    r['fair_odds'][1]]),
        'no official source link': lambda r: (r.__setitem__('evidence', []),
                                              r.__setitem__('fixture_sources', []),
                                              r.__setitem__('source_url', '')),
        'expiry after kick-off': lambda r: r.__setitem__('expires_at', r['start']),
        'unpriced row with no reason and no attempts': lambda r: (r.__setitem__('probabilities', None),
                                                                 r.__setitem__('fair_odds', None),
                                                                 r.__setitem__('method', None),
                                                                 r.__setitem__('pick', None),
                                                                 r.__setitem__('attempts', []),
                                                                 r.__setitem__('reason', '')),
        'research pick that hides a number': lambda r: (r.__setitem__('probabilities', None),
                                                        r.__setitem__('fair_odds', None),
                                                        r.__setitem__('method', 'research_rank'),
                                                        r.__setitem__('reason', 'x')),
        'https downgraded to http': lambda r: r.__setitem__('source_url', 'http://example.com/x'),
    }
    caught = {}
    for name, mutate in cases.items():
        failures = run(mutate)
        caught[name] = bool(failures)
    return caught


def load_identities(path='data/identities.json'):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', default='data/latest.json')
    parser.add_argument('--site', default='.')
    parser.add_argument('--json', dest='json_out')
    parser.add_argument('--markdown', dest='markdown_out')
    parser.add_argument('--no-site', action='store_true',
                        help='verify rows only; skip the rendered-page checks')
    parser.add_argument('--selftest', action='store_true')
    args = parser.parse_args(argv)

    snapshot = json.loads(Path(args.data).read_text())
    verifier = SiteVerifier(args.site, load_identities())
    for row in snapshot.get('matches', []):
        verifier.verify_row(row)
    if not args.no_site:
        verifier.verify_site(snapshot)

    open_rows = [r for r in snapshot.get('matches', []) if r.get('state') == 'open']
    report = {
        'snapshot_generated_at': snapshot.get('generated_at'),
        'rows': len(snapshot.get('matches', [])),
        'open_rows': len(open_rows),
        'open_with_pick': sum(1 for r in open_rows if r.get('pick')),
        'open_with_probability': sum(1 for r in open_rows if r.get('probabilities')),
        'open_unpriced': sum(1 for r in open_rows if not r.get('probabilities')),
        'checks': verifier.checks,
        'failures': verifier.failures,
        'failure_count': len(verifier.failures),
    }
    if args.selftest:
        report['selftest'] = selftest(snapshot)
        report['selftest_all_caught'] = all(report['selftest'].values())

    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(json.dumps(report, indent=1) + '\n')
    if args.markdown_out:
        lines = ['# Independent verification — session 93f6951a', '',
                 'Snapshot `%s` · %d rows · %d open · %d with a pick · %d with a probability · '
                 '%d unpriced · **%d checks / %d failures**'
                 % (report['snapshot_generated_at'], report['rows'], report['open_rows'],
                    report['open_with_pick'], report['open_with_probability'],
                    report['open_unpriced'], report['checks'], report['failure_count']), '']
        if report['failures']:
            lines.extend(['## Failures', '', '| row | code | detail |', '| --- | --- | --- |'])
            for failure in report['failures']:
                lines.append('| %s | %s | %s |' % (failure['row'], failure['code'],
                                                   failure['message'].replace('|', '/')))
        else:
            lines.append('No failures: every open row re-derived from its own stored evidence.')
        if args.selftest:
            lines.extend(['', '## Self-test (the verifier must catch each corruption)', '',
                          '| corruption | caught |', '| --- | --- |'])
            for name, ok in report['selftest'].items():
                lines.append('| %s | %s |' % (name, 'yes' if ok else '**NO**'))
        Path(args.markdown_out).write_text('\n'.join(lines) + '\n')

    print(json.dumps({k: report[k] for k in ('rows', 'open_rows', 'open_with_pick',
                                             'open_with_probability', 'open_unpriced',
                                             'checks', 'failure_count')}, indent=1))
    if args.selftest:
        print(json.dumps(report['selftest'], indent=1))
    for failure in report['failures'][:20]:
        print('FAIL %s %s: %s' % (failure['row'], failure['code'], failure['message']), file=sys.stderr)
    return 1 if report['failures'] or (args.selftest and not report.get('selftest_all_caught')) else 0


if __name__ == '__main__':
    raise SystemExit(main())
