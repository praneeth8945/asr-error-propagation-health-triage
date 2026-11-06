"""Safe orchestration layer joining safety checks and the demo classifier."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re

from .classifier import TopicPrediction, get_default_classifier
from .content import (
    EMERGENCY_ACTION,
    MEDICATION_ACTION,
    PROMPT_ACTION,
    guidance_for_topic,
)
from .triage import TriageResult, asks_for_medication_or_dose, assess_text_for_safety


_MAX_TEXT_LENGTH = 1_200


@dataclass(frozen=True)
class AnalysisResult:
    """A UI-ready response with fixed safe wording."""

    transcript: str
    triage: TriageResult
    medication_request_detected: bool
    prediction: TopicPrediction | None
    next_steps: tuple[str, ...]
    clinician_note: str

    def as_dict(self) -> dict[str, object]:
        """Return JSON-friendly output for the CLI without retaining any data."""

        return {
            "transcript": self.transcript,
            "triage": {
                "level": self.triage.level,
                "flags": [asdict(flag) for flag in self.triage.flags],
            },
            "medication_request_detected": self.medication_request_detected,
            "prediction": asdict(self.prediction) if self.prediction else None,
            "next_steps": list(self.next_steps),
            "clinician_note": self.clinician_note,
        }


def _normalise_input(text: str) -> str:
    normalised = re.sub(r"\s+", " ", text.strip())
    if not normalised:
        raise ValueError("Please enter or record a symptom description first.")
    if len(normalised) > _MAX_TEXT_LENGTH:
        raise ValueError("Please shorten the description to 1,200 characters or fewer.")
    return normalised


def _clinician_note(transcript: str) -> str:
    """Create a copyable description without adding a diagnosis or treatment."""

    return (
        "User-described symptom note (not clinically interpreted): "
        f"{transcript}"
    )


def analyse_text(text: str) -> AnalysisResult:
    """Analyse text using a safety-first order of operations.

    Safety rules always take precedence over the topic model. No model output
    is returned for emergency or prompt-assessment wording.
    """

    transcript = _normalise_input(text)
    triage = assess_text_for_safety(transcript)

    if triage.level == "emergency":
        return AnalysisResult(
            transcript=transcript,
            triage=triage,
            medication_request_detected=False,
            prediction=None,
            next_steps=EMERGENCY_ACTION,
            clinician_note=_clinician_note(transcript),
        )

    if triage.level == "prompt":
        return AnalysisResult(
            transcript=transcript,
            triage=triage,
            medication_request_detected=False,
            prediction=None,
            next_steps=PROMPT_ACTION,
            clinician_note=_clinician_note(transcript),
        )

    if asks_for_medication_or_dose(transcript):
        return AnalysisResult(
            transcript=transcript,
            triage=triage,
            medication_request_detected=True,
            prediction=None,
            next_steps=MEDICATION_ACTION,
            clinician_note=_clinician_note(transcript),
        )

    prediction = get_default_classifier().predict(transcript)
    return AnalysisResult(
        transcript=transcript,
        triage=triage,
        medication_request_detected=False,
        prediction=prediction,
        next_steps=guidance_for_topic(prediction.topic_id),
        clinician_note=_clinician_note(transcript),
    )

