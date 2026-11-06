"""Small, reproducible text-topic classifier for the academic demo.

The classifier maps a symptom description to a broad educational topic. It is
not a disease classifier and must not be used for clinical decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "data" / "symptom_topics.json"
DEFAULT_ARTIFACT_PATH = PROJECT_ROOT / "models" / "topic_classifier.joblib"
MODEL_FORMAT_VERSION = 1


@dataclass(frozen=True)
class TopicDefinition:
    """One broad, non-diagnostic topic from the bundled synthetic data."""

    topic_id: str
    label: str
    examples: tuple[str, ...]


@dataclass(frozen=True)
class TopicPrediction:
    """A transparent result from the demonstration text matcher."""

    topic_id: str | None
    label: str
    score: float
    matched_terms: tuple[str, ...]
    is_uncertain: bool


def clean_text(text: str) -> str:
    """Normalise whitespace while preserving the user's wording."""

    return re.sub(r"\s+", " ", text.strip())


def load_topic_definitions(dataset_path: Path = DEFAULT_DATASET_PATH) -> tuple[TopicDefinition, ...]:
    """Load and validate the compact synthetic topic dataset."""

    with dataset_path.open("r", encoding="utf-8") as handle:
        raw_data: dict[str, Any] = json.load(handle)

    topics = raw_data.get("topics")
    if not isinstance(topics, list) or not topics:
        raise ValueError("The dataset must contain a non-empty 'topics' list.")

    definitions: list[TopicDefinition] = []
    seen_ids: set[str] = set()
    for item in topics:
        if not isinstance(item, dict):
            raise ValueError("Each topic must be an object.")
        topic_id = item.get("id")
        label = item.get("label")
        examples = item.get("examples")
        if not isinstance(topic_id, str) or not topic_id:
            raise ValueError("Each topic needs a non-empty string id.")
        if topic_id in seen_ids:
            raise ValueError(f"Duplicate topic id: {topic_id}")
        if not isinstance(label, str) or not label:
            raise ValueError(f"Topic {topic_id} needs a label.")
        if not isinstance(examples, list) or len(examples) < 2:
            raise ValueError(f"Topic {topic_id} needs at least two examples.")
        if not all(isinstance(example, str) and example.strip() for example in examples):
            raise ValueError(f"Topic {topic_id} has an invalid example.")
        definitions.append(
            TopicDefinition(
                topic_id=topic_id,
                label=label,
                examples=tuple(clean_text(example) for example in examples),
            )
        )
        seen_ids.add(topic_id)

    return tuple(definitions)


def dataset_hash(dataset_path: Path) -> str:
    """Return a deterministic content hash for an artifact compatibility check."""

    return sha256(dataset_path.read_bytes()).hexdigest()


class SymptomTopicClassifier:
    """TF-IDF plus logistic-regression matcher trained only on synthetic text."""

    def __init__(
        self,
        pipeline: Pipeline,
        labels: dict[str, str],
        source_hash: str,
        uncertainty_threshold: float = 0.40,
    ) -> None:
        self.pipeline = pipeline
        self.labels = labels
        self.source_hash = source_hash
        self.uncertainty_threshold = uncertainty_threshold

    @classmethod
    def train(cls, dataset_path: Path = DEFAULT_DATASET_PATH) -> "SymptomTopicClassifier":
        """Train a reproducible baseline from the tracked demo dataset."""

        definitions = load_topic_definitions(dataset_path)
        texts: list[str] = []
        targets: list[str] = []
        labels: dict[str, str] = {}
        for topic in definitions:
            labels[topic.topic_id] = topic.label
            texts.extend(topic.examples)
            targets.extend([topic.topic_id] * len(topic.examples))

        pipeline = Pipeline(
            steps=[
                (
                    "tfidf",
                    TfidfVectorizer(
                        lowercase=True,
                        ngram_range=(1, 2),
                        strip_accents="unicode",
                        stop_words="english",
                        sublinear_tf=True,
                    ),
                ),
                (
                    "classifier",
                    LogisticRegression(
                        C=2.0,
                        class_weight="balanced",
                        max_iter=2_000,
                        random_state=42,
                    ),
                ),
            ]
        )
        pipeline.fit(texts, targets)
        return cls(pipeline=pipeline, labels=labels, source_hash=dataset_hash(dataset_path))

    def predict(self, text: str) -> TopicPrediction:
        """Return a broad topic or an uncertainty result.

        The returned score reflects text-pattern matching inside this tiny
        synthetic dataset. It is not a probability of a disease or condition.
        """

        cleaned = clean_text(text)
        if not cleaned:
            return TopicPrediction(
                topic_id=None,
                label="no usable symptom text",
                score=0.0,
                matched_terms=(),
                is_uncertain=True,
            )

        probabilities = self.pipeline.predict_proba([cleaned])[0]
        classifier: LogisticRegression = self.pipeline.named_steps["classifier"]
        best_index = int(probabilities.argmax())
        topic_id = str(classifier.classes_[best_index])
        score = float(probabilities[best_index])
        matched_terms = self._matched_terms(cleaned, best_index)

        if score < self.uncertainty_threshold:
            return TopicPrediction(
                topic_id=None,
                label="no clear demonstration topic",
                score=score,
                matched_terms=matched_terms,
                is_uncertain=True,
            )

        return TopicPrediction(
            topic_id=topic_id,
            label=self.labels[topic_id],
            score=score,
            matched_terms=matched_terms,
            is_uncertain=False,
        )

    def _matched_terms(self, text: str, class_index: int) -> tuple[str, ...]:
        """Extract up to five influential positive text features for display."""

        vectorizer: TfidfVectorizer = self.pipeline.named_steps["tfidf"]
        classifier: LogisticRegression = self.pipeline.named_steps["classifier"]
        sparse_row = vectorizer.transform([text])
        feature_names = vectorizer.get_feature_names_out()
        weighted_features: list[tuple[float, str]] = []
        for feature_index, value in zip(sparse_row.indices, sparse_row.data):
            contribution = float(value * classifier.coef_[class_index, feature_index])
            if contribution > 0:
                weighted_features.append((contribution, str(feature_names[feature_index])))

        weighted_features.sort(reverse=True)
        return tuple(term for _, term in weighted_features[:5])

    def save(self, artifact_path: Path) -> None:
        """Persist a reproducible local artifact; callers choose when to write."""

        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "format_version": MODEL_FORMAT_VERSION,
                "pipeline": self.pipeline,
                "labels": self.labels,
                "source_hash": self.source_hash,
                "uncertainty_threshold": self.uncertainty_threshold,
            },
            artifact_path,
        )

    @classmethod
    def load(cls, artifact_path: Path) -> "SymptomTopicClassifier":
        """Load an artifact created by save."""

        artifact: dict[str, Any] = joblib.load(artifact_path)
        if artifact.get("format_version") != MODEL_FORMAT_VERSION:
            raise ValueError("Unsupported classifier artifact version.")
        return cls(
            pipeline=artifact["pipeline"],
            labels=dict(artifact["labels"]),
            source_hash=str(artifact["source_hash"]),
            uncertainty_threshold=float(artifact["uncertainty_threshold"]),
        )


@lru_cache(maxsize=1)
def get_default_classifier() -> SymptomTopicClassifier:
    """Load a matching local artifact when available, otherwise train in memory."""

    expected_hash = dataset_hash(DEFAULT_DATASET_PATH)
    if DEFAULT_ARTIFACT_PATH.exists():
        try:
            candidate = SymptomTopicClassifier.load(DEFAULT_ARTIFACT_PATH)
            if candidate.source_hash == expected_hash:
                return candidate
        except (OSError, ValueError, KeyError):
            # A stale local artifact must never block the safe text-only demo.
            pass
    return SymptomTopicClassifier.train(DEFAULT_DATASET_PATH)
