"""Name the fixtures the Hotspawn lobby shows but the fixture feed did not return.

Why this module exists
----------------------
Measured on 2026-10-26 (this session). The scheduled publisher captured the
official fixtures API at 2026-10-26T00:07:16Z and published 73 CS2 rows
(`build-info.json`, `built_at 2026-10-26T00:10:50Z`, revision `3b158a37`). The
public lobby at https://play.hotspawn.com/lobby, read at 00:47Z, listed seven
further CS2 fixtures that snapshot does not contain:

    1079201  INOX Division vs Nemesis          NODWIN Clutch Series #13
    1081159  LFO 10 vs ex-6666                 CCT Europe 2026 Series #12
    1079202  FOKUS vs ex-Zero Tenacity         NODWIN Clutch Series #13
    1081160  HAVU vs ILLYRIANS                 CCT Europe 2026 Series #12
    1079203  Metizport vs BRUTE                NODWIN Clutch Series #13
    1081162  ex-RUSTEC vs Spirit Academy       CCT Europe 2026 Series #12
    1081163  BakS vs Saint Sinners              CCT Europe 2026 Series #12
    1081164  Inner Circle Academy vs Lavked    CCT Europe 2026 Series #12

The same API read again at 00:57Z returned those rows interleaved with rows the
00:07Z snapshot already had, so the most likely explanation is that Hotspawn
publishes fixtures into the feed lazily and the board is complete only as of its
own observation time. That explanation is **not** proven here, and this module
does not act on it: it does not invent a start time, a team identity or a
probability for a lobby-only row. It records the difference so the gap is
visible, countable and reviewable instead of silently missing.

What is deliberately not done
-----------------------------
* No row is synthesized. `normalize_fixtures` requires the feed's own
  `scheduled_start_time` and `lock_time`; a lobby listing supplies neither, so a
  lobby-only fixture cannot be priced without guessing.
* Hotspawn's own crowd percentages are never read as a probability.
* A missing lobby read is not an empty lobby: no ids are compared against a
  failed source.

The parser is intentionally narrow: it accepts one URL shape,
``/matches/<slug>-<fixture id>``, on hotspawn.com hosts, and nothing else.
The caller feeds it only the CS2 pick'em page (``play.hotspawn.com/cs2-pickems``):
the general lobby carries a sport switcher, so its anchors can name a non-CS2
match and are never used to claim a CS2 coverage gap.
"""
import re

# `https://www.hotspawn.com/matches/ground-zero-vs-off-chops-dfrag-invitational-2026-1082858`
# and the root-relative form `/matches/<slug>-<id>`. The fixture id is the final
# numeric segment of the slug, which is how Hotspawn builds every match permalink
# the collector already stores in `source_url`. `/api/v1/fixtures...` can never
# match because it does not start with `/matches/`.
SLUG = r'/matches/[A-Za-z0-9][A-Za-z0-9._~%+-]*?-(\d{5,})(?=["\'/?#<\s]|$)'
# Absolute permalinks must sit on a hotspawn.com host; a root-relative path is
# accepted because the lobby renders its own links that way. A third-party URL
# that merely contains "/matches/" is never counted as a Hotspawn fixture.
MATCH_PATH = re.compile(r'https?://(?:www\.|play\.)?hotspawn\.com' + SLUG)
RELATIVE_PATH = re.compile(r'(?<![/.\w])' + SLUG)

HOSTS = ('hotspawn.com',)


def ids_from_html(html):
    """Every Hotspawn fixture id a lobby/CS2 page links to, sorted, deduplicated.

    Returns an empty list for a non-string or empty body so a failed read can
    never be reported as "the lobby lists nothing".
    """
    if not isinstance(html, str) or not html:
        return []
    found = {m.group(1) for m in MATCH_PATH.finditer(html)}
    found |= {m.group(1) for m in RELATIVE_PATH.finditer(html)}
    return sorted(found)


def compare(feed_ids, lobby_ids):
    """Difference between the fixture feed and the lobby's own links.

    ``feed_ids`` are the ids the official feed returned for this capture;
    ``lobby_ids`` are the ids the lobby page linked to in the same run. Only ids
    present in the lobby and absent from the feed are reported, because those are
    the fixtures a visitor can see and the board cannot price.

    A lobby read that produced no ids is reported as ``lobby_read=False`` rather
    than as a gap of zero, so an unreadable page is never mistaken for parity.
    """
    feed = {str(x) for x in (feed_ids or []) if str(x).strip()}
    lobby = {str(x) for x in (lobby_ids or []) if str(x).strip()}
    missing = sorted(lobby - feed)
    return {
        'feed_count': len(feed),
        'lobby_count': len(lobby),
        'lobby_read': bool(lobby),
        'missing_from_feed': missing,
        'missing_count': len(missing),
    }


def summary_gap(rows, limit=None):
    """The gap as a short, quotable sentence; ``None`` when there is nothing to say."""
    rows = list(rows or [])
    if not rows:
        return None
    shown = rows if limit is None else rows[:limit]
    ids = ', '.join(shown)
    more = '' if len(shown) == len(rows) else ' and %d more' % (len(rows) - len(shown))
    return ('%d fixture(s) linked from the Hotspawn lobby are absent from this '
            'capture\'s official fixture feed: %s%s.' % (len(rows), ids, more))
