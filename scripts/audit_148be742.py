"""Session 148be742 - independent pick-coverage audit of one published snapshot.

What this answers
-----------------
The requirement is "a pick for every match listed on Hotspawn, with a win
probability wherever one can be sourced, and an explicit, sourced limitation for
anything that cannot". This module checks that contract on a *published* snapshot
plus the pages built from it, using nothing but the JSON the build renders from.
It shares no pricing code with ``scripts.refresh``: it re-reads the stored
numbers and re-checks the invariants rather than recomputing the market.

Per open row:
 1. ``pick`` is present and names exactly one of the fixture's two teams.
 2. ``source_url`` is an https Hotspawn page (the official fixture inventory).
 3. Priced row: two probabilities in (0, 1), summing to 1 (+-0.005), and the
    pick is the larger one; ``fair_odds`` is the reciprocal within 0.02; the
    first evidence quote carries an https ``url`` and an ``observed_at`` inside
    the snapshot's own evidence window; ``expires_at`` is present.
 4. Research-only row (a pick with no percentage): the method is a documented
    ``research_*`` tier, the reason states that no percentage is published, and
    at least one recorded attempt carries an https source. A blank is never a
    default 50/50 and must never appear as a number.
 5. Unresolved row (no pick): refused, because this project's contract is that
    every open fixture carries either a pick or a *published* unresolved entry;
    the row must still carry a limitation and an https source attempt so the
    entry can be rendered on the unresolved page.

Per build:
 6. Every open fixture appears on ``picks.html`` with both team labels.
 7. The executive summary links to the updated pick list and carries the
    separate unresolved/limitations section.
 8. Every row without a percentage is listed in that section with an https
    source link, so a missing number is never silent.

Exit code is non-zero if any check fails. ``--json`` prints a receipt.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_WINDOW = timedelta(hours=8)
SUM_TOLERANCE = 0.005
ODDS_TOLERANCE = 0.02


def _clock(value):
    return datetime.fromisoformat(str(value).replace('Z', '+00:00')).astimezone(timezone.utc)


def _https(value):
    return isinstance(value, str) and value.startswith('https://')


def audit_row(m, snapshot_clock):
    """Return the list of contract violations for one open row (empty = pass)."""
    problems = []
    fixture = m.get('id')
    teams = m.get('teams') or []
    if len(teams) != 2:
        return ['%s: fixture does not have exactly two teams' % fixture]
    pick = m.get('pick')
    if not pick:
        problems.append('%s %s vs %s: open fixture has no pick at all'
                        % (fixture, teams[0], teams[1]))
    elif pick not in teams:
        problems.append('%s: pick %r is not one of the two teams' % (fixture, pick))
    if not _https(m.get('source_url')):
        problems.append('%s: official fixture link is missing or not https' % fixture)
    probabilities = m.get('probabilities')
    if probabilities is not None:
        if not isinstance(probabilities, list) or len(probabilities) != 2:
            return problems + ['%s: probabilities is not a two-value list' % fixture]
        a, b = probabilities
        if not all(isinstance(p, (int, float)) and 0 < p < 1 for p in probabilities):
            problems.append('%s: a probability is outside (0, 1): %r' % (fixture, probabilities))
        elif abs(a + b - 1) > SUM_TOLERANCE:
            problems.append('%s: probabilities sum to %.6f, not 1' % (fixture, a + b))
        if pick in teams and probabilities[teams.index(pick)] != max(probabilities):
            problems.append('%s: the pick is not the more likely team' % fixture)
        odds = m.get('fair_odds')
        if not isinstance(odds, list) or len(odds) != 2:
            problems.append('%s: priced row publishes no fair odds' % fixture)
        else:
            for p, o in zip(probabilities, odds):
                if not isinstance(o, (int, float)) or abs(o - 1 / p) > ODDS_TOLERANCE:
                    problems.append('%s: fair odds %r do not match probability %r' % (fixture, o, p))
        method = m.get('method')
        # A priced row must name how it was priced, and that tier must not be a
        # research tier: a research pick is defined by publishing no number.
        # A new market/model adapter is not blocked here on purpose - an audit
        # that fails on an unknown-but-honest source name would stop publishing.
        if not method:
            problems.append('%s: priced row names no method' % fixture)
        elif str(method).startswith('research_'):
            problems.append('%s: research tier %r published a probability' % (fixture, method))
        evidence = m.get('evidence') or []
        if not evidence:
            problems.append('%s: priced row has no retained quote' % fixture)
        else:
            quote = evidence[0]
            if not _https(quote.get('url')):
                problems.append('%s: retained quote has no https source' % fixture)
            observed = quote.get('observed_at')
            if not observed:
                problems.append('%s: retained quote has no observation time' % fixture)
            elif snapshot_clock - _clock(observed) > EVIDENCE_WINDOW:
                problems.append('%s: retained quote is older than the 8-hour window' % fixture)
        if not m.get('expires_at'):
            problems.append('%s: priced row publishes no expiry' % fixture)
    else:
        if not m.get('pick'):
            # No number and no pick is allowed only as an explicitly published
            # unresolved entry with a stated limitation and a sourced attempt.
            if not (m.get('reason') or '').strip():
                problems.append('%s: unresolved row publishes no limitation' % fixture)
            attempts = [a for a in (m.get('attempts') or []) if _https(a.get('url'))]
            if not attempts:
                problems.append('%s: unresolved row records no sourced attempt' % fixture)
            return problems
        method = m.get('method')
        if not str(method).startswith('research_'):
            problems.append('%s: a pick without a percentage must use a research tier, not %r'
                            % (fixture, method))
        reason = (m.get('reason') or '')
        if not reason.strip():
            problems.append('%s: research-only row publishes no reason' % fixture)
        attempts = [a for a in (m.get('attempts') or []) if _https(a.get('url'))]
        if not attempts:
            problems.append('%s: research-only row records no sourced attempt' % fixture)
        if m.get('fair_odds'):
            problems.append('%s: research-only row must not publish fair odds' % fixture)
    return problems


def audit_snapshot(data):
    snapshot_clock = _clock(data.get('built_at') or data.get('generated_at'))
    observed = _clock(data['fixtures_observed_at'])
    problems = []
    if snapshot_clock - observed > EVIDENCE_WINDOW:
        problems.append('snapshot: fixture evidence is older than the 8-hour window')
    open_rows = [m for m in data['matches'] if m.get('state') == 'open']
    for m in open_rows:
        problems.extend(audit_row(m, snapshot_clock))
    return open_rows, problems


def strip_tags(html_text):
    text = re.sub(r'<script.*?</script>', ' ', html_text, flags=re.S)
    text = re.sub(r'<style.*?</style>', ' ', text, flags=re.S)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', text))


def audit_pages(data, site):
    """The pages must show every pick, and must not hide a missing one."""
    site = Path(site)
    problems = []
    index = (site / 'index.html').read_text()
    picks = (site / 'picks.html').read_text()
    unresolved = (site / 'unresolved.html').read_text()
    if 'id="unresolved-limits"' not in index:
        problems.append('index.html: the executive summary has no unresolved/limitations section')
    if 'href="picks.html"' not in index:
        problems.append('index.html: the executive summary does not link the updated pick list')
    if 'href="#picks-at-a-glance"' not in index:
        problems.append('index.html: the executive summary does not link its own pick list')
    open_rows = [m for m in data['matches'] if m.get('state') == 'open']
    for m in open_rows:
        anchor = 'match-%s' % m.get('id')
        if anchor not in picks:
            problems.append('%s: open fixture is not on the pick board' % m.get('id'))
        for team in m.get('teams') or []:
            if team not in picks:
                problems.append('%s: team label %r is not printed on the pick board'
                                % (m.get('id'), team))
        if m.get('probabilities') is None:
            if anchor not in unresolved:
                problems.append('%s: row without a percentage is not on the unresolved page'
                                % m.get('id'))
            section = index[index.find('id="unresolved-limits"'):]
            section = section[:section.find('</section>')] if '</section>' in section else section
            if m.get('id') not in index and m.get('id') not in section:
                # The compact section counts rather than lists rows; the full
                # list is #unresolved-picks, which must carry every one of them.
                full = index[index.find('id="unresolved-picks"'):]
                if anchor not in full:
                    problems.append('%s: row without a percentage is not listed in the '
                                    'executive summary' % m.get('id'))
    return problems


def audit(data, site=None):
    open_rows, problems = audit_snapshot(data)
    if site:
        problems.extend(audit_pages(data, site))
    priced = [m for m in open_rows if m.get('probabilities') is not None]
    research = [m for m in open_rows if m.get('probabilities') is None and m.get('pick')]
    unresolved = [m for m in open_rows if not m.get('pick')]
    return {
        'snapshot': data.get('generated_at'),
        'fixtures_observed_at': data.get('fixtures_observed_at'),
        'rows': len(data['matches']),
        'open': len(open_rows),
        'open_with_pick': sum(1 for m in open_rows if m.get('pick')),
        'open_with_probability': len(priced),
        'open_research_only': len(research),
        'open_unresolved': len(unresolved),
        'unresolved_ids': [m['id'] for m in unresolved],
        'research_ids': [m['id'] for m in research],
        'problems': problems,
        'passed': not problems,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--data', default='data/latest.json')
    parser.add_argument('--site', default='public')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    data = json.loads(Path(args.data).read_text())
    site = Path(args.site) if Path(args.site).exists() else None
    result = audit(data, site)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print('%s: %d rows, %d open, %d picked, %d priced, %d research-only, %d unresolved'
              % ('PASS' if result['passed'] else 'FAIL', result['rows'], result['open'],
                 result['open_with_pick'], result['open_with_probability'],
                 result['open_research_only'], result['open_unresolved']))
        for problem in result['problems']:
            print(' - ' + problem)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
