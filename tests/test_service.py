from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.service import analyse_text


class ServiceTests(unittest.TestCase):
    def test_emergency_routing_suppresses_model_prediction(self) -> None:
        result = analyse_text("I have chest pain and shortness of breath.")
        self.assertEqual(result.triage.level, "emergency")
        self.assertIsNone(result.prediction)

    def test_medication_routing_suppresses_model_prediction(self) -> None:
        result = analyse_text("What medicine and dosage should I take for a headache?")
        self.assertTrue(result.medication_request_detected)
        self.assertIsNone(result.prediction)
        self.assertIn("cannot recommend", result.next_steps[0].lower())

    def test_normal_text_returns_educational_topic(self) -> None:
        result = analyse_text("My nose is blocked and I keep sneezing.")
        self.assertEqual(result.triage.level, "information")
        self.assertIsNotNone(result.prediction)
        self.assertFalse(result.prediction.is_uncertain)


if __name__ == "__main__":
    unittest.main()
