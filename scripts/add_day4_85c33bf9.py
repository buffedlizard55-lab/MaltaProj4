"""Session 85c33bf9 additive day-4 updates (2026-10-17 morning, UTC).

One verified identity alias, one renewed book-listing receipt, five dated
re-read rejections, three review flags and additive day-four analysis keys.
Every value below was read from a primary source in this session; the read
URLs and observation times travel with the value. Idempotent: re-running
never duplicates an entry and never edits an existing one.

Reads this file publishes (all 2026-10-17 UTC):
* Polymarket market 5778024 (FURIA-Aurora)   ~10:00, updatedAt 09:59:15Z
* Polymarket market 5787759 (Falcons-BetBoom) ~10:03, updatedAt 10:03:15Z
* Polymarket market 5796276 (Hacha-Los Niños) ~10:32, updatedAt 10:31:16Z
* Polymarket market 5799524 (Lavked-Sökerorg) ~10:33, updatedAt 10:27:15Z
* HLTV results page                           ~10:04
* HLTV betting analytics 2399415              ~10:22
* HLTV team pages 13722 / 14092 / 14084       ~10:37 / ~10:37 / ~10:52
* EGamersWorld match pages (manual reads; the site refuses the automated
  runner with HTTP 403, so these are hand-captured dated observations):
  ex-6666/Privateer 10:10 (page countdown '1d : 3h : 35m' to 18 Oct 13:45Z
  anchors the read), antidaun 10:11, Lynn Vision 10:11, Chinggis 10:13,
  VP.Future 10:13, Lavked 10:06.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITIES = ROOT / 'data/identities.json'
RECEIPTS = ROOT / 'data/book-receipts.json'
REVIEW = ROOT / 'data/review-notes.json'
ANALYSIS = ROOT / 'data/analysis.json'

GAMMA = 'https://gamma-api.polymarket.com/markets/'
HLTV_2399768 = 'https://www.hltv.org/matches/2399768/hacha-vs-los-ninos-cct-2026-south-america-series-7'
HOTSPAWN_1082019 = 'https://www.hotspawn.com/matches/hacha-vs-los-ninos-cct-south-america-2026-series-7-1082019'
EGW_EX6666 = 'https://egamersworld.com/counterstrike/match/rW6Ymkl0D/ex-6666-vs-privateer-gaming-sfo_MjtRV'
HLTV_2399681 = 'https://www.hltv.org/matches/2399681/ex-6666-vs-privateer-cct-2026-challengers-europe-series-8'
HOTSPAWN_1081521 = 'https://www.hotspawn.com/matches/ex-6666-vs-privateer-cct-europe-2026-challengers-8-1081521'

HACHA_ALIAS = {
    'canonical': 'Hacha',
    'names': ['Hacha', 'Hacha Esports'],
    'source': HLTV_2399768,
    'additional_source': GAMMA + '5796276',
    'basis': ("Fixture parity for a single sponsor-suffixed label, the same basis as the Privateer and "
        "BC.Game entries in this register. Hotspawn row 1082019 lists Hacha vs LOS NINOS in CCT South "
        "America 2026 Series #7 at 2026-10-17T22:00:00Z (lock 21:54 UTC). HLTV lists exactly one fixture "
        "in that slot: match 2399768 'Hacha vs LOS NINOS', CCT 2026 South America Series 7, start_unix "
        "2026-10-17T22:00:00Z, with lineups published for both clubs (HLTV team pages 13722 'Hacha', "
        "Argentina, and 14092 'LOS NINOS', Brazil). Polymarket market 5796276 'Counter-Strike: Hacha "
        "Esports vs Los Niños (BO3) - CCT South America Series 7 Group Stage' carries gameStartTime "
        "2026-10-17 22:00:00+00 and names hltv.org as its resolution source, so only the trailing "
        "'Esports' differs and no other club named Hacha appears in this competition. 'Los Niños' and "
        "'LOS NINOS' need no register entry: scripts/core.py plain_name folds diacritics (NFKD), which "
        "makes them one key (behaviour proven by research/ef0969b9/UNPRICED-FIXTURE-LINES.md). Exact "
        "opponent pair and UTC start are still required per market; main CS2 team label only; no academy "
        "or roster-continuity inference. The HLTV match-page lineup for Hacha (Lucasye, superex, toto, "
        "BUSAN, Rivo) shares only two of five players with the HLTV team-page roster (Lucasye, aidy y, "
        "guztt, frG, superex); that discrepancy is flagged in data/review-notes.json "
        "(hacha-market-thin-85c33bf9) and does not affect the label mapping."),
}

EX6666_RECEIPT = {
    'provider': 'EGamersWorld book listing',
    'id': 'egw-rW6Ymkl0D-ex-6666-privateer-1010z',
    'fixture_id': '1081521',
    'source_teams': ['ex-6666', 'Privateer Gaming'],
    'team_aliases': [['ex-6666'], ['Privateer Gaming', 'Privateer']],
    'alias_sources': [HLTV_2399681, HOTSPAWN_1081521],
    'start': '2026-10-18T13:45:00Z',
    'best_of': 3,
    'odds': [1.13, 4.75],
    'observed_at': '2026-10-17T10:10:00Z',
    'url': EGW_EX6666,
    'api_url': EGW_EX6666,
    'event': 'CCT Europe 2026 Challengers #8',
    'identity_evidence': [
        {'label': "HLTV match page for the same fixture: ex-6666 vs Privateer, CCT Europe 2026 Challengers #8, 18 October 2026 13:45 UTC, best of 3",
         'url': HLTV_2399681},
        {'label': "Hotspawn board row 1081521: ex-6666 vs Privateer, 2026-10-18T13:45:00Z, lock 13:39 UTC. 'Privateer' is the same club as the listing's 'Privateer Gaming' (register entry; same opponent, same slot, same UTC start).",
         'url': HOTSPAWN_1081521},
        {'label': "EGamersWorld match page: title 'ex-6666 VS Privateer Gaming: 18.10.2026 at 13:45' (UTC) and header odds row ex-6666 1.13 / Privateer Gaming 4.75, Bo3, CCT Europe 2026 Challengers #8. The page's own countdown '1d : 3h : 35m' to 18 Oct 13:45 UTC anchors this read at ~10:10 UTC on 17 October.",
         'url': EGW_EX6666},
    ],
    'corroboration': [
        {'label': 'Same page, EGWxxxBOT book-average summary (verbatim)',
         'text': 'ex-6666 are listed as the favorites of the match in the majority of bookmakers and odds on them are equal to 1.13. Privateer Gaming, in turn, are the outsiders of the match. Odds on their victory are about 4.75.'},
        {'label': 'The header odds row repeats the pair (1.13 / 4.75), so the sentence and the header agree.',
         'url': EGW_EX6666},
        {'label': 'Supersedes receipt egw-rW6Ymkl0D-ex-6666-privateer (observed 2026-10-17T00:45:00Z, odds 1.15/4.5), which aged out of the eight-hour evidence window at 08:45 UTC and left the row on the originated model line (78.2/21.8). De-margined, this listing is ex-6666 80.8% / Privateer 19.2% (overround 9.5%), the same direction as the model line.'},
        {'label': 'The 00:45Z receipt URL variant under the EkjkYUfoNl event prefix redirected to the EGW matches listing at the 10:07 UTC read; the canonical rW6Ymkl0D URL above resolves to the match page.',
         'url': EGW_EX6666},
    ],
    'limitation': ("Aggregator listing of bookmaker odds: the underlying books are not named on the header row and "
        "no price-update timestamp is supplied, so the observation time is what ages out. Read manually through the "
        "session's document-retrieval path because EGamersWorld refuses the project's automated runner with HTTP 403, "
        "so this is a dated observation, not a self-refreshing line; it expires eight hours after observation "
        "(2026-10-17T18:10 UTC), before the 18 October 13:45 UTC start, after which the row falls back to the "
        "originated model line and the reason is published. Observed 2026-10-17T10:10:00Z."),
}

REREAD_REJECTIONS = [
    {'fixture_id': '1079634', 'teams': ['Lavked', 'LFO 10'],
     'url': 'https://egamersworld.com/counterstrike/match/_rW8GEyWK/lavked-vs-z6CTAa5pD',
     'observed_at': '2026-10-17T10:06:00Z', 'displayed': [1.8, 1.8],
     'reason': ("Re-read 17 October ~10:06 UTC: still the identical default odds 1.8/1.8 and an empty opponent label "
         "('Lavked VS'; the second team's name, logo and record are blank, though a Swedish lineup is shown: Jackinho, "
         "Sapec, dottie, flaw, tvs). Polymarket market 5799524 names the same 11:00 UTC CCT Europe Series #11 slot "
         "'Lavked vs Sökerorg' at 0.6/0.4, but no primary source read in this session states that Sökerorg is LFO 10 "
         "(HLTV team page 14084 lists no roster and no alternate name; the HLTV match-page lineup L00m1, Sapec, flaw, "
         "dottie, Mann3n and the EGW lineup share only three names), so that quote was not transferred on a name guess. "
         "The row kept its research-only pick (Lavked, HLTV world #140 against an unranked opponent) and locked at "
         "10:54 UTC; HLTV's live widget showed the series started 0-0 at the 10:52 UTC team-page read.")},
    {'fixture_id': '1081522', 'teams': ['antidaun', 'Phantom Academy'],
     'url': 'https://egamersworld.com/counterstrike/match/rW6Ymkl0D/antidaun-vs-phantom-academy-zXFTwo17o8',
     'observed_at': '2026-10-17T10:11:00Z', 'displayed': [1.8, 1.8],
     'reason': ("Re-read 17 October ~10:11 UTC (page countdown '1d : 3h : 34m' to 18 Oct 13:45 UTC): still the "
         "identical default odds 1.8/1.8 on both sides - a listing placeholder, not a two-sided market line; the "
         "16-17 October reads under both event prefixes showed the same placeholder. antidaun is absent from Valve's "
         "5 October global standings (Phantom Academy is listed #172), so no two-sided originated line exists either. "
         "The row keeps its research-only pick (Phantom Academy, HLTV world #178) with no percentage.")},
    {'fixture_id': '1081861', 'teams': ['Lynn Vision', 'Morningstar'],
     'url': 'https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/lynn-vision-vs-morningstar-7AWA3eTHD',
     'observed_at': '2026-10-17T10:11:00Z', 'displayed': [1.8, 1.8],
     'reason': ("Re-read 17 October ~10:11 UTC (page countdown '2d : 16h : 49m' to 20 Oct 03:00 UTC): still the "
         "identical default odds 1.8/1.8 - placeholder, not a line. Morningstar is absent from Valve's 5 October "
         "global standings (Lynn Vision is listed #64, 1190 points), so no originated line is possible. The row keeps "
         "its research-only pick (Lynn Vision, HLTV world #39) with no percentage.")},
    {'fixture_id': '1081863', 'teams': ['Chinggis Warriors', 'WXM'],
     'url': 'https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/chinggis-warriors-vs-wxm-_ddme1I7dZ',
     'observed_at': '2026-10-17T10:13:00Z', 'displayed': [1.8, 1.8],
     'reason': ("Re-read 17 October ~10:13 UTC (page countdown '2d : 20h : 47m' to 20 Oct 07:00 UTC): still the "
         "identical default odds 1.8/1.8, and the WXM side shows a blank label and five placeholder players. WXM is "
         "absent from Valve's 5 October global standings; Chinggis Warriors appears twice there (#87 with cool4st, "
         "fury5k, ROUX, sk0R, yAmi and #220 with Aceari, hasteka, ROUX, sk0R, yAmi), so even a listed opponent would "
         "still need roster-based label disambiguation before an originated line. The row keeps its research-only pick "
         "(Chinggis Warriors, HLTV world #61) with no percentage.")},
    {'fixture_id': '1081511', 'teams': ['VP.Future', 'Black Phoenix'],
     'url': 'https://egamersworld.com/counterstrike/match/Eklp98tP5Ee/vpfuture-vs-black-phoenix-dGceA4XCC',
     'observed_at': '2026-10-17T10:13:00Z', 'displayed': [1.8, 1.8],
     'reason': ("Re-read 17 October ~10:13 UTC: still the identical default odds 1.8/1.8, and the match is already "
         "live - the EGW live score widget at the read showed Black Phoenix leading the series 1-0 after winning "
         "Inferno 13-10 (live score at read time, not a final result). The Hotspawn pick for this row locked at "
         "08:54 UTC, so no listing could have priced the row in time regardless. It keeps its research-only pick "
         "(Black Phoenix, HLTV world #57 against an unranked VP.Future; VP.Future is Virtus.pro's academy label and "
         "is not mapped to the Virtus.pro standing, per the no-academy-inference rule).")},
]

REVIEW_NOTES = [
    {'id': 'hacha-alias-verified-85c33bf9',
     'status': 'Resolved \u2014 verified alias registered; row priceable at the next refresh',
     'finding': ("The identity gap flagged by coverage-gap-90795adf for row 1082019 (Hacha vs LOS NINOS, CCT South "
         "America 2026 Series #7, 2026-10-17T22:00:00Z) is closed on primary sources. HLTV match 2399768 is the only "
         "fixture in that event slot at that exact UTC start and names both clubs (team pages 13722 Hacha/Argentina "
         "and 14092 LOS NINOS/Brazil, each linking the other as their 17 October opponent). Polymarket market 5796276 "
         "'Hacha Esports vs Los Niños (BO3) - CCT South America Series 7 Group Stage' carries the identical "
         "gameStartTime 2026-10-17 22:00:00+00 and names hltv.org as resolution source. The register entry maps only "
         "'Hacha Esports' to 'Hacha' (fixture parity, same precedent as Privateer Gaming and BC.Game Esports); "
         "'Los Niños'/'LOS NINOS' already fold to one key via core.plain_name diacritic folding and need no entry. At "
         "the 10:32 UTC read the market was 0.395/0.605 with a 41-point spread and $128.97 liquidity, which is the "
         "labelled wide low-confidence tier (spread over the 25-point strict ceiling, under the 60-point wide ceiling, "
         "liquidity over the $100 floor): pick LOS NINOS, direction only. No quote was transferred before the alias "
         "was verified."),
     'sources': [
         {'label': 'HLTV fixture 2399768 (both clubs, exact 22:00 UTC start, lineups)', 'url': HLTV_2399768},
         {'label': 'HLTV team page 13722 (Hacha, Argentina; next match 17 Oct vs LOS NINOS)', 'url': 'https://www.hltv.org/team/13722/hacha'},
         {'label': 'HLTV team page 14092 (LOS NINOS, Brazil; next match 17 Oct vs Hacha)', 'url': 'https://www.hltv.org/team/14092/los-ninos'},
         {'label': 'Polymarket market 5796276 (Hacha Esports vs Los Niños, gameStartTime 2026-10-17 22:00:00+00, resolution source hltv.org)', 'url': GAMMA + '5796276'},
         {'label': 'Hotspawn board row 1082019', 'url': HOTSPAWN_1082019},
         {'label': 'Identity register entry (this PR)', 'url': 'https://github.com/buffedlizard55-lab/MaltaProj4/blob/main/data/identities.json'},
     ]},
    {'id': 'hacha-market-thin-85c33bf9',
     'status': 'Needs review \u2014 thin volatile wide market and a Hacha lineup discrepancy',
     'finding': ("Two honest warnings ride along with the new Hacha vs LOS NINOS price. (1) The exchange market is "
         "thin and volatile: $27.18 total volume at the 10:32 UTC read, $128.97 liquidity, bid/ask 0.19/0.60 "
         "(41-point spread), a last-trade print of 0.95 against outcome prices 0.395/0.605, a -0.20 one-hour price "
         "change, and outcome prices that moved 0.47/0.53 \u2192 0.395/0.605 between the 10:05 UTC runner capture and "
         "the 10:32 UTC read. The wide tier publishes the real spread and a low-confidence label; the direction "
         "(LOS NINOS favoured) is the usable signal, not the exact number, and each refresh re-reads the market. "
         "(2) HLTV's match-page lineup for Hacha (Lucasye, superex, toto, BUSAN, Rivo) shares only two of five "
         "players with HLTV's team-page roster (Lucasye, aidy y, guztt, frG, superex), which suggests stand-ins. "
         "That is a sourced observation only: no probability adjustment is made from it and no fatigue or "
         "'weakened roster' number is claimed."),
     'sources': [
         {'label': 'Polymarket market 5796276 (all quoted market fields)', 'url': GAMMA + '5796276'},
         {'label': 'Runner capture of the same market at 10:05 UTC (0.47/0.53)', 'url': 'https://github.com/buffedlizard55-lab/MaltaProj4/tree/main/research/harvest-85c33bf9'},
         {'label': 'HLTV fixture 2399768 (match-page lineup)', 'url': HLTV_2399768},
         {'label': 'HLTV team page 13722 (main roster)', 'url': 'https://www.hltv.org/team/13722/hacha'},
     ]},
    {'id': 'lfo10-sokerorg-unverified-85c33bf9',
     'status': 'Needs review \u2014 unverified alias; quote not transferred',
     'finding': ("Polymarket market 5799524 'Lavked vs Sökerorg (BO3) - CCT Europe Series #11 Group Stage' "
         "(gameStartTime 2026-10-17 11:00:00+00, outcome prices 0.6/0.4, bid/ask 0.57/0.63, liquidity $191.84, "
         "volume $5, read ~10:33 UTC) occupies the same slot as Hotspawn row 1079634 'Lavked vs LFO 10' and HLTV "
         "match 2399311 'Lavked vs LFO 10'. The Lavked side matches exactly, but no primary source read in this "
         "session states that 'Sökerorg' is 'LFO 10': the names share no tokens; HLTV team page 14084 (LFO 10, "
         "Sweden) lists no roster and no alternate name; and the two third-party lineup listings disagree (HLTV "
         "match page: L00m1, Sapec, flaw, dottie, Mann3n; EGamersWorld, which leaves the team label blank: "
         "Jackinho, Sapec, dottie, flaw, tvs). A Polymarket rename or a roster swap could explain either listing, "
         "but both are inference, so the 0.6/0.4 quote was not transferred and no alias was registered. The row "
         "kept its research-only pick (Lavked, HLTV world #140 against an opponent with no HLTV world-ranking "
         "number) and locked at 10:54 UTC; the series was live 0-0 at the 10:52 UTC read. If a primary source for "
         "the mapping appears, the register entry and the line can be added before any future fixture between "
         "these labels."),
     'sources': [
         {'label': 'Polymarket market 5799524 (Lavked vs Sökerorg)', 'url': GAMMA + '5799524'},
         {'label': 'HLTV fixture 2399311 (Lavked vs LFO 10, lineups, 11:00 UTC)', 'url': 'https://www.hltv.org/matches/2399311/lavked-vs-lfo-10-cct-2026-europe-series-11'},
         {'label': 'HLTV team page 14084 (LFO 10; no roster, no alternate name; live widget at read time)', 'url': 'https://www.hltv.org/team/14084/lfo-10'},
         {'label': 'EGamersWorld listing (blank opponent label, Swedish lineup, placeholder 1.8/1.8)', 'url': 'https://egamersworld.com/counterstrike/match/_rW8GEyWK/lavked-vs-z6CTAa5pD'},
     ]},
]

ANALYSIS_POINTS = [
    {'claim': 'Day-4 morning re-read (~10:00-10:03 UTC): the Falcons-BETBOOM exchange line moved toward BETBOOM, from 79.5/20.5 to 72.5/27.5.',
     'detail': ("Polymarket market 5787759 outcome prices were 0.795/0.205 at the 17 October 00:10 UTC read and "
         "0.725/0.275 at the market's own 10:03:15 UTC update; liquidity rose from $60,452.33 to $195,389.17 and "
         "volume from about $12,271 to $178,947.70, with bid/ask 0.72/0.73 (1-point spread) and orders still being "
         "accepted. The board pick stays Falcons, now at 72.5%; BETBOOM at 27.5% sits inside the project's 15-40% "
         "risk band (a deliberate high-variance swing, not a recommended value pick). The move is published as "
         "sourced market information only - it is not evidence for a fatigue or rest effect, and per the corrected "
         "day-4 framing both semi-final underdogs played on 16 October while both favourites last played on "
         "15 October, so shorter recovery is a counterweight for the dogs, not an edge."),
     'source': GAMMA + '5787759'},
    {'claim': 'FURIA-Aurora held steady through the same window: 52.5/47.5, with liquidity nearly doubled.',
     'detail': ("Polymarket market 5778024 outcome prices were unchanged at 0.525/0.475 (market update 09:59:15 UTC, "
         "read ~10:00 UTC), bid/ask 0.52/0.53 (1-point spread), last trade 0.53; liquidity rose from $158,627.63 at "
         "the 00:10 UTC read to $306,044.98 and volume stands at $68,930.31. Board pick: FURIA. Aurora remains the "
         "priced contrarian option at 47.5% - a coin flip, not a long shot - and the HLTV odds page still disagrees "
         "with the exchange about which side is the bookmaker favourite; the disagreement stays published."),
     'source': GAMMA + '5778024'},
    {'claim': "HLTV's betting-analytics page for the second semi-final ranks Falcons #5 and BETBOOM #14, with Falcons three wins from their last five.",
     'detail': ("Read ~10:22 UTC for match 2399415: the analytics summary lists 'Falcons has better form ranking', "
         "'Falcons has won 3 out of the last 5 matches', 'Falcons is better ranked (#5)' and 'BETBOOM is worse ranked "
         "(#14)'; no insights were detected for BETBOOM. HLTV ranks and form are context for the reader - they are "
         "not a pricing input anywhere on this board, and no rank-to-probability formula is applied to them."),
     'source': 'https://www.hltv.org/betting/analytics/2399415/falcons-vs-betboom-thunderpick-world-championship-2026'},
    {'claim': 'Day-4 morning board results (HLTV, read ~10:05 UTC): ex-6666 beat G2 Ares 2-0 - the originated model pick on row 1079633 settled correct.',
     'detail': ("Completed 17 October results on HLTV's results page at the read: G2 Ares 0-2 ex-6666 (CCT 2026 "
         "Europe Series 11, match 2399310) - the 01:05 UTC snapshot carried that row as model_vrs ex-6666 51.1%; "
         "Rooster 0-2 Off Chops (DFRAG Logitech G Pro Series, 2399546); FlyQuest 2-1 NEXVOID (DFRAG, 2399545 - "
         "NEXVOID next appears on the board 20 October vs Vitalem Aerem, row 1081864). The other morning board rows "
         "(NiP-Heroic, WBT-HAVU, Eternal Fire-Nuclear TigeRES, 33-Just Players, VP.Future-Black Phoenix) were live "
         "at the read; the EGW live widget showed Black Phoenix leading VP.Future 1-0 after Inferno 13-10. Live "
         "scores are observations at a timestamp, not final results, and none is published as a result here."),
     'source': 'https://www.hltv.org/results'},
    {'claim': 'The new board row Hacha vs LOS NINOS (1082019, 22:00 UTC tonight) now has a verified exchange path - the last no-pick row on the board.',
     'detail': ("Polymarket market 5796276 'Hacha Esports vs Los Niños (BO3) - CCT South America Series 7 Group "
         "Stage' carries gameStartTime 2026-10-17 22:00:00+00, exactly the Hotspawn row's UTC start, and names "
         "hltv.org as its resolution source; HLTV fixture 2399768 is the only match in that slot. The alias register "
         "now maps 'Hacha Esports' to 'Hacha' on that fixture parity (Los Niños/LOS NINOS fold together by "
         "diacritic normalization alone). At the 10:32 UTC read the market was 0.395/0.605 with a 41-point spread "
         "(bid 0.19 / ask 0.60) and $128.97 liquidity on $27.18 volume: that is the labelled wide low-confidence "
         "tier, direction LOS NINOS (60.5%) over Hacha (39.5%). The market moved from 0.47/0.53 at the 10:05 UTC "
         "runner capture and once printed a 0.95 last trade, so the number is directional only and each refresh "
         "re-reads it."),
     'source': GAMMA + '5796276'},
]

ANALYSIS_UNPRICED = {
    'label': 'Research-only board rows with no percentage \u2014 re-verified 17 October, 10:05-10:55 UTC',
    'when': 'Re-read window 10:05-10:55 UTC \u00b7 rows 1079634, 1081522, 1081861, 1081863',
    'status': 'Four open rows keep sourced research-only picks; no reachable source publishes a two-sided line',
    'limitation': ("Each of the four was re-checked line by line this morning. (1) 1079634 Lavked vs LFO 10 (11:00 "
        "UTC, locked 10:54): EGW listing is the 1.8/1.8 placeholder with a blank opponent label; Polymarket lists "
        "the same slot as 'Lavked vs Sökerorg' at 0.6/0.4, but no primary source read states Sökerorg is LFO 10 "
        "(names share no tokens; HLTV team page 14084 shows no roster or alternate name; the HLTV and EGW lineup "
        "listings disagree), so the quote was not transferred on a name guess and the row kept its research pick "
        "(Lavked, HLTV #140 vs unranked). (2) 1081522 antidaun vs Phantom Academy (18 Oct 13:45 UTC): EGW "
        "placeholder 1.8/1.8 at the 10:11 UTC re-read; antidaun is absent from Valve's 5 October standings "
        "(Phantom Academy #172), so no originated line. Research pick: Phantom Academy (HLTV #178). (3) 1081861 "
        "Lynn Vision vs Morningstar (20 Oct 03:00 UTC): EGW placeholder at 10:11 UTC; Morningstar absent from "
        "Valve's standings (Lynn Vision #64). Research pick: Lynn Vision (HLTV #39). (4) 1081863 Chinggis Warriors "
        "vs WXM (20 Oct 07:00 UTC): EGW placeholder with a blank WXM side at 10:13 UTC; WXM absent from Valve's "
        "standings and Chinggis Warriors appears twice there (#87, #220) needing roster disambiguation. Research "
        "pick: Chinggis Warriors (HLTV #61). For all four, the 10:05 UTC runner harvest confirms no Pinnacle "
        "matchup, no numeric HLTV betting rows and no Polymarket market under verified labels; percentages stay "
        "blank rather than invented, and each pick remains re-derivable from its stored HLTV ranking evidence. "
        "A fifth row from the overnight list, 1081511 VP.Future vs Black Phoenix, went live at 09:00 UTC (pick "
        "locked 08:54) with its EGW listing still a placeholder; it keeps its research pick (Black Phoenix, HLTV "
        "#57) and no longer accepts picks."),
    'sources': [
        {'url': GAMMA + '5799524', 'label': 'Polymarket 5799524 (Lavked vs Sökerorg, 0.6/0.4, start 11:00 UTC) - alias unverified, not transferred'},
        {'url': 'https://www.hltv.org/matches/2399311/lavked-vs-lfo-10-cct-2026-europe-series-11', 'label': 'HLTV fixture 2399311 (Lavked #140 vs unranked LFO 10, lineups)'},
        {'url': 'https://www.hltv.org/team/14084/lfo-10', 'label': 'HLTV team page 14084 (LFO 10: no roster, no alternate name)'},
        {'url': 'https://egamersworld.com/counterstrike/match/rW6Ymkl0D/antidaun-vs-phantom-academy-zXFTwo17o8', 'label': 'EGW antidaun vs Phantom Academy (placeholder 1.8/1.8 at 10:11 UTC)'},
        {'url': 'https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/lynn-vision-vs-morningstar-7AWA3eTHD', 'label': 'EGW Lynn Vision vs Morningstar (placeholder 1.8/1.8 at 10:11 UTC)'},
        {'url': 'https://egamersworld.com/counterstrike/match/EJcHRdr5Vx/chinggis-warriors-vs-wxm-_ddme1I7dZ', 'label': 'EGW Chinggis Warriors vs WXM (placeholder 1.8/1.8 at 10:13 UTC)'},
        {'url': 'https://github.com/ValveSoftware/counter-strike_regional_standings/blob/eec4853d7bcf0f1f7efe7f0d901234bef7e98b75/live/2026/standings_global_2026_10_05.md', 'label': "Valve official global standings 2026-10-05 (missing sides: LFO 10, antidaun, Morningstar, WXM, VP.Future)"},
        {'url': 'https://github.com/buffedlizard55-lab/MaltaProj4/tree/main/research/harvest-85c33bf9', 'label': 'Runner harvest 10:05 UTC (Pinnacle/HLTV/Polymarket attempt receipts per row)'},
    ],
}

ANALYSIS_UNVERIFIED = [
    ("The Polymarket label 'Sökerorg' for Lavked's 11:00 UTC opponent (market 5799524, 0.6/0.4) is not verified as "
     "HLTV/Hotspawn's 'LFO 10': the names share no tokens, HLTV team page 14084 lists no roster and no alternate "
     "name, and the third-party lineup listings disagree (HLTV match page: L00m1, Sapec, flaw, dottie, Mann3n; "
     "EGamersWorld with a blank team label: Jackinho, Sapec, dottie, flaw, tvs). The quote was not transferred and "
     "row 1079634 kept its research-only pick (Lavked) before locking at 10:54 UTC."),
    ("The Hacha Esports\u2194Hacha mapping is fixture-parity identity evidence (same event slot, same exact UTC start, "
     "HLTV as Polymarket's resolution source, register precedent), not roster confirmation. HLTV's match-page lineup "
     "for Hacha (Lucasye, superex, toto, BUSAN, Rivo) shares only two of five players with HLTV's team-page roster "
     "(Lucasye, aidy y, guztt, frG, superex), suggesting stand-ins; no probability adjustment is derived from this."),
    ("The Hacha vs LOS NINOS exchange market (5796276) is thin and volatile: $27.18 volume at the 10:32 UTC read, "
     "$128.97 liquidity, a 41-point bid/ask spread (0.19/0.60), a 0.95 last-trade print against 0.395/0.605 outcome "
     "prices, a -0.20 one-hour change, and a move from 0.47/0.53 at 10:05 UTC. It is published only through the "
     "labelled wide low-confidence tier; the direction (LOS NINOS favoured) is the usable signal, not the number."),
]


def apply_identities():
    doc = json.loads(IDENTITIES.read_text())
    if any(a.get('canonical') == 'Hacha' for a in doc['aliases']):
        return 'identities: Hacha entry already present'
    doc['aliases'].append(HACHA_ALIAS)
    doc['reviewed_at'] = '2026-10-17'
    IDENTITIES.write_text(json.dumps(doc, indent=2) + '\n')
    return 'identities: added Hacha / Hacha Esports entry'


def apply_receipts():
    doc = json.loads(RECEIPTS.read_text())
    out = []
    if not any(r.get('id') == EX6666_RECEIPT['id'] for r in doc['receipts']):
        doc['receipts'].append(EX6666_RECEIPT)
        out.append('receipts: added renewed ex-6666/Privateer listing (1.13/4.75 @ 10:10Z)')
    else:
        out.append('receipts: renewed ex-6666 receipt already present')
    have = {(r.get('url'), r.get('observed_at')) for r in doc.get('rejected_listings', [])}
    added = 0
    for entry in REREAD_REJECTIONS:
        if (entry['url'], entry['observed_at']) not in have:
            doc.setdefault('rejected_listings', []).append(entry)
            added += 1
    out.append('rejected_listings: added %d dated re-reads' % added)
    if '85c33bf9' not in doc.get('collected_by', ''):
        doc['collected_by'] = doc.get('collected_by', '') + ' and 85c33bf9'
        doc['collected_at'] = '2026-10-17T10:13:00Z'
    RECEIPTS.write_text(json.dumps(doc, indent=1) + '\n')
    return '; '.join(out)


def apply_review_notes():
    notes = json.loads(REVIEW.read_text())
    have = {n.get('id') for n in notes}
    added = [n['id'] for n in REVIEW_NOTES if n['id'] not in have]
    for n in REVIEW_NOTES:
        if n['id'] not in have:
            notes.append(n)
    REVIEW.write_text(json.dumps(notes, indent=1) + '\n')
    return 'review-notes: added %s' % (added or 'nothing (already present)')


def apply_analysis():
    doc = json.loads(ANALYSIS.read_text())
    d4 = doc['day_four_guidance']
    claims = {p.get('claim') for p in d4.get('points', [])}
    added = 0
    for p in ANALYSIS_POINTS:
        if p['claim'] not in claims:
            d4['points'].append(p)
            added += 1
    labels = {u.get('label') for u in d4.get('unpriced', [])}
    unpriced_added = 0
    if ANALYSIS_UNPRICED['label'] not in labels:
        d4['unpriced'].append(ANALYSIS_UNPRICED)
        unpriced_added = 1
    have_u = set(d4.get('unverified', []))
    unverified_added = 0
    for s in ANALYSIS_UNVERIFIED:
        if s not in have_u:
            d4['unverified'].append(s)
            unverified_added += 1
    doc['reviewed_at_utc'] = '2026-10-17T10:55:00Z'
    ANALYSIS.write_text(json.dumps(doc, indent=1) + '\n')
    return 'analysis: +%d points, +%d unpriced, +%d unverified' % (added, unpriced_added, unverified_added)


if __name__ == '__main__':
    print(apply_identities())
    print(apply_receipts())
    print(apply_review_notes())
    print(apply_analysis())
