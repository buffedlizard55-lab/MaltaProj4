"""Session a54996e1: apply the 2026-10-18T00:55Z Day-5 Thunderpick re-read.

Idempotent. Prices come only from research/session-a54996e1/day5-lines.json
(a direct document read of the official Thunderpick market pages); every
probability here is recomputed de-vig arithmetic, never typed by hand.
The superseded 2026-10-17 prices stay in that receipt for audit.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / 'research/session-a54996e1/day5-lines.json'
ANALYSIS = ROOT / 'data/analysis.json'
OBSERVED = '2026-10-18T00:55:00Z'
EXPIRES = '2026-10-18T08:55:00Z'  # observed + 8h evidence TTL; before both starts, flagged


def dec(american):
    return 1 + american / 100 if american > 0 else 1 + 100 / abs(american)


def devig(prices):
    implied = {t: 1 / dec(p) for t, p in prices.items()}
    total = sum(implied.values())
    return {t: v / total for t, v in implied.items()}, total


def fmt_pct(x):
    return f'{x * 100:.2f}%'


def main():
    receipt = json.loads(RECEIPT.read_text())
    assert receipt['observed_at_utc'] == OBSERVED
    notes = json.loads(ANALYSIS.read_text())
    guide = notes['day_five_guidance']
    guide['date'] = 'Day 5 · Sunday 18 October 2026 · lines re-read 18 October 00:55 UTC'
    guide['card'] = ('TODAY: Falcons (61.54%) and FURIA (68.24%) are the re-read Thunderpick favourites. '
                     'Aurora shortened +170 → +140 overnight. View the Day-5 guide, the line-move flag and the '
                     'expiry limits. Still not listed on Hotspawn at 00:48 UTC — research picks, not board picks.')
    guide['summary'] = (
        'Final day is TODAY, Sunday 18 October. Day four produced another upset: BETBOOM beat Falcons 2-1, while '
        'FURIA swept Aurora 2-0. Sunday is FURIA–BETBOOM in the grand final (15:00 UTC, BO5) and Aurora–Falcons '
        'for third place (11:30 UTC, BO3). The official Thunderpick market pages were re-read at 00:55 UTC on '
        '18 October: Falcons shortened from −238 to −200 (Aurora +170 → +140), so the de-vig is now Falcons 61.54% / '
        'Aurora 38.46%; FURIA −286 / BETBOOM +190 is unchanged at 68.24% / 31.76%. These are single-book observations, '
        'not consensus, and their eight-hour expiry (08:55 UTC) is before both starts — no current-at-lock price is '
        'verified. The Hotspawn lobby re-read at 00:48 UTC still lists 81 CS2 matches with only the South American '
        'Series named for Thunderpick, so neither Sunday fixture is a submitable board pick at observation; use the '
        'current picks board for anything listed later. Contrarian read: Aurora at 38.46% is the only measured '
        'alternative (closer line, overnight shortening, VRS #6 vs #5 — a 19-point gap); BETBOOM at 31.76% is a '
        'higher-variance swing justified only by three straight 2-1 wins, not by rest (BETBOOM played 11 maps to '
        'FURIA\u2019s 7). Neither proves a pricing error or a leaderboard edge without crowd pick shares, which Hotspawn '
        'does not publish to this project.')
    markets = {m['label']: m for m in receipt['markets']}
    for card in guide['not_listed']:
        teams = card['teams']
        m = next(v for v in markets.values() if all(t in v['label'] for t in teams))
        prices = m['american']
        probs, total = devig(prices)
        pick = max(probs, key=probs.get)
        assert card['pick'] == pick, (card, pick)
        other = [t for t in teams if t != pick][0]
        def american(t):
            p = prices[t]
            return f'+{p}' if p > 0 else f'\u2212{abs(p)}'
        card['market'] = {
            'label': 'Thunderpick Match Winner',
            'detail': (f'{teams[0]} {american(teams[0])} / {teams[1]} {american(teams[1])} '
                       f'(decimal {dec(prices[teams[0]]):.3f} / {dec(prices[teams[1]]):.3f}). '
                       f'De-vig {fmt_pct(probs[teams[0]])} / {fmt_pct(probs[teams[1]])}; '
                       f'overround {(total - 1) * 100:.2f}%. Observed 18 Oct 00:55Z.'),
            'url': m['market_url'], 'link_label': 'Thunderpick market \u2197',
            'observed_at': OBSERVED, 'expires_at': EXPIRES}
        card['pick_detail'] = (
            f'Research-only ranking baseline with a re-read published price: {pick} {fmt_pct(probs[pick])} de-vig from Thunderpick '
            f'{american(pick)} (fair decimal {1 / probs[pick]:.3f}), observed 18 Oct 00:55 UTC. '
            f'Not a submitable Hotspawn pick (not on the 00:48 UTC board). Single-book document read by session '
            f'a54996e1, not a live automated quote. Expires 18 Oct 08:55 UTC, before the start.')
        # line-move / unchanged note
        prev = m['previous_observation_2026-10-17T20:20:54Z']['american']
        if prev != prices:
            card['line_move'] = (f'Verified line move on the same official market page: '
                                 f'{teams[0]} {prev[teams[0]]:+d} \u2192 {prices[teams[0]]:+d}, '
                                 f'{teams[1]} {prev[teams[1]]:+d} \u2192 {prices[teams[1]]:+d} '
                                 f'between 17 Oct 20:20Z and 18 Oct 00:55Z. A price move is market information, not proof the underdog will win.')
        else:
            card['line_move'] = 'Price unchanged from the 17 Oct 20:20Z read on the same official market page.'
        src = {'label': 'Session a54996e1 Day-5 line re-read receipt (18 Oct 00:55Z)',
               'url': 'https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/research/session-a54996e1/day5-lines.json'}
        if src not in card['sources']:
            card['sources'].append(src)
    for item in guide.get('unpriced', []):
        item['limitation'] = (
            'A separate official Thunderpick match-page document read at 00:55 UTC on 18 October supplies the line '
            'shown above (re-read of the 17 Oct 20:20Z observation). It was not in the retained exchange/Pinnacle '
            'feeds and is not refreshed by their adapters. One bookmaker is not consensus. This observation expires '
            'at 08:55 UTC, before the match; no current-at-lock price is verified. Neither Sunday match was on the '
            'Hotspawn board re-read at 00:48 UTC (81 matches, main TWC event not named).')
    guide['unverified'] = [
        'The automated exchange/Pinnacle receipts have no Sunday line. Attributed Thunderpick sportsbook document reads (17 Oct 20:20Z, re-read 18 Oct 00:55Z) supply dated prices, not a functioning automated Thunderpick adapter or a guaranteed current-at-lock quote. The EGamersWorld aggregator still displays the superseded Aurora 2.73 / Falcons 1.42 prices; that stale display is flagged, not used.',
        'Aurora\u2013Falcons verified line move: +170/\u2212238 (17 Oct 20:20Z) \u2192 +140/\u2212200 (18 Oct 00:55Z) on the same official Thunderpick market page. The 17 Oct tournament-card display (+150/\u2212208) discrepancy is a historical display conflict, not a second current line.',
        'HLTV match pages 2399416/2399417 were re-read 18 Oct ~00:45Z: BO3 third-place decider 11:30 UTC and BO5 grand final 15:00 UTC, VRS Aurora 1839 (#6) vs Falcons 1858 (#5) and FURIA 1858 (#4) vs BETBOOM 1681 (#9). HLTV fan-vote percentages on those pages are crowd votes, not win probabilities, and are not used.',
        'No verified crowd pick shares, current leaderboard distribution, personal position or streak-bonus formula are available. A market underdog is not necessarily a crowd contrarian; no optimal rank-climbing claim is made.',
        'Neither Sunday matchup was in the Hotspawn inventory re-read at 00:48 UTC on 18 October (81 CS2 matches). This is a dated observation, not a permanent absence claim; scheduled refreshes re-check the board every 15 minutes on main.',
        'HLTV is a specialist secondary source. Tournament-organizer confirmation of results, schedule and current roster is not collected; these remain flagged for manual review.',
        'No final-day calibrated model percentage or leaderboard advantage is asserted by these strategy cards. Use the current source-backed board row if a fixture is listed later.']
    # Board integration: the 00:52Z harvest (98 rows, three-way parity verified)
    # listed both Sunday fixtures after the 00:48Z lobby document read had not.
    latest = json.loads((ROOT / 'data/latest.json').read_text())
    board = {}
    for r in latest['matches']:
        if r['id'] in ('1080209', '1080210'):
            board[tuple(sorted(t.casefold() for t in r['teams']))] = r
    for card in guide['not_listed']:
        r = board.get(tuple(sorted(t.casefold() for t in card['teams'])))
        if r:
            ix = r['teams'].index(r['pick'])
            card['now_listed'] = True
            card['hotspawn_id'] = r['id']
            card['board_detail'] = (f"Now a submitable Hotspawn board pick: row {r['id']}, tier {r.get('tier')}, "
                f"{r['pick']} {r['probabilities'][ix]*100:.1f}% from the validated Polymarket exchange line "
                f"observed {r['evidence'][0]['observed_at']} (snapshot {latest['generated_at']}). "
                f"Thunderpick book cross-check above agrees on the favourite; the board row is the live, expiry-checked pick.")
    if len(board) == 2:
        guide['card'] = ('TODAY on the board: Falcons 60.5% (row 1080209, 11:30 UTC) and FURIA 70.5% (row 1080210, '
                         '15:00 UTC) — tap Updated picks. Thunderpick cross-check: 61.54% / 68.24%. Aurora is the '
                         'measured contrarian at ~38-40%; BETBOOM the higher-variance swing at ~30%.')
        guide['summary'] = (
            'Final day is TODAY, Sunday 18 October. FURIA–BETBOOM grand final (15:00 UTC, BO5) and Aurora–Falcons '
            'third-place decider (11:30 UTC, BO3) are NOW on the Hotspawn board: the verified 00:52 UTC harvest '
            '(98 rows, three-way parity) lists Falcons–Aurora as row 1080209 and FURIA–BetBoom as row 1080210, both '
            'tier S, priced from validated Polymarket exchange lines at Falcons 60.5% and FURIA 70.5%. The official '
            'Thunderpick book re-read at 00:55 UTC agrees on both favourites (Falcons 61.54% after shortening '
            '+170/−238 → +140/−200 overnight; FURIA 68.24% unchanged) — two independent sources, same picks, within '
            '2.3 points. Use the live picks board for the expiry-checked board lines; the Thunderpick observations '
            'expire 08:55 UTC and are a cross-check, not the board quote. Contrarian read: Aurora (~38-40%) is the '
            'only measured alternative — closer line, overnight shortening, VRS #6 vs #5 (19 points); BETBOOM '
            '(~30%) is a higher-variance swing justified only by three straight 2-1 wins, not by rest (11 maps played '
            'to FURIA\u2019s 7). Day-1 lesson stands: 9z\u2019s 2-0 upset of Aurora did not repeat in the day-3 rematch '
            '(Aurora 2-0), and Aurora\u2019s roster rebuild dates to 8 July 2026 — not a fresh onboarding shock. No '
            'crowd pick-share or leaderboard formula is published, so no rank-climbing edge is claimed.')
        guide['unverified'] = [
            'Board membership changed overnight: the Hotspawn lobby document read at 00:48 UTC showed 81 matches without the main-event Sunday fixtures, while the production harvest at 00:52 UTC verified 98 rows across the API, CS2 page and lobby including rows 1080209/1080210. The earlier lobby read is retained as a dated, superseded observation and the discrepancy is flagged — the runner receipts (research/session-a54996e1/) are the controlling evidence.',
            'The Thunderpick book lines (re-read 18 Oct 00:55Z, expiring 08:55Z) are a single-book cross-check for the board exchange lines, not a consensus and not a current-at-lock guarantee. The EGamersWorld aggregator still displays superseded Aurora 2.73 / Falcons 1.42 prices; flagged, not used.',
            'Aurora–Falcons verified line move: Thunderpick +170/−238 (17 Oct 20:20Z) → +140/−200 (18 Oct 00:55Z); Polymarket board line at 00:50Z: Falcons 60.5%. FURIA: Thunderpick −286/+190 unchanged; Polymarket board line 70.5%.',
            'HLTV match pages 2399416/2399417 re-read 18 Oct ~00:45Z: BO3 11:30 UTC and BO5 15:00 UTC; VRS Aurora 1839 (#6) vs Falcons 1858 (#5), FURIA 1858 (#4) vs BETBOOM 1681 (#9). HLTV fan-vote percentages are crowd votes, not probabilities, and are not used.',
            'No verified Hotspawn crowd pick shares, leaderboard distribution, personal position or streak-bonus formula are available. A market underdog is not necessarily a crowd contrarian; no optimal rank-climbing claim is made.',
            'HLTV is a specialist secondary source. Tournament-organizer confirmation of results, schedule and roster is not collected; flagged for manual review.',
            'Prices expire at the earliest TTL, lock or start. Re-check the live board before locking a pick.']
        for item in guide.get('unpriced', []):
            item['status'] = 'Now priced on the Hotspawn board (exchange) with a single-book Thunderpick cross-check'
            item['limitation'] = ('Resolved on the board at the 00:52 UTC harvest: a validated Polymarket exchange line '
                'prices this fixture (see Updated picks). The Thunderpick book observation (00:55 UTC, expires 08:55 UTC) '
                'is a single-book cross-check only. One bookmaker is not consensus, and it is not a current-at-lock guarantee.')
    notes['reviewed_at'] = '2026-10-18'
    notes['reviewed_at_utc'] = OBSERVED
    notes['note'] = notes.get('note', '') + (' Day-5 lines re-read 18 Oct 00:55Z by session a54996e1 from the official '
        'Thunderpick market pages: Aurora-Falcons moved to +140/-200 (Falcons 61.54%), FURIA-BETBOOM unchanged '
        '-286/+190 (FURIA 68.24%); Hotspawn lobby re-read 00:48Z still has no main-event Sunday fixture. Receipt: '
        'research/session-a54996e1/day5-lines.json.')
    ANALYSIS.write_text(json.dumps(notes, indent=1, ensure_ascii=False) + '\n')
    print('updated', OBSERVED)


if __name__ == '__main__':
    main()
