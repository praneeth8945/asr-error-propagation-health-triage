from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.speech import transcribe_audio


class _FakeModel:
    def __init__(self) -> None:
        self.temporary_path: Path | None = None
        self.existed_during_transcription = False

    def transcribe(self, path: str, **_: object):
        self.temporary_path = Path(path)
        self.existed_during_transcription = self.temporary_path.exists()
        return iter([SimpleNamespace(text=" A short test. ")]), SimpleNamespace(
            language="en", duration=1.0
        )


class SpeechTests(unittest.TestCase):
    def test_temporary_audio_is_removed_after_transcription(self) -> None:
        fake_model = _FakeModel()
        with patch("src.speech._get_model", return_value=fake_model):
            result = transcribe_audio(b"not-real-wav-content", suffix=".wav")

        self.assertEqual(result.text, "A short test.")
        self.assertTrue(fake_model.existed_during_transcription)
        self.assertIsNotNone(fake_model.temporary_path)
        self.assertFalse(fake_model.temporary_path.exists())


if __name__ == "__main__":
    unittest.main()
