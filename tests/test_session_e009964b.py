"""Session e009964b: a single originated-model row the publisher's validator
rejects is withheld on its own instead of freezing the whole board.

Reproduced on branch arena/e009964b-maltaproj4 (diagnostic run 40197625563):
`scripts.validate` raised "Model roster has no HLTV source on this row" for one
model_vrs row of a fresh snapshot; the rest of the board was otherwise valid.
"""
import unittest
from unittest import mock

from scripts import quarantine, validate


def model_row(state='open'):
    return {
        'id': '1', 'state': state, 'method': 'model_vrs', 'teams': ['A', 'B'],
        'probabilities': [0.6, 0.4], 'fair_odds': [1.67, 2.5], 'pick': 'A',
        'evidence': [{'provider': 'Valve VRS model'}], 'flags': [],
    }


class PublicationViolations(unittest.TestCase):
    data = {'generated_at': '2026-10-25T13:00:00Z', 'matches': []}

    def test_non_model_and_closed_rows_are_not_rechecked(self):
        for row in (model_row(state='closed'), dict(model_row(), method='exchange'),
                    dict(model_row(), evidence=[])):
            with mock.patch.object(validate, 'validate_model_row',
                                   side_effect=AssertionError('must not run')) as spy:
                self.assertEqual(quarantine.publication_violations(self.data, row), [])
                spy.assert_not_called()

    def test_rejected_model_row_is_reported_with_the_validator_message(self):
        row = model_row()
        with mock.patch.object(validate, 'validate_model_row',
                               side_effect=AssertionError('Model roster has no HLTV source on this row')):
            problems = quarantine.publication_violations(self.data, row)
        self.assertEqual(problems, ['Publication validator: Model roster has no HLTV source on this row'])

    def test_accepted_model_row_has_no_violation(self):
        with mock.patch.object(validate, 'validate_model_row', return_value=None):
            self.assertEqual(quarantine.publication_violations(self.data, model_row()), [])

    def test_non_assertion_errors_are_not_swallowed(self):
        # An unexpected crash in the checks must still fail the publish, not hide a row.
        with mock.patch.object(validate, 'validate_model_row', side_effect=KeyError('x')):
            with self.assertRaises(KeyError):
                quarantine.publication_violations(self.data, model_row())


if __name__ == '__main__':
    unittest.main()
