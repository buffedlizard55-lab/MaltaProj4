"""Recompute the Day-5 de-vig probabilities from the verified American prices.

Research only. Reads ``research/session-e0fd5a32/day5-lines.json`` and fails loudly if any
stored derived value disagrees with the arithmetic. It never fetches a source, so a stale price
can never be silently renewed by running it.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RECEIPT = ROOT / 'research' / 'session-e0fd5a32' / 'day5-lines.json'
TOLERANCE = 1e-5


def decimal_from_american(price: int) -> float:
    if price == 0:
        raise ValueError('American price cannot be zero')
    return 1 + (price / 100 if price > 0 else 100 / abs(price))


def implied_from_american(price: int) -> float:
    if price == 0:
        raise ValueError('American price cannot be zero')
    return 100 / (price + 100) if price > 0 else abs(price) / (abs(price) + 100)


def devig(team_a: str, team_b: str, prices: dict[str, int]) -> dict:
    a_raw = implied_from_american(prices[team_a])
    b_raw = implied_from_american(prices[team_b])
    overround = a_raw + b_raw
    if overround <= 1:
        raise ValueError('A two-way book cannot have an overround at or below 1')
    p_a, p_b = a_raw / overround, b_raw / overround
    return {
        'decimal': {team_a: decimal_from_american(prices[team_a]),
                    team_b: decimal_from_american(prices[team_b])},
        'raw_implied': {team_a: a_raw, team_b: b_raw},
        'overround': overround,
        'devig': {team_a: p_a, team_b: p_b},
        'fair_decimal': {team_a: 1 / p_a, team_b: 1 / p_b},
    }


def verify(receipt_path: Path) -> list[dict]:
    data = json.loads(receipt_path.read_text())
    failures, computed = [], []
    for fixture in data['fixtures']:
        a, b = fixture['team_a'], fixture['team_b']
        calc = devig(a, b, fixture['prices_american'])
        stored_fields = {'decimal': 'prices_decimal', 'raw_implied': 'raw_implied',
                         'devig': 'devig', 'fair_decimal': 'fair_decimal'}
        for team in (a, b):
            for field, json_field in stored_fields.items():
                stored = fixture[json_field][team]
                if abs(stored - calc[field][team]) > TOLERANCE:
                    failures.append(f"{fixture['id']} {team} {field}: stored {stored} != {calc[field][team]}")
        if abs(fixture['overround'] - calc['overround']) > TOLERANCE:
            failures.append(f"{fixture['id']} overround: stored {fixture['overround']} != {calc['overround']}")
        pick = max((a, b), key=lambda team: calc['devig'][team])
        if fixture['pick'] != pick:
            failures.append(f"{fixture['id']} pick: stored {fixture['pick']} != {pick}")
        if abs(fixture['pick_probability'] - calc['devig'][pick]) > TOLERANCE:
            failures.append(f"{fixture['id']} pick_probability does not match devig")
        if abs(sum(calc['devig'].values()) - 1) > 1e-12:
            failures.append(f"{fixture['id']} devig does not sum to 1")
        computed.append({'id': fixture['id'], 'label': fixture['label'], 'start_utc': fixture['start_utc'],
                         'best_of': fixture['best_of'], 'pick': pick,
                         'pick_probability': round(calc['devig'][pick] * 100, 2),
                         'teams': {team: {'american': fixture['prices_american'][team],
                                          'devig_pct': round(calc['devig'][team] * 100, 2),
                                          'fair_decimal': round(calc['fair_decimal'][team], 3)}
                                   for team in (a, b)}})
    if failures:
        raise SystemExit('VERIFICATION FAILED:\n' + '\n'.join(failures))
    return computed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    rows = verify(args.receipt)
    for row in rows:
        print(f"{row['label']} ({row['id']}, bo{row['best_of']}, {row['start_utc']}): "
              f"pick {row['pick']} {row['pick_probability']}%")
        for team, values in row['teams'].items():
            print(f"  {team:10s} {values['american']:+5d}  {values['devig_pct']:6.2f}%  fair {values['fair_decimal']}")
    print('All stored derived values reproduce.')


if __name__ == '__main__':
    main()
