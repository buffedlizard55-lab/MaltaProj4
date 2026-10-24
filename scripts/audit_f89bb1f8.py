"""Independent coverage audit: does every match still open carry a pick?

This is the check the executive summary promises in one sentence -- "every open
Hotspawn CS2 match has a pick" -- written as code that fails loudly instead of as
prose that can drift. It reads one published snapshot and re-derives the two
answers a reader cares about:

* **Coverage.** Every fixture whose pick lock and start are still in the future
  must be ``state == "open"``, must name one of its two teams as the pick, and
  must either carry two probabilities that sum to 1, or be explicitly labelled a
  research-only pick with no numbers. A future fixture that is silently dropped
  or left blank is a failure, not a limitation.
* **Exclusivity of the unresolved class.** A row may only be unresolved when the
  snapshot records *why*: a reason, at least one attempted provider, and an
  official source URL. An unexplained blank is a failure.

It never invents a pick, never fills a blank, and never treats Hotspawn's crowd
percentages (``participants*_picked_percent``) as a probability. Those values are
deliberately not read anywhere in this module.

Run: ``python -m scripts.audit_f89bb1f8 [--data data/latest.json] [--now ISO]``
Exit code 0 means every rule passed; 1 prints the failures.
"""
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.core import FIXTURES, HOTSPAWN

ROOT = Path(__file__).resolve().parents[1]
LOBBY = 'https://play.hotspawn.com/lobby'
INVENTORY_URLS = {'api': FIXTURES, 'page': HOTSPAWN, 'lobby': LOBBY}

# Methods that publish a probability, and the ones that publish a pick without one.
PRICED = {'exchange', 'exchange_wide', 'bookmaker', 'bookmaker_fallback',
          'model_vrs', 'model_vrs_mirror'}
# Integrated from session 019a253a (50c8bfea): the production recent-form
# fallback is a research-only method too; omitting it would reject a valid fresh
# board as soon as that rung supplied its first pick.
RESEARCH = {'research_rank', 'research_rank_single', 'research_vrs_single', 'research_form'}

# The three official views are required to agree in the snapshot's own counts.
COUNT_KEYS = ('api', 'page', 'lobby')


def moment(value):
    return datetime.fromisoformat(str(value).replace('Z', '+00:00'))


def inventory_problems(snapshot):
    """Validate exact retained/raw parity and a disclosed three-source union.

    ``verified`` retains the original exact-count rule. ``partial`` is acceptable
    only for the narrower case where all three official reads succeeded but their
    ID sets disagree: the per-row source receipts must reproduce each reported
    count, their current union must equal every retained row, and no conflict or
    previous-only row may be hidden inside that union. A missing source is not
    proof that the remaining views are complete.
    """
    matches = snapshot.get('matches') or []
    problems = []
    ids = {str(m.get('id')) for m in matches}
    raw_ids = {str(m.get('id')) for m in snapshot.get('fixture_evidence') or []}
    if ids != raw_ids:
        problems.append('retained fixture IDs differ from raw official fixture evidence')
    counts = snapshot.get('coverage_counts') or {}
    if counts.get('retained') != len(matches):
        problems.append('coverage_counts.retained=%r does not match %d retained rows'
                        % (counts.get('retained'), len(matches)))
    coverage = snapshot.get('coverage')
    if coverage == 'verified':
        for key in COUNT_KEYS:
            if counts.get(key) != len(matches):
                problems.append('coverage_counts.%s=%r does not match %d retained rows'
                                % (key, counts.get(key), len(matches)))
        return problems
    if coverage != 'partial':
        problems.append('inventory coverage is neither verified nor a reviewable sourced union')
        return problems
    issues = snapshot.get('issues') or []
    codes = {i.get('code') for i in issues}
    if 'coverage_difference' not in codes:
        problems.append('partial inventory lacks its coverage_difference disclosure')
    forbidden = {'fixture_conflicts', 'retained_open_rows', 'unexpected_empty', 'retained'}
    if codes & forbidden or snapshot.get('fixture_conflicts'):
        problems.append('partial inventory contains a conflict or previous-only row, not a current sourced union')
    current_union = set()
    for key, url in INVENTORY_URLS.items():
        count = counts.get(key)
        if type(count) is not int or count < 0:
            problems.append('coverage_counts.%s=%r is not a completed official read' % (key, count))
            continue
        sourced = set()
        for match in matches:
            receipts = match.get('fixture_sources') or []
            if any(r.get('url') == url and not r.get('retained_from_previous_snapshot')
                   for r in receipts):
                sourced.add(str(match.get('id')))
        if count != len(sourced):
            problems.append('coverage_counts.%s=%r does not match %d sourced union rows'
                            % (key, count, len(sourced)))
        current_union |= sourced
    if current_union != ids:
        problems.append('current official source union does not cover every retained row')
    return problems


def audit(snapshot, now=None):
    """Return (failures, summary). Pure function of one snapshot."""
    now = now or moment(snapshot['built_at'])
    matches = snapshot['matches']
    failures = []

    future = [m for m in matches
              if m.get('start') and m.get('lock')
              and moment(m['lock']) > now and moment(m['start']) > now]

    priced = research = unresolved = 0
    for match in future:
        ident = match['id']
        if match.get('state') != 'open':
            failures.append('%s %s: future fixture is not open (%s)'
                            % (ident, ' vs '.join(match['teams']), match.get('state')))
        if match.get('resolution_blocked'):
            failures.append('%s: future fixture blocked but still listed as open' % ident)
        pick = match.get('pick')
        if not pick:
            unresolved += 1
            if not match.get('reason'):
                failures.append('%s: unresolved row carries no published reason' % ident)
            if not match.get('attempts'):
                failures.append('%s: unresolved row lists no attempted source' % ident)
            if not any((a.get('url') or '').startswith('https://') for a in match.get('attempts') or []):
                failures.append('%s: unresolved row has no official https source' % ident)
            continue
        if pick not in match['teams']:
            # Report, never raise: a corrupted snapshot must fail the audit, not
            # crash the auditor that is supposed to catch it.
            failures.append('%s: pick %r is not one of the two teams' % (ident, pick))
            continue
        probabilities = match.get('probabilities')
        if probabilities is not None:
            priced += 1
            if match.get('method') not in PRICED:
                failures.append('%s: probabilities without a priced method (%r)' % (ident, match.get('method')))
            if len(probabilities) != 2 or abs(sum(probabilities) - 1) > 1e-6:
                failures.append('%s: probabilities do not sum to 1' % ident)
            if probabilities[max(range(2), key=lambda i: probabilities[i])] != probabilities[match['teams'].index(pick)]:
                failures.append('%s: pick is not the more likely team' % ident)
        else:
            research += 1
            if match.get('method') not in RESEARCH:
                failures.append('%s: research-only pick without a research method (%r)' % (ident, match.get('method')))
            if match.get('fair_odds'):
                failures.append('%s: research-only pick must not publish fair odds' % ident)
            if 'not a market probability' not in (match.get('reason') or ''):
                failures.append('%s: research-only pick is not labelled as non-market' % ident)

    # The stale class must be past its lock or start, never merely dropped.
    for match in matches:
        if match.get('state') == 'open':
            continue
        if match.get('pick') or match.get('probabilities'):
            failures.append('%s: closed/past row still publishes a pick or a probability' % match['id'])

    failures.extend(inventory_problems(snapshot))
    counts = snapshot.get('coverage_counts') or {}

    observed = moment(snapshot['fixtures_observed_at'])
    if not timedelta(0) <= now - observed < timedelta(hours=8):
        failures.append('snapshot is outside its 8-hour evidence window at the audit clock')

    return failures, {
        'audited_at': now.isoformat().replace('+00:00', 'Z'),
        'snapshot_observed_at': snapshot['fixtures_observed_at'],
        'rows': len(matches),
        'future_rows': len(future),
        'future_with_pick': len(future) - unresolved,
        'future_priced': priced,
        'future_research_only': research,
        'future_unresolved': unresolved,
        'counts': {key: counts.get(key) for key in COUNT_KEYS},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default=str(ROOT / 'data/latest.json'))
    parser.add_argument('--now', default=None)
    args = parser.parse_args()
    snapshot = json.loads(Path(args.data).read_text())
    failures, summary = audit(snapshot, moment(args.now) if args.now else None)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if failures:
        print('\nFAILURES')
        for failure in failures:
            print(' - ' + failure)
        raise SystemExit(1)
    print('\nOK: every future fixture carries a sourced pick or a documented limitation.')


if __name__ == '__main__':
    main()
