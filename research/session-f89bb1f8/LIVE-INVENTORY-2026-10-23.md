# Live Hotspawn CS2 inventory — three official views, 2026-10-23

Read during this session (tools: the sandbox cannot open TLS to any external host, so the
official pages were read with the browser-side fetcher; every figure below is copied from the
response, not inferred).

| View | URL | CS2 entries reported | What it is |
| --- | --- | --- | --- |
| Fixtures API (`status=scheduled`) | https://phpstack-1372681-6459848.cloudwaysapps.com/api/v1/fixtures?sport_alias=cs2&status=scheduled&tenantId=1 | 92 (the committed snapshot's own `coverage_counts.api`; SHA-256 `1d98b7ae…` in `data/latest.json`) | scheduled pick'em fixtures only |
| CS2 Pick'ems page | https://play.hotspawn.com/cs2-pickems | "Tournament All tournaments (92)", "All tiers (92)" | the CS2 pick'em lobby |
| General lobby | https://play.hotspawn.com/lobby | "Tier All tiers (94)", "All tiers (94)", "203 matches this week" | both games; CS2 filter reported 94 |

## The two views disagree by two entries (Hotspawn-side, not ours)

Tournament counts copied from each page at 2026-10-23 ~09:45Z:

* `play.hotspawn.com/lobby` lists **ESL Challenger League Season 52: Europe - Cup #9 (1)** and
  **Circuit X Curitiba #4 (2)** and **VOID Autumn Cup 2026 (1)**.
* `play.hotspawn.com/cs2-pickems` lists **Circuit X Curitiba #4 (1)** and **VOID Autumn Cup 2026 (1)**
  and does **not** list the ESL Challenger League entry.

Totals: 94 (general lobby) vs 92 (CS2 page) vs 92 (API). The committed board carries the ESL
Challenger row (`1082980 LPH vs WBT Academy`, 13:00Z) and two `Circuit X Curitiba #4` rows
(`1082693`, `1083025`) and no `VOID Autumn Cup 2026` row — i.e. it follows the API for every fixture that is still
scheduled, and it carries the one scheduled fixture the CS2 page omits (the ESL Challenger row).

## VOID Autumn Cup 2026: in play, not pickable

The one CS2 entry the board does not carry is the remaining `VOID Autumn Cup 2026` fixture.
Independent official sources place the tournament's 23 Oct matches before this snapshot:

* HLTV event page https://www.hltv.org/events/9435/macemedia-void-autumn-cup-2026 — "Oct 20th -
  Oct 24th 2026", Shanghai; the matches page https://www.hltv.org/matches lists the 23 Oct
  playoff matches at 00:00/02:00/08:20.
* Hotspawn's own CS2 matches page https://www.hotspawn.com/counter-strike/matches showed the
  VOID Autumn Cup fixture **LIVE** (Vitalem Aerem 0-0 Rare Atom) when read at ~09:45Z.

A fixture whose lock has passed is not a missing pick: `scripts.core.normalize_fixtures` marks it
`not_open`, and no probability is invented for it. It is absent from the scheduled feed our
collector reads, so it does not appear on the board at all.

## Bracket placeholders that can never be picked

`https://www.hotspawn.com/counter-strike/matches` (read 2026-10-23 ~09:45Z) also lists, under
"Live and Upcoming":

| Time (UTC) | Competition | Teams shown |
| --- | --- | --- |
| 17:00 23 Oct | ESL Challenger League Season 52: Europe - Cup #9 | TBD vs TBD |
| 17:00 23 Oct | ESL Challenger League Season 52: Europe - Cup #9 | TBD vs TBD |
| 17:00 23 Oct | CIS LAN Championship #9 | TBD vs TBD |

These are bracket slots whose teams are not announced. They are not pick'em entries (they are
absent from both the API and the CS2 pick'em lobby), and `normalize_fixtures` refuses to issue a
pick when a team name is `TBD`/`TBA`/`unknown` ("Team identity unverified or not yet announced").
Covering them is therefore impossible by definition until the bracket resolves — this is the
limitation class the unresolved section documents.
