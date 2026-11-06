"""Train and save the reproducible synthetic text-topic artifact."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.classifier import DEFAULT_DATASET_PATH, SymptomTopicClassifier


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "models" / "topic_classifier.joblib",
        help="Output path for the generated local model artifact.",
    )
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output

    classifier = SymptomTopicClassifier.train(DEFAULT_DATASET_PATH)
    classifier.save(output)
    print(f"Saved reproducible topic model to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

