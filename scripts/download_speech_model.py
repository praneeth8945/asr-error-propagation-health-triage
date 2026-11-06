"""Pre-download a local faster-whisper model for offline demonstrations."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.speech import TranscriptionError, _get_model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="base.en", choices=("base.en", "tiny.en"))
    args = parser.parse_args()

    try:
        _get_model(args.model)
    except TranscriptionError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(f"{args.model} is available in models/whisper.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

