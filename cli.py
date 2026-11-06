"""Command-line entry point for text or local audio demonstration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from src.service import analyse_text
from src.speech import TranscriptionError, transcribe_audio


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Educational, non-diagnostic symptom text demonstration."
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--text", help="Typed symptom description.")
    input_group.add_argument("--audio", type=Path, help="Path to a local audio file.")
    parser.add_argument(
        "--model",
        default="base.en",
        choices=("base.en", "tiny.en"),
        help="Local faster-whisper model to use with --audio.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.audio:
            if not args.audio.is_file():
                raise ValueError(f"Audio file not found: {args.audio}")
            transcription = transcribe_audio(
                args.audio.read_bytes(),
                suffix=args.audio.suffix or ".wav",
                model_size=args.model,
            )
            result = analyse_text(transcription.text)
        else:
            result = analyse_text(args.text)
    except (ValueError, TranscriptionError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    print(json.dumps(result.as_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

