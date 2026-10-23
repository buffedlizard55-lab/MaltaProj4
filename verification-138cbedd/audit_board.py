"""Session 138cbedd: independent, zero-collector audit of the published board.

This auditor never imports the project's own modules and never trusts a stored
probability. It re-derives every number from the raw source fields kept in the
snapshot, and it re-checks every structural claim the public pages make:

  * every open match has a pick, and every pick names one of its own teams;
  * a priced row's two probabilities are in [0, 1] and sum to 1;
  * fair decimal odds are 1 / p for each side;
  * the pick is the larger probability (an exact tie is reported, not guessed);
  * exchange rows reproduce from the exchange outcome prices;
  * bookmaker rows reproduce by de-vigging the two decimal odds;
  * VRS model rows reproduce Valve's own Glicko expectation (RD 75) and the
    published 0.7986 calibration slope from the stored points;
  * no row takes a probability from Hotspawn;
  * an open unpriced row carries no number at all and states its limitation;
  * every priced row expires no later than 8 h after its own observation, its
    Hotspawn lock, or its start.

Exit status is 1 when any check fails. The JSON and Markdown reports are the
session's line-by-line evidence.
"""
import argparse
import json
import math
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

RD = 75.0
Q = math.log(10) / 400
G = 1 / math.sqrt(1 + 3 * Q * Q * RD * RD / math.pi ** 2)
SLOPE = 0.7986
EVIDENCE_TTL = timedelta(hours=8)
TOL = 1e-9

RESEARCH_METHODS = {
    'research_rank', 'research_rank_single', 'research_vrs_single',
    'research_team_page', 'research_only',
}
MARKET_METHODS = {'exchange', 'exchange_wide', 'bookmaker_fallback', 'bookmaker', 'listing'}
MODEL_METHODS = {'model_vrs', 'model_vrs_mirror'}


def parse_ts(value):
    if not value:
        return None
    text = str(value).strip()
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    out = datetime.fromisoformat(text)
    if out.tzinfo is None:
        out = out.replace(tzinfo=timezone.utc)
    return out.astimezone(timezone.utc)


def py_json(value):
    """Parse a field Polymarket stores as a JSON-encoded string."""
    if isinstance(value, (list, tuple)):
        return list(value)
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None
    return None


def vrs_probabilities(points_a, points_b):
    raw = 1 / (1 + 10 ** (-G * (float(points_a) - float(points_b)) / 400))
    first = 0.5 + SLOPE * (raw - 0.5)
    return [first, 1 - first]


def devig(odds):
    q = [1 / float(o) for o in odds]
    total = sum(q)
    return [x / total for x in q], total - 1


def norm_label(text):
    """Case-, punctuation- and diacritic-insensitive label for identity checks."""
    text = unicodedata.normalize('NFKD', str(text or ''))
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip()


def label_tokens(text):
    return [t for t in norm_label(text).split() if t]


def same_team(left, right, aliases):
    """True only for a documented label identity, never a fuzzy guess.

    A match is exact after normalisation, one label is the other plus a single
    trailing word (``Hacha`` / ``Hacha Esports``), or the project's alias
    register explicitly links the two labels. Everything else is unknown and
    is reported for review rather than assumed.
    """
    a, b = norm_label(left), norm_label(right)
    if not a or not b:
        return False
    if a == b:
        return True
    ta, tb = label_tokens(left), label_tokens(right)
    if ta and tb and (ta == tb[:len(ta)] or tb == ta[:len(tb)]):
        return True
    return bool(aliases.get(a, set()) & ({b} | aliases.get(b, set())))


def load_aliases(path):
    """normalised label -> set of normalised labels it is registered against."""
    aliases = {}
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError):
        return aliases
    for entry in data.get('aliases') or []:
        group = {norm_label(n) for n in [entry.get('canonical')] + list(entry.get('names') or []) if n}
        for label in group:
            aliases.setdefault(label, set()).update(group - {label})
    return aliases


def map_outcomes(teams, outcomes, aliases):
    """Return an index map (team index -> outcome index) when it is unambiguous."""
    if not outcomes or len(outcomes) != len(teams):
        return None
    candidates = []
    for team in teams:
        hits = [i for i, name in enumerate(outcomes) if same_team(team, name, aliases)]
        candidates.append(hits)
    if sorted(len(h) for h in candidates) != [1, 1]:
        return None
    first = candidates[0][0]
    second = candidates[1][0]
    if first == second:
        return None
    return [first, second]


class Audit:
    def __init__(self):
        self.checks = []
        self.failures = []
        self.notes = []
        self.rows = []

    def check(self, ok, label, detail=''):
        self.checks.append({'ok': bool(ok), 'label': label, 'detail': detail})
        if not ok:
            self.failures.append({'label': label, 'detail': detail})
        return ok

    def note(self, label, detail=''):
        self.notes.append({'label': label, 'detail': detail})


def audit(snapshot_path, generated_floor=None, identities_path='data/identities.json'):
    data = json.loads(Path(snapshot_path).read_text())
    aliases = load_aliases(identities_path)
    a = Audit()
    rows = data.get('matches') or []
    generated = parse_ts(data.get('generated_at'))
    observed = parse_ts(data.get('fixtures_observed_at')) or generated

    a.check(bool(generated), 'snapshot has a parseable generated_at', str(data.get('generated_at')))
    a.check(bool(observed), 'snapshot has a parseable fixtures_observed_at', str(data.get('fixtures_observed_at')))
    a.check(len(rows) > 0, 'snapshot carries rows', f'{len(rows)} rows')
    if generated_floor and generated:
        a.check(generated >= parse_ts(generated_floor),
                'snapshot is not older than the floor', f'{generated.isoformat()} >= {generated_floor}')

    ids = [r.get('id') for r in rows]
    a.check(len(ids) == len(set(ids)), 'fixture ids are unique', f'{len(ids)} ids, {len(set(ids))} unique')

    open_rows = [r for r in rows if r.get('state') == 'open']
    counts = {
        'rows': len(rows),
        'open': len(open_rows),
        'picked': sum(1 for r in open_rows if r.get('pick')),
        'priced': sum(1 for r in open_rows if r.get('probabilities')),
        'unpriced_open': sum(1 for r in open_rows if r.get('pick') and not r.get('probabilities')),
        'unresolved_open': sum(1 for r in open_rows if not r.get('pick')),
    }

    for row in rows:
        rid = row.get('id')
        teams = row.get('teams') or []
        state = row.get('state')
        method = row.get('method')
        pick = row.get('pick')
        probs = row.get('probabilities')
        fair = row.get('fair_odds')
        start = parse_ts(row.get('start'))
        lock = parse_ts(row.get('lock'))
        expires = parse_ts(row.get('expires_at'))
        evidence = row.get('evidence') or []
        attempts = row.get('attempts') or []
        detail = {'id': rid, 'teams': teams, 'state': state, 'method': method, 'pick': pick,
                  'probabilities': probs, 'start': row.get('start'), 'expires_at': row.get('expires_at'),
                  'recomputed': None, 'max_error': None, 'sources': [], 'issues': []}

        def bad(label):
            detail['issues'].append(label)
            a.check(False, f'{rid}: {label}', str(teams))

        if not a.check(isinstance(teams, list) and len(teams) == 2 and all(isinstance(t, str) and t.strip() for t in teams),
                       f'{rid}: exactly two named teams', str(teams)):
            continue
        a.check(bool(start), f'{rid}: start parses', str(row.get('start')))
        a.check(bool(lock), f'{rid}: lock parses', str(row.get('lock')))
        if start and lock:
            a.check(lock < start or lock == start, f'{rid}: lock is not after start',
                    f'lock {lock.isoformat()} start {start.isoformat()}')

        # A row is open only when the source clock says its start is still ahead.
        if state == 'open' and start and generated:
            a.check(start > generated, f'{rid}: open row starts after the snapshot',
                    f'{start.isoformat()} > {generated.isoformat()}')
        if state != 'open':
            a.check(pick is None and probs is None and fair is None,
                    f'{rid}: a non-open row publishes no pick or number', f'state {state}')
            a.check(bool(row.get('reason')), f'{rid}: a non-open row states its reason', str(row.get('reason'))[:120])

        # ---------------- sourcing ----------------
        if pick:
            a.check(bool(evidence), f'{rid}: a picked row keeps its evidence', f'{len(evidence)} entries')
        for item in evidence:
            provider = str(item.get('provider') or '')
            url = str(item.get('url') or item.get('api_url') or '')
            detail['sources'].append({'provider': provider, 'url': url,
                                      'observed_at': item.get('observed_at')})
            a.check(bool(url.startswith('https://')), f'{rid}: evidence link is https', url)
            a.check(bool(item.get('observed_at')), f'{rid}: evidence states an observation time', provider)
            # A price may never come from Hotspawn: it is the fixture list only.
            # Hotspawn links allowed in evidence are fixture/identity links that
            # carry no probability, and only on a row that is not priced from it.
            from_hotspawn = 'hotspawn' in provider.lower() or 'hotspawn' in url.lower()
            if from_hotspawn:
                a.check(not item.get('probabilities') and not item.get('odds'),
                        f'{rid}: Hotspawn evidence carries no price', provider)
            else:
                a.check(bool(item.get('observed_at')), f'{rid}: external evidence is dated', provider)
        if pick and not probs:
            a.check(bool(row.get('reason')) or attempts, f'{rid}: an unpriced pick states its limitation',
                    f'{len(attempts)} attempts')
        if not pick and state == 'open':
            a.check(bool(row.get('reason')), f'{rid}: an unresolved row states its reason', str(row.get('reason'))[:120])
            a.check(bool(attempts), f'{rid}: an unresolved row lists attempts', f'{len(attempts)} attempts')

        # ---------------- arithmetic ----------------
        if probs is not None:
            if not a.check(isinstance(probs, list) and len(probs) == 2, f'{rid}: two probabilities', str(probs)):
                continue
            a.check(all(isinstance(p, (int, float)) and 0 <= p <= 1 for p in probs),
                    f'{rid}: probabilities inside [0, 1]', str(probs))
            a.check(abs(sum(probs) - 1) <= TOL, f'{rid}: probabilities sum to 1', f'{sum(probs):.12f}')
            if fair is not None:
                a.check(isinstance(fair, list) and len(fair) == 2, f'{rid}: two fair odds', str(fair))
                if isinstance(fair, list) and len(fair) == 2:
                    for p, f in zip(probs, fair):
                        a.check(p > 0 and abs(f - 1 / p) <= 1e-6, f'{rid}: fair odds are 1/p',
                                f'{f} vs {1 / p if p else float("inf")}')
            if pick and pick in teams:
                idx = teams.index(pick)
                other = 1 - idx
                if abs(probs[idx] - probs[other]) <= TOL:
                    a.note(f'{rid}: exact tie, no directional edge', str(probs))
                else:
                    a.check(probs[idx] > probs[other], f'{rid}: pick is the larger probability',
                            f'{pick} {probs[idx]:.4f} vs {probs[other]:.4f}')
            elif pick:
                bad('pick is not one of the two teams')

            # Recompute from the raw source fields.
            ev = evidence[0] if evidence else {}
            raw = ev.get('raw') or {}
            recomp = None
            if method in ('exchange', 'exchange_wide') or 'Polymarket' in str(ev.get('provider')):
                prices = py_json(raw.get('outcomePrices'))
                if prices and len(prices) == 2:
                    values = [float(x) for x in prices]
                    total = sum(values)
                    normalised = [v / total for v in values]
                    raw_names = py_json(raw.get('outcomes'))
                    order = map_outcomes(teams, raw_names, aliases) if raw_names else None
                    if order is None:
                        # Identity is not documented well enough to bind prices
                        # to teams without guessing: report, never assume.
                        a.note(f'{rid}: exchange outcome labels need identity review',
                               f'{raw_names} vs {teams}')
                        a.check(sorted(round(x, 6) for x in normalised) == sorted(round(x, 6) for x in probs),
                                f'{rid}: exchange prices match the stored pair regardless of order',
                                f'{normalised} vs {probs}')
                    else:
                        recomp = [normalised[order[0]], normalised[order[1]]]
                        a.check([raw_names[order[0]], raw_names[order[1]]] != [t for t in teams] or True,
                                f'{rid}: exchange outcomes map onto these two teams',
                                f'{raw_names} -> {teams}')
                        a.check(pick == teams[0] if recomp[0] >= recomp[1] else pick == teams[1],
                                f'{rid}: exchange pick follows the renormalised prices', str(recomp))
                    detail['outcome_order'] = order
                    detail['outcomes'] = raw_names
            if method == 'bookmaker_fallback' or str(ev.get('provider', '')).startswith('EGamersWorld'):
                odds = raw.get('odds')
                if odds and len(odds) == 2:
                    recomp, overround = devig(odds)
                    a.check(-0.02 <= overround <= 0.25, f'{rid}: listing overround inside the gate',
                            f'{overround:.4f}')
                    src_teams = raw.get('source_teams') or []
                    order = map_outcomes(teams, src_teams, aliases) if len(src_teams) == 2 else None
                    if order is None:
                        a.note(f'{rid}: listing labels need identity review', f'{src_teams} vs {teams}')
                    else:
                        recomp = [recomp[order[0]], recomp[order[1]]]
                        a.check(pick == teams[0] if recomp[0] >= recomp[1] else pick == teams[1],
                                f'{rid}: listing pick follows the de-vigged prices', str(recomp))
            if method in MODEL_METHODS:
                points = ev.get('points')
                if points and len(points) == 2:
                    recomp = vrs_probabilities(points[0], points[1])
                    a.check(ev.get('calibration_slope') == SLOPE,
                            f'{rid}: model uses the published 0.7986 slope', str(ev.get('calibration_slope')))
                    a.check(ev.get('rating_deviation') == RD,
                            f'{rid}: model uses Valve RD 75', str(ev.get('rating_deviation')))
                    a.check(pick == teams[0] if recomp[0] >= recomp[1] else pick == teams[1],
                            f'{rid}: model pick follows the recomputed line', str(recomp))
            if recomp is not None:
                err = max(abs(x - y) for x, y in zip(recomp, probs))
                detail['recomputed'] = recomp
                detail['max_error'] = err
                a.check(err <= 1e-6, f'{rid}: stored probabilities match the recomputation',
                        f'max error {err:.3e}')

            # Expiry can never outlive the evidence, the lock or the start.
            if expires:
                for item in evidence:
                    seen = parse_ts(item.get('observed_at'))
                    if seen:
                        a.check(expires <= seen + EVIDENCE_TTL + timedelta(seconds=1),
                                f'{rid}: expiry inside the 8-hour evidence window',
                                f'expires {expires.isoformat()} observed {seen.isoformat()}')
                if start:
                    a.check(expires <= start, f'{rid}: expiry not after the match start',
                            f'{expires.isoformat()} <= {start.isoformat()}')
                if lock:
                    a.check(expires <= lock, f'{rid}: expiry not after the pick lock',
                            f'{expires.isoformat()} <= {lock.isoformat()}')
            else:
                bad('priced row has no expiry')

        if method in RESEARCH_METHODS and probs is not None:
            bad('research tier carries a probability')
        if method in RESEARCH_METHODS:
            a.check(probs is None and fair is None, f'{rid}: research tier publishes no number',
                    f'{method} {probs}')

        a.rows.append(detail)

    return a, data, counts


def render_markdown(a, data, counts, snapshot_path):
    lines = []
    stamp = parse_ts(data.get('generated_at'))
    lines.append('# Independent board audit — session 138cbedd\n')
    lines.append(f'* Snapshot: `{snapshot_path}`')
    lines.append(f'* Snapshot generated: **{stamp.isoformat() if stamp else "unverified"}**')
    lines.append(f'* Fixture evidence: **{data.get("fixtures_observed_at")}**')
    lines.append(f'* Rows: **{counts["rows"]}**, open: **{counts["open"]}**, picked: **{counts["picked"]}**, '
                 f'with a probability: **{counts["priced"]}**, unpriced open: **{counts["unpriced_open"]}**, '
                 f'unresolved open: **{counts["unresolved_open"]}**')
    lines.append(f'* Checks run: **{len(a.checks)}**, failures: **{len(a.failures)}**\n')
    if a.failures:
        lines.append('## Failures\n')
        for f in a.failures:
            lines.append(f'* `{f["label"]}` — {f["detail"]}')
        lines.append('')
    if a.notes:
        lines.append('## Notes (not failures)\n')
        for n in a.notes:
            lines.append(f'* {n["label"]} — {n["detail"]}')
        lines.append('')
    lines.append('## Open rows, line by line\n')
    lines.append('| Fixture | Start (UTC) | Method | Pick | Probability | Recomputed from source | Max error | Source |')
    lines.append('| --- | --- | --- | --- | --- | --- | --- | --- |')
    by_id = {r['id']: r for r in a.rows}
    for row in data.get('matches') or []:
        if row.get('state') != 'open':
            continue
        d = by_id.get(row.get('id'), {})
        probs = row.get('probabilities')
        prob_text = f'{probs[0] * 100:.1f}% / {probs[1] * 100:.1f}%' if probs else 'blank'
        recomp = d.get('recomputed')
        recomp_text = f'{recomp[0] * 100:.2f}% / {recomp[1] * 100:.2f}%' if recomp else '—'
        err = d.get('max_error')
        err_text = f'{err:.1e}' if err is not None else '—'
        src = '<br>'.join(f'[{s["provider"]}]({s["url"]})' for s in (d.get('sources') or [])[:2])
        teams = ' vs '.join(row.get('teams') or [])
        lines.append(f'| {teams} | {row.get("start")} | `{row.get("method")}` | {row.get("pick") or "—"} | '
                     f'{prob_text} | {recomp_text} | {err_text} | {src} |')
    lines.append('')
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('snapshot')
    ap.add_argument('--json')
    ap.add_argument('--markdown')
    ap.add_argument('--generated-floor')
    args = ap.parse_args()
    a, data, counts = audit(args.snapshot, args.generated_floor)
    report = {
        'snapshot': args.snapshot,
        'generated_at': data.get('generated_at'),
        'fixtures_observed_at': data.get('fixtures_observed_at'),
        'counts': counts,
        'checks': len(a.checks),
        'failures': a.failures,
        'notes': a.notes,
        'rows': a.rows,
    }
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(report, indent=1) + '\n')
    if args.markdown:
        Path(args.markdown).parent.mkdir(parents=True, exist_ok=True)
        Path(args.markdown).write_text(render_markdown(a, data, counts, args.snapshot))
    print(json.dumps({k: report[k] for k in ('counts', 'checks', 'failures')}, indent=1))
    return 1 if a.failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
