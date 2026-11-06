from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.triage import asks_for_medication_or_dose, assess_text_for_safety


class TriageTests(unittest.TestCase):
    def test_emergency_wording_overrides_information_routing(self) -> None:
        result = assess_text_for_safety("I have chest pain and cannot breathe.")
        self.assertEqual(result.level, "emergency")
        self.assertGreaterEqual(len(result.flags), 1)

    def test_explicit_negation_does_not_trigger_chest_rule(self) -> None:
        result = assess_text_for_safety("I have no chest pain, only a sore throat.")
        self.assertEqual(result.level, "information")

    def test_shared_negation_does_not_trigger_two_red_flags(self) -> None:
        result = assess_text_for_safety(
            "I have no chest pain or shortness of breath, only a sore throat."
        )
        self.assertEqual(result.level, "information")

    def test_positive_clause_after_but_is_not_silenced_by_negation(self) -> None:
        result = assess_text_for_safety(
            "I have no chest pain but I do have shortness of breath."
        )
        self.assertEqual(result.level, "emergency")

    def test_blood_wording_routes_to_prompt_assessment(self) -> None:
        result = assess_text_for_safety("I noticed blood in my urine.")
        self.assertEqual(result.level, "prompt")

    def test_medication_and_dose_question_is_detected(self) -> None:
        self.assertTrue(asks_for_medication_or_dose("Which medicine and dosage should I take?"))

    def test_implicit_or_named_medicine_request_is_detected(self) -> None:
        self.assertTrue(asks_for_medication_or_dose("What should I take for this?"))
        self.assertTrue(asks_for_medication_or_dose("Can I take paracetamol?"))
        self.assertTrue(asks_for_medication_or_dose("Can you prescribe something?"))

    def test_additional_emergency_variants_are_detected(self) -> None:
        self.assertEqual(
            assess_text_for_safety("My throat is closing.").level,
            "emergency",
        )
        self.assertEqual(
            assess_text_for_safety("I think I have taken an overdose.").level,
            "emergency",
        )
        self.assertEqual(
            assess_text_for_safety("I want to end my life.").level,
            "emergency",
        )


if __name__ == "__main__":
    unittest.main()
