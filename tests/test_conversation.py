from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.conversation import (
    SKIPPED_RESPONSE,
    begin_guided_conversation,
    load_question_bank,
    record_response,
)


def _safe_response(question) -> str:
    """Choose a non-escalating response for a synthetic test conversation."""

    if question.input_type == "text":
        return SKIPPED_RESPONSE
    for candidate in ("No", "About the same", "Improving", "Less than 24 hours ago"):
        if candidate in question.choices:
            return candidate
    return "Prefer not to answer"


def _advance_until(conversation, target_question_id: str):
    while (
        conversation.current_question is not None
        and conversation.current_question.identifier != target_question_id
    ):
        question = conversation.current_question
        conversation = record_response(
            conversation,
            question.identifier,
            _safe_response(question),
        )
    return conversation


class GuidedConversationTests(unittest.TestCase):
    def test_question_bank_loads_project_authored_questions(self) -> None:
        standard, topics, final_question = load_question_bank()
        self.assertGreaterEqual(len(standard), 4)
        self.assertIn("cough_like", topics)
        self.assertEqual(final_question.input_type, "text")

    def test_benign_check_in_completes_with_factual_note(self) -> None:
        conversation = begin_guided_conversation(
            "My nose is blocked and I keep sneezing."
        )
        while conversation.current_question is not None:
            question = conversation.current_question
            conversation = record_response(
                conversation,
                question.identifier,
                _safe_response(question),
            )

        outcome = conversation.outcome()
        self.assertIsNotNone(outcome)
        self.assertEqual(outcome.triage.level, "information")
        self.assertIsNotNone(outcome.topic_label)
        self.assertIn("Initial concern: My nose is blocked", outcome.clinician_note)
        self.assertIn("not clinically interpreted", outcome.clinician_note)

    def test_late_free_text_red_flag_terminates_benign_flow(self) -> None:
        conversation = begin_guided_conversation(
            "My nose is blocked and I keep sneezing."
        )
        conversation = _advance_until(conversation, "additional_note")
        self.assertEqual(conversation.current_question.identifier, "additional_note")

        conversation = record_response(
            conversation,
            "additional_note",
            "I now have chest pain and cannot breathe.",
        )
        outcome = conversation.outcome()
        self.assertIsNotNone(outcome)
        self.assertEqual(outcome.triage.level, "emergency")
        self.assertIsNone(outcome.topic_label)
        self.assertIn("Do not rely on this application", outcome.next_steps[0])

    def test_structured_breathing_answer_terminates_flow(self) -> None:
        conversation = begin_guided_conversation("I have been coughing since yesterday.")
        conversation = _advance_until(conversation, "cough_breathing")
        self.assertEqual(conversation.current_question.identifier, "cough_breathing")

        conversation = record_response(conversation, "cough_breathing", "Yes")
        outcome = conversation.outcome()
        self.assertIsNotNone(outcome)
        self.assertEqual(outcome.triage.level, "emergency")

    def test_late_medicine_request_suppresses_topic_output(self) -> None:
        conversation = begin_guided_conversation(
            "My nose is blocked and I keep sneezing."
        )
        conversation = _advance_until(conversation, "additional_note")
        conversation = record_response(
            conversation,
            "additional_note",
            "Can I take ibuprofen for this?",
        )
        outcome = conversation.outcome()
        self.assertIsNotNone(outcome)
        self.assertTrue(outcome.medication_request_detected)
        self.assertIsNone(outcome.topic_label)
        self.assertIn("cannot recommend", outcome.next_steps[0].lower())

    def test_stale_second_submit_does_not_duplicate_answer(self) -> None:
        conversation = begin_guided_conversation(
            "My nose is blocked and I keep sneezing."
        )
        first_question = conversation.current_question
        updated = record_response(conversation, first_question.identifier, "No")
        stale = record_response(updated, first_question.identifier, "No")
        self.assertEqual(len(updated.answers), 1)
        self.assertEqual(stale, updated)

    def test_blank_free_text_note_is_rejected(self) -> None:
        conversation = begin_guided_conversation(
            "My nose is blocked and I keep sneezing."
        )
        conversation = _advance_until(conversation, "additional_note")
        with self.assertRaises(ValueError):
            record_response(conversation, "additional_note", "   ")


if __name__ == "__main__":
    unittest.main()
