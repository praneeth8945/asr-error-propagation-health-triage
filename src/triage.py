"""Deterministic safety checks for the educational interface.

The rule set is deliberately conservative, limited, and non-exhaustive. It
does not diagnose, validate, or replace emergency or clinical services.
"""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class SafetyFlag:
    """A human-readable escalation signal, not a clinical determination."""

    level: str
    title: str
    message: str


@dataclass(frozen=True)
class TriageResult:
    """The highest applicable warning level plus matched rule descriptions."""

    level: str
    flags: tuple[SafetyFlag, ...]


@dataclass(frozen=True)
class _Rule:
    level: str
    title: str
    message: str
    expression: re.Pattern[str]


EMERGENCY_RULES: tuple[_Rule, ...] = (
    _Rule(
        "emergency",
        "Chest pain or pressure wording",
        "Chest pain or pressure can need urgent in-person assessment.",
        re.compile(r"\b(chest pain|chest pressure|pressure in (my )?chest)\b", re.I),
    ),
    _Rule(
        "emergency",
        "Severe breathing difficulty wording",
        "Severe breathing difficulty can need urgent in-person assessment.",
        re.compile(
            r"\b(can(?:not|'t) breathe|trouble breathing|difficulty breathing|shortness of breath)\b",
            re.I,
        ),
    ),
    _Rule(
        "emergency",
        "Stroke-like symptom wording",
        "Sudden face, arm, or speech changes can need urgent in-person assessment.",
        re.compile(
            r"\b(slurred speech|face droop|one[- ]sided weakness|sudden weakness on (one )?side)\b",
            re.I,
        ),
    ),
    _Rule(
        "emergency",
        "Severe allergic swelling wording",
        "Swelling of the face, lips, tongue, or throat can need urgent in-person assessment.",
        re.compile(
            r"\b((face|lip|lips|tongue|throat) swelling|swollen tongue|tongue is swollen|throat (is )?(closing|swelling))\b",
            re.I,
        ),
    ),
    _Rule(
        "emergency",
        "Loss of consciousness or seizure wording",
        "Loss of consciousness or a seizure can need urgent in-person assessment.",
        re.compile(r"\b(unconscious|passed out|loss of consciousness|seizure)\b", re.I),
    ),
    _Rule(
        "emergency",
        "Heavy bleeding wording",
        "Heavy bleeding can need urgent in-person assessment.",
        re.compile(r"\b(heavy bleeding|bleeding heavily|soaking (through )?(a )?(pad|bandage))\b", re.I),
    ),
    _Rule(
        "emergency",
        "Self-harm wording",
        "Thoughts of self-harm need immediate human support.",
        re.compile(
            r"\b(kill myself|hurt myself|harm myself|end my life|suicidal)\b",
            re.I,
        ),
    ),
    _Rule(
        "emergency",
        "Possible poisoning or overdose wording",
        "Possible poisoning or overdose can need urgent in-person assessment.",
        re.compile(
            r"\b(overdose|poisoned|poisoning|swallowed (too many|a lot of) (pills|tablets|medicines|chemicals))\b",
            re.I,
        ),
    ),
)

PROMPT_ASSESSMENT_RULES: tuple[_Rule, ...] = (
    _Rule(
        "prompt",
        "Blood-related symptom wording",
        "Blood-related symptoms are a reason to contact a healthcare professional promptly.",
        re.compile(
            r"\b(blood in (my )?(stool|urine|vomit)|vomit(ing)? blood|cough(ing)? blood)\b",
            re.I,
        ),
    ),
    _Rule(
        "prompt",
        "Unable to keep liquids down wording",
        "Difficulty keeping liquids down can need prompt professional assessment.",
        re.compile(r"\b(can(?:not|'t) keep (?:liquids|fluids|water) down|very dehydrated)\b", re.I),
    ),
    _Rule(
        "prompt",
        "Severe or worsening pain wording",
        "Severe or rapidly worsening pain can need prompt professional assessment.",
        re.compile(r"\b(severe|unbearable|worsening) (head|stomach|abdominal|back) pain\b", re.I),
    ),
)

_MEDICATION_REQUEST = re.compile(
    r"\b(what|which|recommend|suggest|give|tell me|need|want|how much|how many)\b"
    r".{0,60}\b(medicine|medication|drug|tablet|pill|antibiotic|antibiotics|dose|dosage|milligram|mg)\b"
    r"|\b(medicine|medication|drug|tablet|pill|antibiotic|antibiotics)\b.{0,40}\b(dose|dosage|mg|milligram)\b"
    r"|\b(what|which) should i take\b"
    r"|\b(can|could|should|may) i take (paracetamol|acetaminophen|ibuprofen|aspirin|amoxicillin|an antibiotic|antihistamine|a painkiller|cough syrup)\b"
    r"|\b(can you|could you|please) prescribe\b"
    r"|\bi (need|want) (an )?(antibiotic|medicine|medication|drug|prescription)\b",
    re.I,
)


def _is_negated(text: str, match_start: int) -> bool:
    """Handle a limited explicit-negation scope without claiming clinical NLP.

    This covers ordinary phrases such as "no chest pain or shortness of
    breath", while deliberately treating a later "but" clause as a new
    statement. It is not a comprehensive language-understanding system.
    """

    clause_prefix = re.split(r"[.!?;]", text[:match_start])[-1].lower()
    negation_patterns = (
        r"\b(?:no|without|denies|denied|never)\b(?!\s*,).*",
        r"\b(?:do|does|did)\s+not\s+(?:have|feel|experience).*",
        r"\b(?:don't|dont|doesn't|doesnt|didn't|didnt)\s+(?:have|feel|experience).*",
        r"\b(?:am|is|are|was|were)\s+not\s+(?:having|feeling|experiencing).*",
    )
    for pattern in negation_patterns:
        match = re.search(pattern, clause_prefix, re.I)
        if match and not re.search(r"\b(but|however|except)\b", match.group(0), re.I):
            return True
    return False


def _flags_for_rules(text: str, rules: tuple[_Rule, ...]) -> tuple[SafetyFlag, ...]:
    matches: list[SafetyFlag] = []
    for rule in rules:
        for match in rule.expression.finditer(text):
            if not _is_negated(text, match.start()):
                matches.append(SafetyFlag(rule.level, rule.title, rule.message))
                break
    return tuple(matches)


def assess_text_for_safety(text: str) -> TriageResult:
    """Return emergency, prompt-assessment, or information-only routing."""

    emergency_flags = _flags_for_rules(text, EMERGENCY_RULES)
    if emergency_flags:
        return TriageResult(level="emergency", flags=emergency_flags)

    prompt_flags = _flags_for_rules(text, PROMPT_ASSESSMENT_RULES)
    if prompt_flags:
        return TriageResult(level="prompt", flags=prompt_flags)

    return TriageResult(level="information", flags=())


def asks_for_medication_or_dose(text: str) -> bool:
    """Recognise requests that this project must route to a clinician/pharmacist."""

    return bool(_MEDICATION_REQUEST.search(text))
