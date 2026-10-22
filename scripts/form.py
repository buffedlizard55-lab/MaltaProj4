"""Opponent-anchored form ratings for teams the Valve standings do not list.

Why this module exists
----------------------
Every published row must carry a pick *and* a win probability, and the Valve
VRS model can only price a fixture when *both* labels resolve in Valve's
official global standings. Low-tier events regularly contain a club that Valve
does not list at all (on 2026-10-22: LOS NINOS, TitanFlow and Staqued), so those
rows used to fall through to a research pick with no percentage.

This module estimates the missing team's strength **in Valve's own points
units** from that team's own published HLTV results, using the opponents it has
actually played as anchors:

* every input is a dated, public HLTV results page for that team
  (``https://www.hltv.org/results?team=<id>``), stored on the snapshot with its
  URL, observation time and SHA-256 receipt;
* the opponent's rating is that opponent's published Valve VRS points, and an
  opponent is used only when its label is unique in the standings file;
* the estimate maximises a penalised Bernoulli likelihood under Valve's own
  expected-win curve (``scripts.vrs.expected``), with a weak normal prior at the
  opponents' weighted mean and recency weighting (90-day half-life);
* the standard error comes from the observed Fisher information, and a 95%
  interval is published with the point estimate, so the row shows a range, not
  a false-precision number.

The resulting probability is then produced by exactly the same Valve formula and
published calibration slope as every other model row. It is an **estimate of a
rating**, never a market price, and the row says so.

Validation: ``holdout`` hides a listed team's Valve points, estimates them from
results alone, and reports the error against the published figure. The build and
the validator replay every stored estimate offline.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from bs4 import BeautifulSoup

from scripts.core import dt, iso, norm, plain_name
from scripts.vrs import G, ROSTER_OVERLAP, SLOPE, expected

BASE = 'https://www.hltv.org'
RESULTS = BASE + '/results?team='
SEARCH = BASE + '/search?query='
MAX_MATCHES = 40          # most recent results read per team
MIN_ANCHORED = 6          # matches against standings-listed opponents
MAX_RESULT_AGE_DAYS = 180
HALF_LIFE_DAYS = 90.0
PRIOR_SD = 250.0          # points
MAX_SE = 180.0            # no line when the standard error is wider than this
REUSE_AFTER_HOURS = 7.5   # a capture this fresh is reused instead of re-read
FLAG = 'Originated line: HLTV-results form estimate in Valve points, not a market price.'

TEAM_LINK_RE = re.compile(r'^/team/(\d+)/([^/?#]+)$')


def parse_results(html):
    """Parse one HLTV results page into dated, source-linked results.

    The page lists each completed match as ``.result-con`` with a millisecond
    epoch in ``data-zonedgrouping-entry-unix``, two ``.team-cell .team`` labels
    and a ``.result-score`` whose ``score-won``/``score-lost`` classes say which
    side won. A row that cannot supply all four facts is skipped, never guessed.
    """
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    for node in soup.select('.result-con'):
        anchor = node.select_one('a.a-reset[href^="/matches/"]')
        stamp = node.get('data-zonedgrouping-entry-unix')
        labels = [t.get_text(' ', strip=True) for t in node.select('.team-cell .team')]
        score = node.select_one('.result-score')
        if anchor is None or not stamp or len(labels) != 2 or score is None:
            continue
        if not all(labels) or norm(labels[0]) == norm(labels[1]):
            continue
        spans = score.find_all('span')
        if len(spans) < 2:
            continue
        classes = [' '.join(s.get('class') or []) for s in spans[:2]]
        won = ['score-won' in classes[0], 'score-won' in classes[1]]
        if won[0] == won[1]:
            continue
        try:
            when = datetime.fromtimestamp(int(stamp) / 1000, timezone.utc)
        except (ValueError, OSError, OverflowError):
            continue
        out.append({
            'start': iso(when),
            'teams': labels,
            'winner': labels[0] if won[0] else labels[1],
            'score': ' '.join(score.get_text(' ', strip=True).split()),
            'url': BASE + anchor['href'],
        })
    return out


def parse_team_search(html):
    """Exact ``/team/<id>/<slug>`` links from an HLTV search response."""
    soup = BeautifulSoup(html, 'html.parser')
    found = {}
    for anchor in soup.select('a[href^="/team/"]'):
        href = anchor.get('href') or ''
        if not TEAM_LINK_RE.match(href):
            continue
        label = ' '.join(anchor.get_text(' ', strip=True).split())
        if label:
            found.setdefault(BASE + href, label)
    return found


def receipt(url, body, observed_at):
    return {'url': url, 'observed_at': observed_at,
            'sha256': hashlib.sha256(body.encode('utf-8', 'replace')).hexdigest()}


def corpus(matches, standings, src, now, validation_sample=2, previous=None):
    """Read the public results page of every team this run needs.

    Two groups are read, both capped:

    * ``unlisted`` - labels genuinely absent from the standings file that an
      open fixture still needs priced (at most eight);
    * ``validation`` - a deterministic sample of *listed* teams (at most four),
      read only so :func:`holdout` can hide their published points and measure
      the estimator's real error on this run. They never change a published row.

    Returns ``{'captured_at':..., 'teams': {label: {...}}}`` and records every
    failure on the entry rather than retrying into a different answer.
    """
    counts = {}
    for row in standings['teams']:
        counts[norm(row['name'])] = counts.get(norm(row['name']), 0) + 1
    listed = {norm(row['name']) for row in standings['teams']}
    # A label is "hard" when Valve either does not list it at all, or lists it
    # more than once and the current lineup is needed to tell the rosters apart.
    # Both cases need the club's own results before a line can exist.
    hard = lambda team: norm(team) not in listed or counts.get(norm(team), 0) > 1
    known = {}
    for m in matches:
        for row in (m.get('hltv_team_pages') or {}).get('teams') or []:
            if row.get('team') and str(row.get('url') or '').startswith(BASE + '/team/'):
                known.setdefault(norm(row['team']), row['url'])
        for row in (m.get('hltv_context') or {}).get('team_links') or []:
            if row.get('team') and str(row.get('url') or '').startswith(BASE + '/team/'):
                known.setdefault(norm(row['team']), row['url'])
        for anchor in (m.get('hltv_context') or {}).get('lineups') or []:
            if anchor.get('team') and str(anchor.get('source') or '').startswith(BASE + '/team/'):
                known.setdefault(norm(anchor['team']), anchor['source'])
    # A team URL recorded by an earlier capture is stable identity, so it is
    # reused even when that capture's results are too old to publish: the run
    # only needs the club's page, not a fresh label search that may be refused.
    for label, entry in ((previous or {}).get('teams') or {}).items():
        url = str(entry.get('team_url') or '')
        if url.startswith(BASE + '/team/') and TEAM_LINK_RE.match(url.split(BASE)[-1]):
            known.setdefault(norm(label), url)
    wanted, sampled = [], []
    for m in matches:
        if m.get('state') != 'open':
            continue
        for team in m['teams']:
            if m.get('probabilities') is not None:
                if not hard(team) and norm(team) not in {norm(x) for x in sampled} and len(sampled) < validation_sample:
                    sampled.append(team)
                continue
            if hard(team) and norm(team) not in {norm(x) for x in wanted}:
                wanted.append(team)
            elif norm(team) not in {norm(x) for x in sampled} and len(sampled) < validation_sample:
                sampled.append(team)
    plan = [(label, 'unlisted') for label in wanted[:6]] + [(label, 'validation') for label in sampled[:validation_sample]]
    # A capture younger than this is reused verbatim: re-reading a host that has
    # just served the same page is what turns a rate limit into a block. It is
    # deliberately below the eight-hour evidence window, so a reused entry can
    # never be published as fresher evidence than it is.
    carried = {}
    for label, entry in ((previous or {}).get('teams') or {}).items():
        try:
            age = (now - dt(entry.get('captured_at') or (previous or {}).get('captured_at'))).total_seconds()
        except (TypeError, ValueError):
            continue
        if entry.get('status') == 'rescued' and entry.get('results') and age < REUSE_AFTER_HOURS * 3600:
            carried[norm(label)] = entry
    # Teams already identified by the fixture's own HLTV page go first: they need
    # no search request at all, and the host is read politely (one request every
    # couple of seconds) so a burst can never turn a useful source into a block.
    plan.sort(key=lambda item: 0 if known.get(norm(item[0])) else 1)
    out = {'captured_at': iso(now), 'teams': {}}
    for index, (label, role) in enumerate(plan):
        if norm(label) in carried and carried[norm(label)].get('role') == role:
            out['teams'][label] = dict(carried[norm(label)], reused=True)
            continue
        if index:
            time.sleep(2.0)
        entry = {'team': label, 'role': role, 'status': 'unresolved', 'results': [], 'captured_at': iso(now)}
        try:
            url = known.get(norm(label))
            if not url:
                raise ValueError('no HLTV team link was recorded on this fixture; a label search is not attempted '
                                 '(the search endpoint answers 403 and blocks the host for the run)')
            entry['team_url'] = url
            entry['team_url_source'] = 'recorded on this fixture by the HLTV research step'
            page, page_receipt = src.get('HLTV team results ' + label, RESULTS + TEAM_LINK_RE.match(url.split(BASE)[-1]).group(1), False)
            entry['results_url'] = page_receipt['url']
            entry['results_receipt'] = page_receipt
            rows = parse_results(page)
            if not rows:
                raise ValueError('HLTV results page returned no parsed completed matches')
            cutoff = now - timedelta(days=MAX_RESULT_AGE_DAYS)
            recent = [r for r in rows if dt(r['start']) >= cutoff][:MAX_MATCHES]
            entry.update(status='rescued' if recent else 'unresolved', results=recent)
            if not recent:
                raise ValueError('no completed HLTV match inside the %d-day window' % MAX_RESULT_AGE_DAYS)
            entry['page_sha256'] = page_receipt['sha256']
        except (ValueError, KeyError, TypeError) as exc:
            entry['problem'] = str(exc)[:300]
        out['teams'][label] = entry
    return out


def _points_index(standings):
    index = {}
    for row in standings['teams']:
        index.setdefault(norm(row['name']), []).append(row)
    return {key: rows[0] for key, rows in index.items() if len(rows) == 1}


def _weight(age_days):
    return 0.5 ** (max(age_days, 0.0) / HALF_LIFE_DAYS)


def anchored(results, team, index, now):
    """Results of ``team`` against uniquely-listed opponents, with anchors."""
    rows = []
    for r in results:
        mine = [i for i, label in enumerate(r['teams']) if norm(label) == norm(team)]
        if len(mine) != 1:
            continue
        other = 1 - mine[0]
        anchor = index.get(norm(r['teams'][other]))
        if anchor is None or not isinstance(anchor.get('points'), int):
            continue
        age = max((now - dt(r['start'])).total_seconds() / 86400.0, 0.0)
        rows.append({'opponent': r['teams'][other], 'opponent_points': anchor['points'],
                     'opponent_standing': anchor['standing'], 'won': norm(r['winner']) == norm(team),
                     'start': r['start'], 'url': r['url'], 'weight': _weight(age)})
    return rows


def _loglik(rating, rows, prior_mean):
    total = 0.0
    for row in rows:
        p = expected(rating, row['opponent_points'])
        p = min(max(p, 1e-9), 1 - 1e-9)
        total += row['weight'] * (math.log(p) if row['won'] else math.log(1 - p))
    total -= 0.5 * ((rating - prior_mean) / PRIOR_SD) ** 2
    return total


def estimate(results, team, index, now, prior_sd=PRIOR_SD):
    """Penalised maximum-likelihood rating in Valve points, with a 95% interval."""
    rows = anchored(results, team, index, now)
    if len(rows) < MIN_ANCHORED:
        return None, ('only %d completed match(es) against opponents who are uniquely listed in the Valve '
                      'standings; at least %d are required' % (len(rows), MIN_ANCHORED))
    total_w = sum(r['weight'] for r in rows)
    prior_mean = sum(r['weight'] * r['opponent_points'] for r in rows) / total_w
    lo, hi = prior_mean - 900, prior_mean + 900
    step = 2.0
    grid = {}
    value = lo
    while value <= hi:
        grid[value] = _loglik(value, rows, prior_mean)
        value += step
    best = max(grid, key=grid.get)
    # Golden-section refinement on the bracketing interval.
    a, b = best - step, best + step
    phi = (math.sqrt(5) - 1) / 2
    c, d = b - phi * (b - a), a + phi * (b - a)
    for _ in range(60):
        if _loglik(c, rows, prior_mean) > _loglik(d, rows, prior_mean):
            b = d
        else:
            a = c
        c, d = b - phi * (b - a), a + phi * (b - a)
    rating = (a + b) / 2
    # Observed Fisher information by central second difference.
    h = 1.0
    f0, fp, fm = _loglik(rating, rows, prior_mean), _loglik(rating + h, rows, prior_mean), _loglik(rating - h, rows, prior_mean)
    second = (fp - 2 * f0 + fm) / (h * h)
    if second >= 0:
        return None, 'the likelihood is not locally concave; no estimate published'
    se = 1.0 / math.sqrt(-second)
    return {'team': team, 'rating': rating, 'se': se,
            'interval': [rating - 1.96 * se, rating + 1.96 * se],
            'matches': len(rows), 'wins': sum(1 for r in rows if r['won']),
            'prior_mean': prior_mean, 'prior_sd': prior_sd,
            'anchors': sorted({r['opponent'] for r in rows}),
            # Every anchored result travels with the row, so the build validator
            # and the independent auditor can replay the optimum and its
            # curvature from the snapshot alone, without the standings file.
            'anchored': [{k: r[k] for k in ('opponent', 'opponent_points', 'won', 'weight', 'start', 'url')}
                         for r in rows],
            'results': rows,
            'anchored': [{k: r[k] for k in ('opponent', 'opponent_points', 'won', 'weight', 'start', 'url')} for r in rows],
            'formula_source': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/model/fit.js',
            'calibration_source': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/modelfit.png'}, None


def line(fixture, standings, meta, corpus_doc, now=None, lineups=None):
    """Price one fixture from a mix of published and form-estimated points."""
    now = now or datetime.now(timezone.utc)
    index = _points_index(standings)
    from scripts.vrs import identify
    parts, notes = [], []
    for team in fixture['teams']:
        lineup = next((v for k, v in (lineups or {}).items() if k and norm(k) == norm(team)), None)
        entry, note = identify(team, standings, lineup)
        if entry is not None:
            parts.append({'team': team, 'points': entry['points'], 'standing': entry['standing'],
                          'name': entry['name'], 'basis': 'valve_standings', 'note': note})
            continue
        form = (corpus_doc or {}).get('teams', {}).get(team) or {}
        if form.get('status') != 'rescued':
            return None, ('%s cannot be resolved in the %s Valve standings (%s) and no verified HLTV results '
                          'corpus exists for it (%s)' % (team, standings['as_of'], note,
                                                         form.get('problem') or 'not captured'))
        est, problem = estimate(form['results'], team, index, now)
        if est is None:
            return None, '%s: %s' % (team, problem)
        if est['se'] > MAX_SE:
            return None, ('%s: form estimate standard error %.0f points is wider than the %d-point ceiling'
                          % (team, est['se'], MAX_SE))
        parts.append({'team': team, 'points': est['rating'], 'standing': None,
                      'name': team, 'basis': 'hltv_results_estimate', 'note': problem or 'form estimate',
                      'form': est, 'results_url': form.get('results_url'), 'team_url': form.get('team_url')})
    if parts[0]['team'] == parts[1]['team']:
        return None, 'Both sides resolved to one team.'
    raw = expected(parts[0]['points'], parts[1]['points'])
    # Propagate each estimated side's 95% interval through the same formula.
    def prob_at(points_a, points_b):
        return 0.5 + SLOPE * (expected(points_a, points_b) - 0.5)
    p = [prob_at(parts[0]['points'], parts[1]['points']),
         1 - prob_at(parts[0]['points'], parts[1]['points'])]
    low, high = None, None
    se = [0.0, 0.0]
    for i, part in enumerate(parts):
        if part['basis'] == 'hltv_results_estimate':
            se[i] = part['form']['se']
    if any(se):
        width = math.sqrt(se[0] ** 2 + se[1] ** 2)
        low = prob_at(parts[0]['points'] - 1.96 * width, parts[1]['points'] + 1.96 * width)
        high = prob_at(parts[0]['points'] + 1.96 * width, parts[1]['points'] - 1.96 * width)
        low, high = min(low, high), max(low, high)
    quote = {
        'provider': 'CS2 Scout form model',
        'id': 'form-%s-%s' % (fixture['id'], standings['as_of']),
        'url': (parts[0].get('results_url') or parts[1].get('results_url') or ''),
        'api_url': meta['raw_url'], 'observed_at': iso(now), 'updated_at': None,
        'standings_as_of': standings['as_of'], 'standings_file': meta['file'],
        'standings_commit': meta.get('commit'), 'standings_origin': meta['origin'],
        'standings_url': meta['blob_url'],
        'probability_model': 'form_bridge_v1',
        'fixture_teams': list(fixture['teams']),
        'points': [part['points'] for part in parts],
        'bases': [part['basis'] for part in parts],
        'parts': [{'team': part['team'], 'points': part['points'], 'basis': part['basis'],
                   'vrs_name': part['name'], 'vrs_standing': part['standing'],
                   'results_url': part.get('results_url'), 'team_url': part.get('team_url'),
                   'form': ({k: v for k, v in part['form'].items() if k != 'results'}
                            if part.get('form') else None)} for part in parts],
        'raw_expected': [raw, 1 - raw],
        'calibration_slope': SLOPE,
        'formula_source': parts[0].get('form', {}).get('formula_source') or
                          'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/model/fit.js',
        'calibration_source': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/main/modelfit.png',
        'probabilities': p,
        'interval': [low, high],
        'warning': FLAG + ' Estimated side(s): ' + ', '.join(p['team'] for p in parts if p['basis'] == 'hltv_results_estimate') + '.',
    }
    return quote, None


def apply(fixture, standings, meta, corpus_doc, now=None, lineups=None):
    """Price a remaining open fixture from a form estimate. Never overwrites a market."""
    if fixture['probabilities'] is not None or fixture['state'] != 'open' or fixture.get('resolution_blocked'):
        return
    quote, reason = line(fixture, standings, meta, corpus_doc, now, lineups)
    attempt = {'provider': 'CS2 Scout form model', 'url': meta['blob_url'] if meta else BASE}
    if quote is None:
        attempt.update(status='unresolved', reason='No form-model line: ' + reason)
        fixture['attempts'].append(attempt)
        return
    p = quote['probabilities']
    fixture.update(probabilities=p, fair_odds=[1 / x for x in p],
                   pick=None if abs(p[0] - p[1]) < .0001 else fixture['teams'][0 if p[0] > p[1] else 1],
                   method='model_form', evidence=[quote],
                   reason=None)
    fixture['flags'].append(FLAG)
    estimated = [part['team'] for part in quote['parts'] if part['basis'] == 'hltv_results_estimate']
    attempt.update(status='resolved',
                   reason=('Originated line: Valve standings points for both teams' if not estimated else
                           'Originated line: published Valve points for %s, plus an HLTV-results estimate for %s '
                           '(standard error shown on the row).' % (
                               ', '.join(p['team'] for p in quote['parts'] if p['basis'] == 'valve_standings') or 'neither side',
                               ', '.join(estimated))))
    fixture['attempts'].append(attempt)


def holdout(standings, corpus_doc, now, limit=8):
    """Hide listed teams' points, re-estimate from results, and score the error.

    This is the evidence that the estimate is worth publishing: for teams that
    *are* in Valve's file, the same procedure is run without looking at their
    points, and the miss against the published figure is recorded. It is a
    real out-of-sample check of the estimator, not a fit to the published value.
    """
    index = _points_index(standings)
    rows = []
    for label, entry in (corpus_doc or {}).get('teams', {}).items():
        if entry.get('role') != 'validation' or entry.get('status') != 'rescued' or norm(label) not in index:
            continue
        truth = index[norm(label)]
        est, problem = estimate(entry['results'], label, index, now)
        if est is None:
            rows.append({'team': label, 'status': 'no_estimate', 'problem': problem})
            continue
        rows.append({'team': label, 'status': 'ok', 'estimated_points': round(est['rating'], 1),
                     'published_points': truth['points'], 'error': round(est['rating'] - truth['points'], 1),
                     'se': round(est['se'], 1), 'matches': est['matches']})
        if len(rows) >= limit:
            break
    scored = [r for r in rows if r.get('status') == 'ok']
    summary = {'n': len(scored),
               'mae': round(sum(abs(r['error']) for r in scored) / len(scored), 1) if scored else None,
               'max_abs_error': round(max((abs(r['error']) for r in scored), default=0), 1) if scored else None}
    return {'rows': rows, 'summary': summary}
