"""Deterministic multi-turn symptom-intake flow for an academic demonstration.

The flow asks fixed, non-diagnostic questions and prepares a factual note. It
does not infer a disease, select treatment, or calculate a medication dose.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import re
from typing import Any

from .content import EMERGENCY_ACTION, MEDICATION_ACTION, PROMPT_ACTION, guidance_for_topic
from .service import AnalysisResult, analyse_text
from .triage import SafetyFlag, TriageResult, asks_for_medication_or_dose, assess_text_for_safety


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTION_BANK_PATH = PROJECT_ROOT / "data" / "follow_up_questions.json"
SKIPPED_RESPONSE = "Skipped"
_VALID_INPUT_TYPES = frozenset({"choice", "text"})
_LEVEL_PRIORITY = {"information": 0, "prompt": 1, "emergency": 2}


@dataclass(frozen=True)
class FollowUpQuestion:
    identifier: str
    prompt: str
    input_type: str
    choices: tuple[str, ...]
    risk_key: str
    max_length: int


@dataclass(frozen=True)
class FollowUpAnswer:
    question_id: str
    prompt: str
    response: str


@dataclass(frozen=True)
class ConversationOutcome:
    triage: TriageResult
    medication_request_detected: bool
    topic_label: str | None
    topic_is_uncertain: bool
    next_steps: tuple[str, ...]
    clinician_note: str


@dataclass(frozen=True)
class GuidedConversation:
    """Immutable conversation state for predictable Streamlit reruns."""

    initial: AnalysisResult
    questions: tuple[FollowUpQuestion, ...]
    answers: tuple[FollowUpAnswer, ...] = ()
    turn_triage: TriageResult = TriageResult(level="information", flags=())
    turn_medication_request_detected: bool = False

    @property
    def is_initially_blocked(self) -> bool:
        return (
            self.initial.triage.level != "information"
            or self.initial.medication_request_detected
        )

    @property
    def is_terminal(self) -> bool:
        return (
            self.is_initially_blocked
            or self.turn_triage.level != "information"
            or self.turn_medication_request_detected
        )

    @property
    def is_complete(self) -> bool:
        return self.is_terminal or len(self.answers) >= len(self.questions)

    @property
    def current_question(self) -> FollowUpQuestion | None:
        if self.is_terminal or len(self.answers) >= len(self.questions):
            return None
        return self.questions[len(self.answers)]

    def outcome(self) -> ConversationOutcome | None:
        """Return a terminal/completed outcome, otherwise None."""

        if not self.is_complete:
            return None

        triage = self.initial.triage
        medication_requested = self.initial.medication_request_detected
        if triage.level == "information":
            triage = self.turn_triage
        medication_requested = medication_requested or self.turn_medication_request_detected

        if triage.level == "emergency":
            next_steps = EMERGENCY_ACTION
            topic_label = None
            topic_is_uncertain = True
        elif triage.level == "prompt":
            next_steps = PROMPT_ACTION
            topic_label = None
            topic_is_uncertain = True
        elif medication_requested:
            next_steps = MEDICATION_ACTION
            topic_label = None
            topic_is_uncertain = True
        else:
            prediction = self.initial.prediction
            topic_label = prediction.label if prediction and not prediction.is_uncertain else None
            topic_is_uncertain = prediction is None or prediction.is_uncertain
            topic_id = prediction.topic_id if prediction else None
            next_steps = guidance_for_topic(topic_id)

        return ConversationOutcome(
            triage=triage,
            medication_request_detected=medication_requested,
            topic_label=topic_label,
            topic_is_uncertain=topic_is_uncertain,
            next_steps=next_steps,
            clinician_note=_build_clinician_note(self.initial.transcript, self.answers),
        )


def _load_question(question: dict[str, Any]) -> FollowUpQuestion:
    identifier = question.get("id")
    prompt = question.get("prompt")
    input_type = question.get("input_type", "choice")
    choices = question.get("choices", [])
    risk_key = question.get("risk_key", "none")
    max_length = question.get("max_length", 300)

    if not isinstance(identifier, str) or not identifier:
        raise ValueError("Every follow-up question needs an id.")
    if not isinstance(prompt, str) or not prompt:
        raise ValueError(f"Question {identifier} needs a prompt.")
    if input_type not in _VALID_INPUT_TYPES:
        raise ValueError(f"Question {identifier} has an unsupported input type.")
    if not isinstance(risk_key, str):
        raise ValueError(f"Question {identifier} needs a risk key.")
    if not isinstance(max_length, int) or max_length < 1:
        raise ValueError(f"Question {identifier} has an invalid max length.")
    if input_type == "choice":
        if not isinstance(choices, list) or len(choices) < 2:
            raise ValueError(f"Choice question {identifier} needs at least two choices.")
        if not all(isinstance(choice, str) and choice for choice in choices):
            raise ValueError(f"Choice question {identifier} has an invalid choice.")
    else:
        choices = []

    return FollowUpQuestion(
        identifier=identifier,
        prompt=prompt,
        input_type=input_type,
        choices=tuple(choices),
        risk_key=risk_key,
        max_length=max_length,
    )


def load_question_bank(path: Path = QUESTION_BANK_PATH) -> tuple[
    tuple[FollowUpQuestion, ...], dict[str, tuple[FollowUpQuestion, ...]], FollowUpQuestion
]:
    """Load the visible, project-authored question data."""

    with path.open("r", encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)

    standard_raw = data.get("standard_questions")
    topic_raw = data.get("topic_specific_questions")
    final_raw = data.get("final_question")
    if not isinstance(standard_raw, list) or not isinstance(topic_raw, dict):
        raise ValueError("The question bank has an invalid structure.")

    standard = tuple(_load_question(question) for question in standard_raw)
    by_topic: dict[str, tuple[FollowUpQuestion, ...]] = {}
    for topic_id, questions in topic_raw.items():
        if not isinstance(topic_id, str) or not isinstance(questions, list):
            raise ValueError("Topic question entries must be lists keyed by string id.")
        by_topic[topic_id] = tuple(_load_question(question) for question in questions)

    final_question = _load_question(final_raw) if isinstance(final_raw, dict) else None
    if final_question is None:
        raise ValueError("The question bank needs a final question.")

    all_ids = [question.identifier for question in standard]
    all_ids.extend(
        question.identifier
        for questions in by_topic.values()
        for question in questions
    )
    all_ids.append(final_question.identifier)
    if len(all_ids) != len(set(all_ids)):
        raise ValueError("Question ids must be unique.")

    return standard, by_topic, final_question


def question_plan_for(topic_id: str | None) -> tuple[FollowUpQuestion, ...]:
    """Select a broad question path from the existing non-diagnostic topic."""

    standard, by_topic, final_question = load_question_bank()
    return standard + by_topic.get(topic_id or "", ()) + (final_question,)


def begin_guided_conversation(text: str) -> GuidedConversation:
    """Check the initial concern before choosing any follow-up question."""

    initial = analyse_text(text)
    topic_id = initial.prediction.topic_id if initial.prediction else None
    return GuidedConversation(initial=initial, questions=question_plan_for(topic_id))


def _response_flag(question: FollowUpQuestion, response: str) -> SafetyFlag | None:
    """Map a selected answer to a transparent fixed escalation rule."""

    rules: dict[str, dict[str, tuple[str, str, str]]] = {
        "emergency_warning_check": {
            "Yes": (
                "emergency",
                "Emergency warning selected",
                "You selected an emergency warning that this demo cannot safely assess.",
            ),
            "Not sure": (
                "prompt",
                "Emergency warning uncertain",
                "You were not sure about an emergency warning; seek professional help promptly.",
            ),
        },
        "rapid_worsening": {
            "Getting worse quickly": (
                "prompt",
                "Rapid worsening selected",
                "Rapid worsening is a reason to seek professional assessment promptly.",
            )
        },
        "daily_impact": {
            "Yes": (
                "prompt",
                "Daily activities affected",
                "Symptoms stopping normal activities are a reason to seek professional assessment.",
            )
        },
        "needs_clinician_context": {
            "Yes": (
                "prompt",
                "Additional context selected",
                "This context needs individual assessment by a qualified professional.",
            ),
            "Not sure": (
                "prompt",
                "Additional context uncertain",
                "This context needs individual assessment by a qualified professional.",
            ),
        },
        "sudden_or_neurological": {
            "Yes": (
                "emergency",
                "Sudden or neurological warning selected",
                "You selected a warning that can need emergency assessment.",
            ),
            "Not sure": (
                "prompt",
                "Sudden or neurological warning uncertain",
                "You were unsure about a warning that needs professional assessment.",
            ),
        },
        "breathing_difficulty": {
            "Yes": (
                "emergency",
                "Breathing difficulty selected",
                "Breathing difficulty can need emergency assessment.",
            ),
            "Not sure": (
                "prompt",
                "Breathing difficulty uncertain",
                "You were unsure about breathing difficulty; seek professional assessment promptly.",
            ),
        },
        "digestive_warning": {
            "Yes": (
                "prompt",
                "Digestive warning selected",
                "You selected wording that needs professional assessment promptly.",
            ),
            "Not sure": (
                "prompt",
                "Digestive warning uncertain",
                "You were unsure about a warning that needs professional assessment.",
            ),
        },
        "allergic_swelling": {
            "Yes": (
                "emergency",
                "Allergic swelling warning selected",
                "Swelling of the face, lips, tongue, or throat can need emergency assessment.",
            ),
            "Not sure": (
                "prompt",
                "Allergic swelling uncertain",
                "You were unsure about swelling that needs professional assessment.",
            ),
        },
        "prompt_warning": {
            "Yes": (
                "prompt",
                "Prompt-care warning selected",
                "You selected wording that needs professional assessment promptly.",
            ),
            "Not sure": (
                "prompt",
                "Prompt-care warning uncertain",
                "You were unsure about a warning that needs professional assessment.",
            ),
        },
        "rapid_decline_or_confusion": {
            "Yes": (
                "emergency",
                "Rapid decline or confusion warning selected",
                "Rapid worsening or confusion can need emergency assessment.",
            ),
            "Not sure": (
                "prompt",
                "Rapid decline or confusion uncertain",
                "You were unsure about a warning that needs professional assessment.",
            ),
        },
    }
    selected_rule = rules.get(question.risk_key, {}).get(response)
    if selected_rule is None:
        return None
    level, title, message = selected_rule
    return SafetyFlag(level=level, title=title, message=message)


def _highest_triage(*results: TriageResult) -> TriageResult:
    """Choose the highest safety tier while retaining same-tier evidence."""

    highest_level = max(results, key=lambda result: _LEVEL_PRIORITY[result.level]).level
    flags = tuple(
        flag
        for result in results
        if result.level == highest_level
        for flag in result.flags
    )
    return TriageResult(level=highest_level, flags=flags)


def _validate_response(question: FollowUpQuestion, response: str) -> str:
    cleaned = re.sub(r"\s+", " ", response.strip())
    if not cleaned:
        raise ValueError("Choose an answer or skip this question.")
    if question.input_type == "choice":
        if cleaned not in question.choices and cleaned != SKIPPED_RESPONSE:
            raise ValueError("Choose one of the listed answers or skip the question.")
    elif cleaned != SKIPPED_RESPONSE and len(cleaned) > question.max_length:
        raise ValueError(
            f"Please keep this answer to {question.max_length} characters or fewer."
        )
    return cleaned


def record_response(
    conversation: GuidedConversation,
    question_id: str,
    response: str,
) -> GuidedConversation:
    """Record one response after a separate turn-level safety check.

    A stale double-submit for an earlier question returns the current immutable
    state unchanged. Answers are never concatenated before safety analysis.
    """

    question = conversation.current_question
    if question is None or question.identifier != question_id:
        return conversation

    cleaned = _validate_response(question, response)
    answer = FollowUpAnswer(
        question_id=question.identifier,
        prompt=question.prompt,
        response=cleaned,
    )
    updated = replace(conversation, answers=conversation.answers + (answer,))
    if cleaned == SKIPPED_RESPONSE:
        return updated

    free_text_safety = assess_text_for_safety(cleaned)
    structured_flag = _response_flag(question, cleaned)
    structured_safety = (
        TriageResult(level=structured_flag.level, flags=(structured_flag,))
        if structured_flag
        else TriageResult(level="information", flags=())
    )
    turn_triage = _highest_triage(free_text_safety, structured_safety)
    medication_requested = asks_for_medication_or_dose(cleaned)

    if turn_triage.level != "information" or medication_requested:
        return replace(
            updated,
            turn_triage=turn_triage,
            turn_medication_request_detected=medication_requested,
        )
    return updated


def _build_clinician_note(
    initial_transcript: str, answers: tuple[FollowUpAnswer, ...]
) -> str:
    """Build a factual note that contains no inferred diagnosis or treatment."""

    lines = [
        "User-entered conversation note (not clinically interpreted)",
        f"Initial concern: {initial_transcript}",
        "Follow-up responses:",
    ]
    if answers:
        lines.extend(f"- {answer.prompt} Response: {answer.response}" for answer in answers)
    else:
        lines.append("- No follow-up responses recorded.")
    lines.append(
        "This academic prototype does not provide a diagnosis, medicine recommendation, or dosage."
    )
    return "\n".join(lines)
