"""Plain-language coverage accounting for the executive summary.

Why this module exists
---------------------
The board publishes three different kinds of answer for an open match:

* a **win probability** from a two-sided betting line (market tier),
* a **win probability** from our own Valve-standings model (originated tier),
* a **pick with no percentage** (research tier), and
* nothing at all, which must then be blank and flagged.

Before this module the executive summary expressed that mix in prose written by
hand, so the counts in the headline, the stat cards, the notices and the
"unresolved" section could drift apart. Everything here is a pure function of
one published snapshot: counts, the pick's origin, the ordered list of sources
that were tried, and the per-row limitation. No number is estimated, projected
or carried over from an earlier build, and nothing here can turn a blank into a
percentage -- a row without a verified two-sided line stays without one.

The ladder is the publication order implemented by ``scripts.refresh``: an
automated exchange gate, HLTV identity research, Pinnacle, the labelled wide
exchange tier, a researched book listing, our own Valve VRS model line, and
finally a research-only pick. The wording is derived from that code path so a
future change to the order has to be reflected here.
"""
from __future__ import annotations

from scripts.core import GAMMA, PIN

# Every method a priced row can carry, and where the number came from.
ORIGINS = {
    'exchange': ('market', 'Betting-market line', 'Polymarket two-sided order book, de-vigged'),
    'exchange_wide': ('market', 'Betting-market line · wide quote', 'Polymarket quote past the strict spread ceiling, published as low confidence'),
    'bookmaker': ('market', 'Bookmaker line', 'A bookmaker’s own two-way price, de-vigged'),
    'bookmaker_fallback': ('market', 'Bookmaker line · researched listing', 'A dated two-way price read from a bookmaker listing page'),
    'model_vrs': ('model', 'Our own VRS model line', 'Valve’s official standings points through Valve’s own expected-win formula'),
    'model_vrs_mirror': ('model', 'Our VRS model line · HLTV mirror', 'Valve points published by HLTV’s dated ranking, through the same formula; not a market price'),
    'research_rank': ('research', 'Research pick · ranking order', 'HLTV world ranking order for an exact fixture; no percentage'),
    'research_rank_single': ('research', 'Research pick · one team ranked', 'Only one side carries an HLTV world ranking; no percentage'),
    'research_vrs_single': ('research', 'Research pick · one Valve listing', 'Only one side appears in Valve’s official global standings; no percentage'),
    'research_form': ('research', 'Research pick · HLTV recent form', 'More wins over each side’s last completed matches on the fixture’s own HLTV page (head-to-head breaks a tie); no percentage'),
}

# The publication ladder, in the order scripts.refresh applies it. Each step
# names the official source it reads so the summary can link every claim.
LADDER = (
    ('exchange', 'Polymarket exchange line, strict gate',
     'Two-sided, funded and fresh: spread 25 points or less, at least $100 of liquidity, '
     'and an observation no older than eight hours. De-vigged from both outcome prices.',
     'Polymarket Gamma API', GAMMA + '/events'),
    ('hltv', 'HLTV fixture identity, rankings and lineups',
     'Confirms the exact opponent pair and UTC start, the world ranking and the current five. '
     'HLTV’s own betting table exposes no numeric two-way price to this collector, and its '
     'community vote is never used as a probability.',
     'HLTV match pages', 'https://www.hltv.org/matches'),
    ('pinnacle', 'Pinnacle esports moneyline',
     'A sharp bookmaker’s two-way price for the exact fixture, de-vigged with the same formula. '
     'One bookmaker is not a consensus.',
     'Pinnacle guest esports API', PIN + '/sports/12/markets/straight'),
    ('exchange_wide', 'Wide exchange quote, labelled low confidence',
     'Used only when a row would otherwise have no pick at all: still two-sided, funding and '
     'freshness gates unchanged, spread between 25 and 60 points. The real spread is published.',
     'Polymarket Gamma API', GAMMA + '/events'),
    ('book', 'Researched bookmaker listing',
     'A dated two-way price read from a listing page, accepted only when it re-confirms the exact '
     'pair, the exact UTC start and an asymmetric pair bound to both team labels. The identical '
     '1.8 / 1.8 placeholder some listings serve is refused, never published.',
     'EGamersWorld CS2 listing', 'https://egamersworld.com/counterstrike/matches'),
    ('model_vrs', 'Our own VRS model line',
     'Valve’s official Regional Standings points through Valve’s own published expected-win formula '
     'and calibration. Labelled as our model everywhere; never presented as a market price.',
     'Valve counter-strike_regional_standings', 'https://github.com/ValveSoftware/counter-strike_regional_standings'),
    ('model_vrs_mirror', 'Our VRS model from HLTV’s dated Valve ranking',
     'Only when Valve’s monthly file cannot resolve the clubs: the same formula and calibration, '
     'with points from HLTV’s dated Valve-points list, explicit provenance and the same expiry gates. '
     'Not an operator price or a claim that HLTV’s current points occur in the older monthly file.',
     'HLTV dated Valve ranking', 'https://www.hltv.org/valve-ranking/teams'),
    ('research', 'Research pick, no percentage',
     'Ranking-order evidence for an exact fixture — or, when HLTV lists no fixture page, each '
     'club’s world rank on its own exact HLTV team page (an unranked side counts only where '
     'HLTV states the absence in words) — one side listed in Valve’s official standings '
     'while the other side is absent from that file, or — weakest and last — HLTV’s own recent '
     'completed results for both teams on the fixture page (more wins over the same number of '
     'recent matches; HLTV’s lifetime head-to-head series wins break a tie; still level stays '
     'unresolved). A directional pick only — the percentage and the fair odds stay blank.',
     'HLTV rankings and Valve standings', 'https://www.hltv.org/ranking/teams'),
)

# Which ladder step answers for which published method.
METHOD_STEP = {
    'exchange': 'exchange', 'exchange_wide': 'exchange_wide', 'bookmaker': 'pinnacle',
    'bookmaker_fallback': 'book', 'model_vrs': 'model_vrs', 'model_vrs_mirror': 'model_vrs_mirror',
    'research_rank': 'research', 'research_rank_single': 'research',
    'research_vrs_single': 'research', 'research_form': 'research',
}


# The documented fourth answer: a verified two-way line that is *exactly* even.
# ``scripts.core.resolve`` (and the VRS tiers) publish the price, publish the
# fair line, and deliberately publish **no pick**, with this limitation, because
# a directional pick cannot be derived from 0.500 / 0.500 without inventing one.
# The policy is stated on the method page -- "exactly equal verified prices get
# 'no directional edge'" -- and ``scripts.coverage_contract`` already accepts it.
# What did not accept it, until 2026-10-24, was the count arithmetic: the row
# carried a probability (so ``priced`` counted it) but no pick (so ``with_pick``
# did not), and every summary block that derived one from the other published a
# total that could not be reproduced. On the 16:24Z board (83 rows, 22 open,
# 22 priced, 21 picked) that single row froze publication: 4 scheduled publish
# runs failed, and the live board withheld every pick at 16:06Z. One predicate,
# used everywhere, is the fix.
NO_EDGE_MARKER = 'no directional edge'


def is_no_edge(match):
    """True for a documented *no directional edge* row: priced exactly even, no pick.

    Deliberately strict. A row qualifies only when it publishes both sides of a
    normalized two-way line that are equal to the last bit, carries no pick, and
    states the documented limitation. Anything else -- a missing price, a pick,
    an unstated reason -- is *not* no-edge, so a broken row cannot hide behind
    this classification.
    """
    if not isinstance(match, dict):
        return False
    if match.get('pick') or match.get('probabilities') is None:
        return False
    probabilities = match.get('probabilities')
    try:
        even = (len(probabilities) == 2 and
                abs(float(probabilities[0]) - float(probabilities[1])) < 1e-12)
    except (TypeError, ValueError):
        return False
    return even and NO_EDGE_MARKER in str(match.get('reason') or '').lower()


def origin(match):
    """Return ``(kind, label, basis)`` for one row's published pick.

    ``kind`` is ``market``, ``model``, ``research`` or ``none``. An unknown
    method is reported as unknown rather than being folded into a known tier, so
    a new method cannot silently mislabel the summary.
    """
    method = match.get('method')
    if is_no_edge(match):
        return ('no_edge', 'No edge — 50/50 verified line',
                'a verified two-way line priced exactly even, so no directional pick is supportable')
    if match.get('probabilities') is not None:
        return ORIGINS.get(method, ('unknown', 'Unclassified line', 'method not in the published tier list'))
    if match.get('pick'):
        return ORIGINS.get(method, ('research', 'Research pick', 'sourced pick without a percentage'))
    return ('none', 'No pick', 'no source established a line or a ranking edge')


def counts(matches):
    """Count the open board by the kind of answer each row publishes.

    ``matches`` is the snapshot list after ``scripts.build.build`` has applied
    its own expiry rules, so this is exactly what the page displays.
    """
    open_rows = [m for m in matches if m.get('state') == 'open']
    kinds = {'market': 0, 'model': 0, 'research': 0, 'no_edge': 0, 'none': 0, 'unknown': 0}
    for m in open_rows:
        kinds[origin(m)[0]] = kinds.get(origin(m)[0], 0) + 1
    priced = [m for m in open_rows if m.get('probabilities') is not None]
    with_pick = [m for m in open_rows if m.get('pick')]
    no_edge = [m for m in open_rows if is_no_edge(m)]
    without_percentage = [m for m in open_rows if m.get('probabilities') is None]
    # Partition, not three independent tallies: every open row is exactly one of
    # picked / no-edge / unresolved, so a summary can never publish a total that
    # does not equal the board (the 2026-10-24 freeze).
    unresolved = [m for m in open_rows if not m.get('pick') and not is_no_edge(m)]
    return {
        'feed_rows': len(matches),
        'open': len(open_rows),
        'with_pick': len(with_pick),
        'priced': len(priced),
        'market': kinds['market'],
        'model': kinds['model'],
        'research': kinds['research'],
        'no_edge': len(no_edge),
        'none': kinds['none'],
        'unknown': kinds['unknown'],
        'unresolved': len(unresolved),
        'no_pick': len(open_rows) - len(with_pick),
        'without_percentage': len(without_percentage),
        'percent': round(len(priced) / len(open_rows) * 100) if open_rows else 0,
        'research_rows': [m for m in without_percentage if m.get('pick')],
        'blank_rows': [m for m in without_percentage if not m.get('pick')],
        'no_edge_rows': no_edge,
        'unresolved_rows': unresolved,
    }


def partition(c):
    """Assert the three published answers add up, and return them for rendering."""
    total = c['with_pick'] + c['no_edge'] + c['unresolved']
    if total != c['open']:
        raise AssertionError('coverage does not partition the open board: %d picks + %d no-edge + '
                             '%d unresolved != %d open' % (c['with_pick'], c['no_edge'], c['unresolved'], c['open']))
    return c['with_pick'], c['no_edge'], c['unresolved']


def completeness_sentence(c):
    """One sentence a phone can read without scrolling: is the board complete?"""
    if not c['open']:
        return 'No open CS2 fixture at the last check.'
    if c['no_pick'] == 0:
        head = ('The only open match has a pick' if c['open'] == 1 else
                'Every one of the %d open matches has a pick' % c['open'])
    else:
        head = ('%d of %d open matches have a pick' % (c['with_pick'], c['open']))
    no_edge = (' %d carries a verified line priced exactly even, so it publishes both probabilities and '
               'no directional pick.' % c['no_edge']) if c.get('no_edge') else ''
    if c['without_percentage'] == 0:
        return head + ', and every pick carries a win probability.' + no_edge
    missing = ('It carries' if c['open'] == 1 else
               'One of them carries' if c['without_percentage'] == 1 else
               '%d of them carry' % c['without_percentage'])
    return (head + '. ' + missing + ' no win probability because no verified two-way line or '
            'two-team model input exists — the reason for each is listed below.' + no_edge)


def _attempts(match):
    return [a for a in (match.get('attempts') or []) if isinstance(a, dict)]


def step_status(match, step):
    """How the published ladder step was answered for this row.

    Returns one of ``accepted``, ``no usable line``, ``access refused or
    failed``, ``not recorded``. Only attempts the collector actually recorded
    are reported; a missing attempt is never described as a refusal.
    """
    providers = {
        'exchange': ('Polymarket',), 'exchange_wide': ('Polymarket',),
        'hltv': ('HLTV', 'HLTV team pages', 'HLTV lineup receipt'),
        'pinnacle': ('Pinnacle',), 'book': ('Book research', 'Book listing re-observation'),
        'model_vrs': ('Valve VRS model',), 'research': ('HLTV', 'HLTV team pages', 'Valve VRS model', 'Rank research', 'Form research'),
    }.get(step, ())
    statuses = [str(a.get('status') or '') for a in _attempts(match) if a.get('provider') in providers]
    if not statuses:
        return 'not recorded'
    if 'resolved' in statuses:
        return 'accepted'
    if 'error' in statuses:
        return 'access refused or failed'
    return 'no usable line'


def limitation(match):
    """The reason this row carries no percentage, in the row's own words.

    The snapshot stores the reason the collector recorded. When it is missing the
    limitation says so instead of implying that a line was never looked for.
    """
    reason = (match.get('reason') or '').strip()
    if reason:
        return reason
    return 'No reason was recorded with this row; treat it as unverified.'


def ladder_rows(match=None):
    """The ordered ladder with this row's own status where one is recorded."""
    rows = []
    for key, title, what, source_label, url in LADDER:
        rows.append({'key': key, 'title': title, 'what': what,
                     'source_label': source_label, 'url': url,
                     'status': step_status(match, key) if match is not None else None})
    return rows
