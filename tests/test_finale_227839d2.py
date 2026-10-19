"""Session 227839d2: completed-event results, pick record and archive gating.

The Thunderpick World Championship 2026 finished on 18 October 2026. Three things
have to hold, and each one is asserted here:

* the final-day results stored in ``data/analysis.json`` are the ones published on
  the official HLTV match pages, with a working link for each;
* the pick record replays only picks this site actually published, and scores them
  against the official winner (never the reverse);
* a build made after the final day stops presenting the final-day guide as if the
  matches were still ahead, while a build made from the pre-match capture keeps it.

Nothing in this file produces a probability. A missing or contradictory field is a
test failure, not a value to infer.
"""
import copy
import json
import re
import unittest
from datetime import timezone
from pathlib import Path

from scripts import build
from scripts.core import dt

ROOT = Path(__file__).resolve().parents[1]
NOTES = json.loads((ROOT / 'data/analysis.json').read_text())
DATA = json.loads((ROOT / 'data/latest.json').read_text())
PRE_MATCH = dt('2026-10-18T01:00:00Z')
AFTER = dt('2026-10-19T04:00:00Z')


def split_maps(text):
    """One stored map list, split on the separators the data actually uses."""
    return [part.strip() for part in re.split(r'[;,]', text) if part.strip()]


def snapshot(observed):
    """A snapshot as it would look if it had just been built for ``observed``.

    ``built_at`` is the moment the page is generated for (build_moment prefers it),
    so it has to move with ``generated_at`` or the page would still be dated by the
    committed build receipt.
    """
    data = copy.deepcopy(DATA)
    data['generated_at'] = observed
    data['last_attempt_at'] = observed
    data['built_at'] = observed
    return data


class EventCompletion(unittest.TestCase):
    def test_event_is_marked_complete_with_a_source(self):
        event = NOTES['event']
        self.assertTrue(event['completed'])
        self.assertEqual(event['completed_date'], '2026-10-18')
        self.assertEqual(event['champion'], 'FURIA')
        for key in ('champion_source', 'status_source'):
            self.assertTrue(event[key].startswith('https://www.hltv.org/'), key)
        self.assertIn('/matches/2399417/', event['champion_source'])
        self.assertEqual(event['status_source'], 'https://www.hltv.org/results?event=8932')

    def test_final_day_series_match_the_hltv_pages(self):
        final = NOTES['day_five_results']
        self.assertEqual(final['key'], 'day-five-results')
        self.assertEqual(final['results_url'], 'https://www.hltv.org/results?event=8932')
        grand = next(m for m in final['matches'] if m['stage'].lower().startswith('grand final'))
        third = next(m for m in final['matches'] if 'third-place' in m['stage'].lower() or '3rd place' in m['stage'].lower())
        self.assertEqual((grand['winner'], grand['loser'], grand['score']), ('FURIA', 'BETBOOM', '3-2'))
        self.assertEqual((third['winner'], third['loser'], third['score']), ('Aurora', 'Falcons', '2-1'))
        self.assertIn('/2399417/', grand['match_url'])
        self.assertIn('/2399416/', third['match_url'])
        # Map scores were read from those match pages; the grand final's five maps
        # and the decider's three are the shape HLTV published.
        self.assertEqual(len(split_maps(grand['maps'])), 5)
        self.assertEqual(len(split_maps(third['maps'])), 3)
        for m in final['matches']:
            self.assertTrue(m['match_url'].startswith('https://www.hltv.org/matches/'))
            self.assertEqual(m['report_url'], final['results_url'])
            self.assertTrue(m['flag'])

    def test_map_scores_reproduce_each_series_score(self):
        # Each stored map string is "Map a-b" where a is the score of the series
        # winner listed first in the results line and b is the opponent's score.
        # If those map winners do not add up to the stored series score, the row is
        # internally inconsistent and must not be published.
        for match in NOTES['day_five_results']['matches']:
            winner_maps = 0
            loser_maps = 0
            for entry in split_maps(match['maps']):
                _map, score = entry.rsplit(' ', 1)
                left, right = (int(x) for x in score.split('-'))
                if left > right:
                    winner_maps += 1
                else:
                    loser_maps += 1
            self.assertEqual('%d-%d' % (winner_maps, loser_maps), match['score'], match['stage'])


class PickRecord(unittest.TestCase):
    def test_every_entry_is_sourced_and_scored_against_the_winner(self):
        entries = NOTES['pick_record']['entries']
        self.assertEqual(len(entries), 4)
        for row in entries:
            self.assertIn(row['outcome'], ('correct', 'incorrect'))
            self.assertTrue(row['result_url'].startswith('https://www.hltv.org/matches/'))
            self.assertTrue(row['chance_source'].startswith('https://'))
            self.assertGreater(row['chance'], 0)
            self.assertLess(row['chance'], 1)
            self.assertEqual(row['outcome'] == 'correct', row['winner'] == row['pick'], row['fixture'])
            self.assertTrue(row['result'].startswith(row['winner'] + ' '), row['result'])
            self.assertIn(row['pick'], row['fixture'])

    def test_tally_is_recomputable_from_the_entries(self):
        record = NOTES['pick_record']
        correct = sum(1 for row in record['entries'] if row['outcome'] == 'correct')
        self.assertEqual(record['tally']['priced_picks'], len(record['entries']))
        self.assertEqual(record['tally']['correct'], correct)
        mean = sum(row['chance'] for row in record['entries']) / len(record['entries'])
        self.assertAlmostEqual(record['tally']['mean_published_chance'], mean, places=4)
        self.assertAlmostEqual(record['tally']['observed_win_rate'], correct / len(record['entries']), places=4)

    def test_the_two_final_day_rows_carry_the_board_prices(self):
        by_id = {row['hotspawn_id']: row for row in NOTES['pick_record']['entries']}
        self.assertAlmostEqual(by_id['1080209']['chance'], 0.605)
        self.assertAlmostEqual(by_id['1080210']['chance'], 0.705)
        self.assertEqual(by_id['1080209']['pick'], 'Falcons')
        self.assertEqual(by_id['1080210']['pick'], 'FURIA')
        # The board rows themselves still exist in the retained snapshot with those prices.
        rows = {m['id']: m for m in DATA['matches']}
        self.assertAlmostEqual(rows['1080209']['probabilities'][0], 0.605)
        self.assertAlmostEqual(rows['1080210']['probabilities'][0], 0.705)

    def test_contrarian_calls_are_scored_separately(self):
        contrarian = NOTES['pick_record']['contrarian']
        self.assertEqual(contrarian['tally']['calls'], len(contrarian['entries']))
        correct = sum(1 for row in contrarian['entries'] if row['outcome'] == 'correct')
        self.assertEqual(contrarian['tally']['correct'], correct)
        for row in contrarian['entries']:
            self.assertTrue(row['result_url'].startswith('https://www.hltv.org/matches/'))


class ArchiveGating(unittest.TestCase):
    def test_archive_gate_follows_the_snapshot_date(self):
        self.assertFalse(build.event_archived(NOTES, PRE_MATCH))
        self.assertTrue(build.event_archived(NOTES, AFTER))
        # An unparseable timestamp falls back to pre-match presentation, never results.
        self.assertFalse(build.event_archived(NOTES, 'not-a-timestamp'))
        # No completion date means the event is still treated as running.
        notes = copy.deepcopy(NOTES)
        notes['event'].pop('completed_date')
        notes['event']['completed'] = False
        self.assertFalse(build.event_archived(notes, PRE_MATCH))

    def test_front_page_before_the_final_day_keeps_the_pre_match_guide(self):
        html = build.overview(snapshot('2026-10-18T01:00:00Z'))
        self.assertIn('Day-5 final-day guide', html)
        self.assertNotIn('analysis.html#twc-final-summary', html)
        self.assertNotIn('id="twc-archive"', html)

    def test_front_page_after_the_final_day_points_at_the_results(self):
        html = build.overview(snapshot('2026-10-19T04:00:00Z'))
        self.assertIn('analysis.html#twc-final-summary', html)
        self.assertIn('id="twc-archive"', html)
        self.assertNotIn('analysis.html#day-five-guidance', html)
        self.assertIn('TWC final results', html)

    def test_analysis_page_shows_results_only_after_the_event(self):
        late = build.analysis_page(snapshot('2026-10-19T04:00:00Z'))
        self.assertIn('id="twc-final-summary"', late)
        self.assertIn('id="pick-record"', late)
        self.assertIn('FURIA won the Thunderpick World Championship 2026.', late)
        self.assertIn('Maps (series winner first)', late)
        # The day-two orientation correction travels with the row it corrects.
        self.assertIn('Correction: Re-read from the HLTV match page', late)
        self.assertIn('https://www.hltv.org/matches/2399417/', late)
        early = build.analysis_page(snapshot('2026-10-18T01:00:00Z'))
        self.assertNotIn('id="twc-final-summary"', early)
        self.assertNotIn('id="pick-record"', early)

    def test_archived_guidance_is_labelled_as_a_record(self):
        plan = NOTES['day_five_guidance']
        archived = build.guidance_section(snapshot('2026-10-19T04:00:00Z'), NOTES,
                                          'day_five_guidance', 'day-five-guidance',
                                          'Day-five guidance', archived=True)
        self.assertIn('Event complete · archived pre-match guide', archived)
        pre = build.guidance_section(snapshot('2026-10-18T01:00:00Z'), NOTES,
                                     'day_five_guidance', 'day-five-guidance', 'Day-five guidance')
        self.assertNotIn('Event complete · archived pre-match guide', pre)
        self.assertEqual(plan['nav_label'], 'Day-5 final-day guide')


class ResultTableConsistency(unittest.TestCase):
    """Every stored map list must reproduce the series score it sits next to."""

    DAYS = ('day_one', 'day_two', 'day_three_results', 'day_four_results', 'day_five_results')

    def test_every_map_list_reproduces_its_series_score(self):
        import re
        checked = 0
        for key in self.DAYS:
            for match in NOTES[key]['matches']:
                winner_maps = loser_maps = 0
                for segment in split_maps(match['maps']):
                    flat = segment.replace(',', ';')
                    for piece in (p.strip() for p in flat.split(';')):
                        found = re.match(r'^([A-Za-z0-9 .]+?)\s+(\d+)-(\d+)', piece)
                        if not found:
                            continue
                        left, right = int(found.group(2)), int(found.group(3))
                        self.assertNotEqual(left, right, 'Tied map score in ' + segment)
                        if left > right:
                            winner_maps += 1
                        else:
                            loser_maps += 1
                self.assertEqual('%d-%d' % (winner_maps, loser_maps), match['score'],
                                 '%s %s vs %s: map scores do not add up to %s (%r)'
                                 % (key, match['winner'], match['loser'], match['score'], match['maps']))
                checked += 1
        self.assertGreaterEqual(checked, 14)

    def test_the_corrected_day_two_row_is_the_verified_one(self):
        row = next(m for m in NOTES['day_two']['matches'] if m['winner'] == 'BETBOOM')
        self.assertEqual(row['maps'], 'Ancient 10-13 (PARIVISION); Anubis 13-4; Mirage 13-7')
        self.assertIn('HLTV match page', row['maps_note'])


class CrossBlockConsistency(unittest.TestCase):
    """The two published final-day records must not disagree with each other."""

    def test_pick_record_matches_the_final_day_pick_outcomes(self):
        outcomes = {row['board_pick']: row for row in NOTES['day_five_results']['pick_outcomes']['rows']}
        final = [row for row in NOTES['pick_record']['entries'] if row['date'] == '2026-10-18']
        self.assertEqual(len(final), 2)
        for row in final:
            other = outcomes[row['pick']]
            self.assertAlmostEqual(other['board_probability'], row['chance'] * 100, places=5)
            expected = 'won' if row['outcome'] == 'correct' else 'lost'
            self.assertEqual(other['result'], expected, row['fixture'])


if __name__ == '__main__':
    unittest.main()
