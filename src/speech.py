"""Local, temporary-file speech transcription wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_CACHE = PROJECT_ROOT / "models" / "whisper"
ALLOWED_SUFFIXES = frozenset({".wav", ".mp3", ".m4a", ".mp4", ".webm", ".ogg", ".flac"})


class TranscriptionError(RuntimeError):
    """Raised when local speech transcription cannot be completed."""


@dataclass(frozen=True)
class TranscriptionResult:
    text: str
    language: str | None
    duration_seconds: float | None


@lru_cache(maxsize=2)
def _get_model(model_size: str):
    """Load a CPU-friendly model once per process, downloading it if needed."""

    try:
        from faster_whisper import WhisperModel
    except ImportError as error:
        raise TranscriptionError(
            "Audio transcription is unavailable. Install requirements.txt first."
        ) from error

    MODEL_CACHE.mkdir(parents=True, exist_ok=True)
    return WhisperModel(
        model_size,
        device="cpu",
        compute_type="int8",
        download_root=str(MODEL_CACHE),
    )


def transcribe_audio(
    audio_bytes: bytes,
    suffix: str = ".wav",
    model_size: str = "base.en",
) -> TranscriptionResult:
    """Transcribe audio without retaining the submitted file.

    faster-whisper's audio decoder handles common browser-recording formats.
    The temporary input is removed even when transcription fails.
    """

    if not audio_bytes:
        raise TranscriptionError("The audio file was empty.")
    suffix = suffix.lower() if suffix else ".wav"
    if suffix not in ALLOWED_SUFFIXES:
        raise TranscriptionError("Use WAV, MP3, M4A, MP4, WebM, OGG, or FLAC audio.")

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
            temporary_file.write(audio_bytes)
            temporary_path = Path(temporary_file.name)

        model = _get_model(model_size)
        segments, info = model.transcribe(
            str(temporary_path),
            beam_size=3,
            condition_on_previous_text=False,
            vad_filter=True,
        )
        text = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
        if not text:
            raise TranscriptionError(
                "No speech was detected. Try a clearer recording or enter the text manually."
            )
        return TranscriptionResult(
            text=text,
            language=getattr(info, "language", None),
            duration_seconds=getattr(info, "duration", None),
        )
    except TranscriptionError:
        raise
    except Exception as error:
        raise TranscriptionError(
            "The audio could not be transcribed. Check the file and try again."
        ) from error
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
