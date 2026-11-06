from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.classifier import DEFAULT_DATASET_PATH, SymptomTopicClassifier, load_topic_definitions


class SymptomTopicClassifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.classifier = SymptomTopicClassifier.train(DEFAULT_DATASET_PATH)

    def test_dataset_has_expected_shape(self) -> None:
        topics = load_topic_definitions(DEFAULT_DATASET_PATH)
        self.assertGreaterEqual(len(topics), 5)
        self.assertTrue(all(len(topic.examples) >= 2 for topic in topics))

    def test_known_upper_respiratory_text_maps_to_broad_topic(self) -> None:
        prediction = self.classifier.predict(
            "I have a blocked nose, sneezing, and a scratchy throat."
        )
        self.assertEqual(prediction.topic_id, "upper_respiratory_like")
        self.assertFalse(prediction.is_uncertain)
        self.assertTrue(prediction.matched_terms)

    def test_low_signal_text_is_uncertain(self) -> None:
        prediction = self.classifier.predict("I want to discuss something today.")
        self.assertTrue(prediction.is_uncertain)
        self.assertIsNone(prediction.topic_id)


if __name__ == "__main__":
    unittest.main()

