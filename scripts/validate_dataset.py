"""Validate the small tracked synthetic dataset without downloading anything."""

from __future__ import annotations

import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.classifier import DEFAULT_DATASET_PATH, load_topic_definitions
from src.conversation import QUESTION_BANK_PATH, load_question_bank


def main() -> int:
    topics = load_topic_definitions(DEFAULT_DATASET_PATH)
    example_count = sum(len(topic.examples) for topic in topics)
    standard, by_topic, final_question = load_question_bank(QUESTION_BANK_PATH)
    with (PROJECT_ROOT / "data" / "demo_navigation_scenarios.json").open(
        "r", encoding="utf-8"
    ) as handle:
        scenarios = json.load(handle).get("scenarios", [])
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("The navigation scenario file must contain scenarios.")
    if not all(scenario.get("synthetic") is True for scenario in scenarios):
        raise ValueError("Every bundled scenario must be marked synthetic.")
    question_count = len(standard) + sum(len(items) for items in by_topic.values()) + 1
    print(
        "Validated "
        f"{len(topics)} topics, {example_count} synthetic examples, "
        f"{question_count} follow-up questions, and {len(scenarios)} navigation scenarios."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
