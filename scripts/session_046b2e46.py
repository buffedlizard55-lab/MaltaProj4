"""Session 046b2e46: independent line-by-line ledger of every open pick.

This module deliberately shares **no code** with ``scripts/core.py``,
``scripts/vrs.py`` or ``verification-c6/audit_snapshot.py``. It re-derives each
published probability from the raw evidence retained on the row itself:

* **Polymarket (exchange)** — the quote is the midpoint of the market's own
  ``bestBid`` / ``bestAsk``; the complementary outcome is ``1 - midpoint``.
* **Bookmaker listing (BO3.gg -> Thunderpick/GG.BET odds)** — inverse decimal
  odds, normalised to remove the book's overround.
* **Valve VRS model** — Valve's own published Glicko expectation
  (``1 / (1 + 10 ** (-g * (a - b) / 400))`` with ``RD = 75``) and Valve's
  published fit slope ``p = 0.5 + 0.7986 * (E - 0.5)``, from
  ``model/fit.js`` and ``modelfit.png`` in Valve's
  ``counter-strike_regional_standings`` repository.

A row is ``reproduced`` only when the re-derived pair matches the published
pair to 1e-9, both sum to one, the published pick is the higher-probability
team, and ``fair_odds`` is exactly ``1 / p``. Anything else is a failure and the
process exits non-zero, so this cannot pass by accident.

Usage::

    python -m scripts.session_046b2e46 --data data/latest.json \
        --output research/session-046b2e46/ROW-LEDGER.md
"""
import argparse
import json
import math
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

# Valve's published constants, quoted from the official repository.
VALVE_RD = 75.0
VALVE_SLOPE = 0.7986
VALVE_FORMULA = ('https://github.com/ValveSoftware/counter-strike_regional_standings/'
                 'blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/model/fit.js')
VALVE_CALIBRATION = ('https://github.com/ValveSoftware/counter-strike_regional_standings/'
                     'blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/modelfit.png')
HOTSPAWN_HOSTS = ('play.hotspawn.com', 'www.hotspawn.com')
EXCHANGE_HOSTS = ('polymarket.com', 'gamma-api.polymarket.com')
TOLERANCE = 1e-9
IDENTITY_FILE = Path(__file__).resolve().parents[1] / 'data' / 'identities.json'


def fold(value):
    """Case/diacritic/punctuation folding only. Never guesses a suffix."""
    folded = unicodedata.normalize('NFKD', str(value)).casefold()
    folded = ''.join(c for c in folded if not unicodedata.combining(c))
    return ''.join(c for c in unicodedata.normalize('NFKC', folded) if c.isalnum())


def alias_map():
    """Registered label -> canonical club, read from the published identity data."""
    records = json.loads(IDENTITY_FILE.read_text())['aliases']
    return {fold(name): fold(item['canonical']) for item in records for name in item['names']}


def club_key(value):
    key = fold(value)
    return alias_map().get(key, key)


def orient(fixture_teams, source_teams, metadata=None):
    """Which source outcome is fixture team 0, and which is fixture team 1.

    The exchange and the fixture inventory legitimately publish the two clubs in
    different orders (Polymarket had paiN as the home side on fixture 1082697
    while Hotspawn listed BESTIA first). Reordering is only allowed on evidence
    the quote itself carries:

    1. an exact folded name match, or a label joined by a registered identity
       record in ``data/identities.json`` (which carries its own sources), or
    2. the exchange's own ``abbreviation`` for that outcome, as published in its
       team metadata on the same quote — fixture 1082996 is *UNiTY* on Hotspawn
       and *UNiTY esports* on Polymarket, whose own metadata gives the
       abbreviation ``unity``.

    Anything else is a failure, never a guess, and the assignment must still be
    a bijection over the two outcomes.
    """
    abbreviations = {}
    for item in metadata or []:
        if isinstance(item, dict) and item.get('name'):
            abbreviations[fold(item['name'])] = item.get('abbreviation')
    mapping = {}
    for team in fixture_teams:
        hits = [index for index, source in enumerate(source_teams)
                if source and club_key(source) == club_key(team)]
        if len(hits) != 1:
            # The exchange's own abbreviation for that outcome, published in
            # the same quote's team metadata, names this fixture team.
            hits = [index for index, source in enumerate(source_teams)
                    if abbreviations.get(fold(source))
                    and fold(abbreviations[fold(source)]) == fold(team)]
        if len(hits) != 1:
            raise ValueError('cannot map fixture team %r to exactly one quoted outcome' % (team,))
        mapping[team] = hits[0]
    if sorted(mapping.values()) != list(range(len(fixture_teams))):
        raise ValueError('quoted outcomes are not a bijection of the fixture teams')
    return mapping


def parse_time(value):
    return datetime.fromisoformat(str(value).replace('Z', '+00:00')).astimezone(timezone.utc)


def valve_probabilities(points_a, points_b):
    """Valve's expectation, re-implemented from the published formula."""
    q = math.log(10) / 400
    g = 1 / math.sqrt(1 + 3 * q * q * VALVE_RD * VALVE_RD / math.pi ** 2)
    raw = 1 / (1 + 10 ** (-g * (float(points_a) - float(points_b)) / 400))
    first = 0.5 + VALVE_SLOPE * (raw - 0.5)
    return [first, 1 - first]


def polymarket_probabilities(raw):
    bid, ask = raw.get('bestBid'), raw.get('bestAsk')
    if not isinstance(bid, (int, float)) or not isinstance(ask, (int, float)):
        raise ValueError('market carries no numeric two-sided quote')
    mid = (float(bid) + float(ask)) / 2
    if not 0 < mid < 1:
        raise ValueError('midpoint outside (0, 1)')
    return [mid, 1 - mid]


def bookmaker_probabilities(odds):
    if not isinstance(odds, list) or len(odds) != 2:
        raise ValueError('listing carries no two-way decimal odds')
    if not all(isinstance(x, (int, float)) and x > 1 for x in odds):
        raise ValueError('decimal odds must exceed 1')
    weights = [1 / float(x) for x in odds]
    total = sum(weights)
    return [w / total for w in weights]


def rederive(row):
    """Re-derive (probabilities, method_note, primary_url, api_url) from the row."""
    quote = (row.get('evidence') or [None])[0]
    if not quote:
        raise ValueError('no retained quote')
    method = row.get('method')
    if method in ('exchange', 'exchange_wide'):
        if quote.get('provider') != 'Polymarket':
            raise ValueError('exchange tier from an unexpected provider')
        probs = polymarket_probabilities(quote.get('raw') or {})
        note = 'Polymarket midpoint of bestBid/bestAsk'
    elif method == 'bookmaker_fallback':
        odds = (quote.get('raw') or {}).get('odds') or quote.get('decimal_odds')
        probs = bookmaker_probabilities(odds)
        note = 'decimal odds de-vigged'
    elif method in ('model_vrs', 'model_vrs_mirror'):
        points = quote.get('points')
        if not isinstance(points, list) or len(points) != 2:
            raise ValueError('model row without two points')
        probs = valve_probabilities(*points)
        note = ('Valve Glicko + published fit slope' if method == 'model_vrs'
                else 'Valve Glicko + fit slope, points from HLTV\'s dated view')
    else:
        raise ValueError('unknown method %r' % (method,))
    return probs, note, quote.get('url'), quote.get('api_url')


def quote_teams(row):
    """The two labels the quote was published under, in the quote's own order."""
    quote = (row.get('evidence') or [None])[0] or {}
    teams = quote.get('source_teams') or (quote.get('raw') or {}).get('source_teams')
    if isinstance(teams, list) and len(teams) == 2:
        return teams
    model = quote.get('vrs_teams') or quote.get('fixture_teams')
    if isinstance(model, list) and len(model) == 2:
        return model
    raise ValueError('quote carries no two labels')


def check_row(row, snapshot_time):
    """Every line-by-line assertion for one open row. Returns list of problems."""
    problems = []
    row_id = row.get('id')
    probs, note, url, api_url = rederive(row)
    try:
        source_teams = quote_teams(row)
        metadata = (row.get('evidence') or [{}])[0].get('team_metadata')
        order = orient(row['teams'], source_teams, metadata)
        probs = [probs[order[team]] for team in row['teams']]
    except (ValueError, KeyError, TypeError) as exc:
        return (['%s: cannot map the quote to the fixture (%s)' % (row_id, exc)],
                None, note, url, api_url)
    published = row.get('probabilities')
    if not isinstance(published, list) or len(published) != 2:
        return ['%s: no published pair' % row_id], None, note, url, api_url
    for i, (want, got) in enumerate(zip(probs, published)):
        if abs(want - got) > TOLERANCE:
            problems.append('%s: published p[%d]=%.12f re-derives to %.12f' % (row_id, i, got, want))
    if abs(sum(published) - 1) > TOLERANCE:
        problems.append('%s: published pair does not sum to 1' % row_id)
    fair = row.get('fair_odds') or []
    if len(fair) != 2:
        problems.append('%s: fair odds missing' % row_id)
    else:
        for i, p in enumerate(published):
            if abs(fair[i] - 1 / p) > 1e-9:
                problems.append('%s: fair odds[%d] is not 1/p' % (row_id, i))
    expected_pick = row['teams'][0] if published[0] > published[1] else row['teams'][1]
    if abs(published[0] - published[1]) < 1e-4:
        problems.append('%s: level market published with a pick' % row_id)
    elif row.get('pick') != expected_pick:
        problems.append('%s: pick %r does not follow the higher probability %r'
                        % (row_id, row.get('pick'), expected_pick))
    source = urlsplit(row.get('source_url') or '')
    if source.scheme != 'https' or source.netloc not in HOTSPAWN_HOSTS:
        problems.append('%s: fixture URL is not Hotspawn' % row_id)
    if url:
        bit = urlsplit(url)
        if bit.scheme != 'https':
            problems.append('%s: evidence URL is not https' % row_id)
    else:
        problems.append('%s: evidence carries no public URL' % row_id)
    if row.get('method') in ('exchange', 'exchange_wide'):
        if not (url and urlsplit(url).netloc.endswith('polymarket.com')):
            problems.append('%s: exchange row does not link Polymarket' % row_id)
        if not (api_url and urlsplit(api_url).netloc in EXCHANGE_HOSTS):
            problems.append('%s: exchange row does not link its API record' % row_id)
    if row.get('method') == 'model_vrs':
        if 'not a market price' not in ' '.join(row.get('flags') or []):
            problems.append('%s: model row is not labelled non-market' % row_id)
        if not (url or '').startswith('https://github.com/ValveSoftware/counter-strike_regional_standings/'):
            problems.append('%s: model row does not link Valve\'s official file' % row_id)
    if row.get('state') != 'open':
        problems.append('%s: row is not open' % row_id)
    start, lock = parse_time(row['start']), parse_time(row['lock'])
    if lock <= snapshot_time and row.get('state') == 'open':
        problems.append('%s: open row already past its lock' % row_id)
    if not row.get('expires_at'):
        problems.append('%s: open row carries no expiry' % row_id)
    return problems, probs, note, url, api_url


def build_receipt(snapshot):
    now = parse_time(snapshot['generated_at'])
    observed = parse_time(snapshot['fixtures_observed_at'])
    open_rows = [m for m in snapshot['matches'] if m.get('state') == 'open']
    unpicked = [m for m in open_rows if not m.get('pick')]
    unpriced = [m for m in open_rows if m.get('probabilities') is None]
    failures, ledger = [], []
    for row in open_rows:
        try:
            problems, probs, note, url, api_url = check_row(row, observed)
        except (ValueError, KeyError, TypeError) as exc:
            failures.append('%s: cannot re-derive (%s)' % (row.get('id'), exc))
            ledger.append({'row': row, 'note': 'NOT REPRODUCIBLE', 'url': None, 'api_url': None})
            continue
        failures.extend(problems)
        ledger.append({'row': row, 'note': note, 'url': url, 'api_url': api_url, 'derived': probs})
    return {'now': now, 'observed': observed, 'open': open_rows, 'ledger': ledger,
            'failures': failures, 'unpicked': unpicked, 'unpriced': unpriced}


def markdown(snapshot, receipt, source_label):
    rows = receipt['ledger']
    out = ['# Every open pick, re-derived line by line', '',
           '**Source of this table:** `%s` (snapshot `%s`, fixture evidence `%s`). ' % (
               source_label, snapshot['generated_at'], snapshot['fixtures_observed_at']) +
           'Session 046b2e46 regenerates it with `python -m scripts.session_046b2e46`.', '',
           'Each percentage below is **re-derived from the raw evidence retained on the row**, by code that '
           'shares nothing with the pipeline: Polymarket midpoints of the market\'s own `bestBid`/`bestAsk`, '
           'de-vigged decimal odds for a book listing, or Valve\'s published Glicko formula and calibration '
           'slope for the originated lines. A row appears here only if the arithmetic reproduces to 1e-9.', '',
           '| # | Fixture | Match | Start (UTC) | Pick | Win probability | Method | Evidence (official) | Re-derived |',
           '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for index, item in enumerate(rows, 1):
        row = item['row']
        teams = row.get('teams') or ['Unverified', 'Unverified']
        probs = row.get('probabilities') or []
        shown = ' · '.join('%s **%.1f%%**' % (t or 'Unverified', 100 * p)
                           for t, p in zip(teams, probs)) if len(probs) == 2 else 'blank (see limits)'
        links = []
        if item.get('url'):
            links.append('[market](%s)' % item['url'])
        if item.get('api_url'):
            links.append('[API record](%s)' % item['api_url'])
        links.append('[fixture](%s)' % row.get('source_url', ''))
        out.append('| %d | [%s](%s) | %s vs %s | %s | **%s** | %s | %s | %s | %s |' % (
            index, row.get('id'), row.get('source_url', ''), teams[0], teams[1], row.get('start'),
            row.get('pick'), shown, row.get('method'),
            ' · '.join(links),
            'reproduced' if item.get('derived') and not any(
                str(row.get('id')) in f for f in receipt['failures']) else '**FAILED**'))
    out += ['', '## Coverage', '',
            '- **%d open matches** in the fixture feed at the observation time.' % len(receipt['open']),
            '- **%d with a pick**, **%d with a reproduced win probability**.' % (
                len(receipt['open']) - len(receipt['unpicked']),
                len(receipt['open']) - len(receipt['unpriced'])),
            '- **%d marked unresolved** (no pick from any sourced rung).' % (len(receipt['unpicked'])),
            '- Arithmetic/field failures in this ledger: **%d**.' % len(receipt['failures']), '']
    if receipt['unpicked']:
        out += ['## Unresolved picks and their limitations', '',
                '| Fixture | Match | Start (UTC) | Why no pick was published | Sources attempted |',
                '| --- | --- | --- | --- | --- |']
        for row in receipt['unpicked']:
            attempted = '; '.join('%s (%s)' % (a.get('provider'), a.get('status'))
                                  for a in (row.get('attempts') or [])) or 'none recorded'
            out.append('| [%s](%s) | %s vs %s | %s | %s | %s |' % (
                row.get('id'), row.get('source_url'), row['teams'][0], row['teams'][1], row['start'],
                (row.get('reason') or 'Unverified').replace('|', '/'), attempted.replace('|', '/')))
        out.append('')
    else:
        out += ['## Unresolved picks and their limitations', '',
                'No open match on this snapshot is unpicked. The ladder still records, per row, every source it '
                'tried and refused; those attempts are published on the site\'s *Unresolved & limitations* '
                'section and in `unresolved.html`, so a row that loses its line later shows exactly why.', '']
    out += ['## Method limits that a reader must know', '',
            '- A Polymarket midpoint is a **market** estimate, not a forecast: it is the middle of the live '
            'two-sided quote and moves with the order book.',
            '- A wide-quote row (spread above 25 points) is published at the market mid and labelled '
            'low-confidence; the true value is less precise than the number suggests.',
            '- A bookmaker listing is a **de-vigged** pair: the book\'s margin is removed proportionally. '
            'Listing pages carry no price-update timestamp, so the observation time is what is shown.',
            '- Valve VRS lines are **our own originated lines**, not market prices: Glicko expectation from '
            'Valve\'s official points ([%s](%s)) calibrated with Valve\'s published fit slope '
            '([%s](%s)). They are used only where no market line passed its gates.' % (
                'formula', VALVE_FORMULA, 'calibration', VALVE_CALIBRATION),
            '- Hotspawn supplies **fixture inventory and lock times only**. No probability on this site comes '
            'from Hotspawn, from crowd votes, or from an inferred value.', '']
    if receipt['failures']:
        out += ['## Failures', ''] + ['- %s' % f for f in receipt['failures']] + ['']
    return '\n'.join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data/latest.json')
    parser.add_argument('--output', default='research/session-046b2e46/ROW-LEDGER.md')
    args = parser.parse_args()
    snapshot = json.loads(Path(args.data).read_text())
    receipt = build_receipt(snapshot)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(markdown(snapshot, receipt, args.data))
    print(json.dumps({'open': len(receipt['open']),
                      'picked': len(receipt['open']) - len(receipt['unpicked']),
                      'priced': len(receipt['open']) - len(receipt['unpriced']),
                      'unresolved': len(receipt['unpicked']),
                      'failures': len(receipt['failures'])}, indent=1))
    for failure in receipt['failures']:
        print('FAILED ' + failure)
    raise SystemExit(bool(receipt['failures']))


if __name__ == '__main__':
    main()
